#!/bin/bash
# FAISS index is built HERE (not in build step) because OPENAI_API_KEY
# is only injected by Render at runtime, not during the build phase.
set -e

# Resolve python binary (Render uses 'python', Mac uses 'python3')
PYTHON=$(command -v python || command -v python3)
echo "[start] Using Python: $PYTHON"
echo "[start] CWD=$(pwd) | FAISS_INDEX_PATH=${FAISS_INDEX_PATH:-./vectorstore/faiss_index}"

INDEX_DIR="${FAISS_INDEX_PATH:-./vectorstore/faiss_index}"

if [ -f "${INDEX_DIR}/index.faiss" ]; then
  echo "[start] FAISS index already exists — skipping ingest."
else
  echo "[start] Building FAISS index (OPENAI_API_KEY is available at runtime)..."
  $PYTHON vectorstore/ingest.py
  echo "[start] Index ready."
fi

echo "[start] Starting uvicorn..."
exec uvicorn api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
