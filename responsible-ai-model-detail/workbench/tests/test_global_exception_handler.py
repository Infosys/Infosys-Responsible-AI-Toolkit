"""
Unit tests for global_exception_handler module.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app.exception.global_exception_handler import (
    validation_error_handler,
    http_exception_handler,
    unsupported_mediatype_error_handler
)
from app.exception.global_exception import UnSupportedMediaTypeException
from app.constants import global_constants
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class TestValidationErrorHandler:
    """Tests for validation_error_handler function."""
    
    @patch('app.exception.global_exception_handler.jsonable_encoder')
    def test_validation_error_handler_basic(self, mock_encoder):
        # Create a mock RequestValidationError
        mock_exc = Mock(spec=RequestValidationError)
        mock_exc.errors.return_value = [
            {
                "loc": ["body", "field1"],
                "msg": "field required",
                "type": "value_error.missing"
            }
        ]
        mock_encoder.return_value = {"detail": mock_exc.errors()}
        
        result = validation_error_handler(mock_exc)
        
        assert isinstance(result, JSONResponse)
        assert result.status_code == int(global_constants.HTTP_422_UNPROCESSABLE_ENTITY)
        mock_encoder.assert_called_once()
    
    @patch('app.exception.global_exception_handler.jsonable_encoder')
    def test_validation_error_handler_multiple_errors(self, mock_encoder):
        mock_exc = Mock(spec=RequestValidationError)
        mock_exc.errors.return_value = [
            {"loc": ["body", "field1"], "msg": "field required"},
            {"loc": ["body", "field2"], "msg": "invalid type"}
        ]
        mock_encoder.return_value = {"detail": mock_exc.errors()}
        
        result = validation_error_handler(mock_exc)
        
        assert isinstance(result, JSONResponse)
        assert result.status_code == int(global_constants.HTTP_422_UNPROCESSABLE_ENTITY)
    
    @patch('app.exception.global_exception_handler.jsonable_encoder')
    def test_validation_error_handler_empty_errors(self, mock_encoder):
        mock_exc = Mock(spec=RequestValidationError)
        mock_exc.errors.return_value = []
        mock_encoder.return_value = {"detail": []}
        
        result = validation_error_handler(mock_exc)
        
        assert isinstance(result, JSONResponse)
        assert result.status_code == int(global_constants.HTTP_422_UNPROCESSABLE_ENTITY)
    
    @patch('app.exception.global_exception_handler.jsonable_encoder')
    def test_validation_error_handler_complex_error(self, mock_encoder):
        mock_exc = Mock(spec=RequestValidationError)
        mock_exc.errors.return_value = [
            {
                "loc": ["body", "nested", "field"],
                "msg": "string does not match regex",
                "type": "value_error.str.regex",
                "ctx": {"pattern": "^[a-z]+$"}
            }
        ]
        mock_encoder.return_value = {"detail": mock_exc.errors()}
        
        result = validation_error_handler(mock_exc)
        
        assert isinstance(result, JSONResponse)
        mock_encoder.assert_called_once_with({"detail": mock_exc.errors()})
    
    @patch('app.exception.global_exception_handler.jsonable_encoder')
    def test_validation_error_handler_with_query_params(self, mock_encoder):
        mock_exc = Mock(spec=RequestValidationError)
        mock_exc.errors.return_value = [
            {
                "loc": ["query", "page"],
                "msg": "value is not a valid integer",
                "type": "type_error.integer"
            }
        ]
        mock_encoder.return_value = {"detail": mock_exc.errors()}
        
        result = validation_error_handler(mock_exc)
        
        assert isinstance(result, JSONResponse)
        assert result.status_code == int(global_constants.HTTP_422_UNPROCESSABLE_ENTITY)


class TestHttpExceptionHandler:
    """Tests for http_exception_handler function."""
    
    @patch('app.exception.global_exception_handler.jsonable_encoder')
    def test_http_exception_handler_basic(self, mock_encoder):
        mock_exc = Mock()
        mock_exc.status_code = 404
        mock_exc.detail = "Resource not found"
        mock_encoder.return_value = {"detail": "Resource not found"}
        
        result = http_exception_handler(mock_exc)
        
        assert isinstance(result, JSONResponse)
        assert result.status_code == 404
        mock_encoder.assert_called_once_with({"detail": "Resource not found"})
    
    @patch('app.exception.global_exception_handler.jsonable_encoder')
    def test_http_exception_handler_400_error(self, mock_encoder):
        mock_exc = Mock()
        mock_exc.status_code = 400
        mock_exc.detail = "Bad request"
        mock_encoder.return_value = {"detail": "Bad request"}
        
        result = http_exception_handler(mock_exc)
        
        assert isinstance(result, JSONResponse)
        assert result.status_code == 400
    
    @patch('app.exception.global_exception_handler.jsonable_encoder')
    def test_http_exception_handler_500_error(self, mock_encoder):
        mock_exc = Mock()
        mock_exc.status_code = 500
        mock_exc.detail = "Internal server error"
        mock_encoder.return_value = {"detail": "Internal server error"}
        
        result = http_exception_handler(mock_exc)
        
        assert isinstance(result, JSONResponse)
        assert result.status_code == 500
    
    @patch('app.exception.global_exception_handler.jsonable_encoder')
    def test_http_exception_handler_with_empty_detail(self, mock_encoder):
        mock_exc = Mock()
        mock_exc.status_code = 403
        mock_exc.detail = ""
        mock_encoder.return_value = {"detail": ""}
        
        result = http_exception_handler(mock_exc)
        
        assert isinstance(result, JSONResponse)
        assert result.status_code == 403
    
    @patch('app.exception.global_exception_handler.jsonable_encoder')
    def test_http_exception_handler_with_complex_detail(self, mock_encoder):
        mock_exc = Mock()
        mock_exc.status_code = 422
        mock_exc.detail = {"errors": ["error1", "error2"]}
        mock_encoder.return_value = {"detail": str({"errors": ["error1", "error2"]})}
        
        result = http_exception_handler(mock_exc)
        
        assert isinstance(result, JSONResponse)
        assert result.status_code == 422
    
    @patch('app.exception.global_exception_handler.jsonable_encoder')
    def test_http_exception_handler_unauthorized(self, mock_encoder):
        mock_exc = Mock()
        mock_exc.status_code = 401
        mock_exc.detail = "Unauthorized access"
        mock_encoder.return_value = {"detail": "Unauthorized access"}
        
        result = http_exception_handler(mock_exc)
        
        assert isinstance(result, JSONResponse)
        assert result.status_code == 401
    
    @patch('app.exception.global_exception_handler.jsonable_encoder')
    def test_http_exception_handler_with_special_characters(self, mock_encoder):
        mock_exc = Mock()
        mock_exc.status_code = 400
        mock_exc.detail = "Invalid input: @#$%^&*()"
        mock_encoder.return_value = {"detail": "Invalid input: @#$%^&*()"}
        
        result = http_exception_handler(mock_exc)
        
        assert isinstance(result, JSONResponse)
        mock_encoder.assert_called_once()


class TestUnsupportedMediaTypeErrorHandler:
    """Tests for unsupported_mediatype_error_handler function."""
    
    @patch('app.exception.global_exception_handler.jsonable_encoder')
    def test_unsupported_mediatype_error_handler_basic(self, mock_encoder):
        exc = UnSupportedMediaTypeException("application/xml")
        mock_encoder.return_value = {"detail": exc.message}
        
        result = unsupported_mediatype_error_handler(exc)
        
        assert isinstance(result, JSONResponse)
        assert result.status_code == exc.status_code
        mock_encoder.assert_called_once()
    
    @patch('app.exception.global_exception_handler.jsonable_encoder')
    def test_unsupported_mediatype_error_handler_with_empty_type(self, mock_encoder):
        exc = UnSupportedMediaTypeException("")
        mock_encoder.return_value = {"detail": exc.message}
        
        result = unsupported_mediatype_error_handler(exc)
        
        assert isinstance(result, JSONResponse)
        assert result.status_code == global_constants.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    
    @patch('app.exception.global_exception_handler.jsonable_encoder')
    def test_unsupported_mediatype_error_handler_text_plain(self, mock_encoder):
        exc = UnSupportedMediaTypeException("text/plain")
        mock_encoder.return_value = {"detail": exc.message}
        
        result = unsupported_mediatype_error_handler(exc)
        
        assert isinstance(result, JSONResponse)
        assert result.status_code == global_constants.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        mock_encoder.assert_called_once_with({"detail": str(exc.message)})
    
    @patch('app.exception.global_exception_handler.jsonable_encoder')
    def test_unsupported_mediatype_error_handler_image_type(self, mock_encoder):
        exc = UnSupportedMediaTypeException("image/jpeg")
        mock_encoder.return_value = {"detail": exc.message}
        
        result = unsupported_mediatype_error_handler(exc)
        
        assert isinstance(result, JSONResponse)
        assert result.status_code == global_constants.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    
    @patch('app.exception.global_exception_handler.jsonable_encoder')
    def test_unsupported_mediatype_error_handler_video_type(self, mock_encoder):
        exc = UnSupportedMediaTypeException("video/mp4")
        mock_encoder.return_value = {"detail": exc.message}
        
        result = unsupported_mediatype_error_handler(exc)
        
        assert isinstance(result, JSONResponse)
    
    @patch('app.exception.global_exception_handler.jsonable_encoder')
    def test_unsupported_mediatype_error_handler_custom_type(self, mock_encoder):
        exc = UnSupportedMediaTypeException("application/x-custom")
        mock_encoder.return_value = {"detail": exc.message}
        
        result = unsupported_mediatype_error_handler(exc)
        
        assert isinstance(result, JSONResponse)
        assert "application/x-custom" in exc.message


class TestExceptionHandlerIntegration:
    """Integration tests for exception handlers."""
    
    @patch('app.exception.global_exception_handler.jsonable_encoder')
    def test_all_handlers_return_json_response(self, mock_encoder):
        mock_encoder.return_value = {"detail": "test"}
        
        # Test validation_error_handler
        mock_validation_exc = Mock(spec=RequestValidationError)
        mock_validation_exc.errors.return_value = []
        result1 = validation_error_handler(mock_validation_exc)
        assert isinstance(result1, JSONResponse)
        
        # Test http_exception_handler
        mock_http_exc = Mock()
        mock_http_exc.status_code = 400
        mock_http_exc.detail = "test"
        result2 = http_exception_handler(mock_http_exc)
        assert isinstance(result2, JSONResponse)
        
        # Test unsupported_mediatype_error_handler
        mock_media_exc = UnSupportedMediaTypeException("test")
        result3 = unsupported_mediatype_error_handler(mock_media_exc)
        assert isinstance(result3, JSONResponse)
    
    @patch('app.exception.global_exception_handler.jsonable_encoder')
    def test_handlers_with_various_status_codes(self, mock_encoder):
        mock_encoder.return_value = {"detail": "test"}
        
        status_codes = [400, 401, 403, 404, 422, 500, 503]
        
        for code in status_codes:
            mock_exc = Mock()
            mock_exc.status_code = code
            mock_exc.detail = f"Error {code}"
            
            result = http_exception_handler(mock_exc)
            assert result.status_code == code
    
    @patch('app.exception.global_exception_handler.jsonable_encoder')
    def test_encoder_called_correctly(self, mock_encoder):
        mock_encoder.return_value = {"detail": "encoded"}
        
        # Test with validation error
        mock_validation_exc = Mock(spec=RequestValidationError)
        mock_validation_exc.errors.return_value = [{"test": "error"}]
        validation_error_handler(mock_validation_exc)
        
        # Test with http error
        mock_http_exc = Mock()
        mock_http_exc.status_code = 400
        mock_http_exc.detail = "http error"
        http_exception_handler(mock_http_exc)
        
        # Test with media type error
        media_exc = UnSupportedMediaTypeException("application/xml")
        unsupported_mediatype_error_handler(media_exc)
        
        # Verify encoder was called multiple times
        assert mock_encoder.call_count >= 3
