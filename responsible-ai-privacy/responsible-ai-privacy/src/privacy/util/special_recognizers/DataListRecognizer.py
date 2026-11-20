'''
License textMIT Licensehttps://mit-license.org/Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

import logging
from typing import Optional, List, Tuple, Set
import spacy
from spacy.matcher import PhraseMatcher
from presidio_analyzer.predefined_recognizers.spacy_recognizer import SpacyRecognizer

from presidio_analyzer import RecognizerResult
import copy




from presidio_analyzer import (
    RecognizerResult,
    LocalRecognizer,
    AnalysisExplanation,
)

logger = logging.getLogger("presidio_analyzer")

nlp = spacy.load("en_core_web_lg")
        




class DataListRecognizer(SpacyRecognizer):     
    """
    Recognize PII entities using a spaCy NLP model.

    Since the spaCy pipeline is ran by the AnalyzerEngine,
    this recognizer only extracts the entities from the NlpArtifacts
    and replaces their types to align with Presidio's.

    :param supported_language: Language this recognizer supports
    :param supported_entities: The entities this recognizer can detect
    :param ner_strength: Default confidence for NER prediction
    :param check_label_groups: Tuple containing Presidio entity names
    and spaCy entity names, for verifying that the right entity
    is translated into a Presidio entity.
    """



    DEFAULT_EXPLANATION = "Identified as {} by Spacy's Named Entity Recognition"

    CHECK_LABEL_GROUPS = [
    ]
        
    

    

    def __init__(
        self,
        terms,entitie,
        supported_language: str = "en",
        supported_entities: Optional[List[str]] = None,
        ner_strength: float = 0.6,
        check_label_groups: Optional[Tuple[Set, Set]] = None,
        context: Optional[List[str]] = None,
        base_score:float=0.6,  
        
    ):
        self.terms=terms
        self.ENTITIES=entitie
        self.ner_strength = base_score
        self.check_label_groups = (
            check_label_groups if check_label_groups else self.CHECK_LABEL_GROUPS
        )
        supported_entities = supported_entities if supported_entities else self.ENTITIES

        super().__init__(
            supported_entities=supported_entities,
            supported_language=supported_language,
            ner_strength=base_score,
            context=context,
        )
        self.ner_strength = base_score
        print(f"DataListRecognizer ner_strength set to: {self.ner_strength}")

    def load(self) -> None:  
        pass
    
    
    def build_spacy_explanation(
        self, original_score: float, explanation: str
    ) -> AnalysisExplanation:
        """
        Create explanation for why this result was detected.

        :param original_score: Score given by this recognizer
        :param explanation: Explanation string
        :return:
        """
        explanation = AnalysisExplanation(
            recognizer=self.__class__.__name__,
            original_score=original_score,
            textual_explanation=explanation,
        )
        return explanation
    
    def analyze(self, text, entities, nlp_artifacts=None):  
        
     
        
        matcher = PhraseMatcher(nlp.vocab)
        
      
        patterns = [nlp.make_doc(text) for text in self.terms]
        
        matcher.add("TerminologyList", patterns)
        
        results = []
     
       
        doc = nlp(text)
        doc1 = str(doc)
        
        matches = matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            
            if doc1.find(str(span)):
                doc1=doc1.replace(str(span.text),"<COMPANY_NAME>")
         
            etype=self.ENTITIES 
            spacy_result = RecognizerResult(
                    
                    entity_type=etype[0],
                    start=span.start_char,
                    end=span.end_char,
                    score=self.ner_strength,
              
                    recognition_metadata={
                        RecognizerResult.RECOGNIZER_NAME_KEY: self.name,
                        RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: self.id,
                    },
                )
            

            results.append(spacy_result)

       
      

        return results

  
