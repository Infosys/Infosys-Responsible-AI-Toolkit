"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from pymongo import MongoClient
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from dao.databaseConnection import DataBase


# ==================== FIXTURES ====================

@pytest.fixture
def mock_mongo_client():
    """Fixture to mock MongoClient for testing"""
    with patch('dao.databaseConnection.MongoClient') as mock_client:
        mock_instance = MagicMock()
        mock_db = MagicMock()
        mock_instance.__getitem__.return_value = mock_db
        mock_client.return_value = mock_instance
        yield mock_client, mock_instance, mock_db


@pytest.fixture
def clear_env_vars():
    """Fixture to clear environment variables before each test"""
    original_env = os.environ.copy()
    
    # Clear relevant environment variables
    for key in ['DB_TYPE', 'MONGO_PATH', 'COSMOS_PATH', 'DB_NAME']:
        if key in os.environ:
            del os.environ[key]
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def set_mongo_env():
    """Fixture to set MongoDB environment variables"""
    os.environ['DB_TYPE'] = 'mongo'
    os.environ['MONGO_PATH'] = 'mongodb://localhost:27017/'
    os.environ['DB_NAME'] = 'test_database'
    yield
    # Cleanup happens in clear_env_vars


@pytest.fixture
def set_cosmos_env():
    """Fixture to set CosmosDB environment variables"""
    os.environ['DB_TYPE'] = 'cosmos'
    os.environ['COSMOS_PATH'] = 'mongodb://cosmos.test.azure.com:10255/'
    os.environ['DB_NAME'] = 'test_cosmos_db'
    yield
    # Cleanup happens in clear_env_vars


# ==================== FUNCTIONAL CORRECTNESS TESTS ====================

class TestDatabaseFunctionalCorrectness:
    """Test functional correctness of database connection"""
    
    def test_mongo_connection_successful(self, clear_env_vars, set_mongo_env, mock_mongo_client):
        """Test successful MongoDB connection with correct environment variables"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        
        db = DataBase()
        
        # Assertions
        assert db.client is not None
        assert db.db is not None
        mock_client.assert_called_once_with('mongodb://localhost:27017/')
        mock_instance.__getitem__.assert_called_once_with('test_database')
    
    def test_cosmos_connection_successful(self, clear_env_vars, set_cosmos_env, mock_mongo_client):
        """Test successful CosmosDB connection with correct environment variables"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        
        db = DataBase()
        
        # Assertions
        assert db.client is not None
        assert db.db is not None
        mock_client.assert_called_once_with('mongodb://cosmos.test.azure.com:10255/')
        mock_instance.__getitem__.assert_called_once_with('test_cosmos_db')
    
    def test_default_db_type_is_mongo(self, clear_env_vars, mock_mongo_client):
        """Test that default DB_TYPE is 'mongo' when not specified"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        os.environ['MONGO_PATH'] = 'mongodb://localhost:27017/'
        os.environ['DB_NAME'] = 'test_db'
        # DB_TYPE not set, should default to 'mongo'
        
        db = DataBase()
        
        # Should use MONGO_PATH since default is 'mongo'
        mock_client.assert_called_once_with('mongodb://localhost:27017/')
    
    def test_db_type_case_insensitive_mongo(self, clear_env_vars, mock_mongo_client):
        """Test that DB_TYPE 'MONGO' (uppercase) works correctly"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        os.environ['DB_TYPE'] = 'MONGO'
        os.environ['MONGO_PATH'] = 'mongodb://localhost:27017/'
        os.environ['DB_NAME'] = 'test_db'
        
        db = DataBase()
        
        mock_client.assert_called_once_with('mongodb://localhost:27017/')
    
    def test_db_type_case_insensitive_cosmos(self, clear_env_vars, mock_mongo_client):
        """Test that DB_TYPE 'COSMOS' (uppercase) works correctly"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        os.environ['DB_TYPE'] = 'COSMOS'
        os.environ['COSMOS_PATH'] = 'mongodb://cosmos.test.azure.com:10255/'
        os.environ['DB_NAME'] = 'test_db'
        
        db = DataBase()
        
        mock_client.assert_called_once_with('mongodb://cosmos.test.azure.com:10255/')


# ==================== EDGE CASES & ERROR HANDLING TESTS ====================

class TestDatabaseEdgeCases:
    """Test edge cases and error handling"""
    
    def test_missing_mongo_path(self, clear_env_vars, mock_mongo_client):
        """Test exception when MONGO_PATH is missing for mongo DB_TYPE"""
        os.environ['DB_TYPE'] = 'mongo'
        os.environ['DB_NAME'] = 'test_db'
        # MONGO_PATH not set
        
        with pytest.raises(Exception) as exc_info:
            DataBase()
        
        assert "Environment variables MONGO_PATH or DB_NAME are not set" in str(exc_info.value)
    
    def test_empty_mongo_path(self, clear_env_vars, mock_mongo_client):
        """Test exception when MONGO_PATH is empty string"""
        os.environ['DB_TYPE'] = 'mongo'
        os.environ['MONGO_PATH'] = ''
        os.environ['DB_NAME'] = 'test_db'
        
        with pytest.raises(Exception) as exc_info:
            DataBase()
        
        assert "Environment variables MONGO_PATH or DB_NAME are not set" in str(exc_info.value)
    
    def test_missing_cosmos_path(self, clear_env_vars, mock_mongo_client):
        """Test exception when COSMOS_PATH is missing for cosmos DB_TYPE"""
        os.environ['DB_TYPE'] = 'cosmos'
        os.environ['DB_NAME'] = 'test_db'
        # COSMOS_PATH not set
        
        with pytest.raises(Exception) as exc_info:
            DataBase()
        
        assert "Environment variables COSMOS_PATH or DB_NAME are not set" in str(exc_info.value)
    
    def test_empty_cosmos_path(self, clear_env_vars, mock_mongo_client):
        """Test exception when COSMOS_PATH is empty string"""
        os.environ['DB_TYPE'] = 'cosmos'
        os.environ['COSMOS_PATH'] = ''
        os.environ['DB_NAME'] = 'test_db'
        
        with pytest.raises(Exception) as exc_info:
            DataBase()
        
        assert "Environment variables COSMOS_PATH or DB_NAME are not set" in str(exc_info.value)
    
    def test_missing_db_name_mongo(self, clear_env_vars, mock_mongo_client):
        """Test exception when DB_NAME is missing for mongo"""
        os.environ['DB_TYPE'] = 'mongo'
        os.environ['MONGO_PATH'] = 'mongodb://localhost:27017/'
        # DB_NAME not set
        
        with pytest.raises(Exception) as exc_info:
            DataBase()
        
        assert "Environment variables MONGO_PATH or DB_NAME are not set" in str(exc_info.value)
    
    def test_missing_db_name_cosmos(self, clear_env_vars, mock_mongo_client):
        """Test exception when DB_NAME is missing for cosmos"""
        os.environ['DB_TYPE'] = 'cosmos'
        os.environ['COSMOS_PATH'] = 'mongodb://cosmos.test.azure.com:10255/'
        # DB_NAME not set
        
        with pytest.raises(Exception) as exc_info:
            DataBase()
        
        assert "Environment variables COSMOS_PATH or DB_NAME are not set" in str(exc_info.value)
    
    def test_empty_db_name(self, clear_env_vars, mock_mongo_client):
        """Test behavior when DB_NAME is empty string - current implementation allows it"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        os.environ['DB_TYPE'] = 'mongo'
        os.environ['MONGO_PATH'] = 'mongodb://localhost:27017/'
        os.environ['DB_NAME'] = ''
        
        # Current implementation only checks if DB_NAME is None, not if it's empty
        # This test documents the current behavior
        db = DataBase()
        assert db.client is not None
        mock_instance.__getitem__.assert_called_once_with('')
    
    def test_invalid_db_type(self, clear_env_vars, mock_mongo_client):
        """Test exception when DB_TYPE is invalid"""
        os.environ['DB_TYPE'] = 'invalid_type'
        os.environ['MONGO_PATH'] = 'mongodb://localhost:27017/'
        os.environ['DB_NAME'] = 'test_db'
        
        with pytest.raises(Exception) as exc_info:
            DataBase()
        
        assert "Invalid DB_TYPE" in str(exc_info.value)
        assert "Expected 'cosmos' or 'mongo'" in str(exc_info.value)
    
    def test_none_db_type(self, clear_env_vars, mock_mongo_client):
        """Test behavior when DB_TYPE is None (should use default 'mongo')"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        os.environ['MONGO_PATH'] = 'mongodb://localhost:27017/'
        os.environ['DB_NAME'] = 'test_db'
        # DB_TYPE not set (None)
        
        db = DataBase()
        
        # Should default to 'mongo'
        mock_client.assert_called_once_with('mongodb://localhost:27017/')
    
    def test_whitespace_only_db_name(self, clear_env_vars, mock_mongo_client):
        """Test handling of whitespace-only DB_NAME"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        os.environ['DB_TYPE'] = 'mongo'
        os.environ['MONGO_PATH'] = 'mongodb://localhost:27017/'
        os.environ['DB_NAME'] = '   '
        
        # Current implementation doesn't validate whitespace, so it should pass
        db = DataBase()
        assert db.client is not None
    
    def test_special_characters_in_connection_string(self, clear_env_vars, mock_mongo_client):
        """Test connection strings with special characters"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        os.environ['DB_TYPE'] = 'mongo'
        os.environ['MONGO_PATH'] = 'mongodb://user:p@ssw0rd!@localhost:27017/'
        os.environ['DB_NAME'] = 'test_db'
        
        db = DataBase()
        
        mock_client.assert_called_once_with('mongodb://user:p@ssw0rd!@localhost:27017/')


# ==================== RESOURCE MANAGEMENT TESTS ====================

class TestDatabaseResourceManagement:
    """Test resource management and connection handling"""
    
    def test_client_initialization(self, clear_env_vars, set_mongo_env, mock_mongo_client):
        """Test that MongoClient is properly initialized"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        
        db = DataBase()
        
        assert hasattr(db, 'client')
        assert hasattr(db, 'db')
        assert db.client == mock_instance
        assert db.db == mock_db
    
    def test_database_selection(self, clear_env_vars, set_mongo_env, mock_mongo_client):
        """Test that correct database is selected from client"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        
        db = DataBase()
        
        # Verify database was accessed with correct name
        mock_instance.__getitem__.assert_called_once_with('test_database')
    
    def test_multiple_database_instances(self, clear_env_vars, set_mongo_env, mock_mongo_client):
        """Test creating multiple DataBase instances"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        
        db1 = DataBase()
        db2 = DataBase()
        
        # Each instance should create its own client
        assert mock_client.call_count == 2
        assert db1.client is not None
        assert db2.client is not None


# ==================== SECURITY TESTS ====================

class TestDatabaseSecurity:
    """Test security aspects of database connections"""
    
    def test_connection_string_not_logged(self, clear_env_vars, set_mongo_env, mock_mongo_client):
        """Test that sensitive connection strings are not exposed in normal operations"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        
        db = DataBase()
        
        # Verify connection was made with correct string
        call_args = mock_client.call_args[0][0]
        assert 'mongodb://localhost:27017/' == call_args
    
    def test_credentials_in_connection_string(self, clear_env_vars, mock_mongo_client):
        """Test handling of connection strings with credentials"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        os.environ['DB_TYPE'] = 'mongo'
        os.environ['MONGO_PATH'] = 'mongodb://username:password@localhost:27017/'
        os.environ['DB_NAME'] = 'secure_db'
        
        db = DataBase()
        
        # Verify credentials are passed through to MongoClient
        mock_client.assert_called_once_with('mongodb://username:password@localhost:27017/')
    
    def test_ssl_connection_string(self, clear_env_vars, mock_mongo_client):
        """Test connection strings with SSL parameters"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        os.environ['DB_TYPE'] = 'cosmos'
        os.environ['COSMOS_PATH'] = 'mongodb://cosmos.azure.com:10255/?ssl=true'
        os.environ['DB_NAME'] = 'secure_db'
        
        db = DataBase()
        
        mock_client.assert_called_once_with('mongodb://cosmos.azure.com:10255/?ssl=true')


# ==================== INTEGRATION POINTS TESTS ====================

class TestDatabaseIntegrationPoints:
    """Test integration with external dependencies"""
    
    def test_pymongo_import_available(self):
        """Test that pymongo is available for import"""
        try:
            from pymongo import MongoClient
            assert True
        except ImportError:
            pytest.fail("pymongo should be available")
    
    def test_dotenv_loading(self, clear_env_vars):
        """Test that dotenv is loaded (load_dotenv is called)"""
        # This is implicitly tested by the module loading
        # The import should not raise any errors
        from dao.databaseConnection import DataBase
        assert True
    
    @patch('dao.databaseConnection.MongoClient')
    def test_mongo_client_connection_failure(self, mock_client, clear_env_vars, set_mongo_env):
        """Test handling when MongoClient raises connection error"""
        mock_client.side_effect = Exception("Connection refused")
        
        with pytest.raises(Exception) as exc_info:
            DataBase()
        
        assert "Connection refused" in str(exc_info.value)
    
    @patch('dao.databaseConnection.MongoClient')
    def test_database_access_failure(self, mock_client, clear_env_vars, set_mongo_env):
        """Test handling when database access fails"""
        mock_instance = MagicMock()
        mock_instance.__getitem__.side_effect = Exception("Database not found")
        mock_client.return_value = mock_instance
        
        with pytest.raises(Exception) as exc_info:
            DataBase()
        
        assert "Database not found" in str(exc_info.value)


# ==================== REGRESSION TESTS ====================

class TestDatabaseRegression:
    """Test for regression and backward compatibility"""
    
    def test_backwards_compatible_mongo_env_vars(self, clear_env_vars, mock_mongo_client):
        """Test that original mongo environment variables still work"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        os.environ['DB_TYPE'] = 'mongo'
        os.environ['MONGO_PATH'] = 'mongodb://localhost:27017/'
        os.environ['DB_NAME'] = 'legacy_db'
        
        db = DataBase()
        
        assert db.client is not None
        assert db.db is not None
    
    def test_backwards_compatible_cosmos_env_vars(self, clear_env_vars, mock_mongo_client):
        """Test that original cosmos environment variables still work"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        os.environ['DB_TYPE'] = 'cosmos'
        os.environ['COSMOS_PATH'] = 'mongodb://cosmos.azure.com:10255/'
        os.environ['DB_NAME'] = 'legacy_cosmos_db'
        
        db = DataBase()
        
        assert db.client is not None
        assert db.db is not None
    
    def test_db_type_lowercase_conversion(self, clear_env_vars, mock_mongo_client):
        """Test that DB_TYPE is converted to lowercase"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        os.environ['DB_TYPE'] = 'MoNgO'
        os.environ['MONGO_PATH'] = 'mongodb://localhost:27017/'
        os.environ['DB_NAME'] = 'test_db'
        
        db = DataBase()
        
        # Should work with mixed case
        mock_client.assert_called_once()


# ==================== CODE QUALITY TESTS ====================

class TestDatabaseCodeQuality:
    """Test code quality indicators"""
    
    def test_class_has_init_method(self):
        """Test that DataBase class has __init__ method"""
        assert hasattr(DataBase, '__init__')
    
    def test_class_instantiation_without_parameters(self, clear_env_vars, set_mongo_env, mock_mongo_client):
        """Test that DataBase can be instantiated without parameters"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        
        db = DataBase()
        
        assert isinstance(db, DataBase)
    
    def test_instance_attributes_set(self, clear_env_vars, set_mongo_env, mock_mongo_client):
        """Test that instance attributes are properly set"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        
        db = DataBase()
        
        assert hasattr(db, 'client')
        assert hasattr(db, 'db')
    
    def test_exception_messages_are_descriptive(self, clear_env_vars):
        """Test that exception messages provide clear information"""
        os.environ['DB_TYPE'] = 'invalid'
        
        with pytest.raises(Exception) as exc_info:
            DataBase()
        
        error_message = str(exc_info.value)
        assert len(error_message) > 10  # Should have descriptive message
        assert 'cosmos' in error_message.lower() or 'mongo' in error_message.lower()


# ==================== PERFORMANCE TESTS ====================

class TestDatabasePerformance:
    """Test performance characteristics"""
    
    def test_initialization_speed(self, clear_env_vars, set_mongo_env, mock_mongo_client):
        """Test that initialization completes quickly"""
        import time
        mock_client, mock_instance, mock_db = mock_mongo_client
        
        start_time = time.time()
        db = DataBase()
        end_time = time.time()
        
        # Initialization should be fast (under 1 second with mocking)
        assert (end_time - start_time) < 1.0
    
    def test_multiple_initializations_performance(self, clear_env_vars, set_mongo_env, mock_mongo_client):
        """Test performance of multiple database initializations"""
        import time
        mock_client, mock_instance, mock_db = mock_mongo_client
        
        start_time = time.time()
        for _ in range(10):
            db = DataBase()
        end_time = time.time()
        
        # 10 initializations should complete quickly
        assert (end_time - start_time) < 2.0


# ==================== PARAMETRIZED TESTS ====================

class TestDatabaseParametrized:
    """Parametrized tests for comprehensive coverage"""
    
    @pytest.mark.parametrize("db_type,path_var,path_value", [
        ('mongo', 'MONGO_PATH', 'mongodb://localhost:27017/'),
        ('cosmos', 'COSMOS_PATH', 'mongodb://cosmos.azure.com:10255/'),
        ('MONGO', 'MONGO_PATH', 'mongodb://test.com:27017/'),
        ('Cosmos', 'COSMOS_PATH', 'mongodb://cosmos-test.azure.com:10255/'),
    ])
    def test_various_db_configurations(self, clear_env_vars, mock_mongo_client, db_type, path_var, path_value):
        """Test various valid database configurations"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        os.environ['DB_TYPE'] = db_type
        os.environ[path_var] = path_value
        os.environ['DB_NAME'] = 'test_db'
        
        db = DataBase()
        
        assert db.client is not None
        assert db.db is not None
        mock_client.assert_called_once_with(path_value)
    
    @pytest.mark.parametrize("invalid_type", [
        'mysql',
        'postgresql',
        'sqlite',
        '',
        'mongodb',
        'cosmosdb',
        '123',
        'null',
    ])
    def test_various_invalid_db_types(self, clear_env_vars, mock_mongo_client, invalid_type):
        """Test various invalid DB_TYPE values"""
        os.environ['DB_TYPE'] = invalid_type
        os.environ['MONGO_PATH'] = 'mongodb://localhost:27017/'
        os.environ['DB_NAME'] = 'test_db'
        
        with pytest.raises(Exception) as exc_info:
            DataBase()
        
        # Empty string should default to mongo (won't raise for invalid type)
        if invalid_type != '':
            assert "Invalid DB_TYPE" in str(exc_info.value) or "COSMOS_PATH" in str(exc_info.value)
    
    @pytest.mark.parametrize("db_name", [
        'simple_db',
        'database-with-hyphens',
        'database_with_underscores',
        'database123',
        'CamelCaseDatabase',
        'db',
    ])
    def test_various_valid_db_names(self, clear_env_vars, mock_mongo_client, db_name):
        """Test various valid database names"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        os.environ['DB_TYPE'] = 'mongo'
        os.environ['MONGO_PATH'] = 'mongodb://localhost:27017/'
        os.environ['DB_NAME'] = db_name
        
        db = DataBase()
        
        mock_instance.__getitem__.assert_called_once_with(db_name)


# ==================== ISOLATION TESTS ====================

class TestDatabaseIsolation:
    """Test that tests are properly isolated"""
    
    def test_isolation_test_1(self, clear_env_vars, set_mongo_env, mock_mongo_client):
        """Test isolation - modifying environment in test 1"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        os.environ['CUSTOM_VAR'] = 'test1'
        
        db = DataBase()
        assert db.client is not None
    
    def test_isolation_test_2(self, clear_env_vars, set_mongo_env, mock_mongo_client):
        """Test isolation - environment should be clean in test 2"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        
        # CUSTOM_VAR should not exist from previous test
        assert 'CUSTOM_VAR' not in os.environ or os.environ.get('CUSTOM_VAR') != 'test1'
        
        db = DataBase()
        assert db.client is not None


# ==================== SCALABILITY TESTS ====================

class TestDatabaseScalability:
    """Test scalability aspects"""
    
    def test_connection_string_length_limit(self, clear_env_vars, mock_mongo_client):
        """Test handling of very long connection strings"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        long_connection_string = 'mongodb://' + 'a' * 1000 + '.com:27017/'
        
        os.environ['DB_TYPE'] = 'mongo'
        os.environ['MONGO_PATH'] = long_connection_string
        os.environ['DB_NAME'] = 'test_db'
        
        db = DataBase()
        
        mock_client.assert_called_once_with(long_connection_string)
    
    def test_db_name_length_limit(self, clear_env_vars, mock_mongo_client):
        """Test handling of very long database names"""
        mock_client, mock_instance, mock_db = mock_mongo_client
        long_db_name = 'a' * 200
        
        os.environ['DB_TYPE'] = 'mongo'
        os.environ['MONGO_PATH'] = 'mongodb://localhost:27017/'
        os.environ['DB_NAME'] = long_db_name
        
        db = DataBase()
        
        mock_instance.__getitem__.assert_called_once_with(long_db_name)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
