"""
Quick Actions Component for Larry Navigator v2.0
Provides commonly used prompts and actions
"""

import streamlit as st
from typing import Callable, Optional


def render_quick_actions(on_action_click: Optional[Callable] = None):
    """Render quick action buttons for common tasks

    Args:
        on_action_click: Callback function when an action is clicked
                         Should accept action_id and prompt text
    """

    st.markdown("""
    <div style="margin: 1.5rem 0;">
        <div style="font-weight: 600; color: var(--text-secondary); margin-bottom: 0.75rem; font-size: 0.875rem;">
            Quick Actions
        </div>
        <div class="quick-actions">
    """, unsafe_allow_html=True)

    actions = [
        {
            "id": "pws_check",
            "label": "🔍 PWS Check",
            "prompt": "Can you evaluate this problem against the PWS framework? Is it Real, Winnable, and Worth It?"
        },
        {
            "id": "define_problem",
            "label": "📝 Define Problem",
            "prompt": "Help me clearly define this problem. What's the core issue we're trying to solve?"
        },
        {
            "id": "research",
            "label": "🔬 Research",
            "prompt": "Can you research the latest information and best practices related to this problem?"
        },
        {
            "id": "frameworks",
            "label": "🧰 Suggest Frameworks",
            "prompt": "What frameworks or methodologies would be most helpful for approaching this problem?"
        },
        {
            "id": "stakeholders",
            "label": "👥 Identify Stakeholders",
            "prompt": "Who are the key stakeholders for this problem? What are their perspectives and needs?"
        },
        {
            "id": "constraints",
            "label": "⚠️ Analyze Constraints",
            "prompt": "What are the key constraints, limitations, or risks I should consider?"
        }
    ]

    # Create buttons in columns for better layout
    cols = st.columns(3)
    for i, action in enumerate(actions):
        with cols[i % 3]:
            if st.button(
                action["label"],
                key=f"quick_action_{action['id']}",
                use_container_width=True
            ):
                if on_action_click:
                    on_action_click(action["id"], action["prompt"])
                # Store the selected action in session state
                st.session_state.last_quick_action = action["prompt"]
                st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)


def render_pws_quick_prompts():
    """Render PWS-specific quick prompts"""

    st.markdown("""
    <div class="diagnostic-card">
        <h4 style="margin-bottom: 1rem;">💡 PWS Exploration Prompts</h4>
    """, unsafe_allow_html=True)

    prompts = [
        {
            "category": "Real",
            "icon": "🔥",
            "color": "var(--pws-real)",
            "questions": [
                "Who experiences this problem? How often?",
                "What evidence do we have that this is a real pain point?",
                "How are people currently dealing with this problem?"
            ]
        },
        {
            "category": "Winnable",
            "icon": "🎯",
            "color": "var(--pws-winnable)",
            "questions": [
                "What capabilities do we need to solve this?",
                "What similar problems have been solved before?",
                "What are the technical/resource constraints?"
            ]
        },
        {
            "category": "Worth It",
            "icon": "💎",
            "color": "var(--pws-worth)",
            "questions": [
                "What value does solving this create?",
                "How many people/organizations benefit?",
                "What's the opportunity cost of NOT solving this?"
            ]
        }
    ]

    for prompt_set in prompts:
        st.markdown(f"""
        <div style="margin-bottom: 1.5rem; padding: 1rem; background: var(--cream-bg); border-radius: var(--radius-md); border-left: 4px solid {prompt_set['color']};">
            <div style="font-weight: 600; color: {prompt_set['color']}; margin-bottom: 0.5rem; font-size: 1.125rem;">
                {prompt_set['icon']} {prompt_set['category']}
            </div>
        """, unsafe_allow_html=True)

        for question in prompt_set["questions"]:
            st.markdown(f"""
            <div style="margin: 0.5rem 0; padding-left: 1rem; color: var(--text-secondary);">
                • {question}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_problem_type_prompts(problem_type: str):
    """Render contextual prompts based on current problem type

    Args:
        problem_type: "undefined" | "ill-defined" | "well-defined"
    """

    prompts_by_type = {
        "undefined": {
            "title": "🔮 Exploring Undefined Territory",
            "color": "var(--undefined)",
            "prompts": [
                "What are the symptoms or pain points we're observing?",
                "What don't we know yet about this space?",
                "What assumptions should we challenge first?",
                "What would help us better understand this problem?"
            ]
        },
        "ill-defined": {
            "title": "🔍 Clarifying Ill-Defined Problem",
            "color": "var(--ill-defined)",
            "prompts": [
                "What are the boundaries of this problem?",
                "Which stakeholders have different perspectives on this?",
                "What data or evidence would help clarify this?",
                "What are the root causes vs. symptoms?"
            ]
        },
        "well-defined": {
            "title": "✅ Tackling Well-Defined Problem",
            "color": "var(--well-defined)",
            "prompts": [
                "What are the solution approaches we should consider?",
                "What success criteria should we define?",
                "What resources and timeline do we need?",
                "What risks might derail our solution?"
            ]
        }
    }

    config = prompts_by_type.get(problem_type, prompts_by_type["undefined"])

    st.markdown(f"""
    <div class="diagnostic-card">
        <h4 style="color: {config['color']}; margin-bottom: 1rem;">{config['title']}</h4>
        <div style="color: var(--text-secondary);">
            Based on your current problem state, consider these questions:
        </div>
        <div style="margin-top: 1rem;">
    """, unsafe_allow_html=True)

    for prompt in config["prompts"]:
        st.markdown(f"""
        <div style="padding: 0.75rem; margin: 0.5rem 0; background: var(--cream-bg); border-radius: var(--radius-sm); border-left: 3px solid {config['color']};">
            {prompt}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)


def render_welcome_prompts():
    """Render welcome prompts for first-time users"""

    st.markdown("""
    <div class="diagnostic-card">
        <h3 style="text-align: center; margin-bottom: 1.5rem;">👋 Welcome to Larry Navigator</h3>

        <p style="color: var(--text-secondary); text-align: center; margin-bottom: 2rem;">
            I'm here to help you navigate complex problems using the PWS methodology.
            Let's start by exploring what brought you here.
        </p>

        <div class="insight-box">
            <span class="insight-icon">💡</span>
            <span class="insight-text">
                <strong>Try starting with:</strong><br>
                "I'm working on [problem]..." or "I need help understanding [situation]..."
            </span>
        </div>

        <div style="margin-top: 2rem;">
            <div style="font-weight: 600; margin-bottom: 1rem; color: var(--text-secondary);">
                Example starting points:
            </div>

            <div style="display: grid; gap: 0.75rem;">
                <div style="padding: 1rem; background: var(--cream-bg); border-radius: var(--radius-md); border-left: 4px solid var(--teal-primary);">
                    "I'm exploring whether to build a new product feature..."
                </div>
                <div style="padding: 1rem; background: var(--cream-bg); border-radius: var(--radius-md); border-left: 4px solid var(--teal-primary);">
                    "My team is struggling with [challenge]..."
                </div>
                <div style="padding: 1rem; background: var(--cream-bg); border-radius: var(--radius-md); border-left: 4px solid var(--teal-primary);">
                    "I need to make a decision about [situation]..."
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
