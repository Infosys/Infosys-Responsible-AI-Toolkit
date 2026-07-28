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


class TestPrivacyRouter(unittest.TestCase):
    """Test cases for privacyRouter endpoints."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
        # Import and register blueprint after Flask app is created
        with patch('routing.privacyRouter.CustomLogger'):
            from routing.privacyRouter import privacy_router
            self.app.register_blueprint(privacy_router)
        
        self.client = self.app.test_client()
    
    @patch('routing.privacyRouter.privacy')
    @patch('routing.privacyRouter.log_dict', {})
    @patch('routing.privacyRouter.CustomLogger')
    def test_pii_check_success(self, mock_logger, mock_privacy):
        """Test successful PII check."""
        mock_privacy.return_value = {
            "pii_detected": False,
            "entities": [],
            "confidence": 0.95
        }
        
        response = self.client.post('/privacy', 
                                   json={'text': 'Hello world'})
        
        self.assertEqual(response.status_code, 200)
        mock_privacy.assert_called_once()
    
    @patch('routing.privacyRouter.privacy')
    @patch('routing.privacyRouter.log_dict', {})
    @patch('routing.privacyRouter.CustomLogger')
    def test_pii_check_text_preprocessing(self, mock_logger, mock_privacy):
        """Test PII check with text preprocessing."""
        mock_privacy.return_value = {
            "pii_detected": False,
            "entities": []
        }
        
        response = self.client.post('/privacy', 
                                   json={'text': 'Hello   World   With   Extra   Spaces'})
        
        self.assertEqual(response.status_code, 200)
        # Verify text was lowercased and spaces normalized
        call_args = mock_privacy.call_args[0][0]
        self.assertEqual(call_args, 'hello world with extra spaces')
    
    @patch('routing.privacyRouter.privacy')
    @patch('routing.privacyRouter.log_dict', {})
    @patch('routing.privacyRouter.CustomLogger')
    def test_pii_check_empty_text(self, mock_logger, mock_privacy):
        """Test PII check with empty text."""
        response = self.client.post('/privacy', 
                                   json={'text': ''})
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.privacyRouter.privacy')
    @patch('routing.privacyRouter.log_dict', {})
    @patch('routing.privacyRouter.CustomLogger')
    def test_pii_check_null_text(self, mock_logger, mock_privacy):
        """Test PII check with null text."""
        response = self.client.post('/privacy', 
                                   json={'text': None})
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.privacyRouter.privacy')
    @patch('routing.privacyRouter.log_dict', {})
    @patch('routing.privacyRouter.CustomLogger')
    def test_pii_check_no_payload(self, mock_logger, mock_privacy):
        """Test PII check with no payload."""
        response = self.client.post('/privacy', json=None)
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.privacyRouter.privacy')
    @patch('routing.privacyRouter.log_dict', {})
    @patch('routing.privacyRouter.CustomLogger')
    def test_pii_check_validation_error(self, mock_logger, mock_privacy):
        """Test PII check with validation error."""
        from exception.exception import ValidationError
        
        mock_privacy.side_effect = ValidationError("Invalid input", service_name="privacy")
        
        response = self.client.post('/privacy', 
                                   json={'text': 'test'})
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.privacyRouter.privacy')
    @patch('routing.privacyRouter.log_dict', {})
    @patch('routing.privacyRouter.CustomLogger')
    def test_pii_check_processing_error(self, mock_logger, mock_privacy):
        """Test PII check with processing error."""
        from exception.exception import ProcessingError
        
        mock_privacy.side_effect = ProcessingError("Processing failed", service_name="privacy")
        
        response = self.client.post('/privacy', 
                                   json={'text': 'test'})
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.privacyRouter.privacy')
    @patch('routing.privacyRouter.log_dict', {})
    @patch('routing.privacyRouter.CustomLogger')
    def test_pii_check_service_exception(self, mock_logger, mock_privacy):
        """Test PII check with service exception."""
        from exception.exception import ServiceException
        
        mock_privacy.side_effect = ServiceException("Service error", status_code=503)
        
        response = self.client.post('/privacy', 
                                   json={'text': 'test'})
        
        self.assertEqual(response.status_code, 503)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.privacyRouter.privacy')
    @patch('routing.privacyRouter.log_dict', {})
    @patch('routing.privacyRouter.CustomLogger')
    def test_pii_check_pii_detected(self, mock_logger, mock_privacy):
        """Test PII check detecting personal information."""
        mock_privacy.return_value = {
            "pii_detected": True,
            "entities": [
                {"type": "EMAIL", "text": "test@example.com", "score": 0.98},
                {"type": "PHONE", "text": "123-456-7890", "score": 0.95}
            ],
            "confidence": 0.97
        }
        
        response = self.client.post('/privacy', 
                                   json={'text': 'My email is test@example.com'})
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['pii_detected'])
        self.assertEqual(len(data['entities']), 2)
    
    @patch('routing.privacyRouter.privacy')
    @patch('routing.privacyRouter.log_dict', {})
    @patch('routing.privacyRouter.CustomLogger')
    def test_pii_check_generic_exception(self, mock_logger, mock_privacy):
        """Test PII check with generic exception."""
        mock_privacy.side_effect = Exception("Unexpected error")
        
        response = self.client.post('/privacy', 
                                   json={'text': 'test'})
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)


if __name__ == '__main__':
    unittest.main()
