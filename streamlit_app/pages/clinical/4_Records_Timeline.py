"""
Records Timeline - Chronological view of all care activities

Structured timeline showing analyses, reports, follow-ups, and system interactions
in a clean, professional chronology format.
"""
import streamlit as st
from pathlib import Path
from datetime import datetime
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Page config
st.set_page_config(
    page_title="Records Timeline - Clinical Intelligence",
    layout="wide",
    page_icon="⚕️",
    initial_sidebar_state="collapsed"
)

# Load Clinical Intelligence theme
def load_clinical_theme():
    css_path = Path(__file__).parent.parent.parent / "streamlit_app" / "styles" / "clinical_theme.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_clinical_theme()

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #0E3A5D 0%, #185C8D 100%); 
            border-radius: 16px; padding: 2rem; margin-bottom: 2rem; color: white;">
    <div style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">Records Timeline</div>
    <div style="font-size: 1rem; opacity: 0.9;">
        Chronological view of all care activities, analyses, and system interactions
    </div>
</div>
""", unsafe_allow_html=True)

# Back button
if st.button("← Back to Care Home", key="back_home"):
    st.switch_page("app_clinical.py")

st.markdown("<br>", unsafe_allow_html=True)

# Collect all timeline events
timeline_events = []

# Add analysis history
if "analysis_history" in st.session_state:
    for item in st.session_state.analysis_history:
        timeline_events.append({
            "timestamp": item.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "type": "AI Question",
            "title": item.get("query", "")[:60] + "...",
            "content": item.get("response", {}).get("answer", "")[:150] + "...",
            "confidence": item.get("response", {}).get("confidence", 0),
            "icon": "💬"
        })

# Add daily updates
if "daily_updates" in st.session_state:
    for item in st.session_state.daily_updates:
        timeline_events.append({
            "timestamp": item.get("timestamp", item.get("date", "")),
            "type": "Daily Check-in",
            "title": f"{item.get('condition_trend', 'Unknown')} | Risk: {item.get('risk_level', 'unknown').title()}",
            "content": item.get("summary", ""),
            "risk_level": item.get("risk_level", "low"),
            "icon": "📊"
        })

# Add report analyses (if any)
if "reports_analyzed" in st.session_state and st.session_state.reports_analyzed > 0:
    timeline_events.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "Report Analysis",
        "title": f"{st.session_state.reports_analyzed} reports analyzed",
        "content": "Medical reports have been processed and analyzed",
        "icon": "📄"
    })

# Sort by timestamp (most recent first)
timeline_events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

# Display timeline
if timeline_events:
    # Summary metrics
    col_m1, col_m2, col_m3, col_m4 = st.columns(4, gap="large")
    
    with col_m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Activities</div>
            <div class="metric-value">{len(timeline_events)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_m2:
        ai_questions = len([e for e in timeline_events if e["type"] == "AI Question"])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">AI Questions</div>
            <div class="metric-value">{ai_questions}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_m3:
        daily_checkins = len([e for e in timeline_events if e["type"] == "Daily Check-in"])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Daily Check-ins</div>
            <div class="metric-value">{daily_checkins}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_m4:
        high_risk = len([e for e in timeline_events if e.get("risk_level") == "high"])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">High Risk Alerts</div>
            <div class="metric-value">{high_risk}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Timeline display
    st.markdown("""
    <div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1.5rem;">
        Activity Timeline
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
    
    for event in timeline_events:
        # Format timestamp
        try:
            ts = datetime.strptime(event["timestamp"], "%Y-%m-%d %H:%M:%S")
            date_str = ts.strftime("%B %d, %Y")
            time_str = ts.strftime("%I:%M %p")
        except:
            date_str = event["timestamp"]
            time_str = ""
        
        # Risk badge if applicable
        risk_badge = ""
        if "risk_level" in event:
            risk_level = event["risk_level"]
            risk_class = "high" if risk_level == "high" else "medium" if risk_level == "medium" else "low"
            risk_badge = f'<span class="confidence-badge confidence-{risk_class}" style="margin-left: 0.5rem;">{risk_level.title()} Risk</span>'
        
        # Confidence badge if applicable
        confidence_badge = ""
        if "confidence" in event:
            conf = event["confidence"]
            conf_class = "high" if conf > 0.8 else "medium" if conf > 0.6 else "low"
            confidence_badge = f'<span class="confidence-badge confidence-{conf_class}" style="margin-left: 0.5rem;">{conf:.0%}</span>'
        
        st.markdown(f"""
        <div class="timeline-item">
            <div class="timeline-date">{date_str} {time_str}</div>
            <div class="timeline-title">
                {event['icon']} {event['type']}: {event['title']}
                {risk_badge}
                {confidence_badge}
            </div>
            <div class="timeline-content">{event['content']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Empty state
    st.markdown("""
    <div class="answer-card" style="text-align: center; padding: 4rem 2rem;">
        <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;">📋</div>
        <div style="font-size: 1.25rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">
            No Records Yet
        </div>
        <div style="color: var(--text-secondary); margin-bottom: 2rem;">
            Your care activities will appear here as you use the system
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_btn1, col_btn2, col_btn3 = st.columns(3, gap="large")
    
    with col_btn1:
        if st.button("📄 Analyze a Report", use_container_width=True, type="primary"):
            st.switch_page("pages/3_Report_Analyzer.py")
    
    with col_btn2:
        if st.button("💬 Ask AI", use_container_width=True, type="primary"):
            st.switch_page("pages/clinical/2_Analysis_Workspace.py")
    
    with col_btn3:
        if st.button("📊 Start Follow-up", use_container_width=True, type="primary"):
            st.switch_page("pages/clinical/3_Ongoing_Monitoring.py")

# Export options
if timeline_events:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    
    col_export1, col_export2, col_export3 = st.columns([1, 1, 2])
    
    with col_export1:
        if st.button("📥 Export Timeline", use_container_width=True):
            st.info("Timeline export feature coming soon")
    
    with col_export2:
        if st.button("📊 Generate Report", use_container_width=True):
            st.info("Report generation feature coming soon")
