'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import encodings
from elasticsearch import Elasticsearch,helpers
import time
import elasticsearch.exceptions as es_exceptions
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
import queue
data_queue = queue.Queue()
last_insert_time = time.time()
chunk_size = int(os.getenv("CHUNK_SIZE"))
delay = int(os.getenv("DELAY"))
import logging
logger = logging.getLogger(__name__)
CUSTOM_THEME_CHECK = 'Custom Theme Check'
JAILBREAK_CHECK = 'Jailbreak Check'
RESTRICTED_TOPIC_CHECK = 'Restricted Topic Check'
PROMPT_INJECTION_CHECK = 'Prompt Injection Check'
TOXICITY_CHECK = 'Toxicity Check'
def moderationElasticDataPush(data):
    try:
        logger.info(f"Processing Moderation Telemetry")
        if data.Moderation_layer_time is not None:
            moderation_layer_time = data.Moderation_layer_time.dict()
        else:
            moderation_layer_time = None

        input_prompt = data.moderationResults.dict().get('text')
        anonymize_flag = getattr(data, 'anonymize', True)
        if anonymize_flag is not False:
            try:
                    input_prompt = textAnonymize(input_prompt)
                    logger.info("Anonymization completed successfully.")
            except Exception as e:
                    logger.error(f"Anonymization error: {e}")
                    anonymize_flag=False
        else:
                logger.info(f"Anonymization disabled - using original inputText: {input_prompt}")           
        
      
        data_dict = {"_id": data.uniqueid,"lotNumber": data.lotNumber,"userid": data.userid,"Source":data.Source,"portfolioName":data.portfolioName, "accountName":data.accountName,"anonymize":anonymize_flag,"created":data.created, "moderationResults": data.moderationResults.dict(),"Moderation_layer_time":moderation_layer_time}
        data_dict['moderationResults']['text'] = input_prompt

        logger.info(f"Prepared data for indexing")
        now = datetime.now()
        index_name = 'moderationindexv1'
        if not es.indices.exists(index=index_name):
            index_body = {
                    'mappings': {
                        'properties': {
                            'lotNumber': {'type': 'keyword'},
                            'userid': {'type': 'keyword'},
                            'Source': {'type': 'keyword'},
                            'uniqueid': {'type': 'keyword'},
                            'timestamp': {'type': 'date'},
                            'accountName': {'type': 'keyword'},
                            'portfolioName': {'type': 'keyword'},
                            'anonymize': {'type': 'keyword'},
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
                                   
                                    'sentimentCheck': {
                                        'properties': {
                                            'score': {'type': 'float'},
                                            'threshold': {'type': 'float'},
                                            'result': {'type': 'keyword'}
                                        }
                                    },
                                    'invisibleTextCheck': {
                                        'properties': {
                                            'invisibleTextIdentified': {'type': 'keyword'},
                                            'result': {'type': 'keyword'}
                                        }
                                    },
                                    'gibberishCheck': {
                                        'properties': {
                                            'gibberishScore': {'type': 'object'},
                                            'threshold': {'type': 'float'},
                                            'result': {'type': 'keyword'}
                                        }
                                    },
                                    'bancodeCheck': {
                                        'properties': {
                                            'label': {'type': 'keyword'},
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
                                        TOXICITY_CHECK: {'type': 'keyword'},
                                        PROMPT_INJECTION_CHECK: {'type': 'keyword'},
                                        'Profanity Check': {'type': 'keyword'},
                                        RESTRICTED_TOPIC_CHECK: {'type': 'keyword'},
                                        JAILBREAK_CHECK: {'type': 'keyword'},
                                        'Refusal Check': {'type': 'keyword'},
                                        CUSTOM_THEME_CHECK: {'type': 'keyword'},
                                        'Sentiment Check': {'type': 'keyword'},
                                        'Invisible Text Check': {'type': 'keyword'},
                                        'Gibberish Check': {'type': 'keyword'},
                                        'Embed Check': {'type': 'keyword'}
                                    }
                                },
                                'Time_taken_by_each_model': {
                                    'properties': {
                                        'Privacy Check': {'type': 'keyword'},
                                        TOXICITY_CHECK: {'type': 'keyword'},
                                        PROMPT_INJECTION_CHECK: {'type': 'keyword'},
                                        RESTRICTED_TOPIC_CHECK: {'type': 'keyword'},
                                        JAILBREAK_CHECK: {'type': 'keyword'},
                                        CUSTOM_THEME_CHECK: {'type': 'keyword'},
                                        'Sentiment Check': {'type': 'keyword'},
                                        'Invisible Text Check': {'type': 'keyword'},
                                        'Gibberish Check': {'type': 'keyword'},
                                        'Embed Check': {'type': 'keyword'}
                                    }
                                },
                                'Time_taken_By_API': {
                                    'properties': {
                                        TOXICITY_CHECK: {'type': 'keyword'},
                                        PROMPT_INJECTION_CHECK: {'type': 'keyword'},
                                        'Profanity Check': {'type': 'keyword'},
                                        RESTRICTED_TOPIC_CHECK: {'type': 'keyword'},
                                        JAILBREAK_CHECK: {'type': 'keyword'},
                                        'Refusal Check': {'type': 'keyword'},
                                        CUSTOM_THEME_CHECK: {'type': 'keyword'}
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
        es_data = []
        i = 0
        i += 1
        # print("COUNTER", i)
        es_doc = {
            'lotNumber': data_dict['lotNumber'],
            'userid': data_dict['userid'],
            'Source': data_dict['Source'],
            'uniqueid': data_dict['_id'],
            'timestamp': data_dict['created'],
            'accountName': data_dict['accountName'],
            'portfolioName': data_dict['portfolioName'],
            'anonymize': data_dict['anonymize'],
            'moderationResults': {
                'text': data_dict['moderationResults']['text'],
                'promptInjectionCheck': {
                    'injectionConfidenceScore': data_dict['moderationResults']['promptInjectionCheck']['injectionConfidenceScore'],
                    'injectionThreshold': data_dict['moderationResults']['promptInjectionCheck']['injectionThreshold'],
                    'result': data_dict['moderationResults']['promptInjectionCheck']['result']
                },
                'jailbreakCheck': {
                    'jailbreakSimilarityScore': data_dict['moderationResults']['jailbreakCheck']['jailbreakSimilarityScore'],
                    'jailbreakThreshold': data_dict['moderationResults']['jailbreakCheck']['jailbreakThreshold'],
                    'result': data_dict['moderationResults']['jailbreakCheck']['result']
                },
                'privacyCheck': {
                    'entitiesRecognised': data_dict['moderationResults']['privacyCheck']['entitiesRecognised'],
                    'entitiesConfiguredToBlock': data_dict['moderationResults']['privacyCheck']['entitiesConfiguredToBlock'],
                    'result': data_dict['moderationResults']['privacyCheck']['result']
                },
                'profanityCheck': {
                    'profaneWordsIdentified': data_dict['moderationResults']['profanityCheck']['profaneWordsIdentified'],
                    'profaneWordsthreshold': data_dict['moderationResults']['profanityCheck']['profaneWordsthreshold'],
                    'result': data_dict['moderationResults']['profanityCheck']['result']
                },
                'toxicityCheck': {
                    'toxicityScore': data_dict['moderationResults']['toxicityCheck']['toxicityScore'],
                    'toxicitythreshold': data_dict['moderationResults']['toxicityCheck']['toxicitythreshold'],
                    'result': data_dict['moderationResults']['toxicityCheck']['result']
                },
                'restrictedtopic': {
                    'topicScores': data_dict['moderationResults']['restrictedtopic']['topicScores'],
                    'topicThreshold': data_dict['moderationResults']['restrictedtopic']['topicThreshold'],
                    'result': data_dict['moderationResults']['restrictedtopic']['result']
                },
                'textQuality': {
                    'readabilityScore': data_dict['moderationResults']['textQuality']['readabilityScore'],
                    'textGrade': data_dict['moderationResults']['textQuality']['textGrade']
                },
                'refusalCheck': {
                    'refusalSimilarityScore': data_dict['moderationResults']['refusalCheck']['refusalSimilarityScore'],
                    'RefusalThreshold': data_dict['moderationResults']['refusalCheck']['RefusalThreshold'],
                    'result': data_dict['moderationResults']['refusalCheck']['result']
                },
                'customThemeCheck': {
                    'customSimilarityScore': data_dict['moderationResults']['customThemeCheck']['customSimilarityScore'],
                    'themeThreshold': data_dict['moderationResults']['customThemeCheck']['themeThreshold'],
                    'result': data_dict['moderationResults']['customThemeCheck']['result']
                },
               
                'sentimentCheck': {
                    'score': data_dict['moderationResults']['sentimentCheck']['score'],
                    'threshold': data_dict['moderationResults']['sentimentCheck']['threshold'],
                    'result': data_dict['moderationResults']['sentimentCheck']['result']
                },
                'invisibleTextCheck': {
                    'invisibleTextIdentified': data_dict['moderationResults']['invisibleTextCheck']['invisibleTextIdentified'],
                    'result': data_dict['moderationResults']['invisibleTextCheck']['result']
                },
                'gibberishCheck': {
                    'gibberishScore': data_dict['moderationResults']['gibberishCheck']['gibberishScore'],
                    'threshold': data_dict['moderationResults']['gibberishCheck']['threshold'],
                    'result': data_dict['moderationResults']['gibberishCheck']['result']
                },
                'bancodeCheck': {
                    'label': data_dict['moderationResults']['bancodeCheck']['label'],
                    'result': data_dict['moderationResults']['bancodeCheck']['result']
                },
                'summary': {
                    'status': data_dict['moderationResults']['summary']['status'],
                    'reason': data_dict['moderationResults']['summary']['reason']
                }
                },
                "Moderation_layer_time": data_dict['Moderation_layer_time']
                }
        es_data.append(es_doc)
        data_queue.put(es_data)
        global last_insert_time
        if (data_queue.qsize() >= chunk_size) or (last_insert_time is None) or (time.time() - last_insert_time >= delay):
            es_data = []
            while not data_queue.empty():
                es_data.extend(data_queue.get())

            try:
                helpers.bulk(es, es_data, index=index_name)
                print("Documents indexed successfully.")
            except Exception as e:
                print("Error indexing documents")

            last_insert_time = time.time()  
        else:
            chunk_size_left = max(0, chunk_size - data_queue.qsize())
            print(f"Chunk size left for next insertion: {chunk_size_left}")
            time_left = max(0, delay - (time.time() - last_insert_time))
            print(f"Time left for next insertion: {time_left} seconds")

        es.indices.refresh(index=index_name)

        return es_doc
    except Exception as e:
        logger.error(f"Moderation telemetry processing failed: {e}")
        raise Exception(f"Processing failed: {e}")

        
from mapper.coupledmoderationrequestdata import CoupledModerationRequestData


def moderationRequestElasticDataPush(data):

    logger.info(f"Processing Moderation Request Telemetry")

    
    moderation_data = {
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
            return moderation_data  
    except Exception as e:
            print("Error indexing document:", e)



## For Coupled Moderation

def coupledRequestModerationElasticDataPush(data: CoupledModerationRequestData):
    # Prepare the moderation data
    
    logger.info(f"Processing Coupled Moderation Request Telemetry")
    anonymize_flag = getattr(data, 'anonymize', True)
    input_prompt=data.Prompt
    if anonymize_flag is not False:
        try:
                input_prompt = textAnonymize(data.Prompt)
                logger.info("Anonymization completed successfully.")
        except Exception as e:
                logger.error(f"Anonymization error: {e}")
                anonymize_flag=False

    moderation_data = {
        # "_id": data.userid,  # Assuming userid is unique
        "lotNumber": data.lotNumber,
        "userid": data.userid,
        "accountName": data.AccountName,
        "portfolioName": data.PortfolioName,
        "anonymize": anonymize_flag,
        "created": datetime.now(),
        "model_name": data.model_name,
        "translate": data.translate,
        "temperature": data.temperature,
        "LLMinteraction": data.LLMinteraction,
        "PromptTemplate": data.PromptTemplate,
        "EmojiModeration": data.EmojiModeration,
        "Prompt": input_prompt,
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
                    'anonymize' : {'type': 'keyword'},
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
        return moderation_data
    except Exception as e:
        print("Error indexing document:", e)