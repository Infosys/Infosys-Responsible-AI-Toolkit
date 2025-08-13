from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pymongo
from mapper.privacytelemetrydata import TelemetryData
router = APIRouter()
from datetime import datetime, date,timedelta
# from elasticforprivacy import privacyElasticData
from dotenv import load_dotenv
from service.privacyservice import privacyElasticDataPush
load_dotenv()
import os 
'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
# # Establish a connection to MongoDB
# client = pymongo.MongoClient(os.getenv("MONGO_PATH"))
# db = client[os.getenv("MONGO_DB_NAME")]
# collection = db['privacytelemetrydata']
today = datetime.today()
@router.post('/privacytelemetryapi')
async def privacyTelemetryProcessing(data: TelemetryData):
    # print("ELASTIC URL AFTER Calling CODE===",os.getenv("ELASTIC_URL"))
    print("ELASTIC URL AFTER Calling CODE===To be printed")
    now = datetime.now()
    today= now.isoformat()
    #print(today)
    data.date = today
    #result = collection.insert_one(data.dict())
    # Call the insert_data function from the mongodb module
    # if insert_data(data):
    #     response_message = "Data inserted successfully"
    # else:
    #     raise HTTPException(status_code=500, detail='Failed to insert data into MongoDB')
    
    # Generate a response
    response_data = {
        # 'message': response_message,
        'data': data
    }
    print("DATA INSERTED/UPDATED", data)
    # print("ELASTIC URL AFTER Calling CODE===",os.getenv("ELASTIC_URL"))
    privacyElasticDataPush(data)
    return response_data

