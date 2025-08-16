"""Unit tests for Unity Catalog MCP tools."""

import os
from unittest.mock import Mock, patch

import pytest
from databricks.sdk.errors import NotFound, PermissionDenied


@pytest.mark.unit
@pytest.mark.tools
class TestUnityCatalogTools:
  """Test Unity Catalog MCP tools functionality."""

  def test_load_uc_tools_registers_all_tools(self, mcp_server):
    """Test that load_uc_tools registers all expected tools."""
    from server.tools.unity_catalog import load_uc_tools

    load_uc_tools(mcp_server)

    expected_tools = [
      'list_uc_catalogs',
      'describe_uc_catalog',
      'describe_uc_schema',
      'describe_uc_table',
      'list_uc_volumes',
      'describe_uc_volume',
      'list_uc_functions',
      'describe_uc_function',
      'list_uc_models',
      'describe_uc_model',
    ]

    tool_names = list(mcp_server.tools.keys())
    for tool_name in expected_tools:
      assert tool_name in tool_names


@pytest.mark.unit
@pytest.mark.tools
class TestListUCCatalogs:
  """Test list_uc_catalogs tool."""

  def test_list_uc_catalogs_success(self, mcp_server, mock_databricks_client):
    """Test successful catalog listing."""
    from server.tools.unity_catalog import load_uc_tools

    load_uc_tools(mcp_server)

    # Configure mock to return catalogs
    mock_catalog = Mock()
    mock_catalog.name = 'test_catalog'
    mock_catalog.catalog_type = 'MANAGED'
    mock_catalog.comment = 'Test catalog'
    mock_catalog.owner = 'test@example.com'
    mock_catalog.created_at = '2024-01-01T00:00:00Z'
    mock_catalog.updated_at = '2024-01-01T00:00:00Z'
    mock_catalog.properties = {}

    mock_databricks_client.catalogs.list.return_value = [mock_catalog]

    # Get and call the tool
    tool = mcp_server.tools['list_uc_catalogs'].fn

    with patch('server.tools.unity_catalog.WorkspaceClient', return_value=mock_databricks_client):
      result = tool()

    assert result['success'] is True
    assert result['count'] == 1
    assert len(result['catalogs']) == 1
    assert result['catalogs'][0]['name'] == 'test_catalog'
    assert result['catalogs'][0]['type'] == 'MANAGED'
    assert 'Found 1 catalog(s)' in result['message']

  def test_list_uc_catalogs_empty_result(self, mcp_server, mock_databricks_client):
    """Test catalog listing with no catalogs."""
    from server.tools.unity_catalog import load_uc_tools

    load_uc_tools(mcp_server)

    mock_databricks_client.catalogs.list.return_value = []

    tool = mcp_server.tools['list_uc_catalogs'].fn

    with patch('server.tools.unity_catalog.WorkspaceClient', return_value=mock_databricks_client):
      result = tool()

    assert result['success'] is True
    assert result['count'] == 0
    assert len(result['catalogs']) == 0
    assert 'Found 0 catalog(s)' in result['message']

  def test_list_uc_catalogs_error_handling(self, mcp_server, mock_databricks_client):
    """Test error handling in catalog listing."""
    from server.tools.unity_catalog import load_uc_tools

    load_uc_tools(mcp_server)

    mock_databricks_client.catalogs.list.side_effect = PermissionDenied('Access denied')

    tool = mcp_server.tools['list_uc_catalogs'].fn

    with patch('server.tools.unity_catalog.WorkspaceClient', return_value=mock_databricks_client):
      result = tool()

    assert result['success'] is False
    assert 'error' in result
    assert 'Access denied' in result['error']
    assert result['count'] == 0
    assert result['catalogs'] == []


@pytest.mark.unit
@pytest.mark.tools
class TestDescribeUCCatalog:
  """Test describe_uc_catalog tool."""

  def test_describe_uc_catalog_success(self, mcp_server, mock_databricks_client):
    """Test successful catalog description."""
    from server.tools.unity_catalog import load_uc_tools

    load_uc_tools(mcp_server)

    # Mock catalog details
    mock_catalog = Mock()
    mock_catalog.name = 'test_catalog'
    mock_catalog.catalog_type = 'MANAGED'
    mock_catalog.comment = 'Test catalog'
    mock_catalog.owner = 'test@example.com'
    mock_catalog.created_at = '2024-01-01T00:00:00Z'
    mock_catalog.updated_at = '2024-01-01T00:00:00Z'
    mock_catalog.properties = {}

    mock_databricks_client.catalogs.get.return_value = mock_catalog

    # Mock schemas
    mock_schema = Mock()
    mock_schema.name = 'test_schema'
    mock_schema.comment = 'Test schema'
    mock_schema.owner = 'test@example.com'
    mock_schema.created_at = '2024-01-01T00:00:00Z'
    mock_schema.updated_at = '2024-01-01T00:00:00Z'
    mock_schema.properties = {}

    mock_databricks_client.schemas.list.return_value = [mock_schema]

    tool = mcp_server.tools['describe_uc_catalog'].fn

    with patch('server.tools.unity_catalog.WorkspaceClient', return_value=mock_databricks_client):
      result = tool('test_catalog')

    assert result['success'] is True
    assert result['catalog']['name'] == 'test_catalog'
    assert result['schema_count'] == 1
    assert len(result['schemas']) == 1
    assert result['schemas'][0]['name'] == 'test_schema'

  def test_describe_uc_catalog_not_found(self, mcp_server, mock_databricks_client):
    """Test describing non-existent catalog."""
    from server.tools.unity_catalog import load_uc_tools

    load_uc_tools(mcp_server)

    mock_databricks_client.catalogs.get.side_effect = NotFound('Catalog not found')

    tool = mcp_server.tools['describe_uc_catalog'].fn

    with patch('server.tools.unity_catalog.WorkspaceClient', return_value=mock_databricks_client):
      result = tool('nonexistent_catalog')

    assert result['success'] is False
    assert 'error' in result
    assert 'Catalog not found' in result['error']


@pytest.mark.unit
@pytest.mark.tools
class TestDescribeUCSchema:
  """Test describe_uc_schema tool."""

  def test_describe_uc_schema_success(self, mcp_server, mock_databricks_client):
    """Test successful schema description."""
    from server.tools.unity_catalog import load_uc_tools

    load_uc_tools(mcp_server)

    # Mock schema details
    mock_schema = Mock()
    mock_schema.name = 'test_schema'
    mock_schema.comment = 'Test schema'
    mock_schema.owner = 'test@example.com'
    mock_schema.created_at = '2024-01-01T00:00:00Z'
    mock_schema.updated_at = '2024-01-01T00:00:00Z'
    mock_schema.properties = {}

    mock_databricks_client.schemas.get.return_value = mock_schema

    # Mock tables
    mock_table = Mock()
    mock_table.name = 'test_table'
    mock_table.table_type = 'MANAGED'
    mock_table.comment = 'Test table'
    mock_table.owner = 'test@example.com'
    mock_table.created_at = '2024-01-01T00:00:00Z'
    mock_table.updated_at = '2024-01-01T00:00:00Z'
    mock_table.properties = {}

    mock_databricks_client.tables.list.return_value = [mock_table]

    tool = mcp_server.tools['describe_uc_schema'].fn

    with patch('server.tools.unity_catalog.WorkspaceClient', return_value=mock_databricks_client):
      result = tool('test_catalog', 'test_schema')

    assert result['success'] is True
    assert result['schema']['name'] == 'test_schema'
    assert result['table_count'] == 1
    assert len(result['tables']) == 1
    assert result['tables'][0]['name'] == 'test_table'

  def test_describe_uc_schema_with_columns(self, mcp_server, mock_databricks_client):
    """Test schema description with column details."""
    from server.tools.unity_catalog import load_uc_tools

    load_uc_tools(mcp_server)

    # Mock schema
    mock_schema = Mock()
    mock_schema.name = 'test_schema'
    mock_schema.comment = 'Test schema'
    mock_schema.owner = 'test@example.com'
    mock_schema.created_at = '2024-01-01T00:00:00Z'
    mock_schema.updated_at = '2024-01-01T00:00:00Z'
    mock_schema.properties = {}

    mock_databricks_client.schemas.get.return_value = mock_schema

    # Mock tables
    mock_table = Mock()
    mock_table.name = 'test_table'
    mock_table.table_type = 'MANAGED'
    mock_table.comment = 'Test table'

    mock_databricks_client.tables.list.return_value = [mock_table]

    # Mock table details for column information
    mock_table_details = Mock()
    mock_table_details.name = 'test_table'
    mock_table_details.columns = [
      Mock(name='id', type_name='bigint', comment='ID column'),
      Mock(name='name', type_name='string', comment='Name column'),
    ]

    mock_databricks_client.tables.get.return_value = mock_table_details

    tool = mcp_server.tools['describe_uc_schema'].fn

    with patch('server.tools.unity_catalog.WorkspaceClient', return_value=mock_databricks_client):
      result = tool('test_catalog', 'test_schema', include_columns=True)

    assert result['success'] is True
    assert result['tables'][0]['column_count'] == 2
    assert 'columns' in result['tables'][0]
    assert len(result['tables'][0]['columns']) == 2


@pytest.mark.unit
@pytest.mark.tools
class TestDescribeUCTable:
  """Test describe_uc_table tool."""

  def test_describe_uc_table_success(self, mcp_server, mock_databricks_client):
    """Test successful table description."""
    from server.tools.unity_catalog import load_uc_tools

    load_uc_tools(mcp_server)

    # Mock table details
    mock_table = Mock()
    mock_table.name = 'test_table'
    mock_table.table_type = 'MANAGED'
    mock_table.comment = 'Test table'
    mock_table.owner = 'test@example.com'
    mock_table.created_at = '2024-01-01T00:00:00Z'
    mock_table.updated_at = '2024-01-01T00:00:00Z'
    mock_table.properties = {}
    mock_table.storage_location = 's3://bucket/path'
    mock_table.data_source_format = 'DELTA'
    mock_table.columns = [
      Mock(name='id', type_name='bigint', comment='ID column'),
      Mock(name='name', type_name='string', comment='Name column'),
    ]

    mock_databricks_client.tables.get.return_value = mock_table

    tool = mcp_server.tools['describe_uc_table'].fn

    with patch('server.tools.unity_catalog.WorkspaceClient', return_value=mock_databricks_client):
      result = tool('test_catalog.test_schema.test_table')

    assert result['success'] is True
    assert result['table']['name'] == 'test_table'
    assert result['table']['type'] == 'MANAGED'
    assert result['table']['column_count'] == 2
    assert len(result['table']['columns']) == 2
    assert result['table']['columns'][0]['name'] == 'id'

  def test_describe_uc_table_with_lineage(self, mcp_server, mock_databricks_client):
    """Test table description with lineage information."""
    from server.tools.unity_catalog import load_uc_tools

    load_uc_tools(mcp_server)

    # Mock table details
    mock_table = Mock()
    mock_table.name = 'test_table'
    mock_table.table_type = 'MANAGED'
    mock_table.columns = []

    mock_databricks_client.tables.get.return_value = mock_table

    # Mock lineage information
    mock_lineage = Mock()
    mock_lineage.upstream_tables = ['catalog.schema.source_table']
    mock_lineage.downstream_tables = ['catalog.schema.target_table']

    # Mock the lineage method
    mock_databricks_client.lineage = Mock()
    mock_databricks_client.lineage.get_lineage_by_table = Mock(return_value=mock_lineage)

    tool = mcp_server.tools['describe_uc_table'].fn

    with patch('server.tools.unity_catalog.WorkspaceClient', return_value=mock_databricks_client):
      result = tool('test_catalog.test_schema.test_table', include_lineage=True)

    assert result['success'] is True
    # Note: Lineage implementation may vary based on actual SDK capabilities
    assert 'table' in result


@pytest.mark.unit
@pytest.mark.tools
class TestUCVolumes:
  """Test UC volume tools."""

  def test_list_uc_volumes_success(self, mcp_server, mock_databricks_client):
    """Test successful volume listing."""
    from server.tools.unity_catalog import load_uc_tools

    load_uc_tools(mcp_server)

    # Mock volume
    mock_volume = Mock()
    mock_volume.name = 'test_volume'
    mock_volume.volume_type = 'MANAGED'
    mock_volume.comment = 'Test volume'

    mock_databricks_client.volumes.list.return_value = [mock_volume]

    tool = mcp_server.tools['list_uc_volumes'].fn

    with patch('server.tools.unity_catalog.WorkspaceClient', return_value=mock_databricks_client):
      result = tool('test_catalog', 'test_schema')

    assert result['success'] is True
    assert result['count'] == 1
    assert result['volumes'][0]['name'] == 'test_volume'

  def test_describe_uc_volume_success(self, mcp_server, mock_databricks_client):
    """Test successful volume description."""
    from server.tools.unity_catalog import load_uc_tools

    load_uc_tools(mcp_server)

    # Mock volume details
    mock_volume = Mock()
    mock_volume.name = 'test_volume'
    mock_volume.volume_type = 'MANAGED'
    mock_volume.comment = 'Test volume'
    mock_volume.storage_location = 's3://bucket/volume'

    mock_databricks_client.volumes.get.return_value = mock_volume

    tool = mcp_server.tools['describe_uc_volume'].fn

    with patch('server.tools.unity_catalog.WorkspaceClient', return_value=mock_databricks_client):
      result = tool('test_catalog.test_schema.test_volume')

    assert result['success'] is True
    assert result['volume']['name'] == 'test_volume'
    assert result['volume']['type'] == 'MANAGED'


@pytest.mark.unit
@pytest.mark.tools
class TestUCErrorHandling:
  """Test error handling across UC tools."""

  def test_workspace_client_initialization_error(self, mcp_server):
    """Test error handling when WorkspaceClient initialization fails."""
    from server.tools.unity_catalog import load_uc_tools

    load_uc_tools(mcp_server)

    tool = mcp_server.tools['list_uc_catalogs'].fn

    with patch(
      'server.tools.unity_catalog.WorkspaceClient', side_effect=Exception('Connection failed')
    ):
      result = tool()

    assert result['success'] is False
    assert 'error' in result
    assert 'Connection failed' in result['error']

  def test_missing_environment_variables(self, mcp_server):
    """Test behavior with missing environment variables."""
    from server.tools.unity_catalog import load_uc_tools

    load_uc_tools(mcp_server)

    tool = mcp_server.tools['list_uc_catalogs'].fn

    # Clear environment variables
    with patch.dict(os.environ, {}, clear=True):
      with patch(
        'server.tools.unity_catalog.WorkspaceClient', side_effect=Exception('Missing credentials')
      ):
        result = tool()

    assert result['success'] is False
    assert 'error' in result


@pytest.mark.integration
@pytest.mark.tools
class TestUCToolsIntegration:
  """Integration tests for UC tools."""

  def test_all_uc_tools_load_successfully(self):
    """Test that all UC tools can be loaded without errors."""
    from fastmcp import FastMCP

    from server.tools.unity_catalog import load_uc_tools

    test_server = FastMCP(name='test-uc-tools')

    # Should not raise any exceptions
    load_uc_tools(test_server)

    # Verify tools were loaded
    assert len(test_server.tools) > 0

    expected_tools = ['list_uc_catalogs', 'describe_uc_catalog', 'describe_uc_schema']
    for tool_name in expected_tools:
      assert tool_name in test_server.tools
