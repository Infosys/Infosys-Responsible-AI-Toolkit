import json
import logging
import tempfile
from presidio_analyzer import AnalyzerEngine, BatchAnalyzerEngine
from presidio_analyzer import Pattern, PatternRecognizer
from presidio_anonymizer import BatchAnonymizerEngine
from privacy.service.imagePrivacy import AttributeDict, ImagePrivacy
from privacy.service.api_req import ApiCall
from privacy.service.__init__ import AttributeDict,registry,admin_par,update_session_dict,error_dict,roberta_recog,ranha_recog
from privacy.util.special_recognizers.DataListRecognizer import DataListRecognizer
from privacy.config.logger import request_id_var

log = logging.getLogger(__name__)

class JSONService:
    @staticmethod
    def anonymize_json(payload):
        try:
            log.debug("Entering anonymize_json function")

            payload = AttributeDict(payload)
            if payload.portfolio is not None or payload.account is not None:
                response_value = ApiCall.request(AttributeDict({"portfolio": payload.portfolio, "account": payload.account}))
                if response_value is None:
                    return None

            file = payload["file"]
            keys_to_skip = payload["keys_to_skip"]
            pii_entities_to_be_redacted=[]
            if payload["pii_entities_to_be_redacted"] is not None:
               pii_entities_to_be_redacted=payload["pii_entities_to_be_redacted"].split(',')
            score_threshold=0
            if payload["score_threshold"] is not None:
                 score_threshold=payload["score_threshold"]     
            acc_name=None
            if(payload.portfolio!=None):
                acc_name=AttributeDict({"portfolio":payload.portfolio,"account":payload.account})
            nlp=payload["nlp"]
            exclusion=payload.exclusion.split(',') if payload.exclusion is not None else []
 
            sp_recog=None
            if(nlp=="roberta"):
                sp_recog=[roberta_recog]
            if(nlp=="ranha"):
                if pii_entities_to_be_redacted is None and  acc_name is None:
                    pii_entities_to_be_redacted=list(set(ranha_recog.supported_entities+registry.get_supported_entities()))
                sp_recog=[ranha_recog]
             

            # Read the JSON file into a dictionary or list
            data = json.load(file.file)
            log.debug("Original JSON: " + str(data))

            # Initialize the analyzer and anonymizer engines
            analyzer = AnalyzerEngine()
            batch_analyzer = BatchAnalyzerEngine(analyzer_engine=analyzer)
            batch_anonymizer = BatchAnonymizerEngine()

            # Process the input dynamically based on its type
            if isinstance(data, dict):
                anonymized_data = JSONService.process_dict(data, batch_analyzer, batch_anonymizer, "en", keys_to_skip,acc_name,exclusion,pii_entities_to_be_redacted,score_threshold,sp_recog)
            elif isinstance(data, list):
                anonymized_data = JSONService.process_list(data, batch_analyzer, batch_anonymizer, "en", keys_to_skip,acc_name,exclusion,pii_entities_to_be_redacted,score_threshold,sp_recog)
            else:
                raise ValueError("Unsupported data type")

            # Convert the anonymized data to JSON with indentation
            anonymized_json = json.dumps(anonymized_data, indent=3)
            log.debug("Anonymized JSON: " + anonymized_json)

            # Save the JSON to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
                temp_file.write(anonymized_json.encode())

            log.debug("Returning from anonymize_json function")
            return anonymized_json
        except Exception as e:
            log.error(str(e))
            raise RuntimeError(e)

    @staticmethod
    def process_dict(data, batch_analyzer, batch_anonymizer, language, keys_to_skip,acc_name,exclusion,pii_entities_to_be_redacted,score_threshold,sp_recog):
        anonymized_data = {}
        for key, value in data.items():
            if isinstance(value, list):
                anonymized_list = []
                for item in value:
                    if isinstance(item, dict):
                        # Flatten the nested structure
                        flattened_item = JSONService.flatten_json(item)
                        # Analyze the data
                        analyzer_results = []
                        if acc_name is None:
                            if pii_entities_to_be_redacted is None:
                                analyzer_results = batch_analyzer.analyze_dict(flattened_item, language="en", keys_to_skip=keys_to_skip, allow_list=exclusion, return_decision_process=True, score_threshold=score_threshold,ad_hoc_recognizers=sp_recog)
                            else:
                                try:
                                    analyzer_results = batch_analyzer.analyze_dict(flattened_item, language="en", keys_to_skip=keys_to_skip,allow_list=exclusion,entities=pii_entities_to_be_redacted,return_decision_process = True,score_threshold=score_threshold,ad_hoc_recognizers=sp_recog)
                                except Exception as e:
                                        log.error(str(e))
                                        raise RuntimeError(e)
                        
                        

                        else:
                            pre_entity=[]
                            data_list_ent = []

                            response_value = ApiCall.request(acc_name)
                            if response_value is None:
                                return None
                            if response_value == 404:

                                return response_value
                            entity_type,datalist,pre_entity=response_value
                            for d in range(len(datalist)):
                                record=ApiCall.getRecord(entity_type[d])
                                record=AttributeDict(record)
                                log.debug("Record====="+str(record))

                                    
                                if(record.RecogType=="Data"):

                                        data_recog=(DataListRecognizer(terms=datalist[d],entitie=[entity_type[d]]))
                                        registry.add_recognizer(data_recog)


                                        update_session_dict(entity_type[d], datalist[d])
                                        data = {entity_type[d]: datalist[d]}
                                        data_list_ent.append(data)
                                
                                elif(record.RecogType=="Pattern" and record.isPreDefined=="No"):
                                        context_obj=record.Context.split(',')
                                        pattern="|".join(datalist[d])
                                         
                                        log.debug("pattern="+str(pattern))
                                        pattern_obj = Pattern(name=entity_type[d],
                                                                    regex=pattern,
                                                                    score=record.Score)
                                        pattern_recog = PatternRecognizer(supported_entity=entity_type[d],
                                                                                patterns=[pattern_obj], context=context_obj)
                                        registry.add_recognizer(pattern_recog)
                        # Anonymize the data
                            analyzer_results = batch_analyzer.analyze_dict(flattened_item, language="en", keys_to_skip=keys_to_skip,allow_list=exclusion,entities=entity_type+pre_entity,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"],ad_hoc_recognizers=sp_recog)

                        anonymizer_results = batch_anonymizer.anonymize_dict(analyzer_results)
                        log.debug("Anonymizer results: " + str(anonymizer_results))

                        anonymized_list.append(anonymizer_results)
                    else:
                        anonymized_list.append(item)
                anonymized_data[key] = anonymized_list
            else:
                anonymized_data[key] = value
        return anonymized_data

    @staticmethod
    def process_list(data, batch_analyzer, batch_anonymizer, language, keys_to_skip, acc_name, exclusion, pii_entities_to_be_redacted,score_threshold, sp_recog):
        anonymized_list = []
        for item in data:
            if isinstance(item, dict):
                # Flatten the nested structure
                flattened_item = JSONService.flatten_json(item)
                        # Analyze the data
                analyzer_results = []
                if acc_name is None:
                    if pii_entities_to_be_redacted is None:
                        analyzer_results = batch_analyzer.analyze_dict(flattened_item, language="en", keys_to_skip=keys_to_skip,allow_list=exclusion,return_decision_process = True,score_threshold=score_threshold,ad_hoc_recognizers=sp_recog)
                    else:
                        try:
                            analyzer_results = batch_analyzer.analyze_dict(flattened_item, language="en", keys_to_skip=keys_to_skip,allow_list=exclusion,entities=pii_entities_to_be_redacted,return_decision_process = True,score_threshold=score_threshold,ad_hoc_recognizers=sp_recog)
                        except Exception as e:
                                log.error(str(e))
                                raise RuntimeError(e)
                
                

                else:
                    pre_entity=[]
                    data_list_ent = []

                    response_value = ApiCall.request(acc_name)
                    if response_value == None:
                            return None
                    if(response_value==404):
                             
                            return response_value
                    entity_type,datalist,pre_entity=response_value
                    for d in range(len(datalist)):
                        record=ApiCall.getRecord(entity_type[d])
                        record=AttributeDict(record)
                        log.debug("Record====="+str(record))

                            
                        if(record.RecogType=="Data"):

                                data_recog=(DataListRecognizer(terms=datalist[d],entitie=[entity_type[d]]))
                                registry.add_recognizer(data_recog)


                                update_session_dict(entity_type[d], datalist[d])
                                data = {entity_type[d]: datalist[d]}
                                data_list_ent.append(data)
                        
                        elif(record.RecogType=="Pattern" and record.isPreDefined=="No"):
                                context_obj=record.Context.split(',')
                                pattern="|".join(datalist[d])
                                 
                                log.debug("pattern="+str(pattern))
                                pattern_obj = Pattern(name=entity_type[d],
                                                            regex=pattern,
                                                            score=record.Score)
                                pattern_recog = PatternRecognizer(supported_entity=entity_type[d],
                                                                        patterns=[pattern_obj], context=context_obj)
                                registry.add_recognizer(pattern_recog)
                # Anonymize the data
                    analyzer_results = batch_analyzer.analyze_dict(flattened_item, language="en", keys_to_skip=keys_to_skip,allow_list=exclusion,entities=entity_type+pre_entity,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"],ad_hoc_recognizers=sp_recog)

                anonymizer_results = batch_anonymizer.anonymize_dict(analyzer_results)
                log.debug("Anonymizer results: " + str(anonymizer_results))

                anonymized_list.append(anonymizer_results)
                 
            else:
                anonymized_list.append(item)
        return anonymized_list

    @staticmethod
    def flatten_json(y):
        out = {}

        def flatten(x, name=''):
            if type(x) is dict:
                for a in x:
                    flatten(x[a], name + a + '_')
            elif type(x) is list:
                i = 0
                for a in x:
                    flatten(a, name + str(i) + '_')
                    i += 1
            else:
                out[name[:-1]] = x

        flatten(y)
        return out

    @staticmethod
    def reconstruct_json(flattened_json):
        if isinstance(flattened_json, list):
            return [JSONService.reconstruct_json(item) if isinstance(item, dict) else item for item in flattened_json]
        reconstructed = {}
        for key, value in flattened_json.items():
            parts = key.split('_')
            current = reconstructed
            for part in parts[:-1]:
                if part.isdigit():
                    part = int(part)
                    if not isinstance(current, list):
                        current = []
                    while len(current) <= part:
                        current.append({})
                    current = current[part]
                else:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
            current[parts[-1]] = value
        return reconstructed