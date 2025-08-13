from datetime import datetime
from typing import Annotated, List, Optional
from config.logger import CustomLogger
from service.gcp_service import FairnessUIservice
from mappers.mappers import BlobInfo
from fastapi import APIRouter, HTTPException, Query, UploadFile, Form
from fastapi.responses import Response, StreamingResponse
import io

gcp_router = APIRouter()

log = CustomLogger()
uiService = FairnessUIservice()


@gcp_router.post('/gcs/addFile')
def gcs_add_file(file: UploadFile, bucket_name: Annotated[str, Form()], object_name: Annotated[str, Form()] = None):
    """Upload a file to Google Cloud Storage bucket"""
    try:
        log.info('before invoking gcs add file service')
        response = uiService.gcs_addFile(file, bucket_name, object_name)
        log.debug(response)
        return response
    except Exception as e:
        log.exception("Exception details:")
        log.info('exit gcs add file service')
        raise HTTPException(status_code=500, detail=f"Error in adding object: {str(e)}")


@gcp_router.get("/gcs/{bucket_name}/listObjects", response_model=List[BlobInfo])
def list_objects(
    bucket_name: str = ...,
    name_starts_with: Optional[str] = Query(None, description="Filter objects that start with this prefix"),
    content_type: Optional[str] = Query(None, description="Filter objects by content type"),
    max_results: Optional[int] = Query(100, description="Maximum number of results to return")
):
    """List objects in a GCS bucket with optional filtering"""
    try:
        log.info('before invoking gcs list objects service')
        response = uiService.list_objects(bucket_name, name_starts_with, content_type, max_results)
        log.debug(response)
        return response
    except Exception as e:
        log.exception("Exception details:")
        log.info('exit gcs list objects service')
        raise HTTPException(status_code=500, detail=f"Error in listing objects: {str(e)}")


@gcp_router.get('/gcs/getObject')
def gcs_get_object(object_name: str, bucket_name: str):
    """Download an object from GCS bucket"""
    try:
        log.info('before invoking gcs get object service')
        headers = {
            "Content-Disposition": f"attachment; filename={object_name}",
        }
        return StreamingResponse(
            uiService.get_object(object_name, bucket_name), 
            headers=headers, 
            media_type="application/octet-stream"
        )
    except Exception as e:
        log.exception("Exception details:")
        log.info('exit gcs get object service')
        raise HTTPException(status_code=500, detail=f"Error in fetching object: {str(e)}")


@gcp_router.delete("/gcs/deleteObject")
def delete_object(object_name: str, bucket_name: str):
    """Delete an object from GCS bucket"""
    try:
        log.info('before invoking gcs delete object service')
        uiService.delete_object(bucket_name, object_name)
        log.info('exit gcs delete object service')
        return {"message": f"Object '{object_name}' deleted successfully"}
    except Exception as e:
        log.exception("Exception details:")
        log.info('exit gcs delete object service')
        raise HTTPException(status_code=500, detail=f"Error deleting object: {str(e)}")


@gcp_router.post('/gcs/updateFile')
def gcs_update_file(file: UploadFile, object_name: Annotated[str, Form()], bucket_name: Annotated[str, Form()]):
    """Update (overwrite) an existing file in GCS bucket"""
    try:
        log.info('before invoking gcs update file service')
        response = uiService.gcs_updateFile(file, object_name, bucket_name)
        log.debug(response)
        log.info('exit gcs update file service')
        return response
    except Exception as e:
        log.exception("Exception details:")
        log.info('exit gcs update file service')
        raise HTTPException(status_code=500, detail=f"Error updating object: {str(e)}")


@gcp_router.get('/gcs/listBuckets')
def list_buckets():
    """List all GCS buckets in the project"""
    try:
        log.info('before invoking gcs list buckets service')
        response = uiService.list_buckets()
        log.debug(response)
        log.info('exit gcs list buckets service')
        return response
    except Exception as e:
        log.exception("Exception details:")
        log.info('exit gcs list buckets service')
        raise HTTPException(status_code=500, detail=f"Error in fetching buckets: {str(e)}")


@gcp_router.post('/gcs/addBucket')
def gcs_add_bucket(bucket_name: Annotated[str, Form()]):
    """Create a new GCS bucket"""
    try:
        log.info('before invoking gcs add bucket service')
        response = uiService.gcs_addBucket(bucket_name)
        log.debug(response)
        log.info('exit gcs add bucket service')
        return response
    except Exception as e:
        log.exception("Exception details:")
        log.info('exit gcs add bucket service')
        raise HTTPException(status_code=500, detail=f"Error creating bucket: {str(e)}")


@gcp_router.get("/gcs/getObjectProperties")
def get_object_properties(object_name: str, bucket_name: str):
    """Get properties of an object in GCS bucket"""
    try:
        log.info('before invoking gcs get object properties service')
        response = uiService.get_object_properties(object_name, bucket_name)
        log.debug(response)
        log.info('exit gcs get object properties service')
        return response
    except Exception as e:
        log.exception("Exception details:")
        log.info('exit gcs get object properties service')
        raise HTTPException(status_code=500, detail=f"Error in fetching object properties: {str(e)}")


# Additional GCS-specific endpoints that might be useful

# @gcp_router.get("/gcs/bucketExists")
# def check_bucket_exists(bucket_name: str):
#     """Check if a bucket exists"""
#     try:
#         log.info('before invoking gcs check bucket exists service')
#         bucket = uiService.storage_client.bucket(bucket_name)
#         exists = bucket.exists()
#         log.info('exit gcs check bucket exists service')
#         return {"bucket_name": bucket_name, "exists": exists}
#     except Exception as e:
#         log.exception("Exception details:")
#         log.info('exit gcs check bucket exists service')
#         raise HTTPException(status_code=500, detail=f"Error checking bucket existence: {str(e)}")


# @gcp_router.get("/gcs/objectExists")
# def check_object_exists(object_name: str, bucket_name: str):
#     """Check if an object exists in a bucket"""
#     try:
#         log.info('before invoking gcs check object exists service')
#         bucket = uiService.storage_client.bucket(bucket_name)
#         blob = bucket.blob(object_name)
#         exists = blob.exists()
#         log.info('exit gcs check object exists service')
#         return {"bucket_name": bucket_name, "object_name": object_name, "exists": exists}
#     except Exception as e:
#         log.exception("Exception details:")
#         log.info('exit gcs check object exists service')
#         raise HTTPException(status_code=500, detail=f"Error checking object existence: {str(e)}")


# @gcp_router.delete("/gcs/deleteBucket")
# def delete_bucket(bucket_name: str, force: bool = Query(False, description="Force delete bucket even if not empty")):
#     """Delete a GCS bucket"""
#     try:
#         log.info('before invoking gcs delete bucket service')
#         bucket = uiService.storage_client.bucket(bucket_name)
        
#         if force:
#             # Delete all objects in the bucket first
#             blobs = bucket.list_blobs()
#             for blob in blobs:
#                 blob.delete()
        
#         bucket.delete()
#         log.info('exit gcs delete bucket service')
#         return {"message": f"Bucket '{bucket_name}' deleted successfully"}
#     except Exception as e:
#         log.exception("Exception details:")
#         log.info('exit gcs delete bucket service')
#         raise HTTPException(status_code=500, detail=f"Error deleting bucket: {str(e)}")


# @gcp_router.post("/gcs/copyObject")
# def copy_object(
#     source_bucket: Annotated[str, Form()],
#     source_object: Annotated[str, Form()],
#     destination_bucket: Annotated[str, Form()],
#     destination_object: Annotated[str, Form()]
# ):
#     """Copy an object from one location to another"""
#     try:
#         log.info('before invoking gcs copy object service')
#         source_bucket_obj = uiService.storage_client.bucket(source_bucket)
#         source_blob = source_bucket_obj.blob(source_object)
        
#         destination_bucket_obj = uiService.storage_client.bucket(destination_bucket)
        
#         # Copy the blob
#         new_blob = source_bucket_obj.copy_blob(source_blob, destination_bucket_obj, destination_object)
        
#         log.info('exit gcs copy object service')
#         return {
#             "message": f"Object copied successfully",
#             "source": f"{source_bucket}/{source_object}",
#             "destination": f"{destination_bucket}/{destination_object}"
#         }
#     except Exception as e:
#         log.exception("Exception details:")
#         log.info('exit gcs copy object service')
#         raise HTTPException(status_code=500, detail=f"Error copying object: {str(e)}")


# @gcp_router.post("/gcs/moveObject")
# def move_object(
#     source_bucket: Annotated[str, Form()],
#     source_object: Annotated[str, Form()],
#     destination_bucket: Annotated[str, Form()],
#     destination_object: Annotated[str, Form()]
# ):
#     """Move an object from one location to another"""
#     try:
#         log.info('before invoking gcs move object service')
#         source_bucket_obj = uiService.storage_client.bucket(source_bucket)
#         source_blob = source_bucket_obj.blob(source_object)
        
#         destination_bucket_obj = uiService.storage_client.bucket(destination_bucket)
        
#         # Copy the blob
#         new_blob = source_bucket_obj.copy_blob(source_blob, destination_bucket_obj, destination_object)
        
#         # Delete the source blob
#         source_blob.delete()
        
#         log.info('exit gcs move object service')
#         return {
#             "message": f"Object moved successfully",
#             "source": f"{source_bucket}/{source_object}",
#             "destination": f"{destination_bucket}/{destination_object}"
#         }
#     except Exception as e:
#         log.exception("Exception details:")
#         log.info('exit gcs move object service')
#         raise HTTPException(status_code=500, detail=f"Error moving object: {str(e)}")