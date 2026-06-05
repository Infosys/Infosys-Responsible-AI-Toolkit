'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

"""
test_mappers.py - Tests for mappers module (mappers.py)
"""

import sys
import os
import pytest
from unittest.mock import Mock, MagicMock, patch
from pydantic import ValidationError
from explain.mappers.mappers import *
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestEnums:
    """Tests for Enum classes"""

    def test_dataset_type_enum_csv(self):
        """Test DatasetType enum CSV value"""
         
        
        assert DatasetType.csv == 'text/csv'
        assert DatasetType.csv.value == 'text/csv'

    def test_dataset_type_enum_parquet(self):
        """Test DatasetType enum Parquet value"""
         
        
        assert DatasetType.parquet == 'text/parquet'
        assert DatasetType.parquet.value == 'text/parquet'

    def test_task_type_enum_classification(self):
        """Test TaskType enum CLASSIFICATION value"""
         
        
        assert TaskType.CLASSIFICATION == 'CLASSIFICATION'
        assert TaskType.CLASSIFICATION.value == 'CLASSIFICATION'

    def test_task_type_enum_regression(self):
        """Test TaskType enum REGRESSION value"""
         
        
        assert TaskType.REGRESSION == 'REGRESSION'
        assert TaskType.REGRESSION.value == 'REGRESSION'

    def test_task_type_enum_timeseriesforecast(self):
        """Test TaskType enum TIMESERIESFORECAST value"""
         
        
        assert TaskType.TIMESERIESFORECAST == 'TIMESERIESFORECAST'
        assert TaskType.TIMESERIESFORECAST.value == 'TIMESERIESFORECAST'

    def test_scope_enum_global(self):
        """Test Scope enum GLOBAL value"""
         
        
        assert Scope.GLOBAL == 'GLOBAL'
        assert Scope.GLOBAL.value == 'GLOBAL'

    def test_scope_enum_local(self):
        """Test Scope enum LOCAL value"""
         
        
        assert Scope.LOCAL == 'LOCAL'
        assert Scope.LOCAL.value == 'LOCAL'

    def test_status_enum_success(self):
        """Test Status enum SUCCESS value"""
         
        
        assert Status.SUCCESS == 'SUCCESS'
        assert Status.SUCCESS.value == 'SUCCESS'

    def test_status_enum_failure(self):
        """Test Status enum FAILURE value"""
         
        
        assert Status.FAILURE == 'FAILURE'
        assert Status.FAILURE.value == 'FAILURE'


class TestGetExplanationMethodsRequest:
    """Tests for GetExplanationMethodsRequest model"""

    def test_valid_request(self):
        """Test creating valid GetExplanationMethodsRequest"""
         
        
        request = GetExplanationMethodsRequest(
            modelId=11.0,
            datasetId=12.0,
            scope="LOCAL"
        )
        
        assert request.modelId == 11.0
        assert request.datasetId == 12.0
        assert request.scope == "LOCAL"

    def test_request_without_scope(self):
        """Test request without scope (optional)"""
        
        
        request = GetExplanationMethodsRequest(
            modelId=11.0,
            datasetId=12.0
        )
        
        assert request.modelId == 11.0
        assert request.datasetId == 12.0
        assert request.scope is None

    def test_request_with_global_scope(self):
        """Test request with GLOBAL scope"""
        
        
        request = GetExplanationMethodsRequest(
            modelId=1.0,
            datasetId=2.0,
            scope="GLOBAL"
        )
        
        assert request.scope == "GLOBAL"

    def test_request_model_dict(self):
        """Test dict method"""
        
        
        request = GetExplanationMethodsRequest(
            modelId=11.0,
            datasetId=12.0,
            scope="LOCAL"
        )
        
        # Use dict() method which is available in both pydantic v1 and v2
        data = request.dict() if hasattr(request, 'dict') else request.model_dump()
        assert data['modelId'] == 11.0
        assert data['datasetId'] == 12.0


class TestGetExplanationMethodsResponse:
    """Tests for GetExplanationMethodsResponse model"""

    def test_valid_response_success(self):
        """Test creating valid success response"""
        
        
        response = GetExplanationMethodsResponse(
            status='SUCCESS',
            message='Identification of explanation methods successful',
            dataType='Tabular',
            methods=['LIME-TABULAR', 'KERNEL-SHAP']
        )
        
        assert response.status == 'SUCCESS'
        assert response.message == 'Identification of explanation methods successful'
        assert response.dataType == 'Tabular'
        assert len(response.methods) == 2

    def test_valid_response_failure(self):
        """Test creating valid failure response"""
        
        response = GetExplanationMethodsResponse(
            status='FAILURE',
            message='No explanation methods found',
            dataType='',
            methods=[]
        )
        
        assert response.status == 'FAILURE'
        assert len(response.methods) == 0

    def test_response_with_many_methods(self):
        """Test response with multiple methods"""
        
        
        methods = ['LIME-TABULAR', 'KERNEL-SHAP', 'TREE-SHAP', 'ANCHOR-TABULAR', 'INTEGRATED-GRADIENTS']
        response = GetExplanationMethodsResponse(
            status='SUCCESS',
            message='Success',
            dataType='Tabular',
            methods=methods
        )
        
        assert len(response.methods) == 5


class TestGetExplanationRequest:
    """Tests for GetExplanationRequest model"""

    def test_valid_request_with_input_row(self):
        """Test creating request with input row"""
        
        
        request = GetExplanationRequest(
            modelId=11.01,
            datasetId=12.02,
            scope="LOCAL",
            method="LIME-TABULAR",
            inputRow={'feature1': 0.5, 'feature2': 0.3}
        )
        
        assert request.modelId == 11.01
        assert request.datasetId == 12.02
        assert request.scope == "LOCAL"
        assert request.method == "LIME-TABULAR"
        assert request.inputRow == {'feature1': 0.5, 'feature2': 0.3}

    def test_valid_request_with_input_text(self):
        """Test creating request with input text"""
        
        
        request = GetExplanationRequest(
            modelId=11.0,
            datasetId=12.0,
            scope="LOCAL",
            method="TEXT-SHAP",
            inputText="This movie was fantastic!"
        )
        
        assert request.inputText == "This movie was fantastic!"

    def test_request_with_preprocessor_id(self):
        """Test request with preprocessor ID"""
        
        
        request = GetExplanationRequest(
            modelId=11.0,
            datasetId=12.0,
            preprocessorId=13.03,
            scope="LOCAL",
            method="LIME-TABULAR"
        )
        
        assert request.preprocessorId == 13.03

    def test_request_without_optional_fields(self):
        """Test request without optional fields"""
        
        
        request = GetExplanationRequest(
            modelId=11.0,
            datasetId=12.0,
            scope="GLOBAL",
            method="KERNEL-SHAP"
        )
        
        assert request.inputText is None
        assert request.inputRow is None
        assert request.preprocessorId is None


class TestExplainabilityTabular:
    """Tests for ExplainabilityTabular model"""

    def test_valid_tabular_model(self):
        """Test creating valid ExplainabilityTabular"""
        
        
        tabular = ExplainabilityTabular(
            modelPrediction="Class_GOOD",
            importantFeatures=[{'feature': 'age', 'importance': 0.8}],
            description="Test description"
        )
        
        assert tabular.modelPrediction == "Class_GOOD"

    def test_tabular_with_anchor(self):
        """Test ExplainabilityTabular with anchor explanation"""
        
        
        tabular = ExplainabilityTabular(
            anchor=["age > 30", "income > 50000"]
        )
        
        assert len(tabular.anchor) == 2

    def test_tabular_with_shap_values(self):
        """Test ExplainabilityTabular with SHAP values"""
        
        
        tabular = ExplainabilityTabular(
            shapValues=[0.5, -0.3, 0.2]
        )
        
        assert len(tabular.shapValues) == 3


class TestExplainabilityTabular1:
    """Tests for ExplainabilityTabular_1 model"""

    def test_valid_model(self):
        """Test creating valid ExplainabilityTabular_1"""
       
        
        tabular = ExplainabilityTabular_1(
            inputText="Test input",
            modelPrediction="Normal",
            explanation=[{'feature': 'x', 'value': 0.5}]
        )
        
        assert tabular.inputText == "Test input"
        assert tabular.modelPrediction == "Normal"

    def test_model_with_input_row(self):
        """Test model with input row"""
        
        
        tabular = ExplainabilityTabular_1(
            inputRow=[{'featureName': 'age', 'featureValue': 30}],
            modelPrediction="Class_A"
        )
        
        assert len(tabular.inputRow) == 1

    def test_model_with_time_series(self):
        """Test model with time series"""
        
        
        tabular = ExplainabilityTabular_1(
            timeSeries="base64_encoded_image"
        )
        
        assert tabular.timeSeries == "base64_encoded_image"


class TestExplainabilityTabularNew:
    """Tests for ExplainabilityTabular_New model"""

    def test_valid_new_model(self):
        """Test creating valid ExplainabilityTabular_New"""
        
        
        tabular = ExplainabilityTabular_New(
            modelName="BMI Classification Model",
            algorithm="Random Forest",
            taskType="CLASSIFICATION",
            datasetName="BMI Dataset",
            dataType="Tabular",
            methodName="LIME-TABULAR",
            methodDescription="LIME explanation"
        )
        
        assert tabular.modelName == "BMI Classification Model"
        assert tabular.algorithm == "Random Forest"
        assert tabular.taskType == "CLASSIFICATION"

    def test_model_with_feature_names(self):
        """Test model with feature names"""
        
        
        tabular = ExplainabilityTabular_New(
            modelName="Test Model",
            algorithm="XGBoost",
            taskType="REGRESSION",
            datasetName="Test Dataset",
            dataType="Tabular",
            methodName="SHAP",
            methodDescription="SHAP description",
            featureNames=["Age", "Weight", "Height"]
        )
        
        assert len(tabular.featureNames) == 3

    def test_model_with_ground_truth(self):
        """Test model with ground truth details"""
        
        
        tabular = ExplainabilityTabular_New(
            modelName="Test",
            algorithm="SVM",
            taskType="CLASSIFICATION",
            datasetName="Test",
            dataType="Tabular",
            methodName="LIME",
            methodDescription="Test",
            groundTruthLabel="Index",
            groundTruthClassNames=["Underweight", "Normal", "Overweight"]
        )
        
        assert tabular.groundTruthLabel == "Index"
        assert len(tabular.groundTruthClassNames) == 3


class TestGetExplanationResponse:
    """Tests for GetExplanationResponse model"""

    def test_valid_response(self):
        """Test creating valid GetExplanationResponse"""
         
        
        explanation = ExplainabilityTabular_New(
            modelName="Test",
            algorithm="RF",
            taskType="CLASSIFICATION",
            datasetName="Test",
            dataType="Tabular",
            methodName="LIME",
            methodDescription="Test"
        )
        
        response = GetExplanationResponse(
            status='SUCCESS',
            message='Explanation generated',
            explanation=[explanation]
        )
        
        assert response.status == 'SUCCESS'
        assert len(response.explanation) == 1

    def test_failure_response(self):
        """Test creating failure response"""
         
        
        response = GetExplanationResponse(
            status='FAILURE',
            message='Error generating explanation',
            explanation=[]
        )
        
        assert response.status == 'FAILURE'
        assert len(response.explanation) == 0


class TestGetReportRequest:
    """Tests for GetReportRequest model"""

    def test_valid_request(self):
        """Test creating valid GetReportRequest"""
        
        
        request = GetReportRequest(batchId=123.0)
        
        assert request.batchId == 123.0

    def test_request_with_float(self):
        """Test request with float batch ID"""
        
        
        request = GetReportRequest(batchId=456.78)
        
        assert request.batchId == 456.78


class TestGetReportResponse:
    """Tests for GetReportResponse model"""

    def test_valid_success_response(self):
        """Test creating valid success response"""
        
        
        response = GetReportResponse(
            status='SUCCESS',
            message='Report generated successfully'
        )
        
        assert response.status == 'SUCCESS'
        assert response.message == 'Report generated successfully'

    def test_valid_failure_response(self):
        """Test creating valid failure response"""
        
        
        response = GetReportResponse(
            status='FAILURE',
            message='Error generating report'
        )
        
        assert response.status == 'FAILURE'


class TestMapperIntegration:
    """Integration tests for mappers"""

    def test_request_response_flow(self):
        """Test typical request-response flow"""
        
        
        # Create request
        request = GetExplanationMethodsRequest(
            modelId=1.0,
            datasetId=2.0,
            scope="LOCAL"
        )
        
        # Create response
        response = GetExplanationMethodsResponse(
            status='SUCCESS',
            message='Methods found',
            dataType='Tabular',
            methods=['LIME', 'SHAP']
        )
        
        assert request.modelId == 1.0
        assert response.status == 'SUCCESS'

    def test_model_serialization(self):
        """Test model serialization"""
        
        
        request = GetExplanationMethodsRequest(
            modelId=1.0,
            datasetId=2.0,
            scope="LOCAL"
        )
        
        # Serialize to dict (compatible with both pydantic v1 and v2)
        data = request.dict() if hasattr(request, 'dict') else request.model_dump()
        
        # Recreate from dict
        recreated = GetExplanationMethodsRequest(**data)
        
        assert recreated.modelId == request.modelId
        assert recreated.datasetId == request.datasetId

    def test_all_status_values(self):
        """Test all Status enum values work in responses"""
        
        
        for status in Status:
            response = GetExplanationMethodsResponse(
                status=status,
                message=f'Test {status.value}',
                dataType='Tabular',
                methods=[]
            )
            assert response.status == status.value

    def test_all_scope_values(self):
        """Test all Scope enum values work in requests"""
        
        
        for scope in Scope:
            request = GetExplanationMethodsRequest(
                modelId=1.0,
                datasetId=2.0,
                scope=scope
            )
            assert request.scope == scope.value
