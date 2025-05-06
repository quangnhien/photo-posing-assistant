import faiss
import numpy as np
from pymongo import MongoClient

# 1. Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["your_db"]
collection = db["your_collection"]

# 2. Load image vectors and their IDs
docs = list(collection.find({}, {"_id": 1, "image_vector": 1}))
ids = [str(doc["_id"]) for doc in docs]
vectors = np.array([doc["image_vector"] for doc in docs]).astype("float32")

# 3. Create FAISS index
dimension = vectors.shape[1]
index = faiss.IndexFlatL2(dimension)  # You can use IndexIVFFlat for large datasets
index.add(vectors)

# 4. Perform a search
query_vector = np.array([[...]]).astype("float32")  # Your query image embedding
k = 5  # Number of results
distances, indices = index.search(query_vector, k)

# 5. Get the top matching document IDs
matched_ids = [ids[i] for i in indices[0]]
results = list(collection.find({"_id": {"$in": [ObjectId(mid) for mid in matched_ids]}}))
