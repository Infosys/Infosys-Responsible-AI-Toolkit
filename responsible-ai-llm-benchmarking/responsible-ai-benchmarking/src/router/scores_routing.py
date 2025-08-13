"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from fastapi import APIRouter, HTTPException, UploadFile, Form
from fastapi.responses import StreamingResponse, FileResponse
from config.logger import CustomLogger
from service.scores import Scores
from dao.mappers.fairness import Fairness
from typing import Dict, Any
import io
import os
router = APIRouter()

#Router for scores operations
log=CustomLogger()
service=Scores()

@router.get("/scores/getScores")
def getScore(category:str):
    log.info("Entered Scores")
    try:
        response=service.getScores(category)
        log.info("Response from getScore is: ",str(response))
        return response
        
    except Exception as e:
        log.error(e.__dict__)
        log.info("Exit getScore with",e.__dict__)
        raise HTTPException(**e.__dict__)

log=CustomLogger()
@router.post("/scores/addScore")
def addScore(payload:Dict[str, Any]):
    log.info("Entered Utils")
    try:
        if "inhouse_model" not in payload:
            payload["inhouse_model"]=False
        response=service.addScore(payload)
        return response
        
    except Exception as e:
        log.error(e.__dict__)
        log.info("Exit dataset with",e.__dict__)
        raise HTTPException(**e.__dict__)
    
    
og=CustomLogger()
@router.post("/scores/deleteScore")
def deleteScore(category:str,model_name:str):
    log.info("Entered deleteScore")
    try:
        response=service.deleteScores(category,model_name)
        return response
        
    except Exception as e:
        log.error(e.__dict__)
        log.info("Exit dataset with",e.__dict__)
        raise HTTPException(**e.__dict__)
