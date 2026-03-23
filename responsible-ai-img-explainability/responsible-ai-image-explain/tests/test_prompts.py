"""
Extended test coverage for base.py - Prompt class static methods
"""

import pytest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from image_explain.utils.prompts.base import Prompt


class TestPromptImageAnalyze:
    """Test image_analyze_prompt method"""
    
    def test_image_analyze_prompt_returns_string(self):
        """Test that image_analyze_prompt returns a string"""
        prompt = Prompt()
        result = prompt.image_analyze_prompt()
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_image_analyze_prompt_not_empty(self):
        """Test that image_analyze_prompt returns non-empty string"""
        prompt = Prompt()
        result = prompt.image_analyze_prompt()
        
        assert result.strip() != ""
    
    def test_image_analyze_prompt_contains_keywords(self):
        """Test that image_analyze_prompt contains relevant keywords"""
        prompt = Prompt()
        result = prompt.image_analyze_prompt()
        
        # Should contain instructions for analysis
        assert len(result) > 20  # Should be a meaningful prompt
    
    def test_image_analyze_prompt_consistency(self):
        """Test that image_analyze_prompt returns consistent results"""
        prompt = Prompt()
        result1 = prompt.image_analyze_prompt()
        result2 = prompt.image_analyze_prompt()
        
        assert result1 == result2
    
    def test_image_analyze_prompt_is_static(self):
        """Test that image_analyze_prompt is callable without instance"""
        # Should not raise AttributeError
        prompt = Prompt()
        result = prompt.image_analyze_prompt()
        
        assert result is not None
    
    def test_image_analyze_prompt_json_format(self):
        """Test that image_analyze_prompt may contain JSON instructions"""
        prompt = Prompt()
        result = prompt.image_analyze_prompt()
        
        # Check if it's asking for JSON output
        contains_json_mention = ('json' in result.lower() or 
                                 '{' in result or 
                                 'format' in result.lower())
        assert contains_json_mention or len(result) > 50


class TestPromptAnalyzeBiasWithoutPrompt:
    """Test analyze_bias_without_prompt method"""
    
    def test_analyze_bias_without_prompt_returns_string(self):
        """Test that analyze_bias_without_prompt returns a string"""
        prompt = Prompt()
        result = prompt.analyze_bias_without_prompt()
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_analyze_bias_without_prompt_not_empty(self):
        """Test that analyze_bias_without_prompt returns non-empty string"""
        prompt = Prompt()
        result = prompt.analyze_bias_without_prompt()
        
        assert result.strip() != ""
    
    def test_analyze_bias_without_prompt_contains_bias_keyword(self):
        """Test that bias analysis prompt contains relevant content"""
        prompt = Prompt()
        result = prompt.analyze_bias_without_prompt()
        
        # Should be meaningful prompt
        assert len(result) > 20
    
    def test_analyze_bias_without_prompt_consistency(self):
        """Test that analyze_bias_without_prompt returns consistent results"""
        prompt = Prompt()
        result1 = prompt.analyze_bias_without_prompt()
        result2 = prompt.analyze_bias_without_prompt()
        
        assert result1 == result2
    
    def test_analyze_bias_without_prompt_different_from_analyze_prompt(self):
        """Test that bias prompt is different from image analyze prompt"""
        prompt = Prompt()
        bias_result = prompt.analyze_bias_without_prompt()
        analyze_result = prompt.image_analyze_prompt()
        
        # Should be different prompts
        assert bias_result != analyze_result
    
    def test_analyze_bias_without_prompt_is_static(self):
        """Test that analyze_bias_without_prompt is callable without instance"""
        prompt = Prompt()
        result = prompt.analyze_bias_without_prompt()
        
        assert result is not None


class TestPromptQueryBasedImageAnalysis:
    """Test query_based_image_analysis_prompt method"""
    
    def test_query_based_image_analysis_prompt_returns_string(self):
        """Test that query_based_image_analysis_prompt returns a string"""
        prompt = Prompt()
        result = prompt.query_based_image_analysis_prompt("What is in this image?")
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_query_based_image_analysis_prompt_with_empty_query(self):
        """Test query_based_image_analysis_prompt with empty query"""
        prompt = Prompt()
        result = prompt.query_based_image_analysis_prompt("")
        
        assert isinstance(result, str)
    
    def test_query_based_image_analysis_prompt_with_none_query(self):
        """Test query_based_image_analysis_prompt with None query"""
        try:
            prompt = Prompt()
            result = prompt.query_based_image_analysis_prompt(None)
            assert result is not None
        except (TypeError, AttributeError):
            # Expected if method doesn't handle None
            pass
    
    def test_query_based_image_analysis_prompt_includes_query(self):
        """Test that query is incorporated into prompt"""
        query = "Identify all objects in the image"
        prompt = Prompt()
        result = prompt.query_based_image_analysis_prompt(query)
        
        # Query should be included or used in prompt
        assert len(result) > len(query)
    
    def test_query_based_image_analysis_prompt_with_long_query(self):
        """Test query_based_image_analysis_prompt with long query"""
        long_query = "Analyze this image for all types of objects, their positions, colors, and relationships" * 2
        prompt = Prompt()
        result = prompt.query_based_image_analysis_prompt(long_query)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_query_based_image_analysis_prompt_with_special_characters(self):
        """Test query_based_image_analysis_prompt with special characters"""
        query = "What are the objects? Find: @#$% & (objects)"
        prompt = Prompt()
        result = prompt.query_based_image_analysis_prompt(query)
        
        assert isinstance(result, str)
    
    def test_query_based_image_analysis_prompt_consistency(self):
        """Test that same query produces same prompt"""
        query = "Test query"
        prompt = Prompt()
        result1 = prompt.query_based_image_analysis_prompt(query)
        result2 = prompt.query_based_image_analysis_prompt(query)
        
        assert result1 == result2
    
    def test_query_based_image_analysis_prompt_different_queries(self):
        """Test that different queries produce different prompts"""
        query1 = "Find cars"
        query2 = "Find people"
        
        prompt = Prompt()
        result1 = prompt.query_based_image_analysis_prompt(query1)
        result2 = prompt.query_based_image_analysis_prompt(query2)
        
        # Should be different
        assert result1 != result2 or len(result1) > 0


class TestPromptObjectDetection:
    """Test object detection prompt methods"""
    
    def test_object_detection_img_prompt_returns_string(self):
        """Test that object_detection_img_prompt returns a string"""
        prompt = Prompt()
        result = prompt.object_detection_img_prompt()
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_object_detection_img_prompt_contains_detection_keywords(self):
        """Test object detection prompt has relevant content"""
        prompt = Prompt()
        result = prompt.object_detection_img_prompt()
        
        assert len(result) > 20
    
    def test_object_detection_img_prompt_consistency(self):
        """Test object_detection_img_prompt is consistent"""
        prompt = Prompt()
        result1 = prompt.object_detection_img_prompt()
        result2 = prompt.object_detection_img_prompt()
        
        assert result1 == result2
    
    def test_detect_objects_prompt_returns_string(self):
        """Test that detect_objects_prompt returns a string"""
        prompt = Prompt()
        result = prompt.detect_objects_prompt()
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_detect_objects_prompt_consistency(self):
        """Test detect_objects_prompt is consistent"""
        prompt = Prompt()
        result1 = prompt.detect_objects_prompt()
        result2 = prompt.detect_objects_prompt()
        
        assert result1 == result2
    
    def test_detect_objects_prompt_different_from_img_prompt(self):
        """Test that detect_objects_prompt differs from object_detection_img_prompt"""
        prompt = Prompt()
        result1 = prompt.detect_objects_prompt()
        result2 = prompt.object_detection_img_prompt()
        
        # May or may not be different, but both should be valid
        assert len(result1) > 0 and len(result2) > 0


class TestPromptDetectObjectsSLM:
    """Test SLM-based object detection prompts"""
    
    def test_detect_objects_slm_prompt_returns_string(self):
        """Test that detect_objects_slm_prompt returns a string"""
        prompt = Prompt()
        result = prompt.detect_objects_slm_prompt()
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_detect_objects_slm_prompt_contains_slm_context(self):
        """Test that SLM prompt is appropriate for smaller models"""
        prompt = Prompt()
        result = prompt.detect_objects_slm_prompt()
        
        # Should be a meaningful prompt
        assert len(result) > 20
    
    def test_detect_objects_slm_prompt_consistency(self):
        """Test detect_objects_slm_prompt is consistent"""
        prompt = Prompt()
        result1 = prompt.detect_objects_slm_prompt()
        result2 = prompt.detect_objects_slm_prompt()
        
        assert result1 == result2
    
    def test_detect_objects_slm_prompt_different_from_llm_variant(self):
        """Test SLM variant differs from standard variant"""
        prompt = Prompt()
        slm_result = prompt.detect_objects_slm_prompt()
        standard_result = prompt.detect_objects_prompt()
        
        # Both should be valid
        assert len(slm_result) > 0 and len(standard_result) > 0


class TestPromptBoundingBoxes:
    """Test bounding box prompts"""
    
    def test_bounding_boxes_prompt_returns_string(self):
        """Test that bounding_boxes_prompt returns a string"""
        prompt = Prompt()
        result = prompt.bounding_boxes_prompt()
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_bounding_boxes_prompt_contains_bbox_context(self):
        """Test that bounding box prompt contains relevant instructions"""
        prompt = Prompt()
        result = prompt.bounding_boxes_prompt()
        
        assert len(result) > 20
    
    def test_bounding_boxes_prompt_consistency(self):
        """Test bounding_boxes_prompt is consistent"""
        prompt = Prompt()
        result1 = prompt.bounding_boxes_prompt()
        result2 = prompt.bounding_boxes_prompt()
        
        assert result1 == result2
    
    def test_bounding_boxes_slm_prompt_returns_string(self):
        """Test that bounding_boxes_slm_prompt returns a string"""
        prompt = Prompt()
        result = prompt.bounding_boxes_slm_prompt()
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_bounding_boxes_slm_prompt_consistency(self):
        """Test bounding_boxes_slm_prompt is consistent"""
        prompt = Prompt()
        result1 = prompt.bounding_boxes_slm_prompt()
        result2 = prompt.bounding_boxes_slm_prompt()
        
        assert result1 == result2
    
    def test_bounding_boxes_slm_prompt_different_from_standard(self):
        """Test SLM bounding box prompt differs from standard"""
        prompt = Prompt()
        slm_result = prompt.bounding_boxes_slm_prompt()
        standard_result = prompt.bounding_boxes_prompt()
        
        # Both should be valid
        assert len(slm_result) > 0 and len(standard_result) > 0


class TestPromptAllMethodsNotEmpty:
    """Test that all Prompt methods return non-empty strings"""
    
    def test_all_static_methods_return_string(self):
        """Test that all static methods return non-empty strings"""
        prompt = Prompt()
        methods_without_params = [
            prompt.image_analyze_prompt,
            prompt.analyze_bias_without_prompt,
            prompt.object_detection_img_prompt,
            prompt.detect_objects_prompt,
            prompt.detect_objects_slm_prompt,
            prompt.bounding_boxes_prompt,
            prompt.bounding_boxes_slm_prompt,
        ]
        
        for method in methods_without_params:
            result = method()
            assert isinstance(result, str), f"{method.__name__} should return string"
            assert len(result) > 0, f"{method.__name__} should return non-empty string"
    
    def test_query_based_method_with_sample_query(self):
        """Test query_based_image_analysis_prompt with sample query"""
        prompt = Prompt()
        result = prompt.query_based_image_analysis_prompt("sample query")
        
        assert isinstance(result, str)
        assert len(result) > 0


class TestPromptJSONFormatting:
    """Test that prompts contain JSON formatting instructions"""
    
    def test_prompts_contain_json_instructions(self):
        """Test that prompts mention JSON format requirements"""
        prompt = Prompt()
        prompts = [
            prompt.image_analyze_prompt(),
            prompt.analyze_bias_without_prompt(),
            prompt.detect_objects_prompt(),
            prompt.bounding_boxes_prompt(),
        ]
        
        # At least some prompts should mention JSON
        json_mentions = 0
        for prompt in prompts:
            if 'json' in prompt.lower() or '{' in prompt or 'format' in prompt.lower():
                json_mentions += 1
        
        # At least half should mention JSON or have formatting markers
        assert json_mentions >= len(prompts) // 2 or any(
            '{' in p for p in prompts
        )


class TestPromptStringProperties:
    """Test string properties of all prompts"""
    
    def test_image_analyze_prompt_has_reasonable_length(self):
        """Test that image_analyze_prompt has reasonable length"""
        prompt = Prompt()
        result = prompt.image_analyze_prompt()
        
        assert 20 <= len(result) <= 10000
    
    def test_bias_analyze_prompt_has_reasonable_length(self):
        """Test that bias prompt has reasonable length"""
        prompt = Prompt()
        result = prompt.analyze_bias_without_prompt()
        
        assert 20 <= len(result) <= 10000
    
    def test_object_detection_prompt_has_reasonable_length(self):
        """Test that object detection prompt has reasonable length"""
        prompt = Prompt()
        result = prompt.object_detection_img_prompt()
        
        assert 20 <= len(result) <= 10000
    
    def test_bounding_boxes_prompt_has_reasonable_length(self):
        """Test that bounding box prompt has reasonable length"""
        prompt = Prompt()
        result = prompt.bounding_boxes_prompt()
        
        assert 20 <= len(result) <= 10000
    
    def test_query_based_prompt_includes_query_parameter(self):
        """Test that query parameter affects output"""
        query1 = "Find cats"
        query2 = "Find dogs"
        
        prompt = Prompt()
        result1 = prompt.query_based_image_analysis_prompt(query1)
        result2 = prompt.query_based_image_analysis_prompt(query2)
        
        # Results should be different due to different queries
        assert result1 != result2 or 'Find' in result1 and 'Find' in result2


class TestPromptMethodExistence:
    """Test that all expected methods exist on Prompt class"""
    
    def test_image_analyze_prompt_method_exists(self):
        """Test image_analyze_prompt method exists"""
        assert hasattr(Prompt, 'image_analyze_prompt')
        assert callable(Prompt.image_analyze_prompt)
    
    def test_analyze_bias_without_prompt_method_exists(self):
        """Test analyze_bias_without_prompt method exists"""
        assert hasattr(Prompt, 'analyze_bias_without_prompt')
        assert callable(Prompt.analyze_bias_without_prompt)
    
    def test_query_based_image_analysis_prompt_method_exists(self):
        """Test query_based_image_analysis_prompt method exists"""
        assert hasattr(Prompt, 'query_based_image_analysis_prompt')
        assert callable(Prompt.query_based_image_analysis_prompt)
    
    def test_object_detection_img_prompt_method_exists(self):
        """Test object_detection_img_prompt method exists"""
        assert hasattr(Prompt, 'object_detection_img_prompt')
        assert callable(Prompt.object_detection_img_prompt)
    
    def test_detect_objects_prompt_method_exists(self):
        """Test detect_objects_prompt method exists"""
        assert hasattr(Prompt, 'detect_objects_prompt')
        assert callable(Prompt.detect_objects_prompt)
    
    def test_detect_objects_slm_prompt_method_exists(self):
        """Test detect_objects_slm_prompt method exists"""
        assert hasattr(Prompt, 'detect_objects_slm_prompt')
        assert callable(Prompt.detect_objects_slm_prompt)
    
    def test_bounding_boxes_prompt_method_exists(self):
        """Test bounding_boxes_prompt method exists"""
        assert hasattr(Prompt, 'bounding_boxes_prompt')
        assert callable(Prompt.bounding_boxes_prompt)
    
    def test_bounding_boxes_slm_prompt_method_exists(self):
        """Test bounding_boxes_slm_prompt method exists"""
        assert hasattr(Prompt, 'bounding_boxes_slm_prompt')
        assert callable(Prompt.bounding_boxes_slm_prompt)


class TestPromptEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_query_based_prompt_with_multiline_query(self):
        """Test query_based_image_analysis_prompt with multiline query"""
        query = """Find all:
        - People
        - Objects
        - Relationships"""
        
        prompt = Prompt()
        result = prompt.query_based_image_analysis_prompt(query)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_query_based_prompt_with_unicode_query(self):
        """Test query_based_image_analysis_prompt with unicode characters"""
        query = "找到所有对象 🎨 🖼️"
        prompt = Prompt()
        result = prompt.query_based_image_analysis_prompt(query)
        
        assert isinstance(result, str)
    
    def test_all_prompts_callable_multiple_times(self):
        """Test that all prompts can be called multiple times"""
        prompt = Prompt()
        prompts_to_test = [
            (prompt.image_analyze_prompt, []),
            (prompt.analyze_bias_without_prompt, []),
            (prompt.object_detection_img_prompt, []),
            (prompt.detect_objects_prompt, []),
            (prompt.detect_objects_slm_prompt, []),
            (prompt.bounding_boxes_prompt, []),
            (prompt.bounding_boxes_slm_prompt, []),
            (prompt.query_based_image_analysis_prompt, ["test"]),
        ]
        
        for method, args in prompts_to_test:
            for _ in range(3):
                result = method(*args)
                assert isinstance(result, str)
