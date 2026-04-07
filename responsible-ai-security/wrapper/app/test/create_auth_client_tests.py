# Test for auth_client_id
test_auth_client = '''import pytest
import os
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from src.util.auth.auth_client_id import AzureAuthClient, get_azure_token

class TestAzureAuthClient:
    @patch('src.util.auth.auth_client_id.msal.ConfidentialClientApplication')
    def test_azure_auth_client_initialization(self, mock_msal):
        mock_app = MagicMock()
        mock_msal.return_value = mock_app
        
        client = AzureAuthClient('tenant123', 'client123', 'secret123', ['scope1'])
        assert client.tenant_id == 'tenant123'
        assert client.client_id == 'client123'
        assert client.client_secret == 'secret123'
        assert client.scope == ['scope1']
    
    @patch('src.util.auth.auth_client_id.msal.ConfidentialClientApplication')
    def test_get_token_success(self, mock_msal):
        mock_app = MagicMock()
        mock_app.acquire_token_for_client.return_value = {
            'access_token': 'test_token_123',
            'expires_in': 3600
        }
        mock_msal.return_value = mock_app
        
        client = AzureAuthClient('tenant123', 'client123', 'secret123', ['scope1'])
        token = client.get_token()
        assert token == 'test_token_123'
    
    @patch('src.util.auth.auth_client_id.msal.ConfidentialClientApplication')
    def test_get_token_failure(self, mock_msal):
        mock_app = MagicMock()
        mock_app.acquire_token_for_client.return_value = {}
        mock_msal.return_value = mock_app
        
        client = AzureAuthClient('tenant123', 'client123', 'secret123', ['scope1'])
        with pytest.raises(HTTPException) as exc_info:
            client.get_token()
        assert exc_info.value.status_code == 401
    
    @patch('src.util.auth.auth_client_id.msal.ConfidentialClientApplication')
    def test_get_token_caching(self, mock_msal):
        mock_app = MagicMock()
        mock_app.acquire_token_for_client.return_value = {
            'access_token': 'cached_token',
            'expires_in': 9999
        }
        mock_msal.return_value = mock_app
        
        client = AzureAuthClient('tenant123', 'client123', 'secret123', ['scope1'])
        token1 = client.get_token()
        token2 = client.get_token()
        assert token1 == token2
        assert mock_app.acquire_token_for_client.call_count == 1
'''

with open('test_auth_client_id.py', 'w', encoding='utf-8') as f:
    f.write(test_auth_client)

print('Created test_auth_client_id.py')
