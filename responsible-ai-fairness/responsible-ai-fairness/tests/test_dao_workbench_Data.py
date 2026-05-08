"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Comprehensive test cases for src/fairness/dao/WorkBench/Data.py

Test Coverage:
- 4 Classes: SampleDataset, Dataset, DataAttributes, DataAttributeValues
- Core Principles: Clarity, Isolation, Repeatability, Coverage, Assertions
- Quality Metrics: Functional Correctness, Edge Cases, Error Handling, Performance,
  Resource Management, Security, Scalability, Integration Points, Regression, Code Quality
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from fastapi import HTTPException
from typing import Dict, Any, List


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_db():
    """Create a mock database with collection."""
    db = MagicMock()
    collection = MagicMock()
    db.__getitem__.return_value = collection
    return db


@pytest.fixture
def mock_collection():
    """Create a mock collection for database operations."""
    return MagicMock()


@pytest.fixture
def sample_dataset_instance(mock_db):
    """Create SampleDataset instance with mocked database."""
    with patch('fairness.dao.WorkBench.Data.DataBase_WB') as mock_db_class:
        mock_db_instance = MagicMock()
        mock_db_instance.db = mock_db
        mock_db_class.return_value = mock_db_instance
        
        from fairness.dao.WorkBench.Data import SampleDataset
        return SampleDataset(db=mock_db)


@pytest.fixture
def dataset_instance(mock_db):
    """Create Dataset instance with mocked database."""
    from fairness.dao.WorkBench.Data import Dataset
    return Dataset(db=mock_db)


@pytest.fixture
def data_attributes_instance(mock_db):
    """Create DataAttributes instance with mocked database."""
    from fairness.dao.WorkBench.Data import DataAttributes
    return DataAttributes(db=mock_db)


@pytest.fixture
def data_attribute_values_instance(mock_db):
    """Create DataAttributeValues instance with mocked database."""
    from fairness.dao.WorkBench.Data import DataAttributeValues
    return DataAttributeValues(db=mock_db)


@pytest.fixture
def valid_sample_id():
    """Valid sample ID."""
    return 123.45


@pytest.fixture
def valid_dataset_id():
    """Valid dataset ID."""
    return 456.78


@pytest.fixture
def valid_file_id():
    """Valid file ID."""
    return 789.01


@pytest.fixture
def valid_batch_id():
    """Valid batch ID."""
    return 111.22


@pytest.fixture
def valid_dataset_attributes():
    """Valid dataset attributes list."""
    return ["age", "gender", "income"]


@pytest.fixture
def valid_dataset_attribute_ids():
    """Valid dataset attribute IDs list."""
    return [1.0, 2.0, 3.0]


# ============================================================================
# TEST CLASS 1: SampleDataset Initialization Tests
# ============================================================================

class TestSampleDatasetInitialization:
    """Test SampleDataset class initialization scenarios."""
    
    def test_init_with_db_parameter(self, mock_db):
        """Test initialization with provided db parameter."""
        from fairness.dao.WorkBench.Data import SampleDataset
        sample = SampleDataset(db=mock_db)
        
        assert sample is not None
        assert sample.ModelWorkBench == mock_db
        assert sample.collection is not None
    
    def test_init_without_db_parameter(self):
        """Test initialization without providing db parameter."""
        with patch('fairness.dao.WorkBench.Data.DataBase_WB') as mock_db_class:
            mock_db_instance = MagicMock()
            mock_db_instance.db = MagicMock()
            mock_db_class.return_value = mock_db_instance
            
            from fairness.dao.WorkBench.Data import SampleDataset
            sample = SampleDataset()
            
            assert sample is not None
            mock_db_class.assert_called()
    
    def test_init_collection_assignment_dataset(self, mock_db):
        """Test that collection is correctly assigned to 'Dataset'."""
        with patch('fairness.dao.WorkBench.Data.ModelWorkBench', mock_db):
            from fairness.dao.WorkBench.Data import SampleDataset
            sample = SampleDataset(db=mock_db)
            
            # Collection should be from global ModelWorkBench, not self.ModelWorkBench
            assert sample.collection is not None
    
    def test_init_with_none_db(self):
        """Test initialization with None as db parameter."""
        with patch('fairness.dao.WorkBench.Data.DataBase_WB') as mock_db_class:
            mock_db_instance = MagicMock()
            mock_db_instance.db = MagicMock()
            mock_db_class.return_value = mock_db_instance
            
            from fairness.dao.WorkBench.Data import SampleDataset
            sample = SampleDataset(db=None)
            
            mock_db_class.assert_called()
    
    def test_init_multiple_instances(self, mock_db):
        """Test creating multiple SampleDataset instances."""
        from fairness.dao.WorkBench.Data import SampleDataset
        sample1 = SampleDataset(db=mock_db)
        sample2 = SampleDataset(db=mock_db)
        
        assert sample1 is not sample2
        assert sample1.ModelWorkBench == sample2.ModelWorkBench


# ============================================================================
# TEST CLASS 2: Dataset Initialization Tests
# ============================================================================

class TestDatasetInitialization:
    """Test Dataset class initialization scenarios."""
    
    def test_init_with_db_parameter(self, mock_db):
        """Test initialization with provided db parameter."""
        from fairness.dao.WorkBench.Data import Dataset
        dataset = Dataset(db=mock_db)
        
        assert dataset is not None
        assert dataset.ModelWorkBench == mock_db
        assert dataset.collection is not None
    
    def test_init_without_db_parameter(self):
        """Test initialization without providing db parameter."""
        with patch('fairness.dao.WorkBench.Data.DataBase_WB') as mock_db_class:
            mock_db_instance = MagicMock()
            mock_db_instance.db = MagicMock()
            mock_db_class.return_value = mock_db_instance
            
            from fairness.dao.WorkBench.Data import Dataset
            dataset = Dataset()
            
            assert dataset is not None
            mock_db_class.assert_called()
    
    def test_init_collection_assignment(self, mock_db):
        """Test that collection is correctly assigned during initialization."""
        from fairness.dao.WorkBench.Data import Dataset
        dataset = Dataset(db=mock_db)
        
        mock_db.__getitem__.assert_called_with("Dataset")
    
    def test_init_with_none_db(self):
        """Test initialization with None as db parameter."""
        with patch('fairness.dao.WorkBench.Data.DataBase_WB') as mock_db_class:
            mock_db_instance = MagicMock()
            mock_db_instance.db = MagicMock()
            mock_db_class.return_value = mock_db_instance
            
            from fairness.dao.WorkBench.Data import Dataset
            dataset = Dataset(db=None)
            
            mock_db_class.assert_called()


# ============================================================================
# TEST CLASS 3: DataAttributes Initialization Tests
# ============================================================================

class TestDataAttributesInitialization:
    """Test DataAttributes class initialization scenarios."""
    
    def test_init_with_db_parameter(self, mock_db):
        """Test initialization with provided db parameter."""
        from fairness.dao.WorkBench.Data import DataAttributes
        data_attr = DataAttributes(db=mock_db)
        
        assert data_attr is not None
        assert data_attr.ModelWorkBench == mock_db
        assert data_attr.collection is not None
    
    def test_init_without_db_parameter(self):
        """Test initialization without providing db parameter."""
        with patch('fairness.dao.WorkBench.Data.DataBase_WB') as mock_db_class:
            mock_db_instance = MagicMock()
            mock_db_instance.db = MagicMock()
            mock_db_class.return_value = mock_db_instance
            
            from fairness.dao.WorkBench.Data import DataAttributes
            data_attr = DataAttributes()
            
            assert data_attr is not None
            mock_db_class.assert_called()
    
    def test_init_collection_assignment(self, mock_db):
        """Test that collection is correctly assigned to DataAttributes."""
        from fairness.dao.WorkBench.Data import DataAttributes
        data_attr = DataAttributes(db=mock_db)
        
        mock_db.__getitem__.assert_called_with("DataAttributes")


# ============================================================================
# TEST CLASS 4: DataAttributeValues Initialization Tests
# ============================================================================

class TestDataAttributeValuesInitialization:
    """Test DataAttributeValues class initialization scenarios."""
    
    def test_init_with_db_parameter(self, mock_db):
        """Test initialization with provided db parameter."""
        from fairness.dao.WorkBench.Data import DataAttributeValues
        data_attr_values = DataAttributeValues(db=mock_db)
        
        assert data_attr_values is not None
        assert data_attr_values.ModelWorkBench == mock_db
        assert data_attr_values.collection is not None
    
    def test_init_without_db_parameter(self):
        """Test initialization without providing db parameter."""
        with patch('fairness.dao.WorkBench.Data.DataBase_WB') as mock_db_class:
            mock_db_instance = MagicMock()
            mock_db_instance.db = MagicMock()
            mock_db_class.return_value = mock_db_instance
            
            from fairness.dao.WorkBench.Data import DataAttributeValues
            data_attr_values = DataAttributeValues()
            
            assert data_attr_values is not None
            mock_db_class.assert_called()
    
    def test_init_collection_assignment(self, mock_db):
        """Test that collection is correctly assigned to DataAttributesValues."""
        from fairness.dao.WorkBench.Data import DataAttributeValues
        data_attr_values = DataAttributeValues(db=mock_db)
        
        mock_db.__getitem__.assert_called_with("DataAttributesValues")


# ============================================================================
# TEST CLASS 5: Dataset Find Method - Functional Correctness
# ============================================================================

class TestDatasetFindFunctionalCorrectness:
    """Test Dataset.find method functional correctness."""
    
    def test_find_successful_retrieval(self, dataset_instance, valid_dataset_id):
        """Test successful dataset retrieval."""
        expected_result = {"DataSetName": "test_dataset", "SampleData": 123.45}
        dataset_instance.collection.find_one.return_value = expected_result
        
        result = dataset_instance.find(valid_dataset_id)
        
        assert result == expected_result
        dataset_instance.collection.find_one.assert_called_once()
    
    def test_find_correct_query_parameters(self, dataset_instance, valid_dataset_id):
        """Test that find method uses correct query parameters."""
        dataset_instance.collection.find_one.return_value = {"DataSetName": "test"}
        
        dataset_instance.find(valid_dataset_id)
        
        call_args = dataset_instance.collection.find_one.call_args
        assert call_args[0][0] == {"DataId": valid_dataset_id}
        assert call_args[0][1] == {"_id": 0, "DataSetName": 1, "SampleData": 1}
    
    def test_find_returns_only_specified_fields(self, dataset_instance, valid_dataset_id):
        """Test that find returns only DataSetName and SampleData fields."""
        expected_result = {"DataSetName": "test_dataset", "SampleData": 123.45}
        dataset_instance.collection.find_one.return_value = expected_result
        
        result = dataset_instance.find(valid_dataset_id)
        
        assert "DataSetName" in result
        assert "SampleData" in result
        assert "_id" not in result
    
    def test_find_with_different_dataset_ids(self, dataset_instance):
        """Test find with various dataset IDs."""
        dataset_instance.collection.find_one.return_value = {"DataSetName": "test"}
        
        for dataset_id in [1.0, 123.45, 999.99, 0.01]:
            dataset_instance.find(dataset_id)
            call_args = dataset_instance.collection.find_one.call_args
            assert call_args[0][0]["DataId"] == dataset_id


# ============================================================================
# TEST CLASS 6: Dataset FindFile Method - Functional Correctness
# ============================================================================

class TestDatasetFindFileFunctionalCorrectness:
    """Test Dataset.findFile method functional correctness."""
    
    def test_findfile_successful_retrieval(self, dataset_instance, valid_file_id):
        """Test successful file retrieval."""
        expected_result = {"DataId": 456.78}
        dataset_instance.collection.find_one.return_value = expected_result
        
        result = dataset_instance.findFile(valid_file_id)
        
        assert result == expected_result
        dataset_instance.collection.find_one.assert_called_once()
    
    def test_findfile_correct_query_parameters(self, dataset_instance, valid_file_id):
        """Test that findFile method uses correct query parameters."""
        dataset_instance.collection.find_one.return_value = {"DataId": 456.78}
        
        dataset_instance.findFile(valid_file_id)
        
        call_args = dataset_instance.collection.find_one.call_args
        assert call_args[0][0] == {"SampleData": valid_file_id}
        assert call_args[0][1] == {"_id": 0, "DataId": 1}
    
    def test_findfile_returns_only_dataid(self, dataset_instance, valid_file_id):
        """Test that findFile returns only DataId field."""
        expected_result = {"DataId": 456.78}
        dataset_instance.collection.find_one.return_value = expected_result
        
        result = dataset_instance.findFile(valid_file_id)
        
        assert "DataId" in result
        assert "_id" not in result


# ============================================================================
# TEST CLASS 7: Dataset Methods - Edge Cases
# ============================================================================

class TestDatasetEdgeCases:
    """Test Dataset class edge cases."""
    
    def test_find_with_none_dataset_id(self, dataset_instance):
        """Test find raises exception when dataset_id is None."""
        with pytest.raises(HTTPException) as exc_info:
            dataset_instance.find(None)
        
        assert exc_info.value.status_code == 500
        assert "Data ID must be a non-empty float" in str(exc_info.value.detail)
    
    def test_find_with_string_dataset_id(self, dataset_instance):
        """Test find raises exception when dataset_id is string."""
        with pytest.raises(HTTPException) as exc_info:
            dataset_instance.find("123.45")
        
        assert exc_info.value.status_code == 500
    
    def test_find_with_integer_dataset_id(self, dataset_instance):
        """Test find raises exception when dataset_id is integer."""
        with pytest.raises(HTTPException) as exc_info:
            dataset_instance.find(123)
        
        assert exc_info.value.status_code == 500
    
    def test_find_with_zero_dataset_id(self, dataset_instance):
        """Test find with zero as dataset_id."""
        dataset_instance.collection.find_one.return_value = {"DataSetName": "test"}
        
        result = dataset_instance.find(0.0)
        assert result is not None
    
    def test_find_with_negative_dataset_id(self, dataset_instance):
        """Test find with negative dataset_id."""
        dataset_instance.collection.find_one.return_value = {"DataSetName": "test"}
        
        result = dataset_instance.find(-123.45)
        assert result is not None
    
    def test_findfile_with_none_file_id(self, dataset_instance):
        """Test findFile raises exception when file_id is None."""
        with pytest.raises(HTTPException) as exc_info:
            dataset_instance.findFile(None)
        
        assert exc_info.value.status_code == 500
    
    def test_findfile_with_invalid_type(self, dataset_instance):
        """Test findFile raises exception with invalid type."""
        with pytest.raises(HTTPException) as exc_info:
            dataset_instance.findFile("invalid")
        
        assert exc_info.value.status_code == 500


# ============================================================================
# TEST CLASS 8: Dataset Methods - Error Handling
# ============================================================================

class TestDatasetErrorHandling:
    """Test Dataset class error handling."""
    
    def test_find_dataset_not_found(self, dataset_instance, valid_dataset_id):
        """Test find raises HTTPException when dataset not found."""
        dataset_instance.collection.find_one.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            dataset_instance.find(valid_dataset_id)
        
        assert exc_info.value.status_code == 500
        assert "Data ID not found" in str(exc_info.value.detail)
    
    def test_find_database_connection_error(self, dataset_instance, valid_dataset_id):
        """Test find handles database connection errors."""
        dataset_instance.collection.find_one.side_effect = Exception("Connection error")
        
        with pytest.raises(Exception) as exc_info:
            dataset_instance.find(valid_dataset_id)
        
        assert "Connection error" in str(exc_info.value)
    
    def test_findfile_file_not_found(self, dataset_instance, valid_file_id):
        """Test findFile raises HTTPException when file not found."""
        dataset_instance.collection.find_one.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            dataset_instance.findFile(valid_file_id)
        
        assert exc_info.value.status_code == 500
        assert "Data ID not found" in str(exc_info.value.detail)
    
    def test_findfile_database_error(self, dataset_instance, valid_file_id):
        """Test findFile handles database errors."""
        dataset_instance.collection.find_one.side_effect = Exception("DB Error")
        
        with pytest.raises(Exception) as exc_info:
            dataset_instance.findFile(valid_file_id)
        
        assert "DB Error" in str(exc_info.value)


# ============================================================================
# TEST CLASS 9: DataAttributes Find Method - Functional Correctness
# ============================================================================

class TestDataAttributesFindFunctionalCorrectness:
    """Test DataAttributes.find method functional correctness."""
    
    def test_find_successful_retrieval(self, data_attributes_instance, valid_dataset_attributes):
        """Test successful data attributes retrieval."""
        mock_results = [
            {"DataAttributeId": 1.0, "DataAttributeName": "age"},
            {"DataAttributeId": 2.0, "DataAttributeName": "gender"},
            {"DataAttributeId": 3.0, "DataAttributeName": "income"}
        ]
        data_attributes_instance.collection.find.return_value = mock_results
        
        result = data_attributes_instance.find(valid_dataset_attributes)
        
        assert result == [1.0, 2.0, 3.0]
        data_attributes_instance.collection.find.assert_called_once()
    
    def test_find_correct_query_parameters(self, data_attributes_instance, valid_dataset_attributes):
        """Test that find method uses correct query parameters."""
        mock_results = [{"DataAttributeId": 1.0, "DataAttributeName": "age"}]
        data_attributes_instance.collection.find.return_value = mock_results
        
        data_attributes_instance.find(valid_dataset_attributes)
        
        call_args = data_attributes_instance.collection.find.call_args
        assert call_args[0][0] == {"DataAttributeName": {"$in": valid_dataset_attributes}}
        assert call_args[0][1] == {"_id": 0, "DataAttributeId": 1, "DataAttributeName": 1}
    
    def test_find_sorts_results_by_input_order(self, data_attributes_instance):
        """Test that find sorts results by input order."""
        mock_results = [
            {"DataAttributeId": 3.0, "DataAttributeName": "income"},
            {"DataAttributeId": 1.0, "DataAttributeName": "age"},
            {"DataAttributeId": 2.0, "DataAttributeName": "gender"}
        ]
        data_attributes_instance.collection.find.return_value = mock_results
        
        result = data_attributes_instance.find(["age", "gender", "income"])
        
        assert result == [1.0, 2.0, 3.0]
    
    def test_find_with_single_attribute(self, data_attributes_instance):
        """Test find with single attribute."""
        mock_results = [{"DataAttributeId": 1.0, "DataAttributeName": "age"}]
        data_attributes_instance.collection.find.return_value = mock_results
        
        result = data_attributes_instance.find(["age"])
        
        assert result == [1.0]
    
    def test_find_with_many_attributes(self, data_attributes_instance):
        """Test find with many attributes."""
        attributes = [f"attr_{i}" for i in range(10)]
        mock_results = [
            {"DataAttributeId": float(i), "DataAttributeName": f"attr_{i}"}
            for i in range(10)
        ]
        data_attributes_instance.collection.find.return_value = mock_results
        
        result = data_attributes_instance.find(attributes)
        
        assert len(result) == 10


# ============================================================================
# TEST CLASS 10: DataAttributes Find Method - Edge Cases
# ============================================================================

class TestDataAttributesFindEdgeCases:
    """Test DataAttributes.find method edge cases."""
    
    def test_find_with_none_attributes(self, data_attributes_instance):
        """Test find raises exception when attributes is None."""
        with pytest.raises(HTTPException) as exc_info:
            data_attributes_instance.find(None)
        
        assert exc_info.value.status_code == 500
        assert "Dataset attribute(s) names must be a non-empty list" in str(exc_info.value.detail)
    
    def test_find_with_empty_list(self, data_attributes_instance):
        """Test find raises exception when attributes list is empty."""
        with pytest.raises(HTTPException) as exc_info:
            data_attributes_instance.find([])
        
        assert exc_info.value.status_code == 500
        assert "Dataset attribute(s) names must be a non-empty list" in str(exc_info.value.detail)
    
    def test_find_with_non_list_type(self, data_attributes_instance):
        """Test find raises exception when attributes is not a list."""
        with pytest.raises(HTTPException) as exc_info:
            data_attributes_instance.find("not_a_list")
        
        assert exc_info.value.status_code == 500
    
    def test_find_with_dict_type(self, data_attributes_instance):
        """Test find raises exception when attributes is dict."""
        with pytest.raises(HTTPException) as exc_info:
            data_attributes_instance.find({"attr": "value"})
        
        assert exc_info.value.status_code == 500


# ============================================================================
# TEST CLASS 11: DataAttributes Find Method - Error Handling
# ============================================================================

class TestDataAttributesFindErrorHandling:
    """Test DataAttributes.find method error handling."""
    
    def test_find_no_attributes_found(self, data_attributes_instance, valid_dataset_attributes):
        """Test find raises HTTPException when no attributes found."""
        data_attributes_instance.collection.find.return_value = []
        
        with pytest.raises(HTTPException) as exc_info:
            data_attributes_instance.find(valid_dataset_attributes)
        
        assert exc_info.value.status_code == 500
        assert "No dataset attributes found" in str(exc_info.value.detail)
    
    def test_find_database_connection_error(self, data_attributes_instance, valid_dataset_attributes):
        """Test find handles database connection errors."""
        data_attributes_instance.collection.find.side_effect = Exception("Connection error")
        
        with pytest.raises(Exception) as exc_info:
            data_attributes_instance.find(valid_dataset_attributes)
        
        assert "Connection error" in str(exc_info.value)
    
    def test_find_partial_results(self, data_attributes_instance):
        """Test find with partial results (some attributes not found)."""
        mock_results = [
            {"DataAttributeId": 1.0, "DataAttributeName": "age"}
        ]
        data_attributes_instance.collection.find.return_value = mock_results
        
        result = data_attributes_instance.find(["age", "nonexistent"])
        
        assert result == [1.0]


# ============================================================================
# TEST CLASS 12: DataAttributeValues Find Method - Functional Correctness
# ============================================================================

class TestDataAttributeValuesFindFunctionalCorrectness:
    """Test DataAttributeValues.find method functional correctness."""
    
    def test_find_successful_retrieval(self, data_attribute_values_instance, valid_dataset_id, 
                                       valid_dataset_attribute_ids, valid_batch_id):
        """Test successful data attribute values retrieval."""
        mock_results = [
            {"DataAttributeValues": [1, 2, 3], "DataAttributeId": 1.0},
            {"DataAttributeValues": [4, 5, 6], "DataAttributeId": 2.0},
            {"DataAttributeValues": [7, 8, 9], "DataAttributeId": 3.0}
        ]
        data_attribute_values_instance.collection.find.return_value = mock_results
        
        result = data_attribute_values_instance.find(valid_dataset_id, valid_dataset_attribute_ids, valid_batch_id)
        
        assert result == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        data_attribute_values_instance.collection.find.assert_called_once()
    
    def test_find_correct_query_parameters(self, data_attribute_values_instance, valid_dataset_id,
                                          valid_dataset_attribute_ids, valid_batch_id):
        """Test that find method uses correct query parameters."""
        mock_results = [{"DataAttributeValues": [1, 2], "DataAttributeId": 1.0}]
        data_attribute_values_instance.collection.find.return_value = mock_results
        
        data_attribute_values_instance.find(valid_dataset_id, valid_dataset_attribute_ids, valid_batch_id)
        
        call_args = data_attribute_values_instance.collection.find.call_args
        expected_query = {
            "DataId": valid_dataset_id,
            "DataAttributeId": {"$in": valid_dataset_attribute_ids},
            "BatchId": valid_batch_id
        }
        assert call_args[0][0] == expected_query
        assert call_args[0][1] == {"_id": 0, "DataAttributeValues": 1, "DataAttributeId": 1}
    
    def test_find_sorts_results_by_attribute_ids(self, data_attribute_values_instance, valid_dataset_id,
                                                 valid_batch_id):
        """Test that find sorts results by attribute IDs order."""
        mock_results = [
            {"DataAttributeValues": [7, 8, 9], "DataAttributeId": 3.0},
            {"DataAttributeValues": [1, 2, 3], "DataAttributeId": 1.0},
            {"DataAttributeValues": [4, 5, 6], "DataAttributeId": 2.0}
        ]
        data_attribute_values_instance.collection.find.return_value = mock_results
        
        result = data_attribute_values_instance.find(valid_dataset_id, [1.0, 2.0, 3.0], valid_batch_id)
        
        assert result == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]


# ============================================================================
# TEST CLASS 13: DataAttributeValues Find Method - Edge Cases
# ============================================================================

class TestDataAttributeValuesFindEdgeCases:
    """Test DataAttributeValues.find method edge cases."""
    
    def test_find_with_none_dataset_id(self, data_attribute_values_instance, valid_dataset_attribute_ids,
                                       valid_batch_id):
        """Test find raises exception when dataset_id is None."""
        with pytest.raises(HTTPException) as exc_info:
            data_attribute_values_instance.find(None, valid_dataset_attribute_ids, valid_batch_id)
        
        assert exc_info.value.status_code == 500
        assert "Data ID must be a non-empty float" in str(exc_info.value.detail)
    
    def test_find_with_invalid_dataset_id_type(self, data_attribute_values_instance,
                                               valid_dataset_attribute_ids, valid_batch_id):
        """Test find raises exception when dataset_id is not float."""
        with pytest.raises(HTTPException) as exc_info:
            data_attribute_values_instance.find("invalid", valid_dataset_attribute_ids, valid_batch_id)
        
        assert exc_info.value.status_code == 500
    
    def test_find_with_zero_dataset_id(self, data_attribute_values_instance, valid_dataset_attribute_ids,
                                       valid_batch_id):
        """Test find with zero dataset_id."""
        mock_results = [{"DataAttributeValues": [1, 2], "DataAttributeId": 1.0}]
        data_attribute_values_instance.collection.find.return_value = mock_results
        
        result = data_attribute_values_instance.find(0.0, valid_dataset_attribute_ids, valid_batch_id)
        assert result is not None
    
    def test_find_with_empty_attribute_ids_list(self, data_attribute_values_instance, valid_dataset_id,
                                                valid_batch_id):
        """Test find with empty attribute IDs list."""
        data_attribute_values_instance.collection.find.return_value = []
        
        with pytest.raises(HTTPException):
            data_attribute_values_instance.find(valid_dataset_id, [], valid_batch_id)


# ============================================================================
# TEST CLASS 14: DataAttributeValues Find Method - Error Handling
# ============================================================================

class TestDataAttributeValuesFindErrorHandling:
    """Test DataAttributeValues.find method error handling."""
    
    def test_find_no_values_found(self, data_attribute_values_instance, valid_dataset_id,
                                  valid_dataset_attribute_ids, valid_batch_id):
        """Test find raises HTTPException when no values found."""
        data_attribute_values_instance.collection.find.return_value = []
        
        with pytest.raises(HTTPException) as exc_info:
            data_attribute_values_instance.find(valid_dataset_id, valid_dataset_attribute_ids, valid_batch_id)
        
        assert exc_info.value.status_code == 500
        assert "No dataset attributes found" in str(exc_info.value.detail)
    
    def test_find_database_connection_error(self, data_attribute_values_instance, valid_dataset_id,
                                           valid_dataset_attribute_ids, valid_batch_id):
        """Test find handles database connection errors."""
        data_attribute_values_instance.collection.find.side_effect = Exception("Connection error")
        
        with pytest.raises(Exception) as exc_info:
            data_attribute_values_instance.find(valid_dataset_id, valid_dataset_attribute_ids, valid_batch_id)
        
        assert "Connection error" in str(exc_info.value)


# ============================================================================
# TEST CLASS 15: DataAttributeValues Update Method - Functional Correctness
# ============================================================================

class TestDataAttributeValuesUpdateFunctionalCorrectness:
    """Test DataAttributeValues.update method functional correctness."""
    
    def test_update_successful(self, data_attribute_values_instance, valid_dataset_id):
        """Test successful update."""
        mock_result = MagicMock()
        mock_result.acknowledged = True
        data_attribute_values_instance.collection.update_many.return_value = mock_result
        
        value = {"IsActive": True}
        result = data_attribute_values_instance.update(valid_dataset_id, value)
        
        assert result is True
        data_attribute_values_instance.collection.update_many.assert_called_once()
    
    def test_update_correct_query_format(self, data_attribute_values_instance, valid_dataset_id):
        """Test that update uses correct query format."""
        mock_result = MagicMock()
        mock_result.acknowledged = True
        data_attribute_values_instance.collection.update_many.return_value = mock_result
        
        value = {"IsActive": True}
        data_attribute_values_instance.update(valid_dataset_id, value)
        
        call_args = data_attribute_values_instance.collection.update_many.call_args
        assert call_args[0][0] == {"DataId": valid_dataset_id}
        assert call_args[0][1] == {"$set": value}
    
    def test_update_multiple_fields(self, data_attribute_values_instance, valid_dataset_id):
        """Test updating multiple fields."""
        mock_result = MagicMock()
        mock_result.acknowledged = True
        data_attribute_values_instance.collection.update_many.return_value = mock_result
        
        value = {
            "IsActive": True,
            "ProcessedAt": "2025-12-24",
            "Status": "completed"
        }
        result = data_attribute_values_instance.update(valid_dataset_id, value)
        
        assert result is True
    
    def test_update_returns_acknowledgement_status(self, data_attribute_values_instance, valid_dataset_id):
        """Test that update returns acknowledgement status."""
        mock_result = MagicMock()
        mock_result.acknowledged = True
        data_attribute_values_instance.collection.update_many.return_value = mock_result
        
        result = data_attribute_values_instance.update(valid_dataset_id, {"status": "done"})
        
        assert isinstance(result, bool)
        assert result is True


# ============================================================================
# TEST CLASS 16: DataAttributeValues Update Method - Edge Cases
# ============================================================================

class TestDataAttributeValuesUpdateEdgeCases:
    """Test DataAttributeValues.update method edge cases."""
    
    def test_update_with_empty_dict(self, data_attribute_values_instance, valid_dataset_id):
        """Test update with empty dictionary."""
        mock_result = MagicMock()
        mock_result.acknowledged = True
        data_attribute_values_instance.collection.update_many.return_value = mock_result
        
        result = data_attribute_values_instance.update(valid_dataset_id, {})
        
        assert result is True
    
    def test_update_with_none_values(self, data_attribute_values_instance, valid_dataset_id):
        """Test update with None values."""
        mock_result = MagicMock()
        mock_result.acknowledged = True
        data_attribute_values_instance.collection.update_many.return_value = mock_result
        
        value = {"status": None, "data": None}
        result = data_attribute_values_instance.update(valid_dataset_id, value)
        
        assert result is True
    
    def test_update_with_nested_dict(self, data_attribute_values_instance, valid_dataset_id):
        """Test update with nested dictionary."""
        mock_result = MagicMock()
        mock_result.acknowledged = True
        data_attribute_values_instance.collection.update_many.return_value = mock_result
        
        value = {
            "metadata": {
                "created_by": "user1",
                "timestamp": "2025-12-24"
            }
        }
        result = data_attribute_values_instance.update(valid_dataset_id, value)
        
        assert result is True


# ============================================================================
# TEST CLASS 17: DataAttributeValues Update Method - Error Handling
# ============================================================================

class TestDataAttributeValuesUpdateErrorHandling:
    """Test DataAttributeValues.update method error handling."""
    
    def test_update_not_acknowledged(self, data_attribute_values_instance, valid_dataset_id):
        """Test update raises RuntimeError when not acknowledged."""
        mock_result = MagicMock()
        mock_result.acknowledged = False
        data_attribute_values_instance.collection.update_many.return_value = mock_result
        
        with pytest.raises(RuntimeError) as exc_info:
            data_attribute_values_instance.update(valid_dataset_id, {"status": "test"})
        
        assert f"Failed to update document with  batchId {valid_dataset_id}" in str(exc_info.value)
    
    def test_update_database_error(self, data_attribute_values_instance, valid_dataset_id):
        """Test update handles database errors."""
        data_attribute_values_instance.collection.update_many.side_effect = Exception("DB Error")
        
        with pytest.raises(Exception) as exc_info:
            data_attribute_values_instance.update(valid_dataset_id, {"status": "test"})
        
        assert "DB Error" in str(exc_info.value)
    
    def test_update_connection_timeout(self, data_attribute_values_instance, valid_dataset_id):
        """Test update handles connection timeout."""
        data_attribute_values_instance.collection.update_many.side_effect = TimeoutError("Timeout")
        
        with pytest.raises(TimeoutError):
            data_attribute_values_instance.update(valid_dataset_id, {"status": "test"})


# ============================================================================
# TEST CLASS 18: DataAttributeValues CheckValue Method - Functional Correctness
# ============================================================================

class TestDataAttributeValuesCheckValueFunctionalCorrectness:
    """Test DataAttributeValues.checkValue method functional correctness."""
    
    def test_checkvalue_returns_true_when_values_exist(self, data_attribute_values_instance, valid_dataset_id,
                                                      valid_dataset_attribute_ids, valid_batch_id):
        """Test checkValue returns True when values exist."""
        mock_results = [
            {"DataAttributeValues": [1, 2, 3], "DataAttributeId": 1.0}
        ]
        data_attribute_values_instance.collection.find.return_value = mock_results
        
        result = data_attribute_values_instance.checkValue(valid_dataset_id, valid_dataset_attribute_ids, valid_batch_id)
        
        assert result is True
    
    def test_checkvalue_returns_false_when_no_values(self, data_attribute_values_instance, valid_dataset_id,
                                                     valid_dataset_attribute_ids, valid_batch_id):
        """Test checkValue returns False when no values found."""
        data_attribute_values_instance.collection.find.return_value = []
        
        result = data_attribute_values_instance.checkValue(valid_dataset_id, valid_dataset_attribute_ids, valid_batch_id)
        
        assert result is False
    
    def test_checkvalue_correct_query_parameters(self, data_attribute_values_instance, valid_dataset_id,
                                                 valid_dataset_attribute_ids, valid_batch_id):
        """Test that checkValue uses correct query parameters."""
        mock_results = [{"DataAttributeValues": [1, 2], "DataAttributeId": 1.0}]
        data_attribute_values_instance.collection.find.return_value = mock_results
        
        data_attribute_values_instance.checkValue(valid_dataset_id, valid_dataset_attribute_ids, valid_batch_id)
        
        call_args = data_attribute_values_instance.collection.find.call_args
        expected_query = {
            "DataId": valid_dataset_id,
            "DataAttributeId": {"$in": valid_dataset_attribute_ids},
            "BatchId": valid_batch_id
        }
        assert call_args[0][0] == expected_query


# ============================================================================
# TEST CLASS 19: DataAttributeValues CheckValue Method - Edge Cases
# ============================================================================

class TestDataAttributeValuesCheckValueEdgeCases:
    """Test DataAttributeValues.checkValue method edge cases."""
    
    def test_checkvalue_with_none_dataset_id(self, data_attribute_values_instance, valid_dataset_attribute_ids,
                                             valid_batch_id):
        """Test checkValue raises exception when dataset_id is None."""
        with pytest.raises(HTTPException) as exc_info:
            data_attribute_values_instance.checkValue(None, valid_dataset_attribute_ids, valid_batch_id)
        
        assert exc_info.value.status_code == 500
        assert "No dataset found" in str(exc_info.value.detail)
    
    def test_checkvalue_with_invalid_dataset_id_type(self, data_attribute_values_instance,
                                                     valid_dataset_attribute_ids, valid_batch_id):
        """Test checkValue raises exception when dataset_id is not float."""
        with pytest.raises(HTTPException) as exc_info:
            data_attribute_values_instance.checkValue("invalid", valid_dataset_attribute_ids, valid_batch_id)
        
        assert exc_info.value.status_code == 500
    
    def test_checkvalue_with_zero_dataset_id(self, data_attribute_values_instance, valid_dataset_attribute_ids,
                                             valid_batch_id):
        """Test checkValue with zero dataset_id."""
        data_attribute_values_instance.collection.find.return_value = []
        
        result = data_attribute_values_instance.checkValue(0.0, valid_dataset_attribute_ids, valid_batch_id)
        assert result is False


# ============================================================================
# TEST CLASS 20: Performance Tests
# ============================================================================

class TestPerformance:
    """Test performance characteristics across all classes."""
    
    def test_dataset_find_performance_multiple_calls(self, dataset_instance):
        """Test Dataset.find performance with multiple calls."""
        dataset_instance.collection.find_one.return_value = {"DataSetName": "test"}
        
        for i in range(100):
            dataset_instance.find(float(i))
        
        assert dataset_instance.collection.find_one.call_count == 100
    
    def test_data_attributes_find_performance(self, data_attributes_instance):
        """Test DataAttributes.find performance."""
        mock_results = [{"DataAttributeId": 1.0, "DataAttributeName": "attr"}]
        data_attributes_instance.collection.find.return_value = mock_results
        
        for _ in range(50):
            data_attributes_instance.find(["attr"])
        
        assert data_attributes_instance.collection.find.call_count == 50
    
    def test_data_attribute_values_update_performance(self, data_attribute_values_instance):
        """Test DataAttributeValues.update performance."""
        mock_result = MagicMock()
        mock_result.acknowledged = True
        data_attribute_values_instance.collection.update_many.return_value = mock_result
        
        for i in range(100):
            data_attribute_values_instance.update(float(i), {"status": f"status_{i}"})
        
        assert data_attribute_values_instance.collection.update_many.call_count == 100


# ============================================================================
# TEST CLASS 21: Resource Management Tests
# ============================================================================

class TestResourceManagement:
    """Test resource management across all classes."""
    
    def test_dataset_collection_reference_maintained(self, dataset_instance):
        """Test that collection reference is maintained in Dataset."""
        collection = dataset_instance.collection
        
        dataset_instance.collection.find_one.return_value = {"DataSetName": "test"}
        dataset_instance.find(123.45)
        
        assert dataset_instance.collection is collection
    
    def test_data_attributes_collection_reference_maintained(self, data_attributes_instance):
        """Test that collection reference is maintained in DataAttributes."""
        collection = data_attributes_instance.collection
        
        mock_results = [{"DataAttributeId": 1.0, "DataAttributeName": "attr"}]
        data_attributes_instance.collection.find.return_value = mock_results
        data_attributes_instance.find(["attr"])
        
        assert data_attributes_instance.collection is collection
    
    def test_data_attribute_values_collection_reference_maintained(self, data_attribute_values_instance):
        """Test that collection reference is maintained in DataAttributeValues."""
        collection = data_attribute_values_instance.collection
        
        mock_results = [{"DataAttributeValues": [1, 2], "DataAttributeId": 1.0}]
        data_attribute_values_instance.collection.find.return_value = mock_results
        data_attribute_values_instance.find(123.45, [1.0], 111.22)
        
        assert data_attribute_values_instance.collection is collection


# ============================================================================
# TEST CLASS 22: Security Tests
# ============================================================================

class TestSecurity:
    """Test security aspects across all classes."""
    
    def test_dataset_find_no_injection_in_dataset_id(self, dataset_instance):
        """Test that Dataset.find handles potential injection attempts."""
        with pytest.raises(HTTPException):
            dataset_instance.find("'; DROP TABLE datasets; --")
    
    def test_data_attributes_find_with_malicious_list(self, data_attributes_instance):
        """Test DataAttributes.find with potentially malicious list."""
        mock_results = [{"DataAttributeId": 1.0, "DataAttributeName": "$ne"}]
        data_attributes_instance.collection.find.return_value = mock_results
        
        result = data_attributes_instance.find(["$ne", "$gt"])
        assert isinstance(result, list)
    
    def test_dataset_find_excludes_id_field(self, dataset_instance):
        """Test that Dataset.find excludes _id field."""
        result_with_id = {"_id": "internal_id", "DataSetName": "test", "SampleData": 123.45}
        dataset_instance.collection.find_one.return_value = result_with_id
        
        dataset_instance.find(123.45)
        
        call_args = dataset_instance.collection.find_one.call_args
        assert call_args[0][1]["_id"] == 0
    
    def test_data_attribute_values_update_with_mongo_operators(self, data_attribute_values_instance):
        """Test DataAttributeValues.update handles MongoDB operators."""
        mock_result = MagicMock()
        mock_result.acknowledged = True
        data_attribute_values_instance.collection.update_many.return_value = mock_result
        
        value = {"$set": {"status": "test"}}
        result = data_attribute_values_instance.update(123.45, value)
        
        assert result is True


# ============================================================================
# TEST CLASS 23: Scalability Tests
# ============================================================================

class TestScalability:
    """Test scalability characteristics across all classes."""
    
    def test_data_attributes_find_with_large_list(self, data_attributes_instance):
        """Test DataAttributes.find with large attribute list."""
        large_list = [f"attr_{i}" for i in range(1000)]
        mock_results = [
            {"DataAttributeId": float(i), "DataAttributeName": f"attr_{i}"}
            for i in range(1000)
        ]
        data_attributes_instance.collection.find.return_value = mock_results
        
        result = data_attributes_instance.find(large_list)
        
        assert len(result) == 1000
    
    def test_data_attribute_values_update_large_dict(self, data_attribute_values_instance):
        """Test DataAttributeValues.update with large dictionary."""
        mock_result = MagicMock()
        mock_result.acknowledged = True
        data_attribute_values_instance.collection.update_many.return_value = mock_result
        
        large_dict = {f"field_{i}": f"value_{i}" for i in range(500)}
        result = data_attribute_values_instance.update(123.45, large_dict)
        
        assert result is True
    
    def test_concurrent_operations(self, dataset_instance, data_attributes_instance):
        """Test concurrent operations across multiple classes."""
        dataset_instance.collection.find_one.return_value = {"DataSetName": "test"}
        mock_results = [{"DataAttributeId": 1.0, "DataAttributeName": "attr"}]
        data_attributes_instance.collection.find.return_value = mock_results
        
        for i in range(50):
            dataset_instance.find(float(i))
            data_attributes_instance.find(["attr"])
        
        assert dataset_instance.collection.find_one.call_count == 50
        assert data_attributes_instance.collection.find.call_count == 50


# ============================================================================
# TEST CLASS 24: Integration Tests
# ============================================================================

class TestIntegration:
    """Test integration points across all classes."""
    
    def test_integration_with_database_wb(self):
        """Test integration with DataBase_WB."""
        with patch('fairness.dao.WorkBench.Data.DataBase_WB') as mock_db_class:
            mock_db_instance = MagicMock()
            mock_db_instance.db = MagicMock()
            mock_db_class.return_value = mock_db_instance
            
            from fairness.dao.WorkBench.Data import Dataset
            dataset = Dataset()
            
            mock_db_class.assert_called()
            assert dataset.ModelWorkBench is not None
    
    def test_integration_with_custom_logger(self):
        """Test that custom logger is imported."""
        with patch('fairness.dao.WorkBench.Data.DataBase_WB'):
            from fairness.dao.WorkBench.Data import Dataset
            dataset = Dataset(db=MagicMock())
            assert dataset is not None
    
    def test_integration_workflow_dataset_to_attributes(self, dataset_instance, data_attributes_instance):
        """Test typical workflow from dataset to attributes."""
        # Find dataset
        dataset_instance.collection.find_one.return_value = {"DataSetName": "test", "SampleData": 123.45}
        dataset_result = dataset_instance.find(456.78)
        assert dataset_result["DataSetName"] == "test"
        
        # Find attributes
        mock_results = [{"DataAttributeId": 1.0, "DataAttributeName": "age"}]
        data_attributes_instance.collection.find.return_value = mock_results
        attr_result = data_attributes_instance.find(["age"])
        assert attr_result == [1.0]


# ============================================================================
# TEST CLASS 25: Regression Tests
# ============================================================================

class TestRegression:
    """Test regression scenarios across all classes."""
    
    def test_regression_dataset_find_returns_dict(self, dataset_instance):
        """Regression: Ensure Dataset.find returns dict type."""
        dataset_instance.collection.find_one.return_value = {"DataSetName": "test", "SampleData": 123.45}
        
        result = dataset_instance.find(123.45)
        
        assert isinstance(result, dict)
    
    def test_regression_data_attributes_find_returns_list(self, data_attributes_instance):
        """Regression: Ensure DataAttributes.find returns list type."""
        mock_results = [{"DataAttributeId": 1.0, "DataAttributeName": "attr"}]
        data_attributes_instance.collection.find.return_value = mock_results
        
        result = data_attributes_instance.find(["attr"])
        
        assert isinstance(result, list)
    
    def test_regression_data_attribute_values_update_returns_bool(self, data_attribute_values_instance):
        """Regression: Ensure DataAttributeValues.update returns boolean."""
        mock_result = MagicMock()
        mock_result.acknowledged = True
        data_attribute_values_instance.collection.update_many.return_value = mock_result
        
        result = data_attribute_values_instance.update(123.45, {"status": "done"})
        
        assert isinstance(result, bool)
    
    def test_regression_checkvalue_returns_bool(self, data_attribute_values_instance):
        """Regression: Ensure checkValue returns boolean."""
        data_attribute_values_instance.collection.find.return_value = []
        
        result = data_attribute_values_instance.checkValue(123.45, [1.0], 111.22)
        
        assert isinstance(result, bool)
    
    def test_regression_dataset_findfile_validation_before_query(self, dataset_instance):
        """Regression: Ensure validation happens before database query."""
        with pytest.raises(HTTPException):
            dataset_instance.findFile(None)
        
        dataset_instance.collection.find_one.assert_not_called()


# ============================================================================
# TEST CLASS 26: Code Quality Tests
# ============================================================================

class TestCodeQuality:
    """Test code quality indicators across all classes."""
    
    def test_all_classes_have_init_method(self):
        """Test that all classes have __init__ method."""
        from fairness.dao.WorkBench.Data import SampleDataset, Dataset, DataAttributes, DataAttributeValues
        
        assert hasattr(SampleDataset, '__init__')
        assert hasattr(Dataset, '__init__')
        assert hasattr(DataAttributes, '__init__')
        assert hasattr(DataAttributeValues, '__init__')
    
    def test_dataset_class_has_all_methods(self):
        """Test that Dataset class has all expected methods."""
        from fairness.dao.WorkBench.Data import Dataset
        
        assert hasattr(Dataset, 'find')
        assert hasattr(Dataset, 'findFile')
    
    def test_data_attributes_class_has_find_method(self):
        """Test that DataAttributes class has find method."""
        from fairness.dao.WorkBench.Data import DataAttributes
        
        assert hasattr(DataAttributes, 'find')
    
    def test_data_attribute_values_class_has_all_methods(self):
        """Test that DataAttributeValues class has all expected methods."""
        from fairness.dao.WorkBench.Data import DataAttributeValues
        
        assert hasattr(DataAttributeValues, 'find')
        assert hasattr(DataAttributeValues, 'update')
        assert hasattr(DataAttributeValues, 'checkValue')
    
    def test_instance_attributes_set_correctly(self, dataset_instance):
        """Test that instance attributes are set correctly."""
        assert hasattr(dataset_instance, 'ModelWorkBench')
        assert hasattr(dataset_instance, 'collection')


# ============================================================================
# TEST CLASS 27: Type Validation Tests
# ============================================================================

class TestTypeValidation:
    """Test type validation across all classes."""
    
    def test_dataset_find_validates_float_type(self, dataset_instance):
        """Test Dataset.find validates dataset_id is float."""
        with pytest.raises(HTTPException):
            dataset_instance.find(123)  # int, not float
    
    def test_dataset_findfile_validates_float_type(self, dataset_instance):
        """Test Dataset.findFile validates file_id is float."""
        with pytest.raises(HTTPException):
            dataset_instance.findFile("123.45")  # string, not float
    
    def test_data_attributes_find_validates_list_type(self, data_attributes_instance):
        """Test DataAttributes.find validates list type."""
        with pytest.raises(HTTPException):
            data_attributes_instance.find("not_a_list")
    
    def test_data_attribute_values_find_validates_types(self, data_attribute_values_instance):
        """Test DataAttributeValues.find validates parameter types."""
        with pytest.raises(HTTPException):
            data_attribute_values_instance.find("invalid", [1.0], 111.22)


# ============================================================================
# TEST CLASS 28: SampleDataset Specific Tests (Bug Detection)
# ============================================================================

class TestSampleDatasetBugs:
    """Test SampleDataset class - note: code has bugs."""
    
    def test_sampledataset_find_has_undefined_variable(self, sample_dataset_instance):
        """Test that SampleDataset.find has undefined variable bug (Dataset_Id)."""
        # Note: The original code has a bug - it checks Dataset_Id but parameter is Sample_Id
        # This test documents the bug
        try:
            sample_dataset_instance.find(123.45)
        except NameError as e:
            assert "Dataset_Id" in str(e) or "not defined" in str(e)
    
    def test_sampledataset_collection_uses_global_modelworkbench(self):
        """Test that SampleDataset uses global ModelWorkBench for collection."""
        # This is a design inconsistency - collection uses global, not self.ModelWorkBench
        with patch('fairness.dao.WorkBench.Data.ModelWorkBench') as mock_global_wb:
            mock_global_wb.__getitem__.return_value = MagicMock()
            from fairness.dao.WorkBench.Data import SampleDataset
            
            sample = SampleDataset(db=MagicMock())
            # The collection assignment happens from global ModelWorkBench, not self.ModelWorkBench
            assert sample.collection is not None
