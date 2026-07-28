'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import encodings
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import pytz
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
load_dotenv()
import os
import json
from mapper.moderationtelemetrydata import ModerationResults
from service.elasticconnectionservice import es

from middleware.text_anonymize import textAnonymize

def moderationElasticDataPushTest(data):

        anonymize_flag = getattr(data, 'anonymize', True)
        input_text = data.moderationResults.text
        if anonymize_flag is not False:
            try:
                input_text = textAnonymize(input_text)
                print("Anonymization completed successfully.")
            except Exception as e:
                print(f"Anonymization error: {e}")
                anonymize_flag=False
        else:
            print(f"Going without anonymization")   

        data = {"_id": data.uniqueid,"portfolioName":data.portfolioName, "accountName":data.accountName,"created":data.created, "moderationResults": data.moderationResults.dict()}

        print("ELASTIC URL BEFORE EXEC CONNECTION")

        now = datetime.now()
        index_name = 'moderationindextesting'
        if not es.indices.exists(index=index_name):
            

            index_body = {
                'mappings': {
                    'properties': {
                        'uniqueid': {'type': 'keyword'},
                        'timestamp': {'type': 'date'},
                        'accountName': {'type': 'keyword'},
                        'portfolioName': {'type': 'keyword'},
                        'anonymize' :{'type':'keyword'},
                        'moderationResults': {
                            'properties': {
                                'text': {'type': 'keyword'},
                                'promptInjectionCheck': {
                                    'properties': {
                                        'injectionConfidenceScore': {'type': 'float'},
                                        'injectionThreshold': {'type': 'float'},
                                        'result': {'type': 'keyword'}
                                    }
                                },
                                'jailbreakCheck': {
                                    'properties': {
                                        'jailbreakSimilarityScore': {'type': 'float'},
                                        'jailbreakThreshold': {'type': 'float'},
                                        'result': {'type': 'keyword'}
                                    }
                                },
                                'privacyCheck': {
                                    'properties': {
                                        'entitiesRecognised': {'type': 'keyword'},
                                        'entitiesConfiguredToBlock': {'type': 'keyword'},
                                        'result': {'type': 'keyword'}
                                    }
                                },
                                'profanityCheck': {
                                    'properties': {
                                        'profaneWordsIdentified': {'type': 'keyword'},
                                        'profaneWordsthreshold': {'type': 'integer'},
                                        'result': {'type': 'keyword'}
                                    }
                                },
                                'toxicityCheck': {
                                    'properties': {
                                        'toxicityScore': {
                                            'properties': {
                                                'toxicity': {'type': 'float'},
                                                'severe_toxicity': {'type': 'float'},
                                                'obscene': {'type': 'float'},
                                                'identity_attack': {'type': 'float'},
                                                'insult': {'type': 'float'},
                                                'threat': {'type': 'float'},
                                                'sexual_explicit': {'type': 'float'}
                                            }
                                        },
                                        'toxicitythreshold': {'type': 'float'},
                                        'result': {'type': 'keyword'}
                                    }
                                },
                                'restrictedtopic': {
                                    'properties': {
                                        'topicScores': {
                                            'properties': {
                                                'Explosives': {'type': 'float'},
                                                'Terrorism': {'type': 'float'}
                                            }
                                        },
                                        'topicThreshold': {'type': 'float'},
                                        'result': {'type': 'keyword'}
                                    }
                                },
                                'textQuality': {
                                    'properties': {
                                        'readabilityScore': {'type': 'float'},
                                        'textGrade': {'type': 'keyword'}
                                    }
                                },
                                'refusalCheck': {
                                    'properties': {
                                        'refusalSimilarityScore': {'type': 'float'},
                                        'RefusalThreshold': {'type': 'float'},
                                        'result': {'type': 'keyword'}
                                    }
                                },
                                'customThemeCheck': {
                                    'properties': {
                                        'customSimilarityScore': {'type': 'float'},
                                        'themeThreshold': {'type': 'float'},
                                        'result': {'type': 'keyword'}
                                    }
                                },
                                'summary': {
                                    'properties': {
                                        'status': {'type': 'keyword'},
                                        'reason': {'type': 'keyword'}
                                    }
                                }
                            }
                        }
                    }
                }
            }

            
            es.indices.create(index=index_name, body=index_body)



       
        es_data = []
        i = 0
       
        i += 1
        print("COUNTER", i)
        es_doc = {
        'uniqueid': data['_id'],
        'timestamp': data['created'],
        'accountName': data['accountName'],
        'portfolioName': data['portfolioName'],
        'anonymize': anonymize_flag,
        'moderationResults': {
            'text': input_text,
            'promptInjectionCheck': {
                'injectionConfidenceScore': data['moderationResults']['promptInjectionCheck']['injectionConfidenceScore'],
                'injectionThreshold': data['moderationResults']['promptInjectionCheck']['injectionThreshold'],
                'result': data['moderationResults']['promptInjectionCheck']['result']
            },
            'jailbreakCheck': {
                'jailbreakSimilarityScore': data['moderationResults']['jailbreakCheck']['jailbreakSimilarityScore'],
                'jailbreakThreshold': data['moderationResults']['jailbreakCheck']['jailbreakThreshold'],
                'result': data['moderationResults']['jailbreakCheck']['result']
            },
            'privacyCheck': {
                'entitiesRecognised': data['moderationResults']['privacyCheck']['entitiesRecognised'],
                'entitiesConfiguredToBlock': data['moderationResults']['privacyCheck']['entitiesConfiguredToBlock'],
                'result': data['moderationResults']['privacyCheck']['result']
            },
            'profanityCheck': {
                'profaneWordsIdentified': data['moderationResults']['profanityCheck']['profaneWordsIdentified'],
                'profaneWordsthreshold': data['moderationResults']['profanityCheck']['profaneWordsthreshold'],
                'result': data['moderationResults']['profanityCheck']['result']
            },
            'toxicityCheck': {
                'toxicityScore': data['moderationResults']['toxicityCheck']['toxicityScore'],
                'toxicitythreshold': data['moderationResults']['toxicityCheck']['toxicitythreshold'],
                'result': data['moderationResults']['toxicityCheck']['result']
            },
            'restrictedtopic': {
                'topicScores': data['moderationResults']['restrictedtopic']['topicScores'],
                'topicThreshold': data['moderationResults']['restrictedtopic']['topicThreshold'],
                'result': data['moderationResults']['restrictedtopic']['result']
            },
            'textQuality': {
                'readabilityScore': data['moderationResults']['textQuality']['readabilityScore'],
                'textGrade': data['moderationResults']['textQuality']['textGrade']
            },
            'refusalCheck': {
                'refusalSimilarityScore': data['moderationResults']['refusalCheck']['refusalSimilarityScore'],
                'RefusalThreshold': data['moderationResults']['refusalCheck']['RefusalThreshold'],
                'result': data['moderationResults']['refusalCheck']['result']
            },
            'summary': {
                'status': data['moderationResults']['summary']['status'],
                'reason': data['moderationResults']['summary']['reason']
            }
            }
            }
        es_data.append(es_doc)

        
        for doc in es_data:

            
            id = str(doc["uniqueid"])
            doc["uniqueid"]=str(doc["uniqueid"])
            print("Indexing document:", doc)
            try:
                
                es.index(index=index_name,id=id,document=doc)
                print("Document indexed successfully.")
            except:
                print("Error indexing document:")
                
        return es_doc
            

