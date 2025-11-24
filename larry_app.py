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
    """Load the dark theme CSS stylesheet"""
    css_path = Path(__file__).parent / "dark_theme_style.css"
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
    page_title="Larry | PWS Navigator",
    page_icon="🎯",
    layout="centered",
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

if "tavily_api_key" not in st.session_state:
    try:
        st.session_state.tavily_api_key = st.secrets.get("TAVILY_API_KEY", os.getenv("TAVILY_API_KEY"))
    except Exception as e:
        print(f"⚠️ Failed to load TAVILY_API_KEY from secrets: {str(e)}")
        st.session_state.tavily_api_key = os.getenv("TAVILY_API_KEY")

# Set TAVILY_API_KEY in environment if available
if st.session_state.tavily_api_key:
    os.environ["TAVILY_API_KEY"] = st.session_state.tavily_api_key

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
    
    if st.session_state.tavily_api_key:
        st.info("🔍 Tavily AI Search Enabled")
    else:
        st.info("💡 Web Search Optional")
        tavily_input = st.text_input("Tavily AI API Key (Optional)", type="password", key="tavily_input")
        if tavily_input:
            st.session_state.tavily_api_key = tavily_input
            os.environ["TAVILY_API_KEY"] = tavily_input
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
    
    st.caption(f"Tavily AI Search: {'✓ Active' if st.session_state.tavily_api_key else '✗ Not configured'}")

    st.markdown("---")

    # Problem Type Classification
    st.markdown("#### 📊 Problem Classification")

    # Determine active problem type based on session state
    problem_type = st.session_state.problem_type
    undefined_active = "active" if problem_type == "undefined" else ""
    ill_defined_active = "active" if problem_type == "ill-defined" else ""
    well_defined_active = "active" if problem_type == "well-defined" else ""

    st.markdown(f"""
    <div class="problem-indicator">
        <div class="problem-type undefined {undefined_active}">
            ◉ Un-defined
        </div>
        <div class="problem-type ill-defined {ill_defined_active}">
            ○ Ill-defined
        </div>
        <div class="problem-type well-defined {well_defined_active}">
            ○ Well-defined
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Reasoning Display Toggle
    st.markdown("#### 🧠 Display Options")

    if "show_thinking" not in st.session_state:
        st.session_state.show_thinking = True

    show_thinking = st.checkbox(
        "Show Larry's reasoning process",
        value=st.session_state.show_thinking,
        help="Display step-by-step thinking and sources used"
    )

    if show_thinking != st.session_state.show_thinking:
        st.session_state.show_thinking = show_thinking

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

# Header - Dark Theme with PWS Philosophy
st.markdown("""
<div class="larry-header">
    <div class="larry-title">🎯 Larry</div>
    <div class="larry-subtitle">Your PWS Innovation Mentor</div>
    <div style="margin-top: 1rem;">
        <span class="pws-badge badge-real">● Real</span>
        <span class="pws-badge badge-winnable">● Winnable</span>
        <span class="pws-badge badge-worth">● Worth It</span>
    </div>
</div>
""", unsafe_allow_html=True)

# State is managed by the app, not extracted from agent

# Session Stats (only show if there are messages)
if len(st.session_state.messages) > 0:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stat-value">{st.session_state.chat_count}</div>
            <div class="stat-label">Messages</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Count frameworks mentioned (placeholder logic)
        frameworks_count = sum(1 for msg in st.session_state.messages if msg["role"] == "assistant" and len(msg["content"]) > 200)
        st.markdown(f"""
        <div class="stats-card">
            <div class="stat-value">{frameworks_count}</div>
            <div class="stat-label">Frameworks</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        problem_label = st.session_state.problem_type.replace("-", " ").title() if st.session_state.problem_type != "general" else "Exploring"
        st.markdown(f"""
        <div class="stats-card">
            <div class="stat-value" style="font-size: 1.25rem; text-transform: capitalize;">{problem_label}</div>
            <div class="stat-label">Problem Type</div>
        </div>
        """, unsafe_allow_html=True)

# Welcome Message (only show if no messages)
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="framework-card">
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="color: var(--text-primary); margin-bottom: 1rem;">Welcome. I'm Larry.</h2>
        </div>

        <p style="color: var(--text-secondary); font-size: 1.05rem; line-height: 1.8;">
            Let me challenge your thinking from the start: <em style="color: var(--challenge);">What problem brought you here today?</em>
        </p>

        <p style="color: var(--text-secondary); margin-top: 1rem;">
            Notice I didn't ask about your <em>idea</em>, your <em>product</em>, or your <em>business plan</em>. That's intentional.
        </p>

        <div style="background: rgba(244, 63, 94, 0.1); padding: 1rem; border-radius: 8px; border-left: 3px solid var(--challenge); margin: 1.5rem 0;">
            <p style="color: var(--text-primary); font-weight: 500; margin: 0;">
                <strong>Here's what most people miss:</strong> Innovation doesn't start with ideas.
                It starts with <span style="color: var(--challenge);">problems worth solving</span>.
            </p>
        </div>

        <p style="color: var(--text-secondary); font-weight: 500; margin-bottom: 0.5rem;">
            A problem worth solving meets three criteria:
        </p>

        <div style="display: grid; gap: 0.75rem; margin: 1rem 0;">
            <div style="display: flex; align-items: start; gap: 0.75rem; padding: 0.75rem; background: rgba(255, 107, 53, 0.1); border-radius: 6px;">
                <span style="color: var(--pws-real); font-size: 1.5rem;">🔥</span>
                <div>
                    <strong style="color: var(--pws-real);">Real</strong>
                    <span style="color: var(--text-muted); margin-left: 0.5rem;">— People actually experience this pain</span>
                </div>
            </div>

            <div style="display: flex; align-items: start; gap: 0.75rem; padding: 0.75rem; background: rgba(0, 217, 165, 0.1); border-radius: 6px;">
                <span style="color: var(--pws-winnable); font-size: 1.5rem;">🎯</span>
                <div>
                    <strong style="color: var(--pws-winnable);">Winnable</strong>
                    <span style="color: var(--text-muted); margin-left: 0.5rem;">— A solution is feasible within your constraints</span>
                </div>
            </div>

            <div style="display: flex; align-items: start; gap: 0.75rem; padding: 0.75rem; background: rgba(255, 217, 61, 0.1); border-radius: 6px;">
                <span style="color: var(--pws-worth); font-size: 1.5rem;">💎</span>
                <div>
                    <strong style="color: var(--pws-worth);">Worth It</strong>
                    <span style="color: var(--text-muted); margin-left: 0.5rem;">— The value of solving exceeds the cost</span>
                </div>
            </div>
        </div>

        <p style="color: var(--text-secondary); margin-top: 1.5rem;">
            So, what's the problem you're wrestling with? Or if you're not sure yet — that's exactly where we should start.
        </p>

        <p style="color: var(--text-larry); font-style: italic; text-align: center; margin-top: 1.5rem; font-size: 0.95rem;">
            The best questions begin in uncertainty.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Chat Messages - Using native Streamlit components (styled by CSS)
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]

    with st.chat_message(role):
        st.markdown(content)

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
            # Clear status message
            status_msg.empty()

            # Create a placeholder for streaming response
            response_placeholder = st.empty()
            response_chunks = []

            # Stream response chunks incrementally
            for chunk in st.session_state.larry_chat_handler.chat(
                message_text,
                conversation_history=st.session_state.messages,
                show_thinking=st.session_state.get("show_thinking", True)
            ):
                response_chunks.append(chunk)
                # Update display with accumulated response
                current_response = "".join(response_chunks)
                response_placeholder.markdown(f"""
                <div class="message-card larry-message">
                    <div class="message-header">
                        <span class="message-avatar">🎯 LARRY</span>
                        <span class="message-time">{datetime.now().strftime("%H:%M")}</span>
                    </div>
                    <div class="message-content">{current_response}</div>
                </div>
                """, unsafe_allow_html=True)

            # Final response
            response = "".join(response_chunks)

            # Clear streaming placeholder
            response_placeholder.empty()

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
