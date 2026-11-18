"""
Extra tests for json_service.py targeting missing coverage lines:
  - process_dict with acc_name (lines 106-144): ApiCall returns None / 404
  - process_list with acc_name (lines 179-217): ApiCall returns None / 404
  - reconstruct_json digit key path (lines 257-262)
  - anonymize_json exception path (line 78)
"""
import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_engines():
    batch_analyzer = MagicMock()
    batch_anonymizer = MagicMock()
    batch_anonymizer.anonymize_dict.return_value = {}
    return batch_analyzer, batch_anonymizer


ACC_NAME = {"portfolio": "test_portfolio", "account": "test_account"}


# ---------------------------------------------------------------------------
# process_dict — acc_name branch, ApiCall returns None (lines 109-111)
# ---------------------------------------------------------------------------

class TestProcessDictAccNameNoneResponse:
    def test_process_dict_acc_name_api_returns_none(self):
        """process_dict returns None when ApiCall.request returns None (lines 109-111)."""
        from privacy.service.json_service import JSONService
        ba, bana = _mock_engines()
        data = {"records": [{"name": "Alice", "email": "alice@example.com"}]}

        with patch("privacy.service.json_service.ApiCall.request", return_value=None):
            result = JSONService.process_dict(
                data, ba, bana, "en",
                [], ACC_NAME, [], [], 0, None
            )
        assert result is None

    def test_process_dict_acc_name_api_returns_404(self):
        """process_dict returns 404 when ApiCall.request returns 404 (lines 112-114)."""
        from privacy.service.json_service import JSONService
        ba, bana = _mock_engines()
        data = {"records": [{"name": "Bob"}]}

        with patch("privacy.service.json_service.ApiCall.request", return_value=404):
            result = JSONService.process_dict(
                data, ba, bana, "en",
                [], ACC_NAME, [], [], 0, None
            )
        assert result == 404


# ---------------------------------------------------------------------------
# process_list — acc_name branch, ApiCall returns None / 404 (lines 182-187)
# ---------------------------------------------------------------------------

class TestProcessListAccNameApiResponse:
    def test_process_list_acc_name_api_returns_none(self):
        """process_list returns None when ApiCall.request returns None (lines 183-184)."""
        from privacy.service.json_service import JSONService
        ba, bana = _mock_engines()
        data = [{"name": "Charlie", "ssn": "123-45-6789"}]

        with patch("privacy.service.json_service.ApiCall.request", return_value=None):
            result = JSONService.process_list(
                data, ba, bana, "en",
                [], ACC_NAME, [], [], 0, None
            )
        assert result is None

    def test_process_list_acc_name_api_returns_404(self):
        """process_list returns 404 when ApiCall.request returns 404 (lines 185-187)."""
        from privacy.service.json_service import JSONService
        ba, bana = _mock_engines()
        data = [{"name": "Diana"}]

        with patch("privacy.service.json_service.ApiCall.request", return_value=404):
            result = JSONService.process_list(
                data, ba, bana, "en",
                [], ACC_NAME, [], [], 0, None
            )
        assert result == 404

    def test_process_list_non_dict_items_pass_through(self):
        """process_list appends non-dict items unchanged (line 225)."""
        from privacy.service.json_service import JSONService
        ba, bana = _mock_engines()
        data = ["plain string", 42, None]

        result = JSONService.process_list(
            data, ba, bana, "en",
            [], None, [], None, 0, None
        )
        assert result == ["plain string", 42, None]


# ---------------------------------------------------------------------------
# reconstruct_json — digit key path (lines 257-262)
# ---------------------------------------------------------------------------

class TestReconstructJsonDigitPath:
    def test_reconstruct_json_with_digit_part(self):
        """Digit part in flattened key triggers list creation (lines 257-262)."""
        from privacy.service.json_service import JSONService
        flattened = {"0_name": "Alice", "0_age": "30"}
        result = JSONService.reconstruct_json(flattened)
        assert isinstance(result, dict)

    def test_reconstruct_json_list_input(self):
        """reconstruct_json with list input recurses over items (line 250)."""
        from privacy.service.json_service import JSONService
        input_list = [{"key": "value"}, "plain"]
        result = JSONService.reconstruct_json(input_list)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_reconstruct_json_plain_dict(self):
        """reconstruct_json with a flat dict returns the same mapping."""
        from privacy.service.json_service import JSONService
        flattened = {"name": "Alice", "city": "London"}
        result = JSONService.reconstruct_json(flattened)
        assert result.get("name") == "Alice"
        assert result.get("city") == "London"

    def test_reconstruct_json_nested_string_keys(self):
        """reconstruct_json rebuilds nested structure from underscore-split keys."""
        from privacy.service.json_service import JSONService
        flattened = {"person_name": "Eve", "person_age": "28"}
        result = JSONService.reconstruct_json(flattened)
        assert "person" in result
        assert result["person"]["name"] == "Eve"


# ---------------------------------------------------------------------------
# anonymize_json — exception path (line 78-79)
# ---------------------------------------------------------------------------

class TestAnonymizeJsonExceptionPath:
    def test_anonymize_json_raises_on_invalid_file(self):
        """anonymize_json catches exception and raises RuntimeError (lines 77-79)."""
        from privacy.service.json_service import JSONService
        mock_file = MagicMock()
        mock_file.file.read.side_effect = ValueError("broken file")

        payload = MagicMock()
        payload.portfolio = None
        payload.account = None
        payload.__getitem__ = lambda self, k: {
            "file": mock_file,
            "keys_to_skip": [],
            "pii_entities_to_be_redacted": None,
            "score_threshold": None,
            "nlp": None,
        }.get(k)
        payload.exclusion = None

        with patch("privacy.service.json_service.json.load", side_effect=ValueError("bad json")):
            with pytest.raises(RuntimeError):
                JSONService.anonymize_json({
                    "portfolio": None,
                    "account": None,
                    "file": mock_file,
                    "keys_to_skip": [],
                    "pii_entities_to_be_redacted": None,
                    "score_threshold": None,
                    "nlp": None,
                    "exclusion": None,
                })


# ---------------------------------------------------------------------------
# process_dict — acc_name=None, pii_entities_to_be_redacted not None (lines 96-101)
# ---------------------------------------------------------------------------

class TestProcessDictPIIEntitiesNotNone:
    def test_process_dict_with_pii_entities_list(self):
        """process_dict with pii_entities_to_be_redacted calls analyze_dict with entities."""
        from privacy.service.json_service import JSONService
        ba, bana = _mock_engines()
        ba.analyze_dict.return_value = iter([])
        bana.anonymize_dict.return_value = {}

        data = {"records": [{"name": "Frank"}]}

        result = JSONService.process_dict(
            data, ba, bana, "en",
            [], None, [], ["PERSON"], 0, None
        )
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# flatten_json — verify utility (already covered but adding sanity tests)
# ---------------------------------------------------------------------------

class TestFlattenJson:
    def test_flatten_nested_dict(self):
        """flatten_json converts nested dict to flat key-value pairs."""
        from privacy.service.json_service import JSONService
        nested = {"a": {"b": {"c": 1}}}
        result = JSONService.flatten_json(nested)
        assert result == {"a_b_c": 1}

    def test_flatten_list_within_dict(self):
        """flatten_json handles lists within dicts."""
        from privacy.service.json_service import JSONService
        data = {"items": [{"name": "x"}, {"name": "y"}]}
        result = JSONService.flatten_json(data)
        assert "items_0_name" in result
        assert result["items_0_name"] == "x"

    def test_flatten_scalar_value(self):
        """flatten_json handles plain scalar values."""
        from privacy.service.json_service import JSONService
        data = {"key": "value"}
        result = JSONService.flatten_json(data)
        assert result == {"key": "value"}
