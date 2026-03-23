import os
from dotenv import load_dotenv
from privacy.config.logger import CustomLogger,request_id_var
log = CustomLogger()
from privacy.service.__init__ import *
import time
import requests
load_dotenv()
class ApiCall:
    # records=[]
    # encryptionList=[]
    # scoreTreshold=    0.0
    def request(data):
        try:
            # admin_par[request_id_var]={}
            # raise Exception() 
            # print("==================",os.getenv("ADMIN_CONNECTION"))
            # print("==================",os.getenv("ADMIN_CONNECTION")=="False")
            
            if(os.getenv("ADMIN_CONNECTION")=="False" or os.getenv("ADMIN_CONNECTION")=="false"):
           
                # print("--------------------------------------------------------------")
                return 404
            # ApiCall.records.clear()
            # ApiCall.encryptionList.clear()
            payload=AttributeDict({"portfolio":data.portfolio,"account":data.account})
            
            # payload={"accName":"Infosys","subAccName":"Impact"}
            api_url = os.getenv("PRIVADMIN_API")
            
            # print(api_url)
            t=time.time()
            
            # aurl="http://10.66.155.13:30016/api/v1/rai/admin/PrivacyDataList"
            aurl=api_url
            # log.debug(aurl)
            # log.debug(str(type(aurl)))
            log.debug("Calling Admin Api  ======")
            # log.debug("api payload:"+str(payload))
            # print(payload)
            response1 = requests.post(
                url=aurl
                , headers={'Content-Type': "application/json",
                           'accept': "application/json"}
                , json=payload
                )
            # print(response1.content[0])
            # response1=httpx.post(aurl, json=payload)
            # response1=httpx.post('http://10.66.155.13:30016/api/v1/rai/admin/PrivacyDataList', json=payload)
            # log.debug("response="+str(response1))
            # log.debug("response11="+str(response1.text))
            # response1=PrivacyData.getDataList(payload)
            entityType,datalist,preEntity,records,encryptionList,scoreTreshold=response1.json()["datalist"]
            # print("=========================",time.time()-t)
            log.debug("data fetched")
            if(len(records)==0):
                return None
            log.debug("entityType="+str(entityType))
            admin_par[request_id_var.get()]={"encryptionList":encryptionList,"records":records,"scoreTreshold":scoreTreshold[0]}
            # print("===============",len(admin_par))
            # ApiCall.encryptionList.extend(encryptionList)
            # ApiCall.records.extend(records)
            # ApiCall.scoreTreshold=scoreTreshold[0]
            return(entityType,datalist,preEntity)
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            # print("------------------------------",request_id_var.get())
            # ExceptionDb.create({"UUID":request_id_var.get(),"function":"ApiRequestFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"ApiRequestFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            # print("err",error_dict,error_dict[request_id_var.get()])
            
            return Exception(e)
            # raise Exception(e)

  
        # record=[ele for ele in records if ele.RecogName=="PASSPORT"][0]  
    
    def getRecord(name):
        # log.debug("name="+str(name))
        # log.debug("ApiCall.records="+str(ApiCall.records))
        record=[ele for ele in admin_par[request_id_var.get()]["records"] if ele["RecogName"]==name][0]
        return record
    def delAdminList():
        id=request_id_var.get()
        if id in admin_par:
                del admin_par[id]
