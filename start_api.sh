#!/bin/bash
# start_api.sh — Render startup script for FastAPI backend
exec uvicorn api.main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}"
