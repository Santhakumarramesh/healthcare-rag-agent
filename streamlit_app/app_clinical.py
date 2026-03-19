"""
Healthcare AI Platform - Clinical Intelligence Interface

Care Home: Premium clinical operating system for report analysis,
grounded AI support, and longitudinal follow-up.
"""
import streamlit as st
import os
from pathlib import Path
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Clinical Intelligence - Healthcare AI",
    layout="wide",
    page_icon="⚕️",
    initial_sidebar_state="collapsed"
)

# Load Clinical Intelligence theme
def load_clinical_theme():
    css_path = Path(__file__).parent / "styles" / "clinical_theme.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_clinical_theme()

# Initialize session state
if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

if "care_mode" not in st.session_state:
    st.session_state.care_mode = None

if "reports_analyzed" not in st.session_state:
    st.session_state.reports_analyzed = 0

if "questions_answered" not in st.session_state:
    st.session_state.questions_answered = 0

if "daily_updates" not in st.session_state:
    st.session_state.daily_updates = []

if "risk_alerts_today" not in st.session_state:
    st.session_state.risk_alerts_today = 0

if "avg_confidence" not in st.session_state:
    st.session_state.avg_confidence = 0.0

# Calculate average confidence from history
if "history" in st.session_state and st.session_state.history:
    confidences = [h.get("confidence", 0) for h in st.session_state.history if "confidence" in h]
    if confidences:
        st.session_state.avg_confidence = sum(confidences) / len(confidences)

# Hero Section
st.markdown(f"""
<div class="care-home-hero">
    <div class="care-home-title">Clinical Intelligence</div>
    <div class="care-home-subtitle">
        A premium clinical operating system for report analysis, grounded AI support, 
        and longitudinal follow-up — designed for trust, clarity, and ongoing care.
    </div>
    
    <div class="care-home-status">
        <div class="status-metric">
            <div class="status-metric-label">Active Mode</div>
            <div class="status-metric-value">{st.session_state.care_mode or "None"}</div>
        </div>
        <div class="status-metric">
            <div class="status-metric-label">Avg Confidence</div>
            <div class="status-metric-value">{st.session_state.avg_confidence:.0%}</div>
        </div>
        <div class="status-metric">
            <div class="status-metric-label">Reports Analyzed</div>
            <div class="status-metric-value">{st.session_state.reports_analyzed}</div>
        </div>
        <div class="status-metric">
            <div class="status-metric-label">Risk Alerts Today</div>
            <div class="status-metric-value">{st.session_state.risk_alerts_today}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Section Title
st.markdown("""
<div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1.5rem;">
    Choose Your Care Workflow
</div>
""", unsafe_allow_html=True)

# Mode Cards
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown("""
    <div class="mode-card">
        <div class="mode-card-icon">📄</div>
        <div class="mode-card-title">Report Analysis</div>
        <div class="mode-card-description">
            Upload PDF, images, or lab text and get structured explanation with extracted findings, 
            abnormal values, and AI-powered clinical insights.
        </div>
        <div class="mode-card-meta">
            <span>Structured extraction</span> • <span>Evidence-based</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Analyze Report", key="btn_report", use_container_width=True, type="primary"):
        st.session_state.care_mode = "report_analysis"
        st.switch_page("pages/clinical/2_Analysis_Workspace.py")

with col2:
    st.markdown("""
    <div class="mode-card">
        <div class="mode-card-icon">💬</div>
        <div class="mode-card-title">AI Question Answering</div>
        <div class="mode-card-description">
            Ask grounded medical questions and receive structured answers with key insights, 
            possible considerations, next steps, and cited evidence.
        </div>
        <div class="mode-card-meta">
            <span>Confidence scoring</span> • <span>Source citations</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Ask AI", key="btn_ask", use_container_width=True, type="primary"):
        st.session_state.care_mode = "ai_qa"
        st.switch_page("pages/clinical/2_Analysis_Workspace.py")

with col3:
    st.markdown("""
    <div class="mode-card">
        <div class="mode-card-icon">📊</div>
        <div class="mode-card-title">Serious Condition Follow-up</div>
        <div class="mode-card-description">
            Daily tracking for high-risk conditions with change detection, risk escalation, 
            symptom trends, and longitudinal monitoring.
        </div>
        <div class="mode-card-meta">
            <span>Daily monitoring</span> • <span>Risk alerts</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Start Follow-up", key="btn_followup", use_container_width=True, type="primary"):
        st.session_state.care_mode = "serious_followup"
        st.switch_page("pages/clinical/3_Ongoing_Monitoring.py")

st.markdown("<br><br>", unsafe_allow_html=True)

# Two-column layout for Recent Activity and Trust Panel
col_left, col_right = st.columns([1.5, 1], gap="large")

with col_left:
    st.markdown("""
    <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
        Recent Care Activity
    </div>
    """, unsafe_allow_html=True)
    
    # Recent activity timeline
    if "history" in st.session_state and st.session_state.history:
        st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
        
        for item in st.session_state.history[-5:]:
            timestamp = item.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M"))
            query_type = item.get("query_type", "General")
            query = item.get("query", "No query")[:60] + "..."
            confidence = item.get("confidence", 0)
            
            st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-date">{timestamp}</div>
                <div class="timeline-title">{query_type} Query</div>
                <div class="timeline-content">{query}</div>
                <div style="margin-top: 0.5rem;">
                    <span class="confidence-badge confidence-{'high' if confidence > 0.8 else 'medium' if confidence > 0.6 else 'low'}">
                        {confidence:.0%} Confidence
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="answer-card">
            <div style="color: var(--text-secondary); text-align: center; padding: 2rem;">
                No recent activity. Start by choosing a care workflow above.
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <div class="trust-panel">
        <div class="trust-panel-title">Why Trust This System</div>
        
        <div class="trust-item">
            <div class="trust-item-icon">✓</div>
            <div class="trust-item-content">
                <div class="trust-item-title">Evidence-Based Responses</div>
                <div class="trust-item-description">
                    Every answer cites medical sources and shows relevance scores
                </div>
            </div>
        </div>
        
        <div class="trust-item">
            <div class="trust-item-icon">✓</div>
            <div class="trust-item-content">
                <div class="trust-item-title">Confidence Transparency</div>
                <div class="trust-item-description">
                    Multi-factor confidence scoring displayed for every response
                </div>
            </div>
        </div>
        
        <div class="trust-item">
            <div class="trust-item-icon">✓</div>
            <div class="trust-item-content">
                <div class="trust-item-title">Emergency Detection</div>
                <div class="trust-item-description">
                    14 critical symptoms trigger immediate risk alerts
                </div>
            </div>
        </div>
        
        <div class="trust-item">
            <div class="trust-item-icon">✓</div>
            <div class="trust-item-content">
                <div class="trust-item-title">Secure Workflow</div>
                <div class="trust-item-description">
                    Uploaded data stays within your secure session
                </div>
            </div>
        </div>
        
        <div class="trust-item">
            <div class="trust-item-icon">✓</div>
            <div class="trust-item-content">
                <div class="trust-item-title">Longitudinal Tracking</div>
                <div class="trust-item-description">
                    Follow-up mode compares daily changes and detects worsening patterns
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer navigation
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

col_nav1, col_nav2, col_nav3, col_nav4 = st.columns(4)

with col_nav1:
    if st.button("📋 Records Timeline", use_container_width=True):
        st.switch_page("pages/clinical/4_Records_Timeline.py")

with col_nav2:
    if st.button("📊 System Monitoring", use_container_width=True):
        st.switch_page("pages/clinical/5_System_Monitoring.py")

with col_nav3:
    if st.button("⚙️ Settings", use_container_width=True):
        st.switch_page("pages/6_Settings.py")

with col_nav4:
    if st.button("📖 Documentation", use_container_width=True):
        st.info("View comprehensive system documentation and user guides")
