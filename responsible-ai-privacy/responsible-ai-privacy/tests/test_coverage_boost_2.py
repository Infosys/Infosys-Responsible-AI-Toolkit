"""
Targeted coverage-boost tests for several small uncovered branches.

Targets:
  - auth_jwt.py lines 46-49        (except Exception branch)
  - auth_client_id.py lines 88-90  (except Exception branch)
  - fakeData.py lines 39-44        (text in ent_value True branch)
  - lemma_context_aware_enhancer1.py lines 208-213 (else: create EnhancedAnalysisExplanation)
"""
import sys
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import ExpiredSignatureError, JWTError

# Capture real modules NOW (at collection time) before test_routing_coverage_boost.py
# replaces them in sys.modules with MagicMocks.


# ============================================================
# auth_jwt.py — lines 46-49 (except Exception branch)
# ============================================================

class TestAuthJWTExceptionBranch:
    def test_unexpected_exception_raises_http_500(self):
        """Generic Exception in jwt.decode hits lines 46-49, returns HTTP 500."""
        from privacy.util.auth.auth_jwt import authenticate_jwt

        credentials = MagicMock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = "some.token"

        with patch("privacy.util.auth.auth_jwt.jwt.decode",
                   side_effect=RuntimeError("disk read error")):
            with pytest.raises(HTTPException) as exc_info:
                authenticate_jwt(credentials)

        assert exc_info.value.status_code == 500
        assert "Unexpected error" in exc_info.value.detail

    def test_value_error_hits_exception_branch(self):
        """ValueError (not a JWT exception) also hits lines 46-49."""
        from privacy.util.auth.auth_jwt import authenticate_jwt

        credentials = MagicMock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = "other.token"

        with patch("privacy.util.auth.auth_jwt.jwt.decode",
                   side_effect=ValueError("unexpected")):
            with pytest.raises(HTTPException) as exc_info:
                authenticate_jwt(credentials)

        assert exc_info.value.status_code == 500


# ============================================================
# auth_client_id.py — lines 88-90 (except Exception branch)
# ============================================================

class TestAuthClientIdExceptionBranch:
    def test_connection_error_from_get_public_keys_hits_exception_branch(self):
        """ConnectionError from get_public_keys hits lines 88-90, returns HTTP 500."""
        from privacy.util.auth.auth_client_id import authenticate_client_id

        credentials = MagicMock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = "some.token"

        with patch("privacy.util.auth.auth_client_id.get_public_keys",
                   side_effect=ConnectionError("network error")):
            with pytest.raises(HTTPException) as exc_info:
                authenticate_client_id(credentials)

        assert exc_info.value.status_code == 500
        assert "Unexpected error" in exc_info.value.detail

    def test_runtime_error_hits_exception_branch(self):
        """RuntimeError from get_public_keys hits lines 88-90."""
        from privacy.util.auth.auth_client_id import authenticate_client_id

        credentials = MagicMock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = "some.token"

        with patch("privacy.util.auth.auth_client_id.get_public_keys",
                   side_effect=RuntimeError("service unavailable")):
            with pytest.raises(HTTPException) as exc_info:
                authenticate_client_id(credentials)

        assert exc_info.value.status_code == 500


# ============================================================
# fakeData.py — lines 39-44 (text in ent_value is True)
# ============================================================

class TestFakeDataTextInEntValue:
    def test_text_in_ent_value_with_different_choice(self):
        """
        When text IS in ent_value AND secrets.choice returns a different value,
        lines 39-44 execute: update fake_dict, remove chosen item, break.
        """
        from privacy.util.special_recognizers.fakeData import FakeDataGenerate

        generator = FakeDataGenerate()

        result = MagicMock()
        result.entity_type = "COMPANY"
        result.start = 0
        result.end = 7  # "Infosys"
        result.analysis_explanation = None

        input_text = "Infosys is a company"
        results = [result]

        # text = input_text[0:7] = "Infosys"
        # ent_value = ["Infosys", "Wipro", "TCS"]
        # "Infosys" in ent_value → True (line 39)
        # secrets.choice returns "Wipro" which != "infosys" → lines 42-44 execute
        session_data = {"COMPANY": ["Infosys", "Wipro", "TCS"]}

        with patch("privacy.util.special_recognizers.fakeData.hasattr", return_value=False), \
             patch("privacy.util.special_recognizers.fakeData.get_session_dict",
                   return_value=session_data), \
             patch("privacy.util.special_recognizers.fakeData.secrets.choice",
                   return_value="Wipro"):
            fake_dict = generator.fake_data_generation(results, input_text)

        assert "COMPANY" in fake_dict

    def test_text_in_ent_value_same_choice_then_different(self):
        """
        When secrets.choice first returns same as input (loop again),
        then returns different — lines 39-44 still covered on second iteration.
        """
        from privacy.util.special_recognizers.fakeData import FakeDataGenerate

        generator = FakeDataGenerate()

        result = MagicMock()
        result.entity_type = "BRAND"
        result.start = 0
        result.end = 4  # "Nike"
        result.analysis_explanation = None

        input_text = "Nike shoes"
        results = [result]

        session_data = {"BRAND": ["Nike", "Adidas", "Puma"]}

        # First call returns "Nike" (same as input → loop again)
        # Second call returns "Adidas" (different → exit loop at line 44)
        with patch("privacy.util.special_recognizers.fakeData.hasattr", return_value=False), \
             patch("privacy.util.special_recognizers.fakeData.get_session_dict",
                   return_value=session_data), \
             patch("privacy.util.special_recognizers.fakeData.secrets.choice",
                   side_effect=["Nike", "Adidas"]):
            fake_dict = generator.fake_data_generation(results, input_text)

        assert "BRAND" in fake_dict


# ============================================================
# lemma_context_aware_enhancer1.py — lines 208-213
# (else: analysis_explanation has no set_supportive_context_word)
# ============================================================

class TestLemmaContextEnhancerElseBranch:
    def test_analysis_explanation_none_hits_else_branch(self):
        """
        Covers lines 208-213: the else branch when analysis_explanation lacks
        set_supportive_context_word.

        Flow:
          1. result.analysis_explanation = None → line 196 creates first
             EnhancedAnalysisExplanation (mock_no_method, spec=['set_improved_score'])
          2. hasattr(mock_no_method, 'set_supportive_context_word') → False → else at 206
          3. Lines 208-212 create second EnhancedAnalysisExplanation (mock_with_method)
          4. Line 213 calls mock_with_method.set_supportive_context_word(...)

        Both EnhancedAnalysisExplanation calls are patched so the real MagicMock
        (whose state could leak to later tests) is never actually called.
        """
        from presidio_analyzer import RecognizerResult
        from privacy.util.lemma_context_aware_enhancer1 import LemmaContextAwareEnhancer

        enhancer = LemmaContextAwareEnhancer()
        text = "My email is john@example.com"

        result = MagicMock()
        result.recognition_metadata = MagicMock()
        result.recognition_metadata.keys.return_value = [
            RecognizerResult.RECOGNIZER_IDENTIFIER_KEY
        ]
        result.recognition_metadata.__getitem__.return_value = "email_recognizer"
        result.recognition_metadata.get.return_value = False
        result.score = 0.5
        result.start = 12
        result.analysis_explanation = None  # triggers creation at line 196

        recognizer = MagicMock()
        recognizer.id = "email_recognizer"
        recognizer.context = ["email"]
        recognizer.__class__.__name__ = "EmailRecognizer"

        nlp_artifacts = MagicMock()

        # First call returns a mock WITHOUT set_supportive_context_word → else branch (208)
        # Second call returns a mock WITH set_supportive_context_word → line 213 executes
        mock_no_method = MagicMock(spec=["set_improved_score"])  # no set_supportive_context_word
        mock_with_method = MagicMock()  # has set_supportive_context_word

        with patch(
            "privacy.util.lemma_context_aware_enhancer1.EnhancedAnalysisExplanation",
            side_effect=[mock_no_method, mock_with_method],
        ), patch(
            "privacy.util.lemma_context_aware_enhancer1.is_data_near_word",
            return_value=True,
        ):
            results = enhancer.enhance_using_context(
                text=text,
                raw_results=[result],
                nlp_artifacts=nlp_artifacts,
                recognizers=[recognizer],
                context=[],
            )

        assert len(results) == 1
        assert results[0].analysis_explanation is not None
        mock_with_method.set_supportive_context_word.assert_called_once()
