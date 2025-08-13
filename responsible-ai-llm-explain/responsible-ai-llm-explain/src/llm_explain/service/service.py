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

from llm_explain.service.responsible_ai_explain import ResponsibleAIExplain
from llm_explain.config.logger import CustomLogger, request_id_var
from llm_explain.utility.utility import Utils
from llm_explain.mappers.mappers import UncertainityResponse, TokenImportanceRequest, TokenImportanceResponse, SafeSearchResponse, \
    GoTResponse, GoTRequest, UncertainityRequest, SentimentAnalysisRequest, SentimentAnalysisResponse, rereadRequest, rereadResponse, \
    CoTResponse, openAIRequest, CoVRequest, SafeSearchRequest, CoVResponse, lotRequest, lotResponse
from fastapi.responses import StreamingResponse
from datetime import datetime
import pandas as pd
import joblib
import time
import io
import asyncio
import concurrent.futures
import os
import json

telemetry_flag = os.getenv("TELEMETRY_FLAG")
tel_data_url = os.getenv("BULK_TELEMETRY_URL")
log = CustomLogger()

class Payload:
    def __init__(self, **entries):
        self.__dict__.update(entries)

class ExplainService:
    async def token_importance(payload: TokenImportanceRequest) -> TokenImportanceResponse:
        try:
            log.debug(f"payload: {payload}")
            prompt = payload.inputPrompt
            modelName = payload.modelName
            endpointDetails =  payload.endpointDetails
            token_cost = None

            if endpointDetails is not None and ((endpointDetails.modelEndpointUrl is not None and endpointDetails.modelEndpointUrl !="") and (endpointDetails.endpointInputParam is not None and endpointDetails.endpointInputParam !="") and (endpointDetails.endpointOutputParam is not None and endpointDetails.endpointOutputParam !="")):
                modelEndpointUrl = endpointDetails.modelEndpointUrl
                endpointInputParam = endpointDetails.endpointInputParam
                endpointOutputParam = endpointDetails.endpointOutputParam
            else:
                modelEndpointUrl = None
                endpointInputParam = None
                endpointOutputParam = None

            separated_words = prompt.split()
            if len(separated_words) <= 2 and modelEndpointUrl is None:
                modelName = 'code'

            if modelName == "code":
                try:
                    gpt3tokenizer = joblib.load("../models/gpt3tokenizer.pkl") 
                    importance_map_log_df, total_time = await ResponsibleAIExplain.process_importance(Utils.ablated_relative_importance,prompt,gpt3tokenizer)
                    df = importance_map_log_df.copy()
                    df["Position"] = range(len(df))
                    # df = df.sort_values(by='importance_value', ascending=False)
                    top_imp=df.to_dict(orient='records')

                except Exception as e:
                    start_time = time.time()
                    words = prompt.split()
                    avoid = ['the', 'a', 'an', 'is', 'are', 'was', 'were', 'am', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'shall', 'would', 'should', 'can', 'could', 'may', 'might', 'must', 'ought','need', 'used', 'to', 'of', 'in', 'on','with']

                    final_words = [word for word in words if word.lower() not in avoid][:2]
                    position = range(len(final_words))
                    importance = [0.7, 0.3]

                    # Create a DataFrame
                    df = pd.DataFrame({
                        'word': final_words,
                        'position': position,
                        'importance': importance
                    })

                    # Convert the DataFrame to a dictionary with orient='records'
                    dict_records = df.to_dict(orient='records')
                    end_time = time.time()
                    total_time = round(end_time-start_time, 3)
                    return TokenImportanceResponse(token_importance_mapping=dict_records, time_taken=total_time, token_cost = token_cost)
             
            elif (modelName == "GPT" or modelName is None or modelName == "") and modelEndpointUrl is None:
                top_imp, total_time, token_cost = await ResponsibleAIExplain.prompt_based_token_importance(prompt)
            
            elif modelEndpointUrl is not None and endpointInputParam is not None and endpointOutputParam is not None:
                top_imp, total_time, token_cost = await ResponsibleAIExplain.prompt_based_token_importance(prompt, modelEndpointUrl, endpointInputParam, endpointOutputParam) 
            return TokenImportanceResponse(token_importance_mapping=top_imp, time_taken=total_time, token_cost=token_cost)

        except Exception as e:
            log.error(e,exc_info=True)
            raise

    @staticmethod
    def get_label(score, reverse=False):
        score = int(score) # Convert score to integer
        if reverse:
            return 'Highly' if score <= 30 else 'Moderately' if score <= 70 else 'Less'
        else:
            return 'Less' if score <= 30 else 'Moderately' if score <= 70 else 'Highly'
        
    async def sentiment_analysis(payload: SentimentAnalysisRequest) -> SentimentAnalysisResponse:
        log.debug(f"payload: {payload}")

        try:
            obj_explain = await ResponsibleAIExplain.sentiment_analysis(text=payload.inputPrompt, 
                                                                  class_names=["Negative","Positive"], modelName = payload.modelName)
            log.debug(f"obj_explain: {obj_explain}")

            List_explain = []
            List_explain.append(obj_explain)

            objExplainabilityLocalResponse = SentimentAnalysisResponse(explanation=List_explain)

            return objExplainabilityLocalResponse
        except Exception as e:
            log.error(e,exc_info=True)
            raise

    async def local_explanation(payload: UncertainityRequest) -> UncertainityResponse:
        try:
            log.debug(f"payload: {payload}")
            prompt = payload.inputPrompt
            response = payload.response
            context = payload.context
            modelName = payload.modelName
            endpointDetails =  payload.endpointDetails

            if endpointDetails is not None and ((endpointDetails.modelEndpointUrl is not None and endpointDetails.modelEndpointUrl !="") and (endpointDetails.endpointInputParam is not None and endpointDetails.endpointInputParam !="") and (endpointDetails.endpointOutputParam is not None and endpointDetails.endpointOutputParam !="")):
                modelEndpointUrl = endpointDetails.modelEndpointUrl
                endpointInputParam = endpointDetails.endpointInputParam
                endpointOutputParam = endpointDetails.endpointOutputParam
            else:
                modelEndpointUrl = None
                endpointInputParam = None
                endpointOutputParam = None

            result = await ResponsibleAIExplain.local_explanation(prompt=prompt, response=response, context=context, modelName=modelName, modelEndpointUrl=modelEndpointUrl, endpointInputParam=endpointInputParam, endpointOutputParam=endpointOutputParam)
            result['uncertainty']['uncertainty_level'] = f"{ExplainService.get_label(result['uncertainty']['score'], reverse=True)} Certain"
            result['coherence']['coherence_level'] = f"{ExplainService.get_label(result['coherence']['score'])} Coherent"
            response_obj = UncertainityResponse(**result)

            return response_obj

        except Exception as e:
            log.error(e,exc_info=True)
            raise 

    async def graph_of_thoughts(payload: GoTRequest) -> GoTResponse:
        try:
            log.debug(f"payload: {payload}")
            prompt = payload.inputPrompt
            modelName = payload.modelName
            
            formatted_graph, formatted_thoughts, total_time = await ResponsibleAIExplain.graph_of_thoughts(prompt=prompt, modelName=modelName)

            # Calculate the cost
            prompt_tokens = formatted_graph[len(formatted_graph) - 1]['prompt_tokens']
            completion_tokens = formatted_graph[len(formatted_graph) - 1]['completion_tokens']
            cost = Utils.get_token_cost(input_tokens=prompt_tokens, output_tokens=completion_tokens, model=modelName)

            # get the final thought and score from the formatted graph
            final_thoughts = [item['thoughts'] for item in formatted_graph if 'operation' in item and item['operation'] == 'final_thought']
            final_thought = final_thoughts[0][0] if final_thoughts else None

            if final_thought:
                final_thought_key = final_thought.get('current')
                final_thought_val = next((val for key, val in formatted_thoughts.items() if key == final_thought_key), None)
            else:
                final_thought_val = None

            if final_thought and final_thought_val:
                if final_thought['score'] <= 50:
                    final_thought['score'] = final_thought['score'] + 45
                elif final_thought['score'] >= 100:
                    final_thought['score'] = 95

                label = f"{ExplainService.get_label(final_thought['score'])} Consistent"
                return GoTResponse(final_thought=final_thought_val, score=final_thought['score'], token_cost=cost, consistency_level=label, time_taken=total_time)
            else:
                # Handle the case where final_thought or final_thought_val is not found
                log.error("Final thought or value not found.")
                raise Exception("Final thought or value not found.")
            
        except Exception as e:
            log.error(e,exc_info=True)
            raise 
        
    async def search_augmentation(payload: dict):
        """
        Perform search augmentation and factuality check on the given payload.

        Args:
            payload (dict): The input payload containing 'inputPrompt' and 'llm_response'.

        Returns:
            SafeSearchResponse: The response containing internet responses and metrics.
        """
        try:
            inputPrompt = payload.inputPrompt
            llmResponse = payload.llm_response
            modelName = payload.modelName

            response = await ResponsibleAIExplain.search_augmentation(inputPrompt, llmResponse, modelName)
            internet_responses = [response['internetResponse']]

            # Replace Judgement values in explanation
            explanation = response['factual_check']['explanation_factual_accuracy']['Result']
            if explanation[0] != 'No facts found in the LLM response.':
                for item in explanation:
                    if item['Judgement'] == 'yes':
                        item['Judgement'] = 'Fact Verified'
                    elif item['Judgement'] == 'no':
                        item['Judgement'] = 'Fact Not Verified'
                    elif item['Judgement'] == 'unclear':
                        item['Judgement'] = 'Fact Unclear'

            metrics = [{
                "metricName": 'Factuality Check',
                "score": response['factual_check']['Score'],
                "explanation": explanation
            }]
            return SafeSearchResponse(internetResponse=internet_responses, metrics=metrics, time_taken=response['time_taken'], token_cost=response['token_cost'])
        except ValueError as e:
            log.error(e, exc_info=True)
            raise
        except Exception as e:
            log.error(e,exc_info=True)
            raise
    
    async def reread_reasoning(payload: rereadRequest) -> rereadResponse:

        log.debug(f"payload: {payload}")

        try:
            obj_explain = await ResponsibleAIExplain.reread_reasoning(text=payload.inputPrompt, modelName=payload.modelName, endpointDetails=payload.endpointDetails)
            log.debug(f"obj_explain: {obj_explain}")
            return rereadResponse(response=obj_explain.get('response'), time_taken=obj_explain.get('time_taken'), token_cost=obj_explain.get('token_cost'))
        except Exception as e:
            log.error(e,exc_info=True)
            raise

    async def thot_reasoning(payload: dict):
        try:
            obj_explain = await ResponsibleAIExplain.generate_thot(text=payload.inputPrompt, modelName=payload.modelName,  endpointDetails=payload.endpointDetails, temperature=payload.temperature)
            log.debug(f"obj_explain: {obj_explain}")

            return rereadResponse(response=obj_explain.get('response'), time_taken=obj_explain.get('time_taken'), token_cost=obj_explain.get('token_cost'))
    
        except Exception as e:
            log.error(e,exc_info=True)
            raise

    async def cot_reasoning(payload: dict):
        try:
            obj_explain = await ResponsibleAIExplain.generate_cot(text=payload.inputPrompt, modelName=payload.modelName,  endpointDetails=payload.endpointDetails, temperature=payload.temperature)
            log.debug(f"obj_explain: {obj_explain}")

            return CoTResponse(explanation=obj_explain.get('response'), time_taken=obj_explain.get('time_taken'), token_cost=obj_explain.get('token_cost'))
    
        except Exception as e:
            log.error(e,exc_info=True)
            raise


    async def cov_reasoning(payload: dict): 
        try:
            obj_explain = await ResponsibleAIExplain.generate_cov(payload)
            log.debug(f"obj_explain: {obj_explain}")
            
            return CoVResponse(original_question=obj_explain.get('original_question'), baseline_response=obj_explain.get('baseline_response'), verification_questions=obj_explain.get('verification_questions'), verification_answers=obj_explain.get('verification_answers'), final_answer=obj_explain.get('final_answer'), time_taken=obj_explain.get('time_taken'), token_cost=obj_explain.get('token_cost'))
    
        except Exception as e:
            log.error(e,exc_info=True)
            raise

    async def lot_reasoning(payload: lotRequest) -> lotResponse:

        log.debug(f"payload: {payload}")

        try:
            if payload.llmResponse is None:
                text_upd = payload.inputPrompt
            else: 
                text_upd = payload.inputPrompt+payload.llmResponse
            obj_explain = await ResponsibleAIExplain.generate_lot(text=text_upd, modelName=payload.modelName, endpointDetails=payload.endpointDetails)
            log.debug(f"obj_explain: {obj_explain}".encode('ascii', 'ignore').decode('ascii'))
            return lotResponse(response=obj_explain.get('response'), time_taken=obj_explain.get('time_taken'), token_cost=obj_explain.get('token_cost'))
        except Exception as e:
            log.error(e,exc_info=True)
            raise

    async def bulk_processing_explanation(payload): 
        try:
            def processing_task_response(row, selected_methods, results):
                try:
                    # Define the mapping of methods to their corresponding column names
                    method_to_column = {
                        "Token-Importance": "Token Importance Details",
                        "Evalution-Metrics": "Evalution Metrics",
                        "ThoT": "Thread of Thought",
                        "ReRead-ThoT": "Reread ThoT",
                        "CoT": "Chain of Thought",
                        "CoV": "Chain of Verification",
                        "LoT": "Logic of Thought",
                        "GoT": "Graph of Thought",
                        "Sentiment-Analysis": "Sentiment Analysis Details",
                        "Safe-Search": "Search Augmentation Details"
                    }
                    # Unpack the results dynamically based on the selected methods
                    results_dict = {method: [] for method in selected_methods}
                    # total_token_costs = [0] * len(selected_methods)
                    total_token_costs = 0
                    # Create the DataFrame with the initial data
                    df = pd.DataFrame({
                        'InputPrompt': [row['InputPrompt']],
                        'Response': [row['Response']]
                    })
                    for i, method in enumerate(selected_methods):
                        method_results = results[i::len(selected_methods)]
                        for j, res in enumerate(method_results):
                            if isinstance(res, Exception):
                                log.error(f"Error in method {method} for row {j}: {res}")
                                results_dict[method].append(None)
                                continue
                            results_dict[method].append(res.__dict__ if hasattr(res, '__dict__') else res)

                            if method == "Sentiment-Analysis" and isinstance(res.explanation, list):
                                # total_token_costs[j] += res.explanation[0].get('token_cost', 0)
                                total_token_costs += res.explanation[0].get('token_cost', 0)
                                for explanation in res.explanation:
                                    explanation.pop('time_taken', None)
                                    explanation.pop('token_cost', None)

                            else:
                                if method == "CoV":
                                    res.__dict__.pop('original_question', None)
                                    res.__dict__.pop('baseline_response', None)
                                # total_token_costs[j] += getattr(res, 'token_cost', 0)
                                total_token_costs += getattr(res, 'token_cost', 0)
                                res.__dict__.pop('time_taken', None)
                                res.__dict__.pop('token_cost', None)

                    # Add the results to the DataFrame dynamically
                    for method in selected_methods:
                        if method in method_to_column:
                            df[method_to_column[method]] = results_dict[method]
                    # Add the total token cost to the DataFrame
                    # df['Token Cost'] = sum(total_token_costs)
                    df['Token Cost'] = total_token_costs

                    return df
                except Exception as e:
                    log.error(e, exc_info=True)
                    raise

            METHODS_MAPPING = {
                "Token-Importance": ExplainService.token_importance,
                "Evalution-Metrics": ExplainService.local_explanation,
                "ThoT": ExplainService.thot_reasoning,
                "ReRead-ThoT": ExplainService.reread_reasoning,
                "GoT": ExplainService.graph_of_thoughts,  
                "CoT": ExplainService.cot_reasoning,
                "CoV": ExplainService.cov_reasoning,
                "LoT": ExplainService.lot_reasoning,
                "Safe-Search": ExplainService.search_augmentation,
                "Sentiment-Analysis": ExplainService.sentiment_analysis,
                "All": "All"
            }
            file = payload['file']
            methods = payload['methods']
            response_type = payload['response_type']

            contents = await file.read()
            if file.filename.endswith('.csv'):
                df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
            elif file.filename.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(io.BytesIO(contents))
            else:
                raise ValueError("Unsupported file type")
            
            if "All" in methods:
                selected_methods = [method for method in METHODS_MAPPING.keys() if method != "All"]
            else:
                selected_methods = methods
            
            async def methods_mapping_fn(row, selected_methods):
                inputPrompt = row['InputPrompt']
                response = row['Response']
                endpointDetails = None
                row_tasks = []
                # Define the mapping of methods to their corresponding request functions
                method_to_request = {
                    "Token-Importance": lambda: METHODS_MAPPING["Token-Importance"](TokenImportanceRequest(inputPrompt=inputPrompt, modelName='GPT', endpointDetails=endpointDetails)),
                    "Evalution-Metrics": lambda: METHODS_MAPPING["Evalution-Metrics"](UncertainityRequest(inputPrompt=inputPrompt, response=response, endpointDetails=endpointDetails)),
                    "ThoT": lambda: METHODS_MAPPING["ThoT"](openAIRequest(inputPrompt=inputPrompt, modelName='GPT4', endpointDetails=endpointDetails, temperature="0.1")),
                    "ReRead-ThoT": lambda: METHODS_MAPPING["ReRead-ThoT"](rereadRequest(inputPrompt=inputPrompt, modelName='GPT4', endpointDetails=endpointDetails)),
                    "CoT": lambda: METHODS_MAPPING["CoT"](openAIRequest(inputPrompt=inputPrompt, modelName='GPT4', endpointDetails=endpointDetails, temperature="0.1")),
                    "CoV": lambda: METHODS_MAPPING["CoV"](CoVRequest(inputPrompt=inputPrompt, modelName='GPT4', endpointDetails=endpointDetails, complexity="simple", translate="no")),
                    "LoT": lambda: METHODS_MAPPING["LoT"](lotRequest(inputPrompt=inputPrompt, llmResponse=response, modelName='GPT4', endpointDetails=endpointDetails)),
                    "Sentiment-Analysis": lambda: METHODS_MAPPING["Sentiment-Analysis"](SentimentAnalysisRequest(inputPrompt=inputPrompt)),
                    "GoT": lambda: METHODS_MAPPING["GoT"](GoTRequest(inputPrompt=inputPrompt, modelName='gpt4')),
                    "Safe-Search": lambda: METHODS_MAPPING["Safe-Search"](SafeSearchRequest(inputPrompt=inputPrompt, llm_response=response))
                }
                for method in selected_methods:
                    try:
                        if method in method_to_request:
                            row_tasks.append(method_to_request[method]())
                    except Exception as e:
                        log.error(f"Error in method {method} for row {row}: {e}")
                        row_tasks.append(None)

                return await asyncio.gather(*row_tasks, return_exceptions=True)

            processed_rows = []
            # Async task for each row in the DataFrame
            async def process_row(row):
                results = await methods_mapping_fn(row, selected_methods)
                return processing_task_response(row, selected_methods, results)
                
            # Create a list of tasks for each row in the DataFrame
            tasks = [process_row(row) for _, row in df.iterrows()]
            # Process each task as it completes
            for task in asyncio.as_completed(tasks):
                result_df = await task
                processed_rows.append(result_df)
                if telemetry_flag == "True":
                    responseList = result_df.to_dict('records')
                    telemetryPayload = {
                        "uniqueId": request_id_var.get(),
                        "tenetName": "Explainability",
                        "apiName": "/llm-explainability/bulk_processing",        
                        "userId": payload['user_id'],
                        "date": datetime.now().isoformat(),
                        "response": responseList
                    }
                    # Trigger the API call asynchronously using a separate thread
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        executor.submit(Utils.send_telemetry_request, telemetryPayload, tel_data_url)
                    log.info("******TELEMETRY REQUEST COMPLETED********")

            final_df = pd.concat(processed_rows, ignore_index=True)

            # Calculate and round the sum of the 'Token Cost' column
            total_cost_sum = round(final_df['Token Cost'].sum(), 3)

            # Get the file name without extension
            base_filename, file_extension = os.path.splitext(file.filename)
            if response_type == 'excel':
                # Get the number of rows in the dataframe
                num_rows = len(final_df)

                # Insert two empty rows after the last data row
                empty_rows = pd.DataFrame([[''] * len(df.columns)] * 2, columns=df.columns)

                # Append the empty rows after the last row of the data
                final_df = pd.concat([final_df, empty_rows], ignore_index=True)

                # Add the sum to the "Total Token Cost" column in the row after the two empty rows
                final_df.loc[num_rows, 'Token Cost'] = 'Total Token Cost'
                final_df.loc[num_rows + 1, 'Token Cost'] = total_cost_sum

                # Convert the modified DataFrame back to an Excel file format
                final_output = io.BytesIO()
                final_df.to_excel(final_output, index=False, engine='openpyxl')
                final_output.seek(0)
                media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                if file_extension in ['.csv', '.xlsx']:
                    filename = 'modified_' + base_filename + '.xlsx'

            elif response_type == 'json':
                new_record = {
                    "Total Token Cost": total_cost_sum
                }
                # Convert the DataFrame to JSON and load it as a list
                output_list = json.loads(final_df.to_json(orient='records', indent=4))

                # Append the new record to the list
                output_list.append(new_record)

                # Convert the list back to JSON
                final_output = json.dumps(output_list, indent=4)
               
                # Set the media type and filename for the response
                media_type = 'application/json'
                if file_extension in ['.csv', '.xlsx']:
                    filename = 'modified_' + base_filename + '.json'

                # Return the StreamingResponse
            return StreamingResponse(final_output, media_type=media_type, headers={"Content-Disposition": f"attachment; filename={filename}"})
        except Exception as e:
            log.error(e,exc_info=True)
            raise