"""
Comprehensive tests for pii_redaction.py module - Missing lines 105-129
Tests cover redact_pii_batch function with various configurations
"""

import pytest
from unittest.mock import MagicMock, patch
from privacy.util.code_detect.pii_redaction import redact_pii_batch, redact_pii_text


class TestRedactPiiBatch:
    """Test redact_pii_batch function"""
    
    def test_redact_pii_batch_with_secrets_and_references(self):
        """Test batch redaction with references enabled"""
        examples = [
            {
                "content": "John's email is john@example.com",
                "secrets": ["john@example.com"],
                "has_secrets": True
            },
            {
                "content": "Contact Jane at jane@example.com",
                "secrets": ["jane@example.com"],
                "has_secrets": True
            }
        ]
        replacements = {"@example.com": "[EMAIL_DOMAIN]"}
        
        with patch('privacy.util.code_detect.pii_redaction.redact_pii_text') as mock_redact:
            mock_redact.side_effect = [
                ("John's email is john[EMAIL_DOMAIN]", "john@example.com", True),
                ("Contact Jane at jane[EMAIL_DOMAIN]", "jane@example.com", True)
            ]
            
            result = redact_pii_batch(examples, replacements, add_references=True)
            
            assert "new_content" in result
            assert "modified" in result
            assert "references" in result
            assert len(result["new_content"]) == 2
            assert len(result["modified"]) == 2
            assert len(result["references"]) == 2
    
    def test_redact_pii_batch_without_references(self):
        """Test batch redaction without references"""
        examples = [
            {
                "content": "Phone: 555-1234",
                "secrets": ["555-1234"],
                "has_secrets": True
            }
        ]
        replacements = {}
        
        with patch('privacy.util.code_detect.pii_redaction.redact_pii_text') as mock_redact:
            mock_redact.return_value = ("Phone: [PHONE]", True)
            
            result = redact_pii_batch(examples, replacements, add_references=False)
            
            assert "new_content" in result
            assert "modified" in result
            assert "references" not in result
            assert len(result["new_content"]) == 1
    
    def test_redact_pii_batch_no_secrets(self):
        """Test batch with entries that have no secrets"""
        examples = [
            {
                "content": "Just plain text",
                "secrets": [],
                "has_secrets": False
            },
            {
                "content": "Email: test@test.com",
                "secrets": ["test@test.com"],
                "has_secrets": True
            }
        ]
        replacements = {}
        
        with patch('privacy.util.code_detect.pii_redaction.redact_pii_text') as mock_redact:
            mock_redact.return_value = ("Email: [EMAIL]", "test@test.com", True)
            
            result = redact_pii_batch(examples, replacements, add_references=True)
            
            # First entry should have has_secrets=False, so text not modified
            assert result["new_content"][0] == "Just plain text"
            assert result["modified"][0] == False
            assert result["references"][0] == "Just plain text"
            
            # Second entry should be redacted
            assert result["modified"][1] == True
    
    def test_redact_pii_batch_empty_examples(self):
        """Test batch with empty examples list"""
        examples = []
        replacements = {}
        
        result = redact_pii_batch(examples, replacements, add_references=True)
        
        assert result["new_content"] == []
        assert result["modified"] == []
        assert result["references"] == []
    
    def test_redact_pii_batch_mixed_has_secrets(self):
        """Test batch with mixed has_secrets values"""
        examples = [
            {
                "content": "No secrets here",
                "secrets": [],
                "has_secrets": False
            },
            {
                "content": "Has secret password123",
                "secrets": ["password123"],
                "has_secrets": True
            },
            {
                "content": "Another safe text",
                "secrets": [],
                "has_secrets": False
            },
            {
                "content": "api_key=secret_key",
                "secrets": ["secret_key"],
                "has_secrets": True
            }
        ]
        replacements = {"password123": "[REDACTED]", "secret_key": "[KEY]"}
        
        with patch('privacy.util.code_detect.pii_redaction.redact_pii_text') as mock_redact:
            mock_redact.side_effect = [
                ("Has secret [REDACTED]", "[REDACTED]", True),
                ("api_key=[KEY]", "[KEY]", True)
            ]
            
            result = redact_pii_batch(examples, replacements, add_references=True)
            
            assert len(result["new_content"]) == 4
            assert result["modified"] == [False, True, False, True]
            assert result["new_content"][0] == "No secrets here"  # Unchanged
            assert result["new_content"][2] == "Another safe text"  # Unchanged
    
    def test_redact_pii_batch_with_add_references_false(self):
        """Test that result doesn't include references when add_references=False"""
        examples = [
            {
                "content": "Text with email@domain.com",
                "secrets": ["email@domain.com"],
                "has_secrets": True
            }
        ]
        replacements = {}
        
        with patch('privacy.util.code_detect.pii_redaction.redact_pii_text') as mock_redact:
            mock_redact.return_value = ("Text with [EMAIL]", True)
            
            result = redact_pii_batch(examples, replacements, add_references=False)
            
            # Verify references key is NOT in result
            assert "references" not in result
            assert "new_content" in result
            assert "modified" in result
    
    def test_redact_pii_batch_with_add_references_true(self):
        """Test that result includes references when add_references=True"""
        examples = [
            {
                "content": "Text with email@domain.com",
                "secrets": ["email@domain.com"],
                "has_secrets": True
            }
        ]
        replacements = {}
        
        with patch('privacy.util.code_detect.pii_redaction.redact_pii_text') as mock_redact:
            mock_redact.return_value = ("Text with [EMAIL]", "email@domain.com", True)
            
            result = redact_pii_batch(examples, replacements, add_references=True)
            
            # Verify references key IS in result
            assert "references" in result
            assert "new_content" in result
            assert "modified" in result
    
    def test_redact_pii_batch_multiple_no_secrets(self):
        """Test batch where all entries have no secrets"""
        examples = [
            {"content": "Text 1", "secrets": [], "has_secrets": False},
            {"content": "Text 2", "secrets": [], "has_secrets": False},
            {"content": "Text 3", "secrets": [], "has_secrets": False}
        ]
        replacements = {}
        
        result = redact_pii_batch(examples, replacements, add_references=True)
        
        # All should be unchanged and unmodified
        assert result["new_content"] == ["Text 1", "Text 2", "Text 3"]
        assert result["modified"] == [False, False, False]
        assert result["references"] == ["Text 1", "Text 2", "Text 3"]
    
    def test_redact_pii_batch_none_add_references_with_has_secrets(self):
        """Test with add_references=False but has_secrets=True for entries"""
        examples = [
            {
                "content": "Secret content password",
                "secrets": ["password"],
                "has_secrets": True
            }
        ]
        replacements = {}
        
        with patch('privacy.util.code_detect.pii_redaction.redact_pii_text') as mock_redact:
            mock_redact.return_value = ("Secret content [PASS]", True)
            
            result = redact_pii_batch(examples, replacements, add_references=False)
            
            # Should still redact even without add_references
            assert result["new_content"][0] == "Secret content [PASS]"
            assert result["modified"][0] == True
            assert "references" not in result
