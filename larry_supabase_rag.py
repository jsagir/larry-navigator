"""
Larry Navigator - Supabase Knowledge Base Integration
Semantic search using pgvector and Gemini embeddings
"""

from supabase import create_client, Client
from google import genai
import os
from typing import List, Dict, Optional


class SupabaseKnowledgeBase:
    """
    Knowledge base retrieval using Supabase pgvector and Gemini embeddings

    Usage:
        kb = SupabaseKnowledgeBase()
        results = kb.retrieve_context("What is the PWS framework?", top_k=5)
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        google_ai_key: Optional[str] = None
    ):
        """
        Initialize the knowledge base

        Args:
            supabase_url: Supabase project URL (or set SUPABASE_URL env var)
            supabase_key: Supabase API key (or set SUPABASE_KEY env var)
            google_ai_key: Google AI API key (or set GOOGLE_AI_API_KEY env var)
        """
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        self.google_ai_key = google_ai_key or os.getenv("GOOGLE_AI_API_KEY")

        if not all([self.supabase_url, self.supabase_key, self.google_ai_key]):
            raise ValueError(
                "Missing credentials. Set SUPABASE_URL, SUPABASE_KEY, and GOOGLE_AI_API_KEY "
                "environment variables or pass them to the constructor."
            )

        # Initialize clients
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        self.gemini = genai.Client(api_key=self.google_ai_key)

    def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.5
    ) -> List[Dict[str, any]]:
        """
        Retrieve relevant chunks for a query using semantic search

        Args:
            query: User's question or search query
            top_k: Number of results to return (max: 10 recommended)
            threshold: Minimum similarity score (0.0-1.0)
                      - 0.7+: Very similar (strict, high precision)
                      - 0.5-0.7: Similar (balanced)
                      - <0.5: Loosely related (broad, high recall)

        Returns:
            List of dicts with keys: content, title, source, similarity
            Empty list if no results above threshold

        Example:
            >>> kb = SupabaseKnowledgeBase()
            >>> results = kb.retrieve_context("What is Jobs to be Done?", top_k=3)
            >>> for r in results:
            ...     print(f"{r['title']} (similarity: {r['similarity']:.3f})")
        """
        try:
            # Generate query embedding
            result = self.gemini.models.embed_content(
                model="models/text-embedding-004",
                contents=query
            )
            query_embedding = result.embeddings[0].values

            # Search Supabase using RPC function
            response = self.supabase.rpc(
                'search_knowledge_base',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': threshold,
                    'match_count': top_k
                }
            ).execute()

            # Format results
            return [
                {
                    'content': r['content'],
                    'title': r['title'] or 'Untitled',
                    'source': r['source'] or 'Unknown',
                    'similarity': r['similarity']
                }
                for r in response.data
            ]

        except Exception as e:
            print(f"Error retrieving context: {e}")
            return []

    def format_context_for_llm(
        self,
        chunks: List[Dict[str, any]],
        include_similarity: bool = False
    ) -> str:
        """
        Format retrieved chunks into a context string for LLM prompts

        Args:
            chunks: List of chunks from retrieve_context()
            include_similarity: Whether to include similarity scores

        Returns:
            Formatted context string ready for LLM prompt

        Example:
            >>> results = kb.retrieve_context(query)
            >>> context = kb.format_context_for_llm(results)
            >>> prompt = f"Context:\\n{context}\\n\\nQuestion: {query}"
        """
        if not chunks:
            return "No relevant context found in knowledge base."

        formatted = []
        for i, chunk in enumerate(chunks, 1):
            header = f"[{i}] {chunk['title']}"
            if include_similarity:
                header += f" (relevance: {chunk['similarity']:.2f})"

            formatted.append(f"{header}\n{chunk['content']}")

        return "\n\n---\n\n".join(formatted)

    def get_stats(self) -> Dict[str, any]:
        """
        Get knowledge base statistics

        Returns:
            Dict with total_chunks and other metadata
        """
        try:
            result = self.supabase.table('knowledge_base') \
                .select('*', count='exact') \
                .limit(1) \
                .execute()

            return {
                'total_chunks': result.count,
                'embedding_model': 'text-embedding-004',
                'embedding_dimensions': 768
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}


# Convenience function for quick usage
def quick_search(query: str, top_k: int = 5) -> List[Dict[str, any]]:
    """
    Quick search function - requires environment variables to be set

    Example:
        >>> from larry_supabase_rag import quick_search
        >>> results = quick_search("What is the Cynefin framework?")
    """
    kb = SupabaseKnowledgeBase()
    return kb.retrieve_context(query, top_k=top_k)


if __name__ == "__main__":
    # Test the module
    print("Testing Supabase Knowledge Base...")
    print()

    try:
        kb = SupabaseKnowledgeBase()
        stats = kb.get_stats()
        print(f"✓ Connected to knowledge base")
        print(f"✓ Total chunks: {stats.get('total_chunks', 'unknown')}")
        print()

        test_query = "What is Jobs to be Done?"
        print(f"Testing query: {test_query}")
        results = kb.retrieve_context(test_query, top_k=3)

        print(f"Found {len(results)} results:")
        for r in results:
            print(f"  - {r['title']} (similarity: {r['similarity']:.3f})")

        print()
        print("✓ Module working correctly!")

    except Exception as e:
        print(f"✗ Error: {e}")
        print()
        print("Make sure environment variables are set:")
        print("  SUPABASE_URL")
        print("  SUPABASE_KEY")
        print("  GOOGLE_AI_API_KEY")
