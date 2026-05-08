import pytest
import json
from pydantic import ValidationError

from llm_explain.mappers.mappers import (
    Methods, ResponseTypes, EndPointRequest, SentimentAnalysisRequest,
    SentimentAnalysisResponse, UncertainityRequest, UncertainityResponse,
    TokenImportanceRequest, TokenImportanceResponse, GoTRequest, GoTResponse,
    SafeSearchRequest, SafeSearchResponse, rereadRequest, rereadResponse,
    openAIRequest, CoTResponse, CoVRequest, CoVResponse, FileUploadRequest,
    lotRequest, lotResponse
)


@pytest.mark.unit
class TestEnums:
    """Test enum classes"""
    
    def test_methods_enum_values(self):
        """Test Methods enum contains all expected values"""
        assert Methods.ALL == "All"
        assert Methods.TOKEN_IMPORTANCE == "Token-Importance"
        assert Methods.EVALUATION_METRICS == "Evalution-Metrics"
        assert Methods.THOT == "ThoT"
        assert Methods.REREAD_THOT == "ReRead-ThoT"
        assert Methods.GOT == "GoT"
        assert Methods.COT == "CoT"
        assert Methods.COV == "CoV"
        assert Methods.LOT == "LoT"
        assert Methods.SAFE_SEARCH == "Safe-Search"
        assert Methods.SENTIMENT_ANALYSIS == "Sentiment-Analysis"
    
    def test_response_types_enum_values(self):
        """Test ResponseTypes enum contains expected values"""
        assert ResponseTypes.JSON == "json"
        assert ResponseTypes.EXCEL == "excel"
    
    def test_methods_enum_is_string(self):
        """Test Methods enum values are strings"""
        for method in Methods:
            assert isinstance(method.value, str)
    
    def test_response_types_enum_is_string(self):
        """Test ResponseTypes enum values are strings"""
        for resp_type in ResponseTypes:
            assert isinstance(resp_type.value, str)


@pytest.mark.unit
class TestEndPointRequest:
    """Test EndPointRequest model"""
    
    def test_endpoint_request_creation_with_all_fields(self):
        """Test creating EndPointRequest with all fields"""
        endpoint = EndPointRequest(
            modelEndpointUrl="http://localhost:8002/model/endpoint",
            endpointInputParam={"input_parameter": "inputs", "parameters": {}},
            endpointOutputParam="['output']['choices'][0]['text']"
        )
        assert endpoint.modelEndpointUrl == "http://localhost:8002/model/endpoint"
        assert endpoint.endpointInputParam == {"input_parameter": "inputs", "parameters": {}}
        assert endpoint.endpointOutputParam == "['output']['choices'][0]['text']"
    
    def test_endpoint_request_optional_fields(self):
        """Test EndPointRequest with optional fields"""
        endpoint = EndPointRequest(
            modelEndpointUrl=None,
            endpointInputParam=None,
            endpointOutputParam=None
        )
        assert endpoint.modelEndpointUrl is None
        assert endpoint.endpointInputParam is None
        assert endpoint.endpointOutputParam is None
    
    def test_endpoint_request_partial_fields(self):
        """Test EndPointRequest with some fields"""
        endpoint = EndPointRequest(
            modelEndpointUrl="http://test.com",
            endpointInputParam=None,
            endpointOutputParam=None
        )
        assert endpoint.modelEndpointUrl == "http://test.com"
        assert endpoint.endpointInputParam is None
    
    def test_endpoint_request_dict_conversion(self):
        """Test EndPointRequest to dict conversion"""
        endpoint = EndPointRequest(
            modelEndpointUrl="http://test.com",
            endpointInputParam={"key": "value"},
            endpointOutputParam=None
        )
        endpoint_dict = endpoint.model_dump()
        assert isinstance(endpoint_dict, dict)
        assert endpoint_dict["modelEndpointUrl"] == "http://test.com"


@pytest.mark.unit
class TestSentimentAnalysisRequest:
    """Test SentimentAnalysisRequest model"""
    
    def test_sentiment_request_creation(self):
        """Test creating SentimentAnalysisRequest"""
        request = SentimentAnalysisRequest(
            inputPrompt="This is a great product!",
            modelName="gpt4"
        )
        assert request.inputPrompt == "This is a great product!"
        assert request.modelName == "gpt4"
    
    def test_sentiment_request_without_model_name(self):
        """Test SentimentAnalysisRequest without modelName"""
        request = SentimentAnalysisRequest(
            inputPrompt="Test prompt",
            modelName=None
        )
        assert request.inputPrompt == "Test prompt"
        assert request.modelName is None
    
    def test_sentiment_request_validation_missing_prompt(self):
        """Test SentimentAnalysisRequest fails without inputPrompt"""
        with pytest.raises(ValidationError):
            SentimentAnalysisRequest()
    
    def test_sentiment_request_empty_prompt(self):
        """Test SentimentAnalysisRequest with empty prompt"""
        request = SentimentAnalysisRequest(inputPrompt="", modelName=None)
        assert request.inputPrompt == ""
        assert request.modelName is None


@pytest.mark.unit
class TestSentimentAnalysisResponse:
    """Test SentimentAnalysisResponse model"""
    
    def test_sentiment_response_creation(self):
        """Test creating SentimentAnalysisResponse"""
        response = SentimentAnalysisResponse(
            explanation=["positive", "score: 0.9"]
        )
        assert isinstance(response.explanation, list)
        assert len(response.explanation) == 2
    
    def test_sentiment_response_empty_list(self):
        """Test SentimentAnalysisResponse with empty list"""
        response = SentimentAnalysisResponse(explanation=[])
        assert response.explanation == []
    
    def test_sentiment_response_validation_missing_explanation(self):
        """Test SentimentAnalysisResponse fails without explanation"""
        with pytest.raises(ValidationError):
            SentimentAnalysisResponse()


@pytest.mark.unit
class TestUncertainityRequest:
    """Test UncertainityRequest model"""
    
    def test_uncertainty_request_creation(self):
        """Test creating UncertainityRequest with all fields"""
        request = UncertainityRequest(
            inputPrompt="What is AI?",
            response="AI is artificial intelligence",
            context="General knowledge",
            modelName="gpt4",
            endpointDetails=EndPointRequest(
                modelEndpointUrl="http://test.com",
                endpointInputParam=None,
                endpointOutputParam=None
            )
        )
        assert request.inputPrompt == "What is AI?"
        assert request.response == "AI is artificial intelligence"
        assert request.context == "General knowledge"
        assert request.modelName == "gpt4"
        assert request.endpointDetails.modelEndpointUrl == "http://test.com"
    
    def test_uncertainty_request_minimal_fields(self):
        """Test UncertainityRequest with minimal required fields"""
        request = UncertainityRequest(
            inputPrompt="Test",
            response="Response",
            context=None,
            modelName=None,
            endpointDetails=None
        )
        assert request.inputPrompt == "Test"
        assert request.response == "Response"
        assert request.context is None
        assert request.modelName is None
    
    def test_uncertainty_request_validation_missing_fields(self):
        """Test UncertainityRequest fails without required fields"""
        with pytest.raises(ValidationError):
            UncertainityRequest(inputPrompt="Test")


@pytest.mark.unit
class TestUncertainityResponse:
    """Test UncertainityResponse model"""
    
    def test_uncertainty_response_creation(self):
        """Test creating UncertainityResponse"""
        response = UncertainityResponse(
            uncertainty={"score": 0.5, "explanation": "test"},
            coherence={"score": 0.8, "explanation": "test"},
            time_taken=1.5,
            token_cost=100
        )
        assert response.uncertainty["score"] == 0.5
        assert response.coherence["score"] == 0.8
        assert response.time_taken == 1.5
        assert response.token_cost == 100
    
    def test_uncertainty_response_without_token_cost(self):
        """Test UncertainityResponse without token_cost"""
        response = UncertainityResponse(
            uncertainty={"score": 0.5},
            coherence={"score": 0.8},
            time_taken=1.5
        )
        assert response.token_cost is None


@pytest.mark.unit
class TestTokenImportanceRequest:
    """Test TokenImportanceRequest model"""
    
    def test_token_importance_request_creation(self):
        """Test creating TokenImportanceRequest"""
        request = TokenImportanceRequest(
            inputPrompt="What is the capital of France?",
            modelName="GPT"
        )
        assert request.inputPrompt == "What is the capital of France?"
        assert request.modelName == "GPT"
    
    def test_token_importance_request_with_endpoint(self):
        """Test TokenImportanceRequest with endpoint details"""
        endpoint = EndPointRequest(
            modelEndpointUrl="http://test.com",
            endpointInputParam=None,
            endpointOutputParam=None
        )
        request = TokenImportanceRequest(
            inputPrompt="Test prompt",
            modelName=None,
            endpointDetails=endpoint
        )
        assert request.endpointDetails.modelEndpointUrl == "http://test.com"
    
    def test_token_importance_request_validation(self):
        """Test TokenImportanceRequest validation"""
        with pytest.raises(ValidationError):
            TokenImportanceRequest()


@pytest.mark.unit
class TestTokenImportanceResponse:
    """Test TokenImportanceResponse model"""
    
    def test_token_importance_response_creation(self):
        """Test creating TokenImportanceResponse"""
        response = TokenImportanceResponse(
            token_importance_mapping=[
                {"word": "capital", "importance": 0.8},
                {"word": "France", "importance": 0.7}
            ],
            time_taken=1.5,
            token_cost=100
        )
        assert len(response.token_importance_mapping) == 2
        assert response.time_taken == 1.5
        assert response.token_cost == 100
    
    def test_token_importance_response_empty_mapping(self):
        """Test TokenImportanceResponse with empty mapping"""
        response = TokenImportanceResponse(
            token_importance_mapping=[],
            time_taken=0.5
        )
        assert response.token_importance_mapping == []


@pytest.mark.unit
class TestGoTRequest:
    """Test GoTRequest model"""
    
    def test_got_request_creation(self):
        """Test creating GoTRequest"""
        request = GoTRequest(
            inputPrompt="Solve this problem",
            modelName="gpt4"
        )
        assert request.inputPrompt == "Solve this problem"
        assert request.modelName == "gpt4"
    
    def test_got_request_validation(self):
        """Test GoTRequest validation"""
        with pytest.raises(ValidationError):
            GoTRequest()


@pytest.mark.unit
class TestGoTResponse:
    """Test GoTResponse model"""
    
    def test_got_response_creation(self):
        """Test creating GoTResponse"""
        response = GoTResponse(
            final_thought="The answer is 42",
            score=9.5,
            token_cost=150.0,
            consistency_level="High Consistent",
            time_taken=2.5
        )
        assert response.final_thought == "The answer is 42"
        assert response.score == 9.5
        assert response.token_cost == 150.0
        assert response.consistency_level == "High Consistent"
        assert response.time_taken == 2.5
    
    def test_got_response_validation(self):
        """Test GoTResponse validation for required fields"""
        with pytest.raises(ValidationError):
            GoTResponse(final_thought="test")


@pytest.mark.unit
class TestSafeSearchRequest:
    """Test SafeSearchRequest model"""
    
    def test_safe_search_request_creation(self):
        """Test creating SafeSearchRequest"""
        request = SafeSearchRequest(
            inputPrompt="Test query",
            llm_response="Test response",
            modelName="gpt4"
        )
        assert request.inputPrompt == "Test query"
        assert request.llm_response == "Test response"
        assert request.modelName == "gpt4"
    
    def test_safe_search_request_validation(self):
        """Test SafeSearchRequest validation"""
        with pytest.raises(ValidationError):
            SafeSearchRequest(inputPrompt="Test")


@pytest.mark.unit
class TestSafeSearchResponse:
    """Test SafeSearchResponse model"""
    
    def test_safe_search_response_creation(self):
        """Test creating SafeSearchResponse"""
        response = SafeSearchResponse(
            internetResponse=["result1", "result2"],
            metrics=[{"precision": 0.9}],
            time_taken=1.5,
            token_cost=100
        )
        assert len(response.internetResponse) == 2
        assert len(response.metrics) == 1
        assert response.time_taken == 1.5


@pytest.mark.unit
class TestRereadRequest:
    """Test rereadRequest model"""
    
    def test_reread_request_creation(self):
        """Test creating rereadRequest"""
        request = rereadRequest(
            inputPrompt="Test prompt",
            modelName="GPT4"
        )
        assert request.inputPrompt == "Test prompt"
        assert request.modelName == "GPT4"
    
    def test_reread_request_with_endpoint(self):
        """Test rereadRequest with endpoint details"""
        endpoint = EndPointRequest(
            modelEndpointUrl="http://test.com",
            endpointInputParam=None,
            endpointOutputParam=None
        )
        request = rereadRequest(
            inputPrompt="Test",
            modelName=None,
            endpointDetails=endpoint
        )
        assert request.endpointDetails.modelEndpointUrl == "http://test.com"


@pytest.mark.unit
class TestRereadResponse:
    """Test rereadResponse model"""
    
    def test_reread_response_creation(self):
        """Test creating rereadResponse"""
        response = rereadResponse(
            response={"answer": "test answer"},
            time_taken=2.0,
            token_cost=150
        )
        assert response.response == {"answer": "test answer"}
        assert response.time_taken == 2.0
        assert response.token_cost == 150


@pytest.mark.unit
class TestOpenAIRequest:
    """Test openAIRequest model"""
    
    def test_openai_request_creation(self):
        """Test creating openAIRequest"""
        request = openAIRequest(
            inputPrompt="What is AI?",
            temperature="0.7",
            modelName="GPT4"
        )
        assert request.inputPrompt == "What is AI?"
        assert request.temperature == "0.7"
        assert request.modelName == "GPT4"
    
    def test_openai_request_minimal(self):
        """Test openAIRequest with minimal fields"""
        request = openAIRequest(
            inputPrompt="Test",
            temperature=None,
            modelName=None,
            endpointDetails=None
        )
        assert request.inputPrompt == "Test"
        assert request.temperature is None


@pytest.mark.unit
class TestCoTResponse:
    """Test CoTResponse model"""
    
    def test_cot_response_creation(self):
        """Test creating CoTResponse"""
        response = CoTResponse(
            explanation="Step by step solution",
            time_taken=2.5,
            token_cost=200
        )
        assert response.explanation == "Step by step solution"
        assert response.time_taken == 2.5
        assert response.token_cost == 200


@pytest.mark.unit
class TestCoVRequest:
    """Test CoVRequest model"""
    
    def test_cov_request_creation(self):
        """Test creating CoVRequest"""
        request = CoVRequest(
            inputPrompt="Test question",
            complexity="medium",
            modelName="gpt4",
            translate="no"
        )
        assert request.inputPrompt == "Test question"
        assert request.complexity == "medium"
        assert request.modelName == "gpt4"
        assert request.translate == "no"
    
    def test_cov_request_validation(self):
        """Test CoVRequest validation for required fields"""
        with pytest.raises(ValidationError):
            CoVRequest(inputPrompt="Test")


@pytest.mark.unit
class TestCoVResponse:
    """Test CoVResponse model"""
    
    def test_cov_response_creation(self):
        """Test creating CoVResponse"""
        response = CoVResponse(
            original_question="What is 2+2?",
            baseline_response="4",
            verification_questions="Is 2+2 equal to 4?",
            verification_answers="Yes",
            final_answer="4",
            time_taken=2.0,
            token_cost=150
        )
        assert response.original_question == "What is 2+2?"
        assert response.baseline_response == "4"
        assert response.final_answer == "4"
        assert response.time_taken == 2.0


@pytest.mark.unit
class TestFileUploadRequest:
    """Test FileUploadRequest model"""
    
    def test_file_upload_request_creation(self):
        """Test creating FileUploadRequest"""
        request = FileUploadRequest(
            methods=[Methods.TOKEN_IMPORTANCE, Methods.GOT],
            responseFileType=ResponseTypes.JSON,
            userId="user123"
        )
        assert len(request.methods) == 2
        assert request.responseFileType == ResponseTypes.JSON
        assert request.userId == "user123"
    
    def test_file_upload_request_json_validation(self):
        """Test FileUploadRequest JSON string validation"""
        json_str = '{"methods": ["Token-Importance"], "responseFileType": "json", "userId": "test"}'
        request = FileUploadRequest.model_validate_json(json_str)
        assert len(request.methods) == 1
        assert request.responseFileType == ResponseTypes.JSON
    
    def test_file_upload_request_default_user_id(self):
        """Test FileUploadRequest with default userId"""
        request = FileUploadRequest(
            methods=[Methods.GOT],
            responseFileType=ResponseTypes.EXCEL
        )
        assert request.userId == ""


@pytest.mark.unit
class TestLotRequest:
    """Test lotRequest model"""
    
    def test_lot_request_creation(self):
        """Test creating lotRequest"""
        request = lotRequest(
            inputPrompt="Test prompt",
            llmResponse="Test LLM response",
            modelName="GPT4"
        )
        assert request.inputPrompt == "Test prompt"
        assert request.llmResponse == "Test LLM response"
        assert request.modelName == "GPT4"
    
    def test_lot_request_optional_fields(self):
        """Test lotRequest with optional fields"""
        request = lotRequest(
            inputPrompt="Test",
            llmResponse=None,
            modelName=None,
            endpointDetails=None
        )
        assert request.inputPrompt == "Test"
        assert request.llmResponse is None
        assert request.modelName is None


@pytest.mark.unit
class TestLotResponse:
    """Test lotResponse model"""
    
    def test_lot_response_creation(self):
        """Test creating lotResponse"""
        response = lotResponse(
            response={"result": "test"},
            time_taken=1.5,
            token_cost=100
        )
        assert response.response == {"result": "test"}
        assert response.time_taken == 1.5
        assert response.token_cost == 100
    
    def test_lot_response_default_response(self):
        """Test lotResponse with default response dict"""
        response = lotResponse(time_taken=1.0)
        assert response.response == {}
        assert response.time_taken == 1.0
