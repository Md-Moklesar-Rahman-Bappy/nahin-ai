"""Web search functionality."""

import logging
from duckduckgo_search import DDGS
from typing import List, Dict

logger = logging.getLogger(__name__)


class WebSearchActions:
    def __init__(self, ollama_client):
        self.ollama = ollama_client
        self.max_results = 5
        
    def search(self, query: str) -> str:
        if not query:
            return "কোন বিষয়ে search করতে চাও বলো নি"
            
        try:
            logger.info(f"Searching for: {query}")
            
            results = self._duckduckgo_search(query)
            
            if not results:
                return f"'{query}' এ কোন ফলাফল পাওয়া যায়নি"
                
            summary = self._summarize_results(query, results)
            return summary
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return f"Search করতে সমস্যা হয়েছে: {str(e)}"
            
    def _duckduckgo_search(self, query: str) -> List[Dict]:
        try:
            results = []
            with DDGS() as ddgs:
                for result in ddgs.news(query, max_results=self.max_results):
                    results.append({
                        "title": result.get("title", ""),
                        "body": result.get("body", ""),
                        "href": result.get("href", "")
                    })
                    
            if not results:
                with DDGS() as ddgs:
                    for result in ddgs.search(query, max_results=self.max_results):
                        results.append({
                            "title": result.get("title", ""),
                            "body": result.get("description", ""),
                            "href": result.get("href", "")
                        })
                        
            return results
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return []
            
    def _summarize_results(self, query: str, results: List[Dict]) -> str:
        context = f"User asked about: '{query}'\n\nSearch results:\n"
        for i, r in enumerate(results, 1):
            context += f"{i}. {r['title']}\n{r['body'][:200]}...\n\n"
            
        prompt = f"""Summarize these search results in Bengali for the user.
Keep it concise (2-3 sentences) and informative.

{context}

Provide a brief summary of the most relevant information."""
        
        try:
            summary = self.ollama.generate_response(prompt)
            return summary
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return f"'{query}' সম্পর্কে {len(results)} টি result পাওয়া গেছে। সাম্প্রতিক তথ্যের জন্য check করো।"
