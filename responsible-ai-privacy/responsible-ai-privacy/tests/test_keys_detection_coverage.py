"""
Comprehensive tests for keys_detection.py - Missing lines 112-139
Tests cover the detect function with various scenarios including gibberish, hashes, and indexes
"""

import pytest
import tempfile
import os
from unittest.mock import MagicMock, patch, ANY
from privacy.util.code_detect.utils.keys_detection import detect_keys


class TestKeysDetection:
    """Test keys detection functionality"""
    
    def test_detect_with_valid_key(self):
        """Test detecting a valid secret key"""
        content = "api_key=s3cr3t_t0k3n_abc123xyz"
        suffix = ".py"
        
        with patch('privacy.util.code_detect.utils.keys_detection.tempfile.NamedTemporaryFile') as mock_temp, \
             patch('privacy.util.code_detect.utils.keys_detection.SecretsCollection') as mock_secrets, \
             patch('privacy.util.code_detect.utils.keys_detection.transient_settings'), \
             patch('privacy.util.code_detect.utils.keys_detection.is_gibberish', return_value=True), \
             patch('privacy.util.code_detect.utils.keys_detection.is_hash', return_value=False), \
             patch('privacy.util.code_detect.utils.keys_detection.file_has_hashes', return_value=False), \
             patch('privacy.util.code_detect.utils.keys_detection.get_indexes', return_value=[(8, 27)]), \
             patch('privacy.util.code_detect.utils.keys_detection.os.unlink'):
            
            mock_fp = MagicMock()
            mock_fp.name = "/tmp/test_file_12345.py"
            mock_temp.return_value = mock_fp
            
            mock_secret_obj = MagicMock()
            mock_secret_obj.secret_value = "s3cr3t_t0k3n_abc123xyz"
            
            mock_secrets_instance = MagicMock()
            mock_secrets_instance.data = {"key1": [mock_secret_obj]}
            mock_secrets.return_value = mock_secrets_instance
            
            result = detect_keys(content, suffix)
            
            assert len(result) > 0
            assert result[0]["tag"] == "KEY"
            assert result[0]["value"] == "s3cr3t_t0k3n_abc123xyz"
            assert result[0]["start"] == 8
            assert result[0]["end"] == 27
    
    def test_detect_empty_secrets_data(self):
        """Test when SecretsCollection has no data"""
        content = "safe_code_no_secrets()"
        suffix = ".py"
        
        with patch('privacy.util.code_detect.utils.keys_detection.tempfile.NamedTemporaryFile') as mock_temp, \
             patch('privacy.util.code_detect.utils.keys_detection.SecretsCollection') as mock_secrets, \
             patch('privacy.util.code_detect.utils.keys_detection.transient_settings'), \
             patch('privacy.util.code_detect.utils.keys_detection.os.unlink'):
            
            mock_fp = MagicMock()
            mock_fp.name = "/tmp/test_file.py"
            mock_temp.return_value = mock_fp
            
            mock_secrets_instance = MagicMock()
            mock_secrets_instance.data = {}  # Empty data
            mock_secrets.return_value = mock_secrets_instance
            
            result = detect_keys(content, suffix)
            
            assert result == []
    
    def test_detect_gibberish_filter(self):
        """Test that gibberish values are skipped"""
        content = "token=abc123"
        suffix = ".env"
        
        with patch('privacy.util.code_detect.utils.keys_detection.tempfile.NamedTemporaryFile') as mock_temp, \
             patch('privacy.util.code_detect.utils.keys_detection.SecretsCollection') as mock_secrets, \
             patch('privacy.util.code_detect.utils.keys_detection.transient_settings'), \
             patch('privacy.util.code_detect.utils.keys_detection.is_gibberish', return_value=False), \
             patch('privacy.util.code_detect.utils.keys_detection.os.unlink'):
            
            mock_fp = MagicMock()
            mock_fp.name = "/tmp/test_file.env"
            mock_temp.return_value = mock_fp
            
            mock_secret_obj = MagicMock()
            mock_secret_obj.secret_value = "abc123"
            
            mock_secrets_instance = MagicMock()
            mock_secrets_instance.data = {"key1": [mock_secret_obj]}
            mock_secrets.return_value = mock_secrets_instance
            
            result = detect_keys(content, suffix)
            
            # Should be empty because is_gibberish returns False (skip non-gibberish)
            assert result == []
    
    def test_detect_hash_filter(self):
        """Test that hash values are skipped"""
        content = "hash=5d41402abc4b2a76b9719d911017c592"  # MD5 of 'hello'
        suffix = ".txt"
        
        with patch('privacy.util.code_detect.utils.keys_detection.tempfile.NamedTemporaryFile') as mock_temp, \
             patch('privacy.util.code_detect.utils.keys_detection.SecretsCollection') as mock_secrets, \
             patch('privacy.util.code_detect.utils.keys_detection.transient_settings'), \
             patch('privacy.util.code_detect.utils.keys_detection.is_gibberish', return_value=True), \
             patch('privacy.util.code_detect.utils.keys_detection.is_hash', return_value=True), \
             patch('privacy.util.code_detect.utils.keys_detection.os.unlink'):
            
            mock_fp = MagicMock()
            mock_fp.name = "/tmp/test_file.txt"
            mock_temp.return_value = mock_fp
            
            mock_secret_obj = MagicMock()
            mock_secret_obj.secret_value = "5d41402abc4b2a76b9719d911017c592"
            
            mock_secrets_instance = MagicMock()
            mock_secrets_instance.data = {"key1": [mock_secret_obj]}
            mock_secrets.return_value = mock_secrets_instance
            
            result = detect_keys(content, suffix)
            
            # Should be empty because is_hash returns True (skip hashes)
            assert result == []
    
    def test_detect_file_has_hashes_filter(self):
        """Test that files with hashes are skipped"""
        content = "password=abc123\nsha256=5d41402abc4b2a76b9719d911017c592"
        suffix = ".py"
        
        with patch('privacy.util.code_detect.utils.keys_detection.tempfile.NamedTemporaryFile') as mock_temp, \
             patch('privacy.util.code_detect.utils.keys_detection.SecretsCollection') as mock_secrets, \
             patch('privacy.util.code_detect.utils.keys_detection.transient_settings'), \
             patch('privacy.util.code_detect.utils.keys_detection.is_gibberish', return_value=True), \
             patch('privacy.util.code_detect.utils.keys_detection.is_hash', return_value=False), \
             patch('privacy.util.code_detect.utils.keys_detection.file_has_hashes', return_value=True), \
             patch('privacy.util.code_detect.utils.keys_detection.os.unlink'):
            
            mock_fp = MagicMock()
            mock_fp.name = "/tmp/test_file.py"
            mock_temp.return_value = mock_fp
            
            mock_secret_obj = MagicMock()
            mock_secret_obj.secret_value = "abc123"
            
            mock_secrets_instance = MagicMock()
            mock_secrets_instance.data = {"key1": [mock_secret_obj]}
            mock_secrets.return_value = mock_secrets_instance
            
            result = detect_keys(content, suffix)
            
            # Should be empty because file_has_hashes returns True
            assert result == []
    
    def test_detect_multiple_secrets(self):
        """Test detecting multiple secrets in one file"""
        content = "api_key=secret1\ndb_pass=secret2"
        suffix = ".json"
        
        with patch('privacy.util.code_detect.utils.keys_detection.tempfile.NamedTemporaryFile') as mock_temp, \
             patch('privacy.util.code_detect.utils.keys_detection.SecretsCollection') as mock_secrets, \
             patch('privacy.util.code_detect.utils.keys_detection.transient_settings'), \
             patch('privacy.util.code_detect.utils.keys_detection.is_gibberish', return_value=True), \
             patch('privacy.util.code_detect.utils.keys_detection.is_hash', return_value=False), \
             patch('privacy.util.code_detect.utils.keys_detection.file_has_hashes', return_value=False), \
             patch('privacy.util.code_detect.utils.keys_detection.get_indexes') as mock_indexes, \
             patch('privacy.util.code_detect.utils.keys_detection.os.unlink'):
            
            mock_fp = MagicMock()
            mock_fp.name = "/tmp/test_file.json"
            mock_temp.return_value = mock_fp
            
            mock_secret_obj1 = MagicMock()
            mock_secret_obj1.secret_value = "secret1"
            mock_secret_obj2 = MagicMock()
            mock_secret_obj2.secret_value = "secret2"
            
            mock_secrets_instance = MagicMock()
            mock_secrets_instance.data = {"key1": [mock_secret_obj1, mock_secret_obj2]}
            mock_secrets.return_value = mock_secrets_instance
            
            # Return different indexes for each secret
            mock_indexes.side_effect = [[(8, 15)], [(32, 39)]]
            
            result = detect_keys(content, suffix)
            
            assert len(result) == 2
            assert result[0]["value"] == "secret1"
            assert result[1]["value"] == "secret2"
    
    def test_detect_multiple_occurrences_same_secret(self):
        """Test detecting same secret appearing multiple times"""
        content = "token=abc123xyz\nauth_token=abc123xyz"
        suffix = ".py"
        
        with patch('privacy.util.code_detect.utils.keys_detection.tempfile.NamedTemporaryFile') as mock_temp, \
             patch('privacy.util.code_detect.utils.keys_detection.SecretsCollection') as mock_secrets, \
             patch('privacy.util.code_detect.utils.keys_detection.transient_settings'), \
             patch('privacy.util.code_detect.utils.keys_detection.is_gibberish', return_value=True), \
             patch('privacy.util.code_detect.utils.keys_detection.is_hash', return_value=False), \
             patch('privacy.util.code_detect.utils.keys_detection.file_has_hashes', return_value=False), \
             patch('privacy.util.code_detect.utils.keys_detection.get_indexes', return_value=[(6, 15), (26, 35)]), \
             patch('privacy.util.code_detect.utils.keys_detection.os.unlink'):
            
            mock_fp = MagicMock()
            mock_fp.name = "/tmp/test_file.py"
            mock_temp.return_value = mock_fp
            
            mock_secret_obj = MagicMock()
            mock_secret_obj.secret_value = "abc123xyz"
            
            mock_secrets_instance = MagicMock()
            mock_secrets_instance.data = {"key1": [mock_secret_obj]}
            mock_secrets.return_value = mock_secrets_instance
            
            result = detect_keys(content, suffix)
            
            # Should have 2 entries for the same secret at different positions
            assert len(result) == 2
            assert result[0]["value"] == "abc123xyz"
            assert result[1]["value"] == "abc123xyz"
            assert result[0]["start"] == 6
            assert result[1]["start"] == 26
    
    def test_detect_temp_file_cleanup(self):
        """Test that temporary file is properly deleted"""
        content = "key=value"
        suffix = ".txt"
        
        with patch('privacy.util.code_detect.utils.keys_detection.tempfile.NamedTemporaryFile') as mock_temp, \
             patch('privacy.util.code_detect.utils.keys_detection.SecretsCollection') as mock_secrets, \
             patch('privacy.util.code_detect.utils.keys_detection.transient_settings'), \
             patch('privacy.util.code_detect.utils.keys_detection.os.unlink') as mock_unlink:
            
            mock_fp = MagicMock()
            mock_fp.name = "/tmp/test_file_to_delete.txt"
            mock_temp.return_value = mock_fp
            
            mock_secrets_instance = MagicMock()
            mock_secrets_instance.data = {}
            mock_secrets.return_value = mock_secrets_instance
            
            detect_keys(content, suffix)
            
            # Verify os.unlink was called with the temp file
            mock_unlink.assert_called_once_with(mock_fp.name)
    
    def test_detect_with_different_suffix(self):
        """Test detection with different file suffixes"""
        suffixes = [".py", ".json", ".env", ".yml", ".yaml", ".txt"]
        
        for suffix in suffixes:
            with patch('privacy.util.code_detect.utils.keys_detection.tempfile.NamedTemporaryFile') as mock_temp, \
                 patch('privacy.util.code_detect.utils.keys_detection.SecretsCollection') as mock_secrets, \
                 patch('privacy.util.code_detect.utils.keys_detection.transient_settings'), \
                 patch('privacy.util.code_detect.utils.keys_detection.os.unlink'):
                
                mock_fp = MagicMock()
                mock_fp.name = f"/tmp/test_file{suffix}"
                mock_temp.return_value = mock_fp
                
                mock_secrets_instance = MagicMock()
                mock_secrets_instance.data = {}
                mock_secrets.return_value = mock_secrets_instance
                
                result = detect_keys(f"content_for_{suffix}", suffix)
                
                # Should return empty list for no secrets
                assert result == []
                
                # Verify NamedTemporaryFile was called with correct suffix
                assert mock_temp.called
