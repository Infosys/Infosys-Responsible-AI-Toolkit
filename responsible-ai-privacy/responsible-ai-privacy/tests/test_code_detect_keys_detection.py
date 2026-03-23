"""
Tests for privacy.util.code_detect.utils.keys_detection module
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from privacy.util.code_detect.utils.keys_detection import (
    is_gibberish,
    is_hash,
    file_has_hashes,
    get_indexes,
    detect_keys
)


class TestIsGibberish:
    """Test is_gibberish function"""
    
    @patch('privacy.util.code_detect.utils.keys_detection.detector.create_from_model')
    def test_is_gibberish_with_gibberish_string(self, mock_detector):
        """Test that gibberish strings are correctly identified"""
        mock_instance = MagicMock()
        mock_instance.is_gibberish.return_value = True
        mock_detector.return_value = mock_instance
        
        result = is_gibberish("xK9mP4vL2qR8")
        
        assert result is True
        mock_detector.assert_called_once_with('privacy/util/code_detect/gibberish_data/big.model')
        mock_instance.is_gibberish.assert_called_once_with("xk9mp4vl2qr8")
    
    @patch('privacy.util.code_detect.utils.keys_detection.detector.create_from_model')
    def test_is_gibberish_with_real_words(self, mock_detector):
        """Test that real words are not identified as gibberish"""
        mock_instance = MagicMock()
        mock_instance.is_gibberish.return_value = False
        mock_detector.return_value = mock_instance
        
        result = is_gibberish("HelloWorld")
        
        assert result is False
        mock_instance.is_gibberish.assert_called_once_with("helloworld")
    
    @patch('privacy.util.code_detect.utils.keys_detection.detector.create_from_model')
    def test_is_gibberish_case_conversion(self, mock_detector):
        """Test that input is converted to lowercase"""
        mock_instance = MagicMock()
        mock_instance.is_gibberish.return_value = True
        mock_detector.return_value = mock_instance
        
        is_gibberish("UPPERCASE")
        
        mock_instance.is_gibberish.assert_called_once_with("uppercase")


class TestIsHash:
    """Test is_hash function"""
    
    def test_is_hash_with_sha_keyword_32_chars(self):
        """Test hash detection with SHA keyword and 32 char hash"""
        # MD5 hash is 32 characters
        content = "sha256_hash = 5d41402abc4b2a76b9719d911017c592"
        value = "5d41402abc4b2a76b9719d911017c592"
        
        result = is_hash(content, value)
        
        assert result is True
    
    def test_is_hash_with_md5_keyword_32_chars(self):
        """Test hash detection with MD5 keyword and 32 char hash"""
        content = "md5 checksum: 5d41402abc4b2a76b9719d911017c592"
        value = "5d41402abc4b2a76b9719d911017c592"
        
        result = is_hash(content, value)
        
        assert result is True
    
    def test_is_hash_with_hash_keyword_40_chars(self):
        """Test hash detection with hash keyword and 40 char SHA1"""
        content = "file hash = 356a192b7913b04c54574d18c28d46e6395428ab"
        value = "356a192b7913b04c54574d18c28d46e6395428ab"
        
        result = is_hash(content, value)
        
        assert result is True
    
    def test_is_hash_with_byte_keyword_64_chars(self):
        """Test hash detection with byte keyword and 64 char SHA256"""
        content = "byte array: 2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"
        value = "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"
        
        result = is_hash(content, value)
        
        assert result is True
    
    def test_is_hash_wrong_length(self):
        """Test that values with incorrect lengths are not identified as hashes"""
        content = "some_value = abc123"
        value = "abc123"
        
        result = is_hash(content, value)
        
        assert result is False
    
    def test_is_hash_no_keyword(self):
        """Test that values without keywords are not identified as hashes"""
        content = "random_string = a1b2c3d4e5f6789012345678901234"
        value = "a1b2c3d4e5f6789012345678901234"
        
        result = is_hash(content, value)
        
        assert result is False
    
    def test_is_hash_value_not_found(self):
        """Test handling when value is not found in content"""
        content = "some code here"
        value = "notfound"
        
        result = is_hash(content, value)
        
        assert result is False


class TestFileHasHashes:
    """Test file_has_hashes function"""
    
    def test_file_has_hashes_with_sha_occurrences(self):
        """Test detection when file has many SHA occurrences"""
        content = "\n".join(["sha256_hash = abc123"] * 10)
        
        result = file_has_hashes(content, coeff=0.02)
        
        assert result is True
    
    def test_file_has_hashes_with_hash_occurrences(self):
        """Test detection when file has many hash occurrences"""
        content = "\n".join(["hash_value = xyz789"] * 10)
        
        result = file_has_hashes(content, coeff=0.02)
        
        assert result is True
    
    def test_file_has_hashes_below_threshold(self):
        """Test when hash occurrences are below threshold"""
        content = "\n".join(["regular code line"] * 100 + ["sha256 = abc"])
        
        result = file_has_hashes(content, coeff=0.02)
        
        assert result is False
    
    def test_file_has_hashes_custom_coefficient(self):
        """Test with custom coefficient value"""
        content = "\n".join(["sha_value"] * 5)
        
        result = file_has_hashes(content, coeff=0.5)
        
        assert result is True
    
    def test_file_has_hashes_empty_content(self):
        """Test with empty content"""
        content = ""
        
        result = file_has_hashes(content)
        
        assert result is False
    
    def test_file_has_hashes_case_insensitive(self):
        """Test that detection is case-insensitive"""
        content = "\n".join(["SHA256 value"] * 10)
        
        result = file_has_hashes(content, coeff=0.02)
        
        assert result is True


class TestGetIndexes:
    """Test get_indexes function"""
    
    def test_get_indexes_single_occurrence(self):
        """Test finding single occurrence of value"""
        text = "Hello World"
        value = "World"
        
        result = get_indexes(text, value)
        
        assert result == [(6, 11)]
    
    def test_get_indexes_multiple_occurrences(self):
        """Test finding multiple occurrences of value"""
        text = "test test test"
        value = "test"
        
        result = get_indexes(text, value)
        
        assert result == [(0, 4), (5, 9), (10, 14)]
    
    def test_get_indexes_no_occurrences(self):
        """Test when value is not found"""
        text = "Hello World"
        value = "Python"
        
        result = get_indexes(text, value)
        
        assert result == []
    
    def test_get_indexes_overlapping_pattern(self):
        """Test with overlapping patterns"""
        text = "aaa"
        value = "aa"
        
        result = get_indexes(text, value)
        
        # Non-overlapping matches: position 0
        assert result == [(0, 2)]
    
    def test_get_indexes_at_start(self):
        """Test value at the start of text"""
        text = "start middle end"
        value = "start"
        
        result = get_indexes(text, value)
        
        assert result == [(0, 5)]
    
    def test_get_indexes_at_end(self):
        """Test value at the end of text"""
        text = "start middle end"
        value = "end"
        
        result = get_indexes(text, value)
        
        assert result == [(13, 16)]
    
    def test_get_indexes_special_characters(self):
        """Test with special characters in value"""
        text = "key=value&key=value"
        value = "key=value"
        
        result = get_indexes(text, value)
        
        assert result == [(0, 9), (10, 19)]
    
    def test_get_indexes_empty_text(self):
        """Test with empty text"""
        text = ""
        value = "test"
        
        result = get_indexes(text, value)
        
        assert result == []


class TestDetectKeys:
    """Test detect_keys function"""
    
    @patch('privacy.util.code_detect.utils.keys_detection.is_gibberish')
    @patch('privacy.util.code_detect.utils.keys_detection.is_hash')
    @patch('privacy.util.code_detect.utils.keys_detection.SecretsCollection')
    def test_detect_keys_with_valid_key(self, mock_secrets_class, mock_is_hash, mock_is_gibberish):
        """Test detection of valid secrets"""
        mock_is_gibberish.return_value = True
        mock_is_hash.return_value = False
        
        # Mock secret object
        mock_secret = Mock()
        mock_secret.secret_value = "xKcd1234aBcD5678"
        
        # Mock SecretsCollection
        mock_secrets_instance = Mock()
        mock_secrets_instance.data = {"file": [mock_secret]}
        mock_secrets_class.return_value = mock_secrets_instance
        
        content = "API Key: xKcd1234aBcD5678 is secret"
        result = detect_keys(content, suffix=".txt")
        
        assert len(result) > 0
        assert result[0]["tag"] == "KEY"
        assert result[0]["value"] == "xKcd1234aBcD5678"
    
    @patch('privacy.util.code_detect.utils.keys_detection.is_gibberish')
    @patch('privacy.util.code_detect.utils.keys_detection.SecretsCollection')
    def test_detect_keys_filters_non_gibberish(self, mock_secrets_class, mock_is_gibberish):
        """Test that non-gibberish secrets are filtered"""
        mock_is_gibberish.return_value = False
        
        mock_secret = Mock()
        mock_secret.secret_value = "password123"
        
        mock_secrets_instance = Mock()
        mock_secrets_instance.data = {"file": [mock_secret]}
        mock_secrets_class.return_value = mock_secrets_instance
        
        content = "password: password123"
        result = detect_keys(content)
        
        assert len(result) == 0
    
    @patch('privacy.util.code_detect.utils.keys_detection.is_gibberish')
    @patch('privacy.util.code_detect.utils.keys_detection.is_hash')
    @patch('privacy.util.code_detect.utils.keys_detection.file_has_hashes')
    @patch('privacy.util.code_detect.utils.keys_detection.SecretsCollection')
    def test_detect_keys_filters_hashes(self, mock_secrets_class, mock_file_hashes, mock_is_hash, mock_is_gibberish):
        """Test that hash values are filtered"""
        mock_is_gibberish.return_value = True
        mock_is_hash.return_value = True
        mock_file_hashes.return_value = False
        
        mock_secret = Mock()
        mock_secret.secret_value = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
        
        mock_secrets_instance = Mock()
        mock_secrets_instance.data = {"file": [mock_secret]}
        mock_secrets_class.return_value = mock_secrets_instance
        
        content = "SHA256: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
        result = detect_keys(content)
        
        assert len(result) == 0
    
    @patch('privacy.util.code_detect.utils.keys_detection.file_has_hashes')
    @patch('privacy.util.code_detect.utils.keys_detection.is_gibberish')
    @patch('privacy.util.code_detect.utils.keys_detection.SecretsCollection')
    def test_detect_keys_filters_files_with_hashes(self, mock_secrets_class, mock_is_gibberish, mock_file_hashes):
        """Test that files with many hashes are filtered"""
        mock_is_gibberish.return_value = True
        mock_file_hashes.return_value = True
        
        mock_secret = Mock()
        mock_secret.secret_value = "somekey123"
        
        mock_secrets_instance = Mock()
        mock_secrets_instance.data = {"file": [mock_secret]}
        mock_secrets_class.return_value = mock_secrets_instance
        
        content = "key: somekey123"
        result = detect_keys(content)
        
        assert len(result) == 0
    
    @patch('privacy.util.code_detect.utils.keys_detection.SecretsCollection')
    def test_detect_keys_no_secrets_found(self, mock_secrets_class):
        """Test when no secrets are found"""
        mock_secrets_instance = Mock()
        mock_secrets_instance.data = {}
        mock_secrets_class.return_value = mock_secrets_instance
        
        content = "This is plain text with no secrets"
        result = detect_keys(content)
        
        assert len(result) == 0
    
    @patch('privacy.util.code_detect.utils.keys_detection.is_gibberish')
    @patch('privacy.util.code_detect.utils.keys_detection.is_hash')
    @patch('privacy.util.code_detect.utils.keys_detection.SecretsCollection')
    def test_detect_keys_with_custom_suffix(self, mock_secrets_class, mock_is_hash, mock_is_gibberish):
        """Test detect_keys with custom file suffix"""
        mock_is_gibberish.return_value = True
        mock_is_hash.return_value = False
        
        mock_secret = Mock()
        mock_secret.secret_value = "apiKey789xyz"
        
        mock_secrets_instance = Mock()
        mock_secrets_instance.data = {"file": [mock_secret]}
        mock_secrets_class.return_value = mock_secrets_instance
        
        content = "key=apiKey789xyz"
        result = detect_keys(content, suffix=".py")
        
        assert len(result) > 0
