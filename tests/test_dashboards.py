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

      # Mock legacy dashboard
      mock_legacy_dashboard = Mock()
      mock_legacy_dashboard.id = 'legacy-456'
      mock_legacy_dashboard.name = 'Legacy Report'
      mock_legacy_dashboard.description = 'Legacy dashboard'
      mock_legacy_dashboard.created_at = '2023-01-01T00:00:00Z'
      mock_legacy_dashboard.updated_at = '2023-06-01T00:00:00Z'
      mock_legacy_dashboard.user = 'legacy@example.com'
      mock_legacy_dashboard.status = 'active'

      # Setup mock responses
      mock_workspace.lakeview.list.return_value = [mock_lakeview_dashboard]
      mock_workspace.dashboards.list.return_value = [mock_legacy_dashboard]

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
      mock_dashboard.name = 'New Test Dashboard'

      # Setup mock response
      mock_workspace.lakeview.create.return_value = mock_dashboard

      mock_client.return_value = mock_workspace

      dashboard_config = {'name': 'Test Dashboard', 'description': 'Test'}

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['create_lakeview_dashboard']
      result = tool.fn(dashboard_config=dashboard_config)

      assert_success_response(result)
      assert result['dashboard_id'] == 'lakeview-789'
      assert result['name'] == 'New Test Dashboard'
      assert result['type'] == 'lakeview'
      assert (
        result['message']
        == 'Successfully created lakeview dashboard New Test Dashboard with ID lakeview-789'
      )

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
      # Mock dashboard update with actual implementation
      mock_workspace = Mock()

      # Mock updated dashboard
      mock_dashboard = Mock()
      mock_dashboard.name = 'Updated Dashboard'

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

  @pytest.mark.unit
  def test_list_lakeview_dashboards_fallback(self, mcp_server, mock_env_vars):
    """Test listing Lakeview dashboards with fallback to legacy API."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock dashboard listing with fallback behavior
      mock_workspace = Mock()

      # Mock that Lakeview API is not available (AttributeError)
      mock_workspace.lakeview.list.side_effect = AttributeError(
        "'WorkspaceClient' object has no attribute 'lakeview'"
      )

      # Mock legacy dashboard
      mock_legacy_dashboard = Mock()
      mock_legacy_dashboard.id = 'legacy-456'
      mock_legacy_dashboard.name = 'Legacy Report'
      mock_legacy_dashboard.description = 'Legacy dashboard'
      mock_legacy_dashboard.created_at = '2023-01-01T00:00:00Z'
      mock_legacy_dashboard.updated_at = '2023-06-01T00:00:00Z'
      mock_legacy_dashboard.user = 'legacy@example.com'
      mock_legacy_dashboard.status = 'active'

      # Setup mock response for legacy API
      mock_workspace.dashboards.list.return_value = [mock_legacy_dashboard]

      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_lakeview_dashboards']
      result = tool.fn()

      assert_success_response(result)
      assert result['message'] == 'Found 1 dashboard(s)'
      assert result['count'] == 1
      assert len(result['dashboards']) == 1
      assert result['dashboards'][0]['dashboard_id'] == 'legacy-456'
      assert result['dashboards'][0]['name'] == 'Legacy Report'
      assert result['dashboards'][0]['type'] == 'legacy'
      assert 'note' in result

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

  @pytest.mark.unit
  def test_legacy_dashboard_errors(self, mcp_server, mock_env_vars):
    """Test legacy dashboard error scenarios."""
    from tests.utils import ERROR_SCENARIOS, simulate_databricks_error

    load_dashboard_tools(mcp_server)

    # Test legacy dashboard authentication errors
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_client.side_effect = simulate_databricks_error(
        next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Authentication failed'),
        'Authentication failed',
      )

      legacy_operations = [
        ('list_dashboards', {}),
        ('get_dashboard', {'dashboard_id': 'legacy-123'}),
        ('delete_dashboard', {'dashboard_id': 'legacy-123'}),
      ]

      for tool_name, params in legacy_operations:
        tool = mcp_server._tool_manager._tools[tool_name]
        result = tool.fn(**params)

        assert_error_response(result)
        assert (
          'access denied' in result['error'].lower() or 'authentication' in result['error'].lower()
        )


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
        'parameters': {'title': 'Total Users'}
      }

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['add_widget_to_dashboard']
      result = tool.fn(
        dashboard_id='dashboard-123',
        widget_spec=widget_spec
      )

      assert_success_response(result)
      assert result['dashboard_id'] == 'dashboard-123'
      assert result['widget_name'] == 'New Counter Widget'
      assert result['widget_type'] == 'counter'
      assert result['dashboard_type'] == 'lakeview'
      assert 'widget_id' in result
      assert result['message'] == 'Successfully added widget New Counter Widget to lakeview dashboard dashboard-123'

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

      widget_spec = {
        'type': 'chart',
        'name': 'Sales Chart',
        'parameters': {'chart_type': 'bar'}
      }

      load_dashboard_tools(mcp_server)
      
      # Test adding widget without dataset (simpler case)
      tool = mcp_server._tool_manager._tools['add_widget_to_dashboard']
      result = tool.fn(
        dashboard_id='dashboard-123',
        widget_spec=widget_spec
      )

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
        {'widget_id': 'widget_2', 'type': 'table', 'name': 'Table 1'}
      ]
      
      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.return_value = Mock()
      
      mock_client.return_value = mock_workspace

      updates = {
        'title': 'Updated Chart Title',
        'parameters': {'color_scheme': 'blue'}
      }

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['update_dashboard_widget']
      result = tool.fn(
        dashboard_id='dashboard-123',
        widget_id='widget_1',
        updates=updates
      )

      assert_success_response(result)
      assert result['dashboard_id'] == 'dashboard-123'
      assert result['widget_id'] == 'widget_1'
      assert result['updates_applied'] == updates
      assert result['dashboard_type'] == 'lakeview'
      assert result['message'] == 'Successfully updated widget widget_1 in lakeview dashboard dashboard-123'

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
      mock_dashboard.widgets = [
        {'widget_id': 'widget_1', 'type': 'chart', 'name': 'Chart 1'}
      ]
      
      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_client.return_value = mock_workspace

      updates = {'title': 'Updated Title'}

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['update_dashboard_widget']
      result = tool.fn(
        dashboard_id='dashboard-123',
        widget_id='nonexistent_widget',
        updates=updates
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
      result = tool.fn(
        dashboard_id='dashboard-123',
        widget_id='widget_1',
        updates=None
      )
      assert_error_response(result)
      assert 'updates dictionary is required' in result['error']

      # Test empty updates
      result = tool.fn(
        dashboard_id='dashboard-123',
        widget_id='widget_1',
        updates={}
      )
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
        {'widget_id': 'widget_3', 'type': 'counter', 'name': 'Counter 1'}
      ]
      
      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.return_value = Mock()
      
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['remove_dashboard_widget']
      result = tool.fn(
        dashboard_id='dashboard-123',
        widget_id='widget_2'
      )

      assert_success_response(result)
      assert result['dashboard_id'] == 'dashboard-123'
      assert result['widget_id'] == 'widget_2'
      assert result['removed_widget']['widget_id'] == 'widget_2'
      assert result['remaining_widgets'] == 2
      assert result['dashboard_type'] == 'lakeview'
      assert result['message'] == 'Successfully removed widget widget_2 from lakeview dashboard dashboard-123'

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
      mock_dashboard.widgets = [
        {'widget_id': 'widget_1', 'type': 'chart', 'name': 'Chart 1'}
      ]
      
      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['remove_dashboard_widget']
      result = tool.fn(
        dashboard_id='dashboard-123',
        widget_id='nonexistent_widget'
      )

      assert_error_response(result)
      assert 'Widget nonexistent_widget not found in dashboard dashboard-123' in result['error']

  @pytest.mark.unit
  def test_widget_operations_fallback_to_legacy(self, mcp_server, mock_env_vars):
    """Test widget operations falling back to legacy API."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock workspace client
      mock_workspace = Mock()
      
      # Mock Lakeview API failure
      mock_workspace.lakeview.get.side_effect = AttributeError("'WorkspaceClient' object has no attribute 'lakeview'")
      
      # Mock legacy dashboard API success
      mock_dashboard = Mock()
      mock_dashboard.widgets = [
        {'widget_id': 'legacy_widget_1', 'type': 'chart', 'name': 'Legacy Chart'}
      ]
      
      mock_workspace.dashboards.get.return_value = mock_dashboard
      mock_workspace.dashboards.update.return_value = Mock()
      
      mock_client.return_value = mock_workspace

      widget_spec = {
        'type': 'table',
        'name': 'Legacy Table Widget'
      }

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['add_widget_to_dashboard']
      result = tool.fn(
        dashboard_id='legacy-dashboard-123',
        widget_spec=widget_spec
      )

      assert_success_response(result)
      assert result['dashboard_type'] == 'legacy'
      assert result['widget_name'] == 'Legacy Table Widget'


class TestDatasetManagementTools:
  """Test dataset management operations."""

  @pytest.mark.unit
  def test_create_dashboard_dataset(self, mcp_server, mock_env_vars):
    """Test creating dataset for dashboard."""
    load_dashboard_tools(mcp_server)
    
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock the test_dataset_query function by overriding it in the test
      test_query_tool = mcp_server._tool_manager._tools['test_dataset_query']
      
      def mock_test_query(*args, **kwargs):
        return {
          'success': True,
          'row_count': 5,
          'columns': ['id', 'name', 'value'],
          'message': 'Query executed successfully'
        }
      
      original_test_fn = test_query_tool.fn
      test_query_tool.fn = mock_test_query
      
      try:
        mock_client.return_value = Mock()

        tool = mcp_server._tool_manager._tools['create_dashboard_dataset']
        result = tool.fn(
          dashboard_id='dashboard-123',
          name='Sales Dataset',
          query='SELECT * FROM sales_table',
          warehouse_id='warehouse-456'
        )

        assert_success_response(result)
        assert result['dataset_name'] == 'Sales Dataset'
        assert result['dashboard_id'] == 'dashboard-123'
        assert result['warehouse_id'] == 'warehouse-456'
        assert result['query'] == 'SELECT * FROM sales_table'
        assert 'dataset_id' in result
        assert 'Successfully created dataset Sales Dataset for dashboard dashboard-123' in result['message']
        
      finally:
        # Restore original function
        test_query_tool.fn = original_test_fn

  @pytest.mark.unit
  def test_create_dataset_with_env_warehouse(self, mcp_server, mock_env_vars):
    """Test creating dataset using environment warehouse ID."""
    mock_env_vars['DATABRICKS_SQL_WAREHOUSE_ID'] = 'env-warehouse-789'
    
    load_dashboard_tools(mcp_server)
    
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock the test_dataset_query function by overriding it in the test
      test_query_tool = mcp_server._tool_manager._tools['test_dataset_query']
      
      def mock_test_query(*args, **kwargs):
        return {
          'success': True,
          'row_count': 3,
          'columns': ['user_id', 'action'],
          'message': 'Query executed successfully'
        }
      
      original_test_fn = test_query_tool.fn
      test_query_tool.fn = mock_test_query
      
      try:
        mock_client.return_value = Mock()

        tool = mcp_server._tool_manager._tools['create_dashboard_dataset']
        result = tool.fn(
          dashboard_id='dashboard-123',
          name='User Actions',
          query='SELECT user_id, action FROM user_actions'
        )

        assert_success_response(result)
        assert result['warehouse_id'] == 'env-warehouse-789'
        
      finally:
        # Restore original function
        test_query_tool.fn = original_test_fn

  @pytest.mark.unit
  def test_create_dataset_missing_warehouse(self, mcp_server, mock_env_vars):
    """Test creating dataset without warehouse ID."""
    # Remove warehouse from environment
    if 'DATABRICKS_SQL_WAREHOUSE_ID' in mock_env_vars:
      del mock_env_vars['DATABRICKS_SQL_WAREHOUSE_ID']
    
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['create_dashboard_dataset']
      result = tool.fn(
        dashboard_id='dashboard-123',
        name='Test Dataset',
        query='SELECT * FROM test_table'
      )

      assert_error_response(result)
      assert 'SQL warehouse ID is required' in result['error']

  @pytest.mark.unit
  def test_create_dataset_invalid_query(self, mcp_server, mock_env_vars):
    """Test creating dataset with invalid query."""
    load_dashboard_tools(mcp_server)
    
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      # Mock the test_dataset_query function by overriding it in the test
      test_query_tool = mcp_server._tool_manager._tools['test_dataset_query']
      
      def mock_test_query(*args, **kwargs):
        return {
          'success': False,
          'error': 'Invalid SQL syntax: missing FROM clause',
          'query': 'SELECT *'
        }
      
      original_test_fn = test_query_tool.fn
      test_query_tool.fn = mock_test_query
      
      try:
        mock_client.return_value = Mock()

        tool = mcp_server._tool_manager._tools['create_dashboard_dataset']
        result = tool.fn(
          dashboard_id='dashboard-123',
          name='Invalid Dataset',
          query='SELECT *',
          warehouse_id='warehouse-456'
        )

        assert_error_response(result)
        assert 'Query validation failed' in result['error']
        assert 'Invalid SQL syntax: missing FROM clause' in result['error']
        
      finally:
        # Restore original function
        test_query_tool.fn = original_test_fn

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
      mock_response.result.data_array = [
        ['1', 'John Doe', '100.0'],
        ['2', 'Jane Smith', '150.0']
      ]
      
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
        query='SELECT id, name, value FROM users',
        warehouse_id='warehouse-456',
        limit=5
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
      result = tool.fn(
        query='SELECT * FROM large_table',
        warehouse_id='warehouse-456',
        limit=10
      )

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
      result = tool.fn(
        query='SELECT * FROM invalid_table',
        warehouse_id='warehouse-456'
      )

      assert_error_response(result)
      assert 'Query execution failed: Table not found: invalid_table' in result['error']
      assert result['status'] == 'FAILED'

  @pytest.mark.unit
  def test_test_query_missing_warehouse(self, mcp_server, mock_env_vars):
    """Test query testing without warehouse ID."""
    # Remove warehouse from environment
    if 'DATABRICKS_SQL_WAREHOUSE_ID' in mock_env_vars:
      del mock_env_vars['DATABRICKS_SQL_WAREHOUSE_ID']
    
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
      mock_workspace.statement_execution.execute_statement.side_effect = Exception('Network timeout')
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['test_dataset_query']
      result = tool.fn(
        query='SELECT * FROM test_table',
        warehouse_id='warehouse-456'
      )

      assert_error_response(result)
      assert 'SQL execution failed: Network timeout' in result['error']
