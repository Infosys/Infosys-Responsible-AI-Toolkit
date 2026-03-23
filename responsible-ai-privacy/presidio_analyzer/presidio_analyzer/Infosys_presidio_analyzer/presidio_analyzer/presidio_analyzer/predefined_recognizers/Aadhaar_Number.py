from typing import Optional, List

from presidio_analyzer import Pattern, PatternRecognizer


class Aadhaar_Number(PatternRecognizer):
    """
    Recognizes US bank number using regex.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(name="aadhaar_number_pattern", regex="[2-9]{1}[0-9]{3}\s{1}[0-9]{4}\s{1}[0-9]{4}", score=0.5),
    ]

    CONTEXT = [
        "bank"
        # Task #603: Support keyphrases: change to "checking account"
        # as part of keyphrase change
        "check",
        "account",
        "account#",
        "acct",
        "save",
        "debit",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "AADHAR_NUMBER",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
