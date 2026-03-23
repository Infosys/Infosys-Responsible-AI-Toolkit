"""
Comprehensive tests for Ollama model client integration
Tests Ollama API interactions for local model inference
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock, Mock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from image_explain.utils.model.ollama import Ollama


class TestOllamaGenerate:
    """Test suite for Ollama generate method"""
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_generate_with_image(self, mock_ollama_chat):
        """Test generate method with image"""
        mock_response = {
            'message': {
                'content': 'This is a test response'
            }
        }
        mock_ollama_chat.return_value = mock_response
        
        result = Ollama.generate(
            model_name='llama',
            prompt='Analyze this image',
            image_url='/path/to/image.jpg'
        )
        
        assert result == 'This is a test response'
        mock_ollama_chat.assert_called_once()
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_generate_without_image(self, mock_ollama_chat):
        """Test generate method without image"""
        mock_response = {
            'message': {
                'content': 'Text only response'
            }
        }
        mock_ollama_chat.return_value = mock_response
        
        result = Ollama.generate(
            model_name='llama',
            prompt='Describe this scene',
            image_url=None
        )
        
        assert result == 'Text only response'
        mock_ollama_chat.assert_called_once()
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_generate_with_llama_model(self, mock_ollama_chat):
        """Test generate with llama model"""
        mock_response = {
            'message': {
                'content': 'Llama response'
            }
        }
        mock_ollama_chat.return_value = mock_response
        
        result = Ollama.generate(
            model_name='llama3.2-vision',
            prompt='Test prompt',
            image_url='/path/to/image.jpg'
        )
        
        assert result == 'Llama response'
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_generate_model_name_normalization(self, mock_ollama_chat):
        """Test that model name is normalized to llama3.2-vision"""
        mock_response = {
            'message': {
                'content': 'Response'
            }
        }
        mock_ollama_chat.return_value = mock_response
        
        # Test with lowercase 'llama'
        Ollama.generate(
            model_name='llama',
            prompt='Test',
            image_url=None
        )
        
        # Should call with 'llama3.2-vision'
        call_args = mock_ollama_chat.call_args
        assert call_args[1]['model'] == 'llama3.2-vision'
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_generate_message_structure_with_image(self, mock_ollama_chat):
        """Test message structure when image is provided"""
        mock_response = {
            'message': {
                'content': 'Response'
            }
        }
        mock_ollama_chat.return_value = mock_response
        
        image_path = '/path/to/image.jpg'
        Ollama.generate(
            model_name='llama',
            prompt='Analyze',
            image_url=image_path
        )
        
        # Verify message structure
        call_args = mock_ollama_chat.call_args
        messages = call_args[1]['messages']
        
        assert len(messages) == 1
        assert messages[0]['role'] == 'user'
        assert messages[0]['content'] == 'Analyze'
        assert 'images' in messages[0]
        assert messages[0]['images'] == [image_path]
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_generate_message_structure_without_image(self, mock_ollama_chat):
        """Test message structure when no image is provided"""
        mock_response = {
            'message': {
                'content': 'Response'
            }
        }
        mock_ollama_chat.return_value = mock_response
        
        Ollama.generate(
            model_name='llama',
            prompt='Text only',
            image_url=None
        )
        
        # Verify message structure
        call_args = mock_ollama_chat.call_args
        messages = call_args[1]['messages']
        
        assert len(messages) == 1
        assert messages[0]['role'] == 'user'
        assert messages[0]['content'] == 'Text only'
        assert 'images' not in messages[0]
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_generate_temperature_parameter(self, mock_ollama_chat):
        """Test that temperature parameter is set correctly"""
        mock_response = {
            'message': {
                'content': 'Response'
            }
        }
        mock_ollama_chat.return_value = mock_response
        
        Ollama.generate(
            model_name='llama',
            prompt='Test',
            image_url=None
        )
        
        # Verify temperature is set to 0.2
        call_args = mock_ollama_chat.call_args
        assert call_args[1]['options']['temperature'] == 0.2


class TestOllamaModelNames:
    """Test suite for Ollama model name handling"""
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_model_name_with_lowercase_llama(self, mock_ollama_chat):
        """Test with lowercase 'llama' in model name"""
        mock_response = {'message': {'content': 'Response'}}
        mock_ollama_chat.return_value = mock_response
        
        Ollama.generate(
            model_name='llama',
            prompt='Test',
            image_url=None
        )
        
        call_model = mock_ollama_chat.call_args[1]['model']
        assert call_model == 'llama3.2-vision'
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_model_name_with_uppercase_llama(self, mock_ollama_chat):
        """Test with uppercase 'LLAMA' in model name"""
        mock_response = {'message': {'content': 'Response'}}
        mock_ollama_chat.return_value = mock_response
        
        Ollama.generate(
            model_name='LLAMA',
            prompt='Test',
            image_url=None
        )
        
        call_model = mock_ollama_chat.call_args[1]['model']
        assert call_model == 'llama3.2-vision'
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_model_name_with_mixed_case_llama(self, mock_ollama_chat):
        """Test with mixed case 'Llama' in model name"""
        mock_response = {'message': {'content': 'Response'}}
        mock_ollama_chat.return_value = mock_response
        
        Ollama.generate(
            model_name='Llama3.2',
            prompt='Test',
            image_url=None
        )
        
        call_model = mock_ollama_chat.call_args[1]['model']
        assert call_model == 'llama3.2-vision'
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_model_name_without_llama(self, mock_ollama_chat):
        """Test with model name that doesn't contain 'llama'"""
        mock_response = {'message': {'content': 'Response'}}
        mock_ollama_chat.return_value = mock_response
        
        Ollama.generate(
            model_name='mistral',
            prompt='Test',
            image_url=None
        )
        
        call_model = mock_ollama_chat.call_args[1]['model']
        # Should pass through as-is
        assert call_model == 'mistral'


class TestOllamaResponseHandling:
    """Test suite for Ollama response handling"""
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_extract_content_from_response(self, mock_ollama_chat):
        """Test extracting content from API response"""
        expected_content = 'This is the generated content'
        mock_response = {
            'message': {
                'content': expected_content
            }
        }
        mock_ollama_chat.return_value = mock_response
        
        result = Ollama.generate(
            model_name='llama',
            prompt='Test',
            image_url=None
        )
        
        assert result == expected_content
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_response_with_multiline_content(self, mock_ollama_chat):
        """Test response with multiline content"""
        multiline_content = """Line 1
Line 2
Line 3
Line 4"""
        mock_response = {
            'message': {
                'content': multiline_content
            }
        }
        mock_ollama_chat.return_value = mock_response
        
        result = Ollama.generate(
            model_name='llama',
            prompt='Test',
            image_url=None
        )
        
        assert result == multiline_content
        assert '\n' in result
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_response_with_special_characters(self, mock_ollama_chat):
        """Test response with special characters"""
        special_content = 'Response with !@#$%^&*() special chars'
        mock_response = {
            'message': {
                'content': special_content
            }
        }
        mock_ollama_chat.return_value = mock_response
        
        result = Ollama.generate(
            model_name='llama',
            prompt='Test',
            image_url=None
        )
        
        assert result == special_content


class TestOllamaErrorHandling:
    """Test suite for Ollama error handling"""
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_generate_api_error(self, mock_ollama_chat):
        """Test handling of API errors"""
        mock_ollama_chat.side_effect = Exception('Connection refused')
        
        with pytest.raises(Exception):
            Ollama.generate(
                model_name='llama',
                prompt='Test',
                image_url=None
            )
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_generate_with_missing_message_field(self, mock_ollama_chat):
        """Test handling when response missing message field"""
        mock_response = {
            'error': 'Some error'
            # Missing 'message' field
        }
        mock_ollama_chat.return_value = mock_response
        
        # Should raise KeyError
        with pytest.raises(KeyError):
            Ollama.generate(
                model_name='llama',
                prompt='Test',
                image_url=None
            )
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_generate_with_missing_content_field(self, mock_ollama_chat):
        """Test handling when response missing content field"""
        mock_response = {
            'message': {
                # Missing 'content' field
            }
        }
        mock_ollama_chat.return_value = mock_response
        
        # Should raise KeyError
        with pytest.raises(KeyError):
            Ollama.generate(
                model_name='llama',
                prompt='Test',
                image_url=None
            )


class TestOllamaIntegration:
    """Integration tests for Ollama client"""
    
    def test_ollama_class_exists(self):
        """Test that Ollama class can be imported"""
        from image_explain.utils.model.ollama import Ollama
        assert Ollama is not None
    
    def test_ollama_has_generate_method(self):
        """Test that Ollama has generate method"""
        from image_explain.utils.model.ollama import Ollama
        assert hasattr(Ollama, 'generate')
        assert callable(Ollama.generate)
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_generate_is_static_method(self, mock_ollama_chat):
        """Test that generate can be called without instance"""
        mock_response = {'message': {'content': 'Response'}}
        mock_ollama_chat.return_value = mock_response
        
        # Should be callable without instantiating
        result = Ollama.generate(
            model_name='llama',
            prompt='Test',
            image_url=None
        )
        
        assert result is not None


class TestOllamaImageHandling:
    """Test suite for image handling in Ollama"""
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_image_url_passed_correctly(self, mock_ollama_chat):
        """Test that image URL is passed correctly"""
        mock_response = {'message': {'content': 'Response'}}
        mock_ollama_chat.return_value = mock_response
        
        image_path = '/home/user/images/test.jpg'
        Ollama.generate(
            model_name='llama',
            prompt='Analyze',
            image_url=image_path
        )
        
        call_args = mock_ollama_chat.call_args
        messages = call_args[1]['messages']
        assert messages[0]['images'][0] == image_path
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_image_url_as_list(self, mock_ollama_chat):
        """Test that image URL is wrapped in list"""
        mock_response = {'message': {'content': 'Response'}}
        mock_ollama_chat.return_value = mock_response
        
        image_path = '/path/to/image.jpg'
        Ollama.generate(
            model_name='llama',
            prompt='Test',
            image_url=image_path
        )
        
        call_args = mock_ollama_chat.call_args
        messages = call_args[1]['messages']
        
        # images should be a list
        assert isinstance(messages[0]['images'], list)
        assert len(messages[0]['images']) == 1
        assert messages[0]['images'][0] == image_path
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_empty_image_url_excluded(self, mock_ollama_chat):
        """Test that empty image URL is excluded from message"""
        mock_response = {'message': {'content': 'Response'}}
        mock_ollama_chat.return_value = mock_response
        
        Ollama.generate(
            model_name='llama',
            prompt='Test',
            image_url=None
        )
        
        call_args = mock_ollama_chat.call_args
        messages = call_args[1]['messages']
        
        # Should not have images key
        assert 'images' not in messages[0]
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_empty_string_image_url_excluded(self, mock_ollama_chat):
        """Test that empty string image URL is excluded from message"""
        mock_response = {'message': {'content': 'Response'}}
        mock_ollama_chat.return_value = mock_response
        
        Ollama.generate(
            model_name='llama',
            prompt='Test',
            image_url=''
        )
        
        call_args = mock_ollama_chat.call_args
        messages = call_args[1]['messages']
        
        # Should not have images key
        assert 'images' not in messages[0]


class TestOllamaPrompts:
    """Test suite for prompt handling in Ollama"""
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_prompt_passed_correctly(self, mock_ollama_chat):
        """Test that prompt is passed correctly"""
        mock_response = {'message': {'content': 'Response'}}
        mock_ollama_chat.return_value = mock_response
        
        prompt_text = 'Analyze this image for bias'
        Ollama.generate(
            model_name='llama',
            prompt=prompt_text,
            image_url=None
        )
        
        call_args = mock_ollama_chat.call_args
        messages = call_args[1]['messages']
        assert messages[0]['content'] == prompt_text
    
    @patch('image_explain.utils.model.ollama.ollama.chat')
    def test_multiline_prompt(self, mock_ollama_chat):
        """Test with multiline prompt"""
        mock_response = {'message': {'content': 'Response'}}
        mock_ollama_chat.return_value = mock_response
        
        multiline_prompt = """Analyze this image:
1. Objects present
2. Colors used
3. Overall composition"""
        
        Ollama.generate(
            model_name='llama',
            prompt=multiline_prompt,
            image_url=None
        )
        
        call_args = mock_ollama_chat.call_args
        messages = call_args[1]['messages']
        assert messages[0]['content'] == multiline_prompt
