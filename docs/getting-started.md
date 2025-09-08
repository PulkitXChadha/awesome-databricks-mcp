# Getting Started

Welcome to the Databricks MCP Server! This guide will help you get up and running quickly.

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** installed on your system
- **Databricks Workspace** with admin access
- **Personal Access Token** or service principal credentials
- **Git** for cloning the repository

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/awesome-databricks-mcp.git
cd awesome-databricks-mcp
```

### 2. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using uv (recommended)
uv sync
```

### 3. Configure Authentication

Set your Databricks credentials as environment variables:

```bash
# Personal Access Token (recommended for development)
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-personal-access-token"

# Or use CLI profile
export DATABRICKS_CONFIG_PROFILE="your-profile-name"
```

### 4. Start the Server

```bash
# Run locally
./run_app_local.sh

# Or start manually
python -m server.app
```

The server will start on `http://localhost:8000` by default.

## 🔐 Authentication Setup

### Option 1: Personal Access Token (Recommended)

1. **Generate Token**:
   - Go to your Databricks workspace
   - Click on your username → User Settings
   - Go to Access Tokens → Generate New Token
   - Copy the token (you won't see it again!)

2. **Set Environment Variables**:
   ```bash
   export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
   export DATABRICKS_TOKEN="dapi1234567890abcdef..."
   ```

### Option 2: CLI Profile

1. **Install Databricks CLI**:
   ```bash
   pip install databricks-cli
   ```

2. **Configure Profile**:
   ```bash
   databricks configure --profile your-profile-name
   ```

3. **Set Environment Variable**:
   ```bash
   export DATABRICKS_CONFIG_PROFILE="your-profile-name"
   ```

### Option 3: Service Principal (Production)

1. **Create Service Principal**:
   ```python
   from databricks.sdk import WorkspaceClient
   
   client = WorkspaceClient()
   sp = client.service_principals.create(
       display_name="mcp-server-sp",
       application_id="your-app-id"
   )
   ```

2. **Assign Permissions**:
   ```python
   # Add to workspace admin group
   client.groups.add_member("admins", sp.id)
   ```

## 🧪 Test Your Setup

### 1. Test Connection

```bash
# Test basic connectivity
python -c "
from databricks.sdk import WorkspaceClient
client = WorkspaceClient()
user = client.current_user.me()
print(f'Connected as: {user.user_name}')
"
```

### 2. Test MCP Tools

```bash
# Test Unity Catalog tools
python claude_scripts/test_uc_tools.py

# Test SQL operations
python claude_scripts/test_mcp_tools.py
```

### 3. Test API Endpoints

```bash
# Start the server
./run_app_local.sh

# In another terminal, test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/user/me
```

## 📚 Basic Usage Examples

### 1. List Unity Catalog Objects

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# List all catalogs
catalogs = client.catalogs.list()
for catalog in catalogs:
    print(f"Catalog: {catalog.name}")

# List schemas in a catalog
schemas = client.schemas.list("hive_metastore")
for schema in schemas:
    print(f"Schema: {schema.name}")

# List tables in a schema
tables = client.tables.list("hive_metastore.default")
for table in tables:
    print(f"Table: {table.name}")
```

### 2. Execute SQL Queries

```python
# List SQL warehouses
warehouses = client.warehouses.list()
warehouse_id = warehouses[0].id

# Execute a query
response = client.statement_execution.execute_statement(
    warehouse_id=warehouse_id,
    statement="SELECT * FROM hive_metastore.default.users LIMIT 10"
)

# Get results
if response.result:
    for row in response.result.data_array:
        print(row)
```

### 3. Manage Clusters

```python
# List clusters
clusters = client.clusters.list()
for cluster in clusters:
    print(f"Cluster: {cluster.cluster_name} - State: {cluster.state}")

# Start a cluster
if clusters:
    cluster_id = clusters[0].cluster_id
    client.clusters.start(cluster_id)
    print(f"Starting cluster: {cluster_id}")
```

### 4. Work with Files

```python
# List workspace files
files = client.workspace.list("/Users/your-email")
for file in files:
    print(f"File: {file.path} - Type: {file.object_type}")

# Upload a file
with open("script.py", "rb") as f:
    client.workspace.upload("/Users/your-email/script.py", f.read())
    print("File uploaded successfully")
```

## 🏗️ Project Structure

```
awesome-databricks-mcp/
├── server/                 # FastAPI server implementation
│   ├── app.py             # Main application
│   ├── routers/           # API route definitions
│   ├── services/          # Business logic
│   └── tools/             # MCP tool implementations
├── client/                 # React frontend (optional)
├── docs/                   # Documentation
├── claude_scripts/         # Testing and utility scripts
├── requirements.txt        # Python dependencies
├── pyproject.toml         # Project configuration
└── README.md              # Project overview
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABRICKS_HOST` | Databricks workspace URL | Yes* |
| `DATABRICKS_TOKEN` | Personal access token | Yes* |
| `DATABRICKS_CONFIG_PROFILE` | CLI profile name | Yes* |
| `PORT` | Server port (default: 8000) | No |
| `HOST` | Server host (default: 0.0.0.0) | No |
| `LOG_LEVEL` | Logging level (default: INFO) | No |

*Either token or profile is required

### Server Configuration

```python
# server/app.py
app = FastAPI(
    title="Databricks MCP Server",
    description="MCP server for Databricks services",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Custom settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🚀 Deployment Options

### 1. Local Development

```bash
# Start with auto-reload
uvicorn server.app:app --reload --host 0.0.0.0 --port 8000

# Or use the provided script
./run_app_local.sh
```

### 2. Docker Deployment

```bash
# Build image
docker build -t databricks-mcp-server .

# Run container
docker run -p 8000:8000 \
  -e DATABRICKS_HOST="$DATABRICKS_HOST" \
  -e DATABRICKS_TOKEN="$DATABRICKS_TOKEN" \
  databricks-mcp-server
```

### 3. Cloud Deployment

```bash
# Deploy to Google Cloud Run
./deploy.sh

# Or deploy to AWS App Runner
aws apprunner create-service --cli-input-json apprunner-config.json
```

## 🧪 Testing Your Setup

### 1. Health Check

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "timestamp": "..."}
```

### 2. Authentication Test

```bash
curl http://localhost:8000/api/v1/user/me
# Expected: {"user_name": "your-email", "workspace": "..."}
```

### 3. Tool Functionality Test

```bash
# Test Unity Catalog tools
python -c "
from server.tools.unity_catalog import describe_uc_catalog
result = describe_uc_catalog('hive_metastore')
print(f'Schemas found: {result.get(\"schema_count\", 0)}')
"
```

### 4. MCP Protocol Test

```bash
# Test MCP tools endpoint
curl http://localhost:8000/api/v1/mcp/tools
# Expected: List of available tools
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Authentication Errors

```bash
# Check environment variables
echo "Host: $DATABRICKS_HOST"
echo "Token: ${DATABRICKS_TOKEN:0:10}..."

# Test SDK connection
python -c "
from databricks.sdk import WorkspaceClient
try:
    client = WorkspaceClient()
    user = client.current_user.me()
    print(f'Success: {user.user_name}')
except Exception as e:
    print(f'Error: {e}')
"
```

#### 2. Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
PORT=8001 ./run_app_local.sh
```

#### 3. Import Errors

```bash
# Check Python environment
python --version
pip list | grep databricks

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 4. Permission Errors

```bash
# Check file permissions
ls -la run_app_local.sh

# Make executable
chmod +x run_app_local.sh
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Start with verbose output
python -m server.app --debug

# Check logs
tail -f logs/app.log
```

## 📖 Next Steps

1. **Explore Tools**: Check [Core Tools](core-tools.md) for available functionality
2. **API Reference**: See [API Reference](api-reference.md) for detailed documentation
3. **Examples**: Review [Examples](examples.md) for common use cases
4. **Development**: Check [Development Guide](development.md) for contributing

## 🆘 Getting Help

- **Documentation**: Check the [docs/](docs/) directory
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Examples**: Check the [examples/](examples/) directory

## 📝 Quick Reference

### Essential Commands

```bash
# Start server
./run_app_local.sh

# Test connection
python -c "from databricks.sdk import WorkspaceClient; WorkspaceClient().current_user.me()"

# Check health
curl http://localhost:8000/health

# View logs
tail -f logs/app.log
```

### Key Environment Variables

```bash
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-token"
export PORT=8000
export LOG_LEVEL=INFO
```

### Useful URLs

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **User Info**: http://localhost:8000/api/v1/user/me
- **MCP Tools**: http://localhost:8000/api/v1/mcp/tools

---

**Ready to get started?** Follow the steps above and you'll be running your own Databricks MCP Server in minutes!
