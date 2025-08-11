# 🤖 Databricks MCP Server Template

Host Model Context Protocol (MCP) prompts and tools on Databricks Apps, enabling AI assistants like Claude to interact with your Databricks workspace through a secure, authenticated interface.

## What is this?

This template lets you create an MCP server that runs on Databricks Apps. You can:
- 📝 **Add prompts** as simple markdown files in the `prompts/` folder
- 🛠️ **Create tools** as Python functions that leverage Databricks SDK
- 🔐 **Authenticate securely** with OAuth through Databricks Apps
- 🚀 **Deploy instantly** to make your MCP server accessible to Claude

Think of it as a bridge between Claude and your Databricks workspace - you define what Claude can see and do, and this server handles the rest.

## How it Works

### Architecture Overview

```
┌─────────────┐       MCP Protocol      ┌──────────────────┐        OAuth         ┌─────────────────┐
│   Claude    │ ◄─────────────────────► │  dba-mcp-proxy   │ ◄──────────────────► │ Databricks App  │
│    CLI      │     (stdio/JSON-RPC)    │ (local process)  │    (HTTPS/SSE)      │  (MCP Server)   │
└─────────────┘                         └──────────────────┘                      └─────────────────┘
                                                ▲                                           │
                                                │                                           ▼
                                                └────────── Databricks OAuth ──────► Workspace APIs
```

### Components

1. **MCP Server** (`server/app.py`): A FastAPI app with integrated MCP server that:
   - Dynamically loads prompts from `prompts/*.md` files
   - Exposes Python functions as MCP tools via `@mcp_server.tool` decorator
   - Handles both HTTP requests and MCP protocol over Server-Sent Events

2. **Prompts** (`prompts/`): Simple markdown files where:
   - Filename = prompt name (e.g., `check_system.md` → `check_system` prompt)
   - First line with `#` = description
   - File content = what gets returned to Claude

3. **Local Proxy** (`dba_mcp_proxy/`): Authenticates and proxies MCP requests:
   - Handles Databricks OAuth authentication automatically
   - Translates between Claude's stdio protocol and HTTP/SSE
   - Works with both local development and deployed apps

## 🎬 Demo

This 10-minute video shows you how to set up and use a Databricks MCP server with Claude: https://www.youtube.com/watch?v=oKE59zgb6e0

[![Databricks MCP Demo](https://github.com/user-attachments/assets/315a0e35-73c0-47f7-9ce5-dfada3149101)](https://www.youtube.com/watch?v=oKE59zgb6e0)

This video demonstrates creating your own MCP server with a custom jobs interface in Claude.

## Quick Start

### Create Your Own MCP Server

#### Step 1: Use this template

[![Use this template](https://img.shields.io/badge/Use%20this%20template-2ea44f?style=for-the-badge)](https://github.com/databricks-solutions/custom-mcp-databricks-app/generate)

Or use the GitHub CLI:
```bash
gh repo create my-mcp-server --template databricks-solutions/custom-mcp-databricks-app --private
```

#### Step 2: Clone and setup

```bash
# Clone your new repository
git clone https://github.com/YOUR-USERNAME/my-mcp-server.git
cd my-mcp-server

# Run the interactive setup
./setup.sh
```

This will:
- Configure Databricks authentication
- Set your MCP server name
- Install all dependencies
- Create your `.env.local` file

#### Step 3: Deploy with Claude

In Claude Code, run:
```
/setup-mcp
```

This will:
- Deploy your MCP server to Databricks Apps
- Configure the MCP integration
- Show you available prompts and tools

Then restart Claude Code to use your new MCP server.

### Add to Claude CLI

After deployment, add your MCP server to Claude:

```bash
# Set your Databricks configuration
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_APP_URL="https://your-app.databricksapps.com"  # Get this from ./app_status.sh
export SERVER_NAME="your-server-name"  # This comes from config.yaml (set during ./setup.sh)

# Add your MCP server to Claude (user-scoped)
claude mcp add $SERVER_NAME --scope user -- \
  uvx --from git+ssh://git@github.com/YOUR-USERNAME/your-repo.git dba-mcp-proxy \
  --databricks-host $DATABRICKS_HOST \
  --databricks-app-url $DATABRICKS_APP_URL
```

### Local Development

```bash
# Clone and setup
git clone <your-repo>
cd <your-repo>
./setup.sh

# Start dev server
./watch.sh

# Set your configuration for local testing
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_APP_URL="http://localhost:8000"  # Local dev server

# Add to Claude for local testing
claude mcp add databricks-mcp-local --scope local -- \
  uvx --from git+ssh://git@github.com/YOUR-ORG/YOUR-REPO.git dba-mcp-proxy \
  --databricks-host $DATABRICKS_HOST \
  --databricks-app-url $DATABRICKS_APP_URL
```

## Customization Guide

This template uses [FastMCP](https://github.com/jlowin/fastmcp), a framework that makes it easy to build MCP servers. FastMCP provides two main decorators for extending functionality:

- **`@mcp_server.prompt`** - For registering prompts that return text
- **`@mcp_server.tool`** - For registering tools that execute functions

### Adding Prompts

The easiest way is to create a markdown file in the `prompts/` directory:

```markdown
# Get cluster information

List all available clusters in the workspace with their current status
```

The prompt will be automatically loaded with:
- **Name**: filename without extension (e.g., `get_clusters.md` → `get_clusters`)
- **Description**: first line after `#` 
- **Content**: entire file content

Alternatively, you can register prompts as functions in `server/app.py`:

```python
@mcp_server.prompt(name="dynamic_status", description="Get dynamic system status")
async def get_dynamic_status():
    # This can include dynamic logic, API calls, etc.
    w = get_workspace_client()
    current_user = w.current_user.me()
    return f"Current user: {current_user.display_name}\nWorkspace: {DATABRICKS_HOST}"
```

We auto-load `prompts/` for convenience, but function-based prompts are useful when you need dynamic content.

### Adding Tools

Add a function in `server/app.py` using the `@mcp_server.tool` decorator:

```python
@mcp_server.tool
def list_clusters(status: str = "RUNNING") -> dict:
    """List Databricks clusters by status."""
    w = get_workspace_client()
    clusters = []
    for cluster in w.clusters.list():
        if cluster.state.name == status:
            clusters.append({
                "id": cluster.cluster_id,
                "name": cluster.cluster_name,
                "state": cluster.state.name
            })
    return {"clusters": clusters}
```

Tools must:
- Use the `@mcp_server.tool` decorator
- Have a docstring (becomes the tool description)
- Return JSON-serializable data (dict, list, str, etc.)
- Accept only JSON-serializable parameters


## Deployment

```bash
# Deploy to Databricks Apps
./deploy.sh

# Check status and get your app URL
./app_status.sh
```

Your MCP server will be available at `https://your-app.databricksapps.com/mcp/`

The `app_status.sh` script will show your deployed app URL, which you'll need for the `DATABRICKS_APP_URL` environment variable when adding the MCP server to Claude.

## Authentication

- **Local Development**: No authentication required
- **Production**: OAuth is handled automatically by the proxy using your Databricks CLI credentials

## Examples

### Using with Claude

Once added, you can interact with your MCP server in Claude:

```
Human: What prompts are available?

Claude: I can see the following prompts from your Databricks MCP server:
- check_system: Get system information
- list_files: List files in the current directory
- ping_google: Check network connectivity
```

### Sample Tool Usage

```
Human: Can you execute a SQL query to show databases?

Claude: I'll execute that SQL query for you using the execute_dbsql tool.

[Executes SQL and returns results]
```

## Project Structure

```
├── server/                    # FastAPI backend with MCP server
│   ├── app.py                # Main application + MCP tools
│   └── routers/              # API endpoints
├── prompts/                  # MCP prompts (markdown files)
│   ├── check_system.md      
│   ├── list_files.md        
│   └── ping_google.md       
├── dba_mcp_proxy/           # MCP proxy for Claude CLI
│   └── mcp_client.py        # OAuth + proxy implementation
├── client/                  # React frontend (optional)
├── scripts/                 # Development tools
└── pyproject.toml          # Python package configuration
```

## Advanced Usage

### Environment Variables

Configure in `.env.local`:
```bash
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-token  # For local development
DATABRICKS_SQL_WAREHOUSE_ID=your-warehouse-id  # For SQL tools
```

### Creating Complex Tools

Tools can access the full Databricks SDK:

```python
@mcp_server.tool
def create_job(name: str, notebook_path: str, cluster_id: str) -> dict:
    """Create a Databricks job."""
    w = get_workspace_client()
    job = w.jobs.create(
        name=name,
        tasks=[{
            "task_key": "main",
            "notebook_task": {"notebook_path": notebook_path},
            "existing_cluster_id": cluster_id
        }]
    )
    return {"job_id": job.job_id, "run_now_url": f"{DATABRICKS_HOST}/#job/{job.job_id}"}
```

## Testing Your MCP Server

This template includes comprehensive testing tools for validating MCP functionality at multiple levels.

### Quick Verification

After adding the MCP server to Claude, verify it's working:

```bash
# List available prompts and tools
echo "What MCP prompts are available from databricks-mcp?" | claude

# Test a specific prompt
echo "Use the check_system prompt from databricks-mcp" | claude
```

### Comprehensive Testing Suite

The `claude_scripts/` directory contains 6 testing tools for thorough MCP validation:

#### Command Line Tests
```bash
# Test local MCP server (requires ./watch.sh to be running)
./claude_scripts/test_local_mcp_curl.sh      # Direct HTTP/curl tests with session handling
./claude_scripts/test_local_mcp_proxy.sh     # MCP proxy client tests

# Test remote MCP server (requires Databricks auth and deployment)
./claude_scripts/test_remote_mcp_curl.sh     # OAuth + HTTP tests with dynamic URL discovery
./claude_scripts/test_remote_mcp_proxy.sh    # Full end-to-end MCP proxy tests
```

#### Interactive Web UI Tests
```bash
# Launch MCP Inspector for visual testing (requires ./watch.sh for local)
./claude_scripts/inspect_local_mcp.sh        # Local server web interface
./claude_scripts/inspect_remote_mcp.sh       # Remote server web interface
```

**MCP Inspector Features:**
- 🖥️ Web-based interface for interactive MCP server testing
- 🔧 Visual tool execution with parameter input forms  
- 📊 Real-time request/response monitoring
- 🐛 Protocol-level debugging and error inspection
- 📋 Complete tool and resource discovery

#### What Each Test Validates

| Test Type | Authentication | Protocol | Session Management | Tool Discovery |
|-----------|---------------|----------|-------------------|----------------|
| **curl tests** | ✅ | ✅ | ✅ | ✅ |
| **proxy tests** | ✅ | ✅ | ✅ | ✅ |
| **MCP Inspector** | ✅ | ✅ | ✅ | ✅ |

All tests dynamically discover app URLs and handle OAuth authentication automatically.

See [`claude_scripts/README.md`](claude_scripts/README.md) for detailed documentation.

## Troubleshooting

- **Authentication errors**: Run `databricks auth login` to refresh credentials
- **MCP not found**: Ensure the app is deployed and accessible
- **Tool errors**: Check logs at `https://your-app.databricksapps.com/logz`
- **MCP connection issues**: 
  - Check Claude logs: `tail -f ~/Library/Logs/Claude/*.log`
  - Verify the proxy works: `uvx --from git+ssh://... dba-mcp-proxy --help`
  - Test with echo pipe: `echo "list your mcp commands" | claude`
- **Cached version issues**: If you get errors about missing arguments after an update:
  ```bash
  # Clear uvx cache for this package
  rm -rf ~/.cache/uv/git-v0/checkouts/*/
  # Or clear entire uv cache
  uv cache clean
  ```

## Contributing

1. Fork the repository
2. Add your prompts and tools
3. Test locally with `./watch.sh`
4. Submit a pull request

## License

See [LICENSE.md](LICENSE.md)