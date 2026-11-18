"""
Unit tests for exception module
"""
import pytest
from unittest.mock import MagicMock
from privacy.exception.exception import (
    PrivacyException,
    PrivacyNotFoundError,
    PrivacyNameNotEmptyError,
    UnSupportedMediaTypeException
)


class TestPrivacyException:
    """Test PrivacyException base class"""

    def test_privacy_exception_creation(self):
        """Test creating a PrivacyException"""
        exception = PrivacyException("Test error message")
        assert "Test error message" in str(exception)
        assert hasattr(exception, 'status_code')

    def test_privacy_exception_has_status_code(self):
        """Test exception has status_code attribute"""
        exception = PrivacyException("Error")
        assert hasattr(exception, 'status_code')

    def test_privacy_exception_raising(self):
        """Test raising PrivacyException"""
        with pytest.raises(PrivacyException) as exc_info:
            raise PrivacyException("Test exception")
        assert "Test exception" in str(exc_info.value)


class TestPrivacyNotFoundError:
    """Test PrivacyNotFoundError"""

    def test_not_found_error_creation(self):
        """Test creating PrivacyNotFoundError"""
        error = PrivacyNotFoundError("test_resource")
        assert hasattr(error, 'status_code')
        assert hasattr(error, 'detail')
        assert isinstance(error, PrivacyException)

    def test_not_found_error_status_code(self):
        """Test NotFoundError has 404 status code"""
        error = PrivacyNotFoundError("resource")
        assert error.status_code == 404

    def test_not_found_error_raising(self):
        """Test raising PrivacyNotFoundError"""
        with pytest.raises(PrivacyNotFoundError):
            raise PrivacyNotFoundError("Entity not found")

    def test_not_found_error_inheritance(self):
        """Test that NotFoundError inherits from PrivacyException"""
        error = PrivacyNotFoundError("test")
        assert isinstance(error, PrivacyException)
        assert isinstance(error, Exception)


class TestPrivacyNameNotEmptyError:
    """Test PrivacyNameNotEmptyError"""

    def test_name_not_empty_error_creation(self):
        """Test creating PrivacyNameNotEmptyError"""
        error = PrivacyNameNotEmptyError("test_name")
        assert hasattr(error, 'status_code')
        assert hasattr(error, 'detail')
        assert isinstance(error, PrivacyException)

    def test_name_not_empty_error_status_code(self):
        """Test NameNotEmptyError has 409 status code"""
        error = PrivacyNameNotEmptyError("name")
        assert error.status_code == 409

    def test_name_not_empty_error_raising(self):
        """Test raising PrivacyNameNotEmptyError"""
        with pytest.raises(PrivacyNameNotEmptyError):
            raise PrivacyNameNotEmptyError("Name is required")

    def test_name_not_empty_error_inheritance(self):
        """Test inheritance chain"""
        error = PrivacyNameNotEmptyError("test")
        assert isinstance(error, PrivacyException)
        assert isinstance(error, Exception)


class TestUnSupportedMediaTypeException:
    """Test UnSupportedMediaTypeException"""

    def test_unsupported_media_type_creation(self):
        """Test creating UnSupportedMediaTypeException"""
        error = UnSupportedMediaTypeException("application/xml")
        assert hasattr(error, 'status_code')
        assert hasattr(error, 'message')

    def test_unsupported_media_type_status_code(self):
        """Test exception has 415 status code"""
        error = UnSupportedMediaTypeException("text/plain")
        assert error.status_code == 415

    def test_unsupported_media_type_message(self):
        """Test exception message contains content type"""
        content_type = "application/xml"
        error = UnSupportedMediaTypeException(content_type)
        assert content_type in error.message

    def test_unsupported_media_type_raising(self):
        """Test raising UnSupportedMediaTypeException"""
        with pytest.raises(UnSupportedMediaTypeException):
            raise UnSupportedMediaTypeException("invalid/type")


class TestExceptionHandling:
    """Test exception handling scenarios"""

    def test_catch_privacy_exception(self):
        """Test catching PrivacyException"""
        try:
            raise PrivacyException("Test error")
        except PrivacyException as e:
            assert "Test error" in str(e)
            assert hasattr(e, 'status_code')

    def test_catch_specific_exception_with_base_class(self):
        """Test catching specific exception with base class handler"""
        try:
            raise PrivacyNotFoundError("Not found")
        except PrivacyException as e:
            assert hasattr(e, 'detail')
            assert isinstance(e, PrivacyNotFoundError)

    def test_exception_hierarchy(self):
        """Test exception class hierarchy"""
        not_found = PrivacyNotFoundError("test")
        name_error = PrivacyNameNotEmptyError("test")
        
        assert isinstance(not_found, PrivacyException)
        assert isinstance(name_error, PrivacyException)
        assert not isinstance(not_found, PrivacyNameNotEmptyError)
        assert not isinstance(name_error, PrivacyNotFoundError)

    def test_multiple_exceptions_different_status_codes(self):
        """Test different exceptions have different status codes"""
        base_error = PrivacyException("base")
        not_found = PrivacyNotFoundError("nf")
        name_error = PrivacyNameNotEmptyError("ne")
        media_error = UnSupportedMediaTypeException("me")
        
        assert hasattr(base_error, 'status_code')
        assert not_found.status_code == 404
        assert name_error.status_code == 409
        assert media_error.status_code == 415


class TestExceptionHandlerFunctions:
    """Test suite for exception handler functions (lines 62, 70, 76)."""
    
    def test_validation_error_handler(self):
        """Test validation_error_handler function (line 62)."""
        from privacy.exception.exception import validation_error_handler
        from fastapi.exceptions import RequestValidationError
        from pydantic import ValidationError
        
        # Create a mock RequestValidationError
        mock_exc = MagicMock(spec=RequestValidationError)
        mock_exc.errors.return_value = [
            {'loc': ('body', 'field'), 'msg': 'field required', 'type': 'value_error.missing'}
        ]
        
        # Call the handler
        response = validation_error_handler(mock_exc)
        
        # Verify response
        assert response.status_code == 422
        assert hasattr(response, 'body')
    
    def test_http_exception_handler(self):
        """Test http_exception_handler function (line 70)."""
        from privacy.exception.exception import http_exception_handler
        
        # Create a mock HTTP exception
        mock_exc = MagicMock()
        mock_exc.status_code = 400
        mock_exc.detail = "Bad Request"
        
        # Call the handler
        response = http_exception_handler(mock_exc)
        
        # Verify response (line 70-73)
        assert response.status_code == 400
        assert hasattr(response, 'body')
    
    def test_unsupported_mediatype_error_handler(self):
        """Test unsupported_mediatype_error_handler function (line 76)."""
        from privacy.exception.exception import unsupported_mediatype_error_handler, UnSupportedMediaTypeException
        
        # Create an UnSupportedMediaTypeException
        exc = UnSupportedMediaTypeException("application/xml")
        
        # Call the handler
        response = unsupported_mediatype_error_handler(exc)
        
        # Verify response (line 76-79)
        assert response.status_code == 415
        assert hasattr(response, 'body')

