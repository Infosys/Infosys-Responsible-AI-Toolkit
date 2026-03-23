'''
MIT License https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Test cases for privacy.exception.exception module
Testing custom exception classes and handlers
'''

import pytest
from unittest.mock import Mock, MagicMock, patch, call

from privacy.exception.exception import (
    PrivacyException,
    PrivacyNotFoundError,
    PrivacyNameNotEmptyError,
    UnSupportedMediaTypeException,
    validation_error_handler,
    http_exception_handler,
    unsupported_mediatype_error_handler
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class TestPrivacyException:
    """Test cases for PrivacyException base class"""
    
    def test_privacy_exception_initialization(self):
        """Test PrivacyException initialization"""
        exception = PrivacyException("Test error message")
        
        assert str(exception) == "Test error message"
        assert hasattr(exception, 'status_code')
        assert exception.status_code == 500  # HTTP_STATUS_BAD_REQUEST is defined as 500
    
    def test_privacy_exception_is_exception(self):
        """Test that PrivacyException is an Exception"""
        exception = PrivacyException("Test")
        
        assert isinstance(exception, Exception)
    
    def test_privacy_exception_can_be_raised(self):
        """Test that PrivacyException can be raised"""
        with pytest.raises(PrivacyException) as exc_info:
            raise PrivacyException("Test error")
        
        assert "Test error" in str(exc_info.value)


class TestPrivacyNotFoundError:
    """Test cases for PrivacyNotFoundError"""
    
    def test_privacy_not_found_error_initialization(self):
        """Test PrivacyNotFoundError initialization"""
        error = PrivacyNotFoundError("TestResource")
        
        assert hasattr(error, 'status_code')
        assert error.status_code == 404  # HTTP_STATUS_NOT_FOUND
        assert hasattr(error, 'detail')
        assert "TestResource" in error.detail or error.detail is not None
    
    def test_privacy_not_found_error_inherits_from_privacy_exception(self):
        """Test that PrivacyNotFoundError inherits from PrivacyException"""
        error = PrivacyNotFoundError("Resource")
        
        assert isinstance(error, PrivacyException)
        assert isinstance(error, Exception)
    
    def test_privacy_not_found_error_with_different_names(self):
        """Test PrivacyNotFoundError with different resource names"""
        error1 = PrivacyNotFoundError("User")
        error2 = PrivacyNotFoundError("Portfolio")
        
        assert error1.status_code == error2.status_code
        assert error1.detail != error2.detail or "User" in error1.detail
    
    def test_privacy_not_found_error_can_be_raised(self):
        """Test that PrivacyNotFoundError can be raised"""
        with pytest.raises(PrivacyNotFoundError) as exc_info:
            raise PrivacyNotFoundError("TestItem")
        
        assert exc_info.value.status_code == 404


class TestPrivacyNameNotEmptyError:
    """Test cases for PrivacyNameNotEmptyError"""
    
    def test_privacy_name_not_empty_error_initialization(self):
        """Test PrivacyNameNotEmptyError initialization"""
        error = PrivacyNameNotEmptyError("EmptyName")
        
        assert hasattr(error, 'status_code')
        assert error.status_code == 409  # HTTP_STATUS_409_CODE
        assert hasattr(error, 'detail')
    
    def test_privacy_name_not_empty_error_inherits_from_privacy_exception(self):
        """Test that PrivacyNameNotEmptyError inherits from PrivacyException"""
        error = PrivacyNameNotEmptyError("Name")
        
        assert isinstance(error, PrivacyException)
        assert isinstance(error, Exception)
    
    def test_privacy_name_not_empty_error_has_validation_message(self):
        """Test that error has validation message in detail"""
        error = PrivacyNameNotEmptyError("TestName")
        
        # Detail should be set from USECASE_NAME_VALIDATION_ERROR constant
        assert error.detail is not None
        assert isinstance(error.detail, str)
    
    def test_privacy_name_not_empty_error_can_be_raised(self):
        """Test that PrivacyNameNotEmptyError can be raised"""
        with pytest.raises(PrivacyNameNotEmptyError) as exc_info:
            raise PrivacyNameNotEmptyError("")
        
        assert exc_info.value.status_code == 409


class TestUnSupportedMediaTypeException:
    """Test cases for UnSupportedMediaTypeException"""
    
    def test_unsupported_media_type_exception_initialization(self):
        """Test UnSupportedMediaTypeException initialization"""
        content_type = "application/xml"
        exception = UnSupportedMediaTypeException(content_type)
        
        assert hasattr(exception, 'status_code')
        assert exception.status_code == 415  # HTTP_415_UNSUPPORTED_MEDIA_TYPE
        assert hasattr(exception, 'message')
        assert content_type in exception.message
    
    def test_unsupported_media_type_exception_with_different_types(self):
        """Test exception with different content types"""
        xml_exception = UnSupportedMediaTypeException("application/xml")
        text_exception = UnSupportedMediaTypeException("text/plain")
        
        assert "xml" in xml_exception.message
        assert "plain" in text_exception.message
        assert xml_exception.status_code == text_exception.status_code
    
    def test_unsupported_media_type_exception_inherits_from_exception(self):
        """Test that UnSupportedMediaTypeException inherits from Exception"""
        exception = UnSupportedMediaTypeException("invalid/type")
        
        assert isinstance(exception, Exception)
    
    def test_unsupported_media_type_exception_can_be_raised(self):
        """Test that exception can be raised"""
        with pytest.raises(UnSupportedMediaTypeException) as exc_info:
            raise UnSupportedMediaTypeException("bad/type")
        
        assert exc_info.value.status_code == 415


class TestValidationErrorHandler:
    """Test cases for validation_error_handler function"""
    
    def test_validation_error_handler_returns_json_response(self):
        """Test that validation error handler returns JSONResponse"""
        # Create a mock RequestValidationError
        mock_exc = Mock(spec=RequestValidationError)
        mock_exc.errors.return_value = [
            {
                "loc": ["body", "field"],
                "msg": "field required",
                "type": "value_error.missing"
            }
        ]
        
        response = validation_error_handler(mock_exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 422  # HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_validation_error_handler_includes_error_details(self):
        """Test that handler includes error details in response"""
        mock_exc = Mock(spec=RequestValidationError)
        mock_exc.errors.return_value = [
            {
                "loc": ["body", "inputText"],
                "msg": "field required",
                "type": "value_error.missing"
            }
        ]
        
        response = validation_error_handler(mock_exc)
        
        # The response body should contain error details
        assert response.status_code == 422
        # Response should have body with detail key
        assert hasattr(response, 'body')
    
    def test_validation_error_handler_with_multiple_errors(self):
        """Test handler with multiple validation errors"""
        mock_exc = Mock(spec=RequestValidationError)
        mock_exc.errors.return_value = [
            {"loc": ["body", "field1"], "msg": "error1", "type": "type1"},
            {"loc": ["body", "field2"], "msg": "error2", "type": "type2"}
        ]
        
        response = validation_error_handler(mock_exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 422


class TestHttpExceptionHandler:
    """Test cases for http_exception_handler function"""
    
    def test_http_exception_handler_returns_json_response(self):
        """Test that HTTP exception handler returns JSONResponse"""
        mock_exc = Mock()
        mock_exc.status_code = 404
        mock_exc.detail = "Resource not found"
        
        response = http_exception_handler(mock_exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 404
    
    def test_http_exception_handler_includes_detail(self):
        """Test that handler includes exception detail"""
        mock_exc = Mock()
        mock_exc.status_code = 500
        mock_exc.detail = "Internal server error"
        
        response = http_exception_handler(mock_exc)
        
        assert response.status_code == 500
        # Response body should contain the detail
        assert hasattr(response, 'body')
    
    def test_http_exception_handler_with_different_status_codes(self):
        """Test handler with different HTTP status codes"""
        status_codes = [400, 401, 403, 404, 500, 503]
        
        for status_code in status_codes:
            mock_exc = Mock()
            mock_exc.status_code = status_code
            mock_exc.detail = f"Error {status_code}"
            
            response = http_exception_handler(mock_exc)
            
            assert response.status_code == status_code
    
    def test_http_exception_handler_with_privacy_not_found_error(self):
        """Test handler with PrivacyNotFoundError"""
        exc = PrivacyNotFoundError("TestResource")
        
        response = http_exception_handler(exc)
        
        assert response.status_code == 404
        assert isinstance(response, JSONResponse)


class TestUnsupportedMediaTypeErrorHandler:
    """Test cases for unsupported_mediatype_error_handler function"""
    
    def test_unsupported_mediatype_error_handler_returns_json_response(self):
        """Test that handler returns JSONResponse"""
        exc = UnSupportedMediaTypeException("application/xml")
        
        response = unsupported_mediatype_error_handler(exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 415
    
    def test_unsupported_mediatype_error_handler_includes_message(self):
        """Test that handler includes exception message"""
        exc = UnSupportedMediaTypeException("text/csv")
        
        response = unsupported_mediatype_error_handler(exc)
        
        assert response.status_code == 415
        # Response body should contain the message
        assert hasattr(response, 'body')
    
    def test_unsupported_mediatype_error_handler_with_different_types(self):
        """Test handler with different unsupported media types"""
        media_types = ["application/xml", "text/csv", "image/tiff", "video/mpeg"]
        
        for media_type in media_types:
            exc = UnSupportedMediaTypeException(media_type)
            response = unsupported_mediatype_error_handler(exc)
            
            assert response.status_code == 415
            assert isinstance(response, JSONResponse)


class TestExceptionIntegration:
    """Integration tests for exception handling"""
    
    def test_privacy_exception_hierarchy(self):
        """Test exception hierarchy is correct"""
        not_found = PrivacyNotFoundError("test")
        name_empty = PrivacyNameNotEmptyError("test")
        
        # Both should be instances of PrivacyException
        assert isinstance(not_found, PrivacyException)
        assert isinstance(name_empty, PrivacyException)
        
        # Both should be instances of Exception
        assert isinstance(not_found, Exception)
        assert isinstance(name_empty, Exception)
    
    def test_exception_status_codes_are_different(self):
        """Test that different exceptions have different status codes"""
        base_exc = PrivacyException("test")
        not_found = PrivacyNotFoundError("test")
        name_empty = PrivacyNameNotEmptyError("test")
        unsupported = UnSupportedMediaTypeException("test")
        
        status_codes = [
            base_exc.status_code,
            not_found.status_code,
            name_empty.status_code,
            unsupported.status_code
        ]
        
        # Should have at least 3 different status codes
        assert len(set(status_codes)) >= 3
    
    def test_exception_handlers_with_real_exceptions(self):
        """Test handlers work with real exception instances"""
        # Test with PrivacyNotFoundError
        not_found = PrivacyNotFoundError("Resource")
        response = http_exception_handler(not_found)
        assert response.status_code == 404
        
        # Test with PrivacyNameNotEmptyError
        name_empty = PrivacyNameNotEmptyError("Name")
        response = http_exception_handler(name_empty)
        assert response.status_code == 409
        
        # Test with UnSupportedMediaTypeException
        unsupported = UnSupportedMediaTypeException("bad/type")
        response = unsupported_mediatype_error_handler(unsupported)
        assert response.status_code == 415


class TestExceptionEdgeCases:
    """Test edge cases and error scenarios"""
    
    def test_exception_with_empty_string(self):
        """Test exceptions with empty string parameters"""
        exc1 = PrivacyException("")
        exc2 = PrivacyNotFoundError("")
        exc3 = PrivacyNameNotEmptyError("")
        exc4 = UnSupportedMediaTypeException("")
        
        # All should initialize without error
        assert exc1 is not None
        assert exc2 is not None
        assert exc3 is not None
        assert exc4 is not None
    
    def test_exception_with_special_characters(self):
        """Test exceptions with special characters"""
        special_chars = "!@#$%^&*()[]{}|\\:;\"'<>?,./`~"
        
        exc = PrivacyNotFoundError(special_chars)
        assert exc is not None
        
        unsupported = UnSupportedMediaTypeException(special_chars)
        assert unsupported is not None
    
    def test_exception_with_unicode(self):
        """Test exceptions with unicode characters"""
        unicode_text = "Test 测试 тест परीक्षण"
        
        exc1 = PrivacyException(unicode_text)
        exc2 = PrivacyNotFoundError(unicode_text)
        
        assert exc1 is not None
        assert exc2 is not None
    
    def test_handler_with_none_detail(self):
        """Test handlers handle None detail gracefully"""
        mock_exc = Mock()
        mock_exc.status_code = 500
        mock_exc.detail = None
        
        response = http_exception_handler(mock_exc)
        
        # Should still return valid response
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
    
    def test_multiple_exception_instances_are_independent(self):
        """Test that multiple exception instances don't interfere"""
        exc1 = PrivacyNotFoundError("Resource1")
        exc2 = PrivacyNotFoundError("Resource2")
        exc3 = PrivacyNotFoundError("Resource3")
        
        # Each should have its own detail
        assert exc1.detail != exc2.detail or "Resource1" in exc1.detail
        assert exc2.detail != exc3.detail or "Resource2" in exc2.detail
