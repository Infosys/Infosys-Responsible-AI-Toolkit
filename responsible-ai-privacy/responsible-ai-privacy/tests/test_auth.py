"""
Tests for authentication modules
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose.exceptions import ExpiredSignatureError, JWTError
from privacy.util.auth.auth_none import authenticate_none, get_auth_none
from privacy.util.auth.auth_jwt import authenticate_jwt, get_auth_jwt


class TestAuthNone:
    """Test suite for auth_none module"""

    def test_authenticate_none_returns_true(self):
        """Test that authenticate_none always returns True"""
        result = authenticate_none()
        assert result is True

    def test_get_auth_none_returns_function(self):
        """Test that get_auth_none returns the authenticate_none function"""
        result = get_auth_none()
        assert callable(result)
        assert result == authenticate_none

    def test_get_auth_none_can_be_called(self):
        """Test that the function returned by get_auth_none can be called"""
        auth_func = get_auth_none()
        result = auth_func()
        assert result is True


class TestAuthJWT:
    """Test suite for auth_jwt module"""

    @patch('privacy.util.auth.auth_jwt.jwt.decode')
    @patch('privacy.util.auth.auth_jwt.secret_key', 'test_secret_key')
    def test_authenticate_jwt_with_valid_token(self, mock_decode):
        """Test authenticate_jwt with a valid token"""
        mock_decode.return_value = {'user_id': '123', 'username': 'testuser'}
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = 'valid_token'
        
        result = authenticate_jwt(credentials)
        
        assert result == {'user_id': '123', 'username': 'testuser'}
        mock_decode.assert_called_once_with(
            'valid_token', 
            'test_secret_key', 
            algorithms=["HS256"],
            options={"verify_signature": False, "verify_aud": False}
        )

    @patch('privacy.util.auth.auth_jwt.jwt.decode')
    @patch('privacy.util.auth.auth_jwt.secret_key', 'test_secret_key')
    def test_authenticate_jwt_with_expired_token(self, mock_decode):
        """Test authenticate_jwt with an expired token"""
        mock_decode.side_effect = ExpiredSignatureError('Token expired')
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = 'expired_token'
        
        with pytest.raises(HTTPException) as exc_info:
            authenticate_jwt(credentials)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Token expired"

    @patch('privacy.util.auth.auth_jwt.jwt.decode')
    @patch('privacy.util.auth.auth_jwt.secret_key', 'test_secret_key')
    def test_authenticate_jwt_with_invalid_token(self, mock_decode):
        """Test authenticate_jwt with an invalid token"""
        mock_decode.side_effect = JWTError('Invalid token')
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = 'invalid_token'
        
        with pytest.raises(HTTPException) as exc_info:
            authenticate_jwt(credentials)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token"

    @patch('privacy.util.auth.auth_jwt.jwt.decode')
    @patch('privacy.util.auth.auth_jwt.secret_key', 'test_secret_key')
    @patch('privacy.util.auth.auth_jwt.log')
    def test_authenticate_jwt_with_unexpected_error(self, mock_log, mock_decode):
        """Test authenticate_jwt with an unexpected error"""
        mock_decode.side_effect = ValueError('Unexpected error')
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = 'token_causing_error'
        
        with pytest.raises(HTTPException) as exc_info:
            authenticate_jwt(credentials)
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Unexpected error"
        assert mock_log.error.called

    def test_get_auth_jwt_returns_function(self):
        """Test that get_auth_jwt returns the authenticate_jwt function"""
        result = get_auth_jwt()
        assert callable(result)
        assert result == authenticate_jwt
