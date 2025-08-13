'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import requests
import time
import os
from config.logger import CustomLogger

# Global variables to hold the auth token and its expiration time
auth_token = None
token_expiry_time = 0  

log=CustomLogger()
TOKEN_URL = os.getenv("AICLOUD_MODEL_AUTH")

verify_ssl = os.getenv("VERIFY_SSL")
sslv={"False":False,"True":True,"None":True}

def _generate_auth_token():
    """Generate and store the auth token for llama model, set its expiry time."""
    global auth_token, token_expiry_time
    
    response = requests.get(TOKEN_URL,verify=sslv[verify_ssl])

    if response.status_code == 200:
        auth_token = response.json()["access_token"]
        # Set the token's expiration time for 1 hour
        token_expiry_time = time.time() + 3600 
        log.info("Llama auth token generated.")
    else:
        raise Exception("Failed to generate auth token")

def _get_auth_token():
    """Return the auth token if valid, else generate a new one."""
    global auth_token, token_expiry_time

    # Checking if the token exists and if it's expired
    if auth_token is None or time.time() > token_expiry_time:
        _generate_auth_token()  
    
    return auth_token

# Function to get the auth token
def load_token():
    """Method to explicitly load the auth token and generate it if necessary."""
    return _get_auth_token()

