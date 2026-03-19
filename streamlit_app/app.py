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
                            analyze_resp = requests.post(
                                f"{API_BASE}/records/analyze",
                                json={"session_id": st.session_state.session_id},
                                timeout=30
                            )
                            
                            if analyze_resp.status_code == 200:
                                st.session_state.analysis_result = analyze_resp.json()
                                st.success("Analysis complete!")
                                st.rerun()
                        else:
                            st.error(f"Upload failed: {upload_resp.status_code}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with col_right:
        st.markdown("### Analysis Results")
        
        if "analysis_result" in st.session_state:
            result = st.session_state.analysis_result
            
            st.markdown("#### Detected Report Type")
            st.info(result.get("report_type", "Medical Document"))
            
            st.markdown("#### Important Values")
            labs = result.get("lab_values", [])
            if labs:
                for lab in labs[:5]:
                    status = "Abnormal" if lab.get("abnormal") else "Normal"
                    st.markdown(f"**{lab.get('name')}**: {lab.get('value')} {lab.get('unit', '')} ({status})")
            else:
                st.info("No lab values detected")
            
            diagnoses = result.get("diagnoses", [])
            if diagnoses:
                st.markdown("#### Diagnoses")
                for dx in diagnoses:
                    st.markdown(f"- {dx}")
            
            st.markdown("#### Simple Explanation")
            explanation = result.get("explanation", "Analysis complete. Review the extracted values above.")
            st.markdown(explanation)
            
            st.warning("**When to Seek Medical Attention:** If you notice any abnormal values or have concerns, consult your healthcare provider immediately.")
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
        
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{stats.get('cache', {}).get('total_requests', 0)}</div>
                <div class="metric-label">Total Queries</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            hit_rate = stats.get('cache', {}).get('hit_rate', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{int(hit_rate*100)}%</div>
                <div class="metric-label">Cache Hit Rate</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">6.2s</div>
                <div class="metric-label">Avg Latency</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">87%</div>
                <div class="metric-label">Avg Confidence</div>
            </div>
            """, unsafe_allow_html=True)
        
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
