import logging
from typing import Optional, List, Tuple, Set
import spacy
from spacy.matcher import PhraseMatcher
from presidio_analyzer.predefined_recognizers.spacy_recognizer import SpacyRecognizer
# from presidio_analyzer.predefined_recognizers import SpacyRecognizer
from presidio_analyzer import RecognizerResult
import copy




from presidio_analyzer import (
    RecognizerResult,
    LocalRecognizer,
    AnalysisExplanation,
)

logger = logging.getLogger("presidio_analyzer")
# terms = ["1&1 Telecommunication SE","1010 data services LLC","AMA",
#          "A O Smith Corporations","ABBMST","Addidas India","CITI","Cisco Systems","ERICSSON","Gati Ltd","IBM",
#          "Infosys Ltd","Intel Corporation","Johnson","JTC Corporation","NSC Global","SUZUKI MOTOR CORPORATION",
#          "Synopsys Ltd","TIBCOO", "T-Mobile UK","Toyota Systems Corporation","TSB Bank","UBS Bank"
#         ,"United Health Corporation","Vodafone quickcom","Voltas","VOLVO CARS","WIPRO LIMITED",
#          "Walmart", "CVS Health", "Walgreens Boots Alliance"]
terms=[]
class DataList:
    # def __init__(self,val) -> None:
        # self.Entiity=val
    entity=[]
    def setData(values):
        terms.extend(values)
        # print(terms)
    def resetData():
        terms.clear()
    # def setEntity(val):
    #     DataList.Entity=val
    #     ClientListRecognizer(supported_entities=val)
    # def getE():
        # return self.Entiity
        

nlp = spacy.load("en_core_web_lg")
        




class ClientListRecognizer(SpacyRecognizer):     
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

    ENTITIES = DataList.entity

    DEFAULT_EXPLANATION = "Identified as {} by Spacy's Named Entity Recognition"

    CHECK_LABEL_GROUPS = [
        # ({"LOCATION"}, {"GPE", "LOC"}),
        # ({"PERSON", "PER"}, {"PERSON", "PER"}),
        # ({"DATE_TIME"}, {"DATE", "TIME"}),
        # ({"NRP"}, {"NORP"}),
        # ({"ORGANIZATION"}, {"ORG"}),
        # ()
    ]
        
    

    

    def __init__(
        self,
        supported_language: str = "en",
        supported_entities: Optional[List[str]] = None,
        ner_strength: float = 0.85,
        check_label_groups: Optional[Tuple[Set, Set]] = None,
        context: Optional[List[str]] = None,
    ):
        self.ner_strength = ner_strength
        self.check_label_groups = (
            check_label_groups if check_label_groups else self.CHECK_LABEL_GROUPS
        )
        supported_entities = supported_entities if supported_entities else self.ENTITIES
        # print("=========",supported_entities)
        super().__init__(
            supported_entities=supported_entities,
            supported_language=supported_language,
            context=context,
        )

    def load(self) -> None:  # noqa D102
        # no need to load anything as the analyze method already receives
        # preprocessed nlp artifacts
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
    
    def analyze(self, text, entities, nlp_artifacts=None):  # noqa D102
        
        # print("=========",self.supported_entities)
       
    #     matcher = PhraseMatcher(nlp.vocab)
       
    # # Only run nlp.make_doc to speed things up
    #     patterns = [nlp.make_doc(text) for text in terms]
    
    #     matcher.add("TerminologyList", patterns)
        # result = []
        
        matcher = PhraseMatcher(nlp.vocab)
        
        # Only run nlp.make_doc to speed things up
        patterns = [nlp.make_doc(text) for text in terms]
        
        matcher.add("TerminologyList", patterns)
        
        results = []
        # result =[]
       
        doc = nlp(text)
        doc1 = str(doc)
        
        matches = matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            
            if doc1.find(str(span)):
                doc1=doc1.replace(str(span.text),"<COMPANY_NAME>")
            etype=copy.deepcopy(DataList.entity)    
            spacy_result = RecognizerResult(
                    
                    entity_type=etype[0],
                    start=span.start_char,
                    end=span.end_char,
                    score=self.ner_strength,
                    # analysis_explanation=explanation,
                    recognition_metadata={
                        RecognizerResult.RECOGNIZER_NAME_KEY: self.name,
                        RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: self.id,
                    },
                )
            

            results.append(spacy_result)

       
      

        return results

    @staticmethod
    def __check_label(
        entity: str, label: str, check_label_groups: Tuple[Set, Set]
    ) -> bool:
        return any(
            [entity in egrp and label in lgrp for egrp, lgrp in check_label_groups]
        )
