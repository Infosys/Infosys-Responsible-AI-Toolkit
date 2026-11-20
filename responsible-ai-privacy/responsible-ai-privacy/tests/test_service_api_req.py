"""
Comprehensive tests for api_req.py module - API request handling
Tests cover ApiCall.request, get_record, and del_admin_list methods
"""

import os
import pytest
from unittest.mock import patch, MagicMock, call
from privacy.service.api_req import ApiCall
from privacy.service.__init__ import AttributeDict


class TestApiCallRequestSuccess:
    """Test ApiCall.request with successful API responses"""
    
    @patch('privacy.service.api_req.requests.post')
    @patch.dict(os.environ, {'ADMIN_CONNECTION': 'True', 'PRIVADMIN_API': 'http://admin.api'})
    def test_request_success_with_valid_response(self, mock_post):
        """Test successful API call with valid response"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "datalist": [
                "entity_type_val",
                "datalist_val",
                "pre_entity_val",
                [{"RecogName": "test", "data": "value"}],
                ["key1", "key2"],
                [50]
            ]
        }
        mock_post.return_value = mock_response
        
        data = AttributeDict({"portfolio": "test_portfolio", "account": "test_account"})
        
        with patch('privacy.service.api_req.request_id_var') as mock_req_id:
            mock_req_id.get.return_value = "test_uuid"
            with patch('privacy.service.api_req.admin_par', {}) as mock_admin_par:
                result = ApiCall.request(data)
                
                assert result == ("entity_type_val", "datalist_val", "pre_entity_val")
                mock_post.assert_called_once()


class TestApiCallRequestDisabled:
    """Test ApiCall.request when ADMIN_CONNECTION is disabled"""
    
    @patch.dict(os.environ, {'ADMIN_CONNECTION': 'False'})
    def test_request_returns_404_when_disabled(self):
        """Test request returns 404 when admin connection is disabled"""
        data = AttributeDict({"portfolio": "test_portfolio", "account": "test_account"})
        result = ApiCall.request(data)
        assert result == 404
    
    @patch.dict(os.environ, {'ADMIN_CONNECTION': 'false'})
    def test_request_returns_404_when_disabled_lowercase(self):
        """Test request returns 404 when admin connection is false (lowercase)"""
        data = AttributeDict({"portfolio": "test_portfolio", "account": "test_account"})
        result = ApiCall.request(data)
        assert result == 404


class TestApiCallRequestEmptyRecords:
    """Test ApiCall.request with empty records"""
    
    @patch('privacy.service.api_req.requests.post')
    @patch.dict(os.environ, {'ADMIN_CONNECTION': 'True', 'PRIVADMIN_API': 'http://admin.api'})
    def test_request_returns_none_for_empty_records(self, mock_post):
        """Test request returns None when records list is empty"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "datalist": [
                "entity_type_val",
                "datalist_val",
                "pre_entity_val",
                [],  # Empty records
                ["key1"],
                [50]
            ]
        }
        mock_post.return_value = mock_response
        
        data = AttributeDict({"portfolio": "test_portfolio", "account": "test_account"})
        
        with patch('privacy.service.api_req.request_id_var') as mock_req_id:
            mock_req_id.get.return_value = "test_uuid"
            with patch('privacy.service.api_req.admin_par', {}):
                result = ApiCall.request(data)
                assert result is None


class TestApiCallRequestExceptions:
    """Test ApiCall.request exception handling"""
    
    @patch('privacy.service.api_req.requests.post')
    @patch.dict(os.environ, {'ADMIN_CONNECTION': 'True', 'PRIVADMIN_API': 'http://admin.api'})
    def test_request_handles_json_error(self, mock_post):
        """Test request handles JSON parsing errors"""
        mock_post.side_effect = ValueError("Invalid JSON")
        
        data = AttributeDict({"portfolio": "test_portfolio", "account": "test_account"})
        
        with patch('privacy.service.api_req.request_id_var') as mock_req_id:
            mock_req_id.get.return_value = "test_uuid"
            with patch('privacy.service.api_req.error_dict', {"test_uuid": []}):
                result = ApiCall.request(data)
                assert isinstance(result, Exception)
    
    @patch('privacy.service.api_req.requests.post')
    @patch.dict(os.environ, {'ADMIN_CONNECTION': 'True', 'PRIVADMIN_API': 'http://admin.api'})
    def test_request_handles_connection_error(self, mock_post):
        """Test request handles connection errors"""
        mock_post.side_effect = ConnectionError("Connection refused")
        
        data = AttributeDict({"portfolio": "test_portfolio", "account": "test_account"})
        
        with patch('privacy.service.api_req.request_id_var') as mock_req_id:
            mock_req_id.get.return_value = "test_uuid"
            with patch('privacy.service.api_req.error_dict', {"test_uuid": []}):
                result = ApiCall.request(data)
                assert isinstance(result, Exception)
    
    @patch('privacy.service.api_req.requests.post')
    @patch.dict(os.environ, {'ADMIN_CONNECTION': 'True', 'PRIVADMIN_API': 'http://admin.api'})
    def test_request_handles_keyerror(self, mock_post):
        """Test request handles KeyError when datalist key missing"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"wrong_key": []}
        mock_post.return_value = mock_response
        
        data = AttributeDict({"portfolio": "test_portfolio", "account": "test_account"})
        
        with patch('privacy.service.api_req.request_id_var') as mock_req_id:
            mock_req_id.get.return_value = "test_uuid"
            with patch('privacy.service.api_req.error_dict', {"test_uuid": []}):
                result = ApiCall.request(data)
                assert isinstance(result, Exception)


class TestApiCallGetRecord:
    """Test ApiCall.get_record method"""
    
    def test_get_record_finds_matching_record(self):
        """Test get_record returns matching record by RecogName"""
        test_uuid = "test_uuid"
        mock_admin_par = {
            test_uuid: {
                "records": [
                    {"RecogName": "person", "data": "John"},
                    {"RecogName": "email", "data": "test@example.com"},
                    {"RecogName": "phone", "data": "123-456-7890"}
                ]
            }
        }
        
        with patch('privacy.service.api_req.request_id_var') as mock_req_id:
            mock_req_id.get.return_value = test_uuid
            with patch('privacy.service.api_req.admin_par', mock_admin_par):
                record = ApiCall.get_record("email")
                assert record == {"RecogName": "email", "data": "test@example.com"}
    
    def test_get_record_first_match(self):
        """Test get_record returns first matching record"""
        test_uuid = "test_uuid"
        mock_admin_par = {
            test_uuid: {
                "records": [
                    {"RecogName": "person", "data": "John"},
                    {"RecogName": "person", "data": "Jane"}
                ]
            }
        }
        
        with patch('privacy.service.api_req.request_id_var') as mock_req_id:
            mock_req_id.get.return_value = test_uuid
            with patch('privacy.service.api_req.admin_par', mock_admin_par):
                record = ApiCall.get_record("person")
                assert record["data"] == "John"


class TestApiCallDelAdminList:
    """Test ApiCall.del_admin_list method"""
    
    def test_del_admin_list_removes_entry(self):
        """Test del_admin_list removes admin_par entry by UUID"""
        test_uuid = "test_uuid_12345"
        mock_admin_par = {
            test_uuid: {"records": []},
            "other_uuid": {"records": []}
        }
        
        with patch('privacy.service.api_req.request_id_var') as mock_req_id:
            mock_req_id.get.return_value = test_uuid
            with patch('privacy.service.api_req.admin_par', mock_admin_par):
                ApiCall.del_admin_list()
                assert test_uuid not in mock_admin_par
                assert "other_uuid" in mock_admin_par
    
    def test_del_admin_list_with_missing_uuid(self):
        """Test del_admin_list handles missing UUID gracefully"""
        test_uuid = "nonexistent_uuid"
        mock_admin_par = {"other_uuid": {"records": []}}
        
        with patch('privacy.service.api_req.request_id_var') as mock_req_id:
            mock_req_id.get.return_value = test_uuid
            with patch('privacy.service.api_req.admin_par', mock_admin_par):
                # Should not raise error
                ApiCall.del_admin_list()
                assert "other_uuid" in mock_admin_par


class TestApiCallPayloadConstruction:
    """Test API call payload construction"""
    
    @patch('privacy.service.api_req.requests.post')
    @patch.dict(os.environ, {'ADMIN_CONNECTION': 'True', 'PRIVADMIN_API': 'http://admin.api'})
    def test_request_sends_correct_payload(self, mock_post):
        """Test request sends payload with portfolio and account"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"datalist": ["type", "list", "pre", [], [], [50]]}
        mock_post.return_value = mock_response
        
        data = AttributeDict({"portfolio": "my_portfolio", "account": "my_account"})
        
        with patch('privacy.service.api_req.request_id_var') as mock_req_id:
            mock_req_id.get.return_value = "uuid"
            with patch('privacy.service.api_req.admin_par', {}):
                with patch('privacy.service.api_req.error_dict', {"uuid": []}):
                    ApiCall.request(data)
                    
                    # Verify POST was called with correct payload
                    call_args = mock_post.call_args
                    assert call_args is not None
                    payload = call_args.kwargs['json']
                    assert payload['portfolio'] == "my_portfolio"
                    assert payload['account'] == "my_account"


class TestApiCallAdminParStorage:
    """Test admin_par data storage and retrieval"""
    
    @patch('privacy.service.api_req.requests.post')
    @patch.dict(os.environ, {'ADMIN_CONNECTION': 'True', 'PRIVADMIN_API': 'http://admin.api'})
    def test_request_stores_encryption_list_and_records(self, mock_post):
        """Test request stores encryption_list, records, and score_threshold in admin_par"""
        mock_response = MagicMock()
        encryption_list = ["enc_key_1", "enc_key_2"]
        records = [{"RecogName": "person", "id": 1}]
        threshold = [85]
        
        mock_response.json.return_value = {
            "datalist": [
                "entity_type",
                "datalist_val",
                "pre_entity",
                records,
                encryption_list,
                threshold
            ]
        }
        mock_post.return_value = mock_response
        
        data = AttributeDict({"portfolio": "test", "account": "test"})
        
        with patch('privacy.service.api_req.request_id_var') as mock_req_id:
            mock_req_id.get.return_value = "test_id"
            mock_admin_par = {}
            with patch('privacy.service.api_req.admin_par', mock_admin_par):
                ApiCall.request(data)
                
                # Verify admin_par contains correct data
                assert "test_id" in mock_admin_par
                assert mock_admin_par["test_id"]["encryption_list"] == encryption_list
                assert mock_admin_par["test_id"]["records"] == records
                assert mock_admin_par["test_id"]["score_treshold"] == 85
