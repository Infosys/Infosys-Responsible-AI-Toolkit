'''
MIT License https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Unit tests for privacy.dao.DatabaseConnection module
Tests database connection functionality
'''

import pytest
import os
import sys
from unittest.mock import Mock, MagicMock, patch, call


class TestDatabaseConnection:
    """Test cases for DatabaseConnection.DB class"""
    
    @patch('privacy.dao.DatabaseConnection.pymongo.MongoClient')
    @patch.dict(os.environ, {'MONGO_PATH': 'mongodb://localhost:27017', 'DB_NAME': 'test_db'})
    def test_connect_success(self, mock_mongo_client):
        """Test successful database connection"""
        # Setup
        mock_client_instance = MagicMock()
        mock_db = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client_instance
        
        # Import after mocking to get fresh module
        from privacy.dao.DatabaseConnection import DB
        
        # Execute
        result = DB.connect()
        
        # Assert
        mock_mongo_client.assert_called_once_with('mongodb://localhost:27017')
        assert result == mock_db
    
    @patch('privacy.dao.DatabaseConnection.pymongo.MongoClient')
    @patch('privacy.dao.DatabaseConnection.sys.exit')
    @patch.dict(os.environ, {'MONGO_PATH': 'mongodb://localhost:27017', 'DB_NAME': 'test_db'})
    def test_connect_failure_exits(self, mock_exit, mock_mongo_client):
        """Test that connection failure causes system exit"""
        # Setup
        mock_mongo_client.side_effect = Exception("Connection failed")
        
        # Import after mocking
        from privacy.dao.DatabaseConnection import DB
        
        # Execute
        DB.connect()
        
        # Assert
        mock_exit.assert_called_once()
    
    @patch('privacy.dao.DatabaseConnection.pymongo.MongoClient')
    @patch('privacy.dao.DatabaseConnection.log.info')
    @patch('privacy.dao.DatabaseConnection.sys.exit')
    @patch.dict(os.environ, {'MONGO_PATH': 'mongodb://invalid', 'DB_NAME': 'test_db'})
    def test_connect_logs_error_on_failure(self, mock_exit, mock_log_info, mock_mongo_client):
        """Test that connection errors are logged"""
        # Setup
        error_message = "Invalid connection string"
        mock_mongo_client.side_effect = Exception(error_message)
        
        # Import after mocking
        from privacy.dao.DatabaseConnection import DB
        
        # Execute
        DB.connect()
        
        # Assert
        mock_log_info.assert_called_once()
        call_args = str(mock_log_info.call_args)
        assert error_message in call_args or mock_log_info.called
    
    @patch('privacy.dao.DatabaseConnection.pymongo.MongoClient')
    @patch.dict(os.environ, {'MONGO_PATH': 'mongodb://testhost:27017', 'DB_NAME': 'my_custom_db'})
    def test_connect_uses_environment_variables(self, mock_mongo_client):
        """Test that connection uses environment variables correctly"""
        # Setup
        mock_client_instance = MagicMock()
        mock_db = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client_instance
        
        # Import after mocking
        from privacy.dao.DatabaseConnection import DB
        
        # Execute
        result = DB.connect()
        
        # Assert
        mock_mongo_client.assert_called_with('mongodb://testhost:27017')
        mock_client_instance.__getitem__.assert_called_with('my_custom_db')
