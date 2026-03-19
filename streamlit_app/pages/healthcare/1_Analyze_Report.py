"""
Analyze Report Page - Flagship workflow for medical report analysis

Two-column layout:
- Left: Upload panel, metadata, extracted values summary
- Right: Analysis results, values table, concerns, next steps, sources
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
    render_upload_dropzone,
    render_clinical_summary_card,
    render_important_values_table,
    render_source_citation_card,
    render_safety_notice,
    render_confidence_badge
)

# Page config
render_app_shell()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://healthcare-rag-api.onrender.com")

# Sidebar
render_sidebar_nav("Analyze Report")

# Page header
render_page_header(
    "Analyze Report",
    "Upload medical reports for structured extraction, analysis, and plain-language explanation"
)

# Initialize session state
if "current_report" not in st.session_state:
    st.session_state.current_report = None

if "report_analysis" not in st.session_state:
    st.session_state.report_analysis = None

# Two-column layout
col_left, col_right = st.columns([1, 1.8], gap="large")

# ============================================================================
# LEFT COLUMN
# ============================================================================

with col_left:
    # Section 1: Upload Panel
    st.markdown("""
    <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
        Upload Report
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = render_upload_dropzone(key="report_upload")
    
    # Text input option
    with st.expander("Or paste report text"):
        report_text = st.text_area(
            "Paste report text here",
            height=200,
            placeholder="Paste lab report or medical document text...",
            key="report_text_input"
        )
        
        if st.button("Analyze Text", type="primary", use_container_width=True):
            if report_text:
                with st.spinner("Analyzing report text..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/reports/analyze-text",
                            json={"text": report_text},
                            timeout=120
                        )
                        
                        if response.status_code == 200:
                            st.session_state.report_analysis = response.json()
                            st.session_state.current_report = {
                                "type": "text",
                                "content": report_text[:200] + "...",
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            if "reports_analyzed" in st.session_state:
                                st.session_state.reports_analyzed += 1
                            st.success("✓ Report analyzed successfully")
                            st.rerun()
                        else:
                            st.error(f"Analysis failed: {response.status_code}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    # Section 2: File Metadata (if uploaded)
    if st.session_state.current_report:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
            Report Metadata
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="answer-card">
            <div style="margin-bottom: 0.5rem;"><strong>Type:</strong> {st.session_state.current_report.get('type', 'Unknown')}</div>
            <div style="margin-bottom: 0.5rem;"><strong>Uploaded:</strong> {st.session_state.current_report.get('timestamp', 'N/A')}</div>
            <div style="margin-bottom: 0.5rem;"><strong>Status:</strong> <span style="color: var(--success);">✓ Analyzed</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Section 3: Extracted Values Summary
    if st.session_state.report_analysis:
        analysis = st.session_state.report_analysis
        extracted_values = analysis.get("extracted_values", [])
        abnormal_count = len([v for v in extracted_values if v.get("is_abnormal")])
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
            Extraction Summary
        </div>
        """, unsafe_allow_html=True)
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Values</div>
                <div class="metric-value">{len(extracted_values)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_s2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Abnormal</div>
                <div class="metric-value" style="color: var(--warning);">{abnormal_count}</div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# RIGHT COLUMN
# ============================================================================

with col_right:
    if st.session_state.report_analysis:
        analysis = st.session_state.report_analysis
        
        # Section 4: Analysis Summary
        st.markdown("""
        <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
            Clinical Analysis
        </div>
        """, unsafe_allow_html=True)
        
        summary = analysis.get("summary", "No summary available")
        confidence = analysis.get("confidence", 0)
        report_type = analysis.get("report_type", "Medical Report")
        
        render_clinical_summary_card(summary, confidence, report_type)
        
        
        # Section 5: Simple Explanation
        if analysis.get("simple_explanation"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
                Plain Language Explanation
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="answer-card">
                <div style="color: var(--text-secondary); line-height: 1.7;">
                    {analysis['simple_explanation']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Section 6: Important Values Table
        if analysis.get("extracted_values"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
                Important Values
            </div>
            """, unsafe_allow_html=True)
            
            render_important_values_table(analysis["extracted_values"])
        
        # Section 7: Possible Concerns (API returns 'potential_concerns')
        concerns = analysis.get("concerns") or analysis.get("potential_concerns", [])
        if concerns:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
                Possible Concerns
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="findings-grid">', unsafe_allow_html=True)
            for concern in concerns:
                st.markdown(f"""
                <div class="finding-card">
                    <div class="finding-value">{concern}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Section 8: Suggested Next Steps
        if analysis.get("next_steps"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
                Suggested Next Steps
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="findings-grid">', unsafe_allow_html=True)
            for step in analysis["next_steps"]:
                st.markdown(f"""
                <div class="finding-card">
                    <div class="finding-value">{step}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Section 9: Evidence / Sources
        if analysis.get("sources"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
                Evidence Sources
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="evidence-container">', unsafe_allow_html=True)
            for idx, source in enumerate(analysis["sources"][:5], 1):
                render_source_citation_card(source, idx)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Section 10: Safety Note
        st.markdown("<br>", unsafe_allow_html=True)
        render_safety_notice()
    
    else:
        # Empty state
        st.markdown("""
        <div class="answer-card" style="text-align: center; padding: 4rem 2rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;">📄</div>
            <div style="font-size: 1.25rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">
                Ready to Analyze
            </div>
            <div style="color: var(--text-secondary);">
                Upload a medical report or paste text to begin analysis
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer actions
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    if st.button("← Back to Home", use_container_width=True):
        st.switch_page("app_healthcare.py")

with col_f2:
    if st.button("View Records Timeline", use_container_width=True):
        st.switch_page("pages/healthcare/4_Records_Timeline.py")

with col_f3:
    if st.session_state.report_analysis:
        if st.button("Ask Question About Report", use_container_width=True):
            st.switch_page("pages/healthcare/2_Ask_AI.py")
