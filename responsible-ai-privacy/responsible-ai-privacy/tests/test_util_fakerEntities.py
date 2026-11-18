"""
Tests for FakeData utility class.
Testing all static methods for generating fake PII data.
"""

import pytest
from privacy.util.fakerEntities import FakeData


class TestFakeDataMethods:
    """Test all FakeData static methods."""
    
    def test_person(self):
        """Test person() method returns valid name."""
        result = FakeData.person()
        assert isinstance(result, str)
        assert len(result) > 0
        assert result != ""
    
    def test_email_address(self):
        """Test email_address() method returns valid email."""
        result = FakeData.email_address()
        assert isinstance(result, str)
        assert '@' in result
        assert len(result) > 0
    
    def test_us_ssn(self):
        """Test us_ssn() method returns valid SSN format."""
        result = FakeData.us_ssn()
        assert isinstance(result, str)
        assert len(result) > 0
        # SSN format: XXX-XX-XXXX
        assert result.replace('-', '').isdigit() or len(result) == 11
    
    def test_address(self):
        """Test address() method returns valid address."""
        result = FakeData.address()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_date_time(self):
        """Test date_time() method returns valid datetime string."""
        result = FakeData.date_time()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_location(self):
        """Test location() method returns valid location."""
        result = FakeData.location()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_credit_card(self):
        """Test credit_card() method returns valid credit card number."""
        result = FakeData.credit_card()
        assert isinstance(result, str)
        assert len(result) > 0
        # Credit card numbers are typically 13-19 digits
        digits_only = result.replace(' ', '').replace('-', '')
        assert digits_only.isdigit() or len(digits_only) >= 13
    
    def test_crypto(self):
        """Test crypto() method returns valid crypto address."""
        result = FakeData.crypto()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_date(self):
        """Test date() method returns valid date string."""
        result = FakeData.date()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_ip_address(self):
        """Test ip_address() method returns valid IP."""
        result = FakeData.ip_address()
        assert isinstance(result, str)
        assert len(result) > 0
        # Basic IP format check
        parts = result.split('.')
        assert len(parts) == 4 or ':' in result  # IPv4 or IPv6
    
    def test_phone_number(self):
        """Test phone_number() method returns valid phone."""
        result = FakeData.phone_number()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_iban_code(self):
        """Test iban_code() method returns valid IBAN."""
        result = FakeData.iban_code()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_passport(self):
        """Test passport() method returns valid passport number."""
        result = FakeData.passport()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_data_list_with_multiple_items(self):
        """Test data_list() with multiple items."""
        data_list = ['apple', 'banana', 'cherry', 'date']
        text = 'apple'
        
        result = FakeData.data_list(data_list, text)
        assert result in data_list
        assert result.lower() != text.lower()
    
    def test_data_list_filters_matching_item(self):
        """Test data_list() filters out the matching text."""
        data_list = ['Item1', 'Item2', 'Item3']
        text = 'item2'
        
        result = FakeData.data_list(data_list, text)
        assert result.lower() != text.lower()
        assert result in data_list
    
    def test_data_list_with_single_different_item(self):
        """Test data_list() with only one different item."""
        data_list = ['same', 'different']
        text = 'same'
        
        result = FakeData.data_list(data_list, text)
        assert result == 'different'
    
    def test_data_list_case_insensitive(self):
        """Test data_list() is case insensitive."""
        data_list = ['UPPER', 'lower', 'MiXeD']
        text = 'LOWER'
        
        result = FakeData.data_list(data_list, text)
        assert result.lower() != text.lower()
        assert result in data_list


class TestFakeDataReturnTypes:
    """Test that all methods return expected types."""
    
    def test_all_methods_return_strings(self):
        """Test all methods return string type."""
        methods = [
            FakeData.person,
            FakeData.email_address,
            FakeData.us_ssn,
            FakeData.address,
            FakeData.date_time,
            FakeData.location,
            FakeData.credit_card,
            FakeData.crypto,
            FakeData.date,
            FakeData.ip_address,
            FakeData.phone_number,
            FakeData.iban_code,
            FakeData.passport
        ]
        
        for method in methods:
            result = method()
            assert isinstance(result, str), f"{method.__name__} did not return string"
            assert len(result) > 0, f"{method.__name__} returned empty string"
    
    def test_multiple_calls_produce_different_values(self):
        """Test that multiple calls to methods produce different values (usually)."""
        # This tests randomness - not guaranteed but highly likely
        names = [FakeData.person() for _ in range(5)]
        # At least some should be different
        assert len(set(names)) > 1, "All generated names are identical"
        
        emails = [FakeData.email_address() for _ in range(5)]
        assert len(set(emails)) > 1, "All generated emails are identical"
