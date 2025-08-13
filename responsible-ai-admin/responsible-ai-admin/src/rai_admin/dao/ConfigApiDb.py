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


# class ConfigApiDb:
#     mycol = mydb["ApiConfig"]
#     def findOne(id):
#         values=ConfigApiDb.mycol.find({"_id":id},{})[0]
#         # print(values)
#         values=AttributeDict(values)
#         return values
#     def findall(query):
#         value_list=[]
#         values=ConfigApiDb.mycol.find(query,{})
#         for v in values:

#             v=AttributeDict(v)
#             value_list.append(v)
#         return value_list
#     def create(value):
#          value=AttributeDict(value)
#          localTime = time.time()
#          mydoc = {
#         "_id":localTime,
#         "ApiName":value.Name,
#         "ApiIp":value.Ip,
#         "ApiPort":value.port,
#         "CreatedDateTime": datetime.datetime.now(),
#         "LastUpdatedDateTime": datetime.datetime.now(),
#          }
#          PtrnRecogCreatedData = ConfigApiDb.mycol.insert_one(mydoc)
#          return PtrnRecogCreatedData.inserted_id
    
#     def update(id,value:dict):
      
#         newvalues = { "$set": value }
#         PtrnRecogUpdatedData=ConfigApiDb.mycol.update_one({"_id":id},newvalues)
#         log.debug(str(newvalues)) 
#         return PtrnRecogUpdatedData.acknowledged
    
#     def delete(id):
#         #ConfigApiDb.mycol.delete_many({"_id":id})
#         ConfigApiDb.mycol.delete_one({"_id":id})
#         # DocProcDtl.mycol.delete_many({})
#         # Docpagedtl.mycol.delete_many({})


class ConfigApiDb:
    mycol = mydb["ApiConfig"]

    def findOne(id):
        print(f"Finding document with id: {id}")
        values=ConfigApiDb.mycol.find({"_id":id},{})[0]
        print(f"Found document: {values}")
        values=AttributeDict(values)
        return values

    def findall(query):
        print(f"Finding all documents with query: {query}")
        value_list=[]
        values=ConfigApiDb.mycol.find(query,{})
        for v in values:
            v=AttributeDict(v)
            value_list.append(v)
        print(f"Found documents: {value_list}")
        return value_list

    def create(value):
        print(f"Creating document with value: {value}")
        value=AttributeDict(value)
        localTime = time.time()
        mydoc = {
            "_id":localTime,
            "ApiName":value.Name,
            "ApiIp":value.Ip,
            "ApiPort":value.port,
            "CreatedDateTime": datetime.datetime.now(),
            "LastUpdatedDateTime": datetime.datetime.now(),
        }
        print(f"Inserting document: {mydoc}")
        PtrnRecogCreatedData = ConfigApiDb.mycol.insert_one(mydoc)
        print(f"Inserted document with id: {PtrnRecogCreatedData.inserted_id}")
        return PtrnRecogCreatedData.inserted_id

    def update(id,value:dict):
        print(f"Updating document with id: {id} and value: {value}")
        newvalues = { "$set": value }
        PtrnRecogUpdatedData=ConfigApiDb.mycol.update_one({"_id":id},newvalues)
        print(f"Update result: {PtrnRecogUpdatedData.acknowledged}")
        return PtrnRecogUpdatedData.acknowledged

    def delete(id):
        print(f"Deleting document with id: {id}")
        result = ConfigApiDb.mycol.delete_one({"_id": float(id)})
        if result.deleted_count == 0:
            print(f"No documents were deleted.")
            return False
        else:
            print(f"Deleted document with id: {id}")
            return True
    