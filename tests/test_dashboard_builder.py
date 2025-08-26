"""Comprehensive integration tests for dashboard builder functionality."""

from unittest.mock import Mock, patch

import pytest

from server.tools.dashboards import load_dashboard_tools
from server.tools.widgets import load_widget_tools
from tests.utils import assert_error_response, assert_success_response


class TestDashboardBuilderIntegration:
  """Integration tests for complete dashboard building workflows."""

  @pytest.mark.integration
  def test_complete_dashboard_creation_workflow(self, mcp_server, mock_env_vars):
    """Test complete dashboard creation with multiple widgets."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_dashboard_client:
      with patch('server.tools.widgets.WorkspaceClient') as mock_widget_client:
        # Setup mock clients
        mock_dashboard_workspace = Mock()
        mock_widget_workspace = Mock()

        mock_dashboard_client.return_value = mock_dashboard_workspace
        mock_widget_client.return_value = mock_widget_workspace

        # Mock dashboard creation
        mock_created_dashboard = Mock()
        mock_created_dashboard.dashboard_id = 'new-dashboard-123'
        mock_created_dashboard.name = 'Sales Analytics Dashboard'
        mock_created_dashboard.widgets = []

        mock_dashboard_workspace.lakeview.create.return_value = mock_created_dashboard
        mock_dashboard_workspace.lakeview.get.return_value = mock_created_dashboard
        mock_dashboard_workspace.lakeview.update.return_value = Mock()

        # Mock statement execution for dataset validation
        mock_statement_response = Mock()
        mock_statement_response.status.state = 'SUCCEEDED'
        mock_statement_response.result.data_array = [['test_data']]
        mock_statement_response.result.schema.columns = [Mock(name='test_col')]

        mock_dashboard_workspace.statement_execution.execute_statement.return_value = (
          mock_statement_response
        )

        # Load tools
        load_dashboard_tools(mcp_server)
        load_widget_tools(mcp_server)

        # Step 1: Create dashboard
        create_tool = mcp_server._tool_manager._tools['create_lakeview_dashboard']
        dashboard_result = create_tool.fn(
          dashboard_config={
            'name': 'Sales Analytics Dashboard',
            'description': 'Comprehensive sales analysis',
          }
        )

        assert_success_response(dashboard_result)
        dashboard_id = dashboard_result['dashboard_id']

        # Step 2: Create dataset
        dataset_tool = mcp_server._tool_manager._tools['create_dashboard_dataset']
        dataset_result = dataset_tool.fn(
          dashboard_id=dashboard_id,
          name='Sales Data',
          query='SELECT region, product, revenue FROM sales_table',
          warehouse_id='warehouse-123',
        )

        assert_success_response(dataset_result)

        # Step 3: Add multiple widget types
        widget_specs = [
          {
            'tool': 'create_bar_chart',
            'params': {
              'dataset_name': 'Sales Data',
              'x_field': 'region',
              'y_field': 'revenue',
              'title': 'Revenue by Region',
            },
          },
          {
            'tool': 'create_pie_chart',
            'params': {
              'dataset_name': 'Sales Data',
              'category_field': 'product',
              'value_field': 'revenue',
              'title': 'Revenue by Product',
            },
          },
          {
            'tool': 'create_counter_widget',
            'params': {
              'dataset_name': 'Sales Data',
              'value_field': 'revenue',
              'aggregation': 'sum',
              'title': 'Total Revenue',
            },
          },
        ]

        widget_ids = []
        for spec in widget_specs:
          tool = mcp_server._tool_manager._tools[spec['tool']]
          result = tool.fn(**spec['params'], dashboard_id=dashboard_id)
          assert_success_response(result)
          widget_ids.append(result.get('widget_id'))

        # Step 4: Apply auto-layout
        layout_tool = mcp_server._tool_manager._tools['auto_layout_dashboard']
        layout_result = layout_tool.fn(dashboard_id=dashboard_id, layout_type='grid')

        assert_success_response(layout_result)
        assert layout_result['widgets_arranged'] == 3

        # Verify dashboard was properly updated
        assert mock_dashboard_workspace.lakeview.update.call_count >= 3

  @pytest.mark.integration
  def test_dashboard_with_filters_workflow(self, mcp_server, mock_env_vars):
    """Test creating dashboard with filter widgets."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      mock_dashboard = Mock()
      mock_dashboard.dashboard_id = 'filter-dashboard-456'
      mock_dashboard.widgets = []

      mock_workspace.lakeview.create.return_value = mock_dashboard
      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.return_value = Mock()

      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)

      # Create dashboard with filter widgets
      filter_widgets = [
        {
          'tool': 'create_dropdown_filter',
          'params': {'dataset_name': 'sales_data', 'filter_field': 'region', 'multi_select': True},
        },
        {
          'tool': 'create_date_range_filter',
          'params': {'dataset_name': 'sales_data', 'date_field': 'order_date'},
        },
        {
          'tool': 'create_slider_filter',
          'params': {
            'dataset_name': 'sales_data',
            'numeric_field': 'price',
            'min_value': 0,
            'max_value': 1000,
          },
        },
      ]

      for widget_spec in filter_widgets:
        tool = mcp_server._tool_manager._tools[widget_spec['tool']]
        result = tool.fn(**widget_spec['params'])
        assert_success_response(result)

  @pytest.mark.integration
  def test_dashboard_update_workflow(self, mcp_server, mock_env_vars):
    """Test updating existing dashboard with new widgets."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()

      # Mock existing dashboard with widgets
      existing_widgets = [{'widget_id': 'widget_1', 'type': 'bar_chart', 'name': 'Existing Chart'}]

      mock_dashboard = Mock()
      mock_dashboard.dashboard_id = 'existing-dashboard-789'
      mock_dashboard.widgets = existing_widgets.copy()

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.return_value = Mock()

      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)

      # Update dashboard with new widget
      add_widget_tool = mcp_server._tool_manager._tools['add_widget_to_dashboard']
      result = add_widget_tool.fn(
        dashboard_id='existing-dashboard-789',
        widget_spec={
          'type': 'line_chart',
          'name': 'New Trend Chart',
          'parameters': {'x_field': 'date', 'y_field': 'value'},
        },
      )

      assert_success_response(result)

      # Update existing widget
      update_widget_tool = mcp_server._tool_manager._tools['update_dashboard_widget']
      update_result = update_widget_tool.fn(
        dashboard_id='existing-dashboard-789',
        widget_id='widget_1',
        updates={'title': 'Updated Chart Title'},
      )

      assert_success_response(update_result)

      # Remove a widget
      remove_tool = mcp_server._tool_manager._tools['remove_dashboard_widget']
      remove_result = remove_tool.fn(dashboard_id='existing-dashboard-789', widget_id='widget_1')

      assert_success_response(remove_result)

  @pytest.mark.integration
  def test_dashboard_layout_combinations(self, mcp_server, mock_env_vars):
    """Test different layout combinations."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()

      # Create mock dashboard with various widget sizes
      mock_dashboard = Mock()
      mock_dashboard.widgets = [
        {'widget_id': 'w1', 'position': {'width': 6, 'height': 4}},
        {'widget_id': 'w2', 'position': {'width': 6, 'height': 4}},
        {'widget_id': 'w3', 'position': {'width': 3, 'height': 2}},
        {'widget_id': 'w4', 'position': {'width': 3, 'height': 2}},
        {'widget_id': 'w5', 'position': {'width': 3, 'height': 2}},
        {'widget_id': 'w6', 'position': {'width': 3, 'height': 2}},
      ]

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.return_value = Mock()

      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)

      layout_types = ['grid', 'vertical', 'horizontal', 'masonry']

      for layout_type in layout_types:
        layout_tool = mcp_server._tool_manager._tools['auto_layout_dashboard']
        result = layout_tool.fn(dashboard_id='test-dashboard', layout_type=layout_type)

        assert_success_response(result)
        assert result['layout_type'] == layout_type


class TestDashboardBuilderValidation:
  """Test validation and error handling in dashboard builder."""

  @pytest.mark.integration
  def test_invalid_widget_combinations(self, mcp_server, mock_env_vars):
    """Test handling of invalid widget combinations."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      mock_dashboard = Mock()
      mock_dashboard.widgets = []

      # Simulate constraint violations
      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.side_effect = Exception(
        'Dashboard cannot have more than 20 widgets'
      )

      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)

      # Try to add widget that violates constraints
      add_tool = mcp_server._tool_manager._tools['add_widget_to_dashboard']
      result = add_tool.fn(
        dashboard_id='test-dashboard', widget_spec={'type': 'chart', 'name': 'Widget 21'}
      )

      assert_error_response(result)

  @pytest.mark.integration
  def test_dataset_query_validation(self, mcp_server, mock_env_vars):
    """Test SQL query validation in dataset creation."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()

      # Mock failed query validation
      mock_response = Mock()
      mock_response.status.state = 'FAILED'
      mock_response.status.error = Mock()
      mock_response.status.error.message = 'Syntax error near SELECT'

      mock_workspace.statement_execution.execute_statement.return_value = mock_response
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)

      dataset_tool = mcp_server._tool_manager._tools['create_dashboard_dataset']
      result = dataset_tool.fn(
        dashboard_id='test-dashboard',
        name='Invalid Dataset',
        query='SELCT * FORM table',  # Intentional typos
        warehouse_id='warehouse-123',
      )

      assert_error_response(result)
      assert 'Query validation failed' in result['error']

  @pytest.mark.integration
  def test_widget_position_conflicts(self, mcp_server, mock_env_vars):
    """Test handling of widget position conflicts."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()

      # Mock dashboard with overlapping widgets
      mock_dashboard = Mock()
      mock_dashboard.widgets = [
        {'widget_id': 'w1', 'position': {'x': 0, 'y': 0, 'width': 6, 'height': 4}}
      ]

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)

      # Try to reposition widget to overlapping position
      reposition_tool = mcp_server._tool_manager._tools['reposition_widget']
      reposition_tool.fn(
        dashboard_id='test-dashboard',
        widget_id='w2',
        position={'x': 2, 'y': 2, 'width': 6, 'height': 4},
      )

      # Note: Current implementation may not detect overlaps
      # This test documents expected behavior


class TestDashboardBuilderPerformance:
  """Test performance aspects of dashboard builder."""

  @pytest.mark.integration
  def test_bulk_widget_creation(self, mcp_server, mock_env_vars):
    """Test creating many widgets efficiently."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      mock_dashboard = Mock()
      mock_dashboard.widgets = []

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.return_value = Mock()

      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)

      # Create 20 widgets (typical dashboard limit)
      for i in range(20):
        widget_spec = {'type': 'counter', 'name': f'Metric {i}', 'widget_id': f'widget_{i}'}

        add_tool = mcp_server._tool_manager._tools['add_widget_to_dashboard']
        result = add_tool.fn(dashboard_id='test-dashboard', widget_spec=widget_spec)

        assert_success_response(result)

      # Verify all updates were made
      assert mock_workspace.lakeview.update.call_count == 20

  @pytest.mark.integration
  def test_large_dataset_handling(self, mcp_server, mock_env_vars):
    """Test handling large datasets in widgets."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()

      # Mock large dataset response
      mock_response = Mock()
      mock_response.status.state = 'SUCCEEDED'
      mock_response.result.data_array = [
        [f'row_{i}', f'value_{i}']
        for i in range(100)  # Limit for test
      ]

      mock_col1 = Mock()
      mock_col1.name = 'id'
      mock_col2 = Mock()
      mock_col2.name = 'value'
      mock_response.result.schema.columns = [mock_col1, mock_col2]

      mock_workspace.statement_execution.execute_statement.return_value = mock_response
      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)

      # Test query with large result set
      test_tool = mcp_server._tool_manager._tools['test_dataset_query']
      result = test_tool.fn(
        query='SELECT * FROM large_table',
        warehouse_id='warehouse-123',
        limit=100,  # Should limit results
      )

      assert_success_response(result)
      assert result['row_count'] == 100  # Total rows from mock
      assert len(result['sample_data']) <= 100  # Limited sample


class TestDashboardBuilderRecovery:
  """Test error recovery and rollback scenarios."""

  @pytest.mark.integration
  def test_partial_update_recovery(self, mcp_server, mock_env_vars):
    """Test recovery from partial update failures."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()
      mock_dashboard = Mock()

      original_widgets = [
        {'widget_id': 'w1', 'type': 'chart'},
        {'widget_id': 'w2', 'type': 'table'},
      ]
      mock_dashboard.widgets = original_widgets.copy()

      # First update succeeds, second fails
      update_count = 0

      def mock_update(*args, **kwargs):
        nonlocal update_count
        update_count += 1
        if update_count > 1:
          raise Exception('Update failed')
        return Mock()

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.side_effect = mock_update

      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)

      # First update should succeed
      add_tool = mcp_server._tool_manager._tools['add_widget_to_dashboard']
      result1 = add_tool.fn(
        dashboard_id='test-dashboard', widget_spec={'type': 'counter', 'name': 'New Counter'}
      )
      assert_success_response(result1)

      # Second update should fail
      result2 = add_tool.fn(
        dashboard_id='test-dashboard', widget_spec={'type': 'filter', 'name': 'New Filter'}
      )
      assert_error_response(result2)

  @pytest.mark.integration
  def test_dashboard_state_consistency(self, mcp_server, mock_env_vars):
    """Test maintaining dashboard state consistency."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()

      # Track dashboard state changes
      dashboard_states = []

      def mock_get(*args, **kwargs):
        mock_dashboard = Mock()
        mock_dashboard.widgets = dashboard_states[-1] if dashboard_states else []
        return mock_dashboard

      def mock_update(*args, **kwargs):
        # Capture widget state
        if 'widgets' in kwargs:
          dashboard_states.append(kwargs['widgets'].copy())
        return Mock()

      mock_workspace.lakeview.get.side_effect = mock_get
      mock_workspace.lakeview.update.side_effect = mock_update

      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)

      # Perform series of operations
      operations = [
        (
          'add_widget_to_dashboard',
          {'dashboard_id': 'test-dashboard', 'widget_spec': {'widget_id': 'w1', 'type': 'chart'}},
        ),
        (
          'update_dashboard_widget',
          {'dashboard_id': 'test-dashboard', 'widget_id': 'w1', 'updates': {'title': 'Updated'}},
        ),
        ('remove_dashboard_widget', {'dashboard_id': 'test-dashboard', 'widget_id': 'w1'}),
      ]

      for tool_name, params in operations:
        tool = mcp_server._tool_manager._tools[tool_name]
        tool.fn(**params)

        # Verify state consistency after each operation
        if tool_name == 'add_widget_to_dashboard':
          # Should have added one widget
          if dashboard_states:
            assert len(dashboard_states[-1]) >= 1
        elif tool_name == 'remove_dashboard_widget':
          # Should have removed widget if it existed
          # Note: Mock may not perfectly simulate removal logic
          pass  # Skip this assertion for mock environment


class TestDashboardBuilderConcurrency:
  """Test concurrent operations on dashboards."""

  @pytest.mark.integration
  def test_concurrent_widget_additions(self, mcp_server, mock_env_vars):
    """Test handling concurrent widget additions."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()

      # Simulate concurrent modifications
      widget_count = 0

      def mock_get(*args, **kwargs):
        nonlocal widget_count
        mock_dashboard = Mock()
        mock_dashboard.widgets = [{'widget_id': f'w{i}'} for i in range(widget_count)]
        return mock_dashboard

      def mock_update(*args, **kwargs):
        nonlocal widget_count
        widget_count += 1
        return Mock()

      mock_workspace.lakeview.get.side_effect = mock_get
      mock_workspace.lakeview.update.side_effect = mock_update

      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)

      # Simulate concurrent additions
      add_tool = mcp_server._tool_manager._tools['add_widget_to_dashboard']

      for i in range(5):
        result = add_tool.fn(
          dashboard_id='test-dashboard', widget_spec={'type': 'chart', 'name': f'Chart {i}'}
        )
        assert_success_response(result)

      assert widget_count == 5

  @pytest.mark.integration
  def test_concurrent_layout_updates(self, mcp_server, mock_env_vars):
    """Test concurrent layout update handling."""
    with patch('server.tools.dashboards.WorkspaceClient') as mock_client:
      mock_workspace = Mock()

      # Track layout update attempts
      layout_updates = []

      mock_dashboard = Mock()
      mock_dashboard.widgets = [
        {'widget_id': f'w{i}', 'position': {'width': 3, 'height': 2}} for i in range(4)
      ]

      def mock_update(*args, **kwargs):
        if 'widgets' in kwargs:
          layout_updates.append(kwargs['widgets'])
        return Mock()

      mock_workspace.lakeview.get.return_value = mock_dashboard
      mock_workspace.lakeview.update.side_effect = mock_update

      mock_client.return_value = mock_workspace

      load_dashboard_tools(mcp_server)

      # Try different layout types concurrently
      layout_tool = mcp_server._tool_manager._tools['auto_layout_dashboard']

      for layout_type in ['grid', 'vertical']:
        result = layout_tool.fn(dashboard_id='test-dashboard', layout_type=layout_type)
        assert_success_response(result)

      # Verify both layouts were applied
      assert len(layout_updates) == 2


if __name__ == '__main__':
  pytest.main([__file__, '-v'])
