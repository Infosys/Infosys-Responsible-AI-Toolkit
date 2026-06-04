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

import os
import openai
from llm.config.logger import CustomLogger
import time
from openai import AzureOpenAI
import traceback
import json
log = CustomLogger()

class Openaicompletions:
    def __init__(self):
        self.deployment_name=os.getenv("OPENAI_MODEL_GPT4")
        self.deployment_name=os.getenv("OPENAI_MODEL_GPT4")
        self.openai_api_type = os.getenv("OPENAI_API_TYPE")
        self.openai_api_base = os.getenv("OPENAI_API_BASE_GPT4")
        self.openai_api_key = os.getenv("OPENAI_API_KEY_GPT4")
        self.openai_api_version = os.getenv("OPENAI_API_VERSION_GPT4")

    def textCompletion(self,payload):
        try:
            if payload.model == "gpt3":
                self.deployment_name = os.getenv("OPENAI_MODEL_GPT3")
                self.openai_api_base = os.getenv("OPENAI_API_BASE_GPT3")
                self.openai_api_key = os.getenv("OPENAI_API_KEY_GPT3")
                self.openai_api_version = os.getenv("OPENAI_API_VERSION_GPT3")
            if payload.model=="gpt4O":
                self.openai_api_key = os.getenv('OPENAI_API_KEY_GPT4_O')
                self.openai_api_base =  os.getenv('OPENAI_API_BASE_GPT4_O')            
                self.openai_api_version = os.getenv('OPENAI_API_VERSION_GPT4_O')
                self.deployment_name = os.getenv("OPENAI_MODEL_GPT4_O")

            openai.api_key = self.openai_api_key
            openai.api_base = self.openai_api_base
            openai.api_type = self.openai_api_type
            openai.api_version = self.openai_api_version
            openai.verify_ssl_certs = False

            log.info(f"Interaction with GPT ")
            st = time.time()
            messages = json.loads(payload.messages) 
            max_tokens=float(payload.max_tokens) if 'max_tokens' in payload else 1000
            top_p=float(payload.top_p) if 'top_p' in payload else 0.95
            frequency_penalty=float(payload.frequency_penalty) if 'frequency_penalty' in payload else 0
            presence_penalty=float(payload.presence_penalty) if 'presence_penalty' in payload else 0
            stop=payload.stop if 'stop' in payload else None

            client = AzureOpenAI(api_key=openai.api_key, 
                                 azure_endpoint=openai.api_base,
                                 api_version=openai.api_version)
            
            retries = 0
            max_retries = 10
            while retries < max_retries:
                try:
                    response = client.chat.completions.create(
                        model=self.deployment_name,
                        messages = messages ,
                        temperature=float(payload.temperature),
                        max_tokens=max_tokens,
                        top_p=top_p,
                        frequency_penalty=frequency_penalty,
                        presence_penalty=presence_penalty,
                        stop=stop
                        )            
                    et= time.time()
                    rt = et - st
                    log.info(f'Run time with openAI:{rt}')

                    if len(response.choices[0].message.content)!=0:
                        text = response.choices[0].message.content
                        index = response.choices[0].index
                        finish_reason= response.choices[0].finish_reason

                    else:
                        text = response.choices[0].finish_reason
                        index = response.choices[0].index
                        finish_reason = response.choices[0].finish_reason
                    res={"text":text,"index":index,"finish_reason":finish_reason}
                    return res 
                
                except openai.RateLimitError as e:
                    retries += 1
                    if(retries > max_retries):
                        return "Rate Limit Error"
                    wait_time = 2 ** retries  # Exponential backoff
                    print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)   
                
        except openai.BadRequestError as IR:
            log.error(f"Exception: {IR}")
            log.error("Invalid Request Error")
            log.error(f"Exception: {str(traceback.extract_tb(IR.__traceback__)[0].lineno),IR}")
            return str(IR),0,str(IR)
        except Exception as e:
            log.error("Failed at Openai model call")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            return "",0,"No response from Openai"
