from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torch
import io

app = FastAPI()

# Load CLIP model ONCE when server starts
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Only normalize (no resize, you handle resize before sending)
def embed_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    inputs = clip_processor(images=image, return_tensors="pt").to(device)
    with torch.no_grad():
        image_features = clip_model.get_image_features(**inputs)
    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
    return image_features.squeeze().cpu().tolist()

@app.post("/clip_embed")
async def clip_embed(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        vector = embed_image(contents)
        return JSONResponse(content={"vector": vector}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
