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

from llm_explain.config.logger import CustomLogger
import openai
import os
import requests
import google.generativeai as genai
import json
import boto3
from datetime import datetime

log = CustomLogger()

class Azure:
    def __init__(self):
        
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY") # Retrieve Azure OpenAI API key from environment variables
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") # Retrieve Azure OpenAI endpoint from environment variables
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION") # Retrieve Azure OpenAI API version from environment variables
        self.deployment_engine = os.getenv("AZURE_DEPLOYMENT_ENGINE") # Retrieve Azure OpenAI deployment engine (model) from environment variables

        # Initialize the AzureOpenAI client with the retrieved API key, API version, and endpoint
        self.client = openai.AzureOpenAI(
                            api_key = self.api_key, 
                            api_version = self.api_version,
                            azure_endpoint = self.azure_endpoint
                        )
        
    def generate(self, prompt, modelName=None):
        try:
            if modelName is not None:
                modelName = modelName.lower()
            if modelName == "gpt-4o":
                completion = self.client.chat.completions.create(
                    model=self.deployment_engine, # Specify the model (deployment engine) to use
                    messages=[
                        {
                            "role": "system", # System message to set the context for the AI
                            "content": "You are a helpful assistant.",
                        },
                        {
                            "role": "user", # User message that contains the actual prompt
                            "content": prompt
                        }
                    ],
                    response_format={ "type": "json_object" }
                )
            else:
                completion = self.client.chat.completions.create(
                    model= self.deployment_engine, # Specify the model (deployment engine) to use
                    messages=[
                        {
                            "role": "system", # System message to set the context for the AI
                            "content": "You are a helpful assistant.",
                        },
                        {
                            "role": "user", # User message that contains the actual prompt
                            "content": prompt
                        }
                    ],
                    # response_format={ "type": "json_object" }
                )

            # Extract token usage information
            input_tokens = completion.usage.prompt_tokens
            output_tokens = completion.usage.completion_tokens

            # Return the content of the first message from the generated completion
            return completion.choices[0].message.content, input_tokens, output_tokens
        except openai.APIConnectionError as e:
            log.error(f"Azure OpenAI API connection error: {e}")
            raise Exception("Azure OpenAI API connection error")


class Gemini:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model_name_pro = os.getenv("GEMINI_MODEL_NAME_PRO")
        self.gemini_model_name_flash = os.getenv("GEMINI_MODEL_NAME_FLASH")

    def generate(self, prompt, modelName=None):
        try:
            if modelName is not None:
                modelName = modelName.lower()
                if modelName == 'gemini-pro':
                    modelName = self.gemini_model_name_pro
                elif modelName == 'gemini-flash':
                    modelName = self.gemini_model_name_flash

                genai.configure(api_key=self.gemini_api_key)
                model = genai.GenerativeModel(modelName)
                completion = model.generate_content(prompt)
                return completion.text
            else:
                raise ValueError("Invalid model name. Only 'gemini' is supported.")
        except Exception as e:
            log.error(f"Gemini API error: {e}")
            raise Exception("Gemini API error")

class AWS:
 
    def __init__(self):
        # Placeholder for AWS LLM initialization
        self.url = os.getenv('AWS_KEY_ADMIN_PATH')
        self.aws_service_name= os.getenv("AWS_SERVICE_NAME")
        self.region_name = os.getenv("REGION_NAME")
        self.model_id = os.getenv("AWS_MODEL_ID")
        self.accept = os.getenv("ACCEPT")
        self.contentType = os.getenv("CONTENTTYPE")
        self.anthropic_version = os.getenv("ANTHROPIC_VERSION")
        if not all([self.url, self.aws_service_name,self.region_name,self.model_id, self.accept,self.contentType, self.anthropic_version]):
            raise Exception("AWS environment variables are not properly set")
 
    def call_AWS(self, prompt):
        """Get chat completion from AWS LLM"""
        try:
            url = self.url
            response_admin = requests.get(url,verify=False)
            if response_admin.status_code == 200:
                expiration_time = int(response_admin.json()['expirationTime'].split("hrs")[0])
                creation_time = datetime.strptime(response_admin.json()['creationTime'], "%Y-%m-%dT%H:%M:%S.%f")
                if AWS.is_time_difference_12_hours(self,creation_time, expiration_time):
                    aws_access_key_id=response_admin.json()['awsAccessKeyId']
                    aws_secret_access_key=response_admin.json()['awsSecretAccessKey']
                    aws_session_token=response_admin.json()['awsSessionToken']
                    log.info("AWS Creds retrieved !!!")
                    aws_service_name = self.aws_service_name
                    region_name=self.region_name
                    model_id=self.model_id
                    accept=self.accept
                    contentType=self.contentType
                    anthropic_version=self.anthropic_version
                    native_request = {
                        "anthropic_version": anthropic_version,
                        "max_tokens": 512,
                        "temperature": 0.1,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    }

                    request = json.dumps(native_request)
                    client = boto3.client(
                        service_name=self.aws_service_name,
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        aws_session_token=aws_session_token,
                        region_name=self.region_name,
                        verify=False
                    )
                    response = client.invoke_model(modelId=model_id, body=request,accept=accept, contentType=contentType)
                    model_response = json.loads(response["body"].read())
                    llm_resp = model_response["content"][0]["text"] if len(model_response["content"][0]["text"])!=0 else model_response["stop_reason"]
                else:
                    log.info("session expired, please enter the credentials again")
                    llm_resp = "Response cannot be generated at this moment. Reason : (ExpiredTokenException) AWS Credentials included in the request is expired. Solution : Please update with new credentials and try again."
                return llm_resp
        except Exception as e:
            log.error(f"AWS chat completion error: {e}")
            raise e

    def is_time_difference_12_hours(self, creation_time, expiration_time):
        """
        Checks if the time difference between current time and creation time is 12 hours.
 
        Args:
            creation_time (datetime.datetime): The time the item was created.
            expiration_time (int): The expiration time in hours.
 
        Returns:
            bool: True if the time difference is 12 hours, False otherwise.
        """
        time_difference = datetime.now() - creation_time
        log.info(f"time diff : {time_difference}")
        log.info(f"time diff total hours : {time_difference.total_seconds() / 3600}")
 
        # Check if difference is exactly 12 hours, accounting for minutes and seconds
        return (time_difference.total_seconds() / 3600) < expiration_time

class Perplexity:
    def __init__(self):
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY") 
        self.perplexity_model = os.getenv("PERPLEXITY_MODEL") 
        self.perplexity_url = os.getenv("PERPLEXITY_URL")
        
    def get_perplexity(self, prompt):
        try:
            payload = {
                "model": self.perplexity_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Be precise and concise."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.2,
                "top_p": 0.9,
                "return_images": False,
                "return_related_questions": False,
                "search_recency_filter": "month",
                "top_k": 0,
                "stream": False,
                "presence_penalty": 0,
                "frequency_penalty": 1
            }
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }

            response = requests.request("POST", self.perplexity_url, json=payload, headers=headers, verify=False).json()
            
            # Extracting the content from the response
            content = response['choices'][0]['message']['content']

            return content
        except Exception as e:
            log.error(f"Perplexity API error: {e}")
            raise Exception("Perplexity API error")

    

        
        

    
