#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

echo ""
echo "  Agent Readiness Workbench"
echo "  -------------------------"
echo "  Open in your browser:  http://localhost:8080"
echo "  API health check:      http://localhost:8080/api/health"
echo ""
echo "  (Uvicorn logs below — the UI does not render in the terminal.)"
echo ""

uvicorn backend.main:app --reload --host 0.0.0.0 --port 8080