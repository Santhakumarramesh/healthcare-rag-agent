# ─────────────────────────────────────────────────────────────────────────────
# Healthcare RAG Agent — Makefile
# Common dev, build, and deploy commands in one place.
#
# Usage:  make <target>
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: help install dev-install lint test build run stop logs \
        index deploy deploy-api deploy-ui deploy-verify health clean

# ── Default target ────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  Healthcare RAG Agent — available commands"
	@echo "  ─────────────────────────────────────────────────────────────────"
	@echo "  Setup"
	@echo "    make install          Install production dependencies"
	@echo "    make dev-install      Install dev + production dependencies"
	@echo ""
	@echo "  Quality"
	@echo "    make lint             Run ruff linter"
	@echo "    make test             Run pytest tests"
	@echo ""
	@echo "  Index (run once locally before first deploy)"
	@echo "    make index            Build FAISS index from knowledge base"
	@echo ""
	@echo "  Local run"
	@echo "    make run              Start API + UI via docker-compose"
	@echo "    make stop             Stop docker-compose services"
	@echo "    make logs             Tail docker-compose logs"
	@echo "    make health           Curl local /health endpoint"
	@echo ""
	@echo "  Deploy to Render"
	@echo "    make deploy           Trigger both API + UI deploys"
	@echo "    make deploy-api       Trigger API deploy only"
	@echo "    make deploy-ui        Trigger UI deploy only"
	@echo "    make deploy-verify    Deploy + wait + verify /health"
	@echo ""
	@echo "  Cleanup"
	@echo "    make clean            Remove __pycache__, .pytest_cache, logs"
	@echo ""

# ── Setup ─────────────────────────────────────────────────────────────────────
install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements-local.txt
	pip install ruff pytest pytest-asyncio

# ── Quality ───────────────────────────────────────────────────────────────────
lint:
	ruff check . --output-format=full

test:
	pytest tests/ -v --tb=short

# ── Index (build once locally, commit, deploy) ────────────────────────────────
index:
	@echo "Building FAISS index locally..."
	@bash scripts/build_index_locally.sh

# ── Local run ─────────────────────────────────────────────────────────────────
run:
	docker compose up --build -d
	@echo "API  → http://localhost:8000"
	@echo "UI   → http://localhost:8501"
	@echo "Docs → http://localhost:8000/docs"

stop:
	docker compose down

logs:
	docker compose logs -f

health:
	@curl -s http://localhost:8000/health | python3 -m json.tool || \
	  echo "API not reachable — is it running? Try: make run"

# ── Deploy ────────────────────────────────────────────────────────────────────
deploy:
	@bash scripts/deploy.sh both

deploy-api:
	@bash scripts/deploy.sh api

deploy-ui:
	@bash scripts/deploy.sh ui

deploy-verify:
	@bash scripts/deploy.sh both --verify

# ── Cleanup ───────────────────────────────────────────────────────────────────
clean:
	find . -type d -name "__pycache__" -not -path "./.venv/*" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -not -path "./.venv/*" -delete 2>/dev/null || true
	rm -f logs/*.log
	@echo "Clean complete."
