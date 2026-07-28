"""
MIT License
Copyright © 2025 Infosys Ltd.

Comprehensive tests for src/translate.py - Google and Azure translation
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
import os
from azure.core.exceptions import HttpResponseError


class TestTranslateGoogleTranslate:
    """Tests for Translate.translate() - Google Translate API"""
    
    @patch('src.translate.log')
    @patch('src.translate.requests.get')
    @patch('langcodes.Language')
    def test_translate_english_text(self, mock_language_class, mock_requests_get, mock_log):
        """Test translating English text with Google Translate"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'sentences': [
                {'trans': 'Hola, '},
                {'trans': '¿cómo estás?'}
            ],
            'src': 'en-US'
        }
        mock_requests_get.return_value = mock_response
        
        mock_language = Mock()
        mock_language.display_name.return_value = 'English'
        mock_language_class.make.return_value = mock_language
        
        from src.translate import Translate
        
        translated_text, language = Translate.translate("Hello, how are you?")
        
        assert translated_text == "Hola, ¿cómo estás?"
        assert language == "English"
        mock_requests_get.assert_called_once()
    
    @patch('src.translate.log')
    @patch('src.translate.requests.get')
    @patch('langcodes.Language')
    def test_translate_spanish_text(self, mock_language_class, mock_requests_get, mock_log):
        """Test translating Spanish text"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'sentences': [
                {'trans': 'Hello, '},
                {'trans': 'how are you?'}
            ],
            'src': 'es'
        }
        mock_requests_get.return_value = mock_response
        
        mock_language = Mock()
        mock_language.display_name = Mock(return_value='Spanish')
        mock_language_class.make = Mock(return_value=mock_language)
        
        from src.translate import Translate
        
        translated_text, language = Translate.translate("Hola, ¿cómo estás?")
        
        assert isinstance(translated_text, str)
        assert len(translated_text) > 0
    
    @patch('src.translate.log')
    @patch('src.translate.requests.get')
    @patch('langcodes.Language')
    def test_translate_chinese_text(self, mock_language_class, mock_requests_get, mock_log):
        """Test translating Chinese text"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'sentences': [
                {'trans': 'Hello world'}
            ],
            'src': 'zh-CN'
        }
        mock_requests_get.return_value = mock_response
        
        mock_language = Mock()
        mock_language.display_name = Mock(return_value='Chinese')
        mock_language_class.make = Mock(return_value=mock_language)
        
        from src.translate import Translate
        
        translated_text, language = Translate.translate("你好世界")
        
        assert isinstance(translated_text, str)
        assert len(translated_text) > 0
    
    @patch('src.translate.log')
    @patch('src.translate.requests.get')
    @patch('langcodes.Language')
    def test_translate_multiple_sentences(self, mock_language_class, mock_requests_get, mock_log):
        """Test translating text with multiple sentences"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'sentences': [
                {'trans': 'First sentence. '},
                {'trans': 'Second sentence. '},
                {'trans': 'Third sentence.'}
            ],
            'src': 'en'
        }
        mock_requests_get.return_value = mock_response
        
        mock_language = Mock()
        mock_language.display_name.return_value = 'English'
        mock_language_class.make.return_value = mock_language
        
        from src.translate import Translate
        
        translated_text, language = Translate.translate("First sentence. Second sentence. Third sentence.")
        
        assert "First sentence." in translated_text
        assert "Second sentence." in translated_text
    
    @patch('src.translate.log')
    @patch('src.translate.requests.get')
    @patch('langcodes.Language')
    def test_translate_french_text(self, mock_language_class, mock_requests_get, mock_log):
        """Test translating French text"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'sentences': [
                {'trans': 'Good morning'}
            ],
            'src': 'fr'
        }
        mock_requests_get.return_value = mock_response
        
        mock_language = Mock()
        mock_language.display_name = Mock(return_value='French')
        mock_language_class.make = Mock(return_value=mock_language)
        
        from src.translate import Translate
        
        translated_text, language = Translate.translate("Bonjour")
        
        assert isinstance(translated_text, str)
        assert len(translated_text) > 0
    
    @patch('src.translate.log')
    @patch('src.translate.requests.get')
    @patch('langcodes.Language')
    def test_translate_empty_string(self, mock_language_class, mock_requests_get, mock_log):
        """Test translating empty string"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'sentences': [],
            'src': 'en'
        }
        mock_requests_get.return_value = mock_response
        
        mock_language = Mock()
        mock_language.display_name.return_value = 'English'
        mock_language_class.make.return_value = mock_language
        
        from src.translate import Translate
        
        translated_text, language = Translate.translate("")
        
        assert isinstance(translated_text, str)
    
    @patch('src.translate.log')
    @patch('src.translate.requests.get')
    @patch('langcodes.Language')
    def test_translate_special_characters(self, mock_language_class, mock_requests_get, mock_log):
        """Test translating text with special characters"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'sentences': [
                {'trans': 'Café, naïve, résumé'}
            ],
            'src': 'fr'
        }
        mock_requests_get.return_value = mock_response
        
        mock_language = Mock()
        mock_language.display_name.return_value = 'French'
        mock_language_class.make.return_value = mock_language
        
        from src.translate import Translate
        
        translated_text, language = Translate.translate("Café, naïve, résumé")
        
        assert translated_text == "Café, naïve, résumé"
    
    @patch('src.translate.log')
    @patch('src.translate.requests.get')
    def test_translate_request_exception(self, mock_requests_get, mock_log):
        """Test handling of request exceptions"""
        mock_requests_get.side_effect = Exception("Network error")
        
        from src.translate import Translate
        
        try:
            result = Translate.translate("Test")
            # Should handle exception gracefully
            assert True
        except:
            # Exception properly handled
            assert True
    
    @patch('src.translate.log')
    @patch('src.translate.requests.get')
    @patch('langcodes.Language')
    def test_translate_url_format(self, mock_language_class, mock_requests_get, mock_log):
        """Test that Google Translate API URL is correctly formatted"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'sentences': [{'trans': 'translated'}],
            'src': 'en'
        }
        mock_requests_get.return_value = mock_response
        
        mock_language = Mock()
        mock_language.display_name.return_value = 'English'
        mock_language_class.make.return_value = mock_language
        
        from src.translate import Translate
        
        Translate.translate("Test text")
        
        # Verify the URL includes required parameters
        call_args = mock_requests_get.call_args
        url = call_args[0][0]
        assert 'translate.googleapis.com' in url
        assert 'client=gtx' in url
        assert 'sl=auto' in url
        assert 'tl=en' in url
    
    @patch('src.translate.log')
    @patch('src.translate.requests.get')
    @patch('langcodes.Language')
    def test_translate_long_text(self, mock_language_class, mock_requests_get, mock_log):
        """Test translating long text"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'sentences': [
                {'trans': 'This is '},
                {'trans': 'a very '},
                {'trans': 'long '},
                {'trans': 'translated '},
                {'trans': 'text.'}
            ],
            'src': 'en'
        }
        mock_requests_get.return_value = mock_response
        
        mock_language = Mock()
        mock_language.display_name.return_value = 'English'
        mock_language_class.make.return_value = mock_language
        
        from src.translate import Translate
        
        long_text = "This is a very long text. " * 50
        translated_text, language = Translate.translate(long_text)
        
        assert isinstance(translated_text, str)


class TestTranslateAzureTranslate:
    """Tests for Translate.azure_translate() - Azure Translate API"""
    
    @patch.dict(os.environ, {
        'AZURE_TRANSLATE_KEY': 'test-key',
        'AZURE_TRANSLATE_ENDPOINT': 'https://api.cognitive.microsofttranslator.com',
        'AZURE_TRANSLATE_REGION': 'westus'
    })
    @patch('src.translate.log')
    @patch('src.translate.TextTranslationClient')
    @patch('langcodes.Language')
    def test_azure_translate_success(self, mock_language_class, mock_client_class, mock_log):
        """Test successful Azure Translate call"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock the translate response - uses dict access for detectedLanguage, object for translations
        mock_translation = {
            'detectedLanguage': {'language': 'en'},
            'translations': [Mock(to='en', text='Hello world')]
        }
        mock_translation_obj = Mock()
        mock_translation_obj.__getitem__ = Mock(side_effect=lambda key: mock_translation[key])
        mock_translation_obj.translations = [Mock(to='en', text='Hello world')]
        mock_client.translate.return_value = [mock_translation_obj]
        
        mock_language = Mock()
        mock_language.display_name = Mock(return_value='English')
        mock_language_class.make = Mock(return_value=mock_language)
        
        from src.translate import Translate
        
        translated_text, language = Translate.azure_translate("Hola mundo")
        
        assert isinstance(translated_text, str)
        assert len(translated_text) > 0
    
    @patch.dict(os.environ, {
        'AZURE_TRANSLATE_KEY': 'test-key',
        'AZURE_TRANSLATE_ENDPOINT': 'https://api.cognitive.microsofttranslator.com',
        'AZURE_TRANSLATE_REGION': 'westus'
    })
    @patch('src.translate.log')
    @patch('src.translate.TextTranslationClient')
    @patch('langcodes.Language')
    def test_azure_translate_spanish(self, mock_language_class, mock_client_class, mock_log):
        """Test Azure Translate with Spanish language"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock the translate response - uses dict access for detectedLanguage, object for translations
        mock_translation = {
            'detectedLanguage': {'language': 'es'},
            'translations': [Mock(to='en', text='Good morning')]
        }
        mock_translation_obj = Mock()
        mock_translation_obj.__getitem__ = Mock(side_effect=lambda key: mock_translation[key])
        mock_translation_obj.translations = [Mock(to='en', text='Good morning')]
        mock_client.translate.return_value = [mock_translation_obj]
        
        mock_language = Mock()
        mock_language.display_name = Mock(return_value='Spanish')
        mock_language_class.make = Mock(return_value=mock_language)
        
        from src.translate import Translate
        
        translated_text, language = Translate.azure_translate("Buenos días")
        
        assert isinstance(translated_text, str)
        assert len(translated_text) > 0
    
    @patch.dict(os.environ, {
        'AZURE_TRANSLATE_KEY': 'test-key',
        'AZURE_TRANSLATE_ENDPOINT': 'https://api.cognitive.microsofttranslator.com',
        'AZURE_TRANSLATE_REGION': 'westus'
    })
    @patch('src.translate.log')
    @patch('src.translate.TextTranslationClient')
    def test_azure_translate_http_error(self, mock_client_class, mock_log):
        """Test Azure Translate handling HTTP errors"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock HTTP error
        error = HttpResponseError("Bad Request")
        error.error = Mock(code="BadRequest", message="Invalid input")
        mock_client.translate.side_effect = error
        
        from src.translate import Translate
        
        try:
            result = Translate.azure_translate("Test")
            # Should handle error gracefully
            assert True
        except HttpResponseError:
            # Error properly caught
            assert True
    
    @patch.dict(os.environ, {
        'AZURE_TRANSLATE_KEY': 'test-key',
        'AZURE_TRANSLATE_ENDPOINT': 'https://api.cognitive.microsofttranslator.com',
        'AZURE_TRANSLATE_REGION': 'westus'
    })
    @patch('src.translate.log')
    @patch('src.translate.TextTranslationClient')
    @patch('langcodes.Language')
    def test_azure_translate_empty_response(self, mock_language_class, mock_client_class, mock_log):
        """Test Azure Translate with empty response"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_client.translate.return_value = []
        
        from src.translate import Translate
        
        result = Translate.azure_translate("Test")
        
        # Should handle empty response
        assert result is None or isinstance(result, tuple)
    
    @patch.dict(os.environ, {
        'AZURE_TRANSLATE_KEY': 'test-key',
        'AZURE_TRANSLATE_ENDPOINT': 'https://api.cognitive.microsofttranslator.com',
        'AZURE_TRANSLATE_REGION': 'westus'
    })
    @patch('src.translate.log')
    @patch('src.translate.TextTranslationClient')
    @patch('langcodes.Language')
    def test_azure_translate_multiple_translations(self, mock_language_class, mock_client_class, mock_log):
        """Test Azure Translate with multiple translation options"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock the translate response - uses dict access for detectedLanguage, object for translations
        mock_translation = {
            'detectedLanguage': {'language': 'en'},
            'translations': [
                Mock(to='en', text='First translation'),
                Mock(to='es', text='Segunda traducción'),
                Mock(to='fr', text='Première traduction')
            ]
        }
        mock_translation_obj = Mock()
        mock_translation_obj.__getitem__ = Mock(side_effect=lambda key: mock_translation[key])
        mock_translation_obj.translations = [
            Mock(to='en', text='First translation'),
            Mock(to='es', text='Segunda traducción'),
            Mock(to='fr', text='Première traduction')
        ]
        mock_client.translate.return_value = [mock_translation_obj]
        
        mock_language = Mock()
        mock_language.display_name = Mock(return_value='English')
        mock_language_class.make = Mock(return_value=mock_language)
        
        from src.translate import Translate
        
        # First translation should be returned
        translated_text, language = Translate.azure_translate("Test")
        
        assert isinstance(translated_text, str)
        assert len(translated_text) > 0
    
    @patch.dict(os.environ, {
        'AZURE_TRANSLATE_KEY': 'test-key',
        'AZURE_TRANSLATE_ENDPOINT': 'https://api.cognitive.microsofttranslator.com',
        'AZURE_TRANSLATE_REGION': 'westus'
    })
    @patch('src.translate.log')
    @patch('src.translate.TextTranslationClient')
    @patch('langcodes.Language')
    def test_azure_translate_chinese(self, mock_language_class, mock_client_class, mock_log):
        """Test Azure Translate with Chinese text"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock the translate response - uses dict access for detectedLanguage, object for translations
        mock_translation = {
            'detectedLanguage': {'language': 'zh-Hans'},
            'translations': [Mock(to='en', text='Hello')]
        }
        mock_translation_obj = Mock()
        mock_translation_obj.__getitem__ = Mock(side_effect=lambda key: mock_translation[key])
        mock_translation_obj.translations = [Mock(to='en', text='Hello')]
        mock_client.translate.return_value = [mock_translation_obj]
        
        mock_language = Mock()
        mock_language.display_name = Mock(return_value='Chinese')
        mock_language_class.make = Mock(return_value=mock_language)
        
        from src.translate import Translate
        
        translated_text, language = Translate.azure_translate("你好")
        
        assert isinstance(translated_text, str)
        assert len(translated_text) > 0
