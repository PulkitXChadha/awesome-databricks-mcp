"""Unit tests for MCP tools loading system."""

from unittest.mock import patch

import pytest


@pytest.mark.unit
@pytest.mark.tools
class TestToolsLoadingSystem:
  """Test the overall MCP tools loading system."""

  def test_load_tools_function_exists_and_callable(self):
    """Test that load_tools function exists and is callable."""
    from server.tools import load_tools

    assert callable(load_tools)

  def test_load_tools_calls_all_module_loaders(self, mcp_server):
    """Test that load_tools calls all module loader functions."""
    with (
      patch('server.tools.core.load_core_tools') as mock_core,
      patch('server.tools.sql_operations.load_sql_tools') as mock_sql,
      patch('server.tools.unity_catalog.load_uc_tools') as mock_uc,
      patch('server.tools.jobs_pipelines.load_job_tools') as mock_jobs,
      patch('server.tools.workspace_files.load_workspace_tools') as mock_workspace,
      patch('server.tools.dashboards.load_dashboard_tools') as mock_dashboards,
      patch('server.tools.repositories.load_repo_tools') as mock_repos,
    ):
      from server.tools import load_tools

      load_tools(mcp_server)

      # Verify all module loaders were called
      mock_core.assert_called_once_with(mcp_server)
      mock_sql.assert_called_once_with(mcp_server)
      mock_uc.assert_called_once_with(mcp_server)
      mock_jobs.assert_called_once_with(mcp_server)
      mock_workspace.assert_called_once_with(mcp_server)
      mock_dashboards.assert_called_once_with(mcp_server)
      mock_repos.assert_called_once_with(mcp_server)

  def test_load_tools_with_real_modules(self, mcp_server):
    """Test loading tools with real module implementations."""
    from server.tools import load_tools

    # Load all tools
    load_tools(mcp_server)

    # Verify that tools were actually registered
    assert len(mcp_server.tools) > 0

    # Check for expected core tools
    tool_names = list(mcp_server.tools.keys())
    assert 'health' in tool_names

    # Check for expected UC tools
    uc_tools = ['list_uc_catalogs', 'describe_uc_catalog', 'describe_uc_schema']
    for tool in uc_tools:
      assert tool in tool_names

    # Check for expected SQL tools
    sql_tools = ['execute_dbsql', 'list_warehouses']
    for tool in sql_tools:
      assert tool in tool_names

    # Check for expected dashboard tools
    dashboard_tools = ['list_lakeview_dashboards', 'get_lakeview_dashboard']
    for tool in dashboard_tools:
      assert tool in tool_names

  def test_tool_loading_order_independence(self):
    """Test that tool loading works regardless of call order."""
    from fastmcp import FastMCP

    from server.tools import load_tools

    # Create multiple servers and load tools
    server1 = FastMCP(name='test-server-1')
    server2 = FastMCP(name='test-server-2')

    load_tools(server1)
    load_tools(server2)

    # Both servers should have the same tools
    assert len(server1.tools) == len(server2.tools)
    assert set(server1.tools.keys()) == set(server2.tools.keys())

  def test_tool_registration_integrity(self, mcp_server):
    """Test that all registered tools have proper structure."""
    from server.tools import load_tools

    load_tools(mcp_server)

    for tool_name, tool_info in mcp_server.tools.items():
      # Each tool should have a callable function
      assert hasattr(tool_info, 'fn')
      assert callable(tool_info.fn)

      # Each tool should have documentation
      assert tool_info.fn.__doc__ is not None
      assert len(tool_info.fn.__doc__.strip()) > 0

      # Tool names should be valid identifiers
      assert tool_name.isidentifier()
      assert not tool_name.startswith('_')


@pytest.mark.unit
@pytest.mark.tools
class TestIndividualModuleLoaders:
  """Test individual module loader functions."""

  def test_core_tools_loader(self, mcp_server):
    """Test core tools module loader."""
    from server.tools.core import load_core_tools

    initial_count = len(mcp_server.tools)
    load_core_tools(mcp_server)

    # Should have added at least the health tool
    assert len(mcp_server.tools) > initial_count
    assert 'health' in mcp_server.tools

  def test_sql_tools_loader(self, mcp_server):
    """Test SQL tools module loader."""
    from server.tools.sql_operations import load_sql_tools

    initial_count = len(mcp_server.tools)
    load_sql_tools(mcp_server)

    # Should have added SQL tools
    assert len(mcp_server.tools) > initial_count
    assert 'execute_dbsql' in mcp_server.tools
    assert 'list_warehouses' in mcp_server.tools

  def test_uc_tools_loader(self, mcp_server):
    """Test Unity Catalog tools module loader."""
    from server.tools.unity_catalog import load_uc_tools

    initial_count = len(mcp_server.tools)
    load_uc_tools(mcp_server)

    # Should have added UC tools
    assert len(mcp_server.tools) > initial_count
    assert 'list_uc_catalogs' in mcp_server.tools
    assert 'describe_uc_catalog' in mcp_server.tools

  def test_dashboard_tools_loader(self, mcp_server):
    """Test dashboard tools module loader."""
    from server.tools.dashboards import load_dashboard_tools

    initial_count = len(mcp_server.tools)
    load_dashboard_tools(mcp_server)

    # Should have added dashboard tools
    assert len(mcp_server.tools) > initial_count
    assert 'list_lakeview_dashboards' in mcp_server.tools

  def test_jobs_tools_loader(self, mcp_server):
    """Test jobs/pipelines tools module loader."""
    from server.tools.jobs_pipelines import load_job_tools

    initial_count = len(mcp_server.tools)
    load_job_tools(mcp_server)

    # Jobs module might not add tools if they're commented out
    # This test verifies the loader function works without errors
    assert len(mcp_server.tools) >= initial_count

  def test_workspace_tools_loader(self, mcp_server):
    """Test workspace files tools module loader."""
    from server.tools.workspace_files import load_workspace_tools

    initial_count = len(mcp_server.tools)
    load_workspace_tools(mcp_server)

    # Workspace module might not add tools if they're commented out
    # This test verifies the loader function works without errors
    assert len(mcp_server.tools) >= initial_count

  def test_repositories_tools_loader(self, mcp_server):
    """Test repositories tools module loader."""
    from server.tools.repositories import load_repo_tools

    initial_count = len(mcp_server.tools)
    load_repo_tools(mcp_server)

    # Repository module might not add tools if they're commented out
    # This test verifies the loader function works without errors
    assert len(mcp_server.tools) >= initial_count


@pytest.mark.unit
@pytest.mark.tools
class TestToolsModuleStructure:
  """Test tools module structure and imports."""

  def test_tools_module_imports(self):
    """Test that tools module imports work correctly."""
    # Test main tools module import
    import server.tools

    assert hasattr(server.tools, 'load_tools')

    # Test individual module imports
    from server.tools import core, dashboards, sql_operations, unity_catalog

    assert hasattr(core, 'load_core_tools')
    assert hasattr(sql_operations, 'load_sql_tools')
    assert hasattr(unity_catalog, 'load_uc_tools')
    assert hasattr(dashboards, 'load_dashboard_tools')

  def test_tools_init_module_exports(self):
    """Test that tools __init__.py exports expected functions."""
    from server.tools import (
      load_core_tools,
      load_dashboard_tools,
      load_job_tools,
      load_repo_tools,
      load_sql_tools,
      load_tools,
      load_uc_tools,
      load_workspace_tools,
    )

    # All imports should succeed and be callable
    loaders = [
      load_core_tools,
      load_sql_tools,
      load_uc_tools,
      load_job_tools,
      load_workspace_tools,
      load_dashboard_tools,
      load_repo_tools,
      load_tools,
    ]

    for loader in loaders:
      assert callable(loader)

  def test_commented_modules_dont_break_loading(self, mcp_server):
    """Test that modules with commented code don't break tool loading."""
    from server.tools import load_tools

    # This should work even if some modules have all tools commented out
    try:
      load_tools(mcp_server)
      # If we get here, loading succeeded
      assert True
    except Exception as e:
      pytest.fail(f'Tool loading failed due to commented modules: {e}')


@pytest.mark.integration
@pytest.mark.tools
class TestToolsLoadingIntegration:
  """Integration tests for tools loading system."""

  def test_complete_tools_loading_workflow(self):
    """Test complete workflow of loading all tools."""
    from fastmcp import FastMCP

    from server.tools import load_tools

    # Create fresh MCP server
    server = FastMCP(name='integration-test-server')

    # Load all tools
    load_tools(server)

    # Verify comprehensive tool set
    tool_names = list(server.tools.keys())

    # Should have tools from multiple categories
    categories = {
      'core': ['health'],
      'sql': ['execute_dbsql', 'list_warehouses'],
      'uc': ['list_uc_catalogs', 'describe_uc_catalog'],
      'dashboards': ['list_lakeview_dashboards'],
    }

    for category, expected_tools in categories.items():
      for tool in expected_tools:
        assert tool in tool_names, f'Missing {category} tool: {tool}'

  def test_tools_loading_performance(self):
    """Test that tools loading completes in reasonable time."""
    import time

    from fastmcp import FastMCP

    from server.tools import load_tools

    server = FastMCP(name='performance-test-server')

    start_time = time.time()
    load_tools(server)
    end_time = time.time()

    loading_time = end_time - start_time

    # Tool loading should complete in under 5 seconds
    assert loading_time < 5.0, f'Tool loading took too long: {loading_time:.2f}s'

    # Should have loaded multiple tools
    assert len(server.tools) > 10, f'Expected more tools, got {len(server.tools)}'

  def test_tools_work_after_loading(self, mock_databricks_client):
    """Test that tools are functional after loading."""
    from fastmcp import FastMCP

    from server.tools import load_tools

    server = FastMCP(name='functional-test-server')
    load_tools(server)

    # Test health tool works
    health_tool = server.tools['health'].fn
    result = health_tool()
    assert result['status'] == 'healthy'

    # Test UC tool with mocked client
    uc_tool = server.tools['list_uc_catalogs'].fn

    mock_databricks_client.catalogs.list.return_value = []

    with patch('server.tools.unity_catalog.WorkspaceClient', return_value=mock_databricks_client):
      result = uc_tool()
      assert result['success'] is True
      assert result['count'] == 0
