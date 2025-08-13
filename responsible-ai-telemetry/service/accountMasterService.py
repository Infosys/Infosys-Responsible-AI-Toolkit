'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from elasticsearch import Elasticsearch
import pymongo
from datetime import datetime, timedelta
import pytz
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
load_dotenv()
import os
from service.elasticconnectionservice import es
# # Establish a connection to MongoDB
# client = pymongo.MongoClient(os.getenv("MONGO_PATH"))
# db = client[os.getenv("MONGO_DB_NAME")]
# collection = db['accMastertelemetrydata']


# def insert_data(data):
#     result = collection.insert_one(data.dict())
#     if result.acknowledged:
#         return True
#     else:
#         return False
def accMasterElasticDataPush(data):
    
    # Index Creation
    index_name = 'accmasterindex'
    if not es.indices.exists(index=index_name):
        index_body = {
            'mappings': {
                'properties': {
                    'tenant': {'type': 'keyword'},
                    'apiname': {'type': 'keyword'},
                    'date': {'type': 'date'},
                    'accMaster_requests': {
                        'properties': {
                            'portfolio_name': {'type': 'keyword'},
                            'account_name': {'type': 'keyword'},
                            'dataGrp_list': {'type': 'keyword'}
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
        'accMaster_requests': {
            'portfolio_name': data.accMaster_requests.portfolio_name,
            'account_name': data.accMaster_requests.account_name,
            'dataGrp_list': data.accMaster_requests.dataGrp_list
        }
    }

    # Upload data to Elasticsearch
    es.index(index=index_name, body=es_doc)
    es.indices.refresh(index=index_name)


            



