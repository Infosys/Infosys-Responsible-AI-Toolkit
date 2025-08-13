import boto3
from botocore.exceptions import ClientError, NoCredentialsError
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
from botocore.config import Config


logger = logging.getLogger("aws")
logger.setLevel(logging.DEBUG)

# Set the logging level for boto3
boto3.set_stream_logger('boto3', logging.DEBUG)
boto3.set_stream_logger('botocore', logging.DEBUG)

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

# Configure multipart upload chunk size (equivalent to Azure's CHUNK_SIZE)
CHUNK_SIZE = 15 * 1024 * 1024  # 15MB

class FairnessUIservice:
    def __init__(self):
        # Configure boto3 with multipart threshold and chunk size
        config = Config(
            max_pool_connections=50,
            retries={'max_attempts': 3},
            signature_version='s3v4'
        )

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
            config=config
        )


    def list_buckets(self) -> List[str]:
        """List all S3 buckets"""
        try:
            response = self.s3_client.list_buckets()
            return [bucket['Name'] for bucket in response['Buckets']]
        except ClientError as e:
            logger.error(f"Error listing buckets: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def s3_upload_file(self, file, bucket_name: str, object_key: Optional[str] = None) -> dict:
        """Upload file to S3 bucket"""
        start_time = time.time()
        print("Upload file started at", start_time)

        if object_key is None:
            unique_id = str(uuid.uuid4()) 
            filename, file_extension = os.path.splitext(file.filename)
            object_key = f"{filename}_{unique_id}{file_extension}"

        print(f"Object key: {object_key}")

        try:
            # Check if object already exists (equivalent to overwrite=False)
            try:
                self.s3_client.head_object(Bucket=bucket_name, Key=object_key)
                raise HTTPException(status_code=409, detail=f"Object '{object_key}' already exists")
            except ClientError as e:
                if e.response['Error']['Code'] != '404':
                    raise

            print("Uploading to AWS S3 as object:", object_key)

            # Upload with metadata
            extra_args = {
                'ContentType': file.content_type,
                'Metadata': {
                    'original_filename': file.filename
                }
            }

            # Reset file pointer to beginning
            file.file.seek(0)



            self.s3_client.upload_fileobj(
                file.file,
                bucket_name,
                object_key
            )

            response = {
                "object_key": object_key,
            }

            end_time = time.time()
            print("Upload file ended at", end_time)
            print("Total time it takes to upload the file is", end_time - start_time, "seconds")
            return response

        except ClientError as e:
            logger.error(f"Error uploading file: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def s3_update_file(self, file, object_key: str, bucket_name: str) -> dict:
        """Update/overwrite file in S3 bucket"""
        try:
            print("Uploading to AWS S3 as object:", object_key)

            # Upload with metadata (overwrite=True equivalent)
            extra_args = {
                'ContentType': file.content_type,
                'Metadata': {
                    'original_filename': file.filename
                }
            }

            # Reset file pointer to beginning
            file.file.seek(0)


            self.s3_client.upload_fileobj(
                file.file,
                bucket_name,
                object_key
            )

            response = {
                "object_key": object_key,
            }
            return response

        except ClientError as e:
            logger.error(f"Error updating file: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_object(self, object_key: str, bucket_name: str) -> Generator[bytes, None, None]:
        """Download S3 object in chunks"""
        try:
            # Get object with streaming
            response = self.s3_client.get_object(Bucket=bucket_name, Key=object_key)

            # Stream the object body in chunks
            for chunk in response['Body'].iter_chunks(chunk_size=CHUNK_SIZE):
                start_time = time.time()
                yield chunk
                end_time = time.time()
                print("Time taken to download the chunk is", end_time - start_time, "seconds")

        except ClientError as e:
            logger.error(f"Error downloading object: {e}")
            raise HTTPException(status_code=404 if e.response['Error']['Code'] == 'NoSuchKey' else 500, 
                              detail=str(e))

    def delete_object(self, bucket_name: str, object_key: str):
        """Delete S3 object"""
        try:
            self.s3_client.delete_object(Bucket=bucket_name, Key=object_key)
            logger.info(f"Successfully deleted object: {object_key}")
        except ClientError as e:
            logger.error(f"Error deleting object: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def s3_create_bucket(self, bucket_name: str) -> dict:
        """Create S3 bucket"""
        try:
            # For regions other than us-east-1, you need to specify LocationConstraint
            region = os.getenv('AWS_REGION', 'us-east-1')

            if region == 'us-east-1':
                self.s3_client.create_bucket(Bucket=bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )

            return {"message": f"Bucket '{bucket_name}' created successfully"}

        except ClientError as e:
            logger.error(f"Error creating bucket: {e}")
            if e.response['Error']['Code'] == 'BucketAlreadyExists':
                raise HTTPException(status_code=409, detail=f"Bucket '{bucket_name}' already exists")
            raise HTTPException(status_code=500, detail=str(e))

    def is_valid_bucket_name(self, name: str) -> bool:
        """Validate S3 bucket name according to AWS naming rules"""
        if len(name) < 3 or len(name) > 63:
            return False

        # S3 bucket naming rules
        pattern = r'^[a-z0-9]([a-z0-9\-]*[a-z0-9])?$'

        if not re.match(pattern, name):
            return False

        # Additional checks
        if '..' in name or '.-' in name or '-.' in name:
            return False

        # Cannot be formatted as IP address
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        if re.match(ip_pattern, name):
            return False

        return True

    def is_valid_object_key(self, name: str) -> bool:
        """Validate S3 object key"""
        # S3 object keys can be up to 1024 characters
        if len(name) > 1024 or len(name) == 0:
            return False

        # S3 allows most characters, but some should be avoided or encoded
        # This is a basic validation - in practice, most characters are allowed
        return True

    def get_object_properties(self, object_key: str, bucket_name: str) -> dict:
        """Get S3 object metadata"""
        if not self.is_valid_bucket_name(bucket_name):
            raise ValueError(f"Invalid bucket name: {bucket_name}")
        if not self.is_valid_object_key(object_key):
            raise ValueError(f"Invalid object key: {object_key}")

        try:
            response = self.s3_client.head_object(Bucket=bucket_name, Key=object_key)

            print("Full response", response)
            print(f"Object key: {object_key}")
            print(f"Object size: {response['ContentLength']}")
            print(f"Object Last Modified: {response['LastModified']}")

            return {
                "object_key": object_key,
                "object_type": "S3Object",  # S3 doesn't have blob types like Azure
                "object_size": response['ContentLength'],
                "last_modified": response['LastModified'],
                "content_type": response.get('ContentType', 'binary/octet-stream'),
                "etag": response['ETag'],
                "metadata": response.get('Metadata', {})
            }

        except ClientError as e:
            print(f"Failed to get object properties: {e}")
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise HTTPException(status_code=404, detail=f"Object '{object_key}' not found")
            raise HTTPException(status_code=500, detail=str(e))

    def list_objects(self, bucket_name: str, key_starts_with: Optional[str] = None, 
                     content_type: Optional[str] = None, max_results: Optional[int] = None) -> List[BlobInfo]:
        """List objects in S3 bucket with optional filtering"""
        try:
            # Prepare parameters for list_objects_v2
            params = {'Bucket': bucket_name}

            if key_starts_with:
                params['Prefix'] = key_starts_with

            if max_results:
                params['MaxKeys'] = max_results

            response = self.s3_client.list_objects_v2(**params)

            if 'Contents' not in response:
                return []

            filtered_objects = []

            for obj in response['Contents']:
                # Get object metadata to check content type if needed
                if content_type:
                    try:
                        head_response = self.s3_client.head_object(
                            Bucket=bucket_name, 
                            Key=obj['Key']
                        )
                        obj_content_type = head_response.get('ContentType', 'binary/octet-stream')

                        if obj_content_type != content_type:
                            continue
                    except ClientError:
                        # If we can't get the head, skip content type filtering for this object
                        if content_type:
                            continue
                        obj_content_type = 'binary/octet-stream'
                else:
                    obj_content_type = 'binary/octet-stream'  # Default for listing

                object_info = BlobInfo(  # Reusing BlobInfo class for compatibility
                    name=obj['Key'],
                    size=obj['Size'],
                    last_modified=obj['LastModified'],
                    content_type=obj_content_type
                )

                filtered_objects.append(object_info)

                # If we have max_results, stop when we reach it
                if max_results and len(filtered_objects) >= max_results:
                    break

            return filtered_objects

        except ClientError as e:
            logger.error(f"Error listing objects: {e}")
            raise HTTPException(status_code=500, detail=str(e))