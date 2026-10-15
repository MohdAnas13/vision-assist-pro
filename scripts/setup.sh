#!/bin/bash
echo "🚀 Setting up Vision Assistant..."
pip install -r requirements.txt
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
mkdir -p logs data/images data/videos data/results
echo "✅ Setup complete!"