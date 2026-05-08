# test_service_thot.py
#
# Focused unit tests for thot() and helpers in RAG.service.thot.

import os
import sys
import types
import pytest

# Ensure src/RAG is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from RAG.service import thot as thot_mod


class DummyRetriever:
    def __init__(self, docs_with_source=True):
        self._docs_with_source = docs_with_source

    def as_retriever(self):
        return self

    def get_relevant_documents(self, query: str):
        if self._docs_with_source:
            return [
                types.SimpleNamespace(
                    page_content="dummy page content",
                    metadata={"source": "dummy_thot.pdf"},
                    dict=lambda: {
                        "page_content": "dummy page content",
                        "metadata": {"source": "dummy_thot.pdf"},
                    },
                )
            ]
        else:
            return [
                types.SimpleNamespace(
                    page_content="dummy page content",
                    metadata={},
                    dict=lambda: {
                        "page_content": "dummy page content",
                        "metadata": {},
                    },
                )
            ]


class DummyVectorstore:
    def __init__(self, docs_with_source=True):
        self._retriever = DummyRetriever(docs_with_source=docs_with_source)

    def as_retriever(self):
        return self._retriever


class DummyQAChain:
    def __init__(self, result_text: str):
        self._result_text = result_text

    def __call__(self, inputs):
        return {
            "result": self._result_text,
            "source_documents": [],
        }


def _patch_basic_llm_and_chain(monkeypatch, result_text: str):
    """Patch select_llmtype + RetrievalQA.from_chain_type for thot()."""

    def fake_select_llmtype(llmtype):
        return "dummy-llm"

    monkeypatch.setattr(thot_mod, "select_llmtype", fake_select_llmtype)

    def fake_from_chain_type(llm, retriever, return_source_documents, chain_type_kwargs):
        return DummyQAChain(result_text=result_text)

    monkeypatch.setattr(thot_mod.RetrievalQA, "from_chain_type", staticmethod(fake_from_chain_type))


# ---------------- Helper functions tests ----------------


def test_thot_get_price_details_known_model():
    prompt_price, response_price = thot_mod.get_price_details("gpt-4o")
    assert prompt_price > 0
    assert response_price > 0


def test_thot_get_price_details_unknown_model_raises():
    with pytest.raises(ValueError):
        thot_mod.get_price_details("unknown-model-for-thot")


def test_thot_get_token_cost_and_calculate_token_count(monkeypatch):
    class DummyEncoding:
        def encode(self, text: str):
            return text.split()

    def fake_encoding_for_model(model_name: str):
        return DummyEncoding()

    monkeypatch.setattr(thot_mod.tiktoken, "encoding_for_model", fake_encoding_for_model)

    text = "thread of thoughts"
    token_count = thot_mod.calculate_token_count(text)
    assert token_count == 3

    cost_info = thot_mod.get_token_cost(input_tokens=token_count, output_tokens=6, model="gpt-4o")
    assert isinstance(cost_info, dict)
    assert "total_cost" in cost_info
    assert cost_info["total_cost"] > 0


# ---------------- thot() tests ----------------


def test_thot_fileupload_true_mongo_like_branch(monkeypatch):
    """
    Cover:
    - fileupload == True
    - llmtype == "openai"
    - dbtypename != "mongo" so we go through collection.find_one path
    - realsource == "internet" -> source-name == ["Outside context/Internet"]
    """

    monkeypatch.setattr(thot_mod, "dbtypename", "not-mongo")

    dummy_vs = DummyVectorstore(docs_with_source=True)

    def fake_find_one(filter):
        return {"id": filter["id"], "data": thot_mod.pickle.dumps(dummy_vs)}

    fake_collection = types.SimpleNamespace(find_one=fake_find_one)
    monkeypatch.setattr(thot_mod, "collection", fake_collection)

    result_text = (
        'Result: "answer"\n'
        'Explanation: "reasoning"\n'
        'Source: "internet"'
    )
    _patch_basic_llm_and_chain(monkeypatch, result_text=result_text)

    class DummyEncoding:
        def encode(self, text: str):
            return text.split()

    def fake_encoding_for_model(model_name: str):
        return DummyEncoding()

    monkeypatch.setattr(thot_mod.tiktoken, "encoding_for_model", fake_encoding_for_model)

    output = thot_mod.thot(
        text="dummy thot question",
        fileupload=True,
        llmtype="openai",
        vectorestoreid="testid",
    )

    assert isinstance(output, dict)
    assert "thot_response" in output
    assert "timetaken" in output
    assert "source-name" in output
    assert "token_cost" in output
    assert output["source-name"] == ["Outside context/Internet"]


def test_thot_fileupload_true_faiss_branch(monkeypatch):
    """
    Cover:
    - fileupload == True
    - llmtype != "openai" -> FAISS.load_local path
    - realsource != "internet" -> unique_pdf_names branch
    """

    monkeypatch.setattr(thot_mod, "dbtypename", "not-mongo")

    class FakeFAISS:
        @staticmethod
        def load_local(path, embedding_function, allow_dangerous_deserialization=True):
            return DummyVectorstore(docs_with_source=True)

    monkeypatch.setattr(thot_mod, "FAISS", FakeFAISS)

    def fake_select_embeddingmodel(embeddingmodel):
        return "dummy-embedding"

    monkeypatch.setattr(thot_mod, "select_embeddingmodel", fake_select_embeddingmodel)

    result_text = (
        'Result: "answer"\n'
        'Explanation: "reasoning"\n'
        'Source: "dummy_thot.pdf"'
    )
    _patch_basic_llm_and_chain(monkeypatch, result_text=result_text)

    class DummyEncoding:
        def encode(self, text: str):
            return text.split()

    def fake_encoding_for_model(model_name: str):
        return DummyEncoding()

    monkeypatch.setattr(thot_mod.tiktoken, "encoding_for_model", fake_encoding_for_model)

    output = thot_mod.thot(
        text="dummy thot question",
        fileupload=True,
        llmtype="local-thot-llm",
        vectorestoreid="faissid",
    )

    assert isinstance(output, dict)
    assert "thot_response" in output
    assert "source-name" in output
    assert "dummy_thot.pdf" in output["source-name"] or list(output["source-name"]) == ["dummy_thot.pdf"]


def test_thot_fileupload_false_cache_branch(monkeypatch):
    """
    Cover:
    - fileupload == False
    - vectorestoreid truthy -> cache[int(vectorestoreid)] path
    """

    dummy_vs = DummyVectorstore(docs_with_source=True)
    fake_cache = [None, dummy_vs]
    monkeypatch.setattr(thot_mod, "cache", fake_cache)

    result_text = (
        'Result: "answer"\n'
        'Explanation: "reasoning"\n'
        'Source: "dummy_thot.pdf"'
    )
    _patch_basic_llm_and_chain(monkeypatch, result_text=result_text)

    class DummyEncoding:
        def encode(self, text: str):
            return text.split()

    def fake_encoding_for_model(model_name: str):
        return DummyEncoding()

    monkeypatch.setattr(thot_mod.tiktoken, "encoding_for_model", fake_encoding_for_model)

    output = thot_mod.thot(
        text="dummy thot question",
        fileupload=False,
        llmtype="openai",
        vectorestoreid="1",  # int("1") -> index 1 in cache
    )

    assert isinstance(output, dict)
    assert "thot_response" in output
    assert "source-name" in output
    assert "dummy_thot.pdf" in output["source-name"] or list(output["source-name"]) == ["dummy_thot.pdf"]