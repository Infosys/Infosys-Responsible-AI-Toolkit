"""
Test suite for privacy.util.fakerEntities module.
Tests all FakeData static methods to improve coverage.
"""
import pytest
from privacy.util.fakerEntities import FakeData


class TestFakeDataMethods:
    """Test all FakeData static methods - lines 23-86."""
    
    def test_PERSON_returns_valid_name(self):
        """Test PERSON method returns a name string."""
        result = FakeData.PERSON()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_EMAIL_ADDRESS_returns_valid_email(self):
        """Test EMAIL_ADDRESS method returns an email."""
        result = FakeData.EMAIL_ADDRESS()
        assert isinstance(result, str)
        assert "@" in result
    
    def test_US_SSN_returns_valid_ssn(self):
        """Test US_SSN method returns SSN string."""
        result = FakeData.US_SSN()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_ADDRESS_returns_valid_address(self):
        """Test ADDRESS method returns an address."""
        result = FakeData.ADDRESS()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_DATE_TIME_returns_valid_date(self):
        """Test DATE_TIME method returns a date."""
        result = FakeData.DATE_TIME()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_LOCATION_returns_valid_city(self):
        """Test LOCATION method returns a city name."""
        result = FakeData.LOCATION()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_CREDIT_CARD_returns_valid_number(self):
        """Test CREDIT_CARD method returns credit card number."""
        result = FakeData.CREDIT_CARD()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_CRYPTO_returns_valid_cryptocurrency(self):
        """Test CRYPTO method returns cryptocurrency name."""
        result = FakeData.CRYPTO()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_DATE_returns_valid_date(self):
        """Test DATE method returns a date."""
        result = FakeData.DATE()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_IP_ADDRESS_returns_valid_ipv4(self):
        """Test IP_ADDRESS method returns IPv4 address."""
        result = FakeData.IP_ADDRESS()
        assert isinstance(result, str)
        assert "." in result  # IPv4 format
    
    def test_PHONE_NUMBER_returns_valid_phone(self):
        """Test PHONE_NUMBER method returns phone number."""
        result = FakeData.PHONE_NUMBER()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_IBAN_CODE_returns_valid_iban(self):
        """Test IBAN_CODE method returns IBAN code."""
        result = FakeData.IBAN_CODE()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_PASSPORT_returns_valid_passport(self):
        """Test PASSPORT method returns passport number."""
        result = FakeData.PASSPORT()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_DataList_returns_different_value(self):
        """Test DataList method returns a different value from data."""
        data = ["value1", "value2", "value3", "value4"]
        text = "value1"
        
        result = FakeData.DataList(data, text)
        
        # Result should be from data but not equal to text
        assert result in data
        assert result.lower() != text.lower()
    
    def test_DataList_case_insensitive(self):
        """Test DataList method is case-insensitive."""
        data = ["Value1", "VALUE2", "value3"]
        text = "value1"  # lowercase
        
        result = FakeData.DataList(data, text)
        
        # Should not return Value1 (case-insensitive match)
        assert result.lower() != text.lower()
    
    def test_DataList_with_single_valid_option(self):
        """Test DataList with only one option different from text."""
        data = ["same", "same", "different"]
        text = "same"
        
        result = FakeData.DataList(data, text)
        
        # Should return the only different value
        assert result == "different"
    
    def test_DataList_with_mixed_case_data(self):
        """Test DataList with mixed case data."""
        data = ["Apple", "BANANA", "cherry", "DATE"]
        text = "apple"
        
        result = FakeData.DataList(data, text)
        
        # Should not return Apple (case-insensitive)
        assert result.lower() != "apple"
        assert result in data
