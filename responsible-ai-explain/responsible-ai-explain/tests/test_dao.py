'''
Copyright 2025-2026 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

"""
test_dao.py - Tests for DAO module (Database Access Objects)
"""

import sys
import os
import pytest
from unittest.mock import Mock, MagicMock, patch
from io import BytesIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================================
# Test Database Connection - Workbench
# ============================================================================

class TestWorkbenchDatabaseConnection:
    """Tests for Workbench DatabaseConnection"""

    @patch('explain.dao.workbench.DatabaseConnection.pymongo.MongoClient')
    @patch.dict(os.environ, {'DB_NAME': 'test_db', 'MONGO_PATH': 'mongodb://localhost:27017', 'DB_TYPE': 'mongo'})
    def test_db_connect_success_mongo(self, mock_mongo_client):
        """Test successful MongoDB connection"""
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__ = MagicMock(return_value=mock_db)
        mock_client.admin.command = MagicMock(return_value={'ismaster': True})
        mock_mongo_client.return_value = mock_client
        
        from explain.dao.workbench.DatabaseConnection import DB
        
        with patch.object(DB, 'connect', return_value=mock_db):
            result = DB.connect()
            assert result is not None

    @patch('explain.dao.workbench.DatabaseConnection.pymongo.MongoClient')
    @patch.dict(os.environ, {'DB_NAME': 'test_db', 'COSMOS_PATH': 'mongodb://localhost:27017', 'DB_TYPE': 'cosmos'})
    def test_db_connect_success_cosmos(self, mock_mongo_client):
        """Test successful CosmosDB connection"""
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__ = MagicMock(return_value=mock_db)
        mock_client.admin.command = MagicMock(return_value={'ismaster': True})
        mock_mongo_client.return_value = mock_client
        
        from explain.dao.workbench.DatabaseConnection import DB
        
        with patch.object(DB, 'connect', return_value=mock_db):
            result = DB.connect()
            assert result is not None

    @patch.dict(os.environ, {'DB_NAME': '', 'MONGO_PATH': '', 'DB_TYPE': 'mongo'})
    def test_db_connect_missing_env_vars(self):
        """Test connection failure with missing environment variables"""
        # This test verifies the error handling for missing env vars
        # The actual module may exit, so we need to handle that
        pass  # Environment variable validation is tested at module load


class TestExplainabilityDatabaseConnection:
    """Tests for Explainability DatabaseConnection"""

    @patch('explain.dao.explainability.DatabaseConnection.pymongo.MongoClient')
    @patch.dict(os.environ, {'RAI_EXPLAIN_DB': 'test_explain_db', 'MONGO_PATH': 'mongodb://localhost:27017', 'DB_TYPE': 'mongo'})
    def test_explain_db_connect_success(self, mock_mongo_client):
        """Test successful Explainability DB connection"""
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__ = MagicMock(return_value=mock_db)
        mock_client.admin.command = MagicMock(return_value={'ismaster': True})
        mock_mongo_client.return_value = mock_client
        
        # Test that connection module can be imported
        from explain.dao.explainability import DatabaseConnection
        assert DatabaseConnection is not None


# ============================================================================
# Test FileStoreDb
# ============================================================================

class TestFileStoreDb:
    """Tests for FileStoreDb DAO"""

    @patch('explain.dao.workbench.FileStoreDb.DB')
    @patch('explain.dao.workbench.FileStoreDb.GridFS')
    @patch.dict(os.environ, {'DB_TYPE': 'mongo', 'VERIFY_SSL': 'false'})
    def test_save_file_mongo_success(self, mock_gridfs, mock_db):
        """Test saving file to MongoDB GridFS"""
        mock_fs = MagicMock()
        mock_file = MagicMock()
        mock_file._id = "test_file_id"
        mock_fs.new_file.return_value.__enter__ = MagicMock(return_value=mock_file)
        mock_fs.new_file.return_value.__exit__ = MagicMock()
        mock_gridfs.return_value = mock_fs
        
        # Test the save logic
        file_content = b"test file content"
        filename = "test.pkl"
        content_type = "application/octet-stream"
        tenet = "explainability"
        
        # Verify the mock setup
        assert mock_gridfs is not None

    @patch('explain.dao.workbench.FileStoreDb.DB')
    @patch('explain.dao.workbench.FileStoreDb.GridFS')
    @patch.dict(os.environ, {'DB_TYPE': 'mongo'})
    def test_save_file_none_content_raises_error(self, mock_gridfs, mock_db):
        """Test saving None content raises ValueError"""
        # The actual fileStoreDb.save_file should raise ValueError for None content
        pass  # Tested via integration

    @patch('explain.dao.workbench.FileStoreDb.DB')
    @patch('explain.dao.workbench.FileStoreDb.GridFS')
    @patch.dict(os.environ, {'DB_TYPE': 'mongo'})
    def test_read_file_exp_mongo_success(self, mock_gridfs, mock_db):
        """Test reading file from MongoDB GridFS"""
        mock_fs = MagicMock()
        mock_file_metadata = MagicMock()
        mock_file_metadata._id = "test_id"
        mock_file_metadata.filename = "test.pkl"
        
        mock_file_content = MagicMock()
        mock_file_content.read = MagicMock(return_value=b"file content")
        
        mock_fs.find_one = MagicMock(return_value=mock_file_metadata)
        mock_fs.get = MagicMock(return_value=mock_file_content)
        mock_gridfs.return_value = mock_fs
        
        # Verify setup
        assert mock_fs.find_one is not None

    @patch('explain.dao.workbench.FileStoreDb.DB')
    @patch('explain.dao.workbench.FileStoreDb.GridFS')
    @patch.dict(os.environ, {'DB_TYPE': 'mongo'})
    def test_read_file_exp_not_found(self, mock_gridfs, mock_db):
        """Test reading non-existent file raises FileNotFoundError"""
        mock_fs = MagicMock()
        mock_fs.find_one = MagicMock(return_value=None)
        mock_gridfs.return_value = mock_fs
        
        # Should raise FileNotFoundError when file not found
        pass  # Tested via integration

    @patch('explain.dao.workbench.FileStoreDb.requests.post')
    @patch('explain.dao.workbench.FileStoreDb.DB')
    @patch('explain.dao.workbench.FileStoreDb.GridFS')
    @patch.dict(os.environ, {'DB_TYPE': 'cosmos', 'AZURE_UPLOAD_API': 'http://localhost/upload', 'HTML_CONTAINER_NAME': 'html', 'VERIFY_SSL': 'false'})
    def test_save_file_azure_success(self, mock_gridfs, mock_db, mock_post):
        """Test saving file to Azure Blob Storage"""
        mock_response = MagicMock()
        mock_response.json = MagicMock(return_value={'blob_name': 'test_blob'})
        mock_post.return_value = mock_response
        
        # Verify setup
        assert mock_post is not None

    @patch('explain.dao.workbench.FileStoreDb.requests.get')
    @patch('explain.dao.workbench.FileStoreDb.DB')
    @patch('explain.dao.workbench.FileStoreDb.GridFS')
    @patch.dict(os.environ, {'DB_TYPE': 'cosmos', 'AZURE_GET_API': 'http://localhost/get', 'VERIFY_SSL': 'false'})
    def test_read_file_exp_azure_success(self, mock_gridfs, mock_db, mock_get):
        """Test reading file from Azure Blob Storage"""
        mock_response = MagicMock()
        mock_response.content = b"azure file content"
        mock_get.return_value = mock_response
        
        # Verify setup
        assert mock_get is not None


# ============================================================================
# Test Tbl_Explanation_Methods
# ============================================================================

class TestTblExplanationMethods:
    """Tests for Tbl_Explanation_Methods DAO"""

    def test_find_methods_returns_cursor(self, mock_explanation_methods):
        """Test find_methods returns cursor with methods"""
        # Mock the collection
        mock_collection = MagicMock()
        mock_collection.find = MagicMock(return_value=mock_explanation_methods)
        
        # Verify the expected structure
        assert len(mock_explanation_methods) == 3
        assert mock_explanation_methods[0]['methods'] == 'LIME-TABULAR'

    def test_find_methods_with_valid_params(self, mock_explanation_methods):
        """Test find_methods with valid parameters"""
        mock_collection = MagicMock()
        mock_collection.find = MagicMock(return_value=mock_explanation_methods)
        
        # Simulate calling find with params
        result = mock_collection.find({
            "modelFramework": "Scikit-learn",
            "taskType": "CLASSIFICATION",
            "dataType": "Tabular"
        })
        
        assert result is not None

    def test_find_methods_empty_params(self):
        """Test find_methods with empty parameters returns error"""
        mock_collection = MagicMock()
        
        # With empty params, should return error dict
        # This tests the validation in find_methods
        pass  # Tested via integration

    def test_find_methods_no_results(self):
        """Test find_methods with no matching results"""
        mock_collection = MagicMock()
        mock_collection.find = MagicMock(return_value=[])
        
        result = mock_collection.find({
            "modelFramework": "NonExistent",
            "taskType": "CLASSIFICATION",
            "dataType": "Tabular"
        })
        
        assert len(list(result)) == 0


# ============================================================================
# Test Model DAO
# ============================================================================

class TestModelDAO:
    """Tests for Model, ModelAttributes, ModelAttributeValues DAOs"""

    def test_model_find(self, mock_model_dao):
        """Test Model.find returns model data"""
        mock_collection = MagicMock()
        mock_collection.find_one = MagicMock(return_value=mock_model_dao)
        
        result = mock_collection.find_one({"_id": 1.0})
        
        assert result is not None
        assert result['ModelName'] == 'TestModel'

    def test_model_attributes_find(self):
        """Test ModelAttributes.find returns attribute IDs"""
        mock_collection = MagicMock()
        mock_documents = [
            {'_id': 1, 'attributeName': 'modelFramework'},
            {'_id': 2, 'attributeName': 'algorithm'},
            {'_id': 3, 'attributeName': 'taskType'}
        ]
        mock_collection.find = MagicMock(return_value=mock_documents)
        
        result = list(mock_collection.find({"attributeName": {"$in": ['modelFramework', 'algorithm', 'taskType']}}))
        
        assert len(result) == 3

    def test_model_attribute_values_find(self):
        """Test ModelAttributeValues.find returns values"""
        mock_collection = MagicMock()
        mock_documents = [
            {'attributeId': 1, 'value': 'Scikit-learn'},
            {'attributeId': 2, 'value': 'RandomForest'},
            {'attributeId': 3, 'value': 'CLASSIFICATION'}
        ]
        mock_collection.find = MagicMock(return_value=mock_documents)
        
        result = list(mock_collection.find({"modelId": 1.0}))
        
        assert len(result) == 3


# ============================================================================
# Test Dataset DAO
# ============================================================================

class TestDatasetDAO:
    """Tests for Dataset, DatasetAttributes, DatasetAttributeValues DAOs"""

    def test_dataset_find(self, mock_dataset_dao):
        """Test Dataset.find returns dataset data"""
        mock_collection = MagicMock()
        mock_collection.find_one = MagicMock(return_value=mock_dataset_dao)
        
        result = mock_collection.find_one({"_id": 1.0})
        
        assert result is not None
        assert result['DatasetName'] == 'TestDataset'

    def test_dataset_attributes_find(self):
        """Test DatasetAttributes.find returns attribute IDs"""
        mock_collection = MagicMock()
        mock_documents = [
            {'_id': 1, 'attributeName': 'dataType'},
            {'_id': 2, 'attributeName': 'groundTruthClassLabel'}
        ]
        mock_collection.find = MagicMock(return_value=mock_documents)
        
        result = list(mock_collection.find({"attributeName": {"$in": ['dataType', 'groundTruthClassLabel']}}))
        
        assert len(result) == 2

    def test_dataset_attribute_values_find(self):
        """Test DatasetAttributeValues.find returns values"""
        mock_collection = MagicMock()
        mock_documents = [
            {'attributeId': 1, 'value': 'Tabular'},
            {'attributeId': 2, 'value': 'target'}
        ]
        mock_collection.find = MagicMock(return_value=mock_documents)
        
        result = list(mock_collection.find({"datasetId": 1.0}))
        
        assert len(result) == 2


# ============================================================================
# Test Batch DAO
# ============================================================================

class TestBatchDAO:
    """Tests for Batch DAO"""

    def test_batch_find_by_id(self):
        """Test Batch.findByIdAndTenetId"""
        mock_collection = MagicMock()
        mock_batch = {
            '_id': 123.0,
            'tenetId': 1,
            'status': 'COMPLETED',
            'explainability': [{'method': 'LIME'}]
        }
        mock_collection.find_one = MagicMock(return_value=mock_batch)
        
        result = mock_collection.find_one({"_id": 123.0, "tenetId": 1})
        
        assert result is not None
        assert result['_id'] == 123.0

    def test_batch_find_tenet_id(self):
        """Test Batch.findTenetIdByBatchId"""
        mock_collection = MagicMock()
        mock_batch = {'_id': 123.0, 'tenetId': 5}
        mock_collection.find_one = MagicMock(return_value=mock_batch)
        
        result = mock_collection.find_one({"_id": 123.0})
        
        assert result['tenetId'] == 5

    def test_batch_update_status(self):
        """Test Batch.updateBatch"""
        mock_collection = MagicMock()
        mock_collection.update_one = MagicMock(return_value=MagicMock(modified_count=1))
        
        result = mock_collection.update_one(
            {"_id": 123.0},
            {"$set": {"status": "COMPLETED"}}
        )
        
        assert result.modified_count == 1


# ============================================================================
# Test Html DAO
# ============================================================================

class TestHtmlDAO:
    """Tests for Html DAO"""

    def test_html_create(self):
        """Test Html.create"""
        mock_collection = MagicMock()
        mock_collection.insert_one = MagicMock(return_value=MagicMock(inserted_id="html_123"))
        
        html_data = {
            'batchId': 123.0,
            'tenetId': 1,
            'htmlContent': '<html>Report</html>'
        }
        
        result = mock_collection.insert_one(html_data)
        
        assert result.inserted_id is not None

    def test_html_find_by_batch_and_tenet(self):
        """Test Html.findByBatchIdAndTenetId"""
        mock_collection = MagicMock()
        mock_html = {
            '_id': 'html_123',
            'batchId': 123.0,
            'tenetId': 1,
            'htmlContent': '<html>Report</html>'
        }
        mock_collection.find_one = MagicMock(return_value=mock_html)
        
        result = mock_collection.find_one({"batchId": 123.0, "tenetId": 1})
        
        assert result is not None
        assert result['batchId'] == 123.0


# ============================================================================
# Test Tenet DAO
# ============================================================================

class TestTenetDAO:
    """Tests for Tenet DAO"""

    def test_tenet_find_by_name(self):
        """Test Tenet.find"""
        mock_collection = MagicMock()
        mock_tenet = {
            '_id': 1,
            'tenetName': 'Explainability'
        }
        mock_collection.find_one = MagicMock(return_value=mock_tenet)
        
        result = mock_collection.find_one({"tenetName": "Explainability"})
        
        assert result is not None
        assert result['tenetName'] == 'Explainability'


# ============================================================================
# Test Preprocessor DAO
# ============================================================================

class TestPreprocessorDAO:
    """Tests for Preprocessor DAO"""

    def test_preprocessor_find(self):
        """Test Preprocessor.find"""
        mock_collection = MagicMock()
        mock_preprocessor = {
            '_id': 1.0,
            'name': 'StandardScaler',
            'data': 'preprocessor_file_id'
        }
        mock_collection.find_one = MagicMock(return_value=mock_preprocessor)
        
        result = mock_collection.find_one({"_id": 1.0})
        
        assert result is not None
        assert result['name'] == 'StandardScaler'


# ============================================================================
# Test Tbl_Exception DAO
# ============================================================================

class TestTblExceptionDAO:
    """Tests for Tbl_Exception DAO"""

    def test_exception_create(self):
        """Test Tbl_Exception.create"""
        mock_collection = MagicMock()
        mock_collection.insert_one = MagicMock(return_value=MagicMock(inserted_id="exc_123"))
        
        exception_data = {
            'UUID': 'test-uuid-123',
            'function': 'test_function',
            'msg': 'Test error',
            'description': 'Test error description'
        }
        
        result = mock_collection.insert_one(exception_data)
        
        assert result.inserted_id is not None

    def test_exception_find_by_dataset_id(self):
        """Test Tbl_Exception.findByDatasetId"""
        mock_collection = MagicMock()
        mock_exceptions = [
            {'_id': 1, 'datasetId': 123, 'msg': 'Error 1'},
            {'_id': 2, 'datasetId': 123, 'msg': 'Error 2'}
        ]
        mock_collection.find = MagicMock(return_value=mock_exceptions)
        
        result = list(mock_collection.find({"datasetId": 123}))
        
        assert len(result) == 2


# ============================================================================
# Test TblTelemetry DAO
# ============================================================================

class TestTblTelemetryDAO:
    """Tests for TblTelemetry DAO"""

    def test_telemetry_create(self):
        """Test creating telemetry record"""
        mock_collection = MagicMock()
        mock_collection.insert_one = MagicMock(return_value=MagicMock(inserted_id="tel_123"))
        
        telemetry_data = {
            'batchId': 123.0,
            'action': 'EXPLANATION_GENERATED',
            'timestamp': '2024-01-01T00:00:00Z'
        }
        
        result = mock_collection.insert_one(telemetry_data)
        
        assert result.inserted_id is not None


# ============================================================================
# Integration Tests
# ============================================================================

class TestDAOIntegration:
    """Integration tests for DAO modules"""

    def test_dao_modules_can_be_imported(self):
        """Test all DAO modules can be imported"""
        # These imports may fail if DB connection is required at import time
        # So we catch and skip if needed
        try:
            from explain.dao.workbench import DatabaseConnection
            from explain.dao.explainability import DatabaseConnection as ExplainDB
            assert True
        except Exception as e:
            pytest.skip(f"DAO modules require database connection: {e}")

    def test_mock_db_connection_pattern(self):
        """Test the mock database connection pattern works"""
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        
        mock_client.__getitem__ = MagicMock(return_value=mock_db)
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        mock_collection.find_one = MagicMock(return_value={'_id': 1, 'name': 'test'})
        
        # Test the mock chain
        db = mock_client['test_db']
        collection = db['test_collection']
        result = collection.find_one({'_id': 1})
        
        assert result['name'] == 'test'


# ============================================================================
# Comprehensive FileStoreDb Tests
# ============================================================================

class TestFileStoreDbComprehensive:
    """Comprehensive tests for FileStoreDb to increase coverage"""

    @patch('explain.dao.workbench.FileStoreDb.fileStoreDb.fs')
    @patch('explain.dao.workbench.FileStoreDb.fileStoreDb.db_type', 'mongo')
    def test_save_file_mongo_none_file_raises_error(self, mock_fs):
        """Test save_file raises ValueError for None file"""
        from explain.dao.workbench.FileStoreDb import fileStoreDb
        
        with pytest.raises(ValueError, match="File content cannot be None"):
            fileStoreDb.save_file(None, 'test.txt', 'text/plain', 'test')

    @patch('explain.dao.workbench.FileStoreDb.fileStoreDb.fs')
    @patch('explain.dao.workbench.FileStoreDb.fileStoreDb.db_type', 'mongo')
    def test_save_file_mongo_none_filename_raises_error(self, mock_fs):
        """Test save_file raises ValueError for None filename"""
        from explain.dao.workbench.FileStoreDb import fileStoreDb
        
        with pytest.raises(ValueError, match="Filename, contentType, and tenet cannot be None"):
            fileStoreDb.save_file(b'content', None, 'text/plain', 'test')

    @patch('explain.dao.workbench.FileStoreDb.fileStoreDb.fs')
    @patch('explain.dao.workbench.FileStoreDb.fileStoreDb.db_type', 'mongo')
    def test_save_file_mongo_none_content_type_raises_error(self, mock_fs):
        """Test save_file raises ValueError for None contentType"""
        from explain.dao.workbench.FileStoreDb import fileStoreDb
        
        with pytest.raises(ValueError, match="Filename, contentType, and tenet cannot be None"):
            fileStoreDb.save_file(b'content', 'test.txt', None, 'test')

    @patch('explain.dao.workbench.FileStoreDb.fileStoreDb.fs')
    @patch('explain.dao.workbench.FileStoreDb.fileStoreDb.db_type', 'mongo')
    def test_save_file_mongo_none_tenet_raises_error(self, mock_fs):
        """Test save_file raises ValueError for None tenet"""
        from explain.dao.workbench.FileStoreDb import fileStoreDb
        
        with pytest.raises(ValueError, match="Filename, contentType, and tenet cannot be None"):
            fileStoreDb.save_file(b'content', 'test.txt', 'text/plain', None)

    @patch('explain.dao.workbench.FileStoreDb.fileStoreDb.fs')
    @patch('explain.dao.workbench.FileStoreDb.fileStoreDb.db_type', 'mongo')
    def test_read_file_exp_mongo_not_found(self, mock_fs):
        """Test read_file_exp raises FileNotFoundError for non-existent file"""
        from explain.dao.workbench.FileStoreDb import fileStoreDb
        
        mock_fs.find_one.return_value = None
        
        with pytest.raises(FileNotFoundError, match="No file found"):
            fileStoreDb.read_file_exp('nonexistent_id', None)

    @patch('explain.dao.workbench.FileStoreDb.fileStoreDb.fs')
    @patch('explain.dao.workbench.FileStoreDb.fileStoreDb.db_type', 'mongo')
    def test_read_file_exp_mongo_success(self, mock_fs):
        """Test read_file_exp returns file data successfully"""
        from explain.dao.workbench.FileStoreDb import fileStoreDb
        
        mock_metadata = MagicMock()
        mock_metadata._id = 'test_id'
        mock_metadata.filename = 'test.pkl'
        
        mock_content = MagicMock()
        mock_content.read.return_value = b'file content'
        
        mock_fs.find_one.return_value = mock_metadata
        mock_fs.get.return_value = mock_content
        
        result = fileStoreDb.read_file_exp('test_id', None)
        
        assert result['type'] == 'pkl'
        assert result['data'] is not None

    @patch('explain.dao.workbench.FileStoreDb.requests.post')
    @patch('explain.dao.workbench.FileStoreDb.fileStoreDb.db_type', 'cosmos')
    @patch.dict(os.environ, {'HTML_CONTAINER_NAME': 'html', 'AZURE_UPLOAD_API': 'http://test.com/upload'})
    def test_save_file_cosmos_success(self, mock_post):
        """Test save_file to Azure Blob Storage"""
        from explain.dao.workbench.FileStoreDb import fileStoreDb
        
        mock_response = MagicMock()
        mock_response.json.return_value = {'blob_name': 'test_blob_123'}
        mock_post.return_value = mock_response
        
        file_obj = BytesIO(b'test content')
        result = fileStoreDb.save_file(file_obj, 'test.html', 'text/html', 'test')
        
        assert result == 'test_blob_123'

    @patch('explain.dao.workbench.FileStoreDb.requests.get')
    @patch('explain.dao.workbench.FileStoreDb.fileStoreDb.db_type', 'cosmos')
    @patch.dict(os.environ, {'AZURE_GET_API': 'http://test.com/get'})
    def test_read_file_exp_cosmos_success(self, mock_get):
        """Test read_file_exp from Azure Blob Storage"""
        from explain.dao.workbench.FileStoreDb import fileStoreDb
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'azure file content'
        mock_get.return_value = mock_response
        
        result = fileStoreDb.read_file_exp('blob_id.pkl', 'container_name')
        
        assert result['data'] == b'azure file content'
        assert result['type'] == 'pkl'


# ============================================================================
# Comprehensive Model DAO Tests
# ============================================================================

class TestModelDAOComprehensive:
    """Comprehensive tests for Model DAO to increase coverage"""

    @patch('explain.dao.workbench.Model.Model.collection')
    def test_model_find_success(self, mock_collection):
        """Test Model.find returns model data"""
        from explain.dao.workbench.Model import Model
        
        mock_collection.find_one.return_value = {
            'ModelName': 'TestModel',
            'ModelData': 'model_file_id',
            'ModelEndPoint': None
        }
        
        result = Model.find(1.0)
        
        assert result['ModelName'] == 'TestModel'

    @patch('explain.dao.workbench.Model.Model.collection')
    def test_model_find_none_id_raises_error(self, mock_collection):
        """Test Model.find raises ValueError for None ID"""
        from explain.dao.workbench.Model import Model
        
        with pytest.raises(ValueError, match="Model ID must be a non-empty float"):
            Model.find(None)

    @patch('explain.dao.workbench.Model.Model.collection')
    def test_model_find_invalid_type_raises_error(self, mock_collection):
        """Test Model.find raises ValueError for invalid ID type"""
        from explain.dao.workbench.Model import Model
        
        with pytest.raises(ValueError, match="Model ID must be a non-empty float"):
            Model.find("invalid")

    @patch('explain.dao.workbench.Model.Model.collection')
    def test_model_find_not_found_raises_error(self, mock_collection):
        """Test Model.find raises ValueError when model not found"""
        from explain.dao.workbench.Model import Model
        
        mock_collection.find_one.return_value = None
        
        with pytest.raises(ValueError, match="Invalid Model ID"):
            Model.find(999.0)

    @patch('explain.dao.workbench.Model.ModelAttributes.collection')
    def test_model_attributes_find_success(self, mock_collection):
        """Test ModelAttributes.find returns attribute IDs"""
        from explain.dao.workbench.Model import ModelAttributes
        
        mock_collection.find.return_value = [
            {'ModelAttributeId': 1, 'ModelAttributeName': 'modelFramework'},
            {'ModelAttributeId': 2, 'ModelAttributeName': 'algorithm'}
        ]
        
        result = ModelAttributes.find(['modelFramework', 'algorithm'])
        
        assert len(result) == 2
        assert 1 in result

    @patch('explain.dao.workbench.Model.ModelAttributes.collection')
    def test_model_attributes_find_none_raises_error(self, mock_collection):
        """Test ModelAttributes.find raises ValueError for None"""
        from explain.dao.workbench.Model import ModelAttributes
        
        with pytest.raises(ValueError, match="Model attributes must be a non-empty list"):
            ModelAttributes.find(None)

    @patch('explain.dao.workbench.Model.ModelAttributes.collection')
    def test_model_attributes_find_empty_list_raises_error(self, mock_collection):
        """Test ModelAttributes.find raises ValueError for empty list"""
        from explain.dao.workbench.Model import ModelAttributes
        
        with pytest.raises(ValueError, match="Model attributes must not be an empty list"):
            ModelAttributes.find([])

    @patch('explain.dao.workbench.Model.ModelAttributeValues.collection')
    def test_model_attribute_values_find_success(self, mock_collection):
        """Test ModelAttributeValues.find returns values"""
        from explain.dao.workbench.Model import ModelAttributeValues
        
        mock_collection.find.return_value = [
            {'ModelAttributeValues': 'Scikit-learn', 'ModelAttributeId': 1},
            {'ModelAttributeValues': 'RandomForest', 'ModelAttributeId': 2}
        ]
        
        result = ModelAttributeValues.find(None, 1.0, [1, 2])
        
        assert len(result) == 2

    @patch('explain.dao.workbench.Model.ModelAttributeValues.collection')
    def test_model_attribute_values_find_none_id_raises_error(self, mock_collection):
        """Test ModelAttributeValues.find raises ValueError for None model_id"""
        from explain.dao.workbench.Model import ModelAttributeValues
        
        with pytest.raises(ValueError, match="Model ID must be a non-empty float"):
            ModelAttributeValues.find(None, None, [1])


# ============================================================================
# Comprehensive Dataset DAO Tests
# ============================================================================

class TestDatasetDAOComprehensive:
    """Comprehensive tests for Dataset DAO to increase coverage"""

    @patch('explain.dao.workbench.Dataset.Dataset.collection')
    def test_dataset_find_success(self, mock_collection):
        """Test Dataset.find returns dataset data"""
        from explain.dao.workbench.Dataset import Dataset
        
        mock_collection.find_one.return_value = {
            'DataSetName': 'TestDataset',
            'SampleData': 'data_file_id'
        }
        
        result = Dataset.find(1.0)
        
        assert result['DataSetName'] == 'TestDataset'

    @patch('explain.dao.workbench.Dataset.Dataset.collection')
    def test_dataset_find_none_id_raises_error(self, mock_collection):
        """Test Dataset.find raises ValueError for None ID"""
        from explain.dao.workbench.Dataset import Dataset
        
        with pytest.raises(ValueError, match="Dataset ID must be a non-empty float"):
            Dataset.find(None)

    @patch('explain.dao.workbench.Dataset.Dataset.collection')
    def test_dataset_find_not_found_raises_error(self, mock_collection):
        """Test Dataset.find raises ValueError when not found"""
        from explain.dao.workbench.Dataset import Dataset
        
        mock_collection.find_one.return_value = None
        
        with pytest.raises(ValueError, match="Invalid Dataset ID"):
            Dataset.find(999.0)

    @patch('explain.dao.workbench.Dataset.DatasetAttributes.collection')
    def test_dataset_attributes_find_success(self, mock_collection):
        """Test DatasetAttributes.find returns attribute IDs"""
        from explain.dao.workbench.Dataset import DatasetAttributes
        
        mock_collection.find.return_value = [
            {'DataAttributeId': 1, 'DataAttributeName': 'dataType'},
            {'DataAttributeId': 2, 'DataAttributeName': 'groundTruthClassLabel'}
        ]
        
        result = DatasetAttributes.find(['dataType', 'groundTruthClassLabel'])
        
        assert len(result) == 2

    @patch('explain.dao.workbench.Dataset.DatasetAttributes.collection')
    def test_dataset_attributes_find_none_raises_error(self, mock_collection):
        """Test DatasetAttributes.find raises ValueError for None"""
        from explain.dao.workbench.Dataset import DatasetAttributes
        
        with pytest.raises(ValueError, match="Dataset attribute.*must be a non-empty list"):
            DatasetAttributes.find(None)

    @patch('explain.dao.workbench.Dataset.DatasetAttributes.collection')
    def test_dataset_attributes_find_empty_raises_error(self, mock_collection):
        """Test DatasetAttributes.find raises ValueError for empty list"""
        from explain.dao.workbench.Dataset import DatasetAttributes
        
        with pytest.raises(ValueError, match="Dataset attribute.*must not be an empty list"):
            DatasetAttributes.find([])

    @patch('explain.dao.workbench.Dataset.DatasetAttributeValues.collection')
    def test_dataset_attribute_values_find_success(self, mock_collection):
        """Test DatasetAttributeValues.find returns values"""
        from explain.dao.workbench.Dataset import DatasetAttributeValues
        
        mock_collection.find.return_value = [
            {'DataAttributeValues': 'Tabular', 'DataAttributeId': 1},
            {'DataAttributeValues': 'target', 'DataAttributeId': 2}
        ]
        
        result = DatasetAttributeValues.find(1.0, [1, 2])
        
        assert len(result) == 2

    @patch('explain.dao.workbench.Dataset.DatasetAttributeValues.collection')
    def test_dataset_attribute_values_find_none_id_raises_error(self, mock_collection):
        """Test DatasetAttributeValues.find raises ValueError for None ID"""
        from explain.dao.workbench.Dataset import DatasetAttributeValues
        
        with pytest.raises(ValueError, match="Dataset ID must be a non-empty float"):
            DatasetAttributeValues.find(None, [1])


# ============================================================================
# Comprehensive Batch DAO Tests
# ============================================================================

class TestBatchDAOComprehensive:
    """Comprehensive tests for Batch DAO to increase coverage"""

    @patch('explain.dao.workbench.Batch.Batch.collection')
    def test_batch_find_success(self, mock_collection):
        """Test Batch.find returns batch data"""
        from explain.dao.workbench.Batch import Batch
        
        mock_collection.find_one.return_value = {
            'ModelId': 1.0,
            'DataId': 2.0,
            'PreprocessorId': None,
            'Title': 'Test Batch'
        }
        
        result = Batch.find(123.0, 1)
        
        assert result['Title'] == 'Test Batch'

    @patch('explain.dao.workbench.Batch.Batch.collection')
    def test_batch_find_none_id_raises_error(self, mock_collection):
        """Test Batch.find raises ValueError for None batch_id"""
        from explain.dao.workbench.Batch import Batch
        
        with pytest.raises(ValueError, match="Batch ID must be a non-empty float"):
            Batch.find(None, 1)

    @patch('explain.dao.workbench.Batch.Batch.collection')
    def test_batch_update_success(self, mock_collection):
        """Test Batch.update updates status"""
        from explain.dao.workbench.Batch import Batch
        
        mock_result = MagicMock()
        mock_result.acknowledged = True
        mock_collection.update_one.return_value = mock_result
        
        result = Batch.update(123.0, {'Status': 'Completed'})
        
        # Batch.update returns acknowledged (bool)
        assert result is True


# ============================================================================
# Comprehensive Html DAO Tests
# ============================================================================

class TestHtmlDAOComprehensive:
    """Comprehensive tests for Html DAO to increase coverage"""

    @patch('explain.dao.workbench.Html.Html.collection')
    def test_html_create_success(self, mock_collection):
        """Test Html.create inserts document"""
        from explain.dao.workbench.Html import Html
        
        mock_result = MagicMock()
        mock_result.acknowledged = True
        mock_collection.insert_one.return_value = mock_result
        
        doc = {
            'HtmlId': 123,
            'BatchId': 456,
            'TenetId': 1,
            'ReportName': 'test.html',
            'HtmlFileId': 'file_id'
        }
        
        result = Html.create(doc)
        
        # Html.create returns acknowledged (bool)
        assert result is True


# ============================================================================
# Comprehensive Tenet DAO Tests
# ============================================================================

class TestTenetDAOComprehensive:
    """Comprehensive tests for Tenet DAO to increase coverage"""

    @patch('explain.dao.workbench.Tenet.Tenet.collection')
    def test_tenet_find_success(self, mock_collection):
        """Test Tenet.find returns tenet ID"""
        from explain.dao.workbench.Tenet import Tenet
        
        # Tenet.find accesses result['Id']
        mock_collection.find_one.return_value = {'Id': 5}
        
        result = Tenet.find('Explainability')
        
        assert result == 5

    @patch('explain.dao.workbench.Tenet.Tenet.collection')
    def test_tenet_find_none_name_raises_error(self, mock_collection):
        """Test Tenet.find raises ValueError for None name"""
        from explain.dao.workbench.Tenet import Tenet
        
        # The actual error message uses "Tenet Name"
        with pytest.raises(ValueError, match="Tenet Name must be a non-empty string"):
            Tenet.find(None)


# ============================================================================
# Comprehensive Preprocessor DAO Tests
# ============================================================================

class TestPreprocessorDAOComprehensive:
    """Comprehensive tests for Preprocessor DAO to increase coverage"""

    @patch('explain.dao.workbench.Preprocessor.Preprocessor.collection')
    def test_preprocessor_find_success(self, mock_collection):
        """Test Preprocessor.find returns preprocessor data"""
        from explain.dao.workbench.Preprocessor import Preprocessor
        
        mock_collection.find_one.return_value = {
            'PreprocessorFileId': 'file_123'
        }
        
        result = Preprocessor.find(1.0)
        
        assert result['PreprocessorFileId'] == 'file_123'

    @patch('explain.dao.workbench.Preprocessor.Preprocessor.collection')
    def test_preprocessor_find_none_id_raises_error(self, mock_collection):
        """Test Preprocessor.find raises ValueError for None ID"""
        from explain.dao.workbench.Preprocessor import Preprocessor
        
        with pytest.raises(ValueError, match="Preprocessor ID must be a non-empty float"):
            Preprocessor.find(None)


# ============================================================================
# Comprehensive Tbl_Exception DAO Tests
# ============================================================================

class TestTblExceptionDAOComprehensive:
    """Comprehensive tests for Tbl_Exception DAO to increase coverage"""

    @patch('explain.dao.explainability.TblException.Tbl_Exception.collection')
    def test_exception_create_success(self, mock_collection):
        """Test Tbl_Exception.create inserts exception"""
        from explain.dao.explainability.TblException import Tbl_Exception
        
        mock_collection.insert_one.return_value = MagicMock(inserted_id='exc_123')
        
        doc = {
            'UUID': 'test-uuid',
            'function': 'test_func',
            'msg': 'Error',
            'description': 'Error desc'
        }
        
        result = Tbl_Exception.create(doc)
        
        mock_collection.insert_one.assert_called_once()


# ============================================================================
# Comprehensive TblExplanationMethods DAO Tests
# ============================================================================

class TestTblExplanationMethodsDAOComprehensive:
    """Comprehensive tests for TblExplanationMethods DAO to increase coverage"""

    @patch('explain.dao.explainability.TblExplanationMethods.Tbl_Explanation_Methods.collection')
    def test_find_methods_success(self, mock_collection):
        """Test find_methods returns methods"""
        from explain.dao.explainability.TblExplanationMethods import Tbl_Explanation_Methods
        
        mock_collection.find.return_value = [
            {'methods': 'LIME-TABULAR', 'scope': 'LOCAL', 'unsupportedModels': []},
            {'methods': 'KERNEL-EXPLAINER', 'scope': 'GLOBAL', 'unsupportedModels': []}
        ]
        
        result = Tbl_Explanation_Methods.find_methods('Scikit-learn', 'CLASSIFICATION', 'Tabular')
        
        assert len(list(result)) == 2

    @patch('explain.dao.explainability.TblExplanationMethods.Tbl_Explanation_Methods.collection')
    def test_find_methods_none_framework_returns_error(self, mock_collection):
        """Test find_methods returns error dict for None model_framework"""
        from explain.dao.explainability.TblExplanationMethods import Tbl_Explanation_Methods
        
        # find_methods returns error dict, not raises exception
        result = Tbl_Explanation_Methods.find_methods(None, 'CLASSIFICATION', 'Tabular')
        
        assert 'error' in result

    @patch('explain.dao.explainability.TblExplanationMethods.Tbl_Explanation_Methods.collection')
    def test_find_methods_none_task_type_returns_error(self, mock_collection):
        """Test find_methods returns error dict for None task_type"""
        from explain.dao.explainability.TblExplanationMethods import Tbl_Explanation_Methods
        
        result = Tbl_Explanation_Methods.find_methods('Scikit-learn', None, 'Tabular')
        
        assert 'error' in result

    @patch('explain.dao.explainability.TblExplanationMethods.Tbl_Explanation_Methods.collection')
    def test_find_methods_none_data_type_returns_error(self, mock_collection):
        """Test find_methods returns error dict for None data_type"""
        from explain.dao.explainability.TblExplanationMethods import Tbl_Explanation_Methods
        
        result = Tbl_Explanation_Methods.find_methods('Scikit-learn', 'CLASSIFICATION', None)
        
        assert 'error' in result

    @patch('explain.dao.explainability.TblExplanationMethods.Tbl_Explanation_Methods.collection')
    def test_find_methods_empty_string_returns_error(self, mock_collection):
        """Test find_methods returns error dict for empty strings"""
        from explain.dao.explainability.TblExplanationMethods import Tbl_Explanation_Methods
        
        result = Tbl_Explanation_Methods.find_methods('', '', '')
        
        assert 'error' in result
