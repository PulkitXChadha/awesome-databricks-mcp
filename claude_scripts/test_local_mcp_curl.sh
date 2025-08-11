#!/bin/bash
# Test local MCP server with direct curl commands

echo "🧪 Testing Local MCP Server with curl"
echo "=====================================\n"

BASE_URL="http://localhost:8000"

# Check if server is running
echo "Checking if local server is running..."
if ! curl -s --connect-timeout 3 "${BASE_URL}/mcp/" > /dev/null 2>&1; then
  echo "❌ ERROR: No local server running on ${BASE_URL}"
  echo "   Please start the server with: ./watch.sh"
  exit 1
fi

echo "✅ Local server is running\n"

echo "1. Get session ID from server:"
RESPONSE=$(curl -s -D /tmp/mcp_headers.txt "${BASE_URL}/mcp/" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer local-test-token" 2>/dev/null)

SESSION_ID=$(grep -i "mcp-session-id:" /tmp/mcp_headers.txt | cut -d' ' -f2 | tr -d '\r\n')
if [ -n "$SESSION_ID" ]; then
  echo "✅ Got session ID: $SESSION_ID"
else
  echo "❌ No session ID received"
  echo "Response: $RESPONSE"
fi
echo "\n"

echo "2. Initialize MCP session:"
INIT_RESPONSE=$(curl -s -X POST "${BASE_URL}/mcp/" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer local-test-token" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": "initialize", 
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {"roots": {"listChanged": true}, "sampling": {}},
      "clientInfo": {"name": "curl-test", "version": "1.0.0"}
    }
  }')
if echo "$INIT_RESPONSE" | grep -q "event: message"; then
  echo "✅ MCP session initialized"
else
  echo "❌ Initialize failed: $INIT_RESPONSE"
fi
echo "\n"

echo "3. Send initialized notification:"
curl -s -X POST "${BASE_URL}/mcp/" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer local-test-token" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc": "2.0", "method": "notifications/initialized"}' > /dev/null
echo "✅ Initialized notification sent"
echo "\n"

echo "4. Test tools/list with proper session:"
TOOLS_RESPONSE=$(curl -s -X POST "${BASE_URL}/mcp/" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer local-test-token" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}')

# Extract JSON from SSE response
TOOLS_JSON=$(echo "$TOOLS_RESPONSE" | grep "^data: " | sed 's/^data: //')
if [ -n "$TOOLS_JSON" ]; then
  echo "✅ MCP tools/list successful:"
  echo "$TOOLS_JSON" | jq '.result.tools | length' | while read count; do
    echo "   Found $count tools:"
  done
  echo "$TOOLS_JSON" | jq -r '.result.tools[] | "   - \(.name): \(.description[:60])..."'
else
  echo "❌ No tools data received: $TOOLS_RESPONSE"
fi
echo "\n"

echo "ℹ️  Note: Direct curl requires full MCP session initialization."
echo "   Use the proxy test for complete MCP protocol compliance."
echo "\n"

echo "✅ Local MCP curl tests complete"