# Testing Guide

This document provides comprehensive information about testing the Databricks MCP Server project.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Writing Tests](#writing-tests)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

## Overview

The Databricks MCP Server project uses a comprehensive testing strategy with multiple types of tests:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions and workflows
- **API Tests**: Test FastAPI endpoints and HTTP interfaces
- **MCP Protocol Tests**: Test MCP server compliance and functionality
- **Proxy Tests**: Test MCP proxy functionality
- **Performance Tests**: Test performance characteristics

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures and configuration
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── test_app.py            # FastAPI app tests
│   ├── test_mcp_proxy.py      # MCP proxy tests
│   ├── tools/                 # Tool-specific tests
│   │   ├── __init__.py
│   │   ├── test_core.py
│   │   ├── test_unity_catalog.py
│   │   ├── test_sql_operations.py
│   │   ├── test_dashboards.py
│   │   └── test_tools_loading.py
│   ├── routers/               # API router tests
│   │   ├── __init__.py
│   │   ├── test_user.py
│   │   ├── test_mcp_info.py
│   │   ├── test_prompts.py
│   │   └── test_router_init.py
│   └── services/              # Service layer tests
│       └── __init__.py
└── integration/               # Integration tests
    ├── __init__.py
    ├── test_mcp_server_integration.py
    └── test_services_integration.py
```

## Running Tests

### Quick Start

```bash
# Run all tests (recommended)
make test

# Or use the test runner directly
./run_tests.sh
```

### Test Runner Options

The `run_tests.sh` script supports various options:

```bash
# Unit tests only
./run_tests.sh --unit-only

# Integration tests only  
./run_tests.sh --integration-only

# Include slow tests
./run_tests.sh --slow

# Skip linting
./run_tests.sh --no-lint

# Skip type checking
./run_tests.sh --no-type-check

# Run security checks
./run_tests.sh --security

# Verbose output
./run_tests.sh --verbose

# No parallel execution
./run_tests.sh --no-parallel

# No coverage reporting
./run_tests.sh --no-coverage
```

### Make Targets

The project includes a comprehensive Makefile:

```bash
# Basic testing
make test              # Run standard test suite
make test-unit         # Unit tests only
make test-integration  # Integration tests only
make test-all          # All tests including slow ones
make test-slow         # Slow tests only

# Code quality
make lint              # Run linting
make format            # Format code
make type-check        # Type checking
make security          # Security checks

# Development
make test-dev          # Fast development testing
make test-quick        # Minimal quick testing
make test-watch        # Watch mode for development

# Specialized
make test-mcp          # MCP-specific tests
make test-api          # API tests only
make test-tools        # Tool tests only
make test-proxy        # Proxy tests only

# Coverage and reporting
make coverage          # Generate coverage report
make test-report       # Generate HTML test report
make benchmark         # Run performance benchmarks
```

### Direct pytest Usage

You can also run pytest directly:

```bash
# Basic usage
uv run pytest tests/

# With coverage
uv run pytest tests/ --cov=server --cov=dba_mcp_proxy

# Specific test categories
uv run pytest tests/ -m "unit"
uv run pytest tests/ -m "integration"
uv run pytest tests/ -m "slow"
uv run pytest tests/ -m "api"

# Parallel execution
uv run pytest tests/ -n auto

# Verbose output
uv run pytest tests/ -v

# Stop on first failure
uv run pytest tests/ -x
```

## Test Categories

Tests are organized using pytest markers:

### Core Markers

- `unit`: Unit tests for individual components
- `integration`: Integration tests for component interactions
- `slow`: Tests that take longer to run or interact with external services

### Functional Markers

- `mcp`: Tests for MCP server functionality
- `tools`: Tests for tool functions
- `api`: Tests for FastAPI endpoints
- `proxy`: Tests for MCP proxy functionality
- `services`: Tests for service layer
- `auth`: Tests requiring authentication

### Specialized Markers

- `environment`: Tests for environment configuration
- `prompts`: Tests for prompts system
- `logging`: Tests for logging functionality
- `performance`: Performance and benchmark tests
- `deployment`: Tests for deployment scenarios

### Example Usage

```bash
# Run only API tests
uv run pytest tests/ -m "api"

# Run unit tests but not slow ones
uv run pytest tests/ -m "unit and not slow"

# Run integration tests with authentication
uv run pytest tests/ -m "integration and auth"
```

## Writing Tests

### Test Structure Guidelines

1. **Use descriptive test names**: Test names should clearly describe what is being tested
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Use appropriate fixtures**: Leverage shared fixtures from `conftest.py`
4. **Mark tests appropriately**: Use pytest markers to categorize tests
5. **Mock external dependencies**: Use mocks for Databricks SDK and external services

### Example Unit Test

```python
"""Example unit test for a tool function."""

import pytest
from unittest.mock import Mock, patch


@pytest.mark.unit
@pytest.mark.tools
class TestExampleTool:
    """Test example tool functionality."""
    
    def test_tool_success(self, mcp_server, mock_databricks_client):
        """Test successful tool execution."""
        from server.tools.example import load_example_tools
        
        # Arrange
        load_example_tools(mcp_server)
        mock_databricks_client.some_method.return_value = 'expected_result'
        
        # Act
        tool = mcp_server.tools['example_tool'].fn
        with patch('server.tools.example.WorkspaceClient', return_value=mock_databricks_client):
            result = tool()
        
        # Assert
        assert result['success'] is True
        assert result['data'] == 'expected_result'
    
    def test_tool_error_handling(self, mcp_server, mock_databricks_client):
        """Test tool error handling."""
        from server.tools.example import load_example_tools
        
        # Arrange
        load_example_tools(mcp_server)
        mock_databricks_client.some_method.side_effect = Exception('Test error')
        
        # Act
        tool = mcp_server.tools['example_tool'].fn
        with patch('server.tools.example.WorkspaceClient', return_value=mock_databricks_client):
            result = tool()
        
        # Assert
        assert result['success'] is False
        assert 'Test error' in result['error']
```

### Example Integration Test

```python
"""Example integration test."""

import pytest


@pytest.mark.integration
@pytest.mark.mcp
class TestMCPWorkflow:
    """Test MCP workflow integration."""
    
    def test_complete_mcp_workflow(self, mcp_server_with_tools, mock_databricks_client):
        """Test complete MCP workflow from tool loading to execution."""
        # Setup mock data
        mock_databricks_client.catalogs.list.return_value = [
            Mock(name='test_catalog', catalog_type='MANAGED')
        ]
        
        # Test tool execution
        with patch('server.tools.unity_catalog.WorkspaceClient', return_value=mock_databricks_client):
            health_tool = mcp_server_with_tools.tools['health'].fn
            health_result = health_tool()
            
            uc_tool = mcp_server_with_tools.tools['list_uc_catalogs'].fn
            uc_result = uc_tool()
        
        # Verify workflow
        assert health_result['status'] == 'healthy'
        assert uc_result['success'] is True
        assert uc_result['count'] == 1
```

### Using Fixtures

The project provides several useful fixtures in `conftest.py`:

```python
def test_with_fixtures(mcp_server, mock_databricks_client, test_client, mock_environment):
    """Example test using multiple fixtures."""
    # mcp_server: Clean MCP server instance
    # mock_databricks_client: Mocked Databricks SDK client
    # test_client: FastAPI test client
    # mock_environment: Test environment variables
    pass
```

## CI/CD Integration

### GitHub Actions

The project includes comprehensive GitHub Actions workflows:

#### Test Workflow (`.github/workflows/test.yml`)

- Runs on Python 3.11 and 3.12
- Executes linting, type checking, unit tests, and integration tests
- Generates coverage reports
- Includes security scanning
- Tests frontend build

#### Deploy Test Workflow (`.github/workflows/deploy-test.yml`)

- Tests deployment build process
- Validates MCP protocol compliance
- Runs performance benchmarks
- Tests Claude CLI integration format

### Local CI Simulation

```bash
# Simulate CI environment locally
make test-ci

# Run the same checks as GitHub Actions
./run_tests.sh --security --verbose
make test-frontend
```

## Configuration

### pytest Configuration

The `pyproject.toml` file contains comprehensive pytest configuration:

```toml
[tool.pytest.ini_options]
addopts = [
    "-v",
    "--tb=short", 
    "--strict-markers",
    "--cov=server",
    "--cov=dba_mcp_proxy",
    "--cov-fail-under=80",
]
testpaths = ["tests"]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow tests",
    # ... more markers
]
```

### Coverage Configuration

Coverage is configured to:

- Track coverage for `server/` and `dba_mcp_proxy/` modules
- Exclude test files and build artifacts
- Generate HTML and terminal reports
- Require minimum 80% coverage

### Environment Setup

Tests use the following environment variables:

```bash
DATABRICKS_HOST=https://test.cloud.databricks.com
DATABRICKS_TOKEN=test-token
TESTING=true
```

These are automatically set by the test runner and CI workflows.

## Troubleshooting

### Common Issues

#### Test Discovery Issues

```bash
# If pytest can't find tests
uv run pytest --collect-only

# Check test path configuration
uv run pytest --help
```

#### Import Errors

```bash
# Ensure dependencies are installed
uv sync --all-extras

# Check Python path
uv run python -c "import sys; print(sys.path)"
```

#### Mock/Fixture Issues

```bash
# Run tests with verbose output to see fixture usage
uv run pytest tests/ -v -s

# Check fixture scope and dependencies
uv run pytest --fixtures tests/
```

#### Coverage Issues

```bash
# Run with coverage debug
uv run pytest tests/ --cov=server --cov-report=term-missing --cov-debug=trace

# Check coverage configuration
uv run coverage report --show-missing
```

### Performance Issues

```bash
# Run tests without parallelization
./run_tests.sh --no-parallel

# Profile test execution
uv run pytest tests/ --durations=10

# Run only fast tests
uv run pytest tests/ -m "not slow"
```

### Debugging Tests

```bash
# Run with debugging output
uv run pytest tests/ -s -vv

# Stop on first failure
uv run pytest tests/ -x

# Run specific test with debugging
uv run pytest tests/unit/test_app.py::TestFastAPIApp::test_app_creation -s -vv
```

## Best Practices

### Test Writing

1. **Keep tests independent**: Each test should be able to run in isolation
2. **Use meaningful assertions**: Assert specific expected values, not just truthiness
3. **Test edge cases**: Include tests for error conditions and boundary cases
4. **Keep tests fast**: Unit tests should run quickly; mark slow tests appropriately
5. **Use appropriate mocking**: Mock external dependencies but not the code under test

### Test Organization

1. **Group related tests**: Use test classes to group related functionality
2. **Use clear file naming**: Follow the `test_*.py` naming convention
3. **Organize by component**: Structure tests to mirror the source code structure
4. **Use appropriate markers**: Mark tests with relevant categories

### CI/CD

1. **Run tests in CI**: Ensure all tests pass before merging
2. **Monitor coverage**: Maintain good test coverage (target: 80%+)
3. **Use parallel execution**: Speed up test runs with parallel execution
4. **Separate fast and slow tests**: Run fast tests first, slow tests separately

## Contributing

When adding new features:

1. **Write tests first**: Consider using TDD (Test-Driven Development)
2. **Update test documentation**: Document any new test patterns or fixtures
3. **Add appropriate markers**: Mark new tests with relevant categories
4. **Consider integration tests**: Add integration tests for new workflows
5. **Update CI**: Modify CI workflows if needed for new test requirements

For more information, see the main project [README.md](../README.md) and [CLAUDE.md](../CLAUDE.md).