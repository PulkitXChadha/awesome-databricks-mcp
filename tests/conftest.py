"""Test configuration and fixtures for Databricks MCP Server tests."""

import asyncio
import os
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest
from databricks.sdk import WorkspaceClient
from fastapi.testclient import TestClient
from fastmcp import FastMCP

# Set test environment variables
os.environ['DATABRICKS_HOST'] = 'https://test.cloud.databricks.com'
os.environ['DATABRICKS_TOKEN'] = 'test-token'
os.environ['TESTING'] = 'true'


@pytest.fixture(scope='session')
def event_loop():
  """Create an instance of the default event loop for the test session."""
  loop = asyncio.get_event_loop_policy().new_event_loop()
  yield loop
  loop.close()


@pytest.fixture
def mock_databricks_client():
  """Mock Databricks WorkspaceClient for testing."""
  with patch('databricks.sdk.WorkspaceClient') as mock_client:
    # Mock the client instance
    client = Mock(spec=WorkspaceClient)
    mock_client.return_value = client

    # Mock user info
    client.current_user.me.return_value = Mock(
      user_name='test@example.com', display_name='Test User'
    )

    # Mock catalogs
    client.catalogs.list.return_value = [Mock(name='test_catalog', comment='Test catalog')]
    client.catalogs.get.return_value = Mock(name='test_catalog', comment='Test catalog')

    # Mock schemas
    client.schemas.list.return_value = [Mock(name='test_schema', comment='Test schema')]
    client.schemas.get.return_value = Mock(name='test_schema', comment='Test schema')

    # Mock tables
    client.tables.list.return_value = [Mock(name='test_table', comment='Test table')]
    client.tables.get.return_value = Mock(
      name='test_table',
      comment='Test table',
      columns=[Mock(name='id', type_name='bigint'), Mock(name='name', type_name='string')],
    )

    # Mock SQL warehouses
    client.warehouses.list.return_value = [
      Mock(id='test-warehouse', name='Test Warehouse', state='RUNNING')
    ]
    client.warehouses.get.return_value = Mock(
      id='test-warehouse', name='Test Warehouse', state='RUNNING'
    )

    # Mock statement execution
    client.statement_execution.execute_statement.return_value = Mock(
      statement_id='test-statement-id'
    )
    client.statement_execution.get_statement.return_value = Mock(
      statement_id='test-statement-id',
      status=Mock(state='SUCCEEDED'),
      result=Mock(
        data_array=[['1', 'test'], ['2', 'test2']],
        schema=Mock(
          columns=[Mock(name='id', type_name='bigint'), Mock(name='name', type_name='string')]
        ),
      ),
    )

    yield client


@pytest.fixture
def mcp_server():
  """Create a test MCP server instance."""
  server = FastMCP(name='test-databricks-mcp')
  return server


@pytest.fixture
def mcp_server_with_tools(mcp_server, mock_databricks_client):
  """Create MCP server with all tools loaded."""
  # Import and load tools
  from server.tools import load_tools

  load_tools(mcp_server)
  return mcp_server


@pytest.fixture
def fastapi_app():
  """Create FastAPI app for testing."""
  # We need to mock the MCP server creation to avoid conflicts
  with patch('server.app.mcp_server') as mock_mcp:
    mock_mcp.name = 'test-databricks-mcp'
    mock_mcp.tools = {}
    mock_mcp.prompts = {}

    from server.app import app

    yield app


@pytest.fixture
def test_client(fastapi_app):
  """Create test client for FastAPI app."""
  return TestClient(fastapi_app)


@pytest.fixture
def sample_catalog_data():
  """Sample Unity Catalog data for testing."""
  return {
    'catalogs': [
      {
        'name': 'test_catalog',
        'comment': 'Test catalog for unit tests',
        'schemas': [
          {
            'name': 'test_schema',
            'comment': 'Test schema',
            'tables': [
              {
                'name': 'test_table',
                'comment': 'Test table',
                'columns': [{'name': 'id', 'type': 'bigint'}, {'name': 'name', 'type': 'string'}],
              }
            ],
          }
        ],
      }
    ]
  }


@pytest.fixture
def sample_sql_query_result():
  """Sample SQL query result for testing."""
  return {
    'statement_id': 'test-statement-id',
    'status': 'SUCCEEDED',
    'data': [{'id': 1, 'name': 'test'}, {'id': 2, 'name': 'test2'}],
    'schema': [{'name': 'id', 'type': 'bigint'}, {'name': 'name', 'type': 'string'}],
  }


@pytest.fixture
def mock_environment(monkeypatch):
  """Set up mock environment variables for testing."""
  test_env = {
    'DATABRICKS_HOST': 'https://test.cloud.databricks.com',
    'DATABRICKS_TOKEN': 'test-token',
    'TESTING': 'true',
  }

  for key, value in test_env.items():
    monkeypatch.setenv(key, value)

  return test_env


@pytest.fixture
def mock_file_system(tmp_path):
  """Create temporary file system for testing."""
  # Create test files
  test_config = tmp_path / 'config.yaml'
  test_config.write_text('servername: test-databricks-mcp\n')

  test_env = tmp_path / '.env.local'
  test_env.write_text(
    'DATABRICKS_HOST=https://test.cloud.databricks.com\nDATABRICKS_TOKEN=test-token\n'
  )

  return tmp_path


@pytest.fixture
def mock_mcp_proxy():
  """Mock MCP proxy for testing."""
  proxy = Mock()
  proxy.start.return_value = None
  proxy.stop.return_value = None
  proxy.is_running = True
  proxy.get_tools.return_value = ['list_uc_catalogs', 'execute_dbsql']
  proxy.call_tool.return_value = {'success': True, 'result': 'test'}
  return proxy


class MockResponse:
  """Mock HTTP response for testing."""

  def __init__(self, status_code: int = 200, json_data: Dict[str, Any] = None):
    self.status_code = status_code
    self._json_data = json_data or {}

  def json(self):
    return self._json_data

  def raise_for_status(self):
    if self.status_code >= 400:
      raise Exception(f'HTTP {self.status_code}')


@pytest.fixture
def mock_requests():
  """Mock requests library for HTTP testing."""
  with (
    patch('requests.get') as mock_get,
    patch('requests.post') as mock_post,
    patch('requests.put') as mock_put,
    patch('requests.delete') as mock_delete,
  ):
    # Default successful responses
    mock_get.return_value = MockResponse(200, {'status': 'ok'})
    mock_post.return_value = MockResponse(201, {'created': True})
    mock_put.return_value = MockResponse(200, {'updated': True})
    mock_delete.return_value = MockResponse(204)

    yield {'get': mock_get, 'post': mock_post, 'put': mock_put, 'delete': mock_delete}


@pytest.fixture(autouse=True)
def setup_test_logging():
  """Configure logging for tests."""
  import logging

  logging.getLogger('databricks').setLevel(logging.WARNING)
  logging.getLogger('httpx').setLevel(logging.WARNING)
  logging.getLogger('uvicorn').setLevel(logging.WARNING)
