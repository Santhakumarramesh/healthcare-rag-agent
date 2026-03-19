"""
run.py — Single entry point to start the Healthcare RAG Agent

Usage:
    python run.py api          # Start FastAPI backend (port 8000)
    python run.py ui           # Start Streamlit UI (port 8501)
    python run.py ingest       # Ingest knowledge base into vector store
    python run.py download     # Download all healthcare datasets
    python run.py eval         # Run RAGAS evaluation
    python run.py all          # Start API + UI together (requires tmux or two terminals)
"""

import sys
import os
import subprocess

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "api":
        port = int(os.environ.get("PORT", 8000))
        reload_flag = "--reload" if os.environ.get("APP_ENV") == "development" else ""
        print(f"🚀 Starting FastAPI backend on http://0.0.0.0:{port} ...")
        print(f"   API docs: http://localhost:{port}/docs")
        os.system(f"uvicorn api.main:app --host 0.0.0.0 --port {port} {reload_flag}".strip())

    elif cmd == "ui":
        print("🎨 Starting Streamlit UI on http://localhost:8501 ...")
        os.system("streamlit run streamlit_app/app.py --server.port 8501")

    elif cmd == "ingest":
        print("🧠 Ingesting healthcare knowledge base into vector store...")
        os.system("python data/ingest_knowledge_base.py")

    elif cmd == "download":
        print("📥 Downloading healthcare datasets from HuggingFace...")
        os.system("python data/download_datasets.py")

    elif cmd == "eval":
        print("📊 Running RAGAS evaluation pipeline...")
        os.system("python evaluation/ragas_eval.py")

    elif cmd == "all":
        print("🚀 Starting full stack (API + UI)...")
        print("   Open two terminals and run:")
        print("   Terminal 1: python run.py api")
        print("   Terminal 2: python run.py ui")
        print("\n   Or use Docker: docker-compose up --build")

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
