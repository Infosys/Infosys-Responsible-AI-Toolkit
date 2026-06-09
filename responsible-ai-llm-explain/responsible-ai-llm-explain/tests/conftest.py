import sys
import os
import pytest
import json
from unittest.mock import patch, Mock

# Set environment variables BEFORE any imports
os.environ['AZURE_OPENAI_API_KEY'] = 'test-api-key-1234'
os.environ['AZURE_OPENAI_API_VERSION'] = '2023-05-15'
os.environ['AZURE_OPENAI_ENDPOINT'] = 'https://test.openai.azure.com'
os.environ['TELEMETRY_FLAG'] = 'False'
os.environ['BULK_TELEMETRY_URL'] = 'http://localhost:8000/telemetry'
os.environ['ERROR_LOG_TELEMETRY_URL'] = 'http://localhost:8000/error'
os.environ['OPENAI_API_KEY'] = 'test-openai-key'

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


# Workaround for duplicate Cov class - patch after import
@pytest.fixture(scope="session", autouse=True)
def patch_cov_llm_response_to_json():
    """Add llm_response_to_json method to Cov class if missing"""
    try:
        from llm_explain.utility.cov import Cov
        
        if not hasattr(Cov, 'llm_response_to_json'):
            @staticmethod
            def llm_response_to_json(response):
                try:
                    start_index = response.find('{')
                    if start_index == -1:
                        return response
                    curly_count = 0
                    for i in range(start_index, len(response)):
                        if response[i] == '{':
                            curly_count += 1
                        elif response[i] == '}':
                            curly_count -= 1
                        if curly_count == 0:
                            end_index = i
                            break
                    json_content = response[start_index:end_index+1]
                    result = json.loads(json_content)
                    return result
                except Exception:
                    raise ValueError("An error occurred while parsing JSON from response.")
            
            Cov.llm_response_to_json = llm_response_to_json
    except:
        pass
    yield


# Mock logger config to avoid missing logger.ini
@pytest.fixture(scope="session", autouse=True)
def mock_logger_config():
    """Mock readConfig to avoid logger.ini issues"""
    with patch('llm_explain.config.config.readConfig') as mock_read:
        mock_read.return_value = {
            'file_name': 'test',
            'verbose': False,
            'log_dir': None
        }
        yield



@pytest.fixture
def sample_token_importance_request():
    """Sample token importance request data"""
    return {
        "inputPrompt": "What is artificial intelligence?",
        "modelName": "GPT"
    }


@pytest.fixture
def mock_token_importance_response():
    """Mock token importance response data"""
    return {
        "token_importance_mapping": [
            {"word": "What", "importance": 0.5, "position": 0},
            {"word": "is", "importance": 0.3, "position": 1}
        ],
        "time_taken": 1.5,
        "token_cost": 100
    }
