"""Tests for `service.invisibletext_service.InvisibleText.scan`.

Comprehensive business logic coverage for invisible character detection including:
  * ASCII-only text optimization (fast path without Unicode scanning)
  * Unicode character category detection (Cf, Cc, Co, Cn)
  * Multiple banned categories handling
  * Empty/edge case inputs
  * Exception handling with InternalServerError
  * Request ID context variable management
  * Time measurement accuracy
  * Character collection and filtering logic
"""

import sys
import os
import pytest
from unittest.mock import MagicMock
from types import ModuleType

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from tests.utils.mock_helpers import (
    make_aicloud_modules,
    make_local_constants,
    isolate_and_reload,
    make_config_logger_stub,
    make_werkzeug_exceptions,
)
from tests.utils.isolate_module import reload_module


def make_invisibletext_stubs():
    """Create deterministic stubs for unicodedata and other dependencies."""
    # Unicodedata stub with predictable category mapping
    ud = ModuleType('unicodedata')
    def category(char):
        # Map specific test characters to categories for predictable testing
        char_categories = {
            '\u200b': 'Cf',  # ZERO WIDTH SPACE (Format)
            '\u0000': 'Cc',  # NULL (Control)
            '\ue000': 'Co',  # Private Use Area
            '\ufdd0': 'Cn',  # Unassigned (noncharacter)
            'a': 'Ll',       # Lowercase Letter (normal)
            'A': 'Lu',       # Uppercase Letter (normal)
            ' ': 'Zs',       # Space Separator (normal)
            '1': 'Nd',       # Decimal Number (normal)
            '!': 'Po',       # Other Punctuation (normal)
        }
        return char_categories.get(char, 'Ll')  # Default to lowercase letter
    ud.category = category

    return {
        'unicodedata': ud,
    }


@pytest.fixture(scope='function')
def invisibletext_mod():
    """Reload invisible text service in isolated context with deterministic stubs."""
    replacements = {
        **make_aicloud_modules(),
        'constants.local_constants': make_local_constants(),
        'config.logger': make_config_logger_stub(),
        'werkzeug.exceptions': make_werkzeug_exceptions(),
        **make_invisibletext_stubs(),
    }
    import sys as _sys
    _sys.modules.pop('service.invisibletext_service', None)
    with isolate_and_reload('service.invisibletext_service', replacements):
        mod = reload_module('service.invisibletext_service')
        # Ensure log_dict exists for error handling paths
        if not hasattr(mod, 'log_dict') or not isinstance(getattr(mod, 'log_dict'), dict):
            mod.log_dict = {}
        yield mod


# --- Business Logic Tests ---

def test_ascii_only_text_fast_path(invisibletext_mod):
    """ASCII-only text takes fast path and returns empty result."""
    instance = invisibletext_mod.InvisibleText()
    result = instance.scan('Plain ASCII text 123!', banned_categories=['Cf', 'Cc'])
    
    assert isinstance(result, dict)
    assert 'result' in result and 'time_taken' in result
    assert result['result'] == []  # No Unicode chars, so empty result
    assert result['time_taken'].endswith('s')


def test_unicode_text_format_character_detection(invisibletext_mod):
    """Unicode text with Format characters (Cf) detected and collected."""
    instance = invisibletext_mod.InvisibleText()
    text_with_cf = 'Hello\u200bWorld'  # Contains ZERO WIDTH SPACE (Cf)
    result = instance.scan(text_with_cf, banned_categories=['Cf'])
    
    assert isinstance(result, dict)
    assert 'result' in result and 'time_taken' in result
    assert len(result['result']) == 1
    assert '\u200b' in result['result']  # Should find the Cf character
    assert result['time_taken'].endswith('s')


def test_unicode_text_control_character_detection(invisibletext_mod):
    """Unicode text with Control characters (Cc) detected."""
    instance = invisibletext_mod.InvisibleText()
    # Use a Unicode control char (ord > 127) to ensure Unicode path is taken
    text_with_cc = 'Tëxt\u0000End'  # 'ë' forces Unicode path, NULL is Cc
    result = instance.scan(text_with_cc, banned_categories=['Cc'])
    
    assert isinstance(result, dict)
    assert len(result['result']) == 1
    assert '\u0000' in result['result']  # Should find the Cc character


def test_multiple_banned_categories(invisibletext_mod):
    """Text with multiple Unicode categories, multiple banned categories specified."""
    instance = invisibletext_mod.InvisibleText()
    # Mix of Cf, Cc, Co characters with normal text
    text_mixed = 'Hello\u200b\u0000\ue000World'
    result = instance.scan(text_mixed, banned_categories=['Cf', 'Cc', 'Co'])
    
    assert isinstance(result, dict)
    assert len(result['result']) == 3  # Should find all three invisible chars
    expected_chars = ['\u200b', '\u0000', '\ue000']
    for char in expected_chars:
        assert char in result['result']


def test_unicode_text_no_banned_categories_found(invisibletext_mod):
    """Unicode text with no characters matching banned categories."""
    instance = invisibletext_mod.InvisibleText()
    # Contains Unicode but not in banned categories (all normal letters/punctuation)
    unicode_text = 'Héllo Wørld! 123'
    result = instance.scan(unicode_text, banned_categories=['Cf', 'Cc'])
    
    assert isinstance(result, dict)
    assert result['result'] == []  # No chars match banned categories


def test_unicode_text_partial_category_match(invisibletext_mod):
    """Unicode text where only some characters match banned categories."""
    instance = invisibletext_mod.InvisibleText()
    # Mix: normal chars + one banned Cf char
    text_partial = 'Normal\u200bText'
    result = instance.scan(text_partial, banned_categories=['Cf'])
    
    assert isinstance(result, dict)
    assert len(result['result']) == 1
    assert '\u200b' in result['result']
    # Verify normal chars are not included
    for char in 'NormalText':
        assert char not in result['result']


def test_empty_string_input(invisibletext_mod):
    """Empty string input should return empty result via ASCII fast path."""
    instance = invisibletext_mod.InvisibleText()
    result = instance.scan('', banned_categories=['Cf', 'Cc'])
    
    assert isinstance(result, dict)
    assert result['result'] == []
    assert result['time_taken'].endswith('s')


def test_empty_banned_categories_list(invisibletext_mod):
    """Empty banned categories should return no matches even with invisible chars."""
    instance = invisibletext_mod.InvisibleText()
    text_with_invisible = 'Text\u200b\u0000'
    result = instance.scan(text_with_invisible, banned_categories=[])
    
    assert isinstance(result, dict)
    assert result['result'] == []  # No categories banned, so no matches


def test_unicodedata_exception_raises_internal_server_error(invisibletext_mod, monkeypatch):
    """Exception in unicodedata.category triggers error response."""
    # Mock create_secure_error_response to return a simple dict instead of using jsonify
    def mock_error_response(message, status_code=500, error_type="Error"):
        return ({'error': message, 'type': error_type}, status_code)
    
    monkeypatch.setattr(invisibletext_mod, 'create_secure_error_response', mock_error_response)
    
    def failing_category(char):
        if char == 'ë':  # Fail on Unicode char to trigger exception during Unicode path
            raise ValueError('Unicode lookup failed')
        return 'Ll'
    
    monkeypatch.setattr(invisibletext_mod.unicodedata, 'category', failing_category)
    
    instance = invisibletext_mod.InvisibleText()
    # The service catches exceptions and returns error response tuple
    result = instance.scan('Tëst', banned_categories=['Cf'])
    
    # Check it returns error response (tuple of response, status_code)
    assert isinstance(result, tuple) and len(result) == 2
    response, status_code = result
    assert status_code == 500
    assert 'error' in response


def test_request_id_context_variable_set(invisibletext_mod):
    """Verify request_id_var is set correctly during execution."""
    instance = invisibletext_mod.InvisibleText()
    
    # Use a monkeypatch to capture the request_id during execution
    captured_request_id = None
    original_category = invisibletext_mod.unicodedata.category
    
    def capturing_category(char):
        nonlocal captured_request_id
        if captured_request_id is None:  # Capture on first call
            from config.logger import request_id_var
            captured_request_id = request_id_var.get()
        return original_category(char)
    
    invisibletext_mod.unicodedata.category = capturing_category
    
    result = instance.scan('Tëst', banned_categories=['Cf'])
    
    # Request ID should be a UUID hex string (32 chars)
    assert captured_request_id is not None
    assert isinstance(captured_request_id, str)
    assert len(captured_request_id) >= 8  # UUID hex should be reasonably long


def test_time_measurement_accuracy(invisibletext_mod):
    """Verify time_taken is measured and formatted correctly."""
    import time
    
    # Patch unicodedata.category to simulate processing time
    original_category = invisibletext_mod.unicodedata.category
    def slow_category(char):
        time.sleep(0.05)  # Small delay to ensure measurable time
        return original_category(char)
    
    invisibletext_mod.unicodedata.category = slow_category
    
    instance = invisibletext_mod.InvisibleText()
    result = instance.scan('Tëst', banned_categories=['Cf'])
    
    assert 'time_taken' in result
    time_str = result['time_taken']
    assert time_str.endswith('s')
    
    # Extract numeric part and verify it's reasonable
    time_val = float(time_str[:-1])
    assert time_val >= 0.01  # Should capture some processing time


def test_character_order_preservation(invisibletext_mod):
    """Verify that detected characters maintain their order from the input."""
    instance = invisibletext_mod.InvisibleText()
    # Multiple invisible chars in specific order
    ordered_text = 'A\u200bB\u0000C\ue000D'
    result = instance.scan(ordered_text, banned_categories=['Cf', 'Cc', 'Co'])
    
    assert isinstance(result, dict)
    assert len(result['result']) == 3
    # Should maintain input order: Cf, then Cc, then Co
    assert result['result'][0] == '\u200b'  # First invisible char
    assert result['result'][1] == '\u0000'  # Second invisible char  
    assert result['result'][2] == '\ue000'  # Third invisible char


def test_unicode_detection_logic(invisibletext_mod):
    """Verify contains_unicode logic correctly identifies Unicode vs ASCII."""
    instance = invisibletext_mod.InvisibleText()
    
    # Test ASCII - should take fast path
    ascii_result = instance.scan('ASCII123', banned_categories=['Cf'])
    assert ascii_result['result'] == []
    
    # Test Unicode - should scan character by character
    unicode_result = instance.scan('Tëst', banned_categories=['Cf'])  # 'ë' is > 127
    assert isinstance(unicode_result['result'], list)  # Should process Unicode path
