"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pymongo
import datetime,time
from rai_admin.dao.DatabaseConnection import DB
from dotenv import load_dotenv
from rai_admin.config.logger import CustomLogger

load_dotenv()
log = CustomLogger()

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


mydb=DB.connect()


class ModerationChecksDb:
    mycol = mydb["ModerationChecks"]
    def findOne(id):
        values=ModerationChecksDb.mycol.find({"_id":id},{})[0]
        # print(values)
        values=AttributeDict(values)
        return values
    def findall(query):
        value_list=[]
        values=ModerationChecksDb.mycol.find(query,{})
        for v in values:

            v=AttributeDict(v)
            value_list.append(v)
        return value_list
    def create(value):
         value=AttributeDict(value)
         counter_doc = ModerationChecksDb.mycol.find_one_and_update(
        {"_id": "counter"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
        )
        #  
         unique_id = counter_doc["seq"]
         mydoc = {
        "_id":unique_id,
        "name":value.Name,       
         }
         PtrnRecogCreatedData = ModerationChecksDb.mycol.insert_one(mydoc)
         return PtrnRecogCreatedData.acknowledged
    
    def update(id,value:dict):
      
        newvalues = { "$set": value }
        PtrnRecogUpdatedData=ModerationChecksDb.mycol.update_one({"_id":id},newvalues)
        log.debug(str(newvalues)) 
        return PtrnRecogUpdatedData.acknowledged
    
    def delete(id):
        ModerationChecksDb.mycol.delete_many({"_id":id})
        # DocProcDtl.mycol.delete_many({})
        # Docpagedtl.mycol.delete_many({})

class OutputModerationChecksDb:
    mycol = mydb["OutputModerationChecks"]
    def findOne(id):
        values=OutputModerationChecksDb.mycol.find({"_id":id},{})[0]
        # print(values)
        values=AttributeDict(values)
        return values
    def findall(query):
        value_list=[]
        values=OutputModerationChecksDb.mycol.find(query,{})
        for v in values:

            v=AttributeDict(v)
            value_list.append(v)
        return value_list
    def create(value):
         value=AttributeDict(value)
         counter_doc = OutputModerationChecksDb.mycol.find_one_and_update(
        {"_id": "counter"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
        )
         unique_id = counter_doc["seq"]
         mydoc = {
        "_id":unique_id,
        "name":value.Name,       
         }
         PtrnRecogCreatedData = OutputModerationChecksDb.mycol.insert_one(mydoc)
         return PtrnRecogCreatedData.acknowledged
    
    def update(id,value:dict):    
        newvalues = { "$set": value }
        PtrnRecogUpdatedData=OutputModerationChecksDb.mycol.update_one({"_id":id},newvalues)
        log.debug(str(newvalues)) 
        return PtrnRecogUpdatedData.acknowledged
    
    def delete(id):
        OutputModerationChecksDb.mycol.delete_many({"_id":id})
    

    
    