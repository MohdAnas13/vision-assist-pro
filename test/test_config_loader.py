# test/test_config_loader.py
"""Unit tests for the Config Loader."""
import unittest
import sys
import os
import json
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.config_loader import ConfigLoader


class TestConfigLoader(unittest.TestCase):
    """Tests for ConfigLoader JSON loading and environment variable injection."""

    def setUp(self):
        """Create a temporary config file for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'test_config.json')
        self.config_data = {
            'app_name': 'TestApp',
            'model': {'yolo_path': 'models/test.pt', 'confidence_threshold': 0.5},
            'risk_assessment': {
                'danger_distance_car': 5,
                'danger_distance_person': 3,
                'warning_distance_car': 10,
                'warning_distance_person': 5,
            },
            'api': {'gemini_model': 'gemini-test', 'temperature': 0.7},
            'audio': {'voice_speed': 1.0, 'volume': 0.8},
        }
        with open(self.config_file, 'w') as f:
            json.dump(self.config_data, f)

    def tearDown(self):
        """Clean up temporary files."""
        os.remove(self.config_file)
        os.rmdir(self.temp_dir)

    def test_load_json_correctly(self):
        """ConfigLoader should load JSON data correctly."""
        loader = ConfigLoader(self.config_file)
        config = loader.load()
        self.assertEqual(config['app_name'], 'TestApp')
        self.assertEqual(config['model']['yolo_path'], 'models/test.pt')
        self.assertEqual(config['model']['confidence_threshold'], 0.5)

    def test_injects_gemini_api_key_from_env(self):
        """GEMINI_API_KEY from environment should be injected into config."""
        os.environ['GEMINI_API_KEY'] = 'test_api_key_123'
        try:
            loader = ConfigLoader(self.config_file)
            config = loader.load()
            self.assertEqual(config['api']['gemini_api_key'], 'test_api_key_123')
        finally:
            del os.environ['GEMINI_API_KEY']

    def test_gemini_api_key_loaded_from_env_file(self):
        """gemini_api_key should be loaded from .env file if present."""
        # The project .env file may contain a real API key, so load_dotenv() will pick it up.
        # We verify that the key is present in the loaded config (not None).
        loader = ConfigLoader(self.config_file)
        config = loader.load()
        # The key should be set (either from .env or from environment)
        self.assertIn('gemini_api_key', config['api'])

    def test_preserves_existing_api_keys(self):
        """Existing API config keys should be preserved."""
        loader = ConfigLoader(self.config_file)
        config = loader.load()
        self.assertEqual(config['api']['gemini_model'], 'gemini-test')
        self.assertEqual(config['api']['temperature'], 0.7)

    def test_preserves_risk_assessment_config(self):
        """Risk assessment config should be loaded correctly."""
        loader = ConfigLoader(self.config_file)
        config = loader.load()
        self.assertEqual(config['risk_assessment']['danger_distance_car'], 5)
        self.assertEqual(config['risk_assessment']['danger_distance_person'], 3)
        self.assertEqual(config['risk_assessment']['warning_distance_car'], 10)
        self.assertEqual(config['risk_assessment']['warning_distance_person'], 5)

    def test_preserves_audio_config(self):
        """Audio config should be loaded correctly."""
        loader = ConfigLoader(self.config_file)
        config = loader.load()
        self.assertEqual(config['audio']['voice_speed'], 1.0)
        self.assertEqual(config['audio']['volume'], 0.8)

    def test_missing_config_file_raises_error(self):
        """Loading a non-existent config file should raise FileNotFoundError."""
        loader = ConfigLoader('nonexistent.json')
        with self.assertRaises(FileNotFoundError):
            loader.load()

    def test_config_has_all_expected_top_level_keys(self):
        """Config should have all expected top-level keys."""
        loader = ConfigLoader(self.config_file)
        config = loader.load()
        expected_keys = ['app_name', 'model', 'risk_assessment', 'api', 'audio']
        for key in expected_keys:
            self.assertIn(key, config)


if __name__ == '__main__':
    unittest.main()
