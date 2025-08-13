'''
MIT license https://opensource.org/licenses/MIT Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from fastapi import Depends,APIRouter,Query, Body,Form
from app.mappers.mappers import GetBatchPayloadRequest, TenetDataRequest,GetModelPayloadRequest,GetModelRequest,UpdateModelPayloadRequest,GetDataPayloadRequest,GetDataRequest,UpdateDataPayloadRequest,GetPreprocessorPayloadRequest,GetPreprocessorRequest, UpdatePreprocessorPayloadRequest          #,GetGroundtruthFileRequest
from app.service.service import InfosysRAI
from app.config.logger import CustomLogger
import os
import gc

data = APIRouter()
model = APIRouter()
tenet = APIRouter()
batch = APIRouter()
preprocessor = APIRouter()
log=CustomLogger()

# ------------------------------------------------------------------------------------

@tenet.get('/v1/workbench/tenet')
def get_tenet():
    response = InfosysRAI.getTenetsList()
    gc.collect()
    return response

@tenet.post('/v1/workbench/addtenet')
def add_tenet(Payload:TenetDataRequest):
    response = InfosysRAI.addTenet(Payload)
    gc.collect()
    return response

@tenet.delete('/v1/workbench/deletetenet')
def delete_tenet(TenetName: str):
    payload = {'TenetName':TenetName}
    response = InfosysRAI.deletetenet(payload)
    gc.collect()
    return response

# ------------------------------------------------------------------------------------

@data.post('/v1/workbench/data')
def get_Datas(userId:str=Form()):
    payload = {'userid':userId}
    response = InfosysRAI.getData(payload)
    gc.collect()
    return response

@data.post('/v1/workbench/adddata')
async def add_Data(userId = Form(...),Payload:GetDataPayloadRequest = Body(...), Payload2:GetDataRequest = Depends()):      #Payload3:GetGroundtruthFileRequest = Depends()
    response = InfosysRAI.addData(userId,Payload,Payload2)       #Payload3
    gc.collect()
    return response

@data.patch('/v1/workbench/updatedata')
async def update_Data(userId = Form(...),dataid:float=Form(),Payload:UpdateDataPayloadRequest = Body(...), Payload2:GetDataRequest = Depends()):
    payload = {'userid':userId, 'dataid':dataid}
    response = InfosysRAI.updateData(payload,Payload,Payload2)
    gc.collect()
    return response

@data.delete('/v1/workbench/deletedata')
async def delete_Data(userId:str=Form(), dataid:float=Form()):
    payload = {'userid':userId, 'dataid':dataid}
    response = InfosysRAI.deleteData(payload)
    gc.collect()  
    return response

# ------------------------------------------------------------------------------------

@model.post('/v1/workbench/model')
def get_Models(userId:str=Form()):
    payload = {'userid':userId}
    response = InfosysRAI.getModel(payload)
    gc.collect()
    return response

@model.post('/v1/workbench/addmodel')
async def add_Model(userId = Form(...),Payload:GetModelPayloadRequest = Body(...), Payload2:GetModelRequest = Depends()):
    response = InfosysRAI.addModel(userId,Payload,Payload2)
    gc.collect()
    return response

@model.patch('/v1/workbench/updatemodel')
async def update_Model(userId = Form(...),modelId:float=Form(),Payload:UpdateModelPayloadRequest = Body(...), Payload2:GetModelRequest = Depends()):
    payload = {'userid':userId, 'modelid':modelId}
    response = InfosysRAI.updateModel(payload,Payload,Payload2)
    gc.collect()
    return response

@model.delete('/v1/workbench/deletemodel')
async def delete_Model(userId:str=Form(), modelId:float=Form()):
    payload = {'userid':userId, 'modelid':modelId}
    response = InfosysRAI.deleteModel(payload)
    gc.collect()  
    return response

# ------------------------------------------------------------------------------------

## FOR PREPROCESSING ------------------------------------------------------------------------------------
@preprocessor.post('/v1/workbench/preprocessor')
def get_Preprocessor(userId:str=Form()):
    payload = {'userid':userId}
    response = InfosysRAI.getPreprocessor(payload)
    gc.collect()
    return response

@preprocessor.post('/v1/workbench/addpreprocessor')
async def add_Preprocessor(userId = Form(...),preprocessorName: str = Form(...), Payload2:GetPreprocessorRequest = Depends()):
    Payload = {"userId": userId, "preprocessorName": preprocessorName}
    response = InfosysRAI.addPreprocessor(userId,Payload,Payload2)
    gc.collect()
    return response

@preprocessor.patch('/v1/workbench/updatepreprocessor')
async def update_Preprocessor(userId: str = Form(...), preprocessorId: float = Form(...),preprocessorName: str = Form(...), Payload2: GetPreprocessorRequest = Depends()):
    payload = {'userid':userId, 'preprocessorid':preprocessorId}
    payload1 = {'PreprocessorName':preprocessorName}
    response = InfosysRAI.updatePreprocessor(payload,payload1,Payload2)
    gc.collect()
    return response

@preprocessor.delete('/v1/workbench/deletepreprocessor')
async def delete_Preprocessor(userId:str=Form(), preprocessorId:float=Form()):
    payload = {'userid':userId, 'preprocessorid':preprocessorId}
    response = InfosysRAI.deletePreprocessor(payload)
    gc.collect()  
    return response

@batch.post('/v1/workbench/batchgeneration')
async def getBatch(Payload:GetBatchPayloadRequest = Body(...)):
    response = InfosysRAI.getBatchList(Payload)
    gc.collect()
    return response

@batch.post('/v1/workbench/getbatchstatus')
def getBatch(id:float=Form()):
    response = InfosysRAI.getBatchStatusList(id)
    gc.collect()
    return response

@batch.post('/v1/workbench/getbatchtable')
def getBatch(userId:str=Form()):
    payload = {'userid':userId}
    response = InfosysRAI.getBatchTable(payload)
    gc.collect()
    return response

@batch.delete('/v1/workbench/deletebatch')
async def delete_Batch(userId:str=Form(), batchId:float=Form()):
    payload = {'userid':userId, 'batchid':batchId}
    response = InfosysRAI.deleteBatch(payload)
    gc.collect()  
    return response