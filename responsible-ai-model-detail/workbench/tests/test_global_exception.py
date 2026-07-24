"""
Unit tests for global_exception module.
"""

import pytest
import os
import sys
from unittest.mock import patch, Mock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app.exception.global_exception import (
    AicloudException,
    DbConnectionError,
    DataError,
    OperationalError,
    IntegrityError,
    InternalError,
    NotSupportedError,
    DatabaseError,
    ForbiddenError,
    InternalServerError,
    IncompleteRead,
    MethodArgumentNotValidException,
    UnSupportedMediaTypeException
)
from app.constants import global_constants


class TestAicloudException:
    """Tests for AicloudException base class."""
    
    def test_aicloud_exception_initialization(self):
        message = "Test exception message"
        exc = AicloudException(message)
        
        assert str(exc) == message
        assert isinstance(exc, Exception)
    
    def test_aicloud_exception_with_empty_message(self):
        message = ""
        exc = AicloudException(message)
        
        assert str(exc) == message
    
    def test_aicloud_exception_with_long_message(self):
        message = "Error " * 100
        exc = AicloudException(message)
        
        assert str(exc) == message
    
    def test_aicloud_exception_can_be_raised(self):
        with pytest.raises(AicloudException) as exc_info:
            raise AicloudException("Test error")
        
        assert "Test error" in str(exc_info.value)


class TestDbConnectionError:
    """Tests for DbConnectionError exception."""
    
    def test_db_connection_error_initialization(self):
        name = "mongodb://localhost:27017"
        exc = DbConnectionError(name)
        
        assert exc.status_code == global_constants.HTTP_STATUS_SERVICE_UNAVAILBLE
        assert hasattr(exc, 'message')
        assert isinstance(exc, AicloudException)
    
    def test_db_connection_error_with_empty_name(self):
        exc = DbConnectionError("")
        
        assert exc.status_code == global_constants.HTTP_STATUS_SERVICE_UNAVAILBLE
        assert hasattr(exc, 'message')
    
    def test_db_connection_error_can_be_raised(self):
        with pytest.raises(DbConnectionError) as exc_info:
            raise DbConnectionError("postgres://localhost")
        
        assert exc_info.value.status_code == global_constants.HTTP_STATUS_SERVICE_UNAVAILBLE
    
    def test_db_connection_error_with_special_chars(self):
        name = "mongodb://user:pass@host:27017"
        exc = DbConnectionError(name)
        
        assert hasattr(exc, 'message')


class TestDataError:
    """Tests for DataError exception."""
    
    def test_data_error_with_message(self):
        msg = "Invalid data format"
        exc = DataError(msg)
        
        assert exc.status_code == global_constants.HTTP_STATUS_DATA_PROCESSING_ERROR
        assert exc.message == msg
        assert isinstance(exc, AicloudException)
    
    def test_data_error_with_none_message(self):
        exc = DataError(None)
        
        assert exc.status_code == global_constants.HTTP_STATUS_DATA_PROCESSING_ERROR
        assert exc.message == global_constants.DATA_ERROR
    
    def test_data_error_with_empty_string(self):
        exc = DataError("")
        
        assert exc.status_code == global_constants.HTTP_STATUS_DATA_PROCESSING_ERROR
        assert exc.message == global_constants.DATA_ERROR
    
    def test_data_error_can_be_raised(self):
        with pytest.raises(DataError) as exc_info:
            raise DataError("Custom data error")
        
        assert exc_info.value.message == "Custom data error"


class TestOperationalError:
    """Tests for OperationalError exception."""
    
    def test_operational_error_with_message(self):
        msg = "Database operation failed"
        exc = OperationalError(msg)
        
        assert exc.status_code == global_constants.HTTP_STATUS_SERVICE_UNAVAILBLE
        assert exc.message == msg
    
    def test_operational_error_with_none_message(self):
        exc = OperationalError(None)
        
        assert exc.status_code == global_constants.HTTP_STATUS_SERVICE_UNAVAILBLE
        assert exc.message == global_constants.OPERATIONAL_ERROR
    
    def test_operational_error_with_empty_string(self):
        exc = OperationalError("")
        
        assert exc.status_code == global_constants.HTTP_STATUS_SERVICE_UNAVAILBLE
        assert exc.message == global_constants.OPERATIONAL_ERROR
    
    def test_operational_error_can_be_raised(self):
        with pytest.raises(OperationalError):
            raise OperationalError("Operation failed")


class TestIntegrityError:
    """Tests for IntegrityError exception."""
    
    def test_integrity_error_with_message(self):
        msg = "Unique constraint violation"
        exc = IntegrityError(msg)
        
        assert exc.status_code == global_constants.HTTP_STATUS_SERVICE_UNAVAILBLE
        assert exc.message == msg
    
    def test_integrity_error_with_none_message(self):
        exc = IntegrityError(None)
        
        assert exc.status_code == global_constants.HTTP_STATUS_SERVICE_UNAVAILBLE
        assert exc.message == global_constants.OPERATIONAL_ERROR
    
    def test_integrity_error_with_empty_string(self):
        exc = IntegrityError("")
        
        assert exc.status_code == global_constants.HTTP_STATUS_SERVICE_UNAVAILBLE
        assert exc.message == global_constants.OPERATIONAL_ERROR
    
    def test_integrity_error_can_be_raised(self):
        with pytest.raises(IntegrityError):
            raise IntegrityError("Integrity check failed")


class TestInternalError:
    """Tests for InternalError exception."""
    
    def test_internal_error_with_message(self):
        msg = "Internal server error occurred"
        exc = InternalError(msg)
        
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == msg
    
    def test_internal_error_with_none_message(self):
        exc = InternalError(None)
        
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == global_constants.DATA_ERROR
    
    def test_internal_error_with_empty_string(self):
        exc = InternalError("")
        
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == global_constants.DATA_ERROR
    
    def test_internal_error_can_be_raised(self):
        with pytest.raises(InternalError):
            raise InternalError("Internal processing error")


class TestNotSupportedError:
    """Tests for NotSupportedError exception."""
    
    def test_not_supported_error_with_message(self):
        msg = "Operation not supported"
        exc = NotSupportedError(msg)
        
        assert exc.status_code == global_constants.HTTP_STATUS_NOT_ALLLOWED
        assert exc.message == msg
    
    def test_not_supported_error_with_none_message(self):
        exc = NotSupportedError(None)
        
        assert exc.status_code == global_constants.HTTP_STATUS_NOT_ALLLOWED
        assert exc.message == global_constants.NOT_ALLOWED_MESSAGE
    
    def test_not_supported_error_with_empty_string(self):
        exc = NotSupportedError("")
        
        assert exc.status_code == global_constants.HTTP_STATUS_NOT_ALLLOWED
        assert exc.message == global_constants.NOT_ALLOWED_MESSAGE
    
    def test_not_supported_error_can_be_raised(self):
        with pytest.raises(NotSupportedError):
            raise NotSupportedError("Feature not supported")


class TestDatabaseError:
    """Tests for DatabaseError exception."""
    
    def test_database_error_initialization(self):
        name = "users_table"
        exc = DatabaseError(name)
        
        assert exc.status_code == global_constants.HTTP_STATUS_NOT_FOUND
        assert hasattr(exc, 'message')
        assert name in exc.message
    
    def test_database_error_with_empty_name(self):
        exc = DatabaseError("")
        
        assert exc.status_code == global_constants.HTTP_STATUS_NOT_FOUND
        assert hasattr(exc, 'message')
    
    def test_database_error_can_be_raised(self):
        with pytest.raises(DatabaseError):
            raise DatabaseError("test_db")


class TestForbiddenError:
    """Tests for ForbiddenError exception."""
    
    @patch('app.exception.global_exception.global_constants')
    def test_forbidden_error_with_message(self, mock_constants):
        mock_constants.HTTP_STATUS_FORBIDDEN = 403
        msg = "Access forbidden"
        exc = ForbiddenError(msg)
        
        assert exc.status_code == 403
        assert exc.message == msg
    
    @patch('app.exception.global_exception.global_constants')
    def test_forbidden_error_with_none_message(self, mock_constants):
        mock_constants.HTTP_STATUS_FORBIDDEN = 403
        mock_constants.FORBIDDEN_ERROR_MESSAGE = "Forbidden"
        exc = ForbiddenError(None)
        
        assert exc.status_code == 403
        assert exc.message == "Forbidden"
    
    @patch('app.exception.global_exception.global_constants')
    def test_forbidden_error_with_empty_string(self, mock_constants):
        mock_constants.HTTP_STATUS_FORBIDDEN = 403
        mock_constants.FORBIDDEN_ERROR_MESSAGE = "Forbidden"
        exc = ForbiddenError("")
        
        assert exc.status_code == 403
        assert exc.message == "Forbidden"
    
    @patch('app.exception.global_exception.global_constants')
    def test_forbidden_error_can_be_raised(self, mock_constants):
        mock_constants.HTTP_STATUS_FORBIDDEN = 403
        with pytest.raises(ForbiddenError):
            raise ForbiddenError("User not authorized")


class TestInternalServerError:
    """Tests for InternalServerError exception."""
    
    def test_internal_server_error_with_message(self):
        msg = "Server error occurred"
        exc = InternalServerError(msg)
        
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == msg
    
    def test_internal_server_error_with_none_message(self):
        exc = InternalServerError(None)
        
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == global_constants.DATA_ERROR
    
    def test_internal_server_error_with_empty_string(self):
        exc = InternalServerError("")
        
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == global_constants.DATA_ERROR
    
    def test_internal_server_error_can_be_raised(self):
        with pytest.raises(InternalServerError):
            raise InternalServerError("Server crashed")


class TestIncompleteRead:
    """Tests for IncompleteRead exception."""
    
    def test_incomplete_read_with_message(self):
        msg = "Read operation incomplete"
        exc = IncompleteRead(msg)
        
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == msg
    
    def test_incomplete_read_with_none_message(self):
        exc = IncompleteRead(None)
        
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == global_constants.DATA_ERROR
    
    def test_incomplete_read_with_empty_string(self):
        exc = IncompleteRead("")
        
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == global_constants.DATA_ERROR
    
    def test_incomplete_read_can_be_raised(self):
        with pytest.raises(IncompleteRead):
            raise IncompleteRead("Connection dropped")


class TestMethodArgumentNotValidException:
    """Tests for MethodArgumentNotValidException exception."""
    
    def test_method_argument_not_valid_with_message(self):
        msg = "Invalid argument provided"
        exc = MethodArgumentNotValidException(msg)
        
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == msg
    
    def test_method_argument_not_valid_with_none_message(self):
        exc = MethodArgumentNotValidException(None)
        
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == global_constants.DATA_ERROR
    
    def test_method_argument_not_valid_with_empty_string(self):
        exc = MethodArgumentNotValidException("")
        
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == global_constants.DATA_ERROR
    
    def test_method_argument_not_valid_can_be_raised(self):
        with pytest.raises(MethodArgumentNotValidException):
            raise MethodArgumentNotValidException("Argument validation failed")


class TestUnSupportedMediaTypeException:
    """Tests for UnSupportedMediaTypeException exception."""
    
    def test_unsupported_media_type_initialization(self):
        content_type = "application/xml"
        exc = UnSupportedMediaTypeException(content_type)
        
        assert exc.status_code == global_constants.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        assert hasattr(exc, 'message')
        assert content_type in exc.message
    
    def test_unsupported_media_type_with_empty_string(self):
        exc = UnSupportedMediaTypeException("")
        
        assert exc.status_code == global_constants.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        assert hasattr(exc, 'message')
    
    def test_unsupported_media_type_can_be_raised(self):
        with pytest.raises(UnSupportedMediaTypeException):
            raise UnSupportedMediaTypeException("text/plain")
    
    def test_unsupported_media_type_with_various_types(self):
        types = ["image/png", "video/mp4", "text/csv", "application/pdf"]
        
        for content_type in types:
            exc = UnSupportedMediaTypeException(content_type)
            assert content_type in exc.message


class TestExceptionInheritance:
    """Test exception inheritance hierarchy."""
    
    @patch('app.exception.global_exception.global_constants')
    def test_all_exceptions_inherit_from_aicloud_exception(self, mock_constants):
        # Set up mock constants
        mock_constants.HTTP_STATUS_SERVICE_UNAVAILBLE = 503
        mock_constants.HTTP_STATUS_DATA_PROCESSING_ERROR = 500
        mock_constants.HTTP_STATUS_BAD_REQUEST = 400
        mock_constants.HTTP_STATUS_NOT_ALLLOWED = 405
        mock_constants.HTTP_STATUS_NOT_FOUND = 404
        mock_constants.HTTP_STATUS_FORBIDDEN = 403
        mock_constants.HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415
        mock_constants.DATA_ERROR = "Data Error"
        mock_constants.OPERATIONAL_ERROR = "Operational Error"
        mock_constants.NOT_ALLOWED_MESSAGE = "Not Allowed"
        mock_constants.DATABASE_ERROR = " not found"
        mock_constants.FORBIDDEN_ERROR_MESSAGE = "Forbidden"
        mock_constants.UNSUPPPORTED_MEDIA_TYPE_ERROR = "Unsupported: "
        
        exceptions = [
            DbConnectionError("test"),
            DataError("test"),
            OperationalError("test"),
            IntegrityError("test"),
            InternalError("test"),
            NotSupportedError("test"),
            DatabaseError("test"),
            ForbiddenError("test"),
            InternalServerError("test"),
            IncompleteRead("test"),
            MethodArgumentNotValidException("test"),
            UnSupportedMediaTypeException("test")
        ]
        
        for exc in exceptions:
            assert isinstance(exc, AicloudException)
            assert isinstance(exc, Exception)
    
    @patch('app.exception.global_exception.global_constants')
    def test_exception_can_be_caught_by_base_class(self, mock_constants):
        mock_constants.HTTP_STATUS_DATA_PROCESSING_ERROR = 500
        mock_constants.HTTP_STATUS_SERVICE_UNAVAILBLE = 503
        mock_constants.DATA_ERROR = "Data Error"
        
        with pytest.raises(AicloudException):
            raise DataError("test")
        
        with pytest.raises(AicloudException):
            raise DbConnectionError("test")
    
    @patch('app.exception.global_exception.global_constants')
    def test_all_exceptions_have_status_code_or_message(self, mock_constants):
        # Set up mock constants
        mock_constants.HTTP_STATUS_SERVICE_UNAVAILBLE = 503
        mock_constants.HTTP_STATUS_DATA_PROCESSING_ERROR = 500
        mock_constants.HTTP_STATUS_BAD_REQUEST = 400
        mock_constants.HTTP_STATUS_NOT_ALLLOWED = 405
        mock_constants.HTTP_STATUS_NOT_FOUND = 404
        mock_constants.HTTP_STATUS_FORBIDDEN = 403
        mock_constants.HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415
        mock_constants.DATA_ERROR = "Data Error"
        mock_constants.OPERATIONAL_ERROR = "Operational Error"
        mock_constants.NOT_ALLOWED_MESSAGE = "Not Allowed"
        mock_constants.DATABASE_ERROR = " not found"
        mock_constants.FORBIDDEN_ERROR_MESSAGE = "Forbidden"
        mock_constants.UNSUPPPORTED_MEDIA_TYPE_ERROR = "Unsupported: "
        
        exceptions = [
            DbConnectionError("test"),
            DataError("test"),
            OperationalError("test"),
            IntegrityError("test"),
            InternalError("test"),
            NotSupportedError("test"),
            DatabaseError("test"),
            ForbiddenError("test"),
            InternalServerError("test"),
            IncompleteRead("test"),
            MethodArgumentNotValidException("test"),
            UnSupportedMediaTypeException("test")
        ]
        
        for exc in exceptions:
            assert hasattr(exc, 'status_code') or hasattr(exc, 'message')
