import pytest
import importlib
import sys
from types import SimpleNamespace

ROOT_SRC = None

def _reload_service():
    # Ensure src is importable (conftest handles sys.path)
    # Make sure a robust transformers stub exists in sys.modules before import
    import types as _types
    # Force-inject a torch stub to satisfy torch.cuda and torch.device checks used at import-time
    torch_mod = _types.ModuleType('torch')
    class _FakeDevice:
        def __init__(self, name):
            self.name = name
        def __repr__(self):
            return f"_FakeDevice({self.name})"
    torch_mod.cuda = _types.SimpleNamespace(is_available=lambda: False)
    torch_mod.device = lambda name: _FakeDevice(name)
    # provide minimal attributes used elsewhere
    torch_mod.nn = _types.SimpleNamespace()
    sys.modules['torch'] = torch_mod

    # Force-inject a transformers stub to avoid import-time issues with the real package
    tmod = _types.ModuleType('transformers')
    def fake_pipeline(task=None, model=None, tokenizer=None, **kwargs):
        return lambda urls: [[{"label": "benign", "score": 0.1}] for _ in urls]
    class _Model:
        def to(self, device):
            return self
    class _AutoSeq:
        @staticmethod
        def from_pretrained(path, local_files_only=True):
            return _Model()
    class _AutoTok:
        @staticmethod
        def from_pretrained(path, local_files_only=True):
            return object()
    tmod.pipeline = fake_pipeline
    tmod.AutoModelForSequenceClassification = _AutoSeq
    tmod.AutoTokenizer = _AutoTok
    sys.modules['transformers'] = tmod

    return importlib.reload(importlib.import_module('profanity.service.malicious_url_service'))


def test_scan_no_url():
    mod = _reload_service()
    svc = mod.MaliciousUrlService()
    req = mod.MaliciousURLAnalyzeRequest(inputText='no urls here', maliciousThreshold=0.5)
    res = svc.scan(req)
    assert res['result'] == 'UNMODERATED'
    assert res['scoreList'] == []


def test_scan_benign_url(monkeypatch):
    mod = _reload_service()
    # monkeypatch module-level nlp to return benign label
    def fake_nlp(urls):
        return [[{"label": "benign", "score": 0.1}] for _ in urls]

    monkeypatch.setattr(mod, 'nlp', fake_nlp)
    svc = mod.MaliciousUrlService()
    req = mod.MaliciousURLAnalyzeRequest(inputText='visit http://example.com', maliciousThreshold=0.5)
    res = svc.scan(req)
    assert res['result'] == 'PASSED'
    assert res['scoreList'] == []


def test_scan_malicious_url(monkeypatch):
    mod = _reload_service()

    # Return a malicious label with high score
    def fake_nlp(urls):
        return [[{"label": "phishing", "score": 0.9}] for _ in urls]

    monkeypatch.setattr(mod, 'nlp', fake_nlp)
    svc = mod.MaliciousUrlService()
    req = mod.MaliciousURLAnalyzeRequest(inputText='click http://bad.example', maliciousThreshold=0.5)
    res = svc.scan(req)
    assert res['result'] == 'FAILED'
    assert len(res['scoreList']) == 1
    assert 'phishing' in list(res['scoreList'][0]['scores'].keys())
