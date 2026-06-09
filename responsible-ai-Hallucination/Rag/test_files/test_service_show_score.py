# test_service_show_score.py
#
# Minimal test for show_score()'s maxScore > 0.45 branch.

import os
import sys
import pytest

# Ensure src/RAG is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from RAG.service import service as svc


class FakeSim(float):
    """Float-like similarity value; arithmetic works and comparisons too."""

    def tolist(self):
        return [float(self)]


def test_show_score_high_maxscore_branch(monkeypatch):
    """
    Cover branch: elif maxScore > 0.45 -> finalScore = 0.2.
    This branch does NOT call .tolist(), so we avoid tensor issues.
    """

    def fake_promptResponseSimilarity(a, b):
        # Always high similarity so maxScore > 0.45
        return FakeSim(0.9)

    monkeypatch.setattr(svc, "promptResponseSimilarity", fake_promptResponseSimilarity)

    prompt = "prompt"
    response = "high similarity response,0.9"
    sourcearr = ["src1", "src2"]

    result = svc.show_score(prompt, response, sourcearr)
    assert isinstance(result, dict)
    assert result["score"] == 0.2