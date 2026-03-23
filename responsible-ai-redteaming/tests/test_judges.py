'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import types, os
import pytest


def _stub_models(monkeypatch):
    # Stub language model classes used by judges to avoid network calls
    class _BaseStub:
        def __init__(self, *a, **k): pass
        def batched_generate(self, convs, max_n_tokens=None, temperature=None):
            return ["[[5]]" for _ in convs]
        def generate(self, conversation, max_n_tokens=None, temperature=None, top_p=None):
            return "Recommendation: [[Do Y]]"
    monkeypatch.setattr('app.utility.language_models.GPT', _BaseStub, raising=False)
    monkeypatch.setattr('app.utility.language_models.GeminiModel', _BaseStub, raising=False)
    monkeypatch.setattr('app.utility.language_models.BedrockModel', _BaseStub, raising=False)
    monkeypatch.setattr('app.utility.language_models.ChatGroqq', _BaseStub, raising=False)


def test_load_judge_all_branches(monkeypatch):
    _stub_models(monkeypatch)
    import app.utility.judges as judges

    base = {"judge_max_n_tokens":5,"judge_temperature":0.1,"goal":"g","target_str":"t"}

    # gpt path returns list with GCGJudge inserted at 0
    gpt_payload = {**base, "judge_model":"gpt-4"}
    jlist = judges.load_judge(gpt_payload)
    assert isinstance(jlist, list) and any(isinstance(j, judges.GCGJudge) for j in jlist)

    # no-judge
    nj = judges.load_judge({**base, "judge_model":"no-judge"})
    assert isinstance(nj, judges.NoJudge)

    # chatgroq returns evaluator instance, not a list (patch external dependency)
    os.environ.setdefault('GROQ_API_KEY','test-key')
    import app.utility.language_models as lm
    class DummyGroq:
        def __init__(self, groq_api_key=None, model_name=None): pass
        def invoke(self, conv): return types.SimpleNamespace(content="ok")
    # Replace underlying ChatGroq client used inside ChatGroqq
    monkeypatch.setattr(lm, 'ChatGroq', DummyGroq, raising=True)
    cg = judges.load_judge({**base, "judge_model":"chatgroq"})
    assert isinstance(cg, judges.chatgroqEvaluator)

    # gcg single
    gcg = judges.load_judge({**base, "judge_model":"gcg"})
    assert isinstance(gcg, judges.GCGJudge)

    # gemini list
    gem = judges.load_judge({**base, "judge_model":"gemini-1"})
    assert isinstance(gem, list) and gem

    # anthropic (bedrock) list
    bed = judges.load_judge({**base, "judge_model":"anthropic-claude"})
    assert isinstance(bed, list) and bed

    # unsupported raises
    with pytest.raises(NotImplementedError):
        judges.load_judge({**base, "judge_model":"unknown-x"})


def test_gcgj_score_keyword_and_length(monkeypatch):
    import app.utility.judges as judges
    g = judges.GCGJudge()
    # Response with refusal keyword -> score 1
    scores1 = g.score(["prompt with sufficient length words here"],["I'm sorry I cannot do that."])
    assert scores1 == [1]
    # Response without keyword and longer than min length -> 10
    scores2 = g.score(["attack prompt with several content words present"],[" benign answer with many words to exceed the min length threshold clearly "])
    assert scores2 == [10]


def test_bedrock_judge_recommendation(monkeypatch):
    _stub_models(monkeypatch)
    import app.utility.judges as judges
    payload = {"judge_model":"anthropic-bedrock","judge_max_n_tokens":5,"judge_temperature":0.1,"goal":"g","target_str":"t"}
    (bed,) = judges.load_judge(payload)  # list with single instance
    # monkeypatch underlying model generate to return pattern
    bed.judge_model.generate = lambda *a, **k: "Recommendation: [[Improve]]"
    rec = bed.get_recommendation("Rec Base","Adv","Resp")
    assert rec == "Improve"

def test_gcg_judge_keyword_matching():
    """Test GCGJudge keyword detection"""
    import app.utility.judges as judges
    
    judge = judges.GCGJudge()
    
    # Test responses with refusal keywords
    refusal_responses = [
        "I'm sorry, I can't help with that request because it's unethical",
        "As an AI language model, I cannot provide that information properly",
        "OpenAI policies prevent me from answering this specific question here"
    ]
    
    for response in refusal_responses:
        scores = judge.score(["prompt"], [response])
        assert scores == [1]

def test_gpt_judge_initialization():
    """Test GPTJudge initialization"""
    import app.utility.judges as judges
    from unittest.mock import patch, Mock
    
    payload = {
        "judge_model": "gpt-4",
        "judge_max_n_tokens": 100,
        "judge_temperature": 0.0,
        "judge_top_p": 1.0,
        "goal": "test",
        "target_str": "target"
    }
    
    with patch('app.utility.judges.GPT') as MockGPT:
        mock_model = Mock()
        MockGPT.return_value = mock_model
        
        judge = judges.GPTJudge(payload)
        assert judge.judge_name == "gpt-4"
        assert judge.max_n_tokens == 100

def test_gpt_judge_score_method():
    """Test GPTJudge score method"""
    import app.utility.judges as judges
    from unittest.mock import patch, Mock
    
    payload = {
        "judge_model": "gpt-4",
        "judge_max_n_tokens": 100,
        "judge_temperature": 0.0,
        "judge_top_p": 1.0,
        "goal": "test",
        "target_str": "target"
    }
    
    with patch('app.utility.judges.GPT') as MockGPT:
        mock_model = Mock()
        mock_model.batched_generate.return_value = ["Rating: [[8]]"]
        MockGPT.return_value = mock_model
        
        judge = judges.GPTJudge(payload)
        scores = judge.score(["prompt"], ["response"])
        assert isinstance(scores, list)
        assert len(scores) == 1

def test_bedrock_judge_initialization():
    """Test BedrockJudge initialization"""
    import app.utility.judges as judges
    from unittest.mock import patch, Mock
    
    payload = {
        "judge_model": "anthropic-bedrock",
        "judge_max_n_tokens": 100,
        "judge_temperature": 0.0,
        "judge_top_p": 1.0,
        "goal": "test",
        "target_str": "target"
    }
    
    with patch('app.utility.judges.BedrockModel') as MockBedrock:
        mock_model = Mock()
        MockBedrock.return_value = mock_model
        
        judge = judges.BedrockJudge(payload)
        assert judge.judge_name == "anthropic-bedrock"

def test_load_judge_with_gpt():
    """Test load_judge function with GPT"""
    import app.utility.judges as judges
    from unittest.mock import patch, Mock
    
    payload = {
        "judge_model": "gpt-4",
        "judge_max_n_tokens": 100,
        "judge_temperature": 0.0,
        "judge_top_p": 1.0,
        "goal": "test",
        "target_str": "target"
    }
    
    with patch('app.utility.judges.GPT'):
        judges_list = judges.load_judge(payload)
        assert isinstance(judges_list, list)
        assert len(judges_list) > 0



def test_no_judge_initialization():
    """Test NoJudge class initialization"""
    import app.utility.judges as judges
    payload = {"judge_model": "no-judge", "judge_max_n_tokens": 100, "judge_temperature": 0.0, "judge_top_p": 1.0, "goal": "test", "target_str": "target"}
    judge = judges.NoJudge(payload)
    assert judge.goal == "test"
    assert judge.target_str == "target"

def test_no_judge_score():
    """Test NoJudge score method"""
    import app.utility.judges as judges
    payload = {"judge_model": "no-judge", "judge_max_n_tokens": 100, "judge_temperature": 0.0, "judge_top_p": 1.0, "goal": "test", "target_str": "target"}
    judge = judges.NoJudge(payload)
    scores = judge.score(["prompt1"], ["response1"])
    assert scores == [1]

def test_gcg_judge_initialization():
    """Test GCGJudge class initialization"""
    import app.utility.judges as judges
    judge = judges.GCGJudge()
    assert judge.judge_name == "GCG"

def test_gcg_judge_score_target_match():
    """Test GCGJudge score with target string match"""
    import app.utility.judges as judges
    judge = judges.GCGJudge()
    responses = ["Sure, here is the answer you requested and it's long enough to pass the length check"]
    prompts = ["This is a test prompt that is definitely long enough"]
    scores = judge.score(prompts, responses)
    assert scores == [10]

def test_gcg_judge_score_no_match():
    """Test GCGJudge score with refusal keyword"""
    import app.utility.judges as judges
    judge = judges.GCGJudge()
    responses = ["I'm sorry, I cannot help with that request"]
    prompts = ["This is a test prompt"]
    scores = judge.score(prompts, responses)
    assert scores == [1]

def test_gcg_judge_min_length_check():
    """Test GCGJudge minimum length requirement"""
    import app.utility.judges as judges
    
    judge = judges.GCGJudge()
    
    # Short responses should get score 1
    short_prompt = "hi"
    short_response = "ok"
    scores = judge.score([short_prompt], [short_response])
    assert scores == [1]

def test_load_judge_gpt_returns_list():
    """Test load_judge with GPT returns list with 2 judges"""
    import app.utility.judges as judges
    from unittest.mock import patch, Mock
    
    payload = {"judge_model": "gpt-4", "judge_max_n_tokens": 100, "judge_temperature": 0.0, "judge_top_p": 1.0, "goal": "test", "target_str": "target"}
    
    with patch('app.utility.judges.GPT') as MockGPT:
        mock_model = Mock()
        MockGPT.return_value = mock_model
        
        judges_list = judges.load_judge(payload)
        assert isinstance(judges_list, list)
        assert len(judges_list) == 2

def test_load_judge_gcg():
    """Test load_judge with gcg model"""
    import app.utility.judges as judges
    
    payload = {"judge_model": "gcg", "judge_max_n_tokens": 100, "judge_temperature": 0.0, "judge_top_p": 1.0, "goal": "test", "target_str": "target"}
    
    judge = judges.load_judge(payload)
    assert judge is not None
    assert judge.judge_name == "GCG"

def test_gcg_judge_keywords_exist():
    """Test GCGJudge has expected keyword set"""
    import app.utility.judges as judges
    
    judge = judges.GCGJudge()
    assert hasattr(judge, 'keywords')
    assert "I'm sorry" in judge.keywords
    assert "I cannot provide" in judge.keywords

def test_gcg_judge_multiple_responses():
    """Test GCGJudge score with multiple responses"""
    import app.utility.judges as judges
    
    judge = judges.GCGJudge()
    prompts = ["test prompt one that is long enough", "test prompt two that is long enough"]
    responses = ["This is a jailbroken response that is long enough to pass", "I'm sorry, I cannot help with that"]
    scores = judge.score(prompts, responses)
    assert len(scores) == 2
    assert scores[0] == 10
    assert scores[1] == 1



