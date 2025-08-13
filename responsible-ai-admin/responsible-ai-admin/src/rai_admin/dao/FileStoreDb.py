"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import shutil
import pymongo
import datetime,time
from rai_admin.dao.DatabaseConnection import DB
from dotenv import load_dotenv
from rai_admin.config.logger import CustomLogger
from gridfs import GridFS
from bson import objectid

load_dotenv()
log = CustomLogger()

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


mydb=DB.connect()


class fileStoreDb:
    # mycol = mydb["ResponseRegistery"]
    fs=GridFS(mydb)
    def findOne(id):
        file=fileStoreDb.fs.find_one({"_id":id})
        if file:
            content=file.read()
            return {"data":content,"type":file.contentType}
        # values=fileStoreDb.mycol.find({"_id":id},{})[0]
        # print(values)
        values=AttributeDict(values)
        return values
    def findall(query):
        value_list=[]
        values=fileStoreDb.mycol.find(query,{})
        for v in values:

            v=AttributeDict(v)
            value_list.append(v)
        return value_list
    
    def create(value):
        #  value=AttributeDict(value)
         fileid:any
         
         with fileStoreDb.fs.new_file(_id=time.time(),filename=value.filename,content_type=value.content_type) as f:
             shutil.copyfileobj(value.file,f)
             fileid=f._id
           
         return fileid
    
    def update(id,value:dict):
      
        newvalues = { "$set": value }
        docProccessData=fileStoreDb.mycol.update_one({"_id":id},newvalues)
        log.debug(str(newvalues)) 
        return docProccessData.acknowledged
    
    def delete(id):
        print(id)
        return fileStoreDb.fs.delete(id)
        # DocProcDtl.mycol.delete_many({})
        # Docpagedtl.mycol.delete_many({})
    
    