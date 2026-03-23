"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Pytest configuration and common fixtures for tests
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from typing import Generator
import os

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Set test environment variables
os.environ.setdefault("allow_origin", "*")
os.environ.setdefault("allow_method", "GET,POST,PUT,DELETE,PATCH,OPTIONS")
os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "test_db")


@pytest.fixture
def mock_mongo_client():
    """Mock MongoDB client"""
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()
    
    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection
    
    return mock_client


@pytest.fixture
def mock_logger():
    """Mock CustomLogger"""
    mock_log = MagicMock()
    mock_log.info = MagicMock()
    mock_log.error = MagicMock()
    mock_log.warning = MagicMock()
    mock_log.debug = MagicMock()
    return mock_log


@pytest.fixture
def sample_account_data():
    """Sample account data for testing"""
    return {
        "accountId": "test_account_123",
        "accountName": "Test Account",
        "isActive": True,
        "createdDate": "2024-01-01T00:00:00",
        "updatedDate": "2024-01-01T00:00:00"
    }


@pytest.fixture
def sample_recognizer_data():
    """Sample recognizer data for testing"""
    return {
        "recognizerId": "recognizer_123",
        "recognizerName": "Test Recognizer",
        "entityType": "EMAIL",
        "pattern": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "isActive": True
    }


@pytest.fixture
def sample_openai_config():
    """Sample OpenAI config for testing"""
    return {
        "configId": "config_123",
        "apiKey": "sk-test-key",
        "model": "gpt-4",
        "temperature": 0.7,
        "maxTokens": 1000
    }


@pytest.fixture
def sample_fm_config():
    """Sample FM config for testing"""
    return {
        "fmConfigId": "fm_config_123",
        "accountId": "test_account_123",
        "toxicityThreshold": 0.8,
        "enableModeration": True,
        "restrictedTopics": ["violence", "hate"]
    }


@pytest.fixture
def mock_database_connection():
    """Mock database connection"""
    with patch('rai_admin.dao.DatabaseConnection.DatabaseConnection') as mock_db:
        mock_instance = MagicMock()
        mock_db.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_pymongo():
    """Mock pymongo module"""
    with patch('pymongo.MongoClient') as mock_client:
        yield mock_client


@pytest.fixture
async def async_mock_response():
    """Create an async mock response"""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={"success": True})
    return mock_response


@pytest.fixture
def mock_request():
    """Mock FastAPI Request object"""
    mock_req = MagicMock()
    mock_req.headers = {"Authorization": "Bearer test_token"}
    mock_req.client = MagicMock()
    mock_req.client.host = "127.0.0.1"
    return mock_req


@pytest.fixture
def mock_file_upload():
    """Mock file upload"""
    mock_file = MagicMock()
    mock_file.filename = "test.txt"
    mock_file.content_type = "text/plain"
    mock_file.file = MagicMock()
    mock_file.read = AsyncMock(return_value=b"test content")
    return mock_file
