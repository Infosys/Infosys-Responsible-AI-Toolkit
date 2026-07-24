import sys
import os
import pytest
from unittest.mock import Mock, MagicMock, patch

# Add src to path for imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.dao.DatabaseConnection import DB


# ============================================================================
# Test DB.connect
# ============================================================================

class TestDBConnect:
    """Test DB.connect method"""
    
    @patch('app.dao.DatabaseConnection.os.getenv')
    @patch('app.dao.DatabaseConnection.pymongo.MongoClient')
    def test_connect_mongo_success(self, mock_mongo_client, mock_getenv):
        """Test successful MongoDB connection"""
        # Setup mocks
        mock_getenv.side_effect = lambda key, default=None: {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://localhost:27017',
            'DB_NAME': 'test_db'
        }.get(key, default)
        
        mock_db = MagicMock()
        mock_client = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client
        
        result = DB.connect()
        
        mock_mongo_client.assert_called_once_with('mongodb://localhost:27017')
        assert result == mock_db
    
    @patch('app.dao.DatabaseConnection.os.getenv')
    @patch('app.dao.DatabaseConnection.pymongo.MongoClient')
    def test_connect_mongo_default_db_type(self, mock_mongo_client, mock_getenv):
        """Test connection when DB_TYPE is not set (defaults to mongo)"""
        mock_getenv.side_effect = lambda key, default=None: {
            'MONGO_PATH': 'mongodb://localhost:27017',
            'DB_NAME': 'test_db'
        }.get(key, default)
        
        mock_db = MagicMock()
        mock_client = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client
        
        result = DB.connect()
        
        mock_mongo_client.assert_called_once_with('mongodb://localhost:27017')
        assert result == mock_db
    
    @patch('app.dao.DatabaseConnection.os.getenv')
    @patch('app.dao.DatabaseConnection.pymongo.MongoClient')
    def test_connect_mongo_case_insensitive(self, mock_mongo_client, mock_getenv):
        """Test MongoDB connection with uppercase DB_TYPE"""
        mock_getenv.side_effect = lambda key, default=None: {
            'DB_TYPE': 'MONGO',
            'MONGO_PATH': 'mongodb://localhost:27017',
            'DB_NAME': 'test_db'
        }.get(key, default)
        
        mock_db = MagicMock()
        mock_client = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client
        
        result = DB.connect()
        
        mock_mongo_client.assert_called_once_with('mongodb://localhost:27017')
        assert result == mock_db
    
    @patch('app.dao.DatabaseConnection.os.getenv')
    @patch('app.dao.DatabaseConnection.pymongo.MongoClient')
    @patch('app.dao.DatabaseConnection.sys.exit')
    def test_connect_mongo_connection_failure(self, mock_exit, mock_mongo_client, mock_getenv):
        """Test MongoDB connection failure"""
        mock_getenv.side_effect = lambda key, default=None: {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://invalid:27017',
            'DB_NAME': 'test_db'
        }.get(key, default)
        
        mock_mongo_client.side_effect = Exception("Connection refused")
        
        DB.connect()
        
        mock_exit.assert_called_once()
    
    @patch('app.dao.DatabaseConnection.os.getenv')
    @patch('app.dao.DatabaseConnection.pymongo.MongoClient')
    @patch('app.dao.DatabaseConnection.sys.exit')
    def test_connect_unsupported_db_type(self, mock_exit, mock_mongo_client, mock_getenv):
        """Test with unsupported database type"""
        mock_getenv.side_effect = lambda key, default=None: {
            'DB_TYPE': 'postgresql',
            'DB_NAME': 'test_db'
        }.get(key, default)
        
        DB.connect()
        
        mock_exit.assert_called_once()
    
    @patch('app.dao.DatabaseConnection.os.getenv')
    @patch('app.dao.DatabaseConnection.pymongo.MongoClient')
    def test_connect_with_auth(self, mock_mongo_client, mock_getenv):
        """Test MongoDB connection with authentication"""
        mongo_path = 'mongodb://user:password@localhost:27017/authDB'
        mock_getenv.side_effect = lambda key, default=None: {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': mongo_path,
            'DB_NAME': 'test_db'
        }.get(key, default)
        
        mock_db = MagicMock()
        mock_client = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client
        
        result = DB.connect()
        
        mock_mongo_client.assert_called_once_with(mongo_path)
        assert result == mock_db
    
    @patch('app.dao.DatabaseConnection.os.getenv')
    @patch('app.dao.DatabaseConnection.pymongo.MongoClient')
    def test_connect_with_options(self, mock_mongo_client, mock_getenv):
        """Test MongoDB connection with connection options"""
        mongo_path = 'mongodb://localhost:27017/?ssl=true&replicaSet=rs0'
        mock_getenv.side_effect = lambda key, default=None: {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': mongo_path,
            'DB_NAME': 'test_db'
        }.get(key, default)
        
        mock_db = MagicMock()
        mock_client = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client
        
        result = DB.connect()
        
        mock_mongo_client.assert_called_once_with(mongo_path)
        assert result == mock_db
    
    @patch('app.dao.DatabaseConnection.os.getenv')
    @patch('app.dao.DatabaseConnection.pymongo.MongoClient')
    @patch('app.dao.DatabaseConnection.sys.exit')
    def test_connect_missing_mongo_path(self, mock_exit, mock_mongo_client, mock_getenv):
        """Test connection when MONGO_PATH is missing"""
        mock_getenv.side_effect = lambda key, default=None: {
            'DB_TYPE': 'mongo',
            'DB_NAME': 'test_db'
        }.get(key, default)
        
        mock_mongo_client.side_effect = Exception("MONGO_PATH not set")
        
        DB.connect()
        
        mock_exit.assert_called_once()
    
    @patch('app.dao.DatabaseConnection.os.getenv')
    @patch('app.dao.DatabaseConnection.pymongo.MongoClient')
    @patch('app.dao.DatabaseConnection.sys.exit')
    def test_connect_empty_db_name(self, mock_exit, mock_mongo_client, mock_getenv):
        """Test connection when DB_NAME is empty"""
        mock_getenv.side_effect = lambda key, default=None: {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://localhost:27017',
            'DB_NAME': ''
        }.get(key, default)
        
        mock_client = MagicMock()
        mock_client.__getitem__.side_effect = Exception("Empty database name")
        mock_mongo_client.return_value = mock_client
        
        DB.connect()
        
        mock_exit.assert_called_once()
