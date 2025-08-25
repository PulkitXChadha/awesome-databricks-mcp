"""MCP Protocol compliance tests."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from server.prompts import load_prompts
from server.tools import load_tools
from tests.utils import assert_error_response


class TestMCPProtocolCompliance:
  """Test MCP Protocol implementation compliance."""

  @pytest.mark.mcp
  def test_tool_discovery(self, mcp_server, mock_env_vars):
    """Verify all tools are discoverable."""
    # Load all tools into the MCP server
    load_tools(mcp_server)

    # Verify tool registration
    tools = mcp_server._tool_manager._tools

    # Should have all expected tools loaded
    expected_tool_count = 97  # Based on actual tool count
    assert len(tools) == expected_tool_count

    # Verify core tools are registered
    core_tools = ['health']
    for tool_name in core_tools:
      assert tool_name in tools
      tool = tools[tool_name]
      assert hasattr(tool, 'fn')
      assert callable(tool.fn)

    # Verify SQL operation tools are registered
    sql_tools = [
      'execute_dbsql',
      'list_warehouses',
      'get_sql_warehouse',
      'create_sql_warehouse',
      'start_sql_warehouse',
      'stop_sql_warehouse',
      'delete_sql_warehouse',
      'list_queries',
      'get_query',
      'get_query_results',
      'cancel_query',
    ]
    for tool_name in sql_tools:
      assert tool_name in tools
      tool = tools[tool_name]
      assert hasattr(tool, 'fn')
      assert callable(tool.fn)

    # Verify Unity Catalog tools are registered
    uc_tools = [
      'list_uc_catalogs',
      'describe_uc_catalog',
      'list_uc_schemas',
      'describe_uc_schema',
      'list_uc_tables',
      'describe_uc_table',
      'list_uc_volumes',
      'describe_uc_volume',
      'list_uc_functions',
      'describe_uc_function',
      'list_uc_models',
      'describe_uc_model',
    ]
    for tool_name in uc_tools:
      assert tool_name in tools
      tool = tools[tool_name]
      assert hasattr(tool, 'fn')
      assert callable(tool.fn)

    # Verify Jobs & Pipelines tools are registered
    job_tools = [
      'list_jobs',
      'get_job',
      'create_job',
      'update_job',
      'delete_job',
      'list_job_runs',
      'get_job_run',
      'submit_job_run',
      'cancel_job_run',
      'list_pipelines',
      'get_pipeline',
      'create_pipeline',
      'update_pipeline',
    ]
    for tool_name in job_tools:
      assert tool_name in tools
      tool = tools[tool_name]
      assert hasattr(tool, 'fn')
      assert callable(tool.fn)

    # Verify Dashboard tools are registered
    dashboard_tools = [
      'list_lakeview_dashboards',
      'get_lakeview_dashboard',
      'create_lakeview_dashboard',
      'update_lakeview_dashboard',
      'list_dashboards',
      'get_dashboard',
      'create_dashboard',
    ]
    for tool_name in dashboard_tools:
      assert tool_name in tools
      tool = tools[tool_name]
      assert hasattr(tool, 'fn')
      assert callable(tool.fn)

    # Test tool discoverability through MCP protocol
    # Verify that each tool has proper metadata
    for tool_name, tool in tools.items():
      assert hasattr(tool, 'fn')
      assert callable(tool.fn)
      # FastMCP tools should have description
      if hasattr(tool, 'description'):
        assert isinstance(tool.description, str)
        assert len(tool.description) > 0

  @pytest.mark.mcp
  def test_prompt_loading(self, mcp_server, mock_env_vars):
    """Test prompt system integration."""
    # Load prompts into the MCP server
    load_prompts(mcp_server)

    # Verify prompt registration
    if hasattr(mcp_server, '_prompt_manager'):
      prompts = mcp_server._prompt_manager._prompts

      # Should have expected prompts loaded
      expected_prompts = ['build_ldp_pipeline', 'performance_optimization']
      assert len(prompts) >= 2

      for prompt_name in expected_prompts:
        assert prompt_name in prompts
        prompt = prompts[prompt_name]
        assert hasattr(prompt, 'fn') or callable(prompt)

    # Test prompt loading from files
    prompt_files = Path('prompts').glob('*.md')
    prompt_file_names = [f.stem for f in prompt_files]

    assert 'build_ldp_pipeline' in prompt_file_names
    assert 'performance_optimization' in prompt_file_names

    # Verify prompt file contents can be loaded
    for prompt_file in prompt_files:
      with open(prompt_file, 'r') as f:
        content = f.read()
        assert len(content) > 0
        lines = content.strip().split('\n')
        # First line should be a title starting with #
        assert lines[0].startswith('#')

  @pytest.mark.mcp
  def test_protocol_message_validation(self, mcp_server, mock_env_vars):
    """Test MCP protocol message validation."""
    # Load tools for testing
    load_tools(mcp_server)

    # Test successful tool execution returns proper structure
    with patch('server.tools.core.os.environ.get') as mock_env:
      mock_env.side_effect = lambda key, default=None: {
        'DATABRICKS_HOST': 'https://test.cloud.databricks.com',
        'DATABRICKS_TOKEN': 'test-token',
      }.get(key, default)

      health_tool = mcp_server._tool_manager._tools['health']
      result = health_tool.fn()

      # Verify response structure follows MCP protocol expectations
      assert isinstance(result, dict)
      assert 'status' in result
      assert result['status'] == 'healthy'
      assert 'service' in result
      assert 'databricks_configured' in result

    # Test tool with parameters
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      mock_client.return_value.catalogs.list.return_value = []

      catalog_tool = mcp_server._tool_manager._tools['list_uc_catalogs']
      result = catalog_tool.fn()

      # Verify standard MCP response structure
      assert isinstance(result, dict)
      assert 'success' in result
      assert result['success'] is True
      assert 'catalogs' in result
      assert 'count' in result
      assert 'message' in result

    # Test tool parameter validation
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      mock_schema = Mock()
      mock_schema.name = 'test_schema'
      mock_schema.comment = 'Test schema'
      mock_schema.owner = 'test@example.com'
      mock_schema.created_at = 1234567890
      mock_schema.updated_at = 1234567890
      mock_schema.properties = {}

      mock_client.return_value.schemas.get.return_value = mock_schema
      mock_client.return_value.tables.list.return_value = []

      schema_tool = mcp_server._tool_manager._tools['describe_uc_schema']
      result = schema_tool.fn('main', 'test_schema')

      # Verify parameter handling in response
      assert isinstance(result, dict)
      assert result['success'] is True
      assert 'schema' in result
      assert result['schema']['name'] == 'test_schema'

  @pytest.mark.mcp
  def test_error_response_formatting(self, mcp_server, mock_env_vars):
    """Test MCP protocol error response formatting."""
    # Load tools for testing
    load_tools(mcp_server)

    # Test authentication/connection error handling
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      # Simulate connection error
      mock_client.side_effect = Exception('Authentication failed: Invalid token')

      catalog_tool = mcp_server._tool_manager._tools['list_uc_catalogs']
      result = catalog_tool.fn()

      # Verify error response follows MCP protocol
      assert_error_response(result)
      assert 'error' in result
      assert 'Authentication failed' in result['error']
      assert result['success'] is False
      assert 'catalogs' in result
      assert result['catalogs'] == []
      assert result['count'] == 0

    # Test permission error handling
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      from databricks.sdk.errors import PermissionDenied

      mock_client.return_value.catalogs.list.side_effect = PermissionDenied('Access denied')

      catalog_tool = mcp_server._tool_manager._tools['list_uc_catalogs']
      result = catalog_tool.fn()

      # Verify permission error response structure
      assert_error_response(result)
      assert 'error' in result
      assert 'Access denied' in result['error'] or 'PermissionDenied' in result['error']

    # Test invalid parameter handling
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      table_tool = mcp_server._tool_manager._tools['describe_uc_table']
      result = table_tool.fn('invalid-table-name')  # Should be catalog.schema.table format

      # Verify parameter validation error response
      assert_error_response(result)
      assert 'error' in result
      assert 'format' in result['error'].lower()

    # Test SQL execution error handling
    with patch('server.tools.sql_operations.WorkspaceClient') as mock_client:
      # Mock SQL execution failure
      error_response = Mock()
      error_response.status.state = 'FAILED'
      error_response.status.error = Mock(message='SQL syntax error: Invalid query')

      mock_client.return_value.statement_execution.execute_statement.return_value = error_response

      sql_tool = mcp_server._tool_manager._tools['execute_dbsql']
      result = sql_tool.fn(query='INVALID SQL QUERY', warehouse_id='test-warehouse')

      # Verify SQL error response structure
      assert result['success'] is False
      assert 'error' in result

  @pytest.mark.mcp
  def test_tool_metadata_compliance(self, mcp_server, mock_env_vars):
    """Test tool metadata follows MCP protocol standards."""
    # Load tools for metadata testing
    load_tools(mcp_server)

    tools = mcp_server._tool_manager._tools

    # Verify each tool has required metadata
    for tool_name, tool in tools.items():
      # Tool must be callable
      assert hasattr(tool, 'fn')
      assert callable(tool.fn)

      # Tool should have docstring/description
      if hasattr(tool.fn, '__doc__'):
        assert tool.fn.__doc__ is not None
        assert len(tool.fn.__doc__.strip()) > 0

    # Test specific tool metadata for key operations
    key_tools = {
      'health': 'Core health check functionality',
      'list_uc_catalogs': 'Unity Catalog discovery',
      'execute_dbsql': 'SQL query execution',
      'list_jobs': 'Job management',
      'list_lakeview_dashboards': 'Dashboard operations',
    }

    for tool_name, expected_purpose in key_tools.items():
      assert tool_name in tools
      tool = tools[tool_name]

      # Verify tool has documentation
      if hasattr(tool.fn, '__doc__'):
        doc = tool.fn.__doc__
        assert doc is not None
        assert len(doc.strip()) > 10  # Meaningful documentation

    # Test tool parameter inspection
    health_tool = tools['health']
    execute_sql_tool = tools['execute_dbsql']

    # Health tool should have no required parameters
    import inspect

    health_sig = inspect.signature(health_tool.fn)
    assert len(health_sig.parameters) == 0

    # SQL tool should have required parameters
    sql_sig = inspect.signature(execute_sql_tool.fn)
    assert 'query' in sql_sig.parameters
    # warehouse_id should have default value or be optional

  @pytest.mark.mcp
  def test_prompt_metadata_compliance(self, mcp_server, mock_env_vars):
    """Test prompt metadata follows MCP protocol standards."""
    # Load prompts for testing
    load_prompts(mcp_server)

    if hasattr(mcp_server, '_prompt_manager'):
      prompts = mcp_server._prompt_manager._prompts

      # Verify prompt registration structure
      assert len(prompts) >= 2

      expected_prompts = ['build_ldp_pipeline', 'performance_optimization']
      for prompt_name in expected_prompts:
        assert prompt_name in prompts
        prompt = prompts[prompt_name]

        # Verify prompt is callable or has proper structure
        assert callable(prompt) or hasattr(prompt, 'fn')

    # Test prompt file structure compliance
    prompt_files = list(Path('prompts').glob('*.md'))
    assert len(prompt_files) >= 2

    for prompt_file in prompt_files:
      with open(prompt_file, 'r') as f:
        content = f.read()

      # Verify prompt file structure
      lines = content.strip().split('\n')
      assert len(lines) > 0

      # First line should be title with # prefix
      title_line = lines[0].strip()
      assert title_line.startswith('#')
      assert len(title_line) > 1  # More than just #

      # Content should be substantial
      assert len(content.strip()) > 50  # Meaningful prompt content

  @pytest.mark.mcp
  def test_protocol_response_structure(self, mcp_server, mock_env_vars):
    """Test all responses follow MCP protocol structure."""
    # Load tools for response testing
    load_tools(mcp_server)

    # Test various tool response structures
    test_cases = [
      {
        'tool': 'health',
        'args': {},
        'expected_keys': ['status', 'service', 'databricks_configured'],
      },
      {
        'tool': 'list_warehouses',
        'args': {},
        'expected_keys': ['success', 'warehouses', 'count', 'message'],
        'mock_setup': lambda client: setattr(client.sql_warehouses, 'list', lambda: []),
      },
      {
        'tool': 'list_uc_catalogs',
        'args': {},
        'expected_keys': ['success', 'catalogs', 'count', 'message'],
        'mock_setup': lambda client: setattr(client.catalogs, 'list', lambda: []),
      },
    ]

    for test_case in test_cases:
      tool_name = test_case['tool']
      args = test_case['args']
      expected_keys = test_case['expected_keys']

      tool = mcp_server._tool_manager._tools[tool_name]

      # Setup mocking if needed
      if 'mock_setup' in test_case:
        with (
          patch('server.tools.sql_operations.WorkspaceClient') as mock_sql_client,
          patch('server.tools.unity_catalog.WorkspaceClient') as mock_uc_client,
        ):
          client = Mock()
          mock_sql_client.return_value = client
          mock_uc_client.return_value = client
          test_case['mock_setup'](client)

          result = tool.fn(**args)
      else:
        # For tools that don't need Databricks client (like health)
        with patch('server.tools.core.os.environ.get') as mock_env:
          mock_env.side_effect = lambda key, default=None: {
            'DATABRICKS_HOST': 'https://test.cloud.databricks.com',
            'DATABRICKS_TOKEN': 'test-token',
          }.get(key, default)

          result = tool.fn(**args)

      # Verify response structure
      assert isinstance(result, dict)
      for key in expected_keys:
        assert key in result, f'Tool {tool_name} missing required key: {key}'

      # Verify response is JSON serializable (MCP requirement)
      try:
        json.dumps(result)
      except (TypeError, ValueError) as e:
        pytest.fail(f'Tool {tool_name} response not JSON serializable: {e}')

  @pytest.mark.mcp
  def test_async_compatibility(self, mcp_server, mock_env_vars):
    """Test MCP server async compatibility."""
    # Load tools and prompts
    load_tools(mcp_server)
    load_prompts(mcp_server)

    # Verify MCP server has async capabilities
    assert hasattr(mcp_server, 'http_app')

    # Create ASGI app (this is how the server is used in production)
    asgi_app = mcp_server.http_app(path='/mcp/')
    assert asgi_app is not None

    # Verify the app has proper ASGI structure
    assert hasattr(asgi_app, 'lifespan')

    # Test that tools work in async context (FastMCP handles sync/async)
    with patch('server.tools.core.os.environ.get') as mock_env:
      mock_env.side_effect = lambda key, default=None: {
        'DATABRICKS_HOST': 'https://test.cloud.databricks.com',
        'DATABRICKS_TOKEN': 'test-token',
      }.get(key, default)

      health_tool = mcp_server._tool_manager._tools['health']
      result = health_tool.fn()

      # Should work properly in async context
      assert result['status'] == 'healthy'

  @pytest.mark.mcp
  def test_tool_parameter_validation(self, mcp_server, mock_env_vars):
    """Test tool parameter validation follows MCP standards."""
    # Load tools for parameter testing
    load_tools(mcp_server)

    # Test tools with different parameter requirements
    tools_with_params = {
      'describe_uc_catalog': {'required': ['catalog_name'], 'optional': []},
      'describe_uc_schema': {
        'required': ['catalog_name', 'schema_name'],
        'optional': ['include_columns'],
      },
      'execute_dbsql': {
        'required': ['query'],
        'optional': ['warehouse_id', 'catalog', 'schema', 'limit'],
      },
    }

    import inspect

    for tool_name, param_info in tools_with_params.items():
      tool = mcp_server._tool_manager._tools[tool_name]
      sig = inspect.signature(tool.fn)

      # Check required parameters
      for required_param in param_info['required']:
        assert required_param in sig.parameters
        param = sig.parameters[required_param]
        # Required params should not have defaults
        if required_param in ['catalog_name', 'schema_name', 'query']:
          assert param.default == inspect.Parameter.empty

      # Check optional parameters
      for optional_param in param_info['optional']:
        if optional_param in sig.parameters:
          param = sig.parameters[optional_param]
          # Optional params should have defaults
          assert param.default != inspect.Parameter.empty

  @pytest.mark.mcp
  def test_error_handling_consistency(self, mcp_server, mock_env_vars):
    """Test consistent error handling across all tools."""
    # Load tools for error testing
    load_tools(mcp_server)

    # Test error scenarios for different tool types
    error_test_cases = [
      {
        'tool': 'list_uc_catalogs',
        'error_type': Exception,
        'error_message': 'Connection timeout',
        'client_patch': 'server.tools.unity_catalog.WorkspaceClient',
      },
      {
        'tool': 'execute_dbsql',
        'error_type': Exception,
        'error_message': 'Warehouse not found',
        'client_patch': 'server.tools.sql_operations.WorkspaceClient',
      },
      {
        'tool': 'list_jobs',
        'error_type': Exception,
        'error_message': 'API rate limit exceeded',
        'client_patch': 'server.tools.jobs_pipelines.WorkspaceClient',
      },
    ]

    for test_case in error_test_cases:
      tool_name = test_case['tool']
      error_type = test_case['error_type']
      error_message = test_case['error_message']
      client_patch = test_case['client_patch']

      with patch(client_patch) as mock_client:
        mock_client.side_effect = error_type(error_message)

        tool = mcp_server._tool_manager._tools[tool_name]

        # Execute tool with error condition
        if tool_name == 'execute_dbsql':
          result = tool.fn(query='SELECT 1', warehouse_id='invalid-warehouse')
        else:
          result = tool.fn()

        # Verify consistent error response structure
        assert isinstance(result, dict)
        assert 'success' in result
        assert result['success'] is False
        assert 'error' in result
        assert error_message in result['error']

        # Verify error response is JSON serializable
        try:
          json.dumps(result)
        except (TypeError, ValueError) as e:
          pytest.fail(f'Error response for {tool_name} not JSON serializable: {e}')

  @pytest.mark.mcp
  def test_tool_registration_verification(self, mcp_server, mock_env_vars):
    """Verify tool registration process follows MCP protocol."""
    # Start with empty server
    tools_before = len(mcp_server._tool_manager._tools)

    # Load tools module by module and verify registration
    from server.tools.core import load_core_tools

    load_core_tools(mcp_server)

    tools_after_core = len(mcp_server._tool_manager._tools)
    assert tools_after_core > tools_before
    assert 'health' in mcp_server._tool_manager._tools

    # Load SQL tools
    from server.tools.sql_operations import load_sql_tools

    load_sql_tools(mcp_server)

    tools_after_sql = len(mcp_server._tool_manager._tools)
    assert tools_after_sql > tools_after_core
    assert 'execute_dbsql' in mcp_server._tool_manager._tools
    assert 'list_warehouses' in mcp_server._tool_manager._tools

    # Load Unity Catalog tools
    from server.tools.unity_catalog import load_uc_tools

    load_uc_tools(mcp_server)

    tools_after_uc = len(mcp_server._tool_manager._tools)
    assert tools_after_uc > tools_after_sql
    assert 'list_uc_catalogs' in mcp_server._tool_manager._tools
    assert 'describe_uc_table' in mcp_server._tool_manager._tools

    # Verify no duplicate tool registrations
    tool_names = list(mcp_server._tool_manager._tools.keys())
    assert len(tool_names) == len(set(tool_names))  # No duplicates

    # Verify all tools are properly accessible
    for tool_name, tool in mcp_server._tool_manager._tools.items():
      assert hasattr(tool, 'fn')
      assert callable(tool.fn)

  @pytest.mark.mcp
  def test_protocol_versioning(self, mcp_server, mock_env_vars):
    """Test MCP protocol version compatibility."""
    # Load tools and prompts
    load_tools(mcp_server)
    load_prompts(mcp_server)

    # Verify FastMCP version compatibility
    import fastmcp

    assert hasattr(fastmcp, '__version__')

    # Test that server configuration is accessible
    assert hasattr(mcp_server, 'name')
    assert mcp_server.name == 'test-databricks-mcp'

    # Verify ASGI app creation (MCP protocol transport)
    asgi_app = mcp_server.http_app(path='/test/')
    assert asgi_app is not None

    # Test server info structure
    server_info = {
      'name': mcp_server.name,
      'version': '0.1.0',  # From app configuration
      'tool_count': len(mcp_server._tool_manager._tools),
      'prompt_count': len(mcp_server._prompt_manager._prompts)
      if hasattr(mcp_server, '_prompt_manager')
      else 0,
    }

    # Verify server info is JSON serializable
    try:
      json.dumps(server_info)
    except (TypeError, ValueError) as e:
      pytest.fail(f'Server info not JSON serializable: {e}')

    # Verify minimum tool coverage for Databricks operations
    assert server_info['tool_count'] >= 60  # Should have comprehensive tool set
    assert server_info['prompt_count'] >= 2  # Should have business prompts
