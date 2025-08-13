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
from service.EmbedingModel import *
from service.topicModel import *
from service.privacyModel import *
from service.detoxifyModel import *
from service.sentiment_service import *
from service.invisibletext_service import *
from service.gibberish_service import *
from service.bancode_service import *
from config.logger import CustomLogger ,request_id_var

import uuid
from mapper.mapper import *
import psutil

request_id_var.set('Startup')
router = Blueprint('router', __name__,)
log=CustomLogger()

@router.route("/detoxifymodel",methods=[ 'POST'])
def toxic_model():
    st=time.time()
    stmem = psutil.Process().memory_info().rss
    id=uuid.uuid4().hex
    request_id_var.set(id)
    try:
        
        # id=uuid.uuid4().hex
        payload=request.get_json()
        # request_id_var.set(id)
        log.info("before invoking toxic_model service ")
        log_dict[request_id_var.get()]=[]
        if payload['text'] is None or (payload['text'] is not None and len(payload['text'])==0):
            raise UnprocessableEntity("1021-Input Text should not be empty ")
        response = toxicity_check(payload,id)
 
        log.info("after invoking toxic_model service ")
        
        er=log_dict[request_id_var.get()]
        logobj = {"_id":id,"error":er}
	

        if len(er)!=0:
            log.debug(str(logobj))
            # print("this is --> ",str(logobj) )
        del log_dict[id]
        log.debug("response : " + str(response))
        log.info("exit toxic_model routing method")
        log.info(f"Time taken by toxicity {time.time()-st}")
        return jsonable_encoder(response)
    except UnprocessableEntity as cie:
        log.error(str(cie.__dict__))
        log.info("exit toxic_model routing method")
        raise UnprocessableEntity(**cie.__dict__)
    except Exception as cie:
        log.error(str(cie.__dict__))
        log.info("exit toxic_model routing method")
        raise HTTPException()
    
@router.route("/privacy",methods=[ 'POST'])
def pii_check():
    st=time.time()
    id=uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered pii_check routing method")
    try:
        
        # id=uuid.uuid4().hex
        payload=request.get_json()
        # request_id_var.set(id)
        log.info("before invoking create usecase service ")
        log_dict[request_id_var.get()]=[]
        if payload['text'] is None or (payload['text'] is not None and len(payload['text'])==0):
            raise UnprocessableEntity("1021-invalid input!")
        response = privacy(id,payload['text'])
        log.info("after invoking create usecase service ")
        er=log_dict[request_id_var.get()]
        logobj = {"_id":id,"error":er}
        if len(er)!=0:
            log.debug(str(logobj))
        del log_dict[id]
        log.debug("response : " + str(response))
        # log.debug("response : " + str(response))
        log.info("exit pii_check routing method")
        log.info(f"Time taken by privacy {time.time()-st}")
        return jsonable_encoder(response)
    except UnprocessableEntity as cie:
        log.error(str(cie.__dict__))
        log.info("exit pii_check routing method")
        raise UnprocessableEntity(**cie.__dict__)
    except Exception as cie:
        log.error(str(cie.__dict__))
        log.info("exit pii_check routing method")
        raise HTTPException()
    
@router.route("/promptinjectionmodel",methods=[ 'POST'])
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
    
@router.route("/restrictedtopicmodel",methods=[ 'POST'])
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
    
@router.route("/multi_q_net_embedding",methods=[ 'POST'])
def embedding_model():
    st=time.time()
    id=uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered embedding_model routing method")
 
    try:
        
        # id=uuid.uuid4().hex
        payload=request.get_json()
        # request_id_var.set(id)

        log.info("before invoking embedding_model service ")
        log_dict[request_id_var.get()]=[]
        if payload['text'] is None or (payload['text'] is not None and len(payload['text'])==0):
            raise UnprocessableEntity("1021-Input Text should not be empty ")
        response = multi_q_net_embedding(id,payload['text'])
        log.info("after invoking embedding_model service ")
        er=log_dict[request_id_var.get()]
        logobj = {"_id":id,"error":er}
        if len(er)!=0:
            log.debug(str(logobj))
        del log_dict[id]
        # log.debug("response : " + str(response))
        # log.debug("response : " + str(response))
        log.info("exit embedding_model routing method")
        log.info(f"Time taken by Jailbreak {time.time()-st}")
        return jsonable_encoder(response)
    except UnprocessableEntity as cie:
        log.error(str(cie.__dict__))
        log.info("exit embedding_model routing method")
        raise UnprocessableEntity(**cie.__dict__)
    except Exception as cie:
        log.error(str(cie.__dict__))
        log.info("exit embedding_model routing method")
        raise HTTPException()

@router.route("/multi-qa-mpnet-model_similarity",methods=[ 'POST'])
def similarity_model():
    st=time.time()
    id=uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered similarity_model routing method")
    try:
        log.info("before invoking similarity_model service ")
        payload=request.get_json()
        log_dict[request_id_var.get()]=[]
        emb1_cond=None
        emb2_cond=None

        text1_cond = payload['text1'] is None or (payload['text1'] is not None and len(payload['text1'])==0)
        text2_cond = payload['text2'] is None or (payload['text2'] is not None and len(payload['text2'])==0)
        if('emb1' in payload):
                emb1_cond = payload['emb1'] is None or (payload['emb1'] is not None and len(payload['emb1'])==0)
        else:
            payload['emb1']=None
        if('emb2' in payload):
            emb2_cond = payload['emb2'] is None or (payload['emb2'] is not None and len(payload['emb2'])==0)
        else:
            payload['emb2']=None
            
        if text1_cond or text2_cond or emb1_cond or emb2_cond:
            raise UnprocessableEntity("1021-Input Text should not be empty ")
        response = multi_q_net_similarity(id,payload['text1'],payload['text2'],payload['emb1'],payload['emb2'])
        log.info("after invoking similarity_model service ")
        er=log_dict[request_id_var.get()]
        logobj = {"_id":id,"error":er}
        if len(er)!=0:
            log.debug(str(logobj))
        del log_dict[id]
        log.debug("response : " + str(response))
        # log.debug("response : " + str(response))
        log.info("exit similarity_model routing method")
        log.info(f"Time taken by similary{time.time()-st}")
        return jsonable_encoder(response)
    except UnprocessableEntity as cie:
        log.error(str(cie.__dict__))
        log.info("exit similarity_model routing method")
        raise UnprocessableEntity(**cie.__dict__)
    
@router.route("/sentimentmodel",methods=[ 'POST'])
def sentimentmodel():
    st=time.time()
    log.info("Entered sentiment routing method")
    try:
        payload=request.get_json()
        log.info("before invoking sentiment_model service ")
        s = Sentiment()
        response = s.scan(payload['text'])
        log.info("after invoking sentiment_model service ")
        log.debug("response : " + str(response))
        log.info("exit sentiment_model routing method")
        log.info(f"Time taken by Sentiment Check{time.time()-st}")
        return jsonable_encoder(response)
    except Exception as cie:
        log.error(cie)
        log.error(cie.__dict__)
        log.info("exit sentiment_model routing method")
        raise HTTPException()
    
@router.route("/invisibletextmodel",methods=[ 'POST'])
def invisibletextmodel():
    st=time.time()
    log.info("Entered invisible_text routing method")
    try:
        payload=request.get_json()
        log.info("before invoking invisible_text service ")
        s = InvisibleText()
        response = s.scan(payload['text'],payload['banned_categories'])
        log.info("after invoking invisible_text service ")
        log.debug("response : " + str(response))
        log.info("exit secret_model routing method")
        log.info(f"Time taken by Invisible Text Check{time.time()-st}")
        return jsonable_encoder(response)
    except Exception as cie:
        log.error(cie)
        log.error(cie.__dict__)
        log.info("exit secret_model routing method")
        raise HTTPException()
    
@router.route("/gibberishmodel",methods=[ 'POST'])
def gibberishmodel():
    st=time.time()
    log.info("Entered gibberish routing method")
    try:
        payload=request.get_json()
        log.info("before invoking gibberish_model service ")
        gib = Gibberish()
        response = gib.scan(payload)
        log.info("after invoking gibberish_model service ")
        log.debug("response : " + str(response))
        log.info("exit gibberish_model routing method")
        log.info(f"Time taken by Gibberish Check{time.time()-st}")
        return jsonable_encoder(response)
    except Exception as cie:
        log.error(str(cie.__dict__))
        log.info("exit gibberish_model routing method")
        raise HTTPException()
    
@router.route("/bancodemodel",methods=[ 'POST'])
def bancodemodel():
    st=time.time()
    log.info("Entered ban topic routing method")
    try:
        payload=request.get_json()
        log.info("before invoking bantopicmodel service ")
        ban = BanCode()
        response = ban.scan(payload)
        log.info("after invoking bantopicmodel service ")
        log.debug("response : " + str(response))
        log.info("exit bantopicmodel routing method")
        log.info(f"Time taken by Ban topic Check{time.time()-st}")
        return jsonable_encoder(response)
    except Exception as cie:
        log.error(str(cie.__dict__))
        log.info("exit bantopic_model routing method")
        raise HTTPException()