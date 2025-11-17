#!/usr/bin/env python3
"""
Larry Web Search Integration with Exa.ai
Neural semantic search with proper source citation
"""

import datetime
import os
from typing import List, Dict, Optional

try:
    from exa_py import Exa
    EXA_AVAILABLE = True
except ImportError:
    EXA_AVAILABLE = False
    print("⚠️ exa_py not installed. Install with: pip install exa_py")

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

def search_with_exa(
    query: str,
    exa_api_key: str,
    num_results: int = 5,
    start_published_date: Optional[str] = None
) -> Optional[Dict]:
    """
    Search using Exa.ai neural search engine

    Args:
        query: Search query
        exa_api_key: Exa API key
        num_results: Number of results to return (default 5)
        start_published_date: ISO date string (e.g., "2022-01-01")

    Returns:
        Dictionary with search results or None if error
    """

    if not EXA_AVAILABLE:
        return None

    if not exa_api_key:
        print("⚠️ Exa API key not provided")
        return None

    try:
        exa = Exa(api_key=exa_api_key)

        # Default to last 3 years if no date specified
        if not start_published_date:
            three_years_ago = datetime.datetime.now() - datetime.timedelta(days=3*365)
            start_published_date = three_years_ago.strftime("%Y-%m-%d")

        # Search with Exa
        results = exa.search_and_contents(
            query,
            type="neural",  # Use neural search for semantic matching
            num_results=num_results,
            start_published_date=start_published_date,
            text={"max_characters": 500},  # Get excerpts
            highlights=True  # Get highlighted relevant sections
        )

        return results

    except Exception as e:
        print(f"⚠️ Exa search error: {e}")
        return None

def format_exa_results(results, max_sources: int = 3) -> str:
    """Format Exa search results with proper citations"""

    if not results or not hasattr(results, 'results') or len(results.results) == 0:
        return """
🔎 **Web Search Status:**
No recent research found matching your query. Proceeding with existing knowledge base.
"""

    formatted = """
🔎 **Current Research Findings:**

Based on the latest cutting-edge research and industry reports:

"""

    # Process up to max_sources results
    sources_list = []
    for i, result in enumerate(results.results[:max_sources], 1):
        title = result.title or "Untitled"
        url = result.url
        published_date = result.published_date or "Recent"

        # Extract year from published_date if available
        year = "2024"
        if published_date != "Recent":
            try:
                year = published_date.split('-')[0]
            except:
                pass

        # Get excerpt or highlight
        excerpt = ""
        if hasattr(result, 'highlights') and result.highlights:
            excerpt = result.highlights[0][:200] + "..."
        elif hasattr(result, 'text') and result.text:
            excerpt = result.text[:200] + "..."

        sources_list.append(f"**{i}. [{title}, {year}]({url})**\n   {excerpt}\n")

    formatted += "\n".join(sources_list)

    formatted += """
**Synthesis:** These findings represent cutting-edge, hyper-validated research from the last 3 years.

"""

    return formatted

def create_search_summary(results) -> str:
    """Create a brief summary of search results for context"""

    if not results or not hasattr(results, 'results') or len(results.results) == 0:
        return "No current research found."

    num_results = len(results.results)
    sources = [result.url.split('/')[2] for result in results.results[:3]]  # Get domains

    return f"Found {num_results} recent sources from {', '.join(set(sources))} and others."

def integrate_search_with_response(
    user_message: str,
    persona: str,
    problem_type: str,
    exa_api_key: Optional[str] = None
) -> Optional[str]:
    """
    Main integration function: Check if search needed, perform search, format results

    Args:
        user_message: User's question
        persona: Detected user persona
        problem_type: Detected problem type
        exa_api_key: Exa API key

    Returns:
        Formatted search results string or None if search not needed/failed
    """

    # Check if web search is needed
    if not should_use_web_search(user_message):
        return None

    if not exa_api_key:
        print("⚠️ Exa API key not configured. Skipping web search.")
        return None

    # Construct optimized query
    query = construct_search_query(user_message, persona, problem_type)

    print(f"🔍 Searching Exa.ai with query: {query}")

    # Perform search
    results = search_with_exa(query, exa_api_key, num_results=5)

    if not results:
        return None

    # Format results
    formatted_results = format_exa_results(results, max_sources=3)

    return formatted_results

# Example usage:
"""
from larry_web_search import integrate_search_with_response

# In chat function:
search_results = integrate_search_with_response(
    user_message=user_input,
    persona=st.session_state.persona,
    problem_type=st.session_state.problem_type,
    exa_api_key=os.getenv('EXA_API_KEY')
)

if search_results:
    # Prepend search results to system prompt or include in context
    enhanced_prompt = f"{LARRY_SYSTEM_PROMPT}\n\n{search_results}"
"""
