"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from fairness.config.logger import CustomLogger
from fairness.dao.WorkBench.databaseconnection import DataBase_WB
from dotenv import load_dotenv
from fastapi import HTTPException
load_dotenv()

log = CustomLogger()

# Create a MongoDB database instance
# ModelWorkBenchconnection = DataBase_WB()
# ModelWorkBench=ModelWorkBenchconnection.db

class Tenet:
    
    # Access the "Model" collection in the Common Workbench MongoDB database
    def __init__(self,db=None) -> None:
        if db is not None:
            log.info("inside Tenet loop")
            self.ModelWorkBench= db
        else:

            ModelWorkBenchconnection = DataBase_WB()
            self.ModelWorkBench=ModelWorkBenchconnection.db
    
    # Access the "Model" collection in the Common Workbench MongoDB database
        self.collection = self.ModelWorkBench["Tenet"]
        
    def find(self,tenet_name: str):
        # Check if tenet_name is not None and is a string
        if tenet_name is None or not isinstance(tenet_name, str):
            raise HTTPException(status_code=500, detail="Tenet Name must be a non-empty string")
        
        # Try to find the model by model_id in the database
        result = self.collection.find_one({"TenetName": tenet_name}, {"_id": 0, "Id": 1})['Id']
        if result is None:
            raise HTTPException(status_code=500, detail="Tenet Name not found")
        
        return result