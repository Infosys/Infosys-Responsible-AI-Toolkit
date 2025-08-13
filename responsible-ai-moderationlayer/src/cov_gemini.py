'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import os
import time
import traceback
from config.logger import CustomLogger
from utilities.utility_methods import *
import google.generativeai as genai

log = CustomLogger()
temp={"simple":0,"medium":0.7,"complex":2}

verify_ssl = os.getenv("VERIFY_SSL")
sslv={"False":False,"True":True,"None":True}

class CovGemini:
    def call_Gemini(prompt,temperature,model_name):
        try:
            if model_name == 'Gemini-Pro':
                log.info("Response using Gemini-Pro")
                gemini_api_key = os.getenv("GEMINI_PRO_API_KEY")
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel(os.getenv("GEMINI_PRO_MODEL_NAME"))
            elif model_name == 'Gemini-Flash':
                log.info("Response using Gemini-Flash")
                gemini_api_key = os.getenv("GEMINI_FLASH_API_KEY")
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel(os.getenv("GEMINI_FLASH_MODEL_NAME"))
            generation_config = genai.types.GenerationConfig(temperature=temperature)
            response = model.generate_content(prompt,generation_config=generation_config)

            if response.candidates and response.candidates[0].content.parts:            
                text = response.candidates[0].content.parts[0].text.strip()
                log.info(f"Gemini response : {text}")

            return 0,text
        except Exception as e:
                log.error("Exception in calling Gemini model")
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

                if complexity=="simple":
                    expiration_flag,baseline_response = CovGemini.call_Gemini(BASELINE_PROMPT_LONG,temp["simple"],model_name)
                    if expiration_flag==-1:
                        return baseline_response
                    log.info(f"baseline_response : {baseline_response}")
                    VERIFICATION_QUESTION_PROMPT_LONG_simple = f"""[INST]Your task is to create verification questions based on the below original question and the baseline response and the question should be very simple. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should be numbered list of verification questions.Always come up with 5 to the point questions. Do not give options.
                                Actual Question: {original_question}
                                Baseline Response: {baseline_response}
                                Final Verification Questions:[/INST]"""
                    expiration_flag,verification_question = CovGemini.call_Gemini(VERIFICATION_QUESTION_PROMPT_LONG_simple,temp["simple"],model_name)
                    log.info(f"verification_question : {verification_question}")

                elif complexity=="medium":
                    expiration_flag,baseline_response = CovGemini.call_Gemini,(BASELINE_PROMPT_LONG,temp["medium"],model_name)
                    if expiration_flag==-1:
                        return baseline_response
                    log.info(f"baseline_response : {baseline_response}")
                    VERIFICATION_QUESTION_PROMPT_LONG_medium = f"""[INST]Your task is to create verification questions based on the below original question and the baseline response and the question should be moderate neither complex nor simple. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should be numbered list of verification questions. Always come up with 5 to the point questions. Do not give options.
                            Actual Question: {original_question}
                            Baseline Response: {baseline_response}
                            Final Verification Questions:[/INST]"""
                    expiration_flag,verification_question = CovGemini.call_Gemini(VERIFICATION_QUESTION_PROMPT_LONG_medium,temp["medium"],model_name)
                    log.info(f"verification_question : {verification_question}")

                elif complexity=="complex":
                    expiration_flag,baseline_response = CovGemini.call_Gemini(BASELINE_PROMPT_LONG,temp["complex"],model_name)
                    if expiration_flag==-1:
                        return baseline_response
                    log.info(f"baseline_response : {baseline_response}")
                    VERIFICATION_QUESTION_PROMPT_LONG_complex = f"""[INST]Your task is to create verification questions based on the below original question and the baseline response and the question should be more complex not a simple question. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should be numbered list of verification questions.Always come up with 5 to the point questions. Do not give options.
                                Actual Question: {original_question}
                                Baseline Response: {baseline_response}
                                Final Verification Questions:[/INST]"""
                    expiration_flag,verification_question = CovGemini.call_Gemini(VERIFICATION_QUESTION_PROMPT_LONG_complex,temp["complex"],model_name)
                    log.info(f"verification_question : {verification_question}")

                questions = [qt for qt in verification_question.split("\n") if qt[0].isnumeric()]

                verification_answers=[]
                for q in questions:
                    EXECUTE_PLAN_PROMPT_SELF_LLM = f"""[INST]Answer the following question correctly to the point. Be succinct.
                                Question: {q}
                                Answer:[/INST]"""
                    if complexity=="simple":
                        flag,ans = CovGemini.call_Gemini(EXECUTE_PLAN_PROMPT_SELF_LLM,temp["simple"],model_name)
                    elif complexity=="medium":
                        flag,ans = CovGemini.call_Gemini(EXECUTE_PLAN_PROMPT_SELF_LLM,temp["medium"],model_name)
                    else:
                        flag,ans = CovGemini.call_Gemini(EXECUTE_PLAN_PROMPT_SELF_LLM,temp["complex"],model_name)
                    
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
                    expiration_flag,final_answer = CovGemini.call_Gemini(FINAL_REFINED_PROMPT,temp["simple"],model_name)
                elif complexity=="medium":
                    expiration_flag,final_answer = CovGemini.call_Gemini(FINAL_REFINED_PROMPT,temp["medium"],model_name)
                else:
                    expiration_flag,final_answer = CovGemini.call_Gemini(FINAL_REFINED_PROMPT,temp["complex"],model_name)
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