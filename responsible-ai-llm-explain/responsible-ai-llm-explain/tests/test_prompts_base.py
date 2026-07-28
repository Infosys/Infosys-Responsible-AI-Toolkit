import pytest


class TestPromptGetClassificationPrompt:
    """Test get_classification_prompt method."""

    def test_get_classification_prompt_basic(self):
        """Test basic classification prompt generation."""
        from llm_explain.utility.prompts.base import Prompt
        
        input_prompt = "I love this product!"
        template = Prompt.get_classification_prompt(input_prompt)
        
        assert isinstance(template, str)
        assert input_prompt in template
        assert "sentiment" in template.lower()
        assert "keywords" in template.lower()

    def test_get_classification_prompt_contains_instructions(self):
        """Test that classification prompt contains key instructions."""
        from llm_explain.utility.prompts.base import Prompt
        
        template = Prompt.get_classification_prompt("test")
        
        assert "Responsible AI expert" in template
        assert "token" in template.lower()
        assert "importance" in template.lower()

    def test_get_classification_prompt_scoring_range(self):
        """Test that scoring range is specified."""
        from llm_explain.utility.prompts.base import Prompt
        
        template = Prompt.get_classification_prompt("test")
        
        assert "1 (low importance)" in template
        assert "100 (high importance)" in template


class TestPromptGetLocalExplanationPrompt:
    """Test get_local_explanation_prompt method."""

    def test_get_local_explanation_prompt_without_context(self):
        """Test local explanation prompt without context."""
        from llm_explain.utility.prompts.base import Prompt
        
        prompt = "What is AI?"
        response = "AI is artificial intelligence."
        
        template = Prompt.get_local_explanation_prompt(prompt, response)
        
        assert prompt in template
        assert response in template
        assert "Uncertainty" in template
        assert "Coherence" in template

    def test_get_local_explanation_prompt_with_context(self):
        """Test local explanation prompt with context provided."""
        from llm_explain.utility.prompts.base import Prompt
        
        prompt = "Explain the concept"
        response = "The concept is..."
        context = "Background information about the topic"
        
        template = Prompt.get_local_explanation_prompt(prompt, response, context)
        
        assert prompt in template
        assert response in template
        assert context in template
        assert "Context:" in template

    def test_get_local_explanation_prompt_metrics(self):
        """Test that both metrics are included."""
        from llm_explain.utility.prompts.base import Prompt
        
        template = Prompt.get_local_explanation_prompt("p", "r")
        
        assert "1. Uncertainty:" in template
        assert "2. Coherence:" in template
        assert "0 (certain)" in template
        assert "95 (highly uncertain)" in template

    def test_get_local_explanation_prompt_recommendations(self):
        """Test that prompt asks for recommendations."""
        from llm_explain.utility.prompts.base import Prompt
        
        template = Prompt.get_local_explanation_prompt("p", "r")
        
        assert "recommendation" in template.lower()
        assert "concrete and actionable" in template.lower()


class TestPromptGetTokenImportancePromptBase:
    """Test get_token_importance_prompt in base module."""

    def test_get_token_importance_prompt_base(self):
        """Test token importance prompt in base module."""
        from llm_explain.utility.prompts.base import Prompt
        
        prompt = "Test prompt"
        template = Prompt.get_token_importance_prompt(prompt)
        
        assert prompt in template
        assert "Token Importance" in template
        assert "JSON format" in template


class TestPromptGetTonePredictionPrompt:
    """Test get_tone_prediction_prompt method."""

    def test_get_tone_prediction_prompt_basic(self):
        """Test basic tone prediction prompt."""
        from llm_explain.utility.prompts.base import Prompt
        
        response = "Great job! Keep up the good work."
        template = Prompt.get_tone_prediction_prompt(response)
        
        assert response in template
        assert "tone" in template.lower()

    def test_get_tone_prediction_prompt_tone_categories(self):
        """Test that all tone categories are listed."""
        from llm_explain.utility.prompts.base import Prompt
        
        template = Prompt.get_tone_prediction_prompt("test")
        
        assert "Formal:" in template
        assert "Informal:" in template
        assert "Informative:" in template
        assert "Positive:" in template
        assert "Negative:" in template
        assert "Neutral:" in template
        assert "Humorous:" in template
        assert "Dramatic:" in template
        assert "Inspiring:" in template
        assert "Persuasive:" in template
        assert "Empathetic:" in template
        assert "Authoritative:" in template

    def test_get_tone_prediction_prompt_recommendations(self):
        """Test that prompt includes recommendation requirement."""
        from llm_explain.utility.prompts.base import Prompt
        
        template = Prompt.get_tone_prediction_prompt("test")
        
        assert "recommendation" in template.lower()


class TestPromptGetCoherencePrompt:
    """Test get_coherence_prompt method (note: typo in original name)."""

    def test_get_coherence_prompt_basic(self):
        """Test basic coherence prompt."""
        from llm_explain.utility.prompts.base import Prompt
        
        response = "This is a well-structured text with clear ideas."
        template = Prompt.get_coherehce_prompt(response)  # Note: typo in original
        
        assert response in template
        assert "coherence" in template.lower()

    def test_get_coherence_prompt_scoring_scale(self):
        """Test that 1-5 scoring scale is specified."""
        from llm_explain.utility.prompts.base import Prompt
        
        template = Prompt.get_coherehce_prompt("test")
        
        assert "1-5" in template or "scale" in template.lower()
        assert "1 meaning" in template.lower()
        assert "5 meaning" in template.lower()

    def test_get_coherence_prompt_chain_of_thought(self):
        """Test that chain of thought is requested."""
        from llm_explain.utility.prompts.base import Prompt
        
        template = Prompt.get_coherehce_prompt("test")
        
        assert "step-by-step" in template.lower() or "analyze" in template.lower()


class TestPromptGetResponseRelevancePrompt:
    """Test get_response_revelance_prompt method."""

    def test_get_response_relevance_prompt_basic(self):
        """Test basic response relevance prompt."""
        from llm_explain.utility.prompts.base import Prompt
        
        prompt = "What is machine learning?"
        response = "Machine learning is a subset of AI."
        
        template = Prompt.get_response_revelance_prompt(prompt, response)
        
        assert prompt in template
        assert response in template
        assert "relevance" in template.lower() or "relevant" in template.lower()

    def test_get_response_relevance_prompt_scoring(self):
        """Test that 0-1 scoring is specified."""
        from llm_explain.utility.prompts.base import Prompt
        
        template = Prompt.get_response_revelance_prompt("p", "r")
        
        assert "0 and 1" in template or "between 0 and 1" in template
        assert "0 indicates" in template
        assert "1 indicates" in template

    def test_get_response_relevance_prompt_instructions(self):
        """Test that detailed instructions are included."""
        from llm_explain.utility.prompts.base import Prompt
        
        template = Prompt.get_response_revelance_prompt("p", "r")
        
        assert "irrelevant" in template.lower()
        assert "relevant" in template.lower()


class TestPromptIntegration:
    """Integration tests for Prompt class."""

    def test_all_prompt_methods_return_strings(self):
        """Test that all prompt methods return non-empty strings."""
        from llm_explain.utility.prompts.base import Prompt
        
        methods_to_test = [
            (Prompt.get_classification_prompt, ("test",)),
            (Prompt.get_local_explanation_prompt, ("prompt", "response")),
            (Prompt.get_token_importance_prompt, ("prompt",)),
            (Prompt.get_tone_prediction_prompt, ("response",)),
            (Prompt.get_coherehce_prompt, ("response",)),
            (Prompt.get_response_revelance_prompt, ("prompt", "response"))
        ]
        
        for method, args in methods_to_test:
            result = method(*args)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_prompts_with_multiline_inputs(self):
        """Test all prompts work with multiline inputs."""
        from llm_explain.utility.prompts.base import Prompt
        
        multiline_text = """Line 1
        Line 2
        Line 3"""
        
        result1 = Prompt.get_classification_prompt(multiline_text)
        assert "Line 1" in result1
        
        result2 = Prompt.get_local_explanation_prompt(multiline_text, "response")
        assert "Line 1" in result2

    def test_prompts_with_special_characters(self):
        """Test prompts handle special characters."""
        from llm_explain.utility.prompts.base import Prompt
        
        special_text = "Test with $pecial ch@rs & symbols!"
        
        result = Prompt.get_classification_prompt(special_text)
        assert special_text in result

    def test_local_explanation_context_branch_coverage(self):
        """Test both branches of local explanation (with and without context)."""
        from llm_explain.utility.prompts.base import Prompt
        
        # Without context
        result1 = Prompt.get_local_explanation_prompt("p", "r", None)
        assert "Context:" not in result1
        
        # With context
        result2 = Prompt.get_local_explanation_prompt("p", "r", "ctx")
        assert "Context:" in result2
        assert "ctx" in result2

    def test_prompts_require_json_output(self):
        """Test that prompts specify JSON output format."""
        from llm_explain.utility.prompts.base import Prompt
        
        prompts_to_check = [
            Prompt.get_classification_prompt("test"),
            Prompt.get_local_explanation_prompt("p", "r"),
            Prompt.get_token_importance_prompt("p"),
            Prompt.get_tone_prediction_prompt("r"),
            Prompt.get_coherehce_prompt("r"),
            Prompt.get_response_revelance_prompt("p", "r")
        ]
        
        for prompt_template in prompts_to_check:
            assert "JSON" in prompt_template or "json" in prompt_template
