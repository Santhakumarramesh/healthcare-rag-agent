"""
Analysis Workspace - Structured medical Q&A and report analysis

Premium interface for evidence-based responses with confidence scoring,
source citations, and safety boundaries.
"""
import streamlit as st
import requests
import os
from pathlib import Path
from datetime import datetime
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Page config
st.set_page_config(
    page_title="Analysis Workspace - Clinical Intelligence",
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

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://healthcare-rag-api.onrender.com")

# Initialize session state
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []

if "current_analysis" not in st.session_state:
    st.session_state.current_analysis = None

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #0E3A5D 0%, #185C8D 100%); 
            border-radius: 16px; padding: 2rem; margin-bottom: 2rem; color: white;">
    <div style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">Analysis Workspace</div>
    <div style="font-size: 1rem; opacity: 0.9;">
        Evidence-based medical analysis with structured insights, confidence scoring, and source citations
    </div>
</div>
""", unsafe_allow_html=True)

# Back button
if st.button("← Back to Care Home", key="back_home"):
    st.switch_page("app_clinical.py")

st.markdown("<br>", unsafe_allow_html=True)

# Two-column layout: Sidebar + Main Content
col_sidebar, col_main = st.columns([1, 2.5], gap="large")

with col_sidebar:
    st.markdown("""
    <div class="analysis-sidebar">
        <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
            New Analysis
        </div>
    """, unsafe_allow_html=True)
    
    # Query input
    query = st.text_area(
        "Enter your medical question",
        height=150,
        placeholder="Example: What are the symptoms of diabetes? What does elevated creatinine mean?",
        key="query_input"
    )
    
    # Analysis button
    analyze_btn = st.button("Analyze Question", use_container_width=True, type="primary")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("""
    <div class="analysis-sidebar">
        <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
            Quick Actions
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("📄 Analyze Report Instead", use_container_width=True):
        st.switch_page("pages/3_Report_Analyzer.py")
    
    if st.button("📊 View Follow-up Monitor", use_container_width=True):
        st.switch_page("pages/clinical/3_Ongoing_Monitoring.py")
    
    if st.button("📋 View Records Timeline", use_container_width=True):
        st.switch_page("pages/clinical/4_Records_Timeline.py")
    
    st.markdown("</div>", unsafe_allow_html=True)

with col_main:
    if analyze_btn and query:
        with st.spinner("Analyzing your question with evidence-based AI..."):
            try:
                # Call API
                response = requests.post(
                    f"{API_BASE_URL}/chat",
                    json={"query": query},
                    timeout=120
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.current_analysis = data
                    st.session_state.analysis_history.append({
                        "query": query,
                        "response": data,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                    # Update session stats
                    if "questions_answered" in st.session_state:
                        st.session_state.questions_answered += 1
                else:
                    st.error(f"API Error: {response.status_code}")
                    st.session_state.current_analysis = None
            
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.session_state.current_analysis = None
    
    # Display current analysis
    if st.session_state.current_analysis:
        data = st.session_state.current_analysis
        
        # Emergency alert if present
        if data.get("is_emergency"):
            st.markdown("""
            <div class="risk-alert risk-alert-high">
                <div class="risk-alert-icon">⚠️</div>
                <div class="risk-alert-content">
                    <div class="risk-alert-title">Emergency Detected</div>
                    <div class="risk-alert-message">
                        This query contains emergency symptoms. Seek immediate medical attention.
                        Call emergency services or go to the nearest emergency room.
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Main answer card
        st.markdown('<div class="answer-card">', unsafe_allow_html=True)
        
        # Summary section
        st.markdown("""
        <div class="answer-section">
            <div class="answer-section-title">Summary</div>
        """, unsafe_allow_html=True)
        
        answer = data.get("answer") or data.get("response", "No answer available")
        st.markdown(f'<div class="answer-summary">{answer}</div>', unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Key Insights
        if data.get("key_insights"):
            st.markdown("""
            <div class="answer-section">
                <div class="answer-section-title">Key Insights</div>
                <div class="findings-grid">
            """, unsafe_allow_html=True)
            
            for insight in data["key_insights"]:
                st.markdown(f"""
                <div class="finding-card">
                    <div class="finding-value">{insight}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Possible Considerations
        if data.get("possible_considerations"):
            st.markdown("""
            <div class="answer-section">
                <div class="answer-section-title">Possible Considerations</div>
                <div class="findings-grid">
            """, unsafe_allow_html=True)
            
            for consideration in data["possible_considerations"]:
                st.markdown(f"""
                <div class="finding-card">
                    <div class="finding-value">{consideration}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Next Steps
        if data.get("next_steps"):
            st.markdown("""
            <div class="answer-section">
                <div class="answer-section-title">Suggested Next Steps</div>
                <div class="findings-grid">
            """, unsafe_allow_html=True)
            
            for step in data["next_steps"]:
                st.markdown(f"""
                <div class="finding-card">
                    <div class="finding-value">{step}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Confidence and Quality Metrics
        st.markdown("""
        <div class="answer-section">
            <div class="answer-section-title">Analysis Quality</div>
        """, unsafe_allow_html=True)
        
        confidence = data.get("confidence", 0)
        confidence_class = "high" if confidence > 0.8 else "medium" if confidence > 0.6 else "low"
        
        col_conf1, col_conf2, col_conf3 = st.columns(3)
        
        with col_conf1:
            st.markdown(f"""
            <div class="finding-card">
                <div class="finding-title">Confidence Score</div>
                <div class="finding-value">
                    <span class="confidence-badge confidence-{confidence_class}">{confidence:.0%}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_conf2:
            quality = data.get("quality_score", 0)
            quality_class = "high" if quality > 0.8 else "medium" if quality > 0.6 else "low"
            st.markdown(f"""
            <div class="finding-card">
                <div class="finding-title">Quality Score</div>
                <div class="finding-value">
                    <span class="confidence-badge confidence-{quality_class}">{quality:.0%}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_conf3:
            latency = data.get("latency_ms", 0) / 1000
            st.markdown(f"""
            <div class="finding-card">
                <div class="finding-title">Response Time</div>
                <div class="finding-value">{latency:.2f}s</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Evidence Sources
        if data.get("sources"):
            st.markdown("""
            <div class="answer-section">
                <div class="answer-section-title">Evidence Sources</div>
                <div class="evidence-container">
            """, unsafe_allow_html=True)
            
            for idx, source in enumerate(data["sources"][:5], 1):
                content = source.get("content", "No content")[:200] + "..."
                relevance = source.get("relevance_score", 0)
                
                st.markdown(f"""
                <div class="evidence-source">
                    <div class="evidence-header">
                        <div class="evidence-title">Source {idx}</div>
                        <div class="evidence-relevance">Relevance: {relevance:.0%}</div>
                    </div>
                    <div class="evidence-content">{content}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Safety Boundary Card
        safety_note = data.get("safety_note", "This assistant does not replace professional medical advice.")
        st.markdown(f"""
        <div class="safety-card">
            <div class="safety-title">⚠️ Safety Boundary</div>
            <div class="safety-content">
                {safety_note}<br><br>
                This AI assistant provides information only. Always consult qualified healthcare 
                professionals for medical decisions, diagnosis, or treatment.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # Empty state
        st.markdown("""
        <div class="answer-card" style="text-align: center; padding: 4rem 2rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;">💬</div>
            <div style="font-size: 1.25rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">
                Ready to Analyze
            </div>
            <div style="color: var(--text-secondary);">
                Enter your medical question in the sidebar to get started with evidence-based analysis
            </div>
        </div>
        """, unsafe_allow_html=True)

# Analysis History
if st.session_state.analysis_history:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
        Recent Analyses
    </div>
    """, unsafe_allow_html=True)
    
    for item in reversed(st.session_state.analysis_history[-3:]):
        with st.expander(f"📝 {item['query'][:60]}... ({item['timestamp']})"):
            st.markdown(f"**Answer:** {item['response'].get('answer', 'N/A')[:200]}...")
            st.markdown(f"**Confidence:** {item['response'].get('confidence', 0):.0%}")
