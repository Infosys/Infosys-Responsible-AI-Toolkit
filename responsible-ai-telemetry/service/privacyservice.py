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
from service.elasticconnectionservice import es
load_dotenv()

# # Establish a connection to MongoDB
# client = pymongo.MongoClient(os.getenv("MONGO_PATH"))
# db = client[os.getenv("MONGO_DB_NAME")]
# collection = db['privacytelemetrydata']


# def insert_data(data):
#     result = collection.insert_one(data.dict())
#     if result.acknowledged:
#         return True
#     else:
#         return False
    
def privacyElasticDataPush(data):
        data = {"_id": data.uniqueid, "tenant": data.tenant, "apiname": data.apiname, "user": data.user, "lotNumber":data.lotNumber, "date": data.date, "request": data.request.dict(), "response": data.response}
        print(data)
        print("DATE",data['date'])
        # Connect to Elasticsearch
        print("ELASTIC URL BEFORE EXEC CONNECTION")
        # print("ELASTIC URL FROM CONNECTION FILE===",os.getenv("ELASTIC_URL"))
        # es = Elasticsearch(
        #     [os.getenv("ELASTIC_URL")],
        #     basic_auth=('elastic', ''),
        #     verify_certs=False
        # )
        # print(es.ping())
        

        # Index Creation
        index_name = 'privacyindexv2'
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
                    'portfolio_name': {'type': 'keyword'},
                    'account_name': {'type': 'keyword'},
                    'exclusion_list': {'type': 'keyword'},
                    'inputText': {'type': 'keyword'}
                }
            },
            'response': {
                # 'type': 'nested',  # Change 'array' to 'nested'
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
        'uniqueid': data['_id'],
        'tenant': data['tenant'],
        'apiname': data['apiname'],
        'user': data['user'],
        'lotNumber':data['lotNumber'],
        'date': dt_utc_formatted,  # Use the formatted UTC date string
        'request': {
            'portfolio_name': data['request']['portfolio_name'],
            'account_name': data['request']['account_name'],
            'exclusion_list': data['request']['exclusion_list'],
            'inputText': data['request']['inputText']
        },
        'response': []
    }
        
        for response_data in data['response']:
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
        print(es_data)

        # # Upload data to Elasticsearch if it doesn't already exist
        # for doc in es_data:
        #     es_query = {
        #         "query": {
        #             "bool": {
        #                 "must": [
        #                     {"match": {"tenant": doc['tenant']}},
        #                     {"match": {"apiname": doc['apiname']}},
        #                     {"match": {"date": doc['date']}}
        #                 ]
        #             }
        #         }
        #     }
        #     existing_data = es.search(index=index_name, body=es_query)

        #     if existing_data['hits']['total']['value'] == 0:
        #         print("DATA INSERTED IN ELASTIC")
        #         es.index(index=index_name, body=doc)

        # es.indices.refresh(index=index_name)
        # Upload data to Elasticsearch without checking for existing data
        for doc in es_data:
            try:
                es.index(index=index_name, body=doc)
                print("DOC INSERTED IN THE ELASTIC", doc)
            except Exception as e:
                print("Error occurred while inserting document")    
            
            
        print("ELASTIC DATA AFTER INSERTION", es_data)
        es.indices.refresh(index=index_name)

        # # Display indices
        # indices = es.indices.get_alias()
        # for index in indices:
        #     print(index)