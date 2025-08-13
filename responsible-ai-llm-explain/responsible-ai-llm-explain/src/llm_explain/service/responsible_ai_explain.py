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

from llm_explain.utility import got as GraphOfThoughts
from llm_explain.utility.prompts.base import Prompt
from llm_explain.config.logger import CustomLogger
from llm_explain.utility.utility import Utils
from llm_explain.utility.connections import Azure, Gemini, AWS, Perplexity
from llm_explain.utility.llama import Llamacompletion
from llm_explain.utility.aws import AWScompletions
from llm_explain.utility.endpoint import APIEndpoint
from llm_explain.utility.cov import Cov
from llm_explain.utility.cov_llama import CovLlama
from llm_explain.utility.cov_aws import CovAWS
from llm_explain.utility.translate import Translate
from json.decoder import JSONDecodeError
import pandas as pd
import time
import json
import ast
import os

log = CustomLogger()

class ResponsibleAIExplain:

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
        
    @staticmethod
    def normalize_scores(dict_list):
        try:
            # Calculate the total sum of all importance scores
            total_sum = sum(d['importance_score'] for d in dict_list)
            
            # If the total sum is zero, return the original list (to handle cases where all scores are zero)
            if total_sum == 0:
                return dict_list

            # Normalize the scores to ensure their sum equals 100
            normalized_scores = [round((d['importance_score'] / total_sum) * 100) for d in dict_list]
            
            # Adjust the scores to ensure their sum is exactly 100
            adjustment = 100 - sum(normalized_scores)
            normalized_scores[0] += adjustment

            # Update the original list with normalized scores
            for i, d in enumerate(dict_list):
                d['importance_score'] = normalized_scores[i]
            
            return dict_list
        
        except KeyError as e:
            log.error(f"KeyError: Missing key in one of the dictionaries - {e}")
            raise KeyError(f"KeyError: Missing key in one of the dictionaries - {e}")
        except TypeError as e:
            log.error(f"TypeError: Invalid type encountered - {e}")
            raise TypeError(f"TypeError: Invalid type encountered - {e}")
        except Exception as e:
            log.error(f"An unexpected error occurred: {e}")
            raise
    
    @staticmethod
    def filter_token_importance(scores, anchors):
        import re
        try:
            # Split each phrase in anchors into individual words, remove special characters, and convert to lowercase
            anchors = [re.sub(r'\W+', '', word).lower() for anchor in anchors for word in anchor.split()]
            
            importance_scores = [] # Initialize a list to store the importance scores of the anchors
            for score in scores: # Iterate through the scores list
                cleaned_token = re.sub(r'\W+', '', str(score['token'])).lower()
                if cleaned_token in anchors: # Check if the token value is in the anchors list
                    importance_scores.append(score['importance_score']) # Append the importance score to the list
            
            # Calculate the remaining importance score
            x = 100 - sum(importance_scores) 

            filtered_tokens = []
            for score in scores: # Iterate through the scores list
                cleaned_token = re.sub(r'\W+', '', str(score['token'])).lower()
                if cleaned_token in anchors: # Check if the token value is in the anchors list
                    updated_importance = {'token': score['token'],
                                        'importance_score': score['importance_score'] + (x / len(importance_scores)),
                                        'position': score['position']}
                    filtered_tokens.append(updated_importance) # Append the updated importance score to the new list
            return filtered_tokens
        
        except KeyError as e:
            log.error(f"KeyError: Missing key in one of the dictionaries - {e}")
            raise
        except TypeError as e:
            log.error(f"TypeError: Invalid type encountered - {e}")
            raise
        except ZeroDivisionError as e:
            log.error(f"ZeroDivisionError: Division by zero encountered - {e}")
            raise
        except Exception as e:
            log.error(f"An unexpected error occurred: {e}")
            raise
        
    async def sentiment_analysis(text: str, class_names, modelName):
        log.info("Running local_explain")
        try:
            token_cost = None
            if (modelName is not None and modelName != "" and modelName.lower() == "gpt4" or modelName.lower() == "gpt-4o" or modelName.lower() == "gpt-35-turbo"):
                start_time = time.time()
                explanation, input_tokens, output_tokens = Azure().generate(Prompt.get_classification_prompt(text), modelName)
                end_time = time.time()
                total_time = round(end_time-start_time, 3)
                explanation = ResponsibleAIExplain.llm_response_to_json(explanation.replace("\n", " "))

                # Normalize the importance scores to ensure their sum equals 100
                explanation['token_importance_mapping'] = ResponsibleAIExplain.normalize_scores(explanation['token_importance_mapping'])

                # Extract the top 10 important tokens
                tokens_mapping = ResponsibleAIExplain.filter_token_importance(explanation['token_importance_mapping'], explanation['Keywords'])
                token_cost = Utils.get_token_cost(input_tokens, output_tokens, os.getenv("AZURE_DEPLOYMENT_ENGINE"))
                return {"predictedTarget": explanation['Sentiment'], 
                        "anchor": explanation['Keywords'], 
                        "explanation": explanation['Explanation'],
                        "token_importance_mapping": tokens_mapping,
                        "time_taken": total_time,
                        "token_cost": token_cost}
        except Exception as e:
            log.error(e,exc_info=True)
            raise

    async def local_explanation(prompt: str, response: str, context: None, modelName: None, modelEndpointUrl: None, endpointInputParam: None, endpointOutputParam: None):
        try:
            token_cost = None
            start_time = time.time()
            if modelEndpointUrl is not None and endpointInputParam is not None and endpointOutputParam is not None:
                prompt = Prompt.get_local_explanation_prompt(prompt, response, context)
                explanation = APIEndpoint.endpoint_calling(prompt, modelEndpointUrl, endpointInputParam, endpointOutputParam)
            elif (modelName is not None and modelName != "" and modelName.lower().startswith(("gpt"))) and modelEndpointUrl is None:
                explanation, input_tokens, output_tokens = Azure().generate(Prompt.get_local_explanation_prompt(prompt, response, context), modelName)
                token_cost = Utils.get_token_cost(input_tokens, output_tokens, os.getenv("AZURE_DEPLOYMENT_ENGINE"))
            end_time = time.time()
            total_time = round(end_time-start_time, 3)

            explanation = ResponsibleAIExplain.llm_response_to_json(explanation.replace("\n", " "))
            explanation['time_taken'] = total_time
            explanation['token_cost'] = token_cost

            return explanation
        except Exception as e:
            log.error(e, exc_info=True)
            raise
        
    async def process_importance(importance_function, *args, **kwargs):
        try:
            start_time = time.time()
            importance_map = await importance_function(*args, **kwargs)
            importance_map_df = pd.DataFrame(importance_map, columns=['token', 'importance_value'])
            offset = importance_map_df['importance_value'].mean()

            importance_log = Utils.scale_importance_log(
                importance_map, 
                base=None, 
                offset=offset, 
                min_percentile=0,
                max_percentile=100, 
                scaling_factor=1, 
                bias=0
            )
            importance_log_df = pd.DataFrame(importance_log, columns=['token', 'importance_value'])
            end_time = time.time()
            total_time = round(end_time-start_time, 3)
            return importance_log_df, total_time
        
        except Exception as e:
            log.error(e, exc_info=True)
            raise 
    
    async def prompt_based_token_importance(prompt, modelEndpointUrl = None, endpointInputParam = None, endpointOutputParam = None):
       
        try:
            start_time = time.time()    
            max_retries = 5
            attempts = 0
            token_cost = None   
            while attempts < max_retries:
                try:
                    if modelEndpointUrl is not None and endpointInputParam is not None:
                        prompt = Prompt.get_token_importance_prompt(prompt)
                        explanation = APIEndpoint.endpoint_calling(prompt, modelEndpointUrl, endpointInputParam, endpointOutputParam)
                    else:
                        explanation, input_tokens, output_tokens = Azure().generate(Prompt.get_token_importance_prompt(prompt))
                        token_cost = Utils.get_token_cost(input_tokens, output_tokens, os.getenv("AZURE_DEPLOYMENT_ENGINE"))

                    # Manually find the JSON substring within the mixed content
                    start_index = explanation.find('{')
                    end_index = explanation.rfind('}')
                    if start_index != -1 and end_index != -1 and end_index > start_index:
                        json_content = explanation[start_index:end_index+1]
                        result = json.loads(json_content)
                        # If JSON loads successfully, break out of the loop
                        break
                except JSONDecodeError:
                    attempts += 1
                    if attempts == max_retries:
                        raise Exception("Failed to decode JSON after 5 attempts.")
                    else:
                        log.debug(f"JSONDecodeError encountered. Retrying... Attempt {attempts}/{max_retries}")
                        # Add a delay before the next attempt
                        time.sleep(2) # Delay for 2 seconds
                        
            # Assuming 'result' is a dictionary with "Token" and "Importance Score" as keys, and their values are lists
            # First, create a DataFrame from the 'result' dictionary
            tokens = result['Token']
            scores = result['Importance Score']
            # Check if scores is a list containing a single string
            if isinstance(scores, list) and len(scores) == 1 and isinstance(scores[0], str):
                # Split the string by commas and convert each element to a float
                scores = [float(score.strip()) for score in scores[0].split(',')]
            positions = list(range(1, len(result['Token']) + 1))

            # Find the length of the shortest list
            min_length = min(len(tokens), len(scores), len(positions))

            # Trim the lists to the length of the shortest list
            tokens = tokens[:min_length]
            scores = scores[:min_length]
            positions = positions[:min_length]

            df = pd.DataFrame({
                'token': tokens,
                'importance_value': scores,
                'position': positions
            })
 
            df['importance_value'] = df['importance_value'].astype(float)

            df_top = df
            df_top.reset_index(drop=True, inplace=True)
            end_time = time.time()
            total_time = round(end_time-start_time, 3)
            return df_top.to_dict(orient='records'), total_time, token_cost
        
        except Exception as e:
            log.error(e, exc_info=True)
            raise 

    async def graph_of_thoughts(prompt: str, modelName: str):
        try:
            start_time = time.time()
            budget = 30
            task = "answer the following question"
            question = prompt
            approaches = [GraphOfThoughts.got]
            modelName = modelName
            
            formatted_graph, formatted_thoughts = GraphOfThoughts.run(task=task, question=question, 
                                                                      methods=approaches, 
                                                                      budget=budget, 
                                                                      lm_name=modelName)
            
            formatted_graph[3]['operation'] = 'final_thought'
            for i in range(4):
                thoughts = formatted_graph[i]['thoughts']
                for j in range(len(thoughts)):
                    formatted_graph[i]['thoughts'][j]['score'] = round(formatted_graph[i]['thoughts'][j]['score'], 2)
            end_time = time.time()
            total_time = round(end_time-start_time, 3)

            return formatted_graph, formatted_thoughts, total_time
        except Exception as e:
            log.error(e, exc_info=True)
            raise

    async def search_augmentation(inputPrompt, llmResponse, modelName):
        try:
            import datetime
            current_date = datetime.datetime.now()

            start_time = time.time()
            if (modelName is not None and modelName != "" and modelName.lower() == "gpt4" or modelName.lower() == "gpt-4o" or modelName.lower() == "gpt-35-turbo"):

                # Step 1: Generate Facts with LLM response
                facts, input_tokens, output_tokens = Azure().generate(Prompt.generate_facts_prompt(inputPrompt, llmResponse, current_date), modelName)
                facts_cost = Utils.get_token_cost(input_tokens, output_tokens, os.getenv("AZURE_DEPLOYMENT_ENGINE"))

                if isinstance(facts, str):
                    facts = ResponsibleAIExplain.llm_response_to_json(facts.replace("\n", " "))
                facts_list = [fact['Fact'] for fact in facts['Facts']] # Extracting the facts into a list of strings

                # Step 2: Filter the facts that are relevant to the input prompt
                filtered_facts, input_tokens1, output_tokens1 = Azure().generate(Prompt.filter_facts_prompt(prompt=inputPrompt, facts=facts_list), modelName)
                if isinstance(filtered_facts, str):
                    filtered_facts = filtered_facts.replace('```json', '').replace('```', '').strip()
                filtered_facts_cost = Utils.get_token_cost(input_tokens1, output_tokens1, os.getenv("AZURE_DEPLOYMENT_ENGINE"))
                filtered_facts = ast.literal_eval(filtered_facts)
                filtered_facts_ir = [fact + ' is this statement valid as of today ? why ? #' for fact in filtered_facts]
                questions = [inputPrompt] + filtered_facts_ir

                # Step 3: Run the prompt and facts through the Perplexity API
                answers= Perplexity().get_perplexity(inputPrompt)
                qa_dict_list_prompt = [{'question': q, 'answer': a} for q, a in zip([inputPrompt], [answers])] # Creating the list of dictionaries
                
                answers_facts  = [Perplexity().get_perplexity(qn) for qn in questions]
                qa_dict_list = [{'question': q, 'answer': a} for q, a in zip(questions, answers_facts)] # Creating the list of dictionaries

                if len(facts_list) == 0:
                    return {'internetResponse': qa_dict_list_prompt[0]['answer'], 
                            'factual_check': {"Score": 0.0,
                                            "explanation_factual_accuracy": {'Result': ['No facts found in the LLM response.']} }}

                # Step 4: Summarize the internet responses for prompt and facts
                summary_prompt, input_tokens2, output_tokens2 = Azure().generate(Prompt.summarize_prompt(qa_dict_list_prompt), modelName)
                summary_prompt_cost = Utils.get_token_cost(input_tokens2, output_tokens2, os.getenv("AZURE_DEPLOYMENT_ENGINE"))
                # Step 5: Evaluate fact with Google Search results
                facts, input_tokens3, output_tokens3 = Azure().generate(Prompt.evaluate_facts_prompt(facts=filtered_facts_ir, context=qa_dict_list, prompt=inputPrompt), modelName)
                eval_facts_cost = Utils.get_token_cost(input_tokens3, output_tokens3, os.getenv("AZURE_DEPLOYMENT_ENGINE"))
                if isinstance(facts, str):
                    facts = ResponsibleAIExplain.llm_response_to_json(facts.replace("\n", " "))

                # In facts['Result'], each fact is a dictionary with keys 'Fact', 'Reasoning', and 'Judgement', update Fact with the filtered facts
                for i, fact in enumerate(facts['Result']):
                    fact['Fact'] = filtered_facts[i]

                factuality_check = { "Score": 1.0,
                                    "explanation_factual_accuracy": facts }
            end_time = time.time()
            total_time = round(end_time-start_time, 3)
            return {'internetResponse': summary_prompt,
                    'factual_check': factuality_check,
                    'time_taken': total_time,
                    'token_cost': facts_cost + filtered_facts_cost + summary_prompt_cost + eval_facts_cost}
        
        except Exception as e:
            log.error(e, exc_info=True)
            raise

    async def reread_reasoning(text: str, modelName: str, endpointDetails: dict):
        log.info("Running local_explain")
        try:
            token_cost = None
            if endpointDetails is not None and ((endpointDetails.modelEndpointUrl is not None and endpointDetails.modelEndpointUrl !="") and (endpointDetails.endpointInputParam is not None and endpointDetails.endpointInputParam !="") and (endpointDetails.endpointOutputParam is not None and endpointDetails.endpointOutputParam !="")):
                
                modelEndpointUrl = endpointDetails.modelEndpointUrl
                endpointInputParam = endpointDetails.endpointInputParam
                endpointOutputParam = endpointDetails.endpointOutputParam
            else:
                
                modelEndpointUrl = None
                endpointInputParam = None
                endpointOutputParam = None

            start_time = time.time()
            if (modelName is not None and modelName != "" and modelName.lower() == "gpt4" or modelName.lower() == "gpt-4o" or modelName.lower() == "gpt-35-turbo") and modelEndpointUrl is None:
                explanation, input_tokens, output_tokens = Azure().generate(Prompt.reread_thot(text),modelName)
                explanation = ResponsibleAIExplain.llm_response_to_json(explanation.replace("\n", " "))
                token_cost = Utils.get_token_cost(input_tokens, output_tokens, modelName.lower())
                reponse_obj = {"result": explanation['Result'], "explanation": explanation['Explanation']}

            elif (modelName is not None and modelName != "" and modelName.lower() == "gemini-pro" or modelName.lower() == "gemini-flash" and modelEndpointUrl is None):
                explanation = Gemini().generate(Prompt.reread_thot(text),modelName)
                explanation = ResponsibleAIExplain.llm_response_to_json(explanation.replace("\n", " "))
                reponse_obj = {"result": explanation['Result'], "explanation": explanation['Explanation']}

            elif (modelName is not None and modelName != "" and modelName.lower() == "aws" and modelEndpointUrl is None):
                explanation = AWS().call_AWS(Prompt.reread_thot(text))
                explanation = ResponsibleAIExplain.llm_response_to_json(explanation.replace("\n", " "))
                reponse_obj = {"result": explanation['Result'], "explanation": explanation['Explanation']}

            elif (modelName is not None and modelName != "" and modelName.lower() == "llama2") and modelEndpointUrl is None:
                explanation = Llamacompletion().textCompletion(text, "Reread THOT")
                response_string = explanation[0]
                result_start = response_string.find("Result:") + len("Result:")
                result_end = response_string.find("Explanation:")
                result = response_string[result_start:result_end].strip()
                explanation_start = response_string.find("Explanation:") + len("Explanation:")
                explanation = response_string[explanation_start:].strip()
                reponse_obj = {"result": result, "explanation": explanation}

            elif modelEndpointUrl is not None and endpointInputParam is not None and endpointOutputParam is not None:
                response = APIEndpoint.endpoint_calling((Prompt.reread_thot(text)), modelEndpointUrl, endpointInputParam, endpointOutputParam)
                explanation = ResponsibleAIExplain.llm_response_to_json(response.replace("\n", " "))
                reponse_obj = {"result": explanation['Result'], "explanation": explanation['Explanation']}
            
            end_time = time.time()
            total_time = round(end_time-start_time, 3)
            return {"response": reponse_obj, "time_taken": total_time, "token_cost": token_cost}
        except Exception as e:
            log.error(e,exc_info=True)
            raise 

    async def generate_thot(text: str, modelName: str, endpointDetails: dict, temperature: float = 0.1):
        log.info("Running local_explain")
        try:
            token_cost = None
            if endpointDetails is not None and ((endpointDetails.modelEndpointUrl is not None and endpointDetails.modelEndpointUrl !="") and (endpointDetails.endpointInputParam is not None and endpointDetails.endpointInputParam !="") and (endpointDetails.endpointOutputParam is not None and endpointDetails.endpointOutputParam !="")):
              
                modelEndpointUrl = endpointDetails.modelEndpointUrl
                endpointInputParam = endpointDetails.endpointInputParam
                endpointOutputParam = endpointDetails.endpointOutputParam
            else:
              
                modelEndpointUrl = None
                endpointInputParam = None
                endpointOutputParam = None

            start_time = time.time()
            if (modelName is not None and modelName != "" and modelName.lower() == "gpt4" or modelName.lower() == "gpt-4o" or modelName.lower() == "gpt-35-turbo") and modelEndpointUrl is None:
                response, input_tokens, output_tokens = Azure().generate(Prompt.thot(text), modelName)
                explanation = ResponsibleAIExplain.llm_response_to_json(response.replace("\n", " "))
                token_cost = Utils.get_token_cost(input_tokens, output_tokens, modelName.lower())
                reponse_obj = {"result": explanation['Result'], "explanation": explanation['Explanation']}
            
            elif (modelName is not None and modelName != "" and modelName.lower() == "gemini-pro" or modelName.lower() == "gemini-flash" and modelEndpointUrl is None):
                response = Gemini().generate(Prompt.thot(text), modelName)
                explanation = ResponsibleAIExplain.llm_response_to_json(response.replace("\n", " "))
                reponse_obj = {"result": explanation['Result'], "explanation": explanation['Explanation']}
            
            elif (modelName is not None and modelName != "" and modelName.lower() == "aws" and modelEndpointUrl is None):
                response = AWS().call_AWS(Prompt.thot(text))
                explanation = ResponsibleAIExplain.llm_response_to_json(response.replace("\n", " "))
                reponse_obj = {"result": explanation['Result'], "explanation": explanation['Explanation']}

            elif (modelName is not None and modelName != "" and modelName.lower() == "llama2") and modelEndpointUrl is None:
                response = Llamacompletion().textCompletion(text, technique="THOT")
                response_string = response[0]
                result_start = response_string.find("Result:") + len("Result:")
                result_end = response_string.find("Explanation:")
                result = response_string[result_start:result_end].strip()
                explanation_start = response_string.find("Explanation:") + len("Explanation:")
                explanation = response_string[explanation_start:].strip()
                reponse_obj = {"result": result, "explanation": explanation}


            elif modelEndpointUrl is not None and endpointInputParam is not None and endpointOutputParam is not None:
                response = APIEndpoint.endpoint_calling((Prompt.thot(text)), modelEndpointUrl, endpointInputParam, endpointOutputParam)
                explanation = ResponsibleAIExplain.llm_response_to_json(response.replace("\n", " "))
                reponse_obj = {"result": explanation['Result'], "explanation": explanation['Explanation']}

            end_time = time.time()
            total_time = round(end_time-start_time, 3)
            return {"response": reponse_obj, "time_taken": total_time, "token_cost": token_cost}
        except Exception as e:
            log.error(e,exc_info=True)
            raise 

    async def generate_cot(text: str, modelName: str, endpointDetails: dict, temperature: float = 0.1):
        log.info("Running local_explain")
        try:
            token_cost = None
            if endpointDetails is not None and ((endpointDetails.modelEndpointUrl is not None and endpointDetails.modelEndpointUrl !="") and (endpointDetails.endpointInputParam is not None and endpointDetails.endpointInputParam !="") and (endpointDetails.endpointOutputParam is not None and endpointDetails.endpointOutputParam !="")):
                
                modelEndpointUrl = endpointDetails.modelEndpointUrl
                endpointInputParam = endpointDetails.endpointInputParam
                endpointOutputParam = endpointDetails.endpointOutputParam
            else:
                
                modelEndpointUrl = None
                endpointInputParam = None
                endpointOutputParam = None

            start_time = time.time()
            if (modelName is not None and modelName != "" and modelName.lower() == "gpt4" or modelName.lower() == "gpt-4o" or modelName.lower() == "gpt-35-turbo") and modelEndpointUrl is None:
                response, input_tokens, output_tokens = Azure().generate(Prompt.cot(text), modelName)
                explanation = ResponsibleAIExplain.llm_response_to_json(response.replace("\n", " "))
                reponse_obj = explanation['Explanation']
                token_cost = Utils.get_token_cost(input_tokens, output_tokens, modelName.lower())
            
            elif (modelName is not None and modelName != "" and modelName.lower() == "gemini-pro" or modelName.lower() == "gemini-flash" and modelEndpointUrl is None):
                response = Gemini().generate(Prompt.cot(text), modelName)
                explanation = ResponsibleAIExplain.llm_response_to_json(response.replace("\n", " "))
                reponse_obj = explanation['Explanation']

            elif (modelName is not None and modelName != "" and modelName.lower() == "aws" and modelEndpointUrl is None):
                response = AWS().call_AWS(Prompt.cot(text))
                explanation = ResponsibleAIExplain.llm_response_to_json(response.replace("\n", " "))
                reponse_obj = explanation['Explanation']
 
            elif (modelName is not None and modelName != "" and modelName.lower() == "llama2") and modelEndpointUrl is None:
                response = Llamacompletion().textCompletion(text, technique="COT")
                # Split the explanation into lines
                lines = response[0].split('\n')
                # Remove the first and last lines
                if len(lines) > 2:
                    lines = lines[1:-1]
                # Join the remaining lines back together
                filtered_explanation = '\n'.join(lines)
                reponse_obj = filtered_explanation


            elif modelEndpointUrl is not None and endpointInputParam is not None and endpointOutputParam is not None:
                response = APIEndpoint.endpoint_calling((Prompt.cot(text)), modelEndpointUrl, endpointInputParam, endpointOutputParam)
                explanation = ResponsibleAIExplain.llm_response_to_json(response.replace("\n", " "))
                reponse_obj =  explanation['Explanation']

            end_time = time.time()
            total_time = round(end_time-start_time, 3)
            return {"response": reponse_obj, "time_taken": total_time, "token_cost": token_cost}
        except Exception as e:
            log.error(e,exc_info=True)
            raise 

    async def generate_cov(payload: dict):
        log.info("Running local_explain")

        text = payload.inputPrompt
        modelName = payload.modelName
        endpointDetails = payload.endpointDetails
        complexity = payload.complexity
        translate = payload.translate
        
        try:
            if endpointDetails is not None and ((endpointDetails.modelEndpointUrl is not None and endpointDetails.modelEndpointUrl !="") and (endpointDetails.endpointInputParam is not None and endpointDetails.endpointInputParam !="") and (endpointDetails.endpointOutputParam is not None and endpointDetails.endpointOutputParam !="")):
                modelEndpointUrl = endpointDetails.modelEndpointUrl
                endpointInputParam = endpointDetails.endpointInputParam
                endpointOutputParam = endpointDetails.endpointOutputParam
            else:
                modelEndpointUrl = None
                endpointInputParam = None
                endpointOutputParam = None

            if (modelName is not None and modelName != "" and modelName.lower() == "gpt4" or modelName.lower() == "gpt-4o" or modelName.lower() == "gpt-35-turbo" or modelName.lower() == "gemini-pro" or modelName.lower() == "gemini-flash") and modelEndpointUrl is None:
                response = Cov.cov_gpt(text, complexity, modelName)
                promptTriggering = "The response was filtered due to the prompt triggering Azure OpenAI's content management policy. Please modify your prompt and retry. To learn more about our content filtering policies please read our documentation: https://go.microsoft.com/fwlink/?linkid=2198766"
                if (promptTriggering not in response) and (response != "Rate Limit Error"):
                    if isinstance(response, dict):
                        if isinstance(response.get('original_question'), list):
                            response['original_question'] = response['original_question'].pop()

            elif (modelName is not None and modelName != "" and modelName.lower() == "llama2") and modelEndpointUrl is None:
                response = response = CovLlama.cov(text, complexity)

            elif (modelName is not None and modelName != "" and modelName.lower() == "aws") and modelEndpointUrl is None:
                response = CovAWS.cov(text, complexity)

            elif modelEndpointUrl is not None and endpointInputParam is not None and endpointOutputParam is not None:
                response =  Cov.cov_endpoint(text, complexity, modelEndpointUrl, endpointInputParam, endpointOutputParam)

            if translate == "google":
                translated_final_answer,language = Translate.translate(response['final_answer'])
                response['translated_final_answer'] = translated_final_answer
            elif translate == "azure":
                translated_final_answer,language = Translate.azure_translate(response['final_answer'])
                response['translated_final_answer'] = translated_final_answer
            return response
        except Exception as e:
            log.error(e,exc_info=True)
            raise 

    async def generate_lot(text: str, modelName: str, endpointDetails: dict):
        log.info("Running local_explain")
        try:
            token_cost = None
            Propositions = None
            logical_expression = None
            Extended_Logical_Expression = None
            Law_used = None
            Extended_Logical_Information = None
            explanation_final = None
            total_input_tokens = 0
            total_output_tokens = 0

            if endpointDetails is not None and ((endpointDetails.modelEndpointUrl is not None and endpointDetails.modelEndpointUrl !="") and (endpointDetails.endpointInputParam is not None and endpointDetails.endpointInputParam !="") and (endpointDetails.endpointOutputParam is not None and endpointDetails.endpointOutputParam !="")):
                
                modelEndpointUrl = endpointDetails.modelEndpointUrl
                endpointInputParam = endpointDetails.endpointInputParam
                endpointOutputParam = endpointDetails.endpointOutputParam
            else:
                
                modelEndpointUrl = None
                endpointInputParam = None
                endpointOutputParam = None

            start_time = time.time()
            if (modelName is not None and modelName != "" and modelName.lower() == "gpt4" or modelName.lower() == "gpt-4o" or modelName.lower() == "gpt-35-turbo") and modelEndpointUrl is None:
                try:
                    explanation, input_tokens, output_tokens = Azure().generate(Prompt.lot_phase1(text), modelName)
                    total_input_tokens += input_tokens
                    total_output_tokens += output_tokens
                    parsed_data = ResponsibleAIExplain.llm_response_to_json(explanation.replace("\n", " "))
                    if isinstance(parsed_data, dict) and "Propositions" in parsed_data and "Logical Expression" in parsed_data:
                        if parsed_data["Propositions"] and parsed_data["Logical Expression"] != "":
                            logical_expression = parsed_data["Logical Expression"]
                            Propositions = parsed_data["Propositions"]
                            explanation2, input_tokens, output_tokens = Azure().generate(Prompt.lot_phase2(logical_expression), modelName)
                            total_input_tokens += input_tokens
                            total_output_tokens += output_tokens
                            parsed_data2 = ResponsibleAIExplain.llm_response_to_json(explanation2.replace("\n", " "))
                            Extended_Logical_Expression = parsed_data2["Extended Logical Expression"]
                            Law_used = parsed_data2["Law Used"]
                            explanation3, input_tokens, output_tokens = Azure().generate(Prompt.lot_phase3(Propositions,Extended_Logical_Expression), modelName)
                            total_input_tokens += input_tokens
                            total_output_tokens += output_tokens
                            parsed_data3 = ResponsibleAIExplain.llm_response_to_json(explanation3.replace("\n", " "))
                            Extended_Logical_Information = parsed_data3["Extended Logical Information"]
                            final_prompt = text+ str(Extended_Logical_Information)
                        else:
                            final_prompt = text
                    else:
                        final_prompt = text
                    explanation4, input_tokens, output_tokens = Azure().generate(Prompt.lot_phase4(final_prompt),modelName)
                    total_input_tokens += input_tokens
                    total_output_tokens += output_tokens
                    parsed_data4 = ResponsibleAIExplain.llm_response_to_json(explanation4.replace("\n", " "))
                    explanation_final = parsed_data4["Explanation"]       
                    token_cost = Utils.get_token_cost(total_input_tokens, total_output_tokens, modelName.lower())
                except Exception as e:
                    log.error(e,exc_info=True)
                    
            elif (modelName is not None and modelName != "" and modelName.lower() == "gemini-pro" or modelName.lower() == "gemini-flash" and modelEndpointUrl is None):
                try:
                    explanation = Gemini().generate(Prompt.lot_phase1(text), modelName)
                    parsed_data = ResponsibleAIExplain.llm_response_to_json(explanation.replace("\n", " "))
                    if isinstance(parsed_data, dict) and "Propositions" in parsed_data and "Logical Expression" in parsed_data:
                        if parsed_data["Propositions"] and parsed_data["Logical Expression"] != "":
                            logical_expression = parsed_data["Logical Expression"]
                            Propositions = parsed_data["Propositions"]
                            explanation2 = Gemini().generate(Prompt.lot_phase2(logical_expression), modelName)
                            parsed_data2 = ResponsibleAIExplain.llm_response_to_json(explanation2.replace("\n", " "))
                            Extended_Logical_Expression = parsed_data2["Extended Logical Expression"]
                            Law_used = parsed_data2["Law Used"]
                            explanation3= Gemini().generate(Prompt.lot_phase3(Propositions,Extended_Logical_Expression), modelName)
                            parsed_data3 = ResponsibleAIExplain.llm_response_to_json(explanation3.replace("\n", " "))
                            Extended_Logical_Information = parsed_data3["Extended Logical Information"]
                            final_prompt = text+ str(Extended_Logical_Information)
                        else:
                            final_prompt = text
                    else:
                        final_prompt = text
                    explanation4 = Gemini().generate(Prompt.lot_phase4(final_prompt),modelName)
                    parsed_data4 = ResponsibleAIExplain.llm_response_to_json(explanation4.replace("\n", " "))
                    explanation_final = parsed_data4["Explanation"]       
                except Exception as e:
                    log.error(e,exc_info=True)

            elif (modelName is not None and modelName != "" and modelName.lower() == "aws" and modelEndpointUrl is None):
                try:
                    explanation = AWS().call_AWS(Prompt.lot_phase1(text))
                    parsed_data = ResponsibleAIExplain.llm_response_to_json(explanation.replace("\n", " "))
                    if isinstance(parsed_data, dict) and "Propositions" in parsed_data and "Logical Expression" in parsed_data:
                        if parsed_data["Propositions"] and parsed_data["Logical Expression"] != "":
                            logical_expression = parsed_data["Logical Expression"]
                            Propositions = parsed_data["Propositions"]
                            explanation2 = AWS().call_AWS(Prompt.lot_phase2(logical_expression))
                            parsed_data2 = ResponsibleAIExplain.llm_response_to_json(explanation2.replace("\n", " "))
                            Extended_Logical_Expression = parsed_data2["Extended Logical Expression"]
                            Law_used = parsed_data2["Law Used"]
                            explanation3= AWS().call_AWS(Prompt.lot_phase3(Propositions,Extended_Logical_Expression))
                            parsed_data3 = ResponsibleAIExplain.llm_response_to_json(explanation3.replace("\n", " "))
                            Extended_Logical_Information = parsed_data3["Extended Logical Information"]
                            final_prompt = text+ str(Extended_Logical_Information)
                        else:
                            final_prompt = text
                    else:
                        final_prompt = text
                    explanation4 = AWS().call_AWS(Prompt.lot_phase4(final_prompt))
                    parsed_data4 = ResponsibleAIExplain.llm_response_to_json(explanation4.replace("\n", " "))
                    explanation_final = parsed_data4["Explanation"]       
                except Exception as e:
                    log.error(e,exc_info=True)
        
            elif modelEndpointUrl is not None and endpointInputParam is not None and endpointOutputParam is not None:
                response = APIEndpoint.endpoint_calling((Prompt.lot_phase1(text)), modelEndpointUrl, endpointInputParam, endpointOutputParam)
                explanation = ResponsibleAIExplain.llm_response_to_json(response.replace("\n", " "))
                if isinstance(explanation, dict) and "Propositions" in explanation and "Logical Expression" in explanation:
                    if explanation["Propositions"] and explanation["Logical Expression"] != "":
                        logical_expression = explanation["Logical Expression"]
                        Propositions = explanation["Propositions"]
                        response2 = APIEndpoint.endpoint_calling((Prompt.lot_phase2(logical_expression)), modelEndpointUrl, endpointInputParam, endpointOutputParam)
                        explanation2 = ResponsibleAIExplain.llm_response_to_json(response2.replace("\n", " "))
                        Extended_Logical_Expression = explanation2["Extended Logical Expression"]
                        Law_used = explanation2["Law Used"]
                        response3 = APIEndpoint.endpoint_calling((Prompt.lot_phase3(Propositions,Extended_Logical_Expression)), modelEndpointUrl, endpointInputParam, endpointOutputParam)
                        explanation3 = ResponsibleAIExplain.llm_response_to_json(response3.replace("\n", " "))
                        Extended_Logical_Information = explanation3["Extended Logical Information"]
                        final_prompt = text+ str(Extended_Logical_Information)
                    else:
                        final_prompt = text
                else:
                    final_prompt = text
                response4 = APIEndpoint.endpoint_calling((Prompt.lot_phase4(final_prompt)), modelEndpointUrl, endpointInputParam, endpointOutputParam)
                explanation4 = ResponsibleAIExplain.llm_response_to_json(response4.replace("\n", " "))
                explanation_final = explanation4["Explanation"]

            combined_response = {
                    "Explanation": explanation_final,
                    "Propositions": Propositions,
                    "Logical Expression": logical_expression,
                    "Extended Logical Expression": Extended_Logical_Expression,
                    "Law used to extend the logical expression": Law_used,
                    "Extended Logical Information": Extended_Logical_Information
                    }
            final_explanation = json.dumps(combined_response)
            explanation = ResponsibleAIExplain.llm_response_to_json(final_explanation.replace("\n", " "))
            end_time = time.time()
            total_time = round(end_time-start_time, 3)
            return {"response": explanation, "time_taken": total_time, "token_cost": token_cost}
        except Exception as e:
            log.error(e,exc_info=True)
            raise
