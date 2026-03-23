'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import pymongo
from datetime import datetime
import time
from dotenv import load_dotenv
from questionnaire.config.logger import CustomLogger
from questionnaire.dao.DatabaseConnection import DB
load_dotenv()
log = CustomLogger()

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


mydb=DB.connect()

class TelemetryUrlStore:
    mycol = mydb["DashboardLinkStore"]
    def findOne(tenant):
        result=TelemetryUrlStore.mycol.find_one({'tenant': tenant}, {'telemetryLink': 1})
        if result:
            return result['telemetryLink']
        else:
            return None
        
    def findall(query):
        value_list=[]
        values=TelemetryUrlStore.mycol.find(query,{})
        for v in values:
            v=AttributeDict(v)
            value_list.append(v)
        return value_list
    def create(value):
        localTime = time.time()
        mydoc = {
                    "_id":localTime,
                    "tenant":value.tenant,
                    "telemetryLink":value.telemetryLink,                  
                    }
        Created = TelemetryUrlStore.mycol.insert_one(mydoc)
        return Created.acknowledged

