from llm_explain.config.logger import CustomLogger
import hashlib
import json
import re

log = CustomLogger()

class ChainOfDraft:
    MAX_WORDS_PER_STEP = 5 # Maximum number of words allowed per reasoning step.
    @staticmethod
    def count_words(text: str):
        try:
            words = text.strip().split()
            return len(words)
        except Exception as e:
            log.error(f"Error counting words: {e}", exc_info=True)
            return 0
    
    @staticmethod
    def truncate_to_word_limit(text: str, max_words: int = MAX_WORDS_PER_STEP):
        try:
            words = text.strip().split()
            if len(words) <= max_words:
                return text.strip()
            
            truncated = ' '.join(words[:max_words])
            return truncated
        except Exception as e:
            log.error(f"Error truncating text: {e}", exc_info=True)
            return text
    
    @staticmethod
    def generate_deterministic_hash(text: str):
        try:
            hash_object = hashlib.sha256(text.encode())
            return hash_object.hexdigest()[:16]
        except Exception as e:
            log.error(f"Error generating hash: {e}", exc_info=True)
            return ""
    
    @staticmethod
    def validate_step(step: str):
        try:
            if not step or not isinstance(step, str):
                return False
            
            # Check if step is not empty and has reasonable length
            stripped_step = step.strip()
            if not stripped_step:
                return False
            
            # Check word count
            word_count = ChainOfDraft.count_words(stripped_step)
            if word_count == 0 or word_count > ChainOfDraft.MAX_WORDS_PER_STEP:
                return False
            
            return True
        except Exception as e:
            log.error(f"Error validating step: {e}", exc_info=True)
            return False
    
    @staticmethod
    def split_reasoning_into_steps(reasoning: str, max_steps: int = 10):
        try:
            steps = []
            sentences = re.split(r'[.!?]+', reasoning)
            for sentence in sentences:
                if len(steps) >= max_steps:
                    break                
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                truncated = ChainOfDraft.truncate_to_word_limit(sentence)
                
                if ChainOfDraft.validate_step(truncated):
                    steps.append(truncated)
            
            return steps
        except Exception as e:
            log.error(f"Error splitting reasoning into steps: {e}", exc_info=True)
            return []
    
    @staticmethod
    def ensure_consistency(input_text: str, steps: list) -> dict:
        try:
            input_hash = ChainOfDraft.generate_deterministic_hash(input_text)
            steps_hash = ChainOfDraft.generate_deterministic_hash(json.dumps(steps))
            
            consistency_metadata = {
                "input_hash": input_hash,
                "steps_hash": steps_hash,
                "step_count": len(steps),
                "is_deterministic": True,
                "consistency_level": "High" if len(steps) > 0 else "Low"
            }
            
            return consistency_metadata
        except Exception as e:
            log.error(f"Error ensuring consistency: {e}", exc_info=True)
            return {}
    
    @staticmethod
    def generate_chain_of_draft(query: str, reasoning_text: str, max_steps: int = 10) -> dict:
        try:
            # Split reasoning into steps
            steps = ChainOfDraft.split_reasoning_into_steps(reasoning_text, max_steps)            
            if not steps:
                log.warning("No valid steps generated from reasoning text")
                return {
                    "query": query,
                    "steps": [],
                    "step_count": 0,
                    "consistency_metadata": {},
                    "error": "Unable to generate valid reasoning steps"
                }
            
            # Ensure consistency
            consistency_metadata = ChainOfDraft.ensure_consistency(query, steps)
            
            # Build detailed step information, Kadavilea Ajithey
            detailed_steps = []
            for idx, step in enumerate(steps, 1):
                detailed_steps.append({
                    "step_number": idx,
                    "reasoning": step,
                    "word_count": ChainOfDraft.count_words(step),
                    "is_valid": ChainOfDraft.validate_step(step)
                })
            
            response = {
                "query": query,
                "steps": detailed_steps,
                "step_count": len(detailed_steps),
                "consistency_metadata": consistency_metadata,
                "summary": "Chain of Draft reasoning completed successfully"
            }
            
            return response
        except Exception as e:
            log.error(f"Error generating Chain of Draft: {e}", exc_info=True)
            return {
                "query": query,
                "steps": [],
                "step_count": 0,
                "consistency_metadata": {},
                "error": str(e)
            }
