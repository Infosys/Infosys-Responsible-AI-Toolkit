"""
Tests for telemetry services
"""
import pytest
from unittest.mock import Mock, MagicMock, patch


class TestAuthenticateTelemetryService:
    """Tests for TelemetryContent class"""

    @patch('rai_backend.service.authenticatetelemetryservice.TelemetryFlag.findall')
    def test_telemetry_content_getAlldata(self, mock_findall):
        """Test TelemetryContent.getAlldata method"""
        from rai_backend.service.authenticatetelemetryservice import TelemetryContent
        
        # Mock the database response
        mock_findall.return_value = [{"module": "auth", "flag": True}]
        
        result = TelemetryContent.getAlldata()
        
        mock_findall.assert_called_once_with({})
        assert result is not None

    @patch('rai_backend.service.authenticatetelemetryservice.TelemetryFlag.create')
    def test_telemetry_content_creation(self, mock_create):
        """Test TelemetryContent.creation method"""
        from rai_backend.service.authenticatetelemetryservice import TelemetryContent
        
        # Mock the database response
        mock_create.return_value = "success"
        
        payload = {"module": "auth", "flag": True}
        result = TelemetryContent.creation(payload)
        
        mock_create.assert_called_once_with(payload)
        assert result is not None

    @patch('rai_backend.service.authenticatetelemetryservice.TelemetryFlag.update')
    def test_telemetry_content_updation(self, mock_update):
        """Test TelemetryContent.updation method"""
        from rai_backend.service.authenticatetelemetryservice import TelemetryContent
        
        # Mock the database response
        mock_update.return_value = "success"
        
        payload = Mock()
        payload.Module = "auth"
        payload.TelemetryFlag = True
        
        result = TelemetryContent.updation(payload)
        
        mock_update.assert_called_once_with("auth", True)
        assert result is not None
