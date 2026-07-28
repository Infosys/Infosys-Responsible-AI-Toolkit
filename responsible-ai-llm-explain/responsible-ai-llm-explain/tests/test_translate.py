import sys
import os
import pytest
from unittest.mock import patch, MagicMock, Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from llm_explain.utility.translate import Translate


@pytest.mark.unit
class TestTranslateGoogleBasic:
    """Test basic Google Translate functionality"""
    
    def test_translate_basic(self):
        """Test basic translation"""
        with patch('llm_explain.utility.translate.requests.get') as mock_get:
            with patch('llm_explain.utility.translate.Language') as mock_language_class:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'sentences': [
                        {'trans': 'Bonjour'},
                        {'trans': ' le monde'}
                    ],
                    'src': 'fr-FR'
                }
                mock_get.return_value = mock_response
                
                mock_lang = MagicMock()
                mock_lang.display_name.return_value = "French"
                mock_language_class.make.return_value = mock_lang
                
                result = Translate.translate("Hello world")
                
                assert result[0] == "Bonjour le monde"
                assert result[1] == "French"
    
    def test_translate_spanish(self):
        """Test translation from Spanish"""
        with patch('llm_explain.utility.translate.requests.get') as mock_get:
            with patch('llm_explain.utility.translate.Language') as mock_language_class:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'sentences': [
                        {'trans': 'Hello'},
                        {'trans': ' world'}
                    ],
                    'src': 'es-ES'
                }
                mock_get.return_value = mock_response
                
                mock_lang = MagicMock()
                mock_lang.display_name.return_value = "Spanish"
                mock_language_class.make.return_value = mock_lang
                
                result = Translate.translate("Hola mundo")
                
                assert result[0] == "Hello world"
                assert result[1] == "Spanish"
    
    def test_translate_german(self):
        """Test translation from German"""
        with patch('llm_explain.utility.translate.requests.get') as mock_get:
            with patch('llm_explain.utility.translate.Language') as mock_language_class:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'sentences': [
                        {'trans': 'Hello'},
                        {'trans': ' world'}
                    ],
                    'src': 'de-DE'
                }
                mock_get.return_value = mock_response
                
                mock_lang = MagicMock()
                mock_lang.display_name.return_value = "German"
                mock_language_class.make.return_value = mock_lang
                
                result = Translate.translate("Hallo Welt")
                
                assert result[0] == "Hello world"
                assert result[1] == "German"
    
    def test_translate_single_sentence(self):
        """Test translation of single sentence"""
        with patch('llm_explain.utility.translate.requests.get') as mock_get:
            with patch('llm_explain.utility.translate.Language') as mock_language_class:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'sentences': [
                        {'trans': 'Single sentence'}
                    ],
                    'src': 'en-US'
                }
                mock_get.return_value = mock_response
                
                mock_lang = MagicMock()
                mock_lang.display_name.return_value = "English"
                mock_language_class.make.return_value = mock_lang
                
                result = Translate.translate("Phrase simple")
                
                assert result[0] == "Single sentence"
    
    def test_translate_empty_input(self):
        """Test translation of empty string"""
        with patch('llm_explain.utility.translate.requests.get') as mock_get:
            with patch('llm_explain.utility.translate.Language') as mock_language_class:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'sentences': [],
                    'src': 'auto'
                }
                mock_get.return_value = mock_response
                
                mock_lang = MagicMock()
                mock_lang.display_name.return_value = "Unknown"
                mock_language_class.make.return_value = mock_lang
                
                result = Translate.translate("")
                
                assert result[0] == ""


@pytest.mark.unit
class TestTranslateErrorHandling:
    """Test error handling in translate functions"""
    
    def test_translate_request_error(self):
        """Test handling of request error"""
        with patch('llm_explain.utility.translate.requests.get') as mock_get:
            with patch('llm_explain.utility.translate.log') as mock_log:
                mock_get.side_effect = Exception("Network error")
                
                result = Translate.translate("Test")
                
                mock_log.error.assert_called()
                # Should return None or handle gracefully
                assert result is None or result == (None, None)
    
    def test_translate_url_construction(self):
        """Test that correct URL is constructed"""
        with patch('llm_explain.utility.translate.requests.get') as mock_get:
            with patch('llm_explain.utility.translate.Language') as mock_language_class:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'sentences': [{'trans': 'translated'}],
                    'src': 'en-US'
                }
                mock_get.return_value = mock_response
                
                mock_lang = MagicMock()
                mock_lang.display_name.return_value = "English"
                mock_language_class.make.return_value = mock_lang
                
                text = "hello"
                Translate.translate(text)
                
                # Verify the URL was constructed correctly
                called_url = mock_get.call_args[0][0]
                assert "translate_a/single" in called_url
                assert "client=gtx" in called_url
                assert "sl=auto" in called_url
                assert "tl=en" in called_url
                assert text in called_url


@pytest.mark.unit
class TestAzureTranslate:
    """Test Azure Translation service"""
    
    def test_azure_translate_basic(self):
        """Test basic Azure translation"""
        os.environ["AZURE_TRANSLATE_KEY"] = "fake_key"
        os.environ["AZURE_TRANSLATE_ENDPOINT"] = "https://fake.endpoint"
        os.environ["AZURE_TRANSLATE_REGION"] = "fake_region"
        
        with patch('llm_explain.utility.translate.TextTranslationClient') as mock_client_class:
            with patch('llm_explain.utility.translate.TranslatorCredential') as mock_cred:
                with patch('llm_explain.utility.translate.Language') as mock_language_class:
                    mock_client = MagicMock()
                    mock_client_class.return_value = mock_client
                    
                    # Create a proper mock translation object
                    mock_translated_text = MagicMock()
                    mock_translated_text.text = 'Hello world'
                    
                    mock_translation = MagicMock()
                    mock_translation.__getitem__ = lambda self, key: {
                        'detectedLanguage': {'language': 'fr'},
                        'translations': None
                    }[key]
                    mock_translation.translations = [mock_translated_text]
                    
                    mock_client.translate.return_value = [mock_translation]
                    
                    mock_lang = MagicMock()
                    mock_lang.display_name.return_value = "French"
                    mock_language_class.make.return_value = mock_lang
                    
                    result = Translate.azure_translate("Bonjour le monde")
                    
                    assert result[0] == 'Hello world'
                    assert result[1] == "French"
    
    def test_azure_translate_empty_response(self):
        """Test Azure translation with empty response"""
        os.environ["AZURE_TRANSLATE_KEY"] = "fake_key"
        os.environ["AZURE_TRANSLATE_ENDPOINT"] = "https://fake.endpoint"
        os.environ["AZURE_TRANSLATE_REGION"] = "fake_region"
        
        with patch('llm_explain.utility.translate.TextTranslationClient') as mock_client_class:
            with patch('llm_explain.utility.translate.TranslatorCredential'):
                mock_client = MagicMock()
                mock_client_class.return_value = mock_client
                mock_client.translate.return_value = []
                
                result = Translate.azure_translate("Test")
                
                assert result is None
    
    def test_azure_translate_http_error(self):
        """Test Azure translation with HTTP error"""
        os.environ["AZURE_TRANSLATE_KEY"] = "fake_key"
        os.environ["AZURE_TRANSLATE_ENDPOINT"] = "https://fake.endpoint"
        os.environ["AZURE_TRANSLATE_REGION"] = "fake_region"
        
        from azure.core.exceptions import HttpResponseError
        
        with patch('llm_explain.utility.translate.TextTranslationClient') as mock_client_class:
            with patch('llm_explain.utility.translate.TranslatorCredential'):
                with patch('llm_explain.utility.translate.log') as mock_log:
                    mock_client = MagicMock()
                    mock_client_class.return_value = mock_client
                    
                    error = HttpResponseError("API Error")
                    error.error = MagicMock(code="400", message="Bad Request")
                    mock_client.translate.side_effect = error
                    
                    result = Translate.azure_translate("Test")
                    
                    mock_log.error.assert_called()
    
    def test_azure_translate_multiple_languages(self):
        """Test Azure translation with multiple target languages"""
        os.environ["AZURE_TRANSLATE_KEY"] = "fake_key"
        os.environ["AZURE_TRANSLATE_ENDPOINT"] = "https://fake.endpoint"
        os.environ["AZURE_TRANSLATE_REGION"] = "fake_region"
        
        with patch('llm_explain.utility.translate.TextTranslationClient') as mock_client_class:
            with patch('llm_explain.utility.translate.TranslatorCredential'):
                with patch('llm_explain.utility.translate.Language') as mock_language_class:
                    mock_client = MagicMock()
                    mock_client_class.return_value = mock_client
                    
                    # Create a proper mock translation object
                    mock_translated_text = MagicMock()
                    mock_translated_text.text = 'Hello'
                    
                    mock_translation = MagicMock()
                    mock_translation.__getitem__ = lambda self, key: {
                        'detectedLanguage': {'language': 'es'},
                        'translations': None
                    }[key]
                    mock_translation.translations = [mock_translated_text]
                    
                    mock_client.translate.return_value = [mock_translation]
                    
                    mock_lang = MagicMock()
                    mock_lang.display_name.return_value = "Spanish"
                    mock_language_class.make.return_value = mock_lang
                    
                    result = Translate.azure_translate("Hola")
                    
                    assert result[0] == 'Hello'
                    assert result[1] == "Spanish"
    
    def test_azure_translate_chinese(self):
        """Test Azure translation for Chinese text"""
        os.environ["AZURE_TRANSLATE_KEY"] = "fake_key"
        os.environ["AZURE_TRANSLATE_ENDPOINT"] = "https://fake.endpoint"
        os.environ["AZURE_TRANSLATE_REGION"] = "fake_region"
        
        with patch('llm_explain.utility.translate.TextTranslationClient') as mock_client_class:
            with patch('llm_explain.utility.translate.TranslatorCredential'):
                with patch('llm_explain.utility.translate.Language') as mock_language_class:
                    mock_client = MagicMock()
                    mock_client_class.return_value = mock_client
                    
                    # Create a proper mock translation object
                    mock_translated_text = MagicMock()
                    mock_translated_text.text = 'Hello'
                    
                    mock_translation = MagicMock()
                    mock_translation.__getitem__ = lambda self, key: {
                        'detectedLanguage': {'language': 'zh'},
                        'translations': None
                    }[key]
                    mock_translation.translations = [mock_translated_text]
                    
                    mock_client.translate.return_value = [mock_translation]
                    
                    mock_lang = MagicMock()
                    mock_lang.display_name.return_value = "Chinese"
                    mock_language_class.make.return_value = mock_lang
                    
                    result = Translate.azure_translate("你好")
                    
                    assert result[0] == 'Hello'
                    assert result[1] == "Chinese"

@pytest.mark.unit
class TestTranslateLanguageDetection:
    """Test language detection in translate functions"""
    
    def test_translate_language_code_parsing(self):
        """Test language code parsing"""
        with patch('llm_explain.utility.translate.requests.get') as mock_get:
            with patch('llm_explain.utility.translate.Language') as mock_language_class:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'sentences': [{'trans': 'Test'}],
                    'src': 'fr-FR'
                }
                mock_get.return_value = mock_response
                
                mock_lang = MagicMock()
                mock_lang.display_name.return_value = "French"
                mock_language_class.make.return_value = mock_lang
                
                translated, lang = Translate.translate("Test")
                
                # Should extract 'fr' from 'fr-FR'
                assert lang is not None
    
    def test_translate_multiple_language_pairs(self):
        """Test multiple language pair detections"""
        test_cases = [
            ('en-US', 'English'),
            ('es-ES', 'Spanish'),
            ('de-DE', 'German'),
            ('fr-FR', 'French'),
            ('it-IT', 'Italian'),
        ]
        
        for lang_code, expected_lang in test_cases:
            with patch('llm_explain.utility.translate.requests.get') as mock_get:
                with patch('llm_explain.utility.translate.Language') as mock_language_class:
                    mock_response = MagicMock()
                    mock_response.json.return_value = {
                        'sentences': [{'trans': 'Test'}],
                        'src': lang_code
                    }
                    mock_get.return_value = mock_response
                    
                    mock_lang = MagicMock()
                    mock_lang.display_name.return_value = expected_lang
                    mock_language_class.make.return_value = mock_lang
                    
                    translated, detected_lang = Translate.translate("Test")
                    
                    # Language should be detected
                    assert detected_lang is not None


@pytest.mark.unit
class TestTranslateInputVariations:
    """Test translate with various input types"""
    
    def test_translate_with_numbers(self):
        """Test translation of text with numbers"""
        with patch('llm_explain.utility.translate.requests.get') as mock_get:
            with patch('llm_explain.utility.translate.Language') as mock_language_class:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'sentences': [{'trans': 'Test 123'}],
                    'src': 'en-US'
                }
                mock_get.return_value = mock_response
                
                mock_lang = MagicMock()
                mock_lang.display_name.return_value = "English"
                mock_language_class.make.return_value = mock_lang
                
                result = Translate.translate("Test 123")
                
                assert result[0] is not None
    
    def test_translate_with_punctuation(self):
        """Test translation of text with punctuation"""
        with patch('llm_explain.utility.translate.requests.get') as mock_get:
            with patch('llm_explain.utility.translate.Language') as mock_language_class:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'sentences': [{'trans': 'Hello, world!'}],
                    'src': 'en-US'
                }
                mock_get.return_value = mock_response
                
                mock_lang = MagicMock()
                mock_lang.display_name.return_value = "English"
                mock_language_class.make.return_value = mock_lang
                
                result = Translate.translate("Hello, world!")
                
                assert result[0] is not None
    
    def test_translate_with_special_characters(self):
        """Test translation of text with special characters"""
        with patch('llm_explain.utility.translate.requests.get') as mock_get:
            with patch('llm_explain.utility.translate.Language') as mock_language_class:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'sentences': [{'trans': 'Test @#$%'}],
                    'src': 'en-US'
                }
                mock_get.return_value = mock_response
                
                mock_lang = MagicMock()
                mock_lang.display_name.return_value = "English"
                mock_language_class.make.return_value = mock_lang
                
                result = Translate.translate("Test @#$%")
                
                assert result[0] is not None
    
    def test_translate_with_unicode(self):
        """Test translation of text with unicode characters"""
        with patch('llm_explain.utility.translate.requests.get') as mock_get:
            with patch('llm_explain.utility.translate.Language') as mock_language_class:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'sentences': [{'trans': 'Test 你好'}],
                    'src': 'zh-CN'
                }
                mock_get.return_value = mock_response
                
                mock_lang = MagicMock()
                mock_lang.display_name.return_value = "Chinese"
                mock_language_class.make.return_value = mock_lang
                
                result = Translate.translate("Test 你好")
                
                assert result[0] is not None


@pytest.mark.unit
class TestTranslateEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_translate_very_long_text(self):
        """Test translation of very long text"""
        with patch('llm_explain.utility.translate.requests.get') as mock_get:
            with patch('llm_explain.utility.translate.Language') as mock_language_class:
                long_text = "Test " * 1000
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    'sentences': [{'trans': long_text}],
                    'src': 'en-US'
                }
                mock_get.return_value = mock_response
                
                mock_lang = MagicMock()
                mock_lang.display_name.return_value = "English"
                mock_language_class.make.return_value = mock_lang
                
                result = Translate.translate(long_text)
                
                assert result is not None
    
    def test_translate_json_decode_error(self):
        """Test handling of JSON decode error"""
        with patch('llm_explain.utility.translate.requests.get') as mock_get:
            with patch('llm_explain.utility.translate.log') as mock_log:
                mock_response = MagicMock()
                mock_response.json.side_effect = ValueError("Invalid JSON")
                mock_get.return_value = mock_response
                
                result = Translate.translate("Test")
                
                # Should handle error gracefully
                assert result is None or isinstance(result, tuple)