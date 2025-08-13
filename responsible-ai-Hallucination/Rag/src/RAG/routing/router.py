"""
SPDX-License-Identifier: MIT

Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from fastapi import Depends,Request,APIRouter, HTTPException,Form,UploadFile,File,Body
from fastapi.responses import StreamingResponse
from RAG.mapper.mapper import *
from RAG.service.service import createvector,defaultQARetrievalKepler,show_score,cache,createvector
from RAG.service.caching import caching,removeCache
# from RAG.service.FileUploadtodb import FileUploadtodb
from RAG.service.caching import caching
from RAG.service.cov import cov
from RAG.service.cot import cot
from RAG.service.thot import thot
from RAG.service.lot import lot
from RAG.service.multimodal import Multimodal
from RAG.service.videorag import video_rag
from RAG.service.audiorag import audio_rag
from RAG.exception.exception import completionException
from RAG.config.logger import CustomLogger,request_id_var
from RAG.service.geval import gEval
import uuid
import os
from typing import Annotated, List, Optional
#from RAG.service.authenticate import create_access_token,authenticate_user
router = APIRouter()
log=CustomLogger()

# @router.post("/FileUpload")#, response_model=Choice)
# def generate_text(payload: List[UploadFile]):
#     log.info("Entered create usecase routing method")
#     try:
#         log.info("before invoking create usecase service ")
#         id = uuid.uuid4().hex
#         request_id_var.set(id)
#         output_text = createvector(payload)
#         log.info("after invoking create usecase service ")
#         log.info("exit create usecase routing method")
#         return output_text
#     except completionException as cie:
#         log.error(cie.__dict__)
#         log.info("exit create usecase routing method")
#         raise HTTPException(**cie.__dict__)
    
@router.post("/FileUpload")
def generate_text(files: List[UploadFile] = File(...), select_model: str = Form("openai")):
    log.info("Entered create usecase routing method")
    try:
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        output_text = createvector(files, select_model)
        log.info("after invoking create usecase service ")
        log.info("exit create usecase routing method")
        return output_text
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    
@router.post("/RetrievalKepler")#, response_model=Choice)
# def generate_text(fileupload: bool = Form(...),cov: bool = Form(...),cot: bool = Form(...),file: Union[UploadFile, None] = None, text: str = Form(...), vectorestoreid: int = Form(...)):
def generate_text(payload: defaultRetrievalRequest):
    log.info("Entered create usecase routing method")
    try:
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        
        return defaultQARetrievalKepler(payload.text,payload.fileupload,payload.llmtype,payload.vectorestoreid)

        # log.info("after invoking create usecase service ")
        # log.info("exit create usecase routing method")
        # return output_text
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    
@router.post("/cov")#, response_model=Choice)
# def generate_text(fileupload: bool = Form(...),cov: bool = Form(...),cot: bool = Form(...),file: Union[UploadFile, None] = None, text: str = Form(...), vectorestoreid: int = Form(...)):
def generate_text(payload: covRequest):
    log.info("Entered create usecase routing method")
    try:
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        
        return cov(payload.text,payload.fileupload,payload.complexity,payload.llmtype,payload.vectorestoreid)

        # log.info("after invoking create usecase service ")
        # log.info("exit create usecase routing method")
        # return output_text
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)   

@router.post("/cot")#, response_model=Choice)
# def generate_text(fileupload: bool = Form(...),cov: bool = Form(...),cot: bool = Form(...),file: Union[UploadFile, None] = None, text: str = Form(...), vectorestoreid: int = Form(...)):
def generate_text(payload: defaultRetrievalRequest):
    log.info("Entered create usecase routing method")
    try:
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        
        return cot(payload.text,payload.fileupload,payload.llmtype,payload.vectorestoreid)

        # log.info("after invoking create usecase service ")
        # log.info("exit create usecase routing method")
        # return output_text
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)      
    
@router.post("/thot")#, response_model=Choice)
# def generate_text(fileupload: bool = Form(...),thotov: bool = Form(...),cot: bool = Form(...),file: Union[UploadFile, None] = None, text: str = Form(...), vectorestoreid: int = Form(...)):
def generate_text(payload: defaultRetrievalRequest):
    log.info("Entered create usecase routing method")
    try:
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        
        return thot(payload.text,payload.fileupload,payload.llmtype,payload.vectorestoreid)

        # log.info("after invoking create usecase service ")
        # log.info("exit create usecase routing method")
        # return output_text
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)  
    
    
@router.post("/lot")#, response_model=Choice)
# def generate_text(fileupload: bool = Form(...),thotov: bool = Form(...),cot: bool = Form(...),file: Union[UploadFile, None] = None, text: str = Form(...), vectorestoreid: int = Form(...)):
def generate_text(payload: defaultRetrievalRequest):
    log.info("Entered create usecase routing method")
    try:
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        
        return lot(payload.text,payload.fileupload,payload.llmtype,payload.vectorestoreid)

        # log.info("after invoking create usecase service ")
        # log.info("exit create usecase routing method")
        # return output_text
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    
@router.post("/geval")
def generate_text(payload: gevalRequest):
    log.info("Entered create usecase routing method")
    try:
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        output_text = gEval(payload.text,payload.response,payload.sourcetext, payload.llmtype)
        log.info("after invoking create usecase service ")
        # log.debug("response : " + str(response))
        log.info("exit create usecase routing method")
        return output_text
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)    
        
@router.post("/caching")#, response_model=Choice)
def generate_text(payload: cachingRequest):
    log.info("Entered create usecase routing method")
    try:
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        output_text = caching(payload.vectorestoreid, payload.llmtype)
        log.info("after invoking create usecase service ")
        log.info("exit create usecase routing method")
        return output_text
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    
@router.post("/removeCache")#, response_model=Choice)
def generate_text(payload: removecachingRequest):
    log.info("Entered create usecase routing method")
    try:
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        output_text = removeCache(payload.id)
        log.info("after invoking create usecase service ")
        log.info("exit create usecase routing method")
        return output_text
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    
@router.post("/multimodal_Image")
# def multimodal_RAG(file: List[UploadFile] = File(...),text:str=Form(...))->List:
def multimodal_Image_RAG(file: List[UploadFile] = File(...),text:str=Form(...), cov_complexity: str = Form("medium"), llmtype: str =Form("openai"))->List:
    log.info("Entered create usecase routing method")
    log.info("MultiModal API STARTED")
    try:
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        payload={"file":file,"text":text, "cov_complexity": cov_complexity, "llmtype": llmtype}
        m = Multimodal()
        response = m.image_rag(payload)
        log.info("after invoking create usecase service ")
        log.info("exit create usecase routing method")
        print("response",response)
        return response
        # return responseObj
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)

@router.post("/multimodal_Video")
# def multimodal_RAG(file: List[UploadFile] = File(...),text:str=Form(...))->List:
def multimodal_Video_RAG(file: UploadFile = File(...),text:str=Form(...), cov_complexity: str = Form("medium"), llmtype: str =Form("openai"))->List:
    log.info("Entered create usecase routing method")
    log.info("MultiModal Video API STARTED")
    try:
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        payload={"file":file, "text":text, "cov_complexity": cov_complexity, "llmtype": llmtype}
        response = video_rag(payload)
        log.info("after invoking create usecase service ")
        log.info("exit create usecase routing method")
        print("response",response)
        return response
        # return responseObj
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    
@router.post("/multimodal_Audio")
# def multimodal_RAG(file: List[UploadFile] = File(...),text:str=Form(...))->List:
def multimodal_Audio_RAG(file: List[UploadFile] = File(...),text:str=Form(...), cov_complexity: str = Form("medium"), llmtype: str =Form("openai"))->List:
    log.info("Entered create usecase routing method")
    log.info("MultiModal Audio API STARTED")
    try:
        log.info("before invoking create usecase service ")
        id = uuid.uuid4().hex
        request_id_var.set(id)
        payload={"file":file,"text":text, "cov_complexity": cov_complexity, "llmtype": llmtype}
        response = audio_rag(payload)
        log.info("after invoking create usecase service ")
        log.info("exit create usecase routing method")
        print("response",response)
        return response
        # return responseObj
    except completionException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
