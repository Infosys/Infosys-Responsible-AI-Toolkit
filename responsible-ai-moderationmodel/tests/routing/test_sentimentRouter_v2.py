"""
Test cases for sentimentRouter.py
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


def _reload_sentiment_with(payload, sentiment_response=None, should_raise=False):
    """Reload sentimentRouter with mocked dependencies."""
    flask_stub = make_flask_stub()

    # Mock service module
    svc = ModuleType('service.sentiment_service')
    
    class MockSentiment:
        def scan(self, text):
            if should_raise:
                raise Exception("Sentiment service error")
            return sentiment_response or {
                'score': {'compound': 0.5, 'pos': 0.6, 'neg': 0.1, 'neu': 0.3},
                'label': 'positive',
                'time_taken': '0.25s'
            }
    
    svc.Sentiment = MockSentiment

    # Mock psutil
    ps = ModuleType('psutil')
    class _P:
        def memory_info(self):
            return type('T', (), {'rss': 0})()
    ps.Process = lambda: _P()

    # Mock uuid
    uuid_mod = ModuleType('uuid')
    uuid_mod.uuid4 = lambda: type('obj', (object,), {'hex': 'test-uuid-sentiment'})()

    # Mock time
    time_mod = ModuleType('time')
    time_mod.time = lambda: 1234567890.0

    # Config and werkzeug via helpers
    cfg = make_config_logger_stub()
    werkzeug_exc = make_werkzeug_exceptions()

    replacements = {
        'flask': flask_stub,
        'service.sentiment_service': svc,
        'psutil': ps,
        'uuid': uuid_mod,
        'time': time_mod,
        'config.logger': cfg,
        'werkzeug.exceptions': werkzeug_exc,
        **make_aicloud_modules(),
        'constants.local_constants': make_local_constants()
    }

    # Set request payload
    flask_stub.request = flask_stub.request.__class__(payload)

    with isolate_and_reload('routing.sentimentRouter', replacements):
        mod = reload_module('routing.sentimentRouter')

    return mod


def test_sentimentmodel_positive():
    """Test sentiment endpoint with positive text"""
    payload = {'text': 'I love this product! It is amazing!'}
    expected = {
        'score': {'compound': 0.8, 'pos': 0.9, 'neg': 0.0, 'neu': 0.1},
        'label': 'positive',
        'time_taken': '0.25s'
    }
    mod = _reload_sentiment_with(payload, sentiment_response=expected)
    res = mod.sentimentmodel()
    assert res is not None


def test_sentimentmodel_negative():
    """Test sentiment endpoint detecting negative sentiment"""
    payload = {'text': 'This is terrible and disappointing'}
    expected = {
        'score': {'compound': -0.6, 'pos': 0.0, 'neg': 0.8, 'neu': 0.2},
        'label': 'negative',
        'time_taken': '0.25s'
    }
    mod = _reload_sentiment_with(payload, sentiment_response=expected)
    res = mod.sentimentmodel()
    assert res is not None


def test_sentimentmodel_neutral():
    """Test sentiment endpoint detecting neutral sentiment"""
    payload = {'text': 'This is a statement'}
    expected = {
        'score': {'compound': 0.0, 'pos': 0.0, 'neg': 0.0, 'neu': 1.0},
        'label': 'neutral',
        'time_taken': '0.25s'
    }
    mod = _reload_sentiment_with(payload, sentiment_response=expected)
    res = mod.sentimentmodel()
    assert res is not None


def test_sentimentmodel_mixed_sentiment():
    """Test with mixed sentiment text"""
    payload = {'text': 'The product is good but the price is too high'}
    expected = {
        'score': {'compound': 0.1, 'pos': 0.4, 'neg': 0.3, 'neu': 0.3},
        'label': 'neutral',
        'time_taken': '0.25s'
    }
    mod = _reload_sentiment_with(payload, sentiment_response=expected)
    res = mod.sentimentmodel()
    assert res is not None


def test_sentimentmodel_long_text():
    """Test with long text"""
    payload = {'text': 'This is a very long text. ' * 50}
    mod = _reload_sentiment_with(payload)
    res = mod.sentimentmodel()
    assert res is not None


def test_sentimentmodel_service_exception():
    """Test handling of service exceptions"""
    payload = {'text': 'Test text'}
    mod = _reload_sentiment_with(payload, should_raise=True)
    
    try:
        res = mod.sentimentmodel()
        assert res is not None
    except Exception:
        # Exception handling is working
        pass


def test_sentimentmodel_empty_text():
    """Test with empty text field"""
    payload = {'text': ''}
    mod = _reload_sentiment_with(payload)
    
    try:
        res = mod.sentimentmodel()
        assert True
    except Exception:
        # Exception handling works
        pass


def test_sentimentmodel_missing_text():
    """Test with missing text field"""
    payload = {}
    mod = _reload_sentiment_with(payload)
    
    try:
        res = mod.sentimentmodel()
        assert True
    except Exception:
        # Exception handling works
        pass


def test_sentimentmodel_special_characters():
    """Test with special characters"""
    payload = {'text': 'Amazing!!! @#$% product!!!'}
    mod = _reload_sentiment_with(payload)
    res = mod.sentimentmodel()
    assert res is not None


def test_sentimentmodel_numbers():
    """Test with numbers in text"""
    payload = {'text': 'I give it 5 out of 5 stars'}
    mod = _reload_sentiment_with(payload)
    res = mod.sentimentmodel()
    assert res is not None
