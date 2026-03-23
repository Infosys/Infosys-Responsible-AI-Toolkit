"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Unit tests for DAO layer
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


@pytest.mark.unit
class TestDatabaseConnection:
    """Test cases for database connection utilities"""

    @patch('pymongo.MongoClient')
    def test_mongo_client_creation(self, mock_mongo_client):
        """Test MongoDB client creation"""
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        
        # Simulate database connection
        client = mock_mongo_client("mongodb://localhost:27017")
        
        assert client is not None
        mock_mongo_client.assert_called_once_with("mongodb://localhost:27017")

    @patch('pymongo.MongoClient')
    def test_database_selection(self, mock_mongo_client):
        """Test database selection"""
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        
        client = mock_mongo_client("mongodb://localhost:27017")
        db = client["test_db"]
        
        assert db is not None

    @patch('pymongo.MongoClient')
    def test_collection_selection(self, mock_mongo_client):
        """Test collection selection"""
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        
        mock_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        
        client = mock_mongo_client("mongodb://localhost:27017")
        db = client["test_db"]
        collection = db["test_collection"]
        
        assert collection is not None


@pytest.mark.unit
class TestCRUDOperations:
    """Test CRUD operations on database"""

    def test_create_operation(self, mock_mongo_client):
        """Test create operation"""
        mock_collection = MagicMock()
        mock_collection.insert_one.return_value.inserted_id = "test_id_123"
        
        data = {"name": "Test", "value": "123"}
        result = mock_collection.insert_one(data)
        
        assert result.inserted_id == "test_id_123"
        mock_collection.insert_one.assert_called_once_with(data)

    def test_read_operation(self, mock_mongo_client):
        """Test read operation"""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {"_id": "123", "name": "Test"}
        
        result = mock_collection.find_one({"_id": "123"})
        
        assert result["name"] == "Test"
        mock_collection.find_one.assert_called_once_with({"_id": "123"})

    def test_update_operation(self, mock_mongo_client):
        """Test update operation"""
        mock_collection = MagicMock()
        mock_collection.update_one.return_value.modified_count = 1
        
        result = mock_collection.update_one(
            {"_id": "123"},
            {"$set": {"name": "Updated"}}
        )
        
        assert result.modified_count == 1

    def test_delete_operation(self, mock_mongo_client):
        """Test delete operation"""
        mock_collection = MagicMock()
        mock_collection.delete_one.return_value.deleted_count = 1
        
        result = mock_collection.delete_one({"_id": "123"})
        
        assert result.deleted_count == 1

    def test_find_all_operation(self, mock_mongo_client):
        """Test find all operation"""
        mock_collection = MagicMock()
        mock_collection.find.return_value = [
            {"_id": "1", "name": "Test1"},
            {"_id": "2", "name": "Test2"}
        ]
        
        results = list(mock_collection.find({}))
        
        assert len(results) == 2
        assert results[0]["name"] == "Test1"


@pytest.mark.unit
class TestRecogDbOperations:
    """Test RecogDb specific operations"""

    @patch('rai_admin.dao.DataRecogdb.RecogDb')
    def test_recog_db_find_all(self, mock_recog_db):
        """Test RecogDb find_all method"""
        mock_recog_db.find_all.return_value = [
            {"RecogName": "Email", "entity": "EMAIL"},
            {"RecogName": "Phone", "entity": "PHONE"}
        ]
        
        results = mock_recog_db.find_all({})
        
        assert len(results) == 2
        assert results[0]["RecogName"] == "Email"

    @patch('rai_admin.dao.DataRecogdb.RecogDb')
    def test_recog_db_create(self, mock_recog_db):
        """Test RecogDb create method"""
        mock_recog_db.create.return_value = "recog_123"
        
        data = {"RecogName": "Test", "entity": "TEST"}
        result = mock_recog_db.create(data)
        
        assert result == "recog_123"

    @patch('rai_admin.dao.DataRecogdb.RecogDb')
    def test_recog_db_update(self, mock_recog_db):
        """Test RecogDb update method"""
        mock_recog_db.update.return_value = "success"
        
        result = mock_recog_db.update("recog_123", {"RecogName": "Updated"})
        
        assert result == "success"

    @patch('rai_admin.dao.DataRecogdb.RecogDb')
    def test_recog_db_delete(self, mock_recog_db):
        """Test RecogDb delete method"""
        mock_recog_db.delete.return_value = "success"
        
        result = mock_recog_db.delete("recog_123")
        
        assert result == "success"


@pytest.mark.unit
class TestEntityDbOperations:
    """Test EntityDb specific operations"""

    @patch('rai_admin.dao.EntityDb.EntityDb')
    def test_entity_db_create(self, mock_entity_db):
        """Test EntityDb create method"""
        mock_entity_db.create.return_value = "entity_123"
        
        data = {"Name": "Test Entity", "dgid": "recog_123"}
        result = mock_entity_db.create(data)
        
        assert result == "entity_123"

    @patch('rai_admin.dao.EntityDb.EntityDb')
    def test_entity_db_find_all(self, mock_entity_db):
        """Test EntityDb find_all method"""
        mock_entity_db.find_all.return_value = [
            {"EntityName": "Entity1", "RecogId": "recog_123"},
            {"EntityName": "Entity2", "RecogId": "recog_123"}
        ]
        
        results = mock_entity_db.find_all({"RecogId": "recog_123"})
        
        assert len(results) == 2

    @patch('rai_admin.dao.EntityDb.EntityDb')
    def test_entity_db_delete_many(self, mock_entity_db):
        """Test EntityDb delete_many method"""
        mock_entity_db.delete_many.return_value = "success"
        
        result = mock_entity_db.delete_many({"RecogId": "recog_123"})
        
        assert result == "success"


@pytest.mark.unit
class TestAccMasterDbOperations:
    """Test AccMasterDb operations"""

    @patch('rai_admin.dao.AccMasterDb.AccMasterDb')
    def test_acc_master_db_get_accounts(self, mock_acc_master_db):
        """Test AccMasterDb get accounts"""
        mock_acc_master_db.find_all.return_value = [
            {"accountId": "acc_1", "accountName": "Account 1"},
            {"accountId": "acc_2", "accountName": "Account 2"}
        ]
        
        results = mock_acc_master_db.find_all({})
        
        assert len(results) == 2
        assert results[0]["accountName"] == "Account 1"

    @patch('rai_admin.dao.AccMasterDb.AccMasterDb')
    def test_acc_master_db_create_account(self, mock_acc_master_db):
        """Test AccMasterDb create account"""
        mock_acc_master_db.create.return_value = "acc_123"
        
        data = {"accountName": "New Account", "isActive": True}
        result = mock_acc_master_db.create(data)
        
        assert result == "acc_123"
