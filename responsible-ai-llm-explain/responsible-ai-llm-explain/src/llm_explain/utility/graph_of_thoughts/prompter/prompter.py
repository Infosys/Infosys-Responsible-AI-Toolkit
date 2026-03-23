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

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List


class Prompter(ABC):
    """
    Abstract base class that defines the interface for all prompters.
    Prompters are used to generate the prompts for the language models.
    """

    @abstractmethod
    def aggregation_prompt(self, state_dicts: List[Dict], **kwargs) -> str:
        """
        Generate a aggregation prompt for the language model.

        :param state_dicts: The thought states that should be aggregated.
        :type state_dicts: List[Dict]
        :param kwargs: Additional keyword arguments.
        :return: The aggregation prompt.
        :rtype: str
        """
        pass

    @abstractmethod
    def improve_prompt(self, **kwargs) -> str:
        """
        Generate an improve prompt for the language model.
        The thought state is unpacked to allow for additional keyword arguments
        and concrete implementations to specify required arguments explicitly.

        :param kwargs: Additional keyword arguments.
        :return: The improve prompt.
        :rtype: str
        """
        pass

    @abstractmethod
    def generate_prompt(self, num_branches: int, **kwargs) -> str:
        """
        Generate a generate prompt for the language model.
        The thought state is unpacked to allow for additional keyword arguments
        and concrete implementations to specify required arguments explicitly.

        :param num_branches: The number of responses the prompt should ask the LM to generate.
        :type num_branches: int
        :param kwargs: Additional keyword arguments.
        :return: The generate prompt.
        :rtype: str
        """
        pass

    @abstractmethod
    def validation_prompt(self, **kwargs) -> str:
        """
        Generate a validation prompt for the language model.
        The thought state is unpacked to allow for additional keyword arguments
        and concrete implementations to specify required arguments explicitly.

        :param kwargs: Additional keyword arguments.
        :return: The validation prompt.
        :rtype: str
        """
        pass

    @abstractmethod
    def score_prompt(self, state_dicts: List[Dict], **kwargs) -> str:
        """
        Generate a score prompt for the language model.

        :param state_dicts: The thought states that should be scored,
                            if more than one, they should be scored together.
        :type state_dicts: List[Dict]
        :param kwargs: Additional keyword arguments.
        :return: The score prompt.
        :rtype: str
        """
        pass
