"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from azure.storage.blob import BlobServiceClient,ContentSettings
from azure.core.exceptions import ResourceExistsError
from config import config
from dotenv import load_dotenv
import uuid 
import os
import time
import io
import logging
import sys
from mappers.mappers import BlobInfo

logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)

# Set the logging level for the azure.storage.blob library
logger = logging.getLogger("azure.storage.blob")
logger.setLevel(logging.DEBUG)

# Direct logging output to stdout. Without adding a handler,
# no logging output is visible.
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

print(
    f"Logger enabled for ERROR={logger.isEnabledFor(logging.ERROR)}, "
    f"WARNING={logger.isEnabledFor(logging.WARNING)}, "
    f"INFO={logger.isEnabledFor(logging.INFO)}, "
    f"DEBUG={logger.isEnabledFor(logging.DEBUG)}"
)

load_dotenv()
CHUNK_SIZE=15*1024*1024
class FairnessUIservice:
    def __init__(self):
        self.blob_service_client = BlobServiceClient.from_connection_string(os.getenv('AZURE_BLOB_STORAGE_CONNECTION_KEY'),max_chunk_get_size=CHUNK_SIZE) 
    
    def list_container(self):
       
        container_list = self.blob_service_client.list_containers()
        return [container.name for container in container_list]
    
    def azure_addFile(self,file,container_name):
        start_time=time.time()
        print("Upload file started at", start_time)
        unique_id = str(uuid.uuid4()) 
        filename, file_extension = os.path.splitext(file.filename)
        blob_name = f"{filename}_{unique_id}{file_extension}"
        print(blob_name)
        container_client = self.blob_service_client.get_container_client(container_name)
        content_settings = ContentSettings(content_type=file.content_type)
        print("Uploading to Azure Storage as blob:", blob_name)
        container_client.upload_blob(data=file.file,name=blob_name, overwrite = False, max_concurrency=4 ,content_settings=content_settings,connection_timeout=30000, logging_enable=True)
        response = {
            "blob_name": blob_name,             
        }
        end_time=time.time()
        print("Upload file ended at", end_time)
        print("Total time it takes to upload the file is", end_time-start_time, "seconds")
        return response
    
    def azure_updateFile(self,file,blob_name,container_name):
        container_client = self.blob_service_client.get_container_client(container_name)
        content_settings = ContentSettings(content_type=file.content_type)
        print("Uploading to Azure Storage as blob:", blob_name)
        container_client.upload_blob(data=file.file,name=blob_name, overwrite = True, max_concurrency=4 ,content_settings=content_settings,connection_timeout=30000, logging_enable=True)
        response = {
            "blob_name": blob_name,                     
        }
        return response

    def get_blob(self,blob_name:str,container_name:str):
       
        container_client = self.blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob=blob_name)
        for chunk in blob_client.download_blob(max_concurrency=4,logging_enable=True).chunks():
            start_time=time.time()
            yield chunk
            end_time=time.time()
            print("Time taken to download the chunk is", end_time-start_time, "seconds")
    
    
    def delete_blob(self,container_name: str, blob_name: str):
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.delete_blob(logging_enable=True)
        
    def azure_addContainer(self,container_name):
        container_client = self.blob_service_client.get_container_client(container_name)
        container_client.create_container()
        return {"message": f"Container '{container_name}' created successfully"}    
    
    def list_blobs(self, container_name: str, name_starts_with: str = None, content_type: str = None, max_results: int = None):
        try:
            container_client = self.blob_service_client.get_container_client(container_name)
            
            blobs = container_client.list_blobs(
                name_starts_with=name_starts_with,
                results_per_page=max_results
            )

            filtered_blobs = []
            for blob in blobs:
                if content_type and blob.content_settings.content_type != content_type:
                    continue
                
                blob_info = BlobInfo(
                    name=blob.name,
                    size=blob.size,
                    last_modified=blob.last_modified,
                    content_type=blob.content_settings.content_type
                )
                
                filtered_blobs.append(blob_info)

            return filtered_blobs[:max_results]

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))





