"""
Unit tests for authService
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from rai_backend.service.authService import AuthService


class TestAuthService:
    """Tests for AuthService class"""

    @patch('rai_backend.service.authService.UserDb')
    def test_account_service_success(self, mock_userdb):
        """Test accountService with valid username"""
        mock_userdb.getUserByName.return_value = {
            'id': 1,
            'login': 'testuser',
            'email': 'test@infosys.com',
            'activated': True
        }
        
        result = AuthService.accountService('testuser')
        
        assert result is not None
        assert result['login'] == 'testuser'
        mock_userdb.getUserByName.assert_called_once_with('testuser')

    @patch('rai_backend.service.authService.UserDb')
    def test_account_service_exception(self, mock_userdb):
        """Test accountService handles exceptions"""
        mock_userdb.getUserByName.side_effect = Exception("Database error")
        
        result = AuthService.accountService('testuser')
        
        assert result is None

    @patch('rai_backend.service.authService.check_password_hash')
    @patch('rai_backend.service.authService.UserInDB')
    @patch('rai_backend.service.authService.PageauthorityDbNew')
    @patch('rai_backend.service.authService.UserDb')
    @patch('rai_backend.service.authService.AuthService.mycol')
    def test_login_post_service_success(self, mock_collection, mock_userdb, mock_pageauth, 
                                       mock_userindb, mock_check_hash):
        """Test loginPostService with valid credentials"""
        # Setup mocks
        mock_user = {
            'login': 'testuser',
            'passwordHash': 'hashed_password',
            'activated': True
        }
        mock_collection.find_one.return_value = mock_user
        mock_check_hash.return_value = True
        mock_userindb.login_for_access_token.return_value = 'test_token'
        
        result = AuthService.loginPostService('testuser', 'password123')
        
        assert result == {"id_token": 'test_token'}
        mock_userdb.add_initial_data.assert_called_once()
        mock_pageauth.add_initial_data.assert_called_once()

    @patch('rai_backend.service.authService.AuthService.mycol')
    @patch('rai_backend.service.authService.PageauthorityDbNew')
    @patch('rai_backend.service.authService.UserDb')
    def test_login_post_service_user_not_found(self, mock_userdb, mock_pageauth, mock_collection):
        """Test loginPostService with non-existent user"""
        mock_collection.find_one.return_value = None
        
        result = AuthService.loginPostService('nonexistent', 'password')
        
        assert result == {"error": "User not found", "code": 404}

    @patch('rai_backend.service.authService.check_password_hash')
    @patch('rai_backend.service.authService.AuthService.mycol')
    @patch('rai_backend.service.authService.PageauthorityDbNew')
    @patch('rai_backend.service.authService.UserDb')
    def test_login_post_service_incorrect_password(self, mock_userdb, mock_pageauth, 
                                                   mock_collection, mock_check_hash):
        """Test loginPostService with incorrect password"""
        mock_user = {
            'login': 'testuser',
            'passwordHash': 'hashed_password',
            'activated': True
        }
        mock_collection.find_one.return_value = mock_user
        mock_check_hash.return_value = False
        
        result = AuthService.loginPostService('testuser', 'wrongpassword')
        
        assert result == {"error": "Incorrect password", "code": 401}
    @patch('rai_backend.service.authService.check_password_hash')
    @patch('rai_backend.service.authService.AuthService.mycol')
    @patch('rai_backend.service.authService.PageauthorityDbNew')
    @patch('rai_backend.service.authService.UserDb')
    def test_login_post_service_user_not_activated(self, mock_userdb, mock_pageauth,
                                                   mock_collection, mock_check_hash):
        """Test loginPostService with non-activated user"""
        mock_user = {
            'login': 'testuser',
            'passwordHash': 'hashed_password',
            'activated': False
        }
        mock_collection.find_one.return_value = mock_user
        mock_check_hash.return_value = True
        
        result = AuthService.loginPostService('testuser', 'password')
        
        assert result == {"error": "User not activated", "code": 403}
    @patch('rai_backend.service.authService.UserDb')
    @patch('rai_backend.service.authService.PageauthorityDbNew')
    def test_signup_post_service_success(self, mock_pageauth, mock_userdb):
        """Test signupPostService with valid user data"""
        mock_userdb.create.return_value = True
        
        new_user = {
            'email': 'newuser@infosys.com',
            'login': 'newuser',
            'cred': 'Password@123',
            'langKey': 'en'
        }
        
        result = AuthService.signupPostService(new_user)
        
        assert result == {"message": "User created successfully", "status_code": 200}
        mock_userdb.add_initial_data.assert_called_once()
        mock_pageauth.add_initial_data.assert_called_once()
        mock_userdb.create.assert_called_once_with(new_user)

    @patch('rai_backend.service.authService.UserDb')
    @patch('rai_backend.service.authService.PageauthorityDbNew')
    def test_signup_post_service_user_exists(self, mock_pageauth, mock_userdb):
        """Test signupPostService when user already exists"""
        mock_userdb.create.return_value = False
        
        new_user = {
            'email': 'existing@infosys.com',
            'login': 'existing',
            'cred': 'Password@123',
            'langKey': 'en'
        }
        
        result = AuthService.signupPostService(new_user)
        
        assert result == {"message": "User already exists", "status_code": 200}

    @patch('rai_backend.service.authService.UserDb')
    @patch('rai_backend.service.authService.PageauthorityDbNew')
    def test_signup_post_service_exception(self, mock_pageauth, mock_userdb):
        """Test signupPostService handles exceptions"""
        mock_userdb.create.side_effect = Exception("Database error")
        
        new_user = {'email': 'test@infosys.com', 'login': 'test', 'cred': 'Pass@123', 'langKey': 'en'}
        
        result = AuthService.signupPostService(new_user)
        
        assert result == {"message": "An error occurred", "status_code": 500}

    @patch('rai_backend.service.authService.UserDb')
    def test_new_user_role_success(self, mock_userdb):
        """Test newUserRole with valid data"""
        mock_userdb.update_newUser_role.return_value = {"status": "success"}
        
        result = AuthService.newUserRole('testuser', ['ROLE_ADMIN'])
        
        assert result == {"status": "success"}
        mock_userdb.update_newUser_role.assert_called_once_with('testuser', ['ROLE_ADMIN'])

    @patch('rai_backend.service.authService.UserDb')
    def test_new_user_role_exception(self, mock_userdb):
        """Test newUserRole handles exceptions"""
        mock_userdb.update_newUser_role.side_effect = Exception("Update error")
        
        result = AuthService.newUserRole('testuser', ['ROLE_ADMIN'])
        
        assert result is None

    @patch('rai_backend.service.authService.UserDb')
    def test_reset_count(self, mock_userdb):
        """Test resetCount method"""
        mock_userdb.myCount = MagicMock()
        
        AuthService.resetCount()
        
        mock_userdb.myCount.update_one.assert_called_once_with({}, {'$set': {'counter': 0}})

    @patch('rai_backend.service.authService.UserDb')
    def test_new_authority(self, mock_userdb):
        """Test newAuthority method"""
        mock_userdb.newAuthority.return_value = {"authority": "ROLE_ML"}
        
        result = AuthService.newAuthority('ROLE_ML')
        
        assert result == {"authority": "ROLE_ML"}
        mock_userdb.newAuthority.assert_called_once_with('ROLE_ML')

    @patch('rai_backend.service.authService.UserDb')
    def test_reset_password_service_success(self, mock_userdb):
        """Test resetPasswordService with valid data"""
        mock_userdb.reset_password.return_value = {
            "message": "Password reset successfully",
            "status_code": 200
        }
        
        result = AuthService.resetPasswordService('testuser', 'test@infosys.com', 'NewPass@123')
        
        assert result["message"] == "Password reset successfully"
        assert result["status_code"] == 200
        mock_userdb.reset_password.assert_called_once_with('testuser', 'test@infosys.com', 'NewPass@123')

    @patch('rai_backend.service.authService.UserDb')
    def test_reset_password_service_missing_fields(self, mock_userdb):
        """Test resetPasswordService with missing fields"""
        result = AuthService.resetPasswordService('', 'test@infosys.com', 'NewPass@123')
        
        assert result["status_code"] == 400
        assert "required" in result["message"].lower()

    @patch('rai_backend.service.authService.UserDb')
    def test_reset_password_service_exception(self, mock_userdb):
        """Test resetPasswordService handles exceptions"""
        mock_userdb.reset_password.side_effect = Exception("Database error")
        
        result = AuthService.resetPasswordService('testuser', 'test@infosys.com', 'NewPass@123')
        
        assert result["status_code"] == 500
        assert "error" in result["message"].lower()
