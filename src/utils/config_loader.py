# src/utils/config_loader.py
import json
import os
from dotenv import load_dotenv

class ConfigLoader:
    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        load_dotenv()
        
    def load(self):
        """Load configuration from JSON and environment"""
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        # Add API key from environment
        config['api']['gemini_api_key'] = os.getenv('GEMINI_API_KEY')
        
        return config