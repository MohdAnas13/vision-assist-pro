# test/test_integration.py
"""Integration tests for agent initialization and data flow."""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestAgentImports(unittest.TestCase):
    """Verify all agents can be imported without errors."""

    def test_import_video_capture(self):
        """VideoCaptureAgent should import successfully."""
        from agents.video_capture import VideoCaptureAgent
        self.assertTrue(callable(VideoCaptureAgent))

    def test_import_object_detection(self):
        """ObjectDetectionAgent should import successfully."""
        from agents.object_detection import ObjectDetectionAgent
        self.assertTrue(callable(ObjectDetectionAgent))

    def test_import_spatial_metadata(self):
        """SpatialMetadataAgent should import successfully."""
        from agents.spatial_metadata import SpatialMetadataAgent
        self.assertTrue(callable(SpatialMetadataAgent))

    def test_import_risk_engine(self):
        """RiskEngineAgent should import successfully."""
        from agents.risk_engine import RiskEngineAgent
        self.assertTrue(callable(RiskEngineAgent))

    def test_import_audio_output(self):
        """AudioOutputAgent should import successfully."""
        from agents.audio_output import AudioOutputAgent
        self.assertTrue(callable(AudioOutputAgent))

    def test_import_logging_agent(self):
        """LoggingAgent should import successfully."""
        from agents.logging_agent import LoggingAgent
        self.assertTrue(callable(LoggingAgent))

    def test_import_config_loader(self):
        """ConfigLoader should import successfully."""
        from utils.config_loader import ConfigLoader
        self.assertTrue(callable(ConfigLoader))


class TestAgentInitialization(unittest.TestCase):
    """Verify agents can be initialized with valid parameters."""

    def test_spatial_metadata_init(self):
        """SpatialMetadataAgent should initialize with defaults."""
        from agents.spatial_metadata import SpatialMetadataAgent
        agent = SpatialMetadataAgent()
        self.assertEqual(agent.focal_length, 700)
        self.assertEqual(agent.known_width, 0.5)

    def test_risk_engine_init(self):
        """RiskEngineAgent should initialize with config."""
        from agents.risk_engine import RiskEngineAgent
        config = {
            'risk_assessment': {
                'danger_distance_car': 5,
                'danger_distance_person': 3,
                'warning_distance_car': 10,
                'warning_distance_person': 5,
                'update_frequency': 0.5,
            }
        }
        agent = RiskEngineAgent(config)
        self.assertEqual(agent.danger_distance_car, 5)
        self.assertEqual(agent.danger_distance_person, 3)

    def test_audio_output_init(self):
        """AudioOutputAgent should initialize without error."""
        from agents.audio_output import AudioOutputAgent
        agent = AudioOutputAgent()
        self.assertIsNotNone(agent)

    def test_logging_agent_init(self):
        """LoggingAgent should initialize without error."""
        from agents.logging_agent import LoggingAgent
        agent = LoggingAgent()
        self.assertIsNotNone(agent)


class TestDataFlow(unittest.TestCase):
    """Verify data flows correctly between agents."""

    def test_detection_to_spatial_to_risk(self):
        """Full pipeline: detection → spatial → risk should work."""
        from agents.spatial_metadata import SpatialMetadataAgent
        from agents.risk_engine import RiskEngineAgent

        config = {
            'risk_assessment': {
                'danger_distance_car': 5,
                'danger_distance_person': 3,
                'warning_distance_car': 10,
                'warning_distance_person': 5,
                'update_frequency': 0.5,
            }
        }
        spatial_agent = SpatialMetadataAgent()
        risk_agent = RiskEngineAgent(config)

        # Simulate a detection — car with bbox width 252px → distance ≈ 5m (CRITICAL)
        detection = {
            'class_name': 'car',
            'confidence': 0.9,
            'bbox': [194, 200, 446, 300],
            'center': [320, 250],
        }

        # Spatial processing
        distance = spatial_agent.estimate_distance(detection['bbox'], detection['class_name'])
        position = spatial_agent.calculate_position(detection['bbox'])
        spatial_data = [{'distance': distance, 'position': position}]

        # Risk processing
        risks = risk_agent.analyze_risks([detection], spatial_data)

        # Verify the pipeline produced output
        self.assertIsInstance(risks, list)
        # Car at this distance should produce a risk
        self.assertGreater(len(risks), 0)
        self.assertIn(risks[0]['risk_level'], ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'])


if __name__ == '__main__':
    unittest.main()
