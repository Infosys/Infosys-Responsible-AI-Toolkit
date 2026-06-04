'''
Copyright 2024-2025 Infosys Ltd.

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
from unittest.mock import patch, MagicMock, Mock
from fastapi.testclient import TestClient

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from llm.mapper.mapper import OpenAiRequest, ImageGenerationRequest, ImageGenerationResponse


class TestLLMService:
    """Test suite for LLMService class"""
    
    @patch('llm.service.service.Azure')
    def test_generate_image_valid_payload(self, mock_azure):
        """Test generate_image with valid payload"""
        from llm.service.service import LLMService
        
        mock_instance = MagicMock()
        mock_instance.generate_image.return_value = "base64_image_data"
        mock_azure.return_value = mock_instance
        
        payload = ImageGenerationRequest(
            prompt="Test prompt",
            model="DALL-E-2"
        )
        
        result = LLMService.generate_image(payload)
        assert isinstance(result, ImageGenerationResponse)
        assert result.image == "base64_image_data"
    
    @patch('llm.service.service.Azure')
    def test_generate_image_empty_prompt(self, mock_azure):
        """Test generate_image with empty prompt raises exception"""
        from llm.service.service import LLMService
        
        payload = ImageGenerationRequest(
            prompt="",
            model="DALL-E-2"
        )
        
        with pytest.raises(Exception) as exc_info:
            LLMService.generate_image(payload)
        assert "Prompt is required" in str(exc_info.value)
    
    @patch('llm.service.service.Azure')
    def test_generate_image_with_valid_prompts(self, mock_azure):
        """Test generate_image with various valid prompts"""
        from llm.service.service import LLMService
        
        mock_instance = MagicMock()
        mock_instance.generate_image.return_value = "base64_image_data"
        mock_azure.return_value = mock_instance
        
        prompts = [
            "A simple image",
            "A doctor with stethoscope",
            "A landscape"
        ]
        
        for prompt in prompts:
            payload = ImageGenerationRequest(
                prompt=prompt,
                model="DALL-E-2"
            )
            result = LLMService.generate_image(payload)
            assert isinstance(result, ImageGenerationResponse)
    
    @patch('llm.service.service.Azure')
    def test_generate_image_azure_error_handling(self, mock_azure):
        """Test generate_image handles Azure errors"""
        from llm.service.service import LLMService
        
        mock_instance = MagicMock()
        mock_instance.generate_image.side_effect = Exception("Azure API error")
        mock_azure.return_value = mock_instance
        
        payload = ImageGenerationRequest(
            prompt="Test prompt",
            model="DALL-E-2"
        )
        
        with pytest.raises(Exception) as exc_info:
            LLMService.generate_image(payload)
        assert "Azure API error" in str(exc_info.value)
    
    @patch('llm.service.service.Azure')
    def test_generate_image_with_different_models(self, mock_azure):
        """Test generate_image with different model names"""
        from llm.service.service import LLMService
        
        mock_instance = MagicMock()
        mock_instance.generate_image.return_value = "base64_image"
        mock_azure.return_value = mock_instance
        
        models = ["DALL-E-2", "DALL-E-3", "custom-model"]
        for model in models:
            payload = ImageGenerationRequest(
                prompt="Test",
                model=model
            )
            result = LLMService.generate_image(payload)
            assert isinstance(result, ImageGenerationResponse)
    
    @patch('llm.service.service.Azure')
    def test_generate_image_with_detailed_prompts(self, mock_azure):
        """Test generate_image with various detailed prompts"""
        from llm.service.service import LLMService
        
        mock_instance = MagicMock()
        mock_instance.generate_image.return_value = "base64_image"
        mock_azure.return_value = mock_instance
        
        prompts = [
            "A simple image",
            "A doctor in a white coat with a stethoscope in a hospital",
            "A detailed landscape with mountains, rivers, and wildlife"
        ]
        
        for prompt in prompts:
            payload = ImageGenerationRequest(
                prompt=prompt,
                model="DALL-E-2"
            )
            result = LLMService.generate_image(payload)
            assert isinstance(result, ImageGenerationResponse)
    
    @patch('llm.service.service.Azure')
    def test_generate_image_returns_valid_response_model(self, mock_azure):
        """Test generate_image returns valid ImageGenerationResponse"""
        from llm.service.service import LLMService
        
        mock_instance = MagicMock()
        base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        mock_instance.generate_image.return_value = base64_data
        mock_azure.return_value = mock_instance
        
        payload = ImageGenerationRequest(
            prompt="Test",
            model="DALL-E-2"
        )
        
        result = LLMService.generate_image(payload)
        assert isinstance(result, ImageGenerationResponse)
        assert result.image == base64_data


class TestLLMServiceIntegration:
    """Integration tests for LLMService"""
    
    @patch('llm.service.service.Azure')
    def test_service_request_response_flow(self, mock_azure):
        """Test complete request-response flow"""
        from llm.service.service import LLMService
        
        mock_instance = MagicMock()
        mock_instance.generate_image.return_value = "test_base64"
        mock_azure.return_value = mock_instance
        
        # Create request
        request = ImageGenerationRequest(
            prompt="Integration test image",
            model="DALL-E-2"
        )
        
        # Get response
        response = LLMService.generate_image(request)
        
        # Validate response structure
        assert hasattr(response, 'image')
        assert response.image == "test_base64"
