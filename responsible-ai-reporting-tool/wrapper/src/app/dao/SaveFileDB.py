'''
MIT license https://opensource.org/licenses/MIT Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''


import shutil
import pymongo
import datetime,time

# from docProcess.dao.DatabaseConnection import DB
from dotenv import load_dotenv
# from docProcess.config.logger import CustomLogger
from app.config.logger import CustomLogger
from app.dao.DatabaseConnection import DB
from gridfs.errors import NoFile, FileExists
from gridfs import GridFS
from bson import objectid
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

    # mycol = mydb["ResponseRegistery"]
    fs = GridFS(mydb)
    db_type = os.getenv('DB_TYPE').lower()
    verify_ssl = os.getenv('sslVerify', 'false').lower() in ('true', '1', 't', 'yes')
    
    @staticmethod
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
            download_file_api = os.getenv('AZURE_GET_API')
            # Check if the environment variable is set
            if not download_file_api:
                raise ValueError("Environment variable AZURE_GET_API is not set")

            # Check if container_name and unique_id are not empty
            if not container_name or not unique_id:
                raise ValueError("container_name and unique_id must not be empty")
            try:
                response = requests.get(url=download_file_api, params={"container_name": container_name, "blob_name": unique_id}, verify=FileStoreDb.verify_ssl)
                # Check if the request was successful
                if response.status_code != 200:
                    raise Exception(f"Request to {download_file_api} failed with status code {response.status_code}")

                return {'data': response.content}

            except Exception as e:
                # Handle any exceptions that requests.post might raise
                raise 

    @staticmethod
    def save_file(file, tenet_id, content_type):
        if FileStoreDb.db_type == 'mongo':
            # Check if file_content is not None
            if file is None:
                raise ValueError("File content cannot be None")
            
            # Check if TenetId is None
            if tenet_id is None:
                raise ValueError("TenetId cannot be None")
            
            localTime=time.time()
            time.sleep(1/1000)
            try:
                with FileStoreDb.fs.new_file(_id=str(localTime), 
                                                tenet_id = tenet_id,
                                                content_type=content_type
                                            ) as f:
                    f.write(file)
            except FileExists:
                raise FileExistsError(f"A file with the same ID ({localTime}) already exists")
            except Exception as e:
                raise IOError(f"An error occurred while writing the file: {str(e)}")

            return f._id
        else:
            # Check if file_content is not None
            if file is None:
                raise ValueError("File content cannot be None")
            
            # Check if filename, contentType, and tenet are not None
            if tenet_id is None or content_type is None:
                raise ValueError("contentType, and tenet cannot be None")
            
            try:
                container_name = os.getenv('PDF_CONTAINER_NAME')
                upload_file_api = os.getenv('AZURE_UPLOAD_API')
                filename = "exp_pdf_file" 
                response =requests.post(url =upload_file_api, files ={"file":(filename, file)}, data ={"container_name":container_name}, verify=FileStoreDb.verify_ssl).json()
                blob_name =response["blob_name"]
            except Exception as e:
                raise IOError(f"An error occurred while writing the file: {str(e)}")
            
            return blob_name

    def findOne(id):

        file = FileStoreDb.fs.find_one({"_id":id})
        if file:
            content = file.read()
            return {"fileName":file.filename,"data":content,"type":file.content_type}
        values = AttributeDict(values)

        return values
    

    def findall(query):

        value_list = []
        values = FileStoreDb.mycol.find(query,{})
        for v in values:
            v = AttributeDict(v)
            value_list.append(v)

        return value_list
    

    def create(value, modelName):

        localTime = time.time()
        time.sleep(1/1000)
        fileid:any
        with FileStoreDb.fs.new_file(_id=localTime,filename=modelName, content_type=value.content_type) as f:
            shutil.copyfileobj(value.file,f)
            fileid = f._id
        #  grid =FileStoreDb.fs.new_file(filename = "xyz.pkl")
        #  grid.write(value.file.read())
        #  grid.close()

        return fileid
    
    
    def update(id,value,modelName):

        FileStoreDb.delete(id)
        fileid:any
        with FileStoreDb.fs.new_file(_id=id,filename=modelName,content_type=value.content_type) as f:
            shutil.copyfileobj(value.file,f)
            fileid = f._id
        #  grid =FileStoreDb.fs.new_file(filename = "xyz.pkl")
        #  grid.write(value.file.read())
        #  grid.close()

        return fileid
    
    
    def delete(payload):

        # FileStoreDb.fs.delete(id)
        # DocProcDtl.mycol.delete_many({})
        # Docpagedtl.mycol.delete_many({})

        # collection_list = mydb.list_collection_names()

        mydb['fs.files'].delete_many({'_id':payload})
        mydb['fs.chunks'].delete_many({'files_id':payload})

        # print(collection_list)
        # print(mydb['fs.files'])
        # print(mydb['fs.chunks'])


    
    
