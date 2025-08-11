#!/bin/bash
# Test remote MCP server with direct curl commands

echo "🧪 Testing Remote MCP Server with curl"
echo "======================================\n"

# Read configuration from .env.local
if [ ! -f ".env.local" ]; then
  echo "❌ ERROR: .env.local file not found"
  echo "   Please run ./setup.sh to configure the environment"
  exit 1
fi

# Source the environment file and get the host
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

echo "Getting OAuth token from Databricks CLI..."
TOKEN=$(uvx --from databricks-cli databricks auth token --host "${DATABRICKS_HOST}" 2>/dev/null | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ ERROR: Failed to get OAuth token"
     echo "   Please run: uvx --from databricks-cli databricks auth login --host ${DATABRICKS_HOST}"
  exit 1
fi

echo "✅ Got OAuth token\n"

echo "1. Test OAuth authentication and headers:"
RESPONSE=$(curl -s "${REMOTE_URL}/mcp/" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ${TOKEN}")
if echo "$RESPONSE" | grep -q "Missing session ID"; then
  echo "✅ OAuth authentication accepted, server requires MCP session (expected)"
else
  echo "❌ Unexpected response: $RESPONSE"
fi
echo "\n"

echo "2. Test direct tools/list (requires MCP session):"
curl -s -X POST "${REMOTE_URL}/mcp/" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | jq '.'
echo "\n"

echo "ℹ️  Note: Direct curl requires full MCP session initialization."
echo "   Use the proxy test for complete MCP protocol compliance."
echo "\n"

echo "✅ Remote MCP curl tests complete"