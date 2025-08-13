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

class Model:
    
    # Access the "Model" collection in the Common Workbench database
    collection = RAIExplainDB["Model"]
        
    def find(model_id: float):
        # Check if model_id is not None and is a string
        if model_id is None or not isinstance(model_id, float):
            raise ValueError("Model ID must be a non-empty float")
        
        # Try to find the model by model_id in the database
        try:
            result = Model.collection.find_one({"ModelId": model_id}, {"_id": 0, "ModelName": 1, "ModelData": 1, 'ModelEndPoint': 1})
            if result is None:
                raise ValueError(f"Invalid Model ID: {model_id}")

        except Exception as e:
            raise 
        
        return result

class ModelAttributes:
   
    # Access the "ModelAttributes" collection in the Common Workbench database
    collection = RAIExplainDB["ModelAttributes"]
       
    def find(model_attributes: list):
        # Check if model_id is not None and is a string
        if model_attributes is None or not isinstance(model_attributes, list):
            raise ValueError("Model attributes must be a non-empty list")
       
        # Check if model_attributes is an empty list
        if not model_attributes:
            raise ValueError("Model attributes must not be an empty list")
       
        # Try to find the model by model_attributes in the database
        try:
            # Query the database for the model attributes
            model_attribute_ids = list(ModelAttributes.collection.find({"ModelAttributeName": {"$in": model_attributes}}, {"_id": 0, "ModelAttributeId": 1, "ModelAttributeName": 1}))
           
            # Sort dataset_attribute_ids based on the order of dataset_attributes
            model_attribute_ids.sort(key=lambda x: model_attributes.index(x['ModelAttributeName']))

            # Check if the query returned any results
            if not model_attribute_ids:
                raise ValueError(f"Unable to found attribute id(s) from the given list: {model_attributes}")
           
            # Extract the ModelAttributeId values from the query results
            model_attribute_ids_values = [item['ModelAttributeId'] for item in model_attribute_ids]
        except Exception as e:
            # Catch exceptions that might occur during the database query
            raise 
       
        return model_attribute_ids_values
 
class ModelAttributeValues:
   
    # Access the "ModelAttributesValues" collection in the Common Workbench database
    collection = RAIExplainDB["ModelAttributesValues"]
       
    def find(batch_id: float, model_id: float, model_attribute_ids: list):
        # Check if model_id is not None and is a string
        if model_id is None or not isinstance(model_id, float):
            raise ValueError("Model ID must be a non-empty float")
       
        # Try to find the model by model_id in the database
        try:
            if batch_id is not None:
                # Query the database for the model attribute values
                model_attributes = list(ModelAttributeValues.collection.find({"ModelId": model_id, "ModelAttributeId": {"$in": model_attribute_ids}, "BatchId": batch_id, 'IsActive':'Y'}, {"_id": 0, "ModelAttributeValues": 1, "ModelAttributeId": 1}))
            else:
                # Query the database for the model attribute values
                model_attributes = list(ModelAttributeValues.collection.find({"ModelId": model_id, "ModelAttributeId": {"$in": model_attribute_ids}, 'IsActive':'Y'}, {"_id": 0, "ModelAttributeValues": 1, "ModelAttributeId": 1}))
            
            if not model_attributes:
                raise ValueError(f"No records found for model_id: {model_id}. Please check the model_id.")
            
            # Sort dataset_attributes_result based on the order of dataset_attribute_ids
            model_attributes.sort(key=lambda x: model_attribute_ids.index(x['ModelAttributeId']))

            # Extract the ModelAttributeId values from the query results
            model_attribute_values = [item['ModelAttributeValues'] for item in model_attributes]

        except Exception as e:
            raise
 
        return model_attribute_values
    
    def update(batch_id,model_id,model_attribute_id,value:dict):
    
        try:
            # Update the document in the collection
            update_result= ModelAttributeValues.collection.update_one({'BatchId': batch_id, 'ModelId': model_id,'ModelAttributeId': model_attribute_id, 'IsActive':'Y'}, {'$set': value})
            
            # Check if the update was acknowledged
            if not update_result.acknowledged:
                raise RuntimeError(f"Failed to update document with ModelId {model_id} and ModelAttributeId {model_attribute_id}")
            
            return update_result.acknowledged
        except InvalidDocument:
            raise ValueError(f"Document is not a valid document with ModelId {model_id} and ModelAttributeId {model_attribute_id}")
        except Exception as e:
            raise
    