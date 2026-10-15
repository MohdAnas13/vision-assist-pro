# test/test_risk_engine.py
"""Comprehensive unit tests for the Risk Engine."""
import unittest
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.risk_engine import RiskEngineAgent


class TestRiskEngineAgent(unittest.TestCase):
    """Tests for RiskEngineAgent risk assessment logic."""

    def setUp(self):
        """Create a RiskEngineAgent with standard config."""
        self.config = {
            'risk_assessment': {
                'danger_distance_car': 5,
                'danger_distance_person': 3,
                'warning_distance_car': 10,
                'warning_distance_person': 5,
                'update_frequency': 0.5,
            }
        }
        self.agent = RiskEngineAgent(self.config)

    # --- Vehicle Risk Tests ---

    def test_vehicle_critical_risk(self):
        """Car at 3m (<=5m danger) should be CRITICAL, priority 10."""
        detection = {'class_name': 'car', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        spatial = {'distance': 3, 'position': {'horizontal': 'center', 'vertical': 'center', 'angle': 0}}
        risks = self.agent.analyze_risks([detection], [spatial])
        self.assertEqual(len(risks), 1)
        self.assertEqual(risks[0]['risk_level'], 'CRITICAL')
        self.assertEqual(risks[0]['priority'], 10)
        self.assertEqual(risks[0]['type'], 'vehicle')
        self.assertIn('STOP', risks[0]['action'])

    def test_vehicle_at_exact_danger_boundary(self):
        """Car at exactly 5m (==danger_distance_car) should be CRITICAL."""
        detection = {'class_name': 'car', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        spatial = {'distance': 5, 'position': {'horizontal': 'left', 'vertical': 'center', 'angle': 0}}
        risks = self.agent.analyze_risks([detection], [spatial])
        self.assertEqual(len(risks), 1)
        self.assertEqual(risks[0]['risk_level'], 'CRITICAL')
        self.assertEqual(risks[0]['priority'], 10)

    def test_vehicle_high_risk(self):
        """Car at 7m (>5 danger, <=10 warning) should be HIGH, priority 7."""
        detection = {'class_name': 'car', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        spatial = {'distance': 7, 'position': {'horizontal': 'right', 'vertical': 'center', 'angle': 0}}
        risks = self.agent.analyze_risks([detection], [spatial])
        self.assertEqual(len(risks), 1)
        self.assertEqual(risks[0]['risk_level'], 'HIGH')
        self.assertEqual(risks[0]['priority'], 7)

    def test_vehicle_at_exact_warning_boundary(self):
        """Car at exactly 10m (==warning_distance_car) should be HIGH."""
        detection = {'class_name': 'car', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        spatial = {'distance': 10, 'position': {'horizontal': 'center', 'vertical': 'center', 'angle': 0}}
        risks = self.agent.analyze_risks([detection], [spatial])
        self.assertEqual(len(risks), 1)
        self.assertEqual(risks[0]['risk_level'], 'HIGH')
        self.assertEqual(risks[0]['priority'], 7)

    def test_vehicle_no_risk(self):
        """Car at 15m (>10 warning) should produce no risk."""
        detection = {'class_name': 'car', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        spatial = {'distance': 15, 'position': {'horizontal': 'center', 'vertical': 'center', 'angle': 0}}
        risks = self.agent.analyze_risks([detection], [spatial])
        self.assertEqual(len(risks), 0)

    def test_truck_critical_risk(self):
        """Truck at 3m should be CRITICAL."""
        detection = {'class_name': 'truck', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        spatial = {'distance': 3, 'position': {'horizontal': 'center', 'vertical': 'center', 'angle': 0}}
        risks = self.agent.analyze_risks([detection], [spatial])
        self.assertEqual(len(risks), 1)
        self.assertEqual(risks[0]['risk_level'], 'CRITICAL')

    def test_bus_high_risk(self):
        """Bus at 8m should be HIGH."""
        detection = {'class_name': 'bus', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        spatial = {'distance': 8, 'position': {'horizontal': 'center', 'vertical': 'center', 'angle': 0}}
        risks = self.agent.analyze_risks([detection], [spatial])
        self.assertEqual(len(risks), 1)
        self.assertEqual(risks[0]['risk_level'], 'HIGH')

    def test_motorcycle_critical_risk(self):
        """Motorcycle at 2m should be CRITICAL."""
        detection = {'class_name': 'motorcycle', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        spatial = {'distance': 2, 'position': {'horizontal': 'center', 'vertical': 'center', 'angle': 0}}
        risks = self.agent.analyze_risks([detection], [spatial])
        self.assertEqual(len(risks), 1)
        self.assertEqual(risks[0]['risk_level'], 'CRITICAL')

    def test_bicycle_no_risk(self):
        """Bicycle at 12m should produce no risk."""
        detection = {'class_name': 'bicycle', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        spatial = {'distance': 12, 'position': {'horizontal': 'center', 'vertical': 'center', 'angle': 0}}
        risks = self.agent.analyze_risks([detection], [spatial])
        self.assertEqual(len(risks), 0)

    # --- Pedestrian Risk Tests ---

    def test_person_high_risk(self):
        """Person at 2m (<=3m danger) should be HIGH, priority 8."""
        detection = {'class_name': 'person', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        spatial = {'distance': 2, 'position': {'horizontal': 'center', 'vertical': 'center', 'angle': 0}}
        risks = self.agent.analyze_risks([detection], [spatial])
        self.assertEqual(len(risks), 1)
        self.assertEqual(risks[0]['risk_level'], 'HIGH')
        self.assertEqual(risks[0]['priority'], 8)
        self.assertEqual(risks[0]['type'], 'pedestrian')

    def test_person_at_exact_danger_boundary(self):
        """Person at exactly 3m should be HIGH."""
        detection = {'class_name': 'person', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        spatial = {'distance': 3, 'position': {'horizontal': 'center', 'vertical': 'center', 'angle': 0}}
        risks = self.agent.analyze_risks([detection], [spatial])
        self.assertEqual(len(risks), 1)
        self.assertEqual(risks[0]['risk_level'], 'HIGH')

    def test_person_medium_risk(self):
        """Person at 4m (>3 danger, <=5 warning) should be MEDIUM, priority 5."""
        detection = {'class_name': 'person', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        spatial = {'distance': 4, 'position': {'horizontal': 'center', 'vertical': 'center', 'angle': 0}}
        risks = self.agent.analyze_risks([detection], [spatial])
        self.assertEqual(len(risks), 1)
        self.assertEqual(risks[0]['risk_level'], 'MEDIUM')
        self.assertEqual(risks[0]['priority'], 5)

    def test_person_at_exact_warning_boundary(self):
        """Person at exactly 5m should be MEDIUM."""
        detection = {'class_name': 'person', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        spatial = {'distance': 5, 'position': {'horizontal': 'center', 'vertical': 'center', 'angle': 0}}
        risks = self.agent.analyze_risks([detection], [spatial])
        self.assertEqual(len(risks), 1)
        self.assertEqual(risks[0]['risk_level'], 'MEDIUM')

    def test_person_no_risk(self):
        """Person at 8m (>5 warning) should produce no risk."""
        detection = {'class_name': 'person', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        spatial = {'distance': 8, 'position': {'horizontal': 'center', 'vertical': 'center', 'angle': 0}}
        risks = self.agent.analyze_risks([detection], [spatial])
        self.assertEqual(len(risks), 0)

    # --- Edge Cases ---

    def test_empty_detections(self):
        """Empty detections should return empty risks."""
        risks = self.agent.analyze_risks([], [])
        self.assertEqual(risks, [])

    def test_missing_spatial_data(self):
        """Detection without matching spatial data should be skipped."""
        detection = {'class_name': 'car', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        risks = self.agent.analyze_risks([detection], [])
        self.assertEqual(len(risks), 0)

    def test_missing_distance_in_spatial(self):
        """Missing distance defaults to 10m, which is HIGH for car."""
        detection = {'class_name': 'car', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        spatial = {'position': {'horizontal': 'center', 'vertical': 'center', 'angle': 0}}
        risks = self.agent.analyze_risks([detection], [spatial])
        self.assertEqual(len(risks), 1)
        self.assertEqual(risks[0]['risk_level'], 'HIGH')

    def test_missing_position_in_spatial(self):
        """Missing position defaults to center."""
        detection = {'class_name': 'car', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        spatial = {'distance': 3}
        risks = self.agent.analyze_risks([detection], [spatial])
        self.assertEqual(len(risks), 1)
        self.assertIn('center', risks[0]['action'])

    def test_unknown_class_ignored(self):
        """Unknown class (e.g., 'dog') should produce no risk."""
        detection = {'class_name': 'dog', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        spatial = {'distance': 1, 'position': {'horizontal': 'center', 'vertical': 'center', 'angle': 0}}
        risks = self.agent.analyze_risks([detection], [spatial])
        self.assertEqual(len(risks), 0)

    # --- Priority Sorting ---

    def test_priority_sorting(self):
        """Risks should be sorted by priority descending."""
        car_det = {'class_name': 'car', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        person_det = {'class_name': 'person', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        car_spatial = {'distance': 3, 'position': {'horizontal': 'center', 'vertical': 'center', 'angle': 0}}
        person_spatial = {'distance': 2, 'position': {'horizontal': 'center', 'vertical': 'center', 'angle': 0}}
        risks = self.agent.analyze_risks([person_det, car_det], [person_spatial, car_spatial])
        # Car CRITICAL (10) should come before person HIGH (8)
        self.assertEqual(len(risks), 2)
        self.assertEqual(risks[0]['priority'], 10)
        self.assertEqual(risks[1]['priority'], 8)

    # --- Risk Object Structure ---

    def test_risk_object_has_required_fields(self):
        """Risk object should have all required fields."""
        detection = {'class_name': 'car', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        spatial = {'distance': 3, 'position': {'horizontal': 'center', 'vertical': 'center', 'angle': 0}}
        risks = self.agent.analyze_risks([detection], [spatial])
        risk = risks[0]
        required_fields = ['type', 'class_name', 'distance', 'position', 'risk_level', 'priority', 'action', 'timestamp']
        for field in required_fields:
            self.assertIn(field, risk, f"Missing field: {field}")

    def test_risk_timestamp_is_datetime(self):
        """Risk timestamp should be a datetime object."""
        detection = {'class_name': 'car', 'confidence': 0.9, 'bbox': (0, 0, 100, 100)}
        spatial = {'distance': 3, 'position': {'horizontal': 'center', 'vertical': 'center', 'angle': 0}}
        risks = self.agent.analyze_risks([detection], [spatial])
        self.assertIsInstance(risks[0]['timestamp'], datetime)


if __name__ == '__main__':
    unittest.main()
