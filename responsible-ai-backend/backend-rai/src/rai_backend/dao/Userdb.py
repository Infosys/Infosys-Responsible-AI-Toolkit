"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import datetime
import json
from rai_backend.mappers.UserMapper import UserData, UserDataResponse
from fastapi import HTTPException, Response
from rai_backend.dao.DatabaseConnection import DB
from rai_backend.config.logger import CustomLogger
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from rai_backend.service.backend_service import UserInDB
load_dotenv()
log = CustomLogger()

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


mydb=DB.connect()

class UserDb:
    if 'UserConsent' not in mydb.list_collection_names():
        mydb.create_collection('UserConsent')
    
    mycol = mydb['User']
    myuserauth = mydb['UserAuthRel']
    myAuth = mydb['Authority']
    myCount = mydb['UserLimit']
    myConsent = mydb['UserConsent']
    def findOne(id):
        try:
            user=UserDb.mycol.find_one({'id':id},{'_id':0})
            if user is not None:
                return user
                
            else:
                #raise HTTPException(status_code=404, detail="No users Found")
                return 'No users Found'
        except Exception as e:
            log.error(e)
            return "<p>the error:<br>" + str(e) + "</p>",500
    def findAll()->UserDataResponse:
            try:                                    
                users=UserDb.mycol.find({},{'_id':0})
                userResponseArray = []
                if users:
                    for user in users:
                        user_dict={}
                        user_dict["id"]=user['id']
                        user_dict["login"]=user["login"]
                        user_dict["activated"]=user["activated"]
                        user_dict["createdBy"]=user["createdBy"]
                        user_dict["createdDate"]=user["createdDate"]
                        user_dict["firstName"]=user["firstName"]
                        user_dict["lastModifiedBy"]=user["lastModifiedBy"]
                        user_dict["lastModifiedDate"]=user["lastModifiedDate"]
                        user_dict['authorities'] = user['authorities']
                        userResponseArray.append(user_dict) 
                        res = userResponseArray  
                        obj =UserDataResponse
                        obj.userList=res      
                        #res=UserDataResponse(userList=userResponseArray)
                    return obj
                    #return res
                else:
                    return [], 404
            except Exception as e:
                log.debug(e)
                return "<p>the error:<br>" + str(e) + "</p>",500
    def create(newUser):
        DB.connect()
        try:
            newUser= AttributeDict(newUser)
            user=UserDb.mycol.find_one({'login':newUser.login},{"_id":0})
            if(user):
                return False
            else:
                document = UserDb.myCount.find_one()
                if document:
                    count_value = document.get('counter')
                print(f"Current count value: {count_value}")
                
                userLength=list(UserDb.mycol.find({},{"_id":0,"id":1}).sort("id",-1))
                if len(userLength)>0:
                    new_id = userLength[0]["id"]+ 1
                    myDoc ={
                        "id":new_id, 
                        "email":newUser.email, 
                        "login":newUser.login, 
                        "firstName":newUser.login, 
                        "langKey":newUser.langKey,
                        "passwordHash":generate_password_hash(newUser.cred, method='pbkdf2:sha256'),
                        "activated":True, 
                        "createdDate":datetime.datetime.now(), 
                        "createdBy":'system',
                        "lastModifiedBy":'system', 
                        "lastModifiedDate":datetime.datetime.now(),
                        "authorities":["ROLE_USER"]
                        }
                    UserDb.myuserauth.insert_one({"user_id":new_id,"authority_name":"ROLE_USER"})
                    # if count_value > 100:
                    #     myDoc["activated"] = False  # Set activated to false
                    # count_value += 1
                    # UserDb.myCount.update_one({},{'$set': {'counter': count_value}})
                    # print(f"Updated count value: {count_value}")            
                    result = UserDb.mycol.insert_one(myDoc).inserted_id
                    return True
        except Exception as e:
            log.debug(e)
            return False
        
    def update(id,user):
        try:
            oldData= UserDb.mycol.find_one({'id':id},{'_id':0})
            newData={ '$set': user}
            #UserDb.mycol.update_one(oldData,newData)
            UpdatedData = UserDb.mycol.update_one({'id':id},newData)
            log.debug(str(newData))
            authorities = user.get("authorities")
            UserDb.myuserauth.UserAuthRel.delete_many({ "user_id": id })
            for auth in authorities:
                 UserDb.myuserauth.UserAuthRel.insert_one({"user_id":id,"authority_name":auth})	
                 #db.UserAuthRel.update_one({"user_id":id,"authority_name":"ROLE_USER"})
                 log.info("The record has been successfully updated.")
            if UpdatedData:
                return {"message": "User updated successfully", "status_code": 200}
            else:
                return {"message": "User updating fails", "status_code": 400}
        except Exception as e:
            log.error(e)
            return {"message": "An error occurred", "status_code": 500}
    def delete(id):
        try:
             UserDb.mycol.delete_one({"id":id})
             UserDb.myuserauth.UserAuthRel.delete_many({ "user_id": id })
             return "The record has been successfully deleted.", 204
        except Exception as e:
             log.error(e)
             return "<p>the error:<br>" + str(e) + "</p>", 500
        
    def getAllAuthority():
        try:
            authResponseArray=[]
            cursor = list(UserDb.myAuth.distinct("name"))
            if (len(cursor) > 0):
                for doc in cursor:
                    authResponseArray.append(doc)
                return authResponseArray
            return ''
        except Exception as e:
            log.error(e)
            return '<p>the error:<br>'+str(e)+'</p>', 500
    def getUserByName(loginName):
        try:
            myquery = { 'login': loginName }
            user = UserDb.mycol.find_one(myquery,{"_id":0})
            if user is not None:
                user_dict={}
                user_dict["id"]=user['id']
                user_dict["login"]=user["login"]
                user_dict["activated"]=user["activated"]
                user_dict["createdBy"]=user["createdBy"]
                user_dict["createdDate"]=user["createdDate"]
                user_dict["firstName"]=user["firstName"]
                user_dict["lastModifiedBy"]=user["lastModifiedBy"]
                user_dict["lastModifiedDate"]=user["lastModifiedDate"]
                user_dict['authorities'] = user['authorities']
                return user_dict
            else:
                raise HTTPException(status_code=401, detail="Unauthorized")
        except Exception as e:
            log.info("Inside Except")
            log.debug(e)
            raise HTTPException(status_code=401, detail="Unauthorized")
    def add_initial_data():
        auth = list(UserDb.myAuth.find({},{"_id":0}))
        if len(auth)==0:
            admin_role = {"name":"ROLE_ADMIN"}
            user_role = {"name":"ROLE_USER"}
            ml_role = {"name":"ROLE_ML"}
            excel_role = {"name":"ROLE_EXCEL"}
            empty_role = {"name":"ROLE_EMPTY"}
            UserDb.myAuth.insert_many([admin_role, user_role,ml_role, excel_role,empty_role])
        user=list(UserDb.mycol.find({},{"_id":0}))
        if(len(user)==0):
            admin_user = {"id":1, "login":"admin", "firstName":"Admin", "langKey":'en', "passwordHash":generate_password_hash(
            'admin', method='pbkdf2:sha256'), "activated":True, "createdDate":datetime.datetime.now(), "lastModifiedBy":'system', "lastModifiedDate":datetime.datetime.now(), "createdBy":'system',"authorities":["ROLE_ADMIN","ROLE_USER"]}
            user_user = {"id":2, "login":"user", "firstName":"User", "langKey":'en', "passwordHash":generate_password_hash(
            'user', method='pbkdf2:sha256'), "activated":True, "createdDate":datetime.datetime.now(), "lastModifiedBy":'system', "lastModifiedDate":datetime.datetime.now(), "createdBy":'system',"authorities":["ROLE_USER"]}
            UserDb.mycol.insert_many([admin_user, user_user])
            UserDb.myuserauth.insert_many([{"user_id":admin_user["id"],"authority_name":"ROLE_ADMIN"},{"user_id":admin_user["id"],"authority_name":"ROLE_USER"},{"user_id":user_user["id"],"authority_name":"ROLE_USER"}])
        userLimit = list(UserDb.myCount.find({},{"_id":0}))
        if(len(userLimit)==0):
            user_limit_count ={"counter":0}
            UserDb.myCount.insert_one(user_limit_count)

    def update_newUser_role(loginName,role):
        myQuery = { 'login': loginName }
        newUsers =  UserDb.mycol.find_one(myQuery,{"_id":0})
        if newUsers is not None:
            #newData = {'$set': {'authorities': role}}
            id = newUsers['id']
            auth = newUsers['authorities']           
            for ath in role:
                if ath not in auth:  # Check if the authority already exists
                    auth.append(ath)
            newData = {'$set': {'authorities': auth}}
            response = UserDb.mycol.update_one({'login': loginName},newData)

            UserDb.myuserauth.delete_many({"user_id":id})
            for auth in role:              
                 UserDb.myuserauth.insert_many([{"user_id":id ,"authority_name":auth}])	
            return response.acknowledged
    
    def newAuthority(role):
        myQuery = { 'name': role }
        newRole =  UserDb.myAuth.find_one(myQuery,{"_id":0})
        if newRole is  None:
            try:
                auth = UserDb.myAuth.insert_one({"name":role}) 
                if auth:
                    return {"message": "NewRole created successfully", "status_code": 200} 
            except Exception as e:
                log.debug(e)
                return {"message": "Error creating new role", "status_code": 500}
        else:
            return {"message": "Role already exists", "status_code": 500} 
    
    
    def set_user_consent(userId, userConsentStatus):
        try:
            existing_user = UserDb.myConsent.find_one({'userId': userId})
            if existing_user:
                UserDb.myConsent.update_one({'userId': userId}, {'$set': {'userConsentStatus': userConsentStatus}})
            else:
                UserDb.myConsent.insert_one({'userId': userId, 'userConsentStatus': userConsentStatus})
            return {"message": "User consent updated successfully", "status_code": 200}
        except Exception as e:
            log.error(e)
            return {"message": "An error occurred", "status_code": 500}
    

    
    def get_user_consent(userId):
        try:
            user_consent = UserDb.myConsent.find_one({'userId': userId}, {'_id': 0, 'userConsentStatus': 1})
            if user_consent:
                return user_consent['userConsentStatus']
            return False
        except Exception as e:
            log.error(e)
            return False
        
       
            



                
                 

        
		
	
            

        





            

                    





        
        

