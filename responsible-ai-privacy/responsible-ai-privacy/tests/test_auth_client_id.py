"""
Tests for auth_client_id authentication module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt, ExpiredSignatureError, JWTError

from privacy.util.auth.auth_client_id import (
    get_public_keys,
    authenticate_client_id,
    get_auth_client_id
)


@pytest.fixture
def mock_jwks_response():
    """Mock JWKS response from Azure AD."""
    return {
        "keys": [
            {
                "kid": "test_kid_123",
                "kty": "RSA",
                "use": "sig",
                "n": "test_n_value",
                "e": "AQAB"
            },
            {
                "kid": "test_kid_456",
                "kty": "RSA",
                "use": "sig",
                "n": "test_n_value_2",
                "e": "AQAB"
            }
        ]
    }


@pytest.fixture
def mock_decoded_token():
    """Mock decoded JWT token."""
    return {
        "iss": "https://sts.windows.net/tenant-id/",
        "aud": "test-client-id",
        "tid": "test-tenant-id",
        "sub": "test-subject",
        "exp": 1234567890
    }


@pytest.fixture
def mock_credentials():
    """Mock HTTPAuthorizationCredentials."""
    credentials = Mock(spec=HTTPAuthorizationCredentials)
    credentials.credentials = "test_token_12345"
    return credentials


class TestGetPublicKeys:
    """Test get_public_keys function."""
    
    @patch('privacy.util.auth.auth_client_id.requests.get')
    @patch('privacy.util.auth.auth_client_id.os.getenv')
    def test_get_public_keys_success(self, mock_getenv, mock_requests_get, mock_jwks_response):
        """Test successful retrieval of public keys."""
        mock_getenv.return_value = "https://login.microsoftonline.com/tenant/discovery/v2.0/keys"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_jwks_response
        mock_requests_get.return_value = mock_response
        
        result = get_public_keys()
        
        assert "test_kid_123" in result
        assert "test_kid_456" in result
        assert result["test_kid_123"]["kty"] == "RSA"
        mock_requests_get.assert_called_once()
    
    @patch('privacy.util.auth.auth_client_id.requests.get')
    @patch('privacy.util.auth.auth_client_id.os.getenv')
    def test_get_public_keys_http_error(self, mock_getenv, mock_requests_get):
        """Test get_public_keys with HTTP error."""
        mock_getenv.return_value = "https://login.microsoftonline.com/tenant/discovery/v2.0/keys"
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_requests_get.return_value = mock_response
        
        with pytest.raises(HTTPException) as exc_info:
            get_public_keys()
        
        assert exc_info.value.status_code == 500
        assert "Failed to fetch JWKS" in str(exc_info.value.detail)
    
    @patch('privacy.util.auth.auth_client_id.requests.get')
    @patch('privacy.util.auth.auth_client_id.os.getenv')
    def test_get_public_keys_invalid_response(self, mock_getenv, mock_requests_get):
        """Test get_public_keys with invalid JWKS response."""
        mock_getenv.return_value = "https://login.microsoftonline.com/tenant/discovery/v2.0/keys"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "format"}
        mock_requests_get.return_value = mock_response
        
        with pytest.raises(HTTPException) as exc_info:
            get_public_keys()
        
        assert exc_info.value.status_code == 500
        assert "JWKS response format is invalid" in str(exc_info.value.detail)


class TestAuthenticateClientId:
    """Test authenticate_client_id function."""
    
    @patch('privacy.util.auth.auth_client_id.get_public_keys')
    @patch('privacy.util.auth.auth_client_id.jwt.decode')
    @patch('privacy.util.auth.auth_client_id.jwt.get_unverified_header')
    def test_authenticate_client_id_success(
        self,
        mock_get_header,
        mock_jwt_decode,
        mock_get_keys,
        mock_credentials,
        mock_decoded_token,
        mock_jwks_response
    ):
        """Test successful authentication."""
        mock_get_header.return_value = {"kid": "test_kid_123"}
        mock_get_keys.return_value = {
            "test_kid_123": mock_jwks_response["keys"][0]
        }
        mock_jwt_decode.return_value = mock_decoded_token
        
        # Should not raise an exception
        authenticate_client_id(mock_credentials)
        
        mock_get_header.assert_called_once_with("test_token_12345")
        mock_get_keys.assert_called_once()
        mock_jwt_decode.assert_called_once()
    
    @patch('privacy.util.auth.auth_client_id.get_public_keys')
    @patch('privacy.util.auth.auth_client_id.jwt.get_unverified_header')
    def test_authenticate_client_id_expired_token(
        self,
        mock_get_header,
        mock_get_keys,
        mock_credentials,
        mock_jwks_response
    ):
        """Test authentication with expired token."""
        mock_get_header.return_value = {"kid": "test_kid_123"}
        mock_get_keys.return_value = {
            "test_kid_123": mock_jwks_response["keys"][0]
        }
        
        with patch('privacy.util.auth.auth_client_id.jwt.decode') as mock_decode:
            mock_decode.side_effect = ExpiredSignatureError("Token expired")
            
            with pytest.raises(HTTPException) as exc_info:
                authenticate_client_id(mock_credentials)
            
            assert exc_info.value.status_code == 401
            assert "Token has expired" in str(exc_info.value.detail)
    
    @patch('privacy.util.auth.auth_client_id.get_public_keys')
    @patch('privacy.util.auth.auth_client_id.jwt.get_unverified_header')
    def test_authenticate_client_id_invalid_token(
        self,
        mock_get_header,
        mock_get_keys,
        mock_credentials,
        mock_jwks_response
    ):
        """Test authentication with invalid token."""
        mock_get_header.return_value = {"kid": "test_kid_123"}
        mock_get_keys.return_value = {
            "test_kid_123": mock_jwks_response["keys"][0]
        }
        
        with patch('privacy.util.auth.auth_client_id.jwt.decode') as mock_decode:
            mock_decode.side_effect = JWTError("Invalid signature")
            
            with pytest.raises(HTTPException) as exc_info:
                authenticate_client_id(mock_credentials)
            
            assert exc_info.value.status_code == 401
            assert "Invalid token" in str(exc_info.value.detail)
    
    @patch('privacy.util.auth.auth_client_id.get_public_keys')
    @patch('privacy.util.auth.auth_client_id.jwt.get_unverified_header')
    def test_authenticate_client_id_unexpected_error(
        self,
        mock_get_header,
        mock_get_keys,
        mock_credentials,
        mock_jwks_response
    ):
        """Test authentication with unexpected error."""
        mock_get_header.return_value = {"kid": "test_kid_123"}
        mock_get_keys.return_value = {
            "test_kid_123": mock_jwks_response["keys"][0]
        }
        
        with patch('privacy.util.auth.auth_client_id.jwt.decode') as mock_decode:
            mock_decode.side_effect = Exception("Unexpected error occurred")
            
            with pytest.raises(HTTPException) as exc_info:
                authenticate_client_id(mock_credentials)
            
            assert exc_info.value.status_code == 500
            assert "Unexpected error" in str(exc_info.value.detail)


class TestGetAuthClientId:
    """Test get_auth_client_id function."""
    
    def test_get_auth_client_id_returns_function(self):
        """Test that get_auth_client_id returns the authenticate function."""
        result = get_auth_client_id()
        
        assert result == authenticate_client_id
        assert callable(result)


class TestAuthClientIdIntegration:
    """Integration tests for auth_client_id module."""
    
    @patch('privacy.util.auth.auth_client_id.os.getenv')
    @patch('privacy.util.auth.auth_client_id.requests.get')
    @patch('privacy.util.auth.auth_client_id.jwt.get_unverified_header')
    @patch('privacy.util.auth.auth_client_id.jwt.decode')
    def test_full_authentication_flow(
        self,
        mock_jwt_decode,
        mock_get_header,
        mock_requests_get,
        mock_getenv,
        mock_credentials,
        mock_jwks_response,
        mock_decoded_token
    ):
        """Test full authentication flow from token to validation."""
        # Setup environment
        def getenv_side_effect(key):
            env_vars = {
                'AZURE_AD_JWKS_URL': 'https://login.microsoftonline.com/tenant/discovery/v2.0/keys',
                'AZURE_CLIENT_ID': 'test-client-id',
                'AZURE_TENANT_ID': 'test-tenant-id'
            }
            return env_vars.get(key)
        
        mock_getenv.side_effect = getenv_side_effect
        
        # Setup JWKS response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_jwks_response
        mock_requests_get.return_value = mock_response
        
        # Setup JWT processing
        mock_get_header.return_value = {"kid": "test_kid_123"}
        mock_jwt_decode.return_value = mock_decoded_token
        
        # Execute
        authenticate_client_id(mock_credentials)
        
        # Verify
        mock_requests_get.assert_called_once()
        mock_get_header.assert_called_once_with("test_token_12345")
        mock_jwt_decode.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
