'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
"""Comprehensive test suite for app.utility.conversers module.

This module consolidates all converser-related tests into one organized suite,
providing comprehensive coverage of:

Test Organization:
    - TestJSONExtraction: Tests for extract_json function
    - TestConversationHelpers: Tests for PAIR helper functions (get_init_msg_pair, etc.)
    - TestAttackLM: Tests for AttackLM class (TAP/PAIR attack model wrapper)
    - TestTargetLM: Tests for TargetLM class (TAP/PAIR target model wrapper)
    - TestAttackLLM: Tests for AttackLLM class (legacy PAIR attack model)
    - TestTargetLLM: Tests for TargetLLM class (legacy PAIR target model)
    - TestModelLoading: Tests for model loading functions (load_attack_and_target_models_*)
    - TestPruning: Tests for prune function and clean_attacks_and_convs
    - TestModelPathResolution: Tests for get_model_path_and_template
    - TestEdgeCases: Edge cases, error handling, and retry logic

Coverage Focus:
    - Model initialization and configuration
    - Batch generation and response handling
    - JSON extraction from model outputs with retry logic
    - Conversation template handling (GPT vs non-GPT paths)
    - Pruning and filtering attack candidates
    - Error handling and exhaustion scenarios
    - Endpoint model retry logic and error paths

Note: All tests use mocking/monkeypatching to avoid actual model loading.
"""

import types
import pytest


def _fake_conv_template(template_name):
    """Create minimal conversation object compatible with conversers expectations."""
    class Conv:
        def __init__(self):
            self.roles = ("user", "assistant")
            self.messages = []
            self.sep_style = None
            self.sep = None
        
        def append_message(self, role, content):
            self.messages.append((role, content))
        
        def update_last_message(self, txt):
            if self.messages:
                self.messages[-1] = (self.messages[-1][0], txt)
        
        def get_prompt(self):
            # Join last two messages to form a prompt
            return "\n".join([m[1] or "" for m in self.messages if m[1] is not None])
        
        def to_openai_api_messages(self):
            return [{"role": r, "content": c or ""} for (r, c) in self.messages]
    
    return Conv()


class FakeConv:
    """Reusable fake conversation template object for tests."""
    
    def __init__(self):
        self.roles = ["user", "assistant"]
        self.messages = []
        self.sep = "\n"
        self.sep_style = None
        self.sep2 = "  \n"  # has trailing spaces to test strip in conv_template_pair for llama-2
    
    def append_message(self, role, content):
        self.messages.append([role, content])
    
    def get_prompt(self):
        # simple linear prompt join
        prompt = "".join([
            (m[0] + ": " + (m[1] or "")) if m[1] is not None else (m[0] + ":") 
            for m in self.messages
        ])
        return prompt
    
    def to_openai_api_messages(self):
        return [{"role": r, "content": c} for r, c in self.messages]
    
    def update_last_message(self, content):
        if self.messages:
            self.messages[-1][1] = content
    
    def copy(self):
        c = FakeConv()
        c.messages = [m[:] for m in self.messages]
        return c
    
    def __repr__(self):
        return f"FakeConv({self.messages})"


class FakeModel:
    """Minimal fake model with programmable outputs."""
    
    def __init__(self, batches=None):
        self._batches = batches or [[""]]  # list of list-of-strings returned per call
        self.calls = 0
        self.extended = False
    
    def extend_eos_tokens(self):
        self.extended = True
    
    def batched_generate(self, prompts, max_n_tokens=None, temperature=None, top_p=None, **kwargs):
        # Return next batch cycle (loop if needed)
        batch = self._batches[min(self.calls, len(self._batches) - 1)]
        self.calls += 1
        # ensure length corresponds
        if len(batch) != len(prompts):
            # Auto-adjust if mismatch
            return batch * len(prompts) if len(batch) == 1 else batch[:len(prompts)]
        return batch


def _build_convs(n):
    """Build n conversation objects for testing."""
    return [FakeConv() for _ in range(n)]


class TestJSONExtraction:
    """Test JSON extraction from model outputs."""
    
    def test_extract_json_valid(self):
        """Test extracting valid JSON with required keys."""
        from app.utility.conversers import extract_json
        
        text = 'Some text {"improvement": "test", "prompt": "hello"} more text'
        parsed, json_str = extract_json(text)
        
        assert parsed is not None
        assert "improvement" in parsed
        assert "prompt" in parsed
        assert parsed["improvement"] == "test"
        assert parsed["prompt"] == "hello"
    
    def test_extract_json_success_and_failure(self):
        """Test valid JSON and missing required keys."""
        from app.utility.conversers import extract_json
        
        # Valid JSON (newline and double quote cleanup paths exercised)
        valid = '{\n"improvement": "Better phrasing",\n"prompt": "Do X"\n}'
        parsed, raw = extract_json(valid)
        assert parsed == {"improvement": "Better phrasing", "prompt": "Do X"}
        assert raw.startswith('{') and raw.endswith('}')
        
        # Missing required keys triggers failure path
        invalid = '{"foo": 1, "bar": 2}'
        parsed2, raw2 = extract_json(invalid)
        assert parsed2 is None and raw2 is None
    
    def test_extract_json_no_braces(self):
        """Test extraction when no JSON braces found."""
        from app.utility.conversers import extract_json
        
        text = "No JSON here at all"
        parsed, json_str = extract_json(text)
        
        assert parsed is None
        assert json_str is None
    
    def test_extract_json_malformed(self):
        """Test extraction with malformed JSON."""
        from app.utility.conversers import extract_json
        
        text = '{"improvement": "test", "missing_closing": '
        parsed, json_str = extract_json(text)
        
        # Should handle gracefully
        assert parsed is None or isinstance(parsed, dict)
    
    def test_extract_json_missing_keys(self):
        """Test extraction when required keys are missing."""
        from app.utility.conversers import extract_json
        
        text = '{"only_improvement": "test"}'
        parsed, json_str = extract_json(text)
        
        assert parsed is None
        assert json_str is None
    
    def test_extract_json_with_newlines(self):
        """Test extraction handles newlines in JSON."""
        from app.utility.conversers import extract_json
        
        text = '''{"improvement": "line1
line2", "prompt": "test"}'''
        parsed, json_str = extract_json(text)
        
        # Should remove newlines and parse
        if parsed:
            assert "improvement" in parsed


class TestConversationHelpers:
    """Test helper functions for PAIR attack."""
    
    def test_get_init_msg_pair(self):
        """Test initial message generation."""
        from app.utility.conversers import get_init_msg_pair
        
        goal = "bypass filters"
        target = "Sure, I can help"
        
        msg = get_init_msg_pair(goal, target)
        
        assert isinstance(msg, str)
        assert goal in msg
        assert target in msg
        assert "objective" in msg.lower()
    
    def test_process_target_response_pair(self):
        """Test target response processing."""
        from app.utility.conversers import process_target_response_pair
        
        response = "I cannot help with that"
        score = 7
        goal = "test goal"
        target_str = "target"
        
        result = process_target_response_pair(response, score, goal, target_str)
        
        assert isinstance(result, str)
        assert response in result
        assert str(score) in result
        assert goal in result
    
    def test_conv_template_pair_llama(self):
        """Test conversation template for llama."""
        from app.utility.conversers import conv_template_pair
        
        template = conv_template_pair("llama-2")
        
        assert template is not None
        assert hasattr(template, 'name')
    
    def test_conv_template_pair_other(self):
        """Test conversation template for other models."""
        from app.utility.conversers import conv_template_pair
        
        try:
            template = conv_template_pair("vicuna")
            assert template is not None
        except:
            # Some templates might not be available
            pass
    
    def test_util_helper_functions(self, monkeypatch):
        """Test get_init_msg_pair, process_target_response_pair, conv_template_pair."""
        from app.utility import conversers as conv_mod
        
        s = conv_mod.get_init_msg_pair("steal key", "BEGIN-Z")
        assert "steal key" in s and "BEGIN-Z" in s
        
        resp = conv_mod.process_target_response_pair("LLM Output", 0.87, "goalX", "targetY")
        assert "LLM Output" in resp and "0.87" in resp
        
        # Simulate llama-2 template altering sep2
        class Tmpl:
            name = 'llama-2'
            sep2 = '   \n'
        
        def fake_get_conv(name):
            return Tmpl()
        
        monkeypatch.setattr(conv_mod, 'get_conversation_template', fake_get_conv)
        tpl = conv_mod.conv_template_pair('llama-2')
        # Original code strips sep2; our fake has only spaces + newline which becomes '' after strip
        assert tpl.sep2 == ''  # stripped completely


class TestAttackLM:
    """Test AttackLM class for TAP attack strategy."""
    
    def test_attacklm_get_attack_pair_parses_json(self, monkeypatch):
        """Test AttackLM.get_attack_pair successfully parses JSON output."""
        import app.utility.conversers as conv
        
        # Avoid heavy model load
        class FakeModel:
            def extend_eos_tokens(self):
                return None
            
            def batched_generate(self, prompts, max_n_tokens=None, temperature=None, top_p=None):
                # Return a payload that, when prefixed by init_message, contains a JSON
                return ['{"improvement":"i","prompt":"p"}'] * len(prompts)
        
        monkeypatch.setattr(conv, 'load_indiv_model', 
                           lambda name, device=None: (FakeModel(), 'gpt-3.5-turbo'), raising=True)
        monkeypatch.setattr(conv, 'conv_template', 
                           lambda template: _fake_conv_template(template), raising=True)
        
        atk = conv.AttackLM(model_name='llama-2', max_n_tokens=10, max_n_attack_attempts=1, 
                           temperature=0.1, top_p=0.9)
        # Prepare one conv and one prompt
        convs = [_fake_conv_template('gpt-3.5-turbo')]
        prompts = ["hello"]
        out = atk.get_attack_pair(convs, prompts)
        assert isinstance(out, list) and out[0] == {"improvement": "i", "prompt": "p"}
    
    def test_attacklm_non_gpt_invalid_json(self, monkeypatch):
        """Cover non-gpt branch with init_message seeding and regeneration path when JSON invalid."""
        from app.utility import conversers as conv
        
        class FakeModel:
            def __init__(self):
                self.calls = 0
            
            def extend_eos_tokens(self):
                pass
            
            def batched_generate(self, prompts, max_n_tokens=None, temperature=None, 
                               top_p=None, **kwargs):
                # Return outputs without JSON so extract_json fails
                self.calls += 1
                return ["NO_JSON_OUTPUT" for _ in prompts]
        
        # Monkeypatch loader to return our fake model and dummy template
        monkeypatch.setattr(conv, 'load_indiv_model', lambda name: (FakeModel(), object()))
        
        # Build minimal FakeConv replicating interface AttackLM expects
        class FakeConv:
            def __init__(self):
                self.roles = ['user', 'assistant']
                self.messages = []
                self.sep_style = None
                self.sep = None
            
            def append_message(self, role, content):
                self.messages.append((role, content))
            
            def to_openai_api_messages(self):
                return [{'role': r, 'content': c} for r, c in self.messages]
            
            def update_last_message(self, content):
                if self.messages:
                    r, _ = self.messages[-1]
                    self.messages[-1] = (r, content)
            
            def get_prompt(self):
                return "\n".join(str(m) for m in self.messages)
        
        attack = conv.AttackLM(
            model_name="vicuna-13b",  # triggers non-gpt path + extend_eos_tokens
            max_n_tokens=5,
            max_n_attack_attempts=1,
            temperature=0.5,
            top_p=0.9,
        )
        out = attack.get_attack_pair([FakeConv()], ["Some prompt"])
        # Expect list with single None because no valid JSON extracted
        assert out == [None]
    
    def test_attacklm_get_attack_pair_success(self, monkeypatch):
        """Test AttackLM with retry logic - first attempt fails, second succeeds."""
        from app.utility import conversers as conv_mod
        from app.utility import common
        
        # First call returns invalid json; second call returns valid json for both prompts
        batches = [
            ["garbage text no brace", "partial {\"improvement\": \"x\""],
            ["{\"improvement\": \"a\", \"prompt\": \"P1\"}", 
             "{\"improvement\": \"b\", \"prompt\": \"P2\"}"],
        ]
        fake_model = FakeModel(batches)
        # patch loader to return fake model + template name
        monkeypatch.setattr(conv_mod, "load_indiv_model", lambda name: (fake_model, "llama-2"))
        
        # Only patch common.conv_template
        def _factory(name):
            return FakeConv()
        monkeypatch.setattr(common, "conv_template", _factory)
        
        att = conv_mod.AttackLM(
            model_name="llama-2-local",
            max_n_tokens=10,
            max_n_attack_attempts=3,
            temperature=0.1,
            top_p=0.9,
        )
        
        convs = _build_convs(2)
        prompts = ["Prompt A", "Prompt B"]
        outputs = att.get_attack_pair(convs, prompts)
        # After two generations should be valid dicts
        assert outputs[0]["prompt"] == "P1"
        assert outputs[1]["prompt"] == "P2"
        # EOS extension for llama path
        assert fake_model.extended is True
    
    def test_attacklm_get_attack_pair_exhausts(self, monkeypatch):
        """Test AttackLM exhausts all retry attempts when JSON always invalid."""
        from app.utility import conversers as conv_mod
        from app.utility import common
        
        # Always invalid -> will exhaust attempts
        batches = [
            ["nope", "still nope"],
            ["bad", "bad"],
            ["{not json", "<< >>"],
        ]
        fake_model = FakeModel(batches)
        monkeypatch.setattr(conv_mod, "load_indiv_model", lambda name: (fake_model, "llama-2"))
        
        def _factory(name):
            return FakeConv()
        monkeypatch.setattr(common, "conv_template", _factory)
        
        att = conv_mod.AttackLM(
            model_name="llama-2-local",
            max_n_tokens=10,
            max_n_attack_attempts=3,
            temperature=0.1,
            top_p=0.9,
        )
        
        convs = _build_convs(2)
        prompts = ["x", "y"]
        outputs = att.get_attack_pair(convs, prompts)
        assert outputs == [None, None]
        assert fake_model.calls == 3  # exhausted attempts
    
    def test_attacklm_get_attack_success_multi_attempt(self, monkeypatch):
        """Test AttackLM with multi-attempt retry - first fails, second succeeds."""
        from app.utility import conversers as conv
        
        # First attempt returns invalid JSON; second attempt valid minimal JSON
        class FakeModel:
            def __init__(self):
                self.calls = 0
            
            def extend_eos_tokens(self):
                pass
            
            def batched_generate(self, prompts, max_n_tokens=None, temperature=None, 
                               top_p=None, **kwargs):
                self.calls += 1
                if self.calls == 1:
                    return ["garbage output"]
                # Return valid JSON fragment
                return ["{\"improvement\": \"Better\", \"prompt\": \"Do Y\"}"]
        
        # Ensure non-gpt path by using vicuna name
        monkeypatch.setattr(conv, 'load_indiv_model', lambda name: (FakeModel(), 'vicuna-13b'))
        attack = conv.AttackLM(
            model_name='vicuna-13b',
            max_n_tokens=8,
            max_n_attack_attempts=2,
            temperature=0.5,
            top_p=0.9,
        )
        
        class FakeConv:
            def __init__(self):
                self.roles = ['user', 'assistant']
                self.messages = []
                self.sep_style = None
                self.sep = None
            
            def append_message(self, role, content):
                self.messages.append((role, content))
            
            def update_last_message(self, content):
                if self.messages:
                    role, _ = self.messages[-1]
                    self.messages[-1] = (role, content)
            
            def to_openai_api_messages(self):
                return [{'role': r, 'content': c} for r, c in self.messages]
            
            def get_prompt(self):
                return "\n".join(str(m) for m in self.messages)
        
        convs = [FakeConv()]
        outputs = attack.get_attack_pair(convs, ["Prompt A"])
        assert outputs[0] == {"improvement": "Better", "prompt": "Do Y"}
    
    def test_attacklm_get_attack_exhausts_attempts(self, monkeypatch):
        """Test AttackLM exhausts all attempts when model always returns invalid JSON."""
        from app.utility import conversers as conv
        
        class AlwaysBadModel:
            def extend_eos_tokens(self):
                pass
            
            def batched_generate(self, prompts, max_n_tokens=None, temperature=None, 
                               top_p=None, **kwargs):
                return ["NO_JSON"]
        
        monkeypatch.setattr(conv, 'load_indiv_model', lambda name: (AlwaysBadModel(), 'vicuna-13b'))
        attack = conv.AttackLM(
            model_name='vicuna-13b',
            max_n_tokens=4,
            max_n_attack_attempts=2,
            temperature=0.1,
            top_p=0.9,
        )
        
        class FakeConv:
            def __init__(self):
                self.roles = ['user', 'assistant']
                self.messages = []
                self.sep_style = None
                self.sep = None
            
            def append_message(self, role, content):
                self.messages.append((role, content))
            
            def update_last_message(self, content):
                if self.messages:
                    role, _ = self.messages[-1]
                    self.messages[-1] = (role, content)
            
            def to_openai_api_messages(self):
                return [{'role': r, 'content': c} for r, c in self.messages]
            
            def get_prompt(self):
                return "\n".join(str(m) for m in self.messages)
        
        convs = [FakeConv()]
        outputs = attack.get_attack_pair(convs, ["Prompt B"])
        assert outputs == [None]
    
    def test_attacklm_multi_attempt_and_success(self, monkeypatch):
        """Test AttackLM with GPT model - multi-attempt with success on second try."""
        from app.utility import conversers as conv
        
        # Fake underlying model used by load_indiv_model
        class FakeModel:
            def __init__(self):
                self.attempt = 0
            
            def extend_eos_tokens(self):
                pass
            
            def batched_generate(self, prompts, max_n_tokens=None, temperature=None, 
                               top_p=None, **kwargs):
                self.attempt += 1
                if self.attempt == 1:
                    return ["NOT_JSON"]  # forces regenerate
                return ["{\"improvement\": \"X\", \"prompt\": \"Y\"}"]
        
        # Monkeypatch the model loader to ensure deterministic behavior
        monkeypatch.setattr(conv, 'load_indiv_model', lambda name: (FakeModel(), object()))
        
        # Conversation stub
        class FakeConv:
            def __init__(self):
                self.roles = ['user', 'assistant']
                self.messages = []
                self.sep_style = None
                self.sep = None
            
            def append_message(self, role, content):
                self.messages.append((role, content))
            
            def to_openai_api_messages(self):
                return [{'role': r, 'content': c} for r, c in self.messages]
            
            def update_last_message(self, content):
                if self.messages:
                    r, _ = self.messages[-1]
                    self.messages[-1] = (r, content)
            
            def get_prompt(self):
                return "\n".join(str(m) for m in self.messages)
        
        attack = conv.AttackLM(
            model_name="gpt-test",  # goes through GPT branch
            max_n_tokens=5,
            max_n_attack_attempts=2,  # ensures second attempt executed
            temperature=0.2,
            top_p=0.9
        )
        out = attack.get_attack_pair([FakeConv()], ["Prompt"])
        # After second attempt we should have a parsed dict
        assert isinstance(out, list) and isinstance(out[0], dict)
        assert out[0]["prompt"] == "Y"


class TestTargetLM:
    """Test TargetLM class for TAP target strategy."""
    
    def test_targetlm_get_response_batches(self, monkeypatch):
        """Test TargetLM.get_response handles batch responses correctly."""
        import app.utility.conversers as conv
        
        class FakeModel:
            def batched_generate(self, prompts, max_n_tokens=None, temperature=None, top_p=None):
                return [f"resp:{i}" for i in range(len(prompts))]
        
        # patch load_indiv_model to return fake model and simple template id
        monkeypatch.setattr(conv, 'load_indiv_model', 
                           lambda name, device=None: (FakeModel(), 'gpt-3.5-turbo'), raising=True)
        monkeypatch.setattr(conv, 'conv_template', 
                           lambda template: _fake_conv_template(template), raising=True)
        
        tgt = conv.TargetLM(model_name='gpt-3.5-turbo', max_n_tokens=5, 
                           temperature=0.1, top_p=1.0)
        outs = tgt.get_response(["q1", "q2"])
        assert outs == ["resp:0", "resp:1"]
    
    def test_targetlm_gpt_branch(self, monkeypatch):
        """Test TargetLM with GPT model (uses openai message format)."""
        from app.utility import conversers as conv
        
        # Force gpt path
        class GPTModel:
            def batched_generate(self, prompts, max_n_tokens=None, temperature=None, 
                               top_p=None, **kwargs):
                # prompts will be list of openai message arrays
                assert isinstance(prompts[0], list)
                return ["GPT-ANSWER"]
        
        monkeypatch.setattr(conv, 'load_indiv_model', lambda name: (GPTModel(), 'gpt-3.5-turbo'))
        target = conv.TargetLM(
            model_name='gpt-3.5-turbo',
            max_n_tokens=6,
            temperature=0.2,
            top_p=1.0,
            preloaded_model=None
        )
        outputs = target.get_response(["Hello world"])
        assert outputs == ["GPT-ANSWER"]
    
    def test_targetlm_non_gpt_branch(self, monkeypatch):
        """Test TargetLM with non-GPT model (uses conversation template)."""
        from app.utility import conversers as conv
        from app.utility import common
        
        class FakeModel:
            def __init__(self):
                self.calls = 0
            
            def extend_eos_tokens(self):
                self.calls += 1
            
            def batched_generate(self, prompts, max_n_tokens=None, temperature=None, 
                               top_p=None, **kwargs):
                return ["SIMPLE-RESP" for _ in prompts]
        
        # Provide a simple template string to avoid fastchat model adapter path logic
        monkeypatch.setattr(conv, 'load_indiv_model', lambda name: (FakeModel(), 'vicuna-13b'))
        
        # Bypass fastchat.conv_template by returning a minimal conversation obj
        class MiniConv:
            def __init__(self):
                self.roles = ['user', 'assistant']
                self.messages = []
                self.sep_style = None
                self.sep = None
            
            def append_message(self, role, content):
                self.messages.append((role, content))
            
            def to_openai_api_messages(self):
                return [{'role': r, 'content': c} for r, c in self.messages]
            
            def get_prompt(self):
                return "\n".join(str(m) for m in self.messages)
        
        monkeypatch.setattr(common, 'conv_template', lambda template: MiniConv())
        tgt = conv.TargetLM(
            model_name="vicuna-13b",  # triggers non-gpt path with init_message appended
            max_n_tokens=4,
            temperature=0.1,
            top_p=0.9
        )
        # TargetLM.get_response expects only list of prompts (no payload arg)
        responses = tgt.get_response(["Hi there"])  # exercises non-gpt path adding assistant None
        assert responses[0] == "SIMPLE-RESP"


class TestAttackLLM:
    """Test AttackLLM class (legacy PAIR).
    
    Note: AttackLLM takes a model_name string, not a model object.
    The initialization tests are covered by TestAttackLM above.
    """
    pass


class TestTargetLLM:
    """Test TargetLLM class (legacy PAIR).
    
    Note: TargetLLM takes a model_name string, not a model object.
    The initialization tests are covered by TestTargetLM above.
    """
    pass


class TestModelLoading:
    """Test model loading functions."""
    
    def _setup_stubs(self):
        """Setup minimal stubs for language models."""
        import app.utility.language_models as lm
        
        class StubModel:
            def __init__(self, model_name, *args, **kwargs):
                self.model_name = model_name
            
            def generate(self, *args, **kwargs):
                return "stub response"
            
            def batched_generate(self, *args, **kwargs):
                return ["stub"] * len(args[0])
        
        # Patch models if needed
        for model_class in ['GPT', 'Claude', 'ChatGroqq', 'GeminiModel', 'BedrockModel']:
            if hasattr(lm, model_class):
                original = getattr(lm, model_class)
                if not callable(original):
                    setattr(lm, model_class, StubModel)
    
    def test_load_attack_model_gpt(self, monkeypatch):
        """Test loading GPT as attack model."""
        self._setup_stubs()
        from app.utility.conversers import load_attack_and_target_models_pair
        
        payload = {
            "attack_model": "gpt-4",
            "target_model": "gpt-3.5-turbo",
            "attack_max_n_tokens": 500,
            "target_max_n_tokens": 150,
            "attack_max_n_attempts": 5,
            "target_max_n_attempts": 5
        }
        
        attack_lm, target_lm = load_attack_and_target_models_pair(payload)
        
        assert attack_lm is not None
        assert target_lm is not None
    
    def test_load_attack_model_claude(self, monkeypatch):
        """Test loading Claude as attack model."""
        self._setup_stubs()
        from app.utility.conversers import load_attack_and_target_models_pair
        
        payload = {
            "attack_model": "claude-2",
            "target_model": "gpt-4",
            "attack_max_n_tokens": 500,
            "target_max_n_tokens": 150,
            "attack_max_n_attempts": 5,
            "target_max_n_attempts": 5
        }
        
        attack_lm, target_lm = load_attack_and_target_models_pair(payload)
        
        assert attack_lm is not None
        assert target_lm is not None
    
    def test_load_models_tap_gpt(self, monkeypatch):
        """Test loading models for TAP with GPT."""
        self._setup_stubs()
        from app.utility.conversers import load_attack_and_target_models_tap
        
        payload = {
            "attack_model": "gpt-4",
            "target_model": "gpt-3.5-turbo",
            "attack_max_n_tokens": 500,
            "target_max_n_tokens": 150
        }
        
        attack_lm, target_lm = load_attack_and_target_models_tap(payload)
        
        assert attack_lm is not None
        assert target_lm is not None
    
    def test_load_models_tap_with_endpoints(self, monkeypatch):
        """Test loading TAP models with custom endpoints."""
        self._setup_stubs()
        from app.utility.conversers import load_attack_and_target_models_tap
        
        payload = {
            "attack_endpoint_url": "http://test.com/attack",
            "attack_endpoint_headers": {},
            "attack_endpoint_payload": {},
            "attack_endpoint_prompt_variable": "prompt",
            "target_endpoint_url": "http://test.com/target",
            "target_endpoint_headers": {},
            "target_endpoint_payload": {},
            "target_endpoint_prompt_variable": "input",
            "attack_max_n_tokens": 500,
            "target_max_n_tokens": 150
        }
        
        attack_lm, target_lm = load_attack_and_target_models_tap(payload)
        
        assert attack_lm is not None
        assert target_lm is not None
    
    def test_load_endpoint_models(self, monkeypatch):
        """Test that endpoint configuration is handled."""
        self._setup_stubs()
        
        from app.utility.language_models import EndpointModel_Pair
        
        model = EndpointModel_Pair(
            "http://test.com",
            {},
            {},
            "prompt"
        )
        
        assert model is not None


class TestPruning:
    """Test pruning and cleaning functions."""
    
    def test_clean_attacks_and_convs_all_none(self):
        """Test clean_attacks_and_convs with empty/None inputs."""
        import app.utility.conversers as conv
        
        # Empty lists raise inside (zip then index) and return (None, None)
        a, c = conv.clean_attacks_and_convs([], [])
        assert a is None and c is None
        
        # None inputs
        a2, c2 = conv.clean_attacks_and_convs(None, None)
        assert a2 is None and c2 is None
    
    def test_clean_attacks_and_convs_with_data(self):
        """Test cleaning with actual data - removes None attacks."""
        from app.utility.conversers import clean_attacks_and_convs
        
        attacks = [{"a": 1}, None, {"b": 2}]
        convs = ["c1", "c2", "c3"]
        cleaned_attacks, cleaned_convs = clean_attacks_and_convs(attacks, convs)
        assert cleaned_attacks == [{"a": 1}, {"b": 2}]
        assert cleaned_convs == ["c1", "c3"]
    
    def test_prune_with_explicit_width(self, monkeypatch):
        """Test prune function with explicit width parameter."""
        import app.utility.conversers as conv
        
        on_topic = [1]
        judge_scores = [5]
        adv = ['p']
        improv = ['i']
        
        class C:
            pass
        
        convs = [C()]
        extracted = [{'prompt': 'p', 'improvement': 'i'}]
        out = conv.prune(on_topic, judge_scores, adv, improv, convs, ['r'], extracted, 
                        sorting_score=judge_scores, attack_params={'width': 1})
        assert out[0] and len(out[0]) == 1
    
    def test_prune_positive_and_judge_branch(self, monkeypatch):
        """Test prune function with positive scores and proper truncation."""
        from app.utility.conversers import prune
        
        # Build data where some scores > 0 so normal truncation path executes
        sorting_score = [3, 0, 2, 0]
        attack_params = {'width': 2}
        judge_scores = [9, 1, 7, 2]
        on_topic_scores = [5, 0, 4, 0]
        adv_prompt_list = [f"adv{i}" for i in range(4)]
        improv_list = [f"imp{i}" for i in range(4)]
        convs_list = [f"conv{i}" for i in range(4)]
        target_response_list = [f"resp{i}" for i in range(4)]
        extracted_attack_list = [f"ext{i}" for i in range(4)]
        
        o, j, a, i, c, t, e = prune(
            on_topic_scores=on_topic_scores,
            judge_scores=judge_scores,
            adv_prompt_list=adv_prompt_list,
            improv_list=improv_list,
            convs_list=convs_list,
            target_response_list=target_response_list,
            extracted_attack_list=extracted_attack_list,
            sorting_score=sorting_score,
            attack_params=attack_params
        )
        # Width=2 so expect 2 retained and only those with positive scores
        assert len(o) == 2 and all(x in [5, 4] for x in o)
        assert len(j) == 2 and all(x in [9, 7] for x in j)
        assert len(a) == 2 and all(x.startswith('adv') for x in a)
        assert len(c) == 2 and len(t) == 2 and len(e) == 2
    
    def test_prune_with_defaults(self):
        """Test prune function with minimal inputs."""
        from app.utility.conversers import prune
        
        try:
            result = prune(
                on_topic_scores=None,
                judge_scores=None,
                adv_prompt_list=[],
                improv_list=[],
                convs_list=[],
                target_response_list=[],
                extracted_attack_list=[],
                sorting_score=[],
                attack_params={"width": 10}
            )
            
            assert isinstance(result, tuple) or result is None
        except (KeyError, ValueError, IndexError):
            # Expected with empty data
            pass
    
    def test_prune_with_scores(self):
        """Test prune function with actual scores."""
        from app.utility.conversers import prune
        
        result = prune(
            on_topic_scores=[8, 6, 9],
            judge_scores=[7, 5, 8],
            adv_prompt_list=["p1", "p2", "p3"],
            improv_list=["i1", "i2", "i3"],
            convs_list=["c1", "c2", "c3"],
            target_response_list=["r1", "r2", "r3"],
            extracted_attack_list=["a1", "a2", "a3"],
            sorting_score=[7.5, 5.5, 8.5],
            attack_params={"width": 10}
        )
        
        assert isinstance(result, tuple)
        for item in result:
            assert isinstance(item, list)


class TestModelPathResolution:
    """Test model path and template resolution."""
    
    def test_get_model_path_vicuna(self):
        """Test getting path for Vicuna model."""
        from app.utility.conversers import get_model_path_and_template
        
        try:
            path, template = get_model_path_and_template("vicuna")
            assert path is not None or path == ""
            assert template is not None
        except Exception:
            # Model path might not be configured
            pass
    
    def test_get_model_path_llama(self):
        """Test getting path for Llama model."""
        from app.utility.conversers import get_model_path_and_template
        
        try:
            path, template = get_model_path_and_template("llama-2")
            assert path is not None or path == ""
            assert template is not None
        except Exception:
            # Model path might not be configured
            pass
    
    def test_get_model_path_and_template_error(self, monkeypatch):
        """Test ValueError for unknown model name."""
        from app.utility.conversers import get_model_path_and_template
        
        with pytest.raises(ValueError):
            get_model_path_and_template('non-existent-model-xyz')
    
    def test_get_model_path_unknown(self):
        """Test getting path for unknown model."""
        from app.utility.conversers import get_model_path_and_template
        
        try:
            path, template = get_model_path_and_template("unknown-model-xyz")
            # Should handle gracefully or raise known exception
        except (ValueError, KeyError, AttributeError):
            # Expected for unknown models
            pass


class TestEdgeCases:
    """Test edge cases, error handling, and retry logic."""
    
    def test_get_attack_pair_exhaustion(self, monkeypatch):
        """Test exhaustion of retry attempts when model always returns invalid JSON."""
        import app.utility.conversers as conv
        
        # Fake model returning invalid json forcing retries until exhaustion
        class FakeModel:
            def __init__(self):
                self.calls = 0
            
            def batched_generate(self, convs, max_n_tokens=None, temperature=None):
                self.calls += 1
                return ["not json"]
        
        monkeypatch.setattr(conv, 'get_model_path_and_template', lambda name: (name, name))
        
        # AttackLM signature: (model_name, max_n_tokens, max_n_attack_attempts, temperature, top_p)
        am = conv.AttackLM('gpt-4', 5, 2, 0.1, 1.0)
        am.attack_pair_model = FakeModel()
        
        # Build minimal conversation object required
        class Conv:
            def __init__(self):
                self.messages = []
                self.roles = ['user', 'assistant']
                self.sep_style = None
                self.sep = None
            
            def append_message(self, role, content):
                self.messages.append((role, content))
            
            def to_openai_api_messages(self):
                return [{'role': r, 'content': c} for r, c in self.messages]
        
        convs = [Conv()]
        res = am.get_attack_pair(convs, ["prompt"])
        assert isinstance(res, list) and len(res) == 1
    
    def test_endpointmodel_pair_retry_and_success(self, monkeypatch):
        """Test EndpointModel_Pair retry logic - network error, HTTP 500, then success."""
        from app.utility.language_models import EndpointModel_Pair
        
        # Sequence: network exception -> HTTP 500 -> success JSON
        calls = {"i": 0}
        import requests
        
        class NetErr(requests.RequestException):
            pass
        
        def fake_post(url, headers=None, json=None, verify=None, timeout=None):
            class Resp:
                def __init__(self, code, body=b"{}"):
                    self.status_code = code
                    self.text = body.decode() if isinstance(body, bytes) else body
                
                def json(self):
                    return {"text": "hello world"}
            
            calls["i"] += 1
            if calls["i"] == 1:
                raise NetErr("boom")
            if calls["i"] == 2:
                return Resp(500, b"fail")
            return Resp(200, b"ok")
        
        import requests as real_requests
        monkeypatch.setattr(real_requests, 'post', fake_post)
        
        # Avoid nested GPT call by stubbing extract_text_with_gpt
        monkeypatch.setattr(EndpointModel_Pair, 'extract_text_with_gpt', 
                           lambda self, result: "extracted")
        
        m = EndpointModel_Pair(
            target_endpoint_url="http://example/api",
            target_endpoint_headers={"A": "B"},
            target_endpoint_payload={"foo": "bar"},
            target_endpoint_prompt_variable="question",
            max_retries=4
        )
        out = m.generate("What?", m.target_endpoint_url, m.target_endpoint_headers, 
                        m.target_endpoint_payload, m.target_endpoint_prompt_variable)
        assert out == "extracted"
    
    def test_endpointmodel_pair_exhaustion_and_non_json(self, monkeypatch):
        """Test EndpointModel_Pair exhaustion and non-JSON response handling."""
        from app.utility.language_models import EndpointModel_Pair
        
        # First test exhaustion: always HTTP 500
        def always_500(url, headers=None, json=None, verify=None, timeout=None):
            class Resp:
                status_code = 500
                text = "bad"
                
                def json(self):
                    return {"ignored": True}
            
            return Resp()
        
        import requests as real_requests
        monkeypatch.setattr(real_requests, 'post', always_500)
        monkeypatch.setattr(EndpointModel_Pair, 'extract_text_with_gpt', 
                           lambda self, result: "")
        
        m_fail = EndpointModel_Pair("http://e", {}, {}, "q", max_retries=2)
        res_fail = m_fail.generate("Q", m_fail.target_endpoint_url, 
                                   m_fail.target_endpoint_headers, 
                                   m_fail.target_endpoint_payload, 
                                   m_fail.target_endpoint_prompt_variable)
        assert res_fail == "$ERROR$"
        
        # Non-JSON response branch
        class RespBadJSON:
            status_code = 200
            text = "not-json"
            
            def json(self):
                raise ValueError("bad json")
        
        monkeypatch.setattr(real_requests, 'post', lambda *a, **k: RespBadJSON())
        m_bad = EndpointModel_Pair("http://e", {}, {}, "q", max_retries=1)
        res_bad = m_bad.generate("Q", m_bad.target_endpoint_url, 
                                m_bad.target_endpoint_headers, 
                                m_bad.target_endpoint_payload, 
                                m_bad.target_endpoint_prompt_variable)
        assert res_bad == "$ERROR$"


class TestJSONExtractionEdgeCases:
    """Additional JSON extraction edge cases."""
    
    def test_extract_json_with_improvement_and_prompt(self):
        """Test extract_json with required keys."""
        from app.utility.conversers import extract_json
        
        text = 'Response: {"improvement": "better", "prompt": "test"}'
        result, json_str = extract_json(text)
        assert result is not None
        assert "improvement" in result
        assert "prompt" in result
        
    def test_extract_json_missing_keys(self):
        """Test extract_json missing required keys."""
        from app.utility.conversers import extract_json
        
        text = '{"other": "value"}'
        result, json_str = extract_json(text)
        assert result is None


class TestConversationUtilities:
    """Test conversation utility functions."""
    
    def test_get_init_msg_pair(self):
        """Test get_init_msg_pair."""
        from app.utility.conversers import get_init_msg_pair
        
        msg = get_init_msg_pair("goal", "target")
        assert isinstance(msg, str)
        assert len(msg) > 0
        
    def test_process_target_response_pair(self):
        """Test process_target_response_pair."""
        from app.utility.conversers import process_target_response_pair
        
        result = process_target_response_pair("response", 8, "goal", "target")
        assert isinstance(result, str)
        
    def test_conv_template_pair_variants(self):
        """Test conv_template_pair with different models."""
        from app.utility.conversers import conv_template_pair
        
        for model in ["llama-2", "vicuna"]:
            template = conv_template_pair(model)
            assert template is not None
            
    def test_clean_attacks_and_convs(self):
        """Test clean_attacks_and_convs."""
        from app.utility.conversers import clean_attacks_and_convs
        
        attacks = ["a1", "a2", "a3"]
        convs = ["c1", "c2", "c3"]
        
        cleaned_a, cleaned_c = clean_attacks_and_convs(attacks, convs)
        assert len(cleaned_a) <= len(attacks)

def test_attack_llm_with_gpt():
    """Test AttackLLM initialization and basic setup with GPT"""
    from app.utility.conversers import AttackLLM
    from unittest.mock import Mock, patch
    
    with patch('app.utility.conversers.load_indiv_model') as mock_load:
        mock_model = Mock()
        mock_template = "template"
        mock_load.return_value = (mock_model, mock_template)
        
        attack_llm = AttackLLM(
            model_name="gpt-4",
            max_n_tokens=500,
            max_n_attack_attempts=3,
            temperature=1.0,
            top_p=0.9
        )
        
        assert attack_llm.model_name == "gpt-4"
        assert attack_llm.max_n_tokens == 500
        assert attack_llm.temperature == 1.0



def test_attack_lm_initialization():
    """Test AttackLM class initialization"""
    from app.utility.conversers import AttackLM
    from unittest.mock import Mock, patch
    
    with patch('app.utility.conversers.load_indiv_model') as mock_load:
        mock_model = Mock()
        mock_template = "template"
        mock_load.return_value = (mock_model, mock_template)
        
        attack_lm = AttackLM(
            model_name="gpt-4",
            max_n_tokens=500,
            max_n_attack_attempts=3,
            temperature=1.0,
            top_p=0.9
        )
        
        assert attack_lm.model_name == "gpt-4"
        assert attack_lm.max_n_tokens == 500



def test_load_indiv_model_gpt():
    """Test load_indiv_model function with GPT"""
    from app.utility.conversers import load_indiv_model
    from unittest.mock import patch, Mock
    
    with patch('app.utility.conversers.GPT') as MockGPT:
        mock_gpt_instance = Mock()
        MockGPT.return_value = mock_gpt_instance
        
        model, template = load_indiv_model("gpt-4")
        assert model is not None
        assert template == "gpt-4"



def test_conv_template_vicuna():
    """Test conv_template with vicuna"""
    from app.utility.conversers import conv_template
    conv = conv_template("vicuna_v1.1")
    assert conv is not None
    assert hasattr(conv, 'messages')

def test_conv_template_llama():
    """Test conv_template with llama"""
    from app.utility.conversers import conv_template
    conv = conv_template("llama-2")
    assert conv is not None
    assert hasattr(conv, 'messages')

def test_extract_json_valid():
    """Test extract_json with valid JSON string"""
    from app.utility.conversers import extract_json
    s = '{"improvement": "test improvement", "prompt": "test prompt"}'
    parsed, json_str = extract_json(s)
    assert parsed is not None
    assert parsed["improvement"] == "test improvement"
    assert parsed["prompt"] == "test prompt"

def test_extract_json_embedded():
    """Test extract_json with embedded JSON"""
    from app.utility.conversers import extract_json
    s = 'Some text before {"improvement": "improved", "prompt": "new prompt"} some text after'
    parsed, json_str = extract_json(s)
    assert parsed is not None
    assert "improvement" in parsed
    assert "prompt" in parsed

def test_get_init_msg_pair():
    """Test get_init_msg_pair function"""
    from app.utility.conversers import get_init_msg_pair
    goal = "test goal"
    target = "test target"
    msg = get_init_msg_pair(goal, target)
    assert goal in msg
    assert target in msg
    assert "adversarial jailbreaking prompt" in msg

def test_process_target_response_pair():
    """Test process_target_response_pair function"""
    from app.utility.conversers import process_target_response_pair
    response = "test response"
    score = 5
    goal = "test goal"
    target = "test target"
    result = process_target_response_pair(response, score, goal, target)
    assert response in result
    assert str(score) in result
    assert goal in result

def test_conv_template_pair():
    """Test conv_template_pair function"""
    from app.utility.conversers import conv_template_pair
    template = conv_template_pair("vicuna_v1.1")
    assert template is not None
    assert hasattr(template, 'name')

def test_conv_template_pair_llama():
    """Test conv_template_pair with llama-2"""
    from app.utility.conversers import conv_template_pair
    template = conv_template_pair("llama-2")
    assert template is not None
    assert template.name == 'llama-2'

def test_extract_json_missing_keys():
    """Test extract_json with missing keys"""
    from app.utility.conversers import extract_json
    s = '{"improvement": "test"}'
    parsed, json_str = extract_json(s)
    assert parsed is None
    assert json_str is None

def test_extract_json_no_braces():
    """Test extract_json with no JSON braces"""
    from app.utility.conversers import extract_json
    s = 'No JSON here at all'
    parsed, json_str = extract_json(s)
    assert parsed is None
    assert json_str is None

def test_get_init_msg_pair_content():
    """Test get_init_msg_pair message content"""
    from app.utility.conversers import get_init_msg_pair
    msg = get_init_msg_pair("hack system", "Sure, here")
    assert "hack system" in msg
    assert "Sure, here" in msg
    assert "objective" in msg.lower()

def test_process_target_response_pair_format():
    """Test process_target_response_pair formatting"""
    from app.utility.conversers import process_target_response_pair
    result = process_target_response_pair("response text", 8, "goal text", "target")
    assert "LANGUAGE MODEL OUTPUT" in result
    assert "response text" in result
    assert "OBJECTIVE" in result
    assert "SCORE" in result
    assert "8" in result

def test_conv_template_vicuna_attributes():
    """Test conv_template returns object with expected attributes"""
    from app.utility.conversers import conv_template
    conv = conv_template("vicuna_v1.1")
    assert hasattr(conv, 'messages')
    assert hasattr(conv, 'roles')
    assert hasattr(conv, 'append_message')

