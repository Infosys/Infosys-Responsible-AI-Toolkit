"""
Test suite for privacy.util.special_recognizers.fakeData module.

This module tests the FakeDataGenerate class and its fakeDataGeneration method
to achieve >90% code coverage.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from presidio_anonymizer.entities import OperatorConfig
import re
import secrets

# Import the module under test
from privacy.util.special_recognizers.fakeData import FakeDataGenerate, x


class TestFakeDataGenerate:
    """Comprehensive test suite for FakeDataGenerate class."""

    def test_fakeDataGeneration_with_fakedata_attribute_person(self):
        """Test fakeDataGeneration when FakeData has PERSON entity type."""
        mock_result = MagicMock()
        mock_result.entity_type = "PERSON"
        mock_result.start = 0
        mock_result.end = 4
        mock_result.analysis_explanation = None
        
        with patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            mock_fake_data.PERSON = MagicMock(return_value="Jane Doe")
            # Make hasattr return True
            type(mock_fake_data).PERSON = MagicMock(return_value="Jane Doe")
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "John Smith")
            
            assert "PERSON" in result
            assert isinstance(result["PERSON"], OperatorConfig)
            assert result["PERSON"].params["new_value"] == "Jane Doe"

    def test_fakeDataGeneration_with_fakedata_attribute_email(self):
        """Test fakeDataGeneration when FakeData has EMAIL_ADDRESS entity type."""
        mock_result = MagicMock()
        mock_result.entity_type = "EMAIL_ADDRESS"
        mock_result.start = 0
        mock_result.end = 15
        mock_result.analysis_explanation = None
        
        with patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            mock_fake_data.EMAIL_ADDRESS = MagicMock(return_value="fake@example.com")
            type(mock_fake_data).EMAIL_ADDRESS = MagicMock(return_value="fake@example.com")
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "test@example.com")
            
            assert "EMAIL_ADDRESS" in result
            assert isinstance(result["EMAIL_ADDRESS"], OperatorConfig)
            assert result["EMAIL_ADDRESS"].params["new_value"] == "fake@example.com"

    def test_fakeDataGeneration_with_fakedata_attribute_ssn(self):
        """Test fakeDataGeneration when FakeData has US_SSN entity type."""
        mock_result = MagicMock()
        mock_result.entity_type = "US_SSN"
        mock_result.start = 0
        mock_result.end = 11
        mock_result.analysis_explanation = None
        
        with patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            mock_fake_data.US_SSN = MagicMock(return_value="123-45-6789")
            type(mock_fake_data).US_SSN = MagicMock(return_value="123-45-6789")
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "987-65-4321")
            
            assert "US_SSN" in result
            assert isinstance(result["US_SSN"], OperatorConfig)

    def test_fakeDataGeneration_with_session_dict_matching_text(self):
        """Test fakeDataGeneration with session dict when text matches an entry."""
        mock_result = MagicMock()
        mock_result.entity_type = "CUSTOM_ENTITY"
        mock_result.start = 0
        mock_result.end = 6
        mock_result.analysis_explanation = None
        
        session_dict = {"CUSTOM_ENTITY": ["value1", "value2", "value3"]}
        
        with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value=session_dict), \
             patch('privacy.util.special_recognizers.fakeData.secrets.choice', return_value="value2"), \
             patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            
            # Make hasattr return False
            delattr(mock_fake_data, 'CUSTOM_ENTITY') if hasattr(mock_fake_data, 'CUSTOM_ENTITY') else None
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "value1")
            
            assert "CUSTOM_ENTITY" in result
            assert isinstance(result["CUSTOM_ENTITY"], OperatorConfig)
            assert result["CUSTOM_ENTITY"].params["new_value"] == "value2"

    def test_fakeDataGeneration_with_session_dict_case_insensitive_match(self):
        """Test fakeDataGeneration with session dict case-insensitive matching."""
        mock_result = MagicMock()
        mock_result.entity_type = "CUSTOM_ENTITY"
        mock_result.start = 0
        mock_result.end = 6
        mock_result.analysis_explanation = None
        
        session_dict = {"CUSTOM_ENTITY": ["Value1", "Value2", "Value3"]}
        
        with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value=session_dict), \
             patch('privacy.util.special_recognizers.fakeData.secrets.choice', return_value="Value2"), \
             patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            
            delattr(mock_fake_data, 'CUSTOM_ENTITY') if hasattr(mock_fake_data, 'CUSTOM_ENTITY') else None
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "value1")
            
            assert "CUSTOM_ENTITY" in result

    def test_fakeDataGeneration_with_session_dict_text_not_in_list(self):
        """Test fakeDataGeneration with session dict when text is not in the list."""
        mock_result = MagicMock()
        mock_result.entity_type = "CUSTOM_ENTITY"
        mock_result.start = 0
        mock_result.end = 10
        mock_result.analysis_explanation = None
        
        session_dict = {"CUSTOM_ENTITY": ["value1", "value2", "value3"]}
        
        with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value=session_dict), \
             patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            
            delattr(mock_fake_data, 'CUSTOM_ENTITY') if hasattr(mock_fake_data, 'CUSTOM_ENTITY') else None
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "not_in_list")
            
            assert "CUSTOM_ENTITY" in result
            assert result["CUSTOM_ENTITY"].params["new_value"] == ""

    def test_fakeDataGeneration_with_session_dict_same_value_retry(self):
        """Test fakeDataGeneration with session dict when same value is chosen first."""
        mock_result = MagicMock()
        mock_result.entity_type = "CUSTOM_ENTITY"
        mock_result.start = 0
        mock_result.end = 6
        mock_result.analysis_explanation = None
        
        session_dict = {"CUSTOM_ENTITY": ["value1", "value2", "value3"]}
        
        # First call returns same value (value1), second call returns different (value2)
        choice_side_effects = ["value1", "value2"]
        
        with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value=session_dict), \
             patch('privacy.util.special_recognizers.fakeData.secrets.choice', side_effect=choice_side_effects), \
             patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            
            delattr(mock_fake_data, 'CUSTOM_ENTITY') if hasattr(mock_fake_data, 'CUSTOM_ENTITY') else None
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "value1")
            
            assert "CUSTOM_ENTITY" in result
            assert result["CUSTOM_ENTITY"].params["new_value"] == "value2"

    def test_fakeDataGeneration_with_pattern_phone_number(self):
        """Test fakeDataGeneration with regex pattern for phone number."""
        mock_decision = MagicMock()
        mock_decision.pattern = r'\d{3}-\d{3}-\d{4}'
        
        mock_result = MagicMock()
        mock_result.entity_type = "PHONE_NUMBER"
        mock_result.start = 0
        mock_result.end = 12
        mock_result.analysis_explanation = mock_decision
        
        with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value={}), \
             patch('privacy.util.special_recognizers.fakeData.x.xeger', return_value="555-555-5555"), \
             patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            
            delattr(mock_fake_data, 'PHONE_NUMBER') if hasattr(mock_fake_data, 'PHONE_NUMBER') else None
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "123-456-7890")
            
            assert "PHONE_NUMBER" in result
            assert isinstance(result["PHONE_NUMBER"], OperatorConfig)
            assert result["PHONE_NUMBER"].params["new_value"] == "555-555-5555"

    def test_fakeDataGeneration_with_pattern_special_chars_removed(self):
        """Test fakeDataGeneration with pattern containing special characters that get removed."""
        mock_decision = MagicMock()
        mock_decision.pattern = r'[A-Z]{3}'
        
        mock_result = MagicMock()
        mock_result.entity_type = "CODE"
        mock_result.start = 0
        mock_result.end = 3
        mock_result.analysis_explanation = mock_decision
        
        # Xeger returns string with control characters
        with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value={}), \
             patch('privacy.util.special_recognizers.fakeData.x.xeger', return_value="ABC\x00\x1F"), \
             patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            
            delattr(mock_fake_data, 'CODE') if hasattr(mock_fake_data, 'CODE') else None
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "XYZ")
            
            assert "CODE" in result
            # Control characters should be replaced with spaces
            assert result["CODE"].params["new_value"] == "ABC  "

    def test_fakeDataGeneration_with_pattern_extended_ascii(self):
        """Test fakeDataGeneration with pattern containing extended ASCII characters."""
        mock_decision = MagicMock()
        mock_decision.pattern = r'[A-Z]{2}'
        
        mock_result = MagicMock()
        mock_result.entity_type = "TOKEN"
        mock_result.start = 0
        mock_result.end = 2
        mock_result.analysis_explanation = mock_decision
        
        # Xeger returns string with extended ASCII
        with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value={}), \
             patch('privacy.util.special_recognizers.fakeData.x.xeger', return_value="AB\xFF"), \
             patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            
            delattr(mock_fake_data, 'TOKEN') if hasattr(mock_fake_data, 'TOKEN') else None
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "CD")
            
            assert "TOKEN" in result
            # Extended ASCII should be replaced with space
            assert result["TOKEN"].params["new_value"] == "AB "

    def test_fakeDataGeneration_with_none_analysis_explanation(self):
        """Test fakeDataGeneration when analysis_explanation is None (continue case)."""
        mock_result = MagicMock()
        mock_result.entity_type = "UNKNOWN"
        mock_result.start = 0
        mock_result.end = 7
        mock_result.analysis_explanation = None
        
        with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value={}), \
             patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            
            delattr(mock_fake_data, 'UNKNOWN') if hasattr(mock_fake_data, 'UNKNOWN') else None
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "unknown")
            
            # Should return empty dict when analysis_explanation is None and no other match
            assert "UNKNOWN" not in result

    def test_fakeDataGeneration_multiple_results_mixed_types(self):
        """Test fakeDataGeneration with multiple results of different types."""
        mock_result1 = MagicMock()
        mock_result1.entity_type = "PERSON"
        mock_result1.start = 0
        mock_result1.end = 4
        mock_result1.analysis_explanation = None
        
        mock_result2 = MagicMock()
        mock_result2.entity_type = "EMAIL_ADDRESS"
        mock_result2.start = 5
        mock_result2.end = 20
        mock_result2.analysis_explanation = None
        
        mock_decision = MagicMock()
        mock_decision.pattern = r'\d{3}-\d{4}'
        
        mock_result3 = MagicMock()
        mock_result3.entity_type = "ZIP_CODE"
        mock_result3.start = 21
        mock_result3.end = 29
        mock_result3.analysis_explanation = mock_decision
        
        with patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data, \
             patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value={}), \
             patch('privacy.util.special_recognizers.fakeData.x.xeger', return_value="123-4567"):
            
            mock_fake_data.PERSON = MagicMock(return_value="Jane Doe")
            mock_fake_data.EMAIL_ADDRESS = MagicMock(return_value="jane@example.com")
            type(mock_fake_data).PERSON = MagicMock(return_value="Jane Doe")
            type(mock_fake_data).EMAIL_ADDRESS = MagicMock(return_value="jane@example.com")
            delattr(mock_fake_data, 'ZIP_CODE') if hasattr(mock_fake_data, 'ZIP_CODE') else None
            
            result = FakeDataGenerate.fakeDataGeneration(
                [mock_result1, mock_result2, mock_result3], 
                "John test@example.com 555-1234"
            )
            
            assert "PERSON" in result
            assert "EMAIL_ADDRESS" in result
            assert "ZIP_CODE" in result
            assert len(result) == 3

    def test_fakeDataGeneration_empty_results_list(self):
        """Test fakeDataGeneration with empty results list."""
        result = FakeDataGenerate.fakeDataGeneration([], "some text")
        
        assert result == {}

    def test_fakeDataGeneration_with_session_dict_single_value_list(self):
        """Test fakeDataGeneration with session dict containing two values."""
        mock_result = MagicMock()
        mock_result.entity_type = "SINGLE_ENTITY"
        mock_result.start = 0
        mock_result.end = 6
        mock_result.analysis_explanation = None
        
        session_dict = {"SINGLE_ENTITY": ["value1", "value2"]}
        
        with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value=session_dict), \
             patch('privacy.util.special_recognizers.fakeData.secrets.choice', return_value="value2"), \
             patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            
            delattr(mock_fake_data, 'SINGLE_ENTITY') if hasattr(mock_fake_data, 'SINGLE_ENTITY') else None
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "value1")
            
            assert "SINGLE_ENTITY" in result
            assert result["SINGLE_ENTITY"].params["new_value"] == "value2"

    def test_fakeDataGeneration_with_pattern_credit_card(self):
        """Test fakeDataGeneration with credit card pattern."""
        mock_decision = MagicMock()
        mock_decision.pattern = r'\d{4}-\d{4}-\d{4}-\d{4}'
        
        mock_result = MagicMock()
        mock_result.entity_type = "CREDIT_CARD"
        mock_result.start = 0
        mock_result.end = 19
        mock_result.analysis_explanation = mock_decision
        
        with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value={}), \
             patch('privacy.util.special_recognizers.fakeData.x.xeger', return_value="1234-5678-9012-3456"), \
             patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            
            delattr(mock_fake_data, 'CREDIT_CARD') if hasattr(mock_fake_data, 'CREDIT_CARD') else None
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "4532-1234-5678-9010")
            
            assert "CREDIT_CARD" in result
            assert result["CREDIT_CARD"].params["new_value"] == "1234-5678-9012-3456"

    def test_fakeDataGeneration_with_pattern_ip_address(self):
        """Test fakeDataGeneration with IP address pattern."""
        mock_decision = MagicMock()
        mock_decision.pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        
        mock_result = MagicMock()
        mock_result.entity_type = "IP_ADDRESS"
        mock_result.start = 0
        mock_result.end = 13
        mock_result.analysis_explanation = mock_decision
        
        with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value={}), \
             patch('privacy.util.special_recognizers.fakeData.x.xeger', return_value="192.168.1.100"), \
             patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            
            delattr(mock_fake_data, 'IP_ADDRESS') if hasattr(mock_fake_data, 'IP_ADDRESS') else None
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "10.0.0.1")
            
            assert "IP_ADDRESS" in result

    def test_fakeDataGeneration_with_pattern_alphanumeric(self):
        """Test fakeDataGeneration with alphanumeric pattern."""
        mock_decision = MagicMock()
        mock_decision.pattern = r'[A-Z0-9]{8}'
        
        mock_result = MagicMock()
        mock_result.entity_type = "ID"
        mock_result.start = 0
        mock_result.end = 8
        mock_result.analysis_explanation = mock_decision
        
        with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value={}), \
             patch('privacy.util.special_recognizers.fakeData.x.xeger', return_value="ABC12345"), \
             patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            
            delattr(mock_fake_data, 'ID') if hasattr(mock_fake_data, 'ID') else None
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "XYZ98765")
            
            assert "ID" in result
            assert result["ID"].params["new_value"] == "ABC12345"

    def test_fakeDataGeneration_with_session_dict_uppercase_matching(self):
        """Test fakeDataGeneration with session dict uppercase matching."""
        mock_result = MagicMock()
        mock_result.entity_type = "CUSTOM"
        mock_result.start = 0
        mock_result.end = 6
        mock_result.analysis_explanation = None
        
        session_dict = {"CUSTOM": ["VALUE1", "VALUE2", "VALUE3"]}
        
        with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value=session_dict), \
             patch('privacy.util.special_recognizers.fakeData.secrets.choice', return_value="VALUE3"), \
             patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            
            delattr(mock_fake_data, 'CUSTOM') if hasattr(mock_fake_data, 'CUSTOM') else None
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "VALUE1")
            
            assert "CUSTOM" in result
            assert result["CUSTOM"].params["new_value"] == "VALUE3"

    def test_fakeDataGeneration_with_multiple_fakedata_entities(self):
        """Test fakeDataGeneration with multiple FakeData entities in sequence."""
        mock_result1 = MagicMock()
        mock_result1.entity_type = "LOCATION"
        mock_result1.start = 0
        mock_result1.end = 7
        mock_result1.analysis_explanation = None
        
        mock_result2 = MagicMock()
        mock_result2.entity_type = "DATE_TIME"
        mock_result2.start = 8
        mock_result2.end = 18
        mock_result2.analysis_explanation = None
        
        with patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            mock_fake_data.LOCATION = MagicMock(return_value="New York")
            mock_fake_data.DATE_TIME = MagicMock(return_value="2025-12-30")
            type(mock_fake_data).LOCATION = MagicMock(return_value="New York")
            type(mock_fake_data).DATE_TIME = MagicMock(return_value="2025-12-30")
            
            result = FakeDataGenerate.fakeDataGeneration(
                [mock_result1, mock_result2],
                "Seattle 2024-01-01"
            )
            
            assert "LOCATION" in result
            assert "DATE_TIME" in result
            assert result["LOCATION"].params["new_value"] == "New York"
            assert result["DATE_TIME"].params["new_value"] == "2025-12-30"

    def test_fakeDataGeneration_with_pattern_complex_regex(self):
        """Test fakeDataGeneration with complex regex pattern."""
        mock_decision = MagicMock()
        mock_decision.pattern = r'[A-Z]{2}\d{2}[A-Z]{2}\d{4}'
        
        mock_result = MagicMock()
        mock_result.entity_type = "ACCOUNT_NUMBER"
        mock_result.start = 0
        mock_result.end = 10
        mock_result.analysis_explanation = mock_decision
        
        with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value={}), \
             patch('privacy.util.special_recognizers.fakeData.x.xeger', return_value="AB12CD3456"), \
             patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            
            delattr(mock_fake_data, 'ACCOUNT_NUMBER') if hasattr(mock_fake_data, 'ACCOUNT_NUMBER') else None
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "XY99ZW7890")
            
            assert "ACCOUNT_NUMBER" in result
            assert result["ACCOUNT_NUMBER"].params["new_value"] == "AB12CD3456"

    def test_fakeDataGeneration_session_dict_with_long_list(self):
        """Test fakeDataGeneration with session dict containing many values."""
        mock_result = MagicMock()
        mock_result.entity_type = "LARGE_LIST"
        mock_result.start = 0
        mock_result.end = 7
        mock_result.analysis_explanation = None
        
        long_list = [f"value{i}" for i in range(1, 51)]  # 50 values
        session_dict = {"LARGE_LIST": long_list}
        
        with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value=session_dict), \
             patch('privacy.util.special_recognizers.fakeData.secrets.choice', return_value="value25"), \
             patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            
            delattr(mock_fake_data, 'LARGE_LIST') if hasattr(mock_fake_data, 'LARGE_LIST') else None
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "value10")
            
            assert "LARGE_LIST" in result
            assert result["LARGE_LIST"].params["new_value"] == "value25"

    def test_fakeDataGeneration_with_pattern_clean_output(self):
        """Test fakeDataGeneration with pattern that generates clean output."""
        mock_decision = MagicMock()
        mock_decision.pattern = r'[A-Z]{5}'
        
        mock_result = MagicMock()
        mock_result.entity_type = "CODE"
        mock_result.start = 0
        mock_result.end = 5
        mock_result.analysis_explanation = mock_decision
        
        with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value={}), \
             patch('privacy.util.special_recognizers.fakeData.x.xeger', return_value="ABCDE"), \
             patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            
            delattr(mock_fake_data, 'CODE') if hasattr(mock_fake_data, 'CODE') else None
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "FGHIJ")
            
            assert "CODE" in result
            assert result["CODE"].params["new_value"] == "ABCDE"


class TestFakeDataGenerateEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_input_text(self):
        """Test with empty input text."""
        mock_result = MagicMock()
        mock_result.entity_type = "PERSON"
        mock_result.start = 0
        mock_result.end = 0
        mock_result.analysis_explanation = None
        
        with patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            mock_fake_data.PERSON = MagicMock(return_value="Jane")
            type(mock_fake_data).PERSON = MagicMock(return_value="Jane")
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "")
            
            assert "PERSON" in result

    def test_session_dict_empty_list(self):
        """Test with session dict containing empty list."""
        mock_result = MagicMock()
        mock_result.entity_type = "EMPTY_ENTITY"
        mock_result.start = 0
        mock_result.end = 4
        mock_result.analysis_explanation = None
        
        session_dict = {"EMPTY_ENTITY": []}
        
        with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value=session_dict), \
             patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            
            delattr(mock_fake_data, 'EMPTY_ENTITY') if hasattr(mock_fake_data, 'EMPTY_ENTITY') else None
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "test")
            
            assert "EMPTY_ENTITY" in result

    def test_special_characters_in_input(self):
        """Test with special characters in input text."""
        mock_result = MagicMock()
        mock_result.entity_type = "PERSON"
        mock_result.start = 0
        mock_result.end = 10
        mock_result.analysis_explanation = None
        
        with patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            mock_fake_data.PERSON = MagicMock(return_value="Jane Doe")
            type(mock_fake_data).PERSON = MagicMock(return_value="Jane Doe")
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "John@#$%^&")
            
            assert "PERSON" in result

    def test_unicode_in_input(self):
        """Test with unicode characters in input text."""
        mock_result = MagicMock()
        mock_result.entity_type = "PERSON"
        mock_result.start = 0
        mock_result.end = 5
        mock_result.analysis_explanation = None
        
        with patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            mock_fake_data.PERSON = MagicMock(return_value="Jane Doe")
            type(mock_fake_data).PERSON = MagicMock(return_value="Jane Doe")
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "José")
            
            assert "PERSON" in result

    def test_very_long_input_text(self):
        """Test with very long input text."""
        mock_result = MagicMock()
        mock_result.entity_type = "PERSON"
        mock_result.start = 0
        mock_result.end = 10
        mock_result.analysis_explanation = None
        
        long_text = "A" * 10000
        
        with patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            mock_fake_data.PERSON = MagicMock(return_value="Jane Doe")
            type(mock_fake_data).PERSON = MagicMock(return_value="Jane Doe")
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], long_text)
            
            assert "PERSON" in result


class TestFakeDataGenerateIntegration:
    """Integration tests to ensure all branches are covered."""

    def test_all_three_branches_in_sequence(self):
        """Test all three main branches (FakeData, session_dict, pattern) in one call."""
        # Branch 1: FakeData hasattr
        mock_result1 = MagicMock()
        mock_result1.entity_type = "PERSON"
        mock_result1.start = 0
        mock_result1.end = 4
        mock_result1.analysis_explanation = None
        
        # Branch 2: session_dict
        mock_result2 = MagicMock()
        mock_result2.entity_type = "CUSTOM"
        mock_result2.start = 5
        mock_result2.end = 11
        mock_result2.analysis_explanation = None
        
        # Branch 3: pattern
        mock_decision = MagicMock()
        mock_decision.pattern = r'\d{4}'
        mock_result3 = MagicMock()
        mock_result3.entity_type = "CODE"
        mock_result3.start = 12
        mock_result3.end = 16
        mock_result3.analysis_explanation = mock_decision
        
        session_dict = {"CUSTOM": ["value1", "value2"]}
        
        with patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data, \
             patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value=session_dict), \
             patch('privacy.util.special_recognizers.fakeData.secrets.choice', return_value="value2"), \
             patch('privacy.util.special_recognizers.fakeData.x.xeger', return_value="9999"):
            
            mock_fake_data.PERSON = MagicMock(return_value="Jane")
            type(mock_fake_data).PERSON = MagicMock(return_value="Jane")
            delattr(mock_fake_data, 'CUSTOM') if hasattr(mock_fake_data, 'CUSTOM') else None
            delattr(mock_fake_data, 'CODE') if hasattr(mock_fake_data, 'CODE') else None
            
            result = FakeDataGenerate.fakeDataGeneration(
                [mock_result1, mock_result2, mock_result3],
                "John value1 1234"
            )
            
            assert len(result) == 3
            assert "PERSON" in result
            assert "CUSTOM" in result
            assert "CODE" in result

    def test_pattern_with_multiple_control_chars(self):
        """Test pattern branch with multiple types of control characters."""
        mock_decision = MagicMock()
        mock_decision.pattern = r'[A-Z]{3}'
        
        mock_result = MagicMock()
        mock_result.entity_type = "TOKEN"
        mock_result.start = 0
        mock_result.end = 3
        mock_result.analysis_explanation = mock_decision
        
        # String with multiple control and extended ASCII chars
        bad_string = "ABC\x00\x01\x1F\x7F\xFF\xFE"
        
        with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value={}), \
             patch('privacy.util.special_recognizers.fakeData.x.xeger', return_value=bad_string), \
             patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_fake_data:
            
            delattr(mock_fake_data, 'TOKEN') if hasattr(mock_fake_data, 'TOKEN') else None
            
            result = FakeDataGenerate.fakeDataGeneration([mock_result], "XYZ")
            
            assert "TOKEN" in result
            # All control and extended ASCII chars should be replaced with spaces
            cleaned = result["TOKEN"].params["new_value"]
            assert "ABC" in cleaned
            assert "\x00" not in cleaned
            assert "\xFF" not in cleaned
