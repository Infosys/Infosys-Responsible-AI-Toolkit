from datetime import datetime
from typing import Annotated, List, Optional
from config.logger import CustomLogger
from service.aws_service import FairnessUIservice
from mappers.mappers import BlobInfo
from fastapi import APIRouter, HTTPException, Query, UploadFile, Form
from fastapi.responses import Response, StreamingResponse
import io

aws_router = APIRouter()

log = CustomLogger()
uiService = FairnessUIservice()


@aws_router.post('/s3/uploadFile')
def s3_upload_file(file: UploadFile, bucket_name: Annotated[str, Form()], object_key: Annotated[str, Form()] = None):
    try:
        log.info('before invoking s3 upload file service')
        response = uiService.s3_upload_file(file, bucket_name, object_key)
        log.debug(response)
        return response
    except Exception as e:
        log.exception("Exception details:")
        log.info('exit s3 upload file service')
        raise HTTPException(status_code=500, detail=f"Error uploading file to S3: {str(e)}")


@aws_router.get("/s3/{bucket_name}/listObjects", response_model=List[BlobInfo])
def list_objects(
    bucket_name: str = ...,
    key_starts_with: Optional[str] = Query(None, description="Filter objects that start with this prefix"),
    content_type: Optional[str] = Query(None, description="Filter objects by content type"),
    max_results: Optional[int] = Query(100, description="Maximum number of results to return")
):
    try:
        log.info('before invoking s3 list objects service')
        response = uiService.list_objects(bucket_name, key_starts_with, content_type, max_results)
        log.debug(response)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@aws_router.get('/s3/getObject')
def s3_get_object(object_key: str, bucket_name: str):
    try:
        log.info('before invoking s3 get object service')
        headers = {
            "Content-Disposition": f"attachment; filename={object_key}",
        }
        return StreamingResponse(
            uiService.get_object(object_key, bucket_name), 
            headers=headers, 
            media_type="application/octet-stream"
        )
    except Exception as e:
        log.exception("Exception details:")
        log.info('exit s3 get object service')
        raise HTTPException(status_code=500, detail=f"Error fetching object from S3: {str(e)}")


@aws_router.delete("/s3/deleteObject")
def delete_object(object_key: str, bucket_name: str):
    try:
        log.info('before invoking s3 delete object service')
        uiService.delete_object(bucket_name, object_key)
        return {"message": f"Object '{object_key}' deleted successfully"}
    except Exception as e:
        log.exception("Exception details:")
        log.info('exit s3 delete object service')
        raise HTTPException(status_code=500, detail=f"Error deleting object from S3: {str(e)}")


@aws_router.post('/s3/updateFile')
def s3_update_file(file: UploadFile, object_key: Annotated[str, Form()], bucket_name: Annotated[str, Form()]):
    try:
        log.info('before invoking s3 update file service')
        response = uiService.s3_update_file(file, object_key, bucket_name)
        log.debug(response)
        return response
    except Exception as e:
        log.exception("Exception details:")
        log.info('exit s3 update file service')
        raise HTTPException(status_code=500, detail=f"Error updating file in S3: {str(e)}")


@aws_router.get('/s3/listBuckets')
def list_buckets():
    try:
        log.info('before invoking s3 list buckets service')
        response = uiService.list_buckets()
        log.debug(response)
        return response
    except Exception as e:
        log.exception("Exception details:")
        log.info('exit s3 list buckets service')
        raise HTTPException(status_code=500, detail=f"Error fetching S3 buckets: {str(e)}")


@aws_router.post('/s3/createBucket')
def s3_create_bucket(bucket_name: Annotated[str, Form()]):
    try:
        log.info('before invoking s3 create bucket service')
        response = uiService.s3_create_bucket(bucket_name)
        log.debug(response)
        return response
    except Exception as e:
        log.exception("Exception details:")
        log.info('exit s3 create bucket service')
        raise HTTPException(status_code=500, detail=f"Error creating S3 bucket: {str(e)}")


@aws_router.get("/s3/getObjectProperties")
def get_object_properties(object_key: str, bucket_name: str):
    try:
        log.info('before invoking s3 get object properties service')
        response = uiService.get_object_properties(object_key, bucket_name)
        log.debug(response)
        return response
    except Exception as e:
        log.exception("Exception details:")
        log.info('exit s3 get object properties service')
        raise HTTPException(status_code=500, detail=f"Error fetching object properties from S3: {str(e)}")