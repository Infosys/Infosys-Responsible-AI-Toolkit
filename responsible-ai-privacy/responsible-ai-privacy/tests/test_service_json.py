"""
Tests for json_service module.

This module tests the JSONService class which handles JSON file anonymization
with support for PII detection, batch processing, and portfolio-based rules.
"""

import pytest
import json
import io
from unittest.mock import MagicMock, patch, Mock, mock_open
from privacy.service.api_req import ApiCall


@pytest.fixture
def mock_json_payload():
    """Create a mock payload for JSON anonymization."""
    payload = {
        "file": MagicMock(),
        "keys_to_skip": ["id", "timestamp"],
        "pii_entities_to_be_redacted": "PERSON,EMAIL,PHONE_NUMBER",
        "score_threshold": 0.5,
        "portfolio": None,
        "account": None,
        "nlp": None,
        "exclusion": "exclude1,exclude2"
    }
    payload["file"].file = io.BytesIO(json.dumps({"name": "John Doe", "email": "john@example.com"}).encode())
    return payload


@pytest.fixture
def mock_json_payload_minimal():
    """Create a minimal mock payload."""
    payload = {
        "file": MagicMock(),
        "keys_to_skip": [],
        "pii_entities_to_be_redacted": None,
        "score_threshold": None,
        "portfolio": None,
        "account": None,
        "nlp": None,
        "exclusion": None
    }
    payload["file"].file = io.BytesIO(json.dumps({"data": "test"}).encode())
    return payload


class TestJSONServiceFlattenReconstruct:
    """Test suite for JSON flattening and reconstruction utilities."""
    
    def test_flatten_simple_dict(self):
        """Test flattening a simple dictionary."""
        from privacy.service.json_service import JSONService
        
        input_data = {"name": "John", "age": 30}
        result = JSONService.flatten_json(input_data)
        
        assert result == {"name": "John", "age": 30}
    
    def test_flatten_nested_dict(self):
        """Test flattening a nested dictionary."""
        from privacy.service.json_service import JSONService
        
        input_data = {
            "user": {
                "name": "John",
                "contact": {
                    "email": "john@example.com"
                }
            }
        }
        result = JSONService.flatten_json(input_data)
        
        assert "user_name" in result
        assert result["user_name"] == "John"
        assert "user_contact_email" in result
        assert result["user_contact_email"] == "john@example.com"
    
    def test_flatten_with_list(self):
        """Test flattening a dictionary with lists."""
        from privacy.service.json_service import JSONService
        
        input_data = {
            "items": ["apple", "banana", "cherry"]
        }
        result = JSONService.flatten_json(input_data)
        
        assert "items_0" in result
        assert result["items_0"] == "apple"
        assert "items_1" in result
        assert result["items_1"] == "banana"
        assert "items_2" in result
        assert result["items_2"] == "cherry"
    
    def test_flatten_complex_nested_structure(self):
        """Test flattening a complex nested structure."""
        from privacy.service.json_service import JSONService
        
        input_data = {
            "company": {
                "employees": [
                    {"name": "John", "age": 30},
                    {"name": "Jane", "age": 25}
                ]
            }
        }
        result = JSONService.flatten_json(input_data)
        
        assert "company_employees_0_name" in result
        assert result["company_employees_0_name"] == "John"
        assert "company_employees_1_name" in result
        assert result["company_employees_1_name"] == "Jane"
    
    def test_flatten_empty_dict(self):
        """Test flattening an empty dictionary."""
        from privacy.service.json_service import JSONService
        
        result = JSONService.flatten_json({})
        
        assert result == {}
    
    def test_reconstruct_simple_json(self):
        """Test reconstructing a simple flattened JSON."""
        from privacy.service.json_service import JSONService
        
        flattened = {"name": "John", "age": 30}
        result = JSONService.reconstruct_json(flattened)
        
        assert "name" in result
        assert result["name"] == "John"
        assert "age" in result
        assert result["age"] == 30
    
    def test_reconstruct_nested_json(self):
        """Test reconstructing nested flattened JSON."""
        from privacy.service.json_service import JSONService
        
        flattened = {
            "user_name": "John",
            "user_email": "john@example.com"
        }
        result = JSONService.reconstruct_json(flattened)
        
        assert "user" in result
        assert isinstance(result["user"], dict)
        assert result["user"]["name"] == "John"
        assert result["user"]["email"] == "john@example.com"
    
    def test_reconstruct_with_list_input(self):
        """Test reconstruct_json handles list input."""
        from privacy.service.json_service import JSONService
        
        input_list = [{"a": 1}, {"b": 2}]
        result = JSONService.reconstruct_json(input_list)
        
        assert isinstance(result, list)
        assert len(result) == 2


class TestJSONServiceAnonymize:
    """Test suite for JSONService.anonymize_json method."""
    
    def test_anonymize_json_with_dict_data(self, mock_json_payload):
        """Test anonymize_json with dictionary JSON data."""
        from privacy.service.json_service import JSONService
        
        mock_json_payload["file"].file = io.BytesIO(
            json.dumps({"name": "John Doe", "email": "john@example.com"}).encode()
        )
        
        with patch('privacy.service.json_service.AnalyzerEngine') as mock_analyzer_cls, \
             patch('privacy.service.json_service.BatchAnalyzerEngine') as mock_batch_analyzer_cls, \
             patch('privacy.service.json_service.BatchAnonymizerEngine') as mock_batch_anonymizer_cls, \
             patch('privacy.service.json_service.ApiCall.request', return_value=None), \
             patch('privacy.service.json_service.JSONService.process_dict') as mock_process_dict, \
             patch('tempfile.NamedTemporaryFile', mock_open()):
            
            mock_process_dict.return_value = {"name": "<PERSON>", "email": "<EMAIL>"}
            
            result = JSONService.anonymize_json(mock_json_payload)
            
            # Verify result is JSON string
            assert isinstance(result, str)
            anonymized_data = json.loads(result)
            assert anonymized_data["name"] == "<PERSON>"
            assert anonymized_data["email"] == "<EMAIL>"
            
            # Verify process_dict was called
            mock_process_dict.assert_called_once()
    
    def test_anonymize_json_with_list_data(self, mock_json_payload):
        """Test anonymize_json with list JSON data."""
        from privacy.service.json_service import JSONService
        
        list_data = [
            {"name": "John", "email": "john@example.com"},
            {"name": "Jane", "email": "jane@example.com"}
        ]
        mock_json_payload["file"].file = io.BytesIO(json.dumps(list_data).encode())
        
        with patch('privacy.service.json_service.AnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnonymizerEngine'), \
             patch('privacy.service.json_service.ApiCall.request', return_value=None), \
             patch('privacy.service.json_service.JSONService.process_list') as mock_process_list, \
             patch('tempfile.NamedTemporaryFile', mock_open()):
            
            mock_process_list.return_value = [
                {"name": "<PERSON>", "email": "<EMAIL>"},
                {"name": "<PERSON>", "email": "<EMAIL>"}
            ]
            
            result = JSONService.anonymize_json(mock_json_payload)
            
            # Verify result is JSON string
            assert isinstance(result, str)
            anonymized_data = json.loads(result)
            assert isinstance(anonymized_data, list)
            assert len(anonymized_data) == 2
            
            # Verify process_list was called
            mock_process_list.assert_called_once()
    
    def test_anonymize_json_with_portfolio_and_account(self, mock_json_payload):
        """Test anonymize_json with portfolio and account specified."""
        from privacy.service.json_service import JSONService
        
        mock_json_payload["portfolio"] = "TestPortfolio"
        mock_json_payload["account"] = "TestAccount"
        
        with patch('privacy.service.json_service.AnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnonymizerEngine'), \
             patch('privacy.service.json_service.ApiCall.request') as mock_api_call, \
             patch('privacy.service.json_service.JSONService.process_dict') as mock_process_dict, \
             patch('tempfile.NamedTemporaryFile', mock_open()):
            
            mock_api_call.return_value = None
            
            result = JSONService.anonymize_json(mock_json_payload)
            
            # Verify API call was made with portfolio/account
            assert mock_api_call.called
            call_args = mock_api_call.call_args[0][0]
            assert call_args["portfolio"] == "TestPortfolio"
            assert call_args["account"] == "TestAccount"
    
    def test_anonymize_json_api_returns_none(self, mock_json_payload):
        """Test anonymize_json when API returns None."""
        from privacy.service.json_service import JSONService
        
        mock_json_payload["portfolio"] = "TestPortfolio"
        mock_json_payload["account"] = "TestAccount"
        
        with patch('privacy.service.json_service.ApiCall.request', return_value=None):
            result = JSONService.anonymize_json(mock_json_payload)
            
            assert result is None
    
    def test_anonymize_json_with_nlp_roberta(self, mock_json_payload):
        """Test anonymize_json with roberta NLP model."""
        from privacy.service.json_service import JSONService
        
        mock_json_payload["nlp"] = "roberta"
        
        with patch('privacy.service.json_service.AnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnonymizerEngine'), \
             patch('privacy.service.json_service.ApiCall.request', return_value=None), \
             patch('privacy.service.json_service.roberta_recog', MagicMock()), \
             patch('privacy.service.json_service.JSONService.process_dict') as mock_process_dict, \
             patch('tempfile.NamedTemporaryFile', mock_open()):
            
            mock_process_dict.return_value = {"data": "anonymized"}
            
            result = JSONService.anonymize_json(mock_json_payload)
            
            assert isinstance(result, str)
            # Verify process_dict was called with sp_recog parameter
            assert mock_process_dict.called
    
    def test_anonymize_json_with_nlp_ranha(self, mock_json_payload):
        """Test anonymize_json with ranha NLP model."""
        from privacy.service.json_service import JSONService
        
        mock_json_payload["nlp"] = "ranha"
        mock_json_payload["pii_entities_to_be_redacted"] = None
        
        mock_ranha = MagicMock()
        mock_ranha.supported_entities = ["PERSON", "EMAIL"]
        
        with patch('privacy.service.json_service.AnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnonymizerEngine'), \
             patch('privacy.service.json_service.ApiCall.request', return_value=None), \
             patch('privacy.service.json_service.ranha_recog', mock_ranha), \
             patch('privacy.service.json_service.registry') as mock_registry, \
             patch('privacy.service.json_service.JSONService.process_dict') as mock_process_dict, \
             patch('tempfile.NamedTemporaryFile', mock_open()):
            
            mock_registry.get_supported_entities.return_value = ["PHONE"]
            mock_process_dict.return_value = {"data": "anonymized"}
            
            result = JSONService.anonymize_json(mock_json_payload)
            
            assert isinstance(result, str)
    
    def test_anonymize_json_minimal_payload(self, mock_json_payload_minimal):
        """Test anonymize_json with minimal payload (all None values)."""
        from privacy.service.json_service import JSONService
        
        with patch('privacy.service.json_service.AnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnonymizerEngine'), \
             patch('privacy.service.json_service.ApiCall.request', return_value=None), \
             patch('privacy.service.json_service.JSONService.process_dict') as mock_process_dict, \
             patch('tempfile.NamedTemporaryFile', mock_open()):
            
            mock_process_dict.return_value = {"data": "test"}
            
            result = JSONService.anonymize_json(mock_json_payload_minimal)
            
            assert isinstance(result, str)
            data = json.loads(result)
            assert data == {"data": "test"}
    
    def test_anonymize_json_unsupported_data_type(self, mock_json_payload):
        """Test anonymize_json with unsupported data type."""
        from privacy.service.json_service import JSONService
        
        # JSON with string (not dict or list)
        mock_json_payload["file"].file = io.BytesIO(json.dumps("just a string").encode())
        
        with patch('privacy.service.json_service.AnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnonymizerEngine'), \
             patch('privacy.service.json_service.ApiCall.request', return_value=None):
            
            with pytest.raises(RuntimeError) as exc_info:
                JSONService.anonymize_json(mock_json_payload)
            
            assert "Unsupported data type" in str(exc_info.value)
    
    def test_anonymize_json_exception_handling(self, mock_json_payload):
        """Test anonymize_json exception handling."""
        from privacy.service.json_service import JSONService
        
        with patch('privacy.service.json_service.AnalyzerEngine', side_effect=Exception("Test error")), \
             patch('privacy.service.json_service.ApiCall.request', return_value=None):
            
            with pytest.raises(RuntimeError) as exc_info:
                JSONService.anonymize_json(mock_json_payload)
            
            assert "Test error" in str(exc_info.value)


class TestJSONServiceProcessDict:
    """Test suite for JSONService.process_dict method."""
    
    def test_process_dict_simple_structure(self):
        """Test process_dict with simple dictionary structure."""
        from privacy.service.json_service import JSONService
        
        data = {"key1": "value1", "key2": "value2"}
        mock_batch_analyzer = MagicMock()
        mock_batch_anonymizer = MagicMock()
        
        result = JSONService.process_dict(
            data, mock_batch_analyzer, mock_batch_anonymizer, 
            "en", [], None, [], None, 0.5, None
        )
        
        # Should return dict with same keys
        assert isinstance(result, dict)
        assert "key1" in result
        assert "key2" in result
    
    def test_process_dict_with_list_value(self):
        """Test process_dict with list values containing dicts."""
        from privacy.service.json_service import JSONService
        
        data = {
            "users": [
                {"name": "John", "email": "john@example.com"},
                {"name": "Jane", "email": "jane@example.com"}
            ]
        }
        
        mock_batch_analyzer = MagicMock()
        mock_batch_anonymizer = MagicMock()
        
        # Mock analyzer results
        mock_batch_analyzer.analyze_dict.return_value = {}
        mock_batch_anonymizer.anonymize_dict.return_value = {"name": "<PERSON>", "email": "<EMAIL>"}
        
        result = JSONService.process_dict(
            data, mock_batch_analyzer, mock_batch_anonymizer,
            "en", [], None, [], None, 0.5, None
        )
        
        # Should process list items
        assert "users" in result
        assert isinstance(result["users"], list)
        assert len(result["users"]) == 2
    
    def test_process_dict_with_non_dict_list_items(self):
        """Test process_dict with list containing non-dict items."""
        from privacy.service.json_service import JSONService
        
        data = {"numbers": [1, 2, 3, 4]}
        mock_batch_analyzer = MagicMock()
        mock_batch_anonymizer = MagicMock()
        
        result = JSONService.process_dict(
            data, mock_batch_analyzer, mock_batch_anonymizer,
            "en", [], None, [], None, 0.5, None
        )
        
        # Non-dict items should be preserved
        assert result["numbers"] == [1, 2, 3, 4]


class TestJSONServiceProcessList:
    """Test suite for JSONService.process_list method."""
    
    def test_process_list_with_dicts(self):
        """Test process_list with list of dictionaries."""
        from privacy.service.json_service import JSONService
        
        data = [
            {"name": "John", "email": "john@example.com"},
            {"name": "Jane", "email": "jane@example.com"}
        ]
        
        mock_batch_analyzer = MagicMock()
        mock_batch_anonymizer = MagicMock()
        
        # Mock analyzer and anonymizer
        mock_batch_analyzer.analyze_dict.return_value = {}
        mock_batch_anonymizer.anonymize_dict.return_value = {"name": "<PERSON>", "email": "<EMAIL>"}
        
        result = JSONService.process_list(
            data, mock_batch_analyzer, mock_batch_anonymizer,
            "en", [], None, [], None, 0.5, None
        )
        
        assert isinstance(result, list)
        assert len(result) == 2
    
    def test_process_list_with_non_dict_items(self):
        """Test process_list with non-dictionary items."""
        from privacy.service.json_service import JSONService
        
        data = ["string1", 123, True, None]
        
        mock_batch_analyzer = MagicMock()
        mock_batch_anonymizer = MagicMock()
        
        result = JSONService.process_list(
            data, mock_batch_analyzer, mock_batch_anonymizer,
            "en", [], None, [], None, 0.5, None
        )
        
        # Non-dict items should be preserved as-is
        assert result == ["string1", 123, True, None]
    
    def test_process_list_empty(self):
        """Test process_list with empty list."""
        from privacy.service.json_service import JSONService
        
        mock_batch_analyzer = MagicMock()
        mock_batch_anonymizer = MagicMock()
        
        result = JSONService.process_list(
            [], mock_batch_analyzer, mock_batch_anonymizer,
            "en", [], None, [], None, 0.5, None
        )
        
        assert result == []


class TestJSONServiceIntegration:
    """Integration tests for JSONService."""
    
    def test_full_anonymization_workflow(self):
        """Test complete JSON anonymization workflow."""
        from privacy.service.json_service import JSONService
        
        payload = {
            "file": MagicMock(),
            "keys_to_skip": ["id"],
            "pii_entities_to_be_redacted": "PERSON,EMAIL",
            "score_threshold": 0.5,
            "portfolio": None,
            "account": None,
            "nlp": None,
            "exclusion": None
        }
        
        json_data = {
            "users": [
                {"id": 1, "name": "John Doe", "email": "john@example.com"},
                {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
            ]
        }
        payload["file"].file = io.BytesIO(json.dumps(json_data).encode())
        
        with patch('privacy.service.json_service.AnalyzerEngine') as mock_analyzer_cls, \
             patch('privacy.service.json_service.BatchAnalyzerEngine') as mock_batch_analyzer_cls, \
             patch('privacy.service.json_service.BatchAnonymizerEngine') as mock_batch_anonymizer_cls, \
             patch('privacy.service.json_service.ApiCall.request', return_value=None), \
             patch('tempfile.NamedTemporaryFile', mock_open()):
            
            # Setup mocks
            mock_batch_analyzer = MagicMock()
            mock_batch_anonymizer = MagicMock()
            
            mock_batch_analyzer_cls.return_value = mock_batch_analyzer
            mock_batch_anonymizer_cls.return_value = mock_batch_anonymizer
            
            mock_batch_analyzer.analyze_dict.return_value = {}
            mock_batch_anonymizer.anonymize_dict.return_value = {
                "id": 1,
                "name": "<PERSON>",
                "email": "<EMAIL>"
            }
            
            result = JSONService.anonymize_json(payload)
            
            # Verify result
            assert isinstance(result, str)
            result_data = json.loads(result)
            assert "users" in result_data
            assert isinstance(result_data["users"], list)
    
    def test_flatten_and_reconstruct_roundtrip(self):
        """Test that flatten and reconstruct are inverse operations."""
        from privacy.service.json_service import JSONService
        
        original = {
            "user": {
                "name": "John",
                "contact": {
                    "email": "john@example.com",
                    "phone": "555-1234"
                }
            }
        }
        
        # Flatten then reconstruct
        flattened = JSONService.flatten_json(original)
        reconstructed = JSONService.reconstruct_json(flattened)
        
        # Verify structure is similar (keys should match)
        assert "user" in reconstructed
        assert isinstance(reconstructed["user"], dict)


class TestJSONServiceAdvancedScenarios:
    """Advanced test scenarios for JSON service."""
    
    def test_process_dict_with_pii_entities(self):
        """Test process_dict with specific PII entities to redact."""
        from privacy.service.json_service import JSONService
        
        data = {
            "users": [
                {"name": "John Doe", "ssn": "123-45-6789"}
            ]
        }
        
        mock_batch_analyzer = MagicMock()
        mock_batch_anonymizer = MagicMock()
        
        # Mock analyzer with specific entities
        mock_batch_analyzer.analyze_dict.return_value = {
            "name": [{"entity_type": "PERSON", "start": 0, "end": 8}]
        }
        mock_batch_anonymizer.anonymize_dict.return_value = {
            "name": "<PERSON>",
            "ssn": "<SSN>"
        }
        
        result = JSONService.process_dict(
            data, mock_batch_analyzer, mock_batch_anonymizer,
            "en", ["id"], None, [], ["PERSON", "SSN"], 0.6, None
        )
        
        assert "users" in result
        assert isinstance(result["users"], list)
    
    def test_process_dict_with_exception_handling(self):
        """Test process_dict handles exceptions in analyzer."""
        from privacy.service.json_service import JSONService
        
        data = {
            "items": [
                {"field": "value"}
            ]
        }
        
        mock_batch_analyzer = MagicMock()
        mock_batch_anonymizer = MagicMock()
        
        # Make analyzer raise exception
        mock_batch_analyzer.analyze_dict.side_effect = Exception("Analysis failed")
        
        with pytest.raises(RuntimeError) as exc_info:
            JSONService.process_dict(
                data, mock_batch_analyzer, mock_batch_anonymizer,
                "en", [], None, [], ["PERSON"], 0.5, None
            )
        
        assert "Analysis failed" in str(exc_info.value)
    
    def test_process_list_with_pii_entities(self):
        """Test process_list with specific PII entities."""
        from privacy.service.json_service import JSONService
        
        data = [
            {"name": "John", "email": "john@test.com"},
            {"name": "Jane", "email": "jane@test.com"}
        ]
        
        mock_batch_analyzer = MagicMock()
        mock_batch_anonymizer = MagicMock()
        
        mock_batch_analyzer.analyze_dict.return_value = {}
        mock_batch_anonymizer.anonymize_dict.return_value = {
            "name": "<PERSON>",
            "email": "<EMAIL>"
        }
        
        result = JSONService.process_list(
            data, mock_batch_analyzer, mock_batch_anonymizer,
            "en", [], None, [], ["PERSON", "EMAIL"], 0.7, None
        )
        
        assert isinstance(result, list)
        assert len(result) == 2
    
    def test_process_list_with_exception(self):
        """Test process_list handles exceptions."""
        from privacy.service.json_service import JSONService
        
        data = [{"field": "value"}]
        
        mock_batch_analyzer = MagicMock()
        mock_batch_anonymizer = MagicMock()
        
        mock_batch_analyzer.analyze_dict.side_effect = Exception("Processing error")
        
        with pytest.raises(RuntimeError):
            JSONService.process_list(
                data, mock_batch_analyzer, mock_batch_anonymizer,
                "en", [], None, [], ["PERSON"], 0.5, None
            )
    
    def test_anonymize_json_with_score_threshold_zero(self):
        """Test anonymize_json with score threshold of 0."""
        from privacy.service.json_service import JSONService
        
        payload = {
            "file": MagicMock(),
            "keys_to_skip": [],
            "pii_entities_to_be_redacted": None,
            "score_threshold": 0,
            "portfolio": None,
            "account": None,
            "nlp": None,
            "exclusion": None
        }
        payload["file"].file = io.BytesIO(json.dumps({"test": "data"}).encode())
        
        with patch('privacy.service.json_service.AnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnonymizerEngine'), \
             patch('privacy.service.json_service.ApiCall.request', return_value=None), \
             patch('privacy.service.json_service.JSONService.process_dict') as mock_process, \
             patch('tempfile.NamedTemporaryFile', mock_open()):
            
            mock_process.return_value = {"test": "anonymized"}
            
            result = JSONService.anonymize_json(payload)
            
            assert isinstance(result, str)
            # Verify score_threshold of 0 was used
            call_args = mock_process.call_args
            assert call_args[0][8] == 0  # score_threshold parameter
    
    def test_anonymize_json_with_empty_exclusion_list(self):
        """Test anonymize_json with empty exclusion after split."""
        from privacy.service.json_service import JSONService
        
        payload = {
            "file": MagicMock(),
            "keys_to_skip": [],
            "pii_entities_to_be_redacted": "PERSON",
            "score_threshold": 0.5,
            "portfolio": None,
            "account": None,
            "nlp": None,
            "exclusion": ""
        }
        payload["file"].file = io.BytesIO(json.dumps({"name": "test"}).encode())
        
        with patch('privacy.service.json_service.AnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnonymizerEngine'), \
             patch('privacy.service.json_service.ApiCall.request', return_value=None), \
             patch('privacy.service.json_service.JSONService.process_dict') as mock_process, \
             patch('tempfile.NamedTemporaryFile', mock_open()):
            
            mock_process.return_value = {"name": "<PERSON>"}
            
            result = JSONService.anonymize_json(payload)
            
            assert isinstance(result, str)
            # Empty string split should result in ['']
            call_args = mock_process.call_args
            assert call_args[0][6] == ['']  # exclusion parameter
    
    def test_process_dict_with_keys_to_skip(self):
        """Test process_dict respects keys_to_skip parameter."""
        from privacy.service.json_service import JSONService
        
        data = {
            "records": [
                {"id": 1, "name": "John", "secret": "data"}
            ]
        }
        
        mock_batch_analyzer = MagicMock()
        mock_batch_anonymizer = MagicMock()
        
        mock_batch_analyzer.analyze_dict.return_value = {}
        mock_batch_anonymizer.anonymize_dict.return_value = {
            "id": 1,
            "name": "<PERSON>",
            "secret": "data"
        }
        
        result = JSONService.process_dict(
            data, mock_batch_analyzer, mock_batch_anonymizer,
            "en", ["id", "secret"], None, [], None, 0.5, None
        )
        
        # Verify keys_to_skip was passed to analyzer
        mock_batch_analyzer.analyze_dict.assert_called()
        call_kwargs = mock_batch_analyzer.analyze_dict.call_args[1]
        assert call_kwargs["keys_to_skip"] == ["id", "secret"]
    
    def test_process_list_with_keys_to_skip(self):
        """Test process_list respects keys_to_skip parameter."""
        from privacy.service.json_service import JSONService
        
        data = [
            {"id": 1, "data": "sensitive"},
            {"id": 2, "data": "info"}
        ]
        
        mock_batch_analyzer = MagicMock()
        mock_batch_anonymizer = MagicMock()
        
        mock_batch_analyzer.analyze_dict.return_value = {}
        mock_batch_anonymizer.anonymize_dict.return_value = {
            "id": 1,
            "data": "<REDACTED>"
        }
        
        result = JSONService.process_list(
            data, mock_batch_analyzer, mock_batch_anonymizer,
            "en", ["id"], None, [], None, 0.5, None
        )
        
        # Verify keys_to_skip was passed
        assert mock_batch_analyzer.analyze_dict.call_count == 2
        for call in mock_batch_analyzer.analyze_dict.call_args_list:
            assert call[1]["keys_to_skip"] == ["id"]
    
    def test_anonymize_json_with_nlp_ranha_and_pii_entities(self):
        """Test anonymize_json with ranha NLP and PII entities specified."""
        from privacy.service.json_service import JSONService
        
        payload = {
            "file": MagicMock(),
            "keys_to_skip": [],
            "pii_entities_to_be_redacted": "PERSON,EMAIL",
            "score_threshold": 0.5,
            "portfolio": None,
            "account": None,
            "nlp": "ranha",
            "exclusion": None
        }
        payload["file"].file = io.BytesIO(json.dumps({"test": "data"}).encode())
        
        mock_ranha = MagicMock()
        mock_ranha.supported_entities = ["LOCATION"]
        
        with patch('privacy.service.json_service.AnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnonymizerEngine'), \
             patch('privacy.service.json_service.ApiCall.request', return_value=None), \
             patch('privacy.service.json_service.ranha_recog', mock_ranha), \
             patch('privacy.service.json_service.registry') as mock_registry, \
             patch('privacy.service.json_service.JSONService.process_dict') as mock_process, \
             patch('tempfile.NamedTemporaryFile', mock_open()):
            
            mock_registry.get_supported_entities.return_value = []
            mock_process.return_value = {"test": "anonymized"}
            
            result = JSONService.anonymize_json(payload)
            
            # When pii_entities specified with ranha, should not call get_supported_entities
            assert isinstance(result, str)
    
    def test_anonymize_json_with_portfolio_only(self):
        """Test anonymize_json with portfolio but no account."""
        from privacy.service.json_service import JSONService
        
        payload = {
            "file": MagicMock(),
            "keys_to_skip": [],
            "pii_entities_to_be_redacted": None,
            "score_threshold": 0.5,
            "portfolio": "TestPortfolio",
            "account": None,
            "nlp": None,
            "exclusion": None
        }
        payload["file"].file = io.BytesIO(json.dumps({"data": "test"}).encode())
        
        with patch('privacy.service.json_service.AnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnonymizerEngine'), \
             patch('privacy.service.json_service.ApiCall.request') as mock_api, \
             patch('privacy.service.json_service.JSONService.process_dict') as mock_process, \
             patch('tempfile.NamedTemporaryFile', mock_open()):
            
            mock_api.return_value = None
            mock_process.return_value = {"data": "test"}
            
            result = JSONService.anonymize_json(payload)
            
            # Should call API with portfolio
            mock_api.assert_called_once()
            assert result is None  # Returns None when API returns None
    
    def test_flatten_json_with_numeric_dict_keys(self):
        """Test flatten_json handles numeric-like string keys."""
        from privacy.service.json_service import JSONService
        
        data = {
            "0": "value0",
            "1": "value1",
            "items": {
                "2": "value2"
            }
        }
        
        result = JSONService.flatten_json(data)
        
        assert "0" in result
        assert "1" in result
        assert "items_2" in result
    
    def test_reconstruct_json_with_numeric_indices(self):
        """Test reconstruct_json properly handles numeric indices."""
        from privacy.service.json_service import JSONService
        
        flattened = {
            "list_0": "first",
            "list_1": "second",
            "list_2": "third"
        }
        
        result = JSONService.reconstruct_json(flattened)
        
        assert "list" in result
    
    def test_process_dict_empty_list_value(self):
        """Test process_dict with empty list as value."""
        from privacy.service.json_service import JSONService
        
        data = {
            "empty_list": [],
            "non_empty": "value"
        }
        
        mock_batch_analyzer = MagicMock()
        mock_batch_anonymizer = MagicMock()
        
        result = JSONService.process_dict(
            data, mock_batch_analyzer, mock_batch_anonymizer,
            "en", [], None, [], None, 0.5, None
        )
        
        assert result["empty_list"] == []
        assert result["non_empty"] == "value"
    
    def test_anonymize_json_creates_temp_file(self):
        """Test that anonymize_json creates a temporary file."""
        from privacy.service.json_service import JSONService
        
        payload = {
            "file": MagicMock(),
            "keys_to_skip": [],
            "pii_entities_to_be_redacted": None,
            "score_threshold": None,
            "portfolio": None,
            "account": None,
            "nlp": None,
            "exclusion": None
        }
        payload["file"].file = io.BytesIO(json.dumps({"test": "data"}).encode())
        
        mock_temp_file = MagicMock()
        mock_temp_file.__enter__ = MagicMock(return_value=mock_temp_file)
        mock_temp_file.__exit__ = MagicMock(return_value=False)
        mock_temp_file.write = MagicMock()
        
        with patch('privacy.service.json_service.AnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnalyzerEngine'), \
             patch('privacy.service.json_service.BatchAnonymizerEngine'), \
             patch('privacy.service.json_service.ApiCall.request', return_value=None), \
             patch('privacy.service.json_service.JSONService.process_dict') as mock_process, \
             patch('tempfile.NamedTemporaryFile', return_value=mock_temp_file) as mock_tempfile:
            
            mock_process.return_value = {"test": "anonymized"}
            
            result = JSONService.anonymize_json(payload)
            
            # Verify temp file was created and written to
            mock_tempfile.assert_called_once()
            assert mock_temp_file.write.called
            # Verify JSON was written
            written_data = mock_temp_file.write.call_args[0][0]
            assert b"anonymized" in written_data

