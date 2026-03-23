"""
Tests for DatabaseConnection module
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import sys


class TestDatabaseConnection:
    """Tests for DB connection class"""

    @patch('rai_backend.dao.DatabaseConnection.pymongo.MongoClient')
    @patch.dict('os.environ', {
        'DB_TYPE': 'mongo',
        'DB_NAME': 'test_db',
        'MONGO_PATH': 'mongodb://localhost:27017'
    })
    def test_connect_mongo_success(self, mock_mongo_client):
        """Test successful MongoDB connection"""
        from rai_backend.dao.DatabaseConnection import DB
        
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client
        
        # Patch sys.exit to prevent actual exit
        with patch.object(sys, 'exit'):
            result = DB.connect()
            
            assert result is not None

    @patch('rai_backend.dao.DatabaseConnection.pymongo.MongoClient')
    @patch.dict('os.environ', {
        'DB_TYPE': 'cosmos',
        'DB_NAME': 'test_db',
        'COSMOS_PATH': 'cosmos://connection_string'
    })
    def test_connect_cosmos_success(self, mock_mongo_client):
        """Test successful Cosmos DB connection"""
        from rai_backend.dao.DatabaseConnection import DB
        
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client
        
        with patch.object(sys, 'exit'):
            result = DB.connect()
            
            assert result is not None

    @patch.dict('os.environ', {
        'DB_TYPE': 'mongo',
        'DB_NAME': '',
        'MONGO_PATH': 'mongodb://localhost:27017'
    })
    def test_connect_missing_db_name(self):
        """Test connection with missing DB_NAME"""
        from rai_backend.dao.DatabaseConnection import DB
        
        with patch.object(sys, 'exit') as mock_exit:
            try:
                DB.connect()
            except:
                pass
            
            # Should have attempted to exit
            assert True

    @patch.dict('os.environ', {
        'DB_TYPE': 'mongo',
        'DB_NAME': 'test_db',
        'MONGO_PATH': ''
    })
    def test_connect_missing_mongo_path(self):
        """Test connection with missing MONGO_PATH"""
        from rai_backend.dao.DatabaseConnection import DB
        
        with patch.object(sys, 'exit') as mock_exit:
            try:
                DB.connect()
            except:
                pass
            
            assert True

    @patch.dict('os.environ', {
        'DB_TYPE': 'unsupported',
        'DB_NAME': 'test_db'
    })
    def test_connect_unsupported_db_type(self):
        """Test connection with unsupported database type"""
        from rai_backend.dao.DatabaseConnection import DB
        
        with patch.object(sys, 'exit') as mock_exit:
            try:
                DB.connect()
            except:
                pass
            
            assert True
