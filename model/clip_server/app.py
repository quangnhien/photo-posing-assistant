from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torch
import io
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
        starting_time = time()
        contents = await file.read()
        vector = embed_image(contents)
        
        #Prometheus log
        label = {"api": "/clip"}
        # Increase the counter
        counter.add(10, label)
        # Mark the end of the response
        ending_time = time()
        elapsed_time = ending_time - starting_time
        # Add histogram
        histogram.record(elapsed_time, label)

        return JSONResponse(content={"vector": vector}, status_code=200)
    except Exception as e:
        raise
        return JSONResponse(content={"error": str(e)}, status_code=500)
