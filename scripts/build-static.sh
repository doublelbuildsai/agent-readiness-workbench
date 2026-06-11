#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf dist
mkdir -p dist
cp frontend/index.html frontend/styles.css frontend/app.js frontend/static-demo.json dist/
touch dist/.nojekyll
echo "Built static site → dist/"
echo "Preview: python3 -m http.server 4173 --directory dist"
echo "Recording: http://localhost:4173/?record=1"