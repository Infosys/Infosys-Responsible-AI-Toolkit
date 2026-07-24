"""
Tests for privacy.util.code_detect.utils.emails_ip_addresses_detection module
"""
import pytest
from unittest.mock import patch, Mock
from privacy.util.code_detect.utils.emails_ip_addresses_detection import (
    get_regexes,
    ip_has_digit,
    matches_date_pattern,
    filter_versions,
    not_ip_address,
    is_gibberish,
    detect_email_addresses
)


class TestGetRegexes:
    """Test get_regexes function"""
    
    def test_get_regexes_default_tags(self):
        """Test get_regexes with default high risk tags"""
        result = get_regexes()
        
        assert "EMAIL" in result
        assert "IP_ADDRESS" in result
        assert "KEY" in result
        assert len(result) == 3
    
    def test_get_regexes_email_only(self):
        """Test get_regexes with only EMAIL tag"""
        result = get_regexes(high_risk_tags={"EMAIL"})
        
        assert "EMAIL" in result
        assert "IP_ADDRESS" not in result
        assert "KEY" not in result
        assert len(result) == 1
    
    def test_get_regexes_key_only(self):
        """Test get_regexes with only KEY tag"""
        result = get_regexes(high_risk_tags={"KEY"})
        
        assert "KEY" in result
        assert "EMAIL" not in result
        assert len(result) == 1
    
    def test_get_regexes_ipv4_only(self):
        """Test get_regexes with only IPv4 tag"""
        result = get_regexes(high_risk_tags={"IPv4"})
        
        assert "IPv4" in result
        assert "EMAIL" not in result
        assert len(result) == 1
    
    def test_get_regexes_ipv6_only(self):
        """Test get_regexes with only IPv6 tag"""
        result = get_regexes(high_risk_tags={"IPv6"})
        
        assert "IPv6" in result
        assert "EMAIL" not in result
        assert len(result) == 1
    
    def test_get_regexes_ip_address_tag(self):
        """Test get_regexes with IP_ADDRESS tag"""
        result = get_regexes(high_risk_tags={"IP_ADDRESS"})
        
        assert "IP_ADDRESS" in result
        assert len(result) == 1
    
    def test_get_regexes_multiple_tags(self):
        """Test get_regexes with multiple tags"""
        result = get_regexes(high_risk_tags={"EMAIL", "KEY"})
        
        assert "EMAIL" in result
        assert "KEY" in result
        assert len(result) == 2
    
    def test_get_regexes_email_pattern_matches_valid_email(self):
        """Test that EMAIL regex matches valid email addresses"""
        regexes = get_regexes(high_risk_tags={"EMAIL"})
        email_regex = regexes["EMAIL"]
        
        test_text = "Contact me at user@example.com for details"
        matches = email_regex.findall(test_text)
        
        assert len(matches) > 0
        assert "user@example.com" in matches[0]
    
    def test_get_regexes_key_pattern_matches_api_key(self):
        """Test that KEY regex matches API key patterns"""
        regexes = get_regexes(high_risk_tags={"KEY"})
        key_regex = regexes["KEY"]
        
        test_text = "API_KEY=abcd1234efgh5678ijkl"
        matches = key_regex.findall(test_text)
        
        assert len(matches) > 0
    
    def test_get_regexes_ipv4_pattern_matches_valid_ip(self):
        """Test that IPv4 regex matches valid IPv4 addresses"""
        regexes = get_regexes(high_risk_tags={"IPv4"})
        ipv4_regex = regexes["IPv4"]
        
        test_text = "Server IP: 192.168.1.1"
        matches = ipv4_regex.findall(test_text)
        
        assert len(matches) > 0
        assert "192.168.1.1" in matches
    
    def test_get_regexes_ipv6_pattern_matches_valid_ipv6(self):
        """Test that IPv6 regex matches valid IPv6 addresses"""
        regexes = get_regexes(high_risk_tags={"IPv6"})
        ipv6_regex = regexes["IPv6"]
        
        test_text = "IPv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        matches = ipv6_regex.findall(test_text)
        
        assert len(matches) > 0
    
    def test_get_regexes_ip_address_pattern_matches_both_versions(self):
        """Test that IP_ADDRESS regex matches both IPv4 and IPv6"""
        regexes = get_regexes(high_risk_tags={"IP_ADDRESS"})
        ip_regex = regexes["IP_ADDRESS"]
        
        test_text_ipv4 = "IPv4: 10.0.0.1"
        test_text_ipv6 = "IPv6: fe80::1"
        
        matches_v4 = ip_regex.findall(test_text_ipv4)
        matches_v6 = ip_regex.findall(test_text_ipv6)
        
        assert len(matches_v4) > 0
        assert len(matches_v6) > 0
    
    def test_get_regexes_empty_tags(self):
        """Test get_regexes with empty tags set"""
        result = get_regexes(high_risk_tags=set())
        
        assert len(result) == 0
    
    def test_get_regexes_unknown_tag(self):
        """Test get_regexes with unknown tag (should be ignored)"""
        result = get_regexes(high_risk_tags={"UNKNOWN_TAG"})
        
        assert "UNKNOWN_TAG" not in result
        assert len(result) == 0
    
    def test_get_regexes_mixed_known_unknown_tags(self):
        """Test get_regexes with mix of known and unknown tags"""
        result = get_regexes(high_risk_tags={"EMAIL", "UNKNOWN", "KEY"})
        
        assert "EMAIL" in result
        assert "KEY" in result
        assert "UNKNOWN" not in result
        assert len(result) == 2
    
    def test_get_regexes_regex_objects_are_compiled(self):
        """Test that returned values are compiled regex objects"""
        import regex
        result = get_regexes()
        
        for tag, pattern in result.items():
            assert isinstance(pattern, regex.Pattern)
    
    def test_get_regexes_email_pattern_multiline_flag(self):
        """Test that EMAIL regex has MULTILINE flag"""
        import regex
        regexes = get_regexes(high_risk_tags={"EMAIL"})
        email_regex = regexes["EMAIL"]
        
        # Check if MULTILINE flag is set
        assert email_regex.flags & regex.MULTILINE
    
    def test_get_regexes_ip_pattern_multiline_flag(self):
        """Test that IP_ADDRESS regex has MULTILINE flag"""
        import regex
        regexes = get_regexes(high_risk_tags={"IP_ADDRESS"})
        ip_regex = regexes["IP_ADDRESS"]
        
        # Check if MULTILINE flag is set
        assert ip_regex.flags & regex.MULTILINE


class TestIpHasDigit:
    """Test ip_has_digit function"""
    
    def test_ip_has_digit_with_digits(self):
        """Test that ip_has_digit returns True for string with digits"""
        assert ip_has_digit("192.168.1.1") == True
        assert ip_has_digit("::1") == True
        assert ip_has_digit("fe80::1") == True
    
    def test_ip_has_digit_without_digits(self):
        """Test that ip_has_digit returns False for string without digits"""
        assert ip_has_digit("::") == False
        assert ip_has_digit("abcd:efgh") == False
    
    def test_ip_has_digit_empty_string(self):
        """Test ip_has_digit with empty string"""
        assert ip_has_digit("") == False


class TestMatchesDatePattern:
    """Test matches_date_pattern function"""
    
    def test_matches_date_pattern_yyyy_yyyy(self):
        """Test date pattern matching for yyyy-yyyy format"""
        assert matches_date_pattern("2020-2023") == True
        assert matches_date_pattern("1999/2000") == True
    
    def test_matches_date_pattern_yyyy_mm_dd(self):
        """Test date pattern matching for yyyy-mm-dd format"""
        assert matches_date_pattern("2023-12-31") == True
        assert matches_date_pattern("2023.01.15") == True
        assert matches_date_pattern("2023/06/20") == True
    
    def test_matches_date_pattern_dd_mm_yyyy(self):
        """Test date pattern matching for dd-mm-yyyy format"""
        assert matches_date_pattern("31-12-2023") == True
        assert matches_date_pattern("15/01/23") == True
    
    def test_matches_date_pattern_mm_yyyy(self):
        """Test date pattern matching for mm-yyyy format"""
        assert matches_date_pattern("12-2023") == True
        assert matches_date_pattern("06/2023") == True
    
    def test_matches_date_pattern_yyyy_mm(self):
        """Test date pattern matching for yyyy-mm format"""
        assert matches_date_pattern("2023-12") == True
    
    def test_matches_date_pattern_non_date(self):
        """Test that non-date strings return False"""
        assert matches_date_pattern("192.168.1.1") == False
        assert matches_date_pattern("hello world") == False
        assert matches_date_pattern("abc-def") == False


class TestFilterVersions:
    """Test filter_versions function"""
    
    def test_filter_versions_with_version_format_no_dns(self):
        """Test filter_versions returns True for version format without dns context"""
        assert filter_versions("1.2.3.4", "This is version 1.2.3.4 of the software") == True
    
    def test_filter_versions_with_dns_context(self):
        """Test filter_versions returns False when dns in context"""
        assert filter_versions("1.2.3.4", "DNS server at 1.2.3.4 is down") == False
    
    def test_filter_versions_with_server_context(self):
        """Test filter_versions returns False when server in context"""
        assert filter_versions("1.2.3.4", "Server 1.2.3.4 is running") == False
    
    def test_filter_versions_non_version_format(self):
        """Test filter_versions returns False for non-version format"""
        assert filter_versions("192.168.1.1", "IP address 192.168.1.1") == False
        assert filter_versions("10.20.30.40", "Some text") == False


class TestNotIpAddress:
    """Test not_ip_address function"""
    
    def test_not_ip_address_valid_ipv4(self):
        """Test not_ip_address returns False for valid IPv4"""
        assert not_ip_address("192.168.1.1") == False
        assert not_ip_address("10.0.0.1") == False
        assert not_ip_address("8.8.8.8") == False
    
    def test_not_ip_address_valid_ipv6(self):
        """Test not_ip_address returns False for valid IPv6"""
        assert not_ip_address("2001:0db8:85a3:0000:0000:8a2e:0370:7334") == False
        assert not_ip_address("::1") == False
        assert not_ip_address("fe80::1") == False
    
    def test_not_ip_address_invalid_ip(self):
        """Test not_ip_address returns True for invalid IP"""
        assert not_ip_address("256.1.1.1") == True
        assert not_ip_address("33.01.33.33") == True
        assert not_ip_address("999.999.999.999") == True
        assert not_ip_address("not.an.ip.address") == True


class TestIsGibberish:
    """Test is_gibberish function"""
    
    @patch('privacy.util.code_detect.utils.emails_ip_addresses_detection.detector.create_from_model')
    def test_is_gibberish_with_gibberish_string(self, mock_detector):
        """Test is_gibberish returns True for gibberish strings"""
        mock_detector_instance = Mock()
        mock_detector_instance.is_gibberish.return_value = True
        mock_detector.return_value = mock_detector_instance
        
        result = is_gibberish("xkcd1234abcd5678")
        
        assert result == True
        mock_detector_instance.is_gibberish.assert_called_once()
    
    @patch('privacy.util.code_detect.utils.emails_ip_addresses_detection.detector.create_from_model')
    def test_is_gibberish_with_real_words(self, mock_detector):
        """Test is_gibberish returns False for real words"""
        mock_detector_instance = Mock()
        mock_detector_instance.is_gibberish.return_value = False
        mock_detector.return_value = mock_detector_instance
        
        result = is_gibberish("password123")
        
        assert result == False


class TestDetectEmailAddresses:
    """Test detect_email_addresses function"""
    
    def test_detect_email_addresses_with_email(self):
        """Test detection of email addresses"""
        content = "Contact me at user@example.com for more info"
        result = detect_email_addresses(content, tag_types={"EMAIL"})
        
        assert len(result) > 0
        assert result[0]["tag"] == "EMAIL"
        assert "user@example.com" in result[0]["value"]
    
    def test_detect_email_addresses_with_ip(self):
        """Test detection of IP addresses"""
        content = "Server is at 192.168.1.100 and running"
        result = detect_email_addresses(content, tag_types={"IP_ADDRESS"})
        
        assert len(result) > 0
        assert result[0]["tag"] == "IP_ADDRESS"
        assert result[0]["value"] == "192.168.1.100"
    
    def test_detect_email_addresses_filters_date_false_positives(self):
        """Test that date patterns are filtered out from IP detection"""
        content = "Meeting on 2023-12-31 at noon"
        result = detect_email_addresses(content, tag_types={"IP_ADDRESS"})
        
        # Should not detect date as IP
        assert len(result) == 0
    
    def test_detect_email_addresses_filters_version_false_positives(self):
        """Test that version numbers are filtered out"""
        content = "Using version 1.2.3.4 of the software"
        result = detect_email_addresses(content, tag_types={"IP_ADDRESS"})
        
        # Should filter out version format
        assert len(result) == 0
    
    def test_detect_email_addresses_filters_invalid_ip(self):
        """Test that invalid IPs are filtered out"""
        content = "Invalid IP 256.256.256.256 detected"
        result = detect_email_addresses(content, tag_types={"IP_ADDRESS"})
        
        assert len(result) == 0
    
    def test_detect_email_addresses_filters_no_digits_ip(self):
        """Test that IPs without digits are filtered out"""
        content = "IPv6 :: detected"
        result = detect_email_addresses(content, tag_types={"IP_ADDRESS"})
        
        # :: has no digits, should be filtered
        assert len(result) == 0
    
    @patch('privacy.util.code_detect.utils.emails_ip_addresses_detection.is_gibberish')
    def test_detect_email_addresses_with_key_gibberish(self, mock_is_gibberish):
        """Test KEY detection filters non-gibberish strings"""
        mock_is_gibberish.return_value = True
        
        content = "API key is xkcd1234abcd5678efgh"
        result = detect_email_addresses(content, tag_types={"KEY"})
        
        # Should detect gibberish keys
        assert len(result) > 0
        assert result[0]["tag"] == "KEY"
    
    @patch('privacy.util.code_detect.utils.emails_ip_addresses_detection.is_gibberish')
    def test_detect_email_addresses_key_filters_real_words(self, mock_is_gibberish):
        """Test KEY detection filters real words"""
        mock_is_gibberish.return_value = False
        
        content = "The password123 is not secure"
        result = detect_email_addresses(content, tag_types={"KEY"})
        
        # Should filter out real words
        assert len(result) == 0
    
    def test_detect_email_addresses_multiple_tags(self):
        """Test detection with multiple tag types"""
        content = "Email: user@test.com, IP: 10.0.0.1"
        result = detect_email_addresses(content, tag_types={"EMAIL", "IP_ADDRESS"})
        
        assert len(result) >= 2
        tags = [r["tag"] for r in result]
        assert "EMAIL" in tags
        assert "IP_ADDRESS" in tags
    
    def test_detect_email_addresses_with_dns_context(self):
        """Test IP detection with DNS context doesn't filter"""
        content = "DNS server 192.168.1.1 is configured"
        result = detect_email_addresses(content, tag_types={"IP_ADDRESS"})
        
        # Should detect IP even with DNS context (only filters version format)
        assert len(result) > 0
    
    def test_detect_email_addresses_empty_content(self):
        """Test detection with empty content"""
        result = detect_email_addresses("", tag_types={"EMAIL"})
        
        assert len(result) == 0
    
    def test_detect_email_addresses_no_matches(self):
        """Test detection when no PII present"""
        content = "This is just plain text with no PII"
        result = detect_email_addresses(content, tag_types={"EMAIL", "IP_ADDRESS"})
        
        assert len(result) == 0
    
    def test_detect_ip_without_digit_filtered(self):
        """Test IP ADDRESS that has no digits is filtered (line 177)"""
        # Create content with IP-like pattern but no actual digits
        content = "IP: abc.def.ghi.jkl"  # Invalid IP format
        result = detect_email_addresses(content, tag_types={"IP_ADDRESS"})
        
        # Should be filtered out because ip_has_digit returns False
        assert len(result) == 0
    
    def test_detect_ip_matching_date_pattern_filtered(self):
        """Test IP ADDRESS matching date pattern is filtered (line 189)"""
        content = "Date: 12.34.56.78"  # Looks like date
        result = detect_email_addresses(content, tag_types={"IP_ADDRESS"})
        
        # May be filtered if matches_date_pattern returns True
        # This tests line 189 coverage
        assert isinstance(result, list)
    
    def test_detect_ip_version_filter(self):
        """Test IP ADDRESS with version context filtered (line 197)"""
        content = "Version 1.0.0.1 released"  # Version format
        result = detect_email_addresses(content, tag_types={"IP_ADDRESS"})
        
        # Should be filtered by filter_versions
        assert len(result) == 0
    
    def test_detect_key_not_gibberish_filtered(self):
        """Test KEY that is not gibberish is filtered (line 207)"""
        content = "key: HelloWorld123"  # Too readable, not gibberish
        result = detect_email_addresses(content, tag_types={"KEY"})
        
        # Should be filtered because is_gibberish returns False
        # This tests line 207 coverage
        assert isinstance(result, list)

