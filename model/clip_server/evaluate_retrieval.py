import os
from PIL import Image
from tqdm import tqdm
from collections import defaultdict

import torch
import torch.nn.functional as F
from torchvision import transforms, models
import torch.nn as nn

# ==== Setup Transform and Device ====
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ==== Define Embedding Extractor ====
class EfficientNetEmbeddingExtractor(nn.Module):
    def __init__(self, model):
        super().__init__()
        self.features = model.features
        self.avgpool = model.avgpool
        self.flatten = nn.Flatten()
        self.dropout = model.classifier[0]

    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        x = self.flatten(x)
        x = self.dropout(x)
        return x

# ==== Load Model ====
base_model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAUL)
base_model.classifier[1] = nn.Linear(base_model.classifier[1].in_features, 1000)  # dummy
base_model.load_state_dict(torch.load("efficientnet_b0_landmark.pth", map_location=device))
base_model.eval()
embedding_model = EfficientNetEmbeddingExtractor(base_model).to(device)

# ==== Load Images and Labels ====
image_folder = "../../../images/"
image_paths = []
labels = []
label_map = {}

for label in os.listdir(image_folder):
    label_path = os.path.join(image_folder, label)
    if not os.path.isdir(label_path): continue
    for fname in os.listdir(label_path):
        if fname.endswith(".jpg"):
            path = os.path.join(label_path, fname)
            image_paths.append(path)
            labels.append(label)
            label_map[path] = label

# ==== Compute Embeddings ====
embeddings = []
for path in tqdm(image_paths, desc="Extracting embeddings"):
    image = Image.open(path).convert("RGB")
    x = transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        emb = embedding_model(x)
        emb = F.normalize(emb, dim=-1)  # L2 normalize
        embeddings.append(emb.squeeze().cpu())

embedding_db = torch.stack(embeddings)
label_db = labels

# ==== Evaluation Loop ====
top1_correct = 0
top5_correct = 0
n = len(image_paths)

print("Evaluating retrieval...")
for i, query_emb in enumerate(tqdm(embedding_db)):
    true_label = label_db[i]

    sims = F.cosine_similarity(query_emb.unsqueeze(0), embedding_db)  # (N,)
    sims[i] = -1.0  # exclude self

    topk = torch.topk(sims, k=5).indices
    topk_labels = [label_db[j] for j in topk]

    if topk_labels[0] == true_label:
        top1_correct += 1
    if true_label in topk_labels:
        top5_correct += 1

top1_acc = top1_correct / n
top5_acc = top5_correct / n

print(f"\n✅ Top-1 Accuracy: {top1_acc:.4f}")
print(f"✅ Top-5 Accuracy: {top5_acc:.4f}")
