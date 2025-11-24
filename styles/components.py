"""
Component-specific CSS for Larry Navigator v2.0
Dashboard, research panels, citations, etc.
"""

COMPONENT_CSS = """
<style>
/* ============================================
   COMPONENT STYLES - Larry Navigator v2.0
   ============================================ */

/* === Larry Header === */
.larry-header {
    text-align: center;
    padding: var(--space-xl) var(--space-lg);
    background: linear-gradient(135deg, #FFFFFF 0%, var(--cream-light) 100%);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    margin-bottom: var(--space-xl);
    border: 1px solid var(--border-light);
}

.larry-title {
    font-size: 3rem;
    font-weight: 700;
    color: var(--teal-primary);
    margin-bottom: var(--space-sm);
    font-family: var(--font-display);
}

.larry-subtitle {
    font-size: 1.25rem;
    color: var(--text-secondary);
    margin-bottom: var(--space-lg);
}

.larry-pws-badges {
    display: flex;
    justify-content: center;
    gap: var(--space-md);
    flex-wrap: wrap;
}

/* === Problem Dashboard === */
.problem-dashboard {
    background: var(--cream-light);
    border: 2px solid var(--border-light);
    border-radius: var(--radius-lg);
    padding: var(--space-xl);
    margin-bottom: var(--space-xl);
    box-shadow: var(--shadow-md);
}

.dashboard-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: var(--space-lg);
    display: flex;
    align-items: center;
    gap: var(--space-sm);
}

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--space-lg);
    margin-top: var(--space-lg);
}

.dimension-card {
    background: var(--cream-bg);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    padding: var(--space-lg);
    transition: all var(--transition-normal);
}

.dimension-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}

.dimension-label {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: var(--space-sm);
}

.dimension-value {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--teal-primary);
    margin-bottom: var(--space-md);
}

/* === Definition Track === */
.definition-track {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-sm);
    padding: var(--space-md);
    background: var(--cream-light);
    border-radius: var(--radius-md);
    margin-top: var(--space-sm);
}

.definition-stage {
    flex: 1;
    text-align: center;
    padding: var(--space-sm);
    border-radius: var(--radius-sm);
    transition: all var(--transition-normal);
    position: relative;
}

.definition-stage.active {
    background-color: var(--teal-bg);
    font-weight: 600;
}

.definition-stage.active::before {
    content: '';
    position: absolute;
    top: -8px;
    left: 50%;
    transform: translateX(-50%);
    width: 8px;
    height: 8px;
    background-color: var(--teal-primary);
    border-radius: 50%;
    box-shadow: 0 0 0 4px var(--teal-bg);
}

.definition-stage.undefined { color: var(--undefined); }
.definition-stage.ill-defined { color: var(--ill-defined); }
.definition-stage.well-defined { color: var(--well-defined); }

/* === Complexity Cynefin === */
.cynefin-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-xs);
    margin-top: var(--space-sm);
}

.cynefin-quadrant {
    padding: var(--space-md);
    border-radius: var(--radius-sm);
    text-align: center;
    border: 2px solid transparent;
    transition: all var(--transition-normal);
    background: var(--cream-light);
}

.cynefin-quadrant.active {
    border-color: var(--teal-primary);
    background: var(--teal-bg);
    font-weight: 600;
    transform: scale(1.05);
    box-shadow: var(--shadow-md);
}

.cynefin-simple { border-top: 3px solid var(--simple); }
.cynefin-complicated { border-top: 3px solid var(--complicated); }
.cynefin-complex { border-top: 3px solid var(--complex); }
.cynefin-chaotic { border-top: 3px solid var(--chaotic); }

/* === Risk-Uncertainty Slider === */
.risk-uncertainty-container {
    padding: var(--space-lg);
    margin-top: var(--space-sm);
}

.slider-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.875rem;
    color: var(--text-secondary);
    margin-bottom: var(--space-sm);
}

.slider-track {
    position: relative;
    height: 12px;
    background: linear-gradient(90deg,
        var(--well-defined) 0%,
        var(--orange-warm) 50%,
        var(--chaotic) 100%);
    border-radius: var(--radius-full);
    margin: var(--space-md) 0;
}

.slider-position {
    position: absolute;
    top: 50%;
    transform: translate(-50%, -50%);
    width: 24px;
    height: 24px;
    background: var(--cream-light);
    border: 3px solid var(--teal-primary);
    border-radius: 50%;
    box-shadow: var(--shadow-md);
    transition: all var(--transition-normal);
}

.slider-value {
    text-align: center;
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--teal-primary);
    margin-top: var(--space-md);
}

/* === Wickedness Scale === */
.wickedness-scale {
    display: flex;
    gap: var(--space-xs);
    margin-top: var(--space-sm);
}

.wickedness-level {
    flex: 1;
    padding: var(--space-md) var(--space-sm);
    border-radius: var(--radius-sm);
    text-align: center;
    font-size: 0.875rem;
    border: 2px solid transparent;
    transition: all var(--transition-normal);
    background: var(--cream-light);
}

.wickedness-level.active {
    border-color: var(--teal-primary);
    background: var(--teal-bg);
    font-weight: 600;
    transform: scale(1.05);
}

.wickedness-tame { border-top: 3px solid var(--tame); }
.wickedness-messy { border-top: 3px solid var(--messy); }
.wickedness-complex { border-top: 3px solid var(--complex-wicked); }
.wickedness-wicked { border-top: 3px solid var(--wicked); }

/* === Quick Actions === */
.quick-actions {
    display: flex;
    gap: var(--space-sm);
    flex-wrap: wrap;
    margin: var(--space-lg) 0;
}

.action-button {
    background: var(--cream-light);
    border: 1px solid var(--border-medium);
    border-radius: var(--radius-md);
    padding: var(--space-sm) var(--space-lg);
    color: var(--text-primary);
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition-fast);
    display: flex;
    align-items: center;
    gap: var(--space-sm);
}

.action-button:hover {
    background: var(--teal-bg);
    border-color: var(--teal-primary);
    transform: translateY(-1px);
    box-shadow: var(--shadow-sm);
}

/* === Research Panel === */
.research-panel {
    background: linear-gradient(135deg, #FFFFFF 0%, var(--cream-light) 100%);
    border: 1px solid var(--border-light);
    border-left: 4px solid var(--orange-warm);
    border-radius: var(--radius-lg);
    padding: var(--space-xl);
    margin: var(--space-lg) 0;
    box-shadow: var(--shadow-md);
}

.research-header {
    display: flex;
    align-items: center;
    gap: var(--space-md);
    margin-bottom: var(--space-lg);
}

.research-icon {
    font-size: 2rem;
}

.research-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-primary);
}

.research-queries {
    background: var(--cream-bg);
    border-radius: var(--radius-md);
    padding: var(--space-md);
    margin-bottom: var(--space-lg);
}

.research-query {
    display: flex;
    align-items: center;
    gap: var(--space-sm);
    padding: var(--space-sm);
    color: var(--text-secondary);
    font-style: italic;
}

/* === Citation Cards === */
.citation-card {
    background: var(--cream-light);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    padding: var(--space-lg);
    margin-bottom: var(--space-md);
    transition: all var(--transition-normal);
    position: relative;
    overflow: hidden;
}

.citation-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: var(--teal-primary);
}

.citation-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateX(4px);
}

.citation-header {
    display: flex;
    justify-content: space-between;
    align-items: start;
    margin-bottom: var(--space-md);
}

.citation-title {
    font-weight: 600;
    color: var(--teal-primary);
    font-size: 1.125rem;
    flex: 1;
    text-decoration: none;
}

.citation-title:hover {
    text-decoration: underline;
}

.citation-score {
    background: var(--teal-bg);
    color: var(--teal-primary);
    padding: var(--space-xs) var(--space-sm);
    border-radius: var(--radius-full);
    font-size: 0.875rem;
    font-weight: 600;
}

.citation-content {
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: var(--space-md);
}

.citation-url {
    font-size: 0.875rem;
    color: var(--text-muted);
    word-break: break-all;
}

/* === Insights === */
.insight-box {
    background: linear-gradient(135deg, rgba(42, 157, 143, 0.08) 0%, rgba(42, 157, 143, 0.04) 100%);
    border-left: 4px solid var(--teal-primary);
    border-radius: var(--radius-md);
    padding: var(--space-lg);
    margin: var(--space-lg) 0;
}

.insight-icon {
    font-size: 1.5rem;
    margin-right: var(--space-sm);
}

.insight-text {
    color: var(--text-primary);
    font-weight: 500;
    line-height: 1.6;
}

/* === Warning Box === */
.warning-box {
    background: rgba(231, 111, 81, 0.08);
    border-left: 4px solid var(--orange-warm);
    border-radius: var(--radius-md);
    padding: var(--space-lg);
    margin: var(--space-lg) 0;
}

.warning-icon {
    font-size: 1.5rem;
    margin-right: var(--space-sm);
    color: var(--orange-warm);
}

/* === Typing Indicator === */
.typing-container {
    display: flex;
    align-items: center;
    gap: var(--space-md);
    padding: var(--space-lg);
    background: var(--cream-light);
    border-radius: var(--radius-lg);
    margin: var(--space-md) 0;
}

.typing-avatar {
    width: 40px;
    height: 40px;
    background: var(--teal-primary);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
}

.typing-text {
    color: var(--text-secondary);
    font-style: italic;
}

/* === Stats Bar === */
.stats-bar {
    display: flex;
    gap: var(--space-lg);
    padding: var(--space-lg);
    background: var(--cream-light);
    border-radius: var(--radius-md);
    margin-bottom: var(--space-lg);
    border: 1px solid var(--border-light);
}

.stat-item {
    flex: 1;
    text-align: center;
}

.stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--teal-primary);
}

.stat-label {
    font-size: 0.875rem;
    color: var(--text-muted);
    margin-top: var(--space-xs);
}

/* === Responsive Adjustments === */
@media (max-width: 768px) {
    .larry-title {
        font-size: 2rem;
    }

    .dashboard-grid {
        grid-template-columns: 1fr;
    }

    .cynefin-grid {
        grid-template-columns: 1fr;
    }

    .wickedness-scale {
        flex-direction: column;
    }

    .quick-actions {
        flex-direction: column;
    }

    .action-button {
        width: 100%;
        justify-content: center;
    }

    .stats-bar {
        flex-direction: column;
        gap: var(--space-md);
    }
}
</style>
"""

def inject_component_styles():
    """Inject component-specific CSS into Streamlit"""
    import streamlit as st
    st.markdown(COMPONENT_CSS, unsafe_allow_html=True)
