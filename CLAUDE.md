# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Databricks MCP (Model Context Protocol) server that enables AI assistants like Claude to interact with Databricks workspaces. It's built as a hybrid application combining:
- **MCP Server**: FastAPI backend with integrated MCP server using FastMCP
- **Web Interface**: React TypeScript frontend for MCP discovery and testing
- **Modular Tools**: 100+ tools organized across 8 specialized modules for Databricks operations
- **OAuth Integration**: Secure authentication via Databricks Apps deployment

## Architecture

The MCP server architecture consists of:
- **FastAPI backend** (`server/app.py`) with integrated MCP server via FastMCP
- **Modular tools system** (`server/tools/`) with specialized modules for different Databricks operations  
- **React frontend** (`client/`) for web-based MCP discovery and testing
- **MCP proxy** (`dba_mcp_proxy/`) for Claude CLI integration with OAuth handling
- **Prompts system** (`prompts/`) where markdown files become MCP prompts

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

## Tool System Architecture

The modular tools system (`server/tools/`) is organized into specialized modules:
- `core.py` - Health checks and basic operations
- `sql_operations.py` - SQL warehouse and query tools
- `unity_catalog.py` - Unity Catalog operations (catalogs, schemas, tables)
- `jobs_pipelines.py` - Job and DLT pipeline management
- `workspace_files.py` - Workspace file operations
- `dashboards.py` - Dashboard management tools
- `repositories.py` - Git repository integration
- `data_management.py` - DBFS and data operations (commented out)
- `governance.py` - Governance tools (commented out)

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
  uvx --from git+ssh://git@github.com/YOUR-USERNAME/YOUR-REPO.git dba-mcp-proxy \
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

## Documentation

Reference documentation in `docs/` directory:
- `docs/databricks_apis/` - Databricks SDK integration guides
- `docs/unity_catalog_tools.md` - Unity Catalog operations reference
- `docs/core-tools.md` - Core tool documentation
- `claude_scripts/README.md` - Testing tools documentation