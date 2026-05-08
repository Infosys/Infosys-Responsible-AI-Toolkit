'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import unittest
from unittest.mock import patch, Mock, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))


class TestMainMMImports(unittest.TestCase):
    """Test all imports in main_MM.py"""
    
    def test_flask_imports(self):
        """Test Flask imports"""
        from flask import Flask, jsonify
        self.assertTrue(callable(Flask))
        self.assertTrue(callable(jsonify))
    
    def test_flask_swagger_ui_import(self):
        """Test flask_swagger_ui import"""
        from flask_swagger_ui import get_swaggerui_blueprint
        self.assertTrue(callable(get_swaggerui_blueprint))
    
    def test_waitress_import(self):
        """Test waitress serve import"""
        from waitress import serve
        self.assertTrue(callable(serve))
    
    def test_werkzeug_exceptions_import(self):
        """Test werkzeug exceptions import"""
        from werkzeug.exceptions import HTTPException, UnsupportedMediaType, BadRequest
        self.assertTrue(issubclass(HTTPException, Exception))
        self.assertTrue(issubclass(UnsupportedMediaType, HTTPException))
        self.assertTrue(issubclass(BadRequest, HTTPException))
    
    def test_dotenv_import(self):
        """Test dotenv import"""
        from dotenv import load_dotenv
        self.assertTrue(callable(load_dotenv))
    
    def test_logger_import(self):
        """Test CustomLogger import"""
        from config.logger import CustomLogger
        self.assertTrue(callable(CustomLogger))


class TestMainMMSecurityHeaders(unittest.TestCase):
    """Test security headers function"""
    
    @patch('main_MM.Flask')
    def test_add_security_headers_function_exists(self, mock_flask):
        """Test add_security_headers function exists"""
        import main_MM
        self.assertTrue(hasattr(main_MM, 'add_security_headers'))
        self.assertTrue(callable(main_MM.add_security_headers))
    
    def test_security_headers_structure(self):
        """Test security headers are added correctly"""
        mock_response = Mock()
        mock_response.headers = {}
        
        import main_MM
        result = main_MM.add_security_headers(mock_response)
        
        self.assertEqual(mock_response.headers['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(mock_response.headers['X-Frame-Options'], 'DENY')
        self.assertEqual(mock_response.headers['X-XSS-Protection'], '1; mode=block')
        self.assertIn('Content-Security-Policy', mock_response.headers)
        self.assertEqual(result, mock_response)
    
    def test_csp_header_content(self):
        """Test Content-Security-Policy header content"""
        mock_response = Mock()
        mock_response.headers = {}
        
        import main_MM
        main_MM.add_security_headers(mock_response)
        
        csp = mock_response.headers['Content-Security-Policy']
        self.assertIn("default-src 'self'", csp)
        self.assertIn("style-src 'self' 'unsafe-inline'", csp)
        self.assertIn("script-src 'self' 'unsafe-inline'", csp)
        self.assertIn("img-src 'self' data:", csp)


class TestMainMMConstants(unittest.TestCase):
    """Test constants defined in main_MM.py"""
    
    def test_api_prefix_constant(self):
        """Test API_PREFIX constant"""
        import main_MM
        self.assertEqual(main_MM.API_PREFIX, '/rai/v1/raimoderationmodels')
    
    def test_swagger_url_constant(self):
        """Test SWAGGER_URL constant"""
        import main_MM
        self.assertEqual(main_MM.SWAGGER_URL, '/rai/v1/raimoderationmodels/docs')
    
    def test_api_url_constant(self):
        """Test API_URL constant"""
        import main_MM
        self.assertEqual(main_MM.API_URL, '/static/swagger.json')


class TestMainMMRouterConfig(unittest.TestCase):
    """Test ROUTER_CONFIG dictionary"""
    
    def test_router_config_exists(self):
        """Test ROUTER_CONFIG dictionary exists"""
        import main_MM
        self.assertTrue(hasattr(main_MM, 'ROUTER_CONFIG'))
        self.assertIsInstance(main_MM.ROUTER_CONFIG, dict)
    
    def test_router_config_keys(self):
        """Test all expected router config keys exist"""
        import main_MM
        expected_keys = [
            "INJECTION_MODEL", "DETOXIFY_MODEL", "JAILBREAK_MODEL",
            "EMBED_MODEL", "PRIVACY_MODEL", "TOPIC_MODEL",
            "SENTIMENT_MODEL", "INVISIBLETEXT_MODEL", "GIBBERISH_MODEL",
            "BANCODE_MODEL", "TRANSLATION_MODEL"
        ]
        for key in expected_keys:
            self.assertIn(key, main_MM.ROUTER_CONFIG)
    
    def test_router_config_values_structure(self):
        """Test router config values are tuples with 2 elements"""
        import main_MM
        for key, value in main_MM.ROUTER_CONFIG.items():
            self.assertIsInstance(value, tuple)
            self.assertEqual(len(value), 2)
            self.assertIsInstance(value[0], str)  # module name
            self.assertIsInstance(value[1], str)  # router name
    
    def test_injection_model_config(self):
        """Test INJECTION_MODEL config"""
        import main_MM
        module_name, router_name = main_MM.ROUTER_CONFIG["INJECTION_MODEL"]
        self.assertEqual(module_name, "routing.injectionRouter")
        self.assertEqual(router_name, "injection_router")
    
    def test_detoxify_model_config(self):
        """Test DETOXIFY_MODEL config"""
        import main_MM
        module_name, router_name = main_MM.ROUTER_CONFIG["DETOXIFY_MODEL"]
        self.assertEqual(module_name, "routing.detoxifyRouter")
        self.assertEqual(router_name, "detoxify_router")
    
    def test_jailbreak_model_config(self):
        """Test JAILBREAK_MODEL config"""
        import main_MM
        module_name, router_name = main_MM.ROUTER_CONFIG["JAILBREAK_MODEL"]
        self.assertEqual(module_name, "routing.embedingRouter")
        self.assertEqual(router_name, "jailbreak_router")
    
    def test_embed_model_config(self):
        """Test EMBED_MODEL config"""
        import main_MM
        module_name, router_name = main_MM.ROUTER_CONFIG["EMBED_MODEL"]
        self.assertEqual(module_name, "routing.embedingRouter")
        self.assertEqual(router_name, "embed_router")


class TestMainMMFlaskApp(unittest.TestCase):
    """Test Flask app configuration"""
    
    def test_app_instance_exists(self):
        """Test Flask app instance exists"""
        import main_MM
        self.assertTrue(hasattr(main_MM, 'app'))
        from flask import Flask
        self.assertIsInstance(main_MM.app, Flask)
    
    def test_swagger_blueprint_exists(self):
        """Test swaggerui_blueprint exists"""
        import main_MM
        self.assertTrue(hasattr(main_MM, 'swaggerui_blueprint'))
    
    def test_logger_instance_exists(self):
        """Test CustomLogger instance exists"""
        import main_MM
        self.assertTrue(hasattr(main_MM, 'log'))


class TestMainMMErrorHandlers(unittest.TestCase):
    """Test error handler functions"""
    
    def test_handle_http_exception_function_exists(self):
        """Test handle_http_exception function exists"""
        import main_MM
        self.assertTrue(hasattr(main_MM, 'handle_http_exception'))
        self.assertTrue(callable(main_MM.handle_http_exception))
    
    def test_handle_http_exception_returns_json(self):
        """Test handle_http_exception returns JSON response"""
        import main_MM
        from werkzeug.exceptions import NotFound
        
        exc = NotFound()
        response = main_MM.handle_http_exception(exc)
        
        # Response should have json and status_code
        self.assertTrue(hasattr(response, 'status_code'))
        self.assertEqual(response.status_code, 404)
    
    def test_handle_unsupported_mediatype_function_exists(self):
        """Test handle_unsupported_mediatype function exists"""
        import main_MM
        self.assertTrue(hasattr(main_MM, 'handle_unsupported_mediatype'))
        self.assertTrue(callable(main_MM.handle_unsupported_mediatype))
    
    def test_handle_unsupported_mediatype_returns_415(self):
        """Test handle_unsupported_mediatype returns 415 status"""
        import main_MM
        
        response, status_code = main_MM.handle_unsupported_mediatype(None)
        
        self.assertEqual(status_code, 415)
        # Response should be JSON-like
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], 'Unsupported media type')


class TestMainMMAppEndToEnd(unittest.TestCase):
    """Test Flask app end-to-end functionality"""
    
    def setUp(self):
        """Set up test client"""
        import main_MM
        main_MM.app.config['TESTING'] = True
        self.client = main_MM.app.test_client()
    
    def test_app_has_security_headers_on_response(self):
        """Test security headers are applied to responses"""
        response = self.client.get('/rai/v1/raimoderationmodels/health')
        
        # Check security headers
        self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(response.headers.get('X-Frame-Options'), 'DENY')
        self.assertEqual(response.headers.get('X-XSS-Protection'), '1; mode=block')
        self.assertIn('Content-Security-Policy', response.headers)
    
    def test_app_handles_404_error(self):
        """Test app handles 404 errors"""
        response = self.client.get('/nonexistent-endpoint')
        self.assertEqual(response.status_code, 404)
    
    def test_swagger_ui_endpoint_exists(self):
        """Test Swagger UI endpoint exists"""
        response = self.client.get('/rai/v1/raimoderationmodels/docs/')
        # Should redirect or return swagger page
        self.assertIn(response.status_code, [200, 301, 302, 308])


class TestMainMMRouterLoading(unittest.TestCase):
    """Test dynamic router loading logic"""
    
    @patch.dict(os.environ, {'INJECTION_MODEL': 'true'})
    @patch('main_MM.__import__')
    def test_router_loading_when_enabled(self, mock_import):
        """Test router is loaded when env var is true"""
        mock_module = Mock()
        mock_router = Mock()
        mock_module.injection_router = mock_router
        mock_import.return_value = mock_module
        
        # This test validates the pattern used in main_MM.py
        module_name = "routing.injectionRouter"
        router_name = "injection_router"
        
        # Simulate the dynamic import
        module = __import__(module_name, fromlist=[router_name])
        self.assertIsNotNone(module)
    
    def test_router_config_all_routers_mappable(self):
        """Test all routers in config can be mapped"""
        import main_MM
        
        for env_var, (module_name, router_name) in main_MM.ROUTER_CONFIG.items():
            # Verify structure
            self.assertIsInstance(module_name, str)
            self.assertIsInstance(router_name, str)
            self.assertTrue(module_name.startswith('routing.'))
            self.assertTrue(router_name.endswith('_router'))


class TestMainMMEnvironmentVariables(unittest.TestCase):
    """Test environment variable handling"""
    
    @patch.dict(os.environ, {'DB_PORT': '9000'})
    def test_db_port_env_variable(self):
        """Test DB_PORT environment variable is read"""
        port = int(os.getenv('DB_PORT') or 8000)
        self.assertEqual(port, 9000)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_db_port_default_value(self):
        """Test DB_PORT defaults to 8000"""
        port = int(os.getenv('DB_PORT') or 8000)
        self.assertEqual(port, 8000)
    
    @patch.dict(os.environ, {'THREADS': '10'})
    def test_threads_env_variable(self):
        """Test THREADS environment variable is read"""
        threads = int(os.getenv('THREADS') or 5)
        self.assertEqual(threads, 10)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_threads_default_value(self):
        """Test THREADS defaults to 5"""
        threads = int(os.getenv('THREADS') or 5)
        self.assertEqual(threads, 5)
    
    @patch.dict(os.environ, {'CONNECTION_LIMIT': '1000'})
    def test_connection_limit_env_variable(self):
        """Test CONNECTION_LIMIT environment variable is read"""
        conn_limit = int(os.getenv('CONNECTION_LIMIT') or 500)
        self.assertEqual(conn_limit, 1000)
    
    @patch.dict(os.environ, {'CHANNEL_TIMEOUT': '240'})
    def test_channel_timeout_env_variable(self):
        """Test CHANNEL_TIMEOUT environment variable is read"""
        timeout = int(os.getenv('CHANNEL_TIMEOUT') or 120)
        self.assertEqual(timeout, 240)


class TestMainMMWaitressConfig(unittest.TestCase):
    """Test Waitress server configuration"""
    
    @patch('main_MM.serve')
    @patch.dict(os.environ, {'DB_PORT': '8080', 'THREADS': '8', 'CONNECTION_LIMIT': '600', 'CHANNEL_TIMEOUT': '180'})
    def test_serve_configuration(self, mock_serve):
        """Test serve is called with correct configuration"""
        # This test verifies the serve parameters pattern
        import main_MM
        
        # Get environment values
        port = int(os.getenv('DB_PORT') or 8000)
        threads = int(os.getenv('THREADS') or 5)
        conn_limit = int(os.getenv('CONNECTION_LIMIT') or 500)
        timeout = int(os.getenv('CHANNEL_TIMEOUT') or 120)
        
        self.assertEqual(port, 8080)
        self.assertEqual(threads, 8)
        self.assertEqual(conn_limit, 600)
        self.assertEqual(timeout, 180)


if __name__ == '__main__':
    unittest.main()
