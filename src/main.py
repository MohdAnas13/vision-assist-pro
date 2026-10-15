# src/main.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dashboard.app import app

if __name__ == "__main__":
    print("🚀 Starting Vision Assistant...")
    app.run(debug=True, host='0.0.0.0', port=5000)