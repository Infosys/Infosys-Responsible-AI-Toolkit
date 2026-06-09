import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock, mock_open, call
import json
import os
from typing import Dict, List


# Test GeneralPrompter class
@pytest.mark.unit
class TestGeneralPrompter:
    """Test GeneralPrompter class"""
    
    def test_prompter_initialization(self):
        """Test GeneralPrompter initialization"""
        from llm_explain.utility.got import GeneralPrompter
        
        prompter = GeneralPrompter("answer the question", "What is AI?")
        
        assert prompter.task == "answer the question"
        assert prompter.question == "What is AI?"
    
    def test_generate_prompt_io_method(self):
        """Test generate_prompt with io method"""
        from llm_explain.utility.got import GeneralPrompter
        
        prompter = GeneralPrompter("answer the question", "What is 2+2?")
        prompt = prompter.generate_prompt(1, "io", "")
        
        assert "You are a helpful AI assistant" in prompt
        assert "What is 2+2?" in prompt
        assert "Think step by step" in prompt
    
    def test_generate_prompt_cot_method(self):
        """Test generate_prompt with cot method"""
        from llm_explain.utility.got import GeneralPrompter
        
        prompter = GeneralPrompter("solve the problem", "Calculate 5*6")
        prompt = prompter.generate_prompt(1, "cot", "")
        
        assert "Think step by step" in prompt
        assert "Calculate 5*6" in prompt
    
    def test_generate_prompt_tot_method(self):
        """Test generate_prompt with tot method"""
        from llm_explain.utility.got import GeneralPrompter
        
        prompter = GeneralPrompter("answer", "Test question")
        prompt = prompter.generate_prompt(1, "tot", "")
        
        assert "Think step by step" in prompt
        assert "use previous reasoning steps" in prompt
    
    def test_generate_prompt_got_method(self):
        """Test generate_prompt with got method"""
        from llm_explain.utility.got import GeneralPrompter
        
        prompter = GeneralPrompter("answer", "Test question")
        prompt = prompter.generate_prompt(1, "got", "")
        
        assert "Think step by step" in prompt
        assert "focus on specific parts" in prompt
    
    def test_generate_prompt_invalid_method(self):
        """Test generate_prompt with invalid method raises assertion"""
        from llm_explain.utility.got import GeneralPrompter
        
        prompter = GeneralPrompter("answer", "Test")
        
        with pytest.raises(AssertionError, match="Not implemented yet"):
            prompter.generate_prompt(1, "invalid_method", "")
    
    def test_score_prompt_single_state(self):
        """Test score_prompt with single state"""
        from llm_explain.utility.got import GeneralPrompter
        
        prompter = GeneralPrompter("answer", "What is AI?")
        state_dicts = [{"current": "AI is artificial intelligence"}]
        
        prompt = prompter.score_prompt(state_dicts)
        
        assert "score the reasoning process" in prompt
        assert "AI is artificial intelligence" in prompt
    
    def test_score_prompt_multiple_states_raises_assertion(self):
        """Test score_prompt with multiple states raises assertion"""
        from llm_explain.utility.got import GeneralPrompter
        
        prompter = GeneralPrompter("answer", "Test")
        state_dicts = [{"current": "state1"}, {"current": "state2"}]
        
        with pytest.raises(AssertionError, match="Only one state is allowed"):
            prompter.score_prompt(state_dicts)
    
    def test_aggregation_prompt(self):
        """Test aggregation_prompt"""
        from llm_explain.utility.got import GeneralPrompter
        
        prompter = GeneralPrompter("answer", "What is 1+1?")
        state_dicts = [
            {"current": "The answer is 2"},
            {"current": "1+1 equals 2"}
        ]
        
        prompt = prompter.aggregation_prompt(state_dicts)
        
        assert "aggregate" in prompt.lower() or "combine" in prompt.lower()
    



# Test GeneralParser class
@pytest.mark.unit
class TestGeneralParser:
    """Test GeneralParser class"""
    
    def test_parser_initialization(self):
        """Test GeneralParser initialization"""
        from llm_explain.utility.got import GeneralParser
        
        parser = GeneralParser()
        assert parser is not None
    
    def test_parse_generate_answer_simple(self):
        """Test parse_generate_answer with simple response"""
        from llm_explain.utility.got import GeneralParser
        
        parser = GeneralParser()
        base_state = {"method": "got"}
        responses = ["Answer 1", "Answer 2"]
        
        results = list(parser.parse_generate_answer(base_state, responses))
        
        assert len(results) == 2
        assert all("current" in r for r in results)
    



# Test got function
class TestGotFunction:
    
    @pytest.mark.unit
    @patch('llm_explain.utility.got.operations.GraphOfOperations')
    @patch('llm_explain.utility.got.operations.Generate')
    @patch('llm_explain.utility.got.operations.Score')
    @patch('llm_explain.utility.got.operations.KeepBestN')
    @patch('llm_explain.utility.got.operations.Aggregate')
    def test_got_creates_graph(self, mock_aggregate, mock_keep, mock_score, mock_generate, mock_graph):
        """Test got() creates graph of operations"""
        from llm_explain.utility.got import got
        
        mock_graph_instance = Mock()
        mock_graph.return_value = mock_graph_instance
        
        result = got()
        
        assert mock_graph_instance.append_operation.called
    
    @pytest.mark.unit
    def test_got_exception_handling(self):
        """Test got() exception handling"""
        from llm_explain.utility.got import got
        
        with patch('llm_explain.utility.got.operations.GraphOfOperations', side_effect=Exception("Graph error")):
            with pytest.raises(Exception):
                got()


# Test run function
class TestRunFunction:
    
    @pytest.mark.unit
    @patch('llm_explain.utility.got.os.makedirs')
    @patch('llm_explain.utility.got.os.path.exists')
    @patch('llm_explain.utility.got.language_models.AzureOpenAI')
    @patch('llm_explain.utility.got.controller.Controller')
    def test_run_basic_execution(self, mock_controller, mock_llm, mock_exists, mock_makedirs):
        """Test run function basic execution"""
        from llm_explain.utility.got import run, got
        
        mock_exists.return_value = False
        mock_lm_instance = Mock()
        mock_lm_instance.cost = 0.5
        mock_llm.return_value = mock_lm_instance
        
        mock_executor = Mock()
        mock_controller.return_value = mock_executor
        mock_executor.format_graph.return_value = (
            [{"operation": "generate", "thoughts": []}],
            {"thought_1": "test"}
        )
        
        # Mock the method to return a graph
        methods = [got]
        
        result = run("answer question", "What is AI?", methods, 30.0, "gpt4")
        
        assert result is not None
        mock_makedirs.assert_called()
    

    
    @pytest.mark.unit
    @patch('llm_explain.utility.got.os.makedirs')
    @patch('llm_explain.utility.got.os.path.exists')
    @patch('llm_explain.utility.got.language_models.AzureOpenAI')
    @patch('llm_explain.utility.got.controller.Controller')
    def test_run_executor_exception(self, mock_controller, mock_llm, mock_exists, mock_makedirs):
        """Test run function with executor exception"""
        from llm_explain.utility.got import run, got
        
        mock_exists.return_value = True
        mock_lm_instance = Mock()
        mock_lm_instance.cost = 0.5
        mock_llm.return_value = mock_lm_instance
        
        mock_executor = Mock()
        mock_executor.run.side_effect = Exception("Execution error")
        mock_controller.return_value = mock_executor
        
        methods = [got]
        
        with pytest.raises(Exception, match="Execution error"):
            run("answer", "question", methods, 30.0, "gpt4")
    
    @pytest.mark.unit
    @patch('llm_explain.utility.got.os.makedirs')
    @patch('llm_explain.utility.got.os.path.exists')
    @patch('llm_explain.utility.got.language_models.AzureOpenAI')
    @patch('llm_explain.utility.got.controller.Controller')
    @patch('builtins.open', new_callable=mock_open)
    def test_run_output_graph_called(self, mock_file, mock_controller, mock_llm, mock_exists, mock_makedirs):
        """Test run function calls output_graph"""
        from llm_explain.utility.got import run, got
        
        mock_exists.return_value = True
        mock_lm_instance = Mock()
        mock_lm_instance.cost = 0.5
        mock_llm.return_value = mock_lm_instance
        
        mock_executor = Mock()
        mock_controller.return_value = mock_executor
        mock_executor.format_graph.return_value = (
            [{"operation": "generate"}],
            {"thought": "test"}
        )
        
        # Mock operations graph with thoughts
        mock_operations_graph = Mock()
        mock_operation = Mock()
        mock_thought = Mock()
        mock_thought.state = {"current": "test", "documents": "docs", "parts": "parts", "method": "got"}
        mock_operation.thoughts = [mock_thought]
        mock_operations_graph.operations = [mock_operation]
        
        methods = [lambda: mock_operations_graph]
        
        result = run("answer", "question", methods, 30.0, "gpt4")
        
        mock_executor.output_graph.assert_called()
        mock_executor.format_graph.assert_called()
    
    @pytest.mark.unit
    @patch('llm_explain.utility.got.os.makedirs')
    @patch('llm_explain.utility.got.os.path.exists')
    @patch('llm_explain.utility.got.language_models.AzureOpenAI')
    @patch('llm_explain.utility.got.controller.Controller')
    def test_run_cleans_thought_state(self, mock_controller, mock_llm, mock_exists, mock_makedirs):
        """Test run function cleans unused keys from thought state"""
        from llm_explain.utility.got import run
        
        mock_exists.return_value = True
        mock_lm_instance = Mock()
        mock_lm_instance.cost = 0.5
        mock_llm.return_value = mock_lm_instance
        
        mock_executor = Mock()
        mock_controller.return_value = mock_executor
        mock_executor.format_graph.return_value = ([], {})
        
        # Create mock thought with keys that should be deleted
        mock_thought = Mock()
        mock_thought.state = {
            "current": "test",
            "documents": "should be deleted",
            "parts": "should be deleted",
            "method": "should be deleted",
            "other": "should remain"
        }
        
        mock_operation = Mock()
        mock_operation.thoughts = [mock_thought]
        
        mock_operations_graph = Mock()
        mock_operations_graph.operations = [mock_operation]
        
        methods = [lambda: mock_operations_graph]
        
        result = run("answer", "question", methods, 30.0, "gpt4")
        
        # Check that keys were deleted
        assert "documents" not in mock_thought.state
        assert "parts" not in mock_thought.state
        assert "method" not in mock_thought.state
        assert "other" in mock_thought.state


# Edge cases
class TestGotEdgeCases:
    
    @pytest.mark.unit
    def test_general_prompter_empty_question(self):
        """Test GeneralPrompter with empty question"""
        from llm_explain.utility.got import GeneralPrompter
        
        prompter = GeneralPrompter("task", "")
        prompt = prompter.generate_prompt(1, "got", "")
        
        assert "task" in prompt
    
    @pytest.mark.unit
    def test_general_parser_empty_responses(self):
        """Test GeneralParser with empty responses"""
        from llm_explain.utility.got import GeneralParser
        
        parser = GeneralParser()
        results = list(parser.parse_generate_answer({}, []))
        
        assert len(results) == 0
    
    @pytest.mark.unit
    @patch('llm_explain.utility.got.os.makedirs')
    @patch('llm_explain.utility.got.os.path.exists')
    def test_run_creates_results_dir(self, mock_exists, mock_makedirs):
        """Test run creates results directory if it doesn't exist"""
        from llm_explain.utility.got import run, got
        
        mock_exists.return_value = False
        
        with patch('llm_explain.utility.got.language_models.AzureOpenAI'):
            with patch('llm_explain.utility.got.controller.Controller'):
                try:
                    run("answer", "question", [got], 30.0, "gpt4")
                except:
                    pass
        
        mock_makedirs.assert_called()
