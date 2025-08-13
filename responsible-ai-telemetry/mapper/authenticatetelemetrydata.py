'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class requestTelemetry(BaseModel):
    userName: Optional[str] = None
    email: Optional[str] = None
    loginTime : Optional[str] = None
    logOutTime : Optional[str] = None
    duration : Optional[str] = None
    
class responseTelemetry(BaseModel):
    responseMessage: Optional[str] = None
class UserManagementTelemetryData(BaseModel):
    # Define the structure of the telemetry data
    tenantName: Optional[str] = None 
    apiName: Optional[str] = None 
    request : Optional[requestTelemetry] = None
    response : Optional[responseTelemetry] = None

    