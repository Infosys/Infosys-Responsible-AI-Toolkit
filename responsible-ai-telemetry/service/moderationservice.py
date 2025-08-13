'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import encodings
from elasticsearch import Elasticsearch,helpers
import time
import elasticsearch.exceptions as es_exceptions
import pymongo
from datetime import datetime, timedelta
import pytz
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
load_dotenv()
import os
import json
from bson import ObjectId
from mapper.moderationtelemetrydata import ModerationResults
from service.elasticconnectionservice import es
import queue
data_queue = queue.Queue()
last_insert_time = time.time()
chunk_size = int(os.getenv("CHUNK_SIZE"))
delay = int(os.getenv("DELAY"))
def moderationElasticDataPush(data):
        if data.Moderation_layer_time is not None:
            moderation_layer_time = data.Moderation_layer_time.dict()
        else:
            moderation_layer_time = None
        
        data = {"_id": data.uniqueid,"lotNumber": data.lotNumber,"userid": data.userid,"portfolioName":data.portfolioName, "accountName":data.accountName,"created":data.created, "moderationResults": data.moderationResults.dict(),"Moderation_layer_time":moderation_layer_time}
        now = datetime.now()
        # Index Creation
        index_name = 'moderationindexv1'
        if not es.indices.exists(index=index_name):
            index_body = {
                'mappings': {
                    'properties': {
                        'lotNumber': {'type': 'keyword'},
                        'userid': {'type': 'keyword'},
                        'uniqueid': {'type': 'keyword'},
                        'timestamp': {'type': 'date'},
                        'accountName': {'type': 'keyword'},
                        'portfolioName': {'type': 'keyword'},
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
                        },
                        'Moderation_layer_time': {
                        'properties': {
                            'Time_for_each_individual_check': {
                                'properties': {
                                    'Privacy Check': {'type': 'keyword'},
                                    'Text Quality Check': {'type': 'keyword'},
                                    'Toxicity Check': {'type': 'keyword'},
                                    'Prompt Injection Check': {'type': 'keyword'},
                                    'Profanity Check': {'type': 'keyword'},
                                    'Restricted Topic Check': {'type': 'keyword'},
                                    'Jailbreak Check': {'type': 'keyword'},
                                    'Refusal Check': {'type': 'keyword'},
                                    'Custom Theme Check': {'type': 'keyword'}
                                }
                            },
                            'Time_taken_by_each_model': {
                                'properties': {
                                    'Privacy Check': {'type': 'keyword'},
                                    'Toxicity Check': {'type': 'keyword'},
                                    'Prompt Injection Check': {'type': 'keyword'},
                                    'Restricted Topic Check': {'type': 'keyword'},
                                    'Jailbreak Check': {'type': 'keyword'},
                                    'Custom Theme Check': {'type': 'keyword'}
                                }
                            },
                            'Time_taken_By_API': {
                                'properties': {
                                    'Toxicity Check': {'type': 'keyword'},
                                    'Prompt Injection Check': {'type': 'keyword'},
                                    'Profanity Check': {'type': 'keyword'},
                                    'Restricted Topic Check': {'type': 'keyword'},
                                    'Jailbreak Check': {'type': 'keyword'},
                                    'Refusal Check': {'type': 'keyword'},
                                    'Custom Theme Check': {'type': 'keyword'}
                                }
                            },
                            'Time_By_Model': {'type': 'keyword'},
                            'Latency_By_API': {'type': 'keyword'},
                            'Time_By_Validation': {'type': 'keyword'},
                            'Time_Difference_mdoel_and_validity': {'type': 'keyword'},
                            'Time_Diffrence_btwn_ML_and_MM': {'type': 'keyword'},
                            'Total_time_for_moderation_Check': {'type': 'keyword'}
                        }
                        }
                    }
                }
            }
            es.indices.create(index=index_name, body=index_body)
        mongo_data = data
        es_data = []
        # print("MONGODATA=======",type(mongo_data))
        i = 0
        i += 1
        # print("COUNTER", i)
        es_doc = {
        'lotNumber': data['lotNumber'],
        'userid': data['userid'],
        'uniqueid': data['_id'],
        'timestamp': data['created'],
        'accountName': data['accountName'],
        'portfolioName': data['portfolioName'],
        'moderationResults': {
            'text': data['moderationResults']['text'],
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
            },
            "Moderation_layer_time": data['Moderation_layer_time']
            }
        es_data.append(es_doc)
        # Collect the data in the queue
        data_queue.put(es_data)
        global last_insert_time
        # Check if it's time to perform bulk insertion
        if (data_queue.qsize() >= chunk_size) or (last_insert_time is None) or (time.time() - last_insert_time >= delay):
            # Perform bulk insertion
            es_data = []
            while not data_queue.empty():
                es_data.extend(data_queue.get())
                # print("ES DATA IN WHILE", es_data)

            try:
                # print("ES DATA IN TRYs", es_data)
                helpers.bulk(es, es_data, index=index_name)
                print("Documents indexed successfully.")
            except Exception as e:
                print("Error indexing documents")

            last_insert_time = time.time()  # Update the last_insert_time
        else:
            # Calculate the chunk size left and time left for next insertion
            chunk_size_left = max(0, chunk_size - data_queue.qsize())
            print(f"Chunk size left for next insertion: {chunk_size_left}")
            time_left = max(0, delay - (time.time() - last_insert_time))
            print(f"Time left for next insertion: {time_left} seconds")

        # Refresh indices
        es.indices.refresh(index=index_name)

        # # Display indices
        # indices = es.indices.get_alias()


        
from mapper.coupledmoderationrequestdata import CoupledModerationRequestData


def moderationRequestElasticDataPush(data):
    # Prepare the moderation data
    moderation_data = {
        # "_id": data.userid,  # Assuming userid is unique
        "lotNumber": data.lotNumber,
        "userid": data.userid,
        "accountName": data.AccountName,
        "portfolioName": data.PortfolioName,
        "created": datetime.now(),
        "moderationChecks": data.ModerationChecks,
        "moderationCheckThresholds": data.ModerationCheckThresholds.dict()
    }

    index_name = 'moderationrequestindex'

    # Index Creation
    if not es.indices.exists(index=index_name):
        index_body = {
            'mappings': {
                'properties': {
                    'lotNumber': {'type': 'keyword'},
                    'userid': {'type': 'keyword'},
                    'accountName': {'type': 'keyword'},
                    'portfolioName': {'type': 'keyword'},
                    'created': {'type': 'date'},
                    'moderationChecks': {'type': 'keyword'},
                    'moderationCheckThresholds': {
                        'properties': {
                            'PromptinjectionThreshold': {'type': 'float'},
                            'JailbreakThreshold': {'type': 'float'},
                            'PiientitiesConfiguredToBlock': {'type': 'keyword'},
                            'RefusalThreshold': {'type': 'float'},
                            'ToxicityThresholds': {
                                'properties': {
                                    'ToxicityThreshold': {'type': 'float'},
                                    'SevereToxicityThreshold': {'type': 'float'},
                                    'ObsceneThreshold': {'type': 'float'},
                                    'ThreatThreshold': {'type': 'float'},
                                    'InsultThreshold': {'type': 'float'},
                                    'IdentityAttackThreshold': {'type': 'float'},
                                    'SexualExplicitThreshold': {'type': 'float'}
                                }
                            },
                            'ProfanityCountThreshold': {'type': 'integer'},
                            'RestrictedtopicDetails': {
                                'properties': {
                                    'RestrictedtopicThreshold': {'type': 'float'},
                                    'Restrictedtopics': {'type': 'keyword'}
                                }
                            },
                            'CustomTheme': {
                                'properties': {
                                    'Themename': {'type': 'keyword'},
                                    'Themethresold': {'type': 'float'},
                                    'ThemeTexts': {'type': 'keyword'}
                                }
                            }
                        }
                    }
                }
            }
        }
        es.indices.create(index=index_name, body=index_body)

    # Insert the moderation data into Elasticsearch
    try:
        es.index(index=index_name, body=moderation_data)
        print("Document indexed successfully.")
    except Exception as e:
        print("Error indexing document:", e)

## For Coupled Moderation

def coupledRequestModerationElasticDataPush(data: CoupledModerationRequestData):
    # Prepare the moderation data
    moderation_data = {
        # "_id": data.userid,  # Assuming userid is unique
        "lotNumber": data.lotNumber,
        "userid": data.userid,
        "accountName": data.AccountName,
        "portfolioName": data.PortfolioName,
        "created": datetime.now(),
        "model_name": data.model_name,
        "translate": data.translate,
        "temperature": data.temperature,
        "LLMinteraction": data.LLMinteraction,
        "PromptTemplate": data.PromptTemplate,
        "EmojiModeration": data.EmojiModeration,
        "Prompt": data.Prompt,
        "InputModerationChecks": data.InputModerationChecks,
        "OutputModerationChecks": data.OutputModerationChecks,
        "llm_BasedChecks": data.llm_BasedChecks,
        "ModerationCheckThresholds": data.ModerationCheckThresholds.dict()
    }

    index_name = 'coupledmoderationrequestindex'

    # Index Creation
    if not es.indices.exists(index=index_name):
        index_body = {
            'mappings': {
                'properties': {
                    'lotNumber': {'type': 'keyword'},
                    'userid': {'type': 'keyword'},
                    'accountName': {'type': 'keyword'},
                    'portfolioName': {'type': 'keyword'},
                    'created': {'type': 'date'},
                    'model_name': {'type': 'keyword'},
                    'translate': {'type': 'keyword'},
                    'temperature': {'type': 'keyword'},
                    'LLMinteraction': {'type': 'keyword'},
                    'PromptTemplate': {'type': 'keyword'},
                    'EmojiModeration': {'type': 'keyword'},
                    'Prompt': {'type': 'text'},
                    'InputModerationChecks': {'type': 'keyword'},
                    'OutputModerationChecks': {'type': 'keyword'},
                    'llm_BasedChecks': {'type': 'keyword'},
                    'ModerationCheckThresholds': {
                        'properties': {
                            'PromptinjectionThreshold': {'type': 'float'},
                            'JailbreakThreshold': {'type': 'float'},
                            'PiientitiesConfiguredToBlock': {'type': 'keyword'},
                            'RefusalThreshold': {'type': 'float'},
                            'ToxicityThresholds': {
                                'properties': {
                                    'ToxicityThreshold': {'type': 'float'},
                                    'SevereToxicityThreshold': {'type': 'float'},
                                    'ObsceneThreshold': {'type': 'float'},
                                    'ThreatThreshold': {'type': 'float'},
                                    'InsultThreshold': {'type': 'float'},
                                    'IdentityAttackThreshold': {'type': 'float'},
                                    'SexualExplicitThreshold': {'type': 'float'}
                                }
                            },
                            'ProfanityCountThreshold': {'type': 'integer'},
                            'RestrictedtopicDetails': {
                                'properties': {
                                    'RestrictedtopicThreshold': {'type': 'float'},
                                    'Restrictedtopics': {'type': 'keyword'}
                                }
                            },
                            'CustomTheme': {
                                'properties': {
                                    'Themename': {'type': 'keyword'},
                                    'Themethresold': {'type': 'float'},
                                    'ThemeTexts': {'type': 'keyword'}
                                }
                            },
                            'SmoothLlmThreshold': {
                                'properties': {
                                    'input_pertubation': {'type': 'float'},
                                    'number_of_iteration': {'type': 'integer'},
                                    'SmoothLlmThreshold': {'type': 'float'}
                                }
                            }
                        }
                    }
                }
            }
        }
        es.indices.create(index=index_name, body=index_body)

    # Insert the moderation data into Elasticsearch
    try:
        es.index(index=index_name, body=moderation_data)
        print("Document indexed successfully.")
    except Exception as e:
        print("Error indexing document:", e)