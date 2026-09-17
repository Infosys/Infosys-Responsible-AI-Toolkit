'''
MIT License
https://mit-license.org/
Copyright © 2026 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import pytest
from src.hinglish_detect import looks_like_hinglish


# Real Hinglish/English pairs, pulled from the public findnitai/english-to-hinglish
# dataset on HuggingFace (rows 0-14 of the train split) — not invented examples.
REAL_HINGLISH_SAMPLES = [
    "film ka kya naam hai",
    "namaste, sada hua tomatoes score mahaan hai, lekin meta critic score is gunavatta kee philm se thoda kam lagata hai.",
    "kya aapako lagata hai ki aapako film pasand aaegee",
    "yah kis tarah kee philm hai",
    "film  kab banee thee?",
    "aashchary hai ki mahila, mujhe lagata hai ki mujhe is film mein bahut maja aaega",
    "yah deesee komik duniya mein sthaapit ek ekshan philm hai",
    ": film mein kaun sitaare hain",
    "Movie 2015 mein banee thee",
    "kya isane theaters mein achchha pradarshan kiya?",
    "Kya mujhe ise paane kelie any movie dekhanee hongee?",
    "Main character Gal gadot hai, lekin Chris pine, Robin wright aur Danny huston bhi hain",
    "Movie ke baare mein kya hai?",
]

# The matching English originals for the same 13 rows — must NOT be flagged.
REAL_ENGLISH_SAMPLES = [
    "What's the name of the movie",
    "Hi, the rotten tomatoes score is great but the meta critic score seems a little low a movie of this quality. ",
    "Do you think you will like the movie",
    "What kind of movie is it",
    "when was the movie made?",
    "Wonder woman, I think i would enjoy this movie very much",
    "It is a action movie set in the DC comic world",
    "Who stars in the movie",
    "the movie was made in 2015",
    "did it do well in theaters?",
    "did I have to see other movies to get it?",
    "The main character is Gal Gadot, but also stars  Chris Pine, Robin Wright and Danny Huston",
    "what is the movie about?",
]


class TestLooksLikeHinglish:
    def test_flags_real_hinglish_samples(self):
        results = [looks_like_hinglish(s) for s in REAL_HINGLISH_SAMPLES]
        true_positive_rate = sum(results) / len(results)
        # Validated against 3 independent 100-row samples of the full dataset
        # during design: ~72-87% true positive rate. This 13-row slice should
        # clear a lower bar comfortably; assert the measured minimum, not a
        # hoped-for number.
        assert true_positive_rate >= 0.7, (
            f"Only {true_positive_rate:.0%} of known-Hinglish samples flagged; "
            f"results: {list(zip(REAL_HINGLISH_SAMPLES, results))}"
        )

    def test_does_not_flag_matching_english_samples(self):
        results = [looks_like_hinglish(s) for s in REAL_ENGLISH_SAMPLES]
        false_positive_rate = sum(results) / len(results)
        # Validated at 0% false positives across 300 real rows during design.
        assert false_positive_rate == 0.0, (
            f"{false_positive_rate:.0%} of English samples wrongly flagged; "
            f"results: {list(zip(REAL_ENGLISH_SAMPLES, results))}"
        )

    def test_empty_string_not_flagged(self):
        assert looks_like_hinglish("") is False

    def test_whitespace_only_not_flagged(self):
        assert looks_like_hinglish("   ") is False

    def test_none_input_not_flagged(self):
        assert looks_like_hinglish(None) is False

    def test_single_hindi_marker_word_short_text_is_flagged(self):
        # "kya" alone is 100% of tokens, well above threshold.
        assert looks_like_hinglish("kya") is True

    def test_plain_english_sentence_not_flagged(self):
        assert looks_like_hinglish("The quick brown fox jumps over the lazy dog") is False

    def test_does_not_flag_english_words_that_look_like_hindi_markers(self):
        # Found during review: these words were previously in the marker
        # list and caused false positives on ordinary English text.
        english_homograph_samples = [
            "Open a new tab in the browser",
            "Press the tab key to indent",
            "Use the tab character as the delimiter",
            "That is a mere formality",
            "Can you hum that tune for me",
            "I keep koi fish in my pond",
        ]
        for sample in english_homograph_samples:
            assert looks_like_hinglish(sample) is False, f"False positive on: {sample!r}"

    def test_non_string_input_not_flagged(self):
        assert looks_like_hinglish(["not", "a", "string"]) is False
        assert looks_like_hinglish(12345) is False
