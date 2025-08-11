#!/bin/bash
# Launch MCP Inspector to test remote Databricks MCP server

echo "🔍 Launching MCP Inspector for Remote Databricks MCP Server"
echo "=========================================================\n"

# Read configuration from .env.local
if [ ! -f ".env.local" ]; then
  echo "❌ ERROR: .env.local file not found"
  echo "   Please run ./setup.sh to configure the environment"
  exit 1
fi

# Source the environment file
source .env.local
if [ -z "$DATABRICKS_HOST" ]; then
  echo "❌ ERROR: DATABRICKS_HOST not set in .env.local"
  exit 1
fi
if [ -z "$DATABRICKS_APP_NAME" ]; then
  echo "❌ ERROR: DATABRICKS_APP_NAME not set in .env.local"
  exit 1
fi

echo "Getting app URL from Databricks Apps API..."
# Get the app URL dynamically using the Databricks CLI with environment variables
export DATABRICKS_HOST
export DATABRICKS_TOKEN
APP_INFO=$(uvx databricks apps list 2>/dev/null | grep "^${DATABRICKS_APP_NAME}" || true)

if [ -z "$APP_INFO" ]; then
  echo "❌ ERROR: App '${DATABRICKS_APP_NAME}' not found in Databricks Apps"
  echo "   Please deploy the app first with: ./deploy.sh"
  exit 1
fi

# Extract the URL from the app info (second column in tabular output)
REMOTE_URL=$(echo "$APP_INFO" | awk '{print $2}')

if [ -z "$REMOTE_URL" ]; then
  echo "❌ ERROR: Could not extract app URL from: $APP_INFO"
  exit 1
fi

echo "✅ Found app URL: $REMOTE_URL"
echo "✅ Using Databricks host: $DATABRICKS_HOST"
echo ""

# Create a temporary config file with dynamic values
TEMP_CONFIG=$(mktemp)
cat > "$TEMP_CONFIG" << EOF
{
  "mcpServers": {
    "databricks-remote": {
      "command": "uv",
      "args": [
        "run", 
        "python", 
        "dba_mcp_proxy/mcp_client.py",
        "--databricks-host", "$DATABRICKS_HOST",
        "--databricks-app-url", "$REMOTE_URL"
      ]
    }
  }
}
EOF

echo "🚀 Launching MCP Inspector..."
echo "   This will open a web browser with the MCP Inspector interface"
echo "   You can test all MCP tools and functionality through the UI"
echo ""

# Launch MCP Inspector with the temporary config
npx @modelcontextprotocol/inspector --config "$TEMP_CONFIG" --server databricks-remote

# Clean up temporary config file
rm -f "$TEMP_CONFIG"