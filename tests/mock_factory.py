"""Simple mock data functions for testing."""

from unittest.mock import Mock

from tests.utils import load_mock_response


def mock_catalog_list():
  """Simple mock data for catalog listing."""
  return [{'name': 'main', 'type': 'HIVE_METASTORE'}, {'name': 'test', 'type': 'UNITY_CATALOG'}]


def mock_warehouse():
  """Simple mock warehouse data."""
  return {'id': 'test-wh', 'name': 'Test Warehouse', 'state': 'RUNNING'}


def mock_warehouse_list():
  """Simple mock data for warehouse listing."""
  return load_mock_response('warehouses')


def mock_job():
  """Simple mock job data."""
  return {
    'job_id': 123,
    'name': 'Test Job',
    'created_time': 1234567890,
    'creator_user_name': 'test@example.com',
  }


def mock_pipeline():
  """Simple mock pipeline data."""
  return {
    'pipeline_id': 'pipeline-123',
    'name': 'Test Pipeline',
    'state': 'IDLE',
    'creator_user_name': 'test@example.com',
    'created_time': 1234567890,
  }


def mock_cluster():
  """Simple mock cluster data."""
  return {
    'cluster_id': 'cluster-123',
    'cluster_name': 'Test Cluster',
    'state': 'RUNNING',
    'spark_version': '13.3.x-scala2.12',
    'node_type_id': 'i3.xlarge',
    'num_workers': 2,
  }


def mock_dbfs_file():
  """Simple mock DBFS file data."""
  return {
    'path': '/test/file.txt',
    'is_dir': False,
    'file_size': 1024,
    'modification_time': 1234567890,
  }


def mock_volume():
  """Simple mock volume data."""
  return {
    'name': 'test-volume',
    'catalog_name': 'main',
    'schema_name': 'default',
    'volume_type': 'EXTERNAL',
    'storage_location': 's3://bucket/volume',
    'owner': 'test@example.com',
    'created_time': 1234567890,
  }


def mock_user():
  """Simple mock user data."""
  return {
    'user_name': 'test@example.com',
    'display_name': 'Test User',
    'active': True,
    'groups': ['admins', 'users'],
  }


def mock_notebook():
  """Simple mock notebook data."""
  return {
    'path': '/Users/test@example.com/Test Notebook',
    'language': 'python',
    'created_time': 1234567890,
    'modified_time': 1234567890,
  }


def mock_workspace_client():
  """Create a basic mock workspace client."""
  client = Mock()

  # Set up minimal required attributes for basic functionality
  client.catalogs = Mock()
  client.schemas = Mock()
  client.tables = Mock()
  client.sql_warehouses = Mock()
  client.jobs = Mock()
  client.pipelines = Mock()
  client.clusters = Mock()
  client.dbfs = Mock()
  client.volumes = Mock()
  client.users = Mock()
  client.workspace = Mock()
  client.statement_execution = Mock()

  return client


def mock_error_client():
  """Create a mock client that raises connection errors."""
  client = mock_workspace_client()

  # Make all operations fail with connection error
  error = Exception('Connection failed')
  client.catalogs.list.side_effect = error
  client.schemas.list.side_effect = error
  client.tables.list.side_effect = error
  client.sql_warehouses.list.side_effect = error

  return client


def mock_empty_client():
  """Create a mock client with no data."""
  client = mock_workspace_client()

  # Return empty lists for all operations
  client.catalogs.list.return_value = []
  client.schemas.list.return_value = []
  client.tables.list.return_value = []
  client.sql_warehouses.list.return_value = []
  client.jobs.list.return_value = []
  client.pipelines.list_pipelines.return_value = []

  return client
