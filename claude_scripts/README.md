# Claude Scripts

This folder contains test scripts for validating MCP (Model Context Protocol) functionality.

## Purpose

These scripts test:
- Local and remote MCP server connectivity
- MCP protocol compliance and tool discovery
- OAuth authentication flows
- Direct HTTP API calls vs MCP proxy routing

## Test Scripts

### Local MCP Testing

**`test_local_mcp_curl.sh`**
Tests local MCP server using direct curl commands.
- Checks if local server is running on http://localhost:8000
- Tests MCP tools/list endpoint
- Validates tool execution (health check)
- Provides clear error messages if server is not running

**`test_local_mcp_proxy.sh`** 
Tests local MCP server using the MCP proxy client.
- Uses `dba_mcp_proxy/mcp_client.py` for MCP protocol handling
- Tests tool discovery through proxy
- Validates MCP session management
- No authentication required for local testing

### Remote MCP Testing

**`test_remote_mcp_curl.sh`**
Tests remote MCP server using direct curl commands with OAuth.
- Automatically retrieves OAuth token from Databricks CLI
- Dynamically discovers app URL from Databricks Apps API
- Tests deployed Databricks App MCP endpoints
- Validates authentication and tool execution

**`test_remote_mcp_proxy.sh`**
Tests remote MCP server using the MCP proxy client.
- Dynamically discovers app URL using Databricks CLI
- Uses optimized token caching and validation
- Tests OAuth flow with automatic refresh
- Validates end-to-end MCP proxy functionality

### Interactive Testing

**`inspect_local_mcp.sh`**
Launches MCP Inspector web UI for interactive local server testing.
- Opens browser-based MCP Inspector interface
- Provides visual tool testing and debugging
- Real-time interaction with MCP server
- No authentication required for local testing

**`inspect_remote_mcp.sh`**
Launches MCP Inspector web UI for interactive remote server testing.
- Dynamically discovers app URL from Databricks Apps API
- Handles OAuth authentication automatically through proxy
- Full-featured web interface for testing all MCP functionality
- Interactive tool execution and debugging

## Usage

### Command Line Tests
Run tests from the project root directory:

```bash
# Test local MCP server (requires ./watch.sh to be running)
./claude_scripts/test_local_mcp_curl.sh
./claude_scripts/test_local_mcp_proxy.sh

# Test remote MCP server (requires Databricks auth)
./claude_scripts/test_remote_mcp_curl.sh
./claude_scripts/test_remote_mcp_proxy.sh
```

### Interactive Web UI Tests
Launch MCP Inspector for visual testing:

```bash
# Inspect local MCP server (requires ./watch.sh to be running)
./claude_scripts/inspect_local_mcp.sh

# Inspect remote MCP server (requires Databricks auth)
./claude_scripts/inspect_remote_mcp.sh
```

**MCP Inspector Features:**
- 🖥️ Web-based interface for interactive MCP server testing
- 🔧 Visual tool execution with parameter input forms
- 📊 Real-time request/response monitoring
- 🐛 Protocol-level debugging and error inspection
- 📋 Complete tool and resource discovery
- 🔄 Session management and connection status

## Prerequisites

### For Local Testing
- Local development server running: `./watch.sh`
- Server accessible on http://localhost:8000

### For Remote Testing  
- Databricks CLI configured: `uvx databricks auth login --host <your-workspace>`
- App deployed with `./deploy.sh`
- Valid `.env.local` configuration with `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, and `DATABRICKS_APP_NAME`

## Expected Output

### Successful Tests Show:
- ✅ Connection successful
- 🧪 Tool discovery (typically 4 tools: health, execute_dbsql, list_warehouses, list_dbfs_files)
- ✅ Tool execution results

### Failed Tests Show:
- ❌ Clear error messages
- 💡 Suggested remediation steps

## Test Results Summary

| Test | Status | Notes |
|------|--------|-------|
| **Local curl** | ✅ Pass | Authentication & headers validated |
| **Local proxy** | ✅ Pass | Full MCP protocol compliance |
| **Remote curl** | ✅ Pass | OAuth authentication & headers validated |
| **Remote proxy** | ✅ Pass | End-to-end OAuth + MCP working |

**Key Findings**: 
- Direct curl tests validate authentication and proper HTTP headers
- MCP protocol requires session initialization (initialize → initialized → tools)
- MCP proxy client handles full protocol complexity correctly
- Both local (token-based) and remote (OAuth) authentication work perfectly

## Architecture

These tests validate the complete MCP stack:
1. **FastAPI Server**: Hosts MCP endpoints at `/mcp/`
2. **MCP Protocol**: JSON-RPC 2.0 over HTTP with SSE support
3. **Authentication**: OAuth for remote, local token for development
4. **Proxy Client**: Transparent MCP protocol routing with token caching
5. **Dynamic Discovery**: Apps API integration for URL resolution

## Technical Notes

- All scripts are pure shell (bash) for simplicity and portability
- Remote scripts automatically discover app URLs via Databricks Apps API
- Configuration is read from `.env.local` using standard shell sourcing
- Proper timeout handling and error reporting throughout
- JSON parsing uses `jq` for reliable response processing