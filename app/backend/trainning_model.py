import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd
import mediapipe as mp
import cv2
import numpy as np
import requests

def analyze_pose_and_description(image_url):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)
    
    try:
        # Load and process image for pose analysis
        response = requests.get(image_url)
        response.raise_for_status()
        image_array = np.frombuffer(response.content, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Analyze pose
        results = pose.process(image_rgb)
        pose_result = "No human pose detected"
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
            right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
            left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
            
            if left_elbow.y < left_shoulder.y or right_elbow.y < right_shoulder.y:
                pose_result = "Pose: One or both arms raised, possibly pointing or waving"
            elif abs(left_shoulder.x - right_shoulder.x) > 0.3:
                pose_result = "Pose: Sideways or angled stance"
            elif left_hip.y - left_shoulder.y < 0.5:
                pose_result = "Pose: Sitting or crouching"
            else:
                pose_result = "Pose: Standing or neutral position"
        
        # Combine description and pose result
        return pose_result
    
    except Exception as e:
        return f"Error analyzing image: {e}"
    
    finally:
        pose.close()

# Sample dataset (replace with your data)
data = [
    {"description": "A person standing in a park with one arm raised", "pose": "Pose: One or both arms raised, possibly pointing or waving", "label": 1},
    {"description": "A person sitting in a room", "pose": "Pose: Sitting or crouching", "label": 0},
    # Add more samples
]

# Convert to DataFrame
df = pd.DataFrame(data)

# Load SentenceTransformer for text embeddings
text_model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings for descriptions
description_embeddings = text_model.encode(df['description'].tolist())

# Convert pose to categorical features (e.g., one-hot encoding)
pose_categories = pd.get_dummies(df['pose'])

# Combine features
X = np.hstack([description_embeddings, pose_categories.values])
y = df['label'].values

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Evaluate
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy}")

# Function to predict for a new image
def predict_location_and_pose(image_url, description):
    poseResult = analyze_pose_and_description(image_url)
    if isinstance(poseResult, dict):
        description = description
        pose = poseResult
        
        # Generate features
        desc_embedding = text_model.encode([description])
        pose_feature = pd.get_dummies(pd.Series([pose]), columns=pose_categories.columns).values
        features = np.hstack([desc_embedding, pose_feature])
        
        # Predict
        prediction = clf.predict(features)
        return "Correct location and pose" if prediction[0] == 1 else "Incorrect location or pose"
    return poseResult