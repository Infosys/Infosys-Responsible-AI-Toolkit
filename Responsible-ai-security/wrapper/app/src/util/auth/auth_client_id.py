'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024-2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from jose import jwt, ExpiredSignatureError,JWTError
import os
from dotenv import load_dotenv
import requests
import msal
import time
from fastapi import Depends, HTTPException
import os
# from app.config.logger import CustomLogger
from src.config.logger import CustomLogger

log=CustomLogger()
class AzureAuthClient:
    def __init__(self, tenant_id, client_id, client_secret, scope):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.token = None
        self.token_expiry = 0
        self.app = msal.ConfidentialClientApplication(
            client_id,
            authority=f"https://login.microsoftonline.com/{tenant_id}",
            client_credential=client_secret,
        )
    def get_token(self):
        try:
            if time.time() >= self.token_expiry:
                result = self.app.acquire_token_for_client(scopes=self.scope)
                if "access_token" not in result:
                    raise HTTPException(status_code=401, detail="Failed to acquire token")
                self.token = result['access_token']
                self.token_expiry = time.time() + result['expires_in'] - 300  # Refresh 5 minutes before expiry
            return self.token
        except Exception as e:
            log.error(f"Error getting Azure token: {str(e)}")
            raise HTTPException(status_code=401, detail="Failed to acquire token")
auth_client = AzureAuthClient(
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    client_id=os.getenv("AZURE_CLIENT_ID"),
    client_secret=os.getenv("AZURE_CLIENT_SECRET"),
    scope=['https://graph.microsoft.com/.default']
)
def get_azure_token():
    return auth_client.get_token()
 
 
# if __name__ == "__main__":
#     token = get_azure_token()
#     print(f"Bearer Token: {token}")