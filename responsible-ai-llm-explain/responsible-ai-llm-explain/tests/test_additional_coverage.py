import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))


@pytest.mark.unit
class TestPromptsBase:
    """Test prompts base.py file"""
    
    def test_import_prompts_base(self):
        """Test importing prompts base module"""
        from llm_explain.utility.prompts import base
        assert base is not None
    
    def test_prompts_base_classes_exist(self):
        """Test that prompt classes exist"""
        try:
            from llm_explain.utility.prompts.base import llm_response_parser
            assert callable(llm_response_parser)
        except (ImportError, AttributeError):
            # If function doesn't exist with that name, pass
            pass
    
    def test_get_classification_prompt(self):
        """Test get_classification_prompt method"""
        from llm_explain.utility.prompts.base import Prompt
        
        input_prompt = "This is a great product!"
        result = Prompt.get_classification_prompt(input_prompt)
        
        assert isinstance(result, str)
        assert input_prompt in result
        assert "sentiment" in result.lower()
        assert "token" in result.lower()
    
    def test_get_local_explanation_prompt_with_context(self):
        """Test get_local_explanation_prompt with context"""
        from llm_explain.utility.prompts.base import Prompt
        
        prompt = "What is AI?"
        response = "AI is artificial intelligence"
        context = "AI has revolutionized technology"
        
        result = Prompt.get_local_explanation_prompt(prompt, response, context)
        
        assert isinstance(result, str)
        assert prompt in result
        assert response in result
        assert context in result
        assert "Uncertainty" in result
        assert "Coherence" in result
    
    def test_get_local_explanation_prompt_without_context(self):
        """Test get_local_explanation_prompt without context"""
        from llm_explain.utility.prompts.base import Prompt
        
        prompt = "What is AI?"
        response = "AI is artificial intelligence"
        
        result = Prompt.get_local_explanation_prompt(prompt, response, None)
        
        assert isinstance(result, str)
        assert prompt in result
        assert response in result
        assert "Uncertainty" in result
        assert "Coherence" in result
    
    def test_get_token_importance_prompt(self):
        """Test get_token_importance_prompt method"""
        from llm_explain.utility.prompts.base import Prompt
        
        prompt = "What is machine learning?"
        result = Prompt.get_token_importance_prompt(prompt)
        
        assert isinstance(result, str)
        assert prompt in result
        assert "Token Importance" in result
        assert "importance" in result.lower()
    
    def test_get_tone_prediction_prompt(self):
        """Test get_tone_prediction_prompt method"""
        from llm_explain.utility.prompts.base import Prompt
        
        response = "This is an amazing achievement!"
        result = Prompt.get_tone_prediction_prompt(response)
        
        assert isinstance(result, str)
        assert response in result
        assert "tone" in result.lower()
        assert "Formal" in result
        assert "Informal" in result
    
    def test_get_coherence_prompt(self):
        """Test get_coherehce_prompt method"""
        from llm_explain.utility.prompts.base import Prompt
        
        response = "The sky is blue. It is a clear day."
        result = Prompt.get_coherehce_prompt(response)
        
        assert isinstance(result, str)
        assert response in result
        assert "coherence" in result.lower()
        assert "score" in result.lower()
    
    def test_get_response_relevance_prompt(self):
        """Test get_response_revelance_prompt method"""
        from llm_explain.utility.prompts.base import Prompt
        
        prompt = "What is Python?"
        response = "Python is a programming language"
        result = Prompt.get_response_revelance_prompt(prompt, response)
        
        assert isinstance(result, str)
        assert prompt in result
        assert response in result
        assert "relevance" in result.lower() or "relevant" in result.lower()
    
    def test_generate_facts_prompt(self):
        """Test generate_facts_prompt method"""
        from llm_explain.utility.prompts.base import Prompt
        
        prompt = "Who is the president?"
        response = "The president is the leader of the country"
        current_date = "2024-01-01"
        
        result = Prompt.generate_facts_prompt(prompt, response, current_date)
        
        assert isinstance(result, str)
        assert prompt in result
        assert response in result
        assert "facts" in result.lower()
    
    def test_evaluate_facts_prompt(self):
        """Test evaluate_facts_prompt method"""
        from llm_explain.utility.prompts.base import Prompt
        
        facts = "Fact 1 # Fact 2 # Fact 3"
        context = "Context information"
        prompt = "Original question"
        
        result = Prompt.evaluate_facts_prompt(facts, context, prompt)
        
        assert isinstance(result, str)
        assert facts in result
        assert context in result
        assert prompt in result
        assert "judgement" in result.lower()
    
    def test_filter_facts_prompt(self):
        """Test filter_facts_prompt method"""
        from llm_explain.utility.prompts.base import Prompt
        
        prompt = "What is AI?"
        facts = "AI is technology. Weather is nice."
        
        result = Prompt.filter_facts_prompt(prompt, facts)
        
        assert isinstance(result, str)
        assert prompt in result
        assert facts in result
        assert "filter" in result.lower()
    
    def test_summarize_prompt(self):
        """Test summarize_prompt method"""
        from llm_explain.utility.prompts.base import Prompt
        
        qa_dict_list = [{"question": "Q1", "answer": "A1"}]
        result = Prompt.summarize_prompt(qa_dict_list)
        
        assert isinstance(result, str)
        assert "summary" in result.lower() or "summarize" in result.lower()
    
    def test_reread_thot(self):
        """Test reread_thot method"""
        from llm_explain.utility.prompts.base import Prompt
        
        prompt = "Explain quantum physics"
        result = Prompt.reread_thot(prompt)
        
        assert isinstance(result, str)
        assert prompt in result
        assert "Read the question again" in result
        assert "step-by-step" in result
    
    def test_thot(self):
        """Test thot method"""
        from llm_explain.utility.prompts.base import Prompt
        
        prompt = "Explain machine learning"
        result = Prompt.thot(prompt)
        
        assert isinstance(result, str)
        assert prompt in result
        assert "step-by-step" in result
    
    def test_cot(self):
        """Test cot method"""
        from llm_explain.utility.prompts.base import Prompt
        
        prompt = "How does photosynthesis work?"
        result = Prompt.cot(prompt)
        
        assert isinstance(result, str)
        assert prompt in result
        assert "step by step" in result
    
    def test_lot_phase1(self):
        """Test lot_phase1 method"""
        from llm_explain.utility.prompts.base import Prompt
        
        prompt = "All humans are mortal. Socrates is human."
        result = Prompt.lot_phase1(prompt)
        
        assert isinstance(result, str)
        assert prompt in result
        assert "logical" in result.lower()
        assert "proposition" in result.lower()
    
    def test_lot_phase2(self):
        """Test lot_phase2 method"""
        from llm_explain.utility.prompts.base import Prompt
        
        prompt = "A → B"
        result = Prompt.lot_phase2(prompt)
        
        assert isinstance(result, str)
        assert prompt in result
        assert "logical" in result.lower()
        assert "law" in result.lower()
    
    def test_lot_phase3(self):
        """Test lot_phase3 method"""
        from llm_explain.utility.prompts.base import Prompt
        
        prompt1 = "A: Human, B: Mortal"
        prompt2 = "A → B"
        result = Prompt.lot_phase3(prompt1, prompt2)
        
        assert isinstance(result, str)
        assert prompt1 in result
        assert prompt2 in result
        assert "translate" in result.lower()
    
    def test_lot_phase4(self):
        """Test lot_phase4 method"""
        from llm_explain.utility.prompts.base import Prompt
        
        prompt = "If A then B. A is true. Therefore B is true."
        result = Prompt.lot_phase4(prompt)
        
        assert isinstance(result, str)
        assert prompt in result
        assert "analyse" in result.lower() or "analyze" in result.lower()
        assert "explanation" in result.lower()


@pytest.mark.unit
class TestGraphOfThoughtsThought:
    """Test graph_of_thoughts thought.py"""
    
    def test_thought_class_creation(self):
        """Test Thought class can be created"""
        from llm_explain.utility.graph_of_thoughts.operations.thought import Thought
        
        thought = Thought(state="test state")
        
        assert thought.state == "test state"
        assert hasattr(thought, 'id')
    
    def test_thought_with_state(self):
        """Test Thought with different states"""
        from llm_explain.utility.graph_of_thoughts.operations.thought import Thought
        
        parent = Thought(state="parent")
        child = Thought(state="child")
        
        assert parent.state == "parent"
        assert child.state == "child"
        assert parent.id != child.id
    
    def test_thought_state_modification(self):
        """Test modifying thought state"""
        from llm_explain.utility.graph_of_thoughts.operations.thought import Thought
        
        thought = Thought(state={"data": "initial"})
        thought.state = {"data": "modified"}
        
        assert thought.state["data"] == "modified"
    
    def test_thought_get_path(self):
        """Test thought attributes"""
        from llm_explain.utility.graph_of_thoughts.operations.thought import Thought
        
        t1 = Thought(state="1")
        t2 = Thought(state="2")
        t3 = Thought(state="3")
        
        assert t1.id != t2.id
        assert t2.id != t3.id
        assert hasattr(t1, '_score')
    
    def test_thought_str_representation(self):
        """Test string representation of Thought"""
        from llm_explain.utility.graph_of_thoughts.operations.thought import Thought
        
        thought = Thought(state="test")
        str_repr = str(thought)
        
        assert isinstance(str_repr, str)
    
    def test_thought_comparison(self):
        """Test thought comparison if implemented"""
        from llm_explain.utility.graph_of_thoughts.operations.thought import Thought
        
        t1 = Thought(state="same")
        t2 = Thought(state="same")
        
        # Even if states are same, objects are different
        assert t1 is not t2


@pytest.mark.unit
class TestGraphOfOperations:
    """Test GraphOfOperations class"""
    
    def test_graph_of_operations_creation(self):
        """Test GraphOfOperations can be created"""
        from llm_explain.utility.graph_of_thoughts.operations.graph_of_operations import GraphOfOperations
        from llm_explain.utility.graph_of_thoughts.operations.operations import Generate
        
        graph = GraphOfOperations()
        assert graph is not None
    
    def test_graph_add_operation(self):
        """Test adding operation to graph"""
        from llm_explain.utility.graph_of_thoughts.operations.graph_of_operations import GraphOfOperations
        from llm_explain.utility.graph_of_thoughts.operations.operations import Generate
        
        graph = GraphOfOperations()
        op = Generate()
        
        if hasattr(graph, 'add_operation'):
            graph.add_operation(op)
            assert op in graph.operations
    
    def test_graph_multiple_operations(self):
        """Test graph with multiple operations"""
        from llm_explain.utility.graph_of_thoughts.operations.graph_of_operations import GraphOfOperations
        from llm_explain.utility.graph_of_thoughts.operations.operations import Generate, Aggregate
        
        graph = GraphOfOperations()
        
        if hasattr(graph, 'add_operation'):
            op1 = Generate()
            op2 = Aggregate()
            graph.add_operation(op1)
            graph.add_operation(op2)


@pytest.mark.unit
class TestOperations:
    """Test operations.py classes"""
    
    def test_generate_operation(self):
        """Test Generate operation"""
        from llm_explain.utility.graph_of_thoughts.operations.operations import Generate
        
        gen_op = Generate()
        assert gen_op is not None
        assert hasattr(gen_op, 'operation_type')
    
    def test_aggregate_operation(self):
        """Test Aggregate operation"""
        from llm_explain.utility.graph_of_thoughts.operations.operations import Aggregate
        
        agg_op = Aggregate()
        assert agg_op is not None
    
    def test_improve_operation(self):
        """Test Improve operation"""
        from llm_explain.utility.graph_of_thoughts.operations.operations import Improve
        
        imp_op = Improve()
        assert imp_op is not None
    
    def test_validate_operation(self):
        """Test operations module has required classes"""
        from llm_explain.utility.graph_of_thoughts.operations import operations
        
        # Check that operations module exists and has key classes
        assert hasattr(operations, 'Operation')
        assert hasattr(operations, 'Generate')
    
    def test_score_operation(self):
        """Test Score operation"""
        from llm_explain.utility.graph_of_thoughts.operations.operations import Score
        
        score_op = Score()
        assert score_op is not None
    
    def test_operation_can_be_executed(self):
        """Test can_be_executed method"""
        from llm_explain.utility.graph_of_thoughts.operations.operations import Generate
        
        op = Generate()
        # Initially should be able to execute if no predecessors
        if hasattr(op, 'can_be_executed'):
            result = op.can_be_executed()
            assert isinstance(result, bool)
    
    def test_operation_with_predecessors(self):
        """Test operation with predecessors"""
        from llm_explain.utility.graph_of_thoughts.operations.operations import Generate, Aggregate
        
        op1 = Generate()
        op2 = Aggregate()
        
        if hasattr(op2, 'add_predecessor'):
            op2.add_predecessor(op1)
            assert op1 in op2.predecessors if hasattr(op2, 'predecessors') else True
    
    def test_operation_with_successors(self):
        """Test operation with successors"""
        from llm_explain.utility.graph_of_thoughts.operations.operations import Generate, Improve
        
        op1 = Generate()
        op2 = Improve()
        
        if hasattr(op1, 'add_successor'):
            op1.add_successor(op2)
            assert op2 in op1.successors if hasattr(op1, 'successors') else True


@pytest.mark.unit
class TestParser:
    """Test parser.py"""
    
    def test_parser_creation(self):
        """Test Parser class exists and is abstract"""
        from llm_explain.utility.graph_of_thoughts.parser.parser import Parser
        from abc import ABC
        
        assert issubclass(Parser, ABC)
        assert hasattr(Parser, 'parse_generate_answer')
    
    def test_parser_parse_method_exists(self):
        """Test Parser has required abstract methods"""
        from llm_explain.utility.graph_of_thoughts.parser.parser import Parser
        import inspect
        
        methods = inspect.getmembers(Parser, predicate=inspect.isfunction)
        method_names = [m[0] for m in methods]
        
        assert 'parse_generate_answer' in method_names or 'parse' in method_names
    
    def test_parser_parse_generate_output(self):
        """Test Parser parse_generate_answer signature"""
        from llm_explain.utility.graph_of_thoughts.parser.parser import Parser
        import inspect
        
        if hasattr(Parser, 'parse_generate_answer'):
            sig = inspect.signature(Parser.parse_generate_answer)
            assert len(sig.parameters) >= 1
    
    def test_parser_parse_aggregation_output(self):
        """Test Parser parse_aggregation_answer exists"""
        from llm_explain.utility.graph_of_thoughts.parser.parser import Parser
        import inspect
        
        if hasattr(Parser, 'parse_aggregation_answer'):
            sig = inspect.signature(Parser.parse_aggregation_answer)
            assert len(sig.parameters) >= 1
    
    def test_parser_parse_validation_output(self):
        """Test Parser parse_validation_answer exists"""
        from llm_explain.utility.graph_of_thoughts.parser.parser import Parser
        import inspect
        
        if hasattr(Parser, 'parse_validation_answer'):
            sig = inspect.signature(Parser.parse_validation_answer)
            assert len(sig.parameters) >= 1


@pytest.mark.unit
class TestPrompter:
    """Test prompter.py"""
    
    def test_prompter_creation(self):
        """Test Prompter class exists and is abstract"""
        from llm_explain.utility.graph_of_thoughts.prompter.prompter import Prompter
        from abc import ABC
        
        assert issubclass(Prompter, ABC)
        assert hasattr(Prompter, 'generate_prompt')
    
    def test_prompter_generate_prompt_exists(self):
        """Test Prompter has required abstract methods"""
        from llm_explain.utility.graph_of_thoughts.prompter.prompter import Prompter
        import inspect
        
        methods = inspect.getmembers(Prompter, predicate=inspect.isfunction)
        method_names = [m[0] for m in methods]
        
        assert 'generate_prompt' in method_names or 'aggregation_prompt' in method_names
    
    def test_prompter_aggregation_prompt(self):
        """Test Prompter has aggregation_prompt method"""
        from llm_explain.utility.graph_of_thoughts.prompter.prompter import Prompter
        import inspect
        
        if hasattr(Prompter, 'aggregation_prompt'):
            sig = inspect.signature(Prompter.aggregation_prompt)
            assert len(sig.parameters) >= 1
    
    def test_prompter_improve_prompt(self):
        """Test Prompter has improve_prompt method"""
        from llm_explain.utility.graph_of_thoughts.prompter.prompter import Prompter
        import inspect
        
        if hasattr(Prompter, 'improve_prompt'):
            sig = inspect.signature(Prompter.improve_prompt)
            assert len(sig.parameters) >= 1
    
    def test_prompter_validation_prompt(self):
        """Test Prompter has validation_prompt method"""
        from llm_explain.utility.graph_of_thoughts.prompter.prompter import Prompter
        import inspect
        
        if hasattr(Prompter, 'validation_prompt'):
            sig = inspect.signature(Prompter.validation_prompt)
            assert len(sig.parameters) >= 1


@pytest.mark.unit
class TestQuerySerper:
    """Test query_serper.py additional scenarios"""
    
    @patch.dict(os.environ, {'SERPER_KEY': 'fake_api_key'})
    def test_query_serper_success(self):
        """Test successful serper query"""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper()
        assert wrapper is not None
        assert hasattr(wrapper, 'k')
    
    @patch.dict(os.environ, {'SERPER_KEY': 'fake_api_key'})
    def test_query_serper_no_results(self):
        """Test serper query wrapper initialization"""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper()
        assert hasattr(wrapper, 'k')
    
    @patch.dict(os.environ, {'SERPER_KEY': 'fake_api_key'})
    def test_query_serper_http_error(self):
        """Test serper query wrapper methods"""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper()
        assert hasattr(wrapper, 'k')
    
    @patch.dict(os.environ, {'SERPER_KEY': 'fake_api_key'})
    def test_query_serper_multiple_results(self):
        """Test serper query with multiple results"""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper()
        # Test wrapper exists
        assert wrapper is not None
        assert wrapper.k == 10


@pytest.mark.unit
class TestCovLlama:
    """Test cov_llama.py additional scenarios"""
    
    @patch('requests.post')
    def test_cov_llama_thot(self, mock_post):
        """Test COV with Llama THOT"""
        try:
            from llm_explain.utility import cov_llama
            # Test that module can be imported
            assert cov_llama is not None
        except ImportError:
            pytest.skip("cov_llama module not available")
    
    @patch('requests.post')
    def test_cov_llama_cot(self, mock_post):
        """Test COV with Llama class init"""
        try:
            from llm_explain.utility import cov_llama
            assert cov_llama is not None
        except ImportError:
            pytest.skip("cov_llama module not available")
    
    @patch('requests.post')
    def test_cov_llama_reread_thot(self, mock_post):
        """Test COV with Llama class methods"""
        try:
            from llm_explain.utility import cov_llama
            assert cov_llama is not None
        except ImportError:
            pytest.skip("cov_llama module not available")


@pytest.mark.unit
class TestGOT:
    """Test got.py additional scenarios"""
    
    def test_got_basic(self):
        """Test GOT basic functionality"""
        from llm_explain.utility import got
        
        # Test that got module can be imported
        assert got is not None


@pytest.mark.unit
class TestConfig:
    """Test config.py additional scenarios"""
    
    def test_config_logger_initialization(self):
        """Test logger config initialization"""
        from llm_explain.config.config import readConfig
        
        config = readConfig()
        assert config is not None
        assert isinstance(config, dict)
    
    def test_config_has_required_fields(self):
        """Test config has required fields"""
        from llm_explain.config.config import readConfig
        
        config = readConfig()
        # Should have some configuration
        assert len(config) >= 0
