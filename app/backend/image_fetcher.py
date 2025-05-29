import os
from typing import List
import requests
from predictor import predict_location_and_pose
from dotenv import load_dotenv

load_dotenv()

UNSPLASH_API_KEY = os.getenv('UNSPLASH_API_KEY')
UNSPLASH_URL = os.getenv('UNSPLASH_URL', "https://api.unsplash.com")

def fetch_unsplash_images(query: str, page: int, per_page: int = 10):
    if not UNSPLASH_API_KEY:
        raise ValueError("Unsplash API key not found")

    headers = {"Authorization": f"Client-ID {UNSPLASH_API_KEY}"}
    params = {
        "query": query,
        "page": page,
        "per_page": per_page,
        "orientation": "portrait"
    }

    response = requests.get(f"{UNSPLASH_URL}/search/photos", headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    images = []
    for photo in data.get("results", []):
        images.append({
            "url": photo["urls"]["regular"],
            "description": photo.get("description") or photo.get("alt_description") or "No description",
            "photographer": photo["user"]["name"],
            "link": photo["links"]["html"]
        })
    return images

def fetch_location_pose_images(location: str, page: int, per_page: int):
    query = f"{location}, a person"
    count = 0
    max_attempts = 5

    while count < max_attempts:
        images = fetch_unsplash_images(query, UNSPLASH_API_KEY, page + count, per_page)
        results = []

        for img in images:
            predicted_pose = predict_location_and_pose(img["url"], img.get("description", ""))
            if predicted_pose == "Correct location and pose":
                img["pose"] = predicted_pose
                results.append(img)

        if results:
            return {
                "images": results,
                "currentPage": page + count
            }

        count += 1

    return {
        "images": [],
        "currentPage": page + count
    }
