"""
Ask AI Page - Structured medical Q&A with evidence-based answers

Single wide content area with:
- Query input bar
- Suggested questions
- Structured answer stack (7 cards)
- Right utility rail (optional)
"""
import streamlit as st
import requests
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from components.healthcare_components import (
    render_app_shell,
    render_sidebar_nav,
    render_page_header,
    render_query_input_bar,
    render_prompt_suggestion_row,
    render_confidence_badge,
    render_source_citation_card,
    render_safety_notice,
    render_risk_alert_banner
)

# Page config
render_app_shell()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://healthcare-rag-api.onrender.com")

# Sidebar
render_sidebar_nav("Ask AI")

# Page header
render_page_header(
    "Ask AI",
    "Evidence-based medical Q&A with structured insights, confidence scoring, and source citations"
)

# Initialize session state
if "ai_qa_history" not in st.session_state:
    st.session_state.ai_qa_history = []

if "current_answer" not in st.session_state:
    st.session_state.current_answer = None

# Main content area
col_main, col_util = st.columns([2.5, 1], gap="large")

with col_main:
    # Section 1: Query Bar
    st.markdown("""
    <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
        Ask Your Question
    </div>
    """, unsafe_allow_html=True)
    
    # Simple text area without session state conflicts
    query = st.text_area(
        "",
        height=120,
        placeholder="Example: What are the symptoms of diabetes? What does elevated creatinine mean?",
        key="ai_query_input",
        label_visibility="collapsed"
    )
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    with col_btn1:
        ask_btn = st.button("Ask Question", type="primary", use_container_width=True, key="ask_btn")
    
    # Section 2: Suggested Questions
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="font-size: 0.875rem; color: var(--text-muted); margin-bottom: 0.5rem;">Suggested Questions:</div>', unsafe_allow_html=True)
    
    suggestions = [
        "What are the symptoms of diabetes?",
        "What does elevated creatinine mean?",
        "Explain drug interactions",
        "When should I see a doctor?"
    ]
    
    cols = st.columns(len(suggestions))
    selected_suggestion = None
    for idx, (col, suggestion) in enumerate(zip(cols, suggestions)):
        with col:
            if st.button(suggestion, key=f"suggestion_{idx}", use_container_width=True):
                selected_suggestion = suggestion
    
    if selected_suggestion:
        query = selected_suggestion
        ask_btn = True
    
    # Process query
    if ask_btn and query:
        with st.spinner("Analyzing your question with evidence-based AI..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/chat",
                    json={"query": query},
                    timeout=120
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.current_answer = data
                    st.session_state.ai_qa_history.append({
                        "query": query,
                        "answer": data,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                    if "questions_answered" in st.session_state:
                        st.session_state.questions_answered += 1
                    
                    st.rerun()
                else:
                    st.error(f"API Error: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section 3: Answer Stack
    if st.session_state.current_answer:
        data = st.session_state.current_answer
        
        # Emergency alert if present
        if data.get("is_emergency"):
            render_risk_alert_banner(
                "high",
                "Emergency symptoms detected. Seek immediate medical attention. Call emergency services or go to the nearest emergency room."
            )
        
        # Card A: Final Answer
        st.markdown("""
        <div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
            Answer
        </div>
        """, unsafe_allow_html=True)
        
        answer = data.get("answer") or data.get("response", "No answer available")
        st.markdown(f"""
        <div class="answer-card">
            <div class="answer-summary">{answer}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Card B: Key Insights
        if data.get("key_insights"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
                Key Insights
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="findings-grid">', unsafe_allow_html=True)
            for insight in data["key_insights"]:
                st.markdown(f"""
                <div class="finding-card">
                    <div class="finding-value">{insight}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Card C: Possible Concerns
        if data.get("possible_considerations"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
                Possible Considerations
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="findings-grid">', unsafe_allow_html=True)
            for consideration in data["possible_considerations"]:
                st.markdown(f"""
                <div class="finding-card">
                    <div class="finding-value">{consideration}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Card D: Next Best Step
        if data.get("next_steps"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
                Suggested Next Steps
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="findings-grid">', unsafe_allow_html=True)
            for step in data["next_steps"]:
                st.markdown(f"""
                <div class="finding-card">
                    <div class="finding-value">{step}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Card E: Confidence
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
            Analysis Quality
        </div>
        """, unsafe_allow_html=True)
        
        col_q1, col_q2, col_q3 = st.columns(3)
        
        confidence = data.get("confidence", 0)
        quality = data.get("quality_score", 0)
        latency = data.get("latency_ms", 0) / 1000
        
        conf_class = "high" if confidence > 0.8 else "medium" if confidence > 0.6 else "low"
        qual_class = "high" if quality > 0.8 else "medium" if quality > 0.6 else "low"
        
        with col_q1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Confidence</div>
                <div class="metric-value">
                    <span class="confidence-badge confidence-{conf_class}">{confidence:.0%}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_q2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Quality Score</div>
                <div class="metric-value">
                    <span class="confidence-badge confidence-{qual_class}">{quality:.0%}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_q3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Response Time</div>
                <div class="metric-value">{latency:.2f}s</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Card F: Sources
        if data.get("sources"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
                Evidence Sources
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="evidence-container">', unsafe_allow_html=True)
            for idx, source in enumerate(data["sources"][:5], 1):
                render_source_citation_card(source, idx)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Card G: Safety Note
        st.markdown("<br>", unsafe_allow_html=True)
        render_safety_notice()
    
    else:
        # Empty state
        st.markdown("""
        <div class="answer-card" style="text-align: center; padding: 4rem 2rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;">💬</div>
            <div style="font-size: 1.25rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">
                Ready to Answer
            </div>
            <div style="color: var(--text-secondary);">
                Ask a medical question to get evidence-based answers with confidence scoring
            </div>
        </div>
        """, unsafe_allow_html=True)

# Section 4: Right Utility Rail
with col_util:
    st.markdown("""
    <div class="answer-card">
        <div style="font-size: 1.1rem; font-weight: 700; margin-bottom: 1rem;">
            Context
        </div>
    """, unsafe_allow_html=True)
    
    # Last uploaded report
    if "current_report" in st.session_state and st.session_state.current_report:
        st.markdown("""
        <div style="padding: 1rem; background: var(--info-light); border-radius: 8px; margin-bottom: 1rem;">
            <div style="font-weight: 600; color: var(--teal-primary); margin-bottom: 0.5rem;">
                Recent Report
            </div>
            <div style="font-size: 0.875rem; color: var(--text-secondary);">
                You recently analyzed a report. You can ask questions about it.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Active follow-up case
    if "active_followup_cases" in st.session_state and st.session_state.active_followup_cases > 0:
        st.markdown("""
        <div style="padding: 1rem; background: var(--warning-light); border-radius: 8px; margin-bottom: 1rem;">
            <div style="font-weight: 600; color: var(--warning); margin-bottom: 0.5rem;">
                Active Follow-up
            </div>
            <div style="font-size: 0.875rem; color: var(--text-secondary);">
                You have an active condition follow-up case.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent question history
    if st.session_state.ai_qa_history:
        st.markdown("""
        <div style="font-weight: 600; margin-top: 1.5rem; margin-bottom: 0.75rem;">
            Recent Questions
        </div>
        """, unsafe_allow_html=True)
        
        for item in reversed(st.session_state.ai_qa_history[-5:]):
            query_preview = item["query"][:40] + "..."
            timestamp = item["timestamp"]
            
            st.markdown(f"""
            <div style="padding: 0.75rem; background: var(--background); border-radius: 8px; margin-bottom: 0.5rem;">
                <div style="font-size: 0.875rem; color: var(--text-primary); margin-bottom: 0.25rem;">
                    {query_preview}
                </div>
                <div style="font-size: 0.75rem; color: var(--text-muted);">
                    {timestamp}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Footer actions
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    if st.button("← Back to Home", use_container_width=True):
        st.switch_page("app_healthcare.py")

with col_f2:
    if st.button("Analyze Report", use_container_width=True):
        st.switch_page("pages/1_Analyze_Report.py")

with col_f3:
    if st.button("View Records", use_container_width=True):
        st.switch_page("pages/4_Records_Timeline.py")
