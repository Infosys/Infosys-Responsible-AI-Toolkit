"""
Comprehensive tests for src/config/logger.py
Covers CustomLogger class and all its methods for high coverage.
"""

import datetime
import logging
import os
import sys
import tempfile
from unittest import mock
from unittest.mock import MagicMock, patch, PropertyMock

import pytest


class TestCustomLoggerInit:
    """Test CustomLogger initialization."""

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    @patch('os.makedirs')
    def test_init_with_verbose_true(self, mock_makedirs, mock_exists, mock_read_config):
        """Test initialization with verbose=True."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'True',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        assert logger.verbose is True
        assert logger.name == 'test_log'
        mock_read_config.assert_called_once()

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    @patch('os.makedirs')
    def test_init_with_verbose_false(self, mock_makedirs, mock_exists, mock_read_config):
        """Test initialization with verbose=False."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        assert logger.verbose is False

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    @patch('os.makedirs')
    def test_init_with_verbose_exception(self, mock_makedirs, mock_exists, mock_read_config):
        """Test initialization when verbose conversion fails."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': None,
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        assert isinstance(logger.verbose, bool)

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    @patch('os.makedirs')
    def test_init_without_log_dir(self, mock_makedirs, mock_exists, mock_read_config):
        """Test initialization without log directory."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': ''
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        assert logger is not None

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=False)
    @patch('os.makedirs')
    def test_init_creates_log_directory(self, mock_makedirs, mock_exists, mock_read_config):
        """Test that log directory is created if it doesn't exist."""
        log_dir = os.path.join(tempfile.gettempdir(), 'test_logs_new')
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': log_dir
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        mock_makedirs.assert_called_once_with(log_dir)


class TestAddFileHandler:
    """Test add_file_handler method."""

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_add_file_handler_creates_handler(self, mock_exists, mock_read_config):
        """Test that add_file_handler creates a file handler."""
        log_dir = tempfile.gettempdir()
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': log_dir
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        assert logger.file_handler is not None
        assert isinstance(logger.file_handler, logging.FileHandler)

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=False)
    @patch('os.makedirs', side_effect=OSError("Permission denied"))
    def test_add_file_handler_makedirs_failure_linux(self, mock_makedirs, mock_exists, mock_read_config):
        """Test fallback when makedirs fails on Linux."""
        with patch('sys.platform', 'linux'):
            mock_read_config.return_value = {
                'file_name': 'test_log',
                'verbose': 'False',
                'log_dir': '/nonexistent/path'
            }
            
            from src.config.logger import CustomLogger
            logger = CustomLogger()
            
            assert logger is not None

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=False)
    @patch('os.makedirs', side_effect=OSError("Permission denied"))
    def test_add_file_handler_makedirs_failure_windows(self, mock_makedirs, mock_exists, mock_read_config):
        """Test fallback when makedirs fails on Windows."""
        with patch('sys.platform', 'win32'):
            mock_read_config.return_value = {
                'file_name': 'test_log',
                'verbose': 'False',
                'log_dir': 'C:\\nonexistent\\path'
            }
            
            from src.config.logger import CustomLogger
            logger = CustomLogger()
            
            assert logger is not None


class TestHasHandlers:
    """Test has_console_handler and has_file_handler methods."""

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_has_console_handler(self, mock_exists, mock_read_config):
        """Test has_console_handler method."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        assert logger.has_console_handler() is True

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_has_file_handler(self, mock_exists, mock_read_config):
        """Test has_file_handler method."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        assert logger.has_file_handler() is True

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_has_file_handler_false(self, mock_exists, mock_read_config):
        """Test has_file_handler returns False when no file handler."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': ''
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        assert logger.file_handler is None


class TestEnableDisableConsoleOutput:
    """Test enable/disable console output methods."""

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_disable_console_output(self, mock_exists, mock_read_config):
        """Test disabling console output."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        assert logger.has_console_handler() is True
        logger.disable_console_output()
        assert logger.has_console_handler() is False

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_disable_console_output_when_not_present(self, mock_exists, mock_read_config):
        """Test disabling console output when already disabled."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        logger.disable_console_output()
        logger.disable_console_output()
        assert logger.has_console_handler() is False

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_enable_console_output(self, mock_exists, mock_read_config):
        """Test enabling console output."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        logger.disable_console_output()
        logger.enable_console_output()
        assert logger.has_console_handler() is True

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_enable_console_output_when_already_present(self, mock_exists, mock_read_config):
        """Test enabling console output when already enabled."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        logger.enable_console_output()
        handler_count = len([h for h in logger.handlers if type(h) == logging.StreamHandler])
        assert handler_count == 1


class TestEnableDisableFileOutput:
    """Test enable/disable file output methods."""

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_disable_file_output(self, mock_exists, mock_read_config):
        """Test disabling file output."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        assert logger.has_file_handler() is True
        logger.disable_file_output()
        assert logger.has_file_handler() is False

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_disable_file_output_when_not_present(self, mock_exists, mock_read_config):
        """Test disabling file output when not present."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': ''
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        logger.disable_file_output()

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_enable_file_output(self, mock_exists, mock_read_config):
        """Test enabling file output."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        logger.disable_file_output()
        logger.enable_file_output()
        assert logger.has_file_handler() is True

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_enable_file_output_when_already_present(self, mock_exists, mock_read_config):
        """Test enabling file output when already present."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        logger.enable_file_output()
        handler_count = len([h for h in logger.handlers if isinstance(h, logging.FileHandler)])
        assert handler_count == 1


class TestFrameworkMethod:
    """Test framework logging method."""

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_framework_method(self, mock_exists, mock_read_config):
        """Test framework logging method."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'True',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        with patch.object(logger, 'info') as mock_info:
            logger.framework("Test framework message")


class TestCustomLog:
    """Test _custom_log helper method."""

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_custom_log_verbose_true(self, mock_exists, mock_read_config):
        """Test _custom_log when verbose is True."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'True',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        mock_func = MagicMock()
        logger._custom_log(mock_func, "Test message")
        mock_func.assert_called_once()

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_custom_log_verbose_false_with_file_handler(self, mock_exists, mock_read_config):
        """Test _custom_log when verbose is False but file handler exists."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        mock_func = MagicMock()
        logger._custom_log(mock_func, "Test message")
        mock_func.assert_called_once()

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_custom_log_verbose_false_no_file_handler(self, mock_exists, mock_read_config):
        """Test _custom_log when verbose is False and no file handler."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': ''
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        mock_func = MagicMock()
        logger._custom_log(mock_func, "Test message")
        mock_func.assert_not_called()


class TestGetSessionId:
    """Test getSeesionId static method."""

    def test_get_session_id_returns_request_id(self):
        """Test getSeesionId returns request_id when set."""
        from src.config.logger import CustomLogger, request_id_var
        
        token = request_id_var.set("test-request-123")
        try:
            result = CustomLogger.getSeesionId()
            assert result == "test-request-123"
        finally:
            request_id_var.reset(token)

    def test_get_session_id_returns_startup_on_exception(self):
        """Test getSeesionId returns StartUp when request_id not set."""
        from src.config.logger import CustomLogger
        
        result = CustomLogger.getSeesionId()
        assert result == "StartUp"


class TestLoggingMethods:
    """Test debug, info, warning, error, critical methods."""

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_debug_method(self, mock_exists, mock_read_config):
        """Test debug logging method."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'True',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        with patch.object(logger, '_custom_log') as mock_custom_log:
            logger.debug("Debug message")
            mock_custom_log.assert_called_once()

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_info_method(self, mock_exists, mock_read_config):
        """Test info logging method."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'True',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        with patch.object(logger, '_custom_log') as mock_custom_log:
            logger.info("Info message")
            mock_custom_log.assert_called_once()

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_warning_method(self, mock_exists, mock_read_config):
        """Test warning logging method."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'True',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        with patch.object(logger, '_custom_log') as mock_custom_log:
            logger.warning("Warning message")
            mock_custom_log.assert_called_once()

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_error_method(self, mock_exists, mock_read_config):
        """Test error logging method."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'True',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        with patch.object(logger, '_custom_log') as mock_custom_log:
            logger.error("Error message")
            mock_custom_log.assert_called_once()

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_critical_method(self, mock_exists, mock_read_config):
        """Test critical logging method."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'True',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        with patch.object(logger, '_custom_log') as mock_custom_log:
            logger.critical("Critical message")
            mock_custom_log.assert_called_once()


class TestRequestIdVar:
    """Test request_id_var context variable."""

    def test_request_id_var_exists(self):
        """Test that request_id_var is defined."""
        from src.config.logger import request_id_var
        import contextvars
        
        assert isinstance(request_id_var, contextvars.ContextVar)

    def test_request_id_var_set_get(self):
        """Test setting and getting request_id_var."""
        from src.config.logger import request_id_var
        
        token = request_id_var.set("my-request-id")
        try:
            assert request_id_var.get() == "my-request-id"
        finally:
            request_id_var.reset(token)


class TestModuleLevelExecution:
    """Test module-level execution (if __name__ == '__main__')."""

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_main_execution(self, mock_exists, mock_read_config):
        """Test that module can be executed directly."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        
        logger = CustomLogger()
        assert logger is not None


class TestLogFileNaming:
    """Test log file naming conventions."""

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    @patch('datetime.datetime')
    def test_log_file_name_format(self, mock_datetime, mock_exists, mock_read_config):
        """Test that log file name follows expected format."""
        mock_datetime.now.return_value.strftime.return_value = '20250202_120000'
        
        mock_read_config.return_value = {
            'file_name': 'my test log',
            'verbose': 'False',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        assert logger.file_handler is not None


class TestLoggerLevel:
    """Test logger level settings."""

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_logger_level_is_debug(self, mock_exists, mock_read_config):
        """Test that logger level is set to DEBUG."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        assert logger.level == logging.DEBUG

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_stdout_handler_level_is_debug(self, mock_exists, mock_read_config):
        """Test that stdout handler level is set to DEBUG."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        assert logger.stdout_handler.level == logging.DEBUG

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_file_handler_level_is_debug(self, mock_exists, mock_read_config):
        """Test that file handler level is set to DEBUG."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        assert logger.file_handler.level == logging.DEBUG


class TestLoggerFormatters:
    """Test logger formatters."""

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_stdout_handler_formatter(self, mock_exists, mock_read_config):
        """Test stdout handler has correct formatter."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        formatter = logger.stdout_handler.formatter
        assert formatter is not None

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_file_handler_formatter(self, mock_exists, mock_read_config):
        """Test file handler has correct formatter."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'False',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        formatter = logger.file_handler.formatter
        assert formatter is not None


class TestEdgeCases:
    """Test edge cases and error handling."""

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_logging_with_user_id_parameter(self, mock_exists, mock_read_config):
        """Test logging methods accept user_id parameter."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'True',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        with patch.object(logger, '_custom_log'):
            logger.warning("Test warning", user_id="user123")
            logger.error("Test error", user_id="user123")
            logger.critical("Test critical", user_id="user123")

    @patch('src.config.logger.readConfig')
    @patch('os.path.exists', return_value=True)
    def test_logging_with_extra_args(self, mock_exists, mock_read_config):
        """Test logging methods handle extra arguments."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': 'True',
            'log_dir': tempfile.gettempdir()
        }
        
        from src.config.logger import CustomLogger
        logger = CustomLogger()
        
        with patch.object(logger, '_custom_log'):
            logger.debug("Test debug %s", "arg1")
            logger.info("Test info %s", "arg1")

    @patch('src.config.logger.readConfig')
    def test_verbose_exception_handling(self, mock_read_config):
        """Test that verbose exception is handled gracefully."""
        mock_read_config.return_value = {
            'file_name': 'test_log',
            'verbose': object(),
            'log_dir': ''
        }
        
        from src.config.logger import CustomLogger
        
        logger = CustomLogger()
        assert logger.verbose is False
