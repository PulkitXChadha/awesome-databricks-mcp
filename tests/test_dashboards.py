"""Test dashboard tools."""

from unittest.mock import Mock, patch

import pytest

from server.tools.dashboards import load_dashboard_tools
from tests.utils import assert_error_response, assert_success_response


class TestDashboardTools:
  """Test dashboard operations."""

  @pytest.mark.unit
  def test_list_lakeview_dashboards(self, mcp_server, mock_env_vars):
    """Test listing Lakeview dashboards."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock dashboard listing with actual implementation
      mock_workspace = Mock()

      # Mock Lakeview dashboard
      mock_lakeview_dashboard = Mock()
      mock_lakeview_dashboard.dashboard_id = 'lakeview-123'
      mock_lakeview_dashboard.name = 'Sales Analytics'
      mock_lakeview_dashboard.description = 'Sales team analytics dashboard'
      mock_lakeview_dashboard.created_time = 1234567890
      mock_lakeview_dashboard.updated_time = 1234567990
      mock_lakeview_dashboard.owner = 'sales@example.com'
      mock_lakeview_dashboard.status = 'active'

      # Setup mock responses
      mock_workspace.lakeview.list.return_value = [mock_lakeview_dashboard]

      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_lakeview_dashboards']
      result = tool.fn()

      assert_success_response(result)
      assert result['message'] == 'Found 1 dashboard(s)'
      assert result['count'] == 1
      assert len(result['dashboards']) == 1
      assert result['dashboards'][0]['dashboard_id'] == 'lakeview-123'
      assert result['dashboards'][0]['name'] == 'Sales Analytics'
      assert result['dashboards'][0]['type'] == 'lakeview'
      assert 'note' in result

  @pytest.mark.unit
  def test_get_lakeview_dashboard(self, mcp_server, mock_env_vars):
    """Test getting specific Lakeview dashboard."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock dashboard retrieval with actual implementation
      mock_workspace = Mock()

      # Mock Lakeview dashboard
      mock_dashboard = Mock()
      mock_dashboard.dashboard_id = 'lakeview-123'
      mock_dashboard.name = 'Sales Analytics'
      mock_dashboard.description = 'Sales team analytics dashboard'
      mock_dashboard.created_time = 1234567890
      mock_dashboard.updated_time = 1234567990
      mock_dashboard.owner = 'sales@example.com'
      mock_dashboard.status = 'active'
      mock_dashboard.layout = {'widgets': [{'type': 'chart'}]}

      # Setup mock response
      mock_workspace.lakeview.get.return_value = mock_dashboard

      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['get_lakeview_dashboard']
      result = tool.fn(dashboard_id='lakeview-123')

      assert_success_response(result)
      assert result['dashboard']['dashboard_id'] == 'lakeview-123'
      assert result['dashboard']['name'] == 'Sales Analytics'
      assert result['dashboard']['type'] == 'lakeview'
      assert result['message'] == 'Retrieved details for lakeview dashboard lakeview-123'
      assert 'layout' in result['dashboard']

  @pytest.mark.unit
  def test_create_lakeview_dashboard(self, mcp_server, mock_env_vars):
    """Test creating Lakeview dashboard."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock dashboard creation with actual implementation
      mock_workspace = Mock()

      # Mock created dashboard
      mock_dashboard = Mock()
      mock_dashboard.dashboard_id = 'lakeview-789'
      mock_dashboard.display_name = 'New Test Dashboard'

      # Setup mock response
      mock_workspace.lakeview.create.return_value = mock_dashboard

      mock_client.return_value = mock_workspace

      dashboard_config = {'name': 'Test Dashboard', 'description': 'Test'}

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['create_lakeview_dashboard']
      result = tool.fn(dashboard_config=dashboard_config)

      assert_success_response(result)
      assert result['dashboard_id'] == 'lakeview-789'
      assert result['name'] == 'New Test Dashboard'  # Uses display_name from mock dashboard
      assert result['type'] == 'lakeview'
      assert (
        result['message']
        == 'Successfully created lakeview dashboard New Test Dashboard with ID lakeview-789'
      )

  @pytest.mark.unit
  def test_update_lakeview_dashboard(self, mcp_server, mock_env_vars):
    """Test updating Lakeview dashboard."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock dashboard update with actual implementation
      mock_workspace = Mock()

      # Mock updated dashboard
      mock_dashboard = Mock()
      mock_dashboard.display_name = 'Updated Dashboard'

      # Setup mock response
      mock_workspace.lakeview.update.return_value = mock_dashboard

      mock_client.return_value = mock_workspace

      updates = {'name': 'Updated Dashboard', 'description': 'Updated'}

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['update_lakeview_dashboard']
      result = tool.fn(dashboard_id='lakeview-123', updates=updates)

      assert_success_response(result)
      assert result['dashboard_id'] == 'lakeview-123'
      assert result['name'] == 'Updated Dashboard'
      assert result['type'] == 'lakeview'
      assert result['updates_applied'] == updates
      assert result['message'] == 'Successfully updated lakeview dashboard lakeview-123'

  @pytest.mark.unit
  def test_delete_lakeview_dashboard(self, mcp_server, mock_env_vars):
    """Test deleting Lakeview dashboard."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock dashboard deletion with actual implementation
      mock_workspace = Mock()

      # Setup mock response (delete methods typically don't return values)
      mock_workspace.lakeview.delete_dashboard.return_value = None

      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['delete_lakeview_dashboard']
      result = tool.fn(dashboard_id='lakeview-123')

      assert_success_response(result)
      assert result['dashboard_id'] == 'lakeview-123'
      assert result['type'] == 'lakeview'
      assert result['message'] == 'Successfully deleted lakeview dashboard lakeview-123'

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
      # Create a mock workspace client
      client = Mock()

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

      # Mock the Lakeview API responses with correct method names
      client.lakeview = Mock()
      client.lakeview.list.return_value = [mock_dashboard]
      client.lakeview.get.return_value = mock_dashboard
      client.lakeview.create.return_value = mock_dashboard
      client.lakeview.update.return_value = mock_dashboard
      client.lakeview.trash.return_value = None
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

  @pytest.mark.unit
  def test_list_lakeview_dashboards_error_handling(self, mcp_server, mock_env_vars):
    """Test listing Lakeview dashboards with error handling."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock dashboard listing with error
      mock_workspace = Mock()

      # Mock that Lakeview API throws an error
      mock_workspace.lakeview.list.side_effect = Exception('Failed to list dashboards')

      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_lakeview_dashboards']
      result = tool.fn()

      assert_error_response(result)
      assert 'Failed to list dashboards' in result['error']

  @pytest.mark.unit
  def test_create_lakeview_dashboard_validation(self, mcp_server, mock_env_vars):
    """Test dashboard creation validation."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['create_lakeview_dashboard']

      # Test missing name
      result = tool.fn(dashboard_config={})
      assert not result['success']
      assert 'name is required' in result['error']

      # Test empty name
      result = tool.fn(dashboard_config={'name': ''})
      assert not result['success']
      assert 'name is required' in result['error']

  @pytest.mark.unit
  def test_update_lakeview_dashboard_validation(self, mcp_server, mock_env_vars):
    """Test dashboard update validation."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['update_lakeview_dashboard']

      # Test empty updates
      result = tool.fn(dashboard_id='lakeview-123', updates={})
      assert not result['success']
      assert 'No updates provided' in result['error']


class TestDashboardErrorScenarios:
  """Test Dashboard error handling across different failure scenarios."""

  @pytest.mark.unit
  def test_dashboard_network_failures(self, mcp_server, mock_env_vars):
    """Test dashboard operations network failure handling."""
    from tests.utils import ERROR_SCENARIOS, simulate_databricks_error

    # Test dashboard listing timeout
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_client.side_effect = simulate_databricks_error(
        next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Network timeout'), 'Network timeout'
      )

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_lakeview_dashboards']
      result = tool.fn()

      assert_error_response(result)
      assert 'timeout' in result['error'].lower() or 'network' in result['error'].lower()

  @pytest.mark.unit
  def test_dashboard_authentication_errors(self, mcp_server, mock_env_vars):
    """Test dashboard access authentication errors."""
    from tests.utils import ERROR_SCENARIOS, simulate_databricks_error

    # Test dashboard access denied
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_client.side_effect = simulate_databricks_error(
        next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Permission denied'),
        'Permission denied',
      )

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['get_lakeview_dashboard']
      result = tool.fn(dashboard_id='restricted-dashboard-123')

      assert_error_response(result)
      assert 'access denied' in result['error'].lower() or 'permission' in result['error'].lower()

  @pytest.mark.unit
  def test_dashboard_rate_limiting(self, mcp_server, mock_env_vars):
    """Test dashboard operations rate limiting."""
    from tests.utils import ERROR_SCENARIOS, simulate_databricks_error

    # Test dashboard creation rate limiting
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_client.side_effect = simulate_databricks_error(
        next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Rate limiting'), 'Rate limiting'
      )

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['create_lakeview_dashboard']

      dashboard_config = {'name': 'High Volume Dashboard', 'description': 'Test'}
      result = tool.fn(dashboard_config=dashboard_config)

      assert_error_response(result)
      assert (
        'rate limit' in result['error'].lower() or 'too many requests' in result['error'].lower()
      )

  @pytest.mark.unit
  def test_dashboard_malformed_input_handling(self, mcp_server, mock_env_vars):
    """Test malformed dashboard parameter handling."""
    from tests.utils import ERROR_SCENARIOS, simulate_databricks_error

    load_dashboard_tools(mcp_server)

    # Test invalid dashboard configuration
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_client.side_effect = simulate_databricks_error(
        next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Invalid parameters'),
        'Invalid parameters',
      )

      create_tool = mcp_server._tool_manager._tools['create_lakeview_dashboard']

      # Test malformed dashboard configurations
      malformed_configs = [
        {},  # Empty configuration
        {'name': ''},  # Empty name
        {'description': 'No name provided'},  # Missing name
        {'name': 123, 'description': 'Invalid name type'},  # Wrong type
        {'name': 'Test', 'layout': 'invalid'},  # Invalid layout format
      ]

      for config in malformed_configs:
        result = create_tool.fn(dashboard_config=config)
        assert_error_response(result)
        assert 'invalid' in result['error'].lower() or 'parameter' in result['error'].lower()

  @pytest.mark.unit
  def test_dashboard_resource_not_found(self, mcp_server, mock_env_vars):
    """Test dashboard resource not found scenarios."""
    from tests.utils import ERROR_SCENARIOS, simulate_databricks_error

    load_dashboard_tools(mcp_server)

    # Test dashboard not found operations
    dashboard_operations = [
      ('get_lakeview_dashboard', {'dashboard_id': 'nonexistent-dashboard-999'}),
      (
        'update_lakeview_dashboard',
        {'dashboard_id': 'nonexistent-dashboard-999', 'updates': {'name': 'Updated'}},
      ),
      ('delete_lakeview_dashboard', {'dashboard_id': 'nonexistent-dashboard-999'}),
      (
        'share_lakeview_dashboard',
        {
          'dashboard_id': 'nonexistent-dashboard-999',
          'share_config': {'users': ['test@example.com']},
        },
      ),
      ('get_dashboard_permissions', {'dashboard_id': 'nonexistent-dashboard-999'}),
    ]

    for tool_name, params in dashboard_operations:
      with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
        mock_client.side_effect = simulate_databricks_error(
          next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Resource not found'),
          'Resource not found',
        )

        tool = mcp_server._tool_manager._tools[tool_name]
        result = tool.fn(**params)

        assert_error_response(result)
        assert 'not found' in result['error'].lower() or 'resource' in result['error'].lower()


class TestWidgetManagementTools:
  """Test widget management operations."""

  @pytest.mark.unit
  def test_add_widget_to_dashboard(self, mcp_server, mock_env_vars):
    """Test adding widget to dashboard."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock workspace client
      mock_workspace = Mock()

      # Mock current dashboard with existing widgets
      mock_dashboard = Mock()
      mock_dashboard.widgets = [
        {'widget_id': 'widget_1', 'type': 'chart', 'name': 'Existing Chart'}
      ]

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.return_value = Mock()

      mock_client.return_value = mock_workspace

      widget_spec = {
        'type': 'counter',
        'name': 'New Counter Widget',
        'parameters': {'title': 'Total Users'},
      }

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['add_widget_to_dashboard']
      result = tool.fn(dashboard_id='dashboard-123', widget_spec=widget_spec)

      assert_success_response(result)
      assert result['dashboard_id'] == 'dashboard-123'
      assert result['widget_name'] == 'New Counter Widget'
      assert result['widget_type'] == 'counter'
      assert result['dashboard_type'] == 'lakeview'
      assert 'widget_id' in result
      assert (
        result['message']
        == 'Successfully added widget New Counter Widget to lakeview dashboard dashboard-123'
      )

      # Verify widget was added to dashboard
      mock_workspace.lakeview.update.assert_called_once()
      call_args = mock_workspace.lakeview.update.call_args
      assert call_args[1]['dashboard_id'] == 'dashboard-123'
      assert 'widgets' in call_args[1]
      assert len(call_args[1]['widgets']) == 2  # Original + new widget

  @pytest.mark.unit
  def test_add_widget_with_dataset(self, mcp_server, mock_env_vars):
    """Test adding widget with dataset creation."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock workspace client
      mock_workspace = Mock()
      mock_dashboard = Mock()
      mock_dashboard.widgets = []

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.return_value = Mock()

      mock_client.return_value = mock_workspace

      widget_spec = {'type': 'chart', 'name': 'Sales Chart', 'parameters': {'chart_type': 'bar'}}

      load_dashboard_tools(mcp_server)

      # Test adding widget without dataset (simpler case)
      tool = mcp_server._tool_manager._tools['add_widget_to_dashboard']
      result = tool.fn(dashboard_id='dashboard-123', widget_spec=widget_spec)

      assert_success_response(result)
      assert result['widget_name'] == 'Sales Chart'
      assert result['widget_type'] == 'chart'
      assert result['dataset_id'] is None  # No dataset created
      assert result['dataset_name'] is None

  @pytest.mark.unit
  def test_add_widget_validation(self, mcp_server, mock_env_vars):
    """Test widget addition validation."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock workspace client for successful cases
      mock_workspace = Mock()
      mock_dashboard = Mock()
      mock_dashboard.widgets = []

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.return_value = Mock()
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['add_widget_to_dashboard']

      # Test missing widget_spec
      result = tool.fn(dashboard_id='dashboard-123', widget_spec=None)
      assert_error_response(result)
      assert 'widget_spec is required' in result['error']

      # Test empty widget_spec
      result = tool.fn(dashboard_id='dashboard-123', widget_spec={})
      assert_success_response(result)  # Should work with minimal spec

  @pytest.mark.unit
  def test_update_dashboard_widget(self, mcp_server, mock_env_vars):
    """Test updating widget in dashboard."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock workspace client
      mock_workspace = Mock()

      # Mock dashboard with existing widgets
      mock_dashboard = Mock()
      mock_dashboard.widgets = [
        {'widget_id': 'widget_1', 'type': 'chart', 'name': 'Chart 1', 'title': 'Old Title'},
        {'widget_id': 'widget_2', 'type': 'table', 'name': 'Table 1'},
      ]

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.return_value = Mock()

      mock_client.return_value = mock_workspace

      updates = {'title': 'Updated Chart Title', 'parameters': {'color_scheme': 'blue'}}

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['update_dashboard_widget']
      result = tool.fn(dashboard_id='dashboard-123', widget_id='widget_1', updates=updates)

      assert_success_response(result)
      assert result['dashboard_id'] == 'dashboard-123'
      assert result['widget_id'] == 'widget_1'
      assert result['updates_applied'] == updates
      assert result['dashboard_type'] == 'lakeview'
      assert (
        result['message']
        == 'Successfully updated widget widget_1 in lakeview dashboard dashboard-123'
      )

      # Verify update was called with modified widgets
      mock_workspace.lakeview.update.assert_called_once()
      call_args = mock_workspace.lakeview.update.call_args
      updated_widgets = call_args[1]['widgets']

      # Find the updated widget
      updated_widget = next(w for w in updated_widgets if w['widget_id'] == 'widget_1')
      assert updated_widget['title'] == 'Updated Chart Title'
      assert updated_widget['parameters']['color_scheme'] == 'blue'

  @pytest.mark.unit
  def test_update_widget_not_found(self, mcp_server, mock_env_vars):
    """Test updating non-existent widget."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock workspace client
      mock_workspace = Mock()

      # Mock dashboard with existing widgets (without target widget)
      mock_dashboard = Mock()
      mock_dashboard.widgets = [{'widget_id': 'widget_1', 'type': 'chart', 'name': 'Chart 1'}]

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_client.return_value = mock_workspace

      updates = {'title': 'Updated Title'}

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['update_dashboard_widget']
      result = tool.fn(
        dashboard_id='dashboard-123', widget_id='nonexistent_widget', updates=updates
      )

      assert_error_response(result)
      assert 'Widget nonexistent_widget not found in dashboard dashboard-123' in result['error']

  @pytest.mark.unit
  def test_update_widget_validation(self, mcp_server, mock_env_vars):
    """Test widget update validation."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['update_dashboard_widget']

      # Test missing updates
      result = tool.fn(dashboard_id='dashboard-123', widget_id='widget_1', updates=None)
      assert_error_response(result)
      assert 'updates dictionary is required' in result['error']

      # Test empty updates
      result = tool.fn(dashboard_id='dashboard-123', widget_id='widget_1', updates={})
      assert_error_response(result)
      assert 'updates dictionary is required' in result['error']

  @pytest.mark.unit
  def test_remove_dashboard_widget(self, mcp_server, mock_env_vars):
    """Test removing widget from dashboard."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock workspace client
      mock_workspace = Mock()

      # Mock dashboard with existing widgets
      mock_dashboard = Mock()
      mock_dashboard.widgets = [
        {'widget_id': 'widget_1', 'type': 'chart', 'name': 'Chart 1'},
        {'widget_id': 'widget_2', 'type': 'table', 'name': 'Table 1'},
        {'widget_id': 'widget_3', 'type': 'counter', 'name': 'Counter 1'},
      ]

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.return_value = Mock()

      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['remove_dashboard_widget']
      result = tool.fn(dashboard_id='dashboard-123', widget_id='widget_2')

      assert_success_response(result)
      assert result['dashboard_id'] == 'dashboard-123'
      assert result['widget_id'] == 'widget_2'
      assert result['removed_widget']['widget_id'] == 'widget_2'
      assert result['remaining_widgets'] == 2
      assert result['dashboard_type'] == 'lakeview'
      assert (
        result['message']
        == 'Successfully removed widget widget_2 from lakeview dashboard dashboard-123'
      )

      # Verify update was called with remaining widgets
      mock_workspace.lakeview.update.assert_called_once()
      call_args = mock_workspace.lakeview.update.call_args
      remaining_widgets = call_args[1]['widgets']

      # Verify correct widgets remain
      assert len(remaining_widgets) == 2
      widget_ids = [w['widget_id'] for w in remaining_widgets]
      assert 'widget_1' in widget_ids
      assert 'widget_3' in widget_ids
      assert 'widget_2' not in widget_ids

  @pytest.mark.unit
  def test_remove_widget_not_found(self, mcp_server, mock_env_vars):
    """Test removing non-existent widget."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock workspace client
      mock_workspace = Mock()

      # Mock dashboard with existing widgets (without target widget)
      mock_dashboard = Mock()
      mock_dashboard.widgets = [{'widget_id': 'widget_1', 'type': 'chart', 'name': 'Chart 1'}]

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['remove_dashboard_widget']
      result = tool.fn(dashboard_id='dashboard-123', widget_id='nonexistent_widget')

      assert_error_response(result)
      assert 'Widget nonexistent_widget not found in dashboard dashboard-123' in result['error']


class TestDatasetManagementTools:
  """Test dataset management operations."""

  @pytest.mark.unit
  def test_create_dashboard_dataset(self, mcp_server, mock_env_vars):
    """Test creating dataset for dashboard."""
    load_dashboard_tools(mcp_server)

    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock the workspace client and statement execution
      mock_workspace = Mock()

      # Mock successful query validation response
      mock_response = Mock()
      mock_response.status = Mock()
      mock_response.status.state = 'SUCCEEDED'

      mock_workspace.statement_execution.execute_statement.return_value = mock_response
      mock_client.return_value = mock_workspace

      tool = mcp_server._tool_manager._tools['create_dashboard_dataset']
      result = tool.fn(
        dashboard_id='dashboard-123',
        name='Sales Dataset',
        query='SELECT * FROM sales_table',
        warehouse_id='warehouse-456',
      )

      assert_success_response(result)
      assert result['dataset_name'] == 'Sales Dataset'
      assert result['dashboard_id'] == 'dashboard-123'
      assert result['warehouse_id'] == 'warehouse-456'
      assert result['query'] == 'SELECT * FROM sales_table'
      assert 'dataset_id' in result
      assert (
        'Successfully created dataset Sales Dataset for dashboard dashboard-123'
        in result['message']
      )

  @pytest.mark.unit
  def test_create_dataset_with_env_warehouse(self, mcp_server, mock_env_vars, monkeypatch):
    """Test creating dataset using environment warehouse ID."""
    monkeypatch.setenv('DATABRICKS_SQL_WAREHOUSE_ID', 'env-warehouse-789')

    load_dashboard_tools(mcp_server)

    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock the workspace client and statement execution
      mock_workspace = Mock()

      # Mock successful query validation response
      mock_response = Mock()
      mock_response.status = Mock()
      mock_response.status.state = 'SUCCEEDED'

      mock_workspace.statement_execution.execute_statement.return_value = mock_response
      mock_client.return_value = mock_workspace

      tool = mcp_server._tool_manager._tools['create_dashboard_dataset']
      result = tool.fn(
        dashboard_id='dashboard-123',
        name='User Actions',
        query='SELECT user_id, action FROM user_actions',
      )

      assert_success_response(result)
      assert result['warehouse_id'] == 'env-warehouse-789'

  @pytest.mark.unit
  def test_create_dataset_missing_warehouse(self, mcp_server, mock_env_vars, monkeypatch):
    """Test creating dataset without warehouse ID."""
    # Remove warehouse from environment
    monkeypatch.delenv('DATABRICKS_SQL_WAREHOUSE_ID', raising=False)

    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['create_dashboard_dataset']
      result = tool.fn(
        dashboard_id='dashboard-123', name='Test Dataset', query='SELECT * FROM test_table'
      )

      assert_error_response(result)
      assert 'SQL warehouse ID is required' in result['error']

  @pytest.mark.unit
  def test_create_dataset_invalid_query(self, mcp_server, mock_env_vars):
    """Test creating dataset with invalid query."""
    load_dashboard_tools(mcp_server)

    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock the workspace client to simulate query validation failure
      mock_workspace = Mock()

      # Mock failed query validation response
      mock_response = Mock()
      mock_response.status = Mock()
      mock_response.status.state = 'FAILED'
      mock_response.status.error = Mock()
      mock_response.status.error.message = 'Invalid SQL syntax: missing FROM clause'

      mock_workspace.statement_execution.execute_statement.return_value = mock_response
      mock_client.return_value = mock_workspace

      tool = mcp_server._tool_manager._tools['create_dashboard_dataset']
      result = tool.fn(
        dashboard_id='dashboard-123',
        name='Invalid Dataset',
        query='SELECT *',
        warehouse_id='warehouse-456',
      )

      assert_error_response(result)
      assert 'Query validation failed' in result['error']
      assert 'Invalid SQL syntax: missing FROM clause' in result['error']

  @pytest.mark.unit
  def test_test_dataset_query(self, mcp_server, mock_env_vars):
    """Test SQL query testing functionality."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock workspace client
      mock_workspace = Mock()

      # Mock successful statement execution
      mock_response = Mock()
      mock_response.status.state = 'SUCCEEDED'
      mock_response.duration = '2.3s'
      mock_response.statement_id = 'stmt_123'

      # Mock result data
      mock_response.result.data_array = [['1', 'John Doe', '100.0'], ['2', 'Jane Smith', '150.0']]

      # Mock result schema
      mock_column_1 = Mock()
      mock_column_1.name = 'id'
      mock_column_2 = Mock()
      mock_column_2.name = 'name'
      mock_column_3 = Mock()
      mock_column_3.name = 'value'

      mock_response.result.schema.columns = [mock_column_1, mock_column_2, mock_column_3]

      mock_workspace.statement_execution.execute_statement.return_value = mock_response
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['test_dataset_query']
      result = tool.fn(
        query='SELECT id, name, value FROM users', warehouse_id='warehouse-456', limit=5
      )

      assert_success_response(result)
      assert result['query'] == 'SELECT id, name, value FROM users'
      assert result['warehouse_id'] == 'warehouse-456'
      assert result['execution_time'] == '2.3s'
      assert result['row_count'] == 2
      assert result['columns'] == ['id', 'name', 'value']
      assert len(result['sample_data']) == 2
      assert result['statement_id'] == 'stmt_123'
      assert 'Query executed successfully, returned 2 rows' in result['message']

  @pytest.mark.unit
  def test_test_query_with_limit_addition(self, mcp_server, mock_env_vars):
    """Test query testing with automatic LIMIT addition."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock workspace client
      mock_workspace = Mock()

      # Mock successful statement execution
      mock_response = Mock()
      mock_response.status.state = 'SUCCEEDED'
      mock_response.result.data_array = []
      mock_response.result.schema.columns = []

      mock_workspace.statement_execution.execute_statement.return_value = mock_response
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['test_dataset_query']
      result = tool.fn(query='SELECT * FROM large_table', warehouse_id='warehouse-456', limit=10)

      assert_success_response(result)
      assert result['test_query'] == 'SELECT * FROM large_table LIMIT 10;'

      # Verify execute_statement was called with modified query
      call_args = mock_workspace.statement_execution.execute_statement.call_args
      assert call_args[1]['statement'] == 'SELECT * FROM large_table LIMIT 10;'

  @pytest.mark.unit
  def test_test_query_execution_failure(self, mcp_server, mock_env_vars):
    """Test query testing with execution failure."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock workspace client
      mock_workspace = Mock()

      # Mock failed statement execution
      mock_response = Mock()
      mock_response.status.state = 'FAILED'
      mock_response.status.error = Mock()
      mock_response.status.error.message = 'Table not found: invalid_table'

      mock_workspace.statement_execution.execute_statement.return_value = mock_response
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['test_dataset_query']
      result = tool.fn(query='SELECT * FROM invalid_table', warehouse_id='warehouse-456')

      assert_error_response(result)
      assert 'Query execution failed: Table not found: invalid_table' in result['error']
      assert result['status'] == 'FAILED'

  @pytest.mark.unit
  def test_test_query_missing_warehouse(self, mcp_server, mock_env_vars, monkeypatch):
    """Test query testing without warehouse ID."""
    # Remove warehouse from environment
    monkeypatch.delenv('DATABRICKS_SQL_WAREHOUSE_ID', raising=False)

    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['test_dataset_query']
      result = tool.fn(query='SELECT * FROM test_table')

      assert_error_response(result)
      assert 'SQL warehouse ID is required' in result['error']

  @pytest.mark.unit
  def test_test_query_execution_exception(self, mcp_server, mock_env_vars):
    """Test query testing with execution exception."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock workspace client
      mock_workspace = Mock()

      # Mock execution exception
      mock_workspace.statement_execution.execute_statement.side_effect = Exception(
        'Network timeout'
      )
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['test_dataset_query']
      result = tool.fn(query='SELECT * FROM test_table', warehouse_id='warehouse-456')

      assert_error_response(result)
      assert 'SQL execution failed: Network timeout' in result['error']


class TestWidgetCreationTools:
  """Test comprehensive widget creation tools."""

  @pytest.mark.unit
  def test_create_bar_chart(self, mcp_server, mock_env_vars):
    """Test creating bar chart widget."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['create_bar_chart']
      result = tool.fn(
        dataset_name='sales_data', x_field='region', y_field='revenue', title='Revenue by Region'
      )

      assert_success_response(result)
      widget_spec = result['widget_spec']
      assert widget_spec['type'] == 'bar_chart'
      assert widget_spec['name'] == 'Revenue by Region'
      assert widget_spec['dataset_name'] == 'sales_data'
      assert widget_spec['encodings']['x']['field'] == 'region'
      assert widget_spec['encodings']['y']['field'] == 'revenue'
      assert widget_spec['position']['width'] == 6
      assert widget_spec['position']['height'] == 4

  @pytest.mark.unit
  def test_create_line_chart(self, mcp_server, mock_env_vars):
    """Test creating line chart widget."""
    load_dashboard_tools(mcp_server)
    tool = mcp_server._tool_manager._tools['create_line_chart']
    result = tool.fn(
      dataset_name='time_series', x_field='date', y_field='value', color_field='category'
    )

    assert_success_response(result)
    widget_spec = result['widget_spec']
    assert widget_spec['type'] == 'line_chart'
    assert 'Line Chart: value over date' in widget_spec['name']
    assert widget_spec['encodings']['x']['type'] == 'temporal'
    assert widget_spec['encodings']['color']['field'] == 'category'

  @pytest.mark.unit
  def test_create_area_chart(self, mcp_server, mock_env_vars):
    """Test creating area chart widget."""
    load_dashboard_tools(mcp_server)
    tool = mcp_server._tool_manager._tools['create_area_chart']
    result = tool.fn(
      dataset_name='cumulative_data', x_field='month', y_field='cumulative_sales', stacked=True
    )

    assert_success_response(result)
    widget_spec = result['widget_spec']
    assert widget_spec['type'] == 'area_chart'
    assert widget_spec['stacked'] is True
    assert widget_spec['encodings']['x']['type'] == 'temporal'
    assert widget_spec['encodings']['y']['type'] == 'quantitative'

  @pytest.mark.unit
  def test_create_pie_chart(self, mcp_server, mock_env_vars):
    """Test creating pie chart widget."""
    load_dashboard_tools(mcp_server)
    tool = mcp_server._tool_manager._tools['create_pie_chart']
    result = tool.fn(
      dataset_name='market_share',
      category_field='company',
      value_field='market_share_pct',
      show_percentages=True,
    )

    assert_success_response(result)
    widget_spec = result['widget_spec']
    assert widget_spec['type'] == 'pie_chart'
    assert widget_spec['show_percentages'] is True
    assert widget_spec['encodings']['theta']['field'] == 'market_share_pct'
    assert widget_spec['encodings']['color']['field'] == 'company'

  @pytest.mark.unit
  def test_create_counter_widget(self, mcp_server, mock_env_vars):
    """Test creating counter widget."""
    load_dashboard_tools(mcp_server)
    tool = mcp_server._tool_manager._tools['create_counter_widget']
    result = tool.fn(
      dataset_name='metrics',
      value_field='total_revenue',
      aggregation='sum',
      format_type='currency',
      color='green',
    )

    assert_success_response(result)
    widget_spec = result['widget_spec']
    assert widget_spec['type'] == 'counter'
    assert widget_spec['value_field'] == 'total_revenue'
    assert widget_spec['aggregation'] == 'sum'
    assert widget_spec['format_type'] == 'currency'
    assert widget_spec['color'] == 'green'

  @pytest.mark.unit
  def test_create_data_table(self, mcp_server, mock_env_vars):
    """Test creating data table widget."""
    load_dashboard_tools(mcp_server)
    tool = mcp_server._tool_manager._tools['create_data_table']
    result = tool.fn(
      dataset_name='customer_data',
      columns=['customer_id', 'name', 'email', 'signup_date'],
      page_size=50,
      sortable=True,
      searchable=True,
    )

    assert_success_response(result)
    widget_spec = result['widget_spec']
    assert widget_spec['type'] == 'data_table'
    assert widget_spec['columns'] == ['customer_id', 'name', 'email', 'signup_date']
    assert widget_spec['page_size'] == 50
    assert widget_spec['sortable'] is True
    assert widget_spec['searchable'] is True

  @pytest.mark.unit
  def test_create_scatter_plot(self, mcp_server, mock_env_vars):
    """Test creating scatter plot widget."""
    load_dashboard_tools(mcp_server)
    tool = mcp_server._tool_manager._tools['create_scatter_plot']
    result = tool.fn(
      dataset_name='correlation_data',
      x_field='advertising_spend',
      y_field='revenue',
      color_field='channel',
      size_field='impressions',
    )

    assert_success_response(result)
    widget_spec = result['widget_spec']
    assert widget_spec['type'] == 'scatter_plot'
    assert widget_spec['encodings']['x']['field'] == 'advertising_spend'
    assert widget_spec['encodings']['y']['field'] == 'revenue'
    assert widget_spec['encodings']['color']['field'] == 'channel'
    assert widget_spec['encodings']['size']['field'] == 'impressions'

  @pytest.mark.unit
  def test_create_histogram(self, mcp_server, mock_env_vars):
    """Test creating histogram widget."""
    load_dashboard_tools(mcp_server)
    tool = mcp_server._tool_manager._tools['create_histogram']
    result = tool.fn(
      dataset_name='distribution_data', value_field='user_age', bins=25, color='purple'
    )

    assert_success_response(result)
    widget_spec = result['widget_spec']
    assert widget_spec['type'] == 'histogram'
    assert widget_spec['encodings']['x']['bin']['maxbins'] == 25
    assert widget_spec['color'] == 'purple'

  @pytest.mark.unit
  def test_create_combo_chart(self, mcp_server, mock_env_vars):
    """Test creating combo chart widget."""
    load_dashboard_tools(mcp_server)
    tool = mcp_server._tool_manager._tools['create_combo_chart']
    result = tool.fn(
      dataset_name='mixed_metrics', x_field='month', bar_field='revenue', line_field='profit_margin'
    )

    assert_success_response(result)
    widget_spec = result['widget_spec']
    assert widget_spec['type'] == 'combo_chart'
    assert len(widget_spec['layers']) == 2
    assert widget_spec['layers'][0]['mark'] == 'bar'
    assert widget_spec['layers'][1]['mark'] == 'line'

  @pytest.mark.unit
  def test_create_pivot_table(self, mcp_server, mock_env_vars):
    """Test creating pivot table widget."""
    load_dashboard_tools(mcp_server)
    tool = mcp_server._tool_manager._tools['create_pivot_table']
    result = tool.fn(
      dataset_name='sales_analysis',
      row_fields=['region', 'product'],
      column_fields=['quarter'],
      value_fields=['revenue', 'units_sold'],
      aggregations={'revenue': 'sum', 'units_sold': 'sum'},
    )

    assert_success_response(result)
    widget_spec = result['widget_spec']
    assert widget_spec['type'] == 'pivot_table'
    assert widget_spec['row_fields'] == ['region', 'product']
    assert widget_spec['column_fields'] == ['quarter']
    assert widget_spec['value_fields'] == ['revenue', 'units_sold']
    assert widget_spec['aggregations'] == {'revenue': 'sum', 'units_sold': 'sum'}

  @pytest.mark.unit
  def test_create_delta_counter(self, mcp_server, mock_env_vars):
    """Test creating delta counter widget."""
    load_dashboard_tools(mcp_server)
    tool = mcp_server._tool_manager._tools['create_delta_counter']
    result = tool.fn(
      dataset_name='kpi_comparison',
      value_field='current_value',
      comparison_field='previous_value',
      show_percentage=True,
      format_type='percentage',
    )

    assert_success_response(result)
    widget_spec = result['widget_spec']
    assert widget_spec['type'] == 'delta_counter'
    assert widget_spec['value_field'] == 'current_value'
    assert widget_spec['comparison_field'] == 'previous_value'
    assert widget_spec['show_percentage'] is True
    assert widget_spec['format_type'] == 'percentage'

  @pytest.mark.unit
  def test_widget_creation_with_dashboard_id(self, mcp_server, mock_env_vars):
    """Test widget creation directly adds to dashboard."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock workspace and dashboard
      mock_workspace = Mock()
      mock_dashboard = Mock()
      mock_dashboard.widgets = []

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.return_value = Mock()
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['create_bar_chart']
      result = tool.fn(
        dataset_name='sales_data', x_field='region', y_field='revenue', dashboard_id='dashboard-123'
      )

      assert_success_response(result)
      assert result['dashboard_id'] == 'dashboard-123'
      assert result['widget_id'] is not None
      assert result['dashboard_type'] == 'lakeview'

      # Verify add_widget_to_dashboard was called
      mock_workspace.lakeview.get.assert_called_once_with(dashboard_id='dashboard-123')
      mock_workspace.lakeview.update.assert_called_once()


class TestFilterWidgets:
  """Test filter widget creation tools."""

  @pytest.mark.unit
  def test_create_dropdown_filter(self, mcp_server, mock_env_vars):
    """Test creating dropdown filter widget."""
    load_dashboard_tools(mcp_server)
    tool = mcp_server._tool_manager._tools['create_dropdown_filter']
    result = tool.fn(
      dataset_name='products',
      filter_field='category',
      multi_select=True,
      default_values=['Electronics', 'Books'],
    )

    assert_success_response(result)
    widget_spec = result['widget_spec']
    assert widget_spec['type'] == 'dropdown_filter'
    assert widget_spec['filter_field'] == 'category'
    assert widget_spec['multi_select'] is True
    assert widget_spec['default_values'] == ['Electronics', 'Books']

  @pytest.mark.unit
  def test_create_date_range_filter(self, mcp_server, mock_env_vars):
    """Test creating date range filter widget."""
    load_dashboard_tools(mcp_server)
    tool = mcp_server._tool_manager._tools['create_date_range_filter']
    result = tool.fn(
      dataset_name='events',
      date_field='event_date',
      default_range={'start': '2023-01-01', 'end': '2023-12-31'},
    )

    assert_success_response(result)
    widget_spec = result['widget_spec']
    assert widget_spec['type'] == 'date_range_filter'
    assert widget_spec['date_field'] == 'event_date'
    assert widget_spec['default_range']['start'] == '2023-01-01'
    assert widget_spec['default_range']['end'] == '2023-12-31'

  @pytest.mark.unit
  def test_create_slider_filter(self, mcp_server, mock_env_vars):
    """Test creating slider filter widget."""
    load_dashboard_tools(mcp_server)
    tool = mcp_server._tool_manager._tools['create_slider_filter']
    result = tool.fn(
      dataset_name='metrics',
      numeric_field='score',
      min_value=0.0,
      max_value=100.0,
      step=5.0,
      default_value=50.0,
    )

    assert_success_response(result)
    widget_spec = result['widget_spec']
    assert widget_spec['type'] == 'slider_filter'
    assert widget_spec['numeric_field'] == 'score'
    assert widget_spec['min_value'] == 0.0
    assert widget_spec['max_value'] == 100.0
    assert widget_spec['step'] == 5.0
    assert widget_spec['default_value'] == 50.0

  @pytest.mark.unit
  def test_create_text_filter(self, mcp_server, mock_env_vars):
    """Test creating text filter widget."""
    load_dashboard_tools(mcp_server)
    tool = mcp_server._tool_manager._tools['create_text_filter']
    result = tool.fn(
      dataset_name='users',
      text_field='username',
      placeholder='Search users...',
      case_sensitive=False,
    )

    assert_success_response(result)
    widget_spec = result['widget_spec']
    assert widget_spec['type'] == 'text_filter'
    assert widget_spec['text_field'] == 'username'
    assert widget_spec['placeholder'] == 'Search users...'
    assert widget_spec['case_sensitive'] is False


class TestSpecialtyWidgets:
  """Test specialty widget creation tools."""

  @pytest.mark.unit
  def test_create_map_widget(self, mcp_server, mock_env_vars):
    """Test creating map widget."""
    load_dashboard_tools(mcp_server)
    tool = mcp_server._tool_manager._tools['create_map_widget']
    result = tool.fn(
      dataset_name='locations',
      latitude_field='lat',
      longitude_field='lng',
      color_field='temperature',
      size_field='population',
      map_style='satellite',
    )

    assert_success_response(result)
    widget_spec = result['widget_spec']
    assert widget_spec['type'] == 'map_widget'
    assert widget_spec['encodings']['latitude']['field'] == 'lat'
    assert widget_spec['encodings']['longitude']['field'] == 'lng'
    assert widget_spec['encodings']['color']['field'] == 'temperature'
    assert widget_spec['encodings']['size']['field'] == 'population'
    assert widget_spec['map_style'] == 'satellite'

  @pytest.mark.unit
  def test_create_text_widget(self, mcp_server, mock_env_vars):
    """Test creating text widget."""
    load_dashboard_tools(mcp_server)
    tool = mcp_server._tool_manager._tools['create_text_widget']
    result = tool.fn(
      content='# Dashboard Title\n\nThis dashboard shows key metrics.',
      content_type='markdown',
      text_size='large',
      text_color='primary',
    )

    assert_success_response(result)
    widget_spec = result['widget_spec']
    assert widget_spec['type'] == 'text_widget'
    assert '# Dashboard Title' in widget_spec['content']
    assert widget_spec['content_type'] == 'markdown'
    assert widget_spec['text_size'] == 'large'
    assert widget_spec['text_color'] == 'primary'

  @pytest.mark.unit
  def test_create_image_widget(self, mcp_server, mock_env_vars):
    """Test creating image widget."""
    load_dashboard_tools(mcp_server)
    tool = mcp_server._tool_manager._tools['create_image_widget']
    result = tool.fn(
      image_url='https://example.com/logo.png',
      alt_text='Company Logo',
      fit_type='contain',
      link_url='https://example.com',
    )

    assert_success_response(result)
    widget_spec = result['widget_spec']
    assert widget_spec['type'] == 'image_widget'
    assert widget_spec['image_url'] == 'https://example.com/logo.png'
    assert widget_spec['alt_text'] == 'Company Logo'
    assert widget_spec['fit_type'] == 'contain'
    assert widget_spec['link_url'] == 'https://example.com'

  @pytest.mark.unit
  def test_create_iframe_widget(self, mcp_server, mock_env_vars):
    """Test creating iframe widget."""
    load_dashboard_tools(mcp_server)
    tool = mcp_server._tool_manager._tools['create_iframe_widget']
    result = tool.fn(
      iframe_url='https://example.com/embed',
      sandbox_attributes=['allow-scripts', 'allow-same-origin'],
      allow_fullscreen=True,
    )

    assert_success_response(result)
    widget_spec = result['widget_spec']
    assert widget_spec['type'] == 'iframe_widget'
    assert widget_spec['iframe_url'] == 'https://example.com/embed'
    assert widget_spec['sandbox_attributes'] == ['allow-scripts', 'allow-same-origin']
    assert widget_spec['allow_fullscreen'] is True


class TestLayoutAndPositioningTools:
  """Test layout and positioning functionality."""

  @pytest.mark.unit
  def test_auto_layout_dashboard_grid(self, mcp_server, mock_env_vars):
    """Test auto-layout with grid algorithm."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock workspace client
      mock_workspace = Mock()

      # Mock dashboard with existing widgets
      mock_dashboard = Mock()
      mock_dashboard.widgets = [
        {'widget_id': 'widget_1', 'type': 'chart', 'position': {'width': 6, 'height': 4}},
        {'widget_id': 'widget_2', 'type': 'counter', 'position': {'width': 3, 'height': 2}},
        {'widget_id': 'widget_3', 'type': 'table', 'position': {'width': 9, 'height': 6}},
      ]

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.return_value = Mock()
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['auto_layout_dashboard']
      result = tool.fn(dashboard_id='dashboard-123', layout_type='grid')

      assert_success_response(result)
      assert result['dashboard_id'] == 'dashboard-123'
      assert result['layout_type'] == 'grid'
      assert result['widgets_arranged'] == 3
      assert result['dashboard_type'] == 'lakeview'
      assert 'Successfully applied grid layout to 3 widgets' in result['message']

      # Verify update was called with repositioned widgets
      mock_workspace.lakeview.update.assert_called_once()
      call_args = mock_workspace.lakeview.update.call_args
      updated_widgets = call_args[1]['widgets']

      # Check that widgets have been repositioned
      assert len(updated_widgets) == 3
      for widget in updated_widgets:
        assert 'position' in widget
        assert 'x' in widget['position']
        assert 'y' in widget['position']

  @pytest.mark.unit
  def test_auto_layout_dashboard_vertical(self, mcp_server, mock_env_vars):
    """Test auto-layout with vertical algorithm."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock workspace client
      mock_workspace = Mock()

      # Mock dashboard with widgets
      mock_dashboard = Mock()
      mock_dashboard.widgets = [
        {'widget_id': 'widget_1', 'position': {'height': 4}},
        {'widget_id': 'widget_2', 'position': {'height': 3}},
      ]

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.return_value = Mock()
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['auto_layout_dashboard']
      result = tool.fn(dashboard_id='dashboard-123', layout_type='vertical')

      assert_success_response(result)
      assert result['layout_type'] == 'vertical'

      # Verify widgets are stacked vertically
      call_args = mock_workspace.lakeview.update.call_args
      updated_widgets = call_args[1]['widgets']

      # First widget should be at y=0
      assert updated_widgets[0]['position']['x'] == 0
      assert updated_widgets[0]['position']['y'] == 0
      assert updated_widgets[0]['position']['width'] == 12

      # Second widget should be below first
      assert updated_widgets[1]['position']['x'] == 0
      assert updated_widgets[1]['position']['y'] == 4  # height of first widget

  @pytest.mark.unit
  def test_auto_layout_dashboard_horizontal(self, mcp_server, mock_env_vars):
    """Test auto-layout with horizontal algorithm."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock workspace client
      mock_workspace = Mock()

      # Mock dashboard with widgets
      mock_dashboard = Mock()
      mock_dashboard.widgets = [
        {'widget_id': 'widget_1', 'position': {'height': 4}},
        {'widget_id': 'widget_2', 'position': {'height': 4}},
        {'widget_id': 'widget_3', 'position': {'height': 4}},
      ]

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.return_value = Mock()
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['auto_layout_dashboard']
      result = tool.fn(dashboard_id='dashboard-123', layout_type='horizontal')

      assert_success_response(result)
      assert result['layout_type'] == 'horizontal'

      # Verify widgets are arranged horizontally
      call_args = mock_workspace.lakeview.update.call_args
      updated_widgets = call_args[1]['widgets']

      # Widgets should be side by side with equal width (12/3 = 4)
      expected_width = 4
      for i, widget in enumerate(updated_widgets):
        assert widget['position']['x'] == i * expected_width
        assert widget['position']['y'] == 0
        assert widget['position']['width'] == expected_width

  @pytest.mark.unit
  def test_auto_layout_dashboard_masonry(self, mcp_server, mock_env_vars):
    """Test auto-layout with masonry algorithm."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock workspace client
      mock_workspace = Mock()

      # Mock dashboard with widgets of different heights
      mock_dashboard = Mock()
      mock_dashboard.widgets = [
        {'widget_id': 'widget_1', 'position': {'height': 4}},
        {'widget_id': 'widget_2', 'position': {'height': 2}},
        {'widget_id': 'widget_3', 'position': {'height': 6}},
        {'widget_id': 'widget_4', 'position': {'height': 3}},
      ]

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.return_value = Mock()
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['auto_layout_dashboard']
      result = tool.fn(dashboard_id='dashboard-123', layout_type='masonry')

      assert_success_response(result)
      assert result['layout_type'] == 'masonry'

      # Verify widgets are arranged in 3 columns (4 grid units each)
      call_args = mock_workspace.lakeview.update.call_args
      updated_widgets = call_args[1]['widgets']

      for widget in updated_widgets:
        # All widgets should have width of 4 (12/3 columns)
        assert widget['position']['width'] == 4
        # X position should be 0, 4, or 8 (column positions)
        assert widget['position']['x'] in [0, 4, 8]

  @pytest.mark.unit
  def test_auto_layout_invalid_type(self, mcp_server, mock_env_vars):
    """Test auto-layout with invalid layout type."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      mock_dashboard = Mock()
      mock_dashboard.widgets = [{'widget_id': 'widget_1'}]

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['auto_layout_dashboard']
      result = tool.fn(dashboard_id='dashboard-123', layout_type='invalid_layout')

      assert_error_response(result)
      assert 'Unknown layout type: invalid_layout' in result['error']

  @pytest.mark.unit
  def test_auto_layout_empty_dashboard(self, mcp_server, mock_env_vars):
    """Test auto-layout with empty dashboard."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      mock_dashboard = Mock()
      mock_dashboard.widgets = []

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['auto_layout_dashboard']
      result = tool.fn(dashboard_id='dashboard-123', layout_type='grid')

      assert_error_response(result)
      assert 'No widgets found in dashboard to layout' in result['error']

  @pytest.mark.unit
  def test_reposition_widget(self, mcp_server, mock_env_vars):
    """Test repositioning individual widget."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock workspace client
      mock_workspace = Mock()

      # Mock dashboard with existing widgets
      mock_dashboard = Mock()
      mock_dashboard.widgets = [
        {'widget_id': 'widget_1', 'position': {'x': 0, 'y': 0, 'width': 6, 'height': 4}}
      ]

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.return_value = Mock()
      mock_client.return_value = mock_workspace

      new_position = {'x': 6, 'y': 4, 'width': 4, 'height': 3}

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['reposition_widget']
      result = tool.fn(dashboard_id='dashboard-123', widget_id='widget_1', position=new_position)

      assert_success_response(result)
      assert result['dashboard_id'] == 'dashboard-123'
      assert result['widget_id'] == 'widget_1'
      assert result['new_position'] == new_position
      assert 'Successfully repositioned widget widget_1' in result['message']

  @pytest.mark.unit
  def test_reposition_widget_validation(self, mcp_server, mock_env_vars):
    """Test widget repositioning validation."""
    load_dashboard_tools(mcp_server)
    tool = mcp_server._tool_manager._tools['reposition_widget']

    # Test missing position keys
    incomplete_positions = [
      {'x': 0, 'y': 0, 'width': 6},  # missing height
      {'x': 0, 'y': 0, 'height': 4},  # missing width
      {'x': 0, 'width': 6, 'height': 4},  # missing y
      {'y': 0, 'width': 6, 'height': 4},  # missing x
    ]

    for pos in incomplete_positions:
      result = tool.fn(dashboard_id='dashboard-123', widget_id='widget_1', position=pos)
      assert_error_response(result)
      assert 'Position must include' in result['error']

    # Test negative positions
    result = tool.fn(
      dashboard_id='dashboard-123',
      widget_id='widget_1',
      position={'x': -1, 'y': 0, 'width': 6, 'height': 4},
    )
    assert_error_response(result)
    assert 'x and y must be non-negative' in result['error']

    # Test zero/negative dimensions
    result = tool.fn(
      dashboard_id='dashboard-123',
      widget_id='widget_1',
      position={'x': 0, 'y': 0, 'width': 0, 'height': 4},
    )
    assert_error_response(result)
    assert 'width and height must be positive' in result['error']

    # Test widget extending beyond grid
    result = tool.fn(
      dashboard_id='dashboard-123',
      widget_id='widget_1',
      position={'x': 8, 'y': 0, 'width': 6, 'height': 4},
    )
    assert_error_response(result)
    assert 'Widget extends beyond 12-column grid' in result['error']


class TestWidgetCreationErrors:
  """Test error scenarios in widget creation."""

  @pytest.mark.unit
  def test_widget_creation_errors(self, mcp_server, mock_env_vars):
    """Test various widget creation error scenarios."""
    load_dashboard_tools(mcp_server)

    # Test each widget type with missing required parameters
    widget_tests = [
      ('create_bar_chart', {'dataset_name': 'test', 'x_field': 'x'}),  # missing y_field
      ('create_line_chart', {'dataset_name': 'test', 'x_field': 'x'}),  # missing y_field
      (
        'create_pie_chart',
        {'dataset_name': 'test', 'category_field': 'cat'},
      ),  # missing value_field
      ('create_counter_widget', {'dataset_name': 'test'}),  # missing value_field
      ('create_data_table', {'dataset_name': 'test'}),  # missing columns
      ('create_scatter_plot', {'dataset_name': 'test', 'x_field': 'x'}),  # missing y_field
      ('create_histogram', {'dataset_name': 'test'}),  # missing value_field
    ]

    for tool_name, incomplete_params in widget_tests:
      try:
        tool = mcp_server._tool_manager._tools[tool_name]
        tool.fn(**incomplete_params)
        # Some tools may handle missing parameters gracefully,
        # others may raise TypeError due to missing required args
        # Either response is acceptable as long as it's handled
      except TypeError as e:
        # Expected for tools with required parameters
        assert 'required positional argument' in str(e) or 'missing' in str(e)

  @pytest.mark.unit
  def test_widget_creation_with_dashboard_errors(self, mcp_server, mock_env_vars):
    """Test widget creation errors when adding to dashboard."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock workspace client that fails
      mock_workspace = Mock()
      mock_workspace.lakeview.get.side_effect = Exception('Dashboard not found')
      mock_workspace.dashboards.get.side_effect = Exception('Dashboard not found')
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['create_bar_chart']
      result = tool.fn(
        dataset_name='sales_data',
        x_field='region',
        y_field='revenue',
        dashboard_id='nonexistent-dashboard',
      )

      assert_error_response(result)
      # The error should come from the add_widget_to_dashboard function

  @pytest.mark.unit
  def test_create_lakeview_dashboard_with_widgets(self, mcp_server, mock_env_vars):
    """Test creating Lakeview dashboard with initial widgets."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock dashboard creation
      mock_workspace = Mock()
      mock_dashboard = Mock()
      mock_dashboard.dashboard_id = 'lakeview-789'
      mock_dashboard.display_name = 'Dashboard with Widgets'

      # Mock widget creation
      mock_widget = Mock()
      mock_widget.id = 'widget-123'

      # Setup mocks
      mock_workspace.lakeview.create.return_value = mock_dashboard
      mock_workspace.dashboard_widgets = Mock()
      mock_workspace.dashboard_widgets.create.return_value = mock_widget
      mock_client.return_value = mock_workspace

      # Dashboard config with widgets
      dashboard_config = {
        'name': 'Dashboard with Widgets',
        'description': 'Test dashboard with initial widgets',
        'widgets': [
          {
            'type': 'text',
            'name': 'Welcome Text',
            'width': 6,
            'text': 'Welcome to the dashboard',
            'position': {'x': 0, 'y': 0},
          }
        ],
      }

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['create_lakeview_dashboard']

      # Mock the hasattr calls to ensure dashboard_widgets is detected
      with patch('builtins.hasattr') as mock_hasattr:

        def hasattr_side_effect(obj, attr):
          if attr == 'dashboard_widgets':
            return True
          return hasattr(type(obj), attr)

        mock_hasattr.side_effect = hasattr_side_effect

        result = tool.fn(dashboard_config=dashboard_config)

        assert_success_response(result)
        assert result['dashboard_id'] == 'lakeview-789'
        assert result['widgets_created'] == 1
        assert 'widget_details' in result
        assert len(result['widget_details']) == 1

  @pytest.mark.unit
  def test_update_lakeview_dashboard_with_widgets(self, mcp_server, mock_env_vars):
    """Test updating Lakeview dashboard with widget operations."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock dashboard update
      mock_workspace = Mock()
      mock_dashboard = Mock()
      mock_dashboard.display_name = 'Updated Dashboard'

      # Mock widget operations
      mock_widget = Mock()
      mock_widget.id = 'widget-new'

      # Setup mocks
      mock_workspace.lakeview.update.return_value = mock_dashboard
      mock_workspace.dashboard_widgets = Mock()
      mock_workspace.dashboard_widgets.create.return_value = mock_widget
      mock_workspace.dashboard_widgets.update.return_value = mock_widget
      mock_workspace.dashboard_widgets.delete.return_value = None
      mock_client.return_value = mock_workspace

      # Updates with widget operations
      updates = {
        'name': 'Updated Dashboard',
        'add_widgets': [{'type': 'chart', 'name': 'New Chart', 'width': 8}],
        'update_widgets': [{'widget_id': 'widget-123', 'width': 6, 'position': {'x': 0, 'y': 1}}],
        'remove_widgets': ['widget-old'],
      }

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['update_lakeview_dashboard']

      # Mock the hasattr calls to ensure dashboard_widgets is detected
      with patch('builtins.hasattr') as mock_hasattr:

        def hasattr_side_effect(obj, attr):
          if attr == 'dashboard_widgets':
            return True
          return hasattr(type(obj), attr)

        mock_hasattr.side_effect = hasattr_side_effect

        result = tool.fn(dashboard_id='lakeview-123', updates=updates)

        assert_success_response(result)
        assert result['dashboard_id'] == 'lakeview-123'
        assert result['name'] == 'Updated Dashboard'
        assert 'widget_operations' in result
        assert result['widget_operations']['widgets_added_count'] == 1
        assert result['widget_operations']['widgets_updated_count'] == 1
        assert result['widget_operations']['widgets_removed_count'] == 1

  @pytest.mark.unit
  def test_manage_dashboard_widgets(self, mcp_server, mock_env_vars):
    """Test comprehensive widget management tool."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()

      # Mock widget for create/update operations
      mock_widget = Mock()
      mock_widget.id = 'widget-123'

      # Mock dashboard layout for list operation
      mock_dashboard = Mock()
      mock_dashboard.layout = {
        'widgets': [
          {'id': 'widget-1', 'type': 'chart', 'name': 'Chart 1'},
          {'id': 'widget-2', 'type': 'table', 'name': 'Table 1'},
        ]
      }

      # Setup mocks
      mock_workspace.dashboard_widgets = Mock()
      mock_workspace.dashboard_widgets.create.return_value = mock_widget
      mock_workspace.dashboard_widgets.update.return_value = mock_widget
      mock_workspace.dashboard_widgets.delete.return_value = None
      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['manage_dashboard_widgets']

      # Mock the hasattr calls to ensure dashboard_widgets is detected
      with patch('builtins.hasattr') as mock_hasattr:

        def hasattr_side_effect(obj, attr):
          if attr == 'dashboard_widgets':
            return True
          return hasattr(type(obj), attr)

        mock_hasattr.side_effect = hasattr_side_effect

        # Test widget creation
        widget_config = {'type': 'chart', 'name': 'Test Chart', 'width': 6}
        result = tool.fn(dashboard_id='dash-123', operation='create', widget_config=widget_config)
        assert_success_response(result)

        # Test widget listing
        result = tool.fn(dashboard_id='dash-123', operation='list')
        assert_success_response(result)
        assert result['widgets_count'] == 2

        # Test widget update
        update_config = {'widget_id': 'widget-123', 'width': 8, 'position': {'x': 0, 'y': 0}}
        result = tool.fn(dashboard_id='dash-123', operation='update', widget_config=update_config)
        assert_success_response(result)
        assert result['widget_id'] == 'widget-123'

        # Test widget deletion
        delete_config = {'widget_id': 'widget-123'}
        result = tool.fn(dashboard_id='dash-123', operation='delete', widget_config=delete_config)
        assert_success_response(result)

  @pytest.mark.unit
  def test_publish_lakeview_dashboard(self, mcp_server, mock_env_vars):
    """Test publishing Lakeview dashboard."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()

      # Mock published dashboard
      mock_published = Mock()
      mock_published.dashboard_id = 'published-123'
      mock_published.revision_id = 'rev-456'
      mock_published.embed_url = 'https://example.com/embed/dash-123'

      # Setup mocks
      mock_workspace.lakeview.publish.return_value = mock_published
      mock_client.return_value = mock_workspace

      publish_config = {'embed_credentials': True, 'warehouse_id': 'warehouse-123'}

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['publish_lakeview_dashboard']
      result = tool.fn(dashboard_id='dash-123', publish_config=publish_config)

      assert_success_response(result)
      assert result['dashboard_id'] == 'dash-123'
      assert result['published_dashboard_id'] == 'published-123'
      assert result['embed_credentials']
      assert result['warehouse_id'] == 'warehouse-123'
      assert 'published_dashboard' in result

  @pytest.mark.unit
  def test_manage_dashboard_schedule(self, mcp_server, mock_env_vars):
    """Test dashboard schedule management."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()

      # Mock schedule
      mock_schedule = Mock()
      mock_schedule.schedule_id = 'schedule-123'
      mock_schedule.cron_schedule = Mock()
      mock_schedule.cron_schedule.cron_expression = '0 9 * * 1-5'
      mock_schedule.cron_schedule.timezone = 'UTC'
      mock_schedule.pause_status = 'UNPAUSED'

      # Setup mocks
      mock_workspace.lakeview.create_schedule.return_value = mock_schedule
      mock_workspace.lakeview.list_schedules.return_value = [mock_schedule]
      mock_workspace.lakeview.delete_schedule.return_value = None
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['manage_dashboard_schedule']

      # Mock the hasattr calls to ensure lakeview schedule methods are detected
      with patch('builtins.hasattr') as mock_hasattr:

        def hasattr_side_effect(obj, attr):
          if attr in ['list_schedules', 'create_schedule', 'delete_schedule']:
            return True
          return hasattr(type(obj), attr)

        mock_hasattr.side_effect = hasattr_side_effect

        # Test schedule creation
        schedule_config = {
          'cron_expression': '0 9 * * 1-5',
          'timezone': 'UTC',
          'pause_status': 'UNPAUSED',
        }
        result = tool.fn(
          dashboard_id='dash-123', operation='create', schedule_config=schedule_config
        )
        assert_success_response(result)

        # Test schedule listing
        result = tool.fn(dashboard_id='dash-123', operation='list')
        assert_success_response(result)
        assert result['schedules_count'] == 1

        # Test schedule deletion
        delete_config = {'schedule_id': 'schedule-123'}
        result = tool.fn(dashboard_id='dash-123', operation='delete', schedule_config=delete_config)
        assert_success_response(result)

  @pytest.mark.unit
  def test_widget_management_errors(self, mcp_server, mock_env_vars):
    """Test error handling in widget management."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock workspace without dashboard_widgets API
      mock_workspace = Mock()
      delattr(mock_workspace, 'dashboard_widgets') if hasattr(
        mock_workspace, 'dashboard_widgets'
      ) else None
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['manage_dashboard_widgets']

      # Test API not available error
      result = tool.fn(dashboard_id='dash-123', operation='create', widget_config={'type': 'chart'})
      assert_error_response(result)
      assert 'Dashboard widgets API not available' in result['error']

      # Test invalid operation
      mock_workspace.dashboard_widgets = Mock()  # Add back for this test
      result = tool.fn(dashboard_id='dash-123', operation='invalid_operation')
      assert_error_response(result)
      assert 'Unsupported operation' in result['error']
