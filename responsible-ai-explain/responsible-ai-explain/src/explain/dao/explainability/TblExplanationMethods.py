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

from explain.dao.explainability.DatabaseConnection import DB
from explain.config.logger import CustomLogger

from dotenv import load_dotenv
load_dotenv()

# Create a custom logger instance
log = CustomLogger()

# Connect to the RAIExplainDB database
RAIExplainDB = DB.connect()

class Tbl_Explanation_Methods:
    # Set the collection to Tbl_Explanation_Methods in the RAIExplainDB database
    collection = RAIExplainDB["Tbl_Explanation_Methods"]
    
    @staticmethod
    def find_methods(model_framework, task_type, data_type):
        # Check if model_framework, task_type and data_type are not None or empty
        if not model_framework or not task_type or not data_type:
            log.error("model_framework, task_type and data_type are required")
            return {"error": "model_framework, task_type and data_type are required"}

        try:
            # Find the values in the collection where the 'modelFramework', 'taskType' and 'dataType' fields match the provided model_framework, task_type and data_type
            values = Tbl_Explanation_Methods.collection.find({"modelFramework": model_framework, "taskType": task_type, "dataType": data_type})
            
            # If no values were found, log an error and return None
            if not values:
                log.error("No values found with this model_framework, task_type and data_type")
                return {"error": "No values found with this model_framework, task_type and data_type"}

            # If values were found, return them
            return values
        except Exception as e:
            # If there was an error finding the values, log the error and return error message
            log.error(e)
            return {"error": str(e)}