'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import traceback
from flask import Blueprint
import time
from flask import request
from werkzeug.exceptions import HTTPException, UnprocessableEntity
from tqdm.auto import tqdm
from fastapi.encoders import jsonable_encoder
from service.topicModel import restricttopic_check
from config.logger import CustomLogger, request_id_var
import uuid
from mapper.mapper import *
import psutil

request_id_var.set('Startup')
topic_router = Blueprint('router5', __name__,)
log = CustomLogger()

@topic_router.route("/restrictedtopicmodel", methods=['POST'])
def restrictedTopic_model():
    st = time.time()
    req_id = uuid.uuid4().hex
    request_id_var.set(req_id)
    log.info("Entered restrictedTopic_model routing method")

    try:
        payload = request.get_json()

        if payload is None:
            raise UnprocessableEntity("1021-invalid input: Request body is empty or not valid JSON.")
        
        text = payload.get('text')
        model_name = payload.get('model', "deberta")
        labels = payload.get('labels')

        if text is None or (isinstance(text, str) and len(text.strip()) == 0):
            raise UnprocessableEntity("1021-invalid input: 'text' field is missing or empty.")

        if model_name in ["deberta"]:
            if labels is None or not isinstance(labels, list) or len(labels) == 0:
                raise UnprocessableEntity(f"1021-invalid input: 'labels' field is mandatory and cannot be empty for model '{model_name}'.")
        elif model_name == "fine-tuned distilbert":
            if labels is not None and not isinstance(labels, list):
                raise UnprocessableEntity("1021-invalid input: 'labels' field, if provided for 'fine-tuned distilbert' model, must be a list.")
        else:
            raise UnprocessableEntity(f"1021-invalid input: Unknown model specified '{model_name}'.")

        if not hasattr(restricttopic_check, 'log_dict'):
            restricttopic_check.log_dict = {}
        restricttopic_check.log_dict[request_id_var.get()] = []

        log.info("before invoking restricttopic_check service ")
        response = restricttopic_check(payload, req_id)
        log.info("after invoking restricttopic_check service ")
        
        er = restricttopic_check.log_dict.get(req_id, [])
        logobj = {"_id": req_id, "error": er}
        if len(er) != 0:
            log.debug(f"Errors for request {req_id}: {logobj}")
        
        if req_id in restricttopic_check.log_dict:
            del restricttopic_check.log_dict[req_id]

        log.debug("response : " + str(response))
        log.info("exit restrictedTopic_model routing method")
        log.info(f"Time taken by RestrictedTopic: {time.time() - st:.3f}s")
        
        return jsonable_encoder(response)

    except UnprocessableEntity as cie:
        log.error(f"UnprocessableEntity Error: {cie.description}")
        log.info("exit restrictedTopic_model routing method with UnprocessableEntity")
        raise

    except HTTPException as he:
        log.error(f"HTTPException: {he.description}")
        log.info("exit restrictedTopic_model routing method with HTTPException")
        raise

    except Exception as e:
        log.error(f"Unhandled Exception in router: {str(e)}")
        log.error(f"Traceback: {traceback.format_exc()}")
        log.info("exit restrictedTopic_model routing method with unhandled Exception")
        raise HTTPException(description="An unexpected error occurred.", code=500)