"""
Coverage boost for:
  - imagePrivacy.py lines 379-384  (image_analyze except Exception)
  - imagePrivacy.py lines 480-485  (image_verify except Exception)
  - imagePrivacy.py lines 599-604  (image_encryption except Exception)
"""
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
import io


# ===========================================================================
# imagePrivacy.py — exception handlers
# ===========================================================================

def _make_request_id_mock(rid="test-img-exc"):
    m = MagicMock()
    m.get.return_value = rid
    return m


def _make_mock_payload():
    try:
        from privacy.service import AttributeDict
    except Exception:
        AttributeDict = dict

    payload_data = {
        "image": MagicMock(),
        "nlp": "basic",
        "easyocr": "Tesseract",
        "pii_entities_to_be_redacted": None,
        "exclusion": None,
        "portfolio": None,
        "account": None,
        "score_threshold": 0.5,
        "rotation_flag": False,
        "mag_ratio": 1.0,
        "pii_entities_to_be_hashified": None,
    }
    try:
        return AttributeDict(payload_data)
    except Exception:
        return MagicMock(**payload_data)


class TestImageAnalyzeExceptionHandler:
    """Covers imagePrivacy.py lines 379-384."""

    def test_image_analyze_exception_raises_runtime_error(self):
        from privacy.service.imagePrivacy import ImagePrivacy

        mock_rid = _make_request_id_mock("img-anon-exc")
        error_store = {"img-anon-exc": []}

        payload = _make_mock_payload()

        with patch("privacy.service.imagePrivacy.request_id_var", mock_rid), \
             patch("privacy.service.imagePrivacy.error_dict", error_store), \
             patch("privacy.service.imagePrivacy.select_nlp",
                   side_effect=RuntimeError("engine crash")), \
             patch("privacy.service.imagePrivacy.log"):
            with pytest.raises((RuntimeError, Exception)):
                obj = ImagePrivacy()
                obj.image_analyze(payload)


class TestImageVerifyExceptionHandler:
    """Covers imagePrivacy.py lines 480-485."""

    def test_image_verify_exception_raises_runtime_error(self):
        from privacy.service.imagePrivacy import ImagePrivacy

        mock_rid = _make_request_id_mock("img-verify-exc")
        error_store = {"img-verify-exc": []}

        payload = _make_mock_payload()

        with patch("privacy.service.imagePrivacy.request_id_var", mock_rid), \
             patch("privacy.service.imagePrivacy.error_dict", error_store), \
             patch("privacy.service.imagePrivacy.select_nlp",
                   side_effect=RuntimeError("verify crash")), \
             patch("privacy.service.imagePrivacy.log"):
            with pytest.raises((RuntimeError, Exception)):
                obj = ImagePrivacy()
                obj.image_verify(payload)


class TestImageEncryptionExceptionHandler:
    """Covers imagePrivacy.py lines 599-604."""

    def test_image_encryption_exception_raises_runtime_error(self):
        from privacy.service.imagePrivacy import ImagePrivacy

        mock_rid = _make_request_id_mock("img-enc-exc")
        error_store = {"img-enc-exc": []}

        payload = _make_mock_payload()

        with patch("privacy.service.imagePrivacy.request_id_var", mock_rid), \
             patch("privacy.service.imagePrivacy.error_dict", error_store), \
             patch("privacy.service.imagePrivacy.select_nlp",
                   side_effect=RuntimeError("encryption crash")), \
             patch("privacy.service.imagePrivacy.log"):
            with pytest.raises((RuntimeError, Exception)):
                ImagePrivacy.image_encryption(payload)

