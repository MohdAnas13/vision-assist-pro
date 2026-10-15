# scripts/run_demo.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.dashboard.app import app
print("🚀 Starting demo...")
app.run(debug=True, port=5000)