"""
Ongoing Monitoring - Longitudinal care tracking for serious conditions

Premium dashboard for daily symptom tracking, risk assessment, trend analysis,
and worsening pattern detection.
"""
import streamlit as st
import pandas as pd
from datetime import date, datetime
from pathlib import Path
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Page config
st.set_page_config(
    page_title="Ongoing Monitoring - Clinical Intelligence",
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

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #0E3A5D 0%, #185C8D 100%); 
            border-radius: 16px; padding: 2rem; margin-bottom: 2rem; color: white;">
    <div style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">Ongoing Monitoring</div>
    <div style="font-size: 1rem; opacity: 0.9;">
        Longitudinal care tracking for serious conditions with daily symptom monitoring, 
        risk assessment, and worsening pattern detection
    </div>
</div>
""", unsafe_allow_html=True)

# Back button
if st.button("← Back to Care Home", key="back_home"):
    st.switch_page("app_clinical.py")

st.markdown("<br>", unsafe_allow_html=True)

# Condition Profile Section
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
            st.success("✓ Profile saved successfully")
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_profile_right:
    st.markdown("""
    <div class="trust-panel">
        <div class="trust-panel-title">How This Helps</div>
        
        <div class="trust-item">
            <div class="trust-item-icon">✓</div>
            <div class="trust-item-content">
                <div class="trust-item-title">Daily Tracking</div>
                <div class="trust-item-description">
                    Monitor symptoms, pain, and vital signs every day
                </div>
            </div>
        </div>
        
        <div class="trust-item">
            <div class="trust-item-icon">✓</div>
            <div class="trust-item-content">
                <div class="trust-item-title">Change Detection</div>
                <div class="trust-item-description">
                    Automatically compare with previous days
                </div>
            </div>
        </div>
        
        <div class="trust-item">
            <div class="trust-item-icon">✓</div>
            <div class="trust-item-content">
                <div class="trust-item-title">Risk Escalation</div>
                <div class="trust-item-description">
                    Alert when symptoms worsen or emergency signs appear
                </div>
            </div>
        </div>
        
        <div class="trust-item">
            <div class="trust-item-icon">✓</div>
            <div class="trust-item-content">
                <div class="trust-item-title">Trend Analysis</div>
                <div class="trust-item-description">
                    Visualize pain levels and risk patterns over time
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Daily Check-in Section
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
            
            # Update risk alerts count
            if "risk_alerts_today" in st.session_state and risk_level in ["high", "medium"]:
                st.session_state.risk_alerts_today += 1
            
            st.success("✓ Daily update saved successfully")
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_checkin_right:
    if st.session_state.daily_updates:
        latest = st.session_state.daily_updates[-1]
        
        # Risk alert
        risk_class = f"risk-alert-{latest['risk_level']}"
        st.markdown(f"""
        <div class="risk-alert {risk_class}">
            <div class="risk-alert-icon">{'⚠️' if latest['risk_level'] == 'high' else '⚡' if latest['risk_level'] == 'medium' else '✓'}</div>
            <div class="risk-alert-content">
                <div class="risk-alert-title">{latest['risk_level'].title()} Risk</div>
                <div class="risk-alert-message">{latest['risk_message']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Today's status
        st.markdown(f"""
        <div class="answer-card">
            <div style="font-size: 1.1rem; font-weight: 700; margin-bottom: 1rem;">Today's Status</div>
            <div style="margin-bottom: 0.5rem;"><strong>Trend:</strong> {latest['condition_trend']}</div>
            <div style="margin-bottom: 0.5rem;"><strong>Pain Level:</strong> {latest['pain_level']}/10</div>
            <div style="margin-bottom: 0.5rem;"><strong>Medication:</strong> {'Taken' if latest['medications_taken'] else 'Not confirmed'}</div>
            <div style="margin-bottom: 0.5rem;"><strong>Sleep:</strong> {latest['sleep_quality']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Daily summary
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

# Trend Analysis
if st.session_state.daily_updates:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
        Trend Analysis
    </div>
    """, unsafe_allow_html=True)
    
    df = pd.DataFrame(st.session_state.daily_updates)
    
    col_chart1, col_chart2 = st.columns(2, gap="large")
    
    with col_chart1:
        st.markdown("**Pain Level Over Time**")
        chart_df = df[["date", "pain_level"]].copy()
        chart_df["date"] = pd.to_datetime(chart_df["date"])
        chart_df = chart_df.set_index("date")
        st.line_chart(chart_df, height=300)
    
    with col_chart2:
        st.markdown("**Risk Level Distribution**")
        if "risk_level" in df.columns:
            risk_counts = df["risk_level"].value_counts()
            st.bar_chart(risk_counts, height=300)
    
    # Timeline
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
        Check-in History
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
    
    for item in reversed(st.session_state.daily_updates[-7:]):
        st.markdown(f"""
        <div class="timeline-item">
            <div class="timeline-date">{item['date']}</div>
            <div class="timeline-title">{item['condition_trend']} | Risk: {item['risk_level'].title()}</div>
            <div class="timeline-content">{item['summary']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Safety disclaimer
st.markdown("""
<div class="safety-card">
    <div class="safety-title">⚠️ Safety Boundary</div>
    <div class="safety-content">
        This monitoring assistant is informational only and should not replace professional medical care.
        Any severe or worsening symptoms should be reviewed by a clinician immediately.
        In case of emergency, call emergency services or go to the nearest emergency room.
    </div>
</div>
""", unsafe_allow_html=True)
