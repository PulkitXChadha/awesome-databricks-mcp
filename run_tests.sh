#!/bin/bash
# Test runner script for Databricks MCP Server.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Default values
RUN_UNIT=true
RUN_INTEGRATION=true
RUN_SLOW=false
RUN_LINT=true
RUN_TYPE_CHECK=true
RUN_SECURITY=false
COVERAGE=true
PARALLEL=true
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --unit-only)
            RUN_UNIT=true
            RUN_INTEGRATION=false
            shift
            ;;
        --integration-only)
            RUN_UNIT=false
            RUN_INTEGRATION=true
            shift
            ;;
        --slow)
            RUN_SLOW=true
            shift
            ;;
        --no-lint)
            RUN_LINT=false
            shift
            ;;
        --no-type-check)
            RUN_TYPE_CHECK=false
            shift
            ;;
        --security)
            RUN_SECURITY=true
            shift
            ;;
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        --no-parallel)
            PARALLEL=false
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --unit-only      Run only unit tests"
            echo "  --integration-only Run only integration tests" 
            echo "  --slow           Include slow tests"
            echo "  --no-lint        Skip linting"
            echo "  --no-type-check  Skip type checking"
            echo "  --security       Run security checks"
            echo "  --no-coverage    Skip coverage reporting"
            echo "  --no-parallel    Run tests sequentially"
            echo "  --verbose        Verbose output"
            echo "  --help           Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    print_error "uv is required but not installed. Please install uv first."
    exit 1
fi

# Setup test environment
print_status "Setting up test environment..."
export DATABRICKS_HOST="https://test.cloud.databricks.com"
export DATABRICKS_TOKEN="test-token"  
export TESTING="true"

# Install dependencies
print_status "Installing dependencies..."
uv sync --all-extras

# Run linting
if [[ "$RUN_LINT" == true ]]; then
    print_status "Running linting checks..."
    if uv run ruff check server/ dba_mcp_proxy/ tests/; then
        print_success "Linting passed"
    else
        print_error "Linting failed"
        exit 1
    fi
    
    print_status "Checking code formatting..."
    if uv run ruff format --check server/ dba_mcp_proxy/ tests/; then
        print_success "Code formatting is correct"
    else
        print_error "Code formatting issues found. Run 'uv run ruff format server/ dba_mcp_proxy/ tests/' to fix"
        exit 1
    fi
fi

# Run type checking
if [[ "$RUN_TYPE_CHECK" == true ]]; then
    print_status "Running type checks..."
    if uv run ty check server/ dba_mcp_proxy/; then
        print_success "Type checking passed"
    else
        print_warning "Type checking found issues (continuing...)"
    fi
fi

# Prepare pytest arguments
PYTEST_ARGS=()
if [[ "$VERBOSE" == true ]]; then
    PYTEST_ARGS+=("-v")
fi

if [[ "$COVERAGE" == true ]]; then
    PYTEST_ARGS+=("--cov=server" "--cov=dba_mcp_proxy" "--cov-report=term-missing" "--cov-report=html:coverage_html")
fi

if [[ "$PARALLEL" == true ]]; then
    PYTEST_ARGS+=("-n" "auto")
fi

# Run unit tests
if [[ "$RUN_UNIT" == true ]]; then
    print_status "Running unit tests..."
    if uv run pytest tests/unit/ "${PYTEST_ARGS[@]}"; then
        print_success "Unit tests passed"
    else
        print_error "Unit tests failed"
        exit 1
    fi
fi

# Run integration tests
if [[ "$RUN_INTEGRATION" == true ]]; then
    print_status "Running integration tests..."
    
    INTEGRATION_ARGS=("${PYTEST_ARGS[@]}")
    
    if [[ "$RUN_SLOW" == false ]]; then
        INTEGRATION_ARGS+=("-m" "not slow")
        print_status "(Excluding slow tests - use --slow to include them)"
    fi
    
    if uv run pytest tests/integration/ "${INTEGRATION_ARGS[@]}"; then
        print_success "Integration tests passed"
    else
        print_error "Integration tests failed"
        exit 1
    fi
fi

# Run slow tests separately if requested
if [[ "$RUN_SLOW" == true && "$RUN_INTEGRATION" == true ]]; then
    print_status "Running slow integration tests..."
    if uv run pytest tests/integration/ -m "slow" --tb=short; then
        print_success "Slow tests passed"
    else
        print_warning "Some slow tests failed (this might be expected)"
    fi
fi

# Run security checks
if [[ "$RUN_SECURITY" == true ]]; then
    print_status "Running security checks..."
    
    print_status "Running bandit security scan..."
    if uv run bandit -r server/ dba_mcp_proxy/ --format json --output bandit-report.json; then
        print_success "Bandit security scan passed"
    else
        print_warning "Bandit found potential security issues (check bandit-report.json)"
    fi
    
    print_status "Running safety dependency check..."
    if uv run safety check --json --output safety-report.json; then
        print_success "Safety dependency check passed"
    else
        print_warning "Safety found potential dependency issues (check safety-report.json)"
    fi
fi

# Summary
print_success "Test run completed!"

if [[ "$COVERAGE" == true ]]; then
    print_status "Coverage report generated in coverage_html/"
fi

if [[ "$RUN_SECURITY" == true ]]; then
    print_status "Security reports: bandit-report.json, safety-report.json"
fi

print_status "All checks completed successfully!"