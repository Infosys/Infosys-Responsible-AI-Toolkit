"""Edge case tests for code detection utilities to improve coverage"""
import pytest
from unittest.mock import Mock, patch
from privacy.util.code_detect.pii_redaction import is_private_ip
from privacy.util.code_detect.utils.keys_detection import is_gibberish, is_hash


class TestPiiRedactionUtils:
    """Test PII redaction utility functions"""
    
    def test_is_private_ip_10_range(self):
        """Test detecting private IP in 10.x.x.x range"""
        assert is_private_ip("10.0.0.1") == True
        assert is_private_ip("10.255.255.255") == True
    
    def test_is_private_ip_192_range(self):
        """Test detecting private IP in 192.168.x.x range"""
        assert is_private_ip("192.168.1.1") == True
        assert is_private_ip("192.168.0.255") == True
    
    def test_is_private_ip_172_range(self):
        """Test detecting private IP in 172.16-31.x.x range"""
        assert is_private_ip("172.16.0.1") == True
        assert is_private_ip("172.31.255.255") == True
    
    def test_is_private_ip_public(self):
        """Test public IP returns False"""
        assert is_private_ip("8.8.8.8") == False
        assert is_private_ip("1.2.3.4") == False
    
    def test_is_private_ip_edge_cases(self):
        """Test edge cases for private IP detection"""
        assert is_private_ip("172.15.0.1") == False  # Just outside range
        assert is_private_ip("172.32.0.1") == False  # Just outside range
        assert is_private_ip("192.167.1.1") == False  # Not 192.168


class TestKeysDetection:
    """Test API key detection utilities"""
    
    @patch('privacy.util.code_detect.utils.keys_detection.detector.create_from_model')
    def test_is_gibberish_true(self, mock_detector):
        """Test detecting gibberish string"""
        mock_detector_instance = Mock()
        mock_detector_instance.is_gibberish.return_value = True
        mock_detector.return_value = mock_detector_instance
        
        result = is_gibberish("xkcd1234abcdefgh")
        
        assert result == True
    
    @patch('privacy.util.code_detect.utils.keys_detection.detector.create_from_model')
    def test_is_gibberish_false(self, mock_detector):
        """Test detecting real word"""
        mock_detector_instance = Mock()
        mock_detector_instance.is_gibberish.return_value = False
        mock_detector.return_value = mock_detector_instance
        
        result = is_gibberish("password")
        
        assert result == False
    
    def test_is_hash_not_hash(self):
        """Test non-hash value"""
        content = "regular_string = 'test'"
        value = "test"
        
        result = is_hash(content, value)
        
        assert result == False
    
    def test_is_hash_wrong_length(self):
        """Test value with wrong length for hash"""
        content = "short_value = 'abc'"
        value = "abc"
        
        result = is_hash(content, value)
        
        assert result == False
