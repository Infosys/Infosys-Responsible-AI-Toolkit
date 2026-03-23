'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

from src.config.logger import CustomLogger
from src.dao.DatabaseConnection import DB 
from pymongo.errors import InvalidDocument

from dotenv import load_dotenv
import concurrent.futures as con
import os

load_dotenv()

telemetry_flg =os.getenv("TELEMETRY_FLAG")

apiEndPoint ='/v1/security/model'
errorRequestMethod = 'GET'



log = CustomLogger()

# Create a MongoDB database instance
RAI_Report_DB = DB.connect()

class Html:
    # Access the "Html" collection in the RAI_Report_DB MongoDB database
    collection = RAI_Report_DB["Html"]

    @staticmethod
    def find_one(batch_id: float, tenet_id: float):
        try:
            # Check if model_id is not None and is a string
            if batch_id is None or not isinstance(batch_id, float) or tenet_id is None or not isinstance(tenet_id, float):
                raise ValueError("BatchID/TenetID must be a non-empty float")
            
            # Try to find the HtmlFileId by BatchId and TenetId in the database
            try:
                HtmlFileId = Html.collection.find_one({"BatchId": batch_id, "TenetId": tenet_id}, {"_id": 0, "HtmlFileId": 1})['HtmlFileId']
            except Exception as e:
                raise ValueError(f"Invalid BatchID/TenetID: {batch_id}, {tenet_id}: {str(e)}")
            
            return HtmlFileId
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "find_oneHtml", e, apiEndPoint, errorRequestMethod)
    
    @staticmethod
    def find(batch_id: float, tenet_id: float):
        try:
            # Check if model_id is not None and is a string
            if batch_id is None or not isinstance(batch_id, float) or tenet_id is None or not isinstance(tenet_id, float):
                raise ValueError("BatchID/TenetID must be a non-empty float")
            
            # Try to find the HtmlFileId by BatchId and TenetId in the database
            try:
                HtmlFileId = Html.collection.find_one({"BatchId": batch_id, "TenetId": tenet_id}, {"_id": 0, "HtmlFileId": 1, "ReportName": 1})['HtmlFileId']
            except Exception as e:
                raise ValueError(f"Invalid BatchID/TenetID: {batch_id}, {tenet_id}: {str(e)}")
            
            return HtmlFileId
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "findHtml", e, apiEndPoint, errorRequestMethod)
    
    @staticmethod
    def create(document):
        
        try:
            # Check if document is not None
            if document is None:
                raise ValueError("Document must be a non-empty value")
            
            try:
                # Insert the document into the collection
                create_result = Html.collection.insert_one(document)
                
                # Check if the insertion was acknowledged
                if not create_result.acknowledged:
                    raise RuntimeError("Failed to insert document into the collection")
                
                return create_result.acknowledged
            except InvalidDocument:
                raise ValueError("Document is not a valid document")
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "createHtml", e, apiEndPoint, errorRequestMethod)