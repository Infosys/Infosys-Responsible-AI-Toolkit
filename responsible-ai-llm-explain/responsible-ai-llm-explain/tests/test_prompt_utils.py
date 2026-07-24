
import pytest


class TestPromptGetPrompt:
    """Test get_prompt method for comprehensive explanation prompts."""

    def test_get_prompt_basic(self):
        """Test basic prompt generation with simple inputs."""
        from llm_explain.utility.prompt_utils import Prompt
        
        prompt = "What is AI?"
        response = "AI is artificial intelligence."
        
        template = Prompt.get_prompt(prompt, response)
        
        assert isinstance(template, str)
        assert prompt in template
        assert response in template
        assert "sentiment" in template.lower()
        assert "uncertainty" in template.lower()

    def test_get_prompt_contains_all_metrics(self):
        """Test that prompt contains all required metrics."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_prompt("Test prompt", "Test response")
        
        # Check all 7 metrics are present
        assert "1. Sentiment:" in template
        assert "2. Grammatical Mistakes:" in template
        assert "3. Uncertainty:" in template
        assert "4. Out of Vocabulary (OOV):" in template
        assert "5. Coherence:" in template
        assert "6. Relevance:" in template
        assert "7. How did you arrive at the following response" in template

    def test_get_prompt_has_json_format(self):
        """Test that prompt includes JSON format specification."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_prompt("prompt", "response")
        
        assert "JSON format" in template
        assert '"sentiment"' in template
        assert '"grammatical_mistakes"' in template
        assert '"uncertainty"' in template
        assert '"out_of_vocabulary"' in template
        assert '"coherence"' in template
        assert '"relevance"' in template
        assert '"reasoning"' in template

    def test_get_prompt_with_complex_prompt(self):
        """Test prompt generation with complex multi-line prompt."""
        from llm_explain.utility.prompt_utils import Prompt
        
        prompt = """Explain quantum computing
        in simple terms
        with examples"""
        response = "Quantum computing uses qubits..."
        
        template = Prompt.get_prompt(prompt, response)
        
        assert "Explain quantum computing" in template
        assert "in simple terms" in template

    def test_get_prompt_with_special_characters(self):
        """Test prompt with special characters."""
        from llm_explain.utility.prompt_utils import Prompt
        
        prompt = "What's the cost of $100 @ 5%?"
        response = "The cost is $105."
        
        template = Prompt.get_prompt(prompt, response)
        
        assert "$100" in template
        assert "$105" in template

    def test_get_prompt_with_unicode(self):
        """Test prompt with Unicode characters."""
        from llm_explain.utility.prompt_utils import Prompt
        
        prompt = "Translate: Hello 世界"
        response = "你好 world"
        
        template = Prompt.get_prompt(prompt, response)
        
        assert "世界" in template
        assert "你好" in template

    def test_get_prompt_includes_responsible_ai_context(self):
        """Test that prompt includes Responsible AI expert context."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_prompt("test", "response")
        
        assert "Responsible AI expert" in template
        assert "Explainable AI" in template

    def test_get_prompt_includes_scoring_instructions(self):
        """Test that prompt includes scoring instructions for metrics."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_prompt("test", "response")
        
        assert "score between" in template
        assert "explain your reasoning" in template

    def test_get_prompt_instructs_no_fabrication(self):
        """Test that prompt instructs not to fabricate information."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_prompt("test", "response")
        
        assert "Do not fabricate" in template or "helpful assistant" in template

    def test_get_prompt_requires_json_only(self):
        """Test that prompt requires JSON-only response."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_prompt("test", "response")
        
        assert "Do not provide any response other than the JSON object" in template

    def test_get_prompt_with_empty_strings(self):
        """Test prompt generation with empty strings."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_prompt("", "")
        
        assert isinstance(template, str)
        assert len(template) > 0


class TestPromptGetTokenImportancePrompt:
    """Test get_token_importance_prompt method."""

    def test_get_token_importance_prompt_basic(self):
        """Test basic token importance prompt generation."""
        from llm_explain.utility.prompt_utils import Prompt
        
        prompt = "What is machine learning?"
        
        template = Prompt.get_token_importance_prompt(prompt)
        
        assert isinstance(template, str)
        assert prompt in template
        assert "Token Importance" in template

    def test_get_token_importance_prompt_contains_task(self):
        """Test that prompt contains the task description."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_token_importance_prompt("test prompt")
        
        assert "helpful assistant" in template
        assert "Do not fabricate" in template

    def test_get_token_importance_prompt_has_json_format(self):
        """Test that prompt includes JSON format specification."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_token_importance_prompt("test")
        
        assert "JSON format" in template
        assert '"Token"' in template
        assert '"Importance Score"' in template
        assert '"Position"' in template

    def test_get_token_importance_prompt_scoring_range(self):
        """Test that prompt specifies correct scoring range."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_token_importance_prompt("test")
        
        assert "0 (low importance)" in template
        assert "1 (high importance)" in template

    def test_get_token_importance_prompt_consistency_requirement(self):
        """Test that prompt requires consistency."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_token_importance_prompt("test")
        
        assert "consistent" in template.lower()

    def test_get_token_importance_prompt_no_empty_spaces(self):
        """Test that prompt warns against empty spaces."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_token_importance_prompt("test")
        
        assert "no empty spaces" in template or "ensure" in template.lower()

    def test_get_token_importance_prompt_all_tokens(self):
        """Test that prompt requires all tokens to be analyzed."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_token_importance_prompt("test")
        
        assert "all the tokens" in template or "all tokens" in template

    def test_get_token_importance_prompt_with_complex_prompt(self):
        """Test token importance prompt with complex input."""
        from llm_explain.utility.prompt_utils import Prompt
        
        prompt = """Analyze the sentiment of this text:
        The product is amazing but expensive."""
        
        template = Prompt.get_token_importance_prompt(prompt)
        
        assert "Analyze the sentiment" in template
        assert "amazing" in template

    def test_get_token_importance_prompt_with_special_chars(self):
        """Test with special characters."""
        from llm_explain.utility.prompt_utils import Prompt
        
        prompt = "Calculate: 5 + 3 * 2 = ?"
        
        template = Prompt.get_token_importance_prompt(prompt)
        
        assert "5 + 3 * 2" in template

    def test_get_token_importance_prompt_requires_json_only(self):
        """Test that prompt requires JSON-only response."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_token_importance_prompt("test")
        
        assert "Do not provide any response other than the JSON object" in template

    def test_get_token_importance_prompt_output_format_label(self):
        """Test that output format is clearly labeled."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_token_importance_prompt("test")
        
        assert "output-format:" in template.lower() or "format:" in template.lower()

    def test_get_token_importance_prompt_with_empty_prompt(self):
        """Test with empty prompt string."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_token_importance_prompt("")
        
        assert isinstance(template, str)
        assert len(template) > 0

    def test_get_token_importance_prompt_with_unicode(self):
        """Test with Unicode characters."""
        from llm_explain.utility.prompt_utils import Prompt
        
        prompt = "翻译这个句子"
        
        template = Prompt.get_token_importance_prompt(prompt)
        
        assert "翻译这个句子" in template

    def test_get_token_importance_prompt_includes_position(self):
        """Test that prompt asks for token positions."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_token_importance_prompt("test")
        
        assert "Position" in template
        assert "index" in template.lower()

    def test_get_token_importance_prompt_comma_separated(self):
        """Test that prompt specifies comma-separated format."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_token_importance_prompt("test")
        
        assert "comma-separated" in template

    def test_get_prompt_metric_1_sentiment(self):
        """Test that metric 1 is sentiment with correct range."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_prompt("test", "response")
        
        assert "1. Sentiment:" in template
        assert "-1 (negative)" in template
        assert "0 (neutral)" in template
        assert "1 (positive)" in template

    def test_get_prompt_metric_2_grammatical_mistakes(self):
        """Test that metric 2 is grammatical mistakes."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_prompt("test", "response")
        
        assert "2. Grammatical Mistakes:" in template
        assert "0 (no mistakes)" in template
        assert "1 (more mistakes)" in template

    def test_get_prompt_metric_3_uncertainty(self):
        """Test that metric 3 is uncertainty."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_prompt("test", "response")
        
        assert "3. Uncertainty:" in template
        assert "0 (certain)" in template
        assert "1 (highly uncertain)" in template

    def test_get_prompt_metric_4_oov(self):
        """Test that metric 4 is Out of Vocabulary."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_prompt("test", "response")
        
        assert "4. Out of Vocabulary" in template
        assert "0 and 100" in template

    def test_get_prompt_metric_5_coherence(self):
        """Test that metric 5 is coherence."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_prompt("test", "response")
        
        assert "5. Coherence:" in template
        assert "0 (incoherent)" in template
        assert "1 (highly coherent)" in template

    def test_get_prompt_metric_6_relevance(self):
        """Test that metric 6 is relevance."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_prompt("test", "response")
        
        assert "6. Relevance:" in template
        assert "0 (irrelevant)" in template
        assert "1 (highly relevant)" in template

    def test_get_prompt_metric_7_reasoning(self):
        """Test that metric 7 asks for reasoning."""
        from llm_explain.utility.prompt_utils import Prompt
        
        template = Prompt.get_prompt("test", "response")
        
        assert "7. How did you arrive" in template
        assert "reasoning and steps" in template
