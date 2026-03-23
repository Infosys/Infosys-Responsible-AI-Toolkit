'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

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


class DataAttributes:

    mycol = mydb["DataAttributes"]


    def get_all(payload):

        dataAttributeNameList = DataAttributes.mycol.distinct(payload)

        return dataAttributeNameList


    def findOne(id):

        values = DataAttributes.mycol.find({"_id":id},{})[0]
        values = AttributeDict(values)

        return values
    

    def findall(query):

        value_list = []
        values = DataAttributes.mycol.find(query,{})
        for v in values:
            v = AttributeDict(v)
            value_list.append(v)
            
        return value_list
    

    def create(values):
         
        value = AttributeDict(values)
        localTime = time.time()
        time.sleep(1/1000)
        mydoc = {
        "_id":localTime,
        "DataAttributeId":localTime,
        "DataAttributeName":value.dataAttributeName,
        "IsActive":"Y",
        "TenetId":value.tenetId,
        "CreatedDateTime": datetime.datetime.now(),
        "LastUpdatedDateTime": datetime.datetime.now(),
        }
        dataAttributesCreatedData = DataAttributes.mycol.insert_one(mydoc)

        return dataAttributesCreatedData.inserted_id
    
    def findDAVId(name,id):
        query = {
            "DataAttributeName": name['DataAttributeName'],
            "TenetId": id['tenetId']
        }
        result = DataAttributes.mycol.find_one(query)
        if result:
            return result["_id"]
        else:
            return None
    
    def update(id,value:dict):
      
        newvalues = { "$set": value }
        dataAttributesUpdatedData = DataAttributes.mycol.update_one({"_id":id},newvalues)
        log.debug(str(newvalues)) 

        return dataAttributesUpdatedData.acknowledged
    

    def delete(query):
        
        DataAttributes.mycol.delete_many(query)