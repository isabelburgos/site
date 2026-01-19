#!/bin/bash
# Development server for Website with live CSS editing
#
# Usage:
#   ./dev-server.sh          # Start server
#   # Edit docs/styles.css, then rebuild:
#   .venv/bin/mkdocs build --no-directory-urls
#   # Server will serve updated files automatically

cd "$(dirname "$0")"

# Kill any existing servers on port 8000
echo "Checking for existing servers on port 8000..."
PIDS=$(lsof -ti :8000 2>/dev/null)
if [ ! -z "$PIDS" ]; then
  echo "Stopping existing servers: $PIDS"
  kill $PIDS 2>/dev/null
  sleep 1
fi

# Build the site first
echo "Building site..."
.venv/bin/mkdocs build --no-directory-urls

# Start simple HTTP server
echo "Starting server at http://localhost:8000"
python3 -m http.server 8000 --directory site
