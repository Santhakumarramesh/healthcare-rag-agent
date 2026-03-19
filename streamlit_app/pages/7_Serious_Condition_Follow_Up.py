"""
Serious Condition Follow-up - Daily monitoring for high-risk conditions.

Track daily updates, compare symptom changes, and surface escalation risk early.
"""
import streamlit as st
import pandas as pd
from datetime import date
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.ui_helpers import (
    inject_global_styles,
    render_hero,
    render_status_card,
    render_risk_banner,
)

st.set_page_config(
    page_title="Serious Condition Follow-up",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_styles()

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

if "care_mode" not in st.session_state:
    st.session_state.care_mode = "serious_followup"


def assess_risk(payload: dict) -> tuple[str, str]:
    """
    Assess risk level based on daily check-in data.
    
    Args:
        payload: Daily check-in data
        
    Returns:
        Tuple of (risk_level, risk_message)
    """
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
            "High-risk symptoms were reported today. Seek urgent medical attention immediately.",
        )

    if payload.get("fever") and payload.get("condition_trend") == "Worse":
        return (
            "medium",
            "Condition appears to be worsening with fever present. Contact a clinician promptly.",
        )

    if int(payload.get("pain_level", 0)) >= 8:
        return (
            "medium",
            "High pain level reported. Clinical review is recommended soon.",
        )

    return (
        "low",
        "No immediate high-risk signal detected from today's update, but continued monitoring is recommended.",
    )


def build_daily_summary(payload: dict, risk_level: str) -> str:
    """
    Build a daily summary from check-in data.
    
    Args:
        payload: Daily check-in data
        risk_level: Assessed risk level
        
    Returns:
        Summary text
    """
    parts = [
        f"Condition trend: {payload.get('condition_trend', 'Unknown')}.",
        f"Pain level: {payload.get('pain_level', 'N/A')}/10.",
    ]

    if payload.get("new_symptoms"):
        parts.append(f"New symptoms reported: {payload['new_symptoms']}.")

    if payload.get("medications_taken"):
        parts.append("Medication adherence reported today.")
    else:
        parts.append("Medication adherence was not confirmed today.")

    if risk_level == "high":
        parts.append("Urgent follow-up is advised.")
    elif risk_level == "medium":
        parts.append("Prompt clinician contact is recommended.")
    else:
        parts.append("Continue regular monitoring and compare with tomorrow's update.")

    return " ".join(parts)


# Sidebar
with st.sidebar:
    st.markdown("### Navigation")
    st.page_link("app_professional.py", label="Dashboard")
    st.page_link("pages/1_Dashboard.py", label="Home")
    st.page_link("pages/2_Ask_AI.py", label="Ask AI")
    st.page_link("pages/3_Report_Analyzer.py", label="Report Analyzer")
    st.page_link("pages/7_Serious_Condition_Follow_Up.py", label="Condition Follow-up")
    st.page_link("pages/5_Monitoring.py", label="Monitoring")

    st.markdown("---")
    st.markdown("### System Status")
    render_status_card("Care Mode", "Follow-up")
    render_status_card("Saved Updates", str(len(st.session_state.daily_updates)))
    render_status_card(
        "Profile",
        "Ready" if st.session_state.followup_profile.get("is_initialized") else "Setup Required",
    )

# Main content
render_hero(
    "Serious Condition Follow-up",
    "Track daily updates for high-risk or serious health conditions, compare symptom changes over time, and surface escalation risk early.",
)

st.markdown('<div class="section-title">Condition Profile</div>', unsafe_allow_html=True)

profile_left, profile_right = st.columns([1.1, 0.9], gap="large")

with profile_left:
    with st.form("followup_profile_form", clear_on_submit=False):
        condition_name = st.text_input(
            "Condition Name",
            value=st.session_state.followup_profile.get("condition_name", ""),
            placeholder="Example: Heart Failure, COPD, Post-Surgery Recovery",
        )
        diagnosis_date = st.date_input(
            "Diagnosis or Monitoring Start Date",
            value=st.session_state.followup_profile.get("diagnosis_date") or date.today(),
        )
        primary_symptoms = st.text_area(
            "Primary Symptoms / Concerns",
            value=st.session_state.followup_profile.get("primary_symptoms", ""),
            height=100,
            placeholder="Example: shortness of breath, fatigue, swelling, fever",
        )
        current_medications = st.text_area(
            "Current Medications",
            value=st.session_state.followup_profile.get("current_medications", ""),
            height=90,
            placeholder="List medications or care instructions",
        )
        doctor_notes = st.text_area(
            "Doctor Instructions / Special Watchouts",
            value=st.session_state.followup_profile.get("doctor_notes", ""),
            height=90,
            placeholder="Example: watch for chest pain, oxygen drop, or persistent fever",
        )

        submitted_profile = st.form_submit_button("Save Condition Profile", use_container_width=True)

        if submitted_profile:
            st.session_state.followup_profile = {
                "condition_name": condition_name,
                "diagnosis_date": diagnosis_date,
                "primary_symptoms": primary_symptoms,
                "current_medications": current_medications,
                "doctor_notes": doctor_notes,
                "is_initialized": True,
            }
            st.success("Condition profile saved successfully.")

with profile_right:
    st.markdown(
        """
        <div class="panel-card">
            <div class="mini-heading">How this mode helps</div>
            <div class="subtle-text">
                This mode is intended for daily follow-up when a patient is seriously ill, under active observation,
                recovering after hospitalization, or managing a condition where symptom changes should be monitored closely.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="panel-card">
            <div class="mini-heading">What gets tracked</div>
            <div class="subtle-text">
                Daily symptom trend, pain level, fever, breathing changes, medications, new symptoms, and risk flags.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="section-title">Daily Check-in</div>', unsafe_allow_html=True)

checkin_left, checkin_right = st.columns([1.05, 0.95], gap="large")

with checkin_left:
    with st.form("daily_checkin_form", clear_on_submit=False):
        update_date = st.date_input("Update Date", value=date.today(), key="update_date")
        condition_trend = st.selectbox(
            "How is the condition compared to yesterday?",
            ["Improved", "Stable", "Worse"],
        )
        pain_level = st.slider("Pain Level", min_value=0, max_value=10, value=3)
        fever = st.radio("Fever today?", ["No", "Yes"], horizontal=True)
        breathing_difficulty = st.radio("Breathing difficulty?", ["No", "Yes"], horizontal=True)
        chest_pain = st.radio("Chest pain?", ["No", "Yes"], horizontal=True)
        confusion = st.radio("Confusion or altered awareness?", ["No", "Yes"], horizontal=True)
        fainting = st.radio("Fainting / blackout episode?", ["No", "Yes"], horizontal=True)
        uncontrolled_bleeding = st.radio("Uncontrolled bleeding?", ["No", "Yes"], horizontal=True)
        medications_taken = st.radio("Medication taken as instructed?", ["Yes", "No"], horizontal=True)
        sleep_quality = st.selectbox("Sleep Quality", ["Good", "Fair", "Poor"])
        appetite = st.selectbox("Appetite", ["Normal", "Reduced", "Very Low"])
        hydration = st.selectbox("Hydration", ["Adequate", "Reduced", "Poor"])
        new_symptoms = st.text_area(
            "Any new symptoms or important changes?",
            height=100,
            placeholder="Describe any new symptom or worsening sign",
        )

        submitted_update = st.form_submit_button("Save Daily Update", use_container_width=True)

        if submitted_update:
            payload = {
                "date": str(update_date),
                "condition_trend": condition_trend,
                "pain_level": pain_level,
                "fever": fever == "Yes",
                "breathing_difficulty": breathing_difficulty == "Yes",
                "chest_pain": chest_pain == "Yes",
                "confusion": confusion == "Yes",
                "fainting": fainting == "Yes",
                "uncontrolled_bleeding": uncontrolled_bleeding == "Yes",
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

            st.session_state.daily_updates.append(payload)
            st.success("Daily update saved successfully.")
            st.rerun()

with checkin_right:
    if st.session_state.daily_updates:
        latest = st.session_state.daily_updates[-1]
        render_risk_banner(latest["risk_level"], latest["risk_message"])

        st.markdown(
            f"""
            <div class="panel-card">
                <div class="mini-heading">Today's Status</div>
                <div class="subtle-text"><strong>Trend:</strong> {latest['condition_trend']}</div>
                <div class="subtle-text"><strong>Pain Level:</strong> {latest['pain_level']}/10</div>
                <div class="subtle-text"><strong>Medication Taken:</strong> {"Yes" if latest['medications_taken'] else "No"}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="panel-card">
                <div class="mini-heading">Daily Summary</div>
                <div class="subtle-text">{latest['summary']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="panel-card">
                <div class="mini-heading">Safety Note</div>
                <div class="subtle-text">
                    This follow-up assistant is informational only and should not replace professional medical care.
                    Any severe or worsening symptoms should be reviewed by a clinician immediately.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="panel-card">
                <div class="mini-heading">No Daily Update Yet</div>
                <div class="subtle-text">
                    Complete the daily check-in form to generate a condition summary and risk alert.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown('<div class="section-title">Trend Summary</div>', unsafe_allow_html=True)

if st.session_state.daily_updates:
    df = pd.DataFrame(st.session_state.daily_updates)

    trend_col1, trend_col2 = st.columns([1, 1], gap="large")

    with trend_col1:
        st.markdown("**Pain Level Over Time**")
        chart_df = df[["date", "pain_level"]].copy()
        chart_df["date"] = pd.to_datetime(chart_df["date"])
        chart_df = chart_df.set_index("date")
        st.line_chart(chart_df, height=250)

    with trend_col2:
        st.markdown("**Risk Level Distribution**")
        if "risk_level" in df.columns:
            risk_counts = df["risk_level"].value_counts()
            st.bar_chart(risk_counts, height=250)

    st.markdown('<div class="section-title">Previous Check-ins</div>', unsafe_allow_html=True)

    for item in reversed(st.session_state.daily_updates[-7:]):
        st.markdown(
            f"""
            <div class="timeline-item">
                <div class="timeline-date">{item['date']}</div>
                <div class="timeline-title">{item['condition_trend']} | Risk: {item['risk_level'].title()}</div>
                <div class="timeline-body">{item['summary']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.info("No previous check-ins available yet. Complete the daily check-in form above to begin tracking.")
