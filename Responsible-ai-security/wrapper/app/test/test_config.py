'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024-2025 Infosys Ltd.
'''

import pytest
import os
import tempfile
import yaml
from configparser import ConfigParser
from unittest.mock import patch, MagicMock, mock_open
from src.config.config import readConfig, read_config_yaml


class TestConfigModule:
    """Test cases for config.py module"""

    def test_readConfig_success(self):
        """Test readConfig with valid section and file"""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as f:
            f.write('[database]\n')
            f.write('host=localhost\n')
            f.write('port=5432\n')
            f.write('user=testuser\n')
            temp_file = f.name
        
        try:
            result = readConfig('database', temp_file)
            assert result == {'host': 'localhost', 'port': '5432', 'user': 'testuser'}
        finally:
            os.unlink(temp_file)

    def test_readConfig_missing_section(self):
        """Test readConfig with missing section raises exception"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as f:
            f.write('[database]\n')
            f.write('host=localhost\n')
            temp_file = f.name
        
        try:
            with pytest.raises(Exception) as exc_info:
                readConfig('nonexistent', temp_file)
            assert 'not found' in str(exc_info.value)
        finally:
            os.unlink(temp_file)

    def test_readConfig_empty_section(self):
        """Test readConfig with empty section"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as f:
            f.write('[empty_section]\n')
            temp_file = f.name
        
        try:
            result = readConfig('empty_section', temp_file)
            assert result == {}
        finally:
            os.unlink(temp_file)

    def test_readConfig_multiple_sections(self):
        """Test readConfig with multiple sections"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as f:
            f.write('[section1]\n')
            f.write('key1=value1\n')
            f.write('[section2]\n')
            f.write('key2=value2\n')
            temp_file = f.name
        
        try:
            result = readConfig('section2', temp_file)
            assert result == {'key2': 'value2'}
        finally:
            os.unlink(temp_file)

    def test_readConfig_special_characters(self):
        """Test readConfig with special characters in values"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as f:
            f.write('[test]\n')
            f.write('path=/var/log/app.log\n')
            f.write('url=http://localhost:8000/api\n')
            temp_file = f.name
        
        try:
            result = readConfig('test', temp_file)
            assert result['path'] == '/var/log/app.log'
            assert result['url'] == 'http://localhost:8000/api'
        finally:
            os.unlink(temp_file)

    def test_read_config_yaml_success(self):
        """Test read_config_yaml with valid YAML file"""
        yaml_content = {
            'database': {'host': 'localhost', 'port': 5432},
            'api': {'endpoint': '/api/v1', 'timeout': 30}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            yaml.dump(yaml_content, f)
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            assert result == yaml_content
            assert result['database']['host'] == 'localhost'
            assert result['api']['timeout'] == 30
        finally:
            os.unlink(temp_file)

    def test_read_config_yaml_empty_file(self):
        """Test read_config_yaml with empty YAML file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            assert result is None
        finally:
            os.unlink(temp_file)

    def test_read_config_yaml_nested_structure(self):
        """Test read_config_yaml with nested YAML structure"""
        yaml_content = {
            'app': {
                'name': 'security_api',
                'version': '1.0',
                'config': {
                    'database': {
                        'host': 'localhost',
                        'port': 5432
                    },
                    'cache': {
                        'enabled': True,
                        'ttl': 3600
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            yaml.dump(yaml_content, f)
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            assert result['app']['name'] == 'security_api'
            assert result['app']['config']['database']['port'] == 5432
            assert result['app']['config']['cache']['enabled'] is True
        finally:
            os.unlink(temp_file)

    def test_read_config_yaml_list_values(self):
        """Test read_config_yaml with list values"""
        yaml_content = {
            'servers': ['server1', 'server2', 'server3'],
            'ports': [8000, 8001, 8002]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            yaml.dump(yaml_content, f)
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            assert len(result['servers']) == 3
            assert result['servers'][0] == 'server1'
            assert result['ports'][2] == 8002
        finally:
            os.unlink(temp_file)

    def test_read_config_yaml_boolean_values(self):
        """Test read_config_yaml with boolean values"""
        yaml_content = {
            'features': {
                'auth': True,
                'cache': False,
                'logging': True
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            yaml.dump(yaml_content, f)
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            assert result['features']['auth'] is True
            assert result['features']['cache'] is False
        finally:
            os.unlink(temp_file)

    def test_read_config_yaml_file_not_found(self):
        """Test read_config_yaml with non-existent file"""
        with pytest.raises(FileNotFoundError):
            read_config_yaml('/nonexistent/path/config.yaml')

    def test_readConfig_file_not_found(self):
        """Test readConfig with non-existent file"""
        # ConfigParser.read() doesn't raise exception for missing file
        # but the section won't exist
        with pytest.raises(Exception) as exc_info:
            readConfig('anysection', '/nonexistent/file.ini')
        assert 'not found' in str(exc_info.value)
