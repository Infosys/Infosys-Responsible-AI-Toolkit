"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from collections import defaultdict
from rai_admin.config.logger import CustomLogger
from rai_admin.dao.AWSCredDb import AWSCredDb
from rai_admin.mappers.AWSMapper import *
import datetime

log = CustomLogger()
class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    

class AWSService:
    def createCreds(payload:AWSReq)->AWSStatus:
        try:
            log.info(f"createCreds: {payload}")
            obj=AWSStatus
            if(len(AWSCredDb.findall({"credName":payload.credName}))>0):
                obj.status="Creds exists for user {}".format(str(payload.id))
                return obj
            res=AWSCredDb.create(payload)
            log.debug("createCred status: "+str(res))   
            obj.status=str(res)
            return obj
        except Exception as e:
            log.error(str(e))
            obj=AWSStatus
            obj.status="False"
            return obj
        

    
    def getAWSCreds(payload)->AWSRes:
        try:
            log.info("getAWSCreds")
            obj=AWSCredDb.findall({"credName":payload['credName']})[0]
            return obj
        except Exception as e:
            log.error(str(e))
            return e      
        
    
    def updateCreds(payload:CredUpdate)->AWSStatus:
        try:
            log.info(f"updateCreds: {payload}")
            obj=AWSStatus
            res=AWSCredDb.findall({"credName":payload.credName})
            if(len(res)==0):
                obj.status="Creds dosent exists"
                return obj
            updateCred = AWSCredDb.update(res[0]['_id'],{"awsAccessKeyId":payload.awsAccessKeyId,
                                                        "awsSecretAccessKey":payload.awsSecretAccessKey,
                                                        "awsSessionToken":payload.awsSessionToken,
                                                        "creationTime":datetime.datetime.now()})
            obj.status=str(updateCred)
            return obj
        except Exception as e:
            log.error(str(e))
            obj=AWSStatus
            obj.status="False"
            return obj
        
    def deleteTemplate(id)->AWSStatus:
        try:
            log.info(f"createTemplate: {id}")
            obj=AWSStatus
            res=AWSCredDb.findall({"id":float(id)})
            if(len(res)==0):
                obj.status="Creds dosent exists"
                return obj
            delcred = AWSCredDb.delete(float(id))
            log.debug("DeleteCred status: "+str(delcred))
            obj.status=str(delcred)
            return obj
        except Exception as e:
            log.error(str(e))
            obj=AWSStatus
            obj.status="False"
            return obj