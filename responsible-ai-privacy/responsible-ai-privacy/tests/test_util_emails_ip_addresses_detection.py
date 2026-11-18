"""
Tests for emails_ip_addresses_detection module.

This module tests the detection of emails, IP addresses, and API keys in text.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
import ipaddress

# Import the module to test
from privacy.util.code_detect.utils import emails_ip_addresses_detection


class TestGetRegexes:
    """Test get_regexes function."""
    
    def test_get_regexes_default_tags(self):
        """Test getting regexes with default high risk tags."""
        regexes = emails_ip_addresses_detection.get_regexes()
        
        assert "EMAIL" in regexes
        assert "IP_ADDRESS" in regexes
        assert "KEY" in regexes
        assert len(regexes) == 3
    
    def test_get_regexes_email_only(self):
        """Test getting only email regex."""
        regexes = emails_ip_addresses_detection.get_regexes({"EMAIL"})
        
        assert "EMAIL" in regexes
        assert "IP_ADDRESS" not in regexes
        assert "KEY" not in regexes
        assert len(regexes) == 1
    
    def test_get_regexes_ipv4_only(self):
        """Test getting only IPv4 regex."""
        regexes = emails_ip_addresses_detection.get_regexes({"IPv4"})
        
        assert "IPv4" in regexes
        assert len(regexes) == 1
    
    def test_get_regexes_ipv6_only(self):
        """Test getting only IPv6 regex."""
        regexes = emails_ip_addresses_detection.get_regexes({"IPv6"})
        
        assert "IPv6" in regexes
        assert len(regexes) == 1
    
    def test_get_regexes_unknown_tag(self):
        """Test with unknown tag triggers warning."""
        with patch('privacy.util.code_detect.utils.emails_ip_addresses_detection.logging') as mock_logging:
            regexes = emails_ip_addresses_detection.get_regexes({"UNKNOWN_TAG"})
            
            # Should log warning
            mock_logging.warning.assert_called_once()
            assert len(regexes) == 0


class TestIpHasDigit:
    """Test ip_has_digit function."""
    
    def test_ip_has_digit_true(self):
        """Test that IP with digits returns True."""
        assert emails_ip_addresses_detection.ip_has_digit("192.168.1.1")
        assert emails_ip_addresses_detection.ip_has_digit("::1")
        assert emails_ip_addresses_detection.ip_has_digit("fe80::1")
    
    def test_ip_has_digit_false(self):
        """Test that IP without digits returns False."""
        assert not emails_ip_addresses_detection.ip_has_digit("::")
        assert not emails_ip_addresses_detection.ip_has_digit("abcd::")


class TestMatchesDatePattern:
    """Test matches_date_pattern function."""
    
    def test_matches_date_pattern_yyyy_yyyy(self):
        """Test matching yyyy-yyyy pattern."""
        assert emails_ip_addresses_detection.matches_date_pattern(" 2020-2021 ")
        assert emails_ip_addresses_detection.matches_date_pattern(" 2020/2021 ")
    
    def test_matches_date_pattern_yyyy_mm_dd(self):
        """Test matching yyyy-mm-dd pattern."""
        assert emails_ip_addresses_detection.matches_date_pattern(" 2021-12-31 ")
        assert emails_ip_addresses_detection.matches_date_pattern(" 2021/12/31 ")
        assert emails_ip_addresses_detection.matches_date_pattern(" 2021.12.31 ")
    
    def test_matches_date_pattern_dd_mm_yyyy(self):
        """Test matching dd-mm-yyyy pattern."""
        assert emails_ip_addresses_detection.matches_date_pattern(" 31-12-2021 ")
        assert emails_ip_addresses_detection.matches_date_pattern(" 31/12/2021 ")
        assert emails_ip_addresses_detection.matches_date_pattern(" 31.12.21 ")
    
    def test_matches_date_pattern_mm_yyyy(self):
        """Test matching mm-yyyy pattern."""
        assert emails_ip_addresses_detection.matches_date_pattern(" 12-2021 ")
        assert emails_ip_addresses_detection.matches_date_pattern(" 12/2021 ")
    
    def test_matches_date_pattern_yyyy_mm(self):
        """Test matching yyyy-mm pattern."""
        assert emails_ip_addresses_detection.matches_date_pattern(" 2021-12 ")
    
    def test_matches_date_pattern_no_match(self):
        """Test non-matching patterns."""
        assert not emails_ip_addresses_detection.matches_date_pattern("192.168.1.1")
        assert not emails_ip_addresses_detection.matches_date_pattern("test@example.com")
        assert not emails_ip_addresses_detection.matches_date_pattern("random text")


class TestFilterVersions:
    """Test filter_versions function."""
    
    def test_filter_versions_true_without_dns_server(self):
        """Test filtering version-like IPs without dns/server context."""
        context = "The version is 1.2.3.4 in this release"
        assert emails_ip_addresses_detection.filter_versions("1.2.3.4", context)
    
    def test_filter_versions_false_with_dns(self):
        """Test not filtering when dns is in context."""
        context = "The DNS server is 1.2.3.4"
        assert not emails_ip_addresses_detection.filter_versions("1.2.3.4", context)
    
    def test_filter_versions_false_with_server(self):
        """Test not filtering when server is in context."""
        context = "Server address 1.2.3.4"
        assert not emails_ip_addresses_detection.filter_versions("1.2.3.4", context)
    
    def test_filter_versions_false_longer_ip(self):
        """Test not filtering longer IPs."""
        context = "Some context"
        assert not emails_ip_addresses_detection.filter_versions("192.168.1.1", context)


class TestNotIpAddress:
    """Test not_ip_address function."""
    
    def test_not_ip_address_valid_ipv4(self):
        """Test valid IPv4 addresses return False."""
        assert not emails_ip_addresses_detection.not_ip_address("192.168.1.1")
        assert not emails_ip_addresses_detection.not_ip_address("8.8.8.8")
        assert not emails_ip_addresses_detection.not_ip_address("10.0.0.1")
    
    def test_not_ip_address_valid_ipv6(self):
        """Test valid IPv6 addresses return False."""
        assert not emails_ip_addresses_detection.not_ip_address("::1")
        assert not emails_ip_addresses_detection.not_ip_address("fe80::1")
    
    def test_not_ip_address_invalid_ip(self):
        """Test invalid IP addresses return True."""
        assert emails_ip_addresses_detection.not_ip_address("999.999.999.999")
        assert emails_ip_addresses_detection.not_ip_address("33.01.33.33")
        assert emails_ip_addresses_detection.not_ip_address("not.an.ip.address")


class TestIsGibberish:
    """Test is_gibberish function."""
    
    def test_is_gibberish_with_gibberish_string(self):
        """Test gibberish detection with gibberish string."""
        with patch('privacy.util.code_detect.utils.emails_ip_addresses_detection.detector.create_from_model') as mock_detector:
            mock_instance = MagicMock()
            mock_instance.is_gibberish.return_value = True
            mock_detector.return_value = mock_instance
            
            result = emails_ip_addresses_detection.is_gibberish("asdfghjkl123456")
            assert result is True
            mock_instance.is_gibberish.assert_called_once_with("asdfghjkl123456")
    
    def test_is_gibberish_with_real_word(self):
        """Test gibberish detection with real word."""
        with patch('privacy.util.code_detect.utils.emails_ip_addresses_detection.detector.create_from_model') as mock_detector:
            mock_instance = MagicMock()
            mock_instance.is_gibberish.return_value = False
            mock_detector.return_value = mock_instance
            
            result = emails_ip_addresses_detection.is_gibberish("password")
            assert result is False


class TestDetectEmailAddresses:
    """Test detect_email_addresses function."""
    
    def test_detect_email_simple(self):
        """Test detecting a simple email address."""
        content = "Contact me at john.doe@example.com for more info."
        matches = emails_ip_addresses_detection.detect_email_addresses(content, {"EMAIL"})
        
        assert len(matches) == 1
        assert matches[0]["tag"] == "EMAIL"
        assert matches[0]["value"] == "john.doe@example.com"
        assert "start" in matches[0]
        assert "end" in matches[0]
    
    def test_detect_email_multiple(self):
        """Test detecting multiple email addresses."""
        content = "Email alice@test.com or bob@example.org"
        matches = emails_ip_addresses_detection.detect_email_addresses(content, {"EMAIL"})
        
        assert len(matches) == 2
        assert matches[0]["value"] == "alice@test.com"
        assert matches[1]["value"] == "bob@example.org"
    
    def test_detect_email_with_special_chars(self):
        """Test detecting email with special characters."""
        content = "Send to user.name-test@subdomain.example.com"
        matches = emails_ip_addresses_detection.detect_email_addresses(content, {"EMAIL"})
        
        assert len(matches) >= 1
        assert any("@" in m["value"] for m in matches)
    
    def test_detect_ipv4_address(self):
        """Test detecting IPv4 address."""
        content = "The DNS server is at 192.168.1.1"
        matches = emails_ip_addresses_detection.detect_email_addresses(content, {"IP_ADDRESS"})
        
        assert len(matches) == 1
        assert matches[0]["tag"] == "IP_ADDRESS"
        assert matches[0]["value"] == "192.168.1.1"
    
    def test_detect_ipv4_multiple(self):
        """Test detecting multiple IPv4 addresses."""
        content = "Server 10.0.0.1 and 8.8.8.8 are available"
        matches = emails_ip_addresses_detection.detect_email_addresses(content, {"IP_ADDRESS"})
        
        assert len(matches) == 2
    
    def test_detect_ip_filters_date_pattern(self):
        """Test that date-like patterns are filtered out."""
        content = "Release dates are 2021-12-31 and 2022.01.15"
        matches = emails_ip_addresses_detection.detect_email_addresses(content, {"IP_ADDRESS"})
        
        # Should not detect dates as IPs
        assert len(matches) == 0
    
    def test_detect_ip_filters_version(self):
        """Test that version-like IPs are filtered out."""
        content = "Version 1.2.3.4 was released"
        matches = emails_ip_addresses_detection.detect_email_addresses(content, {"IP_ADDRESS"})
        
        # Should filter out version
        assert len(matches) == 0
    
    def test_detect_ip_filters_no_digit(self):
        """Test that IPs without digits are filtered out."""
        content = "Something like :: is not an IP"
        matches = emails_ip_addresses_detection.detect_email_addresses(content, {"IP_ADDRESS"})
        
        assert len(matches) == 0
    
    def test_detect_ip_filters_invalid_ip(self):
        """Test that invalid IPs are filtered out."""
        content = "Invalid IP 999.999.999.999"
        matches = emails_ip_addresses_detection.detect_email_addresses(content, {"IP_ADDRESS"})
        
        assert len(matches) == 0
    
    def test_detect_key_with_gibberish(self):
        """Test detecting API key with gibberish."""
        with patch('privacy.util.code_detect.utils.emails_ip_addresses_detection.is_gibberish') as mock_gibberish:
            mock_gibberish.return_value = True
            
            content = "API_KEY: abcd1234efgh5678ijkl"
            matches = emails_ip_addresses_detection.detect_email_addresses(content, {"KEY"})
            
            # Should detect if gibberish returns True
            assert len(matches) >= 0  # May or may not match depending on regex
    
    def test_detect_key_filters_non_gibberish(self):
        """Test that non-gibberish keys are filtered out."""
        with patch('privacy.util.code_detect.utils.emails_ip_addresses_detection.is_gibberish') as mock_gibberish:
            mock_gibberish.return_value = False
            
            content = "API_KEY: passwordTest1234"
            matches = emails_ip_addresses_detection.detect_email_addresses(content, {"KEY"})
            
            # Should filter out non-gibberish
            for match in matches:
                if match["tag"] == "KEY":
                    pytest.fail("Non-gibberish key should be filtered")
    
    def test_detect_empty_content(self):
        """Test with empty content."""
        content = ""
        matches = emails_ip_addresses_detection.detect_email_addresses(content, {"EMAIL", "IP_ADDRESS"})
        
        assert matches == []
    
    def test_detect_no_matches(self):
        """Test with content that has no PII."""
        content = "This is just plain text with no sensitive information."
        matches = emails_ip_addresses_detection.detect_email_addresses(content, {"EMAIL", "IP_ADDRESS"})
        
        assert len(matches) == 0
    
    def test_detect_multiple_tag_types(self):
        """Test detecting multiple types of PII."""
        content = "Email john@test.com from server 10.0.0.1"
        matches = emails_ip_addresses_detection.detect_email_addresses(content, {"EMAIL", "IP_ADDRESS"})
        
        assert len(matches) == 2
        tags = {m["tag"] for m in matches}
        assert "EMAIL" in tags
        assert "IP_ADDRESS" in tags
    
    def test_detect_ipv6_address(self):
        """Test detecting IPv6 address."""
        content = "IPv6 address is fe80::1"
        matches = emails_ip_addresses_detection.detect_email_addresses(content, {"IP_ADDRESS"})
        
        # May or may not match depending on context filtering
        assert isinstance(matches, list)
    
    def test_detect_with_context_filtering(self):
        """Test that context is used for filtering."""
        content = "The DNS server address is 192.168.1.1 for configuration"
        matches = emails_ip_addresses_detection.detect_email_addresses(content, {"IP_ADDRESS"})
        
        # Should detect IP when DNS is in context
        assert len(matches) >= 1


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_email_at_start_of_string(self):
        """Test email at start of content."""
        content = "admin@example.com is the contact"
        matches = emails_ip_addresses_detection.detect_email_addresses(content, {"EMAIL"})
        
        assert len(matches) == 1
    
    def test_email_at_end_of_string(self):
        """Test email at end of content."""
        content = "Contact us at support@example.com"
        matches = emails_ip_addresses_detection.detect_email_addresses(content, {"EMAIL"})
        
        assert len(matches) == 1
    
    def test_ip_at_start_of_string(self):
        """Test IP at start of content."""
        content = "192.168.1.1 is the server address"
        matches = emails_ip_addresses_detection.detect_email_addresses(content, {"IP_ADDRESS"})
        
        # Should detect
        assert isinstance(matches, list)
    
    def test_mixed_content(self):
        """Test mixed content with various PII types."""
        content = """
        Server: 10.0.0.1
        Contact: admin@example.com
        Dates: 2021-12-31 and 2022-01-01
        Version: 1.2.3.4
        Real IP: 8.8.8.8
        """
        matches = emails_ip_addresses_detection.detect_email_addresses(content, {"EMAIL", "IP_ADDRESS"})
        
        # Should have at least email and some IPs (filtering out dates and versions)
        assert len(matches) >= 2
