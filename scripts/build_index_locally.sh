#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# build_index_locally.sh
#
# Run this ONCE on your local machine before pushing to Render / HF Spaces.
# It builds the FAISS vector index from the sample medical knowledge base
# and writes the output to vectorstore/faiss_index/.
#
# Usage:
#   cp .env.example .env          # fill in OPENAI_API_KEY
#   bash scripts/build_index_locally.sh
#   git add vectorstore/faiss_index/
#   git commit -m "chore: add prebuilt FAISS index"
#   git push
#
# After that your deployment will start cleanly without any ML work at runtime.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

# ── Sanity checks ─────────────────────────────────────────────────────────────
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found."
    echo "  cp .env.example .env  and fill in OPENAI_API_KEY first."
    exit 1
fi

# Load env vars from .env without exporting the file wholesale
set -a
# shellcheck disable=SC1091
source .env
set +a

if [ -z "${OPENAI_API_KEY:-}" ] || [ "${OPENAI_API_KEY}" = "sk-your-openai-key-here" ]; then
    echo "ERROR: OPENAI_API_KEY is not set or still a placeholder."
    echo "  Edit .env and set a real key."
    exit 1
fi

# ── Activate venv if present ──────────────────────────────────────────────────
if [ -f ".venv/bin/activate" ]; then
    echo "[build] Activating .venv..."
    # shellcheck disable=SC1091
    source .venv/bin/activate
fi

# ── Run ingest ────────────────────────────────────────────────────────────────
echo "[build] Starting FAISS index build..."
echo "[build] This calls the OpenAI embeddings API (~100-300 chunks for the default dataset)."
echo ""

python vectorstore/ingest.py

echo ""
echo "[build] ✓ Done! Index written to vectorstore/faiss_index/"
echo ""
echo "Next steps:"
echo "  git add vectorstore/faiss_index/"
echo "  git commit -m 'chore: add prebuilt FAISS index'"
echo "  git push"
echo ""
echo "Then redeploy on Render — the API will start immediately without any"
echo "embedding calls at runtime."
