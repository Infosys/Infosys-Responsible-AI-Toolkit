"""
Unit tests for privacy.service.csv_service module.
Tests cover CSV anonymization functionality with various configurations.
"""
import pytest
import pandas as pd
import io
import tempfile
from unittest.mock import Mock, MagicMock, patch, mock_open
from privacy.service.csv_service import CSVService
from privacy.service.imagePrivacy import AttributeDict
from presidio_analyzer import RecognizerResult


@pytest.fixture
def sample_csv_data():
    """Create a sample CSV file for testing."""
    csv_content = """name,email,phone,address
John Doe,john@example.com,123-456-7890,123 Main St
Jane Smith,jane@example.com,098-765-4321,456 Oak Ave"""
    return io.StringIO(csv_content)


@pytest.fixture
def sample_csv_file(sample_csv_data):
    """Create a mock file object with CSV data."""
    mock_file = Mock()
    mock_file.file = sample_csv_data
    mock_file.filename = "test.csv"
    return mock_file


@pytest.fixture
def basic_payload(sample_csv_file):
    """Create a basic payload for CSV anonymization."""
    return {
        "file": sample_csv_file,
        "keys_to_skip": [],
        "piiEntitiesToBeRedacted": None,
        "portfolio": None,
        "account": None,
        "nlp": "basic",
        "exclusion": None
    }


@pytest.fixture
def payload_with_entities(sample_csv_file):
    """Create payload with specific entities to redact."""
    return {
        "file": sample_csv_file,
        "keys_to_skip": ["address"],
        "piiEntitiesToBeRedacted": "PERSON,EMAIL_ADDRESS,PHONE_NUMBER",
        "portfolio": None,
        "account": None,
        "nlp": "basic",
        "exclusion": "Main"
    }


@pytest.fixture
def payload_with_portfolio(sample_csv_file):
    """Create payload with portfolio and account."""
    return {
        "file": sample_csv_file,
        "keys_to_skip": [],
        "piiEntitiesToBeRedacted": None,
        "portfolio": "test_portfolio",
        "account": "test_account",
        "nlp": "basic",
        "exclusion": None
    }


@pytest.fixture
def payload_with_roberta_nlp(sample_csv_file):
    """Create payload with roberta NLP."""
    return {
        "file": sample_csv_file,
        "keys_to_skip": [],
        "piiEntitiesToBeRedacted": None,
        "portfolio": None,
        "account": None,
        "nlp": "roberta",
        "exclusion": None
    }


@pytest.fixture
def payload_with_ranha_nlp(sample_csv_file):
    """Create payload with ranha NLP."""
    return {
        "file": sample_csv_file,
        "keys_to_skip": [],
        "piiEntitiesToBeRedacted": None,
        "portfolio": None,
        "account": None,
        "nlp": "ranha",
        "exclusion": None
    }


class TestCSVServiceBasic:
    """Test basic CSV anonymization functionality."""

    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    @patch('privacy.service.csv_service.AnalyzerEngine')
    @patch('privacy.service.csv_service.tempfile.NamedTemporaryFile')
    def test_csv_anonymize_basic_success(
        self, 
        mock_tempfile, 
        mock_analyzer_engine, 
        mock_batch_analyzer, 
        mock_batch_anonymizer, 
        basic_payload
    ):
        """Test successful CSV anonymization with basic configuration."""
        # Setup mocks
        mock_analyzer_instance = MagicMock()
        mock_analyzer_engine.return_value = mock_analyzer_instance
        
        mock_batch_analyzer_instance = MagicMock()
        mock_batch_analyzer.return_value = mock_batch_analyzer_instance
        
        # Mock analyzer results
        mock_analyzer_results = [
            {
                "name": [RecognizerResult(entity_type="PERSON", start=0, end=8, score=0.9)],
                "email": [RecognizerResult(entity_type="EMAIL_ADDRESS", start=0, end=17, score=0.95)]
            }
        ]
        mock_batch_analyzer_instance.analyze_dict.return_value = mock_analyzer_results
        
        # Mock anonymizer results
        mock_anonymized_data = {
            "name": ["<PERSON>", "<PERSON>"],
            "email": ["<EMAIL_ADDRESS>", "<EMAIL_ADDRESS>"],
            "phone": ["123-456-7890", "098-765-4321"],
            "address": ["123 Main St", "456 Oak Ave"]
        }
        mock_batch_anonymizer_instance = MagicMock()
        mock_batch_anonymizer.return_value = mock_batch_anonymizer_instance
        mock_batch_anonymizer_instance.anonymize_dict.return_value = mock_anonymized_data
        
        # Mock tempfile
        mock_temp = MagicMock()
        mock_temp.name = "/tmp/test.csv"
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        
        # Execute
        result = CSVService.csv_anonymize(basic_payload)
        
        # Verify
        assert result is not None
        assert isinstance(result, io.StringIO)
        mock_batch_analyzer_instance.analyze_dict.assert_called_once()
        mock_batch_anonymizer_instance.anonymize_dict.assert_called_once()

    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    @patch('privacy.service.csv_service.AnalyzerEngine')
    @patch('privacy.service.csv_service.tempfile.NamedTemporaryFile')
    def test_csv_anonymize_with_keys_to_skip(
        self, 
        mock_tempfile, 
        mock_analyzer_engine, 
        mock_batch_analyzer, 
        mock_batch_anonymizer, 
        payload_with_entities
    ):
        """Test CSV anonymization with keys to skip."""
        # Setup mocks
        mock_analyzer_instance = MagicMock()
        mock_analyzer_engine.return_value = mock_analyzer_instance
        
        mock_batch_analyzer_instance = MagicMock()
        mock_batch_analyzer.return_value = mock_batch_analyzer_instance
        mock_analyzer_results = [{"name": [], "email": []}]
        mock_batch_analyzer_instance.analyze_dict.return_value = mock_analyzer_results
        
        mock_anonymized_data = {
            "name": ["<PERSON>", "<PERSON>"],
            "email": ["<EMAIL_ADDRESS>", "<EMAIL_ADDRESS>"],
            "phone": ["<PHONE_NUMBER>", "<PHONE_NUMBER>"],
            "address": ["123 Main St", "456 Oak Ave"]
        }
        mock_batch_anonymizer_instance = MagicMock()
        mock_batch_anonymizer.return_value = mock_batch_anonymizer_instance
        mock_batch_anonymizer_instance.anonymize_dict.return_value = mock_anonymized_data
        
        mock_temp = MagicMock()
        mock_temp.name = "/tmp/test.csv"
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        
        # Execute
        result = CSVService.csv_anonymize(payload_with_entities)
        
        # Verify
        assert result is not None
        call_args = mock_batch_analyzer_instance.analyze_dict.call_args
        assert call_args[1]["keys_to_skip"] == ["address"]
        assert call_args[1]["allow_list"] == ["Main"]
        assert "PERSON" in call_args[1]["entities"]

    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    @patch('privacy.service.csv_service.AnalyzerEngine')
    @patch('privacy.service.csv_service.tempfile.NamedTemporaryFile')
    def test_csv_anonymize_with_exclusion_list(
        self, 
        mock_tempfile, 
        mock_analyzer_engine, 
        mock_batch_analyzer, 
        mock_batch_anonymizer
    ):
        """Test CSV anonymization with exclusion list."""
        csv_content = io.StringIO("name\nJohn Doe\nJane Smith")
        mock_file = Mock()
        mock_file.file = csv_content
        
        payload = {
            "file": mock_file,
            "keys_to_skip": [],
            "piiEntitiesToBeRedacted": None,
            "portfolio": None,
            "account": None,
            "nlp": "basic",
            "exclusion": "John,Jane"
        }
        
        # Setup mocks
        mock_analyzer_instance = MagicMock()
        mock_analyzer_engine.return_value = mock_analyzer_instance
        
        mock_batch_analyzer_instance = MagicMock()
        mock_batch_analyzer.return_value = mock_batch_analyzer_instance
        mock_batch_analyzer_instance.analyze_dict.return_value = [{"name": []}]
        
        mock_batch_anonymizer_instance = MagicMock()
        mock_batch_anonymizer.return_value = mock_batch_anonymizer_instance
        mock_batch_anonymizer_instance.anonymize_dict.return_value = {"name": ["John Doe", "Jane Smith"]}
        
        mock_temp = MagicMock()
        mock_temp.name = "/tmp/test.csv"
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        
        # Execute
        result = CSVService.csv_anonymize(payload)
        
        # Verify
        assert result is not None
        call_args = mock_batch_analyzer_instance.analyze_dict.call_args
        assert call_args[1]["allow_list"] == ["John", "Jane"]


class TestCSVServiceWithNLP:
    """Test CSV anonymization with different NLP engines."""

    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    @patch('privacy.service.csv_service.AnalyzerEngine')
    @patch('privacy.service.csv_service.tempfile.NamedTemporaryFile')
    @patch('privacy.service.csv_service.roberta_recog')
    def test_csv_anonymize_with_roberta_nlp(
        self, 
        mock_roberta_recog,
        mock_tempfile, 
        mock_analyzer_engine, 
        mock_batch_analyzer, 
        mock_batch_anonymizer, 
        payload_with_roberta_nlp
    ):
        """Test CSV anonymization with roberta NLP engine."""
        # Setup mocks
        mock_analyzer_instance = MagicMock()
        mock_analyzer_engine.return_value = mock_analyzer_instance
        
        mock_batch_analyzer_instance = MagicMock()
        mock_batch_analyzer.return_value = mock_batch_analyzer_instance
        mock_batch_analyzer_instance.analyze_dict.return_value = [{"name": []}]
        
        mock_batch_anonymizer_instance = MagicMock()
        mock_batch_anonymizer.return_value = mock_batch_anonymizer_instance
        mock_batch_anonymizer_instance.anonymize_dict.return_value = {"name": ["<PERSON>"]}
        
        mock_temp = MagicMock()
        mock_temp.name = "/tmp/test.csv"
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        
        # Execute
        result = CSVService.csv_anonymize(payload_with_roberta_nlp)
        
        # Verify
        assert result is not None
        call_args = mock_batch_analyzer_instance.analyze_dict.call_args
        assert call_args[1]["ad_hoc_recognizers"] is not None

    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    @patch('privacy.service.csv_service.AnalyzerEngine')
    @patch('privacy.service.csv_service.tempfile.NamedTemporaryFile')
    @patch('privacy.service.csv_service.roberta_recog')
    @patch('privacy.service.csv_service.ranha_recog')
    @patch('privacy.service.csv_service.registry')
    def test_csv_anonymize_with_ranha_nlp_no_entities(
        self, 
        mock_registry,
        mock_ranha_recog,
        mock_roberta_recog,
        mock_tempfile, 
        mock_analyzer_engine, 
        mock_batch_analyzer, 
        mock_batch_anonymizer, 
        payload_with_ranha_nlp
    ):
        """Test CSV anonymization with ranha NLP engine without predefined entities."""
        # Setup mocks
        mock_ranha_recog.supported_entities = ["PERSON", "EMAIL"]
        mock_registry.get_supported_entities.return_value = ["PHONE_NUMBER", "ADDRESS"]
        
        mock_analyzer_instance = MagicMock()
        mock_analyzer_engine.return_value = mock_analyzer_instance
        
        mock_batch_analyzer_instance = MagicMock()
        mock_batch_analyzer.return_value = mock_batch_analyzer_instance
        mock_batch_analyzer_instance.analyze_dict.return_value = [{"name": []}]
        
        mock_batch_anonymizer_instance = MagicMock()
        mock_batch_anonymizer.return_value = mock_batch_anonymizer_instance
        mock_batch_anonymizer_instance.anonymize_dict.return_value = {"name": ["<PERSON>"]}
        
        mock_temp = MagicMock()
        mock_temp.name = "/tmp/test.csv"
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        
        # Execute
        result = CSVService.csv_anonymize(payload_with_ranha_nlp)
        
        # Verify
        assert result is not None

    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    @patch('privacy.service.csv_service.AnalyzerEngine')
    @patch('privacy.service.csv_service.tempfile.NamedTemporaryFile')
    @patch('privacy.service.csv_service.ranha_recog')
    def test_csv_anonymize_with_ranha_nlp_with_entities(
        self, 
        mock_ranha_recog,
        mock_tempfile, 
        mock_analyzer_engine, 
        mock_batch_analyzer, 
        mock_batch_anonymizer
    ):
        """Test CSV anonymization with ranha NLP and specific entities."""
        csv_content = io.StringIO("name\nJohn Doe")
        mock_file = Mock()
        mock_file.file = csv_content
        
        payload = {
            "file": mock_file,
            "keys_to_skip": [],
            "piiEntitiesToBeRedacted": "PERSON,EMAIL",
            "portfolio": None,
            "account": None,
            "nlp": "ranha",
            "exclusion": None
        }
        
        # Setup mocks
        mock_analyzer_instance = MagicMock()
        mock_analyzer_engine.return_value = mock_analyzer_instance
        
        mock_batch_analyzer_instance = MagicMock()
        mock_batch_analyzer.return_value = mock_batch_analyzer_instance
        mock_batch_analyzer_instance.analyze_dict.return_value = [{"name": []}]
        
        mock_batch_anonymizer_instance = MagicMock()
        mock_batch_anonymizer.return_value = mock_batch_anonymizer_instance
        mock_batch_anonymizer_instance.anonymize_dict.return_value = {"name": ["<PERSON>"]}
        
        mock_temp = MagicMock()
        mock_temp.name = "/tmp/test.csv"
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        
        # Execute
        result = CSVService.csv_anonymize(payload)
        
        # Verify
        assert result is not None


class TestCSVServiceWithPortfolio:
    """Test CSV anonymization with portfolio/account configuration."""

    @patch('privacy.service.csv_service.ApiCall')
    def test_csv_anonymize_with_portfolio_no_response(
        self, 
        mock_api_call, 
        payload_with_portfolio
    ):
        """Test CSV anonymization when portfolio API returns None."""
        # Setup mock
        mock_api_call.request.return_value = None
        
        # Execute
        result = CSVService.csv_anonymize(payload_with_portfolio)
        
        # Verify
        assert result is None
        assert mock_api_call.request.call_count == 1

    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    @patch('privacy.service.csv_service.AnalyzerEngine')
    @patch('privacy.service.csv_service.tempfile.NamedTemporaryFile')
    @patch('privacy.service.csv_service.ApiCall')
    @patch('privacy.service.csv_service.DataListRecognizer')
    @patch('privacy.service.csv_service.registry')
    @patch('privacy.service.csv_service.update_session_dict')
    @patch('privacy.service.csv_service.admin_par', {'test-request-id': {'scoreTreshold': 0.5}})
    def test_csv_anonymize_with_portfolio_data_recognizer(
        self, 
        mock_update_session,
        mock_registry,
        mock_data_recognizer,
        mock_api_call, 
        mock_tempfile, 
        mock_analyzer_engine, 
        mock_batch_analyzer, 
        mock_batch_anonymizer, 
        payload_with_portfolio
    ):
        """Test CSV anonymization with portfolio and data recognizer."""
        # Setup mocks
        mock_api_call.request.side_effect = [
            True,  # First call in payload check
            (["CUSTOM_ENTITY"], [["value1", "value2"]], ["PERSON"])  # Second call for entity types
        ]
        
        mock_record = {
            "RecogType": "Data",
            "Score": 0.8
        }
        mock_api_call.getRecord.return_value = mock_record
        
        mock_analyzer_instance = MagicMock()
        mock_analyzer_engine.return_value = mock_analyzer_instance
        
        mock_batch_analyzer_instance = MagicMock()
        mock_batch_analyzer.return_value = mock_batch_analyzer_instance
        mock_batch_analyzer_instance.analyze_dict.return_value = [{"name": []}]
        
        mock_batch_anonymizer_instance = MagicMock()
        mock_batch_anonymizer.return_value = mock_batch_anonymizer_instance
        mock_batch_anonymizer_instance.anonymize_dict.return_value = {"name": ["<PERSON>"]}
        
        mock_temp = MagicMock()
        mock_temp.name = "/tmp/test.csv"
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        
        mock_data_recognizer_instance = MagicMock()
        mock_data_recognizer.return_value = mock_data_recognizer_instance
        
        # Mock request_id_var - create a mock object with get method
        mock_request_id_var = MagicMock()
        mock_request_id_var.get.return_value = 'test-request-id'
        
        with patch('privacy.service.csv_service.request_id_var', mock_request_id_var):
            # Execute
            result = CSVService.csv_anonymize(payload_with_portfolio)
        
        # Verify
        assert result is not None
        mock_registry.add_recognizer.assert_called()
        mock_update_session.assert_called()

    @patch('privacy.service.csv_service.ApiCall')
    def test_csv_anonymize_with_portfolio_404_response(
        self, 
        mock_api_call, 
        payload_with_portfolio
    ):
        """Test CSV anonymization when portfolio API returns 404."""
        # Setup mock
        mock_api_call.request.side_effect = [True, 404]
        
        # Execute
        result = CSVService.csv_anonymize(payload_with_portfolio)
        
        # Verify
        assert result == 404

    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    @patch('privacy.service.csv_service.AnalyzerEngine')
    @patch('privacy.service.csv_service.tempfile.NamedTemporaryFile')
    @patch('privacy.service.csv_service.ApiCall')
    @patch('privacy.service.csv_service.PatternRecognizer')
    @patch('privacy.service.csv_service.Pattern')
    @patch('privacy.service.csv_service.registry')
    @patch('privacy.service.csv_service.admin_par', {'test-request-id': {'scoreTreshold': 0.5}})
    def test_csv_anonymize_with_portfolio_pattern_recognizer(
        self, 
        mock_registry,
        mock_pattern,
        mock_pattern_recognizer,
        mock_api_call, 
        mock_tempfile, 
        mock_analyzer_engine, 
        mock_batch_analyzer, 
        mock_batch_anonymizer, 
        payload_with_portfolio
    ):
        """Test CSV anonymization with portfolio and pattern recognizer."""
        # Setup mocks
        mock_api_call.request.side_effect = [
            True,  # First call
            (["CUSTOM_PATTERN"], [["pattern1", "pattern2"]], ["PERSON"])  # Second call
        ]
        
        mock_record = {
            "RecogType": "Pattern",
            "isPreDefined": "No",
            "Context": "context1,context2",
            "Score": 0.9
        }
        mock_api_call.getRecord.return_value = mock_record
        
        mock_analyzer_instance = MagicMock()
        mock_analyzer_engine.return_value = mock_analyzer_instance
        
        mock_batch_analyzer_instance = MagicMock()
        mock_batch_analyzer.return_value = mock_batch_analyzer_instance
        mock_batch_analyzer_instance.analyze_dict.return_value = [{"name": []}]
        
        mock_batch_anonymizer_instance = MagicMock()
        mock_batch_anonymizer.return_value = mock_batch_anonymizer_instance
        mock_batch_anonymizer_instance.anonymize_dict.return_value = {"name": ["<PERSON>"]}
        
        mock_temp = MagicMock()
        mock_temp.name = "/tmp/test.csv"
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        
        mock_pattern_instance = MagicMock()
        mock_pattern.return_value = mock_pattern_instance
        
        mock_pattern_recognizer_instance = MagicMock()
        mock_pattern_recognizer.return_value = mock_pattern_recognizer_instance
        
        # Mock request_id_var - create a mock object with get method
        mock_request_id_var = MagicMock()
        mock_request_id_var.get.return_value = 'test-request-id'
        
        with patch('privacy.service.csv_service.request_id_var', mock_request_id_var):
            # Execute
            result = CSVService.csv_anonymize(payload_with_portfolio)
        
        # Verify
        assert result is not None
        mock_pattern.assert_called()
        mock_pattern_recognizer.assert_called()
        mock_registry.add_recognizer.assert_called()

    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    @patch('privacy.service.csv_service.AnalyzerEngine')
    @patch('privacy.service.csv_service.tempfile.NamedTemporaryFile')
    @patch('privacy.service.csv_service.ApiCall')
    @patch('privacy.service.csv_service.registry')
    @patch('privacy.service.csv_service.admin_par')
    @patch('privacy.service.csv_service.request_id_var')
    def test_csv_anonymize_with_portfolio_and_admin_params(
        self, 
        mock_request_id_var,
        mock_admin_par,
        mock_registry,
        mock_api_call, 
        mock_tempfile, 
        mock_analyzer_engine, 
        mock_batch_analyzer, 
        mock_batch_anonymizer, 
        payload_with_portfolio
    ):
        """Test CSV anonymization with portfolio using admin parameters."""
        # Setup mocks
        mock_request_id_var.get.return_value = "test_request_id"
        mock_admin_par.__getitem__.return_value = {"scoreTreshold": 0.7}
        
        mock_api_call.request.side_effect = [
            True,  # First call
            (["ENTITY1"], [["data1"]], ["PERSON"])  # Second call
        ]
        
        mock_record = {
            "RecogType": "Data",
            "Score": 0.8
        }
        mock_api_call.getRecord.return_value = mock_record
        
        mock_analyzer_instance = MagicMock()
        mock_analyzer_engine.return_value = mock_analyzer_instance
        
        mock_batch_analyzer_instance = MagicMock()
        mock_batch_analyzer.return_value = mock_batch_analyzer_instance
        mock_batch_analyzer_instance.analyze_dict.return_value = [{"name": []}]
        
        mock_batch_anonymizer_instance = MagicMock()
        mock_batch_anonymizer.return_value = mock_batch_anonymizer_instance
        mock_batch_anonymizer_instance.anonymize_dict.return_value = {"name": ["<PERSON>"]}
        
        mock_temp = MagicMock()
        mock_temp.name = "/tmp/test.csv"
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        
        # Execute
        result = CSVService.csv_anonymize(payload_with_portfolio)
        
        # Verify
        assert result is not None


class TestCSVServiceErrorHandling:
    """Test error handling in CSV service."""

    @patch('privacy.service.csv_service.AnalyzerEngine')
    def test_csv_anonymize_with_invalid_csv(
        self, 
        mock_analyzer_engine
    ):
        """Test CSV anonymization with invalid CSV data."""
        invalid_csv = io.StringIO("invalid,csv\ndata")
        mock_file = Mock()
        mock_file.file = invalid_csv
        
        payload = {
            "file": mock_file,
            "keys_to_skip": [],
            "piiEntitiesToBeRedacted": None,
            "portfolio": None,
            "account": None,
            "nlp": "basic",
            "exclusion": None
        }
        
        mock_analyzer_engine.side_effect = Exception("CSV parsing error")
        
        # Execute and verify
        with pytest.raises(Exception) as exc_info:
            CSVService.csv_anonymize(payload)
        
        assert "CSV parsing error" in str(exc_info.value)

    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    @patch('privacy.service.csv_service.AnalyzerEngine')
    def test_csv_anonymize_analyzer_exception(
        self, 
        mock_analyzer_engine, 
        mock_batch_analyzer, 
        basic_payload
    ):
        """Test CSV anonymization when analyzer raises exception."""
        # Setup mocks
        mock_analyzer_instance = MagicMock()
        mock_analyzer_engine.return_value = mock_analyzer_instance
        
        mock_batch_analyzer_instance = MagicMock()
        mock_batch_analyzer.return_value = mock_batch_analyzer_instance
        mock_batch_analyzer_instance.analyze_dict.side_effect = Exception("Analyzer error")
        
        # Execute and verify
        with pytest.raises(Exception) as exc_info:
            CSVService.csv_anonymize(basic_payload)
        
        assert "Analyzer error" in str(exc_info.value)

    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    @patch('privacy.service.csv_service.AnalyzerEngine')
    def test_csv_anonymize_with_entities_exception(
        self, 
        mock_analyzer_engine, 
        mock_batch_analyzer, 
        mock_batch_anonymizer, 
        payload_with_entities
    ):
        """Test CSV anonymization with entities that causes exception."""
        # Setup mocks
        mock_analyzer_instance = MagicMock()
        mock_analyzer_engine.return_value = mock_analyzer_instance
        
        mock_batch_analyzer_instance = MagicMock()
        mock_batch_analyzer.return_value = mock_batch_analyzer_instance
        mock_batch_analyzer_instance.analyze_dict.side_effect = Exception("Entity error")
        
        # Execute and verify
        with pytest.raises(Exception) as exc_info:
            CSVService.csv_anonymize(payload_with_entities)
        
        assert "Entity error" in str(exc_info.value)

    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    @patch('privacy.service.csv_service.AnalyzerEngine')
    def test_csv_anonymize_anonymizer_exception(
        self, 
        mock_analyzer_engine, 
        mock_batch_analyzer, 
        mock_batch_anonymizer, 
        basic_payload
    ):
        """Test CSV anonymization when anonymizer raises exception."""
        # Setup mocks
        mock_analyzer_instance = MagicMock()
        mock_analyzer_engine.return_value = mock_analyzer_instance
        
        mock_batch_analyzer_instance = MagicMock()
        mock_batch_analyzer.return_value = mock_batch_analyzer_instance
        mock_batch_analyzer_instance.analyze_dict.return_value = [{"name": []}]
        
        mock_batch_anonymizer_instance = MagicMock()
        mock_batch_anonymizer.return_value = mock_batch_anonymizer_instance
        mock_batch_anonymizer_instance.anonymize_dict.side_effect = Exception("Anonymizer error")
        
        # Execute and verify
        with pytest.raises(Exception) as exc_info:
            CSVService.csv_anonymize(basic_payload)
        
        assert "Anonymizer error" in str(exc_info.value)


class TestCSVServiceEdgeCases:
    """Test edge cases in CSV service."""

    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    @patch('privacy.service.csv_service.AnalyzerEngine')
    @patch('privacy.service.csv_service.tempfile.NamedTemporaryFile')
    def test_csv_anonymize_empty_csv(
        self, 
        mock_tempfile, 
        mock_analyzer_engine, 
        mock_batch_analyzer, 
        mock_batch_anonymizer
    ):
        """Test CSV anonymization with empty CSV file."""
        empty_csv = io.StringIO("column1,column2\n")
        mock_file = Mock()
        mock_file.file = empty_csv
        
        payload = {
            "file": mock_file,
            "keys_to_skip": [],
            "piiEntitiesToBeRedacted": None,
            "portfolio": None,
            "account": None,
            "nlp": "basic",
            "exclusion": None
        }
        
        # Setup mocks
        mock_analyzer_instance = MagicMock()
        mock_analyzer_engine.return_value = mock_analyzer_instance
        
        mock_batch_analyzer_instance = MagicMock()
        mock_batch_analyzer.return_value = mock_batch_analyzer_instance
        mock_batch_analyzer_instance.analyze_dict.return_value = [{}]
        
        mock_batch_anonymizer_instance = MagicMock()
        mock_batch_anonymizer.return_value = mock_batch_anonymizer_instance
        mock_batch_anonymizer_instance.anonymize_dict.return_value = {"column1": [], "column2": []}
        
        mock_temp = MagicMock()
        mock_temp.name = "/tmp/test.csv"
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        
        # Execute
        result = CSVService.csv_anonymize(payload)
        
        # Verify
        assert result is not None

    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    @patch('privacy.service.csv_service.AnalyzerEngine')
    @patch('privacy.service.csv_service.tempfile.NamedTemporaryFile')
    def test_csv_anonymize_with_special_characters(
        self, 
        mock_tempfile, 
        mock_analyzer_engine, 
        mock_batch_analyzer, 
        mock_batch_anonymizer
    ):
        """Test CSV anonymization with special characters in data."""
        special_csv = io.StringIO("name,data\nJohn Doe,test@#$%\nJane,äöü")
        mock_file = Mock()
        mock_file.file = special_csv
        
        payload = {
            "file": mock_file,
            "keys_to_skip": [],
            "piiEntitiesToBeRedacted": None,
            "portfolio": None,
            "account": None,
            "nlp": "basic",
            "exclusion": None
        }
        
        # Setup mocks
        mock_analyzer_instance = MagicMock()
        mock_analyzer_engine.return_value = mock_analyzer_instance
        
        mock_batch_analyzer_instance = MagicMock()
        mock_batch_analyzer.return_value = mock_batch_analyzer_instance
        mock_batch_analyzer_instance.analyze_dict.return_value = [{"name": [], "data": []}]
        
        mock_batch_anonymizer_instance = MagicMock()
        mock_batch_anonymizer.return_value = mock_batch_anonymizer_instance
        mock_batch_anonymizer_instance.anonymize_dict.return_value = {
            "name": ["<PERSON>", "<PERSON>"],
            "data": ["test@#$%", "äöü"]
        }
        
        mock_temp = MagicMock()
        mock_temp.name = "/tmp/test.csv"
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        
        # Execute
        result = CSVService.csv_anonymize(payload)
        
        # Verify
        assert result is not None

    @patch('privacy.service.csv_service.ApiCall')
    def test_csv_anonymize_portfolio_none_at_initial_check(self, mock_api_call):
        """Test when portfolio check returns None immediately."""
        csv_content = io.StringIO("name\nJohn")
        mock_file = Mock()
        mock_file.file = csv_content
        
        payload = {
            "file": mock_file,
            "keys_to_skip": [],
            "piiEntitiesToBeRedacted": None,
            "portfolio": "test",
            "account": "test",
            "nlp": "basic",
            "exclusion": None
        }
        
        # Setup mock to return None on first call
        mock_api_call.request.return_value = None
        
        # Execute
        result = CSVService.csv_anonymize(payload)
        
        # Verify
        assert result is None

    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    @patch('privacy.service.csv_service.AnalyzerEngine')
    @patch('privacy.service.csv_service.tempfile.NamedTemporaryFile')
    @patch('privacy.service.csv_service.ApiCall')
    def test_csv_anonymize_portfolio_second_call_none(
        self,
        mock_api_call,
        mock_tempfile,
        mock_analyzer_engine,
        mock_batch_analyzer,
        mock_batch_anonymizer
    ):
        """Test when portfolio second API call returns None."""
        csv_content = io.StringIO("name\nJohn")
        mock_file = Mock()
        mock_file.file = csv_content
        
        payload = {
            "file": mock_file,
            "keys_to_skip": [],
            "piiEntitiesToBeRedacted": None,
            "portfolio": "test",
            "account": "test",
            "nlp": "basic",
            "exclusion": None
        }
        
        # Setup mock - first call succeeds, second returns None
        mock_api_call.request.side_effect = [True, None]
        
        # Execute
        result = CSVService.csv_anonymize(payload)
        
        # Verify
        assert result is None

    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    @patch('privacy.service.csv_service.AnalyzerEngine')
    def test_csv_anonymize_with_entities_logs_error(
        self,
        mock_analyzer_engine,
        mock_batch_analyzer
    ):
        """Test CSV anonymization logs error when analyzer with entities fails (covers line 73)."""
        csv_content = io.StringIO("name\nJohn Doe")
        mock_file = Mock()
        mock_file.file = csv_content
        
        payload = {
            "file": mock_file,
            "keys_to_skip": [],
            "piiEntitiesToBeRedacted": "INVALID_ENTITY",  # Invalid entity to trigger exception
            "portfolio": None,
            "account": None,
            "nlp": "basic",
            "exclusion": None
        }
        
        # Setup mocks
        mock_analyzer_instance = MagicMock()
        mock_analyzer_engine.return_value = mock_analyzer_instance
        
        mock_batch_analyzer_instance = MagicMock()
        mock_batch_analyzer.return_value = mock_batch_analyzer_instance
        
        # Make analyze_dict raise an exception to trigger the error path
        test_exception = ValueError("Invalid entity type")
        mock_batch_analyzer_instance.analyze_dict.side_effect = test_exception
        
        # Execute and verify exception is raised
        with pytest.raises(ValueError) as exc_info:
            CSVService.csv_anonymize(payload)
        
        # Verify the exception matches
        assert "Invalid entity type" in str(exc_info.value)


class TestCSVServiceEdgeCases:
    """Test edge cases for missing coverage lines"""
    
    def test_csv_anonymize_with_ranha_nlp_and_none_entities(self):
        """Test csv_anonymize with nlp='ranha' when piiEntitiesToBeRedacted is None (line 47)"""
        csv_content = "name,email\nJohn Doe,john@test.com"
        csv_io = io.StringIO(csv_content)
        
        mock_file = Mock()
        mock_file.file = csv_io
        mock_file.filename = "test.csv"
        
        payload = {
            "file": mock_file,
            "keys_to_skip": [],
            "piiEntitiesToBeRedacted": None,  # This with accName=None triggers line 47
            "portfolio": None,
            "account": None,
            "nlp": "ranha",  # This triggers line 45-48
            "exclusion": None
        }
        
        with patch('privacy.service.csv_service.AnalyzerEngine') as mock_analyzer, \
             patch('privacy.service.csv_service.BatchAnalyzerEngine') as mock_batch_analyzer, \
             patch('privacy.service.csv_service.BatchAnonymizerEngine') as mock_batch_anon, \
             patch('privacy.service.csv_service.ranha_recog') as mock_ranha:
            
            mock_analyzer_instance = MagicMock()
            mock_analyzer.return_value = mock_analyzer_instance
            
            mock_batch_analyzer_instance = MagicMock()
            mock_batch_analyzer.return_value = mock_batch_analyzer_instance
            mock_batch_analyzer_instance.analyze_dict.return_value = []
            
            mock_batch_anon_instance = MagicMock()
            mock_batch_anon.return_value = mock_batch_anon_instance
            mock_batch_anon_instance.anonymize_dict.return_value = ({"name": ["<PERSON>"]}, {})
            
            mock_ranha.supported_entities = ["PERSON", "EMAIL"]
            
            result = CSVService.csv_anonymize(payload)
            
            assert result is not None

    def test_csv_anonymize_with_portfolio_api_returns_none(self):
        """Test csv_anonymize when ApiCall.request returns None (line 73)"""
        csv_content = "name,email\nJohn Doe,john@test.com"
        csv_io = io.StringIO(csv_content)
        
        mock_file = Mock()
        mock_file.file = csv_io
        mock_file.filename = "test.csv"
        
        payload = {
            "file": mock_file,
            "keys_to_skip": [],
            "piiEntitiesToBeRedacted": None,
            "portfolio": "test_portfolio",
            "account": "test_account",
            "nlp": "basic",
            "exclusion": None
        }
        
        with patch('privacy.service.csv_service.ApiCall.request') as mock_api_call:
            mock_api_call.return_value = None  # This triggers line 73
            
            result = CSVService.csv_anonymize(payload)
            
            assert result is None

    def test_csv_anonymize_with_portfolio_api_returns_404(self):
        """Test csv_anonymize when ApiCall.request returns 404 (line 86)"""
        csv_content = "name,email\nJohn Doe,john@test.com"
        csv_io = io.StringIO(csv_content)
        
        mock_file = Mock()
        mock_file.file = csv_io
        mock_file.filename = "test.csv"
        
        payload = {
            "file": mock_file,
            "keys_to_skip": [],
            "piiEntitiesToBeRedacted": None,
            "portfolio": "test_portfolio",
            "account": "test_account",
            "nlp": "basic",
            "exclusion": None
        }
        
        with patch('privacy.service.csv_service.ApiCall.request') as mock_api_call:
            mock_api_call.return_value = 404  # This triggers line 86
            
            result = CSVService.csv_anonymize(payload)
            
            assert result == 404
    
    def test_csv_anonymize_with_entities_raises_exception(self):
        """Test csv_anonymize when analyze_dict raises exception (line 73-75)"""
        csv_content = "name,email\nJohn Doe,john@test.com"
        csv_io = io.StringIO(csv_content)
        
        mock_file = Mock()
        mock_file.file = csv_io
        mock_file.filename = "test.csv"
        
        payload = {
            "file": mock_file,
            "keys_to_skip": [],
            "piiEntitiesToBeRedacted": "PERSON,EMAIL",  # String format (gets split)
            "portfolio": None,
            "account": None,
            "nlp": "basic",
            "exclusion": None
        }
        
        with patch('privacy.service.csv_service.AnalyzerEngine') as mock_analyzer, \
             patch('privacy.service.csv_service.BatchAnalyzerEngine') as mock_batch_analyzer, \
             patch('privacy.service.csv_service.BatchAnonymizerEngine'):
            
            mock_analyzer_instance = MagicMock()
            mock_analyzer.return_value = mock_analyzer_instance
            
            mock_batch_analyzer_instance = MagicMock()
            mock_batch_analyzer.return_value = mock_batch_analyzer_instance
            
            # Make analyze_dict raise an exception to hit line 73-75
            test_exception = ValueError("Test exception for coverage")
            mock_batch_analyzer_instance.analyze_dict.side_effect = test_exception
            
            with pytest.raises(ValueError) as exc_info:
                CSVService.csv_anonymize(payload)
            
            assert "Test exception for coverage" in str(exc_info.value)
    
    def test_csv_anonymize_with_ranha_trigger_line_47_exact(self):
        """Test to trigger exact conditions for line 47: nlp='ranha' with both None values"""
        csv_content = "name,email\nTest User,test@example.com"
        csv_io = io.StringIO(csv_content)
        
        mock_file = Mock()
        mock_file.file = csv_io
        mock_file.filename = "coverage_test.csv"
        
        # Critical: Both piiEntitiesToBeRedacted AND account must be None
        payload = AttributeDict({
            "file": mock_file,
            "keys_to_skip": [],
            "piiEntitiesToBeRedacted": None,  # Must be None
            "portfolio": None,
            "account": None,  # accName is derived from this - must be None
            "nlp": "ranha",  # Must be 'ranha'
            "exclusion": None
        })
        
        with patch('privacy.service.csv_service.AnalyzerEngine') as mock_analyzer, \
             patch('privacy.service.csv_service.BatchAnalyzerEngine') as mock_batch_analyzer, \
             patch('privacy.service.csv_service.BatchAnonymizerEngine') as mock_batch_anon, \
             patch('privacy.service.csv_service.ranha_recog') as mock_ranha, \
             patch('privacy.service.csv_service.RecognizerRegistry') as mock_registry_class:
            
            # Setup mocks
            mock_ranha.supported_entities = ["PERSON", "EMAIL"]
            
            mock_registry_instance = MagicMock()
            mock_registry_instance.get_supported_entities.return_value = ["PHONE_NUMBER"]
            mock_registry_class.return_value = mock_registry_instance
            
            mock_analyzer_instance = MagicMock()
            mock_analyzer.return_value = mock_analyzer_instance
            
            mock_batch_analyzer_instance = MagicMock()
            mock_batch_analyzer.return_value = mock_batch_analyzer_instance
            mock_batch_analyzer_instance.analyze_dict.return_value = []
            
            mock_batch_anon_instance = MagicMock()
            mock_batch_anon.return_value = mock_batch_anon_instance
            mock_batch_anon_instance.anonymize_dict.return_value = ({"name": ["Test"]}, {})
            
            # Execute - this should trigger line 47
            result = CSVService.csv_anonymize(payload)
            
            # Verify it executed
            assert result is not None


class TestCSVServiceMissingLineCoverage:
    """Test cases to cover remaining missing lines: 73, 86"""
    
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    @patch('privacy.service.csv_service.AnalyzerEngine')
    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    @patch('privacy.service.csv_service.pd.read_csv')
    @patch('privacy.service.csv_service.request_id_var')
    @patch('privacy.service.csv_service.error_dict', {})
    def test_csv_anonymize_without_account_and_without_entities_line_73(
        self, mock_request_id, mock_read_csv, mock_batch_anon, mock_analyzer, mock_batch_analyzer
    ):
        """Test csv_anonymize when accName is None and piiEntitiesToBeRedacted is None - covers line 73"""
        mock_request_id.get.return_value = 'test-csv-line73'
        
        # Mock read_csv
        mock_df = pd.DataFrame({'name': ['John'], 'email': ['test@test.com']})
        mock_read_csv.return_value = mock_df
        
        # Mock file
        mock_file = MagicMock()
        mock_file.file = io.BytesIO(b'name,email\nJohn,test@test.com')
        mock_file.filename = 'test.csv'
        
        # Mock analyzers and anonymizer
        mock_analyzer_instance = MagicMock()
        mock_analyzer.return_value = mock_analyzer_instance
        
        mock_batch_analyzer_instance = MagicMock()
        mock_batch_analyzer.return_value = mock_batch_analyzer_instance
        mock_batch_analyzer_instance.analyze_dict.return_value = []
        
        mock_batch_anon_instance = MagicMock()
        mock_batch_anon.return_value = mock_batch_anon_instance
        mock_batch_anon_instance.anonymize_dict.return_value = ({'name': ['John']}, {})
        
        # Payload without account and without entities (triggers line 73)
        payload = {
            'file': mock_file,
            'keys_to_skip': [],
            'piiEntitiesToBeRedacted': None,  # None triggers line 73
            'portfolio': None,
            'account': None,  # None means accName is None
            'nlp': 'basic',
            'exclusion': None
        }
        
        result = CSVService.csv_anonymize(payload)
        
        # Verify the line 73 path was executed (analyze_dict without entities parameter)
        assert mock_batch_analyzer_instance.analyze_dict.called
        assert result is not None
    
    @patch('privacy.service.csv_service.ApiCall.request')
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    @patch('privacy.service.csv_service.AnalyzerEngine')
    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    @patch('privacy.service.csv_service.pd.read_csv')
    @patch('privacy.service.csv_service.request_id_var')
    @patch('privacy.service.csv_service.error_dict', {})
    def test_csv_anonymize_with_account_returns_404_line_86(
        self, mock_request_id, mock_read_csv, mock_batch_anon, mock_analyzer, 
        mock_batch_analyzer, mock_api_call
    ):
        """Test csv_anonymize when API returns 404 - covers line 86"""
        mock_request_id.get.return_value = 'test-csv-line86'
        
        # Mock API to return 404
        mock_api_call.return_value = 404  # This triggers line 86
        
        # Mock read_csv
        mock_df = pd.DataFrame({'name': ['John'], 'email': ['test@test.com']})
        mock_read_csv.return_value = mock_df
        
        # Mock file
        mock_file = MagicMock()
        mock_file.file = io.BytesIO(b'name,email\nJohn,test@test.com')
        mock_file.filename = 'test.csv'
        
        # Payload with account (triggers API call which returns 404)
        payload = {
            'file': mock_file,
            'keys_to_skip': [],
            'piiEntitiesToBeRedacted': None,
            'portfolio': 'TestPortfolio',
            'account': 'TestAccount',  # This triggers API call
            'nlp': 'basic',
            'exclusion': None
        }
        
        result = CSVService.csv_anonymize(payload)
        
        # Should return 404 when API returns 404
        assert result == 404


class TestCSVServiceMissingLinesCoverage:
    """Additional tests to cover missing lines 47, 73, 86"""
    
    @patch('privacy.service.csv_service.AnalyzerEngine')
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    def test_csv_anonymize_with_ranha_none_entities_none_account(
        self, mock_batch_anon, mock_batch_analyzer, mock_analyzer):
        """Test CSV anonymization with ranha NLP, None entities, None account (covers line 47)"""
        
        # Setup mocks
        mock_analyzer_instance = Mock()
        mock_analyzer.return_value = mock_analyzer_instance
        mock_batch_analyzer_instance = Mock()
        mock_batch_analyzer_instance.analyze_dict.return_value = []
        mock_batch_analyzer.return_value = mock_batch_analyzer_instance
        mock_batch_anon_instance = Mock()
        mock_batch_anon_instance.anonymize_dict.return_value = {}
        mock_batch_anon.return_value = mock_batch_anon_instance
        
        # Create test CSV
        csv_content = "name,email\nJohn,john@example.com"
        mock_file = Mock()
        mock_file.file = io.StringIO(csv_content)
        
        payload = {
            'file': mock_file,
            'keys_to_skip': [],
            'piiEntitiesToBeRedacted': None,  # None entities
            'portfolio': None,
            'account': None,  # None account
            'nlp': 'ranha',  # ranha NLP
            'exclusion': None
        }
        
        result = CSVService.csv_anonymize(payload)
        
        # Verify the analyze_dict was called (line 73 path with None entities)
        assert mock_batch_analyzer_instance.analyze_dict.called
        assert isinstance(result, (io.BytesIO, io.StringIO))
    
    @patch('privacy.service.csv_service.ApiCall')
    @patch('privacy.service.csv_service.AnalyzerEngine')
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    def test_csv_anonymize_with_account_api_returns_none(
        self, mock_batch_anon, mock_batch_analyzer, mock_analyzer, mock_api_call):
        """Test CSV anonymization when API returns None (covers line 86)"""
        
        # Setup mocks
        mock_analyzer_instance = Mock()
        mock_analyzer.return_value = mock_analyzer_instance
        mock_batch_analyzer_instance = Mock()
        mock_batch_analyzer.return_value = mock_batch_analyzer_instance
        mock_batch_anon_instance = Mock()
        mock_batch_anon.return_value = mock_batch_anon_instance
        
        # Mock API to return None (line 86 check)
        mock_api_call.request.return_value = None
        
        # Create test CSV
        csv_content = "name,email\nJohn,john@example.com"
        mock_file = Mock()
        mock_file.file = io.StringIO(csv_content)
        
        accName = AttributeDict({"portfolio": "test", "account": "test_account"})
        
        payload = {
            'file': mock_file,
            'keys_to_skip': [],
            'piiEntitiesToBeRedacted': None,
            'portfolio': accName.portfolio,
            'account': accName.account,
            'nlp': 'basic',
            'exclusion': None
        }
        
        result = CSVService.csv_anonymize(payload)
        
        # Should return None when API returns None (line 86)
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=privacy.service.csv_service", "--cov-report=term"])
