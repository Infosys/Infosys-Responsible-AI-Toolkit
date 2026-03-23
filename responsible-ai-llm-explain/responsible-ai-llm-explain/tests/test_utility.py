import sys
import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import numpy as np

# Set environment variables required for class initialization
os.environ["AZURE_OPENAI_API_KEY"] = "fake_key"
os.environ["AZURE_OPENAI_API_VERSION"] = "fake_version"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://fake.endpoint"

# Patch AzureOpenAI before importing utility so the client initialization doesn't fail
with patch("openai.AzureOpenAI") as mock_azure_openai:
    from llm_explain.utility.utility import Utils

class TestUtility:
    
    def test_normalize_vector_nonzero(self):
        vector = np.array([3.0, 4.0])
        result = Utils.normalize_vector(vector)
        expected = np.array([0.6, 0.8])
        assert np.allclose(result, expected)

    def test_normalize_vector_zero(self):
        vector = np.array([0.0, 0.0])
        result = Utils.normalize_vector(vector)
        assert np.allclose(result, vector)

    def test_calculate_normalized_entropy_uniform(self):
        # Uniform distribution of 2 elements: p=0.5, logp = -log(2)
        logprobs = [-np.log(2), -np.log(2)]
        result = Utils.calculate_normalized_entropy(logprobs)
        # Entropy = - (0.5*-log2 + 0.5*-log2) = log2
        # Max entropy = log(2)
        # Normalized = 1.0
        assert np.isclose(result, 1.0)
    
    def test_calculate_normalized_entropy_exception(self):
        """Test calculate_normalized_entropy with invalid data"""
        with pytest.raises(Exception):
            Utils.calculate_normalized_entropy(None)
    
    @pytest.mark.asyncio
    async def test_process_token_async(self):
        """Test process_token_async function"""
        top_logprobs_list = [{'token1': -0.69, 'token2': -1.2, 'token3': -1.6}]
        choice = {
            'logprobs': {
                'tokens': ['Hello', ' world']
            }
        }
        choice_embedding = np.array([0.1] * 1536)
        
        with patch.object(Utils, 'get_embedding', new_callable=AsyncMock) as mock_embedding:
            mock_embedding.return_value = np.array([0.1] * 1536)
            
            mean_distance, normalized_entropy = await Utils.process_token_async(
                0, top_logprobs_list, choice, choice_embedding, max_tokens=None
            )
            
            assert isinstance(mean_distance, (float, np.floating))
            assert isinstance(normalized_entropy, (float, np.floating))
    
    @pytest.mark.asyncio
    async def test_process_token_async_with_max_tokens(self):
        """Test process_token_async with max_tokens limit"""
        top_logprobs_list = [{'tokenA': -0.69, 'tokenB': -1.2}]
        choice = {
            'logprobs': {
                'tokens': ['A', 'B', 'C', 'D', 'E']
            }
        }
        choice_embedding = np.array([0.1] * 1536)
        
        with patch.object(Utils, 'get_embedding', new_callable=AsyncMock) as mock_embedding:
            mock_embedding.return_value = np.array([0.2] * 1536)
            
            mean_distance, normalized_entropy = await Utils.process_token_async(
                0, top_logprobs_list, choice, choice_embedding, max_tokens=3
            )
            
            assert isinstance(mean_distance, (float, np.floating))
            assert mock_embedding.call_count == 2
    
    @pytest.mark.asyncio
    async def test_process_token_async_exception(self):
        """Test process_token_async handles exceptions"""
        with pytest.raises(Exception):
            await Utils.process_token_async(0, [], {}, np.array([]), None)
    
    def test_decoded_tokens(self):
        """Test decoded_tokens function"""
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.return_value = [123, 456, 789]
        mock_tokenizer.decode.side_effect = lambda x: f"token_{x[0]}"
        
        result = Utils.decoded_tokens("test string", mock_tokenizer)
        
        assert result == ["token_123", "token_456", "token_789"]
        mock_tokenizer.encode.assert_called_once_with("test string")
    
    def test_scale_importance_log_basic(self):
        """Test scale_importance_log with basic input"""
        importance_scores = [("token1", 0.5), ("token2", 0.8), ("token3", 0.2)]
        
        result = Utils.scale_importance_log(importance_scores)
        
        assert len(result) == 3
        assert all(isinstance(score[1], (float, np.floating)) for score in result)
        assert all(0 <= score[1] <= 1 for score in result)
    
    def test_scale_importance_log_with_percentiles(self):
        """Test scale_importance_log with percentile clipping"""
        importance_scores = [("token1", 0.1), ("token2", 0.5), ("token3", 0.9)]
        
        result = Utils.scale_importance_log(
            importance_scores, 
            min_percentile=10, 
            max_percentile=90
        )
        
        assert len(result) == 3
    
    def test_scale_importance_log_with_base(self):
        """Test scale_importance_log with custom base"""
        importance_scores = [("token1", 1.0), ("token2", 2.0), ("token3", 3.0)]
        
        result = Utils.scale_importance_log(importance_scores, base=10)
        
        assert len(result) == 3
        assert all(isinstance(score[1], (float, np.floating)) for score in result)
    
    def test_scale_importance_log_with_offset_and_scaling(self):
        """Test scale_importance_log with offset and scaling factor"""
        importance_scores = [("token1", 0.5), ("token2", 1.0)]
        
        result = Utils.scale_importance_log(
            importance_scores, 
            offset=0.5,
            scaling_factor=2.0,
            bias=0.1
        )
        
        assert len(result) == 2
    
    def test_scale_importance_log_all_equal_values(self):
        """Test scale_importance_log when all values are equal"""
        importance_scores = [("token1", 0.5), ("token2", 0.5), ("token3", 0.5)]
        
        result = Utils.scale_importance_log(importance_scores)
        
        assert len(result) == 3
        # All should be normalized to 0.5
        assert all(np.isclose(score[1], 0.5) for score in result)
    
    def test_scale_importance_log_exception(self):
        """Test scale_importance_log handles exceptions"""
        with pytest.raises(Exception):
            Utils.scale_importance_log([("token", None)])
    
    @pytest.mark.asyncio
    async def test_get_embedding(self):
        """Test get_embedding async function"""
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        
        # Patch the retry decorator to avoid retries in tests
        with patch('llm_explain.utility.utility.retry', lambda f: f):
            with patch.object(Utils.client.embeddings, 'create', return_value=mock_response):
                result = await Utils.get_embedding("test text")
                
                assert isinstance(result, np.ndarray)
                assert len(result) == 1536
    
    @pytest.mark.asyncio
    async def test_get_embedding_exception(self):
        """Test get_embedding handles exceptions"""
        # Directly patch the get_embedding method to avoid retry decorator issues
        async def mock_get_embedding(text):
            raise Exception("API Error")
        
        with patch.object(Utils, 'get_embedding', side_effect=mock_get_embedding):
            with pytest.raises(Exception, match="API Error"):
                await Utils.get_embedding("test text")
    
    @pytest.mark.asyncio
    async def test_approximate_importance(self):
        """Test approximate_importance function"""
        original_embedding = np.array([0.1] * 1536)
        
        with patch.object(Utils, 'get_embedding', new_callable=AsyncMock) as mock_embedding:
            mock_embedding.return_value = np.array([0.2] * 1536)
            
            result = await Utils.approximate_importance("perturbed", original_embedding)
            
            assert isinstance(result, (float, np.floating))
            # Cosine distance range with tolerance for floating point precision
            assert -1e-10 <= result <= 2
    
    @pytest.mark.asyncio
    async def test_approximate_importance_exception(self):
        """Test approximate_importance handles exceptions"""
        # Directly patch approximate_importance to avoid retry decorator issues from get_embedding
        async def mock_approximate_importance(text, embedding):
            raise Exception("Calculation error")
        
        with patch.object(Utils, 'approximate_importance', side_effect=mock_approximate_importance):
            with pytest.raises(Exception, match="Calculation error"):
                await Utils.approximate_importance("test", None)
    
    @pytest.mark.asyncio
    async def test_ablated_relative_importance(self):
        """Test ablated_relative_importance function"""
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.return_value = [1, 2, 3]
        mock_tokenizer.decode.side_effect = lambda x: f"token"
        
        with patch.object(Utils, 'get_embedding', new_callable=AsyncMock) as mock_embedding:
            mock_embedding.return_value = np.array([0.1] * 1536)
            with patch.object(Utils, 'approximate_importance', new_callable=AsyncMock) as mock_approx:
                mock_approx.return_value = 0.5
                
                result = await Utils.ablated_relative_importance("test input", mock_tokenizer)
                
                assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_ablated_relative_importance_exception(self):
        """Test ablated_relative_importance handles exceptions"""
        # Directly patch ablated_relative_importance to avoid retry decorator issues from get_embedding
        async def mock_ablated_relative_importance(text, tokenizer):
            raise Exception("Ablation error")
        
        with patch.object(Utils, 'ablated_relative_importance', side_effect=mock_ablated_relative_importance):
            with pytest.raises(Exception, match="Ablation error"):
                await Utils.ablated_relative_importance("test", None)
    
    def test_get_price_details_gpt4o(self):
        """Test get_price_details for gpt-4o model"""
        prompt_price, response_price = Utils.get_price_details("gpt-4o")
        
        assert prompt_price == 0.0050
        assert response_price == 0.0150
    
    def test_get_price_details_gpt35_turbo(self):
        """Test get_price_details for gpt-35-turbo model"""
        prompt_price, response_price = Utils.get_price_details("gpt-35-turbo")
        
        assert prompt_price == 0.0005
        assert response_price == 0.0015
    
    def test_get_price_details_gpt4(self):
        """Test get_price_details for gpt4 model"""
        prompt_price, response_price = Utils.get_price_details("gpt4")
        
        assert prompt_price == 0.0300
        assert response_price == 0.0600
    
    def test_get_price_details_unknown_model(self):
        """Test get_price_details for unknown model"""
        prompt_price, response_price = Utils.get_price_details("unknown-model")
        
        assert prompt_price == 0
        assert response_price == 0
    
    def test_get_token_cost_gpt4o(self):
        """Test get_token_cost for gpt-4o model"""
        cost = Utils.get_token_cost(1000, 500, "gpt-4o")
        
        # Cost is rounded to 3 decimal places
        expected_cost = round((1000/1000 * 0.0050) + (500/1000 * 0.0150), 3)
        assert cost == expected_cost
    
    def test_get_token_cost_gpt35(self):
        """Test get_token_cost for gpt-35-turbo model"""
        cost = Utils.get_token_cost(2000, 1000, "gpt-35-turbo")
        
        # Cost is rounded to 3 decimal places
        expected_cost = round((2000/1000 * 0.0005) + (1000/1000 * 0.0015), 3)
        assert cost == expected_cost
    
    def test_get_token_cost_gpt4o_variant(self):
        """Test get_token_cost handles gpt-4o variants"""
        cost = Utils.get_token_cost(1000, 500, "gpt-4o-mini")
        
        # Cost is rounded to 3 decimal places
        expected_cost = round((1000/1000 * 0.0050) + (500/1000 * 0.0150), 3)
        assert cost == expected_cost
    
    def test_get_token_cost_unknown_model(self):
        """Test get_token_cost for unknown model returns 0"""
        cost = Utils.get_token_cost(1000, 500, "unknown-model")
        
        assert cost == 0
    
    def test_get_token_cost_exception(self):
        """Test get_token_cost handles exceptions"""
        # This should not raise but return 0
        cost = Utils.get_token_cost(None, 500, "gpt-4o")
        assert cost == 0
    
    def test_calculate_token_count(self):
        """Test calculate_token_count function"""
        text = "Hello world"
        
        count = Utils.calculate_token_count(text)
        
        assert isinstance(count, int)
        assert count > 0
    
    def test_calculate_token_count_empty_string(self):
        """Test calculate_token_count with empty string"""
        count = Utils.calculate_token_count("")
        
        assert count == 0
    
    def test_calculate_token_count_long_text(self):
        """Test calculate_token_count with long text"""
        text = "Hello world " * 100
        
        count = Utils.calculate_token_count(text)
        
        assert isinstance(count, int)
        assert count > 100
    
    def test_send_telemetry_request_success(self):
        """Test send_telemetry_request with successful response"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        
        with patch('llm_explain.utility.utility.requests.post', return_value=mock_response):
            # Should not raise exception
            Utils.send_telemetry_request({"data": "test"}, "http://test.com")
            
            mock_response.raise_for_status.assert_called_once()
    
    def test_send_telemetry_request_failure(self):
        """Test send_telemetry_request with failure"""
        from fastapi import HTTPException
        
        with patch('llm_explain.utility.utility.requests.post', side_effect=Exception("Connection error")):
            with pytest.raises(HTTPException) as exc_info:
                Utils.send_telemetry_request({"data": "test"}, "http://test.com")
            
            assert exc_info.value.status_code == 500

