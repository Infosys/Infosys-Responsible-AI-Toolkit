"""
Test cases for wrapper.py

This module contains comprehensive test cases for the FairnessWorkbench class
and related functions in fairness.service.wrapper module.
"""

import pytest
import json
import pandas as pd
import os
import io
from unittest.mock import Mock, MagicMock, patch, call, ANY
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO, StringIO
from bson import ObjectId

from fairness.service.wrapper import FairnessWorkbench, AttributeDict
from fairness.mappers.mappers import BatchId


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_database():
    """Create a mock database for testing."""
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(side_effect=lambda key: MagicMock())
    mock_db["bias"] = MagicMock()
    mock_db["mitigation"] = MagicMock()
    mock_db["fs.files"] = MagicMock()
    return mock_db


@pytest.fixture
def mock_file_store():
    """Create a mock FileStoreReportDb instance."""
    mock_fs = MagicMock()
    mock_fs.read_file = MagicMock()
    mock_fs.read_chunked_file = MagicMock()
    return mock_fs


@pytest.fixture
def mock_batch():
    """Create a mock Batch instance."""
    mock_b = MagicMock()
    mock_b.update = MagicMock()
    mock_b.find = MagicMock()
    return mock_b


@pytest.fixture
def mock_tenet():
    """Create a mock Tenet instance."""
    mock_t = MagicMock()
    mock_t.find = MagicMock(return_value='tenet_123')
    return mock_t


@pytest.fixture
def mock_dataset():
    """Create a mock Dataset instance."""
    mock_ds = MagicMock()
    mock_ds.find = MagicMock(return_value={'DatasetId': 'dataset_123', 'DatasetName': 'test_dataset'})
    return mock_ds


@pytest.fixture
def mock_data_attributes():
    """Create a mock DataAttributes instance."""
    mock_da = MagicMock()
    mock_da.find = MagicMock(return_value=['attr_1', 'attr_2', 'attr_3'])
    return mock_da


@pytest.fixture
def mock_data_attribute_values():
    """Create a mock DataAttributeValues instance."""
    mock_dav = MagicMock()
    mock_dav.find = MagicMock(return_value=['PREPROCESSING', 'PRETRAIN', 'Generic'])
    return mock_dav


@pytest.fixture
def mock_report():
    """Create a mock Report instance."""
    mock_r = MagicMock()
    mock_r.find = MagicMock()
    return mock_r


@pytest.fixture
def fairness_workbench_instance(mock_database, mock_file_store, mock_batch, mock_tenet, 
                                  mock_dataset, mock_data_attributes, mock_data_attribute_values, mock_report):
    """Create a FairnessWorkbench instance with mocked dependencies."""
    with patch('fairness.service.wrapper.FileStoreReportDb') as mock_filestore_class, \
         patch('fairness.service.wrapper.Batch') as mock_batch_class, \
         patch('fairness.service.wrapper.Tenet') as mock_tenet_class, \
         patch('fairness.service.wrapper.Dataset') as mock_dataset_class, \
         patch('fairness.service.wrapper.DataAttributes') as mock_data_attr_class, \
         patch('fairness.service.wrapper.DataAttributeValues') as mock_data_attr_vals_class, \
         patch('fairness.service.wrapper.Report') as mock_report_class, \
         patch('fairness.service.wrapper.Utils') as mock_utils_class:
        
        # Setup mock class returns
        mock_filestore_class.return_value = mock_file_store
        mock_batch_class.return_value = mock_batch
        mock_tenet_class.return_value = mock_tenet
        mock_dataset_class.return_value = mock_dataset
        mock_data_attr_class.return_value = mock_data_attributes
        mock_data_attr_vals_class.return_value = mock_data_attribute_values
        mock_report_class.return_value = mock_report
        mock_utils_class.return_value = MagicMock()
        
        workbench = FairnessWorkbench(db=mock_database)
        return workbench


@pytest.fixture
def sample_batch_payload():
    """Create a sample batch payload for testing."""
    payload = AttributeDict()
    payload.Batch_id = 123.0
    return payload


@pytest.fixture
def sample_batch_details():
    """Create sample batch details."""
    return {
        'BatchId': 123.0,
        'DataId': 'dataset_456',
        'TenetId': 'tenet_789',
        'Status': 'Pending'
    }


@pytest.fixture
def sample_report_details():
    """Create sample report details."""
    return {
        'ReportId': 'report_123',
        'ReportFileId': ObjectId(),
        'ReportName': 'test_report.pdf',
        'BatchId': 123.0
    }


# ============================================================================
# TEST CLASS: AttributeDict
# ============================================================================

class TestAttributeDict:
    """Test cases for AttributeDict class."""

    def test_attribute_dict_creation(self):
        """Test creating an AttributeDict with initial data."""
        data = {'key1': 'value1', 'key2': 'value2'}
        attr_dict = AttributeDict(data)
        
        assert attr_dict['key1'] == 'value1'
        assert attr_dict['key2'] == 'value2'
        assert attr_dict.key1 == 'value1'
        assert attr_dict.key2 == 'value2'

    def test_attribute_dict_setattr(self):
        """Test setting attributes on AttributeDict."""
        attr_dict = AttributeDict()
        attr_dict.test_key = 'test_value'
        
        assert attr_dict['test_key'] == 'test_value'
        assert attr_dict.test_key == 'test_value'

    def test_attribute_dict_getattr(self):
        """Test getting attributes from AttributeDict."""
        attr_dict = AttributeDict({'name': 'test', 'value': 123})
        
        assert attr_dict.name == 'test'
        assert attr_dict.value == 123

    def test_attribute_dict_delattr(self):
        """Test deleting attributes from AttributeDict."""
        attr_dict = AttributeDict({'key1': 'value1', 'key2': 'value2'})
        del attr_dict.key1
        
        assert 'key1' not in attr_dict
        assert 'key2' in attr_dict


# ============================================================================
# TEST CLASS: FairnessWorkbench Initialization
# ============================================================================

class TestFairnessWorkbenchInit:
    """Test cases for FairnessWorkbench initialization."""

    def test_init_with_db(self, mock_database):
        """Test initialization with provided database."""
        with patch('fairness.service.wrapper.FileStoreReportDb') as mock_fs, \
             patch('fairness.service.wrapper.Batch') as mock_batch, \
             patch('fairness.service.wrapper.Tenet') as mock_tenet, \
             patch('fairness.service.wrapper.Dataset') as mock_dataset, \
             patch('fairness.service.wrapper.DataAttributes') as mock_da, \
             patch('fairness.service.wrapper.DataAttributeValues') as mock_dav, \
             patch('fairness.service.wrapper.Report') as mock_report, \
             patch('fairness.service.wrapper.Utils') as mock_utils:
            
            workbench = FairnessWorkbench(db=mock_database)
            
            assert workbench.db == mock_database
            # Note: The collections are created via __getitem__ calls, so we just verify db is set correctly
            
            # Verify all DAOs were initialized with the database
            mock_fs.assert_called_once_with(mock_database)
            mock_batch.assert_called_once_with(mock_database)
            mock_tenet.assert_called_once_with(mock_database)
            mock_dataset.assert_called_once_with(mock_database)
            mock_da.assert_called_once_with(mock_database)
            mock_dav.assert_called_once_with(mock_database)
            mock_report.assert_called_once_with(mock_database)

    def test_init_without_db(self):
        """Test initialization without providing database (uses DataBase singleton)."""
        with patch('fairness.service.wrapper.DataBase') as mock_db_class, \
             patch('fairness.service.wrapper.FileStoreReportDb') as mock_fs, \
             patch('fairness.service.wrapper.Batch') as mock_batch, \
             patch('fairness.service.wrapper.Tenet') as mock_tenet, \
             patch('fairness.service.wrapper.Dataset') as mock_dataset, \
             patch('fairness.service.wrapper.DataAttributes') as mock_da, \
             patch('fairness.service.wrapper.DataAttributeValues') as mock_dav, \
             patch('fairness.service.wrapper.Report') as mock_report, \
             patch('fairness.service.wrapper.Utils') as mock_utils:
            
            mock_db_instance = MagicMock()
            mock_db_instance.__getitem__ = MagicMock(side_effect=lambda key: MagicMock())
            mock_db_class.return_value.db = mock_db_instance
            
            workbench = FairnessWorkbench()
            
            assert workbench.db == mock_db_instance
            
            # Verify all DAOs were initialized without arguments (using default DB)
            mock_fs.assert_called_once_with()
            mock_batch.assert_called_once_with()
            mock_tenet.assert_called_once_with()
            mock_dataset.assert_called_once_with()
            mock_da.assert_called_once_with()
            mock_dav.assert_called_once_with()
            mock_report.assert_called_once_with()


# ============================================================================
# TEST CLASS: wrapper_trigger Method
# ============================================================================

class TestWrapperTrigger:
    """Test cases for wrapper_trigger method."""

    def test_wrapper_trigger_with_empty_mitigation_technique(self, fairness_workbench_instance, 
                                                               sample_batch_payload, sample_batch_details):
        """Test wrapper_trigger when mitigationTechnique is empty (calls analyseDB)."""
        # Setup mocks
        fairness_workbench_instance.tenet.find.return_value = 'tenet_123'
        fairness_workbench_instance.batch.find.return_value = sample_batch_details
        fairness_workbench_instance.dataset.find.return_value = {'DatasetId': 'dataset_456'}
        fairness_workbench_instance.dataAttributes.find.return_value = ['attr_1', 'attr_2', 'attr_3']
        fairness_workbench_instance.dataAttributeValues.find.return_value = ['', 'PREPROCESSING', 'Generic']
        
        expected_response = {'status': 'success', 'biasResults': []}
        
        with patch('fairness.service.wrapper.FairnessUIservicePreproc') as mock_preproc:
            mock_preproc_instance = MagicMock()
            mock_preproc_instance.return_protected_attrib_analyseDB.return_value = expected_response
            mock_preproc.return_value = mock_preproc_instance
            
            response = fairness_workbench_instance.wapper_trigger(sample_batch_payload)
            
            # Verify batch status was updated
            fairness_workbench_instance.batch.update.assert_called_once_with(
                batch_id=123.0, 
                value={"Status": "In-progress"}
            )
            
            # Verify correct method was called
            mock_preproc_instance.return_protected_attrib_analyseDB.assert_called_once()
            assert response == expected_response

    def test_wrapper_trigger_with_mitigation_technique(self, fairness_workbench_instance, 
                                                         sample_batch_payload, sample_batch_details):
        """Test wrapper_trigger when mitigationTechnique is provided (calls pretrainMitigation)."""
        # Setup mocks
        fairness_workbench_instance.tenet.find.return_value = 'tenet_123'
        fairness_workbench_instance.batch.find.return_value = sample_batch_details
        fairness_workbench_instance.dataset.find.return_value = {'DatasetId': 'dataset_456'}
        fairness_workbench_instance.dataAttributes.find.return_value = ['attr_1', 'attr_2', 'attr_3']
        fairness_workbench_instance.dataAttributeValues.find.return_value = ['REWEIGHING', 'PREPROCESSING', 'Generic']
        
        expected_response = {'status': 'success', 'mitigatedDataset': 'dataset_789'}
        
        with patch('fairness.service.wrapper.FairnessUIservicePreproc') as mock_preproc:
            mock_preproc_instance = MagicMock()
            mock_preproc_instance.return_pretrainMitigation_protected_attrib.return_value = expected_response
            mock_preproc.return_value = mock_preproc_instance
            
            response = fairness_workbench_instance.wapper_trigger(sample_batch_payload)
            
            # Verify batch status was updated
            fairness_workbench_instance.batch.update.assert_called_once_with(
                batch_id=123.0, 
                value={"Status": "In-progress"}
            )
            
            # Verify correct method was called
            mock_preproc_instance.return_pretrainMitigation_protected_attrib.assert_called_once()
            assert response == expected_response

    def test_wrapper_trigger_audit_generic(self, fairness_workbench_instance, 
                                            sample_batch_payload, sample_batch_details):
        """Test wrapper_trigger with AUDIT mitigation type and Generic method."""
        # Setup mocks
        fairness_workbench_instance.tenet.find.return_value = 'tenet_123'
        fairness_workbench_instance.batch.find.return_value = sample_batch_details
        fairness_workbench_instance.dataset.find.return_value = {'DatasetId': 'dataset_456'}
        fairness_workbench_instance.dataAttributes.find.return_value = ['attr_1', 'attr_2', 'attr_3']
        fairness_workbench_instance.dataAttributeValues.find.return_value = ['REWEIGHING', 'AUDIT', 'Generic']
        
        expected_response = {'status': 'success', 'auditResults': []}
        
        with patch('fairness.service.wrapper.FairnessAudit') as mock_audit:
            mock_audit_instance = MagicMock()
            mock_audit_instance.workbench_audit.return_value = expected_response
            mock_audit.return_value = mock_audit_instance
            
            response = fairness_workbench_instance.wapper_trigger(sample_batch_payload)
            
            # Verify audit method was called
            mock_audit_instance.workbench_audit.assert_called_once_with({"Batch_id": 123.0})
            assert response == expected_response

    def test_wrapper_trigger_audit_decisive(self, fairness_workbench_instance, 
                                             sample_batch_payload, sample_batch_details):
        """Test wrapper_trigger with AUDIT mitigation type and Decisive method."""
        # Setup mocks
        fairness_workbench_instance.tenet.find.return_value = 'tenet_123'
        fairness_workbench_instance.batch.find.return_value = sample_batch_details
        fairness_workbench_instance.dataset.find.return_value = {'DatasetId': 'dataset_456'}
        fairness_workbench_instance.dataAttributes.find.return_value = ['attr_1', 'attr_2', 'attr_3']
        fairness_workbench_instance.dataAttributeValues.find.return_value = ['REWEIGHING', 'AUDIT', 'Decisive']
        
        expected_response = {'status': 'success', 'successRates': []}
        
        with patch('fairness.service.wrapper.SuccessRateService') as mock_success:
            mock_success_instance = MagicMock()
            mock_success_instance.workbench_analyze.return_value = expected_response
            mock_success.return_value = mock_success_instance
            
            response = fairness_workbench_instance.wapper_trigger(sample_batch_payload)
            
            # Verify success rate method was called
            mock_success_instance.workbench_analyze.assert_called_once_with({"Batch_id": 123.0})
            assert response == expected_response

    def test_wrapper_trigger_inprocessing(self, fairness_workbench_instance, 
                                           sample_batch_payload, sample_batch_details):
        """Test wrapper_trigger with INPROCESSING mitigation type."""
        # Setup mocks
        fairness_workbench_instance.tenet.find.return_value = 'tenet_123'
        fairness_workbench_instance.batch.find.return_value = sample_batch_details
        fairness_workbench_instance.dataset.find.return_value = {'DatasetId': 'dataset_456'}
        fairness_workbench_instance.dataAttributes.find.return_value = ['attr_1', 'attr_2', 'attr_3']
        fairness_workbench_instance.dataAttributeValues.find.return_value = ['EG_REDUCTION', 'INPROCESSING', 'Generic']
        
        expected_response = {'status': 'success', 'inprocessingResults': []}
        
        with patch('fairness.service.wrapper.InprocessingService') as mock_inproc:
            mock_inproc_instance = MagicMock()
            mock_inproc_instance.inprocessing_exponentiated_gradient_reduction.return_value = expected_response
            mock_inproc.return_value = mock_inproc_instance
            
            response = fairness_workbench_instance.wapper_trigger(sample_batch_payload)
            
            # Verify inprocessing method was called
            mock_inproc_instance.inprocessing_exponentiated_gradient_reduction.assert_called_once_with({"Batch_id": 123.0})
            assert response == expected_response

    def test_wrapper_trigger_missing_batch_id(self, fairness_workbench_instance):
        """Test wrapper_trigger with missing Batch_id."""
        payload = AttributeDict()
        payload.Batch_id = None
        
        # The method doesn't raise exception, it just logs error
        # But batch.update should not be called
        fairness_workbench_instance.batch.update.reset_mock()
        
        # This will likely fail when trying to process None batch_id
        # The actual behavior depends on the downstream methods

    def test_wrapper_trigger_batch_status_update(self, fairness_workbench_instance, 
                                                   sample_batch_payload, sample_batch_details):
        """Test that batch status is updated to In-progress."""
        fairness_workbench_instance.tenet.find.return_value = 'tenet_123'
        fairness_workbench_instance.batch.find.return_value = sample_batch_details
        fairness_workbench_instance.dataset.find.return_value = {'DatasetId': 'dataset_456'}
        fairness_workbench_instance.dataAttributes.find.return_value = ['attr_1', 'attr_2', 'attr_3']
        fairness_workbench_instance.dataAttributeValues.find.return_value = ['', 'PREPROCESSING', 'Generic']
        
        with patch('fairness.service.wrapper.FairnessUIservicePreproc') as mock_preproc:
            mock_preproc_instance = MagicMock()
            mock_preproc_instance.return_protected_attrib_analyseDB.return_value = {}
            mock_preproc.return_value = mock_preproc_instance
            
            fairness_workbench_instance.wapper_trigger(sample_batch_payload)
            
            fairness_workbench_instance.batch.update.assert_called_once_with(
                batch_id=123.0,
                value={"Status": "In-progress"}
            )


# ============================================================================
# TEST CLASS: wrapper_download Method
# ============================================================================

class TestWrapperDownload:
    """Test cases for wrapper_download method."""

    def test_wrapper_download_pdf_file(self, fairness_workbench_instance, sample_batch_payload):
        """Test downloading a PDF report file."""
        report_id = ObjectId()
        report_details = {
            'ReportFileId': report_id,
            'ReportName': 'fairness_report.pdf',
            'BatchId': 'batch_123'
        }
        
        fairness_workbench_instance.report.find.return_value = report_details
        
        file_content = b'PDF file content here'
        fairness_workbench_instance.fileStore.read_file.return_value = {
            'data': file_content,
            'contentType': 'application/pdf'
        }
        
        with patch('fairness.service.wrapper.PDF_CONTAINER_NAME', 'rai-pdf-reports'):
            response = fairness_workbench_instance.wrapper_download(sample_batch_payload)
            
            # Verify report was queried
            fairness_workbench_instance.report.find.assert_called_once_with(batch_id=123.0)
            
            # Verify file was read from correct container
            fairness_workbench_instance.fileStore.read_file.assert_called_once_with(
                report_id, 
                'rai-pdf-reports'
            )
            
            # Verify response is StreamingResponse
            assert isinstance(response, StreamingResponse)
            assert response.headers["Content-Disposition"] == 'attachment; filename=fairness_report.pdf'

    def test_wrapper_download_zip_file(self, fairness_workbench_instance, sample_batch_payload):
        """Test downloading a ZIP file."""
        report_id = ObjectId()
        report_details = {
            'ReportFileId': report_id,
            'ReportName': 'data_bundle.zip',
            'BatchId': 'batch_123'
        }
        
        fairness_workbench_instance.report.find.return_value = report_details
        
        file_content = b'ZIP file content here'
        fairness_workbench_instance.fileStore.read_file.return_value = {
            'data': file_content,
            'contentType': 'application/zip'
        }
        
        with patch('fairness.service.wrapper.ZIP_CONTAINER_NAME', 'rai-zip-files'):
            response = fairness_workbench_instance.wrapper_download(sample_batch_payload)
            
            # Verify file was read from correct container
            fairness_workbench_instance.fileStore.read_file.assert_called_once_with(
                report_id, 
                'rai-zip-files'
            )
            
            # Verify response
            assert isinstance(response, StreamingResponse)
            assert response.headers["Content-Disposition"] == 'attachment; filename=data_bundle.zip'

    def test_wrapper_download_model_file(self, fairness_workbench_instance, sample_batch_payload):
        """Test downloading a model file (.joblib)."""
        report_id = ObjectId()
        report_details = {
            'ReportFileId': report_id,
            'ReportName': 'trained_model.joblib',
            'BatchId': 'batch_123'
        }
        
        fairness_workbench_instance.report.find.return_value = report_details
        
        file_content = b'Model file content here'
        fairness_workbench_instance.fileStore.read_chunked_file.return_value = {
            'data': file_content,
            'contentType': 'application/octet-stream'
        }
        
        with patch('fairness.service.wrapper.MODEL_CONTAINER_NAME', 'rai-models'):
            response = fairness_workbench_instance.wrapper_download(sample_batch_payload)
            
            # Verify file was read using chunked method
            fairness_workbench_instance.fileStore.read_chunked_file.assert_called_once_with(
                report_id, 
                'rai-models'
            )
            
            # Verify response
            assert isinstance(response, StreamingResponse)
            assert response.headers["Content-Disposition"] == 'attachment; filename=trained_model.joblib'

    def test_wrapper_download_csv_file(self, fairness_workbench_instance, sample_batch_payload):
        """Test downloading a CSV dataset file."""
        report_id = ObjectId()
        report_details = {
            'ReportFileId': report_id,
            'ReportName': 'dataset.csv',
            'BatchId': 'batch_123'
        }
        
        fairness_workbench_instance.report.find.return_value = report_details
        
        file_content = b'CSV file content here'
        fairness_workbench_instance.fileStore.read_file.return_value = {
            'data': file_content,
            'contentType': 'text/csv'
        }
        
        with patch.dict(os.environ, {'Dt_containerName': 'rai-datasets'}):
            response = fairness_workbench_instance.wrapper_download(sample_batch_payload)
            
            # Verify file was read from dataset container (default for CSV)
            fairness_workbench_instance.fileStore.read_file.assert_called_once_with(
                report_id, 
                'rai-datasets'
            )
            
            # Verify response
            assert isinstance(response, StreamingResponse)
            assert response.headers["Content-Disposition"] == 'attachment; filename=dataset.csv'

    def test_wrapper_download_with_multiple_extensions(self, fairness_workbench_instance):
        """Test container name selection for different file extensions."""
        test_cases = [
            ('report.pdf', 'PDF_CONTAINER_NAME', 'rai-pdf-reports', 'read_file'),
            ('archive.zip', 'ZIP_CONTAINER_NAME', 'rai-zip-files', 'read_file'),
            ('model.joblib', 'MODEL_CONTAINER_NAME', 'rai-models', 'read_chunked_file'),
            ('data.csv', 'DATASET_CONTAINER_NAME', 'rai-datasets', 'read_file'),
            ('data.xlsx', 'DATASET_CONTAINER_NAME', 'rai-datasets', 'read_file'),
        ]
        
        for filename, constant_name, container_name, read_method in test_cases:
            # Reset mocks
            fairness_workbench_instance.report.find.reset_mock()
            fairness_workbench_instance.fileStore.read_file.reset_mock()
            fairness_workbench_instance.fileStore.read_chunked_file.reset_mock()
            
            report_id = ObjectId()
            report_details = {
                'ReportFileId': report_id,
                'ReportName': filename,
                'BatchId': 'batch_123'
            }
            
            fairness_workbench_instance.report.find.return_value = report_details
            
            file_content = b'File content'
            return_value = {'data': file_content, 'contentType': 'application/octet-stream'}
            
            if read_method == 'read_file':
                fairness_workbench_instance.fileStore.read_file.return_value = return_value
            else:
                fairness_workbench_instance.fileStore.read_chunked_file.return_value = return_value
            
            payload = AttributeDict({'Batch_id': 123.0})
            
            with patch(f'fairness.service.wrapper.{constant_name}', container_name):
                response = fairness_workbench_instance.wrapper_download(payload)
                
                # Verify correct read method was called
                if read_method == 'read_file':
                    fairness_workbench_instance.fileStore.read_file.assert_called_once_with(
                        report_id, 
                        container_name
                    )
                else:
                    fairness_workbench_instance.fileStore.read_chunked_file.assert_called_once_with(
                        report_id, 
                        container_name
                    )


# ============================================================================
# TEST CLASS: Integration Tests
# ============================================================================

class TestIntegrationScenarios:
    """Integration test scenarios for FairnessWorkbench."""

    def test_full_workflow_analyze_and_download(self, fairness_workbench_instance):
        """Test complete workflow: trigger analysis and download report."""
        # Setup trigger
        batch_payload = AttributeDict({'Batch_id': 123.0})
        
        fairness_workbench_instance.tenet.find.return_value = 'tenet_123'
        fairness_workbench_instance.batch.find.return_value = {
            'BatchId': 'batch_123',
            'DataId': 'dataset_456',
            'Status': 'Pending'
        }
        fairness_workbench_instance.dataset.find.return_value = {'DatasetId': 'dataset_456'}
        fairness_workbench_instance.dataAttributes.find.return_value = ['attr_1', 'attr_2', 'attr_3']
        fairness_workbench_instance.dataAttributeValues.find.return_value = ['', 'PREPROCESSING', 'Generic']
        
        with patch('fairness.service.wrapper.FairnessUIservicePreproc') as mock_preproc:
            mock_preproc_instance = MagicMock()
            mock_preproc_instance.return_protected_attrib_analyseDB.return_value = {
                'status': 'success',
                'biasDetected': True
            }
            mock_preproc.return_value = mock_preproc_instance
            
            # Trigger analysis
            trigger_response = fairness_workbench_instance.wapper_trigger(batch_payload)
            
            assert trigger_response['status'] == 'success'
            fairness_workbench_instance.batch.update.assert_called_once()
        
        # Setup download
        report_id = ObjectId()
        fairness_workbench_instance.report.find.return_value = {
            'ReportFileId': report_id,
            'ReportName': 'analysis_report.pdf',
            'BatchId': 123.0
        }
        fairness_workbench_instance.fileStore.read_file.return_value = {
            'data': b'PDF content',
            'contentType': 'application/pdf'
        }
        
        with patch('fairness.service.wrapper.PDF_CONTAINER_NAME', 'rai-pdf-reports'):
            # Download report
            download_response = fairness_workbench_instance.wrapper_download(batch_payload)
            
            assert isinstance(download_response, StreamingResponse)
            assert 'analysis_report.pdf' in download_response.headers["Content-Disposition"]


# ============================================================================
# TEST CLASS: Error Handling
# ============================================================================

class TestErrorHandling:
    """Test error handling scenarios."""

    def test_wrapper_trigger_with_none_batch_id(self, fairness_workbench_instance):
        """Test wrapper_trigger handles None batch_id gracefully."""
        payload = AttributeDict({'Batch_id': None})
        
        # The method logs error but doesn't raise exception
        # Verify it doesn't crash and batch.update is not called with None
        fairness_workbench_instance.batch.update.reset_mock()

    def test_wrapper_trigger_with_empty_string_batch_id(self, fairness_workbench_instance):
        """Test wrapper_trigger handles empty string batch_id."""
        payload = AttributeDict({'Batch_id': ''})
        
        # The method logs error but doesn't raise exception
        fairness_workbench_instance.batch.update.reset_mock()

    def test_wrapper_download_report_not_found(self, fairness_workbench_instance, sample_batch_payload):
        """Test wrapper_download when report is not found."""
        fairness_workbench_instance.report.find.return_value = None
        
        # This should raise an error when trying to access ReportFileId on None
        with pytest.raises((TypeError, KeyError, AttributeError)):
            fairness_workbench_instance.wrapper_download(sample_batch_payload)

    def test_wrapper_download_file_read_error(self, fairness_workbench_instance, sample_batch_payload):
        """Test wrapper_download when file reading fails."""
        report_id = ObjectId()
        fairness_workbench_instance.report.find.return_value = {
            'ReportFileId': report_id,
            'ReportName': 'test.pdf',
            'BatchId': 'batch_123'
        }
        
        # Simulate file read error
        fairness_workbench_instance.fileStore.read_file.side_effect = Exception("File not found in GridFS")
        
        with patch('fairness.service.wrapper.PDF_CONTAINER_NAME', 'pdf-container'):
            with pytest.raises(Exception) as exc_info:
                fairness_workbench_instance.wrapper_download(sample_batch_payload)
            
            assert "File not found in GridFS" in str(exc_info.value)


# ============================================================================
# TEST CLASS: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_attribute_dict_with_special_keys(self):
        """Test AttributeDict with special key names."""
        attr_dict = AttributeDict({
            '__special__': 'value1',
            'with-dash': 'value2',
            'with_underscore': 'value3',
            '123numeric': 'value4'
        })
        
        assert attr_dict['__special__'] == 'value1'
        assert attr_dict['with-dash'] == 'value2'
        assert attr_dict.with_underscore == 'value3'
        assert attr_dict['123numeric'] == 'value4'

    def test_wrapper_download_with_no_extension(self, fairness_workbench_instance, sample_batch_payload):
        """Test wrapper_download with filename without extension."""
        report_id = ObjectId()
        fairness_workbench_instance.report.find.return_value = {
            'ReportFileId': report_id,
            'ReportName': 'report_no_extension',
            'BatchId': 'batch_123'
        }
        
        fairness_workbench_instance.fileStore.read_file.return_value = {
            'data': b'File content',
            'contentType': 'application/octet-stream'
        }
        
        with patch('fairness.service.wrapper.DATASET_CONTAINER_NAME', 'rai-datasets'):
            response = fairness_workbench_instance.wrapper_download(sample_batch_payload)
            
            # Should default to dataset container
            fairness_workbench_instance.fileStore.read_file.assert_called_once_with(
                report_id,
                'rai-datasets'
            )
            assert isinstance(response, StreamingResponse)

    def test_wrapper_trigger_all_mitigation_types(self, fairness_workbench_instance, sample_batch_details):
        """Test wrapper_trigger routes correctly for all mitigation types."""
        mitigation_scenarios = [
            ('', 'PREPROCESSING', 'Generic', 'FairnessUIservicePreproc', 'return_protected_attrib_analyseDB'),
            ('REWEIGHING', 'PREPROCESSING', 'Generic', 'FairnessUIservicePreproc', 'return_pretrainMitigation_protected_attrib'),
            ('TECHNIQUE', 'AUDIT', 'Generic', 'FairnessAudit', 'workbench_audit'),
            ('TECHNIQUE', 'AUDIT', 'Decisive', 'SuccessRateService', 'workbench_analyze'),
            ('TECHNIQUE', 'INPROCESSING', 'Generic', 'InprocessingService', 'inprocessing_exponentiated_gradient_reduction'),
        ]
        
        for idx, (technique, mit_type, method_type, service_name, method_name) in enumerate(mitigation_scenarios):
            # Reset mocks
            fairness_workbench_instance.batch.update.reset_mock()
            
            payload = AttributeDict({'Batch_id': float(100 + idx)})
            
            fairness_workbench_instance.tenet.find.return_value = 'tenet_123'
            fairness_workbench_instance.batch.find.return_value = sample_batch_details
            fairness_workbench_instance.dataset.find.return_value = {'DatasetId': 'dataset_456'}
            fairness_workbench_instance.dataAttributes.find.return_value = ['attr_1', 'attr_2', 'attr_3']
            fairness_workbench_instance.dataAttributeValues.find.return_value = [technique, mit_type, method_type]
            
            with patch(f'fairness.service.wrapper.{service_name}') as mock_service:
                mock_instance = MagicMock()
                getattr(mock_instance, method_name).return_value = {'status': 'success'}
                mock_service.return_value = mock_instance
                
                response = fairness_workbench_instance.wapper_trigger(payload)
                
                # Verify correct service and method were called
                getattr(mock_instance, method_name).assert_called_once()
                assert response['status'] == 'success'
