"""Test Unity Catalog tools."""

from unittest.mock import Mock, patch

import pytest

from server.tools.unity_catalog import load_uc_tools
from tests.mock_factory import (
  mock_catalog_list,
  mock_empty_client,
  mock_error_client,
  mock_workspace_client,
)
from tests.utils import assert_error_response, assert_success_response


class TestUnityCatalogTools:
  """Test Unity Catalog operations."""

  @pytest.mark.unit
  def test_list_uc_catalogs_success(self, mcp_server, mock_env_vars):
    """Test successful catalog listing."""
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      client = mock_workspace_client()

      # Setup catalogs using simplified mock data
      catalog_data = mock_catalog_list()
      catalogs = []
      for cat in catalog_data:
        mock_cat = Mock()
        for key, value in cat.items():
          setattr(mock_cat, key, value)
        catalogs.append(mock_cat)

      client.catalogs.list.return_value = catalogs
      mock_client.return_value = client

      load_uc_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_uc_catalogs']
      result = tool.fn()

      assert_success_response(result)
      assert result['count'] == 2
      assert len(result['catalogs']) == 2
      assert result['catalogs'][0]['name'] == 'main'

  @pytest.mark.unit
  def test_list_uc_catalogs_empty(self, mcp_server, mock_env_vars):
    """Test catalog listing with no catalogs."""
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      mock_client.return_value = mock_empty_client()

      load_uc_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_uc_catalogs']
      result = tool.fn()

      assert_success_response(result)
      assert result['count'] == 0
      assert result['catalogs'] == []

  @pytest.mark.unit
  def test_list_uc_catalogs_error(self, mcp_server, mock_env_vars):
    """Test catalog listing with connection error."""
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      mock_client.return_value = mock_error_client()

      load_uc_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_uc_catalogs']
      result = tool.fn()

      assert_error_response(result)
      assert 'Connection failed' in result['error']

  @pytest.mark.unit
  def test_describe_uc_catalog(self, mcp_server, mock_env_vars):
    """Test describing a specific catalog."""
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      client = mock_workspace_client()

      # Setup catalogs
      catalog_data = mock_catalog_list()
      catalogs = []
      for cat in catalog_data:
        mock_cat = Mock()
        for key, value in cat.items():
          setattr(mock_cat, key, value)
        catalogs.append(mock_cat)

      client.catalogs.list.return_value = catalogs
      client.catalogs.get.side_effect = lambda name: next(
        (c for c in catalogs if c.name == name), None
      )

      # Add schemas to the catalog
      from tests.utils import create_mock_schema

      schemas = [create_mock_schema('main', 'default'), create_mock_schema('main', 'bronze')]
      # Add required attributes for schema objects
      for schema in schemas:
        schema.comment = f'Test schema {schema.name}'
        schema.owner = 'test@example.com'
        schema.created_at = 1234567890
        schema.updated_at = 1234567890
        schema.properties = {'environment': 'test'}

      client.schemas.list.return_value = schemas
      mock_client.return_value = client

      load_uc_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['describe_uc_catalog']
      result = tool.fn('main')

      assert_success_response(result)
      assert result['catalog']['name'] == 'main'
      assert len(result['schemas']) == 2

  @pytest.mark.unit
  def test_describe_uc_schema(self, mcp_server, mock_env_vars):
    """Test describing a specific schema."""
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      client = Mock()

      # Mock schema
      mock_schema = Mock()
      mock_schema.name = 'default'
      mock_schema.catalog_name = 'main'
      mock_schema.owner = 'test@example.com'
      client.schemas.get.return_value = mock_schema

      # Mock tables
      from tests.utils import create_mock_table

      tables = [create_mock_table('main', 'default', 'users')]
      client.tables.list.return_value = tables
      mock_client.return_value = client

      load_uc_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['describe_uc_schema']
      result = tool.fn('main', 'default')

      assert_success_response(result)
      assert result['schema']['name'] == 'default'
      assert len(result['tables']) == 1
      assert result['tables'][0]['name'] == 'users'

  @pytest.mark.unit
  def test_describe_uc_table(self, mcp_server, mock_env_vars):
    """Test describing a specific table."""
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      client = Mock()

      # Mock table
      from tests.utils import create_mock_table

      mock_table = create_mock_table('main', 'default', 'users')
      mock_table.columns = []
      mock_table.partitioning = []
      client.tables.get.return_value = mock_table
      mock_client.return_value = client

      load_uc_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['describe_uc_table']
      result = tool.fn('main.default.users')

      assert_success_response(result)
      assert result['table']['name'] == 'users'

  @pytest.mark.unit
  def test_list_uc_schemas(self, mcp_server, mock_env_vars):
    """Test listing schemas in a catalog."""
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      client = Mock()

      # Mock schemas
      from tests.utils import create_mock_schema

      schemas = [create_mock_schema('main', 'default'), create_mock_schema('main', 'bronze')]
      client.schemas.list.return_value = schemas
      mock_client.return_value = client

      load_uc_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_uc_schemas']
      result = tool.fn('main')

      assert_success_response(result)
      assert result['count'] == 2
      assert len(result['schemas']) == 2
      assert result['schemas'][0]['name'] == 'default'

  @pytest.mark.unit
  def test_list_uc_tables(self, mcp_server, mock_env_vars):
    """Test listing tables in a schema."""
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      client = Mock()

      # Mock tables
      from tests.utils import create_mock_table

      tables = [
        create_mock_table('main', 'default', 'users'),
        create_mock_table('main', 'default', 'orders'),
      ]
      client.tables.list.return_value = tables
      mock_client.return_value = client

      load_uc_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_uc_tables']
      result = tool.fn('main', 'default')

      assert_success_response(result)
      assert result['count'] == 2
      assert len(result['tables']) == 2
      assert result['tables'][0]['name'] == 'users'
      assert result['tables'][1]['name'] == 'orders'

  @pytest.mark.unit
  def test_catalog_operations(self, mcp_server, mock_env_vars):
    """Test catalog listing and description."""
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      client = mock_workspace_client()

      # Setup comprehensive catalog data
      catalog_data = mock_catalog_list()
      catalogs = []
      for cat in catalog_data:
        mock_cat = Mock()
        for key, value in cat.items():
          setattr(mock_cat, key, value)
        # Add required attributes for catalog tools
        mock_cat.catalog_type = cat.get('type', 'UNITY_CATALOG')
        mock_cat.comment = f'Test catalog {cat["name"]}'
        mock_cat.owner = 'test@example.com'
        mock_cat.created_at = 1234567890
        mock_cat.updated_at = 1234567890
        mock_cat.properties = {'environment': 'test'}
        mock_cat.metastore_id = 'metastore-123'
        catalogs.append(mock_cat)

      client.catalogs.list.return_value = catalogs
      client.catalogs.get.side_effect = lambda name: next(
        (c for c in catalogs if c.name == name), None
      )

      # Setup schemas for catalog describe operation
      from tests.utils import create_mock_schema

      schemas = [create_mock_schema('main', 'default'), create_mock_schema('main', 'bronze')]
      # Add required attributes for schema objects
      for schema in schemas:
        schema.comment = f'Test schema {schema.name}'
        schema.owner = 'test@example.com'
        schema.created_at = 1234567890
        schema.updated_at = 1234567890
        schema.properties = {'environment': 'test'}

      client.schemas.list.return_value = schemas
      mock_client.return_value = client

      load_uc_tools(mcp_server)

      # Test catalog listing
      list_tool = mcp_server._tool_manager._tools['list_uc_catalogs']
      list_result = list_tool.fn()

      assert_success_response(list_result)
      assert list_result['count'] == 2
      assert any(cat['name'] == 'main' for cat in list_result['catalogs'])
      assert any(cat['name'] == 'test' for cat in list_result['catalogs'])

      # Test catalog description
      describe_tool = mcp_server._tool_manager._tools['describe_uc_catalog']
      describe_result = describe_tool.fn('main')

      assert_success_response(describe_result)
      assert describe_result['catalog']['name'] == 'main'

  @pytest.mark.unit
  def test_schema_operations(self, mcp_server, mock_env_vars):
    """Test schema operations within catalogs."""
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      client = mock_workspace_client()

      # Setup schemas with comprehensive data
      from tests.utils import create_mock_schema

      schemas = [
        create_mock_schema('main', 'default'),
        create_mock_schema('main', 'bronze'),
        create_mock_schema('main', 'silver'),
        create_mock_schema('main', 'gold'),
      ]

      # Add additional schema properties
      for schema in schemas:
        schema.owner = 'test@example.com'
        schema.comment = f'Test schema {schema.name}'
        schema.properties = {'environment': 'test'}

      client.schemas.list.return_value = schemas
      client.schemas.get.side_effect = lambda full_name: next(
        (s for s in schemas if f'{s.catalog_name}.{s.name}' == full_name), None
      )

      # Setup tables for schema describe operation
      from tests.utils import create_mock_table

      tables = [create_mock_table('main', 'default', 'test_table')]
      client.tables.list.return_value = tables

      mock_client.return_value = client

      load_uc_tools(mcp_server)

      # Test schema description with detailed information
      describe_tool = mcp_server._tool_manager._tools['describe_uc_schema']
      result = describe_tool.fn('main', 'default')

      assert_success_response(result)
      assert result['schema']['name'] == 'default'
      assert result['schema']['owner'] == 'test@example.com'

  @pytest.mark.unit
  def test_table_operations(self, mcp_server, mock_env_vars):
    """Test table listing and metadata."""
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      client = mock_workspace_client()

      # Setup tables with comprehensive metadata
      from tests.utils import create_mock_table

      tables = [
        create_mock_table('main', 'default', 'users'),
        create_mock_table('main', 'default', 'orders'),
        create_mock_table('main', 'default', 'products'),
      ]

      # Add table metadata
      for i, table in enumerate(tables):
        table.owner = 'test@example.com'
        table.comment = f'Test table {table.name}'
        table.table_type = 'MANAGED' if i % 2 == 0 else 'EXTERNAL'
        table.data_source_format = 'DELTA'
        table.location = f's3://bucket/{table.name}/' if table.table_type == 'EXTERNAL' else None
        table.columns = [
          Mock(name='id', type_text='BIGINT', nullable=False),
          Mock(name='name', type_text='STRING', nullable=True),
        ]

      client.tables.list.return_value = tables
      client.tables.get.side_effect = lambda name: next(
        (t for t in tables if t.full_name == name), None
      )
      mock_client.return_value = client

      load_uc_tools(mcp_server)

      # Test table listing
      list_tool = mcp_server._tool_manager._tools['list_uc_tables']
      list_result = list_tool.fn('main', 'default')

      assert_success_response(list_result)
      assert list_result['count'] == 3
      assert len(list_result['tables']) == 3

      # Test table description with metadata
      describe_tool = mcp_server._tool_manager._tools['describe_uc_table']
      describe_result = describe_tool.fn('main.default.users')

      assert_success_response(describe_result)
      assert describe_result['table']['name'] == 'users'
      assert describe_result['table']['table_type'] == 'MANAGED'

  @pytest.mark.unit
  def test_permission_error_scenarios(self, mcp_server, mock_env_vars):
    """Test permission error scenarios."""
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      from databricks.sdk.errors import PermissionDenied

      client = mock_workspace_client()
      client.catalogs.list.side_effect = PermissionDenied('Access denied to catalogs')
      mock_client.return_value = client

      load_uc_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_uc_catalogs']
      result = tool.fn()

      assert_error_response(result)
      assert 'permission' in result['error'].lower() or 'access denied' in result['error'].lower()

  @pytest.mark.unit
  def test_special_character_handling(self, mcp_server, mock_env_vars):
    """Test special character handling in names."""
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      client = mock_workspace_client()

      # Create table with special characters in name
      special_table = Mock()
      special_table.catalog_name = 'main'
      special_table.schema_name = 'default'
      special_table.name = 'table-with-dashes_and_underscores'
      special_table.full_name = 'main.default.table-with-dashes_and_underscores'
      special_table.table_type = 'MANAGED'
      special_table.data_source_format = 'DELTA'
      special_table.comment = 'Test table with special characters'
      special_table.owner = 'test@example.com'
      special_table.created_at = 1234567890
      special_table.updated_at = 1234567890
      special_table.properties = {'test': 'value'}
      special_table.columns = []
      special_table.partitioning = []
      special_table.storage_location = None

      client.tables.get.return_value = special_table
      mock_client.return_value = client

      load_uc_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['describe_uc_table']
      result = tool.fn('main.default.table-with-dashes_and_underscores')

      assert_success_response(result)
      assert result['table']['name'] == 'table-with-dashes_and_underscores'

  @pytest.mark.unit
  def test_volume_operations(self, mcp_server, mock_env_vars):
    """Test volume operations."""
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      from tests.mock_factory import mock_volume

      client = mock_workspace_client()

      # Setup volume data
      volume_data = mock_volume()
      mock_vol = Mock()
      for key, value in volume_data.items():
        setattr(mock_vol, key, value)

      client.volumes.list.return_value = [mock_vol]
      client.volumes.get.return_value = mock_vol
      mock_client.return_value = client

      load_uc_tools(mcp_server)

      # Test volume listing
      list_tool = mcp_server._tool_manager._tools['list_uc_volumes']
      list_result = list_tool.fn('main', 'default')

      assert_success_response(list_result)
      assert len(list_result['volumes']) == 1
      assert list_result['volumes'][0]['name'] == 'test-volume'

      # Test volume description
      describe_tool = mcp_server._tool_manager._tools['describe_uc_volume']
      describe_result = describe_tool.fn('main.default.test-volume')

      assert_success_response(describe_result)
      assert describe_result['volume']['name'] == 'test-volume'
      assert describe_result['volume']['volume_type'] == 'EXTERNAL'

  @pytest.mark.unit
  def test_function_operations(self, mcp_server, mock_env_vars):
    """Test function operations."""
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      client = mock_workspace_client()

      # Setup function data
      mock_function = Mock()
      mock_function.name = 'test_function'
      mock_function.catalog_name = 'main'
      mock_function.schema_name = 'default'
      mock_function.full_name = 'main.default.test_function'
      mock_function.parameters = [
        Mock(name='param1', type_text='STRING'),
        Mock(name='param2', type_text='INT'),
      ]
      mock_function.function_type = 'SQL'
      mock_function.comment = 'Test function'
      mock_function.owner = 'test@example.com'
      mock_function.created_at = 1234567890
      mock_function.updated_at = 1234567890
      mock_function.properties = {'language': 'sql'}

      client.functions.list.return_value = [mock_function]
      client.functions.get.return_value = mock_function
      mock_client.return_value = client

      load_uc_tools(mcp_server)

      # Test function listing
      list_tool = mcp_server._tool_manager._tools['list_uc_functions']
      list_result = list_tool.fn('main', 'default')

      assert_success_response(list_result)
      assert len(list_result['functions']) == 1
      assert list_result['functions'][0]['name'] == 'test_function'

      # Test function description
      describe_tool = mcp_server._tool_manager._tools['describe_uc_function']
      describe_result = describe_tool.fn('main.default.test_function')

      assert_success_response(describe_result)
      assert describe_result['function']['name'] == 'test_function'
      assert len(describe_result['function']['parameters']) == 2


class TestUnityCatalogErrorScenarios:
  """Test Unity Catalog error handling across different failure scenarios."""

  @pytest.mark.unit
  def test_network_failure_handling(self, mcp_server, mock_env_vars):
    """Test network timeout and connection error handling."""
    from tests.utils import ERROR_SCENARIOS, simulate_databricks_error

    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      # Test network timeout
      mock_client.side_effect = simulate_databricks_error(
        next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Network timeout'), 'Network timeout'
      )

      load_uc_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_uc_catalogs']
      result = tool.fn()

      assert_error_response(result)
      assert 'timeout' in result['error'].lower() or 'network' in result['error'].lower()

  @pytest.mark.unit
  def test_authentication_errors(self, mcp_server, mock_env_vars):
    """Test authentication and authorization error handling."""
    from tests.utils import ERROR_SCENARIOS, simulate_databricks_error

    # Test authentication failure
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      mock_client.side_effect = simulate_databricks_error(
        next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Authentication failed'),
        'Authentication failed',
      )

      load_uc_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['describe_uc_catalog']
      result = tool.fn('main')

      assert_error_response(result)
      assert (
        'access denied' in result['error'].lower() or 'authentication' in result['error'].lower()
      )

    # Test permission denied on specific resource
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      mock_client.return_value.schemas.list.side_effect = simulate_databricks_error(
        next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Permission denied'),
        'Permission denied',
      )

      load_uc_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_uc_schemas']
      result = tool.fn('restricted_catalog')

      assert_error_response(result)
      assert 'access denied' in result['error'].lower() or 'permission' in result['error'].lower()

  @pytest.mark.unit
  def test_rate_limiting_responses(self, mcp_server, mock_env_vars):
    """Test rate limiting error handling."""
    from tests.utils import ERROR_SCENARIOS, simulate_databricks_error

    # Test API rate limiting
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      mock_client.return_value.tables.list.side_effect = simulate_databricks_error(
        next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Rate limiting'), 'Rate limiting'
      )

      load_uc_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['list_uc_tables']
      result = tool.fn('main', 'default')

      assert_error_response(result)
      assert (
        'rate limit' in result['error'].lower() or 'too many requests' in result['error'].lower()
      )

    # Test request limit exceeded
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      mock_client.return_value.catalogs.get.side_effect = simulate_databricks_error(
        next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Request limit exceeded'),
        'Request limit exceeded',
      )

      load_uc_tools(mcp_server)
      tool = mcp_server._tool_manager._tools['describe_uc_catalog']
      result = tool.fn('busy_catalog')

      assert_error_response(result)
      assert 'rate limit' in result['error'].lower() or 'limit exceeded' in result['error'].lower()

  @pytest.mark.unit
  def test_malformed_input_handling(self, mcp_server, mock_env_vars):
    """Test malformed input parameter handling."""
    from tests.utils import ERROR_SCENARIOS, simulate_databricks_error

    load_uc_tools(mcp_server)

    # Test invalid table name format
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      mock_client.return_value = Mock()

      table_tool = mcp_server._tool_manager._tools['describe_uc_table']

      # Test various malformed table names
      malformed_inputs = [
        'just-a-name',  # Missing catalog.schema
        'catalog.schema',  # Missing table name
        'too.many.parts.here.invalid',  # Too many parts
        '',  # Empty string
        'catalog..table',  # Empty schema
        '.schema.table',  # Empty catalog
      ]

      for malformed_input in malformed_inputs:
        result = table_tool.fn(malformed_input)
        assert_error_response(result)
        assert (
          'format' in result['error'].lower()
          or 'table name must be' in result['error'].lower()
          or 'mock' in result['error'].lower()
        )  # Handle mock iteration errors

    # Test invalid parameter types
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      mock_client.return_value.schemas.get.side_effect = simulate_databricks_error(
        next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Invalid parameters'),
        'Invalid parameters',
      )

      schema_tool = mcp_server._tool_manager._tools['describe_uc_schema']
      result = schema_tool.fn('invalid@catalog!name', 'invalid@schema#name')

      assert_error_response(result)
      assert 'invalid' in result['error'].lower() or 'parameter' in result['error'].lower()

  @pytest.mark.unit
  def test_resource_not_found_scenarios(self, mcp_server, mock_env_vars):
    """Test resource not found error scenarios."""
    from tests.utils import ERROR_SCENARIOS, simulate_databricks_error

    load_uc_tools(mcp_server)

    # Test catalog not found
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      mock_client.return_value.catalogs.get.side_effect = simulate_databricks_error(
        next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Resource not found'),
        'Resource not found',
      )

      catalog_tool = mcp_server._tool_manager._tools['describe_uc_catalog']
      result = catalog_tool.fn('nonexistent_catalog')

      assert_error_response(result)
      assert 'not found' in result['error'].lower() or 'resource' in result['error'].lower()

    # Test schema not found
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      mock_client.return_value.schemas.get.side_effect = simulate_databricks_error(
        next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Resource does not exist'),
        'Resource does not exist',
      )

      schema_tool = mcp_server._tool_manager._tools['describe_uc_schema']
      result = schema_tool.fn('main', 'nonexistent_schema')

      assert_error_response(result)
      assert 'not found' in result['error'].lower() or 'does not exist' in result['error'].lower()

    # Test table not found
    with patch('server.tools.unity_catalog.WorkspaceClient') as mock_client:
      mock_client.return_value.tables.get.side_effect = simulate_databricks_error(
        next(err[1] for err in ERROR_SCENARIOS if err[0] == 'Resource not found'),
        'Resource not found',
      )

      table_tool = mcp_server._tool_manager._tools['describe_uc_table']
      result = table_tool.fn('main.default.nonexistent_table')

      assert_error_response(result)
      assert 'not found' in result['error'].lower() or 'resource' in result['error'].lower()
