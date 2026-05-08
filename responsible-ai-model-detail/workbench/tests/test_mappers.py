"""
Unit tests for mappers module.
"""

import pytest
import os
import sys
import json
from unittest.mock import Mock
from fastapi import UploadFile

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app.mappers.mappers import (
    TenetDataRequest,
    GetModelPayloadRequest,
    GetModelRequest,
    UpdateModelPayloadRequest,
    GetDataPayloadRequest,
    GetDataRequest,
    UpdateDataPayloadRequest,
    GetBatchPayloadRequest,
    GetBatchStatusPayloadRequest,
    GetPreprocessorPayloadRequest,
    GetPreprocessorRequest,
    UpdatePreprocessorPayloadRequest
)


class TestTenetDataRequest:
    """Tests for TenetDataRequest model."""
    
    def test_tenet_data_request_creation(self):
        tdr = TenetDataRequest(tenetName="Fairness", tenetId=1.0)
        assert tdr.tenetName == "Fairness"
        assert tdr.tenetId == 1.0
    
    def test_tenet_data_request_default_values(self):
        tdr = TenetDataRequest()
        assert tdr.tenetName == "RAI"
        assert tdr.tenetId == "0.0"
    
    def test_tenet_data_request_from_json_string(self):
        json_str = '{"tenetName": "Security", "tenetId": 2.0}'
        tdr = TenetDataRequest.model_validate(json_str)
        assert tdr.tenetName == "Security"
        assert tdr.tenetId == 2.0
    
    def test_tenet_data_request_from_dict(self):
        data = {"tenetName": "Explainability", "tenetId": 3.0}
        tdr = TenetDataRequest(**data)
        assert tdr.tenetName == "Explainability"
        assert tdr.tenetId == 3.0


class TestGetModelPayloadRequest:
    """Tests for GetModelPayloadRequest model."""
    
    def test_get_model_payload_request_with_all_fields(self):
        gmpr = GetModelPayloadRequest(
            modelName="CompleteModel",
            targetDataType="Image",
            taskType="classification",
            imageClassificationTypes="binary classification",
            targetClassifier="SklearnClassifier",
            useModelApi="No",
            modelEndPoint="NA",
            data="training_data",
            prediction="pred_output"
        )
        assert gmpr.modelName == "CompleteModel"
        assert gmpr.imageClassificationTypes == "binary classification"
        assert gmpr.data == "training_data"
        assert gmpr.prediction == "pred_output"


class TestGetModelRequest:
    """Tests for GetModelRequest model."""
    
    def test_get_model_request_with_file(self):
        mock_file = Mock(spec=UploadFile)
        gmr = GetModelRequest(ModelFile=mock_file)
        assert gmr.ModelFile is not None
    
    def test_get_model_request_without_file(self):
        gmr = GetModelRequest()
        assert gmr.ModelFile is None


class TestUpdateModelPayloadRequest:
    """Tests for UpdateModelPayloadRequest model."""
    pass


class TestGetDataPayloadRequest:
    """Tests for GetDataPayloadRequest model."""
    
    def test_get_data_payload_request_from_json(self):
        json_str = '{"dataFileName": "ImageData", "dataType": "Image", "groundTruthClassNames": [0, 1, 2], "groundTruthClassLabel": "label"}'
        gdpr = GetDataPayloadRequest.model_validate_json(json_str)
        assert gdpr.dataFileName == "ImageData"
        assert gdpr.groundTruthClassNames == [0, 1, 2]
        assert gdpr.groundTruthClassLabel == "label"


class TestGetDataRequest:
    """Tests for GetDataRequest model."""
    
    def test_get_data_request_with_file(self):
        mock_file = Mock(spec=UploadFile)
        gdr = GetDataRequest(DataFile=mock_file)
        assert gdr.DataFile is not None
    
    def test_get_data_request_without_file(self):
        gdr = GetDataRequest()
        assert gdr.DataFile is None


class TestUpdateDataPayloadRequest:
    """Tests for UpdateDataPayloadRequest model."""
    
    def test_update_data_payload_request_from_json(self):
        json_str = '{"dataType": "Text", "groundTruthClassNames": [0, 1, 2, 3], "groundTruthClassLabel": "category"}'
        udpr = UpdateDataPayloadRequest.model_validate_json(json_str)
        assert udpr.dataType == "Text"
        assert len(udpr.groundTruthClassNames) == 4
    
    def test_update_data_payload_request_custom_values(self):
        udpr = UpdateDataPayloadRequest(
            dataType="Image",
            groundTruthClassNames=[0, 1, 2],
            groundTruthClassLabel="category"
        )
        assert udpr.dataType == "Image"
        assert udpr.groundTruthClassLabel == "category"


class TestGetBatchPayloadRequest:
    """Tests for GetBatchPayloadRequest model."""
    pass


class TestGetBatchStatusPayloadRequest:
    """Tests for GetBatchStatusPayloadRequest model."""
    
    def test_get_batch_status_payload_request_creation(self):
        gbspr = GetBatchStatusPayloadRequest(batchId=1.1)
        assert gbspr.batchId == 1.1
    
    def test_get_batch_status_payload_request_with_value(self):
        gbspr = GetBatchStatusPayloadRequest(batchId=123.456)
        assert gbspr.batchId == 123.456
    
    def test_get_batch_status_payload_request_various_ids(self):
        gbspr1 = GetBatchStatusPayloadRequest(batchId=123.456)
        gbspr2 = GetBatchStatusPayloadRequest(batchId=0.0)
        gbspr3 = GetBatchStatusPayloadRequest(batchId=999.999)
        
        assert gbspr1.batchId == 123.456
        assert gbspr2.batchId == 0.0
        assert gbspr3.batchId == 999.999


class TestGetPreprocessorPayloadRequest:
    """Tests for GetPreprocessorPayloadRequest model."""
    
    def test_get_preprocessor_payload_request_creation(self):
        gppr = GetPreprocessorPayloadRequest(
            userId="admin",
            preprocessorName="StandardScaler",
            preprocessorFileId=4.1
        )
        assert gppr.userId == "admin"
        assert gppr.preprocessorName == "StandardScaler"
        assert gppr.preprocessorFileId == 4.1


class TestGetPreprocessorRequest:
    """Tests for GetPreprocessorRequest model."""
    
    def test_get_preprocessor_request_with_file(self):
        mock_file = Mock(spec=UploadFile)
        gpr = GetPreprocessorRequest(PreprocessorFile=mock_file)
        assert gpr.PreprocessorFile is not None
    
    def test_get_preprocessor_request_without_file(self):
        gpr = GetPreprocessorRequest()
        assert gpr.PreprocessorFile is None


class TestUpdatePreprocessorPayloadRequest:
    """Tests for UpdatePreprocessorPayloadRequest model."""
    
    def test_update_preprocessor_payload_request_creation(self):
        uppr = UpdatePreprocessorPayloadRequest(preprocessorName="UpdatedScaler")
        assert uppr.preprocessorName == "UpdatedScaler"
    
    def test_update_preprocessor_payload_request_with_name(self):
        uppr = UpdatePreprocessorPayloadRequest(preprocessorName="StandardScaler")
        assert uppr.preprocessorName == "StandardScaler"
    
    def test_update_preprocessor_payload_request_various_names(self):
        uppr1 = UpdatePreprocessorPayloadRequest(preprocessorName="MinMaxScaler")
        uppr2 = UpdatePreprocessorPayloadRequest(preprocessorName="RobustScaler")
        uppr3 = UpdatePreprocessorPayloadRequest(preprocessorName="CustomPreprocessor")
        
        assert uppr1.preprocessorName == "MinMaxScaler"
        assert uppr2.preprocessorName == "RobustScaler"
        assert uppr3.preprocessorName == "CustomPreprocessor"


class TestMapperValidation:
    """Tests for validation in mappers."""
    
    def test_update_data_json_validation(self):
        json_str = json.dumps({
            "dataType": "Text",
            "groundTruthClassNames": [0, 1],
            "groundTruthClassLabel": "sentiment"
        })
        udpr = UpdateDataPayloadRequest.model_validate(json_str)
        assert udpr.groundTruthClassLabel == "sentiment"
    
    def test_tenet_data_validation(self):
        tdr = TenetDataRequest(tenetName="Security", tenetId=2.0)
        assert tdr.tenetName == "Security"
        assert tdr.tenetId == 2.0
