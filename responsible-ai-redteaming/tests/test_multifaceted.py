'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import pytest


def test_multifaceted_evaluate_aggregation(monkeypatch):
    """Smoke test for MultifacetedEvaluation.evaluate aggregation structure with stubbed model.
    Ensures method executes and returns a result object with expected attributes without invoking real APIs.
    """
    import importlib
    import app.utility.multifaceted as mf
    if not hasattr(mf.MultifacetedEvaluation, 'language_model'):
        mf = importlib.reload(mf)

    # Provide required constants if absent
    setattr(mf, 'AZURE_GPT4_MODEL_NAME', getattr(mf, 'AZURE_GPT4_MODEL_NAME', None) or 'gpt4-deployment')
    setattr(mf, 'AZURE_GPT4_API_KEY', getattr(mf, 'AZURE_GPT4_API_KEY', None) or 'key')
    setattr(mf, 'AZURE_GPT4_API_BASE', getattr(mf, 'AZURE_GPT4_API_BASE', None) or 'http://base')
    setattr(mf, 'AZURE_GPT4_API_VERSION', getattr(mf, 'AZURE_GPT4_API_VERSION', None) or '2024-01-01')

    class FakeConv:
        def __init__(self):
            self.roles = ['user','assistant']
            self.messages = []
        def set_system_message(self, msg):
            self.messages.append({'role':'system','content':msg})
        def append_message(self, role, content):
            self.messages.append({'role':role,'content':content})
        def to_openai_api_messages(self):
            return list(self.messages)

    # Replace template factory
    monkeypatch.setattr(mf, 'get_conversation_template', lambda *_: FakeConv())

    # Simple model returning a single-number rating string; production code tolerates this (may parse as default False booleans)
    ratings = ["Rating: 6", "Rating: 4", "Rating: 7"]
    calls = {'i':0}
    def fake_language_model(self, conversation):
        idx = min(calls['i'], len(ratings)-1)
        content = ratings[idx]
        calls['i'] += 1
        return {"choices":[{"message":{"content":content}}]}
    monkeypatch.setattr(mf.MultifacetedEvaluation, 'language_model', fake_language_model)

    m = mf.MultifacetedEvaluation('k','e','v','m')
    result = m.evaluate("Intent", "Para1 line1\nPara1 line2\nPara2 line1\nTail line")

    # Structural checks
    for attr in ('document_level','paragraph_level','sentence_level','joint_level','combination_level'):
        assert hasattr(result, attr)
        seg = getattr(result, attr)
        assert hasattr(seg, 'safeguard_violation')
        assert hasattr(seg, 'relative_truthfulness')
        assert isinstance(seg.safeguard_violation, bool)
        assert isinstance(seg.relative_truthfulness, bool)
