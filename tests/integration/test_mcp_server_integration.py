"""Integration tests for MCP server workflows."""

import os
from unittest.mock import Mock, patch

import pytest


@pytest.mark.integration
@pytest.mark.mcp
class TestMCPServerIntegration:
  """Test MCP server integration workflows."""

  def test_mcp_server_creation_and_tool_loading(self):
    """Test complete MCP server creation and tool loading workflow."""
    from fastmcp import FastMCP

    from server.prompts import load_prompts
    from server.tools import load_tools

    # Create MCP server
    mcp_server = FastMCP(name='integration-test-server')

    # Load tools and prompts
    load_tools(mcp_server)
    load_prompts(mcp_server)

    # Verify server is properly configured
    assert mcp_server.name == 'integration-test-server'
    assert len(mcp_server.tools) > 0

    # Test that core tools are available
    assert 'health' in mcp_server.tools
    assert 'list_uc_catalogs' in mcp_server.tools
    assert 'execute_dbsql' in mcp_server.tools

  def test_mcp_server_tool_execution_workflow(self, mock_databricks_client):
    """Test end-to-end tool execution workflow."""
    from fastmcp import FastMCP

    from server.tools import load_tools

    mcp_server = FastMCP(name='tool-execution-test')
    load_tools(mcp_server)

    # Test health tool execution
    health_tool = mcp_server.tools['health'].fn
    health_result = health_tool()

    assert health_result['status'] == 'healthy'
    assert health_result['service'] == 'databricks-mcp'

    # Test UC tool execution with mocked client
    mock_catalog = Mock()
    mock_catalog.name = 'integration_catalog'
    mock_catalog.catalog_type = 'MANAGED'
    mock_catalog.comment = 'Integration test catalog'
    mock_catalog.owner = 'integration@test.com'
    mock_catalog.created_at = '2024-01-01T00:00:00Z'
    mock_catalog.updated_at = '2024-01-01T00:00:00Z'
    mock_catalog.properties = {}

    mock_databricks_client.catalogs.list.return_value = [mock_catalog]

    uc_tool = mcp_server.tools['list_uc_catalogs'].fn

    with patch('server.tools.unity_catalog.WorkspaceClient', return_value=mock_databricks_client):
      uc_result = uc_tool()

    assert uc_result['success'] is True
    assert uc_result['count'] == 1
    assert uc_result['catalogs'][0]['name'] == 'integration_catalog'

  def test_mcp_server_with_fastapi_integration(self, test_client, mock_databricks_client):
    """Test MCP server integration with FastAPI application."""
    # Test that MCP server is properly mounted in FastAPI app
    response = test_client.get('/mcp/')
    # Should not return 404 (server mounted)
    assert response.status_code != 404

    # Test that API endpoints can access MCP functionality
    response = test_client.get('/api/mcp_info/discovery')
    assert response.status_code == 200

    data = response.json()
    assert 'tools' in data
    assert 'prompts' in data
    assert 'servername' in data

  def test_mcp_server_environment_configuration(self, mock_environment):
    """Test MCP server configuration with environment variables."""
    from fastmcp import FastMCP

    from server.tools.core import load_core_tools

    mcp_server = FastMCP(name='env-config-test')
    load_core_tools(mcp_server)

    # Test health tool reflects environment configuration
    health_tool = mcp_server.tools['health'].fn
    result = health_tool()

    assert result['databricks_configured'] is True  # Because mock_environment sets DATABRICKS_HOST


@pytest.mark.integration
@pytest.mark.slow
class TestDatabricsSDKIntegration:
  """Test integration with Databricks SDK workflows."""

  def test_unity_catalog_workflow(self, mock_databricks_client):
    """Test complete Unity Catalog discovery workflow."""
    from fastmcp import FastMCP

    from server.tools.unity_catalog import load_uc_tools

    mcp_server = FastMCP(name='uc-workflow-test')
    load_uc_tools(mcp_server)

    # Setup mock data for a complete workflow
    mock_catalog = Mock()
    mock_catalog.name = 'workflow_catalog'
    mock_catalog.catalog_type = 'MANAGED'
    mock_catalog.comment = 'Workflow test catalog'
    mock_catalog.owner = 'workflow@test.com'
    mock_catalog.created_at = '2024-01-01T00:00:00Z'
    mock_catalog.updated_at = '2024-01-01T00:00:00Z'
    mock_catalog.properties = {}

    mock_schema = Mock()
    mock_schema.name = 'workflow_schema'
    mock_schema.comment = 'Workflow test schema'
    mock_schema.owner = 'workflow@test.com'
    mock_schema.created_at = '2024-01-01T00:00:00Z'
    mock_schema.updated_at = '2024-01-01T00:00:00Z'
    mock_schema.properties = {}

    mock_table = Mock()
    mock_table.name = 'workflow_table'
    mock_table.table_type = 'MANAGED'
    mock_table.comment = 'Workflow test table'
    mock_table.owner = 'workflow@test.com'
    mock_table.created_at = '2024-01-01T00:00:00Z'
    mock_table.updated_at = '2024-01-01T00:00:00Z'
    mock_table.properties = {}
    mock_table.storage_location = 's3://test-bucket/path'
    mock_table.data_source_format = 'DELTA'
    mock_table.columns = [
      Mock(name='id', type_name='bigint', comment='ID column'),
      Mock(name='name', type_name='string', comment='Name column'),
    ]

    # Configure mock responses
    mock_databricks_client.catalogs.list.return_value = [mock_catalog]
    mock_databricks_client.catalogs.get.return_value = mock_catalog
    mock_databricks_client.schemas.list.return_value = [mock_schema]
    mock_databricks_client.schemas.get.return_value = mock_schema
    mock_databricks_client.tables.list.return_value = [mock_table]
    mock_databricks_client.tables.get.return_value = mock_table

    with patch('server.tools.unity_catalog.WorkspaceClient', return_value=mock_databricks_client):
      # Step 1: List catalogs
      list_tool = mcp_server.tools['list_uc_catalogs'].fn
      catalogs_result = list_tool()

      assert catalogs_result['success'] is True
      assert catalogs_result['count'] == 1
      catalog_name = catalogs_result['catalogs'][0]['name']

      # Step 2: Describe catalog
      describe_catalog_tool = mcp_server.tools['describe_uc_catalog'].fn
      catalog_result = describe_catalog_tool(catalog_name)

      assert catalog_result['success'] is True
      assert catalog_result['catalog']['name'] == catalog_name
      assert catalog_result['schema_count'] == 1
      schema_name = catalog_result['schemas'][0]['name']

      # Step 3: Describe schema
      describe_schema_tool = mcp_server.tools['describe_uc_schema'].fn
      schema_result = describe_schema_tool(catalog_name, schema_name)

      assert schema_result['success'] is True
      assert schema_result['schema']['name'] == schema_name
      assert schema_result['table_count'] == 1
      table_name = schema_result['tables'][0]['name']

      # Step 4: Describe table
      describe_table_tool = mcp_server.tools['describe_uc_table'].fn
      table_result = describe_table_tool(f'{catalog_name}.{schema_name}.{table_name}')

      assert table_result['success'] is True
      assert table_result['table']['name'] == table_name
      assert table_result['table']['column_count'] == 2

  def test_sql_operations_workflow(self, mock_databricks_client):
    """Test complete SQL operations workflow."""
    from fastmcp import FastMCP

    from server.tools.sql_operations import load_sql_tools

    mcp_server = FastMCP(name='sql-workflow-test')
    load_sql_tools(mcp_server)

    # Setup mock data
    mock_warehouse = Mock()
    mock_warehouse.id = 'workflow-warehouse'
    mock_warehouse.name = 'Workflow Warehouse'
    mock_warehouse.state = 'RUNNING'
    mock_warehouse.size = 'MEDIUM'
    mock_warehouse.cluster_size = '2X-Small'
    mock_warehouse.auto_stop_mins = 120
    mock_warehouse.creator_name = 'workflow@test.com'
    mock_warehouse.tags = {}

    mock_sql_result = Mock()
    mock_sql_result.result = Mock()
    mock_sql_result.result.data_array = [['1', 'Alice'], ['2', 'Bob']]
    mock_sql_result.manifest = Mock()
    mock_sql_result.manifest.schema = Mock()
    mock_sql_result.manifest.schema.columns = [Mock(name='id'), Mock(name='name')]

    # Configure mock responses
    mock_databricks_client.warehouses.list.return_value = [mock_warehouse]
    mock_databricks_client.warehouses.get.return_value = mock_warehouse
    mock_databricks_client.statement_execution.execute_statement.return_value = mock_sql_result

    with patch('server.tools.sql_operations.WorkspaceClient', return_value=mock_databricks_client):
      # Step 1: List warehouses
      list_tool = mcp_server.tools['list_warehouses'].fn
      warehouses_result = list_tool()

      assert warehouses_result['success'] is True
      assert warehouses_result['count'] == 1
      warehouse_id = warehouses_result['warehouses'][0]['id']

      # Step 2: Get warehouse details
      get_tool = mcp_server.tools['get_sql_warehouse'].fn
      warehouse_result = get_tool(warehouse_id)

      assert warehouse_result['success'] is True
      assert warehouse_result['warehouse']['id'] == warehouse_id
      assert warehouse_result['warehouse']['state'] == 'RUNNING'

      # Step 3: Execute SQL query
      execute_tool = mcp_server.tools['execute_dbsql'].fn
      sql_result = execute_tool('SELECT id, name FROM test_table', warehouse_id=warehouse_id)

      assert sql_result['success'] is True
      assert sql_result['row_count'] == 2
      assert sql_result['data']['columns'] == ['id', 'name']
      assert len(sql_result['data']['rows']) == 2


@pytest.mark.integration
@pytest.mark.api
class TestFastAPIIntegration:
  """Test FastAPI application integration workflows."""

  def test_complete_api_workflow(self, test_client, tmp_path, monkeypatch):
    """Test complete API workflow from endpoints."""
    # Create test prompts for prompts endpoint
    prompts_dir = tmp_path / 'prompts'
    prompts_dir.mkdir()
    (prompts_dir / 'test_workflow.md').write_text('# Test Workflow\n\nWorkflow test prompt.')

    monkeypatch.chdir(tmp_path)

    # Step 1: Get MCP server info
    response = test_client.get('/api/mcp_info/info')
    assert response.status_code == 200
    mcp_info = response.json()
    assert 'mcp_url' in mcp_info
    assert 'capabilities' in mcp_info

    # Step 2: Get MCP discovery information
    response = test_client.get('/api/mcp_info/discovery')
    assert response.status_code == 200
    discovery = response.json()
    assert 'tools' in discovery
    assert 'prompts' in discovery

    # Step 3: List available prompts
    response = test_client.get('/api/prompts')
    assert response.status_code == 200
    prompts = response.json()
    assert len(prompts) > 0

    # Step 4: Get specific prompt content
    prompt_name = prompts[0]['name']
    response = test_client.get(f'/api/prompts/{prompt_name}')
    assert response.status_code == 200
    prompt_content = response.json()
    assert 'content' in prompt_content

    # Step 5: Get user info (will fail without proper auth, but endpoint should exist)
    response = test_client.get('/api/user/me')
    assert response.status_code != 404  # Endpoint exists

  def test_api_error_handling_workflow(self, test_client):
    """Test API error handling across different endpoints."""
    # Test 404 errors
    response = test_client.get('/api/prompts/nonexistent_prompt')
    assert response.status_code == 404
    error_data = response.json()
    assert 'detail' in error_data

    response = test_client.get('/api/mcp_info/prompt/nonexistent_prompt')
    assert response.status_code == 404
    error_data = response.json()
    assert 'detail' in error_data

    # Test that error responses have consistent structure
    assert isinstance(error_data, dict)
    assert 'detail' in error_data

  def test_api_cors_and_middleware_workflow(self, test_client):
    """Test CORS and middleware functionality."""
    # Test OPTIONS request (CORS preflight)
    response = test_client.options('/api/prompts')
    # Should not return 405 (method not allowed) due to CORS middleware
    assert response.status_code != 405

    # Test that responses include proper content types
    response = test_client.get('/api/mcp_info/info')
    assert response.status_code == 200
    assert 'application/json' in response.headers.get('content-type', '')


@pytest.mark.integration
@pytest.mark.mcp
@pytest.mark.proxy
class TestMCPProxyIntegration:
  """Test MCP proxy integration workflows."""

  def test_proxy_initialization_workflow(self, mock_requests):
    """Test complete proxy initialization and request workflow."""
    from dba_mcp_proxy.mcp_client import MCPProxy

    # Mock successful initialization responses
    init_response = Mock()
    init_response.headers = {'mcp-session-id': 'integration-session-123'}

    # Mock successful request responses
    request_response = Mock()
    request_response.status_code = 200
    request_response.json.return_value = {
      'jsonrpc': '2.0',
      'id': 'test-request',
      'result': 'integration_success',
    }
    request_response.text = (
      '{"jsonrpc": "2.0", "id": "test-request", "result": "integration_success"}'
    )

    proxy = MCPProxy('https://test.databricks.com', 'http://localhost:8000')

    with (
      patch.object(proxy.session, 'get', return_value=init_response),
      patch.object(proxy.session, 'post', return_value=request_response),
    ):
      # Test initialization
      proxy._initialize_session()
      assert proxy.initialized is True
      assert proxy.session_id == 'integration-session-123'

      # Test request handling
      test_request = {'jsonrpc': '2.0', 'id': 'test-request', 'method': 'tools/list'}

      result = proxy.proxy_request(test_request)

      assert result['jsonrpc'] == '2.0'
      assert result['id'] == 'test-request'
      assert result['result'] == 'integration_success'

  def test_proxy_error_handling_workflow(self, mock_requests):
    """Test proxy error handling across different failure scenarios."""
    from dba_mcp_proxy.mcp_client import MCPProxy

    proxy = MCPProxy('https://test.databricks.com', 'https://app.databricksapps.com')

    # Test network error handling
    with patch.object(proxy.session, 'post', side_effect=Exception('Network error')):
      test_request = {'jsonrpc': '2.0', 'id': 'error-test', 'method': 'test_method'}

      result = proxy.proxy_request(test_request)

      assert result['jsonrpc'] == '2.0'
      assert result['id'] == 'error-test'
      assert 'error' in result
      assert 'Network error' in result['error']['message']

    # Test HTTP error handling
    error_response = Mock()
    error_response.status_code = 500
    error_response.text = 'Internal Server Error'

    with patch.object(proxy.session, 'post', return_value=error_response):
      result = proxy.proxy_request(test_request)

      assert result['jsonrpc'] == '2.0'
      assert result['id'] == 'error-test'
      assert 'error' in result
      assert result['error']['code'] == 500


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndWorkflows:
  """Test complete end-to-end workflows."""

  def test_mcp_server_to_api_to_proxy_workflow(self, test_client, mock_databricks_client):
    """Test workflow from MCP server through API to proxy integration."""
    # Step 1: Verify MCP server has tools loaded via API
    response = test_client.get('/api/mcp_info/discovery')
    assert response.status_code == 200
    discovery = response.json()

    tool_names = [tool['name'] for tool in discovery['tools']]
    assert 'health' in tool_names
    assert 'list_uc_catalogs' in tool_names

    # Step 2: Verify individual tool accessibility via API info
    response = test_client.get('/api/mcp_info/config')
    assert response.status_code == 200
    config = response.json()
    assert 'servername' in config

    # Step 3: Simulate proxy workflow (would normally go through MCP protocol)
    from dba_mcp_proxy.mcp_client import MCPProxy

    proxy = MCPProxy('https://test.databricks.com', 'http://localhost:8000')

    # Mock proxy responses that would come from our MCP server
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
      'jsonrpc': '2.0',
      'id': 'health-check',
      'result': {'status': 'healthy', 'service': 'databricks-mcp', 'databricks_configured': True},
    }
    mock_response.text = mock_response.json.return_value.__str__()

    with (
      patch.object(proxy.session, 'get', return_value=Mock(headers={})),
      patch.object(proxy.session, 'post', return_value=mock_response),
    ):
      # Simulate MCP protocol request that would call our health tool
      health_request = {
        'jsonrpc': '2.0',
        'id': 'health-check',
        'method': 'tools/call',
        'params': {'name': 'health', 'arguments': {}},
      }

      result = proxy.proxy_request(health_request)

      # This demonstrates the complete workflow:
      # MCP Server (with loaded tools) -> API (discovery/config) -> Proxy (MCP protocol)
      assert result['jsonrpc'] == '2.0'
      assert result['id'] == 'health-check'

  def test_configuration_and_deployment_workflow(self, test_client, mock_environment):
    """Test configuration workflow for different deployment scenarios."""
    # Test local development configuration
    with patch.dict(os.environ, {'DATABRICKS_HOST': 'https://local.databricks.com'}, clear=False):
      if 'DATABRICKS_APP_PORT' in os.environ:
        del os.environ['DATABRICKS_APP_PORT']

      response = test_client.get('/api/mcp_info/info')
      local_info = response.json()

      assert 'localhost' in local_info['mcp_url']

      response = test_client.get('/api/mcp_info/config')
      local_config = response.json()

      assert local_config['is_databricks_app'] is False

    # Test Databricks app configuration
    with patch.dict(
      os.environ,
      {'DATABRICKS_HOST': 'https://production.databricks.com', 'DATABRICKS_APP_PORT': '8000'},
    ):
      response = test_client.get('/api/mcp_info/info')
      app_info = response.json()

      assert app_info['mcp_url'] == '/mcp/'

      response = test_client.get('/api/mcp_info/config')
      app_config = response.json()

      assert app_config['is_databricks_app'] is True

    # Verify that both configurations provide necessary information
    assert 'servername' in local_config
    assert 'servername' in app_config
    assert 'client_path' in local_config
    assert 'client_path' in app_config
