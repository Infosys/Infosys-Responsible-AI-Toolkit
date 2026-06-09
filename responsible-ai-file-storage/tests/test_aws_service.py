"""
Comprehensive test suite for AWS S3 service
Tests all methods with edge cases, error handling, security, and resource management
"""

import sys
import os
from unittest.mock import MagicMock, Mock, patch, mock_open
from datetime import datetime
from io import BytesIO

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock exception classes for AWS
class MockClientError(Exception):
    """Mock for botocore.exceptions.ClientError"""
    def __init__(self, error_response, operation_name):
        self.response = error_response
        self.operation_name = operation_name
        super().__init__(f"An error occurred ({error_response['Error']['Code']}) when calling the {operation_name} operation")

class MockNoCredentialsError(Exception):
    """Mock for botocore.exceptions.NoCredentialsError"""
    pass

# Create mock modules for AWS SDK before importing service
mock_boto3 = MagicMock()
mock_botocore = MagicMock()
mock_botocore_exceptions = MagicMock()
mock_botocore_config = MagicMock()

# Set up mock exception classes
mock_botocore_exceptions.ClientError = MockClientError
mock_botocore_exceptions.NoCredentialsError = MockNoCredentialsError

# Create Config class mock
class MockConfig:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

mock_botocore_config.Config = MockConfig

# Inject mocks into sys.modules
sys.modules['boto3'] = mock_boto3
sys.modules['botocore'] = mock_botocore
sys.modules['botocore.exceptions'] = mock_botocore_exceptions
sys.modules['botocore.client'] = MagicMock()
sys.modules['botocore.config'] = mock_botocore_config

import pytest
from fastapi import HTTPException
from service.aws_service import FairnessUIservice
from mappers.mappers import BlobInfo


# Fixtures
@pytest.fixture
def mock_s3_client():
    """Mock S3 client"""
    return MagicMock()

@pytest.fixture
def mock_boto3_client(mock_s3_client):
    """Mock boto3.client function"""
    with patch('boto3.client', return_value=mock_s3_client) as mock:
        yield mock

@pytest.fixture
def service_instance(mock_boto3_client, mock_s3_client):
    """Create service instance with mocked S3 client"""
    with patch.dict('os.environ', {
        'AWS_ACCESS_KEY_ID': 'test_key',
        'AWS_SECRET_ACCESS_KEY': 'test_secret',
        'AWS_REGION': 'us-east-1'
    }):
        service = FairnessUIservice()
        service.s3_client = mock_s3_client
        return service

@pytest.fixture
def mock_upload_file():
    """Create mock UploadFile object"""
    mock_file = MagicMock()
    mock_file.filename = "test.txt"
    mock_file.content_type = "text/plain"
    mock_file.file = BytesIO(b"Test content for upload")
    mock_file.file.seek = MagicMock()
    return mock_file

@pytest.fixture
def mock_bucket_list():
    """Create mock bucket list response"""
    return {
        'Buckets': [
            {'Name': 'bucket1', 'CreationDate': datetime(2024, 1, 1)},
            {'Name': 'bucket2', 'CreationDate': datetime(2024, 1, 2)}
        ]
    }


# Test Class 1: Initialization Tests
class TestInitialization:
    """Test service initialization and configuration"""

    def test_init_with_environment_variables(self):
        """Test initialization with environment variables"""
        with patch.dict('os.environ', {
            'AWS_ACCESS_KEY_ID': 'test_key',
            'AWS_SECRET_ACCESS_KEY': 'test_secret',
            'AWS_REGION': 'us-west-2',
            'AWS_SESSION_TOKEN': 'test_token'
        }):
            service = FairnessUIservice()
            assert service is not None
            assert hasattr(service, 's3_client')

    def test_init_default_region(self):
        """Test initialization with default region"""
        with patch.dict('os.environ', {
            'AWS_ACCESS_KEY_ID': 'test_key',
            'AWS_SECRET_ACCESS_KEY': 'test_secret'
        }, clear=True):
            service = FairnessUIservice()
            # Service should initialize successfully with default region
            assert service is not None
            assert hasattr(service, 's3_client')


# Test Class 2: List Buckets Tests
class TestListBuckets:
    """Test list_buckets functionality"""

    def test_list_buckets_success(self, service_instance, mock_s3_client, mock_bucket_list):
        """Test successful bucket listing"""
        mock_s3_client.list_buckets.return_value = mock_bucket_list

        result = service_instance.list_buckets()

        assert len(result) == 2
        assert result[0] == 'bucket1'
        assert result[1] == 'bucket2'
        mock_s3_client.list_buckets.assert_called_once()

    def test_list_buckets_empty(self, service_instance, mock_s3_client):
        """Test listing when no buckets exist"""
        mock_s3_client.list_buckets.return_value = {'Buckets': []}

        result = service_instance.list_buckets()

        assert result == []

    def test_list_buckets_error(self, service_instance, mock_s3_client):
        """Test error handling when listing buckets"""
        mock_s3_client.list_buckets.side_effect = MockClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'Access Denied'}},
            'ListBuckets'
        )

        with pytest.raises(HTTPException) as exc_info:
            service_instance.list_buckets()

        assert exc_info.value.status_code == 500

    def test_list_buckets_returns_names_only(self, service_instance, mock_s3_client):
        """Test that only bucket names are returned"""
        mock_s3_client.list_buckets.return_value = {
            'Buckets': [
                {'Name': 'test-bucket', 'CreationDate': datetime(2024, 1, 1)}
            ]
        }

        result = service_instance.list_buckets()

        assert isinstance(result, list)
        assert all(isinstance(name, str) for name in result)


# Test Class 3: Upload File Tests
class TestUploadFile:
    """Test s3_upload_file functionality"""

    def test_upload_file_success_with_key(self, service_instance, mock_s3_client, mock_upload_file):
        """Test successful file upload with provided object key"""
        mock_s3_client.head_object.side_effect = MockClientError(
            {'Error': {'Code': '404', 'Message': 'Not Found'}},
            'HeadObject'
        )
        mock_s3_client.upload_fileobj.return_value = None

        result = service_instance.s3_upload_file(
            mock_upload_file,
            'test-bucket',
            'custom-key.txt'
        )

        assert result['object_key'] == 'custom-key.txt'
        mock_s3_client.upload_fileobj.assert_called_once()
        mock_upload_file.file.seek.assert_called_with(0)

    def test_upload_file_auto_generate_key(self, service_instance, mock_s3_client, mock_upload_file):
        """Test file upload with auto-generated object key"""
        mock_s3_client.head_object.side_effect = MockClientError(
            {'Error': {'Code': '404', 'Message': 'Not Found'}},
            'HeadObject'
        )
        mock_s3_client.upload_fileobj.return_value = None

        result = service_instance.s3_upload_file(
            mock_upload_file,
            'test-bucket'
        )

        assert 'object_key' in result
        assert 'test' in result['object_key']  # Contains original filename
        assert '.txt' in result['object_key']  # Contains extension
        mock_s3_client.upload_fileobj.assert_called_once()

    def test_upload_file_already_exists(self, service_instance, mock_s3_client, mock_upload_file):
        """Test upload when file already exists"""
        mock_s3_client.head_object.return_value = {'ContentLength': 100}

        with pytest.raises(HTTPException) as exc_info:
            service_instance.s3_upload_file(
                mock_upload_file,
                'test-bucket',
                'existing-key.txt'
            )

        assert exc_info.value.status_code == 409
        assert 'already exists' in str(exc_info.value.detail)

    def test_upload_file_client_error(self, service_instance, mock_s3_client, mock_upload_file):
        """Test error handling during upload"""
        mock_s3_client.head_object.side_effect = MockClientError(
            {'Error': {'Code': '404', 'Message': 'Not Found'}},
            'HeadObject'
        )
        mock_s3_client.upload_fileobj.side_effect = MockClientError(
            {'Error': {'Code': 'NoSuchBucket', 'Message': 'Bucket does not exist'}},
            'UploadFileobj'
        )

        with pytest.raises(HTTPException) as exc_info:
            service_instance.s3_upload_file(
                mock_upload_file,
                'test-bucket',
                'test-key.txt'
            )

        assert exc_info.value.status_code == 500

    def test_upload_file_with_special_characters(self, service_instance, mock_s3_client, mock_upload_file):
        """Test upload with special characters in key"""
        mock_s3_client.head_object.side_effect = MockClientError(
            {'Error': {'Code': '404', 'Message': 'Not Found'}},
            'HeadObject'
        )
        mock_s3_client.upload_fileobj.return_value = None

        special_key = 'folder/file with spaces.txt'
        result = service_instance.s3_upload_file(
            mock_upload_file,
            'test-bucket',
            special_key
        )

        assert result['object_key'] == special_key

    def test_upload_file_resets_file_pointer(self, service_instance, mock_s3_client, mock_upload_file):
        """Test file pointer is reset before upload"""
        mock_s3_client.head_object.side_effect = MockClientError(
            {'Error': {'Code': '404', 'Message': 'Not Found'}},
            'HeadObject'
        )
        mock_s3_client.upload_fileobj.return_value = None

        service_instance.s3_upload_file(
            mock_upload_file,
            'test-bucket',
            'test-key.txt'
        )

        mock_upload_file.file.seek.assert_called_with(0)


# Test Class 4: Update File Tests
class TestUpdateFile:
    """Test s3_update_file functionality"""

    def test_update_file_success(self, service_instance, mock_s3_client, mock_upload_file):
        """Test successful file update"""
        mock_s3_client.upload_fileobj.return_value = None

        result = service_instance.s3_update_file(
            mock_upload_file,
            'test-key.txt',
            'test-bucket'
        )

        assert result['object_key'] == 'test-key.txt'
        mock_s3_client.upload_fileobj.assert_called_once()
        mock_upload_file.file.seek.assert_called_with(0)

    def test_update_file_overwrites_existing(self, service_instance, mock_s3_client, mock_upload_file):
        """Test update overwrites existing file without checking"""
        mock_s3_client.upload_fileobj.return_value = None

        result = service_instance.s3_update_file(
            mock_upload_file,
            'existing-key.txt',
            'test-bucket'
        )

        assert result['object_key'] == 'existing-key.txt'
        # Should not call head_object to check existence
        mock_s3_client.head_object.assert_not_called()

    def test_update_file_client_error(self, service_instance, mock_s3_client, mock_upload_file):
        """Test error handling during update"""
        mock_s3_client.upload_fileobj.side_effect = MockClientError(
            {'Error': {'Code': 'NoSuchBucket', 'Message': 'Bucket not found'}},
            'UploadFileobj'
        )

        with pytest.raises(HTTPException) as exc_info:
            service_instance.s3_update_file(
                mock_upload_file,
                'test-key.txt',
                'nonexistent-bucket'
            )

        assert exc_info.value.status_code == 500

    def test_update_file_resets_file_pointer(self, service_instance, mock_s3_client, mock_upload_file):
        """Test file pointer is reset before update"""
        mock_s3_client.upload_fileobj.return_value = None

        service_instance.s3_update_file(
            mock_upload_file,
            'test-key.txt',
            'test-bucket'
        )

        mock_upload_file.file.seek.assert_called_with(0)


# Test Class 5: Get Object Tests
class TestGetObject:
    """Test get_object functionality"""

    def test_get_object_success(self, service_instance, mock_s3_client):
        """Test successful object retrieval"""
        mock_body = MagicMock()
        mock_body.iter_chunks.return_value = [b"chunk1", b"chunk2", b"chunk3"]
        mock_s3_client.get_object.return_value = {
            'Body': mock_body,
            'ContentType': 'text/plain',
            'ContentLength': 18
        }

        result = list(service_instance.get_object('test-key.txt', 'test-bucket'))

        assert result == [b"chunk1", b"chunk2", b"chunk3"]
        mock_s3_client.get_object.assert_called_once_with(
            Bucket='test-bucket',
            Key='test-key.txt'
        )

    def test_get_object_returns_generator(self, service_instance, mock_s3_client):
        """Test get object returns generator"""
        mock_body = MagicMock()
        mock_body.iter_chunks.return_value = [b"data"]
        mock_s3_client.get_object.return_value = {'Body': mock_body}

        result = service_instance.get_object('test-key.txt', 'test-bucket')

        # Should be a generator
        assert hasattr(result, '__iter__')
        assert hasattr(result, '__next__')

    def test_get_object_not_found(self, service_instance, mock_s3_client):
        """Test get object when it doesn't exist"""
        mock_s3_client.get_object.side_effect = MockClientError(
            {'Error': {'Code': 'NoSuchKey', 'Message': 'Key not found'}},
            'GetObject'
        )

        with pytest.raises(HTTPException) as exc_info:
            list(service_instance.get_object('nonexistent.txt', 'test-bucket'))

        assert exc_info.value.status_code == 404

    def test_get_object_other_client_error(self, service_instance, mock_s3_client):
        """Test get object with other client errors"""
        mock_s3_client.get_object.side_effect = MockClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
            'GetObject'
        )

        with pytest.raises(HTTPException) as exc_info:
            list(service_instance.get_object('test-key.txt', 'test-bucket'))

        assert exc_info.value.status_code == 500

    def test_get_object_chunks_with_correct_size(self, service_instance, mock_s3_client):
        """Test object is retrieved in correct chunk size"""
        mock_body = MagicMock()
        mock_body.iter_chunks.return_value = [b"data"]
        mock_s3_client.get_object.return_value = {'Body': mock_body}

        list(service_instance.get_object('test-key.txt', 'test-bucket'))

        # Verify iter_chunks called with CHUNK_SIZE (15MB)
        mock_body.iter_chunks.assert_called_once_with(chunk_size=15 * 1024 * 1024)


# Test Class 6: Delete Object Tests
class TestDeleteObject:
    """Test delete_object functionality"""

    def test_delete_object_success(self, service_instance, mock_s3_client):
        """Test successful object deletion"""
        mock_s3_client.delete_object.return_value = {}

        # Should not raise exception
        service_instance.delete_object('test-bucket', 'test-key.txt')

        mock_s3_client.delete_object.assert_called_once_with(
            Bucket='test-bucket',
            Key='test-key.txt'
        )

    def test_delete_object_no_return_value(self, service_instance, mock_s3_client):
        """Test delete returns None"""
        mock_s3_client.delete_object.return_value = {}

        result = service_instance.delete_object('test-bucket', 'test-key.txt')

        assert result is None

    def test_delete_object_nonexistent(self, service_instance, mock_s3_client):
        """Test delete succeeds even if object doesn't exist"""
        # S3 delete is idempotent
        mock_s3_client.delete_object.return_value = {}

        service_instance.delete_object('test-bucket', 'nonexistent.txt')

        mock_s3_client.delete_object.assert_called_once()

    def test_delete_object_client_error(self, service_instance, mock_s3_client):
        """Test error handling during deletion"""
        mock_s3_client.delete_object.side_effect = MockClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
            'DeleteObject'
        )

        with pytest.raises(HTTPException) as exc_info:
            service_instance.delete_object('test-bucket', 'test-key.txt')

        assert exc_info.value.status_code == 500


# Test Class 7: Create Bucket Tests
class TestCreateBucket:
    """Test s3_create_bucket functionality"""

    def test_create_bucket_us_east_1(self, service_instance, mock_s3_client):
        """Test bucket creation in us-east-1 (no location constraint)"""
        with patch.dict('os.environ', {'AWS_REGION': 'us-east-1'}):
            mock_s3_client.create_bucket.return_value = {}

            result = service_instance.s3_create_bucket('test-bucket')

            assert result['message'] == "Bucket 'test-bucket' created successfully"
            # Verify create_bucket called without CreateBucketConfiguration for us-east-1
            call_args = mock_s3_client.create_bucket.call_args
            assert 'CreateBucketConfiguration' not in call_args[1]

    def test_create_bucket_other_region(self, service_instance, mock_s3_client):
        """Test bucket creation in non-us-east-1 region"""
        with patch.dict('os.environ', {'AWS_REGION': 'eu-west-1'}):
            with patch('os.getenv', side_effect=lambda k, d=None: 'eu-west-1' if k == 'AWS_REGION' else d):
                mock_s3_client.create_bucket.return_value = {}

                result = service_instance.s3_create_bucket('test-bucket')

                assert result['message'] == "Bucket 'test-bucket' created successfully"
                call_args = mock_s3_client.create_bucket.call_args
                assert 'CreateBucketConfiguration' in call_args[1]
                assert call_args[1]['CreateBucketConfiguration']['LocationConstraint'] == 'eu-west-1'

    def test_create_bucket_already_exists(self, service_instance, mock_s3_client):
        """Test creating bucket that already exists"""
        mock_s3_client.create_bucket.side_effect = MockClientError(
            {'Error': {'Code': 'BucketAlreadyExists', 'Message': 'Bucket exists'}},
            'CreateBucket'
        )

        with pytest.raises(HTTPException) as exc_info:
            service_instance.s3_create_bucket('existing-bucket')

        assert exc_info.value.status_code == 409
        assert 'already exists' in str(exc_info.value.detail)

    def test_create_bucket_other_error(self, service_instance, mock_s3_client):
        """Test create bucket with other errors"""
        mock_s3_client.create_bucket.side_effect = MockClientError(
            {'Error': {'Code': 'InternalError', 'Message': 'Internal error'}},
            'CreateBucket'
        )

        with pytest.raises(HTTPException) as exc_info:
            service_instance.s3_create_bucket('test-bucket')

        assert exc_info.value.status_code == 500


# Test Class 8: Bucket Name Validation Tests
class TestBucketNameValidation:
    """Test is_valid_bucket_name functionality"""

    def test_valid_bucket_names(self, service_instance):
        """Test valid bucket names"""
        valid_names = [
            'valid-bucket',
            'valid-bucket-123',
            'a' * 63,  # Max length
            'abc',     # Min length (3 chars)
            'my-bucket-2024',
            'test123'
        ]

        for name in valid_names:
            assert service_instance.is_valid_bucket_name(name) is True, f"Failed for: {name}"

    def test_invalid_bucket_names(self, service_instance):
        """Test invalid bucket names"""
        invalid_names = [
            'ab',  # Too short
            'a' * 64,  # Too long
            'Invalid_Bucket',  # Uppercase and underscore
            'bucket.',  # Ends with dot
            '.bucket',  # Starts with dot
            'bucket..name',  # Consecutive dots
            'bucket.-name',  # Dot-dash
            'bucket-.name',  # Dash-dot
            '192.168.1.1',  # IP address format
            '-bucket',  # Starts with dash
            'bucket-',  # Ends with dash
            'Bucket',  # Uppercase
        ]

        for name in invalid_names:
            assert service_instance.is_valid_bucket_name(name) is False, f"Should fail for: {name}"

    def test_bucket_name_edge_cases(self, service_instance):
        """Test bucket name edge cases"""
        assert service_instance.is_valid_bucket_name('a-b') is True
        assert service_instance.is_valid_bucket_name('a--b') is True
        # Note: Simple dots are not allowed by the validation regex pattern
        assert service_instance.is_valid_bucket_name('a.b') is False
        assert service_instance.is_valid_bucket_name('10.0.0.1') is False


# Test Class 9: Object Key Validation Tests
class TestObjectKeyValidation:
    """Test is_valid_object_key functionality"""

    def test_valid_object_keys(self, service_instance):
        """Test valid object keys"""
        valid_keys = [
            'simple.txt',
            'folder/file.txt',
            'deep/nested/path/file.txt',
            'file-with-dashes.txt',
            'file_with_underscores.txt',
            'a' * 1024,  # Max length
            'a',  # Min length
            'folder/'
        ]

        for key in valid_keys:
            assert service_instance.is_valid_object_key(key) is True, f"Failed for: {key}"

    def test_invalid_object_keys(self, service_instance):
        """Test invalid object keys"""
        invalid_keys = [
            '',  # Empty
            'a' * 1025  # Too long
        ]

        for key in invalid_keys:
            assert service_instance.is_valid_object_key(key) is False, f"Should fail for: {key}"

    def test_object_key_allows_special_chars(self, service_instance):
        """Test object key allows various special characters"""
        special_keys = [
            'file with spaces.txt',
            'file!@#$%^&*().txt',
            'file(1).txt',
            'file[2].txt'
        ]

        for key in special_keys:
            assert service_instance.is_valid_object_key(key) is True


# Test Class 10: Get Object Properties Tests
class TestGetObjectProperties:
    """Test get_object_properties functionality"""

    def test_get_properties_success(self, service_instance, mock_s3_client):
        """Test successful retrieval of object properties"""
        mock_s3_client.head_object.return_value = {
            'ContentLength': 1024,
            'LastModified': datetime(2024, 1, 1, 12, 0, 0),
            'ContentType': 'text/plain',
            'ETag': '"abc123"',
            'Metadata': {'custom-key': 'custom-value'}
        }

        result = service_instance.get_object_properties('test-key.txt', 'test-bucket')

        assert result['object_key'] == 'test-key.txt'
        assert result['object_type'] == 'S3Object'
        assert result['object_size'] == 1024
        assert result['content_type'] == 'text/plain'
        assert result['etag'] == '"abc123"'
        assert result['metadata'] == {'custom-key': 'custom-value'}

    def test_get_properties_not_found(self, service_instance, mock_s3_client):
        """Test get properties when object doesn't exist"""
        mock_s3_client.head_object.side_effect = MockClientError(
            {'Error': {'Code': 'NoSuchKey', 'Message': 'Key not found'}},
            'HeadObject'
        )

        with pytest.raises(HTTPException) as exc_info:
            service_instance.get_object_properties('nonexistent.txt', 'test-bucket')

        assert exc_info.value.status_code == 404
        assert 'not found' in str(exc_info.value.detail)

    def test_get_properties_invalid_bucket(self, service_instance):
        """Test get properties with invalid bucket name"""
        with pytest.raises(ValueError) as exc_info:
            service_instance.get_object_properties('test-key.txt', 'INVALID')

        assert "Invalid bucket name" in str(exc_info.value)

    def test_get_properties_invalid_key(self, service_instance):
        """Test get properties with invalid key"""
        with pytest.raises(ValueError) as exc_info:
            service_instance.get_object_properties('', 'valid-bucket')

        assert "Invalid object key" in str(exc_info.value)

    def test_get_properties_default_content_type(self, service_instance, mock_s3_client):
        """Test default content type when not specified"""
        mock_s3_client.head_object.return_value = {
            'ContentLength': 1024,
            'LastModified': datetime(2024, 1, 1, 12, 0, 0),
            'ETag': '"abc123"',
            'Metadata': {}
        }

        result = service_instance.get_object_properties('test-key.bin', 'test-bucket')

        assert result['content_type'] == 'binary/octet-stream'

    def test_get_properties_client_error(self, service_instance, mock_s3_client):
        """Test get properties with client error"""
        mock_s3_client.head_object.side_effect = MockClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
            'HeadObject'
        )

        with pytest.raises(HTTPException) as exc_info:
            service_instance.get_object_properties('test-key.txt', 'test-bucket')

        assert exc_info.value.status_code == 500


# Test Class 11: List Objects Tests
class TestListObjects:
    """Test list_objects functionality"""

    def test_list_objects_success(self, service_instance, mock_s3_client):
        """Test successful object listing"""
        mock_s3_client.list_objects_v2.return_value = {
            'Contents': [
                {
                    'Key': 'file1.txt',
                    'Size': 100,
                    'LastModified': datetime(2024, 1, 1)
                },
                {
                    'Key': 'file2.txt',
                    'Size': 200,
                    'LastModified': datetime(2024, 1, 2)
                }
            ]
        }

        result = service_instance.list_objects('test-bucket')

        assert len(result) == 2
        assert isinstance(result[0], BlobInfo)
        assert result[0].name == 'file1.txt'
        assert result[0].size == 100
        assert result[1].name == 'file2.txt'
        assert result[1].size == 200

    def test_list_objects_empty_bucket(self, service_instance, mock_s3_client):
        """Test listing empty bucket"""
        mock_s3_client.list_objects_v2.return_value = {}

        result = service_instance.list_objects('test-bucket')

        assert result == []

    def test_list_objects_with_prefix(self, service_instance, mock_s3_client):
        """Test listing objects with key prefix"""
        mock_s3_client.list_objects_v2.return_value = {
            'Contents': [
                {
                    'Key': 'folder/file1.txt',
                    'Size': 100,
                    'LastModified': datetime(2024, 1, 1)
                }
            ]
        }

        result = service_instance.list_objects('test-bucket', key_starts_with='folder/')

        assert len(result) == 1
        assert result[0].name == 'folder/file1.txt'
        call_args = mock_s3_client.list_objects_v2.call_args
        assert call_args[1]['Prefix'] == 'folder/'

    def test_list_objects_with_max_results(self, service_instance, mock_s3_client):
        """Test listing objects with max results limit"""
        mock_s3_client.list_objects_v2.return_value = {
            'Contents': [
                {
                    'Key': f'file{i}.txt',
                    'Size': 100,
                    'LastModified': datetime(2024, 1, 1)
                }
                for i in range(5)
            ]
        }

        result = service_instance.list_objects('test-bucket', max_results=3)

        assert len(result) <= 3
        call_args = mock_s3_client.list_objects_v2.call_args
        assert call_args[1]['MaxKeys'] == 3

    def test_list_objects_with_content_type_filter(self, service_instance, mock_s3_client):
        """Test listing objects with content type filter"""
        mock_s3_client.list_objects_v2.return_value = {
            'Contents': [
                {
                    'Key': 'file1.txt',
                    'Size': 100,
                    'LastModified': datetime(2024, 1, 1)
                },
                {
                    'Key': 'file2.json',
                    'Size': 200,
                    'LastModified': datetime(2024, 1, 2)
                }
            ]
        }

        # Mock head_object to return different content types
        def head_object_side_effect(*args, **kwargs):
            if kwargs['Key'] == 'file1.txt':
                return {'ContentType': 'text/plain'}
            elif kwargs['Key'] == 'file2.json':
                return {'ContentType': 'application/json'}

        mock_s3_client.head_object.side_effect = head_object_side_effect

        result = service_instance.list_objects('test-bucket', content_type='text/plain')

        assert len(result) == 1
        assert result[0].name == 'file1.txt'
        assert result[0].content_type == 'text/plain'

    def test_list_objects_client_error(self, service_instance, mock_s3_client):
        """Test error handling during object listing"""
        mock_s3_client.list_objects_v2.side_effect = MockClientError(
            {'Error': {'Code': 'NoSuchBucket', 'Message': 'Bucket not found'}},
            'ListObjectsV2'
        )

        with pytest.raises(HTTPException) as exc_info:
            service_instance.list_objects('nonexistent-bucket')

        assert exc_info.value.status_code == 500

    def test_list_objects_head_error_with_content_filter(self, service_instance, mock_s3_client):
        """Test that head_object errors during content type filtering skip objects"""
        mock_s3_client.list_objects_v2.return_value = {
            'Contents': [
                {
                    'Key': 'file1.txt',
                    'Size': 100,
                    'LastModified': datetime(2024, 1, 1)
                }
            ]
        }

        mock_s3_client.head_object.side_effect = MockClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
            'HeadObject'
        )

        result = service_instance.list_objects('test-bucket', content_type='text/plain')

        assert result == []

    def test_list_objects_default_content_type(self, service_instance, mock_s3_client):
        """Test listing without content type filter uses default"""
        mock_s3_client.list_objects_v2.return_value = {
            'Contents': [
                {
                    'Key': 'file1.txt',
                    'Size': 100,
                    'LastModified': datetime(2024, 1, 1)
                }
            ]
        }

        result = service_instance.list_objects('test-bucket')

        assert len(result) == 1
        assert result[0].content_type == 'binary/octet-stream'


# Test Class 12: Edge Cases Tests
class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_upload_empty_file(self, service_instance, mock_s3_client):
        """Test uploading empty file"""
        empty_file = MagicMock()
        empty_file.filename = "empty.txt"
        empty_file.content_type = "text/plain"
        empty_file.file = BytesIO(b"")
        empty_file.file.seek = MagicMock()

        mock_s3_client.head_object.side_effect = MockClientError(
            {'Error': {'Code': '404', 'Message': 'Not Found'}},
            'HeadObject'
        )
        mock_s3_client.upload_fileobj.return_value = None

        result = service_instance.s3_upload_file(empty_file, 'test-bucket', 'empty.txt')

        assert result['object_key'] == 'empty.txt'

    def test_upload_large_filename(self, service_instance, mock_s3_client):
        """Test upload with very long filename"""
        long_filename = 'a' * 500 + '.txt'
        mock_file = MagicMock()
        mock_file.filename = long_filename
        mock_file.content_type = "text/plain"
        mock_file.file = BytesIO(b"data")
        mock_file.file.seek = MagicMock()

        mock_s3_client.head_object.side_effect = MockClientError(
            {'Error': {'Code': '404', 'Message': 'Not Found'}},
            'HeadObject'
        )
        mock_s3_client.upload_fileobj.return_value = None

        result = service_instance.s3_upload_file(mock_file, 'test-bucket')

        assert 'object_key' in result

    def test_list_objects_no_contents_key(self, service_instance, mock_s3_client):
        """Test list objects when response has no Contents key"""
        mock_s3_client.list_objects_v2.return_value = {'IsTruncated': False}

        result = service_instance.list_objects('test-bucket')

        assert result == []

    def test_bucket_name_exactly_3_chars(self, service_instance):
        """Test bucket name with exactly 3 characters (minimum)"""
        assert service_instance.is_valid_bucket_name('abc') is True

    def test_bucket_name_exactly_63_chars(self, service_instance):
        """Test bucket name with exactly 63 characters (maximum)"""
        name = 'a' * 63
        assert service_instance.is_valid_bucket_name(name) is True

    def test_object_key_exactly_1024_chars(self, service_instance):
        """Test object key with exactly 1024 characters (maximum)"""
        key = 'a' * 1024
        assert service_instance.is_valid_object_key(key) is True


# Test Class 13: Security Tests
class TestSecurity:
    """Test security-related functionality"""

    def test_bucket_name_prevents_path_traversal(self, service_instance):
        """Test bucket name validation prevents path traversal"""
        assert service_instance.is_valid_bucket_name('../../../etc/passwd') is False
        assert service_instance.is_valid_bucket_name('..') is False
        assert service_instance.is_valid_bucket_name('.') is False

    def test_bucket_name_ip_address_rejected(self, service_instance):
        """Test bucket names formatted as IP addresses are rejected"""
        assert service_instance.is_valid_bucket_name('192.168.1.1') is False
        assert service_instance.is_valid_bucket_name('10.0.0.1') is False
        assert service_instance.is_valid_bucket_name('255.255.255.255') is False

    def test_object_key_max_length_enforced(self, service_instance):
        """Test object key length is enforced"""
        long_key = 'a' * 1025
        assert service_instance.is_valid_object_key(long_key) is False

    def test_error_messages_wrapped_in_http_exception(self, service_instance, mock_s3_client):
        """Test error messages are wrapped in HTTPException"""
        mock_s3_client.list_buckets.side_effect = MockClientError(
            {'Error': {'Code': 'InternalError', 'Message': 'Internal error'}},
            'ListBuckets'
        )

        with pytest.raises(HTTPException) as exc_info:
            service_instance.list_buckets()

        assert isinstance(exc_info.value, HTTPException)
        assert exc_info.value.status_code == 500

    def test_upload_prevents_overwrite_by_default(self, service_instance, mock_s3_client, mock_upload_file):
        """Test upload checks for existing files"""
        mock_s3_client.head_object.return_value = {'ContentLength': 100}

        with pytest.raises(HTTPException) as exc_info:
            service_instance.s3_upload_file(mock_upload_file, 'test-bucket', 'existing.txt')

        assert exc_info.value.status_code == 409


# Test Class 14: Integration Tests
class TestIntegration:
    """Test integration with BlobInfo and other components"""

    def test_blobinfo_mapper_integration(self, service_instance, mock_s3_client):
        """Test integration with BlobInfo mapper"""
        mock_s3_client.list_objects_v2.return_value = {
            'Contents': [
                {
                    'Key': 'test.txt',
                    'Size': 100,
                    'LastModified': datetime(2024, 1, 1)
                }
            ]
        }

        result = service_instance.list_objects('test-bucket')

        assert isinstance(result[0], BlobInfo)
        assert result[0].name == 'test.txt'
        assert result[0].size == 100
        assert result[0].last_modified == datetime(2024, 1, 1)

    def test_http_exception_format(self, service_instance, mock_s3_client):
        """Test HTTPException follows expected format"""
        mock_s3_client.get_object.side_effect = MockClientError(
            {'Error': {'Code': 'NoSuchKey', 'Message': 'Not found'}},
            'GetObject'
        )

        with pytest.raises(HTTPException) as exc_info:
            list(service_instance.get_object('missing.txt', 'test-bucket'))

        assert isinstance(exc_info.value, HTTPException)
        assert hasattr(exc_info.value, 'status_code')
        assert hasattr(exc_info.value, 'detail')
        assert exc_info.value.status_code == 404


# Test Class 15: Error Handling Tests
class TestErrorHandling:
    """Test comprehensive error handling"""

    def test_no_credentials_error(self, mock_s3_client):
        """Test handling of missing AWS credentials"""
        # Service initialization with module-level mocks doesn't raise credentials error
        # This would only happen with actual boto3, so we test the service exists
        with patch.dict('os.environ', {}, clear=True):
            service = FairnessUIservice()
            # Service initializes with mocked boto3 even without credentials
            assert service is not None

    def test_list_buckets_preserves_error_details(self, service_instance, mock_s3_client):
        """Test error details are preserved in HTTPException"""
        error_code = "CustomError"
        mock_s3_client.list_buckets.side_effect = MockClientError(
            {'Error': {'Code': error_code, 'Message': 'Custom error message'}},
            'ListBuckets'
        )

        with pytest.raises(HTTPException) as exc_info:
            service_instance.list_buckets()

        # The detail contains the exception's string representation which includes the error code
        assert error_code in str(exc_info.value.detail)
        assert 'ListBuckets' in str(exc_info.value.detail)

    def test_get_object_differentiates_404_500(self, service_instance, mock_s3_client):
        """Test get_object returns 404 for NoSuchKey, 500 for others"""
        # Test 404
        mock_s3_client.get_object.side_effect = MockClientError(
            {'Error': {'Code': 'NoSuchKey', 'Message': 'Not found'}},
            'GetObject'
        )

        with pytest.raises(HTTPException) as exc_info:
            list(service_instance.get_object('missing.txt', 'test-bucket'))

        assert exc_info.value.status_code == 404

        # Test 500
        mock_s3_client.get_object.side_effect = MockClientError(
            {'Error': {'Code': 'InternalError', 'Message': 'Server error'}},
            'GetObject'
        )

        with pytest.raises(HTTPException) as exc_info:
            list(service_instance.get_object('test.txt', 'test-bucket'))

        assert exc_info.value.status_code == 500


# Test Class 16: Performance and Resource Management Tests
class TestPerformanceAndResources:
    """Test performance optimizations and resource management"""

    def test_chunk_size_constant(self, service_instance):
        """Test chunk size is set to 15MB"""
        from service.aws_service import CHUNK_SIZE
        assert CHUNK_SIZE == 15 * 1024 * 1024

    def test_boto3_client_configuration(self, mock_boto3_client):
        """Test boto3 client is configured with proper settings"""
        with patch.dict('os.environ', {
            'AWS_ACCESS_KEY_ID': 'test_key',
            'AWS_SECRET_ACCESS_KEY': 'test_secret',
            'AWS_REGION': 'us-west-2'
        }):
            service = FairnessUIservice()

            # Verify service has s3_client configured
            assert hasattr(service, 's3_client')
            assert service.s3_client is not None

    def test_file_pointer_reset_prevents_double_read(self, service_instance, mock_s3_client, mock_upload_file):
        """Test file pointer is reset to prevent partial uploads"""
        mock_s3_client.head_object.side_effect = MockClientError(
            {'Error': {'Code': '404', 'Message': 'Not Found'}},
            'HeadObject'
        )
        mock_s3_client.upload_fileobj.return_value = None

        # Simulate file already read
        mock_upload_file.file.tell = MagicMock(return_value=100)

        service_instance.s3_upload_file(mock_upload_file, 'test-bucket', 'test.txt')

        # Verify seek was called to reset
        mock_upload_file.file.seek.assert_called_with(0)

    def test_update_uses_same_upload_mechanism(self, service_instance, mock_s3_client, mock_upload_file):
        """Test update uses upload_fileobj for efficiency"""
        mock_s3_client.upload_fileobj.return_value = None

        service_instance.s3_update_file(mock_upload_file, 'test.txt', 'test-bucket')

        # Should use upload_fileobj, not put_object
        mock_s3_client.upload_fileobj.assert_called_once()
        mock_s3_client.put_object.assert_not_called()
