"""
Healthcare AI Platform - Professional Clinical SaaS Interface

Main entry point with clean navigation and professional theme.
"""
import streamlit as st
import os
import sys
from pathlib import Path

# Add components to path
sys.path.insert(0, str(Path(__file__).parent))

from components.layout import load_css, render_sidebar_status

# Page config
st.set_page_config(
    page_title="Healthcare AI Platform",
    layout="wide",
    page_icon="🏥",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_css()

# Initialize session state
if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

if "history" not in st.session_state:
    st.session_state.history = []

if "ui_mode" not in st.session_state:
    st.session_state.ui_mode = "patient"

# Sidebar navigation
st.sidebar.markdown('''
<div style="text-align: center; padding: 20px 0;">
    <div style="font-size: 24px; font-weight: 700; color: #0F4C81;">Healthcare AI</div>
    <div style="font-size: 13px; color: #486581; margin-top: 4px;">Clinical Intelligence Platform</div>
</div>
''', unsafe_allow_html=True)

st.sidebar.markdown("---")

# Navigation
st.sidebar.page_link("pages/1_Dashboard.py", label="Dashboard", icon="🏠")
st.sidebar.page_link("pages/2_Ask_AI.py", label="Ask AI", icon="💬")
st.sidebar.page_link("pages/3_Report_Analyzer.py", label="Report Analyzer", icon="📋")
st.sidebar.page_link("pages/4_Records_History.py", label="Records & History", icon="📁")
st.sidebar.page_link("pages/5_Monitoring.py", label="Monitoring", icon="📊")
st.sidebar.page_link("pages/6_Settings.py", label="Settings", icon="⚙️")

# Sidebar status
render_sidebar_status()

# Main content - redirect to dashboard
st.markdown('''
<div style="text-align: center; padding: 100px 0;">
    <div style="font-size: 48px; margin-bottom: 24px;">🏥</div>
    <div style="font-size: 32px; font-weight: 700; color: #102A43; margin-bottom: 12px;">Healthcare AI Platform</div>
    <div style="font-size: 16px; color: #486581; margin-bottom: 32px;">Production-style medical AI system</div>
</div>
''', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("📊 View Dashboard", use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")

with col2:
    if st.button("💬 Ask AI", use_container_width=True):
        st.switch_page("pages/2_Ask_AI.py")

with col3:
    if st.button("📋 Analyze Report", use_container_width=True):
        st.switch_page("pages/3_Report_Analyzer.py")

# Footer
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown('''
<div style="text-align: center; color: #486581; font-size: 12px; padding: 20px 0; border-top: 1px solid #D9E2EC;">
    Healthcare AI Platform v2.0 • Built with FastAPI + Streamlit + LangChain<br>
    <span style="color: #C53030; font-weight: 600;">⚠ Not medical advice</span> • Always consult healthcare professionals
</div>
''', unsafe_allow_html=True)
