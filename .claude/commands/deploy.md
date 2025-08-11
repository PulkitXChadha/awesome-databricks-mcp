---
description: "Deploy your Databricks app to production"
---

# Deploy to Databricks Apps

I'll deploy your Databricks app to production with comprehensive validation and monitoring.

## What I'll do:

1. **Validate environment** - Check authentication and configuration
2. **Test locally first** - Run app locally to catch issues before deployment
3. **Check app status** - Verify if app exists or needs creation
4. **Deploy to Databricks** - Build, sync, and deploy using proper workflow
5. **Monitor deployment** - Verify successful deployment and provide URL
6. **Provide next steps** - Give you monitoring and debugging information

## Deployment Workflow

**Step 1: Environment Validation**
```bash
# Check if .env.local exists and is configured
cat .env.local

# Test Databricks authentication
databricks current-user me
```

**Step 2: Local Testing (Critical)**
```bash
# Test app locally first to catch issues
./run_app_local.sh
```

**Step 3: App Status Check**
```bash
# Check if app exists
./app_status.sh

# Get app details
databricks apps get "$DATABRICKS_APP_NAME"
```

**Step 4: Deployment Decision**

Based on app status:
- **If app exists**: Deploy with `./deploy.sh`
- **If app doesn't exist**: Ask if you want to create it
- **If you want to create**: Use `./deploy.sh --create`

**Step 5: Deploy**
```bash
# Deploy (with creation if needed)
./deploy.sh --create --verbose
```

**Step 6: Deployment Verification**
```bash
# Check final status
./app_status.sh

# Verify app is running
databricks apps get "$DATABRICKS_APP_NAME"
```

## Deployment Options

**Standard Deployment:**
```bash
./deploy.sh
```

**Create New App:**
```bash
./deploy.sh --create
```

**Verbose Deployment:**
```bash
./deploy.sh --verbose
```

## What Happens During Deployment

1. **Authentication** - Validates Databricks credentials
2. **App Creation** - Creates app if using `--create` and doesn't exist
3. **Frontend Build** - Builds React app for production
4. **Requirements Generation** - Creates requirements.txt from pyproject.toml
5. **Workspace Sync** - Uploads source code to Databricks workspace
6. **App Deployment** - Deploys via Databricks CLI
7. **Verification** - Confirms successful deployment

## Monitoring Your Deployment

**Check App Status:**
```bash
./app_status.sh
```

**View Deployment Logs:**
- Visit your app URL + `/logz` in browser
- Requires OAuth authentication
- Cannot be accessed via curl

**Debug Deployment Issues:**
```bash
# Get verbose status
./app_status.sh --verbose

# Check workspace files
databricks workspace list "$DBA_SOURCE_CODE_PATH"
```

## Common Deployment Issues

**Authentication Problems:**
- Check `.env.local` configuration
- Test with `databricks current-user me`
- Reconfigure with `./setup.sh`

**App Creation Issues:**
- Verify you have app creation permissions
- Check if app name is available
- Use `./deploy.sh --create` explicitly

**Build/Import Errors:**
- Test locally first with `./run_app_local.sh`
- Check TypeScript compilation
- Verify all dependencies are installed

**Deployment Failures:**
- Check app logs at URL + `/logz`
- Use `./app_status.sh --verbose` for details
- Verify workspace file sync

## Success Criteria

Deployment is successful when:
- ✅ App status shows "RUNNING"
- ✅ App URL returns 200 OK
- ✅ No errors in `/logz` endpoint
- ✅ App functionality works as expected

## Next Steps After Deployment

1. **Test your app** at the provided URL
2. **Monitor logs** via `/logz` endpoint
3. **Use `/status`** to check health regularly
4. **Use `/debug`** if issues arise
5. **Iterate and deploy** as needed

Your app is now live! 🚀