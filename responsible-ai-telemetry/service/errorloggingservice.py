'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from datetime import datetime, timezone
import json
from pydantic import parse_obj_as
from zoneinfo import ZoneInfo
import os
from elasticsearch import Elasticsearch
from mapper.errorloggingtelemetrydata import ErrorLog
from service.elasticconnectionservice import es
from dateutil.parser import parse

def errorLoggingElasticDataPush(data):
    # if isinstance(data, str):
    #     data = ErrorLog.parse_raw(data)
    errorEnvironment = os.getenv('ERROR_ENVIRONMENT')
    now = datetime.now(timezone.utc)
    today= now.isoformat()
    data = {
        'tenetName': data.tenetName,
        'errorCode': data.errorCode,
        'errorMessage': data.errorMessage,
        'apiEndPoint': data.apiEndPoint,
        'errorRequestMethod': data.errorRequestMethod,
        'errorEnvironment': errorEnvironment,
        'errorTimestamp': today
    }
    index_name = 'errorlogindexv1'
    
    if not es.indices.exists(index=index_name):
        index_body = {
            'mappings': {
                'properties': {
                    'tenetName': {'type': 'keyword'},
                    'errorCode': {'type': 'keyword'},
                    'errorMessage': {'type': 'keyword'},
                    'apiEndPoint': {'type': 'keyword'},
                    'errorRequestMethod': {'type': 'keyword'},
                    'errorEnvironment': {'type': 'keyword'},
                    'errorTimestamp': {'type': 'date'}
                }
            }
        }
        es.indices.create(index=index_name, body=index_body)

    
    es_doc = {
        'tenetName': data['tenetName'],
        'errorCode': data['errorCode'],
        'errorMessage': data['errorMessage'],
        'apiEndPoint': data['apiEndPoint'],
        'errorRequestMethod': data['errorRequestMethod'],
        'errorEnvironment': data['errorEnvironment'],
        'errorTimestamp': today
    }
    try:
        es.index(index=index_name, body=es_doc)
    except Exception as e:
        print("Error occurred while inserting document")

    es.indices.refresh(index=index_name)