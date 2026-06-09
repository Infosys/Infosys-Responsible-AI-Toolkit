"""
Unit tests for config module.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, mock_open
from configparser import ConfigParser
import tempfile
import yaml

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app.config.config import readConfig, read_config_yaml


class TestReadConfig:
    """Tests for readConfig function."""
    
    def test_read_config_success(self):
        # Create a temporary config file
        config_content = """[database]
host = localhost
port = 5432
user = testuser
password = testpass
"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as f:
            f.write(config_content)
            config_file = f.name
        
        try:
            result = readConfig('database', config_file)
            
            assert result['host'] == 'localhost'
            assert result['port'] == '5432'
            assert result['user'] == 'testuser'
            assert result['password'] == 'testpass'
        finally:
            os.unlink(config_file)
    
    def test_read_config_multiple_sections(self):
        config_content = """[section1]
key1 = value1
key2 = value2

[section2]
key3 = value3
key4 = value4
"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as f:
            f.write(config_content)
            config_file = f.name
        
        try:
            result1 = readConfig('section1', config_file)
            result2 = readConfig('section2', config_file)
            
            assert result1['key1'] == 'value1'
            assert result2['key3'] == 'value3'
        finally:
            os.unlink(config_file)
    
    def test_read_config_section_not_found(self):
        config_content = """[existing_section]
key = value
"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as f:
            f.write(config_content)
            config_file = f.name
        
        try:
            with pytest.raises(Exception) as exc_info:
                readConfig('nonexistent_section', config_file)
            
            assert 'not found' in str(exc_info.value)
        finally:
            os.unlink(config_file)
    
    def test_read_config_empty_section(self):
        config_content = """[empty_section]

[another_section]
key = value
"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as f:
            f.write(config_content)
            config_file = f.name
        
        try:
            result = readConfig('empty_section', config_file)
            assert result == {}
        finally:
            os.unlink(config_file)
    
    def test_read_config_with_special_characters(self):
        config_content = """[special]
url = http://example.com:8080/path?query=value
path = /home/user/data
"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as f:
            f.write(config_content)
            config_file = f.name
        
        try:
            result = readConfig('special', config_file)
            assert 'http://example.com' in result['url']
            assert result['path'] == '/home/user/data'
        finally:
            os.unlink(config_file)


class TestReadConfigYaml:
    """Tests for read_config_yaml function."""
    
    def test_read_config_yaml_success(self):
        yaml_content = """
database:
  host: localhost
  port: 27017
  name: testdb
  
settings:
  debug: true
  timeout: 30
"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            f.write(yaml_content)
            yaml_file = f.name
        
        try:
            result = read_config_yaml(yaml_file)
            
            assert result['database']['host'] == 'localhost'
            assert result['database']['port'] == 27017
            assert result['settings']['debug'] is True
            assert result['settings']['timeout'] == 30
        finally:
            os.unlink(yaml_file)
    
    def test_read_config_yaml_nested_structure(self):
        yaml_content = """
app:
  name: TestApp
  version: 1.0
  features:
    - feature1
    - feature2
    - feature3
  config:
    nested:
      key: value
"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            f.write(yaml_content)
            yaml_file = f.name
        
        try:
            result = read_config_yaml(yaml_file)
            
            assert result['app']['name'] == 'TestApp'
            assert len(result['app']['features']) == 3
            assert result['app']['config']['nested']['key'] == 'value'
        finally:
            os.unlink(yaml_file)
    
    def test_read_config_yaml_list_values(self):
        yaml_content = """
items:
  - name: item1
    value: 100
  - name: item2
    value: 200
"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            f.write(yaml_content)
            yaml_file = f.name
        
        try:
            result = read_config_yaml(yaml_file)
            
            assert len(result['items']) == 2
            assert result['items'][0]['name'] == 'item1'
            assert result['items'][1]['value'] == 200
        finally:
            os.unlink(yaml_file)
    
    def test_read_config_yaml_empty_file(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            f.write('')
            yaml_file = f.name
        
        try:
            result = read_config_yaml(yaml_file)
            assert result is None
        finally:
            os.unlink(yaml_file)
    
    def test_read_config_yaml_boolean_and_null(self):
        yaml_content = """
flags:
  enabled: true
  disabled: false
  nullable: null
"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            f.write(yaml_content)
            yaml_file = f.name
        
        try:
            result = read_config_yaml(yaml_file)
            
            assert result['flags']['enabled'] is True
            assert result['flags']['disabled'] is False
            assert result['flags']['nullable'] is None
        finally:
            os.unlink(yaml_file)
