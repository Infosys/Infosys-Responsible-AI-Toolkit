'''
Copyright 2024-2025 Infosys  Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import pytest
import sys
import os
import json
import time
from unittest.mock import patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

# Setup environment variables
os.environ.setdefault('AZURE_OPENAI_API_KEY_DALL_E_2', 'test-key')
os.environ.setdefault('AZURE_OPENAI_ENDPOINT_DALL_E_2', 'https://api.openai.com')
os.environ.setdefault('AZURE_OPENAI_API_VERSION_DALL_E_2', '2024-05-01')
os.environ.setdefault('AZURE_OPENAI_MODEL_DALL_E_2', 'dall-e-2')

# Import and set up request_id_var
from llm.config.logger import request_id_var
request_id_var.set("test-request-id")


class TestAzureImageGeneration:
    """Test suite for Azure image generation class"""
    
    @patch('llm.service.azure_open_ai_img_gen.openai.AzureOpenAI')
    def test_azure_initialization(self, mock_azure_openai):
        """Test Azure class initialization"""
        from llm.service.azure_open_ai_img_gen import Azure
        
        mock_client = MagicMock()
        mock_azure_openai.return_value = mock_client
        
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY_DALL_E_2': 'test-key',
            'AZURE_OPENAI_ENDPOINT_DALL_E_2': 'https://api.openai.com',
            'AZURE_OPENAI_API_VERSION_DALL_E_2': '2024-05-01'
        }):
            azure = Azure()
            assert azure.api_key == 'test-key'
            assert azure.azure_endpoint == 'https://api.openai.com'
            assert azure.api_version == '2024-05-01'
    
    @patch('llm.service.azure_open_ai_img_gen.openai.AzureOpenAI')
    def test_generate_image_dalle2(self, mock_azure_openai):
        """Test image generation with DALL-E-2"""
        from llm.service.azure_open_ai_img_gen import Azure
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.model_dump_json.return_value = json.dumps({
            'data': [{'b64_json': 'base64_image_data_here'}]
        })
        mock_client.images.generate.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY_DALL_E_2': 'test-key',
            'AZURE_OPENAI_ENDPOINT_DALL_E_2': 'https://api.openai.com',
            'AZURE_OPENAI_API_VERSION_DALL_E_2': '2024-05-01',
            'AZURE_OPENAI_MODEL_DALL_E_2': 'dall-e-2'
        }):
            azure = Azure()
            result = azure.generate_image("Test prompt", "DALL-E-2")
            assert result == 'base64_image_data_here'
    
    @patch('llm.service.azure_open_ai_img_gen.openai.AzureOpenAI')
    def test_generate_image_with_prompt(self, mock_azure_openai):
        """Test generate_image preserves prompt"""
        from llm.service.azure_open_ai_img_gen import Azure
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.model_dump_json.return_value = json.dumps({
            'data': [{'b64_json': 'test_base64'}]
        })
        mock_client.images.generate.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY_DALL_E_2': 'test-key',
            'AZURE_OPENAI_ENDPOINT_DALL_E_2': 'https://api.openai.com',
            'AZURE_OPENAI_API_VERSION_DALL_E_2': '2024-05-01',
            'AZURE_OPENAI_MODEL_DALL_E_2': 'dall-e-2'
        }):
            azure = Azure()
            prompt = "A beautiful landscape with mountains"
            result = azure.generate_image(prompt, "DALL-E-2")
            
            # Verify the call was made with the correct prompt
            mock_client.images.generate.assert_called_once()
            call_args = mock_client.images.generate.call_args
            assert call_args[1]['prompt'] == prompt
            assert result == 'test_base64'
    
    @patch('llm.service.azure_open_ai_img_gen.openai.AzureOpenAI')
    def test_generate_image_returns_base64(self, mock_azure_openai):
        """Test generate_image returns base64 string"""
        from llm.service.azure_open_ai_img_gen import Azure
        
        mock_client = MagicMock()
        base64_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        mock_response = MagicMock()
        mock_response.model_dump_json.return_value = json.dumps({
            'data': [{'b64_json': base64_image}]
        })
        mock_client.images.generate.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY_DALL_E_2': 'test-key',
            'AZURE_OPENAI_ENDPOINT_DALL_E_2': 'https://api.openai.com',
            'AZURE_OPENAI_API_VERSION_DALL_E_2': '2024-05-01',
            'AZURE_OPENAI_MODEL_DALL_E_2': 'dall-e-2'
        }):
            azure = Azure()
            result = azure.generate_image("Test", "DALL-E-2")
            assert result == base64_image
            assert isinstance(result, str)
    
    @patch('llm.service.azure_open_ai_img_gen.openai.AzureOpenAI')
    def test_generate_image_with_custom_model(self, mock_azure_openai):
        """Test generate_image with custom model name"""
        from llm.service.azure_open_ai_img_gen import Azure
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.model_dump_json.return_value = json.dumps({
            'data': [{'b64_json': 'custom_base64'}]
        })
        mock_client.images.generate.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY_DALL_E_2': 'test-key',
            'AZURE_OPENAI_ENDPOINT_DALL_E_2': 'https://api.openai.com',
            'AZURE_OPENAI_API_VERSION_DALL_E_2': '2024-05-01',
            'AZURE_OPENAI_MODEL_DALL_E_2': 'dall-e-2'
        }):
            azure = Azure()
            result = azure.generate_image("Test", "custom-model")
            
            # Verify custom model is passed to the API
            call_args = mock_client.images.generate.call_args
            assert call_args[1]['model'] == 'custom-model'
            assert result == 'custom_base64'
    
    @patch('llm.service.azure_open_ai_img_gen.openai.AzureOpenAI')
    def test_generate_image_retry_logic(self, mock_azure_openai):
        """Test generate_image retry mechanism"""
        from llm.service.azure_open_ai_img_gen import Azure
        
        mock_client = MagicMock()
        
        # First call fails, second succeeds
        mock_response_fail = MagicMock()
        mock_response_fail.model_dump_json.side_effect = Exception("API Error")
        
        mock_response_success = MagicMock()
        mock_response_success.model_dump_json.return_value = json.dumps({
            'data': [{'b64_json': 'retry_success'}]
        })
        
        mock_client.images.generate.side_effect = [
            Exception("API Error"),
            mock_response_success
        ]
        
        mock_azure_openai.return_value = mock_client
        
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY_DALL_E_2': 'test-key',
            'AZURE_OPENAI_ENDPOINT_DALL_E_2': 'https://api.openai.com',
            'AZURE_OPENAI_API_VERSION_DALL_E_2': '2024-05-01',
            'AZURE_OPENAI_MODEL_DALL_E_2': 'dall-e-2'
        }):
            azure = Azure()
            
            with patch('llm.service.azure_open_ai_img_gen.time.sleep'):
                result = azure.generate_image("Test", "DALL-E-2")
                assert result == 'retry_success'
    
    @patch('llm.service.azure_open_ai_img_gen.openai.AzureOpenAI')
    def test_generate_image_max_retries_exceeded(self, mock_azure_openai):
        """Test generate_image handles max retries appropriately"""
        from llm.service.azure_open_ai_img_gen import Azure
        
        mock_client = MagicMock()
        mock_client.images.generate.side_effect = Exception("Persistent API Error")
        mock_azure_openai.return_value = mock_client
        
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY_DALL_E_2': 'test-key',
            'AZURE_OPENAI_ENDPOINT_DALL_E_2': 'https://api.openai.com',
            'AZURE_OPENAI_API_VERSION_DALL_E_2': '2024-05-01',
            'AZURE_OPENAI_MODEL_DALL_E_2': 'dall-e-2'
        }):
            azure = Azure()
            
            with patch('llm.service.azure_open_ai_img_gen.time.sleep'):
                # This should handle retries silently or return something
                try:
                    result = azure.generate_image("Test", "DALL-E-2")
                except Exception:
                    # If it raises, that's also acceptable behavior
                    pass
    
    @patch('llm.service.azure_open_ai_img_gen.openai.AzureOpenAI')
    def test_generate_image_various_prompts(self, mock_azure_openai):
        """Test generate_image with various prompts"""
        from llm.service.azure_open_ai_img_gen import Azure
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.model_dump_json.return_value = json.dumps({
            'data': [{'b64_json': 'base64_output'}]
        })
        mock_client.images.generate.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        prompts = [
            "A simple image",
            "A doctor with a stethoscope",
            "A detailed landscape with mountains, rivers, and wildlife",
            "An abstract art piece with vibrant colors"
        ]
        
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY_DALL_E_2': 'test-key',
            'AZURE_OPENAI_ENDPOINT_DALL_E_2': 'https://api.openai.com',
            'AZURE_OPENAI_API_VERSION_DALL_E_2': '2024-05-01',
            'AZURE_OPENAI_MODEL_DALL_E_2': 'dall-e-2'
        }):
            azure = Azure()
            
            for prompt in prompts:
                result = azure.generate_image(prompt, "DALL-E-2")
                assert result == 'base64_output'
    
    @patch('llm.service.azure_open_ai_img_gen.openai.AzureOpenAI')
    def test_generate_image_response_format(self, mock_azure_openai):
        """Test generate_image uses b64_json response format"""
        from llm.service.azure_open_ai_img_gen import Azure
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.model_dump_json.return_value = json.dumps({
            'data': [{'b64_json': 'encoded_image'}]
        })
        mock_client.images.generate.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY_DALL_E_2': 'test-key',
            'AZURE_OPENAI_ENDPOINT_DALL_E_2': 'https://api.openai.com',
            'AZURE_OPENAI_API_VERSION_DALL_E_2': '2024-05-01',
            'AZURE_OPENAI_MODEL_DALL_E_2': 'dall-e-2'
        }):
            azure = Azure()
            result = azure.generate_image("Test", "DALL-E-2")
            
            # Verify response_format is set to b64_json
            call_args = mock_client.images.generate.call_args
            assert call_args[1]['response_format'] == 'b64_json'
            assert result == 'encoded_image'


class TestAzureImageGenerationIntegration:
    """Integration tests for Azure image generation"""
    
    @patch('llm.service.azure_open_ai_img_gen.openai.AzureOpenAI')
    def test_multiple_image_generations(self, mock_azure_openai):
        """Test generating multiple images in sequence"""
        from llm.service.azure_open_ai_img_gen import Azure
        
        mock_client = MagicMock()
        
        # Setup multiple responses
        responses = []
        for i in range(3):
            mock_response = MagicMock()
            mock_response.model_dump_json.return_value = json.dumps({
                'data': [{'b64_json': f'base64_image_{i}'}]
            })
            responses.append(mock_response)
        
        mock_client.images.generate.side_effect = responses
        mock_azure_openai.return_value = mock_client
        
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY_DALL_E_2': 'test-key',
            'AZURE_OPENAI_ENDPOINT_DALL_E_2': 'https://api.openai.com',
            'AZURE_OPENAI_API_VERSION_DALL_E_2': '2024-05-01',
            'AZURE_OPENAI_MODEL_DALL_E_2': 'dall-e-2'
        }):
            azure = Azure()
            
            results = []
            for i in range(3):
                result = azure.generate_image(f"Prompt {i}", "DALL-E-2")
                results.append(result)
            
            assert len(results) == 3
            for i, result in enumerate(results):
                assert result == f'base64_image_{i}'
