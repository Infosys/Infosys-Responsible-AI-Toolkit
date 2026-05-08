"""
Tests all methods in responsible_ai_image_explain.py with proper context setup
"""

import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock, Mock
from contextvars import ContextVar

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from image_explain.service.responsible_ai_image_explain import ImageExplain
from image_explain.config.logger import request_id_var, CustomLogger
import openai

# Setup request_id_var for tests
request_id_var.set('test-request-id-123')


class TestImageExplainPromptBasedAnalysis:
    """Comprehensive tests for prompt_based_analysis method"""
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    @patch('image_explain.service.responsible_ai_image_explain.Prompt')
    def test_prompt_based_analysis_with_gpt_success(self, mock_prompt, mock_azure):
        """Test successful prompt-based analysis with GPT evaluator"""
        # Setup mocks
        mock_azure_instance = MagicMock()
        mock_response_data = {
            'image_description': 'A beautiful sunset',
            'style': 'Landscape Photography',
            'watermark': 'None'
        }
        mock_azure_instance.generate.return_value = json.dumps(mock_response_data)
        mock_azure.return_value = mock_azure_instance
        mock_prompt.image_analyze_prompt.return_value = "Test prompt"
        
        # Execute
        result = ImageExplain.prompt_based_analysis(
            mime_type='image/jpeg',
            image='base64_encoded_image_data',
            prompt='test',
            evaluator='GPT_4o'
        )
        
        # Assert
        assert result == mock_response_data
        mock_azure_instance.generate.assert_called_once()
    
    @patch('image_explain.service.responsible_ai_image_explain.Gemini')
    @patch('image_explain.service.responsible_ai_image_explain.Prompt')
    def test_prompt_based_analysis_with_gemini_success(self, mock_prompt, mock_gemini):
        """Test successful prompt-based analysis with Gemini evaluator"""
        # Setup mocks
        mock_gemini_instance = MagicMock()
        mock_response_data = {'result': 'Analysis complete'}
        mock_gemini_instance.generate.return_value = json.dumps(mock_response_data)
        mock_gemini.return_value = mock_gemini_instance
        mock_prompt.image_analyze_prompt.return_value = "Test prompt"
        
        # Execute
        result = ImageExplain.prompt_based_analysis(
            mime_type='image/png',
            image='base64_data',
            prompt='test',
            evaluator='Gemini'
        )
        
        # Assert
        assert result == mock_response_data
    
    def test_prompt_based_analysis_missing_mime_type(self):
        """Test error when mime_type is missing"""
        with pytest.raises(ValueError) as exc_info:
            ImageExplain.prompt_based_analysis(
                mime_type='',
                image='base64_data',
                prompt='test',
                evaluator='GPT_4o'
            )
        assert "mandatory fields" in str(exc_info.value)
    
    def test_prompt_based_analysis_missing_image(self):
        """Test error when image is missing"""
        with pytest.raises(ValueError):
            ImageExplain.prompt_based_analysis(
                mime_type='image/jpeg',
                image='',
                prompt='test',
                evaluator='GPT_4o'
            )
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    @patch('image_explain.service.responsible_ai_image_explain.Prompt')
    def test_prompt_based_analysis_json_decode_error(self, mock_prompt, mock_azure):
        """Test JSON decode error handling"""
        mock_azure_instance = MagicMock()
        mock_azure_instance.generate.return_value = "Invalid JSON {broken"
        mock_azure.return_value = mock_azure_instance
        mock_prompt.image_analyze_prompt.return_value = "Test"
        
        with pytest.raises(RuntimeError) as exc_info:
            ImageExplain.prompt_based_analysis(
                mime_type='image/jpeg',
                image='data',
                prompt='test',
                evaluator='GPT_4o'
            )
        assert "Error decoding JSON" in str(exc_info.value)
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    @patch('image_explain.service.responsible_ai_image_explain.Prompt')
    def test_prompt_based_analysis_exception(self, mock_prompt, mock_azure):
        """Test generic exception handling"""
        mock_azure.side_effect = Exception("API Error")
        mock_prompt.image_analyze_prompt.return_value = "Test"
        
        with pytest.raises(RuntimeError):
            ImageExplain.prompt_based_analysis(
                mime_type='image/jpeg',
                image='data',
                prompt='test',
                evaluator='GPT_4o'
            )


class TestImageExplainImageBasedBiasAnalysis:
    """Comprehensive tests for image_based_bias_analysis method"""
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    @patch('image_explain.service.responsible_ai_image_explain.Prompt')
    def test_image_based_bias_analysis_gpt_success(self, mock_prompt, mock_azure):
        """Test successful bias analysis with GPT"""
        mock_azure_instance = MagicMock()
        mock_response = {
            'analysis': 'Gender bias detected',
            'bias_type': ['Gender Bias'],
            'privileged_groups': ['Male'],
            'unprivileged_groups': ['Female']
        }
        mock_azure_instance.generate.return_value = json.dumps(mock_response)
        mock_azure.return_value = mock_azure_instance
        mock_prompt.analyze_bias_without_prompt.return_value = "Bias prompt"
        
        result = ImageExplain.image_based_bias_analysis(
            image='base64_data',
            evaluator='GPT_4o',
            mime_type='image/jpeg'
        )
        
        assert result == mock_response
    
    @patch('image_explain.service.responsible_ai_image_explain.Gemini')
    @patch('image_explain.service.responsible_ai_image_explain.Prompt')
    def test_image_based_bias_analysis_gemini_success(self, mock_prompt, mock_gemini):
        """Test successful bias analysis with Gemini"""
        mock_gemini_instance = MagicMock()
        mock_response = {'bias_analysis': 'No bias detected'}
        mock_gemini_instance.generate.return_value = json.dumps(mock_response)
        mock_gemini.return_value = mock_gemini_instance
        mock_prompt.analyze_bias_without_prompt.return_value = "Bias prompt"
        
        result = ImageExplain.image_based_bias_analysis(
            image='base64_data',
            evaluator='Gemini',
            mime_type='image/png'
        )
        
        assert result == mock_response
    
    def test_image_based_bias_analysis_missing_mime_type(self):
        """Test error when mime_type is missing"""
        with pytest.raises(ValueError):
            ImageExplain.image_based_bias_analysis(
                image='base64_data',
                evaluator='GPT_4o',
                mime_type=''
            )
    
    def test_image_based_bias_analysis_missing_image(self):
        """Test error when image is missing"""
        with pytest.raises(ValueError):
            ImageExplain.image_based_bias_analysis(
                image='',
                evaluator='GPT_4o',
                mime_type='image/jpeg'
            )
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    @patch('image_explain.service.responsible_ai_image_explain.Prompt')
    def test_image_based_bias_analysis_json_decode_error(self, mock_prompt, mock_azure):
        """Test JSON decode error in bias analysis"""
        mock_azure_instance = MagicMock()
        mock_azure_instance.generate.return_value = "{invalid}"
        mock_azure.return_value = mock_azure_instance
        mock_prompt.analyze_bias_without_prompt.return_value = "Prompt"
        
        with pytest.raises(RuntimeError):
            ImageExplain.image_based_bias_analysis(
                image='data',
                evaluator='GPT_4o',
                mime_type='image/jpeg'
            )


class TestImageExplainQueryBasedAnalysis:
    """Comprehensive tests for query_based_image_analysis method"""
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    @patch('image_explain.service.responsible_ai_image_explain.Prompt')
    def test_query_based_analysis_gpt_success(self, mock_prompt, mock_azure):
        """Test successful query-based analysis with GPT"""
        mock_azure_instance = MagicMock()
        mock_response = {'response': 'The image shows a dog'}
        mock_azure_instance.generate.return_value = json.dumps(mock_response)
        mock_azure.return_value = mock_azure_instance
        mock_prompt.query_based_image_analysis_prompt.return_value = "Query prompt"
        
        result = ImageExplain.query_based_image_analysis(
            image_base64='base64_data',
            mime_type='image/jpeg',
            prompt='What is in the image?',
            evaluator='GPT_4o'
        )
        
        assert result == mock_response
        mock_prompt.query_based_image_analysis_prompt.assert_called_with('What is in the image?')
    
    @patch('image_explain.service.responsible_ai_image_explain.Gemini')
    @patch('image_explain.service.responsible_ai_image_explain.Prompt')
    def test_query_based_analysis_gemini_success(self, mock_prompt, mock_gemini):
        """Test successful query-based analysis with Gemini"""
        mock_gemini_instance = MagicMock()
        mock_response = {'answer': 'Test answer'}
        mock_gemini_instance.generate.return_value = json.dumps(mock_response)
        mock_gemini.return_value = mock_gemini_instance
        mock_prompt.query_based_image_analysis_prompt.return_value = "Query prompt"
        
        result = ImageExplain.query_based_image_analysis(
            image_base64='data',
            mime_type='image/png',
            prompt='Describe the scene',
            evaluator='Gemini'
        )
        
        assert result == mock_response
    
    def test_query_based_analysis_missing_mime_type(self):
        """Test error when mime_type is missing"""
        with pytest.raises(ValueError):
            ImageExplain.query_based_image_analysis(
                image_base64='data',
                mime_type='',
                prompt='What?',
                evaluator='GPT_4o'
            )
    
    def test_query_based_analysis_missing_image(self):
        """Test error when image is missing"""
        with pytest.raises(ValueError):
            ImageExplain.query_based_image_analysis(
                image_base64='',
                mime_type='image/jpeg',
                prompt='What?',
                evaluator='GPT_4o'
            )
    
    def test_query_based_analysis_missing_prompt(self):
        """Test error when prompt is missing"""
        with pytest.raises(ValueError):
            ImageExplain.query_based_image_analysis(
                image_base64='data',
                mime_type='image/jpeg',
                prompt='',
                evaluator='GPT_4o'
            )


class TestImageExplainAnalyzeImage:
    """Comprehensive tests for analyze_image method"""
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    def test_analyze_image_gpt_success(self, mock_azure):
        """Test successful analyze_image with GPT evaluator"""
        mock_azure_instance = MagicMock()
        mock_response = {'result': 'Analysis complete'}
        mock_azure_instance.generate.return_value = json.dumps(mock_response)
        mock_azure.return_value = mock_azure_instance
        
        result = ImageExplain.analyze_image(
            image='base64_data',
            prompt='Analyze this',
            evaluator='GPT_4o',
            mime_type='image/jpeg'
        )
        
        assert result == mock_response
    
    @patch('image_explain.service.responsible_ai_image_explain.Gemini')
    def test_analyze_image_gemini_success(self, mock_gemini):
        """Test successful analyze_image with Gemini evaluator"""
        mock_gemini_instance = MagicMock()
        mock_response = {'analysis': 'Done'}
        mock_gemini_instance.generate.return_value = json.dumps(mock_response)
        mock_gemini.return_value = mock_gemini_instance
        
        result = ImageExplain.analyze_image(
            image='base64_data',
            prompt='Analyze',
            evaluator='Gemini',
            mime_type='image/jpeg'
        )
        
        assert result == mock_response
    
    @patch('image_explain.service.responsible_ai_image_explain.Ollama')
    def test_analyze_image_ollama_success(self, mock_ollama):
        """Test successful analyze_image with Ollama evaluator"""
        mock_response = {'result': 'Local analysis'}
        mock_ollama.generate.return_value = mock_response
        
        result = ImageExplain.analyze_image(
            image='base64_data',
            prompt='Analyze',
            evaluator='Llama2',
            mime_type='image/jpeg'
        )
        
        assert result == mock_response
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    def test_analyze_image_json_decode_error(self, mock_azure):
        """Test JSON decode error in analyze_image"""
        mock_azure_instance = MagicMock()
        mock_azure_instance.generate.return_value = "Not JSON"
        mock_azure.return_value = mock_azure_instance
        
        with pytest.raises(RuntimeError):
            ImageExplain.analyze_image(
                image='data',
                prompt='Analyze',
                evaluator='GPT_4o',
                mime_type='image/jpeg'
            )
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    def test_analyze_image_bad_request_error(self, mock_azure):
        """Test BadRequestError (Azure Content Policy) handling"""
        mock_azure_instance = MagicMock()
        mock_azure_instance.generate.side_effect = openai.BadRequestError(
            message="Content policy violation",
            response=Mock(),
            body={}
        )
        mock_azure.return_value = mock_azure_instance
        
        with pytest.raises(RuntimeError) as exc_info:
            ImageExplain.analyze_image(
                image='data',
                prompt='Analyze',
                evaluator='GPT_4o',
                mime_type='image/jpeg'
            )
        assert "Content Policy" in str(exc_info.value)
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    def test_analyze_image_generic_exception(self, mock_azure):
        """Test generic exception handling in analyze_image"""
        mock_azure.side_effect = Exception("API Error")
        
        with pytest.raises(RuntimeError):
            ImageExplain.analyze_image(
                image='data',
                prompt='Analyze',
                evaluator='GPT_4o',
                mime_type='image/jpeg'
            )


class TestImageExplainUncertaintyScore:
    """Comprehensive tests for uncertainity_score method"""
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    def test_uncertainty_score_gpt_4o_success(self, mock_azure):
        """Test successful uncertainty score calculation with GPT_4o"""
        mock_azure_instance = MagicMock()
        mock_response = {'uncertainty': 0.25}
        mock_azure_instance.generate.return_value = json.dumps(mock_response)
        mock_azure.return_value = mock_azure_instance
        
        result = ImageExplain.uncertainity_score(
            mime_type='image/jpeg',
            image='base64_data',
            prompt='Calculate uncertainty',
            evaluator='GPT_4o'
        )
        
        assert result == mock_response
    
    @patch('image_explain.service.responsible_ai_image_explain.Gemini')
    def test_uncertainty_score_gemini_success(self, mock_gemini):
        """Test successful uncertainty score with non-GPT evaluator"""
        mock_gemini_instance = MagicMock()
        mock_response = {'score': 0.15}
        mock_gemini_instance.generate.return_value = json.dumps(mock_response)
        mock_gemini.return_value = mock_gemini_instance
        
        result = ImageExplain.uncertainity_score(
            mime_type='image/jpeg',
            image='base64_data',
            prompt='Score',
            evaluator='Gemini'
        )
        
        assert result == mock_response
    
    def test_uncertainty_score_missing_mime_type(self):
        """Test error when mime_type is missing"""
        with pytest.raises(ValueError):
            ImageExplain.uncertainity_score(
                mime_type='',
                image='base64_data',
                prompt='Score',
                evaluator='GPT_4o'
            )
    
    def test_uncertainty_score_missing_image(self):
        """Test error when image is missing"""
        with pytest.raises(ValueError):
            ImageExplain.uncertainity_score(
                mime_type='image/jpeg',
                image='',
                prompt='Score',
                evaluator='GPT_4o'
            )
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    def test_uncertainty_score_json_decode_error(self, mock_azure):
        """Test JSON decode error in uncertainty score"""
        mock_azure_instance = MagicMock()
        mock_azure_instance.generate.return_value = "Invalid"
        mock_azure.return_value = mock_azure_instance
        
        with pytest.raises(RuntimeError):
            ImageExplain.uncertainity_score(
                mime_type='image/jpeg',
                image='data',
                prompt='Score',
                evaluator='GPT_4o'
            )


class TestImageExplainValueErrors:
    """Tests for ValueError handling"""
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    @patch('image_explain.service.responsible_ai_image_explain.Prompt')
    def test_prompt_analysis_value_error(self, mock_prompt, mock_azure):
        """Test ValueError handling in prompt_based_analysis"""
        mock_azure_instance = MagicMock()
        mock_azure_instance.generate.side_effect = ValueError("Invalid value")
        mock_azure.return_value = mock_azure_instance
        mock_prompt.image_analyze_prompt.return_value = "Prompt"
        
        with pytest.raises(RuntimeError) as exc_info:
            ImageExplain.prompt_based_analysis(
                mime_type='image/jpeg',
                image='data',
                prompt='test',
                evaluator='GPT_4o'
            )
        assert "Value error" in str(exc_info.value)
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    @patch('image_explain.service.responsible_ai_image_explain.Prompt')
    def test_bias_analysis_value_error(self, mock_prompt, mock_azure):
        """Test ValueError handling in image_based_bias_analysis"""
        mock_azure_instance = MagicMock()
        mock_azure_instance.generate.side_effect = ValueError("Invalid data")
        mock_azure.return_value = mock_azure_instance
        mock_prompt.analyze_bias_without_prompt.return_value = "Bias prompt"
        
        with pytest.raises(RuntimeError):
            ImageExplain.image_based_bias_analysis(
                image='data',
                evaluator='GPT_4o',
                mime_type='image/jpeg'
            )
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    @patch('image_explain.service.responsible_ai_image_explain.Prompt')
    def test_query_analysis_value_error(self, mock_prompt, mock_azure):
        """Test ValueError handling in query_based_image_analysis"""
        mock_azure_instance = MagicMock()
        mock_azure_instance.generate.side_effect = ValueError("Invalid query")
        mock_azure.return_value = mock_azure_instance
        mock_prompt.query_based_image_analysis_prompt.return_value = "Query prompt"
        
        with pytest.raises(RuntimeError):
            ImageExplain.query_based_image_analysis(
                image_base64='data',
                mime_type='image/jpeg',
                prompt='What?',
                evaluator='GPT_4o'
            )


class TestImageExplainEdgeCases:
    """Tests for edge cases and boundary conditions"""
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    @patch('image_explain.service.responsible_ai_image_explain.Prompt')
    def test_empty_response_handling(self, mock_prompt, mock_azure):
        """Test handling of empty JSON response"""
        mock_azure_instance = MagicMock()
        mock_azure_instance.generate.return_value = '{}'
        mock_azure.return_value = mock_azure_instance
        mock_prompt.image_analyze_prompt.return_value = "Prompt"
        
        result = ImageExplain.prompt_based_analysis(
            mime_type='image/jpeg',
            image='data',
            prompt='test',
            evaluator='GPT_4o'
        )
        
        assert result == {}
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    @patch('image_explain.service.responsible_ai_image_explain.Prompt')
    def test_complex_nested_json_response(self, mock_prompt, mock_azure):
        """Test handling of complex nested JSON responses"""
        mock_azure_instance = MagicMock()
        complex_response = {
            'level1': {
                'level2': {
                    'level3': ['array', 'values']
                }
            },
            'items': [1, 2, 3]
        }
        mock_azure_instance.generate.return_value = json.dumps(complex_response)
        mock_azure.return_value = mock_azure_instance
        mock_prompt.image_analyze_prompt.return_value = "Prompt"
        
        result = ImageExplain.prompt_based_analysis(
            mime_type='image/jpeg',
            image='data',
            prompt='test',
            evaluator='GPT_4o'
        )
        
        assert result == complex_response
    
    @patch('image_explain.service.responsible_ai_image_explain.Ollama')
    def test_ollama_lowercase_handling(self, mock_ollama):
        """Test Ollama evaluator matching is case-insensitive"""
        mock_response = {'result': 'Local AI response'}
        mock_ollama.generate.return_value = mock_response
        
        result = ImageExplain.analyze_image(
            image='data',
            prompt='test',
            evaluator='llama',
            mime_type='image/jpeg'
        )
        
        assert result == mock_response


class TestImageExplainMultipleEvaluators:
    """Tests for handling multiple evaluator types correctly"""
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    def test_gpt_case_insensitive_matching(self, mock_azure):
        """Test that GPT matching is case-insensitive"""
        mock_azure_instance = MagicMock()
        mock_response = {'result': 'OK'}
        mock_azure_instance.generate.return_value = json.dumps(mock_response)
        mock_azure.return_value = mock_azure_instance
        
        # Test various case combinations
        for evaluator in ['GPT', 'gpt', 'Gpt', 'gPt']:
            result = ImageExplain.analyze_image(
                image='data',
                prompt='test',
                evaluator=evaluator,
                mime_type='image/jpeg'
            )
            assert result == mock_response
    
    @patch('image_explain.service.responsible_ai_image_explain.Gemini')
    def test_gemini_case_insensitive_matching(self, mock_gemini):
        """Test that Gemini matching is case-insensitive"""
        mock_gemini_instance = MagicMock()
        mock_response = {'result': 'OK'}
        mock_gemini_instance.generate.return_value = json.dumps(mock_response)
        mock_gemini.return_value = mock_gemini_instance
        
        result = ImageExplain.analyze_image(
            image='data',
            prompt='test',
            evaluator='GEMINI',
            mime_type='image/jpeg'
        )
        assert result == mock_response
