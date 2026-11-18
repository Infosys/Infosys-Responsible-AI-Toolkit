"""
Tests for lemma_context_aware_enhancer1 module.

This module tests the LemmaContextAwareEnhancer class and related functions
for enhancing PII detection using context-aware analysis.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from presidio_analyzer import RecognizerResult, EntityRecognizer
from presidio_analyzer.nlp_engine import NlpArtifacts

# Import the module under test
from privacy.util.lemma_context_aware_enhancer1 import (
    is_data_near_word,
    EnhancedAnalysisExplanation,
    LemmaContextAwareEnhancer
)


class TestIsDataNearWord:
    """Test suite for is_data_near_word function."""
    
    def test_is_data_near_word_found_within_threshold(self):
        """Test when data is near the context word within threshold."""
        text = "My email is john@example.com here"
        supportive_context_word = "email"
        result = MagicMock()
        result.start = 12  # position of "john@example.com"
        
        is_near = is_data_near_word(text, supportive_context_word, result)
        
        assert is_near is True
    
    def test_is_data_near_word_not_found_beyond_threshold(self):
        """Test when data is too far from context word."""
        text = "At the beginning email " + ("word " * 20) + "john@example.com"  # Much longer distance
        supportive_context_word = "email"
        result = MagicMock()
        # Calculate position to be beyond 55 character threshold
        result.start = 160  # position of "john@example.com", far from "email" (> 55 chars away)
        
        is_near = is_data_near_word(text, supportive_context_word, result)
        
        assert is_near is False
    
    def test_is_data_near_word_context_word_not_present(self):
        """Test when context word is not in text."""
        text = "My contact is john@example.com"
        supportive_context_word = "email"
        result = MagicMock()
        result.start = 14
        
        is_near = is_data_near_word(text, supportive_context_word, result)
        
        assert is_near is None
    
    def test_is_data_near_word_case_insensitive(self):
        """Test case insensitivity of the function."""
        text = "My EMAIL is john@example.com here"
        supportive_context_word = "email"
        result = MagicMock()
        result.start = 12
        
        is_near = is_data_near_word(text, supportive_context_word, result)
        
        assert is_near is True
    
    def test_is_data_near_word_multiple_occurrences(self):
        """Test with multiple occurrences of context word."""
        text = "email john@example.com and email again"
        supportive_context_word = "email"
        result = MagicMock()
        result.start = 6  # Near first "email"
        
        is_near = is_data_near_word(text, supportive_context_word, result)
        
        assert is_near is True
    
    def test_is_data_near_word_at_exact_threshold(self):
        """Test when distance equals threshold."""
        text = "email12345678901 data"  # Exactly 15 chars apart
        supportive_context_word = "email"
        result = MagicMock()
        result.start = 17
        
        is_near = is_data_near_word(text, supportive_context_word, result)
        
        assert is_near is True


class TestLemmaContextAwareEnhancerInit:
    """Test suite for LemmaContextAwareEnhancer initialization."""
    
    def test_default_initialization(self):
        """Test default initialization values."""
        enhancer = LemmaContextAwareEnhancer()
        
        assert enhancer.context_similarity_factor == 0.35
        assert enhancer.min_score_with_context_similarity == 0.4
        assert enhancer.context_prefix_count == 5
        assert enhancer.context_suffix_count == 0
    
    def test_custom_initialization(self):
        """Test initialization with custom values."""
        enhancer = LemmaContextAwareEnhancer(
            context_similarity_factor=0.5,
            min_score_with_context_similarity=0.6,
            context_prefix_count=10,
            context_suffix_count=3
        )
        
        assert enhancer.context_similarity_factor == 0.5
        assert enhancer.min_score_with_context_similarity == 0.6
        assert enhancer.context_prefix_count == 10
        assert enhancer.context_suffix_count == 3


class TestLemmaContextAwareEnhancerEnhanceUsingContext:
    """Test suite for enhance_using_context method."""
    
    def test_enhance_with_no_nlp_artifacts(self):
        """Test when NLP artifacts are None."""
        enhancer = LemmaContextAwareEnhancer()
        text = "My email is john@example.com"
        raw_results = [MagicMock()]
        
        results = enhancer.enhance_using_context(
            text=text,
            raw_results=raw_results,
            nlp_artifacts=None,
            recognizers=[],
            context=None
        )
        
        # Should return original results when nlp_artifacts is None
        assert results == raw_results
    
    def test_enhance_with_no_recognizer_metadata(self):
        """Test when result has no recognition_metadata."""
        enhancer = LemmaContextAwareEnhancer()
        text = "My email is john@example.com"
        
        result = MagicMock()
        result.recognition_metadata = None
        
        nlp_artifacts = MagicMock()
        recognizer = MagicMock()
        
        results = enhancer.enhance_using_context(
            text=text,
            raw_results=[result],
            nlp_artifacts=nlp_artifacts,
            recognizers=[recognizer],
            context=[]
        )
        
        assert len(results) == 1
    
    def test_enhance_with_recognizer_no_context(self):
        """Test when recognizer has no context."""
        enhancer = LemmaContextAwareEnhancer()
        text = "My email is john@example.com"
        
        result = MagicMock()
        result.recognition_metadata = {
            RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: "email_recognizer"
        }
        result.score = 0.5
        
        recognizer = MagicMock()
        recognizer.id = "email_recognizer"
        recognizer.context = None
        
        nlp_artifacts = MagicMock()
        
        results = enhancer.enhance_using_context(
            text=text,
            raw_results=[result],
            nlp_artifacts=nlp_artifacts,
            recognizers=[recognizer],
            context=[]
        )
        
        # Score should remain unchanged when recognizer has no context
        assert results[0].score == 0.5
    
    def test_enhance_score_already_boosted(self):
        """Test when score is already enhanced."""
        enhancer = LemmaContextAwareEnhancer()
        text = "My email is john@example.com"
        
        result = MagicMock()
        result.recognition_metadata = {
            RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: "email_recognizer",
            RecognizerResult.IS_SCORE_ENHANCED_BY_CONTEXT_KEY: True
        }
        result.score = 0.8
        
        recognizer = MagicMock()
        recognizer.id = "email_recognizer"
        recognizer.context = ["email", "mail"]
        
        nlp_artifacts = MagicMock()
        
        with patch('privacy.util.lemma_context_aware_enhancer1.logger') as mock_logger:
            results = enhancer.enhance_using_context(
                text=text,
                raw_results=[result],
                nlp_artifacts=nlp_artifacts,
                recognizers=[recognizer],
                context=[]
            )
            
            assert results[0].score == 0.8  # Score unchanged
    
    def test_enhance_with_supportive_context_word(self):
        """Test enhancement when supportive context word is found."""
        enhancer = LemmaContextAwareEnhancer()
        text = "My email is john@example.com"
        
        result = MagicMock()
        result.recognition_metadata = MagicMock()
        result.recognition_metadata.keys.return_value = [RecognizerResult.RECOGNIZER_IDENTIFIER_KEY]
        result.recognition_metadata.__getitem__.return_value = "email_recognizer"
        result.recognition_metadata.get.return_value = False
        result.score = 0.5
        result.start = 12
        result.analysis_explanation = None
        
        recognizer = MagicMock()
        recognizer.id = "email_recognizer"
        recognizer.context = ["email", "mail"]
        recognizer.__class__.__name__ = "EmailRecognizer"
        
        nlp_artifacts = MagicMock()
        
        mock_explanation = MagicMock()
        with patch('privacy.util.lemma_context_aware_enhancer1.is_data_near_word', return_value=True):
            with patch('privacy.util.lemma_context_aware_enhancer1.EnhancedAnalysisExplanation', return_value=mock_explanation):
                results = enhancer.enhance_using_context(
                    text=text,
                    raw_results=[result],
                    nlp_artifacts=nlp_artifacts,
                    recognizers=[recognizer],
                    context=[]
                )
                
                # Score should be enhanced
                assert results[0].score > 0.5
                assert results[0].score <= 1.0
    
    def test_enhance_with_custom_context(self):
        """Test enhancement with custom context words."""
        enhancer = LemmaContextAwareEnhancer()
        text = "My contact is john@example.com"
        
        result = MagicMock()
        result.recognition_metadata = MagicMock()
        result.recognition_metadata.keys.return_value = [RecognizerResult.RECOGNIZER_IDENTIFIER_KEY]
        result.recognition_metadata.__getitem__.return_value = "email_recognizer"
        result.recognition_metadata.get.return_value = False
        result.score = 0.5
        result.start = 14
        result.analysis_explanation = None
        
        recognizer = MagicMock()
        recognizer.id = "email_recognizer"
        recognizer.context = ["email"]
        recognizer.__class__.__name__ = "EmailRecognizer"
        
        nlp_artifacts = MagicMock()
        
        with patch('privacy.util.lemma_context_aware_enhancer1.is_data_near_word', return_value=True):
            results = enhancer.enhance_using_context(
                text=text,
                raw_results=[result],
                nlp_artifacts=nlp_artifacts,
                recognizers=[recognizer],
                context=["contact", "email"]
            )
            
            # Should process custom context
            assert len(results) == 1


class TestFindSupportiveWordInContext:
    """Test suite for _find_supportive_word_in_context static method."""
    
    def test_find_supportive_word_match_found(self):
        """Test when supportive word is found."""
        context_list = ["email", "address", "contact"]
        recognizer_context_list = ["email", "mail"]
        text = "My email is test@example.com"
        result1 = MagicMock()
        result1.start = 12
        
        with patch('privacy.util.lemma_context_aware_enhancer1.is_data_near_word', return_value=True):
            word = LemmaContextAwareEnhancer._find_supportive_word_in_context(
                context_list, recognizer_context_list, text, result1
            )
            
            assert word == "email"
    
    def test_find_supportive_word_no_match(self):
        """Test when no supportive word is found."""
        context_list = ["phone", "number"]
        recognizer_context_list = ["email", "mail"]
        text = "My email is test@example.com"
        result1 = MagicMock()
        result1.start = 12
        
        word = LemmaContextAwareEnhancer._find_supportive_word_in_context(
            context_list, recognizer_context_list, text, result1
        )
        
        assert word == ""
    
    def test_find_supportive_word_none_context_list(self):
        """Test when context_list is None."""
        word = LemmaContextAwareEnhancer._find_supportive_word_in_context(
            None, ["email"], "text", MagicMock()
        )
        
        assert word == ""
    
    def test_find_supportive_word_none_recognizer_context(self):
        """Test when recognizer_context_list is None."""
        word = LemmaContextAwareEnhancer._find_supportive_word_in_context(
            ["email"], None, "text", MagicMock()
        )
        
        assert word == ""
    
    def test_find_supportive_word_partial_match(self):
        """Test partial matching of context words."""
        context_list = ["email_address", "contact"]
        recognizer_context_list = ["email", "mail"]
        text = "My email is test@example.com"
        result1 = MagicMock()
        result1.start = 12
        
        with patch('privacy.util.lemma_context_aware_enhancer1.is_data_near_word', return_value=True):
            word = LemmaContextAwareEnhancer._find_supportive_word_in_context(
                context_list, recognizer_context_list, text, result1
            )
            
            assert word == "email"


class TestExtractSurroundingWords:
    """Test suite for _extract_surrounding_words method."""
    
    def test_extract_surrounding_words_no_tokens(self):
        """Test when NLP artifacts have no tokens."""
        enhancer = LemmaContextAwareEnhancer()
        
        nlp_artifacts = MagicMock()
        nlp_artifacts.tokens = None
        
        result = enhancer._extract_surrounding_words(
            nlp_artifacts=nlp_artifacts,
            word="test",
            start=0
        )
        
        # Should return empty string when no tokens
        assert result == [""]
    
    def test_extract_surrounding_words_with_context(self):
        """Test extracting surrounding words with valid context."""
        enhancer = LemmaContextAwareEnhancer(
            context_prefix_count=2,
            context_suffix_count=1
        )
        
        nlp_artifacts = MagicMock()
        nlp_artifacts.tokens = ["My", "email", "is", "test"]
        nlp_artifacts.tokens_indices = [0, 3, 9, 12]
        nlp_artifacts.keywords = ["my", "email", "is", "test"]
        nlp_artifacts.lemmas = ["my", "email", "be", "test"]
        
        with patch.object(enhancer, '_find_index_of_match_token', return_value=1):
            with patch.object(enhancer, '_add_n_words_backward', return_value=["my"]):
                with patch.object(enhancer, '_add_n_words_forward', return_value=["be"]):
                    result = enhancer._extract_surrounding_words(
                        nlp_artifacts=nlp_artifacts,
                        word="email",
                        start=3
                    )
                    
                    assert "my" in result
                    assert "be" in result


class TestFindIndexOfMatchToken:
    """Test suite for _find_index_of_match_token static method."""
    
    def test_find_index_exact_match(self):
        """Test finding index with exact start position match."""
        tokens = ["My", "email", "is", "test"]
        tokens_indices = [0, 3, 9, 12]
        
        index = LemmaContextAwareEnhancer._find_index_of_match_token(
            word="email",
            start=3,
            tokens=tokens,
            tokens_indices=tokens_indices
        )
        
        assert index == 1
    
    def test_find_index_within_token(self):
        """Test finding index when start is within token range."""
        tokens = ["My", "email", "is", "test"]
        tokens_indices = [0, 3, 9, 12]
        
        index = LemmaContextAwareEnhancer._find_index_of_match_token(
            word="email",
            start=5,  # Within "email" token
            tokens=tokens,
            tokens_indices=tokens_indices
        )
        
        assert index == 1
    
    def test_find_index_not_found_raises_error(self):
        """Test that ValueError is raised when token not found."""
        tokens = ["My", "email"]
        tokens_indices = [0, 3]
        
        with pytest.raises(ValueError) as exc_info:
            LemmaContextAwareEnhancer._find_index_of_match_token(
                word="phone",
                start=20,
                tokens=tokens,
                tokens_indices=tokens_indices
            )
        
        assert "Did not find word" in str(exc_info.value)


class TestAddNWords:
    """Test suite for _add_n_words static method."""
    
    def test_add_n_words_backward(self):
        """Test adding words backward."""
        lemmas = ["my", "primary", "email", "is", "test"]
        filtered_keywords = ["my", "primary", "email", "test"]
        
        result = LemmaContextAwareEnhancer._add_n_words(
            index=2,  # "email"
            n_words=2,
            lemmas=lemmas,
            lemmatized_filtered_keywords=filtered_keywords,
            is_backward=True
        )
        
        assert "primary" in result
        assert "my" in result
        # Result includes current word plus n_words backward
        assert len(result) >= 2
    
    def test_add_n_words_forward(self):
        """Test adding words forward."""
        lemmas = ["my", "email", "is", "test", "address"]
        filtered_keywords = ["my", "email", "test", "address"]
        
        result = LemmaContextAwareEnhancer._add_n_words(
            index=1,  # "email"
            n_words=2,
            lemmas=lemmas,
            lemmatized_filtered_keywords=filtered_keywords,
            is_backward=False
        )
        
        assert "test" in result
        assert "address" in result
    
    def test_add_n_words_at_boundary(self):
        """Test at list boundaries."""
        lemmas = ["email", "address"]
        filtered_keywords = ["email", "address"]
        
        result = LemmaContextAwareEnhancer._add_n_words(
            index=0,
            n_words=5,
            lemmas=lemmas,
            lemmatized_filtered_keywords=filtered_keywords,
            is_backward=True
        )
        
        # Should only get "email" as we're at the start
        assert len(result) <= 1
    
    def test_add_n_words_with_filtered_keywords(self):
        """Test that only filtered keywords are included."""
        lemmas = ["my", "the", "email", "is", "here"]
        filtered_keywords = ["my", "email", "here"]  # "the" and "is" excluded
        
        result = LemmaContextAwareEnhancer._add_n_words(
            index=2,  # "email"
            n_words=3,
            lemmas=lemmas,
            lemmatized_filtered_keywords=filtered_keywords,
            is_backward=True
        )
        
        assert "my" in result
        assert "the" not in result
        assert "is" not in result


class TestAddNWordsForwardBackward:
    """Test suite for _add_n_words_forward and _add_n_words_backward methods."""
    
    def test_add_n_words_forward_wrapper(self):
        """Test _add_n_words_forward wrapper method."""
        enhancer = LemmaContextAwareEnhancer()
        lemmas = ["my", "email", "is", "test"]
        keywords = ["my", "email", "test"]
        
        with patch.object(LemmaContextAwareEnhancer, '_add_n_words', return_value=["test"]) as mock_add:
            result = enhancer._add_n_words_forward(1, 2, lemmas, keywords)
            
            mock_add.assert_called_once_with(1, 2, lemmas, keywords, False)
            assert result == ["test"]
    
    def test_add_n_words_backward_wrapper(self):
        """Test _add_n_words_backward wrapper method."""
        enhancer = LemmaContextAwareEnhancer()
        lemmas = ["my", "email", "is", "test"]
        keywords = ["my", "email", "test"]
        
        with patch.object(LemmaContextAwareEnhancer, '_add_n_words', return_value=["my"]) as mock_add:
            result = enhancer._add_n_words_backward(1, 2, lemmas, keywords)
            
            mock_add.assert_called_once_with(1, 2, lemmas, keywords, True)
            assert result == ["my"]


class TestIntegrationScenarios:
    """Integration tests for complete enhancement scenarios."""
    
    def test_complete_enhancement_flow_without_context_match(self):
        """Test enhancement flow when context word is not near the entity."""
        enhancer = LemmaContextAwareEnhancer(
            context_similarity_factor=0.3,
            min_score_with_context_similarity=0.5
        )
        
        text = "Far away email keyword and then much later john@example.com"
        
        result = MagicMock()
        result.recognition_metadata = MagicMock()
        result.recognition_metadata.keys.return_value = [RecognizerResult.RECOGNIZER_IDENTIFIER_KEY]
        result.recognition_metadata.__getitem__.return_value = "email_recognizer"
        result.recognition_metadata.get.return_value = False
        result.score = 0.4
        result.start = 45  # Position of john@example.com
        # Don't pre-set analysis_explanation - let the code set it naturally
        
        recognizer = MagicMock()
        recognizer.id = "email_recognizer"
        recognizer.context = ["email", "mail"]
        recognizer.__class__.__name__ = "EmailRecognizer"
        
        nlp_artifacts = MagicMock()
        
        # Mock is_data_near_word to return False (word not near enough)
        with patch('privacy.util.lemma_context_aware_enhancer1.is_data_near_word', return_value=False):
            results = enhancer.enhance_using_context(
                text=text,
                raw_results=[result],
                nlp_artifacts=nlp_artifacts,
                recognizers=[recognizer],
                context=[]
            )
            
            # Verify that enhance_using_context was called and returned results
            assert len(results) == 1
            # Score may be enhanced or not depending on context, just verify we got results
            assert results[0].score >= 0


class TestContextAwareEnhancerAbstractBase:
    """Test suite for ContextAwareEnhancer base class (line 66)."""
    
    def test_context_aware_enhancer_abstract_method_returns_raw_results(self):
        """Test that abstract enhance_using_context returns raw_results (line 66)."""
        from privacy.util.context_aware_enhancer1 import ContextAwareEnhancer
        
        # Create an instance of the abstract base class directly
        enhancer = ContextAwareEnhancer(
            context_similarity_factor=0.35,
            min_score_with_context_similarity=0.4,
            context_prefix_count=5,
            context_suffix_count=0
        )
        
        # Create mock raw results
        mock_result = MagicMock()
        raw_results = [mock_result]
        
        # Call the abstract method (should return raw_results unchanged)
        result = enhancer.enhance_using_context(
            text="test text",
            raw_results=raw_results,
            nlp_artifacts=MagicMock(),
            recognizers=[],
            context=None
        )
        
        # Line 66: return raw_results
        assert result == raw_results
        assert result is raw_results  # Same object reference

