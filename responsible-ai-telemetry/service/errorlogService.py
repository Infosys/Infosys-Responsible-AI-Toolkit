'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from datetime import datetime
import json
from pydantic import parse_obj_as
from zoneinfo import ZoneInfo
import os
from elasticsearch import Elasticsearch
from mapper.errorlogtelemetrydata import Error
from service.elasticconnectionservice import es
from dateutil.parser import parse

def errorLogElasticDataPush(data):
    if isinstance(data, str):
        data = parse_obj_as(Error, json.loads(data))

    index_name = 'errorlogindex'
    now = datetime.now()
    today= now.isoformat()
    if not es.indices.exists(index=index_name):
        index_body = {
            'mappings': {
                'properties': {
                    'uniqueid': {'type': 'keyword'},
                    'UUID': {'type': 'keyword'},
                    'function': {'type': 'keyword'},
                    'msg': {'type': 'keyword'},
                    'description': {'type': 'keyword'},
                    'date': {'type': 'date'}
                }
            }
        }
        es.indices.create(index=index_name, body=index_body)

    for error in data.error:
        es_doc = {
            'UUID': error.UUID,
            'function': error.function,
            'msg': error.msg,
            'description': error.description,
            'date': today
        }
        try:
            es.index(index=index_name, body=es_doc)
            print("DOC INSERTED IN THE ELASTIC", es_doc)
        except Exception as e:
            print("Error occurred while inserting document")

    es.indices.refresh(index=index_name)