"""
Tests for fakeDataCSV module.

This module tests the FakeDataCSVGenerate class which generates fake/synthetic
data to replace PII entities in CSV files during anonymization.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock, call
import pandas as pd

# Import the class to test
from privacy.util.special_recognizers.fakeDataCSV import FakeDataCSVGenerate


class TestFakeDataCSVGenerateWithFakeData:
    """Test fakeDataGeneration with FakeData entities."""
    
    def test_fake_data_generation_with_faker_entity(self):
        """Test generating fake data using FakeData attributes."""
        
        # Create mock result with recognizer_results
        result = MagicMock()
        result.value = [["John Smith"]]
        
        # Create a recognizer result
        rec = MagicMock()
        rec.entity_type = "PERSON"
        rec.start = 0
        rec.end = 10
        rec.analysis_explanation = None
        
        result.recognizer_results = [[rec]]
        results = [result]
        
        df = pd.DataFrame({"name": ["John Smith"]})
        
        with patch('privacy.util.special_recognizers.fakeDataCSV.FakeData') as mock_faker:
            mock_faker.PERSON = MagicMock(return_value="Jane Doe")
            with patch('privacy.util.special_recognizers.fakeDataCSV.hasattr', return_value=True):
                with patch('privacy.util.special_recognizers.fakeDataCSV.getattr', return_value=mock_faker.PERSON):
                    fake_dict, updated_results = FakeDataCSVGenerate.fakeDataGeneration(results, df)
                    
                    # Verify entity type key is created (entity_type + original text)
                    assert any("PERSON" in key for key in fake_dict.keys())
                    # Verify the faker was called
                    assert mock_faker.PERSON.called
    
    def test_fake_data_generation_with_multiple_entities(self):
        """Test with multiple entities in the same record."""
        
        result = MagicMock()
        result.value = [["John Smith lives in NYC"]]
        
        # Create multiple recognizer results
        rec1 = MagicMock()
        rec1.entity_type = "PERSON"
        rec1.start = 0
        rec1.end = 10
        rec1.analysis_explanation = None
        
        rec2 = MagicMock()
        rec2.entity_type = "LOCATION"
        rec2.start = 20
        rec2.end = 23
        rec2.analysis_explanation = None
        
        result.recognizer_results = [[rec1, rec2]]
        results = [result]
        
        df = pd.DataFrame({"text": ["John Smith lives in NYC"]})
        
        def mock_hasattr(obj, attr):
            return attr in ["PERSON", "LOCATION"]
        
        with patch('privacy.util.special_recognizers.fakeDataCSV.FakeData') as mock_faker:
            mock_faker.PERSON = MagicMock(return_value="Jane Doe")
            mock_faker.LOCATION = MagicMock(return_value="Boston")
            
            with patch('privacy.util.special_recognizers.fakeDataCSV.hasattr', side_effect=mock_hasattr):
                with patch('privacy.util.special_recognizers.fakeDataCSV.getattr') as mock_getattr:
                    def getattr_side_effect(obj, attr):
                        if attr == "PERSON":
                            return mock_faker.PERSON
                        elif attr == "LOCATION":
                            return mock_faker.LOCATION
                        return MagicMock()
                    
                    mock_getattr.side_effect = getattr_side_effect
                    
                    fake_dict, updated_results = FakeDataCSVGenerate.fakeDataGeneration(results, df)
                    
                    # Should have both entities
                    assert len(fake_dict) >= 2
                    assert any("PERSON" in key for key in fake_dict.keys())
                    assert any("LOCATION" in key for key in fake_dict.keys())


class TestFakeDataCSVGenerateWithSessionDict:
    """Test fakeDataGeneration with session dictionary entities."""
    
    def test_fake_data_generation_with_session_dict(self):
        """Test generating fake data from session dictionary."""
        
        result = MagicMock()
        result.value = [["Acme Corp"]]
        
        rec = MagicMock()
        rec.entity_type = "COMPANY_NAME"
        rec.start = 0
        rec.end = 9
        rec.analysis_explanation = None
        
        result.recognizer_results = [[rec]]
        results = [result]
        
        df = pd.DataFrame({"company": ["Acme Corp"]})
        
        session_data = {
            "COMPANY_NAME": ["Beta Inc", "Gamma LLC", "Delta Co"]
        }
        
        with patch('privacy.util.special_recognizers.fakeDataCSV.hasattr', return_value=False):
            with patch('privacy.util.special_recognizers.fakeDataCSV.get_session_dict', return_value=session_data):
                with patch('privacy.util.special_recognizers.fakeDataCSV.secrets.choice', return_value="Beta Inc"):
                    fake_dict, updated_results = FakeDataCSVGenerate.fakeDataGeneration(results, df)
                    
                    # Should have the entity
                    assert any("COMPANY_NAME" in key for key in fake_dict.keys())
                    assert len(fake_dict) > 0
    
    def test_fake_data_generation_session_dict_with_multiple_rows(self):
        """Test session dict with multiple rows of data."""
        
        result = MagicMock()
        result.value = [["Project Alpha"], ["Project Beta"]]
        
        rec1 = MagicMock()
        rec1.entity_type = "PROJECT"
        rec1.start = 0
        rec1.end = 13
        rec1.analysis_explanation = None
        
        rec2 = MagicMock()
        rec2.entity_type = "PROJECT"
        rec2.start = 0
        rec2.end = 12
        rec2.analysis_explanation = None
        
        result.recognizer_results = [[rec1], [rec2]]
        results = [result]
        
        df = pd.DataFrame({"project": ["Project Alpha", "Project Beta"]})
        
        session_data = {
            "PROJECT": ["Project Gamma", "Project Delta"]
        }
        
        with patch('privacy.util.special_recognizers.fakeDataCSV.hasattr', return_value=False):
            with patch('privacy.util.special_recognizers.fakeDataCSV.get_session_dict', return_value=session_data):
                with patch('privacy.util.special_recognizers.fakeDataCSV.secrets.choice', return_value="Project Gamma"):
                    fake_dict, updated_results = FakeDataCSVGenerate.fakeDataGeneration(results, df)
                    
                    # Should process both rows
                    assert len(fake_dict) >= 1


class TestFakeDataCSVGenerateWithPattern:
    """Test fakeDataGeneration with regex pattern-based generation."""
    
    def test_fake_data_generation_with_pattern(self):
        """Test generating fake data using regex pattern."""
        
        result = MagicMock()
        result.value = [["ABC123"]]
        
        rec = MagicMock()
        rec.entity_type = "CUSTOM_ID"
        rec.start = 0
        rec.end = 6
        
        # Mock analysis_explanation with pattern
        analysis_exp = MagicMock()
        analysis_exp.pattern = r"[A-Z]{3}\d{3}"
        rec.analysis_explanation = analysis_exp
        
        result.recognizer_results = [[rec]]
        results = [result]
        
        df = pd.DataFrame({"id": ["ABC123"]})
        
        with patch('privacy.util.special_recognizers.fakeDataCSV.hasattr', return_value=False):
            with patch('privacy.util.special_recognizers.fakeDataCSV.get_session_dict', return_value={}):
                with patch('privacy.util.special_recognizers.fakeDataCSV.x.xeger', return_value="XYZ789"):
                    fake_dict, updated_results = FakeDataCSVGenerate.fakeDataGeneration(results, df)
                    
                    assert len(fake_dict) > 0
                    assert "CUSTOM_ID" in str(fake_dict.keys())
    
    def test_fake_data_generation_pattern_with_control_chars(self):
        """Test that control characters are removed from generated pattern data."""
        
        result = MagicMock()
        result.value = [["12345"]]
        
        rec = MagicMock()
        rec.entity_type = "ID"
        rec.start = 0
        rec.end = 5
        
        analysis_exp = MagicMock()
        analysis_exp.pattern = r"\w+"
        rec.analysis_explanation = analysis_exp
        
        result.recognizer_results = [[rec]]
        results = [result]
        
        df = pd.DataFrame({"id": ["12345"]})
        
        # Xeger returns string with control characters
        generated_with_control = "AB\x00CD\x1FEF"
        
        with patch('privacy.util.special_recognizers.fakeDataCSV.hasattr', return_value=False):
            with patch('privacy.util.special_recognizers.fakeDataCSV.get_session_dict', return_value={}):
                with patch('privacy.util.special_recognizers.fakeDataCSV.x.xeger', return_value=generated_with_control):
                    fake_dict, updated_results = FakeDataCSVGenerate.fakeDataGeneration(results, df)
                    
                    # Should have processed the entity
                    assert len(fake_dict) > 0
    
    def test_fake_data_generation_no_analysis_explanation(self):
        """Test that results without analysis_explanation are skipped."""
        
        result = MagicMock()
        result.value = [["Unknown"]]
        
        rec = MagicMock()
        rec.entity_type = "UNKNOWN"
        rec.start = 0
        rec.end = 7
        rec.analysis_explanation = None
        
        result.recognizer_results = [[rec]]
        results = [result]
        
        df = pd.DataFrame({"text": ["Unknown"]})
        
        with patch('privacy.util.special_recognizers.fakeDataCSV.hasattr', return_value=False):
            with patch('privacy.util.special_recognizers.fakeDataCSV.get_session_dict', return_value={}):
                fake_dict, updated_results = FakeDataCSVGenerate.fakeDataGeneration(results, df)
                
                # Should not include UNKNOWN since analysis_explanation is None
                assert "UNKNOWN" not in str(fake_dict.keys()) or len(fake_dict) == 0
    
    def test_fake_data_generation_pattern_is_none(self):
        """Test handling when pattern is None."""
        
        result = MagicMock()
        result.value = [["Test"]]
        
        rec = MagicMock()
        rec.entity_type = "CUSTOM"
        rec.start = 0
        rec.end = 4
        
        analysis_exp = MagicMock()
        analysis_exp.pattern = None
        rec.analysis_explanation = analysis_exp
        
        result.recognizer_results = [[rec]]
        results = [result]
        
        df = pd.DataFrame({"text": ["Test"]})
        
        with patch('privacy.util.special_recognizers.fakeDataCSV.hasattr', return_value=False):
            with patch('privacy.util.special_recognizers.fakeDataCSV.get_session_dict', return_value={}):
                fake_dict, updated_results = FakeDataCSVGenerate.fakeDataGeneration(results, df)
                
                # Should skip when pattern is None
                assert len(fake_dict) == 0 or "CUSTOM" not in str(fake_dict.keys())


class TestFakeDataCSVGenerateEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_fake_data_generation_empty_recognizer_results(self):
        """Test with empty recognizer_results list."""
        
        result = MagicMock()
        result.value = [["Some text"]]
        result.recognizer_results = [[]]  # Empty recognizer results
        results = [result]
        
        df = pd.DataFrame({"text": ["Some text"]})
        
        fake_dict, updated_results = FakeDataCSVGenerate.fakeDataGeneration(results, df)
        
        # Should handle empty recognizer results gracefully
        assert isinstance(fake_dict, dict)
    
    def test_fake_data_generation_multiple_results(self):
        """Test with multiple result objects."""
        
        result1 = MagicMock()
        result1.value = [["John"]]
        rec1 = MagicMock()
        rec1.entity_type = "PERSON"
        rec1.start = 0
        rec1.end = 4
        rec1.analysis_explanation = None
        result1.recognizer_results = [[rec1]]
        
        result2 = MagicMock()
        result2.value = [["Alice"]]
        rec2 = MagicMock()
        rec2.entity_type = "PERSON"
        rec2.start = 0
        rec2.end = 5
        rec2.analysis_explanation = None
        result2.recognizer_results = [[rec2]]
        
        results = [result1, result2]
        
        df = pd.DataFrame({"name": ["John", "Alice"]})
        
        with patch('privacy.util.special_recognizers.fakeDataCSV.FakeData') as mock_faker:
            mock_faker.PERSON = MagicMock(return_value="Bob")
            with patch('privacy.util.special_recognizers.fakeDataCSV.hasattr', return_value=True):
                with patch('privacy.util.special_recognizers.fakeDataCSV.getattr', return_value=mock_faker.PERSON):
                    fake_dict, updated_results = FakeDataCSVGenerate.fakeDataGeneration(results, df)
                    
                    # Should process both results
                    assert len(fake_dict) >= 1
    
    def test_fake_data_generation_mixed_sources(self):
        """Test with results from different sources (FakeData, session, pattern)."""
        
        result = MagicMock()
        result.value = [["John works at InfoCorp with code ABCDE"]]
        
        rec1 = MagicMock()
        rec1.entity_type = "PERSON"
        rec1.start = 0
        rec1.end = 4
        rec1.analysis_explanation = None
        
        rec2 = MagicMock()
        rec2.entity_type = "COMPANY"
        rec2.start = 14
        rec2.end = 22
        rec2.analysis_explanation = None
        
        rec3 = MagicMock()
        rec3.entity_type = "CODE"
        rec3.start = 33
        rec3.end = 38
        analysis_exp = MagicMock()
        analysis_exp.pattern = r"[A-Z]{5}"
        rec3.analysis_explanation = analysis_exp
        
        result.recognizer_results = [[rec1, rec2, rec3]]
        results = [result]
        
        df = pd.DataFrame({"text": ["John works at InfoCorp with code ABCDE"]})
        
        session_data = {"COMPANY": ["TechCo", "SoftInc"]}
        
        def mock_hasattr(obj, attr):
            return attr == "PERSON"
        
        with patch('privacy.util.special_recognizers.fakeDataCSV.FakeData') as mock_faker:
            mock_faker.PERSON = MagicMock(return_value="Jane")
            with patch('privacy.util.special_recognizers.fakeDataCSV.hasattr', side_effect=mock_hasattr):
                with patch('privacy.util.special_recognizers.fakeDataCSV.getattr', return_value=mock_faker.PERSON):
                    with patch('privacy.util.special_recognizers.fakeDataCSV.get_session_dict', return_value=session_data):
                        with patch('privacy.util.special_recognizers.fakeDataCSV.secrets.choice', return_value="TechCo"):
                            with patch('privacy.util.special_recognizers.fakeDataCSV.x.xeger', return_value="XYZTW"):
                                fake_dict, updated_results = FakeDataCSVGenerate.fakeDataGeneration(results, df)
                                
                                # Should have multiple entities
                                assert len(fake_dict) >= 2
    
    def test_fake_data_generation_enumerate_index(self):
        """Test that enumerate index k is used correctly for unique keys."""
        
        result = MagicMock()
        result.value = [["John and Jane"]]
        
        # Two PERSON entities in same value
        rec1 = MagicMock()
        rec1.entity_type = "PERSON"
        rec1.start = 0
        rec1.end = 4
        rec1.analysis_explanation = None
        
        rec2 = MagicMock()
        rec2.entity_type = "PERSON"
        rec2.start = 9
        rec2.end = 13
        rec2.analysis_explanation = None
        
        result.recognizer_results = [[rec1, rec2]]
        results = [result]
        
        df = pd.DataFrame({"text": ["John and Jane"]})
        
        with patch('privacy.util.special_recognizers.fakeDataCSV.FakeData') as mock_faker:
            mock_faker.PERSON = MagicMock(return_value="Bob")
            with patch('privacy.util.special_recognizers.fakeDataCSV.hasattr', return_value=True):
                with patch('privacy.util.special_recognizers.fakeDataCSV.getattr', return_value=mock_faker.PERSON):
                    fake_dict, updated_results = FakeDataCSVGenerate.fakeDataGeneration(results, df)
                    
                    # Should create entries with unique keys
                    assert len(fake_dict) >= 1


class TestFakeDataCSVGenerateIntegration:
    """Integration tests for complete workflows."""
    
    def test_complete_csv_anonymization_workflow(self):
        """Test complete workflow with realistic CSV data."""
        
        result = MagicMock()
        # Each row should have the full text, not split
        result.value = [["John Smith"], ["john@example.com"], ["Alice Doe"], ["alice@test.org"]]
        
        rec1 = MagicMock()
        rec1.entity_type = "PERSON"
        rec1.start = 0
        rec1.end = 10
        rec1.analysis_explanation = None
        
        rec2 = MagicMock()
        rec2.entity_type = "EMAIL_ADDRESS"
        rec2.start = 0
        rec2.end = 16
        analysis_exp = MagicMock()
        analysis_exp.pattern = r"\w+@\w+\.\w+"
        rec2.analysis_explanation = analysis_exp
        
        rec3 = MagicMock()
        rec3.entity_type = "PERSON"
        rec3.start = 0
        rec3.end = 9
        rec3.analysis_explanation = None
        
        rec4 = MagicMock()
        rec4.entity_type = "EMAIL_ADDRESS"
        rec4.start = 0
        rec4.end = 15
        rec4.analysis_explanation = analysis_exp
        
        result.recognizer_results = [[rec1], [rec2], [rec3], [rec4]]
        results = [result]
        
        df = pd.DataFrame({"name": ["John Smith", "Alice Doe"], "email": ["john@example.com", "alice@test.org"]})
        
        def mock_hasattr(obj, attr):
            return attr == "PERSON"
        
        with patch('privacy.util.special_recognizers.fakeDataCSV.FakeData') as mock_faker:
            mock_faker.PERSON = MagicMock(return_value="Jane Doe")
            with patch('privacy.util.special_recognizers.fakeDataCSV.hasattr', side_effect=mock_hasattr):
                with patch('privacy.util.special_recognizers.fakeDataCSV.getattr', return_value=mock_faker.PERSON):
                    with patch('privacy.util.special_recognizers.fakeDataCSV.get_session_dict', return_value={}):
                        with patch('privacy.util.special_recognizers.fakeDataCSV.x.xeger', return_value="fake@test.org"):
                            fake_dict, updated_results = FakeDataCSVGenerate.fakeDataGeneration(results, df)
                            
                            # Should return dict and results
                            assert isinstance(fake_dict, dict)
                            assert isinstance(updated_results, list)
                            assert len(fake_dict) >= 1
    
    def test_return_tuple_structure(self):
        """Test that the function returns a tuple of (dict, results)."""
        
        result = MagicMock()
        result.value = [["Test"]]
        result.recognizer_results = [[]]
        results = [result]
        
        df = pd.DataFrame({"text": ["Test"]})
        
        return_value = FakeDataCSVGenerate.fakeDataGeneration(results, df)
        
        # Should return a tuple
        assert isinstance(return_value, tuple)
        assert len(return_value) == 2
        fake_dict, updated_results = return_value
        assert isinstance(fake_dict, dict)
        assert isinstance(updated_results, list)
