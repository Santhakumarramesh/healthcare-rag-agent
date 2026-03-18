#!/bin/bash
# ============================================================
# Healthcare RAG Agent — One-Command Setup Script
# Run: bash setup.sh
# ============================================================

set -e  # Exit on any error

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║       Healthcare RAG Agent — Setup                       ║"
echo "║       Multi-Agent LangGraph + FAISS + GPT-4o             ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ── Step 1: Check Python ──────────────────────────────────────
echo "✅ Step 1/5: Checking Python version..."
python3 --version || { echo "❌ Python 3.11+ required. Install from python.org"; exit 1; }

# ── Step 2: Create virtual environment ───────────────────────
echo ""
echo "✅ Step 2/5: Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo "   Virtual env activated."

# ── Step 3: Install dependencies ─────────────────────────────
echo ""
echo "✅ Step 3/5: Installing dependencies (this takes ~2 min)..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "   Dependencies installed."

# ── Step 4: Set up .env file ──────────────────────────────────
echo ""
echo "✅ Step 4/5: Setting up environment file..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "   ⚠️  IMPORTANT: Open .env and add your OPENAI_API_KEY"
    echo "   Your key: https://platform.openai.com/api-keys"
    echo ""
    read -p "   Press ENTER after you've added your API key to .env..."
else
    echo "   .env already exists — skipping."
fi

# ── Step 5: Ingest knowledge base ────────────────────────────
echo ""
echo "✅ Step 5/5: Ingesting healthcare knowledge base..."
python data/ingest_knowledge_base.py
echo ""

# ── Done ──────────────────────────────────────────────────────
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ✅ Setup Complete!                                       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "   Start the API:    python run.py api"
echo "   Start the UI:     python run.py ui   (new terminal)"
echo "   Or Docker:        docker-compose up --build"
echo ""
echo "   API Docs:   http://localhost:8000/docs"
echo "   Chat UI:    http://localhost:8501"
echo ""
