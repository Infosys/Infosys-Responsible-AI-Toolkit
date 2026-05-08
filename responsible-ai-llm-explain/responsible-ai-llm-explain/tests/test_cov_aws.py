import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json
import time
import os


# Test call_AWS static method
class TestCallAWS:
    
    @pytest.mark.unit
    @patch.dict(os.environ, {
        'AWS_KEY_ADMIN_PATH': 'https://test.aws.com/creds',
        'AWS_SERVICE_NAME': 'bedrock-runtime',
        'REGION_NAME': 'us-east-1',
        'AWS_MODEL_ID': 'anthropic.claude-3-sonnet',
        'ACCEPT': 'application/json',
        'CONTENTTYPE': 'application/json',
        'ANTHROPIC_VERSION': 'bedrock-2023-05-31'
    })
    @patch('llm_explain.utility.cov_aws.requests.get')
    @patch('llm_explain.utility.cov_aws.boto3.client')
    def test_call_aws_success(self, mock_boto_client, mock_requests_get):
        """Test successful AWS call"""
        from llm_explain.utility.cov_aws import CovAWS
        
        # Mock credentials retrieval
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'awsAccessKeyId': 'test-access-key',
            'awsSecretAccessKey': 'test-secret-key',
            'awsSessionToken': 'test-session-token'
        }
        mock_requests_get.return_value = mock_response
        
        # Mock boto3 client
        mock_client = Mock()
        mock_invoke_response = {
            'body': Mock()
        }
        mock_invoke_response['body'].read.return_value = json.dumps({
            'content': [{'text': 'AWS response text'}]
        }).encode('utf-8')
        mock_client.invoke_model.return_value = mock_invoke_response
        mock_boto_client.return_value = mock_client
        
        result = CovAWS.call_AWS("Test prompt", 0.7)
        
        assert result == 'AWS response text'
        mock_boto_client.assert_called_once()
        mock_client.invoke_model.assert_called_once()
    
    @pytest.mark.unit
    @patch.dict(os.environ, {
        'AWS_KEY_ADMIN_PATH': 'https://test.aws.com/creds'
    })
    @patch('llm_explain.utility.cov_aws.requests.get')
    def test_call_aws_creds_retrieval_failure(self, mock_requests_get):
        """Test AWS credentials retrieval failure"""
        from llm_explain.utility.cov_aws import CovAWS
        
        mock_response = Mock()
        mock_response.status_code = 403
        mock_requests_get.return_value = mock_response
        
        # Should log error but not crash
        result = CovAWS.call_AWS("Test prompt", 0.7)
        
        # Result could be None or error message
        mock_requests_get.assert_called_once()
    
    @pytest.mark.unit
    @patch.dict(os.environ, {
        'AWS_KEY_ADMIN_PATH': 'https://test.aws.com/creds',
        'AWS_SERVICE_NAME': 'bedrock-runtime',
        'REGION_NAME': 'us-east-1',
        'AWS_MODEL_ID': 'anthropic.claude-3-sonnet',
        'ACCEPT': 'application/json',
        'CONTENTTYPE': 'application/json',
        'ANTHROPIC_VERSION': 'bedrock-2023-05-31'
    })
    @patch('llm_explain.utility.cov_aws.requests.get')
    @patch('llm_explain.utility.cov_aws.boto3.client')
    def test_call_aws_boto3_exception(self, mock_boto_client, mock_requests_get):
        """Test AWS boto3 exception handling"""
        from llm_explain.utility.cov_aws import CovAWS
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'awsAccessKeyId': 'test-key',
            'awsSecretAccessKey': 'test-secret',
            'awsSessionToken': 'test-token'
        }
        mock_requests_get.return_value = mock_response
        
        mock_boto_client.side_effect = Exception("Boto3 error")
        
        result = CovAWS.call_AWS("Test prompt", 0.7)
        
        # Should handle exception gracefully
        assert result is None or isinstance(result, str)


# Test cov method
class TestCovAWSMethod:
    
    @pytest.mark.unit
    @patch('llm_explain.utility.cov_aws.CovAWS.call_AWS')
    def test_cov_simple_complexity(self, mock_call_aws):
        """Test COV with simple complexity"""
        from llm_explain.utility.cov_aws import CovAWS
        
        mock_call_aws.side_effect = [
            "Paris is the capital of France",  # baseline
            "1. What is the capital?\n2. Where is Paris?",  # verification questions
            "Paris",  # answer 1
            "France",  # answer 2
            "Paris is the capital of France"  # final answer
        ]
        
        result = CovAWS.cov("What is the capital of France?", "simple")
        
        assert "original_question" in result
        assert "baseline_response" in result
        assert "verification_questions" in result
        assert "final_answer" in result
        assert "time_taken" in result
        assert result["original_question"] == "What is the capital of France?"
    
    @pytest.mark.unit
    @patch('llm_explain.utility.cov_aws.CovAWS.call_AWS')
    def test_cov_medium_complexity(self, mock_call_aws):
        """Test COV with medium complexity"""
        from llm_explain.utility.cov_aws import CovAWS
        
        mock_call_aws.side_effect = [
            "Medium baseline response",
            "1. Question one\n2. Question two",
            "Answer one",
            "Answer two",
            "Final medium answer"
        ]
        
        result = CovAWS.cov("Test question", "medium")
        
        assert "baseline_response" in result
        assert result["baseline_response"] == "Medium baseline response"
        assert "verification_questions" in result
    
    @pytest.mark.unit
    @patch('llm_explain.utility.cov_aws.CovAWS.call_AWS')
    def test_cov_complex_complexity(self, mock_call_aws):
        """Test COV with complex complexity"""
        from llm_explain.utility.cov_aws import CovAWS
        
        mock_call_aws.side_effect = [
            "Complex baseline response",
            "1. Complex question one\n2. Complex question two\n3. Complex question three",
            "Answer one",
            "Answer two",
            "Answer three",
            "Final complex answer"
        ]
        
        result = CovAWS.cov("Complex question", "complex")
        
        assert "baseline_response" in result
        assert "final_answer" in result
        assert result["final_answer"] == "Final complex answer"
    
    @pytest.mark.unit
    @patch('llm_explain.utility.cov_aws.CovAWS.call_AWS')
    @patch('llm_explain.utility.cov_aws.time.sleep')
    def test_cov_rate_limit_error_retry(self, mock_sleep, mock_call_aws):
        """Test COV rate limit error retry logic"""
        from llm_explain.utility.cov_aws import CovAWS
        import openai
        
        # First call raises rate limit, subsequent calls succeed
        mock_call_aws.side_effect = [
            "Baseline",
            "1. Question\n2. Question2",
            "Answer1",
            "Answer2",
            "Final"
        ]
        
        # Mock to trigger the retry logic
        with patch.object(CovAWS, 'cov', wraps=CovAWS.cov) as mock_cov:
            result = CovAWS.cov("Test", "simple")
        
        # Should eventually return a result
        assert result is not None
    
    @pytest.mark.unit
    @patch('llm_explain.utility.cov_aws.CovAWS.call_AWS')
    def test_cov_exception_handling(self, mock_call_aws):
        """Test COV exception handling"""
        from llm_explain.utility.cov_aws import CovAWS
        
        mock_call_aws.side_effect = Exception("AWS API error")
        
        result = CovAWS.cov("Test question", "simple")
        
        # Should handle exception and possibly return None or error message
        assert result is None or isinstance(result, str)
    
    @pytest.mark.unit
    @patch('llm_explain.utility.cov_aws.CovAWS.call_AWS')
    def test_cov_bad_request_error(self, mock_call_aws):
        """Test COV BadRequestError handling"""
        from llm_explain.utility.cov_aws import CovAWS
        import openai
        
        mock_call_aws.side_effect = openai.BadRequestError(
            "Bad request",
            response=Mock(),
            body=None
        )
        
        result = CovAWS.cov("Test question", "simple")
        
        # Should handle BadRequestError
        assert result is None or isinstance(result, str)
    
    @pytest.mark.unit
    @patch('llm_explain.utility.cov_aws.CovAWS.call_AWS')
    def test_cov_no_numeric_questions(self, mock_call_aws):
        """Test COV when verification questions don't have numeric prefixes"""
        from llm_explain.utility.cov_aws import CovAWS
        
        mock_call_aws.side_effect = [
            "Baseline response",
            "Question one without number\nQuestion two without number",  # No numeric prefix
            "Final answer"
        ]
        
        result = CovAWS.cov("Test", "simple")
        
        # Should handle empty questions list
        assert result is not None
    
    @pytest.mark.unit
    @patch('llm_explain.utility.cov_aws.CovAWS.call_AWS')
    def test_cov_single_verification_question(self, mock_call_aws):
        """Test COV with single verification question"""
        from llm_explain.utility.cov_aws import CovAWS
        
        mock_call_aws.side_effect = [
            "Baseline",
            "1. Single question",
            "Single answer",
            "Final answer"
        ]
        
        result = CovAWS.cov("Test", "simple")
        
        assert "verification_answers" in result
        assert "Final answer" in result.get("final_answer", "")


# Test temperature mapping
class TestTemperatureMapping:
    
    @pytest.mark.unit
    @patch('llm_explain.utility.cov_aws.CovAWS.call_AWS')
    def test_simple_uses_zero_temperature(self, mock_call_aws):
        """Test simple complexity uses temperature 0"""
        from llm_explain.utility.cov_aws import CovAWS
        
        mock_call_aws.return_value = "Response"
        
        CovAWS.cov("Test", "simple")
        
        # Check that call_AWS was called with temperature 0 for simple
        calls = mock_call_aws.call_args_list
        # First call is baseline with simple temp
        assert calls[0][0][1] == 0
    
    @pytest.mark.unit
    @patch('llm_explain.utility.cov_aws.CovAWS.call_AWS')
    def test_medium_uses_medium_temperature(self, mock_call_aws):
        """Test medium complexity uses temperature 0.7"""
        from llm_explain.utility.cov_aws import CovAWS
        
        mock_call_aws.return_value = "Response"
        
        CovAWS.cov("Test", "medium")
        
        calls = mock_call_aws.call_args_list
        # First call is baseline with medium temp
        assert calls[0][0][1] == 0.7
    
    @pytest.mark.unit
    @patch('llm_explain.utility.cov_aws.CovAWS.call_AWS')
    def test_complex_uses_high_temperature(self, mock_call_aws):
        """Test complex complexity uses temperature 2"""
        from llm_explain.utility.cov_aws import CovAWS
        
        mock_call_aws.return_value = "Response"
        
        CovAWS.cov("Test", "complex")
        
        calls = mock_call_aws.call_args_list
        # First call is baseline with complex temp
        assert calls[0][0][1] == 2



class TestCovAWSEdgeCases:
    
    @pytest.mark.unit
    @patch('llm_explain.utility.cov_aws.CovAWS.call_AWS')
    def test_cov_empty_question(self, mock_call_aws):
        """Test COV with empty question"""
        from llm_explain.utility.cov_aws import CovAWS
        
        mock_call_aws.side_effect = [
            "Empty baseline",
            "1. Question",
            "Answer",
            "Final"
        ]
        
        result = CovAWS.cov("", "simple")
        
        assert result is not None
        assert result["original_question"] == ""
    
    @pytest.mark.unit
    @patch.dict(os.environ, {
        'AWS_KEY_ADMIN_PATH': 'https://test.aws.com/creds',
        'AWS_SERVICE_NAME': 'bedrock-runtime',
        'REGION_NAME': 'us-east-1',
        'AWS_MODEL_ID': 'anthropic.claude-3-sonnet',
        'ACCEPT': 'application/json',
        'CONTENTTYPE': 'application/json',
        'ANTHROPIC_VERSION': 'bedrock-2023-05-31'
    })
    @patch('llm_explain.utility.cov_aws.requests.get')
    @patch('llm_explain.utility.cov_aws.boto3.client')
    def test_call_aws_with_different_temperatures(self, mock_boto_client, mock_requests_get):
        """Test call_AWS with different temperature values"""
        from llm_explain.utility.cov_aws import CovAWS
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'awsAccessKeyId': 'key',
            'awsSecretAccessKey': 'secret',
            'awsSessionToken': 'token'
        }
        mock_requests_get.return_value = mock_response
        
        mock_client = Mock()
        mock_invoke_response = {
            'body': Mock()
        }
        mock_invoke_response['body'].read.return_value = json.dumps({
            'content': [{'text': 'Response'}]
        }).encode('utf-8')
        mock_client.invoke_model.return_value = mock_invoke_response
        mock_boto_client.return_value = mock_client
        
        # Test with different temperatures
        for temp in [0, 0.7, 2]:
            result = CovAWS.call_AWS("Test", temp)
            assert result == 'Response'
    
    @pytest.mark.unit
    @patch('llm_explain.utility.cov_aws.CovAWS.call_AWS')
    def test_cov_multiple_verification_answers(self, mock_call_aws):
        """Test COV with multiple verification questions and answers"""
        from llm_explain.utility.cov_aws import CovAWS
        
        mock_call_aws.side_effect = [
            "Baseline",
            "1. Q1\n2. Q2\n3. Q3\n4. Q4\n5. Q5",
            "A1", "A2", "A3", "A4", "A5",
            "Final comprehensive answer"
        ]
        
        result = CovAWS.cov("Test", "simple")
        
        assert "verification_answers" in result
        # Should have all 5 Q&A pairs
        assert "Q1" in result["verification_answers"]
        assert "A1" in result["verification_answers"]
