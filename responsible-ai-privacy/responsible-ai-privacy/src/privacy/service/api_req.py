import os
from dotenv import load_dotenv
from privacy.config.logger import CustomLogger,request_id_var
log = CustomLogger()
from privacy.service.__init__ import AttributeDict,admin_par,error_dict
import time
import requests
load_dotenv()
class ApiCall:
    @staticmethod
    def request(data):
        try: 
            if(os.getenv("ADMIN_CONNECTION")=="False" or os.getenv("ADMIN_CONNECTION")=="false"):
           
                return 404
            payload=AttributeDict({"portfolio":data.portfolio,"account":data.account})
            api_url = os.getenv("PRIVADMIN_API")
            aurl=api_url
            log.debug("Calling Admin Api  ======")
            response1 = requests.post(
                url=aurl
                , headers={'Content-Type': "application/json",
                           'accept': "application/json"}
                , json=payload
                )
            entity_type,datalist,pre_entity,records,encryption_list,score_treshold=response1.json()["datalist"]
            log.debug("data fetched")
            if(len(records)==0):
                return None
            log.debug("entity_type="+str(entity_type))
            admin_par[request_id_var.get()]={"encryption_list":encryption_list,"records":records,"score_treshold":score_treshold[0]}
            return(entity_type,datalist,pre_entity)
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"ApiRequestFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
            
            return Exception(e)
  
    @staticmethod
    def get_record(name):
        record=[ele for ele in admin_par[request_id_var.get()]["records"] if ele["RecogName"]==name][0]
        return record
    @staticmethod
    def del_admin_list():
        id=request_id_var.get()
        if id in admin_par:
                del admin_par[id]
