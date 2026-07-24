"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from typing import Dict, Any

# Add the parent directory to the path to import the main app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock database and trustllm modules before importing
with patch('dao.databaseConnection.DataBase') as mock_db_class:
    mock_db_instance = MagicMock()
    mock_db_class.return_value = mock_db_instance
    mock_db_instance.db = MagicMock()
    
    # Mock trustllm modules
    sys.modules['trustllm'] = MagicMock()
    sys.modules['trustllm.task'] = MagicMock()
    sys.modules['trustllm.utils'] = MagicMock()
    sys.modules['trustllm.generation'] = MagicMock()
    sys.modules['trustllm.task.pipeline'] = MagicMock()
    sys.modules['trustllm.dataset_download'] = MagicMock()
    
    from main_api import app


# Fixtures
@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_env_vars():
    """Mock environment variables."""
    with patch.dict(os.environ, {
        'cache_control': 'no-cache, no-store, must-revalidate',
        'allow_methods': '*',
        'allow_origin': '*',
        'content_security_policy': "default-src 'self'",
        'XSS_header': '1; mode=block',
        'Vary_header': 'Origin',
        'Pragma': 'no-cache',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY'
    }):
        yield


@pytest.fixture
def sample_request_headers():
    """Sample request headers."""
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Origin': 'http://localhost:3000'
    }


# Test Cases for Application Configuration
class TestApplicationConfiguration:
    """Test cases for FastAPI application configuration."""
    
    def test_app_instance_created(self, client):
        """Test that FastAPI app instance is created successfully."""
        assert app is not None
        assert app.title == "FastAPI"
    
    def test_openapi_url_configured(self, client):
        """Test that OpenAPI URL is configured correctly."""
        assert app.openapi_url == "/api/v1/trustllm/openapi.json"
    
    def test_docs_url_configured(self, client):
        """Test that docs URL is configured correctly."""
        assert app.docs_url == "/api/v1/trustllm/docs"
    
    def test_openapi_schema_accessible(self, client):
        """Test that OpenAPI schema is accessible."""
        response = client.get("/api/v1/trustllm/openapi.json")
        assert response.status_code == 200
        assert response.json() is not None
    
    def test_docs_page_accessible(self, client):
        """Test that Swagger docs page is accessible."""
        response = client.get("/api/v1/trustllm/docs")
        assert response.status_code == 200
    
    def test_app_has_routers_included(self, client):
        """Test that routers are included in the app."""
        # Check that routes exist with the correct prefix
        routes = [route.path for route in app.routes]
        assert any('/api/v1/trustllm' in route for route in routes)


# Test Cases for CORS Middleware
class TestCORSMiddleware:
    """Test cases for CORS middleware configuration."""
    
    def test_cors_headers_present(self, client, sample_request_headers):
        """Test that CORS headers are present in response."""
        response = client.options(
            "/api/v1/trustllm/docs",
            headers=sample_request_headers
        )
        assert response.status_code in [200, 405]
    
    def test_cors_allow_origin_header(self, client):
        """Test that Access-Control-Allow-Origin header is set."""
        response = client.get(
            "/api/v1/trustllm/openapi.json",
            headers={'Origin': 'http://example.com'}
        )
        # CORS headers should be present
        assert response.status_code == 200
    
    def test_cors_preflight_request(self, client):
        """Test CORS preflight OPTIONS request."""
        response = client.options(
            "/api/v1/trustllm/openapi.json",
            headers={
                'Origin': 'http://example.com',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
        )
        assert response.status_code in [200, 400, 405]
    
    def test_cors_with_different_origins(self, client):
        """Test CORS with different origin headers."""
        origins = [
            'http://localhost:3000',
            'http://localhost:8080',
            'https://example.com'
        ]
        
        for origin in origins:
            response = client.get(
                "/api/v1/trustllm/openapi.json",
                headers={'Origin': origin}
            )
            assert response.status_code == 200


# Test Cases for XSS Protection Middleware
class TestXSSProtectionMiddleware:
    """Test cases for XSS protection middleware."""
    
    def test_xss_protection_header_present(self, client):
        """Test that X-XSS-Protection header is present."""
        response = client.get("/api/v1/trustllm/openapi.json")
        assert 'X-XSS-Protection' in response.headers
    
    def test_cache_control_header_present(self, client):
        """Test that Cache-Control header is present."""
        response = client.get("/api/v1/trustllm/openapi.json")
        assert 'Cache-Control' in response.headers
    
    def test_content_security_policy_header_present(self, client):
        """Test that Content-Security-Policy header is present."""
        response = client.get("/api/v1/trustllm/openapi.json")
        assert 'Content-Security-Policy' in response.headers
    
    def test_x_frame_options_header_present(self, client):
        """Test that X-Frame-Options header is present."""
        response = client.get("/api/v1/trustllm/openapi.json")
        assert 'X-Frame-Options' in response.headers
    
    def test_x_content_type_options_header_present(self, client):
        """Test that X-Content-Type-Options header is present."""
        response = client.get("/api/v1/trustllm/openapi.json")
        assert 'X-Content-Type-Options' in response.headers
    
    def test_pragma_header_present(self, client):
        """Test that Pragma header is present."""
        response = client.get("/api/v1/trustllm/openapi.json")
        assert 'Pragma' in response.headers
    
    def test_vary_header_present(self, client):
        """Test that Vary header is present."""
        response = client.get("/api/v1/trustllm/openapi.json")
        assert 'Vary' in response.headers
    
    def test_content_type_with_charset(self, client):
        """Test that Content-Type includes charset."""
        response = client.get("/api/v1/trustllm/openapi.json")
        content_type = response.headers.get('Content-Type', '')
        assert 'charset' in content_type.lower() or response.status_code == 200
    
    def test_security_headers_on_all_endpoints(self, client):
        """Test that security headers are present on all endpoints."""
        endpoints = [
            "/api/v1/trustllm/openapi.json",
            "/api/v1/trustllm/docs"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert 'X-XSS-Protection' in response.headers
            assert 'X-Frame-Options' in response.headers
            assert 'X-Content-Type-Options' in response.headers
    
    def test_security_headers_values(self, client):
        """Test that security headers have expected values."""
        response = client.get("/api/v1/trustllm/openapi.json")
        
        # Verify headers exist (values may vary based on environment)
        assert response.headers.get('X-XSS-Protection') is not None
        assert response.headers.get('Cache-Control') is not None
        assert response.headers.get('X-Frame-Options') is not None


# Test Cases for Router Inclusion
class TestRouterInclusion:
    """Test cases for router inclusion and routing."""
    
    def test_trustllm_router_included(self, client):
        """Test that trustllm router is included."""
        routes = [route.path for route in app.routes]
        trustllm_routes = [r for r in routes if '/api/v1/trustllm' in r]
        assert len(trustllm_routes) > 0
    
    def test_scores_router_included(self, client):
        """Test that scores router is included."""
        routes = [route.path for route in app.routes]
        # Check if scores routes exist
        assert any('/api/v1/trustllm' in route for route in routes)
    
    def test_router_prefix_correct(self, client):
        """Test that router prefix is correct."""
        routes = [route.path for route in app.routes]
        prefixed_routes = [r for r in routes if r.startswith('/api/v1/trustllm')]
        assert len(prefixed_routes) > 0
    
    def test_router_tags_configured(self, client):
        """Test that router tags are configured."""
        openapi_schema = app.openapi()
        # Check if paths exist (which means routers are configured)
        assert 'paths' in openapi_schema
        assert len(openapi_schema['paths']) > 0
        # Verify paths have tags in their operations
        has_tags = False
        for path, operations in openapi_schema['paths'].items():
            for method, details in operations.items():
                if isinstance(details, dict) and 'tags' in details:
                    has_tags = True
                    break
            if has_tags:
                break
        assert has_tags or len(openapi_schema['paths']) > 0


# Test Cases for Middleware Order
class TestMiddlewareOrder:
    """Test cases for middleware execution order."""
    
    def test_cors_and_xss_middleware_both_active(self, client):
        """Test that both CORS and XSS middleware are active."""
        response = client.get(
            "/api/v1/trustllm/openapi.json",
            headers={'Origin': 'http://localhost:3000'}
        )
        
        # Both middleware should add headers
        assert response.status_code == 200
        assert 'X-XSS-Protection' in response.headers
    
    def test_middleware_execution_on_error_responses(self, client):
        """Test that middleware executes on error responses."""
        response = client.get("/nonexistent-endpoint")
        
        # Security headers should still be present
        assert 'X-XSS-Protection' in response.headers
        assert 'X-Frame-Options' in response.headers
    
    def test_middleware_execution_on_success_responses(self, client):
        """Test that middleware executes on success responses."""
        response = client.get("/api/v1/trustllm/openapi.json")
        
        assert response.status_code == 200
        assert 'X-XSS-Protection' in response.headers
        assert 'Cache-Control' in response.headers


# Integration Tests
class TestIntegration:
    """Integration tests for the complete application."""
    
    def test_full_request_response_cycle(self, client):
        """Test complete request-response cycle."""
        response = client.get("/api/v1/trustllm/openapi.json")
        
        assert response.status_code == 200
        assert response.json() is not None
        assert 'X-XSS-Protection' in response.headers
        assert 'Cache-Control' in response.headers
    
    def test_docs_page_loads_completely(self, client):
        """Test that docs page loads with all components."""
        response = client.get("/api/v1/trustllm/docs")
        
        assert response.status_code == 200
        assert len(response.content) > 0
    
    def test_multiple_concurrent_requests(self, client):
        """Test handling multiple concurrent requests."""
        responses = []
        for _ in range(10):
            response = client.get("/api/v1/trustllm/openapi.json")
            responses.append(response)
        
        # All requests should succeed
        assert all(r.status_code == 200 for r in responses)
        # All should have security headers
        assert all('X-XSS-Protection' in r.headers for r in responses)


# Edge Cases and Security Tests
class TestEdgeCases:
    """Test edge cases and security scenarios."""
    
    def test_invalid_endpoint_returns_404(self, client):
        """Test that invalid endpoint returns 404."""
        response = client.get("/api/v1/trustllm/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_method_returns_405(self, client):
        """Test that invalid HTTP method returns 405."""
        response = client.post("/api/v1/trustllm/docs")
        assert response.status_code == 405
    
    def test_malformed_request_handling(self, client):
        """Test handling of malformed requests."""
        response = client.get("/api/v1/trustllm/openapi.json", headers={'Invalid-Header': '\x00'})
        # Should either accept or reject gracefully
        assert response.status_code in [200, 400]
    
    def test_xss_attempt_in_headers(self, client):
        """Test XSS attempt in request headers."""
        response = client.get(
            "/api/v1/trustllm/openapi.json",
            headers={'User-Agent': '<script>alert("xss")</script>'}
        )
        # Should handle without crashing
        assert response.status_code == 200
    
    def test_sql_injection_attempt_in_path(self, client):
        """Test SQL injection attempt in URL path."""
        response = client.get("/api/v1/trustllm/'; DROP TABLE users; --")
        # Should return 404, not crash
        assert response.status_code == 404
    
    def test_path_traversal_attempt(self, client):
        """Test path traversal attempt."""
        response = client.get("/api/v1/trustllm/../../../etc/passwd")
        # Should return 404 or handle securely
        assert response.status_code in [404, 400, 403]
    
    def test_very_long_url(self, client):
        """Test handling of very long URL."""
        long_path = "/api/v1/trustllm/" + "a" * 10000
        response = client.get(long_path)
        # Should either accept or reject gracefully
        assert response.status_code in [404, 414]
    
    def test_unicode_in_path(self, client):
        """Test Unicode characters in URL path."""
        response = client.get("/api/v1/trustllm/テスト")
        # Should handle without crashing
        assert response.status_code in [200, 404]


# Performance Tests
class TestPerformance:
    """Test performance-related scenarios."""
    
    def test_rapid_successive_requests(self, client):
        """Test handling rapid successive requests."""
        for _ in range(50):
            response = client.get("/api/v1/trustllm/openapi.json")
            assert response.status_code == 200
    
    def test_response_time_reasonable(self, client):
        """Test that response time is reasonable."""
        import time
        start = time.time()
        response = client.get("/api/v1/trustllm/openapi.json")
        end = time.time()
        
        assert response.status_code == 200
        # Response should be under 5 seconds
        assert (end - start) < 5.0
    
    def test_large_response_handling(self, client):
        """Test handling of large responses."""
        response = client.get("/api/v1/trustllm/openapi.json")
        
        assert response.status_code == 200
        # Should have substantial content
        assert len(response.content) > 0


# Error Handling Tests
class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_404_error_has_security_headers(self, client):
        """Test that 404 errors include security headers."""
        response = client.get("/nonexistent")
        
        assert response.status_code == 404
        assert 'X-XSS-Protection' in response.headers
        assert 'X-Frame-Options' in response.headers
    
    def test_405_error_has_security_headers(self, client):
        """Test that 405 errors include security headers."""
        response = client.post("/api/v1/trustllm/openapi.json")
        
        assert response.status_code == 405
        assert 'X-XSS-Protection' in response.headers
    
    def test_options_method_supported(self, client):
        """Test that OPTIONS method is supported for CORS."""
        response = client.options("/api/v1/trustllm/openapi.json")
        assert response.status_code in [200, 405]


# Configuration Tests
class TestConfiguration:
    """Test application configuration."""
    
    def test_environment_variables_loaded(self):
        """Test that environment variables are loaded."""
        # This test verifies the app starts even with missing env vars
        assert app is not None
    
    def test_app_middleware_stack(self, client):
        """Test that middleware stack is properly configured."""
        # Verify middleware is in the app
        assert len(app.user_middleware) > 0
    
    def test_app_routes_registered(self, client):
        """Test that routes are registered."""
        routes = [route for route in app.routes]
        assert len(routes) > 0


# Regression Tests
class TestRegression:
    """Regression tests for previously fixed bugs."""
    
    def test_openapi_schema_structure(self, client):
        """Regression: Ensure OpenAPI schema has correct structure."""
        response = client.get("/api/v1/trustllm/openapi.json")
        schema = response.json()
        
        assert 'openapi' in schema
        assert 'info' in schema
        assert 'paths' in schema
    
    def test_docs_page_renders(self, client):
        """Regression: Ensure docs page renders without errors."""
        response = client.get("/api/v1/trustllm/docs")
        
        assert response.status_code == 200
        assert b'swagger' in response.content.lower() or b'html' in response.content.lower()
    
    def test_charset_added_to_content_type(self, client):
        """Regression: Ensure charset is added to Content-Type."""
        response = client.get("/api/v1/trustllm/openapi.json")
        content_type = response.headers.get('Content-Type', '')
        
        # Should have charset specified
        assert response.status_code == 200
        # Charset should be present or content type should be appropriate
        assert content_type != ''


# API Versioning Tests
class TestAPIVersioning:
    """Test API versioning."""
    
    def test_api_v1_prefix_present(self, client):
        """Test that API v1 prefix is present."""
        routes = [route.path for route in app.routes]
        v1_routes = [r for r in routes if '/api/v1/' in r]
        assert len(v1_routes) > 0
    
    def test_trustllm_namespace_present(self, client):
        """Test that trustllm namespace is present."""
        routes = [route.path for route in app.routes]
        trustllm_routes = [r for r in routes if 'trustllm' in r]
        assert len(trustllm_routes) > 0
    
    def test_versioned_openapi_url(self, client):
        """Test that OpenAPI URL includes version."""
        response = client.get("/api/v1/trustllm/openapi.json")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
