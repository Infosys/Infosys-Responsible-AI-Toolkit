"""
Unit tests for constants module
"""
import pytest
from privacy.constants.local_constants import DELTED_SUCCESS_MESSAGE


class TestLocalConstants:
    """Test local constants"""

    def test_deleted_success_message_exists(self):
        """Test DELTED_SUCCESS_MESSAGE constant exists"""
        assert DELTED_SUCCESS_MESSAGE is not None

    def test_deleted_success_message_is_string(self):
        """Test constant is a string"""
        assert isinstance(DELTED_SUCCESS_MESSAGE, str)

    def test_deleted_success_message_not_empty(self):
        """Test constant is not empty"""
        assert len(DELTED_SUCCESS_MESSAGE) > 0
