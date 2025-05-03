from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import config
from src.body import Body 
import cv2
import numpy as np

comparision_model = Body('model/body_pose_model.pth')
cache = {}

app = FastAPI(root_path="/")

@app.post("/compare")
async def compare(img1: UploadFile = File(...),img2: UploadFile = File(...)):
    img1 = await img1.read()
    img1 = np.frombuffer(img1, np.uint8)
    img1 = cv2.imdecode(img1, cv2.IMREAD_COLOR)
    scale1 =config.standard_image_shape/ img1.shape[0]
    img1 = cv2.resize(img1,None,fx=scale1,fy=scale1)
    
    img2 = await img2.read()
    img2 = np.frombuffer(img2, np.uint8)
    img2 = cv2.imdecode(img2, cv2.IMREAD_COLOR)
    scale2 =config.standard_image_shape/ img2.shape[0]
    img2 = cv2.resize(img2,None,fx=scale2,fy=scale2)
    
    canvas,score,guide = comparision_model.compare(img1,img2)
    
    return score,guide

@app.post("/generate_keypoints")
async def compare(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        contents = np.frombuffer(contents, np.uint8)
        contents = cv2.imdecode(contents, cv2.IMREAD_COLOR)
        scale =config.standard_image_shape/ contents.shape[0]
        contents = cv2.resize(contents,None,fx=scale,fy=scale)
        vector = comparision_model.generateKeypoints(contents)
        return JSONResponse(content={"keypoints": vector.tolist()}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)