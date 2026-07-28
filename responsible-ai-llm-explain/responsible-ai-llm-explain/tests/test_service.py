"""
Unit tests for service module
Tests ExplainService methods with mocks
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import pandas as pd
import time

from llm_explain.service.service import ExplainService, Payload
from llm_explain.mappers.mappers import (
    TokenImportanceRequest, TokenImportanceResponse,
    UncertainityRequest, UncertainityResponse,
    GoTRequest, GoTResponse,
    SafeSearchRequest, SafeSearchResponse,
    SentimentAnalysisRequest, SentimentAnalysisResponse,
    rereadRequest, rereadResponse,
    CoTResponse, CoVRequest, CoVResponse,
    lotRequest, lotResponse,
    EndPointRequest
)


@pytest.mark.unit
class TestPayloadClass:
    """Test Payload class"""
    
    def test_payload_creation_with_dict(self):
        """Test creating Payload from dictionary"""
        data = {"key1": "value1", "key2": "value2"}
        payload = Payload(**data)
        assert payload.key1 == "value1"
        assert payload.key2 == "value2"
    
    def test_payload_empty_dict(self):
        """Test creating Payload with empty dict"""
        payload = Payload()
        assert payload.__dict__ == {}
    
    def test_payload_nested_dict(self):
        """Test Payload with nested dictionary"""
        data = {"outer": {"inner": "value"}}
        payload = Payload(**data)
        assert payload.outer == {"inner": "value"}


@pytest.mark.unit
class TestGetLabelMethod:
    """Test get_label static method"""
    
    def test_get_label_less_score(self):
        """Test get_label with low score"""
        assert ExplainService.get_label(20) == "Less"
        assert ExplainService.get_label(30) == "Less"
    
    def test_get_label_moderately_score(self):
        """Test get_label with moderate score"""
        assert ExplainService.get_label(50) == "Moderately"
        assert ExplainService.get_label(70) == "Moderately"
    
    def test_get_label_highly_score(self):
        """Test get_label with high score"""
        assert ExplainService.get_label(80) == "Highly"
        assert ExplainService.get_label(100) == "Highly"
    
    def test_get_label_reverse_highly(self):
        """Test get_label with reverse=True for low scores"""
        assert ExplainService.get_label(20, reverse=True) == "Highly"
        assert ExplainService.get_label(30, reverse=True) == "Highly"
    
    def test_get_label_reverse_moderately(self):
        """Test get_label with reverse=True for moderate scores"""
        assert ExplainService.get_label(50, reverse=True) == "Moderately"
        assert ExplainService.get_label(70, reverse=True) == "Moderately"
    
    def test_get_label_reverse_less(self):
        """Test get_label with reverse=True for high scores"""
        assert ExplainService.get_label(80, reverse=True) == "Less"
        assert ExplainService.get_label(100, reverse=True) == "Less"
    
    def test_get_label_boundary_values(self):
        """Test get_label at boundary values"""
        assert ExplainService.get_label(31) == "Moderately"
        assert ExplainService.get_label(71) == "Highly"
    
    def test_get_label_with_float_conversion(self):
        """Test get_label converts float to int"""
        assert ExplainService.get_label(25.7) == "Less"
        assert ExplainService.get_label(75.3) == "Highly"


@pytest.mark.unit
@pytest.mark.asyncio
class TestTokenImportance:
    """Test token_importance method"""
    
    @pytest.mark.asyncio
    async def test_token_importance_with_gpt_model(self, sample_token_importance_request, mock_token_importance_response):
        """Test token_importance with GPT model"""
        with patch('llm_explain.service.service.ResponsibleAIExplain.prompt_based_token_importance') as mock_method:
            mock_method.return_value = (
                mock_token_importance_response["token_importance_mapping"],
                mock_token_importance_response["time_taken"],
                mock_token_importance_response["token_cost"]
            )
            
            request = TokenImportanceRequest(**sample_token_importance_request)
            response = await ExplainService.token_importance(request)
            
            assert isinstance(response, TokenImportanceResponse)
            assert response.time_taken == 1.5
            assert response.token_cost == 100
            assert len(response.token_importance_mapping) == 2
    
    @pytest.mark.asyncio
    async def test_token_importance_with_code_model(self):
        """Test token_importance with code model"""
        with patch('llm_explain.service.service.ResponsibleAIExplain.process_importance') as mock_process:
            mock_df = pd.DataFrame({
                'word': ['test', 'code'],
                'importance_value': [0.8, 0.6],
                'Position': [0, 1]
            })
            mock_process.return_value = (mock_df, 1.0)
            
            with patch('llm_explain.service.service.joblib.load') as mock_joblib:
                mock_joblib.return_value = Mock()
                
                request = TokenImportanceRequest(
                    inputPrompt="test",
                    modelName="code"
                )
                response = await ExplainService.token_importance(request)
                
                assert isinstance(response, TokenImportanceResponse)
                assert response.time_taken == 1.0
    
    @pytest.mark.asyncio
    async def test_token_importance_with_custom_endpoint(self):
        """Test token_importance with custom endpoint"""
        with patch('llm_explain.service.service.ResponsibleAIExplain.prompt_based_token_importance') as mock_method:
            mock_method.return_value = ([{"word": "test", "importance": 0.9}], 2.0, 150)
            
            endpoint = EndPointRequest(
                modelEndpointUrl="http://test.com",
                endpointInputParam={"input": "test"},
                endpointOutputParam="output"
            )
            request = TokenImportanceRequest(
                inputPrompt="test prompt",
                modelName="GPT",
                endpointDetails=endpoint
            )
            response = await ExplainService.token_importance(request)
            
            assert response.token_cost == 150
            mock_method.assert_called_once()
    
    @pytest.mark.asyncio

    
    @pytest.mark.asyncio
    async def test_token_importance_exception_handling(self):
        """Test token_importance handles exceptions"""
        with patch('llm_explain.service.service.ResponsibleAIExplain.prompt_based_token_importance') as mock_method:
            mock_method.side_effect = Exception("Test error")
            
            request = TokenImportanceRequest(
                inputPrompt="test",
                modelName="GPT"
            )
            
            with pytest.raises(Exception):
                await ExplainService.token_importance(request)


@pytest.mark.unit
@pytest.mark.asyncio
class TestSentimentAnalysis:
    """Test sentiment_analysis method"""
    
    @pytest.mark.asyncio
    async def test_sentiment_analysis_success(self):
        """Test sentiment_analysis with successful response"""
        with patch('llm_explain.service.service.ResponsibleAIExplain.sentiment_analysis') as mock_sentiment:
            mock_sentiment.return_value = {
                "sentiment": "positive",
                "score": 0.9,
                "explanation": "Positive sentiment detected"
            }
            
            request = SentimentAnalysisRequest(
                inputPrompt="This is great!",
                modelName="gpt4"
            )
            response = await ExplainService.sentiment_analysis(request)
            
            assert isinstance(response, SentimentAnalysisResponse)
            assert len(response.explanation) == 1
            mock_sentiment.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_sentiment_analysis_negative_text(self):
        """Test sentiment_analysis with negative text"""
        with patch('llm_explain.service.service.ResponsibleAIExplain.sentiment_analysis') as mock_sentiment:
            mock_sentiment.return_value = {
                "sentiment": "negative",
                "score": 0.2
            }
            
            request = SentimentAnalysisRequest(
                inputPrompt="This is terrible!",
                modelName="gpt4"
            )
            response = await ExplainService.sentiment_analysis(request)
            
            assert isinstance(response, SentimentAnalysisResponse)
            assert response.explanation[0]["sentiment"] == "negative"
    
    @pytest.mark.asyncio
    async def test_sentiment_analysis_exception_handling(self):
        """Test sentiment_analysis exception handling"""
        with patch('llm_explain.service.service.ResponsibleAIExplain.sentiment_analysis') as mock_sentiment:
            mock_sentiment.side_effect = Exception("Sentiment analysis failed")
            
            request = SentimentAnalysisRequest(
                inputPrompt="Test",
                modelName="gpt4"
            )
            
            with pytest.raises(Exception):
                await ExplainService.sentiment_analysis(request)


@pytest.mark.unit
@pytest.mark.asyncio
class TestLocalExplanation:
    """Test local_explanation method"""
    
    @pytest.mark.asyncio
    async def test_local_explanation_success(self):
        """Test local_explanation with successful response"""
        with patch('llm_explain.service.service.ResponsibleAIExplain.local_explanation') as mock_local:
            mock_local.return_value = {
                'uncertainty': {'score': 40, 'explanation': 'Test'},
                'coherence': {'score': 80, 'explanation': 'Test'},
                'time_taken': 2.0,
                'token_cost': 150
            }
            
            request = UncertainityRequest(
                inputPrompt="What is AI?",
                response="AI is artificial intelligence",
                context=None,
                modelName="gpt4"
            )
            response = await ExplainService.local_explanation(request)
            
            assert isinstance(response, UncertainityResponse)
            assert 'uncertainty_level' in response.uncertainty
            assert 'coherence_level' in response.coherence
            assert response.time_taken == 2.0
    
    @pytest.mark.asyncio
    async def test_local_explanation_with_endpoint(self):
        """Test local_explanation with custom endpoint"""
        with patch('llm_explain.service.service.ResponsibleAIExplain.local_explanation') as mock_local:
            mock_local.return_value = {
                'uncertainty': {'score': 25, 'explanation': 'Low uncertainty'},
                'coherence': {'score': 90, 'explanation': 'High coherence'},
                'time_taken': 1.5,
                'token_cost': 100
            }
            
            endpoint = EndPointRequest(
                modelEndpointUrl="http://test.com",
                endpointInputParam={"input": "test"},
                endpointOutputParam="output"
            )
            request = UncertainityRequest(
                inputPrompt="Test",
                response="Test response",
                context=None,
                modelName=None,
                endpointDetails=endpoint
            )
            response = await ExplainService.local_explanation(request)
            
            assert isinstance(response, UncertainityResponse)
            assert "Certain" in response.uncertainty['uncertainty_level']
            assert "Coherent" in response.coherence['coherence_level']
    
    @pytest.mark.asyncio
    async def test_local_explanation_label_generation(self):
        """Test local_explanation generates correct labels"""
        with patch('llm_explain.service.service.ResponsibleAIExplain.local_explanation') as mock_local:
            mock_local.return_value = {
                'uncertainty': {'score': 20, 'explanation': 'Test'},
                'coherence': {'score': 85, 'explanation': 'Test'},
                'time_taken': 1.0,
                'token_cost': 80
            }
            
            request = UncertainityRequest(
                inputPrompt="Test",
                response="Response",
                context=None,
                modelName=None,
                endpointDetails=None
            )
            response = await ExplainService.local_explanation(request)
            
            assert "Highly Certain" in response.uncertainty['uncertainty_level']
            assert "Highly Coherent" in response.coherence['coherence_level']


@pytest.mark.unit
@pytest.mark.asyncio
class TestGraphOfThoughts:
    """Test graph_of_thoughts method"""
    
    @pytest.mark.asyncio
    async def test_graph_of_thoughts_success(self):
        """Test graph_of_thoughts with successful response"""
        with patch('llm_explain.service.service.ResponsibleAIExplain.graph_of_thoughts') as mock_got:
            mock_graph = [
                {
                    'operation': 'final_thought',
                    'thoughts': [{'current': 'thought1', 'score': 85}],
                    'prompt_tokens': 100,
                    'completion_tokens': 50
                }
            ]
            mock_thoughts = {'thought1': 'The final answer is...'}
            mock_got.return_value = (mock_graph, mock_thoughts, 3.0)
            
            with patch('llm_explain.service.service.Utils.get_token_cost') as mock_cost:
                mock_cost.return_value = 200
                
                request = GoTRequest(
                    inputPrompt="Solve this problem",
                    modelName="gpt4"
                )
                response = await ExplainService.graph_of_thoughts(request)
                
                assert isinstance(response, GoTResponse)
                assert response.final_thought == 'The final answer is...'
                assert response.token_cost == 200
                assert response.time_taken == 3.0
    
    @pytest.mark.asyncio
    async def test_graph_of_thoughts_score_adjustment_low(self):
        """Test graph_of_thoughts adjusts low scores"""
        with patch('llm_explain.service.service.ResponsibleAIExplain.graph_of_thoughts') as mock_got:
            mock_graph = [
                {
                    'operation': 'final_thought',
                    'thoughts': [{'current': 'thought1', 'score': 40}],
                    'prompt_tokens': 100,
                    'completion_tokens': 50
                }
            ]
            mock_thoughts = {'thought1': 'Answer'}
            mock_got.return_value = (mock_graph, mock_thoughts, 2.0)
            
            with patch('llm_explain.service.service.Utils.get_token_cost', return_value=150):
                request = GoTRequest(inputPrompt="Test", modelName="gpt4")
                response = await ExplainService.graph_of_thoughts(request)
                
                assert response.score == 85  # 40 + 45
    
    @pytest.mark.asyncio
    async def test_graph_of_thoughts_score_adjustment_high(self):
        """Test graph_of_thoughts adjusts high scores"""
        with patch('llm_explain.service.service.ResponsibleAIExplain.graph_of_thoughts') as mock_got:
            mock_graph = [
                {
                    'operation': 'final_thought',
                    'thoughts': [{'current': 'thought1', 'score': 150}],
                    'prompt_tokens': 100,
                    'completion_tokens': 50
                }
            ]
            mock_thoughts = {'thought1': 'Answer'}
            mock_got.return_value = (mock_graph, mock_thoughts, 2.0)
            
            with patch('llm_explain.service.service.Utils.get_token_cost', return_value=150):
                request = GoTRequest(inputPrompt="Test", modelName="gpt4")
                response = await ExplainService.graph_of_thoughts(request)
                
                assert response.score == 95
    
    @pytest.mark.asyncio
    async def test_graph_of_thoughts_no_final_thought(self):
        """Test graph_of_thoughts handles missing final thought"""
        with patch('llm_explain.service.service.ResponsibleAIExplain.graph_of_thoughts') as mock_got:
            mock_graph = [
                {
                    'operation': 'generate',
                    'thoughts': [],
                    'prompt_tokens': 100,
                    'completion_tokens': 50
                }
            ]
            mock_got.return_value = (mock_graph, {}, 1.0)
            
            with patch('llm_explain.service.service.Utils.get_token_cost', return_value=100):
                request = GoTRequest(inputPrompt="Test", modelName="gpt4")
                
                with pytest.raises(Exception, match="Final thought or value not found"):
                    await ExplainService.graph_of_thoughts(request)


@pytest.mark.unit
@pytest.mark.asyncio
class TestSearchAugmentation:
    """Test search_augmentation method"""
    
    @pytest.mark.asyncio
    async def test_search_augmentation_success(self):
        """Test search_augmentation with verified facts"""
        with patch('llm_explain.service.service.ResponsibleAIExplain.search_augmentation') as mock_search:
            mock_search.return_value = {
                'internetResponse': 'Internet result',
                'factual_check': {
                    'Score': 0.9,
                    'explanation_factual_accuracy': {
                        'Result': [
                            {'Fact': 'Test fact', 'Judgement': 'yes'},
                            {'Fact': 'Another fact', 'Judgement': 'no'}
                        ]
                    }
                },
                'time_taken': 2.5,
                'token_cost': 180
            }
            
            payload = SafeSearchRequest(
                inputPrompt="Test query",
                llm_response="Test response",
                modelName="gpt4"
            )
            response = await ExplainService.search_augmentation(payload)
            
            assert isinstance(response, SafeSearchResponse)
            assert len(response.internetResponse) == 1
            assert response.metrics[0]['metricName'] == 'Factuality Check'
            assert response.metrics[0]['score'] == 0.9
    
    @pytest.mark.asyncio
    async def test_search_augmentation_no_facts_found(self):
        """Test search_augmentation when no facts found"""
        with patch('llm_explain.service.service.ResponsibleAIExplain.search_augmentation') as mock_search:
            mock_search.return_value = {
                'internetResponse': 'No results',
                'factual_check': {
                    'Score': 0.0,
                    'explanation_factual_accuracy': {
                        'Result': ['No facts found in the LLM response.']
                    }
                },
                'time_taken': 1.0,
                'token_cost': 50
            }
            
            payload = SafeSearchRequest(
                inputPrompt="Test",
                llm_response="Response",
                modelName="gpt4"
            )
            response = await ExplainService.search_augmentation(payload)
            
            assert response.metrics[0]['explanation'] == ['No facts found in the LLM response.']
    
    @pytest.mark.asyncio
    async def test_search_augmentation_judgement_replacement(self):
        """Test search_augmentation replaces judgement values correctly"""
        with patch('llm_explain.service.service.ResponsibleAIExplain.search_augmentation') as mock_search:
            mock_search.return_value = {
                'internetResponse': 'Results',
                'factual_check': {
                    'Score': 0.7,
                    'explanation_factual_accuracy': {
                        'Result': [
                            {'Fact': 'Fact1', 'Judgement': 'yes'},
                            {'Fact': 'Fact2', 'Judgement': 'no'},
                            {'Fact': 'Fact3', 'Judgement': 'unclear'}
                        ]
                    }
                },
                'time_taken': 2.0,
                'token_cost': 120
            }
            
            payload = SafeSearchRequest(
                inputPrompt="Query",
                llm_response="Response",
                modelName="gpt4"
            )
            response = await ExplainService.search_augmentation(payload)
            
            explanations = response.metrics[0]['explanation']
            assert explanations[0]['Judgement'] == 'Fact Verified'
            assert explanations[1]['Judgement'] == 'Fact Not Verified'
            assert explanations[2]['Judgement'] == 'Fact Unclear'


@pytest.mark.unit
@pytest.mark.asyncio
class TestRereadReasoning:
    """Test reread_reasoning method"""
    
    @pytest.mark.asyncio
    async def test_reread_reasoning_success(self):
        """Test reread reasoning with GPT model"""
        with patch('llm_explain.service.service.ResponsibleAIExplain.reread_reasoning') as mock_method:
            mock_method.return_value = {
                "response": {"answer": "Final answer after rereading", "reasoning": "Step by step reasoning"},
                "time_taken": 2.5,
                "token_cost": 180
            }
            
            request = rereadRequest(
                inputPrompt="Solve this problem",
                modelName="gpt4"
            )
            
            result = await ExplainService.reread_reasoning(request)
            
            assert isinstance(result, rereadResponse)
            assert result.response["answer"] == "Final answer after rereading"
            assert result.time_taken == 2.5
            assert result.token_cost == 180
            mock_method.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_reread_reasoning_with_endpoint(self):
        """Test reread reasoning with custom endpoint"""
        with patch('llm_explain.service.service.ResponsibleAIExplain.reread_reasoning') as mock_method:
            mock_method.return_value = {
                "response": {"answer": "Endpoint answer", "reasoning": "Endpoint reasoning"},
                "time_taken": 1.8,
                "token_cost": 0
            }
            
            endpoint_details = EndPointRequest(
                modelEndpointUrl="http://test.com",
                endpointInputParam={"input_parameter": "inputs"},
                endpointOutputParam="output"
            )
            
            request = rereadRequest(
                inputPrompt="Question",
                modelName=None,
                endpointDetails=endpoint_details
            )
            
            result = await ExplainService.reread_reasoning(request)
            
            assert result.response["answer"] == "Endpoint answer"
            assert result.time_taken == 1.8
    
    @pytest.mark.asyncio
    async def test_reread_reasoning_gemini(self):
        """Test reread reasoning with Gemini model"""
        with patch('llm_explain.service.service.ResponsibleAIExplain.reread_reasoning') as mock_method:
            mock_method.return_value = {
                "response": {"answer": "Gemini answer", "reasoning": "Gemini reasoning process"},
                "time_taken": 2.0,
                "token_cost": 160
            }
            
            request = rereadRequest(
                inputPrompt="Logic problem",
                modelName="gemini-pro"
            )
            
            result = await ExplainService.reread_reasoning(request)
            
            assert result.response["answer"] == "Gemini answer"
            assert result.token_cost == 160


@pytest.mark.unit
class TestEdgeCasesAndBoundaries:
    """Test edge cases and boundary conditions"""
    
    def test_get_label_boundary_30(self):
        """Test get_label at boundary value 30"""
        assert ExplainService.get_label(30) == "Less"
        assert ExplainService.get_label(30, reverse=True) == "Highly"
    
    def test_get_label_boundary_70(self):
        """Test get_label at boundary value 70"""
        assert ExplainService.get_label(70) == "Moderately"
        assert ExplainService.get_label(70, reverse=True) == "Moderately"
    
    def test_get_label_with_string_number(self):
        """Test get_label converts string to int"""
        assert ExplainService.get_label("50") == "Moderately"
        assert ExplainService.get_label("90") == "Highly"


@pytest.mark.unit
class TestThreadOfThoughtReasoning:
    """Test Thread of Thought reasoning service method"""
    
    @pytest.mark.asyncio
    @patch('llm_explain.service.service.ResponsibleAIExplain.generate_thot')
    async def test_thot_reasoning_success(self, mock_generate_thot):
        """Test successful ThoT reasoning"""
        mock_generate_thot.return_value = {
            'response': {'answer': 'ThoT result', 'reasoning': 'step by step'},
            'time_taken': 2.5,
            'token_cost': 0.003
        }
        
        request = Mock(
            inputPrompt="Test question",
            modelName="gpt4",
            endpointDetails=None,
            temperature="0.7"
        )
        
        result = await ExplainService.thot_reasoning(request)
        
        assert isinstance(result, rereadResponse)
        assert result.response == {'answer': 'ThoT result', 'reasoning': 'step by step'}
        assert result.time_taken == 2.5
        assert result.token_cost == 0.003
        mock_generate_thot.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('llm_explain.service.service.ResponsibleAIExplain.generate_thot')
    async def test_thot_reasoning_exception(self, mock_generate_thot):
        """Test ThoT reasoning exception handling"""
        mock_generate_thot.side_effect = Exception("ThoT failed")
        
        request = Mock(
            inputPrompt="Test",
            modelName="gpt4",
            endpointDetails=None,
            temperature="0.7"
        )
        
        with pytest.raises(Exception) as exc_info:
            await ExplainService.thot_reasoning(request)
        
        assert str(exc_info.value) == "ThoT failed"


@pytest.mark.unit
class TestChainOfThoughtReasoning:
    """Test Chain of Thought reasoning service method"""
    
    @pytest.mark.asyncio
    @patch('llm_explain.service.service.ResponsibleAIExplain.generate_cot')
    async def test_cot_reasoning_success(self, mock_generate_cot):
        """Test successful CoT reasoning"""
        mock_generate_cot.return_value = {
            'response': 'Russia is the largest country',
            'time_taken': 1.8,
            'token_cost': 0.002
        }
        
        request = Mock(
            inputPrompt="Which is the biggest country?",
            modelName="gpt4",
            endpointDetails=None,
            temperature="0.7"
        )
        
        result = await ExplainService.cot_reasoning(request)
        
        assert isinstance(result, CoTResponse)
        assert result.explanation == 'Russia is the largest country'
        assert result.time_taken == 1.8
        mock_generate_cot.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('llm_explain.service.service.ResponsibleAIExplain.generate_cot')
    async def test_cot_reasoning_exception(self, mock_generate_cot):
        """Test CoT reasoning exception handling"""
        mock_generate_cot.side_effect = Exception("CoT failed")
        
        request = Mock(
            inputPrompt="Test",
            modelName="gpt4",
            endpointDetails=None,
            temperature="0.7"
        )
        
        with pytest.raises(Exception) as exc_info:
            await ExplainService.cot_reasoning(request)
        
        assert str(exc_info.value) == "CoT failed"


@pytest.mark.unit
class TestChainOfVerificationReasoning:
    """Test Chain of Verification reasoning service method"""
    
    @pytest.mark.asyncio
    @patch('llm_explain.service.service.ResponsibleAIExplain.generate_cov')
    async def test_cov_reasoning_success(self, mock_generate_cov):
        """Test successful CoV reasoning"""
        mock_generate_cov.return_value = {
            'original_question': 'Which is the biggest country?',
            'baseline_response': 'Russia',
            'verification_questions': '1. What is Russia\'s area?',
            'verification_answers': '1. 17,098,242 sq km',
            'final_answer': 'Russia is the largest country by area',
            'time_taken': 3.2,
            'token_cost': 0.005
        }
        
        request = Mock(
            inputPrompt="Which is the biggest country?",
            complexity="simple",
            modelName="gpt4",
            translate="no"
        )
        
        result = await ExplainService.cov_reasoning(request)
        
        assert isinstance(result, CoVResponse)
        assert result.original_question == 'Which is the biggest country?'
        assert result.final_answer == 'Russia is the largest country by area'
        assert result.time_taken == 3.2
        mock_generate_cov.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('llm_explain.service.service.ResponsibleAIExplain.generate_cov')
    async def test_cov_reasoning_exception(self, mock_generate_cov):
        """Test CoV reasoning exception handling"""
        mock_generate_cov.side_effect = Exception("CoV failed")
        
        request = Mock()
        
        with pytest.raises(Exception) as exc_info:
            await ExplainService.cov_reasoning(request)
        
        assert str(exc_info.value) == "CoV failed"


@pytest.mark.unit
class TestLogicOfThoughtReasoning:
    """Test Logic of Thought reasoning service method"""
    
    @pytest.mark.asyncio
    @patch('llm_explain.service.service.ResponsibleAIExplain.generate_lot')
    async def test_lot_reasoning_success_with_llm_response(self, mock_generate_lot):
        """Test successful LoT reasoning with llmResponse"""
        mock_generate_lot.return_value = {
            'response': {'logic': 'Logical analysis', 'steps': ['step1', 'step2']},
            'time_taken': 2.1,
            'token_cost': 0.002
        }
        
        request = lotRequest(
            inputPrompt="Question",
            llmResponse="Initial answer",
            modelName="gpt4"
        )
        
        result = await ExplainService.lot_reasoning(request)
        
        assert isinstance(result, lotResponse)
        assert result.response == {'logic': 'Logical analysis', 'steps': ['step1', 'step2']}
        assert result.time_taken == 2.1
        mock_generate_lot.assert_called_once_with(
            text="QuestionInitial answer",
            modelName="gpt4",
            endpointDetails=None
        )
    
    @pytest.mark.asyncio
    @patch('llm_explain.service.service.ResponsibleAIExplain.generate_lot')
    async def test_lot_reasoning_success_without_llm_response(self, mock_generate_lot):
        """Test successful LoT reasoning without llmResponse"""
        mock_generate_lot.return_value = {
            'response': {'logic': 'Logical analysis'},
            'time_taken': 1.9,
            'token_cost': 0.001
        }
        
        request = lotRequest(
            inputPrompt="Question only",
            llmResponse=None,
            modelName="gpt4"
        )
        
        result = await ExplainService.lot_reasoning(request)
        
        assert isinstance(result, lotResponse)
        assert result.time_taken == 1.9
        mock_generate_lot.assert_called_once_with(
            text="Question only",
            modelName="gpt4",
            endpointDetails=None
        )
    
    @pytest.mark.asyncio
    @patch('llm_explain.service.service.ResponsibleAIExplain.generate_lot')
    async def test_lot_reasoning_exception(self, mock_generate_lot):
        """Test LoT reasoning exception handling"""
        mock_generate_lot.side_effect = Exception("LoT failed")
        
        request = lotRequest(
            inputPrompt="Test",
            llmResponse=None,
            modelName="gpt4"
        )
        
        with pytest.raises(Exception) as exc_info:
            await ExplainService.lot_reasoning(request)
        
        assert str(exc_info.value) == "LoT failed"


@pytest.mark.unit
class TestRereadReasoning:
    """Test reread_reasoning method"""
    
    @pytest.mark.asyncio
    @patch('llm_explain.service.service.ResponsibleAIExplain.reread_reasoning')
    async def test_reread_reasoning_success(self, mock_reread):
        """Test reread reasoning success"""
        mock_reread.return_value = {
            'response': {'answer': 'Reread analysis', 'confidence': 0.95},
            'time_taken': 1.8,
            'token_cost': 0.0025
        }
        
        request = rereadRequest(
            inputPrompt="Who founded Microsoft?",
            modelName="GPT4"
        )
        
        result = await ExplainService.reread_reasoning(request)
        
        assert isinstance(result, rereadResponse)
        assert result.response == {'answer': 'Reread analysis', 'confidence': 0.95}
        assert result.time_taken == 1.8
        assert result.token_cost == 0.0025
        mock_reread.assert_called_once_with(
            text="Who founded Microsoft?",
            modelName="GPT4",
            endpointDetails=None
        )
    
    @pytest.mark.asyncio
    @patch('llm_explain.service.service.ResponsibleAIExplain.reread_reasoning')
    async def test_reread_reasoning_with_endpoint(self, mock_reread):
        """Test reread reasoning with custom endpoint"""
        mock_reread.return_value = {
            'response': {'analysis': 'Custom endpoint result'},
            'time_taken': 2.3,
            'token_cost': 0.003
        }
        
        endpoint_details = EndPointRequest(
            modelEndpointUrl="http://custom:8000/model",
            endpointInputParam={"input": "text"},
            endpointOutputParam="output"
        )
        
        request = rereadRequest(
            inputPrompt="Test prompt",
            modelName="custom",
            endpointDetails=endpoint_details
        )
        
        result = await ExplainService.reread_reasoning(request)
        
        assert isinstance(result, rereadResponse)
        assert result.response == {'analysis': 'Custom endpoint result'}
        mock_reread.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('llm_explain.service.service.ResponsibleAIExplain.reread_reasoning')
    async def test_reread_reasoning_exception(self, mock_reread):
        """Test reread reasoning exception handling"""
        mock_reread.side_effect = Exception("Reread failed")
        
        request = rereadRequest(
            inputPrompt="Test",
            modelName="gpt4"
        )
        
        with pytest.raises(Exception) as exc_info:
            await ExplainService.reread_reasoning(request)
        
        assert str(exc_info.value) == "Reread failed"


@pytest.mark.unit
class TestTokenImportanceCustomEndpoint:
    """Test token_importance with custom endpoint paths"""
    
    @pytest.mark.asyncio
    @patch('llm_explain.service.service.ResponsibleAIExplain.prompt_based_token_importance')
    async def test_token_importance_gpt_default(self, mock_token_importance):
        """Test token importance with GPT default path"""
        mock_token_importance.return_value = (
            [{"token": "test", "score": 0.8}],
            1.2,
            0.0015
        )
        
        request = TokenImportanceRequest(
            inputPrompt="Default GPT test",
            modelName="GPT"
        )
        
        result = await ExplainService.token_importance(request)
        
        assert isinstance(result, TokenImportanceResponse)
        assert result.time_taken == 1.2
        assert result.token_cost == 0.0015
        mock_token_importance.assert_called_once_with("Default GPT test")


@pytest.mark.asyncio
class TestLocalExplanation:
    """Test local_explanation method"""
    
    @patch('llm_explain.service.service.ResponsibleAIExplain.local_explanation')
    async def test_local_explanation_success(self, mock_local_explanation):
        """Test local explanation with successful response"""
        mock_local_explanation.return_value = {
            'uncertainty': {
                'score': 0.7,
                'explanation': 'Test uncertainty'
            },
            'coherence': {
                'score': 0.8,
                'explanation': 'Test coherence'
            },
            'time_taken': 1.5
        }
        
        request = UncertainityRequest(
            inputPrompt="Test prompt",
            response="Test response",
            modelName="gpt4"
        )
        
        result = await ExplainService.local_explanation(request)
        
        assert isinstance(result, UncertainityResponse)
        assert 'Certain' in result.uncertainty['uncertainty_level']
        assert 'Coherent' in result.coherence['coherence_level']
    
    @patch('llm_explain.service.service.ResponsibleAIExplain.local_explanation')
    async def test_local_explanation_exception(self, mock_local_explanation):
        """Test local explanation with exception"""
        mock_local_explanation.side_effect = Exception("API error")
        
        request = UncertainityRequest(
            inputPrompt="Test prompt",
            response="Test response",
            modelName="gpt4"
        )
        
        with pytest.raises(Exception, match="API error"):
            await ExplainService.local_explanation(request)


@pytest.mark.asyncio
class TestGraphOfThoughts:
    """Test graph_of_thoughts method"""
    
    @patch('llm_explain.service.service.ResponsibleAIExplain.graph_of_thoughts')
    async def test_graph_of_thoughts_exception(self, mock_got):
        """Test graph of thoughts with exception"""
        mock_got.side_effect = Exception("Graph processing error")
        
        request = GoTRequest(
            inputPrompt="Test prompt",
            modelName="gpt4"
        )
        
        with pytest.raises(Exception, match="Graph processing error"):
            await ExplainService.graph_of_thoughts(request)


@pytest.mark.asyncio
class TestSentimentAnalysis:
    """Test sentiment_analysis method"""
    
    @patch('llm_explain.service.service.ResponsibleAIExplain.sentiment_analysis')
    async def test_sentiment_analysis_exception(self, mock_sentiment):
        """Test sentiment analysis with exception"""
        mock_sentiment.side_effect = Exception("Sentiment analysis failed")
        
        request = SentimentAnalysisRequest(
            inputPrompt="Test text",
            modelName="gpt4"
        )
        
        with pytest.raises(Exception, match="Sentiment analysis failed"):
            await ExplainService.sentiment_analysis(request)
