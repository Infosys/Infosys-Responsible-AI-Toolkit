"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Steganography Detection Service
Detects various forms of text-based steganography including:
- Zero-width characters
- Whitespace manipulation
- Linguistic steganography
- Character frequency analysis
- Unicode exploitation
"""

import re
import unicodedata
from typing import Dict, List, Any
from collections import Counter
import math


class SteganographyDetectionService:
    """
    Main service class for detecting text-based steganographic attacks
    """

    def __init__(self):
        # Zero-width and invisible Unicode characters
        self.zero_width_chars = {
            "\u200B",  # Zero Width Space
            "\u200C",  # Zero Width Non-Joiner
            "\u200D",  # Zero Width Joiner
            "\u2060",  # Word Joiner
            "\uFEFF",  # Zero Width No-Break Space (BOM)
            "\u180E",  # Mongolian Vowel Separator
            "\u061C",  # Arabic Letter Mark
            "\u200E",  # Left-to-Right Mark
            "\u200F",  # Right-to-Left Mark
            "\u202A",  # Left-to-Right Embedding
            "\u202B",  # Right-to-Left Embedding
            "\u202C",  # Pop Directional Formatting
            "\u202D",  # Left-to-Right Override
            "\u202E",  # Right-to-Left Override
            "\u2061",  # Function Application
            "\u2062",  # Invisible Times
            "\u2063",  # Invisible Separator
            "\u2064",  # Invisible Plus
        }

        # Suspicious Unicode ranges
        self.suspicious_ranges = [
            (0x2000, 0x206F),  # General Punctuation
            (0xFE00, 0xFE0F),  # Variation Selectors
            (0xE0000, 0xE007F),  # Tags
        ]

    def detect_steganography(self, text: str) -> Dict[str, Any]:
        """
        Main detection method that runs all steganography detection algorithms

        Args:
            text (str): Input text to analyze

        Returns:
            Dict containing detection results and confidence scores
        """
        results = {
            "is_suspicious": False,
            "confidence_score": 0,
            "detected_techniques": [],
            "details": {},
            "recommendations": [],
        }

        # Run all detection methods
        zero_width_result = self._detect_zero_width_characters(text)
        whitespace_result = self._detect_whitespace_manipulation(text)
        linguistic_result = self._detect_linguistic_steganography(text)
        frequency_result = self._detect_frequency_anomalies(text)
        unicode_result = self._detect_unicode_exploitation(text)

        # Aggregate results
        all_results = [
            ("zero_width", zero_width_result),
            ("whitespace", whitespace_result),
            ("linguistic", linguistic_result),
            ("frequency", frequency_result),
            ("unicode", unicode_result),
        ]

        suspicious_count = 0
        total_confidence = 0

        for technique_name, result in all_results:
            results["details"][technique_name] = result
            if result["is_suspicious"]:
                suspicious_count += 1
                results["detected_techniques"].append(technique_name)
                total_confidence += result["confidence"]

        # Calculate overall confidence
        if suspicious_count > 0:
            results["is_suspicious"] = True
            results["confidence_score"] = min(100, total_confidence / len(all_results))
            results["recommendations"] = self._generate_recommendations(results["detected_techniques"])

        return results

    def _detect_zero_width_characters(self, text: str) -> Dict[str, Any]:
        """
        Detect zero-width and invisible Unicode characters
        """
        result = {
            "is_suspicious": False,
            "confidence": 0,
            "found_characters": [],
            "positions": [],
            "binary_pattern": None,
        }

        zero_width_found = []
        positions = []

        for i, char in enumerate(text):
            if char in self.zero_width_chars:
                zero_width_found.append(
                    {
                        "char": char,
                        "unicode": f"U+{ord(char):04X}",
                        "name": unicodedata.name(char, "UNKNOWN"),
                        "position": i,
                    }
                )
                positions.append(i)

        if zero_width_found:
            result["is_suspicious"] = True
            result["found_characters"] = zero_width_found
            result["positions"] = positions
            result["confidence"] = min(100, len(zero_width_found) * 20)

            # Attempt to decode binary pattern if systematic
            if len(zero_width_found) >= 8:  # Minimum for meaningful binary
                result["binary_pattern"] = self._extract_binary_pattern(zero_width_found)

        return result

    def _detect_whitespace_manipulation(self, text: str) -> Dict[str, Any]:
        """
        Detect suspicious whitespace patterns that might hide data
        """
        result = {"is_suspicious": False, "confidence": 0, "anomalies": [], "patterns": []}

        # Check for unusual whitespace patterns
        lines = text.split("\n")
        trailing_spaces = []
        unusual_spacing = []

        for line_num, line in enumerate(lines):
            # Check trailing spaces
            if line.endswith(" ") and len(line.rstrip()) < len(line):
                trailing_count = len(line) - len(line.rstrip())
                trailing_spaces.append(
                    {"line": line_num + 1, "count": trailing_count, "pattern": line[len(line.rstrip()) :]}
                )

            # Check for unusual spacing patterns
            space_sequences = re.findall(r" {2,}", line)
            if space_sequences:
                unusual_spacing.append({"line": line_num + 1, "sequences": space_sequences})

        # Check for systematic patterns
        if len(trailing_spaces) > len(lines) * 0.3:  # More than 30% of lines
            result["is_suspicious"] = True
            result["anomalies"].append("excessive_trailing_spaces")
            result["confidence"] += 30

        if unusual_spacing:
            result["is_suspicious"] = True
            result["anomalies"].append("unusual_spacing_patterns")
            result["confidence"] += 25

        result["patterns"] = {"trailing_spaces": trailing_spaces, "unusual_spacing": unusual_spacing}

        return result

    def _detect_linguistic_steganography(self, text: str) -> Dict[str, Any]:
        """
        Detect linguistic steganography patterns
        """
        result = {"is_suspicious": False, "confidence": 0, "indicators": []}

        # Check for systematic word/letter patterns
        words = re.findall(r"\b\w+\b", text.lower())
        if not words:
            return result

        # Check for systematic first letter patterns
        first_letters = [word[0] for word in words if word]
        if len(first_letters) >= 10:
            # Check for non-random distribution
            letter_freq = Counter(first_letters)
            entropy = self._calculate_entropy(list(letter_freq.values()))

            # Low entropy might indicate systematic encoding
            if entropy < 2.5:  # Arbitrary threshold
                result["is_suspicious"] = True
                result["indicators"].append("low_entropy_first_letters")
                result["confidence"] += 20

        # Check for unusual capitalization patterns
        caps_pattern = "".join(["1" if c.isupper() else "0" for c in text if c.isalpha()])
        if len(caps_pattern) >= 16:  # Minimum for pattern detection
            # Look for systematic patterns
            if self._has_systematic_pattern(caps_pattern):
                result["is_suspicious"] = True
                result["indicators"].append("systematic_capitalization")
                result["confidence"] += 30

        return result

    def _detect_frequency_anomalies(self, text: str) -> Dict[str, Any]:
        """
        Detect character frequency anomalies that might indicate steganography
        """
        result = {"is_suspicious": False, "confidence": 0, "anomalies": []}

        if len(text) < 100:  # Too short for meaningful analysis
            return result

        # Character frequency analysis
        char_freq = Counter(text)

        # Expected frequencies for English text (rough approximations)
        expected_space_freq = 0.12  # ~12% spaces in English
        expected_vowel_freq = 0.40  # ~40% vowels

        actual_space_freq = char_freq.get(" ", 0) / len(text)
        vowels = "aeiouAEIOU"
        actual_vowel_freq = sum(char_freq.get(v, 0) for v in vowels) / len(text)

        # Check for significant deviations
        if abs(actual_space_freq - expected_space_freq) > 0.05:
            result["anomalies"].append(
                {"type": "space_frequency", "expected": expected_space_freq, "actual": actual_space_freq}
            )
            result["confidence"] += 15

        if abs(actual_vowel_freq - expected_vowel_freq) > 0.10:
            result["anomalies"].append(
                {"type": "vowel_frequency", "expected": expected_vowel_freq, "actual": actual_vowel_freq}
            )
            result["confidence"] += 15

        # Check for unusual character distributions
        printable_chars = [c for c in text if c.isprintable()]
        if len(printable_chars) != len(text):
            non_printable = len(text) - len(printable_chars)
            result["anomalies"].append(
                {
                    "type": "non_printable_characters",
                    "count": non_printable,
                    "percentage": (non_printable / len(text)) * 100,
                }
            )
            result["confidence"] += 25

        if result["anomalies"]:
            result["is_suspicious"] = True

        return result

    def _detect_unicode_exploitation(self, text: str) -> Dict[str, Any]:
        """
        Detect exploitation of Unicode features for steganography
        """
        result = {"is_suspicious": False, "confidence": 0, "exploits": []}

        # Check for suspicious Unicode ranges
        for char in text:
            code_point = ord(char)
            for start, end in self.suspicious_ranges:
                if start <= code_point <= end:
                    result["exploits"].append(
                        {
                            "type": "suspicious_unicode_range",
                            "character": char,
                            "code_point": f"U+{code_point:04X}",
                            "range": f"U+{start:04X}-U+{end:04X}",
                        }
                    )

        # Check for homograph attacks (look-alike characters)
        suspicious_pairs = [
            ("a", "а"),  # Latin 'a' vs Cyrillic 'а'
            ("o", "о"),  # Latin 'o' vs Cyrillic 'о'
            ("p", "р"),  # Latin 'p' vs Cyrillic 'р'
            ("c", "с"),  # Latin 'c' vs Cyrillic 'с'
        ]

        for latin, cyrillic in suspicious_pairs:
            if latin in text and cyrillic in text:
                result["exploits"].append(
                    {
                        "type": "homograph_attack",
                        "characters": f"{latin} (U+{ord(latin):04X}) vs {cyrillic} (U+{ord(cyrillic):04X})",
                    }
                )

        if result["exploits"]:
            result["is_suspicious"] = True
            result["confidence"] = min(100, len(result["exploits"]) * 30)

        return result

    def _extract_binary_pattern(self, zero_width_chars: List[Dict]) -> str:
        """
        Attempt to extract binary pattern from zero-width characters
        """
        # Simple binary encoding: map different characters to 0s and 1s
        if len(zero_width_chars) < 2:
            return None

        char_types = list(set(char["char"] for char in zero_width_chars))
        if len(char_types) >= 2:
            # Use first two character types as binary encoding
            binary = ""
            for char_info in zero_width_chars:
                if char_info["char"] == char_types[0]:
                    binary += "0"
                elif char_info["char"] == char_types[1]:
                    binary += "1"
            return binary

        return None

    def _calculate_entropy(self, values: List[int]) -> float:
        """
        Calculate Shannon entropy of a list of values
        """
        if not values:
            return 0

        total = sum(values)
        entropy = 0
        for value in values:
            if value > 0:
                p = value / total
                entropy -= p * math.log2(p)

        return entropy

    def _has_systematic_pattern(self, pattern: str) -> bool:
        """
        Check if a binary string has systematic patterns
        """
        if len(pattern) < 16:
            return False

        # Check for repeating patterns
        for length in [2, 3, 4, 8]:
            if length * 2 <= len(pattern):
                chunk = pattern[:length]
                if pattern.startswith(chunk * (len(pattern) // length)):
                    return True

        # Check for alternating patterns
        if len(set(pattern[::2])) == 1 and len(set(pattern[1::2])) == 1:
            return True

        return False

    def _generate_recommendations(self, detected_techniques: List[str]) -> List[str]:
        """
        Generate security recommendations based on detected techniques
        """
        recommendations = []

        if "zero_width" in detected_techniques:
            recommendations.append("Remove or validate zero-width Unicode characters in input text")
            recommendations.append("Implement Unicode normalization before processing")

        if "whitespace" in detected_techniques:
            recommendations.append("Normalize whitespace patterns and remove trailing spaces")
            recommendations.append("Implement consistent spacing validation")

        if "linguistic" in detected_techniques:
            recommendations.append("Analyze text for linguistic anomalies in production systems")
            recommendations.append("Consider implementing natural language processing validation")

        if "frequency" in detected_techniques:
            recommendations.append("Monitor character frequency distributions for anomalies")
            recommendations.append("Implement statistical analysis of text patterns")

        if "unicode" in detected_techniques:
            recommendations.append("Restrict Unicode character sets to necessary ranges")
            recommendations.append("Implement homograph attack detection")

        return recommendations
