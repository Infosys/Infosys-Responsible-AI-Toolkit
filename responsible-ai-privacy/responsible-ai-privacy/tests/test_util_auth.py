# """
# Test suite for authentication utilities.
# Tests simple authentication helper functions.
# """

# import pytest
# import os
# from unittest.mock import patch, MagicMock, Mock
# from fastapi import HTTPException
# from fastapi.security import HTTPAuthorizationCredentials
# from jose import jwt, ExpiredSignatureError, JWTError
# from src.privacy.util.auth.auth_none import authenticate_none, get_auth_none
# from src.privacy.util.auth.auth_jwt import authenticate_jwt, get_auth_jwt
# from src.privacy.util.auth.auth_client_id import authenticate_client_id, get_auth_client_id, get_public_keys


# class TestAuthNone:
#     """Test the authentication none module (no auth mode)."""
    
#     def test_authenticate_none_returns_true(self):
#         """Test that authenticate_none always returns True."""
#         assert authenticate_none() is True
    
#     def test_authenticate_none_multiple_calls(self):
#         """Test authenticate_none consistency across multiple calls."""
#         results = [authenticate_none() for _ in range(10)]
#         assert all(result is True for result in results)
    
#     def test_get_auth_none_returns_function(self):
#         """Test that get_auth_none returns the authenticate function."""
#         auth_func = get_auth_none()
#         assert callable(auth_func)
#         assert auth_func is authenticate_none
    
#     def test_get_auth_none_function_callable(self):
#         """Test that the returned function can be called."""
#         auth_func = get_auth_none()
#         result = auth_func()
#         assert result is True
    
#     def test_get_auth_none_returns_same_function(self):
#         """Test that get_auth_none consistently returns the same function."""
#         auth_func1 = get_auth_none()
#         auth_func2 = get_auth_none()
#         assert auth_func1 is auth_func2


# class TestAuthJWT:
#     """Test the JWT authentication module."""
    
#     @patch('src.privacy.util.auth.auth_jwt.secret_key', 'test_secret_key_12345')
#     @patch('src.privacy.util.auth.auth_jwt.jwt.decode')
#     def test_authenticate_jwt_success(self, mock_decode):
#         """Test successful JWT authentication."""
#         # Mock a valid token payload
#         mock_decode.return_value = {
#             "user_id": "12345",
#             "username": "testuser",
#             "exp": 1735000000
#         }
        
#         # Create mock credentials
#         credentials = MagicMock(spec=HTTPAuthorizationCredentials)
#         credentials.credentials = "valid.jwt.token"
        
#         result = authenticate_jwt(credentials)
        
#         # Verify jwt.decode was called with correct parameters
#         mock_decode.assert_called_once_with(
#             "valid.jwt.token",
#             "test_secret_key_12345",
#             algorithms=["HS256"],
#             options={"verify_signature": True, "verify_aud": False}
#         )
        
#         # Verify result contains expected payload
#         assert result["user_id"] == "12345"
#         assert result["username"] == "testuser"
    
#     @patch.dict(os.environ, {"SECRET_KEY": "test_secret_key_12345"})
#     @patch('src.privacy.util.auth.auth_jwt.jwt.decode')
#     def test_authenticate_jwt_expired_token(self, mock_decode):
#         """Test JWT authentication with expired token."""
#         # Mock ExpiredSignatureError
#         mock_decode.side_effect = ExpiredSignatureError("Token has expired")
        
#         credentials = MagicMock(spec=HTTPAuthorizationCredentials)
#         credentials.credentials = "expired.jwt.token"
        
#         with pytest.raises(HTTPException) as exc_info:
#             authenticate_jwt(credentials)
        
#         # Verify correct exception details
#         assert exc_info.value.status_code == 401
#         assert exc_info.value.detail == "Token expired"
#         assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
    
#     @patch.dict(os.environ, {"SECRET_KEY": "test_secret_key_12345"})
#     @patch('src.privacy.util.auth.auth_jwt.jwt.decode')
#     def test_authenticate_jwt_invalid_token(self, mock_decode):
#         """Test JWT authentication with invalid token."""
#         # Mock JWTError
#         mock_decode.side_effect = JWTError("Invalid token format")
        
#         credentials = MagicMock(spec=HTTPAuthorizationCredentials)
#         credentials.credentials = "invalid.jwt.token"
        
#         with pytest.raises(HTTPException) as exc_info:
#             authenticate_jwt(credentials)
        
#         # Verify correct exception details
#         assert exc_info.value.status_code == 401
#         assert exc_info.value.detail == "Invalid token"
#         assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
    
#     @patch.dict(os.environ, {"SECRET_KEY": "test_secret_key_12345"})
#     @patch('src.privacy.util.auth.auth_jwt.jwt.decode')
#     @patch('src.privacy.util.auth.auth_jwt.log')
#     def test_authenticate_jwt_unexpected_error(self, mock_log, mock_decode):
#         """Test JWT authentication with unexpected exception."""
#         # Mock an unexpected exception
#         unexpected_error = ValueError("Unexpected error occurred")
#         mock_decode.side_effect = unexpected_error
        
#         credentials = MagicMock(spec=HTTPAuthorizationCredentials)
#         credentials.credentials = "problematic.jwt.token"
        
#         with pytest.raises(HTTPException) as exc_info:
#             authenticate_jwt(credentials)
        
#         # Verify correct exception details
#         assert exc_info.value.status_code == 500
#         assert exc_info.value.detail == "Unexpected error"
        
#         # Verify logging was called
#         assert mock_log.error.call_count >= 2
    
#     @patch.dict(os.environ, {"SECRET_KEY": "test_secret_key_12345"})
#     @patch('src.privacy.util.auth.auth_jwt.jwt.decode')
#     def test_authenticate_jwt_with_different_payloads(self, mock_decode):
#         """Test JWT authentication with various payload structures."""
#         test_payloads = [
#             {"user_id": "123", "role": "admin"},
#             {"email": "test@example.com", "permissions": ["read", "write"]},
#             {"sub": "subject", "iat": 1234567890, "exp": 1234567890},
#             {}  # Empty payload
#         ]
        
#         for payload in test_payloads:
#             mock_decode.return_value = payload
#             credentials = MagicMock(spec=HTTPAuthorizationCredentials)
#             credentials.credentials = "test.token"
            
#             result = authenticate_jwt(credentials)
#             assert result == payload
    
#     @patch.dict(os.environ, {"SECRET_KEY": "test_secret_key_12345"})
#     @patch('src.privacy.util.auth.auth_jwt.jwt.decode')
#     def test_authenticate_jwt_with_complex_payload(self, mock_decode):
#         """Test JWT authentication with complex nested payload."""
#         complex_payload = {
#             "user_id": "67890",
#             "username": "admin_user",
#             "roles": ["admin", "moderator"],
#             "metadata": {
#                 "department": "IT",
#                 "level": 5
#             },
#             "exp": 1735000000,
#             "iat": 1734000000
#         }
        
#         mock_decode.return_value = complex_payload
#         credentials = MagicMock(spec=HTTPAuthorizationCredentials)
#         credentials.credentials = "complex.jwt.token"
        
#         result = authenticate_jwt(credentials)
        
#         assert result == complex_payload
#         assert result["roles"] == ["admin", "moderator"]
#         assert result["metadata"]["department"] == "IT"
    
#     @patch.dict(os.environ, {"SECRET_KEY": "test_secret_key_12345"})
#     @patch('src.privacy.util.auth.auth_jwt.jwt.decode')
#     def test_authenticate_jwt_extracts_credentials(self, mock_decode):
#         """Test that authenticate_jwt correctly extracts token from credentials."""
#         mock_decode.return_value = {"user": "test"}
        
#         credentials = MagicMock(spec=HTTPAuthorizationCredentials)
#         test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token"
#         credentials.credentials = test_token
        
#         authenticate_jwt(credentials)
        
#         # Verify the token was extracted correctly
#         args, kwargs = mock_decode.call_args
#         assert args[0] == test_token
    
#     @patch('src.privacy.util.auth.auth_jwt.secret_key', 'another_secret_key')
#     @patch('src.privacy.util.auth.auth_jwt.jwt.decode')
#     def test_authenticate_jwt_uses_env_secret_key(self, mock_decode):
#         """Test that authenticate_jwt uses the SECRET_KEY from environment."""
#         mock_decode.return_value = {"user": "test"}
        
#         credentials = MagicMock(spec=HTTPAuthorizationCredentials)
#         credentials.credentials = "test.token"
        
#         authenticate_jwt(credentials)
        
#         # Verify the secret key from environment was used
#         args, kwargs = mock_decode.call_args
#         assert args[1] == "another_secret_key"
    
#     def test_get_auth_jwt_returns_function(self):
#         """Test that get_auth_jwt returns the authenticate function."""
#         auth_func = get_auth_jwt()
#         assert callable(auth_func)
#         assert auth_func is authenticate_jwt
    
#     def test_get_auth_jwt_returns_same_function(self):
#         """Test that get_auth_jwt consistently returns the same function."""
#         auth_func1 = get_auth_jwt()
#         auth_func2 = get_auth_jwt()
#         assert auth_func1 is auth_func2
    
#     @patch.dict(os.environ, {"SECRET_KEY": "test_key"})
#     @patch('src.privacy.util.auth.auth_jwt.jwt.decode')
#     def test_authenticate_jwt_decode_options(self, mock_decode):
#         """Test that authenticate_jwt uses correct decode options."""
#         mock_decode.return_value = {"user": "test"}
        
#         credentials = MagicMock(spec=HTTPAuthorizationCredentials)
#         credentials.credentials = "test.token"
        
#         authenticate_jwt(credentials)
        
#         # Verify decode options
#         args, kwargs = mock_decode.call_args
#         assert kwargs["algorithms"] == ["HS256"]
#         assert kwargs["options"] == {"verify_signature": True, "verify_aud": False}
    
#     @patch.dict(os.environ, {"SECRET_KEY": "test_secret_key_12345"})
#     @patch('src.privacy.util.auth.auth_jwt.jwt.decode')
#     @patch('src.privacy.util.auth.auth_jwt.log')
#     def test_authenticate_jwt_logs_traceback_on_error(self, mock_log, mock_decode):
#         """Test that unexpected errors log traceback information."""
#         error = RuntimeError("Test error")
#         mock_decode.side_effect = error
        
#         credentials = MagicMock(spec=HTTPAuthorizationCredentials)
#         credentials.credentials = "test.token"
        
#         with pytest.raises(HTTPException):
#             authenticate_jwt(credentials)
        
#         # Verify logging of error and traceback
#         error_calls = [call for call in mock_log.error.call_args_list]
#         assert len(error_calls) >= 2
#         # First call should log the error message
#         assert "Test error" in str(error_calls[0])


# class TestAuthClientId:
#     """Test the Client ID authentication module."""
    
#     @patch('src.privacy.util.auth.auth_client_id.requests.get')
#     @patch.dict(os.environ, {'AZURE_AD_JWKS_URL': 'https://example.com/jwks'})
#     def test_get_public_keys_success(self, mock_get):
#         """Test successful retrieval of public keys."""
#         mock_response = Mock()
#         mock_response.status_code = 200
#         mock_response.json.return_value = {
#             'keys': [
#                 {'kid': 'key1', 'kty': 'RSA', 'n': 'abc123'},
#                 {'kid': 'key2', 'kty': 'RSA', 'n': 'def456'}
#             ]
#         }
#         mock_get.return_value = mock_response
        
#         result = get_public_keys()
        
#         assert 'key1' in result
#         assert 'key2' in result
#         assert result['key1']['kty'] == 'RSA'
#         assert result['key2']['n'] == 'def456'
#         mock_get.assert_called_once_with('https://example.com/jwks')
    
#     @patch('src.privacy.util.auth.auth_client_id.requests.get')
#     @patch('src.privacy.util.auth.auth_client_id.log')
#     @patch.dict(os.environ, {'AZURE_AD_JWKS_URL': 'https://example.com/jwks'})
#     def test_get_public_keys_http_error(self, mock_log, mock_get):
#         """Test get_public_keys when HTTP request fails."""
#         mock_response = Mock()
#         mock_response.status_code = 500
#         mock_get.return_value = mock_response
        
#         with pytest.raises(HTTPException) as exc_info:
#             get_public_keys()
        
#         assert exc_info.value.status_code == 500
#         assert exc_info.value.detail == "Failed to fetch JWKS"
#         mock_log.error.assert_called()
    
#     @patch('src.privacy.util.auth.auth_client_id.requests.get')
#     @patch('src.privacy.util.auth.auth_client_id.log')
#     @patch.dict(os.environ, {'AZURE_AD_JWKS_URL': 'https://example.com/jwks'})
#     def test_get_public_keys_invalid_response(self, mock_log, mock_get):
#         """Test get_public_keys when response format is invalid."""
#         mock_response = Mock()
#         mock_response.status_code = 200
#         mock_response.json.return_value = {'invalid': 'format'}
#         mock_get.return_value = mock_response
        
#         with pytest.raises(HTTPException) as exc_info:
#             get_public_keys()
        
#         assert exc_info.value.status_code == 500
#         assert exc_info.value.detail == "JWKS response format is invalid"
#         mock_log.error.assert_called_with("JWKS response does not contain 'keys'")
    
#     @patch('src.privacy.util.auth.auth_client_id.get_public_keys')
#     @patch('src.privacy.util.auth.auth_client_id.jwt.get_unverified_header')
#     @patch('src.privacy.util.auth.auth_client_id.jwt.decode')
#     @patch('src.privacy.util.auth.auth_client_id.log')
#     @patch.dict(os.environ, {'AZURE_CLIENT_ID': 'test-client-id', 'AZURE_TENANT_ID': 'test-tenant-id'})
#     def test_authenticate_client_id_success(self, mock_log, mock_decode, mock_header, mock_get_keys):
#         """Test successful client ID authentication."""
#         # Setup mocks
#         mock_header.return_value = {'kid': 'key1', 'alg': 'HS256'}
#         mock_get_keys.return_value = {
#             'key1': {'kid': 'key1', 'kty': 'RSA', 'n': 'abc123'}
#         }
#         mock_decode.return_value = {
#             'aud': 'test-client-id',
#             'iss': 'https://login.microsoftonline.com/test-tenant-id',
#             'tid': 'test-tenant-id',
#             'sub': 'user123'
#         }
        
#         credentials = MagicMock(spec=HTTPAuthorizationCredentials)
#         credentials.credentials = "valid.jwt.token"
        
#         # Should not raise exception
#         authenticate_client_id(credentials)
        
#         # Verify calls
#         mock_header.assert_called_once_with("valid.jwt.token")
#         mock_get_keys.assert_called_once()
#         mock_decode.assert_called_once()
        
#         # Verify logging
#         assert mock_log.info.call_count >= 4
    
#     @patch('src.privacy.util.auth.auth_client_id.get_public_keys')
#     @patch('src.privacy.util.auth.auth_client_id.jwt.get_unverified_header')
#     @patch('src.privacy.util.auth.auth_client_id.jwt.decode')
#     @patch('src.privacy.util.auth.auth_client_id.log')
#     @patch.dict(os.environ, {'AZURE_CLIENT_ID': 'test-client-id'})
#     def test_authenticate_client_id_expired_token(self, mock_log, mock_decode, mock_header, mock_get_keys):
#         """Test authentication with expired token."""
#         mock_header.return_value = {'kid': 'key1'}
#         mock_get_keys.return_value = {'key1': {'kid': 'key1'}}
#         mock_decode.side_effect = ExpiredSignatureError("Token has expired")
        
#         credentials = MagicMock(spec=HTTPAuthorizationCredentials)
#         credentials.credentials = "expired.token"
        
#         with pytest.raises(HTTPException) as exc_info:
#             authenticate_client_id(credentials)
        
#         assert exc_info.value.status_code == 401
#         assert exc_info.value.detail == "Token has expired"
#         mock_log.error.assert_called()
    
#     @patch('src.privacy.util.auth.auth_client_id.get_public_keys')
#     @patch('src.privacy.util.auth.auth_client_id.jwt.get_unverified_header')
#     @patch('src.privacy.util.auth.auth_client_id.jwt.decode')
#     @patch('src.privacy.util.auth.auth_client_id.log')
#     @patch.dict(os.environ, {'AZURE_CLIENT_ID': 'test-client-id'})
#     def test_authenticate_client_id_invalid_token(self, mock_log, mock_decode, mock_header, mock_get_keys):
#         """Test authentication with invalid token."""
#         mock_header.return_value = {'kid': 'key1'}
#         mock_get_keys.return_value = {'key1': {'kid': 'key1'}}
#         mock_decode.side_effect = JWTError("Invalid token signature")
        
#         credentials = MagicMock(spec=HTTPAuthorizationCredentials)
#         credentials.credentials = "invalid.token"
        
#         with pytest.raises(HTTPException) as exc_info:
#             authenticate_client_id(credentials)
        
#         assert exc_info.value.status_code == 401
#         assert exc_info.value.detail == "Invalid token"
#         mock_log.error.assert_called()
    
#     @patch('src.privacy.util.auth.auth_client_id.get_public_keys')
#     @patch('src.privacy.util.auth.auth_client_id.jwt.get_unverified_header')
#     @patch('src.privacy.util.auth.auth_client_id.log')
#     @patch.dict(os.environ, {'AZURE_CLIENT_ID': 'test-client-id'})
#     def test_authenticate_client_id_unexpected_error(self, mock_log, mock_header, mock_get_keys):
#         """Test authentication with unexpected error."""
#         mock_header.return_value = {'kid': 'key1'}
#         mock_get_keys.side_effect = ValueError("Unexpected error")
        
#         credentials = MagicMock(spec=HTTPAuthorizationCredentials)
#         credentials.credentials = "problem.token"
        
#         with pytest.raises(HTTPException) as exc_info:
#             authenticate_client_id(credentials)
        
#         assert exc_info.value.status_code == 500
#         assert exc_info.value.detail == "Unexpected error"
#         mock_log.error.assert_called()
    
#     @patch('src.privacy.util.auth.auth_client_id.get_public_keys')
#     @patch('src.privacy.util.auth.auth_client_id.jwt.get_unverified_header')
#     @patch('src.privacy.util.auth.auth_client_id.jwt.decode')
#     @patch('src.privacy.util.auth.auth_client_id.AZURE_CLIENT_ID', 'my-client-id')
#     def test_authenticate_client_id_uses_correct_audience(self, mock_decode, mock_header, mock_get_keys):
#         """Test that authentication uses correct client ID as audience."""
#         mock_header.return_value = {'kid': 'key1'}
#         mock_get_keys.return_value = {'key1': {'kid': 'key1'}}
#         mock_decode.return_value = {'aud': 'my-client-id', 'iss': 'issuer', 'tid': 'tenant'}
        
#         credentials = MagicMock(spec=HTTPAuthorizationCredentials)
#         credentials.credentials = "test.token"
        
#         authenticate_client_id(credentials)
        
#         # Verify decode was called with correct audience
#         call_kwargs = mock_decode.call_args[1]
#         assert call_kwargs['audience'] == 'my-client-id'
    
#     @patch('src.privacy.util.auth.auth_client_id.get_public_keys')
#     @patch('src.privacy.util.auth.auth_client_id.jwt.get_unverified_header')
#     @patch('src.privacy.util.auth.auth_client_id.jwt.decode')
#     @patch.dict(os.environ, {'AZURE_CLIENT_ID': 'test-client-id'})
#     def test_authenticate_client_id_extracts_kid_from_header(self, mock_decode, mock_header, mock_get_keys):
#         """Test that kid is correctly extracted from token header."""
#         mock_header.return_value = {'kid': 'specific-key-id', 'alg': 'HS256'}
#         mock_get_keys.return_value = {
#             'specific-key-id': {'kid': 'specific-key-id', 'key': 'value'}
#         }
#         mock_decode.return_value = {'aud': 'test-client-id', 'iss': 'issuer', 'tid': 'tenant'}
        
#         credentials = MagicMock(spec=HTTPAuthorizationCredentials)
#         credentials.credentials = "token.with.kid"
        
#         authenticate_client_id(credentials)
        
#         # Verify the correct key was used
#         args, kwargs = mock_decode.call_args
#         assert args[1] == {'kid': 'specific-key-id', 'key': 'value'}
    
#     @patch('src.privacy.util.auth.auth_client_id.get_public_keys')
#     @patch('src.privacy.util.auth.auth_client_id.jwt.get_unverified_header')
#     @patch('src.privacy.util.auth.auth_client_id.jwt.decode')
#     @patch.dict(os.environ, {'AZURE_CLIENT_ID': 'test-client-id'})
#     def test_authenticate_client_id_decode_options(self, mock_decode, mock_header, mock_get_keys):
#         """Test that JWT decode uses correct options."""
#         mock_header.return_value = {'kid': 'key1'}
#         mock_get_keys.return_value = {'key1': {'kid': 'key1'}}
#         mock_decode.return_value = {'aud': 'test-client-id', 'iss': 'issuer', 'tid': 'tenant'}
        
#         credentials = MagicMock(spec=HTTPAuthorizationCredentials)
#         credentials.credentials = "test.token"
        
#         authenticate_client_id(credentials)
        
#         # Verify decode options
#         call_kwargs = mock_decode.call_args[1]
#         assert call_kwargs['algorithms'] == ['HS256']
#         assert call_kwargs['options'] == {"verify_signature": True}
    
#     def test_get_auth_client_id_returns_function(self):
#         """Test that get_auth_client_id returns the authenticate function."""
#         auth_func = get_auth_client_id()
#         assert callable(auth_func)
#         assert auth_func is authenticate_client_id
    
#     def test_get_auth_client_id_returns_same_function(self):
#         """Test that get_auth_client_id consistently returns the same function."""
#         auth_func1 = get_auth_client_id()
#         auth_func2 = get_auth_client_id()
#         assert auth_func1 is auth_func2
    
#     @patch('src.privacy.util.auth.auth_client_id.get_public_keys')
#     @patch('src.privacy.util.auth.auth_client_id.jwt.get_unverified_header')
#     @patch('src.privacy.util.auth.auth_client_id.jwt.decode')
#     @patch('src.privacy.util.auth.auth_client_id.log')
#     @patch.dict(os.environ, {'AZURE_CLIENT_ID': 'test-client-id'})
#     def test_authenticate_client_id_logs_decoded_token_info(self, mock_log, mock_decode, mock_header, mock_get_keys):
#         """Test that decoded token information is logged."""
#         mock_header.return_value = {'kid': 'key1'}
#         mock_get_keys.return_value = {'key1': {'kid': 'key1'}}
#         decoded_token = {
#             'aud': 'test-client-id',
#             'iss': 'https://login.microsoftonline.com/tenant-id',
#             'tid': 'tenant-id',
#             'sub': 'user@example.com'
#         }
#         mock_decode.return_value = decoded_token
        
#         credentials = MagicMock(spec=HTTPAuthorizationCredentials)
#         credentials.credentials = "test.token"
        
#         authenticate_client_id(credentials)
        
#         # Verify info logs were called
#         info_calls = [str(call) for call in mock_log.info.call_args_list]
#         assert len(info_calls) >= 4
    
#     @patch('src.privacy.util.auth.auth_client_id.requests.get')
#     @patch.dict(os.environ, {'AZURE_AD_JWKS_URL': 'https://test.com/keys'})
#     def test_get_public_keys_multiple_keys(self, mock_get):
#         """Test get_public_keys with multiple keys."""
#         mock_response = Mock()
#         mock_response.status_code = 200
#         mock_response.json.return_value = {
#             'keys': [
#                 {'kid': 'key1', 'kty': 'RSA', 'use': 'sig'},
#                 {'kid': 'key2', 'kty': 'RSA', 'use': 'sig'},
#                 {'kid': 'key3', 'kty': 'RSA', 'use': 'enc'}
#             ]
#         }
#         mock_get.return_value = mock_response
        
#         result = get_public_keys()
        
#         assert len(result) == 3
#         assert all(kid in result for kid in ['key1', 'key2', 'key3'])
#         assert result['key3']['use'] == 'enc'

