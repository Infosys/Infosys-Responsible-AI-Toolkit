"""Edge case tests for code detection service to improve coverage"""
import pytest
from unittest.mock import Mock, patch
from privacy.service.code_detect_service import CodeDetect


class TestCodeDetectNER:
    """Test code_detect_ner_text method"""
    
    @patch('privacy.service.code_detect_service.code_detect_ner.textner')
    def test_code_detect_ner_with_pii(self, mock_ner):
        """Test NER detection with PII"""
        mock_ner.return_value = [
            {"entity": "SECRET", "word": "password123", "start": 10, "end": 21}
        ]
        
        service = CodeDetect()
        payload = {"input_text": "password='password123'"}
        
        result = service.code_detect_ner_text(payload)
        
        assert result is not None
        mock_ner.assert_called_once_with("password='password123'")
    
    @patch('privacy.service.code_detect_service.code_detect_ner.textner')
    def test_code_detect_ner_no_pii(self, mock_ner):
        """Test NER detection with no PII"""
        mock_ner.return_value = []
        
        service = CodeDetect()
        payload = {"input_text": "print('Hello World')"}
        
        result = service.code_detect_ner_text(payload)
        
        assert result is not None
        mock_ner.assert_called_once_with("print('Hello World')")
    
    @patch('privacy.service.code_detect_service.code_detect_ner.textner')
    def test_code_detect_ner_javascript(self, mock_ner):
        """Test NER detection with JavaScript code"""
        mock_ner.return_value = [
            {"entity": "KEY", "word": "abc123", "start": 12, "end": 18}
        ]
        
        service = CodeDetect()
        payload = {"input_text": "const token='abc123';"}
        
        result = service.code_detect_ner_text(payload)
        
        assert result is not None
        mock_ner.assert_called_once_with("const token='abc123';")
    
    @patch('privacy.service.code_detect_service.code_detect_ner.textner')
    def test_code_detect_ner_with_special_characters(self, mock_ner):
        """Test NER detection with special characters"""
        mock_ner.return_value = []
        
        service = CodeDetect()
        payload = {"input_text": "password = '!@#$%^&*()'"}
        
        result = service.code_detect_ner_text(payload)
        
        assert result is not None
        mock_ner.assert_called_once_with("password = '!@#$%^&*()'")
    
    @patch('privacy.service.code_detect_service.code_detect_ner.textner')
    def test_code_detect_ner_multiple_secrets(self, mock_ner):
        """Test NER detection with multiple secrets"""
        mock_ner.return_value = [
            {"entity": "SECRET", "word": "pass1", "start": 10, "end": 15},
            {"entity": "SECRET", "word": "pass2", "start": 30, "end": 35}
        ]
        
        service = CodeDetect()
        payload = {"input_text": "password1='pass1' and password2='pass2'"}
        
        result = service.code_detect_ner_text(payload)
        
        assert result is not None
        assert len(result) == 2
