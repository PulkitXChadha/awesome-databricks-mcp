# Deployment Validation Guide

This guide covers the comprehensive deployment validation tests for the Databricks MCP server.

## Test Categories

### 1. Health & Availability Tests (`@pytest.mark.deployment`)
Tests that verify the basic health and availability of the deployed application:
- **Health endpoint validation**: Checks `/health` endpoint returns proper status
- **Health endpoint performance**: Validates response times are acceptable
- **MCP endpoint availability**: Verifies MCP server is accessible
- **MCP tool listing**: Ensures tools are properly exposed

### 2. Smoke Tests (`@pytest.mark.smoke`)
Critical path tests that validate core functionality:
- **Critical endpoints**: Tests all essential API endpoints
- **Basic tool execution**: Validates simple tool execution works
- **Error handling**: Verifies proper error responses
- **CORS headers**: Checks browser compatibility headers

### 3. Security Tests (`@pytest.mark.security`)
Tests that validate security configurations:
- **Security headers**: Checks for proper security headers in responses
- **Unauthorized access**: Verifies protected endpoints require authentication
- **Authentication flow**: Validates OAuth flow (manual testing required)

### 4. Load Tests (`@pytest.mark.load`)
Optional performance tests:
- **Concurrent requests**: Tests handling of multiple simultaneous requests
- **Response time under load**: Validates performance under stress

### 5. Monitoring Tests (`@pytest.mark.monitoring`)
Tests for observability features:
- **Metrics endpoint**: Checks if metrics are exposed
- **Logging availability**: Verifies logging configuration

## Running Deployment Tests

### Quick Start
```bash
# Run all deployment validation tests
./tests/run_deployment_tests.sh
```

### Environment Setup
```bash
# For deployed application
export DATABRICKS_APP_URL="https://your-app.databricksapps.com"

# For local testing
export LOCAL_DEPLOYMENT=true
```

### Running Specific Test Suites
```bash
# Health & availability tests only
uv run pytest tests/test_deployment.py -m deployment -v

# Smoke tests only
uv run pytest tests/test_deployment.py -m smoke -v

# Security tests only
uv run pytest tests/test_deployment.py -m security -v

# Load tests (optional)
uv run pytest tests/test_deployment.py -m load -v

# All automated tests
uv run pytest tests/test_deployment.py -v
```

### Manual OAuth Verification
```bash
# Display manual verification steps
uv run pytest tests/test_deployment.py -m manual -v -s
```

## OAuth Flow Manual Verification

Since OAuth flows require browser interaction, manual verification is necessary:

1. **Initial Authentication**
   - Navigate to `{deployment_url}/auth`
   - Verify redirect to Databricks OAuth consent
   - Check requested scopes

2. **Consent and Authorization**
   - Approve OAuth consent
   - Verify redirect back to application
   - Check for authorization code

3. **Token Exchange**
   - Verify auth code exchange for tokens
   - Check secure token storage
   - Ensure no tokens in URLs

4. **API Access**
   - Make authenticated API request
   - Verify proper authorization headers
   - Check successful response

5. **Token Refresh**
   - Wait for token expiry or force expiry
   - Make another API request
   - Verify automatic refresh

6. **Logout Flow**
   - Navigate to logout endpoint
   - Verify session/tokens cleared
   - Check redirect to login
   - Verify API requests fail with 401

## Test Output Interpretation

### Successful Deployment
```
✓ Health & Availability passed
✓ Smoke Tests passed
✓ Security Tests passed

All automated deployment tests passed!
Remember to perform manual OAuth verification.
```

### Failed Tests
```
✗ Health & Availability failed
  - Check deployment status with ./app_status.sh
  - Verify DATABRICKS_APP_URL is correct
  - Check application logs

✗ Smoke Tests failed
  - Review specific endpoint failures
  - Check for missing dependencies
  - Verify database connectivity

✗ Security Tests failed
  - Review security header warnings
  - Check authentication configuration
  - Verify CORS settings
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Verify deployment URL is correct
   - Check application is running
   - Verify network connectivity

2. **Authentication Failures**
   - Check OAuth configuration
   - Verify client ID/secret
   - Check redirect URIs

3. **Timeout Errors**
   - Check application performance
   - Verify database connectivity
   - Review resource limits

4. **Missing Endpoints**
   - Verify deployment is complete
   - Check API routing configuration
   - Review application logs

### Debug Commands
```bash
# Check deployment status
./app_status.sh

# View application logs
databricks apps logs awesome-databricks-mcp-dev

# Test with curl
curl -v https://your-app.databricksapps.com/health

# Test MCP endpoint
curl https://your-app.databricksapps.com/mcp/ | jq
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Deployment Validation
on:
  deployment_status:
    types: [created]

jobs:
  validate:
    if: github.event.deployment_status.state == 'success'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install uv
      - run: uv sync
      - run: |
          export DATABRICKS_APP_URL=${{ github.event.deployment_status.target_url }}
          ./tests/run_deployment_tests.sh
```

## Best Practices

1. **Run tests after every deployment**
2. **Monitor test execution times** - Increasing times may indicate performance issues
3. **Review security warnings** - Even if tests pass, address security header warnings
4. **Perform manual OAuth verification** - Automated tests can't fully validate OAuth flows
5. **Keep tests updated** - Add tests for new features and endpoints
6. **Use in CI/CD pipelines** - Automate validation in deployment workflows

## Test Metrics

Track these metrics over time:
- **Test execution time**: Should remain consistent
- **Response times**: Monitor for degradation
- **Success rate**: Should be 100% for healthy deployments
- **Security compliance**: Track and address warnings

## Summary

The deployment validation suite provides comprehensive testing of:
- ✅ Application health and availability
- ✅ Critical functionality (smoke tests)
- ✅ Security configurations
- ✅ Performance under load
- ✅ Monitoring and observability

Regular execution of these tests ensures deployed applications meet quality standards and function correctly in production environments.