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
import json
from bson import ObjectId
from mapper.coupledmoderationtelemetrydata import ModerationResults,completionResponse
from service.elasticconnectionservice import es
    
def coupledModerationElasticDataPush(data):
        if data.Moderation_layer_time is not None:
            moderation_layer_time = data.Moderation_layer_time.dict()
        else:
            moderation_layer_time = None
            
        data = {
            "uniqueid": data.uniqueid,
            "object":data.object,
            "userid":data.userid,
            "lotNumber":data.lotNumber,
            "model":data.model,
            "created":data.created, 
            "choices":data.choices[0].dict(),
            "moderationResults": data.moderationResults.dict(),
            "Moderation_layer_time":moderation_layer_time,
            "portfolioName":data.portfolioName, 
            "accountName":data.accountName
            }
        # print("DATA MODIFIED FROM SERVER", json.dumps(data))
        # Connect to Elasticsearch
        # print("ELASTIC URL BEFORE EXEC CONNECTION")
        # print("ELASTIC URL BEFORE EXEC CONNECTION===",os.getenv("ELASTIC_URL"))
        # es = Elasticsearch(
        #     [os.getenv("ELASTIC_URL")],
        #     basic_auth=('elastic', ''),
        #     verify_certs=False
        # )
        print("ELASTIC SERVER AVAILABLE.....?",es.ping())
        
        now = datetime.now()
        # Index Creation

        index_name = 'couplemoderationindexv3'
        # index_name = 'testindex1'
        if not es.indices.exists(index=index_name):
            

            index_body = {
    "mappings": {
        "properties": {
            "uniqueid": {"type": "keyword"},
            "object": {"type": "keyword"},
            "userid": {"type": "keyword"},
            "lotNumber": {"type": "keyword"},
            "created": {"type": "date"},
            "model": {"type": "keyword"},
            "choices": {
                "properties": {
                    "text": {"type": "keyword"},
                    "index": {"type": "integer"},
                    "finishReason": {"type": "keyword"}
                }
            },
            "moderationResults": {
                "properties": {
                    "requestModeration": {
                        "properties": {
                            "text": {"type": "keyword"},
                            "promptInjectionCheck": {
                                "properties": {
                                    "injectionConfidenceScore": {"type": "keyword"},
                                    "injectionThreshold": {"type": "keyword"},
                                    "result": {"type": "keyword"}
                                }
                            },
                            "jailbreakCheck": {
                                "properties": {
                                    "jailbreakSimilarityScore": {"type": "keyword"},
                                    "jailbreakThreshold": {"type": "keyword"},
                                    "result": {"type": "keyword"}
                                }
                            },
                            "privacyCheck": {
                                "properties": {
                                    "entitiesRecognised": {"type": "keyword"},
                                    "entitiesConfiguredToBlock": {"type": "keyword"},
                                    "result": {"type": "keyword"}
                                }
                            },
                            "profanityCheck": {
                                "properties": {
                                    "profaneWordsIdentified": {"type": "keyword"},
                                    "profaneWordsthreshold": {"type": "keyword"},
                                    "result": {"type": "keyword"}
                                }
                            },
                            'toxicityCheck': {
                                'properties': {
                                    'toxicityScore': {
                                        'properties': {
                                            'toxicScore': {
                                                'properties': {
                                                    'metricName': {'type': 'keyword'},
                                                    'metricScore': {'type': 'float'}
                                                }
                                            }
                                        }
                                    },
                                    'toxicitythreshold': {'type': 'keyword'},
                                    'result': {'type': 'keyword'},
                                    'toxicityTypesConfiguredToBlock': {'type': 'keyword'},
                                    'toxicityTypesRecognised': {'type': 'keyword'}
                                }
                            },
                            "restrictedtopic": {
                                "properties": {
                                    "topicScores": {"type": "object"},
                                    "topicThreshold": {"type": "keyword"},
                                    "result": {"type": "keyword"},
                                    "topicTypesConfiguredToBlock": {"type": "keyword"},
                                    "topicTypesRecognised": {"type": "keyword"},
                                }
                            },
                            "textQuality": {
                                "properties": {
                                    "readabilityScore": {"type": "keyword"},
                                    "textGrade": {"type": "keyword"}
                                }
                            },
                            "refusalCheck": {
                                "properties": {
                                    "refusalSimilarityScore": {"type": "keyword"},
                                    "RefusalThreshold": {"type": "keyword"},
                                    "result": {"type": "keyword"}
                                }
                            },
                            "customThemeCheck": {
                                "properties": {
                                    "customSimilarityScore": {"type": "keyword"},
                                    "themeThreshold": {"type": "keyword"},
                                    "result": {"type": "keyword"}
                                }
                            },
                            "randomNoiseCheck": {
                                "properties": {
                                    "smoothLlmScore": {"type": "keyword"},
                                    "smoothLlmThreshold": {"type": "keyword"},
                                    "result": {"type": "keyword"}
                                }
                            },
                            "advancedJailbreakCheck": {
                                "properties": {
                                    "text": {"type": "keyword"},
                                    "result": {"type": "keyword"}
                                }
                            },
                            "summary": {
                                "properties": {
                                    "status": {"type": "keyword"},
                                    "reason": {"type": "keyword"}
                                }
                            }
                        }
                    },
                    "responseModeration": {
                        "properties": {
                            "generatedText": {"type": "keyword"},
                            "privacyCheck": {
                                "properties": {
                                    "entitiesRecognised": {"type": "keyword"},
                                    "entitiesConfiguredToBlock": {"type": "keyword"},
                                    "result": {"type": "keyword"}
                                }
                            },
                            "profanityCheck": {
                                "properties": {
                                    "profaneWordsIdentified": {"type": "keyword"},
                                    "profaneWordsthreshold": {"type": "keyword"},
                                    "result": {"type": "keyword"}
                                }
                            },
                            'toxicityCheck': {
                                'properties': {
                                    'toxicityScore': {
                                        'properties': {
                                            'toxicScore': {
                                                'properties': {
                                                    'metricName': {'type': 'keyword'},
                                                    'metricScore': {'type': 'float'}
                                                }
                                            }
                                        }
                                    },
                                    'toxicitythreshold': {'type': 'keyword'},
                                    'result': {'type': 'keyword'},
                                    'toxicityTypesConfiguredToBlock': {'type': 'keyword'},
                                    'toxicityTypesRecognised': {'type': 'keyword'},
                                }
                            },
                            "restrictedtopic": {
                                "properties": {
                                    "topicScores": {"type": "object"},
                                    "topicThreshold": {"type": "keyword"},
                                    "result": {"type": "keyword"},
                                    "topicTypesConfiguredToBlock": {"type": "keyword"},
                                    "topicTypesRecognised": {"type": "keyword"},
                                }
                            },
                            "textQuality": {
                                "properties": {
                                    "readabilityScore": {"type": "keyword"},
                                    "textGrade": {"type": "keyword"}
                                }
                            },
                            "textRelevanceCheck": {
                                "properties": {
                                    "PromptResponseSimilarityScore": {"type": "float"}
                                }
                            },
                            "refusalCheck": {
                                "properties": {
                                    "refusalSimilarityScore": {"type": "keyword"},
                                    "RefusalThreshold": {"type": "keyword"},
                                    "result": {"type": "keyword"}
                                }
                            },
                            "summary": {
                                "properties": {
                                    "status": {"type": "keyword"},
                                    "reason": {"type": "keyword"}
                                }
                            }
                        }
                    }
                }
            },
            'Moderation_layer_time': {
                'properties': {
                    'requestModeration': {
                        'properties': {
                            'promptInjectionCheck': {'type': 'keyword'},
                            'jailbreakCheck': {'type': 'keyword'},
                            'toxicityCheck': {'type': 'keyword'},
                            'privacyCheck': {'type': 'keyword'},
                            'profanityCheck': {'type': 'keyword'},
                            'refusalCheck': {'type': 'keyword'},
                            'restrictedtopic': {'type': 'keyword'},
                            'textqualityCheck': {'type': 'keyword'},
                            'customthemeCheck': {'type': 'keyword'},
                            'smoothLlmCheck': {'type': 'keyword'},
                            'bergeronCheck': {'type': 'keyword'}
                        }
                    },
                    'responseModeration': {
                        'properties': {
                            'promptInjectionCheck': {'type': 'keyword'},
                            'jailbreakCheck': {'type': 'keyword'},
                            'toxicityCheck': {'type': 'keyword'},
                            'privacyCheck': {'type': 'keyword'},
                            'profanityCheck': {'type': 'keyword'},
                            'refusalCheck': {'type': 'keyword'},
                            'restrictedtopic': {'type': 'keyword'},
                            'textqualityCheck': {'type': 'keyword'},
                            'customthemeCheck': {'type': 'keyword'},
                            'smoothLlmCheck': {'type': 'keyword'},
                            'bergeronCheck': {'type': 'keyword'},
                            'textrelevanceCheck': {'type': 'keyword'}
                        }
                    },
                    'OpenAIInteractionTime': {'type': 'keyword'},
                    'translate': {'type': 'keyword'},
                    'Time_taken_by_each_model_in_requestModeration': {
                        'properties': {
                            'toxicityCheck': {'type': 'keyword'},
                            'privacyCheck': {'type': 'keyword'},
                            'jailbreakCheck': {'type': 'keyword'},
                            'promptInjectionCheck': {'type': 'keyword'},
                            'customthemeCheck': {'type': 'keyword'},
                            'restrictedtopic': {'type': 'keyword'}
                        }
                    },
                    'Total_time_for_moderation_Check': {'type': 'keyword'},
                    'Time_taken_by_each_model_in_responseModeration': {
                        'properties': {
                            'toxicityCheck': {'type': 'keyword'},
                            'privacyCheck': {'type': 'keyword'},
                            'restrictedtopic': {'type': 'keyword'}
                        }
                    }
                }
            },
            "portfolioName": {"type": "keyword"},
            "accountName": {"type": "keyword"},
        }
    }
}

            ##########################
            es.indices.create(index=index_name, body=index_body)



        # Retrieve data from MongoDB
        # mongo_client = pymongo.MongoClient(os.getenv("MONGO_PATH"))
        # db = mongo_client[os.getenv("MONGO_DB_NAME")]
        # collection = db['moderationtelemetrydata']
        # print(mongoid)
        # mongo_data = data
        
        es_data = []
        # print("MONGODATA=======",mongo_data)
        
        # for data in mongo_data:
        # print("TTTTTTTTTTTTTTT",type(data['moderationResults']['responseModeration']['toxicityCheck'])) 
        # print("TTTTTTTTTTTTTTT",type(data['moderationResults']['responseModeration']['toxicityCheck']['toxicityScore']))
        # print("TTTTTTTTTTTTTTT",type(data['moderationResults']['responseModeration']['toxicityCheck']['toxicityScore'][0].metricScore))
            # print(data['moderationResults']['responseModeration']['toxicityCheck']['toxicityScore'][0]['toxicity'])
        toxicity_check = data.get('moderationResults', {}).get('requestModeration', {}).get('toxicityCheck', {})
        toxicity_score = toxicity_check.get('toxicityScore', [{}])
        toxic_scores = toxicity_score[0].get('toxicScore', [{}]) if toxicity_score else [{}]
        
        toxicity_check_response = data.get('moderationResults', {}).get('responseModeration', {}).get('toxicityCheck', {})
        toxicity_score_response = toxicity_check_response.get('toxicityScore', [{}])
        toxic_scores_response = toxicity_score_response[0].get('toxicScore', [{}]) if toxicity_score_response else [{}]
        
        restrictedTopic_response = data.get('moderationResults', {}).get('responseModeration', {}).get('restrictedtopic', {})
        restrictedTopic_score_response = restrictedTopic_response.get('topicScores', [{}])
        restrictedTopic_scores_response = restrictedTopic_score_response[0].get('topicScores', [{}]) if restrictedTopic_score_response else [{}]
        es_doc =  {
    "uniqueid": data['uniqueid'],
    "object": data['object'],
    "userid": data['userid'],
    "lotNumber": data['lotNumber'],
    "created": now,
    "model": data['model'],
    "choices": 
        {
        "text": data['choices']['text'],
        "index": data['choices']['index'],
        "finishReason": data['choices']['finishReason']
        }
    ,
    "moderationResults": {
        "requestModeration": {
        "text": data['moderationResults']['requestModeration']['text'],
        "promptInjectionCheck": {
            "injectionConfidenceScore": data['moderationResults']['requestModeration']['promptInjectionCheck']['injectionConfidenceScore'],
            "injectionThreshold": data['moderationResults']['requestModeration']['promptInjectionCheck']['injectionThreshold'],
            "result": data['moderationResults']['requestModeration']['promptInjectionCheck']['result']
        },
        "jailbreakCheck": {
            "jailbreakSimilarityScore": data['moderationResults']['requestModeration']['jailbreakCheck']['jailbreakSimilarityScore'],
            "jailbreakThreshold": data['moderationResults']['requestModeration']['jailbreakCheck']['jailbreakThreshold'],
            "result": data['moderationResults']['requestModeration']['jailbreakCheck']['result']
        },
        "privacyCheck": {
            "entitiesRecognised": data['moderationResults']['requestModeration']['privacyCheck']['entitiesRecognised'],
            "entitiesConfiguredToBlock": data['moderationResults']['requestModeration']['privacyCheck']['entitiesConfiguredToBlock'],
            "result": data['moderationResults']['requestModeration']['privacyCheck']['result']
        },
        "profanityCheck": {
            "profaneWordsIdentified": data['moderationResults']['requestModeration']['profanityCheck']['profaneWordsIdentified'],
            "profaneWordsthreshold": data['moderationResults']['requestModeration']['profanityCheck']['profaneWordsthreshold'],
            "result": data['moderationResults']['requestModeration']['profanityCheck']['result']
        },
       "toxicityCheck": {
    "toxicityScore": [
        {
            "metricName": "toxicity",
            "metricScore": toxic_scores[0].get('metricScore')
        },
        {
            "metricName": "severe_toxicity",
            "metricScore": toxic_scores[1].get('metricScore') if len(toxic_scores) > 1 else None
        },
        {
            "metricName": "obscene",
            "metricScore": toxic_scores[2].get('metricScore') if len(toxic_scores) > 2 else None
        },
        {
            "metricName": "threat",
            "metricScore": toxic_scores[3].get('metricScore') if len(toxic_scores) > 3 else None
        },
        {
            "metricName": "insult",
            "metricScore": toxic_scores[4].get('metricScore') if len(toxic_scores) > 4 else None
        },
        {
            "metricName": "identity_attack",
            "metricScore": toxic_scores[5].get('metricScore') if len(toxic_scores) > 5 else None
        },
        {
            "metricName": "sexual_explicit",
            "metricScore": toxic_scores[6].get('metricScore') if len(toxic_scores) > 6 else None
        }
    ],
    "toxicitythreshold": toxicity_check.get('toxicitythreshold'),
    "result": toxicity_check.get('result'),
    "toxicityTypesConfiguredToBlock": toxicity_check.get('toxicityTypesConfiguredToBlock'),
    "toxicityTypesRecognised": toxicity_check.get('toxicityTypesRecognised'),
},
        "restrictedtopic": {
            "topicScores": data['moderationResults']['responseModeration']['restrictedtopic']['topicScores'],
            "topicThreshold": data['moderationResults']['requestModeration']['restrictedtopic']['topicThreshold'],
            "result": data['moderationResults']['requestModeration']['restrictedtopic']['result'],
            "topicTypesConfiguredToBlock": data['moderationResults']['requestModeration']['restrictedtopic']['topicTypesConfiguredToBlock'],
            "topicTypesRecognised": data['moderationResults']['requestModeration']['restrictedtopic']['topicTypesRecognised'],
        },
        "textQuality": {
            "readabilityScore": data['moderationResults']['requestModeration']["textQuality"]["readabilityScore"],
            "textGrade": data['moderationResults']['requestModeration']["textQuality"]["textGrade"]
        },
        "refusalCheck": {
            "refusalSimilarityScore": data['moderationResults']['requestModeration']["refusalCheck"]["refusalSimilarityScore"],
            "RefusalThreshold": data['moderationResults']['requestModeration']["refusalCheck"]["RefusalThreshold"],
            "result": data['moderationResults']['requestModeration']['refusalCheck']['result']
        },
        "customThemeCheck": {
            "customSimilarityScore": data['moderationResults']['requestModeration']["customThemeCheck"]["customSimilarityScore"],
            "themeThreshold": data['moderationResults']['requestModeration']["customThemeCheck"]["themeThreshold"],
            "result": data['moderationResults']['requestModeration']['customThemeCheck']['result']
        },
        "randomNoiseCheck": 
        {
            "smoothLlmScore": data['moderationResults']['requestModeration']['randomNoiseCheck']['smoothLlmScore'],
            "smoothLlmThreshold": data['moderationResults']['requestModeration']['randomNoiseCheck']['smoothLlmThreshold'],
            "result": data['moderationResults']['requestModeration']['randomNoiseCheck']['result']
        },
        "advancedJailbreakCheck": {
            "text": data['moderationResults']['requestModeration']['advancedJailbreakCheck']['text'],
            "result": data['moderationResults']['requestModeration']['advancedJailbreakCheck']['result']
        },
        "summary": {
            "status": data['moderationResults']['requestModeration']['summary']['status'],
            "reason": data['moderationResults']['requestModeration']['summary']['reason']
        }
        },
        "responseModeration": {
            "generatedText": data['moderationResults']['responseModeration']['generatedText'],
            "privacyCheck": {
                "entitiesRecognised": data['moderationResults']['responseModeration']['privacyCheck']['entitiesRecognised'],
                "entitiesConfiguredToBlock": data['moderationResults']['responseModeration']['privacyCheck']['entitiesConfiguredToBlock'],
                "result": data['moderationResults']['responseModeration']['privacyCheck']['result']
            },
            "profanityCheck": {
                "profaneWordsIdentified": data['moderationResults']['responseModeration']['profanityCheck']['profaneWordsIdentified'],
                "profaneWordsthreshold": data['moderationResults']['requestModeration']['profanityCheck']['profaneWordsthreshold'],
                "result": data['moderationResults']['responseModeration']['profanityCheck']['result']
            },
            "toxicityCheck": {
                "toxicityScore": [
                    {
                        "metricName": "toxicity",
                        "metricScore": toxic_scores_response[0].get('metricScore')
                    },
                    {
                        "metricName": "severe_toxicity",
                        "metricScore": toxic_scores_response[1].get('metricScore') if len(toxic_scores_response) > 1 else None
                    },
                    {
                        "metricName": "obscene",
                        "metricScore": toxic_scores_response[2].get('metricScore') if len(toxic_scores_response) > 2 else None
                    },
                    {
                        "metricName": "threat",
                        "metricScore": toxic_scores_response[3].get('metricScore') if len(toxic_scores_response) > 3 else None
                    },
                    {
                        "metricName": "insult",
                        "metricScore": toxic_scores_response[4].get('metricScore') if len(toxic_scores_response) > 4 else None
                    },
                    {
                        "metricName": "identity_attack",
                        "metricScore": toxic_scores_response[5].get('metricScore') if len(toxic_scores_response) > 5 else None
                    },
                    {
                        "metricName": "sexual_explicit",
                        "metricScore": toxic_scores_response[6].get('metricScore') if len(toxic_scores_response) > 6 else None
                    }
                ],
                "toxicitythreshold": toxicity_check_response.get('toxicitythreshold'),
                "result": toxicity_check_response.get('result'),
                "toxicityTypesConfiguredToBlock": toxicity_check_response.get('toxicityTypesConfiguredToBlock'),
                "toxicityTypesRecognised": toxicity_check_response.get('toxicityTypesRecognised'),
            },
            "restrictedtopic": {
                "topicScores": restrictedTopic_scores_response[0].get('topicScores') if restrictedTopic_scores_response else None,
                "topicThreshold": data['moderationResults']['responseModeration']['restrictedtopic']['topicThreshold'],
                "result": data['moderationResults']['responseModeration']['restrictedtopic']['result'],
                "topicTypesConfiguredToBlock": data['moderationResults']['responseModeration']['restrictedtopic']['topicTypesConfiguredToBlock'],
                "topicTypesRecognised": data['moderationResults']['responseModeration']['restrictedtopic']['topicTypesRecognised'],
                
            },
            "textQuality": {
            "readabilityScore": data['moderationResults']['responseModeration']["textQuality"]["readabilityScore"],
            "textGrade": data['moderationResults']['responseModeration']["textQuality"]["textGrade"]
        },
        "textRelevanceCheck": {
            "PromptResponseSimilarityScore": data['moderationResults']['responseModeration']["textRelevanceCheck"]["PromptResponseSimilarityScore"]
        },
        "refusalCheck": {
            "refusalSimilarityScore": data['moderationResults']['responseModeration']["refusalCheck"]["refusalSimilarityScore"],
            "RefusalThreshold": data['moderationResults']['responseModeration']["refusalCheck"]["RefusalThreshold"],
            "result": data['moderationResults']['responseModeration']['refusalCheck']['result']
        },
        "summary": {
            "status": data['moderationResults']['responseModeration']["summary"]["status"],
            "reason": data['moderationResults']['responseModeration']["summary"]["reason"]
        }
            }
    },
    "Moderation_layer_time": data['Moderation_layer_time'],
    "portfolioName": data['portfolioName'],
    "accountName": data['accountName']
      }
        es_data.append(es_doc)
        # print(es_data)

        # Upload data to Elasticsearch if it doesn't already exist
        
        # for doc in es_data:
        #     print("!!!!!!!!!!!!!!")
        #     print(type(doc))
        #     print(str(doc["uniqueid"]))
        #     id = str(doc["uniqueid"])
        #     #del doc["uniqueid"]
        #     doc["uniqueid"]=str(doc["uniqueid"])
        #     es.index(index=index_name,id=id,document=doc)
        #     print("22222222222222222222")
        for doc in es_data:
            try:
                es.index(index=index_name, body=doc)
                print("DOC INSERTED IN THE ELASTIC", doc)
            except Exception as e:
                print("Error occurred while inserting document")    
            
            
        # print("ELASTIC DATA AFTER INSERTION", es_data)
        es.indices.refresh(index=index_name) 
            
            
        # print("ELASTIC DATA AFTER INSERTION", es_data)
        # es.indices.refresh(index=index_name)

        # es.indices.refresh(index=index_name)
        # print("333333333333333333333333")
        # # Display indices
        # indices = es.indices.get_alias()
        # for index in indices:
        #     print(index)