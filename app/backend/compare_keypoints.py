import openai
import numpy as np
import copy
import cv2

import os
from dotenv import load_dotenv
load_dotenv()

client = openai.OpenAI(api_key=os.getenv('GPT_API_KEY'))
limbSeqToCompare = [[2, 3], [2, 6], [3, 4], [4, 5], [6, 7], [7, 8], [2, 9], [9, 10], \
            [10, 11], [2, 12], [12, 13], [13, 14], [2, 1]]
joinName = {
    1: "Head",
    2: "Neck",
    3: "Right Shoulder",
    4: "Right Elbow",
    5: "Right Wrist",
    6: "Left Shoulder",
    7: "Left Elbow",
    8: "Left Wrist",
    9: "Right Hip",
    10: "Right Knee",
    11: "Right Ankle",
    12: "Left Hip",
    13: "Left Knee",
    14: "Left Ankle",
    15: "Right Eye",
    16: "Left Eye",
    17: "Right Ear",
    18: "Left Ear",   
}

def compare_keypoints(keypoints1,keypoints2,oriImg,compareImg,guide=True,gpt=True):

    vectors1 = getVectors(keypoints1,limbSeqToCompare)
    vectors2 = getVectors(keypoints2,limbSeqToCompare)

    if not guide:
        return getAngleSetAndScore(vectors1,vectors2)
    angles,score = getAngleSetAndScore(vectors1,vectors2)
    
    # find joints need to improve
    potential_pairs = np.array(limbSeqToCompare)[np.abs(angles)>10]
    potential_angles = angles[np.abs(angles)>10]
    potential_vectors = vectors2[np.abs(angles)>10]
    
    
    guide = ""
    canvas = copy.deepcopy(compareImg)
    for i in range(len(potential_pairs)):
        start_point = np.array(keypoints2[potential_pairs[i][1]-1][:2]).astype(int)
        if abs(potential_vectors[i][1])>abs(potential_vectors[i][0]):
            if potential_vectors[i][1]>0:
                end_point = [start_point[0] + int(potential_angles[i]/2),start_point[1]]
            else:
                end_point = [start_point[0] - int(potential_angles[i]/2),start_point[1]]
            direction = "left" if end_point[0]>start_point[0] else "right"
            guide = guide + f"Move your {joinName[potential_pairs[i][1]]} to the {direction} {determineSizeMoving(abs(potential_angles[i]))}. \n"
        else:
            if potential_vectors[i][0]<0:
                end_point = [start_point[0],start_point[1]+ int(potential_angles[i]/2)]
            else:
                end_point = [start_point[0],start_point[1]- int(potential_angles[i]/2)]
            direction = "down" if end_point[1]>start_point[1] else "up"
            guide = guide + f"Move your {joinName[potential_pairs[i][1]]} to the {direction} {determineSizeMoving(abs(potential_angles[i]))}. \n"
        color = (0, 255, 0) 
        thickness = 2
        tip_length = 0.5
        

        cv2.arrowedLine(canvas, start_point, end_point, color, thickness, tipLength=tip_length)

    # horizontal = cv2.hconcat([oriImg, compareImg, canvas])
    if gpt:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f'''You are a photographer and you are taking pictures of a client. 
                    You have provided them with a photo of a model with a nice pose and your client is copying that pose.
                    After taking the first photo, the matching score is {score}% and you want to ask the client to change a few things to get the perfect:
                    {guide}. Please make the tutorial more natural and concise
                    '''}
            ]
        )
        guide = response.choices[0].message.content
        
    
    return canvas, score, guide 
    
def getVectors(kps,limbSeq):
    return np.array([[kps[limbSeq[i][0]-1][0] - kps[limbSeq[i][1]-1][0],kps[limbSeq[i][0]-1][1] - kps[limbSeq[i][1]-1][1],kps[limbSeq[i][0]-1][2] + kps[limbSeq[i][1]-1][2]] if kps[limbSeq[i][0]-1][2]!=0 and kps[limbSeq[i][1]-1][2]!=0 else [0,0,0] for i in range(len(limbSeq))])
def getAngleSetAndScore(vect1,vect2):
    numerator = vect1[:,0]*vect2[:,1]-vect1[:,1]*vect2[:,0]
    denominator = np.sum(vect2[:,:2]*vect1[:,:2],1)
    angle = np.arctan2(denominator, numerator)
    angle = np.degrees(angle)
    # angle[angle!=0]-=90
    angle[angle>0]-=90
    angle[angle<-90]+=90
    print(angle)
    return angle,1-sum(np.abs(angle))/(sum(angle!=0)*90)
# def getAngleSetAndScore(vect1, vect2):
#     """
#     Computes angles between corresponding 2D vectors and returns a similarity score.
#     """
#     # Compute cross product (z-component) and dot product for angle
#     cross = vect1[:,0] * vect2[:,1] - vect1[:,1] * vect2[:,0]  # scalar cross product (2D)
#     dot = np.sum(vect1[:,:2] * vect2[:,:2], axis=1)           # dot product

#     # Compute angle in degrees
#     angles = np.degrees(np.arctan2(cross, dot))               # atan2(y, x)

#     # Score: how close angles are to 90°, normalized
#     non_zero_mask = angles != 0
#     angles_adj = np.abs(angles[non_zero_mask] - 90)

#     if angles_adj.size == 0:
#         return angles, 1.0  # perfect score if no angles deviate

#     score = 1 - np.sum(angles_adj) / (len(angles_adj) * 90)

#     return angles, score
def determineSizeMoving(angle):
    if angle<30:
        return "a little bit"
    else:
        return "quite a bit"