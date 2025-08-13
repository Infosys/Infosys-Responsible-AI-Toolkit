"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from functools import wraps
from datetime import datetime
import os
import time
from venv import logger
from fastapi import Response
from fastapi.responses import JSONResponse

from rai_backend.service.authenticatetelemetryservice import TelemetryContent
from rai_backend.config.logger import CustomLogger
from fastapi import APIRouter, Form, Request
from rai_backend.dao.Userdb import UserDb
from rai_backend.mappers.UserMapper import *
import concurrent.futures as con
from rai_backend.service.authService import AuthService
import requests
from pymongo import MongoClient
from rai_backend.mappers.PageAuthorityMapper import PageAuthority
from fastapi import APIRouter, HTTPException
from rai_backend.dao.DatabaseConnection import DB
from dotenv import load_dotenv
from rai_backend.dao.TelemetryFlagDb import TelemetryFlag
from werkzeug.security import generate_password_hash
import json
router = APIRouter()
log=CustomLogger()
globalUsername = ''
authenticatetelemetryurl = os.getenv("AUTHENTICATE_TELEMETRY_URL")
registertelemetryurl = os.getenv("AUTHENTICATE_TELEMETRY_URL")

# telFlagData = TelemetryFlag.findall({"Module":"RaiBackend"})
# print("TelData==",telFlagData)
# if(len(telFlagData) == 0):
#     telData = TelemetryFlag.create({"module":"RaiBackend"})
#     print("telData===",telData)

# authenticatetelemetryurl="http://localhost:8000/authenticatetelemetryapi"
# registertelemetryurl = "http://localhost:8000/registertelemetryapi"

# In-memory storage for active sessions
active_sessions = {}
# returns current date and time
now = datetime.now()
load_dotenv()
mydb=DB.connect()

## FUNCTION FOR FAIL_SAFE TELEMETRY
def send_telemetry_request(authenticate_telemetry_request, id=None):
    try:
        print("Starting send_telemetry_request")
        # Add the id to the authenticate_telemetry_request
        if id is not None:
            authenticate_telemetry_request['id'] = id
        response = requests.post(authenticatetelemetryurl, json=authenticate_telemetry_request)
        print(response, "response")
        print("RESPONSEEEEE")
        response.raise_for_status()
        response_data = response.json()
        print(response_data)
    except Exception as e:
        print("An error occurred")
def send_telemetry_request_register(register_telemetry_request):
    try:
        response = requests.post(registertelemetryurl, json=register_telemetry_request)
        response.raise_for_status()
        response_data = response.json()
        print(response_data)
    except Exception as e:
        print("An error occurred")



def token_required(func):
    @wraps(func)
    def decorated(request: Request, *args, **kwargs):
        print("request")
        print(str(request))
        authorization_header = request.headers.get("authorization")
        if authorization_header:
            if authorization_header.startswith("Bearer "):
                token = authorization_header.split()[1]
                if token == "null":
                    raise HTTPException(status_code=401, detail="Unauthorized")
                res = AuthService.accountService(globalUsername)
                print('ressss::')
                print(res)
                if res is None:
                    raise HTTPException(status_code=401, detail="Unauthorized")
                return res
            else:
                raise HTTPException(status_code=401, detail="Unauthorized")
        else:
            raise HTTPException(status_code=401, detail="Unauthorized")
    return decorated



@router.get('/account')
@token_required
def analyze(request: Request):
    print(request)
    log.info("Entered get account method")
    # response = AuthService.accountService(globalUsername)
    # return response

@router.post('/register')
def analyze(payload:NewUserRequest):
    log.info("Entered get register method")
    response = AuthService.signupPostService(payload)
   # telFlagData = TelemetryFlag.findall({"Module":"RaiBackend"})[0]
    #tel_Flag = telFlagData["TelemetryFlag"]
    # tel_Flag = False
    responseMessage = (response['message'],"response")
    responseMessage = responseMessage[0].lower()
    tel_flag = os.getenv("TELEMETRY_FLAG")
    print("responseMessage",responseMessage)
    requestObj = {
        "email":payload.email,
        "userName":payload.login,
    }
    responseObj = {
        # "status":response.status,
        # "message":response.message
    }
    if(tel_flag == 'True' and responseMessage == "user created successfully"):
        register_telemetry_request={
            "tenantName":"User Management",
            "apiName":"User Registration",
            # date=now.isoformat(),
            "request" : requestObj,
            "response" : responseObj
        }
        print("register_telemetry_request===",json.dumps(register_telemetry_request))
        with con.ThreadPoolExecutor() as executor:
            executor.submit(send_telemetry_request_register, register_telemetry_request)     
    return response

# @router.get('/<string:loginName>')
# def login(loginName:str):
#     log.debug("globalUsername: " + globalUsername)
#     response = UserDb.getUserByName(loginName)
#     return response

@router.post('/authenticate')
def authenticate(payload:NewAuthRequest):
    log.debug("Payload received: "+ str(payload))
    global globalUsername
    globalUsername = payload.username
    global active_sessions  # Use the global active_sessions variable
    response = AuthService.loginPostService(payload.username,payload.cred)
    tel_flag = os.getenv("TELEMETRY_FLAG")
    # Record the login time
    active_sessions[payload.username] = {
            "login_time": time.time()
    }
    user_info = active_sessions[payload.username]["login_time"]
    readableLoginTime = datetime.fromtimestamp(user_info).strftime('%Y-%m-%d %H:%M:%S')
    print("readableLoginTime",readableLoginTime)
    print("active_sessions",active_sessions)
    requestObj ={
        "userName":payload.username,
        "loginTime":readableLoginTime,
        "logOutTime": "Not Logged Out",
        "duration": "0 Seconds"
    }
    responseObj = {
        # "status":response.status_code,
        # "message":response.message
    }
    if(tel_flag == 'True'):
        authenticate_telemetry_request= {
            "tenantName" : "User Management",
            "apiName" : "User Authentication",
            # date=now.isoformat(),
            "request" : requestObj,
            "response" : responseObj
        }
        print("authenticate_telemetry_request===",authenticate_telemetry_request)
        with con.ThreadPoolExecutor() as executor:
             executor.submit(send_telemetry_request, authenticate_telemetry_request) 
    return response


@router.get('/logout')
def logout(username: str):
    global active_sessions
    print("username",username)
    print("active_sessions",active_sessions)
    username = str(username.lower())
    username = username.replace('"', '')
    # user_info = active_sessions.pop(username)
    # print(user_info)
    if username in active_sessions:
        user_info = active_sessions.pop(username)
        duration = time.time() - user_info["login_time"]  # Access the login time correctly
        logTime = user_info["login_time"]
        readableLoginTime = datetime.fromtimestamp(logTime).strftime('%Y-%m-%d %H:%M:%S')
        print("readableLoginTime",readableLoginTime)
        duration = f"{duration:.2f} seconds"
        print(duration, "duration")
        print(user_info, "user_info")
        print(active_sessions, "active_sessions")
        # print(f"User {username} was active for {duration:.2f} seconds")
        tel_flag = os.getenv("TELEMETRY_FLAG")
        readableLogOutTime = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        print("readableLogOutTime",readableLogOutTime)
        requestObj ={
            "userName": username,
            "loginTime": readableLoginTime,
            "logOutTime": readableLogOutTime,
            "duration": duration
        }
        responseObj = {
            # "status":response.status_code,
            # "message":response.message
        }
        if(tel_flag == 'True'):
            authenticate_telemetry_request= {
                "tenantName" : "User Logout",
                "apiName" : "User Authentication",
                "request" : requestObj,
                "response" : responseObj
            }
            print("authenticate_telemetry_request===",authenticate_telemetry_request)
            with con.ThreadPoolExecutor() as executor:
                # Pass the username as the id parameter
                executor.submit(send_telemetry_request, authenticate_telemetry_request, id=username) 
        return {'message': 'Logged out', 'duration': duration, 'username': username}
    # else:
    #     logger.warning(f"User {username} attempted to log out without an active session")
    #     return {'message': 'No active session found'}, 400


@router.get('/users',response_model=UserDataResponse)
def getUser():
    users = UserDb.findAll()
    return users

@router.get('/users/getUser')
def getUserById(id:int):
    user = UserDb.findOne(id)
    return user

@router.patch('/users/updateUser')
def updateUser(user:UpdateUserRequest):
    id = user.id
    user_dict = vars(user)
    response = UserDb.update(id,user_dict)
    return response
@router.delete('/users/delete')
def deleteUser(id:int):
    response = UserDb.delete(id)
    return response
@router.get('/users/authorities')
def getAuthority():
    authorities = UserDb.getAllAuthority()
    return authorities

# @router.get('/pageauthority', response_model=PageAuthority)
# async def get_page_access(role:str):
#     try:
#         pageAuth = mydb['PageAuthority']
#         # Retrieve the page access information from the database
#         # result = collection.find_one({"page": page})
#         result=pageAuth.find_one({'role':role})

#         if result:
#             return result
#         else:
#             raise HTTPException(status_code=404, detail="Page not found")
#     except Exception as e:
#         raise e

@router.get('/pageauthority')
async def get_page_access(role:str):
    try:
        pageAuth = mydb['PageAuthority']
        result = pageAuth.find_one({'role': role})

        if result:
            result['_id'] = str(result['_id'])  # Convert ObjectId to string
            return result
        else:
            raise HTTPException(status_code=404, detail="Page not found")
    except Exception as e:
        raise e

@router.get('/pageauthoritynew')
async def get_page_access_new(role:str):
    try:
        pageAuth = mydb['PageAuthorityNew']
        result = pageAuth.find_one({'role': role})

        if result:
            result['_id'] = str(result['_id'])  # Convert ObjectId to string
            return result
        else:
            raise HTTPException(status_code=404, detail="Page not found")
    except Exception as e:
        raise e
    
## Update pageauthoritynew
from typing import Dict

@router.patch('/pageauthoritynewupdate')
async def update_page_access(payload: Dict):
    try:
        print("Payload received: ", payload)
        role = payload.get('role')
        pages = payload.get('pages').get('pages')
        print("Payload received: ", pages)
        pageAuth = mydb['PageAuthorityNew']
        result = pageAuth.find_one_and_update({'role': role}, {'$set': {'pages': pages}})
        if result:
            return {"message": "Page access updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Page not found")
    except Exception as e:
        raise e


from pydantic import BaseModel
class CreateAuth(BaseModel):
    role: str
## Create new pageauthoritynew
@router.post('/createpageauthoritynew')
async def create_page_access(createAuth: CreateAuth):
    try:
        role = createAuth.role
        pages = {}  # Create an empty pages object
        pageAuth = mydb['PageAuthorityNew']
        
        # Check if a document with the same role already exists
        if pageAuth.find_one({'role': role}):
            raise HTTPException(status_code=400, detail="Role already exists")
        
        result = pageAuth.insert_one({'pages': pages,'role': role})
        return {"message": "Page access created successfully"}
    except Exception as e:
        raise e

    
@router.get('/getAll/telemetry',response_model=AllDataResponse)
def getAllFlag():
    try:
      response = TelemetryContent.getAlldata()
      return response
    except Exception as e:
        raise e
@router.post('/create/telemetry',response_model=CreationStatus)
def createFlag(payload:flagCreation):
    try:
      log.debug("Payload received: "+ str(payload))
      response = TelemetryContent.creation(payload)
      return response
    except Exception as e:
        raise e
@router.patch('/update/telemetry',response_model=CreationStatus)
def updateFlag(payload:flagUpdate):
    try:
      log.debug("Payload received: "+ str(payload))
      response = TelemetryContent.updation(payload)
      return response
    except Exception as e:
        raise e
    
@router.patch('/newUser/assignRole')
def assignNewUserRole(payload:newRoleUpdRqst):
    try:
        log.debug("Payload received: "+ str(payload))
        response = AuthService.newUserRole(payload.loginName,payload.role)
        return response
    except Exception as e:
        raise e

@router.post('/newRole')
def createNewRole(payload:newRoleCreate):
    res = AuthService.newAuthority(payload.role)
    return res

@router.post('/setUserConsent')
def set_user_consent(payload: UserConsentCreate):
    res = UserDb.set_user_consent(payload.userId, payload.userConsentStatus)
    return res

@router.get('/getUserConsent/{userId}')
def get_user_consent(userId: str):
    res = UserDb.get_user_consent(userId)
    return JSONResponse(content={"userConsentStatus": res})




