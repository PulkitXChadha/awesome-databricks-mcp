"""Consolidated tests for all MCP tools following CLAUDE.md simplicity guidelines."""

from unittest.mock import Mock, patch

import pytest

from server.tools import load_tools
from server.tools.core import load_core_tools
from server.tools.jobs_pipelines import load_job_tools
from server.tools.lakeview_dashboard import load_dashboard_tools
from server.tools.sql_operations import load_sql_tools
from server.tools.unity_catalog import load_uc_tools


class TestCoreTools:
  """Test core MCP tools."""

  @pytest.mark.unit
  def test_health_check(self, mcp_server, mock_env_vars):
    """Test health check tool."""
    load_core_tools(mcp_server)

    tool = mcp_server._tool_manager._tools['health']
    result = tool.fn()

    assert result == {
      'status': 'healthy',
      'service': 'databricks-mcp',
      'databricks_configured': True,
    }


class TestUnityCatalogTools:
  """Test Unity Catalog tools."""


class TestSQLTools:
  """Test SQL operation tools."""

  @pytest.mark.unit
  def test_list_warehouses_success(self, mcp_server, mock_env_vars):
    """Test listing SQL warehouses successfully."""
    with patch('server.tools.sql_operations.WorkspaceClient') as mock_client_class:
      mock_client = Mock()
      mock_warehouse = Mock()
      mock_warehouse.id = 'test-warehouse'
      mock_warehouse.name = 'Test Warehouse'
      mock_warehouse.state = 'RUNNING'
      mock_warehouse.cluster_size = 'Medium'
      mock_warehouse.auto_stop_mins = 10
      mock_client.warehouses.list.return_value = [mock_warehouse]
      mock_client_class.return_value = mock_client

      load_sql_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_warehouses']
      result = tool.fn()

      assert result['success'] is True
      assert result['count'] == 1
      assert len(result['warehouses']) == 1
      assert result['warehouses'][0]['id'] == 'test-warehouse'

  @pytest.mark.unit
  def test_execute_sql_success(self, mcp_server, mock_env_vars):
    """Test SQL execution successfully."""
    with patch('server.tools.sql_operations.WorkspaceClient') as mock_client_class:
      mock_client = Mock()
      mock_result = Mock()
      mock_result.result = Mock()
      mock_result.result.data_array = [['2024-01', '1000']]
      mock_result.manifest = Mock()
      mock_result.manifest.schema = Mock()
      mock_col = Mock()
      mock_col.name = 'date'
      mock_result.manifest.schema.columns = [mock_col]
      mock_client.statement_execution.execute_statement.return_value = mock_result
      mock_client_class.return_value = mock_client

      load_sql_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['execute_dbsql']
      result = tool.fn(query='SELECT * FROM test', warehouse_id='test-warehouse')

      assert result['success'] is True
      assert 'data' in result
      assert result['row_count'] == 1


class TestJobsTools:
  """Test jobs and pipelines tools."""

  @pytest.mark.unit
  def test_list_jobs_success(self, mcp_server, mock_env_vars):
    """Test listing jobs successfully."""
    with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client_class:
      mock_client = Mock()
      mock_job = Mock()
      mock_job.job_id = 123
      mock_job.settings = Mock()
      mock_job.settings.name = 'Test Job'
      mock_job.created_time = 1234567890
      mock_job.creator_user_name = 'test@example.com'
      mock_client.jobs.list.return_value = [mock_job]
      mock_client_class.return_value = mock_client

      load_job_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_jobs']
      result = tool.fn()

      assert result['success'] is True
      assert result['count'] == 1
      assert len(result['jobs']) == 1
      assert result['jobs'][0]['job_id'] == 123

  @pytest.mark.unit
  def test_list_pipelines_success(self, mcp_server, mock_env_vars):
    """Test listing pipelines successfully."""
    with patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_client_class:
      mock_client = Mock()
      mock_pipeline = Mock()
      mock_pipeline.pipeline_id = 'pipeline-123'
      mock_pipeline.name = 'Test Pipeline'
      mock_pipeline.state = 'IDLE'
      mock_pipeline.creator_user_name = 'test@example.com'
      mock_pipeline.created_time = 1234567890
      mock_client.pipelines.list_pipelines.return_value = [mock_pipeline]
      mock_client_class.return_value = mock_client

      load_job_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_pipelines']
      result = tool.fn()

      assert result['success'] is True
      assert result['count'] == 1
      assert len(result['pipelines']) == 1
      assert result['pipelines'][0]['pipeline_id'] == 'pipeline-123'


class TestDashboardTools:
  """Test dashboard tools."""

  @pytest.mark.unit
  def test_create_dashboard_file(self, mcp_server, mock_env_vars):
    """Test creating a dashboard file."""
    load_dashboard_tools(mcp_server)
    tool = mcp_server._tool_manager._tools['create_dashboard_file']

    result = tool.fn(
      name='Test Dashboard',
      warehouse_id='test-warehouse',
      datasets=[{'name': 'Sales Data', 'query': 'SELECT product, revenue FROM sales'}],
      widgets=[{'type': 'counter', 'dataset': 'Sales Data', 'config': {'value_field': 'revenue'}}],
      file_path='/tmp/test_dashboard.lvdash.json',
      validate_sql=False,
    )

    assert result['success'] is True
    assert 'file_path' in result


class TestToolIntegration:
  """Test tool loading and integration."""

  @pytest.mark.integration
  def test_all_tools_load(self, mcp_server, mock_env_vars):
    """Test that all tools load without errors."""
    load_tools(mcp_server)

    tools = mcp_server._tool_manager._tools
    assert len(tools) > 0

    # Check key tools are present
    expected_tools = [
      'health',
      'describe_uc_catalog',
      'list_warehouses',
      'list_jobs',
      'create_dashboard_file',
    ]

    for tool_name in expected_tools:
      assert tool_name in tools, f'Tool {tool_name} not loaded'

  @pytest.mark.integration
  def test_tool_error_handling(self, mcp_server, mock_env_vars):
    """Test that tools handle errors gracefully."""
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client_class:
      mock_client = Mock()
      mock_client.catalogs.get.side_effect = Exception('Test error')
      mock_client_class.return_value = mock_client

      load_uc_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['describe_uc_catalog']
      result = tool.fn('test_catalog')

      assert result['success'] is False
      assert 'error' in result
