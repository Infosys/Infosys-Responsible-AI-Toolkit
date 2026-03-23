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

from explain.dao.workbench.DatabaseConnection import DB
from explain.config.logger import CustomLogger
from dotenv import load_dotenv
load_dotenv()

log = CustomLogger()

# Create a MongoDB database instance
RAIExplainDB = DB.connect()

class Dataset:
    
    # Access the "DataAttributes" collection in the Common Workbench MongoDB database
    collection = RAIExplainDB["Dataset"]
        
    def find(dataset_id: float):
        # Check if dataset_id is not None and is a string
        if dataset_id is None or not isinstance(dataset_id, float):
            raise ValueError("Dataset ID must be a non-empty float")
        
        # Try to find the model by model_id in the database
        try:
            result = Dataset.collection.find_one({"DataId": dataset_id}, {"_id": 0, "DataSetName": 1, "SampleData": 1})
            if result is None:
                raise ValueError(f"Invalid Dataset ID {dataset_id}")
        except Exception as e:
            raise 
        
        return result

class DatasetAttributes:
    
    # Access the "DataAttributes" collection in the Common Workbench MongoDB database
    collection = RAIExplainDB["DataAttributes"]
        
    def find(dataset_attributes: list):
        # Check if dataset_attributes is not None and is a string
        if dataset_attributes is None or not isinstance(dataset_attributes, list):
            raise ValueError("Dataset attribute(s) must be a non-empty list")
        
        # Check if dataset_attributes is an empty list
        if not dataset_attributes:
            raise ValueError("Dataset attribute(s) names must not be an empty list")
        
        # Try to find the dataset_attributes in the database
        try:
            # Query the database for the dataset attributes
            dataset_attribute_ids = list(DatasetAttributes.collection.find({"DataAttributeName": {"$in": dataset_attributes}}, {"_id": 0, "DataAttributeId": 1, "DataAttributeName": 1}))

            # Sort dataset_attribute_ids based on the order of dataset_attributes
            dataset_attribute_ids.sort(key=lambda x: dataset_attributes.index(x['DataAttributeName']))
            
            # Get all values of each dictionary in dataset_attribute_ids
            dataset_attribute_ids_values = [list(d.values())[0] for d in dataset_attribute_ids]
            
            # Check if the query returned any results
            if not dataset_attribute_ids:
                raise ValueError(f"Unable to found attribute id(s) from the given list: {dataset_attributes}")

        except Exception as e:
            # Catch exceptions that might occur during the database query
            raise
        
        return dataset_attribute_ids_values

class DatasetAttributeValues:
    
    # Access the "Tbl_Dataset" collection in the RAIExplainDB database
    collection = RAIExplainDB["DataAttributesValues"]
    
    @staticmethod
    def find(dataset_id: float, dataset_attribute_ids: list):
        # Check if dataset_id is not None and is a string
        if dataset_id is None or not isinstance(dataset_id, float):
            raise ValueError("Dataset ID must be a non-empty float")
        
        # Try to find the dataset by dataset_id in the database
        try:
            # Query the database for the dataset with the given ID and DataAttributeId
            dataset_attributes_result = list(DatasetAttributeValues.collection.find({"DataId": dataset_id, "DataAttributeId": {"$in": dataset_attribute_ids}}, {"_id": 0, "DataAttributeValues": 1, "DataAttributeId": 1}))

            # Sort dataset_attributes_result based on the order of dataset_attribute_ids
            dataset_attributes_result.sort(key=lambda x: dataset_attribute_ids.index(x['DataAttributeId']))
            
            # Check if the query returned any results
            if not dataset_attributes_result:
                raise ValueError(f"No dataset found with Dataset ID {dataset_id}")
            
            # Extract the ModelAttributeId values from the query results
            data_attribute_values = [item['DataAttributeValues'] for item in dataset_attributes_result]
        except Exception as e:
            # Catch any other exceptions that might occur during the database query
            raise
        
        return data_attribute_values