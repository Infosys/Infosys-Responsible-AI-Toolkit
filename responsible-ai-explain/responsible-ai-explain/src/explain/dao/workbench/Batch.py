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
from explain.dao.workbench.DatabaseConnection import DB
from pymongo.errors import InvalidDocument
from dotenv import load_dotenv
load_dotenv()

log = CustomLogger()

# Create a MongoDB database instance
RAIExplainDB = DB.connect()

class Batch:
    
    # Access the "Model" collection in the Common Workbench MongoDB database
    collection = RAIExplainDB["Batch"]
        
    def find(batch_id: float, tenet_id: int):
        # Check if batch_id is not None and is a string
        if batch_id is None or not isinstance(batch_id, float):
            raise ValueError("Batch ID must be a non-empty float")
        
        # Try to find the model by model_id in the database
        try:
            result = Batch.collection.find_one({"BatchId": batch_id, "TenetId": tenet_id}, {"_id": 0, "ModelId": 1, "DataId": 1,"PreprocessorId": 1, "Title": 1})
            if result is None:
                raise ValueError(f"Invalid Batch ID/Tenet ID {batch_id}/{tenet_id}")
        except Exception as e:
            raise 
        
        return result
    
    def find_tenet_id(batch_id: float):
        # Check if batch_id is not None and is a string
        if batch_id is None or not isinstance(batch_id, float):
            raise ValueError("Batch ID must be a non-empty float")
        
        # Try to find the model by model_id in the database
        try:
            TenetId = Batch.collection.find_one({"BatchId": batch_id}, {"_id": 0, "TenetId": 1})['TenetId']
            if TenetId is None:
                raise ValueError(f"Invalid Batch ID {batch_id}")

        except Exception as e:
            raise 
        
        return TenetId
        
    def update(batch_id,value:dict):
        try:
            # Update the document in the collection
            update_result= Batch.collection.update_one({'BatchId': batch_id}, {'$set': value})
            
            # Check if the update was acknowledged
            if not update_result.acknowledged:
                raise RuntimeError(f"Failed to update document with Batch ID {batch_id}")
            
            return update_result.acknowledged
        except InvalidDocument:
            raise ValueError(f"Document is not a valid document with Batch ID {batch_id}")