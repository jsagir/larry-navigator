"""
Research Panel and Citation Components for Larry Navigator v2.0
Displays Tavily search results and AI synthesis
"""

import streamlit as st
from typing import List, Dict, Any, Optional


def render_research_panel(
    queries: List[str],
    results: List[Dict[str, Any]],
    synthesis: Optional[str] = None,
    is_loading: bool = False
):
    """Render the research panel with queries, results, and synthesis

    Args:
        queries: List of search queries executed
        results: List of search results from Tavily
        synthesis: AI-generated synthesis of the results
        is_loading: Whether research is still in progress
    """

    st.markdown("""
    <div class="research-panel">
        <div class="research-header">
            <span class="research-icon">🔍</span>
            <div class="research-title">Web Research</div>
        </div>
    """, unsafe_allow_html=True)

    # Show queries that were executed
    if queries:
        st.markdown("""
        <div class="research-queries">
            <div style="font-weight: 600; margin-bottom: 0.5rem; color: var(--text-secondary);">
                Queries Executed:
            </div>
        """, unsafe_allow_html=True)

        for i, query in enumerate(queries, 1):
            st.markdown(f"""
            <div class="research-query">
                <span style="color: var(--teal-primary);">{i}.</span>
                <span>"{query}"</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Loading state
    if is_loading:
        render_typing_indicator("Searching the web...")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Show synthesis if available
    if synthesis:
        st.markdown(f"""
        <div class="insight-box" style="margin-top: 1.5rem;">
            <span class="insight-icon">💡</span>
            <div class="insight-text">
                <strong>Research Synthesis:</strong><br>
                {synthesis}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Show results count
    if results:
        st.markdown(f"""
        <div style="margin-top: 1.5rem; margin-bottom: 1rem; color: var(--text-secondary); font-size: 0.875rem;">
            Found {len(results)} relevant sources
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Render citation cards
    if results:
        for result in results:
            render_citation_card(result)


def render_citation_card(result: Dict[str, Any]):
    """Render a single citation card

    Args:
        result: {
            "title": "...",
            "url": "...",
            "content": "...",
            "score": 0.95
        }
    """
    title = result.get("title", "Untitled")
    url = result.get("url", "")
    content = result.get("content", "")
    score = result.get("score", 0.0)
    score_percent = int(score * 100)

    # Truncate content if too long
    if len(content) > 300:
        content = content[:300] + "..."

    st.markdown(f"""
    <div class="citation-card">
        <div class="citation-header">
            <a href="{url}" target="_blank" class="citation-title">
                {title}
            </a>
            <div class="citation-score">
                {score_percent}%
            </div>
        </div>

        <div class="citation-content">
            {content}
        </div>

        <div class="citation-url">
            🔗 {url}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_compact_citation(result: Dict[str, Any]):
    """Render a compact citation (for inline references)

    Args:
        result: Citation data
    """
    title = result.get("title", "Untitled")
    url = result.get("url", "")
    score = result.get("score", 0.0)
    score_percent = int(score * 100)

    st.markdown(f"""
    <div style="background: var(--cream-light); padding: 0.75rem; border-radius: var(--radius-sm); border-left: 3px solid var(--teal-primary); margin: 0.5rem 0;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <a href="{url}" target="_blank" style="color: var(--teal-primary); font-weight: 500; text-decoration: none;">
                {title}
            </a>
            <span style="background: var(--teal-bg); color: var(--teal-primary); padding: 0.25rem 0.5rem; border-radius: var(--radius-full); font-size: 0.75rem; font-weight: 600;">
                {score_percent}%
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_typing_indicator(message: str = "Larry is thinking..."):
    """Render typing indicator animation

    Args:
        message: Message to display
    """
    st.markdown(f"""
    <div class="typing-container">
        <div class="typing-avatar">L</div>
        <div style="flex: 1;">
            <div class="typing-text">{message}</div>
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_research_summary(research_history: List[Dict[str, Any]]):
    """Render summary of all research conducted in this session

    Args:
        research_history: List of research results from session state
    """
    if not research_history:
        st.info("No web research conducted yet.")
        return

    st.markdown("""
    <div style="background: var(--cream-light); padding: 1.5rem; border-radius: var(--radius-lg); border: 1px solid var(--border-light);">
        <h3 style="margin-bottom: 1rem;">📚 Research History</h3>
    """, unsafe_allow_html=True)

    for i, research in enumerate(reversed(research_history), 1):
        queries = research.get("queries", [])
        results_count = len(research.get("results", []))
        timestamp = research.get("timestamp", "")

        st.markdown(f"""
        <div style="padding: 1rem; background: var(--cream-bg); border-radius: var(--radius-md); margin-bottom: 1rem;">
            <div style="font-weight: 600; color: var(--teal-primary); margin-bottom: 0.5rem;">
                Research #{i}
            </div>
            <div style="font-size: 0.875rem; color: var(--text-secondary);">
                <div><strong>Queries:</strong> {', '.join(f'"{q}"' for q in queries)}</div>
                <div><strong>Sources:</strong> {results_count}</div>
                <div><strong>Time:</strong> {timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
