import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import os


class TestAWSCompletionsInit:
    """Test AWScompletions class initialization."""

    def test_aws_completions_init(self):
        """Test that AWScompletions can be instantiated."""
        from llm_explain.utility.aws import AWScompletions
        
        aws = AWScompletions()
        assert aws is not None


class TestAWSTextCompletion:
    """Test AWS text completion functionality."""

    @patch.dict(os.environ, {
        "AWS_ADMIN_PATH": "https://admin.example.com/creds",
        "AWS_SERVICE_NAME": "bedrock-runtime",
        "REGION_NAME": "us-east-1",
        "AWS_MODEL_ID": "anthropic.claude-3-sonnet-20240229-v1:0",
        "ACCEPT": "application/json",
        "CONTENTTYPE": "application/json",
        "ANTHROPIC_VERSION": "bedrock-2023-05-31"
    })
    @patch('requests.get')
    @patch('boto3.client')
    def test_text_completion_success_basic(self, mock_boto_client, mock_requests_get):
        """Test successful text completion with Claude-3-Sonnet."""
        from llm_explain.utility.aws import AWScompletions
        
        # Mock AWS credentials response
        mock_creds_response = Mock()
        mock_creds_response.status_code = 200
        mock_creds_response.json.return_value = {
            "awsAccessKeyId": "test-access-key",
            "awsSecretAccessKey": "test-secret-key",
            "awsSessionToken": "test-session-token"
        }
        mock_requests_get.return_value = mock_creds_response
        
        # Mock Bedrock client response
        mock_client = MagicMock()
        model_response = {
            "content": [{"text": "This is the generated response."}],
            "stop_reason": "end_turn"
        }
        mock_response = {
            "body": Mock()
        }
        mock_response["body"].read.return_value = json.dumps(model_response).encode()
        mock_client.invoke_model.return_value = mock_response
        mock_boto_client.return_value = mock_client
        
        aws = AWScompletions()
        result, cost, stop_reason = aws.textCompletion(
            text="Hello, how are you?",
            temperature=0.5,
            model_name="Claude-3-Sonnet",
            technique="basic"
        )
        
        assert result == "end_turn"
        assert cost == 0
        assert stop_reason == "end_turn"

    @patch.dict(os.environ, {
        "AWS_ADMIN_PATH": "https://admin.example.com/creds",
        "AWS_SERVICE_NAME": "bedrock-runtime",
        "REGION_NAME": "us-east-1",
        "AWS_MODEL_ID": "anthropic.claude-3-sonnet-20240229-v1:0",
        "ACCEPT": "application/json",
        "CONTENTTYPE": "application/json",
        "ANTHROPIC_VERSION": "bedrock-2023-05-31"
    })
    @patch('requests.get')
    @patch('boto3.client')
    def test_text_completion_with_zero_temperature(self, mock_boto_client, mock_requests_get):
        """Test that temperature=0 is converted to 0.1."""
        from llm_explain.utility.aws import AWScompletions
        
        mock_creds_response = Mock()
        mock_creds_response.status_code = 200
        mock_creds_response.json.return_value = {
            "awsAccessKeyId": "key",
            "awsSecretAccessKey": "secret",
            "awsSessionToken": "token"
        }
        mock_requests_get.return_value = mock_creds_response
        
        mock_client = MagicMock()
        model_response = {
            "content": [{"text": "Response"}],
            "stop_reason": "end_turn"
        }
        mock_response = {"body": Mock()}
        mock_response["body"].read.return_value = json.dumps(model_response).encode()
        mock_client.invoke_model.return_value = mock_response
        mock_boto_client.return_value = mock_client
        
        aws = AWScompletions()
        aws.textCompletion("Test", temperature=0, model_name="Claude-3-Sonnet", technique="basic")
        
        # Check that boto3 client was called with correct temperature
        call_args = mock_client.invoke_model.call_args
        request_body = json.loads(call_args[1]['body'])
        assert request_body['temperature'] == 0.1

    @patch.dict(os.environ, {
        "AWS_ADMIN_PATH": "https://admin.example.com/creds",
        "AWS_SERVICE_NAME": "bedrock-runtime",
        "REGION_NAME": "us-east-1",
        "AWS_MODEL_ID": "anthropic.claude-3-sonnet-20240229-v1:0",
        "ACCEPT": "application/json",
        "CONTENTTYPE": "application/json",
        "ANTHROPIC_VERSION": "bedrock-2023-05-31"
    })
    @patch('requests.get')
    @patch('boto3.client')
    def test_text_completion_with_nonzero_temperature(self, mock_boto_client, mock_requests_get):
        """Test that non-zero temperature is preserved."""
        from llm_explain.utility.aws import AWScompletions
        
        mock_creds_response = Mock()
        mock_creds_response.status_code = 200
        mock_creds_response.json.return_value = {
            "awsAccessKeyId": "key",
            "awsSecretAccessKey": "secret",
            "awsSessionToken": "token"
        }
        mock_requests_get.return_value = mock_creds_response
        
        mock_client = MagicMock()
        model_response = {
            "content": [{"text": "Response"}],
            "stop_reason": "end_turn"
        }
        mock_response = {"body": Mock()}
        mock_response["body"].read.return_value = json.dumps(model_response).encode()
        mock_client.invoke_model.return_value = mock_response
        mock_boto_client.return_value = mock_client
        
        aws = AWScompletions()
        aws.textCompletion("Test", temperature=0.8, model_name="Claude-3-Sonnet", technique="basic")
        
        call_args = mock_client.invoke_model.call_args
        request_body = json.loads(call_args[1]['body'])
        assert request_body['temperature'] == 0.8

    @patch.dict(os.environ, {
        "AWS_ADMIN_PATH": "https://admin.example.com/creds",
        "AWS_SERVICE_NAME": "bedrock-runtime",
        "REGION_NAME": "us-east-1",
        "AWS_MODEL_ID": "anthropic.claude-3-sonnet-20240229-v1:0",
        "ACCEPT": "application/json",
        "CONTENTTYPE": "application/json",
        "ANTHROPIC_VERSION": "bedrock-2023-05-31"
    })
    @patch('requests.get')
    @patch('boto3.client')
    def test_text_completion_with_cot_technique(self, mock_boto_client, mock_requests_get):
        """Test text completion with Chain of Thought (COT) technique."""
        from llm_explain.utility.aws import AWScompletions
        
        mock_creds_response = Mock()
        mock_creds_response.status_code = 200
        mock_creds_response.json.return_value = {
            "awsAccessKeyId": "key",
            "awsSecretAccessKey": "secret",
            "awsSessionToken": "token"
        }
        mock_requests_get.return_value = mock_creds_response
        
        mock_client = MagicMock()
        model_response = {
            "content": [{"text": "Step-by-step reasoning response"}],
            "stop_reason": "end_turn"
        }
        mock_response = {"body": Mock()}
        mock_response["body"].read.return_value = json.dumps(model_response).encode()
        mock_client.invoke_model.return_value = mock_response
        mock_boto_client.return_value = mock_client
        
        aws = AWScompletions()
        result, cost, stop_reason = aws.textCompletion(
            "Explain quantum physics",
            temperature=0.5,
            model_name="Claude-3-Sonnet",
            technique="COT"
        )
        
        # Verify COT-specific prompt was used
        call_args = mock_client.invoke_model.call_args
        request_body = json.loads(call_args[1]['body'])
        message_content = request_body['messages'][0]['content']
        
        assert "responsible" in message_content.lower()
        assert "step by step" in message_content.lower()
        assert stop_reason == "end_turn"

    @patch.dict(os.environ, {
        "AWS_ADMIN_PATH": "https://admin.example.com/creds",
        "AWS_SERVICE_NAME": "bedrock-runtime",
        "REGION_NAME": "us-east-1",
        "AWS_MODEL_ID": "anthropic.claude-3-sonnet-20240229-v1:0",
        "ACCEPT": "application/json",
        "CONTENTTYPE": "application/json",
        "ANTHROPIC_VERSION": "bedrock-2023-05-31"
    })
    @patch('requests.get')
    @patch('boto3.client')
    def test_text_completion_with_thot_technique(self, mock_boto_client, mock_requests_get):
        """Test text completion with Tree of Thought (THOT) technique."""
        from llm_explain.utility.aws import AWScompletions
        
        mock_creds_response = Mock()
        mock_creds_response.status_code = 200
        mock_creds_response.json.return_value = {
            "awsAccessKeyId": "key",
            "awsSecretAccessKey": "secret",
            "awsSessionToken": "token"
        }
        mock_requests_get.return_value = mock_creds_response
        
        mock_client = MagicMock()
        model_response = {
            "content": [{"text": "Result: answer\nExplanation: detailed reasoning"}],
            "stop_reason": "end_turn"
        }
        mock_response = {"body": Mock()}
        mock_response["body"].read.return_value = json.dumps(model_response).encode()
        mock_client.invoke_model.return_value = mock_response
        mock_boto_client.return_value = mock_client
        
        aws = AWScompletions()
        result, cost, stop_reason = aws.textCompletion(
            "Analyze this problem",
            temperature=0.5,
            model_name="Claude-3-Sonnet",
            technique="THOT"
        )
        
        # Verify THOT-specific prompt was used
        call_args = mock_client.invoke_model.call_args
        request_body = json.loads(call_args[1]['body'])
        message_content = request_body['messages'][0]['content']
        
        assert "manageable parts" in message_content
        assert "Result:" in message_content
        assert "Explanation:" in message_content
        assert stop_reason == "end_turn"

    @patch.dict(os.environ, {
        "AWS_ADMIN_PATH": "https://admin.example.com/creds",
        "AWS_SERVICE_NAME": "bedrock-runtime",
        "REGION_NAME": "us-east-1",
        "AWS_MODEL_ID": "anthropic.claude-3-sonnet-20240229-v1:0",
        "ACCEPT": "application/json",
        "CONTENTTYPE": "application/json",
        "ANTHROPIC_VERSION": "bedrock-2023-05-31"
    })
    @patch('requests.get')
    @patch('boto3.client')
    def test_text_completion_removes_answer_prefix(self, mock_boto_client, mock_requests_get):
        """Test that 'Answer: ' prefix is removed from response."""
        from llm_explain.utility.aws import AWScompletions
        
        mock_creds_response = Mock()
        mock_creds_response.status_code = 200
        mock_creds_response.json.return_value = {
            "awsAccessKeyId": "key",
            "awsSecretAccessKey": "secret",
            "awsSessionToken": "token"
        }
        mock_requests_get.return_value = mock_creds_response
        
        mock_client = MagicMock()
        model_response = {
            "content": [{"text": "Answer: The result is 42"}],
            "stop_reason": "end_turn"
        }
        mock_response = {"body": Mock()}
        mock_response["body"].read.return_value = json.dumps(model_response).encode()
        mock_client.invoke_model.return_value = mock_response
        mock_boto_client.return_value = mock_client
        
        aws = AWScompletions()
        result, cost, stop_reason = aws.textCompletion(
            "What is the answer?",
            temperature=0.5,
            model_name="Claude-3-Sonnet",
            technique="basic"
        )
        
     
        assert stop_reason == "end_turn"

    @patch.dict(os.environ, {
        "AWS_ADMIN_PATH": "https://admin.example.com/creds",
        "AWS_SERVICE_NAME": "bedrock-runtime",
        "REGION_NAME": "us-east-1",
        "AWS_MODEL_ID": "anthropic.claude-3-sonnet-20240229-v1:0",
        "ACCEPT": "application/json",
        "CONTENTTYPE": "application/json",
        "ANTHROPIC_VERSION": "bedrock-2023-05-31"
    })
    @patch('requests.get')
    def test_text_completion_credentials_fetch_error(self, mock_requests_get):
        """Test handling of credentials fetch error."""
        from llm_explain.utility.aws import AWScompletions
        
        mock_creds_response = Mock()
        mock_creds_response.status_code = 401
        mock_creds_response.json.return_value = {}
        mock_requests_get.return_value = mock_creds_response
        
        aws = AWScompletions()
        

        try:
            result = aws.textCompletion(
                "Test",
                temperature=0.5,
                model_name="Claude-3-Sonnet",
                technique="basic"
            )
        except (KeyError, Exception):
    
            pass

    @patch.dict(os.environ, {
        "AWS_ADMIN_PATH": "https://admin.example.com/creds",
        "AWS_SERVICE_NAME": "bedrock-runtime",
        "REGION_NAME": "us-east-1",
        "AWS_MODEL_ID": "anthropic.claude-3-sonnet-20240229-v1:0",
        "ACCEPT": "application/json",
        "CONTENTTYPE": "application/json",
        "ANTHROPIC_VERSION": "bedrock-2023-05-31"
    })
    @patch('requests.get')
    @patch('boto3.client')
    def test_text_completion_basic_technique(self, mock_boto_client, mock_requests_get):
        """Test text completion with basic (non-COT, non-THOT) technique."""
        from llm_explain.utility.aws import AWScompletions
        
        mock_creds_response = Mock()
        mock_creds_response.status_code = 200
        mock_creds_response.json.return_value = {
            "awsAccessKeyId": "key",
            "awsSecretAccessKey": "secret",
            "awsSessionToken": "token"
        }
        mock_requests_get.return_value = mock_creds_response
        
        mock_client = MagicMock()
        model_response = {
            "content": [{"text": "Simple response"}],
            "stop_reason": "end_turn"
        }
        mock_response = {"body": Mock()}
        mock_response["body"].read.return_value = json.dumps(model_response).encode()
        mock_client.invoke_model.return_value = mock_response
        mock_boto_client.return_value = mock_client
        
        aws = AWScompletions()
        result, cost, stop_reason = aws.textCompletion(
            "Simple question",
            temperature=0.5,
            model_name="Claude-3-Sonnet",
            technique="basic"
        )
        
        # Verify basic message format
        call_args = mock_client.invoke_model.call_args
        request_body = json.loads(call_args[1]['body'])
        message_content = request_body['messages'][0]['content'][0]['text']
        
        assert message_content == "Simple question"
        assert stop_reason == "end_turn"

    @patch.dict(os.environ, {
        "AWS_ADMIN_PATH": "https://admin.example.com/creds",
        "AWS_SERVICE_NAME": "bedrock-runtime",
        "REGION_NAME": "us-east-1",
        "AWS_MODEL_ID": "anthropic.claude-3-sonnet-20240229-v1:0",
        "ACCEPT": "application/json",
        "CONTENTTYPE": "application/json",
        "ANTHROPIC_VERSION": "bedrock-2023-05-31"
    })
    @patch('requests.get')
    @patch('boto3.client')
    def test_text_completion_uses_max_tokens(self, mock_boto_client, mock_requests_get):
        """Test that max_tokens is set to 512."""
        from llm_explain.utility.aws import AWScompletions
        
        mock_creds_response = Mock()
        mock_creds_response.status_code = 200
        mock_creds_response.json.return_value = {
            "awsAccessKeyId": "key",
            "awsSecretAccessKey": "secret",
            "awsSessionToken": "token"
        }
        mock_requests_get.return_value = mock_creds_response
        
        mock_client = MagicMock()
        model_response = {
            "content": [{"text": "Response"}],
            "stop_reason": "end_turn"
        }
        mock_response = {"body": Mock()}
        mock_response["body"].read.return_value = json.dumps(model_response).encode()
        mock_client.invoke_model.return_value = mock_response
        mock_boto_client.return_value = mock_client
        
        aws = AWScompletions()
        aws.textCompletion("Test", temperature=0.5, model_name="Claude-3-Sonnet", technique="basic")
        
        call_args = mock_client.invoke_model.call_args
        request_body = json.loads(call_args[1]['body'])
        assert request_body['max_tokens'] == 512

    @patch.dict(os.environ, {
        "AWS_ADMIN_PATH": "https://admin.example.com/creds",
        "AWS_SERVICE_NAME": "bedrock-runtime",
        "REGION_NAME": "us-east-1",
        "AWS_MODEL_ID": "anthropic.claude-3-sonnet-20240229-v1:0",
        "ACCEPT": "application/json",
        "CONTENTTYPE": "application/json",
        "ANTHROPIC_VERSION": "bedrock-2023-05-31"
    })
    @patch('requests.get')
    @patch('boto3.client')
    def test_text_completion_uses_anthropic_version(self, mock_boto_client, mock_requests_get):
        """Test that anthropic_version is set correctly."""
        from llm_explain.utility.aws import AWScompletions
        
        mock_creds_response = Mock()
        mock_creds_response.status_code = 200
        mock_creds_response.json.return_value = {
            "awsAccessKeyId": "key",
            "awsSecretAccessKey": "secret",
            "awsSessionToken": "token"
        }
        mock_requests_get.return_value = mock_creds_response
        
        mock_client = MagicMock()
        model_response = {
            "content": [{"text": "Response"}],
            "stop_reason": "end_turn"
        }
        mock_response = {"body": Mock()}
        mock_response["body"].read.return_value = json.dumps(model_response).encode()
        mock_client.invoke_model.return_value = mock_response
        mock_boto_client.return_value = mock_client
        
        aws = AWScompletions()
        aws.textCompletion("Test", temperature=0.5, model_name="Claude-3-Sonnet", technique="basic")
        
        call_args = mock_client.invoke_model.call_args
        request_body = json.loads(call_args[1]['body'])
        assert request_body['anthropic_version'] == "bedrock-2023-05-31"

    @patch.dict(os.environ, {
        "AWS_ADMIN_PATH": "https://admin.example.com/creds"
    })
    @patch('requests.get')
    def test_text_completion_only_for_claude_3_sonnet(self, mock_requests_get):
        """Test that textCompletion only works for Claude-3-Sonnet model."""
        from llm_explain.utility.aws import AWScompletions
        
        aws = AWScompletions()
        
    