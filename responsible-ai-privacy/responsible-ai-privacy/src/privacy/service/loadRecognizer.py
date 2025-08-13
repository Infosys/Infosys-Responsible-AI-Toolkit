# MIT license https://opensource.org/licenses/MIT
# Copyright 2024 Infosys Ltd
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import json
from privacy.config.logger import request_id_var
from privacy.service.__init__ import *
from privacy.config.logger import CustomLogger
from privacy.util.special_recognizers.DataListRecognizer import DataListRecognizer

log = CustomLogger()

class LoadRecognizer:


    def set_recognizer(payload):
        error_dict[request_id_var.get()]=[]
        log.debug("Entering in analyze function")
        # gc.collect()
        log.debug(f"payload: {payload}")
        try:
            payload=AttributeDict(payload)
            contents =payload.file.file.read()
          
            json_data_bytes = bytes(contents)
            json_data_decoded = json_data_bytes.decode("utf-8")
            
            json_data = json.loads (json_data_decoded)

            
            for d in range(len(json_data)):
                        # record=ApiCall.getRecord(entityType[d])
                        # record=AttributeDict(record)
                        json_data[d] = AttributeDict(json_data[d])
                         
                        
                        if(json_data[d]['RecogType']=="Data"):
                                
                                dataRecog=(DataListRecognizer(terms=json_data[d].EntityValue,entitie=[json_data[d].RecogName]))
                                 
                                registry.add_recognizer(dataRecog)
                                # log.debug("++++++"+str(entityType[d]))
                                # results = engine.analyze(image,entities=[entityType[d]])
                                # result.extend(results)
                        elif(json_data[d].RecogType=="Pattern" and json_data[d].isPreDefined=="No"):
                            contextObj=json_data[d].Context.split(',')
                            pattern="|".join(json_data[d].EntityValue)
                            # log.debug("pattern="+str(pattern))
                            
                            patternObj = Pattern(name=json_data[d].RecogName,
                                                        regex=pattern,
                                                        score=json_data[d].Score)
                            patternRecog = PatternRecognizer(supported_entity=json_data[d].RecogName,
                                                                    patterns=[patternObj],context=contextObj)
                             
                            registry.add_recognizer(patternRecog)
                            
                  
 
            return {"Available Recognizers":registry.get_supported_entities()+[str(i)+"*" for i in set(ranha_recog.get_supported_entities())-set(registry.get_supported_entities())],"*": "select NLP:ranha use the above entities"}
        except Exception as e:
                log.error(str(e))
                log.error("Line No:"+str(e.__traceback__.tb_lineno))
                log.error(str(e.__traceback__.tb_frame))
                error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"set_recognizer","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
                # ExceptionDb.create({"UUID":request_id_var.get(),"function":"textAnalyzeMainFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
                raise Exception(e)
    
    
    def load_recognizer():
        
        try:
 
            return {"Available Recognizers":registry.get_supported_entities()+[str(i)+"*" for i in set(ranha_recog.get_supported_entities())-set(registry.get_supported_entities())],"*": "select NLP:ranha use the above entities"}
        except Exception as e:
                log.error(str(e))
                log.error("Line No:"+str(e.__traceback__.tb_lineno))
                log.error(str(e.__traceback__.tb_frame))
                error_dict[request_id_var.get()].append({"UUID":request_id_var.get(),"function":"load_recognizer","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
                # ExceptionDb.create({"UUID":request_id_var.get(),"function":"textAnalyzeMainFunction","msg":str(e.__class__.__name__),"description":str(e)+"Line No:"+str(e.__traceback__.tb_lineno)})
                raise Exception(e)