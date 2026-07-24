"""
Unit tests for exception module
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException


class TestUnSupportedMediaTypeException:
    """Tests for UnSupportedMediaTypeException"""

    def test_unsupported_media_type_exception_creation(self):
        """Test creating UnSupportedMediaTypeException"""
        from rai_backend.exception.exception import UnSupportedMediaTypeException
        
        exc = UnSupportedMediaTypeException("application/xml")
        
        assert exc.status_code == 415
        assert "application/xml" in exc.message

    def test_unsupported_media_type_exception_with_different_content_type(self):
        """Test exception with different content type"""
        from rai_backend.exception.exception import UnSupportedMediaTypeException
        
        exc = UnSupportedMediaTypeException("text/plain")
        
        assert exc.status_code == 415
        assert "text/plain" in exc.message


class TestValidationErrorHandler:
    """Tests for validation_error_handler"""

    def test_validation_error_handler_returns_json_response(self):
        """Test validation_error_handler returns proper JSONResponse"""
        from rai_backend.exception.exception import validation_error_handler
        from fastapi.exceptions import RequestValidationError
        from pydantic import ValidationError
        
        # Create a mock validation error
        mock_errors = [
            {
                'loc': ('body', 'email'),
                'msg': 'field required',
                'type': 'value_error.missing'
            }
        ]
        
        # Create a mock RequestValidationError
        mock_exc = MagicMock(spec=RequestValidationError)
        mock_exc.errors.return_value = mock_errors
        
        response = validation_error_handler(mock_exc)
        
        assert response.status_code == 422
        assert response.body is not None

    def test_validation_error_handler_with_multiple_errors(self):
        """Test validation error handler with multiple validation errors"""
        from rai_backend.exception.exception import validation_error_handler
        
        mock_errors = [
            {'loc': ('body', 'email'), 'msg': 'field required'},
            {'loc': ('body', 'password'), 'msg': 'field required'}
        ]
        
        mock_exc = MagicMock(spec=RequestValidationError)
        mock_exc.errors.return_value = mock_errors
        
        response = validation_error_handler(mock_exc)
        
        assert response.status_code == 422


class TestHttpExceptionHandler:
    """Tests for http_exception_handler"""

    def test_http_exception_handler_404(self):
        """Test http_exception_handler with 404 error"""
        from rai_backend.exception.exception import http_exception_handler
        from starlette.exceptions import HTTPException
        
        exc = HTTPException(status_code=404, detail="Not found")
        
        response = http_exception_handler(exc)
        
        assert response.status_code == 404
        assert response.body is not None

    def test_http_exception_handler_401(self):
        """Test http_exception_handler with 401 error"""
        from rai_backend.exception.exception import http_exception_handler
        from starlette.exceptions import HTTPException
        
        exc = HTTPException(status_code=401, detail="Unauthorized")
        
        response = http_exception_handler(exc)
        
        assert response.status_code == 401

    def test_http_exception_handler_500(self):
        """Test http_exception_handler with 500 error"""
        from rai_backend.exception.exception import http_exception_handler
        from starlette.exceptions import HTTPException
        
        exc = HTTPException(status_code=500, detail="Internal Server Error")
        
        response = http_exception_handler(exc)
        
        assert response.status_code == 500


class TestUnsupportedMediaTypeErrorHandler:
    """Tests for unsupported_mediatype_error_handler"""

    def test_unsupported_mediatype_error_handler(self):
        """Test unsupported_mediatype_error_handler returns proper response"""
        from rai_backend.exception.exception import (
            unsupported_mediatype_error_handler,
            UnSupportedMediaTypeException
        )
        
        exc = UnSupportedMediaTypeException("application/xml")
        
        response = unsupported_mediatype_error_handler(exc)
        
        assert response.status_code == 415
        assert response.body is not None

    def test_unsupported_mediatype_error_handler_with_different_types(self):
        """Test handler with different media types"""
        from rai_backend.exception.exception import (
            unsupported_mediatype_error_handler,
            UnSupportedMediaTypeException
        )
        
        for content_type in ["text/plain", "application/xml", "text/html"]:
            exc = UnSupportedMediaTypeException(content_type)
            response = unsupported_mediatype_error_handler(exc)
            
            assert response.status_code == 415
