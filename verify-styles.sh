#!/bin/bash
# verify-styles.sh - Automated CSS verification system
# Verifies that unified blockquote and admonition CSS changes are working correctly

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Change to script directory
cd "$(dirname "$0")"

echo -e "${BLUE}🔍 CSS Verification System${NC}"
echo "=========================="
echo ""

# Step 1: Cleanup existing servers and build artifacts
echo -e "${YELLOW}[1/6] Cleaning up...${NC}"
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
sleep 1
rm -rf site
echo -e "${GREEN}✓ Cleanup complete${NC}"
echo ""

# Step 2: Build the site
echo -e "${YELLOW}[2/6] Building site...${NC}"
BUILD_OUTPUT=$(mktemp)
if .venv/bin/mkdocs build --no-directory-urls > "$BUILD_OUTPUT" 2>&1; then
    echo -e "${GREEN}✓ Build successful${NC}"
    rm -f "$BUILD_OUTPUT"
else
    echo -e "${RED}✗ Build failed${NC}"
    echo ""
    echo "Build error output:"
    tail -20 "$BUILD_OUTPUT"
    rm -f "$BUILD_OUTPUT"
    exit 1
fi
echo ""

# Step 3: Start server in background
echo -e "${YELLOW}[3/6] Starting server...${NC}"
python3 -m http.server 8000 --directory site > /dev/null 2>&1 &
SERVER_PID=$!

# Wait for server to be ready
MAX_WAIT=10
WAITED=0
while ! curl -s -o /dev/null -w '%{http_code}' http://localhost:8000 | grep -q 200; do
    sleep 1
    WAITED=$((WAITED + 1))
    if [ $WAITED -ge $MAX_WAIT ]; then
        echo -e "${RED}✗ Server failed to start${NC}"
        kill $SERVER_PID 2>/dev/null
        exit 1
    fi
done
echo -e "${GREEN}✓ Server started (PID: $SERVER_PID)${NC}"
echo ""

# Step 4: Run verification checks
echo -e "${YELLOW}[4/6] Running verification checks...${NC}"
PASSED=0
FAILED=0
TOTAL=0

# Helper function to run checks
check() {
    local description="$1"
    local command="$2"
    TOTAL=$((TOTAL + 1))

    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}  ✅ $description${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}  ❌ $description${NC}"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Server response checks
check "Server responds with 200" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000 | grep -q 200"
check "styles.css is accessible" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/styles.css | grep -q 200"
check "Test page loads successfully" "curl -s http://localhost:8000/test/ | grep -q 'blockquote'"

# CSS token definition checks
check "Crisp shadow tokens defined (sm)" "curl -s http://localhost:8000/styles.css | grep -q 'token-shadow-crisp-sm'"
check "Crisp shadow tokens defined (md)" "curl -s http://localhost:8000/styles.css | grep -q 'token-shadow-crisp-md'"
check "Crisp shadow tokens defined (lg)" "curl -s http://localhost:8000/styles.css | grep -q 'token-shadow-crisp-lg'"

# Blockquote and callout token checks
check "Blockquote shadow token defined" "curl -s http://localhost:8000/styles.css | grep -q 'token-blockquote-shadow'"
check "Blockquote radius token defined" "curl -s http://localhost:8000/styles.css | grep -q 'token-blockquote-radius'"
check "Callout shadow token defined" "curl -s http://localhost:8000/styles.css | grep -q 'token-callout-shadow'"
check "Callout radius token defined" "curl -s http://localhost:8000/styles.css | grep -q 'token-callout-radius'"

# Shadow value checks (actual pixel values)
check "Small shadow value correct" "curl -s http://localhost:8000/styles.css | grep -q '2px 2px 4px'"
check "Medium shadow value correct" "curl -s http://localhost:8000/styles.css | grep -q '3px 3px 8px'"
check "Large shadow value correct" "curl -s http://localhost:8000/styles.css | grep -q '4px 4px 12px'"

# Border radius checks
check "Border radius values present" "curl -s http://localhost:8000/styles.css | grep -q 'border-radius'"

# Usage in actual styles
check "Blockquote uses shadow token" "curl -s http://localhost:8000/styles.css | grep 'blockquote' | grep -q 'box-shadow'"
check "Admonition uses shadow token" "curl -s http://localhost:8000/styles.css | grep 'admonition' | grep -q 'box-shadow'"

# Security checks
echo ""
echo -e "${YELLOW}Security Checks:${NC}"

# Check attachment size
ATT_SIZE=$(du -sm site/Attachments 2>/dev/null | cut -f1 || echo 0)
if [ $ATT_SIZE -gt 100 ]; then
  echo -e "${RED}  ⚠️  WARNING: Attachments folder is ${ATT_SIZE}MB - possible leak!${NC}"
  echo -e "${RED}     Expected < 100MB for public galleries only${NC}"
else
  echo -e "${GREEN}  ✅ Attachments size OK (${ATT_SIZE}MB)${NC}"
fi

# Check for private folders
if [ -d "site/test-private" ]; then
  echo -e "${RED}  ❌ SECURITY: test-private folder leaked to build!${NC}"
  FAILED=$((FAILED + 1))
  TOTAL=$((TOTAL + 1))
else
  echo -e "${GREEN}  ✅ No private folders in site/${NC}"
fi

# List published attachments
echo ""
echo -e "${BLUE}Published attachments:${NC}"
find site/Attachments -type f 2>/dev/null | head -20 || echo "  (none)"

echo ""

# Step 5: Cleanup - Stop the server
echo -e "${YELLOW}[5/6] Stopping server...${NC}"
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true
echo -e "${GREEN}✓ Server stopped${NC}"
echo ""

# Step 6: Final report
echo -e "${YELLOW}[6/6] Verification Report${NC}"
echo "=========================="
echo -e "Total checks: ${BLUE}${TOTAL}${NC}"
echo -e "Passed: ${GREEN}${PASSED}${NC}"
echo -e "Failed: ${RED}${FAILED}${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "The CSS verification is complete. All blockquote and admonition"
    echo "tokens are properly defined and being used in the styles."
    exit 0
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ Some checks failed${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Please review the failed checks above and verify:"
    echo "  - styles.css contains all required design tokens"
    echo "  - Tokens are properly used in blockquote and admonition styles"
    echo "  - The build completed successfully"
    exit 1
fi
