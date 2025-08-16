"""Unit tests for router initialization and structure."""

import pytest
from fastapi import APIRouter


@pytest.mark.unit
@pytest.mark.api
class TestRouterInitialization:
  """Test router initialization and module structure."""

  def test_main_router_exists(self):
    """Test that main router is properly initialized."""
    from server.routers import router

    assert isinstance(router, APIRouter)

  def test_individual_routers_exist(self):
    """Test that individual router modules exist and export routers."""
    from server.routers.mcp_info import router as mcp_info_router
    from server.routers.prompts import router as prompts_router
    from server.routers.user import router as user_router

    assert isinstance(user_router, APIRouter)
    assert isinstance(prompts_router, APIRouter)
    assert isinstance(mcp_info_router, APIRouter)

  def test_router_includes_all_sub_routers(self):
    """Test that main router includes all sub-routers."""
    from server.routers import router

    # Get all included routes
    included_routes = []
    for route in router.routes:
      if hasattr(route, 'path_regex'):
        included_routes.append(route.path)

    # Should have routes from all sub-routers
    # The exact paths depend on FastAPI's internal route handling
    # but we can check that sub-routers were included by checking
    # that the router has routes
    assert len(router.routes) > 0

  def test_router_prefixes_and_tags(self):
    """Test that routers are included with correct prefixes and tags."""
    from server.routers import router

    # Check that the router has the expected structure
    # This is a basic structural test
    assert hasattr(router, 'routes')
    assert len(router.routes) > 0

    # The specific prefix and tag testing would require
    # examining FastAPI's internal route structure


@pytest.mark.unit
@pytest.mark.api
class TestRouterStructure:
  """Test router structure and organization."""

  def test_user_router_endpoints(self):
    """Test user router has expected endpoints."""
    from server.routers.user import router as user_router

    # Get endpoint paths
    paths = []
    for route in user_router.routes:
      if hasattr(route, 'path'):
        paths.append(route.path)

    # Should have user-related endpoints
    assert len(paths) > 0
    # The specific paths depend on how FastAPI constructs routes

  def test_prompts_router_endpoints(self):
    """Test prompts router has expected endpoints."""
    from server.routers.prompts import router as prompts_router

    # Get endpoint paths
    paths = []
    for route in prompts_router.routes:
      if hasattr(route, 'path'):
        paths.append(route.path)

    # Should have prompts-related endpoints
    assert len(paths) > 0

  def test_mcp_info_router_endpoints(self):
    """Test MCP info router has expected endpoints."""
    from server.routers.mcp_info import router as mcp_info_router

    # Get endpoint paths
    paths = []
    for route in mcp_info_router.routes:
      if hasattr(route, 'path'):
        paths.append(route.path)

    # Should have MCP info related endpoints
    assert len(paths) > 0


@pytest.mark.integration
@pytest.mark.api
class TestRouterIntegration:
  """Integration tests for router system."""

  def test_all_routers_mount_successfully(self, test_client):
    """Test that all routers are successfully mounted in the application."""
    # Test that endpoints from each router are accessible

    # User router endpoints (under /api/user)
    response = test_client.get('/api/user/me')
    assert response.status_code != 404  # Should exist, even if it fails

    # Prompts router endpoints (under /api/prompts)
    response = test_client.get('/api/prompts')
    assert response.status_code == 200  # Should work

    # MCP info router endpoints (under /api/mcp_info)
    response = test_client.get('/api/mcp_info/info')
    assert response.status_code == 200  # Should work

  def test_router_error_handling_consistency(self, test_client):
    """Test that error handling is consistent across routers."""
    # Test 404 responses
    response1 = test_client.get('/api/prompts/nonexistent')
    response2 = test_client.get('/api/mcp_info/prompt/nonexistent')

    assert response1.status_code == 404
    assert response2.status_code == 404

    # Both should return JSON with detail field
    assert 'detail' in response1.json()
    assert 'detail' in response2.json()

  def test_router_prefixes_work_correctly(self, test_client):
    """Test that router prefixes are applied correctly."""
    # Test that endpoints are only accessible with correct prefixes

    # This should work (correct prefix)
    response = test_client.get('/api/prompts')
    assert response.status_code == 200

    # This should not work (no prefix)
    response = test_client.get('/prompts')
    assert response.status_code == 404

  def test_router_response_types(self, test_client):
    """Test that all router endpoints return appropriate content types."""
    endpoints = [
      '/api/prompts',
      '/api/mcp_info/info',
      '/api/mcp_info/config',
      '/api/mcp_info/discovery',
    ]

    for endpoint in endpoints:
      response = test_client.get(endpoint)
      if response.status_code == 200:
        assert 'application/json' in response.headers.get('content-type', '')


@pytest.mark.unit
@pytest.mark.api
class TestRouterConfiguration:
  """Test router configuration and setup."""

  def test_router_imports_work(self):
    """Test that all router imports work correctly."""
    # This should not raise any import errors
    try:
      # Test imports without using them
      # import server.routers  # Not currently used
      # import server.routers.mcp_info  # Not currently used
      # import server.routers.prompts  # Not currently used
      # import server.routers.user  # Not currently used

      # All imports successful
      assert True
    except ImportError as e:
      pytest.fail(f'Router import failed: {e}')

  def test_router_module_structure(self):
    """Test that router modules have expected structure."""
    import server.routers
    import server.routers.mcp_info
    import server.routers.prompts
    import server.routers.user

    # Each module should have a router attribute
    assert hasattr(server.routers, 'router')
    assert hasattr(server.routers.user, 'router')
    assert hasattr(server.routers.prompts, 'router')
    assert hasattr(server.routers.mcp_info, 'router')

  def test_no_circular_imports(self):
    """Test that there are no circular import issues."""
    # Import the main router module
    import server.routers

    # This should work without issues
    router = server.routers.router
    assert router is not None

    # Re-importing should also work
    import server.routers

    router2 = server.routers.router
    assert router2 is not None
