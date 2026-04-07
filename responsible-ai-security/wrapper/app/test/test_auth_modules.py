import pytest
import os
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from src.util.auth.auth_none import authenticate_none, get_auth_none
from src.util.auth.auth_jwt import authenticate_jwt, get_auth_jwt

class TestAuthNone:
    def test_authenticate_none_returns_true(self):
        result = authenticate_none()
        assert result is True
    
    def test_get_auth_none_returns_function(self):
        auth_func = get_auth_none()
        assert callable(auth_func)
    
    def test_get_auth_none_returns_authenticate_none(self):
        auth_func = get_auth_none()
        assert auth_func() is True

class TestAuthJWT:
    @patch('src.util.auth.auth_jwt.jwt.decode')
    def test_authenticate_jwt_success(self, mock_decode):
        mock_decode.return_value = {'sub': 'test_user', 'exp': 9999999999}
        credentials = MagicMock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = 'valid.token.here'
        
        with patch.dict(os.environ, {'SECRET_KEY': 'test_secret'}):
            result = authenticate_jwt(credentials)
            assert result is not None
    
    @patch('src.util.auth.auth_jwt.jwt.decode')
    def test_authenticate_jwt_expired(self, mock_decode):
        from jose.exceptions import ExpiredSignatureError
        mock_decode.side_effect = ExpiredSignatureError('Token expired')
        credentials = MagicMock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = 'expired.token.here'
        
        with patch.dict(os.environ, {'SECRET_KEY': 'test_secret'}):
            with pytest.raises(HTTPException) as exc_info:
                authenticate_jwt(credentials)
            assert exc_info.value.status_code == 401
            assert 'expired' in str(exc_info.value.detail).lower()
    
    @patch('src.util.auth.auth_jwt.jwt.decode')
    def test_authenticate_jwt_invalid(self, mock_decode):
        from jose.exceptions import JWTError
        mock_decode.side_effect = JWTError('Invalid token')
        credentials = MagicMock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = 'invalid.token.here'
        
        with patch.dict(os.environ, {'SECRET_KEY': 'test_secret'}):
            with pytest.raises(HTTPException) as exc_info:
                authenticate_jwt(credentials)
            assert exc_info.value.status_code == 401
    
    def test_get_auth_jwt_returns_function(self):
        auth_func = get_auth_jwt()
        assert callable(auth_func)
