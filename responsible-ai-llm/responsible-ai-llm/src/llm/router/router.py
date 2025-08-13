'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from fastapi import APIRouter, HTTPException
from llm.config.logger import CustomLogger, request_id_var
from llm.service.service import LLMService as service
from llm.mapper.mapper import *
from llm.service.openAiCompletion import Openaicompletions
from datetime import  datetime
import uuid
from dotenv import load_dotenv
load_dotenv()

log=CustomLogger()

router=APIRouter()

@router.post("/llm/openai", summary = "Open AI Models")
def generate_text(payload: OpenAiRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("Before invoking create usecase service ")
        interact=Openaicompletions()
        response = interact.textCompletion(payload)
        log.info("after invoking create usecase service ")
        log.debug("Response : "+ str(response))
        log.info("Exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")
        return response
    except Exception as cie:
        log.error(f"UUID: {request_id_var.get()}, Error: {cie}")
        log.info("exit create usecase routing method")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(cie)}")

@router.post("/llm/image",
             response_model=ImageGenerationResponse, 
             summary = "Generate an image using LLM")
def generate_image(payload: ImageGenerationRequest):
    id = uuid.uuid4().hex
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("Before invoking create usecase service ")
        response = service.generate_image(payload)
        log.info("after invoking create usecase service ")
        log.debug("Response : "+ str(response))
        log.info("Exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")
        return response
    except Exception as cie:
        log.error(f"UUID: {request_id_var.get()}, Error: {cie}")
        log.info("exit create usecase routing method")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(cie)}")