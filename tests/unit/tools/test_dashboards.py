"""Unit tests for Dashboard MCP tools."""

from unittest.mock import Mock, patch

import pytest


@pytest.mark.unit
@pytest.mark.tools
class TestDashboardTools:
  """Test Dashboard MCP tools functionality."""

  def test_load_dashboard_tools_registers_all_tools(self, mcp_server):
    """Test that load_dashboard_tools registers all expected tools."""
    from server.tools.dashboards import load_dashboard_tools

    load_dashboard_tools(mcp_server)

    expected_tools = [
      'list_lakeview_dashboards',
      'get_lakeview_dashboard',
      'create_lakeview_dashboard',
      'update_lakeview_dashboard',
      'delete_lakeview_dashboard',
      'list_dashboards',
      'get_dashboard',
      'create_dashboard',
      'delete_dashboard',
    ]

    tool_names = list(mcp_server.tools.keys())
    for tool_name in expected_tools:
      assert tool_name in tool_names


@pytest.mark.unit
@pytest.mark.tools
class TestLakeviewDashboards:
  """Test Lakeview dashboard tools."""

  def test_list_lakeview_dashboards_placeholder_response(self, mcp_server, mock_databricks_client):
    """Test list_lakeview_dashboards returns placeholder response."""
    from server.tools.dashboards import load_dashboard_tools

    load_dashboard_tools(mcp_server)

    tool = mcp_server.tools['list_lakeview_dashboards'].fn

    with patch('server.tools.dashboards.WorkspaceClient', return_value=mock_databricks_client):
      result = tool()

    assert result['success'] is True
    assert result['count'] == 0
    assert result['dashboards'] == []
    assert 'Lakeview dashboard listing initiated' in result['message']
    assert 'specific permissions' in result['note']

  def test_get_lakeview_dashboard_placeholder_response(self, mcp_server, mock_databricks_client):
    """Test get_lakeview_dashboard returns placeholder response."""
    from server.tools.dashboards import load_dashboard_tools

    load_dashboard_tools(mcp_server)

    tool = mcp_server.tools['get_lakeview_dashboard'].fn

    with patch('server.tools.dashboards.WorkspaceClient', return_value=mock_databricks_client):
      result = tool('test-dashboard-id')

    assert result['success'] is True
    assert 'dashboard_id' in result
    assert result['dashboard_id'] == 'test-dashboard-id'
    assert 'placeholder' in result['note']

  def test_create_lakeview_dashboard_placeholder_response(self, mcp_server, mock_databricks_client):
    """Test create_lakeview_dashboard returns placeholder response."""
    from server.tools.dashboards import load_dashboard_tools

    load_dashboard_tools(mcp_server)

    tool = mcp_server.tools['create_lakeview_dashboard'].fn

    dashboard_config = {'name': 'Test Dashboard', 'description': 'Test description'}

    with patch('server.tools.dashboards.WorkspaceClient', return_value=mock_databricks_client):
      result = tool(dashboard_config)

    assert result['success'] is True
    assert 'placeholder' in result['note']
    assert 'config' in result
    assert result['config'] == dashboard_config

  def test_update_lakeview_dashboard_placeholder_response(self, mcp_server, mock_databricks_client):
    """Test update_lakeview_dashboard returns placeholder response."""
    from server.tools.dashboards import load_dashboard_tools

    load_dashboard_tools(mcp_server)

    tool = mcp_server.tools['update_lakeview_dashboard'].fn

    updates = {'name': 'Updated Dashboard Name'}

    with patch('server.tools.dashboards.WorkspaceClient', return_value=mock_databricks_client):
      result = tool('test-dashboard-id', updates)

    assert result['success'] is True
    assert result['dashboard_id'] == 'test-dashboard-id'
    assert result['updates'] == updates
    assert 'placeholder' in result['note']

  def test_delete_lakeview_dashboard_placeholder_response(self, mcp_server, mock_databricks_client):
    """Test delete_lakeview_dashboard returns placeholder response."""
    from server.tools.dashboards import load_dashboard_tools

    load_dashboard_tools(mcp_server)

    tool = mcp_server.tools['delete_lakeview_dashboard'].fn

    with patch('server.tools.dashboards.WorkspaceClient', return_value=mock_databricks_client):
      result = tool('test-dashboard-id')

    assert result['success'] is True
    assert result['dashboard_id'] == 'test-dashboard-id'
    assert 'placeholder' in result['note']


@pytest.mark.unit
@pytest.mark.tools
class TestLegacyDashboards:
  """Test legacy dashboard tools."""

  def test_list_dashboards_placeholder_response(self, mcp_server, mock_databricks_client):
    """Test list_dashboards returns placeholder response."""
    from server.tools.dashboards import load_dashboard_tools

    load_dashboard_tools(mcp_server)

    tool = mcp_server.tools['list_dashboards'].fn

    with patch('server.tools.dashboards.WorkspaceClient', return_value=mock_databricks_client):
      result = tool()

    assert result['success'] is True
    assert result['count'] == 0
    assert result['dashboards'] == []
    assert 'legacy dashboard listing initiated' in result['message']

  def test_get_dashboard_placeholder_response(self, mcp_server, mock_databricks_client):
    """Test get_dashboard returns placeholder response."""
    from server.tools.dashboards import load_dashboard_tools

    load_dashboard_tools(mcp_server)

    tool = mcp_server.tools['get_dashboard'].fn

    with patch('server.tools.dashboards.WorkspaceClient', return_value=mock_databricks_client):
      result = tool('test-dashboard-id')

    assert result['success'] is True
    assert result['dashboard_id'] == 'test-dashboard-id'
    assert 'placeholder' in result['note']

  def test_create_dashboard_placeholder_response(self, mcp_server, mock_databricks_client):
    """Test create_dashboard returns placeholder response."""
    from server.tools.dashboards import load_dashboard_tools

    load_dashboard_tools(mcp_server)

    tool = mcp_server.tools['create_dashboard'].fn

    dashboard_config = {'name': 'Test Legacy Dashboard', 'queries': []}

    with patch('server.tools.dashboards.WorkspaceClient', return_value=mock_databricks_client):
      result = tool(dashboard_config)

    assert result['success'] is True
    assert 'placeholder' in result['note']
    assert result['config'] == dashboard_config

  def test_delete_dashboard_placeholder_response(self, mcp_server, mock_databricks_client):
    """Test delete_dashboard returns placeholder response."""
    from server.tools.dashboards import load_dashboard_tools

    load_dashboard_tools(mcp_server)

    tool = mcp_server.tools['delete_dashboard'].fn

    with patch('server.tools.dashboards.WorkspaceClient', return_value=mock_databricks_client):
      result = tool('test-dashboard-id')

    assert result['success'] is True
    assert result['dashboard_id'] == 'test-dashboard-id'
    assert 'placeholder' in result['note']


@pytest.mark.unit
@pytest.mark.tools
class TestDashboardErrorHandling:
  """Test error handling in dashboard tools."""

  def test_list_lakeview_dashboards_error_handling(self, mcp_server):
    """Test error handling in list_lakeview_dashboards."""
    from server.tools.dashboards import load_dashboard_tools

    load_dashboard_tools(mcp_server)

    tool = mcp_server.tools['list_lakeview_dashboards'].fn

    with patch(
      'server.tools.dashboards.WorkspaceClient', side_effect=Exception('Connection failed')
    ):
      result = tool()

    assert result['success'] is False
    assert 'error' in result
    assert 'Connection failed' in result['error']
    assert result['dashboards'] == []
    assert result['count'] == 0

  def test_get_lakeview_dashboard_error_handling(self, mcp_server):
    """Test error handling in get_lakeview_dashboard."""
    from server.tools.dashboards import load_dashboard_tools

    load_dashboard_tools(mcp_server)

    tool = mcp_server.tools['get_lakeview_dashboard'].fn

    with patch(
      'server.tools.dashboards.WorkspaceClient', side_effect=Exception('Dashboard not found')
    ):
      result = tool('nonexistent-dashboard')

    assert result['success'] is False
    assert 'error' in result
    assert 'Dashboard not found' in result['error']

  def test_workspace_client_initialization_error(self, mcp_server):
    """Test error handling when WorkspaceClient initialization fails."""
    from server.tools.dashboards import load_dashboard_tools

    load_dashboard_tools(mcp_server)

    # Test with various dashboard tools
    dashboard_tools = [
      'list_lakeview_dashboards',
      'get_lakeview_dashboard',
      'list_dashboards',
      'get_dashboard',
    ]

    for tool_name in dashboard_tools:
      tool = mcp_server.tools[tool_name].fn

      with patch('server.tools.dashboards.WorkspaceClient', side_effect=Exception('Auth failed')):
        if tool_name in ['get_lakeview_dashboard', 'get_dashboard']:
          result = tool('test-id')
        else:
          result = tool()

      assert result['success'] is False
      assert 'error' in result
      assert 'Auth failed' in result['error']


@pytest.mark.unit
@pytest.mark.tools
class TestDashboardToolsMetadata:
  """Test dashboard tools metadata and documentation."""

  def test_all_dashboard_tools_have_documentation(self, mcp_server):
    """Test that all dashboard tools have proper documentation."""
    from server.tools.dashboards import load_dashboard_tools

    load_dashboard_tools(mcp_server)

    for tool_name, tool_info in mcp_server.tools.items():
      assert tool_info.fn.__doc__ is not None
      assert len(tool_info.fn.__doc__.strip()) > 0

      # Check that documentation mentions key concepts
      doc = tool_info.fn.__doc__.lower()
      if 'lakeview' in tool_name:
        assert 'lakeview' in doc
      elif 'dashboard' in tool_name:
        assert 'dashboard' in doc


@pytest.mark.integration
@pytest.mark.tools
class TestDashboardToolsIntegration:
  """Integration tests for dashboard tools."""

  def test_all_dashboard_tools_load_successfully(self):
    """Test that all dashboard tools can be loaded without errors."""
    from fastmcp import FastMCP

    from server.tools.dashboards import load_dashboard_tools

    test_server = FastMCP(name='test-dashboard-tools')

    # Should not raise any exceptions
    load_dashboard_tools(test_server)

    # Verify tools were loaded
    assert len(test_server.tools) > 0

    expected_tools = ['list_lakeview_dashboards', 'get_lakeview_dashboard', 'list_dashboards']
    for tool_name in expected_tools:
      assert tool_name in test_server.tools

  def test_dashboard_tools_with_environment_setup(self, mcp_server, mock_environment):
    """Test dashboard tools work with proper environment setup."""
    from server.tools.dashboards import load_dashboard_tools

    load_dashboard_tools(mcp_server)

    # Test that tools can be called with environment variables set
    list_tool = mcp_server.tools['list_lakeview_dashboards'].fn

    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()
      list_tool()

      # Verify WorkspaceClient was initialized with correct parameters
      mock_client.assert_called_once_with(
        host=mock_environment['DATABRICKS_HOST'], token=mock_environment['DATABRICKS_TOKEN']
      )
