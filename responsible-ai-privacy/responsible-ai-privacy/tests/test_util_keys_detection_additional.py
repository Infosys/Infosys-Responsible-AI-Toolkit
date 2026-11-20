"""Additional tests for keys_detection module"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestKeysDetectionFileHashes:
    '''Test file_has_hashes function'''
    
    @patch('privacy.util.code_detect.utils.keys_detection.detector')
    def test_file_has_hashes_with_sha_keywords(self, mock_detector):
        '''Test file with multiple sha references'''
        from privacy.util.code_detect.utils.keys_detection import file_has_hashes
        
        content = '\n'.join(['sha256 hash here'] * 10 + ['other line'] * 90)
        result = file_has_hashes(content, coeff=0.02)
        
        assert result == True
    
    @patch('privacy.util.code_detect.utils.keys_detection.detector')
    def test_file_has_hashes_with_hash_keywords(self, mock_detector):
        '''Test file with multiple hash references'''
        from privacy.util.code_detect.utils.keys_detection import file_has_hashes
        
        content = '\n'.join(['hash value'] * 5 + ['other'] * 95)
        result = file_has_hashes(content, coeff=0.02)
        
        assert result == True
    
    @patch('privacy.util.code_detect.utils.keys_detection.detector')
    def test_file_has_hashes_below_threshold(self, mock_detector):
        '''Test file with few hash references below threshold'''
        from privacy.util.code_detect.utils.keys_detection import file_has_hashes
        
        content = '\n'.join(['normal line'] * 99 + ['sha256'])
        result = file_has_hashes(content, coeff=0.02)
        
        assert result == False
    
    @patch('privacy.util.code_detect.utils.keys_detection.detector')
    def test_file_has_hashes_empty_content(self, mock_detector):
        '''Test with empty content'''
        from privacy.util.code_detect.utils.keys_detection import file_has_hashes
        
        content = ''
        result = file_has_hashes(content, coeff=0.02)
        
        assert result == False
    
    @patch('privacy.util.code_detect.utils.keys_detection.detector')
    def test_file_has_hashes_custom_coefficient(self, mock_detector):
        '''Test with custom coefficient'''
        from privacy.util.code_detect.utils.keys_detection import file_has_hashes
        
        content = '\n'.join(['sha line'] * 15 + ['other'] * 85)
        result = file_has_hashes(content, coeff=0.10)
        
        assert result == True


class TestKeysDetectionIsHash:
    '''Test is_hash function'''
    
    @patch('privacy.util.code_detect.utils.keys_detection.detector')
    def test_is_hash_md5_with_keyword(self, mock_detector):
        '''Test MD5 hash (32 chars) with keyword'''
        from privacy.util.code_detect.utils.keys_detection import is_hash
        
        content = 'md5 hash: 5d41402abc4b2a76b9719d911017c592'
        value = '5d41402abc4b2a76b9719d911017c592'
        
        result = is_hash(content, value)
        assert result == True
    
    @patch('privacy.util.code_detect.utils.keys_detection.detector')
    def test_is_hash_sha1_with_keyword(self, mock_detector):
        '''Test SHA1 hash (40 chars) with keyword'''
        from privacy.util.code_detect.utils.keys_detection import is_hash
        
        content = 'sha1: aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d'
        value = 'aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d'
        
        result = is_hash(content, value)
        assert result == True
    
    @patch('privacy.util.code_detect.utils.keys_detection.detector')
    def test_is_hash_sha256_with_keyword(self, mock_detector):
        '''Test SHA256 hash (64 chars) with keyword'''
        from privacy.util.code_detect.utils.keys_detection import is_hash
        
        content = 'sha256 checksum: 2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae'
        value = '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae'
        
        result = is_hash(content, value)
        assert result == True
    
    @patch('privacy.util.code_detect.utils.keys_detection.detector')
    def test_is_hash_without_keyword(self, mock_detector):
        '''Test hash without keyword in context'''
        from privacy.util.code_detect.utils.keys_detection import is_hash
        
        content = 'some text 5d41402abc4b2a76b9719d911017c592 more text'
        value = '5d41402abc4b2a76b9719d911017c592'
        
        result = is_hash(content, value)
        assert result == False
    
    @patch('privacy.util.code_detect.utils.keys_detection.detector')
    def test_is_hash_wrong_length(self, mock_detector):
        '''Test string with wrong length for hash'''
        from privacy.util.code_detect.utils.keys_detection import is_hash
        
        content = 'sha256: 12345'
        value = '12345'
        
        result = is_hash(content, value)
        assert result == False
    
    @patch('privacy.util.code_detect.utils.keys_detection.detector')
    def test_is_hash_value_not_found(self, mock_detector):
        '''Test when value not found in content'''
        from privacy.util.code_detect.utils.keys_detection import is_hash
        
        content = 'some content without the value'
        value = 'notfound'
        
        result = is_hash(content, value)
        assert result == False
    
    @patch('privacy.util.code_detect.utils.keys_detection.detector')
    def test_is_hash_with_byte_keyword(self, mock_detector):
        '''Test hash with byte keyword'''
        from privacy.util.code_detect.utils.keys_detection import is_hash
        
        content = 'byte array: 5d41402abc4b2a76b9719d911017c592'
        value = '5d41402abc4b2a76b9719d911017c592'
        
        result = is_hash(content, value)
        assert result == True


class TestKeysDetectionSecretsDetection:
    '''Test secrets detection setup'''
    
    @patch('privacy.util.code_detect.utils.keys_detection.detector')
    def test_filters_configuration(self, mock_detector):
        '''Test filters are properly configured'''
        from privacy.util.code_detect.utils.keys_detection import filters
        
        assert len(filters) == 4
        assert any('is_potential_uuid' in f['path'] for f in filters)
        assert any('is_likely_id_string' in f['path'] for f in filters)
        assert any('is_templated_secret' in f['path'] for f in filters)
        assert any('is_sequential_string' in f['path'] for f in filters)
    
    @patch('privacy.util.code_detect.utils.keys_detection.detector')
    def test_plugins_configuration(self, mock_detector):
        '''Test plugins are properly configured'''
        from privacy.util.code_detect.utils.keys_detection import plugins
        
        plugin_names = [p['name'] for p in plugins]
        
        assert 'AWSKeyDetector' in plugin_names
        assert 'GitHubTokenDetector' in plugin_names
        assert 'JwtTokenDetector' in plugin_names
        assert 'Base64HighEntropyString' in plugin_names
        assert len(plugins) > 10
