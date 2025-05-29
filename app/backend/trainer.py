import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sentence_transformers import SentenceTransformer
import motor.motor_asyncio
import os

text_model = SentenceTransformer('all-MiniLM-L6-v2')
clf = RandomForestClassifier(n_estimators=100, random_state=42)
pose_category_columns = None
client = motor.motor_asyncio.AsyncIOMotorClient(
    f"mongodb+srv://{os.getenv('MONGOBD_USER')}:{os.getenv('MONGOBD_PASSWORD')}@mwa.ah6ka.mongodb.net/?retryWrites=true&w=majority&appName=MWA")
db = client.get_database('posingassistant')
poses_collection = db.get_collection('poses')

async def load_pose_dataset():
    docs = await poses_collection.find().to_list(length=None)
    return pd.DataFrame(docs)

async def train_pose_model():
    global pose_category_columns
    df = await load_pose_dataset()

    embeddings = text_model.encode(df['description'].tolist())
    pose_categories = pd.get_dummies(df['pose'])
    X = np.hstack([embeddings, pose_categories.values])
    y = df['label'].values

    pose_category_columns = pose_categories.columns
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    clf.fit(X_train, y_train)
    print("Training complete. Accuracy:", accuracy_score(y_test, clf.predict(X_test)))

    return clf, pose_category_columns
