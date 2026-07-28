import pytest
import contextvars
from tests.utils.mock_helpers import isolate_and_reload
from tests.utils.isolate_module import reload_module

@pytest.fixture(scope='function')
def logger_mod():
    """Reload config.logger in isolated context"""
    import sys as _sys
    for key in list(_sys.modules.keys()):
        if 'config.logger' in key:
            del _sys.modules[key]
    
    replacements = {}
    with isolate_and_reload('config.logger', replacements):
        yield reload_module('config.logger')

def test_logger_has_request_id_var(logger_mod):
    assert hasattr(logger_mod, 'request_id_var')
    assert isinstance(logger_mod.request_id_var, contextvars.ContextVar)

def test_logger_has_custom_logger_class(logger_mod):
    assert hasattr(logger_mod, 'CustomLogger')
    assert callable(logger_mod.CustomLogger)

def test_custom_logger_init(logger_mod):
    logger = logger_mod.CustomLogger()
    assert logger is not None

def test_custom_logger_debug(logger_mod):
    logger = logger_mod.CustomLogger()
    logger.debug("Test debug message")

def test_custom_logger_info(logger_mod):
    logger = logger_mod.CustomLogger()
    logger.info("Test info message")

def test_custom_logger_warning(logger_mod):
    logger = logger_mod.CustomLogger()
    logger.warning("Test warning message")

def test_custom_logger_error(logger_mod):
    logger = logger_mod.CustomLogger()
    logger.error("Test error message")

def test_custom_logger_critical(logger_mod):
    logger = logger_mod.CustomLogger()
    logger.critical("Test critical message")

def test_custom_logger_framework(logger_mod):
    logger = logger_mod.CustomLogger()
    logger.framework("Test framework message")

def test_custom_logger_has_console_handler_method(logger_mod):
    logger = logger_mod.CustomLogger()
    assert hasattr(logger, 'has_console_handler')
    assert callable(logger.has_console_handler)

def test_custom_logger_disable_console_output(logger_mod):
    logger = logger_mod.CustomLogger()
    logger.disable_console_output()

def test_custom_logger_enable_console_output(logger_mod):
    logger = logger_mod.CustomLogger()
    logger.enable_console_output()

def test_custom_logger_has_file_handler(logger_mod):
    logger = logger_mod.CustomLogger()
    assert hasattr(logger, 'file_handler')
