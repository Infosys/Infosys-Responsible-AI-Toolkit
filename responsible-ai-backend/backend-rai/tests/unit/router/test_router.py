"""
Unit tests for router endpoints
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from datetime import datetime


class TestRouterHelperFunctions:
    """Tests for router helper functions"""

    @patch('rai_backend.router.router.requests.post')
    def test_send_telemetry_request_success(self, mock_post):
        """Test send_telemetry_request with successful request"""
        from rai_backend.router.router import send_telemetry_request
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response
        
        request = {"tenant": "test", "apiname": "test_api"}
        send_telemetry_request(request, id="123")
        
        mock_post.assert_called_once()

    @patch('rai_backend.router.router.requests.post')
    def test_send_telemetry_request_exception(self, mock_post):
        """Test send_telemetry_request with exception"""
        from rai_backend.router.router import send_telemetry_request
        
        mock_post.side_effect = Exception("Connection error")
        
        request = {"tenant": "test", "apiname": "test_api"}
        # Should not raise exception, just print error
        send_telemetry_request(request)

    @patch('rai_backend.router.router.requests.post')
    def test_send_telemetry_request_register_success(self, mock_post):
        """Test send_telemetry_request_register with successful request"""
        from rai_backend.router.router import send_telemetry_request_register
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response
        
        request = {"tenant": "test", "apiname": "register"}
        send_telemetry_request_register(request)
        
        mock_post.assert_called_once()

    @patch('rai_backend.router.router.requests.post')
    def test_send_telemetry_request_register_raf_success(self, mock_post):
        """Test send_telemetry_request_register_raf with successful request"""
        from rai_backend.router.router import send_telemetry_request_register_raf
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response
        
        request = {"events": []}
        send_telemetry_request_register_raf(request)
        
        mock_post.assert_called_once()


class TestTokenRequired:
    """Tests for token_required decorator"""

    @patch('rai_backend.router.router.AuthService')
    def test_token_required_valid_token(self, mock_auth_service):
        """Test token_required with valid authorization header"""
        from rai_backend.router.router import token_required
        from fastapi import Request
        
        mock_auth_service.accountService.return_value = {'id': 1, 'login': 'testuser'}
        
        @token_required
        def test_func(request: Request):
            return "success"
        
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "Bearer valid_token"
        
        result = test_func(mock_request)
        
        assert result == {'id': 1, 'login': 'testuser'}

    def test_token_required_no_authorization_header(self):
        """Test token_required without authorization header"""
        from rai_backend.router.router import token_required
        from fastapi import Request
        
        @token_required
        def test_func(request: Request):
            return "success"
        
        mock_request = MagicMock()
        mock_request.headers.get.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            test_func(mock_request)
        
        assert exc_info.value.status_code == 401

    def test_token_required_invalid_bearer_format(self):
        """Test token_required with invalid bearer format"""
        from rai_backend.router.router import token_required
        from fastapi import Request
        
        @token_required
        def test_func(request: Request):
            return "success"
        
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "InvalidFormat token"
        
        with pytest.raises(HTTPException) as exc_info:
            test_func(mock_request)
        
        assert exc_info.value.status_code == 401

    @patch('rai_backend.router.router.AuthService')
    def test_token_required_null_token(self, mock_auth_service):
        """Test token_required with null token"""
        from rai_backend.router.router import token_required
        from fastapi import Request
        
        @token_required
        def test_func(request: Request):
            return "success"
        
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "Bearer null"
        
        with pytest.raises(HTTPException) as exc_info:
            test_func(mock_request)
        
        assert exc_info.value.status_code == 401

    @patch('rai_backend.router.router.AuthService')
    def test_token_required_account_service_returns_none(self, mock_auth_service):
        """Test token_required when accountService returns None"""
        from rai_backend.router.router import token_required
        from fastapi import Request
        
        mock_auth_service.accountService.return_value = None
        
        @token_required
        def test_func(request: Request):
            return "success"
        
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "Bearer valid_token"
        
        with pytest.raises(HTTPException) as exc_info:
            test_func(mock_request)
        
        assert exc_info.value.status_code == 401


class TestRouterExceptions:
    """Tests for custom exceptions"""

    def test_no_valid_user_exception(self):
        """Test NoValidUser exception"""
        from rai_backend.router.router import NoValidUser
        
        with pytest.raises(NoValidUser):
            raise NoValidUser("User not found")

    def test_incorrect_password_exception(self):
        """Test IncorrectPassword exception"""
        from rai_backend.router.router import IncorrectPassword
        
        with pytest.raises(IncorrectPassword):
            raise IncorrectPassword("Incorrect password")

    def test_user_not_activated_exception(self):
        """Test UserNotActivated exception"""
        from rai_backend.router.router import UserNotActivated
        
        with pytest.raises(UserNotActivated):
            raise UserNotActivated("User not activated")

    def test_internal_server_error_exception(self):
        """Test InternalServerError exception"""
        from rai_backend.router.router import InternalServerError
        
        with pytest.raises(InternalServerError):
            raise InternalServerError("Internal server error")

    def test_user_already_exists_exception(self):
        """Test UserAlreadyExists exception"""
        from rai_backend.router.router import UserAlreadyExists
        
        with pytest.raises(UserAlreadyExists):
            raise UserAlreadyExists("User already exists")
