import os
'''
Copyright 2024 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
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
    log.info("before loading topic model")
    request_id_var = contextvars.ContextVar("request_id_var")
    #pipe = StableDiffusionPipeline.from_pretrained('/model/stablediffusion/fp32/model')
    device = "cuda"
#  
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    print("device",device)
    gpu=0 if torch.cuda.is_available() else -1
   
    topictokenizer_dberta = AutoTokenizer.from_pretrained(os.path.join(application_path,"models/restricted-dberta-base-zeroshot-v2"))
    topicmodel_dberta = AutoModelForSequenceClassification.from_pretrained(os.path.join(application_path,"models/restricted-dberta-base-zeroshot-v2")).to(device)
    nlp = pipeline('zero-shot-classification', model=topicmodel_dberta, tokenizer=topictokenizer_dberta,device=gpu)
    nlimini = pipeline('zero-shot-classification', model="../models/nli-MiniLM2-L6-H768",device=gpu)
 
    request_id_var.set("Startup")
    log_dict={}
    log.info("topic model loaded")

except Exception as e:
    log.error(f"Exception: {e}")
    log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

            
def restricttopic_check(payload,id): 
    log.info("inside restricttopic_check")
    
    try:
        st = time.time()
        # topicmodel = topicmodel_Facebook
        # topictokenizer = topictokenizer_Facebook

        # nlp = pipeline('zero-shot-classification', model=classifier, tokenizer=topictokenizer)

        text=payload['text']
        if('model' in payload):
            model=payload['model']
        else:
            model="nliMini"
        labels=payload['labels']
        #hypothesis_template = "The topic of this text is {}"
        hypothesis_template="This text falls under and is strictly related to topic {}"
        
    
        if(model=="nliMini"):
            cls=nlimini
        else:
            cls=nlp
      
        with torch.no_grad():    
            output=cls(text, labels,hypothesis_template=hypothesis_template,multi_label=True)
        # print("=================",output)
        for i in range(len(output["scores"])):
            output["scores"][i] = round(output["scores"][i],4)

        # del nlp
        del cls
        et = time.time()
        rt = et-st
        output['time_taken'] = str(round(rt,3))+"s"
        # output1['restricttopic'] = output
        return output
    
    except Exception as e:
             
            log.error("Error occured in restricttopic_check")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at restricttopic_check call"})
            raise InternalServerError()

