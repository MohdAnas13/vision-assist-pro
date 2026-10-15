# src/agents/generative_ai.py
# NOTE: google.generativeai is deprecated as of 2025. Consider migrating to google.genai
# when ready. See: https://github.com/google-gemini/deprecated-generative-ai-python
import google.generativeai as genai
import cv2
from datetime import datetime
import logging

class GenerativeAIAgent:
    """Agent 5: Scene description using Gemini 2.5 Pro"""

    def __init__(self, api_key, model="gemini-2.5-pro-exp-03-25"):
        if not api_key:
            raise ValueError("Gemini API key is required for GenerativeAIAgent")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.logger = logging.getLogger(__name__)
        
    def describe_scene(self, frame, detections, risks, spatial_data):
        """Generate natural language scene description"""
        
        objects_summary = self._summarize_objects(detections, spatial_data)
        risk_summary = self._summarize_risks(risks)
        
        # Convert frame to bytes
        _, buffer = cv2.imencode('.jpg', frame)
        image_bytes = buffer.tobytes()
        
        prompt = f"""
        You are a visual assistant for a blind person. Describe the scene naturally.
        
        Objects detected: {objects_summary}
        Risks: {risk_summary}
        
        Give a brief, helpful description focusing on safety.
        """
        
        try:
            response = self.model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": image_bytes}
            ])
            
            return {
                'description': response.text,
                'timestamp': datetime.now(),
                'type': 'scene_description'
            }
            
        except Exception as e:
            self.logger.error(f"Error generating description: {e}")
            return self._fallback_description(detections, risks)
            
    def _summarize_objects(self, detections, spatial_data):
        """Create object summary"""
        if not detections:
            return "No objects detected"
        summary = []
        for i, det in enumerate(detections[:3]):  # Limit to 3 objects
            if i < len(spatial_data):
                dist = spatial_data[i].get('distance', 'unknown')
                summary.append(f"{det['class_name']} at {dist}m")
        return ", ".join(summary)
        
    def _summarize_risks(self, risks):
        """Create risk summary"""
        if not risks:
            return "No immediate risks"
        return risks[0]['action'] if risks else "Safe"
        
    def _fallback_description(self, detections, risks):
        """Fallback if API fails"""
        if risks:
            return {
                'description': f"Warning! {risks[0]['action']}",
                'timestamp': datetime.now(),
                'type': 'fallback_description'
            }
        else:
            return {
                'description': f"Scene is clear. {len(detections)} objects detected.",
                'timestamp': datetime.now(),
                'type': 'fallback_description'
            }