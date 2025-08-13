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
import backoff
import os
import random
import time
from typing import List, Dict, Union

from openai import AzureOpenAI
from openai import ChatCompletion

from .abstract_language_model import AbstractLanguageModel


class ChatGPT(AbstractLanguageModel):
    """
    The ChatGPT class handles interactions with the Azure OpenAI models using the provided configuration.

    Inherits from the AbstractLanguageModel and implements its abstract methods.
    """

    def __init__(
        self, 
        config_path: str = "",
        model_name: str = "gpt4", 
        cache: bool = False
    ) -> None:
        """
        Initialize the ChatGPT instance with configuration from environment variables, model details, and caching options.

        :param model_name: Name of the model, default is 'chatgpt'. Used to select the correct configuration.
        :type model_name: str
        :param cache: Flag to determine whether to cache responses. Defaults to False.
        :type cache: bool
        """
        super().__init__(config_path, model_name, cache) # config_path is not used, so passing an empty string

        # Get configuration from environment variables
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if self.api_key is None:
            raise ValueError("AZURE_OPENAI_API_KEY environment variable is not set.")

        self.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
        if self.api_base is None:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is not set.")

        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15") # Default to "2023-05-15"

        self.deployment_name = os.getenv("AZURE_DEPLOYMENT_ENGINE")
        if self.deployment_name is None:
            raise ValueError("Deployment name is not set.")

        # Get other parameters from config file (if available) or use defaults
        self.config: Dict = self.config.get(model_name, {}) 
        self.prompt_token_cost: float = self.config.get("prompt_token_cost", 0.0015)
        self.response_token_cost: float = self.config.get("response_token_cost", 0.002)
        self.temperature: float = self.config.get("temperature", 1.0)
        self.max_tokens: int = self.config.get("max_tokens", 1024)
        self.stop: Union[str, List[str]] = self.config.get("stop", None)  

        # Initialize the Azure OpenAI Client
        self.client = AzureOpenAI(
            api_key=self.api_key, 
            api_version=self.api_version,
            azure_endpoint=self.api_base
        )

    def query(
        self, query: str, num_responses: int = 1
    ) -> Union[List[ChatCompletion], ChatCompletion]:
        """
        Query the Azure OpenAI model for responses.

        :param query: The query to be posed to the language model.
        :type query: str
        :param num_responses: Number of desired responses, default is 1.
        :type num_responses: int
        :return: Response(s) from the Azure OpenAI model.
        :rtype: Dict
        """
        if self.cache and query in self.respone_cache:
            return self.respone_cache[query]

        if num_responses == 1:
            response = self.chat([{"role": "user", "content": query}], num_responses)
        else:
            response = []
            next_try = num_responses
            total_num_attempts = num_responses
            while num_responses > 0 and total_num_attempts > 0:
                try:
                    assert next_try > 0
                    res = self.chat([{"role": "user", "content": query}], next_try)
                    response.append(res)
                    num_responses -= next_try
                    next_try = min(num_responses, next_try)
                except Exception as e:
                    next_try = (next_try + 1) // 2
                    self.logger.warning(
                        f"Error in chatgpt: {e}, trying again with {next_try} samples"
                    )
                    time.sleep(random.randint(1, 3))
                    total_num_attempts -= 1

        if self.cache:
            self.respone_cache[query] = response
        return response

    @backoff.on_exception(backoff.expo, Exception, max_time=10, max_tries=6)
    def chat(self, messages: List[Dict], num_responses: int = 1) -> ChatCompletion:
        """
        Send chat messages to the Azure OpenAI model and retrieves the model's response.
        Implements backoff on errors.

        :param messages: A list of message dictionaries for the chat.
        :type messages: List[Dict]
        :param num_responses: Number of desired responses, default is 1.
        :type num_responses: int
        :return: The Azure OpenAI model's response.
        :rtype: ChatCompletion
        """
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            n=num_responses,
            stop=self.stop,
        )

        # Extract usage information differently for Azure OpenAI
        self.prompt_tokens += response.usage.prompt_tokens
        self.completion_tokens += response.usage.completion_tokens
        prompt_tokens_k = float(self.prompt_tokens) / 1000.0
        completion_tokens_k = float(self.completion_tokens) / 1000.0
        self.cost += (
            self.prompt_token_cost * prompt_tokens_k
            + self.response_token_cost * completion_tokens_k
        )
        return response

    def get_response_texts(
        self, query_response: Union[List[ChatCompletion], ChatCompletion]
    ) -> List[str]:
        """
        Extract the response texts from the query response.

        :param query_response: The response dictionary (or list of dictionaries) from the Azure OpenAI model.
        :type query_response: Union[List[ChatCompletion], ChatCompletion]
        :return: List of response strings.
        :rtype: List[str]
        """
        if not isinstance(query_response, List):
            query_response = [query_response]
        return [
            choice.message.content
            for response in query_response
            for choice in response.choices
        ]