'''
License textMIT Licensehttps://mit-license.org/Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''



from privacy.mappers.mappers import (
    PIIEntity,
    PIIAnalyzeRequest,
    PIIAnalyzeResponse,
    PIIAnonymizeRequest,
    PIIAnonymizeResponse,
    PIIEncryptResponse,
    PIIDecryptRequest,
    PIIDecryptResponse,
    PIIPrivacyShieldRequest,
    PIIPrivacyShieldResponse,
    PrivacyShield
)
from presidio_anonymizer.entities import (RecognizerResult,
    OperatorResult,
    OperatorConfig)
from typing import List
from privacy.constants.local_constants import (DELTED_SUCCESS_MESSAGE)
from privacy.exception.exception import PrivacyNameNotEmptyError, PrivacyException, PrivacyNotFoundError

from privacy.config.logger import CustomLogger
log = CustomLogger()
from dotenv import load_dotenv
from privacy.config.logger import request_id_var
load_dotenv()
from faker import Faker
fake = Faker()

from privacy.util.special_recognizers.DataListRecognizer import DataListRecognizer
from privacy.service.__init__ import AttributeDict,admin_par,error_dict,select_nlp,roberta_recog,ranha_recog,registry
from privacy.service.api_req import ApiCall

from privacy.util.special_recognizers.fakeData import FakeDataGenerate
LINE_NO_LABEL = "Line No:"
from nltk.tokenize import word_tokenize,sent_tokenize
from transformers import XLMRobertaTokenizerFast
from presidio_anonymizer import AnonymizerEngine,DeanonymizeEngine
anonymizer = AnonymizerEngine()
deanonymizer = DeanonymizeEngine()
tokenizer=XLMRobertaTokenizerFast.from_pretrained("../models/roberta")
def chunk_text(text,chunk_size=500):
    sentences=sent_tokenize(text)
    chunks=[]
    current_chunk=[]
    text_position=0
    for sentence in sentences:
        sentence_start = text.find(sentence, text_position)
        if sentence_start==-1:
            sentence_start=text_position
        tokens=tokenizer.encode(" ".join(current_chunk+[sentence]),add_special_tokens=True)
        if len(tokens)<=chunk_size:
            current_chunk.append(sentence)
        else:
            if current_chunk:
                chunk_text_str = " ".join(current_chunk)
                # Fix: Ensure chunk_start is never negative
                search_start = max(0, text_position - len(chunk_text_str))
                chunk_start = text.find(chunk_text_str, search_start)
                if chunk_start == -1:
                    chunk_start = 0  # Fallback to beginning
                chunks.append((chunk_text_str, chunk_start))
                text_position = chunk_start + len(chunk_text_str)

            current_chunk=[sentence]
    if current_chunk:

        chunk_text_str = " ".join(current_chunk)
        search_start = max(0, text_position - len(chunk_text_str))
        chunk_start = text.find(chunk_text_str, search_start)
        if chunk_start == -1:
            chunk_start = max(0, text_position - len(chunk_text_str))
        chunks.append((chunk_text_str, chunk_start))

    return chunks

class TextPrivacy:
    @staticmethod
    def analyze(payload: PIIAnalyzeRequest) -> PIIAnalyzeResponse:
        print("Entering in analyze function")
        print(f"Received payload: {payload}")
        error_dict[request_id_var.get()] = []
        log.debug("Entering in analyze function")
        log.debug(f"payload: {payload}")
        pii_entities_to_be_redacted = payload.pii_entities_to_be_redacted
        try:
            if payload.exclusion_list is None:
                exclusion_list = []
            else:
                exclusion_list = payload.exclusion_list

            if payload.portfolio is None:
                privacy_obj = TextPrivacy()
                print("Calling privacy_obj.text_analyze with payload.input_text.")
                results = privacy_obj.text_analyze(
                    text=payload.input_text,
                    pii_entities_to_be_redacted=pii_entities_to_be_redacted,
                    exclusion=exclusion_list,
                    nlp=payload.nlp,
                    score_threshold=payload.score_threshold,
                )
            else:
                privacy_obj = TextPrivacy()
                print("Calling privacy_obj.text_analyze with payload.input_text.if payload is not None")
                results = privacy_obj.text_analyze(
                    text=payload.input_text,
                    acc_name=payload,
                    exclusion=exclusion_list,
                    nlp=payload.nlp,
                )
            if results is  None:
                return None
            if results == 404:
                return results
            if results == 482:
                return results
            pii_entity_list = []
            results = sorted(results, key=lambda i: i.start)
            print(f"Received {len(results)} raw results. Sorting them by start position.")

            for result in results:
                print(f"Processing result: type={result.entity_type}, start={result.start}, end={result.end}, score={result.score}")
                log.debug(f"result: {result}")
                obj_pii_entity = PIIEntity(
                    type=result.entity_type,
                    beginOffset=result.start,
                    endOffset=result.end,
                    score=result.score,
                    responseText=payload.input_text[result.start:result.end],
                )
                print(f"Created PIIEntity object: {obj_pii_entity}")
                log.debug(f"obj_pii_entity: {obj_pii_entity}")
                pii_entity_list.append(obj_pii_entity)
                del obj_pii_entity

            log.debug(f"pii_entity_list: {pii_entity_list}")
            print(f"Final list of PIIEntities: {pii_entity_list}")
            
            obj_pii_analyze_response = PIIAnalyzeResponse(PIIEntities=pii_entity_list)
            # gc.collect()
            print(("Returning from analyze function with PIIAnalyzeResponse object."))
            log.debug("Returning from analyze function")
            return obj_pii_analyze_response
        except Exception as e:
            log.error(str(e))
            log.error(LINE_NO_LABEL + str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            error_dict[request_id_var.get()].append(
                {
                    "UUID": request_id_var.get(),
                    "function": "text_analyzeMainFunction",
                    "msg": str(e.__class__.__name__),
                    "description": str(e) + LINE_NO_LABEL + str(e.__traceback__.tb_lineno),
                }
            )
            # ExceptionDb.create({"UUID":request_id_var.get(),"function":"text_analyzeMainFunction","msg":str(e.__class__.__name__),"description":str(e)+LINE_NO_LABEL+str(e.__traceback__.tb_lineno)})
            raise RuntimeError(e)
    @staticmethod
    def text_analyze(
        text: str,
        acc_name: any = None,
        exclusion: any = None,
        pii_entities_to_be_redacted: any = None,
        nlp="basic",
        score_threshold: float = 0,
        return_anonymized_text=False, 
        dict_operators=None
    ):
        print(f"Entering text_analyze function with nlp='{nlp}' and text length={len(text)}")
                
        print(f"Selecting NLP engine for nlp='{nlp}'.")
        result = []
        (
            analyzer,
            imageAnalyzerEngine,
            imageRedactorEngine,
            imagePiiVerifyEngine,
            encryptImageEngin,
        ) = select_nlp(nlp)
        print(f"Selected analyzer: {analyzer.__class__.__name__}")

        sp_recog = None

        if nlp == "roberta":
            print("Roberta NLP selected. Adding roberta_recog.")
            sp_recog = [roberta_recog]          
        if nlp == "ranha":
            print("Ranha NLP selected.")
            if pii_entities_to_be_redacted == None and acc_name == None:
                print("pii_entities_to_be_redacted and acc_name are None. Building list from supported entities.")
                pii_entities_to_be_redacted = list(
                    set(
                        ranha_recog.supported_entities
                        + registry.get_supported_entities()
                    )
                )
            sp_recog = [ranha_recog]
            
        try:
            if acc_name == None:
                print("acc_name is None. Proceeding with standard analyzer.analyze call.")
                if pii_entities_to_be_redacted == None:
                    print("pii_entities_to_be_redacted is None. Analyzing with all supported entities.")
                    result = analyzer.analyze(
                        text=text,
                        language="en",
                        allow_list=exclusion,
                        return_decision_process=True,
                        score_threshold=score_threshold,
                        ad_hoc_recognizers=sp_recog,
                    )
                else:
                    print(f"pii_entities_to_be_redacted is not None. Analyzing for specific entities: {pii_entities_to_be_redacted}")
                    try:
                        if nlp == "roberta" and len(text) > 2000:
                            print("Large text with RoBERTa detected")
                            
                            if return_anonymized_text and dict_operators:
                                # 🎯 CHUNK-BY-CHUNK ANONYMIZATION
                                print("Using chunk-by-chunk processing with immediate anonymization")
                                return self.chunk_analyze_and_anonymize_unified(
                                    text=text,
                                    pii_entities_to_be_redacted=pii_entities_to_be_redacted,
                                    exclusion=exclusion,
                                    score_threshold=score_threshold,
                                    sp_recog=sp_recog,
                                    dict_operators=dict_operators
                                )
                            else:
                                # 🎯 CHUNK-BY-CHUNK ANALYSIS ONLY (for analyze() function)
                                print("Using chunking for analysis only - collecting all results")
                                chunks = chunk_text(text, chunk_size=500)
                                all_results = []
                                
                                for i, (chunk_text_part, chunk_start_pos) in enumerate(chunks):
                                    print(f"Analyzing chunk {i+1}/{len(chunks)} at position {chunk_start_pos}")
                                    
                                    try:
                                        partial_results = analyzer.analyze(
                                            text=chunk_text_part,
                                            language="en",
                                            entities=pii_entities_to_be_redacted,
                                            allow_list=exclusion,
                                            return_decision_process=True,
                                            score_threshold=score_threshold,
                                            ad_hoc_recognizers=sp_recog,
                                        )
                                        
                                        # Adjust positions back to original text
                                        for result_item in partial_results:
                                            result_item.start += chunk_start_pos
                                            result_item.end += chunk_start_pos
                                        
                                        all_results.extend(partial_results)
                                        print(f"Chunk {i+1} found {len(partial_results)} entities")
                                        
                                    except Exception as e:
                                        log.error(f"Chunk analysis error: {e}")
                                        continue
                                
                                result = all_results
                                print(f"Total entities found across all chunks: {len(result)}")
                        else:
                            # Small text or non-RoBERTa - process normally
                            print("Processing without chunking")
                            result = analyzer.analyze(
                                text=text,
                                language="en",
                                entities=pii_entities_to_be_redacted,
                                allow_list=exclusion,
                                return_decision_process=True,
                                score_threshold=score_threshold,
                                ad_hoc_recognizers=sp_recog,
                            )

                    except Exception as e:
                        log.error(f"text_analyze error: {e}")
                        log.error(LINE_NO_LABEL + str(e.__traceback__.tb_lineno))
                        return 482

            # In text_analyze method, complete the portfolio processing for chunking:
            else:
                print("Portfolio case - processing with acc_name")
                pre_entity = []
                data_list_Ent = []
                result=[]

                try:
                    response_value = ApiCall.request(acc_name)
                    
                    if response_value == None:
                        return None
                    if response_value == 404:
                        return response_value
                        
                    entity_type, data_list, pre_entity = response_value
                    
                    # Process custom recognizers
                    for d in range(len(data_list)):
                        record = ApiCall.getRecord(entity_type[d])
                        record = AttributeDict(record)
                        log.debug("Record=====" + str(record))

                        if record.RecogType == "Data":
                            data_recog = data_listRecognizer(
                                terms=data_list[d], entitie=[entity_type[d]]
                            )
                            registry.add_recognizer(data_recog)
                            update_session_dict(entity_type[d], data_list[d])
                            data = {entity_type[d]: data_list[d]}
                            data_list_Ent.append(data)

                        elif record.RecogType == "Pattern" and record.isPreDefined == "No":
                            context_obj = record.Context.split(",")
                            pattern = "|".join(data_list[d])

                            log.debug("pattern=" + str(pattern))
                            pattern_obj = Pattern(
                                name=entity_type[d], regex=pattern, score=record.Score
                            )
                            pattern_recog = PatternRecognizer(
                                supported_entity=entity_type[d],
                                patterns=[pattern_obj],
                                context=context_obj,
                            )
                            registry.add_recognizer(pattern_recog)

                    # 🎯 Handle chunking for portfolio
                    if nlp == "roberta" and len(text) > 2000:
                        if return_anonymized_text and dict_operators:
                            print("Portfolio: Using chunking with immediate anonymization")
                            
                            # 🔧 For portfolio chunking, we need to handle encryption properly
                            # Get encryption list and update dict_operators
                            encryption_list = admin_par[request_id_var.get()]["encryption_list"]
                            if encryption_list is not None and len(encryption_list) > 0:
                                for entity in encryption_list:
                                    dict_operators[entity] = OperatorConfig("hash", {"hash-type": "md5"})
                            
                            return self.chunk_analyze_and_anonymize_unified_portfolio(
                                text=text,
                                entity_type=entity_type,
                                pre_entity=pre_entity,
                                exclusion=exclusion,
                                sp_recog=sp_recog,
                                dict_operators=dict_operators,
                                acc_name=acc_name
                            )
                        else:
                            # Portfolio chunk-by-chunk analysis only
                            print("Portfolio: Using chunking for analysis only")
                            chunks = chunk_text(text, chunk_size=500)
                            all_results = []
                            
                            for i, (chunk_text_part, chunk_start_pos) in enumerate(chunks):
                                try:
                                    partial_results = analyzer.analyze(
                                        text=chunk_text_part,
                                        language="en",
                                        entities=entity_type + pre_entity,
                                        allow_list=exclusion,
                                        score_threshold=admin_par[request_id_var.get()]["scoreTreshold"],
                                        return_decision_process=True,
                                        ad_hoc_recognizers=sp_recog,
                                    )
                                    
                                    for result_item in partial_results:
                                        result_item.start += chunk_start_pos
                                        result_item.end += chunk_start_pos
                                    
                                    all_results.extend(partial_results)
                                    
                                except Exception as e:
                                    log.error(f"Portfolio chunk analysis error: {e}")
                                    continue
                            
                            result = all_results
                    else:
                        # Traditional portfolio processing
                        print("Portfolio: Processing without chunking")
                        results = analyzer.analyze(
                            text=text,
                            language="en",
                            entities=entity_type + pre_entity,
                            allow_list=exclusion,
                            score_threshold=admin_par[request_id_var.get()]["scoreTreshold"],
                            return_decision_process=True,
                            ad_hoc_recognizers=sp_recog,
                        )
                        result.extend(results)
                        
                except Exception as e:
                    log.error(f"Portfolio processing error: {e}")
                    return 482
                
            log.debug("result=" + str(result))
            print(f"Analyzer returned {len(result)} results.")
            return result
        except Exception as e:
            log.error(str(e))

            log.error(LINE_NO_LABEL + str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            error_dict[request_id_var.get()].append(
                {
                    "UUID": request_id_var.get(),
                    "function": "text_analyzeFunction",
                    "msg": str(e.__class__.__name__),
                    "description": str(e) + LINE_NO_LABEL + str(e.__traceback__.tb_lineno),
                }
            )
            raise RuntimeError(e)
    def chunk_analyze_and_anonymize_unified_portfolio(self, text, entity_type, pre_entity, exclusion, sp_recog, dict_operators, acc_name):
        """
        Portfolio-specific chunk-by-chunk processing with immediate anonymization
        """
        print(f"Starting portfolio chunk processing for {len(text)} characters")
        

        (analyzer, imageAnalyzerEngine, imageRedactorEngine, imagePiiVerifyEngine, encryptImageEngin) = select_nlp("roberta")

        chunks = chunk_text(text, chunk_size=500)
        anonymized_chunks = []
        
        for i, (chunk_text_part, chunk_start_pos) in enumerate(chunks):
            print(f"Processing portfolio chunk {i+1}/{len(chunks)} at position {chunk_start_pos}")
            
            try:
                partial_results = analyzer.analyze(
                    text=chunk_text_part,
                    language="en",
                    entities=entity_type + pre_entity,
                    allow_list=exclusion,
                    score_threshold=admin_par[request_id_var.get()]["scoreTreshold"],
                    return_decision_process=True,
                    ad_hoc_recognizers=sp_recog,
                )
                
                
                partial_results = self.resolve_overlapping_entities(partial_results)
                
            
                if partial_results:
                    anonymized_chunk = anonymizer.anonymize(
                        text=chunk_text_part,
                        operators=dict_operators,
                        analyzer_results=partial_results,
                    )
                    anonymized_chunks.append(anonymized_chunk.text)
                    print(f"Portfolio chunk {i+1} anonymized successfully")
                else:
                    anonymized_chunks.append(chunk_text_part)
                    print(f"Portfolio chunk {i+1} has no entities, keeping original")
                    
            except Exception as e:
                log.error(f"Error processing portfolio chunk {i+1}: {e}")
                anonymized_chunks.append(chunk_text_part)
        
        return " ".join(anonymized_chunks)


    def chunk_analyze_and_anonymize_unified(self, text, pii_entities_to_be_redacted, exclusion, score_threshold, sp_recog, dict_operators):
        """
        Unified chunk-by-chunk processing that handles both analysis and anonymization
        """
        print(f"Starting unified chunk-by-chunk processing for text of {len(text)} characters")
        
       
        (analyzer,imageAnalyzerEngine,imageRedactorEngine,imagePiiVerifyEngine,encryptImageEngin,) = select_nlp("roberta")
        
       
        chunks = chunk_text(text, chunk_size=500)
        anonymized_chunks = []
        
        for i, (chunk_text_part, chunk_start_pos) in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)} at position {chunk_start_pos}")
            
            try:
             
                partial_results = analyzer.analyze(
                    text=chunk_text_part,
                    language="en",
                    entities=pii_entities_to_be_redacted,
                    allow_list=exclusion,
                    return_decision_process=True,
                    score_threshold=score_threshold,
                    ad_hoc_recognizers=sp_recog,
                )
                
                print(f"Chunk {i+1} found {len(partial_results)} entities")
                
                # 2. Resolve overlapping entities within this chunk (positions are local to chunk)
                partial_results = self.resolve_overlapping_entities(partial_results)
                 # 3. Handle fake data for this chunk if needed
                chunk_dict_operators = dict_operators.copy()
                
                # 3. Anonymize this chunk immediately with local positions
                if partial_results:
                    anonymized_chunk = anonymizer.anonymize(
                        text=chunk_text_part,  # ← Use chunk text, not full text
                        operators=chunk_dict_operators,
                        analyzer_results=partial_results,  # ← Use local positions
                    )
                    anonymized_chunks.append(anonymized_chunk.text)
                    print(f"Chunk {i+1} anonymized successfully")
                else:
                    # No entities found, keep original chunk
                    anonymized_chunks.append(chunk_text_part)
                    print(f"Chunk {i+1} has no entities, keeping original")
                    
            except Exception as e:
                log.error(f"Error processing chunk {i+1}: {e}")
                # Fallback: keep original chunk
                anonymized_chunks.append(chunk_text_part)
        
        # 4. Combine all anonymized chunks
        final_anonymized_text = " ".join(anonymized_chunks)
        print(f"Successfully combined {len(anonymized_chunks)} chunks")
        
        return final_anonymized_text
    @staticmethod
    def anonymize(payload: PIIAnonymizeRequest):
        error_dict[request_id_var.get()] = []
        log.debug("Entering in anonymize function")
        try:
            pii_entities_to_be_redacted = payload.pii_entities_to_be_redacted
            
            if payload.exclusion_list == None:
                exclusion_list = []
            else:
                exclusion_list = payload.exclusion_list
                
            privacyobj = TextPrivacy()
                            
            # 🎯 UNIFIED APPROACH: Always use text_analyze with appropriate parameters
            text_length = len(payload.input_text)
            print(f"Text length: {text_length} characters")
            
            if text_length > 2000 and payload.nlp == "roberta":
                print("Using unified chunk-by-chunk processing")
                # Use unified chunk-by-chunk processing
                dict_operators = {}
                if payload.fakeData == True:
                    print("Fake data generation enabled - will handle in chunking method.")
                if payload.portfolio != None:
                    print("Portfolio detected - encryption will be handled inside text_analyze for chunking.")
                if "ORGANIZATION" not in dict_operators:
                    print("Adding default replacement for ORGANIZATION")
                    dict_operators["ORGANIZATION"] = OperatorConfig("replace", {"new_value": "<ORGANIZATION>"})
                if payload.portfolio == None:
                    print("dict_operators:", dict_operators)
                    anonymized_text = privacyobj.text_analyze(
                        text=payload.input_text,
                        exclusion=exclusion_list,
                        pii_entities_to_be_redacted=pii_entities_to_be_redacted,
                        nlp=payload.nlp,
                        score_threshold=payload.score_threshold,
                        return_anonymized_text=True, 
                        dict_operators=dict_operators  
                    )
                else:
                    print("dict_operators:", dict_operators)
                    anonymized_text = privacyobj.text_analyze(
                        text=payload.input_text,
                        acc_name=payload,
                        exclusion=exclusion_list,
                        nlp=payload.nlp,
                        return_anonymized_text=True,
                        dict_operators=dict_operators 
                    )
                
                obj_pii_anonymize_response = PIIAnonymizeResponse(anonymizedText=anonymized_text)
                return obj_pii_anonymize_response
                
            else:
                print("Using traditional processing for small text")
                # Traditional processing for small texts
                if payload.portfolio == None:
                    results = privacyobj.text_analyze(
                        text=payload.input_text,
                        exclusion=exclusion_list,
                        pii_entities_to_be_redacted=pii_entities_to_be_redacted,
                        nlp=payload.nlp,
                        score_threshold=payload.score_threshold
                    )
                else:
                    results = privacyobj.text_analyze(
                        text=payload.input_text,
                        acc_name=payload,
                        exclusion=exclusion_list,
                        nlp=payload.nlp
                    )

                if results == None or results == 404 or results == 482:
                    return results
                dict_operators = {}
            
                if payload.fakeData == True:
                    print("Fake data generation enabled.")
                    fake_dict_operator = FakeDataGenerate.fake_data_generation(
                        results, payload.input_text
                    )
                    dict_operators.update(fake_dict_operator)

                # 🎯 NOW get encryption_list AFTER text_analyze (like old code)
                encryption_list = []
                if payload.portfolio != None:
                    print("Retrieving encryption list for portfolio AFTER text_analyze.")
                    encryption_list = admin_par[request_id_var.get()]["encryption_list"]

                if encryption_list is not None and len(encryption_list) > 0:
                    for entity in encryption_list:
                        print(f"Adding hash operator for entity: {entity}")
                        dict_operators[entity] = OperatorConfig("hash", {"hash-type": "md5"})

                if "ORGANIZATION" not in dict_operators:
                    print("Adding default replacement for ORGANIZATION")
                    dict_operators["ORGANIZATION"] = OperatorConfig("replace", {"new_value": "<ORGANIZATION>"})
                    
                # Resolve overlapping entities
                results = TextPrivacy.resolve_overlapping_entities(results)
                
                anonymize_text = anonymizer.anonymize(
                    text=payload.input_text,
                    operators=dict_operators,
                    analyzer_results=results,
                )

                obj_pii_anonymize_response = PIIAnonymizeResponse(anonymizedText=anonymize_text.text)
                return obj_pii_anonymize_response
                
        except Exception as e:
            log.error(str(e))
            log.error(LINE_NO_LABEL + str(e.__traceback__.tb_lineno))
            error_dict[request_id_var.get()].append({
                "UUID": request_id_var.get(),
                "function": "textAnonimyzeFunction",
                "msg": str(e.__class__.__name__),
                "description": str(e) + LINE_NO_LABEL + str(e.__traceback__.tb_lineno),
            })
            
            # Create fallback response
            try:
                fallback_text = payload.input_text if hasattr(payload, 'input_text') else ""
                return PIIAnonymizeResponse(anonymizedText=fallback_text)
            except Exception:
                return PIIAnonymizeResponse(anonymizedText="")
    @staticmethod
    def resolve_overlapping_entities(results):
        """Remove or merge overlapping entities to prevent fragmented masking"""
        if not results:
            return results
            
        # Sort by start position
        sorted_results = sorted(results, key=lambda x: x.start)
        resolved_results = []
        
        for current in sorted_results:
            if not resolved_results:
                resolved_results.append(current)
                continue
                
            last = resolved_results[-1]
            
            # Check for overlap
            if current.start < last.end:
                # Overlapping entities - keep the one with higher score
                if current.score > last.score:
                    resolved_results[-1] = current
                # If same score, keep the longer entity
                elif current.score == last.score and (current.end - current.start) > (last.end - last.start):
                    resolved_results[-1] = current
                # Otherwise keep the existing one (do nothing)
            else:
                resolved_results.append(current)
                
        print(f"Resolved {len(results)} entities to {len(resolved_results)} entities")
        return resolved_results
    @staticmethod
    def encrypt(payload: PIIAnonymizeRequest):
        log.debug("Entering in encrypt function")
        
        try:
            
            if(payload.exclusion_list == None):
                exclusion_list=[]
            else:
                exclusion_list=payload.exclusion_list
            privacy_obj = TextPrivacy()
            if(payload.portfolio== None):
                results = privacy_obj.text_analyze(text=payload.input_text,exclusion=exclusion_list,nlp=payload.nlp,score_threshold=payload.score_threshold)
            else: 
                results = privacy_obj.text_analyze(text=payload.input_text,acc_name=payload,exclusion=exclusion_list,nlp=payload.nlp)
                
            if results == None:
                return None
            dict_operators = {} 
            
            data = "WmZq4t7w!z%C&F)J"
                
            for i in results:
                dict_operators.update({i.entity_type : OperatorConfig("encrypt", {"key": data})})
            
            anonymize_text = anonymizer.anonymize(text=payload.input_text,
                                                  operators=dict_operators,
                                                  analyzer_results=results)
            
            log.debug(f"anonymize_text: {anonymize_text}")
            log.debug("anonymize_text_item: %s", anonymize_text.items)
            
            obj_PIIEncryptResponse = PIIEncryptResponse
            obj_PIIEncryptResponse.text = anonymize_text.text
            obj_PIIEncryptResponse.items= anonymize_text.items
            log.debug("Returning from encrypt function")
            
            return obj_PIIEncryptResponse
        
        
        except Exception as e:
            log.error(str(e))
            log.error(LINE_NO_LABEL+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"textAnonimyzeFunction","msg":str(e.__class__.__name__),"description":str(e)+LINE_NO_LABEL+str(e.__traceback__.tb_lineno)})
            raise RuntimeError(e)
    @staticmethod
    def decryption(payload: PIIDecryptRequest):
        log.debug("Entering in decrypt function")
       
         
        try:
            anonymized_text = payload.text
            anonymized_entities = payload.items
            
            data = "WmZq4t7w!z%C&F)J"
            list_ent= []
            for item in anonymized_entities:
                list_ent.append(OperatorResult(start=item.start,
                                    end=item.end ,
                                    entity_type= item.entity_type,
                                    text= item.text,
                                    operator= item.operator,))
            anonymized_entities=list_ent    
            
            deanonymized_result = deanonymizer.deanonymize(text=anonymized_text,
                                            entities=anonymized_entities,
                                    operators={"DEFAULT": OperatorConfig("decrypt", {"key": data})},)
            
            obj_PIIDecryptResponse = PIIDecryptResponse
            obj_PIIDecryptResponse.decryptedText = deanonymized_result.text
            log.debug("Returning from anonymize function")

            return obj_PIIDecryptResponse
            
            
        except Exception as e:
            log.error(str(e))
            log.error(LINE_NO_LABEL+str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"textAnonimyzeFunction","msg":str(e.__class__.__name__),"description":str(e)+LINE_NO_LABEL+str(e.__traceback__.tb_lineno)})
            raise RuntimeError(e)
    
class Shield:
    def PrivacyShield(self,payload: PIIPrivacyShieldRequest) -> PIIPrivacyShieldResponse:
        log.debug("Entering in privacyShield function")
        log.debug(f"payload: {payload}")

        res = []
        tot_ent=[]
        enres=[]
       
        log.debug("response="+str(res))
        privacy_obj=TextPrivacy()
        if(payload.portfolio== None):
            response_value=ApiCall.request(payload)
            if(response_value==None):
                obj_response = PIIPrivacyShieldResponse()
                obj_response.privacyCheck = []
                return obj_response
            if(response_value==404):
                    return response_value
            entity_type,_,pre_entity=response_value
            results = privacy_obj.text_analyze(text=payload.input_text)
            record=[ele for ele in admin_par[request_id_var.get()]["records"] if ele["isPreDefined"]=="Yes"]
            
            for i in record:
                i=AttributeDict(i)
                tot_ent.append(i.RecogName)
        else:
            response_value=ApiCall.request(payload)
            if response_value is None:
                return None
            if(response_value==404):
                     
                    return response_value
            entity_type,_,pre_entity=response_value
            entity_type.extend(pre_entity)
            tot_ent=entity_type

            results = privacy_obj.text_analyze(text=payload.input_text,acc_name=payload)

        value=payload.input_text
        pii_entity_list = []
        results=sorted(results, key=lambda i: i.start)
        for result in results:
            log.debug(f"result: {result}")
            enres.append({"type":result.entity_type,"start":result.start,"end":result.end,"value":value[result.start:result.end]})
            log.debug(f"obj_pii_entity: {enres}")

        if(len(enres)==0):
            temp= "Passed"
        else:
            temp="Failed"

        objent = PrivacyShield(
             entitiesRecognised=enres,
             entitiesConfigured= tot_ent,
             result=temp
        )
        pii_entity_list.append(objent)
        log.debug(f"pii_entity_list: {pii_entity_list}")
        
        obj_pii_analyze_response = PIIPrivacyShieldResponse
        obj_pii_analyze_response.privacyCheck = pii_entity_list


        log.debug("obj_pii_analyze_response="+str(obj_pii_analyze_response.privacyCheck))
        log.debug("Returning from privacyShield function")
        return obj_pii_analyze_response
    
