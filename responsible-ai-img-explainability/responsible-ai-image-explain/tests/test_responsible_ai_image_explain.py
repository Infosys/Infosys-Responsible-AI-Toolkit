"""
Unit tests for ImageExplain service
Tests image analysis and bias detection methods
"""
import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock, Mock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from image_explain.service.responsible_ai_image_explain import ImageExplain


class TestImageExplainPromptBasedAnalysis:
    """Test suite for prompt_based_analysis method"""
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    def test_prompt_based_analysis_with_gpt_evaluator(self, mock_azure):
        """Test prompt-based analysis with GPT evaluator"""
        mock_azure_instance = MagicMock()
        mock_azure_instance.generate.return_value = json.dumps({
            "ImageDescription": "Test image",
            "Style": "abstract"
        })
        mock_azure.return_value = mock_azure_instance
        
        result = ImageExplain.prompt_based_analysis(
            mime_type="image/jpeg",
            image="base64_string",
            prompt="describe",
            evaluator="GPT_4o"
        )
        
        assert isinstance(result, dict)
        assert "ImageDescription" in result
    
    @patch('image_explain.service.responsible_ai_image_explain.Gemini')
    def test_prompt_based_analysis_with_gemini_evaluator(self, mock_gemini):
        """Test prompt-based analysis with Gemini evaluator"""
        mock_gemini_instance = MagicMock()
        mock_gemini_instance.generate.return_value = json.dumps({
            "ImageDescription": "Gemini result",
            "Style": "modern"
        })
        mock_gemini.return_value = mock_gemini_instance
        
        result = ImageExplain.prompt_based_analysis(
            mime_type="image/png",
            image="base64_string",
            prompt="analyze",
            evaluator="Gemini"
        )
        
        assert isinstance(result, dict)
    
    def test_prompt_based_analysis_missing_mime_type(self):
        """Test prompt-based analysis raises error for missing mime_type"""
        with pytest.raises(ValueError):
            ImageExplain.prompt_based_analysis(
                mime_type="",
                image="base64_string",
                prompt="test",
                evaluator="GPT_4o"
            )
    
    def test_prompt_based_analysis_missing_image(self):
        """Test prompt-based analysis raises error for missing image"""
        with pytest.raises(ValueError):
            ImageExplain.prompt_based_analysis(
                mime_type="image/jpeg",
                image="",
                prompt="test",
                evaluator="GPT_4o"
            )
    
    def test_prompt_based_analysis_missing_both_required_fields(self):
        """Test prompt-based analysis raises error for missing required fields"""
        with pytest.raises(ValueError):
            ImageExplain.prompt_based_analysis(
                mime_type="",
                image="",
                prompt="test",
                evaluator="GPT_4o"
            )
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    def test_prompt_based_analysis_json_parsing(self, mock_azure):
        """Test proper JSON parsing in prompt-based analysis"""
        mock_azure_instance = MagicMock()
        response_json = {
            "ImageDescription": "Complex image",
            "Style": "surrealism",
            "WatermarkContent": "test"
        }
        mock_azure_instance.generate.return_value = json.dumps(response_json)
        mock_azure.return_value = mock_azure_instance
        
        result = ImageExplain.prompt_based_analysis(
            mime_type="image/jpeg",
            image="base64_string",
            prompt="describe",
            evaluator="GPT_4o"
        )
        
        assert result == response_json
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    def test_prompt_based_analysis_invalid_json_response(self, mock_azure):
        """Test error handling for invalid JSON response"""
        mock_azure_instance = MagicMock()
        mock_azure_instance.generate.return_value = "Not valid JSON"
        mock_azure.return_value = mock_azure_instance
        
        with pytest.raises(RuntimeError):
            ImageExplain.prompt_based_analysis(
                mime_type="image/jpeg",
                image="base64_string",
                prompt="test",
                evaluator="GPT_4o"
            )


class TestImageExplainAnalyzeImage:
    """Test suite for analyze_image method"""
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    def test_analyze_image_with_gpt(self, mock_azure):
        """Test analyze_image method with GPT evaluator"""
        mock_azure_instance = MagicMock()
        mock_azure_instance.generate.return_value = json.dumps({
            "Analysis": "Image analysis result"
        })
        mock_azure.return_value = mock_azure_instance
        
        result = ImageExplain.analyze_image(
            mime_type="image/jpeg",
            image="base64_string",
            prompt="analyze",
            evaluator="GPT_4o"
        )
        
        assert result is not None


class TestImageExplainImageBasedBiasAnalysis:
    """Test suite for image_based_bias_analysis method"""
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    def test_image_based_bias_analysis_with_gpt(self, mock_azure):
        """Test image-based bias analysis with GPT"""
        mock_azure_instance = MagicMock()
        mock_azure_instance.generate.return_value = json.dumps({
            "Bias type(s)": "gender bias",
            "Analysis": "Bias found in representation"
        })
        mock_azure.return_value = mock_azure_instance
        
        result = ImageExplain.image_based_bias_analysis(
            mime_type="image/jpeg",
            image="base64_string",
            evaluator="GPT_4o"
        )
        
        assert isinstance(result, dict)


class TestImageExplainQueryBasedAnalysis:
    """Test suite for query_based_image_analysis method"""
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    def test_query_based_image_analysis_with_gpt(self, mock_azure):
        """Test query-based image analysis with GPT"""
        mock_azure_instance = MagicMock()
        mock_azure_instance.generate.return_value = json.dumps({
            "Response": "Answer to query"
        })
        mock_azure.return_value = mock_azure_instance
        
        result = ImageExplain.query_based_image_analysis(
            image_base64="base64_string",
            mime_type="image/jpeg",
            prompt="what is this?",
            evaluator="GPT_4o"
        )
        
        assert isinstance(result, dict)


class TestImageExplainErrorHandling:
    """Test suite for error handling in ImageExplain"""
    
    def test_prompt_based_analysis_handles_exceptions(self):
        """Test that exceptions are properly handled and re-raised"""
        with patch('image_explain.service.responsible_ai_image_explain.Azure') as mock_azure:
            mock_azure.side_effect = Exception("Azure API error")
            
            with pytest.raises(RuntimeError):
                ImageExplain.prompt_based_analysis(
                    mime_type="image/jpeg",
                    image="base64_string",
                    prompt="test",
                    evaluator="GPT_4o"
                )
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    def test_analyze_image_handles_api_errors(self, mock_azure):
        """Test analyze_image handles API errors gracefully"""
        mock_azure_instance = MagicMock()
        mock_azure_instance.generate.side_effect = Exception("API timeout")
        mock_azure.return_value = mock_azure_instance
        
        with pytest.raises(RuntimeError):
            ImageExplain.analyze_image(
                mime_type="image/jpeg",
                image="base64_string",
                prompt="test",
                evaluator="GPT_4o"
            )


class TestImageExplainValidation:
    """Test suite for input validation"""
    
    def test_prompt_based_analysis_validates_mime_type(self):
        """Test that mime_type validation works"""
        with pytest.raises(ValueError) as exc_info:
            ImageExplain.prompt_based_analysis(
                mime_type=None,
                image="base64",
                prompt="test",
                evaluator="GPT_4o"
            )
        assert "mandatory" in str(exc_info.value).lower()
    
    def test_prompt_based_analysis_validates_image(self):
        """Test that image validation works"""
        with pytest.raises(ValueError) as exc_info:
            ImageExplain.prompt_based_analysis(
                mime_type="image/jpeg",
                image=None,
                prompt="test",
                evaluator="GPT_4o"
            )
        assert "mandatory" in str(exc_info.value).lower()


class TestImageExplainJsonHandling:
    """Test suite for JSON response handling"""
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    def test_json_decode_error_handling(self, mock_azure):
        """Test JSON decode error handling"""
        mock_azure_instance = MagicMock()
        mock_azure_instance.generate.return_value = "{invalid json"
        mock_azure.return_value = mock_azure_instance
        
        with pytest.raises(RuntimeError) as exc_info:
            ImageExplain.prompt_based_analysis(
                mime_type="image/jpeg",
                image="base64",
                prompt="test",
                evaluator="GPT_4o"
            )
        assert "JSON" in str(exc_info.value)
    
    @patch('image_explain.service.responsible_ai_image_explain.Azure')
    def test_complex_json_response_handling(self, mock_azure):
        """Test handling complex nested JSON responses"""
        mock_azure_instance = MagicMock()
        complex_response = {
            "ImageDescription": "Test",
            "nested": {
                "level1": {
                    "level2": "value"
                }
            },
            "array": [1, 2, 3]
        }
        mock_azure_instance.generate.return_value = json.dumps(complex_response)
        mock_azure.return_value = mock_azure_instance
        
        result = ImageExplain.prompt_based_analysis(
            mime_type="image/jpeg",
            image="base64",
            prompt="test",
            evaluator="GPT_4o"
        )
        
        assert result == complex_response
