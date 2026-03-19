"""
Serious Condition Follow-up Page - Longitudinal tracking (THE MOAT)

Three vertical sections:
1. Condition Profile
2. Daily Check-in
3. Trend & History
"""
import streamlit as st
from datetime import date, datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from components.healthcare_components import (
    render_app_shell,
    render_sidebar_nav,
    render_page_header,
    render_risk_alert_banner,
    render_check_in_timeline,
    render_trend_chart,
    render_distribution_chart
)

# Page config
render_app_shell()

# Sidebar
render_sidebar_nav("Follow-up Monitor")

# Page header
render_page_header(
    "Serious Condition Follow-up",
    "Daily tracking, trend analysis, risk escalation, and longitudinal monitoring for high-risk conditions"
)

# Initialize session state
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

def compute_delta(today: dict, yesterday: dict) -> dict:
    """Compare two check-ins and return what changed."""
    changes = []
    pain_today = int(today.get("pain_level", 0))
    pain_yesterday = int(yesterday.get("pain_level", 0))
    pain_delta = pain_today - pain_yesterday

    if pain_delta > 0:
        changes.append(f"Pain level increased by {pain_delta} points ({pain_yesterday} → {pain_today})")
    elif pain_delta < 0:
        changes.append(f"Pain level decreased by {abs(pain_delta)} points ({pain_yesterday} → {pain_today})")

    trend_today = today.get("condition_trend", "")
    trend_yesterday = yesterday.get("condition_trend", "")
    if trend_today != trend_yesterday:
        changes.append(f"Condition trend changed: {trend_yesterday} → {trend_today}")

    if today.get("medications_taken") != yesterday.get("medications_taken"):
        today_med = "taken" if today.get("medications_taken") else "missed"
        yesterday_med = "taken" if yesterday.get("medications_taken") else "missed"
        changes.append(f"Medication adherence: {yesterday_med} → {today_med}")

    for field, label in [("sleep_quality", "Sleep"), ("appetite", "Appetite"), ("hydration", "Hydration")]:
        if today.get(field) != yesterday.get(field):
            changes.append(f"{label}: {yesterday.get(field, '?')} → {today.get(field, '?')}")

    emergency_fields = ["fever", "breathing_difficulty", "chest_pain", "confusion"]
    new_emergency = [f.replace("_", " ") for f in emergency_fields
                     if today.get(f) and not yesterday.get(f)]
    if new_emergency:
        changes.append(f"NEW emergency symptoms: {', '.join(new_emergency)}")

    trend_score = {"Improved": 1, "Stable": 0, "Worse": -1}
    direction = trend_score.get(trend_today, 0) - trend_score.get(trend_yesterday, 0)

    return {
        "changes": changes,
        "direction": "improving" if direction > 0 else "worsening" if direction < 0 else "stable",
        "pain_delta": pain_delta,
        "has_changes": len(changes) > 0,
    }


def assess_risk(payload: dict) -> tuple[str, str]:
    """Assess risk level based on daily check-in data."""
    high_risk_triggers = [
        payload.get("breathing_difficulty"),
        payload.get("chest_pain"),
        payload.get("confusion"),
        payload.get("fainting"),
        payload.get("uncontrolled_bleeding"),
    ]

    if any(high_risk_triggers):
        return (
            "high",
            "High-risk symptoms detected. Seek urgent medical attention immediately. Call emergency services or go to the nearest emergency room.",
        )

    if payload.get("fever") and payload.get("condition_trend") == "Worse":
        return (
            "medium",
            "Condition appears to be worsening with fever present. Contact your clinician promptly for evaluation.",
        )

    if int(payload.get("pain_level", 0)) >= 8:
        return (
            "medium",
            "High pain level reported. Clinical review is recommended soon. Contact your healthcare provider.",
        )

    return (
        "low",
        "No immediate high-risk signals detected. Continue regular monitoring and compare with tomorrow's update.",
    )

def build_daily_summary(payload: dict, risk_level: str) -> str:
    """Build a daily summary from check-in data."""
    parts = [
        f"Condition trend: {payload.get('condition_trend', 'Unknown')}.",
        f"Pain level: {payload.get('pain_level', 'N/A')}/10.",
    ]

    if payload.get("new_symptoms"):
        parts.append(f"New symptoms reported: {payload['new_symptoms']}.")

    if payload.get("medications_taken"):
        parts.append("Medication adherence confirmed.")
    else:
        parts.append("Medication adherence not confirmed.")

    if risk_level == "high":
        parts.append("Urgent follow-up advised.")
    elif risk_level == "medium":
        parts.append("Prompt clinician contact recommended.")
    else:
        parts.append("Continue monitoring and compare with next update.")

    return " ".join(parts)

# ============================================================================
# SECTION 1: CONDITION PROFILE
# ============================================================================

st.markdown("""
<div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
    Condition Profile
</div>
""", unsafe_allow_html=True)

col_profile_left, col_profile_right = st.columns([1.5, 1], gap="large")

with col_profile_left:
    st.markdown('<div class="answer-card">', unsafe_allow_html=True)

    with st.form("profile_form", clear_on_submit=False):
        condition_name = st.text_input(
            "Condition Name",
            value=st.session_state.followup_profile.get("condition_name", ""),
            placeholder="Example: Heart Failure, COPD, Post-Surgery Recovery"
        )

        diagnosis_date = st.date_input(
            "Diagnosis or Monitoring Start Date",
            value=st.session_state.followup_profile.get("diagnosis_date") or date.today()
        )

        primary_symptoms = st.text_area(
            "Primary Symptoms / Concerns",
            value=st.session_state.followup_profile.get("primary_symptoms", ""),
            height=100,
            placeholder="Example: shortness of breath, fatigue, swelling, fever"
        )

        current_medications = st.text_area(
            "Current Medications",
            value=st.session_state.followup_profile.get("current_medications", ""),
            height=90,
            placeholder="List medications and dosages"
        )

        doctor_notes = st.text_area(
            "Doctor Instructions / Special Watchouts",
            value=st.session_state.followup_profile.get("doctor_notes", ""),
            height=90,
            placeholder="Example: watch for chest pain, oxygen drop, or persistent fever"
        )

        submitted = st.form_submit_button("Save Profile", use_container_width=True, type="primary")

        if submitted:
            st.session_state.followup_profile = {
                "condition_name": condition_name,
                "diagnosis_date": diagnosis_date,
                "primary_symptoms": primary_symptoms,
                "current_medications": current_medications,
                "doctor_notes": doctor_notes,
                "is_initialized": True,
            }

            if "active_followup_cases" in st.session_state:
                st.session_state.active_followup_cases = 1

            st.success("✓ Profile saved successfully")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

with col_profile_right:
    st.markdown("""
    <div class="answer-card">
        <div style="font-size: 1.1rem; font-weight: 700; margin-bottom: 1rem;">
            How This Helps
        </div>
        <div style="color: var(--text-secondary); line-height: 1.7; margin-bottom: 1rem;">
            This mode is designed for daily follow-up when a patient is seriously ill,
            under active observation, recovering after hospitalization, or managing a
            condition where symptom changes should be monitored closely.
        </div>
        <div style="font-weight: 600; margin-bottom: 0.5rem;">What Gets Tracked:</div>
        <div style="color: var(--text-secondary); line-height: 1.7;">
            • Daily symptom trend<br>
            • Pain level<br>
            • Emergency symptoms<br>
            • Medication adherence<br>
            • Quality of life indicators<br>
            • Risk escalation flags
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================================================
# SECTION 2: DAILY CHECK-IN
# ============================================================================

st.markdown("""
<div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
    Daily Check-in
</div>
""", unsafe_allow_html=True)

col_checkin_left, col_checkin_right = st.columns([1.5, 1], gap="large")

with col_checkin_left:
    st.markdown('<div class="answer-card">', unsafe_allow_html=True)

    with st.form("checkin_form", clear_on_submit=False):
        update_date = st.date_input("Update Date", value=date.today())

        condition_trend = st.selectbox(
            "Compared to yesterday, the condition is:",
            ["Improved", "Stable", "Worse"]
        )

        pain_level = st.slider("Pain Level (0 = no pain, 10 = worst pain)", 0, 10, 3)

        st.markdown("**Emergency Symptoms**")
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            fever = st.checkbox("Fever")
            breathing_difficulty = st.checkbox("Breathing difficulty")
            chest_pain = st.checkbox("Chest pain")
        with col_e2:
            confusion = st.checkbox("Confusion / altered awareness")
            fainting = st.checkbox("Fainting / blackout")
            uncontrolled_bleeding = st.checkbox("Uncontrolled bleeding")

        st.markdown("**Daily Care**")
        medications_taken = st.radio("Medications taken as instructed?", ["Yes", "No"], horizontal=True)

        col_q1, col_q2, col_q3 = st.columns(3)
        with col_q1:
            sleep_quality = st.selectbox("Sleep Quality", ["Good", "Fair", "Poor"])
        with col_q2:
            appetite = st.selectbox("Appetite", ["Normal", "Reduced", "Very Low"])
        with col_q3:
            hydration = st.selectbox("Hydration", ["Adequate", "Reduced", "Poor"])

        new_symptoms = st.text_area(
            "Any new symptoms or important changes?",
            height=100,
            placeholder="Describe any new symptom or worsening sign"
        )

        submitted_update = st.form_submit_button("Save Daily Update", use_container_width=True, type="primary")

        if submitted_update:
            payload = {
                "date": str(update_date),
                "condition_trend": condition_trend,
                "pain_level": pain_level,
                "fever": fever,
                "breathing_difficulty": breathing_difficulty,
                "chest_pain": chest_pain,
                "confusion": confusion,
                "fainting": fainting,
                "uncontrolled_bleeding": uncontrolled_bleeding,
                "medications_taken": medications_taken == "Yes",
                "sleep_quality": sleep_quality,
                "appetite": appetite,
                "hydration": hydration,
                "new_symptoms": new_symptoms.strip(),
            }

            risk_level, risk_message = assess_risk(payload)
            summary = build_daily_summary(payload, risk_level)

            payload["risk_level"] = risk_level
            payload["risk_message"] = risk_message
            payload["summary"] = summary
            payload["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            st.session_state.daily_updates.append(payload)

            if "risk_alerts_open" in st.session_state and risk_level in ["high", "medium"]:
                st.session_state.risk_alerts_open += 1

            st.success("✓ Daily update saved successfully")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# SECTION 3: TODAY'S RESULT
with col_checkin_right:
    if st.session_state.daily_updates:
        latest = st.session_state.daily_updates[-1]

        render_risk_alert_banner(latest['risk_level'], latest['risk_message'])

        # "What Changed" engine — compare today vs yesterday
        if len(st.session_state.daily_updates) >= 2:
            delta = compute_delta(
                st.session_state.daily_updates[-1],
                st.session_state.daily_updates[-2],
            )
            direction_color = {"improving": "#27ae60", "worsening": "#e74c3c", "stable": "#2980b9"}
            direction_label = {"improving": "Improving", "worsening": "Worsening", "stable": "Stable"}
            color = direction_color.get(delta["direction"], "#666")
            label = direction_label.get(delta["direction"], "Unknown")

            changes_html = "".join(
                f'<div style="padding: 4px 0; border-bottom: 1px solid #eee; font-size: 0.85rem; color: #555;">• {c}</div>'
                for c in delta["changes"]
            ) if delta["changes"] else '<div style="color: #888; font-size: 0.85rem;">No significant changes from yesterday.</div>'

            st.markdown(f"""
<div style="background: #f8f9fa; border-left: 4px solid {color}; border-radius: 8px;
     padding: 1rem; margin-bottom: 1rem;">
  <div style="font-weight: 700; color: {color}; margin-bottom: 0.5rem;">
    What Changed Since Yesterday — {label}
  </div>
  {changes_html}
</div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="answer-card">
            <div style="font-size: 1.1rem; font-weight: 700; margin-bottom: 1rem;">Today's Status</div>
            <div style="margin-bottom: 0.5rem;"><strong>Trend:</strong> {latest['condition_trend']}</div>
            <div style="margin-bottom: 0.5rem;"><strong>Pain Level:</strong> {latest['pain_level']}/10</div>
            <div style="margin-bottom: 0.5rem;"><strong>Medication:</strong> {'Taken' if latest['medications_taken'] else 'Not confirmed'}</div>
            <div style="margin-bottom: 0.5rem;"><strong>Sleep:</strong> {latest['sleep_quality']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="answer-card">
            <div style="font-size: 1.1rem; font-weight: 700; margin-bottom: 1rem;">Daily Summary</div>
            <div style="color: var(--text-secondary); line-height: 1.6;">{latest['summary']}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="answer-card" style="text-align: center; padding: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 1rem; opacity: 0.3;">📊</div>
            <div style="color: var(--text-secondary);">
                Complete your first daily check-in to see status and risk assessment
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================================================
# SECTION 4: TREND VISUALIZATION
# ============================================================================

if st.session_state.daily_updates:
    st.markdown("""
    <div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
        Trend Analysis
    </div>
    """, unsafe_allow_html=True)

    col_chart1, col_chart2 = st.columns(2, gap="large")

    with col_chart1:
        render_trend_chart(
            st.session_state.daily_updates,
            "date",
            "pain_level",
            "Pain Level Over Time"
        )

    with col_chart2:
        risk_dist = {}
        for update in st.session_state.daily_updates:
            risk = update.get("risk_level", "low")
            risk_dist[risk] = risk_dist.get(risk, 0) + 1

        render_distribution_chart(risk_dist, "Risk Level Distribution")

# ============================================================================
# SECTION 5: PREVIOUS CHECK-INS TIMELINE
# ============================================================================

if st.session_state.daily_updates:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
        Check-in History
    </div>
    """, unsafe_allow_html=True)

    render_check_in_timeline(st.session_state.daily_updates)

# Footer actions
st.markdown("<br><br>", unsafe_allow_html=True)

# Visit Prep — shows after 3+ check-ins
if len(st.session_state.daily_updates) >= 3:
    st.markdown("---")
    st.markdown("""
<div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem;">
    Visit Preparation
</div>
<div style="color: #666; margin-bottom: 1rem;">
    Generate a pre-visit summary and questions to bring to your next appointment.
</div>""", unsafe_allow_html=True)

    if st.button("Generate Visit Summary", type="primary", use_container_width=False):
        with st.spinner("Preparing your visit summary..."):
            import requests
            import os
            api_url = os.getenv("API_BASE_URL", "https://healthcare-rag-api.onrender.com")
            try:
                resp = requests.post(f"{api_url}/visit/prepare", json={
                    "condition_name": st.session_state.followup_profile.get("condition_name", ""),
                    "daily_updates": st.session_state.daily_updates,
                    "current_medications": st.session_state.followup_profile.get("current_medications", ""),
                    "doctor_notes": st.session_state.followup_profile.get("doctor_notes", ""),
                }, timeout=30)
                if resp.ok:
                    vp = resp.json()
                    st.markdown(f"""
<div style="background: #f0f7ff; border-left: 4px solid #1b6ca8; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
  <div style="font-weight: 700; margin-bottom: 0.5rem;">Condition Summary</div>
  <div style="color: #444;">{vp.get('condition_summary', '')}</div>
</div>""", unsafe_allow_html=True)
                    if vp.get("questions_for_doctor"):
                        st.markdown("**Questions to ask your doctor:**")
                        for q in vp["questions_for_doctor"]:
                            st.markdown(f"- {q}")
                    if vp.get("urgent_items"):
                        st.markdown("**Mention first:**")
                        for item in vp["urgent_items"]:
                            st.markdown(f"- {item}")
                    if vp.get("medication_issues"):
                        st.markdown("**Medication notes:**")
                        for issue in vp["medication_issues"]:
                            st.markdown(f"- {issue}")
                else:
                    st.error("Could not generate visit summary. Check API connection.")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    if st.button("← Back to Home", use_container_width=True):
        st.switch_page("app_healthcare.py")

with col_f2:
    if st.button("View Records Timeline", use_container_width=True):
        st.switch_page("pages/4_Records_Timeline.py")

with col_f3:
    if st.button("Ask AI Question", use_container_width=True):
        st.switch_page("pages/2_Ask_AI.py")
