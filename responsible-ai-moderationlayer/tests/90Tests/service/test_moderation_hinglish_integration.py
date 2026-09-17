'''
MIT License
https://mit-license.org/
Copyright © 2026 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import sys
import types
import pytest
from unittest.mock import MagicMock

# Stub translate dependency — same convention as
# tests/90Tests/service/test_service_phases_consolidated.py, extended
# with normalize_hinglish so importing this stub doesn't break the new
# branch in service.py.
dummy_translate = types.ModuleType("translate")


class _DummyTranslate:
    def __init__(self, *_, **__):
        pass

    @staticmethod
    def translate(text):
        return text, "en"

    @staticmethod
    def azure_translate(text):
        return text, "en"

    @staticmethod
    def normalize_hinglish(text):
        return text


dummy_translate.Translate = _DummyTranslate
sys.modules.setdefault("translate", dummy_translate)

from src.service import service as svc


def create_moderation_payload(prompt):
    return svc.AttributeDict({
        "Prompt": prompt,
        "lotNumber": "12345",
        "AccountName": "TestAccount",
        "PortfolioName": "TestPortfolio",
        "ModerationChecks": ["PromptInjection", "Toxicity"],
        "ModerationCheckThresholds": {
            "PromptinjectionThreshold": 0.8,
            "ToxicityThresholds": {"ToxicityThreshold": 0.5},
            "CustomTheme": {"ThemeTexts": [], "Themethresold": 0.8},
        },
    })


def create_mock_moderation_obj():
    mock_obj = {}
    for key in (
        "Prompt Injection Check", "Jailbreak Check", "Privacy Check",
        "Profanity Check", "Toxicity Check", "Restricted Topic Check",
        "Custom Theme Check", "Text Quality Check", "Refusal Check",
        "Sentiment Check", "Invisible Text Check", "Gibberish Check",
        "Ban Code Check", "summary",
    ):
        mock_obj[key] = MagicMock()
    mock_obj["time check"] = {}
    mock_obj["model time"] = {}
    return mock_obj


class TestModerationHinglishIntegration:
    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch):
        svc.log_dict[svc.request_id_var.get()] = []
        svc.dictcheck = {"Prompt Injection Check": "0s"}
        svc.dict_timecheck = {
            "requestModeration": {},
            "responseModeration": {},
            "OpenAIInteractionTime": "0s",
            "translate": "0s",
        }
        monkeypatch.setattr(svc, "cache_flag", False)

    def test_hinglish_flagged_text_gets_normalized_before_checks(self, monkeypatch):
        payload = create_moderation_payload("kya haal hai")
        mock_obj = create_mock_moderation_obj()
        monkeypatch.setattr(svc, "callModerationModels", lambda *a, **k: mock_obj)
        monkeypatch.setattr(svc, "looks_like_hinglish", lambda text: True)

        mock_translate = MagicMock()
        mock_translate.normalize_hinglish = MagicMock(return_value="normalized english text")
        monkeypatch.setattr(svc, "Translate", mock_translate)

        captured = {}
        real_call_models = svc.callModerationModels
        def capturing_call_models(text, *args, **kwargs):
            captured["text"] = text
            return real_call_models(text, *args, **kwargs)
        monkeypatch.setattr(svc, "callModerationModels", capturing_call_models)

        svc.moderation.completions(payload, {}, "gpt4", None, [], None)

        mock_translate.normalize_hinglish.assert_called_once_with("kya haal hai")
        assert captured["text"] == "normalized english text"

    def test_non_hinglish_text_passes_through_unchanged(self, monkeypatch):
        payload = create_moderation_payload("hello how are you")
        mock_obj = create_mock_moderation_obj()
        monkeypatch.setattr(svc, "looks_like_hinglish", lambda text: False)

        mock_translate = MagicMock()
        monkeypatch.setattr(svc, "Translate", mock_translate)

        captured = {}
        def capturing_call_models(text, *args, **kwargs):
            captured["text"] = text
            return mock_obj
        monkeypatch.setattr(svc, "callModerationModels", capturing_call_models)

        svc.moderation.completions(payload, {}, "gpt4", None, [], None)

        mock_translate.normalize_hinglish.assert_not_called()
        assert captured["text"] == "hello how are you"

    def test_explicit_translate_flag_takes_precedence_over_hinglish_detection(self, monkeypatch):
        # Even if the text WOULD be flagged as Hinglish, an explicit
        # translate= flag from the caller wins — normalize_hinglish must
        # not also run.
        payload = create_moderation_payload("kya haal hai")
        mock_obj = create_mock_moderation_obj()
        monkeypatch.setattr(svc, "looks_like_hinglish", lambda text: True)
        monkeypatch.setattr(svc, "callModerationModels", lambda *a, **k: mock_obj)

        mock_translate = MagicMock()
        mock_translate.azure_translate = MagicMock(return_value=("azure translated text", "Hindi"))
        monkeypatch.setattr(svc, "Translate", mock_translate)

        svc.moderation.completions(payload, {}, "gpt4", None, [], "azure")

        mock_translate.normalize_hinglish.assert_not_called()
        mock_translate.azure_translate.assert_called_once()

    def test_explicit_non_recognized_translate_value_also_skips_detection(self, monkeypatch):
        # Any explicit translate= value (not just "google"/"azure") must be
        # respected and skip automatic Hinglish detection — the spec's
        # explicit non-goal is "no change to the existing opt-in translate
        # flag's behavior when explicitly set by a caller."
        payload = create_moderation_payload("kya haal hai")
        mock_obj = create_mock_moderation_obj()
        monkeypatch.setattr(svc, "looks_like_hinglish", lambda text: True)
        monkeypatch.setattr(svc, "callModerationModels", lambda *a, **k: mock_obj)

        mock_translate = MagicMock()
        monkeypatch.setattr(svc, "Translate", mock_translate)

        svc.moderation.completions(payload, {}, "gpt4", None, [], "no")

        mock_translate.normalize_hinglish.assert_not_called()
