"""
streamlit_app/app.py
--------------------
Production-grade Streamlit UI for the Healthcare RAG Agent.

Tab 1 — Ask MediAssist: streaming multi-agent FAQ chat
Tab 2 — My Medical Records: upload PDFs, get structured extraction, ask questions
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

# ── Config ─────────────────────────────────────────────────────────────────────
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
APP_TITLE = "MediAssist — Healthcare RAG Agent"
APP_ICON  = "🏥"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #0f4c75 0%, #1b6ca8 50%, #163d64 100%);
        padding: 2rem; border-radius: 16px; margin-bottom: 1.5rem;
        color: white; text-align: center;
    }
    .main-header h1 { font-size: 2.2rem; font-weight: 600; margin: 0; }
    .main-header p  { opacity: 0.85; margin: 0.5rem 0 0 0; font-size: 1rem; }

    .chat-message {
        padding: 1rem 1.2rem; border-radius: 12px;
        margin: 0.6rem 0; animation: fadeIn 0.3s ease;
    }
    .chat-message.user      { background: #e8f4fd; border-left: 4px solid #1b6ca8; margin-left: 2rem; }
    .chat-message.assistant { background: #f8fffe; border-left: 4px solid #27ae60; margin-right: 2rem; }

    .source-badge {
        display: inline-block; background: #e3f2fd; color: #1565c0;
        padding: 2px 10px; border-radius: 20px; font-size: 0.75rem;
        margin: 2px; font-weight: 500;
    }
    .score-badge { display: inline-block; padding: 3px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
    .score-high   { background: #d4edda; color: #155724; }
    .score-medium { background: #fff3cd; color: #856404; }
    .score-low    { background: #f8d7da; color: #721c24; }

    .metric-card {
        background: white; padding: 1rem; border-radius: 10px;
        border: 1px solid #e0e0e0; text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #1b6ca8; }
    .metric-label { font-size: 0.8rem; color: #666; margin-top: 0.2rem; }

    .agent-trace {
        background: #f8f9fa; border-radius: 8px; padding: 1rem;
        font-size: 0.8rem; font-family: monospace; color: #444;
    }

    /* Records tab */
    .records-card {
        background: white; border-radius: 12px; padding: 1.2rem 1.5rem;
        border: 1px solid #e0e0e0; margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .records-card h4 { margin: 0 0 0.6rem 0; color: #0f4c75; font-size: 1rem; }

    .lab-normal   { background: #d4edda; color: #155724; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; }
    .lab-high     { background: #f8d7da; color: #721c24; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; }
    .lab-low      { background: #cce5ff; color: #004085; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; }
    .lab-critical { background: #f5c6cb; color: #491217; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: 800; }
    .lab-unknown  { background: #e2e3e5; color: #383d41; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; }

    .abnormal-flag {
        background: #fff3cd; border-left: 4px solid #f39c12;
        padding: 0.5rem 0.8rem; border-radius: 6px; margin: 0.3rem 0;
        font-size: 0.85rem; color: #5d4037;
    }
    .key-findings {
        background: #e8f4fd; border-left: 4px solid #1b6ca8;
        padding: 0.8rem 1rem; border-radius: 8px; font-size: 0.9rem;
    }
    .diagnosis-tag {
        display: inline-block; background: #e8f5e9; color: #1b5e20;
        padding: 3px 12px; border-radius: 20px; font-size: 0.82rem;
        margin: 2px; border: 1px solid #a5d6a7;
    }
    .allergy-tag {
        display: inline-block; background: #fce4ec; color: #880e4f;
        padding: 3px 12px; border-radius: 20px; font-size: 0.82rem;
        margin: 2px; border: 1px solid #f48fb1;
    }
    .records-answer {
        background: #f8fffe; border-left: 4px solid #27ae60;
        padding: 1rem 1.2rem; border-radius: 10px; margin-top: 0.8rem;
        font-size: 0.92rem; line-height: 1.6;
    }
    .disclaimer {
        background: #fff8e1; border: 1px solid #ffe082; border-radius: 8px;
        padding: 0.8rem 1rem; font-size: 0.82rem; color: #5d4037;
    }
    .upload-zone {
        background: #f0f7ff; border: 2px dashed #90caf9; border-radius: 12px;
        padding: 1.5rem; text-align: center; margin-bottom: 1rem;
    }

    @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; } }

    .stTextInput > div > div > input { border-radius: 10px; border: 2px solid #e0e0e0; }
    .stButton > button {
        border-radius: 10px; font-weight: 500;
        background: linear-gradient(135deg, #1b6ca8, #0f4c75);
        color: white; border: none; padding: 0.6rem 1.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Session State ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "stats" not in st.session_state:
    st.session_state.stats = {"total_queries": 0, "avg_latency": 0.0, "avg_score": 0.0}
# Records tab state
if "records_files" not in st.session_state:
    st.session_state.records_files = []
if "records_extraction" not in st.session_state:
    st.session_state.records_extraction = None
if "records_messages" not in st.session_state:
    st.session_state.records_messages = []


# ── Helper functions ───────────────────────────────────────────────────────────

def call_api(endpoint: str, payload: dict) -> dict | None:
    try:
        resp = requests.post(f"{API_BASE}{endpoint}", json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to the API server. Make sure it is running."}
    except Exception as e:
        return {"error": str(e)}


def get_health() -> dict:
    try:
        resp = requests.get(f"{API_BASE}/health", timeout=5)
        return resp.json()
    except Exception:
        return {"status": "unreachable"}


def score_badge(score: float | None) -> str:
    if score is None:
        return ""
    if score >= 0.8:
        cls, label = "score-high",   f"✅ Quality: {score:.2f}"
    elif score >= 0.6:
        cls, label = "score-medium", f"⚠️ Quality: {score:.2f}"
    else:
        cls, label = "score-low",    f"❌ Quality: {score:.2f}"
    return f'<span class="score-badge {cls}">{label}</span>'


def intent_emoji(intent: str) -> str:
    return {"medical_faq": "🩺", "general": "💬", "out_of_scope": "🚫"}.get(intent, "🤖")


def lab_status_html(status: str) -> str:
    s = (status or "UNKNOWN").upper()
    cls = {
        "NORMAL": "lab-normal", "HIGH": "lab-high",
        "LOW": "lab-low", "CRITICAL": "lab-critical",
    }.get(s, "lab-unknown")
    icons = {"NORMAL": "✅", "HIGH": "🔴", "LOW": "🔵", "CRITICAL": "🚨"}
    icon = icons.get(s, "❓")
    return f'<span class="{cls}">{icon} {s}</span>'


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 MediAssist")
    st.markdown("**Healthcare RAG Agent**")
    st.markdown("---")

    health = get_health()
    status_color = "🟢" if health.get("status") == "healthy" else "🔴"
    st.markdown(f"**API Status:** {status_color} {health.get('status', 'unknown').title()}")
    vs_ready = health.get("vector_store_ready", False)
    st.markdown(f"**Knowledge Base:** {'✅ Ready' if vs_ready else '⚠️ Empty'}")
    st.markdown("---")

    stats = st.session_state.stats
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{stats['total_queries']}</div>
            <div class="metric-label">Queries</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{stats['avg_latency']:.0f}ms</div>
            <div class="metric-label">Avg Latency</div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📄 Add to Knowledge Base")
    ingest_text = st.text_area("Paste medical text:", height=100,
                               placeholder="Paste medical guidelines, FAQs, or healthcare content…")
    ingest_source = st.text_input("Source name:", value="custom_document")
    if st.button("➕ Ingest Document", use_container_width=True):
        if ingest_text.strip():
            with st.spinner("Ingesting…"):
                resp = requests.post(f"{API_BASE}/ingest/text",
                                     json={"text": ingest_text, "source_name": ingest_source},
                                     timeout=30)
                if resp.status_code == 200:
                    st.success(f"✅ Ingested {resp.json()['chunks_stored']} chunks!")
                else:
                    st.error("Ingestion failed. Is the API running?")
        else:
            st.warning("Please enter some text to ingest.")

    st.markdown("---")
    st.markdown("### 💡 Sample Questions")
    for q in [
        "What are symptoms of Type 2 diabetes?",
        "How does ibuprofen work?",
        "What foods should I avoid with high blood pressure?",
        "What are the side effects of statins?",
    ]:
        if st.button(q, key=f"sample_{q[:20]}", use_container_width=True):
            st.session_state.prefill_query = q
            st.rerun()

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🏥 MediAssist</h1>
    <p>AI-Powered Healthcare Assistant · Multi-Agent RAG · LangGraph + GPT-4o · Medical Record Analyzer</p>
</div>
""", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_chat, tab_records = st.tabs(["💬 Ask MediAssist", "📋 My Medical Records"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Chat
# ══════════════════════════════════════════════════════════════════════════════
with tab_chat:
    st.markdown("""
    <div class="disclaimer">
        ⚕️ <strong>Medical Disclaimer:</strong> MediAssist provides general health information only.
        It is not a substitute for professional medical advice, diagnosis, or treatment.
        Always consult a qualified healthcare provider for personal medical decisions.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")

    for msg in st.session_state.messages:
        role, content = msg["role"], msg["content"]
        if role == "user":
            st.markdown(f"""<div class="chat-message user">
                <strong>You</strong><br>{content}</div>""", unsafe_allow_html=True)
        else:
            badge = score_badge(msg.get("eval_score"))
            icon  = intent_emoji(msg.get("intent", ""))
            sources_html = "".join(
                f'<span class="source-badge">📄 {s.split("/")[-1][:30]}</span>'
                for s in msg.get("sources", [])
            )
            st.markdown(f"""<div class="chat-message assistant">
                <strong>MediAssist</strong> {icon} {badge}<br><br>
                {content}
                {'<br><br><strong>Sources:</strong> ' + sources_html if sources_html else ''}
            </div>""", unsafe_allow_html=True)
            if msg.get("show_trace"):
                with st.expander("🔍 Agent Trace", expanded=False):
                    st.markdown(f"""<div class="agent-trace">
                    🔀 Router → Intent: <b>{msg.get('intent')}</b><br>
                    📚 Retriever → Sources: {len(msg.get('sources', []))} found<br>
                    💬 Responder → {len(content)} chars<br>
                    ✅ Evaluator → Score: {msg.get('eval_score', 'N/A')}
                    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    prefill = st.session_state.pop("prefill_query", "")
    col1, col2 = st.columns([5, 1])
    with col1:
        user_query = st.text_input(
            "Ask a healthcare question:",
            value=prefill,
            placeholder="e.g. What are the symptoms of diabetes?",
            label_visibility="collapsed",
            key="query_input",
        )
    with col2:
        send_clicked = st.button("Ask 🔍", use_container_width=True)

    show_trace = st.checkbox("Show agent trace", value=False)

    if (send_clicked or user_query) and user_query.strip():
        query = user_query.strip()
        st.session_state.messages.append({"role": "user", "content": query})

        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()
            full_response = ""
            try:
                with requests.post(
                    f"{API_BASE}/chat/stream",
                    json={"query": query},
                    stream=True,
                    timeout=60,
                ) as r:
                    for line in r.iter_lines():
                        if line:
                            decoded = line.decode("utf-8")
                            if decoded.startswith("data: "):
                                try:
                                    data = json.loads(decoded[6:])
                                    if data.get("type") == "token":
                                        full_response += data.get("content", "")
                                        placeholder.markdown(full_response + "▌")
                                    elif data.get("type") == "metadata":
                                        meta = data.get("content", {})
                                        st.session_state.messages.append({
                                            "role": "assistant",
                                            "content": full_response,
                                            "intent": meta.get("intent", "medical_faq"),
                                            "sources": meta.get("retrieved_chunks", []),
                                            "quality_score": meta.get("quality_score", 0.0),
                                            "hallucination_risk": meta.get("hallucination_risk", "unknown"),
                                            "agent_trace": meta.get("agent_trace", []),
                                            "show_trace": show_trace,
                                        })
                                        st.session_state.stats["total_queries"] += 1
                                        placeholder.markdown(full_response)
                                        st.rerun()
                                except json.JSONDecodeError:
                                    pass
            except Exception as e:
                st.error(f"Connection error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — My Medical Records
# ══════════════════════════════════════════════════════════════════════════════
with tab_records:
    session_id = st.session_state.session_id

    st.markdown("""
    <div class="disclaimer">
        🔒 <strong>Privacy:</strong> Your uploaded records are processed only in-memory for this browser session
        and are never saved to disk or shared. They are erased when you clear records or close the session.
        Files are sent to OpenAI's API for analysis — do not upload records containing sensitive identifiers
        if you are not comfortable with that.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")

    # ── Upload + file list ──────────────────────────────────────────────────
    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.markdown("### 📤 Upload Your Records")
        st.markdown("Supports **PDF** and **.txt** files · Max 10 MB each")

        uploaded = st.file_uploader(
            "Choose files",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="record_uploader",
        )

        if uploaded:
            new_files = [f for f in uploaded if f.name not in st.session_state.records_files]
            if new_files:
                for uf in new_files:
                    with st.spinner(f"Indexing {uf.name}…"):
                        try:
                            resp = requests.post(
                                f"{API_BASE}/records/upload",
                                data={"session_id": session_id},
                                files={"file": (uf.name, uf.getvalue(), uf.type or "application/octet-stream")},
                                timeout=60,
                            )
                            if resp.status_code == 200:
                                data = resp.json()
                                st.session_state.records_files.append(uf.name)
                                st.success(f"✅ **{uf.name}** — {data['chunks_stored']} chunks indexed")
                            else:
                                detail = resp.json().get("detail", resp.text)
                                st.error(f"❌ {uf.name}: {detail}")
                        except Exception as e:
                            st.error(f"❌ Upload failed: {e}")

        # Uploaded files list
        if st.session_state.records_files:
            st.markdown("**Indexed files:**")
            for fname in st.session_state.records_files:
                st.markdown(f"• 📄 `{fname}`")

            bcol1, bcol2 = st.columns(2)
            with bcol1:
                analyze_clicked = st.button(
                    "🔬 Analyze My Records",
                    use_container_width=True,
                    type="primary",
                )
            with bcol2:
                if st.button("🗑️ Clear All Records", use_container_width=True):
                    try:
                        requests.delete(f"{API_BASE}/records/clear/{session_id}", timeout=10)
                    except Exception:
                        pass
                    st.session_state.records_files = []
                    st.session_state.records_extraction = None
                    st.session_state.records_messages = []
                    st.rerun()

            if analyze_clicked:
                with st.spinner("Analyzing records… this takes 10-20 seconds…"):
                    try:
                        resp = requests.post(
                            f"{API_BASE}/records/analyze",
                            data={"session_id": session_id},
                            timeout=90,
                        )
                        if resp.status_code == 200:
                            st.session_state.records_extraction = resp.json()
                            st.success("✅ Analysis complete! See results on the right →")
                        else:
                            st.error(f"Analysis failed: {resp.json().get('detail', resp.text)}")
                    except Exception as e:
                        st.error(f"Analysis error: {e}")
        else:
            st.markdown("""
            <div class="upload-zone">
                <strong>Upload a PDF or text file to get started</strong><br>
                <small>Lab results · Discharge summaries · Doctor's notes · Prescription lists</small>
            </div>
            """, unsafe_allow_html=True)

        # ── Q&A section ─────────────────────────────────────────────────────
        if st.session_state.records_files:
            st.markdown("---")
            st.markdown("### 💬 Ask About Your Records")
            st.markdown(
                "Ask anything about the documents you uploaded. The AI answers "
                "**only from your records** — not from general knowledge."
            )

            for rmsg in st.session_state.records_messages:
                if rmsg["role"] == "user":
                    st.markdown(f"""<div class="chat-message user">
                        <strong>You</strong><br>{rmsg['content']}</div>""",
                        unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class="records-answer">{rmsg['content']}</div>""",
                                unsafe_allow_html=True)
                    if rmsg.get("sources"):
                        src_html = "".join(
                            f'<span class="source-badge">📄 {s["source"]} ({s["score"]:.2f})</span>'
                            for s in rmsg["sources"]
                        )
                        st.markdown(f"<small>{src_html}</small>", unsafe_allow_html=True)

            q_col, btn_col = st.columns([5, 1])
            with q_col:
                record_question = st.text_input(
                    "Your question:",
                    placeholder="e.g. What was my HbA1c result? Are any of my labs abnormal?",
                    label_visibility="collapsed",
                    key="record_q_input",
                )
            with btn_col:
                ask_record = st.button("Ask 🔍", key="ask_record_btn", use_container_width=True)

            if ask_record and record_question.strip():
                q = record_question.strip()
                st.session_state.records_messages.append({"role": "user", "content": q})
                with st.spinner("Searching your records…"):
                    try:
                        resp = requests.post(
                            f"{API_BASE}/records/query",
                            json={"session_id": session_id, "question": q},
                            timeout=60,
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            st.session_state.records_messages.append({
                                "role": "assistant",
                                "content": data["answer"],
                                "sources": data.get("sources", []),
                            })
                        else:
                            st.error(resp.json().get("detail", "Query failed."))
                    except Exception as e:
                        st.error(f"Error: {e}")
                st.rerun()

    # ── Extraction results panel ────────────────────────────────────────────
    with right_col:
        extraction = st.session_state.records_extraction

        if not extraction:
            if st.session_state.records_files:
                st.markdown("### 📊 Analysis Results")
                st.info("Click **Analyze My Records** to extract structured information from your documents.")
            else:
                st.markdown("### 📊 What You'll See Here")
                st.markdown("""
After uploading and analyzing your records, this panel will show:

- 🏥 **Patient info** — name, date, provider
- 🩺 **Diagnoses** — conditions listed in the record
- 💊 **Medications** — drugs, doses, and what they treat
- 🧪 **Lab values** — every result with a color-coded normal/abnormal indicator
- ⚠️ **Abnormal flags** — only the out-of-range values, highlighted
- 📋 **Key findings** — plain-English summary of what matters most
- ✅ **Recommended actions** — questions to ask your doctor

**Then ask questions in plain English:**
> *"What was my blood sugar result?"*
> *"Which of my labs are high?"*
> *"What does HbA1c mean?"*
                """)
        else:
            if extraction.get("error") and not extraction.get("diagnoses"):
                st.error(f"Extraction error: {extraction['error']}")
            else:
                st.markdown("### 📊 Analysis Results")
                if extraction.get("latency_ms"):
                    st.caption(f"Analyzed in {extraction['latency_ms']/1000:.1f}s")

                # Patient Info
                pi = extraction.get("patient_info", {})
                if any(v and v != "Not specified" for v in pi.values()):
                    with st.expander("👤 Patient Information", expanded=True):
                        cols = st.columns(2)
                        info_items = [
                            ("Name", pi.get("name")),
                            ("Date of Birth", pi.get("dob")),
                            ("Record Date", pi.get("record_date")),
                            ("Provider", pi.get("provider")),
                        ]
                        for i, (label, val) in enumerate(info_items):
                            if val and val != "Not specified":
                                with cols[i % 2]:
                                    st.markdown(f"**{label}:** {val}")

                # Key Findings
                kf = extraction.get("key_findings", "")
                if kf:
                    st.markdown(f"""<div class="key-findings">
                        <strong>🔑 Key Findings</strong><br>{kf}
                    </div>""", unsafe_allow_html=True)
                    st.markdown("")

                # Abnormal Flags
                flags = extraction.get("abnormal_flags", [])
                if flags:
                    with st.expander(f"⚠️ Abnormal Findings ({len(flags)})", expanded=True):
                        for flag in flags:
                            st.markdown(f'<div class="abnormal-flag">⚠️ {flag}</div>',
                                        unsafe_allow_html=True)

                # Diagnoses
                diagnoses = extraction.get("diagnoses", [])
                if diagnoses:
                    with st.expander(f"🩺 Diagnoses ({len(diagnoses)})", expanded=True):
                        tags = "".join(
                            f'<span class="diagnosis-tag">{d}</span>' for d in diagnoses
                        )
                        st.markdown(tags, unsafe_allow_html=True)

                # Allergies
                allergies = extraction.get("allergies", [])
                if allergies:
                    with st.expander(f"🚫 Allergies ({len(allergies)})", expanded=False):
                        tags = "".join(
                            f'<span class="allergy-tag">⚠️ {a}</span>' for a in allergies
                        )
                        st.markdown(tags, unsafe_allow_html=True)

                # Lab Values
                labs = extraction.get("lab_values", [])
                if labs:
                    with st.expander(f"🧪 Lab Values ({len(labs)})", expanded=True):
                        for lab in labs:
                            status_badge = lab_status_html(lab.get("status", "UNKNOWN"))
                            interpretation = lab.get("interpretation", "")
                            ref = lab.get("normal_range", "N/A")
                            st.markdown(
                                f"**{lab.get('name', '?')}** — {lab.get('value', '?')} "
                                f"{status_badge} &nbsp; <small style='color:#888'>Ref: {ref}</small>",
                                unsafe_allow_html=True,
                            )
                            if interpretation:
                                st.caption(f"↳ {interpretation}")

                # Medications
                meds = extraction.get("medications", [])
                if meds:
                    with st.expander(f"💊 Medications ({len(meds)})", expanded=False):
                        for med in meds:
                            parts = [f"**{med.get('name', '?')}**"]
                            if med.get("dose"):
                                parts.append(med["dose"])
                            if med.get("frequency"):
                                parts.append(med["frequency"])
                            st.markdown(" · ".join(parts))
                            if med.get("indication"):
                                st.caption(f"↳ For: {med['indication']}")

                # Recommended Actions
                actions = extraction.get("recommended_actions", [])
                if actions:
                    with st.expander("✅ Questions to Discuss with Your Doctor", expanded=False):
                        for action in actions:
                            st.markdown(f"- {action}")

                st.markdown("---")
                st.markdown("""
                <div class="disclaimer">
                    ⚕️ This analysis is based solely on the text extracted from your uploaded documents.
                    It is not a medical diagnosis. Always discuss your results with your healthcare provider.
                </div>
                """, unsafe_allow_html=True)


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#999; font-size:0.8rem;">
    Built with LangGraph · FAISS · GPT-4o · FastAPI · Streamlit<br>
    <a href="https://github.com/santhakumarramesh" target="_blank" style="color:#1b6ca8;">GitHub</a> ·
    <a href="https://www.linkedin.com/in/santhakumar-ramesh/" target="_blank" style="color:#1b6ca8;">LinkedIn</a>
</div>
""", unsafe_allow_html=True)
