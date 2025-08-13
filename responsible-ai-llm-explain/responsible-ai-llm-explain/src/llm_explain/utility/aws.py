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
from llm_explain.utility.utility import Utils
import requests
import os
import re
import json
import boto3

log = CustomLogger()

class AWScompletions:

    def textCompletion(self, text, temperature, model_name, technique):
        if model_name == "Claude-3-Sonnet":
                url = os.getenv("AWS_ADMIN_PATH")
                response = requests.get(url)
                if response.status_code == 200:
                    aws_access_key_id=response.json()['awsAccessKeyId']
                    aws_secret_access_key=response.json()['awsSecretAccessKey']
                    aws_session_token=response.json()['awsSessionToken']
                    log.info("AWS Creds retrieved !!!")
                else:
                    log.info("Error getting data: ",{response.status_code})
                aws_service_name = os.getenv("AWS_SERVICE_NAME")
                region_name=os.getenv("REGION_NAME")
                model_id=os.getenv("AWS_MODEL_ID")
                accept=os.getenv("ACCEPT")
                contentType=os.getenv("CONTENTTYPE")
                anthropic_version=os.getenv("ANTHROPIC_VERSION")

        temperature = 0.1 if temperature==0 else temperature

        native_request = {
            "anthropic_version": anthropic_version,
            "max_tokens": 512,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": text}],
                }
            ],
        }
        if technique =="COT":
            native_request['messages'] =[
                {"role": "user", "content":  f"{text} \n Assistant is a large language model trained by Anthropic.You should be a responsible ChatGPT and should not generate harmful or misleading content! Please answer the following user query in a responsible way. Let's think the answer step by step and explain step by step how you got the answer. Please provide website link as references if you are refering from internet to get the answer.You should be a responsible LLM and should not generate harmful or misleading content! Please answer the following user query in a responsible way. Let's think the answer step by step and explain step by step how you got the answer. Always give response in a textual format dont give in json or any code format.Please provide website link as references if you are refering from internet to get the answer.Remember, you are a responsible LLM and good at avoiding generating harmful or misleading content!" }
            ]
        elif technique=="THOT":
            native_request['messages'] =[
                    {"role": "user", "content":  f"""{text}
                     Assistant is a large language model trained by Anthropic.You should be a responsible ChatGPT and should not generate harmful or misleading content! Please answer the following user query in a responsible way. Walk me through this context in manageable parts step by step, summarising and analysing as we go.Engage in a step-by-step thought process to explain how the answer was derived. Additionally, associate the source with the answer using the format:
                        Result: "answer"
                        Explanation: "step-by-step reasoning"
                     Always give response in a textual format dont give in json or any code format.Remember, you are a responsible ChatGPT and good at avoiding generating harmful or misleading content!""" }
                ]

        request = json.dumps(native_request)
        client = boto3.client(
            service_name=aws_service_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=region_name
        )

        response = client.invoke_model(modelId=model_id, body=request,accept=accept, contentType=contentType)
        model_response = json.loads(response["body"].read())
        response_text = model_response["content"][0]["text"]
        response_text = response_text.replace("Answer: ","") if "Answer: " in response_text else response_text
        stop_reason = model_response["stop_reason"]
        response_text=stop_reason
        return response_text,0,stop_reason