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


class TestInvisibletextRouter(unittest.TestCase):
    """Test cases for invisibletextRouter endpoints."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
        # Import and register blueprint after Flask app is created
        with patch('routing.invisibletextRouter.CustomLogger'):
            from routing.invisibletextRouter import invisibletext_router
            self.app.register_blueprint(invisibletext_router)
        
        self.client = self.app.test_client()
    
    @patch('routing.invisibletextRouter.InvisibleText')
    @patch('routing.invisibletextRouter.CustomLogger')
    def test_invisibletextmodel_success(self, mock_logger, mock_invisible_class):
        """Test successful invisible text scan."""
        mock_invisible = Mock()
        mock_invisible.scan.return_value = {"result": "no_invisible_chars", "count": 0}
        mock_invisible_class.return_value = mock_invisible
        
        payload = {
            'text': 'Hello world',
            'banned_categories': ['Cc', 'Cf']
        }
        response = self.client.post('/invisibletextmodel', json=payload)
        
        self.assertEqual(response.status_code, 200)
        mock_invisible.scan.assert_called_once_with('Hello world', ['Cc', 'Cf'])
    
    @patch('routing.invisibletextRouter.InvisibleText')
    @patch('routing.invisibletextRouter.CustomLogger')
    def test_invisibletextmodel_no_payload(self, mock_logger, mock_invisible_class):
        """Test invisibletextmodel with no payload."""
        response = self.client.post('/invisibletextmodel', json=None)
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.invisibletextRouter.InvisibleText')
    @patch('routing.invisibletextRouter.CustomLogger')
    def test_invisibletextmodel_validation_error(self, mock_logger, mock_invisible_class):
        """Test invisibletextmodel with validation error."""
        from exception.exception import ValidationError
        
        mock_invisible = Mock()
        mock_invisible.scan.side_effect = ValidationError("Invalid input", service_name="invisibletext")
        mock_invisible_class.return_value = mock_invisible
        
        payload = {'text': 'test', 'banned_categories': ['Cc']}
        response = self.client.post('/invisibletextmodel', json=payload)
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.invisibletextRouter.InvisibleText')
    @patch('routing.invisibletextRouter.CustomLogger')
    def test_invisibletextmodel_processing_error(self, mock_logger, mock_invisible_class):
        """Test invisibletextmodel with processing error."""
        from exception.exception import ProcessingError
        
        mock_invisible = Mock()
        mock_invisible.scan.side_effect = ProcessingError("Processing failed", service_name="invisibletext")
        mock_invisible_class.return_value = mock_invisible
        
        payload = {'text': 'test', 'banned_categories': ['Cc']}
        response = self.client.post('/invisibletextmodel', json=payload)
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.invisibletextRouter.InvisibleText')
    @patch('routing.invisibletextRouter.CustomLogger')
    def test_invisibletextmodel_service_exception(self, mock_logger, mock_invisible_class):
        """Test invisibletextmodel with service exception."""
        from exception.exception import ServiceException
        
        mock_invisible = Mock()
        mock_invisible.scan.side_effect = ServiceException("Service error", status_code=503)
        mock_invisible_class.return_value = mock_invisible
        
        payload = {'text': 'test', 'banned_categories': ['Cc']}
        response = self.client.post('/invisibletextmodel', json=payload)
        
        self.assertEqual(response.status_code, 503)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.invisibletextRouter.InvisibleText')
    @patch('routing.invisibletextRouter.CustomLogger')
    def test_invisibletextmodel_unprocessable_entity(self, mock_logger, mock_invisible_class):
        """Test invisibletextmodel with unprocessable entity."""
        from werkzeug.exceptions import UnprocessableEntity
        
        mock_invisible = Mock()
        mock_invisible.scan.side_effect = UnprocessableEntity("Unprocessable")
        mock_invisible_class.return_value = mock_invisible
        
        payload = {'text': 'test', 'banned_categories': ['Cc']}
        response = self.client.post('/invisibletextmodel', json=payload)
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.invisibletextRouter.InvisibleText')
    @patch('routing.invisibletextRouter.CustomLogger')
    def test_invisibletextmodel_generic_exception(self, mock_logger, mock_invisible_class):
        """Test invisibletextmodel with generic exception."""
        mock_invisible = Mock()
        mock_invisible.scan.side_effect = Exception("Unexpected error")
        mock_invisible_class.return_value = mock_invisible
        
        payload = {'text': 'test', 'banned_categories': ['Cc']}
        response = self.client.post('/invisibletextmodel', json=payload)
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.invisibletextRouter.InvisibleText')
    @patch('routing.invisibletextRouter.CustomLogger')
    def test_invisibletextmodel_invisible_chars_detected(self, mock_logger, mock_invisible_class):
        """Test invisibletextmodel detecting invisible characters."""
        mock_invisible = Mock()
        mock_invisible.scan.return_value = {
            "result": "invisible_chars_found",
            "count": 3,
            "categories": ["Cc", "Cf"]
        }
        mock_invisible_class.return_value = mock_invisible
        
        payload = {
            'text': 'Hello\u200bworld\u200c',
            'banned_categories': ['Cc', 'Cf', 'Zl', 'Zp']
        }
        response = self.client.post('/invisibletextmodel', json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['result'], 'invisible_chars_found')
    
    @patch('routing.invisibletextRouter.InvisibleText')
    @patch('routing.invisibletextRouter.CustomLogger')
    def test_invisibletextmodel_control_characters(self, mock_logger, mock_invisible_class):
        """Test invisibletextmodel with control characters."""
        mock_invisible = Mock()
        mock_invisible.scan.return_value = {
            "result": "control_chars_found",
            "count": 2,
            "details": "Found control characters"
        }
        mock_invisible_class.return_value = mock_invisible
        
        payload = {
            'text': 'Text with control chars',
            'banned_categories': ['Cc']
        }
        response = self.client.post('/invisibletextmodel', json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('result', data)


if __name__ == '__main__':
    unittest.main()
