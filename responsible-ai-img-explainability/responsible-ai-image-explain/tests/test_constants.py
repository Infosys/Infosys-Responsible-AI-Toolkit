"""
Unit tests for local constants
Tests constant values used across the application
"""
import pytest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from image_explain.constants.local_constants import (
    DELTED_SUCCESS_MESSAGE,
    USECASE_ALREADY_EXISTS,
    USECASE_NOT_FOUND_ERROR,
    USECASE_NAME_VALIDATION_ERROR,
    SPACE_DELIMITER,
    PLACEHOLDER_TEXT
)


class TestLocalConstants:
    """Test suite for local constants validation"""
    
    def test_deleted_success_message_constant(self):
        """Test DELTED_SUCCESS_MESSAGE constant is properly defined"""
        assert DELTED_SUCCESS_MESSAGE is not None
        assert isinstance(DELTED_SUCCESS_MESSAGE, str)
        assert len(DELTED_SUCCESS_MESSAGE) > 0
    
    def test_usecase_already_exists_constant(self):
        """Test USECASE_ALREADY_EXISTS constant contains placeholder"""
        assert USECASE_ALREADY_EXISTS is not None
        assert isinstance(USECASE_ALREADY_EXISTS, str)
        assert PLACEHOLDER_TEXT in USECASE_ALREADY_EXISTS
    
    def test_usecase_not_found_error_constant(self):
        """Test USECASE_NOT_FOUND_ERROR constant contains placeholder"""
        assert USECASE_NOT_FOUND_ERROR is not None
        assert isinstance(USECASE_NOT_FOUND_ERROR, str)
        assert PLACEHOLDER_TEXT in USECASE_NOT_FOUND_ERROR
    
    def test_usecase_name_validation_error_constant(self):
        """Test USECASE_NAME_VALIDATION_ERROR constant is properly defined"""
        assert USECASE_NAME_VALIDATION_ERROR is not None
        assert isinstance(USECASE_NAME_VALIDATION_ERROR, str)
        assert len(USECASE_NAME_VALIDATION_ERROR) > 0
    
    def test_space_delimiter_constant(self):
        """Test SPACE_DELIMITER constant is a space"""
        assert SPACE_DELIMITER == " "
        assert isinstance(SPACE_DELIMITER, str)
    
    def test_placeholder_text_constant(self):
        """Test PLACEHOLDER_TEXT constant is properly defined"""
        assert PLACEHOLDER_TEXT is not None
        assert isinstance(PLACEHOLDER_TEXT, str)
        assert PLACEHOLDER_TEXT == "PLACEHOLDER_TEXT"
    
    def test_message_formatting_with_placeholder(self):
        """Test placeholder replacement in messages"""
        test_name = "test_usecase"
        result = USECASE_NOT_FOUND_ERROR.replace(PLACEHOLDER_TEXT, test_name)
        assert test_name in result
        assert PLACEHOLDER_TEXT not in result
    
    def test_all_constants_are_strings(self):
        """Test all constants are string type"""
        constants = [
            DELTED_SUCCESS_MESSAGE,
            USECASE_ALREADY_EXISTS,
            USECASE_NOT_FOUND_ERROR,
            USECASE_NAME_VALIDATION_ERROR,
            SPACE_DELIMITER,
            PLACEHOLDER_TEXT
        ]
        for const in constants:
            assert isinstance(const, str), f"Constant {const} is not a string"
    
    def test_message_integrity(self):
        """Test message constants are not empty and have meaningful content"""
        messages = {
            'DELTED_SUCCESS_MESSAGE': DELTED_SUCCESS_MESSAGE,
            'USECASE_ALREADY_EXISTS': USECASE_ALREADY_EXISTS,
            'USECASE_NOT_FOUND_ERROR': USECASE_NOT_FOUND_ERROR,
            'USECASE_NAME_VALIDATION_ERROR': USECASE_NAME_VALIDATION_ERROR,
        }
        for name, msg in messages.items():
            assert len(msg) > 0, f"{name} is empty"
            assert msg.strip() == msg, f"{name} has leading/trailing whitespace"
