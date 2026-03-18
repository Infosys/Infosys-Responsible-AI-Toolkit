'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import nltk
from service.service import chunk_text, CHUNK_TOKEN_LIMIT


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _token_count(text: str) -> int:
    """Return the NLTK token count for *text*."""
    return len(nltk.word_tokenize(text))


def _build_text(n_words: int) -> str:
    """Return a synthetic string containing exactly *n_words* whitespace-separated words."""
    return " ".join(f"word{i}" for i in range(n_words))


# ---------------------------------------------------------------------------
# Tests for chunk_text()
# ---------------------------------------------------------------------------

def test_short_text_returns_single_chunk():
    """Text with fewer tokens than the limit is returned as a single-element list."""
    text = _build_text(10)
    result = chunk_text(text)
    assert len(result) == 1
    assert result[0] == text


def test_text_at_exact_limit_returns_single_chunk():
    """Text whose token count equals CHUNK_TOKEN_LIMIT is not split."""
    text = _build_text(CHUNK_TOKEN_LIMIT)
    result = chunk_text(text)
    assert len(result) == 1


def test_text_exceeding_limit_is_split():
    """Text with more tokens than the limit must produce more than one chunk."""
    text = _build_text(CHUNK_TOKEN_LIMIT + 50)
    result = chunk_text(text)
    assert len(result) > 1


def test_each_chunk_respects_token_limit():
    """Every chunk returned by chunk_text() must contain at most *limit* tokens."""
    limit = 50
    text = _build_text(300)
    for chunk in chunk_text(text, limit=limit):
        assert _token_count(chunk) <= limit, (
            f"Chunk exceeds limit ({limit}): '{chunk[:60]}...'"
        )


def test_no_tokens_lost_after_chunking():
    """The total token count across all chunks must equal the original token count."""
    text = _build_text(CHUNK_TOKEN_LIMIT * 3 + 17)
    original_count = _token_count(text)
    chunks = chunk_text(text)
    reassembled_count = sum(_token_count(c) for c in chunks)
    assert reassembled_count == original_count


def test_custom_limit_is_respected():
    """Passing an explicit *limit* overrides CHUNK_TOKEN_LIMIT."""
    limit = 10
    text = _build_text(55)
    chunks = chunk_text(text, limit=limit)
    for chunk in chunks:
        assert _token_count(chunk) <= limit


def test_empty_string_returns_list_with_one_element():
    """An empty string should not raise and should return a non-empty list."""
    result = chunk_text("")
    assert isinstance(result, list)
    assert len(result) == 1


def test_original_character_bug_is_fixed():
    """Regression: the old code used len(token) (char count) for token_count
    instead of 1 per token.  For single-character tokens that bug would allow
    up to *limit* characters (not tokens) per chunk.  Verify that a text made
    entirely of single-character tokens is split correctly by token count.
    """
    limit = 5
    # Each word is a single letter — old code would allow up to 5 characters
    # and would never split (each token counts as 1 char).
    text = "a b c d e f g h i j"  # 10 single-char tokens
    chunks = chunk_text(text, limit=limit)
    # We expect the text to be split into at least 2 chunks.
    assert len(chunks) >= 2, (
        "Single-char-token text was not split — original char-count bug may still be present"
    )
    for chunk in chunks:
        assert _token_count(chunk) <= limit
