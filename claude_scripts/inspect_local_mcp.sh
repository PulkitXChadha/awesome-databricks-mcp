#!/bin/bash
# Launch MCP Inspector to test local Databricks MCP server

echo "🔍 Launching MCP Inspector for Local Databricks MCP Server"
echo "========================================================\n"

LOCAL_URL="http://localhost:8000"

# Check if server is running
echo "Checking if local server is running..."
if ! curl -s --connect-timeout 3 "${LOCAL_URL}/mcp/" > /dev/null 2>&1; then
  echo "❌ ERROR: No local server running on ${LOCAL_URL}"
  echo "   Please start the server with: ./watch.sh"
  exit 1
fi

echo "✅ Local server is running on: ${LOCAL_URL}"
echo ""

# Create a temporary config file for local server
TEMP_CONFIG=$(mktemp)
cat > "$TEMP_CONFIG" << EOF
{
  "mcpServers": {
    "databricks-local": {
      "command": "uv",
      "args": [
        "run", 
        "python", 
        "dba_mcp_proxy/mcp_client.py",
        "--databricks-host", "$LOCAL_URL",
        "--databricks-app-url", "$LOCAL_URL"
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
npx @modelcontextprotocol/inspector --config "$TEMP_CONFIG" --server databricks-local

# Clean up temporary config file
rm -f "$TEMP_CONFIG"