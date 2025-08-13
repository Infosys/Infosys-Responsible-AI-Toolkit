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
ModelWorkBenchconnection = DataBase_WB()
ModelWorkBench=ModelWorkBenchconnection.db


class SampleDataset:
    
    # Access the "Model" collection in the Common Workbench MongoDB database
    def __init__(self,db=None) -> None:
        if db is not None:
            log.info("inside sampleDATASET loop")
            self.ModelWorkBench= db
        else:

            ModelWorkBenchconnection = DataBase_WB()
            self.ModelWorkBench=ModelWorkBenchconnection.db
    
    # Access the "Model" collection in the Common Workbench MongoDB database
        self.collection = ModelWorkBench["Dataset"]
        
    def find(self,Sample_Id: float):
        # Check if model_id is not None and is a string
        if Dataset_Id is None or not isinstance(Sample_Id, float):
            raise HTTPException(status_code=500, detail="Data ID must be a non-empty float")
        
        # Try to find the model by model_id in the database
        result = self.collection.find_one({"SampleData": Sample_Id}, {"_id": 0, "DataId": 1, "SampleData": 0})

        if result is None:
            raise HTTPException(status_code=500, detail="Data ID not found")
        return result

class Dataset:
    
    # Access the "Model" collection in the Common Workbench MongoDB database
    def __init__(self,db=None) -> None:
        if db is not None:
            log.info("inside DATASET loop")
            self.ModelWorkBench= db
        else:

            ModelWorkBenchconnection = DataBase_WB()
            self.ModelWorkBench=ModelWorkBenchconnection.db

    
    # Access the "Model" collection in the Common Workbench MongoDB database
        self.collection = self.ModelWorkBench["Dataset"]
        
    def find(self,Dataset_Id: float):
        # Check if model_id is not None and is a string
        if Dataset_Id is None or not isinstance(Dataset_Id, float):
            raise HTTPException(status_code=500, detail="Data ID must be a non-empty float")
        
        # Try to find the model by model_id in the database
        result = self.collection.find_one({"DataId": Dataset_Id}, {"_id": 0, "DataSetName": 1, "SampleData": 1})
        if result is None:
            raise HTTPException(status_code=500, detail="Data ID not found")
        
        return result
    
    def findFile(self,file_Id: float):
        # Check if model_id is not None and is a string
        if file_Id is None or not isinstance(file_Id, float):
            raise HTTPException(status_code=500, detail="Data ID must be a non-empty float")
        
        # Try to find the model by model_id in the database
        log.info(f"file_Id{file_Id}")
        result = self.collection.find_one({"SampleData": file_Id}, {"_id": 0, "DataId": 1})
        if result is None:
            raise HTTPException(status_code=500, detail="Data ID not found")
        
        return result

class DataAttributes:
    
    # Access the "DataAttributes" collection in the Common Workbench MongoDB database
    def __init__(self, db=None) -> None:
        if db is not None:
            log.info("inside dataattributes loop")
            self.ModelWorkBench= db
        else:

            ModelWorkBenchconnection = DataBase_WB()
            self.ModelWorkBench=ModelWorkBenchconnection.db
    
    # Access the "DataAttributes" collection in the Common Workbench MongoDB database
        self.collection = self.ModelWorkBench["DataAttributes"]
        
    def find(self,dataset_attributes: list):
        # Check if dataset_attributes is not None and is a string
        if dataset_attributes is None or not isinstance(dataset_attributes, list):
            raise HTTPException(status_code=500, detail="Dataset attribute(s) names must be a non-empty list")
       
        # Check if dataset_attributes is an empty list
        if not dataset_attributes:
            raise HTTPException(status_code=500, detail="Dataset attribute(s) names must be a non-empty list")
       
        # Try to find the dataset_attributes in the database
            # Query the database for the dataset attributes
        dataset_attribute_ids = list(self.collection.find({"DataAttributeName": {"$in": dataset_attributes}}, {"_id": 0, "DataAttributeId": 1, "DataAttributeName": 1}))

        # Sort dataset_attribute_ids based on the order of dataset_attributes
        dataset_attribute_ids.sort(key=lambda x: dataset_attributes.index(x['DataAttributeName']))
        
        # Get all values of each dictionary in dataset_attribute_ids
        dataset_attribute_ids_values = [list(d.values())[0] for d in dataset_attribute_ids]
           
            # Check if the query returned any results
        if not dataset_attribute_ids:
            raise HTTPException(status_code=500, detail="No dataset attributes found")
       
        return dataset_attribute_ids_values



class DataAttributeValues:
    
    def __init__(self,db=None) -> None:
        if db is not None:
            log.info("inside dataattribute values loop")
            self.ModelWorkBench= db
        else:

            ModelWorkBenchconnection = DataBase_WB()
            self.ModelWorkBench=ModelWorkBenchconnection.db
    
        self.collection = self.ModelWorkBench["DataAttributesValues"]
    
    def find(self,dataset_id: float, dataset_attribute_ids: list, batch_id: float):
        # Check if dataset_id is not None and is a string
        if dataset_id is None or not isinstance(dataset_id, float):
            raise HTTPException(status_code=500, detail="Data ID must be a non-empty float") 
            
        log.info(f"{dataset_attribute_ids}dataset_attribute_ids")
        # Try to find the dataset by dataset_id in the database
        # Query the database for the dataset with the given ID and DataAttributeId
        dataset_attributes_result = list(self.collection.find({"DataId": dataset_id, "DataAttributeId": {"$in": dataset_attribute_ids}, "BatchId": batch_id}, {"_id": 0, "DataAttributeValues": 1, "DataAttributeId": 1}))
        #dataset_attributes_result = list(DataAttributeValues.collection.find({"DataId": dataset_id, "DataAttributeId": {"$in": dataset_attribute_ids}, "IsActive": IsActive}, {"_id": 0, "DataAttributeValues": 1, "DataAttributeId": 1}))
        # Sort dataset_attributes_result based on the order of dataset_attribute_ids
        dataset_attributes_result.sort(key=lambda x: dataset_attribute_ids.index(x['DataAttributeId']))

            # Check if the query returned any results
        if not dataset_attributes_result:
            raise HTTPException(status_code=500, detail="No dataset attributes found")

            # Extract the ModelAttributeId values from the query results
        data_attribute_values = [item['DataAttributeValues'] for item in dataset_attributes_result]
        return data_attribute_values

    def update(self,dataset_id, value:dict):

        log.info(f"{dataset_id}data set value")
        #update the document with the given collection
        update_result = self.collection.update_many({"DataId": dataset_id}, {"$set": value})
        log.info("success")

            #check if the update was acknowledged
        if not update_result.acknowledged:
            raise RuntimeError(f"Failed to update document with  batchId {dataset_id}")

        return update_result.acknowledged
    
    
    def checkValue(self,dataset_id: float, dataset_attribute_ids: list, batch_id: float):
        # Check if dataset_id is not None and is a string
        if dataset_id is None or not isinstance(dataset_id, float):
            raise HTTPException(status_code=500, detail="No dataset found")
        log.info(f"{dataset_attribute_ids}dataset_attribute_ids")
        # Try to find the dataset by dataset_id in the database
        # Query the database for the dataset with the given ID and DataAttributeId
        dataset_attributes_result = list(self.collection.find({"DataId": dataset_id, "DataAttributeId": {"$in": dataset_attribute_ids}, "BatchId": batch_id}, {"_id": 0, "DataAttributeValues": 1, "DataAttributeId": 1}))
        #dataset_attributes_result = list(DataAttributeValues.collection.find({"DataId": dataset_id, "DataAttributeId": {"$in": dataset_attribute_ids}, "IsActive": IsActive}, {"_id": 0, "DataAttributeValues": 1, "DataAttributeId": 1}))
        # Sort dataset_attributes_result based on the order of dataset_attribute_ids
        dataset_attributes_result.sort(key=lambda x: dataset_attribute_ids.index(x['DataAttributeId']))

            # Check if the query returned any results
        if not dataset_attributes_result:
            return False

            # Extract the ModelAttributeId values from the query results
        return True