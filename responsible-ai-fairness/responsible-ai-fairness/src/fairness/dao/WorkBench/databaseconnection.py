"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

class DataBase_WB:
     def __init__(self):
        self.db_type = os.getenv('DB_TYPE').lower()
        if self.db_type =="cosmos":
            cosmos_path = os.getenv('COSMOS_PATH')
            db_name = os.getenv("DB_NAME_WB")
            if cosmos_path is None or db_name is None:
                raise Exception("Environment variables COSMOS_PATH or DB_NAME are not set")
            self.client = MongoClient(cosmos_path)
            self.db = self.client[db_name]
        elif self.db_type =="mongo":
            mongo_path = os.getenv('MONGO_PATH')
            db_name = os.getenv("DB_NAME_WB")
            if mongo_path is None or db_name is None:
                raise Exception("Environment variables MONGO_PATH or DB_NAME are not set")
            self.client = MongoClient(mongo_path)
            self.db = self.client[db_name]
        else:
            raise Exception("Invalid DB_TYPE. Expected 'cosmos' or 'mongo'")