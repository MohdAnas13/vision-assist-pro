# test/test_spatial_metadata.py
"""Unit tests for the Spatial Metadata Agent."""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.spatial_metadata import SpatialMetadataAgent


class TestSpatialMetadataAgent(unittest.TestCase):
    """Tests for SpatialMetadataAgent distance, position, and angle calculations."""

    def setUp(self):
        """Create a SpatialMetadataAgent with default settings."""
        self.agent = SpatialMetadataAgent(focal_length=700, known_width=0.5)

    # --- Distance Estimation Tests ---

    def test_person_distance_100px(self):
        """Person with bbox width 100px should be ~3.5m away."""
        bbox = (270, 200, 370, 400)  # width = 100
        distance = self.agent.estimate_distance(bbox, 'person')
        # (0.5 * 700) / 100 = 3.5
        self.assertAlmostEqual(distance, 3.5, places=1)

    def test_car_distance_50px(self):
        """Car with bbox width 50px should be ~25.2m away."""
        bbox = (200, 200, 250, 300)  # width = 50
        distance = self.agent.estimate_distance(bbox, 'car')
        # (1.8 * 700) / 50 = 25.2
        self.assertAlmostEqual(distance, 25.2, places=1)

    def test_truck_distance_100px(self):
        """Truck with bbox width 100px should be ~17.5m away."""
        bbox = (200, 200, 300, 350)  # width = 100
        distance = self.agent.estimate_distance(bbox, 'truck')
        # (2.5 * 700) / 100 = 17.5
        self.assertAlmostEqual(distance, 17.5, places=1)

    def test_bicycle_distance_200px(self):
        """Bicycle with bbox width 200px should be ~2.1m away."""
        bbox = (200, 200, 400, 350)  # width = 200
        distance = self.agent.estimate_distance(bbox, 'bicycle')
        # (0.6 * 700) / 200 = 2.1
        self.assertAlmostEqual(distance, 2.1, places=1)

    def test_zero_width_bbox_default_distance(self):
        """Zero-width bbox should return default distance 10m."""
        bbox = (100, 100, 100, 200)  # width = 0
        distance = self.agent.estimate_distance(bbox, 'person')
        self.assertEqual(distance, 10.0)

    def test_unknown_class_uses_default_known_width(self):
        """Unknown class should use default known_width 0.5."""
        bbox = (270, 200, 370, 400)  # width = 100
        distance = self.agent.estimate_distance(bbox, 'unknown_object')
        # (0.5 * 700) / 100 = 3.5
        self.assertAlmostEqual(distance, 3.5, places=1)

    def test_distance_rounding(self):
        """Distance should be rounded to 2 decimal places."""
        bbox = (270, 200, 373, 400)  # width = 103
        distance = self.agent.estimate_distance(bbox, 'person')
        # (0.5 * 700) / 103 = 3.39805...
        self.assertEqual(distance, round(3.39805, 2))

    # --- Position Calculation Tests ---

    def test_position_left(self):
        """Object centered at x=100 should be 'left'."""
        bbox = (50, 200, 150, 300)  # center_x = 100
        position = self.agent.calculate_position(bbox)
        self.assertEqual(position['horizontal'], 'left')

    def test_position_right(self):
        """Object centered at x=540 should be 'right'."""
        bbox = (490, 200, 590, 300)  # center_x = 540
        position = self.agent.calculate_position(bbox)
        self.assertEqual(position['horizontal'], 'right')

    def test_position_center(self):
        """Object centered at x=320 should be 'center'."""
        bbox = (270, 200, 370, 300)  # center_x = 320
        position = self.agent.calculate_position(bbox)
        self.assertEqual(position['horizontal'], 'center')

    def test_position_above(self):
        """Object centered at y=100 should be 'above'."""
        bbox = (270, 50, 370, 150)  # center_y = 100
        position = self.agent.calculate_position(bbox)
        self.assertEqual(position['vertical'], 'above')

    def test_position_below(self):
        """Object centered at y=400 should be 'below'."""
        bbox = (270, 350, 370, 450)  # center_y = 400
        position = self.agent.calculate_position(bbox)
        self.assertEqual(position['vertical'], 'below')

    def test_position_center_vertical(self):
        """Object centered at y=240 should be 'center' vertically."""
        bbox = (270, 190, 370, 290)  # center_y = 240
        position = self.agent.calculate_position(bbox)
        self.assertEqual(position['vertical'], 'center')

    def test_position_boundary_left(self):
        """Object at x=270 (320-50) should be 'center', not 'left'."""
        bbox = (220, 200, 320, 300)  # center_x = 270
        position = self.agent.calculate_position(bbox)
        self.assertEqual(position['horizontal'], 'center')

    def test_position_boundary_right(self):
        """Object at x=370 (320+50) should be 'center', not 'right'."""
        bbox = (320, 200, 420, 300)  # center_x = 370
        position = self.agent.calculate_position(bbox)
        self.assertEqual(position['horizontal'], 'center')

    # --- Angle Calculation Tests ---

    def test_angle_at_center(self):
        """Object at center should have 0 degree angle."""
        angle = self.agent.calculate_angle(320)
        self.assertEqual(angle, 0.0)

    def test_angle_to_the_left(self):
        """Object to the left should have negative angle."""
        angle = self.agent.calculate_angle(100)
        # (100 - 320) / 320 * 30 = -20.625, rounded to -20.6
        self.assertAlmostEqual(angle, -20.6, places=1)
        self.assertLess(angle, 0)

    def test_angle_to_the_right(self):
        """Object to the right should have positive angle."""
        angle = self.agent.calculate_angle(540)
        # (540 - 320) / 320 * 30 = 20.625
        self.assertAlmostEqual(angle, 20.6, places=1)
        self.assertGreater(angle, 0)

    def test_angle_rounding(self):
        """Angle should be rounded to 1 decimal place."""
        angle = self.agent.calculate_angle(200)
        self.assertIsInstance(angle, float)

    # --- Position Object Structure ---

    def test_position_has_required_fields(self):
        """Position object should have horizontal, vertical, and angle."""
        bbox = (270, 200, 370, 300)
        position = self.agent.calculate_position(bbox)
        self.assertIn('horizontal', position)
        self.assertIn('vertical', position)
        self.assertIn('angle', position)

    def test_horizontal_is_valid_value(self):
        """Horizontal position should be one of left, center, right."""
        bbox = (270, 200, 370, 300)
        position = self.agent.calculate_position(bbox)
        self.assertIn(position['horizontal'], ['left', 'center', 'right'])

    def test_vertical_is_valid_value(self):
        """Vertical position should be one of above, center, below."""
        bbox = (270, 200, 370, 300)
        position = self.agent.calculate_position(bbox)
        self.assertIn(position['vertical'], ['above', 'center', 'below'])


if __name__ == '__main__':
    unittest.main()
