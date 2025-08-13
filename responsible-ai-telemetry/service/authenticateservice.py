'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from elasticsearch import Elasticsearch
import pymongo
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
load_dotenv()
import os
from service.elasticconnectionservice import es
from datetime import datetime, timezone
def userManagementElasticDataPush(data, id=None):
    userEnvironment = os.getenv('ERROR_ENVIRONMENT')
    now = datetime.now(timezone.utc)
    today= now.isoformat()
    
    data = {
        'tenantName': data.tenantName,
        'apiName': data.apiName,
        'date': today,
        'userEnvironment': userEnvironment,
        'userid': data.request.userName,
        'request': {
            'email': data.request.email,
            'loginTime': data.request.loginTime,
            'logOutTime': data.request.logOutTime,
            'duration': data.request.duration
        },
        'response': {
            'responseMessage': data.response.responseMessage
        }
    }
    ## add id to the data
    data['id'] = id
    # Index Creation
    index_name = 'usermanagementindex'
    
    if not es.indices.exists(index=index_name):
        index_body = {
            'mappings': {
                'properties': {
                    'tenantName': {'type': 'keyword'},
                    'apiName': {'type': 'keyword'},
                    'date': {'type': 'date'},
                    'userEnvironment': {'type': 'keyword'},
                    'userid': {'type': 'keyword'},
                    'request': {
                        'properties': {
                            'email': {'type': 'keyword'},
                            'loginTime': {'type': 'keyword'},
                            'logOutTime': {'type': 'keyword'},
                            'duration': {'type': 'keyword'}
                        }
                    },
                    'response': {
                        'properties': {
                            'responseMessage': {'type': 'keyword'}
                        }
                    }
                }
            }
        }
        es.indices.create(index=index_name, body=index_body)
        
   
    es_doc = {
        'tenantName': data['tenantName'],
        'apiName': data['apiName'],
        'date': today,
        'userEnvironment': data['userEnvironment'],
        'userid': data['userid'],
        'request': {
            'email': data['request']['email'],
            'loginTime': data['request']['loginTime'],
            'logOutTime': data['request']['logOutTime'],
            'duration': data['request']['duration']
        },
        'response': {
            'responseMessage': data['response']['responseMessage']
        }
    }
    
    # print("Username:", data['request']['username'])
    # print("Duration:", data['request']['duration'])
         # Define your query
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"request.username": data['userid']}},
                    {"match": {"request.duration": "0 Seconds"}}
                ]
            }
        }
    }
    
    # Search for the document
    res = es.search(index=index_name, body=query)
    
    
    
    # If the document exists and meets the condition
    if res['hits']['total']['value'] > 0:
        # Get the id of the document
        idfromAPI = res['hits']['hits'][0]['_id']

        # Update the document
        res = es.update(index=index_name, id=idfromAPI, body={"doc": es_doc})
    else:
        # Create a new document
        res = es.index(index=index_name, body=es_doc)

    es.indices.refresh(index=index_name)


            



