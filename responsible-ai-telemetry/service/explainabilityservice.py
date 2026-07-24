'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from datetime import datetime
import json
from pydantic import parse_obj_as
from zoneinfo import ZoneInfo
import os
from elasticsearch import Elasticsearch
from mapper.explainabilitytelemetrydata import ExplainBulkProcessTelemetryData, TelemetryData
from service.elasticconnectionservice import es
from dateutil.parser import parse
from middleware.text_anonymize import textAnonymize
def explainabilityElasticDataPush(data):
    if isinstance(data, str):
        data = parse_obj_as(TelemetryData, json.loads(data))

    anonymize_flag = getattr(data, 'anonymize', True)
    print(anonymize_flag)
    data_dict=data
    input_text= data.request.inputText
    if anonymize_flag is not False:
        try:
            input_text = textAnonymize(input_text)
            print("Anonymized inputText")
        except Exception as e:
            print(f"Error occurred during anonymization: {e}")
            anonymize_flag=False
    index_name = 'explainabilityindex'
    if not es.indices.exists(index=index_name):
        index_body = {
            'mappings': {
                'properties': {
                    'uniqueid': {'type': 'keyword'},
                    'tenant': {'type': 'keyword'},
                    'apiname': {'type': 'keyword'},
                    'user': {'type': 'keyword'},
                    'lotNumber':{'type': 'keyword'},
                    'anonymize': {'type': 'keyword'},
                    'date': {'type': 'date'},
                    'request': {
                        'properties': {
                            'portfolio_name': {'type': 'keyword'},
                            'account_name': {'type': 'keyword'},
                            'inputText': {'type': 'keyword'},
                            'explainerID': {'type': 'integer'}
                        }
                    },
                    'response': {
                        'properties': {
                            'explainerID': {'type': 'integer'},
                            'explanation': {
                                'properties': {
                                    'predictedTarget': {'type': 'keyword'},
                                    'anchor': {'type': 'keyword'}
                                }
                            }
                        }
                    }
                }
            }
        }
        es.indices.create(index=index_name, body=index_body)
    date = parse(data.date)
    es_data = []
    data_dict.request.inputText = input_text
    data_dict.anonymize=anonymize_flag
    print("data.request.inputText",data.request.inputText)
    es_doc = {
        'uniqueid': data_dict.uniqueid,
        'tenant': data_dict.tenant,
        'apiname': data_dict.apiname,
        'user': data_dict.user,
        'lotNumber': data_dict.lotNumber,
        'date': date.now(),
        'anonymize': data_dict.anonymize,
        'request': data_dict.request.dict(),
        'response': [explanation.dict() for explanation in data_dict.response.explanation]
    }
    es_data.append(es_doc)
    print("es_doc=========",es_doc)
    for doc in es_data:
        try:
            es.index(index=index_name, body=doc)
            print("DOC INSERTED IN THE ELASTIC")
        except Exception as e:
            print("Error occurred while inserting document:", e)

    print("ELASTIC DATA AFTER INSERTION", es_data)
    es.indices.refresh(index=index_name)
    return es_doc
    
def explainabilityBulkElasticDataPush(data):
    if isinstance(data, str):
        data = parse_obj_as(ExplainBulkProcessTelemetryData, json.loads(data))
    
    index_name = 'explainabilitybulkindex'
    anonymize_flag = getattr(data, 'anonymize', True)
    data_dict=data
    data_dict.anonymize=anonymize_flag
    if anonymize_flag is not False and data.response:
        try:
            for i in range(len(data.response)):
                if data.response[i].InputPrompt:
                    data_dict.response[i].InputPrompt = textAnonymize(data.response[i].InputPrompt)
                    data_dict.response[i].Response = textAnonymize(data.response[i].Response)
                    data_dict.response[i].Chain_of_Thought = textAnonymize(data.response[i].Chain_of_Thought)
            print("Anonymization completed successfully.")
        except Exception as e:
            print(f"Anonymization error: {e}")
            anonymize_flag=False
    
    if not es.indices.exists(index=index_name):
        index_body = {
            'mappings': {
                'properties': {
                    'uniqueId': {'type': 'keyword'},
                    'tenetName': {'type': 'keyword'},
                    'apiName': {'type': 'keyword'},
                    'anonymize': {'type': 'keyword'},
                    'userId': {'type': 'keyword'},
                    'date': {'type': 'date'},
                    'response': {
                        'properties': {
                            'InputPrompt': {'type': 'keyword'},
                            'Response': {'type': 'keyword'},
                            'Chain_of_Thought': {'type': 'keyword'},
                            'Token_Cost': {'type': 'integer'}
                        }
                    }
                }
            }
        }
        es.indices.create(index=index_name, body=index_body)
    
    date = parse(data.date) if data.date else datetime.now()
    es_data = []
    es_doc = {
        'uniqueId': data_dict.uniqueId,
        'tenetName': data_dict.tenetName,
        'apiName': data_dict.apiName,
        'userId': data_dict.userId,
        'anonymize': data_dict.anonymize,
        'date': date.isoformat(),
        'response': [response.dict() for response in data_dict.response] if data_dict.response else []
    }
    es_data.append(es_doc)
    print("es_doc=========", es_doc)
    
    for doc in es_data:
        try:
            es.index(index=index_name, body=doc)
            print("DOC INSERTED IN THE ELASTIC")
        except Exception as e:
            print("Error occurred while inserting document:", e)
    
    print("Data inserted/updated in Elasticsearch")
    es.indices.refresh(index=index_name)
    return es_doc