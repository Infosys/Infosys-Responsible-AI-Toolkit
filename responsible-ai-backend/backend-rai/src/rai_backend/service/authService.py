"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from fastapi import HTTPException
from rai_backend.dao.Pageauthoritydb import PageauthorityDb
from rai_backend.dao.Pageauthoritynewdb import PageauthorityDbNew
from rai_backend.service.backend_service import UserInDB
from rai_backend.config.logger import CustomLogger
from rai_backend.dao.DatabaseConnection import DB
from rai_backend.dao.Userdb import UserDb
from rai_backend.domain.userEntity import User
from werkzeug.security import check_password_hash


log = CustomLogger()
mydb=DB.connect()

class AuthService():
    mycol = mydb['User']

    def accountService(globalUsername):
        try:
            log.debug(globalUsername)
            return UserDb.getUserByName(globalUsername)
        except Exception as e:
            log.error("Error in Account Service", exc_info=True)
           # raise HTTPException(status_code=401, detail="Unauthorized")
        
    def loginPostService(username,password):
        try:
            # DATA INSERTION AFTER LOGIN
            UserDb.add_initial_data()
            PageauthorityDb.add_initial_data()
            PageauthorityDbNew.add_initial_data()
            user=AuthService.mycol.find_one({'login':username},{"_id":0})
            if not user or not check_password_hash(user['passwordHash'],password) or user['activated'] is not True:
                return "User not found or Incorrect Password or not activated", 404
            
            # user_obj = User(username=user['login'])
            # login_user(user_obj, remember=rememberMe, force=True)
            access_token = UserInDB.login_for_access_token(username)           
            return {"id_token": access_token}
        except Exception as e:
            log.error("Error in Account Service", exc_info=True)
            #raise HTTPException(status_code=404, detail="Error")
        
    #def logoutService():
        # yet to implement

    def signupPostService(newUser):
        try:
            # DATA INSERTION AFTER SIGNUP
            UserDb.add_initial_data()
            success = UserDb.create(newUser)
            PageauthorityDb.add_initial_data()
            if success:
                return {"message": "User created successfully", "status_code": 200}
            else:
                return {"message": "User already exists", "status_code": 400}
        except Exception as e:
            log.debug(e)
            return {"message": "An error occurred", "status_code": 500}
        
    def newUserRole(loginName,role):
        try:
            res = UserDb.update_newUser_role(loginName,role)
            return res
        except Exception as e:
            log.debug(e)
            #raise HTTPException(status_code=404, detail="Error")

    def resetCount():
        UserDb.myCount.update_one({},{'$set': {'counter':0}})

    def newAuthority(role):
       auth = UserDb.newAuthority(role)
       return auth




        
        