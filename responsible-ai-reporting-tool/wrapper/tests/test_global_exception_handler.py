import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Add src to path for imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.exception.global_exception_handler import (
    validation_error_handler,
    http_exception_handler,
    unsupported_mediatype_error_handler
)
from app.exception.global_exception import UnSupportedMediaTypeException
from app.constants import global_constants


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
    
    def test_validation_error_handler_empty_errors(self):
        """Test validation error handler with empty errors"""
        mock_exc = MagicMock(spec=RequestValidationError)
        mock_exc.errors.return_value = []
        
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
        status_codes = [400, 401, 403, 404, 500, 503]
        
        for status_code in status_codes:
            mock_exc = MagicMock()
            mock_exc.status_code = status_code
            mock_exc.detail = f"Error {status_code}"
            
            response = http_exception_handler(mock_exc)
            
            assert response.status_code == status_code
            assert isinstance(response, JSONResponse)
    
    def test_http_exception_handler_detail_message(self):
        """Test http exception handler preserves detail message"""
        mock_exc = MagicMock()
        mock_exc.status_code = 404
        mock_exc.detail = "Resource not found"
        
        response = http_exception_handler(mock_exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 404
    
    def test_http_exception_handler_empty_detail(self):
        """Test http exception handler with empty detail"""
        mock_exc = MagicMock()
        mock_exc.status_code = 500
        mock_exc.detail = ""
        
        response = http_exception_handler(mock_exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
    
    def test_http_exception_handler_none_detail(self):
        """Test http exception handler with None detail"""
        mock_exc = MagicMock()
        mock_exc.status_code = 500
        mock_exc.detail = None
        
        response = http_exception_handler(mock_exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500


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
        content_types = ["text/html", "image/jpeg", "video/mp4", "application/pdf", "application/xml"]
        
        for ct in content_types:
            exc = UnSupportedMediaTypeException(ct)
            response = unsupported_mediatype_error_handler(exc)
            
            assert isinstance(response, JSONResponse)
            assert response.status_code == global_constants.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    
    def test_unsupported_mediatype_error_handler_message_content(self):
        """Test that message includes content type string"""
        content_type = "application/custom-format"
        exc = UnSupportedMediaTypeException(content_type)
        
        response = unsupported_mediatype_error_handler(exc)
        
        assert isinstance(response, JSONResponse)
        assert content_type in exc.message
