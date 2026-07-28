"""
Unit tests for config module
Tests the configuration and logger functionality
"""
import pytest
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from image_explain.config.config import readConfig, read_config_yaml


class TestReadConfig:
    """Test suite for readConfig function"""
    
    def test_readconfig_valid_section(self):
        """Test reading a valid configuration section"""
        config_content = """[logDetails]
file_name = test.log
verbose = True
log_dir = ./logs
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(config_content)
            f.flush()
            temp_file = f.name
        
        try:
            result = readConfig('logDetails', temp_file)
            assert isinstance(result, dict)
            assert 'file_name' in result
            assert result['file_name'] == 'test.log'
        finally:
            os.unlink(temp_file)
    
    def test_readconfig_multiple_options(self):
        """Test reading configuration with multiple options"""
        config_content = """[logDetails]
file_name = app.log
verbose = True
log_dir = ./logs
user_id = 12345
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(config_content)
            f.flush()
            temp_file = f.name
        
        try:
            result = readConfig('logDetails', temp_file)
            assert len(result) >= 3
            assert result['file_name'] == 'app.log'
            assert result['verbose'] == 'True'
        finally:
            os.unlink(temp_file)
    
    def test_readconfig_missing_section(self):
        """Test reading non-existent section raises exception"""
        config_content = """[existing]
key = value
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(config_content)
            f.flush()
            temp_file = f.name
        
        try:
            with pytest.raises(Exception) as exc_info:
                readConfig('non_existent', temp_file)
            assert 'not found' in str(exc_info.value)
        finally:
            os.unlink(temp_file)


class TestReadConfigYaml:
    """Test suite for read_config_yaml function"""
    
    def test_read_config_yaml_valid_file(self):
        """Test reading a valid YAML configuration file"""
        yaml_content = """title: "Test API"
version: "1.0.0"
description: "Test Description"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            assert isinstance(result, dict)
            assert result['title'] == 'Test API'
            assert result['version'] == '1.0.0'
        finally:
            os.unlink(temp_file)
    
    def test_read_config_yaml_nested_structure(self):
        """Test reading YAML with nested structure"""
        yaml_content = """app:
  name: TestApp
  version: 1.0
  settings:
    debug: true
    timeout: 30
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            assert isinstance(result, dict)
            assert 'app' in result
            assert result['app']['name'] == 'TestApp'
            assert result['app']['settings']['debug'] is True
        finally:
            os.unlink(temp_file)
    
    def test_read_config_yaml_empty_file(self):
        """Test reading empty YAML file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")
            f.flush()
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            assert result is None
        finally:
            os.unlink(temp_file)
    
    def test_read_config_yaml_with_list(self):
        """Test reading YAML with list structure"""
        yaml_content = """servers:
  - name: server1
    port: 8000
  - name: server2
    port: 8001
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            assert isinstance(result['servers'], list)
            assert len(result['servers']) == 2
            assert result['servers'][0]['name'] == 'server1'
        finally:
            os.unlink(temp_file)
