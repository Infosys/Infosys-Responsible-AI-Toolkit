'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

from app.config.logger import CustomLogger
from app.dao.DatabaseConnection import DB 

from dotenv import load_dotenv
load_dotenv()

log = CustomLogger()

# Create a MongoDB database instance
RAI_Report_DB = DB.connect()

class Batch:
    # Access the "Batch" collection in the RAI_Report_DB MongoDB database
    collection = RAI_Report_DB["Batch"]

    def find_tenet_id(batch_id: float):
        # Check if batch_id is not None and is a string
        if batch_id is None or not isinstance(batch_id, float):
            raise ValueError("Batch ID must be a non-empty float")
        
        # Try to find the TenetId by BatchId in the database
        try:
            TenetId = Batch.collection.find_one({"BatchId": batch_id}, {"_id": 0, "TenetId": 1})['TenetId']

        except Exception as e:
            raise ValueError(f"Invalid BatchId {batch_id}: {str(e)}")
        
        return TenetId