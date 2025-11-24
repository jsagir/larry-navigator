"""
Tavily Web Search Client for Larry Navigator v2.0
"""

import os
from typing import List, Dict, Any, Optional
from tavily import TavilyClient


class LarryTavilyClient:
    """Wrapper around Tavily API for web research"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Tavily client

        Args:
            api_key: Tavily API key (if None, reads from TAVILY_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not found in environment or provided")

        self.client = TavilyClient(api_key=self.api_key)

    def search(
        self,
        query: str,
        search_depth: str = "advanced",
        max_results: int = 5,
        include_answer: bool = True,
        include_images: bool = False,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Execute a Tavily search

        Args:
            query: Search query
            search_depth: "basic" or "advanced"
            max_results: Maximum number of results (default 5)
            include_answer: Include AI-generated answer summary
            include_images: Include image results
            include_domains: Only search these domains
            exclude_domains: Exclude these domains

        Returns:
            {
                "answer": "AI summary...",
                "query": "original query",
                "results": [
                    {
                        "title": "...",
                        "url": "...",
                        "content": "...",
                        "score": 0.95
                    }
                ],
                "images": [...] (if include_images=True)
            }
        """
        try:
            response = self.client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_answer=include_answer,
                include_images=include_images,
                include_domains=include_domains,
                exclude_domains=exclude_domains
            )
            return response

        except Exception as e:
            print(f"❌ Tavily search error: {e}")
            return {
                "query": query,
                "answer": None,
                "results": [],
                "error": str(e)
            }

    def format_results_for_display(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format Tavily results for UI display

        Args:
            results: Raw Tavily results

        Returns:
            Formatted results with display-friendly fields
        """
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append({
                "number": i,
                "title": result.get("title", "Untitled"),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "score": result.get("score", 0.0),
                "score_percent": int(result.get("score", 0.0) * 100)
            })
        return formatted

    def search_multiple_queries(
        self,
        queries: List[str],
        search_depth: str = "advanced",
        max_results_per_query: int = 3
    ) -> Dict[str, Any]:
        """Execute multiple search queries and aggregate results

        Args:
            queries: List of search queries
            search_depth: "basic" or "advanced"
            max_results_per_query: Max results per individual query

        Returns:
            {
                "queries": ["query1", "query2"],
                "all_results": [...],  # All results combined
                "by_query": {
                    "query1": [...],
                    "query2": [...]
                }
            }
        """
        all_results = []
        by_query = {}

        for query in queries:
            response = self.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results_per_query,
                include_answer=False
            )

            query_results = response.get("results", [])
            by_query[query] = query_results
            all_results.extend(query_results)

        # Deduplicate by URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)

        # Sort by score
        unique_results.sort(key=lambda x: x.get("score", 0.0), reverse=True)

        return {
            "queries": queries,
            "all_results": unique_results,
            "by_query": by_query,
            "total_unique_results": len(unique_results)
        }


def is_tavily_configured() -> bool:
    """Check if Tavily is properly configured"""
    return bool(os.getenv("TAVILY_API_KEY"))


def get_tavily_client() -> Optional[LarryTavilyClient]:
    """Get Tavily client if configured, else None"""
    try:
        if is_tavily_configured():
            return LarryTavilyClient()
        return None
    except Exception as e:
        print(f"⚠️ Could not initialize Tavily client: {e}")
        return None
