"""
streamlit_app/app.py
--------------------
Production-grade Streamlit UI for the Healthcare RAG Agent.
Features:
  - Clean chat interface with message history
  - Real-time streaming response display
  - Source document viewer
  - Eval score badge
  - Document ingestion sidebar
  - Agent trace visualization
"""

import streamlit as st
import requests
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── Config ─────────────────────────────────────────────────────────────────────
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
APP_TITLE = "MediAssist — Healthcare FAQ Agent"
APP_ICON  = "🏥"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #0f4c75 0%, #1b6ca8 50%, #163d64 100%);
        padding: 2rem; border-radius: 16px; margin-bottom: 2rem;
        color: white; text-align: center;
    }
    .main-header h1 { font-size: 2.2rem; font-weight: 600; margin: 0; }
    .main-header p  { opacity: 0.85; margin: 0.5rem 0 0 0; font-size: 1rem; }

    .chat-message {
        padding: 1rem 1.2rem; border-radius: 12px;
        margin: 0.6rem 0; animation: fadeIn 0.3s ease;
    }
    .chat-message.user {
        background: #e8f4fd; border-left: 4px solid #1b6ca8; margin-left: 2rem;
    }
    .chat-message.assistant {
        background: #f8fffe; border-left: 4px solid #27ae60; margin-right: 2rem;
    }
    .chat-message.assistant.warning {
        background: #fff8e1; border-left: 4px solid #f39c12;
    }

    .source-badge {
        display: inline-block; background: #e3f2fd; color: #1565c0;
        padding: 2px 10px; border-radius: 20px; font-size: 0.75rem;
        margin: 2px; font-weight: 500;
    }
    .score-badge {
        display: inline-block; padding: 3px 12px; border-radius: 20px;
        font-size: 0.8rem; font-weight: 600;
    }
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

    @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

    .stTextInput > div > div > input { border-radius: 10px; border: 2px solid #e0e0e0; }
    .stButton > button {
        border-radius: 10px; font-weight: 500;
        background: linear-gradient(135deg, #1b6ca8, #0f4c75);
        color: white; border: none; padding: 0.6rem 1.5rem;
    }
    .disclaimer {
        background: #fff8e1; border: 1px solid #ffe082; border-radius: 8px;
        padding: 0.8rem 1rem; font-size: 0.82rem; color: #5d4037;
    }
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())
if "stats" not in st.session_state:
    st.session_state.stats = {"total_queries": 0, "avg_latency": 0.0, "avg_score": 0.0}


# ── Helpers ───────────────────────────────────────────────────────────────────

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


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🏥 MediAssist")
    st.markdown("**Healthcare FAQ Agent**")
    st.markdown("---")

    # Health check
    health = get_health()
    status_color = "🟢" if health.get("status") == "healthy" else "🔴"
    st.markdown(f"**API Status:** {status_color} {health.get('status', 'unknown').title()}")
    vs_ready = health.get("vector_store_ready", False)
    st.markdown(f"**Knowledge Base:** {'✅ Ready' if vs_ready else '⚠️ Empty'}")
    st.markdown("---")

    # Stats
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

    # Document ingestion
    st.markdown("### 📄 Add to Knowledge Base")
    ingest_text = st.text_area("Paste medical text:", height=120, placeholder="Paste medical guidelines, FAQs, or any healthcare content...")
    ingest_source = st.text_input("Source name:", value="custom_document")
    if st.button("➕ Ingest Document", use_container_width=True):
        if ingest_text.strip():
            with st.spinner("Ingesting..."):
                resp = requests.post(
                    f"{API_BASE}/ingest/text",
                    json={"text": ingest_text, "source_name": ingest_source},
                    timeout=30
                )
                if resp.status_code == 200:
                    data = resp.json()
                    st.success(f"✅ Ingested {data['chunks_stored']} chunks!")
                else:
                    st.error("Ingestion failed. Is the API running?")
        else:
            st.warning("Please enter some text to ingest.")

    st.markdown("---")

    # Sample questions
    st.markdown("### 💡 Sample Questions")
    sample_questions = [
        "What are symptoms of Type 2 diabetes?",
        "How does ibuprofen work?",
        "What foods should I avoid with high blood pressure?",
        "What is a normal BMI range?",
        "What are the side effects of statins?",
    ]
    for q in sample_questions:
        if st.button(q, key=f"sample_{q[:20]}", use_container_width=True):
            st.session_state.prefill_query = q
            st.rerun()

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ── Main Content ──────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="main-header">
    <h1>🏥 MediAssist</h1>
    <p>AI-Powered Healthcare FAQ Assistant · Multi-Agent RAG · LangGraph + GPT-4o</p>
</div>
""", unsafe_allow_html=True)

# Disclaimer
st.markdown("""
<div class="disclaimer">
    ⚕️ <strong>Medical Disclaimer:</strong> MediAssist provides general health information only.
    It is not a substitute for professional medical advice, diagnosis, or treatment.
    Always consult a qualified healthcare provider for personal medical decisions.
</div>
""", unsafe_allow_html=True)

st.markdown("")

# Chat history
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    css_class = "user" if role == "user" else "assistant"

    if role == "user":
        st.markdown(f"""<div class="chat-message user">
            <strong>You</strong><br>{content}
        </div>""", unsafe_allow_html=True)
    else:
        badge = score_badge(msg.get("eval_score"))
        intent_icon = intent_emoji(msg.get("intent", ""))
        sources_html = ""
        for src in msg.get("sources", []):
            short = src.split("/")[-1][:30]
            sources_html += f'<span class="source-badge">📄 {short}</span>'

        st.markdown(f"""<div class="chat-message assistant">
            <strong>MediAssist</strong> {intent_icon} {badge}<br><br>
            {content}
            {'<br><br><strong>Sources:</strong> ' + sources_html if sources_html else ''}
        </div>""", unsafe_allow_html=True)

        # Agent trace expander
        if msg.get("show_trace"):
            with st.expander("🔍 Agent Trace", expanded=False):
                st.markdown(f"""<div class="agent-trace">
                🔀 Router → Intent: <b>{msg.get('intent')}</b><br>
                📚 Retriever → Sources: {len(msg.get('sources', []))} found<br>
                💬 Responder → {len(content)} chars generated<br>
                ✅ Evaluator → Score: {msg.get('eval_score', 'N/A')} | {msg.get('eval_feedback', '')}
                </div>""", unsafe_allow_html=True)


# ── Query Input ───────────────────────────────────────────────────────────────

st.markdown("---")

# Handle pre-filled query from sample buttons
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

# ── Handle Query ──────────────────────────────────────────────────────────────

if (send_clicked or user_query) and user_query.strip():
    query = user_query.strip()

    # Add user message
    st.session_state.messages.append({"role": "user", "content": query})

    # Call Streaming API
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_response = ""
        
        try:
            with requests.post(f"{API_BASE}/chat/stream", json={"query": query}, stream=True) as r:
                for line in r.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith("data: "):
                            try:
                                data = json.loads(decoded_line[6:])
                                if data.get("type") == "token":
                                    token = data.get("content", "")
                                    full_response += token
                                    placeholder.markdown(full_response + "▌")
                                elif data.get("type") == "metadata":
                                    # We found the final metadata event!
                                    metadata = data.get("content", {})
                                    st.session_state.messages.append({
                                        "role": "assistant",
                                        "content": full_response,
                                        "intent": metadata.get("intent", "medical_faq"),
                                        "sources": metadata.get("retrieved_chunks", []),
                                        "quality_score": metadata.get("quality_score", 0.0),
                                        "hallucination_risk": metadata.get("hallucination_risk", "unknown"),
                                        "agent_trace": metadata.get("agent_trace", []),
                                        "show_trace": show_trace
                                    })
                                    st.session_state.stats["total_queries"] += 1
                                    placeholder.markdown(full_response)
                                    st.rerun() # Rerun to update chat history and stats
                            except json.JSONDecodeError:
                                pass
            
        except Exception as e:
            st.error(f"Connection error: {e}")


# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#999; font-size:0.8rem;">
    Built with LangGraph · FAISS · Pinecone · GPT-4o · FastAPI · Streamlit<br>
    <a href="https://github.com/santhakumarramesh" target="_blank" style="color:#1b6ca8;">GitHub</a> ·
    <a href="https://www.linkedin.com/in/santhakumar-ramesh/" target="_blank" style="color:#1b6ca8;">LinkedIn</a>
</div>
""", unsafe_allow_html=True)
