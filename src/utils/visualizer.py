# src/utils/visualizer.py
# NOTE: This module is currently unused. The dashboard (src/dashboard/app.py) performs
# inline drawing of bounding boxes instead of using this class. It is kept for potential
# future use or alternative visualization pipelines.
import cv2

class Visualizer:
    """Draw bounding boxes and information on frames.

    NOTE: Currently unused in the main application. Kept for future reference.
    """
    
    @staticmethod
    def draw_detections(frame, detections, risks):
        """Draw detections with risk-based colors"""
        for det in detections:
            x1, y1, x2, y2 = map(int, det['bbox'])
            class_name = det['class_name']
            conf = det['confidence']
            
            # Determine color based on risk
            color = (67, 97, 238)  # Blue default
            for risk in risks:
                if risk.get('class_name') == class_name:
                    if risk['risk_level'] == 'CRITICAL':
                        color = (0, 0, 255)  # Red
                    elif risk['risk_level'] == 'HIGH':
                        color = (0, 165, 255)  # Orange
                    elif risk['risk_level'] == 'MEDIUM':
                        color = (0, 255, 255)  # Yellow
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{class_name} {conf:.2f}"
            cv2.putText(frame, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame