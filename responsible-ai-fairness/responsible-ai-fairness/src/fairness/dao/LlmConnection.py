import os
import json
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAI
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import requests
import logging
from mimetypes import guess_type
from io import BytesIO
from PIL import Image
import boto3
from langchain_aws import ChatBedrock
from datetime import datetime
from fairness.service.service_utils import Utils
import base64
import io

load_dotenv()

log = logging.getLogger(__name__)
utils=Utils()

class BaseLLM(ABC):
    """Abstract base class for LLM implementations"""

    @abstractmethod
    def get_chat_completion(self, prompt_template: str, text: str, **kwargs) -> str:
        """Get chat completion from the LLM"""
        pass

    @abstractmethod
    def get_image_completion(self, prompt_template: str, image_data: str, **kwargs) -> str:
        """Get image completion from the LLM"""
        pass


class Azureopenai(BaseLLM):
    """OpenAI LLM implementation"""

    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.api_type = os.getenv('OPENAI_API_TYPE')
        self.api_base = os.getenv('OPENAI_API_BASE')
        self.api_version = os.getenv('OPENAI_API_VERSION')
        self.engine = os.getenv('OPENAI_ENGINE_NAME')

        if not all([self.api_key, self.api_base, self.engine]):
            raise Exception("OpenAI environment variables are not properly set")

        # Configure OpenAI client based on API type
        if self.api_type.lower() == 'azure':
            # For Azure OpenAI, use AzureOpenAI client
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.api_base  # This should be your Azure endpoint URL
            )
        else:
            # For regular OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base if self.api_base else None
            )

    def get_chat_completion(self, prompt_template: str, text: str, **kwargs) -> str:
        """Get chat completion from OpenAI"""
        try:
            message_text = [
                {
                    "role": "system",
                    "content": prompt_template
                },
                {
                    "role": "user", 
                    "content": text
                }
            ]

            # Default parameters
            params = {
                "model": self.engine,
                "messages": message_text,
                "temperature": kwargs.get('temperature', 0.3),
                "max_tokens": kwargs.get('max_tokens', 800),
                "top_p": kwargs.get('top_p', 0.95),
                "frequency_penalty": kwargs.get('frequency_penalty', 0),
                "presence_penalty": kwargs.get('presence_penalty', 0),
                "stop": kwargs.get('stop', None)
            }

            completion = self.client.chat.completions.create(**params)
            log.info(completion)
            output = completion.choices[0].message.content

        except Exception as e:
            log.error(f"AzureOpenAI chat completion error: {e}")
            raise e

        return output

    def get_image_completion(self, prompt_template: str, image_data: str, **kwargs) -> str:
        """Get image completion from AzureOpenAI (GPT-4V)"""
        try:
            completion = self.client.chat.completions.create(
            model=self.engine,
            messages=[
                { 
                    "role": "system", 
                    "content": "You are a helpful assistant." 
                },
                { 
                    "role": "user", 
                    "content": [  
                        { 
                            "type": "text", 
                            "text": prompt_template
                        },
                        { 
                            "type": "image_url",
                            "image_url": {
                                "url": image_data
                            }
                        }
                    ] 
                } 
            ],
            temperature=kwargs.get('temperature', 0.3),
            max_tokens=kwargs.get('max_tokens', 800),
            top_p=kwargs.get('top_p', 0.95),
            frequency_penalty=kwargs.get('frequency_penalty', 0),
            presence_penalty=kwargs.get('presence_penalty', 0)
        )

            response = completion.choices[0].message.content
            return response

        except Exception as e:
            log.error(f"AzureOpenAI image completion error: {e}")
        raise e


class GeminiFlash(BaseLLM):
    """GeminiFlash LLM implementation"""

    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_name = os.getenv('GEMINI_FLASH_MODEL_NAME')

        if not self.api_key:
            raise Exception("Gemini API key is not set")

        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name=self.model_name)

    def get_chat_completion(self, prompt_template: str, text: str, **kwargs) -> str:
        """Get chat completion from Gemini"""
        try:
            # Create message structure with separate system and user prompts
            system_message = f"System Instructions: {prompt_template}\n\nUser Request:"
            message_text = [
            {
                "role": "user",
                "parts": [system_message + " " + text]
            }
            ]
            # Gemini safety settings
            safety_settings = {
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
            }

            # Generation configuration parameters
            # generation_config = {
            # "temperature": kwargs.get('temperature', 0.3),
            # "max_output_tokens": kwargs.get('max_tokens', 800),
            # "top_p": kwargs.get('top_p', 0.95),
            # "top_k": kwargs.get('top_k', 40),
            # "stop_sequences": kwargs.get('stop', None)
            # }

             # Remove None values from generation_config
            # generation_config = {k: v for k, v in generation_config.items() if v is not None}

            response = self.model.generate_content(
                message_text,
                safety_settings=safety_settings
                # generation_config=generation_config
            )
            # Structure the response similar to Azure OpenAI format
            if response.candidates and len(response.candidates) > 0:
                # Get the first candidate (similar to choices[0] in OpenAI)
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    # Get the text content from the first part
                    output = candidate.content.parts[0].text
                else:
                    output = response.text
            else:
                # Fallback to direct text access
                output = response.text
            # output = response.text

            return output

        except Exception as e:
            log.error(f"Gemini chat completion error: {e}")
            raise e

    def get_image_completion(self, prompt_template: str, image_content, **kwargs) -> str:
        """Get image completion from Gemini Pro Vision"""
        try:
            # Gemini safety settings
            safety_settings = {
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
            }

            response = self.model.generate_content(
                [prompt_template, image_content],
                stream=kwargs.get('stream', True),
                safety_settings=safety_settings
            )

            response.resolve()
            return response.text

        except Exception as e:
            log.error(f"Gemini-flash image completion error: {e}")
            raise e
    
class GeminiPro(BaseLLM):
    """GeminiPro LLM implementation"""

    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_name = os.getenv('GEMINI_PRO_MODEL_NAME')

        if not self.api_key:
            raise Exception("Gemini API key is not set")

        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name=self.model_name)

    def get_chat_completion(self, prompt_template: str, text: str, **kwargs) -> str:
        """Get chat completion from Gemini"""
        try:
            # Create message structure with separate system and user prompts
            system_message = f"System Instructions: {prompt_template}\n\nUser Request:"
            message_text = [
            {
                "role": "user",
                "parts": [system_message + " " + text]
            }
            ]
            # Gemini safety settings
            safety_settings = {
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
            }

            # Generation configuration parameters
            # generation_config = {
            # "temperature": kwargs.get('temperature', 0.3),
            # "max_output_tokens": kwargs.get('max_tokens', 800),
            # "top_p": kwargs.get('top_p', 0.95),
            # "top_k": kwargs.get('top_k', 40),
            # "stop_sequences": kwargs.get('stop', None)
            # }

             # Remove None values from generation_config
            # generation_config = {k: v for k, v in generation_config.items() if v is not None}

            response = self.model.generate_content(
                message_text,
                safety_settings=safety_settings
                # generation_config=generation_config
            )
            # Structure the response similar to Azure OpenAI format
            if response.candidates and len(response.candidates) > 0:
                # Get the first candidate (similar to choices[0] in OpenAI)
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    # Get the text content from the first part
                    output = candidate.content.parts[0].text
                else:
                    output = response.text
            else:
                # Fallback to direct text access
                output = response.text
            # output = response.text

            return output

        except Exception as e:
            log.error(f"Gemini-Pro chat completion error: {e}")
            raise e

    def get_image_completion(self, prompt_template: str, image_content, **kwargs) -> str:
        """Get image completion from Gemini Pro Vision"""
        try:
            # Gemini safety settings
            safety_settings = {
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
            }

            response = self.model.generate_content(
                [prompt_template, image_content],
                stream=kwargs.get('stream', True),
                safety_settings=safety_settings
            )

            response.resolve()
            return response.text

        except Exception as e:
            log.error(f"Gemini image completion error: {e}")
            raise e

class AWS(BaseLLM):
    """AWS LLM implementation"""
    ssl_verify = os.getenv('VERIFY_SSL').strip()
    verify = False if ssl_verify == "False" else True
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

    def get_chat_completion(self, prompt_template: str, text: str, **kwargs) -> str:
        """Get chat completion from AWS LLM"""
        try:
            url = self.url
            response_admin = requests.get(url,verify=AWS.verify)
            if response_admin.status_code == 200:
                expiration_time = int(response_admin.json()['expirationTime'].split("hrs")[0])
                creation_time = datetime.strptime(response_admin.json()['creationTime'], "%Y-%m-%dT%H:%M:%S.%f")
                if utils.is_time_difference_12_hours(creation_time, expiration_time):
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
                                "content": prompt_template + " " + text
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
                        verify=AWS.verify
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

    def get_image_completion(self, prompt_template: str, image_data, **kwargs) -> str:
        """Get image completion from AWS LLM"""
        try:
            url = self.url
            response_admin = requests.get(url, verify=AWS.verify)
            if response_admin.status_code == 200:
                expiration_time = int(response_admin.json()['expirationTime'].split("hrs")[0])
                creation_time = datetime.strptime(response_admin.json()['creationTime'], "%Y-%m-%dT%H:%M:%S.%f")
                if utils.is_time_difference_12_hours(creation_time, expiration_time):
                    aws_access_key_id = response_admin.json()['awsAccessKeyId']
                    aws_secret_access_key = response_admin.json()['awsSecretAccessKey']
                    aws_session_token = response_admin.json()['awsSessionToken']
                    log.info("AWS Creds retrieved !!!")

                    # Extract base64 data and media type from data URL
                    # image_data format: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
                    media_type = image_data.split(';')[0].split(':')[1]
                    base64_data = image_data.split(',')[1]

                    aws_service_name = self.aws_service_name
                    region_name = self.region_name
                    model_id = self.model_id
                    accept = self.accept
                    contentType = self.contentType
                    anthropic_version = self.anthropic_version

                    native_request = {
                        "anthropic_version": anthropic_version,
                        "max_tokens": 512,
                        "temperature": 0.1,
                        "messages": [
                            {
                                "role": "user", 
                                "content": [
                                    {
                                        "type": "text",
                                        "text": prompt_template
                                    },
                                    {
                                        "type": "image",
                                        "source": {
                                            "type": "base64",
                                            "media_type": media_type,
                                            "data": base64_data
                                        }
                                    }
                                ]
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
                    response = client.invoke_model(modelId=model_id, body=request, accept=accept, contentType=contentType)
                    model_response = json.loads(response["body"].read())
                    llm_resp = model_response["content"][0]["text"] if len(model_response["content"][0]["text"]) != 0 else model_response["stop_reason"]
                else:
                    log.info("session expired, please enter the credentials again")
                    llm_resp = "Response cannot be generated at this moment. Reason : (ExpiredTokenException) AWS Credentials included in the request is expired. Solution : Please update with new credentials and try again."
                return llm_resp
        except Exception as e:
            log.error(f"AWS image completion error: {e}")
            raise e

class LLMConnection:
    """Factory class to create LLM connections based on active_llm environment variable"""

    def __init__(self):
        self.active_llm = os.getenv('ACTIVE_LLM').lower()
        self.llm_instance = self._create_llm_instance()

    def _create_llm_instance(self) -> BaseLLM:
        """Create LLM instance based on active_llm setting"""
        if self.active_llm == 'azureopenai':
            return Azureopenai()
        elif self.active_llm == 'gemini-2.5-flash':
            return GeminiFlash()
        elif self.active_llm == 'gemini-2.5-pro':
            return GeminiPro()
        elif self.active_llm == 'aws':
            return AWS()
        else:
            raise Exception(f"Invalid ACTIVE_LLM value: {self.active_llm}. Expected 'azureopenai', 'gemini-2.5-flash', 'gemini-2.5-pro','aws'.")

    def get_chat_completion(self, prompt_template, text):
        """Get chat completion using the active LLM"""
        return self.llm_instance.get_chat_completion(prompt_template, text)

    def get_image_completion(self, prompt_template, image_data, **kwargs):
        """Get image completion using the active LLM"""
        return self.llm_instance.get_image_completion(prompt_template, image_data, **kwargs)

    def get_active_llm(self) -> str:
        """Get the name of the currently active LLM"""
        return self.active_llm

# Factory function for easy usage
def create_llm_connection() -> LLMConnection:
    """Factory function to create LLM connection"""
    return LLMConnection()