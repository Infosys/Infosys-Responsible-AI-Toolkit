import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from llm_explain.utility.llama import Llamacompletion


@pytest.mark.unit
class TestLlamacompletionInit:
    """Test Llamacompletion initialization"""
    
    def test_init_with_endpoint(self):
        """Test initialization with LLAMA_ENDPOINT set"""
        with patch.dict(os.environ, {'LLAMA_ENDPOINT': 'http://test.endpoint'}):
            llama = Llamacompletion()
            assert llama.url == 'http://test.endpoint'
    
    def test_init_without_endpoint(self):
        """Test initialization without LLAMA_ENDPOINT"""
        with patch.dict(os.environ, {}, clear=True):
            llama = Llamacompletion()
            assert llama.url is None


@pytest.mark.unit
class TestLlamacompletionTHOT:
    """Test textCompletion with THOT technique"""
    
    def test_text_completion_thot(self):
        """Test textCompletion with THOT technique"""
        with patch.dict(os.environ, {'LLAMA_ENDPOINT': 'http://test.endpoint'}):
            with patch('llm_explain.utility.llama.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = [{
                    'generated_text': 'Some text[/INST]Generated answer with explanation'
                }]
                mock_post.return_value = mock_response
                
                llama = Llamacompletion()
                result = llama.textCompletion("What is AI?", "THOT")
                
                assert result[0] == 'Generated answer with explanation'
                assert result[1] == 0
                assert result[2] == ""
                assert result[3] == "0"
                mock_post.assert_called_once()
    
    def test_text_completion_thot_request_params(self):
        """Test textCompletion THOT sends correct request parameters"""
        with patch.dict(os.environ, {'LLAMA_ENDPOINT': 'http://test.endpoint'}):
            with patch('llm_explain.utility.llama.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = [{
                    'generated_text': 'Test[/INST]Answer'
                }]
                mock_post.return_value = mock_response
                
                llama = Llamacompletion()
                llama.textCompletion("Test question", "THOT")
                
                # Check request parameters
                call_args = mock_post.call_args
                assert call_args[0][0] == 'http://test.endpoint'
                json_data = call_args[1]['json']
                assert 'inputs' in json_data
                assert 'parameters' in json_data
                assert json_data['parameters']['max_new_tokens'] == 512
                assert json_data['parameters']['temperature'] == 0.1


@pytest.mark.unit
class TestLlamacompletionRereadTHOT:
    """Test textCompletion with Reread THOT technique"""
    
    def test_text_completion_reread_thot(self):
        """Test textCompletion with Reread THOT technique"""
        with patch.dict(os.environ, {'LLAMA_ENDPOINT': 'http://test.endpoint'}):
            with patch('llm_explain.utility.llama.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = [{
                    'generated_text': 'Prompt[/INST]Detailed answer with reread'
                }]
                mock_post.return_value = mock_response
                
                llama = Llamacompletion()
                result = llama.textCompletion("Explain quantum physics", "Reread THOT")
                
                assert result[0] == 'Detailed answer with reread'
                assert result[1] == 0
                # Verify the prompt contains "Read the question again"
                call_args = mock_post.call_args
                json_data = call_args[1]['json']
                assert 'Read the question again' in json_data['inputs']
    
    def test_text_completion_reread_thot_double_question(self):
        """Test Reread THOT includes question twice"""
        with patch.dict(os.environ, {'LLAMA_ENDPOINT': 'http://test.endpoint'}):
            with patch('llm_explain.utility.llama.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = [{
                    'generated_text': 'X[/INST]Y'
                }]
                mock_post.return_value = mock_response
                
                llama = Llamacompletion()
                question = "What is machine learning?"
                llama.textCompletion(question, "Reread THOT")
                
                call_args = mock_post.call_args
                json_data = call_args[1]['json']
                # Question should appear twice in the prompt
                assert json_data['inputs'].count(question) == 2


@pytest.mark.unit
class TestLlamacompletionCOT:
    """Test textCompletion with COT technique"""
    
    def test_text_completion_cot(self):
        """Test textCompletion with COT technique"""
        with patch.dict(os.environ, {'LLAMA_ENDPOINT': 'http://test.endpoint'}):
            with patch('llm_explain.utility.llama.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = [{
                    'generated_text': 'Question[/INST]Step by step answer'
                }]
                mock_post.return_value = mock_response
                
                llama = Llamacompletion()
                result = llama.textCompletion("Solve this problem", "COT")
                
                assert result[0] == 'Step by step answer'
                assert result[1] == 0
    
    def test_text_completion_cot_prompt_format(self):
        """Test COT technique has correct prompt format"""
        with patch.dict(os.environ, {'LLAMA_ENDPOINT': 'http://test.endpoint'}):
            with patch('llm_explain.utility.llama.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = [{
                    'generated_text': 'X[/INST]Y'
                }]
                mock_post.return_value = mock_response
                
                llama = Llamacompletion()
                llama.textCompletion("Test", "COT")
                
                call_args = mock_post.call_args
                json_data = call_args[1]['json']
                # COT should mention "step by step"
                assert 'step by step' in json_data['inputs']


@pytest.mark.unit
class TestLlamacompletionErrorHandling:
    """Test error handling in Llamacompletion"""
    
    def test_text_completion_http_error(self):
        """Test textCompletion handles HTTP errors"""
        with patch.dict(os.environ, {'LLAMA_ENDPOINT': 'http://test.endpoint'}):
            with patch('llm_explain.utility.llama.requests.post') as mock_post:
                import requests
                mock_post.side_effect = requests.exceptions.HTTPError("500 Server Error")
                
                llama = Llamacompletion()
                with pytest.raises(requests.exceptions.HTTPError):
                    llama.textCompletion("Test", "THOT")
    
    def test_text_completion_connection_error(self):
        """Test textCompletion handles connection errors"""
        with patch.dict(os.environ, {'LLAMA_ENDPOINT': 'http://test.endpoint'}):
            with patch('llm_explain.utility.llama.requests.post') as mock_post:
                import requests
                mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
                
                llama = Llamacompletion()
                with pytest.raises(requests.exceptions.ConnectionError):
                    llama.textCompletion("Test", "COT")
    
    def test_text_completion_timeout(self):
        """Test textCompletion handles timeout"""
        with patch.dict(os.environ, {'LLAMA_ENDPOINT': 'http://test.endpoint'}):
            with patch('llm_explain.utility.llama.requests.post') as mock_post:
                import requests
                mock_post.side_effect = requests.exceptions.Timeout("Request timeout")
                
                llama = Llamacompletion()
                with pytest.raises(requests.exceptions.Timeout):
                    llama.textCompletion("Test", "THOT")
    
    def test_text_completion_json_decode_error(self):
        """Test textCompletion handles JSON decode errors"""
        with patch.dict(os.environ, {'LLAMA_ENDPOINT': 'http://test.endpoint'}):
            with patch('llm_explain.utility.llama.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.side_effect = ValueError("Invalid JSON")
                mock_post.return_value = mock_response
                
                llama = Llamacompletion()
                with pytest.raises(ValueError):
                    llama.textCompletion("Test", "THOT")


@pytest.mark.unit
class TestLlamacompletionOutputParsing:
    """Test output parsing logic"""
    
    def test_output_parsing_with_inst_tag(self):
        """Test parsing output with [/INST] tag"""
        with patch.dict(os.environ, {'LLAMA_ENDPOINT': 'http://test.endpoint'}):
            with patch('llm_explain.utility.llama.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = [{
                    'generated_text': 'System prompt[/INST]Actual answer here'
                }]
                mock_post.return_value = mock_response
                
                llama = Llamacompletion()
                result = llama.textCompletion("Test", "COT")
                
                assert result[0] == 'Actual answer here'
    
    def test_output_parsing_multiple_inst_tags(self):
        """Test parsing with multiple [/INST] tags"""
        with patch.dict(os.environ, {'LLAMA_ENDPOINT': 'http://test.endpoint'}):
            with patch('llm_explain.utility.llama.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = [{
                    'generated_text': 'First[/INST]Middle[/INST]Last'
                }]
                mock_post.return_value = mock_response
                
                llama = Llamacompletion()
                result = llama.textCompletion("Test", "THOT")
                
                # Should get everything after first [/INST], which includes "Middle[/INST]Last"
                assert 'Middle' in result[0] or 'Last' in result[0]
    
    def test_output_parsing_empty_response(self):
        """Test parsing empty response"""
        with patch.dict(os.environ, {'LLAMA_ENDPOINT': 'http://test.endpoint'}):
            with patch('llm_explain.utility.llama.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = [{
                    'generated_text': '[/INST]'
                }]
                mock_post.return_value = mock_response
                
                llama = Llamacompletion()
                result = llama.textCompletion("Test", "COT")
                
                assert result[0] == ''


@pytest.mark.unit
class TestLlamacompletionReturnValues:
    """Test return value structure"""
    
    def test_return_value_structure(self):
        """Test that return value is a tuple with 4 elements"""
        with patch.dict(os.environ, {'LLAMA_ENDPOINT': 'http://test.endpoint'}):
            with patch('llm_explain.utility.llama.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = [{
                    'generated_text': 'X[/INST]Y'
                }]
                mock_post.return_value = mock_response
                
                llama = Llamacompletion()
                result = llama.textCompletion("Test", "THOT")
                
                assert isinstance(result, tuple)
                assert len(result) == 4
                assert isinstance(result[0], str)  # output text
                assert result[1] == 0  # second element
                assert result[2] == ""  # third element
                assert result[3] == "0"  # fourth element
    
    def test_return_value_default_fields(self):
        """Test default values in return tuple"""
        with patch.dict(os.environ, {'LLAMA_ENDPOINT': 'http://test.endpoint'}):
            with patch('llm_explain.utility.llama.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = [{
                    'generated_text': 'Test[/INST]Answer'
                }]
                mock_post.return_value = mock_response
                
                llama = Llamacompletion()
                _, val2, val3, val4 = llama.textCompletion("Q", "COT")
                
                assert val2 == 0
                assert val3 == ""
                assert val4 == "0"


@pytest.mark.unit
class TestLlamacompletionInputVariations:
    """Test with various input types"""
    
    def test_text_completion_with_special_characters(self):
        """Test with special characters in input"""
        with patch.dict(os.environ, {'LLAMA_ENDPOINT': 'http://test.endpoint'}):
            with patch('llm_explain.utility.llama.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = [{
                    'generated_text': 'X[/INST]Y'
                }]
                mock_post.return_value = mock_response
                
                llama = Llamacompletion()
                result = llama.textCompletion("Test @#$%^&*()", "THOT")
                
                assert result is not None
    
    def test_text_completion_with_long_text(self):
        """Test with long input text"""
        with patch.dict(os.environ, {'LLAMA_ENDPOINT': 'http://test.endpoint'}):
            with patch('llm_explain.utility.llama.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = [{
                    'generated_text': 'X[/INST]Y'
                }]
                mock_post.return_value = mock_response
                
                llama = Llamacompletion()
                long_text = "Test question " * 100
                result = llama.textCompletion(long_text, "COT")
                
                assert result is not None
    
    def test_text_completion_with_unicode(self):
        """Test with unicode characters"""
        with patch.dict(os.environ, {'LLAMA_ENDPOINT': 'http://test.endpoint'}):
            with patch('llm_explain.utility.llama.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = [{
                    'generated_text': 'X[/INST]Y'
                }]
                mock_post.return_value = mock_response
                
                llama = Llamacompletion()
                result = llama.textCompletion("你好 world مرحبا", "THOT")
                
                assert result is not None
