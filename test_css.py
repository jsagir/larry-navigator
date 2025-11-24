"""Quick test to check if CSS injection works"""
import streamlit as st

st.set_page_config(page_title="CSS Test")

# Test 1: Simple HTML
st.markdown("""
<div style="background-color: #FF6B35; padding: 1rem; border-radius: 8px;">
    <h3 style="color: white;">Test 1: Inline Styles</h3>
    <p style="color: white;">If you see this styled with orange background, inline styles work!</p>
</div>
""", unsafe_allow_html=True)

# Test 2: CSS in style tag
st.markdown("""
<style>
.test-box {
    background-color: #2A9D8F;
    padding: 1rem;
    border-radius: 8px;
    color: white;
}
</style>

<div class="test-box">
    <h3>Test 2: CSS Classes</h3>
    <p>If you see this styled with teal background, CSS classes work!</p>
</div>
""", unsafe_allow_html=True)

# Test 3: What you're seeing
st.markdown("---")
st.write("If you see raw HTML code above (not styled boxes), there's a Streamlit version issue.")
