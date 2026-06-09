import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Add src to path for imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.exception.exception import (
    aiShieldException,
    aiShieldNotFoundError,
    aiShieldNameNotEmptyError,
    UnSupportedMediaTypeException,
    validation_error_handler,
    http_exception_handler,
    unsupported_mediatype_error_handler
)
from app.constants import global_constants


# ============================================================================
# Test aiShieldException
# ============================================================================

class TestAiShieldException:
    """Test aiShieldException base class"""
    
    def test_init(self):
        """Test exception initialization"""
        detail = "Test error detail"
        exc = aiShieldException(detail)
        
        assert exc.status_code == global_constants.HTTP_STATUS_BAD_REQUEST
        assert str(exc) == detail
    
    def test_inheritance(self):
        """Test that aiShieldException inherits from Exception"""
        exc = aiShieldException("test")
        assert isinstance(exc, Exception)
    
    def test_detail_preserved(self):
        """Test that detail message is preserved"""
        detail = "Custom error message"
        exc = aiShieldException(detail)
        assert detail in str(exc)


# ============================================================================
# Test aiShieldNotFoundError
# ============================================================================

class TestAiShieldNotFoundError:
    """Test aiShieldNotFoundError exception"""
    
    def test_init(self):
        """Test exception initialization"""
        name = "TestUsecase"
        exc = aiShieldNotFoundError(name)
        
        assert exc.status_code == global_constants.HTTP_STATUS_NOT_FOUND
        assert name in exc.detail
    
    def test_inherits_from_aishield_exception(self):
        """Test inheritance from aiShieldException"""
        exc = aiShieldNotFoundError("test")
        assert isinstance(exc, aiShieldException)
        assert isinstance(exc, Exception)
    
    def test_detail_message_format(self):
        """Test that detail message is formatted correctly"""
        name = "MyUsecase"
        exc = aiShieldNotFoundError(name)
        assert isinstance(exc.detail, str)
        assert len(exc.detail) > 0
    
    def test_different_names(self):
        """Test with different usecase names"""
        names = ["Usecase1", "Test_Usecase", "Special-Usecase123"]
        for name in names:
            exc = aiShieldNotFoundError(name)
            assert exc.status_code == global_constants.HTTP_STATUS_NOT_FOUND
            assert name in exc.detail


# ============================================================================
# Test aiShieldNameNotEmptyError
# ============================================================================

class TestAiShieldNameNotEmptyError:
    """Test aiShieldNameNotEmptyError exception"""
    
    def test_init(self):
        """Test exception initialization"""
        name = "TestName"
        exc = aiShieldNameNotEmptyError(name)
        
        assert exc.status_code == global_constants.HTTP_STATUS_409_CODE
        assert exc.detail is not None
    
    def test_inherits_from_aishield_exception(self):
        """Test inheritance from aiShieldException"""
        exc = aiShieldNameNotEmptyError("test")
        assert isinstance(exc, aiShieldException)
        assert isinstance(exc, Exception)
    
    def test_detail_message(self):
        """Test that detail message is set"""
        exc = aiShieldNameNotEmptyError("any_name")
        assert isinstance(exc.detail, str)
        assert len(exc.detail) > 0
    
    def test_status_code_409(self):
        """Test that status code is 409"""
        exc = aiShieldNameNotEmptyError("test")
        assert exc.status_code == global_constants.HTTP_STATUS_409_CODE


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
    
    def test_inherits_from_exception(self):
        """Test inheritance from Exception"""
        exc = UnSupportedMediaTypeException("text/plain")
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


# ============================================================================
# Test validation_error_handler
# ============================================================================

class TestValidationErrorHandler:
    """Test validation_error_handler function"""
    
    def test_validation_error_handler(self):
        """Test validation error handler returns JSONResponse"""
        mock_exc = MagicMock(spec=RequestValidationError)
        mock_exc.errors.return_value = [{"loc": ["body", "field"], "msg": "field required", "type": "value_error.missing"}]
        
        response = validation_error_handler(mock_exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == int(global_constants.HTTP_422_UNPROCESSABLE_ENTITY)
    
    def test_validation_error_handler_content(self):
        """Test validation error handler response content"""
        mock_exc = MagicMock(spec=RequestValidationError)
        errors = [{"loc": ["body", "email"], "msg": "invalid email", "type": "value_error.email"}]
        mock_exc.errors.return_value = errors
        
        response = validation_error_handler(mock_exc)
        
        assert response.status_code == int(global_constants.HTTP_422_UNPROCESSABLE_ENTITY)
        assert mock_exc.errors.called
    
    def test_validation_error_handler_multiple_errors(self):
        """Test validation error handler with multiple errors"""
        mock_exc = MagicMock(spec=RequestValidationError)
        errors = [
            {"loc": ["body", "name"], "msg": "field required", "type": "value_error.missing"},
            {"loc": ["body", "age"], "msg": "not a valid integer", "type": "type_error.integer"}
        ]
        mock_exc.errors.return_value = errors
        
        response = validation_error_handler(mock_exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == int(global_constants.HTTP_422_UNPROCESSABLE_ENTITY)


# ============================================================================
# Test http_exception_handler
# ============================================================================

class TestHttpExceptionHandler:
    """Test http_exception_handler function"""
    
    def test_http_exception_handler(self):
        """Test http exception handler returns JSONResponse"""
        mock_exc = MagicMock()
        mock_exc.status_code = 400
        mock_exc.detail = "Bad request"
        
        response = http_exception_handler(mock_exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
    
    def test_http_exception_handler_different_status_codes(self):
        """Test http exception handler with different status codes"""
        status_codes = [400, 401, 403, 404, 500]
        
        for status_code in status_codes:
            mock_exc = MagicMock()
            mock_exc.status_code = status_code
            mock_exc.detail = f"Error {status_code}"
            
            response = http_exception_handler(mock_exc)
            
            assert response.status_code == status_code
    
    def test_http_exception_handler_detail_message(self):
        """Test http exception handler preserves detail message"""
        mock_exc = MagicMock()
        mock_exc.status_code = 404
        mock_exc.detail = "Resource not found"
        
        response = http_exception_handler(mock_exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 404


# ============================================================================
# Test unsupported_mediatype_error_handler
# ============================================================================

class TestUnsupportedMediatypeErrorHandler:
    """Test unsupported_mediatype_error_handler function"""
    
    def test_unsupported_mediatype_error_handler(self):
        """Test unsupported media type error handler returns JSONResponse"""
        exc = UnSupportedMediaTypeException("text/xml")
        
        response = unsupported_mediatype_error_handler(exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == global_constants.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    
    def test_unsupported_mediatype_error_handler_message(self):
        """Test unsupported media type error handler preserves message"""
        content_type = "application/custom"
        exc = UnSupportedMediaTypeException(content_type)
        
        response = unsupported_mediatype_error_handler(exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == global_constants.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    
    def test_unsupported_mediatype_error_handler_different_types(self):
        """Test unsupported media type error handler with different content types"""
        content_types = ["text/html", "image/jpeg", "video/mp4", "application/pdf"]
        
        for ct in content_types:
            exc = UnSupportedMediaTypeException(ct)
            response = unsupported_mediatype_error_handler(exc)
            
            assert isinstance(response, JSONResponse)
            assert response.status_code == global_constants.HTTP_415_UNSUPPORTED_MEDIA_TYPE
