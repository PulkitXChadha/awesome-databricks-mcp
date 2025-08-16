# Databricks MCP Server - Refactoring Recommendations

## Executive Summary

This document provides comprehensive refactoring recommendations for the awesome-databricks-mcp project based on a thorough analysis of the codebase, architecture, and development practices. The project demonstrates good architectural patterns but has opportunities for improvement in areas including code organization, testing, error handling, security, and developer experience.

## Project Analysis Overview

### Strengths
- **Clear modular architecture** with separation of concerns between backend (FastAPI), frontend (React), and MCP proxy
- **Well-organized tool system** with logical module separation
- **Comprehensive documentation** and setup scripts
- **Modern technology stack** using FastMCP, FastAPI, React with TypeScript
- **Proper OAuth authentication** handling via Databricks Apps
- **Good deployment automation** with shell scripts
- **Extensive testing infrastructure** with multiple testing approaches

### Areas for Improvement
- **Limited unit test coverage** for core business logic
- **Inconsistent error handling** patterns across modules
- **Security hardening** opportunities
- **Code duplication** in authentication and configuration loading
- **Performance optimization** potential
- **Developer experience** enhancements

## 1. Code Organization & Architecture

### 1.1 Dependency Management Improvements

**Current Issues:**
- Manual requirements.txt generation script could be unreliable
- Mixed use of `uv` and `pip` instructions in documentation
- Version conflicts potential with Databricks pre-installed packages

**Recommendations:**
```python
# pyproject.toml - Improve dependency constraints
[project]
dependencies = [
    "fastapi>=0.104.1,<0.120.0",  # More specific version ranges
    "databricks-sdk>=0.59.0,<1.0.0",  # Prevent major version conflicts
    "pydantic>=2.5.0,<3.0.0",
    # Add dependency groups for better organization
]

[dependency-groups]
server = ["fastapi", "uvicorn", "databricks-sdk"]
mcp = ["fastmcp", "mcp"]
dev = ["ruff", "pytest", "httpx"]
test = ["pytest", "pytest-asyncio", "httpx"]
```

**Implementation:**
1. Consolidate on `uv` as the primary dependency manager
2. Create dependency groups for different use cases
3. Replace custom requirements.txt generation with `uv export`
4. Add dependency vulnerability scanning

### 1.2 Configuration Management

**Current Issues:**
- Environment variable loading scattered across files
- No validation for required configuration
- Hard-coded fallback values

**Recommended Structure:**
```python
# server/config.py
from pydantic import BaseSettings, validator
from typing import Optional

class DatabaseConfig(BaseSettings):
    host: str
    token: Optional[str] = None
    config_profile: Optional[str] = None
    sql_warehouse_id: Optional[str] = None
    
    @validator('host')
    def validate_host(cls, v):
        if not v.startswith('https://'):
            raise ValueError('Host must be HTTPS URL')
        return v

class AppConfig(BaseSettings):
    app_name: str = "databricks-mcp"
    port: int = 8000
    debug: bool = False
    
    databricks: DatabaseConfig = DatabaseConfig()
    
    class Config:
        env_file = [".env", ".env.local"]
        env_nested_delimiter = "_"

# Usage throughout app
from server.config import AppConfig
config = AppConfig()
```

### 1.3 Error Handling Standardization

**Current Issues:**
- Inconsistent error response formats across tools
- Missing error logging and monitoring
- No centralized exception handling

**Recommended Approach:**
```python
# server/exceptions.py
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MCPError(Exception):
    """Base exception for MCP operations."""
    def __init__(self, message: str, error_code: str = "INTERNAL_ERROR", details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)

class DatabricksAPIError(MCPError):
    """Databricks API specific errors."""
    pass

# server/error_handler.py
def create_error_response(error: Exception) -> dict:
    """Standardize error responses across all tools."""
    if isinstance(error, MCPError):
        return {
            "success": False,
            "error": error.message,
            "error_code": error.error_code,
            "details": error.details
        }
    
    logger.exception("Unhandled exception in MCP tool")
    return {
        "success": False,
        "error": "Internal server error",
        "error_code": "INTERNAL_ERROR"
    }

# Decorator for tools
def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return create_error_response(e)
    return wrapper
```

## 2. Testing Strategy Improvements

### 2.1 Unit Testing Framework

**Current State:** Limited to integration testing with `claude_scripts/`

**Recommended Structure:**
```
tests/
├── unit/
│   ├── test_config.py
│   ├── test_tools/
│   │   ├── test_core.py
│   │   ├── test_unity_catalog.py
│   │   └── test_sql_operations.py
│   └── test_utils.py
├── integration/
│   ├── test_mcp_server.py
│   └── test_databricks_api.py
├── fixtures/
│   ├── mock_responses.py
│   └── test_data.py
└── conftest.py
```

**Implementation Example:**
```python
# tests/unit/test_tools/test_unity_catalog.py
import pytest
from unittest.mock import Mock, patch
from server.tools.unity_catalog import load_uc_tools

@pytest.fixture
def mock_workspace_client():
    return Mock()

@pytest.fixture
def mcp_server():
    return Mock()

def test_list_uc_catalogs_success(mock_workspace_client, mcp_server):
    # Setup mock
    mock_workspace_client.catalogs.list.return_value = [
        Mock(name="catalog1", comment="Test catalog")
    ]
    
    # Load tools and get function
    load_uc_tools(mcp_server)
    list_catalogs_fn = mcp_server.tool.call_args_list[0][0][0]
    
    # Test
    with patch('server.tools.unity_catalog.get_workspace_client', return_value=mock_workspace_client):
        result = list_catalogs_fn()
    
    assert result["success"] is True
    assert result["count"] == 1
    assert result["catalogs"][0]["name"] == "catalog1"

# tests/conftest.py
import pytest
import os
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        'DATABRICKS_HOST': 'https://test.databricks.com',
        'DATABRICKS_TOKEN': 'test-token'
    }
    with patch.dict(os.environ, env_vars):
        yield
```

### 2.2 Integration Testing Enhancement

**Current Issues:**
- Manual testing scripts without automated verification
- No CI/CD integration
- Limited test coverage reporting

**Recommendations:**
```python
# tests/integration/test_mcp_server.py
import pytest
import httpx
from fastapi.testclient import TestClient
from server.app import app

@pytest.fixture
def client():
    return TestClient(app)

def test_mcp_endpoint_health(client):
    """Test MCP server health endpoint."""
    response = client.get("/mcp/")
    assert response.status_code == 200
    
def test_mcp_tools_discovery(client):
    """Test MCP tools are properly registered."""
    # Test implementation
    pass

# Add to pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = [
    "--cov=server",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=80"
]
```

## 3. Security Enhancements

### 3.1 Input Validation & Sanitization

**Current Issues:**
- Direct parameter passing to Databricks SDK without validation
- No input sanitization for SQL queries
- Missing rate limiting

**Recommendations:**
```python
# server/validation.py
from pydantic import BaseModel, validator, Field
from typing import Optional, List
import re

class TableIdentifier(BaseModel):
    """Validate table identifiers."""
    catalog: str = Field(..., regex=r'^[a-zA-Z][a-zA-Z0-9_]*$')
    schema: str = Field(..., regex=r'^[a-zA-Z][a-zA-Z0-9_]*$')
    table: str = Field(..., regex=r'^[a-zA-Z][a-zA-Z0-9_]*$')
    
    @property
    def full_name(self) -> str:
        return f"{self.catalog}.{self.schema}.{self.table}"

class SQLQuery(BaseModel):
    """Validate SQL queries."""
    query: str = Field(..., max_length=10000)
    warehouse_id: Optional[str] = Field(None, regex=r'^[a-f0-9\-]+$')
    
    @validator('query')
    def validate_sql(cls, v):
        # Basic SQL injection prevention
        forbidden_patterns = [
            r';\s*(drop|delete|truncate|alter)\s+',
            r'--',
            r'/\*.*\*/',
            r'xp_cmdshell',
            r'sp_executesql'
        ]
        for pattern in forbidden_patterns:
            if re.search(pattern, v.lower()):
                raise ValueError(f'Potentially dangerous SQL pattern detected')
        return v

# Usage in tools
@handle_errors
def describe_uc_table(table_name: str, include_lineage: bool = False) -> dict:
    # Validate input
    try:
        parts = table_name.split('.')
        if len(parts) != 3:
            raise ValueError("Table name must be in format: catalog.schema.table")
        
        table_id = TableIdentifier(
            catalog=parts[0],
            schema=parts[1], 
            table=parts[2]
        )
    except Exception as e:
        raise MCPError(f"Invalid table identifier: {e}", "VALIDATION_ERROR")
    
    # Continue with validated input
    w = get_workspace_client()
    # ... rest of implementation
```

### 3.2 Authentication & Authorization Improvements

**Current Issues:**
- Token handling in proxy could be more secure
- No token refresh mechanism
- Limited audit logging

**Recommendations:**
```python
# server/auth.py
import time
import logging
from typing import Optional
from databricks.sdk import WorkspaceClient
from server.config import AppConfig

logger = logging.getLogger(__name__)

class TokenManager:
    """Manage Databricks authentication tokens."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self._client: Optional[WorkspaceClient] = None
        self._token_expires_at: Optional[float] = None
    
    def get_client(self) -> WorkspaceClient:
        """Get authenticated Databricks client with token refresh."""
        if self._client is None or self._is_token_expired():
            self._refresh_client()
        return self._client
    
    def _is_token_expired(self) -> bool:
        """Check if current token is expired."""
        if self._token_expires_at is None:
            return True
        return time.time() >= self._token_expires_at
    
    def _refresh_client(self):
        """Refresh the Databricks client."""
        logger.info("Refreshing Databricks client")
        self._client = WorkspaceClient(
            host=self.config.databricks.host,
            token=self.config.databricks.token
        )
        # Set expiration (tokens typically last 1 hour)
        self._token_expires_at = time.time() + 3300  # 55 minutes

# Usage in tools
from server.auth import TokenManager
token_manager = TokenManager(config)

def get_workspace_client() -> WorkspaceClient:
    return token_manager.get_client()
```

### 3.3 Rate Limiting & Resource Protection

**Recommendations:**
```python
# server/middleware.py
from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# Add to app.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to sensitive endpoints
@app.post("/api/execute-sql")
@limiter.limit("10/minute")
async def execute_sql(request: Request, query: SQLQuery):
    # Implementation
    pass
```

## 4. Performance Optimizations

### 4.1 Caching Strategy

**Current Issues:**
- No caching for expensive operations
- Repeated API calls for metadata
- No connection pooling

**Recommendations:**
```python
# server/cache.py
from functools import wraps
import asyncio
from typing import Any, Dict, Optional
import time

class TTLCache:
    """Simple TTL cache implementation."""
    
    def __init__(self, default_ttl: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            entry = self.cache[key]
            if time.time() < entry['expires']:
                return entry['value']
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        ttl = ttl or self.default_ttl
        self.cache[key] = {
            'value': value,
            'expires': time.time() + ttl
        }

# Global cache instance
cache = TTLCache()

def cached(ttl: int = 300):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator

# Usage in tools
@cached(ttl=600)  # Cache for 10 minutes
def list_uc_catalogs() -> dict:
    # Implementation
    pass
```

### 4.2 Async Operations

**Current Issues:**
- Synchronous operations block the event loop
- No parallel processing for multiple requests

**Recommendations:**
```python
# server/tools/async_unity_catalog.py
import asyncio
from typing import List, Dict, Any
from databricks.sdk.service.catalog import CatalogInfo

async def list_uc_catalogs_async() -> dict:
    """Async version of list_uc_catalogs."""
    loop = asyncio.get_event_loop()
    w = get_workspace_client()
    
    # Run blocking operation in thread pool
    catalogs = await loop.run_in_executor(None, lambda: list(w.catalogs.list()))
    
    return {
        "success": True,
        "count": len(catalogs),
        "catalogs": [{"name": c.name, "comment": c.comment} for c in catalogs]
    }

async def batch_describe_schemas(catalog_names: List[str]) -> Dict[str, Any]:
    """Describe multiple schemas in parallel."""
    tasks = [describe_uc_catalog_async(name) for name in catalog_names]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return {
        name: result for name, result in zip(catalog_names, results)
        if not isinstance(result, Exception)
    }
```

## 5. Developer Experience Improvements

### 5.1 Enhanced Development Tooling

**Current Issues:**
- Limited debugging capabilities
- No hot reloading for Python changes
- Manual testing workflows

**Recommendations:**

1. **Enhanced Development Scripts:**
```bash
# watch.sh improvements
#!/bin/bash
# Add Python debugger support
export PYTHONPATH="${PYTHONPATH}:."
export DATABRICKS_DEBUG=true

# Start with debugger support
uv run uvicorn server.app:app --reload --host 0.0.0.0 --port 8000 \
  --log-level debug --access-log --reload-dir server
```

2. **VS Code Configuration:**
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug MCP Server",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": ["server.app:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            "envFile": "${workspaceFolder}/.env.local",
            "console": "integratedTerminal"
        }
    ]
}

// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "ruff"
}
```

### 5.2 Documentation Improvements

**Current Issues:**
- API documentation could be more comprehensive
- Missing architecture diagrams
- Limited troubleshooting guides

**Recommendations:**

1. **Enhanced API Documentation:**
```python
# server/app.py - Improve FastAPI docs
app = FastAPI(
    title='Databricks MCP Server',
    description='Model Context Protocol server for Databricks operations',
    version='0.2.0',
    docs_url='/docs',
    redoc_url='/redoc',
    openapi_tags=[
        {"name": "MCP", "description": "Model Context Protocol endpoints"},
        {"name": "Tools", "description": "Databricks operation tools"},
        {"name": "Health", "description": "Health check endpoints"}
    ]
)
```

2. **Architecture Documentation:**
```markdown
# docs/architecture/README.md
# Architecture Overview

## System Components
[Detailed architecture documentation with diagrams]

## Data Flow
[Request/response flow diagrams]

## Security Model
[Authentication and authorization flow]
```

## 6. Deployment & DevOps Improvements

### 6.1 CI/CD Pipeline

**Current Issues:**
- No automated testing in CI
- Manual deployment process
- No deployment validation

**Recommended GitHub Actions:**
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install uv
        run: pip install uv
      - name: Install dependencies
        run: uv sync
      - name: Run tests
        run: uv run pytest
      - name: Run linting
        run: uv run ruff check .
      - name: Type checking
        run: uv run mypy server/

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run security scan
        run: |
          pip install safety bandit
          safety check
          bandit -r server/

  deploy:
    needs: [test, security]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Databricks
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
        run: ./deploy.sh --verbose
```

### 6.2 Monitoring & Observability

**Current Issues:**
- Limited logging structure
- No metrics collection
- No health monitoring

**Recommendations:**
```python
# server/monitoring.py
import logging
import time
from functools import wraps
from typing import Dict, Any
import structlog

# Structured logging setup
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def monitor_performance(func):
    """Monitor function performance and log metrics."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            success = result.get('success', True) if isinstance(result, dict) else True
            logger.info(
                "tool_execution",
                tool=func.__name__,
                duration=time.time() - start_time,
                success=success
            )
            return result
        except Exception as e:
            logger.error(
                "tool_error",
                tool=func.__name__,
                duration=time.time() - start_time,
                error=str(e)
            )
            raise
    return wrapper

# Health check endpoint with detailed status
@app.get("/health")
async def detailed_health():
    """Comprehensive health check."""
    checks = {
        "databricks_connection": check_databricks_connection(),
        "mcp_server": check_mcp_server_status(),
        "cache_status": check_cache_health()
    }
    
    overall_health = all(checks.values())
    
    return {
        "status": "healthy" if overall_health else "unhealthy",
        "timestamp": time.time(),
        "checks": checks
    }
```

## 7. Implementation Priority & Timeline

### Phase 1 (Weeks 1-2): Foundation
1. **Configuration Management** - Centralize config with Pydantic
2. **Error Handling** - Standardize error responses across all tools
3. **Unit Testing** - Add basic unit tests for core functionality
4. **Security** - Input validation and basic rate limiting

### Phase 2 (Weeks 3-4): Enhancement
1. **Caching** - Implement TTL cache for expensive operations
2. **Async Operations** - Convert blocking operations to async
3. **Monitoring** - Add structured logging and metrics
4. **CI/CD** - Implement automated testing pipeline

### Phase 3 (Weeks 5-6): Optimization
1. **Performance** - Database connection pooling and optimization
2. **Documentation** - Enhanced API docs and architecture guides
3. **Advanced Security** - Token management and audit logging
4. **Developer Experience** - Improved debugging and development tools

## 8. Breaking Changes & Migration Guide

### Configuration Changes
- Move from manual environment loading to Pydantic models
- Centralize all configuration in `server/config.py`

### API Response Format Standardization
- All tool responses will follow consistent format:
```json
{
  "success": boolean,
  "data": object,
  "error": string (optional),
  "error_code": string (optional)
}
```

### Tool Function Signatures
- Add input validation decorators to all tools
- Standardize parameter naming conventions

## Conclusion

These refactoring recommendations will significantly improve the awesome-databricks-mcp project's maintainability, security, performance, and developer experience. The phased approach ensures minimal disruption while delivering incremental value. Focus should be on the foundation phase first, as it provides the groundwork for all subsequent improvements.

The project already demonstrates excellent architectural patterns and comprehensive documentation. These recommendations build upon those strengths to create a more robust, scalable, and maintainable codebase.