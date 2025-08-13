'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

# Success Response Codes
HTTP_STATUS_CODES = {
    "OK": 200,
    "NOT_FOUND": 404,
    "METHOD_NOT_ALLOWED": 405,
    "BAD_REQUEST": 400,
    "CONFLICT": 409,
    "UNSUPPORTED_MEDIA_TYPE": 415,
    "UNPROCESSABLE_ENTITY": 422,
    "SERVICE_UNAVAILABLE": 503,
    "INTERNAL_SERVER_ERROR": 500,
    "DATA_ERROR": 500,
}

# Message Constants
HTTP_STATUS_MESSAGES = {
    "OK": "Request processed successfully",
    "NOT_FOUND": "Resource not found",
    "METHOD_NOT_ALLOWED": "Method not allowed",
    "BAD_REQUEST": "Bad request",
    "CONFLICT": "Conflict",
    "UNSUPPORTED_MEDIA_TYPE": "Unsupported media type",
    "UNPROCESSABLE_ENTITY": "Unprocessable entity",
    "SERVICE_UNAVAILABLE": "Service unavailable",
    "INTERNAL_SERVER_ERROR": "Internal server error",
    "DATABASE_CONNECTION_REFUSED": "Database connection refused"
}