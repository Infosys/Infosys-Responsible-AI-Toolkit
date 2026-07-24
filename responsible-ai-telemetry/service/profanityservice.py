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
import logging

from middleware.text_anonymize import textAnonymize


load_dotenv()

logger = logging.getLogger(__name__)

def profanityElasticDataPush(data):
    try:
        logger.info(f"Processing telemetry for tenant: {data.tenant}")
        input_text = data.request.inputText
        anonymize_flag = getattr(data, 'anonymize', True)
        if anonymize_flag is not False:
            try:
                    input_text = textAnonymize(input_text)
                    logger.info("Anonymization completed successfully.")
            except Exception as e:
                    logger.error(f"Anonymization error: {e}")
                    anonymize_flag=False        
        else:
                logger.info(f"Anonymization disabled - using original inputText: {input_text}")
         
        data_dict = {
            'uniqueid': data.uniqueid,
            'tenant': data.tenant,
            'apiname': data.apiname,
            'user': data.user,
            'anonymize': anonymize_flag,
            'lotNumber': data.lotNumber,
            'date': data.date,
            'request': {
                'inputText': input_text,
            },
            'response': data.response.dict(),
            'outputText': data.response.outputText
        }
        logger.info(data_dict)
        index_name = 'profanityindexv2'
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
                    'inputText': {'type': 'keyword'}
                }
            },
            'response': {
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
        
        es_data = []
        count=0
        
        logger.info("date in DB", data_dict['date'])
        date_str = data_dict['date']
        local_tz = ZoneInfo("Asia/Kolkata")
        utc_tz = ZoneInfo("UTC")
        dt = datetime.strptime(date_str,"%Y-%m-%dT%H:%M:%S.%f")
        dt = dt.replace(tzinfo=local_tz)
        dt_utc = dt.astimezone(utc_tz)
        dt_utc_formatted = dt_utc.strftime("%Y-%m-%dT%H:%M:%S")
        logger.info("DATE USED FOR ELASTIC", date_str)
        es_doc = {
        'uniqueid': data_dict['uniqueid'],
        'tenant': data_dict['tenant'],
        'apiname': data_dict['apiname'],
        'user': data_dict['user'],
        'anonymize': data_dict['anonymize'],
        'lotNumber':data_dict['lotNumber'],
        'date': dt_utc_formatted,  
        'request': {
            'inputText': data_dict['request']['inputText']
        },
        'response': {
                'profanityScoreList': [{
                'metricName': item['metricName'],
                'metricScore': item['metricScore']
            } 
            for item in data_dict['response']['profanityScoreList']],
                            
        }
        }
        if data_dict['response']['profanity']:
                es_doc['response']['profanity'] = [{
                    'profaneWord': data_dict['response']['profanity'][0]['profaneWord'],
                    'beginOffset': data_dict['response']['profanity'][0]['beginOffset'],
                    'endOffset': data_dict['response']['profanity'][0]['endOffset']
                }]
        if 'outputText' in data_dict['response']:
            es_doc['response']['outputText'] = data_dict['response']['outputText']
        es_data.append(es_doc)
        count = count + 1
        logger.info(count)
        for doc in es_data:
            try:
                es.index(index=index_name, body=doc)
                logger.info("DOC INSERTED IN THE ELASTIC", doc)
            except Exception as e:
                logger.error("Error occurred while inserting document")    
            
            
        logger.info("ELASTIC DATA AFTER INSERTION", es_data)
        es.indices.refresh(index=index_name)
        return es_doc

    except Exception as e:
        logger.error(f"Profanity telemetry processing failed: {e}")
        raise Exception(f"Processing failed: {e}")