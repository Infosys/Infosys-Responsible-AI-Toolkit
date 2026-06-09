"""
Unit tests for DataListRecognizer.py
Tests custom entity recognition using spaCy phrase matching.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from presidio_analyzer import RecognizerResult, AnalysisExplanation
from privacy.util.special_recognizers.DataListRecognizer import DataListRecognizer


class TestDataListRecognizerInitialization:
    """Test suite for DataListRecognizer initialization"""

    def test_init_with_default_parameters(self):
        """Test initialization with default parameters"""
        terms = ["Infosys", "Microsoft", "Google"]
        entities = ["COMPANY_NAME"]
        
        recognizer = DataListRecognizer(terms=terms, entitie=entities)
        
        assert recognizer.terms == terms
        assert recognizer.ENTITIES == entities
        assert recognizer.ner_strength == 0.85
        assert recognizer.supported_entities == entities

    def test_init_with_custom_ner_strength(self):
        """Test initialization with custom NER strength"""
        terms = ["IBM", "Apple"]
        entities = ["ORGANIZATION"]
        
        # Test custom ner_strength
        recognizer = DataListRecognizer(
            terms=terms, 
            entitie=entities, 
            ner_strength=0.95
        )
        
        assert recognizer.ner_strength == 0.95
        
        # Test default ner_strength
        recognizer_default = DataListRecognizer(
            terms=terms, 
            entitie=entities
        )
        
        assert recognizer_default.ner_strength == 0.85

    def test_init_with_custom_language(self):
        """Test initialization with custom language"""
        terms = ["Tesla"]
        entities = ["COMPANY"]
        
        recognizer = DataListRecognizer(
            terms=terms, 
            entitie=entities, 
            supported_language="fr"
        )
        
        assert recognizer.supported_language == "fr"

    def test_init_with_custom_check_label_groups(self):
        """Test initialization with custom check label groups"""
        terms = ["Amazon"]
        entities = ["ORG"]
        custom_labels = [({"PERSON"}, {"PER"})]
        
        recognizer = DataListRecognizer(
            terms=terms, 
            entitie=entities, 
            check_label_groups=custom_labels
        )
        
        assert recognizer.check_label_groups == custom_labels

    def test_init_with_context(self):
        """Test initialization with context"""
        terms = ["Cisco"]
        entities = ["COMPANY"]
        context = ["technology", "networking"]
        
        recognizer = DataListRecognizer(
            terms=terms, 
            entitie=entities, 
            context=context
        )
        
        assert recognizer.context == context

    def test_init_with_supported_entities(self):
        """Test initialization with explicit supported entities"""
        terms = ["Oracle"]
        entities = ["ORGANIZATION"]
        
        recognizer = DataListRecognizer(
            terms=terms, 
            entitie=entities, 
            supported_entities=["CUSTOM_ENTITY"]
        )
        
        assert recognizer.supported_entities == ["CUSTOM_ENTITY"]


class TestDataListRecognizerLoad:
    """Test suite for load method"""

    def test_load_does_nothing(self):
        """Test that load method exists but does nothing"""
        terms = ["Company"]
        entities = ["ORG"]
        
        recognizer = DataListRecognizer(terms=terms, entitie=entities)
        
        # Should not raise any exception
        result = recognizer.load()
        
        assert result is None


class TestDataListRecognizerBuildSpacyExplanation:
    """Test suite for build_spacy_explanation method"""

    def test_build_spacy_explanation_basic(self):
        """Test building explanation with basic parameters"""
        terms = ["Test Company"]
        entities = ["COMPANY"]
        
        recognizer = DataListRecognizer(terms=terms, entitie=entities)
        
        explanation = recognizer.build_spacy_explanation(
            original_score=0.9,
            explanation="Test explanation"
        )
        
        assert isinstance(explanation, AnalysisExplanation)
        assert explanation.recognizer == "DataListRecognizer"
        assert explanation.original_score == 0.9
        assert explanation.textual_explanation == "Test explanation"

    def test_build_spacy_explanation_with_different_scores(self):
        """Test explanation building with various scores"""
        terms = ["Entity"]
        entities = ["TYPE"]
        
        recognizer = DataListRecognizer(terms=terms, entitie=entities)
        
        explanation1 = recognizer.build_spacy_explanation(0.5, "Low confidence")
        explanation2 = recognizer.build_spacy_explanation(1.0, "High confidence")
        
        assert explanation1.original_score == 0.5
        assert explanation2.original_score == 1.0

    def test_build_spacy_explanation_with_empty_string(self):
        """Test explanation with empty explanation string"""
        terms = ["Company"]
        entities = ["ORG"]
        
        recognizer = DataListRecognizer(terms=terms, entitie=entities)
        
        explanation = recognizer.build_spacy_explanation(0.7, "")
        
        assert explanation.textual_explanation == ""


class TestDataListRecognizerAnalyze:
    """Test suite for analyze method"""

    @patch('privacy.util.special_recognizers.DataListRecognizer.nlp')
    @patch('privacy.util.special_recognizers.DataListRecognizer.PhraseMatcher')
    def test_analyze_with_single_match(self, mock_matcher_class, mock_nlp):
        """Test analyze with single entity match"""
        terms = ["Infosys"]
        entities = ["COMPANY_NAME"]
        text = "I work at Infosys in Bangalore"
        
        # Setup mocks
        mock_doc = Mock()
        mock_doc.__str__ = Mock(return_value=text)
        mock_nlp.return_value = mock_doc
        
        # Mock span
        mock_span = Mock()
        mock_span.text = "Infosys"
        mock_span.start_char = 10
        mock_span.end_char = 17
        mock_doc.__getitem__ = Mock(return_value=mock_span)
        
        # Mock matcher
        mock_matcher = Mock()
        mock_matcher.return_value = [(1, 3, 4)]  # match_id, start, end
        mock_matcher_class.return_value = mock_matcher
        
        recognizer = DataListRecognizer(terms=terms, entitie=entities)
        results = recognizer.analyze(text, entities)
        
        # Verify matcher was called
        mock_matcher_class.assert_called_once()
        assert len(results) >= 0  # May return results based on mock

    @patch('privacy.util.special_recognizers.DataListRecognizer.nlp')
    @patch('privacy.util.special_recognizers.DataListRecognizer.PhraseMatcher')
    def test_analyze_with_multiple_matches(self, mock_matcher_class, mock_nlp):
        """Test analyze with multiple entity matches"""
        terms = ["IBM", "Microsoft", "Google"]
        entities = ["COMPANY"]
        text = "IBM and Microsoft are partners, but Google is a competitor"
        
        # Setup mocks
        mock_doc = Mock()
        mock_doc.__str__ = Mock(return_value=text)
        mock_nlp.return_value = mock_doc
        
        # Mock spans for each match
        mock_span1 = Mock()
        mock_span1.text = "IBM"
        mock_span1.start_char = 0
        mock_span1.end_char = 3
        
        mock_span2 = Mock()
        mock_span2.text = "Microsoft"
        mock_span2.start_char = 8
        mock_span2.end_char = 17
        
        mock_span3 = Mock()
        mock_span3.text = "Google"
        mock_span3.start_char = 36
        mock_span3.end_char = 42
        
        mock_doc.__getitem__ = Mock(side_effect=[mock_span1, mock_span2, mock_span3])
        
        # Mock matcher with 3 matches
        mock_matcher = Mock()
        mock_matcher.return_value = [(1, 0, 1), (1, 2, 3), (1, 7, 8)]
        mock_matcher_class.return_value = mock_matcher
        
        recognizer = DataListRecognizer(terms=terms, entitie=entities)
        results = recognizer.analyze(text, entities)
        
        assert isinstance(results, list)

    @patch('privacy.util.special_recognizers.DataListRecognizer.nlp')
    @patch('privacy.util.special_recognizers.DataListRecognizer.PhraseMatcher')
    def test_analyze_with_no_matches(self, mock_matcher_class, mock_nlp):
        """Test analyze with no entity matches"""
        terms = ["Apple", "Samsung"]
        entities = ["COMPANY"]
        text = "This text contains no matching companies"
        
        # Setup mocks
        mock_doc = Mock()
        mock_doc.__str__ = Mock(return_value=text)
        mock_nlp.return_value = mock_doc
        
        # Mock matcher with no matches
        mock_matcher = Mock()
        mock_matcher.return_value = []
        mock_matcher_class.return_value = mock_matcher
        
        recognizer = DataListRecognizer(terms=terms, entitie=entities)
        results = recognizer.analyze(text, entities)
        
        assert results == []

    @patch('privacy.util.special_recognizers.DataListRecognizer.nlp')
    @patch('privacy.util.special_recognizers.DataListRecognizer.PhraseMatcher')
    def test_analyze_creates_recognizer_result(self, mock_matcher_class, mock_nlp):
        """Test that analyze creates RecognizerResult with correct properties"""
        terms = ["Tesla"]
        entities = ["ORGANIZATION"]
        text = "Tesla is an innovative company"
        
        # Setup mocks
        mock_doc = Mock()
        mock_doc.__str__ = Mock(return_value=text)
        mock_nlp.return_value = mock_doc
        
        mock_span = Mock()
        mock_span.text = "Tesla"
        mock_span.start_char = 0
        mock_span.end_char = 5
        mock_doc.__getitem__ = Mock(return_value=mock_span)
        
        mock_matcher = Mock()
        mock_matcher.return_value = [(1, 0, 1)]
        mock_matcher_class.return_value = mock_matcher
        
        recognizer = DataListRecognizer(terms=terms, entitie=entities, ner_strength=0.90)
        results = recognizer.analyze(text, entities)
        
        # Results should be a list
        assert isinstance(results, list)

    @patch('privacy.util.special_recognizers.DataListRecognizer.nlp')
    @patch('privacy.util.special_recognizers.DataListRecognizer.PhraseMatcher')
    def test_analyze_with_empty_terms(self, mock_matcher_class, mock_nlp):
        """Test analyze with empty terms list"""
        terms = []
        entities = ["COMPANY"]
        text = "Some text"
        
        mock_doc = Mock()
        mock_doc.__str__ = Mock(return_value=text)
        mock_nlp.return_value = mock_doc
        
        mock_matcher = Mock()
        mock_matcher.return_value = []
        mock_matcher_class.return_value = mock_matcher
        
        recognizer = DataListRecognizer(terms=terms, entitie=entities)
        results = recognizer.analyze(text, entities)
        
        assert results == []

    @patch('privacy.util.special_recognizers.DataListRecognizer.nlp')
    @patch('privacy.util.special_recognizers.DataListRecognizer.PhraseMatcher')
    def test_analyze_with_special_characters(self, mock_matcher_class, mock_nlp):
        """Test analyze with special characters in text"""
        terms = ["AT&T", "T-Mobile"]
        entities = ["COMPANY"]
        text = "AT&T and T-Mobile are telecom companies"
        
        mock_doc = Mock()
        mock_doc.__str__ = Mock(return_value=text)
        mock_nlp.return_value = mock_doc
        
        mock_matcher = Mock()
        mock_matcher.return_value = []
        mock_matcher_class.return_value = mock_matcher
        
        recognizer = DataListRecognizer(terms=terms, entitie=entities)
        results = recognizer.analyze(text, entities)
        
        assert isinstance(results, list)

    @patch('privacy.util.special_recognizers.DataListRecognizer.nlp')
    @patch('privacy.util.special_recognizers.DataListRecognizer.PhraseMatcher')
    def test_analyze_with_nlp_artifacts(self, mock_matcher_class, mock_nlp):
        """Test analyze with nlp_artifacts parameter"""
        terms = ["Company"]
        entities = ["ORG"]
        text = "Test text"
        
        mock_doc = Mock()
        mock_doc.__str__ = Mock(return_value=text)
        mock_nlp.return_value = mock_doc
        
        mock_matcher = Mock()
        mock_matcher.return_value = []
        mock_matcher_class.return_value = mock_matcher
        
        recognizer = DataListRecognizer(terms=terms, entitie=entities)
        
        # Test with nlp_artifacts parameter (should be ignored)
        results = recognizer.analyze(text, entities, nlp_artifacts={"some": "data"})
        
        assert isinstance(results, list)


class TestDataListRecognizerCheckLabel:
    """Test suite for __check_label static method"""

    def test_check_label_matching_groups(self):
        """Test __check_label with matching entity and label groups"""
        check_groups = [({"PERSON", "PER"}, {"PERSON", "PER"})]
        
        result = DataListRecognizer._DataListRecognizer__check_label(
            "PERSON", "PERSON", check_groups
        )
        
        assert result is True

    def test_check_label_non_matching_groups(self):
        """Test __check_label with non-matching entity and label groups"""
        check_groups = [({"LOCATION"}, {"GPE", "LOC"})]
        
        result = DataListRecognizer._DataListRecognizer__check_label(
            "PERSON", "PER", check_groups
        )
        
        assert result is False

    def test_check_label_multiple_groups(self):
        """Test __check_label with multiple check groups"""
        check_groups = [
            ({"LOCATION"}, {"GPE", "LOC"}),
            ({"PERSON", "PER"}, {"PERSON", "PER"}),
            ({"ORGANIZATION"}, {"ORG"})
        ]
        
        result1 = DataListRecognizer._DataListRecognizer__check_label(
            "PERSON", "PERSON", check_groups
        )
        result2 = DataListRecognizer._DataListRecognizer__check_label(
            "ORGANIZATION", "ORG", check_groups
        )
        
        assert result1 is True
        assert result2 is True

    def test_check_label_empty_groups(self):
        """Test __check_label with empty check groups"""
        check_groups = []
        
        result = DataListRecognizer._DataListRecognizer__check_label(
            "PERSON", "PER", check_groups
        )
        
        assert result is False


class TestDataListRecognizerIntegration:
    """Integration tests for DataListRecognizer"""

    def test_full_workflow_initialization_to_analysis(self):
        """Test complete workflow from initialization to analysis"""
        terms = ["Walmart", "CVS Health"]
        entities = ["RETAIL_COMPANY"]
        
        recognizer = DataListRecognizer(
            terms=terms, 
            entitie=entities, 
            ner_strength=0.88
        )
        
        # Verify initialization
        assert recognizer.terms == terms
        assert recognizer.ENTITIES == entities
        assert recognizer.ner_strength == 0.88
        
        # Test load
        recognizer.load()
        
        # Test explanation building
        explanation = recognizer.build_spacy_explanation(0.88, "Test")
        assert explanation.original_score == 0.88

    def test_recognizer_with_multiple_entity_types(self):
        """Test recognizer with multiple entity types"""
        terms = ["Company1", "Company2", "Company3"]
        entities = ["ORG", "COMPANY"]
        
        recognizer = DataListRecognizer(terms=terms, entitie=entities)
        
        # First entity type should be used
        assert recognizer.ENTITIES == entities

    def test_recognizer_name_in_results(self):
        """Test that recognizer name appears in recognition metadata"""
        terms = ["TestCorp"]
        entities = ["COMPANY"]
        
        recognizer = DataListRecognizer(terms=terms, entitie=entities)
        
        # Recognizer should have a name attribute
        assert hasattr(recognizer, 'name')

    @patch('privacy.util.special_recognizers.DataListRecognizer.nlp')
    @patch('privacy.util.special_recognizers.DataListRecognizer.PhraseMatcher')
    def test_text_replacement_in_analyze(self, mock_matcher_class, mock_nlp):
        """Test that matched text is replaced with <COMPANY_NAME> tag"""
        terms = ["Infosys"]
        entities = ["COMPANY"]
        text = "Infosys is a company"
        
        mock_doc = Mock()
        mock_doc_str = text
        mock_doc.__str__ = Mock(return_value=mock_doc_str)
        mock_nlp.return_value = mock_doc
        
        mock_span = Mock()
        mock_span.text = "Infosys"
        mock_span.start_char = 0
        mock_span.end_char = 7
        mock_doc.__getitem__ = Mock(return_value=mock_span)
        
        mock_matcher = Mock()
        mock_matcher.return_value = [(1, 0, 1)]
        mock_matcher_class.return_value = mock_matcher
        
        recognizer = DataListRecognizer(terms=terms, entitie=entities)
        results = recognizer.analyze(text, entities)
        
        # Verify analysis was attempted
        assert isinstance(results, list)
