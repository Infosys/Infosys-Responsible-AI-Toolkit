import sys
import os
import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime
from fastapi import HTTPException
from fastapi.testclient import TestClient

# Add src to path for imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.routing.routers import report, html_to_pdf_conversion, convert_to_pdf_report, download_report


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def client():
    """Create a test client for the FastAPI router"""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(report)
    return TestClient(app)


@pytest.fixture
def mock_logger():
    """Mock the logger"""
    with patch('app.routing.routers.log') as mock_log:
        yield mock_log


@pytest.fixture
def mock_gc():
    """Mock garbage collector"""
    with patch('app.routing.routers.gc') as mock_garbage_collector:
        yield mock_garbage_collector


@pytest.fixture
def mock_datetime():
    """Mock datetime"""
    with patch('app.routing.routers.datetime') as mock_dt:
        # Create a fixed datetime for testing
        fixed_datetime = datetime(2024, 1, 15, 10, 30, 0)
        mock_dt.now.return_value = fixed_datetime
        yield mock_dt


# ============================================================================
# Test html_to_pdf_conversion Endpoint
# ============================================================================

class TestHtmlToPdfConversion:
    """Test html_to_pdf_conversion endpoint"""
    
    def test_html_to_pdf_conversion_success(self, client, mock_logger, mock_gc):
        """Test successful HTML to PDF conversion"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.html_to_pdf_conversion.return_value = {
                "status": "SUCCESS",
                "message": "PDF conversion completed",
                "reportId": "report_123"
            }
            
            response = client.post(
                "/v1/report/htmltopdfconversion",
                data={"batchId": 1.1}
            )
            
            assert response.status_code == 200
            assert response.json()["status"] == "SUCCESS"
            assert response.json()["reportId"] == "report_123"
            mock_rai.html_to_pdf_conversion.assert_called_once_with({'batchId': 1.1})
            mock_gc.collect.assert_called_once()
    
    def test_html_to_pdf_conversion_with_float_batch_id(self, client, mock_logger):
        """Test with decimal batch ID"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.html_to_pdf_conversion.return_value = {
                "status": "SUCCESS",
                "message": "Conversion successful"
            }
            
            response = client.post(
                "/v1/report/htmltopdfconversion",
                data={"batchId": 2.5}
            )
            
            assert response.status_code == 200
            mock_rai.html_to_pdf_conversion.assert_called_once_with({'batchId': 2.5})
    
    def test_html_to_pdf_conversion_with_integer_batch_id(self, client, mock_logger):
        """Test with integer batch ID"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.html_to_pdf_conversion.return_value = {
                "status": "SUCCESS"
            }
            
            response = client.post(
                "/v1/report/htmltopdfconversion",
                data={"batchId": 5}
            )
            
            assert response.status_code == 200
            mock_rai.html_to_pdf_conversion.assert_called_once()
    
    def test_html_to_pdf_conversion_logging(self, client, mock_logger):
        """Test that logging occurs during conversion"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.html_to_pdf_conversion.return_value = {"status": "SUCCESS"}
            
            response = client.post(
                "/v1/report/htmltopdfconversion",
                data={"batchId": 1.1}
            )
            
            assert response.status_code == 200
            # Verify logging calls
            assert mock_logger.info.called
            assert mock_logger.debug.called
    
    def test_html_to_pdf_conversion_exception_handling(self, client, mock_logger):
        """Test exception handling in HTML to PDF conversion"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            # Create exception with __dict__ attribute
            exc = HTTPException(status_code=500, detail="Internal Server Error")
            mock_rai.html_to_pdf_conversion.side_effect = exc
            
            response = client.post(
                "/v1/report/htmltopdfconversion",
                data={"batchId": 1.1}
            )
            
            assert response.status_code == 500
            mock_logger.error.assert_called_once()
    
    def test_html_to_pdf_conversion_service_failure(self, client, mock_logger):
        """Test when service returns failure status"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.html_to_pdf_conversion.return_value = {
                "status": "FAILURE",
                "message": "Conversion failed"
            }
            
            response = client.post(
                "/v1/report/htmltopdfconversion",
                data={"batchId": 1.1}
            )
            
            assert response.status_code == 200
            assert response.json()["status"] == "FAILURE"
    
    def test_html_to_pdf_conversion_missing_batch_id(self, client):
        """Test with missing batchId parameter"""
        response = client.post("/v1/report/htmltopdfconversion")
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_html_to_pdf_conversion_invalid_batch_id(self, client):
        """Test with invalid batchId parameter"""
        response = client.post(
            "/v1/report/htmltopdfconversion",
            data={"batchId": "invalid"}
        )
        
        assert response.status_code == 422
    
    def test_html_to_pdf_conversion_timing_logs(self, client, mock_logger, mock_datetime):
        """Test that timing information is logged"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.html_to_pdf_conversion.return_value = {"status": "SUCCESS"}
            
            response = client.post(
                "/v1/report/htmltopdfconversion",
                data={"batchId": 1.1}
            )
            
            assert response.status_code == 200
            # Verify that datetime.now() was called for timing
            assert mock_datetime.now.called
    
    def test_html_to_pdf_conversion_gc_collection(self, client, mock_gc):
        """Test that garbage collection is triggered"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.html_to_pdf_conversion.return_value = {"status": "SUCCESS"}
            
            response = client.post(
                "/v1/report/htmltopdfconversion",
                data={"batchId": 1.1}
            )
            
            assert response.status_code == 200
            mock_gc.collect.assert_called_once()


# ============================================================================
# Test convert_to_pdf_report Endpoint
# ============================================================================

class TestConvertToPdfReport:
    """Test convert_to_pdf_report endpoint"""
    
    def test_convert_to_pdf_report_success(self, client, mock_logger, mock_gc):
        """Test successful PDF report conversion"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.combinedReport.return_value = {
                "status": "SUCCESS",
                "message": "Combined report created",
                "ReportId": "combined_123"
            }
            
            response = client.post(
                "/v1/report/converttopdfreport",
                data={"batchId": 2.2}
            )
            
            assert response.status_code == 200
            assert response.json()["status"] == "SUCCESS"
            assert response.json()["ReportId"] == "combined_123"
            # Note: payload key is 'batchid' (lowercase) in this endpoint
            mock_rai.combinedReport.assert_called_once_with({'batchid': 2.2})
            mock_gc.collect.assert_called_once()
    
    def test_convert_to_pdf_report_with_integer_batch_id(self, client, mock_logger):
        """Test with integer batch ID"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.combinedReport.return_value = {
                "status": "SUCCESS"
            }
            
            response = client.post(
                "/v1/report/converttopdfreport",
                data={"batchId": 3}
            )
            
            assert response.status_code == 200
            mock_rai.combinedReport.assert_called_once_with({'batchid': 3.0})
    
    def test_convert_to_pdf_report_with_decimal_batch_id(self, client, mock_logger):
        """Test with decimal batch ID"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.combinedReport.return_value = {
                "status": "SUCCESS"
            }
            
            response = client.post(
                "/v1/report/converttopdfreport",
                data={"batchId": 4.5}
            )
            
            assert response.status_code == 200
            mock_rai.combinedReport.assert_called_once_with({'batchid': 4.5})
    
    def test_convert_to_pdf_report_logging(self, client, mock_logger):
        """Test that logging occurs during conversion"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.combinedReport.return_value = {"status": "SUCCESS"}
            
            response = client.post(
                "/v1/report/converttopdfreport",
                data={"batchId": 2.2}
            )
            
            assert response.status_code == 200
            # Verify logging was called
            mock_logger.info.assert_called()
    
    def test_convert_to_pdf_report_failure(self, client, mock_logger):
        """Test when combined report fails"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.combinedReport.return_value = {
                "status": "FAILURE",
                "message": "Failed to create combined report"
            }
            
            response = client.post(
                "/v1/report/converttopdfreport",
                data={"batchId": 2.2}
            )
            
            assert response.status_code == 200
            assert response.json()["status"] == "FAILURE"
    
    def test_convert_to_pdf_report_missing_batch_id(self, client):
        """Test with missing batchId parameter"""
        response = client.post("/v1/report/converttopdfreport")
        
        assert response.status_code == 422
    
    def test_convert_to_pdf_report_invalid_batch_id(self, client):
        """Test with invalid batchId parameter"""
        response = client.post(
            "/v1/report/converttopdfreport",
            data={"batchId": "not_a_number"}
        )
        
        assert response.status_code == 422
    
    def test_convert_to_pdf_report_gc_collection(self, client, mock_gc):
        """Test that garbage collection is triggered"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.combinedReport.return_value = {"status": "SUCCESS"}
            
            response = client.post(
                "/v1/report/converttopdfreport",
                data={"batchId": 2.2}
            )
            
            assert response.status_code == 200
            mock_gc.collect.assert_called_once()
    
    def test_convert_to_pdf_report_exception_no_dict(self, client, mock_logger):
        """Test exception handling when exception has no __dict__"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            # Simulate an exception without proper __dict__
            mock_rai.combinedReport.side_effect = Exception("Generic error")
            
            # This should raise an exception
            with pytest.raises(Exception):
                response = client.post(
                    "/v1/report/converttopdfreport",
                    data={"batchId": 2.2}
                )
    
    def test_convert_to_pdf_report_response_structure(self, client, mock_logger):
        """Test response structure"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.combinedReport.return_value = {
                "status": "SUCCESS",
                "ReportId": "report_456",
                "message": "Report generated successfully",
                "timestamp": "2024-01-15 10:30:00"
            }
            
            response = client.post(
                "/v1/report/converttopdfreport",
                data={"batchId": 2.2}
            )
            
            assert response.status_code == 200
            json_response = response.json()
            assert "status" in json_response
            assert "ReportId" in json_response
            assert "message" in json_response
            assert "timestamp" in json_response


# ============================================================================
# Test download_report Endpoint
# ============================================================================

class TestDownloadReport:
    """Test download_report endpoint"""
    
    def test_download_report_success(self, client, mock_logger, mock_gc):
        """Test successful report download"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.download_report.return_value = {
                "status": "SUCCESS",
                "message": "Report ready for download",
                "downloadUrl": "https://example.com/report.pdf"
            }
            
            response = client.post(
                "/v1/report/downloadreport",
                data={"batchId": 3.3}
            )
            
            assert response.status_code == 200
            assert response.json()["status"] == "SUCCESS"
            assert "downloadUrl" in response.json()
            mock_rai.download_report.assert_called_once_with({'batchId': 3.3})
            mock_gc.collect.assert_called_once()
    
    def test_download_report_with_integer_batch_id(self, client, mock_logger):
        """Test with integer batch ID"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.download_report.return_value = {
                "status": "SUCCESS"
            }
            
            response = client.post(
                "/v1/report/downloadreport",
                data={"batchId": 7}
            )
            
            assert response.status_code == 200
            mock_rai.download_report.assert_called_once_with({'batchId': 7.0})
    
    def test_download_report_with_decimal_batch_id(self, client, mock_logger):
        """Test with decimal batch ID"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.download_report.return_value = {
                "status": "SUCCESS"
            }
            
            response = client.post(
                "/v1/report/downloadreport",
                data={"batchId": 8.9}
            )
            
            assert response.status_code == 200
            mock_rai.download_report.assert_called_once_with({'batchId': 8.9})
    
    def test_download_report_logging(self, client, mock_logger):
        """Test that logging occurs during download"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.download_report.return_value = {"status": "SUCCESS"}
            
            response = client.post(
                "/v1/report/downloadreport",
                data={"batchId": 3.3}
            )
            
            assert response.status_code == 200
            # Verify logging calls
            assert mock_logger.info.called
            assert mock_logger.debug.called
    
    def test_download_report_exception_handling(self, client, mock_logger):
        """Test exception handling in download report"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            exc = HTTPException(status_code=404, detail="Report not found")
            mock_rai.download_report.side_effect = exc
            
            response = client.post(
                "/v1/report/downloadreport",
                data={"batchId": 3.3}
            )
            
            assert response.status_code == 404
            mock_logger.error.assert_called_once()
    
    def test_download_report_service_failure(self, client, mock_logger):
        """Test when service returns failure status"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.download_report.return_value = {
                "status": "FAILURE",
                "message": "Report not available"
            }
            
            response = client.post(
                "/v1/report/downloadreport",
                data={"batchId": 3.3}
            )
            
            assert response.status_code == 200
            assert response.json()["status"] == "FAILURE"
    
    def test_download_report_missing_batch_id(self, client):
        """Test with missing batchId parameter"""
        response = client.post("/v1/report/downloadreport")
        
        assert response.status_code == 422
    
    def test_download_report_invalid_batch_id(self, client):
        """Test with invalid batchId parameter"""
        response = client.post(
            "/v1/report/downloadreport",
            data={"batchId": "abc"}
        )
        
        assert response.status_code == 422
    
    def test_download_report_timing_logs(self, client, mock_logger, mock_datetime):
        """Test that timing information is logged"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.download_report.return_value = {"status": "SUCCESS"}
            
            response = client.post(
                "/v1/report/downloadreport",
                data={"batchId": 3.3}
            )
            
            assert response.status_code == 200
            # Verify that datetime.now() was called for timing
            assert mock_datetime.now.called
    
    def test_download_report_gc_collection(self, client, mock_gc):
        """Test that garbage collection is triggered"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.download_report.return_value = {"status": "SUCCESS"}
            
            response = client.post(
                "/v1/report/downloadreport",
                data={"batchId": 3.3}
            )
            
            assert response.status_code == 200
            mock_gc.collect.assert_called_once()
    
    def test_download_report_error_logging_on_exception(self, client, mock_logger):
        """Test that error is logged when exception occurs"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            exc = HTTPException(status_code=500, detail="Internal error")
            mock_rai.download_report.side_effect = exc
            
            response = client.post(
                "/v1/report/downloadreport",
                data={"batchId": 3.3}
            )
            
            assert response.status_code == 500
            # Verify error was logged
            mock_logger.error.assert_called_once()
            # Verify exit log was called
            assert any("Exit create usecase routing method" in str(call) 
                      for call in mock_logger.info.call_args_list)


# ============================================================================
# Integration Tests
# ============================================================================

class TestRouterIntegration:
    """Integration tests for router endpoints"""
    
    def test_all_endpoints_require_batch_id(self, client):
        """Test that all endpoints require batchId parameter"""
        endpoints = [
            "/v1/report/htmltopdfconversion",
            "/v1/report/converttopdfreport",
            "/v1/report/downloadreport"
        ]
        
        for endpoint in endpoints:
            response = client.post(endpoint)
            assert response.status_code == 422
    
    def test_all_endpoints_accept_float_batch_id(self, client):
        """Test that all endpoints accept float batchId"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.html_to_pdf_conversion.return_value = {"status": "SUCCESS"}
            mock_rai.combinedReport.return_value = {"status": "SUCCESS"}
            mock_rai.download_report.return_value = {"status": "SUCCESS"}
            
            endpoints = [
                "/v1/report/htmltopdfconversion",
                "/v1/report/converttopdfreport",
                "/v1/report/downloadreport"
            ]
            
            for endpoint in endpoints:
                response = client.post(endpoint, data={"batchId": 1.5})
                assert response.status_code == 200
    
    def test_router_prefix(self, client):
        """Test that all routes have correct prefix"""
        endpoints = [
            "/v1/report/htmltopdfconversion",
            "/v1/report/converttopdfreport",
            "/v1/report/downloadreport"
        ]
        
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.html_to_pdf_conversion.return_value = {"status": "SUCCESS"}
            mock_rai.combinedReport.return_value = {"status": "SUCCESS"}
            mock_rai.download_report.return_value = {"status": "SUCCESS"}
            
            for endpoint in endpoints:
                assert endpoint.startswith("/v1/report/")
                response = client.post(endpoint, data={"batchId": 1.0})
                assert response.status_code == 200
    
    def test_concurrent_requests(self, client):
        """Test handling of multiple concurrent requests"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.html_to_pdf_conversion.return_value = {"status": "SUCCESS"}
            
            responses = []
            for i in range(5):
                response = client.post(
                    "/v1/report/htmltopdfconversion",
                    data={"batchId": float(i)}
                )
                responses.append(response)
            
            for response in responses:
                assert response.status_code == 200
    
    def test_different_batch_ids_same_endpoint(self, client):
        """Test same endpoint with different batch IDs"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.download_report.return_value = {"status": "SUCCESS"}
            
            batch_ids = [1.0, 2.5, 3.7, 10.0, 100.5]
            
            for batch_id in batch_ids:
                response = client.post(
                    "/v1/report/downloadreport",
                    data={"batchId": batch_id}
                )
                assert response.status_code == 200
                mock_rai.download_report.assert_called_with({'batchId': batch_id})


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_very_large_batch_id(self, client):
        """Test with very large batch ID"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.html_to_pdf_conversion.return_value = {"status": "SUCCESS"}
            
            response = client.post(
                "/v1/report/htmltopdfconversion",
                data={"batchId": 999999999.999}
            )
            
            assert response.status_code == 200
    
    def test_very_small_batch_id(self, client):
        """Test with very small batch ID"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.combinedReport.return_value = {"status": "SUCCESS"}
            
            response = client.post(
                "/v1/report/converttopdfreport",
                data={"batchId": 0.001}
            )
            
            assert response.status_code == 200
    
    def test_zero_batch_id(self, client):
        """Test with zero batch ID"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.download_report.return_value = {"status": "SUCCESS"}
            
            response = client.post(
                "/v1/report/downloadreport",
                data={"batchId": 0.0}
            )
            
            assert response.status_code == 200
    
    def test_negative_batch_id(self, client):
        """Test with negative batch ID"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.html_to_pdf_conversion.return_value = {"status": "SUCCESS"}
            
            response = client.post(
                "/v1/report/htmltopdfconversion",
                data={"batchId": -1.5}
            )
            
            assert response.status_code == 200
    
    def test_empty_response_from_service(self, client):
        """Test when service returns empty response"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.combinedReport.return_value = {}
            
            response = client.post(
                "/v1/report/converttopdfreport",
                data={"batchId": 1.0}
            )
            
            assert response.status_code == 200
            assert response.json() == {}
    
    def test_null_response_from_service(self, client):
        """Test when service returns None"""
        with patch('app.routing.routers.InfosysRAI') as mock_rai:
            mock_rai.download_report.return_value = None
            
            response = client.post(
                "/v1/report/downloadreport",
                data={"batchId": 1.0}
            )
            
            assert response.status_code == 200
            assert response.json() is None
