import numpy as np
import pandas as pd
from trainer import text_model, clf, pose_category_columns
from analyzer import analyze_pose_and_description

def predict_location_and_pose(image_url: str, description: str):
    pose_result = analyze_pose_and_description(image_url)

    desc_embedding = text_model.encode([description])
    pose_feature = pd.get_dummies(pd.Series([pose_result]))

    for col in pose_category_columns:
        if col not in pose_feature:
            pose_feature[col] = 0
    pose_feature = pose_feature[pose_category_columns]

    features = np.hstack([desc_embedding, pose_feature.values])

    # Predict pose label instead of binary result
    predicted_label = clf.predict(features)[0]
    return predicted_label  # e.g., "sitting", "standing", etc.
