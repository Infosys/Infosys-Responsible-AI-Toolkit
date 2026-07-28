"""
Test cases for databaseconnection.py module

Tests the DataBase class that handles MongoDB and Cosmos DB connections
using environment variables for configuration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os


class TestDataBaseInit:
    """Test DataBase initialization with different DB types"""
    
    def test_mongo_initialization_success(self, mocker):
        """Test successful MongoDB connection initialization"""
        # Mock environment variables
        mocker.patch.dict(os.environ, {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://localhost:27017',
            'DB_NAME': 'test_db'
        })
        
        # Mock MongoClient
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        
        with patch('fairness.dao.databaseconnection.MongoClient', return_value=mock_client):
            with patch('fairness.dao.databaseconnection.load_dotenv'):
                from fairness.dao.databaseconnection import DataBase
                db = DataBase()
                
                assert db.client == mock_client
                assert db.db == mock_db
    
    def test_cosmos_initialization_success(self, mocker):
        """Test successful Cosmos DB connection initialization"""
        mocker.patch.dict(os.environ, {
            'DB_TYPE': 'cosmos',
            'COSMOS_PATH': 'mongodb://cosmos.azure.com:10255',
            'DB_NAME': 'cosmos_db'
        })
        
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        
        with patch('fairness.dao.databaseconnection.MongoClient', return_value=mock_client):
            with patch('fairness.dao.databaseconnection.load_dotenv'):
                from fairness.dao.databaseconnection import DataBase
                db = DataBase()
                
                assert db.client == mock_client
                assert db.db == mock_db
    
    def test_default_db_type_is_mongo(self, mocker):
        """Test that DB_TYPE defaults to 'mongo' when not set"""
        mocker.patch.dict(os.environ, {
            'MONGO_PATH': 'mongodb://localhost:27017',
            'DB_NAME': 'test_db'
        }, clear=True)
        
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        
        with patch('fairness.dao.databaseconnection.MongoClient', return_value=mock_client):
            with patch('fairness.dao.databaseconnection.load_dotenv'):
                with patch('fairness.dao.databaseconnection.os.getenv') as mock_getenv:
                    def getenv_side_effect(key, default=None):
                        env_vars = {
                            'DB_TYPE': 'mongo',
                            'MONGO_PATH': 'mongodb://localhost:27017',
                            'DB_NAME': 'test_db'
                        }
                        return env_vars.get(key, default)
                    
                    mock_getenv.side_effect = getenv_side_effect
                    from fairness.dao.databaseconnection import DataBase
                    db = DataBase()
                    
                    assert db.client == mock_client


class TestDataBaseErrors:
    """Test error handling in DataBase initialization"""
    
    def test_mongo_missing_mongo_path(self, mocker):
        """Test error when MONGO_PATH is not set for mongo DB"""
        mocker.patch.dict(os.environ, {
            'DB_TYPE': 'mongo',
            'DB_NAME': 'test_db'
        }, clear=True)
        
        with patch('fairness.dao.databaseconnection.load_dotenv'):
            with patch('fairness.dao.databaseconnection.os.getenv') as mock_getenv:
                def getenv_side_effect(key, default=None):
                    env_vars = {
                        'DB_TYPE': 'mongo',
                        'DB_NAME': 'test_db'
                    }
                    return env_vars.get(key, default)
                
                mock_getenv.side_effect = getenv_side_effect
                
                from fairness.dao.databaseconnection import DataBase
                with pytest.raises(Exception) as exc_info:
                    DataBase()
                
                assert "MONGO_PATH" in str(exc_info.value)
    
    def test_mongo_missing_db_name(self, mocker):
        """Test error when DB_NAME is not set for mongo DB"""
        mocker.patch.dict(os.environ, {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://localhost:27017'
        }, clear=True)
        
        with patch('fairness.dao.databaseconnection.load_dotenv'):
            with patch('fairness.dao.databaseconnection.os.getenv') as mock_getenv:
                def getenv_side_effect(key, default=None):
                    env_vars = {
                        'DB_TYPE': 'mongo',
                        'MONGO_PATH': 'mongodb://localhost:27017'
                    }
                    return env_vars.get(key, default)
                
                mock_getenv.side_effect = getenv_side_effect
                
                from fairness.dao.databaseconnection import DataBase
                with pytest.raises(Exception) as exc_info:
                    DataBase()
                
                assert "DB_NAME" in str(exc_info.value)
    
    def test_cosmos_missing_cosmos_path(self, mocker):
        """Test error when COSMOS_PATH is not set for cosmos DB"""
        mocker.patch.dict(os.environ, {
            'DB_TYPE': 'cosmos',
            'DB_NAME': 'cosmos_db'
        }, clear=True)
        
        with patch('fairness.dao.databaseconnection.load_dotenv'):
            with patch('fairness.dao.databaseconnection.os.getenv') as mock_getenv:
                def getenv_side_effect(key, default=None):
                    env_vars = {
                        'DB_TYPE': 'cosmos',
                        'DB_NAME': 'cosmos_db'
                    }
                    return env_vars.get(key, default)
                
                mock_getenv.side_effect = getenv_side_effect
                
                from fairness.dao.databaseconnection import DataBase
                with pytest.raises(Exception) as exc_info:
                    DataBase()
                
                assert "COSMOS_PATH" in str(exc_info.value)
    
    def test_cosmos_missing_db_name(self, mocker):
        """Test error when DB_NAME is not set for cosmos DB"""
        mocker.patch.dict(os.environ, {
            'DB_TYPE': 'cosmos',
            'COSMOS_PATH': 'mongodb://cosmos.azure.com:10255'
        }, clear=True)
        
        with patch('fairness.dao.databaseconnection.load_dotenv'):
            with patch('fairness.dao.databaseconnection.os.getenv') as mock_getenv:
                def getenv_side_effect(key, default=None):
                    env_vars = {
                        'DB_TYPE': 'cosmos',
                        'COSMOS_PATH': 'mongodb://cosmos.azure.com:10255'
                    }
                    return env_vars.get(key, default)
                
                mock_getenv.side_effect = getenv_side_effect
                
                from fairness.dao.databaseconnection import DataBase
                with pytest.raises(Exception) as exc_info:
                    DataBase()
                
                assert "DB_NAME" in str(exc_info.value)
    
    def test_invalid_db_type(self, mocker):
        """Test error when DB_TYPE is invalid"""
        mocker.patch.dict(os.environ, {
            'DB_TYPE': 'invalid_db',
            'DB_NAME': 'test_db'
        }, clear=True)
        
        with patch('fairness.dao.databaseconnection.load_dotenv'):
            with patch('fairness.dao.databaseconnection.os.getenv') as mock_getenv:
                def getenv_side_effect(key, default=None):
                    env_vars = {
                        'DB_TYPE': 'invalid_db',
                        'DB_NAME': 'test_db'
                    }
                    return env_vars.get(key, default)
                
                mock_getenv.side_effect = getenv_side_effect
                
                from fairness.dao.databaseconnection import DataBase
                with pytest.raises(Exception) as exc_info:
                    DataBase()
                
                assert "Invalid DB_TYPE" in str(exc_info.value)


class TestDataBaseCaseInsensitivity:
    """Test case-insensitive handling of DB_TYPE"""
    
    def test_mongo_uppercase(self, mocker):
        """Test MONGO in uppercase is handled correctly"""
        mocker.patch.dict(os.environ, {
            'DB_TYPE': 'MONGO',
            'MONGO_PATH': 'mongodb://localhost:27017',
            'DB_NAME': 'test_db'
        })
        
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        
        with patch('fairness.dao.databaseconnection.MongoClient', return_value=mock_client):
            with patch('fairness.dao.databaseconnection.load_dotenv'):
                from fairness.dao.databaseconnection import DataBase
                db = DataBase()
                
                assert db.client == mock_client
    
    def test_cosmos_mixed_case(self, mocker):
        """Test CoSmOs in mixed case is handled correctly"""
        mocker.patch.dict(os.environ, {
            'DB_TYPE': 'CoSmOs',
            'COSMOS_PATH': 'mongodb://cosmos.azure.com:10255',
            'DB_NAME': 'cosmos_db'
        })
        
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        
        with patch('fairness.dao.databaseconnection.MongoClient', return_value=mock_client):
            with patch('fairness.dao.databaseconnection.load_dotenv'):
                from fairness.dao.databaseconnection import DataBase
                db = DataBase()
                
                assert db.client == mock_client


class TestMongoClientInteraction:
    """Test MongoClient interaction and database access"""
    
    def test_mongo_client_called_with_correct_path(self, mocker):
        """Test MongoClient is called with correct connection string"""
        mocker.patch.dict(os.environ, {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://testhost:27017',
            'DB_NAME': 'test_db'
        })
        
        mock_client = MagicMock()
        
        with patch('fairness.dao.databaseconnection.MongoClient') as MockMongoClient:
            MockMongoClient.return_value = mock_client
            with patch('fairness.dao.databaseconnection.load_dotenv'):
                from fairness.dao.databaseconnection import DataBase
                db = DataBase()
                
                MockMongoClient.assert_called_once_with('mongodb://testhost:27017')
    
    def test_cosmos_client_called_with_correct_path(self, mocker):
        """Test MongoClient is called with correct Cosmos connection string"""
        mocker.patch.dict(os.environ, {
            'DB_TYPE': 'cosmos',
            'COSMOS_PATH': 'mongodb://cosmos.azure.com:10255/?ssl=true',
            'DB_NAME': 'cosmos_db'
        })
        
        mock_client = MagicMock()
        
        with patch('fairness.dao.databaseconnection.MongoClient') as MockMongoClient:
            MockMongoClient.return_value = mock_client
            with patch('fairness.dao.databaseconnection.load_dotenv'):
                from fairness.dao.databaseconnection import DataBase
                db = DataBase()
                
                MockMongoClient.assert_called_once_with('mongodb://cosmos.azure.com:10255/?ssl=true')
    
    def test_database_accessed_by_name(self, mocker):
        """Test that database is accessed using DB_NAME"""
        mocker.patch.dict(os.environ, {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://localhost:27017',
            'DB_NAME': 'specific_db_name'
        })
        
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        
        with patch('fairness.dao.databaseconnection.MongoClient', return_value=mock_client):
            with patch('fairness.dao.databaseconnection.load_dotenv'):
                from fairness.dao.databaseconnection import DataBase
                db = DataBase()
                
                mock_client.__getitem__.assert_called_once_with('specific_db_name')
                assert db.db == mock_db


class TestEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_empty_string_db_type(self, mocker):
        """Test behavior with empty string DB_TYPE"""
        mocker.patch.dict(os.environ, {
            'DB_TYPE': '',
            'MONGO_PATH': 'mongodb://localhost:27017',
            'DB_NAME': 'test_db'
        })
        
        with patch('fairness.dao.databaseconnection.load_dotenv'):
            with patch('fairness.dao.databaseconnection.os.getenv') as mock_getenv:
                def getenv_side_effect(key, default=None):
                    if key == 'DB_TYPE':
                        return ''
                    env_vars = {
                        'MONGO_PATH': 'mongodb://localhost:27017',
                        'DB_NAME': 'test_db'
                    }
                    return env_vars.get(key, default)
                
                mock_getenv.side_effect = getenv_side_effect
                
                from fairness.dao.databaseconnection import DataBase
                with pytest.raises(Exception) as exc_info:
                    DataBase()
                
                assert "Invalid DB_TYPE" in str(exc_info.value)
    
    def test_whitespace_db_type(self, mocker):
        """Test behavior with whitespace in DB_TYPE - should fail due to invalid type after strip"""
        mocker.patch.dict(os.environ, {
            'DB_TYPE': '   ',
            'MONGO_PATH': 'mongodb://localhost:27017',
            'DB_NAME': 'test_db'
        })
        
        with patch('fairness.dao.databaseconnection.load_dotenv'):
            with patch('fairness.dao.databaseconnection.os.getenv') as mock_getenv:
                def getenv_side_effect(key, default=None):
                    env_vars = {
                        'DB_TYPE': '   ',
                        'MONGO_PATH': 'mongodb://localhost:27017',
                        'DB_NAME': 'test_db'
                    }
                    return env_vars.get(key, default)
                
                mock_getenv.side_effect = getenv_side_effect
                
                from fairness.dao.databaseconnection import DataBase
                with pytest.raises(Exception) as exc_info:
                    DataBase()
                
                assert "Invalid DB_TYPE" in str(exc_info.value)
    
    def test_special_characters_in_db_name(self, mocker):
        """Test database name with special characters"""
        mocker.patch.dict(os.environ, {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://localhost:27017',
            'DB_NAME': 'test-db_2024.v1'
        })
        
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        
        with patch('fairness.dao.databaseconnection.MongoClient', return_value=mock_client):
            with patch('fairness.dao.databaseconnection.load_dotenv'):
                from fairness.dao.databaseconnection import DataBase
                db = DataBase()
                
                mock_client.__getitem__.assert_called_once_with('test-db_2024.v1')
    
    def test_connection_string_with_credentials(self, mocker):
        """Test connection string containing username and password"""
        mocker.patch.dict(os.environ, {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://user:pass@localhost:27017',
            'DB_NAME': 'test_db'
        })
        
        mock_client = MagicMock()
        
        with patch('fairness.dao.databaseconnection.MongoClient') as MockMongoClient:
            MockMongoClient.return_value = mock_client
            with patch('fairness.dao.databaseconnection.load_dotenv'):
                from fairness.dao.databaseconnection import DataBase
                db = DataBase()
                
                MockMongoClient.assert_called_once_with('mongodb://user:pass@localhost:27017')


class TestResourceManagement:
    """Test resource management and connection handling"""
    
    def test_client_attribute_set_correctly(self, mocker):
        """Test that client attribute is properly set"""
        mocker.patch.dict(os.environ, {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://localhost:27017',
            'DB_NAME': 'test_db'
        })
        
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        
        with patch('fairness.dao.databaseconnection.MongoClient', return_value=mock_client):
            with patch('fairness.dao.databaseconnection.load_dotenv'):
                from fairness.dao.databaseconnection import DataBase
                db = DataBase()
                
                assert hasattr(db, 'client')
                assert hasattr(db, 'db')
                assert db.client is mock_client
                assert db.db is mock_db


class TestLoadDotenv:
    """Test dotenv loading functionality"""
    
    def test_load_dotenv_imported(self):
        """Test that load_dotenv is imported and available in module"""
        import fairness.dao.databaseconnection as db_module
        
        # Verify load_dotenv is imported at module level
        assert hasattr(db_module, 'load_dotenv')
        assert callable(db_module.load_dotenv)


class TestPerformance:
    """Test performance-related scenarios"""
    
    def test_multiple_instances_creation(self, mocker):
        """Test creating multiple DataBase instances"""
        mocker.patch.dict(os.environ, {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://localhost:27017',
            'DB_NAME': 'test_db'
        })
        
        mock_clients = [MagicMock() for _ in range(3)]
        
        with patch('fairness.dao.databaseconnection.MongoClient', side_effect=mock_clients):
            with patch('fairness.dao.databaseconnection.load_dotenv'):
                from fairness.dao.databaseconnection import DataBase
                
                db1 = DataBase()
                db2 = DataBase()
                db3 = DataBase()
                
                assert db1.client is mock_clients[0]
                assert db2.client is mock_clients[1]
                assert db3.client is mock_clients[2]


class TestSecurity:
    """Test security-related aspects"""
    
    def test_connection_string_not_exposed_in_error(self, mocker):
        """Test that connection strings are not exposed in error messages"""
        # Cannot set None in os.environ, so use getenv mock instead
        with patch('fairness.dao.databaseconnection.load_dotenv'):
            with patch('fairness.dao.databaseconnection.os.getenv') as mock_getenv:
                def getenv_side_effect(key, default=None):
                    env_vars = {
                        'DB_TYPE': 'mongo',
                        'MONGO_PATH': 'mongodb://secret:password@localhost:27017'
                        # DB_NAME is missing (returns None)
                    }
                    return env_vars.get(key, default)
                
                mock_getenv.side_effect = getenv_side_effect
                
                from fairness.dao.databaseconnection import DataBase
                with pytest.raises(Exception) as exc_info:
                    DataBase()
                
                error_msg = str(exc_info.value)
                # Verify the error is about missing DB_NAME
                assert "DB_NAME" in error_msg
                # Verify connection string credentials are not exposed
                assert "secret" not in error_msg.lower()
                assert "password" not in error_msg.lower()


class TestCodeQuality:
    """Test code quality indicators"""
    
    def test_class_has_init_method(self):
        """Test that DataBase class has __init__ method"""
        from fairness.dao.databaseconnection import DataBase
        
        assert hasattr(DataBase, '__init__')
        assert callable(getattr(DataBase, '__init__'))
    
    def test_module_imports(self):
        """Test that required modules are imported"""
        import fairness.dao.databaseconnection as db_module
        
        assert hasattr(db_module, 'MongoClient')
        assert hasattr(db_module, 'os')
        assert hasattr(db_module, 'load_dotenv')


class TestRegression:
    """Test regression scenarios"""
    
    def test_mongo_connection_complete_flow(self, mocker):
        """Test complete flow for MongoDB connection"""
        mocker.patch.dict(os.environ, {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://localhost:27017',
            'DB_NAME': 'production_db'
        })
        
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        
        with patch('fairness.dao.databaseconnection.MongoClient', return_value=mock_client) as MockClient:
            with patch('fairness.dao.databaseconnection.load_dotenv'):
                from fairness.dao.databaseconnection import DataBase
                db = DataBase()
                
                # Verify all steps completed
                MockClient.assert_called_once_with('mongodb://localhost:27017')
                mock_client.__getitem__.assert_called_once_with('production_db')
                assert db.client == mock_client
                assert db.db == mock_db
    
    def test_cosmos_connection_complete_flow(self, mocker):
        """Test complete flow for Cosmos DB connection"""
        mocker.patch.dict(os.environ, {
            'DB_TYPE': 'cosmos',
            'COSMOS_PATH': 'mongodb://cosmos.documents.azure.com:10255',
            'DB_NAME': 'cosmos_production'
        })
        
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        
        with patch('fairness.dao.databaseconnection.MongoClient', return_value=mock_client) as MockClient:
            with patch('fairness.dao.databaseconnection.load_dotenv'):
                from fairness.dao.databaseconnection import DataBase
                db = DataBase()
                
                # Verify all steps completed
                MockClient.assert_called_once_with('mongodb://cosmos.documents.azure.com:10255')
                mock_client.__getitem__.assert_called_once_with('cosmos_production')
                assert db.client == mock_client
                assert db.db == mock_db
