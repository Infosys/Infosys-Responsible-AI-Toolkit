'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024-2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''



"""
fileName: global_constants.py
description: Global constants for usecase  module
"""


HTTP_STATUS_SERVICE_UNAVAILBLE=503
ERR_CONNECTION_REFUSED="Unable to connect the Database"
HTTP_STATUS_NOT_FOUND=404
DATABASE_ERROR="DATABASE not Found"
HTTP_STATUS_DATA_PROCESSING_ERROR=500
HTTP_STATUS_BAD_REQUEST=500
DATA_ERROR="Bad request. Please check the payload"
OPERATIONAL_ERROR="Some Error occurred while performing the db transaction.Please check with administrator or try later"
HTTP_STATUS_NOT_ALLLOWED=405
NOT_ALLOWED_MESSAGE="Method or DB Transaction not allowed"
HTTP_STATUS_400_CODE=400
HTTP_STATUS_OK=200
HTTP_STATUS_409_CODE=409
EMPTY_LIST_ERR_MESSAGE="No records found"
HTTP_415_UNSUPPORTED_MEDIA_TYPE=415
UNSUPPPORTED_MEDIA_TYPE_ERROR="Unsupported media type: "
HTTP_422_UNPROCESSABLE_ENTITY="422"