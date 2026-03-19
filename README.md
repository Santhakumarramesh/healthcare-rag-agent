# Healthcare AI Super-Agent

**Multi-agent RAG system for healthcare Q&A — featuring hybrid retrieval, real-time web search, self-correction loop, and on-device privacy mode.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-healthcare--rag--ui.onrender.com-blue)](https://healthcare-rag-ui.onrender.com)
[![API Docs](https://img.shields.io/badge/API%20Docs-healthcare--rag--api.onrender.com/docs-teal)](https://healthcare-rag-api.onrender.com/docs)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph%200.4-green)](https://github.com/langchain-ai/langgraph)
[![Tests](https://img.shields.io/badge/Tests-12%20passing-brightgreen)](tests/)

---

## What it does

A user asks a healthcare question. Behind the scenes, five specialized agents collaborate:

1. **Router** — classifies intent (FAQ, emergency, recent news, follow-up), rewrites the query for retrieval, detects life-threatening situations and bypasses the pipeline for immediate emergency response
2. **Retriever** — runs BM25 keyword search + FAISS dense vector search in parallel, fuses results with Reciprocal Rank Fusion, then reranks with a cross-encoder (or NVIDIA NIM Nemotron reranker)
3. **Web Search** — for queries about 2024–2025 drug recalls, outbreaks, or recent guidelines, calls Tavily's real-time search API instead of the static knowledge base
4. **Responder** — generates a grounded, empathetic answer using only the retrieved context, never hallucinating beyond it
5. **Evaluator** — scores the response for faithfulness, relevance, and safety; if quality < 0.7, triggers autonomous self-correction (max 1 retry)

Every token streams to the UI in real time via Server-Sent Events.

---

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                   LangGraph State Machine                    │
│                                                             │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  Router  │───▶│  Retriever   │───▶│    Responder     │  │
│  │  Agent   │    │ BM25+FAISS   │    │  GPT-4o-mini /   │  │
│  │          │    │ RRF + Rerank │    │  NVIDIA NIM      │  │
│  └──────────┘    └──────────────┘    └────────┬─────────┘  │
│       │                                        │             │
│       │ web_search intent                      ▼             │
│       │          ┌──────────────┐    ┌──────────────────┐  │
│       └─────────▶│  Web Search  │───▶│    Evaluator     │  │
│                  │ Tavily API   │    │  Score + Retry   │  │
│                  └──────────────┘    └────────┬─────────┘  │
│                                               │ if < 0.7    │
│                                               └──▶ Responder │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
FastAPI (SSE streaming) ←→ Streamlit UI
```

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| LLM orchestration | LangGraph 0.4 (async StateGraph) |
| Primary LLM | OpenAI GPT-4o-mini (cloud) |
| Optional LLM | NVIDIA NIM Llama-3.1-405B |
| Privacy LLM | Llama 3 8B via AirLLM + Apple MLX (on-device) |
| Embeddings | OpenAI text-embedding-3-small (prod) / all-MiniLM-L6-v2 (local) |
| Vector store | FAISS (local) + Pinecone (cloud fallback) |
| Keyword search | BM25Okapi (rank-bm25) |
| Retrieval fusion | Reciprocal Rank Fusion (RRF) |
| Reranking | cross-encoder/ms-marco-MiniLM-L-6-v2 / NVIDIA Nemotron |
| Web search | Tavily API |
| API backend | FastAPI + Uvicorn (async) |
| Streaming | Server-Sent Events (SSE) via StreamingResponse |
| Frontend | Streamlit |
| Monitoring | Prometheus metrics + custom hallucination detector |
| Rate limiting | In-memory sliding window |
| Response cache | LRU cache with TTL |
| Evaluation | RAGAS (faithfulness, answer relevancy, context precision) |
| Testing | pytest-asyncio, 12 intelligence tests with mocked LLM |
| CI | GitHub Actions (Python 3.11, pytest --cov) |
| Deployment | Render (API) + Streamlit Cloud (UI) |

---

## Key features

**Self-correcting pipeline** — the Evaluator agent scores every response across three dimensions: faithfulness to retrieved context, relevance to the question, and clinical safety. Responses scoring below 0.7 trigger an autonomous retry with a corrective prompt injected into the Responder's system message.

**Hybrid retrieval with RRF** — BM25 catches exact medical terminology (drug names, ICD codes) that dense embeddings miss. FAISS catches semantic meaning. RRF merges both ranked lists mathematically, consistently outperforming either alone.

**Real-time web search routing** — the Router detects queries about recent events (drug recalls, 2024+ guidelines, outbreaks) and routes to Tavily's live web search instead of the static knowledge base, so answers are never stale.

**Privacy mode** — a toggle in the sidebar switches the entire LLM backend from OpenAI's API to Llama 3 8B running locally via AirLLM's layer-by-layer Apple MLX inference. Every token is generated on-device. No data leaves the machine.

**Medical records analyzer** — a second tab lets users upload their own lab reports, discharge summaries, or doctor's notes (PDF or text). The system extracts structured information (diagnoses, lab values with normal/abnormal flags, medications, allergies) and then answers questions grounded strictly in those documents.

**Hallucination detection** — a dedicated utility cross-checks final responses against retrieved context using embedding similarity, flagging responses that introduce claims not present in the source material.

---

## Quick start

```bash
git clone https://github.com/Santhakumarramesh/healthcare-rag-agent
cd healthcare-rag-agent

python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Add your OPENAI_API_KEY to .env

python vectorstore/ingest.py          # build FAISS index (~30 seconds)
python run.py api                     # start API on :8000
python run.py ui                      # start UI on :8501 (new terminal)
```

Or with Docker:
```bash
docker-compose up --build
```

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/chat` | Full pipeline, returns complete JSON |
| `POST` | `/chat/stream` | SSE streaming — token events + final metadata event |
| `POST` | `/ingest/text` | Add text to shared knowledge base |
| `POST` | `/ingest/file` | Upload PDF/text to shared knowledge base |
| `POST` | `/records/upload` | Upload personal medical record (session-scoped) |
| `POST` | `/records/analyze` | Extract structured data from uploaded records |
| `POST` | `/records/query` | Ask questions about uploaded records |
| `GET` | `/health` | Health check |
| `GET` | `/metrics` | Prometheus metrics |
| `GET` | `/stats` | Cache + rate limiter stats |
| `POST` | `/local-model/toggle` | Switch between cloud and local LLM |

Full interactive docs: `https://healthcare-rag-api.onrender.com/docs`

---

## Project structure

```
healthcare-rag-agent/
├── agents/
│   ├── rag_pipeline.py       # LangGraph 5-agent async pipeline (core)
│   └── records_agent.py      # Medical record extraction + grounded QA
├── api/
│   ├── main.py               # FastAPI app — chat, ingest, streaming, monitoring
│   └── records.py            # Personal records CRUD router
├── vectorstore/
│   ├── retriever.py          # BM25 + FAISS + RRF + reranking
│   ├── ingest.py             # Document ingestion pipeline
│   └── personal_store.py     # Session-scoped in-memory FAISS for records
├── streamlit_app/
│   └── app.py                # Chat UI + Medical Records tab (720 lines)
├── utils/
│   ├── config.py             # Centralized settings (pydantic)
│   ├── cache.py              # LRU response cache with TTL
│   ├── rate_limiter.py       # Sliding window rate limiter
│   ├── hallucination_detector.py  # Embedding-based hallucination check
│   └── local_llm.py          # AirLLM wrapper for Apple MLX inference
├── evaluation/
│   ├── evaluate.py           # RAGAS evaluation pipeline
│   └── ragas_eval.py         # Batch evaluation with MLflow logging
├── tests/
│   ├── test_config.py        # Config validation tests
│   └── test_intelligence.py  # 9 async agent intelligence tests
├── .github/workflows/        # CI — pytest on every push
├── render.yaml               # Render deployment config
├── Procfile                  # Process definition
└── requirements.txt          # Production deps (no torch, no CUDA)
```

---

## Honest limitations

- Personal document store is a singleton — breaks with multi-worker deployment (fine on free tier)
- Render free tier cold-starts after 15 min inactivity — first request takes ~30 seconds
- Local privacy mode requires Apple Silicon Mac (M1/M2/M3)
- NVIDIA NIM reranker requires a valid NVIDIA API key

---

## Author

**Santhakumar Ramesh** — AI/ML Engineer @ DXC Technology | MS Data Science, University at Buffalo

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/santhakumar-ramesh/)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?logo=github)](https://github.com/santhakumarramesh)
[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-green)](https://santhakumarramesh.github.io)
