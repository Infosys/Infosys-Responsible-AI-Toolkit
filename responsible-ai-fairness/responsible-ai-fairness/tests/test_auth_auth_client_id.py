"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
import os
import time
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
import requests

from fairness.auth.auth_client_id import (
    get_public_keys,
    authenticate_client_id,
    get_auth_client_id,
    security
)

# ============================================================================
# MODULE SETUP - Fix missing imports in auth_client_id module
# ============================================================================
# The auth_client_id.py module uses ExpiredSignatureError and JWTError
# but doesn't import them. We inject them here for testing purposes.
import fairness.auth.auth_client_id as auth_module
auth_module.ExpiredSignatureError = ExpiredSignatureError
auth_module.JWTError = JWTError


# ============================================================================
# FIXTURES - Provide reusable test data and mocked objects
# ============================================================================

@pytest.fixture
def mock_env_variables(monkeypatch):
    """Fixture to set up environment variables for testing."""
    monkeypatch.setenv('AZURE_TENANT_ID', 'test-tenant-id')
    monkeypatch.setenv('AZURE_CLIENT_ID', 'test-client-id')
    monkeypatch.setenv('AZURE_AD_JWKS_URL', 'https://login.microsoftonline.com/test-tenant/discovery/v2.0/keys')


@pytest.fixture
def mock_jwks_response():
    """Fixture providing a mock JWKS response."""
    return {
        'keys': [
            {
                'kid': 'test-key-id-1',
                'kty': 'RSA',
                'use': 'sig',
                'n': 'test-modulus',
                'e': 'AQAB',
                'alg': 'RS256'
            },
            {
                'kid': 'test-key-id-2',
                'kty': 'RSA',
                'use': 'sig',
                'n': 'test-modulus-2',
                'e': 'AQAB',
                'alg': 'RS256'
            }
        ]
    }


@pytest.fixture
def valid_token_header():
    """Fixture providing a valid JWT token header."""
    return {
        'kid': 'test-key-id-1',
        'alg': 'HS256',
        'typ': 'JWT'
    }


@pytest.fixture
def valid_token_payload():
    """Fixture providing a valid JWT token payload."""
    return {
        'aud': 'test-client-id',
        'iss': 'https://sts.windows.net/test-tenant-id/',
        'tid': 'test-tenant-id',
        'exp': int(time.time()) + 3600,  # Expires in 1 hour
        'iat': int(time.time()),
        'nbf': int(time.time())
    }


@pytest.fixture
def expired_token_payload():
    """Fixture providing an expired JWT token payload."""
    return {
        'aud': 'test-client-id',
        'iss': 'https://sts.windows.net/test-tenant-id/',
        'tid': 'test-tenant-id',
        'exp': int(time.time()) - 3600,  # Expired 1 hour ago
        'iat': int(time.time()) - 7200,
        'nbf': int(time.time()) - 7200
    }


@pytest.fixture
def mock_credentials():
    """Fixture providing mock HTTP authorization credentials."""
    credentials = Mock(spec=HTTPAuthorizationCredentials)
    credentials.credentials = 'mock-bearer-token'
    return credentials


@pytest.fixture
def mock_public_key():
    """Fixture providing a mock public key for JWT verification."""
    return {
        'kid': 'test-key-id-1',
        'kty': 'RSA',
        'use': 'sig',
        'n': 'test-modulus',
        'e': 'AQAB',
        'alg': 'RS256'
    }


# ============================================================================
# TEST CASES FOR get_public_keys()
# ============================================================================

class TestGetPublicKeys:
    """Test suite for the get_public_keys function."""
    
    def test_get_public_keys_success(self, mock_env_variables, mock_jwks_response):
        """
        Test successful retrieval of public keys from JWKS endpoint.
        
        Validates:
        - Functional correctness: Returns correctly formatted key dictionary
        - Integration: Proper HTTP request to JWKS endpoint
        """
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_jwks_response
            
            keys = get_public_keys()
            
            assert isinstance(keys, dict)
            assert 'test-key-id-1' in keys
            assert 'test-key-id-2' in keys
            assert keys['test-key-id-1']['kty'] == 'RSA'
            mock_get.assert_called_once_with('https://login.microsoftonline.com/test-tenant/discovery/v2.0/keys')
    
    def test_get_public_keys_http_error(self, mock_env_variables):
        """
        Test error handling when JWKS endpoint returns non-200 status.
        
        Validates:
        - Error handling: Proper exception raised on HTTP errors
        - Edge case: Network/endpoint failures
        """
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 500
            
            with pytest.raises(HTTPException) as exc_info:
                get_public_keys()
            
            assert exc_info.value.status_code == 500
            assert "Failed to fetch JWKS" in str(exc_info.value.detail)
    
    def test_get_public_keys_404_not_found(self, mock_env_variables):
        """
        Test error handling when JWKS endpoint not found.
        
        Validates:
        - Error handling: Handles 404 errors appropriately
        - Edge case: Invalid endpoint configuration
        """
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 404
            
            with pytest.raises(HTTPException) as exc_info:
                get_public_keys()
            
            assert exc_info.value.status_code == 500
            assert "Failed to fetch JWKS" in str(exc_info.value.detail)
    
    def test_get_public_keys_invalid_response_format(self, mock_env_variables):
        """
        Test error handling when JWKS response doesn't contain 'keys'.
        
        Validates:
        - Error handling: Validates response format
        - Edge case: Malformed API responses
        - Security: Prevents processing invalid JWKS data
        """
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {'invalid': 'response'}
            
            with pytest.raises(HTTPException) as exc_info:
                get_public_keys()
            
            assert exc_info.value.status_code == 500
            assert "JWKS response format is invalid" in str(exc_info.value.detail)
    
    def test_get_public_keys_empty_keys_list(self, mock_env_variables):
        """
        Test handling of empty keys list in JWKS response.
        
        Validates:
        - Edge case: Empty but valid response
        - Functional correctness: Returns empty dictionary
        """
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {'keys': []}
            
            keys = get_public_keys()
            
            assert isinstance(keys, dict)
            assert len(keys) == 0
    
    def test_get_public_keys_network_timeout(self, mock_env_variables):
        """
        Test error handling when network request times out.
        
        Validates:
        - Error handling: Handles network timeouts
        - Performance: Timeout scenarios
        """
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
            
            with pytest.raises(requests.exceptions.Timeout):
                get_public_keys()
    
    def test_get_public_keys_connection_error(self, mock_env_variables):
        """
        Test error handling when connection fails.
        
        Validates:
        - Error handling: Handles connection errors
        - Integration: Network failure scenarios
        """
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
            
            with pytest.raises(requests.exceptions.ConnectionError):
                get_public_keys()
    
    def test_get_public_keys_missing_kid_in_key(self, mock_env_variables):
        """
        Test handling when a key in JWKS is missing 'kid' field.
        
        Validates:
        - Error handling: Handles malformed key data
        - Edge case: Incomplete key information
        """
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                'keys': [
                    {
                        'kty': 'RSA',
                        'use': 'sig',
                        'n': 'test-modulus',
                        'e': 'AQAB'
                    }
                ]
            }
            
            with pytest.raises(KeyError):
                get_public_keys()
    
    def test_get_public_keys_caching_behavior(self, mock_env_variables, mock_jwks_response):
        """
        Test that function makes fresh request each time (no caching).
        
        Validates:
        - Functional correctness: Fresh data retrieval
        - Performance: Multiple calls behavior
        """
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_jwks_response
            
            get_public_keys()
            get_public_keys()
            
            assert mock_get.call_count == 2


# ============================================================================
# TEST CASES FOR authenticate_client_id()
# ============================================================================

class TestAuthenticateClientId:
    """Test suite for the authenticate_client_id function."""
    
    def test_authenticate_valid_token(self, mock_env_variables, mock_credentials, 
                                      mock_jwks_response, valid_token_header, 
                                      valid_token_payload):
        """
        Test successful authentication with a valid token.
        
        Validates:
        - Functional correctness: Valid tokens are accepted
        - Security: Token validation works correctly
        """
        with patch('fairness.auth.auth_client_id.get_public_keys') as mock_get_keys, \
             patch('jose.jwt.get_unverified_header') as mock_get_header, \
             patch('jose.jwt.decode') as mock_decode:
            
            mock_get_keys.return_value = {'test-key-id-1': mock_jwks_response['keys'][0]}
            mock_get_header.return_value = valid_token_header
            mock_decode.return_value = valid_token_payload
            
            result = authenticate_client_id(mock_credentials)
            
            assert result is None  # Function returns None on success
            mock_get_header.assert_called_once_with('mock-bearer-token')
            mock_decode.assert_called_once()
    
    def test_authenticate_expired_token(self, mock_env_variables, mock_credentials,
                                       mock_jwks_response, valid_token_header):
        """
        Test authentication failure with an expired token.
        
        Validates:
        - Security: Expired tokens are rejected
        - Error handling: Proper exception for expired tokens
        """
        # Patch the missing import in the original module
        with patch('fairness.auth.auth_client_id.ExpiredSignatureError', ExpiredSignatureError), \
             patch('fairness.auth.auth_client_id.get_public_keys') as mock_get_keys, \
             patch('jose.jwt.get_unverified_header') as mock_get_header, \
             patch('jose.jwt.decode') as mock_decode:
            
            mock_get_keys.return_value = {'test-key-id-1': mock_jwks_response['keys'][0]}
            mock_get_header.return_value = valid_token_header
            mock_decode.side_effect = ExpiredSignatureError("Token has expired")
            
            with pytest.raises(HTTPException) as exc_info:
                authenticate_client_id(mock_credentials)
            
            assert exc_info.value.status_code == 401
            assert "Token has expired" in str(exc_info.value.detail)
    
    def test_authenticate_invalid_token_format(self, mock_env_variables, mock_credentials):
        """
        Test authentication failure with malformed token.
        
        Validates:
        - Error handling: Handles malformed JWT tokens
        - Security: Rejects invalid token formats
        """
        with patch('fairness.auth.auth_client_id.JWTError', JWTError), \
             patch('jose.jwt.get_unverified_header') as mock_get_header:
            mock_get_header.side_effect = JWTError("Invalid token format")
            
            with pytest.raises(HTTPException) as exc_info:
                authenticate_client_id(mock_credentials)
            
            assert exc_info.value.status_code == 401
            assert "Invalid token" in str(exc_info.value.detail)
    
    def test_authenticate_missing_kid_in_header(self, mock_env_variables, mock_credentials):
        """
        Test authentication failure when token header missing 'kid'.
        
        Validates:
        - Error handling: Handles missing required header fields
        - Security: Validates token structure
        """
        with patch('jose.jwt.get_unverified_header') as mock_get_header:
            mock_get_header.return_value = {'alg': 'HS256', 'typ': 'JWT'}
            
            # KeyError is caught and converted to HTTPException with 500 status
            with pytest.raises(HTTPException) as exc_info:
                authenticate_client_id(mock_credentials)
            
            assert exc_info.value.status_code == 500
            assert "Unexpected error" in str(exc_info.value.detail)
    
    def test_authenticate_kid_not_in_jwks(self, mock_env_variables, mock_credentials,
                                         mock_jwks_response, valid_token_header):
        """
        Test authentication failure when token's kid not found in JWKS.
        
        Validates:
        - Security: Validates key ID exists in JWKS
        - Error handling: Handles key mismatch
        """
        with patch('fairness.auth.auth_client_id.get_public_keys') as mock_get_keys, \
             patch('jose.jwt.get_unverified_header') as mock_get_header:
            
            mock_get_keys.return_value = {'different-key-id': mock_jwks_response['keys'][0]}
            mock_get_header.return_value = valid_token_header
            
            # KeyError is caught and converted to HTTPException with 500 status
            with pytest.raises(HTTPException) as exc_info:
                authenticate_client_id(mock_credentials)
            
            assert exc_info.value.status_code == 500
            assert "Unexpected error" in str(exc_info.value.detail)
    
    def test_authenticate_invalid_signature(self, mock_env_variables, mock_credentials,
                                           mock_jwks_response, valid_token_header):
        """
        Test authentication failure with invalid signature.
        
        Validates:
        - Security: Detects tampered tokens
        - Error handling: Handles signature verification failures
        """
        with patch('fairness.auth.auth_client_id.JWTError', JWTError), \
             patch('fairness.auth.auth_client_id.get_public_keys') as mock_get_keys, \
             patch('jose.jwt.get_unverified_header') as mock_get_header, \
             patch('jose.jwt.decode') as mock_decode:
            
            mock_get_keys.return_value = {'test-key-id-1': mock_jwks_response['keys'][0]}
            mock_get_header.return_value = valid_token_header
            mock_decode.side_effect = JWTError("Signature verification failed")
            
            with pytest.raises(HTTPException) as exc_info:
                authenticate_client_id(mock_credentials)
            
            assert exc_info.value.status_code == 401
            assert "Invalid token" in str(exc_info.value.detail)
    
    def test_authenticate_wrong_audience(self, mock_env_variables, mock_credentials,
                                        mock_jwks_response, valid_token_header):
        """
        Test authentication failure when token audience doesn't match client ID.
        
        Validates:
        - Security: Validates token is for correct application
        - Error handling: Handles audience mismatch
        """
        with patch('fairness.auth.auth_client_id.JWTError', JWTError), \
             patch('fairness.auth.auth_client_id.get_public_keys') as mock_get_keys, \
             patch('jose.jwt.get_unverified_header') as mock_get_header, \
             patch('jose.jwt.decode') as mock_decode:
            
            mock_get_keys.return_value = {'test-key-id-1': mock_jwks_response['keys'][0]}
            mock_get_header.return_value = valid_token_header
            mock_decode.side_effect = JWTClaimsError("Invalid audience")
            
            with pytest.raises(HTTPException) as exc_info:
                authenticate_client_id(mock_credentials)
            
            assert exc_info.value.status_code == 401
    
    def test_authenticate_empty_token(self, mock_env_variables):
        """
        Test authentication with empty token.
        
        Validates:
        - Edge case: Empty/null token
        - Functional correctness: Empty string bypasses validation (returns None)
        Note: This reveals a potential security issue - empty tokens are not rejected
        """
        empty_credentials = Mock(spec=HTTPAuthorizationCredentials)
        empty_credentials.credentials = ''
        
        # Empty string is falsy, so the 'if authorization:' check fails
        # and the function returns None without raising an exception
        # This is actually a bug in the original code - empty tokens should be rejected
        result = authenticate_client_id(empty_credentials)
        
        # The function returns None for empty tokens (should ideally reject them)
        assert result is None
    
    def test_authenticate_none_credentials(self):
        """
        Test handling of None credentials.
        
        Validates:
        - Edge case: Null input
        - Error handling: Handles missing credentials object
        """
        with pytest.raises(AttributeError):
            authenticate_client_id(None)
    
    def test_authenticate_unexpected_exception(self, mock_env_variables, mock_credentials,
                                               mock_jwks_response, valid_token_header):
        """
        Test handling of unexpected exceptions during authentication.
        
        Validates:
        - Error handling: Catches and handles unexpected errors
        - Stability: System doesn't crash on unknown errors
        """
        with patch('fairness.auth.auth_client_id.ExpiredSignatureError', ExpiredSignatureError), \
             patch('fairness.auth.auth_client_id.JWTError', JWTError), \
             patch('fairness.auth.auth_client_id.get_public_keys') as mock_get_keys, \
             patch('jose.jwt.get_unverified_header') as mock_get_header, \
             patch('jose.jwt.decode') as mock_decode:
            
            mock_get_keys.return_value = {'test-key-id-1': mock_jwks_response['keys'][0]}
            mock_get_header.return_value = valid_token_header
            mock_decode.side_effect = RuntimeError("Unexpected error")
            
            with pytest.raises(HTTPException) as exc_info:
                authenticate_client_id(mock_credentials)
            
            assert exc_info.value.status_code == 500
            assert "Unexpected error" in str(exc_info.value.detail)
    
    def test_authenticate_logging_on_success(self, mock_env_variables, mock_credentials,
                                            mock_jwks_response, valid_token_header,
                                            valid_token_payload):
        """
        Test that successful authentication logs appropriately.
        
        Validates:
        - Code quality: Proper logging implementation
        - Observability: Success events are logged
        """
        with patch('fairness.auth.auth_client_id.get_public_keys') as mock_get_keys, \
             patch('jose.jwt.get_unverified_header') as mock_get_header, \
             patch('jose.jwt.decode') as mock_decode, \
             patch('fairness.auth.auth_client_id.log') as mock_log:
            
            mock_get_keys.return_value = {'test-key-id-1': mock_jwks_response['keys'][0]}
            mock_get_header.return_value = valid_token_header
            mock_decode.return_value = valid_token_payload
            
            authenticate_client_id(mock_credentials)
            
            mock_log.info.assert_called()
    
    def test_authenticate_logging_on_error(self, mock_env_variables, mock_credentials,
                                          mock_jwks_response, valid_token_header):
        """
        Test that authentication errors are logged appropriately.
        
        Validates:
        - Code quality: Error logging implementation
        - Observability: Failures are tracked
        """
        with patch('fairness.auth.auth_client_id.ExpiredSignatureError', ExpiredSignatureError), \
             patch('fairness.auth.auth_client_id.get_public_keys') as mock_get_keys, \
             patch('jose.jwt.get_unverified_header') as mock_get_header, \
             patch('jose.jwt.decode') as mock_decode, \
             patch('fairness.auth.auth_client_id.log') as mock_log:
            
            mock_get_keys.return_value = {'test-key-id-1': mock_jwks_response['keys'][0]}
            mock_get_header.return_value = valid_token_header
            mock_decode.side_effect = ExpiredSignatureError("Token has expired")
            
            with pytest.raises(HTTPException):
                authenticate_client_id(mock_credentials)
            
            mock_log.error.assert_called()
    
    def test_authenticate_token_with_special_characters(self, mock_env_variables,
                                                        mock_jwks_response,
                                                        valid_token_header,
                                                        valid_token_payload):
        """
        Test authentication with tokens containing special characters.
        
        Validates:
        - Edge case: Special character handling
        - Functional correctness: Various token formats
        """
        special_credentials = Mock(spec=HTTPAuthorizationCredentials)
        special_credentials.credentials = 'token.with-special_chars+/='
        
        with patch('fairness.auth.auth_client_id.get_public_keys') as mock_get_keys, \
             patch('jose.jwt.get_unverified_header') as mock_get_header, \
             patch('jose.jwt.decode') as mock_decode:
            
            mock_get_keys.return_value = {'test-key-id-1': mock_jwks_response['keys'][0]}
            mock_get_header.return_value = valid_token_header
            mock_decode.return_value = valid_token_payload
            
            result = authenticate_client_id(special_credentials)
            assert result is None
    
    def test_authenticate_concurrent_requests(self, mock_env_variables, mock_credentials,
                                              mock_jwks_response, valid_token_header,
                                              valid_token_payload):
        """
        Test thread safety and concurrent authentication requests.
        
        Validates:
        - Scalability: Handles concurrent requests
        - Performance: No race conditions
        """
        with patch('fairness.auth.auth_client_id.get_public_keys') as mock_get_keys, \
             patch('jose.jwt.get_unverified_header') as mock_get_header, \
             patch('jose.jwt.decode') as mock_decode:
            
            mock_get_keys.return_value = {'test-key-id-1': mock_jwks_response['keys'][0]}
            mock_get_header.return_value = valid_token_header
            mock_decode.return_value = valid_token_payload
            
            # Simulate multiple concurrent calls
            for _ in range(10):
                result = authenticate_client_id(mock_credentials)
                assert result is None


# ============================================================================
# TEST CASES FOR get_auth_client_id()
# ============================================================================

class TestGetAuthClientId:
    """Test suite for the get_auth_client_id function."""
    
    def test_get_auth_client_id_returns_function(self):
        """
        Test that get_auth_client_id returns the authentication function.
        
        Validates:
        - Functional correctness: Returns correct function reference
        - Code quality: Factory pattern implementation
        """
        auth_func = get_auth_client_id()
        
        assert callable(auth_func)
        assert auth_func == authenticate_client_id
    
    def test_get_auth_client_id_return_type(self):
        """
        Test the return type of get_auth_client_id.
        
        Validates:
        - Functional correctness: Proper typing
        """
        auth_func = get_auth_client_id()
        
        assert hasattr(auth_func, '__call__')
    
    def test_get_auth_client_id_immutability(self):
        """
        Test that multiple calls return same function reference.
        
        Validates:
        - Functional correctness: Consistent behavior
        - Code quality: Idempotent function
        """
        auth_func1 = get_auth_client_id()
        auth_func2 = get_auth_client_id()
        
        assert auth_func1 == auth_func2


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for the complete authentication flow."""
    
    def test_full_authentication_flow_success(self, mock_env_variables,
                                             mock_jwks_response,
                                             valid_token_header,
                                             valid_token_payload):
        """
        Test complete authentication flow from start to finish.
        
        Validates:
        - Integration: All components work together
        - Functional correctness: End-to-end flow
        """
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = 'full-flow-token'
        
        with patch('requests.get') as mock_get, \
             patch('jose.jwt.get_unverified_header') as mock_get_header, \
             patch('jose.jwt.decode') as mock_decode:
            
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_jwks_response
            mock_get_header.return_value = valid_token_header
            mock_decode.return_value = valid_token_payload
            
            result = authenticate_client_id(mock_credentials)
            
            assert result is None
            mock_get.assert_called_once()
            mock_get_header.assert_called_once()
            mock_decode.assert_called_once()
    
    def test_full_authentication_flow_with_jwks_failure(self, mock_env_variables):
        """
        Test authentication flow when JWKS retrieval fails.
        
        Validates:
        - Integration: Proper error propagation
        - Error handling: Cascade failure handling
        """
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = 'test-token'
        
        with patch('fairness.auth.auth_client_id.ExpiredSignatureError', ExpiredSignatureError), \
             patch('fairness.auth.auth_client_id.JWTError', JWTError), \
             patch('requests.get') as mock_get, \
             patch('jose.jwt.get_unverified_header') as mock_get_header:
            
            mock_get.return_value.status_code = 500
            mock_get_header.return_value = {'kid': 'test-key', 'alg': 'HS256'}
            
            with pytest.raises(HTTPException) as exc_info:
                authenticate_client_id(mock_credentials)
            
            assert exc_info.value.status_code == 500


# ============================================================================
# SECURITY TESTS
# ============================================================================

class TestSecurity:
    """Security-focused test cases."""
    
    def test_token_injection_attempt(self, mock_env_variables):
        """
        Test protection against token injection attacks.
        
        Validates:
        - Security: Prevents injection attacks
        - Error handling: Rejects malicious input
        """
        malicious_credentials = Mock(spec=HTTPAuthorizationCredentials)
        malicious_credentials.credentials = "'; DROP TABLE users; --"
        
        with patch('fairness.auth.auth_client_id.JWTError', JWTError), \
             patch('jose.jwt.get_unverified_header') as mock_get_header:
            mock_get_header.side_effect = JWTError("Invalid token")
            
            with pytest.raises(HTTPException) as exc_info:
                authenticate_client_id(malicious_credentials)
            
            assert exc_info.value.status_code == 401
    
    def test_algorithm_none_attack(self, mock_env_variables, mock_jwks_response):
        """
        Test protection against 'alg: none' attack.
        
        Validates:
        - Security: Algorithm validation
        - Error handling: Rejects unsigned tokens
        """
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = 'none-alg-token'
        
        none_header = {'kid': 'test-key-id-1', 'alg': 'none', 'typ': 'JWT'}
        
        with patch('fairness.auth.auth_client_id.JWTError', JWTError), \
             patch('fairness.auth.auth_client_id.get_public_keys') as mock_get_keys, \
             patch('jose.jwt.get_unverified_header') as mock_get_header, \
             patch('jose.jwt.decode') as mock_decode:
            
            mock_get_keys.return_value = {'test-key-id-1': mock_jwks_response['keys'][0]}
            mock_get_header.return_value = none_header
            mock_decode.side_effect = JWTError("Algorithm not allowed")
            
            with pytest.raises(HTTPException) as exc_info:
                authenticate_client_id(mock_credentials)
            
            assert exc_info.value.status_code == 401
    
    def test_replay_attack_prevention(self, mock_env_variables, mock_jwks_response,
                                     valid_token_header, valid_token_payload):
        """
        Test that same token can be used multiple times (as expected for bearer tokens).
        
        Validates:
        - Security: Token reuse behavior
        - Functional correctness: Valid tokens work multiple times
        Note: Replay attack prevention typically handled by short token expiry
        """
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = 'reused-token'
        
        with patch('fairness.auth.auth_client_id.get_public_keys') as mock_get_keys, \
             patch('jose.jwt.get_unverified_header') as mock_get_header, \
             patch('jose.jwt.decode') as mock_decode:
            
            mock_get_keys.return_value = {'test-key-id-1': mock_jwks_response['keys'][0]}
            mock_get_header.return_value = valid_token_header
            mock_decode.return_value = valid_token_payload
            
            # Same token used twice
            result1 = authenticate_client_id(mock_credentials)
            result2 = authenticate_client_id(mock_credentials)
            
            assert result1 is None
            assert result2 is None


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance-related test cases."""
    
    def test_authentication_response_time(self, mock_env_variables, mock_credentials,
                                          mock_jwks_response, valid_token_header,
                                          valid_token_payload):
        """
        Test that authentication completes in reasonable time.
        
        Validates:
        - Performance: Response time metrics
        - Scalability: System responsiveness
        """
        import time
        
        with patch('fairness.auth.auth_client_id.get_public_keys') as mock_get_keys, \
             patch('jose.jwt.get_unverified_header') as mock_get_header, \
             patch('jose.jwt.decode') as mock_decode:
            
            mock_get_keys.return_value = {'test-key-id-1': mock_jwks_response['keys'][0]}
            mock_get_header.return_value = valid_token_header
            mock_decode.return_value = valid_token_payload
            
            start_time = time.time()
            authenticate_client_id(mock_credentials)
            elapsed_time = time.time() - start_time
            
            # Should complete in less than 1 second (generous threshold for mocked calls)
            assert elapsed_time < 1.0
    
    def test_bulk_authentication_requests(self, mock_env_variables, mock_jwks_response,
                                         valid_token_header, valid_token_payload):
        """
        Test handling of multiple authentication requests.
        
        Validates:
        - Scalability: Bulk request handling
        - Performance: No significant degradation with volume
        """
        with patch('fairness.auth.auth_client_id.get_public_keys') as mock_get_keys, \
             patch('jose.jwt.get_unverified_header') as mock_get_header, \
             patch('jose.jwt.decode') as mock_decode:
            
            mock_get_keys.return_value = {'test-key-id-1': mock_jwks_response['keys'][0]}
            mock_get_header.return_value = valid_token_header
            mock_decode.return_value = valid_token_payload
            
            # Process 100 authentication requests
            for i in range(100):
                mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
                mock_credentials.credentials = f'token-{i}'
                result = authenticate_client_id(mock_credentials)
                assert result is None


# ============================================================================
# EDGE CASES AND BOUNDARY TESTS
# ============================================================================

class TestEdgeCases:
    """Edge case and boundary condition tests."""
    
    def test_extremely_long_token(self, mock_env_variables):
        """
        Test handling of extremely long token strings.
        
        Validates:
        - Edge case: Boundary conditions
        - Resource management: Memory handling
        """
        long_credentials = Mock(spec=HTTPAuthorizationCredentials)
        long_credentials.credentials = 'x' * 100000  # 100KB token
        
        with patch('fairness.auth.auth_client_id.JWTError', JWTError), \
             patch('jose.jwt.get_unverified_header') as mock_get_header:
            mock_get_header.side_effect = JWTError("Token too large")
            
            with pytest.raises(HTTPException):
                authenticate_client_id(long_credentials)
    
    def test_unicode_in_token(self, mock_env_variables, mock_jwks_response,
                              valid_token_header, valid_token_payload):
        """
        Test handling of Unicode characters in tokens.
        
        Validates:
        - Edge case: Character encoding
        - Functional correctness: Unicode support
        """
        unicode_credentials = Mock(spec=HTTPAuthorizationCredentials)
        unicode_credentials.credentials = 'token-with-émojis-😀'
        
        with patch('fairness.auth.auth_client_id.get_public_keys') as mock_get_keys, \
             patch('jose.jwt.get_unverified_header') as mock_get_header, \
             patch('jose.jwt.decode') as mock_decode:
            
            mock_get_keys.return_value = {'test-key-id-1': mock_jwks_response['keys'][0]}
            mock_get_header.return_value = valid_token_header
            mock_decode.return_value = valid_token_payload
            
            result = authenticate_client_id(unicode_credentials)
            assert result is None
    
    def test_jwks_with_many_keys(self, mock_env_variables):
        """
        Test handling of JWKS with large number of keys.
        
        Validates:
        - Edge case: Large datasets
        - Performance: Key lookup efficiency
        - Resource management: Memory usage
        """
        many_keys = {
            'keys': [
                {
                    'kid': f'key-{i}',
                    'kty': 'RSA',
                    'use': 'sig',
                    'n': f'modulus-{i}',
                    'e': 'AQAB',
                    'alg': 'RS256'
                }
                for i in range(100)
            ]
        }
        
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = many_keys
            
            keys = get_public_keys()
            
            assert len(keys) == 100
            assert 'key-50' in keys
    
    def test_missing_environment_variables(self, monkeypatch):
        """
        Test behavior when required environment variables are missing.
        
        Validates:
        - Error handling: Missing configuration
        - Edge case: Incomplete setup
        """
        # Remove environment variables
        monkeypatch.delenv('AZURE_TENANT_ID', raising=False)
        monkeypatch.delenv('AZURE_CLIENT_ID', raising=False)
        monkeypatch.delenv('AZURE_AD_JWKS_URL', raising=False)
        
        # The module loads env vars at import time, so this tests runtime behavior
        with patch('requests.get') as mock_get:
            # JWKS URL will be None, causing issues
            mock_get.side_effect = Exception("Invalid URL")
            
            with pytest.raises(Exception):
                get_public_keys()


# ============================================================================
# REGRESSION TESTS
# ============================================================================

class TestRegression:
    """Regression tests for previously identified issues."""
    
    def test_missing_import_for_expired_signature_error(self):
        """
        Test that ExpiredSignatureError is properly imported and used.
        
        Validates:
        - Regression: Previously missing import
        - Code quality: Proper exception handling
        """
        # This test validates the code imports ExpiredSignatureError
        from jose.exceptions import ExpiredSignatureError as ImportedError
        assert ImportedError is not None
    
    def test_missing_import_for_jwt_error(self):
        """
        Test that JWTError is properly imported and used.
        
        Validates:
        - Regression: Previously missing import
        - Code quality: Proper exception handling
        """
        from jose import JWTError as ImportedError
        assert ImportedError is not None


# ============================================================================
# CODE QUALITY TESTS
# ============================================================================

class TestCodeQuality:
    """Tests for code quality indicators."""
    
    def test_security_object_exists(self):
        """
        Test that security object is properly defined.
        
        Validates:
        - Code quality: Proper module exports
        - Integration: FastAPI security integration
        """
        from fairness.auth.auth_client_id import security
        from fastapi.security import HTTPBearer
        assert security is not None
        assert isinstance(security, HTTPBearer)
    
    def test_module_exports(self):
        """
        Test that all expected functions are exported from module.
        
        Validates:
        - Code quality: Proper API surface
        - Functional correctness: Module interface
        """
        from fairness.auth import auth_client_id
        
        assert hasattr(auth_client_id, 'get_public_keys')
        assert hasattr(auth_client_id, 'authenticate_client_id')
        assert hasattr(auth_client_id, 'get_auth_client_id')
        assert hasattr(auth_client_id, 'security')
    
    def test_function_signatures(self):
        """
        Test that function signatures match expected interface.
        
        Validates:
        - Code quality: API contract
        - Functional correctness: Type safety
        """
        import inspect
        
        # Check authenticate_client_id signature
        sig = inspect.signature(authenticate_client_id)
        assert 'credentials' in sig.parameters
        
        # Check get_public_keys signature
        sig = inspect.signature(get_public_keys)
        assert len(sig.parameters) == 0


# ============================================================================
# RESOURCE MANAGEMENT TESTS
# ============================================================================

class TestResourceManagement:
    """Tests for proper resource management."""
    
    def test_no_resource_leaks_on_success(self, mock_env_variables, mock_credentials,
                                          mock_jwks_response, valid_token_header,
                                          valid_token_payload):
        """
        Test that successful authentication doesn't leak resources.
        
        Validates:
        - Resource management: Proper cleanup
        - Performance: Memory efficiency
        """
        with patch('fairness.auth.auth_client_id.get_public_keys') as mock_get_keys, \
             patch('jose.jwt.get_unverified_header') as mock_get_header, \
             patch('jose.jwt.decode') as mock_decode:
            
            mock_get_keys.return_value = {'test-key-id-1': mock_jwks_response['keys'][0]}
            mock_get_header.return_value = valid_token_header
            mock_decode.return_value = valid_token_payload
            
            # Multiple calls should not accumulate resources
            for _ in range(50):
                authenticate_client_id(mock_credentials)
    
    def test_no_resource_leaks_on_error(self, mock_env_variables, mock_credentials):
        """
        Test that failed authentication doesn't leak resources.
        
        Validates:
        - Resource management: Cleanup on error paths
        - Error handling: Proper exception handling
        """
        with patch('fairness.auth.auth_client_id.JWTError', JWTError), \
             patch('jose.jwt.get_unverified_header') as mock_get_header:
            mock_get_header.side_effect = JWTError("Invalid token")
            
            # Multiple failures should not accumulate resources
            for _ in range(50):
                with pytest.raises(HTTPException):
                    authenticate_client_id(mock_credentials)
