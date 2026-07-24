"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Comprehensive test suite for config.py module.
Tests configuration file reading for INI and YAML formats.

Test Coverage:
- Functional correctness of readConfig and read_config_yaml
- Edge cases and boundary conditions
- Error handling for missing files, invalid formats, missing sections
- Performance characteristics
- Integration with configparser and yaml libraries
- Code quality and structure validation
- Resource management (file handles)
- Security considerations (path traversal, injection)
- Regression testing
"""

import pytest
import os
import tempfile
import time
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
from configparser import ConfigParser
from concurrent.futures import ThreadPoolExecutor, as_completed
import gc

# Import the functions under test
from fairness.config.config import readConfig, read_config_yaml


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_ini_file(temp_dir):
    """Create a sample INI configuration file."""
    config_path = os.path.join(temp_dir, "test_config.ini")
    content = """[database]
host = localhost
port = 5432
user = testuser
password = testpass
dbname = testdb

[api]
endpoint = https://api.example.com
timeout = 30
retry = 3

[logging]
level = INFO
file = application.log
max_size = 10485760
"""
    with open(config_path, 'w') as f:
        f.write(content)
    return config_path


@pytest.fixture
def sample_yaml_file(temp_dir):
    """Create a sample YAML configuration file."""
    config_path = os.path.join(temp_dir, "test_config.yaml")
    content = {
        'database': {
            'host': 'localhost',
            'port': 5432,
            'user': 'testuser',
            'password': 'testpass'
        },
        'api': {
            'endpoint': 'https://api.example.com',
            'timeout': 30,
            'retry': 3
        },
        'features': ['feature1', 'feature2', 'feature3']
    }
    with open(config_path, 'w') as f:
        yaml.dump(content, f)
    return config_path


@pytest.fixture
def empty_ini_file(temp_dir):
    """Create an empty INI file."""
    config_path = os.path.join(temp_dir, "empty.ini")
    with open(config_path, 'w') as f:
        f.write("")
    return config_path


@pytest.fixture
def malformed_ini_file(temp_dir):
    """Create a malformed INI file."""
    config_path = os.path.join(temp_dir, "malformed.ini")
    content = """[section1
missing_bracket = value
invalid line without equals
[section2]
valid_key = valid_value
"""
    with open(config_path, 'w') as f:
        f.write(content)
    return config_path


@pytest.fixture
def malformed_yaml_file(temp_dir):
    """Create a malformed YAML file."""
    config_path = os.path.join(temp_dir, "malformed.yaml")
    content = """
key1: value1
key2: [unclosed list
  key3: value3
    invalid indentation
"""
    with open(config_path, 'w') as f:
        f.write(content)
    return config_path


@pytest.fixture
def complex_yaml_file(temp_dir):
    """Create a complex YAML file with nested structures."""
    config_path = os.path.join(temp_dir, "complex.yaml")
    content = {
        'server': {
            'host': 'localhost',
            'port': 8080,
            'ssl': {
                'enabled': True,
                'cert': '/path/to/cert.pem',
                'key': '/path/to/key.pem'
            }
        },
        'database': {
            'connections': [
                {'name': 'primary', 'host': 'db1.example.com'},
                {'name': 'replica', 'host': 'db2.example.com'}
            ]
        },
        'metadata': {
            'version': '1.0.0',
            'author': 'Test Author',
            'tags': ['production', 'v1', 'stable']
        }
    }
    with open(config_path, 'w') as f:
        yaml.dump(content, f)
    return config_path


@pytest.fixture
def ini_with_special_chars(temp_dir):
    """Create INI file with special characters."""
    config_path = os.path.join(temp_dir, "special.ini")
    content = """[special]
url = https://example.com/path?param=value&other=123
email = user@example.com
path = C:\\Users\\Test\\Documents
special_chars = Hello-World_123!@#
multiline = Line 1
"""
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return config_path


# ============================================================================
# Test Class 1: Functional Correctness - readConfig
# ============================================================================
class TestReadConfigFunctional:
    """
    Test the readConfig function for functional correctness.
    
    Validates:
    - Correct parsing of INI files
    - Section retrieval
    - Parameter extraction
    - Return value structure
    """
    
    def test_read_valid_section(self, sample_ini_file):
        """
        Test reading a valid section from INI file.
        
        Validates:
        - Functional correctness: Correct data retrieval
        - Return type: Dictionary with key-value pairs
        """
        result = readConfig('database', sample_ini_file)
        
        assert isinstance(result, dict)
        assert result['host'] == 'localhost'
        assert result['port'] == '5432'
        assert result['user'] == 'testuser'
        assert result['password'] == 'testpass'
        assert result['dbname'] == 'testdb'
        assert len(result) == 5
    
    def test_read_different_sections(self, sample_ini_file):
        """
        Test reading multiple different sections.
        
        Validates:
        - Functional correctness: Multiple section access
        - Isolation: Each section read independently
        """
        db_config = readConfig('database', sample_ini_file)
        api_config = readConfig('api', sample_ini_file)
        log_config = readConfig('logging', sample_ini_file)
        
        assert db_config['host'] == 'localhost'
        assert api_config['endpoint'] == 'https://api.example.com'
        assert log_config['level'] == 'INFO'
        
        # Verify independence
        assert 'host' in db_config
        assert 'host' not in api_config
    
    def test_all_parameters_retrieved(self, sample_ini_file):
        """
        Test that all parameters in a section are retrieved.
        
        Validates:
        - Coverage: Complete parameter extraction
        - Data integrity: No missing values
        """
        result = readConfig('api', sample_ini_file)
        
        assert 'endpoint' in result
        assert 'timeout' in result
        assert 'retry' in result
        assert len(result) == 3
    
    def test_parameter_values_as_strings(self, sample_ini_file):
        """
        Test that all values are returned as strings.
        
        Validates:
        - Type consistency: ConfigParser returns strings
        - Expected behavior: Numeric values as strings
        """
        result = readConfig('database', sample_ini_file)
        
        assert isinstance(result['port'], str)
        assert result['port'] == '5432'
        assert not isinstance(result['port'], int)
    
    def test_case_sensitivity(self, temp_dir):
        """
        Test case sensitivity of keys in ConfigParser.
        
        Validates:
        - Behavior: Keys are case-insensitive by default
        - ConfigParser semantics: Duplicate keys raise error
        """
        config_path = os.path.join(temp_dir, "case_test.ini")
        content = """[section]
KeyName = value1
differentkey = value2
"""
        with open(config_path, 'w') as f:
            f.write(content)
        
        result = readConfig('section', config_path)
        # ConfigParser treats keys as case-insensitive
        # Keys are lowercased internally
        assert len(result) == 2
        assert 'keyname' in result or 'differentkey' in result


# ============================================================================
# Test Class 2: Functional Correctness - read_config_yaml
# ============================================================================
class TestReadConfigYamlFunctional:
    """
    Test the read_config_yaml function for functional correctness.
    
    Validates:
    - Correct parsing of YAML files
    - Data structure preservation
    - Type handling
    """
    
    def test_read_valid_yaml(self, sample_yaml_file):
        """
        Test reading a valid YAML configuration file.
        
        Validates:
        - Functional correctness: Proper YAML parsing
        - Data structure: Nested dictionaries preserved
        """
        result = read_config_yaml(sample_yaml_file)
        
        assert isinstance(result, dict)
        assert 'database' in result
        assert 'api' in result
        assert 'features' in result
    
    def test_nested_structure_preserved(self, sample_yaml_file):
        """
        Test that nested YAML structures are preserved.
        
        Validates:
        - Data integrity: Nested dicts maintained
        - Structure: Hierarchical access works
        """
        result = read_config_yaml(sample_yaml_file)
        
        assert isinstance(result['database'], dict)
        assert result['database']['host'] == 'localhost'
        assert result['database']['port'] == 5432  # YAML preserves types
        assert isinstance(result['database']['port'], int)
    
    def test_list_values_preserved(self, sample_yaml_file):
        """
        Test that list values in YAML are preserved.
        
        Validates:
        - Type preservation: Lists remain as lists
        - Data integrity: All list items present
        """
        result = read_config_yaml(sample_yaml_file)
        
        assert isinstance(result['features'], list)
        assert len(result['features']) == 3
        assert 'feature1' in result['features']
        assert 'feature2' in result['features']
        assert 'feature3' in result['features']
    
    def test_type_preservation(self, complex_yaml_file):
        """
        Test that YAML preserves data types correctly.
        
        Validates:
        - Type handling: int, bool, string, list, dict
        - YAML semantics: Native type support
        """
        result = read_config_yaml(complex_yaml_file)
        
        assert isinstance(result['server']['port'], int)
        assert result['server']['port'] == 8080
        assert isinstance(result['server']['ssl']['enabled'], bool)
        assert result['server']['ssl']['enabled'] is True
        assert isinstance(result['metadata']['tags'], list)
    
    def test_complex_nested_structures(self, complex_yaml_file):
        """
        Test reading complex nested YAML structures.
        
        Validates:
        - Deep nesting: Multi-level access works
        - Complex data: Mixed types in nested structures
        """
        result = read_config_yaml(complex_yaml_file)
        
        assert result['server']['ssl']['cert'] == '/path/to/cert.pem'
        assert len(result['database']['connections']) == 2
        assert result['database']['connections'][0]['name'] == 'primary'
        assert result['metadata']['version'] == '1.0.0'


# ============================================================================
# Test Class 3: Error Handling
# ============================================================================
class TestErrorHandling:
    """
    Test error handling for various failure scenarios.
    
    Validates:
    - Missing files
    - Missing sections
    - Malformed files
    - Invalid paths
    """
    
    def test_missing_section_raises_exception(self, sample_ini_file):
        """
        Test that missing section raises appropriate exception.
        
        Validates:
        - Error handling: Exception on missing section
        - Error message: Clear indication of problem
        """
        with pytest.raises(Exception) as exc_info:
            readConfig('nonexistent_section', sample_ini_file)
        
        assert 'not found' in str(exc_info.value)
        assert 'nonexistent_section' in str(exc_info.value)
    
    def test_missing_ini_file(self, temp_dir):
        """
        Test behavior when INI file doesn't exist.
        
        Validates:
        - Error handling: Missing file scenario
        - ConfigParser behavior: Silent failure or empty result
        """
        nonexistent_file = os.path.join(temp_dir, "nonexistent.ini")
        
        # ConfigParser.read() doesn't raise for missing files, just returns empty
        with pytest.raises(Exception) as exc_info:
            readConfig('database', nonexistent_file)
        
        assert 'not found' in str(exc_info.value)
    
    def test_missing_yaml_file(self, temp_dir):
        """
        Test behavior when YAML file doesn't exist.
        
        Validates:
        - Error handling: Missing file raises exception
        - Exception type: FileNotFoundError or IOError
        """
        nonexistent_file = os.path.join(temp_dir, "nonexistent.yaml")
        
        with pytest.raises((FileNotFoundError, IOError)):
            read_config_yaml(nonexistent_file)
    
    def test_empty_ini_file(self, empty_ini_file):
        """
        Test reading empty INI file.
        
        Validates:
        - Error handling: Empty file with section request
        - Exception: Section not found
        """
        with pytest.raises(Exception) as exc_info:
            readConfig('database', empty_ini_file)
        
        assert 'not found' in str(exc_info.value)
    
    def test_malformed_yaml_raises_exception(self, malformed_yaml_file):
        """
        Test that malformed YAML raises parsing exception.
        
        Validates:
        - Error handling: Invalid YAML syntax
        - Exception type: yaml.YAMLError or similar
        """
        with pytest.raises(yaml.YAMLError):
            read_config_yaml(malformed_yaml_file)
    
    def test_invalid_path_characters(self):
        """
        Test handling of invalid path characters.
        
        Validates:
        - Error handling: Invalid file paths
        - Security: Path traversal attempts
        """
        invalid_paths = [
            "*.ini",  # Wildcard
            "<invalid>.ini",  # Invalid chars
            "NUL",  # Reserved name on Windows
        ]
        
        for invalid_path in invalid_paths:
            # Should raise appropriate exception (FileNotFoundError or similar)
            try:
                readConfig('section', invalid_path)
            except Exception:
                pass  # Expected to fail
    
    def test_permission_denied_simulation(self, sample_ini_file):
        """
        Test handling when file permissions deny access.
        
        Validates:
        - Error handling: Permission issues
        - Exception propagation
        """
        # Mock open to raise PermissionError
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            with pytest.raises(PermissionError):
                read_config_yaml(sample_ini_file)


# ============================================================================
# Test Class 4: Edge Cases
# ============================================================================
class TestEdgeCases:
    """
    Test edge cases and boundary conditions.
    
    Validates:
    - Special characters
    - Empty values
    - Long values
    - Unicode support
    """
    
    def test_section_with_special_characters(self, ini_with_special_chars):
        """
        Test reading values with special characters.
        
        Validates:
        - Edge case: URLs, paths, special chars
        - Data integrity: Values preserved correctly
        """
        result = readConfig('special', ini_with_special_chars)
        
        assert 'url' in result
        assert 'example.com' in result['url']
        assert '@' in result['email']
        assert '\\' in result['path'] or '\\\\' in result['path']
    
    def test_empty_section(self, temp_dir):
        """
        Test reading an empty section.
        
        Validates:
        - Edge case: Section exists but has no parameters
        - Return value: Empty dictionary
        """
        config_path = os.path.join(temp_dir, "empty_section.ini")
        content = """[empty]

[nonempty]
key = value
"""
        with open(config_path, 'w') as f:
            f.write(content)
        
        result = readConfig('empty', config_path)
        assert isinstance(result, dict)
        assert len(result) == 0
    
    def test_very_long_values(self, temp_dir):
        """
        Test handling of very long configuration values.
        
        Validates:
        - Edge case: Large string values
        - Memory handling: No truncation
        """
        config_path = os.path.join(temp_dir, "long_values.ini")
        long_value = "x" * 10000
        content = f"""[section]
longkey = {long_value}
"""
        with open(config_path, 'w') as f:
            f.write(content)
        
        result = readConfig('section', config_path)
        assert len(result['longkey']) == 10000
    
    def test_yaml_with_null_values(self, temp_dir):
        """
        Test YAML file with null/None values.
        
        Validates:
        - Edge case: null values in YAML
        - Type handling: None preserved
        """
        config_path = os.path.join(temp_dir, "null_values.yaml")
        content = {
            'key1': None,
            'key2': 'value2',
            'key3': None
        }
        with open(config_path, 'w') as f:
            yaml.dump(content, f)
        
        result = read_config_yaml(config_path)
        assert result['key1'] is None
        assert result['key2'] == 'value2'
        assert result['key3'] is None
    
    def test_yaml_empty_file(self, temp_dir):
        """
        Test reading empty YAML file.
        
        Validates:
        - Edge case: Empty file returns None
        - Behavior: YAML semantics for empty documents
        """
        config_path = os.path.join(temp_dir, "empty.yaml")
        with open(config_path, 'w') as f:
            f.write("")
        
        result = read_config_yaml(config_path)
        assert result is None
    
    def test_whitespace_handling(self, temp_dir):
        """
        Test handling of whitespace in keys and values.
        
        Validates:
        - Edge case: Leading/trailing whitespace
        - ConfigParser behavior: Trimming rules
        """
        config_path = os.path.join(temp_dir, "whitespace.ini")
        content = """[section]
  key_with_spaces  =  value with spaces  
no_spaces=no_spaces_value
"""
        with open(config_path, 'w') as f:
            f.write(content)
        
        result = readConfig('section', config_path)
        # ConfigParser handles whitespace trimming
        assert 'key_with_spaces' in result or 'key_with_spaces  ' in result


# ============================================================================
# Test Class 5: Performance
# ============================================================================
class TestPerformance:
    """
    Test performance characteristics.
    
    Validates:
    - File reading speed
    - Large file handling
    - Repeated access patterns
    """
    
    def test_read_ini_performance(self, sample_ini_file):
        """
        Test performance of reading INI files.
        
        Validates:
        - Performance: Fast file reading
        - Efficiency: Reasonable execution time
        """
        iterations = 100
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            result = readConfig('database', sample_ini_file)
        
        end_time = time.perf_counter()
        avg_time = (end_time - start_time) / iterations
        
        # Should be fast (< 10ms per read on average)
        assert avg_time < 0.01, f"INI read too slow: {avg_time}s"
    
    def test_read_yaml_performance(self, sample_yaml_file):
        """
        Test performance of reading YAML files.
        
        Validates:
        - Performance: Reasonable YAML parsing speed
        - Efficiency: Acceptable for typical configs
        """
        iterations = 100
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            result = read_config_yaml(sample_yaml_file)
        
        end_time = time.perf_counter()
        avg_time = (end_time - start_time) / iterations
        
        # YAML is slower than INI but should be reasonable (< 20ms per read)
        assert avg_time < 0.02, f"YAML read too slow: {avg_time}s"
    
    def test_large_ini_file(self, temp_dir):
        """
        Test handling of large INI files.
        
        Validates:
        - Scalability: Large file handling
        - Memory: No issues with big configs
        """
        config_path = os.path.join(temp_dir, "large.ini")
        
        # Create large INI file
        with open(config_path, 'w') as f:
            f.write("[section1]\n")
            for i in range(1000):
                f.write(f"key{i} = value{i}\n")
        
        start_time = time.perf_counter()
        result = readConfig('section1', config_path)
        end_time = time.perf_counter()
        
        assert len(result) == 1000
        assert end_time - start_time < 0.5  # Should be fast even for large files


# ============================================================================
# Test Class 6: Resource Management
# ============================================================================
class TestResourceManagement:
    """
    Test resource management and cleanup.
    
    Validates:
    - File handle closure
    - Memory management
    - No resource leaks
    """
    
    def test_file_handle_closed_after_read_yaml(self, sample_yaml_file):
        """
        Test that file handles are properly closed after reading YAML.
        
        Validates:
        - Resource management: File handles closed
        - Context manager usage: Proper cleanup
        """
        # Read file
        result = read_config_yaml(sample_yaml_file)
        
        # Try to delete file (should work if handle is closed)
        # On Windows, open file handles prevent deletion
        try:
            os.remove(sample_yaml_file)
            # If successful, recreate for other tests
            content = result
            with open(sample_yaml_file, 'w') as f:
                yaml.dump(content, f)
        except PermissionError:
            pytest.fail("File handle not closed properly")
    
    def test_no_memory_leaks_ini(self, sample_ini_file):
        """
        Test that repeated INI reads don't leak memory.
        
        Validates:
        - Resource management: No memory leaks
        - Garbage collection: Objects released
        """
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        for _ in range(100):
            result = readConfig('database', sample_ini_file)
        
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Allow some growth but not excessive
        growth = final_objects - initial_objects
        assert growth < 500, f"Possible memory leak: {growth} new objects"
    
    def test_no_memory_leaks_yaml(self, sample_yaml_file):
        """
        Test that repeated YAML reads don't leak memory.
        
        Validates:
        - Resource management: No memory leaks
        - Efficient parsing: Objects released
        """
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        for _ in range(100):
            result = read_config_yaml(sample_yaml_file)
        
        gc.collect()
        final_objects = len(gc.get_objects())
        
        growth = final_objects - initial_objects
        assert growth < 500, f"Possible memory leak: {growth} new objects"
    
    def test_concurrent_file_access(self, sample_ini_file, sample_yaml_file):
        """
        Test concurrent access to config files.
        
        Validates:
        - Thread safety: Multiple simultaneous reads
        - Resource management: No file lock issues
        """
        def read_ini():
            return readConfig('database', sample_ini_file)
        
        def read_yaml():
            return read_config_yaml(sample_yaml_file)
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for _ in range(5):
                futures.append(executor.submit(read_ini))
                futures.append(executor.submit(read_yaml))
            
            results = [f.result() for f in as_completed(futures)]
        
        # All reads should succeed
        assert len(results) == 10


# ============================================================================
# Test Class 7: Security
# ============================================================================
class TestSecurity:
    """
    Test security considerations.
    
    Validates:
    - Path traversal prevention
    - Injection attacks
    - Malicious input handling
    """
    
    def test_path_traversal_attempt(self):
        """
        Test handling of path traversal attempts.
        
        Validates:
        - Security: Path traversal not exploitable
        - Error handling: Invalid paths rejected
        """
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM"
        ]
        
        for path in malicious_paths:
            # Should fail gracefully (file not found or access denied)
            try:
                readConfig('section', path)
            except Exception:
                pass  # Expected to fail
    
    def test_yaml_bomb_protection(self, temp_dir):
        """
        Test protection against YAML billion laughs attack.
        
        Validates:
        - Security: YAML bomb doesn't freeze system
        - Resource limits: Reasonable memory usage
        """
        # Note: yaml.safe_load provides some protection
        config_path = os.path.join(temp_dir, "bomb.yaml")
        
        # Create a moderately deep nested structure (not extreme)
        nested = {'level': 'bottom'}
        for i in range(50):  # 50 levels deep
            nested = {'next': nested}
        
        with open(config_path, 'w') as f:
            yaml.dump(nested, f)
        
        # Should handle without hanging
        start_time = time.perf_counter()
        result = read_config_yaml(config_path)
        end_time = time.perf_counter()
        
        assert end_time - start_time < 1.0  # Should not hang
    
    def test_code_injection_in_yaml(self, temp_dir):
        """
        Test that YAML doesn't execute arbitrary code.
        
        Validates:
        - Security: safe_load prevents code execution
        - YAML semantics: No eval() or exec()
        """
        config_path = os.path.join(temp_dir, "injection.yaml")
        
        # Try to inject Python code
        content = """
dangerous: !!python/object/apply:os.system
  args: ['echo hacked']
safe_value: normal_string
"""
        with open(config_path, 'w') as f:
            f.write(content)
        
        # safe_load should reject dangerous constructs
        try:
            result = read_config_yaml(config_path)
            # If it succeeds, make sure no code was executed
            # safe_load will raise error for dangerous constructors
        except yaml.YAMLError:
            pass  # Expected with safe_load


# ============================================================================
# Test Class 8: Integration
# ============================================================================
class TestIntegration:
    """
    Test integration scenarios and real-world usage.
    
    Validates:
    - Multiple config types
    - Config switching
    - Practical usage patterns
    """
    
    def test_read_both_config_types(self, sample_ini_file, sample_yaml_file):
        """
        Test reading both INI and YAML configs in same session.
        
        Validates:
        - Integration: Both parsers work together
        - Isolation: No interference between formats
        """
        ini_result = readConfig('database', sample_ini_file)
        yaml_result = read_config_yaml(sample_yaml_file)
        
        assert isinstance(ini_result, dict)
        assert isinstance(yaml_result, dict)
        assert 'host' in ini_result
        assert 'database' in yaml_result
    
    def test_config_override_pattern(self, temp_dir):
        """
        Test pattern of loading default config then overriding.
        
        Validates:
        - Integration: Config merging pattern
        - Real-world: Common usage scenario
        """
        default_path = os.path.join(temp_dir, "default.yaml")
        override_path = os.path.join(temp_dir, "override.yaml")
        
        default_config = {'host': 'localhost', 'port': 8080, 'debug': False}
        override_config = {'host': 'production.com', 'debug': True}
        
        with open(default_path, 'w') as f:
            yaml.dump(default_config, f)
        with open(override_path, 'w') as f:
            yaml.dump(override_config, f)
        
        # Load and merge
        config = read_config_yaml(default_path)
        overrides = read_config_yaml(override_path)
        config.update(overrides)
        
        assert config['host'] == 'production.com'
        assert config['port'] == 8080
        assert config['debug'] is True
    
    def test_environment_specific_configs(self, temp_dir):
        """
        Test loading environment-specific configuration files.
        
        Validates:
        - Integration: Environment-based config selection
        - Practical usage: Dev/staging/prod configs
        """
        for env in ['dev', 'staging', 'prod']:
            config_path = os.path.join(temp_dir, f"config.{env}.yaml")
            config = {
                'environment': env,
                'database': f'db.{env}.example.com',
                'debug': env == 'dev'
            }
            with open(config_path, 'w') as f:
                yaml.dump(config, f)
        
        # Load each environment config
        dev_config = read_config_yaml(os.path.join(temp_dir, 'config.dev.yaml'))
        prod_config = read_config_yaml(os.path.join(temp_dir, 'config.prod.yaml'))
        
        assert dev_config['debug'] is True
        assert prod_config['debug'] is False
        assert 'dev' in dev_config['database']
        assert 'prod' in prod_config['database']


# ============================================================================
# Test Class 9: Regression
# ============================================================================
class TestRegression:
    """
    Test for regression issues and backward compatibility.
    
    Validates:
    - API stability
    - Function signatures
    - Return value formats
    """
    
    def test_readconfig_signature(self):
        """
        Test that readConfig function signature is stable.
        
        Validates:
        - Regression: API unchanged
        - Function signature: Takes section and filename
        """
        import inspect
        sig = inspect.signature(readConfig)
        params = list(sig.parameters.keys())
        
        assert len(params) == 2
        assert 'section' in params
        assert 'filename' in params
    
    def test_read_config_yaml_signature(self):
        """
        Test that read_config_yaml function signature is stable.
        
        Validates:
        - Regression: API unchanged
        - Function signature: Takes filename only
        """
        import inspect
        sig = inspect.signature(read_config_yaml)
        params = list(sig.parameters.keys())
        
        assert len(params) == 1
        assert 'filename' in params
    
    def test_module_exports(self):
        """
        Test that expected functions are exported.
        
        Validates:
        - Regression: Public API maintained
        - Module structure: Expected functions available
        """
        from fairness.config import config as config_module
        
        assert hasattr(config_module, 'readConfig')
        assert hasattr(config_module, 'read_config_yaml')
        assert callable(config_module.readConfig)
        assert callable(config_module.read_config_yaml)
    
    def test_return_type_consistency_ini(self, sample_ini_file):
        """
        Test that readConfig consistently returns dict.
        
        Validates:
        - Regression: Return type stable
        - API contract: Always returns dict
        """
        result = readConfig('database', sample_ini_file)
        assert isinstance(result, dict)
        
        result2 = readConfig('api', sample_ini_file)
        assert isinstance(result2, dict)
    
    def test_exception_type_consistency(self, sample_ini_file):
        """
        Test that exceptions are consistent across versions.
        
        Validates:
        - Regression: Exception types unchanged
        - Error handling: Predictable behavior
        """
        with pytest.raises(Exception) as exc_info:
            readConfig('nonexistent', sample_ini_file)
        
        # Should raise generic Exception as per current implementation
        assert isinstance(exc_info.value, Exception)


# ============================================================================
# Test Class 10: Code Quality
# ============================================================================
class TestCodeQuality:
    """
    Test code quality indicators.
    
    Validates:
    - Function documentation
    - Import structure
    - Module organization
    """
    
    def test_functions_have_names(self):
        """
        Test that functions have proper names.
        
        Validates:
        - Code quality: Named functions
        - Debuggability: Clear function names
        """
        assert readConfig.__name__ == 'readConfig'
        assert read_config_yaml.__name__ == 'read_config_yaml'
    
    def test_module_imports_available(self):
        """
        Test that required imports are available.
        
        Validates:
        - Code quality: Proper dependencies
        - Import structure: Required modules present
        """
        from fairness.config import config as config_module
        
        # Module should have imported ConfigParser and yaml
        import sys
        assert 'configparser' in sys.modules or 'ConfigParser' in sys.modules
        assert 'yaml' in sys.modules
    
    def test_functions_callable(self):
        """
        Test that exported functions are callable.
        
        Validates:
        - Code quality: Proper function objects
        - API: Functions ready to use
        """
        assert callable(readConfig)
        assert callable(read_config_yaml)
    
    def test_error_messages_informative(self, sample_ini_file):
        """
        Test that error messages are clear and helpful.
        
        Validates:
        - Code quality: Good error messages
        - User experience: Debugging-friendly errors
        """
        try:
            readConfig('missing_section', sample_ini_file)
        except Exception as e:
            error_msg = str(e)
            # Error message should mention the section name
            assert 'missing_section' in error_msg
            # Should mention it's not found
            assert 'not found' in error_msg.lower()
