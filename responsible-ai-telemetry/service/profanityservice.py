'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import pymongo
from dotenv import load_dotenv
import os
from elasticsearch import Elasticsearch
import pymongo
from datetime import datetime, timedelta
import pytz
from zoneinfo import ZoneInfo
load_dotenv()
from service.elasticconnectionservice import es


def profanityElasticDataPush(data):  
        # print("ELASTIC URL AFTER EXEC CODE===",os.getenv("ELASTIC_URL"))
        # data = {"_id": data.uniqueid, "tenant": data.tenant, "apiname": data.apiname, 
        #         "user": data.user, "lotNumber":data.lotNumber, "date": data.date, 
        #         "request": data.request.dict(), "response": data.response}
        print(data)
        data = {
            'uniqueid': data.uniqueid,
            'tenant': data.tenant,
            'apiname': data.apiname,
            'user': data.user,
            'lotNumber': data.lotNumber,
            'date': data.date,
            'request': data.request.dict(),
            'response': data.response.dict(),
            'outputText': data.response.outputText
        }
        print(data)
        # 'response': {
        #                 'profanityScoreList': [{
        #                     'metricName': item.metricName,
        #                     'metricScore': item.metricScore
        #                 } for item in data.response.profanityScoreList]
        #             }
        # Index Creation
        index_name = 'profanityindexv2'
        if not es.indices.exists(index=index_name):
            index_body = {
    'mappings': {
        'properties': {
            'uniqueid': {'type': 'keyword'},
            'tenant': {'type': 'keyword'},
            'apiname': {'type': 'keyword'},
            'user': {'type': 'keyword'},
            'lotNumber':{'type': 'keyword'},
            'date': {'type': 'date'},
            'request': {
                'properties': {
                    'inputText': {'type': 'keyword'}
                }
            },
            'response': {
                # 'type': 'nested',  # Change 'array' to 'nested'
                'properties': {
                     'profanity':{
                          'properties': {                          
                          'profaneWord': {'type': 'keyword'},
                          'beginOffset':{'type': 'integer'},
                          'endOffset':{'type': 'integer'},
                     }    
                    },
                    'profanityScoreList':{
                         'properties':{
                              'metricName': {'type': 'keyword'},
                              'metricScore': {'type': 'float'},
                         }
                    },
                    'outputText': {'type': 'keyword'},    
                }
            }
        }
    }
}
            es.indices.create(index=index_name, body=index_body)
    
        dt_local_formatted = None
        
        # Transform data for Elasticsearch
        es_data = []
        count=0
        
        print("date in DB", data['date'])
        date_str = data['date']
        # Get timezone we're trying to convert from
        local_tz = ZoneInfo("Asia/Kolkata")
        # UTC timezone
        utc_tz = ZoneInfo("UTC")
        dt = datetime.strptime(date_str,"%Y-%m-%dT%H:%M:%S.%f")
        dt = dt.replace(tzinfo=local_tz)
        dt_utc = dt.astimezone(utc_tz)
        dt_utc_formatted = dt_utc.strftime("%Y-%m-%dT%H:%M:%S")
        print("DATE USED FOR ELASTIC", date_str)
        es_doc = {
        'uniqueid': data['uniqueid'],
        'tenant': data['tenant'],
        'apiname': data['apiname'],
        'user': data['user'],
        'lotNumber':data['lotNumber'],
        'date': dt_utc_formatted,  # Use the formatted UTC date string
        'request': {
            'inputText': data['request']['inputText']
        },
        'response': {
                'profanityScoreList': [{
                'metricName': item['metricName'],
                'metricScore': item['metricScore']
            } for item in data['response']['profanityScoreList']],
                            
        }
        }
        if data['response']['profanity']:
                es_doc['response']['profanity'] = [{
                    'profaneWord': data['response']['profanity'][0]['profaneWord'],
                    'beginOffset': data['response']['profanity'][0]['beginOffset'],
                    'endOffset': data['response']['profanity'][0]['endOffset']
                }]
        if 'outputText' in data['response']:
            es_doc['response']['outputText'] = data['response']['outputText']
        es_data.append(es_doc)
        count = count + 1
        print(count)
        for doc in es_data:
            try:
                es.index(index=index_name, body=doc)
                print("DOC INSERTED IN THE ELASTIC", doc)
            except Exception as e:
                print("Error occurred while inserting document")    
            
            
        print("ELASTIC DATA AFTER INSERTION", es_data)
        es.indices.refresh(index=index_name)

