import sys
import os
import pytest

# Add src to path for imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

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


# ============================================================================
# Test AicloudException
# ============================================================================

class TestAicloudException:
    """Test AicloudException base class"""
    
    def test_init(self):
        """Test exception initialization"""
        message = "Test error message"
        exc = AicloudException(message)
        assert str(exc) == message
    
    def test_inheritance(self):
        """Test that AicloudException inherits from Exception"""
        exc = AicloudException("test")
        assert isinstance(exc, Exception)
    
    def test_message_preserved(self):
        """Test that message is preserved"""
        message = "Custom error message"
        exc = AicloudException(message)
        assert message in str(exc)


# ============================================================================
# Test DbConnectionError
# ============================================================================

class TestDbConnectionError:
    """Test DbConnectionError exception"""
    
    def test_init(self):
        """Test exception initialization"""
        name = "TestDB"
        exc = DbConnectionError(name)
        
        assert exc.status_code == global_constants.HTTP_STATUS_SERVICE_UNAVAILBLE
        assert name in exc.message
    
    def test_inherits_from_aicloud_exception(self):
        """Test inheritance from AicloudException"""
        exc = DbConnectionError("test")
        assert isinstance(exc, AicloudException)
        assert isinstance(exc, Exception)
    
    def test_message_format(self):
        """Test that message includes database name"""
        name = "PostgreSQL"
        exc = DbConnectionError(name)
        assert isinstance(exc.message, str)
        assert name in exc.message


# ============================================================================
# Test DataError
# ============================================================================

class TestDataError:
    """Test DataError exception"""
    
    def test_init_with_message(self):
        """Test exception initialization with custom message"""
        msg = "Custom data error"
        exc = DataError(msg)
        
        assert exc.status_code == global_constants.HTTP_STATUS_DATA_PROCESSING_ERROR
        assert exc.message == msg
    
    def test_init_without_message(self):
        """Test exception initialization without message"""
        exc = DataError(None)
        
        assert exc.status_code == global_constants.HTTP_STATUS_DATA_PROCESSING_ERROR
        assert exc.message == global_constants.DATA_ERROR
    
    def test_init_empty_message(self):
        """Test exception initialization with empty message"""
        exc = DataError("")
        
        assert exc.message == global_constants.DATA_ERROR
    
    def test_inherits_from_aicloud_exception(self):
        """Test inheritance from AicloudException"""
        exc = DataError("test")
        assert isinstance(exc, AicloudException)


# ============================================================================
# Test OperationalError
# ============================================================================

class TestOperationalError:
    """Test OperationalError exception"""
    
    def test_init_with_message(self):
        """Test exception initialization with custom message"""
        msg = "Custom operational error"
        exc = OperationalError(msg)
        
        assert exc.status_code == global_constants.HTTP_STATUS_SERVICE_UNAVAILBLE
        assert exc.message == msg
    
    def test_init_without_message(self):
        """Test exception initialization without message"""
        exc = OperationalError(None)
        
        assert exc.status_code == global_constants.HTTP_STATUS_SERVICE_UNAVAILBLE
        assert exc.message == global_constants.OPERATIONAL_ERROR
    
    def test_init_empty_message(self):
        """Test exception initialization with empty message"""
        exc = OperationalError("")
        
        assert exc.message == global_constants.OPERATIONAL_ERROR
    
    def test_inherits_from_aicloud_exception(self):
        """Test inheritance from AicloudException"""
        exc = OperationalError("test")
        assert isinstance(exc, AicloudException)


# ============================================================================
# Test IntegrityError
# ============================================================================

class TestIntegrityError:
    """Test IntegrityError exception"""
    
    def test_init_with_message(self):
        """Test exception initialization with custom message"""
        msg = "Custom integrity error"
        exc = IntegrityError(msg)
        
        assert exc.status_code == global_constants.HTTP_STATUS_SERVICE_UNAVAILBLE
        assert exc.message == msg
    
    def test_init_without_message(self):
        """Test exception initialization without message"""
        exc = IntegrityError(None)
        
        assert exc.status_code == global_constants.HTTP_STATUS_SERVICE_UNAVAILBLE
        assert exc.message == global_constants.OPERATIONAL_ERROR
    
    def test_init_empty_message(self):
        """Test exception initialization with empty message"""
        exc = IntegrityError("")
        
        assert exc.message == global_constants.OPERATIONAL_ERROR
    
    def test_inherits_from_aicloud_exception(self):
        """Test inheritance from AicloudException"""
        exc = IntegrityError("test")
        assert isinstance(exc, AicloudException)


# ============================================================================
# Test InternalError
# ============================================================================

class TestInternalError:
    """Test InternalError exception"""
    
    def test_init_with_message(self):
        """Test exception initialization with custom message"""
        msg = "Custom internal error"
        exc = InternalError(msg)
        
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == msg
    
    def test_init_without_message(self):
        """Test exception initialization without message"""
        exc = InternalError(None)
        
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == global_constants.DATA_ERROR
    
    def test_init_empty_message(self):
        """Test exception initialization with empty message"""
        exc = InternalError("")
        
        assert exc.message == global_constants.DATA_ERROR
    
    def test_inherits_from_aicloud_exception(self):
        """Test inheritance from AicloudException"""
        exc = InternalError("test")
        assert isinstance(exc, AicloudException)


# ============================================================================
# Test NotSupportedError
# ============================================================================

class TestNotSupportedError:
    """Test NotSupportedError exception"""
    
    def test_init_with_message(self):
        """Test exception initialization with custom message"""
        msg = "Custom not supported error"
        exc = NotSupportedError(msg)
        
        assert exc.status_code == global_constants.HTTP_STATUS_NOT_ALLLOWED
        assert exc.message == msg
    
    def test_init_without_message(self):
        """Test exception initialization without message"""
        exc = NotSupportedError(None)
        
        assert exc.status_code == global_constants.HTTP_STATUS_NOT_ALLLOWED
        assert exc.message == global_constants.NOT_ALLOWED_MESSAGE
    
    def test_init_empty_message(self):
        """Test exception initialization with empty message"""
        exc = NotSupportedError("")
        
        assert exc.message == global_constants.NOT_ALLOWED_MESSAGE
    
    def test_inherits_from_aicloud_exception(self):
        """Test inheritance from AicloudException"""
        exc = NotSupportedError("test")
        assert isinstance(exc, AicloudException)


# ============================================================================
# Test DatabaseError
# ============================================================================

class TestDatabaseError:
    """Test DatabaseError exception"""
    
    def test_init(self):
        """Test exception initialization"""
        name = "TestDB"
        exc = DatabaseError(name)
        
        assert exc.status_code == global_constants.HTTP_STATUS_NOT_FOUND
        assert name in exc.message
    
    def test_inherits_from_aicloud_exception(self):
        """Test inheritance from AicloudException"""
        exc = DatabaseError("test")
        assert isinstance(exc, AicloudException)
    
    def test_message_format(self):
        """Test that message includes database name"""
        name = "MyDatabase"
        exc = DatabaseError(name)
        assert isinstance(exc.message, str)
        assert name in exc.message


# ============================================================================
# Test InternalServerError
# ============================================================================

class TestInternalServerError:
    """Test InternalServerError exception"""
    
    def test_init_with_message(self):
        """Test exception initialization with custom message"""
        msg = "Custom internal server error"
        exc = InternalServerError(msg)
        
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == msg
    
    def test_init_without_message(self):
        """Test exception initialization without message"""
        exc = InternalServerError(None)
        
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == global_constants.DATA_ERROR
    
    def test_init_empty_message(self):
        """Test exception initialization with empty message"""
        exc = InternalServerError("")
        
        assert exc.message == global_constants.DATA_ERROR
    
    def test_inherits_from_aicloud_exception(self):
        """Test inheritance from AicloudException"""
        exc = InternalServerError("test")
        assert isinstance(exc, AicloudException)


# ============================================================================
# Test IncompleteRead
# ============================================================================

class TestIncompleteRead:
    """Test IncompleteRead exception"""
    
    def test_init_with_message(self):
        """Test exception initialization with custom message"""
        msg = "Custom incomplete read error"
        exc = IncompleteRead(msg)
        
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == msg
    
    def test_init_without_message(self):
        """Test exception initialization without message"""
        exc = IncompleteRead(None)
        
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == global_constants.DATA_ERROR
    
    def test_init_empty_message(self):
        """Test exception initialization with empty message"""
        exc = IncompleteRead("")
        
        assert exc.message == global_constants.DATA_ERROR
    
    def test_inherits_from_aicloud_exception(self):
        """Test inheritance from AicloudException"""
        exc = IncompleteRead("test")
        assert isinstance(exc, AicloudException)


# ============================================================================
# Test MethodArgumentNotValidException
# ============================================================================

class TestMethodArgumentNotValidException:
    """Test MethodArgumentNotValidException exception"""
    
    def test_init_with_message(self):
        """Test exception initialization with custom message"""
        msg = "Custom method argument error"
        exc = MethodArgumentNotValidException(msg)
        
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == msg
    
    def test_init_without_message(self):
        """Test exception initialization without message"""
        exc = MethodArgumentNotValidException(None)
        
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert exc.message == global_constants.DATA_ERROR
    
    def test_init_empty_message(self):
        """Test exception initialization with empty message"""
        exc = MethodArgumentNotValidException("")
        
        assert exc.message == global_constants.DATA_ERROR
    
    def test_inherits_from_aicloud_exception(self):
        """Test inheritance from AicloudException"""
        exc = MethodArgumentNotValidException("test")
        assert isinstance(exc, AicloudException)


# ============================================================================
# Test UnSupportedMediaTypeException
# ============================================================================

class TestUnSupportedMediaTypeException:
    """Test UnSupportedMediaTypeException exception"""
    
    def test_init(self):
        """Test exception initialization"""
        content_type = "application/xml"
        exc = UnSupportedMediaTypeException(content_type)
        
        assert exc.status_code == global_constants.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        assert content_type in exc.message
    
    def test_inherits_from_aicloud_exception(self):
        """Test inheritance from AicloudException"""
        exc = UnSupportedMediaTypeException("text/plain")
        assert isinstance(exc, AicloudException)
        assert isinstance(exc, Exception)
    
    def test_message_format(self):
        """Test that message includes content type"""
        content_type = "application/octet-stream"
        exc = UnSupportedMediaTypeException(content_type)
        assert isinstance(exc.message, str)
        assert content_type in exc.message
    
    def test_different_content_types(self):
        """Test with different content types"""
        content_types = ["text/html", "application/xml", "image/png", "text/plain"]
        for ct in content_types:
            exc = UnSupportedMediaTypeException(ct)
            assert ct in exc.message
            assert exc.status_code == global_constants.HTTP_415_UNSUPPORTED_MEDIA_TYPE
