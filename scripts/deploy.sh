#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# deploy.sh — One-command manual deploy to Render
#
# Usage:
#   bash scripts/deploy.sh           # deploy both API + UI
#   bash scripts/deploy.sh api       # deploy API only
#   bash scripts/deploy.sh ui        # deploy UI only
#   bash scripts/deploy.sh --verify  # deploy + wait and verify health
#
# Setup (one-time):
#   1. Go to Render → healthcare-rag-api → Settings → Deploy Hook → Copy URL
#   2. Go to Render → healthcare-rag-ui  → Settings → Deploy Hook → Copy URL
#   3. Add both to your .env:
#        RENDER_DEPLOY_HOOK_API=https://api.render.com/deploy/srv-xxxxx?key=xxxxx
#        RENDER_DEPLOY_HOOK_UI=https://api.render.com/deploy/srv-yyyyy?key=yyyyy
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# ── Load env vars ─────────────────────────────────────────────────────────────
if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

API_HOOK="${RENDER_DEPLOY_HOOK_API:-}"
UI_HOOK="${RENDER_DEPLOY_HOOK_UI:-}"
API_URL="${RENDER_API_URL:-https://healthcare-rag-api.onrender.com}"

TARGET="${1:-both}"
VERIFY=false
if [[ "${*}" == *"--verify"* ]]; then
  VERIFY=true
  TARGET="${1:-both}"
  [[ "$TARGET" == "--verify" ]] && TARGET="both"
fi

# ── Helper functions ──────────────────────────────────────────────────────────
trigger_deploy() {
  local name="$1"
  local hook="$2"

  if [ -z "$hook" ]; then
    echo "⚠️  No deploy hook for $name."
    echo "   Add RENDER_DEPLOY_HOOK_$(echo "$name" | tr '[:lower:]' '[:upper:]') to your .env"
    return 0
  fi

  echo "🚀 Triggering $name deploy..."
  local status
  status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$hook")

  if [ "$status" = "200" ] || [ "$status" = "201" ]; then
    echo "   ✅ $name deploy triggered successfully (HTTP $status)"
  else
    echo "   ❌ $name deploy hook returned HTTP $status"
    return 1
  fi
}

verify_health() {
  local url="$API_URL/health"
  local wait_secs=180
  local retries=5
  local retry_interval=30

  echo ""
  echo "⏳ Waiting ${wait_secs}s for Render to build and restart..."
  sleep "$wait_secs"

  echo "🔍 Verifying API health at $url ..."
  for attempt in $(seq 1 "$retries"); do
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    body=$(curl -s "$url" 2>/dev/null || echo "{}")

    if [ "$status" = "200" ]; then
      echo "   ✅ API is healthy (attempt $attempt)"
      echo "   Response: $body"
      return 0
    fi
    echo "   Attempt $attempt/$retries: HTTP $status — retrying in ${retry_interval}s..."
    sleep "$retry_interval"
  done

  echo "   ❌ API health check failed after $retries attempts."
  echo "   Check logs at: https://dashboard.render.com"
  return 1
}

# ── Main ──────────────────────────────────────────────────────────────────────
echo "============================================================"
echo "  Healthcare RAG — Render Deploy"
echo "  Target: $TARGET | Verify: $VERIFY"
echo "  $(date)"
echo "============================================================"
echo ""

case "$TARGET" in
  api)
    trigger_deploy "API" "$API_HOOK"
    ;;
  ui)
    trigger_deploy "UI" "$UI_HOOK"
    ;;
  both|*)
    trigger_deploy "API" "$API_HOOK"
    trigger_deploy "UI"  "$UI_HOOK"
    ;;
esac

if $VERIFY; then
  verify_health
fi

echo ""
echo "🎉 Done. Monitor progress at: https://dashboard.render.com"
