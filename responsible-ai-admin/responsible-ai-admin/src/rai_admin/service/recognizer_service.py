"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from io import BytesIO
import io
import json
import os
import time
from datetime import datetime

from fastapi import Response
from fastapi.responses import FileResponse



from rai_admin.dao.AuthorityDb import AuthorityDb

from rai_admin.dao.OpenAIDb import OpenAIDb

from rai_admin.dao.ConfigApiDb import ConfigApiDb
from rai_admin.dao.AccMasterDb import AccMasterDb
from rai_admin.dao.AccPtrnMappingDb import AccPtrnDb
from rai_admin.dao.AccDataGrpMappingDb import AccDataGrpDb
from rai_admin.dao.AccSafetyMappingDb import AccSafetyDb
from rai_admin.dao.ptrnRecog import PtrnRecog
from rai_admin.dao.DataRecogdb import RecogDb
from rai_admin.dao.EntityDb import EntityDb
from rai_admin.mappers.RecognizerMapper import DataEntitiesResponse, RecogStatus,RecogResponse
from rai_admin.mappers.AccMasterMapper import *
from rai_admin.mappers.PtrnRecogMapper import *
from rai_admin.mappers.PrivacyMapper import *
from rai_admin.mappers.FmConfigMapper import *

from rai_admin.mappers.SafetyMapper import *
from rai_admin.dao.FmConfigDb import FmConfigDb

from rai_admin.dao.FmConfigGrpMappingDb import FmConfigGrpDb
from rai_admin.dao.MasterTemplateMappingDb import AccTemplateMap
from rai_admin.dao.ModerationCheckDb import ModerationChecksDb,OutputModerationChecksDb
from rai_admin.dao.RestrictedtopicDetailsDb import RestrictedTopic
from rai_admin.dao.ThemeTextsDb import ThemeText
from rai_admin.dao.AdminException import ExceptionDb
from rai_admin.config.logger import request_id_var
import pandas as pd
from rai_admin.config.logger import CustomLogger
from rai_admin.dao.AccDataGrpMappingDb import AccDataGrpDb

azurebloburl=os.getenv("AZUREADDFILE")
containername=os.getenv("CONTAINERNAME")

log = CustomLogger()
class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    
# class PrtnRecog:
#     def ptrnEntry(payload)->PtrnRecogStatus:
        
#         print(payload)
#         value={"Name":payload.ptrnName,"ptrn":payload.ptrn,"entity":payload.ptrnEntity}
#         print(value)
#         PtrnRecog.create(value)
#         obj=PtrnRecogStatus
#         obj.status="true"
#         return obj
    
#     def getPtrnEntry()->PtrnRecogResponse:
#         response=PtrnRecog.findall({})
#         obj=PtrnRecogResponse
#         obj.PtrnList=response
#         print(obj)
#         return obj
    
#     Bugfix
#     def ptrnUpdate(payload)->PtrnRecogStatus:
        
#         print(payload)
#         value={"ptrnName":payload.ptrnName,"dataPtrn":payload.ptrn,"supported_entity":payload.ptrnEntity}
#         print(value)
#         PtrnRecog.update(payload.ptrnRecId,value)
#         obj=PtrnRecogStatus
#         obj.status="true"
#         return obj     
        
#     def ptrnDelete(payload)->PtrnRecogStatus:
#         print(payload)
#         PtrnRecog.delete(payload.ptrnRecId)
#         obj=PtrnRecogStatus
#         obj.status="true"
#         return obj     

class DataRecogGrp:
    def dataEntry(payload)->RecogStatus:
        try:
            payload=AttributeDict(payload)
            log.info(str(payload))
            recogs=RecogDb.findall({"RecogName":payload.name})
            if(len(recogs)>0):
                obj=RecogStatus
                obj.status="False"
                return obj
            # score=0.01
            if(payload.score == None):
                score=0.01
            else:
                score=payload.score
            if(payload.context == None):
                context =""
            else:
                context=payload.context
            value={"Name":payload.name,"entity":payload.entity,"type":payload.type,"edit":"Yes","define":"No","score":score,"context":context}
            did=RecogDb.create(value)
            dataList=[]
            if(payload.file):
                content=payload.file.file.read()
                buff=BytesIO(content)
            # print(buff)
                df=pd.read_csv(buff)
                col=df.columns
                dataList=df[col[0]]
            else:
                dataList.append(payload.ptrn)    
            # The line `print(df)` is printing the contents of the DataFrame `df`.
            # print(df)
            # print(col)
            print(dataList)
            status="failed"
            for data in dataList:
                status=EntityDb.create({"Name":data,"dgid":did})
                time.sleep(1/1000)
            obj=RecogStatus
            obj.status=str(status)
            return obj
        except Exception as e:
            log.info(str(e))
            obj=RecogStatus
  
            obj.status="False"
            return obj
       
       
    def getDataEntry()->RecogResponse:

        # print("Inside getDataEntry====")
        
        response=RecogDb.findall({})
        response.sort(key=lambda item: item["RecogName"])
        
        # response=[]
        # values=RecogDb.mycol.find({}).sort("RecogName",1)
        # for v in values:
        #     v=AttributeDict(v)
        #     response.append(v)
            
        # response=list(response)
        

        # print("response======",response)
        
        obj=RecogResponse
        obj.RecogList=response
        # print(obj)
        return obj
    
    def getEntityDetails(payload)->DataEntitiesResponse:
        log.info(str(payload))
        x=EntityDb.findall({"RecogId":payload.RecogId})
        obj=DataEntitiesResponse
        obj.DataEntities=x
        # print(x)
        return obj
        
    def DataGrpUpdate(payload)->RecogStatus:
        try:
            log.info(str(payload))
            value={"RecogName":payload.RecogName,"supported_entity":payload.supported_entity}

            status=RecogDb.update(payload.RecogId,value)
            obj=RecogStatus
            obj.status=str(status)
            return obj
        except Exception as e:
            log.info(str(e))
            obj=RecogStatus
            obj.status="False"
            return obj
            
    
    
    
    def EntityUpdate(payload)->RecogStatus:
        try:
            log.info(str(payload))
            value={"EntityName":payload.EntityName}
            print(value)
            status=EntityDb.update(payload.EntityId,value)
            obj=RecogStatus
            obj.status=str(status)
            return obj
        except Exception as e:
            log.info(str(e))
            obj=RecogStatus
            obj.status="False"
            return obj
                 
    def EntityAdd(payload)->RecogStatus:
        
        log.info(str(payload))
        status="False"
        for data in payload.EntityNames:
            entity=EntityDb.findall({"RecogId":payload.RecogId,"EntityName":data})
            if(len(entity)==0):
                  status=EntityDb.create({"Name":data,"dgid":payload.RecogId}) 
        obj=RecogStatus
        obj.status=str(status)
        return obj

    
    
    
    
    def DataGrpDelete(payload)->AccMasterStatus:
        log.info(str(payload))
        RecogDb.delete(payload.RecogId)
        AccDataGrpDb.deleteMany({"dataRecogGrpId":payload.RecogId})
        status=EntityDb.deleteMany({"dataRecogGrpId":payload.RecogId})
        obj=AccMasterStatus
        obj.status=str(status)
        return obj  
    def DataEntityDelete(payload)->RecogResponse:
        log.info(str(payload))
        status=EntityDb.delete(payload.EntityId)
        obj=DataEntitiesResponse
        obj.status=str(status)
        return obj  
    
    

class AccMaster:
    def getAccountDtl():
        accDtl = AccMasterDb.findall({})
        res=[]
        accdtl=[]
        for i in accDtl:
            accdtl.append({"accMasterId":i.accMasterId,"portfolio":i.portfolio,"account":i.account})
        log.debug("accccc====="+str(accDtl))
        res.append({"AccountDetails":accdtl})
        return res
    def addPrivacyParameter(payload)->AccMasterStatus:
        try:
            log.info(str(payload))
            acc=AccMasterDb.findall({"account":payload.account,"portfolio":payload.portfolio})
            if(len(acc)==0):
                obj=AccMasterStatus
                obj.status="False"
                return obj

            # value={"AName":payload.portfolio,"SName":payload.account}  #skip
            # print(payload)
            # accId=AccMasterDb.create(value)   #skip
            # for ptrn in payload.ptrnList:
            #     ptrnValue={"Aid":accId,"Pid":float(ptrn)}
                # AccPtrnDb.create(ptrnValue)
            accId = acc[0]['accMasterId']
            status="False"
            privacyConfig = AccDataGrpDb.findall({"accMasterId":accId})
            if(len(privacyConfig)>0):
                 obj=AccMasterStatus
                 obj.status="False"
                 return obj
            else:
                for data in payload.dataGrpList:
                    grpValue={"Aid":accId,"Did":float(data)}
                    status=AccDataGrpDb.create(grpValue)
                
                # for data in payload.dataGrpList:
                #     grpValue={"Aid":accId,"Did":float(data)}
                #     status=AccDataGrpDb.create(grpValue)
            #print("PAYLOAD SAFETY",payload.safetyRequest)
            # for data in payload.safetyRequest:
            # safetyValue={"Aid":accId}
            # safetyValue.update(payload.safetyRequest)
            # print("PAYLOAD SAFETY",safetyValue)
            # status=AccSafetyDb.create(safetyValue)

            obj=AccMasterStatus
            obj.status=str(status)
            return obj
        except Exception as e:
            log.info(str(e))
            obj=AccMasterStatus
            obj.status="False"
            return obj
    
    

    def accEntry(payload)->AccMasterStatus:
        try:
            log.info(str(payload))
            acc=AccMasterDb.findall({"account":payload.account,"portfolio":payload.portfolio})
            if(len(acc)>0):
                obj=AccMasterStatus
                obj.status="False"
                return obj

            value={"AName":payload.portfolio,"SName":payload.account}  #skip
            # print(payload)
            accId=AccMasterDb.create(value)   #skip
            # for ptrn in payload.ptrnList:
            #     ptrnValue={"Aid":accId,"Pid":float(ptrn)}
                # AccPtrnDb.create(ptrnValue)
            status="False"
            if accId :
                status="True"
            # for data in payload.dataGrpList:
            #     grpValue={"Aid":accId,"Did":float(data)}
            #     status=AccDataGrpDb.create(grpValue)
            
            # for data in payload.dataGrpList:
            #     grpValue={"Aid":accId,"Did":float(data)}
            #     status=AccDataGrpDb.create(grpValue)
            # #print("PAYLOAD SAFETY",payload.safetyRequest)
            # # for data in payload.safetyRequest:
            # safetyValue={"Aid":accId}
            # safetyValue.update(payload.safetyRequest)
            # print("PAYLOAD SAFETY",safetyValue)
            # status=AccSafetyDb.create(safetyValue)

            obj=AccMasterStatus
            obj.status=status
            return obj
        except Exception as e:
            log.info(str(e))
            obj=AccMasterStatus
            obj.status="False"
            return obj
    
    
    
    def getAccEntry()->AccMasterResponse:
        response=AccMasterDb.findall({})
        
        obj=AccMasterResponse
        obj.accList=response
    
        return obj
    
    # def getAccPtrn(payload)->AccPtrnResponse:
    #     log.info(str(payload))
    #     ptrnList=AccPtrnDb.mycol.distinct("ptrnRecId",{"accMasterId":payload.accMasterId})
    #     # print(data)
        
    #     response=PtrnRecog.findall({"ptrnRecId":{"$in":ptrnList}})
        
    #     obj=AccPtrnResponse
    #     obj.PtrnList=response
    #     obj.accMasterId=payload.accMasterId
    #     return objs

    
    def getAccData(payload)->AccDataResponse:
        log.info(str(payload))
        dataList=AccDataGrpDb.findall({"accMasterId":payload.accMasterId})
        response=[]
        # print("type of datalist===",len(dataList))
        for i in dataList:
            # print("value of i=====",i)
            value= RecogDb.findall({"RecogId":i.dataRecogGrpId})
            if(len(value)>0):
                value[0]["isHashify"]=i.isHashify
                response.append(value[0])
        obj=AccDataResponse
        obj.dataList=response
        obj.accMasterId=payload.accMasterId
        # print(obj)
        return obj
    
    def getAccSafetyData(payload) -> AccSafetyRequest:
        log.info(str(payload))
        dataList = AccSafetyDb.findall({"accMasterId": payload.accMasterId})

        # Extract specific parameters and convert datetime objects to string format
        serialized_dataList = {}
        for item in dataList:
            serialized_item = {
                'drawings': item.get('drawings'),
                'hentai': item.get('hentai'),
                'neutral': item.get('neutral'),
                'porn': item.get('porn'),
                'sexy': item.get('sexy'),
            }
            serialized_dataList.update(serialized_item)

        log.debug("response====="+str(serialized_dataList))
        return serialized_dataList
    
    def AccDelete(payload)->AccMasterStatus:
        log.info(str(payload))
        AccMasterDb.delete(payload.accMasterId)
        status=AccDataGrpDb.deleteMany({"accMasterId":payload.accMasterId})
        status = AccSafetyDb.deleteMany({"accMasterId":payload.accMasterId})
        status = FmConfigGrpDb.deleteMany({"accMasterId":payload.accMasterId})
        status = AccTemplateMap.deleteMany({"accMasterId":payload.accMasterId})
        obj=AccMasterStatus
        obj.status=str(status)
        return obj 
     
    def DataEntityDelete(payload)->AccMasterStatus:
        log.info(str(payload))
        print (str(payload))
        x=AccDataGrpDb.delete(payload.RecogId, payload.accMasterId) #Acc Data Delete Bugfix
        obj=AccMasterStatus
        obj.status=str(x)
        return obj  
    def DataEntityAdd(payload)->AccMasterStatus:
        log.info(str(payload))
        ustatus="True"
        for data in payload.dataGrpList:
            status=AccDataGrpDb.create({"Did":data,"Aid":payload.accMasterId})
            if(status=="False"):
                ustatus="False"
   
        obj=AccMasterStatus
        obj.status=ustatus
        return obj
    
    def SafetyUpdate(payload)->AccMasterStatus:
        log.info(str(payload))
        # ustatus="True"
        status=AccSafetyDb.update({"accMasterId":payload.accMasterId},{payload.parameters:payload.value})
        obj=AccMasterStatus
        obj.status=str(status)
        return obj
    
    def setEncryption(payload)->AccMasterStatus:
        log.info(str(payload))
        query = {"accMasterId":payload.accMasterId,"dataRecogGrpId":payload.dataRecogGrpId}
        x= AccDataGrpDb.update(query,{"isHashify":payload.isHashify})

        # print("x========",x)
        obj=AccMasterStatus
        obj.status=str(x)
        return obj
    


    def ThresholdScoreUpdate(payload) ->AccThresholdScoreResponse:

        # log.info(str(payload))
        try:
            log.info(str(payload))
            value={"ThresholdScore":payload.thresholdScore}
            print(value)
            status=AccMasterDb.update(payload.accMasterId,value)
            obj=AccThresholdScoreResponse
            obj.status=str(status)
            return obj
        except Exception as e:
            log.info(str(e))
            obj=AccThresholdScoreResponse
            obj.status="False"
            return obj

    


class DataLOader:
    def loader()->AccMasterStatus:
        try:
            recog_list=os.getenv("RECOG_LIST")

            # print(recog_list)
            recog_list=json.loads(recog_list)
            # if(os.path.exists("PreDefinedRecg.csv")):
            # df=pd.read_csv("/responsible-ai-admin/src/rai_admin/service/PreDefinedRecg.csv")
            # col=df.columns
            # print([str(ele) for ele in df[col[0]]])
            # recog_list.extend(df[col[0]])
            log.info("Recognizers:"+str(recog_list))
            datalist=RecogDb.findall({"RecogName":{"$in":recog_list}})
            # print(datalist)

            if(len(datalist)!=len(recog_list)):
                for i in recog_list:
                    localTime=time.time()
                    RecogDb.mycol.update_one({"RecogName":i},{"$setOnInsert":{"_id":localTime,
            "RecogId":localTime,
            "supported_entity":i,
            "RecogType":"Pattern",
            "isEditable":"No",
            "Score":0.0,
            "Context":"",
            "isPreDefined":"Yes",
            "isActive":"Y",
            "isCreated":"Completed",
            "CreatedDateTime": datetime.now(),
            "LastUpdatedDateTime": datetime.now()
        }}, True )
            obj=AccMasterStatus
            obj.status="true"        
            return obj
        except Exception as e:
            log.info(str(e))
            obj=AccMasterStatus
            obj.status="false"
            return obj
        

    def fillApi(payload)->AccMasterStatus:
         try:
            log.info(str(payload))
            # print("Inside Fill Api====")
            acc=ConfigApiDb.findall({"ApiName":payload.ApiName})
            # print("acccc===",acc)
            value={"Name":payload.ApiName,"Ip":payload.ApiIp,"port":payload.ApiPort}
            if(len(acc)>0):
                obj=AccMasterStatus
                x=ConfigApiDb.update(acc[0]._id,value)
                print(f"Updated document with id: {acc[0]._id}")  # Print the id of the updated document
                # print("x=====",x)
                obj.status="Created"
                return obj

            accId=ConfigApiDb.create(value)
            print(f"Inserted new document with id: {accId}")
            # print("accid====",accId)
            if(accId > 0):
                status=True
            # for ptrn in payload.ptrnList:
            #     ptrnValue={"Aid":accId,"Pid":float(ptrn)}
                # AccPtrnDb.create(ptrnValue)
            # status="False"
            # for data in payload.dataGrpList:
            #     grpValue={"Aid":accId,"Did":float(data)}
            #     status=AccDataGrpDb.create(grpValue)

            obj=AccMasterStatus
            obj.status=status
            return obj
         except Exception as e:
            log.info(str(e))
            obj=AccMasterStatus
            obj.status="False"
            return obj

        
  

    def loadApi()->ConfigApiResponse:
        response=ConfigApiDb.findall({})

        res={}
        for i in response:
            if i.ApiPort is None :
                d = {i.ApiName:i.ApiIp}
            else:
                d = {i.ApiName:i.ApiIp+':'+i.ApiPort}
            res.update(d)
            
        obj=ConfigApiResponse() # Instantiate the ConfigApiResponse object
        obj.result=res
        return obj
    
    def updateApi(payload: ConfigApiUpdate) -> AccMasterStatus:
        try:
            # Define an empty dictionary
            payload_dict = {}
            # Add ApiName to the dictionary
            payload_dict['ApiName'] = payload.ApiName
            # If ApiIp is not None, add it to the dictionary
            if payload.ApiIp is not None:
                payload_dict['ApiIp'] = payload.ApiIp
                
            # If ApiPort is not None, add it to the dictionary
            if payload.ApiPort is not None:
                payload_dict['ApiPort'] = payload.ApiPort
            
            #print(payload_dict, "payload_dict check")
            # Find the document to update
            acc = ConfigApiDb.findall({"ApiName": payload_dict['ApiName']})
            #print(acc, "acc check") 
            if len(acc) > 0:
                # Update the document
                ConfigApiDb.update(acc[0]._id, payload_dict)
                #print(f"Updated document with id: {acc[0]._id}")  # Print the id of the updated document
                obj = AccMasterStatus
                obj.status = "success"
            else:
                #print("Document not found")
                obj = AccMasterStatus
                obj.status = "Not Found"
            return obj
        except Exception as e:
            log.info(str(e))
            obj = AccMasterStatus
            obj.status = "False"
            return obj

    def deleteApi(payload: ConfigApiDelete) -> AccMasterStatus:
        try:
            # Define an empty dictionary
            payload_dict = {}
           
            # Add ApiName to the dictionary
            payload_dict['ApiName'] = payload.ApiName
            #print(payload_dict, "payload_dict check")
            
            # Find the document to delete
            acc = ConfigApiDb.findall({"ApiName": payload_dict['ApiName']})
            if len(acc) > 0:
                # Delete the document
                ConfigApiDb.delete(acc[0]._id)
                #print(f"Deleted document with id: {acc[0]._id}")  # Print the id of the deleted document
                obj = AccMasterStatus
                obj.status = "success"
            else:
                obj = AccMasterStatus
                obj.status = "Not Found"
            return obj
        except Exception as e:
            log.info(str(e))
            obj = AccMasterStatus
            obj.status = "False"
            return obj
    



    
                  

class PrivacyData:
    def getDataList(payload)->AccPrivacyResponse:
        accName=None
        # print("==============",payload)
        if(payload.portfolio!=None):
            payload=AttributeDict(payload)
            query={"portfolio":payload.portfolio,"account":payload.account}
            # print(query)
            accMasterid=AccMasterDb.findall(query)
            if(len(accMasterid)==0):
                obj=AccPrivacyResponse
                obj.datalist=([],[],[],[],[],[])
                return obj
            # print(accMasterid.accMasterId)

            accName=accMasterid[0].accMasterId  
            thresholdScore=  accMasterid[0].ThresholdScore     

        datalsit=[]
        newEntityType=[]
        preEntity=[]
        recogList=[]
        encrList=[]

        # score=[]
        if(accName!=None):
            # print("=====",accName)
            # accMasterid=AccMasterDb.findall({"accMasterName":accName})[0]
            accdata=AccDataGrpDb.findall({"accMasterId":accName})
            for i in accdata:
                record= RecogDb.findall({"RecogId":i.dataRecogGrpId})
                if(len(record)>0):
                    # record=AttributeDict(record)
                    recogList.append(record[0])
                    if(i.isHashify==True):
                        encrList.append(record[0].RecogName)
                    if(record[0].isPreDefined=="No"):
                        newEntityType.append(record[0].RecogName)
                        datalsit.append(EntityDb.mycol.distinct("EntityName",{"RecogId":i.dataRecogGrpId}))
                    else:
                        preEntity.append(record[0].RecogName)    
            # entityType=
        else:
            recogList=RecogDb.findall({})
        # print(newEntityType)
        # print(preEntity)         
        # print(datalsit)
        # print(recogList)
        obj=AccPrivacyResponse
        obj.datalist=(newEntityType,datalsit,preEntity,recogList,encrList,[thresholdScore])
        return obj
    
    
    def getEntitiesList():
        try:
            recogList=RecogDb.findall({"isPreDefined":"No"})
            # rec = {}
            json_file_path = "recogList.json"
            for i in recogList:
                recValue=EntityDb.mycol.distinct("EntityName",{"RecogId":i.RecogId})
                # EntityDb.findall({"RecogId":i.RecogId})
                i.update({"EntityValue":recValue})
                del i["LastUpdatedDateTime"]
                del i["CreatedDateTime"]
                # print(i)
           
            # print("recogList_dict===",recogList_dict)
            with open(json_file_path, 'w') as json_file:
                json.dump(recogList, json_file)
            json_file=open(json_file_path)
            print("recogList saved to recogList.json")
            response = Response(content=json_file.read(), media_type="application/json")
            response.headers["Content-Disposition"] = "attachment; filename="+json_file_path
            
            return response
        except Exception as e:
            log.info(str(e))
            return {"message": "Error in getting Entities List"}
            

class SafetyData:
    def getDataList(payload)->AccSafetyParameterResponse :
        # accName=None
        payload=AttributeDict(payload)
        if(payload.portfolio!=None and payload.account!=None) :
            
            query={"portfolio":payload.portfolio,"account":payload.account}
            accMasterid=AccMasterDb.findall(query)
            if(len(accMasterid)==0):
               return None
            acc=accMasterid[0].accMasterId
            print(acc)
            dataList=AccSafetyDb.findall({"accMasterId":acc})
            obj=AccSafetyParameterResponse
            print(dataList)
            if(len(dataList)==0):
                obj.safetyParameter=[]
            else:

                obj.safetyParameter=[dataList[0]]
             
            # obj=AccSafetyParameterResponse
            # obj.accMasterId=dataList[0].accMasterId
            # obj.drawings=dataList[0].drawings
            # obj.hentai=dataList[0].hentai
            # obj.neutral=dataList[0].neutral
            # obj.porn=dataList[0].porn
            # obj.sexy=dataList[0].sexy

            # print("obj====",obj)
            return obj

        # print("==============",payload


class OpenAI:
    def setOpenAI(payload)->OpenAIResponse:
         try:
            log.info(str(payload))
            # print("Inside Fill Api====")
            query={"role":payload.role}

            # print("query====",query)
            acc=OpenAIDb.findall(query)  #role
            # print("acc=======",acc)
            value={"isOpenAI":payload.isOpenAI,"role":payload.role}
            # value={"isOpenAI":payload.isOpenAI,"selfReminder":payload.selfReminder,"role":payload.role}
            if(len(acc)==0):
                accId=OpenAIDb.create(value)
                # print("acccc===",accId)
            else:
                x=OpenAIDb.update(acc[0]._id,value)
                # print("x======",x)
            # print("acccc===",acc)
            
            
          
                
            # print("x======",x)
            status="Success"
            temp=OpenAIDb.findall(query)

            obj=OpenAIResponse
            # obj.status=status
            obj.isOpenAI = str(temp[0].isOpenAI)
            obj.selfReminder = str(temp[0].selfReminder)
            obj.goalPriority = str(temp[0].goalPriority)
            obj.role = temp[0].role
            return obj
         except Exception as e:
            log.info(str(e))
            obj=OpenAIResponse
            obj.isOpenAI = "Fail"
            obj.selfReminder = "Fail"
            obj.goalPriority = "Fail"
            obj.role = "Fail"
            # obj.status="Fail"
            return obj
        
    def setReminder(payload)->OpenAIResponse:
         try:
            log.info(str(payload))
            # print("Inside Fill Api====")
            query={"role":payload.role}

            # print("query====",query)
            acc=OpenAIDb.findall(query)  #role
            # print("acc=======",acc)
            value={"selfReminder": payload.selfReminder,"role":payload.role}
            # value={"isOpenAI":payload.isOpenAI,"selfReminder":payload.selfReminder,"role":payload.role}
            if(len(acc)==0):
                accId=OpenAIDb.create(value)
                # print("acccc===",accId)
            else:
                # x=OpenAIDb.update(acc[0]._id,value)
                OpenAIDb.mycol.update_one({"role":payload.role}, {"$set": {"selfReminder": payload.selfReminder}}, upsert=True)
                # print("x======",x)
            # print("acccc===",acc)
        
            # print("x======",x)
            status="Success"
            temp=OpenAIDb.findall(query)

            obj=OpenAIResponse
            # obj.status=status
            obj.isOpenAI = str(temp[0].isOpenAI)
            obj.selfReminder = str(temp[0].selfReminder)
            obj.goalPriority = str(temp[0].goalPriority)
            obj.role = temp[0].role
            
            return obj
         except Exception as e:
            log.info(str(e))
            obj=OpenAIResponse
            obj.isOpenAI = "Fail"
            obj.selfReminder = "Fail"
            obj.goalPriority = "Fail"
            obj.role = "Fail"
            # obj.status="Fail"
            return obj

     
    def setGoalPriority(payload) -> OpenAIResponse:
         try:
            log.info(str(payload))
            # print("Inside Fill Api====")
            query={"role":payload.role}

            # print("query====",query)
            acc=OpenAIDb.findall(query)  #role
            # print("acc=======",acc)
            value={"goalPriority": payload.goalPriority,"role":payload.role}
            # value={"isOpenAI":payload.isOpenAI,"selfReminder":payload.selfReminder,"role":payload.role}
            if(len(acc)==0):
                accId=OpenAIDb.create(value)
                # print("acccc===",accId)
            else:
                # x=OpenAIDb.update(acc[0]._id,value)
                OpenAIDb.mycol.update_one({"role":payload.role}, {"$set": {"goalPriority": payload.goalPriority}}, upsert=True)
                # print("x======",x)
            # print("acccc===",acc)
        
            # print("x======",x)
            status="Success"
            temp=OpenAIDb.findall(query)

            obj=OpenAIResponse
            # obj.status=status
            obj.isOpenAI = str(temp[0].isOpenAI)
            obj.selfReminder = str(temp[0].selfReminder)
            obj.goalPriority = str(temp[0].goalPriority)
            obj.role = temp[0].role
            
            return obj
         except Exception as e:
            log.info(str(e))
            obj=OpenAIResponse
            obj.isOpenAI = "Fail"
            obj.selfReminder = "Fail"
            obj.goalPriority = "Fail"
            obj.role = "Fail"
            # obj.status="Fail"
            return obj

    def getOpenAI()->OpenAIStatus:

    
        # value={"isOpenAI":bool("true")}
        # temp = OpenAIDb.findall({})
        # if(len(temp)==0):
        #     accId=OpenAIDb.create(value)
        #     print(accId)
        # else:
        #      pass

        temp=AuthorityDb.findall({})
        print(temp)
        for i in temp:
            # print("i.name===",i.name)
            query={"role":i.name}
            temp_role=OpenAIDb.findall(query)
            if(len(temp_role)== 0):
                value={"isOpenAI":False,"selfReminder":False,"goalPriority":False,"role":i.name}
                accId=OpenAIDb.create(value)
                # print("acccc===",accId)
            else:
                pass


        

        response=OpenAIDb.findall({})
        res=[]
        for i in response:
            reminder=False
            goal=False
            if(i.selfReminder):
                reminder=i.selfReminder

            if(i.goalPriority):
                goal=i.goalPriority
                
            d = {"isOpenAI":i.isOpenAI,"selfReminder":reminder,"goalPriority":goal,"role":i.role}
            res.append(d)
     
        obj=OpenAIStatus
        obj.result=res
    
        return obj
    

    def CheckRole(payload)->OpenAIRoleResponse:

        try:
            obj=OpenAIRoleResponse
            query={"role":payload.role}
            # temp_role=OpenAIDb.findall(query)
            temp=OpenAIDb.findall(query)
            print("temp====",temp)
            if(len(temp)>0):

                
                # obj.status=status
                obj.isOpenAI = str(temp[0].isOpenAI)
                obj.selfReminder = str(temp[0].selfReminder)
                obj.goalPriority = str(temp[0].goalPriority)
                
                
                
            
            print("obj====",obj)
            return obj
        except Exception as e:
            log.info(str(e))
            obj=OpenAIRoleResponse
            obj.isOpenAI = "Fail"
            
                # obj.status="Fail"
            return obj


        # return obj
    




class Role:

    def getRole()->AuthorityResponse:
        response=AuthorityDb.findall({})
        # print("response=====",response)
        res=[]
        # print(response)
        for i in response:
            # d = {i.ApiName:i.ApiIp+':'+i.ApiPort}
            res.append(i.name)


        # print("res=====",res)

        
        obj=AuthorityResponse
        obj.result=response
    
        return obj

class FMConfig:
    def fmEntry(payload)->FMConfigEntry:
        try:
            log.info(str(payload))
            fm=AccMasterDb.findall({"account":payload.AccountName,"portfolio":payload.PortfolioName})
            print("accc=====",fm)
            accId = fm[0]['accMasterId']
            status=False
            # fmAccountDtl = AccMasterDb.findall({"AName":payload.PortfolioName,"SName":payload.AccountName})
            # print("Account Details====",fmAccountDtl)
            # fm = FmConfigDb.findall({"AccountName":payload.AccountName,"PortfolioName":payload.PortfolioName}) 
            if(len(fm)==0 ):
                obj=FMConfigEntry
                obj.status="False"
                return obj
            # value={"PName": payload.PortfolioName,"AName": payload.AccountName}
            # accountFmId= FmConfigDb.create(value)
            status = "False"
            FmConfig = FmConfigGrpDb.findall({"accMasterId":accId})
            if(len(FmConfig)>0):
                 obj=FMConfigEntry
                 obj.status="False"
                 return obj
            else:

                grpValue = {"Aid":accId,"MChecks":payload.ModerationChecks ,"OutputMChecks":payload.OutputModerationChecks,"MCThreshold": payload.ModerationCheckThresholds}
                log.info("for grp")
                status= FmConfigGrpDb.create(grpValue)
                log.info(str(status))

            obj=FMConfigEntry
            obj.status=str(status)
            return obj
        except Exception as e:
            log.info(str(e))
            obj=FMConfigEntry
            obj.status="False"
            return obj
        
    def fmAccEntry()->FmConfigResponse:
        FMConfig.ModerationChecksCreate()
        FMConfig.RestrictedTopicCreate()
        FMConfig.OutputModerationChecksCreate()
        
        response = AccMasterDb.findall({})
        print("Response====",response)
        obj=FmConfigResponse
        obj.fmList=response
        return obj
    def getFmGrpData(payload)->FmAccDataResponse:
        dataList= FmConfigGrpDb.findall({"accMasterId":payload.accMasterId})
        print("dataList====",dataList)
        if(len(dataList)==0):
            return None
        else:
            dataList=dataList[0]

        obj = FmAccDataResponse
        obj_ModerationChecks = FMGrpData(accMasterId=dataList.accMasterId,
                                      ModerationChecks=dataList.ModerationChecks,
                                      OutputModerationChecks=dataList.OutputModerationChecks,
                                      ModerationCheckThresholds=dataList.ModerationCheckThresholds,
                            )
        print("obj===",obj_ModerationChecks)
        obj.dataList=[obj_ModerationChecks]
        #res=[obj_ModerationChecks]
        return  obj
    def FmGrpUpdate(payload)->FmConfigUpdateStatus:
        try:
            print("moderationCgeckvalues==",payload.ModerationChecks)
            value={"ModerationChecks":payload.ModerationChecks,"OutputModerationChecks":payload.OutputModerationChecks,"ModerationCheckThresholds":payload.ModerationCheckThresholds.dict(),"LastUpdatedDateTime": datetime.now()}
            status= FmConfigGrpDb.update({"accMasterId":payload.accMasterId},value)
            obj=FmConfigUpdateStatus
            obj.status=str(status)
            return obj
        except Exception as e:
            log.info(str(e))
            obj=FmConfigUpdateStatus
            obj.status="False"
            return obj
    def FmConfigDelete(payload)->FmConfigUpdateStatus:
        log.info(str(payload))
        FmConfigDb.delete(payload.accMasterId)
        status=FmConfigGrpDb.deleteMany({"accMasterId":payload.accMasterId})
        obj=FmConfigUpdateStatus
        obj.status=str(status)
        return obj 
            
    def ModerationChecksCreate():
        value =  [
        "PromptInjection",
        "JailBreak",
        "Toxicity",
        "Piidetct",
        "Refusal",
        "Profanity",
        "RestrictTopic",
        "TextQuality",
        "CustomizedTheme",
        "Sentiment",
        "InvisibleText",
        "Gibberish",
        "BanCode"
       ]
        auth = list(ModerationChecksDb.findall({}))
        obj=FmConfigUpdateStatus
        if len(auth)==0:           
            obj.result= "true"
            for val in value:
                response = ModerationChecksDb.create({"Name": val})
                obj.result=response 
        return obj
    def RestrictedTopicCreate():
        value = [
        "Terrorism",
        "Explosives",
        "Nudity",
        "Sexual Content",
        "Cruelty",
        "Cheating",
        "Fraud",
        "Crime",
        "Hacking",
        "Security Breach",
        "Immoral",
        "Cyberattack",
        "Exam Misconduct",
        "Conspiracy",
        "Unethical",
        "Illegal",
        "Robbery",
        "Forgery",
        "Misinformation"
    ]
        auth = list(RestrictedTopic.findall({}))
        obj=FmConfigUpdateStatus
        if len(auth)==0:           
            obj.result= "true"
            for val in value:
                response = RestrictedTopic.create({"Name": val})
                obj.result=response 
        return obj
    def OutputModerationChecksCreate():
        value =  [
        "Toxicity",
        "Piidetct",
        "Refusal",
        "Profanity",
        "RestrictTopic",
        "TextQuality",
        "CustomizedTheme",
        "TextRelevance",
        "Sentiment",
        "InvisibleText",
        "Gibberish",
        "BanCode"
       ]
        auth = list(OutputModerationChecksDb.findall({}))
        obj=FmConfigUpdateStatus
        if len(auth)==0:           
            obj.result= "true"
            for val in value:
                response = OutputModerationChecksDb.create({"Name": val})
                obj.result=response 
        return obj
    # def ThemeTextCreate():
    #     value =  [
    #     "Text1",
    #     "Text2",
    #     "Text3"
    #    ]
    #     auth = list(ThemeText.findall({}))
    #     obj=FmConfigUpdateStatus
    #     if len(auth)==0:           
    #         obj.result= "true"
    #         for val in value:
    #             response = ThemeText.create({"Name": val})
    #             obj.result=response 
    #     return obj
    def getModerationChecks() -> ModerationCheckResponse:
        dataList = ModerationChecksDb.findall({})
        print("dataList====", dataList)
        res = [data.get('name', '') for data in dataList if data.get('name')]
        obj = ModerationCheckResponse(dataList=res)
        return obj
    def getRestrictedTopics() -> ModerationCheckResponse:
        dataList = RestrictedTopic.findall({})
        print("dataList====", dataList)
        res = [data.get('name', '') for data in dataList if data.get('name')]
        obj = ModerationCheckResponse(dataList=res)
        return obj
    def getThemeTexts() -> ModerationCheckResponse:
        dataList = ThemeText.findall({})
        print("dataList====", dataList)
        res = [data.get('name', '') for data in dataList if data.get('name')]
        obj = ModerationCheckResponse(dataList=res)
        return obj
    def getOutputModerationChecks() -> ModerationCheckResponse:
        dataList = OutputModerationChecksDb.findall({})
        print("dataList====", dataList)
        res = [data.get('name', '') for data in dataList if data.get('name')]
        obj = ModerationCheckResponse(dataList=res)
        return obj
    
    def getByAccPort(payload):
        fm = AccMasterDb.findall({"account":payload.AccountName,"portfolio":payload.PortfolioName})
        print(fm)
        if(len(fm)>0):
            id = fm[0]["accMasterId"]
            dataList= FmConfigGrpDb.findall({"accMasterId":id})[0]
            print("dataList====",dataList)
            obj = FmAccDataResponse
            obj_ModerationChecks = FMGrpData(accMasterId=dataList.accMasterId,
                                        ModerationChecks=dataList.ModerationChecks,
                                        OutputModerationChecks=dataList.OutputModerationChecks,
                                        ModerationCheckThresholds=dataList.ModerationCheckThresholds,
                                )
            print("obj===",obj_ModerationChecks)
            obj.dataList=[obj_ModerationChecks]
            return  obj
        else:
            obj = FmAccDataResponse
            obj.dataList=[]
            return obj
        
                


class SafetyParameter:
    def addSafetyParameter(payload)->AccountSafetyResponse:
        try:
            log.info(str(payload))
            acc=AccMasterDb.findall({"account":payload.account,"portfolio":payload.portfolio})
            print("accc=====",acc)
            accId = acc[0]['accMasterId']
            status=False
            if(len(acc)==0):
                obj=AccountSafetyResponse
                obj.status="False"
                return obj

            
            safetyConfig = AccSafetyDb.findall({"accMasterId":accId})
            if(len(safetyConfig)>0):
                 obj=AccountSafetyResponse
                 obj.status="False"
                 return obj
            else:
                value={"Aid":accId,"drawings":payload.drawings,"hentai":payload.hentai,"neutral":payload.neutral,"porn":payload.porn, "sexy": payload.sexy}  #skip
                rstatus=AccSafetyDb.create(value)
            print("status=====",rstatus)
            if(rstatus==True):
                status="Success"
            
            

            obj=AccountSafetyResponse
            obj.status=status
            return obj
        except Exception as e:
            log.info(str(e))
            obj=AccountSafetyResponse
            obj.status="False"
            return obj

        



        

    

    
from rai_admin.dao.DocDetailsDb import docDetailDb
from rai_admin.dao.FileStoreDb import fileStoreDb
from rai_admin.dao.CacheDetailDb import cacheDetailDb
import requests
from zipfile import ZipFile,is_zipfile
class RAG:
    def storeFile(payload):
        try:
            payload=AttributeDict(payload)

            userId=payload.userId
            file=payload.file
            docList=[]
            for docs in file:

                fileName=docs.filename
                print("filename===",fileName)
                # print("size",docs.size)

                filetype=docs.content_type
                print(type(docs))

                # fid=fileStoreDb.create(docs)
                # contents=docs.read()
                response = requests.post(url=azurebloburl, files={"file": (fileName, docs.file)}, data={"container_name": containername}, headers=None, verify=False)
                if response.status_code == 200:
                    print(response.text)
                    blobname_output = response.json()['blob_name']
                docid=docDetailDb.create({"userId":userId,"fileName":fileName, "azureblob":blobname_output,"type":filetype})
                docList.append(docid)


                # print(filetype)
            return docList
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            ExceptionDb.create({"UUID":request_id_var.get(),"function":"uploadFilesFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)
            # return docid
        
    def getFiles(payload):
        try:
            payload=AttributeDict(payload)
            files=docDetailDb.findall({"userId":payload.userId})
            print(files)
            return files
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            ExceptionDb.create({"UUID":request_id_var.get(),"function":"getFilesFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)
    
    def setCache(payload):
        try:
            payload=AttributeDict(payload)
            # print(payload)
            # f=fileStoreDb.findOne(payload.docid[0])
            # print(f)
            url=os.getenv("RAG_IP")+"/rag/v1/caching"
            # print(url)
            blobids=[]
            for ids in payload.docid:
                blobnames=docDetailDb.findall({"docId":float(ids)})
                print(blobnames)
                blobids.append(blobnames[0].azureblob)
            data={"blobname":blobids}
            # print(data)
            cacheList=cacheDetailDb.findall({"userId":payload.uid})
            # print(cacheDetailDb)
            if(len(cacheList)>0):
                RAG.delEmbedings({"eid":cacheList[0]._id})
                docDetailDb.mycol.update_many({"userId":payload.uid},{"$set":{"isCache":"N"}})
            res=requests.post(url,json=data)
            # print(res.json())
            
            payload.docid=[float(item) for item in payload.docid]
            print(payload.docid)
            docsRes=list(docDetailDb.mycol.find({"fileId":{"$in":payload.docid}},{"fileName":1,"_id":0}))
            # print(docsRes)
            cid=cacheDetailDb.create({"cacheId":res.json()[0],"uid":payload.uid,"ename":payload.ename,"fileList":docsRes})
            query={"userId":payload.uid,"fileId":{"$in":payload.docid}}
            # print(query)
            s=docDetailDb.mycol.update_many(query,{"$set":{"isCache":"Y"}})
            print(s.acknowledged)
            if (res.json()[1]!=0):
                cacheDetailDb.delete(res.json()[1])
            return cid
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            ExceptionDb.create({"UUID":request_id_var.get(),"function":"setCacheFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)
    
    def getEmbedings(payload):
        try:
            payload=AttributeDict(payload)

            url=os.getenv("RAG_IP")+"/rag/v1/checkCache"
            # print(url)
            res=requests.get(url).json()
            # print(res)
            if(len(res)==0):
                cacheDetailDb.mycol.delete_many({})
                docDetailDb.mycol.update_many({},{"$set":{"isCache":"N"}})

            cacheList=cacheDetailDb.findall({"userId":payload.userId})
            # print(cacheList)
            return cacheList
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            ExceptionDb.create({"UUID":request_id_var.get(),"function":"getEmbedingsFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)
    
    def delEmbedings(payload):
        try:        
            payload=AttributeDict(payload)
            url=os.getenv("RAG_IP")+"/rag/v1/removeCache"
            data={"id":payload.eid}
            print(data)
            res=requests.post(url,json=data)
            print(res.json())
            res=cacheDetailDb.delete(res.json())
            res=[str(res)]
            return res
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            ExceptionDb.create({"UUID":request_id_var.get(),"function":"delEmbedingsFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)
        
    def delFiles(payload):
        try:        
            payload=AttributeDict(payload)
            # url=os.getenv("RAG_IP")+"/rag/v1/removeCache"
            isCache=docDetailDb.findall({"fileId":payload.docid,"isCache":"Y"})
            msg="Document Deleted Successfully"
            if(len(isCache)>0):
                emb=RAG.getEmbedings(payload)
                # print(emb)
                dres=RAG.delEmbedings({"eid":emb[0]._id})
                # print(dres)
                msg="Document and Embedding associated with it deleted successfully"
            # print(isCache)
            fres=fileStoreDb.delete(payload.docid)
            # if(fres):
            # print(fres)
            res=docDetailDb.delete({"fileId":payload.docid})
            # res=requests.post(url,json=data)
            # print(res)
            # res=cacheDetailDb.delete(res.json())
            # print(res)
            return msg
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            ExceptionDb.create({"UUID":request_id_var.get(),"function":"delDocFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            raise Exception(e)
        
    
        
        
        
        
        
        
        
