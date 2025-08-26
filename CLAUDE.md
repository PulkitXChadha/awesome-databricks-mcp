# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **simplified** Databricks MCP (Model Context Protocol) server that enables AI assistants like Claude to interact with Databricks workspaces. The project has been deliberately simplified to prioritize maintainability and clarity:
- **MCP Server**: FastAPI backend with integrated MCP server using FastMCP
- **Web Interface**: React TypeScript frontend for MCP discovery and testing
- **Modular Tools**: 100+ tools organized across 8 specialized modules for Databricks operations- **OAuth Integration**: Secure authentication via Databricks Apps deployment

## Architecture

The simplified MCP server architecture consists of:
- **FastAPI backend** (`server/app.py`) with integrated MCP server via FastMCP
- **Modular tools system** (`server/tools/`) with specialized modules for different Databricks operations  
- **React frontend** (`client/`) for web-based MCP discovery and testing
- **MCP proxy** (`dba_mcp_proxy/`) for Claude CLI integration with OAuth handling
- **Prompts system** (`prompts/`) where markdown files become MCP prompts

## 🚨 SENIOR DEVELOPER GUIDELINES 🚨

**CRITICAL: This project follows SIMPLE, MAINTAINABLE patterns. DO NOT over-engineer!**

### Code Philosophy
1. **SIMPLE over CLEVER**: Write obvious code that any developer can understand
2. **EXPLICIT over IMPLICIT**: Prefer clear, direct implementations over abstractions
3. **FLAT over NESTED**: Avoid deep inheritance, complex factories, or excessive abstraction layers
4. **FOCUSED over GENERIC**: Write code for the specific use case, not hypothetical future needs

### Forbidden Patterns (DO NOT ADD THESE)
❌ **Abstract base classes** or complex inheritance hierarchies
❌ **Factory patterns** or dependency injection containers
❌ **Decorators for cross-cutting concerns** (logging, caching, performance monitoring)
❌ **Complex configuration classes** with nested structures
❌ **Async/await patterns** unless absolutely necessary
❌ **Connection pooling** or caching layers
❌ **Generic "framework" code** or reusable utilities
❌ **Complex error handling systems** or custom exceptions
❌ **Performance optimization** patterns (premature optimization)
❌ **Enterprise patterns** like singleton, observer, strategy, etc.

### Required Patterns (ALWAYS USE THESE)
✅ **Direct function calls** - no indirection or abstraction layers
✅ **Simple classes** with clear, single responsibilities
✅ **Environment variables** for configuration (no complex config objects)
✅ **Explicit imports** - import exactly what you need
✅ **Basic error handling** with try/catch and simple return dictionaries
✅ **Straightforward control flow** - avoid complex conditional logic
✅ **Standard library first** - only add dependencies when absolutely necessary

### Implementation Rules
1. **One concept per file**: Each module should have a single, clear purpose
2. **Functions over classes**: Prefer functions unless you need state management
3. **Direct SDK calls**: Call Databricks SDK directly, no wrapper layers
4. **Simple data structures**: Use dicts and lists, avoid custom data classes
5. **Basic testing**: Simple unit tests with basic mocking, no complex test frameworks
6. **Minimal dependencies**: Only add new dependencies if critically needed

### Code Review Questions
Before adding any code, ask yourself:
- "Is this the simplest way to solve this problem?"
- "Would a new developer understand this immediately?"
- "Am I adding abstraction for a real need or hypothetical flexibility?"
- "Can I solve this with standard library or existing dependencies?"
- "Does this follow the existing patterns in the codebase?"

### Examples of Good vs Bad Code

**❌ BAD (Over-engineered):**
```python
class AbstractDatabricksClientFactory(ABC):
    @abstractmethod
    def create_client(self) -> WorkspaceClient: ...

class ConfigurableDatabricksClientFactory(AbstractDatabricksClientFactory):
    def __init__(self, config: DatabricksConfig): ...
```

**✅ GOOD (Simple):**
```python
def get_workspace_client() -> WorkspaceClient:
    host = os.getenv('DATABRICKS_HOST')
    token = os.getenv('DATABRICKS_TOKEN')
    return WorkspaceClient(host=host, token=token)
```

**❌ BAD (Complex configuration):**
```python
class DatabaseConfig(BaseModel):
    host: str = Field(..., description="Database host")

class AppConfig(BaseSettings):
    database: DatabaseConfig
    security: SecurityConfig
    monitoring: MonitoringConfig
```

**✅ GOOD (Direct environment variables):**
```python
class Config:
    def __init__(self):
        self.host = os.getenv('DATABRICKS_HOST')
        self.token = os.getenv('DATABRICKS_TOKEN')
```

## Development Commands

### Essential Commands
- `./setup.sh` - Interactive setup for environment, authentication, and dependencies
- `./watch.sh` - Start development servers (backend + frontend + file watching)
- `./fix.sh` - Format code (ruff for Python, prettier for TypeScript)
- `./deploy.sh` - Deploy to Databricks Apps
- `./app_status.sh` - Check deployment status and get app URLs

### Python Execution Rules

**CRITICAL: Always use `uv run` instead of direct `python`:**
```bash
# ✅ CORRECT
uv run python script.py
uv run uvicorn server.app:app

# ❌ WRONG  
python script.py
uvicorn server.app:app
```

### Databricks CLI Rules

**CRITICAL: Always source environment before Databricks CLI:**
```bash
# ✅ CORRECT - Load environment first
source .env.local && export DATABRICKS_HOST && export DATABRICKS_TOKEN && databricks current-user me

# ❌ WRONG - Direct CLI usage
databricks current-user me
```

## Development Workflow

### Starting Development
1. Run `./setup.sh` for first-time setup or configuration changes
2. Run `./watch.sh` to start development servers:
   - Backend: http://localhost:8000 (FastAPI + MCP server)
   - Frontend: http://localhost:5173 (React dev server)
   - MCP endpoint: http://localhost:8000/mcp/
   - API docs: http://localhost:8000/docs

### Making Changes
- **Tools**: Edit functions in `server/tools/*.py` modules
- **Prompts**: Add/edit markdown files in `prompts/` directory
- **Frontend**: Modify React components in `client/src/`
- **Backend**: Update FastAPI routes in `server/routers/`

All changes auto-reload via file watchers in `./watch.sh`.

### Package Management
- **Python**: Use `uv add/remove` for dependencies, never edit pyproject.toml manually
- **Frontend**: Use `bun add/remove` for dependencies, never edit package.json manually
- Always check if dependencies already exist before adding new ones
- **Principle**: Only add dependencies if absolutely critical


## Tool System Architecture

The modular tools system (`server/tools/`) is organized into specialized modules:
- `core.py` - Health checks and basic operations
- `sql_operations.py` - SQL warehouse and query tools
- `unity_catalog.py` - Unity Catalog operations (catalogs, schemas, tables)
- `jobs_pipelines.py` - Job and DLT pipeline management
- `workspace_files.py` - Workspace file operations
- `dashboards.py` - **Comprehensive dashboard management tools** (both Lakeview and legacy)
- `repositories.py` - Git repository integration
- `data_management.py` - DBFS and data operations (commented out)
- `governance.py` - Governance tools (commented out)

### Dashboard Tools Module (`dashboards.py`)

The `dashboards.py` module provides comprehensive tools for building and managing Databricks dashboards programmatically. It supports both modern Lakeview dashboards and legacy dashboard formats with powerful widget creation and management capabilities.

#### Core Dashboard Tools

**Lakeview Dashboard Tools:**
- `list_lakeview_dashboards()` - Enumerate all available Lakeview dashboards
- `get_lakeview_dashboard(dashboard_id)` - Retrieve detailed dashboard configuration  
- `create_lakeview_dashboard(config)` - Build new dashboards with widgets and layouts
- `update_lakeview_dashboard(dashboard_id, updates)` - Modify existing dashboards
- `delete_lakeview_dashboard(dashboard_id)` - Remove dashboards
- `share_lakeview_dashboard(dashboard_id, config)` - Configure dashboard permissions
- `get_dashboard_permissions(dashboard_id)` - View current access settings

#### Dashboard Widget System

The module supports all major widget types for data visualization:

**Chart Widgets:** `counter`, `table`, `bar`, `line`, `pie`, `area`, `scatter`, `pivot`, `funnel`, `box`, `heatmap`
**Text Widgets:** `markdown` for documentation and explanations

#### Widget Creation Patterns

```python
# Example widget configuration following the simple pattern
def create_sales_dashboard():
    """Create a sales dashboard with multiple widget types."""
    
    # KPI counter widget
    revenue_widget = {
        "name": "Total Revenue",
        "type": "counter", 
        "query": "SELECT sum(revenue) as value FROM sales",
        "position": {"x": 0, "y": 0, "width": 3, "height": 2}
    }
    
    # Trend line chart
    trend_widget = {
        "name": "Monthly Revenue Trend",
        "type": "line",
        "query": """
            SELECT 
                date_trunc('month', date) as month,
                sum(revenue) as revenue
            FROM sales 
            GROUP BY 1 ORDER BY 1
        """,
        "position": {"x": 3, "y": 0, "width": 9, "height": 4}
    }
    
    # Simple dashboard structure
    dashboard_config = {
        "name": "Sales Dashboard",
        "widgets": [revenue_widget, trend_widget]
    }
    
    return dashboard_config
```

#### Dashboard Layout System

Dashboards use a **12-column responsive grid** for positioning:
- **X-axis**: 0-11 (left to right)
- **Y-axis**: 0+ (top to bottom) 
- **Width**: 1-12 columns
- **Height**: 2-8 rows (typical)

**Common Layout Patterns:**
```python
# Full width widget
{"x": 0, "y": 0, "width": 12, "height": 4}

# Half width widgets (side by side)  
{"x": 0, "y": 0, "width": 6, "height": 4}
{"x": 6, "y": 0, "width": 6, "height": 4}

# Quarter width widgets (KPI row)
{"x": 0, "y": 0, "width": 3, "height": 2}
{"x": 3, "y": 0, "width": 3, "height": 2}
{"x": 6, "y": 0, "width": 3, "height": 2}
{"x": 9, "y": 0, "width": 3, "height": 2}
```

#### SQL Query Guidelines for Dashboards

**Essential Patterns:**
```sql
-- Use proper aliasing for display
SELECT 
    product_name as "Product",
    sum(quantity) as "Units Sold", 
    sum(revenue) as "Revenue"
FROM sales_detail
GROUP BY 1;

-- Parameterized queries for flexibility
SELECT 
    date_trunc('month', order_date) as month,
    sum(revenue) as total_revenue
FROM sales
WHERE order_date >= :start_date 
  AND order_date <= :end_date
GROUP BY 1 ORDER BY 1;

-- Counter widgets need single numeric value
SELECT count(*) as value FROM customers;
SELECT sum(revenue) as value FROM sales;
```

#### Dashboard Management Best Practices

1. **Start Simple**: Begin with core KPIs, expand iteratively
2. **Consistent Naming**: Use clear, descriptive widget names
3. **Query Optimization**: Use appropriate aggregations and filters
4. **Layout Planning**: Design mobile-responsive layouts
5. **Permission Management**: Set appropriate access controls
6. **Documentation**: Include markdown widgets for context

#### Real-World Dashboard Examples

**Executive Dashboard Pattern:**
```python
# KPIs across the top (4 counters)
# Revenue trend in the middle (full width line chart)
# Department breakdown at bottom (bar chart + table)
```

**Analytics Dashboard Pattern:**
```python
# Customer segmentation (pie chart)
# Cohort analysis (heatmap)  
# Behavior funnel (funnel chart)
# Detailed customer table (filterable)
```

**Operational Dashboard Pattern:**
```python
# System status counters
# Performance trends (multiple line charts)
# Alert summary table
# Resource utilization gauges
```

### Adding New Tools
Tools are automatically registered when added to modules. Follow existing patterns:
```python
def load_module_tools(mcp_server):
    """Register tools from this module."""
    
    @mcp_server.tool
    def your_new_tool(param: str) -> dict:
        """Tool description for Claude."""
        # Implementation using Databricks SDK
        return {"result": "data"}
```

**Key principles:**
- Direct Databricks SDK calls (no wrappers)
- Simple error handling with try/catch
- Return dictionaries with consistent structure
- No decorators, no abstractions, no magic

## MCP Integration

### Local Development Testing
```bash
# Test MCP server directly
./claude_scripts/test_local_mcp_curl.sh

# Test with MCP proxy
./claude_scripts/test_local_mcp_proxy.sh  

# Web-based MCP Inspector
./claude_scripts/inspect_local_mcp.sh
```

### Production Testing
```bash
# Test deployed MCP server
./claude_scripts/test_remote_mcp_curl.sh

# Test with production proxy
./claude_scripts/test_remote_mcp_proxy.sh

# Remote MCP Inspector
./claude_scripts/inspect_remote_mcp.sh
```

### Claude CLI Integration
After deployment, add to Claude CLI:
```bash
# Get app URL from ./app_status.sh
export DATABRICKS_APP_URL="https://your-app.databricksapps.com"
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"

# Add MCP server to Claude
claude mcp add databricks-mcp -- \
  uvx --from git+https://git@github.com/YOUR-USERNAME/YOUR-REPO.git dba-mcp-proxy \
  --databricks-host $DATABRICKS_HOST \
  --databricks-app-url $DATABRICKS_APP_URL
```

## Authentication

### Local Development
- Uses Databricks CLI credentials (PAT or profile-based)
- Environment variables loaded from `.env.local`
- No OAuth required for local testing

### Production Deployment
- OAuth handled automatically via Databricks Apps
- Proxy manages authentication flow
- Users authenticate through their Databricks workspace

## Code Quality

### Formatting and Linting
- Python: `ruff` for formatting and linting
- TypeScript: `prettier` for formatting, ESLint for linting
- Run `./fix.sh` before commits to format all code

### Type Checking
- Python: Uses `ty` for type checking
- TypeScript: Built-in TypeScript compiler

## Testing

### Running Tests

#### Python Tests
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_basic_functionality.py

# Run single test
uv run pytest tests/test_e2e_examples.py::test_specific_function

# Run tests by marker
uv run pytest -m unit        # Unit tests only
uv run pytest -m integration # Integration tests
uv run pytest -m e2e         # End-to-end tests
uv run pytest -m "not slow"  # Skip slow tests

# Run with coverage
uv run pytest --cov=server --cov-report=html
```

#### Frontend Tests
```bash
cd client
bun run lint    # Lint TypeScript code
bun run format  # Format with prettier
```

### Comprehensive Testing Suite
The `claude_scripts/` directory contains testing tools:
- **curl tests**: Direct HTTP testing with session handling
- **proxy tests**: End-to-end MCP proxy testing  
- **MCP Inspector**: Web-based interactive testing UI
- **Tool-specific tests**: Individual tool validation scripts

### API Testing
- FastAPI docs interface: http://localhost:8000/docs
- Manual curl testing for endpoints
- Network tab in browser dev tools for frontend API calls

## Deployment

### Deploying to Databricks Apps
```bash
./deploy.sh
```

This automatically:
- Builds React frontend for production
- Generates Python requirements.txt from pyproject.toml
- Creates app.yaml configuration
- Deploys via Databricks CLI
- Verifies deployment status

### Post-Deployment
- Check status: `./app_status.sh`
- Monitor logs: Visit deployed app URL + `/logz` 
- Test MCP functionality with remote testing scripts

## Configuration Files

### Key Configuration
- `.env.local` - Local development environment variables
- `config.yaml` - MCP server name configuration
- `pyproject.toml` - Python dependencies and project metadata
- `client/package.json` - Frontend dependencies and scripts
- `app.yaml` - Databricks Apps deployment configuration

### Environment Variables
Essential variables in `.env.local`:
```bash
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-token  # For PAT auth
DATABRICKS_CONFIG_PROFILE=DEFAULT  # For profile auth
DATABRICKS_APP_NAME=your-app-name
DBA_SOURCE_CODE_PATH=/Workspace/Users/email/app-name
```

## Troubleshooting

### Common Issues
- **Authentication failures**: Run `databricks auth login` or check `.env.local` configuration
- **MCP connection issues**: Verify app deployment with `./app_status.sh`
- **TypeScript client not found**: Auto-generated by `./watch.sh`, check logs
- **Port conflicts**: Default ports 8000 (backend) and 5173 (frontend)

### Debug Commands
```bash
# Check development server logs
tail -f /tmp/databricks-app-watch.log

# Test Databricks connection
source .env.local && databricks current-user me

# Verify MCP endpoint
curl http://localhost:8000/mcp/

# Check Claude MCP integration
echo "What MCP prompts are available from databricks-mcp?" | claude
```

## Simplified Testing

### Basic Testing Suite

The project includes a **focused** test suite with essential tests only:
- **Unit Tests**: Basic component testing with simple mocks
- **Tool Tests**: Individual MCP tool functionality
- **API Tests**: Basic FastAPI endpoint testing

### Running Tests

```bash
# Run all tests (simple and fast)
make test

# Or directly with uv
uv run pytest tests/ -v
```

### Test Structure

Tests use minimal pytest configuration:
- **9 test files** covering core functionality
- **Basic markers**: unit, tools, integration
- **Simple fixtures**: Basic mocking utilities only
- **No coverage requirements**: Focus on functionality, not metrics

### Writing Tests

Follow the **simple pattern**:
```python
def test_your_feature(mcp_server, mock_env_vars):
    """Test your feature."""
    # Load tools
    load_tools(mcp_server)

    # Mock Databricks SDK calls
    with patch('server.tools.module.get_workspace_client') as mock_client:
        mock_client.return_value.some_api.method.return_value = expected_data

        # Test the tool
        tool = mcp_server._tools['tool_name']
        result = tool.func()

        # Basic assertions
        assert result['status'] == 'success'
```

**Testing principles:**
- Keep tests simple and focused
- Mock external dependencies (Databricks SDK)
- Test success and error cases only
- No complex test infrastructure or frameworks

## Summary: What Makes This Project "Senior Developer Approved"

✅ **Readable**: Any developer can understand the code immediately
✅ **Maintainable**: Simple patterns that are easy to modify
✅ **Focused**: Each module has a single, clear responsibility
✅ **Direct**: No unnecessary abstractions or indirection
✅ **Practical**: Solves the specific problem without over-engineering

When in doubt, choose the **simpler** solution. Your future self (and your teammates) will thank you.

---

# Important Instruction Reminders

**For Claude Code when working on this project:**

1. **Do what has been asked; nothing more, nothing less**
2. **NEVER create files unless absolutely necessary for achieving the goal**
3. **ALWAYS prefer editing an existing file to creating a new one**
4. **NEVER proactively create documentation files (*.md) or README files**
5. **Follow the SIMPLE patterns established in this codebase**
6. **When in doubt, ask "Is this the simplest way?" before implementing**

This project is intentionally simplified. **Respect that simplicity.**

- /clear
