"""
SPDX-License-Identifier: MIT

Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


import os
import pymongo

from dotenv import load_dotenv
from RAG.config.logger import CustomLogger,request_id_var
import sys
load_dotenv()
import json
import requests
#import hvac
import urllib.parse
import requests
import json
import gridfs
#from azure.identity import ClientSecretCredential
#from azure.keyvault.secrets import SecretClient
import traceback
# import psycopg2
import os



log = CustomLogger()

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

# myclient = pymongo.MongoClient(os.getenv("MONGO_PATH"))
# print(myclient)
# dbname = os.getenv("APP_MONGO_DBNAME")
# conn = pymongo.MongoClient(os.environ.get("MONGO_PATH"))
global fs,defaultfs
request_id_var.set("Startup")
class DB:
    def connect():
        try:
            db_flag=os.getenv("DB_TYPE")
            print("dbflag",db_flag)
            if os.getenv("DB_TYPE")=="cosmos":
                log.info("cosmos connection")
                print(db_flag)
                myclient = pymongo.MongoClient(os.getenv("COSMOS_PATH")) 
                # cosmos_client = CosmosClient(os.getenv("COSMOS_PATH"))
                log.info("cosmos connection")
            else:
                myclient = pymongo.MongoClient(os.getenv("MONGO_PATH"))
            # mydb = myclient[os.getenv("DB_NAME")]
            mydb = myclient[os.getenv("DB_NAME")]
            global fs,defaultfs
            fs=gridfs.GridFS(mydb)
            defaultfs=gridfs.GridFS(myclient[os.environ.get("DEFAULT_DB_NAME")])
            # db = conn[os.environ.get("DB_NAME")]
            
            # mydb = myclient[dbname]
            
            return mydb
        except Exception as e:
            log.error("error in DB connection")
            log.error(str(e))
            log.error(str(traceback.extract_tb(e.__traceback__)[0].lineno))
            sys.exit()

mydb=DB.connect()
collection = mydb[os.getenv("COLLECTIONNAME")]
class ProfaneWords:
    mycol = mydb["ProfaneWords"]
    def findOne(id):
        try:
            values=ProfaneWords.mycol.find({"_id":id},{})[0]
            # print(values)
            values=AttributeDict(values)
            return values
        except Exception as e:
            log.error("Error occured in ProfaneWords")
            log.error(f"Exception: {e}")
    
class feedbackdb:
    feedback_collection = mydb["feedback"]
    def create(value):
        try:
            PtrnRecogCreatedData = feedbackdb.feedback_collection.insert_one(value)
            print("PtrnRecogCreatedData.acknowledged",PtrnRecogCreatedData.acknowledged)
            return PtrnRecogCreatedData.acknowledged
        except Exception as e:
            log.error("Error occured in feedbackdb")
            log.error(f"Exception: {e}")

class Results:
    mycol = mydb["moderationtelemetrydata"]
    logdb=mydb["Logdb"]
    # mycol = mydb["Results"]
    mycol2 = mydb["Results"]
    # mycol2 = mydb["Resultswithfeedback"]
    def findOne(id):
        try:
            values=Results.mycol.find({"_id":id},{})[0]
            # print(values)
            values=AttributeDict(values)
            return values
        except Exception as e:
            log.error("Error occured in Results findOne")
            log.error(f"Exception: {e}")
    def findall(query):
        try:
            value_list=[]
            values=Results.mycol.find(query,{})
            for v in values:

                v=AttributeDict(v)
                value_list.append(v)
            return value_list
        except Exception as e:
            log.error("Error occured in Results findall")
            log.error(f"Exception: {e}")

    def create(value,id,portfolio, accountname):
        request_id_var.set(id)
        try:
            value=json.loads(value.json())
            id=value["uniqueid"]
            print(id)
            mydoc={"_id":id , "created":value["created"],"portfolio":portfolio,"accountname":accountname,
                "Moderations":value["moderationResults"]}
            PtrnRecogCreatedData = Results.mycol.insert_one(mydoc)
            print("PtrnRecogCreatedData.acknowledged",PtrnRecogCreatedData.acknowledged)
            return PtrnRecogCreatedData.acknowledged
        except Exception as e:
            log.error("Error occured in Results create")
            log.error(f"Exception: {e}")

    def createlog(value):
        
        try:
            print(value)
            PtrnRecogCreatedData = Results.logdb.insert_one(value)
            print("PtrnRecogCreatedData.acknowledged",PtrnRecogCreatedData.acknowledged)
            return PtrnRecogCreatedData.acknowledged
        except Exception as e:
            log.error("Error occured in Results create")
            log.error(f"Exception: {e}")
    
    
    def createwithfeedback(value):
        
        try:
            # print(id)
            PtrnRecogCreatedData = Results.mycol2.insert_one(value)
            print("PtrnRecogCreatedData.acknowledged",PtrnRecogCreatedData.acknowledged)
            return PtrnRecogCreatedData.acknowledged
        except Exception as e:
            log.error("Error occured in createwithfeedback")
            log.error(f"Exception: {e}")
    
    def update(query,value:dict):
        try:
        
            newvalues = { "$set": value }
            
            PtrnRecogUpdatedData=Results.mycol.update_one(query,newvalues)
            log.debug(str(newvalues)) 
            return PtrnRecogUpdatedData.acknowledged
        except Exception as e:
            log.error("Error occured in Results update")
            log.error(f"Exception: {e}")
    
    def delete(id):
        try:
            return Results.mycol.delete_one({"_id": id})
            return Results.mycol.delete_many({"dataRecogGrpId":id}).acknowledged
            # DocProcDtl.mycol.delete_many({})
            # Docpagedtl.mycol.delete_many({})
        except Exception as e:
            log.error("Error occured in Results delete")
            log.error(f"Exception: {e}")
            
    def deleteMany(query):
        try:
            return Results.mycol.delete_many(query).acknowledged
        except Exception as e:
            log.error("Error occured in Results deleteMany")
            log.error(f"Exception: {e}")
            