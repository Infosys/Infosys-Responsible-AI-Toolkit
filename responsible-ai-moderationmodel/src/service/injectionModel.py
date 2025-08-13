import os
'''
Copyright 2024 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


#from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
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
    log.info("before loading injection model")
    request_id_var = contextvars.ContextVar("request_id_var")
    #pipe = StableDiffusionPipeline.from_pretrained('/model/stablediffusion/fp32/model')
    device = "cuda"
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    print("device",device)
    gpu=0 if torch.cuda.is_available() else -1
    PromptModel_dberta = AutoModelForSequenceClassification.from_pretrained(os.path.join(application_path, "models/dbertaInjection")).to(device)
    Prompttokens_dberta = AutoTokenizer.from_pretrained(os.path.join(application_path, "models/dbertaInjection"))
    promtModel = pipeline("text-classification", model=PromptModel_dberta, tokenizer=Prompttokens_dberta, device=device)

    request_id_var.set("Startup")
    log_dict={}
    log.info("injection model loaded")

except Exception as e:
    log.error(f"Exception: {e}")
    log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
         
def promptInjection_check(text,id):
    
    log.info("inside promptInjection_check")
    try:
        st = time.time()
        result = promtModel(text)
        # print("============:",result)
        predicted_label_name = result[0]["label"]
        predicted_probabilities = result[0]["score"]
        # del tokens
        et = time.time()
        rt = et-st
        # output['promptInjection'] = (predicted_label_name,predicted_probabilities, {'time_taken':str(round(rt,3))+"s"})
        
        return predicted_label_name,predicted_probabilities, {'time_taken':str(round(rt,3))+"s"}
    except Exception as e:
            
            log.error("Error occured in promptInjection_check")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at promptInjection_check call"})
            raise InternalServerError()
 