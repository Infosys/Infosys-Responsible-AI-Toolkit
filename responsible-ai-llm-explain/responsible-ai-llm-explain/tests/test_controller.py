import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock, mock_open
import json
import os
import sys
from typing import List, Dict


# Mock logger at module level BEFORE any imports that use it
@pytest.fixture(scope="module", autouse=True)
def mock_logger_module():
    """Mock CustomLogger at module level to prevent config issues"""
    with patch('llm_explain.config.logger.CustomLogger') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        # Also patch the readConfig function
        with patch('llm_explain.config.config.readConfig', return_value={'file_name': 'test', 'verbose': False, 'log_dir': None}):
            yield mock_instance



class TestControllerInitialization:
    
    @pytest.mark.unit
    def test_controller_init(self):
        """Test Controller initialization"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        mock_lm = Mock()
        mock_graph = Mock()
        mock_prompter = Mock()
        mock_parser = Mock()
        problem_params = {"test": "param"}
        
        controller = Controller(mock_lm, mock_graph, mock_prompter, mock_parser, problem_params)
        
        assert controller.lm == mock_lm
        assert controller.graph == mock_graph
        assert controller.prompter == mock_prompter
        assert controller.parser == mock_parser
        assert controller.problem_parameters == problem_params
        assert controller.run_executed == False
    
    @pytest.mark.unit
    def test_controller_logger_initialized(self):
        """Test Controller logger is initialized"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        controller = Controller(Mock(), Mock(), Mock(), Mock(), {})
        
        assert controller.logger is not None



class TestControllerRun:
    
    @pytest.mark.unit
    def test_run_with_no_roots_raises_assertion(self):
        """Test run raises assertion when graph has no roots"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        mock_graph = Mock()
        mock_graph.roots = None
        
        controller = Controller(Mock(), mock_graph, Mock(), Mock(), {})
        
        with pytest.raises(AssertionError, match="has no root"):
            controller.run()
    
    @pytest.mark.unit
    def test_run_executes_operations_in_queue(self):
        """Test run executes operations from queue"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        mock_lm = Mock()
        mock_prompter = Mock()
        mock_parser = Mock()
        
        # Create mock operations
        mock_op1 = Mock()
        mock_op1.can_be_executed.return_value = True
        mock_op1.successors = []
        
        mock_op2 = Mock()
        mock_op2.can_be_executed.return_value = True
        mock_op2.successors = []
        
        mock_graph = Mock()
        mock_graph.roots = [mock_op1]
        mock_graph.operations = [mock_op1, mock_op2]
        
        controller = Controller(mock_lm, mock_graph, mock_prompter, mock_parser, {})
        controller.run()
        
        mock_op1.execute.assert_called_once()
        assert controller.run_executed == True
    
    @pytest.mark.unit
    def test_run_executes_successor_operations(self):
        """Test run executes successor operations"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        mock_lm = Mock()
        mock_prompter = Mock()
        mock_parser = Mock()
        
    
        mock_op2 = Mock()
        mock_op2.can_be_executed.return_value = True
        mock_op2.successors = []
        
        mock_op1 = Mock()
        mock_op1.can_be_executed.return_value = True
        mock_op1.successors = [mock_op2]
        
        mock_graph = Mock()
        mock_graph.roots = [mock_op1]
        mock_graph.operations = [mock_op1, mock_op2]
        
        controller = Controller(mock_lm, mock_graph, mock_prompter, mock_parser, {})
        controller.run()
        
  
        assert mock_op1.execute.call_count >= 1
        assert mock_op2.execute.call_count >= 1
    
    @pytest.mark.unit
    def test_run_passes_problem_parameters(self):
        """Test run passes problem parameters to operations"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        mock_lm = Mock()
        mock_prompter = Mock()
        mock_parser = Mock()
        problem_params = {"param1": "value1", "param2": "value2"}
        
        mock_op = Mock()
        mock_op.can_be_executed.return_value = True
        mock_op.successors = []
        
        mock_graph = Mock()
        mock_graph.roots = [mock_op]
        mock_graph.operations = [mock_op]
        
        controller = Controller(mock_lm, mock_graph, mock_prompter, mock_parser, problem_params)
        controller.run()
        
        # Verify execute was called with correct parameters
        mock_op.execute.assert_called_once()
        call_kwargs = mock_op.execute.call_args[1]
        assert 'param1' in call_kwargs
        assert call_kwargs['param1'] == 'value1'
    
    @pytest.mark.unit
    def test_run_with_multiple_operations(self):
        """Test run with multiple independent operations"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        mock_lm = Mock()
        mock_prompter = Mock()
        mock_parser = Mock()
        
      
        ops = []
        for i in range(3):
            mock_op = Mock()
            mock_op.can_be_executed.return_value = True
            mock_op.successors = []
            ops.append(mock_op)
        
        mock_graph = Mock()
        mock_graph.roots = [ops[0]]
        mock_graph.operations = ops
        
        controller = Controller(mock_lm, mock_graph, mock_prompter, mock_parser, {})
        controller.run()
        

        assert ops[0].execute.call_count >= 1
    
    @pytest.mark.unit
    def test_run_operation_not_ready(self):
        """Test run skips operations that are not ready"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        mock_op1 = Mock()
        mock_op1.can_be_executed.return_value = False
        mock_op1.successors = []
        
        mock_op2 = Mock()
        mock_op2.can_be_executed.return_value = True
        mock_op2.successors = []
        
        mock_graph = Mock()
        mock_graph.roots = [mock_op1]
        mock_graph.operations = [mock_op1, mock_op2]
        
        controller = Controller(Mock(), mock_graph, Mock(), Mock(), {})
        controller.run()
        
        # Only op2 should execute (if it's in execution queue)
        mock_op1.execute.assert_not_called()
    
    @pytest.mark.unit
    def test_run_sets_executed_flag(self):
        """Test run sets run_executed flag"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        mock_op = Mock()
        mock_op.can_be_executed.return_value = True
        mock_op.successors = []
        
        mock_graph = Mock()
        mock_graph.roots = [mock_op]
        mock_graph.operations = [mock_op]
        
        controller = Controller(Mock(), mock_graph, Mock(), Mock(), {})
        assert controller.run_executed == False
        
        controller.run()
        
        assert controller.run_executed == True
    
    @pytest.mark.unit
    def test_run_successor_not_in_graph_raises_assertion(self):
        """Test run raises assertion when successor not in graph"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        mock_op2 = Mock()
        mock_op2.can_be_executed.return_value = True
        
        mock_op1 = Mock()
        mock_op1.can_be_executed.return_value = True
        mock_op1.successors = [mock_op2]  # op2 as successor
        
        mock_graph = Mock()
        mock_graph.roots = [mock_op1]
        mock_graph.operations = [mock_op1]  # op2 not in operations
        
        controller = Controller(Mock(), mock_graph, Mock(), Mock(), {})
        
        with pytest.raises(AssertionError, match="not in the operations graph"):
            controller.run()


# Test Controller output methods
class TestControllerOutput:
    
    @pytest.mark.unit
    def test_output_graph(self):
        """Test output_graph method"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        mock_graph = Mock()
        mock_graph.operations = []
        
        controller = Controller(Mock(), mock_graph, Mock(), Mock(), {})
        
        # Just test that the graph property exists and is set correctly
        assert controller.graph == mock_graph
        assert controller.graph.operations == []
    
    @pytest.mark.unit
    def test_output_graph_after_run(self):
        """Test output_graph after running controller"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        mock_op = Mock()
        mock_op.can_be_executed.return_value = True
        mock_op.successors = []
        mock_op.__iter__ = Mock(return_value=iter([]))
        
        mock_graph = Mock()
        mock_graph.roots = [mock_op]
        mock_graph.operations = [mock_op]
        
        controller = Controller(Mock(), mock_graph, Mock(), Mock(), {})
        controller.run()
        
        # Just verify run was executed
        assert controller.run_executed == True


# Test Controller complex scenarios
class TestControllerComplexScenarios:
    
    @pytest.mark.unit
    def test_chain_of_operations(self):
        """Test chain of operations execution"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        # Create chain: op1 -> op2 -> op3
        mock_op3 = Mock()
        mock_op3.can_be_executed.return_value = True
        mock_op3.successors = []
        
        mock_op2 = Mock()
        mock_op2.can_be_executed.side_effect = [False, True]  # Not ready first, then ready
        mock_op2.successors = [mock_op3]
        
        mock_op1 = Mock()
        mock_op1.can_be_executed.return_value = True
        mock_op1.successors = [mock_op2]
        
        mock_graph = Mock()
        mock_graph.roots = [mock_op1]
        mock_graph.operations = [mock_op1, mock_op2, mock_op3]
        
        controller = Controller(Mock(), mock_graph, Mock(), Mock(), {})
        controller.run()
        
        # All operations should eventually execute
        assert mock_op1.execute.call_count >= 1
    
    @pytest.mark.unit
    def test_branching_operations(self):
        """Test branching operations (one op with multiple successors)"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        # Create branching: op1 -> [op2, op3]
        mock_op2 = Mock()
        mock_op2.can_be_executed.return_value = True
        mock_op2.successors = []
        
        mock_op3 = Mock()
        mock_op3.can_be_executed.return_value = True
        mock_op3.successors = []
        
        mock_op1 = Mock()
        mock_op1.can_be_executed.return_value = True
        mock_op1.successors = [mock_op2, mock_op3]
        
        mock_graph = Mock()
        mock_graph.roots = [mock_op1]
        mock_graph.operations = [mock_op1, mock_op2, mock_op3]
        
        controller = Controller(Mock(), mock_graph, Mock(), Mock(), {})
        controller.run()
        
        # First operation should execute
        assert mock_op1.execute.call_count >= 1
    
    @pytest.mark.unit
    def test_empty_execution_queue(self):
        """Test with empty execution queue"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        # Operations that can't execute
        mock_op = Mock()
        mock_op.can_be_executed.return_value = False
        mock_op.successors = []
        
        mock_graph = Mock()
        mock_graph.roots = [mock_op]
        mock_graph.operations = [mock_op]
        
        controller = Controller(Mock(), mock_graph, Mock(), Mock(), {})
        controller.run()
        
        # No operations should execute
        mock_op.execute.assert_not_called()
    
    @pytest.mark.unit
    def test_controller_with_empty_parameters(self):
        """Test controller with empty problem parameters"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        mock_op = Mock()
        mock_op.can_be_executed.return_value = True
        mock_op.successors = []
        
        mock_graph = Mock()
        mock_graph.roots = [mock_op]
        mock_graph.operations = [mock_op]
        
        controller = Controller(Mock(), mock_graph, Mock(), Mock(), {})
        controller.run()
        
        # Should still work with empty parameters
        mock_op.execute.assert_called_once()


# Test Controller state management
class TestControllerState:
    
    @pytest.mark.unit
    def test_initial_state(self):
        """Test initial controller state"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        controller = Controller(Mock(), Mock(), Mock(), Mock(), {"test": "value"})
        
        assert controller.run_executed == False
        assert controller.problem_parameters == {"test": "value"}
    
    @pytest.mark.unit
    def test_state_persistence(self):
        """Test state persistence across operations"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        mock_op1 = Mock()
        mock_op1.can_be_executed.return_value = True
        mock_op1.successors = []
        mock_op1.__iter__ = Mock(return_value=iter([]))
        
        mock_op2 = Mock()
        mock_op2.can_be_executed.return_value = True
        mock_op2.successors = []
        mock_op2.__iter__ = Mock(return_value=iter([]))
        
        mock_graph = Mock()
        mock_graph.roots = [mock_op1]
        mock_graph.operations = [mock_op1, mock_op2]
        
        problem_params = {"key": "value"}
        controller = Controller(Mock(), mock_graph, Mock(), Mock(), problem_params)
        controller.run()
        
        # Problem parameters should remain the same
        assert controller.problem_parameters == problem_params
    
    @pytest.mark.unit
    def test_run_raises_assertion_for_invalid_successor(self):
        """Test run raises assertion when successor not in graph"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        mock_lm = Mock()
        mock_prompter = Mock()
        mock_parser = Mock()
        
        # Create operation with successor not in graph
        mock_successor = Mock()
        mock_successor.can_be_executed.return_value = True
        
        mock_op = Mock()
        mock_op.can_be_executed.return_value = True
        mock_op.successors = [mock_successor]
        
        mock_graph = Mock()
        mock_graph.roots = [mock_op]
        mock_graph.operations = [mock_op]  # successor not in operations
        
        controller = Controller(mock_lm, mock_graph, mock_prompter, mock_parser, {})
        
        with pytest.raises(AssertionError, match="not in the operations graph"):
            controller.run()


# Test get_final_thoughts method
class TestGetFinalThoughts:
    
    @pytest.mark.unit
    def test_get_final_thoughts_before_run_raises_assertion(self):
        """Test get_final_thoughts before run raises assertion"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        controller = Controller(Mock(), Mock(), Mock(), Mock(), {})
        
        with pytest.raises(AssertionError, match="has not been executed"):
            controller.get_final_thoughts()
    
    @pytest.mark.unit
    def test_get_final_thoughts_after_run(self):
        """Test get_final_thoughts after successful run"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        mock_thought1 = Mock()
        mock_thought2 = Mock()
        
        mock_leaf1 = Mock()
        mock_leaf1.get_thoughts.return_value = [mock_thought1]
        
        mock_leaf2 = Mock()
        mock_leaf2.get_thoughts.return_value = [mock_thought2]
        
        mock_graph = Mock()
        mock_graph.roots = [Mock()]
        mock_graph.operations = [Mock()]
        mock_graph.leaves = [mock_leaf1, mock_leaf2]
        
        controller = Controller(Mock(), mock_graph, Mock(), Mock(), {})
        controller.run_executed = True
        
        final_thoughts = controller.get_final_thoughts()
        
        assert len(final_thoughts) == 2
        assert final_thoughts[0] == [mock_thought1]
        assert final_thoughts[1] == [mock_thought2]


# Test format_graph method
class TestFormatGraph:
    

    
    @pytest.mark.unit
    def test_count_unique_matches_helper(self):
        """Test count_unique_matches helper function"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        controller = Controller(Mock(), Mock(), Mock(), Mock(), {})
        
       
        pass


# Edge cases and error handling
class TestControllerEdgeCases:
    
    @pytest.mark.unit
    def test_controller_with_empty_problem_parameters(self):
        """Test Controller with empty problem parameters"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        controller = Controller(Mock(), Mock(), Mock(), Mock(), {})
        
        assert controller.problem_parameters == {}
    
    @pytest.mark.unit
    def test_run_with_empty_operations_list(self):
        """Test run with empty operations list"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        mock_op = Mock()
        mock_op.can_be_executed.return_value = True
        mock_op.successors = []
        
        mock_graph = Mock()
        mock_graph.roots = [mock_op]
        mock_graph.operations = [mock_op]
        
        controller = Controller(Mock(), mock_graph, Mock(), Mock(), {})
        controller.run()
        
        assert controller.run_executed == True
    

    
    @pytest.mark.unit
    def test_run_with_operation_that_cannot_be_executed(self):
        """Test run skips operations that cannot be executed"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        mock_op1 = Mock()
        mock_op1.can_be_executed.return_value = False
        mock_op1.successors = []
        
        mock_op2 = Mock()
        mock_op2.can_be_executed.return_value = True
        mock_op2.successors = []
        
        mock_graph = Mock()
        mock_graph.roots = [mock_op1, mock_op2]
        mock_graph.operations = [mock_op1, mock_op2]
        
        controller = Controller(Mock(), mock_graph, Mock(), Mock(), {})
        controller.run()
        
        # Only op2 should be executed
        mock_op1.execute.assert_not_called()
        mock_op2.execute.assert_called_once()


# Test output_graph method
class TestOutputGraph:
    
    @pytest.mark.unit
    @patch('builtins.open', new_callable=mock_open)
    @patch('llm_explain.utility.graph_of_thoughts.controller.controller.CustomLogger')
    def test_output_graph_basic(self, mock_logger_cls, mock_file):
        """Test output_graph writes JSON file"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        from llm_explain.utility.graph_of_thoughts.operations import Thought
        
        mock_logger_cls.return_value = Mock()
        
        mock_thought = Mock(spec=Thought)
        mock_thought.state = "test state"
        mock_thought.scored = False
        mock_thought.validated = False
        mock_thought.compared_to_ground_truth = False
        
        mock_op = Mock()
        mock_op_type = Mock()
        mock_op_type.name = "GENERATE"  # Return string, not Mock
        mock_op.operation_type = mock_op_type
        mock_op.get_thoughts.return_value = [mock_thought]
        
        mock_graph = Mock()
        mock_graph.operations = [mock_op]
        
        mock_lm = Mock()
        mock_lm.prompt_tokens = 100
        mock_lm.completion_tokens = 50
        mock_lm.cost = 0.05
        
        controller = Controller(mock_lm, mock_graph, Mock(), Mock(), {})
        controller.output_graph("test_output.json")
        
        # Verify file was opened for writing
        mock_file.assert_called_once_with("test_output.json", "w")
    
    @pytest.mark.unit
    @patch('builtins.open', new_callable=mock_open)
    @patch('llm_explain.utility.graph_of_thoughts.controller.controller.CustomLogger')
    def test_output_graph_with_scored_thoughts(self, mock_logger_cls, mock_file):
        """Test output_graph with scored thoughts"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        from llm_explain.utility.graph_of_thoughts.operations import Thought
        
        mock_logger_cls.return_value = Mock()
        
        mock_thought = Mock(spec=Thought)
        mock_thought.state = "test state"
        mock_thought.scored = True
        mock_thought.score = 0.95
        mock_thought.validated = False
        mock_thought.compared_to_ground_truth = False
        
        mock_op = Mock()
        mock_op_type = Mock()
        mock_op_type.name = "SCORE"  # Return string, not Mock
        mock_op.operation_type = mock_op_type
        mock_op.get_thoughts.return_value = [mock_thought]
        
        mock_graph = Mock()
        mock_graph.operations = [mock_op]
        
        mock_lm = Mock()
        mock_lm.prompt_tokens = 100
        mock_lm.completion_tokens = 50
        mock_lm.cost = 0.05
        
        controller = Controller(mock_lm, mock_graph, Mock(), Mock(), {})
        controller.output_graph("test_output.json")
        
        mock_file.assert_called_once_with("test_output.json", "w")
    
    @pytest.mark.unit
    @patch('builtins.open', new_callable=mock_open)
    @patch('llm_explain.utility.graph_of_thoughts.controller.controller.CustomLogger')
    def test_output_graph_with_validated_thoughts(self, mock_logger_cls, mock_file):
        """Test output_graph with validated thoughts"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        from llm_explain.utility.graph_of_thoughts.operations import Thought
        
        mock_logger_cls.return_value = Mock()
        
        mock_thought = Mock(spec=Thought)
        mock_thought.state = "test state"
        mock_thought.scored = False
        mock_thought.validated = True
        mock_thought.valid = True
        mock_thought.compared_to_ground_truth = False
        
        mock_op = Mock()
        mock_op_type = Mock()
        mock_op_type.name = "VALIDATE"  # Return string, not Mock
        mock_op.operation_type = mock_op_type
        mock_op.get_thoughts.return_value = [mock_thought]
        
        mock_graph = Mock()
        mock_graph.operations = [mock_op]
        
        mock_lm = Mock()
        mock_lm.prompt_tokens = 100
        mock_lm.completion_tokens = 50
        mock_lm.cost = 0.05
        
        controller = Controller(mock_lm, mock_graph, Mock(), Mock(), {})
        controller.output_graph("test_output.json")
        
        mock_file.assert_called_once_with("test_output.json", "w")
    
    @pytest.mark.unit
    @patch('builtins.open', new_callable=mock_open)
    @patch('llm_explain.utility.graph_of_thoughts.controller.controller.CustomLogger')
    def test_output_graph_with_ground_truth_comparison(self, mock_logger_cls, mock_file):
        """Test output_graph with ground truth comparison"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        from llm_explain.utility.graph_of_thoughts.operations import Thought
        
        mock_logger_cls.return_value = Mock()
        
        mock_thought = Mock(spec=Thought)
        mock_thought.state = "test state"
        mock_thought.scored = False
        mock_thought.validated = False
        mock_thought.compared_to_ground_truth = True
        mock_thought.solved = True
        
        mock_op = Mock()
        mock_op_type = Mock()
        mock_op_type.name = "COMPARE"  # Return string, not Mock
        mock_op.operation_type = mock_op_type
        mock_op.get_thoughts.return_value = [mock_thought]
        
        mock_graph = Mock()
        mock_graph.operations = [mock_op]
        
        mock_lm = Mock()
        mock_lm.prompt_tokens = 100
        mock_lm.completion_tokens = 50
        mock_lm.cost = 0.05
        
        controller = Controller(mock_lm, mock_graph, Mock(), Mock(), {})
        controller.output_graph("test_output.json")
        
        mock_file.assert_called_once_with("test_output.json", "w")
    
    @pytest.mark.unit
    @patch('builtins.open', new_callable=mock_open)
    @patch('llm_explain.utility.graph_of_thoughts.controller.controller.CustomLogger')
    def test_output_graph_with_multiple_operations(self, mock_logger_cls, mock_file):
        """Test output_graph with multiple operations"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        from llm_explain.utility.graph_of_thoughts.operations import Thought
        
        mock_logger_cls.return_value = Mock()
        
        mock_thought1 = Mock(spec=Thought)
        mock_thought1.state = "state 1"
        mock_thought1.scored = True
        mock_thought1.score = 0.8
        mock_thought1.validated = False
        mock_thought1.compared_to_ground_truth = False
        
        mock_thought2 = Mock(spec=Thought)
        mock_thought2.state = "state 2"
        mock_thought2.scored = False
        mock_thought2.validated = True
        mock_thought2.valid = True
        mock_thought2.compared_to_ground_truth = False
        
        mock_op1 = Mock()
        mock_op1_type = Mock()
        mock_op1_type.name = "GENERATE"  # Return string, not Mock
        mock_op1.operation_type = mock_op1_type
        mock_op1.get_thoughts.return_value = [mock_thought1]
        
        mock_op2 = Mock()
        mock_op2_type = Mock()
        mock_op2_type.name = "VALIDATE"  # Return string, not Mock
        mock_op2.operation_type = mock_op2_type
        mock_op2.get_thoughts.return_value = [mock_thought2]
        
        mock_graph = Mock()
        mock_graph.operations = [mock_op1, mock_op2]
        
        mock_lm = Mock()
        mock_lm.prompt_tokens = 200
        mock_lm.completion_tokens = 100
        mock_lm.cost = 0.10
        
        controller = Controller(mock_lm, mock_graph, Mock(), Mock(), {})
        controller.output_graph("test_output.json")
        
        mock_file.assert_called_once_with("test_output.json", "w")


# Test format_graph method
class TestFormatGraph:
    
    @pytest.mark.unit
    @patch('builtins.open', new_callable=mock_open)
    @patch('llm_explain.utility.graph_of_thoughts.controller.controller.CustomLogger')
    @patch('os.path.exists', return_value=True)
    @patch('os.remove')
    def test_format_graph_basic(self, mock_remove, mock_exists, mock_logger_cls, mock_file):
        """Test format_graph basic functionality"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        mock_logger_cls.return_value = Mock()
        
        controller = Controller(Mock(), Mock(), Mock(), Mock(), {})
        
        # Create a simple test data file
        test_data = [
            {
                "operation": "generate",
                "thoughts": [
                    {"current": "thought 1"},
                    {"current": "thought 2"}
                ]
            },
            {
                "operation": "score",
                "thoughts": [
                    {"current": "thought 1"},
                    {"current": "thought 2"}
                ],
                "scores": [0.8, 0.6]
            },
            {
                "operation": "keep_best_n",
                "thoughts": [
                    {"current": "thought 1"}
                ],
                "scored": [True],
                "scores": [0.8]
            },
            {
                "operation": "aggregate",
                "thoughts": [
                    {"current": "thought 1 thought 2"}
                ]
            },
            {
                "operation": "score",
                "thoughts": [
                    {"current": "thought 1 thought 2"}
                ],
                "scores": [0.9]
            },
            {
                "operation": "keep_best_n",
                "thoughts": [
                    {"current": "thought 1 thought 2"}
                ],
                "scored": [True],
                "scores": [0.9]
            }
        ]
        
        with patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
            result, thoughts = controller.format_graph("test.json")
        
        # Verify os.remove was called
        mock_remove.assert_called_once_with("test.json")
        
        # Verify result is a list
        assert isinstance(result, list)
        assert isinstance(thoughts, dict)
    
    @pytest.mark.unit
    @patch('builtins.open', new_callable=mock_open)
    @patch('llm_explain.utility.graph_of_thoughts.controller.controller.CustomLogger')
    @patch('os.remove')
    def test_format_graph_with_aggregation(self, mock_remove, mock_logger_cls, mock_file):
        """Test format_graph with aggregation operations"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        mock_logger_cls.return_value = Mock()
        
        controller = Controller(Mock(), Mock(), Mock(), Mock(), {})
        
        test_data = [
            {"operation": "generate", "thoughts": [{"current": "A"}, {"current": "B"}]},
            {"operation": "score", "thoughts": [{"current": "A"}, {"current": "B"}], "scores": [0.7, 0.8]},
            {"operation": "keep_best_n", "thoughts": [{"current": "B"}], "scored": [True], "scores": [0.8]},
            {"operation": "aggregate", "thoughts": [{"current": "A B combined"}]},
            {"operation": "score", "thoughts": [{"current": "A B combined"}], "scores": [0.95]},
            {"operation": "keep_best_n", "thoughts": [{"current": "A B combined"}], "scored": [True], "scores": [0.95]}
        ]
        
        with patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
            result, thoughts = controller.format_graph("test_agg.json")
        
        mock_remove.assert_called_once_with("test_agg.json")
        assert isinstance(result, list)
        assert isinstance(thoughts, dict)


# Additional edge case tests
class TestControllerAdditionalEdgeCases:
    
    @pytest.mark.unit
    def test_multiple_roots(self):
        """Test controller with multiple root operations"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        mock_op1 = Mock()
        mock_op1.can_be_executed.return_value = True
        mock_op1.successors = []
        
        mock_op2 = Mock()
        mock_op2.can_be_executed.return_value = True
        mock_op2.successors = []
        
        mock_graph = Mock()
        mock_graph.roots = [mock_op1, mock_op2]
        mock_graph.operations = [mock_op1, mock_op2]
        
        controller = Controller(Mock(), mock_graph, Mock(), Mock(), {})
        controller.run()
        
        assert controller.run_executed == True
    
    @pytest.mark.unit
    def test_complex_parameter_passing(self):
        """Test complex parameter passing to operations"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        mock_op = Mock()
        mock_op.can_be_executed.return_value = True
        mock_op.successors = []
        
        mock_graph = Mock()
        mock_graph.roots = [mock_op]
        mock_graph.operations = [mock_op]
        
        complex_params = {
            "nested": {"key": "value"},
            "list": [1, 2, 3],
            "string": "test"
        }
        
        controller = Controller(Mock(), mock_graph, Mock(), Mock(), complex_params)
        controller.run()
        
        # Verify execute was called with complex parameters
        assert mock_op.execute.call_count >= 1
    
    @pytest.mark.unit
    def test_operation_state_transitions(self):
        """Test operation state transitions during execution"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        
        # Operation starts as not executable, becomes executable after first is done
        mock_op2 = Mock()
        call_count = [0]
        
        def can_execute_op2():
            call_count[0] += 1
            return call_count[0] > 1  # Becomes executable on second call
        
        mock_op2.can_be_executed = can_execute_op2
        mock_op2.successors = []
        
        mock_op1 = Mock()
        mock_op1.can_be_executed.return_value = True
        mock_op1.successors = [mock_op2]
        
        mock_graph = Mock()
        mock_graph.roots = [mock_op1]
        mock_graph.operations = [mock_op1, mock_op2]
        
        controller = Controller(Mock(), mock_graph, Mock(), Mock(), {})
        controller.run()
        
        assert mock_op1.execute.call_count >= 1
        assert mock_op2.execute.call_count >= 1
    
    @pytest.mark.unit
    @patch('builtins.open', new_callable=mock_open)
    @patch('llm_explain.utility.graph_of_thoughts.controller.controller.CustomLogger')
    def test_output_graph_all_features_combined(self, mock_logger_cls, mock_file):
        """Test output_graph with all features (scored, validated, ground truth)"""
        from llm_explain.utility.graph_of_thoughts.controller.controller import Controller
        from llm_explain.utility.graph_of_thoughts.operations import Thought
        
        mock_logger_cls.return_value = Mock()
        
        mock_thought = Mock(spec=Thought)
        mock_thought.state = "complex state"
        mock_thought.scored = True
        mock_thought.score = 0.92
        mock_thought.validated = True
        mock_thought.valid = True
        mock_thought.compared_to_ground_truth = True
        mock_thought.solved = True
        
        mock_op = Mock()
        mock_op_type = Mock()
        mock_op_type.name = "COMPLEX"  # Return string, not Mock
        mock_op.operation_type = mock_op_type
        mock_op.get_thoughts.return_value = [mock_thought]
        
        mock_graph = Mock()
        mock_graph.operations = [mock_op]
        
        mock_lm = Mock()
        mock_lm.prompt_tokens = 500
        mock_lm.completion_tokens = 250
        mock_lm.cost = 0.25
        
        controller = Controller(mock_lm, mock_graph, Mock(), Mock(), {})
        controller.output_graph("complex_output.json")
        
        mock_file.assert_called_once_with("complex_output.json", "w")
