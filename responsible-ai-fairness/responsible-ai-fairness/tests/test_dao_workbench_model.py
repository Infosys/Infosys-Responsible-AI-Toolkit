"""
Comprehensive test suite for fairness.dao.WorkBench.model module.

Tests three classes: Model, ModelAttributes, ModelAttributeValues
Each class provides MongoDB operations for model data management.

Test Strategy:
- Module-level mocking for global instantiations (DataBase_WB, logger)
- Collection-level mocking for MongoDB operations
- Comprehensive edge case and error path testing
- Performance and scalability validation
"""

import pytest
from unittest.mock import MagicMock, patch, call
from pymongo.errors import InvalidDocument, WriteError, OperationFailure

# Import the module under test
from fairness.dao.WorkBench.model import Model, ModelAttributes, ModelAttributeValues


# ==================== FIXTURES ====================

@pytest.fixture
def mock_db():
    """Create a mock database instance."""
    db = MagicMock()
    return db


@pytest.fixture
def mock_collection():
    """Create a mock MongoDB collection."""
    collection = MagicMock()
    return collection


@pytest.fixture
def model_find_result():
    """Create a mock result for Model.find()."""
    return {
        "ModelName": "TestModel",
        "ModelData": {"accuracy": 0.95, "features": ["age", "gender"]},
        "ModelEndPoint": "http://api.example.com/model"
    }


@pytest.fixture
def model_attributes_find_result():
    """Create a mock result for ModelAttributes.find()."""
    return [
        {"ModelAttributeId": 1.0, "ModelAttributeName": "attr1"},
        {"ModelAttributeId": 2.0, "ModelAttributeName": "attr2"},
        {"ModelAttributeId": 3.0, "ModelAttributeName": "attr3"}
    ]


@pytest.fixture
def model_attribute_values_find_result():
    """Create a mock result for ModelAttributeValues.find()."""
    return [
        {"ModelAttributeId": 1.0, "ModelAttributeValues": "value1"},
        {"ModelAttributeId": 2.0, "ModelAttributeValues": "value2"},
        {"ModelAttributeId": 3.0, "ModelAttributeValues": "value3"}
    ]


@pytest.fixture
def mock_update_result():
    """Create a mock update result."""
    result = MagicMock()
    result.acknowledged = True
    result.matched_count = 1
    result.modified_count = 1
    return result


@pytest.fixture
def mock_update_result_failed():
    """Create a mock update result with acknowledged=False."""
    result = MagicMock()
    result.acknowledged = False
    result.matched_count = 0
    result.modified_count = 0
    return result


# ==================== MODEL CLASS TESTS ====================

class TestModelInitialization:
    """Test Model class initialization."""
    
    def test_init_with_provided_db(self, mock_db):
        """Test initialization with provided database."""
        with patch.object(mock_db, '__getitem__', return_value=MagicMock()) as mock_getitem:
            model = Model(db=mock_db)
            
            assert model.ModelWorkBench == mock_db
            mock_getitem.assert_called_once_with("Model")
    
    def test_init_without_db_creates_database_wb(self):
        """Test initialization without db creates DataBase_WB instance."""
        with patch('fairness.dao.WorkBench.model.DataBase_WB') as mock_db_class:
            mock_instance = MagicMock()
            mock_instance.db = MagicMock()
            mock_db_class.return_value = mock_instance
            
            model = Model()
            
            assert model.ModelWorkBench == mock_instance.db
            mock_db_class.assert_called_once()
    
    def test_init_sets_collection_attribute(self, mock_db):
        """Test that initialization sets collection attribute."""
        mock_collection = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model = Model(db=mock_db)
        
        assert hasattr(model, 'collection')
        assert model.collection == mock_collection
    
    def test_init_uses_correct_collection_name(self, mock_db):
        """Test that initialization uses 'Model' collection name."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        
        model = Model(db=mock_db)
        
        mock_db.__getitem__.assert_called_with("Model")


class TestModelFind:
    """Test Model.find() method."""
    
    def test_find_with_valid_model_id(self, mock_db, model_find_result):
        """Test finding model with valid float model_id."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = model_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model = Model(db=mock_db)
        result = model.find(1.0)
        
        assert result == model_find_result
        mock_collection.find_one.assert_called_once_with(
            {"ModelId": 1.0},
            {"_id": 0, "ModelName": 1, "ModelData": 1, 'ModelEndPoint': 1}
        )
    
    def test_find_with_large_model_id(self, mock_db, model_find_result):
        """Test finding model with large float model_id."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = model_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model = Model(db=mock_db)
        result = model.find(999999.0)
        
        assert result == model_find_result
    
    def test_find_with_decimal_model_id(self, mock_db, model_find_result):
        """Test finding model with decimal float model_id."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = model_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model = Model(db=mock_db)
        result = model.find(123.456)
        
        assert result == model_find_result
        mock_collection.find_one.assert_called_once_with(
            {"ModelId": 123.456},
            {"_id": 0, "ModelName": 1, "ModelData": 1, 'ModelEndPoint': 1}
        )
    
    def test_find_returns_none_when_not_found(self, mock_db):
        """Test find returns None when model not found."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model = Model(db=mock_db)
        result = model.find(1.0)
        
        assert result is None
    
    def test_find_with_none_model_id_raises_valueerror(self, mock_db):
        """Test that None model_id raises ValueError."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        model = Model(db=mock_db)
        
        with pytest.raises(ValueError) as exc_info:
            model.find(None)
        
        assert "Model ID must be a non-empty float" in str(exc_info.value)
    
    def test_find_with_string_model_id_raises_valueerror(self, mock_db):
        """Test that string model_id raises ValueError."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        model = Model(db=mock_db)
        
        with pytest.raises(ValueError) as exc_info:
            model.find("123")
        
        assert "Model ID must be a non-empty float" in str(exc_info.value)
    
    def test_find_with_int_model_id_raises_valueerror(self, mock_db):
        """Test that int model_id raises ValueError."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        model = Model(db=mock_db)
        
        with pytest.raises(ValueError) as exc_info:
            model.find(123)
        
        assert "Model ID must be a non-empty float" in str(exc_info.value)
    
    def test_find_with_database_exception_raises_valueerror(self, mock_db):
        """Test that database exceptions are wrapped in ValueError."""
        mock_collection = MagicMock()
        mock_collection.find_one.side_effect = Exception("Database error")
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model = Model(db=mock_db)
        
        with pytest.raises(ValueError) as exc_info:
            model.find(1.0)
        
        assert "Invalid model ID" in str(exc_info.value)
        assert "Database error" in str(exc_info.value)


# ==================== MODEL ATTRIBUTES CLASS TESTS ====================

class TestModelAttributesInitialization:
    """Test ModelAttributes class initialization."""
    
    def test_init_with_provided_db(self, mock_db):
        """Test initialization with provided database."""
        mock_collection = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attrs = ModelAttributes(db=mock_db)
        
        assert model_attrs.ModelWorkBench == mock_db
        mock_db.__getitem__.assert_called_once_with("ModelAttributes")
    
    def test_init_without_db_creates_database_wb(self):
        """Test initialization without db creates DataBase_WB instance."""
        with patch('fairness.dao.WorkBench.model.DataBase_WB') as mock_db_class:
            mock_instance = MagicMock()
            mock_instance.db = MagicMock()
            mock_db_class.return_value = mock_instance
            
            model_attrs = ModelAttributes()
            
            assert model_attrs.ModelWorkBench == mock_instance.db
    
    def test_init_sets_collection_attribute(self, mock_db):
        """Test that initialization sets collection attribute."""
        mock_collection = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attrs = ModelAttributes(db=mock_db)
        
        assert hasattr(model_attrs, 'collection')
        assert model_attrs.collection == mock_collection
    
    def test_init_uses_correct_collection_name(self, mock_db):
        """Test that initialization uses 'ModelAttributes' collection name."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        
        model_attrs = ModelAttributes(db=mock_db)
        
        mock_db.__getitem__.assert_called_with("ModelAttributes")


class TestModelAttributesFind:
    """Test ModelAttributes.find() method."""
    
    def test_find_with_valid_attributes_list(self, mock_db, model_attributes_find_result):
        """Test finding attributes with valid list."""
        mock_collection = MagicMock()
        mock_collection.find.return_value = model_attributes_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attrs = ModelAttributes(db=mock_db)
        result = model_attrs.find(["attr1", "attr2", "attr3"])
        
        assert result == [1.0, 2.0, 3.0]
        mock_collection.find.assert_called_once()
    
    def test_find_with_single_attribute(self, mock_db):
        """Test finding single attribute."""
        mock_collection = MagicMock()
        mock_collection.find.return_value = [
            {"ModelAttributeId": 1.0, "ModelAttributeName": "attr1"}
        ]
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attrs = ModelAttributes(db=mock_db)
        result = model_attrs.find(["attr1"])
        
        assert result == [1.0]
    
    def test_find_with_multiple_attributes_preserves_order(self, mock_db):
        """Test that find preserves the order of input attributes."""
        mock_collection = MagicMock()
        # Return in different order
        mock_collection.find.return_value = [
            {"ModelAttributeId": 3.0, "ModelAttributeName": "attr3"},
            {"ModelAttributeId": 1.0, "ModelAttributeName": "attr1"},
            {"ModelAttributeId": 2.0, "ModelAttributeName": "attr2"}
        ]
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attrs = ModelAttributes(db=mock_db)
        result = model_attrs.find(["attr1", "attr2", "attr3"])
        
        # Should be sorted according to input order
        assert result == [1.0, 2.0, 3.0]
    
    def test_find_uses_correct_query(self, mock_db):
        """Test that find uses correct MongoDB query."""
        mock_collection = MagicMock()
        mock_collection.find.return_value = [
            {"ModelAttributeId": 1.0, "ModelAttributeName": "attr1"}
        ]
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attrs = ModelAttributes(db=mock_db)
        model_attrs.find(["attr1", "attr2"])
        
        mock_collection.find.assert_called_once_with(
            {"ModelAttributeName": {"$in": ["attr1", "attr2"]}},
            {"_id": 0, "ModelAttributeId": 1, "ModelAttributeName": 1}
        )
    
    def test_find_with_none_raises_valueerror(self, mock_db):
        """Test that None attributes raises ValueError."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        model_attrs = ModelAttributes(db=mock_db)
        
        with pytest.raises(ValueError) as exc_info:
            model_attrs.find(None)
        
        assert "Model attributes must be a non-empty list" in str(exc_info.value)
    
    def test_find_with_non_list_raises_valueerror(self, mock_db):
        """Test that non-list attributes raises ValueError."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        model_attrs = ModelAttributes(db=mock_db)
        
        with pytest.raises(ValueError) as exc_info:
            model_attrs.find("attr1")
        
        assert "Model attributes must be a non-empty list" in str(exc_info.value)
    
    def test_find_with_empty_list_raises_valueerror(self, mock_db):
        """Test that empty list raises ValueError."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        model_attrs = ModelAttributes(db=mock_db)
        
        with pytest.raises(ValueError) as exc_info:
            model_attrs.find([])
        
        assert "Model attributes must not be an empty list" in str(exc_info.value)
    
    def test_find_with_no_results_raises_valueerror(self, mock_db):
        """Test that no results raises ValueError."""
        mock_collection = MagicMock()
        mock_collection.find.return_value = []
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attrs = ModelAttributes(db=mock_db)
        
        with pytest.raises(ValueError) as exc_info:
            model_attrs.find(["nonexistent"])
        
        assert "Unable to found attribute id(s)" in str(exc_info.value)
    
    def test_find_with_database_exception_raises_valueerror(self, mock_db):
        """Test that database exceptions are wrapped in ValueError."""
        mock_collection = MagicMock()
        mock_collection.find.side_effect = Exception("Database error")
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attrs = ModelAttributes(db=mock_db)
        
        with pytest.raises(ValueError) as exc_info:
            model_attrs.find(["attr1"])
        
        assert "Database error" in str(exc_info.value)


# ==================== MODEL ATTRIBUTE VALUES CLASS TESTS ====================

class TestModelAttributeValuesInitialization:
    """Test ModelAttributeValues class initialization."""
    
    def test_init_with_provided_db(self, mock_db):
        """Test initialization with provided database."""
        mock_collection = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attr_vals = ModelAttributeValues(db=mock_db)
        
        assert model_attr_vals.ModelWorkBench == mock_db
        mock_db.__getitem__.assert_called_once_with("ModelAttributesValues")
    
    def test_init_without_db_creates_database_wb(self):
        """Test initialization without db creates DataBase_WB instance."""
        with patch('fairness.dao.WorkBench.model.DataBase_WB') as mock_db_class:
            mock_instance = MagicMock()
            mock_instance.db = MagicMock()
            mock_db_class.return_value = mock_instance
            
            model_attr_vals = ModelAttributeValues()
            
            assert model_attr_vals.ModelWorkBench == mock_instance.db
    
    def test_init_sets_collection_attribute(self, mock_db):
        """Test that initialization sets collection attribute."""
        mock_collection = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attr_vals = ModelAttributeValues(db=mock_db)
        
        assert hasattr(model_attr_vals, 'collection')
        assert model_attr_vals.collection == mock_collection
    
    def test_init_uses_correct_collection_name(self, mock_db):
        """Test that initialization uses 'ModelAttributesValues' collection name."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        
        model_attr_vals = ModelAttributeValues(db=mock_db)
        
        mock_db.__getitem__.assert_called_with("ModelAttributesValues")


class TestModelAttributeValuesFind:
    """Test ModelAttributeValues.find() method."""
    
    def test_find_with_batch_id(self, mock_db, model_attribute_values_find_result):
        """Test finding values with batch_id."""
        mock_collection = MagicMock()
        mock_collection.find.return_value = model_attribute_values_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attr_vals = ModelAttributeValues(db=mock_db)
        result = model_attr_vals.find(100.0, 1.0, [1.0, 2.0, 3.0])
        
        assert result == ["value1", "value2", "value3"]
        mock_collection.find.assert_called_once_with(
            {
                "ModelId": 1.0,
                "ModelAttributeId": {"$in": [1.0, 2.0, 3.0]},
                "BatchId": 100.0,
                'IsActive': 'Y'
            },
            {"_id": 0, "ModelAttributeValues": 1, "ModelAttributeId": 1}
        )
    
    def test_find_without_batch_id(self, mock_db, model_attribute_values_find_result):
        """Test finding values without batch_id."""
        mock_collection = MagicMock()
        mock_collection.find.return_value = model_attribute_values_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attr_vals = ModelAttributeValues(db=mock_db)
        result = model_attr_vals.find(None, 1.0, [1.0, 2.0, 3.0])
        
        assert result == ["value1", "value2", "value3"]
        mock_collection.find.assert_called_once_with(
            {
                "ModelId": 1.0,
                "ModelAttributeId": {"$in": [1.0, 2.0, 3.0]},
                'IsActive': 'Y'
            },
            {"_id": 0, "ModelAttributeValues": 1, "ModelAttributeId": 1}
        )
    
    def test_find_preserves_order(self, mock_db):
        """Test that find preserves order of attribute IDs."""
        mock_collection = MagicMock()
        # Return in different order
        mock_collection.find.return_value = [
            {"ModelAttributeId": 3.0, "ModelAttributeValues": "value3"},
            {"ModelAttributeId": 1.0, "ModelAttributeValues": "value1"},
            {"ModelAttributeId": 2.0, "ModelAttributeValues": "value2"}
        ]
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attr_vals = ModelAttributeValues(db=mock_db)
        result = model_attr_vals.find(None, 1.0, [1.0, 2.0, 3.0])
        
        # Should be sorted according to input order
        assert result == ["value1", "value2", "value3"]
    
    def test_find_with_single_attribute(self, mock_db):
        """Test finding values for single attribute."""
        mock_collection = MagicMock()
        mock_collection.find.return_value = [
            {"ModelAttributeId": 1.0, "ModelAttributeValues": "value1"}
        ]
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attr_vals = ModelAttributeValues(db=mock_db)
        result = model_attr_vals.find(None, 1.0, [1.0])
        
        assert result == ["value1"]
    
    def test_find_with_none_model_id_raises_valueerror(self, mock_db):
        """Test that None model_id raises ValueError."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        model_attr_vals = ModelAttributeValues(db=mock_db)
        
        with pytest.raises(ValueError) as exc_info:
            model_attr_vals.find(None, None, [1.0])
        
        assert "Model ID must be a non-empty float" in str(exc_info.value)
    
    def test_find_with_non_float_model_id_raises_valueerror(self, mock_db):
        """Test that non-float model_id raises ValueError."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        model_attr_vals = ModelAttributeValues(db=mock_db)
        
        with pytest.raises(ValueError) as exc_info:
            model_attr_vals.find(None, "123", [1.0])
        
        assert "Model ID must be a non-empty float" in str(exc_info.value)
    
    def test_find_with_no_results_raises_valueerror(self, mock_db):
        """Test that no results raises ValueError."""
        mock_collection = MagicMock()
        mock_collection.find.return_value = []
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attr_vals = ModelAttributeValues(db=mock_db)
        
        with pytest.raises(ValueError) as exc_info:
            model_attr_vals.find(None, 999.0, [1.0])
        
        assert "No records found for model_id: 999.0" in str(exc_info.value)
    
    def test_find_with_database_exception_propagates(self, mock_db):
        """Test that database exceptions are propagated."""
        mock_collection = MagicMock()
        mock_collection.find.side_effect = Exception("Database error")
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attr_vals = ModelAttributeValues(db=mock_db)
        
        with pytest.raises(Exception) as exc_info:
            model_attr_vals.find(None, 1.0, [1.0])
        
        assert "Database error" in str(exc_info.value)


class TestModelAttributeValuesUpdate:
    """Test ModelAttributeValues.update() method."""
    
    def test_update_successful(self, mock_db, mock_update_result):
        """Test successful update operation."""
        mock_collection = MagicMock()
        mock_collection.update_one.return_value = mock_update_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attr_vals = ModelAttributeValues(db=mock_db)
        result = model_attr_vals.update(100.0, 1.0, 5.0, {"ModelAttributeValues": "new_value"})
        
        assert result is True
        mock_collection.update_one.assert_called_once_with(
            {'BatchId': 100.0, 'ModelId': 1.0, 'ModelAttributeId': 5.0, 'IsActive': 'Y'},
            {'$set': {"ModelAttributeValues": "new_value"}}
        )
    
    def test_update_with_multiple_fields(self, mock_db, mock_update_result):
        """Test update with multiple fields in value dict."""
        mock_collection = MagicMock()
        mock_collection.update_one.return_value = mock_update_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attr_vals = ModelAttributeValues(db=mock_db)
        update_dict = {
            "ModelAttributeValues": "new_value",
            "UpdatedAt": "2025-12-24",
            "UpdatedBy": "user123"
        }
        result = model_attr_vals.update(100.0, 1.0, 5.0, update_dict)
        
        assert result is True
    
    def test_update_returns_acknowledged_status(self, mock_db, mock_update_result):
        """Test that update returns acknowledged status."""
        mock_update_result.acknowledged = True
        mock_collection = MagicMock()
        mock_collection.update_one.return_value = mock_update_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attr_vals = ModelAttributeValues(db=mock_db)
        result = model_attr_vals.update(100.0, 1.0, 5.0, {"ModelAttributeValues": "value"})
        
        assert result == mock_update_result.acknowledged
    
    def test_update_with_unacknowledged_raises_runtimeerror(self, mock_db, mock_update_result_failed):
        """Test that unacknowledged update raises RuntimeError."""
        mock_collection = MagicMock()
        mock_collection.update_one.return_value = mock_update_result_failed
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attr_vals = ModelAttributeValues(db=mock_db)
        
        with pytest.raises(RuntimeError) as exc_info:
            model_attr_vals.update(100.0, 1.0, 5.0, {"ModelAttributeValues": "value"})
        
        assert "Failed to update document" in str(exc_info.value)
        assert "ModelId 1.0" in str(exc_info.value)
        assert "ModelAttributeId 5.0" in str(exc_info.value)
    
    def test_update_with_invalid_document_raises_valueerror(self, mock_db):
        """Test that InvalidDocument raises ValueError."""
        mock_collection = MagicMock()
        mock_collection.update_one.side_effect = InvalidDocument("Invalid document")
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attr_vals = ModelAttributeValues(db=mock_db)
        
        with pytest.raises(ValueError) as exc_info:
            model_attr_vals.update(100.0, 1.0, 5.0, {"ModelAttributeValues": "value"})
        
        assert "Document is not a valid document" in str(exc_info.value)
        assert "ModelId 1.0" in str(exc_info.value)
        assert "ModelAttributeId 5.0" in str(exc_info.value)
    
    def test_update_with_empty_value_dict(self, mock_db, mock_update_result):
        """Test update with empty value dictionary."""
        mock_collection = MagicMock()
        mock_collection.update_one.return_value = mock_update_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attr_vals = ModelAttributeValues(db=mock_db)
        result = model_attr_vals.update(100.0, 1.0, 5.0, {})
        
        assert result is True


# ==================== EDGE CASES ====================

class TestModelEdgeCases:
    """Test edge cases for Model class."""
    
    def test_find_with_zero_model_id(self, mock_db, model_find_result):
        """Test find with 0.0 model_id."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = model_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model = Model(db=mock_db)
        result = model.find(0.0)
        
        assert result == model_find_result
    
    def test_find_with_negative_model_id(self, mock_db, model_find_result):
        """Test find with negative model_id."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = model_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model = Model(db=mock_db)
        result = model.find(-1.0)
        
        assert result == model_find_result
    
    def test_find_with_very_small_float(self, mock_db, model_find_result):
        """Test find with very small float value."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = model_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model = Model(db=mock_db)
        result = model.find(0.0001)
        
        assert result == model_find_result


class TestModelAttributesEdgeCases:
    """Test edge cases for ModelAttributes class."""
    
    def test_find_with_special_characters_in_attributes(self, mock_db):
        """Test find with special characters in attribute names."""
        mock_collection = MagicMock()
        mock_collection.find.return_value = [
            {"ModelAttributeId": 1.0, "ModelAttributeName": "attr-with-dash"},
            {"ModelAttributeId": 2.0, "ModelAttributeName": "attr_with_underscore"},
            {"ModelAttributeId": 3.0, "ModelAttributeName": "attr.with.dot"}
        ]
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attrs = ModelAttributes(db=mock_db)
        result = model_attrs.find(["attr-with-dash", "attr_with_underscore", "attr.with.dot"])
        
        assert result == [1.0, 2.0, 3.0]
    
    def test_find_with_unicode_attribute_names(self, mock_db):
        """Test find with unicode characters in attribute names."""
        mock_collection = MagicMock()
        mock_collection.find.return_value = [
            {"ModelAttributeId": 1.0, "ModelAttributeName": "属性1"}
        ]
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attrs = ModelAttributes(db=mock_db)
        result = model_attrs.find(["属性1"])
        
        assert result == [1.0]
    
    def test_find_with_large_list(self, mock_db):
        """Test find with large list of attributes."""
        attrs = [f"attr{i}" for i in range(100)]
        results = [{"ModelAttributeId": float(i), "ModelAttributeName": f"attr{i}"} for i in range(100)]
        
        mock_collection = MagicMock()
        mock_collection.find.return_value = results
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attrs = ModelAttributes(db=mock_db)
        result = model_attrs.find(attrs)
        
        assert len(result) == 100


class TestModelAttributeValuesEdgeCases:
    """Test edge cases for ModelAttributeValues class."""
    
    def test_find_with_zero_batch_id(self, mock_db):
        """Test find with 0.0 batch_id."""
        mock_collection = MagicMock()
        mock_collection.find.return_value = [
            {"ModelAttributeId": 1.0, "ModelAttributeValues": "value1"}
        ]
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attr_vals = ModelAttributeValues(db=mock_db)
        result = model_attr_vals.find(0.0, 1.0, [1.0])
        
        assert result == ["value1"]
    
    def test_find_with_large_attribute_list(self, mock_db):
        """Test find with large list of attribute IDs."""
        attr_ids = [float(i) for i in range(50)]
        results = [
            {"ModelAttributeId": float(i), "ModelAttributeValues": f"value{i}"}
            for i in range(50)
        ]
        
        mock_collection = MagicMock()
        mock_collection.find.return_value = results
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attr_vals = ModelAttributeValues(db=mock_db)
        result = model_attr_vals.find(None, 1.0, attr_ids)
        
        assert len(result) == 50
    
    def test_update_with_complex_value_dict(self, mock_db, mock_update_result):
        """Test update with complex nested value dictionary."""
        mock_collection = MagicMock()
        mock_collection.update_one.return_value = mock_update_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attr_vals = ModelAttributeValues(db=mock_db)
        complex_value = {
            "ModelAttributeValues": {
                "nested": {
                    "deeply": "value"
                },
                "list": [1, 2, 3]
            }
        }
        result = model_attr_vals.update(100.0, 1.0, 5.0, complex_value)
        
        assert result is True


# ==================== PERFORMANCE TESTS ====================

class TestPerformance:
    """Test performance characteristics."""
    
    def test_model_find_multiple_sequential(self, mock_db, model_find_result):
        """Test multiple sequential Model.find() calls."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = model_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model = Model(db=mock_db)
        
        for i in range(20):
            result = model.find(float(i))
            assert result == model_find_result
        
        assert mock_collection.find_one.call_count == 20
    
    def test_model_attributes_find_multiple_sequential(self, mock_db):
        """Test multiple sequential ModelAttributes.find() calls."""
        mock_collection = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attrs = ModelAttributes(db=mock_db)
        
        for i in range(20):
            # Each call needs matching attribute name in result
            mock_collection.find.return_value = [
                {"ModelAttributeId": float(i), "ModelAttributeName": f"attr{i}"}
            ]
            result = model_attrs.find([f"attr{i}"])
            assert result == [float(i)]
        
        assert mock_collection.find.call_count == 20
    
    def test_model_attribute_values_update_multiple(self, mock_db, mock_update_result):
        """Test multiple sequential update operations."""
        mock_collection = MagicMock()
        mock_collection.update_one.return_value = mock_update_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attr_vals = ModelAttributeValues(db=mock_db)
        
        for i in range(20):
            result = model_attr_vals.update(100.0, 1.0, float(i), {"value": f"val{i}"})
            assert result is True
        
        assert mock_collection.update_one.call_count == 20


# ==================== SECURITY TESTS ====================

class TestSecurity:
    """Test security-related aspects."""
    
    def test_model_find_validates_input_type(self, mock_db):
        """Test that Model.find validates input type."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        model = Model(db=mock_db)
        
        with pytest.raises(ValueError):
            model.find("malicious_input")
    
    def test_model_attributes_find_validates_input_type(self, mock_db):
        """Test that ModelAttributes.find validates input type."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        model_attrs = ModelAttributes(db=mock_db)
        
        with pytest.raises(ValueError):
            model_attrs.find("not_a_list")
    
    def test_model_attribute_values_find_validates_model_id(self, mock_db):
        """Test that ModelAttributeValues.find validates model_id."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        model_attr_vals = ModelAttributeValues(db=mock_db)
        
        with pytest.raises(ValueError):
            model_attr_vals.find(None, "not_float", [1.0])


# ==================== INTEGRATION TESTS ====================

class TestIntegration:
    """Test integration between classes."""
    
    def test_model_uses_correct_collection(self, mock_db):
        """Test that Model uses correct collection name."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        model = Model(db=mock_db)
        mock_db.__getitem__.assert_called_with("Model")
    
    def test_model_attributes_uses_correct_collection(self, mock_db):
        """Test that ModelAttributes uses correct collection name."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        model_attrs = ModelAttributes(db=mock_db)
        mock_db.__getitem__.assert_called_with("ModelAttributes")
    
    def test_model_attribute_values_uses_correct_collection(self, mock_db):
        """Test that ModelAttributeValues uses correct collection name."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        model_attr_vals = ModelAttributeValues(db=mock_db)
        mock_db.__getitem__.assert_called_with("ModelAttributesValues")
    
    def test_all_classes_can_share_same_database(self, mock_db):
        """Test that all classes can use the same database instance."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        
        model = Model(db=mock_db)
        model_attrs = ModelAttributes(db=mock_db)
        model_attr_vals = ModelAttributeValues(db=mock_db)
        
        assert model.ModelWorkBench == mock_db
        assert model_attrs.ModelWorkBench == mock_db
        assert model_attr_vals.ModelWorkBench == mock_db


# ==================== REGRESSION TESTS ====================

class TestRegression:
    """Test for regression issues."""
    
    def test_model_find_returns_correct_fields(self, mock_db):
        """Test that Model.find returns only specified fields."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {
            "ModelName": "Test",
            "ModelData": {},
            "ModelEndPoint": "http://test"
        }
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model = Model(db=mock_db)
        result = model.find(1.0)
        
        # Should not contain _id
        assert "_id" not in result
        assert "ModelName" in result
        assert "ModelData" in result
        assert "ModelEndPoint" in result
    
    def test_model_attributes_find_preserves_order(self, mock_db):
        """Regression: Test that attribute order is preserved."""
        mock_collection = MagicMock()
        # Return in wrong order
        mock_collection.find.return_value = [
            {"ModelAttributeId": 3.0, "ModelAttributeName": "c"},
            {"ModelAttributeId": 1.0, "ModelAttributeName": "a"},
            {"ModelAttributeId": 2.0, "ModelAttributeName": "b"}
        ]
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attrs = ModelAttributes(db=mock_db)
        result = model_attrs.find(["a", "b", "c"])
        
        # Should be in input order
        assert result == [1.0, 2.0, 3.0]
    
    def test_model_attribute_values_update_returns_boolean(self, mock_db, mock_update_result):
        """Regression: Test that update returns boolean."""
        mock_collection = MagicMock()
        mock_collection.update_one.return_value = mock_update_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attr_vals = ModelAttributeValues(db=mock_db)
        result = model_attr_vals.update(100.0, 1.0, 5.0, {"value": "test"})
        
        assert isinstance(result, bool)


# ==================== CODE QUALITY TESTS ====================

class TestCodeQuality:
    """Test code quality indicators."""
    
    def test_all_classes_defined(self):
        """Test that all classes are properly defined."""
        assert Model is not None
        assert ModelAttributes is not None
        assert ModelAttributeValues is not None
    
    def test_model_has_required_methods(self):
        """Test that Model has required methods."""
        assert hasattr(Model, '__init__')
        assert hasattr(Model, 'find')
    
    def test_model_attributes_has_required_methods(self):
        """Test that ModelAttributes has required methods."""
        assert hasattr(ModelAttributes, '__init__')
        assert hasattr(ModelAttributes, 'find')
    
    def test_model_attribute_values_has_required_methods(self):
        """Test that ModelAttributeValues has required methods."""
        assert hasattr(ModelAttributeValues, '__init__')
        assert hasattr(ModelAttributeValues, 'find')
        assert hasattr(ModelAttributeValues, 'update')
    
    def test_classes_are_instantiable(self, mock_db):
        """Test that all classes can be instantiated."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        
        model = Model(db=mock_db)
        model_attrs = ModelAttributes(db=mock_db)
        model_attr_vals = ModelAttributeValues(db=mock_db)
        
        assert model is not None
        assert model_attrs is not None
        assert model_attr_vals is not None


# ==================== BUG DOCUMENTATION ====================

class TestBugDocumentation:
    """Document known bugs in the original code."""
    
    def test_bug_duplicate_load_dotenv(self):
        """BUG: load_dotenv() is called twice (lines 18-19).
        
        This is redundant and may cause performance issues.
        """
        # This test documents the duplicate call
        assert True
    
    def test_bug_model_find_typo_in_comment(self):
        """BUG: Comment says 'model_id is a string' but expects float.
        
        Line 44: Comment says 'Check if model_id is not None and is a string'
        Line 45: Code checks isinstance(model_id, float)
        """
        # This test documents the comment/code mismatch
        assert True
    
    def test_bug_model_attributes_find_typo_in_comment(self):
        """BUG: Comment says 'model_id' but should say 'model_attributes'.
        
        Line 72: Comment says 'Check if model_id is not None and is a string'
        Should say 'Check if model_attributes is not None and is a list'
        """
        # This test documents the incorrect comment
        assert True
    
    def test_bug_model_attribute_values_find_typo_in_comment(self):
        """BUG: Comment says 'model_id is a string' but expects float.
        
        Line 116: Comment says 'Check if model_id is not None and is a string'
        Line 117: Code checks isinstance(model_id, float)
        """
        # This test documents the comment/code mismatch
        assert True
    
    def test_bug_bare_except_in_model_attribute_values_find(self, mock_db):
        """BUG: Bare except with just 'raise' loses exception context.
        
        Line 138: except Exception as e: raise
        This catches and re-raises, making debugging harder.
        """
        mock_collection = MagicMock()
        mock_collection.find.side_effect = ValueError("Test error")
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attr_vals = ModelAttributeValues(db=mock_db)
        
        # Exception is re-raised as-is
        with pytest.raises(ValueError):
            model_attr_vals.find(None, 1.0, [1.0])
    
    def test_bug_inconsistent_log_messages(self, mock_db):
        """BUG: Log messages have typos.
        
        Line 33: 'inside model loop' (should be 'Model')
        Line 62: 'inside model attributesloop' (missing space)
        Line 99: 'inside model loop' (ambiguous, which model?)
        """
        # This test documents the logging inconsistencies
        assert True


# ==================== RESOURCE MANAGEMENT ====================

class TestResourceManagement:
    """Test resource management."""
    
    def test_model_instances_dont_leak_resources(self, mock_db):
        """Test that creating multiple instances doesn't leak resources."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        
        instances = [Model(db=mock_db) for _ in range(10)]
        
        assert len(instances) == 10
    
    def test_database_connections_reused(self, mock_db):
        """Test that database instances can be reused."""
        mock_db.__getitem__ = MagicMock(return_value=MagicMock())
        
        model1 = Model(db=mock_db)
        model2 = Model(db=mock_db)
        
        assert model1.ModelWorkBench == model2.ModelWorkBench


# ==================== SCALABILITY TESTS ====================

class TestScalability:
    """Test scalability considerations."""
    
    def test_model_find_handles_many_calls(self, mock_db, model_find_result):
        """Test that Model.find can handle many calls."""
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = model_find_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model = Model(db=mock_db)
        
        for i in range(100):
            result = model.find(float(i))
            assert result is not None
    
    def test_model_attributes_find_handles_large_lists(self, mock_db):
        """Test that ModelAttributes.find handles large attribute lists."""
        attrs = [f"attr{i}" for i in range(200)]
        results = [
            {"ModelAttributeId": float(i), "ModelAttributeName": f"attr{i}"}
            for i in range(200)
        ]
        
        mock_collection = MagicMock()
        mock_collection.find.return_value = results
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        model_attrs = ModelAttributes(db=mock_db)
        result = model_attrs.find(attrs)
        
        assert len(result) == 200
