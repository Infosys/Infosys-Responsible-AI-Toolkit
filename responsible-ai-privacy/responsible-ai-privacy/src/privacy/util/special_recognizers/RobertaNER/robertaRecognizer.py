from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider

# Create configuration containing engine name and models
conf_file = r'privacy/util/special_recognizers/RobertaNER/conf.yaml'

# Create NLP engine based on configuration
provider = NlpEngineProvider(conf_file=conf_file)
roberta_nlp_engine = provider.create_engine()

