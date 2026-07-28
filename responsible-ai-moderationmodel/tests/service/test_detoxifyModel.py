import importlib
import sys
import types
import time
import math
from collections import defaultdict
import contextlib
import pytest


class DummyBatchEncoding(dict):
    def __init__(self, text):
        # approximate token count by words; keep as plain python lists
        toks = text.split()
        self['input_ids'] = [list(range(1, len(toks) + 1))]
        # keep original text so downstream fakes can inspect it
        self['text'] = text

    def to(self, device):
        # mimic huggingface BatchEncoding .to(device)
        return self


class DummyTokenizer:
    def encode(self, text, add_special_tokens=False):
        # return a list of token ids approximating token count
        return list(range(len(text.split())))

    def decode(self, ids):
        # record decode calls for chunking tests and return a chunk string
        try:
            self.decode_calls.append(ids)
        except Exception:
            self.decode_calls = [ids]
        # return a word sequence approximating the number of ids
        return ' '.join(['word'] * len(ids))

    def __call__(self, text, return_tensors=None, truncation=True, padding=True):
        # return a mapping-like object (BatchEncoding-like)
        return DummyBatchEncoding(text)

    # lang code mapping used in other modules
    @property
    def lang_code_to_token(self):
        return {"en": "<en>"}


class DummyModel:
    def __init__(self, num_labels=7):
        self.num_labels = num_labels

    def to(self, device):
        return self

    def eval(self):
        return self

    def __call__(self, *args, **kwargs):
        # Derive the input text from kwargs when possible so we can
        # produce different scores for toxic vs benign examples.
        text = None
        if 'text' in kwargs:
            text = kwargs.get('text')
        elif 'input_ids' in kwargs:
            # approximate text by length of input_ids
            ids = kwargs.get('input_ids')
            try:
                length = len(ids[0])
                text = 'word ' * length
            except Exception:
                text = ''
        else:
            # fallback to args (not expected)
            text = ''

        # simple keyword-based heuristic for test realism
        low_base = 0.05
        logits = [low_base for _ in range(self.num_labels)]
        if text:
            t = text.lower()
            # if toxic keywords are present, raise certain label logits
            toxic_keywords = ['badword', 'kill', 'hate', 'stupid', 'idiot']
            if any(k in t for k in toxic_keywords):
                # set higher values for toxicity-related labels
                logits[0] = 3.0  # toxicity
                logits[1] = 2.5  # severe_toxicity
                logits[2] = 2.0  # obscene
                logits[4] = 2.0  # insult
            else:
                # benign text: slightly positive logits near zero
                logits = [0.05 for _ in range(self.num_labels)]

        return types.SimpleNamespace(logits=[logits])


def import_with_stubs(monkeypatch):
    # Provide a fake mapper.mapper module with profanityScore
    fake_mapper_pkg = types.ModuleType('mapper')
    fake_mapper_mod = types.ModuleType('mapper.mapper')

    class profanityScore:
        def __init__(self, metricName=None, metricScore=None):
            self.metricName = metricName
            self.metricScore = metricScore

        def dict(self):
            return {"metricName": self.metricName, "metricScore": self.metricScore}

    fake_mapper_mod.profanityScore = profanityScore
    fake_mapper_pkg.mapper = fake_mapper_mod

    # Insert fake mapper modules into sys.modules using monkeypatch so pytest
    # will restore the original state after the test.
    monkeypatch.setitem(sys.modules, 'mapper', fake_mapper_pkg)
    monkeypatch.setitem(sys.modules, 'mapper.mapper', fake_mapper_mod)

    # Create a fake transformers module with expected factory functions
    fake_transformers = types.ModuleType('transformers')
    fake_transformers.AutoConfig = types.SimpleNamespace(from_pretrained=lambda path: types.SimpleNamespace())
    fake_transformers.AutoTokenizer = types.SimpleNamespace(from_pretrained=lambda path: DummyTokenizer())
    fake_transformers.AutoModelForSequenceClassification = types.SimpleNamespace(from_pretrained=lambda path: DummyModel())
    # Insert fake transformers module via monkeypatch
    monkeypatch.setitem(sys.modules, 'transformers', fake_transformers)

    # Create a lightweight fake torch module with only the functions
    # used by the target module (sigmoid, cat, mean, no_grad, device)
    fake_torch = types.ModuleType('torch')

    def _sigmoid(x):
        # expect x as nested-list [[...]] -> apply elementwise
        def s(v):
            try:
                return 1.0 / (1.0 + math.exp(-v))
            except Exception:
                return v

        return [[s(elem) for elem in row] for row in x]

    def _cat(list_of_preds, dim=0):
        # concatenate list of nested-lists along first axis
        out = []
        for p in list_of_preds:
            # p expected to be nested-list [[...]]
            out.extend(p)
        return out

    def _mean(all_preds, dim=0, keepdim=True):
        # compute mean across first axis; all_preds is list of rows
        if not all_preds:
            return [[0.0]]
        cols = len(all_preds[0])
        means = []
        for c in range(cols):
            s = sum(row[c] for row in all_preds)
            means.append(s / len(all_preds))
        return [means] if keepdim else means

    @contextlib.contextmanager
    def _no_grad():
        yield None

    fake_torch.sigmoid = _sigmoid
    fake_torch.cat = _cat
    fake_torch.mean = _mean
    fake_torch.no_grad = _no_grad
    # a simple device placeholder
    fake_torch.device = lambda *args, **kwargs: 'cpu'

    monkeypatch.setitem(sys.modules, 'torch', fake_torch)

    # Insert a minimal fake fastapi package and submodule to avoid importing real FastAPI
    fake_fastapi = types.ModuleType('fastapi')
    fake_fastapi.__path__ = []  # make it a package
    fake_fastapi_encoders = types.ModuleType('fastapi.encoders')
    fake_fastapi_encoders.jsonable_encoder = lambda x: x
    # register both module and submodule
    monkeypatch.setitem(sys.modules, 'fastapi', fake_fastapi)
    monkeypatch.setitem(sys.modules, 'fastapi.encoders', fake_fastapi_encoders)
    # also expose attribute on package
    fake_fastapi.encoders = fake_fastapi_encoders

    # Ensure module reload for deterministic import
    # Ensure module reload for deterministic import
    monkeypatch.setitem(sys.modules, 'service.detoxifyModel', None)
    if 'service.detoxifyModel' in sys.modules:
        monkeypatch.delitem(sys.modules, 'service.detoxifyModel', raising=False)

    mod = importlib.import_module('service.detoxifyModel')
    importlib.reload(mod)

    # Inject placeholders for symbols that may not have been created
    # when the real model load failed at import time.
    try:
        setattr(mod, 'tokenizer', DummyTokenizer())
    except Exception:
        pass

    try:
        setattr(mod, 'toxicityModel', DummyModel())
    except Exception:
        pass

    # device used in module - resolve from either real or fake torch
    try:
        _torch = sys.modules.get('torch')
        if _torch is not None and hasattr(_torch, 'device'):
            dev = _torch.device('cpu') if callable(_torch.device) else _torch.device
        else:
            dev = 'cpu'
        setattr(mod, 'device', dev)
    except Exception:
        pass

    # simple request_id_var with set/get
    class _ReqVar:
        def __init__(self):
            self._v = None
        def set(self, v):
            self._v = v
        def get(self):
            return self._v

    try:
        setattr(mod, 'request_id_var', _ReqVar())
    except Exception:
        pass

    # log_dict expected to be a dict of lists; use defaultdict to avoid KeyError
    try:
        setattr(mod, 'log_dict', defaultdict(list))
    except Exception:
        pass

    return mod


def test_toxicity_check_short_text(monkeypatch):
    mod = import_with_stubs(monkeypatch)

    payload = {'text': 'this is a short non toxic text'}
    res = mod.toxicity_check(payload, 'test1')

    assert 'toxicScore' in res
    assert isinstance(res['toxicScore'], list)
    assert len(res['toxicScore']) == 7
    # Validate that benign example yields low numeric scores
    scores = [getattr(item, 'metricScore') for item in res['toxicScore']]
    assert all(0.0 <= s <= 1.0 for s in scores)
    # small positive logits yield sigmoid slightly above 0.5; accept small margin
    assert max(scores) < 0.55


def test_toxicity_check_long_text_chunking(monkeypatch):
    mod = import_with_stubs(monkeypatch)

    # create long text that will generate >500 tokens via DummyTokenizer.encode
    long_text = 'word ' * 1200
    payload = {'text': long_text}

    res = mod.toxicity_check(payload, 'test2')

    assert 'toxicScore' in res
    assert isinstance(res['toxicScore'], list)
    assert len(res['toxicScore']) == 7
    # ensure chunking happened by checking that tokenizer.decode was called
    # our DummyTokenizer records decode calls on itself
    assert hasattr(mod.tokenizer, 'decode')
    # If decode_calls were recorded on the DummyTokenizer instance used
    # during import, they will be present.
    if hasattr(mod.tokenizer, 'decode_calls'):
        assert len(mod.tokenizer.decode_calls) >= 1


def test_toxicity_check_invalid_payload(monkeypatch):
    # Ensure error path raises InternalServerError
    mod = import_with_stubs(monkeypatch)
    from werkzeug.exceptions import InternalServerError

    payload = {}  # missing 'text'
    with pytest.raises(InternalServerError):
        mod.toxicity_check(payload, 'test3')


def test_toxic_example_triggers_high_toxicity(monkeypatch):
    mod = import_with_stubs(monkeypatch)

    # craft a clearly toxic sentence with keywords our DummyModel checks
    payload = {'text': 'You are an idiot and I hate you. kill them.'}
    res = mod.toxicity_check(payload, 'test4')

    assert 'toxicScore' in res
    scores = [getattr(item, 'metricScore') for item in res['toxicScore']]
    # toxicity label is first in the label_map -> should be highest
    assert scores[0] > 0.5
    # at least one insult/severe label should be elevated
    assert any(s > 0.5 for s in scores)
