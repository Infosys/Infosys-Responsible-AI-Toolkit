from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
configuration = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": {"spacy":"en_core_web_lg","tarf":"en_core_web_trf"}}],
               
}

provider = NlpEngineProvider(nlp_configuration=configuration)
spc_nlp_engine = provider.create_engine()