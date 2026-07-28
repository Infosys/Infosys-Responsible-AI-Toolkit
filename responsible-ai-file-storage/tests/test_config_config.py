"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pytest
import os
import tempfile
import yaml
from unittest.mock import patch, mock_open, MagicMock
from configparser import ConfigParser
import sys
from pathlib import Path

# Add the src directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.config import readConfig, read_config_yaml, max_block_size, max_single_put_size


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_config_file():
    """
    Fixture to create a temporary INI configuration file for testing.
    Provides isolation and ensures cleanup after tests.
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as f:
        f.write("[database]\n")
        f.write("host=localhost\n")
        f.write("port=5432\n")
        f.write("user=testuser\n")
        f.write("password=testpass\n")
        f.write("\n")
        f.write("[aws]\n")
        f.write("region=us-east-1\n")
        f.write("bucket=test-bucket\n")
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    try:
        os.unlink(temp_file)
    except:
        pass


@pytest.fixture
def temp_yaml_file():
    """
    Fixture to create a temporary YAML configuration file for testing.
    Provides isolation and ensures cleanup after tests.
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
        yaml_content = {
            'database': {
                'host': 'localhost',
                'port': 5432,
                'user': 'yamluser'
            },
            'settings': {
                'timeout': 30,
                'retries': 3
            }
        }
        yaml.dump(yaml_content, f)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    try:
        os.unlink(temp_file)
    except:
        pass


@pytest.fixture
def empty_config_file():
    """
    Fixture to create an empty configuration file for testing edge cases.
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as f:
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    try:
        os.unlink(temp_file)
    except:
        pass


@pytest.fixture
def malformed_yaml_file():
    """
    Fixture to create a malformed YAML file for error handling tests.
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
        f.write("invalid: yaml: content:\n")
        f.write("  - missing\n")
        f.write("  proper: indentation\n")
        f.write("bad syntax here\n")
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    try:
        os.unlink(temp_file)
    except:
        pass


@pytest.fixture
def config_file_with_special_chars():
    """
    Fixture to create a config file with special characters for robustness testing.
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini', encoding='utf-8') as f:
        f.write("[special]\n")
        f.write("url=https://example.com?param=value&other=test\n")
        f.write("path=C:\\Users\\Test\\Path\n")
        f.write("spaces=value with spaces\n")
        f.write("empty=\n")
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    try:
        os.unlink(temp_file)
    except:
        pass


# ============================================================================
# MODULE-LEVEL CONSTANTS TESTS
# ============================================================================

class TestModuleConstants:
    """
    Test module-level constants for correctness and proper values.
    Ensures constants are defined correctly and meet expected specifications.
    """
    
    def test_max_block_size_value(self):
        """Test that max_block_size is set to the correct value (512 MiB)."""
        expected_size = 512 * 1024 * 1024
        assert max_block_size == expected_size, \
            f"max_block_size should be {expected_size} bytes (512 MiB)"
    
    def test_max_single_put_size_value(self):
        """Test that max_single_put_size is set to the correct value (500 MiB)."""
        expected_size = 500 * 1024 * 1024
        assert max_single_put_size == expected_size, \
            f"max_single_put_size should be {expected_size} bytes (500 MiB)"
    
    def test_max_block_size_type(self):
        """Test that max_block_size is an integer."""
        assert isinstance(max_block_size, int), "max_block_size should be an integer"
    
    def test_max_single_put_size_type(self):
        """Test that max_single_put_size is an integer."""
        assert isinstance(max_single_put_size, int), "max_single_put_size should be an integer"
    
    def test_constants_are_positive(self):
        """Test that size constants are positive values."""
        assert max_block_size > 0, "max_block_size should be positive"
        assert max_single_put_size > 0, "max_single_put_size should be positive"
    
    def test_max_single_put_size_less_than_block_size(self):
        """Test the relationship between the two size constants."""
        assert max_single_put_size <= max_block_size, \
            "max_single_put_size should not exceed max_block_size"


# ============================================================================
# readConfig FUNCTION TESTS
# ============================================================================

class TestReadConfig:
    """
    Comprehensive tests for the readConfig function.
    Tests functional correctness, edge cases, error handling, and robustness.
    """
    
    # --- Functional Correctness Tests ---
    
    def test_read_config_basic_functionality(self, temp_config_file):
        """
        Test basic functionality of reading a config section.
        Verifies correct parsing and return of configuration data.
        """
        result = readConfig('database', temp_config_file)
        
        assert isinstance(result, dict), "Should return a dictionary"
        assert result['host'] == 'localhost', "Should read host correctly"
        assert result['port'] == '5432', "Should read port correctly"
        assert result['user'] == 'testuser', "Should read user correctly"
        assert result['password'] == 'testpass', "Should read password correctly"
    
    def test_read_config_multiple_sections(self, temp_config_file):
        """Test reading different sections from the same config file."""
        db_result = readConfig('database', temp_config_file)
        aws_result = readConfig('aws', temp_config_file)
        
        assert db_result['host'] == 'localhost'
        assert aws_result['region'] == 'us-east-1'
        assert aws_result['bucket'] == 'test-bucket'
    
    def test_read_config_all_values_returned(self, temp_config_file):
        """Test that all key-value pairs in a section are returned."""
        result = readConfig('database', temp_config_file)
        
        expected_keys = {'host', 'port', 'user', 'password'}
        assert set(result.keys()) == expected_keys, \
            "Should return all keys from the section"
    
    # --- Edge Cases Tests ---
    
    def test_read_config_nonexistent_section(self, temp_config_file):
        """
        Test error handling when requesting a non-existent section.
        Should raise an Exception with appropriate message.
        """
        with pytest.raises(Exception) as exc_info:
            readConfig('nonexistent', temp_config_file)
        
        assert 'Section nonexistent not found' in str(exc_info.value), \
            "Should provide clear error message about missing section"
    
    def test_read_config_nonexistent_file(self):
        """
        Test error handling when config file doesn't exist.
        ConfigParser doesn't raise an error but returns empty dict for missing sections.
        """
        with pytest.raises(Exception) as exc_info:
            readConfig('database', 'nonexistent_file.ini')
        
        # Should raise exception when section is not found
        assert 'not found' in str(exc_info.value).lower()
    
    def test_read_config_empty_file(self, empty_config_file):
        """Test behavior with an empty configuration file."""
        with pytest.raises(Exception) as exc_info:
            readConfig('database', empty_config_file)
        
        assert 'not found' in str(exc_info.value).lower()
    
    def test_read_config_special_characters(self, config_file_with_special_chars):
        """
        Test handling of special characters in configuration values.
        Ensures proper parsing of URLs, paths, and spaces.
        """
        result = readConfig('special', config_file_with_special_chars)
        
        assert 'url' in result
        assert 'param=value' in result['url'], "Should preserve URL parameters"
        assert 'path' in result
        assert 'spaces' in result
        assert result['spaces'] == 'value with spaces', "Should preserve spaces"
    
    def test_read_config_empty_values(self, config_file_with_special_chars):
        """Test handling of empty configuration values."""
        result = readConfig('special', config_file_with_special_chars)
        
        assert 'empty' in result
        assert result['empty'] == '', "Should handle empty values correctly"
    
    # --- Error Handling Tests ---
    
    def test_read_config_with_none_section(self, temp_config_file):
        """Test behavior when section parameter is None."""
        with pytest.raises(Exception):
            readConfig(None, temp_config_file)
    
    def test_read_config_with_none_filename(self):
        """Test behavior when filename parameter is None."""
        with pytest.raises(Exception):
            readConfig('database', None)
    
    def test_read_config_invalid_section_type(self, temp_config_file):
        """Test behavior with invalid section parameter type."""
        with pytest.raises(Exception):
            readConfig(123, temp_config_file)
    
    # --- Performance & Resource Management Tests ---
    
    def test_read_config_repeated_calls(self, temp_config_file):
        """
        Test that multiple calls to readConfig work correctly.
        Ensures no side effects or resource leaks.
        """
        result1 = readConfig('database', temp_config_file)
        result2 = readConfig('database', temp_config_file)
        result3 = readConfig('aws', temp_config_file)
        
        assert result1 == result2, "Repeated calls should return same result"
        assert result1 != result3, "Different sections should return different results"
    
    def test_read_config_large_section(self):
        """
        Test performance with a large configuration section.
        Ensures the function handles many key-value pairs efficiently.
        """
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as f:
            f.write("[large]\n")
            for i in range(1000):
                f.write(f"key{i}=value{i}\n")
            temp_file = f.name
        
        try:
            result = readConfig('large', temp_file)
            assert len(result) == 1000, "Should handle large sections"
            assert result['key0'] == 'value0'
            assert result['key999'] == 'value999'
        finally:
            os.unlink(temp_file)
    
    # --- Isolation Tests ---
    
    def test_read_config_does_not_modify_file(self, temp_config_file):
        """
        Test that readConfig doesn't modify the original file.
        Ensures read-only behavior.
        """
        with open(temp_config_file, 'r') as f:
            original_content = f.read()
        
        readConfig('database', temp_config_file)
        
        with open(temp_config_file, 'r') as f:
            after_content = f.read()
        
        assert original_content == after_content, "Should not modify the config file"
    
    def test_read_config_result_is_independent(self, temp_config_file):
        """
        Test that returned dictionaries are independent.
        Modifying one result should not affect others.
        """
        result1 = readConfig('database', temp_config_file)
        result2 = readConfig('database', temp_config_file)
        
        result1['host'] = 'modified'
        
        assert result2['host'] == 'localhost', \
            "Modifying one result should not affect others"
    
    # --- Case Sensitivity Tests ---
    
    def test_read_config_case_sensitive_keys(self, temp_config_file):
        """Test that configuration keys are case-insensitive (ConfigParser default)."""
        result = readConfig('database', temp_config_file)
        
        # ConfigParser converts keys to lowercase
        assert 'host' in result
        assert all(key.islower() or not key.isalpha() for key in result.keys())


# ============================================================================
# read_config_yaml FUNCTION TESTS
# ============================================================================

class TestReadConfigYaml:
    """
    Comprehensive tests for the read_config_yaml function.
    Tests YAML parsing, edge cases, error handling, and robustness.
    """
    
    # --- Functional Correctness Tests ---
    
    def test_read_yaml_basic_functionality(self, temp_yaml_file):
        """
        Test basic functionality of reading YAML configuration.
        Verifies correct parsing and structure.
        """
        result = read_config_yaml(temp_yaml_file)
        
        assert isinstance(result, dict), "Should return a dictionary"
        assert 'database' in result
        assert 'settings' in result
        assert result['database']['host'] == 'localhost'
        assert result['database']['port'] == 5432
        assert result['settings']['timeout'] == 30
    
    def test_read_yaml_nested_structure(self, temp_yaml_file):
        """Test handling of nested YAML structures."""
        result = read_config_yaml(temp_yaml_file)
        
        assert isinstance(result['database'], dict), "Should handle nested dictionaries"
        assert result['database']['user'] == 'yamluser'
        assert isinstance(result['settings']['retries'], int)
    
    def test_read_yaml_preserves_data_types(self):
        """
        Test that YAML parsing preserves correct data types.
        Ensures integers, strings, booleans, etc. are correctly typed.
        """
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            yaml_content = {
                'string': 'text',
                'integer': 42,
                'float': 3.14,
                'boolean': True,
                'null_value': None,
                'list': [1, 2, 3],
                'nested': {'key': 'value'}
            }
            yaml.dump(yaml_content, f)
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            
            assert isinstance(result['string'], str)
            assert isinstance(result['integer'], int)
            assert isinstance(result['float'], float)
            assert isinstance(result['boolean'], bool)
            assert result['null_value'] is None
            assert isinstance(result['list'], list)
            assert isinstance(result['nested'], dict)
        finally:
            os.unlink(temp_file)
    
    # --- Edge Cases Tests ---
    
    def test_read_yaml_empty_file(self):
        """Test behavior with an empty YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            assert result is None or result == {}, \
                "Empty YAML should return None or empty dict"
        finally:
            os.unlink(temp_file)
    
    def test_read_yaml_only_comments(self):
        """Test YAML file containing only comments."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            f.write("# This is a comment\n")
            f.write("# Another comment\n")
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            assert result is None or result == {}
        finally:
            os.unlink(temp_file)
    
    def test_read_yaml_complex_structures(self):
        """Test handling of complex YAML structures with lists and nested dicts."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            yaml_content = {
                'servers': [
                    {'name': 'server1', 'ip': '192.168.1.1'},
                    {'name': 'server2', 'ip': '192.168.1.2'}
                ],
                'config': {
                    'level1': {
                        'level2': {
                            'level3': 'deep value'
                        }
                    }
                }
            }
            yaml.dump(yaml_content, f)
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            
            assert len(result['servers']) == 2
            assert result['servers'][0]['name'] == 'server1'
            assert result['config']['level1']['level2']['level3'] == 'deep value'
        finally:
            os.unlink(temp_file)
    
    # --- Error Handling Tests ---
    
    def test_read_yaml_nonexistent_file(self):
        """Test error handling when YAML file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            read_config_yaml('nonexistent_file.yaml')
    
    def test_read_yaml_malformed_file(self, malformed_yaml_file):
        """Test error handling with malformed YAML syntax."""
        with pytest.raises(yaml.YAMLError):
            read_config_yaml(malformed_yaml_file)
    
    def test_read_yaml_invalid_syntax(self):
        """Test handling of various YAML syntax errors."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            f.write("key: value\n")
            f.write("  invalid indentation\n")
            f.write("another: [unclosed list\n")
            temp_file = f.name
        
        try:
            with pytest.raises(yaml.YAMLError):
                read_config_yaml(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_read_yaml_with_none_filename(self):
        """Test behavior when filename parameter is None."""
        with pytest.raises(Exception):
            read_config_yaml(None)
    
    # --- Performance & Resource Management Tests ---
    
    def test_read_yaml_repeated_calls(self, temp_yaml_file):
        """
        Test that multiple calls work correctly without side effects.
        Ensures no resource leaks or state pollution.
        """
        result1 = read_config_yaml(temp_yaml_file)
        result2 = read_config_yaml(temp_yaml_file)
        
        assert result1 == result2, "Repeated calls should return same result"
    
    def test_read_yaml_large_file(self):
        """
        Test performance with a large YAML file.
        Ensures efficient handling of large configurations.
        """
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            large_config = {f'key{i}': f'value{i}' for i in range(1000)}
            yaml.dump(large_config, f)
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            assert len(result) == 1000, "Should handle large YAML files"
            assert result['key0'] == 'value0'
            assert result['key999'] == 'value999'
        finally:
            os.unlink(temp_file)
    
    # --- Isolation Tests ---
    
    def test_read_yaml_does_not_modify_file(self, temp_yaml_file):
        """
        Test that read_config_yaml doesn't modify the original file.
        Ensures read-only behavior.
        """
        with open(temp_yaml_file, 'r') as f:
            original_content = f.read()
        
        read_config_yaml(temp_yaml_file)
        
        with open(temp_yaml_file, 'r') as f:
            after_content = f.read()
        
        assert original_content == after_content, "Should not modify the YAML file"
    
    def test_read_yaml_result_is_independent(self, temp_yaml_file):
        """
        Test that returned dictionaries are independent.
        Modifying one result should not affect others.
        """
        result1 = read_config_yaml(temp_yaml_file)
        result2 = read_config_yaml(temp_yaml_file)
        
        result1['database']['host'] = 'modified'
        
        assert result2['database']['host'] == 'localhost', \
            "Modifying one result should not affect others"
    
    # --- Special Content Tests ---
    
    def test_read_yaml_with_unicode(self):
        """Test handling of Unicode characters in YAML."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml', encoding='utf-8') as f:
            yaml_content = {
                'chinese': '测试',
                'japanese': 'テスト',
                'emoji': '🚀',
                'mixed': 'Hello 世界'
            }
            yaml.dump(yaml_content, f, allow_unicode=True)
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            # Verify that unicode strings are present, actual encoding may vary
            assert 'chinese' in result
            assert 'japanese' in result
            assert 'emoji' in result
            assert 'mixed' in result
            # Just verify they are strings and non-empty
            assert isinstance(result['chinese'], str) and len(result['chinese']) > 0
            assert isinstance(result['japanese'], str) and len(result['japanese']) > 0
        finally:
            os.unlink(temp_file)
    
    def test_read_yaml_with_multiline_strings(self):
        """Test handling of multiline strings in YAML."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            f.write("description: |\n")
            f.write("  This is a\n")
            f.write("  multiline\n")
            f.write("  string\n")
            temp_file = f.name
        
        try:
            result = read_config_yaml(temp_file)
            assert 'description' in result
            assert '\n' in result['description']
        finally:
            os.unlink(temp_file)


# ============================================================================
# INTEGRATION & REGRESSION TESTS
# ============================================================================

class TestIntegrationAndRegression:
    """
    Integration tests to verify components work together.
    Regression tests to prevent previously fixed bugs.
    """
    
    def test_both_functions_read_same_config_structure(self):
        """
        Test that INI and YAML readers can handle similar data structures.
        Ensures consistency across configuration formats.
        """
        # Create similar configs in both formats
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as f:
            f.write("[app]\n")
            f.write("name=testapp\n")
            f.write("version=1.0\n")
            ini_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            yaml.dump({'app': {'name': 'testapp', 'version': '1.0'}}, f)
            yaml_file = f.name
        
        try:
            ini_result = readConfig('app', ini_file)
            yaml_result = read_config_yaml(yaml_file)
            
            assert ini_result['name'] == yaml_result['app']['name']
            assert ini_result['version'] == yaml_result['app']['version']
        finally:
            os.unlink(ini_file)
            os.unlink(yaml_file)
    
    def test_constants_used_in_real_scenario(self):
        """
        Test that module constants can be used for file size validation.
        Simulates real-world usage scenario.
        """
        test_size = 256 * 1024 * 1024  # 256 MiB
        
        assert test_size < max_single_put_size, \
            "256 MiB should be within single put size limit"
        assert test_size < max_block_size, \
            "256 MiB should be within block size limit"
    
    def test_config_file_path_variations(self):
        """
        Test that config readers handle various path formats.
        Ensures cross-platform compatibility.
        """
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as f:
            f.write("[test]\n")
            f.write("key=value\n")
            temp_file = f.name
        
        try:
            # Test with absolute path
            result1 = readConfig('test', temp_file)
            assert result1['key'] == 'value'
            
            # Test with Path object (if converted to string)
            path_obj = Path(temp_file)
            result2 = readConfig('test', str(path_obj))
            assert result2['key'] == 'value'
        finally:
            os.unlink(temp_file)


# ============================================================================
# SECURITY TESTS
# ============================================================================

class TestSecurity:
    """
    Security-related tests to ensure safe configuration handling.
    Tests for injection vulnerabilities and secure file access.
    """
    
    def test_read_config_no_code_injection(self):
        """
        Test that config values don't execute as code.
        Ensures safe handling of potentially malicious config values.
        """
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as f:
            f.write("[security]\n")
            f.write("command=rm -rf /\n")
            f.write("python=__import__('os').system('echo hacked')\n")
            temp_file = f.name
        
        try:
            result = readConfig('security', temp_file)
            
            # Values should be returned as strings, not executed
            assert result['command'] == 'rm -rf /'
            assert '__import__' in result['python']
            assert isinstance(result['python'], str)
        finally:
            os.unlink(temp_file)
    
    def test_read_yaml_no_arbitrary_code_execution(self):
        """
        Test that YAML safe_load prevents arbitrary code execution.
        Ensures yaml.safe_load is used instead of yaml.load.
        """
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            # This would be dangerous with yaml.load but safe with yaml.safe_load
            f.write("command: !!python/object/apply:os.system ['echo hacked']\n")
            temp_file = f.name
        
        try:
            # Should raise error or safely ignore dangerous constructs
            with pytest.raises(yaml.YAMLError):
                read_config_yaml(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_read_config_path_traversal_protection(self):
        """
        Test handling of path traversal attempts in filenames.
        Ensures secure file access - should raise exception for non-existent dangerous paths.
        """
        # Attempt to read outside allowed directories
        dangerous_path = "../../../etc/passwd"
        
        # Should raise exception as file doesn't exist or section not found
        with pytest.raises(Exception):
            readConfig('test', dangerous_path)


# ============================================================================
# CODE QUALITY INDICATOR TESTS
# ============================================================================

class TestCodeQuality:
    """
    Tests that verify code quality indicators.
    Ensures maintainability, readability, and proper design.
    """
    
    def test_functions_have_consistent_return_types(self, temp_config_file, temp_yaml_file):
        """
        Test that functions consistently return dictionaries.
        Ensures predictable behavior and type consistency.
        """
        ini_result = readConfig('database', temp_config_file)
        yaml_result = read_config_yaml(temp_yaml_file)
        
        assert isinstance(ini_result, dict), "readConfig should always return dict"
        assert isinstance(yaml_result, dict), "read_config_yaml should always return dict"
    
    def test_functions_are_stateless(self, temp_config_file):
        """
        Test that functions don't maintain internal state.
        Ensures predictable behavior and thread safety.
        """
        result1 = readConfig('database', temp_config_file)
        result2 = readConfig('aws', temp_config_file)
        result3 = readConfig('database', temp_config_file)
        
        # Results from same section should be identical
        assert result1 == result3
        # Different sections should not affect each other
        assert result1 != result2
    
    def test_error_messages_are_informative(self, temp_config_file):
        """
        Test that error messages provide useful information.
        Ensures good debugging experience.
        """
        try:
            readConfig('missing_section', temp_config_file)
            assert False, "Should have raised an exception"
        except Exception as e:
            error_msg = str(e)
            assert 'missing_section' in error_msg, \
                "Error should mention the missing section name"
            assert temp_config_file in error_msg or 'file' in error_msg.lower(), \
                "Error should mention the file"


# ============================================================================
# MOCK-BASED TESTS
# ============================================================================

class TestWithMocks:
    """
    Tests using mocks to verify internal behavior and external dependencies.
    Ensures proper integration with ConfigParser and YAML libraries.
    """
    
    @patch('config.config.ConfigParser')
    def test_readconfig_uses_configparser(self, mock_configparser, temp_config_file):
        """
        Test that readConfig properly uses ConfigParser.
        Verifies correct interaction with the ConfigParser API.
        """
        mock_parser_instance = MagicMock()
        mock_configparser.return_value = mock_parser_instance
        mock_parser_instance.has_section.return_value = True
        mock_parser_instance.items.return_value = [('key', 'value')]
        
        result = readConfig('test', temp_config_file)
        
        mock_configparser.assert_called_once()
        mock_parser_instance.read.assert_called_once_with(temp_config_file)
        mock_parser_instance.has_section.assert_called_once_with('test')
        mock_parser_instance.items.assert_called_once_with('test')
    
    @patch('builtins.open', new_callable=mock_open, read_data="key: value\n")
    @patch('yaml.safe_load')
    def test_read_yaml_uses_safe_load(self, mock_safe_load, mock_file):
        """
        Test that read_config_yaml uses yaml.safe_load for security.
        Ensures safe YAML parsing practices.
        """
        mock_safe_load.return_value = {'key': 'value'}
        
        result = read_config_yaml('test.yaml')
        
        mock_file.assert_called_once_with('test.yaml')
        mock_safe_load.assert_called_once()
        assert result == {'key': 'value'}
    
    @patch('builtins.open', side_effect=PermissionError("Access denied"))
    def test_read_yaml_handles_permission_error(self, mock_file):
        """
        Test handling of file permission errors.
        Ensures graceful error handling for access issues.
        """
        with pytest.raises(PermissionError):
            read_config_yaml('restricted.yaml')
    
    @patch('builtins.open', side_effect=IOError("Disk error"))
    def test_read_yaml_handles_io_error(self, mock_file):
        """
        Test handling of I/O errors during file reading.
        Ensures robust error handling for disk issues.
        """
        with pytest.raises(IOError):
            read_config_yaml('problematic.yaml')


# ============================================================================
# REPEATABILITY TESTS
# ============================================================================

class TestRepeatability:
    """
    Tests to ensure functions produce consistent results across multiple calls.
    Verifies deterministic behavior and absence of side effects.
    """
    
    def test_readconfig_is_deterministic(self, temp_config_file):
        """
        Test that readConfig returns identical results on repeated calls.
        Ensures deterministic behavior.
        """
        results = [readConfig('database', temp_config_file) for _ in range(10)]
        
        # All results should be identical
        for result in results[1:]:
            assert result == results[0], "Results should be identical across calls"
    
    def test_read_yaml_is_deterministic(self, temp_yaml_file):
        """
        Test that read_config_yaml returns identical results on repeated calls.
        Ensures deterministic behavior.
        """
        results = [read_config_yaml(temp_yaml_file) for _ in range(10)]
        
        # All results should be identical
        for result in results[1:]:
            assert result == results[0], "Results should be identical across calls"
    
    def test_functions_thread_safe_simulation(self, temp_config_file, temp_yaml_file):
        """
        Simulate concurrent access to test thread safety.
        Verifies functions can be called simultaneously without issues.
        """
        import concurrent.futures
        
        def read_ini():
            return readConfig('database', temp_config_file)
        
        def read_yaml():
            return read_config_yaml(temp_yaml_file)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures_ini = [executor.submit(read_ini) for _ in range(10)]
            futures_yaml = [executor.submit(read_yaml) for _ in range(10)]
            
            ini_results = [f.result() for f in futures_ini]
            yaml_results = [f.result() for f in futures_yaml]
        
        # All results should be identical
        assert all(r == ini_results[0] for r in ini_results)
        assert all(r == yaml_results[0] for r in yaml_results)


# ============================================================================
# COVERAGE COMPLETENESS VERIFICATION
# ============================================================================

class TestCoverageCompleteness:
    """
    Meta-tests to verify that all important aspects are covered.
    Ensures comprehensive test coverage.
    """
    
    def test_all_public_functions_tested(self):
        """
        Verify that all public functions from config.py are tested.
        Ensures no functionality is left untested.
        """
        from config import config
        
        # Get only actual functions (not imported classes/modules)
        public_functions = [name for name in dir(config) 
                          if callable(getattr(config, name)) 
                          and not name.startswith('_')
                          and not isinstance(getattr(config, name), type)]  # Exclude classes
        
        tested_functions = {'readConfig', 'read_config_yaml'}
        
        assert set(public_functions) == tested_functions, \
            f"Mismatch in functions. Found: {set(public_functions)}, Expected: {tested_functions}"
    
    def test_all_constants_tested(self):
        """
        Verify that all module-level constants are tested.
        Ensures complete constant validation.
        """
        tested_constants = {'max_block_size', 'max_single_put_size'}
        
        # Verify these constants exist in the module
        from config import config
        for const in tested_constants:
            assert hasattr(config, const), f"Constant {const} should exist"
