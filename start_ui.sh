#!/bin/bash
# start_ui.sh — Render startup script for Streamlit UI
# This script is called by Render's start command
exec streamlit run streamlit_app/app.py \
  --server.port "${PORT:-8501}" \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false \
  --server.address 0.0.0.0
