#!/usr/bin/env python3
"""
Larry Navigator - Streamlit Web Interface
Hyper-Modern Minimal De Stijl Redesign
Powered by LangChain Agent & Anthropic Claude
"""

import streamlit as st
import os
import re
from pathlib import Path
import json

# Import LangChain components
from larry_agent import initialize_larry_agent, chat_with_larry_agent, get_current_state
import google.generativeai as genai
from google.generativeai import types

# Import existing utilities for sidebar display
from larry_neo4j_rag import is_neo4j_configured, is_faiss_configured

# --- 1. Utility Functions ---

def set_secrets_as_env():
    """Reads st.secrets and sets them as environment variables for LangChain tools."""
    for key, value in st.secrets.items():
        if key not in os.environ:
            os.environ[key] = str(value)

def load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()def load_env(): --- 2. Streamlit App Setup ---

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

# --- 3. Session State and Agent Initialization ---

if "messages" not in st.session_state:
    st.session_state.messages = []

# Use ANTHROPIC_API_KEY for the primary LLM
if "anthropic_api_key" not in st.session_state:
    try:
        st.session_state.anthropic_api_key = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY"))
    except:
        st.session_state.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

if "exa_api_key" not in st.session_state:
    try:
        st.session_state.exa_api_key = st.secrets.get("EXA_API_KEY", os.getenv("EXA_API_KEY"))
    except:
        st.session_state.exa_api_key = os.getenv("EXA_API_KEY")

# Initialize the LangChain Agent
if "larry_agent_executor" not in st.session_state and st.session_state.anthropic_api_key:
    st.session_state.larry_agent_executor = initialize_larry_agent(
        api_key=st.session_state.anthropic_api_key, # Pass the key for initialization
        history=st.session_state.messages
    )

# --- 4. Sidebar (Simplified Left Panel) ---

with st.sidebar:
    st.markdown("### ⚙️ Configuration & Context")

    # Get current state from the agent
    if "larry_agent_executor" in st.session_state:
        current_state = get_current_state(st.session_state.larry_agent_executor)
        st.session_state.persona = current_state.get("persona", "general")
        st.session_state.problem_type = current_state.get("problem_type", "general")
        st.session_state.uncertainty_score = current_state.get("uncertainty_score", 50)
        st.session_state.risk_score = current_state.get("risk_score", 50)
        st.session_state.recommended_frameworks = current_state.get("recommended_frameworks", [])
    else:
        st.session_state.persona = "general"
        st.session_state.problem_type = "general"
        st.session_state.uncertainty_score = 50
        st.session_state.risk_score = 50
        st.session_state.recommended_frameworks = []

    uncertainty_level = "low" if st.session_state.uncertainty_score > 75 else ("high" if st.session_state.uncertainty_score < 25 else "medium")
    risk_level = "low" if st.session_state.risk_score < 25 else ("high" if st.session_state.risk_score > 75 else "medium")

    st.markdown("#### 🎭 Persona")
    st.markdown(f"<div class=\"minimal-persona-badge\">{st.session_state.persona.upper()}</div>", unsafe_allow_html=True)

    st.markdown("#### ⚖️ Uncertainty & Risk")
    st.markdown(f"""
    <div class=\"minimal-indicator\">
        Uncertainty: <span>{st.session_state.uncertainty_score}%</span> ({uncertainty_level.upper()})
    </div>
    <div class=\"minimal-indicator\">
        Risk: <span>{st.session_state.risk_score}%</span> ({risk_level.upper()})
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("#### 🔑 API Keys")
    if st.session_state.anthropic_api_key:
        st.success("✅ Anthropic Claude Configured")
    else:
        st.warning("⚠️ Anthropic Claude Key Missing")
        api_key_input = st.text_input("Anthropic Claude API Key", type="password", value="", help="Enter your Anthropic Claude key")
        if api_key_input:
            st.session_state.anthropic_api_key = api_key_input
            st.rerun()

    if st.session_state.exa_api_key:
        st.info("🔍 Exa.ai Configured")
    else:
        st.info("💡 Exa.ai Key Optional")
        exa_key_input = st.text_input("Exa.ai API Key (Optional)", type="password", value="", help="Enables web search")
        if exa_key_input:
            st.session_state.exa_api_key = exa_key_input
            st.rerun()

    st.markdown("---")

    st.markdown("#### 📚 Knowledge Sources")
    st.caption(f"File Search: {'Active' if os.path.exists('larry_store_info.json') else 'Not configured'}")
    st.caption(f"Network-Effect (Neo4j): {'Active' if is_neo4j_configured() else 'Not configured'}")
    st.caption(f"Vector Store (FAISS): {'Active (Simulated)' if is_faiss_configured() else 'Not configured'}")

    st.markdown("---")

    st.markdown("#### 🧭 Frameworks")
    with st.expander("View Recommended Frameworks", expanded=False):
        if st.session_state.recommended_frameworks:
            for framework in st.session_state.recommended_frameworks:
                st.markdown(f"**{framework['name']}**\n<small>{framework['description']}</small>", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("No specific frameworks recommended yet. Start a conversation!")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        if "larry_agent_executor" in st.session_state:
            del st.session_state.larry_agent_executor
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
        <p>I now use a LangChain Agent powered by Anthropic Claude to provide deep, sequential reasoning and a provocative "killer feature" to challenge your thinking.</p>
    </div>
    """, unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state.anthropic_api_key:
    if "larry_agent_executor" not in st.session_state:
        st.info("Initializing LangChain Agent with Anthropic Claude... Please wait.")
        st.rerun()

    user_input = st.chat_input("Ask Larry about innovation, problem-solving, or PWS methodology...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("🧠 Larry is thinking... Orchestrating RAG with LangChain & Claude..."):
            response_text = chat_with_larry_agent(
                agent_executor=st.session_state.larry_agent_executor,
                user_message=user_input
            )
        
        # The response_text is a structured JSON string from the tool
        try:
            structured_response = json.loads(response_text)
            final_answer = structured_response.get("final_answer", "Error: Could not parse final answer.")
            provocative_question = structured_response.get("provocative_question", "No provocative question generated.")
        except (json.JSONDecodeError, TypeError):
            final_answer = response_text # Fallback to raw text if not valid JSON
            provocative_question = "No provocative question generated."

        # 1. Render the Provocative Question (Killer Feature)
        if provocative_question != "No provocative question generated.":
            with st.expander("🚨 Provocative Question", expanded=True):
                st.markdown(f"<div class=\"accent-block provocative-block\">{provocative_question}</div>", unsafe_allow_html=True)
        
        # 2. Render the Final Answer
        with st.chat_message("assistant"):
            st.markdown(final_answer)

        # 3. Append to history
        st.session_state.messages.append({"role": "assistant", "content": final_answer})
        
        # Rerun to update the sidebar with the latest state from the agent
        st.rerun()
else:
    st.info("👈 Please enter your Anthropic Claude API key in the sidebar to start chatting!")

st.markdown("---")
st.markdown("""
<div style=\"text-align: center; color: #666; padding: 1rem;\">
    <strong>Larry - Your Personal Uncertainty Navigator</strong><br>
    Powered by LangChain & Anthropic Claude | Lawrence Aronhime's PWS Methodology
</div>
""", unsafe_allow_html=True)
