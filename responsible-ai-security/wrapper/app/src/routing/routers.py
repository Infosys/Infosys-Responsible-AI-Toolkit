'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024-2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import datetime
from fastapi import Depends,APIRouter,Query, Body,Form,HTTPException
from src.mappers.mappers import GetAttackDataRequest
from src.service.service import Infosys, Bulk
from src.service.utility import Utility as UT
from src.config.logger import CustomLogger
from typing import Dict, Optional
import os
import gc

tool = APIRouter()
logs = APIRouter()
attack = APIRouter()
bulk = APIRouter()
log = CustomLogger()

@attack.post('/rai/v1/security_workbench/attack')
async def get_attacks(TargetClassifier:str=Form(),TargetDataType:str=Form()):
    try:
        # payload = {'targetClassifier': target_classifier, 'targetDataType': target_data_type}
        payload = {'targetClassifier': TargetClassifier, 'targetDataType': TargetDataType}
        response = Infosys.getAttackFuncs(payload)
        gc.collect()
        return response
    except Exception as e:
        log.error(f"Error in get_attacks: {str(e)}")
        gc.collect()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@attack.post('/rai/v1/security_workbench/addattack')
async def add_Attack(Payload: GetAttackDataRequest):
    try:
        response = Infosys.addAttack(Payload)
        gc.collect()
        return response
    except Exception as e:
        log.error(f"Error in add_Attack: {str(e)}")
        gc.collect()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@attack.delete('/rai/v1/security_workbench/deleteattack')
async def delete_Attack(AttacFunc: str):
    try:
        payload = {'attackName': AttacFunc}
        response = Infosys.deleteAttack(payload)
        gc.collect()
        return response
    except Exception as e:
        log.error(f"Error in delete_Attack: {str(e)}")
        gc.collect()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
 
@bulk.post('/rai/v1/security_workbench/runallattacks')
# async def run_all_attacks(batchId: float = Form(...), dateTime: Optional[datetime.datetime] = Form(None, description = "{dateTime=datetime.datetime.now()}")):
async def run_all_attacks(batchId: float = Form(...), dateTime: Optional[datetime.datetime] = Form(None)):
    try:
        print(UT.dateTimeFormat(dateTime))
        # payload = {'batchid': batchId}
        payload = {'batchid': batchId, 'dateTime':UT.dateTimeFormat(dateTime)}
        response = Bulk.runAllAttack(payload)
        gc.collect()
        return {'BatchId': response}
    except Exception as e:
        log.error(f"Error in run_all_attacks: {str(e)}")
        gc.collect()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")