"""
Tests for regexdetection module.

This module tests the code_detect class which performs PII detection and redaction in code.
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open, call
import json

# Import the class to test
from privacy.util.code_detect.regexdetection import code_detect


class TestCodeDetectRegex:
    """Test code_detect_regex method."""
    
    def test_code_detect_regex_with_pii(self):
        """Test code detection with PII present in code."""
        detector = code_detect()
        input_code = "email = 'user@example.com'"
        
        # Mock scan_pii_batch to return PII detection results
        mock_pii_results = {
            'has_secrets': [True],
            'number_secrets': [1],
            'secrets': [[{
                'tag': 'EMAIL',
                'value': 'user@example.com',
                'start': 9,
                'end': 26
            }]]
        }
        
        # Mock redact_pii_batch to return redacted code
        mock_redacted_results = {
            'new_content': ["email = 'REDACTED_EMAIL'"]
        }
        
        mock_replacements = {'EMAIL': ['REDACTED_EMAIL']}
        
        with patch('privacy.util.code_detect.regexdetection.scan_pii_batch', return_value=mock_pii_results):
            with patch('privacy.util.code_detect.regexdetection.redact_pii_batch', return_value=mock_redacted_results):
                with patch('builtins.open', mock_open(read_data=json.dumps(mock_replacements))):
                    with patch('privacy.util.code_detect.regexdetection.secrets.choice'):
                        result = detector.code_detect_regex(input_code)
                        
                        assert result == "email = 'REDACTED_EMAIL'"
    
    def test_code_detect_regex_no_pii(self):
        """Test code detection with no PII."""
        detector = code_detect()
        input_code = "x = 5"
        
        mock_pii_results = {
            'has_secrets': [False],
            'number_secrets': [0],
            'secrets': [[]]
        }
        
        mock_redacted_results = {
            'new_content': ["x = 5"]
        }
        
        mock_replacements = {}
        
        with patch('privacy.util.code_detect.regexdetection.scan_pii_batch', return_value=mock_pii_results):
            with patch('privacy.util.code_detect.regexdetection.redact_pii_batch', return_value=mock_redacted_results):
                with patch('builtins.open', mock_open(read_data=json.dumps(mock_replacements))):
                    with patch('privacy.util.code_detect.regexdetection.secrets.choice'):
                        result = detector.code_detect_regex(input_code)
                        
                        assert result == "x = 5"
    
    def test_code_detect_regex_loads_replacements_file(self):
        """Test that replacements are loaded from file."""
        detector = code_detect()
        input_code = "api_key = 'abc123'"
        
        mock_pii_results = {
            'has_secrets': [True],
            'number_secrets': [1],
            'secrets': [[{
                'tag': 'KEY',
                'value': 'abc123',
                'start': 11,
                'end': 17
            }]]
        }
        
        mock_redacted_results = {
            'new_content': ["api_key = 'REDACTED_KEY'"]
        }
        
        mock_replacements = {'KEY': ['REDACTED_KEY']}
        
        with patch('privacy.util.code_detect.regexdetection.scan_pii_batch', return_value=mock_pii_results):
            with patch('privacy.util.code_detect.regexdetection.redact_pii_batch', return_value=mock_redacted_results):
                m_open = mock_open(read_data=json.dumps(mock_replacements))
                with patch('builtins.open', m_open):
                    with patch('privacy.util.code_detect.regexdetection.secrets.choice'):
                        result = detector.code_detect_regex(input_code)
                        
                        # Verify file was opened for reading
                        m_open.assert_called()
                        assert result == "api_key = 'REDACTED_KEY'"
    
    def test_code_detect_regex_multiple_secrets(self):
        """Test detection with multiple secrets."""
        detector = code_detect()
        input_code = "email = 'user@test.com'\nip = '192.168.1.1'"
        
        mock_pii_results = {
            'has_secrets': [True],
            'number_secrets': [2],
            'secrets': [[
                {'tag': 'EMAIL', 'value': 'user@test.com', 'start': 9, 'end': 22},
                {'tag': 'IP_ADDRESS', 'value': '192.168.1.1', 'start': 29, 'end': 40}
            ]]
        }
        
        mock_redacted_results = {
            'new_content': ["email = 'REDACTED_EMAIL'\nip = 'REDACTED_IP'"]
        }
        
        mock_replacements = {
            'EMAIL': ['REDACTED_EMAIL'],
            'IP_ADDRESS': ['REDACTED_IP']
        }
        
        with patch('privacy.util.code_detect.regexdetection.scan_pii_batch', return_value=mock_pii_results):
            with patch('privacy.util.code_detect.regexdetection.redact_pii_batch', return_value=mock_redacted_results):
                with patch('builtins.open', mock_open(read_data=json.dumps(mock_replacements))):
                    with patch('privacy.util.code_detect.regexdetection.secrets.choice'):
                        result = detector.code_detect_regex(input_code)
                        
                        assert "REDACTED_EMAIL" in result
                        assert "REDACTED_IP" in result
    
    def test_code_detect_regex_calls_scan_pii_batch(self):
        """Test that scan_pii_batch is called with correct parameters."""
        detector = code_detect()
        input_code = "test_code = 'value'"
        
        mock_pii_results = {
            'has_secrets': [False],
            'number_secrets': [0],
            'secrets': [[]]
        }
        
        mock_redacted_results = {
            'new_content': [input_code]
        }
        
        with patch('privacy.util.code_detect.regexdetection.scan_pii_batch', return_value=mock_pii_results) as mock_scan:
            with patch('privacy.util.code_detect.regexdetection.redact_pii_batch', return_value=mock_redacted_results):
                with patch('builtins.open', mock_open(read_data='{}')):
                    with patch('privacy.util.code_detect.regexdetection.secrets.choice'):
                        detector.code_detect_regex(input_code)
                        
                        # Verify scan_pii_batch was called with correct structure
                        mock_scan.assert_called_once()
                        call_args = mock_scan.call_args[0][0]
                        assert len(call_args) == 1
                        assert call_args[0]['content'] == input_code
    
    def test_code_detect_regex_calls_redact_pii_batch(self):
        """Test that redact_pii_batch is called with correct parameters."""
        detector = code_detect()
        input_code = "password = 'secret123'"
        
        mock_pii_results = {
            'has_secrets': [True],
            'number_secrets': [1],
            'secrets': [[{'tag': 'KEY', 'value': 'secret123', 'start': 12, 'end': 21}]]
        }
        
        mock_redacted_results = {
            'new_content': ["password = 'REDACTED'"]
        }
        
        mock_replacements = {'KEY': ['REDACTED']}
        
        with patch('privacy.util.code_detect.regexdetection.scan_pii_batch', return_value=mock_pii_results):
            with patch('privacy.util.code_detect.regexdetection.redact_pii_batch', return_value=mock_redacted_results) as mock_redact:
                with patch('builtins.open', mock_open(read_data=json.dumps(mock_replacements))):
                    with patch('privacy.util.code_detect.regexdetection.secrets.choice'):
                        detector.code_detect_regex(input_code)
                        
                        # Verify redact_pii_batch was called
                        mock_redact.assert_called_once()
                        call_args = mock_redact.call_args
                        
                        # Check that replacements were passed
                        assert 'replacements' in call_args[1]
                        assert 'add_references' in call_args[1]
    
    def test_code_detect_regex_with_reference_text(self):
        """Test that add_references parameter is passed correctly."""
        detector = code_detect()
        input_code = "token = 'xyz789'"
        
        mock_pii_results = {
            'has_secrets': [True],
            'number_secrets': [1],
            'secrets': [[{'tag': 'KEY', 'value': 'xyz789', 'start': 9, 'end': 15}]]
        }
        
        mock_redacted_results = {
            'new_content': ["token = 'REDACTED_TOKEN'"]
        }
        
        mock_replacements = {'KEY': ['REDACTED_TOKEN']}
        
        with patch('privacy.util.code_detect.regexdetection.scan_pii_batch', return_value=mock_pii_results):
            with patch('privacy.util.code_detect.regexdetection.redact_pii_batch', return_value=mock_redacted_results) as mock_redact:
                with patch('builtins.open', mock_open(read_data=json.dumps(mock_replacements))):
                    with patch('privacy.util.code_detect.regexdetection.secrets.choice'):
                        detector.code_detect_regex(input_code)
                        
                        # Verify add_references=True was passed
                        call_kwargs = mock_redact.call_args[1]
                        assert call_kwargs['add_references'] is True
    
    def test_code_detect_regex_returns_redacted_content(self):
        """Test that the method returns the redacted content."""
        detector = code_detect()
        input_code = "user = 'admin@company.com'"
        expected_output = "user = 'ADMIN_EMAIL'"
        
        mock_pii_results = {
            'has_secrets': [True],
            'number_secrets': [1],
            'secrets': [[{'tag': 'EMAIL', 'value': 'admin@company.com', 'start': 8, 'end': 25}]]
        }
        
        mock_redacted_results = {
            'new_content': [expected_output]
        }
        
        with patch('privacy.util.code_detect.regexdetection.scan_pii_batch', return_value=mock_pii_results):
            with patch('privacy.util.code_detect.regexdetection.redact_pii_batch', return_value=mock_redacted_results):
                with patch('builtins.open', mock_open(read_data='{}')):
                    with patch('privacy.util.code_detect.regexdetection.secrets.choice'):
                        result = detector.code_detect_regex(input_code)
                        
                        assert result == expected_output
    
    def test_code_detect_regex_logging_calls(self):
        """Test that logging is called appropriately."""
        detector = code_detect()
        input_code = "test = 'value'"
        
        mock_pii_results = {
            'has_secrets': [False],
            'number_secrets': [0],
            'secrets': [[]]
        }
        
        mock_redacted_results = {
            'new_content': [input_code]
        }
        
        with patch('privacy.util.code_detect.regexdetection.scan_pii_batch', return_value=mock_pii_results):
            with patch('privacy.util.code_detect.regexdetection.redact_pii_batch', return_value=mock_redacted_results):
                with patch('builtins.open', mock_open(read_data='{}')):
                    with patch('privacy.util.code_detect.regexdetection.logging') as mock_logging:
                        with patch('privacy.util.code_detect.regexdetection.secrets.choice'):
                            detector.code_detect_regex(input_code)
                            
                            # Verify logging was called
                            assert mock_logging.info.called
    
    def test_code_detect_regex_secrets_choice_called(self):
        """Test that secrets.choice is called with seed."""
        detector = code_detect()
        input_code = "data = 'test'"
        
        mock_pii_results = {
            'has_secrets': [False],
            'number_secrets': [0],
            'secrets': [[]]
        }
        
        mock_redacted_results = {
            'new_content': [input_code]
        }
        
        with patch('privacy.util.code_detect.regexdetection.scan_pii_batch', return_value=mock_pii_results):
            with patch('privacy.util.code_detect.regexdetection.redact_pii_batch', return_value=mock_redacted_results):
                with patch('builtins.open', mock_open(read_data='{}')):
                    with patch('privacy.util.code_detect.regexdetection.secrets.choice') as mock_choice:
                        detector.code_detect_regex(input_code)
                        
                        # Verify secrets.choice was called
                        mock_choice.assert_called_once_with(0)


class TestCodeDetectEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_code_detect_regex_empty_input(self):
        """Test with empty input code."""
        detector = code_detect()
        input_code = ""
        
        mock_pii_results = {
            'has_secrets': [False],
            'number_secrets': [0],
            'secrets': [[]]
        }
        
        mock_redacted_results = {
            'new_content': [""]
        }
        
        with patch('privacy.util.code_detect.regexdetection.scan_pii_batch', return_value=mock_pii_results):
            with patch('privacy.util.code_detect.regexdetection.redact_pii_batch', return_value=mock_redacted_results):
                with patch('builtins.open', mock_open(read_data='{}')):
                    with patch('privacy.util.code_detect.regexdetection.secrets.choice'):
                        result = detector.code_detect_regex(input_code)
                        
                        assert result == ""
    
    def test_code_detect_regex_multiline_code(self):
        """Test with multiline code input."""
        detector = code_detect()
        input_code = """
def connect():
    host = '192.168.1.1'
    email = 'admin@test.com'
"""
        
        mock_pii_results = {
            'has_secrets': [True],
            'number_secrets': [2],
            'secrets': [[
                {'tag': 'IP_ADDRESS', 'value': '192.168.1.1', 'start': 30, 'end': 41},
                {'tag': 'EMAIL', 'value': 'admin@test.com', 'start': 60, 'end': 74}
            ]]
        }
        
        expected_redacted = """
def connect():
    host = 'REDACTED_IP'
    email = 'REDACTED_EMAIL'
"""
        
        mock_redacted_results = {
            'new_content': [expected_redacted]
        }
        
        with patch('privacy.util.code_detect.regexdetection.scan_pii_batch', return_value=mock_pii_results):
            with patch('privacy.util.code_detect.regexdetection.redact_pii_batch', return_value=mock_redacted_results):
                with patch('builtins.open', mock_open(read_data='{}')):
                    with patch('privacy.util.code_detect.regexdetection.secrets.choice'):
                        result = detector.code_detect_regex(input_code)
                        
                        assert "REDACTED_IP" in result
                        assert "REDACTED_EMAIL" in result
    
    def test_code_detect_regex_special_characters(self):
        """Test with special characters in code."""
        detector = code_detect()
        input_code = "data = {'email': 'user@domain.co.uk', 'key': 'abc-123-xyz'}"
        
        mock_pii_results = {
            'has_secrets': [True],
            'number_secrets': [2],
            'secrets': [[
                {'tag': 'EMAIL', 'value': 'user@domain.co.uk', 'start': 17, 'end': 34},
                {'tag': 'KEY', 'value': 'abc-123-xyz', 'start': 44, 'end': 55}
            ]]
        }
        
        mock_redacted_results = {
            'new_content': ["data = {'email': 'REDACTED_EMAIL', 'key': 'REDACTED_KEY'}"]
        }
        
        with patch('privacy.util.code_detect.regexdetection.scan_pii_batch', return_value=mock_pii_results):
            with patch('privacy.util.code_detect.regexdetection.redact_pii_batch', return_value=mock_redacted_results):
                with patch('builtins.open', mock_open(read_data='{}')):
                    with patch('privacy.util.code_detect.regexdetection.secrets.choice'):
                        result = detector.code_detect_regex(input_code)
                        
                        assert "REDACTED" in result


class TestCodeDetectIntegration:
    """Integration tests for complete workflows."""
    
    def test_complete_detection_and_redaction_workflow(self):
        """Test complete PII detection and redaction workflow."""
        detector = code_detect()
        input_code = """
# Configuration
SERVER = '10.0.0.1'
ADMIN_EMAIL = 'admin@company.com'
API_KEY = 'sk-1234567890abcdef'
"""
        
        mock_pii_results = {
            'has_secrets': [True],
            'number_secrets': [3],
            'secrets': [[
                {'tag': 'IP_ADDRESS', 'value': '10.0.0.1', 'start': 29, 'end': 37},
                {'tag': 'EMAIL', 'value': 'admin@company.com', 'start': 55, 'end': 72},
                {'tag': 'KEY', 'value': 'sk-1234567890abcdef', 'start': 85, 'end': 103}
            ]]
        }
        
        mock_redacted_results = {
            'new_content': ["""
# Configuration
SERVER = 'REDACTED_IP'
ADMIN_EMAIL = 'REDACTED_EMAIL'
API_KEY = 'REDACTED_KEY'
"""]
        }
        
        mock_replacements = {
            'IP_ADDRESS': ['REDACTED_IP'],
            'EMAIL': ['REDACTED_EMAIL'],
            'KEY': ['REDACTED_KEY']
        }
        
        with patch('privacy.util.code_detect.regexdetection.scan_pii_batch', return_value=mock_pii_results):
            with patch('privacy.util.code_detect.regexdetection.redact_pii_batch', return_value=mock_redacted_results):
                with patch('builtins.open', mock_open(read_data=json.dumps(mock_replacements))):
                    with patch('privacy.util.code_detect.regexdetection.secrets.choice'):
                        result = detector.code_detect_regex(input_code)
                        
                        assert "REDACTED_IP" in result
                        assert "REDACTED_EMAIL" in result
                        assert "REDACTED_KEY" in result
                        assert "10.0.0.1" not in result
                        assert "admin@company.com" not in result
