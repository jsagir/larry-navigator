"""
Problem Dashboard Component for Larry Navigator v2.0
4-dimensional problem diagnosis display
"""

import streamlit as st
from utils.session_state import get_diagnosis


def render_problem_dashboard():
    """Render the 4-dimensional problem dashboard"""

    diagnosis = get_diagnosis()

    st.markdown("""
    <div class="problem-dashboard">
        <div class="dashboard-title">
            📊 Problem Diagnosis
        </div>
    """, unsafe_allow_html=True)

    # Create 2x2 grid for the 4 dimensions
    col1, col2 = st.columns(2)

    with col1:
        # Dimension 1: Definition Track
        render_definition_track(diagnosis.definition, diagnosis.definition_confidence)

    with col2:
        # Dimension 2: Complexity (Cynefin)
        render_complexity_cynefin(diagnosis.complexity, diagnosis.complexity_confidence)

    col3, col4 = st.columns(2)

    with col3:
        # Dimension 3: Risk-Uncertainty Slider
        render_risk_uncertainty_slider(diagnosis.risk_uncertainty)

    with col4:
        # Dimension 4: Wickedness Scale
        render_wickedness_scale(diagnosis.wickedness, diagnosis.wickedness_score)

    st.markdown("</div>", unsafe_allow_html=True)


def render_definition_track(current: str, confidence: float):
    """Render the definition track: undefined → ill-defined → well-defined

    Args:
        current: "undefined" | "ill-defined" | "well-defined"
        confidence: 0.0 to 1.0
    """
    stages = ["undefined", "ill-defined", "well-defined"]
    stage_labels = ["Un-defined", "Ill-defined", "Well-defined"]

    active_classes = [
        "active" if stage == current else ""
        for stage in stages
    ]

    st.markdown(f"""
    <div class="dimension-card">
        <div class="dimension-label">Definition Track</div>
        <div class="dimension-value">{stage_labels[stages.index(current)]}</div>

        <div class="definition-track">
            <div class="definition-stage undefined {active_classes[0]}">
                {stage_labels[0]}
            </div>
            <div class="definition-stage ill-defined {active_classes[1]}">
                {stage_labels[1]}
            </div>
            <div class="definition-stage well-defined {active_classes[2]}">
                {stage_labels[2]}
            </div>
        </div>

        <div style="margin-top: 0.75rem; font-size: 0.875rem; color: var(--text-muted);">
            Confidence: {int(confidence * 100)}%
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_complexity_cynefin(current: str, confidence: float):
    """Render the Cynefin complexity grid

    Args:
        current: "simple" | "complicated" | "complex" | "chaotic"
        confidence: 0.0 to 1.0
    """
    quadrants = {
        "simple": "Simple",
        "complicated": "Complicated",
        "complex": "Complex",
        "chaotic": "Chaotic"
    }

    st.markdown(f"""
    <div class="dimension-card">
        <div class="dimension-label">Complexity (Cynefin)</div>
        <div class="dimension-value">{quadrants.get(current, "Complex")}</div>

        <div class="cynefin-grid">
            <div class="cynefin-quadrant cynefin-simple {'active' if current == 'simple' else ''}">
                Simple
            </div>
            <div class="cynefin-quadrant cynefin-complicated {'active' if current == 'complicated' else ''}">
                Complicated
            </div>
            <div class="cynefin-quadrant cynefin-complex {'active' if current == 'complex' else ''}">
                Complex
            </div>
            <div class="cynefin-quadrant cynefin-chaotic {'active' if current == 'chaotic' else ''}">
                Chaotic
            </div>
        </div>

        <div style="margin-top: 0.75rem; font-size: 0.875rem; color: var(--text-muted);">
            Confidence: {int(confidence * 100)}%
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_risk_uncertainty_slider(position: float):
    """Render the risk-uncertainty slider

    Args:
        position: 0.0 (risk/known unknowns) to 1.0 (uncertainty/unknown unknowns)
    """
    # Calculate position percentage
    position_percent = int(position * 100)

    # Determine text description
    if position < 0.3:
        description = "Risk (Known Unknowns)"
    elif position < 0.7:
        description = "Moderate Uncertainty"
    else:
        description = "High Uncertainty (Unknown Unknowns)"

    st.markdown(f"""
    <div class="dimension-card">
        <div class="dimension-label">Risk-Uncertainty Position</div>
        <div class="dimension-value">{description}</div>

        <div class="risk-uncertainty-container">
            <div class="slider-labels">
                <span>Risk</span>
                <span>Uncertainty</span>
            </div>

            <div class="slider-track">
                <div class="slider-position" style="left: {position_percent}%;"></div>
            </div>

            <div class="slider-value">
                {position:.2f}
            </div>
        </div>

        <div style="margin-top: 0.5rem; font-size: 0.875rem; color: var(--text-muted); text-align: center;">
            0.0 = Known unknowns · 1.0 = Unknown unknowns
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_wickedness_scale(current: str, score: float):
    """Render the wickedness scale

    Args:
        current: "tame" | "messy" | "complex" | "wicked"
        score: 0.0 to 1.0
    """
    levels = {
        "tame": "Tame",
        "messy": "Messy",
        "complex": "Complex",
        "wicked": "Wicked"
    }

    st.markdown(f"""
    <div class="dimension-card">
        <div class="dimension-label">Wickedness Scale</div>
        <div class="dimension-value">{levels.get(current, "Messy")}</div>

        <div class="wickedness-scale">
            <div class="wickedness-level wickedness-tame {'active' if current == 'tame' else ''}">
                Tame
            </div>
            <div class="wickedness-level wickedness-messy {'active' if current == 'messy' else ''}">
                Messy
            </div>
            <div class="wickedness-level wickedness-complex {'active' if current == 'complex' else ''}">
                Complex
            </div>
            <div class="wickedness-level wickedness-wicked {'active' if current == 'wicked' else ''}">
                Wicked
            </div>
        </div>

        <div style="margin-top: 0.75rem; font-size: 0.875rem; color: var(--text-muted);">
            Wickedness Score: {int(score * 100)}%
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_compact_dashboard():
    """Render a compact version of the dashboard (for sidebar or collapsed view)"""

    diagnosis = get_diagnosis()

    st.markdown(f"""
    <div style="background: var(--cream-light); padding: 1rem; border-radius: var(--radius-md); border: 1px solid var(--border-light);">
        <div style="font-weight: 600; margin-bottom: 0.75rem; color: var(--text-primary);">
            📊 Current Diagnosis
        </div>

        <div style="display: flex; flex-direction: column; gap: 0.5rem; font-size: 0.875rem;">
            <div>
                <span style="color: var(--text-muted);">Definition:</span>
                <strong style="color: var(--teal-primary); margin-left: 0.5rem;">{diagnosis.definition}</strong>
            </div>
            <div>
                <span style="color: var(--text-muted);">Complexity:</span>
                <strong style="color: var(--teal-primary); margin-left: 0.5rem;">{diagnosis.complexity}</strong>
            </div>
            <div>
                <span style="color: var(--text-muted);">Risk-Uncertainty:</span>
                <strong style="color: var(--teal-primary); margin-left: 0.5rem;">{diagnosis.risk_uncertainty:.2f}</strong>
            </div>
            <div>
                <span style="color: var(--text-muted);">Wickedness:</span>
                <strong style="color: var(--teal-primary); margin-left: 0.5rem;">{diagnosis.wickedness}</strong>
            </div>
        </div>

        <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid var(--border-light); font-size: 0.75rem; color: var(--text-muted);">
            Updates: {diagnosis.update_count}
        </div>
    </div>
    """, unsafe_allow_html=True)
