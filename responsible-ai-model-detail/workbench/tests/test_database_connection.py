"""
Unit tests for DatabaseConnection module.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestDatabaseConnection:
    """Tests for DB.connect method."""
    
    @patch('app.dao.DatabaseConnection.pymongo.MongoClient')
    @patch('app.dao.DatabaseConnection.os.getenv')
    def test_connect_mongo_success(self, mock_getenv, mock_mongo_client):
        # Mock environment variables
        def getenv_side_effect(key, default=None):
            env_vars = {
                'DB_TYPE': 'mongo',
                'MONGO_PATH': 'mongodb://localhost:27017',
                'DB_NAME': 'testdb'
            }
            return env_vars.get(key, default)
        
        mock_getenv.side_effect = getenv_side_effect
        
        # Mock MongoDB client and database
        mock_client_instance = MagicMock()
        mock_db = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client_instance
        
        from app.dao.DatabaseConnection import DB
        result = DB.connect()
        
        assert result is not None
        mock_mongo_client.assert_called_once_with('mongodb://localhost:27017')
    
    @patch('app.dao.DatabaseConnection.pymongo.MongoClient')
    @patch('app.dao.DatabaseConnection.os.getenv')
    def test_connect_cosmos_success(self, mock_getenv, mock_mongo_client):
        # Mock environment variables
        def getenv_side_effect(key, default=None):
            env_vars = {
                'DB_TYPE': 'cosmos',
                'COSMOS_PATH': 'mongodb://cosmos.azure.com:10255',
                'DB_NAME': 'cosmosdb'
            }
            return env_vars.get(key, default)
        
        mock_getenv.side_effect = getenv_side_effect
        
        # Mock MongoDB client and database
        mock_client_instance = MagicMock()
        mock_db = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client_instance
        
        from app.dao.DatabaseConnection import DB
        result = DB.connect()
        
        assert result is not None
        mock_mongo_client.assert_called_once_with('mongodb://cosmos.azure.com:10255')
    
    @patch('app.dao.DatabaseConnection.pymongo.MongoClient')
    @patch('app.dao.DatabaseConnection.os.getenv')
    def test_connect_default_mongo(self, mock_getenv, mock_mongo_client):
        # Mock environment variables with default
        def getenv_side_effect(key, default=None):
            env_vars = {
                'MONGO_PATH': 'mongodb://localhost:27017',
                'DB_NAME': 'defaultdb'
            }
            if key == 'DB_TYPE':
                return default  # Will return 'mongo' as default
            return env_vars.get(key, default)
        
        mock_getenv.side_effect = getenv_side_effect
        
        # Mock MongoDB client and database
        mock_client_instance = MagicMock()
        mock_db = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client_instance
        
        from app.dao.DatabaseConnection import DB
        result = DB.connect()
        
        assert result is not None
    
    @patch('app.dao.DatabaseConnection.pymongo.MongoClient')
    @patch('app.dao.DatabaseConnection.os.getenv')
    @patch('app.dao.DatabaseConnection.sys.exit')
    def test_connect_unsupported_db_type(self, mock_exit, mock_getenv, mock_mongo_client):
        # Mock environment variables with unsupported DB type
        def getenv_side_effect(key, default=None):
            env_vars = {
                'DB_TYPE': 'unsupported_db',
                'DB_NAME': 'testdb'
            }
            return env_vars.get(key, default)
        
        mock_getenv.side_effect = getenv_side_effect
        
        from app.dao.DatabaseConnection import DB
        DB.connect()
        
        # Should call sys.exit() due to unsupported DB type
        mock_exit.assert_called_once()
    
    @patch('app.dao.DatabaseConnection.pymongo.MongoClient')
    @patch('app.dao.DatabaseConnection.os.getenv')
    @patch('app.dao.DatabaseConnection.sys.exit')
    def test_connect_connection_error(self, mock_exit, mock_getenv, mock_mongo_client):
        # Mock environment variables
        def getenv_side_effect(key, default=None):
            env_vars = {
                'DB_TYPE': 'mongo',
                'MONGO_PATH': 'mongodb://localhost:27017',
                'DB_NAME': 'testdb'
            }
            return env_vars.get(key, default)
        
        mock_getenv.side_effect = getenv_side_effect
        
        # Simulate connection error
        mock_mongo_client.side_effect = Exception("Connection failed")
        
        from app.dao.DatabaseConnection import DB
        DB.connect()
        
        # Should call sys.exit() due to connection error
        mock_exit.assert_called_once()
    
    @patch('app.dao.DatabaseConnection.pymongo.MongoClient')
    @patch('app.dao.DatabaseConnection.os.getenv')
    def test_connect_case_insensitive_db_type(self, mock_getenv, mock_mongo_client):
        # Test with uppercase DB_TYPE
        def getenv_side_effect(key, default=None):
            env_vars = {
                'DB_TYPE': 'MONGO',  # Uppercase
                'MONGO_PATH': 'mongodb://localhost:27017',
                'DB_NAME': 'testdb'
            }
            return env_vars.get(key, default)
        
        mock_getenv.side_effect = getenv_side_effect
        
        # Mock MongoDB client and database
        mock_client_instance = MagicMock()
        mock_db = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client_instance
        
        from app.dao.DatabaseConnection import DB
        result = DB.connect()
        
        assert result is not None
        mock_mongo_client.assert_called_once()
    
    @patch('app.dao.DatabaseConnection.pymongo.MongoClient')
    @patch('app.dao.DatabaseConnection.os.getenv')
    def test_connect_mixed_case_db_type(self, mock_getenv, mock_mongo_client):
        # Test with mixed case DB_TYPE
        def getenv_side_effect(key, default=None):
            env_vars = {
                'DB_TYPE': 'CoSmOs',  # Mixed case
                'COSMOS_PATH': 'mongodb://cosmos.azure.com:10255',
                'DB_NAME': 'cosmosdb'
            }
            return env_vars.get(key, default)
        
        mock_getenv.side_effect = getenv_side_effect
        
        # Mock MongoDB client and database
        mock_client_instance = MagicMock()
        mock_db = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client_instance
        
        from app.dao.DatabaseConnection import DB
        result = DB.connect()
        
        assert result is not None
    
    @patch('app.dao.DatabaseConnection.pymongo.MongoClient')
    @patch('app.dao.DatabaseConnection.os.getenv')
    def test_connect_returns_database_object(self, mock_getenv, mock_mongo_client):
        # Mock environment variables
        def getenv_side_effect(key, default=None):
            env_vars = {
                'DB_TYPE': 'mongo',
                'MONGO_PATH': 'mongodb://localhost:27017',
                'DB_NAME': 'testdb'
            }
            return env_vars.get(key, default)
        
        mock_getenv.side_effect = getenv_side_effect
        
        # Mock MongoDB client and database with specific attributes
        mock_client_instance = MagicMock()
        mock_db = MagicMock()
        mock_db.name = 'testdb'
        mock_client_instance.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client_instance
        
        from app.dao.DatabaseConnection import DB
        result = DB.connect()
        
        assert result is not None
        assert result.name == 'testdb'
