# DBA MCP Proxy

A Model Context Protocol (MCP) proxy client for Databricks Apps.

## Usage

Run the proxy directly from GitHub using uvx:

```bash
uvx --from git+ssh://git@github.com/databricks-solutions/custom-mcp-databricks-app.git \
  dba-mcp-proxy \
  --databricks-host <HOST> \
  --databricks-app-url <URL>
```

### Arguments

- **--databricks-host**: Your Databricks workspace URL (e.g., `https://workspace.cloud.databricks.com`)
- **--databricks-app-url**: The Databricks App URL (e.g., `https://myapp.databricksapps.com`)

### Examples

```bash
# Connect to local development server
uvx --from git+ssh://git@github.com/databricks-solutions/custom-mcp-databricks-app.git \
  dba-mcp-proxy \
  --databricks-host https://workspace.cloud.databricks.com \
  --databricks-app-url http://localhost:8000

# Connect to deployed Databricks App
uvx --from git+ssh://git@github.com/databricks-solutions/custom-mcp-databricks-app.git \
  dba-mcp-proxy \
  --databricks-host https://workspace.cloud.databricks.com \
  --databricks-app-url https://myapp.databricksapps.com
```

## What it does

The DBA MCP Proxy:
- Connects to a Databricks App's MCP server endpoint
- Handles authentication (OAuth for deployed apps)
- Provides a standard MCP interface for tools like Claude
- Enables interaction with Databricks workspace resources through MCP

## Authentication

- **Local development**: No authentication required
- **Deployed apps**: Uses Databricks OAuth via CLI authentication