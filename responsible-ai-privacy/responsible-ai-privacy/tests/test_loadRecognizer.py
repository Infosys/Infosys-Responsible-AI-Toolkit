"""
Comprehensive tests for loadRecognizer.py module
Tests LoadRecognizer class for setting and loading custom recognizers
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import io
from privacy.service.loadRecognizer import LoadRecognizer, AttributeDict


class TestAttributeDict:
    """Test AttributeDict functionality"""
    
    def test_attribute_dict_basic(self):
        """Test basic AttributeDict operations"""
        ad = AttributeDict({"RecogName": "TEST", "RecogType": "Data"})
        
        assert ad.RecogName == "TEST"
        assert ad.RecogType == "Data"
        assert ad["RecogName"] == "TEST"


class TestLoadRecognizerSetRecognizer:
    """Test LoadRecognizer.set_recognizer() method"""
    
    @patch('privacy.service.loadRecognizer.registry')
    @patch('privacy.service.loadRecognizer.request_id_var')
    @patch('privacy.service.loadRecognizer.error_dict', {})
    @patch('privacy.service.loadRecognizer.ranha_recog')
    def test_set_recognizer_data_type(self, mock_ranha_recog, mock_request_id_var, mock_registry):
        """Test set_recognizer with Data type recognizer"""
        mock_request_id_var.get.return_value = "test-uuid-data"
        mock_registry.get_supported_entities.return_value = ["PERSON", "EMAIL"]
        mock_ranha_recog.get_supported_entities.return_value = ["PERSON", "EMAIL", "CUSTOM"]
        
        # Create mock file with JSON data
        json_data = [
            {
                "RecogName": "COMPANY_NAME",
                "RecogType": "Data",
                "EntityValue": ["Microsoft", "Google", "Apple"],
                "Score": 0.9,
                "isPreDefined": "No"
            }
        ]
        
        json_bytes = json.dumps(json_data).encode('utf-8')
        mock_file = Mock()
        mock_file.file.read.return_value = json_bytes
        
        payload = {"file": mock_file}
        
        result = LoadRecognizer.set_recognizer(payload)
        
        # Verify DataListRecognizer was added
        assert mock_registry.add_recognizer.called
        assert "Available Recognizers" in result
    
    @patch('privacy.service.loadRecognizer.registry')
    @patch('privacy.service.loadRecognizer.request_id_var')
    @patch('privacy.service.loadRecognizer.error_dict', {})
    @patch('privacy.service.loadRecognizer.ranha_recog')
    def test_set_recognizer_pattern_type(self, mock_ranha_recog, mock_request_id_var, mock_registry):
        """Test set_recognizer with Pattern type recognizer"""
        mock_request_id_var.get.return_value = "test-uuid-pattern"
        mock_registry.get_supported_entities.return_value = ["PERSON", "EMAIL"]
        mock_ranha_recog.get_supported_entities.return_value = ["PERSON", "EMAIL", "EXTRA"]
        
        # Create mock file with pattern recognizer
        json_data = [
            {
                "RecogName": "CUSTOM_ID",
                "RecogType": "Pattern",
                "EntityValue": ["[A-Z]{3}\\d{6}", "[0-9]{10}"],
                "Score": 0.85,
                "Context": "id,identifier,number",
                "isPreDefined": "No"
            }
        ]
        
        json_bytes = json.dumps(json_data).encode('utf-8')
        mock_file = Mock()
        mock_file.file.read.return_value = json_bytes
        
        payload = {"file": mock_file}
        
        result = LoadRecognizer.set_recognizer(payload)
        
        # Verify PatternRecognizer was added
        assert mock_registry.add_recognizer.called
        assert "Available Recognizers" in result
        assert "*" in result
    
    @patch('privacy.service.loadRecognizer.registry')
    @patch('privacy.service.loadRecognizer.request_id_var')
    @patch('privacy.service.loadRecognizer.error_dict', {})
    @patch('privacy.service.loadRecognizer.ranha_recog')
    def test_set_recognizer_pattern_with_string_value(self, mock_ranha_recog, mock_request_id_var, mock_registry):
        """Test set_recognizer with pattern as string (not list)"""
        mock_request_id_var.get.return_value = "test-uuid-string-pattern"
        mock_registry.get_supported_entities.return_value = ["ENTITY1"]
        mock_ranha_recog.get_supported_entities.return_value = ["ENTITY1", "ENTITY2"]
        
        json_data = [
            {
                "RecogName": "SIMPLE_PATTERN",
                "RecogType": "Pattern",
                "EntityValue": "\\d{3}-\\d{2}-\\d{4}",  # String instead of list
                "Score": 0.9,
                "Context": "ssn",
                "isPreDefined": "No"
            }
        ]
        
        json_bytes = json.dumps(json_data).encode('utf-8')
        mock_file = Mock()
        mock_file.file.read.return_value = json_bytes
        
        payload = {"file": mock_file}
        
        result = LoadRecognizer.set_recognizer(payload)
        
        assert mock_registry.add_recognizer.called
        assert "Available Recognizers" in result
    
    @patch('privacy.service.loadRecognizer.registry')
    @patch('privacy.service.loadRecognizer.request_id_var')
    @patch('privacy.service.loadRecognizer.error_dict', {})
    @patch('privacy.service.loadRecognizer.ranha_recog')
    def test_set_recognizer_pattern_with_list_context(self, mock_ranha_recog, mock_request_id_var, mock_registry):
        """Test set_recognizer with context as list"""
        mock_request_id_var.get.return_value = "test-uuid-list-context"
        mock_registry.get_supported_entities.return_value = []
        mock_ranha_recog.get_supported_entities.return_value = ["EXTRA"]
        
        json_data = [
            {
                "RecogName": "ACCOUNT_NUM",
                "RecogType": "Pattern",
                "EntityValue": ["\\d{12}"],
                "Score": 0.88,
                "Context": ["account", "acct", "acc_num"],  # List instead of string
                "isPreDefined": "No"
            }
        ]
        
        json_bytes = json.dumps(json_data).encode('utf-8')
        mock_file = Mock()
        mock_file.file.read.return_value = json_bytes
        
        payload = {"file": mock_file}
        
        result = LoadRecognizer.set_recognizer(payload)
        
        assert mock_registry.add_recognizer.called
    
    @patch('privacy.service.loadRecognizer.registry')
    @patch('privacy.service.loadRecognizer.request_id_var')
    @patch('privacy.service.loadRecognizer.error_dict', {})
    @patch('privacy.service.loadRecognizer.ranha_recog')
    def test_set_recognizer_multiple_recognizers(self, mock_ranha_recog, mock_request_id_var, mock_registry):
        """Test set_recognizer with multiple recognizers in one file"""
        mock_request_id_var.get.return_value = "test-uuid-multiple"
        mock_registry.get_supported_entities.return_value = ["EMAIL"]
        mock_ranha_recog.get_supported_entities.return_value = ["EMAIL", "PHONE"]
        
        json_data = [
            {
                "RecogName": "COMPANY",
                "RecogType": "Data",
                "EntityValue": ["IBM", "Oracle"],
                "Score": 0.9,
                "isPreDefined": "No"
            },
            {
                "RecogName": "EMPLOYEE_ID",
                "RecogType": "Pattern",
                "EntityValue": "EMP\\d{6}",
                "Score": 0.95,
                "Context": "employee,emp_id",
                "isPreDefined": "No"
            }
        ]
        
        json_bytes = json.dumps(json_data).encode('utf-8')
        mock_file = Mock()
        mock_file.file.read.return_value = json_bytes
        
        payload = {"file": mock_file}
        
        result = LoadRecognizer.set_recognizer(payload)
        
        # Should add both recognizers
        assert mock_registry.add_recognizer.call_count == 2
        assert "Available Recognizers" in result
    
    @patch('privacy.service.loadRecognizer.registry')
    @patch('privacy.service.loadRecognizer.request_id_var')
    @patch('privacy.service.loadRecognizer.error_dict', {})
    @patch('privacy.service.loadRecognizer.ranha_recog')
    def test_set_recognizer_predefined_skipped(self, mock_ranha_recog, mock_request_id_var, mock_registry):
        """Test that predefined recognizers (isPreDefined=Yes) are skipped"""
        mock_request_id_var.get.return_value = "test-uuid-predefined"
        mock_registry.get_supported_entities.return_value = []
        mock_ranha_recog.get_supported_entities.return_value = []
        
        json_data = [
            {
                "RecogName": "PREDEFINED_ENTITY",
                "RecogType": "Pattern",
                "EntityValue": "test",
                "Score": 0.9,
                "Context": "test",
                "isPreDefined": "Yes"  # Should be skipped
            }
        ]
        
        json_bytes = json.dumps(json_data).encode('utf-8')
        mock_file = Mock()
        mock_file.file.read.return_value = json_bytes
        
        payload = {"file": mock_file}
        
        result = LoadRecognizer.set_recognizer(payload)
        
        # Should not add any recognizer (isPreDefined=Yes is skipped)
        assert mock_registry.add_recognizer.call_count == 0
    
    @patch('privacy.service.loadRecognizer.request_id_var')
    @patch('privacy.service.loadRecognizer.error_dict', {})
    @patch('privacy.service.loadRecognizer.log')
    def test_set_recognizer_exception_handling(self, mock_log, mock_request_id_var):
        """Test exception handling in set_recognizer"""
        mock_request_id_var.get.return_value = "test-uuid-error"
        
        from privacy.service.loadRecognizer import error_dict
        error_dict["test-uuid-error"] = []
        
        # Create invalid JSON to trigger exception
        mock_file = Mock()
        mock_file.file.read.return_value = b"invalid json {"
        
        payload = {"file": mock_file}
        
        with pytest.raises(Exception):
            LoadRecognizer.set_recognizer(payload)
        
        # Verify error was logged
        assert mock_log.error.called
        assert len(error_dict["test-uuid-error"]) > 0
    
    @patch('privacy.service.loadRecognizer.registry')
    @patch('privacy.service.loadRecognizer.request_id_var')
    @patch('privacy.service.loadRecognizer.error_dict', {})
    @patch('privacy.service.loadRecognizer.ranha_recog')
    def test_set_recognizer_returns_available_recognizers(self, mock_ranha_recog, mock_request_id_var, mock_registry):
        """Test that set_recognizer returns available recognizers list"""
        mock_request_id_var.get.return_value = "test-uuid-return"
        mock_registry.get_supported_entities.return_value = ["PERSON", "EMAIL", "PHONE"]
        mock_ranha_recog.get_supported_entities.return_value = ["PERSON", "EMAIL", "PHONE", "CUSTOM_RANHA"]
        
        json_data = [
            {
                "RecogName": "TEST_ENTITY",
                "RecogType": "Data",
                "EntityValue": ["test"],
                "Score": 0.9,
                "isPreDefined": "No"
            }
        ]
        
        json_bytes = json.dumps(json_data).encode('utf-8')
        mock_file = Mock()
        mock_file.file.read.return_value = json_bytes
        
        payload = {"file": mock_file}
        
        result = LoadRecognizer.set_recognizer(payload)
        
        assert "Available Recognizers" in result
        assert isinstance(result["Available Recognizers"], list)
        # Should contain registry entities + ranha entities with * suffix
        assert "CUSTOM_RANHA*" in result["Available Recognizers"]
        assert "*" in result
    
    @patch('privacy.service.loadRecognizer.registry')
    @patch('privacy.service.loadRecognizer.request_id_var')
    @patch('privacy.service.loadRecognizer.error_dict', {})
    @patch('privacy.service.loadRecognizer.ranha_recog')
    def test_set_recognizer_empty_file(self, mock_ranha_recog, mock_request_id_var, mock_registry):
        """Test set_recognizer with empty JSON array"""
        mock_request_id_var.get.return_value = "test-uuid-empty"
        mock_registry.get_supported_entities.return_value = ["DEFAULT"]
        mock_ranha_recog.get_supported_entities.return_value = ["DEFAULT"]
        
        json_data = []
        
        json_bytes = json.dumps(json_data).encode('utf-8')
        mock_file = Mock()
        mock_file.file.read.return_value = json_bytes
        
        payload = {"file": mock_file}
        
        result = LoadRecognizer.set_recognizer(payload)
        
        # Should complete successfully without adding any recognizers
        assert mock_registry.add_recognizer.call_count == 0
        assert "Available Recognizers" in result


class TestLoadRecognizerLoadRecognizer:
    """Test LoadRecognizer.load_recognizer() method"""
    
    @patch('privacy.service.loadRecognizer.registry')
    @patch('privacy.service.loadRecognizer.ranha_recog')
    def test_load_recognizer_returns_available_entities(self, mock_ranha_recog, mock_registry):
        """Test load_recognizer returns list of available recognizers"""
        mock_registry.get_supported_entities.return_value = ["PERSON", "EMAIL", "CREDIT_CARD"]
        mock_ranha_recog.get_supported_entities.return_value = ["PERSON", "EMAIL", "CREDIT_CARD", "RANHA_CUSTOM"]
        
        result = LoadRecognizer.load_recognizer()
        
        assert "Available Recognizers" in result
        assert isinstance(result["Available Recognizers"], list)
        # Should contain all registry entities
        assert "PERSON" in result["Available Recognizers"]
        assert "EMAIL" in result["Available Recognizers"]
        # Ranha-specific entity should have * suffix
        assert "RANHA_CUSTOM*" in result["Available Recognizers"]
        assert "*" in result
    
    @patch('privacy.service.loadRecognizer.registry')
    @patch('privacy.service.loadRecognizer.ranha_recog')
    def test_load_recognizer_explanation_message(self, mock_ranha_recog, mock_registry):
        """Test that load_recognizer includes explanation for starred entities"""
        mock_registry.get_supported_entities.return_value = ["ENTITY1"]
        mock_ranha_recog.get_supported_entities.return_value = ["ENTITY1", "ENTITY2"]
        
        result = LoadRecognizer.load_recognizer()
        
        assert "*" in result
        assert "select NLP:ranha" in result["*"]
    
    @patch('privacy.service.loadRecognizer.registry')
    @patch('privacy.service.loadRecognizer.ranha_recog')
    def test_load_recognizer_no_ranha_specific_entities(self, mock_ranha_recog, mock_registry):
        """Test load_recognizer when all ranha entities are in registry"""
        mock_registry.get_supported_entities.return_value = ["PERSON", "EMAIL"]
        mock_ranha_recog.get_supported_entities.return_value = ["PERSON", "EMAIL"]
        
        result = LoadRecognizer.load_recognizer()
        
        # No entities should have * suffix since there's no difference
        recognizers = result["Available Recognizers"]
        starred_entities = [r for r in recognizers if r.endswith("*")]
        assert len(starred_entities) == 0
    
    @patch('privacy.service.loadRecognizer.registry')
    @patch('privacy.service.loadRecognizer.ranha_recog')
    def test_load_recognizer_all_unique_ranha_entities(self, mock_ranha_recog, mock_registry):
        """Test load_recognizer with all ranha entities unique"""
        mock_registry.get_supported_entities.return_value = []
        mock_ranha_recog.get_supported_entities.return_value = ["RANHA1", "RANHA2", "RANHA3"]
        
        result = LoadRecognizer.load_recognizer()
        
        # All ranha entities should have * suffix
        recognizers = result["Available Recognizers"]
        assert "RANHA1*" in recognizers
        assert "RANHA2*" in recognizers
        assert "RANHA3*" in recognizers
    
    @patch('privacy.service.loadRecognizer.request_id_var')
    @patch('privacy.service.loadRecognizer.error_dict', {})
    @patch('privacy.service.loadRecognizer.log')
    @patch('privacy.service.loadRecognizer.registry')
    def test_load_recognizer_exception_handling(self, mock_registry, mock_log, mock_request_id_var):
        """Test exception handling in load_recognizer"""
        mock_request_id_var.get.return_value = "test-uuid-load-error"
        
        from privacy.service.loadRecognizer import error_dict
        error_dict["test-uuid-load-error"] = []
        
        # Make registry.get_supported_entities raise exception
        mock_registry.get_supported_entities.side_effect = RuntimeError("Registry error")
        
        with pytest.raises(Exception):
            LoadRecognizer.load_recognizer()
        
        # Verify error was logged
        assert mock_log.error.called
        assert len(error_dict["test-uuid-load-error"]) > 0


class TestLoadRecognizerIntegration:
    """Integration tests for LoadRecognizer"""
    
    @patch('privacy.service.loadRecognizer.registry')
    @patch('privacy.service.loadRecognizer.request_id_var')
    @patch('privacy.service.loadRecognizer.error_dict', {})
    @patch('privacy.service.loadRecognizer.ranha_recog')
    def test_full_workflow_set_and_load(self, mock_ranha_recog, mock_request_id_var, mock_registry):
        """Test complete workflow: set_recognizer then load_recognizer"""
        mock_request_id_var.get.return_value = "integration-uuid"
        
        # Initial state
        initial_entities = ["PERSON", "EMAIL"]
        mock_registry.get_supported_entities.return_value = initial_entities
        mock_ranha_recog.get_supported_entities.return_value = initial_entities + ["RANHA_ENTITY"]
        
        # Set recognizer
        json_data = [
            {
                "RecogName": "CUSTOM_DATA",
                "RecogType": "Data",
                "EntityValue": ["value1", "value2"],
                "Score": 0.9,
                "isPreDefined": "No"
            }
        ]
        
        json_bytes = json.dumps(json_data).encode('utf-8')
        mock_file = Mock()
        mock_file.file.read.return_value = json_bytes
        
        payload = {"file": mock_file}
        
        set_result = LoadRecognizer.set_recognizer(payload)
        
        assert "Available Recognizers" in set_result
        assert mock_registry.add_recognizer.called
        
        # Load recognizers
        load_result = LoadRecognizer.load_recognizer()
        
        assert "Available Recognizers" in load_result
        assert "RANHA_ENTITY*" in load_result["Available Recognizers"]
    
    @patch('privacy.service.loadRecognizer.registry')
    @patch('privacy.service.loadRecognizer.request_id_var')
    @patch('privacy.service.loadRecognizer.error_dict', {})
    @patch('privacy.service.loadRecognizer.ranha_recog')
    def test_mixed_recognizer_types(self, mock_ranha_recog, mock_request_id_var, mock_registry):
        """Test setting both Data and Pattern recognizers in one file"""
        mock_request_id_var.get.return_value = "mixed-uuid"
        mock_registry.get_supported_entities.return_value = []
        mock_ranha_recog.get_supported_entities.return_value = ["RANHA"]
        
        json_data = [
            {
                "RecogName": "DATA_RECOG",
                "RecogType": "Data",
                "EntityValue": ["data1", "data2"],
                "Score": 0.85,
                "isPreDefined": "No"
            },
            {
                "RecogName": "PATTERN_RECOG",
                "RecogType": "Pattern",
                "EntityValue": "\\d{5}",
                "Score": 0.90,
                "Context": "zip,postal",
                "isPreDefined": "No"
            },
            {
                "RecogName": "ANOTHER_DATA",
                "RecogType": "Data",
                "EntityValue": ["data3"],
                "Score": 0.88,
                "isPreDefined": "No"
            }
        ]
        
        json_bytes = json.dumps(json_data).encode('utf-8')
        mock_file = Mock()
        mock_file.file.read.return_value = json_bytes
        
        payload = {"file": mock_file}
        
        result = LoadRecognizer.set_recognizer(payload)
        
        # Should add all 3 recognizers
        assert mock_registry.add_recognizer.call_count == 3
        assert "Available Recognizers" in result
