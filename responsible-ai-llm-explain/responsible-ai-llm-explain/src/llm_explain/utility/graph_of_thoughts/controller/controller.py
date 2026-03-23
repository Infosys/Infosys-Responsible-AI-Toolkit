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

import os
import json
# import logging
from typing import List
from ..language_models import AbstractLanguageModel
from ..operations import GraphOfOperations, Thought
from ..prompter import Prompter
from ..parser import Parser

from llm_explain.config.logger import CustomLogger

logging = CustomLogger()

class Controller:
    """
    Controller class to manage the execution flow of the Graph of Operations,
    generating the Graph Reasoning State.
    This involves language models, graph operations, prompting, and parsing.
    """

    def __init__(
        self,
        lm: AbstractLanguageModel,
        graph: GraphOfOperations,
        prompter: Prompter,
        parser: Parser,
        problem_parameters: dict,
    ) -> None:
        """
        Initialize the Controller instance with the language model,
        operations graph, prompter, parser, and problem parameters.

        :param lm: An instance of the AbstractLanguageModel.
        :type lm: AbstractLanguageModel
        :param graph: The Graph of Operations to be executed.
        :type graph: OperationsGraph
        :param prompter: An instance of the Prompter class, used to generate prompts.
        :type prompter: Prompter
        :param parser: An instance of the Parser class, used to parse responses.
        :type parser: Parser
        :param problem_parameters: Initial parameters/state of the problem.
        :type problem_parameters: dict
        """
        self.logger = CustomLogger()
        self.lm = lm
        self.graph = graph
        self.prompter = prompter
        self.parser = parser
        self.problem_parameters = problem_parameters
        self.run_executed = False

    def run(self) -> None:
        """
        Run the controller and execute the operations from the Graph of
        Operations based on their readiness.
        Ensures the program is in a valid state before execution.
        :raises AssertionError: If the Graph of Operation has no roots.
        :raises AssertionError: If the successor of an operation is not in the Graph of Operations.
        """
        # self.logger.debug("Checking that the program is in a valid state")
        assert self.graph.roots is not None, "The operations graph has no root"
        # self.logger.debug("The program is in a valid state")

        execution_queue = [
            operation
            for operation in self.graph.operations
            if operation.can_be_executed()
        ]
        # self.logger.info(execution_queue)
        while len(execution_queue) > 0:
            current_operation = execution_queue.pop(0)
            # self.logger.info("Executing operation %s", current_operation.operation_type)
            current_operation.execute(
                self.lm, self.prompter, self.parser, **self.problem_parameters
            )
            # self.logger.debug("Operation %s executed", current_operation.operation_type)
            for operation in current_operation.successors:
                assert (
                    operation in self.graph.operations
                ), "The successor of an operation is not in the operations graph"
                if operation.can_be_executed():
                    execution_queue.append(operation)
        # self.logger.info("All operations executed")
        self.run_executed = True

    def get_final_thoughts(self) -> List[List[Thought]]:
        """
        Retrieve the final thoughts after all operations have been executed.

        :return: List of thoughts for each operation in the graph's leaves.
        :rtype: List[List[Thought]]
        :raises AssertionError: If the `run` method hasn't been executed yet.
        """
        assert self.run_executed, "The run method has not been executed"
        return [operation.get_thoughts() for operation in self.graph.leaves]

    def output_graph(self, path: str) -> None:
        """
        Serialize the state and results of the operations graph to a JSON file.

        :param path: The path to the output file.
        :type path: str
        """
        output = []
        for operation in self.graph.operations:
            operation_serialized = {
                "operation": operation.operation_type.name,
                "thoughts": [thought.state for thought in operation.get_thoughts()],
            }
            if any([thought.scored for thought in operation.get_thoughts()]):
                operation_serialized["scored"] = [
                    thought.scored for thought in operation.get_thoughts()
                ]
                operation_serialized["scores"] = [
                    thought.score for thought in operation.get_thoughts()
                ]
            if any([thought.validated for thought in operation.get_thoughts()]):
                operation_serialized["validated"] = [
                    thought.validated for thought in operation.get_thoughts()
                ]
                operation_serialized["validity"] = [
                    thought.valid for thought in operation.get_thoughts()
                ]
            if any(
                [
                    thought.compared_to_ground_truth
                    for thought in operation.get_thoughts()
                ]
            ):
                operation_serialized["compared_to_ground_truth"] = [
                    thought.compared_to_ground_truth
                    for thought in operation.get_thoughts()
                ]
                operation_serialized["problem_solved"] = [
                    thought.solved for thought in operation.get_thoughts()
                ]
            output.append(operation_serialized)

        output.append(
            {
                "prompt_tokens": self.lm.prompt_tokens,
                "completion_tokens": self.lm.completion_tokens,
                "cost": self.lm.cost,
            }
        )

        with open(path, "w") as file:
            file.write(json.dumps(output, indent=2))
            
    def format_graph(self, source: str):
        
        def count_unique_matches(l1, l2):
            l1_set = set(l1)  # Convert l1 to a set for unique elements
            l2_set = set(l2)  # Convert l2 to a set for unique elements
            matches = l1_set & l2_set  # Find the intersection
            return len(matches)
        
        import copy
        
        with open(source, "r") as file:
            data = json.load(file)
        data_new = copy.deepcopy(data)
        
        global_thoughts = []
        global_thoughts_num = []
        data_thoughts = {}

        # generate
        l = []
        for i in range(len(data[0]['thoughts'])):
            l.append(data[0]['thoughts'][i]['current'])
            if data[0]['thoughts'][i]['current'] not in global_thoughts:
                global_thoughts.append(data[0]['thoughts'][i]['current'])
                global_thoughts_num.append(f"thought_{i+1}")
            data_new[0]['thoughts'][i]['current'] = f"thought_{i+1}"
            data_new[0]['thoughts'][i]['score'] = data_new[1]['scores'][i]
            data_thoughts[f"thought_{i+1}"] = data[0]['thoughts'][i]['current']

        # score
        for i in range(len(data[1]['thoughts'])):
            data_new[1]['thoughts'][i]['current'] = f"thought_{i+1}"

        # keep_best_n
        prev_thoughts = {}
        for i in range(len(data[2]['thoughts'])):
            if data[2]['thoughts'][i]['current'] in l:
                data_new[2]['thoughts'][i]['current'] = f"thought_{l.index(data[2]['thoughts'][i]['current'])+1}"
                data_new[2]['thoughts'][i]['score'] = data_new[2]['scores'][i]
                # data_thoughts[f"thought_{l.index(data[2]['thoughts'][i]['current'])+1}"] = data[2]['thoughts'][i]['current']
            elif data[2]['thoughts'][i]['current'] in global_thoughts:
                data_new[2]['thoughts'][i]['current'] = f"thought_{global_thoughts_num[global_thoughts.index(data[2]['thoughts'][i]['current'])]}"
                data_new[2]['thoughts'][i]['score'] = data_new[2]['scores'][i]
                # data_thoughts[f"thought_{global_thoughts_num[global_thoughts.index(data[2]['thoughts'][i]['current'])]}"] = data[2]['thoughts'][i]['current']
            prev_thoughts[str(i)] = data[2]['thoughts'][i]['current']

        # aggregate
        len1 = len(data[0]['thoughts'])
        l, l3 = [], []
        for i in range(len(data[3]['thoughts'])):
            l.append(data[3]['thoughts'][i]['current'])
            temp = []
            for j in range(len(data[2]['thoughts'])):
                temp.append(count_unique_matches(data[2]['thoughts'][j]['current'].split(), data[3]['thoughts'][i]['current'].split()))
            val = data_new[2]['thoughts'][temp.index(max(temp))]['current']
            if data[3]['thoughts'][i]['current'] not in global_thoughts:
                global_thoughts.append(data[3]['thoughts'][i]['current'])
                global_thoughts_num.append(f"aggregate_{val}")
            data_new[3]['thoughts'][i]['current'] = f"aggregate_{val}"
            data_new[3]['thoughts'][i]['score'] = data_new[4]['scores'][i]
            # data_thoughts[f"{val}_thought_{i+1+len1}"] = data[3]['thoughts'][i]['current']
            l3.append(f"aggregate_{val}")

        # score
        data_new[4]['thoughts'] = data_new[3]['thoughts']

        # keep_best_n
        for i in range(len(data[5]['thoughts'])):
            if data[5]['thoughts'][i]['current'] in l:
                data_new[5]['thoughts'][i]['current'] = l3[l.index(data[5]['thoughts'][0]['current'])]
                data_new[5]['thoughts'][i]['score'] = data_new[5]['scores'][i]
                data_thoughts[l3[l.index(data[5]['thoughts'][0]['current'])]] = data[5]['thoughts'][i]['current']
                # data_thoughts['final_thought'] = data[5]['thoughts'][i]['current']
            elif data[5]['thoughts'][i]['current'] in global_thoughts:
                data_new[5]['thoughts'][i]['current'] = global_thoughts_num[global_thoughts.index(data[5]['thoughts'][i]['current'])]
                data_new[5]['thoughts'][i]['score'] = data_new[5]['scores'][i]
                data_thoughts[global_thoughts_num[global_thoughts.index(data[5]['thoughts'][i]['current'])]] = data[5]['thoughts'][i]['current']
                # data_thoughts['final_thought'] = data[5]['thoughts'][i]['current']
        
        # data_new[5]['thoughts'][i]['current'] = 'final_thought'
        
        for i in range(len(data_new)):
            if i >= len(data_new):
                    break
            if 'operation' in data_new[i] and data_new[i]['operation'] == 'score':
                del data_new[i]
            if 'operation' in data_new[i] and data_new[i]['operation'] == 'keep_best_n':
                del data_new[i]['scored']
                del data_new[i]['scores']
                
        os.remove(source)
        
        return data_new, data_thoughts
