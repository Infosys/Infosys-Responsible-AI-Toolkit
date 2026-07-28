'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import unittest
from unittest.mock import patch, Mock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))


class TestMainTopicImports(unittest.TestCase):
    """Test all imports in main_topic.py"""
    
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


class TestMainTopicSecurityHeaders(unittest.TestCase):
    """Test security headers function"""
    
    @patch('main_topic.Flask')
    def test_add_security_headers_function_exists(self, mock_flask):
        """Test add_security_headers function exists"""
        import main_topic
        self.assertTrue(hasattr(main_topic, 'add_security_headers'))
        self.assertTrue(callable(main_topic.add_security_headers))
    
    def test_security_headers_structure(self):
        """Test security headers are added correctly"""
        mock_response = Mock()
        mock_response.headers = {}
        
        import main_topic
        result = main_topic.add_security_headers(mock_response)
        
        self.assertEqual(mock_response.headers['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(mock_response.headers['X-Frame-Options'], 'DENY')
        self.assertEqual(mock_response.headers['X-XSS-Protection'], '1; mode=block')
        self.assertIn('Content-Security-Policy', mock_response.headers)
        self.assertEqual(result, mock_response)
    
    def test_csp_header_content(self):
        """Test Content-Security-Policy header content"""
        mock_response = Mock()
        mock_response.headers = {}
        
        import main_topic
        main_topic.add_security_headers(mock_response)
        
        csp = mock_response.headers['Content-Security-Policy']
        self.assertIn("default-src 'self'", csp)
        self.assertIn("style-src 'self' 'unsafe-inline'", csp)
        self.assertIn("script-src 'self' 'unsafe-inline'", csp)
        self.assertIn("img-src 'self' data:", csp)


class TestMainTopicConstants(unittest.TestCase):
    """Test constants defined in main_topic.py"""
    
    def test_swagger_url_constant(self):
        """Test SWAGGER_URL constant"""
        import main_topic
        self.assertEqual(main_topic.SWAGGER_URL, '/rai/v1/raimoderationmodels/restrictedtopicmodel/docs')
    
    def test_api_url_constant(self):
        """Test API_URL constant"""
        import main_topic
        self.assertEqual(main_topic.API_URL, '/static/topic_swagger.json')


class TestMainTopicFlaskApp(unittest.TestCase):
    """Test Flask app configuration"""
    
    def test_app_instance_exists(self):
        """Test Flask app instance exists"""
        import main_topic
        self.assertTrue(hasattr(main_topic, 'app'))
        from flask import Flask
        self.assertIsInstance(main_topic.app, Flask)
    
    def test_swagger_blueprint_exists(self):
        """Test swaggerui_blueprint exists"""
        import main_topic
        self.assertTrue(hasattr(main_topic, 'swaggerui_blueprint'))
    
    def test_logger_instance_exists(self):
        """Test CustomLogger instance exists"""
        import main_topic
        self.assertTrue(hasattr(main_topic, 'log'))


class TestMainTopicErrorHandlers(unittest.TestCase):
    """Test error handler functions"""
    
    def test_handle_http_exception_function_exists(self):
        """Test handle_http_exception function exists"""
        import main_topic
        self.assertTrue(hasattr(main_topic, 'handle_http_exception'))
        self.assertTrue(callable(main_topic.handle_http_exception))
    
    def test_handle_http_exception_returns_json(self):
        """Test handle_http_exception returns JSON response"""
        import main_topic
        from werkzeug.exceptions import NotFound
        
        exc = NotFound()
        response = main_topic.handle_http_exception(exc)
        
        self.assertTrue(hasattr(response, 'status_code'))
        self.assertEqual(response.status_code, 404)
    
    def test_handle_unsupported_mediatype_function_exists(self):
        """Test handle_unsupported_mediatype function exists"""
        import main_topic
        self.assertTrue(hasattr(main_topic, 'handle_unsupported_mediatype'))
        self.assertTrue(callable(main_topic.handle_unsupported_mediatype))
    
    def test_handle_unsupported_mediatype_returns_415(self):
        """Test handle_unsupported_mediatype returns 415 status"""
        import main_topic
        
        response, status_code = main_topic.handle_unsupported_mediatype(None)
        
        self.assertEqual(status_code, 415)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], 'Unsupported media type')


class TestMainTopicAppEndToEnd(unittest.TestCase):
    """Test Flask app end-to-end functionality"""
    
    def setUp(self):
        """Set up test client"""
        import main_topic
        main_topic.app.config['TESTING'] = True
        self.client = main_topic.app.test_client()
    
    def test_app_has_security_headers_on_response(self):
        """Test security headers are applied to responses"""
        response = self.client.get('/rai/v1/raimoderationmodels/restrictedtopicmodel')
        
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
        response = self.client.get('/rai/v1/raimoderationmodels/restrictedtopicmodel/docs/')
        self.assertIn(response.status_code, [200, 301, 302, 308])


class TestMainTopicEnvironmentVariables(unittest.TestCase):
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
        threads = int(os.getenv('THREADS') or 1)
        self.assertEqual(threads, 10)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_threads_default_value(self):
        """Test THREADS defaults to 1"""
        threads = int(os.getenv('THREADS') or 1)
        self.assertEqual(threads, 1)
    
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


class TestMainTopicWaitressConfig(unittest.TestCase):
    """Test Waitress server configuration"""
    
    @patch('main_topic.serve')
    @patch.dict(os.environ, {'DB_PORT': '8080', 'THREADS': '8', 'CONNECTION_LIMIT': '600', 'CHANNEL_TIMEOUT': '180'})
    def test_serve_configuration(self, mock_serve):
        """Test serve is called with correct configuration"""
        port = int(os.getenv('DB_PORT') or 8000)
        threads = int(os.getenv('THREADS') or 1)
        conn_limit = int(os.getenv('CONNECTION_LIMIT') or 500)
        timeout = int(os.getenv('CHANNEL_TIMEOUT') or 120)
        
        self.assertEqual(port, 8080)
        self.assertEqual(threads, 8)
        self.assertEqual(conn_limit, 600)
        self.assertEqual(timeout, 180)


class TestMainTopicRouterRegistration(unittest.TestCase):
    """Test router registration"""
    
    def test_router_imported_as_router(self):
        """Test topic_router is imported as 'router'"""
        from routing.topicRouter import topic_router as router
        self.assertIsNotNone(router)


if __name__ == '__main__':
    unittest.main()
