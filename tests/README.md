# Tests Directory

This directory contains the comprehensive test suite for the Databricks MCP Server project.

## Quick Start

```bash
# Run all tests
make test

# Or use the test runner
./run_tests.sh

# Run specific test categories
make test-unit
make test-integration
make test-api
```

## Directory Structure

```
tests/
├── conftest.py                 # Shared fixtures and test configuration
├── unit/                       # Unit tests (test individual components)
│   ├── test_app.py            # FastAPI application tests
│   ├── test_mcp_proxy.py      # MCP proxy functionality tests
│   ├── tools/                 # Tool module tests
│   │   ├── test_core.py       # Core tools (health check, etc.)
│   │   ├── test_unity_catalog.py    # Unity Catalog tools
│   │   ├── test_sql_operations.py  # SQL operation tools
│   │   ├── test_dashboards.py      # Dashboard tools
│   │   └── test_tools_loading.py   # Tool loading system
│   ├── routers/               # FastAPI router tests
│   │   ├── test_user.py       # User endpoint tests
│   │   ├── test_mcp_info.py   # MCP info endpoint tests
│   │   ├── test_prompts.py    # Prompts endpoint tests
│   │   └── test_router_init.py # Router initialization tests
│   └── services/              # Service layer tests
└── integration/               # Integration tests (test component interactions)
    ├── test_mcp_server_integration.py    # End-to-end MCP workflows
    └── test_services_integration.py      # Service integration tests
```

## Test Categories

Tests are organized using pytest markers:

### Primary Categories
- `unit`: Fast, isolated component tests
- `integration`: Tests that verify component interactions
- `slow`: Tests that take longer or interact with external services

### Functional Categories
- `mcp`: MCP protocol and server functionality
- `tools`: Databricks tool functions
- `api`: FastAPI HTTP endpoints
- `proxy`: MCP proxy functionality
- `services`: Service layer components

### Specialized Categories
- `auth`: Tests requiring authentication
- `environment`: Environment configuration tests
- `performance`: Performance and benchmark tests
- `deployment`: Deployment scenario tests

## Running Specific Tests

### By Category
```bash
# Unit tests only
uv run pytest tests/unit/

# Integration tests only
uv run pytest tests/integration/

# API-related tests
uv run pytest tests/ -m "api"

# Tool-related tests
uv run pytest tests/ -m "tools"
```

### By Component
```bash
# Test specific modules
uv run pytest tests/unit/tools/test_unity_catalog.py
uv run pytest tests/unit/routers/test_user.py

# Test specific classes
uv run pytest tests/unit/test_app.py::TestFastAPIApp

# Test specific functions
uv run pytest tests/unit/tools/test_core.py::TestCoreTools::test_health_tool_returns_correct_structure
```

### With Options
```bash
# Verbose output
uv run pytest tests/ -v

# Stop on first failure
uv run pytest tests/ -x

# Run in parallel
uv run pytest tests/ -n auto

# With coverage
uv run pytest tests/ --cov=server --cov=dba_mcp_proxy
```

## Key Fixtures

The `conftest.py` file provides several important fixtures:

### Core Fixtures
- `mcp_server`: Clean MCP server instance
- `mcp_server_with_tools`: MCP server with all tools loaded
- `mock_databricks_client`: Mocked Databricks SDK client
- `test_client`: FastAPI test client

### Environment Fixtures
- `mock_environment`: Test environment variables
- `mock_file_system`: Temporary file system for testing
- `mock_requests`: Mocked HTTP requests

### Data Fixtures
- `sample_catalog_data`: Sample Unity Catalog data
- `sample_sql_query_result`: Sample SQL query results

### Example Usage
```python
def test_example(mcp_server, mock_databricks_client):
    """Example test using fixtures."""
    # mcp_server is a clean FastMCP instance
    # mock_databricks_client is pre-configured with common mocks
    pass
```

## Writing New Tests

### Test File Naming
- Unit tests: `test_<component>.py`
- Integration tests: `test_<workflow>_integration.py`
- Place in appropriate subdirectory (`unit/` or `integration/`)

### Test Class and Function Naming
```python
@pytest.mark.unit
@pytest.mark.tools
class TestNewComponent:
    """Test new component functionality."""
    
    def test_component_success_case(self):
        """Test successful operation."""
        pass
    
    def test_component_error_handling(self):
        """Test error handling."""
        pass
```

### Required Markers
Always mark your tests appropriately:
```python
@pytest.mark.unit           # or @pytest.mark.integration
@pytest.mark.tools          # functional category
class TestExample:
    pass
```

### Common Patterns

#### Testing Tools
```python
def test_tool_function(self, mcp_server, mock_databricks_client):
    """Test a tool function."""
    from server.tools.example import load_example_tools
    
    # Load tools
    load_example_tools(mcp_server)
    
    # Configure mock
    mock_databricks_client.some_method.return_value = 'expected'
    
    # Execute tool
    tool = mcp_server.tools['example_tool'].fn
    with patch('server.tools.example.WorkspaceClient', return_value=mock_databricks_client):
        result = tool()
    
    # Verify result
    assert result['success'] is True
```

#### Testing API Endpoints
```python
def test_api_endpoint(self, test_client):
    """Test an API endpoint."""
    response = test_client.get('/api/example')
    
    assert response.status_code == 200
    data = response.json()
    assert 'expected_field' in data
```

#### Testing Error Conditions
```python
def test_error_handling(self, mcp_server, mock_databricks_client):
    """Test error handling."""
    mock_databricks_client.method.side_effect = Exception('Test error')
    
    # Execute and verify error response
    result = some_function()
    assert result['success'] is False
    assert 'Test error' in result['error']
```

## Mocking Guidelines

### Databricks SDK
Always mock the Databricks SDK client:
```python
with patch('module.WorkspaceClient', return_value=mock_databricks_client):
    # Test code here
```

### HTTP Requests
Use the `mock_requests` fixture:
```python
def test_with_http(self, mock_requests):
    mock_requests['get'].return_value.status_code = 200
    # Test code here
```

### File System
Use temporary directories for file tests:
```python
def test_file_operations(self, tmp_path, monkeypatch):
    test_file = tmp_path / 'test.txt'
    test_file.write_text('content')
    monkeypatch.chdir(tmp_path)
    # Test code here
```

## Performance Considerations

### Fast Tests
- Keep unit tests fast (< 1 second each)
- Mock all external dependencies
- Use minimal setup/teardown

### Slow Tests
- Mark slow tests with `@pytest.mark.slow`
- These run separately in CI
- Include actual external service tests here

### Parallel Execution
- Tests should be independent and parallelizable
- Avoid shared state between tests
- Use unique identifiers for test data

## Debugging Tests

### Running Single Tests
```bash
# Run specific test with output
uv run pytest tests/unit/test_app.py::TestFastAPIApp::test_app_creation -s -vv

# With debugger
uv run pytest tests/unit/test_app.py::test_function --pdb
```

### Common Debug Commands
```bash
# Show test collection
uv run pytest --collect-only

# Show available fixtures
uv run pytest --fixtures

# Show test durations
uv run pytest --durations=10

# Coverage debug
uv run pytest --cov-report=term-missing
```

## Coverage Requirements

- Minimum coverage: 80%
- Unit tests should cover all critical paths
- Integration tests should cover main workflows
- Add `# pragma: no cover` only for truly untestable code

## Contributing Guidelines

When adding tests:

1. **Follow existing patterns**: Look at similar tests for guidance
2. **Use appropriate fixtures**: Leverage existing fixtures from `conftest.py`
3. **Mark tests correctly**: Use proper pytest markers
4. **Test both success and failure cases**
5. **Keep tests independent**: Each test should be runnable in isolation
6. **Document complex test logic**: Add comments for non-obvious test setup

## CI Integration

Tests run automatically in GitHub Actions:
- Pull requests: All tests except slow ones
- Main branch: All tests including slow ones
- Security scans and performance benchmarks on main branch

Local CI simulation:
```bash
make test-ci
```

For more detailed information, see [docs/testing.md](../docs/testing.md).