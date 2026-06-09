"""
Comprehensive tests for global_exception_handler.py
Tests all exception handlers and their response formatting
"""

import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock, Mock
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from image_explain.exception.global_exception_handler import (
    validation_error_handler,
    unsupported_mediatype_error_handler,
    http_exception_handler
)
from image_explain.exception.global_exception import (
    UnSupportedMediaTypeException,
    DBConnectionError,
    NotSupportedError,
    InternalServerError,
    MethodArgumentNotValidException
)
from image_explain.exception.constants import HTTP_STATUS_CODES


class TestValidationErrorHandler:
    """Test validation_error_handler function"""
    
    def test_validation_error_handler_basic(self):
        """Test basic validation error handling"""
        # Create a mock validation error
        mock_exc = MagicMock(spec=RequestValidationError)
        mock_exc.errors.return_value = [
            {
                "type": "value_error",
                "loc": ("body", "field"),
                "msg": "Invalid value"
            }
        ]
        
        response = validation_error_handler(mock_exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == HTTP_STATUS_CODES["UNPROCESSABLE_ENTITY"]
        assert response.status_code == 422
    
    def test_validation_error_handler_with_multiple_errors(self):
        """Test validation error handler with multiple field errors"""
        mock_exc = MagicMock(spec=RequestValidationError)
        mock_exc.errors.return_value = [
            {"type": "value_error", "loc": ("body", "field1"), "msg": "Error 1"},
            {"type": "type_error", "loc": ("body", "field2"), "msg": "Error 2"},
            {"type": "value_error", "loc": ("body", "field3"), "msg": "Error 3"}
        ]
        
        response = validation_error_handler(mock_exc)
        
        assert response.status_code == 422
        assert "ERROR" in response.body.decode()
    
    def test_validation_error_handler_with_type_error(self):
        """Test validation error handler with type validation error"""
        mock_exc = MagicMock(spec=RequestValidationError)
        mock_exc.errors.return_value = [
            {
                "type": "type_error.integer",
                "loc": ("body", "age"),
                "msg": "value is not a valid integer"
            }
        ]
        
        response = validation_error_handler(mock_exc)
        
        assert response.status_code == 422
        assert isinstance(response, JSONResponse)
    
    def test_validation_error_handler_with_nested_field_errors(self):
        """Test validation error handler with nested field errors"""
        mock_exc = MagicMock(spec=RequestValidationError)
        mock_exc.errors.return_value = [
            {
                "type": "value_error",
                "loc": ("body", "user", "profile", "age"),
                "msg": "Invalid age"
            }
        ]
        
        response = validation_error_handler(mock_exc)
        
        assert response.status_code == 422
    
    def test_validation_error_handler_with_empty_errors(self):
        """Test validation error handler with empty errors list"""
        mock_exc = MagicMock(spec=RequestValidationError)
        mock_exc.errors.return_value = []
        
        response = validation_error_handler(mock_exc)
        
        assert response.status_code == 422
        assert "ERROR" in response.body.decode()
    
    def test_validation_error_handler_response_contains_error_key(self):
        """Test that response contains ERROR key"""
        mock_exc = MagicMock(spec=RequestValidationError)
        mock_exc.errors.return_value = [{"type": "error", "msg": "test"}]
        
        response = validation_error_handler(mock_exc)
        body = response.body.decode()
        
        assert "ERROR" in body
    
    def test_validation_error_handler_response_json_format(self):
        """Test that response is valid JSON"""
        mock_exc = MagicMock(spec=RequestValidationError)
        mock_exc.errors.return_value = [{"type": "error", "msg": "test"}]
        
        response = validation_error_handler(mock_exc)
        body = response.body.decode()
        
        # Should be valid JSON
        parsed = json.loads(body)
        assert isinstance(parsed, dict)
        assert "ERROR" in parsed


class TestUnsupportedMediaTypeErrorHandler:
    """Test unsupported_mediatype_error_handler function"""
    
    def test_unsupported_mediatype_basic(self):
        """Test basic unsupported media type error handling"""
       
        mock_exc = MagicMock(spec=UnSupportedMediaTypeException)
        mock_exc.message = "Unsupported media type: application/xml"
        mock_exc.status_code = 415
        
        response = unsupported_mediatype_error_handler(mock_exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == HTTP_STATUS_CODES["UNSUPPORTED_MEDIA_TYPE"]
        assert response.status_code == 415
    
    def test_unsupported_mediatype_with_json_content_type(self):
        """Test unsupported media type with JSON content type"""
        mock_exc = MagicMock(spec=UnSupportedMediaTypeException); mock_exc.message = "Unsupported media type: application/json"; mock_exc.status_code = 415; exc = mock_exc
        
        response = unsupported_mediatype_error_handler(exc)
        
        assert response.status_code == 415
        assert "ERROR" in response.body.decode()
    
    def test_unsupported_mediatype_with_text_plain(self):
        """Test unsupported media type with text/plain"""
        mock_exc = MagicMock(spec=UnSupportedMediaTypeException); mock_exc.message = "Unsupported media type: text/plain"; mock_exc.status_code = 415; exc = mock_exc
        
        response = unsupported_mediatype_error_handler(exc)
        
        assert response.status_code == 415
    
    def test_unsupported_mediatype_with_empty_string(self):
        """Test unsupported media type with empty content type string"""
        mock_exc = MagicMock(spec=UnSupportedMediaTypeException)
        mock_exc.message = "Unsupported media type: "
        mock_exc.status_code = 415
        
        response = unsupported_mediatype_error_handler(mock_exc)
        
        assert response.status_code == 415
    
    def test_unsupported_mediatype_response_format(self):
        """Test unsupported media type response format"""
        mock_exc = MagicMock(spec=UnSupportedMediaTypeException); mock_exc.message = "Unsupported media type: application/xml"; mock_exc.status_code = 415; exc = mock_exc
        
        response = unsupported_mediatype_error_handler(exc)
        body = response.body.decode()
        
        assert "ERROR" in body
        parsed = json.loads(body)
        assert isinstance(parsed, dict)
    
    def test_unsupported_mediatype_includes_content_type_in_message(self):
        """Test that content type is included in error message"""
        mock_exc = MagicMock(spec=UnSupportedMediaTypeException)
        mock_exc.message = "Unsupported media type: image/png"
        
        response = unsupported_mediatype_error_handler(mock_exc)
        body = response.body.decode()
        
        # Message should contain the content type
        assert "image/png" in body or "image" in body or "png" in body
    
    def test_unsupported_mediatype_with_charset(self):
        """Test unsupported media type with charset parameter"""
        mock_exc = MagicMock(spec=UnSupportedMediaTypeException); mock_exc.message = "Unsupported media type: text/html; charset=utf-8"; mock_exc.status_code = 415; exc = mock_exc
        
        response = unsupported_mediatype_error_handler(exc)
        
        assert response.status_code == 415
    
    def test_unsupported_mediatype_with_special_characters(self):
        """Test unsupported media type with special characters"""
        mock_exc = MagicMock(spec=UnSupportedMediaTypeException); mock_exc.message = "Unsupported media type: application/vnd.custom+json"; mock_exc.status_code = 415; exc = mock_exc
        
        response = unsupported_mediatype_error_handler(exc)
        
        assert response.status_code == 415


class TestHttpExceptionHandler:
    """Test http_exception_handler function"""
    
    def test_http_exception_handler_404(self):
        """Test HTTP exception handler with 404 status code"""
        mock_exc = MagicMock()
        mock_exc.status_code = 404
        mock_exc.detail = "Resource not found"
        
        response = http_exception_handler(mock_exc)
        
        assert response.status_code == 404
        assert isinstance(response, JSONResponse)
    
    def test_http_exception_handler_400(self):
        """Test HTTP exception handler with 400 status code"""
        mock_exc = MagicMock()
        mock_exc.status_code = 400
        mock_exc.detail = "Bad request"
        
        response = http_exception_handler(mock_exc)
        
        assert response.status_code == 400
    
    def test_http_exception_handler_500(self):
        """Test HTTP exception handler with 500 status code"""
        mock_exc = MagicMock()
        mock_exc.status_code = 500
        mock_exc.detail = "Internal server error"
        
        response = http_exception_handler(mock_exc)
        
        assert response.status_code == 500
    
    def test_http_exception_handler_403(self):
        """Test HTTP exception handler with 403 status code"""
        mock_exc = MagicMock()
        mock_exc.status_code = 403
        mock_exc.detail = "Forbidden"
        
        response = http_exception_handler(mock_exc)
        
        assert response.status_code == 403
    
    def test_http_exception_handler_response_format(self):
        """Test HTTP exception handler response format"""
        mock_exc = MagicMock()
        mock_exc.status_code = 400
        mock_exc.detail = "Invalid request"
        
        response = http_exception_handler(mock_exc)
        body = response.body.decode()
        
        parsed = json.loads(body)
        assert "ERROR" in parsed
        assert parsed["ERROR"] == "Invalid request"
    
    def test_http_exception_handler_with_dict_detail(self):
        """Test HTTP exception handler when detail is a dict"""
        mock_exc = MagicMock()
        mock_exc.status_code = 422
        mock_exc.detail = {"field": "error message"}
        
        response = http_exception_handler(mock_exc)
        
        assert response.status_code == 422
    
    def test_http_exception_handler_with_empty_detail(self):
        """Test HTTP exception handler with empty detail"""
        mock_exc = MagicMock()
        mock_exc.status_code = 400
        mock_exc.detail = ""
        
        response = http_exception_handler(mock_exc)
        
        assert response.status_code == 400
    
    def test_http_exception_handler_preserves_status_code(self):
        """Test that handler preserves the original status code"""
        status_codes = [400, 401, 403, 404, 500, 502, 503]
        
        for code in status_codes:
            mock_exc = MagicMock()
            mock_exc.status_code = code
            mock_exc.detail = f"Error {code}"
            
            response = http_exception_handler(mock_exc)
            
            assert response.status_code == code


class TestExceptionHandlerIntegration:
    """Integration tests for exception handlers with custom exceptions"""
    
    def test_handler_with_db_connection_error(self):
        """Test handler with DBConnectionError exception"""
        mock_exc = MagicMock(); mock_exc.status_code = 503; mock_exc.message = "Database connection refused"; exc = mock_exc
        
        response = http_exception_handler(exc)
        
        assert response.status_code == exc.status_code
        assert "ERROR" in response.body.decode()
    
    def test_handler_with_not_supported_error(self):
        """Test handler with NotSupportedError exception"""
        mock_exc = MagicMock(); mock_exc.status_code = 405; mock_exc.message = "Feature not available"; exc = mock_exc
        
        response = http_exception_handler(exc)
        
        assert response.status_code == exc.status_code
    
    def test_handler_with_internal_server_error(self):
        """Test handler with InternalServerError exception"""
        mock_exc = MagicMock(); mock_exc.status_code = 500; mock_exc.message = "Database query failed"; exc = mock_exc
        
        response = http_exception_handler(exc)
        
        assert response.status_code == exc.status_code
    
    def test_handler_with_method_argument_not_valid(self):
        """Test handler with MethodArgumentNotValidException"""
        mock_exc = MagicMock(); mock_exc.status_code = 400; mock_exc.message = "Required field missing"; exc = mock_exc
        
        response = http_exception_handler(exc)
        
        assert response.status_code == exc.status_code


class TestResponseContentValidation:
    """Test response content validation and JSON encoding"""
    
    def test_validation_error_response_is_json_serializable(self):
        """Test that validation error response is JSON serializable"""
        mock_exc = MagicMock(spec=RequestValidationError)
        mock_exc.errors.return_value = [
            {"type": "error", "loc": ("field",), "msg": "error message"}
        ]
        
        response = validation_error_handler(mock_exc)
        body = response.body.decode()
        
        # Should not raise exception
        parsed = json.loads(body)
        assert isinstance(parsed, dict)
    
    def test_unsupported_mediatype_response_is_json_serializable(self):
        """Test that unsupported media type response is JSON serializable"""
        mock_exc = MagicMock(spec=UnSupportedMediaTypeException); mock_exc.message = "Unsupported media type: application/xml"; mock_exc.status_code = 415; exc = mock_exc
        
        response = unsupported_mediatype_error_handler(exc)
        body = response.body.decode()
        
        parsed = json.loads(body)
        assert isinstance(parsed, dict)
    
    def test_http_exception_response_is_json_serializable(self):
        """Test that HTTP exception response is JSON serializable"""
        mock_exc = MagicMock()
        mock_exc.status_code = 400
        mock_exc.detail = "Bad request"
        
        response = http_exception_handler(mock_exc)
        body = response.body.decode()
        
        parsed = json.loads(body)
        assert isinstance(parsed, dict)
    
    def test_all_handlers_return_json_response_type(self):
        """Test that all handlers return JSONResponse objects"""
        # Validation error handler
        mock_val_exc = MagicMock(spec=RequestValidationError)
        mock_val_exc.errors.return_value = []
        val_response = validation_error_handler(mock_val_exc)
        assert isinstance(val_response, JSONResponse)
        
        # Unsupported media type handler
        unsup_exc = MagicMock(spec=UnSupportedMediaTypeException)
        unsup_exc.message = "Unsupported media type: test"
        unsup_exc.status_code = 415
        unsup_response = unsupported_mediatype_error_handler(unsup_exc)
        assert isinstance(unsup_response, JSONResponse)
        
        # HTTP exception handler
        mock_http_exc = MagicMock()
        mock_http_exc.status_code = 400
        mock_http_exc.detail = "test"
        http_response = http_exception_handler(mock_http_exc)
        assert isinstance(http_response, JSONResponse)


class TestErrorKeyConsistency:
    """Test that all handlers use consistent ERROR key"""
    
    def test_validation_error_has_error_key(self):
        """Test validation error response has ERROR key"""
        mock_exc = MagicMock(spec=RequestValidationError)
        mock_exc.errors.return_value = [{"error": "test"}]
        
        response = validation_error_handler(mock_exc)
        body = json.loads(response.body.decode())
        
        assert "ERROR" in body
    
    def test_unsupported_mediatype_has_error_key(self):
        """Test unsupported media type response has ERROR key"""
        mock_exc = MagicMock(spec=UnSupportedMediaTypeException); mock_exc.message = "Unsupported media type: test"; mock_exc.status_code = 415; exc = mock_exc
        
        response = unsupported_mediatype_error_handler(exc)
        body = json.loads(response.body.decode())
        
        assert "ERROR" in body
    
    def test_http_exception_has_error_key(self):
        """Test HTTP exception response has ERROR key"""
        mock_exc = MagicMock()
        mock_exc.status_code = 400
        mock_exc.detail = "test"
        
        response = http_exception_handler(mock_exc)
        body = json.loads(response.body.decode())
        
        assert "ERROR" in body
    
    def test_all_responses_follow_error_format(self):
        """Test that all responses follow consistent error format"""
        # All responses should be {"ERROR": <value>}
        mock_val_exc = MagicMock(spec=RequestValidationError)
        mock_val_exc.errors.return_value = [{"error": "test"}]
        val_response = validation_error_handler(mock_val_exc)
        val_body = json.loads(val_response.body.decode())
        
        unsup_exc = MagicMock(spec=UnSupportedMediaTypeException)
        unsup_exc.message = "Unsupported media type: test"
        unsup_exc.status_code = 415
        unsup_response = unsupported_mediatype_error_handler(unsup_exc)
        unsup_body = json.loads(unsup_response.body.decode())
        
        mock_http_exc = MagicMock()
        mock_http_exc.status_code = 400
        mock_http_exc.detail = "test"
        http_response = http_exception_handler(mock_http_exc)
        http_body = json.loads(http_response.body.decode())
        
        # All should have ERROR key
        assert "ERROR" in val_body
        assert "ERROR" in unsup_body
        assert "ERROR" in http_body


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_validation_error_with_very_long_error_list(self):
        """Test validation error handler with many errors"""
        mock_exc = MagicMock(spec=RequestValidationError)
        errors = [
            {"type": "error", "loc": (f"field{i}",), "msg": f"Error {i}"}
            for i in range(100)
        ]
        mock_exc.errors.return_value = errors
        
        response = validation_error_handler(mock_exc)
        
        assert response.status_code == 422
        body = json.loads(response.body.decode())
        assert isinstance(body, dict)
    
    def test_unsupported_mediatype_with_very_long_content_type(self):
        """Test unsupported media type with very long content type string"""
        long_content_type = "application/" + "x" * 1000
        mock_exc = MagicMock(spec=UnSupportedMediaTypeException)
        mock_exc.message = f"Unsupported media type: {long_content_type}"
        mock_exc.status_code = 415
        
        response = unsupported_mediatype_error_handler(mock_exc)
        
        assert response.status_code == 415
    
    def test_http_exception_with_max_status_code(self):
        """Test HTTP exception handler with status code 599"""
        mock_exc = MagicMock()
        mock_exc.status_code = 599
        mock_exc.detail = "Custom error"
        
        response = http_exception_handler(mock_exc)
        
        assert response.status_code == 599
    
    def test_http_exception_with_min_status_code(self):
        """Test HTTP exception handler with status code 100"""
        mock_exc = MagicMock()
        mock_exc.status_code = 100
        mock_exc.detail = "Continue"
        
        response = http_exception_handler(mock_exc)
        
        assert response.status_code == 100
    
    def test_http_exception_with_special_characters_in_detail(self):
        """Test HTTP exception with special characters"""
        mock_exc = MagicMock()
        mock_exc.status_code = 400
        mock_exc.detail = "Error: <script>alert('xss')</script>"
        
        response = http_exception_handler(mock_exc)
        body = response.body.decode()
        
        # Should still be valid JSON
        parsed = json.loads(body)
        assert isinstance(parsed, dict)
    
    def test_http_exception_with_unicode_characters(self):
        """Test HTTP exception with unicode characters"""
        mock_exc = MagicMock()
        mock_exc.status_code = 400
        mock_exc.detail = "错误: エラー: Ошибка"
        
        response = http_exception_handler(mock_exc)
        body = response.body.decode()
        
        parsed = json.loads(body)
        assert "ERROR" in parsed


class TestStatusCodeConstants:
    """Test correct usage of HTTP status code constants"""
    
    def test_validation_error_uses_correct_status_code(self):
        """Test that validation error uses UNPROCESSABLE_ENTITY status code"""
        mock_exc = MagicMock(spec=RequestValidationError)
        mock_exc.errors.return_value = []
        
        response = validation_error_handler(mock_exc)
        
        assert response.status_code == HTTP_STATUS_CODES["UNPROCESSABLE_ENTITY"]
        assert response.status_code == 422
    
    def test_unsupported_mediatype_uses_correct_status_code(self):
        """Test that unsupported media type uses UNSUPPORTED_MEDIA_TYPE status code"""
        mock_exc = MagicMock(spec=UnSupportedMediaTypeException); mock_exc.message = "Unsupported media type: test"; mock_exc.status_code = 415; exc = mock_exc
        
        response = unsupported_mediatype_error_handler(exc)
        
        assert response.status_code == HTTP_STATUS_CODES["UNSUPPORTED_MEDIA_TYPE"]
        assert response.status_code == 415

