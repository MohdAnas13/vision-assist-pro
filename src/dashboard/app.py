# src/dashboard/app.py
from flask import Flask, render_template, Response, jsonify
import cv2
import sys
import os
import threading
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.video_capture import VideoCaptureAgent
from agents.object_detection import ObjectDetectionAgent
from agents.spatial_metadata import SpatialMetadataAgent
from agents.risk_engine import RiskEngineAgent
from agents.generative_ai import GenerativeAIAgent
from agents.audio_output import AudioOutputAgent
from agents.logging_agent import LoggingAgent
from utils.config_loader import ConfigLoader

app = Flask(__name__)

# Load configuration
config_loader = ConfigLoader('config.json')
config = config_loader.load()

# Initialize agents
video_agent = VideoCaptureAgent()
detection_agent = ObjectDetectionAgent(config['model']['yolo_path'])
spatial_agent = SpatialMetadataAgent()
risk_agent = RiskEngineAgent(config)
# Initialize AI agent only if API key is available
gemini_key = config.get('api', {}).get('gemini_api_key')
ai_agent = GenerativeAIAgent(gemini_key) if gemini_key else None
audio_agent = AudioOutputAgent()
logging_agent = LoggingAgent()

# Global variables
current_frame = None
current_detections = []
current_risks = []
scene_description = "System ready. Click 'Describe Scene' for AI description."
processing = False

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html', 
                         app_name=config['app_name'])

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/status')
def get_status():
    """Get current system status"""
    return jsonify({
        'detections': len(current_detections),
        'risks': len(current_risks),
        'description': scene_description,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/risks')
def get_risks():
    """Get current risks"""
    return jsonify({
        'risks': current_risks,
        'count': len(current_risks)
    })

@app.route('/api/describe')
def trigger_description():
    """Trigger scene description"""
    global scene_description
    if current_frame is not None:
        spatial_data = []
        for det in current_detections:
            distance = spatial_agent.estimate_distance(det['bbox'], det['class_name'])
            position = spatial_agent.calculate_position(det['bbox'])
            spatial_data.append({
                'distance': distance,
                'position': position
            })
            
        if ai_agent is not None:
            description = ai_agent.describe_scene(
                current_frame, 
                current_detections, 
                current_risks,
                spatial_data
            )
            scene_description = description['description']
            audio_agent.speak(scene_description, priority=3)
        else:
            scene_description = "AI description unavailable: no Gemini API key configured."
    return jsonify({'description': scene_description})

def generate_frames():
    """Generate video frames with overlays"""
    global current_frame, current_detections, current_risks, processing

    # Start agents once before the loop, not on every iteration
    if not getattr(generate_frames, '_started', False):
        video_agent.start()
        audio_agent.start()
        generate_frames._started = True

    while True:
        frame = video_agent.get_frame()
        if frame is None:
            continue
            
        current_frame = frame.copy()
        
        # Process frame
        if not processing:
            processing = True
            thread = threading.Thread(target=process_frame, args=(frame.copy(),))
            thread.start()
        
        # Draw detections
        for detection in current_detections:
            x1, y1, x2, y2 = map(int, detection['bbox'])
            class_name = detection['class_name']
            conf = detection['confidence']
            
            # Determine color
            color = (67, 97, 238)  # Blue
            for risk in current_risks:
                if risk.get('class_name') == class_name:
                    if risk['risk_level'] == 'CRITICAL':
                        color = (0, 0, 255)  # Red
                    elif risk['risk_level'] == 'HIGH':
                        color = (0, 165, 255)  # Orange
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{class_name}", (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def process_frame(frame):
    """Process frame in background"""
    global current_detections, current_risks, processing
    
    try:
        # Detect objects
        detections = detection_agent.detect(frame)
        
        # Get spatial data
        spatial_data = []
        for det in detections:
            distance = spatial_agent.estimate_distance(det['bbox'], det['class_name'])
            position = spatial_agent.calculate_position(det['bbox'])
            spatial_data.append({
                'distance': distance,
                'position': position
            })
        
        # Analyze risks
        risks = risk_agent.analyze_risks(detections, spatial_data)
        
        # Update globals
        current_detections = detections
        current_risks = risks
        
        # Speak critical risks
        for risk in risks:
            if risk['risk_level'] == 'CRITICAL':
                audio_agent.speak(risk['action'], priority=1, interrupt=True)
            elif risk['risk_level'] == 'HIGH':
                audio_agent.speak(risk['action'], priority=2)
        
    except Exception as e:
        logging_agent.log_error(str(e))
    finally:
        processing = False

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)