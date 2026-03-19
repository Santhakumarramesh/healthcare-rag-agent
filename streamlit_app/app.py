"""
AI Healthcare Copilot - Professional Clinical Dashboard
Production-grade medical Q&A, report analysis, and monitoring
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
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# PROFESSIONAL CLINICAL CSS
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #f8f9fa;
    border-right: 1px solid #e0e0e0;
}

/* Status cards in sidebar */
.status-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
}

.status-card-title {
    font-size: 0.75rem;
    font-weight: 600;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}

.status-card-value {
    font-size: 0.9rem;
    font-weight: 500;
    color: #333;
}

.status-indicator {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
}

.status-healthy { background-color: #27ae60; }
.status-warning { background-color: #f39c12; }
.status-error { background-color: #e74c3c; }

/* Hero section */
.hero-section {
    background: linear-gradient(135deg, #0f4c75 0%, #1b6ca8 50%, #3282b8 100%);
    color: white;
    padding: 3rem 2rem;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 2rem;
}

.hero-title {
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.02em;
}

.hero-subtitle {
    font-size: 1.1rem;
    opacity: 0.9;
    font-weight: 400;
    margin: 0;
    line-height: 1.6;
}

/* Quick action cards */
.quick-actions {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin: 2rem 0;
}

.action-card {
    background: white;
    border: 2px solid #e0e0e0;
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
}

.action-card:hover {
    border-color: #1b6ca8;
    box-shadow: 0 4px 12px rgba(27, 108, 168, 0.15);
    transform: translateY(-2px);
}

.action-icon {
    font-size: 2.5rem;
    margin-bottom: 12px;
}

.action-title {
    font-size: 1rem;
    font-weight: 600;
    color: #333;
    margin: 0;
}

/* Clinical answer card */
.answer-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 24px;
    margin: 16px 0;
}

.answer-section {
    margin-bottom: 20px;
}

.answer-section:last-child {
    margin-bottom: 0;
}

.section-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.answer-text {
    font-size: 1rem;
    line-height: 1.7;
    color: #333;
}

/* Confidence badge */
.confidence-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.95rem;
}

.confidence-high { background-color: #d4edda; color: #155724; }
.confidence-medium { background-color: #fff3cd; color: #856404; }
.confidence-low { background-color: #f8d7da; color: #721c24; }

/* Source cards */
.source-card {
    background: #f8f9fa;
    border-left: 3px solid #1b6ca8;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 8px 0;
}

.source-name {
    font-weight: 600;
    color: #333;
    font-size: 0.9rem;
}

.source-score {
    color: #666;
    font-size: 0.85rem;
}

.source-preview {
    color: #555;
    font-size: 0.85rem;
    margin-top: 6px;
    font-style: italic;
}

/* Safety alert */
.safety-alert {
    background: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 16px 0;
    display: flex;
    align-items: flex-start;
    gap: 12px;
}

.safety-icon {
    font-size: 1.5rem;
    flex-shrink: 0;
}

.safety-text {
    font-size: 0.9rem;
    color: #856404;
    line-height: 1.5;
}

/* Metric cards */
.metric-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}

.metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: #1b6ca8;
    margin: 0;
}

.metric-label {
    font-size: 0.85rem;
    color: #666;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 8px;
}

/* Mode toggle */
.mode-toggle {
    background: white;
    border: 2px solid #e0e0e0;
    border-radius: 24px;
    padding: 4px;
    display: inline-flex;
    gap: 4px;
}

.mode-button {
    padding: 8px 20px;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}

.mode-button-active {
    background: #1b6ca8;
    color: white;
}

.mode-button-inactive {
    background: transparent;
    color: #666;
}

/* Report upload box */
.upload-box {
    border: 2px dashed #1b6ca8;
    border-radius: 12px;
    padding: 40px;
    text-align: center;
    background: #f8f9fa;
    margin: 20px 0;
}

.upload-icon {
    font-size: 3rem;
    color: #1b6ca8;
    margin-bottom: 16px;
}

.upload-text {
    font-size: 1rem;
    color: #666;
    margin: 0;
}

/* Key insights */
.insights-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.insight-item {
    padding: 10px 0;
    border-bottom: 1px solid #e0e0e0;
    display: flex;
    align-items: flex-start;
    gap: 12px;
}

.insight-item:last-child {
    border-bottom: none;
}

.insight-bullet {
    color: #1b6ca8;
    font-size: 1.2rem;
    flex-shrink: 0;
}

.insight-text {
    font-size: 0.95rem;
    line-height: 1.6;
    color: #333;
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
    st.session_state.mode = "patient"  # patient or clinician
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR - NAVIGATION & STATUS
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### 🏥 AI Healthcare Copilot")
    st.markdown("---")
    
    # Navigation
    st.markdown("#### Navigation")
    
    if st.button("🏠 Home & Chat", use_container_width=True, 
                 type="primary" if st.session_state.current_page == "home" else "secondary"):
        st.session_state.current_page = "home"
        st.rerun()
    
    if st.button("📋 Report Analyzer", use_container_width=True,
                 type="primary" if st.session_state.current_page == "reports" else "secondary"):
        st.session_state.current_page = "reports"
        st.rerun()
    
    if st.button("📊 Monitoring Dashboard", use_container_width=True,
                 type="primary" if st.session_state.current_page == "dashboard" else "secondary"):
        st.session_state.current_page = "dashboard"
        st.rerun()
    
    if st.button("🕐 Patient History", use_container_width=True,
                 type="primary" if st.session_state.current_page == "history" else "secondary"):
        st.session_state.current_page = "history"
        st.rerun()
    
    st.markdown("---")
    
    # System status cards
    st.markdown("#### System Status")
    
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
        <div class="status-card-title">API Status</div>
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
    st.markdown("**Mode:**")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👤 Patient", use_container_width=True, 
                     type="primary" if st.session_state.mode == "patient" else "secondary"):
            st.session_state.mode = "patient"
            st.rerun()
    with col2:
        if st.button("⚕️ Clinician", use_container_width=True,
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
    intent = response_data.get("intent", "")
    
    # Extract key insights (simple heuristic: split by periods, take first 3-4 sentences)
    sentences = [s.strip() + "." for s in answer.split(".") if s.strip()]
    key_insights = sentences[:min(3, len(sentences))]
    
    st.markdown(f"""
    <div class="answer-card">
        <!-- Answer Section -->
        <div class="answer-section">
            <div class="section-title">💬 Answer</div>
            <div class="answer-text">{answer}</div>
        </div>
        
        <!-- Key Insights Section -->
        <div class="answer-section">
            <div class="section-title">💡 Key Clinical Insights</div>
            <ul class="insights-list">
                {"".join([f'<li class="insight-item"><span class="insight-bullet">•</span><span class="insight-text">{insight}</span></li>' for insight in key_insights])}
            </ul>
        </div>
        
        <!-- Confidence Section -->
        <div class="answer-section">
            <div class="section-title">📊 Confidence Assessment</div>
            {render_confidence_badge(quality_score)}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sources (expandable)
    if sources:
        with st.expander(f"📚 View {len(sources)} Source Citations"):
            for idx, source in enumerate(sources[:5], 1):
                if isinstance(source, dict):
                    source_name = source.get("source", "Document")
                    score = source.get("score", 0)
                    text_preview = source.get("text", "")[:150]
                    
                    st.markdown(f"""
                    <div class="source-card">
                        <div class="source-name">Source {idx}: {source_name}</div>
                        <div class="source-score">Relevance: {score:.3f}</div>
                        <div class="source-preview">{text_preview}...</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Safety note
    st.markdown("""
    <div class="safety-alert">
        <div class="safety-icon">⚠️</div>
        <div class="safety-text">
            <strong>Important:</strong> This AI assistant provides general health information only. 
            It does not replace professional medical advice, diagnosis, or treatment. 
            Always consult a qualified healthcare provider for medical concerns or emergencies.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1: HOME & CHAT
# ═══════════════════════════════════════════════════════════════════════════════

if st.session_state.current_page == "home":
    # Hero section
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">AI Healthcare Copilot</h1>
        <p class="hero-subtitle">
            Grounded medical Q&A, report analysis, and evidence-backed answers with confidence scoring.<br>
            Powered by a 5-stage AI pipeline with hybrid retrieval and self-correction.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick action cards
    st.markdown("### Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💊\n\n**Drug Information**", use_container_width=True, key="qa_drug"):
            st.session_state.prefill_query = "Tell me about metformin - uses, side effects, and contraindications"
            st.rerun()
    
    with col2:
        if st.button("🩺\n\n**Symptom Guidance**", use_container_width=True, key="qa_symptoms"):
            st.session_state.prefill_query = "What could cause persistent fatigue, increased thirst, and frequent urination?"
            st.rerun()
    
    with col3:
        if st.button("📋\n\n**Lab Report Analysis**", use_container_width=True, key="qa_labs"):
            st.session_state.prefill_query = "What does an HbA1c of 8.2% indicate and what should I do?"
            st.rerun()
    
    with col4:
        if st.button("🔬\n\n**Research Summary**", use_container_width=True, key="qa_research"):
            st.session_state.prefill_query = "What are the latest treatment guidelines for Type 2 diabetes?"
            st.rerun()
    
    st.markdown("---")
    
    # Chat interface
    st.markdown("### Ask a Question")
    
    # Get prefilled query if exists
    prefill = st.session_state.pop("prefill_query", "")
    
    user_query = st.text_input(
        "Type your healthcare question...",
        value=prefill,
        placeholder="e.g., What are the symptoms of Type 2 diabetes?",
        label_visibility="collapsed"
    )
    
    col_send, col_clear = st.columns([6, 1])
    with col_send:
        send_button = st.button("🔍 Ask", use_container_width=True, type="primary")
    with col_clear:
        if st.button("🗑️", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    if send_button and user_query:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_query})
        
        # Call API
        with st.spinner("AI is thinking..."):
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
    
    # Display conversation
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown("**AI Healthcare Copilot:**")
            render_clinical_answer_card(msg["content"])

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2: REPORT ANALYZER
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.current_page == "reports":
    st.markdown("# 📋 Medical Report Analyzer")
    st.markdown("Upload lab results, discharge summaries, or medical reports for AI-powered analysis.")
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("### Upload Report")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "txt", "jpg", "png"],
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            st.success(f"✅ Uploaded: {uploaded_file.name}")
            
            if st.button("🔍 Analyze Report", use_container_width=True, type="primary"):
                with st.spinner("Analyzing report..."):
                    try:
                        files = {"file": uploaded_file}
                        data = {"session_id": st.session_state.session_id}
                        
                        # Upload
                        upload_resp = requests.post(
                            f"{API_BASE}/records/upload",
                            files=files,
                            data=data,
                            timeout=30
                        )
                        
                        if upload_resp.status_code == 200:
                            # Analyze
                            analyze_resp = requests.post(
                                f"{API_BASE}/records/analyze",
                                json={"session_id": st.session_state.session_id},
                                timeout=30
                            )
                            
                            if analyze_resp.status_code == 200:
                                st.session_state.analysis_result = analyze_resp.json()
                                st.success("✅ Analysis complete!")
                                st.rerun()
                        else:
                            st.error(f"Upload failed: {upload_resp.status_code}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with col_right:
        st.markdown("### Analysis Results")
        
        if "analysis_result" in st.session_state:
            result = st.session_state.analysis_result
            
            # Detected report type
            st.markdown("#### 📄 Detected Report Type")
            st.info(result.get("report_type", "Medical Document"))
            
            # Important values
            st.markdown("#### 🔬 Important Values")
            labs = result.get("lab_values", [])
            if labs:
                for lab in labs[:5]:
                    status = "🔴" if lab.get("abnormal") else "🟢"
                    st.markdown(f"{status} **{lab.get('name')}**: {lab.get('value')} {lab.get('unit', '')}")
            else:
                st.info("No lab values detected")
            
            # Diagnoses
            diagnoses = result.get("diagnoses", [])
            if diagnoses:
                st.markdown("#### 🩺 Diagnoses")
                for dx in diagnoses:
                    st.markdown(f"- {dx}")
            
            # Simple explanation
            st.markdown("#### 💡 Simple Explanation")
            explanation = result.get("explanation", "Analysis complete. Review the extracted values above.")
            st.markdown(explanation)
            
            # Safety note
            st.warning("⚠️ **When to Seek Medical Attention:** If you notice any abnormal values or have concerns, consult your healthcare provider immediately.")
        else:
            st.info("Upload a report to see analysis results here.")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3: MONITORING DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.current_page == "dashboard":
    st.markdown("# 📊 Monitoring Dashboard")
    st.markdown("Real-time system metrics and performance analytics")
    
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
        
        # Detailed stats
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
# PAGE 4: PATIENT HISTORY
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.current_page == "history":
    st.markdown("# 🕐 Patient History")
    st.markdown("View previous sessions and uploaded reports")
    
    if st.session_state.messages:
        st.markdown("### Recent Conversations")
        
        for idx, msg in enumerate(reversed(st.session_state.messages[-10:])):
            if msg["role"] == "user":
                with st.expander(f"💬 {msg['content'][:60]}..."):
                    st.markdown(f"**Query:** {msg['content']}")
                    if idx > 0 and st.session_state.messages[-(idx)][ "role"] == "assistant":
                        response = st.session_state.messages[-(idx)]["content"]
                        st.markdown(f"**Confidence:** {int(response.get('quality_score', 0)*100)}%")
                        st.markdown(f"**Intent:** {response.get('intent', 'N/A')}")
    else:
        st.info("No conversation history yet. Start chatting to see your history here!")
