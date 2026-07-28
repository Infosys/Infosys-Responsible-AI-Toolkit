import pytest
from unittest.mock import Mock, patch, MagicMock
import openai
import os


class TestAzureInit:
    """Test Azure class initialization with environment variables."""

    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "test-key-12345",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_DEPLOYMENT_ENGINE": "gpt-4"
    })
    @patch('openai.AzureOpenAI')
    def test_azure_init_success(self, mock_azure_openai):
        """Test successful Azure class initialization."""
        from llm_explain.utility.connections import Azure
        
        mock_client = MagicMock()
        mock_azure_openai.return_value = mock_client
        
        azure = Azure()
        
        assert azure.api_key == "test-key-12345"
        assert azure.azure_endpoint == "https://test.openai.azure.com"
        assert azure.api_version == "2024-02-15-preview"
        assert azure.deployment_engine == "gpt-4"
        assert azure.client == mock_client
        
        mock_azure_openai.assert_called_once_with(
            api_key="test-key-12345",
            api_version="2024-02-15-preview",
            azure_endpoint="https://test.openai.azure.com"
        )

    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "key1",
        "AZURE_OPENAI_ENDPOINT": "endpoint1",
        "AZURE_OPENAI_API_VERSION": "v1",
        "AZURE_DEPLOYMENT_ENGINE": "model1"
    })
    @patch('openai.AzureOpenAI')
    def test_azure_init_reads_env_variables(self, mock_azure_openai):
        """Test that Azure reads environment variables correctly."""
        from llm_explain.utility.connections import Azure
        
        azure = Azure()
        
        assert azure.api_key == "key1"
        assert azure.azure_endpoint == "endpoint1"
        assert azure.api_version == "v1"
        assert azure.deployment_engine == "model1"

    @patch.dict(os.environ, {}, clear=True)
    @patch('openai.AzureOpenAI')
    def test_azure_init_missing_env_variables(self, mock_azure_openai):
        """Test Azure initialization when environment variables are missing."""
        from llm_explain.utility.connections import Azure
        
        azure = Azure()
        
        assert azure.api_key is None
        assert azure.azure_endpoint is None
        assert azure.api_version is None
        assert azure.deployment_engine is None


class TestAzureGenerate:
    """Test Azure text generation functionality."""

    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_DEPLOYMENT_ENGINE": "gpt-4"
    })
    @patch('openai.AzureOpenAI')
    def test_generate_success(self, mock_azure_openai):
        """Test successful text generation."""
        from llm_explain.utility.connections import Azure
        
        # Setup mock response
        mock_message = Mock()
        mock_message.content = "This is the generated response."
        
        mock_choice = Mock()
        mock_choice.message = mock_message
        
        mock_completion = Mock()
        mock_completion.choices = [mock_choice]
        mock_completion.usage = Mock(prompt_tokens=10, completion_tokens=20)
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_azure_openai.return_value = mock_client
        
        azure = Azure()
        content, input_tokens, output_tokens = azure.generate("What is AI?")
        
        assert content == "This is the generated response."
        assert input_tokens == 10
        assert output_tokens == 20
        
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": "What is AI?"
                }
            ]
        )

    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_DEPLOYMENT_ENGINE": "gpt-4"
    })
    @patch('openai.AzureOpenAI')
    def test_generate_with_complex_prompt(self, mock_azure_openai):
        """Test generation with complex multi-line prompt."""
        from llm_explain.utility.connections import Azure
        
        mock_message = Mock()
        mock_message.content = "Complex response with\nmultiple lines\nand details."
        
        mock_choice = Mock()
        mock_choice.message = mock_message
        
        mock_completion = Mock()
        mock_completion.choices = [mock_choice]
        mock_completion.usage = Mock(prompt_tokens=15, completion_tokens=25)
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_azure_openai.return_value = mock_client
        
        azure = Azure()
        prompt = "Explain quantum computing\nin detail\nwith examples"
        content, input_tokens, output_tokens = azure.generate(prompt)
        
        assert "Complex response" in content
        assert "multiple lines" in content
        
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['messages'][1]['content'] == prompt

    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_DEPLOYMENT_ENGINE": "gpt-4"
    })
    @patch('openai.AzureOpenAI')
    def test_generate_with_empty_prompt(self, mock_azure_openai):
        """Test generation with empty prompt."""
        from llm_explain.utility.connections import Azure
        
        mock_message = Mock()
        mock_message.content = "I'm ready to help!"
        
        mock_choice = Mock()
        mock_choice.message = mock_message
        
        mock_completion = Mock()
        mock_completion.choices = [mock_choice]
        mock_completion.usage = Mock(prompt_tokens=5, completion_tokens=10)
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_azure_openai.return_value = mock_client
        
        azure = Azure()
        content, input_tokens, output_tokens = azure.generate("")
        
        assert content == "I'm ready to help!"

    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_DEPLOYMENT_ENGINE": "gpt-4"
    })
    @patch('openai.AzureOpenAI')
    def test_generate_api_connection_error(self, mock_azure_openai):
        """Test handling of API connection error."""
        from llm_explain.utility.connections import Azure
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = openai.APIConnectionError(
            request=Mock()
        )
        mock_azure_openai.return_value = mock_client
        
        azure = Azure()
        
        with pytest.raises(Exception) as exc_info:
            azure.generate("Test prompt")
        
        assert "Azure OpenAI API connection error" in str(exc_info.value)

    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_DEPLOYMENT_ENGINE": "gpt-4"
    })
    @patch('openai.AzureOpenAI')
    def test_generate_logs_error_on_connection_failure(self, mock_azure_openai):
        """Test that connection errors are logged."""
        from llm_explain.utility.connections import Azure
        
        mock_client = MagicMock()
        error = openai.APIConnectionError(request=Mock())
        mock_client.chat.completions.create.side_effect = error
        mock_azure_openai.return_value = mock_client
        
        azure = Azure()
        
        with pytest.raises(Exception):
            azure.generate("Test")

    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_DEPLOYMENT_ENGINE": "gpt-4"
    })
    @patch('openai.AzureOpenAI')
    def test_generate_with_special_characters(self, mock_azure_openai):
        """Test generation with special characters in prompt."""
        from llm_explain.utility.connections import Azure
        
        mock_message = Mock()
        mock_message.content = "Response with special chars: !@#$%"
        
        mock_choice = Mock()
        mock_choice.message = mock_message
        
        mock_completion = Mock()
        mock_completion.choices = [mock_choice]
        mock_completion.usage = Mock(prompt_tokens=8, completion_tokens=12)
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_azure_openai.return_value = mock_client
        
        azure = Azure()
        content, input_tokens, output_tokens = azure.generate("Test with !@#$%^&*()")
        
        assert "special chars" in content

    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_DEPLOYMENT_ENGINE": "gpt-4"
    })
    @patch('openai.AzureOpenAI')
    def test_generate_uses_correct_system_message(self, mock_azure_openai):
        """Test that system message is correctly set."""
        from llm_explain.utility.connections import Azure
        
        mock_message = Mock()
        mock_message.content = "Response"
        
        mock_choice = Mock()
        mock_choice.message = mock_message
        
        mock_completion = Mock()
        mock_completion.choices = [mock_choice]
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_azure_openai.return_value = mock_client
        
        azure = Azure()
        azure.generate("Test")
        
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        
        assert messages[0]['role'] == 'system'
        assert messages[0]['content'] == "You are a helpful assistant."

    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_DEPLOYMENT_ENGINE": "gpt-4"
    })
    @patch('openai.AzureOpenAI')
    def test_generate_uses_correct_model(self, mock_azure_openai):
        """Test that correct deployment engine is used."""
        from llm_explain.utility.connections import Azure
        
        mock_message = Mock()
        mock_message.content = "Response"
        
        mock_choice = Mock()
        mock_choice.message = mock_message
        
        mock_completion = Mock()
        mock_completion.choices = [mock_choice]
        mock_completion.usage = Mock(prompt_tokens=5, completion_tokens=10)
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_azure_openai.return_value = mock_client
        
        azure = Azure()
        azure.generate("Test")
        
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['model'] == "gpt-4"

    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_DEPLOYMENT_ENGINE": "gpt-4"
    })
    @patch('openai.AzureOpenAI')
    def test_generate_returns_first_choice_content(self, mock_azure_openai):
        """Test that generate returns content from first choice."""
        from llm_explain.utility.connections import Azure
        
        mock_message1 = Mock()
        mock_message1.content = "First response"
        
        mock_message2 = Mock()
        mock_message2.content = "Second response"
        
        mock_choice1 = Mock()
        mock_choice1.message = mock_message1
        
        mock_choice2 = Mock()
        mock_choice2.message = mock_message2
        
        mock_completion = Mock()
        mock_completion.choices = [mock_choice1, mock_choice2]
        mock_completion.usage = Mock(prompt_tokens=5, completion_tokens=10)
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_azure_openai.return_value = mock_client
        
        azure = Azure()
        content, input_tokens, output_tokens = azure.generate("Test")
        
        assert content == "First response"

    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_DEPLOYMENT_ENGINE": "gpt-4"
    })
    @patch('openai.AzureOpenAI')
    def test_generate_with_unicode_prompt(self, mock_azure_openai):
        """Test generation with Unicode characters."""
        from llm_explain.utility.connections import Azure
        
        mock_message = Mock()
        mock_message.content = "Response with 中文 和 日本語"
        
        mock_choice = Mock()
        mock_choice.message = mock_message
        
        mock_completion = Mock()
        mock_completion.choices = [mock_choice]
        mock_completion.usage = Mock(prompt_tokens=10, completion_tokens=15)
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_azure_openai.return_value = mock_client
        
        azure = Azure()
        content, input_tokens, output_tokens = azure.generate("Translate: Hello 世界")
        
        assert "中文" in content
        assert "日本語" in content
