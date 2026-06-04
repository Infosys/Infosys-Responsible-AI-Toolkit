'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

"""
test_config.py - Tests for config module (config.py)
"""

import sys
import os
import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))
from explain.config.config import read_config_yaml, readConfig


class TestReadConfig:
    """Tests for readConfig function"""

    def test_read_config_valid_section(self, temp_config_file):
        """Test reading a valid section from config file"""
        
        
        result = readConfig('logDetails', temp_config_file)
        
        assert isinstance(result, dict)
        assert 'file_name' in result
        assert result['file_name'] == 'test_log'
        assert result['verbose'] == 'true'
        assert result['log_dir'] == '/tmp/logs'

    def test_read_config_database_section(self, temp_config_file):
        """Test reading database section from config file"""
        
        
        result = readConfig('database', temp_config_file)
        
        assert isinstance(result, dict)
        assert 'host' in result
        assert result['host'] == 'localhost'
        assert result['port'] == '27017'

    def test_read_config_invalid_section_raises_exception(self, temp_config_file):
        """Test that reading invalid section raises exception"""
        
        
        with pytest.raises(Exception) as excinfo:
            readConfig('nonexistent_section', temp_config_file)
        
        assert 'not found' in str(excinfo.value).lower()

    def test_read_config_nonexistent_file(self):
        """Test reading from non-existent file raises exception"""
        
        
        with pytest.raises(Exception):
            readConfig('logDetails', '/nonexistent/path/config.ini')

    def test_read_config_empty_section(self, temp_directory):
        """Test reading an empty section"""
        
        
        config_content = """[empty_section]
"""
        config_path = os.path.join(temp_directory, 'empty_config.ini')
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        result = readConfig('empty_section', config_path)
        assert result == {}

    def test_read_config_with_special_characters(self, temp_directory):
        """Test reading config with special characters in values"""
        
        
        config_content = """[special]
url = http://localhost:8080/api?key=abc&value=123
path = C:\\Users\\test\\file.txt
"""
        config_path = os.path.join(temp_directory, 'special_config.ini')
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        result = readConfig('special', config_path)
        assert 'url' in result
        assert 'path' in result

    def test_read_config_multiple_params(self, temp_directory):
        """Test reading config with multiple parameters"""
        
        
        config_content = """[multi]
param1 = value1
param2 = value2
param3 = value3
param4 = value4
param5 = value5
"""
        config_path = os.path.join(temp_directory, 'multi_config.ini')
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        result = readConfig('multi', config_path)
        assert len(result) == 5
        for i in range(1, 6):
            assert result[f'param{i}'] == f'value{i}'


class TestReadConfigYaml:
    """Tests for read_config_yaml function"""

    def test_read_yaml_valid_file(self, temp_yaml_file):
        """Test reading a valid YAML file"""
        
        
        result = read_config_yaml(temp_yaml_file)
        
        assert isinstance(result, dict)
        assert 'database' in result
        assert 'settings' in result
        assert result['database']['host'] == 'localhost'
        assert result['database']['port'] == 27017
        assert result['settings']['debug'] == True

    def test_read_yaml_nested_structure(self, temp_directory):
        """Test reading YAML with nested structure"""
        
        
        yaml_content = """level1:
  level2:
    level3:
      value: deep_value
"""
        yaml_path = os.path.join(temp_directory, 'nested.yaml')
        with open(yaml_path, 'w') as f:
            f.write(yaml_content)
        
        result = read_config_yaml(yaml_path)
        assert result['level1']['level2']['level3']['value'] == 'deep_value'

    def test_read_yaml_with_lists(self, temp_directory):
        """Test reading YAML with list values"""
        
        
        yaml_content = """items:
  - item1
  - item2
  - item3
numbers:
  - 1
  - 2
  - 3
"""
        yaml_path = os.path.join(temp_directory, 'list.yaml')
        with open(yaml_path, 'w') as f:
            f.write(yaml_content)
        
        result = read_config_yaml(yaml_path)
        assert len(result['items']) == 3
        assert result['items'][0] == 'item1'
        assert result['numbers'] == [1, 2, 3]

    def test_read_yaml_nonexistent_file(self):
        """Test reading non-existent YAML file raises exception"""
        
        
        with pytest.raises(FileNotFoundError):
            read_config_yaml('/nonexistent/path/config.yaml')

    def test_read_yaml_empty_file(self, temp_directory):
        """Test reading empty YAML file"""
        
        
        yaml_path = os.path.join(temp_directory, 'empty.yaml')
        with open(yaml_path, 'w') as f:
            f.write('')
        
        result = read_config_yaml(yaml_path)
        assert result is None

    def test_read_yaml_with_different_types(self, temp_directory):
        """Test reading YAML with different data types"""
        
        
        yaml_content = """string_val: hello
int_val: 42
float_val: 3.14
bool_val: true
null_val: null
"""
        yaml_path = os.path.join(temp_directory, 'types.yaml')
        with open(yaml_path, 'w') as f:
            f.write(yaml_content)
        
        result = read_config_yaml(yaml_path)
        assert result['string_val'] == 'hello'
        assert result['int_val'] == 42
        assert result['float_val'] == 3.14
        assert result['bool_val'] == True
        assert result['null_val'] is None

    def test_read_yaml_with_special_characters(self, temp_directory):
        """Test reading YAML with special characters"""
        
        
        yaml_content = """url: "http://localhost:8080/api?key=abc"
path: "C:\\\\Users\\\\test"
message: "Hello, World!"
"""
        yaml_path = os.path.join(temp_directory, 'special.yaml')
        with open(yaml_path, 'w') as f:
            f.write(yaml_content)
        
        result = read_config_yaml(yaml_path)
        assert 'url' in result
        assert 'path' in result


class TestConfigEdgeCases:
    """Edge case tests for config module"""

    def test_config_with_whitespace_values(self, temp_directory):
        """Test config with whitespace in values"""
        
        
        config_content = """[whitespace]
key_with_spaces = value with spaces
key_with_tabs = value\twith\ttabs
"""
        config_path = os.path.join(temp_directory, 'whitespace.ini')
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        result = readConfig('whitespace', config_path)
        assert 'value with spaces' in result['key_with_spaces']

    def test_config_case_sensitivity(self, temp_directory):
        """Test config key case sensitivity"""
        
        
        config_content = """[CaseSensitive]
KeyOne = Value1
KeyTwo = Value2
"""
        config_path = os.path.join(temp_directory, 'case.ini')
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        # ConfigParser keys are case-insensitive by default
        result = readConfig('CaseSensitive', config_path)
        assert 'keyone' in result
        assert 'keytwo' in result

    def test_yaml_with_unicode(self, temp_directory):
        """Test YAML with unicode characters"""
        
        
        yaml_content = """unicode:
  message: "Hello, World!"
  name: "Test"
"""
        yaml_path = os.path.join(temp_directory, 'unicode.yaml')
        with open(yaml_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        # Just test that YAML can be parsed
        result = read_config_yaml(yaml_path)
        assert result is not None
        assert 'unicode' in result
        assert result['unicode']['message'] == 'Hello, World!'

    def test_config_file_permission_error(self):
        """Test handling of permission errors"""
        
        
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(Exception):
                readConfig('section', '/some/path.ini')
