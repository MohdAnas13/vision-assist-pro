# src/agents/spatial_metadata.py
import math

class SpatialMetadataAgent:
    """Agent 3: Calculate distances and spatial relationships"""
    
    def __init__(self, focal_length=700, known_width=0.5):
        self.focal_length = focal_length
        self.known_width = known_width
        self.frame_center = (320, 240)
        
    def estimate_distance(self, bbox, class_name):
        """Estimate distance to object using bounding box"""
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        
        known_widths = {
            'person': 0.5,
            'car': 1.8,
            'truck': 2.5,
            'bus': 2.5,
            'motorcycle': 0.8,
            'bicycle': 0.6,
            'dog': 0.4,
            'cat': 0.3
        }
        
        obj_width = known_widths.get(class_name, self.known_width)
        
        if width > 0:
            distance = (obj_width * self.focal_length) / width
            return round(distance, 2)
        return 10.0  # Default distance
        
    def calculate_position(self, bbox):
        """Calculate relative position (left/right/center)"""
        x1, y1, x2, y2 = bbox
        obj_center_x = (x1 + x2) / 2
        obj_center_y = (y1 + y2) / 2
        
        if obj_center_x < self.frame_center[0] - 50:
            position_x = "left"
        elif obj_center_x > self.frame_center[0] + 50:
            position_x = "right"
        else:
            position_x = "center"
            
        if obj_center_y < self.frame_center[1] - 50:
            position_y = "above"
        elif obj_center_y > self.frame_center[1] + 50:
            position_y = "below"
        else:
            position_y = "center"
            
        return {
            'horizontal': position_x,
            'vertical': position_y,
            'angle': self.calculate_angle(obj_center_x)
        }
        
    def calculate_angle(self, obj_center_x):
        """Calculate angle from center (in degrees)"""
        pixel_offset = obj_center_x - self.frame_center[0]
        angle = (pixel_offset / 320) * 30
        return round(angle, 1)