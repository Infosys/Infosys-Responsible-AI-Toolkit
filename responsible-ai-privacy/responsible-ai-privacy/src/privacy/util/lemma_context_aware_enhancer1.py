import copy
import logging
from typing import List, Optional
import re
from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts
from privacy.util.context_aware_enhancer1 import ContextAwareEnhancer
from presidio_analyzer import AnalysisExplanation
logger = logging.getLogger("presidio-analyzer")


def is_data_near_word(text, supportive_context_word, result):
            """
            Checks if the given data is near the specified word in the sentence.
        
            Args:
                sentence: The input sentence.
                word: The word to search for.
                data: The data to check for proximity.
        
            Returns:
                True if the data is near the word, False otherwise.
            """
            text_lower = text.lower()
            supportive_context_word_lower = supportive_context_word.lower()
            data_start = result.start

            context_word_positions = [m.start() for m in re.finditer(re.escape(supportive_context_word_lower), text_lower)]
            
            if not context_word_positions:
                return None 


            proximity_threshold = 55


            nearest_context_position = None
            min_distance = float('inf')
            
            

            for context_pos in context_word_positions:
                distance = abs((context_pos + len(supportive_context_word_lower) - 1) - data_start)
                if distance < min_distance:
                    min_distance = distance
                    nearest_context_position = context_pos

            if nearest_context_position is not None and min_distance <= proximity_threshold:
                return True
            else:
                return False

class EnhancedAnalysisExplanation(AnalysisExplanation):
    """Enhanced AnalysisExplanation with context support methods"""

    def __init__(self, recognizer, original_score, textual_explanation):
        super().__init__(recognizer, original_score, textual_explanation)
        self.supportive_context_word = None
        self.improved_score = None

    def set_supportive_context_word(self, supportive_context_word):
        """Set the supportive context word for this explanation"""
        self.supportive_context_word = supportive_context_word

    def set_improved_score(self, improved_score):
        """Set the improved score for this explanation"""
        self.improved_score = improved_score      

class LemmaContextAwareEnhancer(ContextAwareEnhancer):
    """
    A class representing a lemma based context aware enhancer logic.

    Context words might enhance confidence score of a recognized entity,
    LemmaContextAwareEnhancer is an implementation of Lemma based context aware logic,
    it compares spacy lemmas of each word in context of the matched entity to given
    context and the recognizer context words,
    if matched it enhance the recognized entity confidence score by a given factor.

    :param context_similarity_factor: How much to enhance confidence of match entity
    :param min_score_with_context_similarity: Minimum confidence score
    :param context_prefix_count: how many words before the entity to match context
    :param context_suffix_count: how many words after the entity to match context
    """

    def __init__(
        self,
        context_similarity_factor: float = 0.35,
        min_score_with_context_similarity: float = 0.4,
        context_prefix_count: int = 5,
        context_suffix_count: int = 0,
    ):
        super().__init__(
            context_similarity_factor=context_similarity_factor,
            min_score_with_context_similarity=min_score_with_context_similarity,
            context_prefix_count=context_prefix_count,
            context_suffix_count=context_suffix_count,
        )

    def enhance_using_context(
        self,
        text: str,
        raw_results: List[RecognizerResult],
        nlp_artifacts: NlpArtifacts,
        recognizers: List[EntityRecognizer],
        context: Optional[List[str]] = None,
    ) -> List[RecognizerResult]:
        """
        Update results in case the lemmas of surrounding words or input context
        words are identical to the context words.

        Using the surrounding words of the actual word matches, look
        for specific strings that if found contribute to the score
        of the result, improving the confidence that the match is
        indeed of that PII entity type

        :param text: The actual text that was analyzed
        :param raw_results: Recognizer results which didn't take
                            context into consideration
        :param nlp_artifacts: The nlp artifacts contains elements
                              such as lemmatized tokens for better
                              accuracy of the context enhancement process
        :param recognizers: the list of recognizers
        :param context: list of context words
        """  
        
        results = copy.deepcopy(raw_results)

     
        recognizers_dict = {recognizer.id: recognizer for recognizer in recognizers}

        context = [word.lower() for word in context] if context else []

    
        if nlp_artifacts is None:
            logger.warning("NLP artifacts were not provided")
            return results

        for result in results:
            recognizer = None
            if (
                result.recognition_metadata
                and RecognizerResult.RECOGNIZER_IDENTIFIER_KEY
                in result.recognition_metadata.keys()
            ):
                recognizer = recognizers_dict.get(
                    result.recognition_metadata[
                        RecognizerResult.RECOGNIZER_IDENTIFIER_KEY
                    ]
                )

            if not recognizer:
                logger.debug(
                    "Recognizer name not found as part of the "
                    "recognition_metadata dict in the RecognizerResult. "
                )
                continue

           
            if not recognizer.context:
                logger.debug(
                    "recognizer '%s' does not support context enhancement",
                    recognizer.name,
                )
                continue

            if result.recognition_metadata.get(
                RecognizerResult.IS_SCORE_ENHANCED_BY_CONTEXT_KEY
            ):
                logger.debug("result score already boosted, skipping")
                continue



            surrounding_words=[]
      

            for context_word in recognizer.context:
                if context_word.lower().strip() in text.lower():
                    surrounding_words.append(context_word.lower())
            
            surrounding_words.extend(context)            
            surrounding_words=list(set(surrounding_words))
            supportive_context_word = self._find_supportive_word_in_context(
                surrounding_words, recognizer.context,text=text, result1=result
            )
            text=text.lower()
            if supportive_context_word and supportive_context_word in text:
                print(f"Found supportive context word: {supportive_context_word}")
                print(f"Original score: {result.score}")
                result.score += self.context_similarity_factor
                result.score = max(result.score, self.min_score_with_context_similarity)
                result.score = min(result.score, ContextAwareEnhancer.MAX_SCORE)
                print(f"Enhanced score: {result.score}")

                # Fix the analysis_explanation issue
                if result.analysis_explanation is None:
                    result.analysis_explanation = EnhancedAnalysisExplanation(
                        recognizer=recognizer.__class__.__name__,
                        original_score=result.score - self.context_similarity_factor,
                        textual_explanation=f"Found context word: {supportive_context_word}"
                    )

                # Check if the method exists before calling
                if hasattr(result.analysis_explanation, 'set_supportive_context_word'):
                    result.analysis_explanation.set_supportive_context_word(supportive_context_word)
                else:
                    # Create enhanced explanation if method doesn't exist
                    result.analysis_explanation = EnhancedAnalysisExplanation(
                        recognizer=recognizer.__class__.__name__,
                        original_score=result.score - self.context_similarity_factor,
                        textual_explanation=f"Found context word: {supportive_context_word}"
                    )
                    result.analysis_explanation.set_supportive_context_word(supportive_context_word)

                if hasattr(result.analysis_explanation, 'set_improved_score'):
                    result.analysis_explanation.set_improved_score(result.score)
        return results
    @staticmethod
    def _find_supportive_word_in_context(
        context_list: List[str], recognizer_context_list: List[str] , text, result1
    ) -> str:
        """
        Find words in the text which are relevant for context evaluation.

        A word is considered a supportive context word if there's exact match
        between a keyword in context_text and any keyword in context_list.

        :param context_list words before and after the matched entity within
               a specified window size
        :param recognizer_context_list a list of words considered as
                context keywords manually specified by the recognizer's author
        """
        word = ""

        if context_list is None or recognizer_context_list is None:
            return word
        for predefined_context_word in recognizer_context_list:
            predefined_context_word=predefined_context_word.lower().strip()
            result = next(
                (
                    True
                    for keyword in context_list
                    if predefined_context_word in keyword
                ),
                False,
            )
            if result:
                result=is_data_near_word(text,predefined_context_word,result1)
            if result:
                logger.debug("Found context keyword '%s'", predefined_context_word)
                word = predefined_context_word
                break
        return word

    def _extract_surrounding_words(
        self, nlp_artifacts: NlpArtifacts, word: str, start: int
    ) -> List[str]:
        """Extract words surrounding another given word.

        The text from which the context is extracted is given in the nlp
        doc.

        :param nlp_artifacts: An abstraction layer which holds different
                              items which are the result of a NLP pipeline
                              execution on a given text
        :param word: The word to look for context around
        :param start: The start index of the word in the original text
        """
        if not nlp_artifacts.tokens:
            logger.info("Skipping context extraction due to lack of NLP artifacts")
           
            return [""]


        lemmatized_keywords = nlp_artifacts.keywords
        token_index = self._find_index_of_match_token(
            word, start, nlp_artifacts.tokens, nlp_artifacts.tokens_indices
        )
       

        backward_context = self._add_n_words_backward(
            token_index,
            self.context_prefix_count,
            nlp_artifacts.lemmas,
            lemmatized_keywords,
        )
        forward_context = self._add_n_words_forward(
            token_index,
            self.context_suffix_count,
            nlp_artifacts.lemmas,
            lemmatized_keywords,
        )
        context_list = []
        context_list.extend(backward_context)
        context_list.extend(forward_context)
        context_list = list(set(context_list))
        logger.debug("Context list is: %s", " ".join(context_list))
        return context_list

    @staticmethod
    def _find_index_of_match_token(
        word: str,
        start: int,
        tokens,
        tokens_indices: List[int],  # noqa ANN001
    ) -> int:
        found = False
      
        i = -1
        for i, token in enumerate(tokens, 0):
           
            if (tokens_indices[i] == start) or (start < tokens_indices[i] + len(token)):
              
                found = True
                break

        if not found:
            raise ValueError(
                "Did not find word '" + word + "' "
                "in the list of tokens although it "
                "is expected to be found"
            )
        return i

    @staticmethod
    def _add_n_words(
        index: int,
        n_words: int,
        lemmas: List[str],
        lemmatized_filtered_keywords: List[str],
        is_backward: bool,
    ) -> List[str]:
        """
        Prepare a string of context words.

        Return a list of words which surrounds a lemma at a given index.
        The words will be collected only if exist in the filtered array

        :param index: index of the lemma that its surrounding words we want
        :param n_words: number of words to take
        :param lemmas: array of lemmas
        :param lemmatized_filtered_keywords: the array of filtered
               lemmas from the original sentence,
        :param is_backward: if true take the preceeding words, if false,
                            take the successing words
        """
        i = index
        context_words = []
       
        remaining = n_words + 1
        while 0 <= i < len(lemmas) and remaining > 0:
            lower_lemma = lemmas[i].lower()
            if lower_lemma in lemmatized_filtered_keywords:
                context_words.append(lower_lemma)
                remaining -= 1
            i = i - 1 if is_backward else i + 1
        return context_words

    def _add_n_words_forward(
        self,
        index: int,
        n_words: int,
        lemmas: List[str],
        lemmatized_filtered_keywords: List[str],
    ) -> List[str]:
        return self._add_n_words(
            index, n_words, lemmas, lemmatized_filtered_keywords, False
        )

    def _add_n_words_backward(
        self,
        index: int,
        n_words: int,
        lemmas: List[str],
        lemmatized_filtered_keywords: List[str],
    ) -> List[str]:
        return self._add_n_words(
            index, n_words, lemmas, lemmatized_filtered_keywords, True
        )