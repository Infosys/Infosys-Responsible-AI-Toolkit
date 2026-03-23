'''
Copyright 2024 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

"""Util that calls Google Search using the Serper.dev API."""
from llm_explain.config.logger import CustomLogger
import asyncio
import aiohttp
import os
from dotenv import load_dotenv
load_dotenv()

log = CustomLogger()

class GoogleSerperAPIWrapper():
    """Wrapper around the Serper.dev Google Search API. You can create a free API key at https://serper.dev.
    To use, you should have the environment variable ``SERPER_API_KEY`` set with your API key, or 
    pass `serper_api_key` as a named parameter to the constructor.
    """
    def __init__(self, snippet_cnt = 10) -> None:
        self.k = snippet_cnt
        self.gl = "us"
        self.hl = "en"
        self.serper_api_key = os.environ.get("SERPER_KEY", None)
        assert self.serper_api_key is not None, "Please set the SERPER_API_KEY environment variable."
        assert self.serper_api_key != '', "Please set the SERPER_API_KEY environment variable."

    async def _google_serper_search_results(self, session, search_term: str, gl: str, hl: str) -> dict:
        headers = {
            "X-API-KEY": self.serper_api_key or "",
            "Content-Type": "application/json",
        }
        params = {"q": search_term, "gl": gl, "hl": hl}
        try:
            async with session.post(
                "https://google.serper.dev/search", headers=headers, params=params, raise_for_status=True
            ) as response:
                return await response.json()
        except aiohttp.ClientError as e:
            log.error(f"HTTP request failed: {e}")
            raise
        except Exception as e:
            log.error(f"An error occurred: {e}")
            raise
    
    def _parse_results(self, results):
        snippets = []

        try:
            if results.get("answerBox"):
                answer_box = results.get("answerBox", {})
                if answer_box.get("answer"):
                    element = {"content":answer_box.get("answer"),"source":"None"}
                    return [element]
                    # snippets.append(element)
                elif answer_box.get("snippet"):
                    element = {"content":answer_box.get("snippet").replace("\n", " "),"source":"None"}
                    return [element]
                    # snippets.append(element)
                elif answer_box.get("snippetHighlighted"):
                    element = {"content":answer_box.get("snippetHighlighted"),"source":"None"}
                    return [element]
                    # snippets.append(element)
                
            if results.get("knowledgeGraph"):
                kg = results.get("knowledgeGraph", {})
                title = kg.get("title")
                entity_type = kg.get("type")
                if entity_type:
                    element = {"content":f"{title}: {entity_type}","source":"None"}
                    snippets.append(element)
                description = kg.get("description")
                if description:
                    element = {"content":description,"source":"None"}
                    snippets.append(element)
                for attribute, value in kg.get("attributes", {}).items():
                    element = {"content":f"{attribute}: {value}","source":"None"}
                    snippets.append(element)

            for result in results["organic"][: self.k]:
                if "snippet" in result:
                    element = {"content":result["snippet"],"source":result["link"]}
                    snippets.append(element)
                for attribute, value in result.get("attributes", {}).items():
                    element = {"content":f"{attribute}: {value}","source":result["link"]}
                    snippets.append(element)

            if len(snippets) == 0:
                element = {"content":"No good Google Search Result was found","source":"None"}
                return [element]
            
            # keep only the first k snippets
            snippets = snippets[:int(self.k / 2)]
        except AttributeError as e:
            if "'ClientResponseError' object has no attribute 'get'" in str(e):
                log.error("Serper API key is invalid or has expired.")
                raise Exception("Serper API key is invalid or has expired.")
            else:
                log.error(f"An error occurred while parsing results: {e}")
                raise
        except Exception as e:
            log.error(f"An error occurred while parsing results: {e}")
            raise

        return snippets
    
    async def parallel_searches(self, search_queries, gl, hl):
        async with aiohttp.ClientSession() as session:
            tasks = [self._google_serper_search_results(session, query, gl, hl) for query in search_queries]
            try:
                search_results = await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                log.error(f"An error occurred while running parallel searches: {e}")
                raise
            return search_results

    async def run(self, queries):
        """Run query through GoogleSearch and parse result."""

        try:
            results = await self.parallel_searches(queries, gl=self.gl, hl=self.hl)
        except Exception as e:
            log.error(f"An error occurred while running searches: {e}")
            raise
        snippets_list = []

        for i in range(len(results)):
            snippets_list.append(self._parse_results(results[i]))

        return snippets_list