"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from typing import Annotated, List,  Optional
from config.logger import CustomLogger
from exception.exception import AzureBlobException
from service.service import FairnessUIservice
from fastapi import APIRouter, HTTPException, UploadFile, Form, Query
from fastapi.responses import  Response,StreamingResponse
import io
from mappers.mappers import BlobInfo
router = APIRouter()

log=CustomLogger()
uiService = FairnessUIservice()


@router.post('/azureBlob/addFile')
def azure_add_dataset(file: UploadFile,container_name: Annotated[str, Form()]):
    try:
        log.info('before invoking azure add dataset service')
        response =uiService.azure_addFile(file,container_name)
        log.debug(response)
        return response
    except Exception as e:
        # log.error(str(e))
        log.exception("Exception details:") 
        log.info('exit azure add blob service')

        raise HTTPException(status_code=500, detail=f"Error in adding blob: {str(e)}")

@router.get("/azureBlob/{container_name}/listBlobs", response_model=List[BlobInfo])
def list_blobs(
    container_name:str=...,
    name_starts_with: Optional[str] = Query(None, description="Filter blobs that start with this prefix"),
    content_type: Optional[str] = Query(None, description="Filter blobs by content type"),
    max_results: Optional[int] = Query(100, description="Maximum number of results to return")
):
    try:
        log.info('before invoking azure list blob service')
        response = uiService.list_blobs(container_name,name_starts_with, content_type, max_results)
        log.debug(response)
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get('/azureBlob/getBlob')
def azure_get_blob(blob_name: str,container_name: str):
    try:
        log.info('before invoking azure get blob service')
        headers = {
            "Content-Disposition": f"attachment; filename={blob_name}",
        }
        return StreamingResponse(uiService.get_blob(blob_name,container_name), headers=headers, media_type="application/octet-stream")
        
    except Exception as e:
        log.exception("Exception details:") 
        log.info('exit azure get blob service')
        raise HTTPException(status_code=500, detail=f"Error in fetching blob: {str(e)}")
    

@router.delete("/azureBlob/delete_blob")
def delete_blob(blob_name: str,container_name:str):
    try:
        uiService.delete_blob(container_name,blob_name)
        return {"message": f"Blob '{blob_name}' deleted successfully"}
    except Exception as e:
        log.exception("Exception details:") 
        log.info('exit azure delete blob service')
        raise HTTPException(status_code=500, detail=f"Error deleting blob: {str(e)}")
    
@router.post('/azureBlob/updateFile')
def azure_add_dataset(file: UploadFile,blob_name: Annotated[str, Form()], container_name: Annotated[str, Form()]):
    try:
        log.info('before invoking azure update file service')
        response = uiService.azure_updateFile(file,blob_name,container_name)
        log.debug(response)
        return response
    except Exception as e:
        log.exception("Exception details:") 
        log.info('exit azure update file service')
        raise HTTPException(status_code=500, detail=f"Error updating blob: {str(e)}")
    
    
@router.get('/azureBlob/List-Containers')
def list_containers():
    try:
        log.info('before invoking azure list container service')
        response = uiService.list_container()
        log.debug(response)
        return response
    except Exception as e:
        log.exception("Exception details:") 
        log.info('exit azure list conatiner service')
        raise HTTPException(status_code=500, detail=f"Error in fetching containers: {str(e)}")
    
@router.post('/azureBlob/addContainer')
def azureBlob_addContainer(container_name: Annotated[str, Form()]):
    try:
        log.info('before invoking azure update file service')
        response = uiService.azure_addContainer(container_name)
        log.debug(response)
        return response
    except Exception as e:
        log.exception("Exception details:") 
        log.info('exit azure add container service')
        raise HTTPException(status_code=500, detail=f"Error updating blob: {str(e)}")  