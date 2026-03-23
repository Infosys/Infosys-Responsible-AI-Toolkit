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

from explain.config.logger import CustomLogger
from pymongo.errors import ConnectionFailure
import pymongo
import sys
import os

from dotenv import load_dotenv
load_dotenv()

log = CustomLogger()

class DB:
    @staticmethod
    def connect():
        try:
            # Check if the environment variables are set
            if not os.getenv("DB_NAME") or (not os.getenv("MONGO_PATH") and not os.getenv("COSMOS_PATH")):
                raise ValueError("Environment variable DB_NAME must be set and at least one of MONGO_PATH or COSMOS_PATH must be set")
            
            db_type = os.getenv('DB_TYPE', 'mongo').lower()

            if db_type == "cosmos":
                myclient = pymongo.MongoClient(os.getenv("COSMOS_PATH")) 
            elif db_type == "mongo":
                myclient = pymongo.MongoClient(os.getenv("MONGO_PATH"))
            else:   
                raise ValueError("Unsupported database type:{db_type}")

            # Check if the connection is successful
            try:
                myclient.admin.command('ismaster')
            except ConnectionFailure:
                if db_type == "cosmos":
                    raise ConnectionError("Could not connect to CosmosDB")
                elif db_type == "mongo":
                    raise ConnectionError("Could not connect to MongoDB")

            # Connect to the database
            mydb = myclient[os.getenv("DB_NAME")]

            return mydb
        except Exception as e:
            log.error(str(e))
            sys.exit()
    