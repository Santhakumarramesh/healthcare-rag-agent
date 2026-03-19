#!/bin/bash
# Start AI Healthcare Copilot UI
exec streamlit run streamlit_app/app_healthcare.py \
  --server.port "${PORT:-8501}" \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false \
  --server.address 0.0.0.0
