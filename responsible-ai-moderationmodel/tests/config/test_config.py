"""
Unit tests for config module.
Tests configuration file reading utilities.
"""
import pytest
from unittest.mock import Mock, patch, mock_open
import tempfile
import os


class TestReadConfig:
    """Test cases for read_config function."""

    def test_read_config_valid_section(self):
        """Test reading a valid section from config file."""
        from config.config import read_config
        
        # Create a temporary config file
        config_content = """[postgresql]
host=localhost
port=5432
database=testdb
user=admin
password=secret123
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(config_content)
            temp_file = f.name
        
        try:
            result = read_config('postgresql', temp_file)
            
            assert result['host'] == 'localhost'
            assert result['port'] == '5432'
            assert result['database'] == 'testdb'
            assert result['user'] == 'admin'
            assert result['password'] == 'secret123'
        finally:
            os.unlink(temp_file)

    def test_read_config_section_not_found(self):
        """Test that ConfigSectionNotFoundError is raised when section doesn't exist."""
        from config.config import read_config
        from exception.exception import ConfigSectionNotFoundError
        
        config_content = """[section1]
key1=value1
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(config_content)
            temp_file = f.name
        
        try:
            with pytest.raises(ConfigSectionNotFoundError) as exc_info:
                read_config('nonexistent_section', temp_file)
            
            assert 'nonexistent_section' in str(exc_info.value)
            assert 'not found' in str(exc_info.value)
        finally:
            os.unlink(temp_file)

    def test_read_config_multiple_sections(self):
        """Test reading from a config file with multiple sections."""
        from config.config import read_config
        
        config_content = """[section1]
key1=value1
key2=value2

[section2]
key3=value3
key4=value4
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(config_content)
            temp_file = f.name
        
        try:
            result1 = read_config('section1', temp_file)
            result2 = read_config('section2', temp_file)
            
            assert result1['key1'] == 'value1'
            assert result1['key2'] == 'value2'
            assert result2['key3'] == 'value3'
            assert result2['key4'] == 'value4'
        finally:
            os.unlink(temp_file)

    def test_read_config_empty_section(self):
        """Test reading an empty section."""
        from config.config import read_config
        
        config_content = """[empty_section]

[section_with_data]
key=value
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(config_content)
            temp_file = f.name
        
        try:
            result = read_config('empty_section', temp_file)
            assert result == {}
        finally:
            os.unlink(temp_file)

    def test_read_config_special_characters(self):
        """Test reading config values with special characters."""
        from config.config import read_config
        
        config_content = """[test]
url=https://example.com:8080/path?param=value
connection_string=Server=localhost;Database=test;User Id=admin;Password=p@ss!
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(config_content)
            temp_file = f.name
        
        try:
            result = read_config('test', temp_file)
            assert 'https://example.com' in result['url']
            assert 'p@ss!' in result['connection_string']
        finally:
            os.unlink(temp_file)


class TestReadConfigYaml:
    """Test cases for read_config_yaml function."""

    def test_read_config_yaml_valid(self):
        """Test reading a valid YAML config file."""
        from config.config import read_config_yaml
        
        yaml_content = """
database:
  host: localhost
  port: 5432
  name: testdb

application:
  debug: true
  max_connections: 100
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            
            assert result['database']['host'] == 'localhost'
            assert result['database']['port'] == 5432
            assert result['database']['name'] == 'testdb'
            assert result['application']['debug'] is True
            assert result['application']['max_connections'] == 100
        finally:
            os.unlink(temp_file)

    def test_read_config_yaml_nested_structure(self):
        """Test reading YAML with nested structure."""
        from config.config import read_config_yaml
        
        yaml_content = """
level1:
  level2:
    level3:
      key: value
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            assert result['level1']['level2']['level3']['key'] == 'value'
        finally:
            os.unlink(temp_file)

    def test_read_config_yaml_list(self):
        """Test reading YAML with lists."""
        from config.config import read_config_yaml
        
        yaml_content = """
services:
  - name: service1
    port: 8001
  - name: service2
    port: 8002
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            
            assert len(result['services']) == 2
            assert result['services'][0]['name'] == 'service1'
            assert result['services'][0]['port'] == 8001
            assert result['services'][1]['name'] == 'service2'
            assert result['services'][1]['port'] == 8002
        finally:
            os.unlink(temp_file)

    def test_read_config_yaml_empty_file(self):
        """Test reading an empty YAML file."""
        from config.config import read_config_yaml
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            assert result is None
        finally:
            os.unlink(temp_file)

    def test_read_config_yaml_boolean_values(self):
        """Test reading YAML with boolean values."""
        from config.config import read_config_yaml
        
        yaml_content = """
flags:
  enabled: true
  disabled: false
  yes_value: yes
  no_value: no
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            
            assert result['flags']['enabled'] is True
            assert result['flags']['disabled'] is False
            assert result['flags']['yes_value'] is True
            assert result['flags']['no_value'] is False
        finally:
            os.unlink(temp_file)

    def test_read_config_yaml_numeric_values(self):
        """Test reading YAML with various numeric values."""
        from config.config import read_config_yaml
        
        yaml_content = """
numbers:
  integer: 42
  float: 3.14
  negative: -10
  scientific: 1.23e-4
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            
            assert result['numbers']['integer'] == 42
            assert result['numbers']['float'] == 3.14
            assert result['numbers']['negative'] == -10
            assert abs(result['numbers']['scientific'] - 0.000123) < 0.0000001
        finally:
            os.unlink(temp_file)

    def test_read_config_yaml_string_values(self):
        """Test reading YAML with string values."""
        from config.config import read_config_yaml
        
        yaml_content = """
strings:
  simple: hello
  quoted: "hello world"
  with_colon: "key: value"
  multiline: |
    This is
    a multiline
    string
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            
            assert result['strings']['simple'] == 'hello'
            assert result['strings']['quoted'] == 'hello world'
            assert result['strings']['with_colon'] == 'key: value'
            assert 'multiline' in result['strings']['multiline']
        finally:
            os.unlink(temp_file)

    def test_read_config_yaml_file_not_found(self):
        """Test that appropriate error is raised when file doesn't exist."""
        from config.config import read_config_yaml
        
        with pytest.raises(FileNotFoundError):
            read_config_yaml('nonexistent_file.yaml')

    def test_read_config_yaml_invalid_yaml(self):
        """Test handling of invalid YAML syntax."""
        from config.config import read_config_yaml
        import yaml
        
        # Use YAML that will actually raise a ParserError
        yaml_content = """key: value
  invalid: indentation
    nested: badly
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            with pytest.raises(yaml.YAMLError):
                read_config_yaml(temp_file)
        finally:
            os.unlink(temp_file)
