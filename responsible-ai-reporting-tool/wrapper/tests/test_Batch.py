import sys
import os
import pytest
from unittest.mock import Mock, MagicMock, patch

# Add src to path for imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.dao.Batch import Batch


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_collection():
    """Fixture to mock Batch.collection"""
    with patch.object(Batch, 'collection') as mock_col:
        yield mock_col


# ============================================================================
# Test Batch.find_tenet_id
# ============================================================================

class TestBatchFindTenetId:
    """Test Batch.find_tenet_id method"""
    
    def test_find_tenet_id_valid_batch_id(self, mock_collection):
        """Test finding TenetId with valid batch_id"""
        batch_id = 123.0
        expected_tenet_id = 1.0
        
        mock_collection.find_one.return_value = {"TenetId": expected_tenet_id}
        
        result = Batch.find_tenet_id(batch_id)
        
        assert result == expected_tenet_id
        mock_collection.find_one.assert_called_once_with(
            {"BatchId": batch_id}, 
            {"_id": 0, "TenetId": 1}
        )
    
    def test_find_tenet_id_none_batch_id(self):
        """Test with None batch_id"""
        with pytest.raises(ValueError, match="Batch ID must be a non-empty float"):
            Batch.find_tenet_id(None)
    
    def test_find_tenet_id_invalid_type_string(self):
        """Test with string instead of float"""
        with pytest.raises(ValueError, match="Batch ID must be a non-empty float"):
            Batch.find_tenet_id("123")
    
    def test_find_tenet_id_invalid_type_int(self):
        """Test with int instead of float"""
        with pytest.raises(ValueError, match="Batch ID must be a non-empty float"):
            Batch.find_tenet_id(123)
    
    def test_find_tenet_id_invalid_type_dict(self):
        """Test with dict instead of float"""
        with pytest.raises(ValueError, match="Batch ID must be a non-empty float"):
            Batch.find_tenet_id({"batch": 123})
    
    def test_find_tenet_id_database_error(self, mock_collection):
        """Test database error during find_one"""
        batch_id = 123.0
        
        mock_collection.find_one.side_effect = Exception("Database connection error")
        
        with pytest.raises(ValueError, match="Invalid BatchId"):
            Batch.find_tenet_id(batch_id)
    
    def test_find_tenet_id_not_found(self, mock_collection):
        """Test when batch_id is not found in database"""
        batch_id = 999.0
        
        mock_collection.find_one.return_value = None
        
        with pytest.raises(ValueError, match="Invalid BatchId"):
            Batch.find_tenet_id(batch_id)
    
    def test_find_tenet_id_missing_tenet_field(self, mock_collection):
        """Test when result doesn't have TenetId field"""
        batch_id = 123.0
        
        mock_collection.find_one.return_value = {"BatchId": batch_id}
        
        with pytest.raises(ValueError, match="Invalid BatchId"):
            Batch.find_tenet_id(batch_id)
    
    def test_find_tenet_id_zero_batch_id(self, mock_collection):
        """Test with zero batch_id"""
        batch_id = 0.0
        expected_tenet_id = 2.0
        
        mock_collection.find_one.return_value = {"TenetId": expected_tenet_id}
        
        result = Batch.find_tenet_id(batch_id)
        
        assert result == expected_tenet_id
    
    def test_find_tenet_id_negative_batch_id(self, mock_collection):
        """Test with negative batch_id"""
        batch_id = -123.0
        expected_tenet_id = 3.0
        
        mock_collection.find_one.return_value = {"TenetId": expected_tenet_id}
        
        result = Batch.find_tenet_id(batch_id)
        
        assert result == expected_tenet_id
    
    def test_find_tenet_id_large_batch_id(self, mock_collection):
        """Test with large batch_id"""
        batch_id = 999999999.99
        expected_tenet_id = 5.0
        
        mock_collection.find_one.return_value = {"TenetId": expected_tenet_id}
        
        result = Batch.find_tenet_id(batch_id)
        
        assert result == expected_tenet_id
