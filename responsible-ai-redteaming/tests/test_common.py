'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from app.utility import common

class MinimalTemplate:
    def __init__(self, name, sep2='  \n'):
        self.name = name
        self.sep2 = sep2
    def __repr__(self):
        return f"MinimalTemplate(name={self.name!r}, sep2={self.sep2!r})"

def test_conv_template_llama_strips(monkeypatch):
    # Provide template with trailing spaces so strip path triggers
    monkeypatch.setattr(common, 'get_conversation_template', lambda n: MinimalTemplate('llama-2'))
    t = common.conv_template('llama-2')
    assert t.sep2 == ''  # stripped completely
    assert hasattr(t, 'self_id') and hasattr(t, 'parent_id')


def test_extract_json_missing_keys():
    # Provide JSON lacking required keys -> returns (None, None)
    bad = '{"improvement": "x"}'  # missing 'prompt'
    parsed, raw = common.extract_json(bad)
    assert parsed is None and raw is None


def test_extract_json_success():
    good = '{"improvement": "x", "prompt": "P"}'
    parsed, raw = common.extract_json(good)
    assert parsed['prompt'] == 'P'
    assert '"prompt"' in raw


def test_extract_json_no_closing_brace():
    """Test error path when no closing brace found."""
    malformed = '{"improvement": "x", "prompt": "P"'  # Missing closing brace
    parsed, raw = common.extract_json(malformed)
    # Should return None, None when end_pos is -1
    assert parsed is None
    assert raw is None


def test_extract_json_invalid_json():
    """Test with malformed JSON structure."""
    invalid = '{not valid json at all}'
    parsed, raw = common.extract_json(invalid)
    # Should fail JSON parsing
    assert parsed is None

def test_random_string_length():
    """Test random_string generates correct length"""
    import app.utility.common as common
    result = common.random_string(10)
    assert len(result) == 10
    # Test different length
    result2 = common.random_string(5)
    assert len(result2) == 5

def test_get_init_msg():
    """Test get_init_msg returns formatted message"""
    import app.utility.common as common
    goal = "test goal"
    target = "test target"
    msg = common.get_init_msg(goal, target)
    assert goal in msg
    assert target in msg

def test_process_target_response():
    """Test process_target_response formats response correctly"""
    import app.utility.common as common
    response = "sample response"
    score = 5
    goal = "goal"
    target = "target"
    result = common.process_target_response(response, score, goal, target)
    assert "LANGUAGE MODEL OUTPUT" in result
    assert str(score) in result
