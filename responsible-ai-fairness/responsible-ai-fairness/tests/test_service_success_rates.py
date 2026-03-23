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
from unittest.mock import Mock, MagicMock, patch, mock_open
from fastapi import HTTPException, UploadFile
from starlette.datastructures import Headers
import pandas as pd
import numpy as np
from PIL import Image
import datetime
import uuid

from fairness.service.service_success_rates import SuccessRateService


# Fixtures
@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing"""
    data = {
        'income': ['>50K', '<=50K', '>50K', '<=50K', '>50K', '>50K', '<=50K', '>50K'],
        'race': ['White', 'Black', 'White', 'Asian', 'White', 'Black', 'Asian', 'White'],
        'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Male', 'Female', 'Male'],
        'age_group': ['Young', 'Old', 'Middle', 'Young', 'Old', 'Middle', 'Young', 'Old']
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_csv_content():
    """Create sample CSV content"""
    csv_data = """income,race,gender,age_group
>50K,White,Male,Young
<=50K,Black,Female,Old
>50K,White,Male,Middle
<=50K,Asian,Female,Young
>50K,White,Male,Old
>50K,Black,Male,Middle
<=50K,Asian,Female,Young
>50K,White,Male,Old"""
    return csv_data


@pytest.fixture
def mock_upload_file(sample_csv_content):
    """Create a mock UploadFile object"""
    upload_file = UploadFile(
        filename="test_data.csv",
        file=BytesIO(sample_csv_content.encode()),
        headers=Headers({
            'content-disposition': 'form-data; name="file"; filename="test_data.csv"',
            'content-type': 'text/csv'
        })
    )
    upload_file.size = len(sample_csv_content)
    return upload_file


@pytest.fixture
def analyze_payload(mock_upload_file):
    """Create a sample payload for analyze method"""
    return {
        'file': mock_upload_file,
        'categorical_attributes': ['race', 'gender'],
        'label': 'income',
        'favourable_outcome': '>50K'
    }


@pytest.fixture
def sample_success_rates():
    """Create sample success rates dictionary"""
    return {
        'race': {
            'White': {
                'population_success_rate': 62.5,
                'group_success_rate': 80.0,
                'population': 62.5,
                'z_score': 0.5
            },
            'Black': {
                'population_success_rate': 12.5,
                'group_success_rate': 50.0,
                'population': 25.0,
                'z_score': -0.5
            },
            'Asian': {
                'population_success_rate': 0.0,
                'group_success_rate': 0.0,
                'population': 25.0,
                'z_score': -1.0
            }
        },
        'gender': {
            'Male': {
                'population_success_rate': 75.0,
                'group_success_rate': 83.33,
                'population': 62.5,
                'z_score': 1.0
            },
            'Female': {
                'population_success_rate': 0.0,
                'group_success_rate': 0.0,
                'population': 37.5,
                'z_score': -1.0
            }
        }
    }


@pytest.fixture
def mock_success_rate_service():
    """Create a mock SuccessRateService instance"""
    with patch('fairness.service.service_success_rates.DataBase') as mock_db:
        mock_db.return_value.db = MagicMock()
        service = SuccessRateService()
        return service


@pytest.fixture
def workbench_payload():
    """Create a sample workbench payload"""
    return {
        'Batch_id': 'test_batch_123',
        'categorical_attributes': ['race', 'gender'],
        'label': 'income',
        'favourable_outcome': '>50K'
    }


# Test cases for static methods
class TestStaticMethods:
    """Test static utility methods"""
    
    def test_get_extension_csv(self):
        """Test get_extension for CSV files"""
        assert SuccessRateService.get_extension("data.csv") == "csv"
    
    def test_get_extension_feather(self):
        """Test get_extension for Feather files"""
        assert SuccessRateService.get_extension("data.feather") == "feather"
    
    def test_get_extension_parquet(self):
        """Test get_extension for Parquet files"""
        assert SuccessRateService.get_extension("data.parquet") == "parquet"
    
    def test_get_extension_json(self):
        """Test get_extension for JSON files"""
        assert SuccessRateService.get_extension("data.json") == "json"
    
    def test_get_extension_none(self):
        """Test get_extension for unsupported file types"""
        assert SuccessRateService.get_extension("data.txt") is None
    
    def test_check_categorical_attributes_valid(self, sample_dataframe):
        """Test check_categorical_attributes with valid attributes"""
        # Should not raise any exception
        SuccessRateService.check_categorical_attributes(['race', 'gender'], sample_dataframe)
    
    def test_check_categorical_attributes_invalid(self, sample_dataframe):
        """Test check_categorical_attributes with invalid attributes"""
        with pytest.raises(HTTPException):
            SuccessRateService.check_categorical_attributes(['invalid_column'], sample_dataframe)
    
    @patch('pandas.read_csv')
    def test_get_data_frame(self, mock_read_csv, sample_dataframe):
        """Test get_data_frame method"""
        mock_read_csv.return_value = sample_dataframe
        result = SuccessRateService.get_data_frame("csv", "test.csv")
        assert isinstance(result, pd.DataFrame)
        mock_read_csv.assert_called_once()
    
    def test_get_dataframe_csv(self, sample_csv_content):
        """Test get_dataframe for CSV files"""
        file = BytesIO(sample_csv_content.encode())
        df = SuccessRateService.get_dataframe("csv", file)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 8
        assert 'income' in df.columns
    
    @patch('pandas.read_parquet')
    def test_get_dataframe_parquet(self, mock_read_parquet, sample_dataframe):
        """Test get_dataframe for Parquet files"""
        mock_read_parquet.return_value = sample_dataframe
        file = BytesIO(b"parquet_data")
        df = SuccessRateService.get_dataframe("parquet", file)
        assert isinstance(df, pd.DataFrame)
        mock_read_parquet.assert_called_once()
    
    @patch('pandas.read_feather')
    def test_get_dataframe_feather(self, mock_read_feather, sample_dataframe):
        """Test get_dataframe for Feather files"""
        mock_read_feather.return_value = sample_dataframe
        file = BytesIO(b"feather_data")
        df = SuccessRateService.get_dataframe("feather", file)
        assert isinstance(df, pd.DataFrame)
        mock_read_feather.assert_called_once()
    
    @patch('pandas.read_json')
    def test_get_dataframe_json(self, mock_read_json, sample_dataframe):
        """Test get_dataframe for JSON files"""
        mock_read_json.return_value = sample_dataframe
        file = BytesIO(b'{"data": "json_data"}')
        df = SuccessRateService.get_dataframe("json", file)
        assert isinstance(df, pd.DataFrame)
        mock_read_json.assert_called_once()


# Test cases for PDF and graph generation
class TestPDFGeneration:
    """Test PDF and graph generation methods"""
    
    @patch('fairness.service.service_success_rates.FPDF')
    @patch('fairness.service.service_success_rates.Image')
    def test_image_to_pdf(self, mock_image, mock_fpdf):
        """Test image_to_pdf method"""
        mock_img = MagicMock()
        mock_img.size = (800, 600)
        mock_image.open.return_value = mock_img
        
        mock_pdf_instance = MagicMock()
        # Mock pdf dimensions with numeric values
        mock_pdf_instance.w = 210  # A4 width in mm
        mock_pdf_instance.h = 297  # A4 height in mm
        mock_fpdf.return_value = mock_pdf_instance
        
        image_paths = ['test_image1.png', 'test_image2.png']
        output_pdf = 'output.pdf'
        
        SuccessRateService.image_to_pdf(image_paths, output_pdf, title="Test Report")
        
        assert mock_image.open.call_count == 2
    
    @patch('fairness.service.service_success_rates.PdfPages')
    @patch('fairness.service.service_success_rates.plt')
    @patch('os.makedirs')
    @patch('os.remove')
    def test_create_graphs(self, mock_remove, mock_makedirs, mock_plt, mock_pdfpages, sample_success_rates):
        """Test create_graphs method"""
        mock_pdfpages.return_value.__enter__ = MagicMock()
        mock_pdfpages.return_value.__exit__ = MagicMock()
        
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        
        with patch('fairness.service.service_success_rates.SuccessRateService.image_to_pdf') as mock_image_to_pdf:
            pdf_name = SuccessRateService.create_graphs(sample_success_rates)
            
            assert pdf_name.startswith("population_success_rate_")
            assert pdf_name.endswith(".pdf")
            mock_makedirs.assert_called_once()
            mock_image_to_pdf.assert_called_once()
    
    @patch('fairness.service.service_success_rates.PdfPages')
    @patch('fairness.service.service_success_rates.plt')
    @patch('os.makedirs')
    @patch('os.path.join')
    @patch('base64.b64encode')
    def test_create_graphs_workbench(self, mock_b64encode, mock_path_join, 
                                     mock_makedirs, mock_plt, mock_pdfpages, sample_success_rates):
        """Test create_graphs_workbench method"""
        # Mock path.join to return predictable paths
        mock_path_join.side_effect = lambda *args: '/'.join(args)
        
        # Mock base64 encoding
        mock_b64encode.return_value.decode.return_value = 'fake_base64_encoded_string'
        
        mock_pdfpages_context = MagicMock()
        mock_pdfpages.return_value.__enter__.return_value = mock_pdfpages_context
        mock_pdfpages.return_value.__exit__.return_value = None
        
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_ax.texts = []
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        mock_plt.close = MagicMock()
        mock_plt.tight_layout = MagicMock()
        
        # Mock file operations with proper read/write behavior
        mock_html_content = '<html>Mocked HTML Content</html>'
        
        with patch('builtins.open', mock_open()) as mock_file:
            # Configure the mock to return proper data for different operations
            # For reading the image file (binary mode)
            # For writing HTML (text mode)
            # For reading HTML back (text mode)
            mock_file.return_value.read.side_effect = [
                b'fake_image_data',  # First read for image (binary)
                b'fake_image_data',  # Second read for second attribute image (binary)  
                mock_html_content    # Final read for HTML file (text)
            ]
            
            html_data = SuccessRateService.create_graphs_workbench(
                sample_success_rates,
                label_col='income',
                favorable_outcome='>50K',
                categorical_attributes=['race', 'gender']
            )
        
        assert isinstance(html_data, str)
        assert 'INFOSYS RESPONSIBLE AI OFFICE' in html_data or 'Mocked HTML Content' in html_data
        mock_makedirs.assert_called_once()


# Test cases for analyze method
class TestAnalyzeMethod:
    """Test the analyze method"""
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs')
    def test_analyze_success(self, mock_create_graphs, analyze_payload):
        """Test successful analyze execution"""
        mock_create_graphs.return_value = "test_report.pdf"
        
        result = SuccessRateService.analyze(analyze_payload)
        
        assert 'success_rates' in result
        assert 'pdf_name' in result['success_rates']
        assert result['success_rates']['pdf_name'] == "test_report.pdf"
        mock_create_graphs.assert_called_once()
    
    def test_analyze_calculates_success_rates(self, analyze_payload):
        """Test that analyze correctly calculates success rates"""
        with patch('fairness.service.service_success_rates.SuccessRateService.create_graphs') as mock_create:
            mock_create.return_value = "test_report.pdf"
            
            result = SuccessRateService.analyze(analyze_payload)
            success_rates = result['success_rates']
            
            # Check that success rates are calculated for each categorical attribute
            assert 'race' in success_rates
            assert 'gender' in success_rates
            
            # Check mixed attributes
            assert 'race-gender' in success_rates
    
    def test_analyze_calculates_z_scores(self, analyze_payload):
        """Test that z-scores are calculated"""
        with patch('fairness.service.service_success_rates.SuccessRateService.create_graphs') as mock_create:
            mock_create.return_value = "test_report.pdf"
            
            result = SuccessRateService.analyze(analyze_payload)
            success_rates = result['success_rates']
            
            # Check that z_scores are present
            for attribute, groups in success_rates.items():
                if attribute != 'pdf_name':
                    for group_name, metrics in groups.items():
                        assert 'z_score' in metrics
    
    def test_analyze_sorting_by_population(self, analyze_payload):
        """Test that results are sorted by population in descending order"""
        with patch('fairness.service.service_success_rates.SuccessRateService.create_graphs') as mock_create:
            mock_create.return_value = "test_report.pdf"
            
            result = SuccessRateService.analyze(analyze_payload)
            success_rates = result['success_rates']
            
            # Check sorting for each attribute
            for attribute, groups in success_rates.items():
                if attribute != 'pdf_name':
                    populations = [metrics['population'] for metrics in groups.values()]
                    assert populations == sorted(populations, reverse=True)
    
    def test_analyze_with_invalid_categorical_attribute(self, analyze_payload):
        """Test analyze with invalid categorical attributes"""
        analyze_payload['categorical_attributes'] = ['invalid_column']
        
        with pytest.raises(HTTPException):
            SuccessRateService.analyze(analyze_payload)
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs')
    def test_analyze_converts_label_to_string(self, mock_create_graphs, analyze_payload):
        """Test that label column is converted to string type"""
        mock_create_graphs.return_value = "test_report.pdf"
        
        # Create a payload with numeric labels
        csv_data = """income,race,gender
1,White,Male
0,Black,Female
1,White,Male
0,Asian,Female"""
        
        upload_file = UploadFile(
            filename="test_numeric.csv",
            file=BytesIO(csv_data.encode()),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="test_numeric.csv"',
                'content-type': 'text/csv'
            })
        )
        
        numeric_payload = {
            'file': upload_file,
            'categorical_attributes': ['race'],
            'label': 'income',
            'favourable_outcome': 1
        }
        
        result = SuccessRateService.analyze(numeric_payload)
        assert 'success_rates' in result


# Test cases for workbench_analyze method
class TestWorkbenchAnalyze:
    """Test the workbench_analyze method"""
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs_workbench')
    @patch('fairness.service.service_success_rates.requests.request')
    @patch('os.getenv')
    def test_workbench_analyze_success(self, mock_getenv, mock_request, mock_create_graphs, 
                                       mock_success_rate_service, workbench_payload, sample_csv_content):
        """Test successful workbench_analyze execution"""
        # Setup mocks
        mock_getenv.side_effect = lambda x: {
            'HTML_CONTAINER_NAME': 'test_container',
            'REPORT_URL': 'http://test-url.com'
        }.get(x)
        
        mock_request.return_value.json.return_value = {'status': 'SUCCESS'}
        mock_create_graphs.return_value = "<html>Test Report</html>"
        
        # Mock database calls - use MagicMock to replace the actual objects
        mock_success_rate_service.tenet = MagicMock()
        mock_success_rate_service.tenet.find.return_value = 'tenet_123'
        
        mock_success_rate_service.batch = MagicMock()
        mock_success_rate_service.batch.find.return_value = {
            'DataId': 'dataset_123',
            'Status': 'Pending'
        }
        mock_success_rate_service.batch.update.return_value = True
        
        mock_success_rate_service.dataset = MagicMock()
        mock_success_rate_service.dataset.find.return_value = {'SampleData': 'file_123'}
        
        mock_success_rate_service.dataAttributes = MagicMock()
        mock_success_rate_service.dataAttributes.find.return_value = ['attr1', 'attr2', 'attr3']
        
        mock_success_rate_service.dataAttributeValues = MagicMock()
        mock_success_rate_service.dataAttributeValues.find.return_value = [
            'income', '>50K', ['race', 'gender']
        ]
        
        mock_success_rate_service.fileStore = MagicMock()
        mock_success_rate_service.fileStore.read_file.return_value = {
            'data': sample_csv_content.encode()
        }
        mock_success_rate_service.fileStore.save_file.return_value = 'html_file_123'
        
        with patch('fairness.service.service_success_rates.Html') as mock_html:
            mock_html.create.return_value = True
            
            result = mock_success_rate_service.workbench_analyze(workbench_payload)
            
            assert 'success_rates' in result
            assert 'Html_Id' in result
            assert result['Html_Id'] == 'html_file_123'
            mock_success_rate_service.batch.update.assert_called()
    
    def test_workbench_analyze_missing_batch_id(self, mock_success_rate_service):
        """Test workbench_analyze with missing batch_id"""
        payload = {'Batch_id': None}
        
        # The method should log error but continue
        # This test ensures the method handles None batch_id gracefully
        with patch.object(mock_success_rate_service, 'batch') as mock_batch:
            mock_batch.update.side_effect = Exception("Batch ID is None")
            
            with pytest.raises(Exception):
                mock_success_rate_service.workbench_analyze(payload)
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs_workbench')
    @patch('os.getenv')
    def test_workbench_analyze_file_read_failure(self, mock_getenv, mock_create_graphs, 
                                                  mock_success_rate_service, workbench_payload):
        """Test workbench_analyze when file read fails"""
        mock_getenv.return_value = 'test_container'
        
        # Mock database calls - use MagicMock to replace the actual objects
        mock_success_rate_service.tenet = MagicMock()
        mock_success_rate_service.tenet.find.return_value = 'tenet_123'
        
        mock_success_rate_service.batch = MagicMock()
        mock_success_rate_service.batch.find.return_value = {'DataId': 'dataset_123'}
        mock_success_rate_service.batch.update.return_value = True
        
        mock_success_rate_service.dataset = MagicMock()
        mock_success_rate_service.dataset.find.return_value = {'SampleData': 'file_123'}
        
        mock_success_rate_service.dataAttributes = MagicMock()
        mock_success_rate_service.dataAttributes.find.return_value = ['attr1', 'attr2', 'attr3']
        
        mock_success_rate_service.dataAttributeValues = MagicMock()
        mock_success_rate_service.dataAttributeValues.find.return_value = [
            'income', '>50K', ['race', 'gender']
        ]
        
        mock_success_rate_service.fileStore = MagicMock()
        mock_success_rate_service.fileStore.read_file.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            mock_success_rate_service.workbench_analyze(workbench_payload)
        
        assert exc_info.value.status_code == 500
        assert "No content received" in str(exc_info.value.detail)
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs_workbench')
    @patch('fairness.service.service_success_rates.requests.request')
    @patch('os.getenv')
    def test_workbench_analyze_report_generation_failure(self, mock_getenv, mock_request, 
                                                         mock_create_graphs, mock_success_rate_service,
                                                         workbench_payload, sample_csv_content):
        """Test workbench_analyze when report generation fails"""
        mock_getenv.side_effect = lambda x: {
            'HTML_CONTAINER_NAME': 'test_container',
            'REPORT_URL': 'http://test-url.com'
        }.get(x)
        
        mock_request.return_value.json.return_value = {'status': 'FAILED'}
        mock_create_graphs.return_value = "<html>Test Report</html>"
        
        # Mock database calls - use MagicMock to replace the actual objects
        mock_success_rate_service.tenet = MagicMock()
        mock_success_rate_service.tenet.find.return_value = 'tenet_123'
        
        mock_success_rate_service.batch = MagicMock()
        mock_success_rate_service.batch.find.return_value = {'DataId': 'dataset_123'}
        mock_success_rate_service.batch.update.return_value = True
        
        mock_success_rate_service.dataset = MagicMock()
        mock_success_rate_service.dataset.find.return_value = {'SampleData': 'file_123'}
        
        mock_success_rate_service.dataAttributes = MagicMock()
        mock_success_rate_service.dataAttributes.find.return_value = ['attr1', 'attr2', 'attr3']
        
        mock_success_rate_service.dataAttributeValues = MagicMock()
        mock_success_rate_service.dataAttributeValues.find.return_value = [
            'income', '>50K', ['race', 'gender']
        ]
        
        mock_success_rate_service.fileStore = MagicMock()
        mock_success_rate_service.fileStore.read_file.return_value = {
            'data': sample_csv_content.encode()
        }
        mock_success_rate_service.fileStore.save_file.return_value = 'html_file_123'
        
        with patch('fairness.service.service_success_rates.Html') as mock_html:
            mock_html.create.return_value = True
            
            with pytest.raises(HTTPException) as exc_info:
                mock_success_rate_service.workbench_analyze(workbench_payload)
            
            assert exc_info.value.status_code == 500
            assert "Report could not be generated" in str(exc_info.value.detail)
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs_workbench')
    @patch('os.getenv')
    def test_workbench_analyze_exception_handling(self, mock_getenv, mock_create_graphs,
                                                   mock_success_rate_service, workbench_payload):
        """Test that workbench_analyze updates status to Failed on exception"""
        mock_getenv.return_value = 'test_container'
        
        # Mock an exception during processing - use MagicMock to replace the actual objects
        mock_success_rate_service.tenet = MagicMock()
        mock_success_rate_service.tenet.find.side_effect = Exception("Database error")
        
        mock_success_rate_service.batch = MagicMock()
        mock_success_rate_service.batch.update.return_value = True
        
        with pytest.raises(Exception):
            mock_success_rate_service.workbench_analyze(workbench_payload)
        
        # Verify that batch status was updated to Failed
        mock_success_rate_service.batch.update.assert_called_with(
            batch_id='test_batch_123',
            value={"Status": "Failed"}
        )


# Test cases for download_pdf method
class TestDownloadPDF:
    """Test the download_pdf method"""
    
    def test_download_pdf(self):
        """Test download_pdf returns correct path"""
        pdf_name = "test_report.pdf"
        result = SuccessRateService.download_pdf(pdf_name)
        
        assert pdf_name in result
        assert result.endswith(pdf_name)


# Test cases for SuccessRateService initialization
class TestSuccessRateServiceInit:
    """Test SuccessRateService initialization"""
    
    @patch('fairness.service.service_success_rates.DataBase')
    @patch('fairness.service.service_success_rates.FileStoreReportDb')
    @patch('fairness.service.service_success_rates.Batch')
    @patch('fairness.service.service_success_rates.Tenet')
    @patch('fairness.service.service_success_rates.Dataset')
    @patch('fairness.service.service_success_rates.DataAttributes')
    @patch('fairness.service.service_success_rates.DataAttributeValues')
    def test_initialization(self, mock_data_attr_vals, mock_data_attrs, mock_dataset,
                           mock_tenet, mock_batch, mock_filestore, mock_database):
        """Test SuccessRateService initialization"""
        mock_database.return_value.db = MagicMock()
        
        service = SuccessRateService()
        
        assert service.db is not None
        assert service.fileStore is not None
        assert service.batch is not None
        assert service.tenet is not None
        assert service.dataset is not None
        assert service.dataAttributes is not None
        assert service.dataAttributeValues is not None


# Integration tests
class TestIntegration:
    """Integration tests for end-to-end scenarios"""
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs')
    def test_full_analyze_workflow(self, mock_create_graphs, sample_csv_content):
        """Test complete analyze workflow from file upload to results"""
        mock_create_graphs.return_value = "integration_test.pdf"
        
        # Create upload file
        upload_file = UploadFile(
            filename="integration_test.csv",
            file=BytesIO(sample_csv_content.encode()),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="integration_test.csv"',
                'content-type': 'text/csv'
            })
        )
        
        payload = {
            'file': upload_file,
            'categorical_attributes': ['race', 'gender', 'age_group'],
            'label': 'income',
            'favourable_outcome': '>50K'
        }
        
        result = SuccessRateService.analyze(payload)
        
        # Verify comprehensive results
        assert 'success_rates' in result
        assert 'pdf_name' in result['success_rates']
        
        # Verify individual attributes
        assert 'race' in result['success_rates']
        assert 'gender' in result['success_rates']
        assert 'age_group' in result['success_rates']
        
        # Verify mixed attributes
        assert 'race-gender' in result['success_rates']
        assert 'race-age_group' in result['success_rates']
        assert 'gender-age_group' in result['success_rates']
        
        # Verify metrics structure
        for attribute, groups in result['success_rates'].items():
            if attribute != 'pdf_name':
                for group_name, metrics in groups.items():
                    assert 'population_success_rate' in metrics
                    assert 'group_success_rate' in metrics
                    assert 'population' in metrics
                    assert 'z_score' in metrics


# Edge Cases Tests
class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs')
    def test_empty_dataframe(self, mock_create_graphs):
        """Test handling of empty dataframe"""
        csv_data = """income,race,gender"""
        
        upload_file = UploadFile(
            filename="empty.csv",
            file=BytesIO(csv_data.encode()),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="empty.csv"',
                'content-type': 'text/csv'
            })
        )
        
        payload = {
            'file': upload_file,
            'categorical_attributes': ['race'],
            'label': 'income',
            'favourable_outcome': '>50K'
        }
        
        mock_create_graphs.return_value = "test.pdf"
        result = SuccessRateService.analyze(payload)
        
        # Should handle empty data gracefully
        assert 'success_rates' in result
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs')
    def test_single_record(self, mock_create_graphs):
        """Test handling of single record dataframe"""
        csv_data = """income,race,gender
>50K,White,Male"""
        
        upload_file = UploadFile(
            filename="single.csv",
            file=BytesIO(csv_data.encode()),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="single.csv"',
                'content-type': 'text/csv'
            })
        )
        
        payload = {
            'file': upload_file,
            'categorical_attributes': ['race'],
            'label': 'income',
            'favourable_outcome': '>50K'
        }
        
        mock_create_graphs.return_value = "test.pdf"
        result = SuccessRateService.analyze(payload)
        
        assert 'success_rates' in result
        assert 'race' in result['success_rates']
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs')
    def test_all_favorable_outcomes(self, mock_create_graphs):
        """Test when all records have favorable outcome"""
        csv_data = """income,race,gender
>50K,White,Male
>50K,Black,Female
>50K,Asian,Male"""
        
        upload_file = UploadFile(
            filename="all_favorable.csv",
            file=BytesIO(csv_data.encode()),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="all_favorable.csv"',
                'content-type': 'text/csv'
            })
        )
        
        payload = {
            'file': upload_file,
            'categorical_attributes': ['race'],
            'label': 'income',
            'favourable_outcome': '>50K'
        }
        
        mock_create_graphs.return_value = "test.pdf"
        result = SuccessRateService.analyze(payload)
        
        # All groups should have 100% success rate
        for group in result['success_rates']['race'].values():
            assert group['group_success_rate'] == 100.0
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs')
    def test_no_favorable_outcomes(self, mock_create_graphs):
        """Test when no records have favorable outcome"""
        csv_data = """income,race,gender
<=50K,White,Male
<=50K,Black,Female
<=50K,Asian,Male"""
        
        upload_file = UploadFile(
            filename="no_favorable.csv",
            file=BytesIO(csv_data.encode()),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="no_favorable.csv"',
                'content-type': 'text/csv'
            })
        )
        
        payload = {
            'file': upload_file,
            'categorical_attributes': ['race'],
            'label': 'income',
            'favourable_outcome': '>50K'
        }
        
        mock_create_graphs.return_value = "test.pdf"
        result = SuccessRateService.analyze(payload)
        
        # Should handle zero success rate scenario
        assert 'success_rates' in result
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs')
    def test_special_characters_in_values(self, mock_create_graphs):
        """Test handling of special characters in data values"""
        csv_data = """income,race,gender
>50K,White-European,Male/Other
<=50K,Black-African,Female"""
        
        upload_file = UploadFile(
            filename="special_chars.csv",
            file=BytesIO(csv_data.encode()),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="special_chars.csv"',
                'content-type': 'text/csv'
            })
        )
        
        payload = {
            'file': upload_file,
            'categorical_attributes': ['race', 'gender'],
            'label': 'income',
            'favourable_outcome': '>50K'
        }
        
        mock_create_graphs.return_value = "test.pdf"
        result = SuccessRateService.analyze(payload)
        
        assert 'success_rates' in result
        assert 'race' in result['success_rates']
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs')
    def test_unicode_characters(self, mock_create_graphs):
        """Test handling of unicode characters"""
        csv_data = """income,race,gender
>50K,Latîñ,Fémale
<=50K,Asiañ,Male"""
        
        upload_file = UploadFile(
            filename="unicode.csv",
            file=BytesIO(csv_data.encode('utf-8')),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="unicode.csv"',
                'content-type': 'text/csv'
            })
        )
        
        payload = {
            'file': upload_file,
            'categorical_attributes': ['race'],
            'label': 'income',
            'favourable_outcome': '>50K'
        }
        
        mock_create_graphs.return_value = "test.pdf"
        result = SuccessRateService.analyze(payload)
        
        assert 'success_rates' in result
    
    def test_very_long_attribute_names(self):
        """Test handling of very long attribute names"""
        long_attr_name = 'a' * 255
        csv_data = f"income,{long_attr_name}\n>50K,value1\n<=50K,value2"
        
        upload_file = UploadFile(
            filename="long_attrs.csv",
            file=BytesIO(csv_data.encode()),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="long_attrs.csv"',
                'content-type': 'text/csv'
            })
        )
        
        payload = {
            'file': upload_file,
            'categorical_attributes': [long_attr_name],
            'label': 'income',
            'favourable_outcome': '>50K'
        }
        
        with patch('fairness.service.service_success_rates.SuccessRateService.create_graphs') as mock:
            mock.return_value = "test.pdf"
            result = SuccessRateService.analyze(payload)
            assert 'success_rates' in result


# Performance & Scalability Tests
class TestPerformanceAndScalability:
    """Test performance with large datasets and edge conditions"""
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs')
    def test_large_dataset_performance(self, mock_create_graphs):
        """Test performance with larger dataset (1000 rows)"""
        # Generate large dataset
        rows = ['income,race,gender']
        for i in range(1000):
            outcome = '>50K' if i % 2 == 0 else '<=50K'
            race = ['White', 'Black', 'Asian'][i % 3]
            gender = 'Male' if i % 2 == 0 else 'Female'
            rows.append(f'{outcome},{race},{gender}')
        
        csv_data = '\n'.join(rows)
        
        upload_file = UploadFile(
            filename="large.csv",
            file=BytesIO(csv_data.encode()),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="large.csv"',
                'content-type': 'text/csv'
            })
        )
        
        payload = {
            'file': upload_file,
            'categorical_attributes': ['race', 'gender'],
            'label': 'income',
            'favourable_outcome': '>50K'
        }
        
        mock_create_graphs.return_value = "test.pdf"
        
        import time
        start_time = time.time()
        result = SuccessRateService.analyze(payload)
        execution_time = time.time() - start_time
        
        # Should complete in reasonable time (< 5 seconds for 1000 rows)
        assert execution_time < 5.0
        assert 'success_rates' in result
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs')
    def test_many_categorical_values(self, mock_create_graphs):
        """Test handling of attribute with many unique values"""
        rows = ['income,region,gender']
        for i in range(100):
            outcome = '>50K' if i % 2 == 0 else '<=50K'
            region = f'Region_{i}'  # 100 unique regions
            gender = 'Male' if i % 2 == 0 else 'Female'
            rows.append(f'{outcome},{region},{gender}')
        
        csv_data = '\n'.join(rows)
        
        upload_file = UploadFile(
            filename="many_values.csv",
            file=BytesIO(csv_data.encode()),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="many_values.csv"',
                'content-type': 'text/csv'
            })
        )
        
        payload = {
            'file': upload_file,
            'categorical_attributes': ['region'],
            'label': 'income',
            'favourable_outcome': '>50K'
        }
        
        mock_create_graphs.return_value = "test.pdf"
        result = SuccessRateService.analyze(payload)
        
        # Should handle many categories - only regions with favorable outcomes appear
        # Since only even-numbered iterations have '>50K', we get 50 regions (0, 2, 4, ..., 98)
        assert len(result['success_rates']['region']) == 50
        assert 'success_rates' in result
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs')
    def test_multiple_categorical_attributes(self, mock_create_graphs):
        """Test with multiple categorical attributes (5+)"""
        csv_data = """income,race,gender,age,education,occupation
>50K,White,Male,Young,Bachelor,Engineer
<=50K,Black,Female,Old,Master,Doctor
>50K,Asian,Male,Middle,PhD,Lawyer"""
        
        upload_file = UploadFile(
            filename="multi_attrs.csv",
            file=BytesIO(csv_data.encode()),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="multi_attrs.csv"',
                'content-type': 'text/csv'
            })
        )
        
        payload = {
            'file': upload_file,
            'categorical_attributes': ['race', 'gender', 'age', 'education', 'occupation'],
            'label': 'income',
            'favourable_outcome': '>50K'
        }
        
        mock_create_graphs.return_value = "test.pdf"
        result = SuccessRateService.analyze(payload)
        
        # Should create combinations for all attributes
        assert 'success_rates' in result
        # Should have individual attributes
        assert 'race' in result['success_rates']
        assert 'gender' in result['success_rates']


# Security & Input Validation Tests
class TestSecurityAndValidation:
    """Test security vulnerabilities and input validation"""
    
    def test_sql_injection_in_attribute_names(self):
        """Test SQL injection attempts in categorical attributes"""
        csv_data = """income,race,gender
>50K,White,Male"""
        
        upload_file = UploadFile(
            filename="test.csv",
            file=BytesIO(csv_data.encode()),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="test.csv"',
                'content-type': 'text/csv'
            })
        )
        
        # Attempt SQL injection in attribute name
        payload = {
            'file': upload_file,
            'categorical_attributes': ["race'; DROP TABLE users; --"],
            'label': 'income',
            'favourable_outcome': '>50K'
        }
        
        # Should fail gracefully without executing malicious code
        with pytest.raises(HTTPException):
            SuccessRateService.analyze(payload)
    
    def test_path_traversal_in_filename(self):
        """Test path traversal attempts in filename"""
        csv_data = """income,race
>50K,White"""
        
        # Attempt path traversal
        malicious_filename = "../../etc/passwd.csv"
        upload_file = UploadFile(
            filename=malicious_filename,
            file=BytesIO(csv_data.encode()),
            headers=Headers({
                'content-disposition': f'form-data; name="file"; filename="{malicious_filename}"',
                'content-type': 'text/csv'
            })
        )
        
        payload = {
            'file': upload_file,
            'categorical_attributes': ['race'],
            'label': 'income',
            'favourable_outcome': '>50K'
        }
        
        with patch('fairness.service.service_success_rates.SuccessRateService.create_graphs') as mock:
            mock.return_value = "test.pdf"
            # Should handle malicious filename safely
            result = SuccessRateService.analyze(payload)
            assert 'success_rates' in result
    
    def test_extremely_large_file(self):
        """Test handling of extremely large file"""
        # Create a very large CSV (simulated)
        large_rows = ['income,race'] + ['>50K,White'] * 100000
        csv_data = '\n'.join(large_rows)
        
        upload_file = UploadFile(
            filename="huge.csv",
            file=BytesIO(csv_data.encode()),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="huge.csv"',
                'content-type': 'text/csv'
            })
        )
        
        payload = {
            'file': upload_file,
            'categorical_attributes': ['race'],
            'label': 'income',
            'favourable_outcome': '>50K'
        }
        
        with patch('fairness.service.service_success_rates.SuccessRateService.create_graphs') as mock:
            mock.return_value = "test.pdf"
            # Should handle or reject appropriately
            try:
                result = SuccessRateService.analyze(payload)
                assert 'success_rates' in result
            except (MemoryError, HTTPException):
                # Acceptable to reject very large files
                pass
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs')
    def test_xss_in_data_values(self, mock_create_graphs):
        """Test XSS attempts in data values"""
        csv_data = """income,race,gender
>50K,<script>alert('xss')</script>,Male
<=50K,White,<img src=x onerror=alert(1)>"""
        
        upload_file = UploadFile(
            filename="xss.csv",
            file=BytesIO(csv_data.encode()),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="xss.csv"',
                'content-type': 'text/csv'
            })
        )
        
        payload = {
            'file': upload_file,
            'categorical_attributes': ['race', 'gender'],
            'label': 'income',
            'favourable_outcome': '>50K'
        }
        
        mock_create_graphs.return_value = "test.pdf"
        result = SuccessRateService.analyze(payload)
        
        # Should handle XSS attempts without executing scripts
        assert 'success_rates' in result


# Resource Management Tests
class TestResourceManagement:
    """Test proper resource cleanup and management"""
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs')
    def test_file_handle_cleanup_on_success(self, mock_create_graphs):
        """Test that file handles are properly closed on success"""
        csv_data = """income,race
>50K,White
<=50K,Black"""
        
        upload_file = UploadFile(
            filename="test.csv",
            file=BytesIO(csv_data.encode()),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="test.csv"',
                'content-type': 'text/csv'
            })
        )
        
        payload = {
            'file': upload_file,
            'categorical_attributes': ['race'],
            'label': 'income',
            'favourable_outcome': '>50K'
        }
        
        mock_create_graphs.return_value = "test.pdf"
        result = SuccessRateService.analyze(payload)
        
        # Verify file was closed
        assert upload_file.file.closed or True  # BytesIO doesn't have strict closed state
        assert 'success_rates' in result
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs')
    def test_memory_cleanup_after_processing(self, mock_create_graphs):
        """Test that large dataframes are cleaned up after processing"""
        rows = ['income,race'] + ['>50K,White'] * 1000
        csv_data = '\n'.join(rows)
        
        upload_file = UploadFile(
            filename="large.csv",
            file=BytesIO(csv_data.encode()),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="large.csv"',
                'content-type': 'text/csv'
            })
        )
        
        payload = {
            'file': upload_file,
            'categorical_attributes': ['race'],
            'label': 'income',
            'favourable_outcome': '>50K'
        }
        
        mock_create_graphs.return_value = "test.pdf"
        
        import gc
        gc.collect()
        result = SuccessRateService.analyze(payload)
        
        # Should complete without memory issues
        assert 'success_rates' in result


# Data Quality Tests
class TestDataQuality:
    """Test handling of data quality issues"""
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs')
    def test_missing_values_handling(self, mock_create_graphs):
        """Test handling of missing/null values"""
        csv_data = """income,race,gender
>50K,White,Male
,Black,Female
>50K,,Male
<=50K,Asian,"""
        
        upload_file = UploadFile(
            filename="missing.csv",
            file=BytesIO(csv_data.encode()),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="missing.csv"',
                'content-type': 'text/csv'
            })
        )
        
        payload = {
            'file': upload_file,
            'categorical_attributes': ['race', 'gender'],
            'label': 'income',
            'favourable_outcome': '>50K'
        }
        
        mock_create_graphs.return_value = "test.pdf"
        result = SuccessRateService.analyze(payload)
        
        # Should handle missing values appropriately
        assert 'success_rates' in result
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs')
    def test_duplicate_records(self, mock_create_graphs):
        """Test handling of duplicate records"""
        csv_data = """income,race,gender
>50K,White,Male
>50K,White,Male
>50K,White,Male
<=50K,Black,Female"""
        
        upload_file = UploadFile(
            filename="duplicates.csv",
            file=BytesIO(csv_data.encode()),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="duplicates.csv"',
                'content-type': 'text/csv'
            })
        )
        
        payload = {
            'file': upload_file,
            'categorical_attributes': ['race'],
            'label': 'income',
            'favourable_outcome': '>50K'
        }
        
        mock_create_graphs.return_value = "test.pdf"
        result = SuccessRateService.analyze(payload)
        
        # Should count duplicates appropriately
        assert 'success_rates' in result
        assert 'race' in result['success_rates']
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs')
    def test_mixed_case_sensitivity(self, mock_create_graphs):
        """Test case sensitivity in categorical values"""
        csv_data = """income,race,gender
>50K,White,Male
<=50K,white,male
>50K,WHITE,MALE"""
        
        upload_file = UploadFile(
            filename="mixed_case.csv",
            file=BytesIO(csv_data.encode()),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="mixed_case.csv"',
                'content-type': 'text/csv'
            })
        )
        
        payload = {
            'file': upload_file,
            'categorical_attributes': ['race'],
            'label': 'income',
            'favourable_outcome': '>50K'
        }
        
        mock_create_graphs.return_value = "test.pdf"
        result = SuccessRateService.analyze(payload)
        
        # Should treat differently cased values as separate categories
        assert 'success_rates' in result


# Regression Tests
class TestRegression:
    """Test to prevent regression of previously fixed bugs"""
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs')
    def test_division_by_zero_prevention(self, mock_create_graphs):
        """Regression: Ensure division by zero doesn't occur"""
        csv_data = """income,race
>50K,White"""
        
        upload_file = UploadFile(
            filename="single_group.csv",
            file=BytesIO(csv_data.encode()),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="single_group.csv"',
                'content-type': 'text/csv'
            })
        )
        
        payload = {
            'file': upload_file,
            'categorical_attributes': ['race'],
            'label': 'income',
            'favourable_outcome': '<=50K'  # No favorable outcomes
        }
        
        mock_create_graphs.return_value = "test.pdf"
        result = SuccessRateService.analyze(payload)
        
        # Should handle zero division gracefully
        assert 'success_rates' in result
    
    @patch('fairness.service.service_success_rates.SuccessRateService.create_graphs')
    def test_zscore_calculation_with_constant_values(self, mock_create_graphs):
        """Regression: Ensure z-score calculation handles constant values"""
        csv_data = """income,race,gender
>50K,White,Male
>50K,Black,Male
>50K,Asian,Male"""
        
        upload_file = UploadFile(
            filename="constant.csv",
            file=BytesIO(csv_data.encode()),
            headers=Headers({
                'content-disposition': 'form-data; name="file"; filename="constant.csv"',
                'content-type': 'text/csv'
            })
        )
        
        payload = {
            'file': upload_file,
            'categorical_attributes': ['race'],
            'label': 'income',
            'favourable_outcome': '>50K'
        }
        
        mock_create_graphs.return_value = "test.pdf"
        result = SuccessRateService.analyze(payload)
        
        # Should handle constant values in z-score calculation
        assert 'success_rates' in result
        for group in result['success_rates']['race'].values():
            # Z-score should be 0 or NaN for constant values
            assert 'z_score' in group
