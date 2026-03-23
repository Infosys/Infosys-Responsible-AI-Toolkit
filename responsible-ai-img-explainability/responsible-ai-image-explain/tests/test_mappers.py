"""
Unit tests for mappers module
Tests Pydantic model mappings and schema validation
"""
import pytest
import sys
import os
from typing import Dict

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from image_explain.mappers.mappers import AnalyzeResponse, ObjectDetectionResponse


class TestAnalyzeResponse:
    """Test suite for AnalyzeResponse Pydantic model"""
    
    def test_analyze_response_creation(self):
        """Test creating AnalyzeResponse object"""
        response = AnalyzeResponse(
            image_description="Test description",
            insights={"style": "abstract"},
            metrics={"score": 0.85},
            super_pixels="base64_encoded_string"
        )
        assert response is not None
        assert response.image_description == "Test description"
    
    def test_analyze_response_all_fields(self):
        """Test all fields of AnalyzeResponse"""
        test_data = {
            "image_description": "A mountain landscape",
            "insights": {
                "watermark": "test.com",
                "style": "landscape",
                "style_analysis": "Natural landscape photography"
            },
            "metrics": {
                "creativity_score": 75,
                "coherence_score": 85
            },
            "super_pixels": "encoded_image_data"
        }
        response = AnalyzeResponse(**test_data)
        
        assert response.image_description == test_data["image_description"]
        assert response.insights == test_data["insights"]
        assert response.metrics == test_data["metrics"]
        assert response.super_pixels == test_data["super_pixels"]
    
    def test_analyze_response_empty_dicts(self):
        """Test AnalyzeResponse with empty dictionaries"""
        response = AnalyzeResponse(
            image_description="Test",
            insights={},
            metrics={},
            super_pixels=""
        )
        assert response.insights == {}
        assert response.metrics == {}
    
    def test_analyze_response_nested_insights(self):
        """Test AnalyzeResponse with nested insights structure"""
        insights = {
            "watermark": "copyright",
            "style": "modern",
            "style_analysis": "Contemporary design",
            "query_response": "Yes, there is a person",
            "bias_type": "gender bias",
            "bias_analysis": "Analysis details"
        }
        response = AnalyzeResponse(
            image_description="Complex image",
            insights=insights,
            metrics={},
            super_pixels=""
        )
        assert response.insights["bias_type"] == "gender bias"
        assert response.insights["query_response"] == "Yes, there is a person"
    
    def test_analyze_response_dict_conversion(self):
        """Test converting AnalyzeResponse to dict"""
        response = AnalyzeResponse(
            image_description="Test",
            insights={"key": "value"},
            metrics={"metric": 100},
            super_pixels="base64"
        )
        # Pydantic models have dict() method
        response_dict = response.model_dump()
        assert isinstance(response_dict, dict)
        assert "image_description" in response_dict
    
    def test_analyze_response_json_compatible(self):
        """Test AnalyzeResponse is JSON serializable"""
        response = AnalyzeResponse(
            image_description="Test description",
            insights={"key": "value"},
            metrics={"score": 0.95},
            super_pixels="base64_data"
        )
        # Pydantic models should be JSON serializable
        json_data = response.model_dump_json()
        assert isinstance(json_data, str)
        assert "image_description" in json_data


class TestObjectDetectionResponse:
    """Test suite for ObjectDetectionResponse Pydantic model"""
    
    def test_object_detection_response_creation(self):
        """Test creating ObjectDetectionResponse object"""
        response = ObjectDetectionResponse(
            explanation="Detected person and car",
            predicted_image="base64_image",
            time_taken=0.5
        )
        assert response is not None
        assert response.explanation == "Detected person and car"
        assert response.time_taken == 0.5
    
    def test_object_detection_response_all_fields(self):
        """Test all fields of ObjectDetectionResponse"""
        test_data = {
            "explanation": "The image contains a dog in the foreground",
            "predicted_image": "encoded_image_with_bboxes",
            "time_taken": 1.234
        }
        response = ObjectDetectionResponse(**test_data)
        
        assert response.explanation == test_data["explanation"]
        assert response.predicted_image == test_data["predicted_image"]
        assert response.time_taken == test_data["time_taken"]
    
    def test_object_detection_response_time_taken_types(self):
        """Test time_taken field accepts float values"""
        times = [0.0, 0.5, 1.0, 2.5, 10.123]
        for time_val in times:
            response = ObjectDetectionResponse(
                explanation="Test",
                predicted_image="base64",
                time_taken=time_val
            )
            assert response.time_taken == time_val
    
    def test_object_detection_response_empty_fields(self):
        """Test ObjectDetectionResponse with empty strings"""
        response = ObjectDetectionResponse(
            explanation="",
            predicted_image="",
            time_taken=0.0
        )
        assert response.explanation == ""
        assert response.predicted_image == ""
        assert response.time_taken == 0.0
    
    def test_object_detection_response_long_explanation(self):
        """Test ObjectDetectionResponse with long explanation text"""
        long_explanation = "A" * 1000  # 1000 character string
        response = ObjectDetectionResponse(
            explanation=long_explanation,
            predicted_image="base64",
            time_taken=0.5
        )
        assert response.explanation == long_explanation
        assert len(response.explanation) == 1000
    
    def test_object_detection_response_dict_conversion(self):
        """Test converting ObjectDetectionResponse to dict"""
        response = ObjectDetectionResponse(
            explanation="Test",
            predicted_image="image_data",
            time_taken=0.75
        )
        response_dict = response.model_dump()
        assert isinstance(response_dict, dict)
        assert "explanation" in response_dict
        assert "time_taken" in response_dict
    
    def test_object_detection_response_json_compatible(self):
        """Test ObjectDetectionResponse is JSON serializable"""
        response = ObjectDetectionResponse(
            explanation="Detected objects",
            predicted_image="base64_encoded",
            time_taken=1.5
        )
        json_data = response.model_dump_json()
        assert isinstance(json_data, str)
        assert "explanation" in json_data
        assert "time_taken" in json_data


class TestResponseModelsValidation:
    """Test validation of response models"""
    
    def test_analyze_response_missing_field_raises(self):
        """Test that missing required field raises validation error"""
        with pytest.raises(Exception):  # Pydantic raises ValidationError
            AnalyzeResponse(
                image_description="Test",
                insights={},
                # Missing metrics and super_pixels
            )
    
    def test_object_detection_response_missing_field_raises(self):
        """Test that missing required field raises validation error"""
        with pytest.raises(Exception):  # Pydantic raises ValidationError
            ObjectDetectionResponse(
                explanation="Test",
                # Missing predicted_image and time_taken
            )
    
    def test_analyze_response_field_types(self):
        """Test field type validation"""
        response = AnalyzeResponse(
            image_description="Test",
            insights={},
            metrics={},
            super_pixels=""
        )
        assert isinstance(response.image_description, str)
        assert isinstance(response.insights, dict)
        assert isinstance(response.metrics, dict)
        assert isinstance(response.super_pixels, str)
    
    def test_object_detection_response_field_types(self):
        """Test field type validation"""
        response = ObjectDetectionResponse(
            explanation="Test",
            predicted_image="image",
            time_taken=0.5
        )
        assert isinstance(response.explanation, str)
        assert isinstance(response.predicted_image, str)
        assert isinstance(response.time_taken, (int, float))
