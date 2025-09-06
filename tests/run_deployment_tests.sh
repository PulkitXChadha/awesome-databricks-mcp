#!/bin/bash

# Deployment Test Runner Script
# Validates the deployed Databricks MCP server

set -e

echo "=================================================="
echo "Databricks MCP Server - Deployment Validation"
echo "=================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if deployment URL is set
if [ -z "$DATABRICKS_APP_URL" ]; then
    echo -e "${YELLOW}Warning: DATABRICKS_APP_URL not set${NC}"
    echo "Checking for local deployment..."
    
    if [ "$LOCAL_DEPLOYMENT" == "true" ]; then
        export DATABRICKS_APP_URL="http://localhost:8000"
        echo -e "${GREEN}Using local deployment URL: $DATABRICKS_APP_URL${NC}"
    else
        echo -e "${RED}Error: No deployment URL configured${NC}"
        echo "Set DATABRICKS_APP_URL or LOCAL_DEPLOYMENT=true"
        exit 1
    fi
else
    echo -e "${GREEN}Deployment URL: $DATABRICKS_APP_URL${NC}"
fi

# Function to run specific test suites
run_test_suite() {
    local suite=$1
    local description=$2
    
    echo ""
    echo -e "${BLUE}Running: $description${NC}"
    echo "----------------------------------------"
    
    if uv run pytest tests/test_deployment.py -m "$suite" -v --tb=short; then
        echo -e "${GREEN}✓ $description passed${NC}"
        return 0
    else
        echo -e "${RED}✗ $description failed${NC}"
        return 1
    fi
}

# Track test results
FAILED_TESTS=()
PASSED_TESTS=()

# Run test suites
echo ""
echo "Starting deployment validation tests..."
echo ""

# 1. Health checks
if run_test_suite "deployment" "Health & Availability Tests"; then
    PASSED_TESTS+=("Health & Availability")
else
    FAILED_TESTS+=("Health & Availability")
fi

# 2. Smoke tests
if run_test_suite "smoke" "Critical Path Smoke Tests"; then
    PASSED_TESTS+=("Smoke Tests")
else
    FAILED_TESTS+=("Smoke Tests")
fi

# 3. Security tests
if run_test_suite "security" "Security Validation Tests"; then
    PASSED_TESTS+=("Security Tests")
else
    FAILED_TESTS+=("Security Tests")
fi

# 4. Load tests (optional)
echo ""
echo -e "${BLUE}Optional: Load Testing${NC}"
echo "Run with: uv run pytest tests/test_deployment.py -m load -v"

# 5. Manual OAuth verification
echo ""
echo -e "${YELLOW}Manual Verification Required:${NC}"
echo "OAuth flow must be manually tested. Run:"
echo "uv run pytest tests/test_deployment.py -m manual -v -s"

# Summary
echo ""
echo "=================================================="
echo "Deployment Validation Summary"
echo "=================================================="

if [ ${#PASSED_TESTS[@]} -gt 0 ]; then
    echo -e "${GREEN}Passed Tests:${NC}"
    for test in "${PASSED_TESTS[@]}"; do
        echo -e "  ${GREEN}✓${NC} $test"
    done
fi

if [ ${#FAILED_TESTS[@]} -gt 0 ]; then
    echo -e "${RED}Failed Tests:${NC}"
    for test in "${FAILED_TESTS[@]}"; do
        echo -e "  ${RED}✗${NC} $test"
    done
fi

# Exit status
if [ ${#FAILED_TESTS[@]} -eq 0 ]; then
    echo ""
    echo -e "${GREEN}All automated deployment tests passed!${NC}"
    echo "Remember to perform manual OAuth verification."
    exit 0
else
    echo ""
    echo -e "${RED}Some deployment tests failed. Please review the output above.${NC}"
    exit 1
fi