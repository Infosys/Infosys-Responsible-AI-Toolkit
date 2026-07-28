"""
Extended test coverage for azure.py - Gemini class and utility methods
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock, Mock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from image_explain.utils.model.azure import Gemini, Azure


class TestGeminiInitialization:
    """Test Gemini class initialization"""
    
    @patch.dict(os.environ, {
        'GEMINI_API_KEY': 'test-key-123',
        'GEMINI_MODELNAME': 'gemini-pro-vision'
    })
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_gemini_initialization_with_env_vars(self, mock_configure):
        """Test Gemini initialization with environment variables"""
        gemini = Gemini()
        
        assert gemini.api_key == 'test-key-123'
        assert gemini.gemini_modelname == 'gemini-pro-vision'
        mock_configure.assert_called_once_with(api_key='test-key-123')
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'api-key', 'GEMINI_MODELNAME': 'gemini-pro'})
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_gemini_api_key_set(self, mock_configure):
        """Test that Gemini API key is properly set"""
        gemini = Gemini()
        
        assert gemini.api_key == 'api-key'
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key', 'GEMINI_MODELNAME': 'model'})
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_gemini_model_name_set(self, mock_configure):
        """Test that Gemini model name is properly set"""
        gemini = Gemini()
        
        assert gemini.gemini_modelname == 'model'
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_gemini_initialization_missing_api_key(self, mock_configure):
        """Test Gemini initialization when API key is missing"""
        gemini = Gemini()
        
        assert gemini.api_key is None
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key'}, clear=True)
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_gemini_initialization_missing_model_name(self, mock_configure):
        """Test Gemini initialization when model name is missing"""
        gemini = Gemini()
        
        assert gemini.gemini_modelname is None


class TestCleanExplanationString:
    """Test clean_explanation_string method"""
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key', 'GEMINI_MODELNAME': 'model'})
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_clean_explanation_empty_string(self, mock_configure):
        """Test cleaning empty explanation string"""
        gemini = Gemini()
        
        result = gemini.clean_explanation_string("")
        
        assert result == ""
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key', 'GEMINI_MODELNAME': 'model'})
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_clean_explanation_with_response_prefix(self, mock_configure):
        """Test cleaning explanation with Response: prefix"""
        gemini = Gemini()
        
        result = gemini.clean_explanation_string("Response: {'key': 'value'}")
        
        assert result == "{'key': 'value'}"
        assert "Response:" not in result
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key', 'GEMINI_MODELNAME': 'model'})
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_clean_explanation_with_json_markdown_wrapper(self, mock_configure):
        """Test cleaning explanation with ```json ``` wrapper"""
        gemini = Gemini()
        text = '```json{"key": "value"}```'
        
        result = gemini.clean_explanation_string(text)
        
        assert result == '{"key": "value"}'
        assert "```json" not in result
        assert "```" not in result
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key', 'GEMINI_MODELNAME': 'model'})
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_clean_explanation_with_multiple_markdown_wrappers(self, mock_configure):
        """Test cleaning explanation with multiple markdown wrappers"""
        gemini = Gemini()
        text = '```json{"key1": "value1"}``` some text ```{"key2": "value2"}```'
        
        result = gemini.clean_explanation_string(text)
        
        assert "```json" not in result
        assert "```" not in result
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key', 'GEMINI_MODELNAME': 'model'})
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_clean_explanation_response_prefix_with_markdown(self, mock_configure):
        """Test cleaning explanation with Response: prefix and markdown"""
        gemini = Gemini()
        text = 'Response: ```json{"data": "test"}```'
        
        result = gemini.clean_explanation_string(text)
        
        assert result == '{"data": "test"}'
        assert "Response:" not in result
        assert "```" not in result
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key', 'GEMINI_MODELNAME': 'model'})
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_clean_explanation_with_whitespace(self, mock_configure):
        """Test cleaning explanation with extra whitespace"""
        gemini = Gemini()
        text = '  \n  Response:  \n  {"key": "value"}  \n  '
        
        result = gemini.clean_explanation_string(text)
        
        assert result == '{"key": "value"}'
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key', 'GEMINI_MODELNAME': 'model'})
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_clean_explanation_none_input(self, mock_configure):
        """Test cleaning with None input"""
        gemini = Gemini()
        
        result = gemini.clean_explanation_string(None)
        
        assert result == ""
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key', 'GEMINI_MODELNAME': 'model'})
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_clean_explanation_complex_json(self, mock_configure):
        """Test cleaning complex JSON object"""
        gemini = Gemini()
        json_str = '{"nested": {"key": "value"}, "array": [1, 2, 3]}'
        text = f'Response: ```json{json_str}```'
        
        result = gemini.clean_explanation_string(text)
        
        assert result == json_str
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key', 'GEMINI_MODELNAME': 'model'})
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_clean_explanation_plain_text(self, mock_configure):
        """Test cleaning plain text without markdown"""
        gemini = Gemini()
        text = "Just plain text"
        
        result = gemini.clean_explanation_string(text)
        
        assert result == "Just plain text"


class TestGeminiGenerate:
    """Test Gemini generate method"""
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key', 'GEMINI_MODELNAME': 'gemini-pro-vision'})
    @patch('image_explain.utils.model.azure.genai.GenerativeModel')
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_generate_with_image(self, mock_configure, mock_model_class):
        """Test generate method with image"""
        # Setup mocks
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '```json{"result": "success"}```'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        gemini = Gemini()
        result = gemini.generate(
            'gemini-pro-vision',
            'Analyze this image',
            'image/jpeg',
            'base64_image_data'
        )
        
        assert result == '{"result": "success"}'
        mock_model.generate_content.assert_called_once()
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key', 'GEMINI_MODELNAME': 'gemini-pro-vision'})
    @patch('image_explain.utils.model.azure.genai.GenerativeModel')
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_generate_without_image(self, mock_configure, mock_model_class):
        """Test generate method without image"""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = 'Response: ```json{"text": "only"}```'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        gemini = Gemini()
        result = gemini.generate(
            'gemini-pro-vision',
            'Answer this question',
            None,
            None
        )
        
        assert result == '{"text": "only"}'
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key', 'GEMINI_MODELNAME': 'gemini-pro-vision'})
    @patch('image_explain.utils.model.azure.genai.GenerativeModel')
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_generate_creates_model_with_correct_name(self, mock_configure, mock_model_class):
        """Test that generate creates model with correct model name"""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = 'test'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        gemini = Gemini()
        gemini.generate('gemini-pro-vision', 'prompt', None, None)
        
        mock_model_class.assert_called_once_with('gemini-pro-vision')
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key', 'GEMINI_MODELNAME': 'gemini-pro-vision'})
    @patch('image_explain.utils.model.azure.genai.GenerativeModel')
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_generate_with_different_mime_types(self, mock_configure, mock_model_class):
        """Test generate with different image MIME types"""
        mime_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        
        for mime_type in mime_types:
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = 'result'
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            gemini = Gemini()
            result = gemini.generate('gemini-pro-vision', 'prompt', mime_type, 'base64')
            
            # Verify image_part was created with correct MIME type
            call_args = mock_model.generate_content.call_args[0][0]
            image_part = call_args[1]
            assert image_part['mime_type'] == mime_type
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key', 'GEMINI_MODELNAME': 'gemini-pro-vision'})
    @patch('image_explain.utils.model.azure.genai.GenerativeModel')
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_generate_with_empty_prompt(self, mock_configure, mock_model_class):
        """Test generate with empty prompt"""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = ''
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        gemini = Gemini()
        result = gemini.generate('gemini-pro-vision', '', None, None)
        
        assert result == ''
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key', 'GEMINI_MODELNAME': 'gemini-pro-vision'})
    @patch('image_explain.utils.model.azure.genai.GenerativeModel')
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_generate_response_cleaning(self, mock_configure, mock_model_class):
        """Test that generate response is properly cleaned"""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '  Response: ```json{"cleaned": true}```  '
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        gemini = Gemini()
        result = gemini.generate('gemini-pro-vision', 'prompt', None, None)
        
        assert result == '{"cleaned": true}'
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key', 'GEMINI_MODELNAME': 'gemini-pro-vision'})
    @patch('image_explain.utils.model.azure.genai.GenerativeModel')
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_generate_with_base64_image_data(self, mock_configure, mock_model_class):
        """Test generate with base64 image data"""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = 'result'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        base64_data = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        gemini = Gemini()
        result = gemini.generate('gemini-pro-vision', 'prompt', 'image/png', base64_data)
        
        # Verify base64 data was passed correctly
        call_args = mock_model.generate_content.call_args[0][0]
        image_part = call_args[1]
        assert image_part['data'] == base64_data
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key', 'GEMINI_MODELNAME': 'gemini-pro-vision'})
    @patch('image_explain.utils.model.azure.genai.GenerativeModel')
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_generate_handles_multiline_response(self, mock_configure, mock_model_class):
        """Test generate with multiline response"""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '''Response: ```json
        {
            "key": "value",
            "nested": {
                "inner": "data"
            }
        }
        ```'''
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        gemini = Gemini()
        result = gemini.generate('gemini-pro-vision', 'prompt', None, None)
        
        # Should have JSON extracted and cleaned
        assert '"key": "value"' in result or '"key":"value"' in result


class TestAzureGeminiIntegration:
    """Integration tests for Gemini functionality"""
    
    @patch.dict(os.environ, {
        'GEMINI_API_KEY': 'test-key',
        'GEMINI_MODELNAME': 'gemini-pro-vision'
    })
    @patch('image_explain.utils.model.azure.genai.GenerativeModel')
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_gemini_full_workflow_with_image(self, mock_configure, mock_model_class):
        """Test complete Gemini workflow with image"""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = 'Response: ```json{"analysis": "complete"}```'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        gemini = Gemini()
        
        result = gemini.generate(
            'gemini-pro-vision',
            'Analyze this image',
            'image/jpeg',
            'base64_encoded_image'
        )
        
        assert isinstance(result, str)
        assert '{"analysis": "complete"}' in result or '"analysis"' in result
    
    @patch.dict(os.environ, {
        'GEMINI_API_KEY': 'test-key',
        'GEMINI_MODELNAME': 'gemini-pro'
    })
    @patch('image_explain.utils.model.azure.genai.GenerativeModel')
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_gemini_full_workflow_text_only(self, mock_configure, mock_model_class):
        """Test complete Gemini workflow with text only"""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"response": "text only"}'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        gemini = Gemini()
        
        result = gemini.generate(
            'gemini-pro',
            'Answer this question',
            None,
            None
        )
        
        assert isinstance(result, str)
        assert 'response' in result or 'text only' in result


class TestGeminiEdgeCases:
    """Test edge cases for Gemini class"""
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key', 'GEMINI_MODELNAME': 'model'})
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_clean_explanation_with_newlines_in_json(self, mock_configure):
        """Test cleaning JSON with newlines"""
        gemini = Gemini()
        json_with_newlines = '{"key": "value",\n"key2": "value2"}'
        
        result = gemini.clean_explanation_string(json_with_newlines)
        
        assert 'key' in result
        assert 'value' in result
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key', 'GEMINI_MODELNAME': 'model'})
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_clean_explanation_response_case_sensitivity(self, mock_configure):
        """Test that Response: prefix is case sensitive"""
        gemini = Gemini()
        text = 'response: this should not be removed'
        
        result = gemini.clean_explanation_string(text)
        
        # Lowercase 'response:' should not be removed
        assert 'response:' in result.lower()
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'key', 'GEMINI_MODELNAME': 'model'})
    @patch('image_explain.utils.model.azure.genai.configure')
    def test_clean_explanation_special_characters(self, mock_configure):
        """Test cleaning with special characters in JSON"""
        gemini = Gemini()
        text = '```json{"special": "!@#$%^&*()"}```'
        
        result = gemini.clean_explanation_string(text)
        
        assert 'special' in result
        assert '!@#$%^&*()' in result or '!@' in result


