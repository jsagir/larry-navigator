#!/usr/bin/env python3
"""
Larry Web Search Integration with Tavily AI
Real-time web search optimized for AI applications with proper source citation
"""

import os
from typing import List, Dict, Optional

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("⚠️ tavily-python not installed. Install with: pip install tavily-python")

def should_use_web_search(user_message):
    """Determine if web search is needed based on user message"""
    message_lower = user_message.lower()

    # Keywords that indicate need for current information
    current_info_keywords = [
        'latest', 'recent', 'current', 'now', 'today',
        'trending', 'emerging', 'new', '2023', '2024', '2025',
        'state of the art', 'cutting edge', 'modern'
    ]

    # Questions about specific companies/products
    specific_entity_keywords = [
        'startup', 'company', 'product', 'technology',
        'market', 'industry', 'sector'
    ]

    # Research validation queries
    validation_keywords = [
        'research', 'study', 'data', 'statistics', 'evidence',
        'validate', 'proof', 'findings', 'report'
    ]

    # Market/trend questions
    market_keywords = [
        'trend', 'forecast', 'growth', 'adoption',
        'competition', 'landscape', 'analysis'
    ]

    return (
        any(keyword in message_lower for keyword in current_info_keywords) or
        any(keyword in message_lower for keyword in specific_entity_keywords) or
        any(keyword in message_lower for keyword in validation_keywords) or
        any(keyword in message_lower for keyword in market_keywords)
    )

def construct_search_query(user_message: str, persona: str, problem_type: str) -> str:
    """Construct optimized search query based on context"""

    # Extract core topic
    core_topic = user_message.strip()

    # Add persona-specific context
    persona_context = {
        'entrepreneur': 'startup innovation venture capital product market fit',
        'corporate': 'enterprise innovation strategy competitive analysis',
        'researcher': 'academic research peer-reviewed study findings',
        'student': 'educational framework methodology tutorial',
        'consultant': 'consulting best practices industry standards',
        'general': 'innovation strategy framework methodology'
    }

    context = persona_context.get(persona, persona_context['general'])

    # Add problem type context
    problem_context = {
        'undefined': 'future trends scenario planning emerging technologies',
        'ill-defined': 'market opportunities growth strategies innovation',
        'well-defined': 'implementation best practices case studies',
        'general': 'innovation research methodology'
    }

    problem_terms = problem_context.get(problem_type, problem_context['general'])

    # Construct semantic query
    query = f"{core_topic} {context} {problem_terms}"

    return query.strip()

def search_with_tavily(
    query: str,
    tavily_api_key: str,
    max_results: int = 5,
    search_depth: str = "advanced",
    include_answer: bool = True
) -> Optional[Dict]:
    """
    Search using Tavily AI search engine optimized for AI agents

    Args:
        query: Search query
        tavily_api_key: Tavily API key
        max_results: Number of results to return (default 5)
        search_depth: 'basic' or 'advanced' (default 'advanced' for higher quality)
        include_answer: Include AI-generated answer summary (default True)

    Returns:
        Dictionary with search results or None if error
    """

    if not TAVILY_AVAILABLE:
        return None

    if not tavily_api_key:
        print("⚠️ Tavily API key not provided")
        return None

    try:
        # Initialize Tavily client
        tavily = TavilyClient(api_key=tavily_api_key)

        # Search with Tavily
        results = tavily.search(
            query=query,
            search_depth=search_depth,
            max_results=max_results,
            include_answer=include_answer,
            include_raw_content=False,  # Don't need full HTML
            include_images=False  # Focus on text content
        )

        return results

    except Exception as e:
        print(f"⚠️ Tavily search error: {e}")
        return None

def format_tavily_results(results: Dict, max_sources: int = 3) -> str:
    """Format Tavily search results with proper citations"""

    if not results or 'results' not in results or len(results['results']) == 0:
        return """
🔎 **Web Search Status:**
No recent research found matching your query. Proceeding with existing knowledge base.
"""

    formatted = """
🔎 **Current Research Findings:**

Based on the latest cutting-edge research and industry reports:

"""

    # Add AI-generated answer summary if available
    if 'answer' in results and results['answer']:
        formatted += f"**AI Summary:** {results['answer']}\n\n"
        formatted += "**Sources:**\n\n"

    # Process up to max_sources results
    sources_list = []
    for i, result in enumerate(results['results'][:max_sources], 1):
        title = result.get('title', 'Untitled')
        url = result.get('url', '')
        content = result.get('content', '')
        score = result.get('score', 0.0)

        # Extract excerpt (Tavily provides pre-processed content)
        excerpt = content[:200] + "..." if len(content) > 200 else content

        # Tavily provides relevance score
        relevance = "High" if score > 0.7 else "Medium" if score > 0.4 else "Relevant"

        sources_list.append(
            f"**{i}. [{title}]({url})** (Relevance: {relevance})\n   {excerpt}\n"
        )

    formatted += "\n".join(sources_list)

    formatted += """
**Synthesis:** These findings represent cutting-edge, hyper-validated research from real-time web search.

"""

    return formatted

def create_search_summary(results: Dict) -> str:
    """Create a brief summary of search results for context"""

    if not results or 'results' not in results or len(results['results']) == 0:
        return "No current research found."

    num_results = len(results['results'])

    # Extract domains from URLs
    try:
        sources = []
        for result in results['results'][:3]:
            url = result.get('url', '')
            if url:
                domain = url.split('/')[2]
                sources.append(domain)

        return f"Found {num_results} recent sources from {', '.join(set(sources))} and others."
    except:
        return f"Found {num_results} recent sources."

def integrate_search_with_response(
    user_message: str,
    persona: str,
    problem_type: str,
    tavily_api_key: Optional[str] = None
) -> Optional[str]:
    """
    Main integration function: Check if search needed, perform search, format results

    Args:
        user_message: User's question
        persona: Detected user persona
        problem_type: Detected problem type
        tavily_api_key: Tavily API key

    Returns:
        Formatted search results string or None if search not needed/failed
    """

    # Check if web search is needed
    if not should_use_web_search(user_message):
        return None

    if not tavily_api_key:
        print("⚠️ Tavily API key not configured. Skipping web search.")
        return None

    # Construct optimized query
    query = construct_search_query(user_message, persona, problem_type)

    print(f"🔍 Searching Tavily AI with query: {query}")

    # Perform search
    results = search_with_tavily(
        query,
        tavily_api_key,
        max_results=5,
        search_depth="advanced",  # Use advanced for higher quality results
        include_answer=True  # Get AI-generated summary
    )

    if not results:
        return None

    # Format results
    formatted_results = format_tavily_results(results, max_sources=3)

    return formatted_results

# Example usage:
"""
from larry_tavily_search import integrate_search_with_response

# In chat function:
search_results = integrate_search_with_response(
    user_message=user_input,
    persona=st.session_state.persona,
    problem_type=st.session_state.problem_type,
    tavily_api_key=os.getenv('TAVILY_API_KEY')
)

if search_results:
    # Prepend search results to system prompt or include in context
    enhanced_prompt = f"{LARRY_SYSTEM_PROMPT}\n\n{search_results}"
"""
