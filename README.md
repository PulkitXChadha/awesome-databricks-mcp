# awesome-databricks-mcp

Host Model Context Protocol (MCP) prompts and tools on Databricks Apps, enabling AI assistants like Claude to interact with your Databricks workspace through a secure, authenticated interface.

## What is this?

This template lets you create an MCP server that runs on Databricks Apps. You can:
- 📝 **Add prompts** as simple markdown files in the `prompts/` folder
- 🛠️ **Create tools** as Python functions that leverage Databricks SDK
- 🔐 **Authenticate securely** with OAuth through Databricks Apps
- 🚀 **Deploy instantly** to make your MCP server accessible to Claude
- 🖥️ **Web Interface** with a modern React TypeScript frontend for MCP discovery
- 🧪 **Comprehensive Testing** with automated MCP validation tools

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
   - Exposes Python functions as MCP tools via modular tool system
   - Handles both HTTP requests and MCP protocol over Server-Sent Events
   - Uses FastMCP framework for seamless MCP integration

2. **React Frontend** (`client/`): A modern TypeScript React application that:
   - Provides a web interface for MCP discovery and testing
   - Shows available prompts, tools, and MCP configuration
   - Includes copy-paste setup commands for Claude integration
   - Built with TailwindCSS, Radix UI, and modern React patterns
   - Uses Vite for fast development and building

3. **Prompts** (`prompts/`): Simple markdown files where:
   - Filename = prompt name (e.g., `build_dlt_pipeline.md` → `build_dlt_pipeline` prompt)
   - First line with `#` = description
   - File content = what gets returned to Claude

4. **Modular Tools System** (`server/tools/`): Organized tool modules that:
   - Break down functionality into logical, manageable components
   - Provide 104+ tools across 9 specialized modules
   - Enable better maintainability and collaboration
   - Support easy addition of new tools

5. **Local Proxy** (`dba_mcp_proxy/`): Authenticates and proxies MCP requests:
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
- Install all dependencies (Python + Node.js)
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

# Start dev server (both backend and frontend)
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

## Running Locally

### Prerequisites

Before running the MCP server locally, ensure you have:

- **Python 3.11+** and **Node.js 18+** installed
- **Databricks CLI** configured with `databricks auth login`
- **Git** for cloning the repository
- **uv** package manager (recommended) or **pip** for Python dependencies
- **bun** (recommended) or **npm** for Node.js dependencies

### Step-by-Step Local Setup

#### 1. Clone and Configure

```bash
# Clone your repository
git clone https://github.com/YOUR-USERNAME/your-mcp-server.git
cd your-mcp-server

# Run the interactive setup script
./setup.sh
```

The setup script will:
- Install Python dependencies using `uv` or `pip`
- Install Node.js dependencies using `bun` or `npm`
- Configure your Databricks workspace settings
- Create a `.env.local` file with your configuration

#### 2. Start the Development Server

```bash
# Start both backend (FastAPI) and frontend (React) servers
./watch.sh
```

This command starts:
- **Backend**: FastAPI server on `http://localhost:8000`
- **Frontend**: React development server on `http://localhost:3000`
- **File watching**: Automatic reloading when files change

#### 3. Verify Local Setup

Open your browser and navigate to:
- **Backend API**: http://localhost:8000/docs (FastAPI Swagger UI)
- **Frontend**: http://localhost:3000 (React application)
- **MCP Endpoint**: http://localhost:8000/mcp/ (MCP server)

#### 4. Test with Claude CLI

```bash
# Set environment variables for local testing
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_APP_URL="http://localhost:8000"

# Add the local MCP server to Claude
claude mcp add databricks-mcp-local --scope local -- \
  uvx --from git+ssh://git@github.com/YOUR-USERNAME/your-repo.git dba-mcp-proxy \
  --databricks-host $DATABRICKS_HOST \
  --databricks-app-url $DATABRICKS_APP_URL

# Test the connection
echo "What MCP prompts are available from databricks-mcp-local?" | claude
```

### Development Workflow

#### Making Changes

1. **Edit prompts**: Modify files in `prompts/` directory
2. **Edit tools**: Update functions in appropriate modules under `server/tools/`
3. **Edit frontend**: Modify React components in `client/src/`
4. **Edit backend**: Update FastAPI routes in `server/`

All changes automatically reload thanks to the file watchers in `./watch.sh`.

#### Testing Changes

```bash
# Test local MCP server directly
./claude_scripts/test_local_mcp_curl.sh

# Test with MCP proxy
./claude_scripts/test_local_mcp_proxy.sh

# Use the web-based MCP Inspector
./claude_scripts/inspect_local_mcp.sh
```

#### Debugging

- **Backend logs**: Check terminal output from `./watch.sh`
- **Frontend logs**: Check browser console and terminal output
- **MCP logs**: Monitor the `/mcp/` endpoint responses
- **Database queries**: Check Databricks workspace logs

### Local vs Production Differences

| Feature | Local Development | Production |
|---------|------------------|------------|
| **Authentication** | Databricks CLI token | OAuth via Databricks Apps |
| **URL** | `http://localhost:8000` | `https://your-app.databricksapps.com` |
| **HTTPS** | No (HTTP only) | Yes (HTTPS required) |
| **File watching** | Yes (auto-reload) | No |
| **Debug mode** | Yes | No |
| **Logs** | Terminal output | Databricks Apps logs |

### Troubleshooting Local Issues

#### Common Problems

**Port conflicts:**
```bash
# Check what's using port 8000
lsof -i :8000

# Kill process if needed
kill -9 <PID>
```

**Dependencies not found:**
```bash
# Reinstall Python dependencies
uv sync

# Reinstall Node.js dependencies
cd client && bun install
```

**Databricks authentication:**
```bash
# Refresh Databricks CLI credentials
databricks auth login

# Verify configuration
databricks config get
```

**MCP connection issues:**
```bash
# Test MCP endpoint directly
curl http://localhost:8000/mcp/

# Check Claude MCP configuration
claude mcp list
```

#### Performance Tips

- Use `uv` instead of `pip` for faster Python dependency management
- Use `bun` instead of `npm` for faster Node.js dependency management
- The `./watch.sh` script uses `uvicorn --reload` for fast backend development
- Frontend uses Vite for fast hot module replacement

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

Add a function in the appropriate module under `server/tools/` using the `@mcp_server.tool` decorator:

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

## Available MCP Tools

This template includes a comprehensive set of **104+ Databricks tools** organized into **9 logical modules**:

### Core Tools (`core.py`)
- **`health`** - Check MCP server and Databricks connection status

### SQL & Data Tools (`sql_operations.py`)
- **`execute_dbsql`** - Execute SQL queries on Databricks SQL warehouses
- **`list_warehouses`** - List all SQL warehouses in the workspace
- **`get_sql_warehouse`** - Get details of a specific SQL warehouse
- **`create_sql_warehouse`** - Create a new SQL warehouse
- **`start_sql_warehouse`** - Start a SQL warehouse
- **`stop_sql_warehouse`** - Stop a SQL warehouse
- **`delete_sql_warehouse`** - Delete a SQL warehouse
- **`list_queries`** - List queries for a warehouse
- **`get_query`** - Get details of a specific query
- **`get_query_results`** - Get results of a completed query
- **`cancel_query`** - Cancel a running query
- **`get_statement_status`** - Get statement execution status
- **`get_statement_results`** - Get statement results
- **`cancel_statement`** - Cancel statement execution
- **`list_recent_queries`** - List recent queries

### Unity Catalog Tools (`unity_catalog.py`)
- **`list_uc_catalogs`** - List Unity Catalog catalogs
- **`describe_uc_catalog`** - Get detailed catalog information
- **`describe_uc_schema`** - Get schema details and tables
- **`describe_uc_table`** - Get table metadata and lineage
- **`list_uc_volumes`** - List volumes in a Unity Catalog schema
- **`describe_uc_volume`** - Get detailed volume information
- **`list_uc_functions`** - List functions in a Unity Catalog schema
- **`describe_uc_function`** - Get detailed function information
- **`list_uc_models`** - List models in a Unity Catalog schema
- **`describe_uc_model`** - Get detailed model information
- **`list_external_locations`** - List external locations
- **`describe_external_location`** - Get external location details
- **`list_storage_credentials`** - List storage credentials
- **`describe_storage_credential`** - Get storage credential details
- **`list_uc_permissions`** - List permissions for UC objects
- **`search_uc_objects`** - Search for UC objects by name/description
- **`get_table_statistics`** - Get table statistics and metadata
- **`list_metastores`** - List all metastores
- **`describe_metastore`** - Get metastore details
- **`list_uc_tags`** - List available tags
- **`apply_uc_tags`** - Apply tags to UC objects
- **`list_data_quality_monitors`** - List data quality monitors
- **`get_data_quality_results`** - Get monitoring results
- **`create_data_quality_monitor`** - Create data quality monitor

### Data Management Tools (`data_management.py`)
- **`list_dbfs_files`** - Browse DBFS file system
- **`upload_dbfs_file`** - Upload files to DBFS
- **`download_dbfs_file`** - Download files from DBFS
- **`delete_dbfs_file`** - Delete files from DBFS
- **`list_volumes`** - List volumes in a Unity Catalog schema
- **`describe_volume`** - Get detailed volume information
- **`list_external_locations`** - List external locations
- **`describe_external_location`** - Get external location details
- **`list_storage_credentials`** - List storage credentials
- **`describe_storage_credential`** - Get storage credential details

### Jobs & Pipelines Tools (`jobs_pipelines.py`)
- **`list_jobs`** - List all jobs in the workspace
- **`get_job`** - Get details of a specific job
- **`create_job`** - Create a new job
- **`update_job`** - Update an existing job
- **`delete_job`** - Delete a job
- **`run_job`** - Run a job
- **`list_job_runs`** - List runs for a job
- **`get_job_run`** - Get details of a specific job run
- **`cancel_job_run`** - Cancel a running job
- **`list_pipelines`** - List all DLT pipelines
- **`get_pipeline`** - Get details of a specific pipeline
- **`create_pipeline`** - Create a new DLT pipeline
- **`update_pipeline`** - Update an existing pipeline
- **`delete_pipeline`** - Delete a pipeline
- **`start_pipeline`** - Start a pipeline
- **`stop_pipeline`** - Stop a pipeline
- **`list_pipeline_runs`** - List runs for a pipeline
- **`get_pipeline_run`** - Get details of a specific pipeline run
- **`cancel_pipeline_run`** - Cancel a running pipeline
- **`get_pipeline_update`** - Get pipeline update details

### Workspace Files Tools (`workspace_files.py`)
- **`list_workspace_files`** - List files in the workspace
- **`get_workspace_file`** - Get details of a specific file
- **`create_workspace_file`** - Create a new file
- **`update_workspace_file`** - Update an existing file
- **`delete_workspace_file`** - Delete a file

### Dashboard Tools (`dashboards.py`)
- **`list_lakeview_dashboards`** - List all Lakeview dashboards
- **`get_lakeview_dashboard`** - Get details of a specific Lakeview dashboard
- **`create_lakeview_dashboard`** - Create a new Lakeview dashboard
- **`update_lakeview_dashboard`** - Update an existing Lakeview dashboard
- **`delete_lakeview_dashboard`** - Delete a Lakeview dashboard
- **`list_dashboards`** - List all legacy dashboards
- **`get_dashboard`** - Get details of a specific legacy dashboard
- **`delete_dashboard`** - Delete a legacy dashboard

### Repository Tools (`repositories.py`)
- **`list_repositories`** - List all Git repositories
- **`get_repository`** - Get details of a specific repository
- **`create_repository`** - Create a new repository
- **`update_repository`** - Update an existing repository
- **`delete_repository`** - Delete a repository
- **`list_branches`** - List branches for a repository
- **`get_branch`** - Get details of a specific branch
- **`create_branch`** - Create a new branch
- **`delete_branch`** - Delete a branch
- **`list_commits`** - List commits for a repository

### Governance Tools (`governance.py`)
- **`list_audit_logs`** - List audit logs
- **`get_audit_log`** - Get details of a specific audit log
- **`list_governance_rules`** - List governance rules
- **`get_governance_rule`** - Get details of a specific governance rule
- **`create_governance_rule`** - Create a new governance rule
- **`update_governance_rule`** - Update an existing governance rule
- **`delete_governance_rule`** - Delete a governance rule
- **`list_data_lineage`** - List data lineage information
- **`get_data_lineage`** - Get details of specific data lineage
- **`list_access_controls`** - List access controls
- **`get_access_control`** - Get details of a specific access control
- **`create_access_control`** - Create a new access control
- **`update_access_control`** - Update an existing access control
- **`delete_access_control`** - Delete an access control
- **`list_compliance_reports`** - List compliance reports

## Modular Tools Architecture

The tools are organized into logical, manageable modules for better maintainability:

```
server/tools/
├── __init__.py              # Main entry point that imports and registers all tools
├── core.py                  # Core/health tools (1 tool)
├── sql_operations.py        # SQL warehouse and query management (15 tools)
├── unity_catalog.py         # Unity Catalog operations (20 tools)
├── data_management.py       # DBFS, volumes, and data operations (10 tools)
├── jobs_pipelines.py        # Job and pipeline management (20 tools)
├── workspace_files.py       # Workspace file operations (5 tools)
├── dashboards.py            # Dashboard and monitoring tools (8 tools)
├── repositories.py          # Git repository management (10 tools)
└── governance.py            # Governance rules and data lineage (15 tools)
```

### Benefits of Modularization

1. **Maintainability**: Each module focuses on a specific domain
2. **Readability**: Smaller files are easier to navigate and debug
3. **Collaboration**: Multiple developers can work on different modules simultaneously
4. **Testing**: Individual modules can be tested in isolation
5. **Scalability**: New tools can be added to appropriate modules without cluttering

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
- build_dlt_pipeline: Build a DLT pipeline for data processing
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
│   ├── app.py                # Main application + MCP server setup
│   ├── tools/                # Modular MCP tools implementation
│   │   ├── __init__.py       # Tool registration and loading
│   │   ├── core.py           # Core and health tools
│   │   ├── sql_operations.py # SQL and warehouse tools
│   │   ├── unity_catalog.py  # Unity Catalog tools
│   │   ├── data_management.py # Data and DBFS tools
│   │   ├── jobs_pipelines.py # Jobs and DLT pipeline tools
│   │   ├── workspace_files.py # Workspace file tools
│   │   ├── dashboards.py     # Dashboard tools
│   │   ├── repositories.py   # Git repository tools
│   │   └── governance.py     # Governance and compliance tools
│   └── routers/              # API endpoints
├── client/                   # React TypeScript frontend
│   ├── src/                  # Source code
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Page components
│   │   └── fastapi_client/   # Auto-generated API client
│   ├── package.json          # Node.js dependencies
│   └── tailwind.config.js    # TailwindCSS configuration
├── prompts/                  # MCP prompts (markdown files)
│   └── build_dlt_pipeline.md # DLT pipeline building prompt
├── dba_mcp_proxy/           # MCP proxy for Claude CLI
│   └── mcp_client.py        # OAuth + proxy implementation
├── claude_scripts/          # Comprehensive testing tools
│   ├── test_local_mcp_*.sh  # Local MCP testing scripts
│   ├── test_remote_mcp_*.sh # Remote MCP testing scripts
│   ├── test_uc_tools.py     # Unity Catalog tools testing
│   └── inspect_*.sh         # Web-based MCP Inspector
├── docs/                     # Documentation
│   ├── databricks_apis/      # Databricks API documentation
│   └── unity_catalog_tools.md # Unity Catalog tools documentation
├── scripts/                  # Development tools
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
echo "Use the build_dlt_pipeline prompt from databricks-mcp" | claude
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

### Web Interface Testing

The React frontend provides an additional way to test your MCP server:

```bash
# Start the development server
./watch.sh

# Open http://localhost:3000 in your browser
# Navigate to the MCP Discovery page to see:
# - Available prompts and tools
# - MCP configuration details
# - Copy-paste setup commands for Claude
```

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
- **Frontend build issues**: Ensure Node.js dependencies are installed:
  ```bash
  cd client
  bun install
  ```

## Contributing

1. Fork the repository
2. Add your prompts and tools
3. Test locally with `./watch.sh`
4. Submit a pull request

## License

See [LICENSE.md](LICENSE.md)