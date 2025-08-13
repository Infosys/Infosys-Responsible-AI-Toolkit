"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from fairness.config.logger import CustomLogger
from fairness.dao.WorkBench.databaseconnection import DataBase_WB
from fairness.Telemetry.Telemetry_call import SERVICE_UPLOAD_FILE_METADATA
from fastapi import HTTPException

from dotenv import load_dotenv
load_dotenv()

log = CustomLogger()

# Create a MongoDB database instance

class Batch:
    def __init__(self,db=None) -> None:
        if db is not None:
            log.info("inside batch loop")
            self.ModelWorkBench= db
        else:
            ModelWorkBenchconnection = DataBase_WB()
            self.ModelWorkBench=ModelWorkBenchconnection.db
    
    # Access the "Model" collection in the Common Workbench MongoDB database
    # ModelWorkBenchconnection = DataBase_WB()
    # ModelWorkBench=ModelWorkBenchconnection.db

        self.collection = self.ModelWorkBench["Batch"]
    
    # # Access the "Model" collection in the Common Workbench MongoDB database
    # collection = ModelWorkBench["Batch"]
        
    def find(self,batch_id: float, tenet_id: int):
        # Check if batch_id is not None and is a string
        
        if batch_id is None or not isinstance(batch_id, float):
            raise 
        
        # Try to find the model by model_id in the database
        result = self.collection.find_one({"BatchId": batch_id, "TenetId": tenet_id}, {"_id": 0,"DataId": 1, "ModelId":1})
        if result is None:
            raise HTTPException(status_code=500, detail="Batch ID not found")
        return result

    def update(self,batch_id, value:dict):
            #update the document with the given collection
            update_result = self.collection.update_one({"BatchId": batch_id}, {"$set": value})

            # check if the update was acknowledged
            if not update_result.acknowledged:
                raise HTTPException(status_code=500, detail="Batch ID not found")
            return update_result.acknowledged