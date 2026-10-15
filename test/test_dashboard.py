# test/test_dashboard.py
"""Tests for the Flask dashboard routes and API endpoints."""
import unittest
import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestDashboardRoutes(unittest.TestCase):
    """Tests for Flask dashboard routes using test client."""

    @classmethod
    def setUpClass(cls):
        """Set up Flask test client. Skip if dashboard can't be imported."""
        try:
            # Change to project root for config loading
            cls.original_cwd = os.getcwd()
            os.chdir(os.path.join(os.path.dirname(__file__), '..'))

            from dashboard.app import app
            cls.app = app
            cls.client = app.test_client()
            cls.dashboard_available = True
        except Exception as e:
            cls.dashboard_available = False
            cls.error = str(e)
        finally:
            os.chdir(cls.original_cwd)

    def setUp(self):
        """Skip if dashboard is not available."""
        if not getattr(self.__class__, 'dashboard_available', False):
            self.skipTest(f"Dashboard not available: {getattr(self.__class__, 'error', 'unknown')}")

    def test_index_returns_200(self):
        """GET / should return 200 OK."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_index_renders_html(self):
        """GET / should return HTML content."""
        response = self.client.get('/')
        self.assertIn(b'html', response.data.lower())

    def test_api_status_returns_200(self):
        """GET /api/status should return 200 OK."""
        response = self.client.get('/api/status')
        self.assertEqual(response.status_code, 200)

    def test_api_status_returns_json(self):
        """GET /api/status should return valid JSON."""
        response = self.client.get('/api/status')
        data = response.get_json()
        self.assertIsInstance(data, dict)

    def test_api_status_has_required_fields(self):
        """GET /api/status should have detections, risks, description, timestamp."""
        response = self.client.get('/api/status')
        data = response.get_json()
        self.assertIn('detections', data)
        self.assertIn('risks', data)
        self.assertIn('description', data)
        self.assertIn('timestamp', data)

    def test_api_risks_returns_200(self):
        """GET /api/risks should return 200 OK."""
        response = self.client.get('/api/risks')
        self.assertEqual(response.status_code, 200)

    def test_api_risks_returns_json(self):
        """GET /api/risks should return valid JSON."""
        response = self.client.get('/api/risks')
        data = response.get_json()
        self.assertIsInstance(data, dict)

    def test_api_risks_has_risks_key(self):
        """GET /api/risks should have 'risks' and 'count' keys."""
        response = self.client.get('/api/risks')
        data = response.get_json()
        self.assertIn('risks', data)
        self.assertIn('count', data)

    def test_api_describe_returns_200(self):
        """GET /api/describe should return 200 OK."""
        response = self.client.get('/api/describe')
        self.assertEqual(response.status_code, 200)

    def test_api_describe_returns_json(self):
        """GET /api/describe should return valid JSON."""
        response = self.client.get('/api/describe')
        data = response.get_json()
        self.assertIsInstance(data, dict)

    def test_api_describe_has_description(self):
        """GET /api/describe should have 'description' key."""
        response = self.client.get('/api/describe')
        data = response.get_json()
        self.assertIn('description', data)

    def test_video_feed_route_exists(self):
        """GET /video_feed should return 200 (MJPEG stream)."""
        response = self.client.get('/video_feed')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
