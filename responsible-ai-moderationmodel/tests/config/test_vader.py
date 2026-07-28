"""
Comprehensive tests for vader.py sentiment analysis module.
Tests cover VaderConstants, SentiText, and SentimentIntensityAnalyzer classes.
"""

import sys
import os
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from config.vader import VaderConstants, SentiText, SentimentIntensityAnalyzer


class TestVaderConstants:
    """Test suite for VaderConstants class."""
    
    def test_constants_initialization(self):
        """Test that VaderConstants initializes with correct values."""
        constants = VaderConstants()
        assert constants.B_INCR == 0.293
        assert constants.B_DECR == -0.293
        assert constants.C_INCR == 0.733
        assert constants.N_SCALAR == -0.74
    
    def test_negate_set_contains_expected_words(self):
        """Test that NEGATE set contains common negation words."""
        constants = VaderConstants()
        assert "not" in constants.NEGATE
        assert "never" in constants.NEGATE
        assert "neither" in constants.NEGATE
        assert "don't" in constants.NEGATE
        assert "cannot" in constants.NEGATE
    
    def test_booster_dict_positive_boosters(self):
        """Test that BOOSTER_DICT contains positive intensity boosters."""
        constants = VaderConstants()
        assert constants.BOOSTER_DICT["very"] == constants.B_INCR
        assert constants.BOOSTER_DICT["extremely"] == constants.B_INCR
        assert constants.BOOSTER_DICT["absolutely"] == constants.B_INCR
    
    def test_booster_dict_negative_dampeners(self):
        """Test that BOOSTER_DICT contains dampening words."""
        constants = VaderConstants()
        assert constants.BOOSTER_DICT["barely"] == constants.B_DECR
        assert constants.BOOSTER_DICT["hardly"] == constants.B_DECR
        assert constants.BOOSTER_DICT["slightly"] == constants.B_DECR
    
    def test_special_case_idioms(self):
        """Test that SPECIAL_CASE_IDIOMS contains expected phrases."""
        constants = VaderConstants()
        assert "the shit" in constants.SPECIAL_CASE_IDIOMS
        assert "bad ass" in constants.SPECIAL_CASE_IDIOMS
        assert "yeah right" in constants.SPECIAL_CASE_IDIOMS
        assert constants.SPECIAL_CASE_IDIOMS["the shit"] == 3
        assert constants.SPECIAL_CASE_IDIOMS["yeah right"] == -2
    
    def test_punc_list_contains_punctuation(self):
        """Test that PUNC_LIST contains expected punctuation marks."""
        constants = VaderConstants()
        assert "." in constants.PUNC_LIST
        assert "!" in constants.PUNC_LIST
        assert "?" in constants.PUNC_LIST
        assert "!!!" in constants.PUNC_LIST
    
    def test_negated_with_negation_words(self):
        """Test negated() method detects negation words."""
        constants = VaderConstants()
        assert constants.negated(["not", "good"]) is True
        assert constants.negated(["never", "again"]) is True
        assert constants.negated(["neither", "here"]) is True
    
    def test_negated_without_negation_words(self):
        """Test negated() method returns False for non-negated input."""
        constants = VaderConstants()
        assert constants.negated(["good", "day"]) is False
        assert constants.negated(["happy", "time"]) is False
    
    def test_negated_with_contraction_nt(self):
        """Test negated() method detects n't contractions."""
        constants = VaderConstants()
        assert constants.negated(["isn't", "good"]) is True
        assert constants.negated(["won't", "work"]) is True
        assert constants.negated(["can't", "do"]) is True
    
    def test_negated_exclude_nt(self):
        """Test negated() with include_nt=False."""
        constants = VaderConstants()
        # "isn't" is in NEGATE set, so returns True even without nt check
        assert constants.negated(["isn't"], include_nt=False) is True
        assert constants.negated(["not"], include_nt=False) is True
        # Test with a word that only has n't but is not in NEGATE
        assert constants.negated(["shouldn't"], include_nt=False) is True
    
    def test_negated_least_pattern(self):
        """Test negated() detects 'least' pattern."""
        constants = VaderConstants()
        assert constants.negated(["the", "least"]) is True
        assert constants.negated(["at", "least"]) is False
    
    def test_normalize_positive_score(self):
        """Test normalize() with positive score."""
        constants = VaderConstants()
        result = constants.normalize(5)
        assert -1 <= result <= 1
        assert result > 0
    
    def test_normalize_negative_score(self):
        """Test normalize() with negative score."""
        constants = VaderConstants()
        result = constants.normalize(-5)
        assert -1 <= result <= 1
        assert result < 0
    
    def test_normalize_zero_score(self):
        """Test normalize() with zero score."""
        constants = VaderConstants()
        result = constants.normalize(0)
        assert result == 0
    
    def test_normalize_custom_alpha(self):
        """Test normalize() with custom alpha value."""
        constants = VaderConstants()
        result1 = constants.normalize(5, alpha=15)
        result2 = constants.normalize(5, alpha=20)
        assert result1 != result2
    
    def test_scalar_inc_dec_booster_positive_valence(self):
        """Test scalar_inc_dec() with booster word and positive valence."""
        constants = VaderConstants()
        scalar = constants.scalar_inc_dec("very", 1.0, False)
        assert scalar == constants.B_INCR
    
    def test_scalar_inc_dec_booster_negative_valence(self):
        """Test scalar_inc_dec() with booster word and negative valence."""
        constants = VaderConstants()
        scalar = constants.scalar_inc_dec("very", -1.0, False)
        assert scalar == -constants.B_INCR
    
    def test_scalar_inc_dec_dampener(self):
        """Test scalar_inc_dec() with dampener word."""
        constants = VaderConstants()
        scalar = constants.scalar_inc_dec("barely", 1.0, False)
        assert scalar == constants.B_DECR
    
    def test_scalar_inc_dec_allcaps_positive(self):
        """Test scalar_inc_dec() with ALL CAPS and positive valence."""
        constants = VaderConstants()
        scalar = constants.scalar_inc_dec("VERY", 1.0, True)
        assert scalar == constants.B_INCR + constants.C_INCR
    
    def test_scalar_inc_dec_allcaps_negative(self):
        """Test scalar_inc_dec() with ALL CAPS and negative valence."""
        constants = VaderConstants()
        scalar = constants.scalar_inc_dec("VERY", -1.0, True)
        assert scalar == -constants.B_INCR - constants.C_INCR
    
    def test_scalar_inc_dec_non_booster_word(self):
        """Test scalar_inc_dec() with non-booster word."""
        constants = VaderConstants()
        scalar = constants.scalar_inc_dec("hello", 1.0, False)
        assert scalar == 0.0


class TestSentiText:
    """Test suite for SentiText class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.constants = VaderConstants()
    
    def test_sentitext_initialization(self):
        """Test SentiText initialization."""
        text = "This is a test."
        senti = SentiText(text, self.constants.PUNC_LIST, self.constants.REGEX_REMOVE_PUNCTUATION)
        assert senti.text == text
        assert isinstance(senti.words_and_emoticons, list)
    
    def test_sentitext_with_non_string_input(self):
        """Test SentiText handles non-string input."""
        # Test with an object that has encode method
        class CustomObj:
            def encode(self, encoding):
                return b"hello"
        
        senti = SentiText(CustomObj(), self.constants.PUNC_LIST, self.constants.REGEX_REMOVE_PUNCTUATION)
        assert isinstance(senti.text, str)
    
    def test_words_plus_punc_basic(self):
        """Test _words_plus_punc() creates correct mappings."""
        text = "Hello, world!"
        senti = SentiText(text, self.constants.PUNC_LIST, self.constants.REGEX_REMOVE_PUNCTUATION)
        words_punc = senti._words_plus_punc()
        assert isinstance(words_punc, dict)
    
    def test_words_and_emoticons_removes_punctuation(self):
        """Test _words_and_emoticons() removes leading/trailing punctuation."""
        text = "Hello, world!"
        senti = SentiText(text, self.constants.PUNC_LIST, self.constants.REGEX_REMOVE_PUNCTUATION)
        words = senti._words_and_emoticons()
        assert "," not in " ".join(words)
    
    def test_words_and_emoticons_preserves_contractions(self):
        """Test _words_and_emoticons() preserves contractions."""
        text = "I don't think so"
        senti = SentiText(text, self.constants.PUNC_LIST, self.constants.REGEX_REMOVE_PUNCTUATION)
        words = senti._words_and_emoticons()
        assert any("don" in w.lower() for w in words)
    
    def test_words_and_emoticons_filters_short_words(self):
        """Test _words_and_emoticons() filters single character words."""
        text = "I a am good"
        senti = SentiText(text, self.constants.PUNC_LIST, self.constants.REGEX_REMOVE_PUNCTUATION)
        words = senti._words_and_emoticons()
        # Single character words should be filtered
        assert all(len(w) > 1 for w in words)
    
    def test_allcap_differential_all_caps(self):
        """Test allcap_differential() when all words are caps."""
        words = ["HELLO", "WORLD"]
        senti = SentiText("test", self.constants.PUNC_LIST, self.constants.REGEX_REMOVE_PUNCTUATION)
        result = senti.allcap_differential(words)
        assert result is False
    
    def test_allcap_differential_no_caps(self):
        """Test allcap_differential() when no words are caps."""
        words = ["hello", "world"]
        senti = SentiText("test", self.constants.PUNC_LIST, self.constants.REGEX_REMOVE_PUNCTUATION)
        result = senti.allcap_differential(words)
        assert result is False
    
    def test_allcap_differential_mixed_caps(self):
        """Test allcap_differential() with mixed capitalization."""
        words = ["HELLO", "world"]
        senti = SentiText("test", self.constants.PUNC_LIST, self.constants.REGEX_REMOVE_PUNCTUATION)
        result = senti.allcap_differential(words)
        assert result is True
    
    def test_allcap_differential_empty_list(self):
        """Test allcap_differential() with empty list."""
        words = []
        senti = SentiText("test", self.constants.PUNC_LIST, self.constants.REGEX_REMOVE_PUNCTUATION)
        result = senti.allcap_differential(words)
        assert result is False
    
    def test_is_cap_diff_set_correctly(self):
        """Test that is_cap_diff is set correctly during initialization."""
        text = "HELLO world"
        senti = SentiText(text, self.constants.PUNC_LIST, self.constants.REGEX_REMOVE_PUNCTUATION)
        assert senti.is_cap_diff is True
        
        text2 = "hello world"
        senti2 = SentiText(text2, self.constants.PUNC_LIST, self.constants.REGEX_REMOVE_PUNCTUATION)
        assert senti2.is_cap_diff is False


class TestSentimentIntensityAnalyzer:
    """Test suite for SentimentIntensityAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures with mocked lexicon."""
        # Mock the lexicon file loading
        mock_lexicon_content = "good\t2.0\nbad\t-2.0\nhappy\t2.5\nsad\t-2.5\nterrible\t-3.0\namazing\t3.0\nokay\t1.0\nneutral\t0.0"
        
        with patch('nltk.data.load', return_value=mock_lexicon_content):
            self.analyzer = SentimentIntensityAnalyzer()
    
    def test_analyzer_initialization(self):
        """Test SentimentIntensityAnalyzer initializes correctly."""
        assert self.analyzer.lexicon is not None
        assert isinstance(self.analyzer.lexicon, dict)
        assert hasattr(self.analyzer, 'constants')
    
    def test_make_lex_dict(self):
        """Test make_lex_dict() creates correct dictionary."""
        assert "good" in self.analyzer.lexicon
        assert "bad" in self.analyzer.lexicon
        assert self.analyzer.lexicon["good"] == 2.0
        assert self.analyzer.lexicon["bad"] == -2.0
    
    def test_polarity_scores_positive_text(self):
        """Test polarity_scores() with positive text."""
        result = self.analyzer.polarity_scores("I am very good")
        assert "compound" in result
        assert "pos" in result
        assert "neg" in result
        assert "neu" in result
        assert result["compound"] > 0
    
    def test_polarity_scores_negative_text(self):
        """Test polarity_scores() with negative text."""
        result = self.analyzer.polarity_scores("This is bad")
        assert result["compound"] < 0
    
    def test_polarity_scores_neutral_text(self):
        """Test polarity_scores() with neutral text."""
        result = self.analyzer.polarity_scores("The sky is blue")
        assert -0.5 < result["compound"] < 0.5
    
    def test_polarity_scores_empty_text(self):
        """Test polarity_scores() with empty text."""
        result = self.analyzer.polarity_scores("")
        assert result["compound"] == 0.0
        assert result["pos"] == 0.0
        assert result["neg"] == 0.0
        assert result["neu"] == 0.0
    
    def test_polarity_scores_with_exclamation(self):
        """Test polarity_scores() amplifies with exclamation marks."""
        result1 = self.analyzer.polarity_scores("I am good")
        result2 = self.analyzer.polarity_scores("I am good!")
        result3 = self.analyzer.polarity_scores("I am good!!")
        assert result2["compound"] > result1["compound"]
        assert result3["compound"] > result2["compound"]
    
    def test_polarity_scores_with_question_marks(self):
        """Test polarity_scores() with multiple question marks."""
        result1 = self.analyzer.polarity_scores("Is this good")
        result2 = self.analyzer.polarity_scores("Is this good??")
        result3 = self.analyzer.polarity_scores("Is this good???")
        # Question marks should amplify
        assert result2["compound"] >= result1["compound"]
    
    def test_polarity_scores_with_but(self):
        """Test polarity_scores() handles 'but' correctly."""
        result = self.analyzer.polarity_scores("It was good but bad")
        assert "compound" in result
    
    def test_sentiment_valence_word_not_in_lexicon(self):
        """Test sentiment_valence() with word not in lexicon."""
        sentitext = SentiText("hello", self.analyzer.constants.PUNC_LIST, 
                             self.analyzer.constants.REGEX_REMOVE_PUNCTUATION)
        sentiments = []
        result = self.analyzer.sentiment_valence(0, sentitext, "hello", 0, sentiments)
        assert 0 in result
    
    def test_sentiment_valence_word_in_lexicon(self):
        """Test sentiment_valence() with word in lexicon."""
        sentitext = SentiText("good", self.analyzer.constants.PUNC_LIST, 
                             self.analyzer.constants.REGEX_REMOVE_PUNCTUATION)
        sentiments = []
        result = self.analyzer.sentiment_valence(0, sentitext, "good", 0, sentiments)
        assert any(v != 0 for v in result)
    
    def test_apply_caps_modifier_no_caps(self):
        """Test _apply_caps_modifier() with no capitalization."""
        result = self.analyzer._apply_caps_modifier("good", 2.0, False)
        assert result == 2.0
    
    def test_apply_caps_modifier_with_caps_positive(self):
        """Test _apply_caps_modifier() with ALL CAPS and positive valence."""
        result = self.analyzer._apply_caps_modifier("GOOD", 2.0, True)
        assert result > 2.0
        assert result == 2.0 + self.analyzer.constants.C_INCR
    
    def test_apply_caps_modifier_with_caps_negative(self):
        """Test _apply_caps_modifier() with ALL CAPS and negative valence."""
        result = self.analyzer._apply_caps_modifier("BAD", -2.0, True)
        assert result < -2.0
        assert result == -2.0 - self.analyzer.constants.C_INCR
    
    def test_process_preceding_words_no_preceding(self):
        """Test _process_preceding_words() with no preceding words."""
        words = ["good"]
        result = self.analyzer._process_preceding_words(2.0, words, 0, False)
        assert result == 2.0
    
    def test_process_preceding_words_with_booster(self):
        """Test _process_preceding_words() with booster word."""
        words = ["very", "good"]
        result = self.analyzer._process_preceding_words(2.0, words, 1, False)
        assert result > 2.0
    
    def test_should_process_preceding_word_at_start(self):
        """Test _should_process_preceding_word() at start of sentence."""
        words = ["good"]
        result = self.analyzer._should_process_preceding_word(words, 0, 0)
        assert result is False
    
    def test_should_process_preceding_word_word_in_lexicon(self):
        """Test _should_process_preceding_word() when word is in lexicon."""
        words = ["good", "bad"]
        result = self.analyzer._should_process_preceding_word(words, 1, 0)
        assert result is False
    
    def test_should_process_preceding_word_word_not_in_lexicon(self):
        """Test _should_process_preceding_word() when word not in lexicon."""
        words = ["really", "good"]
        result = self.analyzer._should_process_preceding_word(words, 1, 0)
        assert result is True
    
    def test_apply_scalar_modifier(self):
        """Test _apply_scalar_modifier() applies scalar correctly."""
        words = ["very", "good"]
        result = self.analyzer._apply_scalar_modifier(2.0, words, 1, 0, False)
        assert result != 2.0
    
    def test_apply_distance_dampening_zero_scalar(self):
        """Test _apply_distance_dampening() with zero scalar."""
        result = self.analyzer._apply_distance_dampening(0, 1)
        assert result == 0
    
    def test_apply_distance_dampening_distance_zero(self):
        """Test _apply_distance_dampening() at distance 0."""
        result = self.analyzer._apply_distance_dampening(0.293, 0)
        assert result == 0.293
    
    def test_apply_distance_dampening_distance_one(self):
        """Test _apply_distance_dampening() at distance 1."""
        result = self.analyzer._apply_distance_dampening(0.293, 1)
        assert result == 0.293 * 0.95
    
    def test_apply_distance_dampening_distance_two(self):
        """Test _apply_distance_dampening() at distance 2."""
        result = self.analyzer._apply_distance_dampening(0.293, 2)
        assert result == 0.293 * 0.9
    
    def test_least_check_with_least_pattern(self):
        """Test _least_check() detects 'least' negation."""
        words = ["the", "least", "good"]
        result = self.analyzer._least_check(2.0, words, 2)
        assert result < 2.0
    
    def test_least_check_with_at_least(self):
        """Test _least_check() doesn't negate 'at least'."""
        words = ["at", "least", "good"]
        result = self.analyzer._least_check(2.0, words, 2)
        assert result == 2.0
    
    def test_least_check_with_very_least(self):
        """Test _least_check() doesn't negate 'very least'."""
        words = ["very", "least", "good"]
        result = self.analyzer._least_check(2.0, words, 2)
        assert result == 2.0
    
    def test_least_check_immediate_least(self):
        """Test _least_check() with immediate 'least'."""
        words = ["least", "good"]
        result = self.analyzer._least_check(2.0, words, 1)
        assert result < 2.0
    
    def test_but_check_no_but(self):
        """Test _but_check() with no 'but' in sentence."""
        words = ["I", "am", "good"]
        sentiments = [0, 0, 2.0]
        result = self.analyzer._but_check(words, sentiments)
        assert result == sentiments
    
    def test_but_check_with_but(self):
        """Test _but_check() modifies sentiments around 'but'."""
        words = ["good", "but", "bad"]
        sentiments = [2.0, 0, -2.0]
        result = self.analyzer._but_check(words, sentiments)
        assert result[0] == 2.0 * 0.5
        assert result[2] == -2.0 * 1.5
    
    def test_idioms_check_one_zero_pattern(self):
        """Test _idioms_check() detects one-zero idiom pattern."""
        words = ["the", "the", "shit", "is"]
        # "the shit" is an idiom
        result = self.analyzer._idioms_check(0, words, 2)
        assert result == 3  # "the shit" has value 3
    
    def test_idioms_check_two_one_zero_pattern(self):
        """Test _idioms_check() detects two-one-zero idiom pattern."""
        words = ["is", "bad", "ass", "really"]
        # "bad ass" is an idiom
        result = self.analyzer._idioms_check(0, words, 2)
        assert result == 1.5
    
    def test_idioms_check_zero_one_pattern(self):
        """Test _idioms_check() detects zero-one forward pattern."""
        words = ["that", "is", "the", "shit"]
        result = self.analyzer._idioms_check(0, words, 2)
        assert result != 0
    
    def test_idioms_check_with_booster_bigram(self):
        """Test _idioms_check() handles booster bigrams."""
        words = ["kind", "of", "good"]
        result = self.analyzer._idioms_check(2.0, words, 2)
        assert result < 2.0  # Should apply B_DECR
    
    def test_never_check_immediate_negation(self):
        """Test _never_check() with immediate negation (start_i=0)."""
        words = ["not", "good"]
        result = self.analyzer._never_check(2.0, words, 0, 1)
        assert result < 0
    
    def test_never_check_distance_one(self):
        """Test _never_check() at distance one (start_i=1)."""
        words = ["not", "very", "good"]
        result = self.analyzer._never_check(2.0, words, 1, 2)
        assert result < 0
    
    def test_never_check_distance_two(self):
        """Test _never_check() at distance two (start_i=2)."""
        words = ["not", "am", "very", "good"]
        result = self.analyzer._never_check(2.0, words, 2, 3)
        assert result < 0
    
    def test_check_immediate_negation_with_negation(self):
        """Test _check_immediate_negation() detects negation."""
        words = ["not", "good"]
        result = self.analyzer._check_immediate_negation(2.0, words, 1)
        assert result == 2.0 * self.analyzer.constants.N_SCALAR
    
    def test_check_immediate_negation_without_negation(self):
        """Test _check_immediate_negation() without negation."""
        words = ["very", "good"]
        result = self.analyzer._check_immediate_negation(2.0, words, 1)
        assert result == 2.0
    
    def test_check_distance_one_negation_never_so_pattern(self):
        """Test _check_distance_one_negation() with 'never so' pattern."""
        words = ["never", "so", "good"]
        result = self.analyzer._check_distance_one_negation(2.0, words, 2)
        assert result == 2.0 * 1.5
    
    def test_check_distance_one_negation_with_negation(self):
        """Test _check_distance_one_negation() with negation."""
        words = ["not", "very", "good"]
        result = self.analyzer._check_distance_one_negation(2.0, words, 2)
        assert result < 0
    
    def test_check_distance_two_negation_with_emphasis(self):
        """Test _check_distance_two_negation() with emphasis pattern."""
        words = ["never", "so", "very", "good"]
        result = self.analyzer._check_distance_two_negation(2.0, words, 3)
        # 'never' at i-3 causes negation despite 'so' emphasis
        assert result < 0
    
    def test_check_distance_two_negation_with_negation(self):
        """Test _check_distance_two_negation() with negation."""
        words = ["not", "am", "very", "good"]
        result = self.analyzer._check_distance_two_negation(2.0, words, 3)
        assert result < 0
    
    def test_is_never_so_this_pattern_true(self):
        """Test _is_never_so_this_pattern() detects pattern."""
        words = ["never", "so", "good"]
        result = self.analyzer._is_never_so_this_pattern(words, 2, distance=2)
        assert result is True
    
    def test_is_never_so_this_pattern_false(self):
        """Test _is_never_so_this_pattern() with no pattern."""
        words = ["I", "am", "good"]
        result = self.analyzer._is_never_so_this_pattern(words, 2, distance=2)
        assert result is False
    
    def test_is_never_so_this_pattern_insufficient_words(self):
        """Test _is_never_so_this_pattern() with insufficient words."""
        words = ["good"]
        result = self.analyzer._is_never_so_this_pattern(words, 0, distance=2)
        assert result is False
    
    def test_has_never_emphasis_pattern_true(self):
        """Test _has_never_emphasis_pattern() detects pattern."""
        words = ["never", "so", "this", "good"]
        result = self.analyzer._has_never_emphasis_pattern(words, 3)
        # Returns True when 'never' at i-3 and 'so' or 'this' at i-1
        assert result is True
    
    def test_has_never_emphasis_pattern_false(self):
        """Test _has_never_emphasis_pattern() with no pattern."""
        words = ["I", "am", "very", "good"]
        result = self.analyzer._has_never_emphasis_pattern(words, 3)
        assert result is False
    
    def test_has_never_emphasis_pattern_insufficient_words(self):
        """Test _has_never_emphasis_pattern() with insufficient words."""
        words = ["good", "day"]
        result = self.analyzer._has_never_emphasis_pattern(words, 1)
        assert result is False
    
    def test_punctuation_emphasis(self):
        """Test _punctuation_emphasis() combines exclamation and question marks."""
        result = self.analyzer._punctuation_emphasis("Really?!")
        assert result > 0
    
    def test_amplify_ep_single_exclamation(self):
        """Test _amplify_ep() with single exclamation mark."""
        result = self.analyzer._amplify_ep("Good!")
        assert result == 0.292
    
    def test_amplify_ep_multiple_exclamations(self):
        """Test _amplify_ep() with multiple exclamation marks."""
        result = self.analyzer._amplify_ep("Good!!!")
        assert result == 0.292 * 3
    
    def test_amplify_ep_max_four_exclamations(self):
        """Test _amplify_ep() caps at 4 exclamation marks."""
        result1 = self.analyzer._amplify_ep("Good!!!!")
        result2 = self.analyzer._amplify_ep("Good!!!!!")
        assert result1 == result2
        assert result1 == 0.292 * 4
    
    def test_amplify_qm_single_question(self):
        """Test _amplify_qm() with single question mark."""
        result = self.analyzer._amplify_qm("Good?")
        assert result == 0
    
    def test_amplify_qm_two_questions(self):
        """Test _amplify_qm() with two question marks."""
        result = self.analyzer._amplify_qm("Good??")
        assert result == 0.18 * 2
    
    def test_amplify_qm_three_questions(self):
        """Test _amplify_qm() with three question marks."""
        result = self.analyzer._amplify_qm("Good???")
        assert result == 0.18 * 3
    
    def test_amplify_qm_many_questions(self):
        """Test _amplify_qm() with many question marks."""
        result = self.analyzer._amplify_qm("Good?????")
        assert result == 0.96
    
    def test_sift_sentiment_scores_positive(self):
        """Test _sift_sentiment_scores() with positive scores."""
        sentiments = [2.0, 1.5, 1.0]
        pos_sum, neg_sum, neu_count = self.analyzer._sift_sentiment_scores(sentiments)
        assert pos_sum > 0
        assert neg_sum == 0
        assert neu_count == 0
    
    def test_sift_sentiment_scores_negative(self):
        """Test _sift_sentiment_scores() with negative scores."""
        sentiments = [-2.0, -1.5, -1.0]
        pos_sum, neg_sum, neu_count = self.analyzer._sift_sentiment_scores(sentiments)
        assert pos_sum == 0
        assert neg_sum < 0
        assert neu_count == 0
    
    def test_sift_sentiment_scores_neutral(self):
        """Test _sift_sentiment_scores() with neutral scores."""
        sentiments = [0, 0, 0]
        pos_sum, neg_sum, neu_count = self.analyzer._sift_sentiment_scores(sentiments)
        assert pos_sum == 0
        assert neg_sum == 0
        assert neu_count == 3
    
    def test_sift_sentiment_scores_mixed(self):
        """Test _sift_sentiment_scores() with mixed scores."""
        sentiments = [2.0, -1.5, 0, 1.0]
        pos_sum, neg_sum, neu_count = self.analyzer._sift_sentiment_scores(sentiments)
        assert pos_sum > 0
        assert neg_sum < 0
        assert neu_count == 1
    
    def test_score_valence_with_sentiments(self):
        """Test score_valence() with non-empty sentiments."""
        sentiments = [2.0, 1.5, 1.0]
        result = self.analyzer.score_valence(sentiments, "Good text")
        assert "compound" in result
        assert "pos" in result
        assert "neg" in result
        assert "neu" in result
        assert result["compound"] > 0
    
    def test_score_valence_empty_sentiments(self):
        """Test score_valence() with empty sentiments."""
        sentiments = []
        result = self.analyzer.score_valence(sentiments, "")
        assert result["compound"] == 0.0
        assert result["pos"] == 0.0
        assert result["neg"] == 0.0
        assert result["neu"] == 0.0
    
    def test_score_valence_positive_with_exclamation(self):
        """Test score_valence() amplifies positive with exclamation."""
        sentiments = [2.0]
        result1 = self.analyzer.score_valence(sentiments, "Good")
        result2 = self.analyzer.score_valence(sentiments, "Good!")
        assert result2["compound"] > result1["compound"]
    
    def test_score_valence_negative_with_exclamation(self):
        """Test score_valence() amplifies negative with exclamation."""
        sentiments = [-2.0]
        result1 = self.analyzer.score_valence(sentiments, "Bad")
        result2 = self.analyzer.score_valence(sentiments, "Bad!")
        assert result2["compound"] < result1["compound"]
    
    def test_score_valence_rounds_correctly(self):
        """Test score_valence() rounds values correctly."""
        sentiments = [1.23456]
        result = self.analyzer.score_valence(sentiments, "test")
        assert len(str(result["pos"]).split(".")[-1]) <= 3
        assert len(str(result["neg"]).split(".")[-1]) <= 3
        assert len(str(result["neu"]).split(".")[-1]) <= 3
        assert len(str(result["compound"]).split(".")[-1]) <= 4


class TestIntegrationScenarios:
    """Integration tests for complete sentiment analysis workflows."""
    
    def setup_method(self):
        """Set up test fixtures."""
        mock_lexicon_content = "good\t2.0\nbad\t-2.0\nhappy\t2.5\nsad\t-2.5\nterrible\t-3.0\namazing\t3.0\nokay\t1.0\nneutral\t0.0\ngreat\t2.8"
        
        with patch('nltk.data.load', return_value=mock_lexicon_content):
            self.analyzer = SentimentIntensityAnalyzer()
    
    def test_complex_positive_sentence(self):
        """Test complex positive sentence with boosters."""
        result = self.analyzer.polarity_scores("This is amazingly good!")
        assert result["compound"] > 0
        assert result["pos"] > result["neg"]
    
    def test_complex_negative_sentence(self):
        """Test complex negative sentence with negation."""
        result = self.analyzer.polarity_scores("This is not good at all")
        assert result["compound"] < 0
    
    def test_sentence_with_but_reversal(self):
        """Test sentence with 'but' causing sentiment reversal."""
        result = self.analyzer.polarity_scores("It was okay but terrible")
        assert result["compound"] < 0
    
    def test_sentence_with_multiple_punctuation(self):
        """Test sentence with multiple punctuation marks."""
        result = self.analyzer.polarity_scores("This is so good!!!")
        assert result["compound"] > 0
    
    def test_sentence_with_allcaps(self):
        """Test sentence with ALL CAPS for emphasis."""
        result1 = self.analyzer.polarity_scores("This is GOOD")
        result2 = self.analyzer.polarity_scores("This is good")
        assert abs(result1["compound"]) > abs(result2["compound"])
    
    def test_sentence_with_kind_of(self):
        """Test sentence with 'kind of' dampening."""
        result = self.analyzer.polarity_scores("It is kind of good")
        assert result["compound"] > 0
    
    def test_mixed_sentiment_sentence(self):
        """Test sentence with mixed positive and negative."""
        result = self.analyzer.polarity_scores("I'm happy but also sad")
        assert "compound" in result


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        mock_lexicon_content = "good\t2.0\nbad\t-2.0"
        
        with patch('nltk.data.load', return_value=mock_lexicon_content):
            self.analyzer = SentimentIntensityAnalyzer()
    
    def test_very_long_sentence(self):
        """Test with very long sentence."""
        long_text = " ".join(["good"] * 100)
        result = self.analyzer.polarity_scores(long_text)
        assert result["compound"] > 0
    
    def test_unicode_text(self):
        """Test with unicode characters."""
        result = self.analyzer.polarity_scores("This is good 😊")
        assert "compound" in result
    
    def test_only_punctuation(self):
        """Test with only punctuation."""
        result = self.analyzer.polarity_scores("!!!")
        assert result["compound"] == 0.0
    
    def test_only_whitespace(self):
        """Test with only whitespace."""
        result = self.analyzer.polarity_scores("   ")
        assert result["compound"] == 0.0
    
    def test_single_word(self):
        """Test with single sentiment word."""
        result = self.analyzer.polarity_scores("good")
        assert result["compound"] > 0
    
    def test_negation_only(self):
        """Test with negation words only."""
        result = self.analyzer.polarity_scores("not never")
        assert result["compound"] == 0.0
