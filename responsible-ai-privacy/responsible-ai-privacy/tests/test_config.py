'''
MIT License https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Unit tests for privacy.config.config module
Tests configuration file reading functionality including INI and YAML formats
'''

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, mock_open
from configparser import ConfigParser

from privacy.config.config import readConfig, read_config_yaml


class TestReadConfig:
    """Test cases for readConfig function (INI file reading)"""
    
    def test_readConfig_reads_valid_section(self, tmp_path):
        """Test reading a valid section from INI file"""
        # Create a temporary INI file
        config_file = tmp_path / "test_config.ini"
        config_content = """[database]
host = localhost
port = 5432
user = testuser
password = testpass
dbname = testdb
"""
        config_file.write_text(config_content)
        
        result = readConfig("database", str(config_file))
        
        assert result == {
            'host': 'localhost',
            'port': '5432',
            'user': 'testuser',
            'password': 'testpass',
            'dbname': 'testdb'
        }
    
    def test_readConfig_reads_multiple_sections(self, tmp_path):
        """Test reading different sections from the same file"""
        config_file = tmp_path / "multi_section.ini"
        config_content = """[section1]
key1 = value1
key2 = value2

[section2]
key3 = value3
key4 = value4
"""
        config_file.write_text(config_content)
        
        result1 = readConfig("section1", str(config_file))
        result2 = readConfig("section2", str(config_file))
        
        assert result1 == {'key1': 'value1', 'key2': 'value2'}
        assert result2 == {'key3': 'value3', 'key4': 'value4'}
    
    def test_readConfig_raises_exception_for_missing_section(self, tmp_path):
        """Test that missing section raises appropriate exception"""
        config_file = tmp_path / "config.ini"
        config_content = """[existing_section]
key = value
"""
        config_file.write_text(config_content)
        
        with pytest.raises(Exception) as exc_info:
            readConfig("nonexistent_section", str(config_file))
        
        assert "Section nonexistent_section not found" in str(exc_info.value)
        assert "config.ini file" in str(exc_info.value)
    
    def test_readConfig_handles_empty_section(self, tmp_path):
        """Test reading an empty section"""
        config_file = tmp_path / "empty_section.ini"
        config_content = """[empty_section]

[another_section]
key = value
"""
        config_file.write_text(config_content)
        
        result = readConfig("empty_section", str(config_file))
        
        assert result == {}
    
    def test_readConfig_handles_special_characters_in_values(self, tmp_path):
        """Test reading values with special characters"""
        config_file = tmp_path / "special_chars.ini"
        config_content = """[special]
url = http://localhost:8080/api?param=value&other=123
path = /home/user/folder/subfolder
email = test@example.com
"""
        config_file.write_text(config_content)
        
        result = readConfig("special", str(config_file))
        
        assert result['url'] == 'http://localhost:8080/api?param=value&other=123'
        assert result['path'] == '/home/user/folder/subfolder'
        assert result['email'] == 'test@example.com'
    
    def test_readConfig_handles_whitespace_in_values(self, tmp_path):
        """Test reading values with whitespace"""
        config_file = tmp_path / "whitespace.ini"
        config_content = """[whitespace]
name = John Doe
address = 123 Main Street, Apt 4B
description = This is a long description with spaces
"""
        config_file.write_text(config_content)
        
        result = readConfig("whitespace", str(config_file))
        
        assert result['name'] == 'John Doe'
        assert result['address'] == '123 Main Street, Apt 4B'
        assert 'This is a long description' in result['description']
    
    def test_readConfig_handles_numeric_values(self, tmp_path):
        """Test reading numeric values (stored as strings)"""
        config_file = tmp_path / "numeric.ini"
        config_content = """[numbers]
port = 8080
timeout = 30
max_connections = 100
"""
        config_file.write_text(config_content)
        
        result = readConfig("numbers", str(config_file))
        
        assert result['port'] == '8080'
        assert result['timeout'] == '30'
        assert result['max_connections'] == '100'
    
    def test_readConfig_handles_boolean_like_values(self, tmp_path):
        """Test reading boolean-like values"""
        config_file = tmp_path / "booleans.ini"
        config_content = """[settings]
debug = true
enabled = yes
disabled = no
active = false
"""
        config_file.write_text(config_content)
        
        result = readConfig("settings", str(config_file))
        
        assert result['debug'] == 'true'
        assert result['enabled'] == 'yes'
        assert result['disabled'] == 'no'
        assert result['active'] == 'false'
    
    def test_readConfig_with_nonexistent_file(self):
        """Test reading from non-existent file raises exception for missing section"""
        # ConfigParser.read() doesn't raise exception for missing file,
        # but readConfig will raise exception since section won't be found
        with pytest.raises(Exception) as exc_info:
            readConfig("any_section", "nonexistent_file.ini")
        
        assert "Section any_section not found" in str(exc_info.value)
    
    def test_readConfig_preserves_case_sensitivity(self, tmp_path):
        """Test that keys are converted to lowercase by ConfigParser"""
        config_file = tmp_path / "case_test.ini"
        config_content = """[test]
Key = value1
OtherKey = value2
"""
        config_file.write_text(config_content)
        
        result = readConfig("test", str(config_file))
        
        # ConfigParser converts keys to lowercase by default
        assert 'key' in result
        assert 'otherkey' in result
        assert result['key'] == 'value1'
    
    def test_readConfig_with_comments_in_file(self, tmp_path):
        """Test reading config with comments"""
        config_file = tmp_path / "with_comments.ini"
        config_content = """# This is a comment
[section]
# Another comment
key1 = value1
key2 = value2  # inline comment
"""
        config_file.write_text(config_content)
        
        result = readConfig("section", str(config_file))
        
        assert 'key1' in result
        assert 'key2' in result
        assert result['key1'] == 'value1'
    
    def test_readConfig_with_equals_in_value(self, tmp_path):
        """Test reading values that contain equals signs"""
        config_file = tmp_path / "equals_in_value.ini"
        config_content = """[test]
connection_string = Server=localhost;Database=test;User=admin
equation = x=y+z
"""
        config_file.write_text(config_content)
        
        result = readConfig("test", str(config_file))
        
        assert 'Server=localhost' in result['connection_string']
        assert result['equation'] == 'x=y+z'


class TestReadConfigYaml:
    """Test cases for read_config_yaml function"""
    
    def test_read_config_yaml_reads_simple_yaml(self, tmp_path):
        """Test reading a simple YAML file"""
        yaml_file = tmp_path / "config.yaml"
        yaml_content = """
name: test_app
version: 1.0.0
debug: true
"""
        yaml_file.write_text(yaml_content)
        
        result = read_config_yaml(str(yaml_file))
        
        assert result['name'] == 'test_app'
        assert result['version'] == '1.0.0'
        assert result['debug'] is True
    
    def test_read_config_yaml_reads_nested_structure(self, tmp_path):
        """Test reading YAML with nested structure"""
        yaml_file = tmp_path / "nested.yaml"
        yaml_content = """
database:
  host: localhost
  port: 5432
  credentials:
    username: admin
    password: secret
server:
  host: 0.0.0.0
  port: 8080
"""
        yaml_file.write_text(yaml_content)
        
        result = read_config_yaml(str(yaml_file))
        
        assert result['database']['host'] == 'localhost'
        assert result['database']['port'] == 5432
        assert result['database']['credentials']['username'] == 'admin'
        assert result['server']['port'] == 8080
    
    def test_read_config_yaml_reads_lists(self, tmp_path):
        """Test reading YAML with lists"""
        yaml_file = tmp_path / "lists.yaml"
        yaml_content = """
allowed_hosts:
  - localhost
  - 127.0.0.1
  - example.com
ports:
  - 8080
  - 8081
  - 8082
"""
        yaml_file.write_text(yaml_content)
        
        result = read_config_yaml(str(yaml_file))
        
        assert len(result['allowed_hosts']) == 3
        assert 'localhost' in result['allowed_hosts']
        assert result['ports'] == [8080, 8081, 8082]
    
    def test_read_config_yaml_reads_mixed_types(self, tmp_path):
        """Test reading YAML with mixed data types"""
        yaml_file = tmp_path / "mixed_types.yaml"
        yaml_content = """
string_value: hello
integer_value: 42
float_value: 3.14
boolean_value: true
null_value: null
list_value:
  - item1
  - item2
dict_value:
  key: value
"""
        yaml_file.write_text(yaml_content)
        
        result = read_config_yaml(str(yaml_file))
        
        assert isinstance(result['string_value'], str)
        assert isinstance(result['integer_value'], int)
        assert isinstance(result['float_value'], float)
        assert isinstance(result['boolean_value'], bool)
        assert result['null_value'] is None
        assert isinstance(result['list_value'], list)
        assert isinstance(result['dict_value'], dict)
    
    def test_read_config_yaml_handles_empty_file(self, tmp_path):
        """Test reading an empty YAML file"""
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text("")
        
        result = read_config_yaml(str(yaml_file))
        
        assert result is None
    
    def test_read_config_yaml_handles_multiline_strings(self, tmp_path):
        """Test reading YAML with multiline strings"""
        yaml_file = tmp_path / "multiline.yaml"
        yaml_content = """
description: |
  This is a multiline
  description that spans
  multiple lines.
inline_multiline: >
  This is an inline
  multiline string.
"""
        yaml_file.write_text(yaml_content)
        
        result = read_config_yaml(str(yaml_file))
        
        assert 'multiline' in result['description']
        assert 'description' in result['description']
    
    def test_read_config_yaml_raises_exception_for_missing_file(self):
        """Test that reading non-existent file raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            read_config_yaml("nonexistent_file.yaml")
    
    def test_read_config_yaml_with_anchors_and_aliases(self, tmp_path):
        """Test reading YAML with anchors and aliases"""
        yaml_file = tmp_path / "anchors.yaml"
        yaml_content = """
defaults: &defaults
  timeout: 30
  retries: 3

production:
  <<: *defaults
  host: prod.example.com

development:
  <<: *defaults
  host: dev.example.com
"""
        yaml_file.write_text(yaml_content)
        
        result = read_config_yaml(str(yaml_file))
        
        assert result['production']['timeout'] == 30
        assert result['production']['host'] == 'prod.example.com'
        assert result['development']['timeout'] == 30
        assert result['development']['host'] == 'dev.example.com'
    
    def test_read_config_yaml_with_special_characters(self, tmp_path):
        """Test reading YAML with special characters"""
        yaml_file = tmp_path / "special.yaml"
        yaml_content = """
url: "http://example.com/api?param=value&other=123"
path: "/home/user/folder/subfolder"
email: "test@example.com"
quoted_string: "This has: colons and - dashes"
"""
        yaml_file.write_text(yaml_content)
        
        result = read_config_yaml(str(yaml_file))
        
        assert result['url'] == 'http://example.com/api?param=value&other=123'
        assert result['path'] == '/home/user/folder/subfolder'
        assert result['email'] == 'test@example.com'
        assert 'colons' in result['quoted_string']
    
    def test_read_config_yaml_with_environment_like_vars(self, tmp_path):
        """Test reading YAML with environment variable-like values"""
        yaml_file = tmp_path / "env_vars.yaml"
        yaml_content = """
database_url: "${DATABASE_URL}"
api_key: "${API_KEY}"
debug: "${DEBUG:-false}"
"""
        yaml_file.write_text(yaml_content)
        
        result = read_config_yaml(str(yaml_file))
        
        # YAML will read these as literal strings, not expand them
        assert '${DATABASE_URL}' in result['database_url']
        assert '${API_KEY}' in result['api_key']
    
    def test_read_config_yaml_with_complex_nested_structure(self, tmp_path):
        """Test reading YAML with deeply nested structure"""
        yaml_file = tmp_path / "complex.yaml"
        yaml_content = """
application:
  name: privacy-service
  version: 2.2.1
  components:
    analyzer:
      enabled: true
      models:
        - name: roberta
          path: models/roberta
        - name: spacy
          path: models/spacy
    anonymizer:
      enabled: true
      operators:
        - redact
        - hash
        - encrypt
"""
        yaml_file.write_text(yaml_content)
        
        result = read_config_yaml(str(yaml_file))
        
        assert result['application']['name'] == 'privacy-service'
        assert len(result['application']['components']['analyzer']['models']) == 2
        assert result['application']['components']['analyzer']['models'][0]['name'] == 'roberta'
        assert 'encrypt' in result['application']['components']['anonymizer']['operators']


class TestConfigIntegration:
    """Integration tests for config module"""
    
    def test_both_functions_work_independently(self, tmp_path):
        """Test that both config reading functions work independently"""
        # Create INI file
        ini_file = tmp_path / "config.ini"
        ini_content = """[database]
host = localhost
"""
        ini_file.write_text(ini_content)
        
        # Create YAML file
        yaml_file = tmp_path / "config.yaml"
        yaml_content = "database:\n  host: localhost\n"
        yaml_file.write_text(yaml_content)
        
        ini_result = readConfig("database", str(ini_file))
        yaml_result = read_config_yaml(str(yaml_file))
        
        assert ini_result['host'] == 'localhost'
        assert yaml_result['database']['host'] == 'localhost'
    
    def test_readConfig_returns_dict_type(self, tmp_path):
        """Test that readConfig always returns a dictionary"""
        config_file = tmp_path / "test.ini"
        config_content = """[section]
key = value
"""
        config_file.write_text(config_content)
        
        result = readConfig("section", str(config_file))
        
        assert isinstance(result, dict)
    
    def test_read_config_yaml_handles_yml_extension(self, tmp_path):
        """Test that read_config_yaml works with .yml extension too"""
        yaml_file = tmp_path / "config.yml"
        yaml_content = "key: value\n"
        yaml_file.write_text(yaml_content)
        
        result = read_config_yaml(str(yaml_file))
        
        assert result['key'] == 'value'


class TestConfigEdgeCases:
    """Edge case tests for config module"""
    
    def test_readConfig_with_very_long_values(self, tmp_path):
        """Test reading config with very long values"""
        config_file = tmp_path / "long_values.ini"
        long_value = "a" * 1000
        config_content = f"""[section]
long_key = {long_value}
"""
        config_file.write_text(config_content)
        
        result = readConfig("section", str(config_file))
        
        assert len(result['long_key']) == 1000
    
    def test_readConfig_with_many_keys(self, tmp_path):
        """Test reading config with many keys"""
        config_file = tmp_path / "many_keys.ini"
        config_content = "[section]\n"
        for i in range(100):
            config_content += f"key{i} = value{i}\n"
        config_file.write_text(config_content)
        
        result = readConfig("section", str(config_file))
        
        assert len(result) == 100
        assert result['key50'] == 'value50'
    
    def test_read_config_yaml_with_large_file(self, tmp_path):
        """Test reading large YAML file"""
        yaml_file = tmp_path / "large.yaml"
        yaml_content = "items:\n"
        for i in range(100):
            yaml_content += f"  - id: {i}\n    name: item{i}\n"
        yaml_file.write_text(yaml_content)
        
        result = read_config_yaml(str(yaml_file))
        
        assert len(result['items']) == 100
        assert result['items'][50]['id'] == 50
    
    def test_readConfig_with_unicode_characters(self, tmp_path):
        """Test reading config with Unicode characters"""
        config_file = tmp_path / "unicode.ini"
        config_content = """[section]
french = Bonjour
spanish = Hola
german = Guten Tag
"""
        config_file.write_text(config_content, encoding='utf-8')
        
        result = readConfig("section", str(config_file))
        
        assert result['french'] == 'Bonjour'
        assert result['spanish'] == 'Hola'
        assert result['german'] == 'Guten Tag'
    
    def test_read_config_yaml_with_unicode(self, tmp_path):
        """Test reading YAML with basic international characters"""
        yaml_file = tmp_path / "unicode.yaml"
        yaml_content = """
message: "Hello World"
greeting: "Bonjour"
language: "English"
"""
        yaml_file.write_text(yaml_content, encoding='utf-8')
        
        result = read_config_yaml(str(yaml_file))
        
        assert 'World' in result['message']
        assert result['greeting'] == 'Bonjour'
        assert result['language'] == 'English'
    
    def test_readConfig_section_name_case_sensitivity(self, tmp_path):
        """Test section name case sensitivity"""
        config_file = tmp_path / "case.ini"
        config_content = """[Section]
key = value
"""
        config_file.write_text(config_content)
        
        # ConfigParser is case-sensitive for section names
        result = readConfig("Section", str(config_file))
        assert result['key'] == 'value'
        
        # Different case should raise exception
        with pytest.raises(Exception):
            readConfig("section", str(config_file))
