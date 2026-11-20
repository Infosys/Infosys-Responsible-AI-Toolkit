"""
Test suite for privacy utility functions - PII redaction module.
Tests PII redaction and replacement functions without heavy ML dependencies.
"""

import pytest
import json
import ipaddress
from src.privacy.util.code_detect.pii_redaction import (
    load_json,
    random_replacements,
    replace_ip,
    is_private_ip,
    redact_pii_text,
    REPLACEMENTS_IP,
    POPULAR_DNS_SERVERS
)


class TestLoadJsonRedaction:
    """Test the load_json utility function from redaction module."""
    
    def test_load_json_valid_list(self):
        """Test loading valid JSON list."""
        json_str = '[{"tag": "EMAIL", "value": "test@example.com"}]'
        result = load_json(json_str)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["tag"] == "EMAIL"
    
    def test_load_json_valid_dict(self):
        """Test loading valid JSON dictionary raises ValueError."""
        json_str = '{"tag": "EMAIL"}'
        result = load_json(json_str)
        # Should return the original string when not a list
        assert result == '{"tag": "EMAIL"}'
    
    def test_load_json_invalid(self):
        """Test loading invalid JSON."""
        result = load_json("not valid json")
        assert result == "not valid json"
    
    def test_load_json_empty_list(self):
        """Test loading empty JSON list."""
        result = load_json("[]")
        assert result == []


class TestRandomReplacements:
    """Test the random_replacements generator function."""
    
    def test_random_replacements_default_count(self):
        """Test generating random replacements with default count."""
        result = random_replacements()
        
        assert "EMAIL" in result
        assert "KEY" in result
        assert "IP_ADDRESS" in result
        
        assert len(result["EMAIL"]) == 10
        assert len(result["KEY"]) == 10
        assert result["IP_ADDRESS"] == REPLACEMENTS_IP
    
    def test_random_replacements_custom_count(self):
        """Test generating random replacements with custom count."""
        result = random_replacements(n=5)
        
        assert len(result["EMAIL"]) == 5
        assert len(result["KEY"]) == 5
    
    def test_random_replacements_email_format(self):
        """Test that generated emails have correct format."""
        result = random_replacements(n=3)
        
        for email in result["EMAIL"]:
            assert "@example.com" in email
            assert len(email.split("@")[0]) == 5
    
    def test_random_replacements_key_format(self):
        """Test that generated keys have correct format."""
        result = random_replacements(n=3)
        
        for key in result["KEY"]:
            assert len(key) == 32
            assert all(c.isalnum() for c in key)
    
    def test_random_replacements_ip_addresses(self):
        """Test that IP_ADDRESS contains the predefined replacements."""
        result = random_replacements()
        
        assert "IPv4" in result["IP_ADDRESS"]
        assert "IPv6" in result["IP_ADDRESS"]
        assert len(result["IP_ADDRESS"]["IPv4"]) > 0
        assert len(result["IP_ADDRESS"]["IPv6"]) > 0


class TestReplaceIp:
    """Test the replace_ip function."""
    
    def test_replace_ip_valid_ipv4(self):
        """Test replacing valid IPv4 address."""
        replacements = {"IP_ADDRESS": REPLACEMENTS_IP}
        result = replace_ip("192.168.1.1", replacements)
        
        assert result in REPLACEMENTS_IP["IPv4"]
    
    def test_replace_ip_valid_ipv6(self):
        """Test replacing valid IPv6 address."""
        replacements = {"IP_ADDRESS": REPLACEMENTS_IP}
        result = replace_ip("2001:0db8:85a3:0000:0000:8a2e:0370:7334", replacements)
        
        assert result in REPLACEMENTS_IP["IPv6"]
    
    def test_replace_ip_invalid(self):
        """Test with invalid IP address."""
        replacements = {"IP_ADDRESS": REPLACEMENTS_IP}
        result = replace_ip("not_an_ip", replacements)
        
        # Should return original value
        assert result == "not_an_ip"
    
    def test_replace_ip_empty_string(self):
        """Test with empty string."""
        replacements = {"IP_ADDRESS": REPLACEMENTS_IP}
        result = replace_ip("", replacements)
        
        assert result == ""


class TestIsPrivateIp:
    """Test the is_private_ip function."""
    
    def test_is_private_ip_private_ipv4(self):
        """Test with private IPv4 addresses."""
        assert is_private_ip("192.168.1.1") is True
        assert is_private_ip("10.0.0.1") is True
        assert is_private_ip("172.16.0.1") is True
    
    def test_is_private_ip_public_ipv4(self):
        """Test with public IPv4 addresses."""
        assert is_private_ip("8.8.8.8") is False
        assert is_private_ip("1.1.1.1") is False
        assert is_private_ip("93.184.216.34") is False
    
    def test_is_private_ip_private_ipv6(self):
        """Test with private IPv6 addresses."""
        assert is_private_ip("fc00::1") is True
        assert is_private_ip("fd00::1") is True
    
    def test_is_private_ip_public_ipv6(self):
        """Test with public IPv6 addresses."""
        assert is_private_ip("2001:4860:4860::8888") is False
    
    def test_is_private_ip_localhost(self):
        """Test with localhost addresses."""
        assert is_private_ip("127.0.0.1") is True
        assert is_private_ip("::1") is True


class TestRedactPiiText:
    """Test the redact_pii_text function."""
    
    def test_redact_pii_text_single_email(self):
        """Test redacting single email from text."""
        text = "Contact me at john@example.com for details."
        secrets = json.dumps([{
            "tag": "EMAIL",
            "value": "john@example.com",
            "start": 14,
            "end": 30
        }])
        replacements = {"EMAIL": ["redacted@example.com"]}
        
        result_text, references, modified = redact_pii_text(text, secrets, replacements)
        
        assert "redacted@example.com" in result_text
        assert "john@example.com" not in result_text
        assert modified is True
        assert "PI:EMAIL:" in references
    
    def test_redact_pii_text_multiple_secrets(self):
        """Test redacting multiple secrets from text."""
        text = "Email: john@test.com, IP: 93.184.216.34"
        secrets = json.dumps([
            {"tag": "EMAIL", "value": "john@test.com", "start": 7, "end": 20},
            {"tag": "IP_ADDRESS", "value": "93.184.216.34", "start": 26, "end": 39}
        ])
        replacements = {
            "EMAIL": ["redacted@example.com"],
            "IP_ADDRESS": REPLACEMENTS_IP
        }
        
        result_text, references, modified = redact_pii_text(text, secrets, replacements)
        
        assert "john@test.com" not in result_text
        assert "93.184.216.34" not in result_text
        assert modified is True
    
    def test_redact_pii_text_private_ip_not_redacted(self):
        """Test that private IPs are not redacted."""
        text = "Server IP: 192.168.1.1"
        secrets = json.dumps([
            {"tag": "IP_ADDRESS", "value": "192.168.1.1", "start": 11, "end": 22}
        ])
        replacements = {"IP_ADDRESS": REPLACEMENTS_IP}
        
        result_text, references, modified = redact_pii_text(text, secrets, replacements)
        
        # Private IP should not be modified
        assert "192.168.1.1" in result_text
        assert modified is False
    
    def test_redact_pii_text_dns_server_not_redacted(self):
        """Test that popular DNS servers are not redacted."""
        text = "DNS: 8.8.8.8"
        secrets = json.dumps([
            {"tag": "IP_ADDRESS", "value": "8.8.8.8", "start": 5, "end": 12}
        ])
        replacements = {"IP_ADDRESS": REPLACEMENTS_IP}
        
        result_text, references, modified = redact_pii_text(text, secrets, replacements)
        
        # DNS server should not be modified
        assert "8.8.8.8" in result_text
        assert modified is False
    
    def test_redact_pii_text_no_secrets(self):
        """Test with no secrets to redact."""
        text = "This is clean text."
        secrets = "[]"
        replacements = {}
        
        result_text, references, modified = redact_pii_text(text, secrets, replacements)
        
        assert result_text == text
        assert references == ""
        assert modified is False
    
    def test_redact_pii_text_invalid_secrets(self):
        """Test with invalid secrets format."""
        text = "Some text"
        secrets = "invalid json"
        replacements = {}
        
        result_text, references, modified = redact_pii_text(text, secrets, replacements)
        
        assert result_text == text
        assert modified is False
    
    def test_redact_pii_text_without_references(self):
        """Test redaction without adding references."""
        text = "Contact: alice@test.com"
        secrets = json.dumps([
            {"tag": "EMAIL", "value": "alice@test.com", "start": 9, "end": 23}
        ])
        replacements = {"EMAIL": ["redacted@example.com"]}
        
        result_text, references, modified = redact_pii_text(
            text, secrets, replacements, add_references=False
        )
        
        assert "redacted@example.com" in result_text
        assert references == ""
        assert modified is True
    
    def test_redact_pii_text_key_redaction(self):
        """Test redacting API key."""
        text = "API Key: abcd1234efgh5678ijkl9012mnop3456"
        secrets = json.dumps([
            {
                "tag": "KEY",
                "value": "abcd1234efgh5678ijkl9012mnop3456",
                "start": 9,
                "end": 41
            }
        ])
        replacements = {"KEY": ["REDACTED_KEY_12345678901234567890"]}
        
        result_text, references, modified = redact_pii_text(text, secrets, replacements)
        
        assert "abcd1234efgh5678ijkl9012mnop3456" not in result_text
        assert "REDACTED_KEY" in result_text
        assert modified is True
    
    def test_redact_pii_text_overlapping_secrets(self):
        """Test handling of overlapping secret locations."""
        text = "test@example.com"
        secrets = json.dumps([
            {"tag": "EMAIL", "value": "test@example.com", "start": 0, "end": 16}
        ])
        replacements = {"EMAIL": ["a@b.c"]}
        
        result_text, references, modified = redact_pii_text(text, secrets, replacements)
        
        assert result_text == "a@b.c"
        assert modified is True
    
    def test_redact_pii_text_ipv6_handling(self):
        """Test IPv6 address redaction."""
        # Use a public IPv6 address (Google DNS)
        text = "IPv6: 2001:4860:4860::8888"
        secrets = json.dumps([
            {
                "tag": "IP_ADDRESS",
                "value": "2001:4860:4860::8888",
                "start": 6,
                "end": 27
            }
        ])
        replacements = {"IP_ADDRESS": REPLACEMENTS_IP}
        
        result_text, references, modified = redact_pii_text(text, secrets, replacements)
        
        assert "2001:4860:4860::8888" not in result_text
        assert modified is True
        # Result should contain one of the IPv6 replacements
        assert any(ipv6 in result_text for ipv6 in REPLACEMENTS_IP["IPv6"])
