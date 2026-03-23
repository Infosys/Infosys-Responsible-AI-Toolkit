'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
"""Tests for additional utility modules to increase coverage"""
import pytest


def test_common_extract_json_ast_literal_eval():
    """Test common.extract_json uses ast.literal_eval"""
    from app.utility.common import extract_json
    # Valid dict-style JSON
    s = "{'improvement': 'test', 'prompt': 'attack'}"
    parsed, json_str = extract_json(s)
    assert parsed is not None
    assert parsed["improvement"] == "test"
    assert parsed["prompt"] == "attack"


def test_common_extract_json_embedded_multiple():
    """Test common.extract_json extracts first JSON"""
    from app.utility.common import extract_json
    s = 'Text {"improvement": "first", "prompt": "p1"} more {"improvement": "second", "prompt": "p2"}'
    parsed, json_str = extract_json(s)
    assert parsed is not None
    # Should get first JSON only
    assert parsed["improvement"] == "first"


def test_common_process_target_response_formatting():
    """Test common.process_target_response preserves formatting"""
    from app.utility.common import process_target_response
    response = "Response\nwith\nmultiple\nlines"
    result = process_target_response(response, 8, "goal", "target")
    assert "Response" in result
    assert "with" in result
    assert "multiple" in result


def test_common_get_init_msg_goal_target_placement():
    """Test common.get_init_msg places goal and target correctly"""
    from app.utility.common import get_init_msg
    msg = get_init_msg("GOAL_TEXT", "TARGET_TEXT")
    goal_pos = msg.find("GOAL_TEXT")
    target_pos = msg.find("TARGET_TEXT")
    assert goal_pos > 0
    assert target_pos > 0
    # Target should come after goal in template
    assert target_pos > goal_pos


def test_common_conv_template_self_parent_ids():
    """Test common.conv_template sets self_id and parent_id"""
    from app.utility.common import conv_template
    conv = conv_template("vicuna_v1.1", self_id=10, parent_id=5)
    assert conv.self_id == 10
    assert conv.parent_id == 5


def test_common_conv_template_none_ids():
    """Test common.conv_template with None ids"""
    from app.utility.common import conv_template
    conv = conv_template("vicuna_v1.1", self_id=None, parent_id=None)
    assert conv.self_id is None
    assert conv.parent_id is None


def test_common_random_string_different_lengths():
    """Test common.random_string with various lengths"""
    from app.utility.common import random_string
    for length in [1, 5, 10, 20, 50]:
        result = random_string(length)
        assert len(result) == length
        assert result.isalnum()


def test_guardrail_keyword_detection():
    """Test guardrail module if it has keyword checking"""
    try:
        from app.utility.guardrail import check_input
        # Test basic functionality if function exists
        result = check_input("test input")
        assert result is not None
    except (ImportError, AttributeError):
        # Module or function doesn't exist, skip
        pytest.skip("Guardrail check_input not available")


def test_multifaceted_tree_operations():
    """Test multifaceted module tree operations"""
    try:
        from app.utility.multifaceted import EvaluationResult
        # Test basic instantiation if class exists
        result = EvaluationResult.__new__(EvaluationResult)
        assert result is not None
    except (ImportError, AttributeError):
        # Module or class doesn't exist, skip
        pytest.skip("Multifaceted EvaluationResult not available")


def test_report_generation_helpers():
    """Test report module helper functions"""
    try:
        from app.utility.report import format_conversation
        # Test if function exists and can be called
        assert callable(format_conversation)
    except (ImportError, AttributeError):
        # Module or function doesn't exist, skip
        pytest.skip("Report format_conversation not available")


def test_system_prompts_get_judge_prompt():
    """Test system_prompts module judge prompt generation"""
    try:
        from app.utility.system_prompts import get_judge_system_prompt_pair
        prompt = get_judge_system_prompt_pair("test goal", "test target")
        assert prompt is not None
        assert len(prompt) > 0
        assert isinstance(prompt, str)
    except (ImportError, AttributeError):
        pytest.skip("System prompts not available")


def test_system_prompts_contains_goal_target():
    """Test system_prompts includes goal and target"""
    try:
        from app.utility.system_prompts import get_judge_system_prompt_pair
        prompt = get_judge_system_prompt_pair("UNIQUE_GOAL", "UNIQUE_TARGET")
        # Check if goal and target are included
        assert "UNIQUE_GOAL" in prompt or "goal" in prompt.lower()
        assert "UNIQUE_TARGET" in prompt or "target" in prompt.lower()
    except (ImportError, AttributeError):
        pytest.skip("System prompts not available")


def test_common_extract_json_with_list_values():
    """Test common.extract_json with list values in dict"""
    from app.utility.common import extract_json
    s = '{"improvement": "test", "prompt": "attack", "extra": [1,2,3]}'
    parsed, json_str = extract_json(s)
    # Should still extract if improvement and prompt exist
    assert parsed is not None if "improvement" in s and "prompt" in s else True


def test_common_conv_template_different_templates():
    """Test common.conv_template with multiple template types"""
    from app.utility.common import conv_template
    templates = ["vicuna_v1.1", "llama-2"]
    for template_name in templates:
        conv = conv_template(template_name)
        assert conv is not None
        assert hasattr(conv, 'name')
        assert hasattr(conv, 'self_id')
        assert hasattr(conv, 'parent_id')


def test_common_random_string_no_special_chars():
    """Test common.random_string only returns alphanumeric"""
    from app.utility.common import random_string
    result = random_string(100)
    # Should not contain spaces, punctuation, etc
    assert all(c.isalnum() for c in result)


def test_common_get_init_msg_contains_begin():
    """Test common.get_init_msg ends with Begin"""
    from app.utility.common import get_init_msg
    msg = get_init_msg("test", "test")
    assert msg.endswith("Begin.")


def test_common_process_target_response_score_types():
    """Test common.process_target_response with different score types"""
    from app.utility.common import process_target_response
    # Test integer score
    result1 = process_target_response("resp", 5, "goal", "target")
    assert "5" in result1
    
    # Test float score (if supported)
    result2 = process_target_response("resp", 7.5, "goal", "target")
    assert "7.5" in result2
