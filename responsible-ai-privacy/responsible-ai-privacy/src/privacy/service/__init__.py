import contextvars
from presidio_analyzer import Pattern, PatternRecognizer, AnalyzerEngine, RecognizerRegistry,predefined_recognizers
from presidio_anonymizer import AnonymizerEngine, DeanonymizeEngine
from presidio_anonymizer.entities import (RecognizerResult,
    OperatorResult,
    OperatorConfig,ConflictResolutionStrategy)
from privacy.config.logger import CustomLogger
from presidio_image_redactor import ImageRedactorEngine,ImageAnalyzerEngine,ImagePiiVerifyEngine       
from presidio_image_redactor import DicomImageRedactorEngine
# from privacy.util.special_recognizers.roberta import RobertaRecognizer
from privacy.util.encrypt import EncryptImage
from privacy.config.logger import CustomLogger
log = CustomLogger()




from presidio_analyzer.nlp_engine import SpacyNlpEngine
# from privacy.util.special_recognizers.spcy import spc_nlp_engine
import spacy

# from privacy.util.special_recognizers.RobertaNER.robertaRecognizer import roberta_nlp_engine


from privacy.util.special_recognizers.TransformerRecognizer import TransformersRecognizer


print("===========init==========")
error_dict={}
admin_par={}
session_dict = contextvars.ContextVar('session_dict', default={})

# Example usage:
def update_session_dict(key, value):
    session_dict.get()[key] = value

def get_session_dict():
    return session_dict.get()

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    
registry = RecognizerRegistry()
# log.info("============2a")
# analyzer = AnalyzerEngine(registry=registry)
# log.debug("============2b")
# from privacy.util.special_recognizers.RobertaNER.robertaRec import RobertaRecognizer
anonymizer = AnonymizerEngine()
# Create NLP engine based on configuration
# flair_recognizer = (
#     RobertaRecognizer()
# ) 
# # registry.add_recognizer(flair_recognizer)
# provider = NlpEngineProvider(nlp_configuration=configuration)
# analyzer = AnalyzerEngine(registry=registry,nlp_engine=roberta_nlp_engine)
# analyzer = AnalyzerEngine(registry=registry,nlp_engine=loaded_nlp_engine)
# engine_provider = MyCustomNlpEngineProvider()

# analyzer = AnalyzerEngine(registry=registry,nlp_engine=loaded_nlp_engine)

"""Deafult NLP , Less Accuracy less latency"""
analyzer_l = AnalyzerEngine(registry=registry)
imageAnalyzerEngine_l = ImageAnalyzerEngine(analyzer_engine=analyzer_l)
imageRedactorEngine_l = ImageRedactorEngine(image_analyzer_engine=imageAnalyzerEngine_l)
imagePiiVerifyEngine_l = ImagePiiVerifyEngine(image_analyzer_engine=imageAnalyzerEngine_l) 
encryptImageEngin_l=EncryptImage(image_analyzer_engine=imageAnalyzerEngine_l)


"""En_core_web_trf NLP , slightly better Accuracy little High latency"""
class LoadedSpacyNlpEngine(SpacyNlpEngine):
    def __init__(self, loaded_spacy_model):
        super().__init__()
        self.nlp = {"en": loaded_spacy_model}

trf_nlp = spacy.load("en_core_web_trf")

# Pass the loaded model to the new LoadedSpacyNlpEngine
trf_engine = LoadedSpacyNlpEngine(loaded_spacy_model = trf_nlp)
# if not trf_engine.is_loaded():
#             print("----------------------------------------------")
#             trf_engine.load()
analyzer_m = AnalyzerEngine(registry=registry,nlp_engine=trf_engine)
imageAnalyzerEngine_m = ImageAnalyzerEngine(analyzer_engine=analyzer_m)
imageRedactorEngine_m = ImageRedactorEngine(image_analyzer_engine=imageAnalyzerEngine_m)
imagePiiVerifyEngine_m = ImagePiiVerifyEngine(image_analyzer_engine=imageAnalyzerEngine_m) 
encryptImageEngin_m=EncryptImage(image_analyzer_engine=imageAnalyzerEngine_m)


# """Roberta NLP , better Accuracy High latency"""
# analyzer_h = AnalyzerEngine(registry=registry,nlp_engine=roberta_nlp_engine)
# imageAnalyzerEngine_h = ImageAnalyzerEngine(analyzer_engine=analyzer_h)
# imageRedactorEngine_h = ImageRedactorEngine(image_analyzer_engine=imageAnalyzerEngine_h)
# imagePiiVerifyEngine_h = ImagePiiVerifyEngine(image_analyzer_engine=imageAnalyzerEngine_h) 
# encryptImageEngin_h=EncryptImage(image_analyzer_engine=imageAnalyzerEngine_h)




"""Roberta Transformer"""
from privacy.util.special_recognizers.transformer_config.roberta_config import ROBERTA_CONFIGURATION
roberta_path = r"../models/roberta"
supported_entities_1 = ROBERTA_CONFIGURATION.get("PRESIDIO_SUPPORTED_ENTITIES")
roberta_recog = TransformersRecognizer(model_path=roberta_path,
                                                     supported_entities=supported_entities_1)

## This would download a large (~500Mb) model on the first run
roberta_recog.load_transformer(**ROBERTA_CONFIGURATION)


"""PIIRanha Transformer"""
from privacy.util.special_recognizers.transformer_config.ranha_config import RANHA_DEID_CONFIGURATION
ranha_path = r"../models/PIIRanha"
supported_entities_2 = RANHA_DEID_CONFIGURATION.get("PRESIDIO_SUPPORTED_ENTITIES")
ranha_recog= TransformersRecognizer(model_path=ranha_path,  
                                                        supported_entities=supported_entities_2)
ranha_recog.load_transformer(**RANHA_DEID_CONFIGURATION)



""" Loading Roberta-Ner-Multilingual into transformer """
from privacy.util.special_recognizers.transformer_config.roberta_mulitlingual_config import ROBERTA_MULTILINGUAL_CONFIGURATION
multilingual_model_path = r'../models/multilingual-ner'
supported_entities_3 = ROBERTA_MULTILINGUAL_CONFIGURATION.get("PRESIDIO_SUPPORTED_ENTITIES")
roberta_multilingual_recog = TransformersRecognizer(model_path=multilingual_model_path,supported_entities=supported_entities_3)
roberta_multilingual_recog.load_transformer(**ROBERTA_MULTILINGUAL_CONFIGURATION)


deanonymizer = DeanonymizeEngine()
DicomEngine = DicomImageRedactorEngine()
registry.load_predefined_recognizers()
# print("========B===========",registry.get_supported_entities())
registry.add_recognizer(roberta_multilingual_recog)




# print("=========A==========",registry.get_supported_entities())
# print("===================",registry.get_recognizers(language='en'))
# print("===================",registry.get_recognizers(language='en',all_fields=True))
def selectNlp(nlpName):     
    if nlpName == "basic":
        print("basic")
        return analyzer_l,imageAnalyzerEngine_l,imageRedactorEngine_l,imagePiiVerifyEngine_l,encryptImageEngin_l
    elif nlpName == "good":
        print("good")
        return analyzer_m,imageAnalyzerEngine_m,imageRedactorEngine_m,imagePiiVerifyEngine_m,encryptImageEngin_m
    else:
        return analyzer_l,imageAnalyzerEngine_l,imageRedactorEngine_l,imagePiiVerifyEngine_l,encryptImageEngin_l

    
