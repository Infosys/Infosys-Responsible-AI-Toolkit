'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from fastapi import APIRouter, HTTPException
from mapper.coupledmoderationrequestdata import CoupledModerationRequestData
from mapper.moderationrequestdata import ModerationRequestData
from pydantic import BaseModel
import pymongo
from mapper.moderationtelemetrydata import ModerationResults
moderationRouter = APIRouter()
from datetime import datetime, date,timedelta
from zoneinfo import ZoneInfo
from service.moderationservice import moderationElasticDataPush, moderationRequestElasticDataPush, coupledRequestModerationElasticDataPush
from service.testmoderationservice import moderationElasticDataPushTest
from dotenv import load_dotenv
load_dotenv()
import os 
today = datetime.today()
@moderationRouter.post('/moderationtelemetryapi')
async def moderationTelemetryProcessing(data: ModerationResults):
    now = datetime.now()
    today= now.isoformat()
    # Generate a response
    response_data = {
        # 'message': response_message,
        'data': data
    }
    moderationElasticDataPush(data)
    return response_data

## FOR Moderation Request Telemetry API
@moderationRouter.post('/moderationrequesttelemetryapi')
async def moderationRequestTelemetryProcessing(data: ModerationRequestData):
    print("ELASTIC URL in API===",os.getenv("ELASTIC_URL"))
    now = datetime.now()
    today= now.isoformat()
    # print(data.uniqueid)
    # Generate a response
    response_data = {
        # 'message': response_message,
        'data': data
    }
    # print("DATA SENT", data)
    # print(data.uniqueid)
    moderationRequestElasticDataPush(data)
    return response_data

## FOR Coupled Moderation Request Telemetry API
@moderationRouter.post('/coupledmoderationrequesttelemetryapi')
async def coupledModerationRequestTelemetryProcessing(data: CoupledModerationRequestData):
    print("ELASTIC URL in API===",os.getenv("ELASTIC_URL"))
    now = datetime.now()
    today= now.isoformat()

    # Generate a response
    response_data = {
        # 'message': response_message,
        'data': data
    }
    # print("DATA SENT", data)
    # print(data.uniqueid)
    coupledRequestModerationElasticDataPush(data)
    return response_data

## FOR TESTING THE MODERATION API
@moderationRouter.post('/moderationtelemetryapitest')
async def moderationTelemetryProcessing(data: ModerationResults):
    print("ELASTIC URL in API===",os.getenv("ELASTIC_URL"))
    now = datetime.now()
    today= now.isoformat()
    print(data.uniqueid)
    # Generate a response
    response_data = {
        # 'message': response_message,
        'data': data
    }
    print("DATA SENT", data)
    print(data.uniqueid)
    moderationElasticDataPushTest(data)
    return response_data

