"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))


class TestGibberishRouter(unittest.TestCase):
    """Test cases for gibberishRouter endpoints."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
        # Import and register blueprint after Flask app is created
        with patch('routing.gibberishRouter.CustomLogger'):
            from routing.gibberishRouter import gibberish_router
            self.app.register_blueprint(gibberish_router)
        
        self.client = self.app.test_client()
    
    @patch('routing.gibberishRouter.Gibberish')
    @patch('routing.gibberishRouter.CustomLogger')
    def test_gibberishmodel_success(self, mock_logger, mock_gibberish_class):
        """Test successful gibberish scan."""
        mock_gibberish = Mock()
        mock_gibberish.scan.return_value = {"result": "clean", "confidence": 0.95}
        mock_gibberish_class.return_value = mock_gibberish
        
        payload = {
            'text': 'Hello world',
            'labels': ['noise', 'word salad', 'mild gibberish', 'clean']
        }
        response = self.client.post('/gibberishmodel', json=payload)
        
        self.assertEqual(response.status_code, 200)
        mock_gibberish.scan.assert_called_once()
    
    @patch('routing.gibberishRouter.Gibberish')
    @patch('routing.gibberishRouter.CustomLogger')
    def test_gibberishmodel_no_payload(self, mock_logger, mock_gibberish_class):
        """Test gibberishmodel with no payload."""
        response = self.client.post('/gibberishmodel', json=None)
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.gibberishRouter.Gibberish')
    @patch('routing.gibberishRouter.CustomLogger')
    def test_gibberishmodel_validation_error(self, mock_logger, mock_gibberish_class):
        """Test gibberishmodel with validation error."""
        from exception.exception import ValidationError
        
        mock_gibberish = Mock()
        mock_gibberish.scan.side_effect = ValidationError("Invalid input", service_name="gibberish")
        mock_gibberish_class.return_value = mock_gibberish
        
        payload = {'text': 'test', 'labels': ['clean']}
        response = self.client.post('/gibberishmodel', json=payload)
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.gibberishRouter.Gibberish')
    @patch('routing.gibberishRouter.CustomLogger')
    def test_gibberishmodel_processing_error(self, mock_logger, mock_gibberish_class):
        """Test gibberishmodel with processing error."""
        from exception.exception import ProcessingError
        
        mock_gibberish = Mock()
        mock_gibberish.scan.side_effect = ProcessingError("Processing failed", service_name="gibberish")
        mock_gibberish_class.return_value = mock_gibberish
        
        payload = {'text': 'test', 'labels': ['clean']}
        response = self.client.post('/gibberishmodel', json=payload)
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.gibberishRouter.Gibberish')
    @patch('routing.gibberishRouter.CustomLogger')
    def test_gibberishmodel_service_exception(self, mock_logger, mock_gibberish_class):
        """Test gibberishmodel with service exception."""
        from exception.exception import ServiceException
        
        mock_gibberish = Mock()
        mock_gibberish.scan.side_effect = ServiceException("Service error", status_code=503)
        mock_gibberish_class.return_value = mock_gibberish
        
        payload = {'text': 'test', 'labels': ['clean']}
        response = self.client.post('/gibberishmodel', json=payload)
        
        self.assertEqual(response.status_code, 503)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.gibberishRouter.Gibberish')
    @patch('routing.gibberishRouter.CustomLogger')
    def test_gibberishmodel_unprocessable_entity(self, mock_logger, mock_gibberish_class):
        """Test gibberishmodel with unprocessable entity."""
        from werkzeug.exceptions import UnprocessableEntity
        
        mock_gibberish = Mock()
        mock_gibberish.scan.side_effect = UnprocessableEntity("Unprocessable")
        mock_gibberish_class.return_value = mock_gibberish
        
        payload = {'text': 'test', 'labels': ['clean']}
        response = self.client.post('/gibberishmodel', json=payload)
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.gibberishRouter.Gibberish')
    @patch('routing.gibberishRouter.CustomLogger')
    def test_gibberishmodel_generic_exception(self, mock_logger, mock_gibberish_class):
        """Test gibberishmodel with generic exception."""
        mock_gibberish = Mock()
        mock_gibberish.scan.side_effect = Exception("Unexpected error")
        mock_gibberish_class.return_value = mock_gibberish
        
        payload = {'text': 'test', 'labels': ['clean']}
        response = self.client.post('/gibberishmodel', json=payload)
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.gibberishRouter.Gibberish')
    @patch('routing.gibberishRouter.CustomLogger')
    def test_gibberishmodel_noise_detected(self, mock_logger, mock_gibberish_class):
        """Test gibberishmodel detecting noise in text."""
        mock_gibberish = Mock()
        mock_gibberish.scan.return_value = {
            "result": "noise",
            "confidence": 0.89,
            "label": "noise"
        }
        mock_gibberish_class.return_value = mock_gibberish
        
        payload = {
            'text': 'asdfghjkl qwertyuiop',
            'labels': ['noise', 'word salad', 'mild gibberish', 'clean']
        }
        response = self.client.post('/gibberishmodel', json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['result'], 'noise')
    
    @patch('routing.gibberishRouter.Gibberish')
    @patch('routing.gibberishRouter.CustomLogger')
    def test_gibberishmodel_word_salad(self, mock_logger, mock_gibberish_class):
        """Test gibberishmodel detecting word salad."""
        mock_gibberish = Mock()
        mock_gibberish.scan.return_value = {
            "result": "word salad",
            "confidence": 0.82
        }
        mock_gibberish_class.return_value = mock_gibberish
        
        payload = {
            'text': 'random words without meaning together',
            'labels': ['noise', 'word salad', 'mild gibberish', 'clean']
        }
        response = self.client.post('/gibberishmodel', json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['result'], 'word salad')


if __name__ == '__main__':
    unittest.main()
