"""
Comprehensive tests for src/routing/router.py
Tests all routing endpoints, error handling decorators, validators, and service integrations.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock, call
from flask import Flask
from werkzeug.exceptions import UnprocessableEntity

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))


class TestRouterImports(unittest.TestCase):
    """Test that all required imports work correctly"""
    
    @patch('routing.router.jailbreak_check')
    def test_flask_blueprint_import(self, mock_jailbreak):
        """Test Flask Blueprint import"""
        from routing.router import Blueprint
        self.assertIsNotNone(Blueprint)
    
    @patch('routing.router.jailbreak_check')
    def test_fastapi_encoders_import(self, mock_jailbreak):
        """Test FastAPI jsonable_encoder import"""
        from routing.router import jsonable_encoder
        self.assertIsNotNone(jsonable_encoder)
    
    @patch('routing.router.jailbreak_check')
    def test_time_import(self, mock_jailbreak):
        """Test time module import"""
        import time
        self.assertIsNotNone(time)
    
    @patch('routing.router.jailbreak_check')
    def test_uuid_import(self, mock_jailbreak):
        """Test uuid module import"""
        from routing.router import uuid
        self.assertIsNotNone(uuid)
    
    @patch('routing.router.jailbreak_check')
    def test_werkzeug_exceptions_import(self, mock_jailbreak):
        """Test Werkzeug UnprocessableEntity import"""
        from routing.router import UnprocessableEntity
        self.assertIsNotNone(UnprocessableEntity)


class TestRouterConstants(unittest.TestCase):
    """Test constants defined in router.py"""
    
    @patch('routing.router.jailbreak_check')
    def test_input_text_empty_constant(self, mock_jailbreak):
        """Test INPUT_TEXT_EMPTY constant"""
        from routing.router import INPUT_TEXT_EMPTY
        self.assertEqual(INPUT_TEXT_EMPTY, "1021-Input Text should not be empty ")
    
    @patch('routing.router.jailbreak_check')
    def test_response_log_prefix_constant(self, mock_jailbreak):
        """Test RESPONSE_LOG_PREFIX constant"""
        from routing.router import RESPONSE_LOG_PREFIX
        self.assertEqual(RESPONSE_LOG_PREFIX, "response : ")
    
    @patch('routing.router.jailbreak_check')
    def test_exit_toxic_model_msg_constant(self, mock_jailbreak):
        """Test EXIT_TOXIC_MODEL_MSG constant"""
        from routing.router import EXIT_TOXIC_MODEL_MSG
        self.assertEqual(EXIT_TOXIC_MODEL_MSG, "exit toxic_model routing method")
    
    @patch('routing.router.jailbreak_check')
    def test_exit_pii_check_msg_constant(self, mock_jailbreak):
        """Test EXIT_PII_CHECK_MSG constant"""
        from routing.router import EXIT_PII_CHECK_MSG
        self.assertEqual(EXIT_PII_CHECK_MSG, "exit pii_check routing method")
    
    @patch('routing.router.jailbreak_check')
    def test_exit_prompt_model_msg_constant(self, mock_jailbreak):
        """Test EXIT_PROMPT_MODEL_MSG constant"""
        from routing.router import EXIT_PROMPT_MODEL_MSG
        self.assertEqual(EXIT_PROMPT_MODEL_MSG, "exit prompt_model routing method")
    
    @patch('routing.router.jailbreak_check')
    def test_exit_embedding_model_msg_constant(self, mock_jailbreak):
        """Test EXIT_EMBEDDING_MODEL_MSG constant"""
        from routing.router import EXIT_EMBEDDING_MODEL_MSG
        self.assertEqual(EXIT_EMBEDDING_MODEL_MSG, "exit embedding_model routing method")
    
    @patch('routing.router.jailbreak_check')
    def test_exit_restrictedtopic_model_msg_constant(self, mock_jailbreak):
        """Test EXIT_RESTRICTEDTOPIC_MODEL_MSG constant"""
        from routing.router import EXIT_RESTRICTEDTOPIC_MODEL_MSG
        self.assertEqual(EXIT_RESTRICTEDTOPIC_MODEL_MSG, "exit restrictedTopic_model routing method")
    
    @patch('routing.router.jailbreak_check')
    def test_exit_similarity_model_msg_constant(self, mock_jailbreak):
        """Test EXIT_SIMILARITY_MODEL_MSG constant"""
        from routing.router import EXIT_SIMILARITY_MODEL_MSG
        self.assertEqual(EXIT_SIMILARITY_MODEL_MSG, "exit similarity_model routing method")
    
    @patch('routing.router.jailbreak_check')
    def test_exit_sentiment_model_msg_constant(self, mock_jailbreak):
        """Test EXIT_SENTIMENT_MODEL_MSG constant"""
        from routing.router import EXIT_SENTIMENT_MODEL_MSG
        self.assertEqual(EXIT_SENTIMENT_MODEL_MSG, "exit sentiment_model routing method")


class TestRouterBlueprint(unittest.TestCase):
    """Test router blueprint creation"""
    
    @patch('routing.router.jailbreak_check')
    def test_router_blueprint_exists(self, mock_jailbreak):
        """Test that router blueprint is created"""
        from routing.router import router
        self.assertIsNotNone(router)
        self.assertEqual(router.name, 'router')
    
    @patch('routing.router.jailbreak_check')
    def test_logger_instance_created(self, mock_jailbreak):
        """Test that CustomLogger instance is created"""
        from routing.router import log
        self.assertIsNotNone(log)


class TestRouterDecorators(unittest.TestCase):
    """Test decorator functions"""
    
    @patch('routing.router.jailbreak_check')
    def test_handle_errors_decorator_exists(self, mock_jailbreak):
        """Test that handle_errors decorator exists"""
        from routing.router import handle_errors
        self.assertIsNotNone(handle_errors)
        self.assertTrue(callable(handle_errors))
    
    @patch('routing.router.jailbreak_check')
    def test_time_logger_decorator_exists(self, mock_jailbreak):
        """Test that time_logger decorator exists"""
        from routing.router import time_logger
        self.assertIsNotNone(time_logger)
        self.assertTrue(callable(time_logger))
    
    @patch('routing.router.jailbreak_check')
    @patch('routing.router.log')
    def test_handle_errors_catches_validation_error(self, mock_log, mock_jailbreak):
        """Test that handle_errors catches ValidationError"""
        from routing.router import handle_errors
        from exception.exception import ValidationError
        
        @handle_errors
        def test_func():
            raise ValidationError("Test validation error")
        
        result = test_func()
        self.assertIsNotNone(result)
    
    @patch('routing.router.jailbreak_check')
    @patch('routing.router.log')
    def test_handle_errors_catches_processing_error(self, mock_log, mock_jailbreak):
        """Test that handle_errors catches ProcessingError"""
        from routing.router import handle_errors
        from exception.exception import ProcessingError
        
        @handle_errors
        def test_func():
            raise ProcessingError("Test processing error", service_name="test")
        
        result = test_func()
        self.assertIsNotNone(result)
    
    @patch('routing.router.jailbreak_check')
    @patch('routing.router.log')
    def test_handle_errors_catches_service_exception(self, mock_log, mock_jailbreak):
        """Test that handle_errors catches ServiceException"""
        from routing.router import handle_errors
        from exception.exception import ServiceException
        
        @handle_errors
        def test_func():
            raise ServiceException("Test service error", status_code=503)
        
        result = test_func()
        self.assertIsNotNone(result)
    
    @patch('routing.router.jailbreak_check')
    @patch('routing.router.log')
    def test_handle_errors_catches_unprocessable_entity(self, mock_log, mock_jailbreak):
        """Test that handle_errors catches UnprocessableEntity"""
        from routing.router import handle_errors
        from werkzeug.exceptions import UnprocessableEntity
        
        @handle_errors
        def test_func():
            raise UnprocessableEntity("Test unprocessable")
        
        result = test_func()
        self.assertIsNotNone(result)
    
    @patch('routing.router.jailbreak_check')
    @patch('routing.router.log')
    def test_handle_errors_catches_generic_exception(self, mock_log, mock_jailbreak):
        """Test that handle_errors catches generic Exception"""
        from routing.router import handle_errors
        
        @handle_errors
        def test_func():
            raise Exception("Test generic error")
        
        result = test_func()
        self.assertIsNotNone(result)
    
    @patch('routing.router.jailbreak_check')
    @patch('routing.router.log')
    @patch('routing.router.time')
    def test_time_logger_logs_execution_time(self, mock_time, mock_log, mock_jailbreak):
        """Test that time_logger logs execution time"""
        from routing.router import time_logger
        
        mock_time.time.side_effect = [0.0, 1.5]
        
        @time_logger(service_name="test_service")
        def test_func():
            return "result"
        
        result = test_func()
        self.assertEqual(result, "result")
        # Verify log.info was called with timing information
        self.assertTrue(mock_log.info.called)


class TestRouterHelperFunctions(unittest.TestCase):
    """Test helper functions"""
    
    @patch('routing.router.jailbreak_check')
    def test_log_and_cleanup_function_exists(self, mock_jailbreak):
        """Test that log_and_cleanup function exists"""
        from routing.router import log_and_cleanup
        self.assertIsNotNone(log_and_cleanup)
        self.assertTrue(callable(log_and_cleanup))
    
    @patch('routing.router.jailbreak_check')
    def test_validate_payload_function_exists(self, mock_jailbreak):
        """Test that validate_payload function exists"""
        from routing.router import validate_payload
        self.assertIsNotNone(validate_payload)
        self.assertTrue(callable(validate_payload))
    
    @patch('routing.router.jailbreak_check')
    def test_validate_payload_raises_on_empty_payload(self, mock_jailbreak):
        """Test that validate_payload raises ValidationError for empty payload"""
        from routing.router import validate_payload
        from exception.exception import ValidationError
        
        with self.assertRaises(ValidationError):
            validate_payload(None, ['text'])
    
    @patch('routing.router.jailbreak_check')
    def test_validate_payload_raises_on_missing_field(self, mock_jailbreak):
        """Test that validate_payload raises UnprocessableEntity for missing field"""
        from routing.router import validate_payload
        from werkzeug.exceptions import UnprocessableEntity
        
        with self.assertRaises(UnprocessableEntity):
            validate_payload({'other': 'value'}, ['text'])
    
    @patch('routing.router.jailbreak_check')
    def test_validate_payload_passes_with_valid_payload(self, mock_jailbreak):
        """Test that validate_payload passes with valid payload"""
        from routing.router import validate_payload
        
        # Should not raise any exception
        validate_payload({'text': 'valid text'}, ['text'])
    
    @patch('routing.router.jailbreak_check')
    @patch('routing.router.log_dict', {'test-id': ['error1']})
    @patch('routing.router.request_id_var')
    @patch('routing.router.log')
    def test_log_and_cleanup_with_errors(self, mock_log, mock_request_id, mock_jailbreak):
        """Test log_and_cleanup when errors exist"""
        from routing.router import log_and_cleanup, log_dict
        
        mock_request_id.get.return_value = 'test-id'
        log_dict['test-id'] = ['error1']
        
        log_and_cleanup('test-id')
        
        # Verify log.debug was called
        self.assertTrue(mock_log.debug.called)


class TestRouterEndpoints(unittest.TestCase):
    """Test routing endpoints"""
    
    def setUp(self):
        """Set up Flask test client"""
        with patch('routing.router.jailbreak_check'):
            from routing.router import router
            self.app = Flask(__name__)
            self.app.register_blueprint(router, url_prefix='/api')
            self.client = self.app.test_client()
    
    @patch('routing.router.translate_to_english')
    @patch('routing.router.log_dict', {})
    @patch('routing.router.request_id_var')
    def test_translation_model_endpoint(self, mock_request_id, mock_translate):
        """Test /translationmodel endpoint"""
        mock_request_id.get.return_value = 'test-id'
        mock_request_id.set.return_value = None
        mock_translate.return_value = {
            'translated_text': 'Hello',
            'detectedLanguage': 'es',
            'time_taken': 0.5
        }
        
        response = self.client.post('/api/translationmodel', 
                                   json={'text': 'Hola'})
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('translatedText', data)
    
    @patch('routing.router.toxicity_check')
    @patch('routing.router.log_dict', {})
    @patch('routing.router.request_id_var')
    def test_toxic_model_endpoint(self, mock_request_id, mock_toxicity):
        """Test /detoxifymodel endpoint"""
        mock_request_id.get.return_value = 'test-id'
        mock_request_id.set.return_value = None
        mock_toxicity.return_value = {'toxic': False, 'score': 0.1}
        
        response = self.client.post('/api/detoxifymodel', 
                                   json={'text': 'Hello world'})
        
        self.assertEqual(response.status_code, 200)
    
    @patch('routing.router.privacy')
    @patch('routing.router.log_dict', {})
    @patch('routing.router.request_id_var')
    def test_pii_check_endpoint(self, mock_request_id, mock_privacy):
        """Test /privacy endpoint"""
        mock_request_id.get.return_value = 'test-id'
        mock_request_id.set.return_value = None
        mock_privacy.return_value = {'pii_detected': False}
        
        response = self.client.post('/api/privacy', 
                                   json={'text': 'Hello world'})
        
        self.assertEqual(response.status_code, 200)
    
    @patch('routing.router.prompt_injection_check')
    @patch('routing.router.log_dict', {})
    @patch('routing.router.request_id_var')
    def test_prompt_model_endpoint(self, mock_request_id, mock_prompt):
        """Test /promptinjectionmodel endpoint"""
        mock_request_id.get.return_value = 'test-id'
        mock_request_id.set.return_value = None
        mock_prompt.return_value = {'injection_detected': False}
        
        response = self.client.post('/api/promptinjectionmodel', 
                                   json={'text': 'Hello world'})
        
        self.assertEqual(response.status_code, 200)
    
    @patch('routing.router.restricttopic_check')
    @patch('routing.router.log_dict', {})
    @patch('routing.router.request_id_var')
    def test_restrictedtopic_model_endpoint(self, mock_request_id, mock_restrict):
        """Test /restrictedtopicmodel endpoint"""
        mock_request_id.get.return_value = 'test-id'
        mock_request_id.set.return_value = None
        mock_restrict.return_value = {'restricted': False}
        
        response = self.client.post('/api/restrictedtopicmodel', 
                                   json={'text': 'Hello', 'labels': ['violence']})
        
        self.assertEqual(response.status_code, 200)
    
    @patch('routing.router.jailbreak_check')
    @patch('routing.router.log_dict', {})
    @patch('routing.router.request_id_var')
    def test_jailbreak_model_endpoint(self, mock_request_id, mock_jailbreak_check):
        """Test /jailbreak endpoint"""
        mock_request_id.get.return_value = 'test-id'
        mock_request_id.set.return_value = None
        mock_jailbreak_check.return_value = {'jailbreak_detected': False}
        
        response = self.client.post('/api/jailbreak', 
                                   json={'text': 'Hello world'})
        
        self.assertEqual(response.status_code, 200)
    
    @patch('routing.router.multi_q_net_embedding')
    @patch('routing.router.log_dict', {})
    @patch('routing.router.request_id_var')
    def test_embedding_model_endpoint(self, mock_request_id, mock_embedding):
        """Test /multi_q_net_embedding endpoint"""
        mock_request_id.get.return_value = 'test-id'
        mock_request_id.set.return_value = None
        mock_embedding.return_value = {'embedding': [0.1, 0.2, 0.3]}
        
        response = self.client.post('/api/multi_q_net_embedding', 
                                   json={'text': 'Hello world'})
        
        self.assertEqual(response.status_code, 200)
    
    @patch('routing.router.multi_q_net_similarity')
    @patch('routing.router.log_dict', {})
    @patch('routing.router.request_id_var')
    def test_similarity_model_endpoint(self, mock_request_id, mock_similarity):
        """Test /multi-qa-mpnet-model_similarity endpoint"""
        mock_request_id.get.return_value = 'test-id'
        mock_request_id.set.return_value = None
        mock_similarity.return_value = {'similarity': 0.95}
        
        response = self.client.post('/api/multi-qa-mpnet-model_similarity', 
                                   json={'text1': 'Hello', 'text2': 'Hi'})
        
        self.assertEqual(response.status_code, 200)
    
    @patch('routing.router.Sentiment')
    def test_sentiment_model_endpoint(self, mock_sentiment_class):
        """Test /sentimentmodel endpoint"""
        mock_sentiment = MagicMock()
        mock_sentiment.scan.return_value = {'sentiment': 'positive'}
        mock_sentiment_class.return_value = mock_sentiment
        
        response = self.client.post('/api/sentimentmodel', 
                                   json={'text': 'Hello world'})
        
        self.assertEqual(response.status_code, 200)
    
    @patch('routing.router.InvisibleText')
    def test_invisibletext_model_endpoint(self, mock_invisible_class):
        """Test /invisibletextmodel endpoint"""
        mock_invisible = MagicMock()
        mock_invisible.scan.return_value = {'has_invisible': False}
        mock_invisible_class.return_value = mock_invisible
        
        response = self.client.post('/api/invisibletextmodel', 
                                   json={'text': 'Hello', 'banned_categories': []})
        
        self.assertEqual(response.status_code, 200)
    
    @patch('routing.router.Gibberish')
    def test_gibberish_model_endpoint(self, mock_gibberish_class):
        """Test /gibberishmodel endpoint"""
        mock_gibberish = MagicMock()
        mock_gibberish.scan.return_value = {'is_gibberish': False}
        mock_gibberish_class.return_value = mock_gibberish
        
        response = self.client.post('/api/gibberishmodel', 
                                   json={'text': 'Hello world'})
        
        self.assertEqual(response.status_code, 200)
    
    @patch('routing.router.BanCode')
    def test_bancode_model_endpoint(self, mock_bancode_class):
        """Test /bancodemodel endpoint"""
        mock_bancode = MagicMock()
        mock_bancode.scan.return_value = {'is_banned': False}
        mock_bancode_class.return_value = mock_bancode
        
        response = self.client.post('/api/bancodemodel', 
                                   json={'text': 'Hello world'})
        
        self.assertEqual(response.status_code, 200)


class TestRouterValidation(unittest.TestCase):
    """Test input validation for endpoints"""
    
    def setUp(self):
        """Set up Flask test client"""
        with patch('routing.router.jailbreak_check'):
            from routing.router import router
            self.app = Flask(__name__)
            self.app.register_blueprint(router, url_prefix='/api')
            self.client = self.app.test_client()
    
    def test_translation_model_empty_text(self):
        """Test translation endpoint rejects empty text"""
        response = self.client.post('/api/translationmodel', json={})
        self.assertEqual(response.status_code, 422)
    
    def test_detoxify_model_empty_text(self):
        """Test detoxify endpoint rejects empty text"""
        response = self.client.post('/api/detoxifymodel', json={})
        self.assertEqual(response.status_code, 400)
    
    def test_privacy_empty_text(self):
        """Test privacy endpoint rejects empty text"""
        response = self.client.post('/api/privacy', json={})
        self.assertEqual(response.status_code, 400)
    
    def test_prompt_injection_empty_text(self):
        """Test prompt injection endpoint rejects empty text"""
        response = self.client.post('/api/promptinjectionmodel', json={})
        self.assertEqual(response.status_code, 400)
    
    def test_restrictedtopic_empty_text(self):
        """Test restricted topic endpoint rejects empty text"""
        response = self.client.post('/api/restrictedtopicmodel', json={})
        self.assertEqual(response.status_code, 422)
    
    def test_restrictedtopic_empty_labels(self):
        """Test restricted topic endpoint rejects empty labels"""
        response = self.client.post('/api/restrictedtopicmodel', 
                                   json={'text': 'Hello', 'labels': []})
        self.assertEqual(response.status_code, 422)
    
    def test_jailbreak_empty_text(self):
        """Test jailbreak endpoint rejects empty text"""
        response = self.client.post('/api/jailbreak', json={})
        self.assertEqual(response.status_code, 400)
    
    def test_embedding_empty_text(self):
        """Test embedding endpoint rejects empty text"""
        response = self.client.post('/api/multi_q_net_embedding', json={})
        self.assertEqual(response.status_code, 400)
    
    def test_similarity_empty_text1(self):
        """Test similarity endpoint rejects empty text1"""
        response = self.client.post('/api/multi-qa-mpnet-model_similarity', 
                                   json={'text2': 'Hello'})
        self.assertEqual(response.status_code, 422)
    
    def test_similarity_empty_text2(self):
        """Test similarity endpoint rejects empty text2"""
        response = self.client.post('/api/multi-qa-mpnet-model_similarity', 
                                   json={'text1': 'Hello'})
        self.assertEqual(response.status_code, 422)
    
    def test_sentiment_empty_payload(self):
        """Test sentiment endpoint rejects empty payload"""
        response = self.client.post('/api/sentimentmodel', json=None)
        self.assertEqual(response.status_code, 400)
    
    def test_invisibletext_empty_payload(self):
        """Test invisible text endpoint rejects empty payload"""
        response = self.client.post('/api/invisibletextmodel', json=None)
        self.assertEqual(response.status_code, 400)
    
    def test_gibberish_empty_payload(self):
        """Test gibberish endpoint rejects empty payload"""
        response = self.client.post('/api/gibberishmodel', json=None)
        self.assertEqual(response.status_code, 400)
    
    def test_bancode_empty_payload(self):
        """Test bancode endpoint rejects empty payload"""
        response = self.client.post('/api/bancodemodel', json=None)
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
