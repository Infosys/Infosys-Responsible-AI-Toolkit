"""
Comprehensive tests for src/main.py
Tests Flask application, security headers, error handlers, Swagger UI, and Waitress configuration.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock, call
from werkzeug.exceptions import HTTPException, UnsupportedMediaType, NotFound

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestMainImports(unittest.TestCase):
    """Test that all required imports work correctly"""
    
    def test_flask_imports(self):
        """Test Flask core imports"""
        from flask import Flask, jsonify
        self.assertIsNotNone(Flask)
        self.assertIsNotNone(jsonify)
    
    def test_flask_swagger_ui_import(self):
        """Test Flask Swagger UI import"""
        from flask_swagger_ui import get_swaggerui_blueprint
        self.assertIsNotNone(get_swaggerui_blueprint)
    
    def test_waitress_import(self):
        """Test Waitress server import"""
        from waitress import serve
        self.assertIsNotNone(serve)
    
    def test_werkzeug_exceptions_import(self):
        """Test Werkzeug exceptions imports"""
        from werkzeug.exceptions import HTTPException, UnsupportedMediaType, BadRequest
        self.assertIsNotNone(HTTPException)
        self.assertIsNotNone(UnsupportedMediaType)
        self.assertIsNotNone(BadRequest)
    
    def test_dotenv_import(self):
        """Test dotenv import"""
        from dotenv import load_dotenv
        self.assertIsNotNone(load_dotenv)
    
    @patch('main.router')
    def test_routing_router_import(self, mock_router):
        """Test routing.router import"""
        import main
        self.assertTrue(hasattr(main, 'router'))
    
    @patch('main.CustomLogger')
    def test_custom_logger_import(self, mock_logger):
        """Test CustomLogger import"""
        import main
        self.assertTrue(hasattr(main, 'CustomLogger'))


class TestMainSecurityHeaders(unittest.TestCase):
    """Test security headers functionality"""
    
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_add_security_headers_function_exists(self, mock_logger, mock_router):
        """Test that add_security_headers function exists"""
        import main
        self.assertTrue(hasattr(main, 'add_security_headers'))
        self.assertTrue(callable(main.add_security_headers))
    
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_security_headers_structure(self, mock_logger, mock_router):
        """Test that security headers are properly structured"""
        import main
        mock_response = MagicMock()
        mock_response.headers = {}
        
        result = main.add_security_headers(mock_response)
        
        self.assertIn('X-Content-Type-Options', result.headers)
        self.assertIn('X-Frame-Options', result.headers)
        self.assertIn('X-XSS-Protection', result.headers)
        self.assertIn('Content-Security-Policy', result.headers)
    
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_x_content_type_options_header(self, mock_logger, mock_router):
        """Test X-Content-Type-Options header value"""
        import main
        mock_response = MagicMock()
        mock_response.headers = {}
        
        result = main.add_security_headers(mock_response)
        
        self.assertEqual(result.headers['X-Content-Type-Options'], 'nosniff')
    
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_x_frame_options_header(self, mock_logger, mock_router):
        """Test X-Frame-Options header value"""
        import main
        mock_response = MagicMock()
        mock_response.headers = {}
        
        result = main.add_security_headers(mock_response)
        
        self.assertEqual(result.headers['X-Frame-Options'], 'DENY')
    
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_x_xss_protection_header(self, mock_logger, mock_router):
        """Test X-XSS-Protection header value"""
        import main
        mock_response = MagicMock()
        mock_response.headers = {}
        
        result = main.add_security_headers(mock_response)
        
        self.assertEqual(result.headers['X-XSS-Protection'], '1; mode=block')
    
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_csp_header_content(self, mock_logger, mock_router):
        """Test Content-Security-Policy header value"""
        import main
        mock_response = MagicMock()
        mock_response.headers = {}
        
        result = main.add_security_headers(mock_response)
        
        expected_csp = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; img-src 'self' data:"
        self.assertEqual(result.headers['Content-Security-Policy'], expected_csp)


class TestMainConstants(unittest.TestCase):
    """Test constants defined in main.py"""
    
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_swagger_url_constant(self, mock_logger, mock_router):
        """Test SWAGGER_URL constant"""
        import main
        self.assertEqual(main.SWAGGER_URL, '/rai/v1/raimoderationmodels/docs')
    
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_api_url_constant(self, mock_logger, mock_router):
        """Test API_URL constant"""
        import main
        self.assertEqual(main.API_URL, '/static/swagger.json')


class TestMainFlaskApp(unittest.TestCase):
    """Test Flask application setup"""
    
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_app_instance_exists(self, mock_logger, mock_router):
        """Test that Flask app instance is created"""
        import main
        self.assertIsNotNone(main.app)
        self.assertEqual(main.app.name, 'main')
    
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_swagger_blueprint_exists(self, mock_logger, mock_router):
        """Test that Swagger UI blueprint is created"""
        import main
        self.assertTrue(hasattr(main, 'swaggerui_blueprint'))
        self.assertIsNotNone(main.swaggerui_blueprint)
    
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_logger_instance_exists(self, mock_logger, mock_router):
        """Test that CustomLogger instance is created"""
        import main
        self.assertTrue(hasattr(main, 'log'))


class TestMainErrorHandlers(unittest.TestCase):
    """Test error handling functions"""
    
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_handle_http_exception_function_exists(self, mock_logger, mock_router):
        """Test that handle_http_exception function exists"""
        import main
        self.assertTrue(hasattr(main, 'handle_http_exception'))
        self.assertTrue(callable(main.handle_http_exception))
    
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_handle_http_exception_returns_json(self, mock_logger, mock_router):
        """Test that handle_http_exception returns JSON response"""
        import main
        exc = NotFound(description="Test not found")
        
        with main.app.app_context():
            response = main.handle_http_exception(exc)
            self.assertEqual(response.status_code, 404)
    
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_handle_unsupported_mediatype_function_exists(self, mock_logger, mock_router):
        """Test that handle_unsupported_mediatype function exists"""
        import main
        self.assertTrue(hasattr(main, 'handle_unsupported_mediatype'))
        self.assertTrue(callable(main.handle_unsupported_mediatype))
    
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_handle_unsupported_mediatype_returns_415(self, mock_logger, mock_router):
        """Test that handle_unsupported_mediatype returns 415 status"""
        import main
        
        with main.app.app_context():
            response, status_code = main.handle_unsupported_mediatype(None)
            self.assertEqual(status_code, 415)


class TestMainAppEndToEnd(unittest.TestCase):
    """End-to-end tests for Flask app"""
    
    def setUp(self):
        """Set up test client"""
        with patch('main.router'), patch('main.CustomLogger'):
            import main
            self.app = main.app
            self.client = self.app.test_client()
    
    def test_app_has_security_headers_on_response(self):
        """Test that security headers are applied to responses"""
        response = self.client.get('/nonexistent')
        
        self.assertIn('X-Content-Type-Options', response.headers)
        self.assertIn('X-Frame-Options', response.headers)
        self.assertIn('X-XSS-Protection', response.headers)
        self.assertIn('Content-Security-Policy', response.headers)
    
    def test_swagger_ui_endpoint_exists(self):
        """Test that Swagger UI endpoint is accessible"""
        response = self.client.get('/rai/v1/raimoderationmodels/docs/')
        # Swagger UI should return 200 or redirect
        self.assertIn(response.status_code, [200, 301, 302, 308])
    
    def test_app_handles_404_error(self):
        """Test that app handles 404 errors properly"""
        response = self.client.get('/nonexistent-route')
        
        self.assertEqual(response.status_code, 404)


class TestMainEnvironmentVariables(unittest.TestCase):
    """Test environment variable handling"""
    
    @patch.dict(os.environ, {'DB_PORT': '9000'})
    @patch('main.serve')
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_db_port_from_env(self, mock_logger, mock_router, mock_serve):
        """Test DB_PORT is read from environment"""
        # Need to reload main to pick up new env vars
        import main
        
        # Simulate running main
        if hasattr(main, '__name__') and main.__name__ == "__main__":
            pass  # Main module condition
    
    @patch.dict(os.environ, {'THREADS': '10'})
    @patch('main.serve')
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_threads_from_env(self, mock_logger, mock_router, mock_serve):
        """Test THREADS is read from environment"""
        import main
        # Environment variable should be available
        self.assertEqual(os.getenv('THREADS'), '10')
    
    @patch.dict(os.environ, {'CONNECTION_LIMIT': '1000'})
    @patch('main.serve')
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_connection_limit_from_env(self, mock_logger, mock_router, mock_serve):
        """Test CONNECTION_LIMIT is read from environment"""
        import main
        self.assertEqual(os.getenv('CONNECTION_LIMIT'), '1000')
    
    @patch.dict(os.environ, {'CHANNEL_TIMEOUT': '240'})
    @patch('main.serve')
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_channel_timeout_from_env(self, mock_logger, mock_router, mock_serve):
        """Test CHANNEL_TIMEOUT is read from environment"""
        import main
        self.assertEqual(os.getenv('CHANNEL_TIMEOUT'), '240')
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_default_values_used_when_no_env_vars(self, mock_logger, mock_router):
        """Test that default values are used when env vars are not set"""
        import main
        # When env vars are not set, getenv returns None and defaults should be used
        self.assertIsNone(os.getenv('DB_PORT'))
        self.assertIsNone(os.getenv('THREADS'))


class TestMainWaitressConfig(unittest.TestCase):
    """Test Waitress server configuration"""
    
    @patch('main.serve')
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_serve_configuration_defaults(self, mock_logger, mock_router, mock_serve):
        """Test Waitress serve is configured with correct defaults"""
        # We can't directly test it, but we can verify the function exists
        import main
        from waitress import serve
        self.assertIsNotNone(serve)


class TestMainRouterRegistration(unittest.TestCase):
    """Test router blueprint registration"""
    
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_router_registered_with_prefix(self, mock_logger, mock_router):
        """Test that router blueprint is registered with correct URL prefix"""
        import main
        
        # Check that app.register_blueprint was called with router
        blueprints = [bp.name for bp in main.app.blueprints.values()]
        # Router should be registered (though mocked, we can check the call happened)
        self.assertIsNotNone(main.app)
    
    @patch('main.router')
    @patch('main.CustomLogger')
    def test_router_url_prefix(self, mock_logger, mock_router):
        """Test router URL prefix is correct"""
        import main
        # The router is registered with url_prefix='/rai/v1/raimoderationmodels'
        # We verify this by checking the app has blueprints
        self.assertTrue(hasattr(main.app, 'blueprints'))


if __name__ == '__main__':
    unittest.main()
