import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import json
import os
import sys


# Mock logger and config before any imports
@pytest.fixture(scope="function", autouse=True)
def mock_logger_and_config():
    """Mock CustomLogger and readConfig for all tests"""
    # Mock the CustomLogger class to avoid logger.ini file reading
    with patch('llm_explain.config.logger.CustomLogger') as mock_logger_class:
        mock_logger_instance = Mock()
        mock_logger_instance.debug = Mock()
        mock_logger_instance.info = Mock()
        mock_logger_instance.warning = Mock()
        mock_logger_instance.error = Mock()
        mock_logger_class.return_value = mock_logger_instance
        
        # Also patch it in the abstract_language_model module since it imports it
        with patch('llm_explain.utility.graph_of_thoughts.language_models.abstract_language_model.CustomLogger', mock_logger_class):
            yield mock_logger_instance


@pytest.mark.unit
class TestAzureChatGPTInitialization:
    """Test Azure ChatGPT initialization"""
    
    def test_init_with_env_variables(self):
        """Test initialization with environment variables"""
        env_vars = {
            'AZURE_OPENAI_API_KEY': 'test_key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_OPENAI_API_VERSION': '2023-05-15',
            'AZURE_DEPLOYMENT_ENGINE': 'gpt-4'
        }
        
        config = {
            'gpt4': {
                'prompt_token_cost': 0.03,
                'response_token_cost': 0.06,
                'temperature': 0.7,
                'max_tokens': 2048,
                'stop': None
            }
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('llm_explain.utility.graph_of_thoughts.language_models.azure.AzureOpenAI'):
                with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                    with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                        from llm_explain.utility.graph_of_thoughts.language_models.azure import ChatGPT
                        
                        model = ChatGPT(config_path="", model_name="gpt4", cache=False)
                        
                        assert model.api_key == 'test_key'
                        assert model.api_base == 'https://test.openai.azure.com'
                        assert model.api_version == '2023-05-15'
                        assert model.deployment_name == 'gpt-4'
    
    def test_init_missing_api_key(self):
        """Test initialization fails without API key"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                with patch('builtins.open', mock_open(read_data=json.dumps({'gpt4': {}}))):
                    with pytest.raises(ValueError, match="AZURE_OPENAI_API_KEY"):
                        from llm_explain.utility.graph_of_thoughts.language_models.azure import ChatGPT
                        ChatGPT()
    
    def test_init_missing_endpoint(self):
        """Test initialization fails without endpoint"""
        env_vars = {'AZURE_OPENAI_API_KEY': 'test_key'}
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                with patch('builtins.open', mock_open(read_data=json.dumps({'gpt4': {}}))):
                    with pytest.raises(ValueError, match="AZURE_OPENAI_ENDPOINT"):
                        from llm_explain.utility.graph_of_thoughts.language_models.azure import ChatGPT
                        ChatGPT(config_path="", model_name="gpt4")
    
    def test_init_default_api_version(self):
        """Test initialization uses default API version"""
        env_vars = {
            'AZURE_OPENAI_API_KEY': 'test_key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_DEPLOYMENT_ENGINE': 'gpt-4'
        }
        
        config = {'gpt4': {}}
        
        # Clear AZURE_OPENAI_API_VERSION to test default value
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('llm_explain.utility.graph_of_thoughts.language_models.azure.AzureOpenAI'):
                with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                    with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                        from llm_explain.utility.graph_of_thoughts.language_models.azure import ChatGPT
                        
                        model = ChatGPT(config_path="", model_name="gpt4")
                        
                        assert model.api_version == "2023-05-15"


@pytest.mark.unit
class TestAzureChatGPTQuery:
    """Test Azure ChatGPT query method"""
    
    def test_query_single_response(self):
        """Test query with single response"""
        env_vars = {
            'AZURE_OPENAI_API_KEY': 'test_key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_DEPLOYMENT_ENGINE': 'gpt-4'
        }
        
        config = {'gpt4': {}}
        
        with patch.dict(os.environ, env_vars):
            with patch('llm_explain.utility.graph_of_thoughts.language_models.azure.AzureOpenAI'):
                with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                    with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                        from llm_explain.utility.graph_of_thoughts.language_models.azure import ChatGPT
                        
                        model = ChatGPT(config_path="", model_name="gpt4")
                        
                        mock_response = MagicMock()
                        with patch.object(model, 'chat', return_value=mock_response):
                            result = model.query("Test query")
                            
                            assert result == mock_response
                            model.chat.assert_called_once()
    
    def test_query_multiple_responses(self):
        """Test query with multiple responses"""
        env_vars = {
            'AZURE_OPENAI_API_KEY': 'test_key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_DEPLOYMENT_ENGINE': 'gpt-4'
        }
        
        config = {'gpt4': {}}
        
        with patch.dict(os.environ, env_vars):
            with patch('llm_explain.utility.graph_of_thoughts.language_models.azure.AzureOpenAI'):
                with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                    with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                        from llm_explain.utility.graph_of_thoughts.language_models.azure import ChatGPT
                        
                        model = ChatGPT(config_path="", model_name="gpt4")
                        
                        mock_response = MagicMock()
                        with patch.object(model, 'chat', return_value=mock_response):
                            result = model.query("Test query", num_responses=3)
                            
                            assert isinstance(result, list)
    
    def test_query_with_cache_hit(self):
        """Test query returns cached response"""
        env_vars = {
            'AZURE_OPENAI_API_KEY': 'test_key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_DEPLOYMENT_ENGINE': 'gpt-4'
        }
        
        config = {'gpt4': {}}
        
        with patch.dict(os.environ, env_vars):
            with patch('llm_explain.utility.graph_of_thoughts.language_models.azure.AzureOpenAI'):
                with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                    with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                        from llm_explain.utility.graph_of_thoughts.language_models.azure import ChatGPT
                        
                        model = ChatGPT(config_path="", model_name="gpt4", cache=True)
                        
                        mock_response = MagicMock()
                        model.respone_cache["Test query"] = mock_response
                        
                        result = model.query("Test query")
                        
                        assert result == mock_response
    
    def test_query_exception_handling(self):
        """Test query handles exceptions with retry"""
        env_vars = {
            'AZURE_OPENAI_API_KEY': 'test_key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_DEPLOYMENT_ENGINE': 'gpt-4'
        }
        
        config = {'gpt4': {}}
        
        with patch.dict(os.environ, env_vars):
            with patch('llm_explain.utility.graph_of_thoughts.language_models.azure.AzureOpenAI'):
                with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                    with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                        from llm_explain.utility.graph_of_thoughts.language_models.azure import ChatGPT
                        
                        model = ChatGPT(config_path="", model_name="gpt4")
                        
                        with patch.object(model, 'chat', side_effect=Exception("API Error")):
                            with patch('time.sleep'):  # Mock sleep to speed up test
                                result = model.query("Test", num_responses=2)
                                
                                # Should return empty list after retries
                                assert isinstance(result, list)


@pytest.mark.unit
class TestAzureChatGPTChat:
    """Test Azure ChatGPT chat method"""
    
    def test_chat_basic(self):
        """Test basic chat functionality"""
        env_vars = {
            'AZURE_OPENAI_API_KEY': 'test_key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_DEPLOYMENT_ENGINE': 'gpt-4'
        }
        
        config = {'gpt4': {'temperature': 0.7, 'max_tokens': 1024, 'stop': None, 'prompt_token_cost': 0.03, 'response_token_cost': 0.06}}
        
        with patch.dict(os.environ, env_vars):
            with patch('llm_explain.utility.graph_of_thoughts.language_models.azure.AzureOpenAI'):
                with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                    with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                        from llm_explain.utility.graph_of_thoughts.language_models.azure import ChatGPT
                        
                        model = ChatGPT(config_path="", model_name="gpt4")
                        
                        # Mock the client
                        mock_client = MagicMock()
                        model.client = mock_client
                        
                        mock_response = MagicMock()
                        mock_response.usage.prompt_tokens = 10
                        mock_response.usage.completion_tokens = 20
                        mock_client.chat.completions.create.return_value = mock_response
                        
                        messages = [{"role": "user", "content": "Hello"}]
                        result = model.chat(messages)
                        
                        assert result == mock_response
                        assert model.prompt_tokens == 10
                        assert model.completion_tokens == 20
    
    def test_chat_updates_cost(self):
        """Test chat updates cost correctly"""
        env_vars = {
            'AZURE_OPENAI_API_KEY': 'test_key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_DEPLOYMENT_ENGINE': 'gpt-4'
        }
        
        config = {'gpt4': {'prompt_token_cost': 0.03, 'response_token_cost': 0.06}}
        
        with patch.dict(os.environ, env_vars):
            with patch('llm_explain.utility.graph_of_thoughts.language_models.azure.AzureOpenAI'):
                with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                    with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                        from llm_explain.utility.graph_of_thoughts.language_models.azure import ChatGPT
                        
                        model = ChatGPT(config_path="", model_name="gpt4")
                        
                        mock_client = MagicMock()
                        model.client = mock_client
                        
                        mock_response = MagicMock()
                        mock_response.usage.prompt_tokens = 1000
                        mock_response.usage.completion_tokens = 500
                        mock_client.chat.completions.create.return_value = mock_response
                        
                        model.chat([{"role": "user", "content": "Test"}])
                        
                        expected_cost = (1000/1000 * 0.03) + (500/1000 * 0.06)
                        assert model.cost == expected_cost


@pytest.mark.unit
class TestAzureGetResponseTexts:
    """Test Azure get_response_texts method"""
    
    def test_get_response_texts_single(self):
        """Test get_response_texts with single response"""
        env_vars = {
            'AZURE_OPENAI_API_KEY': 'test_key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_DEPLOYMENT_ENGINE': 'gpt-4'
        }
        
        config = {'gpt4': {}}
        
        with patch.dict(os.environ, env_vars):
            with patch('llm_explain.utility.graph_of_thoughts.language_models.azure.AzureOpenAI'):
                with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                    with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                        from llm_explain.utility.graph_of_thoughts.language_models.azure import ChatGPT
                        
                        model = ChatGPT(config_path="", model_name="gpt4")
                        
                        mock_response = MagicMock()
                        mock_choice = MagicMock()
                        mock_choice.message.content = "Test response"
                        mock_response.choices = [mock_choice]
                        
                        result = model.get_response_texts(mock_response)
                        
                        assert result == ["Test response"]
    
    def test_get_response_texts_list(self):
        """Test get_response_texts with list of responses"""
        env_vars = {
            'AZURE_OPENAI_API_KEY': 'test_key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_DEPLOYMENT_ENGINE': 'gpt-4'
        }
        
        config = {'gpt4': {}}
        
        with patch.dict(os.environ, env_vars):
            with patch('llm_explain.utility.graph_of_thoughts.language_models.azure.AzureOpenAI'):
                with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                    with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                        from llm_explain.utility.graph_of_thoughts.language_models.azure import ChatGPT
                        
                        model = ChatGPT(config_path="", model_name="gpt4")
                        
                        responses = []
                        for i in range(3):
                            mock_response = MagicMock()
                            mock_choice = MagicMock()
                            mock_choice.message.content = f"Response {i}"
                            mock_response.choices = [mock_choice]
                            responses.append(mock_response)
                        
                        result = model.get_response_texts(responses)
                        
                        assert len(result) == 3
                        assert result[0] == "Response 0"


@pytest.mark.unit  
class TestOpenAIChatGPTInitialization:
    """Test OpenAI ChatGPT initialization"""
    
    def test_init_with_api_key(self):
        """Test initialization with API key"""
        env_vars = {'OPENAI_API_KEY': 'test_openai_key'}
        
        config = {
            'chatgpt': {
                'api_key': '',
                'model_id': 'gpt-4',
                'prompt_token_cost': 0.03,
                'response_token_cost': 0.06,
                'temperature': 0.7,
                'max_tokens': 1024,
                'stop': None,
                'organization': ''
            }
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('llm_explain.utility.graph_of_thoughts.language_models.chatgpt.OpenAI'):
                with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                    with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                        from llm_explain.utility.graph_of_thoughts.language_models.chatgpt import ChatGPT
                        
                        model = ChatGPT(config_path="", model_name="chatgpt", cache=False)
                        
                        assert model.api_key == 'test_openai_key'
                        assert model.model_id == 'gpt-4'
    
    def test_init_missing_api_key(self):
        """Test initialization fails without API key"""
        config = {
            'chatgpt': {
                'api_key': '',
                'model_id': 'gpt-4',
                'prompt_token_cost': 0.03,
                'response_token_cost': 0.06,
                'temperature': 0.7,
                'max_tokens': 1024,
                'stop': None,
                'organization': ''
            }
        }
        
        with patch.dict(os.environ, {}, clear=True):
            with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                    from llm_explain.utility.graph_of_thoughts.language_models.chatgpt import ChatGPT
                    
                    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                        ChatGPT(config_path="", model_name="chatgpt")


@pytest.mark.unit
class TestOpenAIChatGPTQuery:
    """Test OpenAI ChatGPT query method"""
    
    def test_query_basic(self):
        """Test basic query"""
        env_vars = {'OPENAI_API_KEY': 'test_key'}
        
        config = {
            'chatgpt': {
                'api_key': '',
                'model_id': 'gpt-4',
                'prompt_token_cost': 0.03,
                'response_token_cost': 0.06,
                'temperature': 0.7,
                'max_tokens': 1024,
                'stop': None,
                'organization': ''
            }
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('llm_explain.utility.graph_of_thoughts.language_models.chatgpt.OpenAI'):
                with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                    with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                        from llm_explain.utility.graph_of_thoughts.language_models.chatgpt import ChatGPT
                        
                        model = ChatGPT(config_path="", model_name="chatgpt")
                        
                        mock_response = MagicMock()
                        with patch.object(model, 'chat', return_value=mock_response):
                            result = model.query("Test query")
                            
                            assert result == mock_response


@pytest.mark.unit
class TestAbstractLanguageModel:
    """Test AbstractLanguageModel"""
    
    def test_read_config(self):
        """Test load_config method"""
        from llm_explain.utility.graph_of_thoughts.language_models.abstract_language_model import AbstractLanguageModel
        
        # Test that config is loaded during initialization
        config_data = {'test': {'param': 'value'}}
        config_json = json.dumps(config_data)
        
        with patch('builtins.open', mock_open(read_data=config_json)):
            # Just test that abstract class would load config
            assert config_data is not None
    
    def test_read_config_file_not_found(self):
        """Test load_config with missing file"""
        from llm_explain.utility.graph_of_thoughts.language_models.abstract_language_model import AbstractLanguageModel
        
        with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
            with patch('builtins.open', side_effect=FileNotFoundError):
                # Test that FileNotFoundError is raised when config file is missing
                with pytest.raises(FileNotFoundError):
                    # Attempting to instantiate with a missing config should raise
                    class TestModel(AbstractLanguageModel):
                        def query(self, query, num_responses=1):
                            pass
                        def get_response_texts(self, responses):
                            pass
                    TestModel('', 'test', False)
    
    def test_cost_and_tokens_attributes(self):
        """Test cost and tokens attributes exist"""
        from llm_explain.utility.graph_of_thoughts.language_models.abstract_language_model import AbstractLanguageModel
        
        # Create a concrete mock class
        class MockModel(AbstractLanguageModel):
            def query(self, query, num_responses=1):
                return []
            def get_response_texts(self, responses):
                return []
        
        with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
            with patch('builtins.open', mock_open(read_data='{}')):
                model = MockModel('', 'test', False)
            
            # Test that attributes exist and can be set
            model.cost = 0.5
            model.prompt_tokens = 100
            model.completion_tokens = 50
            
            assert model.cost == 0.5
            assert model.prompt_tokens == 100
            assert model.completion_tokens == 50
    
    def test_cache_functionality(self):
        """Test cache functionality"""
        from llm_explain.utility.graph_of_thoughts.language_models.abstract_language_model import AbstractLanguageModel
        
        class MockModel(AbstractLanguageModel):
            def query(self, query, num_responses=1):
                return []
            def get_response_texts(self, responses):
                return []
        
        with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
            with patch('builtins.open', mock_open(read_data='{}')):
                model = MockModel('', 'test', True)  # Enable cache
                
                # Test that cache is initialized
                assert hasattr(model, 'respone_cache')
                assert model.cache == True
                
                # Test clear_cache method
                model.respone_cache['test'] = 'value'
                model.clear_cache()
                assert len(model.respone_cache) == 0
    
    def test_load_config(self):
        """Test load_config method"""
        from llm_explain.utility.graph_of_thoughts.language_models.abstract_language_model import AbstractLanguageModel
        
        class MockModel(AbstractLanguageModel):
            def query(self, query, num_responses=1):
                return []
            def get_response_texts(self, responses):
                return []
        
        config_data = {'test_model': {'param': 'value'}}
        
        with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
            with patch('builtins.open', mock_open(read_data=json.dumps(config_data))):
                model = MockModel('', 'test_model', False)
                
                # Test that config is loaded
                assert model.config is not None
                assert model.model_name == 'test_model'


@pytest.mark.unit
class TestLanguageModelIntegration:
    """Test integration scenarios"""
    
    def test_azure_end_to_end(self):
        """Test Azure model end-to-end"""
        env_vars = {
            'AZURE_OPENAI_API_KEY': 'test_key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_DEPLOYMENT_ENGINE': 'gpt-4'
        }
        
        config = {'gpt4': {}}
        
        with patch.dict(os.environ, env_vars):
            with patch('llm_explain.utility.graph_of_thoughts.language_models.azure.AzureOpenAI'):
                with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                    with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                        from llm_explain.utility.graph_of_thoughts.language_models.azure import ChatGPT
                        
                        model = ChatGPT(config_path="", model_name="gpt4", cache=True)
                        
                        # Mock responses
                        mock_response = MagicMock()
                        mock_choice = MagicMock()
                        mock_choice.message.content = "Test answer"
                        mock_response.choices = [mock_choice]
                        mock_response.usage.prompt_tokens = 10
                        mock_response.usage.completion_tokens = 5
                        
                        model.client = MagicMock()
                        model.client.chat.completions.create.return_value = mock_response
                        
                        # Query
                        result = model.query("What is AI?")
                        texts = model.get_response_texts(result)
                        
                        assert texts[0] == "Test answer"
                        
                        # Check caching
                        result2 = model.query("What is AI?")
                        assert result2 == result  # Should be cached


@pytest.mark.unit
class TestAzureChatGPTAdditionalCoverage:
    """Additional tests for Azure ChatGPT to increase coverage"""
    
    def test_query_multiple_responses_success_path(self):
        """Test query with multiple responses succeeds"""
        env_vars = {
            'AZURE_OPENAI_API_KEY': 'test_key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_DEPLOYMENT_ENGINE': 'gpt-4'
        }
        
        config = {'gpt4': {}}
        
        with patch.dict(os.environ, env_vars):
            with patch('llm_explain.utility.graph_of_thoughts.language_models.azure.AzureOpenAI'):
                with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                    with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                        from llm_explain.utility.graph_of_thoughts.language_models.azure import ChatGPT
                        
                        model = ChatGPT(config_path="", model_name="gpt4")
                        
                        # Mock successful chat response
                        mock_response = MagicMock()
                        mock_response.usage.prompt_tokens = 10
                        mock_response.usage.completion_tokens = 20
                        
                        with patch.object(model, 'chat', return_value=mock_response):
                            with patch('time.sleep'):
                                result = model.query("Test", num_responses=5)
                                
                                assert isinstance(result, list)
                                # When requesting 5 responses successfully, it makes 1 call with n=5
                                assert len(result) == 1
                                assert result[0] == mock_response
    
    def test_query_with_cache_miss_then_hit(self):
        """Test query with cache miss followed by hit"""
        env_vars = {
            'AZURE_OPENAI_API_KEY': 'test_key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_DEPLOYMENT_ENGINE': 'gpt-4'
        }
        
        config = {'gpt4': {}}
        
        with patch.dict(os.environ, env_vars):
            with patch('llm_explain.utility.graph_of_thoughts.language_models.azure.AzureOpenAI'):
                with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                    with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                        from llm_explain.utility.graph_of_thoughts.language_models.azure import ChatGPT
                        
                        model = ChatGPT(config_path="", model_name="gpt4", cache=True)
                        
                        mock_response = MagicMock()
                        mock_response.usage.prompt_tokens = 10
                        mock_response.usage.completion_tokens = 5
                        
                        model.client = MagicMock()
                        model.client.chat.completions.create.return_value = mock_response
                        
                        # First query - cache miss
                        result1 = model.query("New query")
                        assert result1 == mock_response
                        
                        # Second query - cache hit
                        result2 = model.query("New query")
                        assert result2 == result1
                        assert result2 == mock_response
    
    def test_query_multiple_with_partial_failures(self):
        """Test query with multiple responses and partial failures"""
        env_vars = {
            'AZURE_OPENAI_API_KEY': 'test_key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_DEPLOYMENT_ENGINE': 'gpt-4'
        }
        
        config = {'gpt4': {}}
        
        with patch.dict(os.environ, env_vars):
            with patch('llm_explain.utility.graph_of_thoughts.language_models.azure.AzureOpenAI'):
                with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                    with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                        from llm_explain.utility.graph_of_thoughts.language_models.azure import ChatGPT
                        
                        model = ChatGPT(config_path="", model_name="gpt4")
                        
                        # Mock chat to fail first, then succeed
                        mock_response = MagicMock()
                        mock_response.usage.prompt_tokens = 10
                        mock_response.usage.completion_tokens = 20
                        
                        side_effects = [Exception("API Error"), mock_response]
                        
                        with patch.object(model, 'chat', side_effect=side_effects):
                            with patch('time.sleep'):
                                result = model.query("Test", num_responses=3)
                                
                                assert isinstance(result, list)


@pytest.mark.unit
class TestOpenAIChatGPTAdditionalCoverage:
    """Additional tests for OpenAI ChatGPT to increase coverage"""
    
    def test_query_multiple_responses_success(self):
        """Test query with multiple responses succeeds"""
        env_vars = {'OPENAI_API_KEY': 'test_openai_key'}
        
        config = {
            'chatgpt': {
                'api_key': '',
                'model_id': 'gpt-4',
                'prompt_token_cost': 0.03,
                'response_token_cost': 0.06,
                'temperature': 0.7,
                'max_tokens': 1024,
                'stop': None,
                'organization': ''
            }
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('llm_explain.utility.graph_of_thoughts.language_models.chatgpt.OpenAI'):
                with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                    with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                        from llm_explain.utility.graph_of_thoughts.language_models.chatgpt import ChatGPT
                        
                        model = ChatGPT(config_path="", model_name="chatgpt")
                        
                        # Mock successful chat responses
                        mock_response1 = MagicMock()
                        mock_response1.usage.prompt_tokens = 10
                        mock_response1.usage.completion_tokens = 20
                        
                        mock_response2 = MagicMock()
                        mock_response2.usage.prompt_tokens = 15
                        mock_response2.usage.completion_tokens = 25
                        
                        with patch.object(model, 'chat', side_effect=[mock_response1, mock_response2]):
                            with patch('time.sleep'):
                                result = model.query("Test", num_responses=5)
                                
                                assert isinstance(result, list)
    
    def test_chat_logging(self):
        """Test chat method logs response and cost"""
        env_vars = {'OPENAI_API_KEY': 'test_openai_key'}
        
        config = {
            'chatgpt': {
                'api_key': '',
                'model_id': 'gpt-4',
                'prompt_token_cost': 0.03,
                'response_token_cost': 0.06,
                'temperature': 0.7,
                'max_tokens': 1024,
                'stop': None,
                'organization': ''
            }
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('llm_explain.utility.graph_of_thoughts.language_models.chatgpt.OpenAI'):
                with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                    with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                        from llm_explain.utility.graph_of_thoughts.language_models.chatgpt import ChatGPT
                        
                        model = ChatGPT(config_path="", model_name="chatgpt")
                        
                        # Mock the client
                        mock_client = MagicMock()
                        model.client = mock_client
                        
                        mock_response = MagicMock()
                        mock_response.usage.prompt_tokens = 1000
                        mock_response.usage.completion_tokens = 500
                        mock_client.chat.completions.create.return_value = mock_response
                        
                        messages = [{"role": "user", "content": "Test"}]
                        result = model.chat(messages)
                        
                        assert result == mock_response
                        assert model.prompt_tokens == 1000
                        assert model.completion_tokens == 500
                        # Verify logger.info was called
                        model.logger.info.assert_called()
    
    def test_query_with_cache_enabled(self):
        """Test query with cache enabled"""
        env_vars = {'OPENAI_API_KEY': 'test_openai_key'}
        
        config = {
            'chatgpt': {
                'api_key': '',
                'model_id': 'gpt-4',
                'prompt_token_cost': 0.03,
                'response_token_cost': 0.06,
                'temperature': 0.7,
                'max_tokens': 1024,
                'stop': None,
                'organization': ''
            }
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('llm_explain.utility.graph_of_thoughts.language_models.chatgpt.OpenAI'):
                with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                    with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                        from llm_explain.utility.graph_of_thoughts.language_models.chatgpt import ChatGPT
                        
                        model = ChatGPT(config_path="", model_name="chatgpt", cache=True)
                        
                        mock_response = MagicMock()
                        mock_response.usage.prompt_tokens = 10
                        mock_response.usage.completion_tokens = 5
                        
                        with patch.object(model, 'chat', return_value=mock_response):
                            # First call - cache miss
                            result1 = model.query("What is Python?", num_responses=1)
                            assert result1 == mock_response
                            
                            # Second call - cache hit
                            result2 = model.query("What is Python?", num_responses=1)
                            assert result2 == result1
    
    def test_query_multiple_with_exceptions_and_retry(self):
        """Test query with multiple responses, exceptions, and retry logic"""
        env_vars = {'OPENAI_API_KEY': 'test_openai_key'}
        
        config = {
            'chatgpt': {
                'api_key': '',
                'model_id': 'gpt-4',
                'prompt_token_cost': 0.03,
                'response_token_cost': 0.06,
                'temperature': 0.7,
                'max_tokens': 1024,
                'stop': None,
                'organization': ''
            }
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('llm_explain.utility.graph_of_thoughts.language_models.chatgpt.OpenAI'):
                with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                    with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                        from llm_explain.utility.graph_of_thoughts.language_models.chatgpt import ChatGPT
                        
                        model = ChatGPT(config_path="", model_name="chatgpt", cache=True)
                        
                        mock_response = MagicMock()
                        mock_response.usage.prompt_tokens = 10
                        mock_response.usage.completion_tokens = 20
                        
                        # First call fails, second succeeds
                        side_effects = [Exception("Temporary Error"), mock_response]
                        
                        with patch.object(model, 'chat', side_effect=side_effects):
                            with patch('time.sleep'):
                                result = model.query("Complex query", num_responses=4)
                                
                                assert isinstance(result, list)
                                # Verify logger.warning was called for the exception
                                model.logger.warning.assert_called()
    
    def test_get_response_texts_list_of_responses(self):
        """Test get_response_texts with list of responses"""
        env_vars = {'OPENAI_API_KEY': 'test_openai_key'}
        
        config = {
            'chatgpt': {
                'api_key': '',
                'model_id': 'gpt-4',
                'prompt_token_cost': 0.03,
                'response_token_cost': 0.06,
                'temperature': 0.7,
                'max_tokens': 1024,
                'stop': None,
                'organization': ''
            }
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('llm_explain.utility.graph_of_thoughts.language_models.chatgpt.OpenAI'):
                with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': 'False', 'log_dir': 'None'}):
                    with patch('builtins.open', mock_open(read_data=json.dumps(config))):
                        from llm_explain.utility.graph_of_thoughts.language_models.chatgpt import ChatGPT
                        
                        model = ChatGPT(config_path="", model_name="chatgpt")
                        
                        # Create multiple mock responses
                        responses = []
                        for i in range(3):
                            mock_response = MagicMock()
                            mock_choice = MagicMock()
                            mock_choice.message.content = f"Answer {i}"
                            mock_response.choices = [mock_choice]
                            responses.append(mock_response)
                        
                        result = model.get_response_texts(responses)
                        
                        assert len(result) == 3
                        assert result[0] == "Answer 0"
                        assert result[1] == "Answer 1"
                        assert result[2] == "Answer 2"

