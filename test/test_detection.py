# test/test_detection.py
"""Integration tests for the Object Detection Agent."""
import unittest
import sys
import os
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.object_detection import ObjectDetectionAgent


class TestObjectDetectionAgent(unittest.TestCase):
    """Tests for ObjectDetectionAgent model loading and inference."""

    @classmethod
    def setUpClass(cls):
        """Load the model once for all tests."""
        model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'yolov8n.pt')
        cls.model_exists = os.path.exists(model_path)
        if cls.model_exists:
            cls.agent = ObjectDetectionAgent(model_path, conf_threshold=0.5)
        else:
            cls.agent = None

    def setUp(self):
        """Skip tests if model is not available."""
        if self.agent is None:
            self.skipTest("YOLO model not found at models/yolov8n.pt")

    def test_model_loads_successfully(self):
        """Model should load without error."""
        self.assertIsNotNone(self.agent.model)
        self.assertEqual(self.agent.conf_threshold, 0.5)

    def test_device_is_set(self):
        """Device should be set to cpu or cuda."""
        self.assertIn(self.agent.device, ['cpu', 'cuda'])

    def test_class_names_loaded(self):
        """Class names should be loaded (80 COCO classes)."""
        self.assertEqual(len(self.agent.class_names), 80)
        self.assertIn('person', self.agent.class_names)
        self.assertIn('car', self.agent.class_names)

    def test_detect_returns_list(self):
        """detect() should return a list."""
        black_image = np.zeros((480, 640, 3), dtype=np.uint8)
        result = self.agent.detect(black_image)
        self.assertIsInstance(result, list)

    def test_detect_black_image_returns_empty(self):
        """A black image should produce no detections (no objects)."""
        black_image = np.zeros((480, 640, 3), dtype=np.uint8)
        result = self.agent.detect(black_image)
        self.assertEqual(len(result), 0)

    def test_detect_none_returns_empty(self):
        """detect(None) should return an empty list."""
        result = self.agent.detect(None)
        self.assertEqual(result, [])

    def test_detect_output_format(self):
        """Detection output should have required keys."""
        # We can't guarantee a detection on a synthetic image, so we test
        # the structure by checking that the method doesn't crash
        gray_image = np.full((480, 640, 3), 128, dtype=np.uint8)
        result = self.agent.detect(gray_image)
        self.assertIsInstance(result, list)
        # If there are any detections, verify their structure
        for det in result:
            self.assertIn('bbox', det)
            self.assertIn('confidence', det)
            self.assertIn('class_name', det)
            self.assertIn('center', det)
            self.assertIn('class_id', det)

    def test_detect_with_custom_confidence_threshold(self):
        """High confidence threshold should filter out low-confidence detections."""
        agent = ObjectDetectionAgent(
            os.path.join(os.path.dirname(__file__), '..', 'models', 'yolov8n.pt'),
            conf_threshold=0.99
        )
        black_image = np.zeros((480, 640, 3), dtype=np.uint8)
        result = agent.detect(black_image)
        self.assertEqual(len(result), 0)

    def test_detect_returns_correct_bbox_format(self):
        """Bounding box should be a list of 4 floats."""
        # Use a simple image; if detections exist, verify format
        gray_image = np.full((480, 640, 3), 128, dtype=np.uint8)
        result = self.agent.detect(gray_image)
        for det in result:
            bbox = det['bbox']
            self.assertEqual(len(bbox), 4)
            self.assertIsInstance(bbox[0], float)

    def test_detect_confidence_range(self):
        """Confidence should be between 0 and 1."""
        gray_image = np.full((480, 640, 3), 128, dtype=np.uint8)
        result = self.agent.detect(gray_image)
        for det in result:
            self.assertGreaterEqual(det['confidence'], 0)
            self.assertLessEqual(det['confidence'], 1)


class TestObjectDetectionAgentNoModel(unittest.TestCase):
    """Tests for behavior when model file is missing."""

    def test_missing_model_path(self):
        """When model path doesn't exist, YOLO should still initialize (downloads)."""
        # This test verifies the code path when model doesn't exist
        # It will attempt to download, so we just check the code structure
        agent = ObjectDetectionAgent('nonexistent_model.pt', conf_threshold=0.6)
        self.assertEqual(agent.conf_threshold, 0.6)


if __name__ == '__main__':
    unittest.main()
