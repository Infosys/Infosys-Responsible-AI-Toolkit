"""
Test suite for authentication utilities - auth_client_id and auth_jwt modules.
Comprehensive testing to improve coverage.
"""

import pytest
import os
import json
from unittest.mock import patch, MagicMock, Mock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt, ExpiredSignatureError, JWTError


class TestAuthNone:
    """Test the authentication none module (no auth mode)."""
    
    def test_authenticate_none_returns_true(self):
        """Test that authenticate_none always returns True."""
        from privacy.util.auth.auth_none import authenticate_none
        assert authenticate_none() is True
    
    def test_authenticate_none_multiple_calls(self):
        """Test authenticate_none consistency across multiple calls."""
        from privacy.util.auth.auth_none import authenticate_none
        results = [authenticate_none() for _ in range(5)]
        assert all(result is True for result in results)
    
    def test_get_auth_none_returns_function(self):
        """Test that get_auth_none returns the authenticate function."""
        from privacy.util.auth.auth_none import get_auth_none, authenticate_none
        auth_func = get_auth_none()
        assert callable(auth_func)
        assert auth_func is authenticate_none
    
    def test_get_auth_none_function_callable(self):
        """Test that the returned function can be called."""
        from privacy.util.auth.auth_none import get_auth_none
        auth_func = get_auth_none()
        result = auth_func()
        assert result is True


class TestAuthJWT:
    """Test the JWT authentication module."""
    
    def test_authenticate_jwt_success(self):
        """Test successful JWT authentication."""
        from privacy.util.auth.auth_jwt import authenticate_jwt
        
        with patch('privacy.util.auth.auth_jwt.jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "user_id": "12345",
                "username": "testuser",
                "exp": 1735000000
            }
            
            credentials = MagicMock(spec=HTTPAuthorizationCredentials)
            credentials.credentials = "valid.jwt.token"
            
            result = authenticate_jwt(credentials)
            
            assert result["user_id"] == "12345"
            assert result["username"] == "testuser"
            mock_decode.assert_called_once()
    
    def test_authenticate_jwt_expired_token(self):
        """Test JWT authentication with expired token."""
        from privacy.util.auth.auth_jwt import authenticate_jwt
        
        with patch('privacy.util.auth.auth_jwt.jwt.decode') as mock_decode:
            mock_decode.side_effect = ExpiredSignatureError("Token has expired")
            
            credentials = MagicMock(spec=HTTPAuthorizationCredentials)
            credentials.credentials = "expired.jwt.token"
            
            with pytest.raises(HTTPException) as exc_info:
                authenticate_jwt(credentials)
            
            assert exc_info.value.status_code == 401
            assert "expired" in exc_info.value.detail.lower() or "Token" in exc_info.value.detail
    
    def test_authenticate_jwt_invalid_signature(self):
        """Test JWT authentication with invalid signature."""
        from privacy.util.auth.auth_jwt import authenticate_jwt
        
        with patch('privacy.util.auth.auth_jwt.jwt.decode') as mock_decode:
            mock_decode.side_effect = JWTError("Invalid signature")
            
            credentials = MagicMock(spec=HTTPAuthorizationCredentials)
            credentials.credentials = "invalid.jwt.token"
            
            with pytest.raises(HTTPException) as exc_info:
                authenticate_jwt(credentials)
            
            assert exc_info.value.status_code == 401
    
    def test_get_auth_jwt_returns_function(self):
        """Test that get_auth_jwt returns the authenticate function."""
        from privacy.util.auth.auth_jwt import get_auth_jwt, authenticate_jwt
        auth_func = get_auth_jwt()
        assert callable(auth_func)
        assert auth_func is authenticate_jwt
    
    def test_authenticate_jwt_none_credentials(self):
        """Test JWT authentication with None credentials."""
        from privacy.util.auth.auth_jwt import authenticate_jwt
        
        with pytest.raises((HTTPException, TypeError, AttributeError)):
            authenticate_jwt(None)
    
    def test_authenticate_jwt_empty_token(self):
        """Test JWT authentication with empty token."""
        from privacy.util.auth.auth_jwt import authenticate_jwt
        
        with patch('privacy.util.auth.auth_jwt.jwt.decode') as mock_decode:
            mock_decode.side_effect = JWTError("Invalid token")
            
            credentials = MagicMock(spec=HTTPAuthorizationCredentials)
            credentials.credentials = ""
            
            with pytest.raises(HTTPException):
                authenticate_jwt(credentials)


class TestAuthClientId:
    """Test the Client ID authentication module (Azure AD JWT)."""
    
    def test_authenticate_client_id_valid_jwt(self):
        """Test successful Client ID authentication with valid JWT."""
        from privacy.util.auth.auth_client_id import authenticate_client_id
        
        with patch('privacy.util.auth.auth_client_id.get_public_keys') as mock_get_keys, \
             patch('privacy.util.auth.auth_client_id.jwt.decode') as mock_decode:
            
            # Setup expected decoded token
            expected_token = {
                "aud": "client-id-123",
                "iss": "https://sts.windows.net/tenant-id/",
                "tid": "tenant-id"
            }
            
            mock_decode.return_value = expected_token
            mock_get_keys.return_value = {
                "kid1": {"kty": "RSA", "use": "sig"}
            }

            credentials = MagicMock(spec=HTTPAuthorizationCredentials)
            credentials.credentials = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJjbGllbnQtaWQiLCJpc3MiOiJodHRwczovL2xvZ2luLm1pY3Jvc29mdG9ubGluZS5jb20vdGVuYW50LWlkL3YyLjAiLCJ0aWQiOiJ0ZW5hbnQtaWQifQ.signature"

            result = authenticate_client_id(credentials)

            # Should return the decoded token
            assert result is not None
            assert result["aud"] == "client-id-123"
            assert result["tid"] == "tenant-id"
            
            mock_get_keys.return_value = {"kid1": {"kty": "RSA"}}
            mock_decode.side_effect = ExpiredSignatureError("Token expired")
            
            credentials = MagicMock(spec=HTTPAuthorizationCredentials)
            credentials.credentials = "expired.jwt.token"
            
            with pytest.raises(HTTPException) as exc_info:
                authenticate_client_id(credentials)
            
            assert exc_info.value.status_code == 401
    
    def test_authenticate_client_id_invalid_jwt(self):
        """Test Client ID authentication with invalid JWT."""
        from privacy.util.auth.auth_client_id import authenticate_client_id
        
        with patch('privacy.util.auth.auth_client_id.get_public_keys') as mock_get_keys, \
             patch('privacy.util.auth.auth_client_id.jwt.decode') as mock_decode:
            
            mock_get_keys.return_value = {"kid1": {"kty": "RSA"}}
            mock_decode.side_effect = JWTError("Invalid signature")
            
            credentials = MagicMock(spec=HTTPAuthorizationCredentials)
            credentials.credentials = "invalid.jwt.token"
            
            with pytest.raises(HTTPException) as exc_info:
                authenticate_client_id(credentials)
            
            assert exc_info.value.status_code == 401
    
    def test_authenticate_client_id_decode_fails_all_keys(self):
        """Test Client ID authentication when all keys fail to decode."""
        from privacy.util.auth.auth_client_id import authenticate_client_id
        
        with patch('privacy.util.auth.auth_client_id.get_public_keys') as mock_get_keys, \
             patch('privacy.util.auth.auth_client_id.jwt.decode') as mock_decode:
            
            mock_get_keys.return_value = {"kid1": {"kty": "RSA"}, "kid2": {"kty": "RSA"}}
            mock_decode.side_effect = JWTError("All keys failed")
            
            credentials = MagicMock(spec=HTTPAuthorizationCredentials)
            credentials.credentials = "bad.jwt.token"
            
            with pytest.raises(HTTPException) as exc_info:
                authenticate_client_id(credentials)
            
            assert exc_info.value.status_code == 401
    
    def test_get_auth_client_id_returns_function(self):
        """Test that get_auth_client_id returns the authenticate function."""
        from privacy.util.auth.auth_client_id import get_auth_client_id, authenticate_client_id
        auth_func = get_auth_client_id()
        assert callable(auth_func)
        assert auth_func is authenticate_client_id
    
    def test_authenticate_client_id_none_credentials(self):
        """Test Client ID authentication with None credentials."""
        from privacy.util.auth.auth_client_id import authenticate_client_id
        
        with pytest.raises((HTTPException, TypeError, AttributeError)):
            authenticate_client_id(None)
    
    def test_get_public_keys_success(self):
        """Test successful get_public_keys call."""
        from privacy.util.auth.auth_client_id import get_public_keys
        
        with patch('privacy.util.auth.auth_client_id.requests.get') as mock_get, \
             patch.dict(os.environ, {"AZURE_AD_JWKS_URL": "https://example.com/jwks"}):
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "keys": [
                    {"kid": "key1", "kty": "RSA"},
                    {"kid": "key2", "kty": "RSA"}
                ]
            }
            mock_get.return_value = mock_response
            
            keys = get_public_keys()
            
            assert isinstance(keys, dict)
            assert "key1" in keys
            assert "key2" in keys
    
    def test_get_public_keys_http_error(self):
        """Test get_public_keys when HTTP request fails."""
        from privacy.util.auth.auth_client_id import get_public_keys
        
        with patch('privacy.util.auth.auth_client_id.requests.get') as mock_get, \
             patch.dict(os.environ, {"AZURE_AD_JWKS_URL": "https://example.com/jwks"}):
            
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response
            
            with pytest.raises(HTTPException) as exc_info:
                get_public_keys()
            
            assert exc_info.value.status_code == 500
    
    def test_get_public_keys_invalid_format(self):
        """Test get_public_keys when response format is invalid."""
        from privacy.util.auth.auth_client_id import get_public_keys
        
        with patch('privacy.util.auth.auth_client_id.requests.get') as mock_get, \
             patch.dict(os.environ, {"AZURE_AD_JWKS_URL": "https://example.com/jwks"}):
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"invalid": "format"}
            mock_get.return_value = mock_response
            
            with pytest.raises(HTTPException) as exc_info:
                get_public_keys()
            
            assert exc_info.value.status_code == 500


class TestAuthIntegration:
    """Integration tests for auth modules."""
    
    def test_all_auth_modules_importable(self):
        """Test that all auth modules can be imported."""
        from privacy.util.auth.auth_none import get_auth_none, authenticate_none
        from privacy.util.auth.auth_jwt import get_auth_jwt, authenticate_jwt
        from privacy.util.auth.auth_client_id import get_auth_client_id, authenticate_client_id
        
        assert callable(get_auth_none)
        assert callable(get_auth_jwt)
        assert callable(get_auth_client_id)
    
    def test_auth_none_vs_others(self):
        """Test that auth_none always succeeds."""
        from privacy.util.auth.auth_none import authenticate_none
        
        # None auth should always work
        result = authenticate_none()
        assert result is True
    
    def test_get_auth_functions_return_different_functions(self):
        """Test that different get_auth functions return different functions."""
        from privacy.util.auth.auth_none import get_auth_none
        from privacy.util.auth.auth_jwt import get_auth_jwt
        from privacy.util.auth.auth_client_id import get_auth_client_id
        
        none_auth = get_auth_none()
        jwt_auth = get_auth_jwt()
        client_auth = get_auth_client_id()
        
        # Should return different functions
        assert none_auth is not jwt_auth
        assert jwt_auth is not client_auth
        assert none_auth is not client_auth
