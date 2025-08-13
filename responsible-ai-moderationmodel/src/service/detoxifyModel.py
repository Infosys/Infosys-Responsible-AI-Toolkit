import os
'''
Copyright 2024 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import math
import torch
from detoxify import Detoxify
#from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from transformers import AutoTokenizer
from werkzeug.exceptions import InternalServerError
from fastapi.encoders import jsonable_encoder
import traceback
from mapper.mapper import *
import time
import contextvars
from config.logger import CustomLogger,request_id_var


log = CustomLogger()

import sys
import os

try:
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    else:
        application_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
        
    log=CustomLogger()
    log.info("before loading detoxify model")
    request_id_var = contextvars.ContextVar("request_id_var")
    device = "cuda"
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    print("device",device)
    gpu=0 if torch.cuda.is_available() else -1
    check_point = 'toxic_debiased-c7548aa0.ckpt'
    toxicityModel = Detoxify(checkpoint=os.path.join(application_path, 'models/detoxify/'+ check_point),
                        device=device,
                        huggingface_config_path=os.path.join(application_path, 'models/detoxify'))
    tokenizer = AutoTokenizer.from_pretrained(os.path.join(application_path, "models/detoxify"))

    request_id_var.set("Startup")
    log_dict={}
    log.info("detoxify model loaded")

except Exception as e:
    log.error(f"Exception: {e}")
    log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")


def toxicity_check(payload,id) :
    log.info("inside toxicity_check")
    
    try:
        st = time.time()
        text = payload['text']

        #to check number of tokens 
        input_ids_val = tokenizer.encode(text)
        input_ids=input_ids_val[1:-1]
        result_list=[]
        #to send max 450 tokens to the model at a time and at end find avg result for each token set
        token_limit=450
        if len(input_ids)>token_limit:
            val=math.ceil(len(input_ids)/token_limit)
            j=0
            k=token_limit
            for i in range(0,val):
                text="".join(tokenizer.decode(input_ids[j:k]))
                j+=token_limit
                k+=token_limit
                with torch.no_grad():
                    result = toxicityModel.predict(text)
                    result_list.append(result)
            output = {
                'toxicity': 0,
                'severe_toxicity': 0,
                'obscene': 0,
                'threat': 0,
                'insult': 0,
                'identity_attack': 0,
                'sexual_explicit': 0
                }
            for j in result_list:
                 output['toxicity']+=j['toxicity']
                 output['severe_toxicity']+=j['severe_toxicity']
                 output['obscene']+=j['obscene']
                 output['identity_attack']+=j['identity_attack']
                 output['insult']+=j['insult']
                 output['threat']+=j['threat']
                 output['sexual_explicit']+=j['sexual_explicit']
            output = {k: v / len(result_list) for k, v in output.items()}
        else:
            with torch.no_grad():
                output = toxicityModel.predict(text)
        List_profanity_score = []
        obj_profanityScore_toxic = profanityScore(metricName='toxicity',
                                        metricScore=output['toxicity'])
        obj_profanityScore_severe_toxic = profanityScore(metricName='severe_toxicity',
                                        metricScore=output['severe_toxicity'])
        obj_profanityScore_obscene = profanityScore(metricName='obscene',
                                        metricScore=output['obscene'])
        obj_profanityScore_threat = profanityScore(metricName='threat',
                                        metricScore=output['threat'])
        obj_profanityScore_insult = profanityScore(metricName='insult',
                                        metricScore=output['insult'])
        obj_profanityScore_identity_attack = profanityScore(metricName='identity_attack',
                                        metricScore=output['identity_attack'])
        obj_profanityScore_sexual_explicit = profanityScore(metricName='sexual_explicit',
                                        metricScore=output['sexual_explicit'])
        
        List_profanity_score.append(obj_profanityScore_toxic)
        List_profanity_score.append(obj_profanityScore_severe_toxic)
        List_profanity_score.append(obj_profanityScore_obscene)
        List_profanity_score.append(obj_profanityScore_threat)
        List_profanity_score.append(obj_profanityScore_insult)
        List_profanity_score.append(obj_profanityScore_identity_attack)
        List_profanity_score.append(obj_profanityScore_sexual_explicit)

        objProfanityAnalyzeResponse = {}
        objProfanityAnalyzeResponse['toxicScore'] = List_profanity_score
        et = time.time()
        rt = et-st
        objProfanityAnalyzeResponse['time_taken'] = str(round(rt,3))+"s"
        # output1['toxicity'] = objProfanityAnalyzeResponse
        return objProfanityAnalyzeResponse
    
    except Exception as e:
             
            log.error("Error occured in toxicity_check")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at toxicity_check call"})
            raise InternalServerError()
              
