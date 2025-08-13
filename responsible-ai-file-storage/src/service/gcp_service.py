from google.cloud import storage
from google.cloud.exceptions import NotFound, GoogleCloudError
from fastapi import HTTPException
from dotenv import load_dotenv
import uuid
import os
import time
import logging
import sys
from mappers.mappers import BlobInfo
import re
from typing import Optional, List, Generator
from io import BytesIO

import requests
from google.oauth2 import service_account

requests.packages.urllib3.disable_warnings()
requests.Session.verify = False

logger = logging.getLogger("gcp")
logger.setLevel(logging.DEBUG)

# Set the logging level for the google.cloud.storage library
logger = logging.getLogger("google.cloud.storage")
logger.setLevel(logging.DEBUG)

# Direct logging output to stdout
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

print(
    f"Logger enabled for ERROR={logger.isEnabledFor(logging.ERROR)}, "
    f"WARNING={logger.isEnabledFor(logging.WARNING)}, "
    f"INFO={logger.isEnabledFor(logging.INFO)}, "
    f"DEBUG={logger.isEnabledFor(logging.DEBUG)}"
)

load_dotenv()
CHUNK_SIZE = 15 * 1024 * 1024  # 15MB chunks


class FairnessUIservice:
    def __init__(self):
        # Initialize GCS client
        # You can either:
        # 1. Set GOOGLE_APPLICATION_CREDENTIALS environment variable to point to service account JSON
        # 2. Or pass credentials explicitly: storage.Client.from_service_account_json('path/to/credentials.json')
        # 3. Or use default credentials if running on GCP
        
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_path:
            self.storage_client = storage.Client.from_service_account_json(credentials_path)
        else:
            # Use default credentials (works on GCP or if gcloud auth is configured)
            self.storage_client = storage.Client()
    
    def list_buckets(self) -> List[str]:
        """List all buckets in the project"""
        try:
            buckets = self.storage_client.list_buckets()
            return [bucket.name for bucket in buckets]
        except GoogleCloudError as e:
            logger.error(f"Failed to list buckets: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to list buckets: {str(e)}")
    
    def gcs_addFile(self, file, bucket_name: str, object_name: Optional[str] = None) -> dict:
        """Upload a file to GCS bucket"""
        start_time = time.time()
        print("Upload file started at", start_time)
        
        if object_name is None:
            unique_id = str(uuid.uuid4())
            filename, file_extension = os.path.splitext(file.filename)
            object_name = f"{filename}_{unique_id}{file_extension}"
        
        print(f"Uploading to GCS bucket '{bucket_name}' as object: {object_name}")
        
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(object_name)
            
            # Set content type
            blob.content_type = file.content_type
            
            # Upload file data
            file.file.seek(0)  # Reset file pointer to beginning
            blob.upload_from_file(file.file, timeout=300)
            
            response = {
                "object_name": object_name,
            }
            
            end_time = time.time()
            print("Upload file ended at", end_time)
            print("Total time it takes to upload the file is", end_time - start_time, "seconds")
            
            return response
            
        except GoogleCloudError as e:
            logger.error(f"Failed to upload file: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
    
    def gcs_updateFile(self, file, object_name: str, bucket_name: str) -> dict:
        """Update (overwrite) an existing file in GCS bucket"""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(object_name)
            
            # Set content type
            blob.content_type = file.content_type
            
            print(f"Updating object in GCS bucket '{bucket_name}': {object_name}")
            
            # Upload file data (this overwrites by default)
            file.file.seek(0)  # Reset file pointer to beginning
            blob.upload_from_file(file.file, timeout=300)
            
            response = {
                "object_name": object_name,
            }
            
            return response
            
        except GoogleCloudError as e:
            logger.error(f"Failed to update file: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to update file: {str(e)}")
    
    def get_object(self, object_name: str, bucket_name: str) -> Generator[bytes, None, None]:
        """Download object in chunks"""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(object_name)
            
            # Download blob in chunks
            start_byte = 0
            blob_size = blob.size
            
            if blob_size is None:
                # If size is not available, download the whole blob
                start_time = time.time()
                data = blob.download_as_bytes()
                end_time = time.time()
                print("Time taken to download the object is", end_time - start_time, "seconds")
                yield data
                return
            
            while start_byte < blob_size:
                end_byte = min(start_byte + CHUNK_SIZE - 1, blob_size - 1)
                
                start_time = time.time()
                chunk = blob.download_as_bytes(start=start_byte, end=end_byte)
                end_time = time.time()
                print("Time taken to download the chunk is", end_time - start_time, "seconds")
                
                yield chunk
                start_byte = end_byte + 1
                
        except NotFound:
            raise HTTPException(status_code=404, detail=f"Object '{object_name}' not found in bucket '{bucket_name}'")
        except GoogleCloudError as e:
            logger.error(f"Failed to download object: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to download object: {str(e)}")
    
    def delete_object(self, bucket_name: str, object_name: str) -> None:
        """Delete an object from GCS bucket"""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(object_name)
            blob.delete()
            print(f"Object '{object_name}' deleted from bucket '{bucket_name}'")
            
        except NotFound:
            raise HTTPException(status_code=404, detail=f"Object '{object_name}' not found in bucket '{bucket_name}'")
        except GoogleCloudError as e:
            logger.error(f"Failed to delete object: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to delete object: {str(e)}")
    
    def gcs_addBucket(self, bucket_name: str) -> dict:
        """Create a new GCS bucket"""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            bucket.create()
            return {"message": f"Bucket '{bucket_name}' created successfully"}
            
        except GoogleCloudError as e:
            logger.error(f"Failed to create bucket: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create bucket: {str(e)}")
    
    def is_valid_bucket_name(self, name: str) -> bool:
        """Validate GCS bucket name according to GCS naming rules"""
        # GCS bucket naming rules:
        # - 3-63 characters
        # - lowercase letters, numbers, hyphens, underscores, dots
        # - must start and end with alphanumeric
        # - cannot contain consecutive dots
        # - cannot be formatted as IP address
        if len(name) < 3 or len(name) > 63:
            return False
        
        # Check basic pattern
        if not re.match(r'^[a-z0-9]([a-z0-9._-]*[a-z0-9])?$', name):
            return False
        
        # Check for consecutive dots
        if '..' in name:
            return False
        
        # Check if it looks like an IP address
        if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', name):
            return False
        
        return True
    
    def is_valid_object_name(self, name: str) -> bool:
        """Validate GCS object name"""
        # GCS object names can contain most characters but have some restrictions
        # - Cannot contain certain control characters
        # - Cannot be '.' or '..'
        # - Cannot start with '.well-known/acme-challenge/'
        if name in ['.', '..']:
            return False
        
        if name.startswith('.well-known/acme-challenge/'):
            return False
        
        # Check for control characters
        for char in name:
            if ord(char) < 32 or ord(char) == 127:
                return False
        
        return True
    
    def get_object_properties(self, object_name: str, bucket_name: str) -> dict:
        """Get properties of an object"""
        if not self.is_valid_bucket_name(bucket_name):
            raise ValueError(f"Invalid bucket name: {bucket_name}")
        if not self.is_valid_object_name(object_name):
            raise ValueError(f"Invalid object name: {object_name}")
        
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(object_name)
            blob.reload()  # Fetch the latest metadata
            
            print("Full response", blob.__dict__)
            print(f"Object content type: {blob.content_type}")
            print(f"Object size: {blob.size}")
            print(f"Object time created: {blob.time_created}")
            print(f"Object updated: {blob.updated}")
            
            return {
                "object_name": object_name,
                "object_type": "BlockBlob",  # GCS doesn't have blob types like Azure, all are block blobs
                "object_size": blob.size,
                "last_modified": blob.updated,
                "time_created": blob.time_created,
                "content_type": blob.content_type,
                "etag": blob.etag,
                "md5_hash": blob.md5_hash,
            }
            
        except NotFound:
            raise HTTPException(status_code=404, detail=f"Object '{object_name}' not found in bucket '{bucket_name}'")
        except GoogleCloudError as e:
            logger.error(f"Failed to get object properties: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get object properties: {str(e)}")
    
    def list_objects(self, bucket_name: str, name_starts_with: Optional[str] = None, 
                   content_type: Optional[str] = None, max_results: Optional[int] = None) -> List[BlobInfo]:
        """List objects in a bucket with optional filtering"""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            
            # List blobs with prefix filter
            blobs = bucket.list_blobs(
                prefix=name_starts_with,
                max_results=max_results
            )
            
            filtered_objects = []
            for blob in blobs:
                # Filter by content type if specified
                if content_type and blob.content_type != content_type:
                    continue
                
                blob_info = BlobInfo(
                    name=blob.name,
                    size=blob.size,
                    last_modified=blob.updated,
                    content_type=blob.content_type
                )
                
                filtered_objects.append(blob_info)
                
                # Break if we've reached max_results
                if max_results and len(filtered_objects) >= max_results:
                    break
            
            return filtered_objects
            
        except NotFound:
            raise HTTPException(status_code=404, detail=f"Bucket '{bucket_name}' not found")
        except GoogleCloudError as e:
            logger.error(f"Failed to list objects: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to list objects: {str(e)}")