'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024-2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''


import pymongo
import datetime,time
# from batch_processing.dao.DatabaseConnection import DB
# from batch_processing.dao.DocPageDtl import *
# from batch_processing.dao.DocProcDtlDb import DocProcDtl
from dotenv import load_dotenv
# from batch_processing.config.logger import CustomLogger
from src.config.logger import CustomLogger
from src.dao.DatabaseConnection import DB
import concurrent.futures as con
import os

load_dotenv()

telemetry_flg =os.getenv("TELEMETRY_FLAG")

apiEndPoint ='/v1/security/model'
errorRequestMethod = 'GET'





log = CustomLogger()

mydb = DB.connect()

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class ErrDtl:

    mycol = mydb["ErrDtl"]


    def findOne(id):

        try:
            values=ErrDtl.mycol.find({"_id":id},{})[0]
            values=AttributeDict(values)
            return values
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "findOneErrDtl", e, apiEndPoint, errorRequestMethod)
    

    def findall(query):

        try:
            value_list=[]
            values=ErrDtl.mycol.find(query,{})
            for v in values:
                v=AttributeDict(v)
                value_list.append(v)

            return value_list
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "findallErrDtl", e, apiEndPoint, errorRequestMethod)
    

    def create():
        
        try:
            localTime = time.time()
            time.sleep(1/1000)
            mydoc = {
                "_id":localTime,
                "id":localTime,
                "ErrId":localTime,
                "ErrMsg":"",
                "ErrDesc":"",
                "ErrDateTime":datetime.datetime.now(),
            }
            SecErrDtlCreatedData = ErrDtl.mycol.insert_one(mydoc)

            return SecErrDtlCreatedData.inserted_id
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "createErrDtl", e, apiEndPoint, errorRequestMethod)
    
    
    def update(id,value:dict):
        
        try:
            newvalues = { "$set": value }
            SecErrDtlUpdatedData=ErrDtl.mycol.update_one({"_id":id},newvalues)
            log.debug(str(newvalues)) 

            return SecErrDtlUpdatedData.acknowledged
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "updateErrDtl", e, apiEndPoint, errorRequestMethod)
    
    
    def delete():
        
        try:
            ErrDtl.mycol.delete_many({})
            # DocProcDtl.mycol.delete_many({})
            # Docpagedtl.mycol.delete_many({})
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "deleteErrDtl", e, apiEndPoint, errorRequestMethod)