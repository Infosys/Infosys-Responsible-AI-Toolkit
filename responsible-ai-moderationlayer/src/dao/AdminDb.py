'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import os
import pymongo
import datetime
# from dotenv import load_dotenv
from config.logger import CustomLogger,request_id_var
# import sys
# load_dotenv()
import json
import requests
import hvac
import urllib.parse
# import psycopg2

from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
import traceback
from sqlalchemy import create_engine
from sqlalchemy import text
import json
import time

log = CustomLogger()

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
request_id_var.set("Startup")

    
global conn
conn=None
try:
    vault = os.getenv("ISVAULT")
    if vault=="True":
        vaultname = os.getenv("VAULTNAME")
        if vaultname=="HASHICORP":
            payload = {'role_id': os.getenv("APP_VAULT_ROLE_ID"),'secret_id': os.getenv("APP_VAULT_SECRET_ID")}
            r = requests.post(os.getenv("APP_VAULT_URL")+"/v1/auth/approle/login",data=json.dumps(payload))
            r.raise_for_status()
            data = r.json()
            
            token=data["auth"]["client_token"]
            log.info("Vault token generator")
            
            client = hvac.Client(url=os.getenv("APP_VAULT_URL"),token=token)
            secret = client.secrets.kv.v2.read_secret_version(
                path=os.getenv("APP_VAULT_PATH"), 
                mount_point=os.getenv("APP_VAULT_BACKEND"),
            )["data"]["data"]
            print("secret is here -> ",secret)
            dbname = os.getenv("APP_MONGO_DBNAME")
            encoded_password = urllib.parse.quote(secret[os.getenv("APP_VAULT_KEY_MONGOPASS")], safe='')
            
            if os.getenv("DBTYPE")=="mongo":
                myclient=pymongo.MongoClient("mongodb://"+secret[os.getenv("APP_VAULT_KEY_MONGOUSER")]+":"+encoded_password+"@"+os.getenv("APP_MONGO_HOST")+"/"+"?authMechanism=SCRAM-SHA-256&authSource="+dbname)
                log.info(f"myclient is here -> {myclient}")
            
            elif os.getenv("DBTYPE")=="psql": 
                #-------- Migrating to SQLAlchemy from Psycopg2 due to IP Check issue  -----#
                HOST = os.getenv("APP_MONGO_HOST")
                engine = create_engine(f'postgresql://{secret[os.getenv("APP_VAULT_KEY_MONGOUSER")]}:{secret[os.getenv("APP_VAULT_KEY_MONGOPASS")]}@{HOST.split(":")[0]}:{HOST.split(":")[1]}/{dbname}')
                create_table_query = '''
                    CREATE TABLE IF NOT EXISTS ModerationResult (
                        id VARCHAR(50) PRIMARY KEY,
                        payload JSONB
                    )
                '''
                create_log_table_query = '''
                    CREATE TABLE IF NOT EXISTS log_db (
                        id VARCHAR(50) PRIMARY KEY,
                        error JSONB
                    )
                '''
                with engine.connect() as con:
                    con.execute(text(create_table_query))
                    con.execute(text(create_log_table_query))
                    con.commit()
            
            else:
                myclient=pymongo.MongoClient("mongodb://"+secret[os.getenv("APP_VAULT_KEY_MONGOUSER")]+":"+encoded_password+"@"+os.getenv("APP_MONGO_HOST")+"/"+"?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName="+"@"+secret[os.getenv("APP_VAULT_KEY_MONGOUSER")])
                         
        elif vaultname=="AZURE":
            log.info("AZURE VaultIntegration Starts")
            credential = ClientSecretCredential(
                tenant_id = os.getenv("AZURE_VAULT_TENANT_ID"),
                client_id = os.getenv("AZURE_VAULT_CLIENT_ID"),
                client_secret = os.getenv("VAULT_SECRET")
                )
        
            sc = SecretClient(vault_url = os.getenv("KEYVAULTURL"), credential=credential)
            
            try:
                DB_USERNAME = sc.get_secret(os.getenv("APP_VAULT_KEY_MONGOUSER")).value
                DB_PWD = sc.get_secret(os.getenv("APP_VAULT_KEY_MONGOPASS")).value
                log.info("Retrived username and password")

            except Exception as e:
                log.error("error in Azure vault")
                traceback.print_exc()

            dbname = os.getenv("APP_MONGO_DBNAME")
            encoded_password = urllib.parse.quote(DB_PWD, safe='')
            if os.getenv("DBTYPE")=="mongo":
                myclient=pymongo.MongoClient("mongodb://"+DB_USERNAME+":"+encoded_password+"@"+os.getenv("APP_MONGO_HOST")+"/"+"?authMechanism=SCRAM-SHA-256&authSource="+dbname)
            
            elif os.getenv("DBTYPE")=="psql":
                #-------- Migrating to SQLAlchemy from Psycopg2 due to IP Check issue  -----#
                HOST = os.getenv("APP_MONGO_HOST")
                engine = create_engine(f'postgresql://{sc.get_secret(os.getenv("APP_VAULT_KEY_MONGOUSER")).value}:{sc.get_secret(os.getenv("APP_VAULT_KEY_MONGOPASS")).value}@{HOST.split(":")[0]}:{HOST.split(":")[1]}/{dbname}')
                create_table_query = '''
                    CREATE TABLE IF NOT EXISTS ModerationResult (
                        id VARCHAR(50) PRIMARY KEY,
                        payload JSONB
                    )
                '''
                create_log_table_query = '''
                    CREATE TABLE IF NOT EXISTS log_db (
                        id VARCHAR(50) PRIMARY KEY,
                        error JSONB
                    )
                '''
                with engine.connect() as con:
                    con.execute(text(create_table_query))
                    con.execute(text(create_log_table_query))
                    con.commit()

            else:
                myclient=pymongo.MongoClient("mongodb://"+DB_USERNAME+":"+encoded_password+"@"+os.getenv("APP_MONGO_HOST")+"/"+"?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName="+"@"+DB_USERNAME)

    else:
        dbname = os.getenv("APP_MONGO_DBNAME")
        if os.getenv("DBTYPE")=="mongo":
            myclient = pymongo.MongoClient(os.getenv("MONGO_PATH"))

        elif os.getenv("DBTYPE")=="psql": 
            #-------- Migrating to SQLAlchemy from Psycopg2 due to IP Check issue  -----# 
            HOST = os.getenv("APP_MONGO_HOST")
            engine = create_engine(f'postgresql://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PWD")}@{HOST.split(":")[0]}:{HOST.split(":")[1]}/{dbname}')
            create_table_query = '''
                    CREATE TABLE IF NOT EXISTS ModerationResult (
                        id VARCHAR(50) PRIMARY KEY,
                        payload JSONB
                    )
                '''
            create_log_table_query = '''
                    CREATE TABLE IF NOT EXISTS log_db (
                        id VARCHAR(50) PRIMARY KEY,
                        error JSONB
                    )
                '''
            with engine.connect() as con:
                con.execute(text(create_table_query))
                con.execute(text(create_log_table_query))
                con.commit()

        elif os.getenv("DBTYPE")=="cosmos":  
            cosmos_path = os.getenv("COSMOS_PATH")
            myclient=pymongo.MongoClient(cosmos_path)
            log.info(f"client : {myclient}")
        
except Exception as e:
    log.error("error in vault")
    log.error(str(traceback.extract_tb(e.__traceback__)[0].lineno),e)

class DB:
    def connect():
        try:
            # myclient = pymongo.MongoClient(os.getenv("MONGO_PATH")) 
            # mydb = myclient[os.getenv("APP_MONGO_DBNAME")]
            mydb = myclient[dbname]
            log.info(f"IS myclient from localDB : {myclient}")
            log.info(f"dbname : {dbname}")
            return mydb
        except Exception as e:
            log.error("error in DB connection")
            log.error(str(traceback.extract_tb(e.__traceback__)[0].lineno),e)
            

if conn == None and os.getenv("DBTYPE")!="False":
    mydb=DB.connect()

class ProfaneWords:
    def findOne(id):
        try:
            mycol = mydb["ProfaneWords"]
            values=ProfaneWords.mycol.find({"_id":id},{})[0]
            # print(values)
            values=AttributeDict(values)
            return values
        except Exception as e:
            log.error("Error occured in ProfaneWords")
            log.error(f"Exception: {e}")
    
class feedbackdb:
    # feedback_collection = mydb["feedback"]
    def create(value):
        try:
            feedback_collection = mydb["feedback"]
            PtrnRecogCreatedData = feedbackdb.feedback_collection.insert_one(value)
            print("PtrnRecogCreatedData.acknowledged",PtrnRecogCreatedData.acknowledged)
            return PtrnRecogCreatedData.acknowledged
        except Exception as e:
            log.error("Error occured in feedbackdb")
            log.error(f"Exception: {e}")

class Results:
    # mycol = mydb["moderationtelemetrydata"]
    if conn == None and os.getenv("DBTYPE")!="False":
        logdb=mydb["Logdb"]
        mycol = mydb["Results"]
        mycol2 = mydb["Results"]
    # mycol2 = mydb["Resultswithfeedback"]
    def findOne(id):
        try:
            print("came inside findOne")
            print(Results.mycol)
            values=Results.mycol.find({"_id":id},{})[0]
            print("values -------> ",values)
            values=AttributeDict(values)
            return values
        except Exception as e:
            log.error("Error occured in Results findOne")
            log.error(f"Exception: {e}")
    def findall(query):
        try:
            value_list=[]
            values=Results.mycol.find(query,{})
            for v in values:

                v=AttributeDict(v)
                value_list.append(v)
            return value_list
        except Exception as e:
            log.error("Error occured in Results findall")
            log.error(f"Exception: {e}")

    def create(value,id,portfolio, accountname,user=None,lotnumber=None):
        request_id_var.set(id)
        try:
            if type(value) is not dict:
                value=json.loads(value.json())
            id=value["uniqueid"]
            if user:
                mydoc={"_id":id , "created":value["created"],"user":user,"lotnumber":lotnumber,"portfolio":portfolio,"accountname":accountname,
                    "Moderations":value["moderationResults"]}
            else:
                mydoc={"_id":id , "created":value["created"],"portfolio":portfolio,"accountname":accountname, "lotnumber":lotnumber,
                    "Moderations":value["moderationResults"]}
                
            # if conn != None: #Postgresql Connection
            if os.getenv("DBTYPE")=="psql": #Postgresql Connection
                #-------- Migrating to SQLAlchemy from Psycopg2 due to IP Check issue  -----# 
                # json_col =json.dumps(mydoc)
                # query = "INSERT INTO ModerationResult(id, payload) VALUES (%s, %s)"
                # data = (id, json_col)
                with engine.connect() as con:
                    con.execute(
                        text("INSERT INTO ModerationResult(id, payload) VALUES (:id, :payload)"),
                        [{"id": id, "payload": json.dumps(mydoc)}],
                    )
                    con.commit()
                # cursor.execute(query, data)
                # conn.commit()
                return "PtrnRecogCreatedData"
            
            else:
                PtrnRecogCreatedData = Results.mycol.insert_one(mydoc)
                print("PtrnRecogCreatedData.acknowledged",PtrnRecogCreatedData.acknowledged)
                return PtrnRecogCreatedData.acknowledged
        except Exception as e:
            log.error("Error occured in Results create")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

    def createRequestPayload(endpoint,value,id,portfolio, accountname,user=None,lotnumber=None):
        request_id_var.set(id)
        try:
            if type(value) is not dict:
                value=value#json.loads(value) #.json()
            id=id #value["uniqueid"]
            if user:
                mydoc={"id":id , "created":datetime.datetime.now(),"user":user,"lotnumber":lotnumber,
                       "portfolio":portfolio,"accountname":accountname,
                    "Request Payload":value, "API":endpoint}
            else:
                mydoc={"id":id , "created":datetime.datetime.now(),"portfolio":portfolio,"accountname":accountname, 
                       "lotnumber":lotnumber, "Request Payload":value, "API":endpoint}
                
            # if conn != None: #Postgresql Connection
            if os.getenv("DBTYPE")=="psql": #Postgresql Connection
                #-------- Migrating to SQLAlchemy from Psycopg2 due to IP Check issue  -----# 
                # json_col =json.dumps(mydoc)
                # query = "INSERT INTO ModerationResult(id, payload) VALUES (%s, %s)"
                # data = (id, json_col)
                with engine.connect() as con:
                    con.execute(
                        text("INSERT INTO ModerationResult(id, payload) VALUES (:id, :payload)"),
                        [{"id": id, "payload": json.dumps(mydoc)}],
                    )
                    con.commit()
                # cursor.execute(query, data)
                # conn.commit()
                return "PtrnRecogCreatedData"
            else:
                PtrnRecogCreatedData = Results.mycol.insert_one(mydoc)
                print("PtrnRecogCreatedData.acknowledged",PtrnRecogCreatedData.acknowledged)
                return PtrnRecogCreatedData.acknowledged
        except Exception as e:
            log.error("Error occured in Results createRequestPayload")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
    def createlog(value):
        
        try:
            value["created"]=time.time()
            # if conn != None: #Postgresql Connection
            if os.getenv("DBTYPE")=="psql": #Postgresql Connection
                #-------- Migrating to SQLAlchemy from Psycopg2 due to IP Check issue  -----# 

                # json_col =json.dumps(value)
                # query = "INSERT INTO log_db(id, error) VALUES (%s, %s)"
                # data = (value["_id"], json_col)
                with engine.connect() as con:
                    con.execute(
                        text("INSERT INTO log_db(id, error) VALUES (:id, :error)"),
                        [{"id": value["_id"], "error": json.dumps(value)}],
                    )
                    con.commit()
                # cursor.execute(query, data)
                # conn.commit()
                return "PtrnRecogCreatedData"
            else: 
                PtrnRecogCreatedData = Results.logdb.insert_one(value)
                print("Log added",PtrnRecogCreatedData.acknowledged)
                return PtrnRecogCreatedData.acknowledged
        except Exception as e:
            log.error("Error occured in Log saving")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
    
    
    def createwithfeedback(value):
        
        try:
            # print(id)
            PtrnRecogCreatedData = Results.mycol2.insert_one(value)
            print("PtrnRecogCreatedData.acknowledged",PtrnRecogCreatedData.acknowledged)
            return PtrnRecogCreatedData.acknowledged
        except Exception as e:
            log.error("Error occured in createwithfeedback")
            log.error(f"Exception: {e}")
    
    def update(query,value:dict):
        try:
        
            newvalues = { "$set": value }
            
            PtrnRecogUpdatedData=Results.mycol.update_one(query,newvalues)
            log.debug(str(newvalues)) 
            return PtrnRecogUpdatedData.acknowledged
        except Exception as e:
            log.error("Error occured in Results update")
            log.error(f"Exception: {e}")
    
    def delete(id):
        try:
            return Results.mycol.delete_one({"_id": id})
        except Exception as e:
            log.error("Error occured in Results delete")
            log.error(f"Exception: {e}")
            
    def deleteMany(query):
        try:
            return Results.mycol.delete_many(query).acknowledged
        except Exception as e:
            log.error("Error occured in Results deleteMany")
            log.error(f"Exception: {e}")
