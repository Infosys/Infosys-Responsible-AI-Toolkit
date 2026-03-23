"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import pymongo
import datetime,time
from rai_backend.dao.DatabaseConnection import DB
from dotenv import load_dotenv
from rai_backend.config.logger import CustomLogger

load_dotenv()
log = CustomLogger()

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


mydb=DB.connect()



class TelemetryFlag:
    mycol = mydb["TelemetryFlag"]
    def findOne(id):
        values=TelemetryFlag.mycol.find({"_id":id},{})[0]
        # print(values)
        values=AttributeDict(values)
        return values
    def findall(query):
        value_list=[]
        values=TelemetryFlag.mycol.find(query,{})
        for v in values:
            v=AttributeDict(v)
            value_list.append(v)
        return value_list
    def create(value):
         value=AttributeDict(value)
         user=TelemetryFlag.mycol.find_one({'Module':value.Module})
         if(user):
             return "failed"
         else:  
            localTime = time.time()
            mydoc = {
            "_id":localTime,
            "Module":value.Module,
            "TelemetryFlag":value.TelemetryFlag,
            "CreatedDateTime": datetime.datetime.now(),
            "LastUpdatedDateTime": datetime.datetime.now(),
            }
            PtrnRecogCreatedData = TelemetryFlag.mycol.insert_one(mydoc)
            return PtrnRecogCreatedData.acknowledged
    
    def update(moduleName,value:dict):    
        log.debug( value) 
        newValues = {"$set": {"TelemetryFlag": value}}
        UpdatedData=TelemetryFlag.mycol.update_one({"Module":moduleName},newValues)
        log.debug(str(newValues)) 
        return UpdatedData.acknowledged
    
    def delete(moduleName):
        TelemetryFlag.mycol.delete_many({"Module":moduleName})
        # DocProcDtl.mycol.delete_many({})
        # Docpagedtl.mycol.delete_many({})
    
    