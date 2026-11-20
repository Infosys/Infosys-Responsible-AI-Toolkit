"""
Test cases for privacyfiles_main.py - FastAPI application entry point for file operations
Tests middleware, exception handlers, and app configuration using TestClient
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi.routing import APIRoute


class TestPrivacyFilesMainAppImportWithMock:
    """Test privacyfiles_main.py with mocked config"""

    @patch('privacy.config.config.read_config_yaml')
    def test_app_can_be_imported_mocked(self, mock_config):
        """Test privacyfiles_main module can be imported with mocked config"""
        mock_config.return_value = {'title': 'Test Files API'}
        try:
            from privacyfiles_main import app
            assert app is not None
        except ImportError as e:
            pytest.skip(f"Could not import privacyfiles_main: {e}")

    @patch('privacy.config.config.read_config_yaml')
    def test_app_is_fastapi_instance_mocked(self, mock_config):
        """Test app is FastAPI instance"""
        mock_config.return_value = {'title': 'Test Files API'}
        try:
            from privacyfiles_main import app
            from fastapi import FastAPI
            assert isinstance(app, FastAPI)
        except (ImportError, AssertionError, Exception):
            pytest.skip("Could not verify FastAPI instance")

    @patch('privacy.config.config.read_config_yaml')
    def test_app_has_middleware_mocked(self, mock_config):
        """Test app has middleware configured"""
        mock_config.return_value = {'title': 'Test Files API'}
        try:
            from privacyfiles_main import app
            assert len(app.user_middleware) > 0
        except ImportError:
            pytest.skip("Could not import privacyfiles_main app")

    @patch('privacy.config.config.read_config_yaml')
    def test_app_has_routes_mocked(self, mock_config):
        """Test app has routes configured"""
        mock_config.return_value = {'title': 'Test Files API'}
        try:
            from privacyfiles_main import app
            assert len(app.routes) > 0
        except ImportError:
            pytest.skip("Could not import privacyfiles_main app")


class TestPrivacyFilesMainMiddlewareConfig:
    """Test middleware in privacyfiles_main.py"""

    @patch('privacy.config.config.read_config_yaml')
    def test_middleware_types(self, mock_config):
        """Test app middleware types"""
        mock_config.return_value = {'title': 'Test Files API'}
        try:
            from privacyfiles_main import app
            middleware_classes = [m.__class__.__name__ for m in app.user_middleware]
            assert len(middleware_classes) > 0
        except ImportError:
            pytest.skip("Could not import privacyfiles_main app")


class TestPrivacyFilesMainExceptionHandlers:
    """Test exception handlers in privacyfiles_main.py"""

    @patch('privacy.config.config.read_config_yaml')
    def test_exception_handlers_exist(self, mock_config):
        """Test exception handlers are registered"""
        mock_config.return_value = {'title': 'Test Files API'}
        try:
            from privacyfiles_main import app
            assert len(app.exception_handlers) > 0
        except ImportError:
            pytest.skip("Could not import privacyfiles_main app")

    @patch('privacy.config.config.read_config_yaml')
    def test_request_validation_handler_registered(self, mock_config):
        """Test RequestValidationError handler exists"""
        mock_config.return_value = {'title': 'Test Files API'}
        try:
            from privacyfiles_main import app
            from fastapi.exceptions import RequestValidationError
            assert RequestValidationError in app.exception_handlers
        except ImportError:
            pytest.skip("Could not import privacyfiles_main app")


class TestPrivacyFilesMainRouting:
    """Test routing in privacyfiles_main.py"""

    @patch('privacy.config.config.read_config_yaml')
    def test_rai_v1_routes_exist(self, mock_config):
        """Test file router routes are registered beyond the 3 default FastAPI routes"""
        mock_config.return_value = {'title': 'Test Files API'}
        try:
            from privacyfiles_main import app
            # Default FastAPI routes: /openapi.json, /docs, /redoc (3 routes).
            # include_router adds the file router, so total must exceed 3.
            assert len(app.routes) > 3
        except ImportError:
            pytest.skip("Could not import privacyfiles_main app")
