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


class TestBancodeRouter(unittest.TestCase):
    """Test cases for bancodeRouter endpoints."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
        # Import and register blueprint after Flask app is created
        with patch('routing.bancodeRouter.CustomLogger'):
            from routing.bancodeRouter import bancode_router
            self.app.register_blueprint(bancode_router)
        
        self.client = self.app.test_client()
    
    @patch('routing.bancodeRouter.BanCode')
    @patch('routing.bancodeRouter.CustomLogger')
    def test_bancodemodel_success(self, mock_logger, mock_bancode_class):
        """Test successful bancode scan."""
        mock_bancode = Mock()
        mock_bancode.scan.return_value = {"result": "no_code_detected", "confidence": 0.95}
        mock_bancode_class.return_value = mock_bancode
        
        response = self.client.post('/bancodemodel', 
                                   json={'text': 'Hello world'})
        
        self.assertEqual(response.status_code, 200)
        mock_bancode.scan.assert_called_once()
    
    @patch('routing.bancodeRouter.BanCode')
    @patch('routing.bancodeRouter.CustomLogger')
    def test_bancodemodel_no_payload(self, mock_logger, mock_bancode_class):
        """Test bancodemodel with no payload."""
        response = self.client.post('/bancodemodel', 
                                   json=None)
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.bancodeRouter.BanCode')
    @patch('routing.bancodeRouter.CustomLogger')
    def test_bancodemodel_validation_error(self, mock_logger, mock_bancode_class):
        """Test bancodemodel with validation error."""
        from exception.exception import ValidationError
        
        mock_bancode = Mock()
        mock_bancode.scan.side_effect = ValidationError("Invalid input", service_name="bancode")
        mock_bancode_class.return_value = mock_bancode
        
        response = self.client.post('/bancodemodel', 
                                   json={'text': 'test'})
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.bancodeRouter.BanCode')
    @patch('routing.bancodeRouter.CustomLogger')
    def test_bancodemodel_processing_error(self, mock_logger, mock_bancode_class):
        """Test bancodemodel with processing error."""
        from exception.exception import ProcessingError
        
        mock_bancode = Mock()
        mock_bancode.scan.side_effect = ProcessingError("Processing failed", service_name="bancode")
        mock_bancode_class.return_value = mock_bancode
        
        response = self.client.post('/bancodemodel', 
                                   json={'text': 'test'})
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.bancodeRouter.BanCode')
    @patch('routing.bancodeRouter.CustomLogger')
    def test_bancodemodel_service_exception(self, mock_logger, mock_bancode_class):
        """Test bancodemodel with service exception."""
        from exception.exception import ServiceException
        
        mock_bancode = Mock()
        mock_bancode.scan.side_effect = ServiceException("Service error", status_code=503)
        mock_bancode_class.return_value = mock_bancode
        
        response = self.client.post('/bancodemodel', 
                                   json={'text': 'test'})
        
        self.assertEqual(response.status_code, 503)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.bancodeRouter.BanCode')
    @patch('routing.bancodeRouter.CustomLogger')
    def test_bancodemodel_unprocessable_entity(self, mock_logger, mock_bancode_class):
        """Test bancodemodel with unprocessable entity."""
        from werkzeug.exceptions import UnprocessableEntity
        
        mock_bancode = Mock()
        mock_bancode.scan.side_effect = UnprocessableEntity("Unprocessable")
        mock_bancode_class.return_value = mock_bancode
        
        response = self.client.post('/bancodemodel', 
                                   json={'text': 'test'})
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.bancodeRouter.BanCode')
    @patch('routing.bancodeRouter.CustomLogger')
    def test_bancodemodel_generic_exception(self, mock_logger, mock_bancode_class):
        """Test bancodemodel with generic exception."""
        mock_bancode = Mock()
        mock_bancode.scan.side_effect = Exception("Unexpected error")
        mock_bancode_class.return_value = mock_bancode
        
        response = self.client.post('/bancodemodel', 
                                   json={'text': 'test'})
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.bancodeRouter.BanCode')
    @patch('routing.bancodeRouter.CustomLogger')
    def test_bancodemodel_code_detected(self, mock_logger, mock_bancode_class):
        """Test bancodemodel detecting code in text."""
        mock_bancode = Mock()
        mock_bancode.scan.return_value = {
            "result": "code_detected",
            "confidence": 0.98,
            "code_type": "python"
        }
        mock_bancode_class.return_value = mock_bancode
        
        response = self.client.post('/bancodemodel', 
                                   json={'text': 'def hello(): print("world")'})
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['result'], 'code_detected')


if __name__ == '__main__':
    unittest.main()
