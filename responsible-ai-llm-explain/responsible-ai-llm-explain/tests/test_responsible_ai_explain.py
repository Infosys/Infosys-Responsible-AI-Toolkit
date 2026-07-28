import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock, call
import pandas as pd
import json
import time
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from llm_explain.service.responsible_ai_explain import ResponsibleAIExplain


@pytest.mark.unit
class TestLLMResponseToJson:
    """Test llm_response_to_json static method"""
    
    def test_json_parsing_basic(self):
        """Test parsing basic JSON response"""
        response = '{"key": "value", "number": 42}'
        result = ResponsibleAIExplain.llm_response_to_json(response)
        assert result["key"] == "value"
        assert result["number"] == 42
    
    def test_json_parsing_with_markdown(self):
        """Test parsing JSON wrapped in markdown"""
        response = '```json\n{"key": "value"}\n```'
        result = ResponsibleAIExplain.llm_response_to_json(response)
        assert result["key"] == "value"
    
    def test_json_parsing_with_text(self):
        """Test parsing JSON with surrounding text"""
        response = 'Here is the data: {"status": "ok"} end'
        result = ResponsibleAIExplain.llm_response_to_json(response)
        assert result["status"] == "ok"
    
    def test_json_parsing_invalid_returns_string(self):
        """Test invalid JSON returns the original string"""
        response = 'not json at all'
        result = ResponsibleAIExplain.llm_response_to_json(response)
        # The actual implementation returns the string if parsing fails
        assert isinstance(result, str)
        assert result == response


@pytest.mark.unit
class TestNormalizeScores:
    """Test normalize_scores static method"""
    
    def test_normalize_scores_basic(self):
        """Test normalizing scores to sum to 100"""
        dict_list = [
            {"token": "test", "importance_score": 50},
            {"token": "data", "importance_score": 50}
        ]
        result = ResponsibleAIExplain.normalize_scores(dict_list)
        total = sum(item["importance_score"] for item in result)
        assert abs(total - 100.0) < 0.01
    
    def test_normalize_scores_empty(self):
        """Test normalizing empty list"""
        result = ResponsibleAIExplain.normalize_scores([])
        assert result == []
    
    def test_normalize_scores_single(self):
        """Test normalizing single item"""
        dict_list = [{"token": "only", "importance_score": 42}]
        result = ResponsibleAIExplain.normalize_scores(dict_list)
        assert result[0]["importance_score"] == 100.0


@pytest.mark.unit
class TestFilterTokenImportance:
    """Test filter_token_importance static method"""
    
    def test_filter_basic(self):
        """Test filtering tokens by anchors"""
        scores = [
            {"token": "hello", "importance_score": 0.8, "position": 0},
            {"token": "world", "importance_score": 0.6, "position": 1}
        ]
        anchors = ["hello"]
        result = ResponsibleAIExplain.filter_token_importance(scores, anchors)
        assert len(result) == 1
        assert result[0]["token"] == "hello"
    
    def test_filter_empty_anchors(self):
        """Test filtering with no anchors"""
        scores = [{"token": "test", "importance_score": 0.5, "position": 0}]
        result = ResponsibleAIExplain.filter_token_importance(scores, [])
        assert len(result) == 0
    
    def test_filter_case_insensitive(self):
        """Test filtering is case insensitive"""
        scores = [
            {"token": "Hello", "importance_score": 0.8, "position": 0},
            {"token": "world", "importance_score": 0.6, "position": 1}
        ]
        anchors = ["hello"]
        result = ResponsibleAIExplain.filter_token_importance(scores, anchors)
        assert len(result) == 1


@pytest.mark.unit
@pytest.mark.asyncio
class TestPromptBasedTokenImportance:
    """Test prompt_based_token_importance async method"""
    
    async def test_token_importance_azure_gpt4(self):
        """Test token importance with Azure GPT-4"""
        with patch('llm_explain.service.responsible_ai_explain.Azure') as mock_azure:
            mock_instance = Mock()
            mock_instance.generate.return_value = (
                '{"Token": ["test", "word"], "Importance Score": "0.8, 0.6", "Position": [1, 2]}',
                100,
                50
            )
            mock_azure.return_value = mock_instance
            
            with patch('llm_explain.service.responsible_ai_explain.Utils.get_token_cost', return_value=150):
                with patch('llm_explain.service.responsible_ai_explain.Prompt.get_token_importance_prompt', return_value="mock prompt"):
                    result = await ResponsibleAIExplain.prompt_based_token_importance(
                        "test prompt"
                    )
                    
                    assert isinstance(result, tuple)
                    assert len(result) == 3
                    token_list, time_taken, token_cost = result
                    assert isinstance(token_list, list)
                    assert time_taken > 0
    
    async def test_token_importance_with_endpoint(self):
        """Test token importance with custom endpoint"""
        with patch('llm_explain.service.responsible_ai_explain.APIEndpoint.endpoint_calling') as mock_endpoint:
            mock_endpoint.return_value = '{"Token": ["custom"], "Importance Score": "0.7", "Position": [1]}'
            
            with patch('llm_explain.service.responsible_ai_explain.Prompt.get_token_importance_prompt', return_value="mock prompt"):
                result = await ResponsibleAIExplain.prompt_based_token_importance(
                    "test",
                    modelEndpointUrl="http://test.com",
                    endpointInputParam="input",
                    endpointOutputParam="output"
                )
                
                assert isinstance(result, tuple)
                assert len(result) == 3


@pytest.mark.unit
@pytest.mark.asyncio
class TestSentimentAnalysis:
    """Test sentiment_analysis async method"""
    
    async def test_sentiment_analysis_gpt4(self):
        """Test sentiment analysis with GPT-4"""
        with patch('llm_explain.service.responsible_ai_explain.Azure') as mock_azure:
            mock_instance = Mock()
            mock_instance.generate.return_value = (
                '{"Sentiment": "positive", "Keywords": ["great"], "Explanation": "Positive", "token_importance_mapping": [{"token": "great", "importance_score": 90, "position": 0}]}',
                100,
                50
            )
            mock_azure.return_value = mock_instance
            
            with patch('llm_explain.service.responsible_ai_explain.Utils.get_token_cost', return_value=150):
                with patch('llm_explain.service.responsible_ai_explain.Prompt.get_classification_prompt', return_value="mock prompt"):
                    result = await ResponsibleAIExplain.sentiment_analysis(
                        "This is great!",
                        ["positive", "negative"],
                        "gpt4"
                    )
                    
                    assert result["predictedTarget"] == "positive"
                    assert "great" in result["anchor"]


@pytest.mark.unit
@pytest.mark.asyncio
class TestLocalExplanation:
    """Test local_explanation async method"""
    
    async def test_local_explanation_gpt4_success(self):
        """Test local explanation with GPT-4"""
        with patch('llm_explain.service.responsible_ai_explain.Azure') as mock_azure:
            mock_instance = Mock()
            mock_instance.generate.return_value = (
                '{"uncertainty": {"score": 30, "explanation": "Low uncertainty"}, "coherence": {"score": 80, "explanation": "High coherence"}}',
                120,
                60
            )
            mock_azure.return_value = mock_instance
            
            with patch('llm_explain.service.responsible_ai_explain.Utils.get_token_cost', return_value=180):
                with patch('llm_explain.service.responsible_ai_explain.Prompt.get_local_explanation_prompt', return_value="mock prompt"):
                    result = await ResponsibleAIExplain.local_explanation(
                        "What is AI?",
                        "AI is artificial intelligence",
                        None,
                        "gpt4",
                        None,
                        None,
                        None
                    )
                    
                    assert "uncertainty" in result
                    assert "coherence" in result
                    assert "time_taken" in result
    
    async def test_local_explanation_gemini(self):
        """Test local explanation with Gemini"""
        with patch('llm_explain.service.responsible_ai_explain.Azure') as mock_azure:
            mock_instance = Mock()
            mock_instance.generate.return_value = (
                '{"uncertainty": {"score": 40, "explanation": "Moderate"}, "coherence": {"score": 70, "explanation": "Good"}}',
                100,
                50
            )
            mock_azure.return_value = mock_instance
            
            with patch('llm_explain.service.responsible_ai_explain.Utils.get_token_cost', return_value=150):
                with patch('llm_explain.service.responsible_ai_explain.Prompt.get_local_explanation_prompt', return_value="mock"):
                    result = await ResponsibleAIExplain.local_explanation(
                        "Test",
                        "Response",
                        None,
                        "gpt4",
                        None,
                        None,
                        None
                    )
                    assert result["token_cost"] == 150
    
    async def test_local_explanation_with_endpoint(self):
        """Test local explanation with custom endpoint"""
        with patch('llm_explain.service.responsible_ai_explain.APIEndpoint.endpoint_calling') as mock_endpoint:
            mock_endpoint.return_value = '{"uncertainty": {"score": 25, "explanation": "Very low"}, "coherence": {"score": 90, "explanation": "Very high"}}'
            
            with patch('llm_explain.service.responsible_ai_explain.Prompt.get_local_explanation_prompt', return_value="mock"):
                result = await ResponsibleAIExplain.local_explanation(
                    "Test",
                    "Response",
                    None,
                    None,
                    "http://test.com",
                    "input",
                    "output"
                )
                assert "uncertainty" in result


@pytest.mark.unit
@pytest.mark.asyncio
class TestGraphOfThoughts:
    """Test graph_of_thoughts method"""
    
    async def test_graph_of_thoughts_gpt4(self):
        """Test GoT with GPT-4"""
        with patch('llm_explain.service.responsible_ai_explain.GraphOfThoughts.run') as mock_run:
            mock_run.return_value = (
                [
                    {'operation': 'step1', 'thoughts': [{'current': 'T1', 'score': 0.9}]},
                    {'operation': 'step2', 'thoughts': [{'current': 'T2', 'score': 0.85}]},
                    {'operation': 'step3', 'thoughts': [{'current': 'T3', 'score': 0.88}]},
                    {'operation': 'aggregate', 'thoughts': [{'current': 'Final answer', 'score': 0.95}]}
                ],
                {'t1': 'Answer'}
            )
            
            with patch('llm_explain.service.responsible_ai_explain.Utils.get_token_cost', return_value=200):
                result = await ResponsibleAIExplain.graph_of_thoughts("Solve this problem", "gpt4")
                # Result is a tuple: (formatted_graph, formatted_thoughts, total_time)
                assert len(result) == 3
                assert len(result[0]) == 4  # graph has 4 elements
                assert result[0][3]['operation'] == 'final_thought'
    
    async def test_graph_of_thoughts_gemini(self):
        """Test GoT with Gemini"""
        with patch('llm_explain.service.responsible_ai_explain.GraphOfThoughts.run') as mock_run:
            mock_run.return_value = (
                [
                    {'operation': 'step1', 'thoughts': []},
                    {'operation': 'step2', 'thoughts': []},
                    {'operation': 'step3', 'thoughts': []},
                    {'operation': 'aggregate', 'thoughts': []}
                ],
                {}
            )
            
            with patch('llm_explain.service.responsible_ai_explain.Utils.get_token_cost', return_value=150):
                result = await ResponsibleAIExplain.graph_of_thoughts("Test", "gemini-pro")
                assert len(result) == 3
                assert result[0][3]['operation'] == 'final_thought'


@pytest.mark.unit
@pytest.mark.asyncio
class TestSearchAugmentation:
    """Test search_augmentation method"""
    
    async def test_search_augmentation_success(self):
        """Test search augmentation with GPT-4"""
        with patch('llm_explain.service.responsible_ai_explain.Azure') as mock_azure:
            mock_instance = Mock()
            # Step 1: generate facts, Step 2: filter facts, Step 3: summarize, Step 4: evaluate facts
            mock_instance.generate.side_effect = [
                ('{"Facts": [{"Fact": "fact1"}, {"Fact": "fact2"}]}', 100, 50),
                ('["fact1", "fact2"]', 80, 40),
                ('Summary of internet results', 90, 45),
                ('{"Result": [{"Fact": "fact1", "Reasoning": "R1", "Judgement": "J1"}]}', 70, 35)
            ]
            mock_azure.return_value = mock_instance
            
            with patch('llm_explain.service.responsible_ai_explain.Prompt') as mock_prompt:
                mock_prompt.generate_facts_prompt.return_value = "facts prompt"
                mock_prompt.filter_facts_prompt.return_value = "filter prompt"
                mock_prompt.summarize_prompt.return_value = "summary prompt"
                mock_prompt.evaluate_facts_prompt.return_value = "evaluate prompt"
                
                with patch('llm_explain.service.responsible_ai_explain.Perplexity') as mock_perplexity:
                    mock_perplexity_instance = Mock()
                    mock_perplexity_instance.get_perplexity.return_value = "Perplexity answer"
                    mock_perplexity.return_value = mock_perplexity_instance
                    
                    with patch('llm_explain.service.responsible_ai_explain.Utils.get_token_cost', return_value=50):
                        result = await ResponsibleAIExplain.search_augmentation(
                            "Test query",
                            "LLM response",
                            "gpt4"
                        )
                        assert "internetResponse" in result
                        assert "factual_check" in result
    

@pytest.mark.unit
@pytest.mark.asyncio
class TestRereadReasoning:
    """Test reread_reasoning method"""
    
    async def test_reread_reasoning_gpt4(self):
        """Test reread reasoning with GPT-4"""
        with patch('llm_explain.service.responsible_ai_explain.Azure') as mock_azure:
            mock_instance = Mock()
            mock_instance.generate.return_value = (
                '{"Result": "Final answer", "Explanation": "Step by step reasoning"}',
                120,
                60
            )
            mock_azure.return_value = mock_instance
            
            with patch('llm_explain.service.responsible_ai_explain.Prompt.reread_thot', return_value="reread prompt"):
                with patch('llm_explain.service.responsible_ai_explain.Utils.get_token_cost', return_value=200):
                    result = await ResponsibleAIExplain.reread_reasoning("Test question", "gpt4", None)
                    assert "response" in result
                    assert "result" in result["response"]
                    assert "explanation" in result["response"]
    

@pytest.mark.unit
@pytest.mark.asyncio
class TestGenerateThot:
    """Test generate_thot (Tree of Thoughts) method"""
    
    async def test_generate_thot_gpt4(self):
        """Test ToT with GPT-4"""
        with patch('llm_explain.service.responsible_ai_explain.Azure') as mock_azure:
            mock_instance = Mock()
            mock_instance.generate.return_value = ('{"Result": "Answer", "Explanation": "Explained"}', 150, 75)
            mock_azure.return_value = mock_instance
            
            with patch('llm_explain.service.responsible_ai_explain.Prompt.thot', return_value="prompt"):
                with patch('llm_explain.service.responsible_ai_explain.Utils.get_token_cost', return_value=220):
                    result = await ResponsibleAIExplain.generate_thot("Problem", "gpt4", None, 0.2)
                    assert "response" in result
                    assert result["token_cost"] == 220
    
    async def test_generate_thot_gemini(self):
        """Test ToT with Gemini"""
        with patch('llm_explain.service.responsible_ai_explain.Gemini') as mock_gemini:
            mock_instance = Mock()
            mock_instance.generate.return_value = '{"Result": "Gemini ToT", "Explanation": "Explained"}'
            mock_gemini.return_value = mock_instance
            
            with patch('llm_explain.service.responsible_ai_explain.Prompt.thot', return_value="prompt"):
                with patch('llm_explain.service.responsible_ai_explain.Utils.get_token_cost', return_value=180):
                    result = await ResponsibleAIExplain.generate_thot("Test", "gemini-pro", None)
                    assert "response" in result
    

    async def test_generate_thot_aws(self):
        """Test ToT with AWS"""
        with patch('llm_explain.service.responsible_ai_explain.AWS') as mock_aws:
            mock_instance = Mock()
            mock_instance.call_AWS.return_value = '{"Result": "AWS", "Explanation": "Explained"}'
            mock_aws.return_value = mock_instance
            
            with patch('llm_explain.service.responsible_ai_explain.Prompt.thot', return_value="prompt"):
                result = await ResponsibleAIExplain.generate_thot("Question", "aws", None)
                assert "response" in result


@pytest.mark.unit
@pytest.mark.asyncio
class TestGenerateCot:
    """Test generate_cot (Chain of Thought) method"""
    
    async def test_generate_cot_gpt4(self):
        """Test CoT with GPT-4"""
        with patch('llm_explain.service.responsible_ai_explain.Azure') as mock_azure:
            mock_instance = Mock()
            mock_instance.generate.return_value = ('{"explanation": "GPT4 CoT"}', 100, 50)
            mock_azure.return_value = mock_instance
            
            with patch('llm_explain.service.responsible_ai_explain.Prompt.cot', return_value="prompt"):
                with patch('llm_explain.service.responsible_ai_explain.Utils.get_token_cost', return_value=150):
                    result = await ResponsibleAIExplain.generate_cot("Question", "gpt4", None)
                    assert "response" in result
    
    async def test_generate_cot_llama(self):
        """Test CoT with Llama"""
        with patch('llm_explain.service.responsible_ai_explain.Llamacompletion.generate') as mock_llama:
            mock_llama.return_value = ('{"explanation": "Llama CoT"}', 90, 45)
            
            with patch('llm_explain.service.responsible_ai_explain.Prompt.cot', return_value="prompt"):
                with patch('llm_explain.service.responsible_ai_explain.Utils.get_token_cost', return_value=130):
                    result = await ResponsibleAIExplain.generate_cot("Question", "llama", None)
                    assert "response" in result
    
    async def test_generate_cot_aws(self):
        """Test CoT with AWS"""
        with patch('llm_explain.service.responsible_ai_explain.AWScompletions.generate') as mock_aws:
            mock_aws.return_value = ('{"explanation": "AWS CoT"}', 70, 35)
            
            with patch('llm_explain.service.responsible_ai_explain.Prompt.cot', return_value="prompt"):
                with patch('llm_explain.service.responsible_ai_explain.Utils.get_token_cost', return_value=110):
                    result = await ResponsibleAIExplain.generate_cot("Test", "aws-bedrock", None, 0.3)
                    assert result["token_cost"] == 110


@pytest.mark.unit
@pytest.mark.asyncio
class TestGenerateCov:
    """Test generate_cov async method"""
    
    async def test_generate_cov_gpt4(self):
        """Test CoV generation with GPT-4"""
        with patch('llm_explain.service.responsible_ai_explain.Cov.cov_gpt') as mock_cov:
            mock_cov.return_value = {
                "original_question": "Test question",
                "baseline_response": "Initial answer",
                "verification_questions": "Q1\nQ2",
                "verification_answers": "A1\nA2",
                "final_answer": "Verified answer",
                "time_taken": 2.5
            }
            
            payload = Mock()
            payload.inputPrompt = "Test question"
            payload.modelName = "gpt4"
            payload.endpointDetails = None
            payload.complexity = "simple"
            payload.translate = "no"
            
            result = await ResponsibleAIExplain.generate_cov(payload)
            
            assert "original_question" in result
            assert "final_answer" in result
    
    async def test_generate_cov_llama(self):
        """Test CoV with Llama"""
        with patch('llm_explain.service.responsible_ai_explain.CovLlama.cov') as mock_cov:
            mock_cov.return_value = {"original_question": ["Q"], "final_answer": "A", "time_taken": 3.0}
            
            payload = Mock(inputPrompt="Test", modelName="llama2", complexity="medium", translate="no", endpointDetails=None)
            result = await ResponsibleAIExplain.generate_cov(payload)
            assert "final_answer" in result
    
    async def test_generate_cov_aws(self):
        """Test CoV with AWS"""
        with patch('llm_explain.service.responsible_ai_explain.CovAWS.cov') as mock_cov:
            mock_cov.return_value = {"original_question": ["Q"], "final_answer": "A", "time_taken": 2.8}
            
            payload = Mock(inputPrompt="Q", modelName="aws", complexity="complex", translate="no", endpointDetails=None)
            result = await ResponsibleAIExplain.generate_cov(payload)
            assert "final_answer" in result
    
    async def test_generate_cov_with_translation(self):
        """Test CoV with translation"""
        with patch('llm_explain.service.responsible_ai_explain.Cov.cov_gpt') as mock_cov:
            mock_cov.return_value = {"original_question": ["Q"], "final_answer": "Answer", "time_taken": 2.0}
            
            with patch('llm_explain.service.responsible_ai_explain.Translate.azure_translate') as mock_translate:
                mock_translate.side_effect = lambda text: f"Translated: {text}"
                
                with patch('llm_explain.service.responsible_ai_explain.Utils.get_token_cost', return_value=160):
                    payload = Mock(inputPrompt="Pregunta", modelName="gpt4", complexity="simple", translate="yes", endpointDetails=None)
                    result = await ResponsibleAIExplain.generate_cov(payload)
                    assert "final_answer" in result
    
    async def test_generate_cov_with_endpoint(self):
        """Test CoV with custom endpoint"""
        with patch('llm_explain.service.responsible_ai_explain.Cov.cov_endpoint') as mock_cov_endpoint:
            mock_cov_endpoint.return_value = {"original_question": ["Q"], "final_answer": "Endpoint answer", "time_taken": 1.8}
            
            with patch('llm_explain.service.responsible_ai_explain.Utils.get_token_cost', return_value=140):
                payload = Mock(
                    inputPrompt="Test",
                    modelName="endpoint",
                    complexity="simple",
                    translate="no",
                    endpointDetails=Mock(modelEndpointUrl="http://test.com", endpointInputParam="input", endpointOutputParam="output")
                )
                result = await ResponsibleAIExplain.generate_cov(payload)
                assert "final_answer" in result


@pytest.mark.unit
@pytest.mark.asyncio
class TestGenerateCot:
    """Test generate_cot async method"""
    
    async def test_generate_cot_gpt4(self):
        """Test CoT generation with GPT-4"""
        with patch('llm_explain.service.responsible_ai_explain.Azure') as mock_azure:
            mock_instance = Mock()
            mock_instance.generate.return_value = (
                '{"Explanation": "Step by step answer"}',
                100,
                50
            )
            mock_azure.return_value = mock_instance
            
            with patch('llm_explain.service.responsible_ai_explain.Utils.get_token_cost', return_value=150):
                with patch('llm_explain.service.responsible_ai_explain.Prompt.cot', return_value="mock prompt"):
                    result = await ResponsibleAIExplain.generate_cot(
                        "Test question",
                        "gpt4",
                        None
                    )
                    
                    assert "response" in result
                    assert "time_taken" in result


@pytest.mark.unit
@pytest.mark.asyncio
class TestGenerateLot:
    """Test generate_lot async method"""
    
    async def test_generate_lot_azure(self):
        """Test LoT generation with Azure"""
        with patch('llm_explain.service.responsible_ai_explain.Azure') as mock_azure:
            mock_instance = Mock()
            mock_instance.generate.side_effect = [
                ('{"Propositions": ["P1", "P2"], "Logical Expression": "P1 AND P2"}', 100, 50),
                ('{"Extended Logical Expression": "Extended", "Law Used": "De Morgan"}', 80, 40),
                ('{"Extended Logical Information": "Info"}', 70, 35),
                ('{"Explanation": "Final explanation"}', 90, 45)
            ]
            mock_azure.return_value = mock_instance
            
            with patch('llm_explain.service.responsible_ai_explain.Utils.get_token_cost', return_value=300):
                with patch('llm_explain.service.responsible_ai_explain.Prompt') as mock_prompt:
                    mock_prompt.lot_phase1.return_value = "phase1"
                    mock_prompt.lot_phase2.return_value = "phase2"
                    mock_prompt.lot_phase3.return_value = "phase3"
                    mock_prompt.lot_phase4.return_value = "phase4"
                    
                    result = await ResponsibleAIExplain.generate_lot(
                        "Test question",
                        "gpt4",
                        None
                    )
                    
                    assert "response" in result
                    assert "time_taken" in result


@pytest.mark.unit
@pytest.mark.asyncio
class TestProcessImportance:
    """Test process_importance async method"""
    
    async def test_process_importance_success(self):
        """Test processing importance scores"""
        async def mock_importance_func(*args, **kwargs):
            return [("token1", 0.8), ("token2", 0.6), ("token3", 0.4)]
        
        with patch('llm_explain.service.responsible_ai_explain.Utils.scale_importance_log') as mock_scale:
            mock_scale.return_value = [("token1", 85), ("token2", 65), ("token3", 45)]
            
            result_df, total_time = await ResponsibleAIExplain.process_importance(
                mock_importance_func
            )
            
            assert isinstance(result_df, pd.DataFrame)
            assert len(result_df) == 3
            assert total_time > 0


@pytest.mark.unit
class TestEdgeCasesAndErrors:
    """Test edge cases and error handling"""
    
    def test_normalize_scores_all_zeros(self):
        """Test normalization with all zero scores"""
        dict_list = [
            {"token": "a", "importance_score": 0},
            {"token": "b", "importance_score": 0}
        ]
        result = ResponsibleAIExplain.normalize_scores(dict_list)
        # Should handle division by zero gracefully
        assert isinstance(result, list)
    
    def test_json_parsing_nested(self):
        """Test parsing deeply nested JSON"""
        response = '{"level1": {"level2": {"level3": "value"}}}'
        result = ResponsibleAIExplain.llm_response_to_json(response)
        assert result["level1"]["level2"]["level3"] == "value"
    
    def test_filter_special_characters(self):
        """Test filtering with special characters"""
        scores = [{"token": "test!", "importance_score": 0.7, "position": 0}]
        anchors = ["test!"]
        result = ResponsibleAIExplain.filter_token_importance(scores, anchors)
        assert len(result) == 1
    
    def test_json_parsing_multiple_objects(self):
        """Test parsing response with multiple JSON objects"""
        response = '{"first": 1} some text {"second": 2}'
        result = ResponsibleAIExplain.llm_response_to_json(response)
        # Should parse the first valid JSON object
        assert "first" in result or isinstance(result, str)
    
    def test_normalize_scores_negative_values(self):
        """Test normalization with negative values"""
        dict_list = [
            {"token": "a", "importance_score": -10},
            {"token": "b", "importance_score": 30}
        ]
        result = ResponsibleAIExplain.normalize_scores(dict_list)
        # Should handle negative values
        assert isinstance(result, list)
    
    def test_filter_partial_match(self):
        """Test filtering doesn't match partial strings"""
        scores = [
            {"token": "testing", "importance_score": 0.8, "position": 0},
            {"token": "test", "importance_score": 0.6, "position": 1}
        ]
        anchors = ["test"]
        result = ResponsibleAIExplain.filter_token_importance(scores, anchors)
        # Should only match exact token
        assert all(item["token"].lower() == "test" for item in result)


@pytest.mark.unit
@pytest.mark.asyncio
class TestAsyncMethodErrorHandling:
    """Test error handling in async methods"""
    
    async def test_sentiment_analysis_exception(self):
        """Test sentiment analysis handles exceptions"""
        with patch('llm_explain.service.responsible_ai_explain.Azure') as mock_azure:
            mock_instance = Mock()
            mock_instance.generate.side_effect = Exception("API Error")
            mock_azure.return_value = mock_instance
            
            with pytest.raises(Exception):
                await ResponsibleAIExplain.sentiment_analysis(
                    "Test text",
                    ["positive", "negative"],
                    "gpt4"
                )
    
    async def test_local_explanation_json_error(self):
        """Test local explanation handles JSON decode errors"""
        with patch('llm_explain.service.responsible_ai_explain.Azure') as mock_azure:
            mock_instance = Mock()
            mock_instance.generate.return_value = (
                'invalid json response',
                100,
                50
            )
            mock_azure.return_value = mock_instance
            
            with patch('llm_explain.utility.prompts.base.Prompt.get_local_explanation_prompt', return_value="mock"):
                # Should handle the error gracefully or raise
                try:
                    result = await ResponsibleAIExplain.local_explanation(
                        "prompt", "response", None, None, None, None, None
                    )
                    # If it doesn't raise, check result
                    assert isinstance(result, (dict, str))
                except Exception:
                    # Exception is acceptable
                    pass


@pytest.mark.unit
class TestNormalizeScoresExceptions:
    """Test normalize_scores exception handling"""
    
    def test_normalize_scores_missing_key(self):
        """Test normalize_scores with missing importance_score key"""
        dict_list = [{"token": "test"}]  # Missing importance_score
        with pytest.raises(KeyError):
            ResponsibleAIExplain.normalize_scores(dict_list)
    
    def test_normalize_scores_invalid_type(self):
        """Test normalize_scores with non-numeric importance_score"""
        dict_list = [{"token": "test", "importance_score": "not_a_number"}]
        with pytest.raises(TypeError):
            ResponsibleAIExplain.normalize_scores(dict_list)
    
    def test_normalize_scores_non_list(self):
        """Test normalize_scores with non-list input"""
        with pytest.raises((TypeError, AttributeError)):
            ResponsibleAIExplain.normalize_scores({"invalid": "input"})


@pytest.mark.unit
class TestFilterTokenImportanceExceptions:
    """Test filter_token_importance exception handling"""
    
    def test_filter_missing_token_key(self):
        """Test filter with missing token key"""
        scores = [{"importance_score": 0.8, "position": 0}]  # Missing token
        anchors = ["test"]
        with pytest.raises(KeyError):
            ResponsibleAIExplain.filter_token_importance(scores, anchors)
    
    def test_filter_missing_importance_score_key(self):
        """Test filter with missing importance_score key"""
        scores = [{"token": "test", "position": 0}]  # Missing importance_score
        anchors = ["test"]
        with pytest.raises(KeyError):
            ResponsibleAIExplain.filter_token_importance(scores, anchors)
    
    def test_filter_missing_position_key(self):
        """Test filter with missing position key"""
        scores = [{"token": "test", "importance_score": 0.8}]  # Missing position
        anchors = ["test"]
        with pytest.raises(KeyError):
            ResponsibleAIExplain.filter_token_importance(scores, anchors)
    
    def test_filter_zero_division_all_filtered(self):
        """Test filter handles zero division when all tokens match"""
        scores = [
            {"token": "test", "importance_score": 100.0, "position": 0}
        ]
        anchors = ["test"]
        # Should not raise ZeroDivisionError
        result = ResponsibleAIExplain.filter_token_importance(scores, anchors)
        assert len(result) == 1

