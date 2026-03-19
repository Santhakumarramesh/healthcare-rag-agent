"""
Dashboard - Main landing page with quick actions and system overview.
"""
import streamlit as st
import requests
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.layout import load_css, page_header, render_sidebar_status
from components.cards import metric_card, quick_action_card

# Page config
st.set_page_config(
    page_title="Dashboard - Healthcare AI",
    layout="wide",
    page_icon="⚕️",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_css()

# Sidebar
render_sidebar_status()

# Main content
page_header(
    "AI Healthcare Copilot",
    "Evidence-backed medical Q&A, report analysis, and structured clinical insights"
)

# Hero buttons
col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
with col1:
    if st.button("Analyze Report", use_container_width=True):
        st.switch_page("pages/3_Report_Analyzer.py")
with col2:
    if st.button("Ask AI", use_container_width=True):
        st.switch_page("pages/2_Ask_AI.py")

st.markdown("<br>", unsafe_allow_html=True)

# Quick action cards
st.markdown("### Quick Actions")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('''
    <div style="background: white; border: 1px solid #D9E2EC; border-radius: 16px; padding: 20px; text-align: center;">
        <div style="font-size: 16px; font-weight: 600; color: #102A43; margin-bottom: 6px;">Drug Information</div>
        <div style="font-size: 13px; color: #486581;">Search medications</div>
    </div>
    ''', unsafe_allow_html=True)
    if st.button("Learn More", key="drug_btn", use_container_width=True):
        st.session_state["preset_query"] = "Tell me about common drug interactions"
        st.switch_page("pages/2_Ask_AI.py")

with col2:
    st.markdown('''
    <div style="background: white; border: 1px solid #D9E2EC; border-radius: 16px; padding: 20px; text-align: center;">
        <div style="font-size: 16px; font-weight: 600; color: #102A43; margin-bottom: 6px;">Symptom Guidance</div>
        <div style="font-size: 13px; color: #486581;">Check symptoms</div>
    </div>
    ''', unsafe_allow_html=True)
    if st.button("Learn More", key="symptom_btn", use_container_width=True):
        st.session_state["preset_query"] = "What could cause persistent headaches?"
        st.switch_page("pages/2_Ask_AI.py")

with col3:
    st.markdown('''
    <div style="background: white; border: 1px solid #D9E2EC; border-radius: 16px; padding: 20px; text-align: center;">
        <div style="font-size: 16px; font-weight: 600; color: #102A43; margin-bottom: 6px;">Lab Analysis</div>
        <div style="font-size: 13px; color: #486581;">Upload reports</div>
    </div>
    ''', unsafe_allow_html=True)
    if st.button("Analyze Now", key="lab_btn", use_container_width=True):
        st.switch_page("pages/3_Report_Analyzer.py")

with col4:
    st.markdown('''
    <div style="background: white; border: 1px solid #D9E2EC; border-radius: 16px; padding: 20px; text-align: center;">
        <div style="font-size: 16px; font-weight: 600; color: #102A43; margin-bottom: 6px;">Research Summary</div>
        <div style="font-size: 13px; color: #486581;">Medical research</div>
    </div>
    ''', unsafe_allow_html=True)
    if st.button("Learn More", key="research_btn", use_container_width=True):
        st.session_state["preset_query"] = "Summarize the latest research on diabetes management"
        st.switch_page("pages/2_Ask_AI.py")

st.markdown("<br>", unsafe_allow_html=True)

# KPI Row
st.markdown("### System Overview")

API_BASE = os.getenv("API_BASE_URL", "https://healthcare-rag-api.onrender.com")

try:
    stats_response = requests.get(f"{API_BASE}/monitoring/stats", timeout=5)
    if stats_response.status_code == 200:
        stats = stats_response.json().get("stats", {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            metric_card("Total Queries", str(stats.get("total_queries", 0)))
        
        with col2:
            avg_conf = stats.get("avg_confidence", 0)
            metric_card("Avg Confidence", f"{int(avg_conf * 100)}%" if avg_conf > 0 else "N/A")
        
        with col3:
            success_rate = stats.get("success_rate", 1.0)
            metric_card("Success Rate", f"{int(success_rate * 100)}%")
        
        with col4:
            avg_latency = stats.get("avg_latency_ms", 0)
            metric_card("Avg Latency", f"{int(avg_latency)}ms" if avg_latency > 0 else "N/A")
    else:
        st.info("Monitoring data unavailable")
        
except Exception as e:
    st.info("Monitoring data unavailable")

st.markdown("<br>", unsafe_allow_html=True)

# Recent Activity and System Health
col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("### Recent Activity")
    st.markdown('''
    <div style="background: white; border: 1px solid #D9E2EC; border-radius: 16px; padding: 24px;">
        <div style="color: #486581; font-size: 14px; text-align: center; padding: 40px 0;">
            No recent activity
        </div>
    </div>
    ''', unsafe_allow_html=True)

with col2:
    st.markdown("### System Health")
    
    try:
        health_response = requests.get(f"{API_BASE}/health", timeout=5)
        if health_response.status_code == 200:
            health = health_response.json()
            
            st.markdown('''
            <div style="background: white; border: 1px solid #D9E2EC; border-radius: 16px; padding: 24px;">
            ''', unsafe_allow_html=True)
            
            # Pipeline status
            pipeline_status = "Operational" if health.get("pipeline_loaded") else "Degraded"
            pipeline_color = "#2F855A" if health.get("pipeline_loaded") else "#B7791F"
            st.markdown(f'<div style="margin-bottom: 12px;"><span style="color: #486581; font-size: 13px;">Pipeline:</span> <span style="color: {pipeline_color}; font-weight: 600; font-size: 13px;">{pipeline_status}</span></div>', unsafe_allow_html=True)
            
            # Vector store
            vs_status = "Ready" if health.get("vector_store_ready") else "Not Ready"
            vs_color = "#2F855A" if health.get("vector_store_ready") else "#B7791F"
            st.markdown(f'<div style="margin-bottom: 12px;"><span style="color: #486581; font-size: 13px;">Vector Store:</span> <span style="color: {vs_color}; font-weight: 600; font-size: 13px;">{vs_status}</span></div>', unsafe_allow_html=True)
            
            # Model
            model = health.get("model", "N/A")
            st.markdown(f'<div style="margin-bottom: 12px;"><span style="color: #486581; font-size: 13px;">Model:</span> <span style="color: #0F4C81; font-weight: 600; font-size: 13px;">{model}</span></div>', unsafe_allow_html=True)
            
            # Index size
            index_size = health.get("index_size", 0)
            st.markdown(f'<div><span style="color: #486581; font-size: 13px;">Index Size:</span> <span style="color: #0F4C81; font-weight: 600; font-size: 13px;">{index_size:,} vectors</span></div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    except:
        st.error("Unable to fetch system health")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('''
<div style="text-align: center; color: #486581; font-size: 12px; padding: 20px 0; border-top: 1px solid #D9E2EC;">
    Healthcare AI Platform • Production-style medical AI system<br>
    <span style="color: #C53030; font-weight: 600;">⚠ Not medical advice</span> • Consult healthcare professionals for medical decisions
</div>
''', unsafe_allow_html=True)
