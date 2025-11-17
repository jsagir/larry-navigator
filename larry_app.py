#!/usr/bin/env python3
"""
Larry Navigator - Streamlit Web Interface
Hyper-Modern Minimal De Stijl Redesign
"""

import streamlit as st
import os
import re
from pathlib import Path
from google import genai
from google.genai import types
import json
from larry_web_search import integrate_search_with_response
from larry_framework_recommender import (
    recommend_frameworks,
    calculate_uncertainty_risk,
    get_framework_notification,
    get_all_frameworks_sorted
)
from larry_neo4j_rag import get_neo4j_rag_context, is_neo4j_configured, is_faiss_configured, get_faiss_rag_context
from streamlit_integration import send_to_rasa, parse_rasa_response, map_streamlit_session_to_rasa, update_streamlit_from_rasa

# --- 1. Utility Functions ---

# Load environment variables
def load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

load_env()

# Load store info
def load_store_info():
    """Load File Search store information"""
    store_file = Path(__file__).parent / "larry_store_info.json"
    if store_file.exists():
        with open(store_file, "r") as f:
            return json.load(f)
    return None

def detect_persona(message):
    """Detect user persona from message"""
    message_lower = message.lower()

    if any(word in message_lower for word in ["startup", "founder", "validate", "customer", "market fit"]):
        return "entrepreneur"
    elif any(word in message_lower for word in ["corporate", "company", "team", "organization", "portfolio"]):
        return "corporate"
    elif any(word in message_lower for word in ["exam", "test", "study", "homework", "course", "assignment"]):
        return "student"
    elif any(word in message_lower for word in ["research", "theory", "literature", "scholar", "academic"]):
        return "researcher"
    elif any(word in message_lower for word in ["client", "workshop", "facilitate", "advise", "consult"]):
        return "consultant"
    else:
        return "general"

def classify_problem_type(message):
    """Classify problem type from message context"""
    message_lower = message.lower()

    if any(word in message_lower for word in ["future", "trend", "macro", "scenario", "long-term", "disrupt"]):
        return "undefined", 0
    elif any(word in message_lower for word in ["opportunity", "near-term", "adjacent", "expansion", "growth"]):
        return "ill-defined", 50
    elif any(word in message_lower for word in ["implement", "build", "execute", "prototype", "mvp", "solution"]):
        return "well-defined", 85
    else:
        return "general", 50

def parse_response_for_message_types(response_text):
    # This function is no longer strictly needed as Rasa provides structured responses
    # It is kept as a placeholder to avoid breaking the render_message function below
    messages = []
    sections = response_text.split("\n\n")
    for section in sections:
        if not section.strip():
            continue
        messages.append(("regular", section))
    return messages

def render_message(message_type, content):
    # Updated to handle new custom message types from Rasa
    if message_type == "provocative":
        with st.expander("🚨 Provocative Question", expanded=True):
            st.markdown(f"<div class=\"accent-block provocative-block\">{content}</div>", unsafe_allow_html=True)
    elif message_type == "framework":
        with st.expander("💡 Framework Suggestion", expanded=True):
            st.markdown(f"<div class=\"accent-block framework-block\">{content}</div>", unsafe_allow_html=True)
    elif message_type == "action":
        with st.expander("✅ Action Plan", expanded=True):
            st.markdown(f"<div class=\"accent-block action-block\">{content}</div>", unsafe_allow_html=True)
    elif message_type == "case":
        with st.expander("📚 Case Study", expanded=True):
            st.markdown(f"<div class=\"accent-block case-block\">{content}</div>", unsafe_allow_html=True)
    elif message_type == "diagnostic":
        st.error(content)
    else: # Regular assistant message
        with st.chat_message("assistant"):
            st.markdown(content)

def chat_with_larry(user_message):
    """Send message to Larry via the Rasa Middleware."""
    sender_id = map_streamlit_session_to_rasa(st.session_state)
    
    with st.spinner("🧠 Larry is thinking... Orchestrating intelligent RAG via Rasa..."):
        # 1. Send message to Rasa
        rasa_response = send_to_rasa(user_message, sender_id)
        
        # 2. Parse Rasa response into Streamlit format
        parsed_messages = parse_rasa_response(rasa_response)
        
        # 3. Get latest slots from Rasa (to update sidebar indicators)
        # This is a placeholder. In a full deployment, the custom actions would update the slots
        # and we would need a separate API call to the Rasa tracker to fetch them.
        # For now, we rely on the custom actions to send back the necessary slot updates
        # and manually update the persona/problem_type based on the latest message's intent
        
        # Fallback to manual update if Rasa is not fully integrated yet
        if "rasa_sender_id" not in st.session_state:
            st.session_state.persona = detect_persona(user_message)
            st.session_state.problem_type, _ = classify_problem_type(user_message)
            
        return parsed_messages

# --- 2. Streamlit App Setup ---

def inject_css():
    css_path = Path(__file__).parent / "minimal_destijl_style.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

inject_css()

st.set_page_config(
    page_title="Larry - Your Personal Uncertainty Navigator",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="expanded"
)

from larry_system_prompt_v3 import LARRY_SYSTEM_PROMPT_V3
LARRY_SYSTEM_PROMPT = LARRY_SYSTEM_PROMPT_V3

# --- 3. Session State Initialization ---

if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key" not in st.session_state:
    try:
        st.session_state.api_key = st.secrets.get("GOOGLE_AI_API_KEY", os.getenv("GOOGLE_AI_API_KEY"))
    except:
        st.session_state.api_key = os.getenv("GOOGLE_AI_API_KEY")

if "exa_api_key" not in st.session_state:
    try:
        st.session_state.exa_api_key = st.secrets.get("EXA_API_KEY", os.getenv("EXA_API_KEY"))
    except:
        st.session_state.exa_api_key = os.getenv("EXA_API_KEY")

if "persona" not in st.session_state:
    st.session_state.persona = "general"

if "problem_type" not in st.session_state:
    st.session_state.problem_type = "general"

if "uncertainty_score" not in st.session_state:
    st.session_state.uncertainty_score = 50

if "risk_score" not in st.session_state:
    st.session_state.risk_score = 50

if "uncertainty_level" not in st.session_state:
    st.session_state.uncertainty_level = "medium"

if "risk_level" not in st.session_state:
    st.session_state.risk_level = "medium"

if "recommended_frameworks" not in st.session_state:
    st.session_state.recommended_frameworks = []

# --- 4. Sidebar (Simplified Left Panel) ---

with st.sidebar:
    st.markdown("### ⚙️ Configuration & Context")

    st.markdown("#### 🎭 Persona")
    st.markdown(f"<div class=\"minimal-persona-badge\">{st.session_state.persona.upper()}</div>", unsafe_allow_html=True)

    st.markdown("#### ⚖️ Uncertainty & Risk")
    st.markdown(f"""
    <div class=\"minimal-indicator\">
        Uncertainty: <span>{st.session_state.uncertainty_score}%</span> ({st.session_state.uncertainty_level.upper()})
    </div>
    <div class=\"minimal-indicator\">
        Risk: <span>{st.session_state.risk_score}%</span> ({st.session_state.risk_level.upper()})
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("#### 🔑 API Keys")

    if st.session_state.api_key:
        st.success("✅ Google AI Configured")
    else:
        st.warning("⚠️ Google AI Key Missing")
        api_key_input = st.text_input(
            "Google AI API Key",
            type="password",
            value="",
            help="Enter your Google AI key"
        )
        if api_key_input:
            st.session_state.api_key = api_key_input
            st.rerun()

    if st.session_state.exa_api_key:
        st.info("🔍 Exa.ai Configured")
    else:
        st.info("💡 Exa.ai Key Optional")
        exa_key_input = st.text_input(
            "Exa.ai API Key (Optional)",
            type="password",
            value="",
            help="Enables web search"
        )
        if exa_key_input:
            st.session_state.exa_api_key = exa_key_input
            st.rerun()

    st.markdown("---")

    st.markdown("#### 📚 Knowledge Sources")

    store_info = load_store_info()
    if store_info:
        st.caption(f"File Search: Active ({store_info.get('total_chunks', '2,988')} chunks)")
    else:
        st.caption("File Search: Not configured")

    if is_neo4j_configured():
        st.caption("Network-Effect (Neo4j): Active")
    else:
        st.caption("Network-Effect (Neo4j): Not configured")
        
    if is_faiss_configured():
        st.caption("Vector Store (FAISS): Active (Simulated)")
    else:
        st.caption("Vector Store (FAISS): Not configured")

    st.markdown("---")

    st.markdown("#### 🧭 Frameworks")
    with st.expander("View Recommended Frameworks", expanded=False):
        if st.session_state.recommended_frameworks:
            for framework in st.session_state.recommended_frameworks:
                st.markdown(f"""
                **{framework["name"]}**
                <small>{framework["description"]}</small>
                """, unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("No specific frameworks recommended yet. Start a conversation!")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.persona = "general"
        st.session_state.problem_type = "general"
        st.rerun()

# --- 5. Main Content (Single Column Chat) ---

st.markdown("""
<div class=\"destijl-header\">
    <h1>🎯 LARRY</h1>
    <p>Your Personal Uncertainty Navigator</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class=\"accent-block\">
        <h3>Welcome to Larry, the Hyper-Minimal Uncertainty Navigator.</h3>
        <p>I'm here to help you structure ill-defined problems. Start by asking a question about innovation, strategy, or problem-solving.</p>
        <p>Your persona and problem type will be automatically detected and displayed in the sidebar. Advanced features like framework recommendations are now opt-in, accessible via the sidebar.</p>
    </div>
    """, unsafe_allow_html=True)

for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    else:
        parsed_messages = parse_response_for_message_types(message["content"])
        for msg_type, msg_content in parsed_messages:
            render_message(msg_type, msg_content)

if st.session_state.api_key:
    user_input = st.chat_input("Ask Larry about innovation, problem-solving, or PWS methodology...")

    if user_input:
        # The following logic is now handled by the Rasa Action Server for stateful management:
        # - Persona detection and refinement
        # - Problem type classification
        # - Uncertainty/Risk calculation
        # - Framework recommendation
        # The Streamlit UI will be updated via the Rasa slots.

        st.session_state.messages.append({"role": "user", "content": user_input})

        # 4. Get response from Larry via Rasa Middleware
        rasa_messages = chat_with_larry(user_message=user_input)

        # 5. Render response and update history
        for message in rasa_messages:
            render_message(message["type"], message["content"])
            st.session_state.messages.append({"role": "assistant", "type": message["type"], "content": message["content"]})

        # 6. Rerun to update the sidebar with new persona/problem type (updated by Rasa slots)
        st.rerun()
else:
    st.info("👈 Please enter your Google AI API key in the sidebar to start chatting!")

st.markdown("---")
st.markdown("""
<div style=\"text-align: center; color: #666; padding: 1rem;\">
    <strong>Larry - Your Personal Uncertainty Navigator</strong><br>
    Powered by Google Gemini 2.5 Flash | Lawrence Aronhime's PWS Methodology
</div>
""", unsafe_allow_html=True)
