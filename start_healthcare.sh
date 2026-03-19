#!/bin/bash
# start_healthcare.sh — Startup script for AI Healthcare Copilot
# This script launches the complete 7-page healthcare workflow platform

echo "🏥 Starting AI Healthcare Copilot..."
echo ""
echo "📋 Complete 7-page platform:"
echo "  1. Home - Care operating dashboard"
echo "  2. Analyze Report - Medical report analysis"
echo "  3. Ask AI - Structured medical Q&A"
echo "  4. Follow-up Monitor - Longitudinal tracking (THE MOAT)"
echo "  5. Records Timeline - Persistent healthcare system"
echo "  6. Monitoring - Operations dashboard"
echo "  7. Settings - Admin controls"
echo ""
echo "🚀 Launching..."
echo ""

exec streamlit run streamlit_app/app_healthcare.py \
  --server.port "${PORT:-8501}" \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false \
  --server.address 0.0.0.0
