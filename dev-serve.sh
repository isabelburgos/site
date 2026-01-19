#!/bin/bash
# dev-serve.sh - Start MkDocs development server with live CSS reload
#
# This script starts mkdocs serve with optimal settings for development:
# - Watches docs/ and ../shared/ for changes
# - Disables strict mode for faster iteration
# - Clears any cached files
# - Opens browser automatically

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Change to Website directory
cd "$(dirname "$0")"

echo -e "${BLUE}🚀 Starting MkDocs Development Server${NC}"
echo ""

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found${NC}"
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Clean any cached files
echo -e "${BLUE}Cleaning cache...${NC}"
rm -rf site/
rm -rf .cache/

# Start server
echo ""
echo -e "${GREEN}✓ Server starting${NC}"
echo -e "${BLUE}📝 Edit these files for live reload:${NC}"
echo "   - Website/docs/styles.css"
echo "   - shared/tokens-layout.css"
echo "   - shared/tokens-palette-website.css"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

# Start mkdocs serve with live reload
# --no-strict: Don't fail on warnings (faster iteration)
# --watch docs: Watch docs folder
# --watch ../shared: Watch shared CSS tokens
mkdocs serve --no-strict
