'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

from gridfs import GridFS
import pymongo
import datetime,time
from dotenv import load_dotenv
from app.config.logger import CustomLogger
from app.dao.DatabaseConnection import DB

load_dotenv()
log = CustomLogger()

mydb = DB.connect()

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Batch:

    mycol = mydb["Batch"]
    fs = GridFS(mydb)


    def get_all(payload):

        tenets = Batch.mycol.distinct(payload)

        return tenets


    def findOne(id):

        values = Batch.mycol.find({"BatchId":id},{})[0]
        values = AttributeDict(values)
        print(values)
        return values.Id
    

    def findall(query):

        value_list = []
        values = Batch.mycol.find(query,{})
        for v in values:
            v = AttributeDict(v)
            value_list.append(v)

        return value_list
    

    def create(payloadInDictionary,tenantId):
         
        payloadInDictionary = AttributeDict(payloadInDictionary)
        localTime = time.time()
        
        data = {
            "BatchId":localTime,
            "UserId":payloadInDictionary.userId,
            "Title":payloadInDictionary.title,
            "Status":'Not Started',
            "TenetId":tenantId,
            "ModelId":payloadInDictionary.modelId,
            "DataId":payloadInDictionary.dataId,
            "PreprocessorId":payloadInDictionary.preProcessorId,
            "CreatedDateTime": datetime.datetime.now(),
            "LastUpdatedDateTime": datetime.datetime.now(),
        }
        batchCreatedData = Batch.mycol.insert_one(data)
        result = {
        "BatchId": data["BatchId"],
        "TenetId": data["TenetId"],
        }
        return result
    

    def update(id,value:dict):
      
        newvalues = { "$set": value }
        tenetUpdatedData = Batch.mycol.update_one({"_id":id},newvalues)
        log.debug(str(newvalues)) 

        return tenetUpdatedData.acknowledged
    

    def delete(query):
            Batch.mycol.delete_many(query)


    def findStatus(id):
        values = Batch.mycol.find({"BatchId":id},{})[0]
        values = AttributeDict(values)
        result = values.Status
        print(result)
        return result
    
    def findBatchTable(userName):
        value_list = []
        values = Batch.mycol.find({"UserId":userName},{"_id": 0})
        for value in values:
            value_list.append(value)
        print(value_list, "result")
        return value_list
    
