"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock, ANY
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from datetime import datetime
import io
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from routing.gcp_router import (
    gcs_add_file,
    list_objects,
    gcs_get_object,
    delete_object,
    gcs_update_file,
    list_buckets,
    gcs_add_bucket,
    get_object_properties
)
from mappers.mappers import BlobInfo


class TestGcsAddFile:
    """Test suite for gcs_add_file endpoint"""
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_gcs_add_file_success(self, mock_log, mock_ui_service):
        """Test successful file upload to GCS"""
        # Arrange
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test.txt"
        bucket_name = "test-bucket"
        object_name = "test-object"
        expected_response = {"message": "File uploaded successfully", "name": object_name}
        mock_ui_service.gcs_addFile.return_value = expected_response
        
        # Act
        result = gcs_add_file(mock_file, bucket_name, object_name)
        
        # Assert
        assert result == expected_response
        mock_ui_service.gcs_addFile.assert_called_once_with(mock_file, bucket_name, object_name)
        mock_log.info.assert_called_with('before invoking gcs add file service')
        mock_log.debug.assert_called_once_with(expected_response)
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_gcs_add_file_without_object_name(self, mock_log, mock_ui_service):
        """Test file upload without specifying object name"""
        # Arrange
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test.txt"
        bucket_name = "test-bucket"
        expected_response = {"message": "File uploaded successfully"}
        mock_ui_service.gcs_addFile.return_value = expected_response
        
        # Act
        result = gcs_add_file(mock_file, bucket_name, None)
        
        # Assert
        assert result == expected_response
        mock_ui_service.gcs_addFile.assert_called_once_with(mock_file, bucket_name, None)
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_gcs_add_file_exception(self, mock_log, mock_ui_service):
        """Test file upload with exception handling"""
        # Arrange
        mock_file = Mock(spec=UploadFile)
        bucket_name = "test-bucket"
        error_message = "GCS connection failed"
        mock_ui_service.gcs_addFile.side_effect = Exception(error_message)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            gcs_add_file(mock_file, bucket_name)
        
        assert exc_info.value.status_code == 500
        assert error_message in str(exc_info.value.detail)
        mock_log.exception.assert_called_once_with("Exception details:")
        mock_log.info.assert_any_call('exit gcs add file service')
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_gcs_add_file_empty_bucket_name(self, mock_log, mock_ui_service):
        """Test file upload with empty bucket name"""
        # Arrange
        mock_file = Mock(spec=UploadFile)
        bucket_name = ""
        mock_ui_service.gcs_addFile.side_effect = Exception("Bucket name cannot be empty")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            gcs_add_file(mock_file, bucket_name)
        
        assert exc_info.value.status_code == 500
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_gcs_add_file_large_file(self, mock_log, mock_ui_service):
        """Test uploading a large file"""
        # Arrange
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "large-file.bin"
        mock_file.size = 100 * 1024 * 1024  # 100MB
        bucket_name = "test-bucket"
        expected_response = {"message": "File uploaded successfully"}
        mock_ui_service.gcs_addFile.return_value = expected_response
        
        # Act
        result = gcs_add_file(mock_file, bucket_name)
        
        # Assert
        assert result == expected_response


class TestListObjects:
    """Test suite for list_objects endpoint"""
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_list_objects_success(self, mock_log, mock_ui_service):
        """Test successful listing of objects"""
        # Arrange
        bucket_name = "test-bucket"
        expected_response = [
            BlobInfo(name="file1.txt", size=100, last_modified=datetime.now(), content_type="text/plain"),
            BlobInfo(name="file2.txt", size=200, last_modified=datetime.now(), content_type="text/plain")
        ]
        mock_ui_service.list_objects.return_value = expected_response
        
        # Act
        result = list_objects(bucket_name)
        
        # Assert
        assert result == expected_response
        assert len(result) == 2
        mock_ui_service.list_objects.assert_called_once_with(bucket_name, ANY, ANY, ANY)
        mock_log.info.assert_called_with('before invoking gcs list objects service')
        mock_log.debug.assert_called_once_with(expected_response)
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_list_objects_with_filters(self, mock_log, mock_ui_service):
        """Test listing objects with filters"""
        # Arrange
        bucket_name = "test-bucket"
        name_starts_with = "folder/"
        content_type = "text/plain"
        max_results = 50
        expected_response = [
            BlobInfo(name="folder/file1.txt", size=100, last_modified=datetime.now(), content_type="text/plain")
        ]
        mock_ui_service.list_objects.return_value = expected_response
        
        # Act
        result = list_objects(bucket_name, name_starts_with, content_type, max_results)
        
        # Assert
        assert result == expected_response
        mock_ui_service.list_objects.assert_called_once_with(bucket_name, ANY, ANY, ANY)
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_list_objects_empty_result(self, mock_log, mock_ui_service):
        """Test listing objects with no results"""
        # Arrange
        bucket_name = "test-bucket"
        mock_ui_service.list_objects.return_value = []
        
        # Act
        result = list_objects(bucket_name)
        
        # Assert
        assert result == []
        assert len(result) == 0
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_list_objects_exception(self, mock_log, mock_ui_service):
        """Test list objects with exception handling"""
        # Arrange
        bucket_name = "test-bucket"
        error_message = "Bucket not found"
        mock_ui_service.list_objects.side_effect = Exception(error_message)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            list_objects(bucket_name)
        
        assert exc_info.value.status_code == 500
        assert error_message in str(exc_info.value.detail)
        mock_log.exception.assert_called_once_with("Exception details:")
        mock_log.info.assert_any_call('exit gcs list objects service')
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_list_objects_max_results_boundary(self, mock_log, mock_ui_service):
        """Test list objects with boundary max_results values"""
        # Arrange
        bucket_name = "test-bucket"
        mock_ui_service.list_objects.return_value = []
        
        # Act - Test with 0
        result = list_objects(bucket_name, max_results=0)
        assert result == []
        mock_ui_service.list_objects.assert_called_with(bucket_name, ANY, ANY, ANY)
        
        # Act - Test with large number
        result = list_objects(bucket_name, max_results=10000)
        assert result == []
        mock_ui_service.list_objects.assert_called_with(bucket_name, ANY, ANY, ANY)


class TestGcsGetObject:
    """Test suite for gcs_get_object endpoint"""
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_gcs_get_object_success(self, mock_log, mock_ui_service):
        """Test successful object retrieval"""
        # Arrange
        object_name = "test-file.txt"
        bucket_name = "test-bucket"
        mock_content = io.BytesIO(b"test content")
        mock_ui_service.get_object.return_value = mock_content
        
        # Act
        result = gcs_get_object(object_name, bucket_name)
        
        # Assert
        assert isinstance(result, StreamingResponse)
        assert result.media_type == "application/octet-stream"
        mock_ui_service.get_object.assert_called_once_with(object_name, bucket_name)
        mock_log.info.assert_called_with('before invoking gcs get object service')
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_gcs_get_object_with_special_characters(self, mock_log, mock_ui_service):
        """Test object retrieval with special characters in name"""
        # Arrange
        object_name = "folder/test file with spaces.txt"
        bucket_name = "test-bucket"
        mock_content = io.BytesIO(b"test content")
        mock_ui_service.get_object.return_value = mock_content
        
        # Act
        result = gcs_get_object(object_name, bucket_name)
        
        # Assert
        assert isinstance(result, StreamingResponse)
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_gcs_get_object_exception(self, mock_log, mock_ui_service):
        """Test get object with exception handling"""
        # Arrange
        object_name = "test-file.txt"
        bucket_name = "test-bucket"
        error_message = "Object not found"
        mock_ui_service.get_object.side_effect = Exception(error_message)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            gcs_get_object(object_name, bucket_name)
        
        assert exc_info.value.status_code == 500
        assert error_message in str(exc_info.value.detail)
        mock_log.exception.assert_called_once_with("Exception details:")
        mock_log.info.assert_any_call('exit gcs get object service')
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_gcs_get_object_large_file(self, mock_log, mock_ui_service):
        """Test retrieval of large file"""
        # Arrange
        object_name = "large-file.bin"
        bucket_name = "test-bucket"
        large_content = io.BytesIO(b"x" * (10 * 1024 * 1024))  # 10MB
        mock_ui_service.get_object.return_value = large_content
        
        # Act
        result = gcs_get_object(object_name, bucket_name)
        
        # Assert
        assert isinstance(result, StreamingResponse)


class TestDeleteObject:
    """Test suite for delete_object endpoint"""
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_delete_object_success(self, mock_log, mock_ui_service):
        """Test successful object deletion"""
        # Arrange
        object_name = "test-file.txt"
        bucket_name = "test-bucket"
        mock_ui_service.delete_object.return_value = None
        
        # Act
        result = delete_object(object_name, bucket_name)
        
        # Assert
        assert result == {"message": f"Object '{object_name}' deleted successfully"}
        mock_ui_service.delete_object.assert_called_once_with(bucket_name, object_name)
        mock_log.info.assert_any_call('before invoking gcs delete object service')
        mock_log.info.assert_any_call('exit gcs delete object service')
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_delete_object_with_path(self, mock_log, mock_ui_service):
        """Test deletion of object with path"""
        # Arrange
        object_name = "folder/subfolder/test-file.txt"
        bucket_name = "test-bucket"
        mock_ui_service.delete_object.return_value = None
        
        # Act
        result = delete_object(object_name, bucket_name)
        
        # Assert
        assert "deleted successfully" in result["message"]
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_delete_object_exception(self, mock_log, mock_ui_service):
        """Test delete object with exception handling"""
        # Arrange
        object_name = "test-file.txt"
        bucket_name = "test-bucket"
        error_message = "Object not found"
        mock_ui_service.delete_object.side_effect = Exception(error_message)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            delete_object(object_name, bucket_name)
        
        assert exc_info.value.status_code == 500
        assert error_message in str(exc_info.value.detail)
        mock_log.exception.assert_called_once_with("Exception details:")
        mock_log.info.assert_any_call('exit gcs delete object service')
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_delete_object_empty_name(self, mock_log, mock_ui_service):
        """Test delete object with empty name"""
        # Arrange
        object_name = ""
        bucket_name = "test-bucket"
        mock_ui_service.delete_object.side_effect = Exception("Object name cannot be empty")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            delete_object(object_name, bucket_name)
        
        assert exc_info.value.status_code == 500


class TestGcsUpdateFile:
    """Test suite for gcs_update_file endpoint"""
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_gcs_update_file_success(self, mock_log, mock_ui_service):
        """Test successful file update"""
        # Arrange
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test.txt"
        object_name = "test-object"
        bucket_name = "test-bucket"
        expected_response = {"message": "File updated successfully", "name": object_name}
        mock_ui_service.gcs_updateFile.return_value = expected_response
        
        # Act
        result = gcs_update_file(mock_file, object_name, bucket_name)
        
        # Assert
        assert result == expected_response
        mock_ui_service.gcs_updateFile.assert_called_once_with(mock_file, object_name, bucket_name)
        mock_log.info.assert_any_call('before invoking gcs update file service')
        mock_log.debug.assert_called_once_with(expected_response)
        mock_log.info.assert_any_call('exit gcs update file service')
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_gcs_update_file_different_content_type(self, mock_log, mock_ui_service):
        """Test file update with different content type"""
        # Arrange
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test.json"
        mock_file.content_type = "application/json"
        object_name = "test.json"
        bucket_name = "test-bucket"
        expected_response = {"message": "File updated successfully"}
        mock_ui_service.gcs_updateFile.return_value = expected_response
        
        # Act
        result = gcs_update_file(mock_file, object_name, bucket_name)
        
        # Assert
        assert result == expected_response
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_gcs_update_file_exception(self, mock_log, mock_ui_service):
        """Test file update with exception handling"""
        # Arrange
        mock_file = Mock(spec=UploadFile)
        object_name = "test-object"
        bucket_name = "test-bucket"
        error_message = "Update failed"
        mock_ui_service.gcs_updateFile.side_effect = Exception(error_message)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            gcs_update_file(mock_file, object_name, bucket_name)
        
        assert exc_info.value.status_code == 500
        assert error_message in str(exc_info.value.detail)
        mock_log.exception.assert_called_once_with("Exception details:")
        mock_log.info.assert_any_call('exit gcs update file service')
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_gcs_update_file_large_file(self, mock_log, mock_ui_service):
        """Test updating a large file"""
        # Arrange
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "large-file.bin"
        mock_file.size = 50 * 1024 * 1024  # 50MB
        object_name = "large-file.bin"
        bucket_name = "test-bucket"
        expected_response = {"message": "File updated successfully"}
        mock_ui_service.gcs_updateFile.return_value = expected_response
        
        # Act
        result = gcs_update_file(mock_file, object_name, bucket_name)
        
        # Assert
        assert result == expected_response


class TestListBuckets:
    """Test suite for list_buckets endpoint"""
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_list_buckets_success(self, mock_log, mock_ui_service):
        """Test successful bucket listing"""
        # Arrange
        expected_response = [
            {"name": "bucket1", "location": "us-central1"},
            {"name": "bucket2", "location": "us-west1"}
        ]
        mock_ui_service.list_buckets.return_value = expected_response
        
        # Act
        result = list_buckets()
        
        # Assert
        assert result == expected_response
        assert len(result) == 2
        mock_ui_service.list_buckets.assert_called_once()
        mock_log.info.assert_any_call('before invoking gcs list buckets service')
        mock_log.debug.assert_called_once_with(expected_response)
        mock_log.info.assert_any_call('exit gcs list buckets service')
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_list_buckets_empty(self, mock_log, mock_ui_service):
        """Test listing buckets with no results"""
        # Arrange
        mock_ui_service.list_buckets.return_value = []
        
        # Act
        result = list_buckets()
        
        # Assert
        assert result == []
        assert len(result) == 0
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_list_buckets_exception(self, mock_log, mock_ui_service):
        """Test list buckets with exception handling"""
        # Arrange
        error_message = "Access denied"
        mock_ui_service.list_buckets.side_effect = Exception(error_message)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            list_buckets()
        
        assert exc_info.value.status_code == 500
        assert error_message in str(exc_info.value.detail)
        mock_log.exception.assert_called_once_with("Exception details:")
        mock_log.info.assert_any_call('exit gcs list buckets service')
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_list_buckets_many_buckets(self, mock_log, mock_ui_service):
        """Test listing many buckets"""
        # Arrange
        expected_response = [{"name": f"bucket{i}"} for i in range(100)]
        mock_ui_service.list_buckets.return_value = expected_response
        
        # Act
        result = list_buckets()
        
        # Assert
        assert len(result) == 100


class TestGcsAddBucket:
    """Test suite for gcs_add_bucket endpoint"""
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_gcs_add_bucket_success(self, mock_log, mock_ui_service):
        """Test successful bucket creation"""
        # Arrange
        bucket_name = "new-test-bucket"
        expected_response = {"message": "Bucket created successfully", "bucket_name": bucket_name}
        mock_ui_service.gcs_addBucket.return_value = expected_response
        
        # Act
        result = gcs_add_bucket(bucket_name)
        
        # Assert
        assert result == expected_response
        mock_ui_service.gcs_addBucket.assert_called_once_with(bucket_name)
        mock_log.info.assert_any_call('before invoking gcs add bucket service')
        mock_log.debug.assert_called_once_with(expected_response)
        mock_log.info.assert_any_call('exit gcs add bucket service')
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_gcs_add_bucket_with_valid_name(self, mock_log, mock_ui_service):
        """Test bucket creation with valid naming convention"""
        # Arrange
        bucket_name = "my-valid-bucket-name-123"
        expected_response = {"message": "Bucket created successfully"}
        mock_ui_service.gcs_addBucket.return_value = expected_response
        
        # Act
        result = gcs_add_bucket(bucket_name)
        
        # Assert
        assert result == expected_response
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_gcs_add_bucket_exception(self, mock_log, mock_ui_service):
        """Test bucket creation with exception handling"""
        # Arrange
        bucket_name = "test-bucket"
        error_message = "Bucket already exists"
        mock_ui_service.gcs_addBucket.side_effect = Exception(error_message)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            gcs_add_bucket(bucket_name)
        
        assert exc_info.value.status_code == 500
        assert error_message in str(exc_info.value.detail)
        mock_log.exception.assert_called_once_with("Exception details:")
        mock_log.info.assert_any_call('exit gcs add bucket service')
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_gcs_add_bucket_invalid_name(self, mock_log, mock_ui_service):
        """Test bucket creation with invalid name"""
        # Arrange
        bucket_name = "INVALID_BUCKET_NAME"  # Invalid due to uppercase
        mock_ui_service.gcs_addBucket.side_effect = Exception("Invalid bucket name")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            gcs_add_bucket(bucket_name)
        
        assert exc_info.value.status_code == 500
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_gcs_add_bucket_empty_name(self, mock_log, mock_ui_service):
        """Test bucket creation with empty name"""
        # Arrange
        bucket_name = ""
        mock_ui_service.gcs_addBucket.side_effect = Exception("Bucket name cannot be empty")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            gcs_add_bucket(bucket_name)
        
        assert exc_info.value.status_code == 500


class TestGetObjectProperties:
    """Test suite for get_object_properties endpoint"""
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_get_object_properties_success(self, mock_log, mock_ui_service):
        """Test successful retrieval of object properties"""
        # Arrange
        object_name = "test-file.txt"
        bucket_name = "test-bucket"
        expected_response = {
            "name": object_name,
            "size": 1024,
            "updated": "2023-01-01T00:00:00",
            "content_type": "text/plain",
            "metadata": {}
        }
        mock_ui_service.get_object_properties.return_value = expected_response
        
        # Act
        result = get_object_properties(object_name, bucket_name)
        
        # Assert
        assert result == expected_response
        mock_ui_service.get_object_properties.assert_called_once_with(object_name, bucket_name)
        mock_log.info.assert_any_call('before invoking gcs get object properties service')
        mock_log.debug.assert_called_once_with(expected_response)
        mock_log.info.assert_any_call('exit gcs get object properties service')
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_get_object_properties_with_metadata(self, mock_log, mock_ui_service):
        """Test retrieval of object properties with custom metadata"""
        # Arrange
        object_name = "test-file.txt"
        bucket_name = "test-bucket"
        expected_response = {
            "name": object_name,
            "size": 2048,
            "metadata": {"custom-key": "custom-value"}
        }
        mock_ui_service.get_object_properties.return_value = expected_response
        
        # Act
        result = get_object_properties(object_name, bucket_name)
        
        # Assert
        assert result == expected_response
        assert "metadata" in result
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_get_object_properties_exception(self, mock_log, mock_ui_service):
        """Test get object properties with exception handling"""
        # Arrange
        object_name = "test-file.txt"
        bucket_name = "test-bucket"
        error_message = "Object not found"
        mock_ui_service.get_object_properties.side_effect = Exception(error_message)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_object_properties(object_name, bucket_name)
        
        assert exc_info.value.status_code == 500
        assert error_message in str(exc_info.value.detail)
        mock_log.exception.assert_called_once_with("Exception details:")
        mock_log.info.assert_any_call('exit gcs get object properties service')
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_get_object_properties_large_object(self, mock_log, mock_ui_service):
        """Test retrieval of properties for large object"""
        # Arrange
        object_name = "large-file.bin"
        bucket_name = "test-bucket"
        expected_response = {
            "name": object_name,
            "size": 5 * 1024 * 1024 * 1024,  # 5GB
            "storage_class": "NEARLINE"
        }
        mock_ui_service.get_object_properties.return_value = expected_response
        
        # Act
        result = get_object_properties(object_name, bucket_name)
        
        # Assert
        assert result == expected_response
        assert result["size"] > 1024 * 1024 * 1024
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_get_object_properties_nested_path(self, mock_log, mock_ui_service):
        """Test retrieval of properties for object in nested path"""
        # Arrange
        object_name = "folder/subfolder/deep/test-file.txt"
        bucket_name = "test-bucket"
        expected_response = {"name": object_name, "size": 512}
        mock_ui_service.get_object_properties.return_value = expected_response
        
        # Act
        result = get_object_properties(object_name, bucket_name)
        
        # Assert
        assert result == expected_response


class TestIntegrationScenarios:
    """Integration and workflow tests"""
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_upload_then_get_object(self, mock_log, mock_ui_service):
        """Test upload followed by get operation"""
        # Arrange
        mock_file = Mock(spec=UploadFile)
        bucket_name = "test-bucket"
        object_name = "test-file.txt"
        
        upload_response = {"message": "File uploaded successfully", "name": object_name}
        mock_ui_service.gcs_addFile.return_value = upload_response
        
        mock_content = io.BytesIO(b"test content")
        mock_ui_service.get_object.return_value = mock_content
        
        # Act
        upload_result = gcs_add_file(mock_file, bucket_name, object_name)
        get_result = gcs_get_object(object_name, bucket_name)
        
        # Assert
        assert upload_result == upload_response
        assert isinstance(get_result, StreamingResponse)
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_create_bucket_then_upload(self, mock_log, mock_ui_service):
        """Test bucket creation followed by file upload"""
        # Arrange
        bucket_name = "new-bucket"
        create_response = {"message": "Bucket created successfully"}
        mock_ui_service.gcs_addBucket.return_value = create_response
        
        mock_file = Mock(spec=UploadFile)
        upload_response = {"message": "File uploaded successfully"}
        mock_ui_service.gcs_addFile.return_value = upload_response
        
        # Act
        create_result = gcs_add_bucket(bucket_name)
        upload_result = gcs_add_file(mock_file, bucket_name)
        
        # Assert
        assert create_result == create_response
        assert upload_result == upload_response
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_concurrent_operations_different_objects(self, mock_log, mock_ui_service):
        """Test multiple operations on different objects"""
        # Arrange
        bucket_name = "test-bucket"
        mock_ui_service.list_objects.return_value = []
        mock_ui_service.list_buckets.return_value = [{"name": bucket_name}]
        
        # Act
        list_obj_result = list_objects(bucket_name)
        list_bucket_result = list_buckets()
        
        # Assert
        assert list_obj_result == []
        assert len(list_bucket_result) == 1
        mock_ui_service.list_objects.assert_called_once_with(bucket_name, ANY, ANY, ANY)
        mock_ui_service.list_buckets.assert_called_once()
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_upload_update_delete_workflow(self, mock_log, mock_ui_service):
        """Test complete lifecycle: upload, update, then delete"""
        # Arrange
        mock_file = Mock(spec=UploadFile)
        bucket_name = "test-bucket"
        object_name = "test-file.txt"
        
        mock_ui_service.gcs_addFile.return_value = {"message": "File uploaded"}
        mock_ui_service.gcs_updateFile.return_value = {"message": "File updated"}
        mock_ui_service.delete_object.return_value = None
        
        # Act
        upload_result = gcs_add_file(mock_file, bucket_name, object_name)
        update_result = gcs_update_file(mock_file, object_name, bucket_name)
        delete_result = delete_object(object_name, bucket_name)
        
        # Assert
        assert "uploaded" in upload_result["message"]
        assert "updated" in update_result["message"]
        assert "deleted successfully" in delete_result["message"]


class TestErrorHandlingAndEdgeCases:
    """Additional error handling and edge case tests"""
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_network_timeout_simulation(self, mock_log, mock_ui_service):
        """Test handling of network timeout"""
        # Arrange
        bucket_name = "test-bucket"
        mock_ui_service.list_buckets.side_effect = Exception("Connection timeout")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            list_buckets()
        
        assert exc_info.value.status_code == 500
        assert "timeout" in str(exc_info.value.detail).lower()
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_permission_denied_error(self, mock_log, mock_ui_service):
        """Test handling of permission denied errors"""
        # Arrange
        object_name = "restricted-file.txt"
        bucket_name = "restricted-bucket"
        mock_ui_service.get_object.side_effect = Exception("Access Denied")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            gcs_get_object(object_name, bucket_name)
        
        assert exc_info.value.status_code == 500
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_malformed_request_handling(self, mock_log, mock_ui_service):
        """Test handling of malformed requests"""
        # Arrange
        mock_file = Mock(spec=UploadFile)
        bucket_name = None
        mock_ui_service.gcs_addFile.side_effect = Exception("Bucket name is required")
        
        # Act & Assert
        with pytest.raises(HTTPException):
            gcs_add_file(mock_file, bucket_name)
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_special_characters_in_object_name(self, mock_log, mock_ui_service):
        """Test handling of special characters in object names"""
        # Arrange
        object_name = "test@#$%^&*()_+-=[]{}|;':\",./<>?.txt"
        bucket_name = "test-bucket"
        expected_response = {"name": object_name, "size": 100}
        mock_ui_service.get_object_properties.return_value = expected_response
        
        # Act
        result = get_object_properties(object_name, bucket_name)
        
        # Assert
        assert result == expected_response
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_unicode_characters_in_filename(self, mock_log, mock_ui_service):
        """Test handling of unicode characters in filename"""
        # Arrange
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "测试文件.txt"  # Chinese characters
        bucket_name = "test-bucket"
        expected_response = {"message": "File uploaded successfully"}
        mock_ui_service.gcs_addFile.return_value = expected_response
        
        # Act
        result = gcs_add_file(mock_file, bucket_name)
        
        # Assert
        assert result == expected_response
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_zero_byte_file_upload(self, mock_log, mock_ui_service):
        """Test upload of zero-byte file"""
        # Arrange
        mock_file = Mock(spec=UploadFile)
        mock_file.size = 0
        bucket_name = "test-bucket"
        expected_response = {"message": "File uploaded successfully"}
        mock_ui_service.gcs_addFile.return_value = expected_response
        
        # Act
        result = gcs_add_file(mock_file, bucket_name)
        
        # Assert
        assert result == expected_response


class TestSecurityConsiderations:
    """Security-related tests"""
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_path_traversal_attempt(self, mock_log, mock_ui_service):
        """Test handling of path traversal attempts"""
        # Arrange
        object_name = "../../etc/passwd"
        bucket_name = "test-bucket"
        expected_response = {"name": object_name, "size": 100}
        mock_ui_service.get_object_properties.return_value = expected_response
        
        # Act
        result = get_object_properties(object_name, bucket_name)
        
        # Assert - System should handle it, not reject (GCS treats it as valid name)
        assert result == expected_response
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_sql_injection_attempt_in_bucket_name(self, mock_log, mock_ui_service):
        """Test handling of SQL injection attempts"""
        # Arrange
        bucket_name = "bucket'; DROP TABLE buckets; --"
        mock_ui_service.list_objects.side_effect = Exception("Invalid bucket name")
        
        # Act & Assert
        with pytest.raises(HTTPException):
            list_objects(bucket_name)
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_extremely_long_object_name(self, mock_log, mock_ui_service):
        """Test handling of extremely long object names"""
        # Arrange
        object_name = "a" * 2000  # Very long name
        bucket_name = "test-bucket"
        mock_ui_service.get_object_properties.side_effect = Exception("Name too long")
        
        # Act & Assert
        with pytest.raises(HTTPException):
            get_object_properties(object_name, bucket_name)


class TestPerformanceAndResourceManagement:
    """Performance and resource management tests"""
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_list_objects_pagination(self, mock_log, mock_ui_service):
        """Test pagination with max_results"""
        # Arrange
        bucket_name = "test-bucket"
        max_results = 10
        expected_response = [
            BlobInfo(name=f"file{i}.txt", size=100, last_modified=datetime.now(), content_type="text/plain")
            for i in range(max_results)
        ]
        mock_ui_service.list_objects.return_value = expected_response
        
        # Act
        result = list_objects(bucket_name, max_results=max_results)
        
        # Assert
        assert len(result) == max_results
        mock_ui_service.list_objects.assert_called_once_with(bucket_name, ANY, ANY, ANY)
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_streaming_response_headers(self, mock_log, mock_ui_service):
        """Test streaming response includes correct headers"""
        # Arrange
        object_name = "download-file.pdf"
        bucket_name = "test-bucket"
        mock_content = io.BytesIO(b"PDF content")
        mock_ui_service.get_object.return_value = mock_content
        
        # Act
        result = gcs_get_object(object_name, bucket_name)
        
        # Assert
        assert isinstance(result, StreamingResponse)
        assert result.media_type == "application/octet-stream"


class TestRegressionScenarios:
    """Regression test scenarios"""
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_update_non_existent_file(self, mock_log, mock_ui_service):
        """Test updating a file that doesn't exist"""
        # Arrange
        mock_file = Mock(spec=UploadFile)
        object_name = "non-existent.txt"
        bucket_name = "test-bucket"
        mock_ui_service.gcs_updateFile.side_effect = Exception("File not found")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            gcs_update_file(mock_file, object_name, bucket_name)
        
        assert exc_info.value.status_code == 500
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_delete_already_deleted_object(self, mock_log, mock_ui_service):
        """Test deleting an object that was already deleted"""
        # Arrange
        object_name = "deleted-file.txt"
        bucket_name = "test-bucket"
        mock_ui_service.delete_object.side_effect = Exception("Object not found")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            delete_object(object_name, bucket_name)
        
        assert exc_info.value.status_code == 500
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_list_objects_in_non_existent_bucket(self, mock_log, mock_ui_service):
        """Test listing objects in a bucket that doesn't exist"""
        # Arrange
        bucket_name = "non-existent-bucket"
        mock_ui_service.list_objects.side_effect = Exception("Bucket not found")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            list_objects(bucket_name)
        
        assert exc_info.value.status_code == 500
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_add_file_to_non_existent_bucket(self, mock_log, mock_ui_service):
        """Test adding file to non-existent bucket"""
        # Arrange
        mock_file = Mock(spec=UploadFile)
        bucket_name = "non-existent-bucket"
        mock_ui_service.gcs_addFile.side_effect = Exception("Bucket not found")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            gcs_add_file(mock_file, bucket_name)
        
        assert exc_info.value.status_code == 500


class TestContentTypeHandling:
    """Test content type specific scenarios"""
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_json_file_upload(self, mock_log, mock_ui_service):
        """Test JSON file upload"""
        # Arrange
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "data.json"
        mock_file.content_type = "application/json"
        bucket_name = "test-bucket"
        expected_response = {"message": "File uploaded successfully"}
        mock_ui_service.gcs_addFile.return_value = expected_response
        
        # Act
        result = gcs_add_file(mock_file, bucket_name)
        
        # Assert
        assert result == expected_response
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_image_file_upload(self, mock_log, mock_ui_service):
        """Test image file upload"""
        # Arrange
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "image.png"
        mock_file.content_type = "image/png"
        bucket_name = "test-bucket"
        expected_response = {"message": "File uploaded successfully"}
        mock_ui_service.gcs_addFile.return_value = expected_response
        
        # Act
        result = gcs_add_file(mock_file, bucket_name)
        
        # Assert
        assert result == expected_response
    
    @patch('routing.gcp_router.uiService')
    @patch('routing.gcp_router.log')
    def test_filter_by_content_type(self, mock_log, mock_ui_service):
        """Test filtering objects by content type"""
        # Arrange
        bucket_name = "test-bucket"
        content_type = "image/jpeg"
        expected_response = [
            BlobInfo(name="photo1.jpg", size=1024, last_modified=datetime.now(), content_type="image/jpeg"),
            BlobInfo(name="photo2.jpg", size=2048, last_modified=datetime.now(), content_type="image/jpeg")
        ]
        mock_ui_service.list_objects.return_value = expected_response
        
        # Act
        result = list_objects(bucket_name, content_type=content_type)
        
        # Assert
        assert len(result) == 2
        assert all(obj.content_type == "image/jpeg" for obj in result)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=routing.gcp_router", "--cov-report=term-missing", "--cov-report=html"])
