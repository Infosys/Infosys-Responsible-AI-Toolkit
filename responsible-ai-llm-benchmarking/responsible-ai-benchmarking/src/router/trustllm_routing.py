"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from fastapi import APIRouter, File, HTTPException, UploadFile, Form
from fastapi.responses import StreamingResponse, FileResponse
from config.logger import CustomLogger
from service.operations import Operations
from typing import Annotated, Optional
import io
router = APIRouter()

#Router for dataset generation
log=CustomLogger()
@router.get("/dataset")
def dataset():
    log.info("Entered download/dataset routing")
    try:
        response=Operations.dataset_download()
        log.info("Response from dataset is: ",str(response))
        return response
        
    except Exception as e:
        log.exception(e)
        log.info("Exit dataset with"+str(e))
        raise HTTPException(500,"Internal Server Error")


# router for llm download and generation
@router.get("/offline/generation/")
def offlineGeneration(model_name:str,test_type:str,dataset_name:str):
    log.info("Entered generation routing")
    try:
        response=Operations.generation(model_name,test_type,dataset_name)
        log.info("Response from dataset is: "+str(response))
        return response
        
    except Exception as e:
        log.exception(e)
        log.info("Exit generation with"+str(e))
        raise HTTPException(500,"Internal Server Error")
    
@router.get("/online/generation/")
def onlineGeneration(test_type:str,dataset_name:str,model_url:str,model_name:Optional[str] = None,auth_token:Optional[str] = None):
    log.info("Entered generation routing")
    try:
        response=Operations.onlineGeneration(model_name,test_type,dataset_name,model_url,auth_token)
        log.info("Response from dataset is: ",str(response))
        return response
        
    except Exception as e:
        log.exception(e)
        log.info("Exit generation with"+str(e))
        raise HTTPException(500,"Internal Server Error")




#router for results evaluation
@router.post("/evaluation")
def evaluation(task_type:Annotated[str, Form()],model_name:Annotated[str, Form()],dataset_name:Annotated[str, None,Form()]=None,file: UploadFile = File(default=None),save_to_db:Annotated[str,None,Form()]=None):
    log.info("Entered evaluation routing")
    try:
        response=Operations.evaluation(model_name,dataset_name,file,task_type,save_to_db)
        log.info("Response from evaluation is: ",str(response))
        return response
        
    except Exception as e:
        log.exception(e)
        log.info("Exit evaluation with"+str(e))
        raise HTTPException(500,"Internal Server Error")
    
