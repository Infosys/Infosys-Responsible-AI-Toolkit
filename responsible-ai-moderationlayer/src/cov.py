'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.chat_models import AzureChatOpenAI
import openai
import os
import time
from config.logger import CustomLogger
log = CustomLogger()

# deployment_name = os.getenv("OPENAI_MODEL_GPT4")
class Cov:
    def cov(text,complexity, model_name):
        try:
            if model_name == "gpt3":
                deployment_name = os.getenv("OPENAI_MODEL_GPT3")
                azure_endpoint = os.environ.get("OPENAI_API_BASE_GPT3")
                openai_api_key = os.environ.get("OPENAI_API_KEY_GPT3")
                openai_api_version = os.environ.get("OPENAI_API_VERSION_GPT3")
            else:
                deployment_name = os.getenv("OPENAI_MODEL_GPT4")
                azure_endpoint = os.environ.get("OPENAI_API_BASE_GPT4")
                openai_api_key = os.environ.get("OPENAI_API_KEY_GPT4")
                openai_api_version = os.environ.get("OPENAI_API_VERSION_GPT4")

            # print("deployment_name in cov is ",deployment_name)

            openai_api_type = os.environ.get("OPENAI_API_TYPE")
            
        except Exception as e:
            log.error(f"Exception: {e}")
            
        try:
            llm_1 = AzureChatOpenAI(model=deployment_name,openai_api_version=openai_api_version,openai_api_key=openai_api_key,azure_endpoint=azure_endpoint,openai_api_type ='azure',temperature = 0)
            llm_2 = AzureChatOpenAI(model=deployment_name, openai_api_version=openai_api_version, openai_api_key=openai_api_key, azure_endpoint=azure_endpoint,openai_api_type ='azure',temperature = 0.7)
            llm_3 = AzureChatOpenAI(model=deployment_name, openai_api_version=openai_api_version, openai_api_key=openai_api_key, azure_endpoint=azure_endpoint,openai_api_type ='azure',temperature = 2)

        # except openai.InvalidRequestError as IR:
        #     # log.error(f"Exception: {IR}")
        #     return str(IR)
        
        except Exception as e:
            log.error(f"Exception: {e}")
            
        BASELINE_PROMPT_LONG = """Answer the below question correctly.
                            Question: {original_question}
                            Answer:"""
        # BASELINE_PROMPT_LONG = """Answer the below question correctly. Assistant is a large language model trained by OpenAI.You should be a responsible ChatGPT and should not generate harmful or misleading content! Please answer the following user query in a responsible way.
        #                     Always give response in a textual format dont give in json or any code format. Remember, you are a responsible ChatGPT and good at avoiding generating harmful or misleading content!
        #                     Question: {original_question}
        #                     Answer:"""
        # # messages =[
        #                     {"role": "system", "content": "Assistant is a large language model trained by OpenAI.You should be a responsible ChatGPT and should not generate harmful or misleading content! Please answer the following user query in a responsible way."},
        #                     {"role": "system","content": "Always give response in a textual format dont give in json or any code format"},
        #                     {"role": "user", "content":  f"{text} \n Remember, you are a responsible ChatGPT and good at avoiding generating harmful or misleading content!" }
        #                 ]

        VERIFICATION_QUESTION_PROMPT_LONG = """Your task is to create verification questions based on the below original question and the baseline response. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should be numbered list of verification questions.Always come up with 5 questions.
                    Actual Question: {original_question}
                    Baseline Response: {baseline_response}
                    Final Verification Questions:"""

        VERIFICATION_QUESTION_PROMPT_LONG_simple = """Your task is to create verification questions based on the below original question and the baseline response and the question should be very simple. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should be numbered list of verification questions.Always come up with 5 questions.
                    Actual Question: {original_question}
                    Baseline Response: {baseline_response}
                    Final Verification Questions:"""

        VERIFICATION_QUESTION_PROMPT_LONG_medium = """Your task is to create verification questions based on the below original question and the baseline response and the question should be moderate neither complex nor simple. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should be numbered list of verification questions.
                    Actual Question: {original_question}
                    Baseline Response: {baseline_response}
                    Final Verification Questions:"""

        VERIFICATION_QUESTION_PROMPT_LONG_complex = """Your task is to create verification questions based on the below original question and the baseline response and the question should be more complex not a simple question. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should be numbered list of verification questions.Always come up with 5 questions.
                    Actual Question: {original_question}
                    Baseline Response: {baseline_response}
                    Final Verification Questions:"""

        EXECUTE_PLAN_PROMPT_SELF_LLM = """Answer the following question correctly.
                    Question: {verification_question}
                    Answer:"""

        FINAL_REFINED_PROMPT = """Given the below `Original Query` and `Baseline Answer`, analyze the `Verification Questions & Answers` to finally filter the refined answer.
                    Original Query: {original_question}
                    Baseline Answer: {baseline_response}
                    Verification Questions & Answer Pairs:
                    {verification_answers}
                    Final Refined Answer:"""

        # Chain to generate initial answer
        try:
            baseline_response_prompt_template_long = PromptTemplate.from_template(BASELINE_PROMPT_LONG)
            baseline_response_chain_11 = baseline_response_prompt_template_long | llm_1 | StrOutputParser()
            baseline_response_chain_12 = baseline_response_prompt_template_long | llm_2 | StrOutputParser()
            # baseline_response_chain_13 = baseline_response_prompt_template_long | llm_3 | StrOutputParser()
        
        # except openai.InvalidRequestError as IR:
        #     # log.error(f"Exception: {IR}")
        #     return str(IR)
        
        except Exception as e:
            log.error("Error occured in Chain to generate initial answer")
            log.error(f"Exception: {e}")


        # Chain to generate the verification questionts
        try:
            verification_question_generation_prompt_template_long = PromptTemplate.from_template(VERIFICATION_QUESTION_PROMPT_LONG)
            verification_question_generation_chain_12 = verification_question_generation_prompt_template_long | llm_2 | StrOutputParser()
            # verification_question_generation_chain_13 = verification_question_generation_prompt_template_long | llm_3 | StrOutputParser()
        
        # except openai.InvalidRequestError as IR:
        #     # log.error(f"Exception: {IR}")
        #     return str(IR)
        
        except Exception as e:
            log.error("Error occured in Chain to generate the verification questionts")
            log.error(f"Exception: {e}")

        # Chain to generate the verification questionts for simple complexity
        try:
            verification_question_generation_prompt_template_long_simple = PromptTemplate.from_template(VERIFICATION_QUESTION_PROMPT_LONG_simple)
            verification_question_generation_chain_12_simple = verification_question_generation_prompt_template_long_simple | llm_2 | StrOutputParser()
            # verification_question_generation_chain_13 = verification_question_generation_prompt_template_long_simple | llm_3 | StrOutputParser()
        
        # except openai.InvalidRequestError as IR:
        #     # log.error(f"Exception: {IR}")
        #     return str(IR)
        
        except Exception as e:
            log.error("Error occured in Chain to generate the verification questionts")
            log.error(f"Exception: {e}")    

        # Chain to generate the verification questionts for medium complexity
        try:
            verification_question_generation_prompt_template_long_medium = PromptTemplate.from_template(VERIFICATION_QUESTION_PROMPT_LONG_medium)
            verification_question_generation_chain_12_medium = verification_question_generation_prompt_template_long_medium | llm_2 | StrOutputParser()
            # verification_question_generation_chain_13 = verification_question_generation_prompt_template_long_simple | llm_3 | StrOutputParser()
        
        # except openai.InvalidRequestError as IR:
        #     # log.error(f"Exception: {IR}")
        #     return str(IR)
        
        except Exception as e:
            log.error("Error occured in Chain to generate the verification questionts")
            log.error(f"Exception: {e}")  

        # Chain to generate the verification questionts for complex complexity
        try:
            verification_question_generation_prompt_template_long_complex = PromptTemplate.from_template(VERIFICATION_QUESTION_PROMPT_LONG_complex)
            verification_question_generation_chain_12_complex = verification_question_generation_prompt_template_long_complex | llm_2 | StrOutputParser()
            # verification_question_generation_chain_13 = verification_question_generation_prompt_template_long_simple | llm_3 | StrOutputParser()
        
        # except openai.InvalidRequestError as IR:
        #     # log.error(f"Exception: {IR}")
        #     return str(IR)
        
        except Exception as e:
            log.error("Error occured in Chain to generate the verification questionts")
            log.error(f"Exception: {e}")

        # Chain to execute the verification
        try:
            execution_prompt_self_llm_long = PromptTemplate.from_template(EXECUTE_PLAN_PROMPT_SELF_LLM)
            execution_prompt_llm_chain_11 = execution_prompt_self_llm_long | llm_1 | StrOutputParser()
            # execution_prompt_llm_chain_12 = execution_prompt_self_llm_long | llm_2 | StrOutputParser()
            execution_prompt_llm_chain_13 = execution_prompt_self_llm_long | llm_3 | StrOutputParser()
        
        # except openai.InvalidRequestError as IR:
        #     # log.error(f"Exception: {IR}")
        #     return str(IR)
        
        except Exception as e:
            log.error("Error occured in Chain to execute the verification")
            log.error(f"Exception: {e}")

        try:
            verification_chain_11 = RunnablePassthrough.assign(
                split_questions=lambda x: x['verification_questions'].split("\n"),
            ) | RunnablePassthrough.assign(
                answers = (lambda x: [{"verification_question": q} for q in x['split_questions']])| execution_prompt_llm_chain_11.map()
            ) | (lambda x: "\n".join(["Question: {} Answer: {}\n".format(question, answer) for question, answer in zip(x['split_questions'], x['answers'])]))# Create final refined response
        
        # except openai.InvalidRequestError as IR:
        #     # log.error(f"Exception: {IR}")
        #     return str(IR)
        
        except Exception as e:
            log.error(f"Exception: {e}")

        # verification_chain_12 = RunnablePassthrough.assign(
        #     split_questions=lambda x: x['verification_questions'].split("\n"),
        # ) | RunnablePassthrough.assign(
        #     answers = (lambda x: [{"verification_question": q} for q in x['split_questions']])| execution_prompt_llm_chain_12.map()
        # ) | (lambda x: "\n".join(["Question: {} Answer: {}\n".format(question, answer) for question, answer in zip(x['split_questions'], x['answers'])]))# Create final refined response

        # verification_chain_13 = RunnablePassthrough.assign(
        #     split_questions=lambda x: x['verification_questions'].split("\n"),
        # ) | RunnablePassthrough.assign(
        #     answers = (lambda x: [{"verification_question": q} for q in x['split_questions']])| execution_prompt_llm_chain_13.map()
        # ) | (lambda x: "\n".join(["Question: {} Answer: {}\n".format(question, answer) for question, answer in zip(x['split_questions'], x['answers'])]))# Create final refined response


        # Chain to generate the final answer
        try:
            final_answer_prompt_template_long = PromptTemplate.from_template(FINAL_REFINED_PROMPT)
            # final_answer_chain_11 = final_answer_prompt_template_long | llm_1 | StrOutputParser()
            final_answer_chain_12 = final_answer_prompt_template_long | llm_2 | StrOutputParser()
            # final_answer_chain_13 = final_answer_prompt_template_long | llm_3 | StrOutputParser()
        # except openai.InvalidRequestError as IR:
        #     # log.error(f"Exception: {IR}")
        #     return str(IR)
        except Exception as e:
            log.error("Error occured in Chain to generate the final answer")
            log.error(f"Exception: {e}")



        # chain_long_1 = RunnablePassthrough.assign(
        #     baseline_response=baseline_response_chain_11
        # ) | RunnablePassthrough.assign(
        #     verification_questions=verification_question_generation_chain_11
        # ) | RunnablePassthrough.assign(
        #     verification_answers=verification_chain_11
        # ) | RunnablePassthrough.assign(
        #     final_answer=final_answer_chain_11
        # )

        chain_long_2 = RunnablePassthrough.assign(
            baseline_response=baseline_response_chain_12
        ) | RunnablePassthrough.assign(
            verification_questions=verification_question_generation_chain_12
        ) | RunnablePassthrough.assign(
            verification_answers=verification_chain_11
        ) | RunnablePassthrough.assign(
            final_answer=final_answer_chain_12
        )

        chain_long_2_simple = RunnablePassthrough.assign(
            baseline_response=baseline_response_chain_12
        ) | RunnablePassthrough.assign(
            verification_questions=verification_question_generation_chain_12_simple
        ) | RunnablePassthrough.assign(
            verification_answers=verification_chain_11
        ) | RunnablePassthrough.assign(
            final_answer=final_answer_chain_12
        )


        chain_long_2_medium = RunnablePassthrough.assign(
            baseline_response=baseline_response_chain_12
        ) | RunnablePassthrough.assign(
            verification_questions=verification_question_generation_chain_12_medium
        ) | RunnablePassthrough.assign(
            verification_answers=verification_chain_11
        ) | RunnablePassthrough.assign(
            final_answer=final_answer_chain_12
        )

        chain_long_2_complex = RunnablePassthrough.assign(
            baseline_response=baseline_response_chain_12
        ) | RunnablePassthrough.assign(
            verification_questions=verification_question_generation_chain_12_complex
        ) | RunnablePassthrough.assign(
            verification_answers=verification_chain_11
        ) | RunnablePassthrough.assign(
            final_answer=final_answer_chain_12
        )
        
        
        retries = 0
        max_retries = 10
        while retries < max_retries:
            try:
                st=time.time()
                if complexity=="simple":
                    response = chain_long_2_simple.invoke({f"original_question":{text}})
                elif complexity=="medium":
                    response = chain_long_2_medium.invoke({f"original_question":{text}})
                elif complexity=="complex":
                    response = chain_long_2_complex.invoke({f"original_question":{text}})
                response["timetaken"]=round(time.time()-st,3)
                
                return response
            except openai.RateLimitError as RL:
                
                retries += 1
                if(retries > max_retries):
                    return "Rate Limit Error" 
                wait_time = 2 ** retries  # Exponential backoff
                print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)      
               
                # print("Rate Limit Error")
                # log.error(f"Exception: {RL}")                
                # return "Rate Limit Error"
            except openai.BadRequestError as BRE:
                log.error(f"Exception: {BRE}")
                print("Invalid Request Error")
                return str(BRE)
            except Exception as e:
                log.error("Error occured in cov")
                log.error(f"Exception: {e}")
