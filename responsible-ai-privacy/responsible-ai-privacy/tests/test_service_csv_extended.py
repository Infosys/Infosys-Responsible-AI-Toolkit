"""Extended tests for CSV service to increase coverage"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import io


class TestCSVServiceExtended:
    """Extended test suite for CSVService coverage."""
    
    @patch('privacy.service.csv_service.ApiCall')
    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    def test_csv_anonymize_with_exception_handling(self, mock_batch_analyzer, mock_batch_anonymizer, mock_api_call):
        """Test CSV anonymize with exception handling path."""
        from privacy.service.csv_service import CSVService, AttributeDict
        
        # Setup mock file
        mock_file = Mock()
        csv_content = "name,email\nJohn Doe,john@example.com\nJane Smith,jane@example.com"
        mock_file.file = io.StringIO(csv_content)
        
        payload = {
            "file": mock_file,
            "keys_to_skip": [],
            "pii_entities_to_be_redacted": "PERSON,EMAIL_ADDRESS",
            "portfolio": None,
            "account": None,
            "nlp": None,
            "exclusion": None,
            "score_threshold": 0.5,
            "fakeData": False
        }
        
        # Mock analyzer to raise exception
        mock_analyzer_instance = Mock()
        mock_batch_analyzer.return_value = mock_analyzer_instance
        mock_analyzer_instance.analyze_dict.side_effect = Exception("Test exception")
        
        # Mock anonymizer
        mock_anonymizer_instance = Mock()
        mock_batch_anonymizer.return_value = mock_anonymizer_instance
        
        # Execute and expect exception
        with pytest.raises(Exception):
            CSVService.csv_anonymize(payload)
    
    @patch('privacy.service.csv_service.ApiCall')
    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    @patch('privacy.service.csv_service.FakeDataCSVGenerate')
    def test_csv_anonymize_with_fake_data_generation(self, mock_fake_data, mock_batch_analyzer, mock_batch_anonymizer, mock_api_call):
        """Test CSV anonymize with fake data generation enabled."""
        from privacy.service.csv_service import CSVService, AttributeDict
        
        # Setup mock file
        mock_file = Mock()
        csv_content = "name,email\nJohn Doe,john@example.com"
        mock_file.file = io.StringIO(csv_content)
        
        payload = {
            "file": mock_file,
            "keys_to_skip": [],
            "pii_entities_to_be_redacted": None,
            "portfolio": None,
            "account": None,
            "nlp": None,
            "exclusion": None,
            "score_threshold": None,
            "fakeData": True
        }
        
        # Mock analyzer
        mock_analyzer_instance = Mock()
        mock_batch_analyzer.return_value = mock_analyzer_instance
        mock_analyzer_instance.analyze_dict.return_value = [{"key": "name", "value": "John Doe"}]
        
        # Mock fake data generator
        mock_fake_data.fakeDataGeneration.return_value = ({"name": "REPLACE"}, [{"key": "name", "value": "Fake Name"}])
        
        # Mock anonymizer
        mock_anonymizer_instance = Mock()
        mock_batch_anonymizer.return_value = mock_anonymizer_instance
        mock_anonymizer_instance.anonymize_dict.return_value = {"name": ["Fake Name"], "email": ["fake@test.com"]}
        
        # Execute
        result = CSVService.csv_anonymize(payload)
        
        # Verify fake data generation was called
        assert mock_fake_data.fakeDataGeneration.called
        assert result is not None
    
    @patch('privacy.service.csv_service.ApiCall')
    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    def test_csv_anonymize_with_exclusion_list(self, mock_batch_analyzer, mock_batch_anonymizer, mock_api_call):
        """Test CSV anonymize with exclusion list."""
        from privacy.service.csv_service import CSVService
        
        # Setup mock file
        mock_file = Mock()
        csv_content = "text\nSome sample text"
        mock_file.file = io.StringIO(csv_content)
        
        payload = {
            "file": mock_file,
            "keys_to_skip": [],
            "pii_entities_to_be_redacted": None,
            "portfolio": None,
            "account": None,
            "nlp": None,
            "exclusion": "test1,test2",
            "score_threshold": 0.7,
            "fakeData": False
        }
        
        # Mock analyzer
        mock_analyzer_instance = Mock()
        mock_batch_analyzer.return_value = mock_analyzer_instance
        mock_analyzer_instance.analyze_dict.return_value = []
        
        # Mock anonymizer
        mock_anonymizer_instance = Mock()
        mock_batch_anonymizer.return_value = mock_anonymizer_instance
        mock_anonymizer_instance.anonymize_dict.return_value = {"text": ["Anonymized text"]}
        
        # Execute
        result = CSVService.csv_anonymize(payload)
        
        # Verify exclusion list was parsed
        call_args = mock_analyzer_instance.analyze_dict.call_args
        assert 'allow_list' in call_args.kwargs
        assert call_args.kwargs['allow_list'] == ['test1', 'test2']
    
    @patch('privacy.service.csv_service.ApiCall')
    @patch('privacy.service.csv_service.BatchAnonymizerEngine')
    @patch('privacy.service.csv_service.BatchAnalyzerEngine')
    def test_csv_anonymize_api_returns_404(self, mock_batch_analyzer, mock_batch_anonymizer, mock_api_call):
        """Test CSV anonymize when API returns 404."""
        from privacy.service.csv_service import CSVService, AttributeDict
        
        # Setup mock file
        mock_file = Mock()
        csv_content = "name,value\ntest,123"
        mock_file.file = io.StringIO(csv_content)
        
        payload = {
            "file": mock_file,
            "keys_to_skip": [],
            "pii_entities_to_be_redacted": None,
            "portfolio": "test_portfolio",
            "account": "test_account",
            "nlp": None,
            "exclusion": None,
            "score_threshold": None,
            "fakeData": False
        }
        
        # Mock API to return 404
        mock_api_call.request.return_value = 404
        
        # Execute
        result = CSVService.csv_anonymize(payload)
        
        # Verify 404 is returned
        assert result == 404
