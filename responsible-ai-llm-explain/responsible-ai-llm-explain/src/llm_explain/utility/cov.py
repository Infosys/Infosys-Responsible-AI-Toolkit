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

from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.chat_models import AzureChatOpenAI
from llm_explain.config.logger import CustomLogger
from llm_explain.utility.endpoint import APIEndpoint
from llm_explain.utility.utility import Utils
from json.decoder import JSONDecodeError
import openai
import os
import time
import json

log = CustomLogger()


class Cov:

    @staticmethod
    def llm_response_to_json(response):
        """
        Converts a substring of the given response that is in JSON format into a Python dictionary.
        
        This function searches for the first occurrence of '{' and the last occurrence of '}' to find the JSON substring.
        It then attempts to parse this substring into a Python dictionary. If the parsing is successful, the dictionary
        is returned. If the substring is not valid JSON, the function will return None.
        
        Parameters:
        - response (str): The response string that potentially contains JSON content.
        
        Returns:
        - dict: A dictionary representation of the JSON substring found within the response.
        - None: If no valid JSON substring is found or if an error occurs during parsing.
        """
        try:
            result = None # Initialize result to None in case no valid JSON is found

            # Step 1: Find the start index of the first '{' character and end index of the last '}' character
            start_index = response.find('{')

            if start_index == -1:
                # If '{' is not found, load all content
                result = response
            else:
                # Step 2: Initialize a counter for curly braces
                curly_count = 0

                # Step 3: Find the corresponding closing '}' for the first '{'
                for i in range(start_index, len(response)):
                    if response[i] == '{':
                        curly_count += 1
                    elif response[i] == '}':
                        curly_count -= 1
                    
                    # When curly_count reaches 0, we have matched the opening '{' with the closing '}'
                    if curly_count == 0:
                        end_index = i
                        break
                json_content = response[start_index:end_index+1] # Extract the substring that is potentially in JSON format
                result = json.loads(json_content) # Attempt to parse the JSON substring into a Python dictionary
            
            return result
        
        except Exception as e:
            # Log the exception if any error occurs during parsing
            log.error(f"An error occurred while parsing JSON from response: {e}", exc_info=True)
            raise ValueError("An error occurred while parsing JSON from response.")

    import os
import time
import json
import openai
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.chat_models import AzureChatOpenAI

from llm_explain.config.logger import CustomLogger
from llm_explain.utility.utility import Utils

log = CustomLogger()

class Cov:

    @staticmethod
    def gemini_generate(prompt, api_key, model_name="gemini-2.5-pro-exp-03-25", max_retries=5):
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)

        retries = 0
        while retries < max_retries:
            try:
                response = model.generate_content(prompt)
                return response.text
            except ResourceExhausted as e:
                wait_time = 2 ** retries
                log.error(f"Gemini quota exhausted, retrying in {wait_time}s...")
                time.sleep(wait_time)
                retries += 1
            except Exception as e:
                log.error(f"Exception calling Gemini API: {e}")
                raise
        raise RuntimeError("Max retries exceeded for Gemini API")

    @staticmethod
    def cov_gpt(text, complexity, model_name):
        try:
            # Load env/config depending on model
            if model_name == "gpt3":
                deployment_name = os.getenv("AZURE_DEPLOYMENT_ENGINE")
                azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
                openai_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
                openai_api_version = os.environ.get("AZURE_OPENAI_API_VERSION")
            elif model_name.lower() == "gemini-pro":
                gemini_api_key = os.getenv("GEMINI_API_KEY")
                gemini_model_name = os.getenv("GEMINI_MODEL_NAME_PRO")
            elif model_name.lower() == "gemini-flash":
                gemini_api_key = os.getenv("GEMINI_API_KEY")
                gemini_model_name = os.getenv("GEMINI_MODEL_NAME_FLASH")
            else:
                # default fallback to Azure GPT3 setup
                deployment_name = os.getenv("AZURE_DEPLOYMENT_ENGINE")
                azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
                openai_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
                openai_api_version = os.environ.get("AZURE_OPENAI_API_VERSION")

            # Gemini flow
            if model_name.lower() == "gemini-pro" or model_name.lower() == "gemini-flash":
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel(gemini_model_name)
                
                retries = 0
                max_retries = 10
                
                while retries < max_retries:
                    try:
                        st = time.time()

                        # Step 1: Baseline response
                        baseline_prompt = f"Answer the below question correctly.\nQuestion: {text}\nAnswer:"
                        baseline_response = model.generate_content(baseline_prompt).text

                        # Step 2: Verification questions based on complexity
                        if complexity == "simple":
                            verification_prompt = (
                                f"Your task is to create verification questions based on the below original question "
                                f"and the baseline response and the question should be very simple. The verification questions "
                                f"are meant for verifying the factual accuracy in the baseline response. Output should be numbered list of verification questions. "
                                f"Always come up with 5 questions.\nActual Question: {text}\nBaseline Response: {baseline_response}\nFinal Verification Questions:"
                            )
                        elif complexity == "medium":
                            verification_prompt = (
                                f"Your task is to create verification questions based on the below original question "
                                f"and the baseline response and the question should be moderate neither complex nor simple. The verification questions "
                                f"are meant for verifying the factual accuracy in the baseline response. Output should be numbered list of verification questions.\n"
                                f"Actual Question: {text}\nBaseline Response: {baseline_response}\nFinal Verification Questions:"
                            )
                        elif complexity == "complex":
                            verification_prompt = (
                                f"Your task is to create verification questions based on the below original question "
                                f"and the baseline response and the question should be more complex not a simple question. The verification questions "
                                f"are meant for verifying the factual accuracy in the baseline response. Output should be numbered list of verification questions. "
                                f"Always come up with 5 questions.\nActual Question: {text}\nBaseline Response: {baseline_response}\nFinal Verification Questions:"
                            )
                        else:
                            verification_prompt = (
                                f"Your task is to create verification questions based on the below original question "
                                f"and the baseline response. The verification questions are meant for verifying the factual accuracy in the baseline response. Output should be numbered list of verification questions.\n"
                                f"Actual Question: {text}\nBaseline Response: {baseline_response}\nFinal Verification Questions:"
                            )
                        
                        verification_questions = model.generate_content(verification_prompt).text

                        # Step 3: Generate answers for verification questions
                        execution_prompt = f"Answer the following questions correctly.\nQuestions: {verification_questions}\nAnswer:"
                        verification_answers = model.generate_content(execution_prompt).text

                        # Step 4: Generate final refined answer
                        final_refined_prompt = (
                            f"Given the below Original Query and Baseline Answer, analyze the Verification Questions & Answers "
                            f"to finally filter the refined answer.\nOriginal Query: {text}\nBaseline Answer: {baseline_response}\n"
                            f"Verification Questions & Answer Pairs:\n{verification_questions}\n{verification_answers}\nFinal Refined Answer:"
                        )
                        final_refined_answer = model.generate_content(final_refined_prompt).text

                        elapsed = round(time.time() - st, 3)

                        return {
                            "original_question": text,
                            "baseline_response": baseline_response,
                            "verification_questions": verification_questions,
                            "verification_answers": verification_answers,
                            "final_answer": final_refined_answer,
                            "time_taken": elapsed,
                            "token_cost": None  # Gemini does not provide token cost directly,
                        }

                    except ResourceExhausted:
                        retries += 1
                        if retries > max_retries:
                            return "Gemini API Quota exhausted after retries"
                        wait_time = 2 ** retries
                        time.sleep(wait_time)
                    except Exception as e:
                        log.error(f"Gemini exception: {e}")
                        return str(e)

            # Azure GPT3 flow
            else:
                try:
                    llm_1 = AzureChatOpenAI(
                        deployment_name=deployment_name,
                        openai_api_version=openai_api_version,
                        openai_api_key=openai_api_key,
                        azure_endpoint=azure_endpoint,
                        openai_api_type='azure',
                        temperature=0
                    )
                    llm_2 = AzureChatOpenAI(
                        deployment_name=deployment_name,
                        openai_api_version=openai_api_version,
                        openai_api_key=openai_api_key,
                        azure_endpoint=azure_endpoint,
                        openai_api_type='azure',
                        temperature=0.7
                    )
                    llm_3 = AzureChatOpenAI(
                        deployment_name=deployment_name,
                        openai_api_version=openai_api_version,
                        openai_api_key=openai_api_key,
                        azure_endpoint=azure_endpoint,
                        openai_api_type='azure',
                        temperature=2
                    )
                    Cov.modelFlag = True
                except Exception as e:
                    log.error(f"Exception during Azure LLM initialization: {e}")
                    return str(e)

                # Define prompt templates
                BASELINE_PROMPT_LONG = """Answer the below question correctly.
                Question: {original_question}
                Answer:"""

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

                EXECUTE_PLAN_PROMPT_SELF_LLM = """Answer the following questions correctly.
                Questions: {verification_question}
                Answer:"""

                FINAL_REFINED_PROMPT = """Given the below Original Query and Baseline Answer, analyze the Verification Questions & Answers to finally filter the refined answer.
                Original Query: {original_question}
                Baseline Answer: {baseline_response}
                Verification Questions & Answer Pairs:
                {verification_answers}
                Final Refined Answer:"""

                # Prepare chains
                try:
                    baseline_response_prompt_template_long = PromptTemplate.from_template(BASELINE_PROMPT_LONG)
                    baseline_response_chain_12 = baseline_response_prompt_template_long | llm_2 | StrOutputParser()
                except Exception as e:
                    log.error("Error in baseline response chain")
                    log.error(f"Exception: {e}")
                    return str(e)

                try:
                    verification_question_generation_prompt_template_long_simple = PromptTemplate.from_template(VERIFICATION_QUESTION_PROMPT_LONG_simple)
                    verification_question_generation_chain_12_simple = verification_question_generation_prompt_template_long_simple | llm_2 | StrOutputParser()
                except Exception as e:
                    log.error("Error in verification question chain simple")
                    log.error(f"Exception: {e}")
                    return str(e)

                try:
                    verification_question_generation_prompt_template_long_medium = PromptTemplate.from_template(VERIFICATION_QUESTION_PROMPT_LONG_medium)
                    verification_question_generation_chain_12_medium = verification_question_generation_prompt_template_long_medium | llm_2 | StrOutputParser()
                except Exception as e:
                    log.error("Error in verification question chain medium")
                    log.error(f"Exception: {e}")
                    return str(e)

                try:
                    verification_question_generation_prompt_template_long_complex = PromptTemplate.from_template(VERIFICATION_QUESTION_PROMPT_LONG_complex)
                    verification_question_generation_chain_12_complex = verification_question_generation_prompt_template_long_complex | llm_2 | StrOutputParser()
                except Exception as e:
                    log.error("Error in verification question chain complex")
                    log.error(f"Exception: {e}")
                    return str(e)

                try:
                    execution_prompt_self_llm_long = PromptTemplate.from_template(EXECUTE_PLAN_PROMPT_SELF_LLM)
                    execution_prompt_llm_chain_11 = execution_prompt_self_llm_long | llm_1 | StrOutputParser()
                except Exception as e:
                    log.error("Error in execution chain")
                    log.error(f"Exception: {e}")
                    return str(e)

                try:
                    verification_chain_11 = RunnablePassthrough.assign(
                        split_questions=lambda x: x['verification_questions'].split("\n"),
                    ) | RunnablePassthrough.assign(
                        answers=(lambda x: [{"verification_question": q} for q in x['split_questions']]) | execution_prompt_llm_chain_11.map()
                    ) | (lambda x: "\n".join(
                        ["Question: {} Answer: {}\n".format(question, answer) for question, answer in zip(x['split_questions'], x['answers'])]
                    ))
                except Exception as e:
                    log.error(f"Exception in verification chain: {e}")
                    return str(e)

                try:
                    final_answer_prompt_template_long = PromptTemplate.from_template(FINAL_REFINED_PROMPT)
                    final_answer_chain_12 = final_answer_prompt_template_long | llm_2 | StrOutputParser()
                except Exception as e:
                    log.error("Error in final answer chain")
                    log.error(f"Exception: {e}")
                    return str(e)

                chain_long_2_simple = RunnablePassthrough.assign(
                    baseline_response=baseline_response_chain_12 if not isinstance(baseline_response_chain_12, str) else lambda x: baseline_response_chain_12
                ) | RunnablePassthrough.assign(
                    verification_questions=verification_question_generation_chain_12_simple if not isinstance(verification_question_generation_chain_12_simple, str) else lambda x: verification_question_generation_chain_12_simple
                ) | RunnablePassthrough.assign(
                    verification_answers=verification_chain_11 if not isinstance(verification_chain_11, str) else lambda x: verification_chain_11
                ) | RunnablePassthrough.assign(
                    final_answer=final_answer_chain_12 if not isinstance(final_answer_chain_12, str) else lambda x: final_answer_chain_12
                )

                chain_long_2_medium = RunnablePassthrough.assign(
                    baseline_response=baseline_response_chain_12 if not isinstance(baseline_response_chain_12, str) else lambda x: baseline_response_chain_12
                ) | RunnablePassthrough.assign(
                    verification_questions=verification_question_generation_chain_12_medium if not isinstance(verification_question_generation_chain_12_medium, str) else lambda x: verification_question_generation_chain_12_medium
                ) | RunnablePassthrough.assign(
                    verification_answers=verification_chain_11 if not isinstance(verification_chain_11, str) else lambda x: verification_chain_11
                ) | RunnablePassthrough.assign(
                    final_answer=final_answer_chain_12 if not isinstance(final_answer_chain_12, str) else lambda x: final_answer_chain_12
                )

                chain_long_2_complex = RunnablePassthrough.assign(
                    baseline_response=baseline_response_chain_12 if not isinstance(baseline_response_chain_12, str) else lambda x: baseline_response_chain_12
                ) | RunnablePassthrough.assign(
                    verification_questions=verification_question_generation_chain_12_complex if not isinstance(verification_question_generation_chain_12_complex, str) else lambda x: verification_question_generation_chain_12_complex
                ) | RunnablePassthrough.assign(
                    verification_answers=verification_chain_11 if not isinstance(verification_chain_11, str) else lambda x: verification_chain_11
                ) | RunnablePassthrough.assign(
                    final_answer=final_answer_chain_12 if not isinstance(final_answer_chain_12, str) else lambda x: final_answer_chain_12
                )

                retries = 0
                max_retries = 10
                while retries < max_retries:
                    try:
                        st = time.time()
                        if complexity == "simple":
                            response = chain_long_2_simple.invoke({"original_question": text})
                        elif complexity == "medium":
                            response = chain_long_2_medium.invoke({"original_question": text})
                        elif complexity == "complex":
                            response = chain_long_2_complex.invoke({"original_question": text})
                        else:
                            # Default to simple if unknown
                            response = chain_long_2_simple.invoke({"original_question": text})

                        input_tokens = Utils.calculate_token_count(text)
                        output_tokens = Utils.calculate_token_count(str(response))
                        token_cost = Utils.get_token_cost(input_tokens, output_tokens, model_name.lower())

                        response["time_taken"] = round(time.time() - st, 3)
                        response["token_cost"] = token_cost

                        return response
                    except openai.RateLimitError as RL:
                        retries += 1
                        if retries > max_retries:
                            return "Rate Limit Error"
                        wait_time = 2 ** retries
                        time.sleep(wait_time)
                    except openai.BadRequestError as BRE:
                        log.error(f"BadRequestError: {BRE}")
                        return str(BRE)
                    except Exception as e:
                        log.error("Error occured in cov")
                        log.error(f"Exception: {e}")
                        return str(e)

        except Exception as e:
            log.error(f"Exception in cov_gpt outer: {e}")
            return str(e)


    # def cov_gpt(text,complexity, model_name):
    #     try:
    #         if model_name == "gpt3":
    #             deployment_name = os.getenv("AZURE_DEPLOYMENT_ENGINE")
    #             azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    #             openai_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    #             openai_api_version = os.environ.get("AZURE_OPENAI_API_VERSION")
    #         elif model_name == "gemini":
    #             gemini_api_key = os.getenv("GEMINI_API_KEY")
    #             gemini_model_name = os.getenv("GEMINI_MODEL_NAME")

    #         else:
    #             deployment_name = os.getenv("AZURE_DEPLOYMENT_ENGINE")
    #             azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    #             openai_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    #             openai_api_version = os.environ.get("AZURE_OPENAI_API_VERSION")
                
        
    #         openai_api_type = os.environ.get("OPENAI_API_TYPE", "azure")
    #         try:
                
    #             llm_1 = AzureChatOpenAI(deployment_name=deployment_name,openai_api_version=openai_api_version,openai_api_key=openai_api_key,azure_endpoint=azure_endpoint,openai_api_type ='azure',temperature = 0)
    #             llm_2 = AzureChatOpenAI(deployment_name=deployment_name, openai_api_version=openai_api_version, openai_api_key=openai_api_key, azure_endpoint=azure_endpoint,openai_api_type ='azure',temperature = 0.7)
    #             llm_3 = AzureChatOpenAI(deployment_name=deployment_name, openai_api_version=openai_api_version, openai_api_key=openai_api_key, azure_endpoint=azure_endpoint,openai_api_type ='azure',temperature = 2)
    #             Cov.modelFlag = True
                
                    

            
    #         except Exception as e:
    #             log.error(f"Exception: {e}")

    #     except Exception as e:
    #         log.error(f"Exception: {e}")
            
    #     BASELINE_PROMPT_LONG = """Answer the below question correctly.
    #                         Question: {original_question}
    #                         Answer:"""

    #     VERIFICATION_QUESTION_PROMPT_LONG = """Your task is to create verification questions based on the below original question and the baseline response. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should be numbered list of verification questions.Always come up with 5 questions.
    #                 Actual Question: {original_question}
    #                 Baseline Response: {baseline_response}
    #                 Final Verification Questions:"""

    #     VERIFICATION_QUESTION_PROMPT_LONG_simple = """Your task is to create verification questions based on the below original question and the baseline response and the question should be very simple. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should be numbered list of verification questions.Always come up with 5 questions.
    #                 Actual Question: {original_question}
    #                 Baseline Response: {baseline_response}
    #                 Final Verification Questions:"""

    #     VERIFICATION_QUESTION_PROMPT_LONG_medium = """Your task is to create verification questions based on the below original question and the baseline response and the question should be moderate neither complex nor simple. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should be numbered list of verification questions.
    #                 Actual Question: {original_question}
    #                 Baseline Response: {baseline_response}
    #                 Final Verification Questions:"""

    #     VERIFICATION_QUESTION_PROMPT_LONG_complex = """Your task is to create verification questions based on the below original question and the baseline response and the question should be more complex not a simple question. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should be numbered list of verification questions.Always come up with 5 questions.
    #                 Actual Question: {original_question}
    #                 Baseline Response: {baseline_response}
    #                 Final Verification Questions:"""

    #     EXECUTE_PLAN_PROMPT_SELF_LLM = """Answer the following questions correctly.
    #                 Questions: {verification_question}
    #                 Answer:"""

    #     FINAL_REFINED_PROMPT = """Given the below `Original Query` and `Baseline Answer`, analyze the `Verification Questions & Answers` to finally filter the refined answer.
    #                 Original Query: {original_question}
    #                 Baseline Answer: {baseline_response}
    #                 Verification Questions & Answer Pairs:
    #                 {verification_answers}
    #                 Final Refined Answer:"""

    #     # # Chain to generate initial answer
    #     try:
    #         baseline_response_prompt_template_long = PromptTemplate.from_template(BASELINE_PROMPT_LONG)
    #         baseline_response_chain_12 = baseline_response_prompt_template_long | llm_2 | StrOutputParser()

    #     except Exception as e:
    #         log.error("Error occured in Chain to generate initial answer")
    #         log.error(f"Exception: {e}")


    #     # Chain to generate the verification questionts
    #     try:
    #         verification_question_generation_prompt_template_long = PromptTemplate.from_template(VERIFICATION_QUESTION_PROMPT_LONG)
    #         verification_question_generation_chain_12 = verification_question_generation_prompt_template_long | llm_2 | StrOutputParser()
        
    #     except Exception as e:
    #         log.error("Error occured in Chain to generate the verification questionts")
    #         log.error(f"Exception: {e}")

    #     # Chain to generate the verification questionts for simple complexity
    #     try:
    #         verification_question_generation_prompt_template_long_simple = PromptTemplate.from_template(VERIFICATION_QUESTION_PROMPT_LONG_simple)
    #         verification_question_generation_chain_12_simple = verification_question_generation_prompt_template_long_simple | llm_2 | StrOutputParser()
                
    #     except Exception as e:
    #         log.error("Error occured in Chain to generate the verification questionts")
    #         log.error(f"Exception: {e}")    

    #     # # Chain to generate the verification questionts for medium complexity
    #     try:

    #         verification_question_generation_prompt_template_long_medium = PromptTemplate.from_template(VERIFICATION_QUESTION_PROMPT_LONG_medium)
    #         verification_question_generation_chain_12_medium = verification_question_generation_prompt_template_long_medium | llm_2 | StrOutputParser()
               
    #     except Exception as e:
    #         log.error("Error occured in Chain to generate the verification questionts")
    #         log.error(f"Exception: {e}")  

    #     # # Chain to generate the verification questionts for complex complexity
    #     try:

    #         verification_question_generation_prompt_template_long_complex = PromptTemplate.from_template(VERIFICATION_QUESTION_PROMPT_LONG_complex)
    #         verification_question_generation_chain_12_complex = verification_question_generation_prompt_template_long_complex | llm_2 | StrOutputParser()

    #     except Exception as e:
    #         log.error("Error occured in Chain to generate the verification questionts")
    #         log.error(f"Exception: {e}")

    #     # Chain to execute the verification
    #     try:
    #         execution_prompt_self_llm_long = PromptTemplate.from_template(EXECUTE_PLAN_PROMPT_SELF_LLM)
    #         execution_prompt_llm_chain_11 = execution_prompt_self_llm_long | llm_1 | StrOutputParser()
       
    #     except Exception as e:
    #         log.error("Error occured in Chain to execute the verification")
    #         log.error(f"Exception: {e}")

    #     try:
      
    #         verification_chain_11 = RunnablePassthrough.assign(
    #             split_questions=lambda x: x['verification_questions'].split("\n"),
    #         ) | RunnablePassthrough.assign(
    #             answers = (lambda x: [{"verification_question": q} for q in x['split_questions']])| execution_prompt_llm_chain_11.map()
    #         ) | (lambda x: "\n".join(["Question: {} Answer: {}\n".format(question, answer) for question, answer in zip(x['split_questions'], x['answers'])]))# Create final refined response
        
    #     except Exception as e:
    #         log.error(f"Exception: {e}")

    #     # # Chain to generate the final answer
    #     try:
        
    #         final_answer_prompt_template_long = PromptTemplate.from_template(FINAL_REFINED_PROMPT)
    #         final_answer_chain_12 = final_answer_prompt_template_long | llm_2 | StrOutputParser()
       
    #     except Exception as e:
    #         log.error("Error occured in Chain to generate the final answer")
    #         log.error(f"Exception: {e}")

    #     chain_long_2_simple = RunnablePassthrough.assign(
    #         baseline_response=baseline_response_chain_12 if not isinstance(baseline_response_chain_12, str) else lambda x: baseline_response_chain_12
    #     ) | RunnablePassthrough.assign(
    #         verification_questions=verification_question_generation_chain_12_simple if not isinstance(verification_question_generation_chain_12_simple, str) else lambda x: verification_question_generation_chain_12_simple
    #     ) | RunnablePassthrough.assign(
    #         verification_answers=verification_chain_11 if not isinstance(verification_chain_11, str) else lambda x: verification_chain_11
    #     ) | RunnablePassthrough.assign(
    #         final_answer=final_answer_chain_12 if not isinstance(final_answer_chain_12, str) else lambda x: final_answer_chain_12
    #     )


    #     chain_long_2_medium = RunnablePassthrough.assign(
    #         baseline_response=baseline_response_chain_12 if not isinstance(baseline_response_chain_12, str) else lambda x: baseline_response_chain_12
    #     ) | RunnablePassthrough.assign(
    #         verification_questions=verification_question_generation_chain_12_medium if not isinstance(verification_question_generation_chain_12_medium, str) else lambda x: verification_question_generation_chain_12_medium
    #     ) | RunnablePassthrough.assign(
    #         verification_answers=verification_chain_11 if not isinstance(verification_chain_11, str) else lambda x: verification_chain_11
    #     ) | RunnablePassthrough.assign(
    #         final_answer=final_answer_chain_12 if not isinstance(final_answer_chain_12, str) else lambda x: final_answer_chain_12
    #     )

    #     chain_long_2_complex = RunnablePassthrough.assign(
    #         baseline_response=baseline_response_chain_12 if not isinstance(baseline_response_chain_12, str) else lambda x: baseline_response_chain_12
    #     ) | RunnablePassthrough.assign(
    #         verification_questions=verification_question_generation_chain_12_complex if not isinstance(verification_question_generation_chain_12_complex, str) else lambda x: verification_question_generation_chain_12_complex
    #     ) | RunnablePassthrough.assign(
    #         verification_answers=verification_chain_11 if not isinstance(verification_chain_11, str) else lambda x: verification_chain_11
    #     ) | RunnablePassthrough.assign(
    #         final_answer=final_answer_chain_12 if not isinstance(final_answer_chain_12, str) else lambda x: final_answer_chain_12
    #     )
        
        
    #     retries = 0
    #     max_retries = 10
    #     while retries < max_retries:
    #         try:
    #             st=time.time()
    #             if complexity=="simple":
    #                 response = chain_long_2_simple.invoke({f"original_question":{text}})
    #             elif complexity=="medium":
    #                 response = chain_long_2_medium.invoke({f"original_question":{text}})
    #             elif complexity=="complex":
    #                 response = chain_long_2_complex.invoke({f"original_question":{text}})

    #             input_tokens = Utils.calculate_token_count(text)
    #             output_tokens = Utils.calculate_token_count(str(response))
    #             token_cost = Utils.get_token_cost(input_tokens, output_tokens, model_name.lower())
                    
    #             response["time_taken"]=round(time.time()-st,3)
    #             response["token_cost"] = token_cost
                
    #             return response
    #         except openai.RateLimitError as RL:
                
    #             retries += 1
    #             if(retries > max_retries):
    #                 return "Rate Limit Error" 
    #             wait_time = 2 ** retries  # Exponential backoff
    #             time.sleep(wait_time)      
               
    #         except openai.BadRequestError as BRE:
    #             log.error(f"Exception: {BRE}")
    #             return str(BRE)
    #         except Exception as e:
    #             log.error("Error occured in cov")
    #             log.error(f"Exception: {e}")

    def cov_endpoint(text,complexity, modelEndpointUrl = None, endpointInputParam = None, endpointOutputParam = None):
        try:
            retries = 0
            max_retries = 10
            while retries < max_retries:
                st=time.time()
                original_question = text
                # Chain to generate initial answer
                try:
                    BASELINE_PROMPT_LONG1 = f"""Answer the following question correctly and concisely in one single line. Do not provide any explanations, clarifications, or extra information. Only provide the direct answer with no additional text. Return the output only in the following JSON format. Do not include anything else in your response. Ensure that only one JSON object is returned:{{"Answer": "answer to the question"}}Question: {original_question}Answer:"""
                    response =  APIEndpoint.endpoint_calling(BASELINE_PROMPT_LONG1, modelEndpointUrl, endpointInputParam, endpointOutputParam).strip('`')
                    explanation = Cov.llm_response_to_json(response.replace("\n", " "))
                    baseline_response = explanation["Answer"]

                except Exception as e:
                    log.error("Error occured in Chain to generate initial answer")
                    log.error(f"Exception: {e}")

                # Chain to generate the verification questionts for simple complexity
                try:

                    if complexity=="simple":
                        VERIFICATION_QUESTION_PROMPT_LONG = f"""Your task is to create 5 simple non-repeatable verification questions to cross verify the original question and baseline response. The questions should be easy to understand and designed to verify the factual accuracy of the baseline response. Make sure the generated questions are unique and related to verification of baseline response to the original question. Do not provide any explanations or additional information. Only return a numbered list of 5 questions. Return the output only in the following JSON format. Do not include anything else in your response. Ensure that only one JSON object is returned:{{"Final Verification Questions": "return a numbered list of 5 questions with comma separated"}}Actual Question: {original_question}Baseline Response: {baseline_response}Final Verification Questions:"""
                    elif complexity=="medium":
                        VERIFICATION_QUESTION_PROMPT_LONG = f"""Your task is to create 5 non repeatable verification questions to cross verify the original question and baseline response. The questions should be moderate in complexity, neither too simple nor too complex. The questions are meant to verify the factual accuracy of the baseline response. Make sure the generated questions are unique and related to verification of baseline response to the original question. Do not provide any explanations or additional information. Only return a numbered list of 5 questions. Return the output only in the following JSON format. Do not include anything else in your response. Ensure that only one JSON object is returned:{{"Final Verification Questions": "retrun a numbered list of 5 questions with comma separated"}}Actual Question: {original_question}Baseline Response: {baseline_response}Final Verification Questions:"""
                    elif complexity=="complex":
                        VERIFICATION_QUESTION_PROMPT_LONG = f"""Your task is to create 5 complex non repeatable verification questions to cross verify the original question and baseline response. The questions should be more complex and not simple. The questions are meant to verify the factual accuracy of the baseline response. Make sure the generated questions are unique and related to verification of baseline response to the original question. Do not provide any explanations or additional information. Only return a numbered list of 5 questions. Return the output only in the following JSON format. Do not include anything else in your response. Ensure that only one JSON object is returned:{{"Final Verification Questions": "retrun a numbered list of 5 questions with comma separated"}}Actual Question: {original_question}Baseline Response: {baseline_response}Final Verification Questions:"""
                    verification_response = APIEndpoint.endpoint_calling(VERIFICATION_QUESTION_PROMPT_LONG, modelEndpointUrl, endpointInputParam, endpointOutputParam).strip('`')
                    explanation = Cov.llm_response_to_json(verification_response.replace("\n", " "))
                    if "Final Verification Questions" in explanation:
                        verification_question_generation = explanation["Final Verification Questions"]
                    else:
                        verification_question_generation = explanation
                except Exception as e:
                    log.error("Error occured in Chain to generate the verification questionts")
                    log.error(f"Exception: {e}")    
               
                # Chain to execute the verification
                try:
                    verification_questions = verification_question_generation
                    EXECUTE_PLAN_PROMPT_SELF_LLM1 = f"""Give precise answers to the following questions. Do not repeat the questions again in response. Be succinct. Do not include anything else in your response. Ensure that only one JSON object is returned: Return the output only in the following JSON format.{{"Answers": "Answers to the verification questions with comma separated"}}Questions: {verification_questions}Answers:"""
                    ver_ans_response = APIEndpoint.endpoint_calling(EXECUTE_PLAN_PROMPT_SELF_LLM1, modelEndpointUrl, endpointInputParam, endpointOutputParam).strip('`')
                    explanation = Cov.llm_response_to_json(ver_ans_response.replace("\n", " "))
                    if "Answers" in explanation:
                        execution_prompt_llm_chain_11 = explanation["Answers"]
                    else:
                        execution_prompt_llm_chain_11 = explanation
                    
                except Exception as e:
                    log.error("Error occured in Chain to execute the verification")
                    log.error(f"Exception: {e}")

                # Chain to generate the final answer
                try:
                    # Split the questions and answers
                    split_questions = verification_question_generation.split(", ")
                    answers = execution_prompt_llm_chain_11.split(", ")

                    # Create the final refined response
                    final_response = "\n".join([
                        "Question: {} Answer: {}\n".format(question.strip(), answer.strip()) 
                        for question, answer in zip(split_questions, answers)
                    ])

                    verification_questions_answers = final_response
                    FINAL_REFINED_PROMPT = f"""Given the below 'Original Question' and 'Baseline Answer', analyze the 'Verification Questions & Answer Pairs' to finally filter the refined answer. Do not repeat the response for multiple times. Return the output only in the following JSON format. Do not include anything else in your response. Ensure that only one JSON object is returned:{{"Final Refined Answer": "Final Refined Answer"}}Original Question: {original_question}Baseline Answer: {baseline_response}Verification Questions & Answer Pairs: {verification_questions_answers}Final Refined Answer:"""
                    final_refined_response = APIEndpoint.endpoint_calling(FINAL_REFINED_PROMPT, modelEndpointUrl, endpointInputParam, endpointOutputParam).strip('`')
                    explanation = Cov.llm_response_to_json(final_refined_response)
                    if isinstance(explanation, dict) and "Final Refined Answer" in explanation:
                        final_answer_chain_12 = explanation["Final Refined Answer"]
                    else:
                        final_answer_chain_12 = explanation.split('\n')[0]

                except Exception as e:
                    log.error("Error occured in Chain to generate the final answer")
                    log.error(f"Exception: {e}")

                response = {}
                response['original_question'] = text
                response['baseline_response'] = baseline_response
                response['verification_questions'] = verification_question_generation
                response['verification_answers'] = execution_prompt_llm_chain_11
                response['final_answer'] = final_answer_chain_12          
                response["time_taken"]= round(time.time()-st,3)
                response["token_cost"] = None
    
                return response
            
        except JSONDecodeError:
            retries += 1
            if retries == max_retries:
                raise Exception("Failed to decode JSON after 5 attempts.")
            else:
                log.debug(f"JSONDecodeError encountered. Retrying... Attempt {retries}/{max_retries}")
                # Add a delay before the next attempt
                time.sleep(2) # Delay for 2 seconds
                
        except openai.RateLimitError as RL:
            
            retries += 1
            if(retries > max_retries):
                return "Rate Limit Error" 
            wait_time = 2 ** retries  # Exponential backoff
            time.sleep(wait_time)      
            
        except openai.BadRequestError as BRE:
            log.error(f"Exception: {BRE}")
            return str(BRE)
        except Exception as e:
            log.error("Error occured in cov")
            log.error(f"Exception: {e}")
