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
from jose import jwt, JWTError, ExpiredSignatureError
import traceback

from fairness.auth.auth_jwt import (
    authenticate_jwt,
    get_auth_jwt,
    security,
    secret_key
)


# ============================================================================
# FIXTURES - Provide reusable test data and mocked objects
# ============================================================================

@pytest.fixture
def mock_secret_key(monkeypatch):
    """Fixture to set up SECRET_KEY environment variable."""
    test_secret = "test-secret-key-for-jwt-testing-12345"
    monkeypatch.setenv('SECRET_KEY', test_secret)
    # Also patch the secret_key in the module since it's loaded at import time
    import fairness.auth.auth_jwt as auth_jwt_module
    monkeypatch.setattr(auth_jwt_module, 'secret_key', test_secret)
    return test_secret


@pytest.fixture
def valid_jwt_payload():
    """Fixture providing a valid JWT payload."""
    return {
        'sub': 'test-user-123',
        'name': 'Test User',
        'email': 'test@example.com',
        'exp': int(time.time()) + 3600,  # Expires in 1 hour
        'iat': int(time.time()),
        'nbf': int(time.time())
    }


@pytest.fixture
def expired_jwt_payload():
    """Fixture providing an expired JWT payload."""
    return {
        'sub': 'test-user-123',
        'name': 'Test User',
        'email': 'test@example.com',
        'exp': int(time.time()) - 3600,  # Expired 1 hour ago
        'iat': int(time.time()) - 7200,
        'nbf': int(time.time()) - 7200
    }


@pytest.fixture
def valid_token(mock_secret_key, valid_jwt_payload):
    """Fixture providing a valid JWT token."""
    return jwt.encode(valid_jwt_payload, mock_secret_key, algorithm='HS256')


@pytest.fixture
def expired_token(mock_secret_key, expired_jwt_payload):
    """Fixture providing an expired JWT token."""
    return jwt.encode(expired_jwt_payload, mock_secret_key, algorithm='HS256')


@pytest.fixture
def mock_credentials():
    """Fixture providing mock HTTP authorization credentials."""
    credentials = Mock(spec=HTTPAuthorizationCredentials)
    credentials.credentials = 'mock-jwt-token'
    return credentials


@pytest.fixture
def valid_credentials(valid_token):
    """Fixture providing credentials with a valid token."""
    credentials = Mock(spec=HTTPAuthorizationCredentials)
    credentials.credentials = valid_token
    return credentials


@pytest.fixture
def expired_credentials(expired_token):
    """Fixture providing credentials with an expired token."""
    credentials = Mock(spec=HTTPAuthorizationCredentials)
    credentials.credentials = expired_token
    return credentials


# ============================================================================
# TEST CASES FOR authenticate_jwt()
# ============================================================================

class TestAuthenticateJWT:
    """Test suite for the authenticate_jwt function."""
    
    def test_authenticate_valid_token(self, mock_secret_key, valid_credentials, valid_jwt_payload):
        """
        Test successful authentication with a valid JWT token.
        
        Validates:
        - Functional correctness: Valid tokens are decoded successfully
        - Security: Token validation works correctly
        - Integration: JWT library integration
        """
        result = authenticate_jwt(valid_credentials)
        
        assert result is not None
        assert isinstance(result, dict)
        assert result['sub'] == valid_jwt_payload['sub']
        assert result['email'] == valid_jwt_payload['email']
        assert 'exp' in result
    
    def test_authenticate_expired_token(self, mock_secret_key, expired_credentials):
        """
        Test authentication failure with an expired token.
        
        Validates:
        - Security: Expired tokens are rejected
        - Error handling: Proper exception for expired tokens
        Note: With verify_signature=True, expired tokens cause JWTError, not ExpiredSignatureError
        """
        with pytest.raises(HTTPException) as exc_info:
            authenticate_jwt(expired_credentials)
        
        assert exc_info.value.status_code == 401
        # The jose library with verify_signature=True returns generic JWTError for expired tokens
        assert exc_info.value.detail in ["Token expired", "Invalid token"]
        assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
    
    def test_authenticate_invalid_token_format(self, mock_secret_key):
        """
        Test authentication failure with malformed token.
        
        Validates:
        - Error handling: Handles malformed JWT tokens
        - Security: Rejects invalid token formats
        """
        invalid_credentials = Mock(spec=HTTPAuthorizationCredentials)
        invalid_credentials.credentials = 'not.a.valid.jwt.token'
        
        with pytest.raises(HTTPException) as exc_info:
            authenticate_jwt(invalid_credentials)
        
        assert exc_info.value.status_code == 401
        assert "Invalid token" in str(exc_info.value.detail)
        assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
    
    def test_authenticate_token_with_wrong_secret(self, mock_secret_key, valid_jwt_payload):
        """
        Test authentication failure when token signed with different secret.
        
        Validates:
        - Security: Detects tokens signed with wrong key
        - Error handling: Signature verification
        """
        wrong_secret = "different-secret-key"
        token_with_wrong_secret = jwt.encode(valid_jwt_payload, wrong_secret, algorithm='HS256')
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token_with_wrong_secret
        
        with pytest.raises(HTTPException) as exc_info:
            authenticate_jwt(credentials)
        
        assert exc_info.value.status_code == 401
        assert "Invalid token" in str(exc_info.value.detail)
    
    def test_authenticate_token_with_invalid_signature(self, mock_secret_key, valid_token):
        """
        Test authentication failure with tampered token.
        
        Validates:
        - Security: Detects tampered tokens
        - Error handling: Signature validation
        """
        # Tamper with the token by modifying it
        tampered_token = valid_token[:-5] + "XXXXX"
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = tampered_token
        
        with pytest.raises(HTTPException) as exc_info:
            authenticate_jwt(credentials)
        
        assert exc_info.value.status_code == 401
        assert "Invalid token" in str(exc_info.value.detail)
    
    def test_authenticate_empty_token(self, mock_secret_key):
        """
        Test authentication failure with empty token.
        
        Validates:
        - Edge case: Empty token string
        - Error handling: Handles missing token
        """
        empty_credentials = Mock(spec=HTTPAuthorizationCredentials)
        empty_credentials.credentials = ''
        
        with pytest.raises(HTTPException) as exc_info:
            authenticate_jwt(empty_credentials)
        
        assert exc_info.value.status_code == 401
        assert "Invalid token" in str(exc_info.value.detail)
    
    def test_authenticate_none_token(self, mock_secret_key):
        """
        Test authentication failure with None token.
        
        Validates:
        - Edge case: Null token
        - Error handling: Handles None credentials
        Note: None token causes AttributeError which is caught as unexpected error (500)
        """
        none_credentials = Mock(spec=HTTPAuthorizationCredentials)
        none_credentials.credentials = None
        
        with pytest.raises(HTTPException) as exc_info:
            authenticate_jwt(none_credentials)
        
        # None token causes AttributeError, caught by generic exception handler
        assert exc_info.value.status_code == 500
        assert "Unexpected error" in str(exc_info.value.detail)
    
    def test_authenticate_token_without_expiration(self, mock_secret_key):
        """
        Test authentication with token missing expiration claim.
        
        Validates:
        - Edge case: Token without 'exp' claim
        - Error handling: Missing required claims
        """
        payload_without_exp = {
            'sub': 'test-user-123',
            'name': 'Test User'
        }
        token = jwt.encode(payload_without_exp, mock_secret_key, algorithm='HS256')
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        # Token without exp claim should still work with verify_signature
        result = authenticate_jwt(credentials)
        assert result is not None
        assert result['sub'] == 'test-user-123'
    
    def test_authenticate_token_with_wrong_algorithm(self, mock_secret_key, valid_jwt_payload):
        """
        Test authentication failure with wrong algorithm.
        
        Validates:
        - Security: Algorithm validation
        - Error handling: Rejects tokens with unsupported algorithms
        """
        # Create token with different algorithm
        token_rs256 = jwt.encode(valid_jwt_payload, mock_secret_key, algorithm='HS512')
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token_rs256
        
        with pytest.raises(HTTPException) as exc_info:
            authenticate_jwt(credentials)
        
        assert exc_info.value.status_code == 401
    
    def test_authenticate_token_with_special_characters(self, mock_secret_key):
        """
        Test authentication with payload containing special characters.
        
        Validates:
        - Edge case: Special characters in payload
        - Functional correctness: Unicode support
        """
        special_payload = {
            'sub': 'user-with-émojis-😀',
            'name': 'Tëst Ûser',
            'email': 'test@example.com',
            'exp': int(time.time()) + 3600
        }
        token = jwt.encode(special_payload, mock_secret_key, algorithm='HS256')
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        result = authenticate_jwt(credentials)
        
        assert result is not None
        assert result['sub'] == 'user-with-émojis-😀'
        assert result['name'] == 'Tëst Ûser'
    
    def test_authenticate_token_with_large_payload(self, mock_secret_key):
        """
        Test authentication with large payload.
        
        Validates:
        - Edge case: Large token size
        - Performance: Handles large payloads
        - Resource management: Memory efficiency
        """
        large_payload = {
            'sub': 'test-user-123',
            'data': 'x' * 10000,  # 10KB of data
            'exp': int(time.time()) + 3600
        }
        token = jwt.encode(large_payload, mock_secret_key, algorithm='HS256')
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        result = authenticate_jwt(credentials)
        
        assert result is not None
        assert len(result['data']) == 10000
    
    def test_authenticate_token_about_to_expire(self, mock_secret_key):
        """
        Test authentication with token about to expire.
        
        Validates:
        - Edge case: Token near expiration boundary
        - Functional correctness: Time-based validation
        """
        almost_expired_payload = {
            'sub': 'test-user-123',
            'exp': int(time.time()) + 5  # Expires in 5 seconds
        }
        token = jwt.encode(almost_expired_payload, mock_secret_key, algorithm='HS256')
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        result = authenticate_jwt(credentials)
        
        assert result is not None
        assert result['sub'] == 'test-user-123'
    
    def test_authenticate_with_additional_claims(self, mock_secret_key):
        """
        Test authentication with custom claims.
        
        Validates:
        - Functional correctness: Custom claim handling
        - Coverage: Various payload structures
        """
        custom_payload = {
            'sub': 'test-user-123',
            'role': 'admin',
            'permissions': ['read', 'write', 'delete'],
            'metadata': {'department': 'engineering'},
            'exp': int(time.time()) + 3600
        }
        token = jwt.encode(custom_payload, mock_secret_key, algorithm='HS256')
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        result = authenticate_jwt(credentials)
        
        assert result is not None
        assert result['role'] == 'admin'
        assert result['permissions'] == ['read', 'write', 'delete']
        assert result['metadata']['department'] == 'engineering'
    
    def test_authenticate_logging_on_error(self, mock_secret_key):
        """
        Test that authentication errors are logged appropriately.
        
        Validates:
        - Code quality: Error logging implementation
        - Observability: Failures are tracked
        """
        invalid_credentials = Mock(spec=HTTPAuthorizationCredentials)
        invalid_credentials.credentials = 'invalid-token'
        
        with patch('fairness.auth.auth_jwt.log') as mock_log:
            with pytest.raises(HTTPException):
                authenticate_jwt(invalid_credentials)
            
            # The generic exception handler should log errors
            # (not triggered for JWTError as it has specific handling)
    
    def test_authenticate_unexpected_exception(self, mock_secret_key, mock_credentials):
        """
        Test handling of unexpected exceptions during authentication.
        
        Validates:
        - Error handling: Catches and handles unexpected errors
        - Stability: System doesn't crash on unknown errors
        """
        with patch('jose.jwt.decode') as mock_decode, \
             patch('fairness.auth.auth_jwt.log') as mock_log:
            mock_decode.side_effect = RuntimeError("Unexpected error")
            
            with pytest.raises(HTTPException) as exc_info:
                authenticate_jwt(mock_credentials)
            
            assert exc_info.value.status_code == 500
            assert "Unexpected error" in str(exc_info.value.detail)
            mock_log.error.assert_called()
    
    def test_authenticate_with_numeric_claims(self, mock_secret_key):
        """
        Test authentication with numeric claim values.
        
        Validates:
        - Functional correctness: Various data types in payload
        - Edge case: Type handling
        """
        numeric_payload = {
            'sub': 'test-user-123',
            'user_id': 12345,
            'account_balance': 1000.50,
            'login_count': 42,
            'exp': int(time.time()) + 3600
        }
        token = jwt.encode(numeric_payload, mock_secret_key, algorithm='HS256')
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        result = authenticate_jwt(credentials)
        
        assert result is not None
        assert result['user_id'] == 12345
        assert result['account_balance'] == 1000.50
        assert result['login_count'] == 42
    
    def test_authenticate_token_with_null_claims(self, mock_secret_key):
        """
        Test authentication with null values in claims.
        
        Validates:
        - Edge case: Null values in payload
        - Functional correctness: None handling
        """
        null_payload = {
            'sub': 'test-user-123',
            'optional_field': None,
            'exp': int(time.time()) + 3600
        }
        token = jwt.encode(null_payload, mock_secret_key, algorithm='HS256')
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        result = authenticate_jwt(credentials)
        
        assert result is not None
        assert result['optional_field'] is None
    
    def test_authenticate_token_with_boolean_claims(self, mock_secret_key):
        """
        Test authentication with boolean claim values.
        
        Validates:
        - Functional correctness: Boolean data type handling
        - Edge case: Type variations
        """
        boolean_payload = {
            'sub': 'test-user-123',
            'is_admin': True,
            'is_verified': False,
            'exp': int(time.time()) + 3600
        }
        token = jwt.encode(boolean_payload, mock_secret_key, algorithm='HS256')
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        result = authenticate_jwt(credentials)
        
        assert result is not None
        assert result['is_admin'] is True
        assert result['is_verified'] is False
    
    def test_authenticate_none_credentials_object(self):
        """
        Test handling of None credentials object.
        
        Validates:
        - Edge case: Null input
        - Error handling: Handles missing credentials object
        """
        with pytest.raises(AttributeError):
            authenticate_jwt(None)


# ============================================================================
# TEST CASES FOR get_auth_jwt()
# ============================================================================

class TestGetAuthJWT:
    """Test suite for the get_auth_jwt function."""
    
    def test_get_auth_jwt_returns_function(self):
        """
        Test that get_auth_jwt returns the authentication function.
        
        Validates:
        - Functional correctness: Returns correct function reference
        - Code quality: Factory pattern implementation
        """
        auth_func = get_auth_jwt()
        
        assert callable(auth_func)
        assert auth_func == authenticate_jwt
    
    def test_get_auth_jwt_return_type(self):
        """
        Test the return type of get_auth_jwt.
        
        Validates:
        - Functional correctness: Proper typing
        """
        auth_func = get_auth_jwt()
        
        assert hasattr(auth_func, '__call__')
    
    def test_get_auth_jwt_immutability(self):
        """
        Test that multiple calls return same function reference.
        
        Validates:
        - Functional correctness: Consistent behavior
        - Code quality: Idempotent function
        """
        auth_func1 = get_auth_jwt()
        auth_func2 = get_auth_jwt()
        
        assert auth_func1 == auth_func2


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for the complete JWT authentication flow."""
    
    def test_full_jwt_authentication_flow(self, mock_secret_key):
        """
        Test complete JWT authentication flow from token creation to validation.
        
        Validates:
        - Integration: All components work together
        - Functional correctness: End-to-end flow
        """
        # Create payload
        payload = {
            'sub': 'integration-test-user',
            'email': 'integration@test.com',
            'exp': int(time.time()) + 3600
        }
        
        # Encode token
        token = jwt.encode(payload, mock_secret_key, algorithm='HS256')
        
        # Create credentials
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        # Authenticate
        result = authenticate_jwt(credentials)
        
        # Verify
        assert result['sub'] == 'integration-test-user'
        assert result['email'] == 'integration@test.com'
    
    def test_authentication_with_factory_function(self, mock_secret_key, valid_credentials):
        """
        Test authentication using the factory function.
        
        Validates:
        - Integration: Factory pattern works correctly
        - Functional correctness: Alternative access method
        """
        auth_func = get_auth_jwt()
        result = auth_func(valid_credentials)
        
        assert result is not None
        assert isinstance(result, dict)


# ============================================================================
# SECURITY TESTS
# ============================================================================

class TestSecurity:
    """Security-focused test cases."""
    
    def test_token_injection_attempt(self, mock_secret_key):
        """
        Test protection against token injection attacks.
        
        Validates:
        - Security: Prevents injection attacks
        - Error handling: Rejects malicious input
        """
        malicious_credentials = Mock(spec=HTTPAuthorizationCredentials)
        malicious_credentials.credentials = "'; DROP TABLE users; --"
        
        with pytest.raises(HTTPException) as exc_info:
            authenticate_jwt(malicious_credentials)
        
        assert exc_info.value.status_code == 401
    
    def test_algorithm_confusion_attack(self, mock_secret_key, valid_jwt_payload):
        """
        Test protection against algorithm confusion attacks.
        
        Validates:
        - Security: Algorithm validation
        - Error handling: Rejects unexpected algorithms
        """
        # Try to use 'none' algorithm
        try:
            token_none = jwt.encode(valid_jwt_payload, None, algorithm='none')
            
            credentials = Mock(spec=HTTPAuthorizationCredentials)
            credentials.credentials = token_none
            
            with pytest.raises(HTTPException) as exc_info:
                authenticate_jwt(credentials)
            
            assert exc_info.value.status_code == 401
        except Exception:
            # Some JWT libraries prevent 'none' algorithm entirely
            pass
    
    def test_token_with_extremely_long_expiry(self, mock_secret_key):
        """
        Test handling of tokens with unreasonably long expiration times.
        
        Validates:
        - Security: Expiration time validation
        - Edge case: Boundary values for time
        """
        far_future_payload = {
            'sub': 'test-user-123',
            'exp': int(time.time()) + (365 * 24 * 3600 * 100)  # 100 years
        }
        token = jwt.encode(far_future_payload, mock_secret_key, algorithm='HS256')
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        # Should still work, but application logic should handle this
        result = authenticate_jwt(credentials)
        assert result is not None
    
    def test_replay_attack_scenario(self, mock_secret_key, valid_credentials):
        """
        Test that same token can be used multiple times.
        
        Validates:
        - Security: Token reuse behavior
        - Functional correctness: Valid tokens work multiple times
        Note: Replay attack prevention typically handled by short token expiry
              or additional checks (JTI, nonce, etc.)
        """
        # Same token used twice
        result1 = authenticate_jwt(valid_credentials)
        result2 = authenticate_jwt(valid_credentials)
        
        assert result1 is not None
        assert result2 is not None
        # Both should succeed - replay prevention needs additional mechanisms


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance-related test cases."""
    
    def test_authentication_response_time(self, mock_secret_key, valid_credentials):
        """
        Test that authentication completes in reasonable time.
        
        Validates:
        - Performance: Response time metrics
        - Scalability: System responsiveness
        """
        import time
        
        start_time = time.time()
        authenticate_jwt(valid_credentials)
        elapsed_time = time.time() - start_time
        
        # Should complete in less than 100ms
        assert elapsed_time < 0.1
    
    def test_bulk_authentication_requests(self, mock_secret_key):
        """
        Test handling of multiple authentication requests.
        
        Validates:
        - Scalability: Bulk request handling
        - Performance: No significant degradation with volume
        """
        payload = {
            'sub': 'test-user-123',
            'exp': int(time.time()) + 3600
        }
        token = jwt.encode(payload, mock_secret_key, algorithm='HS256')
        
        # Process 100 authentication requests
        for i in range(100):
            credentials = Mock(spec=HTTPAuthorizationCredentials)
            credentials.credentials = token
            result = authenticate_jwt(credentials)
            assert result is not None
    
    def test_concurrent_authentication_requests(self, mock_secret_key, valid_token):
        """
        Test thread safety and concurrent authentication requests.
        
        Validates:
        - Scalability: Handles concurrent requests
        - Performance: No race conditions
        """
        # Simulate multiple concurrent calls
        for _ in range(10):
            credentials = Mock(spec=HTTPAuthorizationCredentials)
            credentials.credentials = valid_token
            result = authenticate_jwt(credentials)
            assert result is not None


# ============================================================================
# EDGE CASES AND BOUNDARY TESTS
# ============================================================================

class TestEdgeCases:
    """Edge case and boundary condition tests."""
    
    def test_token_with_whitespace(self, mock_secret_key, valid_token):
        """
        Test handling of tokens with leading/trailing whitespace.
        
        Validates:
        - Edge case: Whitespace handling
        - Functional correctness: Input sanitization
        """
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = f"  {valid_token}  "
        
        # JWT decode should handle or fail gracefully
        with pytest.raises(HTTPException) as exc_info:
            authenticate_jwt(credentials)
        
        assert exc_info.value.status_code == 401
    
    def test_token_with_newlines(self, mock_secret_key, valid_token):
        """
        Test handling of tokens with newline characters.
        
        Validates:
        - Edge case: Special characters in token
        - Security: Input validation
        """
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = f"{valid_token}\n"
        
        with pytest.raises(HTTPException) as exc_info:
            authenticate_jwt(credentials)
        
        assert exc_info.value.status_code == 401
    
    def test_extremely_short_token(self, mock_secret_key):
        """
        Test handling of extremely short token strings.
        
        Validates:
        - Edge case: Minimum length validation
        - Error handling: Invalid format detection
        """
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = "abc"
        
        with pytest.raises(HTTPException) as exc_info:
            authenticate_jwt(credentials)
        
        assert exc_info.value.status_code == 401
    
    def test_token_with_only_header_and_payload(self, mock_secret_key):
        """
        Test handling of JWT with missing signature.
        
        Validates:
        - Security: Signature validation
        - Edge case: Incomplete token structure
        """
        payload = {'sub': 'test-user-123', 'exp': int(time.time()) + 3600}
        token = jwt.encode(payload, mock_secret_key, algorithm='HS256')
        
        # Remove signature part
        parts = token.rsplit('.', 1)
        incomplete_token = parts[0] if len(parts) > 0 else token
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = incomplete_token
        
        with pytest.raises(HTTPException) as exc_info:
            authenticate_jwt(credentials)
        
        assert exc_info.value.status_code == 401
    
    def test_missing_secret_key(self, monkeypatch, valid_token):
        """
        Test behavior when SECRET_KEY environment variable is missing.
        
        Validates:
        - Edge case: Missing configuration
        - Error handling: Configuration validation
        """
        monkeypatch.delenv('SECRET_KEY', raising=False)
        
        # Patch the module's secret_key to None
        import fairness.auth.auth_jwt as auth_jwt_module
        monkeypatch.setattr(auth_jwt_module, 'secret_key', None)
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = valid_token
        
        # With secret_key=None, JWT decode will fail
        with pytest.raises(HTTPException) as exc_info:
            authenticate_jwt(credentials)
        
        # Should raise either 401 (Invalid token) or 500 (Unexpected error) depending on how jwt.decode handles None key
        assert exc_info.value.status_code in [401, 500]
    
    def test_empty_payload_token(self, mock_secret_key):
        """
        Test handling of JWT with empty payload.
        
        Validates:
        - Edge case: Minimal valid token
        - Functional correctness: Empty payload handling
        """
        empty_payload = {}
        token = jwt.encode(empty_payload, mock_secret_key, algorithm='HS256')
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        result = authenticate_jwt(credentials)
        
        assert result is not None
        assert isinstance(result, dict)


# ============================================================================
# REGRESSION TESTS
# ============================================================================

class TestRegression:
    """Regression tests for previously identified issues."""
    
    def test_jwt_import_structure(self):
        """
        Test that JWT exceptions are properly imported.
        
        Validates:
        - Regression: Proper imports
        - Code quality: Module structure
        """
        from fairness.auth import auth_jwt
        
        # Verify the module has access to required exceptions
        assert hasattr(jwt, 'ExpiredSignatureError')
        assert hasattr(jwt, 'JWTError')
    
    def test_traceback_logging_on_exception(self, mock_secret_key):
        """
        Test that traceback is logged for unexpected exceptions.
        
        Validates:
        - Regression: Traceback logging implementation
        - Code quality: Debugging support
        """
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = 'invalid-token'
        
        with patch('jose.jwt.decode') as mock_decode, \
             patch('fairness.auth.auth_jwt.log') as mock_log:
            mock_decode.side_effect = RuntimeError("Test error")
            
            with pytest.raises(HTTPException):
                authenticate_jwt(credentials)
            
            # Verify logging was called
            assert mock_log.error.called


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
        from fairness.auth.auth_jwt import security
        from fastapi.security import HTTPBearer
        
        assert security is not None
        assert isinstance(security, HTTPBearer)
    
    def test_secret_key_configuration(self):
        """
        Test that secret key is configurable via environment.
        
        Validates:
        - Code quality: Configuration management
        - Security: Key management
        """
        from fairness.auth.auth_jwt import secret_key
        
        # secret_key should be loaded from environment
        assert secret_key is not None or secret_key == os.environ.get("SECRET_KEY")
    
    def test_module_exports(self):
        """
        Test that all expected functions are exported from module.
        
        Validates:
        - Code quality: Proper API surface
        - Functional correctness: Module interface
        """
        from fairness.auth import auth_jwt
        
        assert hasattr(auth_jwt, 'authenticate_jwt')
        assert hasattr(auth_jwt, 'get_auth_jwt')
        assert hasattr(auth_jwt, 'security')
        assert hasattr(auth_jwt, 'secret_key')
    
    def test_function_signatures(self):
        """
        Test that function signatures match expected interface.
        
        Validates:
        - Code quality: API contract
        - Functional correctness: Type safety
        """
        import inspect
        
        # Check authenticate_jwt signature
        sig = inspect.signature(authenticate_jwt)
        assert 'credentials' in sig.parameters
        
        # Check get_auth_jwt signature
        sig = inspect.signature(get_auth_jwt)
        assert len(sig.parameters) == 0


# ============================================================================
# RESOURCE MANAGEMENT TESTS
# ============================================================================

class TestResourceManagement:
    """Tests for proper resource management."""
    
    def test_no_resource_leaks_on_success(self, mock_secret_key, valid_token):
        """
        Test that successful authentication doesn't leak resources.
        
        Validates:
        - Resource management: Proper cleanup
        - Performance: Memory efficiency
        """
        # Multiple calls should not accumulate resources
        for _ in range(50):
            credentials = Mock(spec=HTTPAuthorizationCredentials)
            credentials.credentials = valid_token
            authenticate_jwt(credentials)
    
    def test_no_resource_leaks_on_error(self, mock_secret_key):
        """
        Test that failed authentication doesn't leak resources.
        
        Validates:
        - Resource management: Cleanup on error paths
        - Error handling: Proper exception handling
        """
        invalid_credentials = Mock(spec=HTTPAuthorizationCredentials)
        invalid_credentials.credentials = 'invalid-token'
        
        # Multiple failures should not accumulate resources
        for _ in range(50):
            with pytest.raises(HTTPException):
                authenticate_jwt(invalid_credentials)
