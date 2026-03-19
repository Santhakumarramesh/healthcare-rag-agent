# Healthcare AI Super-Agent

A multi-agent RAG system for healthcare Q&A with hybrid retrieval, self-correction, medical record analysis, and ML-based risk assessment.

**Live demo:** [healthcare-rag-ui.onrender.com](https://healthcare-rag-ui.onrender.com) · **API docs:** [healthcare-rag-api.onrender.com/docs](https://healthcare-rag-api.onrender.com/docs)

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.4-green)](https://github.com/langchain-ai/langgraph)
[![Tests](https://img.shields.io/badge/Tests-12%20passing-brightgreen)](tests/)
[![CI](https://github.com/Santhakumarramesh/healthcare-rag-agent/actions/workflows/test.yml/badge.svg)](https://github.com/Santhakumarramesh/healthcare-rag-agent/actions)

---

## What it does

A user asks a healthcare question. Five async agents run in sequence:

1. **Router** — classifies intent (FAQ / emergency / web search / follow-up), rewrites query for retrieval
2. **Retriever** — BM25 keyword + FAISS dense search fused with Reciprocal Rank Fusion, then cross-encoder reranked
3. **Web Search** — for recent queries (2024+ drug recalls, outbreaks), routes to Tavily live search instead of static knowledge base
4. **Responder** — generates grounded answer strictly from retrieved context
5. **Evaluator** — scores faithfulness + relevance + safety; if score < 0.7, injects corrective prompt and retries once (self-correction loop)

Every token streams to the UI in real time via Server-Sent Events.

---

## Features — what is implemented now

| Feature | Status |
|---------|--------|
| 4-agent async LangGraph pipeline with self-correction loop | ✅ |
| Hybrid BM25 + FAISS retrieval with RRF fusion | ✅ |
| Cross-encoder reranking (ms-marco-MiniLM) | ✅ |
| Token streaming via SSE (`/chat/stream`) | ✅ |
| Medical records upload + structured extraction (diagnoses, labs, meds) | ✅ |
| Grounded Q&A over uploaded records (session-scoped FAISS) | ✅ |
| ML + LLM patient risk assessment (9 clinical factors → GPT explanation) | ✅ |
| Per-query hallucination detection (embedding similarity) | ✅ |
| LRU response cache with TTL | ✅ |
| Sliding-window rate limiter | ✅ |
| Prometheus metrics (`/metrics`) | ✅ |
| GitHub Actions CI (pytest on every push) | ✅ |
| Docker + docker-compose full-stack deploy | ✅ |
| Render deploy (API) + Streamlit Cloud (UI) | ✅ |

## Optional integrations (require additional API keys)

| Feature | How to enable |
|---------|--------------|
| NVIDIA NIM (Llama-3.1-405B) | Set `NVIDIA_API_KEY` in `.env` |
| Tavily web search | Set `TAVILY_API_KEY` in `.env` |
| Pinecone cloud vector store | Set `PINECONE_API_KEY` in `.env` |
| AirLLM local privacy mode (Apple Silicon only) | `pip install airllm mlx mlx-lm`, set `LOCAL_MODE=true` |

## Roadmap

- [ ] Longitudinal health trend analysis (lab values across multiple records over time)
- [ ] Drug interaction cross-reference against DrugBank open data
- [ ] Streaming UI for risk assessment tab
- [ ] RAGAS batch evaluation pipeline with MLflow logging
- [ ] Fine-tuned cross-encoder for medical domain

---

## How to run locally

**Prerequisites:** Python 3.11, OpenAI API key

```bash
git clone https://github.com/Santhakumarramesh/healthcare-rag-agent
cd healthcare-rag-agent

python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Add your OPENAI_API_KEY to .env

python vectorstore/ingest.py    # build FAISS index (~30 seconds)
python run.py api               # start API on :8000  (terminal 1)
python run.py ui                # start UI on :8501   (terminal 2)
```

| Use case | Command |
|----------|---------|
| API only | `python run.py api` |
| UI only | `python run.py ui` |
| Full stack (Docker) | `docker-compose up --build` |
| Render deployment | `render.yaml` (auto-detected) |

**What happens when things are missing:**

| Situation | Behavior |
|-----------|----------|
| No `OPENAI_API_KEY` | Ingest falls back to `sentence-transformers` locally; LLM calls fail with 401 |
| No FAISS index | API runs ingest automatically on startup; logs warning if it fails |
| Ingest fails | API starts in degraded mode; retriever returns empty results |
| Pinecone not configured | Falls back to FAISS only; no error |

---

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│              4-Agent LangGraph Pipeline (async)              │
│                                                             │
│  Router → Retriever (BM25+FAISS+RRF+Rerank) → Responder    │
│                    ↗ Web Search (Tavily)                    │
│                                         ↓                   │
│                              Evaluator (quality gate)        │
│                              score<0.7 → retry Responder    │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
FastAPI (SSE streaming) ←→ Streamlit UI (4 tabs)
```

**Note on agent count:** The pipeline has 4 agent nodes (Router, Retriever/WebSearch, Responder, Evaluator). The self-correction is a conditional edge in the graph, not a separate agent node.

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check — includes `vector_store_ready` flag |
| `GET` | `/metrics` | Prometheus metrics |
| `GET` | `/stats` | Cache + rate limiter stats |
| `POST` | `/chat` | Full pipeline, returns complete JSON |
| `POST` | `/chat/stream` | SSE — token events + final metadata event |
| `POST` | `/reset` | Clear conversation history |
| `POST` | `/ingest/text` | Add text to shared knowledge base |
| `POST` | `/ingest/file` | Upload PDF/text to shared knowledge base |
| `POST` | `/records/upload` | Upload personal medical record (session-scoped) |
| `POST` | `/records/analyze` | Extract structured data from uploaded records |
| `POST` | `/records/query` | Ask questions about uploaded records |
| `DELETE` | `/records/clear/{session_id}` | Wipe session records |
| `POST` | `/risk/assess` | ML + LLM patient risk assessment |
| `GET` | `/risk/factors` | Risk factor schema for UI form |
| `GET` | `/local-model/status` | AirLLM local model status |
| `POST` | `/local-model/toggle` | Switch cloud ↔ on-device LLM |

Full interactive docs: `https://healthcare-rag-api.onrender.com/docs`

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| LLM orchestration | LangGraph 0.4 (async StateGraph) |
| Primary LLM | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small (prod) |
| Vector store | FAISS local + Pinecone cloud fallback |
| Keyword search | BM25 (rank-bm25) |
| Retrieval fusion | Reciprocal Rank Fusion (RRF) |
| Reranking | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| Web search | Tavily API (optional) |
| API | FastAPI + Uvicorn |
| Streaming | Server-Sent Events (SSE) |
| Frontend | Streamlit (4 tabs) |
| Monitoring | Prometheus metrics |
| Testing | pytest-asyncio, 12 tests |
| CI | GitHub Actions |
| Containerization | Docker + docker-compose |

---

## Project structure

```
healthcare-rag-agent/
├── agents/
│   ├── rag_pipeline.py       # 4-agent async LangGraph pipeline
│   ├── records_agent.py      # Medical record extraction + Q&A
│   └── risk_agent.py         # ML risk scoring + LLM explanation
├── api/
│   ├── main.py               # FastAPI — all endpoints
│   └── records.py            # Personal records router
├── vectorstore/
│   ├── retriever.py          # BM25 + FAISS + RRF + reranking
│   ├── ingest.py             # Document ingestion pipeline
│   └── personal_store.py     # Session-scoped in-memory FAISS
├── streamlit_app/
│   └── app.py                # Chat + Architecture + Risk + Records tabs
├── utils/
│   ├── config.py             # Centralized settings
│   ├── cache.py              # LRU response cache
│   ├── rate_limiter.py       # Sliding window rate limiter
│   ├── hallucination_detector.py
│   └── local_llm.py          # AirLLM wrapper (optional)
├── tests/
│   ├── test_config.py
│   └── test_intelligence.py  # 12 async agent tests
├── .github/workflows/        # CI
├── docker-compose.yml        # Full-stack local deploy
├── render.yaml               # Render deploy config
├── Procfile                  # Process definition
├── requirements.txt          # Production (Render — no torch)
├── requirements-local.txt    # Local dev (includes sentence-transformers, ragas)
└── requirements-ui.txt       # Streamlit Cloud (UI only — 3 packages)
```

---

## What I personally built

- Designed the multi-agent LangGraph state machine (router + conditional edges + retry loop)
- Implemented hybrid BM25 + FAISS retrieval with RRF fusion and cross-encoder reranking
- Built the session-scoped personal document store (in-memory FAISS per user session)
- Built the medical record extraction agent (structured JSON output with lab flagging)
- Implemented the ML risk scoring engine + LLM explanation pipeline
- Built all FastAPI endpoints including SSE streaming
- Built the Streamlit UI (4 tabs with live pipeline visualization)
- Configured CI, Docker, and Render deployment

---

## Limitations

- Personal document store is a singleton — breaks with multi-worker deployment (fine for free tier)
- Render free tier cold-starts after 15 min inactivity — first request ~30 seconds
- AirLLM privacy mode requires Apple Silicon Mac
- Risk assessment uses rule-based scoring, not a trained ML model — production would use XGBoost on outcome data
- NVIDIA NIM reranker and Tavily web search require separate API keys (commented out by default)

---

## Author

**Santhakumar Ramesh** — AI/ML Engineer @ DXC Technology | MS Data Science, University at Buffalo

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/santhakumar-ramesh/)
[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-green)](https://santhakumarramesh.github.io)
