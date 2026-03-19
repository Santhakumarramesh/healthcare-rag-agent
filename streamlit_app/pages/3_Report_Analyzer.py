"""
Medical Report Analyzer Page.

Upload reports (PDF, image, text) for structured analysis.
"""
from __future__ import annotations

import streamlit as st
import requests
import pandas as pd
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.layout import load_css, page_header, render_sidebar_status
from components.badges import confidence_badge, flag_badge

API_BASE_URL = os.getenv("API_BASE_URL", "https://healthcare-rag-api.onrender.com")




def render_abnormal_table(values: list[dict]) -> None:
    """Render extracted values table with abnormal highlighting."""
    if not values:
        st.markdown('<div style="color: #486581; font-size: 14px; padding: 20px; text-align: center; background: white; border: 1px solid #D9E2EC; border-radius: 12px;">No structured lab values detected</div>', unsafe_allow_html=True)
        return

    st.markdown("### Extracted Values")
    
    # Build HTML table
    table_html = '''
    <table style="width: 100%; border-collapse: collapse; background: white; border: 1px solid #D9E2EC; border-radius: 12px; overflow: hidden;">
        <thead>
            <tr style="background: #F7FAFC;">
                <th style="padding: 12px; text-align: left; font-size: 13px; font-weight: 600; color: #486581; text-transform: uppercase;">Test Name</th>
                <th style="padding: 12px; text-align: left; font-size: 13px; font-weight: 600; color: #486581; text-transform: uppercase;">Value</th>
                <th style="padding: 12px; text-align: left; font-size: 13px; font-weight: 600; color: #486581; text-transform: uppercase;">Unit</th>
                <th style="padding: 12px; text-align: left; font-size: 13px; font-weight: 600; color: #486581; text-transform: uppercase;">Reference</th>
                <th style="padding: 12px; text-align: left; font-size: 13px; font-weight: 600; color: #486581; text-transform: uppercase;">Status</th>
            </tr>
        </thead>
        <tbody>
    '''
    
    for val in values:
        flag = val.get("flag", "").lower()
        row_bg = "#FDECEC" if flag in ["high", "low"] else "white"
        
        table_html += f'''
            <tr style="background: {row_bg}; border-top: 1px solid #D9E2EC;">
                <td style="padding: 12px; font-size: 14px; color: #102A43; font-weight: 500;">{val.get("name", "")}</td>
                <td style="padding: 12px; font-size: 14px; color: #102A43; font-weight: 600;">{val.get("value", "")}</td>
                <td style="padding: 12px; font-size: 13px; color: #486581;">{val.get("unit", "") or "—"}</td>
                <td style="padding: 12px; font-size: 13px; color: #486581;">{val.get("reference", "") or "—"}</td>
                <td style="padding: 12px; font-size: 13px;">{flag_badge(val.get("flag", ""))}</td>
            </tr>
        '''
    
    table_html += '</tbody></table>'
    st.markdown(table_html, unsafe_allow_html=True)


def render_sources(sources: list[dict]) -> None:
    """Render source citations."""
    st.subheader("Sources")
    if not sources:
        st.caption("No source citations returned.")
        return

    for idx, src in enumerate(sources, start=1):
        with st.expander(f"{idx}. {src.get('title', src.get('source', 'Source'))}"):
            st.write(f"**Score:** {src.get('score', 'N/A')}")
            if src.get("category"):
                st.write(f"**Category:** {src['category']}")
            st.write(src.get("preview", ""))


def call_report_api(file_obj=None, raw_text: str = "") -> dict:
    """Call report analysis API."""
    if file_obj is not None:
        url = f"{API_BASE_URL}/reports/analyze"
        files = {"file": (file_obj.name, file_obj, file_obj.type)}
        response = requests.post(url, files=files, timeout=120)
    else:
        url = f"{API_BASE_URL}/reports/analyze-text"
        response = requests.post(url, json={"text": raw_text}, timeout=120)

    response.raise_for_status()
    return response.json()


# Page config
st.set_page_config(page_title="Report Analyzer", layout="wide", page_icon="📋")

# Load custom CSS
load_css()

# Sidebar
render_sidebar_status()

# Main content
page_header("Report Analyzer", "Upload medical reports for structured extraction and analysis")

left, right = st.columns([1, 1.25], gap="large")

with left:
    st.markdown("### Input")
    input_mode = st.radio("Choose input type", ["File Upload", "Paste Text"], horizontal=True)

    uploaded_file = None
    raw_text = ""

    if input_mode == "File Upload":
        uploaded_file = st.file_uploader(
            "Upload report",
            type=["pdf", "png", "jpg", "jpeg", "txt"],
            help="Supported formats: PDF, PNG, JPG, JPEG, TXT"
        )
        if uploaded_file:
            st.success(f"File uploaded: {uploaded_file.name}")
    else:
        raw_text = st.text_area(
            "Paste report text",
            height=280,
            placeholder="Paste lab report text, discharge note, or prescription content..."
        )

    analyze_clicked = st.button("Analyze Report", use_container_width=True)

with right:
    st.markdown("### Results")

    if analyze_clicked:
        if uploaded_file is None and not raw_text.strip():
            st.warning("Please upload a file or paste report text.")
        else:
            try:
                with st.spinner("Analyzing report..."):
                    result = call_report_api(file_obj=uploaded_file, raw_text=raw_text)

                confidence = float(result.get("confidence", 0.0))
                confidence_badge(confidence)

                col1, col2 = st.columns([1.2, 1], gap="large")

                with col1:
                    st.subheader("Summary")
                    st.write(result.get("summary", "No summary returned."))

                    st.subheader("Simple Explanation")
                    st.write(result.get("simple_explanation", "No explanation returned."))

                    concerns = result.get("potential_concerns", [])
                    st.subheader("Potential Concerns")
                    if concerns:
                        for item in concerns:
                            st.write(f"- {item}")
                    else:
                        st.caption("No major concerns identified from the extracted report content.")

                    steps = result.get("next_steps", [])
                    st.subheader("Suggested Next Steps")
                    if steps:
                        for item in steps:
                            st.write(f"- {item}")
                    else:
                        st.caption("No suggested next steps returned.")

                with col2:
                    render_abnormal_table(result.get("extracted_values", []))

                st.markdown("---")
                render_sources(result.get("sources", []))

                st.markdown("---")
                st.subheader("Safety Note")
                st.info(result.get(
                    "safety_note",
                    "This analysis is informational and should not replace clinical judgment."
                ))

            except requests.HTTPError as e:
                st.error(f"API request failed: {e}")
            except requests.Timeout:
                st.error("Analysis timed out. The report may be too complex. Please try again.")
            except Exception as e:
                st.error(f"Unexpected error: {e}")
    else:
        st.info("Upload a file or paste report text, then click Analyze Report.")
