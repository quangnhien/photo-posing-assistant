import os
import pandas as pd
from PIL import Image
from tqdm import tqdm

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models

import mlflow
import mlflow.pytorch

# ===================== Dataset =====================
class LandmarkDataset(Dataset):
    def __init__(self, csv_path, images_dir, transform=None):
        self.data = pd.read_csv(csv_path)
        self.images_dir = images_dir
        self.transform = transform
        self.label2idx = {label: idx for idx, label in enumerate(sorted(self.data['landmark_id'].unique()))}
        self.data['label'] = self.data['landmark_id'].map(self.label2idx)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        img_path = os.path.join(self.images_dir, row['name'] + ".jpg")
        image = Image.open(img_path).convert("RGB")
        label = row['label']
        if self.transform:
            image = self.transform(image)
        return image, label

# ===================== Transforms =====================
train_transform = transforms.Compose([
    transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(0.2, 0.2, 0.2, 0.1),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# ===================== Evaluation =====================
def evaluate(model, loader, device):
    model.eval()
    total, correct = 0, 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            preds = torch.argmax(logits, dim=1)
            correct += (preds == y).sum().item()
            total += y.size(0)
    return correct / total

# ===================== Early Stopping =====================
class EarlyStopping:
    def __init__(self, patience=3):
        self.patience = patience
        self.counter = 0
        self.best_score = None

    def step(self, val_score):
        if self.best_score is None or val_score > self.best_score:
            self.best_score = val_score
            self.counter = 0
            return False  # No early stop
        else:
            self.counter += 1
            return self.counter >= self.patience

# ===================== Training =====================
def train(model, train_loader, val_loader, optimizer, criterion, epochs, device):
    early_stopper = EarlyStopping(patience=3)
    for epoch in range(epochs):
        model.train()
        total_loss, total, correct = 0, 0, 0
        loop = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}")
        for x, y in loop:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            loss = criterion(logits, y)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * x.size(0)
            preds = torch.argmax(logits, dim=1)
            correct += (preds == y).sum().item()
            total += y.size(0)

            loop.set_postfix(loss=total_loss/total, acc=100*correct/total)

        train_acc = correct / total
        train_loss = total_loss / total
        val_acc = evaluate(model, val_loader, device)

        print(f"Epoch {epoch+1}: Train Acc = {train_acc:.4f}, Val Acc = {val_acc:.4f}")

        mlflow.log_metric("train_loss", train_loss, step=epoch)
        mlflow.log_metric("train_acc", train_acc, step=epoch)
        mlflow.log_metric("val_acc", val_acc, step=epoch)

        if early_stopper.step(val_acc):
            print("Early stopping triggered.")
            break

# ===================== Main Script =====================
def main():
    train_csv = "train.csv"
    val_csv = "val.csv"
    # test_csv = "test.csv"
    image_dir = "images"

    train_dataset = LandmarkDataset(train_csv, image_dir, transform=train_transform)
    val_dataset = LandmarkDataset(val_csv, image_dir, transform=val_transform)
    # test_dataset = LandmarkDataset(test_csv, image_dir, transform=val_transform)

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False, num_workers=4)
    # test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=4)

    num_classes = len(train_dataset.label2idx)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    base_model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
    in_features = base_model.classifier[1].in_features
    base_model.classifier = nn.Sequential(
        nn.Dropout(p=0.2),
        nn.Linear(in_features, 512),
        nn.ReLU(),
        nn.Linear(512, num_classes)
    )
    model = base_model.to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
    criterion = nn.CrossEntropyLoss()

    mlflow.set_experiment("landmark-efficientnet")

    with mlflow.start_run():
        mlflow.log_param("model", "efficientnet_b0_custom")
        mlflow.log_param("epochs", 100)
        mlflow.log_param("batch_size", 32)
        mlflow.log_param("learning_rate", 1e-4)

        train(model, train_loader, val_loader, optimizer, criterion, epochs=10, device=device)

        # test_acc = evaluate(model, test_loader, device)
        # print(f"Test Accuracy: {test_acc:.4f}")
        # mlflow.log_metric("test_acc", test_acc)

        torch.save(model.state_dict(), "efficientnet_b0_landmark.pth")
        mlflow.log_artifact("efficientnet_b0_landmark.pth")
        mlflow.pytorch.log_model(model, "model")

if __name__ == "__main__":
    main()
