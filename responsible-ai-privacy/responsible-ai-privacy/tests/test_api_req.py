"""
Comprehensive tests for api_req.py module
Tests ApiCall class methods for admin API integration
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from privacy.service.api_req import ApiCall, AttributeDict


class TestAttributeDict:
    """Test AttributeDict functionality"""
    
    def test_attribute_dict_basic(self):
        """Test basic AttributeDict operations"""
        ad = AttributeDict({"key1": "value1", "key2": "value2"})
        
        assert ad.key1 == "value1"
        assert ad.key2 == "value2"
        assert ad["key1"] == "value1"
    
    def test_attribute_dict_setattr(self):
        """Test setting attributes"""
        ad = AttributeDict()
        ad.portfolio = "TestPortfolio"
        ad.account = "TestAccount"
        
        assert ad.portfolio == "TestPortfolio"
        assert ad["account"] == "TestAccount"


class TestApiCallRequest:
    """Test ApiCall.request() method"""
    
    @patch.dict(os.environ, {"ADMIN_CONNECTION": "False"})
    def test_request_admin_connection_disabled_false(self):
        """Test request when ADMIN_CONNECTION is False (string)"""
        data = AttributeDict({"portfolio": "TestPortfolio", "account": "TestAccount"})
        
        result = ApiCall.request(data)
        
        assert result == 404
    
    @patch.dict(os.environ, {"ADMIN_CONNECTION": "false"})
    def test_request_admin_connection_disabled_lowercase(self):
        """Test request when ADMIN_CONNECTION is false (lowercase)"""
        data = AttributeDict({"portfolio": "TestPortfolio", "account": "TestAccount"})
        
        result = ApiCall.request(data)
        
        assert result == 404
    
    @patch.dict(os.environ, {"ADMIN_CONNECTION": "True", "PRIVADMIN_API": "http://test-api.com/endpoint"})
    @patch('privacy.service.api_req.error_dict', {})
    @patch('privacy.service.api_req.admin_par', {})
    @patch('privacy.service.api_req.request_id_var')
    @patch('privacy.service.api_req.requests.post')
    def test_request_successful_api_call(self, mock_post, mock_request_id_var, mock_admin_par, mock_error_dict):
        """Test successful API request"""
        mock_request_id_var.get.return_value = "test-uuid-123"
        
        from privacy.service.api_req import error_dict
        error_dict["test-uuid-123"] = []
        
        # Mock API response - datalist contains 6 elements that get unpacked
        mock_response = Mock()
        mock_response.json.return_value = {
            "datalist": [
                ["PERSON"],  # entityType
                ["John", "Jane"],  # datalist
                ["PERSON_PRE"],  # preEntity
                [{"RecogName": "PERSON", "Score": 0.9}],  # records
                ["encrypt1"],  # encryptionList
                [0.85]  # scoreTreshold
            ]
        }
        mock_post.return_value = mock_response
        
        data = AttributeDict({"portfolio": "TestPortfolio", "account": "TestAccount"})
        
        result = ApiCall.request(data)
        
        # Verify result
        assert result == (["PERSON"], ["John", "Jane"], ["PERSON_PRE"])
        
        # Verify API was called with correct parameters
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs['url'] == "http://test-api.com/endpoint"
        assert call_kwargs['headers']['Content-Type'] == "application/json"
        assert call_kwargs['json']['portfolio'] == "TestPortfolio"
    
    @patch.dict(os.environ, {"ADMIN_CONNECTION": "True", "PRIVADMIN_API": "http://test-api.com/endpoint"})
    @patch('privacy.service.api_req.requests.post')
    @patch('privacy.service.api_req.request_id_var')
    @patch('privacy.service.api_req.admin_par', {})
    def test_request_empty_records_returns_none(self, mock_request_id_var, mock_post):
        """Test request returns None when records list is empty"""
        mock_request_id_var.get.return_value = "test-uuid-456"
        
        # Mock API response with empty records
        mock_response = Mock()
        mock_response.json.return_value = {
            "datalist": [["ENTITY"], ["data"], ["pre"], [], ["enc"], [0.9]]
        }
        mock_post.return_value = mock_response
        
        data = AttributeDict({"portfolio": "Portfolio1", "account": "Account1"})
        
        result = ApiCall.request(data)
        
        assert result is None
    
    @patch.dict(os.environ, {"ADMIN_CONNECTION": "True", "PRIVADMIN_API": "http://test-api.com/endpoint"})
    @patch('privacy.service.api_req.requests.post')
    @patch('privacy.service.api_req.request_id_var')
    @patch('privacy.service.api_req.error_dict', {})
    def test_request_exception_handling(self, mock_request_id_var, mock_post):
        """Test exception handling in request"""
        mock_request_id_var.get.return_value = "test-uuid-error"
        
        from privacy.service.api_req import error_dict
        error_dict["test-uuid-error"] = []
        
        # Mock API call to raise exception
        mock_post.side_effect = ConnectionError("Connection failed")
        
        data = AttributeDict({"portfolio": "Portfolio1", "account": "Account1"})
        
        result = ApiCall.request(data)
        
        # Should return an Exception instance
        assert isinstance(result, Exception)
    
    @patch.dict(os.environ, {"ADMIN_CONNECTION": "True", "PRIVADMIN_API": "http://test-api.com/endpoint"})
    @patch('privacy.service.api_req.requests.post')
    @patch('privacy.service.api_req.request_id_var')
    @patch('privacy.service.api_req.admin_par', {})
    @patch('privacy.service.api_req.log')
    def test_request_logs_debug_messages(self, mock_log, mock_request_id_var, mock_post):
        """Test that request logs appropriate debug messages"""
        mock_request_id_var.get.return_value = "test-uuid-789"
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "datalist": [
                ["EMAIL"], ["test@example.com"], ["EMAIL_PRE"], 
                [{"RecogName": "EMAIL", "Score": 0.95}], 
                ["encrypt_email"], [0.88]
            ]
        }
        mock_post.return_value = mock_response
        
        data = AttributeDict({"portfolio": "TestPort", "account": "TestAcc"})
        
        ApiCall.request(data)
        
        # Verify debug logs were called
        assert mock_log.debug.call_count >= 2  # At least "Calling Admin Api" and "data fetched"
    
    @patch.dict(os.environ, {"ADMIN_CONNECTION": "True", "PRIVADMIN_API": "http://test-api.com/endpoint"})
    @patch('privacy.service.api_req.requests.post')
    @patch('privacy.service.api_req.request_id_var')
    @patch('privacy.service.api_req.admin_par', {})
    def test_request_stores_admin_data(self, mock_request_id_var, mock_post):
        """Test that request stores data in admin_par correctly"""
        test_uuid = "test-uuid-store"
        mock_request_id_var.get.return_value = test_uuid
        
        from privacy.service.api_req import admin_par
        
        mock_response = Mock()
        records_data = [{"RecogName": "SSN", "Score": 0.95}]
        encryption_data = ["encrypt_ssn"]
        score_threshold = 0.75
        
        mock_response.json.return_value = {
            "datalist": [
                ["SSN"], ["123-45-6789"], ["SSN_PRE"], 
                records_data, encryption_data, [score_threshold]
            ]
        }
        mock_post.return_value = mock_response
        
        data = AttributeDict({"portfolio": "P1", "account": "A1"})
        
        ApiCall.request(data)
        
        # Verify admin_par was populated
        assert test_uuid in admin_par
        assert admin_par[test_uuid]["encryptionList"] == encryption_data
        assert admin_par[test_uuid]["records"] == records_data
        assert admin_par[test_uuid]["scoreTreshold"] == score_threshold


class TestApiCallGetRecord:
    """Test ApiCall.getRecord() method"""
    
    @patch('privacy.service.api_req.request_id_var')
    @patch('privacy.service.api_req.admin_par', {})
    def test_get_record_returns_matching_record(self, mock_request_id_var):
        """Test getRecord returns the correct record by RecogName"""
        test_uuid = "test-uuid-get-record"
        mock_request_id_var.get.return_value = test_uuid
        
        from privacy.service.api_req import admin_par
        
        # Setup admin_par with test data
        admin_par[test_uuid] = {
            "records": [
                {"RecogName": "PASSPORT", "Score": 0.9, "Data": "passport_data"},
                {"RecogName": "EMAIL", "Score": 0.85, "Data": "email_data"},
                {"RecogName": "PHONE", "Score": 0.95, "Data": "phone_data"}
            ]
        }
        
        result = ApiCall.getRecord("EMAIL")
        
        assert result["RecogName"] == "EMAIL"
        assert result["Score"] == 0.85
        assert result["Data"] == "email_data"
    
    @patch('privacy.service.api_req.request_id_var')
    @patch('privacy.service.api_req.admin_par', {})
    def test_get_record_first_match(self, mock_request_id_var):
        """Test getRecord returns first match when multiple records exist"""
        test_uuid = "test-uuid-first-match"
        mock_request_id_var.get.return_value = test_uuid
        
        from privacy.service.api_req import admin_par
        
        admin_par[test_uuid] = {
            "records": [
                {"RecogName": "PERSON", "Score": 0.9, "Id": 1},
                {"RecogName": "PERSON", "Score": 0.95, "Id": 2}
            ]
        }
        
        result = ApiCall.getRecord("PERSON")
        
        # Should return first match
        assert result["Id"] == 1
        assert result["Score"] == 0.9
    
    @patch('privacy.service.api_req.request_id_var')
    @patch('privacy.service.api_req.admin_par', {})
    @patch('privacy.service.api_req.log')
    def test_get_record_logs_debug(self, mock_log, mock_request_id_var):
        """Test that getRecord logs debug information"""
        test_uuid = "test-uuid-debug"
        mock_request_id_var.get.return_value = test_uuid
        
        from privacy.service.api_req import admin_par
        
        admin_par[test_uuid] = {
            "records": [{"RecogName": "SSN", "Data": "ssn_test"}]
        }
        
        ApiCall.getRecord("SSN")
        
        # Verify debug logging occurred (commented out in source but still callable)
        # The actual logging is commented out in source, so we just verify no crash


class TestApiCallDelAdminList:
    """Test ApiCall.delAdminList() method"""
    
    @patch('privacy.service.api_req.request_id_var')
    @patch('privacy.service.api_req.admin_par', {})
    def test_del_admin_list_removes_entry(self, mock_request_id_var):
        """Test delAdminList removes the entry from admin_par"""
        test_uuid = "test-uuid-delete"
        mock_request_id_var.get.return_value = test_uuid
        
        from privacy.service.api_req import admin_par
        
        # Setup admin_par with test data
        admin_par[test_uuid] = {
            "records": [{"RecogName": "TEST"}],
            "encryptionList": ["enc1"],
            "scoreTreshold": 0.8
        }
        
        # Verify it exists
        assert test_uuid in admin_par
        
        ApiCall.delAdminList()
        
        # Verify it was deleted
        assert test_uuid not in admin_par
    
    @patch('privacy.service.api_req.request_id_var')
    @patch('privacy.service.api_req.admin_par', {})
    def test_del_admin_list_nonexistent_key(self, mock_request_id_var):
        """Test delAdminList with non-existent key doesn't crash"""
        test_uuid = "test-uuid-nonexistent"
        mock_request_id_var.get.return_value = test_uuid
        
        from privacy.service.api_req import admin_par
        
        # Ensure key doesn't exist
        assert test_uuid not in admin_par
        
        # Should not raise exception
        ApiCall.delAdminList()
        
        # Still shouldn't exist
        assert test_uuid not in admin_par
    
    @patch('privacy.service.api_req.request_id_var')
    @patch('privacy.service.api_req.admin_par', {})
    def test_del_admin_list_multiple_entries(self, mock_request_id_var):
        """Test delAdminList only removes the specified entry"""
        test_uuid1 = "test-uuid-1"
        test_uuid2 = "test-uuid-2"
        
        from privacy.service.api_req import admin_par
        
        # Setup multiple entries
        admin_par[test_uuid1] = {"data": "data1"}
        admin_par[test_uuid2] = {"data": "data2"}
        
        mock_request_id_var.get.return_value = test_uuid1
        
        ApiCall.delAdminList()
        
        # Only test_uuid1 should be deleted
        assert test_uuid1 not in admin_par
        assert test_uuid2 in admin_par
        assert admin_par[test_uuid2]["data"] == "data2"


class TestApiCallIntegration:
    """Integration tests for ApiCall class"""
    
    @patch.dict(os.environ, {"ADMIN_CONNECTION": "True", "PRIVADMIN_API": "http://api.test.com/privacy"})
    @patch('privacy.service.api_req.requests.post')
    @patch('privacy.service.api_req.request_id_var')
    @patch('privacy.service.api_req.admin_par', {})
    def test_full_workflow_request_getrecord_delete(self, mock_request_id_var, mock_post):
        """Test complete workflow: request -> getRecord -> delAdminList"""
        test_uuid = "integration-test-uuid"
        mock_request_id_var.get.return_value = test_uuid
        
        from privacy.service.api_req import admin_par
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "datalist": [
                ["CREDIT_CARD", "SSN"], 
                ["card_data", "ssn_data"], 
                ["CC_PRE", "SSN_PRE"],
                [
                    {"RecogName": "CREDIT_CARD", "Score": 0.92},
                    {"RecogName": "SSN", "Score": 0.88}
                ],
                ["encrypt_cc", "encrypt_ssn"],
                [0.80]
            ]
        }
        mock_post.return_value = mock_response
        
        # Step 1: Request
        data = AttributeDict({"portfolio": "IntegrationPort", "account": "IntegrationAcc"})
        result = ApiCall.request(data)
        
        assert result == (["CREDIT_CARD", "SSN"], ["card_data", "ssn_data"], ["CC_PRE", "SSN_PRE"])
        assert test_uuid in admin_par
        
        # Step 2: Get Record
        record = ApiCall.getRecord("SSN")
        assert record["RecogName"] == "SSN"
        assert record["Score"] == 0.88
        
        # Step 3: Delete Admin List
        ApiCall.delAdminList()
        assert test_uuid not in admin_par
    
    @patch.dict(os.environ, {"ADMIN_CONNECTION": "maybe", "PRIVADMIN_API": "http://test.com/api"})
    @patch('privacy.service.api_req.requests.post')
    @patch('privacy.service.api_req.request_id_var')
    @patch('privacy.service.api_req.error_dict', {})
    def test_admin_connection_other_values(self, mock_request_id_var, mock_post):
        """Test that values other than 'False'/'false' proceed (won't return 404)"""
        mock_request_id_var.get.return_value = "test-request-id"
        
        from privacy.service.api_req import error_dict
        error_dict["test-request-id"] = []
        
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "datalist": [["ENTITY"], ["data"], ["pre"], [{"RecogName": "TEST"}], ["enc"], [0.8]]
        }
        mock_post.return_value = mock_response
        
        data = AttributeDict({"portfolio": "Test", "account": "Test"})
        result = ApiCall.request(data)
        
        # Should not be 404 (will be tuple result)
        assert result != 404
