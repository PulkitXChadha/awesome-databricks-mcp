#!/bin/bash
# Test local MCP server using the MCP proxy client

echo "🧪 Testing Local MCP Server with Proxy"
echo "======================================\n"

LOCAL_URL="http://localhost:8000"

# Check if server is running
echo "Checking if local server is running..."
if ! curl -s --connect-timeout 3 "${LOCAL_URL}/mcp/" > /dev/null 2>&1; then
  echo "❌ ERROR: No local server running on ${LOCAL_URL}"
  echo "   Please start the server with: ./watch.sh"
  exit 1
fi

echo "✅ Local server is running"

# Run the MCP proxy test
echo "Testing MCP proxy connection..."
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | \
  timeout 10 uv run python dba_mcp_proxy/mcp_client.py \
    --databricks-host "${LOCAL_URL}" \
    --databricks-app-url "${LOCAL_URL}" 2>&1 | \
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
  echo "❌ Test timed out - local server may not be running"
  echo "   Please start the server with: ./watch.sh"
fi

echo ""
echo "✅ Local MCP proxy tests complete"