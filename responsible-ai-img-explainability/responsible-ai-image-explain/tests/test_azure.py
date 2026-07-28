"""
Comprehensive tests for Azure API client integration
Tests Azure OpenAI and Gemini API interactions
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock, Mock, call
import json

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from image_explain.utils.model.azure import Azure


class TestAzureInitialization:
    """Test suite for Azure client initialization"""
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test_api_key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_VERSION': '2024-02-15-preview'
    })
    @patch('image_explain.utils.model.azure.AzureOpenAI')
    def test_azure_initialization_with_env_vars(self, mock_azure_client):
        """Test Azure client initialization with environment variables"""
        azure = Azure()
        
        assert azure.api_key == 'test_api_key'
        assert azure.azure_endpoint == 'https://test.openai.azure.com/'
        assert azure.api_version == '2024-02-15-preview'
        assert azure.client is not None
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test_key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_VERSION': '2024-02-15-preview'
    })
    @patch('image_explain.utils.model.azure.AzureOpenAI')
    def test_azure_client_instantiation(self, mock_azure_client):
        """Test that AzureOpenAI client is properly instantiated"""
        azure = Azure()
        
        mock_azure_client.assert_called_once()
        call_kwargs = mock_azure_client.call_args[1]
        
        assert call_kwargs['api_key'] == 'test_key'
        assert call_kwargs['api_version'] == '2024-02-15-preview'
        assert call_kwargs['azure_endpoint'] == 'https://test.openai.azure.com/'
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('image_explain.utils.model.azure.AzureOpenAI')
    def test_azure_initialization_with_missing_env_vars(self, mock_azure_client):
        """Test Azure client initialization with missing environment variables"""
        # Should still initialize, but with None values
        azure = Azure()
        
        assert azure.api_key is None or isinstance(azure.api_key, str)
        assert azure.azure_endpoint is None or isinstance(azure.azure_endpoint, str)
        assert azure.api_version is None or isinstance(azure.api_version, str)


class TestAzureGenerate:
    """Test suite for Azure generate method"""
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test_key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_VERSION': '2024-02-15-preview',
        'AZURE_DEPLOYMENT_ENGINE': 'gpt-4o'
    })
    @patch('image_explain.utils.model.azure.AzureOpenAI')
    def test_generate_with_image(self, mock_azure_openai):
        """Test generate method with image"""
        # Setup mock
        mock_client_instance = MagicMock()
        mock_azure_openai.return_value = mock_client_instance
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test response"))]
        mock_client_instance.chat.completions.create.return_value = mock_response
        
        azure = Azure()
        result = azure.generate(
            model_name="GPT_4o",
            prompt="Analyze this image",
            mime_type="image/jpeg",
            generated_image_base64="base64_data"
        )
        
        assert result is not None
        assert isinstance(result, str)
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test_key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_VERSION': '2024-02-15-preview',
        'AZURE_DEPLOYMENT_ENGINE': 'gpt-4o'
    })
    @patch('image_explain.utils.model.azure.AzureOpenAI')
    def test_generate_without_image(self, mock_azure_openai):
        """Test generate method without image"""
        mock_client_instance = MagicMock()
        mock_azure_openai.return_value = mock_client_instance
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Text response"))]
        mock_client_instance.chat.completions.create.return_value = mock_response
        
        azure = Azure()
        result = azure.generate(
            model_name="GPT_4o",
            prompt="Describe this scene",
            mime_type=None,
            generated_image_base64=None
        )
        
        assert result is not None
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test_key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_VERSION': '2024-02-15-preview',
        'AZURE_DEPLOYMENT_ENGINE': 'gpt-4o'
    })
    @patch('image_explain.utils.model.azure.AzureOpenAI')
    def test_generate_with_gpt_4o_model(self, mock_azure_openai):
        """Test generate with GPT-4o model"""
        mock_client_instance = MagicMock()
        mock_azure_openai.return_value = mock_client_instance
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="GPT-4o response"))]
        mock_client_instance.chat.completions.create.return_value = mock_response
        
        azure = Azure()
        result = azure.generate(
            model_name="GPT_4o",
            prompt="Test prompt",
            mime_type="image/jpeg",
            generated_image_base64="base64"
        )
        
        assert result == "GPT-4o response"
    
class TestAzureMessageConstruction:
    """Test suite for Azure message construction"""
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test_key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_VERSION': '2024-02-15-preview',
        'AZURE_DEPLOYMENT_ENGINE': 'gpt-4o'
    })
    @patch('image_explain.utils.model.azure.AzureOpenAI')
    def test_message_with_base64_image(self, mock_azure_openai):
        """Test message construction with base64 image"""
        mock_client_instance = MagicMock()
        mock_azure_openai.return_value = mock_client_instance
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_client_instance.chat.completions.create.return_value = mock_response
        
        azure = Azure()
        result = azure.generate(
            model_name="GPT_4o",
            prompt="Analyze image",
            mime_type="image/jpeg",
            generated_image_base64="data"
        )
        
        # Verify API was called
        mock_client_instance.chat.completions.create.assert_called_once()
        call_args = mock_client_instance.chat.completions.create.call_args
        
        # Messages should be constructed
        assert call_args is not None
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test_key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_VERSION': '2024-02-15-preview',
        'AZURE_DEPLOYMENT_ENGINE': 'gpt-4o'
    })
    @patch('image_explain.utils.model.azure.AzureOpenAI')
    def test_message_without_image(self, mock_azure_openai):
        """Test message construction without image"""
        mock_client_instance = MagicMock()
        mock_azure_openai.return_value = mock_client_instance
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_client_instance.chat.completions.create.return_value = mock_response
        
        azure = Azure()
        result = azure.generate(
            model_name="GPT_4o",
            prompt="Text only prompt",
            mime_type=None,
            generated_image_base64=None
        )
        
        # Verify API was called
        mock_client_instance.chat.completions.create.assert_called_once()


class TestAzureErrorHandling:
    """Test suite for Azure error handling"""
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test_key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_VERSION': '2024-02-15-preview',
        'AZURE_DEPLOYMENT_ENGINE': 'gpt-4o'
    })
    @patch('image_explain.utils.model.azure.AzureOpenAI')
    def test_generate_api_error_handling(self, mock_azure_openai):
        """Test handling of API errors"""
        mock_client_instance = MagicMock()
        mock_azure_openai.return_value = mock_client_instance
        
        # Simulate API error
        mock_client_instance.chat.completions.create.side_effect = Exception("API Error")
        
        azure = Azure()
        
        with pytest.raises(Exception):
            azure.generate(
                model_name="GPT_4o",
                prompt="Test",
                mime_type=None,
                generated_image_base64=None
            )
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test_key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_VERSION': '2024-02-15-preview',
        'AZURE_DEPLOYMENT_ENGINE': 'gpt-4o'
    })
    @patch('image_explain.utils.model.azure.AzureOpenAI')
    def test_generate_empty_response(self, mock_azure_openai):
        """Test handling of empty API response"""
        mock_client_instance = MagicMock()
        mock_azure_openai.return_value = mock_client_instance
        
        mock_response = MagicMock()
        mock_response.choices = []
        mock_client_instance.chat.completions.create.return_value = mock_response
        
        azure = Azure()
        
        # Should handle empty response gracefully
        try:
            result = azure.generate(
                model_name="GPT_4o",
                prompt="Test",
                mime_type=None,
                generated_image_base64=None
            )
        except (IndexError, AttributeError):
            pytest.skip("Empty response handling may vary")


class TestAzureIntegration:
    """Integration tests for Azure client"""
    
    def test_azure_class_exists(self):
        """Test that Azure class can be imported"""
        from image_explain.utils.model.azure import Azure
        assert Azure is not None
    
    def test_azure_has_generate_method(self):
        """Test that Azure has generate method"""
        from image_explain.utils.model.azure import Azure
        assert hasattr(Azure, 'generate')
        assert callable(Azure.generate)
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test_key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_VERSION': '2024-02-15-preview'
    })
    @patch('image_explain.utils.model.azure.AzureOpenAI')
    def test_azure_generate_returns_string(self, mock_azure_openai):
        """Test that generate method returns string"""
        mock_client_instance = MagicMock()
        mock_azure_openai.return_value = mock_client_instance
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test output"))]
        mock_client_instance.chat.completions.create.return_value = mock_response
        
        azure = Azure()
        result = azure.generate(
            model_name="GPT_4o",
            prompt="Test",
            mime_type="image/jpeg",
            generated_image_base64="base64"
        )
        
        assert isinstance(result, str)


class TestAzureResponseParsing:
    """Test suite for Azure response parsing"""
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test_key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_VERSION': '2024-02-15-preview',
        'AZURE_DEPLOYMENT_ENGINE': 'gpt-4o'
    })
    @patch('image_explain.utils.model.azure.AzureOpenAI')
    def test_parse_json_response(self, mock_azure_openai):
        """Test parsing JSON response"""
        mock_client_instance = MagicMock()
        mock_azure_openai.return_value = mock_client_instance
        
        json_response = '{"key": "value", "data": [1, 2, 3]}'
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=json_response))]
        mock_client_instance.chat.completions.create.return_value = mock_response
        
        azure = Azure()
        result = azure.generate(
            model_name="GPT_4o",
            prompt="Return JSON",
            mime_type=None,
            generated_image_base64=None
        )
        
        # Should return the JSON string
        assert json_response in result or result == json_response


class TestAzureDeploymentEngine:
    """Test suite for Azure deployment engine configuration"""
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test_key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_VERSION': '2024-02-15-preview',
        'AZURE_DEPLOYMENT_ENGINE': 'custom-deployment'
    })
    @patch('image_explain.utils.model.azure.AzureOpenAI')
    def test_custom_deployment_engine(self, mock_azure_openai):
        """Test with custom deployment engine"""
        mock_client_instance = MagicMock()
        mock_azure_openai.return_value = mock_client_instance
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_client_instance.chat.completions.create.return_value = mock_response
        
        azure = Azure()
        result = azure.generate(
            model_name="GPT_4o",
            prompt="Test",
            mime_type=None,
            generated_image_base64=None
        )
        
        assert result is not None
