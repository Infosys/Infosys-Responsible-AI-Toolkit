'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pymongo
errorlogRouter = APIRouter()
from datetime import datetime, date,timedelta
from dotenv import load_dotenv
from service.errorlogService import errorLogElasticDataPush
from mapper.errorlogtelemetrydata import Error, TelemetryData
load_dotenv()
import os 

today = datetime.today()
@errorlogRouter.post('/errorlogtelemetryapi')
async def errorlogTelemetryProcessing(data: TelemetryData):
    # print("ELASTIC URL AFTER Calling CODE===",os.getenv("ELASTIC_URL"))
    # Generate a response
    response_data = {
        # 'message': response_message,
        'data': data
    }
    # print("ELASTIC URL AFTER Calling CODE===",os.getenv("ELASTIC_URL"))
    errorLogElasticDataPush(data)
    return response_data