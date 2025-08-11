#!/bin/bash
# Test remote MCP server using the MCP proxy client

echo "🧪 Testing Remote MCP Server with Proxy"
echo "=======================================\n"

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
if [ -z "$DATABRICKS_TOKEN" ]; then
  echo "❌ ERROR: DATABRICKS_TOKEN not set in .env.local"
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

# Run the MCP proxy test
echo "Testing MCP proxy connection..."
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | \
  timeout 30 uv run python dba_mcp_proxy/mcp_client.py \
    --databricks-host "${DATABRICKS_HOST}" \
    --databricks-app-url "${REMOTE_URL}" 2>&1 | \
  {
    # Read stderr (connection info) and stdout (response) separately
    stderr_line=""
    while IFS= read -r line; do
      if [[ "$line" == *"Connected to MCP server"* ]]; then
        stderr_line="$line"
      elif [[ "$line" == "{"* ]]; then
        echo "Connection: $stderr_line"
        echo ""
        
        # Parse the JSON response
        response="$line"
        if echo "$response" | jq -e '.result.tools' > /dev/null 2>&1; then
          tool_count=$(echo "$response" | jq '.result.tools | length')
          echo "✅ Found $tool_count tools:"
          echo "$response" | jq -r '.result.tools[] | "  - \(.name): \(.description[:60])..."'
        elif echo "$response" | jq -e '.error' > /dev/null 2>&1; then
          error_msg=$(echo "$response" | jq -r '.error.message')
          echo "❌ Error: $error_msg"
        else
          echo "Response: $response"
        fi
        break
      fi
    done
    
    # If we didn't get a JSON response
    if [ -z "$response" ]; then
      echo "❌ No response received"
    fi
  }

if [ $? -eq 124 ]; then
  echo "❌ Test timed out - OAuth authentication may have failed"
     echo "   Please run: uvx --from databricks-cli databricks auth login --host ${DATABRICKS_HOST}"
fi

echo ""
echo "✅ Remote MCP proxy tests complete"