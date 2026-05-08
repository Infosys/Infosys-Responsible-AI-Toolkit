'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024-2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''


import os
import pymongo
from mongomock import MongoClient
from dotenv import load_dotenv
from src.config.logger import CustomLogger
import concurrent.futures as con
import sys
load_dotenv()

telemetry_flg =os.getenv("TELEMETRY_FLAG")

apiEndPoint ='/v1/security/model'
errorRequestMethod = 'GET'

log = CustomLogger()


class DB:
    
     def connect():
        try:
            db_type =os.getenv("DB_TYPE", "mongo").lower()

            db_name = os.getenv("DB_NAME")
            if db_name == os.getenv("TEST_DB"):
                myclient = MongoClient('') 
                mydb = myclient[db_name]
                return mydb
            
            else:
                if db_type == "cosmos":
                    myclient = pymongo.MongoClient(os.getenv("COSMOS_PATH"))
                    mydb = myclient[os.getenv("DB_NAME")]
                    return mydb
                elif db_type == "mongo":  
                    myclient = pymongo.MongoClient(os.getenv("MONGO_PATH")) 
                    mydb = myclient[os.getenv("DB_NAME")]
                    return mydb
                else:
                    raise ValueError(f"Unsupported database type: {db_type}")
        except Exception as e:
            log.info(str(e))
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "connectDB", e, apiEndPoint, errorRequestMethod)
            sys.exit()
            