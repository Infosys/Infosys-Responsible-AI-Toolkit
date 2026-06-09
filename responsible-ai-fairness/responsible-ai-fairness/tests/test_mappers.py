"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pytest
import json
from io import BytesIO
from unittest.mock import Mock, MagicMock
from pydantic import ValidationError
from fastapi import UploadFile
from starlette.datastructures import Headers

from fairness.mappers.mappers import (
    IndividualFairnessRequest,
    ProtetedAttribute,
    TrainingDatasetPath,
    PredictionDatasetPath,
    OutputPath,
    PreDataset,
    PostDataset,
    BiasAnalyzeRequest,
    metricsEntity,
    BiasResults,
    BiasAnalyzeResponse,
    BiasAnalyzeMetrics,
    BiasAnalyzeIndividualMetric,
    BiasPretrainMitigationResponse,
    BiasPretrainMitigationResponseUseCase,
    MitigationType,
    MitigationTechnique,
    MitigateBiasRequest,
    PreprocessingMitigateBiasRequest,
    MitigationResults,
    PreprocessingMitigationResults,
    MitigationAnalyzeResponse,
    PreprocessingMitigationAnalyzeResponse,
    GetBiasRequest,
    GetBiasResponse,
    GetMitigationRequest,
    BatchId,
    FairnessAnalysisRequest,
    MitigationRequest,
    IndividualRequest,
    AnalysisRequest,
    GetDataRequest,
    AuditRequest,
    MonitoringRequest
)


# Test fixtures
@pytest.fixture
def sample_protected_attribute():
    """Sample protected attribute for testing"""
    return {
        "name": "race",
        "privileged": ["White"],
        "unprivileged": ["Black", "Amer-Indian-Eskimo", "Asian-Pac-Islander", "Other"]
    }


@pytest.fixture
def sample_training_dataset_path():
    """Sample training dataset path for testing"""
    return {
        "storage": "INFY_AICLD_NUTANIX",
        "uri": "responsible-ai//responsible-ai-fairness//adult.csv"
    }


@pytest.fixture
def sample_prediction_dataset_path():
    """Sample prediction dataset path for testing"""
    return {
        "storage": "INFY_AICLD_NUTANIX",
        "uri": "responsible-ai//responsible-ai-fairness//TestFairData.csv"
    }


@pytest.fixture
def sample_output_path():
    """Sample output path for testing"""
    return {
        "storage": "INFY_AICLD_NUTANIX",
        "uri": "responsible-ai//responsible-ai-fairness//OUTPUT.json"
    }


@pytest.fixture
def sample_pre_dataset(sample_training_dataset_path):
    """Sample pre-training dataset for testing"""
    return {
        "id": 32,
        "name": "Adult",
        "fileType": "text/csv",
        "path": sample_training_dataset_path,
        "label": "income-per-year"
    }


@pytest.fixture
def sample_post_dataset(sample_prediction_dataset_path):
    """Sample post-training dataset for testing"""
    return {
        "id": 32,
        "name": "Adult",
        "fileType": "text/csv",
        "path": sample_prediction_dataset_path,
        "label": "income-per-year",
        "predlabel": "labels_pred"
    }


@pytest.fixture
def sample_metrics_entity():
    """Sample metrics entity for testing"""
    return {
        "name": "STATISTICAL-PARITY-DIFFERENCE",
        "description": "Computed as the difference of the rate of favorable outcomes",
        "value": "0.25"
    }


@pytest.fixture
def mock_upload_file():
    """Mock UploadFile for testing"""
    file_content = b"test,data\n1,2\n3,4"
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test.csv"
    mock_file.content_type = "text/csv"
    mock_file.file = BytesIO(file_content)
    return mock_file


class TestIndividualFairnessRequest:
    """Test suite for IndividualFairnessRequest model"""
    
    def test_valid_individual_fairness_request(self):
        """Test creating a valid IndividualFairnessRequest"""
        data = {
            "labels": ["income-per-year"],
            "recordId": "6014sla28j123h"
        }
        request = IndividualFairnessRequest(**data)
        assert request.labels == ["income-per-year"]
        assert request.recordId == "6014sla28j123h"
    
    def test_individual_fairness_request_with_multiple_labels(self):
        """Test IndividualFairnessRequest with multiple labels"""
        data = {
            "labels": ["income-per-year", "education"],
            "recordId": "test123"
        }
        request = IndividualFairnessRequest(**data)
        assert len(request.labels) == 2
    
    def test_invalid_individual_fairness_request_missing_fields(self):
        """Test IndividualFairnessRequest with missing required fields"""
        with pytest.raises(ValidationError):
            IndividualFairnessRequest(labels=["income-per-year"])


class TestProtetedAttribute:
    """Test suite for ProtetedAttribute model"""
    
    def test_valid_protected_attribute(self, sample_protected_attribute):
        """Test creating a valid ProtetedAttribute"""
        attr = ProtetedAttribute(**sample_protected_attribute)
        assert attr.name == "race"
        assert attr.privileged == ["White"]
        assert len(attr.unprivileged) == 4
    
    def test_protected_attribute_with_custom_values(self):
        """Test ProtetedAttribute with custom values"""
        data = {
            "name": "sex",
            "privileged": ["Male"],
            "unprivileged": ["Female"]
        }
        attr = ProtetedAttribute(**data)
        assert attr.name == "sex"
        assert attr.privileged == ["Male"]
        assert attr.unprivileged == ["Female"]
    
    def test_protected_attribute_with_multiple_unprivileged(self):
        """Test ProtetedAttribute with multiple unprivileged groups"""
        data = {
            "name": "age",
            "privileged": ["Adult"],
            "unprivileged": ["Child", "Elderly", "Teen"]
        }
        attr = ProtetedAttribute(**data)
        assert len(attr.unprivileged) == 3


class TestDatasetPaths:
    """Test suite for dataset path models"""
    
    def test_valid_training_dataset_path(self, sample_training_dataset_path):
        """Test creating a valid TrainingDatasetPath"""
        path = TrainingDatasetPath(**sample_training_dataset_path)
        assert path.storage == "INFY_AICLD_NUTANIX"
        assert "adult.csv" in path.uri
    
    def test_valid_prediction_dataset_path(self, sample_prediction_dataset_path):
        """Test creating a valid PredictionDatasetPath"""
        path = PredictionDatasetPath(**sample_prediction_dataset_path)
        assert path.storage == "INFY_AICLD_NUTANIX"
        assert "TestFairData.csv" in path.uri
    
    def test_valid_output_path(self, sample_output_path):
        """Test creating a valid OutputPath"""
        path = OutputPath(**sample_output_path)
        assert path.storage == "INFY_AICLD_NUTANIX"
        assert "OUTPUT.json" in path.uri
    
    def test_dataset_path_with_different_storage(self):
        """Test dataset paths with different storage types"""
        data = {
            "storage": "AWS_S3",
            "uri": "s3://bucket/path/to/file.csv"
        }
        path = TrainingDatasetPath(**data)
        assert path.storage == "AWS_S3"
        assert path.uri.startswith("s3://")


class TestPreDataset:
    """Test suite for PreDataset model"""
    
    def test_valid_pre_dataset(self, sample_pre_dataset):
        """Test creating a valid PreDataset"""
        dataset = PreDataset(**sample_pre_dataset)
        assert dataset.id == 32
        assert dataset.name == "Adult"
        assert dataset.fileType == "text/csv"
        assert dataset.label == "income-per-year"
    
    def test_pre_dataset_different_file_types(self, sample_training_dataset_path):
        """Test PreDataset with different file types"""
        data = {
            "id": 10,
            "name": "TestDataset",
            "fileType": "application/json",
            "path": sample_training_dataset_path,
            "label": "target"
        }
        dataset = PreDataset(**data)
        assert dataset.fileType == "application/json"
    
    def test_pre_dataset_missing_required_fields(self):
        """Test PreDataset with missing required fields"""
        with pytest.raises(ValidationError):
            PreDataset(id=1, name="Test")


class TestPostDataset:
    """Test suite for PostDataset model"""
    
    def test_valid_post_dataset(self, sample_post_dataset):
        """Test creating a valid PostDataset"""
        dataset = PostDataset(**sample_post_dataset)
        assert dataset.id == 32
        assert dataset.name == "Adult"
        assert dataset.label == "income-per-year"
        assert dataset.predlabel == "labels_pred"
    
    def test_post_dataset_with_different_labels(self, sample_prediction_dataset_path):
        """Test PostDataset with different label values"""
        data = {
            "id": 50,
            "name": "TestDataset",
            "fileType": "text/csv",
            "path": sample_prediction_dataset_path,
            "label": "actual",
            "predlabel": "predicted"
        }
        dataset = PostDataset(**data)
        assert dataset.label == "actual"
        assert dataset.predlabel == "predicted"


class TestBiasAnalyzeRequest:
    """Test suite for BiasAnalyzeRequest model"""
    
    def test_valid_bias_analyze_request(self, sample_pre_dataset, sample_post_dataset, 
                                       sample_protected_attribute, sample_output_path):
        """Test creating a valid BiasAnalyzeRequest"""
        data = {
            "method": "STATISTICAL-PARITY-DIFFERENCE",
            "biasType": "PRETRAIN",
            "taskType": "CLASSIFICATION",
            "trainingDataset": sample_pre_dataset,
            "predictionDataset": sample_post_dataset,
            "features": "age,workclass,hours-per-week,education,native-country,race,sex,income-per-year",
            "categoricalAttributes": "education,native-country,workclass,sex",
            "favourableOutcome": ['>50K'],
            "labelmaps": {">50K": 1, "<=50K": 0},
            "facet": [sample_protected_attribute],
            "outputPath": sample_output_path
        }
        request = BiasAnalyzeRequest(**data)
        assert request.method == "STATISTICAL-PARITY-DIFFERENCE"
        assert request.biasType == "PRETRAIN"
        assert request.taskType == "CLASSIFICATION"
        assert len(request.facet) == 1
    
    def test_bias_analyze_request_with_multiple_facets(self, sample_pre_dataset, sample_post_dataset,
                                                       sample_output_path):
        """Test BiasAnalyzeRequest with multiple protected attributes"""
        facets = [
            {"name": "race", "privileged": ["White"], "unprivileged": ["Black"]},
            {"name": "sex", "privileged": ["Male"], "unprivileged": ["Female"]}
        ]
        data = {
            "method": "ALL",
            "biasType": "PRETRAIN",
            "taskType": "CLASSIFICATION",
            "trainingDataset": sample_pre_dataset,
            "predictionDataset": sample_post_dataset,
            "features": "age,sex,race",
            "categoricalAttributes": "sex,race",
            "favourableOutcome": [1],
            "labelmaps": {"Yes": 1, "No": 0},
            "facet": facets,
            "outputPath": sample_output_path
        }
        request = BiasAnalyzeRequest(**data)
        assert len(request.facet) == 2


class TestMetricsEntity:
    """Test suite for metricsEntity model"""
    
    def test_valid_metrics_entity(self, sample_metrics_entity):
        """Test creating a valid metricsEntity"""
        metric = metricsEntity(**sample_metrics_entity)
        assert metric.name == "STATISTICAL-PARITY-DIFFERENCE"
        assert metric.value == "0.25"
    
    def test_metrics_entity_with_different_values(self):
        """Test metricsEntity with different values"""
        data = {
            "name": "DISPARATE-IMPACT",
            "description": "Test description",
            "value": "0.85"
        }
        metric = metricsEntity(**data)
        assert metric.name == "DISPARATE-IMPACT"
        assert metric.value == "0.85"


class TestBiasResults:
    """Test suite for BiasResults model"""
    
    def test_valid_bias_results(self, sample_protected_attribute, sample_metrics_entity):
        """Test creating a valid BiasResults"""
        data = {
            "biasDetected": True,
            "protectedAttribute": [sample_protected_attribute],
            "metrics": [sample_metrics_entity]
        }
        results = BiasResults(**data)
        assert results.biasDetected is True
        assert len(results.protectedAttribute) == 1
        assert len(results.metrics) == 1
    
    def test_bias_results_no_bias_detected(self, sample_protected_attribute, sample_metrics_entity):
        """Test BiasResults when no bias is detected"""
        data = {
            "biasDetected": False,
            "protectedAttribute": [sample_protected_attribute],
            "metrics": [sample_metrics_entity]
        }
        results = BiasResults(**data)
        assert results.biasDetected is False


class TestBiasAnalyzeResponse:
    """Test suite for BiasAnalyzeResponse model"""
    
    def test_valid_bias_analyze_response(self, sample_protected_attribute, sample_metrics_entity):
        """Test creating a valid BiasAnalyzeResponse"""
        bias_result = {
            "biasDetected": True,
            "protectedAttribute": [sample_protected_attribute],
            "metrics": [sample_metrics_entity]
        }
        data = {
            "biasResults": [bias_result]
        }
        response = BiasAnalyzeResponse(**data)
        assert len(response.biasResults) == 1
    
    def test_bias_analyze_response_with_multiple_results(self, sample_protected_attribute, 
                                                         sample_metrics_entity):
        """Test BiasAnalyzeResponse with multiple bias results"""
        bias_result1 = {
            "biasDetected": True,
            "protectedAttribute": [sample_protected_attribute],
            "metrics": [sample_metrics_entity]
        }
        bias_result2 = {
            "biasDetected": False,
            "protectedAttribute": [{"name": "sex", "privileged": ["Male"], "unprivileged": ["Female"]}],
            "metrics": [sample_metrics_entity]
        }
        data = {
            "biasResults": [bias_result1, bias_result2]
        }
        response = BiasAnalyzeResponse(**data)
        assert len(response.biasResults) == 2


class TestBiasAnalyzeMetrics:
    """Test suite for BiasAnalyzeMetrics model"""
    
    def test_valid_bias_analyze_metrics(self, sample_protected_attribute, sample_metrics_entity):
        """Test creating a valid BiasAnalyzeMetrics"""
        bias_result = {
            "biasDetected": True,
            "protectedAttribute": [sample_protected_attribute],
            "metrics": [sample_metrics_entity]
        }
        data = {
            "biasResults": [bias_result],
            "individualMetrics": [{"metric": "value"}]
        }
        metrics = BiasAnalyzeMetrics(**data)
        assert len(metrics.biasResults) == 1
        assert metrics.individualMetrics is not None
    
    def test_bias_analyze_metrics_without_individual_metrics(self, sample_protected_attribute,
                                                            sample_metrics_entity):
        """Test BiasAnalyzeMetrics without individual metrics"""
        bias_result = {
            "biasDetected": True,
            "protectedAttribute": [sample_protected_attribute],
            "metrics": [sample_metrics_entity]
        }
        data = {
            "biasResults": [bias_result]
        }
        metrics = BiasAnalyzeMetrics(**data)
        assert metrics.individualMetrics is None


class TestBiasAnalyzeIndividualMetric:
    """Test suite for BiasAnalyzeIndividualMetric model"""
    
    def test_valid_individual_metric(self):
        """Test creating a valid BiasAnalyzeIndividualMetric"""
        data = {
            "individualMetrics": [{"id": 1, "score": 0.85}]
        }
        metric = BiasAnalyzeIndividualMetric(**data)
        assert metric.individualMetrics is not None
        assert len(metric.individualMetrics) == 1
    
    def test_individual_metric_none(self):
        """Test BiasAnalyzeIndividualMetric with None"""
        data = {
            "individualMetrics": None
        }
        metric = BiasAnalyzeIndividualMetric(**data)
        assert metric.individualMetrics is None


class TestBiasPretrainMitigationResponse:
    """Test suite for BiasPretrainMitigationResponse model"""
    
    def test_valid_pretrain_mitigation_response(self, sample_protected_attribute, sample_metrics_entity):
        """Test creating a valid BiasPretrainMitigationResponse"""
        bias_result = {
            "biasDetected": True,
            "protectedAttribute": [sample_protected_attribute],
            "metrics": [sample_metrics_entity]
        }
        data = {
            "biasResults": [bias_result],
            "fileName": "mitigated_dataset.csv"
        }
        response = BiasPretrainMitigationResponse(**data)
        assert response.fileName == "mitigated_dataset.csv"
    
    def test_pretrain_mitigation_response_use_case(self, sample_protected_attribute, 
                                                    sample_metrics_entity):
        """Test BiasPretrainMitigationResponseUseCase"""
        bias_result = {
            "biasDetected": True,
            "protectedAttribute": [sample_protected_attribute],
            "metrics": [sample_metrics_entity]
        }
        data = {
            "biasResults": [bias_result],
            "fileName": ["file1.csv", "file2.csv"]
        }
        response = BiasPretrainMitigationResponseUseCase(**data)
        assert len(response.fileName) == 2


class TestMitigationEnums:
    """Test suite for Mitigation enums"""
    
    def test_mitigation_type_enum(self):
        """Test MitigationType enum values"""
        assert MitigationType.PreProcessing.value == 'PREPROCESSING'
        assert MitigationType.InProcessing.value == 'INPROCESSING'
        assert MitigationType.PostProcessing.value == 'POSTPROCESSING'
    
    def test_mitigation_technique_enum(self):
        """Test MitigationTechnique enum values"""
        assert MitigationTechnique.REWEIGHING.value == 'REWEIGHING'
        assert MitigationTechnique.DISPARATE_IMPACT_REMOVER.value == 'DISPARATE IMPACT REMOVER'
        assert MitigationTechnique.EQUALIZED_ODDS.value == 'EQUALIZED ODDS'


class TestMitigateBiasRequest:
    """Test suite for MitigateBiasRequest model"""
    
    def test_valid_mitigate_bias_request(self, sample_pre_dataset, sample_post_dataset,
                                        sample_protected_attribute, sample_output_path):
        """Test creating a valid MitigateBiasRequest"""
        data = {
            "biasType": "PRETRAIN",
            "mitigationType": "PREPROCESSING",
            "mitigationTechnique": "REWEIGHING",
            "method": "ALL",
            "taskType": "CLASSIFICATION",
            "trainingDataset": sample_pre_dataset,
            "predictionDataset": sample_post_dataset,
            "features": "age,workclass,hours-per-week,education,native-country,race,sex,income-per-year",
            "categoricalAttributes": "education,native-country,workclass,sex",
            "favourableOutcome": ['>50K'],
            "labelmaps": {">50K": 1, "<=50K": 0},
            "facet": [sample_protected_attribute],
            "outputPath": sample_output_path
        }
        request = MitigateBiasRequest(**data)
        assert request.mitigationType == MitigationType.PreProcessing
        assert request.mitigationTechnique == MitigationTechnique.REWEIGHING


class TestPreprocessingMitigateBiasRequest:
    """Test suite for PreprocessingMitigateBiasRequest model"""
    
    def test_valid_preprocessing_mitigate_bias_request(self, sample_pre_dataset,
                                                       sample_protected_attribute, sample_output_path):
        """Test creating a valid PreprocessingMitigateBiasRequest"""
        data = {
            "method": "ALL",
            "biasType": "PRETRAIN",
            "taskType": "CLASSIFICATION",
            "mitigationType": "PREPROCESSING",
            "mitigationTechnique": "REWEIGHING",
            "trainingDataset": sample_pre_dataset,
            "features": "age,workclass,hours-per-week,education,native-country,race,sex,income-per-year",
            "categoricalAttributes": "education,native-country,workclass,sex",
            "favourableOutcome": ['>50K'],
            "labelmaps": {">50K": 1, "<=50K": 0},
            "facet": [sample_protected_attribute],
            "outputPath": sample_output_path
        }
        request = PreprocessingMitigateBiasRequest(**data)
        assert request.method == "ALL"
        assert request.biasType == "PRETRAIN"


class TestMitigationResults:
    """Test suite for MitigationResults model"""
    
    def test_valid_mitigation_results(self, sample_metrics_entity):
        """Test creating a valid MitigationResults"""
        data = {
            "biasType": "PRETRAIN",
            "mitigationType": "PREPROCESSING",
            "mitigationTechnique": "REWEIGHING",
            "metricsBeforeMitigation": [sample_metrics_entity],
            "biasDetectedOriginally": True,
            "metricsAfterMitigation": [sample_metrics_entity],
            "biasDetectedAfterMitigation": False,
            "mitigatedFileName": "mitigated_file.csv"
        }
        results = MitigationResults(**data)
        assert results.biasDetectedOriginally is True
        assert results.biasDetectedAfterMitigation is False
        assert results.mitigatedFileName == "mitigated_file.csv"
    
    def test_preprocessing_mitigation_results(self):
        """Test PreprocessingMitigationResults"""
        data = {
            "biasType": "PRETRAIN",
            "mitigationType": "PREPROCESSING",
            "mitigationTechnique": "REWEIGHING",
            "mitigatedFileName": "output.csv"
        }
        results = PreprocessingMitigationResults(**data)
        assert results.mitigatedFileName == "output.csv"


class TestMitigationAnalyzeResponse:
    """Test suite for MitigationAnalyzeResponse model"""
    
    def test_valid_mitigation_analyze_response(self, sample_metrics_entity):
        """Test creating a valid MitigationAnalyzeResponse"""
        mitigation_result = {
            "biasType": "PRETRAIN",
            "mitigationType": "PREPROCESSING",
            "mitigationTechnique": "REWEIGHING",
            "metricsBeforeMitigation": [sample_metrics_entity],
            "biasDetectedOriginally": True,
            "metricsAfterMitigation": [sample_metrics_entity],
            "biasDetectedAfterMitigation": False,
            "mitigatedFileName": "file.csv"
        }
        data = {
            "mitigationResults": [mitigation_result]
        }
        response = MitigationAnalyzeResponse(**data)
        assert len(response.mitigationResults) == 1
    
    def test_preprocessing_mitigation_analyze_response(self):
        """Test PreprocessingMitigationAnalyzeResponse"""
        mitigation_result = {
            "biasType": "PRETRAIN",
            "mitigationType": "PREPROCESSING",
            "mitigationTechnique": "REWEIGHING",
            "mitigatedFileName": "output.csv"
        }
        data = {
            "mitigationResults": [mitigation_result]
        }
        response = PreprocessingMitigationAnalyzeResponse(**data)
        assert len(response.mitigationResults) == 1


class TestGetBiasRequest:
    """Test suite for GetBiasRequest model"""
    
    def test_valid_get_bias_request(self):
        """Test creating a valid GetBiasRequest"""
        data = {
            "mlModelId": 23
        }
        request = GetBiasRequest(**data)
        assert request.mlModelId == 23
    
    def test_get_bias_request_different_id(self):
        """Test GetBiasRequest with different ID"""
        data = {
            "mlModelId": 999
        }
        request = GetBiasRequest(**data)
        assert request.mlModelId == 999


class TestGetBiasResponse:
    """Test suite for GetBiasResponse model"""
    
    def test_valid_get_bias_response(self, sample_protected_attribute, sample_metrics_entity):
        """Test creating a valid GetBiasResponse"""
        bias_result = {
            "biasDetected": True,
            "protectedAttribute": [sample_protected_attribute],
            "metrics": [sample_metrics_entity]
        }
        data = {
            "biasResults": [bias_result]
        }
        response = GetBiasResponse(**data)
        assert len(response.biasResults) == 1


class TestGetMitigationRequest:
    """Test suite for GetMitigationRequest model"""
    
    def test_valid_get_mitigation_request(self):
        """Test creating a valid GetMitigationRequest"""
        data = {
            "fileName": "Mitigated_Adult_1231213213.csv"
        }
        request = GetMitigationRequest(**data)
        assert "Mitigated_Adult" in request.fileName
    
    def test_get_mitigation_request_different_filename(self):
        """Test GetMitigationRequest with different filename"""
        data = {
            "fileName": "mitigated_data_v2.csv"
        }
        request = GetMitigationRequest(**data)
        assert request.fileName == "mitigated_data_v2.csv"


class TestBatchId:
    """Test suite for BatchId model"""
    
    def test_valid_batch_id(self):
        """Test creating a valid BatchId"""
        data = {
            "Batch_id": 123.12
        }
        batch = BatchId(**data)
        assert batch.Batch_id == 123.12
    
    def test_batch_id_with_integer(self):
        """Test BatchId with integer value"""
        data = {
            "Batch_id": 100.0
        }
        batch = BatchId(**data)
        assert batch.Batch_id == 100.0
    
    def test_batch_id_with_string_raises_error(self):
        """Test that BatchId with string raises ValidationError"""
        with pytest.raises(ValidationError):
            BatchId(Batch_id="invalid_string")


class TestFairnessAnalysisRequest:
    """Test suite for FairnessAnalysisRequest model"""
    
    def test_valid_fairness_analysis_request(self):
        """Test creating a valid FairnessAnalysisRequest"""
        data = {
            "biasType": "PRETRAIN",
            "taskType": "CLASSIFICATION",
            "methodType": "ALL",
            "label": "income-per-year",
            "predLabel": "labels_pred",
            "favourableOutcome": ">50K",
            "protectedAttribute": ["race", "sex"],
            "priviledgedGroups": [["White", "Black"], ["Male"]]
        }
        request = FairnessAnalysisRequest(**data)
        assert request.biasType == "PRETRAIN"
        assert len(request.protectedAttribute) == 2
        assert len(request.priviledgedGroups) == 2
    
    def test_fairness_analysis_request_from_json_string(self):
        """Test FairnessAnalysisRequest validation from JSON string"""
        data_dict = {
            "biasType": "POSTTRAIN",
            "taskType": "REGRESSION",
            "methodType": "SPECIFIC",
            "label": "target",
            "predLabel": "prediction",
            "favourableOutcome": "1",
            "protectedAttribute": ["age"],
            "priviledgedGroups": [["Young"]]
        }
        json_string = json.dumps(data_dict)
        request = FairnessAnalysisRequest.validate_to_json(json_string)
        assert request.biasType == "POSTTRAIN"
        assert request.taskType == "REGRESSION"


class TestMitigationRequest:
    """Test suite for MitigationRequest model"""
    
    def test_valid_mitigation_request(self):
        """Test creating a valid MitigationRequest"""
        data = {
            "mitigationType": "PREPROCESSING",
            "mitigationTechnique": "REWEIGHING",
            "taskType": "ALL",
            "label": "income-per-year",
            "favourableOutcome": ">50K",
            "protectedAttribute": ["race", "sex"],
            "priviledgedGroups": [["White", "Black"], ["Male"]]
        }
        request = MitigationRequest(**data)
        assert request.mitigationType == "PREPROCESSING"
        assert request.mitigationTechnique == "REWEIGHING"
    
    def test_mitigation_request_from_json_string(self):
        """Test MitigationRequest validation from JSON string"""
        data_dict = {
            "mitigationType": "INPROCESSING",
            "mitigationTechnique": "EQUALIZED_ODDS",
            "taskType": "CLASSIFICATION",
            "label": "target",
            "favourableOutcome": "1",
            "protectedAttribute": ["sex"],
            "priviledgedGroups": [["Male"]]
        }
        json_string = json.dumps(data_dict)
        request = MitigationRequest.validate_to_json(json_string)
        assert request.mitigationType == "INPROCESSING"


class TestIndividualRequest:
    """Test suite for IndividualRequest model"""
    
    def test_valid_individual_request(self):
        """Test creating a valid IndividualRequest"""
        data = {
            "label": ["income-per-year"],
            "k": 5
        }
        request = IndividualRequest(**data)
        assert request.label == ["income-per-year"]
        assert request.k == 5
    
    def test_individual_request_with_different_k(self):
        """Test IndividualRequest with different k value"""
        data = {
            "label": ["target", "prediction"],
            "k": 10
        }
        request = IndividualRequest(**data)
        assert request.k == 10
        assert len(request.label) == 2
    
    def test_individual_request_from_json_string(self):
        """Test IndividualRequest validation from JSON string"""
        data_dict = {
            "label": ["score"],
            "k": 3
        }
        json_string = json.dumps(data_dict)
        request = IndividualRequest.validate_to_json(json_string)
        assert request.k == 3


class TestAnalysisRequest:
    """Test suite for AnalysisRequest model"""
    
    def test_valid_analysis_request_with_string_outcome(self):
        """Test creating a valid AnalysisRequest with string outcome"""
        data = {
            "label": "labels_pred",
            "favourableOutcome": "positive",
            "categorical_attrbutes": ["race", "sex"]
        }
        request = AnalysisRequest(**data)
        assert request.label == "labels_pred"
        assert request.favourableOutcome == "positive"
        assert len(request.categorical_attrbutes) == 2
    
    def test_valid_analysis_request_with_int_outcome(self):
        """Test creating a valid AnalysisRequest with integer outcome"""
        data = {
            "label": "prediction",
            "favourableOutcome": 1,
            "categorical_attrbutes": ["age", "gender"]
        }
        request = AnalysisRequest(**data)
        assert request.favourableOutcome == 1
    
    def test_analysis_request_from_json_string(self):
        """Test AnalysisRequest validation from JSON string"""
        data_dict = {
            "label": "result",
            "favourableOutcome": 0,
            "categorical_attrbutes": ["feature1"]
        }
        json_string = json.dumps(data_dict)
        request = AnalysisRequest.validate_to_json(json_string)
        assert request.favourableOutcome == 0


class TestGetDataRequest:
    """Test suite for GetDataRequest model"""
    
    def test_valid_get_data_request_with_file(self, mock_upload_file):
        """Test creating a valid GetDataRequest with file"""
        data = {
            "file": mock_upload_file
        }
        request = GetDataRequest(**data)
        assert request.file is not None
    
    def test_get_data_request_file_attribute(self, mock_upload_file):
        """Test GetDataRequest file attribute"""
        request = GetDataRequest(file=mock_upload_file)
        assert request.file.filename == "test.csv"


class TestAuditRequest:
    """Test suite for AuditRequest model"""
    
    def test_valid_audit_request(self):
        """Test creating a valid AuditRequest"""
        data = {
            "label": "labels_pred",
            "favourableOutcome": 1,
            "categorical_attrbutes": ["race", "sex"]
        }
        request = AuditRequest(**data)
        assert request.label == "labels_pred"
        assert request.favourableOutcome == 1
        assert len(request.categorical_attrbutes) == 2
    
    def test_audit_request_with_string_outcome(self):
        """Test AuditRequest with string outcome"""
        data = {
            "label": "result",
            "favourableOutcome": "success",
            "categorical_attrbutes": ["attribute1"]
        }
        request = AuditRequest(**data)
        assert request.favourableOutcome == "success"
    
    def test_audit_request_from_json_string(self):
        """Test AuditRequest validation from JSON string"""
        data_dict = {
            "label": "prediction",
            "favourableOutcome": "positive",
            "categorical_attrbutes": ["feature1", "feature2"]
        }
        json_string = json.dumps(data_dict)
        request = AuditRequest.validate_to_json(json_string)
        assert len(request.categorical_attrbutes) == 2


class TestMonitoringRequest:
    """Test suite for MonitoringRequest model"""
    
    def test_valid_monitoring_request(self):
        """Test creating a valid MonitoringRequest"""
        data = {
            "label": "Prompt"
        }
        request = MonitoringRequest(**data)
        assert request.label == "Prompt"
    
    def test_monitoring_request_with_different_label(self):
        """Test MonitoringRequest with different label"""
        data = {
            "label": "Query"
        }
        request = MonitoringRequest(**data)
        assert request.label == "Query"
    
    def test_monitoring_request_from_json_string(self):
        """Test MonitoringRequest validation from JSON string"""
        data_dict = {
            "label": "UserInput"
        }
        json_string = json.dumps(data_dict)
        request = MonitoringRequest.validate_to_json(json_string)
        assert request.label == "UserInput"


class TestValidatorFunctions:
    """Test suite for model validator functions"""
    
    def test_fairness_analysis_request_validator_with_dict(self):
        """Test that validator handles dict input correctly"""
        data = {
            "biasType": "PRETRAIN",
            "taskType": "CLASSIFICATION",
            "methodType": "ALL",
            "label": "income-per-year",
            "predLabel": "labels_pred",
            "favourableOutcome": ">50K",
            "protectedAttribute": ["race"],
            "priviledgedGroups": [["White"]]
        }
        # When passed a dict, validate_to_json returns the dict as-is
        result = FairnessAnalysisRequest.validate_to_json(data)
        assert isinstance(result, dict)
        # Create instance directly from dict
        request = FairnessAnalysisRequest(**data)
        assert isinstance(request, FairnessAnalysisRequest)
    
    def test_mitigation_request_validator_with_dict(self):
        """Test that MitigationRequest validator handles dict input"""
        data = {
            "mitigationType": "PREPROCESSING",
            "mitigationTechnique": "REWEIGHING",
            "taskType": "ALL",
            "label": "target",
            "favourableOutcome": "1",
            "protectedAttribute": ["sex"],
            "priviledgedGroups": [["Male"]]
        }
        # When passed a dict, validate_to_json returns the dict as-is
        result = MitigationRequest.validate_to_json(data)
        assert isinstance(result, dict)
        # Create instance directly from dict
        request = MitigationRequest(**data)
        assert isinstance(request, MitigationRequest)
    
    def test_individual_request_validator_with_dict(self):
        """Test that IndividualRequest validator handles dict input"""
        data = {
            "label": ["feature"],
            "k": 7
        }
        # When passed a dict, validate_to_json returns the dict as-is
        result = IndividualRequest.validate_to_json(data)
        assert isinstance(result, dict)
        # Create instance directly from dict
        request = IndividualRequest(**data)
        assert isinstance(request, IndividualRequest)


class TestEdgeCases:
    """Test suite for edge cases and error handling"""
    
    def test_protected_attribute_empty_lists(self):
        """Test ProtetedAttribute with empty lists"""
        data = {
            "name": "test",
            "privileged": [],
            "unprivileged": []
        }
        attr = ProtetedAttribute(**data)
        assert len(attr.privileged) == 0
        assert len(attr.unprivileged) == 0
    
    def test_batch_id_negative_value(self):
        """Test BatchId with negative value"""
        data = {
            "Batch_id": -123.45
        }
        batch = BatchId(**data)
        assert batch.Batch_id == -123.45
    
    def test_metrics_entity_empty_description(self):
        """Test metricsEntity with empty description"""
        data = {
            "name": "TEST_METRIC",
            "description": "",
            "value": "0.0"
        }
        metric = metricsEntity(**data)
        assert metric.description == ""
    
    def test_individual_request_empty_label_list(self):
        """Test IndividualRequest with empty label list"""
        data = {
            "label": [],
            "k": 5
        }
        request = IndividualRequest(**data)
        assert len(request.label) == 0
    
    def test_bias_results_empty_metrics_list(self, sample_protected_attribute):
        """Test BiasResults with empty metrics list"""
        data = {
            "biasDetected": False,
            "protectedAttribute": [sample_protected_attribute],
            "metrics": []
        }
        results = BiasResults(**data)
        assert len(results.metrics) == 0


class TestModelSerialization:
    """Test suite for model serialization and deserialization"""
    
    def test_protected_attribute_to_dict(self, sample_protected_attribute):
        """Test ProtetedAttribute serialization to dict"""
        attr = ProtetedAttribute(**sample_protected_attribute)
        attr_dict = attr.model_dump()
        assert attr_dict['name'] == "race"
        assert 'privileged' in attr_dict
        assert 'unprivileged' in attr_dict
    
    def test_batch_id_to_dict(self):
        """Test BatchId serialization to dict"""
        batch = BatchId(Batch_id=456.78)
        batch_dict = batch.model_dump()
        assert batch_dict['Batch_id'] == 456.78
    
    def test_metrics_entity_to_dict(self, sample_metrics_entity):
        """Test metricsEntity serialization to dict"""
        metric = metricsEntity(**sample_metrics_entity)
        metric_dict = metric.model_dump()
        assert 'name' in metric_dict
        assert 'description' in metric_dict
        assert 'value' in metric_dict


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
