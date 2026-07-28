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


class TestSentimentRouter(unittest.TestCase):
    """Test cases for sentimentRouter endpoints."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
        # Import and register blueprint after Flask app is created
        with patch('routing.sentimentRouter.CustomLogger'):
            from routing.sentimentRouter import sentiment_router
            self.app.register_blueprint(sentiment_router)
        
        self.client = self.app.test_client()
    
    @patch('routing.sentimentRouter.Sentiment')
    @patch('routing.sentimentRouter.CustomLogger')
    def test_sentimentmodel_success(self, mock_logger, mock_sentiment_class):
        """Test successful sentiment scan."""
        mock_sentiment = Mock()
        mock_sentiment.scan.return_value = {
            "sentiment": "positive",
            "compound": 0.8,
            "positive": 0.8,
            "neutral": 0.2,
            "negative": 0.0
        }
        mock_sentiment_class.return_value = mock_sentiment
        
        payload = {'text': 'I love this!'}
        response = self.client.post('/sentimentmodel', json=payload)
        
        self.assertEqual(response.status_code, 200)
        mock_sentiment.scan.assert_called_once_with('I love this!')
    
    @patch('routing.sentimentRouter.Sentiment')
    @patch('routing.sentimentRouter.CustomLogger')
    def test_sentimentmodel_no_payload(self, mock_logger, mock_sentiment_class):
        """Test sentimentmodel with no payload."""
        response = self.client.post('/sentimentmodel', json=None)
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.sentimentRouter.Sentiment')
    @patch('routing.sentimentRouter.CustomLogger')
    def test_sentimentmodel_validation_error(self, mock_logger, mock_sentiment_class):
        """Test sentimentmodel with validation error."""
        from exception.exception import ValidationError
        
        mock_sentiment = Mock()
        mock_sentiment.scan.side_effect = ValidationError("Invalid input", service_name="sentiment")
        mock_sentiment_class.return_value = mock_sentiment
        
        payload = {'text': 'test'}
        response = self.client.post('/sentimentmodel', json=payload)
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.sentimentRouter.Sentiment')
    @patch('routing.sentimentRouter.CustomLogger')
    def test_sentimentmodel_processing_error(self, mock_logger, mock_sentiment_class):
        """Test sentimentmodel with processing error."""
        from exception.exception import ProcessingError
        
        mock_sentiment = Mock()
        mock_sentiment.scan.side_effect = ProcessingError("Processing failed", service_name="sentiment")
        mock_sentiment_class.return_value = mock_sentiment
        
        payload = {'text': 'test'}
        response = self.client.post('/sentimentmodel', json=payload)
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.sentimentRouter.Sentiment')
    @patch('routing.sentimentRouter.CustomLogger')
    def test_sentimentmodel_service_exception(self, mock_logger, mock_sentiment_class):
        """Test sentimentmodel with service exception."""
        from exception.exception import ServiceException
        
        mock_sentiment = Mock()
        mock_sentiment.scan.side_effect = ServiceException("Service error", status_code=503)
        mock_sentiment_class.return_value = mock_sentiment
        
        payload = {'text': 'test'}
        response = self.client.post('/sentimentmodel', json=payload)
        
        self.assertEqual(response.status_code, 503)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.sentimentRouter.Sentiment')
    @patch('routing.sentimentRouter.CustomLogger')
    def test_sentimentmodel_unprocessable_entity(self, mock_logger, mock_sentiment_class):
        """Test sentimentmodel with unprocessable entity."""
        from werkzeug.exceptions import UnprocessableEntity
        
        mock_sentiment = Mock()
        mock_sentiment.scan.side_effect = UnprocessableEntity("Unprocessable")
        mock_sentiment_class.return_value = mock_sentiment
        
        payload = {'text': 'test'}
        response = self.client.post('/sentimentmodel', json=payload)
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.sentimentRouter.Sentiment')
    @patch('routing.sentimentRouter.CustomLogger')
    def test_sentimentmodel_generic_exception(self, mock_logger, mock_sentiment_class):
        """Test sentimentmodel with generic exception."""
        mock_sentiment = Mock()
        mock_sentiment.scan.side_effect = Exception("Unexpected error")
        mock_sentiment_class.return_value = mock_sentiment
        
        payload = {'text': 'test'}
        response = self.client.post('/sentimentmodel', json=payload)
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.sentimentRouter.Sentiment')
    @patch('routing.sentimentRouter.CustomLogger')
    def test_sentimentmodel_negative_sentiment(self, mock_logger, mock_sentiment_class):
        """Test sentimentmodel detecting negative sentiment."""
        mock_sentiment = Mock()
        mock_sentiment.scan.return_value = {
            "sentiment": "negative",
            "compound": -0.7,
            "positive": 0.0,
            "neutral": 0.3,
            "negative": 0.7
        }
        mock_sentiment_class.return_value = mock_sentiment
        
        payload = {'text': 'I hate this!'}
        response = self.client.post('/sentimentmodel', json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['sentiment'], 'negative')
    
    @patch('routing.sentimentRouter.Sentiment')
    @patch('routing.sentimentRouter.CustomLogger')
    def test_sentimentmodel_neutral_sentiment(self, mock_logger, mock_sentiment_class):
        """Test sentimentmodel detecting neutral sentiment."""
        mock_sentiment = Mock()
        mock_sentiment.scan.return_value = {
            "sentiment": "neutral",
            "compound": 0.0,
            "positive": 0.0,
            "neutral": 1.0,
            "negative": 0.0
        }
        mock_sentiment_class.return_value = mock_sentiment
        
        payload = {'text': 'The sky is blue.'}
        response = self.client.post('/sentimentmodel', json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['sentiment'], 'neutral')
    
    @patch('routing.sentimentRouter.Sentiment')
    @patch('routing.sentimentRouter.CustomLogger')
    def test_sentimentmodel_mixed_sentiment(self, mock_logger, mock_sentiment_class):
        """Test sentimentmodel with mixed sentiment."""
        mock_sentiment = Mock()
        mock_sentiment.scan.return_value = {
            "sentiment": "mixed",
            "compound": 0.1,
            "positive": 0.4,
            "neutral": 0.3,
            "negative": 0.3
        }
        mock_sentiment_class.return_value = mock_sentiment
        
        payload = {'text': 'I like some things but not others.'}
        response = self.client.post('/sentimentmodel', json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('sentiment', data)


if __name__ == '__main__':
    unittest.main()
