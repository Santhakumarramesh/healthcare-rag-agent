"""
Ask AI Page - Structured medical Q&A with evidence-based answers

Single wide content area with:
- Medical disclaimer banner
- Query input bar
- Suggested questions
- Structured answer stack (7 cards)
- 👍 / 👎 feedback buttons
- PDF export
- Right utility rail (context + rate-limit info)
"""
import uuid
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
    render_source_citation_card,
    render_safety_notice,
    render_risk_alert_banner,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helper functions (defined first so they're available throughout the script)
# ─────────────────────────────────────────────────────────────────────────────

def _send_feedback(api_base, interaction_id, session_id, query, response, rating):
    """Fire-and-forget feedback submission; silently swallows errors."""
    try:
        requests.post(
            f"{api_base}/feedback",
            json={
                "interaction_id": interaction_id or str(uuid.uuid4()),
                "session_id": session_id,
                "query": query,
                "response": response,
                "rating": rating,
            },
            timeout=10,
        )
    except Exception:
        pass  # Never crash the UI over a failed feedback call


def _build_pdf(query: str, data: dict):
    """
    Generate a PDF report for the current answer.
    Returns raw bytes on success; None if fpdf2 is not installed.
    """
    try:
        from fpdf import FPDF  # type: ignore
    except ImportError:
        return None

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── Title ─────────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(0, 90, 130)
    pdf.cell(0, 10, "Healthcare AI - Answer Report", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(4)

    # ── Disclaimer ────────────────────────────────────────────────────────────
    pdf.set_fill_color(255, 243, 205)
    pdf.set_text_color(133, 100, 4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(
        0, 5,
        "DISCLAIMER: This report is for informational purposes only and does not "
        "constitute medical advice. Always consult a qualified healthcare professional.",
        fill=True,
    )
    pdf.ln(4)

    # ── Question ──────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 8, "Question", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 6, query or "")
    pdf.ln(3)

    def _section(title, items, is_list=True):
        if not items:
            return
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(60, 60, 60)
        if isinstance(items, str):
            pdf.multi_cell(0, 6, items)
        elif is_list:
            for item in items:
                pdf.multi_cell(0, 6, f"  - {item}")
        pdf.ln(3)

    _section("Answer", data.get("answer") or data.get("response", ""), is_list=False)
    _section("Key Insights", data.get("key_insights", []))
    _section("Possible Considerations", data.get("possible_considerations", []))
    _section("Suggested Next Steps", data.get("next_steps", []))

    # ── Quality metrics ───────────────────────────────────────────────────────
    conf = data.get("confidence", 0)
    qual = data.get("quality_score", 0)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 8, "Analysis Quality", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 6, f"  Confidence: {conf:.0%}   |   Quality Score: {qual:.0%}", ln=True)
    pdf.ln(3)

    # ── Sources ───────────────────────────────────────────────────────────────
    sources = data.get("sources", [])
    if sources:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 8, "Evidence Sources", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(60, 60, 60)
        for i, src in enumerate(sources[:5], 1):
            name = src.get("title") or src.get("source") or src.get("filename") or f"Source {i}"
            snippet = src.get("content") or src.get("text") or ""
            pdf.multi_cell(0, 5, f"  [{i}] {name}")
            if snippet:
                pdf.set_text_color(100, 100, 100)
                pdf.set_font("Helvetica", "I", 8)
                pdf.multi_cell(0, 5, f"       {str(snippet)[:200]}...")
                pdf.set_text_color(60, 60, 60)
                pdf.set_font("Helvetica", "", 9)
        pdf.ln(3)

    return bytes(pdf.output())


# ── Page config ───────────────────────────────────────────────────────────────
render_app_shell()

# ── API config ────────────────────────────────────────────────────────────────
# Read from env — HF Space injects API_BASE_URL automatically;
# Streamlit Cloud users set it in Secrets.
_DEFAULT_HF_URL = "https://your-hf-username-healthcare-rag-api.hf.space"
API_BASE_URL = os.getenv("API_BASE_URL", _DEFAULT_HF_URL).rstrip("/")

# ── Sidebar ───────────────────────────────────────────────────────────────────
render_sidebar_nav("Ask AI")

with st.sidebar:
    st.markdown("---")
    st.markdown("### ⚙️ Session Info")

    # Rate-limit status (best-effort — graceful if API unreachable)
    try:
        stats_resp = requests.get(f"{API_BASE_URL}/stats", timeout=5)
        if stats_resp.ok:
            stats = stats_resp.json()
            rl = stats.get("rate_limiter", {})
            total_req = rl.get("total_requests", "—")
            st.markdown(f"**Requests today:** {total_req}")
        else:
            st.caption("Rate-limit info unavailable")
    except Exception:
        st.caption("API not reachable")

    st.markdown("---")
    st.markdown(
        "**Data notice:** Your questions are processed by an AI model. "
        "Do not submit personal health identifiers.",
        help="This app uses OpenAI / Hugging Face inference.",
    )

# ── Medical disclaimer banner ─────────────────────────────────────────────────
st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #fff3cd, #ffeeba);
        border: 1.5px solid #f0ad4e;
        border-radius: 10px;
        padding: 0.85rem 1.2rem;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    ">
        <span style="font-size: 1.4rem;">⚠️</span>
        <span style="font-size: 0.9rem; color: #856404; line-height: 1.5;">
            <strong>Medical Disclaimer:</strong> This tool provides general health information only
            and is <strong>not a substitute for professional medical advice, diagnosis, or treatment</strong>.
            Always consult a qualified healthcare provider for personal medical decisions.
            In an emergency, call <strong>911</strong> immediately.
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Page header ───────────────────────────────────────────────────────────────
render_page_header(
    "Ask AI",
    "Evidence-based medical Q&A with structured insights, confidence scoring, and source citations",
)

# ── Session state ─────────────────────────────────────────────────────────────
if "ai_qa_history" not in st.session_state:
    st.session_state.ai_qa_history = []
if "current_answer" not in st.session_state:
    st.session_state.current_answer = None
if "current_query" not in st.session_state:
    st.session_state.current_query = ""
if "current_interaction_id" not in st.session_state:
    st.session_state.current_interaction_id = None
if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = False
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# ── Main / util layout ────────────────────────────────────────────────────────
col_main, col_util = st.columns([2.5, 1], gap="large")

with col_main:
    # ── Section 1: Query Bar ──────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">Ask Your Question</div>',
        unsafe_allow_html=True,
    )

    query = st.text_area(
        "",
        height=120,
        placeholder="Example: What are the symptoms of diabetes? What does elevated creatinine mean?",
        key="ai_query_input",
        label_visibility="collapsed",
    )

    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    with col_btn1:
        ask_btn = st.button("Ask Question", type="primary", use_container_width=True, key="ask_btn")

    # ── Section 2: Suggested Questions ───────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size: 0.875rem; color: var(--text-muted); margin-bottom: 0.5rem;">Suggested Questions:</div>',
        unsafe_allow_html=True,
    )

    suggestions = [
        "What are the symptoms of diabetes?",
        "What does elevated creatinine mean?",
        "Explain drug interactions",
        "When should I see a doctor?",
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

    # ── Process query ─────────────────────────────────────────────────────────
    if ask_btn and query:
        interaction_id = str(uuid.uuid4())
        st.session_state.current_interaction_id = interaction_id
        st.session_state.feedback_submitted = False

        with st.spinner("Analyzing your question with evidence-based AI…"):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/chat",
                    json={"query": query, "session_id": st.session_state.session_id},
                    timeout=120,
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.current_answer = data
                    st.session_state.current_query = query
                    st.session_state.ai_qa_history.append(
                        {
                            "query": query,
                            "answer": data,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "interaction_id": interaction_id,
                        }
                    )
                    if "questions_answered" in st.session_state:
                        st.session_state.questions_answered += 1
                    st.rerun()
                else:
                    err_detail = ""
                    try:
                        err_detail = response.json().get("error", {}).get("message", "")
                    except Exception:
                        pass
                    st.error(f"API Error {response.status_code}: {err_detail or response.text[:200]}")
            except requests.exceptions.ConnectionError:
                st.error(
                    f"Cannot reach the API at `{API_BASE_URL}`. "
                    "Check that the backend is running and `API_BASE_URL` is set correctly."
                )
            except Exception as exc:
                st.error(f"Error: {exc}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Section 3: Answer Stack ───────────────────────────────────────────────
    if st.session_state.current_answer:
        data = st.session_state.current_answer

        # Emergency alert
        if data.get("is_emergency"):
            render_risk_alert_banner(
                "high",
                "🚨 Emergency symptoms detected. Call 911 or go to the nearest emergency room immediately.",
            )

        # ── Card A: Answer ────────────────────────────────────────────────────
        st.markdown(
            '<div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">Answer</div>',
            unsafe_allow_html=True,
        )
        answer = data.get("answer") or data.get("response", "No answer available")
        st.markdown(
            f'<div class="answer-card"><div class="answer-summary">{answer}</div></div>',
            unsafe_allow_html=True,
        )

        # ── Card B: Key Insights ──────────────────────────────────────────────
        if data.get("key_insights"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">Key Insights</div>',
                unsafe_allow_html=True,
            )
            st.markdown('<div class="findings-grid">', unsafe_allow_html=True)
            for insight in data["key_insights"]:
                st.markdown(
                    f'<div class="finding-card"><div class="finding-value">{insight}</div></div>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Card C: Possible Considerations ──────────────────────────────────
        if data.get("possible_considerations"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">Possible Considerations</div>',
                unsafe_allow_html=True,
            )
            st.markdown('<div class="findings-grid">', unsafe_allow_html=True)
            for item in data["possible_considerations"]:
                st.markdown(
                    f'<div class="finding-card"><div class="finding-value">{item}</div></div>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Card D: Next Steps ────────────────────────────────────────────────
        if data.get("next_steps"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">Suggested Next Steps</div>',
                unsafe_allow_html=True,
            )
            st.markdown('<div class="findings-grid">', unsafe_allow_html=True)
            for step in data["next_steps"]:
                st.markdown(
                    f'<div class="finding-card"><div class="finding-value">{step}</div></div>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Card E: Analysis Quality ──────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">Analysis Quality</div>',
            unsafe_allow_html=True,
        )
        col_q1, col_q2, col_q3 = st.columns(3)
        confidence = data.get("confidence", 0)
        quality = data.get("quality_score", 0)
        latency = data.get("latency_ms", 0) / 1000
        conf_class = "high" if confidence > 0.8 else "medium" if confidence > 0.6 else "low"
        qual_class = "high" if quality > 0.8 else "medium" if quality > 0.6 else "low"

        with col_q1:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Confidence</div>'
                f'<div class="metric-value"><span class="confidence-badge confidence-{conf_class}">{confidence:.0%}</span></div></div>',
                unsafe_allow_html=True,
            )
        with col_q2:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Quality Score</div>'
                f'<div class="metric-value"><span class="confidence-badge confidence-{qual_class}">{quality:.0%}</span></div></div>',
                unsafe_allow_html=True,
            )
        with col_q3:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Response Time</div>'
                f'<div class="metric-value">{latency:.2f}s</div></div>',
                unsafe_allow_html=True,
            )

        # ── Card F: Evidence Sources ──────────────────────────────────────────
        if data.get("sources"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">Evidence Sources</div>',
                unsafe_allow_html=True,
            )
            st.markdown('<div class="evidence-container">', unsafe_allow_html=True)
            for idx, source in enumerate(data["sources"][:5], 1):
                render_source_citation_card(source, idx)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Card G: Safety Notice ─────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        render_safety_notice()

        # ── Card H: 👍 / 👎 Feedback ─────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size: 1rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">Was this answer helpful?</div>',
            unsafe_allow_html=True,
        )

        if st.session_state.feedback_submitted:
            st.success("✅ Thank you for your feedback!")
        else:
            fb_col1, fb_col2, fb_col3 = st.columns([1, 1, 4])
            with fb_col1:
                if st.button("👍 Helpful", key="fb_positive", use_container_width=True):
                    _send_feedback(
                        api_base=API_BASE_URL,
                        interaction_id=st.session_state.current_interaction_id,
                        session_id=st.session_state.session_id,
                        query=st.session_state.current_query,
                        response=answer,
                        rating="positive",
                    )
                    st.session_state.feedback_submitted = True
                    st.rerun()
            with fb_col2:
                if st.button("👎 Not helpful", key="fb_negative", use_container_width=True):
                    _send_feedback(
                        api_base=API_BASE_URL,
                        interaction_id=st.session_state.current_interaction_id,
                        session_id=st.session_state.session_id,
                        query=st.session_state.current_query,
                        response=answer,
                        rating="negative",
                    )
                    st.session_state.feedback_submitted = True
                    st.rerun()

        # ── Card I: PDF Export ────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        pdf_bytes = _build_pdf(
            query=st.session_state.current_query,
            data=data,
        )
        if pdf_bytes:
            st.download_button(
                label="⬇️ Download as PDF",
                data=pdf_bytes,
                file_name=f"healthcare_answer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=False,
            )

    else:
        # ── Empty state ───────────────────────────────────────────────────────
        st.markdown(
            """
            <div class="answer-card" style="text-align: center; padding: 4rem 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;">💬</div>
                <div style="font-size: 1.25rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">
                    Ready to Answer
                </div>
                <div style="color: var(--text-secondary);">
                    Ask a medical question to get evidence-based answers with confidence scoring
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Section 4: Right Utility Rail ────────────────────────────────────────────
with col_util:
    st.markdown(
        '<div class="answer-card"><div style="font-size: 1.1rem; font-weight: 700; margin-bottom: 1rem;">Context</div>',
        unsafe_allow_html=True,
    )

    if "current_report" in st.session_state and st.session_state.current_report:
        st.markdown(
            """
            <div style="padding: 1rem; background: var(--info-light); border-radius: 8px; margin-bottom: 1rem;">
                <div style="font-weight: 600; color: var(--teal-primary); margin-bottom: 0.5rem;">Recent Report</div>
                <div style="font-size: 0.875rem; color: var(--text-secondary);">
                    You recently analyzed a report. You can ask questions about it.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if "active_followup_cases" in st.session_state and st.session_state.active_followup_cases > 0:
        st.markdown(
            """
            <div style="padding: 1rem; background: var(--warning-light); border-radius: 8px; margin-bottom: 1rem;">
                <div style="font-weight: 600; color: var(--warning); margin-bottom: 0.5rem;">Active Follow-up</div>
                <div style="font-size: 0.875rem; color: var(--text-secondary);">
                    You have an active condition follow-up case.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.ai_qa_history:
        st.markdown(
            '<div style="font-weight: 600; margin-top: 1.5rem; margin-bottom: 0.75rem;">Recent Questions</div>',
            unsafe_allow_html=True,
        )
        for item in reversed(st.session_state.ai_qa_history[-5:]):
            query_preview = item["query"][:40] + "…"
            timestamp = item["timestamp"]
            st.markdown(
                f"""
                <div style="padding: 0.75rem; background: var(--background); border-radius: 8px; margin-bottom: 0.5rem;">
                    <div style="font-size: 0.875rem; color: var(--text-primary); margin-bottom: 0.25rem;">{query_preview}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">{timestamp}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
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
