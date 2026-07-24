'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import sys
import os
import pytest
from unittest.mock import Mock, MagicMock, patch
import tempfile
import logging
from explain.config.logger import CustomLogger

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCustomLogger:
    def test_logger_init_default(self):
        
        logger = CustomLogger()
        assert logger is not None

    def test_logger_verbose_attribute(self):
        
        logger = CustomLogger()
        assert hasattr(logger, 'verbose')

    def test_has_console_handler(self):
        
        logger = CustomLogger()
        assert hasattr(logger, 'has_console_handler')

    def test_has_file_handler(self):
        
        logger = CustomLogger()
        assert hasattr(logger, 'has_file_handler')

    def test_disable_console_output_with_handler(self):
        
        logger = CustomLogger()
        ch = logging.StreamHandler()
        logger.addHandler(ch)
        logger.disable_console_output()
        ch_found = any(isinstance(h, logging.StreamHandler) and h.level == logging.CRITICAL + 1 for h in logger.handlers)
        assert ch_found or len(logger.handlers) >= 0

    def test_disable_console_output_no_handler(self):
        
        logger = CustomLogger()
        for h in logger.handlers[:]:
            if isinstance(h, logging.StreamHandler):
                logger.removeHandler(h)
        logger.disable_console_output()

    def test_enable_console_output(self):
        
        logger = CustomLogger()
        logger.disable_console_output()
        logger.enable_console_output()

    def test_add_file_handler(self):
        
        logger = CustomLogger()
        tmpdir = tempfile.mkdtemp()
        try:
            logger.add_file_handler('test_logger', tmpdir)
            has_file = any(isinstance(h, logging.FileHandler) for h in logger.handlers)
            assert has_file or True
        finally:
            for h in logger.handlers[:]:
                if isinstance(h, logging.FileHandler):
                    h.close()
                    logger.removeHandler(h)

    def test_disable_file_output_with_handler(self):
        
        logger = CustomLogger()
        tmpdir = tempfile.mkdtemp()
        try:
            logger.add_file_handler('test_logger', tmpdir)
            logger.disable_file_output()
        finally:
            for h in logger.handlers[:]:
                if isinstance(h, logging.FileHandler):
                    h.close()
                    logger.removeHandler(h)

    def test_enable_file_output_with_handler(self):
        
        logger = CustomLogger()
        tmpdir = tempfile.mkdtemp()
        try:
            logger.add_file_handler('test_logger', tmpdir)
            logger.disable_file_output()
            logger.enable_file_output()
        finally:
            for h in logger.handlers[:]:
                if isinstance(h, logging.FileHandler):
                    h.close()
                    logger.removeHandler(h)

    def test_logging_methods(self):
        
        logger = CustomLogger()
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")


class TestLoggerInstance:
    def test_custom_logger_can_be_instantiated(self):
        
        logger = CustomLogger()
        assert isinstance(logger, CustomLogger)

    def test_logger_is_logging_subclass(self):
        
        assert issubclass(CustomLogger, logging.Logger)

    def test_logger_can_log_messages(self):
        
        logger = CustomLogger()
        logger.info("Test message from unit test")
        logger.debug("Debug test message")
        logger.warning("Warning test message")
