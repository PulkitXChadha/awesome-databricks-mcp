"""Test SQL operations tools."""

from unittest.mock import Mock, patch

import pytest

from server.tools.sql_operations import load_sql_tools
from tests.utils import assert_error_response, assert_success_response, load_mock_response


class TestSQLOperations:
  """Test SQL warehouse and query operations."""

  @pytest.mark.unit
  def test_list_warehouses(self, mcp_server, mock_env_vars):
    """Test listing SQL warehouses."""
    with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
      # Setup mock warehouses
      warehouse_data = load_mock_response('warehouses')
      warehouses = []
      for w in warehouse_data:
        mock_w = Mock()
        for key, value in w.items():
          setattr(mock_w, key, value)
        warehouses.append(mock_w)

      mock_client.return_value.sql_warehouses.list.return_value = warehouses

      load_sql_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_warehouses']
      result = tool.fn()

      assert_success_response(result)
      assert len(result['warehouses']) == 1
      assert result['warehouses'][0]['name'] == 'Test Warehouse'

  @pytest.mark.unit
  def test_execute_dbsql(self, mcp_server, mock_env_vars):
    """Test executing SQL query."""
    with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
      # Mock statement execution
      mock_response = Mock()
      mock_response.statement_id = 'stmt-123'
      mock_response.status.state = 'SUCCEEDED'
      mock_response.result = Mock()
      mock_response.result.data_array = [['1', 'Alice'], ['2', 'Bob']]
      mock_response.manifest.schema.columns = [
        Mock(name='id', type_text='LONG'),
        Mock(name='name', type_text='STRING'),
      ]

      mock_client.return_value.statement_execution.execute_statement.return_value = mock_response

      load_sql_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['execute_dbsql']
      result = tool.fn(query='SELECT * FROM users', warehouse_id='test-warehouse')

      assert_success_response(result)
      assert result['row_count'] == 2
      assert 'data' in result
      assert 'columns' in result['data']
      assert 'rows' in result['data']

  @pytest.mark.unit
  def test_list_warehouses_empty(self, mcp_server, mock_env_vars):
    """Test listing warehouses when none exist."""
    with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
      mock_client.return_value.sql_warehouses.list.return_value = []

      load_sql_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_warehouses']
      result = tool.fn()

      assert_success_response(result)
      assert result['count'] == 0
      assert result['warehouses'] == []

  @pytest.mark.unit
  def test_execute_dbsql_error(self, mcp_server, mock_env_vars):
    """Test SQL execution with error."""
    with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
      # Mock error response
      mock_response = Mock()
      mock_response.status.state = 'FAILED'
      mock_response.status.error = Mock(message='SQL syntax error')

      mock_client.return_value.statement_execution.execute_statement.return_value = mock_response

      load_sql_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['execute_dbsql']
      result = tool.fn(query='INVALID SQL', warehouse_id='test-warehouse')

      assert result['success'] is False
      assert 'error' in result

  @pytest.mark.unit
  def test_get_sql_warehouse(self, mcp_server, mock_env_vars):
    """Test getting warehouse status."""
    with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
      # Mock warehouse status
      mock_warehouse = Mock()
      mock_warehouse.id = 'test-warehouse'
      mock_warehouse.state = 'RUNNING'
      mock_warehouse.name = 'Test Warehouse'
      mock_warehouse.size = 'Small'
      mock_warehouse.auto_stop_mins = 60

      mock_client.return_value.sql_warehouses.get.return_value = mock_warehouse

      load_sql_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['get_sql_warehouse']
      result = tool.fn(warehouse_id='test-warehouse')

      assert_success_response(result)
      assert result['warehouse']['id'] == 'test-warehouse'
      assert result['warehouse']['state'] == 'RUNNING'

  @pytest.mark.unit
  def test_start_sql_warehouse(self, mcp_server, mock_env_vars):
    """Test starting a warehouse."""
    with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
      mock_client.return_value.sql_warehouses.start.return_value = None

      load_sql_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['start_sql_warehouse']
      result = tool.fn(warehouse_id='test-warehouse')

      assert_success_response(result)
      assert result['warehouse_id'] == 'test-warehouse'
      assert result['message'] == 'Warehouse test-warehouse started successfully'

  @pytest.mark.unit
  def test_stop_sql_warehouse(self, mcp_server, mock_env_vars):
    """Test stopping a warehouse."""
    with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
      mock_client.return_value.sql_warehouses.stop.return_value = None

      load_sql_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['stop_sql_warehouse']
      result = tool.fn(warehouse_id='test-warehouse')

      assert_success_response(result)
      assert result['warehouse_id'] == 'test-warehouse'
      assert result['message'] == 'Warehouse test-warehouse stopped successfully'

  @pytest.mark.unit
  def test_sql_authentication_failure(self, mcp_server, mock_env_vars):
    """Test expired token handling."""
    with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
      # Mock authentication failure
      from databricks.sdk.errors import PermissionDenied

      mock_client.side_effect = PermissionDenied('Invalid authentication credentials')

      load_sql_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_warehouses']
      result = tool.fn()

      assert result['success'] is False
      assert 'authentication' in result['error'].lower() or 'permission' in result['error'].lower()

  @pytest.mark.unit
  def test_sql_network_timeout(self, mcp_server, mock_env_vars):
    """Test network timeout resilience."""
    with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
      # Mock network timeout
      import requests

      mock_client.return_value.sql_warehouses.list.side_effect = requests.exceptions.Timeout(
        'Request timed out'
      )

      load_sql_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_warehouses']
      result = tool.fn()

      assert result['success'] is False
      assert (
        'timeout' in result['error'].lower()
        or 'network' in result['error'].lower()
        or 'timed out' in result['error'].lower()
      )

  @pytest.mark.unit
  def test_sql_rate_limiting(self, mcp_server, mock_env_vars):
    """Test API throttling response."""
    with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
      # Mock rate limiting error
      from databricks.sdk.errors import TooManyRequests

      mock_client.return_value.sql_warehouses.list.side_effect = TooManyRequests(
        'Rate limit exceeded'
      )

      load_sql_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_warehouses']
      result = tool.fn()

      assert result['success'] is False
      assert 'rate limit' in result['error'].lower() or 'throttl' in result['error'].lower()

  @pytest.mark.unit
  def test_sql_warehouse_operations(self, mcp_server, mock_env_vars):
    """Test SQL warehouse listing and management."""
    with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
      from tests.mock_factory import mock_warehouse_list

      # Setup mock warehouses using simplified factory
      warehouse_data = mock_warehouse_list()
      warehouses = []
      for w in warehouse_data:
        mock_w = Mock()
        for key, value in w.items():
          setattr(mock_w, key, value)
        warehouses.append(mock_w)

      mock_client.return_value.sql_warehouses.list.return_value = warehouses

      load_sql_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_warehouses']
      result = tool.fn()

      assert_success_response(result)
      assert len(result['warehouses']) >= 0

      # Verify performance threshold (< 2s mocked - should be instant)
      import time

      start_time = time.time()
      result = tool.fn()
      end_time = time.time()
      assert (end_time - start_time) < 2.0


class TestSQLOperationsErrorScenarios:
  """Test SQL operations error handling across different failure scenarios."""

  @pytest.mark.unit
  def test_comprehensive_network_failures(self, mcp_server, mock_env_vars):
    """Test comprehensive network failure handling."""
    from tests.utils import ERROR_SCENARIOS, simulate_databricks_error

    # Test connection timeout on SQL execution
    with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
      mock_client.side_effect = simulate_databricks_error(
        next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Network timeout'), 'Network timeout'
      )

      load_sql_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['execute_dbsql']
      result = tool.fn(query='SELECT * FROM test_table', warehouse_id='test-warehouse')

      assert_error_response(result)
      assert 'timeout' in result['error'].lower() or 'network' in result['error'].lower()

  @pytest.mark.unit
  def test_warehouse_authentication_errors(self, mcp_server, mock_env_vars):
    """Test warehouse access authentication errors."""
    from tests.utils import ERROR_SCENARIOS, simulate_databricks_error

    # Test warehouse access denied
    with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
      mock_client.return_value.sql_warehouses.get.side_effect = simulate_databricks_error(
        next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Permission denied'),
        'Permission denied',
      )

      load_sql_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['get_sql_warehouse']
      result = tool.fn(warehouse_id='restricted-warehouse')

      assert_error_response(result)
      assert 'access denied' in result['error'].lower() or 'permission' in result['error'].lower()

  @pytest.mark.unit
  def test_sql_execution_rate_limiting(self, mcp_server, mock_env_vars):
    """Test SQL execution rate limiting scenarios."""
    from tests.utils import ERROR_SCENARIOS, simulate_databricks_error

    # Test query execution rate limiting
    with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
      mock_client.return_value.statement_execution.execute_statement.side_effect = (
        simulate_databricks_error(
          next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Rate limiting'), 'Rate limiting'
        )
      )

      load_sql_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['execute_dbsql']
      result = tool.fn(query='SELECT COUNT(*) FROM large_table', warehouse_id='busy-warehouse')

      assert_error_response(result)
      assert (
        'rate limit' in result['error'].lower() or 'too many requests' in result['error'].lower()
      )

  @pytest.mark.unit
  def test_sql_malformed_queries(self, mcp_server, mock_env_vars):
    """Test malformed SQL query handling."""
    load_sql_tools(mcp_server)

    # Test SQL syntax errors via mock response
    with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
      # Mock SQL execution failure
      error_response = Mock()
      error_response.status.state = 'FAILED'
      error_response.status.error = Mock(message='SQL syntax error: Invalid query syntax')

      mock_client.return_value.statement_execution.execute_statement.return_value = error_response

      sql_tool = mcp_server._tool_manager._tools['execute_dbsql']

      malformed_queries = [
        'SELCT * FROM table',  # Typo in SELECT
        'SELECT * FROM',  # Incomplete query
        'SELECT * FROM table WHERE',  # Incomplete WHERE
        '',  # Empty query
        'DROP TABLE production_data',  # Potentially dangerous query
      ]

      for bad_query in malformed_queries:
        result = sql_tool.fn(query=bad_query, warehouse_id='test-warehouse')
        assert_error_response(result)
        # SQL errors come through the status.error mechanism
        assert 'error' in result

  @pytest.mark.unit
  def test_warehouse_not_found_scenarios(self, mcp_server, mock_env_vars):
    """Test warehouse not found error scenarios."""
    from tests.utils import ERROR_SCENARIOS, simulate_databricks_error

    load_sql_tools(mcp_server)

    # Test nonexistent warehouse operations
    warehouse_operations = [
      ('get_sql_warehouse', {'warehouse_id': 'nonexistent-warehouse'}),
      ('start_sql_warehouse', {'warehouse_id': 'nonexistent-warehouse'}),
      ('stop_sql_warehouse', {'warehouse_id': 'nonexistent-warehouse'}),
      ('delete_sql_warehouse', {'warehouse_id': 'nonexistent-warehouse'}),
    ]

    for tool_name, params in warehouse_operations:
      with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
        # Mock all warehouse methods that could be called
        error_exception = simulate_databricks_error(
          next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Resource not found'),
          'Resource not found',
        )
        mock_client.return_value.sql_warehouses.get.side_effect = error_exception
        mock_client.return_value.sql_warehouses.start.side_effect = error_exception
        mock_client.return_value.sql_warehouses.stop.side_effect = error_exception
        mock_client.return_value.sql_warehouses.delete.side_effect = error_exception

        tool = mcp_server._tool_manager._tools[tool_name]
        result = tool.fn(**params)

        assert_error_response(result)
        assert 'not found' in result['error'].lower() or 'resource' in result['error'].lower()
