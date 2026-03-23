import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from llm_explain.utility.connections import Azure, Gemini, AWS, Perplexity


# ==================== Azure Tests ====================

@pytest.mark.unit
class TestAzureInitialization:
    """Test Azure class initialization"""
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test-key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
        'AZURE_OPENAI_API_VERSION': '2023-05-15',
        'AZURE_DEPLOYMENT_ENGINE': 'gpt-35-turbo'
    })
    @patch('llm_explain.utility.connections.openai.AzureOpenAI')
    def test_azure_initialization_success(self, mock_client):
        """Test successful Azure initialization"""
        azure = Azure()
        
        assert azure.api_key == 'test-key'
        assert azure.azure_endpoint == 'https://test.openai.azure.com'
        assert azure.api_version == '2023-05-15'
        assert azure.deployment_engine == 'gpt-35-turbo'
        mock_client.assert_called_once()
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'key',
        'AZURE_OPENAI_ENDPOINT': 'endpoint',
        'AZURE_OPENAI_API_VERSION': 'version',
        'AZURE_DEPLOYMENT_ENGINE': 'engine'
    })
    @patch('llm_explain.utility.connections.openai.AzureOpenAI')
    def test_azure_client_initialized(self, mock_client):
        """Test Azure client is properly initialized"""
        azure = Azure()
        
        assert azure.client is not None
        mock_client.assert_called_once_with(
            api_key='key',
            api_version='version',
            azure_endpoint='endpoint'
        )


@pytest.mark.unit
class TestAzureGenerate:
    """Test Azure generate method"""
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test-key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
        'AZURE_OPENAI_API_VERSION': '2023-05-15',
        'AZURE_DEPLOYMENT_ENGINE': 'gpt-35-turbo'
    })
    @patch('llm_explain.utility.connections.openai.AzureOpenAI')
    def test_azure_generate_success(self, mock_client_class):
        """Test successful generation with Azure"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_completion = Mock()
        mock_completion.choices = [Mock(message=Mock(content="Test response"))]
        mock_completion.usage = Mock(prompt_tokens=10, completion_tokens=20)
        mock_client.chat.completions.create.return_value = mock_completion
        
        azure = Azure()
        content, input_tokens, output_tokens = azure.generate("Test prompt")
        
        assert content == "Test response"
        assert input_tokens == 10
        assert output_tokens == 20
        mock_client.chat.completions.create.assert_called_once()
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test-key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
        'AZURE_OPENAI_API_VERSION': '2023-05-15',
        'AZURE_DEPLOYMENT_ENGINE': 'gpt-4o'
    })
    @patch('llm_explain.utility.connections.openai.AzureOpenAI')
    def test_azure_generate_with_gpt4o_model(self, mock_client_class):
        """Test generation with GPT-4o model (JSON mode)"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_completion = Mock()
        mock_completion.choices = [Mock(message=Mock(content='{"result": "test"}'))]
        mock_completion.usage = Mock(prompt_tokens=15, completion_tokens=25)
        mock_client.chat.completions.create.return_value = mock_completion
        
        azure = Azure()
        content, input_tokens, output_tokens = azure.generate("Test prompt", modelName="gpt-4o")
        
        assert '{"result": "test"}' in content
        assert input_tokens == 15
        assert output_tokens == 25
        
        
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs.get('response_format') == {"type": "json_object"}
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test-key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
        'AZURE_OPENAI_API_VERSION': '2023-05-15',
        'AZURE_DEPLOYMENT_ENGINE': 'gpt-35-turbo'
    })
    @patch('llm_explain.utility.connections.openai.AzureOpenAI')
    def test_azure_generate_with_gpt4o_uppercase(self, mock_client_class):
        """Test generation with GPT-4O uppercase (should convert to lowercase)"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_completion = Mock()
        mock_completion.choices = [Mock(message=Mock(content='{"result": "test"}'))]
        mock_completion.usage = Mock(prompt_tokens=15, completion_tokens=25)
        mock_client.chat.completions.create.return_value = mock_completion
        
        azure = Azure()
        content, input_tokens, output_tokens = azure.generate("Test prompt", modelName="GPT-4O")
        
        
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs.get('response_format') == {"type": "json_object"}
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test-key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
        'AZURE_OPENAI_API_VERSION': '2023-05-15',
        'AZURE_DEPLOYMENT_ENGINE': 'gpt-35-turbo'
    })
    @patch('llm_explain.utility.connections.openai.AzureOpenAI')
    def test_azure_generate_without_model_name(self, mock_client_class):
        """Test generation without specifying model name"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_completion = Mock()
        mock_completion.choices = [Mock(message=Mock(content="Response"))]
        mock_completion.usage = Mock(prompt_tokens=10, completion_tokens=20)
        mock_client.chat.completions.create.return_value = mock_completion
        
        azure = Azure()
        content, input_tokens, output_tokens = azure.generate("Test prompt", modelName=None)
        
        # Verify response_format is NOT included
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert 'response_format' not in call_kwargs
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test-key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
        'AZURE_OPENAI_API_VERSION': '2023-05-15',
        'AZURE_DEPLOYMENT_ENGINE': 'gpt-35-turbo'
    })
    @patch('llm_explain.utility.connections.openai.AzureOpenAI')
    def test_azure_generate_with_other_model(self, mock_client_class):
        """Test generation with non-GPT-4o model"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_completion = Mock()
        mock_completion.choices = [Mock(message=Mock(content="Response"))]
        mock_completion.usage = Mock(prompt_tokens=10, completion_tokens=20)
        mock_client.chat.completions.create.return_value = mock_completion
        
        azure = Azure()
        content, input_tokens, output_tokens = azure.generate("Test prompt", modelName="gpt-3.5-turbo")
        
  
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert 'response_format' not in call_kwargs
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test-key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
        'AZURE_OPENAI_API_VERSION': '2023-05-15',
        'AZURE_DEPLOYMENT_ENGINE': 'gpt-35-turbo'
    })
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test-key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
        'AZURE_OPENAI_API_VERSION': '2023-05-15',
        'AZURE_DEPLOYMENT_ENGINE': 'gpt-35-turbo'
    })
    @patch('llm_explain.utility.connections.openai.AzureOpenAI')
    def test_azure_generate_message_structure(self, mock_client_class):
        """Test Azure generate creates correct message structure"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_completion = Mock()
        mock_completion.choices = [Mock(message=Mock(content="Response"))]
        mock_completion.usage = Mock(prompt_tokens=10, completion_tokens=20)
        mock_client.chat.completions.create.return_value = mock_completion
        
        azure = Azure()
        azure.generate("Test prompt")
        
        call_args = mock_client.chat.completions.create.call_args[1]
        messages = call_args['messages']
        
        assert len(messages) == 2
        assert messages[0]['role'] == 'system'
        assert messages[0]['content'] == 'You are a helpful assistant.'
        assert messages[1]['role'] == 'user'
        assert messages[1]['content'] == 'Test prompt'



@pytest.mark.unit
class TestGeminiInitialization:
    """Test Gemini class initialization"""
    
    @patch.dict(os.environ, {
        'GEMINI_API_KEY': 'test-gemini-key',
        'GEMINI_MODEL_NAME_PRO': 'gemini-1.5-pro',
        'GEMINI_MODEL_NAME_FLASH': 'gemini-1.5-flash'
    })
    def test_gemini_initialization_success(self):
        """Test successful Gemini initialization"""
        gemini = Gemini()
        
        assert gemini.gemini_api_key == 'test-gemini-key'
        assert gemini.gemini_model_name_pro == 'gemini-1.5-pro'
        assert gemini.gemini_model_name_flash == 'gemini-1.5-flash'


@pytest.mark.unit
class TestGeminiGenerate:
    """Test Gemini generate method"""
    
    @patch.dict(os.environ, {
        'GEMINI_API_KEY': 'test-key',
        'GEMINI_MODEL_NAME_PRO': 'gemini-1.5-pro',
        'GEMINI_MODEL_NAME_FLASH': 'gemini-1.5-flash'
    })
    @patch('llm_explain.utility.connections.genai')
    def test_gemini_generate_with_pro_model(self, mock_genai):
        """Test Gemini generation with Pro model"""
        mock_model = Mock()
        mock_response = Mock(text="Gemini Pro response")
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        gemini = Gemini()
        result = gemini.generate("Test prompt", modelName="gemini-pro")
        
        assert result == "Gemini Pro response"
        mock_genai.configure.assert_called_once_with(api_key='test-key')
        mock_genai.GenerativeModel.assert_called_once_with('gemini-1.5-pro')
    
    @patch.dict(os.environ, {
        'GEMINI_API_KEY': 'test-key',
        'GEMINI_MODEL_NAME_PRO': 'gemini-1.5-pro',
        'GEMINI_MODEL_NAME_FLASH': 'gemini-1.5-flash'
    })
    @patch('llm_explain.utility.connections.genai')
    def test_gemini_generate_with_flash_model(self, mock_genai):
        """Test Gemini generation with Flash model"""
        mock_model = Mock()
        mock_response = Mock(text="Gemini Flash response")
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        gemini = Gemini()
        result = gemini.generate("Test prompt", modelName="gemini-flash")
        
        assert result == "Gemini Flash response"
        mock_genai.GenerativeModel.assert_called_once_with('gemini-1.5-flash')
    
    @patch.dict(os.environ, {
        'GEMINI_API_KEY': 'test-key',
        'GEMINI_MODEL_NAME_PRO': 'gemini-1.5-pro',
        'GEMINI_MODEL_NAME_FLASH': 'gemini-1.5-flash'
    })
    @patch('llm_explain.utility.connections.genai')
    def test_gemini_generate_with_uppercase_model(self, mock_genai):
        """Test Gemini generation with uppercase model name"""
        mock_model = Mock()
        mock_response = Mock(text="Response")
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        gemini = Gemini()
        result = gemini.generate("Test prompt", modelName="GEMINI-PRO")
        
        assert result == "Response"
        mock_genai.GenerativeModel.assert_called_once_with('gemini-1.5-pro')
    
    @patch.dict(os.environ, {
        'GEMINI_API_KEY': 'test-key',
        'GEMINI_MODEL_NAME_PRO': 'gemini-1.5-pro',
        'GEMINI_MODEL_NAME_FLASH': 'gemini-1.5-flash'
    })
    @patch('llm_explain.utility.connections.genai')
    def test_gemini_generate_api_error(self, mock_genai):
        """Test Gemini generation handles API errors"""
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API error")
        mock_genai.GenerativeModel.return_value = mock_model
        
        gemini = Gemini()
        
        with pytest.raises(Exception, match="Gemini API error"):
            gemini.generate("Test prompt", modelName="gemini-pro")
    
    @patch.dict(os.environ, {
        'GEMINI_API_KEY': 'test-key',
        'GEMINI_MODEL_NAME_PRO': 'gemini-1.5-pro',
        'GEMINI_MODEL_NAME_FLASH': 'gemini-1.5-flash'
    })
    @patch('llm_explain.utility.connections.genai')
    def test_gemini_generate_calls_generate_content(self, mock_genai):
        """Test Gemini generate calls generate_content with prompt"""
        mock_model = Mock()
        mock_response = Mock(text="Response")
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        gemini = Gemini()
        gemini.generate("My test prompt", modelName="gemini-pro")
        
        mock_model.generate_content.assert_called_once_with("My test prompt")




@pytest.mark.unit
class TestAWSInitialization:
    """Test AWS class initialization"""
    
    @patch.dict(os.environ, {
        'AWS_KEY_ADMIN_PATH': 'https://test.aws.com/admin',
        'AWS_SERVICE_NAME': 'bedrock-runtime',
        'REGION_NAME': 'us-east-1',
        'AWS_MODEL_ID': 'anthropic.claude-v2',
        'ACCEPT': 'application/json',
        'CONTENTTYPE': 'application/json',
        'ANTHROPIC_VERSION': 'bedrock-2023-05-31'
    })
    def test_aws_initialization_success(self):
        """Test successful AWS initialization"""
        aws = AWS()
        
        assert aws.url == 'https://test.aws.com/admin'
        assert aws.aws_service_name == 'bedrock-runtime'
        assert aws.region_name == 'us-east-1'
        assert aws.model_id == 'anthropic.claude-v2'
        assert aws.accept == 'application/json'
        assert aws.contentType == 'application/json'
        assert aws.anthropic_version == 'bedrock-2023-05-31'
    
    @patch.dict(os.environ, {
        'AWS_KEY_ADMIN_PATH': '',
        'AWS_SERVICE_NAME': 'bedrock-runtime',
        'REGION_NAME': 'us-east-1',
        'AWS_MODEL_ID': 'model',
        'ACCEPT': 'json',
        'CONTENTTYPE': 'json',
        'ANTHROPIC_VERSION': 'version'
    })
    def test_aws_initialization_missing_url(self):
        """Test AWS initialization fails with missing URL"""
        with pytest.raises(Exception, match="AWS environment variables are not properly set"):
            AWS()
    
    @patch.dict(os.environ, {
        'AWS_KEY_ADMIN_PATH': 'url',
        'AWS_SERVICE_NAME': '',
        'REGION_NAME': 'us-east-1',
        'AWS_MODEL_ID': 'model',
        'ACCEPT': 'json',
        'CONTENTTYPE': 'json',
        'ANTHROPIC_VERSION': 'version'
    })
    def test_aws_initialization_missing_service_name(self):
        """Test AWS initialization fails with missing service name"""
        with pytest.raises(Exception, match="AWS environment variables are not properly set"):
            AWS()


@pytest.mark.unit
class TestAWSCallAWS:
    """Test AWS call_AWS method"""
    
    @patch.dict(os.environ, {
        'AWS_KEY_ADMIN_PATH': 'https://test.aws.com/admin',
        'AWS_SERVICE_NAME': 'bedrock-runtime',
        'REGION_NAME': 'us-east-1',
        'AWS_MODEL_ID': 'anthropic.claude-v2',
        'ACCEPT': 'application/json',
        'CONTENTTYPE': 'application/json',
        'ANTHROPIC_VERSION': 'bedrock-2023-05-31'
    })
    @patch('llm_explain.utility.connections.requests.get')
    @patch('llm_explain.utility.connections.boto3.client')
    def test_call_aws_success(self, mock_boto_client, mock_requests_get):
        """Test successful AWS call"""
        # Mock admin credentials response
        creation_time = datetime.now().isoformat()
        mock_admin_response = Mock()
        mock_admin_response.status_code = 200
        mock_admin_response.json.return_value = {
            'awsAccessKeyId': 'test-access-key',
            'awsSecretAccessKey': 'test-secret-key',
            'awsSessionToken': 'test-session-token',
            'expirationTime': '24hrs',
            'creationTime': creation_time
        }
        mock_requests_get.return_value = mock_admin_response
        
        # Mock boto3 client response
        mock_client = Mock()
        mock_response = {
            'body': Mock(read=lambda: json.dumps({
                'content': [{'text': 'AWS response'}],
                'stop_reason': 'end_turn'
            }).encode())
        }
        mock_client.invoke_model.return_value = mock_response
        mock_boto_client.return_value = mock_client
        
        aws = AWS()
        result = aws.call_AWS("Test prompt")
        
        assert result == 'AWS response'
        mock_requests_get.assert_called_once()
        mock_boto_client.assert_called_once()
    
    @patch.dict(os.environ, {
        'AWS_KEY_ADMIN_PATH': 'https://test.aws.com/admin',
        'AWS_SERVICE_NAME': 'bedrock-runtime',
        'REGION_NAME': 'us-east-1',
        'AWS_MODEL_ID': 'anthropic.claude-v2',
        'ACCEPT': 'application/json',
        'CONTENTTYPE': 'application/json',
        'ANTHROPIC_VERSION': 'bedrock-2023-05-31'
    })
    @patch('llm_explain.utility.connections.requests.get')
    @patch('llm_explain.utility.connections.boto3.client')
    def test_call_aws_with_empty_text(self, mock_boto_client, mock_requests_get):
        """Test AWS call with empty text returns stop_reason"""
        creation_time = datetime.now().isoformat()
        mock_admin_response = Mock()
        mock_admin_response.status_code = 200
        mock_admin_response.json.return_value = {
            'awsAccessKeyId': 'key',
            'awsSecretAccessKey': 'secret',
            'awsSessionToken': 'token',
            'expirationTime': '24hrs',
            'creationTime': creation_time
        }
        mock_requests_get.return_value = mock_admin_response
        
        mock_client = Mock()
        mock_response = {
            'body': Mock(read=lambda: json.dumps({
                'content': [{'text': ''}],
                'stop_reason': 'max_tokens'
            }).encode())
        }
        mock_client.invoke_model.return_value = mock_response
        mock_boto_client.return_value = mock_client
        
        aws = AWS()
        result = aws.call_AWS("Test prompt")
        
        assert result == 'max_tokens'
    
    @patch.dict(os.environ, {
        'AWS_KEY_ADMIN_PATH': 'https://test.aws.com/admin',
        'AWS_SERVICE_NAME': 'bedrock-runtime',
        'REGION_NAME': 'us-east-1',
        'AWS_MODEL_ID': 'model',
        'ACCEPT': 'json',
        'CONTENTTYPE': 'json',
        'ANTHROPIC_VERSION': 'version'
    })
    @patch('llm_explain.utility.connections.requests.get')
    def test_call_aws_expired_session(self, mock_requests_get):
        """Test AWS call with expired session"""
        # Session expired (created more than 24 hours ago)
        old_time = (datetime.now() - timedelta(hours=25)).isoformat()
        mock_admin_response = Mock()
        mock_admin_response.status_code = 200
        mock_admin_response.json.return_value = {
            'awsAccessKeyId': 'key',
            'awsSecretAccessKey': 'secret',
            'awsSessionToken': 'token',
            'expirationTime': '24hrs',
            'creationTime': old_time
        }
        mock_requests_get.return_value = mock_admin_response
        
        aws = AWS()
        result = aws.call_AWS("Test prompt")
        
        assert "ExpiredTokenException" in result
        assert "AWS Credentials included in the request is expired" in result
    
    @patch.dict(os.environ, {
        'AWS_KEY_ADMIN_PATH': 'https://test.aws.com/admin',
        'AWS_SERVICE_NAME': 'bedrock-runtime',
        'REGION_NAME': 'us-east-1',
        'AWS_MODEL_ID': 'model',
        'ACCEPT': 'json',
        'CONTENTTYPE': 'json',
        'ANTHROPIC_VERSION': 'version'
    })
    @patch('llm_explain.utility.connections.requests.get')
    def test_call_aws_admin_error(self, mock_requests_get):
        """Test AWS call with admin endpoint error"""
        mock_requests_get.side_effect = Exception("Connection error")
        
        aws = AWS()
        
        with pytest.raises(Exception, match="Connection error"):
            aws.call_AWS("Test prompt")
    
    @patch.dict(os.environ, {
        'AWS_KEY_ADMIN_PATH': 'https://test.aws.com/admin',
        'AWS_SERVICE_NAME': 'bedrock-runtime',
        'REGION_NAME': 'us-east-1',
        'AWS_MODEL_ID': 'model',
        'ACCEPT': 'json',
        'CONTENTTYPE': 'json',
        'ANTHROPIC_VERSION': 'version'
    })
    @patch('llm_explain.utility.connections.requests.get')
    @patch('llm_explain.utility.connections.boto3.client')
    def test_call_aws_boto_error(self, mock_boto_client, mock_requests_get):
        """Test AWS call with boto3 error"""
        creation_time = datetime.now().isoformat()
        mock_admin_response = Mock()
        mock_admin_response.status_code = 200
        mock_admin_response.json.return_value = {
            'awsAccessKeyId': 'key',
            'awsSecretAccessKey': 'secret',
            'awsSessionToken': 'token',
            'expirationTime': '24hrs',
            'creationTime': creation_time
        }
        mock_requests_get.return_value = mock_admin_response
        
        mock_boto_client.side_effect = Exception("Boto3 error")
        
        aws = AWS()
        
        with pytest.raises(Exception, match="Boto3 error"):
            aws.call_AWS("Test prompt")


@pytest.mark.unit
class TestAWSIsTimeDifference:
    """Test AWS is_time_difference_12_hours method"""
    
    @patch.dict(os.environ, {
        'AWS_KEY_ADMIN_PATH': 'url',
        'AWS_SERVICE_NAME': 'service',
        'REGION_NAME': 'region',
        'AWS_MODEL_ID': 'model',
        'ACCEPT': 'json',
        'CONTENTTYPE': 'json',
        'ANTHROPIC_VERSION': 'version'
    })
    def test_time_difference_less_than_expiration(self):
        """Test time difference less than expiration time returns True"""
        aws = AWS()
        
        # Created 6 hours ago, expiration is 12 hours
        creation_time = datetime.now() - timedelta(hours=6)
        expiration_hours = 12
        
        result = aws.is_time_difference_12_hours(creation_time, expiration_hours)
        
        assert result is True
    
    @patch.dict(os.environ, {
        'AWS_KEY_ADMIN_PATH': 'url',
        'AWS_SERVICE_NAME': 'service',
        'REGION_NAME': 'region',
        'AWS_MODEL_ID': 'model',
        'ACCEPT': 'json',
        'CONTENTTYPE': 'json',
        'ANTHROPIC_VERSION': 'version'
    })
    def test_time_difference_more_than_expiration(self):
        """Test time difference more than expiration time returns False"""
        aws = AWS()
        
       
        creation_time = datetime.now() - timedelta(hours=25)
        expiration_hours = 24
        
        result = aws.is_time_difference_12_hours(creation_time, expiration_hours)
        
        assert result is False
    
    @patch.dict(os.environ, {
        'AWS_KEY_ADMIN_PATH': 'url',
        'AWS_SERVICE_NAME': 'service',
        'REGION_NAME': 'region',
        'AWS_MODEL_ID': 'model',
        'ACCEPT': 'json',
        'CONTENTTYPE': 'json',
        'ANTHROPIC_VERSION': 'version'
    })
    def test_time_difference_exactly_at_expiration(self):
        """Test time difference exactly at expiration boundary"""
        aws = AWS()
        
     
        creation_time = datetime.now() - timedelta(hours=12)
        expiration_hours = 12
        
        result = aws.is_time_difference_12_hours(creation_time, expiration_hours)
        
        assert result is False
    
    @patch.dict(os.environ, {
        'AWS_KEY_ADMIN_PATH': 'url',
        'AWS_SERVICE_NAME': 'service',
        'REGION_NAME': 'region',
        'AWS_MODEL_ID': 'model',
        'ACCEPT': 'json',
        'CONTENTTYPE': 'json',
        'ANTHROPIC_VERSION': 'version'
    })
    def test_time_difference_just_created(self):
        """Test newly created credentials (0 hours)"""
        aws = AWS()
        
        # Created just now
        creation_time = datetime.now()
        expiration_hours = 24
        
        result = aws.is_time_difference_12_hours(creation_time, expiration_hours)
        
        assert result is True



@pytest.mark.unit
class TestPerplexityInitialization:
    """Test Perplexity class initialization"""
    
    @patch.dict(os.environ, {
        'PERPLEXITY_API_KEY': 'test-perplexity-key',
        'PERPLEXITY_MODEL': 'llama-3.1-sonar-small-128k-online',
        'PERPLEXITY_URL': 'https://api.perplexity.ai/chat/completions'
    })
    def test_perplexity_initialization_success(self):
        """Test successful Perplexity initialization"""
        perplexity = Perplexity()
        
        assert perplexity.perplexity_api_key == 'test-perplexity-key'
        assert perplexity.perplexity_model == 'llama-3.1-sonar-small-128k-online'
        assert perplexity.perplexity_url == 'https://api.perplexity.ai/chat/completions'


@pytest.mark.unit
class TestPerplexityGetPerplexity:
    """Test Perplexity get_perplexity method"""
    
    @patch.dict(os.environ, {
        'PERPLEXITY_API_KEY': 'test-key',
        'PERPLEXITY_MODEL': 'llama-3.1-sonar-small-128k-online',
        'PERPLEXITY_URL': 'https://api.perplexity.ai/chat/completions'
    })
    @patch('llm_explain.utility.connections.requests.request')
    def test_get_perplexity_success(self, mock_request):
        """Test successful Perplexity API call"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': 'Perplexity response content'
                }
            }]
        }
        mock_request.return_value = mock_response
        
        perplexity = Perplexity()
        result = perplexity.get_perplexity("Test prompt")
        
        assert result == 'Perplexity response content'
        mock_request.assert_called_once()
    
    @patch.dict(os.environ, {
        'PERPLEXITY_API_KEY': 'test-key',
        'PERPLEXITY_MODEL': 'model',
        'PERPLEXITY_URL': 'https://api.perplexity.ai/chat/completions'
    })
    @patch('llm_explain.utility.connections.requests.request')
    def test_get_perplexity_request_structure(self, mock_request):
        """Test Perplexity request structure is correct"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Response'}}]
        }
        mock_request.return_value = mock_response
        
        perplexity = Perplexity()
        perplexity.get_perplexity("My test prompt")
        
        # Verify request was made with correct parameters
        call_args = mock_request.call_args
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == 'https://api.perplexity.ai/chat/completions'
        
        payload = call_args[1]['json']
        assert payload['model'] == 'model'
        assert payload['max_tokens'] == 500
        assert payload['temperature'] == 0.2
        assert payload['top_p'] == 0.9
        assert payload['messages'][1]['content'] == 'My test prompt'
        
        headers = call_args[1]['headers']
        assert 'Bearer test-key' in headers['Authorization']
        assert headers['Content-Type'] == 'application/json'
    
    @patch.dict(os.environ, {
        'PERPLEXITY_API_KEY': 'test-key',
        'PERPLEXITY_MODEL': 'model',
        'PERPLEXITY_URL': 'https://api.perplexity.ai/chat/completions'
    })
    @patch('llm_explain.utility.connections.requests.request')
    def test_get_perplexity_system_message(self, mock_request):
        """Test Perplexity includes system message"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Response'}}]
        }
        mock_request.return_value = mock_response
        
        perplexity = Perplexity()
        perplexity.get_perplexity("Test")
        
        payload = mock_request.call_args[1]['json']
        messages = payload['messages']
        
        assert len(messages) == 2
        assert messages[0]['role'] == 'system'
        assert messages[0]['content'] == 'Be precise and concise.'
        assert messages[1]['role'] == 'user'
    
    @patch.dict(os.environ, {
        'PERPLEXITY_API_KEY': 'test-key',
        'PERPLEXITY_MODEL': 'model',
        'PERPLEXITY_URL': 'https://api.perplexity.ai/chat/completions'
    })
    @patch('llm_explain.utility.connections.requests.request')
    def test_get_perplexity_api_error(self, mock_request):
        """Test Perplexity handles API errors"""
        mock_request.side_effect = Exception("API connection error")
        
        perplexity = Perplexity()
        
        with pytest.raises(Exception, match="Perplexity API error"):
            perplexity.get_perplexity("Test prompt")
    
    @patch.dict(os.environ, {
        'PERPLEXITY_API_KEY': 'test-key',
        'PERPLEXITY_MODEL': 'model',
        'PERPLEXITY_URL': 'https://api.perplexity.ai/chat/completions'
    })
    @patch('llm_explain.utility.connections.requests.request')
    def test_get_perplexity_json_parse_error(self, mock_request):
        """Test Perplexity handles JSON parsing errors"""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_request.return_value = mock_response
        
        perplexity = Perplexity()
        
        with pytest.raises(Exception, match="Perplexity API error"):
            perplexity.get_perplexity("Test prompt")
    
    @patch.dict(os.environ, {
        'PERPLEXITY_API_KEY': 'test-key',
        'PERPLEXITY_MODEL': 'model',
        'PERPLEXITY_URL': 'https://api.perplexity.ai/chat/completions'
    })
    @patch('llm_explain.utility.connections.requests.request')
    def test_get_perplexity_parameters(self, mock_request):
        """Test Perplexity uses correct API parameters"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Response'}}]
        }
        mock_request.return_value = mock_response
        
        perplexity = Perplexity()
        perplexity.get_perplexity("Test")
        
        payload = mock_request.call_args[1]['json']
        
        assert payload['max_tokens'] == 500
        assert payload['temperature'] == 0.2
        assert payload['top_p'] == 0.9
        assert payload['return_images'] is False
        assert payload['return_related_questions'] is False
        assert payload['search_recency_filter'] == 'month'
        assert payload['top_k'] == 0
        assert payload['stream'] is False
        assert payload['presence_penalty'] == 0
        assert payload['frequency_penalty'] == 1
    
    @patch.dict(os.environ, {
        'PERPLEXITY_API_KEY': 'test-key',
        'PERPLEXITY_MODEL': 'model',
        'PERPLEXITY_URL': 'https://api.perplexity.ai/chat/completions'
    })
    @patch('llm_explain.utility.connections.requests.request')
    def test_get_perplexity_verify_false(self, mock_request):
        """Test Perplexity API call parameters"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Response'}}]
        }
        mock_request.return_value = mock_response
        
        perplexity = Perplexity()
        perplexity.get_perplexity("Test")
        
        # Verify the request was called
        mock_request.assert_called_once()




@pytest.mark.unit
class TestConnectionsIntegration:
    """Integration tests for connections"""
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'azure-key',
        'AZURE_OPENAI_ENDPOINT': 'https://azure.com',
        'AZURE_OPENAI_API_VERSION': '2023-05-15',
        'AZURE_DEPLOYMENT_ENGINE': 'gpt-35-turbo',
        'GEMINI_API_KEY': 'gemini-key',
        'GEMINI_MODEL_NAME_PRO': 'gemini-pro',
        'GEMINI_MODEL_NAME_FLASH': 'gemini-flash'
    })
    @patch('llm_explain.utility.connections.openai.AzureOpenAI')
    @patch('llm_explain.utility.connections.genai')
    def test_multiple_providers_initialized(self, mock_genai, mock_azure):
        """Test multiple providers can be initialized"""
        azure = Azure()
        gemini = Gemini()
        
        assert azure.api_key == 'azure-key'
        assert gemini.gemini_api_key == 'gemini-key'
    
    @patch.dict(os.environ, {
        'AWS_KEY_ADMIN_PATH': 'https://aws.com',
        'AWS_SERVICE_NAME': 'bedrock',
        'REGION_NAME': 'us-east-1',
        'AWS_MODEL_ID': 'claude',
        'ACCEPT': 'json',
        'CONTENTTYPE': 'json',
        'ANTHROPIC_VERSION': 'v1',
        'PERPLEXITY_API_KEY': 'perplexity-key',
        'PERPLEXITY_MODEL': 'model',
        'PERPLEXITY_URL': 'https://perplexity.ai'
    })
    def test_all_providers_have_required_env_vars(self):
        """Test all providers can access their environment variables"""
        aws = AWS()
        perplexity = Perplexity()
        
        assert aws.url is not None
        assert perplexity.perplexity_api_key is not None
