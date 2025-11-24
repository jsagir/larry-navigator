"""
Header Component for Larry Navigator v2.0
Displays title, subtitle, and PWS badges
"""

import streamlit as st


def render_larry_header():
    """Render the Larry Navigator header with PWS badges"""

    st.markdown("""
    <div class="larry-header">
        <div class="larry-title">🎯 Larry</div>
        <div class="larry-subtitle">Your PWS Innovation Mentor</div>

        <div class="larry-pws-badges">
            <span class="pws-badge pws-badge-real">
                🔥 Real
            </span>
            <span class="pws-badge pws-badge-winnable">
                🎯 Winnable
            </span>
            <span class="pws-badge pws-badge-worth">
                💎 Worth It
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_pws_explanation():
    """Render PWS framework explanation (optional, can be shown on first visit)"""

    st.markdown("""
    <div class="diagnostic-card">
        <h3 style="margin-bottom: 1rem;">The PWS Framework</h3>

        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: start; gap: 1rem; margin-bottom: 1rem;">
                <span style="font-size: 2rem;">🔥</span>
                <div>
                    <strong style="color: var(--pws-real); font-size: 1.125rem;">Real</strong>
                    <p style="margin-top: 0.25rem; color: var(--text-secondary);">
                        Is this a problem that people actually experience? Is there evidence of pain?
                    </p>
                </div>
            </div>

            <div style="display: flex; align-items: start; gap: 1rem; margin-bottom: 1rem;">
                <span style="font-size: 2rem;">🎯</span>
                <div>
                    <strong style="color: var(--pws-winnable); font-size: 1.125rem;">Winnable</strong>
                    <p style="margin-top: 0.25rem; color: var(--text-secondary);">
                        Can this problem be solved? Do we have (or can we build) the capabilities needed?
                    </p>
                </div>
            </div>

            <div style="display: flex; align-items: start; gap: 1rem;">
                <span style="font-size: 2rem;">💎</span>
                <div>
                    <strong style="color: var(--pws-worth); font-size: 1.125rem;">Worth It</strong>
                    <p style="margin-top: 0.25rem; color: var(--text-secondary);">
                        Is the value worth the effort? Will solving this create significant impact?
                    </p>
                </div>
            </div>
        </div>

        <div class="insight-box">
            <span class="insight-icon">💡</span>
            <span class="insight-text">
                Every problem we explore will be evaluated through these three lenses.
                This keeps us focused on problems worth solving.
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
