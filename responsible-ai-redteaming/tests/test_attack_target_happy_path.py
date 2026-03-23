'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import pytest


def test_attack_and_target_happy_path(monkeypatch):
    from app.utility import conversers as conv

    # Stub underlying language model generate / batched_generate used by AttackLM/TargetLM wrappers
    class FakeLM:
        def __init__(self, name="fake"):
            self.name = name
        def generate(self, conversation, max_n_tokens=None, temperature=None, top_p=None):
            # produce simple echo marker
            return "FAKE-RESP"
        def batched_generate(self, conversations, max_n_tokens=None, temperature=None, top_p=None, **kwargs):
            # accept optional params like top_p to mirror production signature loosely
            return ["FAKE-BATCH" for _ in conversations]

    # Monkeypatch the various model loader functions used inside AttackLM/TargetLM construction
    monkeypatch.setattr(conv, 'GPT', FakeLM)
    monkeypatch.setattr(conv, 'Claude', FakeLM)
    monkeypatch.setattr(conv, 'ChatGroqq', FakeLM)
    monkeypatch.setattr(conv, 'GeminiModel', FakeLM)
    monkeypatch.setattr(conv, 'LlamaModel', FakeLM)
    monkeypatch.setattr(conv, 'PaLM', FakeLM)

    # AttackLM signature: (model_name, max_n_tokens, max_n_attack_attempts, temperature, top_p)
    attack = conv.AttackLM(
        model_name="gpt-4",
        max_n_tokens=5,
        max_n_attack_attempts=1,
        temperature=0.2,
        top_p=1.0
    )
    # TargetLM signature: (model_name, max_n_tokens, temperature, top_p)
    target = conv.TargetLM(
        model_name="gpt-3.5-turbo",
        max_n_tokens=5,
        temperature=0.2,
        top_p=1.0
    )

    # Basic conversation flow: attack prompt then target response
    attack_prompt = "Explain something"
    # Build conversation objects via template helper to satisfy AttackLM expectations
    # Build a minimal fake conversation object matching interface used in AttackLM
    class FakeConv:
        def __init__(self):
            self.roles = ['user','assistant']
            self.messages = []
            self.sep_style = None
            self.sep = None
        def append_message(self, role, content):
            self.messages.append((role, content))
        def to_openai_api_messages(self):
            return [{'role': r, 'content': c} for r,c in self.messages]
        def update_last_message(self, content):
            if self.messages:
                role,_ = self.messages[-1]
                self.messages[-1] = (role, content)
        def get_prompt(self):
            return "\n".join(str(m) for m in self.messages)
    attack_out = attack.get_attack_pair([FakeConv()], [attack_prompt])
    assert isinstance(attack_out, list)

    target_out = target.get_response(["Follow up"])
    assert isinstance(target_out, list)
    # Ensure stub outputs appear
    assert attack_out[0] in ("FAKE-BATCH", "FAKE-RESP", None)
    assert target_out[0] in ("FAKE-BATCH", "FAKE-RESP", None)
