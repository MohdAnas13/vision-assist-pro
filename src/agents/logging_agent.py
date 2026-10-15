# src/agents/logging_agent.py
import json
import logging
from datetime import datetime
import os

class LoggingAgent:
    """Agent 7: Comprehensive logging system"""
    
    def __init__(self, log_file="logs/navigation_log.json"):
        self.log_file = log_file
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"logs/app_{self.session_id}.log"),
                logging.StreamHandler()
            ]
        )
        
    def log_detection(self, detection_data):
        """Log object detection events"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'detection',
            'session_id': self.session_id,
            'data': detection_data
        }
        self._write_log(log_entry)
        
    def log_risk(self, risk_data):
        """Log risk assessment events"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'risk',
            'session_id': self.session_id,
            'data': risk_data
        }
        self._write_log(log_entry)
        
    def log_error(self, error_message):
        """Log errors"""
        logging.error(error_message)
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'error',
            'session_id': self.session_id,
            'message': error_message
        }
        self._write_log(log_entry)
        
    def _write_log(self, log_entry):
        """Write log entry to file"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logging.error(f"Failed to write log: {e}")