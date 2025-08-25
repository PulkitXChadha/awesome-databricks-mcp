"""
Deployment validation tests for the Databricks MCP server.

Tests focus on validating the deployed application's availability,
functionality, and critical paths in production environments.
"""

import os
import time
import asyncio
import pytest
import pytest_asyncio
import aiohttp
from unittest.mock import patch, MagicMock
from typing import Optional, Dict, Any


def get_deployment_url() -> Optional[str]:
    """Get the deployment URL from environment or configuration."""
    # Check environment variables
    app_url = os.getenv('DATABRICKS_APP_URL')
    if app_url:
        return app_url.rstrip('/')
    
    # Check for local deployment
    if os.getenv('LOCAL_DEPLOYMENT') == 'true':
        return 'http://localhost:8000'
    
    # Default to None if no deployment URL is found
    return None


@pytest.fixture
def deployment_url():
    """Fixture for deployment URL."""
    url = get_deployment_url()
    if not url:
        pytest.skip("No deployment URL configured. Set DATABRICKS_APP_URL or LOCAL_DEPLOYMENT=true")
    return url


@pytest_asyncio.fixture
async def http_session():
    """Create an async HTTP session for testing."""
    async with aiohttp.ClientSession() as session:
        yield session


# ============================================================================
# Health Endpoint Tests
# ============================================================================

@pytest.mark.deployment
@pytest.mark.asyncio
async def test_health_endpoint(deployment_url, http_session):
    """Test deployed user endpoint as health check."""
    health_url = f"{deployment_url}/api/user/me"
    
    try:
        async with http_session.get(health_url, timeout=10) as response:
            assert response.status == 200, f"Health check failed with status {response.status}"
            
            data = await response.json()
            assert 'userName' in data, "Health response missing 'userName' field"
            assert 'active' in data, "Health response missing 'active' field"
            assert data['active'] == True, f"User not active: {data.get('active')}"
            
    except asyncio.TimeoutError:
        pytest.fail(f"Health endpoint timeout at {health_url}")
    except aiohttp.ClientError as e:
        pytest.fail(f"Health endpoint connection error: {e}")


@pytest.mark.deployment
@pytest.mark.asyncio
async def test_health_endpoint_performance(deployment_url, http_session):
    """Test health endpoint response time."""
    health_url = f"{deployment_url}/api/user/me"
    
    response_times = []
    for _ in range(5):
        start_time = time.time()
        
        async with http_session.get(health_url, timeout=10) as response:
            assert response.status == 200
            await response.json()
        
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        response_times.append(response_time)
    
    avg_response_time = sum(response_times) / len(response_times)
    max_response_time = max(response_times)
    
    # Performance assertions - more lenient for local development
    assert avg_response_time < 1000, f"Average response time too high: {avg_response_time:.2f}ms"
    assert max_response_time < 2000, f"Max response time too high: {max_response_time:.2f}ms"


# ============================================================================
# MCP Endpoint Tests
# ============================================================================

@pytest.mark.deployment
@pytest.mark.asyncio
async def test_mcp_endpoint(deployment_url, http_session):
    """Test MCP server availability and basic functionality."""
    mcp_url = f"{deployment_url}/api/mcp_info/discovery"
    
    # Test MCP discovery endpoint
    async with http_session.get(mcp_url, timeout=10) as response:
        assert response.status == 200, f"MCP endpoint failed with status {response.status}"
        
        data = await response.json()
        assert 'servername' in data, "MCP response missing 'servername' field"
        assert 'tools' in data, "MCP response missing 'tools' field"
        assert 'prompts' in data, "MCP response missing 'prompts' field"
        
        # Verify server name
        assert data['servername'] == 'awesome-databricks-mcp', "Unexpected MCP server name"
        
        # Verify tools are exposed
        assert isinstance(data['tools'], list), "Tools should be a list"
        assert len(data['tools']) > 0, "No tools exposed by MCP server"


@pytest.mark.deployment
@pytest.mark.asyncio
async def test_mcp_tool_listing(deployment_url, http_session):
    """Test MCP tool listing and metadata."""
    mcp_url = f"{deployment_url}/api/mcp_info/discovery"
    
    async with http_session.get(mcp_url, timeout=10) as response:
        assert response.status == 200, f"MCP tools endpoint failed with status {response.status}"
        
        data = await response.json()
        tools = data['tools']
        assert isinstance(tools, list), "Tools response should be a list"
        assert len(tools) > 0, "No tools available"
        
        # Verify tool structure
        for tool in tools[:5]:  # Check first 5 tools
            assert 'name' in tool, f"Tool missing 'name' field: {tool}"
            assert 'description' in tool, f"Tool missing 'description' field: {tool}"
            assert isinstance(tool['name'], str), f"Tool name should be string: {tool}"
            assert isinstance(tool['description'], str), f"Tool description should be string: {tool}"


@pytest.mark.deployment
@pytest.mark.asyncio
async def test_mcp_prompts_listing(deployment_url, http_session):
    """Test MCP prompts availability."""
    prompts_url = f"{deployment_url}/api/prompts"
    
    async with http_session.get(prompts_url, timeout=10) as response:
        # Prompts endpoint might not exist in all deployments
        if response.status == 404:
            pytest.skip("Prompts endpoint not available in this deployment")
        
        assert response.status == 200, f"MCP prompts endpoint failed with status {response.status}"
        
        prompts = await response.json()
        assert isinstance(prompts, list), "Prompts response should be a list"
        
        if len(prompts) > 0:
            # Verify prompt structure
            for prompt in prompts[:3]:  # Check first 3 prompts
                assert 'name' in prompt, f"Prompt missing 'name' field: {prompt}"
                assert 'description' in prompt, f"Prompt missing 'description' field: {prompt}"


# ============================================================================
# OAuth Flow Tests (Manual Verification Required)
# ============================================================================

@pytest.mark.deployment
@pytest.mark.manual
def test_oauth_flow_documentation():
    """Document OAuth flow verification steps (manual test)."""
    verification_steps = """
    OAuth Flow Manual Verification Steps:
    
    1. Initial Authentication:
       - Navigate to {deployment_url}/auth
       - Verify redirect to Databricks OAuth consent page
       - Check OAuth scopes requested
    
    2. Consent and Authorization:
       - Approve OAuth consent
       - Verify redirect back to application
       - Check for authorization code in URL parameters
    
    3. Token Exchange:
       - Verify application exchanges auth code for tokens
       - Check for secure token storage (cookies/session)
       - Verify no tokens exposed in URLs or client-side code
    
    4. API Access:
       - Make authenticated API request
       - Verify request includes proper authorization headers
       - Check for successful response with user context
    
    5. Token Refresh:
       - Wait for token expiry (or force expiry)
       - Make another API request
       - Verify automatic token refresh occurs
       - Check new tokens are properly stored
    
    6. Logout Flow:
       - Navigate to logout endpoint
       - Verify session/tokens are cleared
       - Check redirect to login page
       - Verify subsequent API requests fail with 401
    
    7. Error Handling:
       - Test with invalid tokens
       - Test with expired tokens
       - Test with revoked tokens
       - Verify proper error messages and redirects
    """
    
    print("\n" + "="*60)
    print("OAuth Flow Manual Verification Required")
    print("="*60)
    print(verification_steps)
    print("="*60)
    
    # This test always passes but requires manual verification
    assert True, "Manual OAuth verification required"


# ============================================================================
# Smoke Test Suite
# ============================================================================

@pytest.mark.deployment
@pytest.mark.smoke
@pytest.mark.asyncio
async def test_smoke_critical_endpoints(deployment_url, http_session):
    """Smoke test for all critical API endpoints."""
    critical_endpoints = [
        ('/api/user/me', 200),
        ('/api/mcp_info/discovery', 200),
        ('/api/prompts', 200),
        ('/docs', 200),  # FastAPI documentation
    ]
    
    failed_endpoints = []
    
    for endpoint, expected_status in critical_endpoints:
        url = f"{deployment_url}{endpoint}"
        try:
            async with http_session.get(url, timeout=10) as response:
                if response.status != expected_status:
                    failed_endpoints.append({
                        'endpoint': endpoint,
                        'expected': expected_status,
                        'actual': response.status
                    })
        except Exception as e:
            failed_endpoints.append({
                'endpoint': endpoint,
                'error': str(e)
            })
    
    if failed_endpoints:
        failure_msg = "Critical endpoints failed:\n"
        for failure in failed_endpoints:
            if 'error' in failure:
                failure_msg += f"  - {failure['endpoint']}: {failure['error']}\n"
            else:
                failure_msg += f"  - {failure['endpoint']}: Expected {failure['expected']}, got {failure['actual']}\n"
        pytest.fail(failure_msg)


@pytest.mark.deployment
@pytest.mark.smoke
@pytest.mark.asyncio
async def test_smoke_tool_execution(deployment_url, http_session):
    """Smoke test for basic tool execution."""
    # Test health tool (simplest tool)
    tool_url = f"{deployment_url}/mcp/execute"
    
    payload = {
        "tool": "health",
        "parameters": {}
    }
    
    async with http_session.post(
        tool_url,
        json=payload,
        timeout=15
    ) as response:
        if response.status == 404:
            pytest.skip("Tool execution endpoint not available")
        
        assert response.status in [200, 201], f"Tool execution failed with status {response.status}"
        
        result = await response.json()
        assert 'result' in result or 'data' in result, "Tool execution response missing result"
        
        # Verify the health tool returned expected data
        tool_result = result.get('result') or result.get('data')
        assert 'status' in tool_result, "Health tool result missing 'status'"
        assert tool_result['status'] == 'healthy', "Health tool returned unhealthy status"


@pytest.mark.deployment
@pytest.mark.smoke
@pytest.mark.asyncio
async def test_smoke_error_handling(deployment_url, http_session):
    """Smoke test for error handling."""
    # Test 404 handling
    invalid_url = f"{deployment_url}/api/v1/nonexistent"
    
    async with http_session.get(invalid_url) as response:
        assert response.status == 404, f"Expected 404, got {response.status}"
        
        # Verify error response format
        if response.content_type == 'application/json':
            error_data = await response.json()
            assert 'detail' in error_data or 'error' in error_data, "Error response missing detail/error field"
    
    # Test invalid tool execution
    tool_url = f"{deployment_url}/mcp/execute"
    invalid_payload = {
        "tool": "nonexistent_tool",
        "parameters": {}
    }
    
    async with http_session.post(tool_url, json=invalid_payload) as response:
        if response.status != 404:  # Endpoint exists
            assert response.status in [400, 422], f"Expected 400/422 for invalid tool, got {response.status}"


@pytest.mark.deployment
@pytest.mark.smoke
@pytest.mark.asyncio
async def test_smoke_cors_headers(deployment_url, http_session):
    """Test CORS headers for browser compatibility."""
    test_url = f"{deployment_url}/health"
    
    # Test preflight request
    headers = {
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'Content-Type'
    }
    
    async with http_session.options(test_url, headers=headers) as response:
        # CORS might not be configured for all deployments
        if response.status == 200:
            cors_headers = response.headers
            
            # Check for CORS headers
            assert 'Access-Control-Allow-Origin' in cors_headers or \
                   'access-control-allow-origin' in cors_headers, \
                   "Missing Access-Control-Allow-Origin header"
            
            assert 'Access-Control-Allow-Methods' in cors_headers or \
                   'access-control-allow-methods' in cors_headers, \
                   "Missing Access-Control-Allow-Methods header"


# ============================================================================
# Load Testing
# ============================================================================

@pytest.mark.deployment
@pytest.mark.load
@pytest.mark.asyncio
async def test_concurrent_requests(deployment_url, http_session):
    """Test handling of concurrent requests."""
    health_url = f"{deployment_url}/api/user/me"
    num_requests = 20
    
    async def make_request():
        async with http_session.get(health_url) as response:
            return response.status
    
    # Send concurrent requests
    tasks = [make_request() for _ in range(num_requests)]
    start_time = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    total_time = time.time() - start_time
    
    # Check results
    successful = sum(1 for r in results if isinstance(r, int) and r == 200)
    failed = sum(1 for r in results if isinstance(r, Exception))
    
    assert successful >= num_requests * 0.95, f"Too many failed requests: {num_requests - successful}/{num_requests}"
    assert failed == 0, f"Exceptions occurred: {failed} requests failed"
    assert total_time < 10, f"Concurrent requests took too long: {total_time:.2f}s"


# ============================================================================
# Security Tests
# ============================================================================

@pytest.mark.deployment
@pytest.mark.security
@pytest.mark.asyncio
async def test_security_headers(deployment_url, http_session):
    """Test security headers in responses."""
    test_url = f"{deployment_url}/health"
    
    async with http_session.get(test_url) as response:
        headers = response.headers
        
        # Check for security headers (may vary by deployment)
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': None  # Check presence only
        }
        
        warnings = []
        for header, expected_values in security_headers.items():
            if header in headers:
                if expected_values:
                    if isinstance(expected_values, list):
                        if headers[header] not in expected_values:
                            warnings.append(f"{header}: {headers[header]} (expected one of {expected_values})")
                    elif headers[header] != expected_values:
                        warnings.append(f"{header}: {headers[header]} (expected {expected_values})")
            elif expected_values is not None:
                warnings.append(f"Missing security header: {header}")
        
        # Log warnings but don't fail (security headers may vary by deployment)
        if warnings:
            print("\nSecurity header warnings:")
            for warning in warnings:
                print(f"  - {warning}")


@pytest.mark.deployment
@pytest.mark.security
@pytest.mark.asyncio
async def test_unauthorized_access(deployment_url, http_session):
    """Test unauthorized access to protected endpoints."""
    # Test endpoints that should require authentication
    protected_endpoints = [
        '/api/v1/admin',
        '/api/v1/user/profile',
        '/mcp/execute/sensitive_tool'
    ]
    
    for endpoint in protected_endpoints:
        url = f"{deployment_url}{endpoint}"
        
        # Make request without auth headers
        async with http_session.get(url) as response:
            # Should return 401 or 403 for protected endpoints
            # 404 is also acceptable (endpoint might not exist)
            assert response.status in [401, 403, 404], \
                f"Endpoint {endpoint} returned {response.status} without auth (expected 401/403/404)"


# ============================================================================
# Monitoring and Observability Tests
# ============================================================================

@pytest.mark.deployment
@pytest.mark.monitoring
@pytest.mark.asyncio
async def test_metrics_endpoint(deployment_url, http_session):
    """Test metrics endpoint if available."""
    metrics_url = f"{deployment_url}/metrics"
    
    async with http_session.get(metrics_url) as response:
        if response.status == 404:
            pytest.skip("Metrics endpoint not available")
        
        assert response.status in [200, 401], f"Metrics endpoint returned unexpected status: {response.status}"
        
        if response.status == 200:
            content = await response.text()
            # Check for Prometheus-style metrics
            assert '# TYPE' in content or '{' in content, "Metrics format not recognized"


@pytest.mark.deployment
@pytest.mark.monitoring
@pytest.mark.asyncio
async def test_logging_availability(deployment_url, http_session):
    """Test logging endpoint or configuration."""
    logs_url = f"{deployment_url}/logz"
    
    async with http_session.get(logs_url) as response:
        if response.status == 404:
            pytest.skip("Logs endpoint not available")
        
        # Logs endpoint might require authentication
        assert response.status in [200, 401, 403], \
            f"Logs endpoint returned unexpected status: {response.status}"


# ============================================================================
# Configuration and Environment Tests
# ============================================================================

@pytest.mark.deployment
def test_deployment_configuration():
    """Verify deployment configuration is properly set."""
    deployment_url = get_deployment_url()
    
    if deployment_url:
        print(f"\nDeployment URL: {deployment_url}")
        
        # Check for required environment variables
        required_vars = [
            'DATABRICKS_HOST',
            'DATABRICKS_APP_NAME'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"Warning: Missing environment variables: {', '.join(missing_vars)}")
    else:
        pytest.skip("No deployment configuration found")


# ============================================================================
# Test Runner Configuration
# ============================================================================

if __name__ == "__main__":
    # Run deployment tests
    pytest.main([
        __file__,
        '-v',
        '-m', 'deployment',
        '--tb=short'
    ])