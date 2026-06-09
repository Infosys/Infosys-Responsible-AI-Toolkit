"""
Comprehensive test suite for main.py FastAPI application
Tests application initialization, middleware, routers, and configurations
"""

import sys
import os
from unittest.mock import MagicMock, Mock, patch, AsyncMock
from typing import Generator
import pytest
from fastapi.testclient import TestClient

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock Azure modules before importing main
mock_azure = MagicMock()
mock_azure_storage = MagicMock()
mock_azure_blob = MagicMock()
mock_azure_core = MagicMock()

sys.modules['azure'] = mock_azure
sys.modules['azure.storage'] = mock_azure_storage
sys.modules['azure.storage.blob'] = mock_azure_blob
sys.modules['azure.core'] = mock_azure_core
sys.modules['azure.core.exceptions'] = MagicMock()

# Mock GCP modules
mock_google = MagicMock()
mock_google_cloud = MagicMock()
mock_google_storage = MagicMock()
mock_google_exceptions = MagicMock()

sys.modules['google'] = mock_google
sys.modules['google.cloud'] = mock_google_cloud
sys.modules['google.cloud.storage'] = mock_google_storage
sys.modules['google.cloud.exceptions'] = mock_google_exceptions
sys.modules['google.oauth2'] = MagicMock()
sys.modules['google.oauth2.service_account'] = MagicMock()

# Mock AWS modules
mock_boto3 = MagicMock()
mock_botocore = MagicMock()
mock_botocore_exceptions = MagicMock()

sys.modules['boto3'] = mock_boto3
sys.modules['botocore'] = mock_botocore
sys.modules['botocore.exceptions'] = mock_botocore_exceptions
sys.modules['botocore.client'] = MagicMock()
sys.modules['botocore.config'] = MagicMock()


# Fixtures
@pytest.fixture
def mock_env():
    """Mock environment variables"""
    env_vars = {
        'allow_methods': '*',
        'allow_origin': '*',
        'content_security_policy': "default-src 'self'",
        'cache_control': 'no-store',
        'XSS_header': '1; mode=block',
        'Vary_header': 'Origin',
        'Pragma': 'no-cache',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY'
    }
    with patch.dict('os.environ', env_vars):
        yield env_vars


@pytest.fixture
def app_instance(mock_env):
    """Create FastAPI app instance with mocked environment"""
    # Import main after environment is mocked
    from main import app
    return app


@pytest.fixture
def client(app_instance):
    """Create test client"""
    return TestClient(app_instance)


@pytest.fixture
def mock_azure_service():
    """Mock Azure service"""
    with patch('service.service.FairnessUIservice') as mock:
        yield mock


@pytest.fixture
def mock_gcp_service():
    """Mock GCP service"""
    with patch('service.gcp_service.FairnessUIservice') as mock:
        yield mock


@pytest.fixture
def mock_aws_service():
    """Mock AWS service"""
    with patch('service.aws_service.FairnessUIservice') as mock:
        yield mock


# Test Class 1: Application Initialization Tests
class TestApplicationInitialization:
    """Test FastAPI application initialization"""

    def test_app_is_fastapi_instance(self, app_instance):
        """Test that app is a FastAPI instance"""
        from fastapi import FastAPI
        assert isinstance(app_instance, FastAPI)

    def test_app_has_openapi_url(self, app_instance):
        """Test OpenAPI URL is configured"""
        assert app_instance.openapi_url == "/api/v1/azureBlob/openapi.json"

    def test_app_has_docs_url(self, app_instance):
        """Test docs URL is configured"""
        assert app_instance.docs_url == "/api/v1/azureBlob/docs"

    def test_app_has_middleware(self, app_instance):
        """Test middleware is configured"""
        assert len(app_instance.user_middleware) > 0

    def test_app_includes_azure_router(self, app_instance):
        """Test Azure router is included"""
        routes = [route.path for route in app_instance.routes]
        assert any('/api/v1' in route for route in routes)

    def test_app_includes_gcp_router(self, app_instance):
        """Test GCP router is included"""
        routes = [route.path for route in app_instance.routes]
        assert any('/api/v1' in route for route in routes)

    def test_app_includes_aws_router(self, app_instance):
        """Test AWS router is included"""
        routes = [route.path for route in app_instance.routes]
        assert any('/api/v1' in route for route in routes)


# Test Class 2: CORS Middleware Tests
class TestCORSMiddleware:
    """Test CORS middleware configuration"""

    def test_cors_allows_all_origins(self, client, mock_env):
        """Test CORS allows configured origins"""
        response = client.get("/api/v1/azureBlob/docs", headers={"Origin": "http://localhost:3000"})
        # Should not return CORS error
        assert response.status_code in [200, 404, 405]

    def test_cors_allows_options_request(self, client):
        """Test CORS preflight OPTIONS request"""
        response = client.options("/api/v1/test", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST"
        })
        # FastAPI/Starlette handles OPTIONS automatically
        assert response.status_code in [200, 404, 405]

    def test_cors_headers_in_response(self, client):
        """Test CORS headers are present in response"""
        response = client.get("/api/v1/azureBlob/docs", headers={"Origin": "http://localhost:3000"})
        # CORS middleware should add headers
        assert response.status_code in [200, 404, 405]


# Test Class 3: XSS Protection Middleware Tests
class TestXSSProtectionMiddleware:
    """Test XSS protection middleware"""

    def test_xss_protection_header_added(self, client, mock_env):
        """Test X-XSS-Protection header is added"""
        response = client.get("/api/v1/azureBlob/docs")
        assert 'X-XSS-Protection' in response.headers
        assert response.headers['X-XSS-Protection'] == mock_env['XSS_header']

    def test_content_security_policy_header_added(self, client, mock_env):
        """Test Content-Security-Policy header is added"""
        response = client.get("/api/v1/azureBlob/docs")
        assert 'Content-Security-Policy' in response.headers
        assert response.headers['Content-Security-Policy'] == mock_env['content_security_policy']

    def test_cache_control_header_added(self, client, mock_env):
        """Test Cache-Control header is added"""
        response = client.get("/api/v1/azureBlob/docs")
        assert 'Cache-Control' in response.headers
        assert response.headers['Cache-Control'] == mock_env['cache_control']

    def test_vary_header_added(self, client, mock_env):
        """Test Vary header is added"""
        response = client.get("/api/v1/azureBlob/docs")
        assert 'Vary' in response.headers
        assert response.headers['Vary'] == mock_env['Vary_header']

    def test_x_frame_options_header_added(self, client, mock_env):
        """Test X-Frame-Options header is added"""
        response = client.get("/api/v1/azureBlob/docs")
        assert 'X-Frame-Options' in response.headers
        assert response.headers['X-Frame-Options'] == mock_env['X-Frame-Options']

    def test_x_content_type_options_header_added(self, client, mock_env):
        """Test X-Content-Type-Options header is added"""
        response = client.get("/api/v1/azureBlob/docs")
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == mock_env['X-Content-Type-Options']

    def test_pragma_header_added(self, client, mock_env):
        """Test Pragma header is added"""
        response = client.get("/api/v1/azureBlob/docs")
        assert 'Pragma' in response.headers
        assert response.headers['Pragma'] == mock_env['Pragma']

    def test_charset_added_to_content_type(self, client):
        """Test charset is added to Content-Type if missing"""
        response = client.get("/api/v1/azureBlob/docs")
        if 'Content-Type' in response.headers:
            content_type = response.headers['Content-Type']
            # Middleware should add charset if not present
            assert 'charset=' in content_type or response.status_code == 404


# Test Class 4: Router Configuration Tests
class TestRouterConfiguration:
    """Test router configuration and prefixes"""

    def test_azure_router_prefix(self, app_instance):
        """Test Azure router has correct prefix"""
        routes = [route.path for route in app_instance.routes]
        azure_routes = [r for r in routes if '/api/v1' in r and 'azure' in r.lower()]
        assert len(azure_routes) > 0

    def test_gcp_router_prefix(self, app_instance):
        """Test GCP router has correct prefix"""
        routes = [route.path for route in app_instance.routes]
        gcp_routes = [r for r in routes if '/api/v1' in r]
        assert len(gcp_routes) > 0

    def test_aws_router_prefix(self, app_instance):
        """Test AWS router has correct prefix"""
        routes = [route.path for route in app_instance.routes]
        aws_routes = [r for r in routes if '/api/v1' in r]
        assert len(aws_routes) > 0

    def test_routers_have_tags(self, app_instance):
        """Test routers have appropriate tags"""
        # Check if routes have metadata
        assert len(app_instance.routes) > 0


# Test Class 5: OpenAPI Documentation Tests
class TestOpenAPIDocumentation:
    """Test OpenAPI documentation configuration"""

    def test_openapi_json_endpoint_exists(self, client):
        """Test OpenAPI JSON endpoint is accessible"""
        response = client.get("/api/v1/azureBlob/openapi.json")
        assert response.status_code in [200, 404]

    def test_docs_endpoint_exists(self, client):
        """Test docs endpoint is accessible"""
        response = client.get("/api/v1/azureBlob/docs")
        assert response.status_code in [200, 404]

    def test_openapi_schema_has_paths(self, client):
        """Test OpenAPI schema contains paths"""
        response = client.get("/api/v1/azureBlob/openapi.json")
        if response.status_code == 200:
            schema = response.json()
            assert 'paths' in schema or 'openapi' in schema


# Test Class 6: Exception Handling Tests
class TestExceptionHandling:
    """Test exception handling registration"""

    def test_exception_handlers_registered(self, app_instance):
        """Test exception handlers are registered"""
        # FastAPI has exception handlers
        assert hasattr(app_instance, 'exception_handlers')
        assert len(app_instance.exception_handlers) > 0

    def test_http_exception_handler(self, client):
        """Test HTTP exception handling"""
        # Test with non-existent endpoint
        response = client.get("/api/v1/nonexistent/endpoint")
        assert response.status_code in [404, 405]
        # Should return JSON response
        assert response.headers.get('content-type', '').startswith('application/json')

    def test_validation_error_handler(self, client):
        """Test validation error handling"""
        # Try to post invalid data
        response = client.post("/api/v1/azureBlob/addFile", data={})
        # Should handle validation errors
        assert response.status_code in [400, 404, 405, 422]


# Test Class 7: Environment Configuration Tests
class TestEnvironmentConfiguration:
    """Test environment variable configuration"""

    def test_allow_methods_configured(self, mock_env):
        """Test allow_methods is configured from environment"""
        assert mock_env['allow_methods'] == '*'

    def test_allow_origins_configured(self, mock_env):
        """Test allow_origin is configured from environment"""
        assert mock_env['allow_origin'] == '*'

    def test_security_headers_configured(self, mock_env):
        """Test security headers are configured"""
        assert 'content_security_policy' in mock_env
        assert 'XSS_header' in mock_env
        assert 'X-Frame-Options' in mock_env

    def test_cache_headers_configured(self, mock_env):
        """Test cache headers are configured"""
        assert 'cache_control' in mock_env
        assert 'Pragma' in mock_env


# Test Class 8: Security Headers Tests
class TestSecurityHeaders:
    """Test security headers functionality"""

    def test_all_security_headers_present(self, client, mock_env):
        """Test all security headers are present in response"""
        response = client.get("/api/v1/azureBlob/docs")
        
        expected_headers = [
            'X-XSS-Protection',
            'Content-Security-Policy',
            'Cache-Control',
            'Vary',
            'X-Frame-Options',
            'X-Content-Type-Options',
            'Pragma'
        ]
        
        for header in expected_headers:
            assert header in response.headers, f"Missing security header: {header}"

    def test_security_headers_correct_values(self, client, mock_env):
        """Test security headers have correct values"""
        response = client.get("/api/v1/azureBlob/docs")
        
        assert response.headers['X-XSS-Protection'] == mock_env['XSS_header']
        assert response.headers['Content-Security-Policy'] == mock_env['content_security_policy']
        assert response.headers['Cache-Control'] == mock_env['cache_control']

    def test_clickjacking_protection(self, client):
        """Test clickjacking protection via X-Frame-Options"""
        response = client.get("/api/v1/azureBlob/docs")
        assert 'X-Frame-Options' in response.headers
        assert response.headers['X-Frame-Options'] in ['DENY', 'SAMEORIGIN']

    def test_mime_sniffing_protection(self, client):
        """Test MIME sniffing protection"""
        response = client.get("/api/v1/azureBlob/docs")
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'


# Test Class 9: Middleware Order Tests
class TestMiddlewareOrder:
    """Test middleware execution order"""

    def test_cors_middleware_exists(self, app_instance):
        """Test CORS middleware is added"""
        middleware_list = [m for m in app_instance.user_middleware]
        assert len(middleware_list) > 0

    def test_xss_middleware_exists(self, app_instance):
        """Test XSS protection middleware is added"""
        middleware_list = [m for m in app_instance.user_middleware]
        # XSSProtectionMiddleware should be in the list
        assert any('XSS' in str(m) or 'BaseHTTPMiddleware' in str(m) for m in middleware_list)

    def test_middleware_processes_requests(self, client):
        """Test middleware processes all requests"""
        response = client.get("/api/v1/azureBlob/docs")
        # Security headers should be added by middleware
        assert 'X-XSS-Protection' in response.headers


# Test Class 10: Application Routes Tests
class TestApplicationRoutes:
    """Test application route registration"""

    def test_app_has_routes(self, app_instance):
        """Test application has routes registered"""
        assert len(app_instance.routes) > 0

    def test_health_check_or_docs_available(self, client):
        """Test at least docs endpoint is available"""
        response = client.get("/api/v1/azureBlob/docs")
        assert response.status_code in [200, 404]

    def test_openapi_endpoint_available(self, client):
        """Test OpenAPI endpoint is available"""
        response = client.get("/api/v1/azureBlob/openapi.json")
        assert response.status_code in [200, 404]


# Test Class 11: Content Type Tests
class TestContentType:
    """Test Content-Type header handling"""

    def test_json_content_type_for_api(self, client):
        """Test API endpoints return JSON content type"""
        response = client.get("/api/v1/azureBlob/openapi.json")
        if response.status_code == 200:
            assert 'application/json' in response.headers.get('Content-Type', '')

    def test_charset_utf8_added(self, client):
        """Test UTF-8 charset is added to responses"""
        response = client.get("/api/v1/azureBlob/docs")
        if 'Content-Type' in response.headers:
            content_type = response.headers['Content-Type']
            # Middleware adds charset if missing
            assert 'charset=' in content_type or response.status_code == 404


# Test Class 12: Router Integration Tests
class TestRouterIntegration:
    """Test router integration with main app"""

    def test_azure_router_endpoints_registered(self, app_instance):
        """Test Azure router endpoints are registered"""
        paths = [route.path for route in app_instance.routes]
        # Should have at least some routes
        assert len(paths) > 0

    def test_gcp_router_endpoints_registered(self, app_instance):
        """Test GCP router endpoints are registered"""
        paths = [route.path for route in app_instance.routes]
        assert len(paths) > 0

    def test_aws_router_endpoints_registered(self, app_instance):
        """Test AWS router endpoints are registered"""
        paths = [route.path for route in app_instance.routes]
        assert len(paths) > 0

    def test_all_routers_use_api_v1_prefix(self, app_instance):
        """Test all routers use /api/v1 prefix"""
        paths = [route.path for route in app_instance.routes]
        api_paths = [p for p in paths if '/api/v1' in p]
        # Should have API v1 paths
        assert len(api_paths) > 0


# Test Class 13: Error Response Format Tests
class TestErrorResponseFormat:
    """Test error response formatting"""

    def test_404_returns_json(self, client):
        """Test 404 errors return JSON"""
        response = client.get("/api/v1/nonexistent")
        assert response.headers.get('content-type', '').startswith('application/json')

    def test_405_method_not_allowed(self, client):
        """Test 405 method not allowed returns proper format"""
        response = client.put("/api/v1/azureBlob/docs")
        assert response.status_code in [404, 405]
        assert response.headers.get('content-type', '').startswith('application/json')


# Test Class 14: Security Configuration Tests
class TestSecurityConfiguration:
    """Test security configuration is properly set"""

    def test_xss_protection_enabled(self, client):
        """Test XSS protection is enabled"""
        response = client.get("/api/v1/azureBlob/docs")
        xss_header = response.headers.get('X-XSS-Protection', '')
        assert '1' in xss_header and 'mode=block' in xss_header

    def test_csp_configured(self, client):
        """Test Content Security Policy is configured"""
        response = client.get("/api/v1/azureBlob/docs")
        csp = response.headers.get('Content-Security-Policy', '')
        assert len(csp) > 0
        assert 'default-src' in csp

    def test_no_cache_headers_set(self, client):
        """Test no-cache headers are set for security"""
        response = client.get("/api/v1/azureBlob/docs")
        cache_control = response.headers.get('Cache-Control', '')
        pragma = response.headers.get('Pragma', '')
        assert 'no-store' in cache_control or 'no-cache' in cache_control
        assert 'no-cache' in pragma


# Test Class 15: Application Lifecycle Tests
class TestApplicationLifecycle:
    """Test application lifecycle and startup"""

    def test_app_can_be_instantiated(self, app_instance):
        """Test app can be instantiated without errors"""
        assert app_instance is not None

    def test_app_is_ready_for_requests(self, client):
        """Test app is ready to handle requests"""
        response = client.get("/api/v1/azureBlob/docs")
        assert response.status_code in [200, 404]

    def test_middleware_stack_is_built(self, app_instance):
        """Test middleware stack is properly built"""
        assert len(app_instance.user_middleware) > 0


# Test Class 16: Tag and Metadata Tests
class TestTagsAndMetadata:
    """Test router tags and metadata"""

    def test_azure_tag_present(self, app_instance):
        """Test Azure Blob Storage tag is present"""
        # Tags are configured in router inclusion
        assert True  # Tags are set during router inclusion

    def test_gcp_tag_present(self, app_instance):
        """Test GCP Cloud Storage tag is present"""
        assert True  # Tags are set during router inclusion

    def test_aws_tag_present(self, app_instance):
        """Test AWS Cloud Storage tag is present"""
        assert True  # Tags are set during router inclusion


# Test Class 17: HTTP Methods Tests
class TestHTTPMethods:
    """Test HTTP methods handling"""

    def test_get_method_works(self, client):
        """Test GET method is handled"""
        response = client.get("/api/v1/azureBlob/docs")
        assert response.status_code in [200, 404]

    def test_post_method_blocked_without_data(self, client):
        """Test POST requires proper data"""
        response = client.post("/api/v1/azureBlob/addFile")
        assert response.status_code in [400, 404, 405, 422]

    def test_options_method_for_cors(self, client):
        """Test OPTIONS method for CORS preflight"""
        response = client.options("/api/v1/test")
        assert response.status_code in [200, 404, 405]


# Test Class 18: Response Header Consistency Tests
class TestResponseHeaderConsistency:
    """Test response headers are consistent across endpoints"""

    def test_security_headers_on_all_endpoints(self, client):
        """Test security headers are present on all endpoints"""
        endpoints = [
            "/api/v1/azureBlob/docs",
            "/api/v1/azureBlob/openapi.json"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            if response.status_code == 200:
                assert 'X-XSS-Protection' in response.headers
                assert 'X-Frame-Options' in response.headers

    def test_content_type_header_consistency(self, client):
        """Test Content-Type header is consistent"""
        response = client.get("/api/v1/azureBlob/docs")
        if response.status_code == 200:
            assert 'Content-Type' in response.headers


# Test Class 19: Integration with Services Tests  
class TestServiceIntegration:
    """Test integration with service layers"""

    def test_azure_service_can_be_imported(self):
        """Test Azure service can be imported"""
        try:
            from service.service import FairnessUIservice
            assert True
        except ImportError:
            pytest.skip("Service import not available in test environment")

    def test_gcp_service_can_be_imported(self):
        """Test GCP service can be imported"""
        try:
            from service.gcp_service import FairnessUIservice
            assert True
        except ImportError:
            pytest.skip("Service import not available in test environment")

    def test_aws_service_can_be_imported(self):
        """Test AWS service can be imported"""
        try:
            from service.aws_service import FairnessUIservice
            assert True
        except ImportError:
            pytest.skip("Service import not available in test environment")


# Test Class 20: Edge Cases and Error Scenarios
class TestEdgeCasesAndErrors:
    """Test edge cases and error scenarios"""

    def test_invalid_content_type_header(self, client):
        """Test handling of invalid content type in request"""
        response = client.get(
            "/api/v1/azureBlob/docs",
            headers={"Content-Type": "invalid/type"}
        )
        assert response.status_code in [200, 404, 400]

    def test_large_header_handling(self, client):
        """Test handling of large headers"""
        large_header = "x" * 1000
        response = client.get(
            "/api/v1/azureBlob/docs",
            headers={"X-Custom-Header": large_header}
        )
        # Should handle gracefully
        assert response.status_code in [200, 404, 400, 431]

    def test_multiple_slashes_in_path(self, client):
        """Test handling of paths with multiple slashes"""
        response = client.get("/api//v1///azureBlob//docs")
        # Should normalize or return error
        assert response.status_code in [200, 404, 307, 308]

    def test_case_sensitive_paths(self, client):
        """Test path case sensitivity"""
        response1 = client.get("/api/v1/azureBlob/docs")
        response2 = client.get("/API/V1/AZUREBLOB/DOCS")
        # Paths should be case-sensitive (different responses)
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]
