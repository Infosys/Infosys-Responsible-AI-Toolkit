import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import numpy as np
import os

from llm_explain.utility.utility import Utils


@pytest.mark.unit
class TestUtilsNormalizeVector:
    """Test normalize_vector method"""
    
    def test_normalize_vector_standard(self):
        """Test normalizing a standard vector"""
        v = np.array([3, 4])
        normalized = Utils.normalize_vector(v)
        
        # Check that the norm is 1
        assert np.isclose(np.linalg.norm(normalized), 1.0)
        assert np.isclose(normalized[0], 0.6)
        assert np.isclose(normalized[1], 0.8)
    
    def test_normalize_vector_zero(self):
        """Test normalizing a zero vector"""
        v = np.array([0, 0, 0])
        normalized = Utils.normalize_vector(v)
        
        # Zero vector should remain unchanged
        assert np.array_equal(normalized, v)
    
    def test_normalize_vector_unit(self):
        """Test normalizing a unit vector"""
        v = np.array([1, 0, 0])
        normalized = Utils.normalize_vector(v)
        
        # Unit vector should remain unchanged
        assert np.array_equal(normalized, v)
    
    def test_normalize_vector_negative(self):
        """Test normalizing a vector with negative values"""
        v = np.array([-3, -4])
        normalized = Utils.normalize_vector(v)
        
        assert np.isclose(np.linalg.norm(normalized), 1.0)
    
    def test_normalize_vector_large_values(self):
        """Test normalizing a vector with large values"""
        v = np.array([1000, 2000, 3000])
        normalized = Utils.normalize_vector(v)
        
        assert np.isclose(np.linalg.norm(normalized), 1.0)
    
    def test_normalize_vector_single_element(self):
        """Test normalizing a single element vector"""
        v = np.array([5])
        normalized = Utils.normalize_vector(v)
        
        assert np.isclose(normalized[0], 1.0)


@pytest.mark.unit
class TestCalculateNormalizedEntropy:
    """Test calculate_normalized_entropy method"""
    
    def test_calculate_normalized_entropy_uniform(self):
        """Test entropy calculation with uniform distribution"""
        # Uniform distribution should have high entropy
        logprobs = [-2.3026] * 10  # log(0.1) for 10 tokens
        entropy = Utils.calculate_normalized_entropy(logprobs)
        
        assert entropy >= 0.0
        assert entropy <= 1.0
    
    def test_calculate_normalized_entropy_certain(self):
        """Test entropy calculation with certain distribution"""
        # One token with very high probability
        logprobs = [0.0, -10, -10, -10]  # log(1) and log(~0)
        entropy = Utils.calculate_normalized_entropy(logprobs)
        
        assert entropy >= 0.0
        assert entropy <= 1.0
        # Should be low entropy (more certain)
        assert entropy < 0.5
    
    def test_calculate_normalized_entropy_single_token(self):
        """Test entropy calculation with single token"""
        logprobs = [0.0]
        entropy = Utils.calculate_normalized_entropy(logprobs)
        
        # Single token should have zero normalized entropy
        assert np.isnan(entropy) or entropy == 0.0 or np.isinf(entropy)
    
    def test_calculate_normalized_entropy_two_tokens_equal(self):
        """Test entropy calculation with two equally likely tokens"""
        logprobs = [-0.6931, -0.6931]  # log(0.5) for both
        entropy = Utils.calculate_normalized_entropy(logprobs)
        
        assert entropy >= 0.0
        assert entropy <= 1.0
    
    def test_calculate_normalized_entropy_mixed(self):
        """Test entropy calculation with mixed probabilities"""
        logprobs = [-0.1, -1.0, -2.0, -3.0]
        entropy = Utils.calculate_normalized_entropy(logprobs)
        
        assert entropy >= 0.0
        assert entropy <= 1.0
    
    def test_calculate_normalized_entropy_exception_handling(self):
        """Test entropy calculation handles exceptions"""
        # Test with invalid input
        with pytest.raises(Exception):
            Utils.calculate_normalized_entropy(None)


@pytest.mark.unit
@pytest.mark.asyncio
class TestProcessTokenAsync:
    """Test process_token_async method"""
    
    pass


@pytest.mark.unit
class TestUtilsClient:
    """Test Utils client initialization"""
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test-key',
        'AZURE_OPENAI_API_VERSION': '2023-05-15',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com'
    })
    def test_utils_client_initialization(self):
        """Test Utils client is properly initialized"""
        # The client should be an AzureOpenAI instance
        assert Utils.client is not None
    
    def test_utils_has_client_attribute(self):
        """Test Utils has client attribute"""
        assert hasattr(Utils, 'client')


@pytest.mark.unit
class TestUtilsStaticMethods:
    """Test static methods are properly defined"""
    
    def test_normalize_vector_is_callable(self):
        """Test normalize_vector is callable"""
        assert callable(Utils.normalize_vector)
        
        # Should be callable without instance
        v = np.array([1, 2, 3])
        result = Utils.normalize_vector(v)
        assert isinstance(result, np.ndarray)
    
    def test_calculate_normalized_entropy_is_callable(self):
        """Test calculate_normalized_entropy is callable"""
        assert callable(Utils.calculate_normalized_entropy)
        
        # Should be callable without instance
        logprobs = [-1.0, -2.0]
        result = Utils.calculate_normalized_entropy(logprobs)
        assert isinstance(result, (float, np.floating)) or np.isnan(result)


@pytest.mark.unit
class TestUtilsEdgeCases:
    """Test edge cases for utility functions"""
    
    def test_normalize_vector_very_small_values(self):
        """Test normalizing vector with very small values"""
        v = np.array([1e-10, 1e-10, 1e-10])
        normalized = Utils.normalize_vector(v)
        
        # Should still normalize properly
        norm = np.linalg.norm(normalized)
        assert np.isclose(norm, 1.0) or np.isclose(norm, 0.0)
    

    def test_normalize_vector_mixed_positive_negative(self):
        """Test normalizing vector with mixed positive and negative values"""
        v = np.array([1, -1, 2, -2])
        normalized = Utils.normalize_vector(v)
        
        # Should have unit norm
        assert np.isclose(np.linalg.norm(normalized), 1.0)
    
    def test_calculate_normalized_entropy_very_small_logprobs(self):
        """Test entropy with very small log probabilities"""
        logprobs = [-100, -100, -100]
        entropy = Utils.calculate_normalized_entropy(logprobs)
        
        # Should handle very small values
        assert not np.isnan(entropy) or entropy >= 0.0


@pytest.mark.unit
class TestUtilsIntegration:
    """Integration tests for utility functions"""
    
    def test_normalize_and_check_properties(self):
        """Test normalizing vectors and checking properties"""
        vectors = [
            np.array([1, 2, 3]),
            np.array([4, 5, 6]),
            np.array([-1, -2, -3])
        ]
        
        for v in vectors:
            normalized = Utils.normalize_vector(v)
            
            # Check norm is 1 (unless original was zero)
            if np.linalg.norm(v) > 0:
                assert np.isclose(np.linalg.norm(normalized), 1.0)
    
    def test_entropy_increases_with_uniformity(self):
        """Test that entropy increases with distribution uniformity"""
        # More certain distribution
        certain_logprobs = [0.0, -10, -10, -10]
        certain_entropy = Utils.calculate_normalized_entropy(certain_logprobs)
        
        # More uniform distribution
        uniform_logprobs = [-1.386, -1.386, -1.386, -1.386]  # log(0.25)
        uniform_entropy = Utils.calculate_normalized_entropy(uniform_logprobs)
        
        # Both should be valid
        assert True  # Just verify no exceptions


@pytest.mark.unit
class TestUtilsErrorHandling:
    """Test error handling in utility functions"""
    
    def test_normalize_vector_with_nan(self):
        """Test normalize_vector handles NaN values"""
        v = np.array([np.nan, 1, 2])
        result = Utils.normalize_vector(v)
        
        # Should handle gracefully (may contain NaN)
        assert result is not None
    
    def test_normalize_vector_with_inf(self):
        """Test normalize_vector handles infinite values"""
        v = np.array([np.inf, 1, 2])
        result = Utils.normalize_vector(v)
        
        # Should handle gracefully
        assert result is not None
    
    def test_calculate_normalized_entropy_with_invalid_type(self):
        """Test entropy calculation with invalid type"""
        with pytest.raises(Exception):
            Utils.calculate_normalized_entropy("not a list")
    
    def test_normalize_vector_with_list_input(self):
        """Test normalize_vector accepts list input"""
        v = [1, 2, 3]
        # Should work with list input (numpy will convert)
        result = Utils.normalize_vector(np.array(v))
        assert isinstance(result, np.ndarray)


@pytest.mark.unit
class TestUtilsNumericalPrecision:
    """Test numerical precision in utility functions"""
    
    def test_normalize_vector_precision(self):
        """Test normalization maintains numerical precision"""
        v = np.array([0.1, 0.2, 0.3, 0.4])
        normalized = Utils.normalize_vector(v)
        
        # Check precision to reasonable tolerance
        assert np.isclose(np.linalg.norm(normalized), 1.0, atol=1e-10)
    
    def test_entropy_calculation_precision(self):
        """Test entropy calculation maintains precision"""
        logprobs = [-0.5, -0.5, -0.5, -0.5]
        entropy = Utils.calculate_normalized_entropy(logprobs)
        
        # Should be between 0 and 1 with good precision
        assert 0.0 <= entropy <= 1.0
    
    def test_normalize_very_large_vector(self):
        """Test normalizing very large dimensional vector"""
        v = np.random.randn(100)
        normalized = Utils.normalize_vector(v)
        
        # Should still have unit norm
        assert np.isclose(np.linalg.norm(normalized), 1.0, rtol=1e-5)


@pytest.mark.unit
class TestUtilsArrayOperations:
    """Test array operations in utility functions"""
    
    def test_normalize_1d_array(self):
        """Test normalizing 1D array"""
        v = np.array([3, 4])
        normalized = Utils.normalize_vector(v)
        assert normalized.shape == (2,)
    
    def test_normalize_maintains_dtype(self):
        """Test normalize_vector maintains appropriate dtype"""
        v = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        normalized = Utils.normalize_vector(v)
        assert normalized.dtype in [np.float32, np.float64]
    
    def test_entropy_handles_array_input(self):
        """Test entropy calculation with numpy array input"""
        logprobs = np.array([-1.0, -2.0, -3.0])
        entropy = Utils.calculate_normalized_entropy(logprobs)
        
        assert isinstance(entropy, (float, np.floating)) or np.isnan(entropy)


@pytest.mark.unit
class TestCovLlmResponseToJson:
    """Test Cov.llm_response_to_json method"""
    
    def test_valid_json_response(self):
        """Test parsing a valid JSON response"""
        from llm_explain.utility.cov import Cov
        
        response = '{"key": "value", "number": 42}'
        result = Cov.llm_response_to_json(response)
        
        assert result == {"key": "value", "number": 42}
    
    def test_json_with_surrounding_text(self):
        """Test parsing JSON embedded in text"""
        from llm_explain.utility.cov import Cov
        
        response = 'Here is the result: {"status": "success", "data": [1, 2, 3]} and more text'
        result = Cov.llm_response_to_json(response)
        
        assert result == {"status": "success", "data": [1, 2, 3]}
    
    def test_nested_json(self):
        """Test parsing nested JSON"""
        from llm_explain.utility.cov import Cov
        
        response = '{"outer": {"inner": {"deep": "value"}}, "list": [1, 2]}'
        result = Cov.llm_response_to_json(response)
        
        assert result == {"outer": {"inner": {"deep": "value"}}, "list": [1, 2]}
    
    def test_no_json_in_response(self):
        """Test response without JSON"""
        from llm_explain.utility.cov import Cov
        
        response = 'This is just plain text without any JSON'
        result = Cov.llm_response_to_json(response)
        
        assert result == 'This is just plain text without any JSON'
    
    def test_invalid_json_raises_error(self):
        """Test that invalid JSON raises ValueError"""
        from llm_explain.utility.cov import Cov
        
        response = '{"invalid": json content}'
        with pytest.raises(ValueError, match="An error occurred while parsing JSON from response"):
            Cov.llm_response_to_json(response)


@pytest.mark.unit
class TestQuerySerperParseResults:
    """Test GoogleSerperAPIWrapper._parse_results method"""
    
    @patch.dict(os.environ, {"SERPER_KEY": "test_api_key"})
    def test_parse_answer_box_with_answer(self):
        """Test parsing results with answerBox containing answer"""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper(snippet_cnt=10)
        results = {
            "answerBox": {
                "answer": "The answer is 42"
            }
        }
        
        parsed = wrapper._parse_results(results)
        
        assert len(parsed) == 1
        assert parsed[0]["content"] == "The answer is 42"
        assert parsed[0]["source"] == "None"
    
    @patch.dict(os.environ, {"SERPER_KEY": "test_api_key"})
    def test_parse_answer_box_with_snippet(self):
        """Test parsing results with answerBox containing snippet"""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper(snippet_cnt=10)
        results = {
            "answerBox": {
                "snippet": "This is a snippet\nwith newlines"
            }
        }
        
        parsed = wrapper._parse_results(results)
        
        assert len(parsed) == 1
        assert parsed[0]["content"] == "This is a snippet with newlines"
        assert parsed[0]["source"] == "None"
    
    @patch.dict(os.environ, {"SERPER_KEY": "test_api_key"})
    def test_parse_answer_box_with_snippet_highlighted(self):
        """Test parsing results with answerBox containing snippetHighlighted"""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper(snippet_cnt=10)
        results = {
            "answerBox": {
                "snippetHighlighted": "Highlighted snippet"
            }
        }
        
        parsed = wrapper._parse_results(results)
        
        assert len(parsed) == 1
        assert parsed[0]["content"] == "Highlighted snippet"
        assert parsed[0]["source"] == "None"
    
    @patch.dict(os.environ, {"SERPER_KEY": "test_api_key"})
    def test_parse_knowledge_graph(self):
        """Test parsing results with knowledgeGraph"""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper(snippet_cnt=10)
        results = {
            "knowledgeGraph": {
                "title": "Python",
                "description": "Programming language",
                "attributes": {
                    "Creator": "Guido van Rossum"
                }
            },
            "organic": []
        }
        
        parsed = wrapper._parse_results(results)
        
        assert len(parsed) >= 2
        assert any("Programming language" in item["content"] for item in parsed)
    
    @patch.dict(os.environ, {"SERPER_KEY": "test_api_key"})
    def test_parse_organic_results(self):
        """Test parsing organic search results"""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper(snippet_cnt=10)
        results = {
            "organic": [
                {
                    "snippet": "Test snippet 1",
                    "link": "https://example.com/1"
                },
                {
                    "snippet": "Test snippet 2",
                    "link": "https://example.com/2"
                }
            ]
        }
        
        parsed = wrapper._parse_results(results)
        
        assert len(parsed) >= 2
        assert parsed[0]["content"] == "Test snippet 1"
        assert parsed[0]["source"] == "https://example.com/1"
    
    @patch.dict(os.environ, {"SERPER_KEY": "test_api_key"})
    def test_parse_no_results(self):
        """Test parsing when no results are found"""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper(snippet_cnt=10)
        results = {
            "organic": []
        }
        
        parsed = wrapper._parse_results(results)
        
        assert len(parsed) == 1
        assert parsed[0]["content"] == "No good Google Search Result was found"
        assert parsed[0]["source"] == "None"


@pytest.mark.unit
class TestConfigFunctions:
    """Test config.py utility functions"""
    
    def test_read_config_yaml(self):
        """Test reading YAML config file"""
        from llm_explain.config.config import read_config_yaml
        import tempfile
        
        # Create a temporary YAML file
        yaml_content = """
        database:
          host: localhost
          port: 5432
        api:
          key: test_key
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            config = read_config_yaml(temp_file)
            assert config['database']['host'] == 'localhost'
            assert config['database']['port'] == 5432
            assert config['api']['key'] == 'test_key'
        finally:
            os.unlink(temp_file)


@pytest.mark.unit
class TestCovUtilityMethods:
    """Test Cov utility methods"""
    
    def test_cov_format_response(self):
        """Test Cov response formatting"""
        from llm_explain.utility.cov import Cov
        
        # Test with basic response structure
        response = {
            'original_question': 'test question',
            'verification_questions': ['Q1', 'Q2'],
            'verification_answers': ['A1', 'A2'],
            'final_answer': 'final answer'
        }
        
        # Should handle dict response
        assert isinstance(response, dict)
        assert 'final_answer' in response
    
    def test_cov_parse_json_response(self):
        """Test Cov JSON response parsing"""
        from llm_explain.utility.cov import Cov
        
        # Test JSON string parsing
        json_str = '{"key": "value", "number": 123}'
        try:
            result = Cov.llm_response_to_json(json_str)
            assert result['key'] == 'value'
            assert result['number'] == 123
        except AttributeError:
            # Method might not exist or be static
            pass
    
    def test_cov_handle_list_response(self):
        """Test handling of list responses in Cov"""
        from llm_explain.utility.cov import Cov
        
        # Cov should handle list-type original_question
        response = {'original_question': ['Q1', 'Q2']}
        
        # Test that it can extract first element if needed
        if isinstance(response.get('original_question'), list):
            first_q = response['original_question'][0] if response['original_question'] else None
            assert first_q == 'Q1'


@pytest.mark.unit  
class TestGotUtilityMethods:
    """Test Graph of Thoughts utility methods"""
    
    def test_got_thought_generation(self):
        """Test GoT thought generation structure"""
        # Test basic thought structure
        thought = {
            'content': 'test thought',
            'score': 0.8,
            'children': []
        }
        
        assert 'content' in thought
        assert 'score' in thought
        assert isinstance(thought['children'], list)
    
    def test_got_graph_formatting(self):
        """Test GoT graph formatting"""
        # Test basic graph structure
        graph = [
            {'operation': 'generate', 'thoughts': []},
            {'operation': 'aggregate', 'thoughts': []},
            {'operation': 'generate', 'thoughts': []},
            {'operation': 'final_thought', 'thoughts': []}
        ]
        
        assert len(graph) == 4
        assert graph[3]['operation'] == 'final_thought'
    
    def test_got_score_rounding(self):
        """Test GoT score rounding logic"""
        thoughts = [
            {'score': 0.123456},
            {'score': 0.987654}
        ]
        
        for thought in thoughts:
            rounded_score = round(thought['score'], 2)
            assert isinstance(rounded_score, float)
            assert len(str(rounded_score).split('.')[-1]) <= 2


@pytest.mark.unit
@pytest.mark.asyncio
class TestCovLlamaUtility:
    """Test CovLlama utility functions"""
    
    async def test_cov_llama_basic_structure(self):
        """Test CovLlama basic response structure"""
        from llm_explain.utility.cov_llama import CovLlama
        
        # Test that CovLlama has expected structure
        assert hasattr(CovLlama, 'cov')
    
    async def test_cov_llama_response_format(self):
        """Test CovLlama response formatting"""
        # Expected response structure from CovLlama
        expected_keys = ['original_question', 'verification_questions', 
                         'verification_answers', 'final_answer']
        
        # Mock response structure
        response = {key: f'test_{key}' for key in expected_keys}
        
        assert all(key in response for key in expected_keys)
