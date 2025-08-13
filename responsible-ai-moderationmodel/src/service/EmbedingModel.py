import os
'''
Copyright 2024 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import torch
from sentence_transformers import SentenceTransformer,util
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
    log.info("before loading embeding model")
    request_id_var = contextvars.ContextVar("request_id_var")
    #pipe = StableDiffusionPipeline.from_pretrained('/model/stablediffusion/fp32/model')
    device = "cuda"
#    registry = RecognizerRegistry()
#    registry.load_predefined_recognizers()
#    analyzer_engine = AnalyzerEngine(registry=registry)

    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    print("device",device)
    gpu=0 if torch.cuda.is_available() else -1
    encoder = SentenceTransformer(os.path.join(application_path, "models/multi-qa-mpnet-base-dot-v1")).to(device)

    jailbreakModel = encoder
    similarity_model =encoder
    request_id_var.set("Startup")
    log_dict={}
    log.info("embeding model loaded")

except Exception as e:
    log.error(f"Exception: {e}")
    log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")


def multi_q_net_similarity(id,text1=None,text2=None,emb1=None,emb2=None):
    
    try:
        st = time.time()
        if text1:
            with torch.no_grad():
                emb1 = jailbreakModel.encode(text1, convert_to_tensor=True,device=device)
        if text2:
            with torch.no_grad():
                emb2 = jailbreakModel.encode(text2, convert_to_tensor=True,device=device)
        
        emb = util.pytorch_cos_sim(emb1, emb2).to("cpu").numpy().tolist()
        del emb1
        del emb2
        et = time.time()
        rt =et-st
        return emb,{'time_taken': str(round(rt,3))+"s"}
    except Exception as e:
             
            log.error("Error occured in multi_q_net_similarity")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at multi_q_net_similarity call"})
            raise InternalServerError()
            
def multi_q_net_embedding(id,lst):
    log.info("inside multi_q_net_embedding")
    
    try:
        st = time.time()
        # print("start time JB===========",lst,st)
        
        res = []
        for text in lst:
            with torch.no_grad():
                text_embedding = jailbreakModel.encode(text, convert_to_tensor=True,device=device)
            res.append(text_embedding.to("cpu").numpy().tolist())

        del text_embedding
        et = time.time()
        rt = et-st
        # output['multi_q_net_embedding'] =(res,{'time_taken': str(round(rt,3))+"s"})
        return res,{'time_taken': str(round(rt,3))+"s"}
        # return output
        # return text_embedding.numpy().tolist()
    except Exception as e:
             
            log.error("Error occured in multi_q_net text embedding")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at multi_q_net text embedding call"})
            raise InternalServerError()
            
