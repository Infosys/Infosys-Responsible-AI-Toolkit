'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import pytest


def test_get_judge_system_prompt_pair():
    """Test get_judge_system_prompt_pair function"""
    from app.utility.system_prompts import get_judge_system_prompt_pair
    prompt = get_judge_system_prompt_pair("test goal", "test target")
    assert "{goal}" in prompt or "test goal" in prompt
    assert isinstance(prompt, str)
    assert len(prompt) > 100

def test_get_attacker_system_prompt_pair():
    """Test get_attacker_system_prompt_pair function"""
    from app.utility.system_prompts import get_attacker_system_prompt_pair
    prompt = get_attacker_system_prompt_pair("test goal", "test target")
    assert "test goal" in prompt
    assert "test target" in prompt
    assert isinstance(prompt, str)
    assert len(prompt) > 0

def test_get_evaluator_system_prompt_for_judge():
    """Test get_evaluator_system_prompt_for_judge function"""
    from app.utility.system_prompts import get_evaluator_system_prompt_for_judge
    prompt = get_evaluator_system_prompt_for_judge("test goal", "test target")
    assert isinstance(prompt, str)
    assert len(prompt) > 0

def test_get_evaluator_system_prompt_for_on_topic():
    """Test get_evaluator_system_prompt_for_on_topic function"""
    from app.utility.system_prompts import get_evaluator_system_prompt_for_on_topic
    prompt = get_evaluator_system_prompt_for_on_topic("test goal")
    assert "test goal" in prompt
    assert isinstance(prompt, str)

def test_moderation_handler_initialization():
    """Test ModerationHandler class initialization"""
    from app.utility.guardrail import ModerationHandler
    handler = ModerationHandler()
    assert hasattr(handler, 'url')
    assert hasattr(handler, 'timeout')
    assert handler.timeout == 30

def test_moderation_handler_no_url():
    """Test ModerationHandler when URL not configured"""
    from app.utility.guardrail import ModerationHandler
    handler = ModerationHandler()
    result = handler.check_moderation("test prompt")
    assert isinstance(result, dict)
    assert 'moderationResults' in result

def test_random_string_length():
    """Test random_string generates correct length"""
    from app.utility.common import random_string
    result = random_string(10)
    assert len(result) == 10
    assert result.isalnum()

def test_random_string_different():
    """Test random_string generates different strings"""
    from app.utility.common import random_string
    str1 = random_string(15)
    str2 = random_string(15)
    assert str1 != str2

def test_conv_template_vicuna():
    """Test conv_template with vicuna"""
    from app.utility.common import conv_template
    template = conv_template("vicuna_v1.1")
    assert template is not None
    assert hasattr(template, 'messages')
    assert hasattr(template, 'roles')

def test_conv_template_llama():
    """Test conv_template with llama"""
    from app.utility.common import conv_template
    template = conv_template("llama-2")
    assert template is not None
    assert hasattr(template, 'messages')

def test_get_init_msg_common():
    """Test get_init_msg from common module"""
    from app.utility.common import get_init_msg
    msg = get_init_msg("test goal", "test target")
    assert "test goal" in msg
    assert "test target" in msg

def test_process_target_response_common():
    """Test process_target_response from common module"""
    from app.utility.common import process_target_response
    result = process_target_response("response", 7, "goal", "target")
    assert "response" in result
    assert "7" in result

def test_extract_json_common():
    """Test extract_json from common module"""
    from app.utility.common import extract_json
    test_str = '{"improvement": "test", "prompt": "test prompt"}'
    parsed, json_str = extract_json(test_str)
    assert parsed is not None
    assert "improvement" in parsed
    assert "prompt" in parsed

def test_extract_json_embedded_common():
    """Test extract_json with embedded JSON"""
    from app.utility.common import extract_json
    test_str = 'Some text {"improvement": "improve", "prompt": "adv prompt"} more text'
    parsed, json_str = extract_json(test_str)
    assert parsed is not None
    assert parsed["improvement"] == "improve"

def test_extract_json_no_json_common():
    """Test extract_json with no JSON"""
    from app.utility.common import extract_json
    test_str = 'No JSON here'
    parsed, json_str = extract_json(test_str)
    assert parsed is None
    assert json_str is None
