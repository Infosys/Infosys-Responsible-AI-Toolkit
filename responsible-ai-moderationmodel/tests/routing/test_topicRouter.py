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


class TestTopicRouter(unittest.TestCase):
    """Test cases for topicRouter endpoints."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
        # Import and register blueprint after Flask app is created
        with patch('routing.topicRouter.CustomLogger'):
            from routing.topicRouter import topic_router
            self.app.register_blueprint(topic_router)
        
        self.client = self.app.test_client()
    
    @patch('routing.topicRouter.restricttopic_check')
    @patch('routing.topicRouter.CustomLogger')
    def test_restricted_topic_model_success_deberta(self, mock_logger, mock_topic):
        """Test successful restricted topic check with deberta model."""
        mock_topic.log_dict = {}
        mock_topic.return_value = {
            "topic": "technology",
            "confidence": 0.95,
            "restricted": False
        }
        
        payload = {
            'text': 'Hello world',
            'model': 'deberta',
            'labels': ['technology', 'politics', 'sports']
        }
        response = self.client.post('/restrictedtopicmodel', json=payload)
        
        self.assertEqual(response.status_code, 200)
        mock_topic.assert_called_once()
    
    @patch('routing.topicRouter.restricttopic_check')
    @patch('routing.topicRouter.CustomLogger')
    def test_restricted_topic_model_success_distilbert(self, mock_logger, mock_topic):
        """Test successful restricted topic check with fine-tuned distilbert model."""
        mock_topic.log_dict = {}
        mock_topic.return_value = {
            "topic": "general",
            "confidence": 0.88
        }
        
        payload = {
            'text': 'Hello world',
            'model': 'fine-tuned distilbert'
        }
        response = self.client.post('/restrictedtopicmodel', json=payload)
        
        self.assertEqual(response.status_code, 200)
        mock_topic.assert_called_once()
    
    @patch('routing.topicRouter.restricttopic_check')
    @patch('routing.topicRouter.CustomLogger')
    def test_restricted_topic_model_no_payload(self, mock_logger, mock_topic):
        """Test restricted topic with no payload."""
        response = self.client.post('/restrictedtopicmodel', json=None)
        
        self.assertEqual(response.status_code, 415)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.topicRouter.restricttopic_check')
    @patch('routing.topicRouter.CustomLogger')
    def test_restricted_topic_model_empty_text(self, mock_logger, mock_topic):
        """Test restricted topic with empty text."""
        payload = {
            'text': '',
            'model': 'deberta',
            'labels': ['technology']
        }
        response = self.client.post('/restrictedtopicmodel', json=payload)
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.topicRouter.restricttopic_check')
    @patch('routing.topicRouter.CustomLogger')
    def test_restricted_topic_model_null_text(self, mock_logger, mock_topic):
        """Test restricted topic with null text."""
        payload = {
            'text': None,
            'model': 'deberta',
            'labels': ['technology']
        }
        response = self.client.post('/restrictedtopicmodel', json=payload)
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.topicRouter.restricttopic_check')
    @patch('routing.topicRouter.CustomLogger')
    def test_restricted_topic_model_deberta_missing_labels(self, mock_logger, mock_topic):
        """Test restricted topic with deberta model but missing labels."""
        payload = {
            'text': 'Hello world',
            'model': 'deberta'
        }
        response = self.client.post('/restrictedtopicmodel', json=payload)
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.topicRouter.restricttopic_check')
    @patch('routing.topicRouter.CustomLogger')
    def test_restricted_topic_model_deberta_empty_labels(self, mock_logger, mock_topic):
        """Test restricted topic with deberta model but empty labels."""
        payload = {
            'text': 'Hello world',
            'model': 'deberta',
            'labels': []
        }
        response = self.client.post('/restrictedtopicmodel', json=payload)
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.topicRouter.restricttopic_check')
    @patch('routing.topicRouter.CustomLogger')
    def test_restricted_topic_model_unknown_model(self, mock_logger, mock_topic):
        """Test restricted topic with unknown model."""
        payload = {
            'text': 'Hello world',
            'model': 'unknown_model',
            'labels': ['technology']
        }
        response = self.client.post('/restrictedtopicmodel', json=payload)
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.topicRouter.restricttopic_check')
    @patch('routing.topicRouter.CustomLogger')
    def test_restricted_topic_model_validation_error(self, mock_logger, mock_topic):
        """Test restricted topic with validation error."""
        from exception.exception import ValidationError
        
        mock_topic.log_dict = {}
        mock_topic.side_effect = ValidationError("Invalid input", service_name="topic")
        
        payload = {
            'text': 'test',
            'model': 'deberta',
            'labels': ['technology']
        }
        response = self.client.post('/restrictedtopicmodel', json=payload)
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.topicRouter.restricttopic_check')
    @patch('routing.topicRouter.CustomLogger')
    def test_restricted_topic_model_processing_error(self, mock_logger, mock_topic):
        """Test restricted topic with processing error."""
        from exception.exception import ProcessingError
        
        mock_topic.log_dict = {}
        mock_topic.side_effect = ProcessingError("Processing failed", service_name="topic")
        
        payload = {
            'text': 'test',
            'model': 'deberta',
            'labels': ['technology']
        }
        response = self.client.post('/restrictedtopicmodel', json=payload)
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.topicRouter.restricttopic_check')
    @patch('routing.topicRouter.CustomLogger')
    def test_restricted_topic_model_service_exception(self, mock_logger, mock_topic):
        """Test restricted topic with service exception."""
        from exception.exception import ServiceException
        
        mock_topic.log_dict = {}
        mock_topic.side_effect = ServiceException("Service error", status_code=503)
        
        payload = {
            'text': 'test',
            'model': 'deberta',
            'labels': ['technology']
        }
        response = self.client.post('/restrictedtopicmodel', json=payload)
        
        self.assertEqual(response.status_code, 503)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.topicRouter.restricttopic_check')
    @patch('routing.topicRouter.CustomLogger')
    def test_restricted_topic_model_restricted_detected(self, mock_logger, mock_topic):
        """Test restricted topic detecting restricted content."""
        mock_topic.log_dict = {}
        mock_topic.return_value = {
            "topic": "violence",
            "confidence": 0.92,
            "restricted": True,
            "severity": "high"
        }
        
        payload = {
            'text': 'violent content',
            'model': 'deberta',
            'labels': ['violence', 'general', 'sports']
        }
        response = self.client.post('/restrictedtopicmodel', json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['restricted'])
    
    @patch('routing.topicRouter.restricttopic_check')
    @patch('routing.topicRouter.CustomLogger')
    def test_restricted_topic_model_generic_exception(self, mock_logger, mock_topic):
        """Test restricted topic with generic exception."""
        mock_topic.log_dict = {}
        mock_topic.side_effect = Exception("Unexpected error")
        
        payload = {
            'text': 'test',
            'model': 'deberta',
            'labels': ['technology']
        }
        response = self.client.post('/restrictedtopicmodel', json=payload)
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)


if __name__ == '__main__':
    unittest.main()
