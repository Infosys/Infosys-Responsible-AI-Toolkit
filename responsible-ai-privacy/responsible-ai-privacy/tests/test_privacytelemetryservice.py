"""
Comprehensive test suite for privacy.service.privacytelemetryservice module.

This module tests the PrivacyTelemetryRequest class to achieve >90% code coverage
without modifying the source code.
"""

import pytest
from privacy.service.privacytelemetryservice import PrivacyTelemetryRequest


class TestPrivacyTelemetryRequest:
    """Test suite for PrivacyTelemetryRequest class."""
    
    def test_init_with_all_parameters(self):
        """Test PrivacyTelemetryRequest initialization with all parameters provided."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText="John Doe",
            restype="PERSON",
            portfolio="test_portfolio",
            accountname="test_account",
            exclusion_list="exclude1,exclude2,exclude3",
            entityrecognised="PERSON,EMAIL",
            inputText="Sample input text"
        )
        
        assert request.tenant == "test_tenant"
        assert request.apiname == "analyze_api"
        assert request.date == "2025-12-31"
        assert request.user == "test_user"
        
        # Verify privacy_requests
        assert request.privacy_requests['portfolio_name'] == "test_portfolio"
        assert request.privacy_requests['account_name'] == "test_account"
        assert request.privacy_requests['exclusion_list'] == ["exclude1", "exclude2", "exclude3"]
        assert request.privacy_requests['inputText'] == "Sample input text"
        
        # Verify privacy_response
        assert request.privacy_response['type'] == "PERSON"
        assert request.privacy_response['beginOffset'] == 0.0
        assert request.privacy_response['endOffset'] == 10.0
        assert request.privacy_response['score'] == 0.95
        assert request.privacy_response['responseText'] == "John Doe"
    
    def test_init_with_none_portfolio(self):
        """Test initialization when portfolio is None."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText="test",
            restype="PERSON",
            portfolio=None
        )
        
        assert request.privacy_requests['portfolio_name'] == "None"
    
    def test_init_with_none_accountname(self):
        """Test initialization when accountname is None."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText="test",
            restype="PERSON",
            accountname=None
        )
        
        assert request.privacy_requests['account_name'] == "None"
    
    def test_init_with_none_exclusion_list(self):
        """Test initialization when exclusion_list is None."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText="test",
            restype="PERSON",
            exclusion_list=None
        )
        
        assert request.privacy_requests['exclusion_list'] == []
    
    def test_init_with_empty_exclusion_list(self):
        """Test initialization with empty exclusion_list string."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText="test",
            restype="PERSON",
            exclusion_list=""
        )
        
        assert request.privacy_requests['exclusion_list'] == [""]
    
    def test_init_with_single_exclusion(self):
        """Test initialization with single item in exclusion_list."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText="test",
            restype="PERSON",
            exclusion_list="single_item"
        )
        
        assert request.privacy_requests['exclusion_list'] == ["single_item"]
    
    def test_init_with_none_inputText(self):
        """Test initialization when inputText is None."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText="test",
            restype="PERSON",
            inputText=None
        )
        
        assert request.privacy_requests['inputText'] == "None"
    
    def test_init_with_none_restype(self):
        """Test initialization when restype is None."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText="test",
            restype=None
        )
        
        assert request.privacy_response['type'] == "None"
    
    def test_init_with_none_beginOffset(self):
        """Test initialization when beginOffset is None."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=None,
            endOffset=10,
            score=0.95,
            responseText="test",
            restype="PERSON"
        )
        
        assert request.privacy_response['beginOffset'] == 0
    
    def test_init_with_none_endOffset(self):
        """Test initialization when endOffset is None."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=None,
            score=0.95,
            responseText="test",
            restype="PERSON"
        )
        
        assert request.privacy_response['endOffset'] == 0
    
    def test_init_with_none_score(self):
        """Test initialization when score is None."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=None,
            responseText="test",
            restype="PERSON"
        )
        
        assert request.privacy_response['score'] == "None"
    
    def test_init_with_none_responseText(self):
        """Test initialization when responseText is None."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText=None,
            restype="PERSON"
        )
        
        assert request.privacy_response['responseText'] == "None"
    
    def test_init_with_integer_offsets(self):
        """Test initialization with integer offsets (should convert to float)."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=5,
            endOffset=15,
            score=1,
            responseText="test",
            restype="PERSON"
        )
        
        assert request.privacy_response['beginOffset'] == 5.0
        assert request.privacy_response['endOffset'] == 15.0
        assert request.privacy_response['score'] == 1.0
        assert isinstance(request.privacy_response['beginOffset'], float)
        assert isinstance(request.privacy_response['endOffset'], float)
        assert isinstance(request.privacy_response['score'], float)
    
    def test_init_with_string_offsets(self):
        """Test initialization with string offsets (should convert to float)."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset="10.5",
            endOffset="20.7",
            score="0.85",
            responseText="test",
            restype="PERSON"
        )
        
        assert request.privacy_response['beginOffset'] == 10.5
        assert request.privacy_response['endOffset'] == 20.7
        assert request.privacy_response['score'] == 0.85
    
    def test_init_with_zero_offsets_and_score(self):
        """Test initialization with zero values for offsets and score."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=0,
            score=0,
            responseText="test",
            restype="PERSON"
        )
        
        assert request.privacy_response['beginOffset'] == 0.0
        assert request.privacy_response['endOffset'] == 0.0
        assert request.privacy_response['score'] == 0.0
    
    def test_init_with_negative_offsets(self):
        """Test initialization with negative offsets."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=-5,
            endOffset=-10,
            score=-0.5,
            responseText="test",
            restype="PERSON"
        )
        
        assert request.privacy_response['beginOffset'] == -5.0
        assert request.privacy_response['endOffset'] == -10.0
        assert request.privacy_response['score'] == -0.5
    
    def test_init_with_large_offsets(self):
        """Test initialization with large offset values."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=1000000,
            endOffset=2000000,
            score=0.99999,
            responseText="test",
            restype="PERSON"
        )
        
        assert request.privacy_response['beginOffset'] == 1000000.0
        assert request.privacy_response['endOffset'] == 2000000.0
        assert request.privacy_response['score'] == 0.99999
    
    def test_init_with_complex_exclusion_list(self):
        """Test initialization with complex exclusion list containing special characters."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText="test",
            restype="PERSON",
            exclusion_list="item1,item-2,item_3,item.4"
        )
        
        assert request.privacy_requests['exclusion_list'] == ["item1", "item-2", "item_3", "item.4"]
    
    def test_init_with_long_strings(self):
        """Test initialization with very long strings."""
        long_text = "A" * 10000
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10000,
            score=0.95,
            responseText=long_text,
            restype="PERSON",
            inputText=long_text
        )
        
        assert request.privacy_requests['inputText'] == long_text
        assert request.privacy_response['responseText'] == long_text
        assert len(request.privacy_response['responseText']) == 10000
    
    def test_init_with_special_characters_in_strings(self):
        """Test initialization with special characters in string fields."""
        request = PrivacyTelemetryRequest(
            tenant="tenant@#$%",
            apiname="api!@#",
            date="2025-12-31 10:30:45",
            user="user&*(",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText="response <>&",
            restype="TYPE!",
            portfolio="portfolio\"'",
            accountname="account\n\t",
            inputText="input\r\n"
        )
        
        assert request.tenant == "tenant@#$%"
        assert request.apiname == "api!@#"
        assert request.user == "user&*("
        assert request.privacy_response['responseText'] == "response <>&"
        assert request.privacy_response['type'] == "TYPE!"
    
    def test_init_with_unicode_characters(self):
        """Test initialization with unicode characters."""
        request = PrivacyTelemetryRequest(
            tenant="租户",
            apiname="分析API",
            date="2025-12-31",
            user="用户",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText="响应文本",
            restype="类型",
            inputText="输入文本"
        )
        
        assert request.tenant == "租户"
        assert request.apiname == "分析API"
        assert request.user == "用户"
        assert request.privacy_response['responseText'] == "响应文本"
        assert request.privacy_requests['inputText'] == "输入文本"
    
    def test_init_with_numeric_strings_converted(self):
        """Test that numeric values are properly converted to strings where needed."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText=12345,  # Integer
            restype=999,  # Integer
            portfolio=100,  # Integer
            accountname=200,  # Integer
            inputText=300  # Integer
        )
        
        assert request.privacy_response['responseText'] == "12345"
        assert request.privacy_response['type'] == "999"
        assert request.privacy_requests['portfolio_name'] == "100"
        assert request.privacy_requests['account_name'] == "200"
        assert request.privacy_requests['inputText'] == "300"
    
    def test_init_minimal_required_parameters(self):
        """Test initialization with only required parameters."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText="test",
            restype="PERSON"
        )
        
        assert request.tenant == "test_tenant"
        assert request.apiname == "analyze_api"
        assert request.date == "2025-12-31"
        assert request.user == "test_user"
        assert request.privacy_requests['portfolio_name'] == "None"
        assert request.privacy_requests['account_name'] == "None"
        assert request.privacy_requests['exclusion_list'] == []
        assert request.privacy_requests['inputText'] == "None"
    
    def test_init_empty_strings(self):
        """Test initialization with empty strings."""
        request = PrivacyTelemetryRequest(
            tenant="",
            apiname="",
            date="",
            user="",
            beginOffset=0,
            endOffset=0,
            score=0,
            responseText="",
            restype="",
            portfolio="",
            accountname="",
            inputText=""
        )
        
        assert request.tenant == ""
        assert request.apiname == ""
        assert request.date == ""
        assert request.user == ""
        assert request.privacy_requests['portfolio_name'] == ""
        assert request.privacy_requests['account_name'] == ""
        assert request.privacy_requests['inputText'] == ""
        assert request.privacy_response['responseText'] == ""
        assert request.privacy_response['type'] == ""
    
    def test_privacy_requests_structure(self):
        """Test that privacy_requests dictionary has correct structure."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText="test",
            restype="PERSON"
        )
        
        assert isinstance(request.privacy_requests, dict)
        assert 'portfolio_name' in request.privacy_requests
        assert 'account_name' in request.privacy_requests
        assert 'exclusion_list' in request.privacy_requests
        assert 'inputText' in request.privacy_requests
        assert len(request.privacy_requests) == 4
    
    def test_privacy_response_structure(self):
        """Test that privacy_response dictionary has correct structure."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText="test",
            restype="PERSON"
        )
        
        assert isinstance(request.privacy_response, dict)
        assert 'type' in request.privacy_response
        assert 'beginOffset' in request.privacy_response
        assert 'endOffset' in request.privacy_response
        assert 'score' in request.privacy_response
        assert 'responseText' in request.privacy_response
        assert len(request.privacy_response) == 5
    
    def test_exclusion_list_with_whitespace(self):
        """Test exclusion list handling with whitespace around commas."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText="test",
            restype="PERSON",
            exclusion_list="item1, item2 , item3,item4"
        )
        
        # Note: split doesn't trim whitespace, so items will include spaces
        assert request.privacy_requests['exclusion_list'] == ["item1", " item2 ", " item3", "item4"]
    
    def test_boolean_values_converted_to_string(self):
        """Test that boolean values are properly converted to strings."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText=True,
            restype=False,
            portfolio=True,
            accountname=False,
            inputText=True
        )
        
        assert request.privacy_response['responseText'] == "True"
        assert request.privacy_response['type'] == "False"
        assert request.privacy_requests['portfolio_name'] == "True"
        assert request.privacy_requests['account_name'] == "False"
        assert request.privacy_requests['inputText'] == "True"
    
    def test_float_precision_preserved(self):
        """Test that float precision is preserved in offsets and score."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=1.23456789,
            endOffset=9.87654321,
            score=0.123456789,
            responseText="test",
            restype="PERSON"
        )
        
        assert request.privacy_response['beginOffset'] == 1.23456789
        assert request.privacy_response['endOffset'] == 9.87654321
        assert request.privacy_response['score'] == 0.123456789


class TestPrivacyTelemetryRequestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_all_none_optional_parameters(self):
        """Test with all optional parameters set to None."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=None,
            endOffset=None,
            score=None,
            responseText=None,
            restype=None,
            portfolio=None,
            accountname=None,
            exclusion_list=None,
            entityrecognised=None,
            inputText=None
        )
        
        assert request.privacy_requests['portfolio_name'] == "None"
        assert request.privacy_requests['account_name'] == "None"
        assert request.privacy_requests['exclusion_list'] == []
        assert request.privacy_requests['inputText'] == "None"
        assert request.privacy_response['type'] == "None"
        assert request.privacy_response['beginOffset'] == 0
        assert request.privacy_response['endOffset'] == 0
        assert request.privacy_response['score'] == "None"
        assert request.privacy_response['responseText'] == "None"
    
    def test_exclusion_list_single_comma(self):
        """Test exclusion list with just a comma."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText="test",
            restype="PERSON",
            exclusion_list=","
        )
        
        assert request.privacy_requests['exclusion_list'] == ["", ""]
    
    def test_exclusion_list_multiple_commas(self):
        """Test exclusion list with multiple consecutive commas."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText="test",
            restype="PERSON",
            exclusion_list="item1,,,item2"
        )
        
        assert request.privacy_requests['exclusion_list'] == ["item1", "", "", "item2"]
    
    def test_very_high_score(self):
        """Test with score greater than 1."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=100.5,
            responseText="test",
            restype="PERSON"
        )
        
        assert request.privacy_response['score'] == 100.5
    
    def test_entityrecognised_parameter_stored(self):
        """Test that entityrecognised parameter is accepted (though not stored in dict)."""
        # This parameter is accepted by __init__ but not used in the instance
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText="test",
            restype="PERSON",
            entityrecognised="PERSON,EMAIL,PHONE"
        )
        
        # entityrecognised is not stored anywhere, just verifying it doesn't cause errors
        assert request.tenant == "test_tenant"


class TestPrivacyTelemetryRequestTypeConversions:
    """Test type conversion behaviors."""
    
    def test_list_converted_to_string_in_privacy_requests(self):
        """Test that list values are converted to strings."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText="test",
            restype="PERSON",
            portfolio=["item1", "item2"],
            accountname=["acc1", "acc2"],
            inputText=["text1", "text2"]
        )
        
        assert request.privacy_requests['portfolio_name'] == "['item1', 'item2']"
        assert request.privacy_requests['account_name'] == "['acc1', 'acc2']"
        assert request.privacy_requests['inputText'] == "['text1', 'text2']"
    
    def test_dict_converted_to_string(self):
        """Test that dict values are converted to strings."""
        request = PrivacyTelemetryRequest(
            tenant="test_tenant",
            apiname="analyze_api",
            date="2025-12-31",
            user="test_user",
            beginOffset=0,
            endOffset=10,
            score=0.95,
            responseText={"key": "value"},
            restype={"type": "PERSON"},
            portfolio={"name": "test"},
            accountname={"id": 123},
            inputText={"text": "sample"}
        )
        
        assert "key" in request.privacy_response['responseText']
        assert "type" in request.privacy_response['type']
        assert "name" in request.privacy_requests['portfolio_name']
        assert "id" in request.privacy_requests['account_name']
        assert "text" in request.privacy_requests['inputText']
