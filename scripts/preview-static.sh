#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
bash scripts/build-static.sh
echo ""
echo "  Preview:  http://localhost:4173"
echo ""
python3 -m http.server 4173 --directory dist