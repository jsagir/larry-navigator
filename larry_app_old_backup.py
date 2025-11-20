#!/usr/bin/env python3
"""
Larry Navigator - Modern Redesigned Streamlit Interface
User-Friendly Professional UI with Interactive Components
"""

import streamlit as st
import os
import json
from pathlib import Path
from datetime import datetime

# Import LangChain components
from larry_agent import initialize_larry_agent, chat_with_larry_agent, get_current_state

# Import existing utilities
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
                    os.environ[key.strip()] = value.strip()

def inject_css():
    """Load the modern CSS stylesheet"""
    css_path = Path(__file__).parent / "modern_larry_style.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def get_level_class(score):
    """Get CSS class based on score"""
    if score < 33:
        return "low"
    elif score < 67:
        return "medium"
    else:
        return "high"

def get_level_label(score):
    """Get label based on score"""
    if score < 33:
        return "LOW"
    elif score < 67:
        return "MEDIUM"
    else:
        return "HIGH"

# --- 2. Page Configuration ---

st.set_page_config(
    page_title="Larry - Your AI Thinking Partner",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment and inject CSS
load_env()
inject_css()

# --- 3. Session State Initialization ---

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0

# API Keys
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

# Initialize Agent
if "larry_agent_executor" not in st.session_state and st.session_state.anthropic_api_key:
    os.environ["ANTHROPIC_API_KEY"] = st.session_state.anthropic_api_key
    st.session_state.larry_agent_executor = initialize_larry_agent()

# State variables
if "persona" not in st.session_state:
    st.session_state.persona = "general"
if "problem_type" not in st.session_state:
    st.session_state.problem_type = "general"
if "uncertainty_score" not in st.session_state:
    st.session_state.uncertainty_score = 50
if "risk_score" not in st.session_state:
    st.session_state.risk_score = 50
if "clarity_score" not in st.session_state:
    st.session_state.clarity_score = 20

# --- 4. Sidebar ---

with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    # API Keys Section
    st.markdown("#### 🔑 API Keys")
    if st.session_state.anthropic_api_key:
        st.success("✅ Anthropic Claude Active")
    else:
        st.warning("⚠️ Claude API Key Required")
        api_key_input = st.text_input("Anthropic API Key", type="password", key="api_input")
        if api_key_input:
            st.session_state.anthropic_api_key = api_key_input
            os.environ["ANTHROPIC_API_KEY"] = api_key_input
            st.rerun()
    
    if st.session_state.exa_api_key:
        st.info("🔍 Web Search Enabled")
    else:
        st.info("💡 Web Search Optional")
        exa_input = st.text_input("Exa.ai API Key (Optional)", type="password", key="exa_input")
        if exa_input:
            st.session_state.exa_api_key = exa_input
            os.environ["EXA_API_KEY"] = exa_input
            st.rerun()
    
    st.markdown("---")
    
    # Persona Selector
    st.markdown("#### 🎭 Larry's Style")
    persona_options = {
        "Socratic Mentor": "Asks probing questions, rarely gives direct advice",
        "Strategic Advisor": "Balances questions with recommendations",
        "Devil's Advocate": "Challenges every assumption aggressively",
        "Supportive Coach": "Validates feelings while exploring options"
    }
    
    selected_persona = st.radio(
        "Choose interaction style:",
        options=list(persona_options.keys()),
        index=1,
        help="This affects how Larry responds to you"
    )
    
    with st.expander("ℹ️ What this means"):
        st.caption(persona_options[selected_persona])
    
    st.markdown("---")
    
    # Knowledge Sources
    st.markdown("#### 📚 Knowledge Sources")
    st.caption(f"File Search: {'✓ Active' if os.path.exists('larry_store_info.json') else '✗ Not configured'}")
    st.caption(f"Neo4j Graph: {'✓ Active' if is_neo4j_configured() else '✗ Not configured'}")
    st.caption(f"Web Search: {'✓ Active' if st.session_state.exa_api_key else '✗ Not configured'}")
    
    st.markdown("---")
    
    # Clear Chat
    if st.button("🗑️ Start New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_count = 0
        st.session_state.clarity_score = 20
        if "larry_agent_executor" in st.session_state:
            del st.session_state.larry_agent_executor
        st.rerun()

# --- 5. Main Content ---

# Header
st.markdown("""
<div class="modern-header">
    <h1>🎯 LARRY</h1>
    <p>Your AI Thinking Partner for Complex Decisions</p>
</div>
""", unsafe_allow_html=True)

# Update state from agent if available
if "larry_agent_executor" in st.session_state:
    current_state = get_current_state(st.session_state.larry_agent_executor)
    st.session_state.persona = current_state.get("persona", "general")
    st.session_state.problem_type = current_state.get("problem_type", "general")
    st.session_state.uncertainty_score = current_state.get("uncertainty_score", 50)
    st.session_state.risk_score = current_state.get("risk_score", 50)

# Dashboard Metrics Section
st.markdown("""
<div class="dashboard-section">
    <div class="dashboard-title">📊 Your Uncertainty Dashboard</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    uncertainty_level = get_level_class(st.session_state.uncertainty_score)
    uncertainty_label = get_level_label(st.session_state.uncertainty_score)
    st.markdown(f"""
    <div class="metric-card {uncertainty_level}-level">
        <div class="metric-icon">🌡️</div>
        <div class="metric-value">{st.session_state.uncertainty_score}%</div>
        <div class="metric-label">Uncertainty</div>
        <span class="metric-status {uncertainty_level}">{uncertainty_label}</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    risk_level = get_level_class(st.session_state.risk_score)
    risk_label = get_level_label(st.session_state.risk_score)
    st.markdown(f"""
    <div class="metric-card {risk_level}-level">
        <div class="metric-icon">⚠️</div>
        <div class="metric-value">{st.session_state.risk_score}%</div>
        <div class="metric-label">Risk Level</div>
        <span class="metric-status {risk_level}">{risk_label}</span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card low-level">
        <div class="metric-icon">💬</div>
        <div class="metric-value">{st.session_state.chat_count}</div>
        <div class="metric-label">Conversations</div>
        <span class="metric-status low">{'ACTIVE' if st.session_state.chat_count > 0 else 'START ONE!'}</span>
    </div>
    """, unsafe_allow_html=True)

# Quick Start Section (only show if no messages)
if not st.session_state.messages:
    st.markdown("""
    <div class="quick-start-section">
        <h2>🚀 Quick Start</h2>
        <p>Welcome! I'm Larry, your AI thinking partner.</p>
        <p>I help you navigate tough decisions by:</p>
        <ul>
            <li>✓ Challenging your assumptions (killer questions)</li>
            <li>✓ Exploring alternative perspectives</li>
            <li>✓ Mapping uncertainty in your decisions</li>
        </ul>
        <div class="suggestion-pills">
            <h3>💡 Try these to get started:</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Suggestion pills as buttons
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📝 Analyze a decision I'm facing", use_container_width=True):
            st.session_state.pill_input = "I need help analyzing a difficult decision I'm facing. Can you help me think through it?"
    with col_b:
        if st.button("🎯 Map stakeholders in a complex situation", use_container_width=True):
            st.session_state.pill_input = "I'm dealing with a complex situation involving multiple stakeholders. Can you help me map them out?"
    
    col_c, col_d = st.columns(2)
    with col_c:
        if st.button("🔍 Challenge my assumptions about X", use_container_width=True):
            st.session_state.pill_input = "I have some assumptions about my situation that I'd like you to challenge. Can we explore them?"
    with col_d:
        if st.button("🌊 Explore a wicked problem I'm stuck on", use_container_width=True):
            st.session_state.pill_input = "I'm stuck on a wicked problem with no clear solution. Can you help me explore it?"
    
    st.markdown('<p class="cta-text">Or just start typing below ↓</p>', unsafe_allow_html=True)

# Clarity Indicator (show if conversation has started)
if st.session_state.messages:
    clarity_percentage = min(100, st.session_state.clarity_score + (len(st.session_state.messages) * 5))
    st.session_state.clarity_score = clarity_percentage
    
    if clarity_percentage >= 75:
        status_html = '<span class="status-ready">✅ Ready to decide</span>'
    else:
        status_html = '<span class="status-exploring">⚠️ Key unknowns remain</span>'
    
    st.markdown(f"""
    <div class="clarity-indicator">
        <div class="clarity-header">
            <span>Current Clarity:</span>
            <span class="clarity-percentage">{clarity_percentage}%</span>
        </div>
        <div class="clarity-bar">
            <div class="clarity-progress" style="width: {clarity_percentage}%"></div>
        </div>
        <div class="clarity-status">
            {status_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Conversation Display
for idx, message in enumerate(st.session_state.messages):
    role = message["role"]
    content = message["content"]
    
    if role == "user":
        st.markdown(f"""
        <div class="message-card user-message">
            <div class="message-header">
                <span class="avatar">👤 YOU</span>
                <span class="timestamp">Just now</span>
            </div>
            <div class="message-content">
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="message-card larry-message">
            <div class="message-header">
                <span class="avatar">🎯 LARRY</span>
                <span class="timestamp">Just now</span>
            </div>
            <div class="message-content">
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)

# Chat Input
if st.session_state.anthropic_api_key:
    if "larry_agent_executor" not in st.session_state:
        st.info("🔄 Initializing Larry... Please wait.")
        st.rerun()
    
    # Check if pill was clicked
    user_input = None
    if "pill_input" in st.session_state:
        user_input = st.session_state.pill_input
        del st.session_state.pill_input
    else:
        user_input = st.chat_input("Ask Larry about your decision, problem, or uncertainty...")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.chat_count += 1
        
        # Show thinking indicator
        with st.spinner(""):
            st.markdown("""
            <div class="thinking-indicator">
                <span class="thinking-text">Larry is thinking</span>
                <span class="thinking-dots">
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            # Get response from agent
            response_text = chat_with_larry_agent(
                user_input=user_input,
                agent=st.session_state.larry_agent_executor
            )
        
        # Parse response
        try:
            structured_response = json.loads(response_text)
            final_answer = structured_response.get("final_answer", response_text)
            provocative_question = structured_response.get("provocative_question", "")
        except (json.JSONDecodeError, TypeError):
            final_answer = response_text
            provocative_question = ""
        
        # Add provocative question if present
        if provocative_question:
            with st.expander("💡 Provocative Question", expanded=True):
                st.markdown(f"**{provocative_question}**")
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": final_answer})
        
        st.rerun()
else:
    st.warning("👈 Please enter your Anthropic Claude API key in the sidebar to start chatting!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-secondary); padding: var(--spacing-md);">
    <strong>Larry - Your AI Thinking Partner</strong><br>
    Powered by Anthropic Claude & LangChain | Lawrence Aronhime's PWS Methodology
</div>
""", unsafe_allow_html=True)
