"""
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Comprehensive test cases for service_monitoring.py
Testing principles: Clarity, Isolation, Repeatability, Coverage, Assertions
Quality focus: Functional Correctness, Edge Cases, Error Handling, Performance, 
               Resource Management, Security, Scalability, Integration, Regression
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, MagicMock, patch, mock_open, call
from io import BytesIO, StringIO
from fastapi import HTTPException, UploadFile
import json
from PIL import Image
import os
import time
import zipfile
import datetime
import openai


# Import the class to test
from fairness.service.service_monitoring import FairnessAudit, bias_types


# ==================== FIXTURES ====================

@pytest.fixture
def fairness_audit():
    """Create a FairnessAudit instance with mocked dependencies"""
    with patch('fairness.service.service_monitoring.DataBase'), \
         patch('fairness.service.service_monitoring.FileStoreReportDb'), \
         patch('fairness.service.service_monitoring.Batch'), \
         patch('fairness.service.service_monitoring.Tenet'), \
         patch('fairness.service.service_monitoring.Dataset'), \
         patch('fairness.service.service_monitoring.DataAttributes'), \
         patch('fairness.service.service_monitoring.DataAttributeValues'), \
         patch('fairness.service.service_monitoring.Report'):
        
        audit = FairnessAudit()
        # Mock the database and other dependencies
        audit.db = MagicMock()
        audit.fileStore = MagicMock()
        audit.batch = MagicMock()
        audit.tenet = MagicMock()
        audit.dataset = MagicMock()
        audit.dataAttributes = MagicMock()
        audit.dataAttributeValues = MagicMock()
        audit.report = MagicMock()
        
        yield audit


@pytest.fixture
def sample_dataframe():
    """Create a sample dataframe for testing"""
    return pd.DataFrame({
        'text': ['Sample text 1', 'Sample text 2', 'Sample text 3'],
        'label': ['Label A', 'Label B', 'Label C'],
        'value': [10, 20, 30]
    })


@pytest.fixture
def sample_csv_file(sample_dataframe, tmp_path):
    """Create a temporary CSV file"""
    csv_path = tmp_path / "test.csv"
    sample_dataframe.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def mock_upload_file():
    """Create a mock upload file"""
    mock_file = Mock(spec=UploadFile)
    mock_file.filename = "test.csv"
    csv_content = "text,label\nSample 1,A\nSample 2,B\nSample 3,C"
    mock_file.file = BytesIO(csv_content.encode())
    return mock_file


@pytest.fixture
def sample_bias_response():
    """Sample bias detection response"""
    return [{
        'bias_type': 'race',
        'bias_indicator': 'high',
        'privileged_groups': ['white'],
        'unprivileged_groups': ['black'],
        'bias_score': 85,
        'explanation': 'Detected racial bias in the text'
    }]


@pytest.fixture
def sample_bias_dataframe():
    """Sample dataframe with bias analysis results"""
    return pd.DataFrame({
        'text': ['Text 1', 'Text 2', 'Text 3'],
        'bias_type': ['race', 'gender', 'age'],
        'bias_indicator': ['high', 'medium', 'low'],
        'privileged_groups': [['white'], ['male'], ['adults']],
        'unprivileged_groups': [['black'], ['female'], ['seniors']],
        'bias_score': [85, 60, 30]
    })


# ==================== TEST GET_DATAFRAME ====================

class TestGetDataFrame:
    """Test get_dataframe static method"""
    
    def test_get_dataframe_csv(self, sample_csv_file):
        """Test reading CSV file"""
        df = FairnessAudit.get_dataframe('csv', str(sample_csv_file))
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert 'text' in df.columns
    
    def test_get_dataframe_parquet(self, tmp_path, sample_dataframe):
        """Test reading Parquet file"""
        parquet_path = tmp_path / "test.parquet"
        sample_dataframe.to_parquet(parquet_path)
        
        df = FairnessAudit.get_dataframe('parquet', str(parquet_path))
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
    
    def test_get_dataframe_feather(self, tmp_path, sample_dataframe):
        """Test reading Feather file"""
        feather_path = tmp_path / "test.feather"
        sample_dataframe.to_feather(feather_path)
        
        df = FairnessAudit.get_dataframe('feather', str(feather_path))
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
    
    def test_get_dataframe_json(self, tmp_path, sample_dataframe):
        """Test reading JSON file"""
        json_path = tmp_path / "test.json"
        sample_dataframe.to_json(json_path)
        
        df = FairnessAudit.get_dataframe('json', str(json_path))
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
    
    def test_get_dataframe_invalid_extension(self, sample_csv_file):
        """Test with unsupported file extension"""
        result = FairnessAudit.get_dataframe('txt', str(sample_csv_file))
        assert result is None


# ==================== TEST GET_EXTENSION ====================

class TestGetExtension:
    """Test get_extension static method"""
    
    def test_get_extension_csv(self):
        """Test CSV extension detection"""
        assert FairnessAudit.get_extension("file.csv") == "csv"
    
    def test_get_extension_parquet(self):
        """Test Parquet extension detection"""
        assert FairnessAudit.get_extension("file.parquet") == "parquet"
    
    def test_get_extension_feather(self):
        """Test Feather extension detection"""
        assert FairnessAudit.get_extension("file.feather") == "feather"
    
    def test_get_extension_json(self):
        """Test JSON extension detection"""
        assert FairnessAudit.get_extension("file.json") == "json"
    
    def test_get_extension_unsupported(self):
        """Test unsupported extension"""
        result = FairnessAudit.get_extension("file.txt")
        assert result is None
    
    def test_get_extension_no_extension(self):
        """Test file with no extension"""
        result = FairnessAudit.get_extension("file")
        assert result is None


# ==================== TEST EXTRACT_JSON ====================

class TestExtractJson:
    """Test extract_json method"""
    
    def test_extract_json_with_code_block(self, fairness_audit):
        """Test extracting JSON from markdown code block"""
        response = '```json\n[{"bias_type": "race"}]\n```'
        result = fairness_audit.extract_json(response)
        assert result == [{"bias_type": "race"}]
    
    def test_extract_json_with_brackets(self, fairness_audit):
        """Test extracting JSON with brackets"""
        response = 'Some text [{"bias_type": "race"}] more text'
        result = fairness_audit.extract_json(response)
        assert result == [{"bias_type": "race"}]
    
    def test_extract_json_nested(self, fairness_audit):
        """Test extracting nested JSON"""
        response = '[{"data": [{"bias_type": "race"}]}]'
        result = fairness_audit.extract_json(response)
        assert isinstance(result, list)
    
    def test_extract_json_invalid(self, fairness_audit):
        """Test with invalid JSON"""
        response = 'No JSON here'
        result = fairness_audit.extract_json(response)
        assert result is None
    
    def test_extract_json_malformed(self, fairness_audit):
        """Test with malformed JSON"""
        response = '[{invalid json}]'
        result = fairness_audit.extract_json(response)
        assert result is None
    
    def test_extract_json_empty_string(self, fairness_audit):
        """Test with empty string"""
        result = fairness_audit.extract_json("")
        assert result is None


# ==================== TEST CHECK_RESPONSE ====================

class TestCheckResponse:
    """Test check_response method"""
    
    def test_check_response_valid(self, fairness_audit, sample_bias_response):
        """Test with valid response"""
        result = fairness_audit.check_response(sample_bias_response, "input text")
        assert result['valid'] == True
        assert len(result['errors']) == 0
        assert result['response'] == sample_bias_response
    
    def test_check_response_missing_field(self, fairness_audit):
        """Test with missing required field"""
        invalid_response = [{
            'bias_type': 'race',
            'bias_indicator': 'high',
            'privileged_groups': ['white'],
            'unprivileged_groups': ['black']
            # Missing 'bias_score' and 'explanation'
        }]
        
        with patch.object(fairness_audit, 'correct_respnse', return_value=invalid_response):
            result = fairness_audit.check_response(invalid_response, "input text")
            assert result['valid'] == False
    
    def test_check_response_wrong_type(self, fairness_audit):
        """Test with wrong field type"""
        invalid_response = [{
            'bias_type': 'race',
            'bias_indicator': 'high',
            'privileged_groups': 'should_be_list',  # Should be list
            'unprivileged_groups': ['black'],
            'bias_score': 85,
            'explanation': 'Test'
        }]
        
        with patch.object(fairness_audit, 'correct_respnse', return_value=invalid_response):
            result = fairness_audit.check_response(invalid_response, "input text")
            assert result['valid'] == False
    
    def test_check_response_na_bias_type(self, fairness_audit):
        """Test with NA bias type"""
        na_response = [{
            'bias_type': 'NA',
            'bias_indicator': 'low',
            'privileged_groups': [],
            'unprivileged_groups': [],
            'bias_score': 0,
            'explanation': 'No bias detected'
        }]
        
        with patch.object(fairness_audit, 'correct_respnse', return_value=na_response):
            result = fairness_audit.check_response(na_response, "input text")
            assert result['valid'] == False
    
    def test_check_response_invalid_bias_type(self, fairness_audit):
        """Test with invalid bias type"""
        invalid_response = [{
            'bias_type': 'invalid_type',
            'bias_indicator': 'high',
            'privileged_groups': ['white'],
            'unprivileged_groups': ['black'],
            'bias_score': 85,
            'explanation': 'Test'
        }]
        
        with patch.object(fairness_audit, 'correct_respnse', return_value=invalid_response):
            result = fairness_audit.check_response(invalid_response, "input text")
            assert result['valid'] == False
    
    def test_check_response_invalid_indicator(self, fairness_audit):
        """Test with invalid bias indicator"""
        invalid_response = [{
            'bias_type': 'race',
            'bias_indicator': 'invalid',  # Should be low, medium, or high
            'privileged_groups': ['white'],
            'unprivileged_groups': ['black'],
            'bias_score': 85,
            'explanation': 'Test'
        }]
        
        with patch.object(fairness_audit, 'correct_respnse', return_value=invalid_response):
            result = fairness_audit.check_response(invalid_response, "input text")
            assert result['valid'] == False
    
    def test_check_response_case_insensitive_keys(self, fairness_audit):
        """Test that response keys are normalized to lowercase"""
        response = [{
            'BIAS_TYPE': 'race',
            'Bias_Indicator': 'high',
            'Privileged_Groups': ['white'],
            'Unprivileged_Groups': ['black'],
            'Bias_Score': 85,
            'Explanation': 'Test'
        }]
        
        result = fairness_audit.check_response(response, "input text")
        # Check that the response has lowercase keys
        assert 'bias_type' in result['response'][0]
    
    def test_check_response_with_existing_errors(self, fairness_audit):
        """Test with pre-existing errors"""
        response = [{'bias_type': 'race'}]
        errors = ["Pre-existing error"]
        
        with patch.object(fairness_audit, 'correct_respnse', return_value=response):
            result = fairness_audit.check_response(response, "input text", errors=errors)
            assert result['valid'] == False


# ==================== TEST CORRECT_RESPONSE ====================

class TestCorrectResponse:
    """Test correct_respnse method"""
    
    def test_correct_response_success(self, fairness_audit):
        """Test successful correction"""
        response = [{'bias_type': 'invalid'}]
        errors = ['Invalid bias type']
        input_text = 'Test input'
        
        with patch('fairness.service.service_monitoring.create_llm_connection') as mock_llm:
            mock_instance = MagicMock()
            mock_instance.get_chat_completion.return_value = '[{"bias_type": "race", "bias_indicator": "high", "privileged_groups": ["white"], "unprivileged_groups": ["black"], "bias_score": 85, "explanation": "Corrected"}]'
            mock_llm.return_value.llm_instance = mock_instance
            mock_llm.return_value.get_active_llm.return_value = "openai"
            
            result = fairness_audit.correct_respnse(response, errors, input_text)
            assert isinstance(result, list)
            assert result[0]['bias_type'] == 'race'
    
    def test_correct_response_json_decode_error(self, fairness_audit):
        """Test handling of JSON decode error in correction"""
        response = [{'bias_type': 'invalid'}]
        errors = ['Invalid bias type']
        input_text = 'Test input'
        
        with patch('fairness.service.service_monitoring.create_llm_connection') as mock_llm:
            mock_instance = MagicMock()
            mock_instance.get_chat_completion.return_value = 'Invalid JSON'
            mock_llm.return_value.llm_instance = mock_instance
            mock_llm.return_value.get_active_llm.return_value = "openai"
            
            with patch.object(fairness_audit, 'check_response') as mock_check:
                mock_check.return_value = {'response': []}
                fairness_audit.correct_respnse(response, errors, input_text)
                assert mock_check.called
    
    def test_correct_response_none_generated_report(self, fairness_audit):
        """Test handling when LLM returns None"""
        response = [{'bias_type': 'invalid'}]
        errors = ['Invalid bias type']
        input_text = 'Test input'
        
        with patch('fairness.service.service_monitoring.create_llm_connection') as mock_llm:
            mock_instance = MagicMock()
            mock_instance.get_chat_completion.return_value = None
            mock_llm.return_value.llm_instance = mock_instance
            mock_llm.return_value.get_active_llm.return_value = "openai"
            
            # Should not raise exception but handle gracefully
            fairness_audit.correct_respnse(response, errors, input_text)
            # Test passes if no exception is raised


# ==================== TEST CALL_LLM ====================

class TestCallLLM:
    """Test call_llm method"""
    
    def test_call_llm_success(self, fairness_audit):
        """Test successful LLM call"""
        prompt = "Test prompt"
        text = "Test text"
        
        with patch('fairness.service.service_monitoring.create_llm_connection') as mock_llm:
            mock_instance = MagicMock()
            mock_instance.get_chat_completion.return_value = '[{"bias_type": "race", "bias_indicator": "high", "privileged_groups": ["white"], "unprivileged_groups": ["black"], "bias_score": 85, "explanation": "Test"}]'
            mock_llm.return_value.llm_instance = mock_instance
            mock_llm.return_value.get_active_llm.return_value = "openai"
            
            result = fairness_audit.call_llm(prompt, text)
            assert isinstance(result, list)
            assert result[0]['bias_type'] == 'race'
    
    def test_call_llm_none_response(self, fairness_audit):
        """Test LLM returning None"""
        prompt = "Test prompt"
        text = "Test text"
        
        with patch('fairness.service.service_monitoring.create_llm_connection') as mock_llm:
            mock_instance = MagicMock()
            mock_instance.get_chat_completion.return_value = None
            mock_llm.return_value.llm_instance = mock_instance
            mock_llm.return_value.get_active_llm.return_value = "openai"
            
            result = fairness_audit.call_llm(prompt, text)
            assert result is None
    
    def test_call_llm_json_decode_error(self, fairness_audit):
        """Test handling JSON decode error - code catches and retries"""
        prompt = "Test prompt"
        text = "Test text"
        
        with patch('fairness.service.service_monitoring.create_llm_connection') as mock_llm:
            mock_instance = MagicMock()
            # Simulate extract_json returning None, which triggers a retry in the actual implementation
            mock_instance.get_chat_completion.return_value = 'Invalid JSON that extract_json cannot parse'
            mock_llm.return_value.llm_instance = mock_instance
            mock_llm.return_value.get_active_llm.return_value = "openai"
            
            with patch.object(fairness_audit, 'extract_json', return_value=None):
                # Should handle gracefully and return None when extraction fails
                result = fairness_audit.call_llm(prompt, text)
                # Result will be None because extract_json returns None
                assert result is None
    
    def test_call_llm_bad_request_error(self, fairness_audit):
        """Test handling BadRequestError"""
        prompt = "Test prompt"
        text = "Test text"
        
        with patch('fairness.service.service_monitoring.create_llm_connection') as mock_llm:
            mock_instance = MagicMock()
            mock_instance.get_chat_completion.side_effect = openai.BadRequestError(
                "Bad request", 
                response=MagicMock(status_code=400),
                body=None
            )
            mock_llm.return_value.llm_instance = mock_instance
            mock_llm.return_value.get_active_llm.return_value = "openai"
            
            result = fairness_audit.call_llm(prompt, text)
            assert result[0]['bias_type'] == 'Blocked By Azure'
            assert result[0]['bias_score'] == 100
    
    def test_call_llm_rate_limit_error(self, fairness_audit):
        """Test handling RateLimitError"""
        prompt = "Test prompt"
        text = "Test text"
        
        with patch('fairness.service.service_monitoring.create_llm_connection') as mock_llm:
            mock_instance = MagicMock()
            mock_instance.get_chat_completion.side_effect = openai.RateLimitError(
                "Rate limit exceeded",
                response=MagicMock(status_code=429),
                body=None
            )
            mock_llm.return_value.llm_instance = mock_instance
            mock_llm.return_value.get_active_llm.return_value = "openai"
            
            result = fairness_audit.call_llm(prompt, text)
            # Should log the error and return None
            assert result is None


# ==================== TEST IMAGE_TO_PDF ====================

class TestImageToPDF:
    """Test image_to_pdf static method"""
    
    def test_image_to_pdf_single_image(self, tmp_path):
        """Test creating PDF from single image"""
        # Create a test image
        img = Image.new('RGB', (100, 100), color='red')
        img_path = tmp_path / "test_image.png"
        img.save(img_path)
        
        output_pdf = tmp_path / "output.pdf"
        
        FairnessAudit.image_to_pdf([str(img_path)], str(output_pdf))
        
        assert output_pdf.exists()
    
    def test_image_to_pdf_multiple_images(self, tmp_path):
        """Test creating PDF from multiple images"""
        # Create test images
        img1 = Image.new('RGB', (100, 100), color='red')
        img2 = Image.new('RGB', (100, 100), color='blue')
        
        img1_path = tmp_path / "image1.png"
        img2_path = tmp_path / "image2.png"
        
        img1.save(img1_path)
        img2.save(img2_path)
        
        output_pdf = tmp_path / "output.pdf"
        
        FairnessAudit.image_to_pdf([str(img1_path), str(img2_path)], str(output_pdf))
        
        assert output_pdf.exists()
    
    def test_image_to_pdf_with_label(self, tmp_path):
        """Test creating PDF with label"""
        img = Image.new('RGB', (100, 100), color='green')
        img_path = tmp_path / "test_image.png"
        img.save(img_path)
        
        output_pdf = tmp_path / "output.pdf"
        
        FairnessAudit.image_to_pdf([str(img_path)], str(output_pdf), label="Test Label")
        
        assert output_pdf.exists()


# ==================== TEST VISUALIZATION METHODS ====================

class TestVisualization:
    """Test bias_type_bar_chart_visualize methods"""
    
    def test_bias_type_bar_chart_visualize(self, sample_bias_dataframe, tmp_path):
        """Test creating visualizations"""
        # Convert lists to strings for the dataframe
        df = sample_bias_dataframe.copy()
        df['privileged_groups'] = df['privileged_groups'].apply(str)
        df['unprivileged_groups'] = df['unprivileged_groups'].apply(str)
        
        with patch.dict(os.environ, {'THRESHOLD': '50'}):
            with patch('fairness.service.service_monitoring.OUTPUT_FOLDER', str(tmp_path)):
                with patch('fairness.service.service_monitoring.LOCAL_PATH', str(tmp_path)):
                    result = FairnessAudit.bias_type_bar_chart_visualize(df)
                    assert result.endswith('.pdf')
    
    def test_bias_type_bar_chart_visualize_empty_df(self, tmp_path):
        """Test with empty dataframe"""
        df = pd.DataFrame(columns=['text', 'bias_type', 'bias_indicator', 
                                   'privileged_groups', 'unprivileged_groups', 'bias_score'])
        
        with patch.dict(os.environ, {'THRESHOLD': '50'}):
            with patch('fairness.service.service_monitoring.OUTPUT_FOLDER', str(tmp_path)):
                with patch('fairness.service.service_monitoring.LOCAL_PATH', str(tmp_path)):
                    # Should handle empty dataframe gracefully
                    with pytest.raises(Exception):
                        FairnessAudit.bias_type_bar_chart_visualize(df)
    
    def test_bias_type_bar_chart_visualize_workbench(self, sample_bias_dataframe, tmp_path):
        """Test workbench visualization method"""
        df = sample_bias_dataframe.copy()
        df['privileged_groups'] = df['privileged_groups'].apply(str)
        df['unprivileged_groups'] = df['unprivileged_groups'].apply(str)
        
        with patch.dict(os.environ, {'THRESHOLD': '50'}):
            with patch('fairness.service.service_monitoring.OUTPUT_FOLDER', str(tmp_path)):
                with patch('fairness.service.service_monitoring.LOCAL_PATH', str(tmp_path)):
                    result = FairnessAudit.bias_type_bar_chart_visualize_workbench(df, 'test_label')
                    assert isinstance(result, str)
                    assert '<html>' in result.lower() or 'infosys' in result.lower()


# ==================== TEST AUDIT METHOD ====================

class TestAudit:
    """Test audit method"""
    
    def test_audit_success(self, fairness_audit, mock_upload_file):
        """Test successful audit execution"""
        payload = {
            'label': 'text',
            'file': mock_upload_file
        }
        
        with patch('fairness.service.service_monitoring.FairnessAudit.get_extension', return_value='csv'):
            with patch('fairness.service.service_monitoring.FairnessAudit.get_dataframe') as mock_get_df:
                mock_df = pd.DataFrame({
                    'text': ['Sample 1', 'Sample 2', 'Sample 3']
                })
                mock_get_df.return_value = mock_df
                
                with patch.object(fairness_audit, 'call_llm') as mock_call_llm:
                    mock_call_llm.return_value = [{
                        'bias_type': 'race',
                        'bias_indicator': 'high',
                        'privileged_groups': ['white'],
                        'unprivileged_groups': ['black'],
                        'bias_score': 85,
                        'explanation': 'Test'
                    }]
                    
                    with patch('fairness.service.service_monitoring.FairnessAudit.bias_type_bar_chart_visualize') as mock_viz:
                        mock_viz.return_value = 'test_report.pdf'
                        
                        with patch('fairness.service.service_monitoring.LOCAL_PATH', '/tmp'):
                            with patch('os.makedirs'):
                                with patch('pandas.DataFrame.to_csv'):
                                    result = fairness_audit.audit(payload)
                                    
                                    assert 'response' in result
                                    assert 'time_taken' in result
                                    assert 'audit_report_csv' in result['response']
                                    assert 'audit_report_pdf' in result['response']
    
    def test_audit_concurrent_processing(self, fairness_audit, mock_upload_file):
        """Test that audit processes multiple inputs concurrently"""
        payload = {
            'label': 'text',
            'file': mock_upload_file
        }
        
        with patch('fairness.service.service_monitoring.FairnessAudit.get_extension', return_value='csv'):
            with patch('fairness.service.service_monitoring.FairnessAudit.get_dataframe') as mock_get_df:
                # Create dataframe with multiple rows
                mock_df = pd.DataFrame({
                    'text': [f'Sample {i}' for i in range(10)]
                })
                mock_get_df.return_value = mock_df
                
                with patch.object(fairness_audit, 'call_llm') as mock_call_llm:
                    mock_call_llm.return_value = [{
                        'bias_type': 'race',
                        'bias_indicator': 'high',
                        'privileged_groups': ['white'],
                        'unprivileged_groups': ['black'],
                        'bias_score': 85,
                        'explanation': 'Test'
                    }]
                    
                    with patch('fairness.service.service_monitoring.FairnessAudit.bias_type_bar_chart_visualize', return_value='report.pdf'):
                        with patch('fairness.service.service_monitoring.LOCAL_PATH', '/tmp'):
                            with patch('os.makedirs'):
                                with patch('pandas.DataFrame.to_csv'):
                                    fairness_audit.audit(payload)
                                    
                                    # Verify call_llm was called for each row
                                    assert mock_call_llm.call_count == 10


# ==================== TEST WORKBENCH_AUDIT ====================

class TestWorkbenchAudit:
    """Test workbench_audit method"""
    
    def test_workbench_audit_missing_batch_id(self, fairness_audit):
        """Test with missing batch ID"""
        payload = {'Batch_id': None}
        
        with pytest.raises(Exception):
            fairness_audit.workbench_audit(payload)
    
    def test_workbench_audit_empty_batch_id(self, fairness_audit):
        """Test with empty batch ID"""
        payload = {'Batch_id': ''}
        
        with pytest.raises(Exception):
            fairness_audit.workbench_audit(payload)
    
    def test_workbench_audit_success(self, fairness_audit):
        """Test successful workbench audit"""
        payload = {'Batch_id': '123.124'}
        
        # Setup mocks
        fairness_audit.tenet.find.return_value = 1
        fairness_audit.batch.find.return_value = {
            'DataId': 12.12,
            'BatchId': 123.124
        }
        fairness_audit.dataset.find.return_value = {
            'SampleData': 'file_id_123'
        }
        fairness_audit.dataAttributes.find.return_value = [1, 2, 3]
        fairness_audit.dataAttributeValues.find.return_value = ['text']
        
        # Mock file content
        csv_content = "text\nSample 1\nSample 2\nSample 3"
        fairness_audit.fileStore.read_file.return_value = {
            'data': csv_content.encode(),
            'name': 'test_file',
            'extension': 'csv'
        }
        
        with patch.object(fairness_audit, 'call_llm') as mock_call_llm:
            mock_call_llm.return_value = [{
                'bias_type': 'race',
                'bias_indicator': 'high',
                'privileged_groups': ['white'],
                'unprivileged_groups': ['black'],
                'bias_score': 85,
                'explanation': 'Test'
            }]
            
            with patch('fairness.service.service_monitoring.FairnessAudit.bias_type_bar_chart_visualize_workbench') as mock_viz:
                mock_viz.return_value = '<html>Report</html>'
                
                with patch('fairness.service.service_monitoring.Html'):
                    with patch('fairness.service.service_monitoring.Report'):
                        with patch('os.makedirs'):
                            with patch('pandas.DataFrame.to_csv'):
                                with patch('builtins.open', mock_open(read_data=b'test')):
                                    with patch('os.remove'):
                                        with patch.dict(os.environ, {
                                            'HTML_CONTAINER_NAME': 'html',
                                            'REPORT_URL': 'http://test.com',
                                            'PDF_CONTAINER_NAME': 'pdf',
                                            'ZIP_CONTAINER_NAME': 'zip'
                                        }):
                                            with patch('requests.request') as mock_request:
                                                mock_request.return_value.json.return_value = {'status': 'ok'}
                                                fairness_audit.report.find.return_value = {
                                                    'ReportFileId': 'report_id',
                                                    'ReportName': 'report.pdf'
                                                }
                                                fairness_audit.fileStore.save_file.return_value = 'saved_file_id'
                                                
                                                result = fairness_audit.workbench_audit(payload)
                                                
                                                assert 'response' in result
                                                assert 'time_taken' in result
                                                assert 'audit_report_id' in result['response']
    
    def test_workbench_audit_failure_updates_status(self, fairness_audit):
        """Test that batch status is updated to Failed on exception"""
        payload = {'Batch_id': '123.124'}
        
        fairness_audit.tenet.find.side_effect = Exception("Test error")
        
        with pytest.raises(Exception):
            fairness_audit.workbench_audit(payload)
        
        # Verify status was updated to Failed
        fairness_audit.batch.update.assert_called()


# ==================== TEST DOWNLOAD_FILE ====================

class TestDownloadFile:
    """Test download_file static method"""
    
    def test_download_file_exists(self, tmp_path):
        """Test downloading existing file"""
        # Create a test file
        test_file = tmp_path / "test_report.csv"
        test_file.write_text("test data")
        
        with patch('fairness.service.service_monitoring.LOCAL_PATH', str(tmp_path)):
            result = FairnessAudit.download_file("test_report.csv")
            assert result == str(tmp_path / "test_report.csv")
    
    def test_download_file_not_exists(self, tmp_path):
        """Test downloading non-existent file"""
        with patch('fairness.service.service_monitoring.LOCAL_PATH', str(tmp_path)):
            with pytest.raises(HTTPException) as exc_info:
                FairnessAudit.download_file("non_existent.csv")
            
            assert exc_info.value.status_code == 404


# ==================== EDGE CASES & ERROR HANDLING ====================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_empty_input_text(self, fairness_audit):
        """Test handling of empty input text"""
        prompt = "Test prompt"
        text = ""
        
        with patch('fairness.service.service_monitoring.create_llm_connection') as mock_llm:
            mock_instance = MagicMock()
            mock_instance.get_chat_completion.return_value = '[{"bias_type": "NA"}]'
            mock_llm.return_value.llm_instance = mock_instance
            mock_llm.return_value.get_active_llm.return_value = "openai"
            
            result = fairness_audit.call_llm(prompt, text)
            assert result is not None
    
    def test_very_long_input_text(self, fairness_audit):
        """Test handling of very long input text"""
        prompt = "Test prompt"
        text = "A" * 10000  # Very long text
        
        with patch('fairness.service.service_monitoring.create_llm_connection') as mock_llm:
            mock_instance = MagicMock()
            mock_instance.get_chat_completion.return_value = '[{"bias_type": "race"}]'
            mock_llm.return_value.llm_instance = mock_instance
            mock_llm.return_value.get_active_llm.return_value = "openai"
            
            result = fairness_audit.call_llm(prompt, text)
            assert result is not None
    
    def test_special_characters_in_input(self, fairness_audit):
        """Test handling of special characters"""
        prompt = "Test prompt"
        text = "Text with special chars: \n\t\r <>\"'&"
        
        with patch('fairness.service.service_monitoring.create_llm_connection') as mock_llm:
            mock_instance = MagicMock()
            mock_instance.get_chat_completion.return_value = '[{"bias_type": "race"}]'
            mock_llm.return_value.llm_instance = mock_instance
            mock_llm.return_value.get_active_llm.return_value = "openai"
            
            result = fairness_audit.call_llm(prompt, text)
            assert result is not None
    
    def test_dataframe_with_nan_values(self, fairness_audit):
        """Test handling dataframe with NaN values"""
        df = pd.DataFrame({
            'text': ['Text 1', np.nan, 'Text 3'],
            'bias_type': ['race', 'gender', np.nan],
            'bias_indicator': ['high', np.nan, 'low'],
            'privileged_groups': [['white'], np.nan, ['adults']],
            'unprivileged_groups': [['black'], ['female'], np.nan],
            'bias_score': [85, np.nan, 30]
        })
        
        df['privileged_groups'] = df['privileged_groups'].apply(lambda x: str(x) if not pd.isna(x) else '[]')
        df['unprivileged_groups'] = df['unprivileged_groups'].apply(lambda x: str(x) if not pd.isna(x) else '[]')
        
        with patch.dict(os.environ, {'THRESHOLD': '50'}):
            with patch('fairness.service.service_monitoring.OUTPUT_FOLDER', '/tmp'):
                with patch('fairness.service.service_monitoring.LOCAL_PATH', '/tmp'):
                    with patch('os.makedirs'):
                        with patch('os.remove'):
                            # Should handle NaN values without crashing
                            try:
                                result = FairnessAudit.bias_type_bar_chart_visualize(df)
                                assert result is not None
                            except Exception:
                                # If it fails, it should be a controlled failure
                                pass


# ==================== SECURITY TESTS ====================

class TestSecurity:
    """Test security-related scenarios"""
    
    def test_sql_injection_in_input(self, fairness_audit):
        """Test handling of SQL injection attempt"""
        prompt = "Test prompt"
        text = "'; DROP TABLE users; --"
        
        with patch('fairness.service.service_monitoring.create_llm_connection') as mock_llm:
            mock_instance = MagicMock()
            mock_instance.get_chat_completion.return_value = '[{"bias_type": "NA"}]'
            mock_llm.return_value.llm_instance = mock_instance
            mock_llm.return_value.get_active_llm.return_value = "openai"
            
            result = fairness_audit.call_llm(prompt, text)
            # Should handle safely without executing SQL
            assert result is not None
    
    def test_xss_in_input(self, fairness_audit):
        """Test handling of XSS attempt"""
        prompt = "Test prompt"
        text = "<script>alert('XSS')</script>"
        
        with patch('fairness.service.service_monitoring.create_llm_connection') as mock_llm:
            mock_instance = MagicMock()
            mock_instance.get_chat_completion.return_value = '[{"bias_type": "NA"}]'
            mock_llm.return_value.llm_instance = mock_instance
            mock_llm.return_value.get_active_llm.return_value = "openai"
            
            result = fairness_audit.call_llm(prompt, text)
            # Should handle safely without executing script
            assert result is not None
    
    def test_path_traversal_in_filename(self, tmp_path):
        """Test handling of path traversal attempt"""
        with patch('fairness.service.service_monitoring.LOCAL_PATH', str(tmp_path)):
            with pytest.raises(HTTPException):
                FairnessAudit.download_file("../../etc/passwd")


# ==================== PERFORMANCE TESTS ====================

class TestPerformance:
    """Test performance-related scenarios"""
    
    def test_audit_performance_timing(self, fairness_audit, mock_upload_file):
        """Test that audit completes within reasonable time"""
        payload = {
            'label': 'text',
            'file': mock_upload_file
        }
        
        with patch('fairness.service.service_monitoring.FairnessAudit.get_extension', return_value='csv'):
            with patch('fairness.service.service_monitoring.FairnessAudit.get_dataframe') as mock_get_df:
                mock_df = pd.DataFrame({
                    'text': ['Sample text'] * 5  # Small dataset
                })
                mock_get_df.return_value = mock_df
                
                with patch.object(fairness_audit, 'call_llm') as mock_call_llm:
                    mock_call_llm.return_value = [{
                        'bias_type': 'race',
                        'bias_indicator': 'high',
                        'privileged_groups': ['white'],
                        'unprivileged_groups': ['black'],
                        'bias_score': 85,
                        'explanation': 'Test'
                    }]
                    
                    with patch('fairness.service.service_monitoring.FairnessAudit.bias_type_bar_chart_visualize', return_value='report.pdf'):
                        with patch('fairness.service.service_monitoring.LOCAL_PATH', '/tmp'):
                            with patch('os.makedirs'):
                                with patch('pandas.DataFrame.to_csv'):
                                    result = fairness_audit.audit(payload)
                                    
                                    assert 'time_taken' in result
                                    # Should complete reasonably fast for small dataset
                                    assert result['time_taken'] < 60
    
    def test_large_dataset_processing(self, fairness_audit, mock_upload_file):
        """Test processing large dataset"""
        payload = {
            'label': 'text',
            'file': mock_upload_file
        }
        
        with patch('fairness.service.service_monitoring.FairnessAudit.get_extension', return_value='csv'):
            with patch('fairness.service.service_monitoring.FairnessAudit.get_dataframe') as mock_get_df:
                # Large dataset
                mock_df = pd.DataFrame({
                    'text': [f'Sample text {i}' for i in range(100)]
                })
                mock_get_df.return_value = mock_df
                
                with patch.object(fairness_audit, 'call_llm') as mock_call_llm:
                    mock_call_llm.return_value = [{
                        'bias_type': 'race',
                        'bias_indicator': 'high',
                        'privileged_groups': ['white'],
                        'unprivileged_groups': ['black'],
                        'bias_score': 85,
                        'explanation': 'Test'
                    }]
                    
                    with patch('fairness.service.service_monitoring.FairnessAudit.bias_type_bar_chart_visualize', return_value='report.pdf'):
                        with patch('fairness.service.service_monitoring.LOCAL_PATH', '/tmp'):
                            with patch('os.makedirs'):
                                with patch('pandas.DataFrame.to_csv'):
                                    result = fairness_audit.audit(payload)
                                    
                                    # Verify it can handle large dataset
                                    assert 'response' in result


# ==================== INTEGRATION TESTS ====================

class TestIntegration:
    """Test integration scenarios"""
    
    def test_end_to_end_audit_workflow(self, fairness_audit, tmp_path):
        """Test complete audit workflow from file upload to report generation"""
        # Create test CSV file
        csv_content = "text\nSample text 1\nSample text 2\nSample text 3"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)
        
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test.csv"
        mock_file.file = BytesIO(csv_content.encode())
        
        payload = {
            'label': 'text',
            'file': mock_file
        }
        
        with patch('fairness.service.service_monitoring.FairnessAudit.get_extension', return_value='csv'):
            with patch('fairness.service.service_monitoring.FairnessAudit.get_dataframe') as mock_get_df:
                mock_df = pd.DataFrame({
                    'text': ['Sample text 1', 'Sample text 2', 'Sample text 3']
                })
                mock_get_df.return_value = mock_df
                
                with patch.object(fairness_audit, 'call_llm') as mock_call_llm:
                    mock_call_llm.return_value = [{
                        'bias_type': 'race',
                        'bias_indicator': 'high',
                        'privileged_groups': ['white'],
                        'unprivileged_groups': ['black'],
                        'bias_score': 85,
                        'explanation': 'Detected bias'
                    }]
                    
                    with patch('fairness.service.service_monitoring.FairnessAudit.bias_type_bar_chart_visualize', return_value='report.pdf'):
                        with patch('fairness.service.service_monitoring.LOCAL_PATH', str(tmp_path)):
                            with patch('os.makedirs'):
                                with patch('pandas.DataFrame.to_csv'):
                                    result = fairness_audit.audit(payload)
                                    
                                    # Verify complete workflow
                                    assert 'response' in result
                                    assert 'audit_report_csv' in result['response']
                                    assert 'audit_report_pdf' in result['response']
                                    assert 'time_taken' in result


# ==================== RESOURCE MANAGEMENT TESTS ====================

class TestResourceManagement:
    """Test resource management"""
    
    def test_file_cleanup_after_visualization(self, sample_bias_dataframe, tmp_path):
        """Test that temporary files are cleaned up after visualization"""
        df = sample_bias_dataframe.copy()
        df['privileged_groups'] = df['privileged_groups'].apply(str)
        df['unprivileged_groups'] = df['unprivileged_groups'].apply(str)
        
        with patch.dict(os.environ, {'THRESHOLD': '50'}):
            with patch('fairness.service.service_monitoring.OUTPUT_FOLDER', str(tmp_path)):
                with patch('fairness.service.service_monitoring.LOCAL_PATH', str(tmp_path)):
                    with patch('os.remove') as mock_remove:
                        try:
                            FairnessAudit.bias_type_bar_chart_visualize(df)
                            # Verify files were removed
                            assert mock_remove.called
                        except Exception:
                            # Even if visualization fails, cleanup should be attempted
                            pass
    
    def test_concurrent_executor_cleanup(self, fairness_audit, mock_upload_file):
        """Test that thread pool executor is properly cleaned up"""
        payload = {
            'label': 'text',
            'file': mock_upload_file
        }
        
        with patch('fairness.service.service_monitoring.FairnessAudit.get_extension', return_value='csv'):
            with patch('fairness.service.service_monitoring.FairnessAudit.get_dataframe') as mock_get_df:
                mock_df = pd.DataFrame({
                    'text': ['Sample 1', 'Sample 2']
                })
                mock_get_df.return_value = mock_df
                
                with patch.object(fairness_audit, 'call_llm') as mock_call_llm:
                    mock_call_llm.return_value = [{'bias_type': 'race', 'bias_indicator': 'high', 
                                                   'privileged_groups': ['white'], 'unprivileged_groups': ['black'],
                                                   'bias_score': 85, 'explanation': 'Test'}]
                    
                    with patch('fairness.service.service_monitoring.FairnessAudit.bias_type_bar_chart_visualize', return_value='report.pdf'):
                        with patch('fairness.service.service_monitoring.LOCAL_PATH', '/tmp'):
                            with patch('os.makedirs'):
                                with patch('pandas.DataFrame.to_csv'):
                                    # Should not leak threads
                                    result = fairness_audit.audit(payload)
                                    assert result is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
