# Makefile for Databricks MCP Server Testing

.PHONY: help install test test-unit test-integration test-slow test-all lint format type-check security clean coverage setup dev

# Default target
help:
	@echo "Available targets:"
	@echo "  install       - Install dependencies"
	@echo "  setup         - Setup development environment"
	@echo "  dev           - Start development servers"
	@echo ""
	@echo "Testing:"
	@echo "  test          - Run unit and integration tests"
	@echo "  test-unit     - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-slow     - Run slow tests"
	@echo "  test-all      - Run all tests including slow ones"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint          - Run linting checks"
	@echo "  format        - Format code"
	@echo "  type-check    - Run type checking"
	@echo "  security      - Run security checks"
	@echo ""
	@echo "Utilities:"
	@echo "  coverage      - Generate coverage report"
	@echo "  clean         - Clean build artifacts"

# Environment setup
install:
	uv sync --all-extras

setup: install
	@echo "Setting up development environment..."
	@if [ ! -f .env.local ]; then \
		echo "Creating .env.local template..."; \
		cp .env.example .env.local 2>/dev/null || echo "DATABRICKS_HOST=https://your-workspace.cloud.databricks.com\nDATABRICKS_TOKEN=your-token" > .env.local; \
	fi
	@echo "Development environment setup complete!"

dev:
	./watch.sh

# Testing targets
test:
	./run_tests.sh

test-unit:
	./run_tests.sh --unit-only

test-integration:
	./run_tests.sh --integration-only

test-slow:
	./run_tests.sh --slow

test-all:
	./run_tests.sh --slow

# Code quality targets
lint:
	uv run ruff check server/ dba_mcp_proxy/ tests/

format:
	uv run ruff format server/ dba_mcp_proxy/ tests/

type-check:
	uv run ty check server/ dba_mcp_proxy/

security:
	./run_tests.sh --security

# Coverage
coverage:
	uv run pytest tests/ --cov=server --cov=dba_mcp_proxy --cov-report=html:coverage_html --cov-report=term-missing
	@echo "Coverage report generated in coverage_html/"

# Testing with different options
test-verbose:
	./run_tests.sh --verbose

test-no-parallel:
	./run_tests.sh --no-parallel

test-no-coverage:
	./run_tests.sh --no-coverage

# CI-like testing
test-ci:
	./run_tests.sh --security --verbose

# Quick testing (minimal checks)
test-quick:
	./run_tests.sh --unit-only --no-lint --no-type-check

# Development testing (faster feedback)
test-dev:
	./run_tests.sh --no-security --no-slow

# Clean up
clean:
	rm -rf coverage_html/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf */__pycache__/
	rm -rf */*/__pycache__/
	rm -rf *.egg-info/
	rm -rf build/
	rm -rf dist/
	rm -f bandit-report.json
	rm -f safety-report.json
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Deployment testing
test-deploy:
	./run_tests.sh --integration-only --slow
	@echo "Testing deployment build process..."
	uv run python scripts/generate_semver_requirements.py
	@echo "Deployment tests complete!"

# Frontend testing (if needed)
test-frontend:
	cd client && bun run lint && bun run type-check && bun run build

# Full test suite (everything)
test-full: test-all security test-frontend
	@echo "Full test suite completed!"

# Development workflow helpers
fix: format lint
	@echo "Code fixed and linted!"

check: lint type-check
	@echo "Code quality checks passed!"

# Benchmark testing
benchmark:
	uv run pytest tests/ -m "performance" --benchmark-only --benchmark-json=benchmark.json

# Testing with specific markers
test-mcp:
	uv run pytest tests/ -m "mcp" -v

test-api:
	uv run pytest tests/ -m "api" -v

test-tools:
	uv run pytest tests/ -m "tools" -v

test-proxy:
	uv run pytest tests/ -m "proxy" -v

# Watch mode for development
test-watch:
	uv run pytest-watch tests/unit/ -- --tb=short

# Generate test report
test-report:
	uv run pytest tests/ --html=test-report.html --self-contained-html

# Pre-commit hook simulation
pre-commit: format lint type-check test-unit
	@echo "Pre-commit checks passed!"