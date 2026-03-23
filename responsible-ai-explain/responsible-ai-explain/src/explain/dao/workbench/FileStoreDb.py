'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from explain.config.logger import CustomLogger
from explain.dao.workbench.DatabaseConnection import DB
from gridfs.errors import NoFile, FileExists
from gridfs import GridFS
import requests
import time
import os

from dotenv import load_dotenv
load_dotenv()

log = CustomLogger()

# Create a MongoDB database instance
RAIExplainDB = DB.connect()

class fileStoreDb:
    fs = GridFS(RAIExplainDB)
    db_type = os.getenv('DB_TYPE').lower()
    verify_ssl = os.getenv('VERIFY_SSL', 'false').lower() in ('true', '1', 't', 'yes')
    
    @staticmethod
    def save_file(file, filename, contentType, tenet):
        
        if fileStoreDb.db_type == 'mongo':
            # Check if file_content is not None
            if file is None:
                raise ValueError("File content cannot be None")
            
            # Check if filename, contentType, and tenet are not None
            if filename is None or contentType is None or tenet is None:
                raise ValueError("Filename, contentType, and tenet cannot be None")
            
            localTime=time.time()
            time.sleep(1/1000)
            try:
                with fileStoreDb.fs.new_file(_id=str(localTime), 
                                            filename=filename,
                                            contentType=contentType,
                                            tenet = tenet,
                                            ) as f:
                    f.write(file)
            except FileExists:
                raise FileExistsError(f"A file with the same ID ({localTime}) already exists")
            except Exception as e:
                raise IOError(f"An error occurred while writing the file: {str(e)}")
    
            return f._id
        else:
            if file is None:
                raise ValueError("File content cannot be None")
            
            # Check if filename, contentType, and tenet are not None
            if filename is None or contentType is None or tenet is None:
                raise ValueError("Filename, contentType, and tenet cannot be None")
            try:
                container_name = os.getenv('HTML_CONTAINER_NAME')
                upload_file_api = os.getenv('AZURE_UPLOAD_API')
                file.seek(0)
                response = requests.post(url = upload_file_api, files = {"file":(filename, file)}, data ={"container_name":container_name}, verify = fileStoreDb.verify_ssl).json()
                blob_name = response["blob_name"]
                
            except Exception as e:
                log.error(f"An error occurred: {e}")
                raise IOError(f"An error occurred while writing the file: {str(e)}")
            
            return blob_name
        
    @staticmethod
    def read_file_exp(unique_id, container_name):
        if fileStoreDb.db_type == 'mongo':
            try:
                # Find the file in the database
                file_metadata = fileStoreDb.fs.find_one({"_id": unique_id})

                # Check if the file was found
                if file_metadata is None:
                    raise FileNotFoundError(f"No file found with unique ID {unique_id}")
                
                # Get the file from the database
                file_content = fileStoreDb.fs.get(file_metadata._id)
                
                return {"data": file_content, "type": file_metadata.filename.split('.')[-1]}
            
            except NoFile:
                raise FileNotFoundError(f"No file found with unique ID {unique_id}")
        else:
            download_file_api = os.getenv('AZURE_GET_API')
            # Check if the environment variable is set
            if not download_file_api:
                raise ValueError("Environment variable AZURE_READ_API is not set")

            # Check if container_name and unique_id are not empty
            if not container_name or not unique_id:
                raise ValueError("container_name and unique_id must not be empty")
            
            try:
                response = requests.get(url=download_file_api, params={"container_name": container_name, "blob_name": unique_id}, verify=fileStoreDb.verify_ssl)
                # Check if the request was successful
                if response.status_code != 200:
                    raise Exception(f"Request to {download_file_api} failed with status code {response.status_code}")

                return {'data': response.content, 'type': unique_id.split('.')[-1]}

            except Exception as e:
                raise FileNotFoundError(f"No file found with unique ID {unique_id}")