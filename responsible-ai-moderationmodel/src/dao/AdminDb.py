'''
Copyright 2024 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import os
import pymongo

from dotenv import load_dotenv
import sys
load_dotenv()
import json
import requests
import urllib.parse

import requests
import json
import traceback
import os

import logging

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


myclient = pymongo.MongoClient(os.getenv("MONGO_PATH"))
print(myclient)
# dbname = os.getenv("APP_MONGO_DBNAME")
dbname = os.getenv("DB_NAME")

class DB:
    def connect():
        try:
            # myclient = pymongo.MongoClient(os.getenv("MONGO_PATH")) 
            # mydb = myclient[os.getenv("DB_NAME")]
            mydb = myclient[dbname]
            
            return mydb
        except Exception as e:
            logging.error("error in DB connection")
            logging.error(str(e))
            sys.exit()

mydb=DB.connect()


class Results:
    mycol = mydb["moderationtelemetrydata"]
    logdb=mydb["Logdb"]
    # mycol = mydb["Results"]
    mycol2 = mydb["Results"]
    # mycol2 = mydb["Resultswithfeedback"]


    def createlog(value):
        
        try:
            print(value)
            PtrnRecogCreatedData = Results.logdb.insert_one(value)
            print("PtrnRecogCreatedData.acknowledged",PtrnRecogCreatedData.acknowledged)
            return PtrnRecogCreatedData.acknowledged
        except Exception as e:
            logging.error("Error occured in Results create")
            logging.error(f"Exception: {e}")
    
    
    
            