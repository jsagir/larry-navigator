#!/usr/bin/env python3
"""
Larry Navigator - Streamlit Web Interface
De Stijl-Inspired Design with Visual Encoding
"""

import streamlit as st
import os
import re
from pathlib import Path
from google import genai
from google.genai import types
import json
from larry_web_search import integrate_search_with_response

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

# Page configuration
st.set_page_config(
    page_title="Larry - Your Personal Uncertainty Navigator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# De Stijl CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

    /* Global styling */
    * {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    /* Main container */
    .main {
        background: #FFFFFF;
    }

    /* De Stijl Header */
    .destijl-header {
        background: linear-gradient(90deg, #FFFFFF 0%, #FFFFFF 75%, #E30613 75%, #E30613 100%);
        border-left: 16px solid #000000;
        border-bottom: 6px solid #000000;
        padding: 2.5rem 2rem 2.5rem 3rem;
        margin-bottom: 2rem;
    }

    .destijl-header h1 {
        color: #000000;
        font-weight: 700;
        font-size: 3rem;
        margin: 0;
        line-height: 1;
        letter-spacing: -0.02em;
    }

    .destijl-header p {
        color: #333333;
        font-size: 1.2rem;
        margin-top: 1rem;
        font-weight: 400;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #F8F8F8;
        border-right: 6px solid #000000;
    }

    /* MESSAGE TYPE 1: Provocative Questions (RED BLOCKS) */
    .provocative-question {
        background: #E30613;
        color: #FFFFFF;
        border-left: 12px solid #000000;
        padding: 24px 28px;
        margin: 1.5rem 0;
        font-weight: 700;
        font-size: 1.3em;
        line-height: 1.4;
        box-shadow: 8px 8px 0 #000000;
        border-radius: 0;
    }

    .provocative-question::before {
        content: "❓ PROVOCATIVE QUESTION";
        display: block;
        font-size: 0.7em;
        font-weight: 600;
        letter-spacing: 0.1em;
        margin-bottom: 12px;
        opacity: 0.9;
    }

    /* MESSAGE TYPE 2: Framework Blocks (BLUE BLOCKS) */
    .framework-block {
        background: #0066CC;
        color: #FFFFFF;
        border: 4px solid #000000;
        padding: 24px;
        margin: 1.5rem 0;
        box-shadow: 6px 6px 0 #000000;
    }

    .framework-block h3 {
        color: #FFD700;
        font-weight: 700;
        font-size: 1.3em;
        margin: 0 0 16px 0;
        border-bottom: 3px solid #FFD700;
        padding-bottom: 8px;
    }

    .framework-block::before {
        content: "🧭 FRAMEWORK";
        display: block;
        font-size: 0.75em;
        font-weight: 600;
        letter-spacing: 0.1em;
        margin-bottom: 12px;
        color: #FFD700;
    }

    /* MESSAGE TYPE 3: Action Blocks (YELLOW BLOCKS) */
    .action-block {
        background: #FFD700;
        color: #000000;
        border-right: 12px solid #000000;
        border-top: 4px solid #000000;
        padding: 20px 24px;
        margin: 1.5rem 0;
        font-weight: 600;
        box-shadow: -6px 6px 0 #000000;
    }

    .action-block::before {
        content: "⚡ ACTION REQUIRED";
        display: block;
        font-size: 0.75em;
        font-weight: 700;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
        color: #E30613;
    }

    .action-time {
        font-family: 'IBM Plex Mono', monospace;
        background: #000000;
        color: #FFD700;
        padding: 4px 12px;
        display: inline-block;
        margin-top: 12px;
        font-size: 0.9em;
        font-weight: 600;
    }

    /* MESSAGE TYPE 4: Diagnostic Questions (WHITE WITH ACCENT) */
    .diagnostic-block {
        background: #FFFFFF;
        color: #000000;
        border-left: 8px solid #0066CC;
        border-top: 3px solid #000000;
        padding: 20px 24px;
        margin: 1.5rem 0;
        box-shadow: 4px 4px 0 rgba(0,0,0,0.15);
    }

    .diagnostic-block::before {
        content: "🔍 DIAGNOSTIC";
        display: block;
        font-size: 0.75em;
        font-weight: 700;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
        color: #0066CC;
    }

    /* MESSAGE TYPE 5: Search Results (BLUE-WHITE GRID) */
    .search-results {
        background: #FFFFFF;
        border: 4px solid #0066CC;
        padding: 20px;
        margin: 1.5rem 0;
    }

    .search-results .source {
        background: #0066CC;
        color: #FFFFFF;
        padding: 8px 16px;
        font-weight: 700;
        font-size: 0.9em;
        margin-bottom: 12px;
        display: inline-block;
    }

    .search-results .findings {
        padding: 16px;
        border-left: 4px solid #FFD700;
        background: #F8F8F8;
        margin: 12px 0;
    }

    .search-results .insight {
        background: #FFD700;
        color: #000000;
        padding: 12px 16px;
        font-weight: 600;
        border-left: 4px solid #000000;
    }

    /* MESSAGE TYPE 6: Case Stories (RED-YELLOW SPLIT) */
    .case-story {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 0;
        border: 4px solid #000000;
        margin: 1.5rem 0;
        box-shadow: 6px 6px 0 #000000;
    }

    .case-story .story {
        background: #FFFFFF;
        padding: 20px;
        border-right: 4px solid #000000;
    }

    .case-story .lesson {
        background: #E30613;
        color: #FFFFFF;
        padding: 20px;
        font-weight: 700;
        display: flex;
        align-items: center;
    }

    .case-story .lesson::before {
        content: "💡 LESSON";
        display: block;
        font-size: 0.75em;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
    }

    /* MESSAGE TYPE 7: Regular User/Assistant Messages */
    .user-message {
        background: #F8F8F8;
        border-left: 6px solid #000000;
        border-radius: 0;
        padding: 16px 20px;
        margin: 1rem 0;
        color: #000000;
        font-weight: 500;
    }

    .user-message::before {
        content: "💬 YOU";
        display: block;
        font-size: 0.7em;
        font-weight: 700;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
        color: #666666;
    }

    .assistant-message {
        background: #FFFFFF;
        border-left: 6px solid #0066CC;
        border-top: 2px solid #000000;
        padding: 20px 24px;
        margin: 1rem 0;
        color: #1a1a1a;
        line-height: 1.7;
        box-shadow: 3px 3px 0 rgba(0,0,0,0.1);
    }

    .assistant-message::before {
        content: "🎓 LARRY";
        display: block;
        font-size: 0.7em;
        font-weight: 700;
        letter-spacing: 0.1em;
        margin-bottom: 12px;
        color: #0066CC;
    }

    /* Persona Badge */
    .persona-badge {
        background: #000000;
        color: #FFFFFF;
        padding: 12px 20px;
        font-weight: 700;
        font-size: 1.1em;
        margin-bottom: 1.5rem;
        border-left: 8px solid #E30613;
        box-shadow: 4px 4px 0 #E30613;
    }

    .persona-badge.entrepreneur {
        border-left-color: #E30613;
        box-shadow: 4px 4px 0 #E30613;
    }

    .persona-badge.corporate {
        border-left-color: #0066CC;
        box-shadow: 4px 4px 0 #0066CC;
    }

    .persona-badge.student {
        border-left-color: #FFD700;
        box-shadow: 4px 4px 0 #FFD700;
    }

    .persona-badge.researcher {
        border-left-color: #FFFFFF;
        box-shadow: 4px 4px 0 #FFFFFF;
    }

    /* Problem Type Timeline */
    .problem-timeline {
        background: #F8F8F8;
        padding: 20px;
        border: 3px solid #000000;
        margin: 1.5rem 0;
    }

    .problem-timeline h4 {
        margin: 0 0 16px 0;
        font-size: 0.9em;
        letter-spacing: 0.1em;
        color: #000000;
    }

    .timeline-bar {
        position: relative;
        height: 60px;
        background: linear-gradient(90deg, #E30613 0%, #E30613 33%, #FFD700 33%, #FFD700 66%, #0066CC 66%, #0066CC 100%);
        border: 3px solid #000000;
    }

    .timeline-labels {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 8px;
        margin-top: 12px;
        font-size: 0.8em;
        font-weight: 600;
    }

    .timeline-label {
        text-align: center;
        padding: 8px;
        background: #FFFFFF;
        border: 2px solid #000000;
    }

    /* Portfolio Balance Tracker */
    .portfolio-tracker {
        background: #FFFFFF;
        padding: 20px;
        border: 4px solid #000000;
        margin: 1.5rem 0;
    }

    .portfolio-tracker h4 {
        margin: 0 0 16px 0;
        font-size: 0.9em;
        letter-spacing: 0.1em;
    }

    .portfolio-grid {
        display: grid;
        grid-template-rows: auto auto auto;
        gap: 4px;
        background: #000000;
        padding: 4px;
    }

    .portfolio-item {
        padding: 12px;
        color: #FFFFFF;
        font-weight: 600;
        font-size: 0.9em;
    }

    .portfolio-item.now {
        background: #0066CC;
    }

    .portfolio-item.new {
        background: #FFD700;
        color: #000000;
    }

    .portfolio-item.next {
        background: #E30613;
    }

    /* Context Panel Styling */
    .context-panel {
        background: #F8F8F8;
        padding: 20px;
        border: 3px solid #000000;
        margin-bottom: 1.5rem;
    }

    .context-panel h4 {
        margin: 0 0 12px 0;
        font-size: 0.9em;
        letter-spacing: 0.1em;
        color: #000000;
        border-bottom: 3px solid #000000;
        padding-bottom: 8px;
    }

    .context-panel ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .context-panel li {
        padding: 8px 12px;
        margin: 4px 0;
        background: #FFFFFF;
        border-left: 4px solid #0066CC;
        font-size: 0.9em;
    }

    /* Input area */
    .stTextInput > div > div > input {
        border: 4px solid #000000;
        border-radius: 0;
        padding: 1rem;
        font-size: 1rem;
        background: #FFFFFF;
        font-family: 'IBM Plex Sans', sans-serif;
    }

    .stTextInput > div > div > input:focus {
        border-color: #0066CC;
        box-shadow: 0 0 0 4px rgba(0,102,204,0.2);
    }

    /* Buttons */
    .stButton > button {
        background: #E30613;
        color: white;
        border: 4px solid #000000;
        border-radius: 0;
        padding: 0.8rem 2rem;
        font-weight: 700;
        font-size: 1rem;
        box-shadow: 6px 6px 0 #000000;
        font-family: 'IBM Plex Sans', sans-serif;
        letter-spacing: 0.05em;
    }

    .stButton > button:hover {
        background: #FFD700;
        color: #000000;
        transform: translate(-2px, -2px);
        box-shadow: 8px 8px 0 #000000;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #0066CC;
        font-weight: 700;
        font-size: 2rem;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background: #F8F8F8;
        border: 3px solid #000000;
        border-radius: 0;
        font-weight: 700;
        color: #000000;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Column dividers */
    .block-container {
        border-right: 3px solid #E5E5E5;
    }

</style>
""", unsafe_allow_html=True)

# Import system prompt
from larry_system_prompt_v3 import LARRY_SYSTEM_PROMPT_V3

LARRY_SYSTEM_PROMPT = LARRY_SYSTEM_PROMPT_V3

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
    """Parse Larry's response and identify message types"""
    messages = []

    # Split by common patterns
    sections = response_text.split('\n\n')

    for section in sections:
        if not section.strip():
            continue

        # Provocative question (starts with question mark or "Suppose", "What if")
        if section.startswith(('?', 'Suppose', 'What if', 'Think about', 'Do not misunderstand')):
            messages.append(('provocative', section))

        # Framework (contains bold framework names or structured content)
        elif '**' in section and any(word in section for word in ['Framework', 'Tool', 'Model', 'Method']):
            messages.append(('framework', section))

        # Action (starts with "Action:", "Next step:", contains time estimate)
        elif any(phrase in section for phrase in ['Action:', 'Next step:', 'In the next', 'Try this:']):
            messages.append(('action', section))

        # Diagnostic question
        elif section.endswith('?') and any(word in section.lower() for word in ['what', 'where', 'which', 'how']):
            messages.append(('diagnostic', section))

        # Case story (contains examples, case studies)
        elif any(word in section for word in ['Example:', 'Case:', 'Story:', 'Consider:']):
            messages.append(('case', section))

        # Regular assistant message
        else:
            messages.append(('regular', section))

    return messages

def render_message(message_type, content):
    """Render message based on type"""
    if message_type == 'provocative':
        return f'<div class="provocative-question">{content}</div>'

    elif message_type == 'framework':
        # Extract title if exists
        lines = content.split('\n')
        title = lines[0].replace('**', '').strip() if lines else 'Framework'
        body = '\n'.join(lines[1:]) if len(lines) > 1 else content
        return f'<div class="framework-block"><h3>{title}</h3>{body}</div>'

    elif message_type == 'action':
        # Extract time estimate if exists
        time_match = re.search(r'(\d+[-–]\d+\s+\w+|\d+\s+\w+)', content)
        time_estimate = time_match.group(1) if time_match else '20 min'
        return f'<div class="action-block">{content}<div class="action-time">⏱️ {time_estimate}</div></div>'

    elif message_type == 'diagnostic':
        return f'<div class="diagnostic-block">{content}</div>'

    elif message_type == 'case':
        # Try to split story and lesson
        parts = content.split('The lesson?', 1)
        if len(parts) == 2:
            return f'''<div class="case-story">
                <div class="story">{parts[0]}</div>
                <div class="lesson">{parts[1]}</div>
            </div>'''
        else:
            return f'<div class="case-story"><div class="story">{content}</div></div>'

    else:  # regular
        return f'<div class="assistant-message">{content}</div>'

def chat_with_larry(user_message, api_key, store_info, persona, problem_type, exa_api_key=None):
    """Send message to Larry using File Search + Exa.ai web search"""
    try:
        client = genai.Client(api_key=api_key)

        # Check if web search is needed and perform Exa search
        search_results = None
        if exa_api_key:
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
        if store_info:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=enhanced_prompt,
                    tools=[
                        types.Tool(
                            file_search=types.FileSearch(
                                file_search_store_names=[store_info['store_name']]
                            )
                        )
                    ],
                    temperature=0.7,
                    top_p=0.95,
                )
            )
        else:
            # Fallback without File Search
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=enhanced_prompt,
                    temperature=0.7,
                    top_p=0.95,
                )
            )

        # Combine search results with Larry's response
        full_response = ""
        if search_results:
            full_response = search_results + "\n\n---\n\n"

        if response and response.text:
            full_response += response.text
            return full_response
        else:
            return "I'm sorry, I couldn't generate a response. Could you rephrase your question?"

    except Exception as e:
        return f"Error: {str(e)}"

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'api_key' not in st.session_state:
    st.session_state.api_key = None

if 'exa_api_key' not in st.session_state:
    st.session_state.exa_api_key = None

if 'persona' not in st.session_state:
    st.session_state.persona = 'general'

if 'problem_type' not in st.session_state:
    st.session_state.problem_type = 'general'

if 'problem_position' not in st.session_state:
    st.session_state.problem_position = 50

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {'now': 0, 'new': 0, 'next': 0}

# Header
st.markdown("""
<div class="destijl-header">
    <h1>🎯 LARRY</h1>
    <p>Your Personal Uncertainty Navigator</p>
</div>
""", unsafe_allow_html=True)

# 3-Column Layout
left_col, center_col, right_col = st.columns([1, 2, 1])

# LEFT COLUMN: Persona Detection & Problem Classification
with left_col:
    st.markdown("### 🎭 DETECTED PERSONA")
    persona_class = st.session_state.persona
    st.markdown(f'<div class="persona-badge {persona_class}">{st.session_state.persona.upper()}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Problem Type Timeline
    st.markdown("""
    <div class="problem-timeline">
        <h4>📊 PROBLEM TYPE CLASSIFIER</h4>
        <div class="timeline-bar"></div>
        <div class="timeline-labels">
            <div class="timeline-label" style="background: #E30613; color: white;">UNDEFINED<br>5-20 yrs</div>
            <div class="timeline-label" style="background: #FFD700;">ILL-DEFINED<br>1-5 yrs</div>
            <div class="timeline-label" style="background: #0066CC; color: white;">WELL-DEFINED<br><1 yr</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"**Current:** {st.session_state.problem_type.upper()}")

    st.markdown("---")

    # Portfolio Tracker
    st.markdown("""
    <div class="portfolio-tracker">
        <h4>📈 INNOVATION PORTFOLIO</h4>
        <div class="portfolio-grid">
            <div class="portfolio-item now">NOW (Incremental): 70%</div>
            <div class="portfolio-item new">NEW (Adjacent): 20%</div>
            <div class="portfolio-item next">NEXT (Disruptive): 10%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # API Key Configuration
    st.markdown("### 🔑 Configuration")
    api_key_input = st.text_input(
        "Google AI API Key",
        type="password",
        value=st.session_state.api_key or "",
        help="Get your API key from https://aistudio.google.com/apikey"
    )

    if api_key_input:
        st.session_state.api_key = api_key_input
        st.success("✅ Google AI configured!")
    else:
        st.warning("⚠️ Please enter Google AI key")

    st.markdown("---")

    # Exa API Key Configuration
    exa_key_input = st.text_input(
        "Exa.ai API Key (Optional)",
        type="password",
        value=st.session_state.exa_api_key or os.getenv('EXA_API_KEY', ''),
        help="Get your API key from https://exa.ai/ - Enables cutting-edge research search"
    )

    if exa_key_input:
        st.session_state.exa_api_key = exa_key_input
        st.success("✅ Exa.ai configured! 🔍")
    else:
        st.info("💡 Add Exa.ai key for current research")

    # Load store info
    store_info = load_store_info()
    if store_info:
        st.info(f"📚 Knowledge Base: Active\n\n{store_info.get('total_chunks', '2,988')} chunks loaded")
    else:
        st.warning("⚠️ File Search not configured")

    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.persona = 'general'
        st.session_state.problem_type = 'general'
        st.rerun()

# CENTER COLUMN: Chat Interface
with center_col:
    st.markdown("### 💬 Conversation")

    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            # Parse and render message types
            parsed_messages = parse_response_for_message_types(message["content"])
            for msg_type, msg_content in parsed_messages:
                html = render_message(msg_type, msg_content)
                st.markdown(html, unsafe_allow_html=True)

    # Chat input
    if st.session_state.api_key:
        user_input = st.chat_input("Ask Larry about innovation, problem-solving, or PWS methodology...")

        if user_input:
            # Detect persona and problem type
            st.session_state.persona = detect_persona(user_input)
            problem_type, position = classify_problem_type(user_input)
            st.session_state.problem_type = problem_type
            st.session_state.problem_position = position

            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Get Larry's response
            with st.spinner("🤔 Larry is thinking... 🔍 Searching latest research..."):
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
        st.info("👈 Please enter your API key in the left panel to start chatting!")

# RIGHT COLUMN: Context & Tools
with right_col:
    st.markdown("### 🧰 Tools & Templates")

    # Session stats
    st.markdown("""
    <div class="context-panel">
        <h4>📊 SESSION STATS</h4>
    </div>
    """, unsafe_allow_html=True)
    st.metric("Messages", len(st.session_state.messages))
    st.metric("Questions Asked", len([m for m in st.session_state.messages if m["role"] == "user"]))

    st.markdown("---")

    # Quick Tools
    with st.expander("🔧 Quick Tools", expanded=False):
        st.markdown("""
        <div class="context-panel">
            <ul>
                <li>3-Box Portfolio</li>
                <li>JTBD Template</li>
                <li>MECE Tree</li>
                <li>5 Whys</li>
                <li>Scenario Planning</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Frameworks Library
    with st.expander("📚 Frameworks", expanded=False):
        st.markdown("""
        **Top Frameworks:**
        - Design Thinking
        - Disruptive Innovation
        - Jobs-to-be-Done
        - Blue Ocean Strategy
        - Three Box Solution
        - Scenario Analysis
        """)

    # Example Questions
    with st.expander("💡 Example Questions", expanded=False):
        st.markdown("""
        **For Students:**
        - What is Creative Destruction?
        - How do I prepare for the innovation exam?

        **For Entrepreneurs:**
        - How do I validate my startup idea?
        - What frameworks help find opportunities?

        **For Corporate:**
        - How do I build a systematic innovation process?
        - What is the Three Box Solution?
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <strong>Larry - Your Personal Uncertainty Navigator</strong><br>
    Powered by Google Gemini 2.5 Flash | Lawrence Aronhime's PWS Methodology
</div>
""", unsafe_allow_html=True)
