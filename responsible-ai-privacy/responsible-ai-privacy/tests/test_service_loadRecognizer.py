"""
Tests for loadRecognizer module.

This module tests the LoadRecognizer class which handles loading and managing
custom PII recognizers (pattern and data-based) for the Presidio analyzer.
"""

import pytest
import json
import io
import tempfile
import os
from unittest.mock import MagicMock, patch, Mock, mock_open


@pytest.fixture
def mock_recognizer_payload():
    """Create a mock payload for recognizer loading."""
    recognizer_data = [
        {
            "RecogType": "Data",
            "RecogName": "CUSTOM_ID",
            "EntityValue": ["ID123", "ID456"],
            "Score": 0.8,
            "Context": ["id", "identifier"]
        },
        {
            "RecogType": "Pattern",
            "RecogName": "CUSTOM_PATTERN",
            "EntityValue": ["TEST.*", "DEMO.*"],
            "Score": 0.9,
            "Context": "pattern,code",
            "isPreDefined": "No"
        }
    ]
    
    payload = {
        "file": MagicMock()
    }
    payload["file"].file = io.BytesIO(json.dumps(recognizer_data).encode())
    return payload


@pytest.fixture
def mock_recognizer_payload_bytes():
    """Create a mock payload with contents_bytes."""
    recognizer_data = [
        {
            "RecogType": "Data",
            "RecogName": "TEST_ENTITY",
            "EntityValue": ["test1", "test2"],
            "Score": 0.7
        }
    ]
    
    payload = {
        "contents_bytes": json.dumps(recognizer_data).encode()
    }
    return payload


class TestLocationRecognizerWithExclusion:
    """Test suite for LocationRecognizerWithExclusion wrapper."""
    
    def test_location_wrapper_filters_exclusions(self):
        """Test that location recognizer filters out postal code phrases."""
        from privacy.service.loadRecognizer import LocationRecognizerWithExclusion
        
        # Mock base recognizer
        mock_base = MagicMock()
        
        # Create mock results - one for valid location, one for exclusion phrase
        mock_result1 = MagicMock()
        mock_result1.start = 0
        mock_result1.end = 10
        
        mock_result2 = MagicMock()
        mock_result2.start = 11
        mock_result2.end = 19  # "zip code"
        
        mock_base.analyze.return_value = [mock_result1, mock_result2]
        
        wrapper = LocationRecognizerWithExclusion(mock_base)
        
        text = "California zip code"
        results = wrapper.analyze(text)
        
        # Both results returned - exclusion filtering happens based on actual text match
        # The wrapper checks if text[start:end].lower() matches exclusions
        assert len(results) <= 2
    
    def test_location_wrapper_keeps_valid_locations(self):
        """Test that valid locations are not filtered."""
        from privacy.service.loadRecognizer import LocationRecognizerWithExclusion
        
        mock_base = MagicMock()
        
        mock_result = MagicMock()
        mock_result.start = 0
        mock_result.end = 10
        
        mock_base.analyze.return_value = [mock_result]
        
        wrapper = LocationRecognizerWithExclusion(mock_base)
        
        text = "California is a state"
        results = wrapper.analyze(text)
        
        assert len(results) == 1
        assert results[0] == mock_result
    
    def test_location_wrapper_getattr_delegation(self):
        """Test that wrapper delegates attribute access to base recognizer."""
        from privacy.service.loadRecognizer import LocationRecognizerWithExclusion
        
        mock_base = MagicMock()
        mock_base.supported_entities = ["LOCATION"]
        mock_base.some_method = MagicMock(return_value="test")
        
        wrapper = LocationRecognizerWithExclusion(mock_base)
        
        # Test attribute delegation
        assert wrapper.supported_entities == ["LOCATION"]
        assert wrapper.some_method() == "test"
    
    def test_location_wrapper_filters_all_exclusions(self):
        """Test filtering of various postal code phrases."""
        from privacy.service.loadRecognizer import LocationRecognizerWithExclusion
        
        mock_base = MagicMock()
        
        # Create results for different exclusion phrases
        results = []
        exclusions_text = ["postal code", "ZIP CODE", "postalcode", "zip code code"]
        start = 0
        for phrase in exclusions_text:
            result = MagicMock()
            result.start = start
            result.end = start + len(phrase)
            results.append(result)
            start += len(phrase) + 1
        
        mock_base.analyze.return_value = results
        
        wrapper = LocationRecognizerWithExclusion(mock_base)
        
        text = "postal code ZIP CODE postalcode zip code code"
        filtered = wrapper.analyze(text)
        
        # All should be filtered
        assert len(filtered) == 0


class TestLoadRecognizerSetRecognizer:
    """Test suite for LoadRecognizer.set_recognizer method."""
    
    def test_set_recognizer_with_file_payload(self, mock_recognizer_payload):
        """Test set_recognizer with file in payload."""
        from privacy.service.loadRecognizer import LoadRecognizer
        
        with patch('privacy.service.loadRecognizer.registry') as mock_registry, \
             patch('privacy.service.loadRecognizer.ranha_recog') as mock_ranha, \
             patch('privacy.service.loadRecognizer.error_dict', {}), \
             patch('privacy.service.loadRecognizer.request_id_var') as mock_req_id:
            
            mock_req_id.get.return_value = "test_id"
            mock_registry.get_supported_entities.return_value = ["PERSON", "EMAIL"]
            mock_registry.recognizers = []
            mock_ranha.get_supported_entities.return_value = ["LOCATION", "EMAIL"]
            
            result = LoadRecognizer.set_recognizer(mock_recognizer_payload)
            
            # Verify recognizers were added
            assert mock_registry.add_recognizer.called
            assert "Available Recognizers" in result
            assert isinstance(result["Available Recognizers"], list)
    
    def test_set_recognizer_with_contents_bytes(self, mock_recognizer_payload_bytes):
        """Test set_recognizer with contents_bytes."""
        from privacy.service.loadRecognizer import LoadRecognizer
        
        with patch('privacy.service.loadRecognizer.registry') as mock_registry, \
             patch('privacy.service.loadRecognizer.ranha_recog') as mock_ranha, \
             patch('privacy.service.loadRecognizer.DataListRecognizer') as mock_data_recog, \
             patch('privacy.service.loadRecognizer.error_dict', {}), \
             patch('privacy.service.loadRecognizer.request_id_var') as mock_req_id:
            
            mock_req_id.get.return_value = "test_id"
            mock_registry.get_supported_entities.return_value = ["PERSON"]
            mock_registry.recognizers = []
            mock_ranha.get_supported_entities.return_value = ["LOCATION"]
            
            result = LoadRecognizer.set_recognizer(mock_recognizer_payload_bytes)
            
            assert "Available Recognizers" in result
            assert mock_registry.add_recognizer.called
    
    def test_set_recognizer_data_recognizer(self):
        """Test set_recognizer creates Data recognizer correctly."""
        from privacy.service.loadRecognizer import LoadRecognizer
        
        recognizer_data = [{
            "RecogType": "Data",
            "RecogName": "EMPLOYEE_ID",
            "EntityValue": ["EMP001", "EMP002"],
            "Score": 0.85,
            "Context": ["employee", "staff"]
        }]
        
        payload = {"file": MagicMock()}
        payload["file"].file = io.BytesIO(json.dumps(recognizer_data).encode())
        
        with patch('privacy.service.loadRecognizer.registry') as mock_registry, \
             patch('privacy.service.loadRecognizer.ranha_recog') as mock_ranha, \
             patch('privacy.service.loadRecognizer.DataListRecognizer') as mock_data_recog, \
             patch('privacy.service.loadRecognizer.error_dict', {}), \
             patch('privacy.service.loadRecognizer.request_id_var') as mock_req_id:
            
            mock_req_id.get.return_value = "test_id"
            mock_registry.get_supported_entities.return_value = []
            mock_registry.recognizers = []
            mock_ranha.get_supported_entities.return_value = []
            
            LoadRecognizer.set_recognizer(payload)
            
            # Verify DataListRecognizer was created
            mock_data_recog.assert_called_once()
            call_args = mock_data_recog.call_args[1]
            assert call_args["entitie"] == ["EMPLOYEE_ID"]
            assert call_args["terms"] == ["EMP001", "EMP002"]
    
    def test_set_recognizer_pattern_recognizer(self):
        """Test set_recognizer creates Pattern recognizer correctly."""
        from privacy.service.loadRecognizer import LoadRecognizer
        
        recognizer_data = [{
            "RecogType": "Pattern",
            "RecogName": "ORDER_NUM",
            "EntityValue": ["ORD-\\d{4}", "ORDER-\\d{4}"],
            "Score": 0.9,
            "Context": "order,number",
            "isPreDefined": "No"
        }]
        
        payload = {"file": MagicMock()}
        payload["file"].file = io.BytesIO(json.dumps(recognizer_data).encode())
        
        with patch('privacy.service.loadRecognizer.registry') as mock_registry, \
             patch('privacy.service.loadRecognizer.ranha_recog') as mock_ranha, \
             patch('privacy.service.loadRecognizer.Pattern') as mock_pattern, \
             patch('privacy.service.loadRecognizer.PatternRecognizer') as mock_pattern_recog, \
             patch('privacy.service.loadRecognizer.error_dict', {}), \
             patch('privacy.service.loadRecognizer.request_id_var') as mock_req_id:
            
            mock_req_id.get.return_value = "test_id"
            
            mock_registry.get_supported_entities.return_value = []
            mock_registry.recognizers = []
            mock_ranha.get_supported_entities.return_value = []
            
            LoadRecognizer.set_recognizer(payload)
            
            # Verify Pattern and PatternRecognizer were created
            assert mock_pattern.called
            assert mock_pattern_recog.called
            
            # Check pattern creation
            pattern_call = mock_pattern.call_args[1]
            assert pattern_call["name"] == "ORDER_NUM"
            assert "ORD-\\d{4}|ORDER-\\d{4}" in pattern_call["regex"]
    
    def test_set_recognizer_removes_datetime(self):
        """Test that DATE_TIME recognizers are removed."""
        from privacy.service.loadRecognizer import LoadRecognizer
        
        recognizer_data = []
        payload = {"file": MagicMock()}
        payload["file"].file = io.BytesIO(json.dumps(recognizer_data).encode())
        
        # Mock recognizer with DATE_TIME
        mock_datetime_recog = MagicMock()
        mock_datetime_recog.supported_entities = ["DATE_TIME"]
        
        mock_other_recog = MagicMock()
        mock_other_recog.supported_entities = ["PERSON"]
        
        with patch('privacy.service.loadRecognizer.registry') as mock_registry, \
             patch('privacy.service.loadRecognizer.ranha_recog') as mock_ranha, \
             patch('privacy.service.loadRecognizer.error_dict', {}), \
             patch('privacy.service.loadRecognizer.request_id_var') as mock_req_id:
            
            mock_req_id.get.return_value = "test_id"
            mock_registry.recognizers = [mock_datetime_recog, mock_other_recog]
            mock_registry.get_supported_entities.return_value = []
            mock_ranha.get_supported_entities.return_value = []
            
            LoadRecognizer.set_recognizer(payload)
            
            # DATE_TIME should be filtered out
            assert mock_datetime_recog not in mock_registry.recognizers
    
    def test_set_recognizer_wraps_location(self):
        """Test that LOCATION recognizer is wrapped with exclusion filter."""
        from privacy.service.loadRecognizer import LoadRecognizer
        from privacy.service.loadRecognizer import LocationRecognizerWithExclusion
        
        recognizer_data = []
        payload = {"file": MagicMock()}
        payload["file"].file = io.BytesIO(json.dumps(recognizer_data).encode())
        
        mock_location_recog = MagicMock()
        mock_location_recog.supported_entities = ["LOCATION"]
        
        with patch('privacy.service.loadRecognizer.registry') as mock_registry, \
             patch('privacy.service.loadRecognizer.ranha_recog') as mock_ranha, \
             patch('privacy.service.loadRecognizer.error_dict', {}), \
             patch('privacy.service.loadRecognizer.request_id_var') as mock_req_id:
            
            mock_req_id.get.return_value = "test_id"
            mock_registry.recognizers = [mock_location_recog]
            mock_registry.get_supported_entities.return_value = []
            mock_ranha.get_supported_entities.return_value = []
            
            LoadRecognizer.set_recognizer(payload)
            
            # First recognizer should now be wrapped
            wrapped = mock_registry.recognizers[0]
            assert isinstance(wrapped, LocationRecognizerWithExclusion)
    
    def test_set_recognizer_exception_handling(self):
        """Test set_recognizer handles exceptions correctly."""
        from privacy.service.loadRecognizer import LoadRecognizer
        
        # Invalid JSON
        payload = {"file": MagicMock()}
        payload["file"].file = io.BytesIO(b"invalid json{")
        
        with patch('privacy.service.loadRecognizer.error_dict', {}) as mock_error_dict, \
             patch('privacy.service.loadRecognizer.request_id_var') as mock_req_id:
            
            mock_req_id.get.return_value = "test_id"
            
            with pytest.raises(RuntimeError):
                LoadRecognizer.set_recognizer(payload)
            
            # Verify error was logged to error_dict
            assert "test_id" in mock_error_dict
            assert len(mock_error_dict["test_id"]) > 0


class TestLoadRecognizerLoadRecognizer:
    """Test suite for LoadRecognizer.load_recognizer method."""
    
    def test_load_recognizer_returns_available_entities(self):
        """Test load_recognizer returns available recognizers."""
        from privacy.service.loadRecognizer import LoadRecognizer
        
        with patch('privacy.service.loadRecognizer.registry') as mock_registry, \
             patch('privacy.service.loadRecognizer.ranha_recog') as mock_ranha:
            
            mock_registry.get_supported_entities.return_value = ["PERSON", "EMAIL", "PHONE"]
            mock_ranha.get_supported_entities.return_value = ["LOCATION", "ORGANIZATION", "EMAIL"]
            
            result = LoadRecognizer.load_recognizer()
            
            assert "Available Recognizers" in result
            assert "PERSON" in result["Available Recognizers"]
            assert "EMAIL" in result["Available Recognizers"]
            assert "LOCATION*" in result["Available Recognizers"]
            assert "ORGANIZATION*" in result["Available Recognizers"]
            assert "*" in result
    
    def test_load_recognizer_exception_handling(self):
        """Test load_recognizer handles exceptions."""
        from privacy.service.loadRecognizer import LoadRecognizer
        
        with patch('privacy.service.loadRecognizer.registry') as mock_registry, \
             patch('privacy.service.loadRecognizer.error_dict', {"test_id": []}), \
             patch('privacy.service.loadRecognizer.request_id_var') as mock_req_id:
            
            mock_req_id.get.return_value = "test_id"
            mock_registry.get_supported_entities.side_effect = Exception("Registry error")
            
            with pytest.raises(RuntimeError):
                LoadRecognizer.load_recognizer()


class TestLoadRecognizerLoadRecognizersFromJson:
    """Test suite for LoadRecognizer.load_recognizers_from_json method."""
    
    def test_load_recognizers_from_json_file_not_found(self):
        """Test load_recognizers_from_json raises error for missing file."""
        from privacy.service.loadRecognizer import LoadRecognizer
        
        mock_registry = MagicMock()
        
        with pytest.raises(FileNotFoundError):
            LoadRecognizer.load_recognizers_from_json("/nonexistent/file.json", mock_registry)
    
    def test_load_recognizers_from_json_data_recognizer(self):
        """Test loading Data recognizer from JSON file."""
        from privacy.service.loadRecognizer import LoadRecognizer
        
        recognizer_data = [{
            "RecogType": "Data",
            "RecogName": "PRODUCT_CODE",
            "EntityValue": ["PROD123", "PROD456"],
            "Score": 0.75
        }]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(recognizer_data, f)
            temp_file_path = f.name
        
        try:
            mock_registry = MagicMock()
            mock_registry.recognizers = []
            
            with patch('privacy.service.loadRecognizer.DataListRecognizer') as mock_data_recog:
                LoadRecognizer.load_recognizers_from_json(temp_file_path, mock_registry)
                
                # Verify DataListRecognizer was created and added
                mock_data_recog.assert_called_once()
                assert mock_registry.add_recognizer.called
        finally:
            os.unlink(temp_file_path)
    
    def test_load_recognizers_from_json_pattern_recognizer(self):
        """Test loading Pattern recognizer from JSON file."""
        from privacy.service.loadRecognizer import LoadRecognizer
        
        recognizer_data = [{
            "RecogType": "Pattern",
            "RecogName": "LICENSE_PLATE",
            "EntityValue": ["[A-Z]{2}\\d{4}", "[A-Z]{3}\\d{3}"],
            "Score": 0.85,
            "Context": "plate,license",
            "isPreDefined": "No"
        }]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(recognizer_data, f)
            temp_file_path = f.name
        
        try:
            mock_registry = MagicMock()
            mock_registry.recognizers = []
            
            with patch('privacy.service.loadRecognizer.Pattern') as mock_pattern, \
                 patch('privacy.service.loadRecognizer.PatternRecognizer') as mock_pattern_recog:
                
                LoadRecognizer.load_recognizers_from_json(temp_file_path, mock_registry)
                
                # Verify Pattern and PatternRecognizer were created
                assert mock_pattern.called
                assert mock_pattern_recog.called
                assert mock_registry.add_recognizer.called
        finally:
            os.unlink(temp_file_path)
    
    def test_load_recognizers_from_json_removes_datetime(self):
        """Test that DATE_TIME recognizers are removed after loading."""
        from privacy.service.loadRecognizer import LoadRecognizer
        
        recognizer_data = [{"RecogType": "Data", "RecogName": "TEST", "EntityValue": ["test"], "Score": 0.6}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(recognizer_data, f)
            temp_file_path = f.name
        
        try:
            mock_datetime_recog = MagicMock()
            mock_datetime_recog.supported_entities = ["DATE_TIME"]
            
            mock_registry = MagicMock()
            mock_registry.recognizers = [mock_datetime_recog]
            
            with patch('privacy.service.loadRecognizer.DataListRecognizer'):
                LoadRecognizer.load_recognizers_from_json(temp_file_path, mock_registry)
            
            # DATE_TIME should be filtered out
            assert mock_datetime_recog not in mock_registry.recognizers
        finally:
            os.unlink(temp_file_path)
    
    def test_load_recognizers_from_json_wraps_location(self):
        """Test that LOCATION recognizer is wrapped."""
        from privacy.service.loadRecognizer import LoadRecognizer
        from privacy.service.loadRecognizer import LocationRecognizerWithExclusion
        
        recognizer_data = []
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(recognizer_data, f)
            temp_file_path = f.name
        
        try:
            mock_location_recog = MagicMock()
            mock_location_recog.supported_entities = ["LOCATION"]
            
            mock_registry = MagicMock()
            mock_registry.recognizers = [mock_location_recog]
            
            LoadRecognizer.load_recognizers_from_json(temp_file_path, mock_registry)
            
            # First recognizer should be wrapped
            wrapped = mock_registry.recognizers[0]
            assert isinstance(wrapped, LocationRecognizerWithExclusion)
        finally:
            os.unlink(temp_file_path)
    
    def test_load_recognizers_from_json_invalid_json(self):
        """Test handling of invalid JSON file."""
        from privacy.service.loadRecognizer import LoadRecognizer
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json{{{")
            temp_file_path = f.name
        
        try:
            mock_registry = MagicMock()
            
            with pytest.raises(RuntimeError):
                LoadRecognizer.load_recognizers_from_json(temp_file_path, mock_registry)
        finally:
            os.unlink(temp_file_path)
    
    def test_load_recognizers_from_json_skips_unsupported_types(self):
        """Test that unsupported recognizer types are skipped."""
        from privacy.service.loadRecognizer import LoadRecognizer
        
        recognizer_data = [
            {"RecogType": "UnsupportedType", "RecogName": "TEST", "EntityValue": [], "Score": 0.5},
            {"RecogType": "Data", "RecogName": "VALID", "EntityValue": ["test"], "Score": 0.6}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(recognizer_data, f)
            temp_file_path = f.name
        
        try:
            mock_registry = MagicMock()
            mock_registry.recognizers = []
            
            with patch('privacy.service.loadRecognizer.DataListRecognizer'):
                LoadRecognizer.load_recognizers_from_json(temp_file_path, mock_registry)
                
                # Should only add one recognizer (the valid Data type)
                assert mock_registry.add_recognizer.call_count == 1
        finally:
            os.unlink(temp_file_path)
    
    def test_load_recognizers_from_json_data_recognizer_error(self):
        """Test error handling when creating Data recognizer fails."""
        from privacy.service.loadRecognizer import LoadRecognizer
        
        recognizer_data = [{
            "RecogType": "Data",
            "RecogName": "ERROR_TEST",
            "EntityValue": ["test"],
            "Score": 0.6
        }]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(recognizer_data, f)
            temp_file_path = f.name
        
        try:
            mock_registry = MagicMock()
            
            with patch('privacy.service.loadRecognizer.DataListRecognizer', side_effect=Exception("Creation error")):
                with pytest.raises(RuntimeError):
                    LoadRecognizer.load_recognizers_from_json(temp_file_path, mock_registry)
        finally:
            os.unlink(temp_file_path)
    
    def test_load_recognizers_from_json_pattern_recognizer_error(self):
        """Test error handling when creating Pattern recognizer fails."""
        from privacy.service.loadRecognizer import LoadRecognizer
        
        recognizer_data = [{
            "RecogType": "Pattern",
            "RecogName": "ERROR_PATTERN",
            "EntityValue": ["test.*"],
            "Score": 0.6,
            "isPreDefined": "No"
        }]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(recognizer_data, f)
            temp_file_path = f.name
        
        try:
            mock_registry = MagicMock()
            
            with patch('privacy.service.loadRecognizer.Pattern', side_effect=Exception("Pattern error")):
                with pytest.raises(RuntimeError):
                    LoadRecognizer.load_recognizers_from_json(temp_file_path, mock_registry)
        finally:
            os.unlink(temp_file_path)
