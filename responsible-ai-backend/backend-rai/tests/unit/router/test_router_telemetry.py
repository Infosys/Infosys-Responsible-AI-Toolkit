"""
Tests for router telemetry middleware and endpoints
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
import json


class TestRegisterTelemetryFlow:
    """Test registration endpoint with telemetry enabled"""

    @patch.dict('os.environ', {'TELEMETRY_FLAG': 'True'})
    @patch('rai_backend.router.router.AuthService')
    @patch('rai_backend.router.router.send_telemetry_request_register_raf')
    @patch('rai_backend.router.router.send_telemetry_request_register')
    @patch('rai_backend.router.router.con.ThreadPoolExecutor')
    def test_register_telemetry_user_created_successfully(
        self, mock_executor, mock_send_rai, mock_send_raf, mock_auth
    ):
        """Test registration with telemetry when user is created successfully"""
        from rai_backend.router.router import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Mock successful user creation
        mock_auth.signupPostService.return_value = {
            'message': 'User created successfully',
            'status_code': 200
        }
        
        # Mock executor context manager
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        
        response = client.post('/register', json={
            'email': 'test@example.com',
            'login': 'TestUser',
            'cred': 'Password@123',
            'langKey': 'en'
        })
        
        assert response.status_code == 200
        assert mock_executor_instance.submit.call_count == 2  # RAF + RAI telemetry

    @patch.dict('os.environ', {'TELEMETRY_FLAG': 'True'})
    @patch('rai_backend.router.router.AuthService')
    @patch('rai_backend.router.router.send_telemetry_request_register_raf')
    @patch('rai_backend.router.router.con.ThreadPoolExecutor')
    def test_register_telemetry_user_already_exists(
        self, mock_executor, mock_send_raf, mock_auth
    ):
        """Test registration with telemetry when user already exists"""
        from rai_backend.router.router import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Mock user already exists
        mock_auth.signupPostService.return_value = {
            'message': 'User already exists',
            'status_code': 200
        }
        
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        
        response = client.post('/register', json={
            'email': 'existing@example.com',
            'login': 'ExistingUser',
            'cred': 'Password@123',
            'langKey': 'en'
        })
        
        assert response.status_code == 200
        # Should return early, no RAF telemetry sent
        assert response.json()['message'] == 'User already exists'

    @patch.dict('os.environ', {'TELEMETRY_FLAG': 'False'})
    @patch('rai_backend.router.router.AuthService')
    def test_register_without_telemetry(self, mock_auth):
        """Test registration without telemetry flag"""
        from rai_backend.router.router import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        mock_auth.signupPostService.return_value = {
            'message': 'User created successfully',
            'status_code': 200
        }
        
        response = client.post('/register', json={
            'email': 'test@example.com',
            'login': 'TestUser',
            'cred': 'Password@123',
            'langKey': 'en'
        })
        
        assert response.status_code == 200

    @patch('rai_backend.router.router.AuthService')
    def test_register_internal_server_error(self, mock_auth):
        """Test registration when internal server error occurs"""
        from rai_backend.router.router import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        mock_auth.signupPostService.return_value = {
            'message': 'Error',
            'status_code': 500
        }
        
        response = client.post('/register', json={
            'email': 'test@example.com',
            'login': 'TestUser',
            'cred': 'Password@123',
            'langKey': 'en'
        })
        
        assert response.status_code == 500


class TestAuthenticateTelemetryFlow:
    """Test authentication endpoint with telemetry"""

    @patch.dict('os.environ', {'TELEMETRY_FLAG': 'True'})
    @patch('rai_backend.router.router.AuthService')
    @patch('rai_backend.router.router.send_telemetry_request_register_raf')
    @patch('rai_backend.router.router.send_telemetry_request')
    @patch('rai_backend.router.router.con.ThreadPoolExecutor')
    def test_authenticate_with_telemetry_success(
        self, mock_executor, mock_send_rai, mock_send_raf, mock_auth
    ):
        """Test authentication with telemetry enabled"""
        from rai_backend.router.router import router
        from fastapi import FastAPI
        from rai_backend.mappers.UserMapper import UserData
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Mock successful authentication - return AttributeDict
        class MockResponse(dict):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.__dict__ = self
        
        response_obj = MockResponse({
            'id_token': 'test-token',
            'message': 'Login successful',
            'code': 200
        })
        
        mock_auth.loginPostService.return_value = response_obj
        
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        
        response = client.post('/authenticate', json={
            'username': 'test@example.com',
            'cred': 'Password@123',
            'rememberMe': True
        })
        
        assert response.status_code == 200
        assert mock_executor_instance.submit.call_count == 2  # RAF + RAI telemetry

    @patch.dict('os.environ', {'TELEMETRY_FLAG': 'False'})
    @patch('rai_backend.router.router.AuthService')
    def test_authenticate_without_telemetry(self, mock_auth):
        """Test authentication without telemetry"""
        from rai_backend.router.router import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        class MockResponse(dict):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.__dict__ = self
        
        response_obj = MockResponse({
            'id_token': 'test-token',
            'message': 'Login successful',
            'code': 200
        })
        
        mock_auth.loginPostService.return_value = response_obj
        
        response = client.post('/authenticate', json={
            'username': 'test@example.com',
            'cred': 'Password@123',
            'rememberMe': True
        })
        
        assert response.status_code == 200


class TestPageAuthorityNewEndpoints:
    """Test page authority new endpoints"""

    @pytest.mark.asyncio
    @patch('rai_backend.router.router.mydb')
    async def test_get_page_access_new_success(self, mock_db):
        """Test getting page access successfully"""
        from rai_backend.router.router import get_page_access
        
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = {
            '_id': 'some-object-id',
            'role': 'ROLE_ADMIN',
            'pages': {'dashboard': {'active': []}}
        }
        
        result = await get_page_access('ROLE_ADMIN')
        
        assert result['role'] == 'ROLE_ADMIN'
        assert '_id' in result
        assert isinstance(result['_id'], str)

    @pytest.mark.asyncio
    @patch('rai_backend.router.router.mydb')
    async def test_get_page_access_new_not_found(self, mock_db):
        """Test getting page access when not found"""
        from rai_backend.router.router import get_page_access
        from fastapi import HTTPException
        
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_page_access('ROLE_UNKNOWN')
        
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @patch('rai_backend.router.router.mydb')
    async def test_update_page_access_success(self, mock_db):
        """Test updating page access successfully"""
        from rai_backend.router.router import update_page_access
        
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one_and_update.return_value = {
            'role': 'ROLE_ADMIN',
            'pages': {'newpage': {'active': []}}
        }
        
        payload = {
            'role': 'ROLE_ADMIN',
            'pages': {'pages': {'newpage': {'active': []}}}
        }
        
        result = await update_page_access(payload)
        
        assert result['message'] == 'Page access updated successfully'

    @pytest.mark.asyncio
    @patch('rai_backend.router.router.mydb')
    async def test_update_page_access_not_found(self, mock_db):
        """Test updating page access when role not found"""
        from rai_backend.router.router import update_page_access
        from fastapi import HTTPException
        
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one_and_update.return_value = None
        
        payload = {
            'role': 'ROLE_UNKNOWN',
            'pages': {'pages': {}}
        }
        
        with pytest.raises(HTTPException) as exc_info:
            await update_page_access(payload)
        
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @patch('rai_backend.router.router.mydb')
    async def test_create_page_access_success(self, mock_db):
        """Test creating page access successfully"""
        from rai_backend.router.router import create_page_access, CreateAuth
        
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = None
        mock_collection.insert_one.return_value = MagicMock(inserted_id='new-id')
        
        create_auth = CreateAuth(role='ROLE_NEW')
        result = await create_page_access(create_auth)
        
        assert result['message'] == 'Page access created successfully'

    @pytest.mark.asyncio
    @patch('rai_backend.router.router.mydb')
    async def test_create_page_access_already_exists(self, mock_db):
        """Test creating page access when role already exists"""
        from rai_backend.router.router import create_page_access, CreateAuth
        from fastapi import HTTPException
        
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = {'role': 'ROLE_ADMIN'}
        
        create_auth = CreateAuth(role='ROLE_ADMIN')
        
        with pytest.raises(HTTPException) as exc_info:
            await create_page_access(create_auth)
        
        assert exc_info.value.status_code == 200
        assert exc_info.value.detail == 'Role already exists'


class TestTelemetryFlagEndpoints:
    """Test telemetry flag CRUD endpoints"""

    @patch('rai_backend.router.router.TelemetryContent')
    def test_get_all_telemetry_data(self, mock_telemetry):
        """Test getting all telemetry data"""
        from rai_backend.router.router import router
        from fastapi import FastAPI
        from datetime import datetime
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        mock_telemetry.getAlldata.return_value = {
            'DataList': [
                {
                    'Module': 'RaiBackend',
                    'TelemetryFlag': True,
                    'CreatedDateTime': datetime.now(),
                    'LastUpdatedDateTime': datetime.now()
                }
            ]
        }
        
        response = client.get('/getAll/telemetry')
        
        assert response.status_code == 200
        assert 'DataList' in response.json()

    @patch('rai_backend.router.router.TelemetryContent')
    def test_create_telemetry_flag(self, mock_telemetry):
        """Test creating telemetry flag"""
        from rai_backend.router.router import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        mock_telemetry.creation.return_value = {
            'status': 'success'
        }
        
        response = client.post('/create/telemetry', json={
            'Module': 'TestModule',
            'TelemetryFlag': False
        })
        
        assert response.status_code == 200

    @patch('rai_backend.router.router.TelemetryContent')
    def test_update_telemetry_flag(self, mock_telemetry):
        """Test updating telemetry flag"""
        from rai_backend.router.router import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        mock_telemetry.updation.return_value = {
            'status': 'success'
        }
        
        response = client.patch('/update/telemetry', json={
            'Module': 'RaiBackend',
            'TelemetryFlag': True
        })
        
        assert response.status_code == 200
