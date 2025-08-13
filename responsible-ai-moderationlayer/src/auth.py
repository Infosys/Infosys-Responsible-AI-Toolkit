'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import requests
import os
import time
from config.logger import CustomLogger
# from dotenv import load_dotenv

log=CustomLogger()
# Global variables to store the token and its expiration time
bearer_token = None
token_expiration_time = 0

class Auth:

    def is_env_vars_present():
        if os.getenv("AUTH_URL")=="":
            return None
        else:
            return 1


    def get_bearer_token():
        print("inside get_bearer_token")
        global bearer_token, token_expiration_time
        
        #Define authentication endpoints and credentials
        tenant_id=os.getenv("TENANT_ID")
        client_id=os.getenv("CLIENT_ID")
        client_secret=os.getenv("CLIENT_SECRET")
        auth_url= os.getenv("AUTH_URL")
        scope = os.getenv("SCOPE")

        #Create the payload with the necessary parameters
        payload={
                'grant_type':'client_credentials',
                'client_id':client_id,
                'client_secret':client_secret,
                'scope':scope
            }

        #Send the POST request to the authentication server
        response= requests.post(auth_url, data=payload)

        if response.status_code == 200:
                token_info = response.json()
                bearer_token = token_info['access_token']
                log.info(f"Bearer Token: {bearer_token}")
                # Calculate token expiration time
                expires_in = token_info['expires_in']
                token_expiration_time = time.time() + expires_in - 60  # Subtract 60 seconds to account for possible delays
                return bearer_token
        else:
                log.info(f"Failed to obtain token: {response.status_code}")
                log.info(response.text)
                bearer_token = None
                return None
        
    def get_valid_bearer_token():
        global bearer_token, token_expiration_time

        # Check if the current token is expired or not present
        if bearer_token is None or time.time() > token_expiration_time:
            Auth.get_bearer_token()

        return bearer_token
