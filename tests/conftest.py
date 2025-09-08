"""Simple pytest configuration following CLAUDE.md guidelines."""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

# Add server to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_env_vars(monkeypatch):
  """Set test environment variables."""
  monkeypatch.setenv('DATABRICKS_HOST', 'https://test.cloud.databricks.com')
  monkeypatch.setenv('DATABRICKS_TOKEN', 'test-token-12345')
  monkeypatch.setenv('DATABRICKS_SQL_WAREHOUSE_ID', 'test-warehouse')


@pytest.fixture
def mcp_server():
  """Create test MCP server instance."""
  from fastmcp import FastMCP

  return FastMCP(name='test-databricks-mcp')


@pytest.fixture
def mock_workspace_client():
  """Simple mock Databricks WorkspaceClient."""
  mock_client = Mock()

  # Basic mock setup for common operations
  mock_client.catalogs.list.return_value = []
  mock_client.schemas.list.return_value = []
  mock_client.tables.list.return_value = []
  mock_client.sql_warehouses.list.return_value = []
  mock_client.jobs.list.return_value = []
  mock_client.pipelines.list_pipelines.return_value = []

  return mock_client
