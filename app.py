#!/usr/bin/env python3
"""
Larry - Your Personal Uncertainty Navigator
Web Interface using Streamlit
Production version with latest Gemini model and enhanced features
"""

import streamlit as st
import os
from larry_production import LarryProduction, STORE_INFO_FILE, GEMINI_MODEL

# Page configuration
st.set_page_config(
    page_title="Larry - Uncertainty Navigator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    .sidebar-info {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

def initialize_larry():
    """Initialize Production Larry Navigator"""
    # Get API key from environment variable or Streamlit secrets
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key and hasattr(st, 'secrets') and 'GOOGLE_AI_API_KEY' in st.secrets:
        api_key = st.secrets['GOOGLE_AI_API_KEY']

    if not api_key:
        # Fallback to the hardcoded key
        from larry_production import GOOGLE_AI_API_KEY
        api_key = GOOGLE_AI_API_KEY

    return LarryProduction(api_key=api_key, store_info_file=STORE_INFO_FILE)

def main():
    # Header
    st.markdown('<div class="main-header">🎯 Larry - Your Personal Uncertainty Navigator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Teaching innovation using Lawrence Aronhime\'s Problems Worth Solving methodology</div>', unsafe_allow_html=True)

    # Model info
    st.markdown(f'<div style="text-align: center; color: #888; font-size: 0.9rem; margin-bottom: 1rem;">Powered by {GEMINI_MODEL}</div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("### 📚 About Larry")
        st.markdown("""
        <div class="sidebar-info">
        Larry teaches using the <strong>Aronhime Method</strong>:
        <ul>
            <li>🎯 Starts with problems, not answers</li>
            <li>🤔 Challenges your thinking</li>
            <li>📖 Uses memorable stories</li>
            <li>🧰 Provides systematic frameworks</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 💡 Example Questions")
        st.markdown("""
        **For Students:**
        - What is Creative Destruction?
        - What's the difference between un-defined and ill-defined problems?

        **For Entrepreneurs:**
        - How do I validate my startup idea?
        - Is my problem un-defined or ill-defined?

        **For Corporate Teams:**
        - What is the Three Box Solution?
        - How do I manage an innovation portfolio?

        **General:**
        - Show me examples of wicked problems
        - Tell me about Scenario Analysis
        """)

        if st.button("🔄 Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

        # Knowledge base status
        if 'larry' in st.session_state:
            st.markdown("### 📊 System Status")
            if st.session_state.larry.file_search_enabled:
                st.success("✅ Knowledge Base Active")
                st.caption(f"Files: {st.session_state.larry.store_info.get('file_count', 'N/A')}")
                st.caption(f"Chunks: {st.session_state.larry.store_info.get('total_chunks', 'N/A')}")
            else:
                st.warning("⚠️ Knowledge Base Inactive")
                st.caption("Using general AI knowledge")

            # Session stats button
            if st.button("📈 Session Stats"):
                stats = st.session_state.larry.get_session_stats()
                st.write(f"**Duration:** {stats['duration_minutes']} min")
                st.write(f"**Messages:** {stats['total_messages']}")
                st.write(f"**Model:** {stats['model']}")

    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if 'larry' not in st.session_state:
        with st.spinner("Initializing Larry..."):
            try:
                st.session_state.larry = initialize_larry()
            except Exception as e:
                st.error(f"Error initializing Larry: {e}")
                st.info("Tip: Run `python3 build_larry_navigator_v2.py` to enable the PWS knowledge base.")
                return

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask Larry a question..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get Larry's response
        with st.chat_message("assistant"):
            with st.spinner("Larry is thinking..."):
                try:
                    response = st.session_state.larry.chat(prompt)
                    st.markdown(response)

                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

    # Welcome message if no messages
    if len(st.session_state.messages) == 0:
        st.info("👋 Welcome! I'm Larry, your Personal Uncertainty Navigator. Ask me anything about innovation, problem-solving, or the Problems Worth Solving methodology!")

if __name__ == "__main__":
    main()
