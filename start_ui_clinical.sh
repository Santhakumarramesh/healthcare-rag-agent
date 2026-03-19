#!/bin/bash
# start_ui_clinical.sh — Render startup script for Clinical Intelligence UI
# This script launches the new premium clinical interface
exec streamlit run streamlit_app/app_clinical.py \
  --server.port "${PORT:-8501}" \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false \
  --server.address 0.0.0.0
