"""
Larry Navigator v2.0 - Simplified Native Streamlit Version
Works without custom HTML/CSS for maximum compatibility
"""

import os
import json
import streamlit as st
from typing import Iterator, Dict, Any, List
from google import genai
from google.genai import types

# Import utilities
from utils.session_state import (
    initialize_session_state,
    get_diagnosis,
    update_diagnosis,
    add_message,
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
    page_title="🎯 Larry Navigator v2.0",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================
# Helper Functions
# ============================================

def load_file_search_config() -> Dict[str, Any]:
    """Load File Search configuration"""
    try:
        with open("larry_store_info.json", "r") as f:
            store_info = json.load(f)
            return {
                "store_name": store_info.get("store_name"),
                "total_files": store_info.get("total_files", 0)
            }
    except FileNotFoundError:
        return {"store_name": None, "total_files": 0}


def get_gemini_client() -> genai.Client:
    """Get Gemini client with API key"""
    api_key = os.getenv("GOOGLE_AI_API_KEY") or st.secrets.get("GOOGLE_AI_API_KEY")
    if not api_key:
        st.error("❌ GOOGLE_AI_API_KEY not found. Please configure in .streamlit/secrets.toml")
        st.stop()
    return genai.Client(api_key=api_key)


def run_diagnostic_agents_background(api_key: str, conversation_history: List[Dict[str, str]]):
    """Run all diagnostic agents in background"""
    if len(conversation_history) == 0:
        return

    try:
        # Initialize agents
        definition_agent = DefinitionClassifierAgent(api_key)
        complexity_agent = ComplexityAssessorAgent(api_key)
        risk_uncertainty_agent = RiskUncertaintyEvaluatorAgent(api_key)
        wickedness_agent = WickednessClassifierAgent(api_key)

        # Run classifications
        definition_result = definition_agent.classify(conversation_history)
        complexity_result = complexity_agent.assess(conversation_history)
        risk_uncertainty_result = risk_uncertainty_agent.evaluate(conversation_history)
        wickedness_result = wickedness_agent.classify(conversation_history)

        # Update session state
        update_diagnosis("definition", definition_result["classification"], definition_result["confidence"])
        update_diagnosis("complexity", complexity_result["complexity"], complexity_result["confidence"])
        update_diagnosis("risk_uncertainty", risk_uncertainty_result["position"])
        update_diagnosis("wickedness", wickedness_result["wickedness"], wickedness_result["score"])

    except Exception as e:
        st.warning(f"⚠️ Diagnostic agents error: {e}")


MINTO_PYRAMID_FRAMEWORK = """# 🧠 Minto Pyramid Pure Logic Framework

You are a pure reasoning engine using Barbara Minto's Pyramid Principle for structured analysis.

**Core Protocol:**
1. SCQA Analysis (Situation → Complication → Question)
2. MECE Decomposition (Mutually Exclusive, Collectively Exhaustive)
3. Pyramid Assembly (Bottom-up reasoning: Supporting Points → Insights → Main Message)

**Key Principles:**
- Transform problems into opportunities
- Use isolated reasoning for Complication and MECE
- No prescriptive answers, only illuminated opportunity landscapes
- Validate: ME + CE + Same Level (MECE), Vertical + Horizontal + Ordering (Pyramid)

**When activated, structure your analysis using:**
- Phase 0: Pre-Analysis (Query decomposition, domain mapping)
- Phase 1: Context Discovery (Assumptions, stakeholders, baseline)
- Phase 2: SCQA (Situation, Complication [isolated], Question, skip Answer)
- Phase 3: MECE (Framework selection, category generation, validation)
- Phase 4: Pyramid (L3 supporting → L2 insights → L1 main message)

Present structured pyramids that reveal hidden opportunities through systematic reasoning.
"""


def stream_larry_response(
    client: genai.Client,
    user_message: str,
    conversation_history: List[Dict[str, str]],
    file_search_store: str
) -> Iterator[str]:
    """Stream Larry's response"""
    # Build conversation
    contents = []

    # System prompt (with Minto framework if activated)
    system_prompt = LARRY_SYSTEM_PROMPT
    if st.session_state.get("minto_framework_active", False):
        system_prompt = MINTO_PYRAMID_FRAMEWORK + "\n\n" + LARRY_SYSTEM_PROMPT

    contents.append({
        "role": "user",
        "parts": [{"text": system_prompt}]
    })

    contents.append({
        "role": "model",
        "parts": [{"text": "Understood. I'm Larry, your PWS Innovation Mentor."}]
    })

    # History
    for msg in conversation_history:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    # Current message
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
# UI Components (Native Streamlit)
# ============================================

def render_header():
    """Render header with PWS badges"""
    st.title("🎯 Larry Navigator v2.0")
    st.caption("Your PWS Innovation Mentor")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🔥 **Real** - Evidence exists")
    with col2:
        st.success("🎯 **Winnable** - Can be solved")
    with col3:
        st.warning("💎 **Worth It** - Value justifies effort")


def render_problem_dashboard():
    """Render 4D diagnostic dashboard"""
    diagnosis = get_diagnosis()

    st.subheader("📊 Problem Diagnosis")

    col1, col2 = st.columns(2)

    with col1:
        # Definition
        st.metric(
            label="Definition Track",
            value=diagnosis.definition.replace("-", " ").title(),
            delta=f"{int(diagnosis.definition_confidence * 100)}% confidence"
        )

        # Complexity
        st.metric(
            label="Complexity (Cynefin)",
            value=diagnosis.complexity.title(),
            delta=f"{int(diagnosis.complexity_confidence * 100)}% confidence"
        )

    with col2:
        # Risk-Uncertainty
        st.metric(
            label="Risk-Uncertainty Position",
            value=f"{diagnosis.risk_uncertainty:.2f}",
            delta="0.0=Risk, 1.0=Uncertainty"
        )

        # Wickedness
        st.metric(
            label="Wickedness Scale",
            value=diagnosis.wickedness.title(),
            delta=f"{int(diagnosis.wickedness_score * 100)}% wicked"
        )


def render_sidebar():
    """Render sidebar with stats"""
    with st.sidebar:
        st.header("⚙️ Settings")

        # File Search status
        file_search_config = load_file_search_config()
        if file_search_config.get("store_name"):
            st.success(f"✅ File Search: {file_search_config.get('total_files', 0)} chunks")
        else:
            st.warning("⚠️ File Search not configured")

        # Tavily status
        if is_tavily_configured():
            st.success("✅ Web Research: Enabled")
        else:
            st.info("💡 Web Research: Disabled")

        st.divider()

        # Minto Framework Status
        if st.session_state.get("minto_framework_active", False):
            st.success("🧠 **Minto Pyramid Active**")
            st.caption("Using structured SCQA + MECE reasoning")
            st.divider()

        # Compact diagnosis
        st.subheader("📊 Current Diagnosis")
        diagnosis = get_diagnosis()

        st.write(f"**Definition:** {diagnosis.definition}")
        st.write(f"**Complexity:** {diagnosis.complexity}")
        st.write(f"**Risk-Uncertainty:** {diagnosis.risk_uncertainty:.2f}")
        st.write(f"**Wickedness:** {diagnosis.wickedness}")
        st.caption(f"Updates: {diagnosis.update_count}")

        st.divider()

        # Session stats
        stats = get_session_stats()
        st.subheader("📈 Session Stats")
        st.write(f"💬 Turns: {stats['total_turns']}")
        st.write(f"🔍 Research: {stats['total_research_queries']}")
        st.write(f"⏱️ Duration: {stats['session_duration_minutes']} min")

        # Minto Pyramid Framework button
        if st.button("🧠 Load Minto Pyramid Framework", use_container_width=True, help="Activate structured analytical reasoning"):
            st.session_state.minto_framework_active = True
            st.success("✓ Minto Pyramid Framework activated!")
            st.info("Larry will now use structured SCQA + MECE reasoning")

        # Reset button
        if st.button("🔄 New Problem Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ============================================
# Main App
# ============================================

def main():
    """Main application"""

    # Initialize
    initialize_session_state()

    # Get API key
    api_key = os.getenv("GOOGLE_AI_API_KEY") or st.secrets.get("GOOGLE_AI_API_KEY")
    if not api_key:
        st.error("❌ GOOGLE_AI_API_KEY not found.")
        st.stop()

    # Load config
    file_search_config = load_file_search_config()
    file_search_store = file_search_config.get("store_name")

    # Get client
    client = get_gemini_client()

    # Render UI
    render_header()
    render_sidebar()

    # Show dashboard if there's conversation
    if st.session_state.total_turns > 0:
        render_problem_dashboard()
    else:
        # Welcome message
        st.info("💡 **Welcome!** I'm here to help you navigate complex problems using the PWS methodology.")

        with st.expander("📚 **Example starting points**", expanded=True):
            st.write("- 'I'm exploring whether to build a new product feature...'")
            st.write("- 'My team is struggling with [challenge]...'")
            st.write("- 'I need to make a decision about [situation]...'")

    st.divider()

    # Chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if user_input := st.chat_input("Share your problem or question..."):

        # Add user message
        add_message("user", user_input)

        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""

            # Show thinking
            with st.spinner("Larry is thinking..."):
                pass

            # Stream response
            for chunk in stream_larry_response(
                client,
                user_input,
                st.session_state.messages,
                file_search_store
            ):
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")

            response_placeholder.markdown(full_response)

        # Add assistant message
        add_message("assistant", full_response)

        # Run diagnostic agents
        run_diagnostic_agents_background(api_key, st.session_state.messages)

        # Rerun to update dashboard
        st.rerun()


if __name__ == "__main__":
    main()
