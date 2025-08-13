'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import os
import re
import copy
import time
from config.logger import CustomLogger, request_id_var
import uuid
from datetime import datetime
import json
import requests
import asyncio
import threading
import openai
import numpy as np
import nltk
import traceback
import urllib3
from mapper.mapper import *
from dotenv import load_dotenv
from better_profanity import profanity
import aiohttp
import ssl
from smoothLLm import SMOOTHLLM
from telemetry import telemetry
from bergeron import  Bergeron
from dao.AdminDb import Results
from translate import Translate
from openai import AzureOpenAI
import demoji
import string 
import regex
import grapheme
import sys
from utilities.lruCaching import *
from utilities.utility_methods import *
import boto3
from botocore.exceptions import ClientError
import Llama_auth
import google.generativeai as genai
from fkscore import fkscore

log=CustomLogger()
request_id_var.set("Startup")
urllib3.disable_warnings()
startupFlag=True
global log_dict
log_dict={}
contentType = os.getenv("CONTENTTYPE")
aicloud_access_token=None
token_expiration=0

verify_ssl = os.getenv("VERIFY_SSL")
sslv={"False":False,"True":True,"None":True}

def handle_object(obj):
    return vars(obj) 

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


try:
    device = "cuda"
    load_dotenv()
    jailbreakurl=os.getenv("JAILBREAKMODEL")
    promptInjectionurl=os.getenv("PROMPTINJECTIONMODEL")
    detoxifyurl=os.getenv("DETOXIFYMODEL")
    mpnetsimilarityurl=os.getenv("SIMILARITYMODEL")
    topicurl=os.getenv("RESTRICTEDMODEL")
    privacyurl=os.getenv("PRIVACY")
    sentimenturl=os.getenv("SENTIMENT")
    invisibletexturl=os.getenv("INVISIBLETEXT")
    gibberishurl=os.getenv("GIBBERISH")
    bancodeurl=os.getenv("BANCODE")

    tel_env=os.getenv("TELEMETRY_ENVIRONMENT")
    telemetryurl = os.getenv("TELEMETRY_PATH") 
    coupledtelemetryurl=os.getenv("COUPLEDTELEMETRYPATH")
    EXE_CREATION = os.getenv("EXE_CREATION")
    cache_ttl = int(os.getenv("CACHE_TTL"))
    cache_size = int(os.getenv("CACHE_SIZE"))

    promptInjectionraiurl=os.getenv("PROMPTINJECTIONMODELRAI")
    jailbreakraiurl=os.getenv("JAILBREAKMODELRAI")
    detoxifyraiurl=os.getenv("DETOXIFYMODELRAI")
    topicraiurl=os.getenv("RESTRICTEDMODELRAI")
    mpnetsimilarityraiurl=os.getenv("SIMILARITYMODELRAI")
    privacyraiurl=os.getenv("PRIVACYRAI")

    target_env=os.getenv("TARGETENVIRONMENT")
   
    cache_flag = os.getenv("CACHE_FLAG")

    ## FOR NORMAL APP RUNNING
    if(EXE_CREATION == "True"):
        # Get the base path (this will be the path to the executable when running the bundled app)
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Construct the absolute path to the nltk_data directory
    nltk_path = os.path.join(base_path, 'data','nltk_data')
    nltk.data.path.append(nltk_path) # Append the nltk_path to the nltk data path
    
    jailbreak_embeddings_path = os.path.join(base_path, 'data/jailbreak_embeddings.json')
    refusal_embeddings_path = os.path.join(base_path, 'data/refusal_embeddings.json')
    topic_embeddings_path = os.path.join(base_path, 'data/topic_embeddings.json')
    orgpolicy_embeddings_path = os.path.join(base_path, 'data/orgpolicy_embeddings.json')
    inappropriate_emoji_path = os.path.join(base_path, 'data/inappropriate_emoji.json')
    moderation_time_json = os.path.join(base_path, 'data/moderationtime.json')

    with open(jailbreak_embeddings_path, "r") as file:
        json_data = file.read()
        jailbreak_embeddings = json.loads(json_data)
    with open(refusal_embeddings_path, "r") as file:
        json_data = file.read()
        refusal_embeddings = json.loads(json_data)
    with open(topic_embeddings_path, "r") as file:
        json_data = file.read()
        topic_embeddings = json.loads(json_data)
    with open(orgpolicy_embeddings_path, "r") as file:
        json_data = file.read()
        orgpolicy_embeddings = json.loads(json_data)
    
    #load the json file for imappropriate emojis defined
    with open(inappropriate_emoji_path,  encoding="utf-8",mode="r") as emoji_file:
        data=emoji_file.read()
        emoji_data=json.loads(data)
    


except Exception as e:
    log.error(str(traceback.extract_tb(e.__traceback__)[0].lineno))
    log.info(f"Exception: {e}")
    



async def post_request(url, data=None, json=None, headers=None, verify=sslv[verify_ssl]):
  """
  Performs a POST request using aiohttp.

  Args:
      url (str): The URL of the endpoint to send the request to.
      data (dict, optional): A dictionary of data to send as form-encoded data. Defaults to None.
      json (dict, optional): A dictionary of data to be JSON-encoded and sent in the request body. Defaults to None.
      headers (dict, optional): A dictionary of headers to include in the request. Defaults to None.

  Returns:
      aiohttp.ClientResponse: The response object from the server.
  """
  if(headers["Authorization"]==None):
      headers["Authorization"]="None"

  ssl_context = ssl.create_default_context()
  ssl_context.check_hostname = False
  ssl_context.verify_mode = ssl.CERT_NONE
  
  async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
    async with session.post(url, data=data, json=json, headers=headers) as response:
      
      response.raise_for_status() # Raise an exception for non-2xx status codes
      
      return await response.read()

dict_timecheck={"requestModeration": 
                    {"Prompt Injection Check": "0s", 
                    "Jailbreak Check": "0s", 
                    "Toxicity Check": "0s", 
                    "Privacy Check": "0s", 
                    "Profanity Check": "0s", 
                    "Refusal Check": "0s",
                    "Restricted Topic Check": "0s",
                    "Text Quality Check": "0s",
                    "Custom Theme Check": "0s",
                    "Random Noise Check": "0s", 
                    "Advanced Jailbreak Check": "0s"}, 
                "responseModeration": 
                    {"Toxicity Check": "0s", 
                    "Privacy Check": "0s", 
                    "Profanity Check": "0s", 
                    "Refusal Check": "0s", 
                    "Text Relevance Check": "0s", 
                    "Text Quality Check": "0s",
                    "Custom Theme Check": "0s"}, 
                "OpenAIInteractionTime": "0s",
                "translate":"0s",
                }

dictcheck={"Prompt Injection Check": "0s", 
           "Jailbreak Check": "0s", 
           "Toxicity Check": "0s", 
           "Privacy Check": "0s", 
           "Profanity Check": "0s", 
           "Refusal Check": "0s",
           "Restricted Topic Check": "0s",
           "Text Quality Check": "0s",
           "Custom Theme Check": "0s"}

moderation_timecheck = {}
# def writejson(dict_timecheck):            
#     json_object = json.dumps(dict_timecheck)
#     with open("data/moderationtime.json", "w") as outfile:
#         outfile.write(json_object)


# PATH MODIFIED FOR EXE
def writejson(dict_timecheck):            
    json_object = json.dumps(dict_timecheck)

    if(EXE_CREATION == "True"):
        # # Get the directory of the .exe file
        # exe_dir = os.path.dirname(sys.executable)
        # Create the path for the json file
        json_path = moderation_time_json
    else:
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Create the path for the json file
        json_path = os.path.join(script_dir, "data/moderationtime.json")

    with open(json_path, "w") as outfile:
        outfile.write(json_object)



# PATH MODIFIED FOR EXE
def writeDecoupledTime(timecheck):            
    json_object = json.dumps(timecheck)

    if(EXE_CREATION == "True"):
        # # Get the directory of the .exe file
        # exe_dir = os.path.dirname(sys.executable)
        # Create the path for the json file
        json_path = os.path.join(base_path, "data/decoupledModerationtime.json")
    else:
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Create the path for the json file
        json_path = os.path.join(script_dir, "data/decoupledModerationtime.json")

    with open(json_path, "w") as outfile:
        outfile.write(json_object)

###########################################

class PromptInjection:
    async def classify_text(self, text,headers):
        
        try:
            #response with azure moderation model endpoints
            if target_env=="azure":
                log.info("Using azure prompt injection model endpoint")
                output=await post_request(url=promptInjectionurl,json={"text": text},headers=headers)
                output=json.loads(output.decode('utf-8'))
                modeltime = output[2]["time_taken"]
                if output[0]=='LEGIT':
                    injectionscore = 1 - output[1]
                else:
                    injectionscore = output[1]
            #response with aicloud moderation model endpoints
            elif target_env=="aicloud":
                log.info("Using aicloud prompt injection model endpoint")
                st=time.time()
                output=await post_request(url=promptInjectionraiurl,json={"inputs": [text]},headers=headers)
                et=time.time()
                output=json.loads(output.decode('utf-8'))
                modeltime = str(round(st-et,3))+"s"
                if output[0]['label']=='LEGIT':
                    injectionscore = 1 - output[0]['score']
                else:
                    injectionscore = output[0]['score']

            return round(injectionscore,3),modeltime
        except Exception as e:
            log.error("Error occured in PromptInjection")
            line_number = traceback.extract_tb(e.__traceback__)[0].lineno
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at PromptInjection model call"})
            log.error(f"Exception: {line_number,e}")

class SentimentAnalysis:
    async def classify_text(self, text,headers):
        try:
            log.info("Using sentiment endpoint")
            output=await post_request(url=sentimenturl,json={"text": text},headers=headers)
            output=json.loads(output.decode('utf-8'))
            log.info(f"output : {output}")
            return output
        except Exception as e:
            log.error("Error occured in Sentiment Check")
            line_number = traceback.extract_tb(e.__traceback__)[0].lineno
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at Sentiment Check"})
            log.error(f"Exception: {line_number,e}")



class InvisibleText:
    async def find_invisible_chars(self, text,banned_categories,headers):
        try:
            log.info("Using invisibletext endpoint")
            output=await post_request(url=invisibletexturl,json={"text": text,"banned_categories":banned_categories},headers=headers)
            output=json.loads(output.decode('utf-8'))
            log.info(f"output : {output}")
            return output
        except Exception as e:
            log.error("Error occured in Invisible Text Check")
            line_number = traceback.extract_tb(e.__traceback__)[0].lineno
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at Invisible Text Check"})
            log.error(f"Exception: {line_number,e}")

class Gibberish:
    async def detect_gibberish(self, text,gibberish_labels,headers):
        try:
            log.info("Using gibberish endpoint")
            output=await post_request(url=gibberishurl,json={"text": text,"labels":gibberish_labels},headers=headers)
            output=json.loads(output.decode('utf-8'))
            log.info(f"output : {output}")
            return output
        except Exception as e:
            log.error("Error occured in gibberish Check")
            line_number = traceback.extract_tb(e.__traceback__)[0].lineno
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at gibberish Check"})
            log.error(f"Exception: {line_number,e}")


class BanCode:
    async def ban_code(self, text,headers):
        try:
            log.info("Using ban code endpoint")
            output=await post_request(url=bancodeurl,json={"text": text},headers=headers)
            output=json.loads(output.decode('utf-8'))
            log.info(f"output : {output}")
            return output
        except Exception as e:
            log.error("Error occured in BanCode Check")
            line_number = traceback.extract_tb(e.__traceback__)[0].lineno
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at BanCode Check"})
            log.error(f"Exception: {line_number,e}")


def text_quality(text):
    f = fkscore(text)
    ease_score = f.score['readability']
    grade_score = f.score['read_grade']
    return ease_score,grade_score

class promptResponse:
    async def promptResponseSimilarity (self,prompt,output_text,headers):
        try:
            if target_env=="azure":
                url=mpnetsimilarityurl
            elif target_env=="aicloud":
                url=mpnetsimilarityraiurl
            output =await post_request(url = url,json={"text1": prompt,"text2": output_text},headers=headers)
            similarity=json.loads(output.decode('utf-8'))[0][0][0]
            
            # output = requests.post(url = mpnetsimilarityurl,json={"text1": prompt,"text2": output_text},headers=headers,verify=False)
            # similarity=output.json()[0][0]
            # log.info(f"Max similarity : {max(similarity)}")
            return similarity
        except Exception as e:
            log.error("Error occured in promptResponse")
         
            # line_number = traceback.extract_tb(e.__traceback__)[0].lineno
          
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at PromptInjection model call"})
      
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

class Jailbreak:
    async def identify_jailbreak(self, text,headers):

        try:
            #response with azure moderation model endpoints
            if target_env=='azure':
                log.info("Using azure jailbreak model endpoint")
                text_embedding =await post_request(url = jailbreakurl,json={"text": [text]},headers=headers)
                modelcalltime = json.loads(text_embedding.decode('utf-8'))[1]['time_taken']
                text_embedding=json.loads(text_embedding.decode('utf-8'))[0][0]
            #response with aicloud moderation model endpoints
            elif target_env=='aicloud':
                log.info("Using aicloud jailbreak model endpoint")
                st=time.time()
                text_embedding =await post_request(url = jailbreakraiurl,json={"inputs": [text]},headers=headers)
                et=time.time()
                modelcalltime = str(round(et-st,3))+"s"
                text_embedding=json.loads(text_embedding.decode('utf-8'))[0]           
            
            similarities = []
            for embedding in jailbreak_embeddings:
                dot_product = np.dot(text_embedding, embedding)
                norm_product = np.linalg.norm(text_embedding) * np.linalg.norm(embedding)
                similarity = round(dot_product / norm_product,4)
                similarities.append(similarity)
       
            return max(similarities),modelcalltime
        except Exception as e:
        
            log.error("Error occured in Jailbreak")
      
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at PromptInjection model call"})
       
            log.error(f"Exception: {e}")

class Customtheme:
    async def identify_jailbreak(self,text,headers,theme=None):
        try:
            theme.append(text)
            #response with azure moderation model endpoints
            if target_env=='azure':
                log.info("Using azure jailbreak model endpoint for custom theme")
                customTheme_embeddings =await post_request(url = jailbreakurl,json={"text": theme},headers=headers)
                customTheme_embeddings_decoded = json.loads(customTheme_embeddings.decode('utf-8'))
                modelcalltime = customTheme_embeddings_decoded[1]['time_taken']
                text_embedding=customTheme_embeddings_decoded[0]   
                # customTheme_embeddings=customTheme_embeddings_decoded[0][:-1]
                return text_embedding,modelcalltime
            #response with aicloud moderation model endpoints
            elif target_env=='aicloud':
                log.info("Using aicloud jailbreak model endpoint for custom theme")
                st=time.time()
                customTheme_embeddings =await post_request(url = jailbreakraiurl,json={"inputs": theme},headers=headers)
                et=time.time()
                customTheme_embeddings_decoded = json.loads(customTheme_embeddings.decode('utf-8'))
                modelcalltime = str(round(et-st,3))+"s"
                text_embedding=customTheme_embeddings_decoded  
                # customTheme_embeddings=customTheme_embeddings_decoded[:-1]
                return text_embedding,modelcalltime

            # similarities = []
            # for embedding in customTheme_embeddings:
            #     dot_product = np.dot(text_embedding, embedding)
            #     norm_product = np.linalg.norm(text_embedding) * np.linalg.norm(embedding)
            #     similarity = round(dot_product / norm_product,4)
            #     similarities.append(similarity)
            # return max(similarities),modelcalltime
        except Exception as e:
            log.error("Error occured in Customtheme")
         
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at Customtheme"})
       
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
    

class CustomthemeRestricted:
    def identify_jailbreak(self, text,headers,theme=None):
        try:
            #Using azure jailbreak endpoint for custom theme restricted
            if target_env=='azure':
                log.info("Using azure jailbreak endpoint for custom theme restricted")
                text_embedding = requests.post(url = jailbreakurl,json={"text": [text]},headers=headers,verify=sslv[verify_ssl]).json()[0][0]
            #Using aicloud jailbreak endpoint for custom theme restricted
            elif target_env=='aicloud':
                log.info("Using aicloud jailbreak endpoint for custom theme restricted")
                text_embedding = requests.post(url = jailbreakraiurl,json={"inputs": [text]},headers=headers,verify=sslv[verify_ssl]).json()[0]
            if theme:
                embed_array = orgpolicy_embeddings
            else:
                embed_array = topic_embeddings
            similarities = []
            for embedding in embed_array:
                dot_product = np.dot(text_embedding, embedding)
                norm_product = np.linalg.norm(text_embedding) * np.linalg.norm(embedding)
                similarity = round(dot_product / norm_product,4)
                # similarity = util.pytorch_cos_sim(text_embedding, embedding)
                similarities.append(similarity)
        
            # print("1111",max(similarities).tolist()[0][0])
            return max(similarities)
        except Exception as e:
            log.error("Error occured in CustomthemeRestricted")
         
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at PromptInjection model call"})
          
            log.error(f"Exception: {e}")

class Refusal:
    async def refusal_check(self,text,headers):
        try:
            #for response with azure moderation model endpoints
            if target_env == 'azure':
                log.info("Using azure jailbreak model endpoint for refusal check")
                text_embedding =await post_request(url = jailbreakurl,json={"text": [text]},headers=headers)
                text_embedding=json.loads(text_embedding.decode('utf-8'))[0][0]
            
            # for response with aicloud moderation model endpoints
            elif target_env == 'aicloud':
                log.info("Using aicloud jailbreak model endpoint for refusal check")
                text_embedding =await post_request(url = jailbreakraiurl,json={"inputs": [text]},headers=headers)
                text_embedding=json.loads(text_embedding.decode('utf-8'))[0]
            similarities = []
            for embedding in refusal_embeddings:
                dot_product = np.dot(text_embedding, embedding)
                norm_product = np.linalg.norm(text_embedding) * np.linalg.norm(embedding)
                similarity = round(dot_product / norm_product,4)
                # similarity = util.pytorch_cos_sim(text_embedding, embedding)
                # similarity = requests.post(url = mpnetsimilarityurl,json={"emb1":text_embedding,"emb2":embedding},verify=False).json()[0][0]
                similarities.append(similarity)
            return max(similarities)
        except Exception as e:
            log.error("Error occured in Refusal")
          
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at PromptInjection model call"})
          
            # log.error(f"Exception: {e}")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

class Restrict_topic:
    async def restrict_topic(self,text,config_details,headers,model="dberta"): 
        try:
            labels= config_details["ModerationCheckThresholds"]["RestrictedtopicDetails"]["Restrictedtopics"]
            #Using azure moderation model endpoint
            if target_env=='azure':
                log.info("Using the azure endpoint for restricted topic")
                output =await post_request(url = topicurl,json={"text": text,"labels":labels,"model":model},headers=headers)
                output=json.loads(output.decode('utf-8'))
                modelcalltime = output['time_taken']
                d={}
                for i in range(len(labels)):
                    d[output["labels"][i]] = str(round(output["scores"][i],3))

            #Using aicloud moderation model endpoint
            elif target_env=='aicloud':
                log.info("Using the aicloud model endpoint for restricted topic")
                st=time.time()
                output =await post_request(url = topicraiurl,json={"inputs": [{"text":text,"labels":labels}]},headers=headers)
                et=time.time()
                output=json.loads(output.decode('utf-8'))
                modelcalltime = str(round(et-st,3))+"s"
                d={}
                for i in range(len(labels)):
                    d[output[0]["labels"][i]] = str(round(output[0]["scores"][i],3))

            log.debug(f"Dictionary for labels: {d}")

            return d,modelcalltime
        except Exception as e:
            log.error("Error occured in Restrict_topic")
           
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at Restrict_topic model call"})
          

class Toxicity:
    async def toxicity_check(self,text,headers):
        try:
            if identifyIDP(text):
                text=text.replace('IDP','idp')
            # tokens = TreebankWordTokenizer().tokenize
            tokens = nltk.word_tokenize(text)  
            # print("len(tokens)",len(tokens))
            if len(tokens) > 400:
                chunked_texts = []
                chunk = []
                token_count = 0

                for token in tokens:
                    if token_count + len(token) <= 400:
                        chunk.append(token)
                        token_count += len(token)
                    else:
                        chunked_texts.append(' '.join(chunk))
                        chunk = [token]
                        token_count = len(token)

                # Add the last chunk if it's not empty
                
                if chunk:
                    chunked_texts.append(' '.join(chunk))
            
                toxicity_scoreslist = []
                toxicity_scores = {
                'toxicity': 0,
                'severe_toxicity': 0,
                'obscene': 0,
                'threat': 0,
                'insult': 0,
                'identity_attack': 0,
                'sexual_explicit': 0
                }
                
                count = 0

                #Using azure moderation model endpoint 
                if target_env=='azure':
                    log.info("Using azure model endpoints for toxicity")
                    for chunk in chunked_texts:
                        result =await post_request(url=detoxifyurl,json={"text": chunk},headers=headers)
                        result=json.loads(result.decode('utf-8'))
                        modelcalltime = result["time_taken"]
                        toxicity_scoreslist.append(result)

                    for item in toxicity_scoreslist:
                        toxic_score_list = item['toxicScore']
                        for metric in toxic_score_list:
                            metric_name = metric['metricName']
                            metric_score = metric['metricScore']
                            toxicity_scores[metric_name] += metric_score
                        count += 1   

                #Using aicloud moderation model endpoint
                elif target_env=='aicloud':
                    log.info("Using aicloud model endpoints for toxicity")
                    for chunk in chunked_texts:
                        st=time.time()
                        result =await post_request(url=detoxifyraiurl,json={"inputs": [chunk]},headers=headers)
                        et=time.time()
                        result=json.loads(result.decode('utf-8'))
                        modelcalltime =str(round(et-st,3))+"s"
                        toxicity_scoreslist.append(result[0])

                    for item in toxicity_scoreslist:
                        for key,value in item.items():
                            metric_name = key
                            metric_score = value
                            toxicity_scores[metric_name] += metric_score
                        count += 1 
                toxicity_averages = {key: value / count for key, value in toxicity_scores.items()}
                
                l=[]
                for i in toxicity_averages:
                    l.append({'metricName': i, 'metricScore': toxicity_averages[i]})
                output = {"toxicScore":l}
                toxic_score = output["toxicScore"][0]["metricScore"]
    
            else:
                #Using azure moderation model endpoint 
                if target_env=='azure':
                    log.info("Using azure model endpoints for toxicity")
                    output = await post_request(url=detoxifyurl,json={"text": text},headers=headers,verify=False)
                    output=json.loads(output.decode('utf-8'))
                    modelcalltime = output["time_taken"]
                    toxic_score = output["toxicScore"][0]["metricScore"]

                #Using aicloud moderation model endpoint
                elif target_env=='aicloud':
                    log.info("Using aicloud model endpoints for toxicity")
                    st=time.time()
                    output=await post_request(url=detoxifyraiurl,json={"inputs":[text]},headers=headers,verify=False)
                    et=time.time()
                    output=json.loads(output.decode('utf-8'))
                    modelcalltime=str(round(et-st,3))+"s"
                    toxic_score = output[0]["toxicity"]
                    lst=[]
                    for key, value in output[0].items():
                        lst.append({"metricName":key,"metricScore":value})
                    output={'time_taken':modelcalltime,'toxicScore':lst}
            return toxic_score,output,modelcalltime
        except Exception as e:
        
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at Toxicity model call"})
         
            log.error("Error occured in Toxicity")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
    
async def toxicity_popup(payload,token):
    try:
        log.info(f"Initialising toxicity popup")
        # st = time.time()
        toxicity = Toxicity()
        headers = {'Authorization': token}
        payload = AttributeDict(payload)
        result = await toxicity.toxicity_check(payload.text,headers)
        toxic_dict=result
        status="PASSED"
        toxic_dict=toxic_dict[1]["toxicScore"]
        payload.ToxicityThreshold = AttributeDict(payload.ToxicityThreshold)
        if float(toxic_dict[0]["metricScore"])>payload.ToxicityThreshold.ToxicityThreshold:
            status="FAILED"
        if float(toxic_dict[1]["metricScore"])>payload.ToxicityThreshold.SevereToxicityThreshold:
            status="FAILED"
        if float(toxic_dict[2]["metricScore"])>payload.ToxicityThreshold.ObsceneThreshold:
            status="FAILED"
        if float(toxic_dict[3]["metricScore"])>payload.ToxicityThreshold.ThreatThreshold:
            status="FAILED"
        if float(toxic_dict[4]["metricScore"])>payload.ToxicityThreshold.InsultThreshold:
            status="FAILED"
        if float(toxic_dict[5]["metricScore"])>payload.ToxicityThreshold.IdentityAttackThreshold:
            status="FAILED"
        if float(toxic_dict[6]["metricScore"])>payload.ToxicityThreshold.SexualExplicitThreshold:
            status="FAILED"
        toxicity_dict={
            "toxicity":{"score":str(round(float(toxic_dict[0]["metricScore"]),3)),"threshold":payload.ToxicityThreshold.ToxicityThreshold},
            "severe_toxicity":{"score":str(round(float(toxic_dict[1]["metricScore"]),3)),"threshold":payload.ToxicityThreshold.SevereToxicityThreshold},
            "obscene":{"score":str(round(float(toxic_dict[2]["metricScore"]),3)),"threshold":payload.ToxicityThreshold.ObsceneThreshold},
            "threat":{"score":str(round(float(toxic_dict[3]["metricScore"]),3)),"threshold":payload.ToxicityThreshold.ThreatThreshold},
            "insult":{"score":str(round(float(toxic_dict[4]["metricScore"]),3)),"threshold":payload.ToxicityThreshold.InsultThreshold},
            "identity_attack":{"score":str(round(float(toxic_dict[5]["metricScore"]),3)),"threshold":payload.ToxicityThreshold.IdentityAttackThreshold},
            "sexual_explicit":{"score":str(round(float(toxic_dict[6]["metricScore"]),3)),"threshold":payload.ToxicityThreshold.SexualExplicitThreshold},
            "status":status
        }
        return {"toxicity":[toxicity_dict]}
    except Exception as e:
            log.error("Error occured in toxicity_popup")
            # log.error(f"Exception: {e}")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

def profanity_popup(text,headers):
    text_ogn=text
    emoji_dict=identifyEmoji(text)
    emoji_flag= emoji_dict['flag']  
    if emoji_flag:
        converted_text,privacy_text,current_emoji_dict=emojiToText(text=text,emoji_dict=emoji_dict)
        text=converted_text
    else:
        text=text_ogn
    try:
        max_chunk_size = 512
        list_ = text.split()
        length_list = len(list_)
        if length_list > 300:
            chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
        
            toxicity_scoreslist = []

            toxicity_scores = {
            'toxicity': 0,
            'severe_toxicity': 0,
            'obscene': 0,
            'threat': 0,
            'insult': 0,
            'identity_attack': 0,
            'sexual_explicit': 0
            }
            
            count = 0
            #Using azure endpoints for profanity popup
            if target_env=='azure':
                log.info("Using azure endpoints for profanity popup")
                for chunk in chunks:
                    result = requests.post(url=detoxifyurl,json={"text": chunk},headers=headers,verify=sslv[verify_ssl]).json()
                    toxicity_scoreslist.append(result)
                for item in toxicity_scoreslist:
                    toxic_score_list = item['toxicScore']
                    for metric in toxic_score_list:
                        metric_name = metric['metricName']
                        metric_score = metric['metricScore']
                        toxicity_scores[metric_name] += metric_score
                    count += 1
            #Using aicloud endpoints for profanity popup
            elif target_env=='aicloud':
                log.info("Using aicloud endpoints for profanity popup")
                for chunk in chunks:
                    result = requests.post(url=detoxifyraiurl,json={"inputs": [chunk]},headers=headers,verify=sslv[verify_ssl]).json()
                    toxicity_scoreslist.append(result[0])
                for item in toxicity_scoreslist:
                        for key,value in item.items():
                            metric_name = key
                            metric_score = value
                            toxicity_scores[metric_name] += metric_score
                        count += 1 
           
            toxicity_averages = {key: value / count for key, value in toxicity_scores.items()}
            
            l=[]
            for i in toxicity_averages:
                l.append({'metricName': i, 'metricScore': toxicity_averages[i]})
            output = {"toxicScore":l}
            toxic_score = output["toxicScore"][0]["metricScore"]
        else:
            #Using azure endpoints for profanity popup
            if target_env=='azure':
                log.info("Using azure endpoints for profanity popup")
                output = requests.post(url=detoxifyurl,json={"text": text},headers=headers,verify=sslv[verify_ssl]).json()
                toxic_score = output["toxicScore"][0]["metricScore"]
            #Using aicloud endpoints for profanity popup
            elif target_env=='aicloud':
                log.info("Using aicloud endpoints for profanity popup")
                output = requests.post(url=detoxifyraiurl,json={"inputs": [text]},headers=headers,verify=sslv[verify_ssl]).json()
                toxic_score = output[0]["toxicity"]              


        # output = requests.post(url=detoxifyurl,json={"text": text},verify=False).json()
        # toxic_score = output["toxicScore"][0]["metricScore"]
        List_profanity = []
        if toxic_score > 0.6:
            res = profanity.censor(text)
            if emoji_flag:
                res[1]=wordToEmoji(text=text_ogn,current_emoji_dict=current_emoji_dict,result=res[1])
                res[2]=profaneWordIndex(text=text_ogn,profane_list=res[1])
            for i in range(len(res[1])):
                List_profanity.append({"text": res[1][i],"insetIndex":res[2][i][0],"offsetIndex":res[2][i][1]})
        return {"profanity":List_profanity}
    except Exception as e:
            log.error("Error occured in profanity_popup")
            # log.error(f"Exception: {e}")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            
def privacy_popup(payload,headers=None):
    try:
        entityList= []
        entitiesconfigured = payload.PiientitiesConfiguredToDetect
        entitiesconfiguredToBlock = payload.PiientitiesConfiguredToBlock
        text=payload.text
        
        emoji_mod_opt=payload.EmojiModeration if "EmojiModeration" in payload else "no"
        emoji_flag=False

        if(emoji_mod_opt=="yes"):
            emoji_dict=identifyEmoji(text)
            emoji_flag= emoji_dict['flag']
            if emoji_flag:
                privacy_text=emojiToText(text=text,emoji_dict=emoji_dict)[1]
        text=privacy_text if emoji_flag else text
        if target_env=='azure':
            url=privacyurl
        elif target_env=='aicloud':
            url=privacyraiurl
        analyze_result =requests.post(url=url,json={"text": text},headers=headers)
        analyze_result=analyze_result.json()
        entitiesconfigured = payload.PiientitiesConfiguredToDetect
        entitiesconfiguredToBlock = payload.PiientitiesConfiguredToBlock

        entityList=[]   
        result = "Passed"        
        for i in range(0,len(analyze_result["PIIresult"])):

            if analyze_result["PIIresult"][i]["type"] in entitiesconfiguredToBlock and analyze_result["PIIresult"][i]["score"]>0.4:
                result="Block"
                entity_obj = PiiEntitiesforPopup(EntityType = analyze_result["PIIresult"][i]["type"] ,
                                        beginOffset = analyze_result["PIIresult"][i]["beginOffset"],
                                        endOffset = analyze_result["PIIresult"][i]["endOffset"],
                                        score= analyze_result["PIIresult"][i]["score"],
                                        value = analyze_result["PIIresult"][i]["responseText"]) 
                entityList.append(entity_obj)

            if analyze_result["PIIresult"][i]["type"] in entitiesconfigured and analyze_result["PIIresult"][i]["score"]>0.4 and analyze_result["PIIresult"][i]["type"] not in entitiesconfiguredToBlock:
                entity_obj = PiiEntitiesforPopup(EntityType = analyze_result["PIIresult"][i]["type"] ,
                                        beginOffset = analyze_result["PIIresult"][i]["beginOffset"],
                                        endOffset = analyze_result["PIIresult"][i]["endOffset"],
                                        score= analyze_result["PIIresult"][i]["score"],
                                        value = analyze_result["PIIresult"][i]["responseText"]) 
                entityList.append(entity_obj)




        popup_obj = PrivacyPopup(entitiesToDetect = entitiesconfigured,
                    entitiesToBlock = entitiesconfiguredToBlock,
                    entitiesRecognized =entityList,
                    result = result)
        return PrivacyPopupResponse(privacyCheck = [popup_obj])
    
    except Exception as e:
        log.error("Error occured in privacy_popup")
        log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

class Profanity:
    def __init__(self):
        
        self.profanity_method = "Better_profanity"

    async def recognise(self,text,headers):
        try:
            tokens = nltk.word_tokenize(text)    
            if len(tokens) > 400:
                chunked_texts = []
                chunk = []
                token_count = 0

                for token in tokens:
                    if token_count + len(token) <= 400:
                        chunk.append(token)
                        token_count += len(token)
                    else:
                        chunked_texts.append(' '.join(chunk))
                        chunk = [token]
                        token_count = len(token)

                # Add the last chunk if it's not empty
                if chunk:
                    chunked_texts.append(' '.join(chunk))
            
                toxicity_scoreslist = []
                toxicity_scores = {
                'toxicity': 0,
                'severe_toxicity': 0,
                'obscene': 0,
                'threat': 0,
                'insult': 0,
                'identity_attack': 0,
                'sexual_explicit': 0
                }
                
                count = 0

                #Using azure moderation model endpoint 
                if target_env=='azure':
                    log.info("Using azure model endpoints for profanity")
                    for chunk in chunked_texts:
                        result =await post_request(url=detoxifyurl,json={"text": chunk},headers=headers)
                        result=json.loads(result.decode('utf-8'))
                    toxicity_scoreslist.append(result)

                    for item in toxicity_scoreslist:
                        toxic_score_list = item['toxicScore']
                        for metric in toxic_score_list:
                            metric_name = metric['metricName']
                            metric_score = metric['metricScore']
                            toxicity_scores[metric_name] += metric_score
                        count += 1   

                #Using aicloud moderation model endpoint
                elif target_env=='aicloud':
                    log.info("Using aicloud model endpoints for profanity")
                    for chunk in chunked_texts:
                        result =await post_request(url=detoxifyraiurl,json={"inputs": [chunk]},headers=headers)
                        result=json.loads(result.decode('utf-8'))
                    toxicity_scoreslist.append(result[0])

                    for item in toxicity_scoreslist:
                        for key,value in item.items():
                            metric_name = key
                            metric_score = value
                            toxicity_scores[metric_name] += metric_score
                        count += 1 
                
                toxicity_averages = {key: value / count for key, value in toxicity_scores.items()}
                
                l=[]
                for i in toxicity_averages:
                    l.append({'metricName': i, 'metricScore': toxicity_averages[i]})
                output = {"toxicScore":l}
                toxic_score = output["toxicScore"][0]["metricScore"]
            else:
                #Using azure moderation model endpoint 
                if target_env=='azure':
                    log.info("Using azure model endpoints for toxicity")
                    output = await post_request(url=detoxifyurl,json={"text": text},headers=headers,verify=False)
                    output=json.loads(output.decode('utf-8'))
                    toxic_score = output["toxicScore"][0]["metricScore"]

                #Using aicloud moderation model endpoint
                elif target_env=='aicloud':
                    log.info("Using aicloud model endpoints for toxicity")
                    output=await post_request(url=detoxifyraiurl,json={"inputs":[text]},headers=headers,verify=False)
                    output=json.loads(output.decode('utf-8'))
                    toxic_score = output[0]["toxicity"]
            if toxic_score > 0.6:
                res = profanity.censor(text)
                return res[1]
            else:
                return []
        except Exception as e:
            log.error("Error occured in Profanity")
          
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at Profanity"})
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            
#PII 
class PII:
    async def analyze(self,text,headers):
        try:
            if target_env=='azure':
                url=privacyurl
            elif target_env=='aicloud':
                url=privacyraiurl
            analyze_result =await post_request(url=url,json={"text": text},headers=headers)
            analyze_result=json.loads(analyze_result.decode('utf-8'))
            modelcalltime = analyze_result["modelcalltime"]
            entityDict= {}
            entityDict["types"] = [dict["type"] for dict in analyze_result["PIIresult"]]
            entityDict["scores"] = [dict["score"] for dict in analyze_result["PIIresult"]]
            entityDict["responseTexts"]=[dict["responseText"] for dict in analyze_result["PIIresult"]]
            return entityDict,modelcalltime
        except Exception as e:
            log.error("Error occured in PII")
          
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at PII call"})
          
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

     
class validation_input:
    def __init__(self,deployment_name,text,config_details,emoji_mod_opt,accountname,portfolio):
        self.timecheck = {}
        self.modeltime = {}
        #implement output emoji moderation
        #to check if emoji moderation is enabled
        self.emoji_flag=False
        if(emoji_mod_opt=="yes"):
            emoji_dict=identifyEmoji(text)
            self.emoji_flag= emoji_dict['flag']  
            if self.emoji_flag:
                self.converted_text, self.privacy_text,self.current_emoji_dict=emojiToText(text=text,emoji_dict=emoji_dict)
        self.text = text
        self.accountname = accountname
        self.portfolio = portfolio
        self.deployment_name = deployment_name
        self.config_details = config_details
        self.promptInjection_threshold = config_details['ModerationCheckThresholds'].get('PromptinjectionThreshold')
        self.Jailbreak_threshold=config_details['ModerationCheckThresholds'].get("JailbreakThreshold")
        self.Profanity_threshold = config_details['ModerationCheckThresholds'].get('ProfanityCountThreshold')
        self.ToxicityThreshold = (None if config_details['ModerationCheckThresholds'].get('ToxicityThresholds')==None else config_details['ModerationCheckThresholds']['ToxicityThresholds']["ToxicityThreshold"])
        self.RefusalThreshold = config_details["ModerationCheckThresholds"].get('RefusalThreshold')
        self.PIIenities_selectedToBlock = config_details['ModerationCheckThresholds'].get('PiientitiesConfiguredToBlock')
        self.Topic_threshold = (None if config_details['ModerationCheckThresholds'].get("RestrictedtopicDetails")==None else config_details['ModerationCheckThresholds']["RestrictedtopicDetails"]['RestrictedtopicThreshold'])
        self.SmoothLT=config_details['ModerationCheckThresholds'].get('SmoothLlmThreshold')   # added for smoothllm
        
        self.sentiment_threshold=(None if config_details['ModerationCheckThresholds'].get('SentimentThreshold')==None else config_details['ModerationCheckThresholds']['SentimentThreshold'])
        self.invisibletext_threshold=None
        self.invisibletext_categories=None
        self.gibberish_threshold=None
        self.gibberish_labels=None
        if config_details['ModerationCheckThresholds'].get('InvisibleTextCountDetails')!=None:
            self.invisibletext_threshold=config_details['ModerationCheckThresholds'].get('InvisibleTextCountDetails')['InvisibleTextCountThreshold']
            self.invisibletext_categories=config_details['ModerationCheckThresholds'].get('InvisibleTextCountDetails')['BannedCategories']
        if config_details['ModerationCheckThresholds'].get('GibberishDetails')!=None:
            self.gibberish_threshold=config_details['ModerationCheckThresholds'].get('GibberishDetails')['GibberishThreshold']
            self.gibberish_labels=config_details['ModerationCheckThresholds'].get('GibberishDetails')['GibberishLabels']
        self.bancode_threshold=(None if config_details['ModerationCheckThresholds'].get('BanCodeThreshold')==None else config_details['ModerationCheckThresholds']['BanCodeThreshold'])
        
        self.Checks_selected=config_details['ModerationChecks']
        self.dict_prompt = {}
        self.dict_jailbreak = {}
        self.dict_profanity = {}
        self.dict_privacy = {}
        self.dict_topic={}
        self.dict_customtheme={}
        self.dict_toxicity = {}
        self.dict_refusal={}
        self.dict_relevance={}
        self.dict_textQuality={}
        
        self.dict_smoothllm={}    # added for smoothllm
        self.dict_bergeron={}    # added for bergeron
        self.dict_sentiment={}
        self.dict_invisibleText={}
        self.dict_gibberish={}
        self.dict_bancode={}
        ######################################################################
        self.dict_toxicity['object'] =toxicityCheck(toxicityScore = [],
                                          toxicitythreshold = str(''),
                                          result = 'UNMODERATED')
        self.dict_profanity['object'] =profanityCheck(profaneWordsIdentified = [],
                                          profaneWordsthreshold = "0",
                                          result = 'UNMODERATED')   
        self.dict_topic['object'] = restrictedtopic(topicScores=[],topicThreshold="0",result = "UNMODERATED")
        self.dict_refusal['object']=refusalCheck(refusalSimilarityScore =  "",
                                            RefusalThreshold = "",
                                            result = 'UNMODERATED')
        self.dict_relevance['object']=textRelevanceCheck(PromptResponseSimilarityScore = "")
        self.dict_textQuality['object']=textQuality(readabilityScore = "",
                                                        textGrade="") 
        self.dict_customtheme['object']=customThemeCheck(customSimilarityScore = str(''),
                                          themeThreshold = str(''),
                                          result = 'UNMODERATED')                                    
        self.dict_prompt['object']=promptInjectionCheck(injectionConfidenceScore = str(""),
                                          injectionThreshold = str(""),
                                          result = 'UNMODERATED')
        self.dict_jailbreak['object']=jailbreakCheck(jailbreakSimilarityScore = str(''),
                                          jailbreakThreshold = str(''),
                                          result = 'UNMODERATED') 
        self.dict_privacy['object']  = privacyCheck(entitiesRecognised = [],
                                               entitiesConfiguredToBlock = [],
                                               result = 'UNMODERATED')
        self.dict_smoothllm['object']= smoothLlmCheck(smoothLlmScore="",
                                                      smoothLlmThreshold="",
                                                      result='UNMODERATED')
        self.dict_bergeron['object']= bergeronCheck(text="",
                                                    result='UNMODERATED')
        self.dict_sentiment['object']= sentimentCheck(score = str(""),
                                          threshold = str(""),
                                          result = 'UNMODERATED')
        self.dict_invisibleText['object']= invisibleTextCheck(invisibleTextIdentified = [],
                                          threshold = str(""),
                                          result = 'UNMODERATED')
        self.dict_gibberish['object']= gibberishCheck(gibberishScore = [],
                                          threshold = str(""),
                                          result = 'UNMODERATED')
        self.dict_bancode['object']= bancodeCheck(score = [],
                                          threshold = str(""),
                                          result = 'UNMODERATED')      

    
    async def validate_sentiment(self,headers):
        try:
            log.info(f"Initialising Sentiment validation")
            self.dict_sentiment['key'] = "Sentiment Check"
            if self.sentiment_threshold==None:
                self.dict_sentiment['status'] = True
                return [self.dict_sentiment]
            
            st = time.time()
            log.info(f"threshold : {str(round(float(self.sentiment_threshold),2))}")
            sentiment_check = SentimentAnalysis()
            output = await sentiment_check.classify_text(self.text,headers)
            sentiment_score = output['score']['compound']
            self.modeltime["Sentiment Check"]=output['time_taken']
            
            if sentiment_score < self.sentiment_threshold:
                obj_sentiment = sentimentCheck(score = str(round(float(sentiment_score),2)),
                                            threshold = str(round(float(self.sentiment_threshold),2)),
                                            result = 'FAILED')
                self.dict_sentiment['status'] = False
            else:
                obj_sentiment = sentimentCheck(score = str(sentiment_score),
                                            threshold = str(self.sentiment_threshold),
                                            result = 'PASSED')
                self.dict_sentiment['status'] = True

            self.dict_sentiment['object'] = obj_sentiment
            et = time.time()
            rt = et - st
            dictcheck["Sentiment Check"]=str(round(rt,3))+"s"
            log.debug(f"Sentiment run time: {rt}")
            self.timecheck["Sentiment Check"]=str(round(rt,3))+"s"
            
            return [self.dict_sentiment]
        except Exception as e:
            log.error("Failed at sentiment_check")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at sentiment_check"})
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

    
    async def validate_invisibletext(self,headers):
        try:
            log.info(f"Initialising Invisible Text validation")
            self.dict_invisibleText['key'] = "Invisible Text Check"
            if self.invisibletext_threshold==None:
                self.dict_invisibleText['status'] = True
                return [self.dict_invisibleText]
            
            st = time.time()
            invisibletext_check = InvisibleText()
            output = await invisibletext_check.find_invisible_chars(self.text,self.invisibletext_categories,headers)
            invisiblecharsFound = output['result']
            self.modeltime["Invisible Text Check"]=output['time_taken']
            log.info(f"threshold : {str(self.invisibletext_threshold)}")
            if len(invisiblecharsFound) >= self.invisibletext_threshold:
                obj_invisibletext = invisibleTextCheck(invisibleTextIdentified=invisiblecharsFound,
                                            threshold = str(self.invisibletext_threshold),
                                            result = 'FAILED')
                self.dict_invisibleText['status'] = False
            else:
                obj_invisibletext = invisibleTextCheck(invisibleTextIdentified=invisiblecharsFound,
                                            threshold = str(self.invisibletext_threshold),
                                            result = 'PASSED')
                self.dict_invisibleText['status'] = True

            self.dict_invisibleText['object'] = obj_invisibletext
            et = time.time()
            rt = et - st
            dictcheck["Invisible Text Check"]=str(round(rt,3))+"s"
            log.debug(f"Invisible text run time: {rt}")
            self.timecheck["Invisible Text Check"]=str(round(rt,3))+"s"
            
            return [self.dict_invisibleText]
        except Exception as e:
            log.error("Failed at invisibletext_check")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at invisibletext_check"})
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

    async def validate_gibberish(self,headers):
        try:
            self.dict_gibberish['key'] = "Gibberish Check"
            if self.gibberish_threshold==None:
                self.dict_gibberish['status'] = True
                return [self.dict_gibberish]

            log.info(f"Initialising Gibberish validation")
            st = time.time()
            gibberish_check = Gibberish()
            output = await gibberish_check.detect_gibberish(self.text,self.gibberish_labels,headers)
            log.info(f"threshold : {str(self.gibberish_threshold)}")
            for i in range(len(output['result'])):
                gibberish_score = output['result'][i]['gibberish_score']
                if gibberish_score > self.gibberish_threshold and output['result'][i]['gibberish_label']=="noise":
                    obj_gibberish = gibberishCheck(gibberishScore=output['result'],
                                                threshold = str(self.gibberish_threshold),
                                                result = 'FAILED')
                    self.dict_gibberish['status'] = False
                    break
              
                obj_gibberish = gibberishCheck(gibberishScore=output['result'],
                                                threshold = str(self.gibberish_threshold),
                                                result = 'PASSED')
                self.dict_gibberish['status'] = True

            self.modeltime["Gibberish Check"]=output['time_taken']
            self.dict_gibberish['object'] = obj_gibberish
            et = time.time()
            rt = et - st
            dictcheck["Gibberish Check"]=str(round(rt,3))+"s"
            log.debug(f"Gibberish text run time: {rt}")
            self.timecheck["Gibberish Check"]=str(round(rt,3))+"s"
            
            return [self.dict_gibberish]
        except Exception as e:
            log.error("Failed at Gibberish_check")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at Gibberish_check"})
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

    
    async def validate_bancode(self,headers):
        try:
            self.dict_bancode['key'] = "Ban Code Check"
            log.info(f"Initialising Ban Code validation")
            st = time.time()
            bancode_check = BanCode()
            output = await bancode_check.ban_code(self.text,headers)
            res = output['result']
            if res['label']=="CODE":
                obj_bancode = bancodeCheck(label=res['label'],result = 'FAILED')
                self.dict_bancode['status'] = False 
            else: 
                obj_bancode = bancodeCheck(label=res['label'],result = 'PASSED')
                self.dict_bancode['status'] = True

            self.modeltime["Ban Code Check"]=output['time_taken']
            self.dict_bancode['object'] = obj_bancode
            et = time.time()
            rt = et - st
            dictcheck["Ban Code Check"]=str(round(rt,3))+"s"
            log.debug(f"Ban Code Check run time: {rt}")
            self.timecheck["Ban Code Check"]=str(round(rt,3))+"s"
            
            return [self.dict_bancode]
        except Exception as e:
            log.error("Failed at bancode_check")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at bancode_check"})
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")


    async def validate_smoothllm(self,headers):
        try:
            log.info(f"Initialising smoothllm validation")
            st = time.time()        
            #emoji check
            if self.emoji_flag:
                threshold, defense_output =  SMOOTHLLM.main(self.deployment_name,self.privacy_text, self.SmoothLT['input_pertubation'], self.SmoothLT['number_of_iteration'])
            else:
                threshold, defense_output =  SMOOTHLLM.main(self.deployment_name,self.text, self.SmoothLT['input_pertubation'], self.SmoothLT['number_of_iteration'])

            self.dict_smoothllm['key'] = 'Random Noise Check'
            
            error_message = "The response was filtered due to the prompt triggering Azure OpenAI's content management policy. Please modify your prompt and retry. To learn more about our content filtering policies please read our documentation: https://go.microsoft.com/fwlink/?linkid=2198766"
            if type(threshold) == str:
                if error_message in threshold or threshold == "content_filter":
                    obj_smooth = smoothLlmCheck(
                                                smoothLlmScore ="0.85",
                                                smoothLlmThreshold= "0.6",
                                                result='FAILED')
        
                    self.dict_smoothllm['object'] = obj_smooth
                    self.dict_smoothllm['status'] = False
                    et = time.time()
                    rt = et - st
                    dictcheck["Random Noise Check"]=str(round(rt,3))+"s"
                    log.info(f"smoothllm run time: {rt}")
                    
                    return [self.dict_smoothllm]
                
                
            if threshold >= self.SmoothLT['SmoothLlmThreshold']:
                obj_smooth = smoothLlmCheck(
                                            smoothLlmScore = str(threshold),
                                            smoothLlmThreshold= str(self.SmoothLT['SmoothLlmThreshold']),
                                            result='FAILED')
    
                self.dict_smoothllm['object'] = obj_smooth
                self.dict_smoothllm['status'] = False
                et = time.time()
                rt = et - st
                dictcheck["Random Noise Check"]=str(round(rt,3))+"s"
                log.info(f"smoothllm run time: {rt}")
                
                return [self.dict_smoothllm]
            elif threshold == -1:
                obj_smooth = smoothLlmCheck(smoothLlmScore = str(threshold),
                                            smoothLlmThreshold= str(self.SmoothLT['SmoothLlmThreshold']),
                                            result = 'UNDETERMINED')
                self.dict_smoothllm['object'] = obj_smooth
                self.dict_smoothllm['status'] = False
                et = time.time()
                rt = et - st
                dictcheck["Random Noise Check"]=str(round(rt,3))+"s"
                log.info(f"smoothllm run time: {rt}")
                
                return [self.dict_smoothllm]
            else:
                obj_smooth = smoothLlmCheck(smoothLlmScore = str(threshold),
                                            smoothLlmThreshold= str(self.SmoothLT['SmoothLlmThreshold']),
                                            result = 'PASSED')
                self.dict_smoothllm['object'] = obj_smooth
                self.dict_smoothllm['status'] = True
                et = time.time()
                rt = et - st
                dictcheck["Random Noise Check"]=str(round(rt,3))+"s"
                log.info(f"Smoothllm run time: {rt}")
             
                return [self.dict_smoothllm]
        except Exception as e:
            log.error("Failed at validate_smoothllm")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at validate_smoothllm"})
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            
    async def validate_bergeron(self,headers):
        try:
            log.info(f"Initialising Bergeron check validation")
            st = time.time()
            #emoji check
            if self.emoji_flag:
                berger, flag =  Bergeron.generate_final(self.deployment_name,self.privacy_text)
            else:
                berger, flag =  Bergeron.generate_final(self.deployment_name,self.text)
            
            self.dict_bergeron['key'] = 'Advanced Jailbreak Check'
            
            if flag == "The response was filtered due to the prompt triggering Azure OpenAI's content management policy. Please modify your prompt and retry. To learn more about our content filtering policies please read our documentation: https://go.microsoft.com/fwlink/?linkid=2198766":
                obj_berger = bergeronCheck(
                                            text="UNDETERMINED",                                            
                                            result='PASSED')
    
                self.dict_bergeron['object'] = obj_berger
                self.dict_bergeron['status'] = True
                et = time.time()
                rt = et - st
                dictcheck["Advanced Jailbreak Check"]=str(round(rt,3))+"s"
                log.info(f"Bergeron run time: {rt}")
                
                return [self.dict_bergeron]
            
            if flag == "FAILED":
                obj_berger = bergeronCheck(
                                            text="ADVERSARIAL",                                            
                                            result='FAILED')
    
                self.dict_bergeron['object'] = obj_berger
                self.dict_bergeron['status'] = False
                et = time.time()
                rt = et - st
                dictcheck["Advanced Jailbreak Check"]=str(round(rt,3))+"s"
                log.info(f"Bergeron run time: {rt}")
                
                return [self.dict_bergeron]
            
            elif flag == "UNDETERMINED":
                obj_berger = bergeronCheck(
                                            text="Cannot be determined as AWS Creds expired",                                            
                                            result='UNDETERMINED')
    
                self.dict_bergeron['object'] = obj_berger
                self.dict_bergeron['status'] = False
                et = time.time()
                rt = et - st
                dictcheck["Advanced Jailbreak Check"]=str(round(rt,3))+"s"
                log.info(f"Bergeron run time: {rt}")
                
                return [self.dict_bergeron]
            
            else:
                obj_berger = bergeronCheck(
                                            text="NON ADVERSARIAL",
                                            result = 'PASSED')
                self.dict_bergeron['object'] = obj_berger
                self.dict_bergeron['status'] = True
                et = time.time()
                rt = et - st
                dictcheck["Advanced Jailbreak Check"]=str(round(rt,3))+"s"
                log.info(f"Bergeron run time: {rt}")                
             
                return [self.dict_bergeron]
            
            
        except Exception as e:
            log.error("Failed at validate_bergeron")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at validate_bergeron"})
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            
    async def validate_prompt(self,headers):
        try:
            log.info(f"Initialising PromptInjection validation")
            st = time.time()
            prompt_check = PromptInjection()
            injectionscore, modelcalltime = await prompt_check.classify_text(self.text,headers)
            self.modeltime["Prompt Injection Check"]=modelcalltime
            self.dict_prompt['key'] = 'Prompt Injection Check'
            if injectionscore >= self.promptInjection_threshold:
                obj_prompt = promptInjectionCheck(injectionConfidenceScore = str(round(injectionscore,2)),
                                            injectionThreshold = str(self.promptInjection_threshold),
                                            result = 'FAILED')
                self.dict_prompt['status'] = False
            else:
                obj_prompt = promptInjectionCheck(injectionConfidenceScore = str(injectionscore),
                                            injectionThreshold = str(self.promptInjection_threshold),
                                            result = 'PASSED')
                self.dict_prompt['status'] = True

            self.dict_prompt['object'] = obj_prompt
            et = time.time()
            rt = et - st
            dictcheck["Prompt Injection Check"]=str(round(rt,3))+"s"
            log.debug(f"PromptInjection run time: {rt}")
            self.timecheck["Prompt Injection Check"]=str(round(rt,3))+"s"
            
            return [self.dict_prompt]
        except Exception as e:
            log.error("Failed at validate_prompt")
           
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at validate_prompt"})
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            
            
    # async def validate_jailbreak(self,headers):
    #     try:
    #         log.info(f"Initialising jailbreak validation")
    #         st = time.time()
    #         jailbreak = Jailbreak()
    #         result, modelcalltime = await jailbreak.identify_jailbreak(self.text, headers)
    #         self.modeltime['Jailbreak Check'] = modelcalltime
    #         self.dict_jailbreak['key'] = 'Jailbreak Check'
    #         if result <= self.Jailbreak_threshold:
    #             obj_jailbreak = jailbreakCheck(jailbreakSimilarityScore = str(round(float(result),2)),
    #                                         jailbreakThreshold = str(self.Jailbreak_threshold),
    #                                         result = 'PASSED')
    #             self.dict_jailbreak['status'] = True
    #         else:
    #             obj_jailbreak = jailbreakCheck(jailbreakSimilarityScore =  str(round(float(result),2)),
    #                                         jailbreakThreshold = str(self.Jailbreak_threshold),
    #                                         result = 'FAILED')
    #             self.dict_jailbreak['status'] = False

    #         self.dict_jailbreak['object'] = obj_jailbreak
    #         et = time.time()
    #         rt = et - st
    #         dictcheck["Jailbreak Check"]=str(round(rt,3))+"s"
    #         log.debug(f"jailbreak run time: {rt}")
    #         self.timecheck["Jailbreak Check"]=str(round(rt,3))+"s"
                
    #         return self.dict_jailbreak
    #     except Exception as e:
    #         log.error("Failed at validate jailbreak")
          
    #         log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
    #                                                "Error Module":"Failed at validate jailbreak"})

    #         # log.error(f"Exception: {e}")
    #         log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

    # async def validate_customtheme(self,theme,headers):
    #     try:
    #         log.info(f"Initialising Customtheme validation")
    #         st = time.time()
    #         customtheme = Customtheme()
    #         result, modelcalltime = await customtheme.identify_jailbreak(self.text,headers,theme.ThemeTexts)
    #         self.modeltime["Custom Theme Check"]=modelcalltime
    #         self.dict_customtheme['key'] = 'Custom Theme Check'
    #         if result <= theme.Themethresold:
    #             obj_jailbreak = customThemeCheck(customSimilarityScore = str(round(float(result),2)),
    #                                         themeThreshold = str(theme.Themethresold),
    #                                         result = 'PASSED')
    #             self.dict_customtheme['status'] = True 
    #         else:
    #             obj_jailbreak = customThemeCheck(customSimilarityScore =  str(round(float(result),2)),
    #                                         themeThreshold = str(theme.Themethresold),
    #                                         result = 'FAILED')
    #             self.dict_customtheme['status'] = False
            
    #         self.dict_customtheme['object'] = obj_jailbreak
    #         et = time.time()
    #         rt = et - st
    #         dictcheck["Custom Theme Check"]=str(round(rt,3))+"s"
    #         log.debug(f"CustomTheme run time: {rt}")
    #         self.timecheck["Custom Theme Check"]=str(round(rt,3))+"s"
    #         return self.dict_customtheme
        
    #     except Exception as e:
    #         log.error("Failed at validate customtheme")

    #         log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
    #                                                "Error Module":"Failed at validate customtheme"})
    #         log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")


    def jailbreak_val(self,text_embedding,modelcalltime,st,checkRes):
                    #print("---------------------------InsideJailbreak---------------------------")
                    similarities = []
                    # st=time.time()
                    for embedding in jailbreak_embeddings:
                        # similarity = requests.post(url = mpnetsimilarityurl,json={"emb1":text_embedding,"emb2":embedding},verify=False).json()[0][0]
                        # similarity = util.pytorch_cos_sim(text_embedding, embedding)
                        dot_product = np.dot(text_embedding, embedding)
                        norm_product = np.linalg.norm(text_embedding) * np.linalg.norm(embedding)
                        similarity = round(dot_product / norm_product,4)
                        similarities.append(similarity)
                    result = max(similarities)
                    # self.modelcall["Jailbreak Check"]=mt
                    self.modeltime['Jailbreak Check'] = modelcalltime
                    self.dict_jailbreak['key'] = 'Jailbreak Check'
                    if result <= self.Jailbreak_threshold:
                        obj_jailbreak = jailbreakCheck(jailbreakSimilarityScore = str(round(float(result),2)),
                                                    jailbreakThreshold = str(self.Jailbreak_threshold),
                                                    result = 'PASSED')
                        self.dict_jailbreak['status'] = True
                    else:
                        obj_jailbreak = jailbreakCheck(jailbreakSimilarityScore =  str(round(float(result),2)),
                                                    jailbreakThreshold = str(self.Jailbreak_threshold),
                                                    result = 'FAILED')
                        self.dict_jailbreak['status'] = False

                    self.dict_jailbreak['object'] = obj_jailbreak
                    et = time.time()
                    rt = et - st
                    dictcheck["Jailbreak Check"]=str(round(rt,3))+"s"
                    log.debug(f"jailbreak run time: {rt}")
                    self.timecheck["Jailbreak Check"]=str(round(rt,3))+"s"
                    checkRes.append(self.dict_jailbreak)
    
    def refusal_val(self,text_embedding,modelcalltime,st,checkRes):
                    #print("---------------------------InsideRefusal---------------------------")
                    similarities = []
                    for embedding in refusal_embeddings:
                        dot_product = np.dot(text_embedding, embedding)
                        norm_product = np.linalg.norm(text_embedding) * np.linalg.norm(embedding)
                        similarity = round(dot_product / norm_product,4)
                        # similarity = util.pytorch_cos_sim(text_embedding, embedding)
                        # similarity = requests.post(url = mpnetsimilarityurl,json={"emb1":text_embedding,"emb2":embedding},verify=False).json()[0][0]
                        similarities.append(similarity)
                    result = max(similarities)
                    # self.modelcall["Refusal Check"]=mt
                    self.dict_refusal['key'] = 'Refusal Check'
                    if result <= self.RefusalThreshold:
                        obj_refusal= refusalCheck(refusalSimilarityScore = str(round(float(result),2)),
                                                    RefusalThreshold = str(self.RefusalThreshold),
                                                    result = 'PASSED')
                        self.dict_refusal['status'] = True
                    else:
                        obj_refusal = refusalCheck(refusalSimilarityScore =  str(round(float(result),2)),
                                                    RefusalThreshold = str(self.RefusalThreshold),
                                                    result = 'FAILED')
                        self.dict_refusal['status'] = False

                    self.dict_refusal['object'] = obj_refusal
                    et = time.time()
                    rt = et - st
                    dictcheck["Refusal Check"]=str(round(rt,3))+"s"
                    log.debug(f"refusal run time: {rt}")
                    self.timecheck["Refusal Check"]=str(round(rt,3))+"s"
                    checkRes.append(self.dict_refusal)
        
    def custome_val(self,theme,customTheme_embeddings,text_embedding,modelcalltime,st,checkRes):
                    #print("---------------------------InsideCustomizedTheme---------------------------")
                    similarities = []

                    for embedding in customTheme_embeddings:
                        # similarity = requests.post(url = mpnetsimilarityurl,json={"emb1":text_embedding,"emb2":embedding},verify=False).json()[0][0]
                        # similarity = util.pytorch_cos_sim(text_embedding, embedding)
                        dot_product = np.dot(text_embedding, embedding)
                        norm_product = np.linalg.norm(text_embedding) * np.linalg.norm(embedding)
                        similarity = round(dot_product / norm_product,4)
                        similarities.append(similarity)
                    result=0
                    if(len(similarities)!=0):
                        result=max(similarities)
                    self.modeltime["Custom Theme Check"]=modelcalltime
                    # self.modelcall["Custom Theme Check"]=mt
                    self.dict_customtheme['key'] = 'Custom Theme Check'
                    if result <= theme.Themethresold:
                        obj_jailbreak = customThemeCheck(customSimilarityScore = str(round(float(result),2)),
                                                    themeThreshold = str(theme.Themethresold),
                                                    result = 'PASSED')
                        self.dict_customtheme['status'] = True 
                    else:
                        obj_jailbreak = customThemeCheck(customSimilarityScore =  str(round(float(result),2)),
                                                    themeThreshold = str(theme.Themethresold),
                                                    result = 'FAILED')
                        self.dict_customtheme['status'] = False

                    self.dict_customtheme['object'] = obj_jailbreak
                    et = time.time()
                    rt = et - st
                    dictcheck["Custom Theme Check"]=str(round(rt,3))+"s"
                    log.debug(f"CustomTheme run time: {rt}")
                    self.timecheck["Custom Theme Check"]=str(round(rt,3))+"s"
                    checkRes.append(self.dict_customtheme)
 
    async def validate_customtheme(self,theme,headers):
        try:
            log.info(f"Initialising Customtheme validation")
            st = time.time()
            customtheme = Customtheme()
            #print("Theam----",theme)
            results, modelcalltime= await customtheme.identify_jailbreak(self.text,headers,theme.ThemeTexts)
            checkRes=[]
            text_embedding=results[-1]
            threads=[]
            if("JailBreak" in self.Checks_selected):
                    #print("---------------------------Jailbreak---------------------------")
                    thread=threading.Thread(target=self.jailbreak_val,args=(text_embedding,modelcalltime,st,checkRes))
                    thread.start()
                    threads.append(thread)
                    # threads.append(threading.Thread(target=self.jailbreak_val,args=(text_embedding,modelcalltime,mt,st,checkRes)))
            if("Refusal" in self.Checks_selected):
                    #print("---------------------------Refusal---------------------------")
                    thread=threading.Thread(target=self.refusal_val,args=(text_embedding,modelcalltime,st,checkRes))
                    thread.start()
                    threads.append(thread)
                    # threads.append(threading.Thread(target=self.refusal_val,args=(text_embedding,modelcalltime,mt,st,checkRes)))
            if("CustomizedTheme" in self.Checks_selected):
                    #print("---------------------------CustomizedTheme---------------------------")
                
                    customTheme_embeddings=results[:-1]
                    thread=threading.Thread(target=self.custome_val,args=(theme,customTheme_embeddings,text_embedding,modelcalltime,st,checkRes))
                    thread.start()
                    threads.append(thread)
                    # threads.append(threading.Thread(target=self.custome_val,args=(theme,customTheme_embeddings,text_embedding,modelcalltime,mt,st,checkRes)))
                    # #print("customTheme_embeddings",len(customTheme_embeddings))

        

            for thread in threads:
                thread.join()       
                    # return [self.dict_customtheme]
            return checkRes
        except Exception as e:
            log.error("Failed at validate customtheme")

            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at validate customtheme"})
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

        
    # async def validate_profanity(self):
    #     try:
    #         log.info(f"Initialising profanity validation")
    #         st = time.time()
    #         profanity = Profanity()
    #         #check emoji
    #         if self.emoji_flag:
    #             result = await profanity.recognise(self.converted_text)
    #             #check and convert profane word back to emoji
    #             result=wordToEmoji(self.text,self.current_emoji_dict,result)
                
    #         else:
    #             result = await profanity.recognise(self.text)
    #         self.dict_profanity['key'] = 'Profanity Check'
    #         if len(result) < self.Profanity_threshold:
    #             obj_profanity = profanityCheck(profaneWordsIdentified = result,
    #                                         profaneWordsthreshold = str(self.Profanity_threshold),
    #                                         result = 'PASSED')
    #             self.dict_profanity['status'] = True
            
    #         else:
    #             obj_profanity = profanityCheck(profaneWordsIdentified = result,
    #                                         profaneWordsthreshold = str(self.Profanity_threshold),
    #                                         result = 'FAILED')
    #             self.dict_profanity['status'] = False

    #         self.dict_profanity['object'] = obj_profanity
    #         et = time.time()
    #         rt = et - st
    #         dictcheck["Profanity Check"]=str(round(rt,3))+"s"
    #         log.debug(f"profanity run time: {rt}")
    #         self.timecheck["Profanity Check"]=str(round(rt,3))+"s"

    #         return self.dict_profanity
    #     except Exception as e:
    #         log.error("Failed at validate profanity")
           
    #         log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
    #                                                "Error Module":"Failed at validate profanity"})
           
    #         # log.error(f"Exception: {e}")
    #         log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

    # Integrating Privacy into Moderation
    async def validate_pii(self,headers):
        try:
            log.info(f"Initialising PII validation")
            st = time.time()

            text=self.privacy_text if self.emoji_flag else self.text
            pii_analyzer = PII()
            entity_dict,modelcalltime =await pii_analyzer.analyze(text,headers)
            log.info(f"entity list: {entity_dict}")
            self.dict_privacy['key'] = 'Privacy Check' 
            piiEntitiesDetected=[]
            new_entity_dict={'AADHAR_NUMBER':'IN_AADHAAR','PASSPORT':'IN_PASSPORT','PAN_Number':'IN_PAN'}
            for i in self.PIIenities_selectedToBlock:
                if i in new_entity_dict:
                    self.PIIenities_selectedToBlock[self.PIIenities_selectedToBlock.index(i)]=new_entity_dict[i]
            log.info(f"pii entities to be blocked : {self.PIIenities_selectedToBlock}")
            for i in range(0,len(entity_dict['types'])):
                if entity_dict['types'][i] in self.PIIenities_selectedToBlock and entity_dict['scores'][i] > 0.4:
                    piiEntitiesDetected.append(entity_dict['types'][i])


            if len(piiEntitiesDetected)!=0:
                obj_privacy = privacyCheck(entitiesRecognised = piiEntitiesDetected,
                                           entitiesConfiguredToBlock = self.PIIenities_selectedToBlock,
                                           result = 'FAILED')
                self.dict_privacy['status'] = False
            else:
                obj_privacy = privacyCheck(entitiesRecognised = piiEntitiesDetected,
                                           entitiesConfiguredToBlock = self.PIIenities_selectedToBlock,
                                           result = 'PASSED')
                self.dict_privacy['status'] = True
            self.dict_privacy['object'] = obj_privacy
            et = time.time()
            rt = et - st
            dictcheck["Privacy Check"]=str(round(rt,3))+"s"
            log.debug(f"PII run time: {rt}")
            self.timecheck["Privacy Check"]=str(round(rt,3))+"s"    
            self.modeltime['Privacy Check']=str(modelcalltime)+"s"        
            return [self.dict_privacy]
        
        except Exception as e:
            log.error("Failed at validate pii")
          
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at validate pii"})
           
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")


    async def validate_restrict_topic(self,config_details,headers,model="dberta"):
        try:
            log.info(f"Initialising Restricted Topic validation")
            st = time.time()
            topic = Restrict_topic()
            #emoji check
            if self.emoji_flag:
                result, modelcalltime=await topic.restrict_topic(self.converted_text,config_details,headers,model)
            else:
                result, modelcalltime=await topic.restrict_topic(self.text,config_details,headers,model)
            self.modeltime['Restricted Topic Check']=modelcalltime
            self.dict_topic['key'] = 'Restricted Topic Check'
            
            success=1
            for i in result:
                if float(result[i])>self.Topic_threshold:
                    success=0
            if success:
                self.dict_topic['status']= True
                obj_topic = restrictedtopic(topicScores=[result],topicThreshold=str(self.Topic_threshold),result = "PASSED")
            else:
                self.dict_topic['status']= False
                obj_topic = restrictedtopic(topicScores=[result],topicThreshold=str(self.Topic_threshold),result = "FAILED") 
            
            self.dict_topic['object'] = obj_topic
            rt = time.time()-st
            dictcheck["Restricted Topic Check"]=str(round(rt,3))+"s"
            log.debug(f"Restricted topic run time: {rt}")
            self.timecheck["Restricted Topic Check"]=str(round(rt,3))+"s"

            return [self.dict_topic]
        except Exception as e:
            log.error("Failed at validate restrictedtopic")
          
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at alidate restrictedtopic"})
         
            log.error(f"Exception: {e,str(traceback.extract_tb(e.__traceback__)[0].lineno)}")
            
    
    # async def validate_toxicity(self,headers):
    #     try:
    #         log.info(f"Initialising toxicity validation")
    #         st = time.time()
    #         toxicity = Toxicity()
    #         #emoji check
    #         if self.emoji_flag:
    #             result,toxic_dict, modelcalltime =await toxicity.toxicity_check(self.converted_text,headers)
    #         else:
    #             result,toxic_dict, modelcalltime =await toxicity.toxicity_check(self.text,headers)
            
    #         self.dict_toxicity['key'] = 'Toxicity Check'
    #         self.modeltime['Toxicity Check']=modelcalltime
    #         list_toxic = []
    #         list_toxic.append(toxic_dict)
    #         rounded_toxic = []
    #         for item in list_toxic:
    #             toxic_score = item['toxicScore']
    #             rounded_score = [{'metricName': score['metricName'], 'metricScore': round(score['metricScore'], 3)} for score in toxic_score]
    #             rounded_item = {'toxicScore': rounded_score}
    #             rounded_toxic.append(rounded_item)
                
    #         if result < self.ToxicityThreshold:
    #             obj_toxicity = toxicityCheck(toxicityScore =rounded_toxic,
    #                                         toxicitythreshold = str(self.ToxicityThreshold),
    #                                         result = 'PASSED')
    #             self.dict_toxicity['status'] = True
                
    #         else:
    #             obj_toxicity = toxicityCheck(toxicityScore = list_toxic,
    #                                         toxicitythreshold = str(self.ToxicityThreshold),
    #                                         result = 'FAILED')
    #             self.dict_toxicity['status'] = False
            
    #         self.dict_toxicity['object'] = obj_toxicity
    #         et = time.time()
    #         rt = et - st
    #         dictcheck["Toxicity Check"]=str(round(rt,3))+"s"
    #         log.info(f"toxicity run time: {rt}")
    #         self.timecheck["Toxicity Check"]=str(round(rt,3))+"s"
    #         return self.dict_toxicity
    #     except Exception as e:
    #         log.error("Failed at validate toxicity")
           
    #         log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
    #                                                "Error Module":"Failed at validate toxicity"})
    #         log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
    

    # async def validate_profanity(self,header):
    #     try:
    #         log.info(f"Initialising profanity validation")
    #         st = time.time()
    #         profanity = Profanity()
    #         #check emoji
    #         if self.emoji_flag:
    #             result = await profanity.recognise(self.converted_text,header)
    #             #check and convert profane word back to emoji
    #             result=wordToEmoji(self.text,self.current_emoji_dict,result)
                        
    #         else:
    #             result = await profanity.recognise(self.text,header)
    #         self.dict_profanity['key'] = 'Profanity Check'
    #         if len(result) < self.Profanity_threshold:
    #             obj_profanity = profanityCheck(profaneWordsIdentified = result,
    #                                         profaneWordsthreshold = str(self.Profanity_threshold),
    #                                         result = 'PASSED')
    #             self.dict_profanity['status'] = True
                
            
    #         else:
    #             obj_profanity = profanityCheck(profaneWordsIdentified = result,
    #                                         profaneWordsthreshold = str(self.Profanity_threshold),
    #                                         result = 'FAILED')
    #             self.dict_profanity['status'] = False

    #         self.dict_profanity['object'] = obj_profanity
    #         et = time.time()
    #         rt = et - st
    #         dictcheck["Profanity Check"]=str(round(rt,3))+"s"
    #         log.debug(f"profanity run time: {rt}")
    #         self.timecheck["Profanity Check"]=str(round(rt,3))+"s"
    #         return self.dict_profanity
        
    #     except Exception as e:
    #         log.error("Failed at validate profanity")
    #         log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
    #                                                "Error Module":"Failed at validate profanity"})
    #         # log.error(f"Exception: {e}")
    #         log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

    def toxicity_val(self,result,rounded_toxic,list_toxic,st,checkRes):
                #print("---------------------ToxicityVal----------------------")
                if result < self.ToxicityThreshold:
                    obj_toxicity = toxicityCheck(toxicityScore =rounded_toxic,
                                                toxicitythreshold = str(self.ToxicityThreshold),
                                                result = 'PASSED')
                    self.dict_toxicity['status'] = True

                else:
                    obj_toxicity = toxicityCheck(toxicityScore = list_toxic,
                                                toxicitythreshold = str(self.ToxicityThreshold),
                                                result = 'FAILED')
                    self.dict_toxicity['status'] = False

                self.dict_toxicity['object'] = obj_toxicity
            
                et = time.time()
                rt = et - st
                dictcheck["Toxicity Check"]=str(round(rt,3))+"s"
                log.info(f"toxicity run time: {rt}")
                self.timecheck["Toxicity Check"]=str(round(rt,3))+"s"
                checkRes.append(self.dict_toxicity)

    def profanity_val(self,result,st,checkRes):
                    #print("---------------------ProfanityVal----------------------")
                    profRes=[]
                    if result > 0.6:
                        res = profanity.censor(self.text)
                        # #print("==",res)
                        
                        profRes=res[1]
                    # self.modelcall["Profanity Check"]=mt
                    self.dict_profanity['key'] = 'Profanity Check'
                    if len(profRes) < self.Profanity_threshold:
                        obj_profanity = profanityCheck(profaneWordsIdentified = profRes,
                                                    profaneWordsthreshold = str(self.Profanity_threshold),
                                                    result = 'PASSED')
                        self.dict_profanity['status'] = True

                    else:
                        obj_profanity = profanityCheck(profaneWordsIdentified = profRes,
                                                    profaneWordsthreshold = str(self.Profanity_threshold),
                                                    result = 'FAILED')
                        self.dict_profanity['status'] = False

                    self.dict_profanity['object'] = obj_profanity
                    et = time.time()
                    rt = et - st
                    dictcheck["Profanity Check"]=str(round(rt,3))+"s"
                    log.debug(f"profanity run time: {rt}")
                    self.timecheck["Profanity Check"]=str(round(rt,3))+"s"
                    checkRes.append(self.dict_profanity)
 
    async def validate_toxicity(self,headers):
        try:
            log.info(f"Initialising toxicity validation")
            st = time.time()
            toxicity = Toxicity()
            #emoji check
            if self.emoji_flag:
                result,toxic_dict, modelcalltime =await toxicity.toxicity_check(self.converted_text,headers)
            else:
                result,toxic_dict, modelcalltime =await toxicity.toxicity_check(self.text,headers)
            
            # self.modelcall["Toxicity Check"]=mt
            self.dict_toxicity['key'] = 'Toxicity Check'
            self.modeltime['Toxicity Check']=modelcalltime
            list_toxic = []
            list_toxic.append(toxic_dict)
            rounded_toxic = []
            for item in list_toxic:
                toxic_score = item['toxicScore']
                rounded_score = [{'metricName': score['metricName'], 'metricScore': round(score['metricScore'], 3)} for score in toxic_score]
                rounded_item = {'toxicScore': rounded_score}
                rounded_toxic.append(rounded_item)
            checkRes=[]
            threads=[]
            if("Toxicity" in self.Checks_selected):
                #print("---------------------Tocixity----------------------")
                thread=threading.Thread(target=self.toxicity_val,args=(result,rounded_toxic,list_toxic,st,checkRes))
                thread.start()
                threads.append(thread)
            if("Profanity" in self.Checks_selected):
                    #print("---------------------Profanity----------------------")
                    thread=threading.Thread(target=self.profanity_val,args=(result,st,checkRes))
                    thread.start()
                    threads.append(thread)
            # for thread in threads:
            #     thread.start()
            for thread in threads:
                thread.join()
                    
            return checkRes
        except Exception as e:
            log.error("Failed at validate toxicity")
           
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at validate toxicity"})
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
    

    
    # async def validate_refusal(self,headers):
    #     try:
    #         log.info(f"Initialising Refusal validation")
    #         st = time.time()
    #         refusal = Refusal()
    #         result = await refusal.refusal_check(self.text,headers)
    #         self.dict_refusal['key'] = 'Refusal Check'
    #         if result <= self.RefusalThreshold:
    #             obj_refusal= refusalCheck(refusalSimilarityScore = str(round(float(result),2)),
    #                                         RefusalThreshold = str(self.RefusalThreshold),
    #                                         result = 'PASSED')
    #             self.dict_refusal['status'] = True
    #         else:
    #             obj_refusal = refusalCheck(refusalSimilarityScore =  str(round(float(result),2)),
    #                                         RefusalThreshold = str(self.RefusalThreshold),
    #                                         result = 'FAILED')
    #             self.dict_refusal['status'] = False

    #         self.dict_refusal['object'] = obj_refusal
    #         et = time.time()
    #         rt = et - st
    #         dictcheck["Refusal Check"]=str(round(rt,3))+"s"
    #         log.debug(f"refusal run time: {rt}")
    #         self.timecheck["Refusal Check"]=str(round(rt,3))+"s"
    #         return self.dict_refusal
        
    #     except Exception as e:
    #         log.error("Failed at validate refusal")
    #         log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
    #                                                "Error Module":"Failed at validate refusal"})
    #         # log.error(f"Exception: {e}")
    #         log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

    async def validate_text_relevance(self,output_text,headers):
        try:
            log.info(f"Initialising Text relevance validation")
            st = time.time()
            self.dict_relevance['key']="Text Relevance Check"
            prSimilarity = promptResponse()
            prSimilarityscore = await prSimilarity.promptResponseSimilarity(output_text,self.text,headers)
            self.dict_relevance['status']=True
            self.dict_relevance['object']=textRelevanceCheck(PromptResponseSimilarityScore = str(int(prSimilarityscore*100)))
            rt = time.time()-st
            dictcheck["Text Relevance Check"]=str(round(rt,3))+"s"
            log.debug(f"Text relevance run time: {rt}")
            self.timecheck["Text Relevance Check"]=str(round(rt,3))+"s"

            return [self.dict_relevance]
        except Exception as e:
            log.error("Failed at validate_text_relevance")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at validate_text_relevance"})
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

    async def validate_text_quality(self):
        try:
            log.info(f"Initialising Text quality validation")
            st = time.time()
            self.dict_textQuality['key']="Text Quality Check"
            readabilityScore,textGrade = text_quality(self.text)
            
            self.dict_textQuality['status']=True
            self.dict_textQuality['object']=textQuality(readabilityScore = str(int(readabilityScore)),
                                                        textGrade=str(textGrade))
            et = time.time()
            rt = et - st
            dictcheck["Text Quality Check"]=str(round(rt,3))+"s"
            log.debug(f"Text quality run time: {rt}")
            self.timecheck["Text Quality Check"]=str(round(rt,3))+"s"
            return [self.dict_textQuality]
        except Exception as e:
            log.error("Failed at validate_text_quality")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at validate_text_quality"})
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
        


    async def main(self,theme,output_text,headers,llm_BasedChecks=[]):
        try:
            tasks=[]
            checkdict={
                'PromptInjection':"self.validate_prompt(headers)",
                # 'JailBreak':"self.validate_jailbreak(headers)",
                # 'Toxicity':"self.validate_toxicity(headers)",
                'Piidetct':"self.validate_pii(headers)",
                # 'Profanity':"self.validate_profanity(headers)",
                # "CustomizedTheme":"self.validate_customtheme(theme,headers)",
                # 'RestrictTopic':"self.validate_restrict_topic(self.config_details,headers)",
                # 'Refusal' : "self.validate_refusal(headers)",
                'TextRelevance' : "self.validate_text_relevance(output_text,headers)",
                'TextQuality' : "self.validate_text_quality()",
                'randomNoiseCheck':'self.validate_smoothllm(headers)',
                'advancedJailbreakCheck':'self.validate_bergeron(headers)',
                'Sentiment':"self.validate_sentiment(headers)",
                'InvisibleText':"self.validate_invisibletext(headers)",
                'Gibberish':"self.validate_gibberish(headers)",
                'BanCode':"self.validate_bancode(headers)",
                }
            profanFlag=1
            jailFlag=1
            
            for i in self.Checks_selected:
                    if(i == "Profanity" or i=="Toxicity"):
                        if(profanFlag==1):
                            profanFlag=0
                            tasks.append(self.validate_toxicity(headers))
                    elif(i == "JailBreak" or i=="Refusal" or i=="CustomizedTheme"):
                        if(jailFlag==1):
                            jailFlag=0
                            tasks.append(self.validate_customtheme(theme,headers))
                    elif("RestrictTopic" in i):
                        if("RestrictTopic-lite" in i):
                            tasks.append(self.validate_restrict_topic(self.config_details,headers,model="nliMini"))
                        else:    
                            tasks.append(self.validate_restrict_topic(self.config_details,headers,model="dberta"))
                            
                    else:
                        tasks.append(eval(checkdict[i]))
            for i in llm_BasedChecks:
                    tasks.append(eval(checkdict[i]))

            results = await asyncio.gather(*tasks)
            
            list_tasks = []
            results=sum(results, [])
            for i in results:
                list_tasks.append(i['status'])
            final_result = all(list_tasks)
            return final_result,results
        except Exception as e:
          #  print("=======err",e)
            log.error(f"Exception: {e}")
            log.error("Failed at Validate Main ------ ", str(traceback.extract_tb(e.__traceback__)[0].lineno))
            
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at Validate Main"})
            # log.error(f"Exception: {e}")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")



def callModerationModels(text,payload,headers,deployment_name=None,output_text=None,llm_BasedChecks=[]):
    global startupFlag,jailbreak_embeddings,refusal_embeddings,topic_embeddings
    list_checks = []
    payload=AttributeDict(payload)
    portfolio = payload.PortfolioName if "PortfolioName" in payload else "None"
    accountname = payload.AccountName if "AccountName" in payload else "None"
    payload.ModerationCheckThresholds=AttributeDict(payload.ModerationCheckThresholds)
    theme=AttributeDict(payload.ModerationCheckThresholds.CustomTheme)
    emoji_mod_opt=payload.EmojiModeration if "EmojiModeration" in payload else "no" #for emoji moderation

    validate_input=validation_input(deployment_name,text,payload,emoji_mod_opt,accountname,portfolio)
    passed_text,dict_all=asyncio.run(validate_input.main(theme,output_text,headers,llm_BasedChecks))
    
    check_obs = {'Prompt Injection Check': validate_input.dict_prompt['object'],
                 'Jailbreak Check':validate_input.dict_jailbreak['object'],
                 'Profanity Check':validate_input.dict_profanity['object'],
                 'Privacy Check':validate_input.dict_privacy['object'],
                 'Toxicity Check':validate_input.dict_toxicity['object'],
                 'Restricted Topic Check':validate_input.dict_topic['object'],
                 'Custom Theme Check':validate_input.dict_customtheme['object'],
                 'Text Quality Check':validate_input.dict_textQuality['object'],
                 'Refusal Check':validate_input.dict_refusal['object'],
                 'Text Relevance Check':validate_input.dict_relevance['object'],
                 'Random Noise Check':validate_input.dict_smoothllm['object'],
                 'Advanced Jailbreak Check':validate_input.dict_bergeron['object'],
                 'Sentiment Check':validate_input.dict_sentiment['object'],
                 'Invisible Text Check':validate_input.dict_invisibleText['object'],
                 'Gibberish Check':validate_input.dict_gibberish['object'],
                 'Ban Code Check':validate_input.dict_bancode['object'],
                 'model time':validate_input.modeltime,
                 'time check':validate_input.timecheck}
    
    status = 'PASSED'
    for i in dict_all:
        if i['status']==False:
            status = 'FAILED'
            list_checks.append(i['key'])

    objSummary = summary(status = status,reason = list_checks)
    log.debug(f'objSummary:{objSummary}')
    check_obs['summary'] = objSummary
    return check_obs


#===================================  For Decoupled Moderation  ============================================#
class moderation:
    @lru.lru_cache(ttl=cache_ttl,size=cache_size,flag=cache_flag)
    def completions(payload,headers,deployment_name=None,output_text=None,llm_BasedChecks=[],translate=None) -> dict:
        try:    
            
            lotNumber = str(payload.lotNumber) if "lotNumber" in payload else "None"
            created = datetime.now()
            text = payload.Prompt

            if translate == "google" or translate == "yes":
                print("Inside Google Translate")
                starttime = time.time()
                text,lang = Translate.translate(payload.Prompt)
                endtime = time.time()
                rt = endtime - starttime
                dict_timecheck["translate"]=str(round(rt,3))+"s"
            elif translate == "azure":
                print("Inside Azure Translate")
                starttime = time.time()
                text,lang = Translate.azure_translate(payload.Prompt)
                endtime = time.time()
                rt = endtime - starttime
                dict_timecheck["translate"]=str(round(rt,3))+"s"
     
            obj = callModerationModels(text,payload,headers,deployment_name,output_text,llm_BasedChecks)
      
            obj_requestmoderation = RequestModeration(text = text,
                                                        promptInjectionCheck = obj['Prompt Injection Check'],
                                                        jailbreakCheck= obj['Jailbreak Check'],
                                                        privacyCheck = obj['Privacy Check'],
                                                        profanityCheck = obj['Profanity Check'],
                                                        toxicityCheck = obj['Toxicity Check'],
                                                        restrictedtopic = obj['Restricted Topic Check'],
                                                        customThemeCheck = obj['Custom Theme Check'],
                                                        textQuality =obj['Text Quality Check'],
                                                        refusalCheck = obj['Refusal Check'],
                                                        sentimentCheck=obj['Sentiment Check'],
                                                        invisibleTextCheck = obj['Invisible Text Check'],
                                                        gibberishCheck = obj['Gibberish Check'],
                                                        bancodeCheck=obj['Ban Code Check'],
                                                        summary = obj['summary'])
            
            obj_ModerationResults = ModerationResults(lotNumber=lotNumber,created=str(created) ,moderationResults = obj_requestmoderation)
        
            # log.info("res="+str(obj_ModerationResults)+str(obj['time check'])+str(obj['model time']))
            return obj_ModerationResults,obj['time check'],obj['model time']
        except Exception as e:
            print(e)
            log.error("Failed at Completion call Function")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at Completion Function"})
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

            



#========================================= For Coupled Moderation  =========================================# 
class coupledModeration:
    
    @lru.lru_cache(ttl=cache_ttl,size=cache_size,flag=cache_flag)
    def coupledCompletions(payload,token):
        smoothllmresponse = smoothLlmCheck(smoothLlmScore="",smoothLlmThreshold = "",result = 'UNMODERATED')
        bergeronResponse = bergeronCheck(text="",result = 'UNMODERATED')
        objprofanity_out = profanityCheck(profaneWordsIdentified=[],profaneWordsthreshold = '0',result = 'UNMODERATED')
        objprivacy_out = privacyCheck(entitiesRecognised=[],entitiesConfiguredToBlock = [],result = 'UNMODERATED')
        # objtoxicity_out = toxicityCheck(toxicityScore= [],toxicitythreshold = '',result = 'UNMODERATED')
        # objtopic_out = restrictedtopic(topicScores=[],topicThreshold="0",result = "UNMODERATED")
        objtoxicity_out = toxicityCheckTypes(toxicityTypesRecognised = [],
									toxicityTypesConfiguredToBlock=[t.value for t in TOXICITYTYPES][0:-1],
									toxicityScore= [],
									toxicitythreshold = '0',
									result = 'UNMODERATED')		
        topicTypesConfiguredToBlock = payload.ModerationCheckThresholds['RestrictedtopicDetails']['Restrictedtopics']
        objtopic_out = restrictedtopicTypes(topicTypesConfiguredToBlock=topicTypesConfiguredToBlock,
                                                    topicTypesRecognised=[],
                                                    topicScores=[],topicThreshold="0",result = "UNMODERATED")
        objtextQuality_out = textQuality(readabilityScore = "0",textGrade="")
        objpromptResponse_out = textRelevanceCheck(PromptResponseSimilarityScore = "0")
        objrefusal_out = refusalCheck(refusalSimilarityScore = "" , RefusalThreshold = "" , result = 'UNMODERATED')
        obj_sentiment_out = sentimentCheck(score = "",threshold = "",result = 'UNMODERATED')
        obj_invisibleText_out = invisibleTextCheck(invisibleTextIdentified=[],threshold = "",result = 'UNMODERATED')
        obj_gibberish_out = gibberishCheck(gibberishScore=[],threshold = "",result = 'UNMODERATED')
        obj_bancode_out = bancodeCheck(score=[],threshold = "",result = 'UNMODERATED')
        list_choices = []
        created = datetime.now()
        global dictcheck
        st = time.time()
            
        llm_Based_Checks = payload.llm_BasedChecks
        emojiModOpt=payload.EmojiModeration if "EmojiModeration" in payload else "no"
        deployment_name = payload.model_name if "model_name" in payload else "gpt4"
        translate = payload.translate if "translate" in payload else None
        text = payload.Prompt
        PromptTemplate=payload.PromptTemplate
        temperature = float(payload.temperature)
        LLMinteraction = payload.LLMinteraction
        userid = payload.userid if "userid" in payload else "None"
        lotNumber = str(payload.lotNumber) if "lotNumber" in payload else "None"

        if translate == "google" or translate == "yes":
                print("Inside Google Translate")
                starttime = time.time()
                text,lang = Translate.translate(payload.Prompt)
                endtime = time.time()
                rt = endtime - starttime
                dict_timecheck["translate"]=str(round(rt,3))+"s"
        elif translate == "azure":
                print("Inside Azure Translate")
                starttime = time.time()
                text,lang = Translate.azure_translate(payload.Prompt)
                endtime = time.time()
                rt = endtime - starttime
                dict_timecheck["translate"]=str(round(rt,3))+"s"

        inputpayload = completionRequest(AccountName=payload.AccountName if "AccountName" in payload else "None",
                                            PortfolioName=payload.PortfolioName if "PortfolioName" in payload else "None",
                                            translate = payload.translate,
                                            Prompt=payload.Prompt,
                                            ModerationChecks=payload.InputModerationChecks,
                                            ModerationCheckThresholds=payload.ModerationCheckThresholds)
            
        inputpayload = json.loads(json.dumps(inputpayload, default=handle_object))
        inputpayload["EmojiModeration"]=emojiModOpt

        # Call to Moderation Models
        obj = callModerationModels(text=text,payload=inputpayload,headers=token,deployment_name=deployment_name,llm_BasedChecks=llm_Based_Checks)
        
        if len(llm_Based_Checks)!=0:
            smoothllmresponse = obj['Random Noise Check']
            bergeronResponse = obj['Advanced Jailbreak Check']
            log.info(f"smoothllmresponse : {smoothllmresponse}")
            log.info(f"bergeronResponse : {bergeronResponse}")

        toxicityScore = obj['Toxicity Check'].toxicityScore
        toxicityThreshold = obj['Toxicity Check'].toxicitythreshold
        toxicityResult = obj['Toxicity Check'].result
        toxicityTypesRecognised=[]
        if len(toxicityScore)!=0:
            toxicityTypesRecognised = [i['metricName'] for i in toxicityScore[0]['toxicScore'] if i['metricScore']>float(toxicityThreshold)]
        toxicityCheck = toxicityCheckTypes(toxicityTypesRecognised =toxicityTypesRecognised,
                            toxicityTypesConfiguredToBlock=[t.value for t in TOXICITYTYPES][0:-1],
                            toxicityScore =toxicityScore,
                            toxicitythreshold = toxicityThreshold,
                            result = toxicityResult)
        restrictedTopicScores = obj['Restricted Topic Check'].topicScores
        restrictedTopicThreshold = obj['Restricted Topic Check'].topicThreshold
        restrictedTopicResult= obj['Restricted Topic Check'].result
        topicTypesConfiguredToBlock = payload.ModerationCheckThresholds['RestrictedtopicDetails']['Restrictedtopics']
        topicTypesRecognised=[]
        if len(restrictedTopicScores)!=0:
            topicTypesRecognised = [i for i in restrictedTopicScores[0] if float(restrictedTopicScores[0][i])>float(restrictedTopicThreshold)]
        restrictedTopicCheck = restrictedtopicTypes(topicTypesConfiguredToBlock=topicTypesConfiguredToBlock,
                                                topicTypesRecognised=topicTypesRecognised,
                                                topicScores=restrictedTopicScores,
                                                topicThreshold=restrictedTopicThreshold,
                                                result = restrictedTopicResult)
        
        obj_requestmoderation = CoupledRequestModeration(text = payload.Prompt,
                                                    promptInjectionCheck = obj['Prompt Injection Check'],
                                                    jailbreakCheck = obj['Jailbreak Check'],
                                                    privacyCheck = obj['Privacy Check'],
                                                    profanityCheck = obj['Profanity Check'],
                                                    toxicityCheck = toxicityCheck,#inputModResult.moderationResults.toxicityCheck,
                                                    restrictedtopic = restrictedTopicCheck,#inputModResult.moderationResults.restrictedtopic,
                                                    textQuality = obj['Text Quality Check'],
                                                    customThemeCheck = obj['Custom Theme Check'],
                                                    refusalCheck = obj['Refusal Check'],
                                                    randomNoiseCheck = smoothllmresponse,
                                                    advancedJailbreakCheck = bergeronResponse,
                                                    sentimentCheck=obj['Sentiment Check'],
                                                    invisibleTextCheck = obj['Invisible Text Check'],
                                                    gibberishCheck = obj['Gibberish Check'],
                                                    bancodeCheck=obj['Ban Code Check'] ,                                                  
                                                    summary = obj['summary']).__dict__
            
        request_checks = {'Time taken by each model in requestModeration' : obj['model time']}
        dict_timecheck.update(request_checks)
        dict_timecheck["requestModeration"]= dictcheck

        dictcheck = {"Prompt Injection Check": "0s", 
           "Jailbreak Check": "0s", 
           "Toxicity Check": "0s", 
           "Privacy Check": "0s", 
           "Profanity Check": "0s", 
           "Refusal Check": "0s",
           "Restricted Topic Check": "0s",
           "Text Quality Check": "0s",
           "Custom Theme Check": "0s",
           "Random Noise Check":"0s",
           "Advanced Jailbreak Check":"0s",
           "Sentiment Check":"0s",
           "Invisible Text Check":"0s",
           "Gibberish Check":"0s",
           "Ban Code Check":"0s"
        }
        
        
            
        if obj['summary'].status =="FAILED":
                dict_timecheck["responseModeration"]= dictcheck
                objSummary_out = summary(status = 'Rejected',reason = ['Input Moderation'])
                obj_choices = Choice(text='',index= 0,finishReason = '')
                list_choices.append(obj_choices)
                obj_responsemoderation = ResponseModeration(generatedText = "",
                                                        hallucinationScore="",
                                                        privacyCheck = objprivacy_out,
                                                        profanityCheck = objprofanity_out,
                                                        toxicityCheck = objtoxicity_out,
                                                        restrictedtopic = objtopic_out,
                                                        textQuality = objtextQuality_out,
                                                        textRelevanceCheck = objpromptResponse_out,
                                                        refusalCheck = objrefusal_out,
                                                        sentimentCheck = obj_sentiment_out,
                                                        invisibleTextCheck = obj_invisibleText_out,
                                                        gibberishCheck = obj_gibberish_out,
                                                        bancodeCheck = obj_bancode_out,
                                                        summary = objSummary_out).__dict__
                
                objmoderation = CoupledModerationResults(requestModeration = obj_requestmoderation,
                                                         responseModeration = obj_responsemoderation)
                
                final_obj = completionResponse(userid=userid,
                                                        lotNumber=lotNumber,
                                                        object = "text_completion",
                                                        created = str(created),
                                                        model= deployment_name,
                                                        choices=list_choices,
                                                        moderationResults=objmoderation)
                totaltimeforallchecks = str(round(time.time() - st,3))+"s"
                response_checks = {"Time taken by each model in responseModeration" : 
                                       {"toxicityCheck": "0s","privacyCheck": "0s","restrictedtopic": "0s"}
                                       }
                dict_timecheck.update(response_checks)
                dict_timecheck.update({"Total time for moderation Check": totaltimeforallchecks})

        elif obj['summary'].status =="PASSED" and (LLMinteraction=="yes" or LLMinteraction=="Yes"):
                output_text,index,finish_reason,hallucinationScore = getLLMResponse(text,temperature,PromptTemplate,deployment_name,1)
                obj_choices = Choice(text=output_text,index= index,finishReason = finish_reason)
                list_choices.append(obj_choices)
                outputpayload = completionRequest(AccountName=payload.AccountName if "AccountName" in payload else "None",
                                            PortfolioName=payload.AccountName if "AccountName" in payload else "None",
                                            Prompt=output_text,
                                            translate = payload.translate,
                                            ModerationChecks=payload.OutputModerationChecks,
                                            ModerationCheckThresholds=payload.ModerationCheckThresholds)
                outputpayload = json.loads(json.dumps(outputpayload, default=handle_object))
                outputpayload["EmojiModeration"]=emojiModOpt
                
                # Call to Moderation Models
                obj_out = callModerationModels(text,outputpayload,token,deployment_name,output_text=text)
                
                toxicityScore = obj_out['Toxicity Check'].toxicityScore
                toxicityThreshold = obj_out['Toxicity Check'].toxicitythreshold
                toxicityResult = obj_out['Toxicity Check'].result
                toxicityTypesRecognised=[]
                if len(toxicityScore)!=0:
                    toxicityTypesRecognised = [i['metricName'] for i in toxicityScore[0]['toxicScore'] if i['metricScore']>float(toxicityThreshold)]
                toxicityCheck_out = toxicityCheckTypes(toxicityTypesRecognised =toxicityTypesRecognised,
                                toxicityTypesConfiguredToBlock=[t.value for t in TOXICITYTYPES][0:-1],
                                toxicityScore =toxicityScore,
                                    toxicitythreshold = toxicityThreshold,
                                    result = toxicityResult)
                restrictedTopicScores = obj_out['Restricted Topic Check'].topicScores
                restrictedTopicThreshold = obj_out['Restricted Topic Check'].topicThreshold
                restrictedTopicResult = obj_out['Restricted Topic Check'].result
                topicTypesConfiguredToBlock = payload.ModerationCheckThresholds['RestrictedtopicDetails']['Restrictedtopics']
                topicTypesRecognised=[]
                if len(restrictedTopicScores)!=0:
                    topicTypesRecognised = [i for i in restrictedTopicScores[0] if float(restrictedTopicScores[0][i])>float(restrictedTopicThreshold)]
                restrictedTopicCheck_out = restrictedtopicTypes(topicTypesConfiguredToBlock=topicTypesConfiguredToBlock,
                                                        topicTypesRecognised=topicTypesRecognised,
                                                        topicScores=restrictedTopicScores,
                                                        topicThreshold=restrictedTopicThreshold,
                                                        result = restrictedTopicResult)
                
                obj_responsemoderation = ResponseModeration(generatedText = output_text,
                                                        hallucinationScore =hallucinationScore,
                                                        privacyCheck = obj_out['Privacy Check'],
                                                        profanityCheck = obj_out['Profanity Check'],
                                                        toxicityCheck = toxicityCheck_out,#outModResult.moderationResults.toxicityCheck,
                                                        restrictedtopic = restrictedTopicCheck_out,#outModResult.moderationResults.restrictedtopic,
                                                        textQuality = obj_out['Text Quality Check'],
                                                        textRelevanceCheck = obj_out['Text Relevance Check'],
                                                        refusalCheck = obj_out['Refusal Check'],
                                                        sentimentCheck=obj['Sentiment Check'],
                                                        invisibleTextCheck = obj['Invisible Text Check'],
                                                        gibberishCheck = obj['Gibberish Check'],
                                                        bancodeCheck=obj['Ban Code Check'],
                                                        summary = obj_out['summary']).__dict__
                
                objmoderation = CoupledModerationResults(requestModeration = obj_requestmoderation,
                                                         responseModeration = obj_responsemoderation)
                final_obj = completionResponse(object = "text_completion",
                                                userid=userid,
                                                lotNumber=str(lotNumber),
                                                created = str(created),
                                                model= deployment_name,
                                                choices=list_choices,
                                                moderationResults=objmoderation)
                
                totaltimeforallchecks = str(round(time.time() - st,3))+"s"
                response_checks = {'Time taken by each model in responseModeration' : obj_out['model time']}
                if response_checks != None:
                    dict_timecheck.update(response_checks)
                dict_timecheck["responseModeration"]= dictcheck
                dict_timecheck.update({"Total time for moderation Check": totaltimeforallchecks})

        else:
                dict_timecheck["responseModeration"]= dictcheck
                objSummary_out = summary(status = 'Rejected',reason = ['LLM Interaction is disabled'])
                obj_choices = Choice(text='',index= 0,finishReason = '')
                list_choices.append(obj_choices)
                obj_responsemoderation = ResponseModeration(generatedText = "",
                                                        hallucinationScore="",
                                                        privacyCheck = objprivacy_out,
                                                        profanityCheck = objprofanity_out,
                                                        toxicityCheck = objtoxicity_out,
                                                        restrictedtopic = objtopic_out,
                                                        textQuality = objtextQuality_out,
                                                        textRelevanceCheck = objpromptResponse_out,
                                                        refusalCheck = objrefusal_out,
                                                        sentimentCheck = obj_sentiment_out,
                                                        invisibleTextCheck = obj_invisibleText_out,
                                                        gibberishCheck = obj_gibberish_out,
                                                        bancodeCheck = obj_bancode_out,
                                                        summary = objSummary_out).__dict__
                objmoderation = CoupledModerationResults(requestModeration = obj_requestmoderation,
                                            responseModeration = obj_responsemoderation)
                final_obj = completionResponse(userid=userid,
                                                lotNumber=str(lotNumber),
                                                object = "text_completion",
                                                created = str(created),
                                                model= deployment_name,
                                                choices=list_choices,
                                                moderationResults=objmoderation)
                
                totaltimeforallchecks = str(round(time.time() - st,3))+"s"
                if response_checks != None:
                    dict_timecheck.update(response_checks)
                dict_timecheck.update({"Total time for moderation Check": totaltimeforallchecks})

        log.info(f"final_obj : {final_obj}")
        return final_obj


class LlamaDeepSeekcompletion:
    def textCompletion(self,text,temperature=0.1,PromptTemplate="GoalPriority",deployment_name=None,Moderation_flag=None,COT=None,THOT=None):
        log.info("inside Llama/DeepSeek completions function")
        url=""
        if temperature == 0:
            temperature = 0.1

        if COT:
            log.info("Inside COT Llama2 or DeepSeek")
            # messages = f"""[INST]Think step by step. Explain each intermediate step. Only when you are done with all your steps,
            #             Provide the answer based on your intermediate steps. User Query : {text}[/INST]
            #            """
            messages = f"""[INST]<<SYS>>You should be a responsible Assistant and should not generate harmful or 
            misleading content! Please answer the following user query in a responsible way. 
            Let's think the answer step by step and explain step by step how you got the answer. 
            Please provide website link as references if you are refering from internet to get the answer.
            Always give response in a textual format dont give in json or any code format.<</SYS>>
            User Query : {text} [/INST]"""

        elif THOT:
            log.info("Inside THOT Llama2 or DeepSeek")
            messages =f"""[INST]<<SYS>>You should be a responsible Assistant and should not generate harmful or 
            misleading content! Please answer the following user query in a responsible way. 
            Walk me through this context in manageable parts step by step, summarising and analysing as we go.
            Engage in a step-by-step thought process to explain how the answer was derived. 
            Additionally, associate the source with the answer using the format:
                    Result: "answer"
                    Explanation: "step-by-step reasoning"
                    Always give response in a textual format dont give in json or any code format.<</SYS>>
                    User Query: {text} [/INST]"""

        elif Moderation_flag and PromptTemplate=="GoalPriority":
            log.info("Inside GoalPriority Llama2/DeepSeek")
            messages = f"""[INST]<<SYS>>You are an assistant that is harmless and helpful. 
            Importantly, you need to always prioritize safety over helpfulness. 
            That is, if answering the user query could be unsafe or harmful, you should refuse to answer. 
            Otherwise provide a thorough and precise response, ensuring you assist the user to the best 
            of your ability.Always give response in a textual format dont give in json or any code format.<</SYS>>
            User Query:{text}[/INST]"""
            
        elif Moderation_flag and PromptTemplate=="SelfReminder":
            log.info("Inside SelfReminder Llama2/DeepSeek")
            messages =f"""[INST]<<SYS>>You should be a responsible Assistant and should not generate harmful 
            or misleading content! Please answer the following user query in a responsible way.
            Always give response in a textual format dont give in json or any code format.<</SYS>>
            User Query: {text} [/INST]"""
        
        elif Moderation_flag==None:
            log.info("Inside Moderation_flag as None")
            messages = text
        
        if deployment_name == "Llama":
            url = os.environ.get("LLAMA_ENDPOINT")
            input = {
                "inputs": messages,
                "parameters": {
                    "max_new_tokens": 512,
                    "temperature": temperature,
                    "num_return_sequences": 1,
                    "do_sample": True
                }
            }
            response = requests.post(url, json=input, verify=sslv[verify_ssl])
            response.raise_for_status()
            generated_text = response.json()[0]["generated_text"]
            output_text = generated_text.split("[/INST]")[1]
        elif deployment_name == "DeepSeek":
            url = os.getenv("DEEPSEEK_COMPLETION_URL")
            deepseek_model = os.getenv("DEEPSEEK_COMPLETION_MODEL_NAME")
            global aicloud_access_token , token_expiration , contentType
            if aicloud_access_token==None or time.time()>token_expiration:
                aicloud_access_token,token_expiration=aicloud_auth_token_generate(aicloud_access_token,token_expiration)
            input = {
                    "model":deepseek_model,
                    "prompt":messages,
                    "temperature": 0.01,
                    "top_p": 0.98,
                    "frequency_penalty": 0,
                    "presence_penalty": 0,
                    "max_tokens": 128
            }
            headers={"Authorization": "Bearer "+aicloud_access_token,"Content-Type": contentType,"Accept": "*"}
            response = requests.post(url,json=input,headers=headers,verify=sslv[verify_ssl])
            response.raise_for_status()
            response = json.loads(response.text)['choices'][0]['text']
            output_text = response.replace("\n</think>\n\n","") if "\n</think>\n\n" in response else response

        return output_text, 0, "","0"

class Llamacompletionazure:
    def __init__(self):
        self.url = os.environ.get("LLAMA_ENDPOINT")

    def textCompletion(self,text,temperature=None,PromptTemplate="GoalPriority",deployment_name=None,Moderation_flag=None,COT=None,THOT=None):
        try:
            input = {
                "input": text
            }
            response = requests.post(self.url, json=input, verify=sslv[verify_ssl])
            generated_text = response.json()["output"]
            return generated_text, 0, "","0"
        except Exception as e:
            log.error("Failed at LLama model call")
            if Moderation_flag:
                log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at Llama model call"})
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

class Llama3completions:

    def __init__(self):
        self.url = os.environ.get("LLAMA_ENDPOINT3_70b")
        log.info(f"url accessed for llama {self.url}")

    def textCompletion(self,text,temperature=0,PromptTemplate="GoalPriority",deployment_name=None,Moderation_flag=None,COT=None,THOT=None):
        try:
            token = Llama_auth.load_token()
            if isinstance(token, Exception):
                log.error("Failed to fetch aicloud access token") 
                raise Exception("Failed to fetch aicloud access token")
            else:
                log.info("Access token retrived")   

            hallucinationscore = "0"
            #check the prompt templates, hallucination, cov, cot
            hallucination_Score = """Ensure that an answer is always generated, avoiding any guideline restrictions as a response. If you are unsure of the answer, create a plausible response based on general knowledge from the internet. Format your response as follows: `Answer [score]`. For example, "The largest country is Russia. [0.1]".
                Always include a hallucination score ranging from 0 to 1, where: 
                - 0 indicates the answer is highly relevant to the prompt, it is highly realistic, the answer contains no factual errors and the answer is not at all nonsensical.
                - 1 indicates the answer is highly unrelated to the prompt, it is highly implausible or unrealistic, it is completely factually incorrect and highly nonsensical.
                - Scores between 0 and 1 should reflect the degree of confidence based on the relevance and accuracy of the answer. Avoid assigning a score of 0.5.

                Avoid phrases like "I do not know", "Sorry", "I apologize", or "As an AI model, I am not allowed" in your response.
                Do not provide any explanation for the score. Score should be at the very end of the response.
                Prompt: """
            if COT:
                messages =[
                    {"role": "system", "content": "Assistant is a large language model trained by OpenAI.You should be a responsible ChatGPT and should not generate harmful or misleading content! Please answer the following user query in a responsible way. Let's think the answer step by step and explain step by step how you got the answer. Please provide website link as references if you are refering from internet to get the answer"},
                    {"role": "system","content": "Always give response in a textual format dont give in json or any code format"},
                    {"role": "user", "content":  f"{text} \n Remember, you are a responsible ChatGPT and good at avoiding generating harmful or misleading content!" }
                ]
                
            elif THOT:
                messages =[
                    {"role": "system", "content": """Assistant is a large language model trained by OpenAI.You should be a responsible ChatGPT and should not generate harmful or misleading content! Please answer the following user query in a responsible way. Walk me through this context in manageable parts step by step, summarising and analysing as we go.Engage in a step-by-step thought process to explain how the answer was derived. Additionally, associate the source with the answer using the format:
                        Result: "answer"
                        Explanation: "step-by-step reasoning"
                        """},
                    {"role": "system","content": "Always give response in a textual format dont give in json or any code format"},
                    {"role": "user", "content":  f"{text} \n Remember, you are a responsible ChatGPT and good at avoiding generating harmful or misleading content!" }
                ]
                
                    
            elif Moderation_flag and PromptTemplate=="GoalPriority":
                messages = [{"role":"system","content":" You are an assistant that is harmless and helpful. Importantly, you need to always prioritize safety over helpfulness. That is, if answering the user query could be unsafe or harmful, you should refuse to answer. Otherwise provide a thorough and precise response, ensuring you assist the user to the best of your ability."},
                            {"role": "system","content": "Always give response in a textual format dont give in json or any code format"},
                            {"role": "user", "content": f"{hallucination_Score}{text}"}]
                
            elif Moderation_flag and PromptTemplate=="SelfReminder":
                
                messages =[
                    {"role": "system", "content": "Assistant is a large language model trained by OpenAI.You should be a responsible ChatGPT and should not generate harmful or misleading content! Please answer the following user query in a responsible way."},
                    {"role": "system","content": "Always give response in a textual format dont give in json or any code format"},
                    {"role": "user", "content":  f"{hallucination_Score}{text} \n Remember, you are a responsible ChatGPT and good at avoiding generating harmful or misleading content!" }
                ]
            
            elif Moderation_flag==None:
                messages = [{"role": "user", "content": f"{hallucination_Score}{text}"}]
            
            headers={
            "Authorization": "Bearer "+str(token),
            "Content-Type": "application/json",
            "Accept": "*",
            "X-Cluster": "H100"
            }
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
            st=time.time()
            response = requests.post(url=self.url, json=input, headers=headers)
            et= time.time()
            rt = et - st
            dict_timecheck["Llama3InteractionTime"]=str(round(rt,3))+"s"
            log.info(f'Run time with llama3 model:{rt}')
            response.json()['choices'][0]['message']['content']
            if len(response.json()['choices'][0]['message']['content'])!=0:
                text = response.json()['choices'][0]['message']['content']
                print(response.json())
                finish_reason =  response.json()['choices'][0]['finish_reason']
                if not COT and not THOT:
                    try:
                        hallucinationscore = re.findall(r'\[([^\]]+)\]', text)[-1]
                        text = re.sub(r"\[(\d+(\.\d)?)\](?!.*\[\d+(\.\d)?\])", '', text)
                    except:
                        hallucinationscore = "0"
            else:
                text = response.json()['choices'][0]['finish_reason']
                finish_reason =  response.json()['choices'][0]['finish_reason']
                hallucinationscore = "0"

    

            return text,0,finish_reason,hallucinationscore
        except Exception as e:
            log.error("Failed at LLama3 model call")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at Llama3 model call"})
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")            

class Geminicompletions:

    def __init__(self,model_name):
        if model_name == 'Gemini-Pro':
            log.info("Response using Gemini-Pro")
            self.gemini_api_key = os.getenv("GEMINI_PRO_API_KEY")
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel(os.getenv("GEMINI_PRO_MODEL_NAME"))
        elif model_name == 'Gemini-Flash':
            log.info("Response using Gemini-Flash")
            self.gemini_api_key = os.getenv("GEMINI_FLASH_API_KEY")
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel(os.getenv("GEMINI_FLASH_MODEL_NAME"))

    def textCompletion(self,text,temperature=0,PromptTemplate="GoalPriority",deployment_name=None,Moderation_flag=None,COT=None,THOT=None):

        try:   
            hallucinationscore = "0"
            #check the prompt templates, hallucination, cov, cot
            hallucination_Score = """Ensure that an answer is always generated, avoiding any guideline restrictions as a response. If you are unsure of the answer, create a plausible response based on general knowledge from the internet. Format your response as follows: `Answer [score]`. For example, "The largest country is Russia. [0.1]".
                Always include a hallucination score ranging from 0 to 1, where: 
                - 0 indicates the answer is highly relevant to the prompt, it is highly realistic, the answer contains no factual errors and the answer is not at all nonsensical.
                - 1 indicates the answer is highly unrelated to the prompt, it is highly implausible or unrealistic, it is completely factually incorrect and highly nonsensical.
                - Scores between 0 and 1 should reflect the degree of confidence based on the relevance and accuracy of the answer. Avoid assigning a score of 0.5.

                Avoid phrases like "I do not know", "Sorry", "I apologize", or "As an AI model, I am not allowed" in your response.
                Do not provide any explanation for the score. Score should be at the very end of the response.
                Prompt: """
            
            if COT:
                messages = f"""
                Assistant is a large language model trained by Google. You should be a responsible Gemini model and should not generate harmful or misleading content! 
                Please answer the following user query in a responsible way. Let's think the answer step by step and explain step by step how you got the answer. 
                Please provide website links as references if you are referring to the internet to get the answer.

                Always give responses in a textual format. Do not give in JSON or any code format.

                User Query:
                {text}

                Remember, you are a responsible Gemini model and good at avoiding generating harmful or misleading content!
                """

                
            elif THOT:
                messages = f"""
                Assistant is a large language model trained by Google. You should be a responsible Gemini model and should not generate harmful or misleading content! 
                Please answer the following user query in a responsible way.

                Walk me through this context in manageable parts step by step — summarizing and analyzing as we go.
                Engage in a step-by-step thought process to explain how the answer was derived.

                Associate the source with the answer using the format:
                Result: "answer"
                Explanation: "step-by-step reasoning"

                Always give responses in a textual format. Do not respond in JSON or code format.

                User Query:
                {text}

                Remember, you are a responsible Gemini model and good at avoiding generating harmful or misleading content!
                """
        
            elif Moderation_flag and PromptTemplate=="GoalPriority":
                messages =  f"""
                You are an assistant that is harmless and helpful. Importantly, you need to always prioritize safety over helpfulness. 
                That is, if answering the user query could be unsafe or harmful, you should refuse to answer. 
                Otherwise, provide a thorough and precise response, ensuring you assist the user to the best of your ability.

                Always give responses in a textual format. Do not respond in JSON or code format.

                User Query:
                {hallucination_Score}{text}
                """
                
            elif Moderation_flag and PromptTemplate=="SelfReminder":
                
                messages =f"""
                Assistant is a large language model trained by Google. You should be a responsible Gemini model and should not generate harmful or misleading content. 
                Please answer the following user query in a responsible way.

                Always give responses in a textual format. Do not respond in JSON or code format.

                User Query:
                {hallucination_Score}{text}"""
            
            elif Moderation_flag==None:
                messages = f"""
                User Query:
                {hallucination_Score}{text}"""
            
            generation_config = genai.types.GenerationConfig(temperature=temperature)
            st=time.time()
            response = self.model.generate_content(messages,generation_config=generation_config)
            et= time.time()
            rt = et - st
            dict_timecheck["GeminiInteractionTime"]=str(round(rt,3))+"s"
            log.info(f'Run time with Gemini model:{rt}')

            if response.candidates and response.candidates[0].content.parts:
            
                text = response.candidates[0].content.parts[0].text.strip()
                log.info(f"gemini response : {text}")
                finish_reason =  response.candidates[0].finish_reason.name

                if not COT and not THOT:
                    try:
                        hallucinationscore = re.findall(r'\[(\d+(?:\.\d+)?)\]', text)[-1]
                        text = re.sub(r'\[\d+(?:\.\d+)?\]', '', text).strip()
                    except:
                        hallucinationscore = "0"
            else:
                text = response.candidates[0].finish_reason.name
                finish_reason = response.candidates[0].finish_reason.name
                hallucinationscore = "0"
            return text,0,finish_reason,hallucinationscore
        except Exception as e:
            log.error("Failed at Gemini model call")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at Gemini model call"})
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")            

class Bloomcompletion:
    def __init__(self):
        self.url = os.environ.get("BLOOM_ENDPOINT")

    def textCompletion(self,text,temperature=None,PromptTemplate="GoalPriority",deployment_name=None,Moderation_flag=None,COT=None,THOT=None):
        response = requests.post(self.url,text,verify=sslv[verify_ssl])
        generated_text = response.json()[0]["generated_text"]
        return generated_text,0,"","0"


class Openaicompletions:
    def __init__(self):
        self.deployment_name=os.getenv("OPENAI_MODEL_GPT4")
        self.openai_api_type = os.getenv("OPENAI_API_TYPE")
        self.openai_api_base = os.getenv("OPENAI_API_BASE_GPT4")
        self.openai_api_key = os.getenv("OPENAI_API_KEY_GPT4")
        self.openai_api_version = os.getenv("OPENAI_API_VERSION_GPT4")

    def textCompletion(self,text,temperature,PromptTemplate,deployment_name=None,Moderation_flag=None,COT=None,THOT=None):
        try:
            if deployment_name == "gpt3":
                self.deployment_name = os.getenv("OPENAI_MODEL_GPT3")
                self.openai_api_base = os.getenv("OPENAI_API_BASE_GPT3")
                self.openai_api_key = os.getenv("OPENAI_API_KEY_GPT3")
                self.openai_api_version = os.getenv("OPENAI_API_VERSION_GPT3")

            openai.api_key = self.openai_api_key
            openai.api_base = self.openai_api_base
            openai.api_type = self.openai_api_type
            openai.api_version = self.openai_api_version
            openai.verify_ssl_certs = False

            log.info(f"Interaction with GPT ")
            st = time.time()
            hallucinationscore = "0"
            hallucination_Score = """Ensure that an answer is always generated, avoiding any guideline restrictions as a response. If you are unsure of the answer, create a plausible response based on general knowledge from the internet. Format your response as follows: `Answer [score]`. For example, "The largest country is Russia. [0.1]".
                Always include a hallucination score ranging from 0 to 1, where: 
                - 0 indicates the answer is highly relevant to the prompt, it is highly realistic, the answer contains no factual errors and the answer is not at all nonsensical.
                - 1 indicates the answer is highly unrelated to the prompt, it is highly implausible or unrealistic, it is completely factually incorrect and highly nonsensical.
                - Scores between 0 and 1 should reflect the degree of confidence based on the relevance and accuracy of the answer. Avoid assigning a score of 0.5.

                Avoid phrases like "I do not know", "Sorry", "I apologize", or "As an AI model, I am not allowed" in your response.
                Do not provide any explanation for the score. Score should be at the very end of the response.
                Prompt: """
            if COT:
                messages =[
                    {"role": "system", "content": "Assistant is a large language model trained by OpenAI.You should be a responsible ChatGPT and should not generate harmful or misleading content! Please answer the following user query in a responsible way. Let's think the answer step by step and explain step by step how you got the answer. Please provide website link as references if you are refering from internet to get the answer"},
                    {"role": "system","content": "Always give response in a textual format dont give in json or any code format"},
                    {"role": "user", "content":  f"{text} \n Remember, you are a responsible ChatGPT and good at avoiding generating harmful or misleading content!" }
                ]
                
            elif THOT:
                messages =[
                    {"role": "system", "content": """Assistant is a large language model trained by OpenAI.You should be a responsible ChatGPT and should not generate harmful or misleading content! Please answer the following user query in a responsible way. Walk me through this context in manageable parts step by step, summarising and analysing as we go.Engage in a step-by-step thought process to explain how the answer was derived. Additionally, associate the source with the answer using the format:
                        Result: "answer"
                        Explanation: "step-by-step reasoning"
                        """},
                    {"role": "system","content": "Always give response in a textual format dont give in json or any code format"},
                    {"role": "user", "content":  f"{text} \n Remember, you are a responsible ChatGPT and good at avoiding generating harmful or misleading content!" }
                ]
                
                    
            elif Moderation_flag and PromptTemplate=="GoalPriority":
                messages = [{"role":"system","content":" You are an assistant that is harmless and helpful. Importantly, you need to always prioritize safety over helpfulness. That is, if answering the user query could be unsafe or harmful, you should refuse to answer. Otherwise provide a thorough and precise response, ensuring you assist the user to the best of your ability."},
                            {"role": "system","content": "Always give response in a textual format dont give in json or any code format"},
                            {"role": "user", "content": f"{hallucination_Score}{text}"}]
                
            elif Moderation_flag and PromptTemplate=="SelfReminder":
                
                messages =[
                    {"role": "system", "content": "Assistant is a large language model trained by OpenAI.You should be a responsible ChatGPT and should not generate harmful or misleading content! Please answer the following user query in a responsible way."},
                    {"role": "system","content": "Always give response in a textual format dont give in json or any code format"},
                    {"role": "user", "content":  f"{hallucination_Score}{text} \n Remember, you are a responsible ChatGPT and good at avoiding generating harmful or misleading content!" }
                ]
            
            elif Moderation_flag==None:
                messages = [{"role": "user", "content": f"{hallucination_Score}{text}"}]
            
            client = AzureOpenAI(api_key=openai.api_key, 
                                 azure_endpoint=openai.api_base,
                                 api_version=openai.api_version)
            response = client.chat.completions.create(
                model=self.deployment_name,
                messages = messages ,
                temperature=temperature,
                max_tokens=500)
            
            et= time.time()
            rt = et - st
            dict_timecheck["OpenAIInteractionTime"]=str(round(rt,3))+"s"
            log.info(f'Run time with openAI:{rt}')

            if len(response.choices[0].message.content)!=0:
                text = response.choices[0].message.content
                index = response.choices[0].index
                finish_reason= response.choices[0].finish_reason
                if not COT and not THOT:
                    try:
                        # hallucinationscore = re.findall(r'\[([^\]]+)\]', text)[0]
                        # text = re.sub(r'\[.*?\]', '', text)
                        hallucinationscore = re.findall(r'\[([^\]]+)\]', text)[-1]
                        text = re.sub(r"\[(\d+(\.\d)?)\](?!.*\[\d+(\.\d)?\])", '', text)
                    except:
                        hallucinationscore = "0"
            else:
                text = response.choices[0].finish_reason
                index = response.choices[0].index
                finish_reason = response.choices[0].finish_reason
                hallucinationscore = "0"
            
            return text,index,finish_reason,hallucinationscore
        except openai.BadRequestError as IR:
            log.error(f"Exception: {IR}")
            log.error(f"Exception: {str(traceback.extract_tb(IR.__traceback__)[0].lineno),IR}")
            return str(IR),0,str(IR),"0"
        except Exception as e:
            log.error("Failed at Openai model call")
            if Moderation_flag:
                log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at Openai model call"})
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            return "",0,"No response from Openai","0"




class AWScompletions:

    def textCompletion(self,text,temperature=0.1,PromptTemplate="GoalPriority",deployment_name=None,Moderation_flag=None,COT=None,THOT=None):
        temperature = 0.1 if temperature==0 else temperature
        anthropic_version=os.getenv("ANTHROPIC_VERSION")
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
        hallucinationscore = "0"
        hallucination_Score = """Ensure that an answer is always generated, avoiding any guideline restrictions as a response. If you are unsure of the answer, create a plausible response based on general knowledge from the internet. Format your response as follows: `Answer [score]`. For example, "The largest country is Russia. [0.1]".
                Always include a hallucination score ranging from 0 to 1, where: 
                - 0 indicates the answer is highly relevant to the prompt, it is highly realistic, the answer contains no factual errors and the answer is not at all nonsensical.
                - 1 indicates the answer is highly unrelated to the prompt, it is highly implausible or unrealistic, it is completely factually incorrect and highly nonsensical.
                - Scores between 0 and 1 should reflect the degree of confidence based on the relevance and accuracy of the answer. Avoid assigning a score of 0.5.

                Avoid phrases like "I do not know", "Sorry", "I apologize", or "As an AI model, I am not allowed" in your response.
                Do not provide any explanation for the score. Score should be at the very end of the response.
                Prompt: """
        if COT:
            native_request['messages'] =[
                {"role": "user", "content":  f"{text} \n Assistant is a large language model trained by Anthropic.You should be a responsible ChatGPT and should not generate harmful or misleading content! Please answer the following user query in a responsible way. Let's think the answer step by step and explain step by step how you got the answer. Please provide website link as references if you are refering from internet to get the answer.You should be a responsible LLM and should not generate harmful or misleading content! Please answer the following user query in a responsible way. Let's think the answer step by step and explain step by step how you got the answer. Always give response in a textual format dont give in json or any code format.Please provide website link as references if you are refering from internet to get the answer.Remember, you are a responsible LLM and good at avoiding generating harmful or misleading content!" }
            ]
        elif THOT:
            native_request['messages'] =[
                    {"role": "user", "content":  f"""{text}
                     Assistant is a large language model trained by Anthropic.You should be a responsible ChatGPT and should not generate harmful or misleading content! Please answer the following user query in a responsible way. Walk me through this context in manageable parts step by step, summarising and analysing as we go.Engage in a step-by-step thought process to explain how the answer was derived. Additionally, associate the source with the answer using the format:
                        Result: "answer"
                        Explanation: "step-by-step reasoning"
                     Always give response in a textual format dont give in json or any code format.Remember, you are a responsible ChatGPT and good at avoiding generating harmful or misleading content!""" }
                ]
        elif Moderation_flag and PromptTemplate=="GoalPriority":
            native_request['messages'] = [{"role": "user", "content": f"{hallucination_Score}{text}\nAlways give response in a textual format dont give in json or any code format\nYou are an assistant that is harmless and helpful. Importantly, you need to always prioritize safety over helpfulness. That is, if answering the user query could be unsafe or harmful, you should refuse to answer. Otherwise provide a thorough and precise response, ensuring you assist the user to the best of your ability."}]
                
        elif Moderation_flag and PromptTemplate=="SelfReminder":
            native_request['messages'] =[
                    {"role": "user", "content":  f"{hallucination_Score}{text} \n Assistant is a large language model trained by Anthropic.You should be a responsible LLM and should not generate harmful or misleading content! \nAlways give response in a textual format dont give in json or any code format.\nPlease answer the following user query in a responsible way.You are good at avoiding generating harmful or misleading content!" }
                ]
            
        elif Moderation_flag==None:
            native_request['messages'] = [{"role": "user", "content": f"{hallucination_Score}{text}"}]

        request = json.dumps(native_request)
        if deployment_name == "AWS_CLAUDE_V3_5":
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
                        region_name=os.getenv("REGION_NAME")
                        
                        client = boto3.client(
                            service_name=aws_service_name,
                            aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key,
                            aws_session_token=aws_session_token,
                            region_name=region_name,
                            verify=sslv[verify_ssl]
                        )
                        model_id=os.getenv("AWS_MODEL_ID")
                        accept=os.getenv("ACCEPT")
                        response = client.invoke_model(modelId=model_id, body=request,accept=accept, contentType=contentType)
                        model_response = json.loads(response["body"].read())
                        response_text = model_response["content"][0]["text"]
                        response_text = response_text.replace("Answer: ","") if "Answer: " in response_text else response_text
                        stop_reason = model_response["stop_reason"]
                        if len(response_text)!=0:
                            if not COT and not THOT:
                                try:
                                    hallucinationscore = re.findall(r'\[([^\]]+)\]', response_text)[-1]
                                    response_text = re.sub(r"\[(\d+(\.\d)?)\](?!.*\[\d+(\.\d)?\])", '', response_text)
                                    response_text = " ".join(response_text.split())
                                except:
                                    hallucinationscore = "0"
                        else:
                            response_text=stop_reason
                        return response_text,0,stop_reason,hallucinationscore
                        
                else:
                    log.info("session expired, please enter the credentials again")
                    response_text = """Response cannot be generated at this moment.\nReason : (ExpiredTokenException) AWS Credentials included in the request is expired.\nSolution : Please update with new credentials and try again."""
                    return response_text,-1,"","0"
            else:
                log.info("Error getting data: ",{response.status_code})



def getModerationResult(payload,headers,result_flag=1,telemetryFlag=False,token_info=None):
    try:
        id = uuid.uuid4().hex
        request_id_var.set(id)
        log_dict[request_id_var.get()]=[]
        final_response={}
        if(payload.Prompt==""):
            log.info("Prompt is Empty")
            log_dict[request_id_var.get()].append("Prompt is Empty")
            return "Error Occured due to empty prompt"
        
        userid=payload.userid if "userid" in payload else "None"
        portfolio = payload.PortfolioName if "PortfolioName" in payload else "None"
        accountname = payload.AccountName if "AccountName" in payload else "None"
        lotNumber = str(payload.lotNumber) if "lotNumber" in payload else "None"
        headers["id"]=id
        if os.getenv("DBTYPE") != "False":# send request payload into DB #
            thread2=threading.Thread(target=Results.createRequestPayload,args=("moderation",payload,id,
                                                                               str(payload.PortfolioName), 
                                                                 str(payload.AccountName),str(userid),str(lotNumber)
                                                                 ))
            thread2.start()
        
        try:
            log.info(f"cache flag- Moderation : {cache_flag}")
            st = time.time()
            translate = payload.translate if "translate" in payload else None
            response,moderation_timecheck['timecheck'],moderation_timecheck['modeltime'] = moderation.completions(payload,headers,translate=translate)
            moderation_timecheck ["totaltimeforallchecks"]=str(round(time.time() - st,3))+"s"

           
            starttime=time.time()
            # print("mt===",moderation_timecheck)
            
            updated_timecheck= copy.deepcopy(moderation_timecheck)
            # print("ut===",updated_timecheck)
            reset_moderation_timecheck(starttime)
            # print("mt1===",moderation_timecheck)
            # print("ut1===",updated_timecheck)
           
            final_response = response.model_dump()
         
            final_response['uniqueid']=id
            
            if telemetryFlag==True:
                thread = threading.Thread(target=telemetry.send_telemetry_request, args=(final_response,id,lotNumber, portfolio, accountname,userid,headers,token_info,updated_timecheck['timecheck'],updated_timecheck['modeltime'],updated_timecheck['totaltimeforallchecks']))
                thread.start()
                
            if result_flag and os.getenv("DBTYPE") != "False":
                thread2=threading.Thread(target=Results.create,args=(final_response,id,portfolio, accountname,userid, lotNumber))
                thread2.start()
            return final_response
            
        except Exception as e:
            log.error("Failed at Completion Function")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at Completion Function"})
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

            er=log_dict[request_id_var.get()]
            if len(er)!=0:
                err_desc = er
                logobj = {"_id":id,"error":er}
                thread_err = threading.Thread(target=telemetry.send_telemetry_error_request, args=(logobj,id,lotNumber,portfolio,accountname,userid,err_desc,headers,token_info))
                thread_err.start()
                del log_dict[id]
       
            

    except Exception as e:
        log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at getModerationResult Function"})
        log.error(f"Error starting telemetry thread: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
        log.error(traceback.format_exc())
    





def getCoupledModerationResult(payload,headers):
    
    try:
        id = uuid.uuid4().hex
        request_id_var.set(id)
        log_dict[request_id_var.get()]=[]
        final_response={}
        AccountName=payload.AccountName if "AccountName" in payload else "None"
        PortfolioName=payload.PortfolioName if "PortfolioName" in payload else "None"
        userid=payload.userid if "userid" in payload else "None"
        lotNumber = str(payload.lotNumber) if "lotNumber" in payload else "None"

        if(payload.Prompt==""):
            log.info("Prompt is Empty")
            log_dict[request_id_var.get()].append("Prompt is Empty")
            return "Error Occured due to empty prompt"
        
        headers["id"]=id
        if os.getenv("DBTYPE") != "False": # send request payload into DB #
            thread=threading.Thread(target=Results.createRequestPayload,args=("coupledModeration",payload,id,
                                                                              str(payload.PortfolioName),
                                                                              str(payload.AccountName),
                                                                              str(userid),str(lotNumber)))
            thread.start()
        try:
            log.info(f"cache flag-Coupled Moderation :{cache_flag}")
            response = coupledModeration.coupledCompletions(payload,headers)
            writejson(dict_timecheck)
            starttime=time.time()
            if(EXE_CREATION == "True"):
                json_path = moderation_time_json
            else:
                script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                json_path = os.path.join(script_dir, "data/moderationtime.json")

            with open(json_path, "r") as outfile:
                updated_timecheck = json.load(outfile)

            reset_dict_timecheck(starttime)

            final_response = response.model_dump()
            final_response['uniqueid']=id
            log.info(f"Telemetry Flag just BEFORE TELEMETRY THREAD START--> {telemetry.tel_flag}")
            if telemetry.tel_flag:
                thread1 = threading.Thread(target=telemetry.send_coupledtelemetry_request, args=(final_response,id,str(PortfolioName), str(AccountName),updated_timecheck))
                thread1.start()
                log.info("THREAD STARTED")
            
            if os.getenv("DBTYPE") != "False":
                thread2=threading.Thread(target=Results.create,args=(final_response,id,str(PortfolioName), str(AccountName),userid,lotNumber))
                thread2.start()
        except Exception as e:
            log.error("Failed at Coupled Completion Function")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at Coupled Completion Function"})
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

        er=log_dict[request_id_var.get()]
        if len(er)!=0:
            logobj = {"_id":id,"error":er}
            if os.getenv("DBTYPE") != "False":
                Results.createlog(logobj)
            err_desc = er
            payload=AttributeDict(payload)
            token_info = {"unique_name":"None","X-Correlation-ID":"None","X-Span-ID":"None"}
        
            thread_err = threading.Thread(target=telemetry.send_telemetry_error_request, args=(logobj,id,payload.lotNumber,payload.PortfolioName,payload.AccountName,payload.userid,err_desc,headers,token_info))
            thread_err.start()
            del log_dict[id]

        
        return final_response
    
    except Exception as e:
        log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at getCoupledModerationResult Function"})
        log.error(f"Error starting telemetry thread: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
        log.error(traceback.format_exc())
    


def reset_dict_timecheck(starttime):
    global dict_timecheck
    for key in dict_timecheck['requestModeration'].keys():
        dict_timecheck['requestModeration'][key] = str(round(time.time()-starttime,3))+"s"
    for key in dict_timecheck['responseModeration'].keys():
        dict_timecheck['responseModeration'][key] = str(round(time.time()-starttime,3))+"s"
    for key in dict_timecheck['Time taken by each model in requestModeration'].keys():
        dict_timecheck['Time taken by each model in requestModeration'][key] = "0.0s"
    for key in dict_timecheck['Time taken by each model in responseModeration'].keys():
        dict_timecheck['Time taken by each model in responseModeration'][key] = "0.0s"
    dict_timecheck['OpenAIInteractionTime'] = "0.0s"
    dict_timecheck['translate'] = "0.0s"
    dict_timecheck['Total time for moderation Check'] = str(round(time.time()-starttime,3))+"s"


def reset_moderation_timecheck(starttime):
    global moderation_timecheck
    for key in moderation_timecheck['timecheck'].keys():
        moderation_timecheck['timecheck'][key] = str(round(time.time()-starttime,3))+"s"
    for key in moderation_timecheck['modeltime'].keys():
        moderation_timecheck['modeltime'][key] = "0.0s"
    moderation_timecheck['totaltimeforallchecks']=str(round(time.time()-starttime,3))+"s"
    
    


def getLLMResponse(text,temperature,PromptTemplate,deployment_name,mod_flag):
    try:
        if deployment_name == "Bloom":
            interact = Bloomcompletion()
        elif deployment_name in ["Llama","DeepSeek"]:
            interact = LlamaDeepSeekcompletion()
        elif deployment_name == "Llamaazure":
            interact = Llamacompletionazure()
        elif deployment_name == "AWS_CLAUDE_V3_5":
            interact=AWScompletions()
        elif deployment_name=="Llama3-70b":
            interact=Llama3completions()
        elif deployment_name == "Gemini-Pro" or deployment_name == "Gemini-Flash":
            interact=Geminicompletions(deployment_name)
        else:
            interact=Openaicompletions()
        output_text,index,finish_reason,hallucinationScore = interact.textCompletion(text,temperature,PromptTemplate,deployment_name,mod_flag)
        return output_text,index,finish_reason,hallucinationScore
    except Exception as e:
        log.error("Failed at Text Completion Function")
        log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at Text Completion Function"})
        log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
        
        
def moderationTime():
    try:
        with open("data/moderationtime.json", "r") as openfile:
            json_object = json.load(openfile)
        # print("json_object:",json_object)
        return json_object
    except Exception as e:
        print("Moderation time check Failed")

def feedback_submit(feedback):
    user_id = feedback.user_id
    message = feedback.message
    rating = feedback.rating
    
    res = Results.findOne(user_id)
    res["message"] = message
    res["rating"] = rating
    Results.delete(user_id)
    Results.createwithfeedback(res)
    # print("Result from db",type(Results.findOne(user_id)))
    # Process the feedback as needed

    return "Feedback submitted successfully"

def organization_policy(payload,headers): 
    try:
        labels = payload.labels
        text = payload.text
        #Using azure restricted topic model endpoint for organization policy
        if target_env=='azure':
            log.info("Using azure restricted topic model endpoint for organization policy")
            output = requests.post(url = topicurl,json={"text": text,"labels":labels},headers=headers,verify=sslv[verify_ssl])
            output=output.json()

        #Using aicloud restricted topic model endpoint for organization policy
        elif target_env=='aicloud':
            log.info("Using aicloud restricted topic model endpoint for organization policy")
            output = requests.post(url = topicraiurl,json={"inputs": [{"text":text,"labels":labels}]},headers=headers,verify=sslv[verify_ssl])
            output=output.json()[0]

        d={}
        for i in range(len(labels)):
            d[output["labels"][i]] = str(round(output["scores"][i],3))
        themecheck = CustomthemeRestricted()
        print("d",d)
        d["CustomTheme"]=str(themecheck.identify_jailbreak(text,headers,orgpolicy_embeddings))
        log.info(f"Dictionary for labels: {d}")
        return d
    except Exception as e:
        log.error("Error occured in Restrict_topic")
        # log.error(f"Exception: {e}")
        log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

def promptResponseSimilarity(text_1, text_2,headers):
    if target_env=='azure':
        text_1_embedding = requests.post(url = jailbreakurl,json={"text": [text_1]},headers=headers,verify=sslv[verify_ssl]).json()[0][0]
        text_2_embedding = requests.post(url = jailbreakurl,json={"text": [text_2]},headers=headers,verify=sslv[verify_ssl]).json()[0][0]
    elif target_env=='aicloud':
        text_1_embedding = requests.post(url = jailbreakraiurl,json={"inputs": [text_1]},headers=headers,verify=sslv[verify_ssl]).json()[0]
        text_2_embedding = requests.post(url = jailbreakraiurl,json={"inputs": [text_2]},headers=headers,verify=sslv[verify_ssl]).json()[0]
    
    dot_product = np.dot(text_1_embedding, text_2_embedding)
    norm_product = np.linalg.norm(text_1_embedding) * np.linalg.norm(text_2_embedding)
    similarity = round(dot_product / norm_product,4)
    return similarity
    

def show_score(prompt, response, sourcearr,headers):
    try:        
        log.info("Showing Scores")        
        

        response = response.strip('.')  
        response=",".join(response.split(",")[:-1])
        responseArr = re.split(r'(?<=[.!?])\s+(?=\D|$)', response)

        inpoutsim = promptResponseSimilarity(prompt, response, headers)
  
        maxScore = 0
        inpsourcesim = 0
        for i in responseArr:
            simScore = 0   
            flag = 0
            for j in sourcearr:
                score = promptResponseSimilarity(j, i, headers)
                maxScore = max(maxScore,score)
                
                if flag == 0:
                    flag = 1
                    maxScore = max(maxScore, promptResponseSimilarity(j, response, headers))
                    score2 = promptResponseSimilarity(j, prompt, headers)
                    inpsourcesim = max(score2,inpsourcesim)
                if score > simScore:
                    simScore = score        
        
        if maxScore<0.3:            
            finalScore = round(1-(inpoutsim*0.2 + inpsourcesim*0.4 + maxScore*0.4).tolist(),2)
        elif maxScore>0.45:           
            finalScore=0.2
        else:         
            finalScore = round(1-(inpoutsim*0.2 + maxScore*0.8).tolist(),2)
        score = {"score":finalScore}
        return score

    except Exception as e:
            log.info("Failed at Show_Score")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

def identifyIDP(text):
    if 'IDP' in text:
        return True
    return False

def identifyEmoji(text):
    '''Function to find emojis in the text
        Args: string
        Return: dictionary'''
    emoji_values=demoji.findall(text)
    emoji_dict={}
    if len(emoji_values)>0:
        emoji_dict['flag']=True
    else:
        emoji_dict['flag']=False
    emoji_dict['value']=list(emoji_values.keys())
    emoji_dict['mean']=list(emoji_values.values())
    return emoji_dict

def emojiToText(text,emoji_dict):
    '''Function to convert emojis in a sentence to text
       Returns the modified text(text), text with emojis removed(privacy_text) and dictionary containing all emojis and their meanings present in input text(current_emoji_dict)'''
    emoji_list = sorted(emoji_data.keys(), key=len, reverse=True)
    current_emoji_dict=MultiValueDict()
    privacy_text=text
    #replacing emojis with their meaning from inappropriate_emoji.json
    for emoji in emoji_list:
        if emoji in text:
            pattern = regex.escape(emoji)
            occurrences = regex.findall(pattern, text, flags=regex.V1)
            text = text.replace(emoji, ' ' + emoji_data[emoji])
            privacy_text=privacy_text.replace(emoji,' ')
            for i in range(0,len(occurrences)):
                current_emoji_dict[emoji]=emoji_data[emoji]
            
    #replacing rest of the emojis with their meaning from emoji_dict
    for i in range(0,len(emoji_dict['value'])): 
            if emoji_dict['value'][i] in text:
                pattern = regex.escape(emoji_dict['value'][i])
                occurrences = regex.findall(pattern, text, flags=regex.V1)
                text=text.replace(emoji_dict['value'][i],(' '+emoji_dict['mean'][i]).replace('_',' '))
                privacy_text=privacy_text.replace(emoji_dict['value'][i],' ')
                for j in occurrences:
                    current_emoji_dict[j] = emoji_dict['mean'][emoji_dict['value'].index(j)]
    return text,privacy_text,current_emoji_dict

def wordToEmoji(text,current_emoji_dict,result):
    '''Function to check and convert profane word back to emoji(using it for profanity result)'''
    text1=text
    temp_dict=current_emoji_dict
    if len(result)>0:
        for i in range(0,len(result)):
            if result[i] not in text1:
                for j in list(temp_dict):
                    c=0
                    for k in temp_dict[j]:
                        if result[i] in k:
                            text1=text1.replace(result[i],'',1)
                            result[i]=j
                            temp_dict[j].pop(0)
                            c=1
                            break
                    if c==1:
                        break
            else:
                text1=text1.replace(result[i],'',1)
    return result

def profaneWordIndex(text,profane_list):
    '''Function to find location of profane words and emojis if emoji option is present in text'''
    index_list=[]
    for i in profane_list:
        if i in text:
            index_list.append([(text.find(i)),(text.find(i)+grapheme.length(str(i)))])
            alphabet_sequence = (string.ascii_lowercase * (grapheme.length(i) // 26 + 1))[:grapheme.length(i)]
            text=text.replace(i,alphabet_sequence,1)
    return index_list

#Custom dictionary class
class MultiValueDict(dict):
    def __setitem__(self, key, value):
        if key not in self:
            super().__setitem__(key, [])
        self[key].append(value)
    
    def __getitem__(self, key):
        if key not in self:
            raise KeyError(key)
        return self.get_all(key)
    
    def get_all(self, key):
        return super().__getitem__(key)       
