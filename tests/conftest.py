"""Minimal pytest configuration and fixtures."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add server to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_env_vars(monkeypatch):
  """Set test environment variables."""
  env_vars = {
    'DATABRICKS_HOST': 'https://test.cloud.databricks.com',
    'DATABRICKS_TOKEN': 'test-token-12345',
    'DATABRICKS_SQL_WAREHOUSE_ID': 'test-warehouse',
  }

  for key, value in env_vars.items():
    monkeypatch.setenv(key, value)

  return env_vars


@pytest.fixture
def mcp_server():
  """Create test MCP server instance."""
  from fastmcp import FastMCP

  return FastMCP(name='test-databricks-mcp')


@pytest.fixture
def mock_workspace_client():
  """Mock Databricks WorkspaceClient."""
  with (
    patch('server.tools.unity_catalog.WorkspaceClient') as mock_uc,
    patch('server.tools.sql_operations.WorkspaceClient') as mock_sql,
    patch('server.tools.jobs_pipelines.WorkspaceClient') as mock_jobs,
    patch('server.tools.dashboards.WorkspaceClient') as mock_dash,
    patch('server.tools.data_management.WorkspaceClient') as mock_data,
    patch('server.tools.governance.WorkspaceClient') as mock_gov,
  ):
    # Return a single mock that all patches will use
    mock_client = Mock()
    mock_uc.return_value = mock_client
    mock_sql.return_value = mock_client
    mock_jobs.return_value = mock_client
    mock_dash.return_value = mock_client
    mock_data.return_value = mock_client
    mock_gov.return_value = mock_client

    yield mock_client
