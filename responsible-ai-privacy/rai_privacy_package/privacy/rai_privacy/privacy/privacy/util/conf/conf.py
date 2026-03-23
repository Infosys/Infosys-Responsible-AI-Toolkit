import json
import os
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer import Pattern, PatternRecognizer, AnalyzerEngine, RecognizerRegistry,predefined_recognizers
# 
class ConfModle:
    def getAnalyzerEngin(str):
        modle=json.loads(os.getenv(str))
        configuration = {
    "nlp_engine_name": "spacy",
    "models": [
        
            modle
            # print(recog_list)
]}
        provider = NlpEngineProvider(nlp_configuration=configuration)
        nlp_engine = provider.create_engine()
        registry = RecognizerRegistry()
        analyzer = AnalyzerEngine(registry=registry,nlp_engine=nlp_engine)
        return (analyzer,registry)