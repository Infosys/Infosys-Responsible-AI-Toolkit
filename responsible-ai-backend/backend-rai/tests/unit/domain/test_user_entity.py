"""
Tests for domain/userEntity module
"""
import pytest
from unittest.mock import Mock, MagicMock


class TestUserEntity:
    """Tests for User entity class"""

    def test_user_entity_creation(self):
        """Test creating User entity"""
        from rai_backend.domain.userEntity import User
        
        user = User(username="testuser")
        
        assert user.username == "testuser"

    def test_user_entity_is_authenticated(self):
        """Test user is_authenticated property"""
        from rai_backend.domain.userEntity import User
        
        user = User(username="testuser")
        
        # User should be authenticated by default
        assert user.is_authenticated() is True

    def test_user_entity_is_active(self):
        """Test user is_active property"""
        from rai_backend.domain.userEntity import User
        
        user = User(username="testuser")
        
        assert user.is_active() is True

    def test_user_entity_get_id(self):
        """Test user get_id method"""
        from rai_backend.domain.userEntity import User
        
        user = User(username="testuser")
        
        assert user.get_id() == "testuser"

    def test_user_entity_is_anonymous(self):
        """Test user is_anonymous property"""
        from rai_backend.domain.userEntity import User
        
        user = User(username="testuser")
        
        # User with username should not be anonymous
        assert user.is_anonymous() is False
