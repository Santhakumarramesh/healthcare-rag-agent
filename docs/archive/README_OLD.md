# Healthcare RAG Multi-Agent System

Production-style healthcare question answering and document analysis system built with FastAPI, Streamlit, retrieval-augmented generation, streaming responses, and agent-based validation.

**Live demo:** [healthcare-rag-ui.onrender.com](https://healthcare-rag-ui.onrender.com) · **API docs:** [healthcare-rag-api.onrender.com/docs](https://healthcare-rag-api.onrender.com/docs)

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.4-green)](https://github.com/langchain-ai/langgraph)
[![Tests](https://img.shields.io/badge/Tests-12%20passing-brightgreen)](tests/)
[![CI](https://github.com/Santhakumarramesh/healthcare-rag-agent/actions/workflows/test.yml/badge.svg)](https://github.com/Santhakumarramesh/healthcare-rag-agent/actions)

---

## 📸 Screenshots

### Main Chat Interface with Live Agent Pipeline
![Main Interface](docs/screenshots/main-interface.png)
*Real-time agent execution visualization with confidence scores, quality metrics, and hallucination detection*

### Medical Records Analysis
![Medical Records](docs/screenshots/medical-records.png)
*Upload PDFs, extract structured data, ask questions grounded in your personal health documents*

### Architecture Visualization
![Architecture](docs/screenshots/architecture.png)
*5-stage agent pipeline with hybrid retrieval, self-correction, and safety validation*

> **View the interactive architecture diagram:** [Open docs/architecture-diagram.html](docs/architecture-diagram.html)

---

## How It Works

A user asks a healthcare question. The system runs a **5-stage agent pipeline** with optional self-correction:

1. **Router** — classifies intent (FAQ / emergency / web search / follow-up), rewrites query for retrieval
2. **Retriever** — BM25 keyword + FAISS dense search fused with Reciprocal Rank Fusion, then cross-encoder reranked
3. **Web Search** — for recent queries (2024+ drug recalls, outbreaks), routes to Tavily live search (if API key configured)
4. **Responder** — generates grounded answer strictly from retrieved context
5. **Evaluator** — scores faithfulness + relevance + safety; if score < 0.7, triggers self-correction retry with corrective prompt

Every token streams to the UI in real time via Server-Sent Events.

---

## Implemented Now

Core features working out of the box with default configuration:

| Feature | Description |
|---------|-------------|
| **5-stage LangGraph pipeline** | Router → Retriever → Web Search → Responder → Evaluator with conditional self-correction |
| **Streaming chat** | Server-Sent Events (SSE) via `/chat/stream` endpoint |
| **Retrieval-backed Q&A** | FAISS vector store with OpenAI embeddings (text-embedding-3-small) |
| **Confidence scoring** | Quality score (0-1) + retrieval confidence + hallucination risk per response |
| **Source citations** | Shows retrieved chunks with relevance scores in UI |
| **Medical records workflow** | Upload PDFs → structured extraction → grounded Q&A (session-scoped FAISS) |
| **Risk assessment** | 9 clinical factors → rule-based scoring → GPT-4o explanation |
| **Response caching** | LRU cache with 30-min TTL, SHA256 query hashing |
| **Rate limiting** | Token bucket: 20 req/min, 100 req/hour per client |
| **Hallucination detection** | Embedding similarity check (AWS blog approach) |
| **Prometheus metrics** | `/metrics` endpoint for monitoring |
| **Health checks** | `/health` with pipeline status, index readiness |
| **Docker deployment** | `docker-compose.yml` for local full-stack setup |
| **Render deployment** | Auto-deploy from GitHub main branch |

---

## Optional / Configurable

Features that require additional API keys or configuration:

| Feature | How to Enable |
|---------|---------------|
| **NVIDIA NIM backend** | Set `NVIDIA_API_KEY` in `.env` for Llama-3.1-405B or Nemotron reranking |
| **Tavily web search** | Set `TAVILY_API_KEY` in `.env` for real-time web retrieval |
| **Pinecone vector store** | Set `PINECONE_API_KEY` in `.env` to use cloud vector DB instead of FAISS |
| **Hybrid BM25+FAISS** | Enabled by default in retriever; configure weights in `agents/retriever.py` |
| **Cross-encoder reranking** | Enabled by default (ms-marco-MiniLM); swap model in `agents/retriever.py` |
| **AirLLM local mode** | Apple Silicon only: `pip install airllm mlx mlx-lm`, set `LOCAL_MODE=true` |

---

## Roadmap

Future enhancements not yet implemented:

- [ ] Longitudinal health trend analysis (lab values across multiple records over time)
- [ ] Drug interaction cross-reference against DrugBank open data
- [ ] RAGAS batch evaluation pipeline with MLflow logging
- [ ] Fine-tuned cross-encoder for medical domain
- [ ] Multi-user session management with persistent storage

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
│          5-Stage LangGraph Pipeline (async)                  │
│                                                             │
│  1. Router → 2. Retriever (BM25+FAISS+RRF+Rerank)          │
│                    ↘ 3. Web Search (Tavily, optional)       │
│                                         ↓                   │
│                              4. Responder                    │
│                                         ↓                   │
│                              5. Evaluator (quality gate)     │
│                              score<0.7 → retry Responder    │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
FastAPI (SSE streaming) ←→ Streamlit UI (4 tabs)
```

**Architecture notes:**
- **5 stages:** Router → Retriever → Web Search (optional) → Responder → Evaluator
- **Self-correction:** Conditional edge in LangGraph; if quality score < 0.7, Evaluator triggers Responder retry with corrective prompt (max 1 retry)
- **Streaming:** Every token streams to UI via Server-Sent Events as it's generated
- **Session-scoped records:** Separate in-memory FAISS index per user session for personal medical documents

---

## API Endpoints

Core endpoints exposed by the FastAPI application:

### System & Monitoring
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Root endpoint with API info |
| `GET` | `/health` | Health check with `pipeline_loaded`, `vector_store_ready`, `faiss_index_exists` |
| `GET` | `/metrics` | Prometheus metrics (request counts, latency, quality scores) |
| `GET` | `/stats` | Cache hit rate + rate limiter stats |

### Chat & RAG Pipeline
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/chat` | Full pipeline execution, returns complete JSON response |
| `POST` | `/chat/stream` | Server-Sent Events streaming (token events + final metadata) |
| `POST` | `/reset` | Clear conversation history for session |
| `POST` | `/ingest/text` | Add text content to shared FAISS knowledge base |

### Medical Records (session-scoped)
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/records/upload` | Upload personal medical record (PDF/text, session-scoped FAISS) |
| `POST` | `/records/analyze` | Extract structured data (diagnoses, labs, meds, allergies) |
| `POST` | `/records/query` | Ask questions grounded in uploaded records only |
| `DELETE` | `/records/clear/{session_id}` | Clear all records for a session |

### Risk Assessment
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/risk/assess` | ML + LLM patient risk assessment (9 clinical factors) |
| `GET` | `/risk/factors` | Risk factor schema for UI form |

### Local Model (optional, Apple Silicon only)
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/local-model/status` | AirLLM local model availability |
| `POST` | `/local-model/toggle` | Switch between cloud and on-device LLM |

**Full interactive API docs:** https://healthcare-rag-api.onrender.com/docs

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

## Startup Behavior

Understanding what happens when the API starts:

| Situation | Behavior |
|-----------|----------|
| **FAISS index missing** | API runs `vectorstore/ingest.py` automatically on startup to create empty index |
| **Ingest fails** | API logs warning and continues in degraded mode; retriever returns empty results |
| **No `OPENAI_API_KEY`** | Ingest falls back to `sentence-transformers` locally (if installed); LLM calls fail with 401 |
| **Pinecone not configured** | Falls back to FAISS only; no error |
| **User uploads documents** | Documents populate the shared FAISS index via `/ingest/text` or session-scoped index via `/records/upload` |

This resilience pattern ensures the API always starts successfully, even in incomplete configurations. The `/health` endpoint reports `vector_store_ready: false` when the index is missing or empty.

---

## What I Built

**Architecture & Agent Pipeline:**
- Designed the 5-stage LangGraph pipeline with conditional edges and self-correction retry loop
- Implemented hybrid BM25 + FAISS retrieval with Reciprocal Rank Fusion (α=0.5)
- Built cross-encoder reranking layer (ms-marco-MiniLM)
- Implemented emergency detection and 5-type intent classification

**Medical Features:**
- Built session-scoped personal document store (in-memory FAISS per user session)
- Implemented medical record extraction agent (structured JSON with lab value flagging)
- Created ML + LLM risk assessment pipeline (9 clinical factors → rule-based scoring → GPT-4o explanation)

**Production Features:**
- Built response caching system (LRU with 30-min TTL, SHA256 query hashing)
- Implemented token bucket rate limiter (20 req/min, 100 req/hour per client)
- Added hallucination detection using embedding similarity (AWS blog approach)
- Integrated Prometheus metrics for monitoring (`/metrics` endpoint)

**API & UI:**
- Built FastAPI backend with 20+ endpoints including SSE streaming (`/chat/stream`)
- Designed Streamlit UI with 4 tabs and live agent pipeline visualization
- Added real-time confidence scores, quality metrics, and expandable source citations
- Implemented quick-action buttons for common query types

**DevOps & Deployment:**
- Configured GitHub Actions CI with pytest
- Set up Docker + docker-compose for local full-stack deployment
- Deployed API on Render (auto-deploy from main branch)
- Deployed UI on Streamlit Cloud
- Implemented security (pre-commit hooks, `.gitignore` for API keys, `SECURITY.md`)

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
