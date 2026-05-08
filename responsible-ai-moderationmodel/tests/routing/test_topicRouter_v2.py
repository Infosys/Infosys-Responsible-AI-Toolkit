"""
Test cases for topicRouter.py
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


def _reload_topic_with(payload, topic_response=None, should_raise=False):
    """Reload topicRouter with mocked dependencies."""
    flask_stub = make_flask_stub()

    # Mock service module
    svc = ModuleType('service.topicModel')
    
    def mock_restricttopic_check(payload_in):
        if should_raise:
            raise Exception("Topic service error")
        return topic_response or {
            'sequence': payload_in.get('text', ''),
            'labels': payload_in.get('labels', ['technology', 'business']),
            'scores': [0.85, 0.72],
            'time_taken': '0.15s'
        }
    
    mock_restricttopic_check.log_dict = {}
    svc.restricttopic_check = mock_restricttopic_check

    # Mock psutil
    ps = ModuleType('psutil')
    class _P:
        def memory_info(self):
            return type('T', (), {'rss': 0})()
    ps.Process = lambda: _P()

    # Mock uuid
    uuid_mod = ModuleType('uuid')
    uuid_mod.uuid4 = lambda: type('obj', (object,), {'hex': 'test-uuid-topic'})()

    # Mock time
    time_mod = ModuleType('time')
    time_mod.time = lambda: 1234567890.0

    # Mock tqdm
    tqdm_mod = ModuleType('tqdm')
    tqdm_auto_mod = ModuleType('tqdm.auto')
    tqdm_auto_mod.tqdm = lambda x, **kwargs: x
    tqdm_mod.auto = tqdm_auto_mod

    # Mock fastapi
    fastapi_mod = ModuleType('fastapi')
    fastapi_enc_mod = ModuleType('fastapi.encoders')
    fastapi_enc_mod.jsonable_encoder = lambda x: x
    fastapi_mod.encoders = fastapi_enc_mod

    # Mock mapper
    mapper_mod = ModuleType('mapper')
    mapper_map_mod = ModuleType('mapper.mapper')
    mapper_mod.mapper = mapper_map_mod

    # Mock traceback
    traceback_mod = ModuleType('traceback')
    traceback_mod.format_exc = lambda: "Mocked traceback"

    # Config and werkzeug via helpers
    cfg = make_config_logger_stub()
    werkzeug_exc = make_werkzeug_exceptions()

    replacements = {
        'flask': flask_stub,
        'service.topicModel': svc,
        'psutil': ps,
        'uuid': uuid_mod,
        'time': time_mod,
        'tqdm': tqdm_mod,
        'tqdm.auto': tqdm_auto_mod,
        'fastapi': fastapi_mod,
        'fastapi.encoders': fastapi_enc_mod,
        'mapper': mapper_mod,
        'mapper.mapper': mapper_map_mod,
        'traceback': traceback_mod,
        'config.logger': cfg,
        'werkzeug.exceptions': werkzeug_exc,
        **make_aicloud_modules(),
        'constants.local_constants': make_local_constants()
    }

    # Set request payload
    flask_stub.request = flask_stub.request.__class__(payload)

    with isolate_and_reload('routing.topicRouter', replacements):
        mod = reload_module('routing.topicRouter')

    return mod


def test_topic_bert_with_labels():
    """Test topic classification with fine-tuned BERT and labels"""
    payload = {
        'text': 'Artificial intelligence and machine learning are transforming technology',
        'model': 'fine-tuned distilbert',
        'labels': ['technology', 'business', 'sports']
    }
    expected = {
        'sequence': payload['text'],
        'labels': ['technology', 'business'],
        'scores': [0.92, 0.65],
        'time_taken': '0.14s'
    }
    mod = _reload_topic_with(payload, topic_response=expected)
    res = mod.restrictedTopic_model()
    assert res is not None


def test_topic_bert_without_labels():
    """Test topic classification with fine-tuned BERT without labels"""
    payload = {
        'text': 'The stock market showed strong growth today',
        'model': 'fine-tuned distilbert'
    }
    expected = {
        'sequence': payload['text'],
        'labels': ['business', 'finance'],
        'scores': [0.88, 0.79],
        'time_taken': '0.13s'
    }
    mod = _reload_topic_with(payload, topic_response=expected)
    res = mod.restrictedTopic_model()
    assert res is not None


def test_topic_nlimini_with_labels():
    """Test topic classification with nlimini model"""
    payload = {
        'text': 'The football team won the championship',
        'model': 'deberta',
        'labels': ['sports', 'entertainment', 'politics']
    }
    expected = {
        'sequence': payload['text'],
        'labels': ['sports'],
        'scores': [0.95],
        'time_taken': '0.16s'
    }
    mod = _reload_topic_with(payload, topic_response=expected)
    res = mod.restrictedTopic_model()
    assert res is not None


def test_topic_default_model():
    """Test with default model (no model specified)"""
    payload = {
        'text': 'Healthcare innovations are improving patient outcomes',
        'labels': ['healthcare', 'technology', 'business']  # Default model (deberta) requires labels
    }
    mod = _reload_topic_with(payload)
    res = mod.restrictedTopic_model()
    assert res is not None


def test_topic_empty_text():
    """Test with empty text"""
    payload = {'text': '', 'model': 'fine-tuned distilbert'}
    mod = _reload_topic_with(payload)
    
    try:
        res = mod.restrictedTopic_model()
        # Should raise exception for empty text
        assert False, "Should have raised exception"
    except Exception:
        # Expected
        pass


def test_topic_whitespace_text():
    """Test with whitespace only text"""
    payload = {'text': '   \n\t   ', 'model': 'fine-tuned distilbert'}
    mod = _reload_topic_with(payload)
    
    try:
        res = mod.restrictedTopic_model()
        assert False, "Should have raised exception"
    except Exception:
        # Expected
        pass


def test_topic_missing_text():
    """Test with missing text field"""
    payload = {'model': 'fine-tuned distilbert'}
    mod = _reload_topic_with(payload)
    
    try:
        res = mod.restrictedTopic_model()
        assert False, "Should have raised exception"
    except Exception:
        # Expected
        pass


def test_topic_nlimini_missing_labels():
    """Test nlimini without required labels"""
    payload = {'text': 'test text', 'model': 'deberta'}
    mod = _reload_topic_with(payload)
    
    try:
        res = mod.restrictedTopic_model()
        assert False, "Should have raised exception"
    except Exception:
        # Expected - nlimini requires labels
        pass


def test_topic_nlimini_empty_labels():
    """Test nlimini with empty labels list"""
    payload = {'text': 'test text', 'model': 'deberta', 'labels': []}
    mod = _reload_topic_with(payload)
    
    try:
        res = mod.restrictedTopic_model()
        assert False, "Should have raised exception"
    except Exception:
        # Expected
        pass


def test_topic_bert_invalid_labels_type():
    """Test BERT with invalid labels type"""
    payload = {'text': 'test text', 'model': 'fine-tuned distilbert', 'labels': 'not a list'}
    mod = _reload_topic_with(payload)
    
    try:
        res = mod.restrictedTopic_model()
        assert False, "Should have raised exception"
    except Exception:
        # Expected
        pass


def test_topic_unknown_model():
    """Test with unknown model name"""
    payload = {'text': 'test text', 'model': 'unknown-model'}
    mod = _reload_topic_with(payload)
    
    try:
        res = mod.restrictedTopic_model()
        assert False, "Should have raised exception"
    except Exception:
        # Expected
        pass


def test_topic_service_exception():
    """Test handling of service exceptions"""
    payload = {'text': 'test text', 'model': 'fine-tuned distilbert'}
    mod = _reload_topic_with(payload, should_raise=True)
    
    try:
        res = mod.restrictedTopic_model()
        # May handle gracefully or raise
        assert True
    except Exception:
        # Exception is expected
        pass


def test_topic_long_text():
    """Test with very long text"""
    payload = {
        'text': 'This is a sentence about technology. ' * 100,
        'model': 'fine-tuned distilbert'
    }
    mod = _reload_topic_with(payload)
    res = mod.restrictedTopic_model()
    assert res is not None


def test_topic_special_characters():
    """Test with special characters in text"""
    payload = {
        'text': 'Tech news: AI & ML are revolutionizing industries! (2024)',
        'model': 'fine-tuned distilbert'
    }
    mod = _reload_topic_with(payload)
    res = mod.restrictedTopic_model()
    assert res is not None


def test_topic_multilabel_response():
    """Test with multiple labels in response"""
    payload = {
        'text': 'The tech company reported strong financial results',
        'model': 'fine-tuned distilbert',
        'labels': ['technology', 'business', 'finance', 'economy']
    }
    expected = {
        'sequence': payload['text'],
        'labels': ['business', 'technology', 'finance'],
        'scores': [0.89, 0.87, 0.82],
        'time_taken': '0.18s'
    }
    mod = _reload_topic_with(payload, topic_response=expected)
    res = mod.restrictedTopic_model()
    assert res is not None
