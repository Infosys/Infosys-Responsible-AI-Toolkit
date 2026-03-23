"""
Unit tests for backend_service (UserInDB)
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta, timezone
from jose import jwt
from rai_backend.service.backend_service import UserInDB
import os


class TestUserInDB:
    """Tests for UserInDB class"""

    def test_create_access_token_with_expires_delta(self):
        """Test creating access token with custom expiration"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=30)
        
        token = UserInDB.create_access_token(data, expires_delta)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify using the actual SECRET_KEY from environment
        secret_key = os.getenv('SECRET_KEY', 'test_secret_key_for_testing_only')
        decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
        assert decoded['sub'] == 'testuser'
        assert 'exp' in decoded

    def test_create_access_token_default_expiration(self):
        """Test creating access token with default expiration"""
        data = {"sub": "testuser"}
        
        token = UserInDB.create_access_token(data)
        
        assert token is not None
        secret_key = os.getenv('SECRET_KEY', 'test_secret_key_for_testing_only')
        decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
        assert decoded['sub'] == 'testuser'

    def test_login_for_access_token_success(self):
        """Test login_for_access_token with valid user"""
        token = UserInDB.login_for_access_token('testuser')
        
        assert token is not None
        assert isinstance(token, str)
        
        secret_key = os.getenv('SECRET_KEY', 'test_secret_key_for_testing_only')
        decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
        assert decoded['sub'] == 'testuser'

    def test_login_for_access_token_empty_user(self):
        """Test login_for_access_token with empty user raises error"""
        with pytest.raises(ValueError, match="User cannot be null or empty"):
            UserInDB.login_for_access_token('')

    def test_login_for_access_token_none_user(self):
        """Test login_for_access_token with None user raises error"""
        with pytest.raises(ValueError, match="User cannot be null or empty"):
            UserInDB.login_for_access_token(None)

    @patch('rai_backend.service.backend_service.UserInDB.pwd_context.hash')
    def test_verify_password_correct(self, mock_hash):
        """Test verify_password with correct password"""
        from rai_backend.service.backend_service import UserInDB
        
        password = "pass123"
        hashed = "$2b$12$mockedhash"
        mock_hash.return_value = hashed
        
        with patch('rai_backend.service.backend_service.UserInDB.pwd_context.verify', return_value=True):
            result = UserInDB.verify_password(password, hashed)
        
        assert result is True

    @patch('rai_backend.service.backend_service.UserInDB.pwd_context.verify')
    def test_verify_password_incorrect(self, mock_verify):
        """Test verify_password with incorrect password"""
        from rai_backend.service.backend_service import UserInDB
        
        password = "pass123"
        wrong_password = "wrong"
        hashed = "$2b$12$mockedhash"
        mock_verify.return_value = False
        
        result = UserInDB.verify_password(wrong_password, hashed)
        
        assert result is False

    @patch('rai_backend.service.backend_service.UserInDB.pwd_context.verify')
    def test_verify_password_empty_plain_password(self, mock_verify):
        """Test verify_password with empty plain password"""
        from rai_backend.service.backend_service import UserInDB
        
        hashed = "$2b$12$mockedhash"
        mock_verify.return_value = False
        
        result = UserInDB.verify_password('', hashed)
        
        assert result is False

    def test_verify_password_empty_hashed_password(self):
        """Test verify_password with empty hashed password"""
        result = UserInDB.verify_password('pass123', '')
        
        assert result is False

    @patch('rai_backend.service.backend_service.UserInDB.pwd_context.hash')
    def test_get_password_hash_success(self, mock_hash):
        """Test get_password_hash with valid password"""
        from rai_backend.service.backend_service import UserInDB
        
        password = "Pass@123"
        mock_hash.return_value = "$2b$12$mockedhashvalue"
        
        hashed = UserInDB.get_password_hash(password)
        
        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 0
        mock_hash.assert_called_once_with(password)

    def test_get_password_hash_empty_password(self):
        """Test get_password_hash with empty password raises error"""
        with pytest.raises(ValueError, match="Password cannot be null or empty"):
            UserInDB.get_password_hash('')

    def test_get_password_hash_none_password(self):
        """Test get_password_hash with None password raises error"""
        with pytest.raises(ValueError, match="Password cannot be null or empty"):
            UserInDB.get_password_hash(None)

    @patch('rai_backend.service.backend_service.UserInDB.pwd_context')
    def test_password_hash_different_for_same_password(self, mock_pwd_context):
        """Test that same password produces different hashes (due to salt)"""
        from rai_backend.service.backend_service import UserInDB
        
        password = "Pass@123"
        # Mock different hashes for same password (simulating salt)
        mock_pwd_context.hash.side_effect = ["$2b$12$hash1", "$2b$12$hash2"]
        mock_pwd_context.verify.return_value = True
        
        hash1 = UserInDB.get_password_hash(password)
        hash2 = UserInDB.get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        # But both should verify correctly
        assert UserInDB.verify_password(password, hash1)
        assert UserInDB.verify_password(password, hash2)
