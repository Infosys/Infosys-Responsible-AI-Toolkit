# test_service_cot.py
#
# Focused unit tests for cot() and helpers in RAG.service.cot.

import os
import sys
import types
import pytest

# Ensure src/RAG is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from RAG.service import cot as cot_mod


class DummyRetriever:
    def __init__(self, docs_with_source=True):
        self._docs_with_source = docs_with_source

    def as_retriever(self):
        return self

    def get_relevant_documents(self, query: str):
        if self._docs_with_source:
            # Document with metadata.source
            return [
                types.SimpleNamespace(
                    page_content="dummy page content",
                    metadata={"source": "dummy.pdf"},
                    dict=lambda: {
                        "page_content": "dummy page content",
                        "metadata": {"source": "dummy.pdf"},
                    },
                )
            ]
        else:
            # Document without source in metadata
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
        # Emulate RetrievalQA return structure
        return {
            "result": self._result_text,
            "source_documents": [],
        }


# ---- Helpers to patch common behavior --------------------------------------


def _patch_basic_llm_and_chain(monkeypatch, result_text: str, docs_with_source=True):
    """
    Patch:
    - select_llmtype
    - RetrievalQA.from_chain_type
    - retriever.get_relevant_documents() via DummyVectorstore
    """

    def fake_select_llmtype(llmtype):
        return "dummy-llm"

    monkeypatch.setattr(cot_mod, "select_llmtype", fake_select_llmtype)

    def fake_from_chain_type(llm, retriever, return_source_documents, chain_type_kwargs):
        # RetrievalQA.from_chain_type(..) -> DummyQAChain
        return DummyQAChain(result_text=result_text)

    monkeypatch.setattr(cot_mod.RetrievalQA, "from_chain_type", staticmethod(fake_from_chain_type))

    # We'll provide DummyVectorstore separately in each test (via FAISS.load_local or collection.find_one or cache).


# ---- Tests for helper functions -------------------------------------------


def test_get_price_details_known_model():
    # Uses real implementation, just checks we get non-zero positive pricing
    prompt_price, response_price = cot_mod.get_price_details("gpt-4o")
    assert prompt_price > 0
    assert response_price > 0


def test_get_price_details_unknown_model_raises():
    with pytest.raises(ValueError):
        cot_mod.get_price_details("unknown-model-xyz")


def test_get_token_cost_and_calculate_token_count(monkeypatch):
    # Patch tiktoken.encoding_for_model to avoid real tokenizer dependency
    class DummyEncoding:
        def encode(self, text: str):
            # Each "word" becomes one token
            return text.split()

    def fake_encoding_for_model(model_name: str):
        return DummyEncoding()

    monkeypatch.setattr(cot_mod.tiktoken, "encoding_for_model", fake_encoding_for_model)

    text = "hello world"
    token_count = cot_mod.calculate_token_count(text)
    assert token_count == 2  # "hello", "world"

    # Now test get_token_cost using a known model
    cost_info = cot_mod.get_token_cost(input_tokens=token_count, output_tokens=4, model="gpt-4o")
    assert isinstance(cost_info, dict)
    assert "total_cost" in cost_info
    assert cost_info["total_cost"] > 0


# ---- Tests for cot() branches ---------------------------------------------


def test_cot_fileupload_true_mongo_like_branch(monkeypatch):
    """
    Cover:
    - fileupload == True
    - llmtype == "openai"
    - dbtypename != "mongo" so we go through collection.find_one filter path
    - realsource == "internet" branch -> context ["Outside context/Internet"]
    """

    # Ensure we go through the "collection" path
    monkeypatch.setattr(cot_mod, "dbtypename", "not-mongo")

    dummy_vs = DummyVectorstore(docs_with_source=True)

    def fake_find_one(filter):
        # Return a document with pickled DummyVectorstore
        return {"id": filter["id"], "data": cot_mod.pickle.dumps(dummy_vs)}

    fake_collection = types.SimpleNamespace(find_one=fake_find_one)
    monkeypatch.setattr(cot_mod, "collection", fake_collection)

    # Patch LLM + RetrievalQA: last line has 'Source: "internet"'
    result_text = (
        'Result: "answer"\n'
        'Explanation: "reasoning"\n'
        'Source: "internet"'
    )
    _patch_basic_llm_and_chain(monkeypatch, result_text=result_text, docs_with_source=True)

    # Also patch tiktoken so calculate_token_count works
    class DummyEncoding:
        def encode(self, text: str):
            return text.split()

    def fake_encoding_for_model(model_name: str):
        return DummyEncoding()

    monkeypatch.setattr(cot_mod.tiktoken, "encoding_for_model", fake_encoding_for_model)

    output = cot_mod.cot(
        text="dummy question",
        fileupload=True,
        llmtype="openai",
        vectorestoreid="testid",
    )

    assert isinstance(output, dict)
    assert "cot_response" in output
    assert "timetaken" in output
    assert "source-name" in output
    assert "token_cost" in output

    # Since realsource == "internet", we expect ["Outside context/Internet"]
    assert output["source-name"] == ["Outside context/Internet"]


def test_cot_fileupload_true_faiss_branch(monkeypatch):
    """
    Cover:
    - fileupload == True
    - llmtype != "openai" -> FAISS.load_local path
    - realsource != "internet" -> unique_pdf_names branch
    """

    monkeypatch.setattr(cot_mod, "dbtypename", "not-mongo")

    class FakeFAISS:
        @staticmethod
        def load_local(path, embedding_function, allow_dangerous_deserialization=True):
            return DummyVectorstore(docs_with_source=True)

    monkeypatch.setattr(cot_mod, "FAISS", FakeFAISS)

    # Patch embedding model selection to avoid real GloVe/OpenAIEmbeddings
    def fake_select_embeddingmodel(embeddingmodel):
        return "dummy-embedding-fn"

    monkeypatch.setattr(cot_mod, "select_embeddingmodel", fake_select_embeddingmodel)

    # LLM + RetrievalQA: last line 'Source: "context-file"'
    result_text = (
        'Result: "answer"\n'
        'Explanation: "reasoning"\n'
        'Source: "dummy.pdf"'
    )
    _patch_basic_llm_and_chain(monkeypatch, result_text=result_text, docs_with_source=True)

    # tiktoken patch
    class DummyEncoding:
        def encode(self, text: str):
            return text.split()

    def fake_encoding_for_model(model_name: str):
        return DummyEncoding()

    monkeypatch.setattr(cot_mod.tiktoken, "encoding_for_model", fake_encoding_for_model)

    output = cot_mod.cot(
        text="dummy question",
        fileupload=True,
        llmtype="local-llm",
        vectorestoreid="faissid",
    )

    assert isinstance(output, dict)
    assert "cot_response" in output
    assert "source-name" in output
    # Here we expect a set of pdf names; converted to list by function's logic
    assert "dummy.pdf" in output["source-name"] or list(output["source-name"]) == ["dummy.pdf"]


def test_cot_fileupload_false_cache_branch(monkeypatch):
    """
    Cover:
    - fileupload == False branch
    - vectorestoreid truthy -> cache[int(vectorestoreid)] path
    """

    dummy_vs = DummyVectorstore(docs_with_source=True)
    fake_cache = [None, dummy_vs]
    monkeypatch.setattr(cot_mod, "cache", fake_cache)

    # Patch select_llmtype + RetrievalQA
    result_text = (
        'Result: "answer"\n'
        'Explanation: "reasoning"\n'
        'Source: "dummy.pdf"'
    )
    _patch_basic_llm_and_chain(monkeypatch, result_text=result_text, docs_with_source=True)

    # tiktoken patch
    class DummyEncoding:
        def encode(self, text: str):
            return text.split()

    def fake_encoding_for_model(model_name: str):
        return DummyEncoding()

    monkeypatch.setattr(cot_mod.tiktoken, "encoding_for_model", fake_encoding_for_model)

    output = cot_mod.cot(
        text="dummy question",
        fileupload=False,
        llmtype="openai",
        vectorestoreid="1",  # int("1") -> index 1 in cache
    )

    assert isinstance(output, dict)
    assert "cot_response" in output
    assert "source-name" in output
    assert "dummy.pdf" in output["source-name"] or list(output["source-name"]) == ["dummy.pdf"]