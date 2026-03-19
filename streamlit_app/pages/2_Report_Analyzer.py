"""
Medical Report Analyzer Page.

Upload reports (PDF, image, text) for structured analysis.
"""
from __future__ import annotations

import streamlit as st
import requests
import pandas as pd
import os

API_BASE_URL = os.getenv("API_BASE_URL", "https://healthcare-rag-api.onrender.com")


def render_confidence_badge(confidence: float) -> None:
    """Render confidence badge with color coding."""
    if confidence >= 0.85:
        bg = "#E6F4EA"
        fg = "#1E7E34"
        label = "High Confidence"
    elif confidence >= 0.65:
        bg = "#FFF4E5"
        fg = "#B26A00"
        label = "Moderate Confidence"
    else:
        bg = "#FDECEC"
        fg = "#B42318"
        label = "Low Confidence"

    st.markdown(
        f"""
        <div style="
            display:inline-block;
            padding:8px 14px;
            border-radius:999px;
            background:{bg};
            color:{fg};
            font-weight:600;
            font-size:14px;
            margin-bottom:10px;
        ">
            {label}: {int(confidence * 100)}%
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_abnormal_table(values: list[dict]) -> None:
    """Render extracted values table with abnormal highlighting."""
    if not values:
        st.info("No structured lab values detected.")
        return

    df = pd.DataFrame(values)

    def flag_style(row):
        abnormal = str(row.get("flag", "")).lower() in {"high", "low", "abnormal", "critical"}
        return ["background-color: #FDECEC" if abnormal else "" for _ in row]

    st.subheader("Extracted Values")
    styled = df.style.apply(flag_style, axis=1)
    st.dataframe(styled, use_container_width=True)


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

# Custom CSS
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        background-color: #2E7D32;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 12px;
        border: none;
    }
    .stButton > button:hover {
        background-color: #1B5E20;
    }
    h1 {
        color: #1565C0;
        font-weight: 700;
    }
    h2, h3 {
        color: #424242;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.title("📋 Report Analyzer")
st.caption("Upload a medical report, prescription, or lab result for structured extraction and grounded explanation.")

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
                render_confidence_badge(confidence)

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
