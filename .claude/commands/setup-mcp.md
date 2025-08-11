---
description: "Set up and deploy a Databricks MCP server from this template"
---

# 🚀 Databricks MCP Server Setup

I'll help you set up your own Databricks MCP (Model Context Protocol) server so Claude can interact with your Databricks workspace!

## 📋 What We'll Do

⏺ **Step 1: Environment Setup** - Configure Databricks authentication
⏺ **Step 2: Deploy MCP Server** - Deploy to Databricks Apps  
⏺ **Step 3: Add to Claude** - Configure Claude to use your MCP server
⏺ **Step 4: Test Connection** - Verify everything works
⏺ **Step 5: Customize** - Add your own prompts and tools (optional)

---

## Step 0: Check Configuration and Existing MCP Setup

**First, let me check your MCP server configuration:**

[I'll read config.yaml to get your server name]

```yaml
# config.yaml
servername: [your-server-name]  # Default is 'databricks-mcp'
```

**Now let me check if your MCP server is already set up:**

```bash
# Check if MCP server is already added to Claude
SERVER_NAME="[server-name-from-config]"
echo "list your mcp servers" | claude | grep -q "$SERVER_NAME" && echo "✅ MCP server '$SERVER_NAME' already configured!" || echo "❌ MCP server '$SERVER_NAME' not found"
```

[I'll run this check with the actual server name]

**If the MCP server is already configured AND .env.local exists:**

✅ Your MCP server '$SERVER_NAME' is already set up! What would you like to do?

1. **Skip to customization** - Jump to Step 5 to add custom prompts and tools
2. **Test the connection** - Go to Step 4 to verify everything works
3. **Redeploy with changes** - Continue with Step 2 to update deployment
4. **Start fresh** - Remove and reinstall: `claude mcp remove $SERVER_NAME`
5. **Continue from the beginning** - Go through all steps

**Please let me know which option you'd prefer!**

**If .env.local doesn't exist:**
- 🆕 This looks like a fresh clone - let's start from Step 1!

---

## Step 1: Environment Setup

**Let me check if your environment is already configured:**

[I'll check for .env.local file existence]

```bash
# Check if .env.local exists
if [ -f ".env.local" ]; then
    echo "✅ Great! .env.local found - environment is already configured"
    # Test authentication
    source .env.local && export DATABRICKS_HOST && export DATABRICKS_TOKEN && databricks current-user me
else
    echo "📋 Starting fresh - let's create your .env.local with setup"
fi
```

**If .env.local doesn't exist, I'll run the interactive setup script:**

```bash
# Open a new terminal for interactive setup
CURRENT_DIR=$(pwd)
if [ -d "/Applications/iTerm.app" ]; then
    osascript <<EOF
tell application "iTerm"
    create window with default profile
    tell current session of current window
        write text "cd $CURRENT_DIR && ./setup.sh --auto-close"
    end tell
    activate
end tell
EOF
else
    osascript <<EOF
tell application "Terminal"
    do script "cd $CURRENT_DIR && ./setup.sh --auto-close"
    activate
end tell
EOF
fi
```

[I'll wait for you to complete the setup and say "done" when you're ready to continue]

**Please say "done" when the setup script completes!**

---

## Step 2: Deploy MCP Server

**After you've said "done", I'll deploy your MCP server:**

**a) Check if app exists:**
[I'll run `./app_status.sh` to check current status]

**b) Create and deploy app:**
```bash
# Deploy (creates app if needed)
nohup ./deploy.sh --create --verbose > /tmp/mcp-deploy.log 2>&1 &
```

**c) Monitor deployment:**
[I'll tail the log file and monitor progress]

```bash
# Monitor deployment log
tail -f /tmp/mcp-deploy.log
```

**d) Wait for app to be fully ready:**
[I'll keep checking app status until it's RUNNING]

```bash
# Keep checking until app is ready
while true; do
    STATUS=$(./app_status.sh | grep "App Status:" | awk '{print $NF}')
    if [ "$STATUS" = "RUNNING" ]; then
        echo "✅ App is now RUNNING!"
        break
    else
        echo "⏳ App status: $STATUS - waiting..."
        sleep 10
    fi
done
```

**e) Get your app URL:**
[Once the app is RUNNING, I'll show you the deployed app]

```bash
# Get and display app URL
export DATABRICKS_APP_URL=$(./app_status.sh | grep "App URL" | awk '{print $NF}')
echo "
✅ Your MCP server is deployed!
🌐 App URL: $DATABRICKS_APP_URL
🔗 You can visit your app at: $DATABRICKS_APP_URL
"
```

---

## Step 3: Add MCP Server to Claude

**Only after the app is fully deployed and RUNNING, we'll add it to Claude:**

**Now let's add your MCP server to Claude!**

[I'll read the configuration from .env.local and app_status.sh]

```bash
# Get configuration
source .env.local
export DATABRICKS_APP_URL=$(./app_status.sh | grep "App URL" | awk '{print $NF}')

# Add MCP server to Claude
claude mcp add $SERVER_NAME --scope user -- \
  uvx --from git+ssh://git@github.com/databricks-solutions/custom-mcp-databricks-app.git \
  dba-mcp-proxy \
  --databricks-host $DATABRICKS_HOST \
  --databricks-app-url $DATABRICKS_APP_URL
```

[I'll execute this command with your actual values]

---

## Step 4: Test Connection

**Let's verify your MCP server is working:**

```bash
# Test with echo trick
echo "What MCP prompts are available from databricks-mcp?" | claude
```

[I'll run this and show you the results]

**Expected output:**
- Should list available prompts (check_system, list_files, ping_google)
- Should show available tools (execute_parameterized_sql, etc.)

**Note:** You'll need to restart this Claude session to see the MCP server in the `/mcp` command. The echo test confirms it's working for new sessions.

---

## 🎉 Success!

**Your Databricks MCP server is successfully deployed!**

🔄 **Important:** Please restart Claude to see your MCP server in the `/mcp` list.

**Would you like to work on adding custom tools or prompts?**

I can help you:
- 🛠️ Add custom tools for specific Databricks operations
- 📝 Create custom prompts for your workflows
- 🚀 Both tools and prompts
- ✅ No thanks, I'm all set!

**What would you like to do?**

---

## Step 5: Customize (Optional)

### Add Custom Prompts

Create markdown files in the `prompts/` directory:

```markdown
# prompts/my_custom_prompt.md
# Description of what this prompt does

Content that will be returned to Claude
```

### Add Custom Tools

Add functions in `server/app.py`:

```python
@mcp_server.tool
def my_custom_tool(param: str) -> dict:
    """Tool description for Claude."""
    # Your implementation
    return {"result": "data"}
```

[Details on how to add custom prompts and tools will be shown based on your choice above]