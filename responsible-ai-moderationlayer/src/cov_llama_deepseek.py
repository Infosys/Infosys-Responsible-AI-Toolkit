'''
Copyright 2024 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
import openai
import os
import time
import traceback
import requests
from config.logger import CustomLogger
from utilities.utility_methods import *
import Llama_auth
log = CustomLogger()
contentType = os.getenv("CONTENTTYPE")
aicloud_access_token=None
token_expiration=0

verify_ssl = os.getenv("VERIFY_SSL")
sslv={"False":False,"True":True,"None":True}

class COV:
    def call_model_endpoint(prompt,temperature,model_name):
        try:
            endpoint=""
            output_text=""
            input_payload={}
            if model_name == "Llama":
                endpoint = os.environ.get("LLAMA_ENDPOINT")
                input_payload = {
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": 512,
                            "temperature":temperature,
                            "num_return_sequences": 1,
                            "do_sample": True
                        }
                }
                response = requests.post(endpoint, json=input_payload, verify=sslv[verify_ssl])
                response.raise_for_status()
                generated_text = response.json()[0]["generated_text"]
                output_text = generated_text.split("[/INST]")[1]
            
            elif model_name == "DeepSeek":
                endpoint = os.getenv("DEEPSEEK_COMPLETION_URL")
                deepseek_model = os.getenv("DEEPSEEK_COMPLETION_MODEL_NAME")
                global aicloud_access_token , token_expiration , contentType
                if aicloud_access_token==None or time.time()>token_expiration:
                    aicloud_access_token,token_expiration=aicloud_auth_token_generate(aicloud_access_token,token_expiration)
                
                input_payload = {
                    "model":deepseek_model,
                    "prompt":prompt,
                    "temperature": 0.01,
                    "top_p": 0.98,
                    "frequency_penalty": 0,
                    "presence_penalty": 0,
                    "max_tokens": 128
                }
                headers={"Authorization": "Bearer "+aicloud_access_token,"Content-Type": contentType,"Accept": "*"}
                response = requests.post(endpoint, json=input_payload,headers=headers,verify=sslv[verify_ssl])
                response.raise_for_status()
                response = json.loads(response.text)['choices'][0]['text']
                output_text = response.replace("\n</think>\n\n","") if "\n</think>\n\n" in response else response
            
            elif model_name == "Llama3-70b":
                endpoint = os.environ.get("LLAMA_ENDPOINT3_70b")
                token = Llama_auth.load_token()
                if isinstance(token, Exception):
                    log.error("Failed to fetch aicloud access token") 
                    raise Exception("Failed to fetch aicloud access token")
                else:
                    log.info("Access token retrived")   
                
                headers={
                "Authorization": "Bearer "+str(token),
                "Content-Type": "application/json",
                "Accept": "*",
                "X-Cluster": "H100"
                }
                messages = [{"role": "user", "content": f"{prompt}"}]
                input = {
                "model":"/models/Meta-Llama-3.3-70B-Instruct",
                "messages": messages,
                "temperature": temperature,
                "top_p": 0.8,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "max_tokens": 500,
                "stop": "null"
                }
                response = requests.post(endpoint, json=input,headers=headers,verify=sslv[verify_ssl])
                response.raise_for_status()
                response = response.json()['choices'][0]['message']['content']
                output_text = response.replace("\n</think>\n\n","") if "\n</think>\n\n" in response else response
            
            return output_text
        except Exception as e:
            log.error("Exception in call_model_endpoint :",e)
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

    def cov(text,complexity,model_name):
        try:
            retries = 0
            max_retries = 10
            while retries < max_retries:
                st=time.time()
                original_question = text

                BASELINE_PROMPT_LONG = f"""[INST]Answer the below question correctly. Do not give options.
                                    Question: {original_question}
                                    Answer:[/INST]"""

                baseline_response = COV.call_model_endpoint(BASELINE_PROMPT_LONG,0.7,model_name)
                log.info(f"baseline response : {baseline_response}")

                if complexity=="simple":
                    VERIFICATION_QUESTION_PROMPT_LONG_simple = f"""[INST]Your task is to create verification questions based on the below original question and the baseline response and the question should be very simple. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should only be a numbered list of verification questions.Always come up with 5 to the point questions. Do not give options.
                                Actual Question: {original_question}
                                Baseline Response: {baseline_response}
                                Final Verification Questions:[/INST]"""
                    verification_question = COV.call_model_endpoint(VERIFICATION_QUESTION_PROMPT_LONG_simple,0.7,model_name)
                    log.info(f"verification_question :{verification_question}")

                elif complexity=="medium":
                    VERIFICATION_QUESTION_PROMPT_LONG_medium = f"""[INST]Your task is to create verification questions based on the below original question and the baseline response and the question should be moderate neither complex nor simple. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should only be a numbered list of verification questions. Always come up with 5 to the point questions. Do not give options.
                            Actual Question: {original_question}
                            Baseline Response: {baseline_response}
                            Final Verification Questions:[/INST]"""
                    verification_question = COV.call_model_endpoint(VERIFICATION_QUESTION_PROMPT_LONG_medium,0.7,model_name)
                    log.info(f"verification_question :{verification_question}")

                elif complexity=="complex":           
                    VERIFICATION_QUESTION_PROMPT_LONG_complex = f"""[INST]Your task is to create verification questions based on the below original question and the baseline response and the question should be more complex not a simple question. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should only be a numbered list of verification questions.Always come up with 5 to the point questions. Do not give options.
                                Actual Question: {original_question}
                                Baseline Response: {baseline_response}
                                Final Verification Questions:[/INST]"""
                    verification_question = COV.call_model_endpoint(VERIFICATION_QUESTION_PROMPT_LONG_complex,0.7,model_name)
                    log.info(f"verification_question :{verification_question}")

                questions = [qt for qt in verification_question.split("\n") if qt[0].isnumeric()]
                
                verification_answers=[]
                for q in questions:
                    EXECUTE_PLAN_PROMPT_SELF_LLM = f"""[INST]Answer the following question correctly to the point. Be succinct.
                                Question: {q}
                                Answer:[/INST]"""
                    ans = COV.call_model_endpoint(EXECUTE_PLAN_PROMPT_SELF_LLM,0.1,model_name)
                    verification_answers.append(ans)

                verification_qustion_answers_pair = ''
                for q,a in zip(questions,verification_answers):
                    verification_qustion_answers_pair = verification_qustion_answers_pair + 'Question. '+q
                    verification_qustion_answers_pair = verification_qustion_answers_pair + 'Answer. '+a+"\n\n"
                log.info(f"verification q/a pairs : {verification_qustion_answers_pair}")

                FINAL_REFINED_PROMPT = f"""[INST]Given the below `Original Query` and `Baseline Answer`, analyze the `Verification Questions & Answers` to finally filter the refined answer. Be succinct.
                            Original Query: {original_question}
                            Baseline Answer: {baseline_response}
                            Verification Questions & Answer Pairs:
                            {verification_qustion_answers_pair}
                            Final Refined Answer:[/INST]"""

                final_answer = COV.call_model_endpoint(FINAL_REFINED_PROMPT,0.7,model_name)

                response = {}
                response["original_question"] = original_question
                response["baseline_response"] = baseline_response
                response["verification_question"] = verification_question
                response["verification_answers"] = verification_qustion_answers_pair
                response["final_answer"] = final_answer
                response["timetaken"]=round(time.time()-st,3)
                return response

        except openai.RateLimitError as RL:

            retries += 1
            if(retries > max_retries):
                return "Rate Limit Error" 
            wait_time = 2 ** retries  # Exponential backoff
            log.error(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)      

        except openai.BadRequestError as BRE:
            log.error(f"Exception: {BRE}")
            log.error("Invalid Request Error")
            return str(BRE)
        except Exception as e:
            log.error("Error occured in cov")
            log.error(f"Exception: {e}")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
