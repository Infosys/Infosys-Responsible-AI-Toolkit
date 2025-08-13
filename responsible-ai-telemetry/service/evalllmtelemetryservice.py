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
from mapper.evalllmtelemetrydata import TelemetryData
from service.elasticconnectionservice import es
from dateutil.parser import parse


def evalllmElasticPush(data):
    if isinstance(data, str):
        data = parse_obj_as(TelemetryData, json.loads(data))

    index_name = 'evalllmindex'
    now = datetime.now()
    today = now.isoformat()
    if not es.indices.exists(index=index_name):
        index_body = {
            'mappings': {
                'properties': {
                    'uniqueid': {'type': 'keyword'},
                    'userid': {'type': 'keyword'},
                    'accountName': {'type': 'keyword'},
                    'portfolioName': {'type': 'keyword'},
                    'lotNumber': {'type': 'keyword'},
                    'created': {'type': 'date'},
                    'model': {'type': 'keyword'},
                    'moderationResults': {
                        'properties': {
                            'analysis': {'type': 'keyword'},
                            'score': {'type': 'keyword'},
                            'threshold': {'type': 'keyword'},
                            'result': {'type': 'keyword'}
                        }
                    },
                    'evaluation_check': {'type': 'keyword'},
                    'timeTaken': {'type': 'keyword'},
                    'description': {'type': 'keyword'}
                }
            }
        }
        es.indices.create(index=index_name, body=index_body)

    es_doc = {
        'uniqueid': data.uniqueid,
        'userid': data.userid,
        'accountName': data.accountName,
        'portfolioName': data.portfolioName,
        'lotNumber': data.lotNumber,
        'created': data.created.isoformat(),
        'model': data.model,
        'moderationResults': {
            'analysis': data.moderationResults.analysis,
            'score': data.moderationResults.score,
            'threshold': data.moderationResults.threshold,
            'result': data.moderationResults.result
        },
        'evaluation_check': data.evaluation_check,
        'timeTaken': data.timeTaken,
        'description': data.description
    }
    try:
        es.index(index=index_name, body=es_doc)
    except Exception as e:
        print("Error occurred while inserting document")

    es.indices.refresh(index=index_name)