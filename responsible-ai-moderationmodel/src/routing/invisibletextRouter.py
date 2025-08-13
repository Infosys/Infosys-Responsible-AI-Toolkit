'''
Copyright 2024 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from flask import Blueprint
import time
from flask import request
from werkzeug.exceptions import HTTPException,UnprocessableEntity
from tqdm.auto import tqdm
from service.invisibletext_service import *
from config.logger import CustomLogger ,request_id_var
import uuid
from mapper.mapper import *
import psutil

request_id_var.set('Startup')
invisibletext_router = Blueprint('router8', __name__,)
log=CustomLogger()


@invisibletext_router.route("/invisibletextmodel",methods=[ 'POST'])
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
        return response
    except UnprocessableEntity as cie:
        log.error(str(cie.__dict__))
        log.info("exit invisibletext_model routing method")
        raise UnprocessableEntity(**cie.__dict__)
    except Exception as cie:
        log.error(str(cie))       
        log.error(str(cie.__dict__))
        log.info("exit invisibletext_model routing method")
        raise HTTPException()
