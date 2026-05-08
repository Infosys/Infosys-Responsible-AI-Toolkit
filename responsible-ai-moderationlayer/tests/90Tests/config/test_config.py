"""
Tests for config.config module.
Tests INI and YAML configuration file reading functions.
"""

import pytest
import os
import textwrap
from unittest.mock import patch, mock_open, MagicMock


class TestConfigModule:
    """Test cases for configuration reading functions."""

    # Tests for readConfig (INI files)
    def test_readConfig_success(self, tmp_path):
        """Test successful reading of INI configuration file."""
        content = textwrap.dedent("""
        [postgresql]
        host=localhost
        port=5432
        database=testdb
        user=admin
        """)
        config_file = tmp_path / 'database.ini'
        config_file.write_text(content)
        
        from src.config.config import readConfig
        result = readConfig('postgresql', str(config_file))
        
        assert result == {
            'host': 'localhost',
            'port': '5432',
            'database': 'testdb',
            'user': 'admin'
        }

    def test_readConfig_section_not_found(self, tmp_path):
        """Test that Exception is raised when section is not found."""
        content = textwrap.dedent("""
        [other]
        key=value
        """)
        config_file = tmp_path / 'database.ini'
        config_file.write_text(content)
        
        from src.config.config import readConfig
        with pytest.raises(Exception, match="Section"):
            readConfig('mysql', str(config_file))

    def test_readConfig_multiple_sections(self, tmp_path):
        """Test reading different sections from config file."""
        content = textwrap.dedent("""
        [postgresql]
        host=localhost
        
        [api]
        api_key=test123
        api_secret=secret456
        """)
        config_file = tmp_path / 'config.ini'
        config_file.write_text(content)
        
        from src.config.config import readConfig
        result = readConfig('api', str(config_file))
        
        assert result == {
            'api_key': 'test123',
            'api_secret': 'secret456'
        }

    def test_readConfig_empty_section(self, tmp_path):
        """Test reading an empty section."""
        content = textwrap.dedent("""
        [empty]
        """)
        config_file = tmp_path / 'config.ini'
        config_file.write_text(content)
        
        from src.config.config import readConfig
        result = readConfig('empty', str(config_file))
        
        assert result == {}

    # Tests for read_config_yaml
    def test_read_config_yaml_success(self, tmp_path):
        """Test successful reading of YAML configuration file."""
        yaml_content = "database:\n  host: localhost\n  port: 5432"
        config_file = tmp_path / 'config.yaml'
        config_file.write_text(yaml_content)
        
        from src.config.config import read_config_yaml
        result = read_config_yaml(str(config_file))
        
        assert result == {
            'database': {
                'host': 'localhost',
                'port': 5432
            }
        }

    def test_read_config_yaml_file_not_found(self):
        """Test that FileNotFoundError is raised when YAML file doesn't exist."""
        from src.config.config import read_config_yaml
        with pytest.raises(FileNotFoundError):
            read_config_yaml('missing.yaml')

    def test_read_config_yaml_complex_structure(self, tmp_path):
        """Test reading complex YAML structure."""
        yaml_content = "server:\n  host: 0.0.0.0\n  port: 8080\nlogging:\n  level: DEBUG"
        config_file = tmp_path / 'app.yaml'
        config_file.write_text(yaml_content)
        
        from src.config.config import read_config_yaml
        result = read_config_yaml(str(config_file))
        
        assert result['server']['host'] == '0.0.0.0'
        assert result['server']['port'] == 8080
        assert result['logging']['level'] == 'DEBUG'

    def test_read_config_yaml_empty_file(self, tmp_path):
        """Test reading an empty YAML file."""
        config_file = tmp_path / 'empty.yaml'
        config_file.write_text('')
        
        from src.config.config import read_config_yaml
        result = read_config_yaml(str(config_file))
        
        assert result is None  # yaml.safe_load returns None for empty files

    def test_read_config_yaml_flat_structure(self, tmp_path):
        """Test reading flat YAML structure."""
        yaml_content = "key1: value1\nkey2: value2\nkey3: value3"
        config_file = tmp_path / 'flat.yaml'
        config_file.write_text(yaml_content)
        
        from src.config.config import read_config_yaml
        result = read_config_yaml(str(config_file))
        
        assert len(result) == 3
        assert result['key1'] == 'value1'
        assert result['key2'] == 'value2'
        assert result['key3'] == 'value3'


def test_config_folder_exists():
    """Test that config folder structure exists."""
    import os
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'config')
    assert os.path.exists(config_path)
