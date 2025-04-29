from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration,GPT2Tokenizer,BertTokenizerFast
import torch
import io

app = FastAPI()

# Load BLIP-2 Model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)


@app.get("/health")
async def health():
    return {"status": "ok"}

def generate_caption(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    inputs = blip_processor(image, return_tensors="pt").to(device)

    with torch.no_grad():
        output = blip_model.generate(**inputs, max_new_tokens=50)

    caption = blip_processor.decode(output[0], skip_special_tokens=True)
    return caption

@app.post("/generate_caption")
async def generate_caption_api(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        caption = generate_caption(contents)
        return JSONResponse(content={"caption": caption}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
