"""
Unit tests for UserMapper models
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from rai_backend.mappers.UserMapper import (
    NewUserRequest,
    NewAuthRequest,
    UpdateUserRequest,
    UserData,
    UserDataResponse,
    flagCreation,
    getData,
    CreationStatus,
    AllDataResponse,
    flagUpdate,
    newRoleUpdRqst,
    newRoleCreate,
    UserConsentCreate,
    PasswordResetRequest,
    PasswordResetResponse
)


class TestNewUserRequest:
    """Tests for NewUserRequest model"""
    
    def test_valid_new_user_request(self):
        """Test creating a valid NewUserRequest"""
        user_request = NewUserRequest(
            email="test@infosys.com",
            login="testuser",
            cred="Abc@123",
            langKey="en"
        )
        assert user_request.email == "test@infosys.com"
        assert user_request.login == "testuser"
        assert user_request.cred == "Abc@123"
        assert user_request.langKey == "en"
    
    def test_new_user_request_with_defaults(self):
        """Test NewUserRequest with example defaults"""
        user_request = NewUserRequest(
            email="abc@infosys.com",
            login="abc",
            cred="Abc@123",
            langKey="en"
        )
        assert user_request.email == "abc@infosys.com"


class TestNewAuthRequest:
    """Tests for NewAuthRequest model"""
    
    def test_valid_auth_request(self):
        """Test creating a valid NewAuthRequest"""
        auth_request = NewAuthRequest(
            username="test@infosys.com",
            cred="Abc@123",
            rememberMe=True
        )
        assert auth_request.username == "test@infosys.com"
        assert auth_request.cred == "Abc@123"
        assert auth_request.rememberMe is True
    
    def test_auth_request_remember_me_false(self):
        """Test auth request with rememberMe=False"""
        auth_request = NewAuthRequest(
            username="user@test.com",
            cred="Password@1",
            rememberMe=False
        )
        assert auth_request.rememberMe is False


class TestUpdateUserRequest:
    """Tests for UpdateUserRequest model"""
    
    def test_valid_update_user_request(self):
        """Test creating a valid UpdateUserRequest"""
        update_request = UpdateUserRequest(
            activated=True,
            authorities=["ROLE_ML"],
            id=3
        )
        assert update_request.activated is True
        assert update_request.authorities == ["ROLE_ML"]
        assert update_request.id == 3
    
    def test_update_user_request_multiple_authorities(self):
        """Test update request with multiple authorities"""
        update_request = UpdateUserRequest(
            activated=False,
            authorities=["ROLE_ADMIN", "ROLE_USER", "ROLE_ML"],
            id=5
        )
        assert len(update_request.authorities) == 3


class TestUserData:
    """Tests for UserData model"""
    
    def test_valid_user_data(self):
        """Test creating valid UserData"""
        user_data = UserData(
            activated=True,
            authorities=["ROLE_ML"],
            createdBy="system",
            createdDate="2023-06-07T10:56:15.657+00:00",
            firstName="abc@infosys.com",
            id=3,
            lastModifiedBy="system",
            lastModifiedDate="2023-06-07T10:56:15.657+00:00",
            login="abc"
        )
        assert user_data.activated is True
        assert user_data.id == 3
        assert user_data.login == "abc"
    
    def test_user_data_multiple_authorities(self):
        """Test UserData with multiple authorities"""
        user_data = UserData(
            activated=True,
            authorities=["ROLE_ADMIN", "ROLE_USER"],
            createdBy="admin",
            createdDate="2023-06-07T10:56:15.657+00:00",
            firstName="Test User",
            id=1,
            lastModifiedBy="admin",
            lastModifiedDate="2023-06-07T10:56:15.657+00:00",
            login="testuser"
        )
        assert len(user_data.authorities) == 2


class TestUserDataResponse:
    """Tests for UserDataResponse model"""
    
    def test_user_data_response_with_list(self):
        """Test UserDataResponse with list of users"""
        user1 = UserData(
            activated=True,
            authorities=["ROLE_ML"],
            createdBy="system",
            createdDate="2023-06-07T10:56:15.657+00:00",
            firstName="User1",
            id=1,
            lastModifiedBy="system",
            lastModifiedDate="2023-06-07T10:56:15.657+00:00",
            login="user1"
        )
        response = UserDataResponse(userList=[user1])
        assert len(response.userList) == 1
        assert response.userList[0].login == "user1"


class TestFlagCreation:
    """Tests for flagCreation model"""
    
    def test_valid_flag_creation(self):
        """Test creating a valid flag"""
        flag = flagCreation(Module="RaiBackend", TelemetryFlag=False)
        assert flag.Module == "RaiBackend"
        assert flag.TelemetryFlag is False
    
    def test_flag_creation_true(self):
        """Test flag creation with TelemetryFlag=True"""
        flag = flagCreation(Module="TestModule", TelemetryFlag=True)
        assert flag.TelemetryFlag is True


class TestGetData:
    """Tests for getData model"""
    
    def test_valid_get_data(self):
        """Test creating valid getData object"""
        data = getData(
            Module="RaiBackend",
            TelemetryFlag=False,
            CreatedDateTime="2023-06-07T10:56:15.657+00:00",
            LastUpdatedDateTime="2023-06-07T10:56:15.657+00:00"
        )
        assert data.Module == "RaiBackend"
        assert data.TelemetryFlag is False


class TestCreationStatus:
    """Tests for CreationStatus model"""
    
    def test_creation_status_success(self):
        """Test CreationStatus with success status"""
        status = CreationStatus(status="success")
        assert status.status == "success"
    
    def test_creation_status_failure(self):
        """Test CreationStatus with failure status"""
        status = CreationStatus(status="failure")
        assert status.status == "failure"


class TestFlagUpdate:
    """Tests for flagUpdate model"""
    
    def test_valid_flag_update(self):
        """Test creating a valid flag update"""
        flag = flagUpdate(Module="RaiBackend", TelemetryFlag=True)
        assert flag.Module == "RaiBackend"
        assert flag.TelemetryFlag is True


class TestNewRoleUpdRqst:
    """Tests for newRoleUpdRqst model"""
    
    def test_valid_role_update_request(self):
        """Test creating a valid role update request"""
        role_request = newRoleUpdRqst(
            loginName="abc",
            role=["ROLE_ADMIN", "ROLE_USER"]
        )
        assert role_request.loginName == "abc"
        assert len(role_request.role) == 2


class TestNewRoleCreate:
    """Tests for newRoleCreate model"""
    
    def test_valid_role_create(self):
        """Test creating a valid role"""
        role = newRoleCreate(role="ROLE_ML")
        assert role.role == "ROLE_ML"


class TestUserConsentCreate:
    """Tests for UserConsentCreate model"""
    
    def test_valid_user_consent_true(self):
        """Test creating user consent with True status"""
        consent = UserConsentCreate(userId="abc", userConsentStatus=True)
        assert consent.userId == "abc"
        assert consent.userConsentStatus is True
    
    def test_valid_user_consent_false(self):
        """Test creating user consent with False status"""
        consent = UserConsentCreate(userId="xyz", userConsentStatus=False)
        assert consent.userConsentStatus is False


class TestPasswordResetRequest:
    """Tests for PasswordResetRequest model"""
    
    def test_valid_password_reset_request(self):
        """Test creating a valid password reset request"""
        reset_request = PasswordResetRequest(
            userId="abc",
            email="abc@infosys.com",
            newPassword="NewAbc@123"
        )
        assert reset_request.userId == "abc"
        assert reset_request.email == "abc@infosys.com"
        assert reset_request.newPassword == "NewAbc@123"


class TestPasswordResetResponse:
    """Tests for PasswordResetResponse model"""
    
    def test_valid_password_reset_response(self):
        """Test creating a valid password reset response"""
        reset_response = PasswordResetResponse(
            message="Password reset successfully",
            status_code=200
        )
        assert reset_response.message == "Password reset successfully"
        assert reset_response.status_code == 200
    
    def test_password_reset_response_error(self):
        """Test password reset response with error"""
        reset_response = PasswordResetResponse(
            message="User not found",
            status_code=404
        )
        assert reset_response.status_code == 404
