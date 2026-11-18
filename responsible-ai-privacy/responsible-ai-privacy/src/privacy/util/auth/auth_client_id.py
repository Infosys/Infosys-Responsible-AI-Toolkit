'''
License textMIT Licensehttps://mit-license.org/Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''


# # src/privacy/util/auth/auth_client_id.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, ExpiredSignatureError, JWTError 
import os
from dotenv import load_dotenv
import requests
import logging

load_dotenv()

AZURE_TENANT_ID = os.getenv('AZURE_TENANT_ID')
AZURE_CLIENT_ID = os.getenv('AZURE_CLIENT_ID')

# Security scheme for HTTP Bearer token
security = HTTPBearer()
log = logging.getLogger(__name__)
def get_public_keys():
    jwks_url = os.getenv('AZURE_AD_JWKS_URL')
    response = requests.get(jwks_url, verify=True, timeout=10)
    if response.status_code != 200:
        log.error(f"Failed to fetch JWKS: HTTP {response.status_code}")
        raise HTTPException(status_code=500, detail="Failed to fetch JWKS")
    
    jwks = response.json()
    if 'keys' not in jwks:
        log.error("JWKS response does not contain 'keys'")
        raise HTTPException(status_code=500, detail="JWKS response format is invalid")
    
    log.info(f"JWKS response: {jwks}")
    return {key['kid']: key for key in jwks['keys']}


def authenticate_client_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
        authorization = credentials.credentials
        if authorization:
            try:
                # Get public keys first
                keys = get_public_keys()
                
                # Try to decode with each key until one works
                # This avoids using get_unverified_header which could be exploited
                decoded_token = None
                last_error = None
                
                for kid, key in keys.items():
                    try:
                        decoded_token = jwt.decode(
                            authorization, 
                            key, 
                            algorithms=['RS256'],  # Azure AD uses RS256, not HS256
                            audience=AZURE_CLIENT_ID,
                            options={"verify_signature": True}
                        )
                        break  # Successfully decoded
                    except JWTError as e:
                        last_error = e
                        continue  # Try next key
                
                if decoded_token is None:
                    raise last_error or JWTError("Unable to verify token with any available key")
                
                log.info(f"Valid token: {decoded_token}")
                log.info(f"Issuer: {decoded_token.get('iss')}")
                log.info(f"Client ID: {decoded_token.get('aud')}")
                log.info(f"Tenant ID: {decoded_token.get('tid')}")
                
                return decoded_token
            
            except ExpiredSignatureError as e:
                log.error(f"Token has expired: {e}")
                raise HTTPException(status_code=401, detail="Token has expired")
            except JWTError as e:
                log.error(f"Invalid token: {e}")
                raise HTTPException(status_code=401, detail="Invalid token")
            except Exception as e:
                log.error(f"Unexpected error: {e}")
                raise HTTPException(status_code=500, detail="Unexpected error")

def get_auth_client_id():
    return authenticate_client_id

