'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from explain.dao.explainability.DatabaseConnection import DB
from explain.config.logger import CustomLogger
import time
from dotenv import load_dotenv
load_dotenv()

log = CustomLogger()

RAIExplainDB = DB.connect()

class Tbl_Telemetry:
    collection = RAIExplainDB["Explainability_Telemetry"]
    
    def findOne(query):
        value_list=[]
        values=Tbl_Telemetry.collection.find(query,{})
        for v in values:
            value_list.append(v)
        return value_list
    
    def create(value):
        log.debug("Create telemetry data")
        localTime = time.time()
        mydoc = {
            "_id":localTime,
            "uniqueid":value['uniqueid'],
            "tenant":value['tenant'],
            "apiname":value['apiname'],
            "user":value['user'],
            "lotNumber": value['lotNumber'],
            "date": value['date'],
            "request":value['request'],
            "response":value['response'],
        }
        result = Tbl_Telemetry.collection.insert_one(mydoc)
        return result.inserted_id

    
    
    