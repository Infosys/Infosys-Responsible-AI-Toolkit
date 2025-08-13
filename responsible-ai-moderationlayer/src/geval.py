'''
Copyright 2024 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import openai
from openai import AzureOpenAI
import time
import os
from config.logger import CustomLogger,request_id_var
log = CustomLogger()
import traceback
try:
    openai.verify_ssl_certs = False
    request_id_var.set("Startup")
    deployment_name=os.environ.get("OPENAI_MODEL_GPT4")

    openai.api_type = os.environ.get("OPENAI_API_TYPE")
    openai.api_base = os.environ.get("OPENAI_API_BASE_GPT4")
    openai.api_key = os.environ.get("OPENAI_API_KEY_GPT4")
    openai.api_version = os.environ.get("OPENAI_API_VERSION_GPT4")
except Exception as e:
    log.error("Failed at Completion Function")
    log.error(f"Exception: {e,str(traceback.extract_tb(e.__traceback__)[0].lineno)}")


coh_prompt = """You will be given one summary written for a news article.
Your task is to rate the summary on one metric.
Please make sure you read and understand these instructions carefully. Please keep this document open while reviewing, and refer to it as needed.

Evaluation Criteria:
Coherence (1-5) - the collective quality of all sentences. We align this dimension with the DUC quality question of structure and coherence whereby "the summary should be well-structured and well-organized. The summary should not just be a heap of related information, but should build from sentence to a coherent body of information about a topic."

Evaluation Steps:
1. Read the news article carefully and identify the main topic and key points.
2. Read the summary and compare it to the news article. Check if the summary covers the main topic and key points of the news article, and if it presents them in a clear and logical order.
3. Assign a score for coherence on a scale of 1 to 5, where 1 is the lowest and 5 is the highest based on the Evaluation Criteria.


Example:
Source Text:
{{Document}}

Summary:
{{Summary}}

Evaluation Form (scores ONLY):
- Coherence (1-5):"""

con_prompt = """You will be given a news article. You will then be given one summary written for this article.
Your task is to rate the summary on one metric.
Please make sure you read and understand these instructions carefully. Please keep this document open while reviewing, and refer to it as needed.

Evaluation Criteria:
Consistency (1-5) - the factual alignment between the summary and the summarized source. A factually consistent summary contains only statements that are entailed by the source document. Annotators were also asked to penalize summaries that contained hallucinated facts. 

Evaluation Steps:
1. Read the news article carefully and identify the main facts and details it presents.
2. Read the summary and compare it to the article. Check if the summary contains any factual errors that are not supported by the article.
3. Assign a score for consistency based on the Evaluation Criteria.


Example:
Source Text: 
{{Document}}

Summary: 
{{Summary}}

Evaluation Form (scores ONLY):
- Consistency (1-5):"""

flu_prompt = """You will be given one summary written for a news article.
Your task is to rate the summary on one metric.
Please make sure you read and understand these instructions carefully. Please keep this document open while reviewing, and refer to it as needed.

Evaluation Criteria:
Fluency (1-5): the quality of the summary in terms of grammar, spelling, punctuation, word choice, and sentence structure.
- 1: Poor. The summary has many errors that make it hard to understand or sound unnatural.
- 2: Fair. The summary has some errors that affect the clarity or smoothness of the text, but the main points are still comprehensible.
- 3: Good. The summary has few or no errors and is easy to read and follow.

Example:
Summary:
{{Summary}}

Evaluation Form (scores ONLY):
- Fluency (1-5):"""

rel_prompt = """You will be given one summary written for a news article.
Your task is to rate the summary on one metric.
Please make sure you read and understand these instructions carefully. Please keep this document open while reviewing, and refer to it as needed.

Evaluation Criteria:
Relevance (1-5) - selection of important content from the source. The summary should include only important information from the source document. Annotators were instructed to penalize summaries which contained redundancies and excess information.

Evaluation Steps:
1. Read the summary and the source document carefully.
2. Compare the summary to the source document and identify the main points of the article.
3. Assess how well the summary covers the main points of the article, and how much irrelevant or redundant information it contains.
4. Assign a relevance score from 1 to 5.

Example:
Source Text:
{{Document}}

Summary:
{{Summary}}

Evaluation Form (scores ONLY):
- Relevance (1-5):"""


def call_openai_model(prompt, model, temperature):
    response = None
    strt_time = time.perf_counter()
    if model == "gpt3":
        deployment_name = os.getenv("OPENAI_MODEL_GPT3")
        openai.api_base = os.environ.get("OPENAI_API_BASE_GPT3")
        openai.api_key = os.environ.get("OPENAI_API_KEY_GPT3")
        openai.api_version = os.environ.get("OPENAI_API_VERSION_GPT3")
    else:
        deployment_name = os.getenv("OPENAI_MODEL_GPT4")
        openai.api_base = os.environ.get("OPENAI_API_BASE_GPT4")
        openai.api_key = os.environ.get("OPENAI_API_KEY_GPT4")
        openai.api_version = os.environ.get("OPENAI_API_VERSION_GPT4")
    # print("deployment_name in geval ",deployment_name)

    while response is None:
        try:
            messages=[
                    {"role": "system", "content": "You are a helpful assistant. The response should contain only score(one digit number). Nothing Else."},
                    {"role": "user", "content": prompt},
                ]
            client = AzureOpenAI(api_key=openai.api_key, 
                                 azure_endpoint=openai.api_base,
                                 api_version=openai.api_version)
            response = client.chat.completions.create(
                model=deployment_name,
                messages = messages,
                temperature=temperature
                )
            
            '''
            response = openai.ChatCompletion.create(
                engine=deployment_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. The response should contain only score(one digit number). Nothing Else."},
                    {"role": "user", "content": prompt},
                ],
                temperature = temperature
                )
            '''
        except Exception as e:
            log.error('failed at call_openaimodel')
            log.error(f"Exception: {e,str(traceback.extract_tb(e.__traceback__)[0].lineno)}")
            log.info('Retrying...')
            time.sleep(2)
        end_time = time.perf_counter()
        if(end_time-strt_time>10):
            raise Exception("Error")
    try:
        output = response.choices[0].message.content
    except Exception:
        output = 'do not have reponse from chatgpt'
    return output 

def gEval(payload,headers):
    try:
        st=time.time()
        doc_text=payload.text
        sum_text=payload.summary
        curr_coh_prompt = coh_prompt.replace('{{Document}}', doc_text).replace('{{Summary}}', sum_text)
        curr_con_prompt = con_prompt.replace('{{Document}}', doc_text).replace('{{Summary}}', sum_text)
        curr_flu_prompt = flu_prompt.replace('{{Document}}', doc_text).replace('{{Summary}}', sum_text)
        curr_rel_prompt = rel_prompt.replace('{{Document}}', doc_text).replace('{{Summary}}', sum_text)
        
        prompts = [curr_coh_prompt, curr_con_prompt, curr_flu_prompt, curr_rel_prompt]
        scoresDict = {'coherence': 0, 'consistency': 0, 'fluency': 0, 'relevance': 0, 'FinalScore': 0}

        scores, fin_score,pindx = [],0,0
        breakpt = 0
        while(pindx<len(prompts)):
            try:
                res = int(call_openai_model(prompts[pindx], payload.model_name, 2.0)[0])                
                scores.append(res)
                # fin_score+=res
                pindx+=1
            except Exception as e:
                breakpt+=1
                if(breakpt>3):
                    print("Connection Broke... Try Again")
                    return
                pass
        fin_score=round((scores[0]+scores[1]+0.5*scores[2]+scores[3])/3.5,3)
        # fin_score/=4
        scores.append(fin_score)
        indx=0
        for key in scoresDict:
            scoresDict[key]=scores[indx]
            indx+=1
        scoresDict["timetaken"]=str(round(time.time()-st,3))+"s"
        return scoresDict
    except Exception as e:
        log.error("Failed at geval")
        log.error(f"Exception: {e,str(traceback.extract_tb(e.__traceback__)[0].lineno)}")