"""
Larry Navigator v2.0 - PWS Innovation Mentor with 4D Problem Diagnosis
Main Streamlit Application
"""

import os
import json
import streamlit as st
from typing import Iterator, Dict, Any, List
from google import genai
from google.genai import types

# Import styles
from styles.theme import inject_warm_theme
from styles.components import inject_component_styles

# Import components
from components.header import render_larry_header, render_pws_explanation
from components.problem_dashboard import render_problem_dashboard, render_compact_dashboard
from components.research_panel import render_research_panel, render_typing_indicator
from components.quick_actions import render_quick_actions, render_welcome_prompts

# Import utilities
from utils.session_state import (
    initialize_session_state,
    get_diagnosis,
    update_diagnosis,
    add_message,
    add_research_result,
    set_agent_status,
    get_session_stats
)
from utils.tavily_client import LarryTavilyClient, is_tavily_configured

# Import agents
from agents.definition_classifier import DefinitionClassifierAgent
from agents.complexity_assessor import ComplexityAssessorAgent
from agents.risk_uncertainty_evaluator import RiskUncertaintyEvaluatorAgent
from agents.wickedness_classifier import WickednessClassifierAgent
from agents.diagnosis_consolidator import DiagnosisConsolidatorAgent
from agents.research_agent import ResearchAgent

# Import system prompts
from config.prompts import LARRY_SYSTEM_PROMPT


# ============================================
# Configuration
# ============================================

st.set_page_config(
    page_title="Larry Navigator v2.0",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Inject CSS with error handling
try:
    inject_warm_theme()
    inject_component_styles()
except Exception as e:
    st.error(f"⚠️ CSS injection error: {e}")
    # Fallback: use basic Streamlit styling


# ============================================
# Helper Functions
# ============================================

def load_file_search_config() -> Dict[str, Any]:
    """Load File Search configuration from larry_store_info.json"""
    try:
        with open("larry_store_info.json", "r") as f:
            store_info = json.load(f)
            return {
                "store_name": store_info.get("store_name"),
                "total_files": store_info.get("total_files", 0)
            }
    except FileNotFoundError:
        st.warning("⚠️ File Search not configured. larry_store_info.json not found.")
        return {"store_name": None, "total_files": 0}


def get_gemini_client() -> genai.Client:
    """Get Gemini client with API key"""
    api_key = os.getenv("GOOGLE_AI_API_KEY") or st.secrets.get("GOOGLE_AI_API_KEY")
    if not api_key:
        st.error("❌ GOOGLE_AI_API_KEY not found. Please configure in .streamlit/secrets.toml")
        st.stop()
    return genai.Client(api_key=api_key)


def run_diagnostic_agents_background(api_key: str, conversation_history: List[Dict[str, str]]):
    """Run all diagnostic agents in background and update session state

    Args:
        api_key: Google AI API key
        conversation_history: Current conversation
    """

    # Skip if no conversation yet
    if len(conversation_history) == 0:
        return

    try:
        # Initialize agents
        definition_agent = DefinitionClassifierAgent(api_key)
        complexity_agent = ComplexityAssessorAgent(api_key)
        risk_uncertainty_agent = RiskUncertaintyEvaluatorAgent(api_key)
        wickedness_agent = WickednessClassifierAgent(api_key)
        consolidator_agent = DiagnosisConsolidatorAgent(api_key)

        # Run classifications
        set_agent_status("definition_classifier", "running")
        definition_result = definition_agent.classify(conversation_history)
        set_agent_status("definition_classifier", "complete")

        set_agent_status("complexity_assessor", "running")
        complexity_result = complexity_agent.assess(conversation_history)
        set_agent_status("complexity_assessor", "complete")

        set_agent_status("risk_uncertainty_evaluator", "running")
        risk_uncertainty_result = risk_uncertainty_agent.evaluate(conversation_history)
        set_agent_status("risk_uncertainty_evaluator", "complete")

        set_agent_status("wickedness_classifier", "running")
        wickedness_result = wickedness_agent.classify(conversation_history)
        set_agent_status("wickedness_classifier", "complete")

        # Consolidate
        set_agent_status("diagnosis_consolidator", "running")
        consolidated = consolidator_agent.consolidate(
            definition_result,
            complexity_result,
            risk_uncertainty_result,
            wickedness_result
        )
        set_agent_status("diagnosis_consolidator", "complete")

        # Update session state
        update_diagnosis("definition", definition_result["classification"], definition_result["confidence"])
        update_diagnosis("complexity", complexity_result["complexity"], complexity_result["confidence"])
        update_diagnosis("risk_uncertainty", risk_uncertainty_result["position"])
        update_diagnosis("wickedness", wickedness_result["wickedness"], wickedness_result["score"])

        # Store consolidated result
        st.session_state.last_consolidated_diagnosis = consolidated

    except Exception as e:
        st.error(f"⚠️ Diagnostic agents error: {e}")


def stream_larry_response(
    client: genai.Client,
    user_message: str,
    conversation_history: List[Dict[str, str]],
    file_search_store: str
) -> Iterator[str]:
    """Stream Larry's response using Gemini with File Search

    Args:
        client: Gemini client
        user_message: User's message
        conversation_history: Previous messages
        file_search_store: File Search store name

    Yields:
        Response chunks
    """

    # Build conversation for Gemini
    contents = []

    # Add system prompt as first user message
    contents.append({
        "role": "user",
        "parts": [{"text": LARRY_SYSTEM_PROMPT}]
    })

    contents.append({
        "role": "model",
        "parts": [{"text": "Understood. I'm Larry, your PWS Innovation Mentor. I'll help you navigate complex problems using diagnostic thinking and the PWS framework. What brought you here today?"}]
    })

    # Add conversation history
    for msg in conversation_history:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    # Add current user message
    contents.append({
        "role": "user",
        "parts": [{"text": user_message}]
    })

    # Configure File Search
    config = types.GenerateContentConfig(
        temperature=0.7,
        top_p=0.95,
        max_output_tokens=2048,
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store=file_search_store
                )
            )
        ]
    )

    # Stream response
    response = client.models.generate_content_stream(
        model="gemini-3-pro-preview",
        contents=contents,
        config=config
    )

    for chunk in response:
        if chunk.text:
            yield chunk.text


# ============================================
# Main App
# ============================================

def main():
    """Main application"""

    # Initialize session state
    initialize_session_state()

    # Get API key
    api_key = os.getenv("GOOGLE_AI_API_KEY") or st.secrets.get("GOOGLE_AI_API_KEY")
    if not api_key:
        st.error("❌ GOOGLE_AI_API_KEY not found. Please configure.")
        st.stop()

    # Load File Search config
    file_search_config = load_file_search_config()
    file_search_store = file_search_config.get("store_name")

    # Get Gemini client
    client = get_gemini_client()

    # Get Tavily client (optional)
    tavily_client = None
    if is_tavily_configured():
        try:
            tavily_client = LarryTavilyClient()
        except:
            pass

    # ========================================
    # Header
    # ========================================
    render_larry_header()

    # ========================================
    # Sidebar
    # ========================================
    with st.sidebar:
        st.markdown("### ⚙️ Settings")

        # Show File Search status
        if file_search_store:
            st.success(f"✅ File Search: {file_search_config.get('total_files', 0)} chunks")
        else:
            st.warning("⚠️ File Search not configured")

        # Show Tavily status
        if tavily_client:
            st.success("✅ Web Research: Enabled")
        else:
            st.info("💡 Web Research: Disabled")

        st.markdown("---")

        # Compact dashboard
        st.markdown("### 📊 Current Diagnosis")
        render_compact_dashboard()

        st.markdown("---")

        # Session stats
        stats = get_session_stats()
        st.markdown("### 📈 Session Stats")
        st.markdown(f"""
        <div style="font-size: 0.875rem; color: var(--text-secondary);">
            <div>💬 Turns: {stats['total_turns']}</div>
            <div>🔍 Research: {stats['total_research_queries']}</div>
            <div>⏱️ Duration: {stats['session_duration_minutes']} min</div>
        </div>
        """, unsafe_allow_html=True)

        # Reset button
        if st.button("🔄 New Problem Session", use_container_width=True):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # ========================================
    # Main Content
    # ========================================

    # Show problem dashboard
    if st.session_state.total_turns > 0:
        render_problem_dashboard()
    else:
        # First-time welcome
        render_welcome_prompts()

    # ========================================
    # Chat Interface
    # ========================================

    # Display chat history
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]

        with st.chat_message(role):
            st.markdown(content)

    # ========================================
    # Chat Input
    # ========================================

    if user_input := st.chat_input("Share your problem or question..."):

        # Add user message
        add_message("user", user_input)

        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)

        # Check if research is needed
        research_needed = False
        research_results = None

        if tavily_client:
            research_agent = ResearchAgent(api_key)
            research_decision = research_agent.analyze_research_need(
                user_input,
                st.session_state.messages
            )

            if research_decision.get("should_research", False):
                research_needed = True
                queries = research_decision.get("queries", [])

                # Show typing indicator
                with st.chat_message("assistant"):
                    render_typing_indicator("Researching the web...")

                # Execute Tavily searches
                set_agent_status("research_agent", "running")
                research_results = tavily_client.search_multiple_queries(queries)
                set_agent_status("research_agent", "complete")

        # Generate Larry's response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""

            # Show typing indicator while generating
            render_typing_indicator("Larry is thinking...")

            # Stream response
            for chunk in stream_larry_response(
                client,
                user_input,
                st.session_state.messages,
                file_search_store
            ):
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")

            # Final response
            response_placeholder.markdown(full_response)

            # Show research results if available
            if research_needed and research_results:
                render_research_panel(
                    queries=research_results.get("queries", []),
                    results=research_results.get("all_results", []),
                    synthesis=None,  # Could add synthesis here
                    is_loading=False
                )

                # Store research history
                add_research_result(
                    query=", ".join(research_results.get("queries", [])),
                    results=research_results.get("all_results", []),
                    synthesis=""
                )

        # Add assistant message
        add_message("assistant", full_response)

        # Run diagnostic agents in background (after user turn)
        run_diagnostic_agents_background(api_key, st.session_state.messages)

        # Rerun to update dashboard
        st.rerun()


if __name__ == "__main__":
    main()
