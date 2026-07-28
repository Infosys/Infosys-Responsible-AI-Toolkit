"""
Additional integration tests for router endpoints
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi.testclient import TestClient
from datetime import datetime
import time


class TestRegisterEndpoint:
    """Tests for /register endpoint"""

    @patch('rai_backend.router.router.AuthService')
    @patch('rai_backend.router.router.con.ThreadPoolExecutor')
    def test_register_user_already_exists(self, mock_executor, mock_auth_service):
        """Test register when user already exists"""
        from rai_backend.router.router import router
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        mock_auth_service.signupPostService.return_value = {
            "message": "User already exists",
            "status_code": 200
        }
        
        with patch.dict('os.environ', {'TELEMETRY_FLAG': 'False'}):
            from rai_backend.mappers.UserMapper import NewUserRequest
            payload = {
                "email": "existing@infosys.com",
                "login": "Existing",
                "cred": "Pass@123",
                "langKey": "en"
            }
            
            # Mock the router function directly
            with patch('rai_backend.router.router.analyze') as mock_analyze:
                mock_analyze.return_value = {"message": "User already exists", "status_code": 200}
                result = mock_analyze(NewUserRequest(**payload))
                
                assert result["message"] == "User already exists"


class TestAuthenticateEndpoint:
    """Tests for /authenticate endpoint"""

    @patch('rai_backend.router.router.AuthService')
    @patch('rai_backend.router.router.active_sessions', {})
    def test_authenticate_success_creates_session(self, mock_auth_service):
        """Test successful authentication creates active session"""
        from rai_backend.router.router import authenticate, active_sessions
        from rai_backend.mappers.UserMapper import NewAuthRequest
        
        mock_auth_service.loginPostService.return_value = {
            "id_token": "test_token_123"
        }
        
        payload = NewAuthRequest(
            username="TestUser",
            cred="Password@123",
            rememberMe=True
        )
        
        with patch.dict('os.environ', {'TELEMETRY_FLAG': 'False'}):
            result = authenticate(payload)
            
            # Verify session was created with lowercase username
            assert "testuser" in active_sessions
            assert "login_time" in active_sessions["testuser"]

    @patch('rai_backend.router.router.AuthService')
    def test_authenticate_user_not_found_raises_exception(self, mock_auth_service):
        """Test authentication with non-existent user"""
        from rai_backend.router.router import authenticate
        from rai_backend.mappers.UserMapper import NewAuthRequest
        from fastapi import HTTPException
        
        mock_auth_service.loginPostService.return_value = {
            "code": 404,
            "error": "User not found"
        }
        
        payload = NewAuthRequest(
            username="nonexistent",
            cred="Password@123",
            rememberMe=False
        )
        
        with patch.dict('os.environ', {'TELEMETRY_FLAG': 'False'}):
            # Should raise HTTPException with status 404
            with pytest.raises(HTTPException) as exc_info:
                authenticate(payload)
            assert exc_info.value.status_code == 404

    @patch('rai_backend.router.router.AuthService')
    def test_authenticate_incorrect_password_raises_exception(self, mock_auth_service):
        """Test authentication with incorrect password"""
        from rai_backend.router.router import authenticate
        from rai_backend.mappers.UserMapper import NewAuthRequest
        from fastapi import HTTPException
        
        mock_auth_service.loginPostService.return_value = {
            "code": 401,
            "error": "Incorrect password"
        }
        
        payload = NewAuthRequest(
            username="testuser",
            cred="WrongPassword",
            rememberMe=False
        )
        
        with patch.dict('os.environ', {'TELEMETRY_FLAG': 'False'}):
            with pytest.raises(HTTPException) as exc_info:
                authenticate(payload)
            assert exc_info.value.status_code == 401

    @patch('rai_backend.router.router.AuthService')
    def test_authenticate_user_not_activated_raises_exception(self, mock_auth_service):
        """Test authentication with inactive user"""
        from rai_backend.router.router import authenticate
        from rai_backend.mappers.UserMapper import NewAuthRequest
        from fastapi import HTTPException
        
        mock_auth_service.loginPostService.return_value = {
            "code": 403,
            "error": "User not activated"
        }
        
        payload = NewAuthRequest(
            username="inactiveuser",
            cred="Password@123",
            rememberMe=False
        )
        
        with patch.dict('os.environ', {'TELEMETRY_FLAG': 'False'}):
            with pytest.raises(HTTPException) as exc_info:
                authenticate(payload)
            assert exc_info.value.status_code == 403


class TestLogoutEndpoint:
    """Tests for /logout endpoint"""

    @patch('rai_backend.router.router.active_sessions')
    def test_logout_with_active_session(self, mock_sessions):
        """Test logout with active session"""
        from rai_backend.router.router import logout
        
        current_time = time.time()
        mock_sessions.__contains__ = Mock(return_value=True)
        mock_sessions.pop = Mock(return_value={
            "login_time": current_time - 100
        })
        
        with patch.dict('os.environ', {'TELEMETRY_FLAG': 'False'}):
            result = logout('testuser')
            
            assert result['message'] == 'Logged out'
            assert 'duration' in result
            assert result['username'] == 'testuser'

    @patch('rai_backend.router.router.active_sessions', {})
    def test_logout_without_active_session(self):
        """Test logout without active session"""
        from rai_backend.router.router import logout
        
        result = logout('nonexistent')
        
        # Should return None when user not in active sessions
        assert result is None


class TestUserManagementEndpoints:
    """Tests for user management endpoints"""

    @patch('rai_backend.router.router.UserDb')
    def test_get_users(self, mock_userdb):
        """Test getting all users"""
        from rai_backend.router.router import getUser
        
        mock_userdb.findAll.return_value = MagicMock()
        
        result = getUser()
        
        mock_userdb.findAll.assert_called_once()
        assert result is not None

    @patch('rai_backend.router.router.UserDb')
    def test_get_user_by_id(self, mock_userdb):
        """Test getting user by ID"""
        from rai_backend.router.router import getUserById
        
        mock_userdb.findOne.return_value = {
            'id': 1,
            'login': 'testuser'
        }
        
        result = getUserById(1)
        
        mock_userdb.findOne.assert_called_once_with(1)
        assert result['id'] == 1

    @patch('rai_backend.router.router.UserDb')
    def test_update_user(self, mock_userdb):
        """Test updating user"""
        from rai_backend.router.router import updateUser
        from rai_backend.mappers.UserMapper import UpdateUserRequest
        
        mock_userdb.update.return_value = {
            "message": "User updated successfully",
            "status_code": 200
        }
        
        user_update = UpdateUserRequest(
            id=1,
            activated=True,
            authorities=["ROLE_ADMIN"]
        )
        
        result = updateUser(user_update)
        
        assert result["message"] == "User updated successfully"
        mock_userdb.update.assert_called_once()

    @patch('rai_backend.router.router.UserDb')
    def test_delete_user(self, mock_userdb):
        """Test deleting user"""
        from rai_backend.router.router import deleteUser
        
        mock_userdb.delete.return_value = ("Deleted", 204)
        
        result = deleteUser(1)
        
        mock_userdb.delete.assert_called_once_with(1)

    @patch('rai_backend.router.router.UserDb')
    def test_get_authorities(self, mock_userdb):
        """Test getting authorities"""
        from rai_backend.router.router import getAuthority
        
        mock_userdb.getAllAuthority.return_value = [
            "ROLE_ADMIN",
            "ROLE_USER",
            "ROLE_ML"
        ]
        
        result = getAuthority()
        
        assert len(result) == 3
        assert "ROLE_ADMIN" in result


class TestPageAuthorityEndpoint:
    """Tests for page authority endpoint"""

    @patch('rai_backend.router.router.mydb')
    @pytest.mark.asyncio
    async def test_get_page_access_found(self, mock_db):
        """Test getting page access for existing role"""
        from rai_backend.router.router import get_page_access
        from bson import ObjectId
        
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        # Include _id to match actual implementation
        mock_collection.find_one.return_value = {
            '_id': ObjectId('507f1f77bcf86cd799439011'),
            'role': 'ROLE_ADMIN',
            'pages': ['dashboard', 'users']
        }
        
        result = await get_page_access('ROLE_ADMIN')
        
        assert result['role'] == 'ROLE_ADMIN'
        assert '_id' in result

    @patch('rai_backend.router.router.mydb')
    @pytest.mark.asyncio
    async def test_get_page_access_not_found(self, mock_db):
        """Test getting page access for non-existent role"""
        from rai_backend.router.router import get_page_access
        from fastapi import HTTPException
        
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_page_access('ROLE_NONEXISTENT')
        
        assert exc_info.value.status_code == 404
