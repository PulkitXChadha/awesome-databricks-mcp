---
description: "Start development environment with hot reloading"
---

# Start Development Environment

I'll start your Databricks app development environment with hot reloading for both frontend and backend.

## What I'll do:

1. **Check current status** - See if development servers are already running
2. **Stop existing servers** - Clean up any running processes
3. **Start development servers** - Launch with proper background execution and logging
4. **Verify startup** - Ensure both frontend and backend are running correctly
5. **Show access URLs** - Provide links to your running application

## Starting Development Servers

Let me start the development environment for you:

**Step 1: Checking current status**
```bash
ps aux | grep databricks-app
```

**Step 2: Starting development servers**
```bash
nohup ./watch.sh > /tmp/databricks-app-watch.log 2>&1 &
```

**Step 3: Monitoring startup**
```bash
tail -f /tmp/databricks-app-watch.log
```

## Your Development Environment

Once started, you'll have access to:

- **Frontend**: http://localhost:3000 (or next available port)
- **Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **OpenAPI Spec**: http://localhost:8000/openapi.json

## Development Features

✅ **Hot Reloading** - Changes to Python and React code automatically reload
✅ **Auto-Generated Client** - TypeScript client updates when FastAPI changes
✅ **Background Execution** - Servers run in background with comprehensive logging
✅ **Process Management** - Easy to stop/start with proper cleanup

## Monitoring Your Development

**View logs:**
```bash
tail -f /tmp/databricks-app-watch.log
```

**Check process status:**
```bash
ps aux | grep databricks-app
```

**Stop development servers:**
```bash
kill $(cat /tmp/databricks-app-watch.pid) || pkill -f watch.sh
```

## Next Steps

1. **Open your browser** to http://localhost:3000
2. **Start coding** - Changes will automatically reload
3. **Use `/status`** to check health at any time
4. **Use `/deploy`** when ready to deploy to Databricks

Happy coding! 🚀