import os
'''
Copyright 2024 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from werkzeug.exceptions import InternalServerError
from fastapi.encoders import jsonable_encoder
import traceback
from mapper.mapper import *
import time
import contextvars
from config.logger import CustomLogger,request_id_var
from privacy.privacy import Privacy as ps

log = CustomLogger()

import sys
import os

try:
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    else:
        application_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
        
    log=CustomLogger()
    log.info("before loading model")
    request_id_var = contextvars.ContextVar("request_id_var")
    
    request_id_var.set("Startup")
    log_dict={}
    log.info("privacy model loaded")

except Exception as e:
    log.error(f"Exception: {e}")
    log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

def privacy(id,text):  
    log.info("inside privacy")
    
    try:
        st = time.time()
        res=ps.textAnalyze({"inputText":text,
                    "account": None,
                    "portfolio":None,
                    "exclusionList": None,
                    "fakeData": "false",
                    "piiEntitiesToBeRedacted":None,
                    "nlp":None})
        et = time.time()
        rt = et-st
        #print("result start",res.PIIEntities,"result end", "time",rt)
        
        # output['PIIresult'] = {"PIIresult":res.PIIEntities,"modelcalltime":round(rt,3)}
        return {"PIIresult":res.PIIEntities,"modelcalltime":round(rt,3)}
    except Exception as e:
             
            log.error("Error occured in privacy")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            log_dict[request_id_var.get()].append({"Line number":str(traceback.extract_tb(e.__traceback__)[0].lineno),"Error":str(e),
                                                   "Error Module":"Failed at privacy call"})
            raise InternalServerError()

