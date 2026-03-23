'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import logging
from typing import Optional, List, Tuple, Set
import time

from presidio_analyzer import (
    RecognizerResult,
    EntityRecognizer,
    AnalysisExplanation,
)
from presidio_analyzer.nlp_engine import NlpArtifacts

from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForTokenClassification

tokenizer = AutoTokenizer.from_pretrained("C:/WORK/GIT/responsible-ai-privacy/responsible-ai-privacy/models/roberta")
model = AutoModelForTokenClassification.from_pretrained("C:/WORK/GIT/responsible-ai-privacy/responsible-ai-privacy/models/roberta")
classifier = pipeline("ner", model=model, tokenizer=tokenizer)
logger = logging.getLogger("presidio-analyzer")


class RobertaRecognizer(EntityRecognizer):
    """
    Wrapper for a flair model, if needed to be used within Presidio Analyzer.

    :example:
    >from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

    >flair_recognizer = FlairRecognizer()

    >registry = RecognizerRegistry()
    >registry.add_recognizer(flair_recognizer)

    >analyzer = AnalyzerEngine(registry=registry)

    >results = analyzer.analyze(
    >    "My name is Christopher and I live in Irbid.",
    >    language="en",
    >    return_decision_process=True,
    >)
    >for result in results:
    >    print(result)
    >    print(result.analysis_explanation)


    """

    ENTITIES = [
        "LOCATION",
        "PERSON",
        "ORGANIZATION",
        # "MISCELLANEOUS"   # - There are no direct correlation with Presidio entities.
    ]

    DEFAULT_EXPLANATION = "Identified as {} by Flair's Named Entity Recognition"

    CHECK_LABEL_GROUPS = [
        ({"LOCATION"}, {"LOC", "LOCATION"}),
        ({"PERSON"}, {"PER", "PERSON"}),
        ({"ORGANIZATION"}, {"ORG"}),
        # ({"MISCELLANEOUS"}, {"MISC"}), # Probably not PII
    ]

    # MODEL_LANGUAGES = {
    #     "en": "flair/ner-english-large",
    #     "es": "flair/ner-spanish-large",
    #     "de": "flair/ner-german-large",
    #     "nl": "flair/ner-dutch-large",
    # }

    PRESIDIO_EQUIVALENCES = {
        "I-PER": "PERSON",
        "I-LOC": "LOCATION",
        # "I-ORG": "ORGANIZATION",
        # 'MISC': 'MISCELLANEOUS'   # - Probably not PII
    }

    def __init__(
        self,
        supported_language: str = "en",
        supported_entities: Optional[List[str]] = None,
        check_label_groups: Optional[Tuple[Set, Set]] = None,
        model: any = None,
    ):
        self.check_label_groups = (
            check_label_groups if check_label_groups else self.CHECK_LABEL_GROUPS
        )

        supported_entities = supported_entities if supported_entities else self.ENTITIES
        self.model = (
            model
            # if model
            # else SequenceTagger.load(self.MODEL_LANGUAGES.get(supported_language))
        )

        super().__init__(
            supported_entities=supported_entities,
            supported_language=supported_language,
            name="Flair Analytics",
        )

    def load(self) -> None:
        """Load the model, not used. Model is loaded during initialization."""
        pass

    def get_supported_entities(self) -> List[str]:
        """
        Return supported entities by this model.

        :return: List of the supported entities.
        """
        return self.supported_entities

    # Class to use Flair with Presidio as an external recognizer.
    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts = None
    ) -> List[RecognizerResult]:
        """
        Analyze text using Text Analytics.

        :param text: The text for analysis.
        :param entities: Not working properly for this recognizer.
        :param nlp_artifacts: Not used by this recognizer.
        :param language: Text language. Supported languages in MODEL_LANGUAGES
        :return: The list of Presidio RecognizerResult constructed from the recognized
            Flair detections.
        """
        print("------------------------roberta==")
        t=time.time()
        results = []

        res=classifier(text)
        print("timefor rbrt",time.time()-t)
        merged_entities = []
        current_entity = None

        for entity in res:
            if current_entity and entity['start'] <= current_entity['end']:
                # Overlapping entity, update existing entity
                current_entity['end'] = max(current_entity['end'], entity['end'])
                current_entity['word'] += entity['word']
            else:
                # New entity, start a new one
                current_entity = entity
                merged_entities.append(current_entity)

        # Handle partial entities at the end
        if current_entity and len(current_entity['word']) < 2:
            merged_entities.pop()
        # print("=======",merged_entities)
        # If there are no specific list of entities, we will look for all of it.
        if not entities:
            entities = self.supported_entities

        for entity in entities:
            if entity not in self.supported_entities:
                continue

            for ent in merged_entities:
                    # flair_results = RecognizerResult(
                    #              entity_type=ent['entity'],
                    #              start=ent['start'],
                    #              end=ent['end'],
                    #              score=ent["score"],
                    #              analysis_explanation=None,
                    #          )
                # print("---------")
                # print(entity, ent.labels[0].value, self.check_label_groups)
                entity_type = self.PRESIDIO_EQUIVALENCES.get(ent['entity'], ent['entity'])
                roberta_score = round(float(ent["score"]), 2)
                if(entity_type not in entities):
                    continue
                textual_explanation = self.DEFAULT_EXPLANATION.format(
                    entity_type
                )
         
                explanation = self.build_flair_explanation(
                    roberta_score, textual_explanation
                )
                # print(ent)
                flair_result = RecognizerResult(
                                 entity_type=entity_type,
                                 start=ent['start'],
                                 end=ent['end'],
                                 score=roberta_score,
                                 analysis_explanation=explanation,
                             )

                results.append(flair_result)
                # results.append(flair_result)
        # print(results)
        print("time====",time.time()-t)
        return results

    def _convert_to_recognizer_result(self, entity, explanation) -> RecognizerResult:

        entity_type = self.PRESIDIO_EQUIVALENCES.get(entity.tag, entity.tag)
        flair_score = round(entity.score, 2)

        flair_results = RecognizerResult(
            entity_type=entity_type,
            start=entity.start_position,
            end=entity.end_position,
            score=flair_score,
            analysis_explanation=explanation,
        )

        return flair_results

    def build_flair_explanation(
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

    @staticmethod
    def __check_label(
        entity: str, label: str, check_label_groups: Tuple[Set, Set]
    ) -> bool:
        return any(
            [entity in egrp and label in lgrp for egrp, lgrp in check_label_groups]
        )