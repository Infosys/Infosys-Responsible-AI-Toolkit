"""
Unit tests for config module
"""
import pytest
from unittest.mock import Mock, patch, mock_open
from privacy.config.config import readConfig, read_config_yaml


class TestReadConfig:
    """Test configuration reading functions"""

    @patch('privacy.config.config.ConfigParser')
    def test_read_config_success(self, mock_parser):
        """Test reading config successfully"""
        mock_parser_instance = Mock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.has_section.return_value = True
        mock_parser_instance.items.return_value = [('key1', 'value1'), ('key2', 'value2')]
        
        result = readConfig('test_section', 'test_file.ini')
        
        assert result == {'key1': 'value1', 'key2': 'value2'}
        mock_parser_instance.read.assert_called_once_with('test_file.ini')

    @patch('privacy.config.config.ConfigParser')
    def test_read_config_section_not_found(self, mock_parser):
        """Test reading config with non-existent section"""
        mock_parser_instance = Mock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.has_section.return_value = False
        
        with pytest.raises(Exception) as exc_info:
            readConfig('nonexistent_section', 'test_file.ini')
        
        assert 'not found' in str(exc_info.value)

    @patch('privacy.config.config.ConfigParser')
    def test_read_config_empty_section(self, mock_parser):
        """Test reading config with empty section"""
        mock_parser_instance = Mock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.has_section.return_value = True
        mock_parser_instance.items.return_value = []
        
        result = readConfig('empty_section', 'test_file.ini')
        
        assert result == {}


class TestReadConfigYaml:
    """Test YAML configuration reading"""

    @patch('builtins.open', mock_open(read_data='key1: value1\nkey2: value2'))
    @patch('privacy.config.config.yaml.safe_load')
    def test_read_yaml_config_success(self, mock_yaml_load):
        """Test reading YAML config successfully"""
        mock_yaml_load.return_value = {'key1': 'value1', 'key2': 'value2'}
        
        result = read_config_yaml('test_config.yaml')
        
        assert result == {'key1': 'value1', 'key2': 'value2'}
        mock_yaml_load.assert_called_once()

    @patch('builtins.open', mock_open(read_data=''))
    @patch('privacy.config.config.yaml.safe_load')
    def test_read_yaml_config_empty(self, mock_yaml_load):
        """Test reading empty YAML config"""
        mock_yaml_load.return_value = {}
        
        result = read_config_yaml('empty_config.yaml')
        
        assert result == {}

    @patch('builtins.open', mock_open(read_data='nested:\n  key1: value1\n  key2: value2'))
    @patch('privacy.config.config.yaml.safe_load')
    def test_read_yaml_config_nested(self, mock_yaml_load):
        """Test reading nested YAML config"""
        mock_yaml_load.return_value = {'nested': {'key1': 'value1', 'key2': 'value2'}}
        
        result = read_config_yaml('nested_config.yaml')
        
        assert 'nested' in result
        assert result['nested']['key1'] == 'value1'
