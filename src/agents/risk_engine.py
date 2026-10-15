# src/agents/risk_engine.py
from datetime import datetime
import logging

class RiskEngineAgent:
    """Agent 4: Analyze risks based on object detection and movement"""
    
    def __init__(self, config):
        self.config = config
        self.danger_distance_car = config['risk_assessment']['danger_distance_car']
        self.danger_distance_person = config['risk_assessment']['danger_distance_person']
        self.warning_distance_car = config['risk_assessment']['warning_distance_car']
        self.warning_distance_person = config['risk_assessment']['warning_distance_person']
        
        self.object_history = {}
        self.logger = logging.getLogger(__name__)
        
    def analyze_risks(self, detections, spatial_data):
        """Main risk analysis function"""
        risks = []
        
        for i, detection in enumerate(detections):
            if i >= len(spatial_data):
                continue
                
            class_name = detection['class_name']
            spatial = spatial_data[i]
            distance = spatial.get('distance', 10)
            position = spatial.get('position', {'horizontal': 'center'})
            
            if class_name in ['car', 'truck', 'bus', 'motorcycle', 'bicycle']:
                risk = self._assess_vehicle_risk(detection, distance, position)
                if risk:
                    risks.append(risk)
                    
            elif class_name == 'person':
                risk = self._assess_pedestrian_risk(detection, distance, position)
                if risk:
                    risks.append(risk)
        
        risks.sort(key=lambda x: x['priority'], reverse=True)
        return risks
        
    def _assess_vehicle_risk(self, detection, distance, position):
        """Assess risk from vehicles"""
        risk_level = "LOW"
        priority = 0
        action = "Monitor"
        
        if distance <= self.danger_distance_car:
            risk_level = "CRITICAL"
            priority = 10
            action = f"STOP! {detection['class_name']} very close from {position['horizontal']}!"
                
        elif distance <= self.warning_distance_car:
            risk_level = "HIGH"
            priority = 7
            action = f"⚠️ {detection['class_name']} approaching from {position['horizontal']}"
        
        if risk_level != "LOW":
            return {
                'type': 'vehicle',
                'class_name': detection['class_name'],
                'distance': distance,
                'position': position,
                'risk_level': risk_level,
                'priority': priority,
                'action': action,
                'timestamp': datetime.now()
            }
        return None
        
    def _assess_pedestrian_risk(self, detection, distance, position):
        """Assess risk from pedestrians"""
        if distance <= self.danger_distance_person:
            return {
                'type': 'pedestrian',
                'class_name': 'person',
                'distance': distance,
                'position': position,
                'risk_level': "HIGH",
                'priority': 8,
                'action': f"Person very close at {distance}m!",
                'timestamp': datetime.now()
            }
        elif distance <= self.warning_distance_person:
            return {
                'type': 'pedestrian',
                'class_name': 'person',
                'distance': distance,
                'position': position,
                'risk_level': "MEDIUM",
                'priority': 5,
                'action': f"Person ahead at {distance}m",
                'timestamp': datetime.now()
            }
        return None