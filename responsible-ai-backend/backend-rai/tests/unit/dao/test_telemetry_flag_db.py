"""
Tests for TelemetryFlagDb module
"""
import pytest
from unittest.mock import Mock, MagicMock, patch


class TestTelemetryFlagDb:
    """Tests for TelemetryFlag class"""

    @patch('rai_backend.dao.TelemetryFlagDb.TelemetryFlag.mycol')
    def test_findall_with_filter(self, mock_collection):
        """Test findall with filter"""
        from rai_backend.dao.TelemetryFlagDb import TelemetryFlag
        
        # Return a mock cursor that can be iterated
        mock_cursor = [{'Module': 'RaiBackend', 'TelemetryFlag': True}]
        mock_collection.find.return_value = mock_cursor
        
        result = TelemetryFlag.findall({'Module': 'RaiBackend'})
        
        assert isinstance(result, list)
        assert len(result) == 1

    @patch('rai_backend.dao.TelemetryFlagDb.mydb')
    def test_create_telemetry_flag(self, mock_db):
        """Test creating telemetry flag"""
        from rai_backend.dao.TelemetryFlagDb import TelemetryFlag
        
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.insert_one.return_value = MagicMock(inserted_id='123')
        
        result = TelemetryFlag.create({
            'Module': 'TestModule',
            'TelemetryFlag': False
        })
        
        assert result is not None

    @patch('rai_backend.dao.TelemetryFlagDb.TelemetryFlag.mycol')
    def test_update_telemetry_flag(self, mock_collection):
        """Test updating telemetry flag"""
        from rai_backend.dao.TelemetryFlagDb import TelemetryFlag
        
        mock_update_result = MagicMock()
        mock_update_result.acknowledged = True
        mock_collection.update_one.return_value = mock_update_result
        
        # Call with module name and value dict (as per actual implementation)
        result = TelemetryFlag.update('RaiBackend', {'TelemetryFlag': True})
        
        mock_collection.update_one.assert_called_once()
        assert result is True

    @patch('rai_backend.dao.TelemetryFlagDb.TelemetryFlag.mycol')
    def test_delete_telemetry_flag(self, mock_collection):
        """Test deleting telemetry flag"""
        from rai_backend.dao.TelemetryFlagDb import TelemetryFlag
        
        mock_collection.delete_many.return_value = MagicMock(deleted_count=1)
        
        # delete method has no return value
        TelemetryFlag.delete('TestModule')
        
        mock_collection.delete_many.assert_called_once_with({'Module': 'TestModule'})
