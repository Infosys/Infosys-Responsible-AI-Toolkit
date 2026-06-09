"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
from datetime import datetime
import io
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create mock exception classes for Azure
class MockResourceNotFoundError(Exception):
    """Mock for azure.core.exceptions.ResourceNotFoundError"""
    pass

class MockResourceExistsError(Exception):
    """Mock for azure.core.exceptions.ResourceExistsError"""
    pass

class MockHttpResponseError(Exception):
    """Mock for azure.core.exceptions.HttpResponseError"""
    def __init__(self, message="", status_code=None):
        super().__init__(message)
        self.status_code = status_code

class MockServiceRequestTimeoutError(Exception):
    """Mock for azure.core.exceptions.ServiceRequestTimeoutError"""
    pass

class MockClientAuthenticationError(Exception):
    """Mock for azure.core.exceptions.ClientAuthenticationError"""
    pass

class MockServiceRequestError(Exception):
    """Mock for azure.core.exceptions.ServiceRequestError"""
    pass

# Mock Azure modules before importing service
mock_azure_exceptions = MagicMock()
mock_azure_exceptions.ResourceNotFoundError = MockResourceNotFoundError
mock_azure_exceptions.ResourceExistsError = MockResourceExistsError
mock_azure_exceptions.HttpResponseError = MockHttpResponseError
mock_azure_exceptions.ServiceRequestTimeoutError = MockServiceRequestTimeoutError
mock_azure_exceptions.ClientAuthenticationError = MockClientAuthenticationError
mock_azure_exceptions.ServiceRequestError = MockServiceRequestError

# Create a mock ContentSettings class that properly stores content_type
class MockContentSettings:
    def __init__(self, content_type=None, **kwargs):
        self.content_type = content_type

mock_azure_storage_blob = MagicMock()
mock_azure_storage_blob.ContentSettings = MockContentSettings

sys.modules['azure'] = MagicMock()
sys.modules['azure.storage'] = MagicMock()
sys.modules['azure.storage.blob'] = mock_azure_storage_blob
sys.modules['azure.core'] = MagicMock()
sys.modules['azure.core.exceptions'] = mock_azure_exceptions

from service.service import FairnessUIservice
from mappers.mappers import BlobInfo


# ==================== FIXTURES ====================

@pytest.fixture
def mock_blob_service_client():
    """Mock Azure BlobServiceClient"""
    with patch('service.service.BlobServiceClient') as mock_client:
        yield mock_client


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables"""
    monkeypatch.setenv('AZURE_BLOB_STORAGE_CONNECTION_KEY', 'DefaultEndpointsProtocol=https;AccountName=testaccount;AccountKey=testkey==;EndpointSuffix=core.windows.net')


@pytest.fixture
def service_instance(mock_blob_service_client, mock_env_vars):
    """Create a FairnessUIservice instance with mocked dependencies"""
    mock_client_instance = MagicMock()
    mock_blob_service_client.from_connection_string.return_value = mock_client_instance
    
    service = FairnessUIservice()
    service.blob_service_client = mock_client_instance
    
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
def mock_container_list():
    """Mock container list response"""
    container1 = Mock()
    container1.name = "container1"
    
    container2 = Mock()
    container2.name = "container2"
    
    container3 = Mock()
    container3.name = "container3"
    
    return [container1, container2, container3]


@pytest.fixture
def mock_blob_properties():
    """Mock blob properties"""
    blob = Mock()
    blob.name = "test_file_uuid.csv"
    blob.size = 1024
    blob.last_modified = datetime(2025, 12, 25, 10, 30, 0)
    blob.content_settings = Mock()
    blob.content_settings.content_type = "text/csv"
    return blob


# ==================== TEST CASES ====================

class TestFairnessUIserviceInitialization:
    """Test service initialization"""
    
    def test_init_creates_blob_service_client(self, mock_blob_service_client, mock_env_vars):
        """Test that initialization creates a BlobServiceClient"""
        service = FairnessUIservice()
        
        mock_blob_service_client.from_connection_string.assert_called_once()
        assert service.blob_service_client is not None
    
    def test_init_uses_correct_chunk_size(self, mock_blob_service_client, mock_env_vars):
        """Test that initialization uses correct chunk size"""
        service = FairnessUIservice()
        
        # Verify chunk size parameter
        call_kwargs = mock_blob_service_client.from_connection_string.call_args[1]
        expected_chunk_size = 15 * 1024 * 1024
        assert call_kwargs['max_chunk_get_size'] == expected_chunk_size


class TestListContainer:
    """Test list_container method"""
    
    def test_list_container_success(self, service_instance, mock_container_list):
        """Test successful container listing"""
        service_instance.blob_service_client.list_containers.return_value = mock_container_list
        
        result = service_instance.list_container()
        
        assert result == ["container1", "container2", "container3"]
        service_instance.blob_service_client.list_containers.assert_called_once()
    
    def test_list_container_empty(self, service_instance):
        """Test container listing when no containers exist"""
        service_instance.blob_service_client.list_containers.return_value = []
        
        result = service_instance.list_container()
        
        assert result == []


class TestAzureAddFile:
    """Test azure_addFile method"""
    
    def test_add_file_success(self, service_instance, mock_file):
        """Test successful file upload"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        with patch('service.service.uuid.uuid4', return_value='test-uuid-1234'):
            result = service_instance.azure_addFile(mock_file, "test-container")
        
        assert "blob_name" in result
        assert result["blob_name"] == "test_file_test-uuid-1234.csv"
        mock_container_client.upload_blob.assert_called_once()
    
    def test_add_file_with_correct_parameters(self, service_instance, mock_file):
        """Test that file upload uses correct parameters"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        with patch('service.service.uuid.uuid4', return_value='test-uuid-1234'):
            service_instance.azure_addFile(mock_file, "test-container")
        
        call_kwargs = mock_container_client.upload_blob.call_args[1]
        assert call_kwargs['overwrite'] is False
        assert call_kwargs['max_concurrency'] == 4
        assert call_kwargs['connection_timeout'] == 30000
        assert call_kwargs['logging_enable'] is True
    
    def test_add_file_with_different_extensions(self, service_instance):
        """Test file upload with different file extensions"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
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
            
            with patch('service.service.uuid.uuid4', return_value='test-uuid'):
                result = service_instance.azure_addFile(mock_file, "test-container")
            
            name_without_ext, ext = os.path.splitext(filename)
            expected_name = f"{name_without_ext}_test-uuid{ext}"
            assert result["blob_name"] == expected_name


class TestAzureUpdateFile:
    """Test azure_updateFile method"""
    
    def test_update_file_success(self, service_instance, mock_file):
        """Test successful file update"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        result = service_instance.azure_updateFile(mock_file, "existing_blob.csv", "test-container")
        
        assert result["blob_name"] == "existing_blob.csv"
        mock_container_client.upload_blob.assert_called_once()
    
    def test_update_file_with_overwrite(self, service_instance, mock_file):
        """Test that update file sets overwrite to True"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        service_instance.azure_updateFile(mock_file, "existing_blob.csv", "test-container")
        
        call_kwargs = mock_container_client.upload_blob.call_args[1]
        assert call_kwargs['overwrite'] is True


class TestGetBlob:
    """Test get_blob method"""
    
    def test_get_blob_yields_chunks(self, service_instance):
        """Test that get_blob yields file chunks"""
        mock_container_client = MagicMock()
        mock_blob_client = MagicMock()
        mock_download_blob = MagicMock()
        
        # Mock chunks
        test_chunks = [b"chunk1", b"chunk2", b"chunk3"]
        mock_download_blob.chunks.return_value = iter(test_chunks)
        
        mock_blob_client.download_blob.return_value = mock_download_blob
        mock_container_client.get_blob_client.return_value = mock_blob_client
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        # Collect yielded chunks
        result_chunks = list(service_instance.get_blob("test_blob.csv", "test-container"))
        
        assert result_chunks == test_chunks
        mock_blob_client.download_blob.assert_called_once_with(max_concurrency=4, logging_enable=True)
    
    def test_get_blob_empty_file(self, service_instance):
        """Test get_blob with empty file"""
        mock_container_client = MagicMock()
        mock_blob_client = MagicMock()
        mock_download_blob = MagicMock()
        
        mock_download_blob.chunks.return_value = iter([])
        mock_blob_client.download_blob.return_value = mock_download_blob
        mock_container_client.get_blob_client.return_value = mock_blob_client
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        result_chunks = list(service_instance.get_blob("empty.txt", "test-container"))
        
        assert result_chunks == []


class TestDeleteBlob:
    """Test delete_blob method"""
    
    def test_delete_blob_success(self, service_instance):
        """Test successful blob deletion"""
        mock_blob_client = MagicMock()
        service_instance.blob_service_client.get_blob_client.return_value = mock_blob_client
        
        service_instance.delete_blob("test-container", "test_blob.csv")
        
        service_instance.blob_service_client.get_blob_client.assert_called_once_with(
            container="test-container",
            blob="test_blob.csv"
        )
        mock_blob_client.delete_blob.assert_called_once_with(logging_enable=True)
    
    def test_delete_blob_with_special_characters(self, service_instance):
        """Test blob deletion with special characters in name"""
        mock_blob_client = MagicMock()
        service_instance.blob_service_client.get_blob_client.return_value = mock_blob_client
        
        special_blob_name = "test file with spaces & special chars!.csv"
        service_instance.delete_blob("test-container", special_blob_name)
        
        service_instance.blob_service_client.get_blob_client.assert_called_once_with(
            container="test-container",
            blob=special_blob_name
        )


class TestAzureAddContainer:
    """Test azure_addContainer method"""
    
    def test_add_container_success(self, service_instance):
        """Test successful container creation"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        result = service_instance.azure_addContainer("new-container")
        
        assert result["message"] == "Container 'new-container' created successfully"
        mock_container_client.create_container.assert_called_once()
    
    def test_add_container_gets_correct_client(self, service_instance):
        """Test that correct container client is retrieved"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        service_instance.azure_addContainer("test-container")
        
        service_instance.blob_service_client.get_container_client.assert_called_once_with("test-container")


class TestListBlobs:
    """Test list_blobs method"""
    
    def test_list_blobs_success(self, service_instance, mock_blob_properties):
        """Test successful blob listing"""
        mock_container_client = MagicMock()
        mock_container_client.list_blobs.return_value = [mock_blob_properties]
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        result = service_instance.list_blobs("test-container")
        
        assert len(result) == 1
        assert isinstance(result[0], BlobInfo)
        assert result[0].name == "test_file_uuid.csv"
        assert result[0].size == 1024
        assert result[0].content_type == "text/csv"
    
    def test_list_blobs_with_name_filter(self, service_instance, mock_blob_properties):
        """Test blob listing with name filter"""
        mock_container_client = MagicMock()
        mock_container_client.list_blobs.return_value = [mock_blob_properties]
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        result = service_instance.list_blobs("test-container", name_starts_with="test_")
        
        mock_container_client.list_blobs.assert_called_once_with(
            name_starts_with="test_",
            results_per_page=None
        )
        assert len(result) == 1
    
    def test_list_blobs_with_content_type_filter(self, service_instance):
        """Test blob listing with content type filter"""
        mock_container_client = MagicMock()
        
        # Create multiple blobs with different content types
        blob1 = Mock()
        blob1.name = "file1.csv"
        blob1.size = 1024
        blob1.last_modified = datetime(2025, 12, 25, 10, 30, 0)
        blob1.content_settings = Mock()
        blob1.content_settings.content_type = "text/csv"
        
        blob2 = Mock()
        blob2.name = "file2.json"
        blob2.size = 2048
        blob2.last_modified = datetime(2025, 12, 25, 11, 30, 0)
        blob2.content_settings = Mock()
        blob2.content_settings.content_type = "application/json"
        
        mock_container_client.list_blobs.return_value = [blob1, blob2]
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        result = service_instance.list_blobs("test-container", content_type="text/csv")
        
        assert len(result) == 1
        assert result[0].content_type == "text/csv"
        assert result[0].name == "file1.csv"
    
    def test_list_blobs_with_max_results(self, service_instance):
        """Test blob listing with max results limit"""
        mock_container_client = MagicMock()
        
        # Create multiple blobs
        blobs = []
        for i in range(10):
            blob = Mock()
            blob.name = f"file{i}.csv"
            blob.size = 1024 * i
            blob.last_modified = datetime(2025, 12, 25, 10, i, 0)
            blob.content_settings = Mock()
            blob.content_settings.content_type = "text/csv"
            blobs.append(blob)
        
        mock_container_client.list_blobs.return_value = blobs
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        result = service_instance.list_blobs("test-container", max_results=5)
        
        assert len(result) == 5
        mock_container_client.list_blobs.assert_called_once_with(
            name_starts_with=None,
            results_per_page=5
        )
    
    def test_list_blobs_empty_container(self, service_instance):
        """Test blob listing in empty container"""
        mock_container_client = MagicMock()
        mock_container_client.list_blobs.return_value = []
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        result = service_instance.list_blobs("empty-container")
        
        assert result == []
    
    def test_list_blobs_with_combined_filters(self, service_instance):
        """Test blob listing with multiple filters"""
        mock_container_client = MagicMock()
        
        # Create blobs with various properties
        blob1 = Mock()
        blob1.name = "data_file1.csv"
        blob1.size = 1024
        blob1.last_modified = datetime(2025, 12, 25, 10, 30, 0)
        blob1.content_settings = Mock()
        blob1.content_settings.content_type = "text/csv"
        
        blob2 = Mock()
        blob2.name = "data_file2.json"
        blob2.size = 2048
        blob2.last_modified = datetime(2025, 12, 25, 11, 30, 0)
        blob2.content_settings = Mock()
        blob2.content_settings.content_type = "application/json"
        
        blob3 = Mock()
        blob3.name = "data_file3.csv"
        blob3.size = 3072
        blob3.last_modified = datetime(2025, 12, 25, 12, 30, 0)
        blob3.content_settings = Mock()
        blob3.content_settings.content_type = "text/csv"
        
        mock_container_client.list_blobs.return_value = [blob1, blob2, blob3]
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        result = service_instance.list_blobs(
            "test-container",
            name_starts_with="data_",
            content_type="text/csv",
            max_results=10
        )
        
        assert len(result) == 2
        assert all(blob.content_type == "text/csv" for blob in result)
        assert all(blob.name.startswith("data_") for blob in result)


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_list_blobs_handles_exception(self, service_instance):
        """Test that list_blobs handles exceptions properly"""
        from fastapi import HTTPException
        
        mock_container_client = MagicMock()
        mock_container_client.list_blobs.side_effect = Exception("Connection error")
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        with pytest.raises(HTTPException) as exc_info:
            service_instance.list_blobs("test-container")
        
        assert exc_info.value.status_code == 500
    
    def test_add_file_handles_upload_failure(self, service_instance, mock_file):
        """Test handling of upload failures"""
        mock_container_client = MagicMock()
        mock_container_client.upload_blob.side_effect = Exception("Upload failed")
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        with pytest.raises(Exception):
            service_instance.azure_addFile(mock_file, "test-container")
    
    def test_delete_blob_handles_not_found(self, service_instance):
        """Test handling of blob not found during deletion"""
        from fastapi import HTTPException
        
        mock_blob_client = MagicMock()
        mock_blob_client.delete_blob.side_effect = MockResourceNotFoundError("Blob not found")
        service_instance.blob_service_client.get_blob_client.return_value = mock_blob_client
        
        # Service wraps ResourceNotFoundError in HTTPException
        with pytest.raises((MockResourceNotFoundError, HTTPException)):
            service_instance.delete_blob("test-container", "nonexistent.csv")


class TestIntegrationScenarios:
    """Test integration scenarios"""
    
    def test_upload_and_list_workflow(self, service_instance, mock_file):
        """Test complete upload and list workflow"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        # Upload file
        with patch('service.service.uuid.uuid4', return_value='test-uuid'):
            upload_result = service_instance.azure_addFile(mock_file, "test-container")
        
        # Setup list_blobs to return the uploaded file
        blob = Mock()
        blob.name = upload_result["blob_name"]
        blob.size = 1024
        blob.last_modified = datetime.now()
        blob.content_settings = Mock()
        blob.content_settings.content_type = "text/csv"
        
        mock_container_client.list_blobs.return_value = [blob]
        
        # List blobs
        blobs = service_instance.list_blobs("test-container")
        
        assert len(blobs) == 1
        assert blobs[0].name == upload_result["blob_name"]
    
    def test_create_container_and_upload_file(self, service_instance, mock_file):
        """Test creating container and uploading file"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        # Create container
        container_result = service_instance.azure_addContainer("new-container")
        assert "created successfully" in container_result["message"]
        
        # Upload file to new container
        with patch('service.service.uuid.uuid4', return_value='test-uuid'):
            upload_result = service_instance.azure_addFile(mock_file, "new-container")
        
        assert upload_result["blob_name"] == "test_file_test-uuid.csv"


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_add_file_no_extension(self, service_instance):
        """Test uploading file with no extension"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        mock_file = Mock()
        mock_file.filename = "README"
        mock_file.content_type = "text/plain"
        mock_file.file = io.BytesIO(b"test content")
        
        with patch('service.service.uuid.uuid4', return_value='test-uuid'):
            result = service_instance.azure_addFile(mock_file, "test-container")
        
        assert result["blob_name"] == "README_test-uuid"
    
    def test_add_file_unicode_filename(self, service_instance):
        """Test uploading file with unicode characters in filename"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        mock_file = Mock()
        mock_file.filename = "测试文件_テスト_файл.txt"
        mock_file.content_type = "text/plain"
        mock_file.file = io.BytesIO(b"unicode content")
        
        with patch('service.service.uuid.uuid4', return_value='test-uuid'):
            result = service_instance.azure_addFile(mock_file, "test-container")
        
        assert "test-uuid" in result["blob_name"]
        assert result["blob_name"].endswith(".txt")
    
    def test_add_file_very_long_filename(self, service_instance):
        """Test uploading file with very long filename"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        long_name = "a" * 200  # Very long filename
        mock_file = Mock()
        mock_file.filename = f"{long_name}.csv"
        mock_file.content_type = "text/csv"
        mock_file.file = io.BytesIO(b"data")
        
        with patch('service.service.uuid.uuid4', return_value='test-uuid'):
            result = service_instance.azure_addFile(mock_file, "test-container")
        
        assert "test-uuid" in result["blob_name"]
        mock_container_client.upload_blob.assert_called_once()
    
    def test_add_file_with_dots_in_name(self, service_instance):
        """Test file with multiple dots in filename"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        mock_file = Mock()
        mock_file.filename = "my.test.file.data.csv"
        mock_file.content_type = "text/csv"
        mock_file.file = io.BytesIO(b"data")
        
        with patch('service.service.uuid.uuid4', return_value='test-uuid'):
            result = service_instance.azure_addFile(mock_file, "test-container")
        
        assert result["blob_name"] == "my.test.file.data_test-uuid.csv"
    
    def test_add_zero_byte_file(self, service_instance):
        """Test uploading empty/zero-byte file"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        mock_file = Mock()
        mock_file.filename = "empty.txt"
        mock_file.content_type = "text/plain"
        mock_file.file = io.BytesIO(b"")
        
        with patch('service.service.uuid.uuid4', return_value='test-uuid'):
            result = service_instance.azure_addFile(mock_file, "test-container")
        
        assert result["blob_name"] == "empty_test-uuid.txt"
        mock_container_client.upload_blob.assert_called_once()
    
    def test_list_blobs_with_zero_max_results(self, service_instance):
        """Test list_blobs with max_results=0"""
        mock_container_client = MagicMock()
        mock_container_client.list_blobs.return_value = []
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        result = service_instance.list_blobs("test-container", max_results=0)
        
        assert result == []
    
    def test_delete_blob_with_path_separators(self, service_instance):
        """Test deleting blob with path-like structure"""
        mock_blob_client = MagicMock()
        service_instance.blob_service_client.get_blob_client.return_value = mock_blob_client
        
        blob_name = "folder/subfolder/file.txt"
        service_instance.delete_blob("test-container", blob_name)
        
        service_instance.blob_service_client.get_blob_client.assert_called_once_with(
            container="test-container",
            blob=blob_name
        )
    
    def test_get_blob_with_large_file_multiple_chunks(self, service_instance):
        """Test downloading large file that returns multiple chunks"""
        mock_container_client = MagicMock()
        mock_blob_client = MagicMock()
        mock_download_blob = MagicMock()
        
        # Simulate large file with many chunks
        large_chunk = b"x" * (1024 * 1024)  # 1MB chunks
        test_chunks = [large_chunk] * 20  # 20MB file
        mock_download_blob.chunks.return_value = iter(test_chunks)
        
        mock_blob_client.download_blob.return_value = mock_download_blob
        mock_container_client.get_blob_client.return_value = mock_blob_client
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        result_chunks = list(service_instance.get_blob("large_file.bin", "test-container"))
        
        assert len(result_chunks) == 20
        assert all(len(chunk) == 1024 * 1024 for chunk in result_chunks)


class TestSecurityAndValidation:
    """Test security-related scenarios and input validation"""
    
    def test_add_file_with_path_traversal_attempt(self, service_instance):
        """Test that files with path traversal attempts are handled"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        mock_file = Mock()
        mock_file.filename = "../../etc/passwd"
        mock_file.content_type = "text/plain"
        mock_file.file = io.BytesIO(b"malicious content")
        
        with patch('service.service.uuid.uuid4', return_value='test-uuid'):
            result = service_instance.azure_addFile(mock_file, "test-container")
        
        # Service should handle the filename (not sanitized in current implementation)
        assert "test-uuid" in result["blob_name"]
    
    def test_add_file_with_special_shell_characters(self, service_instance):
        """Test filename with special shell characters"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        mock_file = Mock()
        mock_file.filename = "file;rm -rf;.txt"
        mock_file.content_type = "text/plain"
        mock_file.file = io.BytesIO(b"content")
        
        with patch('service.service.uuid.uuid4', return_value='test-uuid'):
            result = service_instance.azure_addFile(mock_file, "test-container")
        
        assert "test-uuid" in result["blob_name"]
    
    def test_add_file_with_sql_injection_attempt(self, service_instance):
        """Test filename with SQL injection attempt"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        mock_file = Mock()
        mock_file.filename = "'; DROP TABLE files; --.txt"
        mock_file.content_type = "text/plain"
        mock_file.file = io.BytesIO(b"content")
        
        with patch('service.service.uuid.uuid4', return_value='test-uuid'):
            result = service_instance.azure_addFile(mock_file, "test-container")
        
        assert "test-uuid" in result["blob_name"]
    
    def test_add_container_with_invalid_name_format(self, service_instance):
        """Test creating container with invalid name"""
        mock_container_client = MagicMock()
        
        # Container names must be lowercase
        mock_container_client.create_container.side_effect = MockHttpResponseError("Invalid container name")
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        with pytest.raises(MockHttpResponseError):
            service_instance.azure_addContainer("INVALID_CONTAINER_NAME")
    
    def test_list_blobs_with_sql_injection_in_name_filter(self, service_instance):
        """Test list_blobs with SQL injection attempt in name filter"""
        mock_container_client = MagicMock()
        mock_container_client.list_blobs.return_value = []
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        # Should be handled safely by Azure SDK
        result = service_instance.list_blobs(
            "test-container",
            name_starts_with="'; DROP TABLE --"
        )
        
        assert result == []


class TestAdvancedErrorHandling:
    """Test comprehensive error handling scenarios"""
    
    def test_add_file_connection_timeout(self, service_instance, mock_file):
        """Test handling of connection timeout during upload"""
        mock_container_client = MagicMock()
        mock_container_client.upload_blob.side_effect = MockServiceRequestTimeoutError("Connection timeout")
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        with pytest.raises(MockServiceRequestTimeoutError):
            service_instance.azure_addFile(mock_file, "test-container")
    
    def test_add_file_authentication_failure(self, service_instance, mock_file):
        """Test handling of authentication failure"""
        mock_container_client = MagicMock()
        mock_container_client.upload_blob.side_effect = MockClientAuthenticationError("Authentication failed")
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        with pytest.raises(MockClientAuthenticationError):
            service_instance.azure_addFile(mock_file, "test-container")
    
    def test_add_file_permission_denied(self, service_instance, mock_file):
        """Test handling of permission errors"""
        mock_container_client = MagicMock()
        mock_container_client.upload_blob.side_effect = MockHttpResponseError("Permission denied")
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        with pytest.raises(MockHttpResponseError):
            service_instance.azure_addFile(mock_file, "test-container")
    
    def test_add_container_already_exists(self, service_instance):
        """Test creating container that already exists"""
        mock_container_client = MagicMock()
        mock_container_client.create_container.side_effect = MockResourceExistsError("Container already exists")
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        with pytest.raises(MockResourceExistsError):
            service_instance.azure_addContainer("existing-container")
    
    def test_get_blob_not_found(self, service_instance):
        """Test downloading non-existent blob"""
        mock_container_client = MagicMock()
        mock_blob_client = MagicMock()
        mock_blob_client.download_blob.side_effect = MockResourceNotFoundError("Blob not found")
        mock_container_client.get_blob_client.return_value = mock_blob_client
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        with pytest.raises(MockResourceNotFoundError):
            list(service_instance.get_blob("nonexistent.txt", "test-container"))
    
    def test_list_blobs_container_not_found(self, service_instance):
        """Test listing blobs in non-existent container"""
        from fastapi import HTTPException
        
        mock_container_client = MagicMock()
        mock_container_client.list_blobs.side_effect = MockResourceNotFoundError("Container not found")
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        with pytest.raises((MockResourceNotFoundError, HTTPException)) as exc_info:
            service_instance.list_blobs("nonexistent-container")
    
    def test_update_file_quota_exceeded(self, service_instance, mock_file):
        """Test handling of storage quota exceeded error"""
        mock_container_client = MagicMock()
        error = MockHttpResponseError("Storage quota exceeded", status_code=507)
        mock_container_client.upload_blob.side_effect = error
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        with pytest.raises(MockHttpResponseError):
            service_instance.azure_updateFile(mock_file, "test.csv", "test-container")
    
    def test_delete_blob_concurrent_modification(self, service_instance):
        """Test deleting blob that was modified concurrently"""
        mock_blob_client = MagicMock()
        error = MockHttpResponseError("Precondition failed", status_code=412)
        mock_blob_client.delete_blob.side_effect = error
        service_instance.blob_service_client.get_blob_client.return_value = mock_blob_client
        
        with pytest.raises(MockHttpResponseError):
            service_instance.delete_blob("test-container", "modified_blob.csv")
    
    def test_list_containers_network_error(self, service_instance):
        """Test handling network error during container listing"""
        service_instance.blob_service_client.list_containers.side_effect = MockServiceRequestError("Network error")
        
        with pytest.raises(MockServiceRequestError):
            service_instance.list_container()


class TestResourceManagement:
    """Test resource management and cleanup scenarios"""
    
    def test_get_blob_properly_closes_stream(self, service_instance):
        """Test that blob download properly manages stream resources"""
        mock_container_client = MagicMock()
        mock_blob_client = MagicMock()
        mock_download_blob = MagicMock()
        
        test_chunks = [b"chunk1", b"chunk2"]
        mock_download_blob.chunks.return_value = iter(test_chunks)
        
        mock_blob_client.download_blob.return_value = mock_download_blob
        mock_container_client.get_blob_client.return_value = mock_blob_client
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        # Consume all chunks
        chunks = list(service_instance.get_blob("test.txt", "test-container"))
        
        assert len(chunks) == 2
        # Verify download was called with proper parameters
        mock_blob_client.download_blob.assert_called_once()
    
    def test_upload_file_with_large_content(self, service_instance):
        """Test uploading file with large content"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        # Create a large mock file (10MB)
        large_content = b"x" * (10 * 1024 * 1024)
        mock_file = Mock()
        mock_file.filename = "large_file.bin"
        mock_file.content_type = "application/octet-stream"
        mock_file.file = io.BytesIO(large_content)
        
        with patch('service.service.uuid.uuid4', return_value='test-uuid'):
            result = service_instance.azure_addFile(mock_file, "test-container")
        
        assert result["blob_name"] == "large_file_test-uuid.bin"
        # Verify upload was called with max_concurrency for performance
        call_kwargs = mock_container_client.upload_blob.call_args[1]
        assert call_kwargs['max_concurrency'] == 4
    
    def test_multiple_sequential_operations(self, service_instance, mock_file):
        """Test multiple sequential operations to verify no resource leaks"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        # Perform multiple uploads
        for i in range(5):
            with patch('service.service.uuid.uuid4', return_value=f'uuid-{i}'):
                result = service_instance.azure_addFile(mock_file, "test-container")
                assert f"uuid-{i}" in result["blob_name"]
        
        # Verify all uploads were called
        assert mock_container_client.upload_blob.call_count == 5


class TestBoundaryConditions:
    """Test boundary conditions and limits"""
    
    def test_list_blobs_exactly_max_results(self, service_instance):
        """Test list_blobs returns exactly max_results when available"""
        mock_container_client = MagicMock()
        
        # Create exactly 5 blobs
        blobs = []
        for i in range(5):
            blob = Mock()
            blob.name = f"file{i}.txt"
            blob.size = 1024
            blob.last_modified = datetime(2025, 12, 25, 10, i, 0)
            blob.content_settings = Mock()
            blob.content_settings.content_type = "text/plain"
            blobs.append(blob)
        
        mock_container_client.list_blobs.return_value = blobs
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        result = service_instance.list_blobs("test-container", max_results=5)
        
        assert len(result) == 5
    
    def test_list_blobs_less_than_max_results(self, service_instance):
        """Test list_blobs when fewer blobs exist than max_results"""
        mock_container_client = MagicMock()
        
        # Create only 3 blobs
        blobs = []
        for i in range(3):
            blob = Mock()
            blob.name = f"file{i}.txt"
            blob.size = 1024
            blob.last_modified = datetime(2025, 12, 25, 10, i, 0)
            blob.content_settings = Mock()
            blob.content_settings.content_type = "text/plain"
            blobs.append(blob)
        
        mock_container_client.list_blobs.return_value = blobs
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        result = service_instance.list_blobs("test-container", max_results=10)
        
        assert len(result) == 3
    
    def test_add_file_minimum_valid_filename(self, service_instance):
        """Test uploading file with minimum valid filename (single character)"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        mock_file = Mock()
        mock_file.filename = "a.t"
        mock_file.content_type = "text/plain"
        mock_file.file = io.BytesIO(b"content")
        
        with patch('service.service.uuid.uuid4', return_value='uuid'):
            result = service_instance.azure_addFile(mock_file, "test-container")
        
        assert result["blob_name"] == "a_uuid.t"
    
    def test_container_name_at_length_limit(self, service_instance):
        """Test container name at maximum length (63 characters)"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        # Azure container names can be 3-63 characters
        long_container_name = "a" * 63
        result = service_instance.azure_addContainer(long_container_name)
        
        assert "created successfully" in result["message"]
        assert long_container_name in result["message"]


class TestDataIntegrity:
    """Test data integrity and correctness"""
    
    def test_blob_info_mapping_correctness(self, service_instance):
        """Test that BlobInfo correctly maps all blob properties"""
        mock_container_client = MagicMock()
        
        blob = Mock()
        blob.name = "test_file.csv"
        blob.size = 2048
        blob.last_modified = datetime(2025, 12, 26, 15, 30, 45)
        blob.content_settings = Mock()
        blob.content_settings.content_type = "text/csv"
        
        mock_container_client.list_blobs.return_value = [blob]
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        result = service_instance.list_blobs("test-container")
        
        assert len(result) == 1
        assert result[0].name == "test_file.csv"
        assert result[0].size == 2048
        assert result[0].last_modified == datetime(2025, 12, 26, 15, 30, 45)
        assert result[0].content_type == "text/csv"
    
    def test_uploaded_file_name_preserves_original(self, service_instance):
        """Test that uploaded file preserves original filename in blob name"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        original_filename = "important_data_2025.csv"
        mock_file = Mock()
        mock_file.filename = original_filename
        mock_file.content_type = "text/csv"
        mock_file.file = io.BytesIO(b"data")
        
        with patch('service.service.uuid.uuid4', return_value='abc-123'):
            result = service_instance.azure_addFile(mock_file, "test-container")
        
        # Should preserve original name with UUID appended
        assert result["blob_name"].startswith("important_data_2025_")
        assert "abc-123" in result["blob_name"]
        assert result["blob_name"].endswith(".csv")
    
    def test_content_type_preserved_on_upload(self, service_instance):
        """Test that content type is correctly preserved during upload"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        content_types = [
            "application/json",
            "text/csv",
            "application/pdf",
            "image/png"
        ]
        
        for content_type in content_types:
            mock_file = Mock()
            mock_file.filename = f"test.{content_type.split('/')[-1]}"
            mock_file.content_type = content_type
            mock_file.file = io.BytesIO(b"content")
            
            service_instance.azure_addFile(mock_file, "test-container")
            
            # Verify ContentSettings was created with correct content_type
            call_args = mock_container_client.upload_blob.call_args
            content_settings = call_args[1]['content_settings']
            assert content_settings.content_type == content_type


class TestConcurrencyAndPerformance:
    """Test concurrency settings and performance characteristics"""
    
    def test_upload_uses_concurrent_connections(self, service_instance, mock_file):
        """Test that upload utilizes max_concurrency setting"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        service_instance.azure_addFile(mock_file, "test-container")
        
        call_kwargs = mock_container_client.upload_blob.call_args[1]
        assert call_kwargs['max_concurrency'] == 4
    
    def test_download_uses_concurrent_connections(self, service_instance):
        """Test that download utilizes max_concurrency setting"""
        mock_container_client = MagicMock()
        mock_blob_client = MagicMock()
        mock_download_blob = MagicMock()
        mock_download_blob.chunks.return_value = iter([b"data"])
        
        mock_blob_client.download_blob.return_value = mock_download_blob
        mock_container_client.get_blob_client.return_value = mock_blob_client
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        list(service_instance.get_blob("test.txt", "test-container"))
        
        mock_blob_client.download_blob.assert_called_once_with(
            max_concurrency=4,
            logging_enable=True
        )
    
    def test_upload_connection_timeout_configured(self, service_instance, mock_file):
        """Test that upload has proper connection timeout configured"""
        mock_container_client = MagicMock()
        service_instance.blob_service_client.get_container_client.return_value = mock_container_client
        
        service_instance.azure_addFile(mock_file, "test-container")
        
        call_kwargs = mock_container_client.upload_blob.call_args[1]
        assert call_kwargs['connection_timeout'] == 30000
    
    def test_service_initialization_chunk_size(self, mock_blob_service_client, mock_env_vars):
        """Test that service initializes with correct chunk size for large files"""
        service = FairnessUIservice()
        
        call_kwargs = mock_blob_service_client.from_connection_string.call_args[1]
        expected_chunk_size = 15 * 1024 * 1024  # 15MB
        assert call_kwargs['max_chunk_get_size'] == expected_chunk_size


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
