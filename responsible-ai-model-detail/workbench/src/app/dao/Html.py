'''
MIT license https://opensource.org/licenses/MIT Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''


from app.config.logger import CustomLogger
from app.dao.DatabaseConnection import DB 

from dotenv import load_dotenv
load_dotenv()

log = CustomLogger()
class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

# Create a MongoDB database instance
mydb = DB.connect()

class Html:
    # Access the "Html" collection in the RAI_Report_DB MongoDB database
    mycol = mydb["Html"]

    @staticmethod
    def find_one(batch_id: float, tenet_id: float):
        # Check if model_id is not None and is a string
        if batch_id is None or not isinstance(batch_id, float) or tenet_id is None or not isinstance(tenet_id, float):
            raise ValueError("BatchID/TenetID must be a non-empty float")
        
        # Try to find the HtmlFileId by BatchId and TenetId in the database
        try:
            HtmlFileId = Html.mycol.find_one({"BatchId": batch_id, "TenetId": tenet_id}, {"_id": 0, "HtmlFileId": 1})['HtmlFileId']
        except Exception as e:
            raise ValueError(f"Invalid BatchID/TenetID: {batch_id}, {tenet_id}: {str(e)}")
        
        return HtmlFileId
    
    @staticmethod
    def find(batch_id: float, tenet_id: float):
        # Check if model_id is not None and is a string
        if batch_id is None or not isinstance(batch_id, float) or tenet_id is None or not isinstance(tenet_id, float):
            raise ValueError("BatchID/TenetID must be a non-empty float")
        
        # Try to find the HtmlFileId by BatchId and TenetId in the database
        try:
            HtmlFileId = Html.mycol.find_one({"BatchId": batch_id, "TenetId": tenet_id})
        except Exception as e:
            raise ValueError(f"Invalid BatchID/TenetID: {batch_id}, {tenet_id}: {str(e)}")
        
        return HtmlFileId
    
    @staticmethod
    def findall(query):

        value_list = []
        values = Html.mycol.find(query,{})
        for v in values:
            v = AttributeDict(v)
            value_list.append(v)

        return value_list
    
    @staticmethod
    def delete(query):
            Html.mycol.delete_many(query)