"""Tests for code_detect_regex method to improve coverage"""
import pytest
from unittest.mock import Mock, patch
from privacy.service.code_detect_service import CodeDetect


class TestCodeDetectRegex:
    """Test code_detect_regex method"""
    
    @patch('privacy.service.code_detect_service.code_detect')
    def test_code_detect_regex_with_input(self, mock_code_detect):
        """Test code_detect_regex with valid input"""
        mock_code_detect.codeDetectRegex = Mock(return_value={
            "redacted": "code with secrets removed"
        })
        
        service = CodeDetect()
        payload = {"input_text": "password = 'secret123'"}
        
        result = service.code_detect_regex(payload)
        
        assert result is not None
        mock_code_detect.codeDetectRegex.assert_called_once_with("password = 'secret123'")
    
    @patch('privacy.service.code_detect_service.code_detect')
    def test_code_detect_regex_empty_string(self, mock_code_detect):
        """Test code_detect_regex with empty string"""
        mock_code_detect.codeDetectRegex = Mock(return_value={"redacted": ""})
        
        service = CodeDetect()
        payload = {"input_text": ""}
        
        result = service.code_detect_regex(payload)
        
        assert result is not None
        mock_code_detect.codeDetectRegex.assert_called_once_with("")
    
    @patch('privacy.service.code_detect_service.code_detect')
    def test_code_detect_regex_multiline(self, mock_code_detect):
        """Test code_detect_regex with multiline code"""
        mock_code_detect.codeDetectRegex = Mock(return_value={
            "redacted": "multiline code redacted"
        })
        
        service = CodeDetect()
        code = """
def authenticate():
    api_key = 'secret'
    return api_key
"""
        payload = {"input_text": code}
        
        result = service.code_detect_regex(payload)
        
        assert result is not None
        mock_code_detect.codeDetectRegex.assert_called_once_with(code)
