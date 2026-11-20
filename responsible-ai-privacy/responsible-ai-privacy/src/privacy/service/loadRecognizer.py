'''
License textMIT Licensehttps://mit-license.org/Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

import os
import json
from privacy.config.logger import request_id_var
from privacy.service.__init__ import AttributeDict, registry, ranha_recog,error_dict,admin_par
from presidio_analyzer import Pattern, PatternRecognizer
from privacy.config.logger import CustomLogger
from presidio_analyzer import RecognizerRegistry
from privacy.util.special_recognizers.DataListRecognizer import DataListRecognizer
LINE_NO_LABEL = "Line No:"

log = CustomLogger()
LOCATION_EXCLUSIONS = [
    "POSTAL CODE","Postal Code","postal code",  "zip code", "ZIP CODE","postalcode","code","zip code code","cypress"
]
class LocationRecognizerWithExclusion:
    def __init__(self, base_recognizer, exclusions=LOCATION_EXCLUSIONS):
        self.base = base_recognizer
        self.exclusions = set(e.lower() for e in exclusions)

    def analyze(self, text, *args, **kwargs):
        results = self.base.analyze(text, *args, **kwargs)
        filtered_results = []
        for r in results:
            entity_text = text[r.start:r.end].lower()
            if entity_text in self.exclusions:
                continue
            filtered_results.append(r)
        return filtered_results

    def __getattr__(self, name):
        
        return getattr(self.base, name)



class LoadRecognizer:

    @staticmethod
    def set_recognizer(payload):
        error_dict[request_id_var.get()]=[]
        log.debug("Entering in analyze function")
        log.debug(f"payload: {payload}")
        try:
            payload=AttributeDict(payload)

            if 'file' in payload and hasattr(payload.file, 'file') and hasattr(payload.file.file, 'read'):
                contents = payload.file.file.read()
            else:
                contents = payload.get('contents_bytes', b'')
          
            json_data_bytes = bytes(contents)
            json_data_decoded = json_data_bytes.decode("utf-8")
            
            json_data = json.loads (json_data_decoded)

            
            for d in range(len(json_data)):
                        json_data[d] = AttributeDict(json_data[d])
                         
                        
                        if(json_data[d]['RecogType']=="Data"):
                                
                                data_recog=(DataListRecognizer(terms=json_data[d].EntityValue, entitie=[json_data[d].RecogName],context=json_data[d].get('Context', []),base_score=json_data[d]['Score']))

                                registry.add_recognizer(data_recog)
                              
                        elif(json_data[d].RecogType=="Pattern" and json_data[d].isPreDefined=="No"):
                            context_obj=json_data[d].Context
                            pattern="|".join(json_data[d].EntityValue)
                          
                            
                            pattern_obj = Pattern(name=json_data[d].RecogName,
                                                        regex=pattern,
                                                        score=json_data[d].Score)
                            pattern_recog = PatternRecognizer(supported_entity=json_data[d].RecogName,
                                                                patterns=[pattern_obj], context=context_obj)

                            registry.add_recognizer(pattern_recog)


           
            registry.recognizers = [r for r in registry.recognizers if "DATE_TIME" not in r.supported_entities]
            
            for idx, recog in enumerate(registry.recognizers):
                if "LOCATION" in recog.supported_entities:
                    registry.recognizers[idx] = LocationRecognizerWithExclusion(recog)
                    log.debug("Wrapped LOCATION recognizer to exclude postal code phrases")
                    break
            return {"Available Recognizers":registry.get_supported_entities()+[str(i)+"*" for i in set(ranha_recog.get_supported_entities())-set(registry.get_supported_entities())],"*": "select NLP:ranha use the above entities"}
        except Exception as e:
                log.error(str(e))
                log.error(LINE_NO_LABEL+str(e.__traceback__.tb_lineno))
                log.error(str(e.__traceback__.tb_frame))
                error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"set_recognizer","msg":str(e.__class__.__name__),"description":str(e)+LINE_NO_LABEL+str(e.__traceback__.tb_lineno)})
                raise RuntimeError(e)
    
    @staticmethod
    def load_recognizer():
        
        try:
 
            return {"Available Recognizers":registry.get_supported_entities()+[str(i)+"*" for i in set(ranha_recog.get_supported_entities())-set(registry.get_supported_entities())],"*": "select NLP:ranha use the above entities"}
        except Exception as e:
                log.error(str(e))
                log.error(LINE_NO_LABEL+str(e.__traceback__.tb_lineno))
                log.error(str(e.__traceback__.tb_frame))
                error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"load_recognizer","msg":str(e.__class__.__name__),"description":str(e)+LINE_NO_LABEL+str(e.__traceback__.tb_lineno)})
                raise RuntimeError(e)
        
    @staticmethod
    def load_recognizers_from_json(json_file_path: str, registry: RecognizerRegistry) -> None:
        """Loads recognizers from a JSON file and adds them to the Presidio registry.

        Args:
            json_file_path: Path to the JSON file.
            registry: The Presidio RecognizerRegistry to add the recognizers to.
        """
        if not os.path.exists(json_file_path):
            log.error(f"Recognizer JSON file not found: {json_file_path}")
            raise FileNotFoundError(f"Recognizer JSON file not found: {json_file_path}")

        try:
            with open(json_file_path, 'r') as f:
                recognizer_data = json.load(f)

            for recognizer_def in recognizer_data:
                recog_type = recognizer_def.get('RecogType')
                recog_name = recognizer_def.get('RecogName')

                if recog_type == "Data":
                    try:
                        terms = [str(term).lower() for term in recognizer_def['EntityValue']]
                        data_recognizer = DataListRecognizer(
                            terms=terms,
                            entitie=[recog_name],
                            score=recognizer_def.get('Score', 0.6)
                        )
                        registry.add_recognizer(data_recognizer)
                    except Exception as e:
                        log.error(f"Error loading Data Recognizer {recog_name}: {e}")
                        raise RuntimeError(e)

                elif recog_type == "Pattern" and recognizer_def.get('isPreDefined') == "No":
                    try:
                        context_obj = recognizer_def['Context'].split(',') if recognizer_def.get('Context') else []
                        pattern_str = "|".join(recognizer_def['EntityValue'])
                        pattern_obj = Pattern(
                            name=recog_name,
                            regex=pattern_str,
                            score=recognizer_def.get('Score', 0.6)
                        )
                        pattern_recognizer = PatternRecognizer(
                            supported_entity=recog_name,
                            patterns=[pattern_obj],
                            context=context_obj
                        )
                        registry.add_recognizer(pattern_recognizer)
                    except Exception as e:
                        log.error(f"Error loading Pattern Recognizer {recog_name}: {e}")
                        raise RuntimeError(e)

                else:
                    log.warning(f"Skipping unsupported recognizer type: {recog_type} for {recog_name}")

            log.info("All custom recognizers loaded successfully.")
            registry.recognizers = [r for r in registry.recognizers if "DATE_TIME" not in r.supported_entities]
            for idx, recog in enumerate(registry.recognizers):
                if "LOCATION" in recog.supported_entities:
                    registry.recognizers[idx] = LocationRecognizerWithExclusion(recog)
                    log.debug("Wrapped LOCATION recognizer to exclude postal code phrases")
                    break


        except (json.JSONDecodeError, FileNotFoundError) as e:
            log.error(f"Error loading recognizers from JSON: {e}")
            raise RuntimeError(e)