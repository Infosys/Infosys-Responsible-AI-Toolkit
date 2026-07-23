"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Unit tests for config.py
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from configparser import ConfigParser
import yaml


@pytest.mark.unit
class TestConfigFunctions:
    """Test cases for config utility functions"""

    def test_read_config_success(self):
        """Test successful config reading"""
        from rai_admin.config.config import read_config
        
        config_content = """[mongodb]
host = localhost
port = 27017
database = test_db
"""
        
        with patch("builtins.open", mock_open(read_data=config_content)):
            with patch.object(ConfigParser, 'read'):
                parser = ConfigParser()
                parser.read_string(config_content)
                
                with patch('rai_admin.config.config.ConfigParser', return_value=parser):
                    result = read_config('mongodb', 'test_config.ini')
                    
                    assert 'host' in result
                    assert result['host'] == 'localhost'
                    assert result['port'] == '27017'

    def test_read_config_section_not_found(self):
        """Test config reading with non-existent section"""
        from rai_admin.config.config import read_config, ConfigSectionNotFoundError
        
        config_content = """[mongodb]
host = localhost
"""
        
        with patch("builtins.open", mock_open(read_data=config_content)):
            with patch.object(ConfigParser, 'read'):
                parser = ConfigParser()
                parser.read_string(config_content)
                
                with patch('rai_admin.config.config.ConfigParser', return_value=parser):
                    with pytest.raises(ConfigSectionNotFoundError):
                        read_config('nonexistent', 'test_config.ini')

    def test_read_config_yaml_success(self):
        """Test successful YAML config reading"""
        from rai_admin.config.config import read_config_yaml
        
        yaml_content = """
title: Test API
version: 1.0.0
openapi_url: /openapi.json
"""
        
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            result = read_config_yaml('test_config.yaml')
            
            assert result['title'] == 'Test API'
            assert result['version'] == '1.0.0'
            assert result['openapi_url'] == '/openapi.json'

    def test_read_config_yaml_empty_file(self):
        """Test YAML config reading with empty file"""
        from rai_admin.config.config import read_config_yaml
        
        with patch("builtins.open", mock_open(read_data="")):
            result = read_config_yaml('empty.yaml')
            
            assert result is None

    def test_read_config_yaml_with_nested_structure(self):
        """Test YAML config reading with nested structure"""
        from rai_admin.config.config import read_config_yaml
        
        yaml_content = """
database:
  host: localhost
  port: 27017
  credentials:
    username: admin
    password: secret
"""
        
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            result = read_config_yaml('config.yaml')
            
            assert 'database' in result
            assert result['database']['host'] == 'localhost'
            assert result['database']['credentials']['username'] == 'admin'

    def test_backward_compatibility_readConfig(self):
        """Test backward compatibility of readConfig function"""
        from rai_admin.config import config
        
        # Verify that readConfig is an alias for read_config
        assert hasattr(config, 'readConfig')
        assert config.readConfig == config.read_config


@pytest.mark.unit
class TestConfigSectionNotFoundError:
    """Test cases for ConfigSectionNotFoundError exception"""

    def test_exception_message(self):
        """Test exception message formatting"""
        from rai_admin.config.config import ConfigSectionNotFoundError
        
        section = "test_section"
        filename = "test.ini"
        
        error = ConfigSectionNotFoundError(f'Section {section} not found in the {filename} file')
        
        assert str(error) == f'Section {section} not found in the {filename} file'

    def test_exception_inheritance(self):
        """Test that ConfigSectionNotFoundError inherits from Exception"""
        from rai_admin.config.config import ConfigSectionNotFoundError
        
        assert issubclass(ConfigSectionNotFoundError, Exception)
