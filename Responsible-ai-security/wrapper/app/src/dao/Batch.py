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
from src.config.logger import CustomLogger
from src.dao.DatabaseConnection import DB
import concurrent.futures as con
import os

load_dotenv()
log = CustomLogger()

mydb = DB.connect()

telemetry_flg =os.getenv("TELEMETRY_FLAG")

apiEndPoint ='/v1/security/model'
errorRequestMethod = 'GET'

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Batch:

    mycol = mydb["Batch"]
    # fs = GridFS(mydb)


    def get_all(payload):

        try:
            tenets = Batch.mycol.distinct(payload)

            return tenets
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "get_allBatch", e, apiEndPoint, errorRequestMethod)


    def findOne(id):

        try:
            values = Batch.mycol.find({"BatchId":id},{})[0]
            values = AttributeDict(values)
            return values.Id
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "findOneBatch", e, apiEndPoint, errorRequestMethod)

    def findall(query):

        try:
            value_list = []
            values = Batch.mycol.find(query,{})
            for v in values:
                v = AttributeDict(v)
                value_list.append(v)

            return value_list
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "findallBatch", e, apiEndPoint, errorRequestMethod)
    

    def create(payloadInDictionary,tenantId):
         
        try:
            payloadInDictionary = AttributeDict(payloadInDictionary)
            localTime = time.time()
            
            data = {
                "BatchId":localTime,
                "UserId":payloadInDictionary.userId,
                "Status":'Not Started',
                "TenetId":tenantId,
                "ModelId":payloadInDictionary.modelId,
                "DataId":payloadInDictionary.dataId,
                "CreatedDateTime": datetime.datetime.now(),
                "LastUpdatedDateTime": datetime.datetime.now(),
            }
            batchCreatedData = Batch.mycol.insert_one(data)
            result = {
            "BatchId": data["BatchId"],
            "TenetId": data["TenetId"],
            }
            return result
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "createBatch", e, apiEndPoint, errorRequestMethod)
    

    def update(id,value:dict):
      
        try:
            newvalues = { "$set": value }
            tenetUpdatedData = Batch.mycol.update_one({"BatchId":id},newvalues)
            log.debug(str(newvalues)) 

            return tenetUpdatedData.acknowledged
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "updateBatch", e, apiEndPoint, errorRequestMethod)

    def delete(query):
        try:
            Batch.mycol.delete_many(query)
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "deleteBatch", e, apiEndPoint, errorRequestMethod)


    def findStatus(id):
        
        try:
            values = Batch.mycol.find({"BatchId":id},{})[0]
            values = AttributeDict(values)
            result = values.Status
            return result
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "findStatusBatch", e, apiEndPoint, errorRequestMethod)