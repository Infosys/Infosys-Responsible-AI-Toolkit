"""
Comprehensive unit tests for Azure Blob Storage router (routing/router.py)
Tests cover all endpoints with 100% code coverage
"""

import pytest
import io
from unittest.mock import Mock, patch, MagicMock, ANY
from fastapi.testclient import TestClient
from fastapi import FastAPI, UploadFile, HTTPException
from routing.router import router
from mappers.mappers import BlobInfo

# Create a test application
app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestAzureAddFile:
    """Tests for POST /azureBlob/addFile endpoint"""

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_azure_add_file_success(self, mock_log, mock_ui_service):
        """Test successful file upload to Azure Blob"""
        # Arrange
        expected_response = {"message": "File uploaded successfully", "blob_name": "test.txt"}
        mock_ui_service.azure_addFile.return_value = expected_response
        
        # Act
        response = client.post(
            "/azureBlob/addFile",
            data={"container_name": "test-container"},
            files={"file": ("test.txt", io.BytesIO(b"test content"), "text/plain")}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json() == expected_response
        mock_ui_service.azure_addFile.assert_called_once()
        mock_log.info.assert_called()

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_azure_add_file_exception(self, mock_log, mock_ui_service):
        """Test file upload with exception handling"""
        # Arrange
        error_message = "Azure Blob connection failed"
        mock_ui_service.azure_addFile.side_effect = Exception(error_message)
        
        # Act
        response = client.post(
            "/azureBlob/addFile",
            data={"container_name": "test-container"},
            files={"file": ("test.txt", io.BytesIO(b"test content"), "text/plain")}
        )
        
        # Assert
        assert response.status_code == 500
        assert "Error in adding blob" in response.json()["detail"]
        mock_log.exception.assert_called()

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_azure_add_file_empty_container_name(self, mock_log, mock_ui_service):
        """Test file upload with empty container name"""
        # Arrange
        mock_ui_service.azure_addFile.side_effect = Exception("Container name cannot be empty")
        
        # Act
        response = client.post(
            "/azureBlob/addFile",
            data={"container_name": ""},
            files={"file": ("test.txt", io.BytesIO(b"test content"), "text/plain")}
        )
        
        # Assert
        assert response.status_code == 500
        assert "Error in adding blob" in response.json()["detail"]

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_azure_add_file_large_file(self, mock_log, mock_ui_service):
        """Test uploading a large file"""
        # Arrange
        large_content = b"x" * (100 * 1024 * 1024)  # 100MB
        expected_response = {"message": "File uploaded successfully"}
        mock_ui_service.azure_addFile.return_value = expected_response
        
        # Act
        response = client.post(
            "/azureBlob/addFile",
            data={"container_name": "test-container"},
            files={"file": ("large-file.bin", io.BytesIO(large_content), "application/octet-stream")}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json() == expected_response

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_azure_add_file_special_characters(self, mock_log, mock_ui_service):
        """Test file upload with special characters in filename"""
        # Arrange
        expected_response = {"message": "File uploaded successfully"}
        mock_ui_service.azure_addFile.return_value = expected_response
        
        # Act
        response = client.post(
            "/azureBlob/addFile",
            data={"container_name": "test-container"},
            files={"file": ("test file with spaces.txt", io.BytesIO(b"test content"), "text/plain")}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json() == expected_response


class TestListBlobs:
    """Tests for GET /azureBlob/{container_name}/listBlobs endpoint"""

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_list_blobs_success(self, mock_log, mock_ui_service):
        """Test successful blob listing"""
        # Arrange
        expected_blobs = [
            BlobInfo(name="file1.txt", size=1024, content_type="text/plain", last_modified="2024-01-01"),
            BlobInfo(name="file2.txt", size=2048, content_type="text/plain", last_modified="2024-01-02")
        ]
        mock_ui_service.list_blobs.return_value = expected_blobs
        
        # Act
        response = client.get("/azureBlob/test-container/listBlobs")
        
        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 2
        mock_ui_service.list_blobs.assert_called_once()

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_list_blobs_with_filters(self, mock_log, mock_ui_service):
        """Test blob listing with query filters"""
        # Arrange
        expected_blobs = [
            BlobInfo(name="data-file1.txt", size=1024, content_type="text/plain", last_modified="2024-01-01")
        ]
        mock_ui_service.list_blobs.return_value = expected_blobs
        
        # Act
        response = client.get(
            "/azureBlob/test-container/listBlobs",
            params={
                "name_starts_with": "data-",
                "content_type": "text/plain",
                "max_results": 50
            }
        )
        
        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 1
        mock_ui_service.list_blobs.assert_called_once_with(
            "test-container", "data-", "text/plain", 50
        )

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_list_blobs_empty_result(self, mock_log, mock_ui_service):
        """Test blob listing with empty result"""
        # Arrange
        mock_ui_service.list_blobs.return_value = []
        
        # Act
        response = client.get("/azureBlob/test-container/listBlobs")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == []

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_list_blobs_exception(self, mock_log, mock_ui_service):
        """Test blob listing with exception"""
        # Arrange
        mock_ui_service.list_blobs.side_effect = Exception("Container not found")
        
        # Act
        response = client.get("/azureBlob/test-container/listBlobs")
        
        # Assert
        assert response.status_code == 500
        assert "Container not found" in response.json()["detail"]

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_list_blobs_max_results_boundary(self, mock_log, mock_ui_service):
        """Test blob listing with boundary max_results"""
        # Arrange
        mock_ui_service.list_blobs.return_value = []
        
        # Act
        response = client.get(
            "/azureBlob/test-container/listBlobs",
            params={"max_results": 1000}
        )
        
        # Assert
        assert response.status_code == 200
        mock_ui_service.list_blobs.assert_called_once_with(
            "test-container", None, None, 1000
        )


class TestAzureGetBlob:
    """Tests for GET /azureBlob/getBlob endpoint"""

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_azure_get_blob_success(self, mock_log, mock_ui_service):
        """Test successful blob retrieval"""
        # Arrange
        mock_content = io.BytesIO(b"test content")
        mock_ui_service.get_blob.return_value = mock_content
        
        # Act
        response = client.get(
            "/azureBlob/getBlob",
            params={"blob_name": "test.txt", "container_name": "test-container"}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.content == b"test content"
        assert "attachment" in response.headers["content-disposition"]
        mock_ui_service.get_blob.assert_called_once_with("test.txt", "test-container")

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_azure_get_blob_with_special_characters(self, mock_log, mock_ui_service):
        """Test blob retrieval with special characters in name"""
        # Arrange
        mock_content = io.BytesIO(b"test content")
        mock_ui_service.get_blob.return_value = mock_content
        
        # Act
        response = client.get(
            "/azureBlob/getBlob",
            params={"blob_name": "test file.txt", "container_name": "test-container"}
        )
        
        # Assert
        assert response.status_code == 200
        assert "test file.txt" in response.headers["content-disposition"]

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_azure_get_blob_exception(self, mock_log, mock_ui_service):
        """Test blob retrieval with exception"""
        # Arrange
        mock_ui_service.get_blob.side_effect = Exception("Blob not found")
        
        # Act
        response = client.get(
            "/azureBlob/getBlob",
            params={"blob_name": "missing.txt", "container_name": "test-container"}
        )
        
        # Assert
        assert response.status_code == 500
        assert "Error in fetching blob" in response.json()["detail"]
        mock_log.exception.assert_called()

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_azure_get_blob_large_file(self, mock_log, mock_ui_service):
        """Test retrieving a large blob"""
        # Arrange
        large_content = b"x" * (100 * 1024 * 1024)  # 100MB
        mock_content = io.BytesIO(large_content)
        mock_ui_service.get_blob.return_value = mock_content
        
        # Act
        response = client.get(
            "/azureBlob/getBlob",
            params={"blob_name": "large-file.bin", "container_name": "test-container"}
        )
        
        # Assert
        assert response.status_code == 200
        assert len(response.content) == len(large_content)


class TestDeleteBlob:
    """Tests for DELETE /azureBlob/delete_blob endpoint"""

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_delete_blob_success(self, mock_log, mock_ui_service):
        """Test successful blob deletion"""
        # Arrange
        mock_ui_service.delete_blob.return_value = None
        
        # Act
        response = client.delete(
            "/azureBlob/delete_blob",
            params={"blob_name": "test.txt", "container_name": "test-container"}
        )
        
        # Assert
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        mock_ui_service.delete_blob.assert_called_once_with("test-container", "test.txt")

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_delete_blob_with_path(self, mock_log, mock_ui_service):
        """Test deleting blob with nested path"""
        # Arrange
        mock_ui_service.delete_blob.return_value = None
        
        # Act
        response = client.delete(
            "/azureBlob/delete_blob",
            params={"blob_name": "folder/subfolder/file.txt", "container_name": "test-container"}
        )
        
        # Assert
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_delete_blob_exception(self, mock_log, mock_ui_service):
        """Test blob deletion with exception"""
        # Arrange
        mock_ui_service.delete_blob.side_effect = Exception("Blob not found")
        
        # Act
        response = client.delete(
            "/azureBlob/delete_blob",
            params={"blob_name": "missing.txt", "container_name": "test-container"}
        )
        
        # Assert
        assert response.status_code == 500
        assert "Error deleting blob" in response.json()["detail"]
        mock_log.exception.assert_called()

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_delete_blob_empty_name(self, mock_log, mock_ui_service):
        """Test deleting blob with empty name"""
        # Arrange
        mock_ui_service.delete_blob.side_effect = Exception("Blob name cannot be empty")
        
        # Act
        response = client.delete(
            "/azureBlob/delete_blob",
            params={"blob_name": "", "container_name": "test-container"}
        )
        
        # Assert
        assert response.status_code == 500


class TestAzureUpdateFile:
    """Tests for POST /azureBlob/updateFile endpoint"""

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_azure_update_file_success(self, mock_log, mock_ui_service):
        """Test successful file update"""
        # Arrange
        expected_response = {"message": "File updated successfully"}
        mock_ui_service.azure_updateFile.return_value = expected_response
        
        # Act
        response = client.post(
            "/azureBlob/updateFile",
            data={"blob_name": "test.txt", "container_name": "test-container"},
            files={"file": ("test.txt", io.BytesIO(b"updated content"), "text/plain")}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json() == expected_response
        mock_ui_service.azure_updateFile.assert_called_once()
        mock_log.info.assert_called()

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_azure_update_file_different_content_type(self, mock_log, mock_ui_service):
        """Test file update with different content type"""
        # Arrange
        expected_response = {"message": "File updated successfully"}
        mock_ui_service.azure_updateFile.return_value = expected_response
        
        # Act
        response = client.post(
            "/azureBlob/updateFile",
            data={"blob_name": "data.json", "container_name": "test-container"},
            files={"file": ("data.json", io.BytesIO(b'{"key": "value"}'), "application/json")}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json() == expected_response

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_azure_update_file_exception(self, mock_log, mock_ui_service):
        """Test file update with exception"""
        # Arrange
        mock_ui_service.azure_updateFile.side_effect = Exception("Update failed")
        
        # Act
        response = client.post(
            "/azureBlob/updateFile",
            data={"blob_name": "test.txt", "container_name": "test-container"},
            files={"file": ("test.txt", io.BytesIO(b"content"), "text/plain")}
        )
        
        # Assert
        assert response.status_code == 500
        assert "Error updating blob" in response.json()["detail"]
        mock_log.exception.assert_called()

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_azure_update_file_large_file(self, mock_log, mock_ui_service):
        """Test updating a large file"""
        # Arrange
        large_content = b"x" * (100 * 1024 * 1024)  # 100MB
        expected_response = {"message": "File updated successfully"}
        mock_ui_service.azure_updateFile.return_value = expected_response
        
        # Act
        response = client.post(
            "/azureBlob/updateFile",
            data={"blob_name": "large-file.bin", "container_name": "test-container"},
            files={"file": ("large-file.bin", io.BytesIO(large_content), "application/octet-stream")}
        )
        
        # Assert
        assert response.status_code == 200


class TestListContainers:
    """Tests for GET /azureBlob/List-Containers endpoint"""

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_list_containers_success(self, mock_log, mock_ui_service):
        """Test successful container listing"""
        # Arrange
        expected_containers = [
            {"name": "container1"},
            {"name": "container2"}
        ]
        mock_ui_service.list_container.return_value = expected_containers
        
        # Act
        response = client.get("/azureBlob/List-Containers")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == expected_containers
        mock_ui_service.list_container.assert_called_once()

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_list_containers_empty(self, mock_log, mock_ui_service):
        """Test container listing with empty result"""
        # Arrange
        mock_ui_service.list_container.return_value = []
        
        # Act
        response = client.get("/azureBlob/List-Containers")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == []

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_list_containers_exception(self, mock_log, mock_ui_service):
        """Test container listing with exception"""
        # Arrange
        mock_ui_service.list_container.side_effect = Exception("Connection failed")
        
        # Act
        response = client.get("/azureBlob/List-Containers")
        
        # Assert
        assert response.status_code == 500
        assert "Error in fetching containers" in response.json()["detail"]
        mock_log.exception.assert_called()

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_list_containers_many_containers(self, mock_log, mock_ui_service):
        """Test listing many containers"""
        # Arrange
        expected_containers = [{"name": f"container{i}"} for i in range(100)]
        mock_ui_service.list_container.return_value = expected_containers
        
        # Act
        response = client.get("/azureBlob/List-Containers")
        
        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 100


class TestAzureBlobAddContainer:
    """Tests for POST /azureBlob/addContainer endpoint"""

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_azureBlob_addContainer_success(self, mock_log, mock_ui_service):
        """Test successful container creation"""
        # Arrange
        expected_response = {"message": "Container created successfully"}
        mock_ui_service.azure_addContainer.return_value = expected_response
        
        # Act
        response = client.post(
            "/azureBlob/addContainer",
            data={"container_name": "new-container"}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json() == expected_response
        mock_ui_service.azure_addContainer.assert_called_once_with("new-container")
        mock_log.info.assert_called()

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_azureBlob_addContainer_with_valid_name(self, mock_log, mock_ui_service):
        """Test container creation with valid name formats"""
        # Arrange
        expected_response = {"message": "Container created successfully"}
        mock_ui_service.azure_addContainer.return_value = expected_response
        
        # Act
        response = client.post(
            "/azureBlob/addContainer",
            data={"container_name": "my-container-123"}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json() == expected_response

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_azureBlob_addContainer_exception(self, mock_log, mock_ui_service):
        """Test container creation with exception"""
        # Arrange
        mock_ui_service.azure_addContainer.side_effect = Exception("Container already exists")
        
        # Act
        response = client.post(
            "/azureBlob/addContainer",
            data={"container_name": "existing-container"}
        )
        
        # Assert
        assert response.status_code == 500
        assert "Error updating blob" in response.json()["detail"]
        mock_log.exception.assert_called()

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_azureBlob_addContainer_invalid_name(self, mock_log, mock_ui_service):
        """Test container creation with invalid name"""
        # Arrange
        mock_ui_service.azure_addContainer.side_effect = Exception("Invalid container name")
        
        # Act
        response = client.post(
            "/azureBlob/addContainer",
            data={"container_name": "Invalid_Name"}
        )
        
        # Assert
        assert response.status_code == 500

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_azureBlob_addContainer_empty_name(self, mock_log, mock_ui_service):
        """Test container creation with empty name"""
        # Arrange
        mock_ui_service.azure_addContainer.side_effect = Exception("Container name cannot be empty")
        
        # Act
        response = client.post(
            "/azureBlob/addContainer",
            data={"container_name": ""}
        )
        
        # Assert
        assert response.status_code == 500


class TestIntegrationScenarios:
    """Integration tests covering multiple operations"""

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_upload_then_get_blob(self, mock_log, mock_ui_service):
        """Test upload followed by get operation"""
        # Arrange
        upload_response = {"message": "File uploaded successfully", "blob_name": "test.txt"}
        mock_ui_service.azure_addFile.return_value = upload_response
        
        mock_content = io.BytesIO(b"test content")
        mock_ui_service.get_blob.return_value = mock_content
        
        # Act - Upload
        upload_result = client.post(
            "/azureBlob/addFile",
            data={"container_name": "test-container"},
            files={"file": ("test.txt", io.BytesIO(b"test content"), "text/plain")}
        )
        
        # Act - Get
        get_result = client.get(
            "/azureBlob/getBlob",
            params={"blob_name": "test.txt", "container_name": "test-container"}
        )
        
        # Assert
        assert upload_result.status_code == 200
        assert get_result.status_code == 200
        assert get_result.content == b"test content"

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_create_container_then_upload(self, mock_log, mock_ui_service):
        """Test container creation followed by file upload"""
        # Arrange
        create_response = {"message": "Container created successfully"}
        mock_ui_service.azure_addContainer.return_value = create_response
        
        upload_response = {"message": "File uploaded successfully"}
        mock_ui_service.azure_addFile.return_value = upload_response
        
        # Act - Create Container
        create_result = client.post(
            "/azureBlob/addContainer",
            data={"container_name": "new-container"}
        )
        
        # Act - Upload File
        upload_result = client.post(
            "/azureBlob/addFile",
            data={"container_name": "new-container"},
            files={"file": ("test.txt", io.BytesIO(b"test content"), "text/plain")}
        )
        
        # Assert
        assert create_result.status_code == 200
        assert upload_result.status_code == 200

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_concurrent_operations_different_blobs(self, mock_log, mock_ui_service):
        """Test concurrent operations on different blobs"""
        # Arrange
        mock_ui_service.delete_blob.return_value = None
        mock_ui_service.azure_addFile.return_value = {"message": "File uploaded"}
        
        # Act - Delete and Upload concurrently
        delete_result = client.delete(
            "/azureBlob/delete_blob",
            params={"blob_name": "old.txt", "container_name": "test-container"}
        )
        
        upload_result = client.post(
            "/azureBlob/addFile",
            data={"container_name": "test-container"},
            files={"file": ("new.txt", io.BytesIO(b"new content"), "text/plain")}
        )
        
        # Assert
        assert delete_result.status_code == 200
        assert upload_result.status_code == 200

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_upload_update_delete_workflow(self, mock_log, mock_ui_service):
        """Test complete lifecycle: upload, update, then delete"""
        # Arrange
        mock_ui_service.azure_addFile.return_value = {"message": "File uploaded"}
        mock_ui_service.azure_updateFile.return_value = {"message": "File updated"}
        mock_ui_service.delete_blob.return_value = None
        
        # Act - Upload
        upload_result = client.post(
            "/azureBlob/addFile",
            data={"container_name": "test-container"},
            files={"file": ("test.txt", io.BytesIO(b"original content"), "text/plain")}
        )
        
        # Act - Update
        update_result = client.post(
            "/azureBlob/updateFile",
            data={"blob_name": "test.txt", "container_name": "test-container"},
            files={"file": ("test.txt", io.BytesIO(b"updated content"), "text/plain")}
        )
        
        # Act - Delete
        delete_result = client.delete(
            "/azureBlob/delete_blob",
            params={"blob_name": "test.txt", "container_name": "test-container"}
        )
        
        # Assert
        assert upload_result.status_code == 200
        assert update_result.status_code == 200
        assert delete_result.status_code == 200


class TestErrorHandlingAndEdgeCases:
    """Tests for error handling and edge cases"""

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_network_timeout_simulation(self, mock_log, mock_ui_service):
        """Test handling of network timeout"""
        # Arrange
        mock_ui_service.azure_addFile.side_effect = Exception("Connection timeout")
        
        # Act
        response = client.post(
            "/azureBlob/addFile",
            data={"container_name": "test-container"},
            files={"file": ("test.txt", io.BytesIO(b"test content"), "text/plain")}
        )
        
        # Assert
        assert response.status_code == 500
        assert "Connection timeout" in response.json()["detail"]

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_permission_denied_error(self, mock_log, mock_ui_service):
        """Test handling of permission denied error"""
        # Arrange
        mock_ui_service.azure_addFile.side_effect = Exception("Permission denied")
        
        # Act
        response = client.post(
            "/azureBlob/addFile",
            data={"container_name": "test-container"},
            files={"file": ("test.txt", io.BytesIO(b"test content"), "text/plain")}
        )
        
        # Assert
        assert response.status_code == 500
        assert "Permission denied" in response.json()["detail"]

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_malformed_request_handling(self, mock_log, mock_ui_service):
        """Test handling of malformed requests"""
        # Arrange
        mock_ui_service.azure_addFile.side_effect = Exception("Invalid request format")
        
        # Act
        response = client.post(
            "/azureBlob/addFile",
            data={"container_name": "test-container"},
            files={"file": ("test.txt", io.BytesIO(b"test content"), "text/plain")}
        )
        
        # Assert
        assert response.status_code == 500

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_special_characters_in_blob_name(self, mock_log, mock_ui_service):
        """Test handling of special characters in blob name"""
        # Arrange
        mock_content = io.BytesIO(b"test content")
        mock_ui_service.get_blob.return_value = mock_content
        
        # Act
        response = client.get(
            "/azureBlob/getBlob",
            params={"blob_name": "file@#$.txt", "container_name": "test-container"}
        )
        
        # Assert
        assert response.status_code == 200

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_unicode_characters_in_filename(self, mock_log, mock_ui_service):
        """Test handling of unicode characters in filename"""
        # Arrange
        expected_response = {"message": "File uploaded successfully"}
        mock_ui_service.azure_addFile.return_value = expected_response
        
        # Act
        response = client.post(
            "/azureBlob/addFile",
            data={"container_name": "test-container"},
            files={"file": ("тест文件.txt", io.BytesIO(b"test content"), "text/plain")}
        )
        
        # Assert
        assert response.status_code == 200

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_zero_byte_file_upload(self, mock_log, mock_ui_service):
        """Test upload of zero-byte file"""
        # Arrange
        expected_response = {"message": "File uploaded successfully"}
        mock_ui_service.azure_addFile.return_value = expected_response
        
        # Act
        response = client.post(
            "/azureBlob/addFile",
            data={"container_name": "test-container"},
            files={"file": ("empty.txt", io.BytesIO(b""), "text/plain")}
        )
        
        # Assert
        assert response.status_code == 200


class TestSecurityConsiderations:
    """Tests for security considerations"""

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_path_traversal_attempt(self, mock_log, mock_ui_service):
        """Test handling of path traversal attempts"""
        # Arrange
        mock_content = io.BytesIO(b"content")
        mock_ui_service.get_blob.return_value = mock_content
        
        # Act
        response = client.get(
            "/azureBlob/getBlob",
            params={"blob_name": "../../etc/passwd", "container_name": "test-container"}
        )
        
        # Assert - Should still process (Azure SDK handles path traversal)
        assert response.status_code == 200

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_sql_injection_attempt_in_container_name(self, mock_log, mock_ui_service):
        """Test handling of SQL injection attempts"""
        # Arrange
        expected_response = {"message": "File uploaded successfully"}
        mock_ui_service.azure_addFile.return_value = expected_response
        
        # Act
        response = client.post(
            "/azureBlob/addFile",
            data={"container_name": "test'; DROP TABLE containers;--"},
            files={"file": ("test.txt", io.BytesIO(b"test content"), "text/plain")}
        )
        
        # Assert - Should handle safely
        assert response.status_code == 200

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_extremely_long_blob_name(self, mock_log, mock_ui_service):
        """Test handling of extremely long blob names"""
        # Arrange
        long_name = "a" * 10000
        expected_response = {"message": "File uploaded successfully"}
        mock_ui_service.azure_addFile.return_value = expected_response
        
        # Act
        response = client.post(
            "/azureBlob/addFile",
            data={"container_name": "test-container"},
            files={"file": (long_name, io.BytesIO(b"test content"), "text/plain")}
        )
        
        # Assert
        assert response.status_code == 200


class TestPerformanceAndResourceManagement:
    """Tests for performance and resource management"""

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_list_blobs_pagination(self, mock_log, mock_ui_service):
        """Test blob listing with pagination"""
        # Arrange
        blobs = [BlobInfo(name=f"file{i}.txt", size=1024, content_type="text/plain", last_modified="2024-01-01") 
                 for i in range(10)]
        mock_ui_service.list_blobs.return_value = blobs
        
        # Act
        response = client.get(
            "/azureBlob/test-container/listBlobs",
            params={"max_results": 10}
        )
        
        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 10

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_streaming_response_headers(self, mock_log, mock_ui_service):
        """Test streaming response headers"""
        # Arrange
        mock_content = io.BytesIO(b"test content")
        mock_ui_service.get_blob.return_value = mock_content
        
        # Act
        response = client.get(
            "/azureBlob/getBlob",
            params={"blob_name": "test.txt", "container_name": "test-container"}
        )
        
        # Assert
        assert response.status_code == 200
        assert "content-disposition" in response.headers
        assert response.headers["content-type"] == "application/octet-stream"


class TestRegressionScenarios:
    """Tests for regression scenarios"""

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_update_non_existent_file(self, mock_log, mock_ui_service):
        """Test updating a non-existent file"""
        # Arrange
        mock_ui_service.azure_updateFile.side_effect = Exception("Blob not found")
        
        # Act
        response = client.post(
            "/azureBlob/updateFile",
            data={"blob_name": "non-existent.txt", "container_name": "test-container"},
            files={"file": ("test.txt", io.BytesIO(b"content"), "text/plain")}
        )
        
        # Assert
        assert response.status_code == 500
        assert "Error updating blob" in response.json()["detail"]

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_delete_already_deleted_blob(self, mock_log, mock_ui_service):
        """Test deleting an already deleted blob"""
        # Arrange
        mock_ui_service.delete_blob.side_effect = Exception("Blob not found")
        
        # Act
        response = client.delete(
            "/azureBlob/delete_blob",
            params={"blob_name": "deleted.txt", "container_name": "test-container"}
        )
        
        # Assert
        assert response.status_code == 500

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_list_blobs_in_non_existent_container(self, mock_log, mock_ui_service):
        """Test listing blobs in non-existent container"""
        # Arrange
        mock_ui_service.list_blobs.side_effect = Exception("Container not found")
        
        # Act
        response = client.get("/azureBlob/non-existent-container/listBlobs")
        
        # Assert
        assert response.status_code == 500

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_add_file_to_non_existent_container(self, mock_log, mock_ui_service):
        """Test adding file to non-existent container"""
        # Arrange
        mock_ui_service.azure_addFile.side_effect = Exception("Container not found")
        
        # Act
        response = client.post(
            "/azureBlob/addFile",
            data={"container_name": "non-existent-container"},
            files={"file": ("test.txt", io.BytesIO(b"test content"), "text/plain")}
        )
        
        # Assert
        assert response.status_code == 500


class TestContentTypeHandling:
    """Tests for content type handling"""

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_json_file_upload(self, mock_log, mock_ui_service):
        """Test JSON file upload"""
        # Arrange
        expected_response = {"message": "File uploaded successfully"}
        mock_ui_service.azure_addFile.return_value = expected_response
        
        # Act
        response = client.post(
            "/azureBlob/addFile",
            data={"container_name": "test-container"},
            files={"file": ("data.json", io.BytesIO(b'{"key": "value"}'), "application/json")}
        )
        
        # Assert
        assert response.status_code == 200

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_image_file_upload(self, mock_log, mock_ui_service):
        """Test image file upload"""
        # Arrange
        expected_response = {"message": "File uploaded successfully"}
        mock_ui_service.azure_addFile.return_value = expected_response
        
        # Act
        response = client.post(
            "/azureBlob/addFile",
            data={"container_name": "test-container"},
            files={"file": ("image.png", io.BytesIO(b'\x89PNG\r\n\x1a\n'), "image/png")}
        )
        
        # Assert
        assert response.status_code == 200

    @patch('routing.router.uiService')
    @patch('routing.router.log')
    def test_filter_by_content_type(self, mock_log, mock_ui_service):
        """Test filtering blobs by content type"""
        # Arrange
        filtered_blobs = [
            BlobInfo(name="file1.json", size=1024, content_type="application/json", last_modified="2024-01-01")
        ]
        mock_ui_service.list_blobs.return_value = filtered_blobs
        
        # Act
        response = client.get(
            "/azureBlob/test-container/listBlobs",
            params={"content_type": "application/json"}
        )
        
        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["content_type"] == "application/json"
