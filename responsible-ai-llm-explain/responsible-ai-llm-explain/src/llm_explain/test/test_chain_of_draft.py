import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from llm_explain.utility.chain_of_draft import ChainOfDraft


class TestChainOfDraft(unittest.TestCase):    
    def setUp(self):
        self.max_words = ChainOfDraft.MAX_WORDS_PER_STEP
        self.test_query = "What are the steps to solve a complex problem?"
        self.test_reasoning = "First, we need to understand the problem deeply. Then, we break it down into smaller parts. Next, we identify the key components. After that, we develop a solution strategy. Finally, we implement and verify the solution."
    
    def test_count_words_basic(self):
        text = "Hello world test"
        word_count = ChainOfDraft.count_words(text)
        self.assertEqual(word_count, 3)
    
    def test_count_words_with_extra_spaces(self):
        text = "  Hello   world   test  "
        word_count = ChainOfDraft.count_words(text)
        self.assertEqual(word_count, 3)
    
    def test_count_words_empty_string(self):
        text = ""
        word_count = ChainOfDraft.count_words(text)
        self.assertEqual(word_count, 0)
    
    def test_count_words_single_word(self):
        text = "Hello"
        word_count = ChainOfDraft.count_words(text)
        self.assertEqual(word_count, 1)
    
    def test_truncate_to_word_limit_basic(self):
        text = "This is a test sentence with many words"
        truncated = ChainOfDraft.truncate_to_word_limit(text, max_words=5)
        word_count = ChainOfDraft.count_words(truncated)
        self.assertEqual(word_count, 5)
        self.assertEqual(truncated, "This is a test sentence")
    
    def test_truncate_to_word_limit_within_limit(self):
        text = "This is short"
        truncated = ChainOfDraft.truncate_to_word_limit(text, max_words=5)
        self.assertEqual(truncated, "This is short")
    
    def test_truncate_to_word_limit_default_max(self):
        text = "One Two Three Four Five Six Seven"
        truncated = ChainOfDraft.truncate_to_word_limit(text)
        word_count = ChainOfDraft.count_words(truncated)
        self.assertLessEqual(word_count, self.max_words)
    
    def test_generate_deterministic_hash(self):
        text = "Test text for hashing"
        hash1 = ChainOfDraft.generate_deterministic_hash(text)
        hash2 = ChainOfDraft.generate_deterministic_hash(text)
        self.assertEqual(hash1, hash2)
    
    def test_generate_deterministic_hash_different_input(self):
        hash1 = ChainOfDraft.generate_deterministic_hash("Text 1")
        hash2 = ChainOfDraft.generate_deterministic_hash("Text 2")
        self.assertNotEqual(hash1, hash2)
    
    def test_generate_deterministic_hash_length(self):
        text = "Test"
        hash_val = ChainOfDraft.generate_deterministic_hash(text)
        self.assertEqual(len(hash_val), 16)
    
    def test_validate_step_valid(self):
        step = "Understand problem deeply"
        is_valid = ChainOfDraft.validate_step(step)
        self.assertTrue(is_valid)
    
    def test_validate_step_invalid_too_long(self):
        step = "This is a very long step that exceeds the limit"
        is_valid = ChainOfDraft.validate_step(step)
        self.assertFalse(is_valid)
    
    def test_validate_step_empty_string(self):
        step = ""
        is_valid = ChainOfDraft.validate_step(step)
        self.assertFalse(is_valid)
    
    def test_validate_step_only_spaces(self):
        step = "   "
        is_valid = ChainOfDraft.validate_step(step)
        self.assertFalse(is_valid)
    
    def test_validate_step_none(self):
        step = None
        is_valid = ChainOfDraft.validate_step(step)
        self.assertFalse(is_valid)
    
    def test_validate_step_exactly_max_words(self):
        step = "One Two Three Four Five"  # Exactly 5 words
        is_valid = ChainOfDraft.validate_step(step)
        self.assertTrue(is_valid)
    
    def test_split_reasoning_into_steps_basic(self):
        steps = ChainOfDraft.split_reasoning_into_steps(self.test_reasoning, max_steps=10)
        self.assertGreater(len(steps), 0)
        # Each step should have max 5 words
        for step in steps:
            word_count = ChainOfDraft.count_words(step)
            self.assertLessEqual(word_count, self.max_words)
    
    def test_split_reasoning_into_steps_respects_max_steps(self):
        steps = ChainOfDraft.split_reasoning_into_steps(self.test_reasoning, max_steps=3)
        self.assertLessEqual(len(steps), 3)
    
    def test_split_reasoning_into_steps_empty_text(self):
        steps = ChainOfDraft.split_reasoning_into_steps("", max_steps=10)
        self.assertEqual(len(steps), 0)
    
    def test_split_reasoning_into_steps_single_sentence(self):
        text = "Understand the problem first"
        steps = ChainOfDraft.split_reasoning_into_steps(text, max_steps=10)
        self.assertGreater(len(steps), 0)
    
    def test_ensure_consistency(self):
        steps = ["Analyze problem", "Break down parts", "Develop solution"]
        consistency = ChainOfDraft.ensure_consistency(self.test_query, steps)
        self.assertIn("input_hash", consistency)
        self.assertIn("steps_hash", consistency)
        self.assertIn("step_count", consistency)
        self.assertIn("is_deterministic", consistency)
        self.assertIn("consistency_level", consistency)
        self.assertEqual(consistency["step_count"], 3)
        self.assertTrue(consistency["is_deterministic"])
    
    def test_ensure_consistency_empty_steps(self):
        consistency = ChainOfDraft.ensure_consistency(self.test_query, [])
        self.assertEqual(consistency["consistency_level"], "Low")
    
    def test_generate_chain_of_draft_basic(self):
        response = ChainOfDraft.generate_chain_of_draft(
            self.test_query,
            self.test_reasoning,
            max_steps=10
        )
        
        self.assertIn("query", response)
        self.assertIn("steps", response)
        self.assertIn("step_count", response)
        self.assertIn("consistency_metadata", response)
        self.assertEqual(response["query"], self.test_query)
        self.assertGreater(response["step_count"], 0)
    
    def test_generate_chain_of_draft_step_validation(self):
        response = ChainOfDraft.generate_chain_of_draft(
            self.test_query,
            self.test_reasoning,
            max_steps=10
        )
        
        for step in response["steps"]:
            self.assertIn("step_number", step)
            self.assertIn("reasoning", step)
            self.assertIn("word_count", step)
            self.assertIn("is_valid", step)
            self.assertLessEqual(step["word_count"], self.max_words)
            self.assertTrue(step["is_valid"])
    
    def test_generate_chain_of_draft_deterministic(self):
        response1 = ChainOfDraft.generate_chain_of_draft(
            self.test_query,
            self.test_reasoning,
            max_steps=10
        )
        response2 = ChainOfDraft.generate_chain_of_draft(
            self.test_query,
            self.test_reasoning,
            max_steps=10
        )
        
        # Same inputs should produce same outputs
        self.assertEqual(response1["step_count"], response2["step_count"])
        self.assertEqual(
            response1["consistency_metadata"]["input_hash"],
            response2["consistency_metadata"]["input_hash"]
        )
    
    def test_generate_chain_of_draft_empty_reasoning(self):
        response = ChainOfDraft.generate_chain_of_draft(
            self.test_query,
            "",
            max_steps=10
        )
        
        self.assertEqual(response["step_count"], 0)
    
    def test_generate_chain_of_draft_max_steps_limit(self):
        response = ChainOfDraft.generate_chain_of_draft(
            self.test_query,
            self.test_reasoning,
            max_steps=3
        )
        
        self.assertLessEqual(response["step_count"], 3)
    
    def test_word_count_consistency(self):
        text = "Test one two three"
        count1 = ChainOfDraft.count_words(text)
        count2 = len(text.split())
        self.assertEqual(count1, count2)
    
    def test_complex_reasoning_processing(self):
        complex_reasoning = (
            "First identify requirements. Then analyze constraints carefully. "
            "Next design solution architecture. After implement components. "
            "Finally test and verify everything. Document all findings."
        )
        steps = ChainOfDraft.split_reasoning_into_steps(complex_reasoning, max_steps=10)
        
        for step in steps:
            word_count = ChainOfDraft.count_words(step)
            self.assertLessEqual(word_count, self.max_words)


class TestChainOfDraftEdgeCases(unittest.TestCase):    
    def test_unicode_text_handling(self):
        text = "Hello 😗"
        word_count = ChainOfDraft.count_words(text)
        self.assertGreater(word_count, 0)
    
    def test_special_characters_in_text(self):
        text = "Test! With? Punctuation, marks."
        steps = ChainOfDraft.split_reasoning_into_steps(text, max_steps=10)
        self.assertGreater(len(steps), 0)
    
    def test_very_long_single_word(self):
        text = "Supercalifragilisticexpialidocious"
        truncated = ChainOfDraft.truncate_to_word_limit(text, max_words=5)
        # Single word should remain unchanged
        self.assertEqual(truncated, text)
    
    def test_numbers_in_text(self):
        text = "Step 1 involves 3 parts"
        word_count = ChainOfDraft.count_words(text)
        self.assertEqual(word_count, 5)


if __name__ == '__main__':
    unittest.main()
