import numpy as np
import mediapipe as mp
import cv2
import requests

def analyze_pose_and_description(image_url: str):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)
    
    try:
        response = requests.get(image_url)
        image_array = np.frombuffer(response.content, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if not results.pose_landmarks:
            return "No human pose detected"

        landmarks = results.pose_landmarks.landmark
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
        right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]

        if left_elbow.y < left_shoulder.y or right_elbow.y < right_shoulder.y:
            return "Pose: One or both arms raised, possibly pointing or waving"
        elif abs(left_shoulder.x - right_shoulder.x) > 0.3:
            return "Pose: Sideways or angled stance"
        elif left_hip.y - left_shoulder.y < 0.5:
            return "Pose: Sitting or crouching"
        else:
            return "Pose: Standing or neutral position"

    except Exception as e:
        return f"Error analyzing image: {e}"
    finally:
        pose.close()
