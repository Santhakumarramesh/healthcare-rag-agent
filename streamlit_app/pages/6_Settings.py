"""
Settings - Configuration and preferences.
"""
import streamlit as st
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.layout import load_css, page_header, render_sidebar_status

# Page config
st.set_page_config(
    page_title="Settings - Healthcare AI",
    layout="wide",
    page_icon="⚕️",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_css()

# Sidebar
render_sidebar_status()

# Main content
page_header("Settings", "Configure your preferences and system settings")

# Settings sections
st.markdown("### Model Settings")

col1, col2 = st.columns(2)

with col1:
    st.markdown('''
    <div style="background: white; border: 1px solid #D9E2EC; border-radius: 16px; padding: 24px;">
        <div style="font-weight: 600; font-size: 15px; color: #102A43; margin-bottom: 16px;">LLM Model</div>
        <div style="font-size: 14px; color: #486581; margin-bottom: 8px;">Current: <span style="color: #0F4C81; font-weight: 600;">gpt-4o-mini</span></div>
        <div style="font-size: 13px; color: #486581;">Configured via environment variables</div>
    </div>
    ''', unsafe_allow_html=True)

with col2:
    st.markdown('''
    <div style="background: white; border: 1px solid #D9E2EC; border-radius: 16px; padding: 24px;">
        <div style="font-weight: 600; font-size: 15px; color: #102A43; margin-bottom: 16px;">Embedding Model</div>
        <div style="font-size: 14px; color: #486581; margin-bottom: 8px;">Current: <span style="color: #0F4C81; font-weight: 600;">text-embedding-3-small</span></div>
        <div style="font-size: 13px; color: #486581;">Configured via environment variables</div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Retrieval settings
st.markdown("### Retrieval Settings")

col1, col2 = st.columns(2)

with col1:
    st.markdown('''
    <div style="background: white; border: 1px solid #D9E2EC; border-radius: 16px; padding: 24px;">
        <div style="font-weight: 600; font-size: 15px; color: #102A43; margin-bottom: 16px;">Vector Store</div>
        <div style="font-size: 14px; color: #486581; margin-bottom: 8px;">Type: <span style="color: #0F4C81; font-weight: 600;">FAISS</span></div>
        <div style="font-size: 13px; color: #486581;">Local vector similarity search</div>
    </div>
    ''', unsafe_allow_html=True)

with col2:
    st.markdown('''
    <div style="background: white; border: 1px solid #D9E2EC; border-radius: 16px; padding: 24px;">
        <div style="font-weight: 600; font-size: 15px; color: #102A43; margin-bottom: 16px;">Retrieval</div>
        <div style="font-size: 14px; color: #486581; margin-bottom: 8px;">Top-K: <span style="color: #0F4C81; font-weight: 600;">5</span></div>
        <div style="font-size: 13px; color: #486581;">Maximum documents retrieved per query</div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Safety settings
st.markdown("### Safety Settings")

st.markdown('''
<div style="background: white; border: 1px solid #D9E2EC; border-radius: 16px; padding: 24px;">
    <div style="font-weight: 600; font-size: 15px; color: #102A43; margin-bottom: 16px;">Clinical Alert Engine</div>
    <div style="font-size: 14px; color: #486581; margin-bottom: 12px;">Status: <span style="color: #2F855A; font-weight: 600;">✓ Active</span></div>
    <div style="font-size: 13px; color: #486581; line-height: 1.6;">
        Monitors for 14 emergency symptoms, drug interactions, and critical lab values.
        Automatic alerts triggered for high-risk queries.
    </div>
</div>
''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# UI Mode
st.markdown("### UI Preferences")

mode = st.radio(
    "Display Mode",
    ["Patient-Friendly", "Professional/Clinical"],
    help="Choose how technical the explanations should be"
)

if mode == "Patient-Friendly":
    st.session_state["ui_mode"] = "patient"
    st.success("Mode set to Patient-Friendly - simpler explanations")
else:
    st.session_state["ui_mode"] = "professional"
    st.success("Mode set to Professional - more technical detail")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('''
<div style="text-align: center; color: #486581; font-size: 12px; padding: 20px 0; border-top: 1px solid #D9E2EC;">
    Settings are stored in your session • Some settings require API configuration
</div>
''', unsafe_allow_html=True)
