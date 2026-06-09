"""
Tests for code_detect_service.py
"""

import pytest
from unittest.mock import patch, MagicMock
from privacy.service.code_detect_service import CodeDetect, AttributeDict


class TestAttributeDict:
    """Test AttributeDict class."""
    
    def test_attribute_dict_basic_operations(self):
        """Test basic dictionary and attribute operations."""
        attr_dict = AttributeDict()
        
        # Test setting and getting via dict interface
        attr_dict['key1'] = 'value1'
        assert attr_dict['key1'] == 'value1'
        
        # Test setting and getting via attribute interface
        attr_dict.key2 = 'value2'
        assert attr_dict.key2 == 'value2'
        assert attr_dict['key2'] == 'value2'
        
        # Test deleting via attribute interface
        del attr_dict.key2
        assert 'key2' not in attr_dict
    
    def test_attribute_dict_initialization(self):
        """Test AttributeDict initialization with data."""
        data = {'inputText': 'sample code', 'option': 'test'}
        attr_dict = AttributeDict(data)
        
        assert attr_dict.inputText == 'sample code'
        assert attr_dict['option'] == 'test'


class TestCodeDetect:
    """Test CodeDetect class methods."""
    
    def test_code_detect_regex_success(self):
        """Test codeDetectRegex with successful detection."""
        with patch('privacy.service.code_detect_service.code_detect') as mock_code_detect:
            # Mock the regex detection
            mock_output = {
                'detected_pii': ['API_KEY', 'EMAIL'],
                'text': 'sample code with secrets'
            }
            mock_code_detect.codeDetectRegex.return_value = mock_output
            
            # Test payload
            payload = {
                'inputText': 'const apiKey = "sk_test_12345"; email = "test@example.com";'
            }
            
            result = CodeDetect.codeDetectRegex(payload)
            
            # Verify mock was called with correct data
            mock_code_detect.codeDetectRegex.assert_called_once()
            call_args = mock_code_detect.codeDetectRegex.call_args[0][0]
            assert call_args == payload['inputText']
            
            # Verify result
            assert result == mock_output
    
    def test_code_detect_regex_empty_input(self):
        """Test codeDetectRegex with empty input."""
        with patch('privacy.service.code_detect_service.code_detect') as mock_code_detect:
            mock_code_detect.codeDetectRegex.return_value = {'detected_pii': []}
            
            payload = {'inputText': ''}
            result = CodeDetect.codeDetectRegex(payload)
            
            mock_code_detect.codeDetectRegex.assert_called_once_with('')
            assert result == {'detected_pii': []}
    
    def test_code_detect_regex_special_characters(self):
        """Test codeDetectRegex with special characters."""
        with patch('privacy.service.code_detect_service.code_detect') as mock_code_detect:
            mock_output = {'detected_pii': ['PASSWORD']}
            mock_code_detect.codeDetectRegex.return_value = mock_output
            
            payload = {
                'inputText': 'password = "P@ssw0rd!#$%";\napi_key="sk-123"'
            }
            
            result = CodeDetect.codeDetectRegex(payload)
            
            assert result == mock_output
            mock_code_detect.codeDetectRegex.assert_called_once()
    
    def test_code_detect_ner_text_success(self):
        """Test codeDetectNerText with successful NER detection."""
        with patch('privacy.service.code_detect_service.code_detect_ner') as mock_ner:
            # Mock the NER detection
            mock_output = {
                'entities': [
                    {'type': 'PERSON', 'text': 'John Doe'},
                    {'type': 'EMAIL', 'text': 'john@example.com'}
                ],
                'redacted_text': 'Hello [PERSON], your email is [EMAIL]'
            }
            mock_ner.textner.return_value = mock_output
            
            # Test payload
            payload = {
                'inputText': 'Hello John Doe, your email is john@example.com'
            }
            
            result = CodeDetect.codeDetectNerText(payload)
            
            # Verify mock was called correctly
            mock_ner.textner.assert_called_once_with(payload['inputText'])
            
            # Verify result
            assert result == mock_output
            assert 'entities' in result
            assert len(result['entities']) == 2
    
    def test_code_detect_ner_text_empty_input(self):
        """Test codeDetectNerText with empty input."""
        with patch('privacy.service.code_detect_service.code_detect_ner') as mock_ner:
            mock_ner.textner.return_value = {'entities': [], 'redacted_text': ''}
            
            payload = {'inputText': ''}
            result = CodeDetect.codeDetectNerText(payload)
            
            mock_ner.textner.assert_called_once_with('')
            assert result == {'entities': [], 'redacted_text': ''}
    
    def test_code_detect_ner_text_code_snippet(self):
        """Test codeDetectNerText with actual code snippet."""
        with patch('privacy.service.code_detect_service.code_detect_ner') as mock_ner:
            mock_output = {
                'entities': [
                    {'type': 'API_KEY', 'text': 'sk_live_1234567890'},
                    {'type': 'EMAIL', 'text': 'admin@company.com'}
                ],
                'redacted_text': 'api_key = "[API_KEY]"\nemail = "[EMAIL]"'
            }
            mock_ner.textner.return_value = mock_output
            
            payload = {
                'inputText': '''
                api_key = "sk_live_1234567890"
                email = "admin@company.com"
                '''
            }
            
            result = CodeDetect.codeDetectNerText(payload)
            
            assert result == mock_output
            assert len(result['entities']) == 2
    
    def test_code_detect_ner_text_multiline_code(self):
        """Test codeDetectNerText with multiline code containing PII."""
        with patch('privacy.service.code_detect_service.code_detect_ner') as mock_ner:
            mock_output = {
                'entities': [
                    {'type': 'PERSON', 'text': 'Alice Smith'},
                    {'type': 'PHONE', 'text': '555-1234'},
                    {'type': 'SSN', 'text': '123-45-6789'}
                ],
                'redacted_text': 'Multiline code with redacted PII'
            }
            mock_ner.textner.return_value = mock_output
            
            code_input = """
            def process_user():
                user = {
                    'name': 'Alice Smith',
                    'phone': '555-1234',
                    'ssn': '123-45-6789'
                }
                return user
            """
            
            payload = {'inputText': code_input}
            result = CodeDetect.codeDetectNerText(payload)
            
            mock_ner.textner.assert_called_once_with(code_input)
            assert result == mock_output
            assert len(result['entities']) == 3
    
    def test_attribute_dict_in_code_detect_regex(self):
        """Test that AttributeDict is properly used in codeDetectRegex."""
        with patch('privacy.service.code_detect_service.code_detect') as mock_code_detect:
            mock_code_detect.codeDetectRegex.return_value = {'result': 'success'}
            
            # Pass regular dict
            payload = {'inputText': 'test code', 'extra_field': 'value'}
            result = CodeDetect.codeDetectRegex(payload)
            
            # Verify AttributeDict conversion worked
            call_args = mock_code_detect.codeDetectRegex.call_args[0][0]
            assert call_args == 'test code'
            assert result == {'result': 'success'}
    
    def test_attribute_dict_in_code_detect_ner(self):
        """Test that AttributeDict is properly used in codeDetectNerText."""
        with patch('privacy.service.code_detect_service.code_detect_ner') as mock_ner:
            mock_ner.textner.return_value = {'entities': []}
            
            # Pass regular dict
            payload = {'inputText': 'test text', 'another_field': 'data'}
            result = CodeDetect.codeDetectNerText(payload)
            
            # Verify AttributeDict conversion worked
            mock_ner.textner.assert_called_once_with('test text')
            assert result == {'entities': []}
    
    def test_code_detect_regex_with_complex_payload(self):
        """Test codeDetectRegex with complex payload structure."""
        with patch('privacy.service.code_detect_service.code_detect') as mock_code_detect:
            mock_output = {
                'detected_pii': ['API_KEY', 'SECRET_KEY', 'PASSWORD'],
                'count': 3,
                'confidence': 0.95
            }
            mock_code_detect.codeDetectRegex.return_value = mock_output
            
            payload = {
                'inputText': '''
                const config = {
                    apiKey: "sk_test_abcd1234",
                    secretKey: "secret_xyz789",
                    password: "MyP@ssw0rd123"
                };
                ''',
                'language': 'javascript',
                'sensitivity': 'high'
            }
            
            result = CodeDetect.codeDetectRegex(payload)
            
            assert result == mock_output
            assert result['count'] == 3
            assert result['confidence'] == 0.95
    
    def test_code_detect_ner_text_with_complex_payload(self):
        """Test codeDetectNerText with complex payload structure."""
        with patch('privacy.service.code_detect_service.code_detect_ner') as mock_ner:
            mock_output = {
                'entities': [
                    {'type': 'PERSON', 'text': 'Bob Johnson', 'start': 10, 'end': 21},
                    {'type': 'EMAIL', 'text': 'bob@example.com', 'start': 35, 'end': 50}
                ],
                'redacted_text': 'Customer [PERSON] contacted us at [EMAIL]',
                'confidence_scores': [0.98, 0.96]
            }
            mock_ner.textner.return_value = mock_output
            
            payload = {
                'inputText': 'Customer Bob Johnson contacted us at bob@example.com',
                'model': 'en_core_web_sm',
                'include_positions': True
            }
            
            result = CodeDetect.codeDetectNerText(payload)
            
            assert result == mock_output
            assert len(result['entities']) == 2
            assert 'confidence_scores' in result
