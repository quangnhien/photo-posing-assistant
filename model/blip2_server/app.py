from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration,GPT2Tokenizer,BertTokenizerFast
import torch
import io
from string import punctuation

import nltk
from nltk.tokenize import word_tokenize
from time import time
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from prometheus_client import start_http_server

# Start Prometheus client
start_http_server(port=8099, addr="0.0.0.0")
# Service name is required for most backends
resource = Resource(attributes={SERVICE_NAME: "pose-service"})
# Exporter to export metrics to Prometheus
reader = PrometheusMetricReader()
# Meter is responsible for creating and recording metrics
provider = MeterProvider(resource=resource, metric_readers=[reader])
set_meter_provider(provider)
meter = metrics.get_meter("pose", "0.1.2")

# Create your first counter
counter = meter.create_counter(
    name="pose_request_counter",
    description="Number of POSE requests"
)

histogram = meter.create_histogram(
    name="pose_response_histogram",
    description="POSE response histogram",
    unit="seconds",
)

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
        starting_time = time()
        contents = await file.read()
        caption = generate_caption(contents)
        
        #Prometheus log
        label = {"api": "/blip"}
        # Increase the counter
        counter.add(10, label)
        # Mark the end of the response
        ending_time = time()
        elapsed_time = ending_time - starting_time
        # Add histogram
        histogram.record(elapsed_time, label)
        return JSONResponse(content={"caption": caption}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
