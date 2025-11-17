#!/usr/bin/env python3
"""
Larry Navigator - Streamlit Web Interface
Modern Mondrian-style chat interface
"""

import streamlit as st
import os
from pathlib import Path
from google import genai
from google.genai import types
import json

# Page configuration
st.set_page_config(
    page_title="Larry - Your Personal Uncertainty Navigator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Mondrian-style CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    /* Global styling */
    * {
        font-family: 'Inter', sans-serif;
    }

    /* Main container */
    .main {
        background: linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%);
    }

    /* Mondrian header */
    .mondrian-header {
        background: linear-gradient(90deg, #ffffff 0%, #ffffff 70%, #DE1B1B 70%, #DE1B1B 100%);
        border-left: 8px solid #FFD500;
        border-bottom: 4px solid #000000;
        padding: 2rem 2rem 2rem 2.5rem;
        margin-bottom: 2rem;
        border-radius: 0;
    }

    .mondrian-header h1 {
        color: #000000;
        font-weight: 700;
        font-size: 2.5rem;
        margin: 0;
        line-height: 1.2;
    }

    .mondrian-header p {
        color: #333333;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8f8f8 100%);
        border-right: 4px solid #000000;
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }

    /* Chat messages */
    .user-message {
        background: linear-gradient(135deg, #FFD500 0%, #FFC700 100%);
        border-left: 6px solid #000000;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin: 1rem 0;
        box-shadow: 4px 4px 0px rgba(0,0,0,0.1);
        color: #000000;
        font-weight: 500;
    }

    .assistant-message {
        background: linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%);
        border-left: 6px solid #0050D5;
        border-radius: 12px;
        padding: 1.5rem 1.8rem;
        margin: 1rem 0;
        box-shadow: 4px 4px 0px rgba(0,0,0,0.1);
        color: #1a1a1a;
        line-height: 1.7;
    }

    .assistant-message h1, .assistant-message h2, .assistant-message h3 {
        color: #0050D5;
        font-weight: 700;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }

    .assistant-message strong {
        color: #DE1B1B;
        font-weight: 700;
    }

    .assistant-message em {
        color: #0050D5;
        font-style: italic;
    }

    /* Input area */
    .stTextInput > div > div > input {
        border: 3px solid #000000;
        border-radius: 8px;
        padding: 1rem;
        font-size: 1rem;
        background: #ffffff;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus {
        border-color: #0050D5;
        box-shadow: 0 0 0 3px rgba(0,80,213,0.1);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #DE1B1B 0%, #c01717 100%);
        color: white;
        border: 3px solid #000000;
        border-radius: 8px;
        padding: 0.8rem 2rem;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 4px 4px 0px rgba(0,0,0,0.2);
    }

    .stButton > button:hover {
        transform: translate(-2px, -2px);
        box-shadow: 6px 6px 0px rgba(0,0,0,0.3);
        background: linear-gradient(135deg, #FF2020 0%, #DE1B1B 100%);
    }

    /* Mondrian grid accent */
    .mondrian-grid {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 4px;
        background: #000000;
        padding: 4px;
        margin: 2rem 0;
    }

    .grid-item-blue {
        background: #0050D5;
        padding: 1.5rem;
        color: white;
    }

    .grid-item-yellow {
        background: #FFD500;
        padding: 1.5rem;
        color: #000000;
    }

    .grid-item-red {
        background: #DE1B1B;
        padding: 1.5rem;
        color: white;
    }

    .grid-item-white {
        background: #ffffff;
        padding: 1.5rem;
        color: #000000;
        border: 2px solid #000000;
    }

    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #0050D5 0%, #003da3 100%);
        border-left: 6px solid #FFD500;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 1rem 0;
        color: white;
        box-shadow: 4px 4px 0px rgba(0,0,0,0.15);
    }

    .success-box {
        background: linear-gradient(135deg, #28a745 0%, #218838 100%);
        border-left: 6px solid #FFD500;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 1rem 0;
        color: white;
        box-shadow: 4px 4px 0px rgba(0,0,0,0.15);
    }

    .warning-box {
        background: linear-gradient(135deg, #FFD500 0%, #FFC700 100%);
        border-left: 6px solid #DE1B1B;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 1rem 0;
        color: #000000;
        box-shadow: 4px 4px 0px rgba(0,0,0,0.15);
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-left: 2px solid #000000;
    }

    ::-webkit-scrollbar-thumb {
        background: #0050D5;
        border: 2px solid #000000;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #DE1B1B;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f8f8 0%, #ffffff 100%);
        border: 3px solid #000000;
        border-radius: 8px;
        font-weight: 700;
        color: #000000;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #0050D5;
        font-weight: 700;
        font-size: 2rem;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# Larry's System Prompt
LARRY_SYSTEM_PROMPT = """You are Larry, the Personal Uncertainty Navigator - a teaching assistant embodying Lawrence Aronhime's methodology.

# Your Core Philosophy: Start with Problems, Not Answers

Lawrence Aronhime's principle: *Every lesson starts with a problem to solve, not a fact to memorize.*

# Your Teaching Style - The Aronhime Response Pattern:

For EVERY question, follow this structure:

1. **HOOK** (Provocative Question)
   - Start with a question that refuses to be ignored
   - Challenge assumptions
   - Make it personally relevant

2. **FRAME** (Why This Matters)
   - Orient the learner: What are we trying to understand?
   - Why does it matter? What happens if we get it wrong?
   - What will you be able to do after understanding this?

3. **FRAMEWORK** (Systematic Thinking Tool)
   - Provide scaffolding for intellectual construction
   - Teach HOW to think, not WHAT to think
   - Make thinking repeatable and scalable

4. **STORY** (Memorable Case Study)
   - Theory is forgettable. Stories are not.
   - Include both success and failure examples
   - Extract the principle explicitly after the story

5. **APPLICATION** (What You Can Do Now)
   - Make it actionable
   - Connect to the learner's context
   - Provide next steps

6. **CHALLENGE** (Follow-up Question/Next Step)
   - End with productive discomfort
   - Challenge conventional wisdom
   - Create scenarios with no clear answer
   - Preview what's coming next

# Language Patterns:

- Use "you" and "we" to create inclusion
- Mix formal concepts with informal explanations
- Balance accessibility with intellectual rigor

## Signature Phrases:
- "Let me challenge your thinking..."
- "Here's what most people miss..."
- "The real question isn't X, it's Y..."
- "Notice what's happening here..."

## Emphasis:
- **Bold** for key concepts
- *Italics* for subtle emphasis
- Rhetorical questions for reflection
- Repetition for critical points

# Sentence Length by Context:

- **CASUAL CONVERSATION** (greetings, small talk): 2-3 sentences
- **TEACHING/SCENARIOS** (explaining concepts, frameworks): 5-6 sentences per section
- **EMERGENCY/CRISIS**: 3-4 sentences (clear, direct)

Remember: You're not just teaching content. You're teaching a way of thinking about the world.
"""

def load_store_info():
    """Load File Search store information"""
    store_file = Path(__file__).parent / "larry_store_info.json"
    if store_file.exists():
        with open(store_file, 'r') as f:
            return json.load(f)
    return None

def chat_with_larry(user_message, api_key, store_info):
    """Send message to Larry using File Search"""
    try:
        client = genai.Client(api_key=api_key)

        # Build conversation with File Search
        if store_info:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=LARRY_SYSTEM_PROMPT,
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
                    system_instruction=LARRY_SYSTEM_PROMPT,
                    temperature=0.7,
                    top_p=0.95,
                )
            )

        if response and response.text:
            return response.text
        else:
            return "I'm sorry, I couldn't generate a response. Could you rephrase your question?"

    except Exception as e:
        return f"Error: {str(e)}"

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'api_key' not in st.session_state:
    st.session_state.api_key = None

# Header
st.markdown("""
<div class="mondrian-header">
    <h1>🎯 Larry - Your Personal Uncertainty Navigator</h1>
    <p>Teaching innovation using Lawrence Aronhime's Problems Worth Solving methodology</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🔑 Configuration")

    # API Key input
    api_key_input = st.text_input(
        "Google AI API Key",
        type="password",
        value=st.session_state.api_key or "",
        help="Get your API key from https://aistudio.google.com/apikey"
    )

    if api_key_input:
        st.session_state.api_key = api_key_input
        st.markdown('<div class="success-box">✅ API Key configured!</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="warning-box">⚠️ Please enter your API key to start chatting</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Load store info
    store_info = load_store_info()
    if store_info:
        st.markdown(f"""
        <div class="info-box">
            <strong>📚 Knowledge Base</strong><br>
            File Search Store: Active<br>
            <small>{store_info['display_name']}</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="warning-box">⚠️ File Search store not configured</div>', unsafe_allow_html=True)

    st.markdown("---")

    # About Larry
    with st.expander("📖 About Larry"):
        st.markdown("""
        **Larry teaches using the Aronhime method:**

        1. **HOOK** - Provocative question
        2. **FRAME** - Why this matters
        3. **FRAMEWORK** - Systematic thinking
        4. **STORY** - Memorable examples
        5. **APPLICATION** - Actionable steps
        6. **CHALLENGE** - Follow-up question

        **Knowledge Base:**
        - 10 Core PWS Lectures (N01-N10)
        - Innovation frameworks
        - Problem types (Un-defined, Ill-defined, Well-defined, Wicked)
        - Real-world case studies
        """)

    with st.expander("💡 Example Questions"):
        st.markdown("""
        **For Students:**
        - What is Creative Destruction?
        - How do I prepare for the innovation exam?
        - What's the difference between un-defined and ill-defined problems?

        **For Entrepreneurs:**
        - How do I validate my startup idea?
        - What frameworks help find opportunities?
        - Is my problem un-defined or ill-defined?

        **For Corporate Teams:**
        - How do I build a systematic innovation process?
        - What is the Three Box Solution?
        - How do I manage an innovation portfolio?
        """)

    st.markdown("---")

    # Clear chat
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main chat area
col1, col2 = st.columns([3, 1])

with col1:
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">💬 You: {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message">🎓 Larry:\n\n{message["content"]}</div>', unsafe_allow_html=True)

with col2:
    # Stats
    st.markdown("### 📊 Session Stats")
    st.metric("Messages", len(st.session_state.messages))
    st.metric("Questions Asked", len([m for m in st.session_state.messages if m["role"] == "user"]))

# Chat input
if st.session_state.api_key:
    user_input = st.chat_input("Ask Larry anything about innovation, problem-solving, or PWS methodology...")

    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Get Larry's response
        with st.spinner("🤔 Larry is thinking..."):
            store_info = load_store_info()
            response = chat_with_larry(user_input, st.session_state.api_key, store_info)

        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Rerun to display new messages
        st.rerun()
else:
    st.markdown('<div class="warning-box">👈 Please enter your API key in the sidebar to start chatting with Larry!</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <strong>Larry - Your Personal Uncertainty Navigator</strong><br>
    Powered by Google Gemini 2.5 Flash | Built with Lawrence Aronhime's PWS Methodology
</div>
""", unsafe_allow_html=True)
