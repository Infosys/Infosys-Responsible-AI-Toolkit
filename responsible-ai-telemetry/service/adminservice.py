'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from pydantic import BaseModel
from elasticsearch import Elasticsearch
import pymongo
from datetime import datetime, timedelta
import pytz
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
load_dotenv()
import os
from service.elasticconnectionservice import es
    
class AdminRequests(BaseModel):
    recognizer_name: str
    recognizer_type: str
    recognizer_value_pattern: str
    entity: str
    context: str
    score_range: str
    
def adminElasticDataPush(data):
    # Index Creation
    index_name = 'adminindex'
    if not es.indices.exists(index=index_name):
        index_body = {
            'mappings': {
                'properties': {
                    'tenant': {'type': 'keyword'},
                    'apiname': {'type': 'keyword'},
                    'date': {'type': 'date'},
                    'admin_requests': {
                        'properties': {
                            'recognizer_name': {'type': 'keyword'},
                            'recognizer_type': {'type': 'keyword'},
                            'recognizer_value_pattern': {'type': 'keyword'},
                            'entity': {'type': 'keyword'},
                            'context': {'type': 'keyword'},
                            'score_range': {'type': 'keyword'}
                        }
                    }
                }
            }
        }
        es.indices.create(index=index_name, body=index_body)

    # Prepare data for Elasticsearch
    es_doc = {
        'tenant': data.tenant,
        'apiname': data.apiname,
        'date': data.date,
        'admin_requests': {
            'recognizer_name': data.admin_requests.recognizer_name,
            'recognizer_type': data.admin_requests.recognizer_type,
            'recognizer_value_pattern': data.admin_requests.recognizer_value_pattern,
            'entity': data.admin_requests.entity,
            'context': data.admin_requests.context,
            'score_range': data.admin_requests.score_range
        }
    }

    # Upload data to Elasticsearch
    es.index(index=index_name, body=es_doc)
    es.indices.refresh(index=index_name)

            



