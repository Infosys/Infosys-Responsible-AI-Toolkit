'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import pytz
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
load_dotenv()
import os
import json
from mapper.coupledmoderationtelemetrydata import ModerationResults,completionResponse
from service.elasticconnectionservice import es
from middleware.text_anonymize import textAnonymize
def coupledModerationElasticDataPush(data):
        if data.Moderation_layer_time is not None:
            moderation_layer_time = data.Moderation_layer_time.dict()
        else:
            moderation_layer_time = None

        anonymize_flag = getattr(data, 'anonymize', True) 
        input_prompt =data.moderationResults.requestModeration.text
        choices_text = data.choices[0].text
        responseModeration_generatedText=data.moderationResults.responseModeration.generatedText
        if anonymize_flag is not False:  
            try:
                
                input_prompt = textAnonymize(input_prompt)
                choices_text = textAnonymize(choices_text)
                responseModeration_generatedText=textAnonymize(responseModeration_generatedText)
            except Exception as e:
                print(f"Error occurred during anonymization: {e}")
                anonymize_flag=False
        else:
            print(f"Anonymization disabled - using original inputText: {input_prompt}")        
        data_dict = {
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
            "accountName":data.accountName,
            "anonymize":anonymize_flag
            }
        data_dict['moderationResults']['requestModeration']['text']=input_prompt
        data_dict['choices']['text']=choices_text
        data_dict['moderationResults']['responseModeration']['generatedText']=responseModeration_generatedText
        print("ELASTIC SERVER AVAILABLE.....?",es.ping())
        
        now = datetime.now()

        index_name = 'couplemoderationindexv3'
        if not es.indices.exists(index=index_name):
            

            index_body = {
    "mappings": {
        "properties": {
            "uniqueid": {"type": "keyword"},
            "object": {"type": "keyword"},
            "userid": {"type": "keyword"},
            "lotNumber": {"type": "keyword"},
            "created": {"type": "date"},
            "anonymize": {"type": "keyword"},
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

            es.indices.create(index=index_name, body=index_body)



    
        
        es_data = []
        

        toxicity_check = data_dict.get('moderationResults', {}).get('requestModeration', {}).get('toxicityCheck', {})
        toxicity_score = toxicity_check.get('toxicityScore', [{}])
        toxic_scores = toxicity_score[0].get('toxicScore', [{}]) if toxicity_score else [{}]
        
        toxicity_check_response = data_dict.get('moderationResults', {}).get('responseModeration', {}).get('toxicityCheck', {})
        toxicity_score_response = toxicity_check_response.get('toxicityScore', [{}])
        toxic_scores_response = toxicity_score_response[0].get('toxicScore', [{}]) if toxicity_score_response else [{}]
        
        restrictedTopic_response = data_dict.get('moderationResults', {}).get('responseModeration', {}).get('restrictedtopic', {})
        restrictedTopic_score_response = restrictedTopic_response.get('topicScores', [{}])
        restrictedTopic_scores_response = restrictedTopic_score_response[0].get('topicScores', [{}]) if restrictedTopic_score_response else [{}]
        es_doc =  {
    "uniqueid": data_dict['uniqueid'],
    "object": data_dict['object'],
    "userid": data_dict['userid'],
    "lotNumber": data_dict['lotNumber'],
    "created": now,
    "model": data_dict['model'],
    "choices": 
        {
        "text": data_dict['choices']['text'],
        "index": data_dict['choices']['index'],
        "finishReason": data_dict['choices']['finishReason']
        }
    ,
    "moderationResults": {
        "requestModeration": {
        "text": data_dict['moderationResults']['requestModeration']['text'],
        "promptInjectionCheck": {
            "injectionConfidenceScore": data_dict['moderationResults']['requestModeration']['promptInjectionCheck']['injectionConfidenceScore'],
            "injectionThreshold": data_dict['moderationResults']['requestModeration']['promptInjectionCheck']['injectionThreshold'],
            "result": data_dict['moderationResults']['requestModeration']['promptInjectionCheck']['result']
        },
        "jailbreakCheck": {
            "jailbreakSimilarityScore": data_dict['moderationResults']['requestModeration']['jailbreakCheck']['jailbreakSimilarityScore'],
            "jailbreakThreshold": data_dict['moderationResults']['requestModeration']['jailbreakCheck']['jailbreakThreshold'],
            "result": data_dict['moderationResults']['requestModeration']['jailbreakCheck']['result']
        },
        "privacyCheck": {
            "entitiesRecognised": data_dict['moderationResults']['requestModeration']['privacyCheck']['entitiesRecognised'],
            "entitiesConfiguredToBlock": data_dict['moderationResults']['requestModeration']['privacyCheck']['entitiesConfiguredToBlock'],
            "result": data_dict['moderationResults']['requestModeration']['privacyCheck']['result']
        },
        "profanityCheck": {
            "profaneWordsIdentified": data_dict['moderationResults']['requestModeration']['profanityCheck']['profaneWordsIdentified'],
            "profaneWordsthreshold": data_dict['moderationResults']['requestModeration']['profanityCheck']['profaneWordsthreshold'],
            "result": data_dict['moderationResults']['requestModeration']['profanityCheck']['result']
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
            "topicScores": data_dict['moderationResults']['responseModeration']['restrictedtopic']['topicScores'],
            "topicThreshold": data_dict['moderationResults']['requestModeration']['restrictedtopic']['topicThreshold'],
            "result": data_dict['moderationResults']['requestModeration']['restrictedtopic']['result'],
            "topicTypesConfiguredToBlock": data_dict['moderationResults']['requestModeration']['restrictedtopic']['topicTypesConfiguredToBlock'],
            "topicTypesRecognised": data_dict['moderationResults']['requestModeration']['restrictedtopic']['topicTypesRecognised'],
        },
        "textQuality": {
            "readabilityScore": data_dict['moderationResults']['requestModeration']["textQuality"]["readabilityScore"],
            "textGrade": data_dict['moderationResults']['requestModeration']["textQuality"]["textGrade"]
        },
        "refusalCheck": {
            "refusalSimilarityScore": data_dict['moderationResults']['requestModeration']["refusalCheck"]["refusalSimilarityScore"],
            "RefusalThreshold": data_dict['moderationResults']['requestModeration']["refusalCheck"]["RefusalThreshold"],
            "result": data_dict['moderationResults']['requestModeration']['refusalCheck']['result']
        },
        "customThemeCheck": {
            "customSimilarityScore": data_dict['moderationResults']['requestModeration']["customThemeCheck"]["customSimilarityScore"],
            "themeThreshold": data_dict['moderationResults']['requestModeration']["customThemeCheck"]["themeThreshold"],
            "result": data_dict['moderationResults']['requestModeration']['customThemeCheck']['result']
        },
        "randomNoiseCheck": 
        {
            "smoothLlmScore": data_dict['moderationResults']['requestModeration']['randomNoiseCheck']['smoothLlmScore'],
            "smoothLlmThreshold": data_dict['moderationResults']['requestModeration']['randomNoiseCheck']['smoothLlmThreshold'],
            "result": data_dict['moderationResults']['requestModeration']['randomNoiseCheck']['result']
        },
        "advancedJailbreakCheck": {
            "text": data_dict['moderationResults']['requestModeration']['advancedJailbreakCheck']['text'],
            "result": data_dict['moderationResults']['requestModeration']['advancedJailbreakCheck']['result']
        },
        "summary": {
            "status": data_dict['moderationResults']['requestModeration']['summary']['status'],
            "reason": data_dict['moderationResults']['requestModeration']['summary']['reason']
        }
        },
        "responseModeration": {
            "generatedText": data_dict['moderationResults']['responseModeration']['generatedText'],
            "privacyCheck": {
                "entitiesRecognised": data_dict['moderationResults']['responseModeration']['privacyCheck']['entitiesRecognised'],
                "entitiesConfiguredToBlock": data_dict['moderationResults']['responseModeration']['privacyCheck']['entitiesConfiguredToBlock'],
                "result": data_dict['moderationResults']['responseModeration']['privacyCheck']['result']
            },
            "profanityCheck": {
                "profaneWordsIdentified": data_dict['moderationResults']['responseModeration']['profanityCheck']['profaneWordsIdentified'],
                "profaneWordsthreshold": data_dict['moderationResults']['requestModeration']['profanityCheck']['profaneWordsthreshold'],
                "result": data_dict['moderationResults']['responseModeration']['profanityCheck']['result']
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
                "topicThreshold": data_dict['moderationResults']['responseModeration']['restrictedtopic']['topicThreshold'],
                "result": data_dict['moderationResults']['responseModeration']['restrictedtopic']['result'],
                "topicTypesConfiguredToBlock": data_dict['moderationResults']['responseModeration']['restrictedtopic']['topicTypesConfiguredToBlock'],
                "topicTypesRecognised": data_dict['moderationResults']['responseModeration']['restrictedtopic']['topicTypesRecognised'],
                
            },
            "textQuality": {
            "readabilityScore": data_dict['moderationResults']['responseModeration']["textQuality"]["readabilityScore"],
            "textGrade": data_dict['moderationResults']['responseModeration']["textQuality"]["textGrade"]
        },
        "textRelevanceCheck": {
            "PromptResponseSimilarityScore": data_dict['moderationResults']['responseModeration']["textRelevanceCheck"]["PromptResponseSimilarityScore"]
        },
        "refusalCheck": {
            "refusalSimilarityScore": data_dict['moderationResults']['responseModeration']["refusalCheck"]["refusalSimilarityScore"],
            "RefusalThreshold": data_dict['moderationResults']['responseModeration']["refusalCheck"]["RefusalThreshold"],
            "result": data_dict['moderationResults']['responseModeration']['refusalCheck']['result']
        },
        "summary": {
            "status": data_dict['moderationResults']['responseModeration']["summary"]["status"],
            "reason": data_dict['moderationResults']['responseModeration']["summary"]["reason"]
        }
            }
    },
    "Moderation_layer_time": data_dict['Moderation_layer_time'],
    "portfolioName": data_dict['portfolioName'],
    "accountName": data_dict['accountName'],
    "anonymize": data_dict['anonymize']
      }
        es_data.append(es_doc)

        for doc in es_data:
            try:
                es.index(index=index_name, body=doc)
                print("DOC INSERTED IN THE ELASTIC")
            except Exception as e:
                print("Error occurred while inserting document")    
            
            
        es.indices.refresh(index=index_name) 
            
        return doc