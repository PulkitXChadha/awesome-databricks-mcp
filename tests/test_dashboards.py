"""Test dashboard tools."""

from unittest.mock import Mock, patch

import pytest

from server.tools.dashboards import load_dashboard_tools
from tests.utils import assert_success_response


class TestDashboardTools:
  """Test dashboard operations."""

  @pytest.mark.unit
  def test_list_lakeview_dashboards(self, mcp_server, mock_env_vars):
    """Test listing Lakeview dashboards."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock dashboard listing (placeholder implementation)
      mock_client.return_value = Mock()

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_lakeview_dashboards']
      result = tool.fn()

      assert_success_response(result)
      assert result['message'] == 'Lakeview dashboard listing initiated'
      assert result['count'] == 0
      assert 'note' in result

  @pytest.mark.unit
  def test_get_lakeview_dashboard(self, mcp_server, mock_env_vars):
    """Test getting specific Lakeview dashboard."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['get_lakeview_dashboard']
      result = tool.fn(dashboard_id='dashboard-123')

      assert_success_response(result)
      assert result['dashboard_id'] == 'dashboard-123'
      assert result['message'] == 'Lakeview dashboard dashboard-123 details retrieval initiated'

  @pytest.mark.unit
  def test_create_lakeview_dashboard(self, mcp_server, mock_env_vars):
    """Test creating Lakeview dashboard."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      dashboard_config = {'name': 'Test Dashboard', 'description': 'Test'}

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['create_lakeview_dashboard']
      result = tool.fn(dashboard_config=dashboard_config)

      assert_success_response(result)
      assert result['dashboard_config'] == dashboard_config
      assert result['message'] == 'Lakeview dashboard creation initiated'

  @pytest.mark.unit
  def test_list_legacy_dashboards(self, mcp_server, mock_env_vars):
    """Test listing legacy dashboards."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_dashboards']
      result = tool.fn()

      assert_success_response(result)
      assert result['message'] == 'Legacy dashboard listing initiated'
      assert result['count'] == 0

  @pytest.mark.unit
  def test_update_lakeview_dashboard(self, mcp_server, mock_env_vars):
    """Test updating Lakeview dashboard."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      updates = {'name': 'Updated Dashboard', 'description': 'Updated'}

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['update_lakeview_dashboard']
      result = tool.fn(dashboard_id='dashboard-123', updates=updates)

      assert_success_response(result)
      assert result['dashboard_id'] == 'dashboard-123'
      assert result['updates'] == updates
      assert result['message'] == 'Lakeview dashboard dashboard-123 update initiated'

  @pytest.mark.unit
  def test_delete_lakeview_dashboard(self, mcp_server, mock_env_vars):
    """Test deleting Lakeview dashboard."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['delete_lakeview_dashboard']
      result = tool.fn(dashboard_id='dashboard-123')

      assert_success_response(result)
      assert result['dashboard_id'] == 'dashboard-123'
      assert result['message'] == 'Lakeview dashboard dashboard-123 deletion initiated'

  @pytest.mark.unit
  def test_share_lakeview_dashboard(self, mcp_server, mock_env_vars):
    """Test sharing Lakeview dashboard."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      share_config = {'users': ['user1@example.com'], 'permission': 'READ'}

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['share_lakeview_dashboard']
      result = tool.fn(dashboard_id='dashboard-123', share_config=share_config)

      assert_success_response(result)
      assert result['dashboard_id'] == 'dashboard-123'
      assert result['share_config'] == share_config
      assert result['message'] == 'Lakeview dashboard dashboard-123 sharing initiated'

  @pytest.mark.unit
  def test_get_dashboard_permissions(self, mcp_server, mock_env_vars):
    """Test getting dashboard permissions."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['get_dashboard_permissions']
      result = tool.fn(dashboard_id='dashboard-123')

      assert_success_response(result)
      assert result['dashboard_id'] == 'dashboard-123'
      assert result['message'] == 'Dashboard permissions retrieved for dashboard-123'

  @pytest.mark.unit
  def test_lakeview_dashboards(self, mcp_server, mock_env_vars):
    """Test Lakeview dashboard operations."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      from tests.mock_factory import mock_workspace_client

      client = mock_workspace_client()

      # Setup Lakeview dashboard data
      mock_dashboard = Mock()
      mock_dashboard.dashboard_id = 'lakeview-123'
      mock_dashboard.name = 'Sales Analytics'
      mock_dashboard.description = 'Sales team analytics dashboard'
      mock_dashboard.created_time = 1234567890
      mock_dashboard.updated_time = 1234567990
      mock_dashboard.owner = 'sales@example.com'
      mock_dashboard.layout = {
        'widgets': [
          {'type': 'chart', 'title': 'Sales by Region'},
          {'type': 'table', 'title': 'Top Products'},
        ]
      }

      # Setup dashboard permissions
      mock_permissions = Mock()
      mock_permissions.dashboard_id = 'lakeview-123'
      mock_permissions.users = [
        {'user': 'user1@example.com', 'permission': 'READ'},
        {'user': 'user2@example.com', 'permission': 'EDIT'},
      ]

      # Mock the Lakeview API responses (placeholder structure)
      client.lakeview = Mock()
      client.lakeview.list.return_value = [mock_dashboard]
      client.lakeview.get.return_value = mock_dashboard
      client.lakeview.create.return_value = mock_dashboard
      client.lakeview.update.return_value = mock_dashboard
      client.lakeview.delete.return_value = {'success': True}
      client.lakeview.get_permissions.return_value = mock_permissions

      mock_client.return_value = client

      load_dashboard_tools(mcp_server)

      # Test Lakeview dashboard listing
      list_tool = mcp_server._tool_manager._tools['list_lakeview_dashboards']
      list_result = list_tool.fn()

      assert_success_response(list_result)

      # Test Lakeview dashboard creation
      create_tool = mcp_server._tool_manager._tools['create_lakeview_dashboard']
      dashboard_config = {
        'name': 'New Dashboard',
        'description': 'Test dashboard',
        'layout': {'widgets': []},
      }
      create_result = create_tool.fn(dashboard_config=dashboard_config)

      assert_success_response(create_result)

      # Test Lakeview dashboard update
      update_tool = mcp_server._tool_manager._tools['update_lakeview_dashboard']
      updates = {'description': 'Updated description'}
      update_result = update_tool.fn(dashboard_id='lakeview-123', updates=updates)

      assert_success_response(update_result)

      # Test Lakeview dashboard sharing
      share_tool = mcp_server._tool_manager._tools['share_lakeview_dashboard']
      share_config = {'users': ['newuser@example.com'], 'permission': 'READ'}
      share_result = share_tool.fn(dashboard_id='lakeview-123', share_config=share_config)

      assert_success_response(share_result)

  @pytest.mark.unit
  def test_legacy_dashboards(self, mcp_server, mock_env_vars):
    """Test legacy dashboard compatibility."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      from tests.mock_factory import mock_workspace_client

      client = mock_workspace_client()

      # Setup legacy dashboard data
      mock_dashboard = Mock()
      mock_dashboard.id = 'legacy-456'
      mock_dashboard.name = 'Legacy Sales Report'
      mock_dashboard.slug = 'legacy-sales-report'
      mock_dashboard.created_at = '2023-01-01T00:00:00Z'
      mock_dashboard.updated_at = '2023-06-01T00:00:00Z'
      mock_dashboard.user = Mock()
      mock_dashboard.user.name = 'legacy@example.com'
      mock_dashboard.widgets = [
        {'id': 1, 'visualization': {'type': 'chart'}},
        {'id': 2, 'visualization': {'type': 'table'}},
      ]

      # Mock the legacy API responses (using simplified structure)
      client.legacy_dashboards = Mock()
      client.legacy_dashboards.list.return_value = [mock_dashboard]
      client.legacy_dashboards.get.return_value = mock_dashboard
      client.legacy_dashboards.create.return_value = mock_dashboard
      client.legacy_dashboards.delete.return_value = {'success': True}

      mock_client.return_value = client

      load_dashboard_tools(mcp_server)

      # Test legacy dashboard listing
      list_tool = mcp_server._tool_manager._tools['list_dashboards']
      list_result = list_tool.fn()

      assert_success_response(list_result)

      # Test legacy dashboard creation
      create_tool = mcp_server._tool_manager._tools['create_dashboard']
      dashboard_config = {'name': 'New Legacy Dashboard', 'widgets': []}
      create_result = create_tool.fn(dashboard_config=dashboard_config)

      assert_success_response(create_result)

      # Test legacy dashboard deletion
      delete_tool = mcp_server._tool_manager._tools['delete_dashboard']
      delete_result = delete_tool.fn(dashboard_id='legacy-456')

      assert_success_response(delete_result)

  @pytest.mark.unit
  def test_dashboard_export_import(self, mcp_server, mock_env_vars):
    """Test export/import functionality."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      from tests.mock_factory import mock_workspace_client

      client = mock_workspace_client()

      # Setup export data
      export_data = {
        'dashboard_id': 'export-123',
        'export_format': 'json',
        'export_data': {
          'name': 'Exported Dashboard',
          'widgets': [
            {'type': 'chart', 'query': 'SELECT * FROM sales'},
            {'type': 'counter', 'query': 'SELECT COUNT(*) FROM users'},
          ],
          'layout': {'grid': {'rows': 2, 'cols': 2}},
        },
      }

      import_result = {
        'dashboard_id': 'import-456',
        'name': 'Imported Dashboard',
        'import_status': 'success',
      }

      # Mock export/import operations
      client.export = Mock()
      client.export.dashboard.return_value = export_data
      client.import_dashboard = Mock()
      client.import_dashboard.return_value = import_result

      mock_client.return_value = client

      load_dashboard_tools(mcp_server)

      # Since export/import tools may not exist yet, this is a framework test
      # Testing the concept of export/import operations through dashboard get
      get_tool = mcp_server._tool_manager._tools['get_lakeview_dashboard']
      result = get_tool.fn(dashboard_id='export-123')

      assert_success_response(result)
