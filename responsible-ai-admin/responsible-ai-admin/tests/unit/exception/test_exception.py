"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Unit tests for exception.py
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


@pytest.mark.unit
class TestRaiAdminException:
    """Test cases for RaiAdminException base class"""

    def test_rai_admin_exception_creation(self):
        """Test RaiAdminException instantiation"""
        from rai_admin.exception.exception import RaiAdminException
        
        error = RaiAdminException("Test error message")
        
        assert str(error) == "Test error message"
        assert hasattr(error, 'status_code')

    def test_rai_admin_exception_inheritance(self):
        """Test RaiAdminException inherits from Exception"""
        from rai_admin.exception.exception import RaiAdminException
        
        assert issubclass(RaiAdminException, Exception)


@pytest.mark.unit
class TestRaiAdminNotFoundError:
    """Test cases for RaiAdminNotFoundError"""

    def test_not_found_error_creation(self):
        """Test RaiAdminNotFoundError instantiation"""
        from rai_admin.exception.exception import RaiAdminNotFoundError
        
        error = RaiAdminNotFoundError("test_resource")
        
        assert hasattr(error, 'status_code')
        assert hasattr(error, 'detail')
        assert "test_resource" in error.detail or "not found" in error.detail.lower()

    def test_not_found_error_inheritance(self):
        """Test RaiAdminNotFoundError inherits from RaiAdminException"""
        from rai_admin.exception.exception import RaiAdminNotFoundError, RaiAdminException
        
        assert issubclass(RaiAdminNotFoundError, RaiAdminException)


@pytest.mark.unit
class TestRaiAdminNameNotEmptyError:
    """Test cases for RaiAdminNameNotEmptyError"""

    def test_name_not_empty_error_creation(self):
        """Test RaiAdminNameNotEmptyError instantiation"""
        from rai_admin.exception.exception import RaiAdminNameNotEmptyError
        
        error = RaiAdminNameNotEmptyError("test_name")
        
        assert hasattr(error, 'status_code')
        assert hasattr(error, 'detail')

    def test_name_not_empty_error_inheritance(self):
        """Test RaiAdminNameNotEmptyError inherits from RaiAdminException"""
        from rai_admin.exception.exception import RaiAdminNameNotEmptyError, RaiAdminException
        
        assert issubclass(RaiAdminNameNotEmptyError, RaiAdminException)


@pytest.mark.unit
class TestUnSupportedMediaTypeException:
    """Test cases for UnSupportedMediaTypeException"""

    def test_unsupported_media_type_creation(self):
        """Test UnSupportedMediaTypeException instantiation"""
        from rai_admin.exception.exception import UnSupportedMediaTypeException
        
        error = UnSupportedMediaTypeException("application/xml")
        
        assert hasattr(error, 'status_code')
        assert hasattr(error, 'message')
        assert "application/xml" in error.message

    def test_unsupported_media_type_inheritance(self):
        """Test UnSupportedMediaTypeException inherits from Exception"""
        from rai_admin.exception.exception import UnSupportedMediaTypeException
        
        assert issubclass(UnSupportedMediaTypeException, Exception)


@pytest.mark.unit
class TestExceptionHandlers:
    """Test cases for exception handler functions"""

    def test_validation_error_handler(self):
        """Test validation_error_handler function"""
        from rai_admin.exception.exception import validation_error_handler
        
        # Create a mock RequestValidationError
        mock_error = Mock(spec=RequestValidationError)
        mock_error.errors.return_value = [
            {
                "loc": ["body", "field"],
                "msg": "field required",
                "type": "value_error.missing"
            }
        ]
        
        response = validation_error_handler(mock_error)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 422

    def test_http_exception_handler(self):
        """Test http_exception_handler function"""
        from rai_admin.exception.exception import http_exception_handler
        
        # Create a mock HTTP exception
        mock_exc = Mock()
        mock_exc.status_code = 404
        mock_exc.detail = "Resource not found"
        
        response = http_exception_handler(mock_exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 404

    def test_unsupported_mediatype_error_handler(self):
        """Test unsupported_mediatype_error_handler function"""
        from rai_admin.exception.exception import (
            unsupported_mediatype_error_handler,
            UnSupportedMediaTypeException
        )
        
        exc = UnSupportedMediaTypeException("application/xml")
        response = unsupported_mediatype_error_handler(exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == exc.status_code

    def test_http_exception_handler_with_string_detail(self):
        """Test http_exception_handler with string detail"""
        from rai_admin.exception.exception import http_exception_handler
        
        mock_exc = Mock()
        mock_exc.status_code = 500
        mock_exc.detail = "Internal server error"
        
        response = http_exception_handler(mock_exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
