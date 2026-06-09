'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from dotenv import load_dotenv
import os
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import pytz
from zoneinfo import ZoneInfo
from service.elasticconnectionservice import es
from middleware.text_anonymize import textAnonymize
import logging
load_dotenv()
logger = logging.getLogger(__name__)

 
def privacyElasticDataPush(data):
    try:
        print(f"Processing telemetry for Privacy API")
        input_text = data.request.inputText
        anonymize_flag = getattr(data, 'anonymize', True)
        if anonymize_flag is not False:  
            try:
                input_text = textAnonymize(input_text)
                print(f"Anonymized inputText")
            except Exception as e:
                print(f"Error occurred during anonymization: {e}")
                anonymize_flag=False
        else:
            print(f"Anonymization disabled - using original inputText: {input_text}")
                                                               
        data_dict = {"_id": data.uniqueid, "tenant": data.tenant, "apiname": data.apiname, "user": data.user, "anonymize": anonymize_flag ,"lotNumber":data.lotNumber, "date": data.date, "request": data.request.dict(), "response": data.response}
        
        data_dict["request"]["inputText"] = input_text
        
                                                                                                                      
        print("DATE",data_dict['date'])

        index_name = 'privacyindexv2'
        if not es.indices.exists(index=index_name):
            index_body = {
    'mappings': {
        'properties': {
            'uniqueid': {'type': 'keyword'},
            'tenant': {'type': 'keyword'},
            'apiname': {'type': 'keyword'},
            'user': {'type': 'keyword'},
            'anonymize': {'type': 'keyword'},
            'lotNumber':{'type': 'keyword'},
            'date': {'type': 'date'},
            'request': {
                'properties': {
                    'portfolio_name': {'type': 'keyword'},
                    'account_name': {'type': 'keyword'},
                    'exclusion_list': {'type': 'keyword'},
                    'inputText': {'type': 'keyword'}
                }
            },
            'response': {
                'properties': {
                    'type': {'type': 'keyword'},
                    'beginOffset': {'type': 'float'},
                    'endOffset': {'type': 'float'},
                    'score': {'type': 'float'},
                    'responseText': {'type': 'keyword'}
                }
            }
        }
    }
}
            es.indices.create(index=index_name, body=index_body)
        
        es_data = []
        count=0

        print("date", data_dict['date'])
        date_str = data_dict['date']
        local_tz = ZoneInfo("Asia/Kolkata")
        utc_tz = ZoneInfo("UTC")
        dt = datetime.strptime(date_str,"%Y-%m-%dT%H:%M:%S.%f")
        dt = dt.replace(tzinfo=local_tz)
        dt_utc = dt.astimezone(utc_tz)
        dt_utc_formatted = dt_utc.strftime("%Y-%m-%dT%H:%M:%S")
        print("DATE USED FOR ELASTIC", date_str)
        es_doc = {
        'uniqueid': data_dict['_id'],
        'tenant': data_dict['tenant'],
        'apiname': data_dict['apiname'],
        'user': data_dict['user'],
        'anonymize': data_dict['anonymize'],
        'lotNumber': data_dict['lotNumber'],
        'date': dt_utc_formatted,  
        'request': {
            'portfolio_name': data_dict['request']['portfolio_name'],
            'account_name': data_dict['request']['account_name'],
            'exclusion_list': data_dict['request']['exclusion_list'],
            'inputText': data_dict['request']['inputText']
        },
        'response': []
    }
        
        for response_data in data_dict['response']:
            response_data= response_data.dict()
            response = {
                'type': response_data['type'],
                'beginOffset': response_data['beginOffset'],
                'endOffset': response_data['endOffset'],
                'score': response_data['score'],
                'responseText': response_data['responseText']
            }
            es_doc['response'].append(response)
        es_data.append(es_doc)
        count = count + 1
        print(count)
        
        for doc in es_data:
            try:
                es.index(index=index_name, body=doc)
                print("DOC INSERTED IN THE ELASTIC")
            except Exception as e:
                print("Error occurred while inserting document")    
            
            
        es.indices.refresh(index=index_name)
        return es_doc

    except Exception as e:
        print(f"Privacy telemetry processing failed: {e}")
        raise Exception(f"Processing failed: {e}")