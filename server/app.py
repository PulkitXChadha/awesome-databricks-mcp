"""FastAPI application for Databricks App Template."""

import os
from pathlib import Path

import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastmcp import FastMCP

from server.prompts import load_prompts
from server.routers import router
from server.tools import load_tools


# Load environment variables from .env.local if it exists
def load_env_file(filepath: str) -> None:
  """Load environment variables from a file."""
  if Path(filepath).exists():
    with open(filepath) as f:
      for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
          key, _, value = line.partition('=')
          if key and value:
            os.environ[key] = value


# Load .env files
load_env_file('.env')
load_env_file('.env.local')


# Load configuration from config.yaml
def load_config() -> dict:
  """Load configuration from config.yaml."""
  config_path = Path('config.yaml')
  if config_path.exists():
    with open(config_path, 'r') as f:
      return yaml.safe_load(f)
  return {}


config = load_config()
servername = config.get('servername', 'awesome-databricks-mcp')

# Create MCP server with comprehensive instructions
mcp_server = FastMCP(
    name=servername,
    instructions="""
Welcome to the Awesome Databricks MCP Server! This server provides comprehensive tools for interacting with your Databricks workspace through Claude and other MCP clients.

## Available Capabilities

### 🔧 Core Tools (88+ available across 5 active modules):
- **SQL Operations**: Execute queries, manage warehouses, monitor performance
- **Unity Catalog**: Browse catalogs, schemas, tables, and manage metadata  
- **Jobs & Pipelines**: Create, run, and monitor Databricks jobs and DLT pipelines
- **Lakeview Dashboards**: Build comprehensive dashboards with 16+ widget types
- **Data Management**: Handle DBFS operations, external locations, and storage

### 📝 Smart Prompts:
- **build_lakeview_dashboard**: Create comprehensive Lakeview dashboards with data validation
- **build_ldp_pipeline**: Build Lakehouse Data Pipelines for data processing

## Getting Started

### Quick Commands to Try:
1. `What MCP tools are available?` - See all available tools
2. `List my Databricks catalogs` - Browse Unity Catalog structure
3. `Execute: SHOW DATABASES` - Run SQL queries
4. `Create a sales dashboard` - Build interactive dashboards
5. `Show my recent job runs` - Monitor pipeline execution

### Best Practices:
- Start with `list_uc_catalogs` to explore your data
- Use `execute_dbsql` for running SQL queries with automatic warehouse selection
- Build dashboards step-by-step: data → validation → widgets → layout
- Monitor long-running operations with status checking tools

### Authentication:
- **Local Development**: Uses your Databricks CLI credentials automatically
- **Production**: OAuth handled seamlessly through Databricks Apps platform

### Need Help?
- Ask: `How do I build a dashboard?` for detailed guidance
- Ask: `What databases can I access?` to explore your data sources
- Ask: `Show me job monitoring tools` for pipeline management options

This server bridges Claude's AI capabilities with your Databricks workspace, enabling natural language data operations, automated dashboard creation, and intelligent workspace management.
    """.strip()
)

# Load prompts and tools
load_prompts(mcp_server)
load_tools(mcp_server)

# Create ASGI app from MCP server
# Note: Setting path='/' here to avoid /mcp/mcp double path
mcp_asgi_app = mcp_server.http_app(path='/')

# Pass the MCP app's lifespan to FastAPI
app = FastAPI(
  title='Databricks App API',
  description='Modern FastAPI application template for Databricks Apps with React frontend',
  version='0.1.0',
  lifespan=mcp_asgi_app.lifespan,
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=[
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
  ],
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*'],
)

app.include_router(router, prefix='/api', tags=['api'])

# Mount the MCP server
app.mount('/mcp', mcp_asgi_app)

# ============================================================================
# SERVE STATIC FILES FROM CLIENT BUILD DIRECTORY (MUST BE LAST!)
# ============================================================================
# This static file mount MUST be the last route registered!
# It catches all unmatched requests and serves the React app.
# Any routes added after this will be unreachable!
if os.path.exists('client/build'):
  app.mount('/', StaticFiles(directory='client/build', html=True), name='static')

if __name__ == '__main__':
  import uvicorn

  port = int(os.environ.get('DATABRICKS_APP_PORT', 8000))
  uvicorn.run(app, host='0.0.0.0', port=port)
