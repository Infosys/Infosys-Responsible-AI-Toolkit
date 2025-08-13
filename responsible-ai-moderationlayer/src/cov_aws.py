'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import json
import boto3
import os
import time
import traceback
import requests
from config.logger import CustomLogger
from utilities.utility_methods import *
log = CustomLogger()
temp={"simple":0,"medium":0.7,"complex":2}

verify_ssl = os.getenv("VERIFY_SSL")
sslv={"False":False,"True":True,"None":True}

class CovAWS:
    def call_AWS(prompt,temperature):
        url = os.getenv("AWS_KEY_ADMIN_PATH")
        response = requests.get(url,verify=sslv[verify_ssl])
        if response.status_code == 200:
            expiration_time = int(response.json()['expirationTime'].split("hrs")[0])
            creation_time = datetime.strptime(response.json()['creationTime'], "%Y-%m-%dT%H:%M:%S.%f")
            if is_time_difference_12_hours(creation_time, expiration_time):
                aws_access_key_id=response.json()['awsAccessKeyId']
                aws_secret_access_key=response.json()['awsSecretAccessKey']
                aws_session_token=response.json()['awsSessionToken']
                log.info("AWS Creds retrieved !!!")
                
                aws_service_name = os.getenv("AWS_SERVICE_NAME")
                region_name = os.getenv("REGION_NAME")
                model_id=os.getenv("AWS_MODEL_ID")
                accept=os.getenv("ACCEPT")
                contentType=os.getenv("CONTENTTYPE")
                anthropic_version=os.getenv("ANTHROPIC_VERSION")
                native_request = {
                    "anthropic_version": anthropic_version,
                    "max_tokens": 512,
                    "temperature": temperature,
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"type": "text", "text": prompt}],
                        }
                    ],
                }
                request = json.dumps(native_request)
                try:
                    client = boto3.client(
                        service_name=aws_service_name,
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        aws_session_token=aws_session_token,
                        region_name=region_name,
                        verify=sslv[verify_ssl]
                    )
                    response = client.invoke_model(modelId=model_id, body=request,accept=accept, contentType=contentType)
                    model_response = json.loads(response["body"].read())
                    response_text = model_response["content"][0]["text"]
                    log.info(f"output text : {response_text}")
                    return 0,response_text
                except Exception as e:
                    log.error("Exception in calling AWS Claude 3 Sonnet model")
                    log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            else:
                log.info("session expired, please enter the credentials again")
                response_text = """Response cannot be generated at this moment. Reason : (ExpiredTokenException) AWS Credentials included in the request is expired. Solution : Please update with new credentials and try again."""
                return -1,response_text
        else:
           log.info("Error getting data: ",{response.status_code})

        
        
        
            

    def cov(text,complexity):
        try:
            retries = 0
            max_retries = 10
            while retries < max_retries:
                st=time.time()
                original_question = text

                BASELINE_PROMPT_LONG = f"""[INST]Answer the below question correctly. Do not give options.
                                    Question: {original_question}
                                    Answer:[/INST]"""

                if complexity=="simple":
                    expiration_flag,baseline_response = CovAWS.call_AWS(BASELINE_PROMPT_LONG,temp["simple"])
                    if expiration_flag==-1:
                        return baseline_response
                    log.info(f"baseline_response : {baseline_response}")
                    VERIFICATION_QUESTION_PROMPT_LONG_simple = f"""[INST]Your task is to create verification questions based on the below original question and the baseline response and the question should be very simple. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should be numbered list of verification questions.Always come up with 5 to the point questions. Do not give options.
                                Actual Question: {original_question}
                                Baseline Response: {baseline_response}
                                Final Verification Questions:[/INST]"""
                    expiration_flag,verification_question = CovAWS.call_AWS(VERIFICATION_QUESTION_PROMPT_LONG_simple,temp["simple"])
                    log.info(f"verification_question : {verification_question}")

                elif complexity=="medium":
                    expiration_flag,baseline_response = CovAWS.call_AWS(BASELINE_PROMPT_LONG,temp["medium"])
                    if expiration_flag==-1:
                        return baseline_response
                    log.info(f"baseline_response : {baseline_response}")
                    VERIFICATION_QUESTION_PROMPT_LONG_medium = f"""[INST]Your task is to create verification questions based on the below original question and the baseline response and the question should be moderate neither complex nor simple. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should be numbered list of verification questions. Always come up with 5 to the point questions. Do not give options.
                            Actual Question: {original_question}
                            Baseline Response: {baseline_response}
                            Final Verification Questions:[/INST]"""
                    expiration_flag,verification_question = CovAWS.call_AWS(VERIFICATION_QUESTION_PROMPT_LONG_medium,temp["medium"])
                    log.info(f"verification_question : {verification_question}")

                elif complexity=="complex":
                    expiration_flag,baseline_response = CovAWS.call_AWS(BASELINE_PROMPT_LONG,temp["complex"])
                    if expiration_flag==-1:
                        return baseline_response
                    log.info(f"baseline_response : {baseline_response}")
                    VERIFICATION_QUESTION_PROMPT_LONG_complex = f"""[INST]Your task is to create verification questions based on the below original question and the baseline response and the question should be more complex not a simple question. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should be numbered list of verification questions.Always come up with 5 to the point questions. Do not give options.
                                Actual Question: {original_question}
                                Baseline Response: {baseline_response}
                                Final Verification Questions:[/INST]"""
                    expiration_flag,verification_question = CovAWS.call_AWS(VERIFICATION_QUESTION_PROMPT_LONG_complex,temp["complex"])
                    log.info(f"verification_question : {verification_question}")

                questions = [qt for qt in verification_question.split("\n") if qt[0].isnumeric()]

                verification_answers=[]
                for q in questions:
                    EXECUTE_PLAN_PROMPT_SELF_LLM = f"""[INST]Answer the following question correctly to the point. Be succinct.
                                Question: {q}
                                Answer:[/INST]"""
                    if complexity=="simple":
                        flag,ans = CovAWS.call_AWS(EXECUTE_PLAN_PROMPT_SELF_LLM,temp["simple"])
                    elif complexity=="medium":
                        flag,ans = CovAWS.call_AWS(EXECUTE_PLAN_PROMPT_SELF_LLM,temp["medium"])
                    else:
                        flag,ans = CovAWS.call_AWS(EXECUTE_PLAN_PROMPT_SELF_LLM,temp["complex"])
                    
                    verification_answers.append(ans)

                verification_qustion_answers_pair = ''
                for q,a in zip(questions,verification_answers):
                    verification_qustion_answers_pair = verification_qustion_answers_pair + 'Question. '+q
                    verification_qustion_answers_pair = verification_qustion_answers_pair + 'Answer. '+a+"\n\n"
                    
                log.info(f"verification_qustion_answers_pair : {verification_qustion_answers_pair}")
                
                FINAL_REFINED_PROMPT = f"""[INST]Given the below `Original Query` and `Baseline Answer`, analyze the `Verification Questions & Answers` to finally filter the refined answer. Be succinct.
                            Original Query: {original_question}
                            Baseline Answer: {baseline_response}
                            Verification Questions & Answer Pairs:
                            {verification_qustion_answers_pair}
                            Final Refined Answer:[/INST]"""

                if complexity=="simple":
                    expiration_flag,final_answer = CovAWS.call_AWS(FINAL_REFINED_PROMPT,temp["simple"])
                elif complexity=="medium":
                    expiration_flag,final_answer = CovAWS.call_AWS(FINAL_REFINED_PROMPT,temp["medium"])
                else:
                    expiration_flag,final_answer = CovAWS.call_AWS(FINAL_REFINED_PROMPT,temp["complex"])
                log.info(f"final answer : {final_answer}")

                response = {}
                response["original_question"] = original_question
                response["baseline_response"] = baseline_response
                response["verification_question"] = verification_question
                response["verification_answers"] = verification_qustion_answers_pair
                response["final_answer"] = final_answer
                response["timetaken"]=round(time.time()-st,3)
                log.info(f"response from cov : {response}")
                return response
        except Exception as e:
            log.error("Error occured in cov")
            log.error(f"Exception: {e}")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
