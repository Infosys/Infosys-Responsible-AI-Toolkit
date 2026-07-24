"""
Unit tests for config module
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
import yaml
from configparser import ConfigParser


class TestConfigFunctions:
    """Tests for configuration functions"""

    def test_readconfig_success(self):
        """Test readConfig with valid section"""
        from rai_backend.config.config import readConfig
        
        config_content = """
[database]
host = localhost
port = 27017
name = testdb
"""
        with patch('builtins.open', mock_open(read_data=config_content)):
            with patch.object(ConfigParser, 'read'):
                with patch.object(ConfigParser, 'has_section', return_value=True):
                    with patch.object(ConfigParser, 'items', return_value=[
                        ('host', 'localhost'),
                        ('port', '27017'),
                        ('name', 'testdb')
                    ]):
                        result = readConfig('database', 'test.ini')
                        
                        assert result['host'] == 'localhost'
                        assert result['port'] == '27017'
                        assert result['name'] == 'testdb'

    def test_readconfig_section_not_found(self):
        """Test readConfig with non-existent section"""
        from rai_backend.config.config import readConfig
        
        with patch.object(ConfigParser, 'read'):
            with patch.object(ConfigParser, 'has_section', return_value=False):
                with pytest.raises(Exception, match='Section .* not found'):
                    readConfig('nonexistent', 'test.ini')

    def test_read_config_yaml_success(self):
        """Test read_config_yaml with valid YAML file"""
        from rai_backend.config.config import read_config_yaml
        
        yaml_content = """
title: Test API
version: 1.0.0
description: Test Description
"""
        mock_yaml_data = {
            'title': 'Test API',
            'version': '1.0.0',
            'description': 'Test Description'
        }
        
        with patch('builtins.open', mock_open(read_data=yaml_content)):
            with patch('yaml.safe_load', return_value=mock_yaml_data):
                result = read_config_yaml('metadata.yaml')
                
                assert result['title'] == 'Test API'
                assert result['version'] == '1.0.0'
                assert result['description'] == 'Test Description'

    def test_read_config_yaml_empty_file(self):
        """Test read_config_yaml with empty YAML file"""
        from rai_backend.config.config import read_config_yaml
        
        with patch('builtins.open', mock_open(read_data='')):
            with patch('yaml.safe_load', return_value=None):
                result = read_config_yaml('empty.yaml')
                
                assert result is None

    def test_read_config_yaml_with_nested_structure(self):
        """Test read_config_yaml with nested YAML structure"""
        from rai_backend.config.config import read_config_yaml
        
        mock_yaml_data = {
            'database': {
                'host': 'localhost',
                'port': 27017
            },
            'api': {
                'version': '1.0',
                'endpoints': ['auth', 'user']
            }
        }
        
        with patch('builtins.open', mock_open()):
            with patch('yaml.safe_load', return_value=mock_yaml_data):
                result = read_config_yaml('config.yaml')
                
                assert result['database']['host'] == 'localhost'
                assert result['database']['port'] == 27017
                assert len(result['api']['endpoints']) == 2
