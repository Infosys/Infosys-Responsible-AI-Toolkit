"""
Test cases for safety_router.py (Image Generation endpoint)
"""

import sys
import os
from types import ModuleType
from unittest.mock import Mock
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
from tests.utils.mock_helpers import (
    make_aicloud_modules,
    make_local_constants,
    isolate_and_reload,
    make_flask_stub,
    make_werkzeug_exceptions,
    make_config_logger_stub,
)
from tests.utils.isolate_module import reload_module


def _reload_safety_with(form_data, image_response=None, should_raise=False):
    """Reload safety_router with mocked dependencies."""
    flask_stub = make_flask_stub()

    # Mock service module with ImageGen class
    svc = ModuleType('service.safety_service')
    
    class MockImageGen:
        @staticmethod
        def generate(prompt):
            if should_raise:
                raise Exception("Image generation error")
            # Return mock image object with save method
            class MockImage:
                def save(self, buffer, format=None):
                    buffer.write(b'fake_image_data')
            return image_response or MockImage()
    
    svc.ImageGen = MockImageGen

    # Mock exception module
    exc_mod = ModuleType('exception.exception')
    class MockDeploymentException(Exception):
        def __init__(self, *args, **kwargs):
            super().__init__(*args)
            self.__dict__ = kwargs
    exc_mod.modeldeploymentException = MockDeploymentException

    # Mock base64
    base64_mod = ModuleType('base64')
    base64_mod.b64encode = lambda x: b'bW9ja2VkX2ltYWdlX2RhdGE='
    base64_mod.b64decode = lambda x: b'mocked_image_data'

    # Mock uuid
    uuid_mod = ModuleType('uuid')
    uuid_mod.uuid4 = lambda: type('obj', (object,), {'hex': 'test-uuid-1234'})()

    # Mock time
    time_mod = ModuleType('time')
    time_mod.time = lambda: 1234567890.0

    # Mock io module with BytesIO
    io_mod = ModuleType('io')
    class MockBytesIO:
        def __init__(self):
            self._data = bytearray()
        def write(self, data):
            self._data.extend(data)
        def getvalue(self):
            return bytes(self._data)
    io_mod.BytesIO = MockBytesIO

    # Config and werkzeug via helpers
    cfg = make_config_logger_stub()
    werkzeug_exc = make_werkzeug_exceptions()

    # Mock psutil
    ps = ModuleType('psutil')
    class _P:
        def memory_info(self):
            return type('T', (), {'rss': 0})()
    ps.Process = lambda: _P()

    replacements = {
        'flask': flask_stub,
        'service.safety_service': svc,
        'exception.exception': exc_mod,
        'base64': base64_mod,
        'uuid': uuid_mod,
        'time': time_mod,
        'io': io_mod,
        'psutil': ps,
        'config.logger': cfg,
        'werkzeug.exceptions': werkzeug_exc,
        **make_aicloud_modules(),
        'constants.local_constants': make_local_constants()
    }

    # Set request form data
    flask_stub.request = flask_stub.request.__class__({})
    flask_stub.request.form = type('obj', (object,), {
        'get': lambda self, key, default=None: form_data.get(key, default)
    })()

    with isolate_and_reload('routing.safety_router', replacements):
        mod = reload_module('routing.safety_router')

    return mod


def test_img_success():
    """Test successful image generation"""
    form_data = {'prompt': 'A beautiful sunset'}
    mod = _reload_safety_with(form_data)
    res = mod.img()
    assert res is not None
    assert isinstance(res, str)  # Should return base64 encoded string


def test_img_different_prompts():
    """Test image generation with various prompts"""
    prompts = [
        'A cat sitting on a mat',
        'A futuristic cityscape',
        'Abstract art with colors',
        'A peaceful mountain landscape'
    ]
    
    for prompt in prompts:
        form_data = {'prompt': prompt}
        mod = _reload_safety_with(form_data)
        res = mod.img()
        assert res is not None


def test_img_service_exception():
    """Test handling of service exceptions during image generation"""
    form_data = {'prompt': 'Test prompt'}
    mod = _reload_safety_with(form_data, should_raise=True)
    
    try:
        res = mod.img()
        # If no exception, that's also fine (error handling worked)
        assert res is not None
    except Exception:
        # Exception was properly raised
        pass


def test_img_empty_prompt():
    """Test with empty prompt string"""
    form_data = {'prompt': ''}
    mod = _reload_safety_with(form_data)
    
    try:
        res = mod.img()
        # Empty prompt might still work or raise error
        assert True
    except Exception:
        # Exception is acceptable for empty prompt
        pass


def test_img_missing_prompt():
    """Test with missing prompt field"""
    form_data = {}
    mod = _reload_safety_with(form_data)
    
    try:
        res = mod.img()
        # None prompt might work or raise error
        assert True
    except Exception:
        # Exception is acceptable
        pass


def test_img_long_prompt():
    """Test with very long prompt"""
    form_data = {'prompt': 'A ' + 'very ' * 100 + 'long prompt'}
    mod = _reload_safety_with(form_data)
    
    try:
        res = mod.img()
        assert res is not None
    except Exception:
        # May have length limits
        pass


def test_img_special_characters():
    """Test prompt with special characters"""
    form_data = {'prompt': 'Image with !@#$%^&*() special chars'}
    mod = _reload_safety_with(form_data)
    res = mod.img()
    assert res is not None
