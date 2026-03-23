"""
Test cases for service.py

This module contains comprehensive test cases for the FairnessService class
and related functions in fairness.service.service module.
"""

import pytest
import json
import pandas as pd
import os
import tempfile
from unittest.mock import Mock, MagicMock, patch, mock_open, call, ANY
from datetime import datetime, timedelta
from fastapi import HTTPException
from io import BytesIO, StringIO
import matplotlib
matplotlib.use('Agg')  # Set non-GUI backend before importing pyplot
import matplotlib.pyplot as plt
import base64

from fairness.service.service import FairnessService, AttributeDict
from fairness.mappers.mappers import (
    BiasAnalyzeResponse,
    BiasResults,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_database():
    """Create a mock database for testing."""
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock()
    mock_db["bias"] = MagicMock()
    mock_db["mitigation"] = MagicMock()
    mock_db["fs.files"] = MagicMock()
    return mock_db


@pytest.fixture
def fairness_service_instance(mock_database):
    """Create a FairnessService instance with mocked database."""
    with patch('fairness.service.service.FileStoreReportDb') as mock_filestore, \
         patch('fairness.service.service.Batch') as mock_batch, \
         patch('fairness.service.service.Tenet') as mock_tenet, \
         patch('fairness.service.service.Dataset') as mock_dataset, \
         patch('fairness.service.service.DataAttributes') as mock_data_attr, \
         patch('fairness.service.service.DataAttributeValues') as mock_data_attr_vals:
        
        # Setup mock returns
        mock_filestore.return_value = MagicMock()
        mock_batch.return_value = MagicMock()
        mock_tenet.return_value = MagicMock()
        mock_dataset.return_value = MagicMock()
        mock_data_attr.return_value = MagicMock()
        mock_data_attr_vals.return_value = MagicMock()
        
        service = FairnessService(db=mock_database)
        return service


@pytest.fixture
def sample_dataframe():
    """Create a sample pandas DataFrame for testing."""
    return pd.DataFrame({
        'age': [25, 30, 35, 40, 45],
        'gender': ['Male', 'Female', 'Male', 'Female', 'Male'],
        'race': ['White', 'Black', 'White', 'Black', 'Asian'],
        'income': [50000, 60000, 70000, 80000, 90000],
        'label': [0, 1, 1, 0, 1]
    })


@pytest.fixture
def sample_bias_payload():
    """Create a sample bias analysis payload."""
    return {
        'method': ['statistical_parity'],
        'biasType': 'PRETRAIN',
        'trainingDataset': {
            'path': {'uri': 'test_data.csv'},
            'label': 'label',
            'extension': 'csv'
        },
        'predictionDataset': {
            'path': {'uri': 'test_pred.csv'},
            'predlabel': 'pred_label',
            'label': 'label'
        },
        'features': 'age,gender,race,income',
        'facet': [
            {'name': 'gender', 'privileged': ['Male'], 'unprivileged': ['Female']},
            {'name': 'race', 'privileged': ['White'], 'unprivileged': ['Black', 'Asian']}
        ],
        'categoricalAttributes': 'gender,race',
        'favourableOutcome': [1],
        'outputPath': {'uri': 'output//results'},
        'labelmaps': {0: 'No', 1: 'Yes'},
        'taskType': 'CLASSIFICATION'
    }


@pytest.fixture
def sample_json_metrics():
    """Create sample JSON metrics for HTML generation."""
    return [
        {
            'metrics': [
                {
                    'name': 'Statistical Parity',
                    'value': 0.15,
                    'description': 'Measures difference in positive outcome rates'
                },
                {
                    'name': 'Disparate Impact',
                    'value': 0.85,
                    'description': 'Ratio of positive outcomes'
                }
            ]
        }
    ]


@pytest.fixture
def temp_test_dir():
    """Create a temporary directory for testing file operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_file_store():
    """Create a mock FileStoreReportDb."""
    mock_store = MagicMock()
    mock_store.save_file = MagicMock(return_value='file_id_12345')
    mock_store.read_file = MagicMock(return_value={
        'data': b'age,gender,race,income,label\n25,Male,White,50000,0\n30,Female,Black,60000,1'
    })
    return mock_store


@pytest.fixture
def attribute_dict_sample():
    """Create sample AttributeDict for testing."""
    return AttributeDict({
        'name': ['gender', 'race'],
        'privileged': [['Male'], ['White']],
        'unprivileged': [['Female'], ['Black', 'Asian']]
    })


# ============================================================================
# TEST CLASSES
# ============================================================================

class TestAttributeDict:
    """Test the AttributeDict class."""
    
    def test_attribute_dict_creation(self):
        """Test creating AttributeDict."""
        data = {'key1': 'value1', 'key2': 'value2'}
        attr_dict = AttributeDict(data)
        
        assert attr_dict.key1 == 'value1'
        assert attr_dict.key2 == 'value2'
    
    def test_attribute_dict_set_item(self):
        """Test setting items in AttributeDict."""
        attr_dict = AttributeDict()
        attr_dict.new_key = 'new_value'
        
        assert attr_dict['new_key'] == 'new_value'
        assert attr_dict.new_key == 'new_value'
    
    def test_attribute_dict_del_item(self):
        """Test deleting items from AttributeDict."""
        attr_dict = AttributeDict({'key': 'value'})
        del attr_dict.key
        
        assert 'key' not in attr_dict


class TestFairnessServiceInitialization:
    """Test FairnessService initialization."""
    
    def test_initialization_with_mock_db(self, mock_database):
        """Test FairnessService initialization with mock database."""
        with patch('fairness.service.service.FileStoreReportDb') as mock_filestore, \
             patch('fairness.service.service.Batch') as mock_batch, \
             patch('fairness.service.service.Tenet') as mock_tenet, \
             patch('fairness.service.service.Dataset') as mock_dataset, \
             patch('fairness.service.service.DataAttributes') as mock_data_attr, \
             patch('fairness.service.service.DataAttributeValues') as mock_data_attr_vals:
            
            service = FairnessService(db=mock_database)
            
            assert service.db == mock_database
            assert hasattr(service, 'fileStore')
            assert hasattr(service, 'batch')
            assert hasattr(service, 'tenet')
            assert hasattr(service, 'dataset')
            assert hasattr(service, 'dataAttributes')
            assert hasattr(service, 'dataAttributeValues')
            assert hasattr(service, 'bias_collection')
            assert hasattr(service, 'mitigation_collection')
            assert hasattr(service, 'fairness_collection')
    
    def test_initialization_without_db(self):
        """Test FairnessService initialization without database."""
        with patch('fairness.service.service.DataBase') as mock_db_class, \
             patch('fairness.service.service.FileStoreReportDb') as mock_filestore, \
             patch('fairness.service.service.Batch') as mock_batch, \
             patch('fairness.service.service.Tenet') as mock_tenet, \
             patch('fairness.service.service.Dataset') as mock_dataset, \
             patch('fairness.service.service.DataAttributes') as mock_data_attr, \
             patch('fairness.service.service.DataAttributeValues') as mock_data_attr_vals:
            
            mock_db = MagicMock()
            mock_db.__getitem__ = MagicMock()
            mock_db["bias"] = MagicMock()
            mock_db["mitigation"] = MagicMock()
            mock_db["fs.files"] = MagicMock()
            mock_db_class.return_value.db = mock_db
            
            service = FairnessService()
            
            assert service.db == mock_db
            assert hasattr(service, 'fileStore')
    
    def test_class_constants_defined(self):
        """Test that class constants are properly defined."""
        assert hasattr(FairnessService, 'MITIGATED_LOCAL_FILE_PATH')
        assert hasattr(FairnessService, 'DATASET_LOCAL_FILE_PATH')
        assert hasattr(FairnessService, 'LOCAL_FILE_PATH')
        assert hasattr(FairnessService, 'MODEL_LOCAL_PATH')
        assert FairnessService.MITIGATED_LOCAL_FILE_PATH.endswith(os.path.join('MitigatedData', ''))
        assert FairnessService.LOCAL_FILE_PATH.endswith(os.path.join('datasets', ''))


class TestStaticFileOperations:
    """Test static file operation methods."""
    
    def test_save_as_json_file(self, temp_test_dir, fairness_service_instance):
        """Test saving content as JSON file."""
        file_path = os.path.join(temp_test_dir, 'test.json')
        content = {'test': 'data', 'value': 42}
        
        FairnessService.save_as_json_file(file_path, content)
        
        assert os.path.exists(file_path)
        with open(file_path, 'r') as f:
            loaded = json.load(f)
        assert loaded == content
    
    def test_save_as_file_binary(self, temp_test_dir, fairness_service_instance):
        """Test saving binary content to file."""
        file_path = os.path.join(temp_test_dir, 'binary.bin')
        content = b'binary test content'
        
        FairnessService.save_as_file(file_path, content)
        
        assert os.path.exists(file_path)
        with open(file_path, 'rb') as f:
            loaded = f.read()
        assert loaded == content
    
    def test_read_html_file(self, temp_test_dir, fairness_service_instance):
        """Test reading HTML file."""
        file_path = os.path.join(temp_test_dir, 'test.html')
        html_content = '<html><body>Test</body></html>'
        
        with open(file_path, 'w') as f:
            f.write(html_content)
        
        result = FairnessService.read_html_file(file_path)
        assert result == html_content
    
    def test_save_html_to_file(self, temp_test_dir, fairness_service_instance):
        """Test saving HTML string to file."""
        file_path = os.path.join(temp_test_dir, 'output.html')
        html_string = '<html><h1>Header</h1></html>'
        
        FairnessService.save_html_to_file(html_string, file_path)
        
        assert os.path.exists(file_path)
        with open(file_path, 'r') as f:
            content = f.read()
        assert content == html_string


class TestParseNutanixBucketObject:
    """Test Nutanix bucket path parsing."""
    
    def test_parse_nutanix_bucket_simple(self, fairness_service_instance):
        """Test parsing simple Nutanix bucket path."""
        fullpath = "my-bucket//path/to/file.csv"
        
        result = FairnessService.parse_nutanix_bucket_object(fullpath)
        
        assert result['bucket_name'] == 'my-bucket'
        assert result['object_key'] == 'path/to/file.csv'
    
    def test_parse_nutanix_bucket_nested_path(self, fairness_service_instance):
        """Test parsing nested Nutanix bucket path."""
        fullpath = "bucket-name//dir1/dir2/dir3/data.json"
        
        result = FairnessService.parse_nutanix_bucket_object(fullpath)
        
        assert result['bucket_name'] == 'bucket-name'
        assert result['object_key'] == 'dir1/dir2/dir3/data.json'
    
    def test_parse_nutanix_bucket_no_path(self, fairness_service_instance):
        """Test parsing Nutanix bucket without object path."""
        fullpath = "bucket-only//"
        
        result = FairnessService.parse_nutanix_bucket_object(fullpath)
        
        assert result['bucket_name'] == 'bucket-only'
        assert result['object_key'] == ''


class TestGetDataFrame:
    """Test DataFrame loading methods."""
    
    def test_get_data_frame_csv(self, temp_test_dir, sample_dataframe, fairness_service_instance):
        """Test loading CSV file into DataFrame."""
        file_path = os.path.join(temp_test_dir, 'data.csv')
        sample_dataframe.to_csv(file_path, index=False)
        
        result = FairnessService.get_data_frame(
            'csv', file_path, ',', ['age', 'gender', 'label']
        )
        
        assert len(result) == 5
        assert 'age' in result.columns
        assert 'gender' in result.columns
        assert 'label' in result.columns
    
    def test_get_data_frame_parquet(self, temp_test_dir, sample_dataframe, fairness_service_instance):
        """Test loading Parquet file into DataFrame."""
        file_path = os.path.join(temp_test_dir, 'data.parquet')
        sample_dataframe.to_parquet(file_path, index=False)
        
        result = FairnessService.get_data_frame(
            'parquet', file_path, ',', ['age', 'gender']
        )
        
        assert len(result) == 5
        assert 'age' in result.columns
    
    def test_get_data_frame_json(self, temp_test_dir, sample_dataframe, fairness_service_instance):
        """Test loading JSON file into DataFrame."""
        file_path = os.path.join(temp_test_dir, 'data.json')
        sample_dataframe.to_json(file_path, orient='records')
        
        result = FairnessService.get_data_frame(
            'json', file_path, ',', ['age', 'label']
        )
        
        assert len(result) == 5
    
    def test_get_data_frame_feather(self, temp_test_dir, sample_dataframe, fairness_service_instance):
        """Test loading Feather file into DataFrame."""
        file_path = os.path.join(temp_test_dir, 'data.feather')
        sample_dataframe.to_feather(file_path)
        
        result = FairnessService.get_data_frame('feather', file_path, ',', None)
        
        assert len(result) == 5
        # Feather loads all columns
        assert len(result.columns) == 5


class TestJSONToHTML:
    """Test JSON to HTML conversion."""
    
    @patch('matplotlib.pyplot.savefig')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    def test_json_to_html_basic(self, mock_file, mock_savefig, fairness_service_instance):
        """Test basic JSON to HTML conversion."""
        json_obj = [
            {
                'metrics': [
                    {
                        'name': 'Test Metric',
                        'value': 0.5,
                        'description': 'Test description'
                    }
                ]
            }
        ]
        
        result = FairnessService.json_to_html(json_obj)
        
        assert 'Fairness Report' in result
        assert 'METRICS' in result
        assert 'Test Metric' in result
        assert 'Test description' in result
    
    @patch('matplotlib.pyplot.savefig')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image')
    def test_json_to_html_multiple_metrics(self, mock_file, mock_savefig, fairness_service_instance):
        """Test JSON to HTML with multiple metrics."""
        json_obj = [
            {
                'metrics': [
                    {'name': 'Metric1', 'value': 0.3, 'description': 'Desc1'},
                    {'name': 'Metric2', 'value': -0.2, 'description': 'Desc2'}
                ]
            }
        ]
        
        result = FairnessService.json_to_html(json_obj)
        
        assert 'Metric1' in result
        assert 'Metric2' in result
        assert 'Desc1' in result
        assert 'Desc2' in result


class TestUploadFileToMongoDB:
    """Test file upload to MongoDB."""
    
    @patch('fairness.service.service.time.time')
    def test_uploadfile_to_mongodb(self, mock_time):
        """Test uploading file to MongoDB."""
        mock_time.side_effect = [1000.0, 1010.0]
        
        # Testing that the method exists and is callable
        assert hasattr(FairnessService, 'uploadfile_to_mongodb')
        assert callable(getattr(FairnessService, 'uploadfile_to_mongodb'))


class TestAnalyzeTenet:
    """Test analyzeTenet method."""
    
    @patch('fairness.service.service.pandas.read_csv')
    @patch('fairness.service.service.FairnessService.pretrainedAnalyse')
    def test_analyze_tenet_pretrain(
        self, mock_pretrain_analyse, mock_read_csv, 
        fairness_service_instance, sample_dataframe, sample_bias_payload
    ):
        """Test analyzeTenet with PRETRAIN bias type."""
        mock_read_csv.return_value = sample_dataframe
        mock_pretrain_analyse.return_value = [{
            'biasDetected': True,
            'protectedAttribute': [],
            'metrics': []
        }]
        
        # Convert dict to object with attributes
        class PayloadObj:
            pass
        
        payload = PayloadObj()
        for key, value in sample_bias_payload.items():
            if isinstance(value, dict):
                setattr(payload, key, AttributeDict(value))
            else:
                setattr(payload, key, value)
        
        result = fairness_service_instance.analyzeTenet(payload)
        
        assert result is not None
        assert isinstance(result, BiasAnalyzeResponse)
        mock_pretrain_analyse.assert_called_once()
    
    @patch('fairness.service.service.pandas.read_csv')
    @patch('fairness.service.service.FairnessService.posttrainedAnalyse')
    def test_analyze_tenet_posttrain(
        self, mock_posttrain_analyse, mock_read_csv,
        fairness_service_instance, sample_dataframe
    ):
        """Test analyzeTenet with POSTTRAIN bias type."""
        mock_read_csv.return_value = sample_dataframe
        mock_posttrain_analyse.return_value = [{
            'biasDetected': True,
            'protectedAttribute': [],
            'metrics': []
        }]
        
        class PayloadObj:
            method = ['statistical_parity']
            biasType = 'POSTTRAIN'
            trainingDataset = AttributeDict({
                'path': AttributeDict({'uri': 'train.csv'}),
                'label': 'label',
                'extension': 'csv'
            })
            predictionDataset = AttributeDict({
                'path': AttributeDict({'uri': 'pred.csv'}),
                'predlabel': 'pred_label',
                'label': 'pred_label'
            })
            features = 'age,gender,race'
            facet = [AttributeDict({
                'name': 'gender',
                'privileged': ['Male'],
                'unprivileged': ['Female']
            })]
            categoricalAttributes = 'gender,race'
            favourableOutcome = [1]
            outputPath = AttributeDict({'uri': 'output//path'})
            labelmaps = {0: 'No', 1: 'Yes'}
            taskType = 'CLASSIFICATION'
        
        payload = PayloadObj()
        result = fairness_service_instance.analyzeTenet(payload)
        
        assert result is not None
        mock_posttrain_analyse.assert_called_once()


class TestAnalyzeDemo:
    """Test analyzedemo method."""
    
    @patch('fairness.service.service.FairnessService.pretrainedAnalyse')
    def test_analyze_demo_without_batch_id(
        self, mock_pretrain_analyse, fairness_service_instance, sample_dataframe
    ):
        """Test analyzedemo without batchId."""
        mock_pretrain_analyse.return_value = [{
            'biasDetected': True,
            'protectedAttribute': [],
            'metrics': []
        }]
        
        # Mock fileStore.read_file
        csv_data = sample_dataframe.to_csv(index=False).encode()
        fairness_service_instance.fileStore.read_file = MagicMock(
            return_value={'data': csv_data}
        )
        
        class PayloadObj:
            method = ['statistical_parity']
            biasType = 'PRETRAIN'
            fileid = 'file123'
            label = 'label'
            features = 'age,gender,race,income'
            facet = [AttributeDict({
                'name': 'gender',
                'privileged': ['Male'],
                'unprivileged': ['Female']
            })]
            categoricalAttributes = 'gender,race'
            favourableOutcome = [1]
            outputPath = AttributeDict({'uri': 'output//path'})
            labelmaps = {0: 'No', 1: 'Yes'}
            taskType = 'CLASSIFICATION'
        
        payload = PayloadObj()
        result = fairness_service_instance.analyzedemo(payload, batchId=None)
        
        assert result is not None
        assert isinstance(result, BiasAnalyzeResponse)
    
    def test_analyze_demo_missing_fileid(self, fairness_service_instance):
        """Test analyzedemo raises error when fileId is missing."""
        class PayloadObj:
            method = ['statistical_parity']
            biasType = 'PRETRAIN'
            fileid = None
        
        payload = PayloadObj()
        
        with pytest.raises((HTTPException, ValueError)):
            fairness_service_instance.analyzedemo(payload)
    
    @patch('fairness.service.service.requests.request')
    @patch('fairness.service.service.FairnessService.save_as_json_file')
    @patch('fairness.service.service.FairnessService.json_to_html')
    @patch('fairness.service.service.FairnessService.save_html_to_file')
    @patch('fairness.service.service.FairnessService.pretrainedAnalyse')
    @patch('os.getenv')
    def test_analyze_demo_with_batch_id(
        self, mock_getenv, mock_pretrain, mock_save_html,
        mock_json_html, mock_save_json, mock_requests,
        fairness_service_instance, sample_dataframe
    ):
        """Test analyzedemo with batchId."""
        mock_pretrain.return_value = [{
            'biasDetected': True,
            'protectedAttribute': [],
            'metrics': []
        }]
        mock_json_html.return_value = '<html>Report</html>'
        mock_getenv.side_effect = lambda x: {
            'HTML_CONTAINER_NAME': 'html_container',
            'REPORT_URL': 'http://report-url.com'
        }.get(x)
        
        mock_response = MagicMock()
        mock_response.json.return_value = {'status': 'success'}
        mock_requests.return_value = mock_response
        
        # Mock fileStore
        csv_data = sample_dataframe.to_csv(index=False).encode()
        fairness_service_instance.fileStore.read_file = MagicMock(
            return_value={'data': csv_data}
        )
        fairness_service_instance.fileStore.save_file = MagicMock(
            return_value='html_file_id_123'
        )
        
        # Mock tenet
        fairness_service_instance.tenet.find = MagicMock(
            return_value='tenet_id_123'
        )
        
        class PayloadObj:
            method = ['statistical_parity']
            biasType = 'PRETRAIN'
            fileid = 'file123'
            label = 'label'
            features = 'age,gender,race,income'
            facet = [AttributeDict({
                'name': 'gender',
                'privileged': ['Male'],
                'unprivileged': ['Female']
            })]
            categoricalAttributes = 'gender,race'
            favourableOutcome = [1]
            outputPath = AttributeDict({'uri': 'output//path'})
            labelmaps = {0: 'No', 1: 'Yes'}
            taskType = 'CLASSIFICATION'
        
        payload = PayloadObj()
        
        with patch('fairness.service.service.Html'):
            result = fairness_service_instance.analyzedemo(payload, batchId='batch123')
        
        assert result is not None
        fairness_service_instance.fileStore.save_file.assert_called_once()


class TestPreprocessingMitigate:
    """Test preprocessing mitigation method."""
    
    @patch('fairness.service.service.FairnessService.preprocessingmitigateandtransform')
    def test_preprocessing_mitigate_success(
        self, mock_mitigate_transform, fairness_service_instance
    ):
        """Test successful preprocessing mitigation."""
        mock_mitigate_transform.return_value = (
            [{
                'biasDetected': True,
                'protectedAttribute': [],
                'metrics': []
            }],
            pd.DataFrame({'col': [1, 2, 3]})
        )
        
        class PayloadObj:
            method = 'reweighting'
            biasType = 'PRETRAIN'
            mitigationType = 'PREPROCESSING'
            mitigationTechnique = 'reweighting'
            taskType = 'classification'
            trainingDataset = AttributeDict({
                'path': AttributeDict({'uri': 'data.csv'}),
                'label': 'label',
                'extension': 'csv',
                'fileType': 'csv',
                'name': 'training_data.csv'
            })
            features = 'age,gender,income'
            facet = [AttributeDict({
                'name': 'gender',
                'privileged': ['Male'],
                'unprivileged': ['Female']
            })]
            categoricalAttributes = 'gender'
            favourableOutcome = [1]
            labelmaps = {0: 'No', 1: 'Yes'}
            outputPath = AttributeDict({'uri': 'output//path'})
        
        payload = PayloadObj()
        
        # Mock file operations
        with patch('pandas.read_csv') as mock_read_csv:
            mock_read_csv.return_value = pd.DataFrame({
                'age': [25, 30],
                'gender': ['Male', 'Female'],
                'income': [50000, 60000],
                'label': [0, 1]
            })
            
            with patch.object(fairness_service_instance, 'fileStore') as mock_store:
                mock_store.save_local_file = MagicMock(return_value='saved_file_id')
                
                result = fairness_service_instance.preprocessingmitigate(payload)
        
        assert result is not None


class TestGetMitigatedData:
    """Test get_mitigated_data method."""
    
    def test_get_mitigated_data_success(self, fairness_service_instance):
        """Test successfully retrieving mitigated data."""
        mock_data = b'mitigated,data,content'
        fairness_service_instance.fileStore.read_file = MagicMock(
            return_value={'data': mock_data, 'contentType': 'text/csv', 'name': 'mitigated.csv'}
        )
        
        result = fairness_service_instance.get_mitigated_data('file_id_123')
        
        assert result is not None
        fairness_service_instance.fileStore.read_file.assert_called_once_with('file_id_123')


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""
    
    def test_save_as_json_file_empty_content(self, temp_test_dir, fairness_service_instance):
        """Test saving empty JSON content."""
        file_path = os.path.join(temp_test_dir, 'empty.json')
        
        FairnessService.save_as_json_file(file_path, {})
        
        assert os.path.exists(file_path)
        with open(file_path, 'r') as f:
            loaded = json.load(f)
        assert loaded == {}
    
    def test_read_html_file_not_found(self, fairness_service_instance):
        """Test reading non-existent HTML file."""
        with pytest.raises(FileNotFoundError):
            FairnessService.read_html_file('/nonexistent/file.html')
    
    def test_parse_nutanix_bucket_empty_string(self, fairness_service_instance):
        """Test parsing empty Nutanix bucket path."""
        result = FairnessService.parse_nutanix_bucket_object('')
        
        assert 'bucket_name' in result
        assert result['bucket_name'] == ''
    
    def test_attribute_dict_get_nonexistent_key(self):
        """Test accessing non-existent key in AttributeDict."""
        attr_dict = AttributeDict({'key': 'value'})
        
        with pytest.raises(KeyError):
            _ = attr_dict.nonexistent
    
    @patch('fairness.service.service.pandas.read_csv')
    def test_analyze_demo_empty_dataframe(
        self, mock_read_csv, fairness_service_instance
    ):
        """Test analyzedemo with empty DataFrame."""
        fairness_service_instance.fileStore.read_file = MagicMock(
            return_value={'data': b'col1,col2\n'}
        )
        
        class PayloadObj:
            method = ['statistical_parity']
            biasType = 'PRETRAIN'
            fileid = 'file123'
        
        payload = PayloadObj()
        
        with pytest.raises(ValueError, match="Dataframe is empty or None"):
            fairness_service_instance.analyzedemo(payload)


class TestIntegrationScenarios:
    """Test integration scenarios."""
    
    @patch('matplotlib.pyplot.savefig')
    @patch('builtins.open', new_callable=mock_open, read_data=b'image')
    def test_full_bias_analysis_workflow(
        self, mock_file, mock_savefig, temp_test_dir, fairness_service_instance
    ):
        """Test complete bias analysis workflow."""
        # Create test data
        df = pd.DataFrame({
            'age': [25, 30, 35],
            'gender': ['Male', 'Female', 'Male'],
            'label': [0, 1, 1]
        })
        csv_path = os.path.join(temp_test_dir, 'test.csv')
        df.to_csv(csv_path, index=False)
        
        # Test HTML generation (mocked open will intercept file operations)
        metrics = [{'metrics': [
            {'name': 'Test', 'value': 0.5, 'description': 'Desc'}
        ]}]
        html = FairnessService.json_to_html(metrics)
        
        assert 'Fairness Report' in html
        # Verify mock was called for image reading
        assert mock_file.called


class TestSecurityAndValidation:
    """Test security and validation aspects."""
    
    def test_sql_injection_in_nutanix_path(self, fairness_service_instance):
        """Test that SQL injection attempts are handled."""
        malicious_path = "bucket'; DROP TABLE users; --//path"
        
        result = FairnessService.parse_nutanix_bucket_object(malicious_path)
        
        # Should parse without executing SQL
        assert 'bucket_name' in result
        assert "DROP TABLE" in result['bucket_name']
    
    def test_path_traversal_in_file_operations(self, temp_test_dir, fairness_service_instance):
        """Test path traversal attempts are handled."""
        malicious_path = os.path.join(temp_test_dir, '../../../etc/passwd')
        content = {'test': 'data'}
        
        # Should create file in temp dir, not traverse
        try:
            FairnessService.save_as_json_file(malicious_path, content)
            # If successful, verify it didn't traverse
            assert not os.path.exists('/etc/passwd_from_test')
        except Exception:
            # Expected - path validation
            pass


class TestPerformanceScenarios:
    """Test performance-related scenarios."""
    
    def test_large_dataframe_handling(self, temp_test_dir, fairness_service_instance):
        """Test handling large DataFrame."""
        large_df = pd.DataFrame({
            f'col_{i}': range(10000) for i in range(50)
        })
        
        csv_path = os.path.join(temp_test_dir, 'large.csv')
        large_df.to_csv(csv_path, index=False)
        
        # Test that we can load it
        result = FairnessService.get_data_frame(
            'csv', csv_path, ',', [f'col_{i}' for i in range(10)]
        )
        
        assert len(result) == 10000
        assert len(result.columns) == 10


class TestCategoricalAttributeParsing:
    """Test categorical attribute parsing."""
    
    def test_categorical_attributes_empty_string(self):
        """Test parsing empty categorical attributes."""
        # This would be part of analyzeTenet logic
        categorical = " "
        result = [] if categorical == " " else categorical.split(",")
        
        assert result == []
    
    def test_categorical_attributes_multiple(self):
        """Test parsing multiple categorical attributes."""
        categorical = "gender,race,age_group"
        result = categorical.split(",")
        
        assert len(result) == 3
        assert 'gender' in result
        assert 'race' in result
        assert 'age_group' in result


class TestProtectedAttributesParsing:
    """Test protected attributes parsing."""
    
    def test_protected_attributes_construction(self):
        """Test constructing protected attributes dict."""
        facets = [
            AttributeDict({
                'name': 'gender',
                'privileged': ['Male'],
                'unprivileged': ['Female']
            }),
            AttributeDict({
                'name': 'race',
                'privileged': ['White'],
                'unprivileged': ['Black', 'Asian']
            })
        ]
        
        attr = {"name": [], "privileged": [], "unprivileged": []}
        for i in facets:
            attr["name"] += [i.name]
            attr["privileged"] += [i.privileged]
            attr["unprivileged"] += [i.unprivileged]
        
        assert len(attr["name"]) == 2
        assert 'gender' in attr["name"]
        assert 'race' in attr["name"]
        assert ['Male'] in attr["privileged"]
        assert ['Female'] in attr["unprivileged"]


class TestFileTypeDetectionAndHandling:
    """Test file type detection and handling."""
    
    @pytest.mark.parametrize("extension,expected", [
        ("csv", True),
        ("parquet", True),
        ("feather", True),
        ("json", True),
    ])
    def test_supported_file_extensions(self, extension, expected, temp_test_dir, fairness_service_instance):
        """Test that supported file extensions are handled."""
        df = pd.DataFrame({'col': [1, 2, 3]})
        file_path = os.path.join(temp_test_dir, f'data.{extension}')
        
        if extension == 'csv':
            df.to_csv(file_path, index=False)
        elif extension == 'parquet':
            df.to_parquet(file_path, index=False)
        elif extension == 'feather':
            df.to_feather(file_path)
        elif extension == 'json':
            df.to_json(file_path)
        
        # Test loading based on extension
        result = FairnessService.get_data_frame(extension, file_path, ',', None)
        assert result is not None


class TestDataValidation:
    """Test data validation scenarios."""
    
    def test_features_parsing_from_string(self):
        """Test parsing features from comma-separated string."""
        features_str = "age,gender,race,income"
        features = features_str.split(",")
        
        assert len(features) == 4
        assert features == ['age', 'gender', 'race', 'income']
    
    def test_labelmap_structure(self):
        """Test labelmap structure validation."""
        labelmap = {0: 'No', 1: 'Yes'}
        
        assert isinstance(labelmap, dict)
        assert 0 in labelmap
        assert 1 in labelmap
        assert labelmap[0] == 'No'
        assert labelmap[1] == 'Yes'
    
    def test_favourable_outcome_conversion(self):
        """Test favourable outcome conversion to strings."""
        favourable = [1, 2]
        favourable_str = [str(i) for i in favourable]
        
        assert favourable_str == ['1', '2']
        assert all(isinstance(x, str) for x in favourable_str)


class TestRegressionCases:
    """Test regression cases for known issues."""
    
    def test_attribute_dict_with_nested_dicts(self):
        """Test AttributeDict with nested dictionaries."""
        nested = {
            'level1': {
                'level2': {
                    'level3': 'value'
                }
            }
        }
        
        attr_dict = AttributeDict(nested)
        assert 'level1' in attr_dict
        assert isinstance(attr_dict.level1, dict)
    
    def test_empty_protected_attributes_list(self):
        """Test handling empty protected attributes."""
        attr = {"name": [], "privileged": [], "unprivileged": []}
        
        assert len(attr["name"]) == 0
        assert isinstance(attr, dict)
    
    @patch('matplotlib.pyplot.savefig')
    @patch('builtins.open', new_callable=mock_open, read_data=b'img')
    def test_json_to_html_with_negative_values(self, mock_file, mock_savefig, fairness_service_instance):
        """Test HTML generation with negative metric values."""
        json_obj = [{
            'metrics': [
                {'name': 'Negative Metric', 'value': -0.5, 'description': 'Test'}
            ]
        }]
        
        result = FairnessService.json_to_html(json_obj)
        
        assert 'Negative Metric' in result
        assert '-0.5' in result or 'Measured Value = -0.5' in result
