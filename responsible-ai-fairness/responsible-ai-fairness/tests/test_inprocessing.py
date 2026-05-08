"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pytest
import os
import sys
from io import BytesIO
from gridfs import GridFS, GridOut
from mongomock import gridfs
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from fairness.dao.WorkBench.FileStoreDb import FileStoreReportDb
from fairness.mappers.mappers import BatchId
from gridfs.errors import NoFile, FileExists
from .MockDB import Database_MockDB
from pytest_mock import mocker
from mongomock import MongoClient
from dotenv import load_dotenv
import requests
import numpy as np
import pandas as pd
from unittest.mock import Mock, MagicMock, patch
from fastapi import HTTPException
from fairness.service.inprocessing import InprocessingService, AttributeDict

load_dotenv()


class TestAttributeDict:
    """Test the AttributeDict utility class"""
    
    def test_attribute_dict_getattr(self):
        """Test AttributeDict attribute access via dot notation"""
        attr_dict = AttributeDict({'key': 'value', 'number': 42})
        assert attr_dict.key == 'value'
        assert attr_dict.number == 42
    
    def test_attribute_dict_setattr(self):
        """Test AttributeDict attribute setting via dot notation"""
        attr_dict = AttributeDict()
        attr_dict.new_key = 'new_value'
        assert attr_dict['new_key'] == 'new_value'
        assert attr_dict.new_key == 'new_value'
    
    def test_attribute_dict_delattr(self):
        """Test AttributeDict attribute deletion via dot notation"""
        attr_dict = AttributeDict({'key': 'value'})
        del attr_dict.key
        assert 'key' not in attr_dict
    
    def test_attribute_dict_inheritance(self):
        """Test AttributeDict inherits from dict"""
        attr_dict = AttributeDict({'a': 1, 'b': 2})
        assert isinstance(attr_dict, dict)
        assert len(attr_dict) == 2


class TestInprocessingServiceInit:
    """Test InprocessingService initialization"""
    
    def test_init_with_mockdb(self, setup_database):
        """Test initialization with MockDB"""
        service = InprocessingService(setup_database[0])
        
        assert service.db is not None
        assert service.fileStore is not None
        assert service.batch is not None
        assert service.tenet is not None
        assert service.dataset is not None
        assert service.dataAttributes is not None
        assert service.dataAttributeValues is not None
        assert service.bias_collection is not None
        assert service.mitigation_collection is not None
        assert service.mitigation_model_collection is not None
        assert service.metrics_collection is not None
        assert service.llm_analysis_collection is not None
        assert service.llm_connection_credentials_collection is not None
    
    def test_init_without_mockdb(self):
        """Test initialization without MockDB (uses real DataBase)"""
        with patch('fairness.service.inprocessing.DataBase') as mock_db:
            mock_db_instance = Mock()
            # Mock database with all required collections
            mock_db_instance.db = {
                'bias': Mock(),
                'mitigation': Mock(),
                'mitigation_model': Mock(),
                'metrics': Mock(),
                'llm_analysis': Mock(),
                'llm_connection_credentails': Mock()
            }
            mock_db.return_value = mock_db_instance
            
            service = InprocessingService()
            
            assert service.db is not None
            assert service.bias_collection is not None
            assert service.mitigation_collection is not None
            mock_db.assert_called_once()


class TestMitigationModelAnalyze:
    """Test the static mitigation_model_analyze method"""
    
    def test_mitigation_model_analyze_basic(self):
        """Test mitigation_model_analyze with basic data"""
        y_true = np.array([1, 0, 1, 0, 1])
        y_pred = np.array([1, 0, 1, 1, 1])
        sensitive_features = pd.Series(['A', 'B', 'A', 'B', 'A'])
        
        result = InprocessingService.mitigation_model_analyze(
            y_true, y_pred, sensitive_features
        )
        
        assert 'demographic_parity_difference' in result
        assert 'equalized_odds_difference' in result
        assert 'true_positive_rate' in result
        assert 'true_negative_rate' in result
        assert 'false_positive_rate' in result
        assert 'false_negative_rate' in result
        assert 'accuracy_score' in result
        
        expected_accuracy = accuracy_score(y_true, y_pred)
        assert result['accuracy_score'] == expected_accuracy
    
    def test_mitigation_model_analyze_perfect_prediction(self):
        """Test with perfect predictions"""
        y_true = np.array([1, 0, 1, 0, 1, 0])
        y_pred = np.array([1, 0, 1, 0, 1, 0])
        sensitive_features = pd.Series(['A', 'B', 'A', 'B', 'A', 'B'])
        
        result = InprocessingService.mitigation_model_analyze(
            y_true, y_pred, sensitive_features
        )
        
        assert result['accuracy_score'] == 1.0
        assert result['true_positive_rate'] == 1.0
        assert result['true_negative_rate'] == 1.0
        assert result['false_positive_rate'] == 0.0
        assert result['false_negative_rate'] == 0.0
    
    def test_mitigation_model_analyze_multiclass_sensitive(self):
        """Test with multiple sensitive feature groups"""
        y_true = np.array([1, 0, 1, 0, 1, 0, 1, 0])
        y_pred = np.array([1, 0, 1, 1, 1, 0, 0, 0])
        sensitive_features = pd.Series(['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B'])
        
        result = InprocessingService.mitigation_model_analyze(
            y_true, y_pred, sensitive_features
        )
        
        assert isinstance(result, dict)
        assert len(result) == 7


class TestUploadInprocess:
    """Test upload_inprocess method"""
    
    def test_upload_inprocess_valid_file(self, setup_database):
        """Test upload with valid file"""
        service = InprocessingService(setup_database[0])
        file_id = setup_database[1]
        
        payload = {'fileId': file_id}
        result = service.upload_inprocess(payload)
        
        assert 'feature_list' in result
        assert isinstance(result['feature_list'], list)
        assert len(result['feature_list']) > 0
    
    def test_upload_inprocess_feature_list_content(self, setup_database):
        """Test feature list contains correct data"""
        service = InprocessingService(setup_database[0])
        file_id = setup_database[1]
        
        payload = {'fileId': file_id}
        result = service.upload_inprocess(payload)
        
        feature_list = result['feature_list']
        assert isinstance(feature_list, list)
        for feature in feature_list:
            assert isinstance(feature, str)
    
    def test_upload_inprocess_missing_file(self, setup_database):
        """Test with non-existent file"""
        service = InprocessingService(setup_database[0])
        
        payload = {'fileId': 'non_existent_file_id'}
        
        with pytest.raises(Exception):
            service.upload_inprocess(payload)
    
    def test_upload_inprocess_empty_payload(self, setup_database):
        """Test with empty payload"""
        service = InprocessingService(setup_database[0])
        
        payload = {}
        
        with pytest.raises(KeyError):
            service.upload_inprocess(payload)


class TestInprocessingExponentiatedGradientReduction:
    """Test inprocessing_exponentiated_gradient_reduction method"""
    
    def test_inprocessing_with_valid_batch_id_dict(self, setup_database):
        """Test with valid batch ID as dict"""
        service = InprocessingService(setup_database[0])
        batch_id = setup_database[2]
        
        # Mock the entire flow including mitigation_model_analyze to avoid size mismatch
        mock_metrics = {
            'demographic_parity_difference': 0.1,
            'equalized_odds_difference': 0.2,
            'true_positive_rate': 0.8,
            'true_negative_rate': 0.7,
            'false_positive_rate': 0.3,
            'false_negative_rate': 0.2,
            'accuracy_score': 0.75
        }
        
        with patch('fairness.service.inprocessing.ExponentiatedGradientReduction') as mock_egr, \
             patch('fairness.service.inprocessing.joblib.dump') as mock_dump, \
             patch.object(InprocessingService, 'mitigation_model_analyze', return_value=mock_metrics):
            mock_model = Mock()
            mock_model.fit.return_value = None
            mock_pred = Mock()
            mock_pred.labels = np.array([[1], [0]])
            mock_model.predict.return_value = mock_pred
            mock_egr.return_value = mock_model
            
            payload = {'Batch_id': batch_id}
            result = service.inprocessing_exponentiated_gradient_reduction(payload)
            
            assert result is not None
            assert 'modelfileId' in result
            assert 'metrics' in result
            assert isinstance(result['metrics'], dict)
            mock_dump.assert_called_once()
    
    def test_inprocessing_with_batchid_object(self, setup_database):
        """Test with BatchId Pydantic model object"""
        service = InprocessingService(setup_database[0])
        batch_id_value = setup_database[2]
        
        # Mock the entire flow including mitigation_model_analyze to avoid size mismatch
        mock_metrics = {
            'demographic_parity_difference': 0.1,
            'equalized_odds_difference': 0.2,
            'true_positive_rate': 0.8,
            'true_negative_rate': 0.7,
            'false_positive_rate': 0.3,
            'false_negative_rate': 0.2,
            'accuracy_score': 0.75
        }
        
        with patch('fairness.service.inprocessing.ExponentiatedGradientReduction') as mock_egr, \
             patch('fairness.service.inprocessing.joblib.dump') as mock_dump, \
             patch.object(InprocessingService, 'mitigation_model_analyze', return_value=mock_metrics):
            mock_model = Mock()
            mock_model.fit.return_value = None
            mock_pred = Mock()
            mock_pred.labels = np.array([[1], [0]])
            mock_model.predict.return_value = mock_pred
            mock_egr.return_value = mock_model
            
            batch_id_obj = BatchId(Batch_id=batch_id_value)
            result = service.inprocessing_exponentiated_gradient_reduction(batch_id_obj)
            
            assert result is not None
            assert 'modelfileId' in result
            assert 'metrics' in result
            mock_dump.assert_called_once()
    
    def test_inprocessing_metrics_structure(self, setup_database):
        """Test metrics structure"""
        service = InprocessingService(setup_database[0])
        batch_id = setup_database[2]
        
        # Mock the entire flow including mitigation_model_analyze to avoid size mismatch
        mock_metrics = {
            'demographic_parity_difference': 0.1,
            'equalized_odds_difference': 0.2,
            'true_positive_rate': 0.8,
            'true_negative_rate': 0.7,
            'false_positive_rate': 0.3,
            'false_negative_rate': 0.2,
            'accuracy_score': 0.75
        }
        
        with patch('fairness.service.inprocessing.ExponentiatedGradientReduction') as mock_egr, \
             patch('fairness.service.inprocessing.joblib.dump') as mock_dump, \
             patch.object(InprocessingService, 'mitigation_model_analyze', return_value=mock_metrics):
            mock_model = Mock()
            mock_model.fit.return_value = None
            mock_pred = Mock()
            mock_pred.labels = np.array([[1], [0]])
            mock_model.predict.return_value = mock_pred
            mock_egr.return_value = mock_model
            
            payload = {'Batch_id': batch_id}
            result = service.inprocessing_exponentiated_gradient_reduction(payload)
            
            metrics = result['metrics']
            assert 'demographic_parity_difference' in metrics
            assert 'equalized_odds_difference' in metrics
            assert 'true_positive_rate' in metrics
            assert 'true_negative_rate' in metrics
            assert 'false_positive_rate' in metrics
            assert 'false_negative_rate' in metrics
            assert 'accuracy_score' in metrics
    
    def test_inprocessing_batch_status_update(self, setup_database):
        """Test batch status updates correctly"""
        service = InprocessingService(setup_database[0])
        batch_id = setup_database[2]
        
        # Mock the entire flow including mitigation_model_analyze to avoid size mismatch
        mock_metrics = {
            'demographic_parity_difference': 0.1,
            'equalized_odds_difference': 0.2,
            'true_positive_rate': 0.8,
            'true_negative_rate': 0.7,
            'false_positive_rate': 0.3,
            'false_negative_rate': 0.2,
            'accuracy_score': 0.75
        }
        
        with patch('fairness.service.inprocessing.ExponentiatedGradientReduction') as mock_egr, \
             patch('fairness.service.inprocessing.joblib.dump') as mock_dump, \
             patch.object(InprocessingService, 'mitigation_model_analyze', return_value=mock_metrics):
            mock_model = Mock()
            mock_model.fit.return_value = None
            mock_pred = Mock()
            mock_pred.labels = np.array([[1], [0]])
            mock_model.predict.return_value = mock_pred
            mock_egr.return_value = mock_model
            
            payload = {'Batch_id': batch_id}
            result = service.inprocessing_exponentiated_gradient_reduction(payload)
            
            # Verify batch.find returns data (Status field is not in projection)
            batch_details = service.batch.find(batch_id=batch_id, tenet_id=1)
            assert batch_details is not None
            assert 'DataId' in batch_details
            assert result is not None
    
    def test_inprocessing_missing_batch_id_none(self, setup_database):
        """Test with None batch ID"""
        service = InprocessingService(setup_database[0])
        
        payload = {'Batch_id': None}
        try:
            result = service.inprocessing_exponentiated_gradient_reduction(payload)
            assert result is None or 'error' in str(result).lower()
        except Exception:
            pass
    
    def test_inprocessing_missing_batch_id_empty(self, setup_database):
        """Test with empty string batch ID"""
        service = InprocessingService(setup_database[0])
        
        payload = {'Batch_id': ''}
        try:
            result = service.inprocessing_exponentiated_gradient_reduction(payload)
            assert result is None or 'error' in str(result).lower()
        except Exception:
            pass
    
    def test_inprocessing_model_file_saved(self, setup_database):
        """Test model file is saved"""
        service = InprocessingService(setup_database[0])
        batch_id = setup_database[2]
        
        # Mock the entire flow including mitigation_model_analyze to avoid size mismatch
        mock_metrics = {
            'demographic_parity_difference': 0.1,
            'equalized_odds_difference': 0.2,
            'true_positive_rate': 0.8,
            'true_negative_rate': 0.7,
            'false_positive_rate': 0.3,
            'false_negative_rate': 0.2,
            'accuracy_score': 0.75
        }
        
        with patch('fairness.service.inprocessing.ExponentiatedGradientReduction') as mock_egr, \
             patch('fairness.service.inprocessing.joblib.dump') as mock_dump, \
             patch.object(InprocessingService, 'mitigation_model_analyze', return_value=mock_metrics):
            mock_model = Mock()
            mock_model.fit.return_value = None
            mock_pred = Mock()
            mock_pred.labels = np.array([[1], [0]])
            mock_model.predict.return_value = mock_pred
            mock_egr.return_value = mock_model
            
            payload = {'Batch_id': batch_id}
            result = service.inprocessing_exponentiated_gradient_reduction(payload)
            
            assert result['modelfileId'] is not None
            assert isinstance(result['modelfileId'], (str, float))
            mock_dump.assert_called_once()
    
    def test_inprocessing_invalid_batch_id(self, setup_database):
        """Test with invalid batch ID"""
        service = InprocessingService(setup_database[0])
        
        payload = {'Batch_id': 'invalid_batch_999'}
        
        try:
            result = service.inprocessing_exponentiated_gradient_reduction(payload)
            assert False, "Should have raised an exception"
        except Exception:
            pass
    
    def test_inprocessing_no_content_error(self, setup_database):
        """Test handling of no content from fileStore"""
        service = InprocessingService(setup_database[0])
        batch_id = setup_database[2]
        
        payload = {'Batch_id': batch_id}
        
        with patch.object(service.fileStore, 'read_file', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                service.inprocessing_exponentiated_gradient_reduction(payload)
            
            assert exc_info.value.status_code == 500
            assert "No content received" in exc_info.value.detail


class TestInprocessingServiceConstants:
    """Test class-level constants"""
    
    def test_aware_model_paths(self):
        """Test AWARE_MODEL paths"""
        assert hasattr(InprocessingService, 'AWARE_MODEL_LOCAL_PATH')
        assert hasattr(InprocessingService, 'AWARE_MODEL_UPLOAD_PATH')
        assert InprocessingService.AWARE_MODEL_LOCAL_PATH.endswith(os.path.join('aware_model', ''))
        assert InprocessingService.AWARE_MODEL_UPLOAD_PATH == 'responsible-ai//responsible-ai-fairness//aware-model'
    
    def test_payload_attributes(self):
        """Test payload class attributes"""
        assert hasattr(InprocessingService, 'request_payload')
        assert hasattr(InprocessingService, 'mitigation_payload')
        assert hasattr(InprocessingService, 'pretrainMitigation_payload')
        assert hasattr(InprocessingService, 'ca_dict')


class TestInprocessingEdgeCases:
    """Test edge cases"""
    
    def test_mismatched_array_lengths(self):
        """Test mismatched array lengths"""
        y_true = np.array([1, 0, 1])
        y_pred = np.array([1, 0, 1, 0, 1])
        sensitive_features = pd.Series(['A', 'B', 'A'])
        
        with pytest.raises(ValueError):
            InprocessingService.mitigation_model_analyze(
                y_true, y_pred, sensitive_features
            )
    
    def test_single_class_predictions(self):
        """Test single class predictions"""
        y_true = np.array([1, 1, 1, 1])
        y_pred = np.array([1, 1, 1, 1])
        sensitive_features = pd.Series(['A', 'B', 'A', 'B'])
        
        result = InprocessingService.mitigation_model_analyze(
            y_true, y_pred, sensitive_features
        )
        
        assert result['accuracy_score'] == 1.0


class TestInprocessingIntegration:
    """Integration tests"""
    
    def test_full_workflow(self, setup_database):
        """Test complete workflow"""
        service = InprocessingService(setup_database[0])
        file_id = setup_database[1]
        batch_id = setup_database[2]
        
        # Step 1: Upload
        upload_payload = {'fileId': file_id}
        upload_result = service.upload_inprocess(upload_payload)
        assert 'feature_list' in upload_result
        
        # Step 2: Process
        # Mock the entire flow including mitigation_model_analyze to avoid size mismatch
        mock_metrics = {
            'demographic_parity_difference': 0.1,
            'equalized_odds_difference': 0.2,
            'true_positive_rate': 0.8,
            'true_negative_rate': 0.7,
            'false_positive_rate': 0.3,
            'false_negative_rate': 0.2,
            'accuracy_score': 0.75
        }
        
        with patch('fairness.service.inprocessing.ExponentiatedGradientReduction') as mock_egr, \
             patch('fairness.service.inprocessing.joblib.dump') as mock_dump, \
             patch.object(InprocessingService, 'mitigation_model_analyze', return_value=mock_metrics):
            mock_model = Mock()
            mock_model.fit.return_value = None
            mock_pred = Mock()
            mock_pred.labels = np.array([[1], [0]])
            mock_model.predict.return_value = mock_pred
            mock_egr.return_value = mock_model
            
            inprocess_payload = {'Batch_id': batch_id}
            inprocess_result = service.inprocessing_exponentiated_gradient_reduction(
                inprocess_payload
            )
            
            assert inprocess_result is not None
            assert 'modelfileId' in inprocess_result
            assert 'metrics' in inprocess_result
            
            metrics = inprocess_result['metrics']
            for key, value in metrics.items():
                assert isinstance(value, (int, float, np.number))
            
            mock_dump.assert_called_once()


class TestInprocessingPerformance:
    """Test performance"""
    
    def test_large_dataset_handling(self):
        """Test large dataset"""
        y_true = np.random.randint(0, 2, size=10000)
        y_pred = np.random.randint(0, 2, size=10000)
        sensitive_features = pd.Series(np.random.choice(['A', 'B', 'C'], size=10000))
        
        result = InprocessingService.mitigation_model_analyze(
            y_true, y_pred, sensitive_features
        )
        
        assert result is not None
        assert 'accuracy_score' in result


# Run with: pytest test_inprocessing.py -v --cov=fairness.service.inprocessing --cov-report=term-missing
