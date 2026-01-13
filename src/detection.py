import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
from ultralytics import YOLO
import numpy as np

# --- 1. ARCHITEKTURA MODELU KLASYFIKACJI ---
class MyCnn_model(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(32),
            nn.MaxPool2d(2, padding=1),
            
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(64),
            nn.MaxPool2d(2, padding=1),
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(128),
            nn.MaxPool2d(2, padding=1),
            
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(256),
            nn.MaxPool2d(2, padding=1),
            
            nn.Conv2d(256, 512, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(512),
            nn.MaxPool2d(2, padding=1)
        )
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

# --- 2. LISTA KLAS ---
CLASS_NAMES = [
    "Asian Green Bee Eater", "Brown Headed Barbet", "Cattle Egret",
    "Common Kingfisher", "Common Myna", "Common Rosefinch",
    "Common Tailorbird", "Coppersmith Barbet", "Forest Wagtail",
    "Gray Wagtail", "Hoopoe", "House Crow",
    "Indian Grey Hornbill", "Indian Peacock", "Indian Pitta",
    "Indian Roller", "Jungle Babbler", "Northern Lapwing",
    "Red Wattled Lapwing", "Ruddy Shelduck", "Rufous Treepie",
    "Sarus Crane", "White Breasted Kingfisher",
    "White Breasted Waterhen", "White Wagtail"
]

class BirdDetector:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.yolo_model = None
        self.classifier_model = None
        self.load_models()

    def load_models(self):
        print("Loading YOLO model...")
        try:
            self.yolo_model = YOLO("trained_models/Bird_Detector.pt")
        except Exception as e:
            print(f"Error loading YOLO: {e}")

        print("Loading Classifier model...")
        try:
            self.classifier_model = MyCnn_model(num_classes=len(CLASS_NAMES)).to(self.device)
            self.classifier_model.load_state_dict(
                torch.load("trained_models/Indian_Bird_Identifier_model.pth", map_location=self.device)
            )
            self.classifier_model.eval()
        except Exception as e:
            print(f"Error loading Classifier: {e}")

    def detect_bbox(self, image_path):
        """
        Zwraca: (bbox, confidence)
        bbox: [x1, y1, x2, y2]
        confidence: float (0.0 - 1.0)
        """
        if not self.yolo_model:
            return None, 0.0
        
        results = self.yolo_model(image_path)
        if len(results) > 0 and len(results[0].boxes) > 0:
            box = results[0].boxes[0].xyxy.cpu().numpy()[0]
            conf = results[0].boxes[0].conf.cpu().numpy()[0] # Pobranie pewności detekcji
            return box, float(conf)
        return None, 0.0

    def classify_species(self, image_path, bbox=None):
        """
        Zwraca: (class_name, confidence)
        """
        if not self.classifier_model:
            return "Model Error", 0.0

        try:
            img = Image.open(image_path).convert("RGB")

            if bbox is not None:
                x1, y1, x2, y2 = map(int, bbox)
                w, h = img.size
                x1 = max(0, x1); y1 = max(0, y1)
                x2 = min(w, x2); y2 = min(h, y2)
                if x2 > x1 and y2 > y1:
                    img = img.crop((x1, y1, x2, y2))

            preprocess = transforms.Compose([
                transforms.Resize((64, 64)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                     std=[0.229, 0.224, 0.225])
            ])

            input_tensor = preprocess(img).unsqueeze(0).to(self.device)

            with torch.no_grad():
                outputs = self.classifier_model(input_tensor)
                # Używamy Softmax, aby uzyskać procenty
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                max_prob, predicted_idx = torch.max(probabilities, 1)
                
                idx = predicted_idx.item()
                conf = max_prob.item()

            if idx < len(CLASS_NAMES):
                return CLASS_NAMES[idx], conf
            else:
                return f"Unknown Class ID: {idx}", 0.0
        except Exception as e:
            print(f"Prediction Error: {e}")
            return "Error", 0.0