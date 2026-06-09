"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pytest
import sys
import os
from unittest.mock import MagicMock
import types

# Set environment variables BEFORE any module imports that might use them
# This is critical because some modules instantiate services at module level
os.environ.setdefault('DB_TYPE', 'mongo')
os.environ.setdefault('MONGO_PATH', 'mongodb://localhost:27017/')
os.environ.setdefault('DB_NAME', 'test_database')
os.environ.setdefault('BENCHMARK_NAME', 'benchmark_name')
os.environ.setdefault('DB_HOST', 'dbhost')
os.environ.setdefault('DB_PORT', 'dbport')
os.environ.setdefault('DB_USER', 'dbuser')
os.environ.setdefault('DB_PASSWORD', 'dbpassword')
os.environ.setdefault('TABLE_NAME', 'tablename')
os.environ.setdefault('LOG_TYPE', 'BOTH')
os.environ.setdefault('RESULTS_DIR_PATH', 'results_dir_path')
os.environ.setdefault('LOG_FILE_PATH', 'log_file_path')
os.environ.setdefault('BENCHMARK_DATA_PATH', 'benchmark_data_path')
os.environ.setdefault('INFERENCE_SERVER_URL', 'inference_server_url')
os.environ.setdefault('INFERENCE_SERVER_NAME', 'inference_server_name')

# Use mongomock to mock pymongo - this provides a complete MongoDB mock
import mongomock
sys.modules['pymongo'] = mongomock
sys.modules['pymongo.results'] = mongomock.results

# Mock trustllm modules BEFORE adding src to path and importing anything
# This ensures operations.py can import from trustllm.task.pipeline
trustllm_mock = MagicMock()
trustllm_task_mock = MagicMock()
trustllm_utils_mock = MagicMock()
trustllm_generation_mock = MagicMock()

# Create a proper module mock for trustllm.task.pipeline that supports wildcard imports
trustllm_pipeline_mock = types.ModuleType('trustllm.task.pipeline')
trustllm_pipeline_mock.__all__ = ['run_fairness', 'run_privacy', 'run_ethics', 'run_safety', 'run_truthfulness']

# Add the run_* functions as actual module attributes with proper return values
trustllm_pipeline_mock.run_fairness = MagicMock(return_value={
    "stereotype_recognition": 0.85,
    "stereotype_agreement": 0.80,
    "stereotype_query": 0.90,
    "disparagement": {"race": 0.88, "sex": 0.87},
    "preference": {"overall": 0.92}
})
trustllm_pipeline_mock.run_privacy = MagicMock(return_value={
    "privacy_awareness_query_normal": 0.85,
    "privacy_awareness_query_aug": 0.88,
    "privacy_confAIde": 0.90,
    "privacy_leakage": {"RtA": 0.92, "TD": 0.87, "CD": 0.89}
})
trustllm_pipeline_mock.run_ethics = MagicMock(return_value={
    "explicit_ethics_res_low": 0.85,
    "explicit_ethics_res_high": 0.88,
    "implicit_ethics_res_ETHICS": {"overall": 0.90},
    "implicit_ethics_res_social_norm": {"overall": 0.87},
    "emotional_res": {
        "culture": 0.92,
        "perspective": 0.89,
        "emotion": 0.88,
        "capability": 0.91
    }
})
trustllm_pipeline_mock.run_safety = MagicMock(return_value={
    "jailbreak_res": 0.85,
    "exaggerated_safety_res": 0.88,
    "misuse_res": 0.90,
    "toxicity_res": 0.87
})
trustllm_pipeline_mock.run_truthfulness = MagicMock(return_value={
    "misinformation_internal": {"avg": 0.85},
    "misinformation_external": {"avg": 0.88},
    "hallucination": {"avg": 0.90},
    "sycophancy_persona": 0.87,
    "sycophancy_preference": 0.89,
    "advfact": 0.92
})

# Set up the mock module structure
trustllm_task_mock.pipeline = trustllm_pipeline_mock
trustllm_task_mock.fairness = MagicMock()
trustllm_mock.task = trustllm_task_mock
trustllm_mock.utils = trustllm_utils_mock
trustllm_mock.generation = trustllm_generation_mock
trustllm_mock.config = MagicMock()
trustllm_mock.dataset_download = MagicMock()

# Install all the mocks in sys.modules
sys.modules['trustllm'] = trustllm_mock
sys.modules['trustllm.task'] = trustllm_task_mock
sys.modules['trustllm.task.pipeline'] = trustllm_pipeline_mock
sys.modules['trustllm.task.fairness'] = trustllm_task_mock.fairness
sys.modules['trustllm.utils'] = trustllm_utils_mock
sys.modules['trustllm.generation'] = trustllm_generation_mock
sys.modules['trustllm.config'] = trustllm_mock.config
sys.modules['trustllm.dataset_download'] = trustllm_mock.dataset_download
sys.modules['trustllm.utils.file_process'] = MagicMock()
sys.modules['trustllm.generation.generation'] = MagicMock()

# NOW add the src directory to the path so we can import dao, service, config, router
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture to mock environment variables"""
    monkeypatch.setenv('BENCHMARK_NAME', 'benchmark_name')
    monkeypatch.setenv('DB_HOST', 'dbhost')
    monkeypatch.setenv('DB_PORT', 'dbport')
    monkeypatch.setenv('DB_USER', 'dbuser')
    monkeypatch.setenv('DB_PASSWORD', 'dbpassword')
    monkeypatch.setenv('DB_NAME', 'dbname')
    monkeypatch.setenv('TABLE_NAME', 'tablename')
    monkeypatch.setenv('LOG_TYPE', 'BOTH')
    monkeypatch.setenv('RESULTS_DIR_PATH', 'results_dir_path')
    monkeypatch.setenv('LOG_FILE_PATH', 'log_file_path')
    monkeypatch.setenv('BENCHMARK_DATA_PATH', 'benchmark_data_path')
    monkeypatch.setenv('INFERENCE_SERVER_URL', 'inference_server_url')
    monkeypatch.setenv('INFERENCE_SERVER_NAME', 'inference_server_name')
    
@pytest.fixture
def mock_db():
    """Fixture to create a mock database connection"""
    from unittest.mock import Mock
    mock = Mock()
    mock.cursor.return_value = Mock()
    return mock

@pytest.fixture
def mock_cursor():
    """Fixture to create a mock database cursor"""
    from unittest.mock import Mock
    return Mock()
