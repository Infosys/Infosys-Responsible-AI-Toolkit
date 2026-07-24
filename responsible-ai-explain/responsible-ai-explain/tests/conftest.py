'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

"""
conftest.py - Pytest configuration and fixtures for comprehensive testing
"""

import sys
import os
import pytest
from unittest.mock import Mock, MagicMock, patch
import tempfile
import pandas as pd
import numpy as np

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================================
# Environment Variables Setup - Must be done before importing modules
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_environment():
    """Setup environment variables for all tests"""
    env_vars = {
        'DB_NAME': 'test_db',
        'MONGO_PATH': 'mongodb://localhost:27017',
        'COSMOS_PATH': 'mongodb://localhost:27017',
        'DB_TYPE': 'mongo',
        'RAI_EXPLAIN_DB': 'test_explain_db',
        'TELEMETRY_FLAG': 'False',
        'ERROR_LOG_TELEMETRY_URL': 'http://localhost:8000/telemetry',
        'REPORT_URL': 'http://localhost:8000/report',
        'MODEL_CONTAINER_NAME': 'models',
        'DATASET_CONTAINER_NAME': 'datasets',
        'HTML_CONTAINER_NAME': 'html',
        'AZURE_UPLOAD_API': 'http://localhost:8000/upload',
        'AZURE_GET_API': 'http://localhost:8000/get',
        'VERIFY_SSL': 'false'
    }
    with patch.dict(os.environ, env_vars):
        yield


# ============================================================================
# Mock Database Connection
# ============================================================================

@pytest.fixture
def mock_mongodb():
    """Mock MongoDB connection"""
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()
    
    mock_client.__getitem__ = MagicMock(return_value=mock_db)
    mock_db.__getitem__ = MagicMock(return_value=mock_collection)
    mock_client.admin.command = MagicMock(return_value={'ismaster': True})
    
    return mock_client, mock_db, mock_collection


@pytest.fixture
def mock_gridfs():
    """Mock GridFS for file operations"""
    mock_fs = MagicMock()
    mock_file = MagicMock()
    mock_file._id = "test_file_id"
    mock_file.filename = "test_file.pkl"
    mock_file.read = MagicMock(return_value=b"test_binary_content")
    
    mock_fs.find_one = MagicMock(return_value=mock_file)
    mock_fs.get = MagicMock(return_value=mock_file)
    mock_fs.new_file = MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=mock_file), __exit__=MagicMock()))
    
    return mock_fs


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing"""
    np.random.seed(42)
    return pd.DataFrame({
        'feature1': np.random.rand(100),
        'feature2': np.random.rand(100),
        'feature3': np.random.rand(100),
        'target': np.random.randint(0, 2, 100)
    })


@pytest.fixture
def sample_classification_dataframe():
    """Create a sample classification DataFrame"""
    np.random.seed(42)
    return pd.DataFrame({
        'age': np.random.randint(18, 80, 100),
        'income': np.random.randint(20000, 150000, 100),
        'score': np.random.rand(100) * 100,
        'class_label': np.random.choice(['A', 'B', 'C'], 100)
    })


@pytest.fixture
def sample_regression_dataframe():
    """Create a sample regression DataFrame"""
    np.random.seed(42)
    return pd.DataFrame({
        'x1': np.random.rand(100),
        'x2': np.random.rand(100),
        'x3': np.random.rand(100),
        'y': np.random.rand(100) * 100
    })


@pytest.fixture
def sample_timeseries_dataframe():
    """Create a sample time series DataFrame"""
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    np.random.seed(42)
    return pd.DataFrame({
        'date': dates,
        'value1': np.random.rand(100),
        'value2': np.random.rand(100),
        'target': np.random.rand(100) * 100
    })


@pytest.fixture
def sample_text_data():
    """Sample text data for text explanation tests"""
    return [
        "This movie was fantastic! The plot was gripping and the acting was top-notch.",
        "I did not enjoy this product. It broke after one day of use.",
        "The service was average. Nothing special but nothing terrible either."
    ]


# ============================================================================
# Mock Model Fixtures
# ============================================================================

@pytest.fixture
def mock_sklearn_model():
    """Mock scikit-learn classifier model"""
    model = MagicMock()
    model.predict = MagicMock(return_value=np.array([0, 1, 0, 1]))
    model.predict_proba = MagicMock(return_value=np.array([[0.8, 0.2], [0.3, 0.7], [0.9, 0.1], [0.4, 0.6]]))
    model.feature_names_in_ = ['feature1', 'feature2', 'feature3']
    return model


@pytest.fixture
def mock_keras_model():
    """Mock Keras model"""
    model = MagicMock()
    model.predict = MagicMock(return_value=np.array([[0.8], [0.3], [0.9], [0.4]]))
    return model


@pytest.fixture
def mock_pipeline_model():
    """Mock sklearn Pipeline model"""
    preprocessor = MagicMock()
    preprocessor.n_features_in_ = 3
    preprocessor.transform = MagicMock(return_value=np.array([[1, 2, 3], [4, 5, 6]]))
    preprocessor.get_feature_names_out = MagicMock(return_value=['feature1', 'feature2', 'feature3'])
    
    estimator = MagicMock()
    estimator.predict = MagicMock(return_value=np.array([0, 1]))
    estimator.predict_proba = MagicMock(return_value=np.array([[0.8, 0.2], [0.3, 0.7]]))
    
    pipeline = MagicMock()
    pipeline.steps = [('preprocessor', preprocessor), ('classifier', estimator)]
    pipeline.__getitem__ = MagicMock(return_value=preprocessor)
    
    return pipeline


# ============================================================================
# Mock SHAP and LIME Fixtures
# ============================================================================

@pytest.fixture
def mock_shap_explainer():
    """Mock SHAP explainer"""
    explainer = MagicMock()
    explainer.shap_values = MagicMock(return_value=np.random.rand(10, 3))
    explainer.expected_value = 0.5
    return explainer


@pytest.fixture
def mock_lime_explainer():
    """Mock LIME explainer"""
    explainer = MagicMock()
    explanation = MagicMock()
    explanation.as_list = MagicMock(return_value=[('feature1', 0.5), ('feature2', -0.3), ('feature3', 0.2)])
    explanation.local_exp = {0: [(0, 0.5), (1, -0.3), (2, 0.2)]}
    explanation.predict_proba = np.array([0.7, 0.3])
    explainer.explain_instance = MagicMock(return_value=explanation)
    return explainer


# ============================================================================
# Temporary File Fixtures
# ============================================================================

@pytest.fixture
def temp_directory():
    """Create a temporary directory for file tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_config_file(temp_directory):
    """Create a temporary config file"""
    config_content = """[logDetails]
file_name = test_log
verbose = true
log_dir = /tmp/logs

[database]
host = localhost
port = 27017
"""
    config_path = os.path.join(temp_directory, 'test_config.ini')
    with open(config_path, 'w') as f:
        f.write(config_content)
    return config_path


@pytest.fixture
def temp_yaml_file(temp_directory):
    """Create a temporary YAML config file"""
    yaml_content = """database:
  host: localhost
  port: 27017
  name: test_db

settings:
  debug: true
  log_level: INFO
"""
    yaml_path = os.path.join(temp_directory, 'test_config.yaml')
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    return yaml_path


# ============================================================================
# Mock DAO Fixtures
# ============================================================================

@pytest.fixture
def mock_model_dao():
    """Mock Model DAO operations"""
    model_data = {
        '_id': 1.0,
        'ModelName': 'TestModel',
        'ModelData': 'model_file_id',
        'ModelEndPoint': 'http://localhost:5000/predict'
    }
    return model_data


@pytest.fixture
def mock_dataset_dao():
    """Mock Dataset DAO operations"""
    dataset_data = {
        '_id': 1.0,
        'DatasetName': 'TestDataset',
        'SampleData': 'dataset_file_id'
    }
    return dataset_data


@pytest.fixture
def mock_explanation_methods():
    """Mock explanation methods from database"""
    return [
        {
            'methods': 'LIME-TABULAR',
            'scope': 'LOCAL',
            'modelFramework': 'Scikit-learn',
            'taskType': 'CLASSIFICATION',
            'dataType': 'Tabular',
            'unsupportedModels': []
        },
        {
            'methods': 'KERNEL-SHAP',
            'scope': 'GLOBAL',
            'modelFramework': 'Scikit-learn',
            'taskType': 'CLASSIFICATION',
            'dataType': 'Tabular',
            'unsupportedModels': []
        },
        {
            'methods': 'ANCHOR-TABULAR',
            'scope': 'LOCAL',
            'modelFramework': 'Scikit-learn',
            'taskType': 'CLASSIFICATION',
            'dataType': 'Tabular',
            'unsupportedModels': ['SVC']
        }
    ]


# ============================================================================
# Request/Response Fixtures
# ============================================================================

@pytest.fixture
def sample_explain_request():
    """Sample explanation request payload"""
    return {
        'modelId': 1.0,
        'datasetId': 2.0,
        'scope': 'LOCAL',
        'method': 'LIME-TABULAR',
        'inputText': None,
        'inputRow': {'feature1': 0.5, 'feature2': 0.3, 'feature3': 0.8},
        'preprocessorId': None
    }


@pytest.fixture
def sample_methods_request():
    """Sample get methods request payload"""
    return {
        'modelId': 1.0,
        'datasetId': 2.0,
        'scope': 'LOCAL'
    }


@pytest.fixture
def sample_report_request():
    """Sample report generation request"""
    return {
        'batchId': 123.0
    }


# ============================================================================
# Logger Mock Fixture
# ============================================================================

@pytest.fixture
def mock_logger():
    """Mock CustomLogger"""
    logger = MagicMock()
    logger.info = MagicMock()
    logger.error = MagicMock()
    logger.debug = MagicMock()
    logger.warning = MagicMock()
    return logger


# ============================================================================
# HTTP Request Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_requests():
    """Mock requests library"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value={'prediction': [0, 1], 'status': 'success'})
    mock_response.text = '{"prediction": [0, 1], "status": "success"}'
    mock_response.content = b'binary_content'
    mock_response.raise_for_status = MagicMock()
    return mock_response


# ============================================================================
# FastAPI Test Client Fixture
# ============================================================================

@pytest.fixture
def test_app():
    """Create a test FastAPI application"""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    
    app = FastAPI()
    return TestClient(app)


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_files():
    """Cleanup any temporary files after each test"""
    yield
    # Cleanup logic if needed
    test_files = ['model.h5', 'test_output.json', 'test_output.html']
    for f in test_files:
        if os.path.exists(f):
            try:
                os.remove(f)
            except:
                pass
