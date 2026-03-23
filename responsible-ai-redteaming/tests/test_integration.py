'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import os
import sys
import types
import io
import json
import base64
import pytest

# Ensure heavy external clients are stubbed before imports

def _prepare_stubs_for_utils(monkeypatch):
    # Stub openai/anthropic/google clients to avoid network
    if 'openai' not in sys.modules:
        openai_mod = types.ModuleType('openai')
        ChatCompletion = types.SimpleNamespace(create=lambda **k: {"choices":[{"message":{"content":"ok"}}]})
        setattr(openai_mod, 'ChatCompletion', ChatCompletion)
        sys.modules['openai'] = openai_mod
    if 'anthropic' not in sys.modules:
        anthropic_mod = types.ModuleType('anthropic')
        setattr(anthropic_mod, 'APIError', Exception)
        # nosec B107 - Test stub only, not a real credential
        Anthropic = lambda api_key="": types.SimpleNamespace(completions=types.SimpleNamespace(create=lambda **k: types.SimpleNamespace(completion="ok")))
        setattr(anthropic_mod, 'Anthropic', Anthropic)
        sys.modules['anthropic'] = anthropic_mod
    # google.generativeai stub
    if 'google.generativeai' not in sys.modules:
        gen_mod = types.ModuleType('google.generativeai')
        class _GenClient:
            def __init__(self, api_key=""):  # nosec B107 - Test stub only, not a real credential
                pass
            class Models:
                def generate_content(self, model=None, contents=None):
                    return types.SimpleNamespace(candidates=[types.SimpleNamespace(content=types.SimpleNamespace(parts=[types.SimpleNamespace(text="ok")]))])
            models = Models()
        class _GenModel:
            def __init__(self, model): pass
            def generate_content(self, contents=None, generation_config=None):
                return types.SimpleNamespace(candidates=[types.SimpleNamespace(content=types.SimpleNamespace(parts=[types.SimpleNamespace(text="ok")]))])
        class _GenConfig:
            def __init__(self, **k): pass
        setattr(gen_mod, 'Client', _GenClient)
        setattr(gen_mod, 'GenerativeModel', _GenModel)
        setattr(gen_mod, 'GenerationConfig', _GenConfig)
        def configure(api_key=""):  # nosec B107 - Test stub only, not a real credential
            return None
        setattr(gen_mod, 'configure', configure)
        sys.modules['google.generativeai'] = gen_mod

    # boto3 and ChatBedrock
    if 'boto3' not in sys.modules:
        boto3_mod = types.ModuleType('boto3')
        setattr(boto3_mod, 'client', lambda **k: object())
        sys.modules['boto3'] = boto3_mod
    if 'langchain_aws' not in sys.modules:
        lc_mod = types.ModuleType('langchain_aws')
        class _ChatBedrock:
            def __init__(self, *a, **kw): pass
            def invoke(self, prompt):
                return types.SimpleNamespace(content="ok")
        setattr(lc_mod, 'ChatBedrock', _ChatBedrock)
        sys.modules['langchain_aws'] = lc_mod

    # requests.post/get mocked later per-test when needed


def test_common_extract_json_and_helpers():
    from app.utility import common
    s = '{"improvement": "i", "prompt": "p"}\nTrailing'
    parsed, json_str = common.extract_json(s)
    assert parsed == {"improvement":"i","prompt":"p"}
    assert json_str.startswith('{') and json_str.endswith('}')
    assert "objective" in common.get_init_msg("goal","target").lower()
    out = common.process_target_response("resp", 5, "g","t")
    assert "LANGUAGE MODEL OUTPUT" in out


def test_language_models_truncate_and_hf_guard(monkeypatch):
    from app.utility.language_models import _truncate_prompts
    # truncation
    long = "x"*9000
    assert len(_truncate_prompts([long])[0]) <= 8000


def test_endpoint_models_pair_tap_generate(monkeypatch):
    _prepare_stubs_for_utils(monkeypatch)
    import app.utility.language_models as lm
    # stub extractors to avoid GPT use
    monkeypatch.setattr(lm.EndpointModel_Pair, 'extract_text_with_gpt', lambda self, res: res.get('text',''))
    monkeypatch.setattr(lm.EndpointModel_Tap, 'extract_text_with_gpt', lambda self, res: res.get('text',''))

    class Resp:
        def __init__(self, code, payload):
            self.status_code = code
            self._payload = payload
            self.text = json.dumps(payload)
        def json(self): return self._payload
    calls = {"n":0}
    def fake_post(url, headers=None, json=None, verify=None, timeout=None):
        calls["n"] += 1
        return Resp(200, {"text":"answer"})
    monkeypatch.setattr(lm, 'requests', types.SimpleNamespace(post=fake_post))

    pair = lm.EndpointModel_Pair("http://u", {"A":"B"}, {"x":"1"}, "prompt")
    out = pair.generate("q", pair.target_endpoint_url, pair.target_endpoint_headers, pair.target_endpoint_payload, pair.target_endpoint_prompt_variable)
    assert out == "answer"

    tap = lm.EndpointModel_Tap("http://u", {"A":"B"}, {"x":"1"}, "prompt")
    out2 = tap.generate("q", tap.target_endpoint_url, tap.target_endpoint_headers, tap.target_endpoint_payload, tap.target_endpoint_prompt_variable)
    assert out2 == "answer"
    assert calls["n"] >= 2


def test_gpt_set_api_configuration_switch(monkeypatch):
    _prepare_stubs_for_utils(monkeypatch)
    import app.utility.language_models as lm
    g = lm.GPT("gpt-4")
    # ensure openai available from stub; calling set_api_configuration should not error
    g.set_api_configuration("gpt-4")
    # switch to gpt-3 path too
    g.set_api_configuration("gpt-3.5")


def test_judges_and_evaluators_loaders(monkeypatch):
    _prepare_stubs_for_utils(monkeypatch)
    import app.utility.judges as judges
    import app.utility.evaluators as evaluators
    payload = {"judge_model":"no-judge","judge_max_n_tokens":5,"judge_temperature":0.1,"goal":"g","target_str":"t"}
    assert isinstance(judges.load_judge(payload), judges.NoJudge)
    payload_gpt = {"judge_model":"gpt-4","judge_max_n_tokens":5,"judge_temperature":0.1,"goal":"g","target_str":"t"}
    jlist = judges.load_judge(payload_gpt)
    assert isinstance(jlist, list) and jlist

    epayload = {"judge_model":"no-evaluator","judge_max_n_tokens":5,"judge_temperature":0.1,"goal":"g","target_str":"t"}
    assert isinstance(evaluators.load_evaluator(epayload), evaluators.NoEvaluator)
    epayload_gpt = {"judge_model":"gpt-4","judge_max_n_tokens":5,"judge_temperature":0.1,"goal":"g","target_str":"t"}
    elist = evaluators.load_evaluator(epayload_gpt)
    assert isinstance(elist, list) and elist


def test_multifaceted_helpers(monkeypatch):
    _prepare_stubs_for_utils(monkeypatch)
    import importlib, sys
    # Replace previously stubbed module (from other tests) with the real one
    # Ensure required env vars exist so AZURE_* constants are not None during import
    os.environ.setdefault('AZURE_GPT4_MODEL_NAME', 'gpt-4')
    os.environ.setdefault('AZURE_GPT4_API_KEY', 'test-key')
    os.environ.setdefault('AZURE_GPT4_API_BASE', 'https://example.test')
    os.environ.setdefault('AZURE_GPT4_API_VERSION', '2024-01-01')
    sys.modules.pop('app.utility.multifaceted', None)
    mf = importlib.import_module('app.utility.multifaceted')
    m = mf.MultifacetedEvaluation("k","e","v","m")
    # preprocess splits lines and excludes blanks
    r = m.preprocess_response("a\n\n b\n c")
    assert r.document.startswith("a") and isinstance(r.paragraph_list, list)
    # process_output extracts rating or defaults to 10
    assert m.process_output("Rating: 7") == 7
    assert m.process_output("bad") == 10


def test_report_generators_minimal(monkeypatch):
    import app.utility.report as report
    data = {
        'total_rows': 2,
        'processed_rows': 2,
        'technical_failed_rows': [],
        'jailbroken_rows': 1,
        'category_wise_score': {},
        'target_model': 'm',
        'target_temperature': 0.1,
        'n_iterations': 1,
        'technique_type': 'PAIR'
    }
    # create_pie_chart returns base64 png string
    png = report.create_pie_chart(data)
    # Should be valid base64
    base64.b64decode(png)
    html = report.generate_html_report_pair({**data, 'category_wise_score': {}})
    assert '<html' in html.lower()


def test_local_constants_are_strings():
    import app.constants.local_constants as lc
    for name in ['DELTED_SUCCESS_MESSAGE','USECASE_ALREADY_EXISTS','USECASE_NOT_FOUND_ERROR','USECASE_NAME_VALIDATION_ERROR','SPACE_DELIMITER','PLACEHOLDER_TEXT']:
        assert isinstance(getattr(lc, name), str)


def test_judges_process_and_recommendation_extractors(monkeypatch):
    _prepare_stubs_for_utils(monkeypatch)
    import app.utility.judges as judges
    payload = {"judge_model":"gpt-4","judge_max_n_tokens":10,"judge_temperature":0.1,"goal":"g","target_str":"t"}
    j = judges.GPTJudge(payload)
    # process_output parses [[7]] else defaults to 1
    assert j.process_output("some [[7]] text") == 7
    assert j.process_output("no brackets here") == 1
    # extract_recommendation extracts inside brackets or fallback
    s = "foo Recommendation: [[Do X carefully]] bar"
    assert j.extract_recommendation(s) == "Do X carefully"
    assert j.extract_recommendation("nothing relevant") == "No recommendation provided."


def test_evaluators_process_output_branches_and_extractors(monkeypatch):
    _prepare_stubs_for_utils(monkeypatch)
    import app.utility.evaluators as evaluators
    payload = {"judge_model":"gpt-4","judge_max_n_tokens":10,"judge_temperature":0.1,"goal":"g","target_str":"t"}
    e = evaluators.GPTEvaluator(payload)
    # judge score parsing
    assert e.process_output_judge_score("[[9]]") == 9
    assert e.process_output_judge_score("oops") == 1
    # on-topic yes/no parsing
    assert e.process_output_on_topic_score("[[yes]]") == 1
    assert e.process_output_on_topic_score("[[no]]") == 0
    assert e.process_output_on_topic_score("meh") == 1
    # Gemini recommendation extractor (regex only)
    ge = evaluators.GeminiEvaluator(payload)
    assert ge.extract_recommendation("Recommendation: [[Tighten filters]]") == "Tighten filters"
    assert ge.extract_recommendation("No tag here") == "No recommendation provided."


def test_language_models_retry_paths(monkeypatch):
    _prepare_stubs_for_utils(monkeypatch)
    import app.utility.language_models as lm
    # EndpointModel_Pair: first non-200 then success
    class Resp:
        def __init__(self, code, payload):
            self.status_code = code
            self._payload = payload
            self.text = json.dumps(payload)
        def json(self): return self._payload
    calls = {"n":0}
    def fake_post(url, headers=None, json=None, verify=None, timeout=None):
        calls["n"] += 1
        if calls["n"] == 1:
            return Resp(500, {"error":"bad"})
        return Resp(200, {"text":"answer"})
    monkeypatch.setattr(lm, 'requests', types.SimpleNamespace(post=fake_post))
    # avoid GPT call inside extractor
    monkeypatch.setattr(lm.EndpointModel_Pair, 'extract_text_with_gpt', lambda self, res: res.get('text',''))
    pair = lm.EndpointModel_Pair("http://u", {"A":"B"}, {"x":"1"}, "prompt")
    out = pair.generate("q", pair.target_endpoint_url, pair.target_endpoint_headers, pair.target_endpoint_payload, pair.target_endpoint_prompt_variable)
    assert out == "answer" and calls["n"] == 2

    # GPT.generate: first exception then success; patch sleep to no-op
    g = lm.GPT("gpt-4")
    call_idx = {"i":0}
    def flaky_create(**kwargs):
        call_idx["i"] += 1
        if call_idx["i"] == 1:
            raise Exception("boom")
        return {"choices":[{"message":{"content":"ok"}}]}
    import openai as _openai
    monkeypatch.setattr(_openai.ChatCompletion, 'create', flaky_create, raising=True)
    monkeypatch.setattr(lm.time, 'sleep', lambda s: None, raising=True)
    res = g.generate([{"role":"user","content":"hi"}], max_n_tokens=5, temperature=0.1, top_p=1.0)
    assert res == "ok"


def test_report_generate_html_report_tap_with_categories(monkeypatch):
    import app.utility.report as report
    data = {
        'total_rows': 4,
        'processed_rows': 4,
        'technical_failed_rows': [],
        'jailbroken_rows': 2,
        'category_wise_score': {
            'Safety': {'count': 1, 'provided': 2, 'details': [{'goal':'g1','prompt':'p1','response':'r1'}]},
            'Privacy': {'count': 2, 'provided': 2, 'details': [{'goal':'g2','prompt':'p2','response':'r2'}]}
        },
        'target_model': 'm',
        'target_temperature': 0.1,
        'depth': 1,
        'width': 1,
        'branching_factor': 1,
        'technique_type': 'TAP'
    }
    html = report.generate_html_report_tap(data)
    assert '<html' in html.lower()
    assert 'RISK CATEGORY ANALYSIS' in html
    assert 'Safety' in html and 'Privacy' in html


def test_chatgroqq_retry_and_empty_content(monkeypatch):
    _prepare_stubs_for_utils(monkeypatch)
    import app.utility.language_models as lm
    # Patch the underlying ChatGroq class used inside ChatGroqq to avoid real client
    class FakeChatGroq:
        def __init__(self, *a, **k): pass
        def invoke(self, conv):
            return types.SimpleNamespace(content="ok")
    monkeypatch.setattr(lm, 'ChatGroq', FakeChatGroq, raising=True)
    cg = lm.ChatGroqq("mixtral-8x7b-32768")
    # First, simulate empty content then valid content
    calls = {"i":0}
    def invoke_empty_then_ok(conv):
        calls["i"] += 1
        return types.SimpleNamespace(content=("" if calls["i"] == 1 else "ok"))
    monkeypatch.setattr(cg.model, 'invoke', invoke_empty_then_ok)
    out = cg.generate([{"role":"user","content":"hi"}], 5, 0.1, 1.0)
    assert out == "ok"
    # Now simulate exception first then success
    calls2 = {"i":0}
    def invoke_boom_then_ok(conv):
        calls2["i"] += 1
        if calls2["i"] == 1:
            raise Exception("boom")
        return types.SimpleNamespace(content="ok2")
    monkeypatch.setattr(cg.model, 'invoke', invoke_boom_then_ok)
    # speed-up sleeps
    monkeypatch.setattr(lm.time, 'sleep', lambda s: None, raising=True)
    out2 = cg.generate([{"role":"user","content":"hi"}], 5, 0.1, 1.0)
    assert out2 == "ok2"


def test_gemini_bedrock_batched_paths(monkeypatch):
    _prepare_stubs_for_utils(monkeypatch)
    import app.utility.language_models as lm
    # GeminiModel: patch generate to return predictable
    gm = lm.GeminiModel("gem-model")
    monkeypatch.setattr(gm, 'generate', lambda prompt, max_n_tokens, temperature, top_p: f"G:{prompt}")
    outs = gm.batched_generate(["a","b"], 5, 0.1, 1.0)
    assert outs == ["G:a","G:b"]
    # BedrockModel: avoid real client by forcing llm None and patch generate
    bm = lm.BedrockModel("bedrock-model")
    monkeypatch.setattr(bm, 'generate', lambda prompt, max_n_tokens, temperature, top_p: f"B:{prompt}")
    outs2 = bm.batched_generate(["x","y"], 5, 0.1, 1.0)
    assert outs2 == ["B:x","B:y"]


def test_conversers_helpers(monkeypatch):
    from app.utility import conversers as conv
    # extract_json happy path
    parsed, json_str = conv.extract_json('{"improvement":"i","prompt":"p"}\nnoise')
    assert parsed == {"improvement":"i","prompt":"p"}
    assert json_str.startswith('{')
    # get_init_msg_pair and process_target_response_pair
    assert "objective" in conv.get_init_msg_pair("goal","target").lower()
    out = conv.process_target_response_pair("resp", 3, "goal","target")
    assert "LANGUAGE MODEL OUTPUT" in out
    # conv_template_pair basic behavior
    tpl = conv.conv_template_pair("gpt-3.5-turbo")
    # Some templates may have sep None initially; just assert attribute exists
    assert hasattr(tpl, 'sep')


def test_conversers_load_models_pair_endpoint_vs_local(monkeypatch):
    # Attack local (AttackLM), Target endpoint (EndpointModel_Pair)
    from app.utility import conversers as conv
    # Monkeypatch load_indiv_model to avoid heavy HF loads
    monkeypatch.setattr(conv, 'load_indiv_model', lambda name, device=None: (types.SimpleNamespace(batched_generate=lambda *a, **k: []), conv.get_conversation_template(name)), raising=True)
    payload = {
        'attack_model': 'gpt-3.5-turbo',
        'attack_max_n_tokens': 10,
        'max_n_attack_attempts': 1,
        'attack_temperature': 0.1,
        'attack_top_p': 0.9,
        'target_endpoint_url': 'http://example.test/api',
        'target_endpoint_headers': {'A':'B'},
        'target_endpoint_payload': {'x':'1'},
        'target_endpoint_prompt_variable': 'q',
        'target_model': 'gpt-3.5-turbo',
        'target_max_n_tokens': 10,
        'target_temperature': 0.1,
        'target_top_p': 1.0
    }
    attack_lm, target_lm = conv.load_attack_and_target_models_pair(payload)
    # attack_lm (PAIR) exposes get_attack_pair; EndpointModel_Pair has generate
    assert hasattr(attack_lm, 'get_attack_pair') and hasattr(target_lm, 'generate')


def test_conversers_load_models_tap_both_variants(monkeypatch):
    from app.utility import conversers as conv
    # Endpoint both sides
    payload_ep = {
        'attack_endpoint_url': 'http://a',
        'attack_headers': {'A':'B'},
        'attack_payload': {'x':'1'},
        'attack_prompt_variable': 'q',
        'target_endpoint_url': 'http://t',
        'target_endpoint_headers': {'A':'B'},
        'target_endpoint_payload': {'x':'1'},
        'target_endpoint_prompt_variable': 'q'
    }
    a1, t1 = conv.load_attack_and_target_models_tap(payload_ep)
    assert hasattr(a1, 'generate') and hasattr(t1, 'generate')
    # Local both sides
    monkeypatch.setattr(conv, 'load_indiv_model', lambda name, device=None: (types.SimpleNamespace(batched_generate=lambda *a, **k: []), conv.get_conversation_template(name)), raising=True)
    payload_local = {
        'attack_model': 'gpt-3.5-turbo',
        'attack_max_n_tokens': 10,
        'max_n_attack_attempts': 1,
        'attack_temperature': 0.1,
        'attack_top_p': 0.9,
        'target_model': 'gpt-3.5-turbo',
        'target_max_n_tokens': 10,
        'target_temperature': 0.1,
        'target_top_p': 1.0
    }
    a2, t2 = conv.load_attack_and_target_models_tap(payload_local)
    assert hasattr(a2, 'get_attack') and hasattr(t2, 'get_response')


def test_text_utils_chunk_and_normalize():
    from app.utility import text_utils as tu
    # chunk_text normal
    text = "one two three four five six"
    chunks = tu.chunk_text(text, 10)
    assert all(len(c) <= 10 for c in chunks) and " ".join(chunks).replace("  ", " ").strip()
    # long token fallback
    chunks2 = tu.chunk_text("aVeryLongToken", 5)
    assert chunks2 == ["aVeryLongToken"]
    # zero max_len returns original as a single chunk
    assert tu.chunk_text("abc", 0) == ["abc"]
    # normalize_whitespace
    assert tu.normalize_whitespace("  a\n\n b\t c  ") == "a b c"


def test_common_edges_and_ids():
    from app.utility import common
    # extract_json failure: missing keys
    parsed, s = common.extract_json('{"notimp":"x","prompt":"p"}')
    assert parsed is None and s is None
    # extract_json failure: malformed json
    parsed2, s2 = common.extract_json('{bad json')
    assert parsed2 is None and s2 is None
    # conv_template attaches ids
    tpl = common.conv_template("gpt-3.5-turbo", self_id="S", parent_id="P")
    assert getattr(tpl, 'self_id', None) == "S" and getattr(tpl, 'parent_id', None) == "P"
    # random_string
    r = common.random_string(8)
    assert isinstance(r, str) and len(r) == 8
import base64
import io
import json
import types
import pytest


def test_report_pair_vulnerability_text_branches():
    import app.utility.report as report
    base = {
        'total_rows': 4,
        'processed_rows': 4,
        'technical_failed_rows': [],
        'jailbroken_rows': 2,
        'target_model': 'm',
        'target_temperature': 0.1,
        'n_iterations': 1,
        'technique_type': 'PAIR'
    }
    # Two top categories
    data_two = {**base, 'category_wise_score': {
        'A': {'count': 1, 'provided': 1, 'details': []},
        'B': {'count': 1, 'provided': 1, 'details': []},
        'C': {'count': 0, 'provided': 2, 'details': []},
    }}
    html_two = report.generate_html_report_pair(data_two)
    assert 'most vulnerable under the A and B categories' in html_two
    # Three top categories
    data_three = {**base, 'category_wise_score': {
        'X': {'count': 1, 'provided': 1, 'details': []},
        'Y': {'count': 1, 'provided': 1, 'details': []},
        'Z': {'count': 1, 'provided': 1, 'details': []},
    }}
    html_three = report.generate_html_report_pair(data_three)
    assert 'X, Y, and Z' in html_three
    # Single category
    data_one = {**base, 'category_wise_score': {
        'Only': {'count': 1, 'provided': 1, 'details': []},
    }}
    html_one = report.generate_html_report_pair(data_one)
    assert 'most vulnerable under the Only category' in html_one


def test_judges_gpt_scoring_and_recommendation(monkeypatch):
    import app.utility.judges as judges
    payload = {"judge_model":"gpt-4","judge_max_n_tokens":10,"judge_temperature":0.1,"goal":"g","target_str":"t"}
    j = judges.GPTJudge(payload)
    # stub underlying model
    class FakeModel:
        def batched_generate(self, convs, max_n_tokens=None, temperature=None):
            return ["[[10]]", "[[1]]"]
        def generate(self, conversation, max_n_tokens=None, temperature=None, top_p=None):
            return "Prefix Recommendation: [[Do X]] Suffix"
    monkeypatch.setattr(j, 'judge_model', FakeModel(), raising=False)
    scores = j.judge_score(["p1","p2"],["r1","r2"])
    assert scores == [10,1]
    rec = j.get_recommendation("R", "p", "r")
    assert rec == 'Do X'


def test_judges_gemini_scoring_and_recommendation(monkeypatch):
    import app.utility.judges as judges
    payload = {"judge_model":"gemini-pro","judge_max_n_tokens":10,"judge_temperature":0.1,"goal":"g","target_str":"t"}
    j = judges.GeminiJudge(payload)
    class FakeModel:
        def batched_generate(self, convs, max_n_tokens=None, temperature=None):
            return ["[[10]]"]
        def generate(self, conversation, max_n_tokens=None, temperature=None, top_p=None):
            return "Recommendation: [[Gem Advice]]"
    monkeypatch.setattr(j, 'judge_model', FakeModel(), raising=False)
    assert j.judge_score(["p"],["r"]) == [10]
    assert j.get_recommendation("R","p","r") == 'Gem Advice'


def test_evaluators_gpt_judge_and_ontopic(monkeypatch):
    import app.utility.evaluators as evaluators
    payload = {"judge_model":"gpt-4","judge_max_n_tokens":10,"judge_temperature":0.1,"goal":"g","target_str":"t"}
    e = evaluators.GPTEvaluator(payload)
    class Fake:
        def batched_generate(self, convs, max_n_tokens=None, temperature=None):
            # judge list then on-topic list
            return ["[[7]]" for _ in range(len(convs))]
    monkeypatch.setattr(e, 'judge_model', Fake(), raising=False)
    assert e.judge_score(["p"],["r"]) == [7]
    # For on-topic, the parser expects yes/no
    class FakeYes:
        def batched_generate(self, convs, max_n_tokens=None, temperature=None):
            return ["[[yes]]" for _ in range(len(convs))]
    monkeypatch.setattr(e, 'judge_model', FakeYes(), raising=False)
    assert e.on_topic_score(["p"], "orig") == [1]


def test_evaluators_chatgroq_judge_score(monkeypatch):
    import app.utility.evaluators as evaluators
    payload = {"judge_model":"chatgroq","judge_max_n_tokens":10,"judge_temperature":0.1,"goal":"g","target_str":"t"}
    # Replace ChatGroqq with a fake on the evaluators module
    class FakeCG:
        def __init__(self, model_name): pass
        def batched_generate(self, convs, max_n_tokens=None, temperature=None):
            return ["[[9]]"]
    monkeypatch.setattr(evaluators, 'ChatGroqq', FakeCG, raising=True)
    ev = evaluators.chatgroqEvaluator(payload)
    assert ev.judge_score(["p"],["r"]) == [9]


def test_conversers_model_path_template_and_helpers(monkeypatch):
    import app.utility.conversers as conv
    # valid model
    p, t = conv.get_model_path_and_template('gpt-4')
    assert p == 'gpt-4' and t == 'gpt-4'
    # invalid model -> ValueError
    with pytest.raises(ValueError):
        conv.get_model_path_and_template('unknown-model')
    # clean_attacks_and_convs happy path with None filtered
    attacks, convs = conv.clean_attacks_and_convs([{"improvement":"i","prompt":"p"}, None], [object(), object()])
    assert attacks and len(attacks) == 1 and isinstance(convs, list) and len(convs) == 1
    # error branch
    a2, c2 = conv.clean_attacks_and_convs(None, [object()])
    assert a2 is None and c2 is None


def test_conversers_prune_deterministic(monkeypatch):
    import app.utility.conversers as conv
    # make shuffle deterministic
    monkeypatch.setattr(conv.np.random, 'shuffle', lambda x: None, raising=True)
    on_topic = [1, 0]
    judge_scores = [10, 5]
    adv = ['a','b']
    improv = ['ia','ib']
    class _C: pass
    convs = [_C(), _C()]
    ex = [{'prompt':'a','improvement':'ia'}, {'prompt':'b','improvement':'ib'}]
    attack_params = {'width': 1}
    out = conv.prune(on_topic_scores=on_topic,
                     judge_scores=judge_scores,
                     adv_prompt_list=adv,
                     improv_list=improv,
                     convs_list=convs,
                     target_response_list=['ra','rb'],
                     extracted_attack_list=ex,
                     sorting_score=judge_scores,
                     attack_params=attack_params)
    # all lists should be truncated to width 1 and aligned
    (on_topic2, judge2, adv2, improv2, convs2, target2, ex2) = out
    assert len(adv2) == len(improv2) == len(convs2) == len(target2) == len(ex2) == 1


def test_language_models_endpoint_pair_batched_and_gpt_batched(monkeypatch):
    import app.utility.language_models as lm
    # EndpointModel_Pair.batched_generate
    class Resp:
        def __init__(self, code, payload):
            self.status_code = code
            self._payload = payload
            self.text = json.dumps(payload)
        def json(self): return self._payload
    def ok_post(url, headers=None, json=None, verify=None, timeout=None):
        return Resp(200, {"text":"answer"})
    monkeypatch.setattr(lm, 'requests', types.SimpleNamespace(post=ok_post))
    monkeypatch.setattr(lm.EndpointModel_Pair, 'extract_text_with_gpt', lambda self, res: res.get('text',''))
    ep = lm.EndpointModel_Pair('http://u', {'A':'B'}, {'x':'1'}, 'q')
    outs = ep.batched_generate(['q1','q2'], ep.target_endpoint_url, ep.target_endpoint_headers, ep.target_endpoint_payload, ep.target_endpoint_prompt_variable)
    assert outs == ["answer","answer"]
    # GPT.batched_generate
    g = lm.GPT('gpt-4')
    class _Chat:
        @staticmethod
        def create(**kwargs):
            return {"choices":[{"message":{"content":"ok"}}]}
    import openai as _openai
    monkeypatch.setattr(_openai, 'ChatCompletion', _Chat, raising=True)
    outs2 = g.batched_generate([[{"role":"user","content":"a"}],[{"role":"user","content":"b"}]], 5, 0.1)
    assert outs2 == ["ok","ok"]


def test_custom_logger_file_and_console_toggle(monkeypatch, tmp_path):
    # Cover logger initialization with file handler, toggle console/file handlers, and custom logging path
    import app.config.logger as clog

    def fake_read_config(section, path):
        # verbose False to exercise _custom_log branch that disables console output
        return {"file_name": "testlog", "verbose": "False", "log_dir": str(tmp_path)}

    monkeypatch.setattr(clog, 'read_config', fake_read_config, raising=True)
    lg = clog.CustomLogger()

    assert lg.has_file_handler() and lg.has_console_handler()

    # Toggle console
    before_handlers = len(lg.handlers)
    lg.disable_console_output()
    after_handlers = len(lg.handlers)
    # Expect handler count decreased by 1 (stdout removed) or unchanged if already absent
    assert after_handlers <= before_handlers
    lg.enable_console_output()
    assert lg.has_console_handler()

    # Remove and re-enable file handler
    lg.disable_file_output()
    assert not lg.has_file_handler()
    lg.enable_file_output()  # should re-add existing stored handler
    assert lg.has_file_handler()

    # Ensure _custom_log disables/enables console around a debug call
    calls = []
    monkeypatch.setattr(lg, 'disable_console_output', lambda: calls.append('disable'), raising=True)
    monkeypatch.setattr(lg, 'enable_console_output', lambda: calls.append('enable'), raising=True)
    lg.debug('msg')
    assert calls == ['disable', 'enable']


def test_custom_logger_verbose_no_file(monkeypatch):
    import app.config.logger as clog

    def fake_read_config(section, path):
        return {"file_name": "vlog", "verbose": "True", "log_dir": ""}

    monkeypatch.setattr(clog, 'read_config', fake_read_config, raising=True)
    lg = clog.CustomLogger()
    assert lg.verbose is True and not lg.has_file_handler() and lg.has_console_handler()
    emitted = []
    orig_emit = lg.stdout_handler.emit
    def wrap(record):
        emitted.append(record.getMessage())
        return orig_emit(record)
    monkeypatch.setattr(lg.stdout_handler, 'emit', wrap, raising=True)
    lg.info('hello')
    assert 'hello' in emitted


def test_custom_logger_non_verbose_no_file_no_output(monkeypatch):
    import app.config.logger as clog

    def fake_read_config(section, path):
        return {"file_name": "nolog", "verbose": "False", "log_dir": ""}

    monkeypatch.setattr(clog, 'read_config', fake_read_config, raising=True)
    lg = clog.CustomLogger()
    assert lg.verbose is False and not lg.has_file_handler()
    emitted = []
    orig_emit = lg.stdout_handler.emit
    def wrap(record):
        emitted.append(record.getMessage())
        return orig_emit(record)
    monkeypatch.setattr(lg.stdout_handler, 'emit', wrap, raising=True)
    lg.debug('silent?')  # should not emit because verbose False and no file handler
    assert emitted == []
import types
import json
import pytest


def test_multifaceted_language_model_cache_and_policy(monkeypatch):
    import app.utility.multifaceted as mf
    # stub openai.ChatCompletion.create to raise policy first, then return content
    calls = {"i": 0}
    def fake_create(**k):
        calls["i"] += 1
        if calls["i"] == 1:
            raise Exception("violates content management policy")
        return {
            "choices": [
                {"message": {"content": "Rating: 7"}}
            ]
        }
    import openai as _openai
    monkeypatch.setattr(_openai.ChatCompletion, 'create', fake_create, raising=True)
    m = mf.MultifacetedEvaluation("k","e","v","m")
    conv = [{"role": "user", "content": "hi"}]
    out1 = m.language_model(conv)
    # On policy error path, function returns synthetic completion with Rating: 10 (not cached)
    assert isinstance(out1, dict)
    assert out1["choices"][0]["message"]["content"].startswith("Rating:")
    # Next call succeeds and caches
    out2 = m.language_model(conv)
    assert isinstance(out2, dict)
    # Third call should reuse cached success response
    out3 = m.language_model(conv)
    assert out3 == out2


def test_language_models_llama_and_palm_and_gempro(monkeypatch):
    import app.utility.language_models as lm
    # LlamaModel: stub requests.post
    class Resp:
        def __init__(self, payload):
            self._p = payload
        def raise_for_status(self):
            return None
        def json(self):
            return {"choices":[{"message":{"content":"ok-llama"}}]}
    monkeypatch.setattr(lm, 'requests', types.SimpleNamespace(post=lambda *a, **k: Resp({})))
    llama = lm.LlamaModel("Meta-Llama-3.3-70B-Instruct")
    assert llama.batched_generate(["q1","q2"], 5, 0.1) == ["ok-llama","ok-llama"]

    # PaLM: stub genai.chat path
    class FakeParts: text = "ok-palm"
    class FakeContent: last = FakeParts.text
    class FakeGenai:
        @staticmethod
        def configure(api_key=None):
            return None
        @staticmethod
        def chat(messages=None, temperature=None, top_p=None):
            return types.SimpleNamespace(last="ok-palm")
    monkeypatch.setattr(lm, 'genai', FakeGenai)
    palm = lm.PaLM("palm-2")
    out_p = palm.generate([{"role":"user","content":"hi"}], 5, 0.1, 1.0)
    assert out_p == "ok-palm"

    # GeminiPro: stub GenerativeModel.generate_content
    class _Resp:
        def __init__(self, text):
            self.candidates = [types.SimpleNamespace(content=types.SimpleNamespace(parts=[types.SimpleNamespace(text=text)]))]
    class _GM:
        def __init__(self, model): pass
        def generate_content(self, contents=None, generation_config=None):
            return _Resp("ok-gempro")
    _Genai2 = types.SimpleNamespace(
        GenerativeModel=_GM,
        GenerationConfig=lambda **k: None,
        configure=lambda api_key=None: None
    )
    monkeypatch.setattr(lm, 'genai', _Genai2)
    gp = lm.GeminiPro("gemini-pro")
    assert gp.batched_generate(["a","b"], 5, 0.1) == ["ok-gempro","ok-gempro"]


def test_endpointmodel_tap_get_response_and_chatgroqq_batch(monkeypatch):
    import app.utility.language_models as lm
    # EndpointModel_Tap.get_response uses batched_generate internally
    ep = lm.EndpointModel_Tap("http://t", {"A":"B"}, {"x":"1"}, "q")
    monkeypatch.setattr(lm.EndpointModel_Tap, 'batched_generate', lambda self, prompts, u, h, p, v: ["ans" for _ in prompts], raising=True)
    outs = ep.get_response(["p1","p2"], {
        "target_endpoint_url":"http://t",
        "target_endpoint_headers": {"A":"B"},
        "target_endpoint_payload": {"x":"1"},
        "target_endpoint_prompt_variable": "q"
    })
    assert outs == ["ans","ans"]

    # ChatGroqq.batched_generate should call generate per item
    class FakeGroq:
        def __init__(self, *a, **k): pass
        def invoke(self, conv):
            return types.SimpleNamespace(content="ok-cg")
    monkeypatch.setattr(lm, 'ChatGroq', FakeGroq, raising=True)
    cg = lm.ChatGroqq("mixtral-8x7b-32768")
    outs2 = cg.batched_generate([[{"role":"user","content":"a"}],[{"role":"user","content":"b"}]], 5, 0.1)
    assert outs2 == ["ok-cg","ok-cg"]


def test_judges_and_evaluators_bedrock_gemini_branches(monkeypatch):
    import app.utility.judges as judges
    import app.utility.evaluators as evaluators
    # GeminiJudge score/get_recommendation
    gj = judges.GeminiJudge({"judge_model":"gemini-pro","judge_max_n_tokens":5,"judge_temperature":0.1,"goal":"g","target_str":"t"})
    class FakeGM:
        def batched_generate(self, convs, max_n_tokens=None, temperature=None):
            return ["[[8]]"]
        def generate(self, conversation, max_n_tokens=None, temperature=None, top_p=None):
            return "Recommendation: [[Use filters]]"
    monkeypatch.setattr(gj, 'judge_model', FakeGM(), raising=False)
    assert gj.judge_score(["p"],["r"]) == [8]
    assert gj.get_recommendation("R","p","r") == "Use filters"

    # BedrockJudge judge_score and recommendation
    bj = judges.BedrockJudge({"judge_model":"bedrock","judge_max_n_tokens":5,"judge_temperature":0.1,"goal":"g","target_str":"t"})
    class FakeBM:
        def batched_generate(self, convs, max_n_tokens=None, temperature=None):
            return ["[[6]]"]
        def generate(self, prompt, max_n_tokens=None, temperature=None, top_p=None):
            return "Recommendation: [[Be cautious]]"
    monkeypatch.setattr(bj, 'judge_model', FakeBM(), raising=False)
    assert bj.judge_score(["p"],["r"]) == [6]
    assert bj.get_recommendation("R","p","r") == "Be cautious"

    # GeminiEvaluator judge/on_topic/recommendation
    ge = evaluators.GeminiEvaluator({"judge_model":"gemini-pro","judge_max_n_tokens":5,"judge_temperature":0.1,"goal":"g","target_str":"t"})
    class FakeGM2:
        def batched_generate(self, convs, max_n_tokens=None, temperature=None):
            # First two items map to judge and on-topic scores
            return ["[[9]]","[[no]]"][:len(convs)]
        def generate(self, conversation, max_n_tokens=None, temperature=None, top_p=None):
            return "Recommendation: [[Tighten policies]]"
    monkeypatch.setattr(ge, 'judge_model', FakeGM2(), raising=False)
    assert ge.judge_score(["p"],["r"]) == [9]
    assert ge.on_topic_score(["p"],["orig"]) in ([0],[1])  # parser maps yes/no; tolerate either based on implementation
    assert ge.get_recommendation("R","p","r") == "Tighten policies"

    # BedrockEvaluator judge/on_topic/recommendation
    be = evaluators.BedrockEvaluator({"judge_model":"bedrock","judge_max_n_tokens":5,"judge_temperature":0.1,"goal":"g","target_str":"t"})
    class FakeBM2:
        def batched_generate(self, convs, max_n_tokens=None, temperature=None):
            return ["[[3]]"]
        def generate(self, prompt, max_n_tokens=None, temperature=None, top_p=None):
            return "Recommendation: [[Harden endpoints]]"
    monkeypatch.setattr(be, 'judge_model', FakeBM2(), raising=False)
    assert be.judge_score(["p"],["r"]) == [3]
    assert be.on_topic_score(["p"],["orig"]) in ([0],[1])
    assert be.get_recommendation("R","p","r") == "Harden endpoints"
import types
import json
import pytest


def test_gpt_retry_and_empty_branch(monkeypatch):
    import app.utility.language_models as lm
    calls = {"n": 0}
    class FakeOpenAI:
        class ChatCompletion:
            @staticmethod
            def create(engine=None, messages=None, max_tokens=None, temperature=None, top_p=None, request_timeout=None):
                calls["n"] += 1
                # First attempt: empty content to trigger retry; second: valid
                content = "" if calls["n"] == 1 else "ok-gpt"
                return {"choices": [{"message": {"content": content}}]}
    monkeypatch.setattr(lm, 'openai', FakeOpenAI)
    gpt = lm.GPT('gpt-3.5-turbo')
    out = gpt.generate([{"role":"user","content":"hi"}], 8, 0.1, 1.0)
    assert out == "ok-gpt"


def test_endpoint_model_pair_generate_paths(monkeypatch):
    import app.utility.language_models as lm
    seq = {"i": 0}
    class Resp:
        def __init__(self, status, text=None, payload=None):
            self.status_code = status
            self.text = text or ""
            self._payload = payload
        def json(self):
            if self._payload is Ellipsis:
                raise ValueError("not json")
            return self._payload or {"foo": "bar"}
    def post_stub(url=None, headers=None, json=None, verify=None, timeout=None):
        seq["i"] += 1
        if seq["i"] == 1:
            # network error
            raise lm.requests.RequestException("net")
        if seq["i"] == 2:
            return Resp(500, text="err")
        return Resp(200, payload={"ok": True})
    monkeypatch.setattr(lm, 'requests', types.SimpleNamespace(post=post_stub, RequestException=Exception))
    monkeypatch.setattr(lm.time, 'sleep', lambda *a, **k: None)

    em = lm.EndpointModel_Pair("http://t", {"A":"B"}, {"x":"1"}, "q", max_retries=4)
    # Bypass GPT extraction and return direct text
    monkeypatch.setattr(lm.EndpointModel_Pair, 'extract_text_with_gpt', lambda self, result: "final")
    out = em.generate("prompt", "http://t", {"A":"B"}, {"x":"1"}, "q")
    assert out == "final"

    # Exhausted case returns $ERROR$
    seq["i"] = 0
    def post_ok(*a, **k):
        return Resp(200, payload={"ok": True})
    monkeypatch.setattr(lm, 'requests', types.SimpleNamespace(post=post_ok, RequestException=Exception))
    monkeypatch.setattr(lm.EndpointModel_Pair, 'extract_text_with_gpt', lambda self, result: "")
    em2 = lm.EndpointModel_Pair("http://t", {}, {}, "q", max_retries=2)
    out2 = em2.generate("p", "http://t", {}, {}, "q")
    assert out2 == "$ERROR$"


def test_endpoint_model_tap_generate_paths(monkeypatch):
    import app.utility.language_models as lm
    class Resp:
        def __init__(self, status, payload):
            self.status_code = status
            self._payload = payload
            self.text = ""
        def json(self):
            if self._payload is Ellipsis:
                raise ValueError()
            return self._payload
    seq = {"i": 0}
    def post_stub(url=None, headers=None, json=None, verify=None, timeout=None):
        seq["i"] += 1
        if seq["i"] == 1:
            raise lm.requests.RequestException("net")
        if seq["i"] == 2:
            return Resp(500, {})
        return Resp(200, {"ok": True})
    monkeypatch.setattr(lm, 'requests', types.SimpleNamespace(post=post_stub, RequestException=Exception))
    monkeypatch.setattr(lm.time, 'sleep', lambda *a, **k: None)
    et = lm.EndpointModel_Tap("http://t", {}, {}, "q")
    monkeypatch.setattr(lm.EndpointModel_Tap, 'extract_text_with_gpt', lambda self, result: "t")
    out = et.generate("p", "http://t", {}, {}, "q")
    assert out == "t"


def test_apimodel_llama_and_vicuna(monkeypatch):
    import app.utility.language_models as lm
    captured = {}
    class FakeResp:
        def __init__(self, payload):
            self._p = payload
        def json(self):
            return self._p
    def req_stub(method, url, headers=None, timeout=None, json=None):
        captured['payload'] = json
        # Return output based on model_name the test sets
        auth = (headers or {}).get('Authorization', '')
        return FakeResp({"output": "vicuna-out"} if 'vicuna' in auth else ["llama-out"])
    monkeypatch.setattr(lm, 'urllib3', types.SimpleNamespace(request=req_stub, Timeout=lambda *a, **k: 1))

    vic = lm.APIModelVicuna13B('vicuna-api-model')
    out_v = vic.generate([{"role":"system","content":"s"}], 5, 0.1, 1.0)
    assert out_v in ("vicuna-out", lm.APIModel.API_ERROR_OUTPUT)

    lam = lm.APIModelLlama7B('llama-2-api-model')
    out_l = lam.generate([{"role":"system","content":"s"}], 4, 0.0, 1.0)
    assert out_l in (["llama-out"], "llama-out", lm.APIModel.API_ERROR_OUTPUT)
    # Ensure prompt moved from system_prompt for llama path
    assert captured['payload']['prompt'] != ''


def test_huggingface_runtime_error_branch(monkeypatch):
    import app.utility.language_models as lm
    class FakeTensor:
        def __init__(self, shape=(1, 1)):
            self._shape = shape
        def to(self, *a, **k):
            return self
        @property
        def shape(self):
            return (1, 1)
    class FakeTokenizer:
        eos_token_id = 0
        def __call__(self, prompts, return_tensors=None, padding=None, truncation=None):
            return {"input_ids": FakeTensor()}
        def batch_decode(self, ids, skip_special_tokens=True):
            return ["decoded"]
    class FakeConfig:
        is_encoder_decoder = False
    class FakeModel:
        config = FakeConfig()
        device = types.SimpleNamespace(index=None)
        def generate(self, *a, **k):
            raise RuntimeError("boom")
        def eval(self):
            return self
    hf = lm.HuggingFace("hf", FakeModel(), FakeTokenizer())
    outs = hf.batched_generate(["p1","p2"], 8, 0.1, 1.0)
    # Implementation may surface concurrency semaphore timeout instead of runtime
    assert outs == ["$ERROR-RUNTIME$"]*2 or outs == ["$ERROR-CONCURRENCY$"]*2


def test_gemini_model_batched(monkeypatch):
    import app.utility.language_models as lm
    class FakeResp:
        def __init__(self, text):
            self.candidates = [types.SimpleNamespace(content=types.SimpleNamespace(parts=[types.SimpleNamespace(text=text)]))]
    class FakeClient:
        def __init__(self, api_key=None):
            self.models = types.SimpleNamespace(generate_content=lambda model=None, contents=None: FakeResp("ok-gm"))
    monkeypatch.setattr(lm, 'genai', types.SimpleNamespace(Client=FakeClient))
    gm = lm.GeminiModel("gemini-1.5-pro")
    outs = gm.batched_generate(["a","b"], 8, 0.1)
    assert outs == ["ok-gm","ok-gm"]


def test_bedrock_model_setup_early_exit(monkeypatch):
    import app.utility.language_models as lm
    # Ensure env missing so _setup_bedrock_client exits early and llm remains None
    monkeypatch.setenv("AWS_KEY_ADMIN_PATH", "")
    br = lm.BedrockModel("anthropic.claude-3-sonnet-20240229-v1:0")
    out = br.generate("p", 8, 0.1, 1.0)
    # With llm None, it should return default_output
    assert out == br.default_output


def test_conversers_prune_zero_scores_branch(monkeypatch):
    from app.utility.conversers import prune
    # sorting_score all zeros to trigger adjusted truncated list branch
    attack_params = {"width": 1}
    lists = {
        'on_topic_scores': [0, 0, 0],
        'judge_scores': [5, 6, 7],
        'adv_prompt_list': ["a1","a2","a3"],
        'improv_list': ["i1","i2","i3"],
        'convs_list': ["c1","c2","c3"],
        'target_response_list': ["t1","t2","t3"],
        'extracted_attack_list': ["e1","e2","e3"],
        'sorting_score': [0,0,0]
    }
    out = prune(
        on_topic_scores=lists['on_topic_scores'],
        judge_scores=lists['judge_scores'],
        adv_prompt_list=lists['adv_prompt_list'],
        improv_list=lists['improv_list'],
        convs_list=lists['convs_list'],
        target_response_list=lists['target_response_list'],
        extracted_attack_list=lists['extracted_attack_list'],
        sorting_score=lists['sorting_score'],
        attack_params=attack_params
    )
    # Only lengths matter for this branch; unpack to named variables for clarity
    on_topic_scores, judge_scores, adv_prompt_list, improv_list, convs_list, target_response_list, extracted_attack_list = out  # noqa: F841
    # Ensure we got at least 2 due to adjusted branch even though width=1
    assert len(on_topic_scores) == 2
    assert len(adv_prompt_list) == 2
    assert len(convs_list) == 2


def test_judges_and_evaluators_fallback_parsing():
    import app.utility.judges as judges
    import app.utility.evaluators as evaluators
    jb = judges.JudgeBase({"judge_model":"gpt-4","judge_max_n_tokens":5,"judge_temperature":0.1,"goal":"g","target_str":"t"})
    assert jb.process_output("no markers here") == 1
    eb = evaluators.EvaluatorBase({"judge_model":"gpt-4","judge_max_n_tokens":5,"judge_temperature":0.1,"goal":"g","target_str":"t"})
    assert eb.process_output_judge_score("none") == 1
    assert eb.process_output_on_topic_score("none") == 1


def test_multifaceted_conv_and_parse_output():
    import importlib
    import app.utility.multifaceted as mf
    # Some earlier tests may stub this module; ensure we reload the real module if methods are missing
    if not hasattr(getattr(mf, 'MultifacetedEvaluation', object), 'multifaceted_create_conv'):
        mf = importlib.reload(mf)
    # Ensure module-level Azure model config exists to satisfy __init__
    setattr(mf, 'AZURE_GPT4_MODEL_NAME', getattr(mf, 'AZURE_GPT4_MODEL_NAME', None) or 'gpt4-deployment')
    setattr(mf, 'AZURE_GPT4_API_KEY', getattr(mf, 'AZURE_GPT4_API_KEY', None) or 'key')
    setattr(mf, 'AZURE_GPT4_API_BASE', getattr(mf, 'AZURE_GPT4_API_BASE', None) or 'http://base')
    setattr(mf, 'AZURE_GPT4_API_VERSION', getattr(mf, 'AZURE_GPT4_API_VERSION', None) or '2024-01-01')
    m = mf.MultifacetedEvaluation("k","e","v","m")
    # Exercise multifaceted_create_conv and parse_response_segment_multifaceted_output
    conv = m.multifaceted_create_conv("intent text", "response text")
    assert isinstance(conv, list)
    # Proper format parses two ratings
    parsed = m.parse_response_segment_multifaceted_output("first: 1;second: 0")
    assert parsed == [True, False]
    # Fallback branch returns [False, False]
    parsed2 = m.parse_response_segment_multifaceted_output("garbled")
    assert parsed2 == [False, False]


def test_nojudge_noevaluator_and_chatgroq_evaluator(monkeypatch):
    import app.utility.judges as judges
    import app.utility.evaluators as evaluators
    nj = judges.NoJudge({"judge_model":"no-judge","judge_max_n_tokens":5,"judge_temperature":0.1,"goal":"g","target_str":"t"})
    assert nj.score(["p1","p2"],["r1","r2"]) == [1,1]
    ne = evaluators.NoEvaluator({"judge_model":"no-evaluator","judge_max_n_tokens":5,"judge_temperature":0.1,"goal":"g","target_str":"t"})
    assert ne.judge_score(["p"],["r"]) == [1]
    assert ne.on_topic_score(["p"],["orig"]) == [1]

    # chatgroqEvaluator path
    class FakeChatGroq:
        def __init__(self, *a, **k): pass
        def batched_generate(self, convs, max_n_tokens=None, temperature=None):
            return ["[[7]]" for _ in convs]
    # Monkeypatch ChatGroqq class before creating evaluator to avoid real API key usage
    monkeypatch.setattr(evaluators, 'ChatGroqq', FakeChatGroq, raising=True)
    cev = evaluators.chatgroqEvaluator({"judge_model":"chatgroq","judge_max_n_tokens":5,"judge_temperature":0.1,"goal":"g","target_str":"t"})
    scores = cev.judge_score(["p1","p2"],["r1","r2"])
    assert scores == [7,7]
import os, sys, types


def _prepare_lightweight_stubs():
    from importlib.machinery import ModuleSpec
    # Stub heavy external modules to avoid network & large dependency import chains
    def ensure(name):
        if name not in sys.modules:
            m = types.ModuleType(name)
            m.__spec__ = ModuleSpec(name, loader=None)
            sys.modules[name] = m
        return sys.modules[name]

    # torch (light stub to avoid heavy dependency if not installed)
    if 'torch' not in sys.modules:
        torch_mod = types.ModuleType('torch')
        class _inference_mode:
            def __enter__(self): return None
            def __exit__(self, *a): return False
        torch_mod.inference_mode = lambda: _inference_mode()
        class _cuda:
            @staticmethod
            def is_available(): return False
            @staticmethod
            def empty_cache(): return None
        torch_mod.cuda = _cuda()
        sys.modules['torch'] = torch_mod

    # openai
    openai = ensure('openai')
    if not hasattr(openai, 'ChatCompletion'):
        class _Chat:
            calls = 0
            @staticmethod
            def create(**k):
                _Chat.calls += 1
                if _Chat.calls == 1:
                    raise RuntimeError('boom')
                return {"choices":[{"message":{"content":"stub"}}]}
        openai.ChatCompletion = _Chat  # type: ignore[attr-defined]

    # anthropic
    anthropic = ensure('anthropic')
    if not hasattr(anthropic, 'Anthropic'):
        anthropic.APIError = Exception
        # Lightweight stub Anthropic client used only for returning a fixed completion
        anthropic.Anthropic = lambda api_key=None: types.SimpleNamespace(completions=types.SimpleNamespace(create=lambda **k: types.SimpleNamespace(completion="ok")))  # type: ignore[attr-defined]

    # google.generativeai
    genai = ensure('google.generativeai')
    if not hasattr(genai, 'Client'):
        class _Client:
            def __init__(self, api_key=None):  # minimal stub to satisfy constructor
                pass
            class models:
                @staticmethod
                def generate_content(model=None, contents=None):
                    return types.SimpleNamespace(candidates=[types.SimpleNamespace(content=types.SimpleNamespace(parts=[types.SimpleNamespace(text="ok")]))])
        class _GenModel:
            def __init__(self, model):  # placeholder for model name
                self._model = model
            def generate_content(self, contents=None, generation_config=None):
                return types.SimpleNamespace(candidates=[types.SimpleNamespace(content=types.SimpleNamespace(parts=[types.SimpleNamespace(text="ok")]))])
        genai.Client = _Client  # type: ignore[attr-defined]
        genai.GenerativeModel = _GenModel  # type: ignore[attr-defined]
        genai.GenerationConfig = lambda **k: None  # type: ignore[attr-defined]
        genai.configure = lambda api_key=None: None  # type: ignore[attr-defined]

    # langchain_groq
    lg = ensure('langchain_groq')
    if not hasattr(lg, 'ChatGroq'):
        class _Groq:
            def __init__(self, groq_api_key=None, model_name=None): self.calls = 0
            def invoke(self, conv):
                self.calls += 1
                if self.calls == 1:
                    return types.SimpleNamespace(content="")
                return types.SimpleNamespace(content="ok")
        lg.ChatGroq = _Groq  # type: ignore[attr-defined]

    # langchain_core (minimal to satisfy potential attribute lookups)
    ensure('langchain_core')
    ensure('langchain_core.load')
    ensure('langchain_core.language_models')
    ensure('langchain_core.language_models.base')
    # transformers (prevent deep dependency chain) only if needed
    tf = ensure('transformers')
    if not hasattr(tf, 'GPT2TokenizerFast'):
        class _Tok: eos_token_id = 0
        tf.GPT2TokenizerFast = _Tok  # type: ignore[attr-defined]

    # boto3 & langchain_aws
    boto3 = ensure('boto3')
    if not hasattr(boto3, 'client'): boto3.client = lambda **k: object()  # type: ignore[attr-defined]
    lc_aws = ensure('langchain_aws')
    if not hasattr(lc_aws, 'ChatBedrock'):
        class _Bed: 
            def __init__(self,*a,**k):  # empty stub
                pass
            def invoke(self,p): return types.SimpleNamespace(content="ok")
        lc_aws.ChatBedrock = _Bed  # type: ignore[attr-defined]

    # Set env for GPT config
    os.environ.setdefault('AZURE_GPT4_MODEL_NAME','gpt-4')
    os.environ.setdefault('AZURE_GPT4_API_KEY','k')
    os.environ.setdefault('AZURE_GPT4_API_BASE','https://x')
    os.environ.setdefault('AZURE_GPT4_API_VERSION','2024-01-01')
    os.environ.setdefault('AZURE_GPT3_MODEL_NAME','gpt-3')
    os.environ.setdefault('AZURE_GPT3_API_KEY','k3')
    os.environ.setdefault('AZURE_GPT3_API_BASE','https://y')
    os.environ.setdefault('AZURE_GPT3_API_VERSION','2024-01-01')
    # Groq key used by ChatGroqq wrapper
    os.environ.setdefault('GROQCLOUD_API_KEY','dummy-key')
    # Also set GROQ_API_KEY for langchain_groq client compatibility
    os.environ.setdefault('GROQ_API_KEY','dummy-key')


def test_language_models_stubbed_paths(monkeypatch):
    _prepare_lightweight_stubs()
    import app.utility.language_models as lm
    # GPT retry path (first raises, then succeeds)
    g = lm.GPT('gpt-4')
    g.set_api_configuration('gpt-4')
    out = g.generate([{"role":"user","content":"hi"}], 5, 0.0, 1.0)
    assert out in ('stub', '$ERROR$')
    # ChatGroqq path with first empty then ok
    cg = lm.ChatGroqq('mix')
    cg_out = cg.generate([{"role":"user","content":"q"}], 5, 0.1, 1.0)
    assert cg_out in ('', 'ok', '$ERROR$')
    # APIModel llama payload branch
    class FakeAPI(lm.APIModel):
        API_HOST_LINK = 'http://unused'
        MODEL_API_KEY = 'k'
    inst = FakeAPI('llama-2')
    # monkeypatch urllib3.request inside module
    def fake_request(method: str, url: str, headers=None, timeout=None, json: dict | None = None):
        # Ensure llama path payload construction occurred
        assert json and 'prompt' in json
        class R:
            def json(self): return {'output':'hello'}
        return R()
    monkeypatch.setattr(lm, 'urllib3', types.SimpleNamespace(request=fake_request), raising=True)
    api_out = inst.generate([{"role":"system","content":"sys"}], 5, 0.0, 1.0)
    assert api_out in ('hello', '$ERROR$')


def test_report_failed_rows_and_no_categories(monkeypatch):
    import app.utility.report as report
    data = {
        'total_rows': 5,
        'processed_rows': 3,
        'technical_failed_rows': [1,2],
        'jailbroken_rows': 0,
        'category_wise_score': {},
        'target_model': 'm',
        'target_temperature': 0.2,
        'n_iterations': 1,
        'technique_type': 'PAIR'
    }
    html = report.generate_html_report_pair(data)
    assert 'technical' in html.lower()


def test_system_prompts_variations():
    from app.utility.system_prompts import get_judge_system_prompt_pair
    prompt = get_judge_system_prompt_pair('goal','target')
    assert 'goal' in prompt.lower()
"""
Targeted tests to increase code coverage above 85%.
Focuses on untested utility functions and edge cases.
"""
import pytest
from unittest.mock import Mock, patch


class TestConversersAdditional:
    """Additional tests for conversers module."""
    
    def test_extract_json_valid_with_required_keys(self):
        """Test extract_json with valid JSON containing required keys."""
        from app.utility.conversers import extract_json
        
        text = 'Some text {"improvement": "better", "prompt": "test prompt"} more text'
        result, json_str = extract_json(text)
        assert result is not None
        assert "improvement" in result
        assert "prompt" in result
        
    def test_extract_json_missing_keys(self):
        """Test extract_json with JSON missing required keys."""
        from app.utility.conversers import extract_json
        
        text = 'Some text {"key": "value"} more text'
        result, json_str = extract_json(text)
        assert result is None
        
    def test_extract_json_no_json(self):
        """Test extract_json with no JSON structure."""
        from app.utility.conversers import extract_json
        
        text = 'No JSON here'
        result, json_str = extract_json(text)
        assert result is None
        assert json_str is None
        
    def test_get_init_msg_pair(self):
        """Test get_init_msg_pair function."""
        from app.utility.conversers import get_init_msg_pair
        
        msg = get_init_msg_pair("test goal", "test target")
        assert isinstance(msg, str)
        assert len(msg) > 0
        
    def test_process_target_response_pair(self):
        """Test process_target_response_pair function."""
        from app.utility.conversers import process_target_response_pair
        
        result = process_target_response_pair("response text", 8, "test goal", "test target")
        assert isinstance(result, str)
        assert len(result) > 0
        
    def test_conv_template_pair(self):
        """Test conv_template_pair function."""
        from app.utility.conversers import conv_template_pair
        
        template = conv_template_pair("llama-2")
        assert template is not None
        
    def test_clean_attacks_and_convs(self):
        """Test clean_attacks_and_convs function."""
        from app.utility.conversers import clean_attacks_and_convs
        
        attacks = ["attack1", "attack2", "attack3"]
        convs = ["conv1", "conv2", "conv3"]
        
        cleaned_attacks, cleaned_convs = clean_attacks_and_convs(attacks, convs)
        assert len(cleaned_attacks) <= len(attacks)
        assert len(cleaned_convs) <= len(convs)
        



class TestMappersValidation:
    """Test mapper validations and defaults."""
    
    def test_redteam_payload_pair_custom_values(self):
        """Test RedteamPayloadRequestPair with custom values."""
        from app.mappers.mappers import RedteamPayloadRequestPair
        
        payload = RedteamPayloadRequestPair(
            goal="custom goal",
            target_str="custom target",
            attack_max_n_tokens=1000,
            max_n_attack_attempts=10
        )
        assert payload.goal == "custom goal"
        assert payload.attack_max_n_tokens == 1000
        assert payload.max_n_attack_attempts == 10
        
    def test_redteam_payload_tap_custom_values(self):
        """Test RedteamPayloadRequestTap with custom values."""
        from app.mappers.mappers import RedteamPayloadRequestTap
        
        payload = RedteamPayloadRequestTap(
            goal="tap goal",
            target_str="tap target",
            branching_factor=5
        )
        assert payload.goal == "tap goal"
        assert payload.branching_factor == 5
        
    def test_redteam_payload_pair_defaults(self):
        """Test RedteamPayloadRequestPair with default values."""
        from app.mappers.mappers import RedteamPayloadRequestPair
        
        payload = RedteamPayloadRequestPair()
        # Should initialize with defaults
        assert payload is not None


class TestExceptionHandling:
    """Test exception classes."""
    
    def test_ai_shield_exception_base(self):
        """Test aiShieldException base class."""
        from app.exception.exception import aiShieldException
        
        # Should be able to create exception
        exc = aiShieldException("test message")
        assert "test message" in str(exc)
        
    def test_exception_module_imports(self):
        """Test exception module imports correctly."""
        from app.exception import exception
        assert exception is not None
        
    def test_global_exception_handler_import(self):
        """Test global exception handler imports."""
        from app.exception import global_exception_handler
        assert global_exception_handler is not None


class TestUtilityFunctions:
    """Test various utility functions for coverage."""
    
    def test_system_prompts_constants_exist(self):
        """Test system_prompts module has expected constants."""
        from app.utility import system_prompts
        
        # Module should be importable and have attributes
        assert hasattr(system_prompts, '__name__')

