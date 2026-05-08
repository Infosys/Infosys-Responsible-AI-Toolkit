"""
Unit tests for Userdb DAO layer
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime
import datetime as dt


class TestUserDb:
    """Tests for UserDb class"""

    @patch('rai_backend.dao.Userdb.UserDb.mycol')
    def test_find_one_success(self, mock_collection):
        """Test findOne with existing user"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_user = {
            'id': 1,
            'login': 'testuser',
            'email': 'test@infosys.com'
        }
        mock_collection.find_one.return_value = mock_user
        
        result = UserDb.findOne(1)
        
        assert result == mock_user
        mock_collection.find_one.assert_called_once_with({'id': 1}, {'_id': 0})

    @patch('rai_backend.dao.Userdb.UserDb.mycol')
    def test_find_one_not_found(self, mock_collection):
        """Test findOne with non-existent user"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_collection.find_one.return_value = None
        
        result = UserDb.findOne(999)
        
        assert result == 'No users Found'

    @patch('rai_backend.dao.Userdb.UserDb.mycol')
    def test_find_all_success(self, mock_collection):
        """Test findAll returns user list"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_users = [
            {
                'id': 1,
                'login': 'user1',
                'activated': True,
                'createdBy': 'system',
                'createdDate': '2023-06-07T10:56:15.657+00:00',
                'firstName': 'User One',
                'lastModifiedBy': 'system',
                'lastModifiedDate': '2023-06-07T10:56:15.657+00:00',
                'authorities': ['ROLE_USER']
            }
        ]
        mock_collection.find.return_value = mock_users
        
        result = UserDb.findAll()
        
        assert result is not None
        mock_collection.find.assert_called_once_with({}, {'_id': 0})

    @patch('rai_backend.dao.Userdb.UserDb.mycol')
    def test_find_all_empty(self, mock_collection):
        """Test findAll with no users"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_collection.find.return_value = []
        
        result = UserDb.findAll()
        
        assert result is not None

    @patch('rai_backend.dao.Userdb.generate_password_hash')
    @patch('rai_backend.dao.Userdb.UserDb.myuserauth')
    @patch('rai_backend.dao.Userdb.UserDb.myCount')
    @patch('rai_backend.dao.Userdb.UserDb.mycol')
    @patch('rai_backend.dao.Userdb.DB')
    def test_create_new_user_success(self, mock_db, mock_collection, 
                                     mock_count, mock_userauth, mock_hash):
        """Test creating a new user successfully"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_hash.return_value = 'hashed_password'
        mock_collection.find_one.return_value = None
        mock_count.find_one.return_value = {'counter': 5}
        mock_collection.aggregate.return_value = [{'max_id': 2}]
        mock_collection.insert_one.return_value = MagicMock(inserted_id='123')
        
        new_user = {
            'email': 'new@infosys.com',
            'login': 'newuser',
            'cred': 'Password@123',
            'langKey': 'en'
        }
        
        result = UserDb.create(new_user)
        
        assert result is True
        mock_collection.insert_one.assert_called_once()

    @patch('rai_backend.dao.Userdb.UserDb.mycol')
    @patch('rai_backend.dao.Userdb.DB')
    def test_create_existing_user(self, mock_db, mock_collection):
        """Test creating a user that already exists"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_collection.find_one.return_value = {'login': 'existing'}
        
        new_user = {
            'email': 'existing@infosys.com',
            'login': 'existing',
            'cred': 'Password@123',
            'langKey': 'en'
        }
        
        result = UserDb.create(new_user)
        
        assert result is False

    @patch('rai_backend.dao.Userdb.UserDb.myuserauth')
    @patch('rai_backend.dao.Userdb.UserDb.mycol')
    def test_update_user_success(self, mock_collection, mock_userauth):
        """Test updating a user successfully"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_collection.find_one.return_value = {'id': 1, 'login': 'user1'}
        mock_collection.update_one.return_value = MagicMock(modified_count=1)
        mock_userauth.UserAuthRel = MagicMock()
        
        user_data = {
            'activated': True,
            'authorities': ['ROLE_ADMIN']
        }
        
        result = UserDb.update(1, user_data)
        
        assert result['status_code'] == 200
        assert 'successfully' in result['message']

    @patch('rai_backend.dao.Userdb.UserDb.myuserauth')
    @patch('rai_backend.dao.Userdb.UserDb.mycol')
    def test_delete_user_success(self, mock_collection, mock_userauth):
        """Test deleting a user successfully"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_userauth.UserAuthRel = MagicMock()
        
        result = UserDb.delete(1)
        
        mock_collection.delete_one.assert_called_once_with({'id': 1})
        assert result[1] == 204

    @patch('rai_backend.dao.Userdb.UserDb.myAuth')
    def test_get_all_authority_success(self, mock_auth):
        """Test getting all authorities"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_auth.distinct.return_value = ['ROLE_ADMIN', 'ROLE_USER', 'ROLE_ML']
        
        result = UserDb.getAllAuthority()
        
        assert len(result) == 3
        assert 'ROLE_ADMIN' in result

    @patch('rai_backend.dao.Userdb.UserDb.myAuth')
    def test_get_all_authority_empty(self, mock_auth):
        """Test getting all authorities when none exist"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_auth.distinct.return_value = []
        
        result = UserDb.getAllAuthority()
        
        assert result == ''

    @patch('rai_backend.dao.Userdb.UserDb.mycol')
    def test_get_user_by_name_success(self, mock_collection):
        """Test getting user by login name"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_user = {
            'id': 1,
            'login': 'testuser',
            'activated': True,
            'createdBy': 'system',
            'createdDate': '2023-06-07T10:56:15.657+00:00',
            'firstName': 'Test',
            'lastModifiedBy': 'system',
            'lastModifiedDate': '2023-06-07T10:56:15.657+00:00',
            'authorities': ['ROLE_USER']
        }
        mock_collection.find_one.return_value = mock_user
        
        result = UserDb.getUserByName('testuser')
        
        assert result is not None
        assert result['login'] == 'testuser'

    @patch('rai_backend.dao.Userdb.UserDb.mycol')
    def test_get_user_by_name_not_found(self, mock_collection):
        """Test getting user by name when not found"""
        from rai_backend.dao.Userdb import UserDb
        from fastapi import HTTPException
        
        mock_collection.find_one.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            UserDb.getUserByName('nonexistent')
        
        assert exc_info.value.status_code == 401

    @patch('rai_backend.dao.Userdb.generate_password_hash')
    @patch('rai_backend.dao.Userdb.UserDb.myCount')
    @patch('rai_backend.dao.Userdb.UserDb.myuserauth')
    @patch('rai_backend.dao.Userdb.UserDb.myAuth')
    @patch('rai_backend.dao.Userdb.UserDb.mycol')
    def test_add_initial_data(self, mock_collection, mock_auth, 
                              mock_userauth, mock_count, mock_hash):
        """Test adding initial data to database"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_auth.find.return_value = []
        mock_collection.find.return_value = []
        mock_count.find.return_value = []
        mock_hash.return_value = 'hashed_password'
        
        with patch.dict('os.environ', {
            'ADMIN_PASSWORD': 'admin123',
            'USER_PASSWORD': 'user123'
        }):
            UserDb.add_initial_data()
        
        # Verify authorities were inserted
        assert mock_auth.insert_many.called
        # Verify users were inserted
        assert mock_collection.insert_many.called
        # Verify user limit was set
        assert mock_count.insert_one.called

    @patch('rai_backend.dao.Userdb.UserDb.myuserauth')
    @patch('rai_backend.dao.Userdb.UserDb.mycol')
    def test_update_new_user_role_success(self, mock_collection, mock_userauth):
        """Test updating user role"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_user = {
            'id': 1,
            'login': 'testuser',
            'authorities': ['ROLE_USER']
        }
        mock_collection.find_one.return_value = mock_user
        mock_collection.update_one.return_value = MagicMock(acknowledged=True)
        
        result = UserDb.update_newUser_role('testuser', ['ROLE_ADMIN'])
        
        assert result is True

    @patch('rai_backend.dao.Userdb.UserDb.myAuth')
    def test_new_authority_success(self, mock_auth):
        """Test creating new authority"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_auth.find_one.return_value = None
        mock_auth.insert_one.return_value = MagicMock(inserted_id='123')
        
        result = UserDb.newAuthority('ROLE_NEW')
        
        assert result['status_code'] == 200
        assert 'successfully' in result['message']

    @patch('rai_backend.dao.Userdb.UserDb.myAuth')
    def test_new_authority_already_exists(self, mock_auth):
        """Test creating authority that already exists"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_auth.find_one.return_value = {'name': 'ROLE_ADMIN'}
        
        result = UserDb.newAuthority('ROLE_ADMIN')
        
        assert result['status_code'] == 500
        assert 'already exists' in result['message']

    @patch('rai_backend.dao.Userdb.UserDb.myConsent')
    def test_set_user_consent_new(self, mock_consent):
        """Test setting user consent for new user"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_consent.find_one.return_value = None
        
        result = UserDb.set_user_consent('testuser', True)
        
        assert result['status_code'] == 200
        mock_consent.insert_one.assert_called_once()

    @patch('rai_backend.dao.Userdb.UserDb.myConsent')
    def test_set_user_consent_existing(self, mock_consent):
        """Test updating user consent for existing user"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_consent.find_one.return_value = {'userId': 'testuser', 'userConsentStatus': False}
        
        result = UserDb.set_user_consent('testuser', True)
        
        assert result['status_code'] == 200
        mock_consent.update_one.assert_called_once()

    @patch('rai_backend.dao.Userdb.UserDb.myConsent')
    def test_get_user_consent_exists(self, mock_consent):
        """Test getting user consent when it exists"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_consent.find_one.return_value = {'userConsentStatus': True}
        
        result = UserDb.get_user_consent('testuser')
        
        assert result is True

    @patch('rai_backend.dao.Userdb.UserDb.myConsent')
    def test_get_user_consent_not_exists(self, mock_consent):
        """Test getting user consent when it doesn't exist"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_consent.find_one.return_value = None
        
        result = UserDb.get_user_consent('testuser')
        
        assert result is False

    @patch('rai_backend.dao.Userdb.generate_password_hash')
    @patch('rai_backend.dao.Userdb.UserDb.mycol')
    def test_reset_password_success(self, mock_collection, mock_hash):
        """Test resetting password successfully"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_user = {
            'login': 'testuser',
            'email': 'test@infosys.com'
        }
        mock_collection.find_one.return_value = mock_user
        mock_hash.return_value = 'new_hashed_password'
        mock_collection.update_one.return_value = MagicMock(modified_count=1)
        
        result = UserDb.reset_password('testuser', 'test@infosys.com', 'NewPass@123')
        
        assert result['status_code'] == 200
        assert 'successfully' in result['message']

    @patch('rai_backend.dao.Userdb.UserDb.mycol')
    def test_reset_password_user_not_found(self, mock_collection):
        """Test resetting password for non-existent user"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_collection.find_one.return_value = None
        
        result = UserDb.reset_password('nonexistent', 'wrong@email.com', 'NewPass@123')
        
        assert result['status_code'] == 404
        assert 'not found' in result['message'].lower()

    @patch('rai_backend.dao.Userdb.generate_password_hash')
    @patch('rai_backend.dao.Userdb.UserDb.mycol')
    def test_reset_password_no_modification(self, mock_collection, mock_hash):
        """Test reset password when no document is modified"""
        from rai_backend.dao.Userdb import UserDb
        
        mock_user = {
            'login': 'testuser',
            'email': 'test@infosys.com'
        }
        mock_collection.find_one.return_value = mock_user
        mock_hash.return_value = 'new_hashed_password'
        mock_collection.update_one.return_value = MagicMock(modified_count=0)
        
        result = UserDb.reset_password('testuser', 'test@infosys.com', 'NewPass@123')
        
        assert result['status_code'] == 400
