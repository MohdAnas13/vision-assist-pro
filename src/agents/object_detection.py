# src/agents/object_detection.py
from ultralytics import YOLO
import cv2
import torch
import logging
import os

class ObjectDetectionAgent:
    """Agent 2: YOLOv8 object detection"""
    
    def __init__(self, model_path="models/yolov8n.pt", conf_threshold=0.5):
        # Download model if not exists
        if not os.path.exists(model_path):
            print(f"📥 Downloading YOLOv8 model to {model_path}...")
            self.model = YOLO('yolov8n.pt')
        else:
            self.model = YOLO(model_path)
            
        self.conf_threshold = conf_threshold
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.logger = logging.getLogger(__name__)
        print(f"✅ YOLOv8 loaded on {self.device}")
        
        self.class_names = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
            'train', 'truck', 'boat', 'traffic light', 'fire hydrant',
            'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog',
            'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe',
            'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
            'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat',
            'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
            'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
            'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot',
            'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
            'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
            'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven',
            'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase',
            'scissors', 'teddy bear', 'hair drier', 'toothbrush'
        ]
        
    def detect(self, frame):
        """Detect objects in frame"""
        if frame is None:
            return []
            
        results = self.model(frame, conf=self.conf_threshold)
        
        detections = []
        for r in results:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = self.class_names[class_id]
                    
                    detections.append({
                        'bbox': [x1, y1, x2, y2],
                        'confidence': confidence,
                        'class_id': class_id,
                        'class_name': class_name,
                        'center': [(x1 + x2) / 2, (y1 + y2) / 2]
                    })
        
        return detections