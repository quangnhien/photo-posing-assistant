from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration,GPT2Tokenizer,BertTokenizerFast
import torch
import io
from string import punctuation

import nltk
from nltk.tokenize import word_tokenize


app = FastAPI()
STOP_WORDS = {
    'a', 'an', 'and', 'the', 'is', 'are', 'was', 'were', 'in', 'on', 'of', 'for',
    'with', 'to', 'at', 'from', 'by', 'as', 'that', 'this', 'it', 'be', 'or', 'not',
    'has', 'have', 'had', 'but', 'if', 'they', 'he', 'she', 'we', 'you', 'i'
}

NOUN_TAGS = {'NN', 'NNS', 'NNP', 'NNPS'}
ADJ_TAGS = {'JJ', 'JJR', 'JJS'}
# Load BLIP-2 Model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)


@app.get("/health")
async def health():
    return {"status": "ok"}

def extract_tags_from_caption(caption):
    words = word_tokenize(caption.lower())
    words = [w for w in words if w not in STOP_WORDS and w not in punctuation]
    pos_tags = nltk.pos_tag(words)

    tags = [word for word, pos in pos_tags if pos in NOUN_TAGS or pos in ADJ_TAGS]
    return tags

def generate_caption(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    inputs = blip_processor(image, return_tensors="pt").to(device)

    with torch.no_grad():
        output = blip_model.generate(**inputs, max_new_tokens=50)

    caption = blip_processor.decode(output[0], skip_special_tokens=True)

    tags = extract_tags_from_caption(caption)
    return tags

@app.post("/generate_caption")
async def generate_caption_api(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        caption = generate_caption(contents)
        return JSONResponse(content={"caption": caption}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
