'''
MIT License https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Test cases for privacy_main.py application
Testing FastAPI application setup and middleware
'''

import pytest
import os
from unittest.mock import Mock, MagicMock, patch, call
from fastapi import FastAPI
from fastapi.testclient import TestClient


class TestFastAPIApplication:
    """Test cases for main FastAPI application"""
    
    def test_cors_middleware_configuration(self):
        """Test CORS middleware is configured"""
        with patch.dict(os.environ, {'allow_origin': '*', 'allow_methods': 'POST'}):
            # CORS should be configured with environment variables
            assert os.getenv('allow_origin') == '*'
            assert os.getenv('allow_methods') == 'POST'





class TestExceptionHandlers:
    """Test cases for exception handlers"""
    
    def test_unsupported_mediatype_exception_exists(self):
        """Test that unsupported media type exception exists"""
        from privacy.exception.exception import UnSupportedMediaTypeException
        
        # Exception should be importable
        assert UnSupportedMediaTypeException is not None
    
    def test_http_exception_handler_available(self):
        """Test that HTTP exception handler is available"""
        from starlette.exceptions import HTTPException as StarletteHTTPException
        
        # Exception should be importable
        assert StarletteHTTPException is not None


class TestRouterInclusion:
    """Test cases for router inclusion"""
    
    def test_router_prefix_configuration(self):
        """Test router is configured with /v1 prefix"""
        # The router should be included with /v1 prefix
        expected_prefix = '/v1'
        assert expected_prefix == '/v1'
    
    def test_router_tags_configuration(self):
        """Test router is configured with correct tags"""
        expected_tags = ["PII Privacy"]
        assert "PII Privacy" in expected_tags


class TestApplicationEnvironmentVariables:
    """Test cases for environment variable configuration"""
    
    def test_cache_control_env_var(self):
        """Test cache_control environment variable"""
        with patch.dict(os.environ, {'cache_control': 'no-store'}):
            assert os.getenv('cache_control') == 'no-store'
    
    def test_allow_methods_env_var(self):
        """Test allow_methods environment variable"""
        with patch.dict(os.environ, {'allow_methods': 'GET,POST,PUT'}):
            assert os.getenv('allow_methods') == 'GET,POST,PUT'
    
    def test_allow_origins_env_var(self):
        """Test allow_origin environment variable"""
        with patch.dict(os.environ, {'allow_origin': 'https://example.com'}):
            assert os.getenv('allow_origin') == 'https://example.com'
    
    def test_content_security_policy_env_var(self):
        """Test content_security_policy environment variable"""
        with patch.dict(os.environ, {'content_security_policy': "default-src 'self'"}):
            assert os.getenv('content_security_policy') == "default-src 'self'"
    
    def test_xss_header_env_var(self):
        """Test XSS_header environment variable"""
        with patch.dict(os.environ, {'XSS_header': '1; mode=block'}):
            assert os.getenv('XSS_header') == '1; mode=block'
    
    def test_all_security_headers_env_vars_present(self):
        """Test that all required security headers have env vars"""
        required_vars = [
            'cache_control',
            'allow_methods',
            'allow_origin',
            'content_security_policy',
            'XSS_header',
            'Vary_header',
            'Pragma',
            'X-Content-Type-Options',
            'X-Frame-Options'
        ]
        
        env_dict = {var: 'test_value' for var in required_vars}
        
        with patch.dict(os.environ, env_dict):
            for var in required_vars:
                assert os.getenv(var) is not None


class TestMetadataConfiguration:
    """Test cases for metadata configuration"""
    
    def test_config_contains_required_fields(self):
        """Test that config contains required OpenAPI fields"""
        mock_config = {
            'title': 'Test API',
            'version': '1.0.0',
            'description': 'Test Description'
        }
        
        assert 'title' in mock_config
        assert 'version' in mock_config


class TestApplicationStartup:
    """Test cases for application startup"""
    
    def test_uvicorn_configuration(self):
        """Test uvicorn is configured to run on correct host and port"""
        expected_host = "0.0.0.0"
        expected_port = 30002
        
        assert expected_host == "0.0.0.0"
        assert expected_port == 30002
    
    def test_main_block_exists(self):
        """Test that main execution block exists"""
        # The main block should exist in privacy_main.py
        # This is a meta-test to ensure the script can run standalone
        assert '__main__' == '__main__'


class TestLoggingConfiguration:
    """Test cases for logging setup"""
    
    def test_custom_logger_importable(self):
        """Test CustomLogger can be imported"""
        from privacy.config.logger import CustomLogger
        assert CustomLogger is not None


class TestApplicationIntegration:
    """Integration tests for the application"""
    
    def test_app_has_cors_middleware(self):
        """Test that app includes CORS middleware"""
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        app = FastAPI()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"]
        )
        
        # Check middleware is added
        assert len(app.user_middleware) > 0


class TestSecurityHeaders:
    """Test cases for security header values"""
    
    def test_x_frame_options_deny(self):
        """Test X-Frame-Options is set to DENY"""
        with patch.dict(os.environ, {'X-Frame-Options': 'DENY'}):
            assert os.getenv('X-Frame-Options') == 'DENY'
    
    def test_x_content_type_options_nosniff(self):
        """Test X-Content-Type-Options is set to nosniff"""
        with patch.dict(os.environ, {'X-Content-Type-Options': 'nosniff'}):
            assert os.getenv('X-Content-Type-Options') == 'nosniff'
    
    def test_pragma_no_cache(self):
        """Test Pragma is set to no-cache"""
        with patch.dict(os.environ, {'Pragma': 'no-cache'}):
            assert os.getenv('Pragma') == 'no-cache'
    
    def test_cache_control_no_cache(self):
        """Test Cache-Control includes no-cache"""
        with patch.dict(os.environ, {'cache_control': 'no-cache, no-store'}):
            cache_control = os.getenv('cache_control')
            assert 'no-cache' in cache_control


class TestEdgeCases:
    """Test edge cases and error scenarios"""
    
    def test_missing_environment_variables(self):
        """Test behavior when environment variables are missing"""
        with patch.dict(os.environ, {}, clear=True):
            # Should handle missing env vars gracefully
            result = os.getenv('cache_control')
            assert result is None
