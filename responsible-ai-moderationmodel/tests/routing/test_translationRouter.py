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


class TestTranslationRouter(unittest.TestCase):
    """Test cases for translationRouter endpoints."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
        # Import and register blueprint after Flask app is created
        with patch('routing.translationRouter.CustomLogger'):
            from routing.translationRouter import translation_router
            self.app.register_blueprint(translation_router)
        
        self.client = self.app.test_client()
    
    @patch('routing.translationRouter.translate_to_english')
    @patch('routing.translationRouter.log_dict', {})
    @patch('routing.translationRouter.CustomLogger')
    def test_translation_model_success(self, mock_logger, mock_translate):
        """Test successful translation."""
        mock_translate.return_value = {
            "translated_text": "Hello world",
            "detectedLanguage": "es",
            "time_taken": "0.5s"
        }
        
        response = self.client.post('/translationmodel', 
                                   json={'text': 'Hola mundo'})
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['translatedText'], 'Hello world')
        self.assertEqual(data['detectedLanguage'], 'es')
    
    @patch('routing.translationRouter.translate_to_english')
    @patch('routing.translationRouter.log_dict', {})
    @patch('routing.translationRouter.CustomLogger')
    def test_translation_model_empty_text(self, mock_logger, mock_translate):
        """Test translation with empty text."""
        response = self.client.post('/translationmodel', 
                                   json={'text': ''})
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.translationRouter.translate_to_english')
    @patch('routing.translationRouter.log_dict', {})
    @patch('routing.translationRouter.CustomLogger')
    def test_translation_model_whitespace_only(self, mock_logger, mock_translate):
        """Test translation with whitespace only text."""
        response = self.client.post('/translationmodel', 
                                   json={'text': '   '})
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.translationRouter.translate_to_english')
    @patch('routing.translationRouter.log_dict', {})
    @patch('routing.translationRouter.CustomLogger')
    def test_translation_model_no_payload(self, mock_logger, mock_translate):
        """Test translation with no payload."""
        response = self.client.post('/translationmodel', json=None)
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.translationRouter.translate_to_english')
    @patch('routing.translationRouter.log_dict', {})
    @patch('routing.translationRouter.CustomLogger')
    def test_translation_model_missing_text_field(self, mock_logger, mock_translate):
        """Test translation with missing text field."""
        response = self.client.post('/translationmodel', json={})
        
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.translationRouter.translate_to_english')
    @patch('routing.translationRouter.log_dict', {})
    @patch('routing.translationRouter.CustomLogger')
    def test_translation_model_validation_error(self, mock_logger, mock_translate):
        """Test translation with validation error."""
        from exception.exception import ValidationError
        
        mock_translate.side_effect = ValidationError("Invalid input", service_name="translation")
        
        response = self.client.post('/translationmodel', 
                                   json={'text': 'test'})
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.translationRouter.translate_to_english')
    @patch('routing.translationRouter.log_dict', {})
    @patch('routing.translationRouter.CustomLogger')
    def test_translation_model_processing_error(self, mock_logger, mock_translate):
        """Test translation with processing error."""
        from exception.exception import ProcessingError
        
        mock_translate.side_effect = ProcessingError("Processing failed", service_name="translation")
        
        response = self.client.post('/translationmodel', 
                                   json={'text': 'test'})
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.translationRouter.translate_to_english')
    @patch('routing.translationRouter.log_dict', {})
    @patch('routing.translationRouter.CustomLogger')
    def test_translation_model_service_exception(self, mock_logger, mock_translate):
        """Test translation with service exception."""
        from exception.exception import ServiceException
        
        mock_translate.side_effect = ServiceException("Service error", status_code=503)
        
        response = self.client.post('/translationmodel', 
                                   json={'text': 'test'})
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.translationRouter.translate_to_english')
    @patch('routing.translationRouter.log_dict', {})
    @patch('routing.translationRouter.CustomLogger')
    def test_translation_model_translation_exception(self, mock_logger, mock_translate):
        """Test translation with exception during translation."""
        mock_translate.side_effect = Exception("Translation failed")
        
        response = self.client.post('/translationmodel', 
                                   json={'text': 'test'})
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('routing.translationRouter.translate_to_english')
    @patch('routing.translationRouter.log_dict', {})
    @patch('routing.translationRouter.CustomLogger')
    def test_translation_model_multiple_languages(self, mock_logger, mock_translate):
        """Test translation from different languages."""
        mock_translate.return_value = {
            "translated_text": "Good morning",
            "detectedLanguage": "fr",
            "time_taken": "0.3s"
        }
        
        response = self.client.post('/translationmodel', 
                                   json={'text': 'Bonjour'})
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['translatedText'], 'Good morning')
        self.assertEqual(data['detectedLanguage'], 'fr')
    
    @patch('routing.translationRouter.translate_to_english')
    @patch('routing.translationRouter.log_dict', {})
    @patch('routing.translationRouter.CustomLogger')
    def test_translation_model_english_input(self, mock_logger, mock_translate):
        """Test translation with English input."""
        mock_translate.return_value = {
            "translated_text": "Hello world",
            "detectedLanguage": "en",
            "time_taken": "0.1s"
        }
        
        response = self.client.post('/translationmodel', 
                                   json={'text': 'Hello world'})
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['translatedText'], 'Hello world')


if __name__ == '__main__':
    unittest.main()
