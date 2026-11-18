"""
Test suite for PII detection utilities.
Tests postprocessing and helper functions without heavy dependencies.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from privacy.util.code_detect.pii_detection import postprocess_secrets, scan_pii_batch


class TestPostprocessSecrets:
    """Test the postprocess_secrets function."""
    
    def test_postprocess_secrets_with_secrets(self):
        """Test postprocessing when secrets are found."""
        secrets = [
            {"tag": "EMAIL", "value": "test@example.com", "start": 0, "end": 16},
            {"tag": "IP_ADDRESS", "value": "192.168.1.1", "start": 20, "end": 31}
        ]
        
        matches, has_secrets = postprocess_secrets(secrets)
        
        assert has_secrets is True
        assert isinstance(matches, str)
        
        # Parse JSON to verify structure
        parsed = json.loads(matches)
        assert len(parsed) == 2
        assert parsed[0]["tag"] == "EMAIL"
        assert parsed[1]["tag"] == "IP_ADDRESS"
    
    def test_postprocess_secrets_empty_list(self):
        """Test postprocessing with empty secrets list."""
        secrets = []
        
        matches, has_secrets = postprocess_secrets(secrets)
        
        assert has_secrets is False
        assert matches == json.dumps([])
        
        # Verify it's valid JSON
        parsed = json.loads(matches)
        assert parsed == []
    
    def test_postprocess_secrets_none(self):
        """Test postprocessing with None."""
        secrets = None
        
        matches, has_secrets = postprocess_secrets(secrets)
        
        assert has_secrets is False
        assert matches == json.dumps([])
    
    def test_postprocess_secrets_single_secret(self):
        """Test postprocessing with single secret."""
        secrets = [
            {"tag": "KEY", "value": "abcd1234efgh5678", "start": 5, "end": 21}
        ]
        
        matches, has_secrets = postprocess_secrets(secrets)
        
        assert has_secrets is True
        parsed = json.loads(matches)
        assert len(parsed) == 1
        assert parsed[0]["tag"] == "KEY"
        assert parsed[0]["value"] == "abcd1234efgh5678"
    
    def test_postprocess_secrets_multiple_same_type(self):
        """Test postprocessing with multiple secrets of same type."""
        secrets = [
            {"tag": "EMAIL", "value": "user1@test.com", "start": 0, "end": 14},
            {"tag": "EMAIL", "value": "user2@test.com", "start": 20, "end": 34},
            {"tag": "EMAIL", "value": "user3@test.com", "start": 40, "end": 54}
        ]
        
        matches, has_secrets = postprocess_secrets(secrets)
        
        assert has_secrets is True
        parsed = json.loads(matches)
        assert len(parsed) == 3
        assert all(item["tag"] == "EMAIL" for item in parsed)
    
    def test_postprocess_secrets_complex_structure(self):
        """Test postprocessing with complex secret structure."""
        secrets = [
            {
                "tag": "EMAIL",
                "value": "complex@example.com",
                "start": 10,
                "end": 30,
                "score": 0.95,
                "additional_field": "extra_data"
            }
        ]
        
        matches, has_secrets = postprocess_secrets(secrets)
        
        assert has_secrets is True
        parsed = json.loads(matches)
        assert parsed[0]["tag"] == "EMAIL"
        assert "score" in parsed[0]
        assert parsed[0]["score"] == 0.95
    
    def test_postprocess_secrets_json_serializable(self):
        """Test that output is always JSON serializable."""
        test_cases = [
            [],
            [{"tag": "EMAIL", "value": "test@test.com"}],
            [{"tag": "KEY", "start": 0, "end": 10}] * 5,
            None
        ]
        
        for secrets in test_cases:
            matches, has_secrets = postprocess_secrets(secrets)
            # Should not raise exception
            parsed = json.loads(matches)
            assert isinstance(parsed, list)
    
    def test_postprocess_secrets_preserves_order(self):
        """Test that order of secrets is preserved."""
        secrets = [
            {"tag": "EMAIL", "value": "first@test.com", "start": 0, "end": 14},
            {"tag": "KEY", "value": "key123", "start": 20, "end": 26},
            {"tag": "IP_ADDRESS", "value": "10.0.0.1", "start": 30, "end": 38}
        ]
        
        matches, has_secrets = postprocess_secrets(secrets)
        parsed = json.loads(matches)
        
        assert parsed[0]["tag"] == "EMAIL"
        assert parsed[1]["tag"] == "KEY"
        assert parsed[2]["tag"] == "IP_ADDRESS"
    
    def test_postprocess_secrets_boolean_consistency(self):
        """Test that has_secrets boolean is consistent with content."""
        # With secrets
        secrets_with_data = [{"tag": "EMAIL"}]
        _, has_secrets_true = postprocess_secrets(secrets_with_data)
        assert has_secrets_true is True
        
        # Without secrets
        _, has_secrets_false = postprocess_secrets([])
        assert has_secrets_false is False
        
        _, has_secrets_none = postprocess_secrets(None)
        assert has_secrets_none is False


class TestScanPiiBatch:
    """Test the scan_pii_batch function."""
    
    @patch('privacy.util.code_detect.pii_detection.detect_email_addresses')
    @patch('privacy.util.code_detect.pii_detection.detect_keys')
    def test_scan_pii_batch_with_regex_detector(self, mock_detect_keys, mock_detect_email_addresses):
        """Test scan_pii_batch with regex key detector."""
        # Mock detect_email_addresses to return email, IP and KEY
        mock_detect_email_addresses.return_value = [
            {"tag": "EMAIL", "value": "test@example.com", "start": 0, "end": 16},
            {"tag": "IP_ADDRESS", "value": "192.168.1.1", "start": 20, "end": 31},
            {"tag": "KEY", "value": "api_key_123", "start": 35, "end": 46}
        ]
        
        examples = [
            {"content": "Contact test@example.com at 192.168.1.1 with api_key_123"}
        ]
        
        result = scan_pii_batch(examples, key_detector="regex")
        
        # Verify detect_email_addresses was called with correct parameters
        mock_detect_email_addresses.assert_called_once_with(
            "Contact test@example.com at 192.168.1.1 with api_key_123",
            tag_types={"KEY", "EMAIL", "IP_ADDRESS"}
        )
        
        # Verify detect_keys was NOT called for regex detector
        mock_detect_keys.assert_not_called()
        
        # Verify results
        assert len(result["secrets"]) == 1
        assert len(result["has_secrets"]) == 1
        assert len(result["number_secrets"]) == 1
        assert result["has_secrets"][0] is True
        assert result["number_secrets"][0] == 3
        
        # Verify secrets JSON
        secrets_parsed = json.loads(result["secrets"][0])
        assert len(secrets_parsed) == 3
        assert secrets_parsed[0]["tag"] == "EMAIL"
        assert secrets_parsed[1]["tag"] == "IP_ADDRESS"
        assert secrets_parsed[2]["tag"] == "KEY"
    
    @patch('privacy.util.code_detect.pii_detection.detect_email_addresses')
    @patch('privacy.util.code_detect.pii_detection.detect_keys')
    def test_scan_pii_batch_with_other_detector(self, mock_detect_keys, mock_detect_email_addresses):
        """Test scan_pii_batch with 'other' (non-regex) key detector."""
        # Mock detect_email_addresses to return email and IP only
        mock_detect_email_addresses.return_value = [
            {"tag": "EMAIL", "value": "user@test.com", "start": 0, "end": 13}
        ]
        
        # Mock detect_keys to return API keys
        mock_detect_keys.return_value = [
            {"tag": "KEY", "value": "secret_key_abc", "start": 20, "end": 34}
        ]
        
        examples = [
            {"content": "user@test.com has secret_key_abc"}
        ]
        
        result = scan_pii_batch(examples, key_detector="other")
        
        # Verify detect_email_addresses was called with EMAIL and IP_ADDRESS only
        mock_detect_email_addresses.assert_called_once_with(
            "user@test.com has secret_key_abc",
            tag_types={"EMAIL", "IP_ADDRESS"}
        )
        
        # Verify detect_keys was called for non-regex detector
        mock_detect_keys.assert_called_once_with("user@test.com has secret_key_abc")
        
        # Verify results
        assert result["has_secrets"][0] is True
        assert result["number_secrets"][0] == 2
        
        secrets_parsed = json.loads(result["secrets"][0])
        assert len(secrets_parsed) == 2
    
    @patch('privacy.util.code_detect.pii_detection.detect_email_addresses')
    @patch('privacy.util.code_detect.pii_detection.detect_keys')
    def test_scan_pii_batch_no_secrets_found(self, mock_detect_keys, mock_detect_email_addresses):
        """Test scan_pii_batch when no secrets are detected."""
        mock_detect_email_addresses.return_value = []
        mock_detect_keys.return_value = []
        
        examples = [
            {"content": "This is clean text with no PII"}
        ]
        
        result = scan_pii_batch(examples, key_detector="other")
        
        assert result["has_secrets"][0] is False
        assert result["number_secrets"][0] == 0
        
        secrets_parsed = json.loads(result["secrets"][0])
        assert secrets_parsed == []
    
    @patch('privacy.util.code_detect.pii_detection.detect_email_addresses')
    @patch('privacy.util.code_detect.pii_detection.detect_keys')
    def test_scan_pii_batch_multiple_examples(self, mock_detect_keys, mock_detect_email_addresses):
        """Test scan_pii_batch with multiple examples."""
        # Different return values for each call
        mock_detect_email_addresses.side_effect = [
            [{"tag": "EMAIL", "value": "first@test.com"}],
            [],
            [{"tag": "IP_ADDRESS", "value": "10.0.0.1"}]
        ]
        
        mock_detect_keys.side_effect = [
            [],
            [{"tag": "KEY", "value": "key123"}],
            []
        ]
        
        examples = [
            {"content": "First example with first@test.com"},
            {"content": "Second example with key123"},
            {"content": "Third example with 10.0.0.1"}
        ]
        
        result = scan_pii_batch(examples, key_detector="other")
        
        # Verify we got results for all examples
        assert len(result["secrets"]) == 3
        assert len(result["has_secrets"]) == 3
        assert len(result["number_secrets"]) == 3
        
        # First example has email
        assert result["has_secrets"][0] is True
        assert result["number_secrets"][0] == 1
        
        # Second example has key
        assert result["has_secrets"][1] is True
        assert result["number_secrets"][1] == 1
        
        # Third example has IP
        assert result["has_secrets"][2] is True
        assert result["number_secrets"][2] == 1
    
    @patch('privacy.util.code_detect.pii_detection.detect_email_addresses')
    @patch('privacy.util.code_detect.pii_detection.detect_keys')
    def test_scan_pii_batch_mixed_results(self, mock_detect_keys, mock_detect_email_addresses):
        """Test scan_pii_batch with mixed results (some with secrets, some without)."""
        mock_detect_email_addresses.side_effect = [
            [{"tag": "EMAIL", "value": "test@example.com"}],
            []
        ]
        
        mock_detect_keys.side_effect = [
            [{"tag": "KEY", "value": "secret"}],
            []
        ]
        
        examples = [
            {"content": "Has PII: test@example.com and secret"},
            {"content": "Clean text without any PII"}
        ]
        
        result = scan_pii_batch(examples, key_detector="other")
        
        # First example has secrets
        assert result["has_secrets"][0] is True
        assert result["number_secrets"][0] == 2
        
        # Second example has no secrets
        assert result["has_secrets"][1] is False
        assert result["number_secrets"][1] == 0
    
    @patch('privacy.util.code_detect.pii_detection.detect_email_addresses')
    @patch('privacy.util.code_detect.pii_detection.detect_keys')
    def test_scan_pii_batch_default_key_detector(self, mock_detect_keys, mock_detect_email_addresses):
        """Test scan_pii_batch with default key_detector parameter."""
        mock_detect_email_addresses.return_value = []
        mock_detect_keys.return_value = []
        
        examples = [{"content": "Test content"}]
        
        # Call without specifying key_detector (should default to "other")
        result = scan_pii_batch(examples)
        
        # Should use detect_keys (not regex mode)
        mock_detect_keys.assert_called_once()
        mock_detect_email_addresses.assert_called_once_with(
            "Test content",
            tag_types={"EMAIL", "IP_ADDRESS"}
        )
    
    @patch('privacy.util.code_detect.pii_detection.detect_email_addresses')
    @patch('privacy.util.code_detect.pii_detection.detect_keys')
    def test_scan_pii_batch_empty_examples(self, mock_detect_keys, mock_detect_email_addresses):
        """Test scan_pii_batch with empty examples list."""
        examples = []
        
        result = scan_pii_batch(examples, key_detector="other")
        
        assert result["secrets"] == []
        assert result["has_secrets"] == []
        assert result["number_secrets"] == []
        
        # No calls should be made
        mock_detect_keys.assert_not_called()
        mock_detect_email_addresses.assert_not_called()
    
    @patch('privacy.util.code_detect.pii_detection.detect_email_addresses')
    @patch('privacy.util.code_detect.pii_detection.detect_keys')
    def test_scan_pii_batch_multiple_secrets_same_example(self, mock_detect_keys, mock_detect_email_addresses):
        """Test scan_pii_batch with multiple secrets in same example."""
        mock_detect_email_addresses.return_value = [
            {"tag": "EMAIL", "value": "email1@test.com"},
            {"tag": "EMAIL", "value": "email2@test.com"},
            {"tag": "IP_ADDRESS", "value": "192.168.1.1"}
        ]
        
        mock_detect_keys.return_value = [
            {"tag": "KEY", "value": "key1"},
            {"tag": "KEY", "value": "key2"}
        ]
        
        examples = [
            {"content": "Multiple secrets: email1@test.com, email2@test.com, 192.168.1.1, key1, key2"}
        ]
        
        result = scan_pii_batch(examples, key_detector="other")
        
        assert result["has_secrets"][0] is True
        assert result["number_secrets"][0] == 5
        
        secrets_parsed = json.loads(result["secrets"][0])
        assert len(secrets_parsed) == 5
    
    @patch('privacy.util.code_detect.pii_detection.detect_email_addresses')
    @patch('privacy.util.code_detect.pii_detection.detect_keys')
    def test_scan_pii_batch_regex_mode_no_detect_keys(self, mock_detect_keys, mock_detect_email_addresses):
        """Test that regex mode doesn't call detect_keys."""
        mock_detect_email_addresses.return_value = []
        
        examples = [{"content": "Test in regex mode"}]
        
        result = scan_pii_batch(examples, key_detector="regex")
        
        # In regex mode, detect_keys should NOT be called
        mock_detect_keys.assert_not_called()
        
        # But detect_email_addresses should be called with KEY in tag_types
        mock_detect_email_addresses.assert_called_once_with(
            "Test in regex mode",
            tag_types={"KEY", "EMAIL", "IP_ADDRESS"}
        )
