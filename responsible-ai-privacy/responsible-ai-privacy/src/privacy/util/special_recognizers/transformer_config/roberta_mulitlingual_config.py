# MIT license https://opensource.org/licenses/MIT
# Copyright 2024 Infosys Ltd
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

ROBERTA_MULTILINGUAL_CONFIGURATION = {
    "PRESIDIO_SUPPORTED_ENTITIES": [
        "LOCATION",
        "PERSON"
    ],
    "DEFAULT_MODEL_PATH": "..\models\multilingual-ner",
    "LABELS_TO_IGNORE": ["O","ORGANIZATION","ORG","I-ORG","B-ORG"],
    "DEFAULT_EXPLANATION": "Identified as {} by the obi/deid_roberta_i2b2 NER model",
    "SUB_WORD_AGGREGATION": "simple",
    "DATASET_TO_PRESIDIO_MAPPING": {
        "DOCTOR": "PERSON",
        "PATIENT": "PERSON",
        "MEDICALRECORD": "O",
        "IDNUM": "O",
        "ZIP": "O",
        "STREET": "LOCATION",
        "COUNTRY": "LOCATION",
        "LOCATION-OTHER": "LOCATION",
        "STATE": "LOCATION",
        "DEVICE": "O",
        "ORG": "O",
    },
    "MODEL_TO_PRESIDIO_MAPPING": {
        "I-LOC" : "LOCATION",
        "B-LOC" : "LOCATION",
        "I-PER" : "PERSON",
        "B-PER" : "PERSON",
        "LOC" : "LOCATION",
        "PER" : "PERSON"
    },
    "CHUNK_OVERLAP_SIZE": 40,
    "CHUNK_SIZE": 600,
    "ID_SCORE_MULTIPLIER": 0.4,
    "ID_ENTITY_NAME": "ID"
}