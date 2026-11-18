"""
Comprehensive tests for privacytelemetryservice.py module
Tests cover PrivacyTelemetryRequest initialization and data hashing
"""

import pytest
import hashlib
from privacy.service.privacytelemetryservice import PrivacyTelemetryRequest


class TestPrivacyTelemetryRequestInitialization:
    """Test PrivacyTelemetryRequest initialization with various parameters"""
    
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters"""
        req = PrivacyTelemetryRequest(
            tenant="tenant1",
            apiname="redact_api",
            date="2024-01-15",
            user="user123",
            beginOffset=0,
            endOffset=100,
            score=95.5,
            responseText="Success",
            restype="redact",
            portfolio="portfolio1",
            accountname="account1",
            exclusion_list="pattern1,pattern2",
            entityrecognised="PERSON",
            inputText="John Doe is from New York"
        )
        
        assert req.tenant == "tenant1"
        assert req.apiname == "redact_api"
        assert req.date == "2024-01-15"
        assert req.user == "user123"


class TestPrivacyTelemetryRequestPrivacyRequest:
    """Test privacy_requests dictionary construction"""
    
    def test_privacy_requests_with_all_values(self):
        """Test privacy_requests dict with all non-None values"""
        req = PrivacyTelemetryRequest(
            tenant="tenant1",
            apiname="api1",
            date="2024-01-15",
            user="user1",
            beginOffset=0,
            endOffset=100,
            score=90,
            responseText="OK",
            restype="type1",
            portfolio="portfolio1",
            accountname="account1",
            exclusion_list="list1,list2",
            entityrecognised="PERSON",
            inputText="Sample input text"
        )
        
        assert req.privacy_requests['portfolio_name'] == "portfolio1"
        assert req.privacy_requests['account_name'] == "account1"
        assert req.privacy_requests['exclusion_list'] == ["list1", "list2"]
        assert req.privacy_requests['inputText'] == len("Sample input text")
        assert req.privacy_requests['input_hash'] == hashlib.sha256("Sample input text".encode()).hexdigest()[:16]
    
    def test_privacy_requests_with_none_portfolio(self):
        """Test privacy_requests with None portfolio"""
        req = PrivacyTelemetryRequest(
            tenant="tenant1",
            apiname="api1",
            date="2024-01-15",
            user="user1",
            beginOffset=0,
            endOffset=100,
            score=90,
            responseText="OK",
            restype="type1",
            portfolio=None,
            accountname="account1"
        )
        
        assert req.privacy_requests['portfolio_name'] == "None"
    
    def test_privacy_requests_with_none_accountname(self):
        """Test privacy_requests with None accountname"""
        req = PrivacyTelemetryRequest(
            tenant="tenant1",
            apiname="api1",
            date="2024-01-15",
            user="user1",
            beginOffset=0,
            endOffset=100,
            score=90,
            responseText="OK",
            restype="type1",
            portfolio="portfolio1",
            accountname=None
        )
        
        assert req.privacy_requests['account_name'] == "None"
    
    def test_privacy_requests_with_none_exclusion_list(self):
        """Test privacy_requests with None exclusion_list"""
        req = PrivacyTelemetryRequest(
            tenant="tenant1",
            apiname="api1",
            date="2024-01-15",
            user="user1",
            beginOffset=0,
            endOffset=100,
            score=90,
            responseText="OK",
            restype="type1",
            exclusion_list=None
        )
        
        assert req.privacy_requests['exclusion_list'] == []
    
    def test_privacy_requests_with_none_inputtext(self):
        """Test privacy_requests with None inputText"""
        req = PrivacyTelemetryRequest(
            tenant="tenant1",
            apiname="api1",
            date="2024-01-15",
            user="user1",
            beginOffset=0,
            endOffset=100,
            score=90,
            responseText="OK",
            restype="type1",
            inputText=None
        )
        
        assert req.privacy_requests['inputText'] == 0
        assert req.privacy_requests['input_hash'] == "None"


class TestPrivacyTelemetryRequestPrivacyResponse:
    """Test privacy_response dictionary construction"""
    
    def test_privacy_response_with_type(self):
        """Test privacy_response dict with response type"""
        req = PrivacyTelemetryRequest(
            tenant="tenant1",
            apiname="api1",
            date="2024-01-15",
            user="user1",
            beginOffset=0,
            endOffset=100,
            score=90,
            responseText="OK",
            restype="redact"
        )
        
        assert req.privacy_response['type'] == "redact"
    
    def test_privacy_response_with_none_type(self):
        """Test privacy_response dict with None type"""
        req = PrivacyTelemetryRequest(
            tenant="tenant1",
            apiname="api1",
            date="2024-01-15",
            user="user1",
            beginOffset=0,
            endOffset=100,
            score=90,
            responseText="OK",
            restype=None
        )
        
        assert req.privacy_response['type'] == "None"


class TestPrivacyTelemetryHashGeneration:
    """Test input text hashing functionality"""
    
    def test_input_hash_consistency(self):
        """Test that same input text produces same hash"""
        input_text = "Consistent input text"
        req1 = PrivacyTelemetryRequest(
            tenant="t1", apiname="a1", date="2024-01-15", user="u1",
            beginOffset=0, endOffset=100, score=90, responseText="OK", 
            restype="type1", inputText=input_text
        )
        req2 = PrivacyTelemetryRequest(
            tenant="t2", apiname="a2", date="2024-01-16", user="u2",
            beginOffset=0, endOffset=100, score=90, responseText="OK", 
            restype="type1", inputText=input_text
        )
        
        assert req1.privacy_requests['input_hash'] == req2.privacy_requests['input_hash']
    
    def test_input_hash_different_for_different_text(self):
        """Test that different input texts produce different hashes"""
        req1 = PrivacyTelemetryRequest(
            tenant="t1", apiname="a1", date="2024-01-15", user="u1",
            beginOffset=0, endOffset=100, score=90, responseText="OK", 
            restype="type1", inputText="Text 1"
        )
        req2 = PrivacyTelemetryRequest(
            tenant="t2", apiname="a2", date="2024-01-16", user="u2",
            beginOffset=0, endOffset=100, score=90, responseText="OK", 
            restype="type1", inputText="Text 2"
        )
        
        assert req1.privacy_requests['input_hash'] != req2.privacy_requests['input_hash']
    
    def test_input_hash_truncated_to_16_chars(self):
        """Test that input hash is truncated to 16 characters"""
        req = PrivacyTelemetryRequest(
            tenant="t1", apiname="a1", date="2024-01-15", user="u1",
            beginOffset=0, endOffset=100, score=90, responseText="OK", 
            restype="type1", inputText="Test input"
        )
        
        expected_hash = hashlib.sha256("Test input".encode()).hexdigest()[:16]
        assert req.privacy_requests['input_hash'] == expected_hash
        assert len(req.privacy_requests['input_hash']) == 16


class TestPrivacyTelemetryExclusionListParsing:
    """Test exclusion_list parsing from comma-separated string"""
    
    def test_exclusion_list_single_item(self):
        """Test exclusion_list with single item"""
        req = PrivacyTelemetryRequest(
            tenant="t1", apiname="a1", date="2024-01-15", user="u1",
            beginOffset=0, endOffset=100, score=90, responseText="OK", 
            restype="type1", exclusion_list="pattern1"
        )
        
        assert req.privacy_requests['exclusion_list'] == ["pattern1"]
    
    def test_exclusion_list_multiple_items(self):
        """Test exclusion_list with multiple comma-separated items"""
        req = PrivacyTelemetryRequest(
            tenant="t1", apiname="a1", date="2024-01-15", user="u1",
            beginOffset=0, endOffset=100, score=90, responseText="OK", 
            restype="type1", exclusion_list="pattern1,pattern2,pattern3"
        )
        
        assert req.privacy_requests['exclusion_list'] == ["pattern1", "pattern2", "pattern3"]
    
    def test_exclusion_list_with_spaces(self):
        """Test exclusion_list preserves spaces in items"""
        req = PrivacyTelemetryRequest(
            tenant="t1", apiname="a1", date="2024-01-15", user="u1",
            beginOffset=0, endOffset=100, score=90, responseText="OK", 
            restype="type1", exclusion_list="pattern 1, pattern 2"
        )
        
        # Note: split doesn't strip spaces
        assert req.privacy_requests['exclusion_list'] == ["pattern 1", " pattern 2"]


class TestPrivacyTelemetryInputTextLength:
    """Test inputText length calculation"""
    
    def test_inputtext_length_empty_string(self):
        """Test inputText length with empty string"""
        req = PrivacyTelemetryRequest(
            tenant="t1", apiname="a1", date="2024-01-15", user="u1",
            beginOffset=0, endOffset=100, score=90, responseText="OK", 
            restype="type1", inputText=""
        )
        
        assert req.privacy_requests['inputText'] == 0
    
    def test_inputtext_length_with_unicode(self):
        """Test inputText length with unicode characters"""
        unicode_text = "Hello 你好 مرحبا"
        req = PrivacyTelemetryRequest(
            tenant="t1", apiname="a1", date="2024-01-15", user="u1",
            beginOffset=0, endOffset=100, score=90, responseText="OK", 
            restype="type1", inputText=unicode_text
        )
        
        assert req.privacy_requests['inputText'] == len(unicode_text)
    
    def test_inputtext_length_large_text(self):
        """Test inputText length with large text"""
        large_text = "A" * 10000
        req = PrivacyTelemetryRequest(
            tenant="t1", apiname="a1", date="2024-01-15", user="u1",
            beginOffset=0, endOffset=100, score=90, responseText="OK", 
            restype="type1", inputText=large_text
        )
        
        assert req.privacy_requests['inputText'] == 10000


class TestPrivacyTelemetryAttributeTypes:
    """Test attribute types and conversions"""
    
    def test_numeric_portfolio_converted_to_string(self):
        """Test that numeric portfolio is converted to string"""
        req = PrivacyTelemetryRequest(
            tenant="t1", apiname="a1", date="2024-01-15", user="u1",
            beginOffset=0, endOffset=100, score=90, responseText="OK", 
            restype="type1", portfolio=12345
        )
        
        assert req.privacy_requests['portfolio_name'] == "12345"
        assert isinstance(req.privacy_requests['portfolio_name'], str)
    
    def test_numeric_accountname_converted_to_string(self):
        """Test that numeric accountname is converted to string"""
        req = PrivacyTelemetryRequest(
            tenant="t1", apiname="a1", date="2024-01-15", user="u1",
            beginOffset=0, endOffset=100, score=90, responseText="OK", 
            restype="type1", accountname=67890
        )
        
        assert req.privacy_requests['account_name'] == "67890"
        assert isinstance(req.privacy_requests['account_name'], str)
    
    def test_numeric_restype_converted_to_string(self):
        """Test that numeric restype is converted to string"""
        req = PrivacyTelemetryRequest(
            tenant="t1", apiname="a1", date="2024-01-15", user="u1",
            beginOffset=0, endOffset=100, score=90, responseText="OK", 
            restype=123
        )
        
        assert req.privacy_response['type'] == "123"
        assert isinstance(req.privacy_response['type'], str)
