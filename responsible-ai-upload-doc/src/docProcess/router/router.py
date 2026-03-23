'''
Copyright 2024-2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from io import BytesIO
from fastapi import Depends, File, Form,Request,APIRouter, HTTPException, UploadFile
from typing import List, Optional, Union

from docProcess.exception.exception import PrivacyException;

from docProcess.config.logger import CustomLogger

from docProcess.service.service import DocProcess
from fastapi.responses import StreamingResponse

router = APIRouter()
log=CustomLogger()
from docProcess.dao.DocProccessDb import docDb    

@router.post('/docProcess/uploadFile')
def pdfFile_anonymize(file: UploadFile = File(...),userId:str=Form(...),exclusionList:Optional[str]=Form(None),maskImage: UploadFile = File(None),categories:Optional[str]=Form(...),subCategoey:Optional[str]=Form(None)):
    try:
        # re = payload.file._file
        # b = io.BytesIO()
        # print(b.read)
        # print("ressssss",re)
        print(subCategoey)
        payload={"file":file,"userId":userId,"exclusionList":exclusionList,"categories":categories,"subCategoey":subCategoey.split(","),"maskImage":maskImage}
        log.info("before invoking create usecase service ")
        print(payload)
        
        response=DocProcess.uploadFile(payload)
        log.info("after invoking create usecase service ")
        
        log.info("exit create usecase routing method")
        # print("res----",response)
        return response
        
    except PrivacyException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    

@router.get('/docProcess/getFiles/{userId}/{categories}')
def process(userId:str,categories:str)->list:
    try:
        log.info("before invoking create usecase service ")
        # print(payload)
        
        response=DocProcess.getFiles(userId,categories)
        log.info("after invoking create usecase service ")
        
        log.info("exit create usecase routing method")
        # print("res----",response)
        return response
        
    except PrivacyException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
@router.post('/docProcess/getFileContent/{docId}')
def process(docId:float):
    try:
        log.info("before invoking create usecase service ")
        # print(payload)

        response=DocProcess.getFileContent(docId)
        log.info("after invoking create usecase service ")

        log.info("exit create usecase routing method")
        # print("res----",response)
        return response

    except PrivacyException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
     
        
@router.get('/docProcess/download/{file_id}')
def download_file(file_id):
    try:
        return docDb.get_file_stream(file_id) 
   
    except Exception as cie:
        log.error(cie.__dict__)
        log.info("exit download file usecase routing method")
        raise HTTPException(**cie.__dict__)
