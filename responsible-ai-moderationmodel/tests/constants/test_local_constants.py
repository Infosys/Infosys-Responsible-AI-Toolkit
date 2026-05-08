"""
Unit tests for local_constants module.
Tests that all constants are defined correctly.
"""
import pytest


class TestLocalConstants:
    """Test cases for local constants."""

    def test_constants_are_defined(self):
        """Test that all required constants are defined."""
        from constants.local_constants import (
            DELTED_SUCCESS_MESSAGE,
            USECASE_ALREADY_EXISTS,
            USECASE_NOT_FOUND_ERROR,
            USECASE_NAME_VALIDATION_ERROR,
            SPACE_DELIMITER,
            PLACEHOLDER_TEXT,
            HTTP_STATUS_BAD_REQUEST,
            HTTP_STATUS_NOT_FOUND,
            HTTP_STATUS_INTERNAL_SERVER_ERROR,
            HTTP_STATUS_UNPROCESSABLE_ENTITY,
            HTTP_STATUS_FORBIDDEN,
            HTTP_STATUS_SUCCESS,
            HTTP_STATUS_CUSTOM,
            HTTP_STATUS_SERVICE_UNAVAILABLE,
        )

        # Assert constants have expected values
        assert DELTED_SUCCESS_MESSAGE == "Successfully deleted the usecase :"
        assert USECASE_ALREADY_EXISTS == "Usecase with name PLACEHOLDER_TEXT already exists"
        assert USECASE_NOT_FOUND_ERROR == "Usecase id PLACEHOLDER_TEXT Not Found"
        assert USECASE_NAME_VALIDATION_ERROR == "Usecase name should not be empty"
        assert SPACE_DELIMITER == " "
        assert PLACEHOLDER_TEXT == "PLACEHOLDER_TEXT"

    def test_http_status_codes(self):
        """Test that HTTP status codes are correct."""
        from constants.local_constants import (
            HTTP_STATUS_BAD_REQUEST,
            HTTP_STATUS_NOT_FOUND,
            HTTP_STATUS_INTERNAL_SERVER_ERROR,
            HTTP_STATUS_UNPROCESSABLE_ENTITY,
            HTTP_STATUS_FORBIDDEN,
            HTTP_STATUS_SUCCESS,
            HTTP_STATUS_CUSTOM,
            HTTP_STATUS_SERVICE_UNAVAILABLE,
        )

        assert HTTP_STATUS_BAD_REQUEST == 400
        assert HTTP_STATUS_NOT_FOUND == 404
        assert HTTP_STATUS_INTERNAL_SERVER_ERROR == 500
        assert HTTP_STATUS_UNPROCESSABLE_ENTITY == 422
        assert HTTP_STATUS_FORBIDDEN == 403
        assert HTTP_STATUS_SUCCESS == 200
        assert HTTP_STATUS_CUSTOM == 310
        assert HTTP_STATUS_SERVICE_UNAVAILABLE == 503

    def test_placeholder_text_replacement(self):
        """Test that placeholder text can be used for replacement."""
        from constants.local_constants import USECASE_NOT_FOUND_ERROR, PLACEHOLDER_TEXT

        test_name = "test_usecase_123"
        result = USECASE_NOT_FOUND_ERROR.replace(PLACEHOLDER_TEXT, test_name)
        assert result == f"Usecase id {test_name} Not Found"

    def test_constants_are_strings(self):
        """Test that message constants are strings."""
        from constants.local_constants import (
            DELTED_SUCCESS_MESSAGE,
            USECASE_ALREADY_EXISTS,
            USECASE_NOT_FOUND_ERROR,
            USECASE_NAME_VALIDATION_ERROR,
        )

        assert isinstance(DELTED_SUCCESS_MESSAGE, str)
        assert isinstance(USECASE_ALREADY_EXISTS, str)
        assert isinstance(USECASE_NOT_FOUND_ERROR, str)
        assert isinstance(USECASE_NAME_VALIDATION_ERROR, str)

    def test_constants_are_integers(self):
        """Test that HTTP status codes are integers."""
        from constants.local_constants import (
            HTTP_STATUS_BAD_REQUEST,
            HTTP_STATUS_NOT_FOUND,
            HTTP_STATUS_INTERNAL_SERVER_ERROR,
        )

        assert isinstance(HTTP_STATUS_BAD_REQUEST, int)
        assert isinstance(HTTP_STATUS_NOT_FOUND, int)
        assert isinstance(HTTP_STATUS_INTERNAL_SERVER_ERROR, int)
