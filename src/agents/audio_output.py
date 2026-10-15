# src/agents/audio_output.py
import pyttsx3
import threading
import queue
import time
import logging

class AudioOutputAgent:
    """Agent 6: Text-to-speech with priority queuing"""
    
    def __init__(self, voice_speed=1.2, volume=0.8):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', int(150 * voice_speed))
        self.engine.setProperty('volume', volume)
        
        self.message_queue = queue.PriorityQueue()
        self.running = False
        self.logger = logging.getLogger(__name__)
        
    def start(self):
        """Start audio output thread"""
        self.running = True
        self.thread = threading.Thread(target=self._process_queue)
        self.thread.start()
        
    def speak(self, text, priority=5, interrupt=False):
        """Add message to queue"""
        if interrupt:
            self.clear_queue()
            priority = 1
        self.message_queue.put((priority, text, time.time()))
        
    def _process_queue(self):
        """Process messages from queue"""
        while self.running:
            try:
                priority, text, timestamp = self.message_queue.get(timeout=1)
                self.engine.say(text)
                self.engine.runAndWait()
            except queue.Empty:
                continue
                
    def clear_queue(self):
        """Clear all pending messages"""
        while not self.message_queue.empty():
            try:
                self.message_queue.get_nowait()
            except queue.Empty:
                break
                
    def stop(self):
        """Stop audio output"""
        self.running = False
        self.clear_queue()
        if hasattr(self, 'thread'):
            self.thread.join()
        self.engine.stop()