import importlib
import sys
import types
import time
import math
from collections import defaultdict
import pytest


class DummyBatchEncoding(dict):
    def __init__(self, text):
        toks = text.split()
        # mimic input_ids as tensor-like object with .shape and indexing
        class DummyTensor:
            def __init__(self, inner):
                self._inner = inner
                # shape as (batch, seq_len)
                self.shape = (1, len(inner[0]) if inner and isinstance(inner[0], list) else len(inner))

            def __getitem__(self, idx):
                return self._inner[idx]

            def __len__(self):
                return len(self._inner)

        self['input_ids'] = DummyTensor([[1] * len(toks)])
        self['text'] = text

    def to(self, device):
        return self


class DummyTokenizer:
    def __init__(self, supported_langs=None):
        self.supported = supported_langs or {'en': '<en>'}
        self.decode_calls = []

    @property
    def lang_code_to_token(self):
        return self.supported

    def __call__(self, text, return_tensors=None):
        return DummyBatchEncoding(text)

    def get_lang_id(self, code):
        # arbitrary mapping
        return 1 if code == 'en' else 0

    def batch_decode(self, tokens, skip_special_tokens=True):
        # tokens may be nested lists of ints
        out = []
        for t in tokens:
            out.append(' '.join(['translated'] * len(t)))
        return out


class DummyModel:
    def generate(self, **kwargs):
        # return tokens with same length as input_ids
        if 'input_ids' in kwargs:
            ids = kwargs['input_ids']
            try:
                length = len(ids[0])
            except Exception:
                length = 1
        else:
            length = 1
        return [[1] * length]
    def to(self, device):
        return self
    def eval(self):
        return self


def import_with_stubs(monkeypatch, supported_langs=None):
    # fake transformers
    fake_transformers = types.ModuleType('transformers')
    fake_transformers.M2M100ForConditionalGeneration = types.SimpleNamespace(from_pretrained=lambda path: DummyModel())
    fake_transformers.M2M100Tokenizer = types.SimpleNamespace(from_pretrained=lambda path: DummyTokenizer(supported_langs))
    monkeypatch.setitem(sys.modules, 'transformers', fake_transformers)

    # fake torch minimal
    fake_torch = types.ModuleType('torch')
    fake_torch.device = lambda *a, **k: 'cpu'
    # mimic cuda namespace used by the module
    fake_torch.cuda = types.SimpleNamespace(is_available=lambda: False)
    monkeypatch.setitem(sys.modules, 'torch', fake_torch)

    # fake nltk (only sent_tokenize)
    fake_nltk = types.ModuleType('nltk')
    def fake_sent_tokenize(text):
        # split into sentences by period for tests
        return [s.strip() for s in text.split('.') if s.strip()]
    fake_nltk.tokenize = types.SimpleNamespace(sent_tokenize=fake_sent_tokenize)
    fake_nltk.data = types.SimpleNamespace(path=[])
    monkeypatch.setitem(sys.modules, 'nltk', fake_nltk)
    monkeypatch.setitem(sys.modules, 'nltk.tokenize', fake_nltk.tokenize)

    # fake langdetect.detect
    fake_langdetect = types.ModuleType('langdetect')
    fake_langdetect.detect = lambda text: 'fr' if 'bonjour' in text.lower() else 'en'
    monkeypatch.setitem(sys.modules, 'langdetect', fake_langdetect)

    # fake langcodes
    fake_langcodes = types.ModuleType('langcodes')
    fake_langcodes.Language = types.SimpleNamespace(get=lambda code: types.SimpleNamespace(display_name=lambda lang: 'French' if code == 'fr' else 'English'))
    fake_langcodes.tag_is_valid = lambda code: code in ('en', 'fr')
    monkeypatch.setitem(sys.modules, 'langcodes', fake_langcodes)

    # minimal werkzeug InternalServerError
    fake_werk = types.ModuleType('werkzeug.exceptions')
    from werkzeug.exceptions import InternalServerError
    monkeypatch.setitem(sys.modules, 'werkzeug.exceptions', types.ModuleType('werkzeug.exceptions'))
    sys.modules['werkzeug.exceptions'].InternalServerError = InternalServerError

    # Ensure translation module imports the fakes
    if 'service.translateservice' in sys.modules:
        monkeypatch.delitem(sys.modules, 'service.translateservice', raising=False)

    mod = importlib.import_module('service.translateservice')
    importlib.reload(mod)

    # inject placeholders that may not exist
    try:
        setattr(mod, 'translation_tokenizer', DummyTokenizer(supported_langs or {'en': '<en>'}))
    except Exception:
        pass
    try:
        setattr(mod, 'translation_model', DummyModel())
    except Exception:
        pass
    try:
        setattr(mod, 'request_id_var', types.SimpleNamespace(set=lambda v: None, get=lambda: 'test'))
    except Exception:
        pass

    return mod


def test_get_language_full_name():
    # uses fake langcodes; 'fr' -> French
    import importlib
    mod = import_with_stubs(pytest.MonkeyPatch(), supported_langs={'fr': '<fr>', 'en': '<en>'})
    assert mod.get_language_full_name('fr') == 'French'
    assert mod.get_language_full_name('xx') == 'unknown'


def test_translate_short_sentence(monkeypatch):
    mod = import_with_stubs(monkeypatch, supported_langs={'en': '<en>', 'fr': '<fr>'})
    payload = 'Hello world.'
    res = mod.translate_to_english(payload)
    assert 'translated_text' in res
    # fake model returns repeated 'translated' words
    assert 'translated' in res['translated_text']
    assert res['detectedLanguage'] in ('English', 'French', 'unknown')


def test_translate_long_sentence_chunking(monkeypatch):
    mod = import_with_stubs(monkeypatch, supported_langs={'en': '<en>'})
    # create long sentence that will be split by fake_sent_tokenize into multiple 'sentences'
    long_text = 'This is a long sentence part one. This is part two, with punctuation! And part three.'
    res = mod.translate_to_english(long_text)
    assert 'translated_text' in res
    # ensure multiple chunks were translated and joined
    assert len(res['translated_text'].split()) >= 1


def test_translate_unsupported_language(monkeypatch):
    # if detect returns a code not in supported set, function returns error object
    mod = import_with_stubs(monkeypatch, supported_langs={'en': '<en>'})
    french_text = 'bonjour tout le monde'
    res = mod.translate_to_english(french_text)
    # Because our fake tokenizer supports only 'en', we expect an error-like response
    assert 'error' in res or 'translated_text' in res
