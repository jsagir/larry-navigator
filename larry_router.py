"""
Intelligent Query Router for Larry Navigator
Routes queries to the appropriate tool: Gemini File Search (default), Neo4j, or Web Search
"""

import re
from typing import Literal

QueryRoute = Literal["file_search", "neo4j", "web_search"]


def route_query(user_message: str) -> QueryRoute:
    """
    Intelligently routes a user query to the appropriate tool.
    
    Args:
        user_message: The user's input message
        
    Returns:
        "file_search" (default), "neo4j", or "web_search"
    """
    message_lower = user_message.lower()
    
    # --- Neo4j Knowledge Graph Triggers ---
    neo4j_keywords = [
        "knowledge graph",
        "graph database",
        "what do i know about",
        "what's in my graph",
        "show me connections",
        "relationships between",
        "entities in my",
        "cypher query",
        "neo4j"
    ]
    
    if any(keyword in message_lower for keyword in neo4j_keywords):
        return "neo4j"
    
    # --- Web Search Triggers ---
    # Current events and time-sensitive queries
    current_time_keywords = [
        "latest", "recent", "current", "today", "this week", "this month",
        "breaking", "news", "update", "now", "2024", "2025"
    ]
    
    # Specific domains that require web search
    web_domains = [
        "stock price", "market cap", "company valuation",
        "weather", "sports score", "election results",
        "trending", "viral", "popular now"
    ]
    
    # Questions that explicitly ask for web information
    web_explicit = [
        "search the web", "look up online", "find on the internet",
        "google", "search for"
    ]
    
    if (any(keyword in message_lower for keyword in current_time_keywords) or
        any(domain in message_lower for domain in web_domains) or
        any(phrase in message_lower for phrase in web_explicit)):
        return "web_search"
    
    # --- Default to File Search (Gemini) ---
    # This handles:
    # - General questions
    # - Questions about uploaded documents
    # - Conversational queries
    # - Analysis and reasoning tasks
    return "file_search"


def should_use_streaming(route: QueryRoute) -> bool:
    """
    Determines if streaming should be used for a given route.
    
    Args:
        route: The query route
        
    Returns:
        True if streaming should be used, False otherwise
    """
    # Only file_search supports streaming with Gemini
    return route == "file_search"


def get_route_description(route: QueryRoute) -> str:
    """
    Get a human-readable description of the route.
    
    Args:
        route: The query route
        
    Returns:
        Description string
    """
    descriptions = {
        "file_search": "Searching your documents with Gemini...",
        "neo4j": "Querying your knowledge graph...",
        "web_search": "Searching the web..."
    }
    return descriptions.get(route, "Processing your query...")
