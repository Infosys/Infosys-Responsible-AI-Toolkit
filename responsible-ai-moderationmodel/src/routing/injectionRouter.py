'''
Copyright 2024 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from flask import Blueprint
import time
# import logging
from flask import request
# from dao.AdminDb import Results
from werkzeug.exceptions import HTTPException,UnprocessableEntity
from tqdm.auto import tqdm
# from fastapi.encoders import jsonable_encoder

from service.injectionModel import *
from config.logger import CustomLogger ,request_id_var

import uuid
from mapper.mapper import *
import psutil

request_id_var.set('Startup')
injection_router = Blueprint('router3', __name__,)
log=CustomLogger()
    
@injection_router.route("/promptinjectionmodel",methods=[ 'POST'])
def prompt_model():
    st=time.time()
    id=uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered prompt_model routing method")
    try:
        
        # id=uuid.uuid4().hex
        payload=request.get_json()
        # request_id_var.set(id)
        log.info("before invoking prompt_model service")
        log_dict[request_id_var.get()]=[]
        if payload['text'] is None or (payload['text'] is not None and len(payload['text'])==0):
            raise UnprocessableEntity("1021-Input Text should not be empty ")
        response = promptInjection_check(payload['text'],id)
        log.info("after invoking prompt_model service ")
        er=log_dict[request_id_var.get()]
        logobj = {"_id":id,"error":er}
        if len(er)!=0:
            log.debug(str(logobj))
        del log_dict[id]
        log.debug("response : " + str(response))
        # log.debug("response : " + str(response))
        log.info("exit prompt_model routing method")
        log.info(f"Time taken by promptinjection {time.time()-st}")
        return jsonable_encoder(response)
    except UnprocessableEntity as cie:
        log.error(str(cie.__dict__))
        log.info("exit prompt_model routing method")
        raise UnprocessableEntity(**cie.__dict__)
    except Exception as cie:
        log.error(str(cie.__dict__))
        log.info("exit prompt_model routing method")
        raise HTTPException()
