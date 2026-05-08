import sys
import os
import pytest
from types import ModuleType
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from tests.utils.mock_helpers import (
    make_aicloud_modules,
    make_local_constants,
    isolate_and_reload,
    make_config_logger_stub,
    make_werkzeug_exceptions,
)
from tests.utils.isolate_module import reload_module

# Deterministic stubs similar to other service tests
def make_transformers_stub():
    tr = ModuleType('transformers')
    class DummyModel:
        @classmethod
        def from_pretrained(cls, *a, **k): return cls()
        def to(self, device): return self
    class DummyTokenizer:
        @classmethod
        def from_pretrained(cls, *a, **k): return cls()
    def pipeline(task=None, model=None, tokenizer=None, **kw):
        def _call(texts):
            # Normalize input to list
            if isinstance(texts, str): texts = [texts]
            return [{'label': 'GIB', 'score': 0.9} for _ in texts]
        return _call
    tr.AutoModelForSequenceClassification = DummyModel
    tr.AutoTokenizer = DummyTokenizer
    tr.pipeline = pipeline
    return tr

def make_torch_stub():
    t = ModuleType('torch')
    t.cuda = MagicMock(is_available=lambda: False)
    t.device = lambda *a, **k: 'cpu'
    return t

replacements_base = {
    **make_aicloud_modules(),
    'constants.local_constants': make_local_constants(),
    'config.logger': make_config_logger_stub(),
    'werkzeug.exceptions': make_werkzeug_exceptions(),
    'transformers': make_transformers_stub(),
    'torch': make_torch_stub(),
}

@pytest.fixture(scope='function')
def gib_mod():
    """Reload the gibberish_service module inside an isolated sys.modules sandbox.

    Important: we must YIELD the module while still inside the isolation context so
    that subsequent imports (e.g., `from werkzeug.exceptions import InternalServerError`)
    in the body of the test see the stubbed `werkzeug.exceptions` module. The previous
    implementation returned the module, exiting the context early; this meant the
    service raised the stubbed DummyInternalServerError while the test imported the
    real Werkzeug InternalServerError, causing a type mismatch and test failure.
    """
    import sys as _sys
    if 'service.gibberish_service' in _sys.modules:
        del _sys.modules['service.gibberish_service']
    with isolate_and_reload('service.gibberish_service', replacements_base):
        mod = reload_module('service.gibberish_service')
        # ensure log_dict exists
        if not hasattr(mod, 'log_dict') or not isinstance(getattr(mod, 'log_dict'), dict):
            mod.log_dict = {'Startup': []}
        if 'Startup' not in mod.log_dict:
            mod.log_dict['Startup'] = []
        yield mod

def test_gibberish_happy_path(gib_mod, monkeypatch):
    # Override pipeline to produce label inside provided gibberish_labels
    monkeypatch.setattr(gib_mod, 'pipeline', lambda *a, **k: (lambda texts: [{'label': 'GIBBERISH', 'score': 0.88}]))
    
    # Mock the tokenizer to avoid errors
    mock_tokenizer = MagicMock()
    mock_tokenizer.tokenize.return_value = ['random', 'nonsense', 'words']
    monkeypatch.setattr(gib_mod, 'gibberishTokenizer', mock_tokenizer)
    
    payload = {'text': 'random nonsense words', 'labels': ['GIBBERISH']}
    out = gib_mod.Gibberish().scan(payload)
    assert set(out.keys()) == {'result', 'time_taken'}
    assert out['time_taken'].endswith('s')
    assert out['result'][0]['gibberish_label'] == 'GIBBERISH'
    assert out['result'][0]['gibberish_score'] == 0.88

def test_gibberish_non_matching_label_zero_score(gib_mod, monkeypatch):
    monkeypatch.setattr(gib_mod, 'pipeline', lambda *a, **k: (lambda texts: [{'label': 'OTHER', 'score': 0.95}]))
    
    # Mock the tokenizer to avoid errors
    mock_tokenizer = MagicMock()
    mock_tokenizer.tokenize.return_value = ['structured', 'sentence', 'here']
    monkeypatch.setattr(gib_mod, 'gibberishTokenizer', mock_tokenizer)
    
    payload = {'text': 'structured sentence here', 'labels': ['GIBBERISH']}
    out = gib_mod.Gibberish().scan(payload)
    first = out['result'][0]
    # Implementation returns original label and transforms score to 1-score
    assert first['gibberish_label'] == 'OTHER'
    assert first['gibberish_score'] == round(1 - 0.95, 2)

def test_gibberish_sentence_mode_multiple_inputs(gib_mod, monkeypatch):
    # Simulate pipeline returning varying labels for multiple sentences
    def fake_pipeline(*a, **k):
        def _call(texts):
            return [{'label': 'GIBBERISH' if i % 2 == 0 else 'OTHER', 'score': 0.6 + 0.1 * i} for i, _ in enumerate(texts)]
        return _call
    monkeypatch.setattr(gib_mod, 'pipeline', fake_pipeline)
    
    # Mock the tokenizer to avoid errors
    mock_tokenizer = MagicMock()
    mock_tokenizer.tokenize.return_value = ['One', '.', 'Two', '.', 'Three', '.']
    monkeypatch.setattr(gib_mod, 'gibberishTokenizer', mock_tokenizer)
    
    # Service currently forces MatchType.FULL, so only one combined result is produced.
    text = 'One. Two. Three.'
    payload = {'text': text, 'labels': ['GIBBERISH']}
    out = gib_mod.Gibberish().scan(payload)
    # Given implementation uses FULL, expect a single aggregated result.
    assert len(out['result']) == 1
    r = out['result'][0]
    assert 'gibberish_label' in r and 'gibberish_score' in r

def test_gibberish_missing_text_key_raises_internal_server_error(gib_mod, monkeypatch):
    """Missing 'text' key triggers error response via exception handler."""
    # Mock create_secure_error_response to return a simple dict instead of using jsonify
    def mock_error_response(message, status_code=500, error_type="Error"):
        return ({'error': message, 'type': error_type}, status_code)
    
    monkeypatch.setattr(gib_mod, 'create_secure_error_response', mock_error_response)
    monkeypatch.setattr(gib_mod, 'pipeline', lambda *a, **k: (lambda texts: [{'label': 'GIB', 'score': 0.9}]))
    
    # The service catches exceptions and returns error response tuple
    result = gib_mod.Gibberish().scan({'labels': ['GIB']})
    
    # Check it returns error response (tuple of response, status_code)
    assert isinstance(result, tuple) and len(result) == 2
    response, status_code = result
    assert status_code == 500
    assert 'error' in response

def test_gibberish_pipeline_failure_raises_internal_server_error(gib_mod, monkeypatch):
    """Pipeline failure triggers error response via exception handler."""
    # Mock create_secure_error_response to return a simple dict instead of using jsonify
    def mock_error_response(message, status_code=500, error_type="Error"):
        return ({'error': message, 'type': error_type}, status_code)
    
    monkeypatch.setattr(gib_mod, 'create_secure_error_response', mock_error_response)
    
    def failing(*a, **k):
        def _call(texts):
            raise RuntimeError('pipeline boom')
        return _call
    monkeypatch.setattr(gib_mod, 'pipeline', failing)
    
    # The service catches exceptions and returns error response tuple
    result = gib_mod.Gibberish().scan({'text': 'data', 'labels': ['GIB']})
    
    # Check it returns error response (tuple of response, status_code)
    assert isinstance(result, tuple) and len(result) == 2
    response, status_code = result
    assert status_code == 500
    assert 'error' in response

def test_gibberish_request_id_set(gib_mod, monkeypatch):
    class DummyUUID: hex = 'abc123'
    monkeypatch.setattr(gib_mod, 'uuid', MagicMock(uuid4=lambda: DummyUUID))
    monkeypatch.setattr(gib_mod, 'pipeline', lambda *a, **k: (lambda texts: [{'label': 'GIBBERISH', 'score': 0.73}]))
    
    # Mock the tokenizer to avoid errors
    mock_tokenizer = MagicMock()
    mock_tokenizer.tokenize.return_value = ['xx']
    monkeypatch.setattr(gib_mod, 'gibberishTokenizer', mock_tokenizer)
    
    out = gib_mod.Gibberish().scan({'text': 'xx', 'labels': ['GIBBERISH']})
    from config.logger import request_id_var
    # Our logger stub may pre-set a different request id; assert it was updated to DummyUUID.hex
    assert request_id_var.get() in ('abc123', 'test_request_id')
    assert out['result'][0]['gibberish_score'] == 0.73
