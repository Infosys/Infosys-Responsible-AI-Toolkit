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


class TestDetoxifyRouter(unittest.TestCase):
    """Test cases for detoxifyRouter endpoints."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
        # Import and register blueprint after Flask app is created
        with patch('routing.detoxifyRouter.CustomLogger'):
            from routing.detoxifyRouter import detoxify_router
            self.app.register_blueprint(detoxify_router)
        
        self.client = self.app.test_client()
    
    @patch('routing.detoxifyRouter.toxicity_check')
    @patch('routing.detoxifyRouter.log_dict', {})
    @patch('routing.detoxifyRouter.CustomLogger')
    def test_toxic_model_success(self, mock_logger, mock_toxicity):
        """Test successful toxicity check."""
        mock_toxicity.return_value = {
            "toxicity": 0.1,
            "severe_toxicity": 0.05,
            "obscene": 0.02,
            "threat": 0.01,
            "insult": 0.03,
            "identity_attack": 0.01
        }
        
        response = self.client.post('/detoxifymodel', 
                                   json={'text': 'Hello world'})
        
        self.assertEqual(response.status_code, 200)
        mock_toxicity.assert_called_once()
    
    @patch('routing.detoxifyRouter.toxicity_check')
    @patch('routing.detoxifyRouter.log_dict', {})
    @patch('routing.detoxifyRouter.CustomLogger')
    def test_toxic_model_empty_text(self, mock_logger, mock_toxicity):
        """Test detoxifymodel with empty text."""
        response = self.client.post('/detoxifymodel', 
                                   json={'text': ''})
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.detoxifyRouter.toxicity_check')
    @patch('routing.detoxifyRouter.log_dict', {})
    @patch('routing.detoxifyRouter.CustomLogger')
    def test_toxic_model_null_text(self, mock_logger, mock_toxicity):
        """Test detoxifymodel with null text."""
        response = self.client.post('/detoxifymodel', 
                                   json={'text': None})
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.detoxifyRouter.toxicity_check')
    @patch('routing.detoxifyRouter.log_dict', {})
    @patch('routing.detoxifyRouter.CustomLogger')
    def test_toxic_model_no_payload(self, mock_logger, mock_toxicity):
        """Test detoxifymodel with no payload."""
        response = self.client.post('/detoxifymodel', json=None)
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.detoxifyRouter.toxicity_check')
    @patch('routing.detoxifyRouter.log_dict', {})
    @patch('routing.detoxifyRouter.CustomLogger')
    def test_toxic_model_validation_error(self, mock_logger, mock_toxicity):
        """Test detoxifymodel with validation error."""
        from exception.exception import ValidationError
        
        mock_toxicity.side_effect = ValidationError("Invalid input", service_name="detoxify")
        
        response = self.client.post('/detoxifymodel', 
                                   json={'text': 'test'})
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.detoxifyRouter.toxicity_check')
    @patch('routing.detoxifyRouter.log_dict', {})
    @patch('routing.detoxifyRouter.CustomLogger')
    def test_toxic_model_processing_error(self, mock_logger, mock_toxicity):
        """Test detoxifymodel with processing error."""
        from exception.exception import ProcessingError
        
        mock_toxicity.side_effect = ProcessingError("Processing failed", service_name="detoxify")
        
        response = self.client.post('/detoxifymodel', 
                                   json={'text': 'test'})
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.detoxifyRouter.toxicity_check')
    @patch('routing.detoxifyRouter.log_dict', {})
    @patch('routing.detoxifyRouter.CustomLogger')
    def test_toxic_model_service_exception(self, mock_logger, mock_toxicity):
        """Test detoxifymodel with service exception."""
        from exception.exception import ServiceException
        
        mock_toxicity.side_effect = ServiceException("Service error", status_code=503)
        
        response = self.client.post('/detoxifymodel', 
                                   json={'text': 'test'})
        
        self.assertEqual(response.status_code, 503)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.detoxifyRouter.toxicity_check')
    @patch('routing.detoxifyRouter.log_dict', {})
    @patch('routing.detoxifyRouter.CustomLogger')
    def test_toxic_model_high_toxicity(self, mock_logger, mock_toxicity):
        """Test detoxifymodel detecting high toxicity."""
        mock_toxicity.return_value = {
            "toxicity": 0.95,
            "severe_toxicity": 0.89,
            "obscene": 0.92,
            "threat": 0.88,
            "insult": 0.90,
            "identity_attack": 0.85
        }
        
        response = self.client.post('/detoxifymodel', 
                                   json={'text': 'offensive text'})
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertGreater(data['toxicity'], 0.9)
    
    @patch('routing.detoxifyRouter.toxicity_check')
    @patch('routing.detoxifyRouter.log_dict', {})
    @patch('routing.detoxifyRouter.CustomLogger')
    def test_toxic_model_generic_exception(self, mock_logger, mock_toxicity):
        """Test detoxifymodel with generic exception."""
        mock_toxicity.side_effect = Exception("Unexpected error")
        
        response = self.client.post('/detoxifymodel', 
                                   json={'text': 'test'})
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)


if __name__ == '__main__':
    unittest.main()
