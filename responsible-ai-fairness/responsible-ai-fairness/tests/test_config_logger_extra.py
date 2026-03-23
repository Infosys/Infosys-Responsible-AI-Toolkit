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
    # Close all logger handlers to release file locks (especially important on Windows)
    for logger_name in list(logging.Logger.manager.loggerDict.keys()):
        logger = logging.getLogger(logger_name)
        handlers = logger.handlers[:]
        for handler in handlers:
            try:
                handler.flush()
                handler.close()
            except:
                pass
            try:
                logger.removeHandler(handler)
            except:
                pass
    # Force garbage collection to release file handles
    gc.collect()
    # Small delay for Windows file system
    import time
    time.sleep(0.1)




class TestCoverage:
    def test_verbose_false_no_console_output(self, temp_log_dir, cleanup_logging, capsys):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'False',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            logger.info("Should not appear in console")
            captured = capsys.readouterr()
            assert "Should not appear in console" not in captured.out
    
    def test_disable_file_handler(self, temp_log_dir, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'False',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            assert logger.has_file_handler()
            logger.close()
            logger.disable_file_output()
            assert not logger.has_file_handler()
            logger.enable_file_output()
            assert logger.has_file_handler()
            logger.close()
    
    def test_double_enable_no_duplicate(self, temp_log_dir, cleanup_logging):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'False',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            initial_count = len([h for h in logger.handlers if type(h) == logging.StreamHandler])
            logger.enable_console_output()
            final_count = len([h for h in logger.handlers if type(h) == logging.StreamHandler])
            assert initial_count == final_count
            logger.close()
    
    def test_log_with_format_args(self, temp_log_dir, cleanup_logging, capsys):
        with patch('fairness.config.logger.readConfig', return_value={
            'file_name': 'test_logger',
            'verbose': 'True',
            'log_dir': temp_log_dir
        }):
            logger = CustomLogger()
            logger.info("Value: %s, Number: %d", "test", 42)
            captured = capsys.readouterr()
            assert "Value: test" in captured.out
            assert "Number: 42" in captured.out
            logger.close()


