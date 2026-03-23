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

from abc import ABC, abstractmethod
from typing import List, Dict, Union, Any
import json
import os
# import logging

from llm_explain.config.logger import CustomLogger

logging = CustomLogger()

class AbstractLanguageModel(ABC):
    """
    Abstract base class that defines the interface for all language models.
    """

    def __init__(
        self, config_path: str = "", model_name: str = "", cache: bool = False
    ) -> None:
        """
        Initialize the AbstractLanguageModel instance with configuration, model details, and caching options.

        :param config_path: Path to the config file. Defaults to "".
        :type config_path: str
        :param model_name: Name of the language model. Defaults to "".
        :type model_name: str
        :param cache: Flag to determine whether to cache responses. Defaults to False.
        :type cache: bool
        """
        self.logger = CustomLogger()
        self.config: Dict = None
        self.model_name: str = model_name
        self.cache = cache
        if self.cache:
            self.respone_cache: Dict[str, List[Any]] = {}
        self.load_config(config_path)
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0
        self.cost: float = 0.0

    def load_config(self, path: str) -> None:
        """
        Load configuration from a specified path.

        :param path: Path to the config file. If an empty path provided,
                     default is `config.json` in the current directory.
        :type path: str
        """
        if path == "":
            current_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(current_dir, "config.json")

        with open(path, "r") as f:
            self.config = json.load(f)

        # self.logger.debug(f"Loaded config from {path} for {self.model_name}")

    def clear_cache(self) -> None:
        """
        Clear the response cache.
        """
        self.respone_cache.clear()

    @abstractmethod
    def query(self, query: str, num_responses: int = 1) -> Any:
        """
        Abstract method to query the language model.

        :param query: The query to be posed to the language model.
        :type query: str
        :param num_responses: The number of desired responses.
        :type num_responses: int
        :return: The language model's response(s).
        :rtype: Any
        """
        pass

    @abstractmethod
    def get_response_texts(self, query_responses: Union[List[Any], Any]) -> List[str]:
        """
        Abstract method to extract response texts from the language model's response(s).

        :param query_responses: The responses returned from the language model.
        :type query_responses: Union[List[Any], Any]
        :return: List of textual responses.
        :rtype: List[str]
        """
        pass
