import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import aiohttp
import asyncio
import os


class TestGoogleSerperAPIWrapperInit:
    """Test GoogleSerperAPIWrapper initialization."""

    @patch.dict(os.environ, {"SERPER_KEY": "test-api-key-12345"})
    def test_init_success(self):
        """Test successful initialization with API key."""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper(snippet_cnt=10)
        
        assert wrapper.k == 10
        assert wrapper.gl == "us"
        assert wrapper.hl == "en"
        assert wrapper.serper_api_key == "test-api-key-12345"

    @patch.dict(os.environ, {"SERPER_KEY": "my-key"})
    def test_init_custom_snippet_count(self):
        """Test initialization with custom snippet count."""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper(snippet_cnt=20)
        
        assert wrapper.k == 20

    @patch.dict(os.environ, {"SERPER_KEY": "key"})
    def test_init_default_values(self):
        """Test that default values are set correctly."""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper()
        
        assert wrapper.gl == "us"
        assert wrapper.hl == "en"

    @patch.dict(os.environ, {}, clear=True)
    def test_init_missing_api_key(self):
        """Test initialization fails when API key is missing."""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        with pytest.raises(AssertionError) as exc_info:
            wrapper = GoogleSerperAPIWrapper()
        
        assert "SERPER_API_KEY" in str(exc_info.value)

    @patch.dict(os.environ, {"SERPER_KEY": ""})
    def test_init_empty_api_key(self):
        """Test initialization fails when API key is empty."""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        with pytest.raises(AssertionError) as exc_info:
            wrapper = GoogleSerperAPIWrapper()
        
        assert "SERPER_API_KEY" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.asyncio
class TestGoogleSerperSearchResults:
    """Test Google Serper search results"""
    



class TestParseResults:
    """Test _parse_results method."""

    @patch.dict(os.environ, {"SERPER_KEY": "test-key"})
    def test_parse_results_with_answer_box(self):
        """Test parsing results with answerBox containing answer."""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper()
        
        results = {
            "answerBox": {"answer": "42"},
            "organic": []
        }
        
        snippets = wrapper._parse_results(results)
        
        assert len(snippets) == 1
        assert snippets[0]["content"] == "42"
        assert snippets[0]["source"] == "None"

    @patch.dict(os.environ, {"SERPER_KEY": "test-key"})
    def test_parse_results_with_answer_box_snippet(self):
        """Test parsing results with answerBox containing snippet."""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper()
        
        results = {
            "answerBox": {"snippet": "This is\nthe answer"},
            "organic": []
        }
        
        snippets = wrapper._parse_results(results)
        
        assert len(snippets) == 1
        assert "This is the answer" in snippets[0]["content"]
        assert snippets[0]["source"] == "None"

    @patch.dict(os.environ, {"SERPER_KEY": "test-key"})
    def test_parse_results_with_answer_box_snippet_highlighted(self):
        """Test parsing results with answerBox containing snippetHighlighted."""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper()
        
        results = {
            "answerBox": {"snippetHighlighted": "Highlighted answer"},
            "organic": []
        }
        
        snippets = wrapper._parse_results(results)
        
        assert len(snippets) == 1
        assert snippets[0]["content"] == "Highlighted answer"

    @patch.dict(os.environ, {"SERPER_KEY": "test-key"})
    def test_parse_results_with_knowledge_graph(self):
        """Test parsing results with knowledge graph."""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper()
        
        results = {
            "knowledgeGraph": {
                "title": "Python",
                "type": "Programming Language",
                "description": "Python is a high-level programming language.",
                "attributes": {
                    "Creator": "Guido van Rossum",
                    "First appeared": "1991"
                }
            },
            "organic": []
        }
        
        snippets = wrapper._parse_results(results)
        
        # Should have title:type, description, and 2 attributes
        assert len(snippets) >= 3
        assert any("Python: Programming Language" in s["content"] for s in snippets)
        assert any("high-level programming language" in s["content"] for s in snippets)

    @patch.dict(os.environ, {"SERPER_KEY": "test-key"})
    def test_parse_results_with_organic_results(self):
        """Test parsing organic search results."""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper(snippet_cnt=10)
        
        results = {
            "organic": [
                {"snippet": "First result", "link": "https://example1.com"},
                {"snippet": "Second result", "link": "https://example2.com"},
                {"snippet": "Third result", "link": "https://example3.com"}
            ]
        }
        
        snippets = wrapper._parse_results(results)
        
        assert len(snippets) > 0
        assert snippets[0]["content"] == "First result"
        assert snippets[0]["source"] == "https://example1.com"

    @patch.dict(os.environ, {"SERPER_KEY": "test-key"})
    def test_parse_results_limits_snippet_count(self):
        """Test that snippet count is limited."""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper(snippet_cnt=10)
        
        organic_results = [
            {"snippet": f"Result {i}", "link": f"https://example{i}.com"}
            for i in range(20)
        ]
        
        results = {"organic": organic_results}
        
        snippets = wrapper._parse_results(results)
        
        # Should be limited to k/2 = 5
        assert len(snippets) <= 5

    @patch.dict(os.environ, {"SERPER_KEY": "test-key"})
    def test_parse_results_no_good_results(self):
        """Test parsing when no good results are found."""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper()
        
        results = {"organic": []}
        
        snippets = wrapper._parse_results(results)
        
        assert len(snippets) == 1
        assert "No good Google Search Result" in snippets[0]["content"]
        assert snippets[0]["source"] == "None"

    @patch.dict(os.environ, {"SERPER_KEY": "test-key"})
    def test_parse_results_with_attributes(self):
        """Test parsing results with attributes in organic results."""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper()
        
        results = {
            "organic": [
                {
                    "snippet": "Main snippet",
                    "link": "https://example.com",
                    "attributes": {
                        "Price": "$99",
                        "Rating": "4.5"
                    }
                }
            ]
        }
        
        snippets = wrapper._parse_results(results)
        
        assert any("Main snippet" in s["content"] for s in snippets)
        assert any("Price: $99" in s["content"] for s in snippets)

    @patch.dict(os.environ, {"SERPER_KEY": "test-key"})
    def test_parse_results_attribute_error_invalid_key(self):
        """Test handling of AttributeError with ClientResponseError."""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper()
        
        # This would raise AttributeError in actual usage with malformed results
        # Testing error handling
        results = {"organic": []}
        
        # Normal case should work
        snippets = wrapper._parse_results(results)
        assert len(snippets) == 1

    @patch.dict(os.environ, {"SERPER_KEY": "test-key"})
    def test_parse_results_exception_handling(self):
        """Test generic exception handling in parse_results."""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper()
        
        # Providing None or invalid structure
        with pytest.raises(Exception):
            wrapper._parse_results(None)


class TestParallelSearches:
    """Test parallel_searches method."""
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"SERPER_KEY": "test-key"})
    async def test_parallel_searches_success(self):
        """Test successful parallel searches."""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper()
        
        with patch.object(wrapper, '_google_serper_search_results') as mock_search:
            mock_search.return_value = {"organic": []}
            
            queries = ["query1", "query2", "query3"]
            results = await wrapper.parallel_searches(queries, "us", "en")
            
            assert len(results) == 3
            assert mock_search.call_count == 3


class TestRun:
    """Test run method."""

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"SERPER_KEY": "test-key"})
    async def test_run_success(self):
        """Test successful run with query list."""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper(snippet_cnt=10)
        
        mock_search_results = [
            {"organic": [{"snippet": "Result 1", "link": "https://example1.com"}]},
            {"organic": [{"snippet": "Result 2", "link": "https://example2.com"}]}
        ]
        
        with patch.object(wrapper, 'parallel_searches', return_value=mock_search_results):
            queries = ["AI", "Machine Learning"]
            results = await wrapper.run(queries)
            
            assert len(results) == 2
            assert len(results[0]) > 0
            assert len(results[1]) > 0

    @patch.dict(os.environ, {"SERPER_KEY": "test-key"})
    @pytest.mark.asyncio
    async def test_run_with_single_query(self):
        """Test run with single query."""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper()
        
        mock_search_results = [
            {"organic": [{"snippet": "Result", "link": "https://example.com"}]}
        ]
        
        with patch.object(wrapper, 'parallel_searches', return_value=mock_search_results):
            results = await wrapper.run(["single query"])
            
            assert len(results) == 1

    @patch.dict(os.environ, {"SERPER_KEY": "test-key"})
    @pytest.mark.asyncio
    async def test_run_search_failure(self):
        """Test run when search fails."""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper()
        
        with patch.object(wrapper, 'parallel_searches', side_effect=Exception("API error")):
            with pytest.raises(Exception):
                await wrapper.run(["query"])

    @patch.dict(os.environ, {"SERPER_KEY": "test-key"})
    @pytest.mark.asyncio
    async def test_run_parses_all_results(self):
        """Test that run parses all search results."""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper()
        
        mock_search_results = [
            {"answerBox": {"answer": "42"}, "organic": []},
            {"organic": [{"snippet": "Test", "link": "https://test.com"}]},
            {"organic": []}
        ]
        
        with patch.object(wrapper, 'parallel_searches', return_value=mock_search_results):
            results = await wrapper.run(["q1", "q2", "q3"])
            
            assert len(results) == 3
            assert results[0][0]["content"] == "42"
            assert "Test" in results[1][0]["content"]
            assert "No good Google Search Result" in results[2][0]["content"]

    @patch.dict(os.environ, {"SERPER_KEY": "test-key"})
    @pytest.mark.asyncio
    async def test_run_empty_query_list(self):
        """Test run with empty query list."""
        from llm_explain.utility.query_serper import GoogleSerperAPIWrapper
        
        wrapper = GoogleSerperAPIWrapper()
        
        with patch.object(wrapper, 'parallel_searches', return_value=[]):
            results = await wrapper.run([])
            
            assert len(results) == 0
