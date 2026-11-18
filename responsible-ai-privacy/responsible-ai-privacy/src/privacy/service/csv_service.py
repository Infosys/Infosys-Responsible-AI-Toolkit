import pandas as pd
import io
import logging
import tempfile
from presidio_analyzer import AnalyzerEngine, BatchAnalyzerEngine
from presidio_anonymizer import AnonymizerEngine, BatchAnonymizerEngine
from privacy.service.imagePrivacy import AttributeDict, ImagePrivacy
from privacy.service.api_req import ApiCall
from privacy.config.logger import request_id_var

from privacy.service.__init__ import AttributeDict,registry,admin_par,update_session_dict,roberta_recog,ranha_recog
from privacy.util.special_recognizers.DataListRecognizer import DataListRecognizer
from privacy.util.special_recognizers.fakeData import FakeDataGenerate
from privacy.util.special_recognizers.fakeDataCSV import FakeDataCSVGenerate



log = logging.getLogger(__name__)

class CSVService:
    @staticmethod
    def csv_anonymize(payload):
        try:
            payload = AttributeDict(payload)
            if(payload.portfolio is not None or payload.account is not None):
                response_value=ApiCall.request(AttributeDict({"portfolio":payload.portfolio,"account":payload.account}))
                if(response_value==None):
                        return None
                
             
            file = payload["file"]
            keys_to_skip = payload["keys_to_skip"]
            pii_entities_to_be_redacted=[]
            if payload["pii_entities_to_be_redacted"] is not None:
               pii_entities_to_be_redacted=payload["pii_entities_to_be_redacted"].split(',')
                 
            acc_name=None
            if(payload.portfolio!=None):
                acc_name=AttributeDict({"portfolio":payload.portfolio,"account":payload.account})
            nlp=payload["nlp"]
            exclusion=payload.exclusion.split(',') if payload.exclusion != None else []
             
            sp_recog=None
            if(nlp=="roberta"):
                sp_recog=[roberta_recog]
            if(nlp=="ranha"):
                # registry.add_recognizer(ranha_recog)
                if(pii_entities_to_be_redacted==None and  acc_name==None):
                    pii_entities_to_be_redacted=list(set(ranha_recog.supported_entities+registry.get_supported_entities()))
                sp_recog=[ranha_recog]

            # Initialize the analyzer and anonymizer engines
            
            analyzer = AnalyzerEngine()
            batch_analyzer = BatchAnalyzerEngine(analyzer_engine=analyzer)
            batch_anonymizer = BatchAnonymizerEngine()
            
            
            
            
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file.file)
            log.debug("Original DataFrame: " + str(df))
            
            # Convert DataFrame to dictionary
            dff = df.to_dict(orient="list")
            log.debug("CSV to dict: " + str(dff))
             
             
            # Analyze the data
            analyzer_results = []
            if(acc_name==None):
                
                if(pii_entities_to_be_redacted == None):
                    analyzer_results = batch_analyzer.analyze_dict(dff, language="en", keys_to_skip=keys_to_skip,allow_list=exclusion,return_decision_process = True,score_threshold=payload.score_threshold if payload.score_threshold is not None else 0,ad_hoc_recognizers=sp_recog)
                else:
                    try:
                        analyzer_results = batch_analyzer.analyze_dict(dff, language="en", keys_to_skip=keys_to_skip,allow_list=exclusion,entities=pii_entities_to_be_redacted,return_decision_process = True,score_threshold=payload.score_threshold if payload.score_threshold is not None else 0,ad_hoc_recognizers=sp_recog)
                    except Exception as e:
                        log.error(str(e))
                        raise e
            else:
                pre_entity = []
                dataist_ent = []

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
                            dataist_ent.append(data)
                    
                    elif(record.RecogType=="Pattern" and record.isPreDefined=="No"):
                            context_obj=record.Context.split(',')
                            pattern="|".join(datalist[d])
                             
                            log.debug("pattern="+str(pattern))
                            pattern_obj = Pattern(name=entity_type[d],
                                                        regex=pattern,
                                                        score=record.Score)
                            pattern_recog = PatternRecognizer(supported_entity=entity_type[d],
                                                                    patterns=[pattern_obj],context=context_obj)
                            registry.add_recognizer(pattern_recog)

                analyzer_results=batch_analyzer.analyze_dict(dff,language="en", keys_to_skip=keys_to_skip,allow_list=exclusion,entities=entity_type+pre_entity,score_threshold=admin_par[request_id_var.get()]["scoreTreshold"],ad_hoc_recognizers=sp_recog)
                log.debug("Analyzer results: " + str(analyzer_results))

             
            dfs=list(analyzer_results)
            dict_operators = {} 
            if payload.fakeData == True:
                fake_dict_operator,dfs = FakeDataCSVGenerate.fakeDataGeneration(dfs,list(dff))
                dict_operators.update(fake_dict_operator)
            # Anonymize the data
            anonymizer_results = batch_anonymizer.anonymize_dict(dfs)
            log.debug("Anonymizer results: " + str(anonymizer_results))

            # Convert the anonymized data back to a DataFrame
            anonymized_df = pd.DataFrame(anonymizer_results)
            log.debug("Anonymized DataFrame: " + str(anonymized_df))

            # Convert the DataFrame to CSV
            output = io.StringIO()
            anonymized_df.to_csv(output, index=False)
            output.seek(0)

            # Save the CSV to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
                temp_file.write(output.getvalue().encode())

            log.debug("Returning from csv_anonymize function")
            return output
        except Exception as e:
            log.error(str(e))
            log.error("Line No:"+str(e.__traceback__.tb_lineno))
            raise e
