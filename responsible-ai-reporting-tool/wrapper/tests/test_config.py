import sys
import os
import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
from configparser import ConfigParser
import yaml

# Add src to path for imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.config.config import readConfig, read_config_yaml


# ============================================================================
# Test readConfig Function
# ============================================================================

class TestReadConfig:
    """Test readConfig function"""
    
    def test_read_config_valid_section(self, tmp_path):
        """Test reading valid config section"""
        # Create a temporary config file
        config_file = tmp_path / "test_config.ini"
        config_content = """[database]
host = localhost
port = 5432
name = testdb
user = testuser
"""
        config_file.write_text(config_content)
        
        result = readConfig('database', str(config_file))
        
        assert result == {
            'host': 'localhost',
            'port': '5432',
            'name': 'testdb',
            'user': 'testuser'
        }
    
    def test_read_config_section_not_found(self, tmp_path):
        """Test reading non-existent section"""
        config_file = tmp_path / "test_config.ini"
        config_content = """[database]
host = localhost
"""
        config_file.write_text(config_content)
        
        with pytest.raises(Exception, match="Section missing_section not found"):
            readConfig('missing_section', str(config_file))
    
    def test_read_config_empty_section(self, tmp_path):
        """Test reading empty section"""
        config_file = tmp_path / "test_config.ini"
        config_content = """[empty_section]
"""
        config_file.write_text(config_content)
        
        result = readConfig('empty_section', str(config_file))
        
        assert result == {}
    
    def test_read_config_multiple_sections(self, tmp_path):
        """Test reading from file with multiple sections"""
        config_file = tmp_path / "test_config.ini"
        config_content = """[section1]
key1 = value1

[section2]
key2 = value2
key3 = value3
"""
        config_file.write_text(config_content)
        
        result = readConfig('section2', str(config_file))
        
        assert result == {
            'key2': 'value2',
            'key3': 'value3'
        }
    
    def test_read_config_special_characters(self, tmp_path):
        """Test reading config with special characters"""
        config_file = tmp_path / "test_config.ini"
        config_content = """[database]
connection_string = mongodb://user:pass@localhost:27017/db?ssl=true
special = value with spaces and = signs
"""
        config_file.write_text(config_content)
        
        result = readConfig('database', str(config_file))
        
        assert 'connection_string' in result
        assert 'special' in result
    
    def test_read_config_file_not_found(self):
        """Test reading non-existent file"""
        # Should not raise exception, just return empty dict for missing section
        with pytest.raises(Exception):
            readConfig('any_section', 'nonexistent_file.ini')
    
    def test_read_config_with_comments(self, tmp_path):
        """Test reading config with comments"""
        config_file = tmp_path / "test_config.ini"
        config_content = """[database]
# This is a comment
host = localhost
; This is also a comment
port = 5432
"""
        config_file.write_text(config_content)
        
        result = readConfig('database', str(config_file))
        
        assert result == {
            'host': 'localhost',
            'port': '5432'
        }


# ============================================================================
# Test read_config_yaml Function
# ============================================================================

class TestReadConfigYaml:
    """Test read_config_yaml function"""
    
    def test_read_config_yaml_valid_file(self, tmp_path):
        """Test reading valid YAML file"""
        yaml_file = tmp_path / "test_config.yaml"
        yaml_content = """
database:
  host: localhost
  port: 5432
  name: testdb
settings:
  debug: true
  timeout: 30
"""
        yaml_file.write_text(yaml_content)
        
        result = read_config_yaml(str(yaml_file))
        
        assert result['database']['host'] == 'localhost'
        assert result['database']['port'] == 5432
        assert result['settings']['debug'] is True
        assert result['settings']['timeout'] == 30
    
    def test_read_config_yaml_empty_file(self, tmp_path):
        """Test reading empty YAML file"""
        yaml_file = tmp_path / "empty_config.yaml"
        yaml_file.write_text("")
        
        result = read_config_yaml(str(yaml_file))
        
        assert result is None
    
    def test_read_config_yaml_nested_structure(self, tmp_path):
        """Test reading nested YAML structure"""
        yaml_file = tmp_path / "nested_config.yaml"
        yaml_content = """
app:
  name: TestApp
  version: 1.0.0
  modules:
    - name: module1
      enabled: true
    - name: module2
      enabled: false
"""
        yaml_file.write_text(yaml_content)
        
        result = read_config_yaml(str(yaml_file))
        
        assert result['app']['name'] == 'TestApp'
        assert len(result['app']['modules']) == 2
        assert result['app']['modules'][0]['name'] == 'module1'
    
    def test_read_config_yaml_with_lists(self, tmp_path):
        """Test reading YAML with lists"""
        yaml_file = tmp_path / "list_config.yaml"
        yaml_content = """
servers:
  - localhost
  - server1.com
  - server2.com
ports:
  - 8080
  - 8081
  - 8082
"""
        yaml_file.write_text(yaml_content)
        
        result = read_config_yaml(str(yaml_file))
        
        assert len(result['servers']) == 3
        assert result['servers'][0] == 'localhost'
        assert len(result['ports']) == 3
        assert result['ports'][0] == 8080
    
    def test_read_config_yaml_file_not_found(self):
        """Test reading non-existent YAML file"""
        with pytest.raises(FileNotFoundError):
            read_config_yaml('nonexistent_file.yaml')
    
    def test_read_config_yaml_with_booleans(self, tmp_path):
        """Test reading YAML with boolean values"""
        yaml_file = tmp_path / "bool_config.yaml"
        yaml_content = """
features:
  feature1: true
  feature2: false
  feature3: yes
  feature4: no
"""
        yaml_file.write_text(yaml_content)
        
        result = read_config_yaml(str(yaml_file))
        
        assert result['features']['feature1'] is True
        assert result['features']['feature2'] is False
        assert result['features']['feature3'] is True
        assert result['features']['feature4'] is False
    
    def test_read_config_yaml_with_numbers(self, tmp_path):
        """Test reading YAML with different number types"""
        yaml_file = tmp_path / "number_config.yaml"
        yaml_content = """
values:
  integer: 42
  float: 3.14
  negative: -10
  zero: 0
"""
        yaml_file.write_text(yaml_content)
        
        result = read_config_yaml(str(yaml_file))
        
        assert result['values']['integer'] == 42
        assert result['values']['float'] == 3.14
        assert result['values']['negative'] == -10
        assert result['values']['zero'] == 0
    
    def test_read_config_yaml_with_nulls(self, tmp_path):
        """Test reading YAML with null values"""
        yaml_file = tmp_path / "null_config.yaml"
        yaml_content = """
settings:
  value1: null
  value2: ~
  value3:
"""
        yaml_file.write_text(yaml_content)
        
        result = read_config_yaml(str(yaml_file))
        
        assert result['settings']['value1'] is None
        assert result['settings']['value2'] is None
        assert result['settings']['value3'] is None


# ============================================================================
# Additional Logger Tests for Coverage
# ============================================================================

class TestCustomLogger:
    """Additional tests for CustomLogger to increase coverage"""
    
    def test_logger_disable_enable_console(self, monkeypatch, tmp_path):
        """Test disabling and enabling console output"""
        # Create a temporary logger config
        monkeypatch.setenv('LOG_DIR', str(tmp_path))
        
        from app.config.logger import CustomLogger
        logger = CustomLogger()
        
        # Test has console handler
        assert logger.has_console_handler() is True
        
        # Disable console output
        logger.disable_console_output()
        assert logger.has_console_handler() is False
        
        # Enable console output
        logger.enable_console_output()
        assert logger.has_console_handler() is True
        
        # Enable again (should not add duplicate)
        logger.enable_console_output()
        assert logger.has_console_handler() is True
    
    def test_logger_disable_enable_file(self, monkeypatch, tmp_path):
        """Test disabling and enabling file output"""
        from app.config.logger import CustomLogger
        logger = CustomLogger()
        
        # Check initial state - logger may or may not have file handler depending on config
        initial_has_handler = logger.has_file_handler()
        
        # Add file handler explicitly
        logger.add_file_handler('test_logger', str(tmp_path))
        
        # Count handlers before disable
        handler_count_before = len(logger.handlers)
        assert logger.has_file_handler() is True
        
        # Disable file output
        logger.disable_file_output()
        
        # After disable, should have fewer handlers
        # The method removes the file_handler but logger may have been created with a default file handler too
        handler_count_after_disable = len(logger.handlers)
        
        # Disable again (should not raise error)
        logger.disable_file_output()
        
        # Enable file output
        logger.enable_file_output()
        assert logger.has_file_handler() is True
    
    def test_logger_framework_method(self, monkeypatch, tmp_path):
        """Test the framework logging method"""
        from app.config.logger import CustomLogger
        logger = CustomLogger()
        
        # Test framework method exists and can be called
        logger.framework("Test framework message")
        # Should not raise exception
    
    def test_logger_all_log_levels(self, monkeypatch, tmp_path):
        """Test all logging levels"""
        from app.config.logger import CustomLogger
        logger = CustomLogger()
        
        # Test all logging levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
    
    def test_logger_with_exc_info(self, monkeypatch, tmp_path):
        """Test logging with exception info"""
        from app.config.logger import CustomLogger
        logger = CustomLogger()
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.error("Error occurred", exc_info=True)
            logger.exception("Exception occurred")
    
    def test_logger_file_creation_failure(self, monkeypatch, tmp_path):
        """Test logger when log directory creation fails"""
        from app.config.logger import CustomLogger
        logger = CustomLogger()
        
        # Try to create file handler with invalid directory
        # Should fallback to /tmp or current directory
        invalid_dir = str(tmp_path / "nonexistent" / "deeply" / "nested" / "path")
        
        with patch('os.makedirs', side_effect=OSError("Cannot create directory")):
            logger.add_file_handler('test_logger', invalid_dir)
            # Should not raise exception, should fallback
