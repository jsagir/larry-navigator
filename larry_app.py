"""
Larry Navigator - Modern Redesigned Streamlit Interface
User-Friendly Professional UI with Interactive Components
Version: 4.0.1
"""

import streamlit as st
import os
import json
from pathlib import Path
from datetime import datetime

# --- CRITICAL: Load secrets FIRST before any other imports ---

# Global flag to track secrets loading status
secrets_loaded = False
secrets_error = None

def set_secrets_as_env():
    """Reads st.secrets and sets them as environment variables for LangChain tools."""
    global secrets_loaded, secrets_error
    try:
        for key, value in st.secrets.items():
            if key not in os.environ:
                os.environ[key] = str(value)
        secrets_loaded = True
        print("✅ Secrets loaded successfully from Streamlit Cloud")
    except Exception as e:
        secrets_error = str(e)
        secrets_loaded = False
        print(f"⚠️ Secrets loading failed: {secrets_error}")
        print("📝 App will continue with manual API key entry")
        # Don't crash - app can still work with manual API key entry

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

# Load environment variables BEFORE importing other modules
load_env()
set_secrets_as_env()

# NOW import chat components (after secrets are loaded)
from larry_chat import create_chat_handler
from larry_router import route_query, get_route_description
from larry_neo4j_rag import is_neo4j_configured, is_faiss_configured
from larry_config import CLARITY_BASE_SCORE, CLARITY_INCREMENT_PER_MESSAGE, CLARITY_READY_THRESHOLD
from larry_security import sanitize_user_input, check_rate_limit

# --- 1. Utility Functions ---

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

# Inject CSS
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
    except Exception as e:
        print(f"⚠️ Failed to load ANTHROPIC_API_KEY from secrets: {str(e)}")
        st.session_state.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

if "exa_api_key" not in st.session_state:
    try:
        st.session_state.exa_api_key = st.secrets.get("EXA_API_KEY", os.getenv("EXA_API_KEY"))
    except Exception as e:
        print(f"⚠️ Failed to load EXA_API_KEY from secrets: {str(e)}")
        st.session_state.exa_api_key = os.getenv("EXA_API_KEY")

# Set EXA_API_KEY in environment if available
if st.session_state.exa_api_key:
    os.environ["EXA_API_KEY"] = st.session_state.exa_api_key

# Initialize chat handler on startup
if "larry_chat_handler" not in st.session_state:
    st.session_state.larry_chat_handler = create_chat_handler()

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
    st.session_state.clarity_score = CLARITY_BASE_SCORE

# --- 4. Sidebar Configuration ---

with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # Show warning if secrets failed to load
    if not secrets_loaded and secrets_error:
        st.warning("⚠️ **Secrets Configuration Issue**")
        with st.expander("ℹ️ Click for details"):
            st.caption(f"Secrets file has a syntax error. Using manual API key entry instead.")
            st.caption(f"To fix: Go to Streamlit Cloud → Settings → Secrets and check TOML syntax.")
    
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
    
    # Check Neo4j configuration
    neo4j_status = is_neo4j_configured()
    st.caption(f"Neo4j Graph: {'✓ Active' if neo4j_status else '✗ Not configured'}")
    
    st.caption(f"Web Search: {'✓ Active' if st.session_state.exa_api_key else '✗ Not configured'}")
    
    st.markdown("---")
    
    # Clear Chat
    if st.button("🗑️ Start New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_count = 0
        st.session_state.clarity_score = CLARITY_BASE_SCORE
        # Reinitialize chat handler for fresh conversation
        st.session_state.larry_chat_handler = create_chat_handler()
        st.rerun()

# --- 5. Main Content ---

# Header
st.markdown("""
<div class="modern-header">
    <h1>🎯 LARRY</h1>
    <p>Your AI Thinking Partner for Complex Decisions</p>
</div>
""", unsafe_allow_html=True)

# State is managed by the app, not extracted from agent

# Dashboard Metrics Section
st.markdown("""
<div class="dashboard-container">
    <h2>📊 Your Uncertainty Dashboard</h2>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    uncertainty_class = get_level_class(st.session_state.uncertainty_score)
    st.markdown(f"""
    <div class="metric-card {uncertainty_class}">
        <div class="metric-icon">🌡️</div>
        <div class="metric-value">{st.session_state.uncertainty_score}%</div>
        <div class="metric-label">Uncertainty</div>
        <div class="metric-status">{get_level_label(st.session_state.uncertainty_score)}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    risk_class = get_level_class(st.session_state.risk_score)
    st.markdown(f"""
    <div class="metric-card {risk_class}">
        <div class="metric-icon">⚠️</div>
        <div class="metric-value">{st.session_state.risk_score}%</div>
        <div class="metric-label">Risk Level</div>
        <div class="metric-status">{get_level_label(st.session_state.risk_score)}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">💬</div>
        <div class="metric-value">{st.session_state.chat_count}</div>
        <div class="metric-label">Conversations</div>
        <div class="metric-status">{'START ONE!' if st.session_state.chat_count == 0 else 'ACTIVE'}</div>
    </div>
    """, unsafe_allow_html=True)

# Quick Start Section (only show if no messages)
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="quick-start-container">
        <h3>🚀 Quick Start</h3>
        <p>Welcome! I'm Larry, your AI thinking partner.</p>
        <p>I help you navigate tough decisions by:</p>
        <ul>
            <li>✓ Challenging your assumptions (killer questions)</li>
            <li>✓ Exploring alternative perspectives</li>
            <li>✓ Mapping uncertainty in your decisions</li>
        </ul>
        <p class="quick-start-hint">💡 Try these to get started:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Suggestion pills
    col1, col2, col3, col4 = st.columns(4)
    suggestions = [
        "I'm facing a tough decision about...",
        "Help me think through...",
        "What am I not considering about...",
        "Challenge my assumptions on..."
    ]
    
    for col, suggestion in zip([col1, col2, col3, col4], suggestions):
        with col:
            if st.button(suggestion, key=f"suggest_{suggestion[:10]}", use_container_width=True):
                st.session_state.quick_start_text = suggestion
    
    st.markdown('<p class="quick-start-hint">Or just start typing below ↓</p>', unsafe_allow_html=True)

# Clarity Indicator
if st.session_state.chat_count > 0:
    clarity_percent = min(100, st.session_state.clarity_score)
    clarity_status = "Ready to decide" if clarity_percent >= CLARITY_READY_THRESHOLD else "Key unknowns remain"
    
    st.markdown(f"""
    <div class="clarity-indicator">
        <div class="clarity-label">Decision Clarity: {clarity_percent}%</div>
        <div class="clarity-bar">
            <div class="clarity-fill" style="width: {clarity_percent}%"></div>
        </div>
        <div class="clarity-status">{clarity_status}</div>
    </div>
    """, unsafe_allow_html=True)

# Chat Messages
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", "")
    
    if role == "user":
        st.markdown(f"""
        <div class="message-card user-message">
            <div class="message-header">
                <span class="message-avatar">👤 YOU</span>
                <span class="message-time">{timestamp}</span>
            </div>
            <div class="message-content">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="message-card larry-message">
            <div class="message-header">
                <span class="message-avatar">🎯 LARRY</span>
                <span class="message-time">{timestamp}</span>
            </div>
            <div class="message-content">{content}</div>
        </div>
        """, unsafe_allow_html=True)

# Chat Input
if True:  # No API key required for Gemini (uses GOOGLE_AI_API_KEY from secrets)
    # Check if there's a quick start suggestion
    default_text = st.session_state.get("quick_start_text", "")
    if default_text:
        del st.session_state.quick_start_text
    
    user_input = st.chat_input("Type your message here...", key="chat_input")
    
    if user_input or default_text:
        message_text = user_input if user_input else default_text
        
        # 1. Check rate limit
        is_allowed, rate_limit_msg = check_rate_limit(st.session_state, max_messages=10, time_window=60)
        if not is_allowed:
            st.error(rate_limit_msg)
            st.stop()
        
        # 2. Sanitize input
        sanitized_text, sanitize_warning = sanitize_user_input(message_text)
        if sanitize_warning:
            st.error(f"⚠️ **Input Error:** {sanitize_warning}")
            st.stop()
        
        message_text = sanitized_text
        
        # Add user message
        timestamp = datetime.now().strftime("%H:%M")
        st.session_state.messages.append({
            "role": "user",
            "content": message_text,
            "timestamp": timestamp
        })
        
        # Detect route and show appropriate status
        route = route_query(message_text)
        route_desc = get_route_description(route)
        
        # Show status message
        status_msg = st.empty()
        status_msg.info(route_desc)
        
        try:
            # Collect response chunks
            response_chunks = []
            for chunk in st.session_state.larry_chat_handler.chat(
                message_text,
                conversation_history=st.session_state.messages
            ):
                response_chunks.append(chunk)
            
            # Clear status and show complete response
            status_msg.empty()
            response = "".join(response_chunks)
            
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            print(f"❌ Chat execution failed: [{error_type}] {error_msg}")
            status_msg.empty()
            response = f"⚠️ **Chat Error**\n\n[{error_type}] {error_msg}\n\n**Possible solutions:**\n- Try rephrasing your message\n- Start a new conversation (refresh the page)\n- Check your API credentials\n\nIf the problem persists, please contact support."
        
        # Add assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().strftime("%H:%M")
        })
        
        # Update chat count and clarity
        st.session_state.chat_count += 1
        st.session_state.clarity_score = min(100, CLARITY_BASE_SCORE + (st.session_state.chat_count * CLARITY_INCREMENT_PER_MESSAGE))
        
        st.rerun()
else:
    st.info("💬 Start chatting! Gemini file search is ready.")

# Footer
st.markdown("""
<div class="footer">
    <p>Larry - Your AI Thinking Partner</p>
    <p>Powered by Anthropic Claude & LangChain | Lawrence Aronhime's PWS Methodology</p>
</div>
""", unsafe_allow_html=True)
