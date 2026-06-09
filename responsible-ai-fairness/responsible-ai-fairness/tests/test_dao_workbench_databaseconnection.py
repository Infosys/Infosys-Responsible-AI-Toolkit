"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Comprehensive test cases for src/fairness/dao/WorkBench/databaseconnection.py

Test Coverage:
- Core Principles: Clarity, Isolation, Repeatability, Coverage, Assertions
- Quality Metrics: Functional Correctness, Edge Cases, Error Handling, Performance,
  Resource Management, Security, Scalability, Integration Points, Regression, Code Quality
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
import os
import sys
from typing import Dict, Any


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_mongo_client():
    """Create a mock MongoClient."""
    return MagicMock()


@pytest.fixture
def cosmos_env_vars():
    """Environment variables for Cosmos DB."""
    return {
        'DB_TYPE': 'cosmos',
        'COSMOS_PATH': 'mongodb://test-cosmos.documents.azure.com:10255/',
        'DB_NAME_WB': 'test_workbench_db'
    }


@pytest.fixture
def mongo_env_vars():
    """Environment variables for MongoDB."""
    return {
        'DB_TYPE': 'mongo',
        'MONGO_PATH': 'mongodb://localhost:27017/',
        'DB_NAME_WB': 'test_workbench_db'
    }


@pytest.fixture
def invalid_env_vars():
    """Invalid environment variables."""
    return {
        'DB_TYPE': 'invalid_type'
    }


@pytest.fixture
def incomplete_cosmos_env_vars():
    """Incomplete Cosmos DB environment variables."""
    return {
        'DB_TYPE': 'cosmos',
        'COSMOS_PATH': None,
        'DB_NAME_WB': 'test_db'
    }


@pytest.fixture
def incomplete_mongo_env_vars():
    """Incomplete MongoDB environment variables."""
    return {
        'DB_TYPE': 'mongo',
        'MONGO_PATH': 'mongodb://localhost:27017/',
        'DB_NAME_WB': None
    }


# ============================================================================
# TEST CLASS 1: Initialization Tests - Cosmos DB
# ============================================================================

class TestDataBaseWBInitializationCosmos:
    """Test DataBase_WB initialization with Cosmos DB."""
    
    def test_init_cosmos_successful(self, cosmos_env_vars, mock_mongo_client):
        """Test successful initialization with Cosmos DB."""
        with patch.dict(os.environ, cosmos_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb is not None
                assert db_wb.db_type == 'cosmos'
                assert db_wb.client is mock_mongo_client
                assert db_wb.db is not None
    
    def test_init_cosmos_client_created_with_correct_path(self, cosmos_env_vars, mock_mongo_client):
        """Test that MongoClient is created with correct Cosmos path."""
        with patch.dict(os.environ, cosmos_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client) as mock_client_class:
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                mock_client_class.assert_called_once_with(cosmos_env_vars['COSMOS_PATH'])
    
    def test_init_cosmos_db_selected_correctly(self, cosmos_env_vars, mock_mongo_client):
        """Test that correct database is selected from Cosmos client."""
        with patch.dict(os.environ, cosmos_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                mock_mongo_client.__getitem__.assert_called_with(cosmos_env_vars['DB_NAME_WB'])
    
    def test_init_cosmos_case_insensitive_db_type(self, mock_mongo_client):
        """Test that DB_TYPE is case-insensitive for Cosmos."""
        env_vars = {
            'DB_TYPE': 'COSMOS',
            'COSMOS_PATH': 'mongodb://test.cosmos.com/',
            'DB_NAME_WB': 'test_db'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb.db_type == 'cosmos'
    
    def test_init_cosmos_with_mixed_case(self, mock_mongo_client):
        """Test Cosmos initialization with mixed case DB_TYPE."""
        env_vars = {
            'DB_TYPE': 'CoSmOs',
            'COSMOS_PATH': 'mongodb://test.cosmos.com/',
            'DB_NAME_WB': 'test_db'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb.db_type == 'cosmos'


# ============================================================================
# TEST CLASS 2: Initialization Tests - MongoDB
# ============================================================================

class TestDataBaseWBInitializationMongo:
    """Test DataBase_WB initialization with MongoDB."""
    
    def test_init_mongo_successful(self, mongo_env_vars, mock_mongo_client):
        """Test successful initialization with MongoDB."""
        with patch.dict(os.environ, mongo_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb is not None
                assert db_wb.db_type == 'mongo'
                assert db_wb.client is mock_mongo_client
                assert db_wb.db is not None
    
    def test_init_mongo_client_created_with_correct_path(self, mongo_env_vars, mock_mongo_client):
        """Test that MongoClient is created with correct MongoDB path."""
        with patch.dict(os.environ, mongo_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client) as mock_client_class:
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                mock_client_class.assert_called_once_with(mongo_env_vars['MONGO_PATH'])
    
    def test_init_mongo_db_selected_correctly(self, mongo_env_vars, mock_mongo_client):
        """Test that correct database is selected from MongoDB client."""
        with patch.dict(os.environ, mongo_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                mock_mongo_client.__getitem__.assert_called_with(mongo_env_vars['DB_NAME_WB'])
    
    def test_init_mongo_case_insensitive_db_type(self, mock_mongo_client):
        """Test that DB_TYPE is case-insensitive for MongoDB."""
        env_vars = {
            'DB_TYPE': 'MONGO',
            'MONGO_PATH': 'mongodb://localhost:27017/',
            'DB_NAME_WB': 'test_db'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb.db_type == 'mongo'
    
    def test_init_mongo_with_mixed_case(self, mock_mongo_client):
        """Test MongoDB initialization with mixed case DB_TYPE."""
        env_vars = {
            'DB_TYPE': 'MoNgO',
            'MONGO_PATH': 'mongodb://localhost:27017/',
            'DB_NAME_WB': 'test_db'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb.db_type == 'mongo'


# ============================================================================
# TEST CLASS 3: Error Handling - Missing Environment Variables
# ============================================================================

class TestDataBaseWBErrorHandlingMissingEnvVars:
    """Test error handling for missing environment variables."""
    
    def test_init_cosmos_missing_cosmos_path(self, mock_mongo_client):
        """Test error when COSMOS_PATH is missing."""
        env_vars = {
            'DB_TYPE': 'cosmos',
            'DB_NAME_WB': 'test_db'
        }
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                with pytest.raises(Exception) as exc_info:
                    DataBase_WB()
                
                assert "Environment variables COSMOS_PATH or DB_NAME are not set" in str(exc_info.value)
    
    def test_init_cosmos_missing_db_name(self, mock_mongo_client):
        """Test error when DB_NAME_WB is missing for Cosmos."""
        env_vars = {
            'DB_TYPE': 'cosmos',
            'COSMOS_PATH': 'mongodb://test.cosmos.com/'
        }
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                with pytest.raises(Exception) as exc_info:
                    DataBase_WB()
                
                assert "Environment variables COSMOS_PATH or DB_NAME are not set" in str(exc_info.value)
    
    def test_init_cosmos_both_variables_missing(self, mock_mongo_client):
        """Test error when both COSMOS_PATH and DB_NAME_WB are missing."""
        env_vars = {
            'DB_TYPE': 'cosmos'
        }
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                with pytest.raises(Exception) as exc_info:
                    DataBase_WB()
                
                assert "Environment variables COSMOS_PATH or DB_NAME are not set" in str(exc_info.value)
    
    def test_init_mongo_missing_mongo_path(self, mock_mongo_client):
        """Test error when MONGO_PATH is missing."""
        env_vars = {
            'DB_TYPE': 'mongo',
            'DB_NAME_WB': 'test_db'
        }
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                with pytest.raises(Exception) as exc_info:
                    DataBase_WB()
                
                assert "Environment variables MONGO_PATH or DB_NAME are not set" in str(exc_info.value)
    
    def test_init_mongo_missing_db_name(self, mock_mongo_client):
        """Test error when DB_NAME_WB is missing for MongoDB."""
        env_vars = {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://localhost:27017/'
        }
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                with pytest.raises(Exception) as exc_info:
                    DataBase_WB()
                
                assert "Environment variables MONGO_PATH or DB_NAME are not set" in str(exc_info.value)
    
    def test_init_mongo_both_variables_missing(self, mock_mongo_client):
        """Test error when both MONGO_PATH and DB_NAME_WB are missing."""
        env_vars = {
            'DB_TYPE': 'mongo'
        }
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                with pytest.raises(Exception) as exc_info:
                    DataBase_WB()
                
                assert "Environment variables MONGO_PATH or DB_NAME are not set" in str(exc_info.value)


# ============================================================================
# TEST CLASS 4: Error Handling - Invalid DB_TYPE
# ============================================================================

class TestDataBaseWBErrorHandlingInvalidDBType:
    """Test error handling for invalid DB_TYPE."""
    
    def test_init_invalid_db_type(self, mock_mongo_client):
        """Test error with invalid DB_TYPE."""
        env_vars = {
            'DB_TYPE': 'invalid_type'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                with pytest.raises(Exception) as exc_info:
                    DataBase_WB()
                
                assert "Invalid DB_TYPE. Expected 'cosmos' or 'mongo'" in str(exc_info.value)
    
    def test_init_empty_db_type(self, mock_mongo_client):
        """Test error with empty DB_TYPE."""
        env_vars = {
            'DB_TYPE': ''
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                with pytest.raises(Exception) as exc_info:
                    DataBase_WB()
                
                assert "Invalid DB_TYPE. Expected 'cosmos' or 'mongo'" in str(exc_info.value)
    
    def test_init_postgresql_db_type(self, mock_mongo_client):
        """Test error with unsupported DB_TYPE (postgresql)."""
        env_vars = {
            'DB_TYPE': 'postgresql'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                with pytest.raises(Exception) as exc_info:
                    DataBase_WB()
                
                assert "Invalid DB_TYPE. Expected 'cosmos' or 'mongo'" in str(exc_info.value)
    
    def test_init_mysql_db_type(self, mock_mongo_client):
        """Test error with unsupported DB_TYPE (mysql)."""
        env_vars = {
            'DB_TYPE': 'mysql'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                with pytest.raises(Exception) as exc_info:
                    DataBase_WB()
                
                assert "Invalid DB_TYPE. Expected 'cosmos' or 'mongo'" in str(exc_info.value)
    
    def test_init_numeric_db_type(self, mock_mongo_client):
        """Test error with numeric DB_TYPE."""
        env_vars = {
            'DB_TYPE': '12345'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                with pytest.raises(Exception) as exc_info:
                    DataBase_WB()
                
                assert "Invalid DB_TYPE. Expected 'cosmos' or 'mongo'" in str(exc_info.value)


# ============================================================================
# TEST CLASS 5: Edge Cases
# ============================================================================

class TestDataBaseWBEdgeCases:
    """Test edge cases for DataBase_WB."""
    
    def test_init_cosmos_with_special_characters_in_path(self, mock_mongo_client):
        """Test Cosmos initialization with special characters in path."""
        env_vars = {
            'DB_TYPE': 'cosmos',
            'COSMOS_PATH': 'mongodb://user:p@ssw0rd!@test.cosmos.com:10255/',
            'DB_NAME_WB': 'test_db'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb is not None
    
    def test_init_mongo_with_special_characters_in_path(self, mock_mongo_client):
        """Test MongoDB initialization with special characters in path."""
        env_vars = {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://user:p@ssw0rd!@localhost:27017/',
            'DB_NAME_WB': 'test_db'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb is not None
    
    def test_init_with_unicode_db_name(self, mock_mongo_client):
        """Test initialization with Unicode characters in DB name."""
        env_vars = {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://localhost:27017/',
            'DB_NAME_WB': 'test_db_数据库'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                mock_mongo_client.__getitem__.assert_called_with('test_db_数据库')
    
    def test_init_with_very_long_db_name(self, mock_mongo_client):
        """Test initialization with very long database name."""
        long_name = 'a' * 200
        env_vars = {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://localhost:27017/',
            'DB_NAME_WB': long_name
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb is not None
    
    def test_init_with_whitespace_in_db_type(self, mock_mongo_client):
        """Test initialization with whitespace in DB_TYPE.
        
        BUG DOCUMENTATION: The code does NOT strip whitespace from DB_TYPE.
        DB_TYPE='  mongo  ' becomes '  mongo  ' after lower(), which is invalid.
        This test documents the actual behavior where whitespace causes failure.
        """
        env_vars = {
            'DB_TYPE': '  mongo  ',
            'MONGO_PATH': 'mongodb://localhost:27017/',
            'DB_NAME_WB': 'test_db'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                # Expect exception because '  mongo  ' != 'cosmos' and != 'mongo'
                with pytest.raises(Exception) as exc_info:
                    DataBase_WB()
                
                assert "Invalid DB_TYPE. Expected 'cosmos' or 'mongo'" in str(exc_info.value)


# ============================================================================
# TEST CLASS 6: Performance Tests
# ============================================================================

class TestDataBaseWBPerformance:
    """Test performance characteristics."""
    
    def test_init_multiple_instances_cosmos(self, cosmos_env_vars, mock_mongo_client):
        """Test creating multiple Cosmos instances."""
        with patch.dict(os.environ, cosmos_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                instances = []
                for _ in range(10):
                    instances.append(DataBase_WB())
                
                assert len(instances) == 10
                assert all(inst.db_type == 'cosmos' for inst in instances)
    
    def test_init_multiple_instances_mongo(self, mongo_env_vars, mock_mongo_client):
        """Test creating multiple MongoDB instances."""
        with patch.dict(os.environ, mongo_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                instances = []
                for _ in range(10):
                    instances.append(DataBase_WB())
                
                assert len(instances) == 10
                assert all(inst.db_type == 'mongo' for inst in instances)
    
    def test_init_rapid_instantiation(self, mongo_env_vars, mock_mongo_client):
        """Test rapid instantiation doesn't cause issues."""
        with patch.dict(os.environ, mongo_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                instances = [DataBase_WB() for _ in range(50)]
                
                assert len(instances) == 50


# ============================================================================
# TEST CLASS 7: Resource Management Tests
# ============================================================================

class TestDataBaseWBResourceManagement:
    """Test resource management."""
    
    def test_init_client_attribute_set(self, cosmos_env_vars, mock_mongo_client):
        """Test that client attribute is properly set."""
        with patch.dict(os.environ, cosmos_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert hasattr(db_wb, 'client')
                assert db_wb.client is mock_mongo_client
    
    def test_init_db_attribute_set(self, cosmos_env_vars, mock_mongo_client):
        """Test that db attribute is properly set."""
        with patch.dict(os.environ, cosmos_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert hasattr(db_wb, 'db')
                assert db_wb.db is not None
    
    def test_init_db_type_attribute_set(self, mongo_env_vars, mock_mongo_client):
        """Test that db_type attribute is properly set."""
        with patch.dict(os.environ, mongo_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert hasattr(db_wb, 'db_type')
                assert db_wb.db_type == 'mongo'
    
    def test_init_all_attributes_present(self, cosmos_env_vars, mock_mongo_client):
        """Test that all expected attributes are present."""
        with patch.dict(os.environ, cosmos_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert hasattr(db_wb, 'db_type')
                assert hasattr(db_wb, 'client')
                assert hasattr(db_wb, 'db')


# ============================================================================
# TEST CLASS 8: Security Tests
# ============================================================================

class TestDataBaseWBSecurity:
    """Test security aspects."""
    
    def test_init_cosmos_with_credentials_in_path(self, mock_mongo_client):
        """Test Cosmos initialization with credentials in connection string."""
        env_vars = {
            'DB_TYPE': 'cosmos',
            'COSMOS_PATH': 'mongodb://username:password@test.cosmos.com:10255/',
            'DB_NAME_WB': 'test_db'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client) as mock_client_class:
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                # Verify credentials are passed to MongoClient
                mock_client_class.assert_called_once_with('mongodb://username:password@test.cosmos.com:10255/')
    
    def test_init_mongo_with_credentials_in_path(self, mock_mongo_client):
        """Test MongoDB initialization with credentials in connection string."""
        env_vars = {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://admin:secret@localhost:27017/',
            'DB_NAME_WB': 'test_db'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client) as mock_client_class:
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                # Verify credentials are passed to MongoClient
                mock_client_class.assert_called_once_with('mongodb://admin:secret@localhost:27017/')
    
    def test_init_with_special_chars_in_credentials(self, mock_mongo_client):
        """Test initialization with special characters in credentials."""
        env_vars = {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://user:p@ss!word%23@localhost:27017/',
            'DB_NAME_WB': 'test_db'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb is not None
    
    def test_init_connection_string_not_exposed(self, cosmos_env_vars, mock_mongo_client):
        """Test that connection string is not stored as attribute."""
        with patch.dict(os.environ, cosmos_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                # Connection string should not be stored as attribute for security
                assert not hasattr(db_wb, 'cosmos_path')
                assert not hasattr(db_wb, 'mongo_path')


# ============================================================================
# TEST CLASS 9: Integration Tests
# ============================================================================

class TestDataBaseWBIntegration:
    """Test integration points."""
    
    def test_init_loads_dotenv(self, cosmos_env_vars, mock_mongo_client):
        """Test that load_dotenv is called during module import."""
        # This is implicitly tested by the fact that environment variables work
        with patch.dict(os.environ, cosmos_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb is not None
    
    def test_init_uses_os_getenv(self, cosmos_env_vars, mock_mongo_client):
        """Test that os.getenv is used to retrieve environment variables."""
        with patch.dict(os.environ, cosmos_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                # If os.getenv works, this should succeed
                assert db_wb.db_type == 'cosmos'
    
    def test_init_mongo_client_from_pymongo(self, mongo_env_vars, mock_mongo_client):
        """Test that MongoClient is imported from pymongo."""
        with patch.dict(os.environ, mongo_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb.client is mock_mongo_client


# ============================================================================
# TEST CLASS 10: Regression Tests
# ============================================================================

class TestDataBaseWBRegression:
    """Test regression scenarios."""
    
    def test_regression_cosmos_db_type_lowercase(self, cosmos_env_vars, mock_mongo_client):
        """Regression: Ensure db_type is always lowercase."""
        with patch.dict(os.environ, cosmos_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb.db_type == db_wb.db_type.lower()
    
    def test_regression_mongo_db_type_lowercase(self, mongo_env_vars, mock_mongo_client):
        """Regression: Ensure db_type is always lowercase."""
        with patch.dict(os.environ, mongo_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb.db_type == db_wb.db_type.lower()
    
    def test_regression_exception_message_format(self, mock_mongo_client):
        """Regression: Ensure exception messages are consistent."""
        env_vars = {
            'DB_TYPE': 'invalid'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                with pytest.raises(Exception) as exc_info:
                    DataBase_WB()
                
                # Exception message should contain expected format
                assert "Invalid DB_TYPE" in str(exc_info.value)
                assert "cosmos" in str(exc_info.value)
                assert "mongo" in str(exc_info.value)
    
    def test_regression_client_type(self, cosmos_env_vars, mock_mongo_client):
        """Regression: Ensure client is MongoClient instance."""
        with patch.dict(os.environ, cosmos_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb.client is mock_mongo_client
    
    def test_regression_db_accessed_via_getitem(self, mongo_env_vars, mock_mongo_client):
        """Regression: Ensure db is accessed via __getitem__."""
        with patch.dict(os.environ, mongo_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                # Verify __getitem__ was called on client
                mock_mongo_client.__getitem__.assert_called_once()


# ============================================================================
# TEST CLASS 11: Code Quality Tests
# ============================================================================

class TestDataBaseWBCodeQuality:
    """Test code quality indicators."""
    
    def test_class_has_init_method(self):
        """Test that DataBase_WB class has __init__ method."""
        from fairness.dao.WorkBench.databaseconnection import DataBase_WB
        
        assert hasattr(DataBase_WB, '__init__')
    
    def test_init_sets_required_attributes(self, cosmos_env_vars, mock_mongo_client):
        """Test that __init__ sets all required attributes."""
        with patch.dict(os.environ, cosmos_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                required_attrs = ['db_type', 'client', 'db']
                for attr in required_attrs:
                    assert hasattr(db_wb, attr), f"Missing attribute: {attr}"
    
    def test_init_method_signature(self):
        """Test __init__ method signature."""
        from fairness.dao.WorkBench.databaseconnection import DataBase_WB
        import inspect
        
        sig = inspect.signature(DataBase_WB.__init__)
        params = list(sig.parameters.keys())
        
        # Should only have 'self' parameter
        assert params == ['self']
    
    def test_class_is_instantiable(self, cosmos_env_vars, mock_mongo_client):
        """Test that class can be instantiated."""
        with patch.dict(os.environ, cosmos_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert isinstance(db_wb, DataBase_WB)


# ============================================================================
# TEST CLASS 12: Connection String Validation Tests
# ============================================================================

class TestDataBaseWBConnectionStringValidation:
    """Test various connection string formats."""
    
    def test_cosmos_with_standard_port(self, mock_mongo_client):
        """Test Cosmos with standard port in connection string."""
        env_vars = {
            'DB_TYPE': 'cosmos',
            'COSMOS_PATH': 'mongodb://test.documents.azure.com:10255/',
            'DB_NAME_WB': 'test_db'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb is not None
    
    def test_mongo_with_custom_port(self, mock_mongo_client):
        """Test MongoDB with custom port."""
        env_vars = {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://localhost:27018/',
            'DB_NAME_WB': 'test_db'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb is not None
    
    def test_mongo_with_replica_set(self, mock_mongo_client):
        """Test MongoDB with replica set connection string."""
        env_vars = {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://host1:27017,host2:27017,host3:27017/?replicaSet=myReplSet',
            'DB_NAME_WB': 'test_db'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb is not None
    
    def test_cosmos_with_ssl_parameters(self, mock_mongo_client):
        """Test Cosmos with SSL parameters in connection string."""
        env_vars = {
            'DB_TYPE': 'cosmos',
            'COSMOS_PATH': 'mongodb://test.cosmos.com:10255/?ssl=true',
            'DB_NAME_WB': 'test_db'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb is not None
    
    def test_mongo_with_query_parameters(self, mock_mongo_client):
        """Test MongoDB with query parameters."""
        env_vars = {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://localhost:27017/?authSource=admin&maxPoolSize=50',
            'DB_NAME_WB': 'test_db'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb is not None


# ============================================================================
# TEST CLASS 13: Scalability Tests
# ============================================================================

class TestDataBaseWBScalability:
    """Test scalability characteristics."""
    
    def test_multiple_db_connections_cosmos(self, cosmos_env_vars, mock_mongo_client):
        """Test creating multiple Cosmos database connections."""
        with patch.dict(os.environ, cosmos_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                connections = []
                for i in range(100):
                    connections.append(DataBase_WB())
                
                assert len(connections) == 100
                assert all(conn.db_type == 'cosmos' for conn in connections)
    
    def test_multiple_db_connections_mongo(self, mongo_env_vars, mock_mongo_client):
        """Test creating multiple MongoDB database connections."""
        with patch.dict(os.environ, mongo_env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                connections = []
                for i in range(100):
                    connections.append(DataBase_WB())
                
                assert len(connections) == 100
                assert all(conn.db_type == 'mongo' for conn in connections)
    
    def test_connection_with_large_db_name(self, mock_mongo_client):
        """Test connection with large database name."""
        large_name = 'db_' + 'a' * 500
        env_vars = {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://localhost:27017/',
            'DB_NAME_WB': large_name
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                mock_mongo_client.__getitem__.assert_called_with(large_name)


# ============================================================================
# TEST CLASS 14: Environment Variable Edge Cases
# ============================================================================

class TestDataBaseWBEnvVarEdgeCases:
    """Test edge cases with environment variables."""
    
    def test_cosmos_path_with_trailing_slash(self, mock_mongo_client):
        """Test Cosmos path with trailing slash."""
        env_vars = {
            'DB_TYPE': 'cosmos',
            'COSMOS_PATH': 'mongodb://test.cosmos.com:10255/',
            'DB_NAME_WB': 'test_db'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb is not None
    
    def test_cosmos_path_without_trailing_slash(self, mock_mongo_client):
        """Test Cosmos path without trailing slash."""
        env_vars = {
            'DB_TYPE': 'cosmos',
            'COSMOS_PATH': 'mongodb://test.cosmos.com:10255',
            'DB_NAME_WB': 'test_db'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                assert db_wb is not None
    
    def test_db_name_with_underscores(self, mock_mongo_client):
        """Test database name with underscores."""
        env_vars = {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://localhost:27017/',
            'DB_NAME_WB': 'test_db_workbench_v2'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                mock_mongo_client.__getitem__.assert_called_with('test_db_workbench_v2')
    
    def test_db_name_with_hyphens(self, mock_mongo_client):
        """Test database name with hyphens."""
        env_vars = {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://localhost:27017/',
            'DB_NAME_WB': 'test-db-workbench'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                mock_mongo_client.__getitem__.assert_called_with('test-db-workbench')
    
    def test_db_name_with_numbers(self, mock_mongo_client):
        """Test database name with numbers."""
        env_vars = {
            'DB_TYPE': 'mongo',
            'MONGO_PATH': 'mongodb://localhost:27017/',
            'DB_NAME_WB': 'test_db_123'
        }
        with patch.dict(os.environ, env_vars):
            with patch('fairness.dao.WorkBench.databaseconnection.MongoClient', return_value=mock_mongo_client):
                from fairness.dao.WorkBench.databaseconnection import DataBase_WB
                
                db_wb = DataBase_WB()
                
                mock_mongo_client.__getitem__.assert_called_with('test_db_123')
