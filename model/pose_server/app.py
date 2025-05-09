from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)
index_map = {
    0: 0,    # Nose
    2: 15,    # Left Eye
    5: 14,    # Right Eye
    7: 17,    # Left Ear
    8: 16,    # Right Ear
    11: 5,   # Left Shoulder
    12: 2,   # Right Shoulder
    13: 6,   # Left Elbow
    14: 3,   # Right Elbow
    15: 7,   # Left Wrist
    16: 4,  # Right Wrist
    23: 11,  # Left Hip
    24: 8,  # Right Hip
    25: 12,  # Left Knee
    26: 9,  # Right Knee
    27: 13,  # Left Ankle
    28: 10   # Right Ankle
}


def convert_mediapipe_to_openpose(landmarks, image_width, image_height, visibility_threshold=0.5):

    keypoints = np.zeros((18, 3), dtype=np.float32)

    # Map known keypoints
    for mp_idx, op_idx in index_map.items():
        lm = landmarks[mp_idx]
        if lm.visibility > visibility_threshold:
            keypoints[op_idx] = [
                int(lm.x * image_width), int(lm.y * image_height), lm.visibility]

    # Compute neck (index 17) only if both shoulders are valid
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]
    if left_shoulder.visibility > visibility_threshold and right_shoulder.visibility > visibility_threshold:
        neck_x = int((left_shoulder.x + right_shoulder.x) / 2 * image_width)
        neck_y = int((left_shoulder.y + right_shoulder.y) / 2 * image_height)
        keypoints[1] = [neck_x, neck_y,
                        (left_shoulder.visibility+right_shoulder.visibility)/2]

    return keypoints


app = FastAPI(root_path="/")

# @app.post("/compare")
# async def compare(img1: UploadFile = File(...),img2: UploadFile = File(...)):
#     img1 = await img1.read()
#     img1 = np.frombuffer(img1, np.uint8)
#     img1 = cv2.imdecode(img1, cv2.IMREAD_COLOR)
#     scale1 =config.standard_image_shape/ img1.shape[0]
#     img1 = cv2.resize(img1,None,fx=scale1,fy=scale1)

#     img2 = await img2.read()
#     img2 = np.frombuffer(img2, np.uint8)
#     img2 = cv2.imdecode(img2, cv2.IMREAD_COLOR)
#     scale2 =config.standard_image_shape/ img2.shape[0]
#     img2 = cv2.resize(img2,None,fx=scale2,fy=scale2)

#     canvas,score,guide = comparision_model.compare(img1,img2)

#     return score,guide

# @app.post("/generate_keypoints")
# async def compare(file: UploadFile = File(...)):
#     try:
#         contents = await file.read()
#         contents = np.frombuffer(contents, np.uint8)
#         contents = cv2.imdecode(contents, cv2.IMREAD_COLOR)
#         scale =config.standard_image_shape/ contents.shape[0]
#         contents = cv2.resize(contents,None,fx=scale,fy=scale)
#         vector = comparision_model.generateKeypoints(contents)
#         return JSONResponse(content={"keypoints": vector.tolist()}, status_code=200)
#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/generate_keypoints")
async def compare(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        contents = np.frombuffer(contents, np.uint8)
        contents = cv2.imdecode(contents, cv2.IMREAD_COLOR)
        contents = cv2.cvtColor(contents, cv2.COLOR_BGR2RGB)

        results = pose.process(contents)

        vector = convert_mediapipe_to_openpose(
            results.pose_landmarks.landmark, contents.shape[1], contents.shape[0])
        return JSONResponse(content={"keypoints": vector.tolist()}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
