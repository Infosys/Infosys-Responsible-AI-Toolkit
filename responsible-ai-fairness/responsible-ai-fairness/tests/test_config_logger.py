import pytest
import os
import tempfile
import logging
import time
from unittest.mock import patch
import gc

from fairness.config.logger import CustomLogger


@pytest.fixture
def temp_log_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def cleanup_logging():
    yield
    for logger_name in list(logging.Logger.manager.loggerDict.keys()):
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


class TestCustomLoggerInitialization:
    def test_logger_initialization(self, temp_log_dir, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'False',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            assert logger is not None
            assert isinstance(logger, logging.Logger)
            assert logger.level == logging.DEBUG
    
    def test_verbose_true(self, temp_log_dir, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'True',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            assert logger.verbose is True
    
    def test_console_handler_added(self, temp_log_dir, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'False',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            assert logger.has_console_handler()
    
    def test_file_handler_added(self, temp_log_dir, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'False',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            assert logger.has_file_handler()


class TestHandlerManagement:
    def test_disable_console(self, temp_log_dir, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'False',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            logger.disable_console_output()
            assert not logger.has_console_handler()
    
    def test_enable_console(self, temp_log_dir, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'False',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            logger.disable_console_output()
            logger.enable_console_output()
            assert logger.has_console_handler()


class TestLoggingFunctionality:
    def test_info_logging_verbose(self, temp_log_dir, cleanup_logging, capsys):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'True',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            logger.info("Test message")
            captured = capsys.readouterr()
            assert "Test message" in captured.out
    
    def test_framework_logging(self, temp_log_dir, cleanup_logging, capsys):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'False',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            logger.framework("Framework message")
            captured = capsys.readouterr()
            assert "Framework message" in captured.out


class TestEdgeCases:
    def test_empty_message(self, temp_log_dir, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'True',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            logger.info("")
            assert logger is not None
    
    def test_no_log_dir(self, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'True',
            'log_dir': ''
        }):
            logger = CustomLogger()
            assert logger.has_console_handler()
            assert not logger.has_file_handler()


class TestPerformance:
    def test_logging_speed(self, temp_log_dir, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'False',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            start_time = time.perf_counter()
            for i in range(100):
                logger.info(f"Message {i}")
            end_time = time.perf_counter()
            assert (end_time - start_time) < 1.0


class TestRegression:
    def test_is_logger_subclass(self):
        assert issubclass(CustomLogger, logging.Logger)
    
    def test_required_methods_exist(self, temp_log_dir, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'False',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            assert hasattr(logger, 'has_console_handler')
            assert hasattr(logger, 'has_file_handler')
            assert hasattr(logger, 'framework')


class TestErrorHandling:
    def test_invalid_verbose_defaults_false(self, temp_log_dir, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'invalid',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            assert logger.verbose is False
    
    def test_log_with_exception(self, temp_log_dir, cleanup_logging, capsys):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'True',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            try:
                raise ValueError("Test exception")
            except ValueError:
                logger.error("Error occurred", exc_info=True)
            captured = capsys.readouterr()
            assert "Error occurred" in captured.out
    
    def test_log_directory_creation_error(self, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'False',
            'log_dir': '/invalid/path'
        }), patch('os.makedirs', side_effect=Exception("Cannot create")):
            logger = CustomLogger()
            assert logger is not None


class TestResourceManagement:
    def test_no_memory_leaks(self, temp_log_dir, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'False',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            gc.collect()
            initial = len(gc.get_objects())
            for i in range(100):
                logger.info(f"Message {i}")
            gc.collect()
            final = len(gc.get_objects())
            growth = final - initial
            assert growth < 500
    
    def test_file_handler_cleanup(self, temp_log_dir, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'False',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            assert logger.has_file_handler()
            logger.disable_file_output()
            assert not logger.has_file_handler()


class TestIntegration:
    def test_log_file_created(self, temp_log_dir, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'integration_logger',
            'verbose': 'False',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            logger.info("Test message")
            for handler in logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    handler.flush()
            log_files = [f for f in os.listdir(temp_log_dir) if f.startswith('integration_logger')]
            assert len(log_files) > 0
    
    def test_all_log_levels(self, temp_log_dir, cleanup_logging, capsys):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'True',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            logger.debug("Debug")
            logger.info("Info")
            logger.warning("Warning")
            logger.error("Error")
            logger.critical("Critical")
            captured = capsys.readouterr()
            assert all(x in captured.out for x in ["Debug", "Info", "Warning", "Error", "Critical"])
    
    def test_logging_hierarchy(self, temp_log_dir, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'False',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            assert logger.level == logging.DEBUG
            assert logger.isEnabledFor(logging.DEBUG)
            assert logger.isEnabledFor(logging.INFO)


class TestCodeQuality:
    def test_class_has_docstring(self):
        assert CustomLogger.__init__.__doc__ is not None
    
    def test_methods_callable(self, temp_log_dir, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'False',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            assert callable(logger.debug)
            assert callable(logger.info)
            assert callable(logger.framework)
            assert callable(logger.add_file_handler)
    
    def test_handler_attributes_exist(self, temp_log_dir, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'False',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            assert hasattr(logger, 'stdout_handler')
            assert hasattr(logger, 'file_handler')
            assert hasattr(logger, 'verbose')


class TestSecurity:
    def test_special_chars_in_message(self, temp_log_dir, cleanup_logging, capsys):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'True',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            special = "Test: !@#$%^&*()_+-=[]{}|;':,.<>?/"
            logger.info(special)
            captured = capsys.readouterr()
            assert special in captured.out
    
    def test_very_long_message(self, temp_log_dir, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'False',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            long_msg = "x" * 10000
            logger.info(long_msg)
            assert logger is not None


class TestScalability:
    def test_bulk_logging(self, temp_log_dir, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'False',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            start = time.perf_counter()
            for i in range(500):
                logger.info(f"Message {i}")
            duration = time.perf_counter() - start
            assert duration < 1.0
    
    def test_handler_toggle_performance(self, temp_log_dir, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'False',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            start = time.perf_counter()
            for _ in range(50):
                logger.disable_console_output()
                logger.enable_console_output()
            duration = time.perf_counter() - start
            assert duration < 0.1

