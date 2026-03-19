"""
streamlit_app/app.py  —  MediAssist Healthcare Super-Agent UI
Tab 1: Ask MediAssist  — streaming chat with live agent pipeline visualization
Tab 2: My Medical Records — PDF upload, structured extraction, grounded Q&A
"""

import streamlit as st
import requests, json, time, os, uuid
from dotenv import load_dotenv
load_dotenv()

API_BASE  = os.getenv("API_BASE_URL", "http://localhost:8000")
APP_TITLE = "MediAssist — Healthcare Super-Agent"

st.set_page_config(page_title=APP_TITLE, page_icon="🏥", layout="wide",
                   initial_sidebar_state="expanded")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.main-header{background:linear-gradient(135deg,#0f4c75,#1b6ca8,#163d64);
  padding:1.5rem 2rem;border-radius:16px;margin-bottom:1.2rem;color:white;text-align:center;}
.main-header h1{font-size:2rem;font-weight:600;margin:0;}
.main-header p{opacity:.85;margin:.4rem 0 0;font-size:.95rem;}
.chat-msg-user{background:#e8f4fd;border-left:4px solid #1b6ca8;
  padding:.9rem 1.2rem;border-radius:10px;margin:.5rem 0;}
.chat-msg-ai{background:#f8fffe;border-left:4px solid #27ae60;
  padding:.9rem 1.2rem;border-radius:10px;margin:.5rem 0;}
/* Agent pipeline bar */
.pipeline-wrap{background:#f8f9fa;border:1px solid #e0e0e0;border-radius:12px;
  padding:.9rem 1.2rem;margin:.6rem 0;}
.pipeline-title{font-size:.78rem;font-weight:600;color:#666;
  text-transform:uppercase;letter-spacing:.06em;margin-bottom:.6rem;}
.agent-steps{display:flex;align-items:center;gap:0;flex-wrap:wrap;}
.agent-step{display:flex;align-items:center;gap:6px;padding:5px 12px;
  border-radius:20px;font-size:.78rem;font-weight:500;white-space:nowrap;}
.step-done{background:#d4edda;color:#155724;}
.step-active{background:#cce5ff;color:#004085;
  animation:pulse .9s ease-in-out infinite;}
.step-wait{background:#f1f3f5;color:#868e96;}
.step-arrow{color:#adb5bd;font-size:.9rem;padding:0 2px;}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.6}}
/* Retrieval panel */
.retrieval-panel{background:#fff8e1;border:1px solid #ffe082;border-radius:10px;
  padding:.8rem 1rem;margin:.5rem 0;font-size:.82rem;}
.retrieval-panel strong{color:#5d4037;}
.chunk-badge{display:inline-block;background:#e3f2fd;color:#1565c0;
  padding:2px 8px;border-radius:12px;font-size:.74rem;margin:2px;}
/* Score badges */
.badge{display:inline-block;padding:3px 10px;border-radius:14px;
  font-size:.78rem;font-weight:600;margin:2px;}
.badge-green{background:#d4edda;color:#155724;}
.badge-amber{background:#fff3cd;color:#856404;}
.badge-red{background:#f8d7da;color:#721c24;}
.badge-blue{background:#cce5ff;color:#004085;}
.badge-gray{background:#e9ecef;color:#495057;}
/* Stat cards */
.stat-card{background:white;padding:.8rem;border-radius:10px;
  border:1px solid #e0e0e0;text-align:center;}
.stat-num{font-size:1.6rem;font-weight:700;color:#1b6ca8;}
.stat-lbl{font-size:.75rem;color:#666;margin-top:.1rem;}
/* System architecture pill row */
.arch-row{display:flex;flex-wrap:wrap;gap:6px;margin:.5rem 0;}
.arch-pill{background:#e8f4fd;color:#0c447c;border:1px solid #b5d4f4;
  padding:3px 10px;border-radius:20px;font-size:.75rem;font-weight:500;}
/* Records */
.lab-NORMAL{background:#d4edda;color:#155724;padding:2px 7px;border-radius:5px;font-size:.75rem;font-weight:600;}
.lab-HIGH{background:#f8d7da;color:#721c24;padding:2px 7px;border-radius:5px;font-size:.75rem;font-weight:600;}
.lab-LOW{background:#cce5ff;color:#004085;padding:2px 7px;border-radius:5px;font-size:.75rem;font-weight:600;}
.lab-CRITICAL{background:#f5c6cb;color:#491217;padding:2px 7px;border-radius:5px;font-size:.75rem;font-weight:700;}
.lab-UNKNOWN{background:#e9ecef;color:#495057;padding:2px 7px;border-radius:5px;font-size:.75rem;}
.flag-box{background:#fff3cd;border-left:3px solid #f39c12;
  padding:.4rem .8rem;border-radius:5px;margin:.25rem 0;font-size:.83rem;color:#5d4037;}
.findings-box{background:#e8f4fd;border-left:4px solid #1b6ca8;
  padding:.7rem 1rem;border-radius:8px;font-size:.88rem;}
.disclaimer{background:#fff8e1;border:1px solid #ffe082;border-radius:8px;
  padding:.7rem 1rem;font-size:.8rem;color:#5d4037;}
.stButton>button{border-radius:10px;font-weight:500;
  background:linear-gradient(135deg,#1b6ca8,#0f4c75);
  color:white;border:none;padding:.5rem 1.4rem;}
</style>""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in [("messages",[]),("session_id",str(uuid.uuid4())),
              ("stats",{"q":0,"lat":0.0,"score":0.0}),
              ("rec_files",[]),("rec_extract",None),("rec_msgs",[])]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_health():
    try: return requests.get(f"{API_BASE}/health", timeout=4).json()
    except: return {"status":"unreachable","pipeline_loaded":False}

def badge(text, kind="gray"):
    return f'<span class="badge badge-{kind}">{text}</span>'

def intent_badge(intent):
    mapping = {"medical_faq":("🩺 Medical FAQ","green"),
               "emergency":("🚨 Emergency","red"),
               "web_search":("🌐 Web Search","blue"),
               "greeting":("👋 Greeting","gray"),
               "out_of_scope":("🚫 Out of Scope","amber")}
    label, kind = mapping.get(intent, (f"🤖 {intent}","gray"))
    return badge(label, kind)

def hall_badge(risk):
    if risk == "low":   return badge("✅ Low hallucination risk","green")
    if risk == "high":  return badge("❌ High hallucination risk","red")
    return badge("⚠️ Medium hallucination risk","amber")

def lab_html(status):
    s = (status or "UNKNOWN").upper()
    icons = {"NORMAL":"✅","HIGH":"🔴","LOW":"🔵","CRITICAL":"🚨"}
    return f'<span class="lab-{s}">{icons.get(s,"❓")} {s}</span>'


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 MediAssist")
    health = get_health()
    ok = health.get("status") == "healthy"
    st.markdown(f"**API:** {'🟢 Healthy' if ok else '🔴 Unreachable'} &nbsp;·&nbsp; "
                f"**Model:** `{health.get('model','—')}`")
    st.markdown("---")

    s = st.session_state.stats
    c1,c2,c3 = st.columns(3)
    with c1: st.markdown(f'<div class="stat-card"><div class="stat-num">{s["q"]}</div>'
                         f'<div class="stat-lbl">Queries</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="stat-card"><div class="stat-num">{s["lat"]:.0f}ms</div>'
                         f'<div class="stat-lbl">Avg latency</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="stat-card"><div class="stat-num">{s["score"]:.2f}</div>'
                         f'<div class="stat-lbl">Avg quality</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🏗️ System Architecture")
    st.markdown("""<div class="arch-row">
      <span class="arch-pill">LangGraph 0.4</span>
      <span class="arch-pill">BM25 + FAISS RRF</span>
      <span class="arch-pill">Cross-encoder rerank</span>
      <span class="arch-pill">SSE streaming</span>
      <span class="arch-pill">Self-correction loop</span>
      <span class="arch-pill">Hallucination detector</span>
      <span class="arch-pill">Rate limiter</span>
      <span class="arch-pill">Response cache</span>
      <span class="arch-pill">Prometheus metrics</span>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💡 Try These")
    for q in ["What are symptoms of Type 2 diabetes?",
               "How does ibuprofen work?",
               "What foods to avoid with high blood pressure?",
               "Side effects of statins?"]:
        if st.button(q, key=f"s_{q[:15]}", use_container_width=True):
            st.session_state.prefill = q
            st.rerun()

    st.markdown("---")
    st.markdown("### 📄 Add to Knowledge Base")
    itxt = st.text_area("Paste medical text:", height=80, key="ingest_txt")
    isrc = st.text_input("Source name:", value="custom", key="ingest_src")
    if st.button("➕ Ingest", use_container_width=True):
        if itxt.strip():
            r = requests.post(f"{API_BASE}/ingest/text",
                              json={"text":itxt,"source_name":isrc}, timeout=30)
            st.success(f"✅ {r.json().get('chunks_stored',0)} chunks added") if r.ok else st.error("Failed")
        else:
            st.warning("Enter text first")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""<div class="main-header">
  <h1>🏥 MediAssist — Healthcare Super-Agent</h1>
  <p>5-Agent LangGraph Pipeline · BM25+FAISS Hybrid Retrieval · Self-Correction Loop · Real-Time Streaming</p>
</div>""", unsafe_allow_html=True)

# Architecture always visible at top
st.markdown("""<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:1rem;align-items:center;">
  <span style="font-size:.78rem;font-weight:600;color:#666;margin-right:4px;">PIPELINE:</span>
  <span class="arch-pill">1️⃣ Router</span>
  <span style="color:#adb5bd">→</span>
  <span class="arch-pill">2️⃣ Retriever (BM25+FAISS+RRF)</span>
  <span style="color:#adb5bd">→</span>
  <span class="arch-pill">3️⃣ Web Search (Tavily)</span>
  <span style="color:#adb5bd">→</span>
  <span class="arch-pill">4️⃣ Responder</span>
  <span style="color:#adb5bd">→</span>
  <span class="arch-pill">5️⃣ Evaluator (self-correct if &lt;0.7)</span>
</div>""", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_chat, tab_arch, tab_risk, tab_records = st.tabs(
    ["💬 Ask MediAssist", "🔬 How It Works", "📊 Risk Assessment", "📋 My Medical Records"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Chat with live agent pipeline visualization
# ══════════════════════════════════════════════════════════════════════════════
with tab_chat:
    st.markdown('<div class="disclaimer">⚕️ <strong>Disclaimer:</strong> General health information only. '
                'Always consult a qualified healthcare provider.</div>', unsafe_allow_html=True)
    st.markdown("")

    # Chat history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-msg-user"><strong>You</strong><br>{msg["content"]}</div>',
                        unsafe_allow_html=True)
        else:
            # Main response
            st.markdown(f'<div class="chat-msg-ai"><strong>🤖 MediAssist</strong><br><br>'
                        f'{msg["content"]}</div>', unsafe_allow_html=True)

            # Always-visible agent pipeline result
            meta = msg.get("meta", {})
            intent     = meta.get("intent", "")
            q_score    = meta.get("quality_score", 0.0)
            hall_risk  = meta.get("hallucination_risk", "unknown")
            latency    = meta.get("latency_ms", 0)
            agent_trace = meta.get("agent_trace", [])
            sources    = meta.get("retrieved_chunks", [])
            retried    = any("RETRY" in t for t in agent_trace)

            st.markdown(f"""<div class="pipeline-wrap">
  <div class="pipeline-title">Agent pipeline result</div>
  <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:.5rem;">
    {intent_badge(intent)}
    {badge(f"Quality: {q_score:.2f}", "green" if q_score>=.8 else "amber" if q_score>=.6 else "red")}
    {hall_badge(hall_risk)}
    {badge(f"⏱ {latency:.0f}ms","gray")}
    {badge("🔁 Self-corrected","blue") if retried else ""}
  </div>""", unsafe_allow_html=True)

            # Retrieval details
            if sources:
                chunk_html = "".join(
                    f'<span class="chunk-badge">📄 {(s.get("source","") or s.get("metadata",{}).get("source","chunk") if isinstance(s,dict) else str(s)).split("/")[-1][:25]} '
                    f'({s.get("score",0):.2f})</span>'
                    for s in sources[:5]
                )
                st.markdown(
                    f'<div class="retrieval-panel"><strong>📚 Retrieval:</strong> '
                    f'BM25+FAISS→RRF fusion→cross-encoder rerank · {len(sources)} chunks<br>'
                    f'{chunk_html}</div>', unsafe_allow_html=True)

            # Agent trace steps
            if agent_trace:
                steps_html = " → ".join(
                    f'<span style="font-family:monospace;font-size:.76rem;color:#444;">{t}</span>'
                    for t in agent_trace)
                st.markdown(f'<details><summary style="font-size:.78rem;color:#666;cursor:pointer;">'
                            f'🔍 Full agent trace ({len(agent_trace)} steps)</summary>'
                            f'<div style="background:#f8f9fa;padding:.6rem;border-radius:6px;'
                            f'margin-top:.4rem;font-size:.76rem;line-height:1.8;">'
                            f'{steps_html}</div></details>', unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    prefill = st.session_state.pop("prefill", "")
    c1, c2 = st.columns([5,1])
    with c1:
        user_query = st.text_input("Ask a healthcare question:", value=prefill,
                                   placeholder="e.g. What are symptoms of diabetes?",
                                   label_visibility="collapsed", key="q_input")
    with c2:
        send = st.button("Ask 🔍", use_container_width=True)

    if (send or user_query) and user_query.strip():
        q = user_query.strip()
        st.session_state.messages.append({"role":"user","content":q})

        # Show live pipeline steps while streaming
        pipeline_placeholder = st.empty()
        steps = [("Router","🔀"),("Retriever","📚"),("Responder","💬"),("Evaluator","✅")]
        active_idx = [0]

        def render_pipeline(done_up_to: int, active: int):
            html = '<div class="pipeline-wrap"><div class="pipeline-title">Running agent pipeline…</div>' \
                   '<div class="agent-steps">'
            for i,(name,icon) in enumerate(steps):
                if i < done_up_to:
                    cls = "step-done"; lbl = f"✓ {icon} {name}"
                elif i == active:
                    cls = "step-active"; lbl = f"⟳ {icon} {name}"
                else:
                    cls = "step-wait";   lbl = f"{icon} {name}"
                html += f'<span class="agent-step {cls}">{lbl}</span>'
                if i < len(steps)-1:
                    html += '<span class="step-arrow">›</span>'
            html += '</div></div>'
            pipeline_placeholder.markdown(html, unsafe_allow_html=True)

        render_pipeline(0, 0)

        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()
            full_response = ""
            meta_out = {}
            start = time.time()

            try:
                with requests.post(f"{API_BASE}/chat/stream",
                                   json={"query":q}, stream=True, timeout=90) as r:
                    for line in r.iter_lines():
                        if not line: continue
                        decoded = line.decode("utf-8")
                        if not decoded.startswith("data: "): continue
                        try:
                            data = json.loads(decoded[6:])
                            if data.get("type") == "token":
                                full_response += data.get("content","")
                                placeholder.markdown(full_response + "▌")
                                # Advance pipeline indicator based on response length
                                if len(full_response) > 20:
                                    render_pipeline(2, 3)
                                elif len(full_response) > 5:
                                    render_pipeline(1, 2)
                            elif data.get("type") == "metadata":
                                meta_out = data.get("content", {})
                                render_pipeline(4, 4)
                                placeholder.markdown(full_response)
                        except json.JSONDecodeError:
                            pass

            except Exception as e:
                placeholder.error(f"Connection error: {e}")

            lat = (time.time()-start)*1000
            meta_out["latency_ms"] = lat

            # Update session stats
            n = st.session_state.stats["q"] + 1
            qs = meta_out.get("quality_score", 0.0)
            st.session_state.stats = {
                "q": n,
                "lat": round((st.session_state.stats["lat"]*(n-1)+lat)/n),
                "score": round((st.session_state.stats["score"]*(n-1)+qs)/n, 2),
            }

            st.session_state.messages.append({
                "role":"assistant","content":full_response,"meta":meta_out})
            pipeline_placeholder.empty()
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — How It Works (architecture explainer)
# ══════════════════════════════════════════════════════════════════════════════
with tab_arch:
    st.markdown("### 🏗️ System Architecture")
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("""
**Multi-agent LangGraph pipeline**

Every query passes through 5 specialized async agents:

| Agent | Role |
|-------|------|
| 🔀 Router | Classifies intent (FAQ / emergency / web search / follow-up), rewrites query for retrieval |
| 📚 Retriever | BM25 keyword + FAISS dense search → RRF fusion → cross-encoder rerank |
| 🌐 Web Search | Routes 2024+ queries to Tavily live search instead of static knowledge base |
| 💬 Responder | Generates grounded response strictly from retrieved context |
| ✅ Evaluator | Scores faithfulness + relevance + safety; triggers self-correction if score < 0.7 |
""")
    with c2:
        st.markdown("""
**What makes this different from a basic RAG chatbot**

| Feature | Basic RAG | This System |
|---------|-----------|-------------|
| Retrieval | Vector only | BM25 + Dense + RRF |
| Reranking | None | Cross-encoder |
| Routing | Single path | 5 intent types |
| Quality | No check | Evaluator + retry |
| Hallucination | No detection | Embedding-based check |
| Web search | No | Tavily real-time |
| Privacy mode | No | AirLLM on-device |
| Monitoring | No | Prometheus metrics |
| Rate limiting | No | Sliding window |
| Response cache | No | LRU with TTL |
""")

    st.markdown("---")
    st.markdown("### 📊 Key Technical Decisions")
    st.markdown("""
**Why BM25 + FAISS + RRF?**
Dense vector search misses exact medical terminology — drug names, ICD codes, specific dosages.
BM25 catches these exact matches. RRF mathematically merges both ranked lists, consistently
outperforming either retriever alone.

**Why a self-correction loop?**
Healthcare answers that are vague, off-topic, or not grounded in the retrieved context get caught
by the Evaluator agent before reaching the user. If quality < 0.7, the Evaluator injects a
corrective prompt and the Responder retries once. This doubles quality control cost but
meaningfully reduces low-quality responses in testing.

**Why SSE streaming instead of polling?**
Every token streams to the UI via Server-Sent Events as soon as it's generated. The user sees
the response building word-by-word rather than waiting 3-5 seconds for a complete response.
This is critical for perceived responsiveness in a healthcare context.

**Why a dedicated Medical Records tab?**
Users can upload their own lab reports, discharge summaries, or doctor's notes. The system
extracts structured information (diagnoses, lab values with normal/abnormal flags, medications,
allergies) and then answers questions grounded strictly in those documents — not in general
knowledge. This is the feature that separates this from a generic healthcare chatbot.
""")

    st.markdown("---")
    st.markdown("### 🔗 Live Endpoints")
    st.code("""
POST /chat               → full pipeline, returns complete JSON
POST /chat/stream        → SSE streaming — token events + final metadata
POST /ingest/text        → add text to shared knowledge base
POST /ingest/file        → upload PDF/text to shared knowledge base
POST /records/upload     → upload personal medical record (session-scoped)
POST /records/analyze    → extract structured data from uploaded records
POST /records/query      → ask questions about uploaded records
GET  /health             → health check
GET  /metrics            → Prometheus metrics
GET  /stats              → cache + rate limiter stats
POST /local-model/toggle → switch between cloud and on-device LLM
""")
    st.markdown(f"Full interactive API docs: [{API_BASE}/docs]({API_BASE}/docs)")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Risk Assessment (ML + LLM)
# ══════════════════════════════════════════════════════════════════════════════
with tab_risk:
    st.markdown("### 📊 Patient Risk Assessment")
    st.markdown(
        "Enter patient metrics to get an ML-based risk score with LLM-generated explanation. "
        "Combines clinical scoring with GPT-4o-mini reasoning."
    )
    st.markdown('<div class="disclaimer">⚕️ <strong>Not a medical device.</strong> '
                'For informational purposes only. Always consult a healthcare provider.</div>',
                unsafe_allow_html=True)
    st.markdown("")

    col_form, col_result = st.columns([1, 1], gap="large")

    with col_form:
        st.markdown("#### Patient Metrics")
        age      = st.slider("Age (years)",             18, 100, 45)
        bmi      = st.slider("BMI",                     15.0, 50.0, 25.0, 0.5)
        sbp      = st.slider("Systolic BP (mmHg)",      80, 220, 120)
        glucose  = st.slider("Fasting glucose (mg/dL)", 50, 400, 95)
        hba1c    = st.slider("HbA1c (%)",               4.0, 15.0, 5.5, 0.1)
        chol     = st.slider("Total cholesterol (mg/dL)", 100, 400, 180)

        st.markdown("#### Lifestyle Factors")
        smoking  = st.radio("Smoking status", [0, 1],
                             format_func=lambda x: "Non-smoker" if x==0 else "Smoker",
                             horizontal=True)
        fam_hist = st.radio("Family history of diabetes", [0, 1],
                             format_func=lambda x: "No" if x==0 else "Yes",
                             horizontal=True)
        activity = st.radio("Physical activity level", [0, 1, 2],
                             format_func=lambda x: ["Low","Moderate","High"][x],
                             horizontal=True)

        assess_btn = st.button("🔬 Run Risk Assessment", use_container_width=True, type="primary")

    with col_result:
        if assess_btn:
            payload = {"age":age,"bmi":bmi,"systolic_bp":sbp,"glucose":glucose,
                       "hba1c":hba1c,"cholesterol":chol,"smoking":smoking,
                       "family_history":fam_hist,"physical_activity":activity}
            with st.spinner("Running ML scoring + LLM explanation…"):
                try:
                    r = requests.post(f"{API_BASE}/risk/assess", json=payload, timeout=30)
                    if r.ok:
                        res = r.json()
                        prob   = res["probability"]
                        level  = res["risk_level"]
                        color_map = {"Low":"#155724","Moderate":"#856404",
                                     "High":"#a04000","Very High":"#721c24"}
                        bg_map    = {"Low":"#d4edda","Moderate":"#fff3cd",
                                     "High":"#ffe5d0","Very High":"#f8d7da"}
                        col = color_map.get(level,"#333")
                        bg  = bg_map.get(level,"#f8f9fa")

                        # Big risk gauge
                        st.markdown(f"""
<div style="background:{bg};border-radius:12px;padding:1.2rem 1.5rem;text-align:center;margin-bottom:1rem;">
  <div style="font-size:2.8rem;font-weight:700;color:{col};">{prob:.0%}</div>
  <div style="font-size:1.1rem;font-weight:600;color:{col};">{level} Risk</div>
  <div style="font-size:.85rem;color:{col};margin-top:.3rem;">{res['risk_summary']}</div>
</div>""", unsafe_allow_html=True)

                        # Top contributing factors
                        st.markdown("**Top contributing factors:**")
                        factors = res.get("top_factors", [])
                        max_pts = factors[0]["points"] if factors else 1
                        for f in factors[:5]:
                            pct = f["points"] / max_pts if max_pts > 0 else 0
                            bar = "█" * int(pct * 10) + "░" * (10 - int(pct * 10))
                            st.markdown(
                                f"`{bar}` **{f['factor']}** — {f['points']} pts"
                            )

                        # LLM explanation
                        st.markdown("---")
                        st.markdown("**Clinical explanation:**")
                        st.markdown(
                            f'<div class="chat-msg-ai">{res["explanation"]}</div>',
                            unsafe_allow_html=True)
                    else:
                        st.error(f"Assessment failed: {r.json().get('detail', r.text)}")
                except Exception as e:
                    st.error(f"Connection error: {e}")
        else:
            st.markdown("#### How This Works")
            st.markdown("""
This combines **two AI techniques** in one pipeline:

**1 — Clinical risk scoring (ML layer)**
Implements a Findrisc-inspired algorithm that scores 9 patient factors
and converts them to a diabetes/cardiovascular risk probability.
In a production system, this would be replaced by a trained XGBoost
model on patient outcome data.

**2 — LLM explanation (GenAI layer)**
The risk score and top contributing factors are passed to GPT-4o-mini
which generates a plain-English explanation and actionable recommendations
personalized to the patient's specific risk profile.

**Why this matters for interviews:**
Most candidates do pure RAG or pure ML. Combining both in one pipeline
is rare and directly maps to how real clinical decision support systems work.
""")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — My Medical Records  (was tab_records)
# ══════════════════════════════════════════════════════════════════════════════
with tab_records:
    sid = st.session_state.session_id
    st.markdown('<div class="disclaimer">🔒 <strong>Privacy:</strong> Records are processed in-memory '
                'for this session only and never saved to disk.</div>', unsafe_allow_html=True)
    st.markdown("")

    left, right = st.columns([1,1], gap="large")

    with left:
        st.markdown("### 📤 Upload Your Records")
        uploaded = st.file_uploader("", type=["pdf","txt"], accept_multiple_files=True,
                                    label_visibility="collapsed", key="rec_up")
        if uploaded:
            for uf in [f for f in uploaded if f.name not in st.session_state.rec_files]:
                with st.spinner(f"Indexing {uf.name}…"):
                    r = requests.post(f"{API_BASE}/records/upload",
                                      data={"session_id":sid},
                                      files={"file":(uf.name,uf.getvalue(),
                                                      uf.type or "application/octet-stream")},
                                      timeout=60)
                    if r.ok:
                        st.session_state.rec_files.append(uf.name)
                        st.success(f"✅ {uf.name} — {r.json().get('chunks_stored',0)} chunks indexed")
                    else:
                        st.error(f"❌ {uf.name}: {r.json().get('detail',r.text)}")

        if st.session_state.rec_files:
            for f in st.session_state.rec_files:
                st.markdown(f"• 📄 `{f}`")
            bc1,bc2 = st.columns(2)
            with bc1:
                analyze = st.button("🔬 Analyze Records", use_container_width=True, type="primary")
            with bc2:
                if st.button("🗑️ Clear Records", use_container_width=True):
                    try: requests.delete(f"{API_BASE}/records/clear/{sid}", timeout=10)
                    except: pass
                    st.session_state.rec_files=[]
                    st.session_state.rec_extract=None
                    st.session_state.rec_msgs=[]
                    st.rerun()
            if analyze:
                with st.spinner("Analyzing… 10-20 seconds…"):
                    r = requests.post(f"{API_BASE}/records/analyze",
                                      data={"session_id":sid}, timeout=90)
                    if r.ok:
                        st.session_state.rec_extract = r.json()
                        st.success("✅ Analysis complete →")
                    else:
                        st.error(r.json().get("detail","Analysis failed"))
        else:
            st.info("Upload a PDF or .txt file to begin. Supports lab results, "
                    "discharge summaries, doctor's notes, prescription lists.")

        if st.session_state.rec_files:
            st.markdown("---")
            st.markdown("### 💬 Ask About Your Records")
            for rm in st.session_state.rec_msgs:
                if rm["role"]=="user":
                    st.markdown(f'<div class="chat-msg-user"><strong>You</strong><br>'
                                f'{rm["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-msg-ai">{rm["content"]}</div>',
                                unsafe_allow_html=True)
            rq = st.text_input("Question about your records:",
                               placeholder="e.g. What was my HbA1c? Are any labs abnormal?",
                               label_visibility="collapsed", key="rec_q")
            if st.button("Ask 🔍", key="rec_ask"):
                if rq.strip():
                    st.session_state.rec_msgs.append({"role":"user","content":rq})
                    with st.spinner("Searching your records…"):
                        r = requests.post(f"{API_BASE}/records/query",
                                          json={"session_id":sid,"question":rq}, timeout=60)
                        if r.ok:
                            d = r.json()
                            st.session_state.rec_msgs.append({
                                "role":"assistant","content":d["answer"],
                                "sources":d.get("sources",[])})
                        else:
                            st.error(r.json().get("detail","Query failed"))
                    st.rerun()

    with right:
        ex = st.session_state.rec_extract
        if not ex:
            st.markdown("### 📊 Analysis Results")
            st.markdown("Upload records and click **Analyze Records** to see structured extraction here.\n\n"
                        "You'll get: diagnoses, lab values (color-coded normal/abnormal), "
                        "medications, allergies, key findings, and recommended questions for your doctor.")
        else:
            st.markdown("### 📊 Analysis Results")
            pi = ex.get("patient_info",{})
            if any(v and v!="Not specified" for v in pi.values()):
                with st.expander("👤 Patient Information", expanded=True):
                    for label,key in [("Name","name"),("DOB","dob"),
                                      ("Record Date","record_date"),("Provider","provider")]:
                        v = pi.get(key,"")
                        if v and v!="Not specified":
                            st.markdown(f"**{label}:** {v}")
            kf = ex.get("key_findings","")
            if kf:
                st.markdown(f'<div class="findings-box"><strong>🔑 Key Findings</strong><br>{kf}</div>',
                            unsafe_allow_html=True)
                st.markdown("")
            flags = ex.get("abnormal_flags",[])
            if flags:
                with st.expander(f"⚠️ Abnormal Findings ({len(flags)})", expanded=True):
                    for f in flags:
                        st.markdown(f'<div class="flag-box">⚠️ {f}</div>', unsafe_allow_html=True)
            if diag := ex.get("diagnoses",[]):
                with st.expander(f"🩺 Diagnoses ({len(diag)})", expanded=True):
                    st.markdown(" ".join(
                        f'<span style="display:inline-block;background:#e8f5e9;color:#1b5e20;'
                        f'padding:3px 10px;border-radius:14px;font-size:.8rem;margin:2px;'
                        f'border:1px solid #a5d6a7;">{d}</span>' for d in diag),
                        unsafe_allow_html=True)
            if labs := ex.get("lab_values",[]):
                with st.expander(f"🧪 Lab Values ({len(labs)})", expanded=True):
                    for lab in labs:
                        st.markdown(
                            f"**{lab.get('name','?')}** — {lab.get('value','?')} "
                            f"{lab_html(lab.get('status','UNKNOWN'))} "
                            f"<small style='color:#888'>Ref: {lab.get('normal_range','N/A')}</small>",
                            unsafe_allow_html=True)
                        if lab.get("interpretation"):
                            st.caption(f"↳ {lab['interpretation']}")
            if meds := ex.get("medications",[]):
                with st.expander(f"💊 Medications ({len(meds)})", expanded=False):
                    for m in meds:
                        parts = [f"**{m.get('name','?')}**"]
                        if m.get("dose"): parts.append(m["dose"])
                        if m.get("frequency"): parts.append(m["frequency"])
                        st.markdown(" · ".join(parts))
                        if m.get("indication"): st.caption(f"↳ For: {m['indication']}")
            if acts := ex.get("recommended_actions",[]):
                with st.expander("✅ Questions for Your Doctor", expanded=False):
                    for a in acts: st.markdown(f"- {a}")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""<div style="text-align:center;color:#999;font-size:.78rem;">
  MediAssist · LangGraph · BM25+FAISS+RRF · GPT-4o · FastAPI · Streamlit ·
  <a href="https://github.com/santhakumarramesh/healthcare-rag-agent" style="color:#1b6ca8;">GitHub</a> ·
  <a href="https://healthcare-rag-api.onrender.com/docs" style="color:#1b6ca8;">API Docs</a> ·
  <a href="https://www.linkedin.com/in/santhakumar-ramesh/" style="color:#1b6ca8;">LinkedIn</a>
</div>""", unsafe_allow_html=True)
