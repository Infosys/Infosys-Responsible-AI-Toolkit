"""
Pytest configuration and shared fixtures for tests
"""
import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up environment variables before any imports
os.environ.setdefault('SECRET_KEY', 'test_secret_key_for_testing_only')
os.environ.setdefault('ALGORITHM', 'HS256')
os.environ.setdefault('ACCESS_TOKEN_EXPIRE_MINUTES', '30')
os.environ.setdefault('TOKEN_URL', '/authenticate')
os.environ.setdefault('MONGO_URI', 'mongodb://localhost:27017')
os.environ.setdefault('DATABASE_NAME', 'test_db')
os.environ.setdefault('DB_TYPE', 'mongo')
os.environ.setdefault('DB_NAME', 'test_rai_db')
os.environ.setdefault('MONGO_PATH', 'mongodb://localhost:27017')
os.environ.setdefault('allow_origin', '*')
os.environ.setdefault('allow_methods', 'GET,POST,PUT,DELETE')
os.environ.setdefault('AUTHENTICATE_TELEMETRY_URL', 'http://localhost:8000/authenticatetelemetry')
os.environ.setdefault('REGISTER_TELEMETRY_URL', 'http://localhost:8000/registertelemetry')
os.environ.setdefault('RAF_TELEMETRY_URL', 'http://localhost:8000/raftelemetry')
os.environ.setdefault('SSL_VERIFY', 'False')
os.environ.setdefault('TELEMETRY_FLAG', 'False')
os.environ.setdefault('ADMIN_PASSWORD', 'Admin@123')
os.environ.setdefault('USER_PASSWORD', 'User@123')

# Mock MongoDB connection at module level to prevent actual database connections during import
@pytest.fixture(scope='session', autouse=True)
def mock_mongodb():
    """Mock MongoDB connection for all tests"""
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_collection)
    
    with patch('pymongo.MongoClient') as mock_client:
        mock_client.return_value.__getitem__.return_value = mock_db
        with patch('rai_backend.dao.DatabaseConnection.DB.connect', return_value=mock_db):
            yield mock_db


@pytest.fixture
def mock_db():
    """Mock database connection"""
    mock_database = MagicMock()
    mock_collection = MagicMock()
    mock_database.__getitem__ = MagicMock(return_value=mock_collection)
    return mock_database


@pytest.fixture
def mock_user_collection():
    """Mock User collection"""
    return MagicMock()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        'id': 1,
        'login': 'testuser',
        'email': 'test@infosys.com',
        'firstName': 'Test',
        'passwordHash': 'pbkdf2:sha256:260000$test$hash',
        'activated': True,
        'authorities': ['ROLE_USER'],
        'createdBy': 'system',
        'createdDate': '2023-06-07T10:56:15.657+00:00',
        'lastModifiedBy': 'system',
        'lastModifiedDate': '2023-06-07T10:56:15.657+00:00'
    }


@pytest.fixture
def sample_new_user_request():
    """Sample new user request"""
    return {
        'email': 'newuser@infosys.com',
        'login': 'newuser',
        'cred': 'Abc@123',
        'langKey': 'en'
    }


@pytest.fixture
def sample_auth_request():
    """Sample authentication request"""
    return {
        'username': 'testuser',
        'cred': 'Abc@123',
        'rememberMe': True
    }


@pytest.fixture
def mock_logger():
    """Mock logger"""
    with patch('rai_backend.config.logger.CustomLogger') as mock:
        yield mock.return_value


@pytest.fixture
def mock_env_vars():
    """Mock environment variables"""
    env_vars = {
        'MONGO_URI': 'mongodb://localhost:27017',
        'DATABASE_NAME': 'test_db',
        'SECRET_KEY': 'test_secret_key',
        'ALGORITHM': 'HS256',
        'ACCESS_TOKEN_EXPIRE_MINUTES': '30',
        'allow_origin': '*',
        'allow_methods': 'GET,POST,PUT,DELETE',
        'AUTHENTICATE_TELEMETRY_URL': 'http://localhost:8000/authenticatetelemetry',
        'REGISTER_TELEMETRY_URL': 'http://localhost:8000/registertelemetry',
        'RAF_TELEMETRY_URL': 'http://localhost:8000/raftelemetry',
        'SSL_VERIFY': 'False'
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def mock_password_hash():
    """Mock password hashing functions"""
    with patch('werkzeug.security.generate_password_hash') as mock_gen, \
         patch('werkzeug.security.check_password_hash') as mock_check:
        mock_gen.return_value = 'hashed_password'
        mock_check.return_value = True
        yield {'generate': mock_gen, 'check': mock_check}
