# test_service_defaultqa.py
#
# Focused unit tests for defaultQARetrievalKepler in RAG.service.service.
# These tests monkeypatch dependencies (collection, FAISS, gEval, scoringmetrics, cache, vectorstore)
# so we can cover the internal branches without real DB/FAISS/LLM calls.

import os
import sys
import types
import pytest

# Ensure src/RAG is on sys.path so `from RAG.service import service` works
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from RAG.service import service as svc


class DummyRetriever:
    def get_relevant_documents(self, query: str):
        return []

    def __call__(self, *args, **kwargs):
        return self

    def as_retriever(self):
        return self


class DummyVectorstore:
    def __init__(self):
        self._retriever = DummyRetriever()

    def as_retriever(self):
        return self._retriever


class DummyQAChain:
    def __init__(self, result_text: str, with_source: bool = True):
        self._result_text = result_text
        self._with_source = with_source

    def __call__(self, inputs):
        # Emulate RetrievalQA return structure
        if self._with_source:
            dummy_doc = types.SimpleNamespace(
                page_content="dummy page content",
                metadata={"source": "dummy.pdf"},
                dict=lambda: {
                    "page_content": "dummy page content",
                    "metadata": {"source": "dummy.pdf"},
                },
            )
            return {
                "result": self._result_text,
                "source_documents": [dummy_doc],
            }
        else:
            dummy_doc = types.SimpleNamespace(
                page_content="dummy page content",
                metadata={},
                dict=lambda: {
                    "page_content": "dummy page content",
                    "metadata": {},
                },
            )
            return {
                "result": self._result_text,
                "source_documents": [dummy_doc],
            }


def _patch_common(monkeypatch, avgmetrics_value, maxscore_value=0.6, with_source=True):
    """
    Common monkeypatching for scoringmetrics, gEval, select_llmtype, RetrievalQA, etc.

    avgmetrics_value: value of avgmetrics (0..5) before division by 5 inside defaultQARetrievalKepler.
                      E.g., pass 4.0 to simulate AverageScore=4.0 => avgmetrics=0.8
    maxscore_value: max(inpoutsim, ressourcescore, inpsourcesim)
    with_source: whether the result text contains 'SOURCE:' or not (so we can hit the "No source found" branch).
    """

    # 1) Fake scoringmetrics to return controlled scores and a simple res/srcArr
    def fake_scoringmetrics(text, fullText, srcArr):
        # inpoutsim, ressourcescore, inpsourcesim, tempscore, res, arrForSourceText
        inpoutsim = maxscore_value
        ressourcescore = maxscore_value
        inpsourcesim = maxscore_value
        tempscore = 1.0
        res = [{"text": "segment1", "source": "dummy.pdf"}]
        arrForSourceText = [doc.page_content for doc in srcArr]
        return inpoutsim, ressourcescore, inpsourcesim, tempscore, res, arrForSourceText

    monkeypatch.setattr(svc, "scoringmetrics", fake_scoringmetrics)

    # 2) Fake gEval to control AverageScore
    def fake_gEval(text, fullText, pagecontent, llmtype):
        return {"AverageScore": avgmetrics_value}, {}

    monkeypatch.setattr(svc, "gEval", fake_gEval)

    # 3) Fake select_llmtype to avoid real LLM
    def fake_select_llmtype(llmtype):
        return "dummy-llm"

    monkeypatch.setattr(svc, "select_llmtype", fake_select_llmtype)

    # 4) Fake RetrievalQA.from_chain_type to return a DummyQAChain
    def fake_from_chain_type(llm, retriever, return_source_documents, chain_type_kwargs):
        if with_source:
            # include SOURCE so that the "match" branch is taken
            result_text = "Answer text. SOURCE: some info,0.9"
        else:
            # no 'SOURCE:' => "No source found" branch
            result_text = "Answer text without source,0.9"
        return DummyQAChain(result_text=result_text, with_source=with_source)

    # Monkeypatch the symbol imported in service.py
    monkeypatch.setattr(svc.RetrievalQA, "from_chain_type", staticmethod(fake_from_chain_type))


def test_defaultqa_mongo_branch_high_avg(monkeypatch):
    """
    Cover:
    - Mongo collection.find_one path
    - avgmetrics >= 0.75 branch
    - avgmetrics > 0.70 so sourceName = unique_pdf_names
    """

    # Force non-mongo so we hit the "collection" path (your code already uses that when dbtypename != "mongo")
    monkeypatch.setattr(svc, "dbtypename", "not-mongo")

    # Fake collection with a stored dummy vectorstore
    dummy_vs = DummyVectorstore()

    def fake_find_one(filter):
        return {"id": filter["id"], "data": svc.pickle.dumps(dummy_vs)}

    fake_collection = types.SimpleNamespace(find_one=fake_find_one)
    monkeypatch.setattr(svc, "collection", fake_collection)

    # scoring + gEval + RetrievalQA
    # AverageScore=4.0 => avgmetrics=0.8 >= 0.75
    _patch_common(monkeypatch, avgmetrics_value=4.0, maxscore_value=0.8, with_source=True)

    result = svc.defaultQARetrievalKepler(
        text="dummy question",
        fileupload=True,
        llmtype="openai",
        embeddingmodel="local",
        vectorstoreid="testid",
    )

    assert isinstance(result, dict)
    assert "rag_response" in result
    queue = result["rag_response"]
    assert isinstance(queue[-1], dict)
    assert "Response" in queue[-1]


def test_defaultqa_faiss_branch_mid_avg(monkeypatch):
    """
    Cover:
    - Non-openai FAISS.load_local branch
    - avgmetrics in [0.5, 0.75)
    """

    monkeypatch.setattr(svc, "dbtypename", "not-mongo")

    class FakeFAISS:
        @staticmethod
        def load_local(path, embedding_function, allow_dangerous_deserialization=True):
            return DummyVectorstore()

    monkeypatch.setattr(svc, "FAISS", FakeFAISS)

    # AverageScore=3.0 -> avgmetrics=0.6 (0.5 <= x < 0.75)
    _patch_common(monkeypatch, avgmetrics_value=3.0, maxscore_value=0.6, with_source=True)

    result = svc.defaultQARetrievalKepler(
        text="dummy question",
        fileupload=True,
        llmtype="local-llm",
        embeddingmodel="local",
        vectorstoreid="faissid",
    )

    assert isinstance(result, dict)
    assert "rag_response" in result


def test_defaultqa_low_avg_outside_context(monkeypatch):
    """
    Cover:
    - avgmetrics < 0.5 branch
    - avgmetrics <= 0.70 => sourceName = ["Outside context/Internet"]
    """

    monkeypatch.setattr(svc, "dbtypename", "not-mongo")

    dummy_vs = DummyVectorstore()

    def fake_find_one(filter):
        return {"id": filter["id"], "data": svc.pickle.dumps(dummy_vs)}

    fake_collection = types.SimpleNamespace(find_one=fake_find_one)
    monkeypatch.setattr(svc, "collection", fake_collection)

    # AverageScore=1.0 => avgmetrics=0.2 < 0.5 and <=0.70
    # Keep with_source=True to avoid match2 being None
    _patch_common(monkeypatch, avgmetrics_value=1.0, maxscore_value=0.3, with_source=True)

    result = svc.defaultQARetrievalKepler(
        text="dummy question",
        fileupload=True,
        llmtype="openai",
        embeddingmodel="local",
        vectorstoreid="lowavgid",
    )

    assert isinstance(result, dict)
    assert "rag_response" in result
    queue = result["rag_response"]

    # There should be an entry with key "source-file"
    source_file_entry = next(
        (entry for entry in queue if isinstance(entry, dict) and "source-file" in entry),
        None,
    )
    assert source_file_entry is not None
    # Because avgmetrics <= 0.70, we expect ["Outside context/Internet"]
    assert source_file_entry["source-file"] == ["Outside context/Internet"]


def test_defaultqa_fileupload_false_cache_branch(monkeypatch):
    """
    Cover:
    - fileupload == False branch
    - vectorstoreid truthy => cache[int(vectorstoreid)] path
    """

    dummy_vs = DummyVectorstore()
    fake_cache = [None, dummy_vs]
    monkeypatch.setattr(svc, "cache", fake_cache)

    _patch_common(monkeypatch, avgmetrics_value=4.0, maxscore_value=0.9, with_source=True)

    result = svc.defaultQARetrievalKepler(
        text="dummy question",
        fileupload=False,
        llmtype="openai",
        embeddingmodel="local",
        vectorstoreid="1",
    )

    assert isinstance(result, dict)
    assert "rag_response" in result
    queue = result["rag_response"]
    assert isinstance(queue[-1], dict)
    assert "Response" in queue[-1]