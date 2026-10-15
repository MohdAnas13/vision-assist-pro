# src/agents/video_capture.py
import cv2
import threading
from queue import Queue
import time
import logging

class VideoCaptureAgent:
    """Agent 1: Captures video frames from camera"""
    
    def __init__(self, camera_id=0, width=640, height=480):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.cap = None
        self.frame = None
        self.running = False
        self.frame_queue = Queue(maxsize=10)
        self.logger = logging.getLogger(__name__)
        
    def start(self):
        """Start video capture"""
        self.cap = cv2.VideoCapture(self.camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.running = True
        self.thread = threading.Thread(target=self._update_frame)
        self.thread.start()
        self.logger.info("Video capture started")
        
    def _update_frame(self):
        """Continuously update frame"""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                if self.frame_queue.full():
                    self.frame_queue.get()
                self.frame_queue.put(frame)
            time.sleep(0.03)
            
    def get_frame(self):
        """Get current frame"""
        if not self.frame_queue.empty():
            return self.frame_queue.get()
        return None
    
    def stop(self):
        """Stop video capture"""
        self.running = False
        if hasattr(self, 'thread') and self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()
        self.logger.info("Video capture stopped")