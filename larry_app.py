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

# --- 1. Utility Functions ---

# Load environment variables
def load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

# Load store info
def load_store_info():
    """Load File Search store information"""
    store_file = Path(__file__).parent / "larry_store_info.json"
    if store_file.exists():
        with open(store_file, 'r') as f:
            return json.load(f)
    return None

def detect_persona(message):
    """Detect user persona from message"""
    message_lower = message.lower()

    if any(word in message_lower for word in ['startup', 'founder', 'validate', 'customer', 'market fit']):
        return 'entrepreneur'
    elif any(word in message_lower for word in ['corporate', 'company', 'team', 'organization', 'portfolio']):
        return 'corporate'
    elif any(word in message_lower for word in ['exam', 'test', 'study', 'homework', 'course', 'assignment']):
        return 'student'
    elif any(word in message_lower for word in ['research', 'theory', 'literature', 'scholar', 'academic']):
        return 'researcher'
    elif any(word in message_lower for word in ['client', 'workshop', 'facilitate', 'advise', 'consult']):
        return 'consultant'
    else:
        return 'general'

def classify_problem_type(message):
    """Classify problem type from message context"""
    message_lower = message.lower()

    # Undefined (5-20 years, future-back)
    if any(word in message_lower for word in ['future', 'trend', 'macro', 'scenario', 'long-term', 'disrupt']):
        return 'undefined', 0  # 0-33% on timeline

    # Ill-Defined (1-5 years, present-forward)
    elif any(word in message_lower for word in ['opportunity', 'near-term', 'adjacent', 'expansion', 'growth']):
        return 'ill-defined', 50  # 34-66% on timeline

    # Well-Defined (<1 year, execute now)
    elif any(word in message_lower for word in ['implement', 'build', 'execute', 'prototype', 'mvp', 'solution']):
        return 'well-defined', 85  # 67-100% on timeline

    else:
        return 'general', 50  # Default to middle

def parse_response_for_message_types(response_text):
    """
    Parse Larry's response and identify message types.
    Simplified from 7 to 3 core types for minimal design.
    """
    messages = []

    # Split by common patterns
    sections = response_text.split('\n\n')

    for section in sections:
        if not section.strip():
            continue

        # Type 3: Accent Block (Provocative, Framework, Action)
        if any(phrase in section for phrase in ['?', 'Suppose', 'What if', 'Think about', 'Do not misunderstand', 'Action:', 'Next step:', 'In the next', 'Try this:', 'Framework', 'Tool', 'Model', 'Method']):
            messages.append(('accent', section))

        # Type 2: Regular assistant message
        else:
            messages.append(('regular', section))

    return messages

def render_message(message_type, content):
    """Render message based on simplified type"""
    if message_type == 'accent':
        # Use st.expander for long accent blocks to improve UX (Response UX)
        with st.expander("💡 Key Insight / Action Item", expanded=True):
            st.markdown(f'<div class="accent-block">{content}</div>', unsafe_allow_html=True)
        return "" # Return empty string as content is rendered in expander

    else:  # regular
        # Use st.chat_message for regular messages
        with st.chat_message("assistant"):
            st.markdown(content)
        return ""

def chat_with_larry(user_message, api_key, store_info, persona, problem_type, exa_api_key=None):
    """Send message to Larry using File Search + Exa.ai web search"""
    try:
        client = genai.Client(api_key=api_key)

        # Check if web search is needed and perform Exa search
        search_results = None
        if exa_api_key:
            # Show progress for web search (Performance Perception)
            with st.spinner("🔍 Searching latest research..."):
                search_results = integrate_search_with_response(
                    user_message=user_message,
                    persona=persona,
                    problem_type=problem_type,
                    exa_api_key=exa_api_key
                )

        # Enhance prompt with detected context and search results
        enhanced_prompt = f"""{LARRY_SYSTEM_PROMPT}

**DETECTED CONTEXT:**
- User Persona: {persona}
- Problem Type: {problem_type}

Adapt your response accordingly! Use appropriate frameworks and language for this persona and problem type.
"""

        # Add search results to context if available
        if search_results:
            enhanced_prompt += f"\n\n**CURRENT WEB RESEARCH:**\n{search_results}\n\nIntegrate these cutting-edge findings into your response with proper citations."

        # Build conversation with File Search
        tools_config = []
        if store_info:
            tools_config.append(
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[store_info['store_name']]
                    )
                )
            )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=enhanced_prompt,
                tools=tools_config,
                temperature=0.7,
                top_p=0.95,
            )
        )

        # Combine search results with Larry's response
        full_response = ""
        if search_results:
            # Use a collapsible section for search results
            full_response += f"**[SEARCH RESULTS]**\n{search_results}\n\n---\n\n"

        if response and response.text:
            full_response += response.text
            return full_response
        else:
            return "I'm sorry, I couldn't generate a response. Could you rephrase your question?"

    except Exception as e:
        return f"Error: {str(e)}"

# --- 2. Streamlit App Setup ---

# Inject minimal De Stijl CSS
def inject_css():
    css_path = Path(__file__).parent / "minimal_destijl_style.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

inject_css()

# Page configuration (Single-column, responsive layout)
st.set_page_config(
    page_title="Larry - Your Personal Uncertainty Navigator",
    page_icon="🎯",
    layout="centered", # Use centered layout for better mobile experience
    initial_sidebar_state="expanded"
)

# Import system prompt
from larry_system_prompt_v3 import LARRY_SYSTEM_PROMPT_V3
LARRY_SYSTEM_PROMPT = LARRY_SYSTEM_PROMPT_V3

# --- 3. Session State Initialization ---

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'api_key' not in st.session_state:
    try:
        st.session_state.api_key = st.secrets.get("GOOGLE_AI_API_KEY", os.getenv('GOOGLE_AI_API_KEY'))
    except:
        st.session_state.api_key = os.getenv('GOOGLE_AI_API_KEY')

if 'exa_api_key' not in st.session_state:
    try:
        st.session_state.exa_api_key = st.secrets.get("EXA_API_KEY", os.getenv('EXA_API_KEY'))
    except:
        st.session_state.exa_api_key = os.getenv('EXA_API_KEY')

if 'persona' not in st.session_state:
    st.session_state.persona = 'general'

if 'problem_type' not in st.session_state:
    st.session_state.problem_type = 'general'

if 'uncertainty_score' not in st.session_state:
    st.session_state.uncertainty_score = 50

if 'risk_score' not in st.session_state:
    st.session_state.risk_score = 50

if 'uncertainty_level' not in st.session_state:
    st.session_state.uncertainty_level = 'medium'

if 'risk_level' not in st.session_state:
    st.session_state.risk_level = 'medium'

if 'recommended_frameworks' not in st.session_state:
    st.session_state.recommended_frameworks = []

# --- 4. Sidebar (Simplified Left Panel) ---

with st.sidebar:
    st.markdown("### ⚙️ Configuration & Context")

    # 1. Simplified Persona Indicator
    st.markdown("#### 🎭 Persona")
    st.markdown(f'<div class="minimal-persona-badge">{st.session_state.persona.upper()}</div>', unsafe_allow_html=True)

    # 2. Simplified Uncertainty/Risk Tracker (Reduced to 2-3 key indicators)
    st.markdown("#### ⚖️ Uncertainty & Risk")
    st.markdown(f"""
    <div class="minimal-indicator">
        Uncertainty: <span>{st.session_state.uncertainty_score}%</span> ({st.session_state.uncertainty_level.upper()})
    </div>
    <div class="minimal-indicator">
        Risk: <span>{st.session_state.risk_score}%</span> ({st.session_state.risk_level.upper()})
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 3. API Key Configuration (Simplified)
    st.markdown("#### 🔑 API Keys")

    # Google AI API Key
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

    # Exa API Key
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

    # Knowledge Base Status
    store_info = load_store_info()
    if store_info:
        st.caption(f"📚 Knowledge Base: Active ({store_info.get('total_chunks', '2,988')} chunks)")
    else:
        st.caption("⚠️ File Search not configured")

    st.markdown("---")

    # 4. Opt-In Framework Recommendations (Right Panel content moved here)
    st.markdown("#### 🧭 Frameworks")
    with st.expander("View Recommended Frameworks", expanded=False):
        if st.session_state.recommended_frameworks:
            for framework in st.session_state.recommended_frameworks:
                st.markdown(f"""
                **{framework['name']}**
                <small>{framework['description']}</small>
                """, unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("No specific frameworks recommended yet. Start a conversation!")

    # 5. Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.persona = 'general'
        st.session_state.problem_type = 'general'
        st.rerun()

# --- 5. Main Content (Single Column Chat) ---

# Header
st.markdown("""
<div class="destijl-header">
    <h1>🎯 LARRY</h1>
    <p>Your Personal Uncertainty Navigator</p>
</div>
""", unsafe_allow_html=True)

# Onboarding (Welcome Message)
if not st.session_state.messages:
    st.markdown("""
    <div class="accent-block">
        <h3>Welcome to Larry, the Hyper-Minimal Uncertainty Navigator.</h3>
        <p>I'm here to help you structure ill-defined problems. Start by asking a question about innovation, strategy, or problem-solving.</p>
        <p>Your persona and problem type will be automatically detected and displayed in the sidebar. Advanced features like framework recommendations are now opt-in, accessible via the sidebar.</p>
    </div>
    """, unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    else:
        # Parse and render message types
        parsed_messages = parse_response_for_message_types(message["content"])
        for msg_type, msg_content in parsed_messages:
            # Render message handles the logic for st.chat_message and st.expander
            render_message(msg_type, msg_content)

# Chat input
if st.session_state.api_key:
    user_input = st.chat_input("Ask Larry about innovation, problem-solving, or PWS methodology...")

    if user_input:
        # Detect persona and problem type
        st.session_state.persona = detect_persona(user_input)
        problem_type, position = classify_problem_type(user_input)
        st.session_state.problem_type = problem_type

        # Calculate uncertainty and risk
        uncertainty_level, risk_level, uncertainty_score, risk_score = calculate_uncertainty_risk(
            problem_type, user_input
        )
        st.session_state.uncertainty_level = uncertainty_level
        st.session_state.risk_level = risk_level
        st.session_state.uncertainty_score = uncertainty_score
        st.session_state.risk_score = risk_score

        # Recommend frameworks
        st.session_state.recommended_frameworks = recommend_frameworks(
            problem_type,
            st.session_state.persona,
            user_input,
            max_recommendations=3
        )

        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Get Larry's response
        with st.spinner("🤔 Larry is thinking..."):
            store_info = load_store_info()
            response = chat_with_larry(
                user_input,
                st.session_state.api_key,
                store_info,
                st.session_state.persona,
                st.session_state.problem_type,
                st.session_state.exa_api_key
            )

        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Rerun to display new messages
        st.rerun()
else:
    st.info("👈 Please enter your Google AI API key in the sidebar to start chatting!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <strong>Larry - Your Personal Uncertainty Navigator</strong><br>
    Powered by Google Gemini 2.5 Flash | Lawrence Aronhime's PWS Methodology
</div>
""", unsafe_allow_html=True)
