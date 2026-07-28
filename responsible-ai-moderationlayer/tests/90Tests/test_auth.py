"""
Tests for auth module.
Tests bearer token authentication and token management.
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from src.auth import Auth
import src.auth as auth_module


class TestAuth:
    """Test cases for Auth class."""

    def setup_method(self):
        """Reset global variables before each test."""
        auth_module.bearer_token = None
        auth_module.token_expiration_time = 0

    # Tests for is_env_vars_present
    @patch.dict('os.environ', {'AUTH_URL': 'https://auth.example.com'})
    def test_is_env_vars_present_with_url(self):
        """Test when AUTH_URL is present."""
        result = Auth.is_env_vars_present()
        
        assert result == 1

    @patch.dict('os.environ', {'AUTH_URL': ''})
    def test_is_env_vars_present_empty_url(self):
        """Test when AUTH_URL is empty string."""
        result = Auth.is_env_vars_present()
        
        assert result is None

    @patch('src.auth.os.getenv')
    def test_is_env_vars_present_no_url(self, mock_getenv):
        """Test when AUTH_URL environment variable doesn't exist."""
        mock_getenv.return_value = None
        
        # When getenv returns None, it will raise AttributeError on == comparison
        # The actual code checks if os.getenv("AUTH_URL")=="", so None != ""
        # This means it will return 1
        result = Auth.is_env_vars_present()
        
        assert result == 1

    # Tests for get_bearer_token
    @patch.dict('os.environ', {
        'AUTH_URL': 'https://auth.example.com',
        'CLIENT_ID': 'test_client',
        'CLIENT_SECRET': 'test_secret',
        'SCOPE': 'test_scope'
    })
    @patch('src.auth.requests.post')
    @patch('src.auth.time.time')
    def test_get_bearer_token_success(self, mock_time, mock_post):
        """Test successful bearer token retrieval."""
        mock_time.return_value = 1000
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test_token_123',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response
        
        result = Auth.get_bearer_token()
        
        assert result == 'test_token_123'
        assert auth_module.bearer_token == 'test_token_123'
        assert auth_module.token_expiration_time == 4540  # 1000 + 3600 - 60
        mock_post.assert_called_once()

    @patch.dict('os.environ', {
        'AUTH_URL': 'https://auth.example.com',
        'CLIENT_ID': 'test_client',
        'CLIENT_SECRET': 'test_secret',
        'SCOPE': 'test_scope'
    })
    @patch('src.auth.requests.post')
    def test_get_bearer_token_failure(self, mock_post):
        """Test failed bearer token retrieval."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_post.return_value = mock_response
        
        result = Auth.get_bearer_token()
        
        assert result is None
        assert auth_module.bearer_token is None

    @patch.dict('os.environ', {
        'AUTH_URL': 'https://auth.example.com',
        'CLIENT_ID': 'client123',
        'CLIENT_SECRET': 'secret456',
        'SCOPE': 'scope789'
    })
    @patch('src.auth.requests.post')
    @patch('src.auth.time.time')
    def test_get_bearer_token_payload_format(self, mock_time, mock_post):
        """Test that payload is correctly formatted."""
        mock_time.return_value = 1000
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'token',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response
        
        Auth.get_bearer_token()
        
        # Verify the payload sent to requests.post
        call_args = mock_post.call_args
        assert call_args[1]['data']['grant_type'] == 'client_credentials'
        assert call_args[1]['data']['client_id'] == 'client123'
        assert call_args[1]['data']['client_secret'] == 'secret456'
        assert call_args[1]['data']['scope'] == 'scope789'

    @patch.dict('os.environ', {
        'AUTH_URL': 'https://auth.example.com',
        'CLIENT_ID': 'test',
        'CLIENT_SECRET': 'test',
        'SCOPE': 'test'
    })
    @patch('src.auth.requests.post')
    @patch('src.auth.time.time')
    def test_get_bearer_token_expiration_calculation(self, mock_time, mock_post):
        """Test token expiration time calculation."""
        mock_time.return_value = 2000
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'token',
            'expires_in': 7200  # 2 hours
        }
        mock_post.return_value = mock_response
        
        Auth.get_bearer_token()
        
        # Should be current_time + expires_in - 60
        expected_expiration = 2000 + 7200 - 60
        assert auth_module.token_expiration_time == expected_expiration

    # Tests for get_valid_bearer_token
    @patch.dict('os.environ', {
        'AUTH_URL': 'https://auth.example.com',
        'CLIENT_ID': 'test',
        'CLIENT_SECRET': 'test',
        'SCOPE': 'test'
    })
    @patch('src.auth.requests.post')
    @patch('src.auth.time.time')
    def test_get_valid_bearer_token_when_none(self, mock_time, mock_post):
        """Test getting valid token when no token exists."""
        mock_time.return_value = 1000
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'new_token',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response
        
        auth_module.bearer_token = None
        
        result = Auth.get_valid_bearer_token()
        
        assert result == 'new_token'
        assert auth_module.bearer_token == 'new_token'

    @patch('src.auth.time.time')
    def test_get_valid_bearer_token_when_valid(self, mock_time):
        """Test getting valid token when current token is still valid."""
        mock_time.return_value = 1000
        auth_module.bearer_token = 'existing_token'
        auth_module.token_expiration_time = 5000  # Expires in future
        
        result = Auth.get_valid_bearer_token()
        
        assert result == 'existing_token'

    @patch.dict('os.environ', {
        'AUTH_URL': 'https://auth.example.com',
        'CLIENT_ID': 'test',
        'CLIENT_SECRET': 'test',
        'SCOPE': 'test'
    })
    @patch('src.auth.requests.post')
    @patch('src.auth.time.time')
    def test_get_valid_bearer_token_when_expired(self, mock_time, mock_post):
        """Test getting valid token when current token has expired."""
        mock_time.return_value = 6000
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'refreshed_token',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response
        
        auth_module.bearer_token = 'old_token'
        auth_module.token_expiration_time = 5000  # Expired
        
        result = Auth.get_valid_bearer_token()
        
        assert result == 'refreshed_token'
        assert auth_module.bearer_token == 'refreshed_token'

    @patch.dict('os.environ', {
        'AUTH_URL': 'https://auth.example.com',
        'CLIENT_ID': 'test',
        'CLIENT_SECRET': 'test',
        'SCOPE': 'test'
    })
    @patch('src.auth.requests.post')
    @patch('src.auth.time.time')
    def test_get_valid_bearer_token_exact_expiration(self, mock_time, mock_post):
        """Test token refresh at exact expiration time."""
        mock_time.return_value = 5000
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'new_token',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response
        
        auth_module.bearer_token = 'old_token'
        auth_module.token_expiration_time = 4999  # Just expired
        
        result = Auth.get_valid_bearer_token()
        
        assert result == 'new_token'

    @patch.dict('os.environ', {
        'AUTH_URL': 'https://auth.example.com',
        'CLIENT_ID': 'test',
        'CLIENT_SECRET': 'test',
        'SCOPE': 'test'
    })
    @patch('src.auth.requests.post')
    def test_get_bearer_token_http_error_codes(self, mock_post):
        """Test various HTTP error codes."""
        error_codes = [400, 401, 403, 500, 503]
        
        for code in error_codes:
            auth_module.bearer_token = None
            mock_response = MagicMock()
            mock_response.status_code = code
            mock_response.text = f'Error {code}'
            mock_post.return_value = mock_response
            
            result = Auth.get_bearer_token()
            
            assert result is None
            assert auth_module.bearer_token is None

    @patch.dict('os.environ', {
        'AUTH_URL': 'https://auth.example.com',
        'CLIENT_ID': 'test',
        'CLIENT_SECRET': 'test',
        'SCOPE': 'test'
    })
    @patch('src.auth.requests.post')
    @patch('src.auth.time.time')
    def test_multiple_token_refreshes(self, mock_time, mock_post):
        """Test multiple token refresh cycles."""
        # First token fetch
        mock_time.return_value = 1000
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'token1',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response
        
        token1 = Auth.get_valid_bearer_token()
        assert token1 == 'token1'
        
        # Token still valid
        mock_time.return_value = 2000
        token2 = Auth.get_valid_bearer_token()
        assert token2 == 'token1'  # Same token
        
        # Token expired, refresh
        mock_time.return_value = 10000
        mock_response.json.return_value = {
            'access_token': 'token2',
            'expires_in': 3600
        }
        token3 = Auth.get_valid_bearer_token()
        assert token3 == 'token2'  # New token

    def test_global_variables_initialization(self):
        """Test that global variables are properly defined."""
        import src.auth as auth
        
        assert hasattr(auth, 'bearer_token')
        assert hasattr(auth, 'token_expiration_time')
