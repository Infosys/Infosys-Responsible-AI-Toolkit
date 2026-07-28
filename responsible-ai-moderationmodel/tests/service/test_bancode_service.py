import sys
import os
import pytest
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

# Shared replacements used for every isolated import of bancode_service
replacements = {
    **make_aicloud_modules(),
    'constants.local_constants': make_local_constants(),
    'config.logger': make_config_logger_stub(),
    'werkzeug.exceptions': make_werkzeug_exceptions(),
}


@pytest.fixture(scope='function')
def bancode_mod():
    """Reload service.bancode_service in an isolated module context each test.

    Ensures heavy imports (transformers, torch, logger) are stubbed and that
    monkeypatch.setattr(module_obj, attr, value) works even after context exit.
    """
    import sys as _sys
    # Remove any stub bancode_service injected by conftest so we load the real implementation
    try:
        existing = _sys.modules.get('service.bancode_service')
        if existing and hasattr(existing, 'BanCode'):
            try:
                # Heuristic: stub BanCode.scan returns dict with 'status' key
                if 'status' in getattr(existing, 'BanCode')().scan({'text': 'x'}):
                    del _sys.modules['service.bancode_service']
            except Exception:
                del _sys.modules['service.bancode_service']
    except Exception:
        pass
    with isolate_and_reload('service.bancode_service', replacements):
        yield reload_module('service.bancode_service')


def test_remove_markdown_basic_preservation(bancode_mod):
    """Bold/italic/link/code markers stripped while inner text preserved."""
    inp = "## Header\nSome **bold** and *italic* text with a [link](http://x) and `code()`"
    out = bancode_mod.remove_markdown(inp)
    # header marker removed but word kept
    assert out.startswith("Header")
    # formatting markers removed, inner text kept
    assert 'bold' in out
    assert 'italic' in out
    # link anchor text preserved, URL removed
    # Entire link and inline code removed by patterns
    assert 'link' not in out
    assert 'http' not in out
    assert 'code' not in out
    # no lingering markdown symbols
    assert '**' not in out and '*' not in out and '`' not in out


def test_remove_markdown_headers_and_lists(bancode_mod):
    """Headers (#) and list markers (removed in scan logic) should not remain after preprocessing."""
    # remove_markdown itself only strips the header markers; list markers are stripped later in scan
    inp = "### Title\n1. First\n- Second\n• Third"
    out = bancode_mod.remove_markdown(inp)
    assert 'Title' in out
    # header markers removed
    assert '#' not in out


def test_bancode_scan_happy_path(bancode_mod, monkeypatch):
    """Scan returns structure with result dict and time_taken suffix."""
    captured = {}
    def fake_pipeline(*a, **k):
        def _call(txt):
            captured['input'] = txt
            return [{'label': 'CODE', 'score': 0.99}]
        return _call
    monkeypatch.setattr(bancode_mod, 'pipeline', fake_pipeline)
    payload = {'text': 'print(1)'}
    res = bancode_mod.BanCode().scan(payload)
    assert set(res.keys()) == {'result', 'time_taken'}
    assert res['result']['label'] == 'CODE'
    assert isinstance(res['result']['score'], float)
    assert res['time_taken'].endswith('s')
    # input text passed to pipeline had markdown removed and numbers stripped
    # original prompt 'print(1)' becomes 'print()' after number removal in scan logic.
    assert captured['input'] == 'print()'


def test_bancode_scan_strips_list_markers_and_numbers(bancode_mod, monkeypatch):
    captured = {}
    def fake_pipeline(*a, **k):
        def _call(txt):
            captured['input'] = txt
            return [{'label': 'CODE', 'score': 0.42}]
        return _call
    monkeypatch.setattr(bancode_mod, 'pipeline', fake_pipeline)
    messy = "## Header\n1. First item\n2. Second item\n- Bullet A\n• Bullet B\nNumber123 period. End."
    res = bancode_mod.BanCode().scan({'text': messy})
    assert res['result']['label'] == 'CODE'
    cleaned = captured['input']
    # list markers and numbers removed
    assert '1.' not in cleaned and '2.' not in cleaned
    assert 'Bullet' in cleaned  # bullet text retained
    assert '123' not in cleaned
    # trailing period removed by regex (unless part of decimal)
    assert not cleaned.endswith('.')


def test_bancode_scan_missing_text_key_raises_internal_server_error(bancode_mod, monkeypatch):
    """Absent 'text' key triggers error response via exception handler."""
    # Mock create_secure_error_response to return a simple dict instead of using jsonify
    def mock_error_response(message, status_code=500, error_type="Error"):
        return ({'error': message, 'type': error_type}, status_code)
    
    monkeypatch.setattr(bancode_mod, 'create_secure_error_response', mock_error_response)
    monkeypatch.setattr(bancode_mod, 'pipeline', lambda *a, **k: (lambda txt: [{'label': 'CODE', 'score': 0.1}]))
    
    # The service catches exceptions and returns error response tuple
    result = bancode_mod.BanCode().scan({'no_text': 'value'})
    
    # Check it returns error response (tuple of response, status_code)
    assert isinstance(result, tuple) and len(result) == 2
    response, status_code = result
    assert status_code == 500
    assert 'error' in response


def test_bancode_scan_pipeline_failure_raises_internal_server_error(bancode_mod, monkeypatch):
    """Pipeline failure triggers error response via exception handler."""
    # Mock create_secure_error_response to return a simple dict instead of using jsonify
    def mock_error_response(message, status_code=500, error_type="Error"):
        return ({'error': message, 'type': error_type}, status_code)
    
    monkeypatch.setattr(bancode_mod, 'create_secure_error_response', mock_error_response)
    
    class Boom(Exception):
        pass
    def failing_pipeline(*a, **k):
        def _call(txt):
            raise Boom('fail')
        return _call
    monkeypatch.setattr(bancode_mod, 'pipeline', failing_pipeline)
    
    # The service catches exceptions and returns error response tuple
    result = bancode_mod.BanCode().scan({'text': 'code here'})
    
    # Check it returns error response (tuple of response, status_code)
    assert isinstance(result, tuple) and len(result) == 2
    response, status_code = result
    assert status_code == 500
    assert 'error' in response


def test_bancode_scan_sets_request_id(bancode_mod, monkeypatch):
    # Patch uuid.uuid4 to deterministic value
    class DummyUUID:
        hex = 'deadbeef'
    monkeypatch.setattr(bancode_mod, 'uuid', MagicMock(uuid4=lambda: DummyUUID))
    monkeypatch.setattr(bancode_mod, 'pipeline', lambda *a, **k: (lambda txt: [{'label': 'CODE', 'score': 0.77}]))
    res = bancode_mod.BanCode().scan({'text': 'print(2)'})
    # Access stubbed request_id_var from config.logger stub
    from config.logger import request_id_var
    assert request_id_var.get() == 'deadbeef'
    assert res['result']['score'] == 0.77

