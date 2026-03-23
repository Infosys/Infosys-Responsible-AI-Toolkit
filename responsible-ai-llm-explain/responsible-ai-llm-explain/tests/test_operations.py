'''
Copyright 2024 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import pytest
from unittest.mock import Mock, MagicMock, patch
from llm_explain.utility.graph_of_thoughts.operations.operations import (
    Operation, OperationType, Score, ValidateAndImprove, Generate, 
    Improve, Aggregate, KeepBestN, KeepValid, GroundTruth, Selector
)
from llm_explain.utility.graph_of_thoughts.operations.thought import Thought


@pytest.mark.unit
class TestOperationType:
    """Test OperationType enum"""
    
    def test_operation_type_values(self):
        """Test all OperationType enum values"""
        assert OperationType.score.value == 0
        assert OperationType.validate_and_improve.value == 1
        assert OperationType.generate.value == 2
        assert OperationType.improve.value == 3
        assert OperationType.aggregate.value == 4
        assert OperationType.keep_best_n.value == 5
        assert OperationType.keep_valid.value == 6
        assert OperationType.ground_truth_evaluator.value == 7
        assert OperationType.selector.value == 8


@pytest.mark.unit
class TestOperationBase:
    """Test Operation base class"""
    
    def test_operation_initialization(self):
        """Test Operation initialization"""
        # Create concrete subclass for testing
        class TestOp(Operation):
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return []
        
        op = TestOp()
        assert op.id >= 0
        assert op.predecessors == []
        assert op.successors == []
        assert op.executed == False
    
    def test_can_be_executed_no_predecessors(self):
        """Test can_be_executed with no predecessors"""
        class TestOp(Operation):
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return []
        
        op = TestOp()
        assert op.can_be_executed() == True
    
    def test_can_be_executed_with_executed_predecessors(self):
        """Test can_be_executed with executed predecessors"""
        class TestOp(Operation):
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return []
        
        op1 = TestOp()
        op2 = TestOp()
        op1.executed = True
        op2.add_predecessor(op1)
        assert op2.can_be_executed() == True
    
    def test_can_be_executed_with_unexecuted_predecessors(self):
        """Test can_be_executed with unexecuted predecessors"""
        class TestOp(Operation):
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return []
        
        op1 = TestOp()
        op2 = TestOp()
        op1.executed = False
        op2.add_predecessor(op1)
        assert op2.can_be_executed() == False
    
    def test_add_predecessor(self):
        """Test add_predecessor method"""
        class TestOp(Operation):
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return []
        
        op1 = TestOp()
        op2 = TestOp()
        op2.add_predecessor(op1)
        assert op1 in op2.predecessors
        assert op2 in op1.successors
    
    def test_add_successor(self):
        """Test add_successor method"""
        class TestOp(Operation):
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return []
        
        op1 = TestOp()
        op2 = TestOp()
        op1.add_successor(op2)
        assert op2 in op1.successors
        assert op1 in op2.predecessors
    
    def test_get_previous_thoughts(self):
        """Test get_previous_thoughts method"""
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                self.thoughts = []
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        op1 = TestOp()
        op2 = TestOp()
        thought1 = Thought({'key': 'value1'})
        thought2 = Thought({'key': 'value2'})
        op1.thoughts = [thought1, thought2]
        op2.add_predecessor(op1)
        
        previous = op2.get_previous_thoughts()
        assert len(previous) == 2
        assert thought1 in previous
        assert thought2 in previous
    
    def test_execute_sets_executed_flag(self):
        """Test execute method sets executed flag"""
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                self.exec_called = False
            def _execute(self, lm, prompter, parser, **kwargs):
                self.exec_called = True
            def get_thoughts(self):
                return []
        
        op = TestOp()
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        op.execute(lm, prompter, parser)
        assert op.executed == True
        assert op.exec_called == True
    
    def test_execute_with_unexecuted_predecessor_raises(self):
        """Test execute raises when predecessor not executed"""
        class TestOp(Operation):
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return []
        
        op1 = TestOp()
        op2 = TestOp()
        op2.add_predecessor(op1)
        
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        with pytest.raises(AssertionError):
            op2.execute(lm, prompter, parser)


@pytest.mark.unit
class TestScoreOperation:
    """Test Score operation"""
    
    def test_score_initialization(self):
        """Test Score initialization"""
        score_op = Score()
        assert score_op.operation_type == OperationType.score
        assert score_op.num_samples == 1
        assert score_op.combined_scoring == False
        assert score_op.thoughts == []
    
    def test_score_initialization_with_params(self):
        """Test Score initialization with parameters"""
        def scoring_func(state):
            return 0.5
        
        score_op = Score(num_samples=3, combined_scoring=True, scoring_function=scoring_func)
        assert score_op.num_samples == 3
        assert score_op.combined_scoring == True
        assert score_op.scoring_function == scoring_func
    
    def test_score_get_thoughts(self):
        """Test Score get_thoughts method"""
        score_op = Score()
        thought = Thought({'key': 'value'})
        score_op.thoughts.append(thought)
        assert len(score_op.get_thoughts()) == 1
    
    def test_score_execute_with_no_predecessors_raises(self):
        """Test Score execute raises with no predecessors"""
        score_op = Score()
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        with pytest.raises(AssertionError):
            score_op._execute(lm, prompter, parser)
    
    def test_score_execute_individual_with_scoring_function(self):
        """Test Score execute with individual scoring function"""
        def scoring_func(state):
            return 0.8
        
        score_op = Score(scoring_function=scoring_func)
        
        # Create predecessor with thoughts
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                self.thoughts = [Thought({'key': 'value'})]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        score_op.add_predecessor(pred_op)
        
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        score_op._execute(lm, prompter, parser)
        assert len(score_op.thoughts) == 1
        assert score_op.thoughts[0].score == 0.8
    
    def test_score_execute_individual_with_lm(self):
        """Test Score execute with LM for individual scoring"""
        score_op = Score(num_samples=1)
        
        # Create predecessor with thoughts
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                self.thoughts = [Thought({'key': 'value'})]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        score_op.add_predecessor(pred_op)
        
        lm = Mock()
        lm.get_response_texts = Mock(return_value=['response'])
        lm.query = Mock(return_value='query_result')
        
        prompter = Mock()
        prompter.score_prompt = Mock(return_value='prompt')
        
        parser = Mock()
        parser.parse_score_answer = Mock(return_value=[0.7])
        
        score_op._execute(lm, prompter, parser)
        assert len(score_op.thoughts) == 1
        assert score_op.thoughts[0].score == 0.7
    
    def test_score_execute_combined_with_scoring_function(self):
        """Test Score execute with combined scoring function"""
        def scoring_func(states):
            return [0.5, 0.6]
        
        score_op = Score(combined_scoring=True, scoring_function=scoring_func)
        
        # Create predecessor with multiple thoughts
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                self.thoughts = [Thought({'key': 'val1'}), Thought({'key': 'val2'})]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        score_op.add_predecessor(pred_op)
        
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        score_op._execute(lm, prompter, parser)
        assert len(score_op.thoughts) == 2
        assert score_op.thoughts[0].score == 0.5
        assert score_op.thoughts[1].score == 0.6
    
    def test_score_execute_combined_with_lm(self):
        """Test Score execute with LM for combined scoring"""
        score_op = Score(combined_scoring=True, num_samples=1)
        
        # Create predecessor with multiple thoughts
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                self.thoughts = [Thought({'key': 'val1'}), Thought({'key': 'val2'})]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        score_op.add_predecessor(pred_op)
        
        lm = Mock()
        lm.get_response_texts = Mock(return_value=['response'])
        lm.query = Mock(return_value='query_result')
        
        prompter = Mock()
        prompter.score_prompt = Mock(return_value='prompt')
        
        parser = Mock()
        parser.parse_score_answer = Mock(return_value=[0.3, 0.4])
        
        score_op._execute(lm, prompter, parser)
        assert len(score_op.thoughts) == 2
        assert score_op.thoughts[0].score == 0.3
        assert score_op.thoughts[1].score == 0.4


@pytest.mark.unit
class TestValidateAndImproveOperation:
    """Test ValidateAndImprove operation"""
    
    def test_validate_and_improve_initialization(self):
        """Test ValidateAndImprove initialization"""
        op = ValidateAndImprove()
        assert op.operation_type == OperationType.validate_and_improve
        assert op.num_samples == 1
        assert op.improve == True
        assert op.num_tries == 3
        assert op.thoughts == []
    
    def test_validate_and_improve_initialization_with_params(self):
        """Test ValidateAndImprove initialization with parameters"""
        def validate_func(state):
            return True
        
        op = ValidateAndImprove(num_samples=2, improve=False, num_tries=5, validate_function=validate_func)
        assert op.num_samples == 2
        assert op.improve == False
        assert op.num_tries == 5
        assert op.validate_function == validate_func
    
    def test_validate_and_improve_get_thoughts(self):
        """Test ValidateAndImprove get_thoughts returns last thought from each list"""
        op = ValidateAndImprove()
        thought1 = Thought({'key': 'val1'})
        thought2 = Thought({'key': 'val2'})
        thought3 = Thought({'key': 'val3'})
        op.thoughts = [[thought1, thought2], [thought3]]
        
        final_thoughts = op.get_thoughts()
        assert len(final_thoughts) == 2
        assert thought2 in final_thoughts
        assert thought3 in final_thoughts
    
    def test_validate_and_improve_execute_no_predecessors_raises(self):
        """Test ValidateAndImprove raises with no predecessors"""
        op = ValidateAndImprove()
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        with pytest.raises(AssertionError):
            op._execute(lm, prompter, parser)
    
    def test_validate_and_improve_execute_with_validate_function_valid(self):
        """Test ValidateAndImprove with validation function returning valid"""
        def validate_func(state):
            return True
        
        op = ValidateAndImprove(validate_function=validate_func, improve=True)
        
        # Create predecessor
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                self.thoughts = [Thought({'key': 'value'})]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        op.add_predecessor(pred_op)
        
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        op._execute(lm, prompter, parser)
        assert len(op.thoughts) == 1
        assert len(op.thoughts[0]) == 1
        assert op.thoughts[0][0].valid == True
    
    def test_validate_and_improve_execute_with_validate_function_invalid_no_improve(self):
        """Test ValidateAndImprove with validation function returning invalid and no improve"""
        def validate_func(state):
            return False
        
        op = ValidateAndImprove(validate_function=validate_func, improve=False)
        
        # Create predecessor
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                self.thoughts = [Thought({'key': 'value'})]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        op.add_predecessor(pred_op)
        
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        op._execute(lm, prompter, parser)
        assert len(op.thoughts) == 1
        assert len(op.thoughts[0]) == 1
        assert op.thoughts[0][0].valid == False
    
    def test_validate_and_improve_execute_with_lm_and_improvement(self):
        """Test ValidateAndImprove with LM validation and improvement"""
        op = ValidateAndImprove(improve=True, num_tries=2)
        
        # Create predecessor
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                self.thoughts = [Thought({'key': 'value', 'attempt': 0})]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        op.add_predecessor(pred_op)
        
        lm = Mock()
        lm.get_response_texts = Mock(return_value=['improved'])
        lm.query = Mock(return_value='query_result')
        
        prompter = Mock()
        prompter.validation_prompt = Mock(return_value='validate_prompt')
        prompter.improve_prompt = Mock(return_value='improve_prompt')
        
        parser = Mock()
        # First call returns False, then True after improvement
        call_count = [0]
        def parse_validation_side_effect(state, responses):
            call_count[0] += 1
            return call_count[0] > 1
        
        parser.parse_validation_answer = Mock(side_effect=parse_validation_side_effect)
        parser.parse_improve_answer = Mock(return_value={'improved': True})
        
        op._execute(lm, prompter, parser)
        assert len(op.thoughts) >= 1
        assert parser.parse_improve_answer.call_count >= 1
    
    def test_validate_and_improve_execute_max_tries_exceeded(self):
        """Test ValidateAndImprove stops after max tries"""
        def validate_func(state):
            return False  # Always invalid
        
        op = ValidateAndImprove(validate_function=validate_func, improve=True, num_tries=2)
        
        # Create predecessor
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                self.thoughts = [Thought({'key': 'value'})]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        op.add_predecessor(pred_op)
        
        lm = Mock()
        lm.get_response_texts = Mock(return_value=['improved'])
        lm.query = Mock(return_value='query_result')
        
        prompter = Mock()
        prompter.improve_prompt = Mock(return_value='improve_prompt')
        
        parser = Mock()
        parser.parse_improve_answer = Mock(return_value={'improved': True})
        
        op._execute(lm, prompter, parser)
        assert len(op.thoughts) == 1
        # Should have tried improvement num_tries times
        assert len(op.thoughts[0]) == 3  # Initial + 2 tries


@pytest.mark.unit
class TestGenerateOperation:
    """Test Generate operation"""
    
    def test_generate_initialization(self):
        """Test Generate initialization"""
        op = Generate()
        assert op.operation_type == OperationType.generate
        assert op.num_branches_prompt == 1
        assert op.num_branches_response == 1
        assert op.thoughts == []
    
    def test_generate_initialization_with_params(self):
        """Test Generate initialization with parameters"""
        op = Generate(num_branches_prompt=3, num_branches_response=2)
        assert op.num_branches_prompt == 3
        assert op.num_branches_response == 2
    
    def test_generate_get_thoughts(self):
        """Test Generate get_thoughts"""
        op = Generate()
        thought = Thought({'key': 'value'})
        op.thoughts.append(thought)
        assert len(op.get_thoughts()) == 1
    
    def test_generate_execute_no_predecessors_with_kwargs(self):
        """Test Generate with no predecessors uses kwargs"""
        op = Generate(num_branches_prompt=1, num_branches_response=1)
        
        lm = Mock()
        lm.get_response_texts = Mock(return_value=['response'])
        lm.query = Mock(return_value='query_result')
        
        prompter = Mock()
        prompter.generate_prompt = Mock(return_value='prompt')
        
        parser = Mock()
        parser.parse_generate_answer = Mock(return_value=[{'generated': 'value'}])
        
        op._execute(lm, prompter, parser, input_key='input_value')
        assert len(op.thoughts) >= 1
    
    def test_generate_execute_with_empty_predecessor_thoughts(self):
        """Test Generate with predecessor but no thoughts returns early"""
        op = Generate()
        
        # Create predecessor with no thoughts
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                self.thoughts = []
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        op.add_predecessor(pred_op)
        
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        op._execute(lm, prompter, parser)
        assert len(op.thoughts) == 0
    
    def test_generate_execute_with_predecessor_thoughts(self):
        """Test Generate with predecessor thoughts"""
        op = Generate(num_branches_prompt=2, num_branches_response=1)
        
        # Create predecessor
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                self.thoughts = [Thought({'base': 'state'})]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        op.add_predecessor(pred_op)
        
        lm = Mock()
        lm.get_response_texts = Mock(return_value=['response'])
        lm.query = Mock(return_value='query_result')
        
        prompter = Mock()
        prompter.generate_prompt = Mock(return_value='prompt')
        
        parser = Mock()
        parser.parse_generate_answer = Mock(return_value=[{'gen1': 'val1'}, {'gen2': 'val2'}])
        
        op._execute(lm, prompter, parser)
        assert len(op.thoughts) == 2
        # Check that base state is preserved
        assert op.thoughts[0].state['base'] == 'state'
        assert op.thoughts[1].state['base'] == 'state'
    
    def test_generate_execute_warning_on_excessive_thoughts(self):
        """Test Generate logs warning when creating more thoughts than expected"""
        op = Generate(num_branches_prompt=1, num_branches_response=1)
        
        # Create predecessor
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                self.thoughts = [Thought({'base': 'state'})]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        op.add_predecessor(pred_op)
        
        lm = Mock()
        lm.get_response_texts = Mock(return_value=['response'])
        lm.query = Mock(return_value='query_result')
        
        prompter = Mock()
        prompter.generate_prompt = Mock(return_value='prompt')
        
        parser = Mock()
        # Return more thoughts than expected
        parser.parse_generate_answer = Mock(return_value=[
            {'gen1': 'val1'}, {'gen2': 'val2'}, {'gen3': 'val3'}
        ])
        
        with patch.object(op.logger, 'warning') as mock_warning:
            op._execute(lm, prompter, parser)
            # Should log warning since 3 > 1*1*1
            assert mock_warning.called


@pytest.mark.unit
class TestImproveOperation:
    """Test Improve operation"""
    
    def test_improve_initialization(self):
        """Test Improve initialization"""
        op = Improve()
        assert op.operation_type == OperationType.improve
        assert op.thoughts == []
    
    def test_improve_get_thoughts(self):
        """Test Improve get_thoughts"""
        op = Improve()
        thought = Thought({'key': 'value'})
        op.thoughts.append(thought)
        assert len(op.get_thoughts()) == 1
    
    def test_improve_execute_no_predecessors_raises(self):
        """Test Improve raises with no predecessors"""
        op = Improve()
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        with pytest.raises(AssertionError):
            op._execute(lm, prompter, parser)
    
    def test_improve_execute_with_predecessors(self):
        """Test Improve execute with predecessors"""
        op = Improve()
        
        # Create predecessor
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                self.thoughts = [Thought({'original': 'state'})]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        op.add_predecessor(pred_op)
        
        lm = Mock()
        lm.get_response_texts = Mock(return_value=['improved'])
        lm.query = Mock(return_value='query_result')
        
        prompter = Mock()
        prompter.improve_prompt = Mock(return_value='improve_prompt')
        
        parser = Mock()
        parser.parse_improve_answer = Mock(return_value={'improved': True})
        
        op._execute(lm, prompter, parser)
        assert len(op.thoughts) == 1
        assert 'original' in op.thoughts[0].state
        assert 'improved' in op.thoughts[0].state


@pytest.mark.unit
class TestAggregateOperation:
    """Test Aggregate operation"""
    
    def test_aggregate_initialization(self):
        """Test Aggregate initialization"""
        op = Aggregate()
        assert op.operation_type == OperationType.aggregate
        assert op.thoughts == []
        assert op.num_responses == 1
    
    def test_aggregate_initialization_with_params(self):
        """Test Aggregate initialization with parameters"""
        op = Aggregate(num_responses=3)
        assert op.num_responses == 3
    
    def test_aggregate_get_thoughts(self):
        """Test Aggregate get_thoughts"""
        op = Aggregate()
        thought = Thought({'key': 'value'})
        op.thoughts.append(thought)
        assert len(op.get_thoughts()) == 1
    
    def test_aggregate_execute_no_predecessors_raises(self):
        """Test Aggregate raises with no predecessors"""
        op = Aggregate()
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        with pytest.raises(AssertionError):
            op._execute(lm, prompter, parser)
    
    def test_aggregate_execute_with_empty_thoughts_returns(self):
        """Test Aggregate returns early with empty thoughts"""
        op = Aggregate()
        
        # Create predecessor with no thoughts
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                self.thoughts = []
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        op.add_predecessor(pred_op)
        
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        op._execute(lm, prompter, parser)
        assert len(op.thoughts) == 0
    
    def test_aggregate_execute_with_thoughts(self):
        """Test Aggregate execute with thoughts"""
        op = Aggregate(num_responses=1)
        
        # Create predecessor with scored thoughts
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                t1 = Thought({'key1': 'val1'})
                t1.score = 0.5
                t2 = Thought({'key2': 'val2'})
                t2.score = 0.8
                self.thoughts = [t1, t2]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        op.add_predecessor(pred_op)
        
        lm = Mock()
        lm.get_response_texts = Mock(return_value=['aggregated'])
        lm.query = Mock(return_value='query_result')
        
        prompter = Mock()
        prompter.aggregation_prompt = Mock(return_value='aggregate_prompt')
        
        parser = Mock()
        parser.parse_aggregation_answer = Mock(return_value={'aggregated': 'result'})
        
        op._execute(lm, prompter, parser)
        assert len(op.thoughts) == 1
        # Should include keys from both thoughts in order of score
        assert 'key1' in op.thoughts[0].state
        assert 'key2' in op.thoughts[0].state
        assert 'aggregated' in op.thoughts[0].state
    
    def test_aggregate_execute_with_list_parsed(self):
        """Test Aggregate execute when parser returns list"""
        op = Aggregate(num_responses=1)
        
        # Create predecessor
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                t1 = Thought({'key': 'val'})
                t1.score = 0.5
                self.thoughts = [t1]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        op.add_predecessor(pred_op)
        
        lm = Mock()
        lm.get_response_texts = Mock(return_value=['agg1', 'agg2'])
        lm.query = Mock(return_value='query_result')
        
        prompter = Mock()
        prompter.aggregation_prompt = Mock(return_value='aggregate_prompt')
        
        parser = Mock()
        # Return list of dicts
        parser.parse_aggregation_answer = Mock(return_value=[{'agg1': 'r1'}, {'agg2': 'r2'}])
        
        op._execute(lm, prompter, parser)
        assert len(op.thoughts) == 2


@pytest.mark.unit
class TestKeepBestNOperation:
    """Test KeepBestN operation"""
    
    def test_keep_best_n_initialization(self):
        """Test KeepBestN initialization"""
        op = KeepBestN(n=3)
        assert op.operation_type == OperationType.keep_best_n
        assert op.n == 3
        assert op.higher_is_better == True
        assert op.thoughts == []
    
    def test_keep_best_n_initialization_with_params(self):
        """Test KeepBestN initialization with parameters"""
        op = KeepBestN(n=2, higher_is_better=False)
        assert op.n == 2
        assert op.higher_is_better == False
    
    def test_keep_best_n_initialization_zero_raises(self):
        """Test KeepBestN raises when n is zero"""
        with pytest.raises(AssertionError):
            KeepBestN(n=0)
    
    def test_keep_best_n_get_thoughts(self):
        """Test KeepBestN get_thoughts"""
        op = KeepBestN(n=2)
        thought = Thought({'key': 'value'})
        op.thoughts.append(thought)
        assert len(op.get_thoughts()) == 1
    
    def test_keep_best_n_execute_no_predecessors_raises(self):
        """Test KeepBestN raises with no predecessors"""
        op = KeepBestN(n=2)
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        with pytest.raises(AssertionError):
            op._execute(lm, prompter, parser)
    
    def test_keep_best_n_get_best_n_unscored_raises(self):
        """Test get_best_n raises when thoughts not scored"""
        op = KeepBestN(n=2)
        
        # Create predecessor with unscored thoughts
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                self.thoughts = [Thought({'key': 'val'})]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        op.add_predecessor(pred_op)
        
        with pytest.raises(AssertionError):
            op.get_best_n()
    
    def test_keep_best_n_execute_keeps_highest(self):
        """Test KeepBestN keeps highest scored thoughts"""
        op = KeepBestN(n=2, higher_is_better=True)
        
        # Create predecessor with scored thoughts
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                t1 = Thought({'id': 1})
                t1.score = 0.3
                t2 = Thought({'id': 2})
                t2.score = 0.9
                t3 = Thought({'id': 3})
                t3.score = 0.7
                self.thoughts = [t1, t2, t3]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        op.add_predecessor(pred_op)
        
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        op._execute(lm, prompter, parser)
        assert len(op.thoughts) == 2
        # Should keep thoughts with scores 0.9 and 0.7
        scores = [t.score for t in op.thoughts]
        assert 0.9 in scores
        assert 0.7 in scores
    
    def test_keep_best_n_execute_keeps_lowest(self):
        """Test KeepBestN keeps lowest scored thoughts when higher_is_better=False"""
        op = KeepBestN(n=2, higher_is_better=False)
        
        # Create predecessor with scored thoughts
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                t1 = Thought({'id': 1})
                t1.score = 0.3
                t2 = Thought({'id': 2})
                t2.score = 0.9
                t3 = Thought({'id': 3})
                t3.score = 0.7
                self.thoughts = [t1, t2, t3]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        op.add_predecessor(pred_op)
        
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        op._execute(lm, prompter, parser)
        assert len(op.thoughts) == 2
        # Should keep thoughts with scores 0.3 and 0.7
        scores = [t.score for t in op.thoughts]
        assert 0.3 in scores
        assert 0.7 in scores
    
    def test_keep_best_n_execute_error_handling(self):
        """Test KeepBestN handles errors in get_best_n"""
        op = KeepBestN(n=2)
        
        # Create predecessor with mixed scored thoughts (some not float)
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                t1 = Thought({'id': 1})
                t1.score = 0.5
                t2 = Thought({'id': 2})
                t2.score = 'invalid'  # Invalid score
                t3 = Thought({'id': 3})
                t3.score = 0.7
                self.thoughts = [t1, t2, t3]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        op.add_predecessor(pred_op)
        
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        with patch.object(op.logger, 'error') as mock_error:
            op._execute(lm, prompter, parser)
            # Should log errors
            assert mock_error.called
            # Should still produce some results
            assert len(op.thoughts) <= 2


@pytest.mark.unit
class TestKeepValidOperation:
    """Test KeepValid operation"""
    
    def test_keep_valid_initialization(self):
        """Test KeepValid initialization"""
        op = KeepValid()
        assert op.operation_type == OperationType.keep_valid
        assert op.thoughts == []
    
    def test_keep_valid_get_thoughts(self):
        """Test KeepValid get_thoughts"""
        op = KeepValid()
        thought = Thought({'key': 'value'})
        op.thoughts.append(thought)
        assert len(op.get_thoughts()) == 1
    
    def test_keep_valid_execute_no_predecessors_raises(self):
        """Test KeepValid raises with no predecessors"""
        op = KeepValid()
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        with pytest.raises(AssertionError):
            op._execute(lm, prompter, parser)
    
    def test_keep_valid_execute_keeps_valid_thoughts(self):
        """Test KeepValid keeps valid thoughts"""
        op = KeepValid()
        
        # Create predecessor with valid and invalid thoughts
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                t1 = Thought({'id': 1})
                t1.valid = True
                t1._validated = True
                t2 = Thought({'id': 2})
                t2.valid = False
                t2._validated = True
                t3 = Thought({'id': 3})
                t3.valid = True
                t3._validated = True
                self.thoughts = [t1, t2, t3]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        op.add_predecessor(pred_op)
        
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        op._execute(lm, prompter, parser)
        # Should keep only valid thoughts (t1 and t3)
        assert len(op.thoughts) == 2
    
    def test_keep_valid_execute_keeps_unvalidated_thoughts(self):
        """Test KeepValid keeps unvalidated thoughts"""
        op = KeepValid()
        
        # Create predecessor with unvalidated thoughts
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                t1 = Thought({'id': 1})
                # t1 is unvalidated (validated = False)
                self.thoughts = [t1]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        op.add_predecessor(pred_op)
        
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        op._execute(lm, prompter, parser)
        # Should keep unvalidated thoughts
        assert len(op.thoughts) == 1


@pytest.mark.unit
class TestGroundTruthOperation:
    """Test GroundTruth operation"""
    
    def test_ground_truth_initialization(self):
        """Test GroundTruth initialization"""
        def evaluator(state):
            return True
        
        op = GroundTruth(ground_truth_evaluator=evaluator)
        assert op.operation_type == OperationType.ground_truth_evaluator
        assert op.ground_truth_evaluator == evaluator
        assert op.thoughts == []
    
    def test_ground_truth_get_thoughts(self):
        """Test GroundTruth get_thoughts"""
        def evaluator(state):
            return True
        
        op = GroundTruth(ground_truth_evaluator=evaluator)
        thought = Thought({'key': 'value'})
        op.thoughts.append(thought)
        assert len(op.get_thoughts()) == 1
    
    def test_ground_truth_execute_no_predecessors_raises(self):
        """Test GroundTruth raises with no predecessors"""
        def evaluator(state):
            return True
        
        op = GroundTruth(ground_truth_evaluator=evaluator)
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        with pytest.raises(AssertionError):
            op._execute(lm, prompter, parser)
    
    def test_ground_truth_execute_evaluates_thoughts(self):
        """Test GroundTruth evaluates thoughts correctly"""
        def evaluator(state):
            return state.get('correct', False)
        
        op = GroundTruth(ground_truth_evaluator=evaluator)
        
        # Create predecessor with thoughts
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                self.thoughts = [
                    Thought({'correct': True}),
                    Thought({'correct': False}),
                    Thought({'other': 'value'})
                ]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        op.add_predecessor(pred_op)
        
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        op._execute(lm, prompter, parser)
        assert len(op.thoughts) == 3
        assert op.thoughts[0].solved == True
        assert op.thoughts[1].solved == False
        assert op.thoughts[2].solved == False
    
    def test_ground_truth_execute_handles_exceptions(self):
        """Test GroundTruth handles exceptions in evaluator"""
        def evaluator(state):
            raise ValueError("Evaluation error")
        
        op = GroundTruth(ground_truth_evaluator=evaluator)
        
        # Create predecessor
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                self.thoughts = [Thought({'key': 'value'})]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        op.add_predecessor(pred_op)
        
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        op._execute(lm, prompter, parser)
        # Should catch exception and set solved to False
        assert len(op.thoughts) == 1
        assert op.thoughts[0].solved == False


@pytest.mark.unit
class TestSelectorOperation:
    """Test Selector operation"""
    
    def test_selector_initialization(self):
        """Test Selector initialization"""
        def selector_func(thoughts):
            return thoughts
        
        op = Selector(selector=selector_func)
        assert op.operation_type == OperationType.selector
        assert op.selector == selector_func
        assert op.thoughts == []
    
    def test_selector_get_thoughts(self):
        """Test Selector get_thoughts"""
        def selector_func(thoughts):
            return thoughts
        
        op = Selector(selector=selector_func)
        thought = Thought({'key': 'value'})
        op.thoughts.append(thought)
        assert len(op.get_thoughts()) == 1
    
    def test_selector_execute_no_predecessors_uses_kwargs(self):
        """Test Selector with no predecessors uses kwargs"""
        def selector_func(thoughts):
            return [t for t in thoughts if t.state.get('select', False)]
        
        op = Selector(selector=selector_func)
        
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        op._execute(lm, prompter, parser, select=True, other='value')
        # Should create thought from kwargs and apply selector
        assert len(op.thoughts) == 1
        assert op.thoughts[0].state['select'] == True
    
    def test_selector_execute_with_predecessors(self):
        """Test Selector with predecessors"""
        def selector_func(thoughts):
            # Select thoughts with score > 0.5
            return [t for t in thoughts if t.score > 0.5]
        
        op = Selector(selector=selector_func)
        
        # Create predecessor with thoughts
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                t1 = Thought({'id': 1})
                t1.score = 0.3
                t2 = Thought({'id': 2})
                t2.score = 0.8
                t3 = Thought({'id': 3})
                t3.score = 0.6
                self.thoughts = [t1, t2, t3]
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        op.add_predecessor(pred_op)
        
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        op._execute(lm, prompter, parser)
        # Should select only thoughts with score > 0.5
        assert len(op.thoughts) == 2
        scores = [t.score for t in op.thoughts]
        assert 0.8 in scores
        assert 0.6 in scores
    
    def test_selector_execute_with_empty_predecessor_thoughts(self):
        """Test Selector with empty predecessor thoughts uses empty list"""
        def selector_func(thoughts):
            return thoughts
        
        op = Selector(selector=selector_func)
        
        # Create predecessor with no thoughts
        class TestOp(Operation):
            def __init__(self):
                super().__init__()
                self.thoughts = []
            def _execute(self, lm, prompter, parser, **kwargs):
                pass
            def get_thoughts(self):
                return self.thoughts
        
        pred_op = TestOp()
        pred_op.executed = True
        op.add_predecessor(pred_op)
        
        lm = Mock()
        prompter = Mock()
        parser = Mock()
        
        # This should create a thought from kwargs since previous_thoughts is empty
        op._execute(lm, prompter, parser, key='value')
        # Selector should receive a thought with kwargs
        assert len(op.thoughts) == 1
