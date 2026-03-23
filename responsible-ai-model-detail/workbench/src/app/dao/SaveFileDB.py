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
from app.config.logger import CustomLogger
from app.dao.DatabaseConnection import DB
from gridfs import GridFS
from bson import objectid

load_dotenv()
log = CustomLogger()

mydb = DB.connect()

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class FileStoreDb:

    fs = GridFS(mydb)


    def findOne(id):

        file = FileStoreDb.fs.find_one({"_id":id})
        if file:
            content = file.read()
            return {"fileName":file.filename,"data":content,"type":file.content_type}
        values = AttributeDict(values)

        return values
    

    def create(value, modelName):
        localTime = str(time.time())
        time.sleep(1/1000)
        fileid = None
        with FileStoreDb.fs.new_file(_id=localTime, filename=modelName, content_type=value.content_type) as f:
            value.file.seek(0)  # Reset the file pointer to the beginning of the file
            shutil.copyfileobj(value.file, f)
            fileid = f._id
        return fileid
    
    
    def update(id,value,modelName):

        FileStoreDb.delete(id)
        fileid:any
        with FileStoreDb.fs.new_file(_id=id,filename=modelName,content_type=value.content_type) as f:
            shutil.copyfileobj(value.file,f)
            fileid = f._id

        return fileid
    
    
    def delete(payload):

        mydb['fs.files'].delete_many({'_id':payload})
        mydb['fs.chunks'].delete_many({'files_id':payload})



    
    
