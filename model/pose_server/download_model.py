import os
import time
from azure.storage.blob import BlobClient
from azure.core.exceptions import ResourceNotFoundError, ServiceRequestError
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("MODEL_FILENAME")
MODEL_DIR = os.getenv("MODEL_DIR")

MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)

CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_MODEL_CONTAINER", "ai-models")
BLOB_NAME = os.getenv("AZURE_MODEL_BLOB_NAME", MODEL_NAME)

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

def download_model():
    if os.path.exists(MODEL_PATH):
        print(f"✅ Model already cached at {MODEL_PATH}")
        return MODEL_PATH

    print(f"⬇️  Downloading model '{MODEL_NAME}' from Azure Blob Storage...")

    os.makedirs(MODEL_DIR, exist_ok=True)
    retries = 0

    while retries < MAX_RETRIES:
        try:
            blob = BlobClient.from_connection_string(
                conn_str=CONNECTION_STRING,
                container_name=CONTAINER_NAME,
                blob_name=BLOB_NAME
            )

            with open(MODEL_PATH, "wb") as f:
                f.write(blob.download_blob().readall())

            print(f"✅ Model downloaded and saved to {MODEL_PATH}")
            return MODEL_PATH

        except (ServiceRequestError, ResourceNotFoundError) as e:
            retries += 1
            print(f"⚠️  Attempt {retries} failed: {e}")
            if retries < MAX_RETRIES:
                print(f"🔁 Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print("❌ Failed to download model after multiple attempts.")
                raise

if __name__ == "__main__":
    download_model()
