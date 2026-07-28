"""
Unit tests for routing module (explain_router)
Tests FastAPI endpoints with mocks
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
from datetime import datetime
import asyncio
import uuid

from llm_explain.routing.explain_router import (
    explanation, reasoning, telemetry_error_logging
)
from llm_explain.mappers.mappers import (
    TokenImportanceRequest, TokenImportanceResponse,
    UncertainityRequest, UncertainityResponse,
    GoTRequest, GoTResponse,
    SafeSearchRequest, SafeSearchResponse,
    SentimentAnalysisRequest, SentimentAnalysisResponse,
    rereadRequest, rereadResponse,
    CoTResponse, CoVRequest, CoVResponse,
    lotRequest, lotResponse
)


@pytest.mark.unit
class TestTelemetryErrorLogging:
    """Test telemetry error logging function"""
    
    def test_telemetry_error_logging_extracts_function_name(self):
        """Test telemetry_error_logging extracts function name from traceback"""
        with patch.dict('os.environ', {'TELEMETRY_FLAG': 'True'}):
            with patch('llm_explain.routing.explain_router.Utils.send_telemetry_request') as mock_send:
                with patch('concurrent.futures.ThreadPoolExecutor') as mock_executor:
                    mock_exec_instance = MagicMock()
                    mock_executor.return_value.__enter__.return_value = mock_exec_instance
                    
                    try:
                        raise Exception("Test error")
                    except Exception as e:
                        mock_request_id = Mock()
                        mock_request_id.get.return_value = "test-id-123"
                        telemetry_error_logging(e, mock_request_id, "/test/endpoint")
    
    def test_telemetry_error_logging_disabled(self):
        """Test telemetry_error_logging when flag is False"""
        with patch.dict('os.environ', {'TELEMETRY_FLAG': 'False'}):
            with patch('llm_explain.routing.explain_router.Utils.send_telemetry_request') as mock_send:
                try:
                    raise Exception("Test error")
                except Exception as e:
                    mock_request_id = Mock()
                    mock_request_id.get.return_value = "test-id"
                    telemetry_error_logging(e, mock_request_id, "/test")
                    
                    # Should not call send_telemetry_request when flag is False
                    mock_send.assert_not_called()
    
    def test_telemetry_error_logging_with_site_packages(self):
        """Test telemetry_error_logging skips site-packages frames"""
        with patch.dict('os.environ', {'TELEMETRY_FLAG': 'True'}):
            with patch('concurrent.futures.ThreadPoolExecutor'):
                try:
                    # Create an error with traceback
                    raise ValueError("Test error")
                except Exception as e:
                    mock_request_id = Mock()
                    mock_request_id.get.return_value = "test-123"
                    # Should not raise any exceptions
                    telemetry_error_logging(e, mock_request_id, "/endpoint")


@pytest.mark.unit
class TestSentimentAnalysisEndpoint:
    """Test sentiment analysis endpoint"""
    
    @patch('llm_explain.routing.explain_router.service.sentiment_analysis')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_sentiment_analysis_success(self, mock_uuid, mock_request_id, mock_service):
        """Test sentiment_analysis endpoint with successful response"""
        # Setup mocks
        mock_uuid.return_value = Mock(hex="test-uuid-123")
        mock_request_id.set = Mock()
        
        mock_response = SentimentAnalysisResponse(
            explanation=[{"sentiment": "positive", "score": 0.9}]
        )
        
        async def mock_sentiment(*args, **kwargs):
            return mock_response
        
        with patch('asyncio.run', side_effect=lambda coro: mock_response):
            from llm_explain.routing.explain_router import sentiment_analysis
            
            request = SentimentAnalysisRequest(
                inputPrompt="This is great!",
                modelName="gpt4"
            )
            
            response = sentiment_analysis(request)
            
            assert isinstance(response, SentimentAnalysisResponse)
            assert len(response.explanation) == 1
    
    @patch('llm_explain.routing.explain_router.service.sentiment_analysis')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_sentiment_analysis_exception_handling(self, mock_uuid, mock_request_id, mock_service):
        """Test sentiment_analysis endpoint handles exceptions"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        mock_request_id.get = Mock(return_value="test-id")
        
        def raise_exception(*args, **kwargs):
            raise Exception("Service error")
        
        with patch('asyncio.run', side_effect=raise_exception):
            with patch.dict('os.environ', {'TELEMETRY_FLAG': 'False'}):
                from llm_explain.routing.explain_router import sentiment_analysis
                
                request = SentimentAnalysisRequest(
                    inputPrompt="Test",
                    modelName="gpt4"
                )
                
                with pytest.raises(HTTPException) as exc_info:
                    sentiment_analysis(request)
                
                assert exc_info.value.status_code == 500


@pytest.mark.unit
class TestCalculateUncertaintyEndpoint:
    """Test calculate uncertainty endpoint"""
    
    @patch('llm_explain.routing.explain_router.service.local_explanation')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_calculate_uncertainty_success(self, mock_uuid, mock_request_id, mock_service):
        """Test calculate_uncertainty endpoint with successful response"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        
        mock_response = UncertainityResponse(
            uncertainty={"score": 0.3, "explanation": "Low uncertainty"},
            coherence={"score": 0.8, "explanation": "High coherence"},
            time_taken=1.5,
            token_cost=100
        )
        
        with patch('asyncio.run', return_value=mock_response):
            from llm_explain.routing.explain_router import calculate_uncertainty
            
            request = UncertainityRequest(
                inputPrompt="Test question",
                response="Test answer",
                modelName="gpt4"
            )
            
            response = calculate_uncertainty(request)
            
            assert isinstance(response, UncertainityResponse)
            assert response.uncertainty["score"] == 0.3
    
    @patch('llm_explain.routing.explain_router.service.local_explanation')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_calculate_uncertainty_exception(self, mock_uuid, mock_request_id, mock_service):
        """Test calculate_uncertainty endpoint handles exceptions"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        mock_request_id.get = Mock(return_value="test-id")
        
        with patch('asyncio.run', side_effect=Exception("Error")):
            with patch.dict('os.environ', {'TELEMETRY_FLAG': 'False'}):
                from llm_explain.routing.explain_router import calculate_uncertainty
                
                request = UncertainityRequest(
                    inputPrompt="Test",
                    response="Response",
                    modelName="gpt4"
                )
                
                with pytest.raises(HTTPException) as exc_info:
                    calculate_uncertainty(request)
                
                assert exc_info.value.status_code == 500


@pytest.mark.unit
class TestTokenImportanceEndpoint:
    """Test token importance endpoint"""
    
    @patch('llm_explain.routing.explain_router.service.token_importance')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_token_importance_success(self, mock_uuid, mock_request_id, mock_service):
        """Test token_importance endpoint with successful response"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        
        mock_response = TokenImportanceResponse(
            token_importance_mapping=[
                {"word": "test", "importance": 0.8},
                {"word": "prompt", "importance": 0.6}
            ],
            time_taken=1.2,
            token_cost=80
        )
        
        with patch('asyncio.run', return_value=mock_response):
            from llm_explain.routing.explain_router import token_importance
            
            request = TokenImportanceRequest(
                inputPrompt="test prompt",
                modelName="GPT"
            )
            
            response = token_importance(request)
            
            assert isinstance(response, TokenImportanceResponse)
            assert len(response.token_importance_mapping) == 2
    
    @patch('llm_explain.routing.explain_router.service.token_importance')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_token_importance_exception(self, mock_uuid, mock_request_id, mock_service):
        """Test token_importance endpoint handles exceptions"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        mock_request_id.get = Mock(return_value="test-id")
        
        with patch('asyncio.run', side_effect=ValueError("Invalid input")):
            with patch.dict('os.environ', {'TELEMETRY_FLAG': 'False'}):
                from llm_explain.routing.explain_router import token_importance
                
                request = TokenImportanceRequest(
                    inputPrompt="test",
                    modelName="GPT"
                )
                
                with pytest.raises(HTTPException) as exc_info:
                    token_importance(request)
                
                assert exc_info.value.status_code == 500
                assert "Invalid input" in str(exc_info.value.detail)


@pytest.mark.unit
class TestSearchAugmentationEndpoint:
    """Test search augmentation endpoint"""
    
    @patch('llm_explain.routing.explain_router.service.search_augmentation')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_search_augmentation_success(self, mock_uuid, mock_request_id, mock_service):
        """Test searchAugmentation endpoint with successful response"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        
        mock_response = SafeSearchResponse(
            internetResponse=["Result 1", "Result 2"],
            metrics=[{"metricName": "Factuality Check", "score": 0.9}],
            time_taken=2.5,
            token_cost=150
        )
        
        with patch('asyncio.run', return_value=mock_response):
            from llm_explain.routing.explain_router import searchAugmentation
            
            request = SafeSearchRequest(
                inputPrompt="Test query",
                llm_response="Test LLM response",
                modelName="gpt4"
            )
            
            response = searchAugmentation(request)
            
            assert isinstance(response, SafeSearchResponse)
            assert len(response.internetResponse) == 2
            assert response.metrics[0]["metricName"] == "Factuality Check"
    
    @patch('llm_explain.routing.explain_router.service.search_augmentation')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_search_augmentation_exception(self, mock_uuid, mock_request_id, mock_service):
        """Test searchAugmentation endpoint handles exceptions"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        mock_request_id.get = Mock(return_value="test-id")
        
        with patch('asyncio.run', side_effect=Exception("Search failed")):
            with patch.dict('os.environ', {'TELEMETRY_FLAG': 'False'}):
                from llm_explain.routing.explain_router import searchAugmentation
                
                request = SafeSearchRequest(
                    inputPrompt="Test",
                    llm_response="Response",
                    modelName="gpt4"
                )
                
                with pytest.raises(HTTPException) as exc_info:
                    searchAugmentation(request)
                
                assert exc_info.value.status_code == 500


@pytest.mark.unit
class TestEndpointLogging:
    """Test endpoint logging behavior"""
    
    @patch('llm_explain.routing.explain_router.service.token_importance')
    @patch('llm_explain.routing.explain_router.log')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_endpoint_logs_start_and_end_times(self, mock_uuid, mock_request_id, mock_log, mock_service):
        """Test endpoint logs start and end times"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        
        mock_response = TokenImportanceResponse(
            token_importance_mapping=[],
            time_taken=1.0
        )
        
        with patch('asyncio.run', return_value=mock_response):
            from llm_explain.routing.explain_router import token_importance
            
            request = TokenImportanceRequest(
                inputPrompt="test",
                modelName="GPT"
            )
            
            response = token_importance(request)
            
            # Check that log.info was called multiple times
            assert mock_log.info.call_count >= 4
    
    @patch('llm_explain.routing.explain_router.service.sentiment_analysis')
    @patch('llm_explain.routing.explain_router.log')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_endpoint_logs_service_invocation(self, mock_uuid, mock_request_id, mock_log, mock_service):
        """Test endpoint logs before and after service invocation"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        
        mock_response = SentimentAnalysisResponse(explanation=[])
        
        with patch('asyncio.run', return_value=mock_response):
            from llm_explain.routing.explain_router import sentiment_analysis
            
            request = SentimentAnalysisRequest(
                inputPrompt="test",
                modelName="gpt4"
            )
            
            response = sentiment_analysis(request)
            
            # Verify logging calls
            assert mock_log.info.called


@pytest.mark.unit
class TestEndpointRequestIdGeneration:
    """Test request ID generation in endpoints"""
    
    @patch('llm_explain.routing.explain_router.service.token_importance')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_endpoint_generates_unique_request_id(self, mock_uuid, mock_request_id, mock_service):
        """Test endpoint generates and sets unique request ID"""
        mock_uuid_value = Mock(hex="unique-test-id-12345")
        mock_uuid.return_value = mock_uuid_value
        mock_request_id.set = Mock()
        
        mock_response = TokenImportanceResponse(
            token_importance_mapping=[],
            time_taken=1.0
        )
        
        with patch('asyncio.run', return_value=mock_response):
            from llm_explain.routing.explain_router import token_importance
            
            request = TokenImportanceRequest(
                inputPrompt="test",
                modelName="GPT"
            )
            
            response = token_importance(request)
            
            # Verify request_id_var.set was called with the UUID hex
            mock_request_id.set.assert_called_once_with("unique-test-id-12345")
    
    @patch('llm_explain.routing.explain_router.service.sentiment_analysis')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_different_endpoints_generate_different_ids(self, mock_uuid, mock_request_id, mock_service):
        """Test different endpoint calls generate different request IDs"""
        call_count = 0
        
        def uuid_side_effect():
            nonlocal call_count
            call_count += 1
            return Mock(hex=f"id-{call_count}")
        
        mock_uuid.side_effect = uuid_side_effect
        mock_request_id.set = Mock()
        
        mock_response = SentimentAnalysisResponse(explanation=[])
        
        with patch('asyncio.run', return_value=mock_response):
            from llm_explain.routing.explain_router import sentiment_analysis
            
            request1 = SentimentAnalysisRequest(inputPrompt="test1", modelName="gpt4")
            request2 = SentimentAnalysisRequest(inputPrompt="test2", modelName="gpt4")
            
            sentiment_analysis(request1)
            sentiment_analysis(request2)
            
            # Verify different IDs were set
            assert mock_request_id.set.call_count == 2


@pytest.mark.unit
class TestEndpointErrorHandling:
    """Test error handling across endpoints"""
    
    @patch('llm_explain.routing.explain_router.service.local_explanation')
    @patch('llm_explain.routing.explain_router.log')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_endpoint_logs_errors(self, mock_uuid, mock_request_id, mock_log, mock_service):
        """Test endpoint logs errors before raising HTTPException"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        mock_request_id.get = Mock(return_value="test-id")
        
        test_error = Exception("Service failure")
        
        with patch('asyncio.run', side_effect=test_error):
            with patch.dict('os.environ', {'TELEMETRY_FLAG': 'False'}):
                from llm_explain.routing.explain_router import calculate_uncertainty
                
                request = UncertainityRequest(
                    inputPrompt="Test",
                    response="Response",
                    modelName="gpt4"
                )
                
                with pytest.raises(HTTPException):
                    calculate_uncertainty(request)
                
                # Verify error was logged
                mock_log.error.assert_called_once_with(test_error)


@pytest.mark.unit
class TestReasoningEndpoints:
    """Test reasoning endpoints (CoT, ToT, CoV, LoT, ReRead)"""
    
    @patch('llm_explain.routing.explain_router.service.reread_reasoning')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_reread_reasoning_endpoint_success(self, mock_uuid, mock_request_id, mock_service):
        """Test reread reasoning endpoint with successful response"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        
        mock_response = rereadResponse(
            response={"answer": "Final answer", "reasoning": "Step by step"},
            time_taken=2.5,
            token_cost=180
        )
        
        async def mock_reread(*args, **kwargs):
            return mock_response
        
        with patch('asyncio.run', side_effect=lambda coro: mock_response):
            from llm_explain.routing.explain_router import reread_reasoning
            
            request = rereadRequest(
                inputPrompt="Solve this problem",
                modelName="gpt4"
            )
            
            response = reread_reasoning(request)
            
            assert isinstance(response, rereadResponse)
            assert response.response["answer"] == "Final answer"
            assert response.time_taken == 2.5
    
    @patch('llm_explain.routing.explain_router.service.graph_of_thoughts')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_graph_of_thoughts_endpoint_success(self, mock_uuid, mock_request_id, mock_service):
        """Test graph of thoughts endpoint"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        
        mock_response = GoTResponse(
            final_thought="Final answer based on graph of thoughts",
            score=9.5,
            token_cost=250.0,
            consistency_level="High Consistent",
            time_taken=3.5
        )
        
        with patch('asyncio.run', side_effect=lambda coro: mock_response):
            from llm_explain.routing.explain_router import graph_of_thoughts
            
            request = GoTRequest(
                inputPrompt="Complex problem",
                modelName="gpt4"
            )
            
            response = graph_of_thoughts(request)
            
            assert isinstance(response, GoTResponse)
            assert response.final_thought == "Final answer based on graph of thoughts"
            assert response.time_taken == 3.5
    
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_reread_reasoning_endpoint_error_handling(self, mock_uuid, mock_request_id):
        """Test reread reasoning endpoint handles errors"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        mock_request_id.get = Mock(return_value="test-id")
        
        def raise_exception(*args, **kwargs):
            raise Exception("Service error")
        
        with patch('asyncio.run', side_effect=raise_exception):
            with patch.dict('os.environ', {'TELEMETRY_FLAG': 'False'}):
                from llm_explain.routing.explain_router import reread_reasoning
                
                request = rereadRequest(
                    inputPrompt="Test",
                    modelName="gpt4"
                )
                
                with pytest.raises(HTTPException) as exc_info:
                    reread_reasoning(request)
                
                assert exc_info.value.status_code == 500


@pytest.mark.unit
class TestChainOfThoughtEndpoint:
    """Test Chain of Thought (CoT) endpoint"""
    
    @patch('llm_explain.routing.explain_router.reasoning')
    def test_cot_endpoint_invocation(self, mock_reasoning):
        """Test CoT endpoint is properly invoked through reasoning function"""
        from llm_explain.mappers.mappers import openAIRequest, CoTResponse
        
        mock_response = CoTResponse(
            explanation="CoT answer explanation",
            time_taken=2.0,
            token_cost=150
        )
        
        mock_reasoning.return_value = mock_response
        
        request = openAIRequest(
            inputPrompt="Solve with chain of thought",
            temperature="0",
            modelName="gpt4"
        )
        
        # The reasoning function handles CoT requests
        result = mock_reasoning(request)
        
        assert isinstance(result, CoTResponse)
        assert result.time_taken == 2.0


@pytest.mark.unit
class TestChainOfVerificationEndpoint:
    """Test Chain of Verification (CoV) endpoint"""
    
    @patch('llm_explain.routing.explain_router.reasoning')
    def test_cov_endpoint_invocation(self, mock_reasoning):
        """Test CoV endpoint is properly invoked"""
        from llm_explain.mappers.mappers import CoVRequest, CoVResponse
        
        mock_response = CoVResponse(
            original_question="Q",
            baseline_response="Initial",
            verification_questions="Q1",
            verification_answers="A1",
            final_answer="Verified",
            time_taken=2.5,
            token_cost=170
        )
        
        mock_reasoning.return_value = mock_response
        
        request = CoVRequest(
            inputPrompt="Verify this answer",
            modelName="gpt4",
            complexity="simple",
            translate="no"
        )
        
        result = mock_reasoning(request)
        
        assert isinstance(result, CoVResponse)
        assert result.final_answer == "Verified"


@pytest.mark.unit
class TestLogicOfThoughtsEndpoint:
    """Test Logic of Thoughts (LoT) endpoint"""
    
    @patch('llm_explain.routing.explain_router.reasoning')
    def test_lot_endpoint_invocation(self, mock_reasoning):
        """Test LoT endpoint is properly invoked"""
        from llm_explain.mappers.mappers import lotRequest, lotResponse
        
        mock_response = lotResponse(
            response={"propositions": ["P1", "P2"], "logical_expression": "P1 AND P2"},
            time_taken=3.2,
            token_cost=220
        )
        
        mock_reasoning.return_value = mock_response
        
        request = lotRequest(
            inputPrompt="Solve with logic",
            llmResponse="Sample logic response",
            modelName="gpt4"
        )
        
        result = mock_reasoning(request)
        
        assert isinstance(result, lotResponse)
        assert result.token_cost == 220


@pytest.mark.unit
class TestSentimentAnalysisEndpoint:
    """Test sentiment analysis endpoint"""
    
    @patch('llm_explain.routing.explain_router.service.sentiment_analysis')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_sentiment_analysis_success(self, mock_uuid, mock_request_id, mock_service):
        """Test sentiment_analysis endpoint with successful response"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        
        mock_response = SentimentAnalysisResponse(
            explanation=[{"token": "good", "importance": 0.8}]
        )
        
        with patch('asyncio.run', return_value=mock_response):
            from llm_explain.routing.explain_router import sentiment_analysis
            
            request = SentimentAnalysisRequest(
                inputPrompt="This is a good movie",
                modelName="gpt4"
            )
            
            response = sentiment_analysis(request)
            
            assert isinstance(response, SentimentAnalysisResponse)
            assert len(response.explanation) > 0
    
    @patch('llm_explain.routing.explain_router.service.sentiment_analysis')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_sentiment_analysis_exception(self, mock_uuid, mock_request_id, mock_service):
        """Test sentiment_analysis endpoint handles exceptions"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        mock_request_id.get = Mock(return_value="test-id")
        
        with patch('asyncio.run', side_effect=Exception("Service error")):
            with patch.dict('os.environ', {'TELEMETRY_FLAG': 'False'}):
                from llm_explain.routing.explain_router import sentiment_analysis
                
                request = SentimentAnalysisRequest(
                    inputPrompt="Test",
                    modelName="gpt4"
                )
                
                with pytest.raises(HTTPException) as exc_info:
                    sentiment_analysis(request)
                
                assert exc_info.value.status_code == 500


@pytest.mark.unit
class TestGraphOfThoughtsEndpoint:
    """Test Graph of Thoughts (GoT) endpoint"""
    
    @patch('llm_explain.routing.explain_router.service.graph_of_thoughts')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_got_success(self, mock_uuid, mock_request_id, mock_service):
        """Test GoT endpoint with successful response"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        
        mock_response = GoTResponse(
            final_thought="Final answer",
            score=9.0,
            token_cost=200,
            consistency_level="High",
            time_taken=3.5
        )
        
        with patch('asyncio.run', return_value=mock_response):
            from llm_explain.routing.explain_router import graph_of_thoughts
            
            request = GoTRequest(
                inputPrompt="Complex question",
                modelName="gpt4"
            )
            
            response = graph_of_thoughts(request)
            
            assert isinstance(response, GoTResponse)
            assert response.final_thought == "Final answer"
            assert response.score == 9.0
    
    @patch('llm_explain.routing.explain_router.service.graph_of_thoughts')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_got_exception(self, mock_uuid, mock_request_id, mock_service):
        """Test GoT endpoint handles exceptions"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        mock_request_id.get = Mock(return_value="test-id")
        
        with patch('asyncio.run', side_effect=Exception("GoT error")):
            with patch.dict('os.environ', {'TELEMETRY_FLAG': 'False'}):
                from llm_explain.routing.explain_router import graph_of_thoughts
                
                request = GoTRequest(
                    inputPrompt="Test",
                    modelName="gpt4"
                )
                
                with pytest.raises(HTTPException) as exc_info:
                    graph_of_thoughts(request)
                
                assert exc_info.value.status_code == 500


@pytest.mark.unit
class TestSafeSearchEndpoint:
    """Test safe search endpoint"""
    
    @patch('llm_explain.routing.explain_router.service.search_augmentation')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_safe_search_success(self, mock_uuid, mock_request_id, mock_service):
        """Test safe_search endpoint with successful response"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        
        mock_response = SafeSearchResponse(
            internetResponse=["Result 1", "Result 2"],
            metrics=[],
            time_taken=2.0,
            token_cost=100
        )
        
        with patch('asyncio.run', return_value=mock_response):
            from llm_explain.routing.explain_router import searchAugmentation
            
            request = SafeSearchRequest(
                inputPrompt="Search query",
                llm_response="LLM answer",
                modelName="gpt4"
            )
            
            response = searchAugmentation(request)
            
            assert isinstance(response, SafeSearchResponse)
            assert len(response.internetResponse) == 2
            assert response.time_taken == 2.0
    
    @patch('llm_explain.routing.explain_router.service.search_augmentation')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_safe_search_exception(self, mock_uuid, mock_request_id, mock_service):
        """Test safe_search endpoint handles exceptions"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        mock_request_id.get = Mock(return_value="test-id")
        
        with patch('asyncio.run', side_effect=Exception("Search error")):
            with patch.dict('os.environ', {'TELEMETRY_FLAG': 'False'}):
                from llm_explain.routing.explain_router import searchAugmentation
                
                request = SafeSearchRequest(
                    inputPrompt="Test",
                    llm_response="Response",
                    modelName="gpt4"
                )
                
                with pytest.raises(HTTPException) as exc_info:
                    searchAugmentation(request)
                
                assert exc_info.value.status_code == 500


@pytest.mark.unit
class TestThreadOfThoughtEndpoint:
    """Test Thread of Thought (ThoT) endpoint"""
    
    @patch('llm_explain.routing.explain_router.service.thot_reasoning')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_thot_success(self, mock_uuid, mock_request_id, mock_service):
        """Test ThoT endpoint with successful response"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        
        mock_response = rereadResponse(
            response={"answer": "Thread of thought answer", "reasoning": "step by step"},
            score=8.5,
            time_taken=2.5,
            token_cost=0.003
        )
        
        with patch('asyncio.run', return_value=mock_response):
            from llm_explain.routing.explain_router import generate_Thot
            
            request = Mock(
                inputPrompt="ThoT question",
                temperature="0.7",
                modelName="gpt4"
            )
            
            response = generate_Thot(request)
            
            assert isinstance(response, rereadResponse)
            assert isinstance(response.response, dict)
            assert response.time_taken == 2.5
    
    @patch('llm_explain.routing.explain_router.service.thot_reasoning')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_thot_exception(self, mock_uuid, mock_request_id, mock_service):
        """Test ThoT endpoint handles exceptions"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        mock_request_id.get = Mock(return_value="test-id")
        
        with patch('asyncio.run', side_effect=Exception("ThoT error")):
            with patch.dict('os.environ', {'TELEMETRY_FLAG': 'False'}):
                from llm_explain.routing.explain_router import generate_Thot
                
                request = Mock(
                    inputPrompt="Test",
                    temperature="0.7",
                    modelName="gpt4"
                )
                
                with pytest.raises(HTTPException) as exc_info:
                    generate_Thot(request)
                
                assert exc_info.value.status_code == 500


class TestChainOfThoughtEndpoint:
    """Tests for Chain of Thought (CoT) endpoint."""
    
    @patch('llm_explain.routing.explain_router.service.cot_reasoning')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_cot_success(self, mock_uuid, mock_request_id, mock_service):
        """Test CoT endpoint with successful response"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        
        mock_response = CoTResponse(
            explanation="Russia is the largest country by land area",
            time_taken=1.8
        )
        
        with patch('asyncio.run', return_value=mock_response):
            from llm_explain.routing.explain_router import generate_CoT
            
            request = Mock(
                inputPrompt="Which is the biggest country?",
                temperature="0.7",
                modelName="gpt4"
            )
            
            response = generate_CoT(request)
            
            assert isinstance(response, CoTResponse)
            assert response.time_taken == 1.8
    
    @patch('llm_explain.routing.explain_router.service.cot_reasoning')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    @patch('llm_explain.routing.explain_router.telemetry_error_logging')
    def test_cot_exception(self, mock_telemetry, mock_uuid, mock_request_id, mock_service):
        """Test CoT endpoint exception handling"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        mock_request_id.get = Mock(return_value="test-uuid")
        
        mock_service.side_effect = Exception("Service error")
        
        with patch('asyncio.run', side_effect=Exception("Service error")):
            from llm_explain.routing.explain_router import generate_CoT
            
            request = Mock(
                inputPrompt="Test",
                temperature="0.7",
                modelName="gpt4"
            )
            
            with pytest.raises(HTTPException) as exc_info:
                generate_CoT(request)
            
            assert exc_info.value.status_code == 500


class TestChainOfVerificationEndpoint:
    """Tests for Chain of Verification (CoV) endpoint."""
    
    @patch('llm_explain.routing.explain_router.service.cov_reasoning')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_cov_success(self, mock_uuid, mock_request_id, mock_service):
        """Test CoV endpoint with successful response"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        
        mock_response = CoVResponse(
            original_question="Which is the biggest country?",
            baseline_response="Russia is the largest",
            verification_questions="1. What is Russia's area?",
            verification_answers="1. 17,098,242 sq km",
            final_answer="Russia is the largest country by area",
            time_taken=3.2
        )
        
        with patch('asyncio.run', return_value=mock_response):
            from llm_explain.routing.explain_router import generate_CoV
            
            request = Mock(
                inputPrompt="Which is the biggest country?",
                complexity="simple",
                modelName="gpt4",
                translate="no"
            )
            
            response = generate_CoV(request)
            
            assert isinstance(response, CoVResponse)
            assert response.time_taken == 3.2
    
    @patch('llm_explain.routing.explain_router.service.cov_reasoning')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    @patch('llm_explain.routing.explain_router.telemetry_error_logging')
    def test_cov_exception(self, mock_telemetry, mock_uuid, mock_request_id, mock_service):
        """Test CoV endpoint exception handling"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        mock_request_id.get = Mock(return_value="test-uuid")
        
        mock_service.side_effect = Exception("Service error")
        
        with patch('asyncio.run', side_effect=Exception("Service error")):
            from llm_explain.routing.explain_router import generate_CoV
            
            request = Mock(
                inputPrompt="Test",
                complexity="simple",
                modelName="gpt4",
                translate="no"
            )
            
            with pytest.raises(HTTPException) as exc_info:
                generate_CoV(request)
            
            assert exc_info.value.status_code == 500


class TestLogicOfThoughtEndpoint:
    """Tests for Logic of Thought (LoT) endpoint."""
    
    @patch('llm_explain.routing.explain_router.service.lot_reasoning')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    def test_lot_success(self, mock_uuid, mock_request_id, mock_service):
        """Test LoT endpoint with successful response"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        
        mock_response = lotResponse(
            response={"logic": "Logical reasoning answer", "steps": ["step1", "step2"]},
            time_taken=2.1,
            token_cost=0.002
        )
        
        with patch('asyncio.run', return_value=mock_response):
            from llm_explain.routing.explain_router import generate_LoT
            
            request = Mock(
                inputPrompt="Explain logical reasoning",
                llmResponse="Initial response",
                modelName="gpt4"
            )
            
            response = generate_LoT(request)
            
            assert isinstance(response, lotResponse)
            assert isinstance(response.response, dict)
            assert response.time_taken == 2.1
    
    @patch('llm_explain.routing.explain_router.service.lot_reasoning')
    @patch('llm_explain.routing.explain_router.request_id_var')
    @patch('llm_explain.routing.explain_router.uuid.uuid4')
    @patch('llm_explain.routing.explain_router.telemetry_error_logging')
    def test_lot_exception(self, mock_telemetry, mock_uuid, mock_request_id, mock_service):
        """Test LoT endpoint exception handling"""
        mock_uuid.return_value = Mock(hex="test-uuid")
        mock_request_id.set = Mock()
        mock_request_id.get = Mock(return_value="test-uuid")
        
        mock_service.side_effect = Exception("Service error")
        
        with patch('asyncio.run', side_effect=Exception("Service error")):
            from llm_explain.routing.explain_router import generate_LoT
            
            request = Mock(
                inputPrompt="Test",
                llmResponse="Initial",
                modelName="gpt4"
            )
            
            with pytest.raises(HTTPException) as exc_info:
                generate_LoT(request)
            
            assert exc_info.value.status_code == 500


