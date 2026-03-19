"""
AI Healthcare Copilot - Home Page

Care operating dashboard that answers:
- What can I do here
- What should I do next
- What changed recently
- What needs attention
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Add components to path
sys.path.insert(0, str(Path(__file__).parent))

from components.healthcare_components import (
    render_app_shell,
    render_sidebar_nav,
    render_hero_banner,
    render_mode_card,
    render_metric_card,
    render_trust_panel,
    format_timestamp
)

# Page config
render_app_shell()

# Initialize session state
if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

if "reports_analyzed" not in st.session_state:
    st.session_state.reports_analyzed = 0

if "questions_answered" not in st.session_state:
    st.session_state.questions_answered = 0

if "active_followup_cases" not in st.session_state:
    st.session_state.active_followup_cases = 0

if "risk_alerts_open" not in st.session_state:
    st.session_state.risk_alerts_open = 0

if "avg_confidence" not in st.session_state:
    st.session_state.avg_confidence = 0.0

if "history" not in st.session_state:
    st.session_state.history = []

if "daily_updates" not in st.session_state:
    st.session_state.daily_updates = []

# Calculate average confidence
if st.session_state.history:
    confidences = [h.get("confidence", 0) for h in st.session_state.history if "confidence" in h]
    if confidences:
        st.session_state.avg_confidence = sum(confidences) / len(confidences)

# Sidebar
render_sidebar_nav("Home")

# ============================================================================
# SECTION 1: HERO / WELCOME
# ============================================================================

def go_to_analyze_report():
    st.switch_page("pages/1_Analyze_Report.py")

def go_to_followup():
    st.switch_page("pages/3_Followup_Monitor.py")

render_hero_banner(
    title="AI Healthcare Copilot",
    subtitle="Grounded medical Q&A, report analysis, and longitudinal care follow-up",
    primary_cta="Analyze a Report",
    secondary_cta="Start Follow-up Check-in",
    primary_action=go_to_analyze_report,
    secondary_action=go_to_followup
)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# SECTION 2: CARE MODE ENTRY
# ============================================================================

st.markdown("""
<div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1.5rem;">
    Choose Your Care Workflow
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    render_mode_card(
        title="Analyze a Report",
        description="Upload reports, extract findings, and explain in plain language with confidence scoring and evidence citations.",
        icon="",
        button_text="Start Analysis",
        button_key="mode_analyze",
        action=lambda: st.switch_page("pages/1_Analyze_Report.py")
    )

with col2:
    render_mode_card(
        title="Ask a Medical Question",
        description="Evidence-backed answers with structured insights, possible concerns, next steps, and source citations.",
        icon="",
        button_text="Ask Question",
        button_key="mode_ask",
        action=lambda: st.switch_page("pages/2_Ask_AI.py")
    )

with col3:
    render_mode_card(
        title="Serious Condition Follow-up",
        description="Daily tracking, trend analysis, risk escalation, and longitudinal monitoring for high-risk conditions.",
        icon="",
        button_text="Start Follow-up",
        button_key="mode_followup",
        action=lambda: st.switch_page("pages/3_Followup_Monitor.py")
    )

st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================================================
# SECTION 3: KPI ROW
# ============================================================================

st.markdown("""
<div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
    System Overview
</div>
""", unsafe_allow_html=True)

col_k1, col_k2, col_k3, col_k4 = st.columns(4, gap="large")

with col_k1:
    render_metric_card(
        label="Reports Analyzed",
        value=str(st.session_state.reports_analyzed),
        change="All time"
    )

with col_k2:
    render_metric_card(
        label="Avg Confidence",
        value=f"{st.session_state.avg_confidence:.0%}",
        change="Last 100 queries"
    )

with col_k3:
    render_metric_card(
        label="Active Follow-up Cases",
        value=str(st.session_state.active_followup_cases),
        change="Currently monitoring"
    )

with col_k4:
    render_metric_card(
        label="Open Risk Alerts",
        value=str(st.session_state.risk_alerts_open),
        change="Requires attention"
    )

st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================================================
# SECTION 4: RECENT ACTIVITY
# ============================================================================

st.markdown("""
<div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
    Recent Activity
</div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([1.5, 1], gap="large")

with col_left:
    st.markdown("""
    <div class="answer-card">
        <div style="font-size: 1.1rem; font-weight: 700; margin-bottom: 1rem;">
            Recent Analyses
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.history:
        st.markdown('<div class="timeline-container">', unsafe_allow_html=True)

        for item in reversed(st.session_state.history[-5:]):
            timestamp = item.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            query_type = item.get("query_type", "General")
            query = item.get("query", "No query")[:60] + "..."
            confidence = item.get("confidence", 0)
            conf_class = "high" if confidence > 0.8 else "medium" if confidence > 0.6 else "low"

            st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-date">{format_timestamp(timestamp)}</div>
                <div class="timeline-title">{query_type} Query</div>
                <div class="timeline-content">{query}</div>
                <div style="margin-top: 0.5rem;">
                    <span class="confidence-badge confidence-{conf_class}">{confidence:.0%}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
            No recent analyses. Start by choosing a care workflow above.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <div class="answer-card">
        <div style="font-size: 1.1rem; font-weight: 700; margin-bottom: 1rem;">
            Current Alerts & Follow-up
        </div>
    """, unsafe_allow_html=True)

    # Check for high-risk daily updates
    high_risk_updates = [u for u in st.session_state.daily_updates if u.get("risk_level") == "high"]

    if high_risk_updates:
        for update in high_risk_updates[-3:]:
            date = update.get("date", "")
            risk_msg = update.get("risk_message", "")

            st.markdown(f"""
            <div class="risk-alert risk-alert-high" style="margin-bottom: 1rem;">
                <div class="risk-alert-icon">!</div>
                <div class="risk-alert-content">
                    <div class="risk-alert-title">High Risk - {date}</div>
                    <div class="risk-alert-message">{risk_msg[:100]}...</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Check for low-confidence analyses
    low_conf_analyses = [h for h in st.session_state.history if h.get("confidence", 1) < 0.6]

    if low_conf_analyses:
        st.markdown("""
        <div style="padding: 1rem; background: var(--warning-light); border-radius: 8px; margin-bottom: 1rem;">
            <div style="font-weight: 600; color: var(--warning); margin-bottom: 0.5rem;">
                Low Confidence Analyses
            </div>
            <div style="font-size: 0.875rem; color: var(--text-secondary);">
                {count} recent analyses had confidence below 60%. Review recommended.
            </div>
        </div>
        """.format(count=len(low_conf_analyses)), unsafe_allow_html=True)

    # Check for due check-ins
    if st.session_state.active_followup_cases > 0:
        st.markdown("""
        <div style="padding: 1rem; background: var(--info-light); border-radius: 8px; margin-bottom: 1rem;">
            <div style="font-weight: 600; color: var(--teal-primary); margin-bottom: 0.5rem;">
                Check-in Due
            </div>
            <div style="font-size: 0.875rem; color: var(--text-secondary);">
                Daily condition check-in is due. Complete your follow-up update.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Go to Follow-up Monitor", key="goto_followup", use_container_width=True):
            st.switch_page("pages/3_Followup_Monitor.py")

    if not high_risk_updates and not low_conf_analyses and st.session_state.active_followup_cases == 0:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
            No alerts or pending actions. System is operating normally.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================================================
# SECTION 5: TRUST & SAFETY PANEL
# ============================================================================

st.markdown("""
<div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
    Trust & Safety
</div>
""", unsafe_allow_html=True)

render_trust_panel()

# ============================================================================
# FOOTER NAVIGATION
# ============================================================================

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

col_f1, col_f2, col_f3, col_f4 = st.columns(4, gap="large")

with col_f1:
    if st.button("View Records Timeline", use_container_width=True):
        st.switch_page("pages/4_Records_Timeline.py")

with col_f2:
    if st.button("System Monitoring", use_container_width=True):
        st.switch_page("pages/5_Monitoring.py")

with col_f3:
    if st.button("Settings", use_container_width=True):
        st.switch_page("pages/6_Settings.py")

with col_f4:
    if st.button("Help & Documentation", use_container_width=True):
        st.info("Comprehensive user guides and system documentation coming soon")
