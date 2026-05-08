"""
Test suite for fairness.dao.LlmConnection module.
Tests BaseLLM abstract class, concrete implementations (Azureopenai, GeminiFlash, GeminiPro, AWS),
and factory pattern (LLMConnection class and create_llm_connection function).
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from io import BytesIO
from PIL import Image
from datetime import datetime

from fairness.dao.LlmConnection import (
    BaseLLM, 
    Azureopenai, 
    GeminiFlash, 
    GeminiPro, 
    AWS, 
    LLMConnection,
    create_llm_connection
)


# ========== Test BaseLLM Abstract Class ==========

class TestBaseLLM:
    """Test the BaseLLM abstract base class."""

    def test_base_llm_is_abstract(self):
        """Test that BaseLLM cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseLLM()

    def test_base_llm_requires_both_methods(self):
        """Test that subclasses must implement both abstract methods."""
        class IncompleteClass(BaseLLM):
            pass
        
        with pytest.raises(TypeError):
            IncompleteClass()


# ========== Test Azureopenai ==========

class TestAzureopenai:
    """Test Azureopenai class."""

    def test_init_success_azure(self, mocker):
        """Test successful initialization with Azure type."""
        env_vars = {
            'OPENAI_API_KEY': 'test_key',
            'OPENAI_API_TYPE': 'azure',
            'OPENAI_API_BASE': 'https://test.openai.azure.com',
            'OPENAI_API_VERSION': '2023-05-15',
            'OPENAI_ENGINE_NAME': 'gpt-4'
        }
        mocker.patch('fairness.dao.LlmConnection.os.getenv', side_effect=lambda k, d=None: env_vars.get(k, d))
        mock_azure = mocker.patch('fairness.dao.LlmConnection.AzureOpenAI')
        mocker.patch('fairness.dao.LlmConnection.load_dotenv')
        
        azure = Azureopenai()
        
        assert azure.api_key == 'test_key'
        assert azure.api_type == 'azure'
        mock_azure.assert_called_once()

    def test_init_missing_env_vars(self, mocker):
        """Test initialization fails when required env vars are missing."""
        env_vars = {'OPENAI_API_KEY': 'test_key'}
        mocker.patch('fairness.dao.LlmConnection.os.getenv', side_effect=lambda k, d=None: env_vars.get(k, d))
        mocker.patch('fairness.dao.LlmConnection.load_dotenv')
        
        with pytest.raises(Exception, match="OpenAI environment variables are not properly set"):
            Azureopenai()

    def test_get_chat_completion_success(self, mocker):
        """Test successful chat completion."""
        env_vars = {
            'OPENAI_API_KEY': 'test_key',
            'OPENAI_API_TYPE': 'azure',
            'OPENAI_API_BASE': 'https://test.openai.azure.com',
            'OPENAI_API_VERSION': '2023-05-15',
            'OPENAI_ENGINE_NAME': 'gpt-4'
        }
        mocker.patch('fairness.dao.LlmConnection.os.getenv', side_effect=lambda k, d=None: env_vars.get(k, d))
        mocker.patch('fairness.dao.LlmConnection.load_dotenv')
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test response"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        mocker.patch('fairness.dao.LlmConnection.AzureOpenAI', return_value=mock_client)
        
        azure = Azureopenai()
        result = azure.get_chat_completion("System prompt", "User text")
        
        assert result == "Test response"


# ========== Test GeminiFlash ==========

class TestGeminiFlash:
    """Test GeminiFlash class."""

    def test_init_success(self, mocker):
        """Test successful initialization."""
        env_vars = {
            'GEMINI_API_KEY': 'test_key',
            'GEMINI_FLASH_MODEL_NAME': 'gemini-1.5-flash'
        }
        mocker.patch('fairness.dao.LlmConnection.os.getenv', side_effect=lambda k, d=None: env_vars.get(k, d))
        mock_genai_configure = mocker.patch('fairness.dao.LlmConnection.genai.configure')
        mock_genai_model = mocker.patch('fairness.dao.LlmConnection.genai.GenerativeModel')
        mocker.patch('fairness.dao.LlmConnection.load_dotenv')
        
        gemini = GeminiFlash()
        
        assert gemini.api_key == 'test_key'
        mock_genai_configure.assert_called_once_with(api_key='test_key')

    def test_init_missing_api_key(self, mocker):
        """Test initialization fails when API key is missing."""
        env_vars = {}
        mocker.patch('fairness.dao.LlmConnection.os.getenv', side_effect=lambda k, d=None: env_vars.get(k, d))
        mocker.patch('fairness.dao.LlmConnection.load_dotenv')
        
        with pytest.raises(Exception, match="Gemini API key is not set"):
            GeminiFlash()

    def test_get_chat_completion_success(self, mocker):
        """Test successful chat completion."""
        env_vars = {
            'GEMINI_API_KEY': 'test_key',
            'GEMINI_FLASH_MODEL_NAME': 'gemini-1.5-flash'
        }
        mocker.patch('fairness.dao.LlmConnection.os.getenv', side_effect=lambda k, d=None: env_vars.get(k, d))
        mocker.patch('fairness.dao.LlmConnection.genai.configure')
        mocker.patch('fairness.dao.LlmConnection.load_dotenv')
        
        mock_model = MagicMock()
        mock_candidate = MagicMock()
        mock_part = MagicMock()
        mock_part.text = "Gemini response"
        mock_candidate.content.parts = [mock_part]
        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]
        mock_model.generate_content.return_value = mock_response
        
        mocker.patch('fairness.dao.LlmConnection.genai.GenerativeModel', return_value=mock_model)
        
        gemini = GeminiFlash()
        result = gemini.get_chat_completion("System prompt", "User text")
        
        assert result == "Gemini response"


# ========== Test GeminiPro ==========

class TestGeminiPro:
    """Test GeminiPro class."""

    def test_init_success(self, mocker):
        """Test successful initialization."""
        env_vars = {
            'GEMINI_API_KEY': 'test_key',
            'GEMINI_PRO_MODEL_NAME': 'gemini-1.5-pro'
        }
        mocker.patch('fairness.dao.LlmConnection.os.getenv', side_effect=lambda k, d=None: env_vars.get(k, d))
        mock_genai_configure = mocker.patch('fairness.dao.LlmConnection.genai.configure')
        mocker.patch('fairness.dao.LlmConnection.genai.GenerativeModel')
        mocker.patch('fairness.dao.LlmConnection.load_dotenv')
        
        gemini = GeminiPro()
        
        assert gemini.api_key == 'test_key'
        mock_genai_configure.assert_called_once_with(api_key='test_key')


# ========== Test AWS ==========

class TestAWS:
    """Test AWS class."""

    def test_init_success(self, mocker):
        """Test successful initialization."""
        env_vars = {
            'AWS_KEY_ADMIN_PATH': 'https://test.aws.com',
            'AWS_SERVICE_NAME': 'bedrock-runtime',
            'REGION_NAME': 'us-east-1',
            'AWS_MODEL_ID': 'anthropic.claude-v2',
            'ACCEPT': 'application/json',
            'CONTENTTYPE': 'application/json',
            'ANTHROPIC_VERSION': 'bedrock-2023-05-31',
            'VERIFY_SSL': 'True'
        }
        mocker.patch('fairness.dao.LlmConnection.os.getenv', side_effect=lambda k, d=None: env_vars.get(k, d))
        mocker.patch('fairness.dao.LlmConnection.load_dotenv')
        
        aws = AWS()
        
        assert aws.url == 'https://test.aws.com'
        assert aws.region_name == 'us-east-1'

    def test_init_missing_env_vars(self, mocker):
        """Test initialization fails when required env vars are missing."""
        env_vars = {'AWS_KEY_ADMIN_PATH': 'https://test.aws.com'}
        mocker.patch('fairness.dao.LlmConnection.os.getenv', side_effect=lambda k, d=None: env_vars.get(k, d))
        mocker.patch('fairness.dao.LlmConnection.load_dotenv')
        
        with pytest.raises(Exception, match="AWS environment variables are not properly set"):
            AWS()

    def test_get_chat_completion_success(self, mocker):
        """Test successful chat completion with valid credentials."""
        env_vars = {
            'AWS_KEY_ADMIN_PATH': 'https://test.aws.com',
            'AWS_SERVICE_NAME': 'bedrock-runtime',
            'REGION_NAME': 'us-east-1',
            'AWS_MODEL_ID': 'anthropic.claude-v2',
            'ACCEPT': 'application/json',
            'CONTENTTYPE': 'application/json',
            'ANTHROPIC_VERSION': 'bedrock-2023-05-31',
            'VERIFY_SSL': 'True'
        }
        mocker.patch('fairness.dao.LlmConnection.os.getenv', side_effect=lambda k, d=None: env_vars.get(k, d))
        mocker.patch('fairness.dao.LlmConnection.load_dotenv')
        
        # Mock requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'expirationTime': '12hrs',
            'creationTime': datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            'awsAccessKeyId': 'test_access',
            'awsSecretAccessKey': 'test_secret',
            'awsSessionToken': 'test_token'
        }
        mocker.patch('fairness.dao.LlmConnection.requests.get', return_value=mock_response)
        
        # Mock boto3 client
        mock_client = MagicMock()
        mock_body = MagicMock()
        mock_body.read.return_value = b'{"content": [{"text": "AWS response"}], "stop_reason": "end_turn"}'
        mock_client.invoke_model.return_value = {"body": mock_body}
        mocker.patch('fairness.dao.LlmConnection.boto3.client', return_value=mock_client)
        
        # Mock utils
        mock_utils = MagicMock()
        mock_utils.is_time_difference_12_hours.return_value = True
        mocker.patch('fairness.dao.LlmConnection.utils', mock_utils)
        
        aws = AWS()
        result = aws.get_chat_completion("System prompt", "User text")
        
        assert result == "AWS response"


# ========== Test LLMConnection Factory ==========

class TestLLMConnection:
    """Test LLMConnection factory class."""

    def test_init_with_azureopenai(self, mocker):
        """Test initialization with Azureopenai provider."""
        azure_env = {
            'ACTIVE_LLM': 'azureopenai',
            'OPENAI_API_KEY': 'test_key',
            'OPENAI_API_TYPE': 'azure',
            'OPENAI_API_BASE': 'https://test.openai.azure.com',
            'OPENAI_API_VERSION': '2023-05-15',
            'OPENAI_ENGINE_NAME': 'gpt-4'
        }
        mocker.patch('fairness.dao.LlmConnection.os.getenv', side_effect=lambda k, d=None: azure_env.get(k, d))
        mocker.patch('fairness.dao.LlmConnection.AzureOpenAI')
        mocker.patch('fairness.dao.LlmConnection.load_dotenv')
        
        connection = LLMConnection()
        
        assert isinstance(connection.llm_instance, Azureopenai)
        assert connection.active_llm == 'azureopenai'

    def test_init_with_gemini_flash(self, mocker):
        """Test initialization with GeminiFlash provider."""
        gemini_env = {
            'ACTIVE_LLM': 'gemini-2.5-flash',
            'GEMINI_API_KEY': 'test_key',
            'GEMINI_FLASH_MODEL_NAME': 'gemini-1.5-flash'
        }
        mocker.patch('fairness.dao.LlmConnection.os.getenv', side_effect=lambda k, d=None: gemini_env.get(k, d))
        mocker.patch('fairness.dao.LlmConnection.genai.configure')
        mocker.patch('fairness.dao.LlmConnection.genai.GenerativeModel')
        mocker.patch('fairness.dao.LlmConnection.load_dotenv')
        
        connection = LLMConnection()
        
        assert isinstance(connection.llm_instance, GeminiFlash)
        assert connection.active_llm == 'gemini-2.5-flash'

    def test_init_with_invalid_llm(self, mocker):
        """Test initialization with invalid LLM provider."""
        env_vars = {'ACTIVE_LLM': 'InvalidLLM'}
        mocker.patch('fairness.dao.LlmConnection.os.getenv', side_effect=lambda k, d=None: env_vars.get(k, d))
        mocker.patch('fairness.dao.LlmConnection.load_dotenv')
        
        with pytest.raises(Exception, match="Invalid ACTIVE_LLM value"):
            LLMConnection()

    def test_get_chat_completion(self, mocker):
        """Test get_chat_completion delegates to underlying LLM."""
        azure_env = {
            'ACTIVE_LLM': 'azureopenai',
            'OPENAI_API_KEY': 'test_key',
            'OPENAI_API_TYPE': 'azure',
            'OPENAI_API_BASE': 'https://test.openai.azure.com',
            'OPENAI_API_VERSION': '2023-05-15',
            'OPENAI_ENGINE_NAME': 'gpt-4'
        }
        mocker.patch('fairness.dao.LlmConnection.os.getenv', side_effect=lambda k, d=None: azure_env.get(k, d))
        mocker.patch('fairness.dao.LlmConnection.load_dotenv')
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Delegated response"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        mocker.patch('fairness.dao.LlmConnection.AzureOpenAI', return_value=mock_client)
        
        connection = LLMConnection()
        result = connection.get_chat_completion("Prompt", "Text")
        
        assert result == "Delegated response"

    def test_get_active_llm(self, mocker):
        """Test get_active_llm returns the active provider name."""
        gemini_env = {
            'ACTIVE_LLM': 'gemini-2.5-pro',
            'GEMINI_API_KEY': 'test_key',
            'GEMINI_PRO_MODEL_NAME': 'gemini-1.5-pro'
        }
        mocker.patch('fairness.dao.LlmConnection.os.getenv', side_effect=lambda k, d=None: gemini_env.get(k, d))
        mocker.patch('fairness.dao.LlmConnection.genai.configure')
        mocker.patch('fairness.dao.LlmConnection.genai.GenerativeModel')
        mocker.patch('fairness.dao.LlmConnection.load_dotenv')
        
        connection = LLMConnection()
        
        assert connection.get_active_llm() == 'gemini-2.5-pro'


# ========== Test create_llm_connection Factory Function ==========

class TestCreateLLMConnection:
    """Test the create_llm_connection factory function."""

    def test_create_llm_connection_function(self, mocker):
        """Test the factory function creates LLMConnection correctly."""
        azure_env = {
            'ACTIVE_LLM': 'azureopenai',
            'OPENAI_API_KEY': 'test_key',
            'OPENAI_API_TYPE': 'azure',
            'OPENAI_API_BASE': 'https://test.openai.azure.com',
            'OPENAI_API_VERSION': '2023-05-15',
            'OPENAI_ENGINE_NAME': 'gpt-4'
        }
        mocker.patch('fairness.dao.LlmConnection.os.getenv', side_effect=lambda k, d=None: azure_env.get(k, d))
        mocker.patch('fairness.dao.LlmConnection.AzureOpenAI')
        mocker.patch('fairness.dao.LlmConnection.load_dotenv')
        
        connection = create_llm_connection()
        
        assert isinstance(connection, LLMConnection)
        assert connection.active_llm == 'azureopenai'


# ========== Test Edge Cases ==========

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_azure_api_error(self, mocker):
        """Test handling of Azure OpenAI API errors."""
        azure_env = {
            'OPENAI_API_KEY': 'test_key',
            'OPENAI_API_TYPE': 'azure',
            'OPENAI_API_BASE': 'https://test.openai.azure.com',
            'OPENAI_API_VERSION': '2023-05-15',
            'OPENAI_ENGINE_NAME': 'gpt-4'
        }
        mocker.patch('fairness.dao.LlmConnection.os.getenv', side_effect=lambda k, d=None: azure_env.get(k, d))
        mocker.patch('fairness.dao.LlmConnection.load_dotenv')
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        mocker.patch('fairness.dao.LlmConnection.AzureOpenAI', return_value=mock_client)
        
        azure = Azureopenai()
        
        with pytest.raises(Exception, match="API Error"):
            azure.get_chat_completion("Prompt", "Text")

    def test_aws_expired_credentials(self, mocker):
        """Test handling of expired AWS credentials."""
        env_vars = {
            'AWS_KEY_ADMIN_PATH': 'https://test.aws.com',
            'AWS_SERVICE_NAME': 'bedrock-runtime',
            'REGION_NAME': 'us-east-1',
            'AWS_MODEL_ID': 'anthropic.claude-v2',
            'ACCEPT': 'application/json',
            'CONTENTTYPE': 'application/json',
            'ANTHROPIC_VERSION': 'bedrock-2023-05-31',
            'VERIFY_SSL': 'True'
        }
        mocker.patch('fairness.dao.LlmConnection.os.getenv', side_effect=lambda k, d=None: env_vars.get(k, d))
        mocker.patch('fairness.dao.LlmConnection.load_dotenv')
        
        # Mock expired credentials
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'expirationTime': '12hrs',
            'creationTime': '2020-01-01T00:00:00.000000',
            'awsAccessKeyId': 'expired',
            'awsSecretAccessKey': 'expired',
            'awsSessionToken': 'expired'
        }
        mocker.patch('fairness.dao.LlmConnection.requests.get', return_value=mock_response)
        
        # Mock utils to return False (expired)
        mock_utils = MagicMock()
        mock_utils.is_time_difference_12_hours.return_value = False
        mocker.patch('fairness.dao.LlmConnection.utils', mock_utils)
        
        aws = AWS()
        result = aws.get_chat_completion("Prompt", "Text")
        
        assert "ExpiredTokenException" in result


# ========== Test Code Quality ==========

class TestCodeQuality:
    """Test code quality and architecture."""

    def test_all_llm_classes_inherit_from_base(self):
        """Test that all LLM classes inherit from BaseLLM."""
        assert issubclass(Azureopenai, BaseLLM)
        assert issubclass(GeminiFlash, BaseLLM)
        assert issubclass(GeminiPro, BaseLLM)
        assert issubclass(AWS, BaseLLM)

    def test_factory_function_exists(self):
        """Test that the module provides a factory function."""
        assert callable(create_llm_connection)


# ========== Test Integration ==========

class TestIntegration:
    """Test integration scenarios."""

    def test_complete_workflow(self, mocker):
        """Test complete workflow with Azure OpenAI."""
        azure_env = {
            'ACTIVE_LLM': 'azureopenai',
            'OPENAI_API_KEY': 'test_key',
            'OPENAI_API_TYPE': 'azure',
            'OPENAI_API_BASE': 'https://test.openai.azure.com',
            'OPENAI_API_VERSION': '2023-05-15',
            'OPENAI_ENGINE_NAME': 'gpt-4'
        }
        mocker.patch('fairness.dao.LlmConnection.os.getenv', side_effect=lambda k, d=None: azure_env.get(k, d))
        mocker.patch('fairness.dao.LlmConnection.load_dotenv')
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Workflow response"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        mocker.patch('fairness.dao.LlmConnection.AzureOpenAI', return_value=mock_client)
        
        # Create connection
        connection = create_llm_connection()
        
        # Verify active LLM
        assert connection.get_active_llm() == 'azureopenai'
        
        # Get chat completion
        result = connection.get_chat_completion("Prompt", "Text")
        assert result == "Workflow response"
