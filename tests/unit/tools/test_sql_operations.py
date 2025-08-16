"""Unit tests for SQL operations MCP tools."""

import os
from unittest.mock import Mock, patch

import pytest
from databricks.sdk.errors import BadRequest, NotFound


@pytest.mark.unit
@pytest.mark.tools
class TestSQLOperationsTools:
  """Test SQL operations MCP tools functionality."""

  def test_load_sql_tools_registers_all_tools(self, mcp_server):
    """Test that load_sql_tools registers all expected tools."""
    from server.tools.sql_operations import load_sql_tools

    load_sql_tools(mcp_server)

    expected_tools = [
      'execute_dbsql',
      'list_warehouses',
      'get_sql_warehouse',
      'create_sql_warehouse',
      'start_sql_warehouse',
      'stop_sql_warehouse',
      'delete_sql_warehouse',
    ]

    tool_names = list(mcp_server.tools.keys())
    for tool_name in expected_tools:
      assert tool_name in tool_names


@pytest.mark.unit
@pytest.mark.tools
class TestExecuteDBSQL:
  """Test execute_dbsql tool."""

  def test_execute_dbsql_success_with_results(self, mcp_server, mock_databricks_client):
    """Test successful SQL execution with results."""
    from server.tools.sql_operations import load_sql_tools

    load_sql_tools(mcp_server)

    # Mock successful query execution
    mock_result = Mock()
    mock_result.result = Mock()
    mock_result.result.data_array = [['1', 'John'], ['2', 'Jane']]
    mock_result.manifest = Mock()
    mock_result.manifest.schema = Mock()
    mock_result.manifest.schema.columns = [Mock(name='id'), Mock(name='name')]

    mock_databricks_client.statement_execution.execute_statement.return_value = mock_result

    tool = mcp_server.tools['execute_dbsql'].fn

    with patch('server.tools.sql_operations.WorkspaceClient', return_value=mock_databricks_client):
      with patch.dict(os.environ, {'DATABRICKS_SQL_WAREHOUSE_ID': 'test-warehouse'}):
        result = tool('SELECT * FROM test_table')

    assert result['success'] is True
    assert result['row_count'] == 2
    assert 'data' in result
    assert result['data']['columns'] == ['id', 'name']
    assert len(result['data']['rows']) == 2
    assert result['data']['rows'][0] == {'id': '1', 'name': 'John'}

  def test_execute_dbsql_success_no_results(self, mcp_server, mock_databricks_client):
    """Test successful SQL execution with no results."""
    from server.tools.sql_operations import load_sql_tools

    load_sql_tools(mcp_server)

    # Mock query execution with no results
    mock_result = Mock()
    mock_result.result = None

    mock_databricks_client.statement_execution.execute_statement.return_value = mock_result

    tool = mcp_server.tools['execute_dbsql'].fn

    with patch('server.tools.sql_operations.WorkspaceClient', return_value=mock_databricks_client):
      with patch.dict(os.environ, {'DATABRICKS_SQL_WAREHOUSE_ID': 'test-warehouse'}):
        result = tool('CREATE TABLE test (id INT)')

    assert result['success'] is True
    assert result['row_count'] == 0
    assert 'Query executed successfully with no results' in result['data']['message']

  def test_execute_dbsql_with_catalog_schema(self, mcp_server, mock_databricks_client):
    """Test SQL execution with catalog and schema specification."""
    from server.tools.sql_operations import load_sql_tools

    load_sql_tools(mcp_server)

    mock_result = Mock()
    mock_result.result = None

    mock_databricks_client.statement_execution.execute_statement.return_value = mock_result

    tool = mcp_server.tools['execute_dbsql'].fn

    with patch('server.tools.sql_operations.WorkspaceClient', return_value=mock_databricks_client):
      with patch.dict(os.environ, {'DATABRICKS_SQL_WAREHOUSE_ID': 'test-warehouse'}):
        tool('SELECT 1', catalog='test_catalog', schema='test_schema')

    # Verify the full query was constructed correctly
    call_args = mock_databricks_client.statement_execution.execute_statement.call_args
    executed_statement = call_args[1]['statement']
    assert 'USE CATALOG test_catalog' in executed_statement
    assert 'USE SCHEMA test_schema' in executed_statement
    assert 'SELECT 1' in executed_statement

  def test_execute_dbsql_with_limit(self, mcp_server, mock_databricks_client):
    """Test SQL execution with row limit."""
    from server.tools.sql_operations import load_sql_tools

    load_sql_tools(mcp_server)

    # Mock query with more results than limit
    mock_result = Mock()
    mock_result.result = Mock()
    mock_result.result.data_array = [['1'], ['2'], ['3'], ['4'], ['5']]
    mock_result.manifest = Mock()
    mock_result.manifest.schema = Mock()
    mock_result.manifest.schema.columns = [Mock(name='id')]

    mock_databricks_client.statement_execution.execute_statement.return_value = mock_result

    tool = mcp_server.tools['execute_dbsql'].fn

    with patch('server.tools.sql_operations.WorkspaceClient', return_value=mock_databricks_client):
      with patch.dict(os.environ, {'DATABRICKS_SQL_WAREHOUSE_ID': 'test-warehouse'}):
        result = tool('SELECT * FROM test_table', limit=3)

    assert result['success'] is True
    assert result['row_count'] == 3
    assert len(result['data']['rows']) == 3

  def test_execute_dbsql_no_warehouse_id(self, mcp_server, mock_databricks_client):
    """Test SQL execution without warehouse ID."""
    from server.tools.sql_operations import load_sql_tools

    load_sql_tools(mcp_server)

    tool = mcp_server.tools['execute_dbsql'].fn

    with patch('server.tools.sql_operations.WorkspaceClient', return_value=mock_databricks_client):
      with patch.dict(os.environ, {}, clear=False):
        # Ensure no warehouse ID is set
        if 'DATABRICKS_SQL_WAREHOUSE_ID' in os.environ:
          del os.environ['DATABRICKS_SQL_WAREHOUSE_ID']

        result = tool('SELECT 1')

    assert result['success'] is False
    assert 'No SQL warehouse ID provided' in result['error']

  def test_execute_dbsql_with_explicit_warehouse_id(self, mcp_server, mock_databricks_client):
    """Test SQL execution with explicitly provided warehouse ID."""
    from server.tools.sql_operations import load_sql_tools

    load_sql_tools(mcp_server)

    mock_result = Mock()
    mock_result.result = None

    mock_databricks_client.statement_execution.execute_statement.return_value = mock_result

    tool = mcp_server.tools['execute_dbsql'].fn

    with patch('server.tools.sql_operations.WorkspaceClient', return_value=mock_databricks_client):
      tool('SELECT 1', warehouse_id='explicit-warehouse')

    # Verify correct warehouse ID was used
    call_args = mock_databricks_client.statement_execution.execute_statement.call_args
    assert call_args[1]['warehouse_id'] == 'explicit-warehouse'

  def test_execute_dbsql_error_handling(self, mcp_server, mock_databricks_client):
    """Test error handling in SQL execution."""
    from server.tools.sql_operations import load_sql_tools

    load_sql_tools(mcp_server)

    mock_databricks_client.statement_execution.execute_statement.side_effect = BadRequest(
      'Invalid SQL'
    )

    tool = mcp_server.tools['execute_dbsql'].fn

    with patch('server.tools.sql_operations.WorkspaceClient', return_value=mock_databricks_client):
      with patch.dict(os.environ, {'DATABRICKS_SQL_WAREHOUSE_ID': 'test-warehouse'}):
        result = tool('INVALID SQL')

    assert result['success'] is False
    assert 'error' in result
    assert 'Invalid SQL' in result['error']


@pytest.mark.unit
@pytest.mark.tools
class TestListWarehouses:
  """Test list_warehouses tool."""

  def test_list_warehouses_success(self, mcp_server, mock_databricks_client):
    """Test successful warehouse listing."""
    from server.tools.sql_operations import load_sql_tools

    load_sql_tools(mcp_server)

    # Mock warehouse data
    mock_warehouse = Mock()
    mock_warehouse.id = 'test-warehouse-1'
    mock_warehouse.name = 'Test Warehouse'
    mock_warehouse.state = 'RUNNING'
    mock_warehouse.size = 'MEDIUM'
    mock_warehouse.cluster_size = '2X-Small'
    mock_warehouse.auto_stop_mins = 120
    mock_warehouse.creator_name = 'test@example.com'

    mock_databricks_client.warehouses.list.return_value = [mock_warehouse]

    tool = mcp_server.tools['list_warehouses'].fn

    with patch('server.tools.sql_operations.WorkspaceClient', return_value=mock_databricks_client):
      result = tool()

    assert result['success'] is True
    assert result['count'] == 1
    assert len(result['warehouses']) == 1
    assert result['warehouses'][0]['id'] == 'test-warehouse-1'
    assert result['warehouses'][0]['name'] == 'Test Warehouse'
    assert result['warehouses'][0]['state'] == 'RUNNING'

  def test_list_warehouses_empty(self, mcp_server, mock_databricks_client):
    """Test warehouse listing with no warehouses."""
    from server.tools.sql_operations import load_sql_tools

    load_sql_tools(mcp_server)

    mock_databricks_client.warehouses.list.return_value = []

    tool = mcp_server.tools['list_warehouses'].fn

    with patch('server.tools.sql_operations.WorkspaceClient', return_value=mock_databricks_client):
      result = tool()

    assert result['success'] is True
    assert result['count'] == 0
    assert len(result['warehouses']) == 0

  def test_list_warehouses_error(self, mcp_server, mock_databricks_client):
    """Test error handling in warehouse listing."""
    from server.tools.sql_operations import load_sql_tools

    load_sql_tools(mcp_server)

    mock_databricks_client.warehouses.list.side_effect = Exception('API error')

    tool = mcp_server.tools['list_warehouses'].fn

    with patch('server.tools.sql_operations.WorkspaceClient', return_value=mock_databricks_client):
      result = tool()

    assert result['success'] is False
    assert 'error' in result
    assert 'API error' in result['error']


@pytest.mark.unit
@pytest.mark.tools
class TestGetSQLWarehouse:
  """Test get_sql_warehouse tool."""

  def test_get_sql_warehouse_success(self, mcp_server, mock_databricks_client):
    """Test successful warehouse retrieval."""
    from server.tools.sql_operations import load_sql_tools

    load_sql_tools(mcp_server)

    # Mock warehouse details
    mock_warehouse = Mock()
    mock_warehouse.id = 'test-warehouse-1'
    mock_warehouse.name = 'Test Warehouse'
    mock_warehouse.state = 'RUNNING'
    mock_warehouse.size = 'MEDIUM'
    mock_warehouse.cluster_size = '2X-Small'
    mock_warehouse.auto_stop_mins = 120
    mock_warehouse.creator_name = 'test@example.com'
    mock_warehouse.tags = {}

    mock_databricks_client.warehouses.get.return_value = mock_warehouse

    tool = mcp_server.tools['get_sql_warehouse'].fn

    with patch('server.tools.sql_operations.WorkspaceClient', return_value=mock_databricks_client):
      result = tool('test-warehouse-1')

    assert result['success'] is True
    assert result['warehouse']['id'] == 'test-warehouse-1'
    assert result['warehouse']['name'] == 'Test Warehouse'
    assert result['warehouse']['state'] == 'RUNNING'

  def test_get_sql_warehouse_not_found(self, mcp_server, mock_databricks_client):
    """Test warehouse retrieval for non-existent warehouse."""
    from server.tools.sql_operations import load_sql_tools

    load_sql_tools(mcp_server)

    mock_databricks_client.warehouses.get.side_effect = NotFound('Warehouse not found')

    tool = mcp_server.tools['get_sql_warehouse'].fn

    with patch('server.tools.sql_operations.WorkspaceClient', return_value=mock_databricks_client):
      result = tool('nonexistent-warehouse')

    assert result['success'] is False
    assert 'error' in result
    assert 'Warehouse not found' in result['error']


@pytest.mark.unit
@pytest.mark.tools
class TestWarehouseManagement:
  """Test warehouse management tools (create, start, stop, delete)."""

  def test_create_sql_warehouse_success(self, mcp_server, mock_databricks_client):
    """Test successful warehouse creation."""
    from server.tools.sql_operations import load_sql_tools

    load_sql_tools(mcp_server)

    # Mock warehouse creation
    mock_warehouse = Mock()
    mock_warehouse.id = 'new-warehouse-id'

    mock_databricks_client.warehouses.create.return_value = mock_warehouse

    tool = mcp_server.tools['create_sql_warehouse'].fn

    warehouse_config = {
      'name': 'New Test Warehouse',
      'cluster_size': '2X-Small',
      'auto_stop_mins': 60,
    }

    with patch('server.tools.sql_operations.WorkspaceClient', return_value=mock_databricks_client):
      result = tool(warehouse_config)

    assert result['success'] is True
    assert result['warehouse_id'] == 'new-warehouse-id'

  def test_start_sql_warehouse_success(self, mcp_server, mock_databricks_client):
    """Test successful warehouse start."""
    from server.tools.sql_operations import load_sql_tools

    load_sql_tools(mcp_server)

    mock_databricks_client.warehouses.start.return_value = None

    tool = mcp_server.tools['start_sql_warehouse'].fn

    with patch('server.tools.sql_operations.WorkspaceClient', return_value=mock_databricks_client):
      result = tool('test-warehouse-1')

    assert result['success'] is True
    assert 'started' in result['message'].lower()

  def test_stop_sql_warehouse_success(self, mcp_server, mock_databricks_client):
    """Test successful warehouse stop."""
    from server.tools.sql_operations import load_sql_tools

    load_sql_tools(mcp_server)

    mock_databricks_client.warehouses.stop.return_value = None

    tool = mcp_server.tools['stop_sql_warehouse'].fn

    with patch('server.tools.sql_operations.WorkspaceClient', return_value=mock_databricks_client):
      result = tool('test-warehouse-1')

    assert result['success'] is True
    assert 'stopped' in result['message'].lower()

  def test_delete_sql_warehouse_success(self, mcp_server, mock_databricks_client):
    """Test successful warehouse deletion."""
    from server.tools.sql_operations import load_sql_tools

    load_sql_tools(mcp_server)

    mock_databricks_client.warehouses.delete.return_value = None

    tool = mcp_server.tools['delete_sql_warehouse'].fn

    with patch('server.tools.sql_operations.WorkspaceClient', return_value=mock_databricks_client):
      result = tool('test-warehouse-1')

    assert result['success'] is True
    assert 'deleted' in result['message'].lower()


@pytest.mark.integration
@pytest.mark.tools
class TestSQLToolsIntegration:
  """Integration tests for SQL operations tools."""

  def test_all_sql_tools_load_successfully(self):
    """Test that all SQL tools can be loaded without errors."""
    from fastmcp import FastMCP

    from server.tools.sql_operations import load_sql_tools

    test_server = FastMCP(name='test-sql-tools')

    # Should not raise any exceptions
    load_sql_tools(test_server)

    # Verify tools were loaded
    assert len(test_server.tools) > 0

    expected_tools = ['execute_dbsql', 'list_warehouses', 'get_sql_warehouse']
    for tool_name in expected_tools:
      assert tool_name in test_server.tools

  def test_sql_execution_workflow(self, mcp_server, mock_databricks_client):
    """Test a complete SQL execution workflow."""
    from server.tools.sql_operations import load_sql_tools

    load_sql_tools(mcp_server)

    # Mock warehouse listing
    mock_warehouse = Mock()
    mock_warehouse.id = 'test-warehouse'
    mock_warehouse.name = 'Test Warehouse'
    mock_warehouse.state = 'RUNNING'

    mock_databricks_client.warehouses.list.return_value = [mock_warehouse]

    # Mock query execution
    mock_result = Mock()
    mock_result.result = Mock()
    mock_result.result.data_array = [['value1']]
    mock_result.manifest = Mock()
    mock_result.manifest.schema = Mock()
    mock_result.manifest.schema.columns = [Mock(name='column1')]

    mock_databricks_client.statement_execution.execute_statement.return_value = mock_result

    with patch('server.tools.sql_operations.WorkspaceClient', return_value=mock_databricks_client):
      # List warehouses
      list_tool = mcp_server.tools['list_warehouses'].fn
      warehouses_result = list_tool()

      assert warehouses_result['success'] is True
      assert len(warehouses_result['warehouses']) == 1

      # Execute SQL on the warehouse
      execute_tool = mcp_server.tools['execute_dbsql'].fn
      sql_result = execute_tool(
        'SELECT * FROM test_table', warehouse_id=warehouses_result['warehouses'][0]['id']
      )

      assert sql_result['success'] is True
      assert sql_result['row_count'] == 1
