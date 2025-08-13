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

from service.topicModel import *
from config.logger import CustomLogger ,request_id_var

import uuid
from mapper.mapper import *
import psutil

request_id_var.set('Startup')
topic_router = Blueprint('router5', __name__,)
log=CustomLogger()
    
@topic_router.route("/restrictedtopicmodel",methods=[ 'POST'])
def restrictedTopic_model():
    st=time.time()
    id=uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered restrictedTopic_model routing method")
    try:
        # id=uuid.uuid4().hex
        payload=request.get_json()
        # request_id_var.set(id)
        log.info("before invoking restrictedTopic_model service ")
        log_dict[request_id_var.get()]=[]

        label_cond = payload['labels'] is None or (payload['labels'] is not None and len(payload['labels'])==0)
        #model_cond=False
        # print("--")
        # if("model" in payload):
        #     model_cond = payload['model'] is None or (payload['model'] is not None and len(payload['model'])==0)
        # print("==")
        if payload['text'] is None or (payload['text'] is not None and len(payload['text'])==0) or label_cond:
            raise UnprocessableEntity("1021-invalid input ")
        response = restricttopic_check(payload,id)
        log.info("after invoking restrictedTopic_model service ")
        er=log_dict[request_id_var.get()]
        logobj = {"_id":id,"error":er}
        if len(er)!=0:
            log.debug(str(logobj))
        del log_dict[id]
        log.debug("response : " + str(response))
        # log.debug("response : " + str(response))
        log.info("exit restrictedTopic_model routing method")
        log.info(f"Time taken by RestrictedTopic{time.time()-st}")
        # print(type(response))
        # print(type(jsonable_encoder(response)))
        return jsonable_encoder(response)
    except UnprocessableEntity as cie:
        log.error(str(cie.__dict__))
        log.info("exit restrictedTopic_model routing method")
        raise UnprocessableEntity(**cie.__dict__)
    except Exception as cie:
        log.error(str(cie))       
        log.error(str(cie.__dict__))
        log.info("exit restrictedTopic_model routing method")
        raise HTTPException()
    
