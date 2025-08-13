'''
MIT license https://opensource.org/licenses/MIT Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import pymongo
import datetime,time
from dotenv import load_dotenv
from app.config.logger import CustomLogger
from app.dao.DatabaseConnection import DB
from gridfs import GridFS
import shutil
import os
import requests

load_dotenv()
log = CustomLogger()

mydb = DB.connect()

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class FileStoreDb:

    fs = GridFS(mydb)
    db_type = os.getenv('DB_TYPE').lower()
    

    def read_file(unique_id, container_name):
        if FileStoreDb.db_type == 'mongo':
            try:
                # Find the file in the database
                file_metadata = FileStoreDb.fs.find_one({"_id": unique_id})
                
                # Check if the file was found
                if file_metadata is None:
                    raise FileNotFoundError(f"No file found with unique ID {unique_id}")
                
                # Get the file from the database
                file_content = file_metadata.read()
                
                return {"data": file_content}
            except NoFile:
                raise FileNotFoundError(f"No file found with unique ID {unique_id}")
        else:
            # download_file_api = 'https://rai-toolkit-dev.az.ad.idemo-ppc.com/api/v1/azureBlob/getBlob'
            download_file_api = os.getenv('AZURE_GET_API')
            # Check if the environment variable is set
            if not download_file_api:
                raise ValueError("Environment variable AZURE_GET_API is not set")

            # Check if container_name and unique_id are not empty
            if not container_name or not unique_id:
                raise ValueError("container_name and unique_id must not be empty")
            try:
                response = requests.get(url=download_file_api, params={"container_name": container_name, "blob_name": unique_id},verify=False)
                # Check if the request was successful
                if response.status_code != 200:
                    raise Exception(f"Request to {download_file_api} failed with status code {response.status_code}")

                return {'data': response.content}

            except Exception as e:
                # Handle any exceptions that requests.post might raise
                raise 


    def findOne(id):

        file = FileStoreDb.fs.find_one({"_id":id})
        if file:
            content = file.read()
            return {"fileName":file.filename,"data":content,"type":file.content_type}
        values = AttributeDict(values)

        return values
    

    def create(value):

        localTime = str(time.time())
        time.sleep(1/1000)
        fileid = None
        with FileStoreDb.fs.new_file(_id=localTime, filename=value.filename, content_type=value.content_type) as f:
            value.file.seek(0)  # Reset the file pointer to the beginning of the file
            shutil.copyfileobj(value.file, f)
            fileid = f._id
        return fileid
    
    
    def update(id,value):

        FileStoreDb.delete(id)
        fileid:any
        with FileStoreDb.fs.new_file(_id=id,filename=value.filename,content_type=value.content_type) as f:
            shutil.copyfileobj(value.file,f)
            fileid = f._id

        return fileid
    
    
    def delete(payload):

        mydb['fs.files'].delete_many({'_id':payload})
        mydb['fs.chunks'].delete_many({'files_id':payload})
