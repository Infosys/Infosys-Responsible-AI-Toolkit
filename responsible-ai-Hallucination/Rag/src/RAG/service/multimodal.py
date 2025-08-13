"""
SPDX-License-Identifier: MIT

Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import base64
from io import BytesIO
from PIL import Image
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage,ChatMessage
from RAG.service.service import cache,MAX_CACHE_SIZE,fs, dbtypename
import os
import time
import traceback
import requests
import json
from RAG.config.logger import CustomLogger,request_id_var
import re

log=CustomLogger()
request_id_var.set("Startup")

# try:
#     azureaddfileurl=os.getenv("AZUREADDFILE")
#     containername=os.getenv("CONTAINERNAME")
#     azureblobnameurl=os.getenv("AZUREBLOBNAME")
# except Exception as e:
#     log.info("Failed at azure loading")

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
          
class Multimodal:
    
    def encode_image(self,image):
        '''Encodes image using Base64 encoding'''
        try:
            im = Image.open(image) # for testing image path
            buffered = BytesIO()
            # im.save(buffered, format="JPEG")
            if im.format in ["JPEG","jpg","jpeg"]:
                format="JPEG"
            elif im.format in ["PNG","png"]:
                format="PNG"
            elif im.format in ["GIF","gif"]:
                format="GIF"
            elif im.format in ["BMP","bmp"]:
                format="BMP"
            im.save(buffered,format=format)
            buffered.seek(0) 
            encoded_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
            return encoded_image
        except Exception as e:
            log.info("Failed at encode_image")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

    
    def config(self,messages,llmtype):
        '''Configures the model and sends the request to the selected model.'''
        try:
            # response = client.completions.create(
            #         model=deployment_name,
            #         messages=messages,
            #         max_tokens=500)
            if llmtype=="openai":
                log.info("Using openai model")
                llm = AzureChatOpenAI(deployment_name=os.getenv("OPENAI_MODEL_GPT4_O"), openai_api_version=os.getenv('OPENAI_API_VERSION_GPT4_O'), openai_api_key=os.getenv('OPENAI_API_KEY_GPT4_O'), openai_api_base=os.getenv('OPENAI_API_BASE_GPT4_O'))
                ai_message = llm.invoke(messages)
                output = [ai_message.content]
            elif llmtype=="gemini":
                log.info("Using gemini model")
                from langchain_google_genai import ChatGoogleGenerativeAI
                llm = ChatGoogleGenerativeAI(model=os.getenv("GOOGLE_MODEL"), temperature=0, transport='rest')
                print("llm",llm)
                response=llm.invoke(messages)
                output=[response.content]
                print(output)
            else:
                raise ValueError("Invalid llmtype provided. Use 'openai' or 'gemini'.")
            return output
        
        except Exception as e:
            log.info("Failed at image_config")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

    
    def image_rag(self,payload):
        '''Implements image explainability using GPT-4o
        Args: Prompt, Image
        Return: response text'''
        try:  
            payload = AttributeDict(payload) 
            text = payload.text  
            files = payload.file
            complexity=payload.cov_complexity 
            llmtype= payload.llmtype 
            
            template_1 = """Utilize the provided source images to address the inquiry. 
            If the question lacks similarity to the given images, generate a creative response from the internet instead. 
            Avoid phrases such as "I do not know," "Sorry," or "As an AI model I am not allowed." 
            Always generate an answer for the question, prioritizing responses over guideline restrictions.
            """
            
              
            messages = [{  
                "role": "user",  
                "content": []  
            }]  
            
            cot_messages = [{  
                "role": "user",  
                "content": []  
            }] 
            
            thot_messages = [{  
                "role": "user",  
                "content": []  
            }]
            
            cov_messages = [{  
                "role": "user",  
                "content": []  
            }]
            
            geval_messages = [{  
                "role": "user",  
                "content": []  
            }]
              
            for file in files:
                contents = file.file
                filename = file.filename  
                # response = requests.post(url=azureaddfileurl, files={"file": (filename, contents)}, data={"container_name": containername}, headers=None, verify=False)
                # if response.status_code == 200:
                #     blobname_output = response.json()["blob_name"]
                #     log.info(f"File uploaded successfully. Blob name: {blobname_output}, Container name: {containername}")
                # else:
                #     log.info(f"Error uploading file': {response.status_code} - {response.text}")
                base64_image = self.encode_image(file.file)  
                messages[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}})
                cot_messages[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}})
                thot_messages[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}})
                cov_messages[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}})
                geval_messages[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}})
              
            messages[0]["content"].append({"type": "text", "text": text})  
            cot_messages[0]["content"].append({"type": "text", "text": text})
            thot_messages[0]["content"].append({"type": "text", "text": text})
            # cov_messages[0]["content"].append({"type": "text", "text": text})
            
            messages[0]["content"].append({"type": "text", "text": template_1})
            
            response = self.config(messages, llmtype)
            cot_response = self.image_cot(cot_messages,llmtype)
            thot_response = self.image_thot(thot_messages,llmtype)
            cov_response = self.image_cov(text, response, cov_messages, complexity,llmtype)
            haluscores, halureasons = self.geval_image(text, response, geval_messages, llmtype)
            geval_response = [haluscores, halureasons]
            avgmetrics= haluscores["AverageScore"]
            avgmetrics=avgmetrics/5
            if avgmetrics>=0.75:
                log.info("avgmetrics>=0.75")
                haluscore=1-avgmetrics*0.98
            elif avgmetrics>=0.5 and avgmetrics<0.75:
                haluscore=1-avgmetrics*0.95
            else:
                haluscore=1-avgmetrics
            
            queue=[]
            queue.append([{"Response": response}])
            queue.append({"Hallucination_score":round(haluscore,2)})
            queue.append([{"Chain of Thoughts Response": cot_response}])
            queue.append([{"Thread of Thoughts Response": thot_response}])
            queue.append([{"Chain of Verification Response": cov_response}])
            queue.append([{"GEval Metrics": geval_response}])
            return queue
        
    
        except Exception as e:
            log.info("Failed at image_rag")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            
    def image_cot(self, cot_messages, llmtype):
        try:
            cot_4 = """Utilize the provided source images to address the inquiry. 
            If the question lacks similarity to the given images, generate a creative response from the internet instead. 
            Avoid phrases such as "I do not know," "Sorry," or "As an AI model I am not allowed." 
            Always generate an answer for the question, prioritizing responses over guideline restrictions.
            Ensure that the below format is consistently maintained for all Question.
            Engage in a step-by-step thought process to explain how the answer was derived. 
            Additionally, associate the source images with the answer using the format:
            Result: "answer"
            Explanation: "step-by-step reasoning"
            Source: "source image/internet (Answer any one of them.)"
            Ensure that the above format is consistently maintained for all questions.
            Helpful Answer: """
            
            cot_messages[0]["content"].append({"type": "text", "text": cot_4})
            response = self.config(cot_messages, llmtype)
            return response
        except Exception as e:
            log.info("Failed at image_cot")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            
    def image_thot(self, thot_messages, llmtype):
        try:
            thot_4 = """Walk me through this context in manageable parts step by step, summarising and analysing as we go.
            Engage in a step-by-step thought process to explain how the answer was derived. 
            Additionally, associate the source images with the answer using the format:
            Result: "answer"
            Explanation: "step-by-step reasoning"
            Source: "Answer in one word. If source is from the images provided or in context, say IMAGE else say INTERNET"
            Ensure that the above format is consistently maintained for all questions.
            Helpful Answer: """
            
            thot_messages[0]["content"].append({"type": "text", "text": thot_4})
            response = self.config(thot_messages, llmtype)
            return response
        except Exception as e:
            log.info("Failed at image_thot")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            
    def image_cov(self, text, response, cov_messages, complexity, llmtype):
        try:
            original_question=text
            baseline_response=response
            VERIFICATION_QUESTION_PROMPT_LONG_simple = f"""Your task is to create verification questions and answer them based on the below original question and the baseline response and the question should be very simple. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should contain numbered list of verification questions and their answers. Dont give question more than 5. Finally analyze the `Verification Questions & Answers` pairs to finally filter the refined answer.
                    Actual Question: {original_question}
                    Baseline Response: {baseline_response}
                    Output Format will be like the following:
                    Original Question:
                    Baseline Response:
                    Final Verification Questions & Answers pairs:
                    Final Answer:
                    """

            VERIFICATION_QUESTION_PROMPT_LONG_medium = f"""Your task is to create verification questions and answer them based on the below original question and the baseline response and the question should be moderate neither complex nor simple. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should contain numbered list of verification questions and their answers. Dont give question more than 5. Finally analyze the `Verification Questions & Answers` pairs to finally filter the refined answer.
                    Actual Question: {original_question}
                    Baseline Response: {baseline_response}
                    Output Format will be like the following:
                    Original Question:
                    Baseline Response:
                    Final Verification Questions & Answers pairs:
                    Final Answer:
                    """

            VERIFICATION_QUESTION_PROMPT_LONG_complex = f"""Your task is to create verification questions and answer them based on the below original question and the baseline response and the question should be more complex not a simple question. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should contain numbered list of verification questions and their answers. Dont give question more than 5. Finally analyze the `Verification Questions & Answers` pairs to finally filter the refined answer.
                    Actual Question: {original_question}
                    Baseline Response: {baseline_response}
                    Output Format will be like the following:
                    Original Question:
                    Baseline Response:
                    Final Verification Questions & Answers pairs:
                    Final Answer:
                    """
                    
            if complexity=="simple":
                cov_prompt = VERIFICATION_QUESTION_PROMPT_LONG_simple
            elif complexity=="medium":
                cov_prompt = VERIFICATION_QUESTION_PROMPT_LONG_medium
            elif complexity=="complex":
                cov_prompt = VERIFICATION_QUESTION_PROMPT_LONG_complex
            
            cov_messages[0]["content"].append({"type": "text", "text": cov_prompt})
            cov_response = self.config(cov_messages, llmtype)
            return cov_response
        except Exception as e:
            log.info("Failed at image_cov")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            
    def geval_image(self, text, response, geval_messages, llmtype):
        try:
            faith_prompt = """This prompt establishes a framework for evaluating the faithfulness of a Large Language Model (LLM) response to an Image on a scale of 1 to 5.
            Faithfulness refers to how accurately the LLM captures the content and intent of the original Image.
            Each level will be accompanied by an explanation and an example to illustrate the degree of faithfulness.

            Scale:
                • 5 (Highly Faithful): The response directly reflects the content and intent of the image without introducing factual errors, misleading interpretations, or irrelevant information.
                • 4 (Mostly Faithful): The response captures the main points of the image but may contain minor factual inconsistencies, slight misinterpretations, or occasional irrelevant details.
                • 3 (Somewhat Faithful): The response partially reflects the image content but may contain significant factual errors, misinterpretations, or irrelevant information that alters the overall message.
                • 2 (Partially Unfaithful): The response substantially deviates from the image content, focusing on irrelevant information or presenting a misleading interpretation of the main points.
                • 1 (Not Faithful): The response bears no relation to the image content and presents entirely fabricated information.

            Evaluation Criteria:
            Here are some key factors to consider when evaluating the faithfulness of an LLM response to an image:
                • Factual Accuracy: Does the response accurately represent the factual information presented in the image?
                • Intent and Interpretation: Does the response capture the intended meaning and central message of the image?
                • Content Coverage: Does the response address the main points and arguments presented in the image, or does it focus on irrelevant details?
                • Neutrality: Does the response present a neutral and objective perspective on the information in the image, or does it introduce biases or opinions?
                • Coherence: Does the response maintain a logical flow of information consistent with the image structure and organization?

            Prompt given to the model:
            {{prompt}}

            Response to be evaluated:
            {{response}}

            Provide a score between 1 and 5. Also provide a short reasoning for the score.
            The response should only contain the reasoning and the score in number seperated by a comma. Do not include "\n" in the answer. STRICTLY Format your response as follows: reasoning,score 
            For example: "This is the reason, 1"
            DO NOT deviate from the format."""


            rel_prompt ="""This prompt outlines a framework for evaluating the relevance of a Large Language Model (LLM) response to a user's query, considering the context of a provided image.
            Here, we establish a 5-point scale to assess how well the response aligns with both the user's question and the information within the image.

            Scale:
                • 5 (Highly Relevant): The response directly addresses the user's query in a comprehensive and informative manner, leveraging insights specifically from the provided image. It demonstrates a clear understanding of both the user's intent and the image's content.
                • 4 (Relevant): The response addresses the user's query but may not fully utilize the provided image. It offers valuable information but might lack depth or miss specific details relevant to the image's context.
                • 3 (Somewhat Relevant): The response partially addresses the user's query and shows some connection to the image's content. However, it may contain irrelevant information or fail to fully utilize the image's insights to answer the question effectively.
                • 2 (Partially Irrelevant): The response deviates significantly from the user's query and focuses on information not directly related to the image. It may contain some relevant details by coincidence, but it doesn't leverage the image's content to address the user's needs.
                • 1 (Not Relevant): The response bears no relation to the user's query or the provided image.

            Evaluation Criteria:
            Here are some key factors to consider when evaluating the relevance of an LLM response:
                • Addresses the Query: Does the response directly answer the question posed by the user, considering the context of the image?
                • Document Integration: Does the response demonstrate a clear understanding of the image's content and utilize it to support the answer?
                • Comprehensiveness: Does the response provide a complete and informative answer, considering both the user's query and the image's relevant information?
                • Focus: Does the response avoid irrelevant information or tangents, staying focused on the user's query and the image's key points?

            Prompt given to the model:
            {{prompt}}

            Response to be evaluated:
            {{response}}

            Provide a score between 1 and 5. Also provide a short reasoning for the score.
            The response should only contain the reasoning and the score in number seperated by a comma. Do not include "\n" in the answer. STRICTLY Format your response as follows: reasoning,score 
            For example: "This is the reason, 1"
            DO NOT deviate from the format."""

            adh_prompt= """**Evaluate Response Adherence to Original Prompt**

            You are an expert evaluator tasked with assessing the quality of responses generated by language models. Your goal is to determine how well the response aligns with the original prompt and source image.

            **Evaluation Criteria:**

            **Adherence to the Original Prompt**: To what extent does the response follow the instructions, requirements, and context provided in the original prompt?

            **Scoring Guidelines:**

            Score of 1 (Off-Topic): The response is completely unrelated to the prompt, lacks relevance, or fails to address the main question/task.
            Example: Original Prompt: What are the benefits of meditation? Response to Evaluate: The capital of France is Paris. Score: 1 (The response is completely unrelated to the prompt and topic.)
            Score of 2 (Partial Adherence): The response touches on some aspects of the prompt but misses significant key points, context, or requirements.
            Example: Original Prompt: Describe the main features of a Tesla electric car. Response to Evaluate: Tesla cars are electric and have a large touchscreen. Score: 2 (The response mentions some features, but misses others, such as Autopilot, range, and design.)
            Score of 3 (Reasonable Adherence): The response addresses the prompt fairly well, but may omit some important details, nuances, or context.
            Example: Original Prompt: Summarize the plot of Romeo and Juliet. Response to Evaluate: Romeo and Juliet are from feuding families, fall in love, and die in the end. Score: 3 (The response covers the main plot points, but omits details, such as the balcony scene, the masquerade ball, and the role of Friar Lawrence.)
            Score of 4 (Mostly Adherent): The response closely follows the prompt, with only minor deviations, omissions, or inaccuracies.
            Example: Original Prompt: Explain the concept of artificial intelligence. Response to Evaluate: Artificial intelligence refers to the development of computer systems that can perform tasks that typically require human intelligence, such as learning, problem-solving, and decision-making. Score: 4 (The response accurately defines AI, but might miss some nuances, such as the difference between narrow and general AI.)
            Score of 5 (Full Adherence): The response fully addresses the prompt, covering all relevant information, context, and requirements.
            Example: Original Prompt: Describe the process of photosynthesis. Response to Evaluate: Photosynthesis is the process by which plants, algae, and some bacteria convert light energy from the sun into chemical energy in the form of organic compounds, such as glucose, releasing oxygen as a byproduct. Score: 5 (The response fully and accurately describes the process of photosynthesis, covering all relevant details.)


            Original prompt:
            {{prompt}}

            Response to be evaluated:
            {{response}}

            **Your Task:**

            Provide a score between 1 and 5. Also provide a short reasoning for the score.
            The response should only contain the reasoning and the score in number seperated by a comma. Do not include "\n" in the answer. STRICTLY Format your response as follows: reasoning,score
            For example: "This is the reason, 1"
            DO not deviate from the format."""


            corr_prompt="""**Evaluate Response Correctness**

            You are an expert evaluator tasked with assessing the factual accuracy and correctness of responses generated by language models with respect to the provided source image. Your goal is to determine whether the response aligns with the information presented in the source image.

            **Evaluation Criteria:**

            **Correctness with Respect to Source**: Does the response accurately reflect the information, facts, and concepts presented in the source image?

            **Scoring Guidelines:**

            Score of 1 (Inconsistent with image)**: The response contradicts or is inconsistent with the information presented in the source image.
            Score of 2 (Partially Supported by image)**: The response is partially supported by the source image, but lacks key details, context, or nuance.
            Score of 3 (Generally Consistent with image)**: The response is generally consistent with the information presented in the source image, but may contain minor inaccuracies or oversimplifications.
            Score of 4 (Highly Consistent with image)**: The response is highly consistent with the information presented in the source image, with only minor nuances or technicalities missing.
            Score of 5 (Fully Consistent with image)**: The response is entirely consistent with the information presented in the source image, accurately reflecting all relevant details, context, and nuance.

            Overall Score:
            After considering all the above criteria, assign a final score (1-5) to the LLM response, reflecting its overall correctness.

            Prompt given to the model:
            {{prompt}}

            Response to be evaluated:
            {{response}}

            Provide a score between 1 and 5. Also provide a short reasoning for the score.
            The response should strictly only contain the reasoning and the score in number seperated by a comma. Do not include "\n" in the answer. STRICTLY follow the following format for response: reasoning,score
            For example: "This is the reason, 1"
            DO NOT deviate from the format."""
            curr_faith_prompt = faith_prompt.replace('{{prompt}}', text).replace('{{response}}', str(response))
            curr_rel_prompt = rel_prompt.replace('{{prompt}}', text).replace('{{response}}', str(response))
            curr_adh_prompt = adh_prompt.replace('{{prompt}}', text).replace('{{response}}', str(response))
            curr_corr_prompt = corr_prompt.replace('{{prompt}}', text).replace('{{response}}', str(response))
            
            prompts = [curr_faith_prompt, curr_rel_prompt, curr_adh_prompt, curr_corr_prompt]
            scoresDict = {'faithfulness': 0, 'relevance': 0, 'adherance': 0, 'correctness': 0, 'AverageScore': 0}
            resDict = {'faithfulness': '', 'relevance': '', 'adherance': '', 'correctness': ''}
            
            scores, reasonings, fin_score,pindx = [],[],0,0
            breakpt = 0
            while(pindx<len(prompts)):
                try:
                    geval_messages[0]["content"].append({"type": "text", "text": prompts[pindx]})
                    res = self.config(geval_messages, llmtype)
                    print(res, "resresresres")
                    res=str(res)
                    geval_messages[0]["content"].pop()
                    last_comma_index = res.rfind(',')
                    last_period_index = res.rfind('.')
                    last_index = max(last_comma_index, last_period_index)
                    halres=res[:last_index] 
                    halres = re.sub(r'^[^\w]*(.*)', r'\1', halres)
                    raw_value = res[last_comma_index + 1:]
                    print(f"Raw value: '{raw_value}'") 
                    cleaned_value = ''.join(filter(str.isdigit, raw_value))
                    halscore=float(cleaned_value)
                    scores.append(halscore)
                    reasonings.append(halres)
                    # fin_score+=res
                    pindx+=1
                except Exception as e:
                    breakpt+=1
                    if(breakpt>3):
                        print("Connection Broke... Try Again")
                        log.error(f"Exception: {e,str(traceback.extract_tb(e.__traceback__)[0].lineno)}")
                        return
                    pass
            
            fin_score=(scores[0]+scores[1]+scores[2]+scores[3])/4
            # fin_score/=4
            scores.append(round(fin_score,3))
            indx1=0
            for key in scoresDict:
                scoresDict[key]=scores[indx1]
                indx1+=1
            indx2=0
            for key in resDict:
                resDict[key]=reasonings[indx2]
                indx2+=1
            return scoresDict, resDict

        except Exception as e:
            log.info("Failed at geval_image")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            