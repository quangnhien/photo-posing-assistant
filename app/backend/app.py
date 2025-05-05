import math
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse,StreamingResponse
import motor.motor_asyncio
from torchvision import transforms
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
from fastapi import HTTPException
from fastapi.params import Body

from compare_keypoints import compare_keypoints
from helper import download_image_as_pil,download_image_as_np_array,resize_image
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

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
AZURE_STORAGE_CONTAINER_NAME = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
blob_service_client = BlobServiceClient.from_connection_string(
    AZURE_STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(
    AZURE_STORAGE_CONTAINER_NAME)


# Resize + CenterCrop Transform (for processed image saved to Azure)
resize_crop_transform = transforms.Compose([
    transforms.Resize(384, interpolation=transforms.InterpolationMode.BICUBIC),
    transforms.CenterCrop(384)
])


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


async def generate_poses(image_bytes):
    async with httpx.AsyncClient() as client:
        files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
        response = await client.post(POSE_ENDPOINT, files=files)
        if response.status_code == 200:
            return response.json()['keypoints']
        else:
            raise Exception(f"PoseModel Server Error: {response.text}")

# Helper: Generate Tags from Image


async def generate_tags_from_image(image_bytes):
    async with httpx.AsyncClient() as client:
        files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
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


async def upload_to_azure(processed_image_bytes, extension='jpg'):
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    random_id = uuid.uuid4().hex[:10]
    new_filename = f"pose_{timestamp}_{random_id}.{extension}"

    blob_client = container_client.get_blob_client(new_filename)
    blob_client.upload_blob(processed_image_bytes, overwrite=True)
    blob_url = blob_client.url
    return blob_url

# Main Upload API


@app.post("/upload_pose")
async def upload_pose(file: UploadFile = File(...)):
    try:
        # original_contents = await file.read()

        # # Open original image
        # image = Image.open(io.BytesIO(original_contents)).convert('RGB')

        # # Resize + CenterCrop 
        # processed_image = resize_crop_transform(image)

        # # Save processed image to bytes buffer
        # buffer = io.BytesIO()
        # # You can adjust quality
        # processed_image.save(buffer, format='JPEG', quality=95)
        # buffer.seek(0)
        # processed_image_bytes = buffer.read()
        processed_image_bytes = await file.read()
        # Upload processed image to Azure
        azure_url = await upload_to_azure(processed_image_bytes)

        # Generate tags (use original full image or processed one — your choice)
        tags = await generate_tags_from_image(processed_image_bytes)

        # Extrect poses (use processed 224x224 image)
        poses = await generate_poses(processed_image_bytes)

        # Generate vector (use processed 224x224 image)
        vector = await embed_image(processed_image_bytes)

        # Save everything to MongoDB
        pose_doc = {
            "image_url": azure_url,
            "popularity":0,
            "tags": tags,
            "vector": vector,
            "poses": poses
        }
        await poses_collection.insert_one(pose_doc)

        return JSONResponse(content={"message": "Pose uploaded with auto-tags!", "tags": tags, "image_url": azure_url}, status_code=200)

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

        modelImage = await download_image_as_np_array(modelPose["image_url"])  # or PIL if you prefer

        # Read and process user image
        user_image_bytes = await userImage.read()
        nparr = np.frombuffer(user_image_bytes, np.uint8)
        userImg = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        userImg = cv2.cvtColor(userImg, cv2.COLOR_BGR2RGB)
        # user_image_pil = Image.open(io.BytesIO(user_image_bytes)).convert("RGB")
        # processed_image = resize_crop_transform(user_image_pil)
        
        # buffer = io.BytesIO()
        # processed_image.save(buffer, format='JPEG', quality=95)
        # buffer.seek(0)
        # processed_user_image_bytes = buffer.read()

        userPose = await generate_poses(user_image_bytes)

        # Compare and generate output image
        horizontal, score, guide = compare_keypoints(
            modelPose["poses"], userPose, resize_image(modelImage), resize_image(userImg)
        )

        # Convert final image to base64
        output_buffer = io.BytesIO()
        Image.fromarray(horizontal).save(output_buffer, format="JPEG")
        #Image.fromarray(cv2.cvtColor(horizontal, cv2.COLOR_BGR2RGB)).save(output_buffer, format="JPEG")
        encoded_image = base64.b64encode(output_buffer.getvalue()).decode("utf-8")
        
        if not math.isfinite(score):  # catches NaN, inf, -inf
            score = 1
        return JSONResponse(content={
            "image_base64": encoded_image,
            "score": round(score, 2),
            "guide": guide
        })

    except Exception as e:
        import traceback
        print("Error during /compare:\n", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
