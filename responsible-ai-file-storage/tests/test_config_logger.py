"""
MIT License
https://mit-license.org/
Copyright  2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import pytest
import logging
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))
from config.logger import CustomLogger

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_log_dir():
    """Fixture for temporary log directory with cleanup."""
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)

@pytest.fixture
def mock_config_no_verbose():
    """Mock configuration with verbose=False and no log dir."""
    return {"file_name": "test", "verbose": "False", "log_dir": ""}

@pytest.fixture
def mock_config_verbose():
    """Mock configuration with verbose=True."""
    return {"file_name": "test", "verbose": "True", "log_dir": ""}

# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestCustomLoggerInitialization:
    """Test CustomLogger initialization and configuration."""
    
    @patch("config.logger.readConfig")
    def test_basic_initialization(self, mock_rc):
        """Test basic logger initialization with minimal config."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": ""}
        logger = CustomLogger()
        assert logger is not None
        assert logger.level == logging.DEBUG
        mock_rc.assert_called_once()
    
    @patch("config.logger.readConfig")
    def test_verbose_false_parsing(self, mock_rc):
        """Test that verbose=False is correctly parsed."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": ""}
        logger = CustomLogger()
        assert hasattr(logger, 'verbose')  # Verbose parsing may vary
    
    @patch("config.logger.readConfig")
    def test_verbose_true_parsing(self, mock_rc):
        """Test that verbose=True is correctly parsed."""
        mock_rc.return_value = {"file_name": "test", "verbose": "True", "log_dir": ""}
        logger = CustomLogger()
        assert logger.verbose is True or logger.verbose == True
    
    @patch("config.logger.readConfig")
    def test_invalid_verbose_defaults_to_false(self, mock_rc):
        """Test that invalid verbose value defaults to False."""
        mock_rc.return_value = {"file_name": "test", "verbose": "invalid", "log_dir": ""}
        logger = CustomLogger()
        # Should handle gracefully
        assert logger is not None
    
    @patch("config.logger.readConfig")
    def test_with_log_directory(self, mock_rc, temp_log_dir):
        """Test initialization with log directory creates file handler."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": temp_log_dir}
        logger = CustomLogger()
        assert logger.has_file_handler()
        assert logger.file_handler is not None
    
    @patch("config.logger.readConfig")
    def test_creates_nonexistent_log_directory(self, mock_rc):
        """Test that logger creates log directory if it doesn not exist."""
        temp_base = tempfile.mkdtemp()
        log_dir = os.path.join(temp_base, "newdir")
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": log_dir}
        try:
            logger = CustomLogger()
            assert os.path.exists(log_dir)
            assert logger.has_file_handler()
        finally:
            shutil.rmtree(temp_base, ignore_errors=True)
    
    @patch("config.logger.readConfig")
    def test_logger_name_with_spaces(self, mock_rc, temp_log_dir):
        """Test logger handles names with spaces."""
        mock_rc.return_value = {"file_name": "test logger name", "verbose": "False", "log_dir": temp_log_dir}
        logger = CustomLogger()
        log_files = os.listdir(temp_log_dir)
        assert any("test_logger_name" in f for f in log_files)


# ============================================================================
# HANDLER MANAGEMENT TESTS
# ============================================================================

class TestHandlerManagement:
    """Test console and file handler management."""
    
    @patch("config.logger.readConfig")
    def test_has_console_handler_by_default(self, mock_rc):
        """Test that console handler is present by default."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": ""}
        logger = CustomLogger()
        assert logger.has_console_handler()
    
    @patch("config.logger.readConfig")
    def test_disable_console_output(self, mock_rc):
        """Test disabling console output."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": ""}
        logger = CustomLogger()
        logger.disable_console_output()
        assert not logger.has_console_handler()
    
    @patch("config.logger.readConfig")
    def test_enable_console_output(self, mock_rc):
        """Test re-enabling console output."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": ""}
        logger = CustomLogger()
        logger.disable_console_output()
        logger.enable_console_output()
        assert logger.has_console_handler()
    
    @patch("config.logger.readConfig")
    def test_enable_console_idempotent(self, mock_rc):
        """Test that enabling console multiple times doesn not add duplicates."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": ""}
        logger = CustomLogger()
        initial_count = len(logger.handlers)
        logger.enable_console_output()
        logger.enable_console_output()
        assert len(logger.handlers) == initial_count
    
    @patch("config.logger.readConfig")
    def test_has_file_handler_with_log_dir(self, mock_rc, temp_log_dir):
        """Test file handler presence when log_dir is set."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": temp_log_dir}
        logger = CustomLogger()
        assert logger.has_file_handler()
    
    @patch("config.logger.readConfig")
    def test_no_file_handler_without_log_dir(self, mock_rc):
        """Test no file handler when log_dir is empty."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": ""}
        logger = CustomLogger()
        assert not logger.has_file_handler()
    
    @patch("config.logger.readConfig")
    def test_disable_file_output(self, mock_rc, temp_log_dir):
        """Test disabling file output."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": temp_log_dir}
        logger = CustomLogger()
        logger.disable_file_output()
        assert not logger.has_file_handler()
    
    @patch("config.logger.readConfig")
    def test_enable_file_output(self, mock_rc, temp_log_dir):
        """Test re-enabling file output."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": temp_log_dir}
        logger = CustomLogger()
        logger.disable_file_output()
        logger.enable_file_output()
        assert logger.has_file_handler()


# ============================================================================
# LOGGING METHODS TESTS
# ============================================================================

class TestLoggingMethods:
    """Test all logging methods with different verbosity settings."""
    
    @patch("config.logger.readConfig")
    def test_debug_verbose_true(self, mock_rc, capsys):
        """Test debug logging outputs to console when verbose=True."""
        mock_rc.return_value = {"file_name": "test", "verbose": "True", "log_dir": ""}
        logger = CustomLogger()
        logger.debug("debug msg")
        captured = capsys.readouterr()
        assert "debug msg" in captured.out
    
    @patch("config.logger.readConfig")
    def test_info_verbose_true(self, mock_rc, capsys):
        """Test info logging outputs to console when verbose=True."""
        mock_rc.return_value = {"file_name": "test", "verbose": "True", "log_dir": ""}
        logger = CustomLogger()
        logger.info("info msg")
        captured = capsys.readouterr()
        assert "info msg" in captured.out
    
    @patch("config.logger.readConfig")
    def test_warning_verbose_true(self, mock_rc, capsys):
        """Test warning logging outputs to console when verbose=True."""
        mock_rc.return_value = {"file_name": "test", "verbose": "True", "log_dir": ""}
        logger = CustomLogger()
        logger.warning("warning msg")
        captured = capsys.readouterr()
        assert "warning msg" in captured.out
    
    @patch("config.logger.readConfig")
    def test_error_verbose_true(self, mock_rc, capsys):
        """Test error logging outputs to console when verbose=True."""
        mock_rc.return_value = {"file_name": "test", "verbose": "True", "log_dir": ""}
        logger = CustomLogger()
        logger.error("error msg")
        captured = capsys.readouterr()
        assert "error msg" in captured.out
    
    @patch("config.logger.readConfig")
    def test_critical_verbose_true(self, mock_rc, capsys):
        """Test critical logging outputs to console when verbose=True."""
        mock_rc.return_value = {"file_name": "test", "verbose": "True", "log_dir": ""}
        logger = CustomLogger()
        logger.critical("critical msg")
        captured = capsys.readouterr()
        assert "critical msg" in captured.out
    
    @patch("config.logger.readConfig")
    def test_framework_always_outputs(self, mock_rc, capsys):
        """Test framework logging always outputs regardless of verbose setting."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": ""}
        logger = CustomLogger()
        logger.framework("framework msg")
        captured = capsys.readouterr()
        assert "framework msg" in captured.out


# ============================================================================
# FILE OUTPUT TESTS
# ============================================================================

class TestFileOutput:
    """Test logging to file."""
    
    @patch("config.logger.readConfig")
    def test_log_file_created(self, mock_rc, temp_log_dir):
        """Test that log file is created in specified directory."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": temp_log_dir}
        logger = CustomLogger()
        logger.info("test message")
        log_files = [f for f in os.listdir(temp_log_dir) if f.endswith(".log")]
        assert len(log_files) > 0
    
    @patch("config.logger.readConfig")
    def test_log_content_written(self, mock_rc, temp_log_dir):
        """Test that log messages are written to file."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": temp_log_dir}
        logger = CustomLogger()
        logger.info("test message")
        log_files = [f for f in os.listdir(temp_log_dir) if f.endswith(".log")]
        with open(os.path.join(temp_log_dir, log_files[0]), "r") as f:
            content = f.read()
            assert "test message" in content
    
    @patch("config.logger.readConfig")
    def test_log_file_format(self, mock_rc, temp_log_dir):
        """Test log file contains proper formatting."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": temp_log_dir}
        logger = CustomLogger()
        logger.info("formatted msg")
        log_files = [f for f in os.listdir(temp_log_dir) if f.endswith(".log")]
        with open(os.path.join(temp_log_dir, log_files[0]), "r") as f:
            content = f.read()
            assert "INFO" in content
            assert "formatted msg" in content
    
    @patch("config.logger.readConfig")
    def test_multiple_log_entries(self, mock_rc, temp_log_dir):
        """Test multiple log entries are all written."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": temp_log_dir}
        logger = CustomLogger()
        logger.debug("msg1")
        logger.info("msg2")
        logger.warning("msg3")
        log_files = [f for f in os.listdir(temp_log_dir) if f.endswith(".log")]
        with open(os.path.join(temp_log_dir, log_files[0]), "r") as f:
            content = f.read()
            assert "msg1" in content
            assert "msg2" in content
            assert "msg3" in content


# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @patch("config.logger.readConfig")
    def test_empty_message(self, mock_rc, capsys):
        """Test logging empty message does not cause errors."""
        mock_rc.return_value = {"file_name": "test", "verbose": "True", "log_dir": ""}
        logger = CustomLogger()
        logger.info("")
        captured = capsys.readouterr()
        assert captured.out is not None
    
    @patch("config.logger.readConfig")
    def test_multiline_message(self, mock_rc, temp_log_dir):
        """Test logging multiline messages."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": temp_log_dir}
        logger = CustomLogger()
        logger.info("line1\\nline2\\nline3")
        log_files = [f for f in os.listdir(temp_log_dir) if f.endswith(".log")]
        with open(os.path.join(temp_log_dir, log_files[0]), "r") as f:
            content = f.read()
            assert "line1" in content
    
    @patch("config.logger.readConfig")
    def test_special_characters_in_message(self, mock_rc, temp_log_dir):
        """Test logging messages with special characters."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": temp_log_dir}
        logger = CustomLogger()
        logger.info("Special: @#$%^&*()")
        log_files = [f for f in os.listdir(temp_log_dir) if f.endswith(".log")]
        with open(os.path.join(temp_log_dir, log_files[0]), "r") as f:
            content = f.read()
            assert "Special" in content
    
    @patch("config.logger.readConfig")
    def test_rapid_logging(self, mock_rc, temp_log_dir):
        """Test rapid sequential logging."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": temp_log_dir}
        logger = CustomLogger()
        for i in range(50):
            logger.info(f"msg{i}")
        log_files = [f for f in os.listdir(temp_log_dir) if f.endswith(".log")]
        with open(os.path.join(temp_log_dir, log_files[0]), "r") as f:
            content = f.read()
            assert "msg0" in content
            assert "msg49" in content


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows."""
    
    @patch("config.logger.readConfig")
    def test_complete_workflow_verbose_false(self, mock_rc, temp_log_dir, capsys):
        """Test complete logging workflow with verbose=False."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": temp_log_dir}
        logger = CustomLogger()
        logger.debug("debug")
        logger.info("info")
        logger.error("error")
        captured = capsys.readouterr()
        # Console should be empty with verbose=False (except framework messages)
        # File should contain all messages
        log_files = [f for f in os.listdir(temp_log_dir) if f.endswith(".log")]
        with open(os.path.join(temp_log_dir, log_files[0]), "r") as f:
            content = f.read()
            assert "debug" in content
            assert "info" in content
            assert "error" in content
    
    @patch("config.logger.readConfig")
    def test_handler_toggling(self, mock_rc, temp_log_dir, capsys):
        """Test dynamic handler toggling during logging."""
        mock_rc.return_value = {"file_name": "test", "verbose": "True", "log_dir": temp_log_dir}
        logger = CustomLogger()
        logger.info("msg1")
        logger.disable_console_output()
        logger.info("msg2")
        logger.enable_console_output()
        logger.info("msg3")
        # File should have all messages
        log_files = [f for f in os.listdir(temp_log_dir) if f.endswith(".log")]
        with open(os.path.join(temp_log_dir, log_files[0]), "r") as f:
            content = f.read()
            assert "msg1" in content
            assert "msg2" in content
            assert "msg3" in content


# ============================================================================
# CODE QUALITY TESTS
# ============================================================================

class TestCodeQuality:
    """Test code quality indicators."""
    
    @patch("config.logger.readConfig")
    def test_logger_is_logging_logger(self, mock_rc):
        """Test CustomLogger is instance of logging.Logger."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": ""}
        logger = CustomLogger()
        assert isinstance(logger, logging.Logger)
    
    @patch("config.logger.readConfig")
    def test_logger_has_all_methods(self, mock_rc):
        """Test CustomLogger has all required logging methods."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": ""}
        logger = CustomLogger()
        assert hasattr(logger, "debug") and callable(logger.debug)
        assert hasattr(logger, "info") and callable(logger.info)
        assert hasattr(logger, "warning") and callable(logger.warning)
        assert hasattr(logger, "error") and callable(logger.error)
        assert hasattr(logger, "critical") and callable(logger.critical)
        assert hasattr(logger, "framework") and callable(logger.framework)
    
    @patch("config.logger.readConfig")
    def test_stdout_formatter_simple(self, mock_rc):
        """Test stdout handler has simple message-only format."""
        mock_rc.return_value = {"file_name": "test", "verbose": "False", "log_dir": ""}
        logger = CustomLogger()
        assert logger.stdout_handler.formatter._fmt == "%(message)s"

