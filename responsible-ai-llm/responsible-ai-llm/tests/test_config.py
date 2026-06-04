'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import pytest
import sys
import os
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from llm.config.config import readConfig, read_config_yaml


class TestReadConfig:
    """Test suite for readConfig function"""
    
    def test_readConfig_valid_section(self):
        """Test reading valid configuration section"""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("[postgresql]\n")
            f.write("user=testuser\n")
            f.write("password=testpass\n")
            f.write("host=localhost\n")
            temp_file = f.name
        
        try:
            result = readConfig('postgresql', temp_file)
            assert isinstance(result, dict)
            assert result['user'] == 'testuser'
            assert result['password'] == 'testpass'
            assert result['host'] == 'localhost'
        finally:
            os.unlink(temp_file)
    
    def test_readConfig_invalid_section(self):
        """Test reading non-existent section raises exception"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("[postgresql]\n")
            f.write("user=testuser\n")
            temp_file = f.name
        
        try:
            with pytest.raises(Exception) as exc_info:
                readConfig('nonexistent', temp_file)
            assert 'Section nonexistent not found' in str(exc_info.value)
        finally:
            os.unlink(temp_file)
    
    def test_readConfig_multiple_options(self):
        """Test reading multiple configuration options"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("[database]\n")
            f.write("host=localhost\n")
            f.write("port=5432\n")
            f.write("username=admin\n")
            f.write("password=secret123\n")
            f.write("database=mydb\n")
            temp_file = f.name
        
        try:
            result = readConfig('database', temp_file)
            assert len(result) == 5
            assert result['host'] == 'localhost'
            assert result['port'] == '5432'
            assert result['username'] == 'admin'
            assert result['password'] == 'secret123'
            assert result['database'] == 'mydb'
        finally:
            os.unlink(temp_file)


class TestReadConfigYaml:
    """Test suite for read_config_yaml function"""
    
    def test_read_config_yaml_valid_file(self):
        """Test reading valid YAML configuration file"""
        config_data = {
            'title': 'LLM API',
            'description': 'Large Language Model API',
            'version': '1.0.0',
            'openapi_url': '/openapi.json'
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.safe_dump(config_data, f)
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            assert isinstance(result, dict)
            assert result['title'] == 'LLM API'
            assert result['description'] == 'Large Language Model API'
            assert result['version'] == '1.0.0'
            assert result['openapi_url'] == '/openapi.json'
        finally:
            os.unlink(temp_file)
    
    def test_read_config_yaml_nested_structure(self):
        """Test reading YAML file with nested structure"""
        config_data = {
            'app': {
                'name': 'LLM Service',
                'debug': True,
                'port': 8000
            },
            'database': {
                'host': 'localhost',
                'port': 5432
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.safe_dump(config_data, f)
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            assert result['app']['name'] == 'LLM Service'
            assert result['app']['debug'] is True
            assert result['app']['port'] == 8000
            assert result['database']['host'] == 'localhost'
        finally:
            os.unlink(temp_file)
    
    def test_read_config_yaml_empty_file(self):
        """Test reading empty YAML file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('')
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            assert result is None
        finally:
            os.unlink(temp_file)
    
    def test_read_config_yaml_with_list(self):
        """Test reading YAML file with list structure"""
        config_data = {
            'servers': [
                {'url': 'http://localhost:8000'},
                {'url': 'http://production:8000'}
            ],
            'features': ['image_generation', 'text_completion']
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.safe_dump(config_data, f)
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            assert len(result['servers']) == 2
            assert result['servers'][0]['url'] == 'http://localhost:8000'
            assert 'image_generation' in result['features']
        finally:
            os.unlink(temp_file)


class TestConfigIntegration:
    """Integration tests for configuration module"""
    
    def test_config_yaml_with_different_types(self):
        """Test YAML configuration with various data types"""
        config_data = {
            'string_value': 'test',
            'int_value': 42,
            'float_value': 3.14,
            'bool_value': True,
            'null_value': None,
            'list_value': [1, 2, 3],
            'dict_value': {'key': 'value'}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.safe_dump(config_data, f)
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            assert result['string_value'] == 'test'
            assert result['int_value'] == 42
            assert result['float_value'] == 3.14
            assert result['bool_value'] is True
            assert result['null_value'] is None
            assert result['list_value'] == [1, 2, 3]
            assert result['dict_value']['key'] == 'value'
        finally:
            os.unlink(temp_file)
    
    def test_readConfig_empty_section(self):
        """Test reading empty configuration section"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("[empty_section]\n")
            temp_file = f.name
        
        try:
            result = readConfig('empty_section', temp_file)
            assert isinstance(result, dict)
            assert len(result) == 0
        finally:
            os.unlink(temp_file)
