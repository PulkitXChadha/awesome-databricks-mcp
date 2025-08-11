# Databricks App Template Development Guide

## Project Memory

This is a modern full-stack application template for Databricks Apps, featuring FastAPI backend with React TypeScript frontend and modern development tooling.

## Tech Stack

**Backend:**
- Python with `uv` for package management
- FastAPI for API framework
- Databricks SDK for workspace integration
- OpenAPI automatic client generation

**Frontend:**
- TypeScript with React
- Vite for fast development and hot reloading
- shadcn/ui components with Tailwind CSS
- React Query for API state management
- Bun for package management

## Development Workflow

### Package Management
- Use `uv add/remove` for Python dependencies, not manual edits to pyproject.toml
- Use `bun add/remove` for frontend dependencies, not manual package.json edits
- Always check if dependencies exist in the project before adding new ones

### Development Commands
- `./setup.sh` - Interactive environment setup and dependency installation
- `./watch.sh` - Start development servers with hot reloading (frontend:5173, backend:8000)
- `./fix.sh` - Format code (ruff for Python, prettier for TypeScript)
- `./deploy.sh` - Deploy to Databricks Apps

### 🚨 IMPORTANT: NEVER RUN THE SERVER MANUALLY 🚨

**ALWAYS use the watch script with nohup and logging:**

```bash
# Start development servers (REQUIRED COMMAND)
nohup ./watch.sh > /tmp/databricks-app-watch.log 2>&1 &

# Or for production mode
nohup ./watch.sh --prod > /tmp/databricks-app-watch.log 2>&1 &
```

**NEVER run uvicorn or the server directly!** Always use `./watch.sh` as it:
- Configures environment variables properly
- Starts both frontend and backend correctly
- Generates TypeScript client automatically
- Handles authentication setup
- Provides proper logging and error handling

### 🚨 PYTHON EXECUTION RULE 🚨

**NEVER run `python` directly - ALWAYS use `uv run`:**

```bash
# ✅ CORRECT - Always use uv run
uv run python script.py
uv run uvicorn server.app:app
uv run scripts/make_fastapi_client.py

# ❌ WRONG - Never use python directly
python script.py
uvicorn server.app:app
python scripts/make_fastapi_client.py
```

### 🚨 DATABRICKS CLI EXECUTION RULE 🚨

**NEVER run `databricks` CLI directly - ALWAYS prefix with environment setup:**

```bash
# ✅ CORRECT - Always source .env.local first
source .env.local && export DATABRICKS_HOST && export DATABRICKS_TOKEN && databricks current-user me
source .env.local && export DATABRICKS_HOST && export DATABRICKS_TOKEN && databricks apps list
source .env.local && export DATABRICKS_HOST && export DATABRICKS_TOKEN && databricks workspace list /

# ❌ WRONG - Never use databricks CLI directly
databricks current-user me
databricks apps list
databricks workspace list /
```

**Why this is required:**
- Ensures environment variables are loaded from .env.local
- Exports authentication variables to environment
- Prevents authentication failures and missing configuration

### Claude Natural Language Commands
Claude understands natural language commands for common development tasks:

**Development Lifecycle:**
- "start the devserver" → Runs `./watch.sh` in background with logging
- "kill the devserver" → Stops all background development processes
- "fix the code" → Runs `./fix.sh` to format Python and TypeScript code
- "deploy the app" → Runs `./deploy.sh` to deploy to Databricks Apps

**Development Tasks:**
- "add a new API endpoint" → Creates FastAPI routes with proper patterns
- "create a new React component" → Builds UI components using shadcn/ui
- "debug this error" → Analyzes logs and fixes issues
- "install [package]" → Adds dependencies using uv (Python) or bun (frontend)
- "generate the TypeScript client" → Regenerates API client from OpenAPI spec
- "open the UI in playwright" → Opens the frontend app in Playwright browser for testing
- "open app" → Gets app URL from `./app_status.sh` and opens it with `open {url}`

### Implementation Validation Workflow
**During implementation, ALWAYS:**
1. **Start development server first**: `nohup ./watch.sh > /tmp/databricks-app-watch.log 2>&1 &`
2. **Open app with Playwright** to see current state before changes
3. **After each implementation step:**
   - Check logs: `tail -f /tmp/databricks-app-watch.log`
   - Use Playwright to verify UI changes are working
   - Take snapshots to confirm features render correctly
   - Test user interactions and API calls
4. **🚨 CRITICAL: FastAPI Endpoint Verification**
   - **IMPORTANT: After adding ANY new FastAPI endpoint, MUST curl the endpoint to verify it works**
   - **NEVER move on to the next step until the endpoint is verified with curl**
   - **Example verification commands:**
     ```bash
     # Test GET endpoint
     curl -s http://localhost:8000/api/new-endpoint | jq
     
     # Test POST endpoint
     curl -X POST -H "Content-Type: application/json" -d '{"key":"value"}' http://localhost:8000/api/new-endpoint | jq
     ```
   - **Show the curl response to confirm the endpoint works correctly**
   - **If the endpoint fails, debug and fix it before proceeding**
5. **Install Playwright if needed**: `claude mcp add playwright npx '@playwright/mcp@latest'`
6. **Iterative validation**: Test each feature before moving to next step

**This ensures every implementation step is validated and working before proceeding.**

### Development Server
- **ALWAYS** run `./watch.sh` with nohup in background and log to file for debugging
- Watch script automatically runs in background and logs to `/tmp/databricks-app-watch.log`
- Frontend runs on http://localhost:5173
- Backend runs on http://localhost:8000
- API docs available at http://localhost:8000/docs
- Supports hot reloading for both frontend and backend
- Automatically generates TypeScript client from FastAPI OpenAPI spec
- **Check logs**: `tail -f /tmp/databricks-app-watch.log`
- **Stop processes**: `pkill -f "watch.sh"` or check PID file

### Code Quality
- Use `./fix.sh` for code formatting before commits
- Python: ruff for formatting and linting, ty for type checking
- TypeScript: prettier for formatting, ESLint for linting
- Type checking with TypeScript and ty (Python)

### API Development
- FastAPI automatically generates OpenAPI spec
- TypeScript client is auto-generated from OpenAPI spec
- Test endpoints with curl or FastAPI docs
- Check server logs after requests
- Verify response includes expected fields

### Databricks API Integration
- **ALWAYS** reference `docs/databricks_apis/` documentation when implementing Databricks features
- Use `docs/databricks_apis/databricks_sdk.md` for workspace, cluster, and SQL operations
- Use `docs/databricks_apis/mlflow_genai.md` for AI agent and LLM functionality
- Use `docs/databricks_apis/model_serving.md` for model serving endpoints and inference
- Use `docs/databricks_apis/workspace_apis.md` for file operations and directory management
- Follow the documented patterns and examples for proper API usage
- Check official documentation links in each API guide for latest updates

### Frontend Development
- Use shadcn/ui components for consistent UI
- Follow React Query patterns for API calls
- Use TypeScript strictly - no `any` types
- Import from auto-generated client: `import { apiClient } from '@/fastapi_client'`
- Client uses shadcn/ui components with proper TypeScript configuration
- shadcn components must be added with: npx shadcn@latest add <component-name>

### Testing Methodology
- Test API endpoints using FastAPI docs interface
- Use browser dev tools for frontend debugging
- Check network tab for API request/response inspection
- Verify console for any JavaScript errors

### Deployment
- Use `./deploy.sh` for Databricks Apps deployment
- Automatically builds frontend and generates requirements.txt
- Configures app.yaml with environment variables
- Verifies deployment through Databricks CLI
- **IMPORTANT**: After deployment, monitor `/logz` endpoint of your Databricks app to check for installation issues
- App logs are available at: `https://<app-url>/logz` (visit in browser - requires OAuth authentication)

### Environment Configuration
- Use `.env.local` for local development configuration
- Set environment variables and Databricks credentials
- Never commit `.env.local` to version control
- Use `./setup.sh` to create and update environment configuration

### Debugging Tips
- Verify environment variables are set correctly
- Use FastAPI docs for API testing: http://localhost:8000/docs
- Check browser console for frontend errors
- Use React Query DevTools for API state inspection
- **Check watch logs**: `tail -f /tmp/databricks-app-watch.log` for all development server output
- **Check process status**: `ps aux | grep databricks-app` or check PID file at `/tmp/databricks-app-watch.pid`
- **Force stop**: `kill $(cat /tmp/databricks-app-watch.pid)` or `pkill -f watch.sh`

### Key Files
- `server/app.py` - FastAPI application entry point
- `server/routers/` - API endpoint routers
- `client/src/App.tsx` - React application entry point
- `client/src/pages/` - React page components
- `scripts/make_fastapi_client.py` - TypeScript client generator
- `pyproject.toml` - Python dependencies and project configuration
- `client/package.json` - Frontend dependencies and scripts
- `claude_scripts/` - Test scripts created by Claude for testing functionality

### API Documentation
- `docs/databricks_apis/` - Comprehensive API documentation for Databricks integrations
- `docs/databricks_apis/databricks_sdk.md` - Databricks SDK usage patterns
- `docs/databricks_apis/mlflow_genai.md` - MLflow GenAI for AI agents
- `docs/databricks_apis/model_serving.md` - Model serving endpoints and inference
- `docs/databricks_apis/workspace_apis.md` - Workspace file operations

### Documentation Files
- `docs/product.md` - Product requirements document (created during /dba workflow)
- `docs/design.md` - Technical design document (created during /dba workflow)
- These files are generated through iterative collaboration with the user during the /dba command

### Common Issues
- If TypeScript client is not found, run the client generation script manually
- If hot reload not working, restart `./watch.sh`
- If dependencies missing, run `./setup.sh` to reinstall

### MCP (Model Context Protocol) Integration

**IMPORTANT: The server must support BOTH HTTP homepage AND MCP over HTTP simultaneously.**

#### MCP Setup and Configuration
- **ALWAYS use absolute paths when adding MCP servers** because the command can be run from anywhere:
  ```bash
  # ✅ CORRECT - Use absolute path
  claude mcp add databricks-proxy /Users/nikhil.thorat/emu/mcp-commands-databricks-app/mcp_databricks_client.py
  
  # ❌ WRONG - Never use relative paths
  claude mcp add databricks-proxy ./mcp_databricks_client.py
  ```

#### MCP Testing Workflow
**End-to-end testing process for MCP integration:**

1. **Add the MCP server to Claude CLI:**
   ```bash
   claude mcp add databricks-proxy /Users/nikhil.thorat/emu/mcp-commands-databricks-app/mcp_databricks_client.py
   ```

2. **Test MCP availability:**
   ```bash
   # Test if MCP tools are available
   echo "list the mcp prompts and tools" | claude
   ```

3. **Check MCP logs for debugging:**
   ```bash
   # Find MCP log directory (created by Claude CLI)
   ls -la ~/Library/Caches/claude-cli-nodejs/-Users-nikhil-thorat-emu-mcp-commands-databricks-app/mcp-logs-databricks-proxy/
   
   # Read the latest log file
   cat ~/Library/Caches/claude-cli-nodejs/-Users-nikhil-thorat-emu-mcp-commands-databricks-app/mcp-logs-databricks-proxy/$(ls -t ~/Library/Caches/claude-cli-nodejs/-Users-nikhil-thorat-emu-mcp-commands-databricks-app/mcp-logs-databricks-proxy/ | head -1)
   ```

   **Log locations from actual testing:**
   - MCP logs: `~/Library/Caches/claude-cli-nodejs/-Users-nikhil-thorat-emu-mcp-commands-databricks-app/mcp-logs-databricks-proxy/`
   - Log files are timestamped like: `mcp-2025-07-22T00-14-48-872Z.log`
   - Logs contain detailed MCP communication including tool discovery and execution

4. **Verify both HTTP and MCP work simultaneously:**
   - HTTP Homepage: `http://localhost:5176` (or port shown in watch logs)
   - MCP Discovery: Available through Claude CLI when MCP server is added
   - Both must work at the same time without conflicts

#### MCP Architecture in this App
- FastAPI app serves both regular HTTP endpoints and MCP functionality
- MCP server is integrated using FastMCP library
- MCP tools are mounted at `/mcp` path with SSE support
- Client proxy (`mcp_databricks_client.py`) connects to deployed app or local server
- OAuth authentication handled automatically for deployed apps

### Testing MCP Servers
When testing MCP server connections, use this trick:
```bash
# Check if MCP server is connected and list available commands
echo "list your mcp commands" | claude

# Check specific MCP server prompts
echo "What MCP prompts are available from databricks-mcp?" | claude
```

If the MCP server doesn't respond:
1. Check Claude logs: `tail -f ~/Library/Logs/Claude/*.log`
2. Check MCP logs in cache directory
3. Verify the proxy command works standalone
4. Ensure the app is deployed and accessible

Remember: This is a development template focused on rapid iteration and modern tooling.