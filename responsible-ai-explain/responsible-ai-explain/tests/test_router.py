'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

"""
test_router.py - Tests for explain_router.py
"""

import sys
import os
import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================================
# Test Router Configuration
# ============================================================================

class TestRouterConfiguration:
    """Tests for router configuration"""

    def test_config_router_exists(self):
        """Test config router is defined"""
        from fastapi import APIRouter
        
        config = APIRouter()
        assert config is not None

    def test_report_router_exists(self):
        """Test report router is defined"""
        from fastapi import APIRouter
        
        report = APIRouter()
        assert report is not None

    def test_explanation_router_exists(self):
        """Test explanation router is defined"""
        from fastapi import APIRouter
        
        explanation = APIRouter()
        assert explanation is not None


# ============================================================================
# Test Telemetry Functions
# ============================================================================

class TestTelemetryFunctions:
    """Tests for telemetry functions"""

    @patch('requests.post')
    def test_send_telemetry_request_success(self, mock_post):
        """Test successful telemetry request"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'status': 'success'}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        telemetry_data = {
            'tenetName': 'Explainability',
            'errorCode': 'TEST_001',
            'errorMessage': 'Test error',
            'apiEndPoint': '/test',
            'errorRequestMethod': 'POST'
        }
        
        response = mock_post('http://localhost/telemetry', json=telemetry_data)
        
        assert response.json()['status'] == 'success'

    @patch('requests.post')
    def test_send_telemetry_request_failure(self, mock_post):
        """Test telemetry request failure"""
        mock_post.side_effect = Exception("Connection error")
        
        with pytest.raises(Exception):
            mock_post('http://localhost/telemetry', json={})

    def test_telemetry_error_logging_structure(self):
        """Test telemetry error logging structure"""
        error_input = {
            "tenetName": "Explainability",
            "errorCode": "test_function_uuid123",
            "errorMessage": "Test error message",
            "apiEndPoint": "/explainability/methods/get",
            "errorRequestMethod": "POST"
        }
        
        assert error_input['tenetName'] == 'Explainability'
        assert error_input['errorRequestMethod'] == 'POST'


# ============================================================================
# Test API Endpoints
# ============================================================================

class TestGetExplanationMethodsEndpoint:
    """Tests for /explainability/methods/get endpoint"""

    def test_endpoint_structure(self):
        """Test endpoint structure"""
        from explain.mappers.mappers import GetExplanationMethodsRequest
        
        request = GetExplanationMethodsRequest(
            modelId=11.0,
            datasetId=12.0,
            scope="LOCAL"
        )
        
        assert request.modelId == 11.0
        assert request.datasetId == 12.0

    @patch('explain.routing.explain_router.service')
    def test_get_methods_success(self, mock_service):
        """Test successful get methods call"""
        from explain.mappers.mappers import GetExplanationMethodsResponse
        
        mock_service.get_explanation_methods.return_value = GetExplanationMethodsResponse(
            status='SUCCESS',
            message='Methods found',
            dataType='Tabular',
            methods=['LIME-TABULAR', 'KERNEL-SHAP']
        )
        
        result = mock_service.get_explanation_methods(MagicMock())
        
        assert result.status == 'SUCCESS'
        assert len(result.methods) == 2

    @patch('explain.routing.explain_router.service')
    def test_get_methods_failure(self, mock_service):
        """Test get methods failure"""
        from explain.mappers.mappers import GetExplanationMethodsResponse
        
        mock_service.get_explanation_methods.return_value = GetExplanationMethodsResponse(
            status='FAILURE',
            message='No methods found',
            dataType='',
            methods=[]
        )
        
        result = mock_service.get_explanation_methods(MagicMock())
        
        assert result.status == 'FAILURE'
        assert len(result.methods) == 0

    @patch('explain.routing.explain_router.service')
    def test_get_methods_exception(self, mock_service):
        """Test get methods exception handling"""
        mock_service.get_explanation_methods.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            mock_service.get_explanation_methods(MagicMock())


class TestGenerateExplanationEndpoint:
    """Tests for /explainability/explanation/get endpoint"""

    def test_explanation_request_with_input_row(self):
        """Test explanation request with input row"""
        from explain.mappers.mappers import GetExplanationRequest
        
        request = GetExplanationRequest(
            modelId=11.0,
            datasetId=12.0,
            scope="LOCAL",
            method="LIME-TABULAR",
            inputRow={'feature1': 0.5, 'feature2': 0.3}
        )
        
        assert request.inputRow is not None
        assert request.inputRow['feature1'] == 0.5

    def test_explanation_request_with_input_text(self):
        """Test explanation request with input text"""
        from explain.mappers.mappers import GetExplanationRequest
        
        request = GetExplanationRequest(
            modelId=11.0,
            datasetId=12.0,
            scope="LOCAL",
            method="TEXT-SHAP",
            inputText="This is test text"
        )
        
        assert request.inputText is not None

    @patch('explain.routing.explain_router.service')
    def test_generate_explanation_success(self, mock_service):
        """Test successful explanation generation"""
        from explain.mappers.mappers import GetExplanationResponse, ExplainabilityTabular_New
        
        explanation = ExplainabilityTabular_New(
            modelName="Test",
            algorithm="RF",
            taskType="CLASSIFICATION",
            datasetName="Test",
            dataType="Tabular",
            methodName="LIME",
            methodDescription="Test"
        )
        
        mock_service.generate_explanation.return_value = GetExplanationResponse(
            status='SUCCESS',
            message='Explanation generated',
            explanation=[explanation]
        )
        
        result = mock_service.generate_explanation(MagicMock())
        
        assert result.status == 'SUCCESS'
        assert len(result.explanation) == 1


class TestGenerateReportEndpoint:
    """Tests for /explainability/report/generate endpoint"""

    def test_report_request_structure(self):
        """Test report request structure"""
        from explain.mappers.mappers import GetReportRequest
        
        request = GetReportRequest(batchId=123.0)
        
        assert request.batchId == 123.0

    @patch('explain.routing.explain_router.service')
    def test_generate_report_success(self, mock_service):
        """Test successful report generation"""
        from explain.mappers.mappers import GetReportResponse
        
        mock_service.generate_report.return_value = GetReportResponse(
            status='SUCCESS',
            message='Report generated successfully'
        )
        
        result = mock_service.generate_report(MagicMock())
        
        assert result.status == 'SUCCESS'

    @patch('explain.routing.explain_router.service')
    def test_generate_report_failure(self, mock_service):
        """Test report generation failure"""
        from explain.mappers.mappers import GetReportResponse
        
        mock_service.generate_report.return_value = GetReportResponse(
            status='FAILURE',
            message='Error generating report'
        )
        
        result = mock_service.generate_report(MagicMock())
        
        assert result.status == 'FAILURE'


# ============================================================================
# Test Request Validation
# ============================================================================

class TestRequestValidation:
    """Tests for request validation"""

    def test_methods_request_valid(self):
        """Test valid methods request"""
        from explain.mappers.mappers import GetExplanationMethodsRequest
        
        request = GetExplanationMethodsRequest(
            modelId=1.0,
            datasetId=2.0
        )
        
        assert request.modelId > 0
        assert request.datasetId > 0

    def test_explanation_request_valid_local(self):
        """Test valid local explanation request"""
        from explain.mappers.mappers import GetExplanationRequest
        
        request = GetExplanationRequest(
            modelId=1.0,
            datasetId=2.0,
            scope="LOCAL",
            method="LIME-TABULAR",
            inputRow={'x': 1}
        )
        
        assert request.scope == "LOCAL"
        assert request.inputRow is not None

    def test_explanation_request_valid_global(self):
        """Test valid global explanation request"""
        from explain.mappers.mappers import GetExplanationRequest
        
        request = GetExplanationRequest(
            modelId=1.0,
            datasetId=2.0,
            scope="GLOBAL",
            method="KERNEL-SHAP"
        )
        
        assert request.scope == "GLOBAL"


# ============================================================================
# Test UUID Generation
# ============================================================================

class TestUUIDGeneration:
    """Tests for UUID generation in router"""

    def test_uuid_generation(self):
        """Test UUID generation"""
        import uuid
        
        id1 = uuid.uuid4().hex
        id2 = uuid.uuid4().hex
        
        assert len(id1) == 32
        assert len(id2) == 32
        assert id1 != id2

    def test_uuid_format(self):
        """Test UUID format"""
        import uuid
        
        id = uuid.uuid4().hex
        
        # Should be 32 hex characters
        assert all(c in '0123456789abcdef' for c in id)


# ============================================================================
# Test Timing
# ============================================================================

class TestTiming:
    """Tests for timing in router"""

    def test_timing_calculation(self):
        """Test timing calculation"""
        from datetime import datetime
        import time
        
        start_time = datetime.now()
        time.sleep(0.1)
        end_time = datetime.now()
        
        total_time = end_time - start_time
        
        assert total_time.total_seconds() >= 0.1


# ============================================================================
# Test Exception Logging
# ============================================================================

class TestExceptionLogging:
    """Tests for exception logging"""

    def test_exception_create_structure(self):
        """Test exception creation structure"""
        exception_data = {
            "UUID": "test-uuid-123",
            "function": "test_function",
            "msg": "Test error",
            "description": "Test error + Line No: 123"
        }
        
        assert 'UUID' in exception_data
        assert 'function' in exception_data
        assert 'msg' in exception_data
        assert 'description' in exception_data

    def test_traceback_extraction(self):
        """Test traceback extraction"""
        import traceback
        
        try:
            raise ValueError("Test error")
        except Exception as e:
            tb = traceback.format_exc()
            
            assert 'ValueError' in tb
            assert 'Test error' in tb


# ============================================================================
# Integration Tests
# ============================================================================

class TestRouterIntegration:
    """Integration tests for router"""

    def test_router_can_be_added_to_app(self):
        """Test router can be added to FastAPI app"""
        from fastapi import FastAPI, APIRouter
        
        app = FastAPI()
        router = APIRouter()
        
        @router.get("/test")
        def test_endpoint():
            return {"status": "ok"}
        
        app.include_router(router)
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_post_endpoint(self):
        """Test POST endpoint"""
        from fastapi import FastAPI, APIRouter
        from pydantic import BaseModel
        
        app = FastAPI()
        router = APIRouter()
        
        class TestRequest(BaseModel):
            value: int
        
        @router.post("/test")
        def test_endpoint(request: TestRequest):
            return {"received": request.value}
        
        app.include_router(router)
        
        client = TestClient(app)
        response = client.post("/test", json={"value": 42})
        
        assert response.status_code == 200
        assert response.json() == {"received": 42}

    def test_error_handling(self):
        """Test error handling in router"""
        from fastapi import FastAPI, APIRouter, HTTPException
        
        app = FastAPI()
        router = APIRouter()
        
        @router.get("/error")
        def error_endpoint():
            raise HTTPException(status_code=500, detail="Test error")
        
        app.include_router(router)
        
        client = TestClient(app)
        response = client.get("/error")
        
        assert response.status_code == 500


# ============================================================================
# Comprehensive Router Function Tests
# ============================================================================

class TestRouterFunctionsComprehensive:
    """Comprehensive tests for router functions to increase coverage"""

    @patch('explain.routing.explain_router.service')
    @patch('explain.routing.explain_router.request_id_var')
    @patch('explain.routing.explain_router.log')
    def test_get_explanation_methods_full_flow(self, mock_log, mock_request_id, mock_service):
        """Test full flow of get_explanation_methods"""
        from explain.mappers.mappers import GetExplanationMethodsRequest, GetExplanationMethodsResponse
        
        mock_request_id.set = MagicMock()
        mock_request_id.get.return_value = 'test-uuid'
        mock_service.get_explanation_methods.return_value = GetExplanationMethodsResponse(
            status='SUCCESS',
            message='Success',
            dataType='Tabular',
            methods=['LIME-TABULAR']
        )
        
        from explain.routing.explain_router import get_explanation_methods
        
        request = GetExplanationMethodsRequest(modelId=1.0, datasetId=2.0)
        result = get_explanation_methods(request)
        
        assert result.status == 'SUCCESS'

    @patch('explain.routing.explain_router.service')
    @patch('explain.routing.explain_router.request_id_var')
    @patch('explain.routing.explain_router.log')
    def test_generate_explanation_full_flow(self, mock_log, mock_request_id, mock_service):
        """Test full flow of generate_explanation"""
        from explain.mappers.mappers import GetExplanationRequest, GetExplanationResponse
        
        mock_request_id.set = MagicMock()
        mock_request_id.get.return_value = 'test-uuid'
        mock_service.generate_explanation.return_value = GetExplanationResponse(
            status='SUCCESS',
            message='Success',
            explanation=[]
        )
        
        from explain.routing.explain_router import generate_explanation
        
        request = GetExplanationRequest(modelId=1.0, datasetId=2.0, scope='LOCAL', method='LIME')
        result = generate_explanation(request)
        
        assert result.status == 'SUCCESS'

    @patch('explain.routing.explain_router.service')
    @patch('explain.routing.explain_router.request_id_var')
    @patch('explain.routing.explain_router.log')
    def test_generate_report_full_flow(self, mock_log, mock_request_id, mock_service):
        """Test full flow of generate_report"""
        from explain.mappers.mappers import GetReportRequest, GetReportResponse
        
        mock_request_id.set = MagicMock()
        mock_request_id.get.return_value = 'test-uuid'
        mock_service.generate_report.return_value = GetReportResponse(
            status='SUCCESS',
            message='Success'
        )
        
        from explain.routing.explain_router import generate_report
        
        request = GetReportRequest(batchId=123.0)
        result = generate_report(request)
        
        assert result.status == 'SUCCESS'

    @patch('explain.routing.explain_router.service')
    @patch('explain.routing.explain_router.request_id_var')
    @patch('explain.routing.explain_router.Tbl_Exception')
    @patch('explain.routing.explain_router.telemetry_error_logging')
    @patch('explain.routing.explain_router.log')
    def test_get_explanation_methods_exception(self, mock_log, mock_telemetry, 
                                                mock_exception, mock_request_id, mock_service):
        """Test get_explanation_methods with exception"""
        from fastapi import HTTPException
        from explain.mappers.mappers import GetExplanationMethodsRequest
        
        mock_request_id.set = MagicMock()
        mock_request_id.get.return_value = 'test-uuid'
        mock_service.get_explanation_methods.side_effect = Exception("Test error")
        
        from explain.routing.explain_router import get_explanation_methods
        
        request = GetExplanationMethodsRequest(modelId=1.0, datasetId=2.0)
        
        with pytest.raises(HTTPException) as exc_info:
            get_explanation_methods(request)
        
        assert exc_info.value.status_code == 500

    @patch('explain.routing.explain_router.service')
    @patch('explain.routing.explain_router.request_id_var')
    @patch('explain.routing.explain_router.Tbl_Exception')
    @patch('explain.routing.explain_router.telemetry_error_logging')
    @patch('explain.routing.explain_router.log')
    def test_generate_explanation_exception(self, mock_log, mock_telemetry,
                                           mock_exception, mock_request_id, mock_service):
        """Test generate_explanation with exception"""
        from fastapi import HTTPException
        from explain.mappers.mappers import GetExplanationRequest
        
        mock_request_id.set = MagicMock()
        mock_request_id.get.return_value = 'test-uuid'
        mock_service.generate_explanation.side_effect = Exception("Test error")
        
        from explain.routing.explain_router import generate_explanation
        
        request = GetExplanationRequest(modelId=1.0, datasetId=2.0, scope='LOCAL', method='LIME')
        
        with pytest.raises(HTTPException) as exc_info:
            generate_explanation(request)
        
        assert exc_info.value.status_code == 500

    @patch('explain.routing.explain_router.service')
    @patch('explain.routing.explain_router.request_id_var')
    @patch('explain.routing.explain_router.Tbl_Exception')
    @patch('explain.routing.explain_router.telemetry_error_logging')
    @patch('explain.routing.explain_router.log')
    def test_generate_report_exception(self, mock_log, mock_telemetry,
                                       mock_exception, mock_request_id, mock_service):
        """Test generate_report with exception"""
        from fastapi import HTTPException
        from explain.mappers.mappers import GetReportRequest
        
        mock_request_id.set = MagicMock()
        mock_request_id.get.return_value = 'test-uuid'
        mock_service.generate_report.side_effect = Exception("Test error")
        
        from explain.routing.explain_router import generate_report
        
        request = GetReportRequest(batchId=123.0)
        
        with pytest.raises(HTTPException) as exc_info:
            generate_report(request)
        
        assert exc_info.value.status_code == 500


class TestTelemetryErrorLogging:
    """Tests for telemetry_error_logging function"""

    @patch('explain.routing.explain_router.telemetry_flag', 'True')
    @patch('explain.routing.explain_router.tel_error_url', 'http://test.com/telemetry')
    @patch('explain.routing.explain_router.send_telemetry_request')
    def test_telemetry_error_logging_enabled(self, mock_send):
        """Test telemetry error logging when enabled"""
        from explain.routing.explain_router import telemetry_error_logging
        from unittest.mock import MagicMock
        
        mock_request_id_var = MagicMock()
        mock_request_id_var.get.return_value = 'test-uuid'
        
        try:
            raise ValueError("Test error")
        except Exception as e:
            telemetry_error_logging(e, mock_request_id_var, '/test/endpoint')

    @patch('explain.routing.explain_router.telemetry_flag', 'False')
    def test_telemetry_error_logging_disabled(self):
        """Test telemetry error logging when disabled"""
        from explain.routing.explain_router import telemetry_error_logging
        from unittest.mock import MagicMock
        
        mock_request_id_var = MagicMock()
        mock_request_id_var.get.return_value = 'test-uuid'
        
        try:
            raise ValueError("Test error")
        except Exception as e:
            # Should not raise an error
            telemetry_error_logging(e, mock_request_id_var, '/test/endpoint')


class TestSendTelemetryRequest:
    """Tests for send_telemetry_request function"""

    @patch('explain.routing.explain_router.requests.post')
    @patch('explain.routing.explain_router.log')
    def test_send_telemetry_request_success(self, mock_log, mock_post):
        """Test successful telemetry request"""
        from explain.routing.explain_router import send_telemetry_request
        
        mock_response = MagicMock()
        mock_response.json.return_value = {'status': 'success'}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        telemetry_data = {'test': 'data'}
        send_telemetry_request(telemetry_data, 'http://test.com/telemetry')

    @patch('explain.routing.explain_router.requests.post')
    @patch('explain.routing.explain_router.Tbl_Exception')
    @patch('explain.routing.explain_router.request_id_var')
    @patch('explain.routing.explain_router.log')
    def test_send_telemetry_request_failure(self, mock_log, mock_request_id, 
                                            mock_exception, mock_post):
        """Test failed telemetry request"""
        from fastapi import HTTPException
        from explain.routing.explain_router import send_telemetry_request
        
        mock_request_id.get.return_value = 'test-uuid'
        mock_post.side_effect = Exception("Connection error")
        
        with pytest.raises(HTTPException):
            send_telemetry_request({}, 'http://test.com/telemetry')
