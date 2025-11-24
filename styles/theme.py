"""
Warm Educational Theme for Larry Navigator v2.0
Cream background, teal accents, warm and inviting
"""

WARM_THEME_CSS = """
<style>
/* ============================================
   WARM EDUCATIONAL THEME - Larry Navigator v2.0
   ============================================ */

:root {
    /* === Foundation Colors === */
    --cream-bg: #FCFCF9;
    --cream-light: #FFFFFF;
    --cream-dark: #F5F5F0;

    /* === Primary Palette === */
    --teal-primary: #2A9D8F;
    --teal-light: #3DB8A8;
    --teal-dark: #1E7A6F;
    --teal-bg: rgba(42, 157, 143, 0.08);

    /* === Accent Colors === */
    --orange-warm: #E76F51;
    --orange-light: #F4A261;
    --coral-soft: #FF9B85;

    /* === PWS Triad === */
    --pws-real: #E76F51;        /* Warm orange - Evidence */
    --pws-winnable: #2A9D8F;    /* Teal - Feasibility */
    --pws-worth: #F4A261;       /* Golden orange - Value */

    /* === Problem Definition Track === */
    --undefined: #9B59B6;       /* Purple - Exploration */
    --ill-defined: #3498DB;     /* Blue - Investigation */
    --well-defined: #27AE60;    /* Green - Clarity */

    /* === Cynefin Complexity === */
    --simple: #27AE60;          /* Green - Clear cause-effect */
    --complicated: #3498DB;     /* Blue - Analyzable */
    --complex: #E67E22;         /* Orange - Emergent */
    --chaotic: #E74C3C;         /* Red - No patterns */

    /* === Wickedness Scale === */
    --tame: #27AE60;            /* Green - Well-bounded */
    --messy: #F39C12;           /* Yellow - Multiple stakeholders */
    --complex-wicked: #E67E22;  /* Orange - Interconnected */
    --wicked: #C0392B;          /* Dark red - No stopping rule */

    /* === Text Colors === */
    --text-primary: #2C3E50;
    --text-secondary: #5A6C7D;
    --text-muted: #95A5A6;
    --text-inverse: #FFFFFF;

    /* === Borders & Shadows === */
    --border-light: #E8E8E3;
    --border-medium: #D1D1CC;
    --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
    --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.10);
    --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);

    /* === Typography === */
    --font-display: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono: 'JetBrains Mono', 'Courier New', monospace;

    /* === Spacing === */
    --space-xs: 0.25rem;
    --space-sm: 0.5rem;
    --space-md: 1rem;
    --space-lg: 1.5rem;
    --space-xl: 2rem;
    --space-xxl: 3rem;

    /* === Border Radius === */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
    --radius-xl: 16px;
    --radius-full: 9999px;

    /* === Transitions === */
    --transition-fast: 150ms ease;
    --transition-normal: 250ms ease;
    --transition-slow: 350ms ease;
}

/* === Global Resets === */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* === Main App Background === */
.stApp {
    background-color: var(--cream-bg) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
}

/* === Main Container === */
.main .block-container {
    max-width: 1200px !important;
    padding: var(--space-xl) var(--space-lg) !important;
}

/* === Headers === */
h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-display) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}

h1 {
    font-size: 2.5rem !important;
    margin-bottom: var(--space-lg) !important;
}

h2 {
    font-size: 2rem !important;
    margin-bottom: var(--space-md) !important;
}

h3 {
    font-size: 1.5rem !important;
    margin-bottom: var(--space-md) !important;
}

/* === Paragraphs === */
p {
    color: var(--text-secondary) !important;
    line-height: 1.6 !important;
    margin-bottom: var(--space-md) !important;
}

/* === Links === */
a {
    color: var(--teal-primary) !important;
    text-decoration: none !important;
    transition: color var(--transition-fast) !important;
}

a:hover {
    color: var(--teal-dark) !important;
    text-decoration: underline !important;
}

/* === Buttons === */
.stButton > button {
    background-color: var(--teal-primary) !important;
    color: var(--text-inverse) !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: var(--space-sm) var(--space-lg) !important;
    font-weight: 500 !important;
    font-family: var(--font-body) !important;
    transition: all var(--transition-normal) !important;
    box-shadow: var(--shadow-sm) !important;
}

.stButton > button:hover {
    background-color: var(--teal-dark) !important;
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-1px) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* === Chat Input === */
.stChatInputContainer {
    background-color: var(--cream-light) !important;
    border: 2px solid var(--border-light) !important;
    border-radius: var(--radius-lg) !important;
    padding: var(--space-sm) !important;
    margin-top: var(--space-lg) !important;
    box-shadow: var(--shadow-sm) !important;
}

.stChatInputContainer:focus-within {
    border-color: var(--teal-primary) !important;
    box-shadow: 0 0 0 3px var(--teal-bg) !important;
}

/* === Chat Messages === */
[data-testid="stChatMessageContent"] {
    background-color: var(--cream-light) !important;
    border-radius: var(--radius-lg) !important;
    padding: var(--space-lg) !important;
    margin-bottom: var(--space-md) !important;
    box-shadow: var(--shadow-sm) !important;
    border: 1px solid var(--border-light) !important;
}

/* Larry's Messages */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #FFFFFF 0%, var(--cream-light) 100%) !important;
    border-left: 4px solid var(--teal-primary) !important;
}

/* User Messages */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background-color: var(--teal-bg) !important;
    border-left: 4px solid var(--teal-light) !important;
}

/* === Sidebar === */
[data-testid="stSidebar"] {
    background-color: var(--cream-light) !important;
    border-right: 1px solid var(--border-light) !important;
    padding: var(--space-lg) !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--text-primary) !important;
}

/* === Cards === */
.diagnostic-card {
    background: var(--cream-light);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    padding: var(--space-lg);
    margin-bottom: var(--space-md);
    box-shadow: var(--shadow-sm);
    transition: all var(--transition-normal);
}

.diagnostic-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}

/* === PWS Badges === */
.pws-badge {
    display: inline-block;
    padding: var(--space-xs) var(--space-md);
    border-radius: var(--radius-full);
    font-size: 0.875rem;
    font-weight: 500;
    margin-right: var(--space-sm);
    transition: all var(--transition-fast);
}

.pws-badge-real {
    background-color: rgba(231, 111, 81, 0.12);
    color: var(--pws-real);
    border: 1px solid var(--pws-real);
}

.pws-badge-winnable {
    background-color: rgba(42, 157, 143, 0.12);
    color: var(--pws-winnable);
    border: 1px solid var(--pws-winnable);
}

.pws-badge-worth {
    background-color: rgba(244, 162, 97, 0.12);
    color: var(--pws-worth);
    border: 1px solid var(--pws-worth);
}

/* === Progress Indicators === */
.progress-track {
    display: flex;
    align-items: center;
    gap: var(--space-sm);
    padding: var(--space-md);
    background: var(--cream-light);
    border-radius: var(--radius-md);
    margin-bottom: var(--space-md);
}

.progress-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: var(--border-medium);
    transition: all var(--transition-normal);
}

.progress-dot.active {
    background-color: var(--teal-primary);
    box-shadow: 0 0 0 4px var(--teal-bg);
    transform: scale(1.3);
}

.progress-dot.completed {
    background-color: var(--well-defined);
}

/* === Slider === */
.risk-uncertainty-slider {
    width: 100%;
    height: 8px;
    background: linear-gradient(90deg,
        var(--well-defined) 0%,
        var(--orange-warm) 100%);
    border-radius: var(--radius-full);
    position: relative;
    margin: var(--space-lg) 0;
}

.slider-marker {
    position: absolute;
    top: 50%;
    transform: translate(-50%, -50%);
    width: 20px;
    height: 20px;
    background: var(--cream-light);
    border: 3px solid var(--teal-primary);
    border-radius: 50%;
    box-shadow: var(--shadow-md);
    transition: all var(--transition-normal);
}

/* === Loading States === */
.typing-indicator {
    display: flex;
    gap: var(--space-xs);
    padding: var(--space-md);
}

.typing-dot {
    width: 8px;
    height: 8px;
    background-color: var(--teal-primary);
    border-radius: 50%;
    animation: typing 1.4s infinite;
}

.typing-dot:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing {
    0%, 60%, 100% {
        transform: translateY(0);
        opacity: 0.5;
    }
    30% {
        transform: translateY(-10px);
        opacity: 1;
    }
}

/* === Animations === */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideIn {
    from {
        transform: translateX(-20px);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.fade-in {
    animation: fadeIn var(--transition-normal);
}

.slide-in {
    animation: slideIn var(--transition-normal);
}

/* === Responsive Design === */
@media (max-width: 768px) {
    .main .block-container {
        padding: var(--space-md) var(--space-sm) !important;
    }

    h1 {
        font-size: 2rem !important;
    }

    h2 {
        font-size: 1.5rem !important;
    }

    .diagnostic-card {
        padding: var(--space-md);
    }

    .pws-badge {
        display: block;
        margin: var(--space-xs) 0;
    }
}

/* === Utility Classes === */
.text-center {
    text-align: center;
}

.mt-1 { margin-top: var(--space-sm); }
.mt-2 { margin-top: var(--space-md); }
.mt-3 { margin-top: var(--space-lg); }

.mb-1 { margin-bottom: var(--space-sm); }
.mb-2 { margin-bottom: var(--space-md); }
.mb-3 { margin-bottom: var(--space-lg); }

.p-1 { padding: var(--space-sm); }
.p-2 { padding: var(--space-md); }
.p-3 { padding: var(--space-lg); }
</style>
"""

def inject_warm_theme():
    """Inject the warm educational theme CSS into Streamlit"""
    import streamlit as st
    st.markdown(WARM_THEME_CSS, unsafe_allow_html=True)
