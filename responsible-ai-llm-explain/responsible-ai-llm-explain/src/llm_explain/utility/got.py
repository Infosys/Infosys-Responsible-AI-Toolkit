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
import re
# import logging
import datetime
import json
from statistics import fmean
from typing import Dict, List, Callable, Set, Union

from .graph_of_thoughts import controller, language_models, operations, prompter, parser
from llm_explain.config.logger import CustomLogger

logging = CustomLogger()

class GeneralPrompter(prompter.Prompter):
    """
    GeneralPrompter provides the generation of prompts for any given task or question.
    """

    def __init__(self, task: str, question: str):
        self.logger = logging
        self.task = task
        self.question = question

    def generate_prompt(
        self,
        num_branches: int,
        # documents: List[str],  # Removed
        method: str,
        # parts: Set[str], # Removed
        current: str,
        **kwargs,
    ) -> str:
        """
        Generate a prompt for the language model based on the task and question.

        :param num_branches: The number of responses the prompt should ask the LM to generate.
        :type num_branches: int
        :param method: Method for which the generate prompt is generated.
        :type method: str
        :param current: The intermediate solution (not used for this prompter).
        :type current: str
        :param kwargs: Additional keyword arguments.
        :return: The generate prompt.
        :rtype: str
        :raise AssertionError: If method is not implemented yet.
        """

        prompt = f"You are a helpful AI assistant. Your task is to {self.task}. \n\n"
        prompt += f"**Question:** {self.question} \n\n"

        if method.startswith("io") or method.startswith("cot"):
            prompt += "Think step by step and provide a detailed reasoning process to arrive at the final answer. \n\n"
            prompt += "**Reasoning:**\n"
        elif method.startswith("tot"):
            prompt += "Think step by step and provide a detailed reasoning process to arrive at the final answer. You can use previous reasoning steps to improve the current answer. \n\n"
            prompt += "**Reasoning:**\n"
        elif method.startswith("got"):
            prompt += "Think step by step and provide a detailed reasoning process to arrive at the final answer. You can use previous reasoning steps to improve the current answer, and focus on specific parts of the reasoning process if needed. \n\n"
            prompt += "**Reasoning:**\n"
        else:
            assert False, "Not implemented yet."

        return prompt

    def score_prompt(self, state_dicts: List[Dict], **kwargs) -> str:
        """
        Generate a score prompt for the language model.
        
        :param state_dicts: The thought states that should be scored,
                            if more than one, they should be scored together.
        :type state_dicts: List[Dict]
        :param kwargs: Additional keyword arguments.
        :return: The score prompt.
        :rtype: str
        :raise AssertionError: If more than one thought state is supplied.
        """

        assert len(state_dicts) == 1, "Only one state is allowed for scoring."
        if len(state_dicts) == 1:
            prompt = f"You are a helpful AI assistant. Your task is to {self.task}. \n\n"
            prompt += f"**Question:** {self.question} \n\n"
            prompt += f"**Reasoning:** {state_dicts[0]['current']} \n\n"
            prompt += "Please score the reasoning process in terms of how much redundant information is contained, independent of the original reasoning, as well as how much information is retained from the original reasoning. \n\n"
            prompt += "A score of 10 for redundancy implies that absolutely no information is redundant, while a score of 0 implies that at least half of the information is redundant (so everything is at least mentioned twice). \n\n"
            prompt += "A score of 10 for retained information implies that all information from the original reasoning is retained, while a score of 0 implies that no information is retained. \n\n"
            prompt += "You may provide reasoning for your scoring, but the final score for redundancy should be between the tags <Redundancy> and </Redundancy>, and the final score for retained information should be between the tags <Retained> and </Retained>, without any additional text within any of those tags.\n\n"
            return prompt

    def aggregation_prompt(self, state_dicts: List[Dict], **kwargs) -> str:
        """
        Generate an aggregation prompt for the language model.

        :param state_dicts: The thought states that should be aggregated.
        :type state_dicts: List[Dict]
        :param kwargs: Additional keyword arguments.
        :return: The aggregation prompt.
        :rtype: str
        """

        prompt = f"You are a helpful AI assistant. Your task is to {self.task}. \n\n"
        prompt += f"**Question:** {self.question} \n\n"
        prompt += "Combine the following reasoning steps into a new one, maximizing their advantages and overall information retention, while minimizing redundancy.\n\n"

        for i, state_dict in enumerate(state_dicts):
            prompt += f"**Reasoning {i+1}:** {state_dict['current']}\n\n"

        prompt += "Output only the new reasoning process between the tags <Merged> and </Merged>, without any additional text."

        return prompt

    def improve_prompt(self, **kwargs) -> str:
        """
        Generate an improve prompt for the language model.

        :param kwargs: Additional keyword arguments.
        :return: The improve prompt.
        :rtype: str
        """
        pass

    def validation_prompt(self, **kwargs) -> str:
        """
        Generate a validation prompt for the language model.

        :param kwargs: Additional keyword arguments.
        :return: The validation prompt.
        :rtype: str
        """
        pass


class GeneralParser(parser.Parser):
    """
    GeneralParser provides the parsing of language model responses for any given task or question.
    """

    def __init__(self) -> None:
        """
        Inits the response cache.
        """
        self.cache = {}

    def strip_answer_helper(self, text: str, tag: str = "") -> str:
        """
        Helper function to remove tags from a text.

        :param text: The input text.
        :type text: str
        :param tag: The tag to be stripped. Defaults to "".
        :type tag: str
        :return: The stripped text.
        :rtype: str
        """

        text = text.strip()
        if "Output:" in text:
            text = text[text.index("Output:") + len("Output:") :].strip()
        if tag != "":
            start = text.rfind(f"<{tag}>")
            end = text.rfind(f"</{tag}>")
            if start != -1 and end != -1:
                text = text[start + len(f"<{tag}>") : end].strip()
            elif start != -1:
                # logging.warning(
                #     f"Only found the start tag <{tag}> in answer: {text}. Returning everything after the tag."
                # )
                text = text[start + len(f"<{tag}>") :].strip()
            elif end != -1:
                # logging.warning(
                #     f"Only found the end tag </{tag}> in answer: {text}. Returning everything before the tag."
                # )
                text = text[:end].strip()
            # else:
            #     logging.warning(
            #         f"Could not find any tag {tag} in answer: {text}. Returning the full answer."
            #     )
        return text

    def parse_aggregation_answer(
        self, states: List[Dict], texts: List[str]
    ) -> Union[Dict, List[Dict]]:
        """
        Parse the response from the language model for an aggregation prompt.

        :param states: The thought states used to generate the prompt.
        :type states: List[Dict]
        :param texts: The responses to the prompt from the language model.
        :type texts: List[str]
        :return: The new thought states after parsing the respones from the language model.
        :rtype: Union[Dict, List[Dict]]
        """

        new_states = []
        for text in texts:
            text = self.strip_answer_helper(text, "Merged")
            new_state = states[0].copy()
            new_state["current"] = text
            new_states.append(new_state)
        return new_states

    def parse_generate_answer(self, state: Dict, texts: List[str]) -> List[Dict]:
        """
        Parse the response from the language model for a generate prompt.

        :param state: The thought state used to generate the prompt.
        :type state: Dict
        :param texts: The responses to the prompt from the language model.
        :type texts: List[str]
        :return: The new thought states after parsing the respones from the language model.
        :rtype: List[Dict]
        """
        new_states = []
        for text in texts:
            text = text.strip()
            new_state = state.copy()
            new_state["current"] = text
            new_states.append(new_state)
        return new_states

    def parse_score_answer(self, states: List[Dict], texts: List[str]) -> List[float]:
        """
        Parse the response from the language model for a score prompt.

        :param states: The thought states used to generate the prompt.
        :type states: List[Dict]
        :param texts: The responses to the prompt from the language model.
        :type texts: List[str]
        :return: The scores for the thought states.
        :rtype: List[float]
        :raise AssertionError: If the number of thought states is not one.
        """
        assert len(states) == 1, "Only one state is allowed for scoring."
        if len(states) == 1:
            # individual scoring
            redundancy_scores = []
            retain_scores = []
            for text in texts:
                answer = self.strip_answer_helper(text, "Redundancy")
                res = re.findall(r"\d+\.?\d*", answer)
                if len(res) == 1:
                    redundancy_scores.append(float(res[0]))
                elif len(res) > 1:
                    # logging.warning(
                    #     f"Found multiple redundancy scores in answer: {text}. Returning the last one."
                    # )
                    redundancy_scores.append(float(res[-1]))
                # else:
                #     logging.warning(
                #         f"Could not find any redundancy score in answer: {text}. Ignoring this answer."
                #     )
                answer = self.strip_answer_helper(text, "Retained")
                res = re.findall(r"\d+\.?\d*", answer)
                if len(res) == 1:
                    retain_scores.append(float(res[0]))
                elif len(res) > 1:
                    # logging.warning(
                    #     f"Found multiple retained scores in answer: {text}. Returning the last one."
                    # )
                    retain_scores.append(float(res[-1]))
                # else:
                #     logging.warning(
                #         f"Could not find any retained score in answer: {text}. Ignoring this answer."
                #     )
            if len(redundancy_scores) == 0 or len(retain_scores) == 0:
                # logging.warning(
                #     f"Could not find any valid score in any answer. Returning 0.0."
                # )
                return [0.0]
            mean_redundancy = fmean(redundancy_scores)
            mean_retain = fmean(retain_scores)
            f1 = 2 * mean_redundancy * mean_retain / (mean_redundancy + mean_retain)
            return [f1]

    def parse_improve_answer(self, state: Dict, texts: List[str]) -> Dict:
        """
        Parse the response from the language model for an improve prompt.

        :param state: The thought state used to generate the prompt.
        :type state: Dict
        :param texts: The responses to the prompt from the language model.
        :type texts: List[str]
        :return: The new thought state after parsing the responses from the language model.
        :rtype: Dict
        """
        pass

    def parse_validation_answer(self, state: Dict, texts: List[str]) -> bool:
        """
        Parse the response from the language model for a validation prompt.

        :param state: The thought state used to generate the prompt.
        :type state: Dict
        :param texts: The responses to the prompt from the language model.
        :type texts: List[str]
        :return: Whether the thought state is valid or not.
        :rtype: bool
        """
        pass

def got() -> operations.GraphOfOperations:
    """
    Generates the Graph of Operations for the GoT method.

    :return: Graph of Operations
    :rtype: GraphOfOperations
    """
    try:
        operations_graph = operations.GraphOfOperations()

        operations_graph.append_operation(operations.Generate(1, 5))
        operations_graph.append_operation(operations.Score(3, False))
        keep_best = operations.KeepBestN(3, True)
        operations_graph.append_operation(keep_best)
        
        operations_graph.append_operation(operations.Aggregate(5))
        operations_graph.append_operation(operations.Score(3, False))
        keep_best2 = operations.KeepBestN(1, True)
        keep_best2.add_predecessor(keep_best)
        operations_graph.append_operation(keep_best2)

        return operations_graph
    except Exception as e:
        logging.error(e,exc_info=True)
        raise

def run(
    task: str,
    question: str,
    methods: List[Callable[[], operations.GraphOfOperations]],
    budget: float,
    lm_name: str = "gpt4",
) -> float:
    """
    Controller function that executes each specified method for the given task
    and question while the budget is not exhausted.

    :param task: The task to be performed.
    :type task: str
    :param question: The question to be answered.
    :type question: str
    :param methods: List of functions to generate Graphs of Operations.
    :type methods: Each function generates a Graph of Operation.
    :param budget: Language model budget for the execution in dollars.
    :type budget: float
    :param lm_name: Name of the language model to be used.
    :type lm_name: str
    :return: Spent budget in dollars.
    :rtype: float
    """
    
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    for method in methods:
        logging.info(f"Running method Graph of Thoughts")
        # logging.info(f"Budget left: {budget}")
        if budget <= 0.0:
            # logging.error(
            #     f"Budget has been depleted, stopping. Method {method.__name__} has not been run."
            # )
            break

        lm = language_models.AzureOpenAI(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
            "./config.json",
            ),
            model_name=lm_name,
            cache=True,
            )
            
        operations_graph = method()
        executor = controller.Controller(
            lm,
            operations_graph,
            GeneralPrompter(task, question),
            GeneralParser(),
            {
                "current": "",
                "method": method.__name__,
            },
        )
        try:
            executor.run()
        except Exception as e:
            logging.error(f"Exception: {e}")
            raise
        path = os.path.join(
            results_dir,
            "result.json",
        )
        for operation in operations_graph.operations:
            for thought in operation.thoughts:
                # Delete unused keys in the thought state
                if "documents" in thought.state:
                    del thought.state["documents"]
                if "parts" in thought.state:
                    del thought.state["parts"]
                if "method" in thought.state:
                    del thought.state["method"]
        executor.output_graph(path)
        
        formatted_graph, formatted_thoughts = executor.format_graph(path)
        budget -= lm.cost

    return formatted_graph, formatted_thoughts
