"""Test utilities and mock factory."""

import pytest

from tests.mock_factory import (
  mock_catalog_list,
  mock_empty_client,
  mock_error_client,
  mock_warehouse_list,
  mock_workspace_client,
)
from tests.utils import (
  create_mock_catalog,
  create_mock_schema,
  create_mock_table,
  load_mock_response,
)


class TestPhase2Utils:
  """Test Phase 2 utility functions."""

  def test_load_mock_response_flat(self):
    """Test loading flat mock responses."""
    catalogs = load_mock_response('catalogs')
    assert isinstance(catalogs, list)
    assert len(catalogs) == 2
    assert catalogs[0]['name'] == 'main'
    assert catalogs[1]['name'] == 'dev'

  def test_create_mock_catalog(self):
    """Test creating mock catalog objects."""
    catalog = create_mock_catalog('test_cat')
    assert catalog.name == 'test_cat'
    assert catalog.owner == 'test@example.com'
    assert catalog.created_at == 1234567890

  def test_create_mock_schema(self):
    """Test creating mock schema objects."""
    schema = create_mock_schema('main', 'bronze')
    assert schema.catalog_name == 'main'
    assert schema.name == 'bronze'
    assert schema.full_name == 'main.bronze'

  def test_create_mock_table(self):
    """Test creating mock table objects."""
    table = create_mock_table('main', 'bronze', 'users')
    assert table.catalog_name == 'main'
    assert table.schema_name == 'bronze'
    assert table.name == 'users'
    assert table.full_name == 'main.bronze.users'
    assert table.table_type == 'MANAGED'
    assert table.data_source_format == 'DELTA'


class TestSimplifiedMockFactory:
  """Test simplified mock factory functionality."""

  def test_mock_catalog_list(self):
    """Test mock catalog data."""
    catalogs = mock_catalog_list()
    assert isinstance(catalogs, list)
    assert len(catalogs) == 2
    assert catalogs[0]['name'] == 'main'
    assert catalogs[1]['name'] == 'test'

  def test_mock_workspace_client(self):
    """Test creating basic mock workspace client."""
    client = mock_workspace_client()
    assert hasattr(client, 'catalogs')
    assert hasattr(client, 'sql_warehouses')
    assert hasattr(client, 'jobs')
    assert hasattr(client, 'pipelines')

  def test_mock_error_client(self):
    """Test creating mock client that raises errors."""
    client = mock_error_client()

    with pytest.raises(Exception, match='Connection failed'):
      client.catalogs.list()

    with pytest.raises(Exception, match='Connection failed'):
      client.schemas.list()

  def test_mock_empty_client(self):
    """Test creating mock client with no data."""
    client = mock_empty_client()
    assert client.catalogs.list.return_value == []
    assert client.schemas.list.return_value == []
    assert client.tables.list.return_value == []
    assert client.sql_warehouses.list.return_value == []

  def test_mock_warehouse_list(self):
    """Test mock warehouse data."""
    warehouses = mock_warehouse_list()
    assert isinstance(warehouses, list)
    assert len(warehouses) >= 0
