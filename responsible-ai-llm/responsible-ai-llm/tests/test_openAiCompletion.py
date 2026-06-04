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
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

# Mock environment setup before imports
os.environ.setdefault('OPENAI_MODEL_GPT4', 'gpt-4')
os.environ.setdefault('OPENAI_API_TYPE', 'azure')
os.environ.setdefault('OPENAI_API_BASE_GPT4', 'https://api.openai.com')
os.environ.setdefault('OPENAI_API_KEY_GPT4', 'test-key')
os.environ.setdefault('OPENAI_API_VERSION_GPT4', '2023-05-15')

# Import and set up request_id_var
from llm.config.logger import request_id_var
request_id_var.set("test-request-id")


class TestOpenaicompletions:
    """Test suite for Openaicompletions class"""
    
    def test_openaicompletions_initialization(self):
        """Test Openaicompletions initialization"""
        from llm.service.openAiCompletion import Openaicompletions
        
        with patch.dict(os.environ, {'OPENAI_MODEL_GPT4': 'gpt-4'}):
            interaction = Openaicompletions()
            assert interaction.deployment_name == 'gpt-4'
            assert interaction.openai_api_type == 'azure'
    
    @patch('llm.service.openAiCompletion.AzureOpenAI')
    def test_textCompletion_gpt4_model(self, mock_azure_openai):
        """Test textCompletion with gpt4 model"""
        from llm.service.openAiCompletion import Openaicompletions
        from llm.mapper.mapper import OpenAiRequest
        
        # Mock the client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(
            message=MagicMock(content="Test response"),
            index=0,
            finish_reason="stop"
        )]
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        # Setup environment
        with patch.dict(os.environ, {
            'OPENAI_MODEL_GPT4': 'gpt-4',
            'OPENAI_API_TYPE': 'azure',
            'OPENAI_API_BASE_GPT4': 'https://api.openai.com',
            'OPENAI_API_KEY_GPT4': 'test-key',
            'OPENAI_API_VERSION_GPT4': '2023-05-15'
        }):
            interaction = Openaicompletions()
            
            payload = OpenAiRequest(
                messages='[{"role": "user", "content": "Hello"}]',
                temperature=0.7,
                model="gpt4"
            )
            
            result = interaction.textCompletion(payload)
            assert 'text' in result
            assert 'index' in result
            assert 'finish_reason' in result
    
    @patch('llm.service.openAiCompletion.AzureOpenAI')
    def test_textCompletion_gpt3_model(self, mock_azure_openai):
        """Test textCompletion with gpt3 model"""
        from llm.service.openAiCompletion import Openaicompletions
        from llm.mapper.mapper import OpenAiRequest
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(
            message=MagicMock(content="GPT3 response"),
            index=0,
            finish_reason="stop"
        )]
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        with patch.dict(os.environ, {
            'OPENAI_MODEL_GPT3': 'gpt-3.5-turbo',
            'OPENAI_API_TYPE': 'azure',
            'OPENAI_API_BASE_GPT3': 'https://api3.openai.com',
            'OPENAI_API_KEY_GPT3': 'test-key-gpt3',
            'OPENAI_API_VERSION_GPT3': '2023-05-15',
            'OPENAI_MODEL_GPT4': 'gpt-4',
            'OPENAI_API_BASE_GPT4': 'https://api.openai.com',
            'OPENAI_API_KEY_GPT4': 'test-key',
            'OPENAI_API_VERSION_GPT4': '2023-05-15'
        }):
            interaction = Openaicompletions()
            
            payload = OpenAiRequest(
                messages='[{"role": "user", "content": "Test"}]',
                temperature=0.5,
                model="gpt3"
            )
            
            result = interaction.textCompletion(payload)
            assert 'text' in result
    
    @patch('llm.service.openAiCompletion.AzureOpenAI')
    def test_textCompletion_gpt4o_model(self, mock_azure_openai):
        """Test textCompletion with gpt4O model"""
        from llm.service.openAiCompletion import Openaicompletions
        from llm.mapper.mapper import OpenAiRequest
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(
            message=MagicMock(content="GPT4O response"),
            index=0,
            finish_reason="stop"
        )]
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        with patch.dict(os.environ, {
            'OPENAI_MODEL_GPT4_O': 'gpt-4o',
            'OPENAI_API_TYPE': 'azure',
            'OPENAI_API_BASE_GPT4_O': 'https://api4o.openai.com',
            'OPENAI_API_KEY_GPT4_O': 'test-key-gpt4o',
            'OPENAI_API_VERSION_GPT4_O': '2023-05-15',
            'OPENAI_MODEL_GPT4': 'gpt-4',
            'OPENAI_API_BASE_GPT4': 'https://api.openai.com',
            'OPENAI_API_KEY_GPT4': 'test-key',
            'OPENAI_API_VERSION_GPT4': '2023-05-15'
        }):
            interaction = Openaicompletions()
            
            payload = OpenAiRequest(
                messages='[{"role": "user", "content": "Test"}]',
                temperature=0.6,
                model="gpt4O"
            )
            
            result = interaction.textCompletion(payload)
            assert 'text' in result
    
    @patch('llm.service.openAiCompletion.AzureOpenAI')
    def test_textCompletion_with_optional_parameters(self, mock_azure_openai):
        """Test textCompletion with optional parameters"""
        from llm.service.openAiCompletion import Openaicompletions
        from llm.mapper.mapper import OpenAiRequest
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(
            message=MagicMock(content="Response with params"),
            index=0,
            finish_reason="length"
        )]
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        with patch.dict(os.environ, {
            'OPENAI_MODEL_GPT4': 'gpt-4',
            'OPENAI_API_TYPE': 'azure',
            'OPENAI_API_BASE_GPT4': 'https://api.openai.com',
            'OPENAI_API_KEY_GPT4': 'test-key',
            'OPENAI_API_VERSION_GPT4': '2023-05-15'
        }):
            interaction = Openaicompletions()
            
            payload = OpenAiRequest(
                messages='[{"role": "user", "content": "Test"}]',
                temperature=0.7,
                model="gpt4",
                max_tokens=500,
                top_p=0.9,
                frequency_penalty=0.5,
                presence_penalty=0.5,
                stop="END"
            )
            
            result = interaction.textCompletion(payload)
            assert result['text'] == "Response with params"
            assert result['finish_reason'] == "length"
    
    @patch('llm.service.openAiCompletion.AzureOpenAI')
    def test_textCompletion_response_structure(self, mock_azure_openai):
        """Test textCompletion returns correct response structure"""
        from llm.service.openAiCompletion import Openaicompletions
        from llm.mapper.mapper import OpenAiRequest
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(
            message=MagicMock(content="Structured response"),
            index=2,
            finish_reason="content_filter"
        )]
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        with patch.dict(os.environ, {
            'OPENAI_MODEL_GPT4': 'gpt-4',
            'OPENAI_API_TYPE': 'azure',
            'OPENAI_API_BASE_GPT4': 'https://api.openai.com',
            'OPENAI_API_KEY_GPT4': 'test-key',
            'OPENAI_API_VERSION_GPT4': '2023-05-15'
        }):
            interaction = Openaicompletions()
            
            payload = OpenAiRequest(
                messages='[{"role": "user", "content": "Test"}]',
                temperature=0.7,
                model="gpt4"
            )
            
            result = interaction.textCompletion(payload)
            
            assert isinstance(result, dict)
            assert 'text' in result
            assert 'index' in result
            assert 'finish_reason' in result
            assert result['index'] == 2
            assert result['text'] == "Structured response"
            assert result['finish_reason'] == "content_filter"
    
    @patch('llm.service.openAiCompletion.AzureOpenAI')
    def test_textCompletion_handles_empty_response_content(self, mock_azure_openai):
        """Test textCompletion handles empty response content"""
        from llm.service.openAiCompletion import Openaicompletions
        from llm.mapper.mapper import OpenAiRequest
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(
            message=MagicMock(content=""),
            index=0,
            finish_reason="stop"
        )]
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        with patch.dict(os.environ, {
            'OPENAI_MODEL_GPT4': 'gpt-4',
            'OPENAI_API_TYPE': 'azure',
            'OPENAI_API_BASE_GPT4': 'https://api.openai.com',
            'OPENAI_API_KEY_GPT4': 'test-key',
            'OPENAI_API_VERSION_GPT4': '2023-05-15'
        }):
            interaction = Openaicompletions()
            
            payload = OpenAiRequest(
                messages='[{"role": "user", "content": "Test"}]',
                temperature=0.7,
                model="gpt4"
            )
            
            result = interaction.textCompletion(payload)
            assert 'text' in result
            assert 'index' in result
            assert 'finish_reason' in result


class TestOpenaicompletionsIntegration:
    """Integration tests for Openaicompletions"""
    
    @patch('llm.service.openAiCompletion.AzureOpenAI')
    def test_multiple_completions_sequence(self, mock_azure_openai):
        """Test multiple completion requests in sequence"""
        from llm.service.openAiCompletion import Openaicompletions
        from llm.mapper.mapper import OpenAiRequest
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(
            message=MagicMock(content="Sequential response"),
            index=0,
            finish_reason="stop"
        )]
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        with patch.dict(os.environ, {
            'OPENAI_MODEL_GPT4': 'gpt-4',
            'OPENAI_API_TYPE': 'azure',
            'OPENAI_API_BASE_GPT4': 'https://api.openai.com',
            'OPENAI_API_KEY_GPT4': 'test-key',
            'OPENAI_API_VERSION_GPT4': '2023-05-15'
        }):
            interaction = Openaicompletions()
            
            for i in range(3):
                payload = OpenAiRequest(
                    messages=f'[{{"role": "user", "content": "Request {i}"}}]',
                    temperature=0.7,
                    model="gpt4"
                )
                result = interaction.textCompletion(payload)
                assert 'text' in result
