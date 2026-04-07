'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''


import shutil
import pymongo
import datetime,time

# from docProcess.dao.DatabaseConnection import DB
from dotenv import load_dotenv
# from docProcess.config.logger import CustomLogger
from src.config.logger import CustomLogger
from src.dao.DatabaseConnection import DB
from gridfs import GridFS
from bson import objectid
from mongomock import gridfs
import concurrent.futures as con
import os

load_dotenv()

telemetry_flg =os.getenv("TELEMETRY_FLAG")

apiEndPoint ='/v1/security/model'
errorRequestMethod = 'GET'


log = CustomLogger()
gridfs.enable_gridfs_integration()
mydb = DB.connect()

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class FileStoreDb:

    # mycol = mydb["ResponseRegistery"]
    fs = GridFS(mydb)


    def findOne(id):

        try:
            file = FileStoreDb.fs.find_one({"_id":id})
            if file:
                content = file.read()
                return {"fileName":file.filename,"data":content,"type":file.content_type}
            values = AttributeDict(values)

            return values
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "findOne", e, apiEndPoint, errorRequestMethod)
    

    def findall(query):

        try:
            value_list = []
            values = FileStoreDb.mycol.find(query,{})
            for v in values:
                v = AttributeDict(v)
                value_list.append(v)

            return value_list
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "findall", e, apiEndPoint, errorRequestMethod)
    

    def create(value,modelName):
    
        try:
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
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "create", e, apiEndPoint, errorRequestMethod)
    
    
    def update(id,value,modelName):

        try:
            FileStoreDb.delete(id)
            fileid:any
            with FileStoreDb.fs.new_file(_id=id,filename=modelName,content_type=value.content_type) as f:
                shutil.copyfileobj(value.file,f)
                fileid = f._id
            #  grid =FileStoreDb.fs.new_file(filename = "xyz.pkl")
            #  grid.write(value.file.read())
            #  grid.close()

            return fileid
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "update", e, apiEndPoint, errorRequestMethod)
    
    
    def delete(payload):

        # FileStoreDb.fs.delete(id)
        # DocProcDtl.mycol.delete_many({})
        # Docpagedtl.mycol.delete_many({})

        # collection_list = mydb.list_collection_names()
        try:
            mydb['fs.files'].delete_many({'_id':payload})
            mydb['fs.chunks'].delete_many({'files_id':payload})

            # print(collection_list)
            # print(mydb['fs.files'])
            # print(mydb['fs.chunks'])
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "delete", e, apiEndPoint, errorRequestMethod)


    
    
