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

def registerElasticDataPush(data):

    # Index Creation
    index_name = 'registerindex'
    if not es.indices.exists(index=index_name):
        index_body = {
            'mappings': {
                'properties': {
                    'tenant': {'type': 'keyword'},
                    'apiname': {'type': 'keyword'},
                    'date': {'type': 'date'},
                    'register_requests': {
                        'properties': {
                            'email': {'type': 'keyword'},
                            'login': {'type': 'keyword'},
                            'password': {'type': 'keyword'}
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
        'register_requests': {
            'email': data.register_requests.email,
            'login': data.register_requests.login,
            'password': data.register_requests.password
        }
    }

    # Upload data to Elasticsearch
    es.index(index=index_name, body=es_doc)
    es.indices.refresh(index=index_name)

            



