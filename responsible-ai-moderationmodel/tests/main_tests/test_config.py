"""
Tests for config module (config.py)
"""
import pytest
import os
import tempfile
from configparser import ConfigParser
import yaml


def test_readConfig_valid_section():
    """Test reading valid section from config file"""
    # source exposes read_config; alias as readConfig for backward-compat in tests
    from src.config.config import read_config as readConfig
    
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write('[database]\n')
        f.write('host=localhost\n')
        f.write('port=5432\n')
        f.write('user=testuser\n')
        config_file = f.name
    
    try:
        result = readConfig('database', config_file)
        assert result == {'host': 'localhost', 'port': '5432', 'user': 'testuser'}
        assert 'host' in result
        assert result['host'] == 'localhost'
    finally:
        os.unlink(config_file)


def test_readConfig_missing_section():
    """Test reading non-existent section raises exception"""
    from src.config.config import read_config as readConfig
    
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write('[database]\n')
        f.write('host=localhost\n')
        config_file = f.name
    
    try:
        with pytest.raises(Exception) as exc_info:
            readConfig('nonexistent', config_file)
        assert 'Section nonexistent not found' in str(exc_info.value)
    finally:
        os.unlink(config_file)


def test_readConfig_empty_section():
    """Test reading empty section"""
    from src.config.config import read_config as readConfig
    
    # Create temporary config file with empty section
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write('[empty]\n')
        config_file = f.name
    
    try:
        result = readConfig('empty', config_file)
        assert result == {}
    finally:
        os.unlink(config_file)


def test_readConfig_multiple_sections():
    """Test reading from file with multiple sections"""
    from src.config.config import read_config as readConfig
    
    # Create temporary config file with multiple sections
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write('[section1]\n')
        f.write('key1=value1\n')
        f.write('[section2]\n')
        f.write('key2=value2\n')
        config_file = f.name
    
    try:
        result1 = readConfig('section1', config_file)
        result2 = readConfig('section2', config_file)
        assert result1 == {'key1': 'value1'}
        assert result2 == {'key2': 'value2'}
    finally:
        os.unlink(config_file)


def test_readConfig_special_characters():
    """Test reading config with special characters"""
    from src.config.config import read_config as readConfig
    
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write('[app]\n')
        f.write('name=Test App\n')
        f.write('path=/usr/local/bin\n')
        f.write('url=https://example.com:8080\n')
        config_file = f.name
    
    try:
        result = readConfig('app', config_file)
        assert result['name'] == 'Test App'
        assert result['path'] == '/usr/local/bin'
        assert result['url'] == 'https://example.com:8080'
    finally:
        os.unlink(config_file)


def test_read_config_yaml_valid():
    """Test reading valid YAML config file"""
    from src.config.config import read_config_yaml
    
    # Create temporary YAML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml_content = {
            'database': {
                'host': 'localhost',
                'port': 5432
            },
            'app': {
                'name': 'TestApp',
                'debug': True
            }
        }
        yaml.dump(yaml_content, f)
        yaml_file = f.name
    
    try:
        result = read_config_yaml(yaml_file)
        assert result['database']['host'] == 'localhost'
        assert result['database']['port'] == 5432
        assert result['app']['name'] == 'TestApp'
        assert result['app']['debug'] is True
    finally:
        os.unlink(yaml_file)


def test_read_config_yaml_empty():
    """Test reading empty YAML file"""
    from src.config.config import read_config_yaml
    
    # Create empty YAML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml_file = f.name
    
    try:
        result = read_config_yaml(yaml_file)
        assert result is None
    finally:
        os.unlink(yaml_file)


def test_read_config_yaml_nested():
    """Test reading YAML with nested structures"""
    from src.config.config import read_config_yaml
    
    # Create YAML with nested data
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml_content = {
            'level1': {
                'level2': {
                    'level3': {
                        'value': 'deep'
                    }
                }
            }
        }
        yaml.dump(yaml_content, f)
        yaml_file = f.name
    
    try:
        result = read_config_yaml(yaml_file)
        assert result['level1']['level2']['level3']['value'] == 'deep'
    finally:
        os.unlink(yaml_file)


def test_read_config_yaml_with_list():
    """Test reading YAML with lists"""
    from src.config.config import read_config_yaml
    
    # Create YAML with list
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml_content = {
            'servers': ['server1', 'server2', 'server3'],
            'ports': [8000, 8001, 8002]
        }
        yaml.dump(yaml_content, f)
        yaml_file = f.name
    
    try:
        result = read_config_yaml(yaml_file)
        assert len(result['servers']) == 3
        assert result['servers'][0] == 'server1'
        assert result['ports'][1] == 8001
    finally:
        os.unlink(yaml_file)


def test_read_config_yaml_file_not_found():
    """Test reading non-existent YAML file"""
    from src.config.config import read_config_yaml
    
    with pytest.raises(FileNotFoundError):
        read_config_yaml('nonexistent_file.yaml')


def test_readConfig_case_sensitive_keys():
    """Test that config keys can be read"""
    from src.config.config import read_config as readConfig
    
    # Create temporary config file
    # Note: ConfigParser lowercases keys by default
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write('[settings]\n')
        f.write('key1=Value1\n')
        f.write('key2=Value2\n')
        config_file = f.name
    
    try:
        result = readConfig('settings', config_file)
        # ConfigParser lowercases keys by default
        assert 'key1' in result or 'key2' in result
    finally:
        os.unlink(config_file)
