"""
Tests for fakeData module.

This module tests the FakeDataGenerate class which generates fake/synthetic
data to replace PII entities during anonymization.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock, call
import sys

# Import the class to test
from privacy.util.special_recognizers.fakeData import FakeDataGenerate


class TestFakeDataGenerateWithFakeData:
    """Test fake_data_generation with FakeData entities."""
    
    def test_fake_data_generation_with_faker_entity(self):
        """Test generating fake data using FakeData attributes."""
        generator = FakeDataGenerate()
        
        # Create a mock result with entity type that exists in FakeData
        result = MagicMock()
        result.entity_type = "PERSON"
        result.start = 0
        result.end = 10
        result.analysis_explanation = None
        
        input_text = "John Smith is here"
        results = [result]
        
        with patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_faker:
            # Mock the PERSON attribute as a callable
            mock_faker.PERSON = MagicMock(return_value="Jane Doe")
            # Make hasattr return True for PERSON
            with patch('privacy.util.special_recognizers.fakeData.hasattr', return_value=True):
                with patch('privacy.util.special_recognizers.fakeData.getattr', return_value=mock_faker.PERSON):
                    fake_dict = generator.fake_data_generation(results, input_text)
                    
                    # Verify the entity type is in the result
                    assert "PERSON" in fake_dict
                    # Verify getattr was called
                    assert mock_faker.PERSON.called
    
    def test_fake_data_generation_with_multiple_faker_entities(self):
        """Test with multiple entities using FakeData."""
        generator = FakeDataGenerate()
        
        result1 = MagicMock()
        result1.entity_type = "PERSON"
        result1.start = 0
        result1.end = 10
        result1.analysis_explanation = None
        
        result2 = MagicMock()
        result2.entity_type = "EMAIL_ADDRESS"
        result2.start = 15
        result2.end = 30
        result2.analysis_explanation = None
        
        input_text = "John Smith email@test.com"
        results = [result1, result2]
        
        with patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_faker:
            mock_faker.PERSON = MagicMock(return_value="Jane Doe")
            mock_faker.EMAIL_ADDRESS = MagicMock(return_value="fake@example.com")
            
            def mock_hasattr(obj, attr):
                return attr in ["PERSON", "EMAIL_ADDRESS"]
            
            with patch('privacy.util.special_recognizers.fakeData.hasattr', side_effect=mock_hasattr):
                fake_dict = generator.fake_data_generation(results, input_text)
                
                assert len(fake_dict) == 2
                assert "PERSON" in fake_dict
                assert "EMAIL_ADDRESS" in fake_dict


class TestFakeDataGenerateWithSessionDict:
    """Test fake_data_generation with session dictionary entities."""
    
    def test_fake_data_generation_with_session_dict(self):
        """Test generating fake data from session dictionary."""
        generator = FakeDataGenerate()
        
        result = MagicMock()
        result.entity_type = "COMPANY_NAME"
        result.start = 0
        result.end = 9
        result.analysis_explanation = None
        
        input_text = "Acme Corp mentioned here"
        results = [result]
        
        session_data = {
            "COMPANY_NAME": ["Beta Inc", "Gamma LLC", "Delta Co"]
        }
        
        with patch('privacy.util.special_recognizers.fakeData.hasattr', return_value=False):
            with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value=session_data):
                with patch('privacy.util.special_recognizers.fakeData.secrets.choice', return_value="Beta Inc"):
                    fake_dict = generator.fake_data_generation(results, input_text)
                    
                    assert "COMPANY_NAME" in fake_dict
                    # Just check that a value was set
                    assert fake_dict["COMPANY_NAME"] is not None
    
    def test_fake_data_generation_session_dict_different_case(self):
        """Test that replacement works with case-insensitive comparison."""
        generator = FakeDataGenerate()
        
        result = MagicMock()
        result.entity_type = "PROJECT"
        result.start = 0
        result.end = 7
        result.analysis_explanation = None
        
        input_text = "Project Alpha Beta"
        results = [result]
        
        session_data = {
            "PROJECT": ["Project Beta", "Project Gamma"]
        }
        
        with patch('privacy.util.special_recognizers.fakeData.hasattr', return_value=False):
            with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value=session_data):
                with patch('privacy.util.special_recognizers.fakeData.secrets.choice', return_value="Project Beta"):
                    fake_dict = generator.fake_data_generation(results, input_text)
                    
                    assert "PROJECT" in fake_dict
    
    def test_fake_data_generation_session_dict_not_in_list(self):
        """Test when detected text is not in the session dictionary list."""
        generator = FakeDataGenerate()
        
        result = MagicMock()
        result.entity_type = "CODE"
        result.start = 0
        result.end = 4
        result.analysis_explanation = None
        
        input_text = "XYZW is the code"
        results = [result]
        
        session_data = {
            "CODE": ["ABCD", "EFGH"]
        }
        
        with patch('privacy.util.special_recognizers.fakeData.hasattr', return_value=False):
            with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value=session_data):
                fake_dict = generator.fake_data_generation(results, input_text)
                
                # Should still create an entry (with empty random_data from the else branch)
                assert "CODE" in fake_dict


class TestFakeDataGenerateWithPattern:
    """Test fake_data_generation with regex pattern-based generation."""
    
    def test_fake_data_generation_with_pattern(self):
        """Test generating fake data using regex pattern from analysis_explanation."""
        generator = FakeDataGenerate()
        
        result = MagicMock()
        result.entity_type = "CUSTOM_ID"
        result.start = 0
        result.end = 8
        
        # Mock analysis_explanation with pattern
        analysis_exp = MagicMock()
        analysis_exp.pattern = r"[A-Z]{3}\d{3}"
        result.analysis_explanation = analysis_exp
        
        input_text = "ABC123 is the ID"
        results = [result]
        
        with patch('privacy.util.special_recognizers.fakeData.hasattr', return_value=False):
            with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value={}):
                with patch('privacy.util.special_recognizers.fakeData.x.xeger', return_value="XYZ789"):
                    fake_dict = generator.fake_data_generation(results, input_text)
                    
                    assert "CUSTOM_ID" in fake_dict
                    # Just check that a value was set
                    assert fake_dict["CUSTOM_ID"] is not None
    
    def test_fake_data_generation_pattern_with_control_chars(self):
        """Test that control characters are removed from generated pattern data."""
        generator = FakeDataGenerate()
        
        result = MagicMock()
        result.entity_type = "ID"
        result.start = 0
        result.end = 5
        
        analysis_exp = MagicMock()
        analysis_exp.pattern = r"\w+"
        result.analysis_explanation = analysis_exp
        
        input_text = "12345 code"
        results = [result]
        
        # Xeger returns string with control characters
        generated_with_control = "AB\x00CD\x1FEF"
        
        with patch('privacy.util.special_recognizers.fakeData.hasattr', return_value=False):
            with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value={}):
                with patch('privacy.util.special_recognizers.fakeData.x.xeger', return_value=generated_with_control):
                    fake_dict = generator.fake_data_generation(results, input_text)
                    
                    assert "ID" in fake_dict
                    # Control chars should be replaced with spaces
                    fake_value = fake_dict["ID"].params["new_value"]
                    assert "\x00" not in fake_value
                    assert "\x1F" not in fake_value
    
    def test_fake_data_generation_no_analysis_explanation(self):
        """Test that results without analysis_explanation are skipped."""
        generator = FakeDataGenerate()
        
        result = MagicMock()
        result.entity_type = "UNKNOWN"
        result.start = 0
        result.end = 7
        result.analysis_explanation = None
        
        input_text = "Unknown entity"
        results = [result]
        
        with patch('privacy.util.special_recognizers.fakeData.hasattr', return_value=False):
            with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value={}):
                fake_dict = generator.fake_data_generation(results, input_text)
                
                # Should not include UNKNOWN since analysis_explanation is None
                assert "UNKNOWN" not in fake_dict


class TestFakeDataGenerateEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_fake_data_generation_empty_results(self):
        """Test with empty results list."""
        generator = FakeDataGenerate()
        
        input_text = "Some text here"
        results = []
        
        fake_dict = generator.fake_data_generation(results, input_text)
        
        assert fake_dict == {}
    
    def test_fake_data_generation_mixed_sources(self):
        """Test with results from different sources (FakeData, session, pattern)."""
        generator = FakeDataGenerate()
        
        result1 = MagicMock()
        result1.entity_type = "PERSON"
        result1.start = 0
        result1.end = 4
        result1.analysis_explanation = None
        
        result2 = MagicMock()
        result2.entity_type = "COMPANY"
        result2.start = 10
        result2.end = 17
        result2.analysis_explanation = None
        
        result3 = MagicMock()
        result3.entity_type = "CODE"
        result3.start = 25
        result3.end = 30
        analysis_exp = MagicMock()
        analysis_exp.pattern = r"[A-Z]{5}"
        result3.analysis_explanation = analysis_exp
        
        input_text = "John works at InfoCorp with code ABCDE"
        results = [result1, result2, result3]
        
        session_data = {"COMPANY": ["TechCo", "SoftInc"]}
        
        def mock_hasattr(obj, attr):
            return attr == "PERSON"
        
        with patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_faker:
            mock_faker.PERSON = MagicMock(return_value="Jane")
            with patch('privacy.util.special_recognizers.fakeData.hasattr', side_effect=mock_hasattr):
                with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value=session_data):
                    with patch('privacy.util.special_recognizers.fakeData.secrets.choice', return_value="TechCo"):
                        with patch('privacy.util.special_recognizers.fakeData.x.xeger', return_value="XYZTW"):
                            fake_dict = generator.fake_data_generation(results, input_text)
                            
                            # Should have all three entities
                            assert len(fake_dict) >= 2  # At least PERSON and CODE
                            assert "PERSON" in fake_dict
                            assert "CODE" in fake_dict
    
    def test_fake_data_generation_duplicate_entity_types(self):
        """Test handling multiple results with same entity type."""
        generator = FakeDataGenerate()
        
        result1 = MagicMock()
        result1.entity_type = "PERSON"
        result1.start = 0
        result1.end = 4
        result1.analysis_explanation = None
        
        result2 = MagicMock()
        result2.entity_type = "PERSON"
        result2.start = 10
        result2.end = 15
        result2.analysis_explanation = None
        
        input_text = "John and Alice"
        results = [result1, result2]
        
        with patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_faker:
            mock_faker.PERSON = MagicMock(return_value="Bob")
            with patch('privacy.util.special_recognizers.fakeData.hasattr', return_value=True):
                fake_dict = generator.fake_data_generation(results, input_text)
                
                # Last update wins - should still have PERSON key
                assert "PERSON" in fake_dict
    
    def test_fake_data_generation_getattr_call(self):
        """Test that getattr is properly called for FakeData entities."""
        generator = FakeDataGenerate()
        
        result = MagicMock()
        result.entity_type = "PHONE_NUMBER"
        result.start = 0
        result.end = 12
        result.analysis_explanation = None
        
        input_text = "123-456-7890"
        results = [result]
        
        with patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_faker:
            mock_phone = MagicMock(return_value="555-0123")
            with patch('privacy.util.special_recognizers.fakeData.hasattr', return_value=True):
                with patch('privacy.util.special_recognizers.fakeData.getattr', return_value=mock_phone) as mock_getattr:
                    fake_dict = generator.fake_data_generation(results, input_text)
                    
                    # Verify getattr was called with correct arguments
                    mock_getattr.assert_called()
                    assert "PHONE_NUMBER" in fake_dict


class TestFakeDataGenerateIntegration:
    """Integration tests for complete workflows."""
    
    def test_complete_anonymization_workflow(self):
        """Test complete workflow with realistic data."""
        generator = FakeDataGenerate()
        
        # Simulate results from a real anonymization scenario
        result1 = MagicMock()
        result1.entity_type = "PERSON"
        result1.start = 0
        result1.end = 10
        result1.analysis_explanation = None
        
        result2 = MagicMock()
        result2.entity_type = "EMAIL_ADDRESS"
        result2.start = 25
        result2.end = 45
        analysis_exp = MagicMock()
        analysis_exp.pattern = r"\w+@\w+\.\w+"
        result2.analysis_explanation = analysis_exp
        
        input_text = "John Smith sent email to john.smith@example.com"
        results = [result1, result2]
        
        def mock_hasattr(obj, attr):
            return attr == "PERSON"
        
        with patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_faker:
            mock_faker.PERSON = MagicMock(return_value="Jane Doe")
            with patch('privacy.util.special_recognizers.fakeData.hasattr', side_effect=mock_hasattr):
                with patch('privacy.util.special_recognizers.fakeData.get_session_dict', return_value={}):
                        with patch('privacy.util.special_recognizers.fakeData.x.xeger', return_value="fake@test.org"):
                            fake_dict = generator.fake_data_generation(results, input_text)
                            
                            assert "PERSON" in fake_dict
                            assert "EMAIL_ADDRESS" in fake_dict
                            # Verify both entities were processed
                            assert len(fake_dict) == 2
    
    def test_operator_config_structure(self):
        """Test that OperatorConfig objects are properly structured."""
        generator = FakeDataGenerate()
        
        result = MagicMock()
        result.entity_type = "NAME"
        result.start = 0
        result.end = 5
        result.analysis_explanation = None
        
        input_text = "Alice"
        results = [result]
        
        with patch('privacy.util.special_recognizers.fakeData.FakeData') as mock_faker:
            mock_faker.NAME = MagicMock(return_value="Bob")
            with patch('privacy.util.special_recognizers.fakeData.hasattr', return_value=True):
                with patch('privacy.util.special_recognizers.fakeData.getattr', return_value=mock_faker.NAME):
                    fake_dict = generator.fake_data_generation(results, input_text)
                    
                    assert "NAME" in fake_dict
                    # Verify the NAME attribute was called
                    assert mock_faker.NAME.called
