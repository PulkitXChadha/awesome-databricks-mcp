---
description: "Open your deployed Databricks app in the browser"
---

# Open Your Databricks App

I'll get your deployed Databricks app URL and open it in your browser.

## What I'll do:

1. **Check app status** - Use `./app_status.sh` to get the current app URL
2. **Validate URL** - Ensure the app URL is available and valid
3. **Open in browser** - Use `open {url}` to launch your app

## Opening Your App

Let me get your app URL and open it for you:

**Step 1: Getting app URL**
```bash
./app_status.sh
```

**Step 2: Opening in browser**
```bash
open {app_url}
```

## App Access Information

Your deployed app provides:
- **Main App**: The primary application interface
- **App Management**: Databricks workspace app management page
- **Logs**: App logs at URL + `/logz` (requires browser authentication)

## What to Expect

When your app opens, you should see:
- ✅ **If app is RUNNING**: Your application loads normally
- ⏳ **If app is STARTING**: Loading or startup page
- ❌ **If app is UNAVAILABLE**: Error page or timeout

## Troubleshooting

**If the app doesn't open:**
- Check if the app exists: `./app_status.sh`
- Verify app is deployed: `./deploy.sh`
- Check app logs: Visit URL + `/logz` in browser

**If the app shows errors:**
- Use `/debug` to troubleshoot
- Check deployment status: `./app_status.sh --verbose`
- Test locally first: `./run_app_local.sh`

**If you need to redeploy:**
- Use `/deploy` to redeploy your app
- Use `./deploy.sh --verbose` for detailed output

## Quick Access Commands

**Open app in browser:**
```bash
./app_status.sh
# Then: open {the_url_from_output}
```

**Open app management page:**
```bash
# Visit: {DATABRICKS_HOST}/apps/{DATABRICKS_APP_NAME}
```

**Open app logs:**
```bash
# Visit: {app_url}/logz
```

Your app is opening now! 🚀