from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pymongo
from mapper.coupledmoderationtelemetrydata import ModerationResults, completionResponse
coupledModerationRouter = APIRouter()
from datetime import datetime, date,timedelta
from zoneinfo import ZoneInfo
'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from service.coupledmoderationservice import coupledModerationElasticDataPush
from dotenv import load_dotenv
load_dotenv()
import os 

today = datetime.today()
@coupledModerationRouter.post('/coupledmoderationtelemetryapi')
async def moderationTelemetryProcessing(data: completionResponse):
    # print("ELASTIC URL AFTER Calling CODE===",os.getenv("ELASTIC_URL"))
    # print("ELASTIC URL AFTER Calling CODE===To be printed")
    # print("DATA RECEIVED FROM SERVER", data)
    now = datetime.now()
    print(type(data))
    print(data.uniqueid)
    #data.date = today
    #result = collection.insert_one({"_id":data.id,"Moderations":data.dict()})
    # if insert_moderation_results(data):
    #     response_message = "Data inserted successfully"
    # else:
    #     raise HTTPException(status_code=500, detail='Failed to insert data into MongoDB')

    # Generate a response
    response_data = {
        # 'message': response_message,
        'data': data
    }
    
    # print("DATA INSERTED/UPDATED", data)
    # print("ELASTIC URL AFTER Calling CODE===",os.getenv("ELASTIC_URL"))
    coupledModerationElasticDataPush(data)
    return response_data

