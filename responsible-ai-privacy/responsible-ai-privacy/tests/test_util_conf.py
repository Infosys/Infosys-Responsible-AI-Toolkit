"""
Tests for conf module.

This module tests the ConfModel class which configures the analyzer engine
with NLP models from environment variables.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
import json
import os

# Import the class to test
from privacy.util.conf.conf import ConfModel


class TestConfModel:
    """Test ConfModel class for analyzer engine configuration."""
    
    def test_get_analyzer_engine_basic(self):
        """Test basic analyzer engine creation."""
        conf = ConfModel()
        
        model_config = {
            "lang_code": "en",
            "model_name": "en_core_web_sm"
        }
        
        with patch.dict(os.environ, {"TEST_MODEL": json.dumps(model_config)}):
            with patch('privacy.util.conf.conf.NlpEngineProvider') as mock_provider:
                with patch('privacy.util.conf.conf.RecognizerRegistry') as mock_registry:
                    with patch('privacy.util.conf.conf.AnalyzerEngine') as mock_analyzer:
                        # Setup mocks
                        mock_nlp_engine = MagicMock()
                        mock_provider_instance = MagicMock()
                        mock_provider_instance.create_engine.return_value = mock_nlp_engine
                        mock_provider.return_value = mock_provider_instance
                        
                        mock_registry_instance = MagicMock()
                        mock_registry.return_value = mock_registry_instance
                        
                        mock_analyzer_instance = MagicMock()
                        mock_analyzer.return_value = mock_analyzer_instance
                        
                        # Call the method
                        analyzer, registry = conf.get_analyzer_engine("TEST_MODEL")
                        
                        # Verify the configuration was parsed correctly
                        assert mock_provider.called
                        assert mock_provider_instance.create_engine.called
                        assert analyzer == mock_analyzer_instance
                        assert registry == mock_registry_instance
    
    def test_get_analyzer_engine_with_spacy_model(self):
        """Test analyzer engine with spacy model configuration."""
        conf = ConfModel()
        
        model_config = {
            "lang_code": "en",
            "model_name": "en_core_web_lg"
        }
        
        with patch.dict(os.environ, {"SPACY_MODEL": json.dumps(model_config)}):
            with patch('privacy.util.conf.conf.NlpEngineProvider') as mock_provider:
                with patch('privacy.util.conf.conf.RecognizerRegistry') as mock_registry:
                    with patch('privacy.util.conf.conf.AnalyzerEngine') as mock_analyzer:
                        mock_nlp_engine = MagicMock()
                        mock_provider_instance = MagicMock()
                        mock_provider_instance.create_engine.return_value = mock_nlp_engine
                        mock_provider.return_value = mock_provider_instance
                        
                        mock_registry_instance = MagicMock()
                        mock_registry.return_value = mock_registry_instance
                        
                        mock_analyzer_instance = MagicMock()
                        mock_analyzer.return_value = mock_analyzer_instance
                        
                        analyzer, registry = conf.get_analyzer_engine("SPACY_MODEL")
                        
                        # Verify NlpEngineProvider was called with correct configuration
                        call_args = mock_provider.call_args
                        assert call_args is not None
                        nlp_config = call_args[1]['nlp_configuration']
                        assert nlp_config['nlp_engine_name'] == 'spacy'
                        assert len(nlp_config['models']) == 1
    
    def test_get_analyzer_engine_returns_tuple(self):
        """Test that get_analyzer_engine returns a tuple of (analyzer, registry)."""
        conf = ConfModel()
        
        model_config = {
            "lang_code": "en",
            "model_name": "en_core_web_sm"
        }
        
        with patch.dict(os.environ, {"MODEL_ENV": json.dumps(model_config)}):
            with patch('privacy.util.conf.conf.NlpEngineProvider') as mock_provider:
                with patch('privacy.util.conf.conf.RecognizerRegistry') as mock_registry:
                    with patch('privacy.util.conf.conf.AnalyzerEngine') as mock_analyzer:
                        mock_nlp_engine = MagicMock()
                        mock_provider_instance = MagicMock()
                        mock_provider_instance.create_engine.return_value = mock_nlp_engine
                        mock_provider.return_value = mock_provider_instance
                        
                        mock_registry_instance = MagicMock()
                        mock_registry.return_value = mock_registry_instance
                        
                        mock_analyzer_instance = MagicMock()
                        mock_analyzer.return_value = mock_analyzer_instance
                        
                        result = conf.get_analyzer_engine("MODEL_ENV")
                        
                        # Verify it's a tuple with 2 elements
                        assert isinstance(result, tuple)
                        assert len(result) == 2
    
    def test_get_analyzer_engine_nlp_engine_creation(self):
        """Test that NLP engine is created correctly."""
        conf = ConfModel()
        
        model_config = {
            "lang_code": "fr",
            "model_name": "fr_core_news_sm"
        }
        
        with patch.dict(os.environ, {"FR_MODEL": json.dumps(model_config)}):
            with patch('privacy.util.conf.conf.NlpEngineProvider') as mock_provider:
                with patch('privacy.util.conf.conf.RecognizerRegistry'):
                    with patch('privacy.util.conf.conf.AnalyzerEngine'):
                        mock_nlp_engine = MagicMock()
                        mock_provider_instance = MagicMock()
                        mock_provider_instance.create_engine.return_value = mock_nlp_engine
                        mock_provider.return_value = mock_provider_instance
                        
                        conf.get_analyzer_engine("FR_MODEL")
                        
                        # Verify create_engine was called
                        assert mock_provider_instance.create_engine.called
    
    def test_get_analyzer_engine_registry_creation(self):
        """Test that RecognizerRegistry is created."""
        conf = ConfModel()
        
        model_config = {
            "lang_code": "en",
            "model_name": "en_core_web_sm"
        }
        
        with patch.dict(os.environ, {"REGISTRY_TEST": json.dumps(model_config)}):
            with patch('privacy.util.conf.conf.NlpEngineProvider') as mock_provider:
                with patch('privacy.util.conf.conf.RecognizerRegistry') as mock_registry:
                    with patch('privacy.util.conf.conf.AnalyzerEngine'):
                        mock_nlp_engine = MagicMock()
                        mock_provider_instance = MagicMock()
                        mock_provider_instance.create_engine.return_value = mock_nlp_engine
                        mock_provider.return_value = mock_provider_instance
                        
                        conf.get_analyzer_engine("REGISTRY_TEST")
                        
                        # Verify RecognizerRegistry was instantiated
                        assert mock_registry.called
    
    def test_get_analyzer_engine_analyzer_with_registry_and_nlp(self):
        """Test that AnalyzerEngine is created with registry and NLP engine."""
        conf = ConfModel()
        
        model_config = {
            "lang_code": "en",
            "model_name": "en_core_web_sm"
        }
        
        with patch.dict(os.environ, {"ANALYZER_TEST": json.dumps(model_config)}):
            with patch('privacy.util.conf.conf.NlpEngineProvider') as mock_provider:
                with patch('privacy.util.conf.conf.RecognizerRegistry') as mock_registry:
                    with patch('privacy.util.conf.conf.AnalyzerEngine') as mock_analyzer:
                        mock_nlp_engine = MagicMock()
                        mock_provider_instance = MagicMock()
                        mock_provider_instance.create_engine.return_value = mock_nlp_engine
                        mock_provider.return_value = mock_provider_instance
                        
                        mock_registry_instance = MagicMock()
                        mock_registry.return_value = mock_registry_instance
                        
                        conf.get_analyzer_engine("ANALYZER_TEST")
                        
                        # Verify AnalyzerEngine was called with correct arguments
                        mock_analyzer.assert_called_once_with(
                            registry=mock_registry_instance,
                            nlp_engine=mock_nlp_engine
                        )
    
    def test_get_analyzer_engine_with_complex_model_config(self):
        """Test with more complex model configuration."""
        conf = ConfModel()
        
        model_config = {
            "lang_code": "en",
            "model_name": "en_core_web_trf",
            "additional_param": "value"
        }
        
        with patch.dict(os.environ, {"COMPLEX_MODEL": json.dumps(model_config)}):
            with patch('privacy.util.conf.conf.NlpEngineProvider') as mock_provider:
                with patch('privacy.util.conf.conf.RecognizerRegistry'):
                    with patch('privacy.util.conf.conf.AnalyzerEngine'):
                        mock_nlp_engine = MagicMock()
                        mock_provider_instance = MagicMock()
                        mock_provider_instance.create_engine.return_value = mock_nlp_engine
                        mock_provider.return_value = mock_provider_instance
                        
                        analyzer, registry = conf.get_analyzer_engine("COMPLEX_MODEL")
                        
                        # Verify the method completed successfully
                        assert analyzer is not None
                        assert registry is not None
    
    def test_get_analyzer_engine_json_parsing(self):
        """Test that JSON is properly parsed from environment variable."""
        conf = ConfModel()
        
        model_config = {
            "lang_code": "de",
            "model_name": "de_core_news_sm"
        }
        json_string = json.dumps(model_config)
        
        with patch.dict(os.environ, {"JSON_TEST": json_string}):
            with patch('privacy.util.conf.conf.NlpEngineProvider') as mock_provider:
                with patch('privacy.util.conf.conf.RecognizerRegistry'):
                    with patch('privacy.util.conf.conf.AnalyzerEngine'):
                        mock_nlp_engine = MagicMock()
                        mock_provider_instance = MagicMock()
                        mock_provider_instance.create_engine.return_value = mock_nlp_engine
                        mock_provider.return_value = mock_provider_instance
                        
                        with patch('privacy.util.conf.conf.os.getenv') as mock_getenv:
                            mock_getenv.return_value = json_string
                            
                            conf.get_analyzer_engine("JSON_TEST")
                            
                            # Verify getenv was called with correct key
                            mock_getenv.assert_called_once_with("JSON_TEST")
    
    def test_get_analyzer_engine_configuration_structure(self):
        """Test the internal configuration structure."""
        conf = ConfModel()
        
        model_config = {
            "lang_code": "es",
            "model_name": "es_core_news_sm"
        }
        
        with patch.dict(os.environ, {"CONFIG_STRUCT": json.dumps(model_config)}):
            with patch('privacy.util.conf.conf.NlpEngineProvider') as mock_provider:
                with patch('privacy.util.conf.conf.RecognizerRegistry'):
                    with patch('privacy.util.conf.conf.AnalyzerEngine'):
                        mock_nlp_engine = MagicMock()
                        mock_provider_instance = MagicMock()
                        mock_provider_instance.create_engine.return_value = mock_nlp_engine
                        mock_provider.return_value = mock_provider_instance
                        
                        conf.get_analyzer_engine("CONFIG_STRUCT")
                        
                        # Get the configuration passed to NlpEngineProvider
                        call_args = mock_provider.call_args
                        config = call_args[1]['nlp_configuration']
                        
                        # Verify configuration structure
                        assert 'nlp_engine_name' in config
                        assert config['nlp_engine_name'] == 'spacy'
                        assert 'models' in config
                        assert isinstance(config['models'], list)


class TestConfModelEdgeCases:
    """Test edge cases and error scenarios."""
    
    def test_get_analyzer_engine_with_minimal_config(self):
        """Test with minimal model configuration."""
        conf = ConfModel()
        
        model_config = {"lang_code": "en"}
        
        with patch.dict(os.environ, {"MINIMAL": json.dumps(model_config)}):
            with patch('privacy.util.conf.conf.NlpEngineProvider') as mock_provider:
                with patch('privacy.util.conf.conf.RecognizerRegistry'):
                    with patch('privacy.util.conf.conf.AnalyzerEngine'):
                        mock_nlp_engine = MagicMock()
                        mock_provider_instance = MagicMock()
                        mock_provider_instance.create_engine.return_value = mock_nlp_engine
                        mock_provider.return_value = mock_provider_instance
                        
                        analyzer, registry = conf.get_analyzer_engine("MINIMAL")
                        
                        assert analyzer is not None
                        assert registry is not None
    
    def test_get_analyzer_engine_multiple_calls(self):
        """Test calling get_analyzer_engine multiple times."""
        conf = ConfModel()
        
        model_config = {
            "lang_code": "en",
            "model_name": "en_core_web_sm"
        }
        
        with patch.dict(os.environ, {"MULTI_CALL": json.dumps(model_config)}):
            with patch('privacy.util.conf.conf.NlpEngineProvider') as mock_provider:
                with patch('privacy.util.conf.conf.RecognizerRegistry') as mock_registry:
                    with patch('privacy.util.conf.conf.AnalyzerEngine') as mock_analyzer:
                        mock_nlp_engine = MagicMock()
                        mock_provider_instance = MagicMock()
                        mock_provider_instance.create_engine.return_value = mock_nlp_engine
                        mock_provider.return_value = mock_provider_instance
                        
                        mock_registry_instance = MagicMock()
                        mock_registry.return_value = mock_registry_instance
                        
                        mock_analyzer_instance = MagicMock()
                        mock_analyzer.return_value = mock_analyzer_instance
                        
                        # Call multiple times
                        result1 = conf.get_analyzer_engine("MULTI_CALL")
                        result2 = conf.get_analyzer_engine("MULTI_CALL")
                        
                        # Both should succeed
                        assert result1 is not None
                        assert result2 is not None
    
    def test_confmodel_instantiation(self):
        """Test that ConfModel can be instantiated."""
        conf = ConfModel()
        assert conf is not None
        assert hasattr(conf, 'get_analyzer_engine')
