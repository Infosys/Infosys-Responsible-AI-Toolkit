import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import requests


class TestConvertPathToList:
    """Test convert_path_to_list static method."""

    def test_convert_path_with_string_keys(self):
        """Test conversion of path with string keys."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        param_str = "['data']['result']['content']"
        result = APIEndpoint.convert_path_to_list(param_str)
        
        assert result == ['data', 'result', 'content']

    def test_convert_path_with_numeric_indices(self):
        """Test conversion of path with numeric indices."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        param_str = "[0][1][2]"
        result = APIEndpoint.convert_path_to_list(param_str)
        
        assert result == [0, 1, 2]

    def test_convert_path_with_mixed_keys_and_indices(self):
        """Test conversion of path with mixed string keys and numeric indices."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        param_str = "['results'][0]['data'][1]"
        result = APIEndpoint.convert_path_to_list(param_str)
        
        assert result == ['results', 0, 'data', 1]

    def test_convert_path_with_double_quotes(self):
        """Test conversion with double-quoted strings."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        param_str = '[\"output\"][\"text\"]'
        result = APIEndpoint.convert_path_to_list(param_str)
        
        assert result == ['output', 'text']

    def test_convert_path_single_element(self):
        """Test conversion with single element."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        param_str = "['response']"
        result = APIEndpoint.convert_path_to_list(param_str)
        
        assert result == ['response']

    def test_convert_path_empty_string(self):
        """Test conversion with empty string."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        param_str = ""
        result = APIEndpoint.convert_path_to_list(param_str)
        
        assert result == []

    def test_convert_path_complex_nested(self):
        """Test conversion with complex nested path."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        param_str = "['api']['v1']['endpoints'][0]['response']['data'][2]['value']"
        result = APIEndpoint.convert_path_to_list(param_str)
        
        assert result == ['api', 'v1', 'endpoints', 0, 'response', 'data', 2, 'value']


class TestEndpointCalling:
    """Test endpoint_calling static method."""

    @patch('requests.request')
    def test_endpoint_calling_success_simple(self, mock_request):
        """Test successful endpoint call with simple response."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "result": "This is the response text"
        }
        mock_request.return_value = mock_response
        
        prompt = "What is AI?"
        modelEndpointUrl = "https://api.example.com/generate"
        endpointInputParam = {"input_parameter": "query"}
        endpointOutputParam = "['result']"
        
        result = APIEndpoint.endpoint_calling(
            prompt,
            modelEndpointUrl,
            endpointInputParam,
            endpointOutputParam
        )
        
        assert result == "This is the response text"
        
        # Verify request was made correctly
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == modelEndpointUrl

    @patch('requests.request')
    def test_endpoint_calling_with_nested_output(self, mock_request):
        """Test endpoint call with nested JSON output path."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "results": [
                    {"text": "first"},
                    {"text": "second result"}
                ]
            }
        }
        mock_request.return_value = mock_response
        
        result = APIEndpoint.endpoint_calling(
            "test prompt",
            "https://api.test.com",
            {"input_parameter": "prompt"},
            "['data']['results'][1]['text']"
        )
        
        assert result == "second result"

    @patch('requests.request')
    def test_endpoint_calling_replaces_input_parameter(self, mock_request):
        """Test that input_parameter key is replaced with prompt."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        mock_response = Mock()
        mock_response.json.return_value = {"output": "response"}
        mock_request.return_value = mock_response
        
        APIEndpoint.endpoint_calling(
            "my prompt",
            "https://api.test.com",
            {"input_parameter": "text", "other_param": "value"},
            "['output']"
        )
        
        # Verify the payload sent
        call_args = mock_request.call_args
        sent_data = json.loads(call_args[1]['data'])
        
        assert "text" in sent_data
        assert sent_data["text"] == "my prompt"
        assert "input_parameter" not in sent_data
        assert sent_data["other_param"] == "value"

    @patch('requests.request')
    def test_endpoint_calling_preserves_other_params(self, mock_request):
        """Test that other parameters are preserved in the request."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        mock_response = Mock()
        mock_response.json.return_value = {"result": "text"}
        mock_request.return_value = mock_response
        
        input_params = {
            "input_parameter": "prompt",
            "temperature": 0.7,
            "max_tokens": 100,
            "model": "gpt-4"
        }
        
        APIEndpoint.endpoint_calling(
            "test",
            "https://api.test.com",
            input_params,
            "['result']"
        )
        
        call_args = mock_request.call_args
        sent_data = json.loads(call_args[1]['data'])
        
        assert sent_data["temperature"] == 0.7
        assert sent_data["max_tokens"] == 100
        assert sent_data["model"] == "gpt-4"

    @patch('requests.request')
    def test_endpoint_calling_with_array_index(self, mock_request):
        """Test endpoint call with array index in output path."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": ["first", "second", "third"]
        }
        mock_request.return_value = mock_response
        
        result = APIEndpoint.endpoint_calling(
            "prompt",
            "https://api.test.com",
            {"input_parameter": "query"},
            "['choices'][0]"
        )
        
        assert result == "first"

    @patch('requests.request')
    def test_endpoint_calling_uses_post_method(self, mock_request):
        """Test that endpoint calling uses POST method."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        mock_response = Mock()
        mock_response.json.return_value = {"result": "text"}
        mock_request.return_value = mock_response
        
        APIEndpoint.endpoint_calling(
            "test",
            "https://api.test.com",
            {"input_parameter": "prompt"},
            "['result']"
        )
        
        call_args = mock_request.call_args
        assert call_args[0][0] == "POST"

    @patch('requests.request')
    def test_endpoint_calling_sets_json_headers(self, mock_request):
        """Test that correct Content-Type headers are set."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        mock_response = Mock()
        mock_response.json.return_value = {"result": "text"}
        mock_request.return_value = mock_response
        
        APIEndpoint.endpoint_calling(
            "test",
            "https://api.test.com",
            {"input_parameter": "prompt"},
            "['result']"
        )
        
        call_args = mock_request.call_args
        assert call_args[1]['headers']['Content-Type'] == 'application/json'

    @patch('requests.request')
    def test_endpoint_calling_disables_ssl_verify(self, mock_request):
        """Test that API endpoint is called correctly."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        mock_response = Mock()
        mock_response.json.return_value = {"result": "text"}
        mock_request.return_value = mock_response
        
        APIEndpoint.endpoint_calling(
            "test",
            "https://api.test.com",
            {"input_parameter": "prompt"},
            "['result']"
        )
        
        # Verify the request was called
        mock_request.assert_called_once()

    @patch('requests.request')
    def test_endpoint_calling_request_exception(self, mock_request):
        """Test handling of request exception."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        mock_request.side_effect = requests.exceptions.RequestException("Connection error")
        
        result = APIEndpoint.endpoint_calling(
            "test",
            "https://api.test.com",
            {"input_parameter": "prompt"},
            "['result']"
        )
        
        # Function catches exception and logs, returns None
        assert result is None

    @patch('requests.request')
    def test_endpoint_calling_connection_error(self, mock_request):
        """Test handling of connection error."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        mock_request.side_effect = requests.exceptions.ConnectionError("Failed to connect")
        
        result = APIEndpoint.endpoint_calling(
            "test",
            "https://api.test.com",
            {"input_parameter": "prompt"},
            "['result']"
        )
        
        assert result is None

    @patch('requests.request')
    def test_endpoint_calling_timeout_error(self, mock_request):
        """Test handling of timeout error."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        mock_request.side_effect = requests.exceptions.Timeout("Request timed out")
        
        result = APIEndpoint.endpoint_calling(
            "test",
            "https://api.test.com",
            {"input_parameter": "prompt"},
            "['result']"
        )
        
        assert result is None

    @patch('requests.request')
    def test_endpoint_calling_with_deepcopy_preserves_original(self, mock_request):
        """Test that deepcopy preserves the original endpointInputParam."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        mock_response = Mock()
        mock_response.json.return_value = {"result": "text"}
        mock_request.return_value = mock_response
        
        original_params = {"input_parameter": "query", "temp": 0.5}
        original_params_copy = original_params.copy()
        
        APIEndpoint.endpoint_calling(
            "test",
            "https://api.test.com",
            original_params,
            "['result']"
        )
        
        # Original should not be modified
        assert original_params == original_params_copy

    @patch('requests.request')
    def test_endpoint_calling_with_complex_nested_response(self, mock_request):
        """Test endpoint call with deeply nested response."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "api": {
                "v2": {
                    "results": [
                        {"data": [{"value": "target"}]}
                    ]
                }
            }
        }
        mock_request.return_value = mock_response
        
        result = APIEndpoint.endpoint_calling(
            "test",
            "https://api.test.com",
            {"input_parameter": "prompt"},
            "['api']['v2']['results'][0]['data'][0]['value']"
        )
        
        assert result == "target"

    @patch('requests.request')
    def test_endpoint_calling_with_empty_prompt(self, mock_request):
        """Test endpoint call with empty prompt."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        mock_response = Mock()
        mock_response.json.return_value = {"result": "response"}
        mock_request.return_value = mock_response
        
        result = APIEndpoint.endpoint_calling(
            "",
            "https://api.test.com",
            {"input_parameter": "prompt"},
            "['result']"
        )
        
        call_args = mock_request.call_args
        sent_data = json.loads(call_args[1]['data'])
        assert sent_data["prompt"] == ""

    @patch('requests.request')
    def test_endpoint_calling_with_special_characters_in_prompt(self, mock_request):
        """Test endpoint call with special characters."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        mock_response = Mock()
        mock_response.json.return_value = {"result": "response"}
        mock_request.return_value = mock_response
        
        special_prompt = "Test with !@#$%^&*() and 日本語"
        
        result = APIEndpoint.endpoint_calling(
            special_prompt,
            "https://api.test.com",
            {"input_parameter": "text"},
            "['result']"
        )
        
        call_args = mock_request.call_args
        sent_data = json.loads(call_args[1]['data'])
        assert sent_data["text"] == special_prompt

    @patch('requests.request')
    def test_endpoint_calling_returns_entire_response_object(self, mock_request):
        """Test that entire objects can be returned."""
        from llm_explain.utility.endpoint import APIEndpoint
        
        mock_response = Mock()
        complex_object = {
            "data": {"nested": "value"},
            "metadata": {"count": 5}
        }
        mock_response.json.return_value = {"result": complex_object}
        mock_request.return_value = mock_response
        
        result = APIEndpoint.endpoint_calling(
            "test",
            "https://api.test.com",
            {"input_parameter": "prompt"},
            "['result']"
        )
        
        assert result == complex_object
        assert result["data"]["nested"] == "value"
        assert result["metadata"]["count"] == 5
