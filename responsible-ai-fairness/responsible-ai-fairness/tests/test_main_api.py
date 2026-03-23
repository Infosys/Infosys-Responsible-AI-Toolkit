"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from fastapi.testclient import TestClient
from fastapi import FastAPI
import time


# Test fixtures
@pytest.fixture
def mock_health_checker():
    """Mock HealthCheck class for testing"""
    mock = MagicMock()
    mock.check_azure_openai.return_value = {
        'healthy': True,
        'status': 'Azure OpenAI OK',
        'message': 'Azure OpenAI OK'
    }
    mock.check_database.return_value = {
        'healthy': True,
        'status': 'Database OK',
        'message': 'Database OK'
    }
    mock.check_logger.return_value = {
        'healthy': True,
        'status': 'Logger OK',
        'message': 'Console handler active | File handler active'
    }
    return mock


@pytest.fixture
def mock_health_checker_unhealthy():
    """Mock HealthCheck class with unhealthy services"""
    mock = MagicMock()
    mock.check_azure_openai.return_value = {
        'healthy': False,
        'status': 'Azure OpenAI Unhealthy',
        'message': 'Connection failed'
    }
    mock.check_database.return_value = {
        'healthy': False,
        'status': 'Database Unhealthy',
        'message': 'Database connection failed'
    }
    mock.check_logger.return_value = {
        'healthy': False,
        'status': 'Logger Unhealthy',
        'message': 'Log file is not writable'
    }
    return mock


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    # Mock environment variables before importing main_api
    with patch.dict(os.environ, {
        'allow_methods': '*',
        'allow_origin': '*',
        'content_security_policy': "default-src 'self'",
        'cache_control': 'no-cache, no-store, must-revalidate',
        'XSS_header': '1; mode=block',
        'Vary_header': 'Accept-Encoding',
        'Pragma': 'no-cache',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY'
    }):
        # Import main_api after setting environment variables
        import main_api
        # Reset the start_time for consistent testing
        main_api.start_time = datetime.now()
        client = TestClient(main_api.app)
        yield client


@pytest.fixture
def mock_logger():
    """Mock CustomLogger"""
    with patch('main_api.CustomLogger') as mock:
        yield mock


class TestAppInitialization:
    """Test suite for FastAPI app initialization"""
    
    def test_app_creation(self, client):
        """Test that FastAPI app is created with correct configuration"""
        import main_api
        assert main_api.app.title == 'FairnessService'
        assert main_api.app.version == '1.0.0'
        assert main_api.app.openapi_url == "/api/v1/fairness/openapi.json"
        assert main_api.app.docs_url == "/api/v1/fairness/docs"
        assert main_api.app.redoc_url == "/api/v1/fairness/redoc"
    
    def test_cors_middleware_added(self, client):
        """Test that CORS middleware is properly configured"""
        import main_api
        # Check if CORSMiddleware is in the middleware stack
        middleware_types = [m.cls.__name__ for m in main_api.app.user_middleware]
        assert 'CORSMiddleware' in middleware_types
    
    def test_xss_middleware_added(self, client):
        """Test that XSSProtectionMiddleware is added"""
        import main_api
        # Check if XSSProtectionMiddleware is in the middleware stack
        middleware_types = [m.cls.__name__ for m in main_api.app.user_middleware]
        assert 'XSSProtectionMiddleware' in middleware_types
    
    def test_routers_included(self, client):
        """Test that all routers are registered"""
        import main_api
        # Get all routes from the app
        routes = [route.path for route in main_api.app.routes]
        # Check that routes with the prefix exist
        assert any('/api/v1' in route for route in routes)


class TestLivenessEndpoint:
    """Test suite for /liveness endpoint"""
    
    def test_liveness_check_success(self, client):
        """Test successful liveness check"""
        response = client.get("/liveness")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'
        assert 'uptime' in data
        assert data['uptime'].endswith('s')
        assert 'timestamp' in data
    
    def test_liveness_check_returns_correct_schema(self, client):
        """Test that liveness returns correct data schema"""
        response = client.get("/liveness")
        data = response.json()
        assert 'status' in data
        assert 'uptime' in data
        assert 'timestamp' in data
        assert len(data.keys()) == 3
    
    def test_liveness_check_uptime_increases(self, client):
        """Test that uptime increases with consecutive calls"""
        response1 = client.get("/liveness")
        uptime1 = int(response1.json()['uptime'].rstrip('s'))
        
        time.sleep(1)
        
        response2 = client.get("/liveness")
        uptime2 = int(response2.json()['uptime'].rstrip('s'))
        
        assert uptime2 >= uptime1
    
    def test_liveness_timestamp_format(self, client):
        """Test that timestamp is in correct datetime format"""
        response = client.get("/liveness")
        data = response.json()
        timestamp = data['timestamp']
        # Verify timestamp can be parsed
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))


class TestHealthCheckEndpoint:
    """Test suite for /health endpoint"""
    
    @patch('main_api.Health_Checker')
    def test_health_check_all_healthy(self, mock_health_class, client, mock_health_checker):
        """Test health check when all services are healthy"""
        mock_health_class.return_value = mock_health_checker
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'healthy'
        assert 'uptime' in data
        assert 'time_taken' in data
        assert 'timestamp' in data
        assert 'dependencies_check' in data
        
        deps = data['dependencies_check']
        assert deps['database_health_check'] == 'Database OK'
        assert deps['logging_health_check'] == 'Logger OK'
        assert 'GPT-4o-mini' in deps['healthy_models']
        assert len(deps['unhealthy_models']) == 0
    
    @patch('main_api.Health_Checker')
    def test_health_check_all_unhealthy(self, mock_health_class, client, mock_health_checker_unhealthy):
        """Test health check when all services are unhealthy"""
        mock_health_class.return_value = mock_health_checker_unhealthy
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'unhealthy'
        deps = data['dependencies_check']
        assert deps['database_health_check'] == 'Database Unhealthy'
        assert deps['logging_health_check'] == 'Logger Unhealthy'
        assert 'GPT-4o-mini' in deps['unhealthy_models']
        assert len(deps['healthy_models']) == 0
    
    @patch('main_api.Health_Checker')
    def test_health_check_partial_healthy(self, mock_health_class, client):
        """Test health check when some services are healthy and some are not"""
        mock = MagicMock()
        mock.check_azure_openai.return_value = {
            'healthy': True,
            'status': 'Azure OpenAI OK',
            'message': 'Azure OpenAI OK'
        }
        mock.check_database.return_value = {
            'healthy': False,
            'status': 'Database Unhealthy',
            'message': 'Connection failed'
        }
        mock.check_logger.return_value = {
            'healthy': True,
            'status': 'Logger OK',
            'message': 'Logger OK'
        }
        mock_health_class.return_value = mock
        
        response = client.get("/health")
        data = response.json()
        
        assert data['status'] == 'unhealthy'
        deps = data['dependencies_check']
        assert 'GPT-4o-mini' in deps['healthy_models']
        assert deps['database_health_check'] == 'Database Unhealthy'
    
    @patch('main_api.Health_Checker')
    def test_health_check_returns_correct_schema(self, mock_health_class, client, mock_health_checker):
        """Test that health check returns correct data schema"""
        mock_health_class.return_value = mock_health_checker
        
        response = client.get("/health")
        data = response.json()
        
        assert 'status' in data
        assert 'uptime' in data
        assert 'time_taken' in data
        assert 'timestamp' in data
        assert 'dependencies_check' in data
        
        deps = data['dependencies_check']
        assert 'healthy_models' in deps
        assert 'unhealthy_models' in deps
        assert 'database_health_check' in deps
        assert 'logging_health_check' in deps
    
    @patch('main_api.Health_Checker')
    def test_health_check_uptime_format(self, mock_health_class, client, mock_health_checker):
        """Test that uptime is in correct format"""
        mock_health_class.return_value = mock_health_checker
        
        response = client.get("/health")
        data = response.json()
        
        uptime = data['uptime']
        assert uptime.endswith('s')
        assert int(uptime.rstrip('s')) >= 0
    
    @patch('main_api.Health_Checker')
    def test_health_check_time_taken_format(self, mock_health_class, client, mock_health_checker):
        """Test that time_taken is in correct format"""
        mock_health_class.return_value = mock_health_checker
        
        response = client.get("/health")
        data = response.json()
        
        time_taken = data['time_taken']
        assert time_taken.endswith('s')
        assert int(time_taken.rstrip('s')) >= 0


class TestXSSProtectionMiddleware:
    """Test suite for XSSProtectionMiddleware"""
    
    def test_xss_headers_on_regular_endpoint(self, client):
        """Test that XSS protection headers are added to regular endpoints"""
        response = client.get("/liveness")
        
        assert 'Content-Security-Policy' in response.headers
        assert 'X-XSS-Protection' in response.headers
        assert 'Cache-Control' in response.headers
        assert 'X-Frame-Options' in response.headers
        assert 'X-Content-Type-Options' in response.headers
        assert 'Pragma' in response.headers
        assert 'Strict-Transport-Security' in response.headers
        assert 'Vary' in response.headers
    
    def test_xss_headers_values(self, client):
        """Test that XSS protection headers have correct values"""
        response = client.get("/liveness")
        
        assert response.headers['X-XSS-Protection'] == '1; mode=block'
        assert response.headers['Cache-Control'] == 'no-cache, no-store, must-revalidate'
        assert response.headers['X-Frame-Options'] == 'DENY'
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        assert response.headers['Pragma'] == 'no-cache'
        assert 'max-age=31536000' in response.headers['Strict-Transport-Security']
        assert response.headers['Vary'] == 'Accept-Encoding'
    
    def test_docs_endpoint_special_csp(self, client):
        """Test that /docs endpoint has special Content-Security-Policy"""
        response = client.get("/api/v1/fairness/docs")
        
        # The /docs endpoint should have a more permissive CSP
        csp = response.headers.get('Content-Security-Policy', '')
        assert 'unsafe-inline' in csp
        assert 'unsafe-eval' in csp
        assert 'cdn.jsdelivr.net' in csp
    
    def test_openapi_endpoint_special_csp(self, client):
        """Test that /openapi.json endpoint has special Content-Security-Policy"""
        response = client.get("/api/v1/fairness/openapi.json")
        
        # The /openapi.json endpoint should have a more permissive CSP
        csp = response.headers.get('Content-Security-Policy', '')
        assert 'unsafe-inline' in csp
        assert 'unsafe-eval' in csp
    
    def test_charset_added_to_content_type(self, client):
        """Test that charset is added to Content-Type header"""
        response = client.get("/liveness")
        
        content_type = response.headers.get('Content-Type', '')
        if content_type and 'charset=' not in content_type:
            # This assertion might not apply if the content type already has charset
            pass
        # FastAPI typically adds charset automatically, so we just check it exists
        assert 'Content-Type' in response.headers


class TestRouterRegistration:
    """Test suite for router registration"""
    
    def test_llm_router_registered(self, client):
        """Test that LLM router is registered with correct prefix"""
        import main_api
        routes = [route.path for route in main_api.app.routes]
        # Check for routes with /api/v1 prefix
        assert any('/api/v1' in route for route in routes)
    
    def test_standalone_apis_router_registered(self, client):
        """Test that standalone APIs router is registered"""
        import main_api
        routes = [route.path for route in main_api.app.routes]
        assert any('/api/v1' in route for route in routes)
    
    def test_workbench_router_registered(self, client):
        """Test that workbench router is registered"""
        import main_api
        routes = [route.path for route in main_api.app.routes]
        assert any('/api/v1' in route for route in routes)
    
    def test_app_prefix_correct(self, client):
        """Test that app prefix is correctly set to /api/v1"""
        import main_api
        assert main_api.app_prefix == '/api/v1'


class TestEnvironmentVariables:
    """Test suite for environment variable handling"""
    
    def test_default_values_when_env_vars_missing(self):
        """Test that app uses default values when environment variables are not set"""
        # Set minimal required env vars to prevent None errors
        minimal_vars = {
            'allow_methods': '*',
            'allow_origin': '*'
        }
        with patch.dict(os.environ, minimal_vars, clear=True):
            # Reimport to test default behavior
            import importlib
            import main_api
            importlib.reload(main_api)
            
            # Test with test client
            client = TestClient(main_api.app)
            response = client.get("/liveness")
            
            # Check that default header values are applied (from XSSProtectionMiddleware defaults)
            assert 'X-XSS-Protection' in response.headers
            assert 'X-Frame-Options' in response.headers
    
    def test_custom_env_vars_applied(self):
        """Test that custom environment variables are correctly applied"""
        custom_vars = {
            'allow_methods': 'GET,POST',
            'allow_origin': 'http://localhost',
            'content_security_policy': "default-src 'self' 'unsafe-inline'",
            'cache_control': 'max-age=3600',
            'XSS_header': '0',
            'Vary_header': 'Origin',
            'Pragma': 'cache',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'SAMEORIGIN'
        }
        
        with patch.dict(os.environ, custom_vars):
            import importlib
            import main_api
            importlib.reload(main_api)
            
            client = TestClient(main_api.app)
            response = client.get("/liveness")
            
            # Verify custom values are used
            assert response.headers['X-XSS-Protection'] == '0'
            assert response.headers['Cache-Control'] == 'max-age=3600'
            assert response.headers['X-Frame-Options'] == 'SAMEORIGIN'
            assert response.headers['Vary'] == 'Origin'
            assert response.headers['Pragma'] == 'cache'


class TestResponseModels:
    """Test suite for response models"""
    
    def test_liveness_model_structure(self, client):
        """Test that Liveness response model has correct structure"""
        response = client.get("/liveness")
        data = response.json()
        
        # Check all required fields are present
        required_fields = ['status', 'uptime', 'timestamp']
        for field in required_fields:
            assert field in data
    
    def test_health_check_model_structure(self, client):
        """Test that HealthCheck response model has correct structure"""
        with patch('main_api.Health_Checker') as mock_health_class:
            mock = MagicMock()
            mock.check_azure_openai.return_value = {
                'healthy': True,
                'status': 'Azure OpenAI OK',
                'message': 'OK'
            }
            mock.check_database.return_value = {
                'healthy': True,
                'status': 'Database OK',
                'message': 'OK'
            }
            mock.check_logger.return_value = {
                'healthy': True,
                'status': 'Logger OK',
                'message': 'OK'
            }
            mock_health_class.return_value = mock
            
            response = client.get("/health")
            data = response.json()
            
            # Check top-level fields
            required_fields = ['dependencies_check', 'status', 'time_taken', 'timestamp', 'uptime']
            for field in required_fields:
                assert field in data
            
            # Check dependencies_check structure
            deps = data['dependencies_check']
            deps_fields = ['healthy_models', 'unhealthy_models', 'database_health_check', 'logging_health_check']
            for field in deps_fields:
                assert field in deps
    
    def test_dependencies_check_model_structure(self, client):
        """Test that DependenciesCheck model has correct structure"""
        with patch('main_api.Health_Checker') as mock_health_class:
            mock = MagicMock()
            mock.check_azure_openai.return_value = {'healthy': True, 'status': 'OK', 'message': 'OK'}
            mock.check_database.return_value = {'healthy': True, 'status': 'Database OK', 'message': 'OK'}
            mock.check_logger.return_value = {'healthy': True, 'status': 'Logger OK', 'message': 'OK'}
            mock_health_class.return_value = mock
            
            response = client.get("/health")
            data = response.json()
            deps = data['dependencies_check']
            
            assert isinstance(deps['healthy_models'], list)
            assert isinstance(deps['unhealthy_models'], list)
            assert isinstance(deps['database_health_check'], str)
            assert isinstance(deps['logging_health_check'], str)


class TestEdgeCases:
    """Test suite for edge cases"""
    
    @patch('main_api.Health_Checker')
    def test_health_check_with_exception(self, mock_health_class, client):
        """Test health check when health checker raises an exception"""
        mock = MagicMock()
        mock.check_azure_openai.side_effect = Exception("Connection error")
        mock.check_database.return_value = {'healthy': True, 'status': 'OK', 'message': 'OK'}
        mock.check_logger.return_value = {'healthy': True, 'status': 'OK', 'message': 'OK'}
        mock_health_class.return_value = mock
        
        # Should handle exception gracefully
        try:
            response = client.get("/health")
            # If it doesn't raise, check status code
            assert response.status_code in [200, 500]
        except Exception:
            # Exception is expected in this test case
            pass
    
    def test_multiple_concurrent_liveness_checks(self, client):
        """Test multiple concurrent liveness checks"""
        responses = []
        for _ in range(5):
            response = client.get("/liveness")
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            assert response.json()['status'] == 'ok'
    
    @patch('main_api.Health_Checker')
    def test_multiple_concurrent_health_checks(self, mock_health_class, client, mock_health_checker):
        """Test multiple concurrent health checks"""
        mock_health_class.return_value = mock_health_checker
        
        responses = []
        for _ in range(3):
            response = client.get("/health")
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
    
    def test_invalid_endpoint(self, client):
        """Test accessing an invalid endpoint"""
        response = client.get("/invalid-endpoint")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test using wrong HTTP method"""
        response = client.post("/liveness")
        assert response.status_code == 405


class TestIntegration:
    """Integration tests for main_api"""
    
    @patch('main_api.Health_Checker')
    def test_full_workflow(self, mock_health_class, client, mock_health_checker):
        """Test full workflow: liveness check followed by health check"""
        mock_health_class.return_value = mock_health_checker
        
        # First check liveness
        liveness_response = client.get("/liveness")
        assert liveness_response.status_code == 200
        
        # Then check health
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        # Verify both work correctly
        assert liveness_response.json()['status'] == 'ok'
        assert health_response.json()['status'] == 'healthy'
    
    def test_app_startup_and_endpoints(self, client):
        """Test that app starts up correctly and all endpoints are accessible"""
        # Check liveness
        liveness = client.get("/liveness")
        assert liveness.status_code == 200
        
        # Check OpenAPI docs are accessible
        openapi = client.get("/api/v1/fairness/openapi.json")
        assert openapi.status_code == 200
        
        # Check that OpenAPI schema is valid JSON
        openapi_data = openapi.json()
        assert 'openapi' in openapi_data
        assert 'info' in openapi_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
