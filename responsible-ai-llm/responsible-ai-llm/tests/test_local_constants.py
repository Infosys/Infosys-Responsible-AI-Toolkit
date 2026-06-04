'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import pytest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from llm.constants.local_constants import (
    DELTED_SUCCESS_MESSAGE,
    USECASE_ALREADY_EXISTS,
    USECASE_NOT_FOUND_ERROR,
    USECASE_NAME_VALIDATION_ERROR,
    SPACE_DELIMITER,
    PLACEHOLDER_TEXT
)


class TestLocalConstants:
    """Test suite for local constants validation"""
    
    def test_deleted_success_message(self):
        """Test DELETED_SUCCESS_MESSAGE constant"""
        assert isinstance(DELTED_SUCCESS_MESSAGE, str)
        assert len(DELTED_SUCCESS_MESSAGE) > 0
        assert "Successfully deleted" in DELTED_SUCCESS_MESSAGE
    
    def test_usecase_already_exists(self):
        """Test USECASE_ALREADY_EXISTS constant"""
        assert isinstance(USECASE_ALREADY_EXISTS, str)
        assert "already exists" in USECASE_ALREADY_EXISTS
        assert PLACEHOLDER_TEXT in USECASE_ALREADY_EXISTS
    
    def test_usecase_not_found_error(self):
        """Test USECASE_NOT_FOUND_ERROR constant"""
        assert isinstance(USECASE_NOT_FOUND_ERROR, str)
        assert "Not Found" in USECASE_NOT_FOUND_ERROR
        assert PLACEHOLDER_TEXT in USECASE_NOT_FOUND_ERROR
    
    def test_usecase_name_validation_error(self):
        """Test USECASE_NAME_VALIDATION_ERROR constant"""
        assert isinstance(USECASE_NAME_VALIDATION_ERROR, str)
        assert "empty" in USECASE_NAME_VALIDATION_ERROR.lower()
    
    def test_space_delimiter(self):
        """Test SPACE_DELIMITER constant"""
        assert SPACE_DELIMITER == " "
        assert isinstance(SPACE_DELIMITER, str)
    
    def test_placeholder_text(self):
        """Test PLACEHOLDER_TEXT constant"""
        assert PLACEHOLDER_TEXT == "PLACEHOLDER_TEXT"
        assert isinstance(PLACEHOLDER_TEXT, str)
    
    def test_constants_not_none(self):
        """Test that all constants are not None"""
        assert DELTED_SUCCESS_MESSAGE is not None
        assert USECASE_ALREADY_EXISTS is not None
        assert USECASE_NOT_FOUND_ERROR is not None
        assert USECASE_NAME_VALIDATION_ERROR is not None
        assert SPACE_DELIMITER is not None
        assert PLACEHOLDER_TEXT is not None
    
    def test_placeholder_in_error_messages(self):
        """Test placeholder text is used in error messages for substitution"""
        assert USECASE_ALREADY_EXISTS.count(PLACEHOLDER_TEXT) >= 1
        assert USECASE_NOT_FOUND_ERROR.count(PLACEHOLDER_TEXT) >= 1
    
    def test_constants_string_format(self):
        """Test constants are properly formatted strings"""
        constants = [
            DELTED_SUCCESS_MESSAGE,
            USECASE_ALREADY_EXISTS,
            USECASE_NOT_FOUND_ERROR,
            USECASE_NAME_VALIDATION_ERROR
        ]
        for constant in constants:
            assert isinstance(constant, str)
            assert len(constant) > 0
            # Check they don't have leading/trailing spaces
            assert constant == constant.strip()
    
    def test_message_substitution_pattern(self):
        """Test that error messages can be used with string substitution"""
        message = USECASE_ALREADY_EXISTS.replace(PLACEHOLDER_TEXT, "TestUsecase")
        assert "TestUsecase" in message
        assert PLACEHOLDER_TEXT not in message
    
    def test_error_message_with_different_values(self):
        """Test error messages with different placeholder values"""
        test_values = ["MyUsecase", "TestCase123", "Special-Case"]
        
        for value in test_values:
            message = USECASE_ALREADY_EXISTS.replace(PLACEHOLDER_TEXT, value)
            assert value in message
            
            not_found = USECASE_NOT_FOUND_ERROR.replace(PLACEHOLDER_TEXT, value)
            assert value in not_found
