"""
Tests for privacy.util.conf.conf module
"""

import pytest
import json
from unittest.mock import Mock, patch
from privacy.util.conf.conf import ConfModle


class TestConfModle:
    """Test suite for ConfModle class"""

    @patch('privacy.util.conf.conf.os.getenv')
    @patch('privacy.util.conf.conf.NlpEngineProvider')
    @patch('privacy.util.conf.conf.RecognizerRegistry')
    @patch('privacy.util.conf.conf.AnalyzerEngine')
    def test_getAnalyzerEngin_creates_analyzer_with_spacy(
        self, mock_analyzer_engine, mock_registry, mock_provider, mock_getenv
    ):
        """Test getAnalyzerEngin creates analyzer with spacy configuration"""
        # Setup mocks
        model_config = {
            "lang_code": "en",
            "model_name": "en_core_web_sm"
        }
        mock_getenv.return_value = json.dumps(model_config)
        
        mock_nlp_engine = Mock()
        mock_provider_instance = Mock()
        mock_provider_instance.create_engine.return_value = mock_nlp_engine
        mock_provider.return_value = mock_provider_instance
        
        mock_registry_instance = Mock()
        mock_registry.return_value = mock_registry_instance
        
        mock_analyzer_instance = Mock()
        mock_analyzer_engine.return_value = mock_analyzer_instance
        
        # Call the method
        analyzer, registry = ConfModle.getAnalyzerEngin("MODEL_CONFIG")
        
        # Assertions
        mock_getenv.assert_called_once_with("MODEL_CONFIG")
        
        # Verify NlpEngineProvider was called with correct configuration
        mock_provider.assert_called_once()
        call_args = mock_provider.call_args
        assert call_args[1]['nlp_configuration']['nlp_engine_name'] == 'spacy'
        assert model_config in call_args[1]['nlp_configuration']['models']
        
        # Verify engine creation
        mock_provider_instance.create_engine.assert_called_once()
        
        # Verify analyzer engine creation
        mock_analyzer_engine.assert_called_once_with(
            registry=mock_registry_instance,
            nlp_engine=mock_nlp_engine
        )
        
        # Verify return values
        assert analyzer == mock_analyzer_instance
        assert registry == mock_registry_instance

    @patch('privacy.util.conf.conf.os.getenv')
    @patch('privacy.util.conf.conf.NlpEngineProvider')
    @patch('privacy.util.conf.conf.RecognizerRegistry')
    @patch('privacy.util.conf.conf.AnalyzerEngine')
    def test_getAnalyzerEngin_with_different_model_config(
        self, mock_analyzer_engine, mock_registry, mock_provider, mock_getenv
    ):
        """Test getAnalyzerEngin with different model configuration"""
        # Setup with different model
        model_config = {
            "lang_code": "es",
            "model_name": "es_core_news_sm"
        }
        mock_getenv.return_value = json.dumps(model_config)
        
        mock_nlp_engine = Mock()
        mock_provider_instance = Mock()
        mock_provider_instance.create_engine.return_value = mock_nlp_engine
        mock_provider.return_value = mock_provider_instance
        
        mock_registry_instance = Mock()
        mock_registry.return_value = mock_registry_instance
        
        mock_analyzer_instance = Mock()
        mock_analyzer_engine.return_value = mock_analyzer_instance
        
        # Call the method
        analyzer, registry = ConfModle.getAnalyzerEngin("ES_MODEL_CONFIG")
        
        # Verify correct configuration
        call_args = mock_provider.call_args
        assert model_config in call_args[1]['nlp_configuration']['models']
        assert analyzer == mock_analyzer_instance
        assert registry == mock_registry_instance

    @patch('privacy.util.conf.conf.os.getenv')
    def test_getAnalyzerEngin_with_invalid_json(self, mock_getenv):
        """Test getAnalyzerEngin handles invalid JSON from environment"""
        mock_getenv.return_value = "invalid json string"
        
        with pytest.raises(json.JSONDecodeError):
            ConfModle.getAnalyzerEngin("INVALID_CONFIG")

    @patch('privacy.util.conf.conf.os.getenv')
    @patch('privacy.util.conf.conf.NlpEngineProvider')
    @patch('privacy.util.conf.conf.RecognizerRegistry')
    @patch('privacy.util.conf.conf.AnalyzerEngine')
    def test_getAnalyzerEngin_with_complex_model_config(
        self, mock_analyzer_engine, mock_registry, mock_provider, mock_getenv
    ):
        """Test getAnalyzerEngin with complex model configuration"""
        # Setup with complex configuration
        model_config = {
            "lang_code": "en",
            "model_name": "en_core_web_lg",
            "extra_param1": "value1",
            "extra_param2": {"nested": "value"}
        }
        mock_getenv.return_value = json.dumps(model_config)
        
        mock_nlp_engine = Mock()
        mock_provider_instance = Mock()
        mock_provider_instance.create_engine.return_value = mock_nlp_engine
        mock_provider.return_value = mock_provider_instance
        
        mock_registry_instance = Mock()
        mock_registry.return_value = mock_registry_instance
        
        mock_analyzer_instance = Mock()
        mock_analyzer_engine.return_value = mock_analyzer_instance
        
        # Call the method
        analyzer, registry = ConfModle.getAnalyzerEngin("COMPLEX_CONFIG")
        
        # Verify the complex config is preserved
        call_args = mock_provider.call_args
        assert model_config in call_args[1]['nlp_configuration']['models']
        assert analyzer == mock_analyzer_instance
