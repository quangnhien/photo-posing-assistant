import math
from fastapi import FastAPI, UploadFile, File, HTTPException, Form,Query
from fastapi.responses import JSONResponse
import motor.motor_asyncio
from PIL import Image
import cv2
from azure.storage.blob import BlobServiceClient
import io
import os
from dotenv import load_dotenv
from datetime import datetime
import uuid
import httpx
from fastapi.middleware.cors import CORSMiddleware
import base64
from bson import ObjectId
from fastapi.params import Body
import traceback
from compare_keypoints import compare_keypoints
from helper import download_image_as_np_array
import numpy as np


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ENDPOINT

CLIP_ENDPOINT = f"http://{os.getenv('SERVER_IP')}:8001/clip_embed"
BLIP2_ENDPOINT = f"http://{os.getenv('SERVER_IP')}:8002/generate_caption"
POSE_ENDPOINT = f"http://{os.getenv('SERVER_IP')}:8003/generate_keypoints"

# MongoDB connection
client = motor.motor_asyncio.AsyncIOMotorClient(
    f"mongodb+srv://{os.getenv('MONGOBD_USER')}:{os.getenv('MONGOBD_PASSWORD')}@mwa.ah6ka.mongodb.net/?retryWrites=true&w=majority&appName=MWA")
db = client.get_database('posingassistant')
poses_collection = db.get_collection('posegallery')
error_collection = db.get_collection('errorimages')
compare_collection = db.get_collection('compare')
# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(
    AZURE_STORAGE_CONNECTION_STRING)



# Helper: Embed Image (for vector embedding only)
async def embed_image(image_bytes):
    async with httpx.AsyncClient() as client:
        files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
        response = await client.post(CLIP_ENDPOINT, files=files)
        if response.status_code == 200:
            return response.json()['vector']
        else:
            raise Exception(f"CLIP Server Error: {response.text}")

# Helper: Extract pose


async def generate_poses(image_bytes,image_url=None):
    async with httpx.AsyncClient() as client:
        files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
        response = await client.post(POSE_ENDPOINT, files=files)
        if response.status_code == 200:
            return response.json()['keypoints']
        else:
            if image_url:
                await error_collection.insert_one({
                "image_url": image_url,
                "error_message": str(response.text)
            })
            raise Exception(f"PoseModel Server Error: {response.text}")

# Helper: Generate Tags from Image


async def generate_tags_from_image(image_bytes):
    async with httpx.AsyncClient() as client:
        files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
        print(BLIP2_ENDPOINT)
        response = await client.post(BLIP2_ENDPOINT, files=files)
        
        if response.status_code == 200:
            caption = response.json()['caption']

            # Simple tag splitting
            # tags = caption.lower().replace(',', '').split(' ')
            # tags = [tag for tag in tags if tag]
            return caption
        else:
            raise Exception(f"BLIP Server Error: {response.text}")

# Helper: Upload processed image bytes to Azure


async def upload_to_azure(processed_image_bytes, extension='jpg',container_name = os.getenv('AZURE_STORAGE_IMAGE_CONTAINER_NAME')):
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    random_id = uuid.uuid4().hex[:10]
    new_filename = f"pose_{timestamp}_{random_id}.{extension}"

    container_client = blob_service_client.get_container_client(
        container_name)
    blob_client = container_client.get_blob_client(new_filename)
    blob_client.upload_blob(processed_image_bytes, overwrite=True)
    blob_url = blob_client.url
    return blob_url

# Main Upload API


@app.post("/upload_pose")
async def upload_pose(
    file: UploadFile = File(...),
    location: str = Form(None)  # Optional location field
):
    try:
        processed_image_bytes = await file.read()

        # Upload to Azure
        azure_url = await upload_to_azure(processed_image_bytes)
        
        try:
            tags = await generate_tags_from_image(processed_image_bytes)
            poses = await generate_poses(processed_image_bytes)
            vector = await embed_image(processed_image_bytes)
            pose_doc = {
                "image_url": azure_url,
                "popularity": 0,
                "tags": tags,
                "vector": vector,
                "poses": poses,
                "poses_confidence": sum(p[2] for p in poses) / len(poses),
                "location": location  # will be None if not provided
            }
            
            await poses_collection.insert_one(pose_doc)

            return JSONResponse(content={
                "message": "Pose uploaded with auto-tags!",
                "tags": tags,
                "image_url": azure_url
            }, status_code=200)

        except Exception as e:
            await error_collection.insert_one({
                "image_url": azure_url,
                "error_message": str(e)
            })
            return JSONResponse(content={"error": str(e)}, status_code=500)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)



@app.get("/popular_poses")
async def get_popular_poses():
    try:
        top_poses_cursor = poses_collection.find(
            {},
            # Projection: include only _id and image_url
            {"_id": 1, "image_url": 1}
        ).sort("popularity", -1).limit(4)

        top_poses = await top_poses_cursor.to_list(length=4)
        response = [
            {
                "id": str(pose["_id"]),
                "image_url": pose["image_url"]
            }
            for pose in top_poses
        ]
        return JSONResponse(content={"poses": response})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/increment_popularity")
async def increment_popularity(pose_id: str = Body(..., embed=True)):
    try:
        result = await poses_collection.update_one(
            {"_id": ObjectId(pose_id)},
            {"$inc": {"popularity": 1}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Pose not found")

        return JSONResponse(content={"message": "Popularity incremented"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/compare")
async def compare_pose(pose: str = Form(...), userImage: UploadFile = File(...)):
    try:
        modelPose = await poses_collection.find_one(
            {"_id": ObjectId(pose)},
            {"image_url": 1, "poses": 1}
        )
        if not modelPose:
            raise HTTPException(status_code=404, detail="Pose not found")

        modelImage = await download_image_as_np_array(modelPose["image_url"])  

        # Read and process user image
        user_image_bytes = await userImage.read()
        user_image_url = await upload_to_azure(user_image_bytes)
        nparr = np.frombuffer(user_image_bytes, np.uint8)
        userImg = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        userImg = cv2.cvtColor(userImg, cv2.COLOR_BGR2RGB)

        userPose = await generate_poses(user_image_bytes,user_image_url)

        # Compare and generate output image
        horizontal, score, guide = compare_keypoints(
            modelPose["poses"], userPose, modelImage, userImg
        )

        # Convert final image to base64
        output_buffer = io.BytesIO()
        Image.fromarray(horizontal).save(output_buffer, format="JPEG")
        encoded_image = base64.b64encode(output_buffer.getvalue()).decode("utf-8")
        
        if not math.isfinite(score):  # catches NaN, inf, -inf
            score = 1
            # Save everything to MongoDB
            
        pose_doc = {
            "model_image_url": modelPose["image_url"],
            "user_image_url":user_image_url,
            "guide_image_url": await upload_to_azure(encoded_image,container_name = os.getenv('AZURE_STORAGE_GUIDE_IMAGE_CONTAINER_NAME')),
            "guide": guide,
            "score": round(score, 2),
            "user_pose":userPose,
            "pose_confidence":sum(p[2] for p in userPose) / len(userPose)
        }
        result = await compare_collection.insert_one(pose_doc)
        return JSONResponse(content={
            "image_base64": encoded_image,
            "score": round(score, 2),
            "guide": guide,
            "id":str(result.inserted_id)
        })

    except Exception as e:
        
        print("Error during /compare:\n", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/submit_feedback")
async def submit_feedback(
    id: str = Form(...),
    is_useful: bool = Form(...),
    comment: str = Form(...)
):
    result = await compare_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "is_useful": is_useful,
            "comment": comment
        }}
    )
    if result.matched_count == 0:
        return JSONResponse(status_code=404, content={"error": "Pose not found"})
    return JSONResponse(content={"message": "Feedback received"}, status_code=200)



@app.get("/search_poses")
async def search_poses(q: str = Query(..., min_length=1)):
    try:
        keywords = q.lower().split()  # ["players", "baseball"]
        
        response = await search_by_keywords(keywords)
        
        return JSONResponse(content={"poses": response})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/search_combined")
async def search_combined(text: str = Form(None), image: UploadFile = File(None)):
    keywords = text.lower().split() if text else []
    image_vector = None
    image_docs = []

    if image:
        image_bytes = await image.read()
        image_vector = await embed_image(image_bytes)
        image_vector = [float(v) for v in image_vector]  # Ensure JSON-serializable

        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",  # your index name
                    "path": "vector",
                    "queryVector": image_vector,
                    "numCandidates": 100,
                    "limit": 20
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "image_url": 1,
                    "tags": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]

        image_docs = await poses_collection.aggregate(pipeline).to_list(length=20)

    text_docs = []
    if keywords:
        text_docs = await search_by_keywords(keywords,20)
    # Combine results by ID
    combined = {}
    alpha, beta = 0.7, 0.4

    for doc in image_docs:
        combined[doc["_id"]] = {
            "doc": doc,
            "image_score": doc["score"],
            "text_score": 0.0
        }

    for doc in text_docs:
        doc_id = str(doc["id"])
        if doc_id not in combined:
            combined[doc_id] = {
                "doc": doc,
                "image_score": 0.0,
                "text_score": 0.0
            }
        combined[doc_id]["text_score"] = doc["score"]

    # Final sort by weighted score
    results = sorted(
        combined.values(),
        key=lambda r: alpha * r["image_score"] + beta * r["text_score"],
        reverse=True
    )
    return JSONResponse(content={
        "results": [
            {
                "id": r["doc"]["_id"],
                "image_url": r["doc"]["image_url"],
                "tags": r["doc"].get("tags", []),
                "score": round(alpha * r["image_score"] + beta * r["text_score"], 3)
            }
            for r in results[:4]
        ]
    })
async def search_by_keywords(keywords,n=4):

    pipeline = [
        {
            "$addFields": {
                "combined": {
                    "$cond": {
                        "if": {"$ne": ["$location", None]},
                        "then": {"$concatArrays": ["$tags", ["$location"]]},
                        "else": "$tags"
                    }
                }
            }
        },           
        {
            "$addFields": {
                "score": {
                    "$size": {
                        "$setIntersection": [
                            "$combined",  # exact tags
                            keywords  # still use raw tokens for now
                        ]
                    }
                }
            }
        },
        {
            "$sort": {
                "score": -1,
                "popularity": -1
            }
        },
        {
            "$limit": n
        },
        {
            "$project": {
                "_id": {"$toString": "$_id"},
                "image_url": 1,
                "tags": 1,
                "score": 1,
                "popularity": 1
            }
        }
    ]

    results = await poses_collection.aggregate(pipeline).to_list(length=4)
    response = [
        {
            "id": str(pose["_id"]),
            "image_url": pose["image_url"],
            "score": pose['score']/len(pose["tags"]),
            "popularity": pose['popularity'],
        }
        for pose in results
    ]
    return response