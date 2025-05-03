from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import motor.motor_asyncio
from torchvision import transforms
from PIL import Image
from azure.storage.blob import BlobServiceClient
import io
import os
from dotenv import load_dotenv
from datetime import datetime
import uuid
import httpx

load_dotenv()

app = FastAPI()

# MongoDB connection
client = motor.motor_asyncio.AsyncIOMotorClient(f"mongodb+srv://{os.getenv('MONGOBD_USER')}:{os.getenv('MONGOBD_PASSWORD')}@mwa.ah6ka.mongodb.net/?retryWrites=true&w=majority&appName=MWA")
db = client.get_database('posingassistant')
poses_collection = db.get_collection('posegallery')

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
AZURE_STORAGE_CONTAINER_NAME = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(AZURE_STORAGE_CONTAINER_NAME)



# Resize + CenterCrop Transform (for processed image saved to Azure)
resize_crop_transform = transforms.Compose([
    transforms.Resize(384, interpolation=transforms.InterpolationMode.BICUBIC),
    transforms.CenterCrop(384),
])


# Helper: Embed Image (for vector embedding only)
async def embed_image(image_bytes):
    async with httpx.AsyncClient() as client:
        files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
        response = await client.post(os.getenv('CLIP_ENDPOINT'), files=files)
        if response.status_code == 200:
            return response.json()['vector']
        else:
            raise Exception(f"CLIP Server Error: {response.text}")
        
# Helper: Extract pose
async def generate_poses(image_bytes):
    async with httpx.AsyncClient() as client:
        files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
        response = await client.post(os.getenv('POSE_ENDPOINT'), files=files)
        if response.status_code == 200:
            return response.json()['vector']
        else:
            raise Exception(f"CLIP Server Error: {response.text}")

# Helper: Generate Tags from Image
async def generate_tags_from_image(image_bytes):
    async with httpx.AsyncClient() as client:
        files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
        response = await client.post(os.getenv('BLIP2_ENDPOINT'), files=files)
        if response.status_code == 200:
            caption = response.json()['caption']
            # Simple tag splitting
            tags = caption.lower().replace(',', '').split(' ')
            tags = [tag for tag in tags if tag]
            return tags
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
        original_contents = await file.read()

        # Open original image
        image = Image.open(io.BytesIO(original_contents)).convert('RGB')

        # Resize + CenterCrop to 224x224
        processed_image = resize_crop_transform(image)

        # Save processed image to bytes buffer
        buffer = io.BytesIO()
        processed_image.save(buffer, format='JPEG', quality=95)  # You can adjust quality
        buffer.seek(0)
        processed_image_bytes = buffer.read()

        # Upload processed image to Azure
        azure_url = await upload_to_azure(processed_image_bytes)

        # Generate tags (use original full image or processed one — your choice)
        tags = await generate_tags_from_image(original_contents)
        
        # Extrect poses (use processed 224x224 image)
        poses = await embed_image(processed_image_bytes)
        
        # Generate vector (use processed 224x224 image)
        vector = await embed_image(processed_image_bytes)

        # Save everything to MongoDB
        pose_doc = {
            "image_url": azure_url,
            "tags": tags,
            "vector": vector,
            "poses":poses
        }
        await poses_collection.insert_one(pose_doc)

        return JSONResponse(content={"message": "Pose uploaded with auto-tags!", "tags": tags, "image_url": azure_url}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)