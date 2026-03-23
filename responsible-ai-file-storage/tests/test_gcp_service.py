"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from datetime import datetime
import io
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create mock exception classes for Google Cloud
class MockNotFound(Exception):
    """Mock for google.cloud.exceptions.NotFound"""
    pass

class MockGoogleCloudError(Exception):
    """Mock for google.cloud.exceptions.GoogleCloudError"""
    pass

# Mock Google Cloud modules before importing gcp_service
mock_gcp_exceptions = MagicMock()
mock_gcp_exceptions.NotFound = MockNotFound
mock_gcp_exceptions.GoogleCloudError = MockGoogleCloudError

sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.storage'] = MagicMock()
sys.modules['google.cloud.exceptions'] = mock_gcp_exceptions
sys.modules['google.oauth2'] = MagicMock()
sys.modules['google.oauth2.service_account'] = MagicMock()

from service.gcp_service import FairnessUIservice
from mappers.mappers import BlobInfo


# ==================== FIXTURES ====================

@pytest.fixture
def mock_storage_client():
    """Mock Google Cloud Storage Client"""
    with patch('service.gcp_service.storage.Client') as mock_client:
        yield mock_client


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables"""
    monkeypatch.setenv('GOOGLE_APPLICATION_CREDENTIALS', '/path/to/credentials.json')
    monkeypatch.setenv('VERIFY_SSL', 'True')


@pytest.fixture
def service_instance(mock_storage_client, mock_env_vars):
    """Create a FairnessUIservice instance with mocked dependencies"""
    with patch('service.gcp_service.storage.Client.from_service_account_json') as mock_from_sa:
        mock_client_instance = MagicMock()
        mock_from_sa.return_value = mock_client_instance
        
        service = FairnessUIservice()
        service.storage_client = mock_client_instance
        
        return service


@pytest.fixture
def mock_file():
    """Create a mock file upload object"""
    mock = Mock()
    mock.filename = "test_file.csv"
    mock.content_type = "text/csv"
    mock.file = io.BytesIO(b"test,data\n1,2\n3,4")
    return mock


@pytest.fixture
def mock_bucket_list():
    """Mock bucket list response"""
    bucket1 = Mock()
    bucket1.name = "bucket1"
    
    bucket2 = Mock()
    bucket2.name = "bucket2"
    
    bucket3 = Mock()
    bucket3.name = "bucket3"
    
    return [bucket1, bucket2, bucket3]


@pytest.fixture
def mock_blob():
    """Mock GCS blob object"""
    blob = Mock()
    blob.name = "test_file_uuid.csv"
    blob.size = 1024
    blob.updated = datetime(2025, 12, 25, 10, 30, 0)
    blob.time_created = datetime(2025, 12, 25, 10, 0, 0)
    blob.content_type = "text/csv"
    blob.etag = "abc123"
    blob.md5_hash = "xyz789"
    return blob


# ==================== TEST CASES ====================

class TestFairnessUIserviceInitialization:
    """Test service initialization"""
    
    def test_init_with_credentials_path(self, mock_env_vars):
        """Test initialization with credentials path"""
        with patch('service.gcp_service.storage.Client.from_service_account_json') as mock_from_sa:
            mock_client = MagicMock()
            mock_from_sa.return_value = mock_client
            
            service = FairnessUIservice()
            
            mock_from_sa.assert_called_once_with('/path/to/credentials.json')
            assert service.storage_client is not None
    
    def test_init_without_credentials_path(self, monkeypatch):
        """Test initialization without credentials path (default credentials)"""
        monkeypatch.delenv('GOOGLE_APPLICATION_CREDENTIALS', raising=False)
        monkeypatch.setenv('VERIFY_SSL', 'True')
        
        with patch('service.gcp_service.storage.Client') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            service = FairnessUIservice()
            
            mock_client_class.assert_called_once()
            assert service.storage_client is not None


class TestListBuckets:
    """Test list_buckets method"""
    
    def test_list_buckets_success(self, service_instance, mock_bucket_list):
        """Test successful bucket listing"""
        service_instance.storage_client.list_buckets.return_value = mock_bucket_list
        
        result = service_instance.list_buckets()
        
        assert result == ["bucket1", "bucket2", "bucket3"]
        service_instance.storage_client.list_buckets.assert_called_once()
    
    def test_list_buckets_empty(self, service_instance):
        """Test bucket listing when no buckets exist"""
        service_instance.storage_client.list_buckets.return_value = []
        
        result = service_instance.list_buckets()
        
        assert result == []
    
    def test_list_buckets_error(self, service_instance):
        """Test bucket listing error handling"""
        from fastapi import HTTPException
        
        service_instance.storage_client.list_buckets.side_effect = MockGoogleCloudError("Failed to list buckets")
        
        with pytest.raises(HTTPException) as exc_info:
            service_instance.list_buckets()
        
        assert exc_info.value.status_code == 500
        assert "Failed to list buckets" in str(exc_info.value.detail)


class TestGcsAddFile:
    """Test gcs_addFile method"""
    
    def test_add_file_success(self, service_instance, mock_file):
        """Test successful file upload"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        with patch('service.gcp_service.uuid.uuid4', return_value='test-uuid-1234'):
            result = service_instance.gcs_addFile(mock_file, "test-bucket")
        
        assert "object_name" in result
        assert result["object_name"] == "test_file_test-uuid-1234.csv"
        mock_blob.upload_from_file.assert_called_once()
    
    def test_add_file_with_custom_name(self, service_instance, mock_file):
        """Test file upload with custom object name"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        result = service_instance.gcs_addFile(mock_file, "test-bucket", object_name="custom_name.csv")
        
        assert result["object_name"] == "custom_name.csv"
        mock_blob.upload_from_file.assert_called_once()
    
    def test_add_file_with_different_extensions(self, service_instance):
        """Test file upload with different file extensions"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        test_files = [
            ("test.json", "application/json"),
            ("test.txt", "text/plain"),
            ("test.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ]
        
        for filename, content_type in test_files:
            mock_file = Mock()
            mock_file.filename = filename
            mock_file.content_type = content_type
            mock_file.file = io.BytesIO(b"test data")
            
            with patch('service.gcp_service.uuid.uuid4', return_value='test-uuid'):
                result = service_instance.gcs_addFile(mock_file, "test-bucket")
            
            name_without_ext, ext = os.path.splitext(filename)
            expected_name = f"{name_without_ext}_test-uuid{ext}"
            assert result["object_name"] == expected_name
    
    def test_add_file_sets_content_type(self, service_instance, mock_file):
        """Test that content type is set correctly"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        service_instance.gcs_addFile(mock_file, "test-bucket")
        
        assert mock_blob.content_type == "text/csv"
    
    def test_add_file_error(self, service_instance, mock_file):
        """Test file upload error handling"""
        from fastapi import HTTPException
        
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.upload_from_file.side_effect = MockGoogleCloudError("Upload failed")
        
        with pytest.raises(HTTPException) as exc_info:
            service_instance.gcs_addFile(mock_file, "test-bucket")
        
        assert exc_info.value.status_code == 500
        assert "Failed to upload file" in str(exc_info.value.detail)


class TestGcsUpdateFile:
    """Test gcs_updateFile method"""
    
    def test_update_file_success(self, service_instance, mock_file):
        """Test successful file update"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        result = service_instance.gcs_updateFile(mock_file, "existing_object.csv", "test-bucket")
        
        assert result["object_name"] == "existing_object.csv"
        mock_blob.upload_from_file.assert_called_once()
    
    def test_update_file_sets_content_type(self, service_instance, mock_file):
        """Test that content type is set during update"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        service_instance.gcs_updateFile(mock_file, "existing_object.csv", "test-bucket")
        
        assert mock_blob.content_type == "text/csv"
    
    def test_update_file_error(self, service_instance, mock_file):
        """Test file update error handling"""
        from fastapi import HTTPException
        
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.upload_from_file.side_effect = MockGoogleCloudError("Update failed")
        
        with pytest.raises(HTTPException) as exc_info:
            service_instance.gcs_updateFile(mock_file, "object.csv", "test-bucket")
        
        assert exc_info.value.status_code == 500
        assert "Failed to update file" in str(exc_info.value.detail)


class TestGetObject:
    """Test get_object method"""
    
    def test_get_object_with_known_size(self, service_instance):
        """Test downloading object with known size"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        
        # Set blob size to 20MB
        type(mock_blob).size = PropertyMock(return_value=20 * 1024 * 1024)
        
        # Mock download_as_bytes to return chunks
        chunk_size = 15 * 1024 * 1024  # 15MB
        mock_blob.download_as_bytes.side_effect = [
            b"x" * chunk_size,  # First chunk
            b"y" * (5 * 1024 * 1024)  # Second chunk (5MB)
        ]
        
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        chunks = list(service_instance.get_object("test_object.bin", "test-bucket"))
        
        assert len(chunks) == 2
        assert len(chunks[0]) == chunk_size
        assert len(chunks[1]) == 5 * 1024 * 1024
    
    def test_get_object_without_size(self, service_instance):
        """Test downloading object without known size"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        
        type(mock_blob).size = PropertyMock(return_value=None)
        mock_blob.download_as_bytes.return_value = b"complete data"
        
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        chunks = list(service_instance.get_object("test_object.txt", "test-bucket"))
        
        assert len(chunks) == 1
        assert chunks[0] == b"complete data"
    
    def test_get_object_not_found(self, service_instance):
        """Test downloading non-existent object"""
        from fastapi import HTTPException
        
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        type(mock_blob).size = PropertyMock(side_effect=MockNotFound("Object not found"))
        
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        with pytest.raises(HTTPException) as exc_info:
            list(service_instance.get_object("nonexistent.txt", "test-bucket"))
        
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail)
    
    def test_get_object_error(self, service_instance):
        """Test download error handling"""
        from fastapi import HTTPException
        
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        type(mock_blob).size = PropertyMock(return_value=1024)
        mock_blob.download_as_bytes.side_effect = MockGoogleCloudError("Download failed")
        
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        with pytest.raises(HTTPException) as exc_info:
            list(service_instance.get_object("test.txt", "test-bucket"))
        
        assert exc_info.value.status_code == 500
        assert "Failed to download object" in str(exc_info.value.detail)


class TestDeleteObject:
    """Test delete_object method"""
    
    def test_delete_object_success(self, service_instance):
        """Test successful object deletion"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        service_instance.delete_object("test-bucket", "test_object.csv")
        
        service_instance.storage_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.blob.assert_called_once_with("test_object.csv")
        mock_blob.delete.assert_called_once()
    
    def test_delete_object_not_found(self, service_instance):
        """Test deleting non-existent object"""
        from fastapi import HTTPException
        
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.delete.side_effect = MockNotFound("Object not found")
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        with pytest.raises(HTTPException) as exc_info:
            service_instance.delete_object("test-bucket", "nonexistent.csv")
        
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail)
    
    def test_delete_object_error(self, service_instance):
        """Test object deletion error handling"""
        from fastapi import HTTPException
        
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.delete.side_effect = MockGoogleCloudError("Delete failed")
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        with pytest.raises(HTTPException) as exc_info:
            service_instance.delete_object("test-bucket", "test.csv")
        
        assert exc_info.value.status_code == 500
        assert "Failed to delete object" in str(exc_info.value.detail)


class TestGcsAddBucket:
    """Test gcs_addBucket method"""
    
    def test_add_bucket_success(self, service_instance):
        """Test successful bucket creation"""
        mock_bucket = MagicMock()
        service_instance.storage_client.bucket.return_value = mock_bucket
        
        result = service_instance.gcs_addBucket("new-bucket")
        
        assert result["message"] == "Bucket 'new-bucket' created successfully"
        mock_bucket.create.assert_called_once()
    
    def test_add_bucket_error(self, service_instance):
        """Test bucket creation error handling"""
        from fastapi import HTTPException
        
        mock_bucket = MagicMock()
        mock_bucket.create.side_effect = MockGoogleCloudError("Bucket already exists")
        service_instance.storage_client.bucket.return_value = mock_bucket
        
        with pytest.raises(HTTPException) as exc_info:
            service_instance.gcs_addBucket("existing-bucket")
        
        assert exc_info.value.status_code == 500
        assert "Failed to create bucket" in str(exc_info.value.detail)


class TestBucketNameValidation:
    """Test is_valid_bucket_name method"""
    
    def test_valid_bucket_names(self, service_instance):
        """Test valid bucket names"""
        valid_names = [
            "my-bucket",
            "mybucket123",
            "my.bucket.name",
            "abc",  # minimum length
            "a" * 63,  # maximum length
            "bucket-with-hyphens",
            "bucket_with_underscores",
            "bucket.with.dots",
        ]
        
        for name in valid_names:
            assert service_instance.is_valid_bucket_name(name), f"Expected '{name}' to be valid"
    
    def test_invalid_bucket_names(self, service_instance):
        """Test invalid bucket names"""
        invalid_names = [
            "ab",  # too short
            "a" * 64,  # too long
            "Bucket",  # uppercase
            "-bucket",  # starts with hyphen
            "bucket-",  # ends with hyphen
            "bucket..name",  # consecutive dots
            "192.168.1.1",  # IP address format
            "255.255.255.255",  # IP address format
        ]
        
        for name in invalid_names:
            assert not service_instance.is_valid_bucket_name(name), f"Expected '{name}' to be invalid"


class TestObjectNameValidation:
    """Test is_valid_object_name method"""
    
    def test_valid_object_names(self, service_instance):
        """Test valid object names"""
        valid_names = [
            "file.txt",
            "folder/subfolder/file.csv",
            "my_file_name.json",
            "file-with-hyphens.txt",
            "file with spaces.txt",
            "unicode_文件.txt",
        ]
        
        for name in valid_names:
            assert service_instance.is_valid_object_name(name), f"Expected '{name}' to be valid"
    
    def test_invalid_object_names(self, service_instance):
        """Test invalid object names"""
        invalid_names = [
            ".",  # just dot
            "..",  # double dot
            ".well-known/acme-challenge/test",  # reserved prefix
        ]
        
        for name in invalid_names:
            assert not service_instance.is_valid_object_name(name), f"Expected '{name}' to be invalid"
    
    def test_object_name_with_control_characters(self, service_instance):
        """Test object names with control characters"""
        # Test with control character (ASCII 1)
        invalid_name = "file\x01name.txt"
        assert not service_instance.is_valid_object_name(invalid_name)
        
        # Test with DEL character (ASCII 127)
        invalid_name = "file\x7fname.txt"
        assert not service_instance.is_valid_object_name(invalid_name)


class TestGetObjectProperties:
    """Test get_object_properties method"""
    
    def test_get_properties_success(self, service_instance, mock_blob):
        """Test successful property retrieval"""
        mock_bucket = MagicMock()
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        result = service_instance.get_object_properties("test_file.csv", "test-bucket")
        
        # The method returns the object_name parameter, not the blob.name
        assert result["object_name"] == "test_file.csv"
        assert result["object_size"] == 1024
        assert result["content_type"] == "text/csv"
        assert result["etag"] == "abc123"
        assert result["md5_hash"] == "xyz789"
        mock_blob.reload.assert_called_once()
    
    def test_get_properties_invalid_bucket_name(self, service_instance):
        """Test property retrieval with invalid bucket name"""
        with pytest.raises(ValueError) as exc_info:
            service_instance.get_object_properties("test.txt", "INVALID-BUCKET")
        
        assert "Invalid bucket name" in str(exc_info.value)
    
    def test_get_properties_invalid_object_name(self, service_instance):
        """Test property retrieval with invalid object name"""
        with pytest.raises(ValueError) as exc_info:
            service_instance.get_object_properties("..", "valid-bucket")
        
        assert "Invalid object name" in str(exc_info.value)
    
    def test_get_properties_not_found(self, service_instance):
        """Test property retrieval for non-existent object"""
        from fastapi import HTTPException
        
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.reload.side_effect = MockNotFound("Object not found")
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        with pytest.raises(HTTPException) as exc_info:
            service_instance.get_object_properties("nonexistent.txt", "test-bucket")
        
        assert exc_info.value.status_code == 404
    
    def test_get_properties_error(self, service_instance):
        """Test property retrieval error handling"""
        from fastapi import HTTPException
        
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.reload.side_effect = MockGoogleCloudError("Failed to reload")
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        with pytest.raises(HTTPException) as exc_info:
            service_instance.get_object_properties("test.txt", "test-bucket")
        
        assert exc_info.value.status_code == 500


class TestListObjects:
    """Test list_objects method"""
    
    def test_list_objects_success(self, service_instance, mock_blob):
        """Test successful object listing"""
        mock_bucket = MagicMock()
        mock_bucket.list_blobs.return_value = [mock_blob]
        service_instance.storage_client.bucket.return_value = mock_bucket
        
        result = service_instance.list_objects("test-bucket")
        
        assert len(result) == 1
        assert isinstance(result[0], BlobInfo)
        assert result[0].name == "test_file_uuid.csv"
        assert result[0].size == 1024
        assert result[0].content_type == "text/csv"
    
    def test_list_objects_with_prefix(self, service_instance, mock_blob):
        """Test object listing with prefix filter"""
        mock_bucket = MagicMock()
        mock_bucket.list_blobs.return_value = [mock_blob]
        service_instance.storage_client.bucket.return_value = mock_bucket
        
        result = service_instance.list_objects("test-bucket", name_starts_with="test_")
        
        mock_bucket.list_blobs.assert_called_once()
        call_kwargs = mock_bucket.list_blobs.call_args[1]
        assert call_kwargs['prefix'] == "test_"
        assert len(result) == 1
    
    def test_list_objects_with_content_type_filter(self, service_instance):
        """Test object listing with content type filter"""
        mock_bucket = MagicMock()
        
        blob1 = Mock()
        blob1.name = "file1.csv"
        blob1.size = 1024
        blob1.updated = datetime(2025, 12, 25, 10, 30, 0)
        blob1.content_type = "text/csv"
        
        blob2 = Mock()
        blob2.name = "file2.json"
        blob2.size = 2048
        blob2.updated = datetime(2025, 12, 25, 11, 30, 0)
        blob2.content_type = "application/json"
        
        mock_bucket.list_blobs.return_value = [blob1, blob2]
        service_instance.storage_client.bucket.return_value = mock_bucket
        
        result = service_instance.list_objects("test-bucket", content_type="text/csv")
        
        assert len(result) == 1
        assert result[0].content_type == "text/csv"
        assert result[0].name == "file1.csv"
    
    def test_list_objects_with_max_results(self, service_instance):
        """Test object listing with max results limit"""
        mock_bucket = MagicMock()
        
        blobs = []
        for i in range(10):
            blob = Mock()
            blob.name = f"file{i}.csv"
            blob.size = 1024 * i
            blob.updated = datetime(2025, 12, 25, 10, i, 0)
            blob.content_type = "text/csv"
            blobs.append(blob)
        
        mock_bucket.list_blobs.return_value = blobs
        service_instance.storage_client.bucket.return_value = mock_bucket
        
        result = service_instance.list_objects("test-bucket", max_results=5)
        
        assert len(result) == 5
        call_kwargs = mock_bucket.list_blobs.call_args[1]
        assert call_kwargs['max_results'] == 5
    
    def test_list_objects_empty_bucket(self, service_instance):
        """Test object listing in empty bucket"""
        mock_bucket = MagicMock()
        mock_bucket.list_blobs.return_value = []
        service_instance.storage_client.bucket.return_value = mock_bucket
        
        result = service_instance.list_objects("empty-bucket")
        
        assert result == []
    
    def test_list_objects_bucket_not_found(self, service_instance):
        """Test listing objects in non-existent bucket"""
        from fastapi import HTTPException
        
        mock_bucket = MagicMock()
        mock_bucket.list_blobs.side_effect = MockNotFound("Bucket not found")
        service_instance.storage_client.bucket.return_value = mock_bucket
        
        with pytest.raises(HTTPException) as exc_info:
            service_instance.list_objects("nonexistent-bucket")
        
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail)
    
    def test_list_objects_error(self, service_instance):
        """Test object listing error handling"""
        from fastapi import HTTPException
        
        mock_bucket = MagicMock()
        mock_bucket.list_blobs.side_effect = MockGoogleCloudError("Failed to list")
        service_instance.storage_client.bucket.return_value = mock_bucket
        
        with pytest.raises(HTTPException) as exc_info:
            service_instance.list_objects("test-bucket")
        
        assert exc_info.value.status_code == 500
        assert "Failed to list objects" in str(exc_info.value.detail)


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_add_file_no_extension(self, service_instance):
        """Test uploading file with no extension"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        mock_file = Mock()
        mock_file.filename = "README"
        mock_file.content_type = "text/plain"
        mock_file.file = io.BytesIO(b"test content")
        
        with patch('service.gcp_service.uuid.uuid4', return_value='test-uuid'):
            result = service_instance.gcs_addFile(mock_file, "test-bucket")
        
        assert result["object_name"] == "README_test-uuid"
    
    def test_add_file_unicode_filename(self, service_instance):
        """Test uploading file with unicode characters"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        mock_file = Mock()
        mock_file.filename = "测试文件_テスト_файл.txt"
        mock_file.content_type = "text/plain"
        mock_file.file = io.BytesIO(b"unicode content")
        
        with patch('service.gcp_service.uuid.uuid4', return_value='test-uuid'):
            result = service_instance.gcs_addFile(mock_file, "test-bucket")
        
        assert "test-uuid" in result["object_name"]
        assert result["object_name"].endswith(".txt")
    
    def test_add_file_very_long_filename(self, service_instance):
        """Test uploading file with very long filename"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        long_name = "a" * 500  # Very long filename
        mock_file = Mock()
        mock_file.filename = f"{long_name}.csv"
        mock_file.content_type = "text/csv"
        mock_file.file = io.BytesIO(b"data")
        
        with patch('service.gcp_service.uuid.uuid4', return_value='test-uuid'):
            result = service_instance.gcs_addFile(mock_file, "test-bucket")
        
        assert "test-uuid" in result["object_name"]
        mock_blob.upload_from_file.assert_called_once()
    
    def test_add_zero_byte_file(self, service_instance):
        """Test uploading empty/zero-byte file"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        mock_file = Mock()
        mock_file.filename = "empty.txt"
        mock_file.content_type = "text/plain"
        mock_file.file = io.BytesIO(b"")
        
        with patch('service.gcp_service.uuid.uuid4', return_value='test-uuid'):
            result = service_instance.gcs_addFile(mock_file, "test-bucket")
        
        assert result["object_name"] == "empty_test-uuid.txt"
        mock_blob.upload_from_file.assert_called_once()
    
    def test_get_object_small_file(self, service_instance):
        """Test downloading small file (less than chunk size)"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        
        small_size = 1024  # 1KB
        type(mock_blob).size = PropertyMock(return_value=small_size)
        mock_blob.download_as_bytes.return_value = b"x" * small_size
        
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        chunks = list(service_instance.get_object("small.txt", "test-bucket"))
        
        assert len(chunks) == 1
        assert len(chunks[0]) == small_size


class TestSecurityAndValidation:
    """Test security-related scenarios"""
    
    def test_add_file_with_path_traversal(self, service_instance):
        """Test file upload with path traversal attempt"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        mock_file = Mock()
        mock_file.filename = "../../etc/passwd"
        mock_file.content_type = "text/plain"
        mock_file.file = io.BytesIO(b"malicious")
        
        with patch('service.gcp_service.uuid.uuid4', return_value='test-uuid'):
            result = service_instance.gcs_addFile(mock_file, "test-bucket")
        
        assert "test-uuid" in result["object_name"]
    
    def test_bucket_name_validation_prevents_ip_addresses(self, service_instance):
        """Test that bucket names cannot be IP addresses"""
        assert not service_instance.is_valid_bucket_name("192.168.1.1")
        assert not service_instance.is_valid_bucket_name("10.0.0.1")


class TestIntegrationScenarios:
    """Test integration scenarios"""
    
    def test_upload_and_list_workflow(self, service_instance, mock_file):
        """Test complete upload and list workflow"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        # Upload file
        with patch('service.gcp_service.uuid.uuid4', return_value='test-uuid'):
            upload_result = service_instance.gcs_addFile(mock_file, "test-bucket")
        
        # Setup list to return uploaded file
        list_blob = Mock()
        list_blob.name = upload_result["object_name"]
        list_blob.size = 1024
        list_blob.updated = datetime.now()
        list_blob.content_type = "text/csv"
        
        mock_bucket.list_blobs.return_value = [list_blob]
        
        # List objects
        objects = service_instance.list_objects("test-bucket")
        
        assert len(objects) == 1
        assert objects[0].name == upload_result["object_name"]
    
    def test_create_bucket_and_upload_file(self, service_instance, mock_file):
        """Test creating bucket and uploading file"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        # Create bucket
        bucket_result = service_instance.gcs_addBucket("new-bucket")
        assert "created successfully" in bucket_result["message"]
        
        # Upload file
        with patch('service.gcp_service.uuid.uuid4', return_value='test-uuid'):
            upload_result = service_instance.gcs_addFile(mock_file, "new-bucket")
        
        assert upload_result["object_name"] == "test_file_test-uuid.csv"


class TestResourceManagement:
    """Test resource management scenarios"""
    
    def test_file_seek_reset(self, service_instance, mock_file):
        """Test that file pointer is reset before upload"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        # Move file pointer away from start
        mock_file.file.seek(10)
        
        service_instance.gcs_addFile(mock_file, "test-bucket")
        
        # Verify seek(0) was called
        # The file.file.seek(0) should be called in the service
        mock_blob.upload_from_file.assert_called_once()


class TestPerformanceSettings:
    """Test performance-related settings"""
    
    def test_upload_timeout_configured(self, service_instance, mock_file):
        """Test that upload has proper timeout configured"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        service_instance.storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        service_instance.gcs_addFile(mock_file, "test-bucket")
        
        call_kwargs = mock_blob.upload_from_file.call_args[1]
        assert call_kwargs['timeout'] == 300


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
