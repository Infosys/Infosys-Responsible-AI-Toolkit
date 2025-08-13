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

from openai import AzureOpenAI
import os
import google.generativeai as genai
import re
import json


class Azure:
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY") # Retrieve Azure OpenAI API Key from environment variables
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") # Retrieve Azure OpenAI Endpoint from environment variables
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION") # Retrieve Azure OpenAI API Version from environment variables

        # Initialize the AzureOpenAI client with the retrieved API key, API version, and Endpoint
        self.client = AzureOpenAI(
                            api_key = self.api_key, 
                            api_version = self.api_version,
                            azure_endpoint = self.azure_endpoint
                        )
        
    def generate(self, model_name, prompt, mime_type, generated_image_base64):
        # Generate a response using the AzureOpenAI client
        # The completion is based on a prompt provided by the user and a predefined system message

        if model_name == "GPT_4o":
            deployment_engine = os.getenv("AZURE_DEPLOYMENT_ENGINE")
        else:
            deployment_engine = os.getenv("AZURE_DEPLOYMENT_ENGINE")

        if generated_image_base64:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant to analyse images and designed to output JSON.",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{generated_image_base64}"},
                        },
                    ],
                },
            ]
        else:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant to resond to user query and output JSON.",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": prompt
                        },
                    ],
                },
            ]

        completion = self.client.chat.completions.create(
            model=deployment_engine,
            messages=messages,
            temperature=0.0,
            response_format={ "type": "json_object" }
        )

        # Return the content of the first message from the generated completion
        return completion.choices[0].message.content

class Gemini:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")  # Retrieve Gemini API Key from environment variables
        self.gemini_modelname = os.getenv("GEMINI_MODELNAME")  # Retrieve Gemini Endpoint from environment variables

    

        # Configure the Gemini API
        genai.configure(api_key=self.api_key)


    def clean_explanation_string(self, explanation: str) -> str:
        """
        Cleans a wrapped explanation string to extract valid JSON.
        Handles optional 'Response:' prefix and removes all ```json / ``` wrappers,
        even if they appear in the middle or end of the explanation.
        """
        if not explanation:
            return ""

        # Remove 'Response:' prefix if present
        explanation = explanation.strip()
        if explanation.startswith("Response:"):
            explanation = explanation[len("Response:"):].strip()

        # Remove all occurrences of markdown-style ```json and ``` anywhere
        explanation = explanation.replace("```json", "")
        explanation = explanation.replace("```", "")

        return explanation.strip()



    def generate(self, model_name, prompt, mime_type, generated_image_base64):
        if generated_image_base64:
            # Prepare image and prompt
            image_part = {
                "mime_type": mime_type,
                "data": generated_image_base64
            }

        # Use gemini-pro-vision for image + text input
        model = genai.GenerativeModel(self.gemini_modelname)

        if generated_image_base64:
            response = model.generate_content([prompt, image_part])
        else:
            response = model.generate_content(prompt)
        response_obj = response.text
        clean_response = self.clean_explanation_string(response_obj)
        return clean_response
