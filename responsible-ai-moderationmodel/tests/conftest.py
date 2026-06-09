"""
Pytest configuration file with shared fixtures for testing.
"""
import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Mock heavy ML model dependencies before any imports
torch_mock = MagicMock()
torch_mock.optim = MagicMock()
torch_mock.nn = MagicMock()
torch_mock.device = MagicMock()
sys.modules['torch'] = torch_mock
sys.modules['torch.optim'] = torch_mock.optim
sys.modules['torch.nn'] = torch_mock.nn

# Create transformers mock with a proper pipeline function
transformers_mock = MagicMock()
# Make pipeline return a callable mock by default
transformers_mock.pipeline = MagicMock(return_value=MagicMock())
sys.modules['transformers'] = transformers_mock

sys.modules['tensorflow'] = MagicMock()
sys.modules['detoxify'] = MagicMock()
sys.modules['presidio_analyzer'] = MagicMock()
sys.modules['presidio_anonymizer'] = MagicMock()
sys.modules['privacy'] = MagicMock()
sys.modules['privacy.privacy'] = MagicMock()
sys.modules['spacy'] = MagicMock()
sys.modules['sentence_transformers'] = MagicMock()


@pytest.fixture
def mock_logger():
    """Mock the CustomLogger to avoid actual logging during tests."""
    with patch('config.logger.CustomLogger') as mock_log:
        logger_instance = Mock()
        mock_log.return_value = logger_instance
        yield logger_instance


@pytest.fixture
def app():
    """Create and configure a Flask app instance for testing."""
    app = Flask(__name__)
    app.config.update({
        "TESTING": True,
    })
    
    # Import and patch before registering blueprint
    from routing import healthCheckRouter
    with patch.object(healthCheckRouter, 'model_health', return_value=('healthy', [])):
        app.register_blueprint(healthCheckRouter.health_check_router, url_prefix='/rai/v1/raimoderationmodels')
    
    yield app


@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner for the Flask app."""
    return app.test_cli_runner()


@pytest.fixture
def sample_text():
    """Provide sample text for testing."""
    return "This is a test message"


@pytest.fixture
def sample_payload():
    """Provide a sample payload for testing."""
    return {
        "text": "This is a test message"
    }


@pytest.fixture
def sample_embedding_payload():
    """Provide a sample embedding payload for testing."""
    return {
        "text": "This is a test message for embedding"
    }


@pytest.fixture
def sample_gibberish_payload():
    """Provide a sample gibberish payload for testing."""
    return {
        "text": "This is a test message",
        "labels": ["word salad", "noise", "mild gibberish", "clean"]
    }


@pytest.fixture
def sample_topic_payload():
    """Provide a sample topic payload for testing."""
    return {
        "text": "This is a test message",
        "model": "deberta",
        "labels": ["violence", "hate"]
    }


@pytest.fixture
def mock_uuid():
    """Mock UUID generation for consistent test results."""
    with patch('uuid.uuid4') as mock:
        mock.return_value.hex = 'test-uuid-1234'
        yield mock


@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset all module-level mocks before each test to prevent state pollution."""
    # Reset transformers mock which is used by pipeline
    if 'transformers' in sys.modules and hasattr(sys.modules['transformers'], 'reset_mock'):
        sys.modules['transformers'].reset_mock()
    
    # Reset other ML mocks
    for module_name in ['torch', 'tensorflow', 'detoxify', 'presidio_analyzer', 'presidio_anonymizer', 'spacy', 'sentence_transformers']:
        if module_name in sys.modules and hasattr(sys.modules[module_name], 'reset_mock'):
            sys.modules[module_name].reset_mock()
    
    yield
