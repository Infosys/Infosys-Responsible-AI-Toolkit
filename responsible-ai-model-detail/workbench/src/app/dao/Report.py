'''
MIT license https://opensource.org/licenses/MIT Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from app.config.logger import CustomLogger
from app.dao.DatabaseConnection import DB
from pymongo.errors import InvalidDocument

from dotenv import load_dotenv
load_dotenv()

log = CustomLogger()
class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

# Create a MongoDB database instance
mydb = DB.connect()


class Report:
    
    # Access the "Tbl_Model" collection in the RAIExplainDB MongoDB database
    mycol = mydb["Report"]
    
    @staticmethod
    def create(document):
        # Check if document is not None
        if document is None:
            raise ValueError("Document must be a non-empty value")
        
        try:
            # Insert the document into the collection
            create_result = Report.mycol.insert_one(document)
            
            # Check if the insertion was acknowledged
            if not create_result.acknowledged:
                raise RuntimeError("Failed to insert document into the collection")
            
            return create_result.acknowledged
        except InvalidDocument:
            raise ValueError("Document is not a valid document")
        
    @staticmethod
    def find_one(batch_id: float, tenet_id: float):
        # Check if model_id is not None and is a string
        if batch_id is None or not isinstance(batch_id, float) or tenet_id is None or not isinstance(tenet_id, float):
            raise ValueError("BatchID/TenetID must be a non-empty float")
        
        # Try to find the model by model_id in the database
        try:
            report_details = Report.mycol.find_one({"BatchId": batch_id, "TenetId": tenet_id}, {"_id": 0, "ReportFileId": 1, "ContentType": 1, "ReportName": 1})
        except Exception as e:
            raise ValueError(f"Invalid BatchID/TenetID: {batch_id}, {tenet_id}: {str(e)}")
        
        return report_details
    
    @staticmethod
    def findall(query):

        value_list = []
        values = Report.mycol.find(query,{})
        for v in values:
            v = AttributeDict(v)
            value_list.append(v)

        return value_list
    
    @staticmethod
    def delete(query):
            Report.mycol.delete_many(query)