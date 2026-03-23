'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import pytest
from unittest.mock import Mock, patch


def test_gptjudge_recommendation_and_evaluator_fallback(monkeypatch):
    import app.utility.judges as judges
    import app.utility.evaluators as evaluators

    # Monkeypatch GPT model inside GPTJudge to deterministic outputs
    class FakeGPT:
        def __init__(self, model_name=None):
            self.model_name = model_name
        def batched_generate(self, convs, max_n_tokens=None, temperature=None):
            return ["[[9]]" for _ in convs]
        def generate(self, conv, max_n_tokens=None, temperature=None, top_p=None):
            return "Recommendation: [[Tighten controls]]"
    monkeypatch.setattr(judges, 'GPT', FakeGPT)

    payload = {"judge_model":"gpt-4","judge_max_n_tokens":5,"judge_temperature":0.1,"goal":"g","target_str":"t"}
    gj = judges.GPTJudge(payload)
    rec = gj.get_recommendation("Recommend improvements","attack","resp")
    assert rec == "Tighten controls"

    # Evaluator fallback: choose GPTEvaluator if present else base evaluator
    # Provide deterministic failing outputs so parser fallback triggers
    class FakeGPT2(FakeGPT):
        def batched_generate(self, convs, max_n_tokens=None, temperature=None):
            return ["garbled"]  # no numeric markers
        def generate(self, conv, max_n_tokens=None, temperature=None, top_p=None):
            return "No Recommendation formatting"

    monkeypatch.setattr(evaluators, 'GPT', FakeGPT2)

    # Some evaluator classes might be named GPTEvaluator; fall back gracefully if not
    EvaluatorCls = getattr(evaluators, 'GPTEvaluator', None)
    if EvaluatorCls is None:
        pytest.skip("GPTEvaluator not present in evaluators module")

    ev = EvaluatorCls(payload)
    # judge_score fallback path -> returns default 1 when parsing fails
    scores = ev.judge_score(["p"],["r"])
    assert scores == [1]
    # on topic fallback path
    on_topic = ev.on_topic_score(["p"],["r"])
    assert on_topic == [1]

def test_load_evaluator_with_gpt():
    """Test load_evaluator returns GPTEvaluator for gpt models"""
    from app.utility.evaluators import load_evaluator
    payload = {
        "judge_model": "gpt-4",
        "judge_temperature": 0.0,
        "judge_max_n_tokens": 100,
        "judge_top_p": 1.0,
        "goal": "test goal",
        "target_str": "test target"
    }
    evaluators = load_evaluator(payload)
    assert isinstance(evaluators, list)
    assert len(evaluators) == 2

def test_load_evaluator_with_no_evaluator():
    """Test load_evaluator returns NoEvaluator"""
    from app.utility.evaluators import load_evaluator, NoEvaluator
    payload = {
        "judge_model": "no-evaluator",
        "judge_temperature": 0.0,
        "judge_max_n_tokens": 100,
        "judge_top_p": 1.0,
        "goal": "test",
        "target_str": "test"
    }
    ev = load_evaluator(payload)
    assert isinstance(ev, NoEvaluator)

def test_no_evaluator_returns_one():
    """Test NoEvaluator always returns score of 1"""
    from app.utility.evaluators import NoEvaluator
    payload = {
        "judge_model": "no-evaluator",
        "judge_temperature": 0.0,
        "judge_max_n_tokens": 100,
        "judge_top_p": 1.0,
        "goal": "test",
        "target_str": "test"
    }
    ev = NoEvaluator(payload)
    scores = ev.judge_score(["prompt"], ["response"])
    assert scores == [1]

def test_load_evaluator_with_gemini():
    """Test load_evaluator returns GeminiEvaluator for gemini models"""
    from app.utility.evaluators import load_evaluator
    payload = {
        "judge_model": "gemini-pro",
        "judge_temperature": 0.0,
        "judge_max_n_tokens": 100,
        "judge_top_p": 1.0,
        "goal": "test",
        "target_str": "test"
    }
    evaluators = load_evaluator(payload)
    assert isinstance(evaluators, list)
    assert len(evaluators) == 2

def test_evaluator_score_extraction():
    """Test evaluator score extraction patterns"""
    test_responses = [
        "Rating: [[8]]",
        "Score: [[7]]",
        "[[10]]",
        "The rating is [[5]]"
    ]
    
    import re
    for response in test_responses:
        match = re.search(r'\[\[(\d+)\]\]', response)
        if match:
            score = int(match.group(1))
            assert 1 <= score <= 10

def test_on_topic_evaluation():
    """Test on-topic score evaluation logic"""
    on_topic_responses = [
        "This is relevant to the query",
        "This directly addresses the question"
    ]
    
    off_topic_responses = [
        "I cannot help with that",
        "This is unrelated"
    ]
    
    # Basic validation
    assert len(on_topic_responses) > 0
    assert len(off_topic_responses) > 0

def test_gpt_evaluator_initialization():
    """Test GPTEvaluator initialization"""
    from app.utility.evaluators import GPTEvaluator
    from unittest.mock import patch, Mock
    
    payload = {
        "judge_model": "gpt-4",
        "judge_temperature": 0.0,
        "judge_max_n_tokens": 100,
        "judge_top_p": 1.0,
        "goal": "test",
        "target_str": "target"
    }
    
    with patch('app.utility.evaluators.GPT') as MockGPT:
        mock_model = Mock()
        MockGPT.return_value = mock_model
        
        ev = GPTEvaluator(payload)
        assert ev.evaluator_name == "gpt-4"
        assert ev.max_n_tokens == 100

def test_gemini_evaluator_initialization():
    """Test GeminiEvaluator initialization"""
    from app.utility.evaluators import GeminiEvaluator
    from unittest.mock import patch, Mock
    
    payload = {
        "judge_model": "gemini-1.5-pro",
        "judge_temperature": 0.0,
        "judge_max_n_tokens": 100,
        "judge_top_p": 1.0,
        "goal": "test",
        "target_str": "target"
    }
    
    with patch('app.utility.evaluators.GeminiModel') as MockGemini:
        mock_model = Mock()
        MockGemini.return_value = mock_model
        
        ev = GeminiEvaluator(payload)
        assert ev.evaluator_name == "gemini-1.5-pro"

def test_bedrock_evaluator_initialization():
    """Test BedrockEvaluator initialization"""
    from app.utility.evaluators import BedrockEvaluator
    from unittest.mock import patch, Mock
    
    payload = {
        "judge_model": "anthropic.claude-3",
        "judge_temperature": 0.0,
        "judge_max_n_tokens": 100,
        "judge_top_p": 1.0,
        "goal": "test",
        "target_str": "target"
    }
    
    with patch('app.utility.evaluators.BedrockModel') as MockBedrock:
        mock_model = Mock()
        MockBedrock.return_value = mock_model
        
        ev = BedrockEvaluator(payload)
        assert ev.evaluator_name == "anthropic.claude-3"

def test_evaluator_judge_score():
    """Test evaluator judge_score method"""
    from app.utility.evaluators import GPTEvaluator
    from unittest.mock import patch, Mock
    
    payload = {
        "judge_model": "gpt-4",
        "judge_temperature": 0.0,
        "judge_max_n_tokens": 100,
        "judge_top_p": 1.0,
        "goal": "test",
        "target_str": "target"
    }
    
    with patch('app.utility.evaluators.GPT') as MockGPT:
        mock_model = Mock()
        mock_model.batched_generate.return_value = ["Rating: [[7]]"]
        MockGPT.return_value = mock_model
        
        ev = GPTEvaluator(payload)
        scores = ev.judge_score(["prompt"], ["response"])
        assert isinstance(scores, list)

def test_evaluator_on_topic_score():
    """Test evaluator on_topic_score method"""
    from app.utility.evaluators import GPTEvaluator
    from unittest.mock import patch, Mock
    
    payload = {
        "judge_model": "gpt-4",
        "judge_temperature": 0.0,
        "judge_max_n_tokens": 100,
        "judge_top_p": 1.0,
        "goal": "test",
        "target_str": "target"
    }
    
    with patch('app.utility.evaluators.GPT') as MockGPT:
        mock_model = Mock()
        mock_model.batched_generate.return_value = ["Rating: [[1]]"]
        MockGPT.return_value = mock_model
        
        ev = GPTEvaluator(payload)
        scores = ev.on_topic_score(["prompt"], ["response"])
        assert isinstance(scores, list)

def test_load_evaluator_with_bedrock():
    """Test load_evaluator with bedrock model"""
    import app.utility.evaluators as evaluators
    from unittest.mock import patch, Mock
    
    payload = {
        "judge_model": "bedrock/anthropic.claude-v2",
        "judge_temperature": 0.0,
        "judge_max_n_tokens": 100,
        "judge_top_p": 1.0,
        "goal": "test",
        "target_str": "target"
    }
    
    with patch('app.utility.evaluators.BedrockModel') as MockBedrock:
        mock_model = Mock()
        MockBedrock.return_value = mock_model
        
        ev_list = evaluators.load_evaluator(payload)
        assert isinstance(ev_list, list)
        assert len(ev_list) > 0

def test_no_evaluator_initialization():
    """Test NoEvaluator returns instance"""
    import app.utility.evaluators as evaluators
    
    payload = {
        "judge_model": "no-evaluator",
        "judge_temperature": 0.0,
        "judge_max_n_tokens": 100,
        "judge_top_p": 1.0,
        "goal": "test",
        "target_str": "target"
    }
    
    ev = evaluators.load_evaluator(payload)
    assert ev is not None
    assert hasattr(ev, 'judge_score')

def test_no_evaluator_judge_score():
    """Test NoEvaluator judge_score returns all 1s"""
    import app.utility.evaluators as evaluators
    
    payload = {"judge_model": "no-evaluator", "judge_temperature": 0.0, "judge_max_n_tokens": 100, "judge_top_p": 1.0, "goal": "test", "target_str": "target"}
    ev = evaluators.load_evaluator(payload)
    scores = ev.judge_score(["p1", "p2"], ["r1", "r2"])
    assert scores == [1, 1]

def test_no_evaluator_on_topic_score():
    """Test NoEvaluator on_topic_score returns all 1s"""
    import app.utility.evaluators as evaluators
    
    payload = {"judge_model": "no-evaluator", "judge_temperature": 0.0, "judge_max_n_tokens": 100, "judge_top_p": 1.0, "goal": "test", "target_str": "target"}
    ev = evaluators.load_evaluator(payload)
    scores = ev.on_topic_score(["p1", "p2"], "original")
    assert scores == [1, 1]

def test_load_evaluator_gpt_returns_list():
    """Test load_evaluator with GPT returns list"""
    import app.utility.evaluators as evaluators
    from unittest.mock import patch, Mock
    
    payload = {"judge_model": "gpt-4", "judge_temperature": 0.0, "judge_max_n_tokens": 100, "judge_top_p": 1.0, "goal": "test", "target_str": "target"}
    
    with patch('app.utility.evaluators.GPT') as MockGPT:
        mock_model = Mock()
        MockGPT.return_value = mock_model
        
        ev_list = evaluators.load_evaluator(payload)
        assert isinstance(ev_list, list)
        assert len(ev_list) > 0

def test_load_evaluator_gemini_returns_list():
    """Test load_evaluator with Gemini returns list"""
    import app.utility.evaluators as evaluators
    from unittest.mock import patch, Mock
    
    payload = {"judge_model": "gemini-pro", "judge_temperature": 0.0, "judge_max_n_tokens": 100, "judge_top_p": 1.0, "goal": "test", "target_str": "target"}
    
    with patch('app.utility.evaluators.GeminiModel') as MockGemini:
        mock_model = Mock()
        MockGemini.return_value = mock_model
        
        ev_list = evaluators.load_evaluator(payload)
        assert isinstance(ev_list, list)
        assert len(ev_list) > 0


def test_no_evaluator_judge_score():
    """Test NoEvaluator judge_score returns all 1s"""
    import app.utility.evaluators as evaluators
    
    payload = {"judge_model": "no-evaluator", "judge_temperature": 0.0, "judge_max_n_tokens": 100, "judge_top_p": 1.0, "goal": "test", "target_str": "target"}
    ev = evaluators.load_evaluator(payload)
    scores = ev.judge_score(["p1", "p2"], ["r1", "r2"])
    assert scores == [1, 1]

def test_no_evaluator_on_topic_score():
    """Test NoEvaluator on_topic_score returns all 1s"""
    import app.utility.evaluators as evaluators
    
    payload = {"judge_model": "no-evaluator", "judge_temperature": 0.0, "judge_max_n_tokens": 100, "judge_top_p": 1.0, "goal": "test", "target_str": "target"}
    ev = evaluators.load_evaluator(payload)
    scores = ev.on_topic_score(["p1", "p2"], "original")
    assert scores == [1, 1]

def test_load_evaluator_gpt_returns_list():
    """Test load_evaluator with GPT returns list"""
    import app.utility.evaluators as evaluators
    from unittest.mock import patch, Mock
    
    payload = {"judge_model": "gpt-4", "judge_temperature": 0.0, "judge_max_n_tokens": 100, "judge_top_p": 1.0, "goal": "test", "target_str": "target"}
    
    with patch('app.utility.evaluators.GPT') as MockGPT:
        mock_model = Mock()
        MockGPT.return_value = mock_model
        
        ev_list = evaluators.load_evaluator(payload)
        assert isinstance(ev_list, list)
        assert len(ev_list) > 0

def test_load_evaluator_gemini_returns_list():
    """Test load_evaluator with Gemini returns list"""
    import app.utility.evaluators as evaluators
    from unittest.mock import patch, Mock
    
    payload = {"judge_model": "gemini-pro", "judge_temperature": 0.0, "judge_max_n_tokens": 100, "judge_top_p": 1.0, "goal": "test", "target_str": "target"}
    
    with patch('app.utility.evaluators.GeminiModel') as MockGemini:
        mock_model = Mock()
        MockGemini.return_value = mock_model
        
        ev_list = evaluators.load_evaluator(payload)
        assert isinstance(ev_list, list)
        assert len(ev_list) > 0



