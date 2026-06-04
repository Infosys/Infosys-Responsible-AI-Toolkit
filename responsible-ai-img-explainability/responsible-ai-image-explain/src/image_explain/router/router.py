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

from typing import Optional
from fastapi import File, Form, APIRouter, HTTPException, UploadFile
from image_explain.config.logger import request_id_var, CustomLogger
from image_explain.service.service import ImageService as Service
from image_explain.mappers.mappers import AnalyzeResponse, ObjectDetectionResponse
from datetime import datetime

router = APIRouter()

log=CustomLogger()

@router.post('/image-explainability/analyze',
             response_model=AnalyzeResponse,
             summary="Prompt Based Analysis")
def analyze_image(image: UploadFile, evaluator: str = Form('GPT_4o'), prompt: str = Form(None), query_flag: bool = Form(False)):
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("Before invoking create usecase service")
        payload = {"prompt":prompt,
                   "image":image,
                   "evaluator":evaluator,
                   "query_flag": query_flag}
        log.debug("Request payload: "+ str(payload))
        response = Service.analyze_image(payload)
        log.info("After invoking create usecase service")
        log.debug("Response : "+ str(response))
        log.info("Exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")
        return response
    except Exception as cie:
        log.error(cie.__dict__)
        log.info("Exit create usecase routing method")
        raise HTTPException(status_code=500, detail=f"ERROR: {str(cie)}")
    
@router.post('/image-explainability/object-detection',
             response_model=ObjectDetectionResponse,
             summary="Analyze Object Detection output in an image")
def object_detection_img(image: UploadFile, evaluator: str = Form('GPT_4o')):
    request_id_var.set(id)
    log.info("Entered create usecase routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("Before invoking create usecase service")
        payload = {"image":image, "evaluator":evaluator}
        log.debug("Request payload: "+ str(payload))
        response = Service.object_detection_img(payload)
        log.info("After invoking create usecase service")
        log.debug("Response : "+ str(response))
        log.info("Exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")
        return response
    except Exception as cie:
        log.error(cie.__dict__)
        log.info("Exit create usecase routing method")
        raise HTTPException(status_code=500, detail=str(cie))