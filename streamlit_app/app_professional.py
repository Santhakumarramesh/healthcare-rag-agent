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
from components.ui_helpers import inject_global_styles, render_hero

# Page config
st.set_page_config(
    page_title="Healthcare AI Platform",
    layout="wide",
    page_icon="⚕️",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_css()
inject_global_styles()

# Initialize session state
if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

if "history" not in st.session_state:
    st.session_state.history = []

if "ui_mode" not in st.session_state:
    st.session_state.ui_mode = "patient"

if "care_mode" not in st.session_state:
    st.session_state.care_mode = None

if "followup_profile" not in st.session_state:
    st.session_state.followup_profile = {
        "condition_name": "",
        "diagnosis_date": None,
        "primary_symptoms": "",
        "current_medications": "",
        "doctor_notes": "",
        "is_initialized": False,
    }

if "daily_updates" not in st.session_state:
    st.session_state.daily_updates = []

# Sidebar navigation
st.sidebar.markdown('''
<div style="text-align: center; padding: 20px 0;">
    <div style="font-size: 24px; font-weight: 700; color: #0F4C81;">Healthcare AI</div>
    <div style="font-size: 13px; color: #486581; margin-top: 4px;">Clinical Intelligence Platform</div>
</div>
''', unsafe_allow_html=True)

st.sidebar.markdown("---")

# Navigation
st.sidebar.page_link("pages/1_Dashboard.py", label="Dashboard")
st.sidebar.page_link("pages/2_Ask_AI.py", label="Ask AI")
st.sidebar.page_link("pages/3_Report_Analyzer.py", label="Report Analyzer")
st.sidebar.page_link("pages/7_Serious_Condition_Follow_Up.py", label="Condition Follow-up")
st.sidebar.page_link("pages/4_Records_History.py", label="Records & History")
st.sidebar.page_link("pages/5_Monitoring.py", label="Monitoring")
st.sidebar.page_link("pages/6_Settings.py", label="Settings")

# Sidebar status
render_sidebar_status()

# Main content - mode selector
render_hero(
    "AI Healthcare Copilot",
    "Evidence-backed medical Q&A, report analysis, and structured follow-up workflows designed for safer, clearer health support.",
)

st.markdown('<div class="section-title">Choose Care Mode</div>', unsafe_allow_html=True)

col_a, col_b, col_c, col_d = st.columns(4, gap="large")

with col_a:
    st.markdown(
        """
        <div class="mode-card">
            <div class="mode-title">General Medical Q&A</div>
            <div class="mode-desc">
                Ask grounded health questions and receive structured, evidence-aware responses.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Open General Q&A", key="mode_general", use_container_width=True):
        st.session_state.care_mode = "general_qa"
        st.switch_page("pages/2_Ask_AI.py")

with col_b:
    st.markdown(
        """
        <div class="mode-card">
            <div class="mode-title">Report Analyzer</div>
            <div class="mode-desc">
                Upload and interpret reports, summarize findings, and review key extracted values.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Open Report Analyzer", key="mode_report", use_container_width=True):
        st.session_state.care_mode = "report_analyzer"
        st.switch_page("pages/3_Report_Analyzer.py")

with col_c:
    st.markdown(
        """
        <div class="mode-card">
            <div class="mode-title">Serious Condition Follow-up</div>
            <div class="mode-desc">
                Track daily condition updates, compare with previous entries, and surface worsening-risk patterns.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Start Follow-up Mode", key="mode_followup", use_container_width=True):
        st.session_state.care_mode = "serious_followup"
        st.switch_page("pages/7_Serious_Condition_Follow_Up.py")

with col_d:
    st.markdown(
        """
        <div class="mode-card">
            <div class="mode-title">Research Summary</div>
            <div class="mode-desc">
                Summarize clinical information, medical knowledge, and evidence-backed reference material.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Open Research Summary", key="mode_research", use_container_width=True):
        st.session_state.care_mode = "research_summary"
        st.switch_page("pages/2_Ask_AI.py")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">Recommended Starting Point</div>', unsafe_allow_html=True)

left, right = st.columns([1.4, 1], gap="large")

with left:
    st.markdown(
        """
        <div class="panel-card">
            <div class="mini-heading">Daily Follow-up for High-Risk or Serious Conditions</div>
            <div class="subtle-text">
                Use this mode for users who are recovering after hospitalization, living with a serious ongoing condition,
                or requiring daily monitoring for worsening symptoms, medication adherence, or physician-directed observation.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Go to Serious Condition Follow-up", key="goto_followup_big", use_container_width=False):
        st.session_state.care_mode = "serious_followup"
        st.switch_page("pages/7_Serious_Condition_Follow_Up.py")

with right:
    st.markdown(
        f"""
        <div class="panel-card">
            <div class="mini-heading">Current Session</div>
            <div class="subtle-text">
                Selected mode: {st.session_state.care_mode or "Not selected"}
            </div>
            <div class="subtle-text" style="margin-top:8px;">
                Daily updates saved: {len(st.session_state.daily_updates)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Footer
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown('''
<div style="text-align: center; color: #486581; font-size: 12px; padding: 20px 0; border-top: 1px solid #D9E2EC;">
    Healthcare AI Platform v2.0 • Built with FastAPI + Streamlit + LangChain<br>
    <span style="color: #C53030; font-weight: 600;">⚠ Not medical advice</span> • Always consult healthcare professionals
</div>
''', unsafe_allow_html=True)
