'''
MIT license https://opensource.org/licenses/MIT Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
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


class Tenet:

    mycol = mydb["Tenet"]
    fs = GridFS(mydb)


    def get_all(payload):

        tenets = Tenet.mycol.distinct(payload)

        return tenets


    def findOne(name):
        name = name.capitalize()
        values = Tenet.mycol.find({"TenetName":name},{})[0]
        values = AttributeDict(values)

        return values.Id
    

    def findall(query):

        value_list = []
        values = Tenet.mycol.find(query,{})
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
        "Id":value.tenetid,
        "TenetName":value.tenetname,
        "ProjectName":value.projectname,
        "CreatedDateTime": datetime.datetime.now(),
        "LastUpdatedDateTime": datetime.datetime.now(),
        }
        tenetCreatedData = Tenet.mycol.insert_one(mydoc)

        return tenetCreatedData.inserted_id
    

    def update(id,value:dict):
      
        newvalues = { "$set": value }
        tenetUpdatedData = Tenet.mycol.update_one({"_id":id},newvalues)
        log.debug(str(newvalues)) 

        return tenetUpdatedData.acknowledged
    

    def delete(query):
            Tenet.mycol.delete_many(query)
