''' 
Copyright 2024-2025 Infosys Ltd.

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

from llm.config.logger import CustomLogger
import openai
import json
import time
import os

log = CustomLogger()

class Azure:
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY_DALL_E_2") # Retrieve Azure OpenAI API Key from environment variables
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_DALL_E_2") # Retrieve Azure OpenAI Endpoint from environment variables
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION_DALL_E_2") # Retrieve Azure OpenAI API Version from environment variables

        # Initialize the AzureOpenAI client with the retrieved API key, API version, and Endpoint
        self.client = openai.AzureOpenAI(
                            api_key = self.api_key, 
                            api_version = self.api_version,
                            azure_endpoint = self.azure_endpoint
                        )
        
    def generate_image(self, prompt: str, model: str) -> str:
        """
        Generates an image based on the given prompt using the specified model.

        Args:
            prompt (str): The text prompt to generate the image.
            model (str): The model to use for image generation. If "DALL-E-2" is specified,
                        it will use the model defined in the environment variable "AZURE_OPENAI_MODEL_DALL_E_2".

        Returns:
            str: The base64 encoded image.
        """
        max_retries = 5
        retry_wait_time = 2  # seconds

        for attempt in range(max_retries):
            try:
                if model == "DALL-E-2":
                    model = os.getenv("AZURE_OPENAI_MODEL_DALL_E_2")
                response = self.client.images.generate(model=model,
                                                    prompt=prompt,
                                                    n=1,
                                                    response_format="b64_json")

                base64_image = json.loads(response.model_dump_json())['data'][0]['b64_json']

                return base64_image

            except Exception as e:
                log.error(f"Error generating image: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_wait_time)
            except Exception as e:
                log.error(f"Error generating image: {e}")
                raise Exception(f"Error generating image: {e}")