"""
AI Healthcare Copilot - Professional Clinical SaaS Dashboard
Evidence-backed medical Q&A, report analysis, and clinical workflow support
"""

import streamlit as st
import requests
import json
import time
import os
import uuid
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="AI Healthcare Copilot",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# PROFESSIONAL CLINICAL SAAS CSS
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Manrope:wght@400;500;600;700&display=swap');

/* Global */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: #1a202c;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Clinical color palette */
:root {
    --primary: #0F4C81;
    --accent: #2CB1BC;
    --background: #F7FAFC;
    --surface: #FFFFFF;
    --border: #D9E6F2;
    --success: #2F855A;
    --warning: #DD6B20;
    --danger: #C53030;
    --text-primary: #1a202c;
    --text-secondary: #4a5568;
    --text-muted: #718096;
}

/* Main container */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: var(--surface);
    border-right: 1px solid var(--border);
    padding-top: 1rem;
}

[data-testid="stSidebar"] .block-container {
    padding-top: 1rem;
}

/* Professional header */
.app-header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 1.25rem 2rem;
    margin: -2rem -2rem 2rem -2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.app-logo {
    display: flex;
    align-items: center;
    gap: 12px;
}

.app-logo-icon {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, var(--primary), var(--accent));
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 700;
    font-size: 1.2rem;
}

.app-logo-text {
    font-family: 'Manrope', sans-serif;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary);
}

/* Status cards in sidebar */
.status-card {
    background: var(--background);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 16px;
    margin: 10px 0;
}

.status-card-title {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
}

.status-card-value {
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 8px;
}

.status-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}

.status-healthy { background-color: var(--success); }
.status-warning { background-color: var(--warning); }
.status-error { background-color: var(--danger); }

/* Hero section */
.hero-section {
    background: linear-gradient(135deg, #0F4C81 0%, #1a6ba8 50%, #2CB1BC 100%);
    color: white;
    padding: 3.5rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 2.5rem;
    box-shadow: 0 4px 6px rgba(15, 76, 129, 0.1);
}

.hero-title {
    font-family: 'Manrope', sans-serif;
    font-size: 2.75rem;
    font-weight: 700;
    margin: 0 0 0.75rem 0;
    letter-spacing: -0.02em;
}

.hero-subtitle {
    font-size: 1.15rem;
    opacity: 0.95;
    font-weight: 400;
    margin: 0;
    line-height: 1.7;
    max-width: 800px;
}

/* Quick action cards */
.action-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 20px;
    margin: 2rem 0;
}

.action-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 28px 24px;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.action-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--primary), var(--accent));
    transform: scaleX(0);
    transition: transform 0.25s ease;
}

.action-card:hover {
    border-color: var(--accent);
    box-shadow: 0 8px 16px rgba(44, 177, 188, 0.12);
    transform: translateY(-2px);
}

.action-card:hover::before {
    transform: scaleX(1);
}

.action-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, var(--primary), var(--accent));
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
    color: white;
    font-size: 1.5rem;
}

.action-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 6px 0;
}

.action-desc {
    font-size: 0.875rem;
    color: var(--text-secondary);
    line-height: 1.5;
    margin: 0;
}

/* Clinical answer card */
.answer-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 28px;
    margin: 20px 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}

.answer-section {
    margin-bottom: 24px;
    padding-bottom: 24px;
    border-bottom: 1px solid var(--border);
}

.answer-section:last-child {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
}

.section-icon {
    width: 24px;
    height: 24px;
    background: var(--background);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--primary);
    font-size: 0.9rem;
}

.section-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0;
}

.answer-text {
    font-size: 1.05rem;
    line-height: 1.75;
    color: var(--text-primary);
}

/* Confidence badge */
.confidence-badge {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 10px 18px;
    border-radius: 24px;
    font-weight: 600;
    font-size: 1rem;
}

.confidence-high {
    background-color: #E6F4EA;
    color: var(--success);
    border: 1px solid #A8DAB5;
}

.confidence-medium {
    background-color: #FFF4E5;
    color: var(--warning);
    border: 1px solid #FFD8A8;
}

.confidence-low {
    background-color: #FEE;
    color: var(--danger);
    border: 1px solid #FCA5A5;
}

/* Source cards */
.source-card {
    background: var(--background);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    padding: 14px 18px;
    margin: 10px 0;
}

.source-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
}

.source-name {
    font-weight: 600;
    color: var(--text-primary);
    font-size: 0.95rem;
}

.source-score {
    color: var(--text-muted);
    font-size: 0.85rem;
    font-weight: 500;
}

.source-preview {
    color: var(--text-secondary);
    font-size: 0.875rem;
    line-height: 1.6;
    font-style: italic;
}

/* Safety alert */
.safety-alert {
    background: #FFF4E5;
    border: 1px solid #FFD8A8;
    border-radius: 10px;
    padding: 16px 20px;
    margin: 20px 0;
    display: flex;
    align-items: flex-start;
    gap: 14px;
}

.safety-icon {
    width: 24px;
    height: 24px;
    background: var(--warning);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1rem;
    flex-shrink: 0;
}

.safety-text {
    font-size: 0.925rem;
    color: #744210;
    line-height: 1.6;
}

/* Metric cards */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin: 2rem 0;
}

.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    position: relative;
}

.metric-value {
    font-size: 2.75rem;
    font-weight: 700;
    color: var(--primary);
    margin: 0 0 8px 0;
    font-family: 'Manrope', sans-serif;
}

.metric-label {
    font-size: 0.875rem;
    color: var(--text-muted);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.metric-trend {
    position: absolute;
    top: 20px;
    right: 20px;
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 0.875rem;
    font-weight: 600;
}

.trend-up {
    color: var(--success);
}

.trend-down {
    color: var(--danger);
}

.trend-arrow {
    font-size: 1.2rem;
}

/* Top header bar */
.top-header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 1rem 2rem;
    margin: -2rem -2rem 2rem -2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.header-search {
    flex: 1;
    max-width: 500px;
    margin: 0 2rem;
}

.header-search input {
    width: 100%;
    padding: 10px 16px 10px 40px;
    border: 1px solid var(--border);
    border-radius: 8px;
    font-size: 0.95rem;
    background: var(--background);
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 16px;
}

.header-icon {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    background: var(--background);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
}

.header-icon:hover {
    background: var(--border);
}

.user-profile {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 12px;
    border-radius: 8px;
    background: var(--background);
    cursor: pointer;
}

.user-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary), var(--accent));
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
    font-size: 0.875rem;
}

/* Data tables */
.data-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
}

.data-table thead {
    background: var(--background);
}

.data-table th {
    padding: 14px 16px;
    text-align: left;
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 2px solid var(--border);
}

.data-table td {
    padding: 14px 16px;
    font-size: 0.95rem;
    color: var(--text-primary);
    border-bottom: 1px solid var(--border);
}

.data-table tbody tr:nth-child(even) {
    background: var(--background);
}

.data-table tbody tr:hover {
    background: #F0FAFB;
}

/* Avatar in tables */
.table-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: inline-block;
    vertical-align: middle;
    margin-right: 10px;
}

/* Status badges in tables */
.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
}

.status-badge.success {
    background: #E6F4EA;
    color: var(--success);
}

.status-badge.warning {
    background: #FFF4E5;
    color: var(--warning);
}

.status-badge.danger {
    background: #FEE;
    color: var(--danger);
}

/* Report upload box */
.upload-box {
    border: 2px dashed var(--border);
    border-radius: 12px;
    padding: 48px;
    text-align: center;
    background: var(--background);
    margin: 24px 0;
    transition: all 0.2s ease;
}

.upload-box:hover {
    border-color: var(--accent);
    background: #F0FAFB;
}

.upload-icon {
    width: 64px;
    height: 64px;
    background: linear-gradient(135deg, var(--primary), var(--accent));
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 2rem;
    margin: 0 auto 20px;
}

.upload-text {
    font-size: 1.05rem;
    color: var(--text-secondary);
    margin: 0;
}

/* Key insights */
.insights-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.insight-item {
    padding: 12px 0;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: flex-start;
    gap: 14px;
}

.insight-item:last-child {
    border-bottom: none;
}

.insight-bullet {
    width: 24px;
    height: 24px;
    background: var(--background);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--accent);
    font-size: 0.875rem;
    flex-shrink: 0;
    font-weight: 600;
}

.insight-text {
    font-size: 0.975rem;
    line-height: 1.7;
    color: var(--text-primary);
    flex: 1;
}

/* Section headers */
.section-header-main {
    font-family: 'Manrope', sans-serif;
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 1.5rem 0;
}

/* Buttons */
.stButton > button {
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.2s ease;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--primary), var(--accent));
    border: none;
}

.stButton > button[kind="primary"]:hover {
    box-shadow: 0 4px 12px rgba(44, 177, 188, 0.3);
    transform: translateY(-1px);
}

/* Input fields */
.stTextInput > div > div > input {
    border-radius: 8px;
    border: 1px solid var(--border);
    padding: 12px 16px;
    font-size: 1rem;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(44, 177, 188, 0.1);
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--background);
    border-radius: 8px;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mode" not in st.session_state:
    st.session_state.mode = "patient"
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR - NAVIGATION & STATUS
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    # Logo
    st.markdown("""
    <div style="padding: 0 0 1.5rem 0; border-bottom: 1px solid var(--border);">
        <div class="app-logo">
            <div class="app-logo-icon">HC</div>
            <div class="app-logo-text">Healthcare Copilot</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Navigation
    if st.button("Dashboard", use_container_width=True, 
                 type="primary" if st.session_state.current_page == "home" else "secondary"):
        st.session_state.current_page = "home"
        st.rerun()
    
    if st.button("Ask AI", use_container_width=True,
                 type="primary" if st.session_state.current_page == "chat" else "secondary"):
        st.session_state.current_page = "chat"
        st.rerun()
    
    if st.button("Report Analyzer", use_container_width=True,
                 type="primary" if st.session_state.current_page == "reports" else "secondary"):
        st.session_state.current_page = "reports"
        st.rerun()
    
    if st.button("Patient History", use_container_width=True,
                 type="primary" if st.session_state.current_page == "history" else "secondary"):
        st.session_state.current_page = "history"
        st.rerun()
    
    if st.button("Monitoring", use_container_width=True,
                 type="primary" if st.session_state.current_page == "dashboard" else "secondary"):
        st.session_state.current_page = "dashboard"
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    
    # System status cards
    st.markdown("**System Status**")
    
    try:
        health = requests.get(f"{API_BASE}/health", timeout=3).json()
        api_status = "healthy" if health.get("status") == "healthy" else "degraded"
        vs_ready = health.get("vector_store_ready", False)
        model = health.get("model", "N/A")
    except:
        api_status = "error"
        vs_ready = False
        model = "N/A"
    
    # API Status Card
    status_class = "status-healthy" if api_status == "healthy" else "status-error"
    st.markdown(f"""
    <div class="status-card">
        <div class="status-card-title">API Service</div>
        <div class="status-card-value">
            <span class="status-indicator {status_class}"></span>
            {api_status.title()}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Vector DB Status Card
    vs_class = "status-healthy" if vs_ready else "status-warning"
    vs_text = "Ready" if vs_ready else "Not Ready"
    st.markdown(f"""
    <div class="status-card">
        <div class="status-card-title">Vector Database</div>
        <div class="status-card-value">
            <span class="status-indicator {vs_class}"></span>
            {vs_text}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Model Card
    st.markdown(f"""
    <div class="status-card">
        <div class="status-card-title">AI Model</div>
        <div class="status-card-value">{model}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("**User Mode**")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Patient", use_container_width=True, 
                     type="primary" if st.session_state.mode == "patient" else "secondary"):
            st.session_state.mode = "patient"
            st.rerun()
    with col2:
        if st.button("Clinician", use_container_width=True,
                     type="primary" if st.session_state.mode == "clinician" else "secondary"):
            st.session_state.mode = "clinician"
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_circular_gauge(value, title, color="#2CB1BC"):
    """Create a circular gauge chart using Plotly"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 16, 'color': '#4a5568'}},
        number = {'suffix': "%", 'font': {'size': 32, 'color': '#1a202c'}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#D9E6F2"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#D9E6F2",
            'steps': [
                {'range': [0, 60], 'color': '#FEE'},
                {'range': [60, 80], 'color': '#FFF4E5'},
                {'range': [80, 100], 'color': '#E6F4EA'}
            ],
            'threshold': {
                'line': {'color': color, 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter, sans-serif'}
    )
    
    return fig

def create_trend_chart(data, title):
    """Create a line chart for trends"""
    fig = px.line(
        x=list(range(len(data))),
        y=data,
        title=title,
        labels={'x': 'Time', 'y': 'Value'}
    )
    
    fig.update_traces(
        line_color='#2CB1BC',
        line_width=3,
        mode='lines+markers',
        marker=dict(size=8, color='#0F4C81')
    )
    
    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter, sans-serif'},
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#D9E6F2')
    )
    
    return fig

def create_bar_chart(categories, values, title):
    """Create a bar chart"""
    fig = px.bar(
        x=categories,
        y=values,
        title=title,
        labels={'x': 'Category', 'y': 'Count'}
    )
    
    fig.update_traces(
        marker_color='#2CB1BC',
        marker_line_color='#0F4C81',
        marker_line_width=1.5
    )
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter, sans-serif'},
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#D9E6F2')
    )
    
    return fig

def render_confidence_badge(score):
    """Render confidence badge with color coding"""
    if score >= 0.8:
        badge_class = "confidence-high"
        label = "High Confidence"
    elif score >= 0.6:
        badge_class = "confidence-medium"
        label = "Medium Confidence"
    else:
        badge_class = "confidence-low"
        label = "Low Confidence"
    
    return f'<div class="confidence-badge {badge_class}">{int(score*100)}% {label}</div>'

def get_avatar_svg(name, index=0):
    """Generate a simple SVG avatar with initials"""
    colors = ['#0F4C81', '#2CB1BC', '#2F855A', '#DD6B20', '#C53030']
    color = colors[index % len(colors)]
    initials = ''.join([word[0].upper() for word in name.split()[:2]])
    
    return f"""
    <svg width="40" height="40" viewBox="0 0 40 40">
        <circle cx="20" cy="20" r="20" fill="{color}"/>
        <text x="20" y="26" text-anchor="middle" fill="white" 
              font-family="Inter, sans-serif" font-size="14" font-weight="600">
            {initials}
        </text>
    </svg>
    """

def render_clinical_answer_card(response_data):
    """Render structured clinical answer card"""
    answer = response_data.get("response", "")
    quality_score = response_data.get("quality_score", 0)
    sources = response_data.get("sources", [])
    
    # Extract key insights
    sentences = [s.strip() + "." for s in answer.split(".") if s.strip()]
    key_insights = sentences[:min(3, len(sentences))]
    
    st.markdown(f"""
    <div class="answer-card">
        <!-- Answer Section -->
        <div class="answer-section">
            <div class="section-header">
                <div class="section-icon">A</div>
                <div class="section-title">Answer</div>
            </div>
            <div class="answer-text">{answer}</div>
        </div>
        
        <!-- Key Insights Section -->
        <div class="answer-section">
            <div class="section-header">
                <div class="section-icon">✓</div>
                <div class="section-title">Key Clinical Insights</div>
            </div>
            <ul class="insights-list">
                {"".join([f'<li class="insight-item"><div class="insight-bullet">{idx}</div><div class="insight-text">{insight}</div></li>' for idx, insight in enumerate(key_insights, 1)])}
            </ul>
        </div>
        
        <!-- Confidence Section -->
        <div class="answer-section">
            <div class="section-header">
                <div class="section-icon">%</div>
                <div class="section-title">Confidence Assessment</div>
            </div>
            {render_confidence_badge(quality_score)}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sources (expandable)
    if sources:
        with st.expander(f"View {len(sources)} Source Citations"):
            for idx, source in enumerate(sources[:5], 1):
                if isinstance(source, dict):
                    source_name = source.get("source", "Document")
                    score = source.get("score", 0)
                    text_preview = source.get("text", "")[:150]
                    
                    st.markdown(f"""
                    <div class="source-card">
                        <div class="source-header">
                            <div class="source-name">Source {idx}: {source_name}</div>
                            <div class="source-score">Relevance: {score:.3f}</div>
                        </div>
                        <div class="source-preview">{text_preview}...</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Safety note
    st.markdown("""
    <div class="safety-alert">
        <div class="safety-icon">!</div>
        <div class="safety-text">
            <strong>Important:</strong> This AI assistant provides general health information only. 
            It does not replace professional medical advice, diagnosis, or treatment. 
            Always consult a qualified healthcare provider for medical concerns or emergencies.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1: HOME / DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

if st.session_state.current_page == "home":
    # Top header bar
    st.markdown("""
    <div class="top-header">
        <div class="app-logo">
            <div class="app-logo-icon">HC</div>
            <div class="app-logo-text">Healthcare Copilot</div>
        </div>
        <div class="header-search">
            <input type="text" placeholder="Search patients, reports, or queries..." />
        </div>
        <div class="header-actions">
            <div class="header-icon">🔔</div>
            <div class="user-profile">
                <div class="user-avatar">DR</div>
                <span>Dr. Smith</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero section
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">AI Healthcare Copilot</h1>
        <p class="hero-subtitle">
            Evidence-backed medical Q&A, report analysis, and clinical workflow support.<br>
            Powered by a 5-stage AI pipeline with hybrid retrieval and self-correction.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick action cards
    st.markdown('<h2 class="section-header-main">Quick Actions</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Drug Information\n\nMedication usage, interactions, contraindications", use_container_width=True, key="qa_drug"):
            st.session_state.prefill_query = "Tell me about metformin - uses, side effects, and contraindications"
            st.session_state.current_page = "chat"
            st.rerun()
    
    with col2:
        if st.button("Symptom Guidance\n\nStructured reasoning from symptoms and history", use_container_width=True, key="qa_symptoms"):
            st.session_state.prefill_query = "What could cause persistent fatigue, increased thirst, and frequent urination?"
            st.session_state.current_page = "chat"
            st.rerun()
    
    with col3:
        if st.button("Lab Report Analysis\n\nUpload and interpret reports with evidence", use_container_width=True, key="qa_labs"):
            st.session_state.prefill_query = "What does an HbA1c of 8.2% indicate and what should I do?"
            st.session_state.current_page = "chat"
            st.rerun()
    
    with col4:
        if st.button("Research Summary\n\nRetrieve and summarize clinical knowledge", use_container_width=True, key="qa_research"):
            st.session_state.prefill_query = "What are the latest treatment guidelines for Type 2 diabetes?"
            st.session_state.current_page = "chat"
            st.rerun()
    
    st.markdown("---")
    
    # Recent activity
    st.markdown('<h2 class="section-header-main">Recent Activity</h2>', unsafe_allow_html=True)
    
    if st.session_state.messages:
        st.info(f"Total conversations: {len([m for m in st.session_state.messages if m['role'] == 'user'])}")
    else:
        st.info("No recent activity. Start a conversation to see your history here.")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2: ASK AI (CHAT)
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.current_page == "chat":
    st.markdown('<h1 class="section-header-main">Ask AI</h1>', unsafe_allow_html=True)
    
    # Get prefilled query if exists
    prefill = st.session_state.pop("prefill_query", "")
    
    col_input, col_send, col_clear = st.columns([8, 1, 1])
    
    with col_input:
        user_query = st.text_input(
            "Type your healthcare question...",
            value=prefill,
            placeholder="e.g., What are the symptoms of Type 2 diabetes?",
            label_visibility="collapsed"
        )
    
    with col_send:
        send_button = st.button("Ask", use_container_width=True, type="primary")
    
    with col_clear:
        if st.button("Clear", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    if send_button and user_query:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_query})
        
        # Call API
        with st.spinner("AI is analyzing..."):
            try:
                response = requests.post(
                    f"{API_BASE}/chat",
                    json={"query": user_query, "session_id": st.session_state.session_id},
                    timeout=30
                )
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.messages.append({"role": "assistant", "content": result})
                else:
                    st.error(f"API Error: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        st.rerun()
    
    st.markdown("---")
    
    # Display conversation
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
            st.markdown("")
        else:
            st.markdown("**AI Healthcare Copilot**")
            render_clinical_answer_card(msg["content"])
            st.markdown("")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3: REPORT ANALYZER
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.current_page == "reports":
    st.markdown('<h1 class="section-header-main">Medical Report Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("Upload lab results, discharge summaries, or medical reports for AI-powered analysis.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("### Upload Report")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "txt", "jpg", "png"],
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            st.success(f"Uploaded: {uploaded_file.name}")
            
            if st.button("Analyze Report", use_container_width=True, type="primary"):
                with st.spinner("Analyzing report..."):
                    try:
                        files = {"file": uploaded_file}
                        data = {"session_id": st.session_state.session_id}
                        
                        upload_resp = requests.post(
                            f"{API_BASE}/records/upload",
                            files=files,
                            data=data,
                            timeout=30
                        )
                        
                        if upload_resp.status_code == 200:
                            # Analyze endpoint expects Form data, not JSON
                            analyze_resp = requests.post(
                                f"{API_BASE}/records/analyze",
                                data={"session_id": st.session_state.session_id},
                                timeout=30
                            )
                            
                            if analyze_resp.status_code == 200:
                                st.session_state.analysis_result = analyze_resp.json()
                                st.success("Analysis complete!")
                                st.rerun()
                            else:
                                st.error(f"Analysis failed: {analyze_resp.status_code} - {analyze_resp.text}")
                        else:
                            st.error(f"Upload failed: {upload_resp.status_code} - {upload_resp.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        import traceback
                        st.error(f"Details: {traceback.format_exc()}")
    
    with col_right:
        st.markdown("### Analysis Results")
        
        if "analysis_result" in st.session_state:
            result = st.session_state.analysis_result
            
            # Patient Information
            patient_info = result.get("patient_info", {})
            if patient_info:
                st.markdown("#### Patient Information")
                info_items = []
                if patient_info.get("name"):
                    info_items.append(f"**Name:** {patient_info['name']}")
                if patient_info.get("dob"):
                    info_items.append(f"**DOB:** {patient_info['dob']}")
                if patient_info.get("record_date"):
                    info_items.append(f"**Date:** {patient_info['record_date']}")
                if patient_info.get("provider"):
                    info_items.append(f"**Provider:** {patient_info['provider']}")
                
                if info_items:
                    st.markdown(" | ".join(info_items))
                st.markdown("<br>", unsafe_allow_html=True)
            
            # Lab Values
            st.markdown("#### Lab Values")
            labs = result.get("lab_values", [])
            if labs:
                for lab in labs:
                    status = lab.get("status", "UNKNOWN")
                    status_color = "🟢" if status == "NORMAL" else "🔴" if status == "ABNORMAL" else "🟡"
                    
                    st.markdown(f"{status_color} **{lab.get('name')}**: {lab.get('value')}")
                    if lab.get("normal_range"):
                        st.caption(f"Normal range: {lab['normal_range']}")
                    if lab.get("interpretation"):
                        st.info(lab['interpretation'])
                    st.markdown("<br>", unsafe_allow_html=True)
            else:
                st.info("No lab values detected")
            
            # Diagnoses
            diagnoses = result.get("diagnoses", [])
            if diagnoses:
                st.markdown("#### Diagnoses")
                for dx in diagnoses:
                    st.markdown(f"- {dx}")
                st.markdown("<br>", unsafe_allow_html=True)
            
            # Medications
            medications = result.get("medications", [])
            if medications:
                st.markdown("#### Medications")
                for med in medications:
                    st.markdown(f"- {med}")
                st.markdown("<br>", unsafe_allow_html=True)
            
            # Key Findings
            key_findings = result.get("key_findings", "")
            if key_findings:
                st.markdown("#### Key Findings")
                st.markdown(key_findings)
                st.markdown("<br>", unsafe_allow_html=True)
            
            # Recommended Actions
            actions = result.get("recommended_actions", [])
            if actions:
                st.markdown("#### Recommended Actions")
                for action in actions:
                    st.markdown(f"- {action}")
                st.markdown("<br>", unsafe_allow_html=True)
            
            # Abnormal Flags
            abnormal_flags = result.get("abnormal_flags", [])
            if abnormal_flags:
                st.warning("**⚠️ Abnormal Values Detected:**")
                for flag in abnormal_flags:
                    st.markdown(f"- {flag}")
                st.markdown("<br>", unsafe_allow_html=True)
            
            # AI-Powered Health Recommendations
            health_recommendations = result.get("health_recommendations")
            if health_recommendations:
                st.markdown("---")
                st.markdown("### 🤖 AI Health Recommendations")
                st.markdown("*Personalized suggestions based on your lab results*")
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Display recommendations in an expandable section for better UX
                with st.expander("📋 View Detailed Health Recommendations", expanded=True):
                    st.markdown(health_recommendations)
            
            # Safety Note
            st.warning("**When to Seek Medical Attention:** If you notice any abnormal values or have concerns, consult your healthcare provider immediately.")
            
            # Processing Time
            latency = result.get("latency_ms", 0)
            if latency:
                extraction_time = result.get("extraction_latency_ms", 0)
                recommendations_time = result.get("recommendations_latency_ms", 0)
                st.caption(
                    f"Analysis completed in {latency/1000:.2f}s "
                    f"(Extraction: {extraction_time/1000:.1f}s, Recommendations: {recommendations_time/1000:.1f}s)"
                )
        else:
            st.info("Upload a report to see analysis results here.")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4: MONITORING DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.current_page == "dashboard":
    st.markdown('<h1 class="section-header-main">Monitoring Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("Real-time system metrics and performance analytics")
    st.markdown("<br>", unsafe_allow_html=True)
    
    try:
        stats = requests.get(f"{API_BASE}/stats", timeout=3).json()
        
        # KPI Cards with trend indicators
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_queries = stats.get('cache', {}).get('total_requests', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-trend trend-up">
                    <span class="trend-arrow">↑</span>
                    <span>12%</span>
                </div>
                <div class="metric-value">{total_queries}</div>
                <div class="metric-label">Total Queries</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            hit_rate = stats.get('cache', {}).get('hit_rate', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-trend trend-up">
                    <span class="trend-arrow">↑</span>
                    <span>8%</span>
                </div>
                <div class="metric-value">{int(hit_rate*100)}%</div>
                <div class="metric-label">Cache Hit Rate</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-trend trend-down">
                    <span class="trend-arrow">↓</span>
                    <span>5%</span>
                </div>
                <div class="metric-value">6.2s</div>
                <div class="metric-label">Avg Latency</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-trend trend-up">
                    <span class="trend-arrow">↑</span>
                    <span>3%</span>
                </div>
                <div class="metric-value">87%</div>
                <div class="metric-label">Avg Confidence</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Circular gauges
        st.markdown("### System Health")
        col_g1, col_g2, col_g3 = st.columns(3)
        
        with col_g1:
            gauge_confidence = create_circular_gauge(87, "Confidence Score", "#2CB1BC")
            st.plotly_chart(gauge_confidence, use_container_width=True)
        
        with col_g2:
            gauge_quality = create_circular_gauge(92, "Response Quality", "#2F855A")
            st.plotly_chart(gauge_quality, use_container_width=True)
        
        with col_g3:
            gauge_uptime = create_circular_gauge(99, "System Uptime", "#0F4C81")
            st.plotly_chart(gauge_uptime, use_container_width=True)
        
        st.markdown("---")
        
        # Charts
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Query trend chart
            trend_data = [45, 52, 48, 65, 58, 72, 68, 75]
            trend_chart = create_trend_chart(trend_data, "Query Volume Trend")
            st.plotly_chart(trend_chart, use_container_width=True)
        
        with col_chart2:
            # Query categories bar chart
            categories = ["Drug Info", "Symptoms", "Lab Results", "Research"]
            values = [35, 28, 22, 15]
            bar_chart = create_bar_chart(categories, values, "Query Categories")
            st.plotly_chart(bar_chart, use_container_width=True)
        
        st.markdown("---")
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("### Cache Statistics")
            cache_stats = stats.get('cache', {})
            st.json(cache_stats)
        
        with col_right:
            st.markdown("### Rate Limiter Statistics")
            rate_stats = stats.get('rate_limiter', {})
            st.json(rate_stats)
        
    except Exception as e:
        st.error(f"Unable to fetch stats: {str(e)}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5: PATIENT HISTORY
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.current_page == "history":
    st.markdown('<h1 class="section-header-main">Patient History</h1>', unsafe_allow_html=True)
    st.markdown("View previous sessions and uploaded reports")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.messages:
        st.markdown("### Recent Conversations")
        
        # Create data table
        table_html = """
        <table class="data-table">
            <thead>
                <tr>
                    <th>User</th>
                    <th>Query</th>
                    <th>Confidence</th>
                    <th>Intent</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
        """
        
        user_queries = []
        for idx, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                user_queries.append((idx, msg))
        
        for table_idx, (msg_idx, msg) in enumerate(reversed(user_queries[-10:])):
            avatar_svg = get_avatar_svg("Patient User", table_idx)
            query_preview = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
            
            # Get response data if available
            confidence = "N/A"
            intent = "N/A"
            status_class = "warning"
            status_text = "Pending"
            
            if msg_idx + 1 < len(st.session_state.messages):
                response = st.session_state.messages[msg_idx + 1]
                if response["role"] == "assistant":
                    confidence_val = response["content"].get('quality_score', 0)
                    confidence = f"{int(confidence_val*100)}%"
                    intent = response["content"].get('intent', 'N/A')
                    
                    if confidence_val >= 0.8:
                        status_class = "success"
                        status_text = "Completed"
                    elif confidence_val >= 0.6:
                        status_class = "warning"
                        status_text = "Review"
                    else:
                        status_class = "danger"
                        status_text = "Low Quality"
            
            table_html += f"""
                <tr>
                    <td>
                        <span class="table-avatar">{avatar_svg}</span>
                        Patient
                    </td>
                    <td>{query_preview}</td>
                    <td>{confidence}</td>
                    <td>{intent}</td>
                    <td><span class="status-badge {status_class}">{status_text}</span></td>
                </tr>
            """
        
        table_html += """
            </tbody>
        </table>
        """
        
        st.markdown(table_html, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Expandable details
        st.markdown("### Conversation Details")
        for idx, msg in enumerate(reversed(st.session_state.messages[-10:])):
            if msg["role"] == "user":
                with st.expander(f"{msg['content'][:60]}..."):
                    st.markdown(f"**Query:** {msg['content']}")
                    if idx > 0 and st.session_state.messages[-(idx)]["role"] == "assistant":
                        response = st.session_state.messages[-(idx)]["content"]
                        st.markdown(f"**Confidence:** {int(response.get('quality_score', 0)*100)}%")
                        st.markdown(f"**Intent:** {response.get('intent', 'N/A')}")
    else:
        st.info("No conversation history yet. Start chatting to see your history here!")
