# ─────────────────────────────────────────────────────────────────────────────
# Healthcare RAG Agent — Production Dockerfile
# Multi-stage build: keeps the final image lean and runs as a non-root user.
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: dependency builder ───────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# System deps needed only for compiling wheels (e.g. faiss-cpu, bcrypt)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime image ────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Security: run as a non-root user
RUN groupadd --gid 1001 appgroup \
    && useradd --uid 1001 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Install curl for HEALTHCHECK only (no build tools in runtime image)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application source (respects .dockerignore)
COPY --chown=appuser:appgroup . .

# Create writable runtime directories
# data/ — SQLite databases (memory, feedback)
# logs/ — application logs
# vectorstore/faiss_index — FAISS index (must be pre-built and committed)
RUN mkdir -p vectorstore/faiss_index logs data \
    && chown -R appuser:appgroup vectorstore logs data

# Drop to non-root
USER appuser

EXPOSE 8000 8501

# Built-in health check so Docker / Compose / K8s know when the app is ready
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
