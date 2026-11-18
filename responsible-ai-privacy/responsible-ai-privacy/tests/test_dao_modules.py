"""
Tests for DAO (Data Access Object) modules.

This module tests all database operations for MongoDB collections including
AccMasterDb, AccDataGrpDb, AccPtrnDb, RecogDb, EntityDb, TelemetryFlag, and DatabaseConnection.
"""

import pytest
import sys
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime


class TestDatabaseConnection:
    """Test suite for DatabaseConnection module."""
    
    def test_connect_success(self):
        """Test successful database connection."""
        with patch('privacy.dao.DatabaseConnection.pymongo.MongoClient') as mock_client, \
             patch('privacy.dao.DatabaseConnection.os.getenv') as mock_getenv:
            
            mock_getenv.side_effect = lambda x: "mongodb://localhost" if x == "MONGO_PATH" else "testdb"
            mock_db = MagicMock()
            mock_client.return_value.__getitem__.return_value = mock_db
            
            from privacy.dao.DatabaseConnection import DB
            result = DB.connect()
            
            assert result == mock_db
            mock_client.assert_called_once_with("mongodb://localhost")
    
    def test_connect_exception_exits(self):
        """Test connection exception causes system exit."""
        with patch('privacy.dao.DatabaseConnection.pymongo.MongoClient', side_effect=Exception("Connection failed")), \
             patch('privacy.dao.DatabaseConnection.os.getenv', return_value="mongodb://localhost"), \
             patch('privacy.dao.DatabaseConnection.sys.exit') as mock_exit:
            
            from privacy.dao.DatabaseConnection import DB
            DB.connect()
            
            mock_exit.assert_called_once()


class TestAccMasterDb:
    """Test suite for AccMasterDb CRUD operations."""
    
    def test_findOne_returns_attribute_dict(self):
        """Test findOne returns data as AttributeDict."""
        with patch('privacy.dao.AccMasterDb.AccMasterDb.mycol') as mock_col:
            mock_data = {"_id": 123, "portfolio": "test_portfolio", "account": "test_account"}
            mock_col.find.return_value = [mock_data]
            
            from privacy.dao.AccMasterDb import AccMasterDb
            result = AccMasterDb.findOne(123)
            
            assert result._id == 123
            assert result.portfolio == "test_portfolio"
            mock_col.find.assert_called_once_with({"_id": 123}, {})
    
    def test_findall_returns_list_of_attribute_dicts(self):
        """Test findall returns list of AttributeDict objects."""
        with patch('privacy.dao.AccMasterDb.AccMasterDb.mycol') as mock_col:
            mock_data = [
                {"_id": 1, "portfolio": "portfolio1"},
                {"_id": 2, "portfolio": "portfolio2"}
            ]
            mock_col.find.return_value = mock_data
            
            from privacy.dao.AccMasterDb import AccMasterDb
            result = AccMasterDb.findall({"isActive": "Y"})
            
            assert len(result) == 2
            assert result[0]._id == 1
            assert result[1].portfolio == "portfolio2"
    
    def test_create_inserts_document(self):
        """Test create inserts new document and returns inserted_id."""
        with patch('privacy.dao.AccMasterDb.AccMasterDb.mycol') as mock_col, \
             patch('privacy.dao.AccMasterDb.time.time', return_value=1234567890.0):
            
            mock_result = MagicMock()
            mock_result.inserted_id = 1234567890.0
            mock_col.insert_one.return_value = mock_result
            
            from privacy.dao.AccMasterDb import AccMasterDb
            test_value = {"AName": "TestPortfolio", "SName": "TestAccount"}
            result = AccMasterDb.create(test_value)
            
            assert result == 1234567890.0
            assert mock_col.insert_one.called
            inserted_doc = mock_col.insert_one.call_args[0][0]
            assert inserted_doc["portfolio"] == "TestPortfolio"
            assert inserted_doc["account"] == "TestAccount"
            assert inserted_doc["isActive"] == "Y"
    
    def test_update_modifies_document(self):
        """Test update modifies existing document."""
        with patch('privacy.dao.AccMasterDb.AccMasterDb.mycol') as mock_col:
            mock_result = MagicMock()
            mock_result.acknowledged = True
            mock_col.update_one.return_value = mock_result
            
            from privacy.dao.AccMasterDb import AccMasterDb
            result = AccMasterDb.update(123, {"portfolio": "UpdatedPortfolio"})
            
            assert result is True
            mock_col.update_one.assert_called_once()
            call_args = mock_col.update_one.call_args[0]
            assert call_args[0] == {"_id": 123}
            assert call_args[1] == {"$set": {"portfolio": "UpdatedPortfolio"}}
    
    def test_delete_removes_document(self):
        """Test delete removes document."""
        with patch('privacy.dao.AccMasterDb.AccMasterDb.mycol') as mock_col:
            mock_result = MagicMock()
            mock_result.acknowledged = True
            mock_col.delete_many.return_value = mock_result
            
            from privacy.dao.AccMasterDb import AccMasterDb
            result = AccMasterDb.delete(123)
            
            assert result is True
            mock_col.delete_many.assert_called_once_with({"_id": 123})


class TestAccDataGrpDb:
    """Test suite for AccDataGrpDb CRUD operations."""
    
    def test_findOne_returns_data(self):
        """Test findOne retrieves single record."""
        with patch('privacy.dao.AccDataGrpMappingDb.AccDataGrpDb.mycol') as mock_col:
            mock_data = {"_id": 456, "accMasterId": 123, "dataRecogGrpId": 789}
            mock_col.find.return_value = [mock_data]
            
            from privacy.dao.AccDataGrpMappingDb import AccDataGrpDb
            result = AccDataGrpDb.findOne(456)
            
            assert result._id == 456
            assert result.accMasterId == 123
    
    def test_findall_returns_multiple_records(self):
        """Test findall retrieves multiple records."""
        with patch('privacy.dao.AccDataGrpMappingDb.AccDataGrpDb.mycol') as mock_col:
            mock_data = [
                {"_id": 1, "accMasterId": 100},
                {"_id": 2, "accMasterId": 100}
            ]
            mock_col.find.return_value = mock_data
            
            from privacy.dao.AccDataGrpMappingDb import AccDataGrpDb
            result = AccDataGrpDb.findall({"accMasterId": 100})
            
            assert len(result) == 2
    
    def test_create_inserts_with_correct_fields(self):
        """Test create inserts document with proper structure."""
        with patch('privacy.dao.AccDataGrpMappingDb.AccDataGrpDb.mycol') as mock_col, \
             patch('privacy.dao.AccDataGrpMappingDb.time.time', return_value=9999.0):
            
            mock_result = MagicMock()
            mock_result.acknowledged = True
            mock_col.insert_one.return_value = mock_result
            
            from privacy.dao.AccDataGrpMappingDb import AccDataGrpDb
            test_value = {"Aid": 123, "Did": 456}
            result = AccDataGrpDb.create(test_value)
            
            assert result is True
            inserted_doc = mock_col.insert_one.call_args[0][0]
            assert inserted_doc["accMasterId"] == 123
            assert inserted_doc["dataRecogGrpId"] == 456
            assert inserted_doc["isActive"] == "Y"
            assert inserted_doc["isHashify"] is False
    
    def test_update_with_query(self):
        """Test update using query parameter."""
        with patch('privacy.dao.AccDataGrpMappingDb.AccDataGrpDb.mycol') as mock_col:
            mock_result = MagicMock()
            mock_result.acknowledged = True
            mock_col.update_one.return_value = mock_result
            
            from privacy.dao.AccDataGrpMappingDb import AccDataGrpDb
            query = {"_id": 123}
            update_values = {"isActive": "N"}
            result = AccDataGrpDb.update(query, update_values)
            
            assert result is True
            mock_col.update_one.assert_called_once_with(query, {"$set": update_values})
    
    def test_delete_by_dataRecogGrpId(self):
        """Test delete removes records by dataRecogGrpId."""
        with patch('privacy.dao.AccDataGrpMappingDb.AccDataGrpDb.mycol') as mock_col:
            mock_result = MagicMock()
            mock_result.acknowledged = True
            mock_col.delete_many.return_value = mock_result
            
            from privacy.dao.AccDataGrpMappingDb import AccDataGrpDb
            result = AccDataGrpDb.delete(789)
            
            assert result is True
            mock_col.delete_many.assert_called_once_with({"dataRecogGrpId": 789})
    
    def test_deleteMany_with_custom_query(self):
        """Test deleteMany removes records matching query."""
        with patch('privacy.dao.AccDataGrpMappingDb.AccDataGrpDb.mycol') as mock_col:
            mock_result = MagicMock()
            mock_result.acknowledged = True
            mock_col.delete_many.return_value = mock_result
            
            from privacy.dao.AccDataGrpMappingDb import AccDataGrpDb
            query = {"accMasterId": 123, "isActive": "N"}
            result = AccDataGrpDb.deleteMany(query)
            
            assert result is True
            mock_col.delete_many.assert_called_once_with(query)


class TestAccPtrnDb:
    """Test suite for AccPtrnDb CRUD operations."""
    
    def test_findOne_retrieves_record(self):
        """Test findOne retrieves pattern record."""
        with patch('privacy.dao.AccPtrnMappingDb.AccPtrnDb.mycol') as mock_col:
            mock_data = {"_id": 111, "accMasterId": 222, "ptrnRecId": 333}
            mock_col.find.return_value = [mock_data]
            
            from privacy.dao.AccPtrnMappingDb import AccPtrnDb
            result = AccPtrnDb.findOne(111)
            
            assert result._id == 111
            assert result.ptrnRecId == 333
    
    def test_findall_retrieves_patterns(self):
        """Test findall retrieves pattern records."""
        with patch('privacy.dao.AccPtrnMappingDb.AccPtrnDb.mycol') as mock_col:
            mock_data = [{"_id": 1, "accMasterId": 100}]
            mock_col.find.return_value = mock_data
            
            from privacy.dao.AccPtrnMappingDb import AccPtrnDb
            result = AccPtrnDb.findall({"isActive": "Y"})
            
            assert len(result) == 1
    
    def test_create_pattern_mapping(self):
        """Test create inserts pattern mapping."""
        with patch('privacy.dao.AccPtrnMappingDb.AccPtrnDb.mycol') as mock_col, \
             patch('privacy.dao.AccPtrnMappingDb.time.time', return_value=5555.0):
            
            mock_result = MagicMock()
            mock_result.inserted_id = 5555.0
            mock_col.insert_one.return_value = mock_result
            
            from privacy.dao.AccPtrnMappingDb import AccPtrnDb
            test_value = {"Aid": 100, "Pid": 200}
            result = AccPtrnDb.create(test_value)
            
            assert result == 5555.0
            inserted_doc = mock_col.insert_one.call_args[0][0]
            assert inserted_doc["accMasterId"] == 100
            assert inserted_doc["ptrnRecId"] == 200
    
    def test_update_pattern_record(self):
        """Test update modifies pattern record."""
        with patch('privacy.dao.AccPtrnMappingDb.AccPtrnDb.mycol') as mock_col:
            mock_result = MagicMock()
            mock_result.acknowledged = True
            mock_col.update_one.return_value = mock_result
            
            from privacy.dao.AccPtrnMappingDb import AccPtrnDb
            result = AccPtrnDb.update(111, {"isActive": "N"})
            
            assert result is True
    
    def test_delete_pattern_record(self):
        """Test delete removes pattern record."""
        with patch('privacy.dao.AccPtrnMappingDb.AccPtrnDb.mycol') as mock_col:
            from privacy.dao.AccPtrnMappingDb import AccPtrnDb
            AccPtrnDb.delete(111)
            
            mock_col.delete_many.assert_called_once_with({"_id": 111})


class TestRecogDb:
    """Test suite for RecogDb (Data Recognition) CRUD operations."""
    
    def test_findOne_retrieves_recognizer(self):
        """Test findOne retrieves recognizer record."""
        with patch('privacy.dao.DataRecogdb.RecogDb.mycol') as mock_col:
            mock_data = {"_id": 777, "RecogName": "TestRecognizer", "RecogType": "Pattern"}
            mock_col.find.return_value = [mock_data]
            
            from privacy.dao.DataRecogdb import RecogDb
            result = RecogDb.findOne(777)
            
            assert result._id == 777
            assert result.RecogName == "TestRecognizer"
    
    def test_findall_retrieves_recognizers(self):
        """Test findall retrieves recognizer records."""
        with patch('privacy.dao.DataRecogdb.RecogDb.mycol') as mock_col:
            mock_data = [
                {"_id": 1, "RecogType": "Pattern"},
                {"_id": 2, "RecogType": "Regex"}
            ]
            mock_col.find.return_value = mock_data
            
            from privacy.dao.DataRecogdb import RecogDb
            result = RecogDb.findall({"isActive": "Y"})
            
            assert len(result) == 2
    
    def test_create_recognizer_with_all_fields(self):
        """Test create inserts recognizer with complete data."""
        with patch('privacy.dao.DataRecogdb.RecogDb.mycol') as mock_col, \
             patch('privacy.dao.DataRecogdb.time.time', return_value=8888.0):
            
            mock_result = MagicMock()
            mock_result.inserted_id = 8888.0
            mock_col.insert_one.return_value = mock_result
            
            from privacy.dao.DataRecogdb import RecogDb
            test_value = {
                "Name": "EmailRecognizer",
                "entity": ["EMAIL"],
                "type": "Pattern",
                "score": 0.9,
                "context": ["email", "mail"],
                "edit": True,
                "define": False
            }
            result = RecogDb.create(test_value)
            
            assert result == 8888.0
            inserted_doc = mock_col.insert_one.call_args[0][0]
            assert inserted_doc["RecogName"] == "EmailRecognizer"
            assert inserted_doc["supported_entity"] == ["EMAIL"]
            assert inserted_doc["Score"] == 0.9
            assert inserted_doc["isEditable"] is True
            assert inserted_doc["isPreDefined"] is False
    
    def test_update_recognizer(self):
        """Test update modifies recognizer record."""
        with patch('privacy.dao.DataRecogdb.RecogDb.mycol') as mock_col:
            mock_result = MagicMock()
            mock_result.acknowledged = True
            mock_col.update_one.return_value = mock_result
            
            from privacy.dao.DataRecogdb import RecogDb
            result = RecogDb.update(777, {"Score": 0.95})
            
            assert result is True
    
    def test_delete_recognizer(self):
        """Test delete removes recognizer."""
        with patch('privacy.dao.DataRecogdb.RecogDb.mycol') as mock_col:
            from privacy.dao.DataRecogdb import RecogDb
            RecogDb.delete(777)
            
            mock_col.delete_many.assert_called_once_with({"_id": 777})


class TestEntityDb:
    """Test suite for EntityDb CRUD operations."""
    
    def test_findOne_retrieves_entity(self):
        """Test findOne retrieves entity record."""
        with patch('privacy.dao.EntityDb.EntityDb.mycol') as mock_col:
            mock_data = {"_id": 555, "EntityName": "PERSON", "RecogId": 999}
            mock_col.find.return_value = [mock_data]
            
            from privacy.dao.EntityDb import EntityDb
            result = EntityDb.findOne(555)
            
            assert result._id == 555
            assert result.EntityName == "PERSON"
    
    def test_findall_retrieves_entities(self):
        """Test findall retrieves entity records."""
        with patch('privacy.dao.EntityDb.EntityDb.mycol') as mock_col:
            mock_data = [
                {"_id": 1, "EntityName": "PERSON"},
                {"_id": 2, "EntityName": "EMAIL"}
            ]
            mock_col.find.return_value = mock_data
            
            from privacy.dao.EntityDb import EntityDb
            result = EntityDb.findall({"RecogId": 999})
            
            assert len(result) == 2
    
    def test_create_entity(self):
        """Test create inserts entity record."""
        with patch('privacy.dao.EntityDb.EntityDb.mycol') as mock_col, \
             patch('privacy.dao.EntityDb.time.time', return_value=6666.0):
            
            mock_result = MagicMock()
            mock_result.acknowledged = True
            mock_col.insert_one.return_value = mock_result
            
            from privacy.dao.EntityDb import EntityDb
            test_value = {"Name": "PHONE_NUMBER", "dgid": 999}
            result = EntityDb.create(test_value)
            
            assert result is True
            inserted_doc = mock_col.insert_one.call_args[0][0]
            assert inserted_doc["EntityName"] == "PHONE_NUMBER"
            assert inserted_doc["RecogId"] == 999
    
    def test_update_entity(self):
        """Test update modifies entity record."""
        with patch('privacy.dao.EntityDb.EntityDb.mycol') as mock_col:
            mock_result = MagicMock()
            mock_result.acknowledged = True
            mock_col.update_one.return_value = mock_result
            
            from privacy.dao.EntityDb import EntityDb
            result = EntityDb.update(555, {"EntityName": "UPDATED_PERSON"})
            
            assert result is True
    
    def test_delete_entity(self):
        """Test delete removes entity."""
        with patch('privacy.dao.EntityDb.EntityDb.mycol') as mock_col:
            mock_result = MagicMock()
            mock_result.acknowledged = True
            mock_col.delete_many.return_value = mock_result
            
            from privacy.dao.EntityDb import EntityDb
            result = EntityDb.delete(555)
            
            assert result is True
            mock_col.delete_many.assert_called_once_with({"_id": 555})
    
    def test_deleteMany_entities(self):
        """Test deleteMany removes entities matching query."""
        with patch('privacy.dao.EntityDb.EntityDb.mycol') as mock_col:
            mock_result = MagicMock()
            mock_result.acknowledged = True
            mock_col.delete_many.return_value = mock_result
            
            from privacy.dao.EntityDb import EntityDb
            query = {"RecogId": 999}
            result = EntityDb.deleteMany(query)
            
            assert result is True
            mock_col.delete_many.assert_called_once_with(query)


class TestTelemetryFlag:
    """Test suite for TelemetryFlag CRUD operations."""
    
    def test_findOne_retrieves_flag(self):
        """Test findOne retrieves telemetry flag."""
        with patch('privacy.dao.TelemetryFlagDb.TelemetryFlag.mycol') as mock_col:
            mock_data = {"_id": 333, "Module": "TextPrivacy", "TelemetryFlag": False}
            mock_col.find.return_value = [mock_data]
            
            from privacy.dao.TelemetryFlagDb import TelemetryFlag
            result = TelemetryFlag.findOne(333)
            
            assert result._id == 333
            assert result.Module == "TextPrivacy"
    
    def test_findall_retrieves_flags(self):
        """Test findall retrieves telemetry flags."""
        with patch('privacy.dao.TelemetryFlagDb.TelemetryFlag.mycol') as mock_col:
            mock_data = [
                {"_id": 1, "Module": "TextPrivacy"},
                {"_id": 2, "Module": "ImagePrivacy"}
            ]
            mock_col.find.return_value = mock_data
            
            from privacy.dao.TelemetryFlagDb import TelemetryFlag
            result = TelemetryFlag.findall({"TelemetryFlag": False})
            
            assert len(result) == 2
    
    def test_create_telemetry_flag(self):
        """Test create inserts telemetry flag."""
        with patch('privacy.dao.TelemetryFlagDb.TelemetryFlag.mycol') as mock_col, \
             patch('privacy.dao.TelemetryFlagDb.time.time', return_value=4444.0):
            
            mock_result = MagicMock()
            mock_result.inserted_id = 4444.0
            mock_col.insert_one.return_value = mock_result
            
            from privacy.dao.TelemetryFlagDb import TelemetryFlag
            test_value = {"module": "VideoService"}
            result = TelemetryFlag.create(test_value)
            
            assert result == 4444.0
            inserted_doc = mock_col.insert_one.call_args[0][0]
            assert inserted_doc["Module"] == "VideoService"
            assert inserted_doc["TelemetryFlag"] is False
    
    def test_update_telemetry_flag(self):
        """Test update modifies telemetry flag."""
        with patch('privacy.dao.TelemetryFlagDb.TelemetryFlag.mycol') as mock_col:
            mock_result = MagicMock()
            mock_result.acknowledged = True
            mock_col.update_one.return_value = mock_result
            
            from privacy.dao.TelemetryFlagDb import TelemetryFlag
            result = TelemetryFlag.update(333, {"TelemetryFlag": True})
            
            assert result is True
    
    def test_delete_telemetry_flag(self):
        """Test delete removes telemetry flag."""
        with patch('privacy.dao.TelemetryFlagDb.TelemetryFlag.mycol') as mock_col:
            from privacy.dao.TelemetryFlagDb import TelemetryFlag
            TelemetryFlag.delete(333)
            
            mock_col.delete_many.assert_called_once_with({"_id": 333})


class TestAttributeDict:
    """Test suite for AttributeDict helper class."""
    
    def test_attribute_dict_getattr(self):
        """Test AttributeDict allows attribute access."""
        from privacy.dao.AccMasterDb import AttributeDict
        
        data = AttributeDict({"name": "test", "value": 123})
        assert data.name == "test"
        assert data.value == 123
    
    def test_attribute_dict_setattr(self):
        """Test AttributeDict allows attribute assignment."""
        from privacy.dao.AccMasterDb import AttributeDict
        
        data = AttributeDict()
        data.name = "test"
        data.value = 456
        
        assert data["name"] == "test"
        assert data["value"] == 456
    
    def test_attribute_dict_delattr(self):
        """Test AttributeDict allows attribute deletion."""
        from privacy.dao.AccMasterDb import AttributeDict
        
        data = AttributeDict({"name": "test", "value": 123})
        del data.name
        
        assert "name" not in data
        assert data.value == 123
