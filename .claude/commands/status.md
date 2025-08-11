---
description: "Check health status of development and deployed app"
---

# Check App Status

I'll check the status of your local development server and deployed Databricks app.

## Local Development Server Status

Check if the development server is running:

```bash
# Check if development servers are running
ps aux | grep -E "(watch\.sh|uvicorn|vite)" | grep -v grep

# Check PID file
if [ -f /tmp/databricks-app-watch.pid ]; then
  echo "Dev server PID: $(cat /tmp/databricks-app-watch.pid)"
else
  echo "Dev server not running"
fi
```

## Deployed App Status

Check the status of your deployed Databricks app:

```bash
./app_status.sh
```

## 📊 Status Summary

I'll provide a clean status report with the current state of both your local development environment and deployed app, showing URLs only when services are actually running.