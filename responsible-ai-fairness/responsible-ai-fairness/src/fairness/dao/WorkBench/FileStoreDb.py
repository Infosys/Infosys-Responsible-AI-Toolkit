"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from io import BytesIO
from fairness.config.logger import CustomLogger
from fairness.dao.WorkBench.databaseconnection import DataBase_WB
from fairness.exception.custom_exception import CustomHTTPException
from fastapi import HTTPException
from gridfs.errors import NoFile, FileExists
from gridfs import GridFS
import shutil
import os
from dotenv import load_dotenv
load_dotenv()
from fairness.config.logger import CustomLogger
from fairness.dao.databaseconnection import DataBase
from fairness.Telemetry.Telemetry_call import SERVICE_UPLOAD_FILE_METADATA
import datetime
import time
import requests

log = CustomLogger()
ssl_verify=os.getenv("VERIFY_SSL").strip()
verify = False if ssl_verify == "False" else True
active_file_storage = os.getenv('ACTIVE_LLM')
   
# ModelWorkBench = DataBase_WB() 
class FileStoreReportDb:
    
    #fs = GridFS(devraidb)
    # Create a MongoDB database instance

    def __init__(self,db=None) -> None:
        if db is not None:
            log.info("inside filestore")
            self.fs = GridFS(db)
            self.db_type = os.getenv('DB_TYPE').lower()
        else:
            ModelWorkBench = DataBase_WB()
            self.fs = GridFS(ModelWorkBench.db)
            self.db_type = os.getenv('DB_TYPE').lower()
    

    def save_file(self,file, filename,contentType,tenet,container_name=None):
        if self.db_type == 'mongo':
            # Check if file_content is not None
            if file is None:
                raise HTTPException(status_code=500, detail="File content cannot be None")
            
            # Check if filename, contentType, and tenet are not None
            if filename is None or contentType is None or tenet is None:
                raise ValueError("Filename, contentType, and tenet cannot be None")
            
            localTime=time.time()
            time.sleep(1/1000)
            with self.fs.new_file(_id=str(localTime), 
                                        filename=filename,
                                        contentType=contentType,
                                        tenet = tenet,
                                        ) as f:
                f.write(file)

            return f._id
        else:
            if file is None:
                raise HTTPException(status_code=500, detail="File content cannot be None")
            
            # Check if filename, contentType, and tenet are not None
            if filename is None or contentType is None or tenet is None:
                raise ValueError("Filename, contentType, and tenet cannot be None")
                # container_name = os.getenv('HTML_CONTAINER_NAME')
            if active_file_storage == "azureopenai":
                upload_file_api = os.getenv('AZURE_UPLOAD_API')
            elif active_file_storage == "gemini-2.5-flash" or active_file_storage == "gemini-2.5-pro":
                upload_file_api = os.getenv('GCP_UPLOAD_API')
            elif active_file_storage == "aws":
                upload_file_api = os.getenv('AWS_UPLOAD_API')
            # html_containerName = os.getenv('HTML_CONTAINER_NAME')
            log.info(f"container_name:{container_name}")
            # filename = "fairness_file"  # Replace with your actual filename if available
            response =requests.post(url =upload_file_api, files ={"file":(filename, file)}, data ={"container_name":container_name},verify=verify).json()
            if response is None:
                raise HTTPException(f"An error occurred: file not found")
            blob_name =response["blob_name"]
            log.info(f"{blob_name} blob name")
            return blob_name
    

    def save_filecreate(self,file):
        
        # Check if file_content is not None
        if file is None:
            raise ValueError("File content cannot be None")
              
        localTime=time.time()
        with self.fs.new_file(_id=localTime,
                                     filename=file.filename,
                                     contentType=file.content_type,
                                     tenet = "fairness",
                                     ) as f:
            file.file.seek(0) # Go back to the start of the file
            shutil.copyfileobj(file.file, f)
        return f._id 
    

    def read_file(self,unique_id: str,container_name=None):
        if self.db_type == 'mongo':

            # try:
                # Find the file in the database
            log.info(unique_id)
            # file_metadata = FileStoreReportDb().fs.find_one({"_id": unique_id, "contentType": file_type})
            file_metadata = self.fs.find_one({"_id": unique_id})
            # Check if the file was found
            if file_metadata is None:
                log.info("inside file not found")
                raise HTTPException(status_code=500, detail=f"No file found with unique ID {unique_id}")
            # Get the file from the database
            file_content = self.fs.get(file_metadata._id).read()
            if file_metadata.content_type=="application/pdf":
                file_name=f"file_{str(unique_id)}.pdf"
                extenion="pdf"    
                return {"data": file_content, "name":file_name, "extension": extenion,"contentType":file_metadata.content_type} 
            
            return {"data": file_content, "name":file_metadata.filename, "extension": file_metadata.filename.split('.')[-1],"contentType":file_metadata.content_type}
        else:
            if active_file_storage == "azureopenai":
                download_file_api = os.getenv('AZURE_GET_API')
            elif active_file_storage == "gemini-2.5-flash" or active_file_storage == "gemini-2.5-pro":
                download_file_api = os.getenv('GCP_GET_API')
            elif active_file_storage == "aws":
                download_file_api = os.getenv('AWS_GET_API')
            if container_name is None:
                container_name = os.getenv('Dt_containerName')

            # Check if the environment variable is set
            if not download_file_api:
                raise HTTPException(status_code=500, detail=f"Environment variable AZURE_READ_API is not set")

            # Check if container_name and unique_id are not empty
            if not container_name or not unique_id:
                raise ValueError("container_name and unique_id must not be empty")
               
            response = requests.get(url=download_file_api, params={"container_name": container_name, "blob_name": unique_id}, verify=verify)
            if response is None:
                raise HTTPException("occurred: file not found")
            # Check if the request was successful
            if response.status_code != 200:
                raise Exception(f"Request to {download_file_api} failed with status code {response.status_code}")

            return {'data': response.content, 'type': unique_id.split('.')[-1], 'name': unique_id.split('/')[-1],'contentType':response.headers['Content-Type'], 'extension': unique_id.split('.')[-1]}

    def read_chunked_file(self,unique_id: str,container_name=None):
        if self.db_type == 'mongo':
            # file_metadata = FileStoreReportDb().fs.find_one({"_id": unique_id, "contentType": file_type})
            file_metadata = self.fs.find_one({"_id": unique_id})
            # Check if the file was found
            if file_metadata is None:
                raise FileNotFoundError(f"No file found with unique ID {unique_id}")
            
            # Get the file from the database
            file_content = self.fs.get(file_metadata._id).read()
            
            return {"data": file_content, "name":file_metadata.filename, "extension": file_metadata.filename.split('.')[-1],"contentType":file_metadata.content_type}
        else:
            if active_file_storage == "azureopenai":
                download_file_api = os.getenv('AZURE_GET_API')
            elif active_file_storage == "gemini-2.5-flash" or active_file_storage == "gemini-2.5-pro":
                download_file_api = os.getenv('GCP_GET_API')
            elif active_file_storage == "aws":
                download_file_api = os.getenv('AWS_GET_API')
            if container_name is None:
                container_name = os.getenv('Model_CONTAINER_NAME')

            # Check if the environment variable is set
            if not download_file_api:
                raise ValueError("Environment variable AZURE_READ_API is not set")

            # Check if container_name and unique_id are not empty
            if not container_name or not unique_id:
                raise ValueError("container_name and unique_id must not be empty")

            file_bytes=BytesIO()
            content_type=""
            with requests.get(url=download_file_api, params={"container_name": container_name, "blob_name": unique_id}, stream=True, verify=verify) as r:
                r.raise_for_status()
                content_type=r.headers['Content-Type']
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        file_bytes.write(chunk)
            file_bytes.seek(0)
            # if response.status_code != 200:
            #     raise Exception(f"Request to {download_file_api} failed with status code {response.status_code}")

            return {'data': file_bytes.getvalue(), 'type': unique_id.split('.')[-1], 'name': unique_id.split('/')[-1],'contentType':content_type, 'extension': unique_id.split('.')[-1]}

    

    def read_modelfile(self,unique_id: str,container_name=None):
        if self.db_type == 'mongo':

            # Find the file in the database
            log.info(f"{unique_id}")
            # file_metadata = FileStoreReportDb().fs.find_one({"_id": unique_id, "contentType": file_type})
            file_metadata = self.fs.find_one({"_id": unique_id})
            # Check if the file was found
            if file_metadata is None:
                raise FileNotFoundError(f"No file found with unique ID {unique_id}")
            
            # Get the file from the database
            file_content = self.fs.get(file_metadata._id).read()
            
            return {"data": file_content, "name":file_metadata.filename, "extension": file_metadata.filename.split('.')[-1],"contentType":file_metadata.content_type}
        else:
            if active_file_storage == "azureopenai":
                download_file_api = os.getenv('AZURE_GET_API')
            elif active_file_storage == "gemini-2.5-flash" or active_file_storage == "gemini-2.5-pro":
                download_file_api = os.getenv('GCP_GET_API')
            elif active_file_storage == "aws":
                download_file_api = os.getenv('AWS_GET_API')
            container_name = os.getenv('Model_CONTAINER_NAME')

            # Check if the environment variable is set
            if not download_file_api:
                raise ValueError("Environment variable AZURE_READ_API is not set")

            # Check if container_name and unique_id are not empty
            if not container_name or not unique_id:
                raise ValueError("container_name and unique_id must not be empty")
            response = requests.get(url=download_file_api, params={"container_name": container_name, "blob_name": unique_id}, verify=verify)
            # Check if the request was successful
            if response.status_code != 200:
                raise Exception(f"Request to {download_file_api} failed with status code {response.status_code}")

            return {'data': response.content, 'type': unique_id.split('.')[-1], 'name': unique_id.split('/')[-1],'contentType':response.headers['Content-Type'], 'extension': unique_id.split('.')[-1]}

    
    def delete_file(self,unique_id: str, file_type: str):
        
        # Check if unique_id is not None and is a string
        if unique_id is None or not isinstance(unique_id, str):
            raise ValueError("Unique ID must be a non-empty string")
        
        # Check if file_type is not None and is a string
        if file_type is None or not isinstance(file_type, str):
            raise ValueError("File type must be a non-empty string")
        
        try:
            # Find the file in the database
            file_metadata = self.fs.find_one({"uniqueId": unique_id, "type": file_type})
            
            # Check if the file was found
            if file_metadata is None:
                raise FileNotFoundError(f"No file found with unique ID {unique_id} and type {file_type}")
            
            # Delete the file from the database
            FileStoreReportDb.fs.delete(file_metadata._id)
            
            return {"message": "File deleted successfully"}
        except NoFile:
            raise FileNotFoundError(f"No file found with unique ID {unique_id} and type {file_type}")
    

    def save_local_file(self,filePath,fileType):
        
        if os.path.exists(filePath):
            if os.path.getsize(filePath)<=0:
                raise ValueError("File content cannot be None")
        else:
            raise FileNotFoundError("No file found with the name "+filePath.split("/")[-1]+" locally")
        with open(filePath,'rb') as f:
             file_id=self.fs.put(f,filename=filePath.split('/')[-1],content_type=fileType)
        return file_id

    def getfilename(self,unique_id: str):
        try:
            # Find the file in the database
            file_metadata = self.fs.find_one({"_id": unique_id})
            log.info(f"file_metadata {file_metadata}")
            if file_metadata:

                filename = file_metadata.filename
                log.info(f"{filename} filename")
            return filename
        except NoFile:
            raise FileNotFoundError(f"No file found with unique ID {unique_id}")