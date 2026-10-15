# 👁️ VisionAssist Pro — AI Navigation Assistant for Visually Impaired Persons

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![YOLOv8](https://img.shields.io/badge/YOLO-v8-green.svg)](https://github.com/ultralytics/ultralytics)
[![Flask](https://img.shields.io/badge/Flask-3.x-orange.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

An AI-powered navigation assistant that uses **real-time object detection**, **rule-based risk assessment**, and **natural language scene description** to help visually impaired persons navigate their surroundings safely.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [Testing](#-testing)
- [Project Structure](#-project-structure)
- [API Endpoints](#-api-endpoints)
- [Known Limitations](#-known-limitations)
- [Safety Disclaimer](#-safety-disclaimer)
- [License](#-license)

---

## 🌟 Features

### ✅ Verified Features

- **Real-time Object Detection** — YOLOv8 (Ultralytics) detects vehicles (car, truck, bus, motorcycle, bicycle) and pedestrians
- **Rule-Based Risk Engine** — configurable distance thresholds classify risks as `CRITICAL`, `HIGH`, or `MEDIUM` with priority-based navigation actions (STOP, MOVE LEFT/RIGHT, PROCEED SLOWLY, PROCEED)
- **Spatial Metadata Calculation** — estimates distance (in meters) and relative position (left/center/right, above/center/below) from bounding box analysis
- **Flask Web Dashboard** — live MJPEG video streaming with REST API endpoints for status, risks, and scene description
- **Scene Description** — Google Gemini AI generates natural language descriptions of detected scenes
- **Text-to-Speech Alerts** — pyttsx3 provides voice feedback for critical and high-priority risks
- **Structured Logging** — runtime events and errors logged to timestamped log files
- **Comprehensive Test Suite** — 86 unit and integration tests covering risk engine, spatial calculations, config loading, detection pipeline, and dashboard routes

### ⚠️ Hardware-Dependent Features (Not Yet Verified on Real Hardware)

- **Live Camera Capture** — requires a working webcam; tested only with synthetic images
- **Real-Time Audio Output** — requires speakers; speech synthesis code is present but not verified on physical hardware
- **Full Real-Time Video Feed** — requires camera + browser; MJPEG streaming route exists but end-to-end performance is unmeasured

---

## 🏗️ Architecture

```
src/main.py → src/dashboard/app.py (Flask)
  ↓
  ConfigLoader loads config.json + .env
  ↓
  Agents initialized at module level:
    VideoCaptureAgent → ObjectDetectionAgent → SpatialMetadataAgent
    → RiskEngineAgent → GenerativeAIAgent → AudioOutputAgent → LoggingAgent
  ↓
  Routes:
    GET / → Dashboard UI (index.html)
    GET /video_feed → MJPEG video stream
    GET /api/status → JSON detections & risks
    GET /api/risks → JSON risk list
    GET /api/describe → Gemini scene description
  ↓
  Frontend: index.html + static/style.css + static/script.js
    (polls /api/status every 1s, /api/risks every 500ms)
```

---

## 📦 Prerequisites

- **Python 3.10+** (tested on 3.14.3)
- **pip** package manager
- **Webcam** (for live video feed)
- **Speakers** (for audio alerts)
- **Internet connection** (for Gemini AI scene description)
- **Google Gemini API key** (optional but recommended for scene description)

---

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd navigation-assistant
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# or
source venv/bin/activate     # Linux/macOS
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the YOLOv8 Model

The YOLOv8 nano model (`yolov8n.pt`, ~6.5 MB) is required for object detection. Download it from the [Ultralytics GitHub releases](https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt) and place it in the `models/` directory:

```bash
# Create the models directory if it doesn't exist
mkdir models

# Download the model (Windows PowerShell)
Invoke-WebRequest -Uri "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt" -OutFile "models/yolov8n.pt"

# Or use curl (Linux/macOS)
curl -L -o models/yolov8n.pt https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt
```

### 5. Configure Environment Variables

Copy the example environment file and add your Gemini API key:

```bash
copy .env.example .env    # Windows
# or
cp .env.example .env      # Linux/macOS
```

Edit `.env` and replace the placeholder:

```
GEMINI_API_KEY=your_actual_api_key_here
```

To get a Gemini API key, visit [Google AI Studio](https://aistudio.google.com/apikey).

> **Note:** Scene description works without an API key, but will show a fallback message. The core detection and risk assessment features work without Gemini.

---

## ⚙️ Configuration

Edit `config.json` to customize:

| Setting | Description | Default |
|---------|-------------|---------|
| `model.yolo_path` | Path to YOLO model | `models/yolov8n.pt` |
| `model.confidence_threshold` | Minimum detection confidence | `0.5` |
| `risk_assessment.danger_distance_car` | CRITICAL risk distance for vehicles (meters) | `5` |
| `risk_assessment.danger_distance_person` | HIGH risk distance for pedestrians (meters) | `3` |
| `risk_assessment.warning_distance_car` | HIGH risk distance for vehicles (meters) | `10` |
| `risk_assessment.warning_distance_person` | MEDIUM risk distance for pedestrians (meters) | `5` |
| `audio.voice_speed` | Speech rate multiplier | `1.2` |

---

## 🚀 Running the Application

### Start the Dashboard

```bash
python src/dashboard/app.py
```

The server starts at `http://localhost:5000`. Open this URL in your browser to see the live dashboard.

### Run the Demo Script

```bash
python scripts/run_demo.py
```

---

## 🧪 Testing

Run the full test suite:

```bash
python -m unittest discover -s test -v
```

Run individual test suites:

```bash
python -m unittest test.test_risk_engine -v
python -m unittest test.test_spatial_metadata -v
python -m unittest test.test_config_loader -v
python -m unittest test.test_detection -v
python -m unittest test.test_dashboard -v
python -m unittest test.test_integration -v
```

**Test coverage:** 86 tests covering risk engine logic, spatial calculations, config loading, YOLO detection pipeline, Flask routes, and agent integration.

---

## 📁 Project Structure

```
navigation-assistant/
├── src/
│   ├── main.py                  # Main entry point
│   ├── agents/                  # Core agent modules
│   │   ├── video_capture.py     # Camera capture
│   │   ├── object_detection.py  # YOLOv8 detection
│   │   ├── spatial_metadata.py  # Distance & position estimation
│   │   ├── risk_engine.py       # Risk classification ⭐
│   │   ├── generative_ai.py     # Gemini AI scene description
│   │   ├── audio_output.py      # Text-to-speech alerts
│   │   └── logging_agent.py     # Runtime logging
│   ├── dashboard/               # Flask web dashboard
│   │   ├── app.py               # Flask application
│   │   ├── templates/
│   │   │   └── index.html       # Dashboard UI
│   │   └── static/
│   │       ├── style.css
│   │       └── script.js
│   └── utils/
│       ├── config_loader.py     # Configuration loading
│       └── visualizer.py        # Bounding box drawing (unused)
├── test/                        # Test suite (86 tests)
│   ├── test_risk_engine.py
│   ├── test_spatial_metadata.py
│   ├── test_config_loader.py
│   ├── test_detection.py
│   ├── test_dashboard.py
│   └── test_integration.py
├── models/                      # YOLO model weights (not in Git)
│   └── yolov8n.pt
├── scripts/
│   ├── run_demo.py
│   └── setup.sh
├── docs/
│   ├── SYSTEM_AUDIT.md          # System audit report
│   └── GITHUB_READINESS.md      # GitHub readiness checklist
├── config.json                  # Application configuration
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
├── .gitignore
└── README.md
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard UI |
| `/video_feed` | GET | MJPEG video stream |
| `/api/status` | GET | Current detections, risks, and timestamp (JSON) |
| `/api/risks` | GET | List of active risks with priority (JSON) |
| `/api/describe` | GET | AI-generated scene description (JSON) |

---

## ⚠️ Known Limitations

1. **No GPU acceleration** — runs on CPU; real-time performance depends on hardware
2. **Single-camera setup** — no multi-camera or 360° coverage
3. **Approximate distance estimation** — based on bounding box width, not depth sensors
4. **No motion tracking** — objects detected per-frame without temporal correlation
5. **Alert-only system** — does not physically control movement or a wheelchair
6. **Deprecated Google API** — `google.generativeai` is deprecated; migration to `google.genai` recommended
7. **No offline mode** — Gemini AI requires internet connection
8. **Windows-optimized audio** — pyttsx3 uses platform-specific voices

---

## ⚠️ Safety Disclaimer

**This system is a research and educational project. It is NOT a certified medical device or assistive technology.**

- The system provides **alerts only** — it does not control physical movement.
- Distance estimates are **approximate** and should not be relied upon for safety-critical decisions.
- Camera and audio features have **not been fully verified on real hardware**.
- Always use proven assistive devices and human guidance for navigation safety.

---

## 📄 License

This project's original source code is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

Third-party dependencies and pretrained model weights are distributed under their own licenses. The MIT License does not cover these components. See the [LICENSE](LICENSE) file for a list of key third-party dependencies and their licenses.