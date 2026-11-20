"""Targeted tests for JSONService to improve coverage"""
import json
import pytest
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock
from privacy.service.json_service import JSONService


class TestJSONServiceAnonymization:
    """Test JSON anonymization with various configurations"""
    
    @patch('privacy.service.json_service.ApiCall')
    @patch('privacy.service.json_service.BatchAnonymizerEngine')
    @patch('privacy.service.json_service.BatchAnalyzerEngine')
    @patch('privacy.service.json_service.AnalyzerEngine')
    def test_anonymize_json_dict_with_portfolio(self, mock_analyzer_class, mock_batch_analyzer_class,
                                                 mock_batch_anonymizer_class, mock_api_call):
        """Test JSON dict anonymization with portfolio"""
        mock_api_call.request.return_value = {"allowed": True}
        mock_analyzer = Mock()
        mock_batch_analyzer = Mock()
        mock_batch_anonymizer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_batch_analyzer_class.return_value = mock_batch_analyzer
        mock_batch_anonymizer_class.return_value = mock_batch_anonymizer
        
        test_data = {"name": "John", "email": "john@example.com"}
        mock_file = Mock()
        mock_file.file = BytesIO(json.dumps(test_data).encode())
        
        with patch.object(JSONService, 'process_dict', return_value={"name": "REDACTED", "email": "REDACTED"}):
            payload = {
                "file": mock_file,
                "portfolio": "test_portfolio",
                "account": "test_account",
                "keys_to_skip": [],
                "pii_entities_to_be_redacted": "PERSON,EMAIL",
                "score_threshold": 0.5,
                "nlp": "roberta",
                "exclusion": None
            }
            
            result = JSONService.anonymize_json(payload)
            assert "REDACTED" in result
    
    @patch('privacy.service.json_service.BatchAnonymizerEngine')
    @patch('privacy.service.json_service.BatchAnalyzerEngine')
    @patch('privacy.service.json_service.AnalyzerEngine')
    def test_anonymize_json_list_without_portfolio(self, mock_analyzer_class, mock_batch_analyzer_class,
                                                     mock_batch_anonymizer_class):
        """Test JSON list anonymization without portfolio"""
        mock_analyzer = Mock()
        mock_batch_analyzer = Mock()
        mock_batch_anonymizer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_batch_analyzer_class.return_value = mock_batch_analyzer
        mock_batch_anonymizer_class.return_value = mock_batch_anonymizer
        
        test_data = [{"name": "Jane"}, {"name": "Bob"}]
        mock_file = Mock()
        mock_file.file = BytesIO(json.dumps(test_data).encode())
        
        with patch.object(JSONService, 'process_list', return_value=[{"name": "REDACTED"}, {"name": "REDACTED"}]):
            payload = {
                "file": mock_file,
                "portfolio": None,
                "account": None,
                "keys_to_skip": ["id"],
                "pii_entities_to_be_redacted": None,
                "score_threshold": None,
                "nlp": "en_core_web_lg",
                "exclusion": "test1,test2"
            }
            
            result = JSONService.anonymize_json(payload)
            assert "REDACTED" in result
    
    @patch('privacy.service.json_service.roberta_recog')
    @patch('privacy.service.json_service.BatchAnonymizerEngine')
    @patch('privacy.service.json_service.BatchAnalyzerEngine')
    @patch('privacy.service.json_service.AnalyzerEngine')
    def test_anonymize_json_with_roberta_nlp(self, mock_analyzer_class, mock_batch_analyzer_class,
                                               mock_batch_anonymizer_class, mock_roberta):
        """Test JSON anonymization with roberta NLP model"""
        mock_analyzer = Mock()
        mock_batch_analyzer = Mock()
        mock_batch_anonymizer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_batch_analyzer_class.return_value = mock_batch_analyzer
        mock_batch_anonymizer_class.return_value = mock_batch_anonymizer
        mock_roberta.supported_entities = ["PERSON"]
        
        test_data = {"user": "Alice"}
        mock_file = Mock()
        mock_file.file = BytesIO(json.dumps(test_data).encode())
        
        with patch.object(JSONService, 'process_dict', return_value={"user": "REDACTED"}):
            payload = {
                "file": mock_file,
                "portfolio": None,
                "account": None,
                "keys_to_skip": [],
                "pii_entities_to_be_redacted": "PERSON",
                "score_threshold": 0.7,
                "nlp": "roberta",
                "exclusion": None
            }
            
            result = JSONService.anonymize_json(payload)
            assert result is not None
    
    @patch('privacy.service.json_service.ranha_recog')
    @patch('privacy.service.json_service.registry')
    @patch('privacy.service.json_service.BatchAnonymizerEngine')
    @patch('privacy.service.json_service.BatchAnalyzerEngine')
    @patch('privacy.service.json_service.AnalyzerEngine')
    def test_anonymize_json_with_ranha_nlp(self, mock_analyzer_class, mock_batch_analyzer_class,
                                             mock_batch_anonymizer_class, mock_registry, mock_ranha):
        """Test JSON anonymization with ranha NLP model"""
        mock_analyzer = Mock()
        mock_batch_analyzer = Mock()
        mock_batch_anonymizer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_batch_analyzer_class.return_value = mock_batch_analyzer
        mock_batch_anonymizer_class.return_value = mock_batch_anonymizer
        mock_ranha.supported_entities = ["PERSON", "ORG"]
        mock_registry.get_supported_entities.return_value = ["LOCATION"]
        
        test_data = {"company": "Acme Corp"}
        mock_file = Mock()
        mock_file.file = BytesIO(json.dumps(test_data).encode())
        
        with patch.object(JSONService, 'process_dict', return_value={"company": "REDACTED"}):
            payload = {
                "file": mock_file,
                "portfolio": None,
                "account": None,
                "keys_to_skip": [],
                "pii_entities_to_be_redacted": None,
                "score_threshold": 0.5,
                "nlp": "ranha",
                "exclusion": "skip"
            }
            
            result = JSONService.anonymize_json(payload)
            assert result is not None
    
    @patch('privacy.service.json_service.BatchAnonymizerEngine')
    @patch('privacy.service.json_service.BatchAnalyzerEngine')
    @patch('privacy.service.json_service.AnalyzerEngine')
    def test_anonymize_json_unsupported_type(self, mock_analyzer_class, mock_batch_analyzer_class,
                                               mock_batch_anonymizer_class):
        """Test JSON anonymization with unsupported data type"""
        mock_analyzer = Mock()
        mock_batch_analyzer = Mock()
        mock_batch_anonymizer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_batch_analyzer_class.return_value = mock_batch_analyzer
        mock_batch_anonymizer_class.return_value = mock_batch_anonymizer
        
        test_data = "not_dict_or_list"
        mock_file = Mock()
        mock_file.file = BytesIO(json.dumps(test_data).encode())
        
        payload = {
            "file": mock_file,
            "portfolio": None,
            "account": None,
            "keys_to_skip": [],
            "pii_entities_to_be_redacted": None,
            "score_threshold": None,
            "nlp": "en_core_web_lg",
            "exclusion": None
        }
        
        with pytest.raises(RuntimeError):
            JSONService.anonymize_json(payload)
    
    @patch('privacy.service.json_service.ApiCall')
    @patch('privacy.service.json_service.BatchAnonymizerEngine')
    @patch('privacy.service.json_service.BatchAnalyzerEngine')
    @patch('privacy.service.json_service.AnalyzerEngine')
    def test_anonymize_json_portfolio_returns_none(self, mock_analyzer_class, mock_batch_analyzer_class,
                                                     mock_batch_anonymizer_class, mock_api_call):
        """Test JSON anonymization when portfolio validation returns None"""
        mock_api_call.request.return_value = None
        mock_analyzer = Mock()
        mock_batch_analyzer = Mock()
        mock_batch_anonymizer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_batch_analyzer_class.return_value = mock_batch_analyzer
        mock_batch_anonymizer_class.return_value = mock_batch_anonymizer
        
        test_data = {"data": "test"}
        mock_file = Mock()
        mock_file.file = BytesIO(json.dumps(test_data).encode())
        
        payload = {
            "file": mock_file,
            "portfolio": "invalid_portfolio",
            "account": "invalid_account",
            "keys_to_skip": [],
            "pii_entities_to_be_redacted": None,
            "score_threshold": None,
            "nlp": "en_core_web_lg",
            "exclusion": None
        }
        
        result = JSONService.anonymize_json(payload)
        assert result is None


# ============================================================================
# Tests for JSONService utility methods (flatten/reconstruct)
# ============================================================================

class TestJSONServiceUtilities:
    """Test JSONService utility methods like flatten_json and reconstruct_json"""
    
    def test_flatten_json_simple_dict(self):
        """Test flatten_json with a simple dictionary"""
        input_json = {"name": "John", "age": 30}
        result = JSONService.flatten_json(input_json)
        
        assert result is not None
        assert isinstance(result, dict)
        assert "name" in result or ("name",) in result
    
    def test_flatten_json_nested_dict(self):
        """Test flatten_json with nested dictionaries"""
        input_json = {
            "user": {
                "name": "Alice",
                "address": {
                    "city": "NYC",
                    "zip": "10001"
                }
            }
        }
        result = JSONService.flatten_json(input_json)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_flatten_json_with_list(self):
        """Test flatten_json with lists"""
        input_json = {"items": ["apple", "banana", "cherry"]}
        result = JSONService.flatten_json(input_json)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_flatten_json_deeply_nested(self):
        """Test flatten_json with deeply nested structure"""
        input_json = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deep"
                    }
                }
            }
        }
        result = JSONService.flatten_json(input_json)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_flatten_json_empty_dict(self):
        """Test flatten_json with empty dictionary"""
        input_json = {}
        result = JSONService.flatten_json(input_json)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_flatten_json_with_mixed_types(self):
        """Test flatten_json with mixed data types"""
        input_json = {
            "string": "text",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "dict": {"key": "value"}
        }
        result = JSONService.flatten_json(input_json)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_flatten_json_with_special_characters_in_keys(self):
        """Test flatten_json with special characters in keys"""
        input_json = {
            "key-with-dash": "value1",
            "key.with.dot": "value2",
            "key_with_underscore": "value3"
        }
        result = JSONService.flatten_json(input_json)
        
        assert result is not None
        assert isinstance(result, dict)


