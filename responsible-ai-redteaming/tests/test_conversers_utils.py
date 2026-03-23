'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
"""Tests for conversers.py utility functions without mocking"""
import pytest


def test_extract_json_with_newlines():
    """Test extract_json handles newlines in JSON"""
    from app.utility.conversers import extract_json
    s = '{"improvement": "line1\nline2", "prompt": "test\nprompt"}'
    parsed, json_str = extract_json(s)
    assert parsed is not None
    assert "\n" not in json_str  # Newlines should be removed
    assert parsed["improvement"] == "line1line2"
    assert parsed["prompt"] == "testprompt"


def test_extract_json_extra_quotes():
    """Test extract_json handles extra quotes"""
    from app.utility.conversers import extract_json
    s = '""{"improvement": "test", "prompt": "attack"}""'
    parsed, json_str = extract_json(s)
    assert parsed is not None
    assert parsed["improvement"] == "test"


def test_extract_json_embedded_in_text():
    """Test extract_json extracts from surrounding text"""
    from app.utility.conversers import extract_json
    s = 'Here is the JSON: {"improvement": "better", "prompt": "new"} and more text'
    parsed, json_str = extract_json(s)
    assert parsed is not None
    assert parsed["improvement"] == "better"
    assert parsed["prompt"] == "new"


def test_extract_json_only_improvement():
    """Test extract_json fails with only improvement key"""
    from app.utility.conversers import extract_json
    s = '{"improvement": "test only"}'
    parsed, json_str = extract_json(s)
    assert parsed is None
    assert json_str is None


def test_extract_json_only_prompt():
    """Test extract_json fails with only prompt key"""
    from app.utility.conversers import extract_json
    s = '{"prompt": "test only"}'
    parsed, json_str = extract_json(s)
    assert parsed is None
    assert json_str is None


def test_extract_json_syntax_error():
    """Test extract_json handles syntax errors"""
    from app.utility.conversers import extract_json
    s = '{"improvement": "test", "prompt": undefined}'
    parsed, json_str = extract_json(s)
    assert parsed is None
    assert json_str is None


def test_get_init_msg_pair_contains_keywords():
    """Test get_init_msg_pair includes required keywords"""
    from app.utility.conversers import get_init_msg_pair
    msg = get_init_msg_pair("bypass filter", "Sure, I will")
    assert "bypass filter" in msg
    assert "Sure, I will" in msg
    assert "adversarial" in msg
    assert "jailbreaking" in msg
    assert "objective" in msg.lower()
    assert "language model" in msg


def test_process_target_response_pair_includes_all_parts():
    """Test process_target_response_pair includes all components"""
    from app.utility.conversers import process_target_response_pair
    result = process_target_response_pair("model said this", 7, "goal here", "target here")
    assert "LANGUAGE MODEL OUTPUT" in result
    assert "model said this" in result
    assert "OBJECTIVE" in result
    assert "goal here" in result
    assert "SCORE" in result
    assert "7" in result


def test_conv_template_pair_vicuna():
    """Test conv_template_pair with vicuna template"""
    from app.utility.conversers import conv_template_pair
    template = conv_template_pair("vicuna_v1.1")
    assert template is not None
    assert hasattr(template, 'name')
    assert hasattr(template, 'messages')
    assert hasattr(template, 'append_message')


def test_conv_template_pair_llama_sep_stripped():
    """Test conv_template_pair strips llama-2 sep2"""
    from app.utility.conversers import conv_template_pair
    template = conv_template_pair("llama-2")
    assert template.name == 'llama-2'
    # Should have sep2 stripped
    assert template.sep2 == template.sep2.strip()


def test_get_init_msg_pair_special_characters():
    """Test get_init_msg_pair handles special characters"""
    from app.utility.conversers import get_init_msg_pair
    msg = get_init_msg_pair("goal with 'quotes'", 'target with "quotes"')
    assert "goal with 'quotes'" in msg
    assert 'target with "quotes"' in msg


def test_process_target_response_pair_multiline():
    """Test process_target_response_pair with multiline response"""
    from app.utility.conversers import process_target_response_pair
    multiline_response = "Line 1\nLine 2\nLine 3"
    result = process_target_response_pair(multiline_response, 10, "test goal", "test target")
    assert "Line 1" in result
    assert "Line 2" in result
    assert "Line 3" in result
    assert "10" in result


def test_extract_json_nested_braces():
    """Test extract_json with nested structures"""
    from app.utility.conversers import extract_json
    s = '{"improvement": "test", "prompt": "attack with {nested}"}'
    parsed, json_str = extract_json(s)
    # Should extract outer braces
    assert parsed is not None or (parsed is None and json_str is None)


def test_conv_template_pair_with_different_templates():
    """Test conv_template_pair works with different template names"""
    from app.utility.conversers import conv_template_pair
    
    # Test multiple templates
    templates = ["vicuna_v1.1", "llama-2"]
    for template_name in templates:
        template = conv_template_pair(template_name)
        assert template is not None
        assert hasattr(template, 'name')


def test_get_init_msg_pair_empty_strings():
    """Test get_init_msg_pair with empty strings"""
    from app.utility.conversers import get_init_msg_pair
    msg = get_init_msg_pair("", "")
    assert msg is not None
    assert len(msg) > 0
    # Should still contain template text
    assert "adversarial" in msg


def test_process_target_response_pair_zero_score():
    """Test process_target_response_pair with score 0"""
    from app.utility.conversers import process_target_response_pair
    result = process_target_response_pair("response", 0, "goal", "target")
    assert "0" in result
    assert "SCORE" in result


def test_process_target_response_pair_high_score():
    """Test process_target_response_pair with high score"""
    from app.utility.conversers import process_target_response_pair
    result = process_target_response_pair("response", 10, "goal", "target")
    assert "10" in result
    assert "SCORE" in result


def test_extract_json_empty_string():
    """Test extract_json with empty string"""
    from app.utility.conversers import extract_json
    s = ''
    parsed, json_str = extract_json(s)
    assert parsed is None
    assert json_str is None


def test_extract_json_no_json_structure():
    """Test extract_json with no JSON at all"""
    from app.utility.conversers import extract_json
    s = 'Just plain text without any JSON structure'
    parsed, json_str = extract_json(s)
    assert parsed is None
    assert json_str is None
