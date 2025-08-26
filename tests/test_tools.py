"""Test MCP tool integration and loading."""

import json
from pathlib import Path

import pytest

# Import tool loading functions
from server.tools import load_tools
from server.tools.core import load_core_tools
from server.tools.dashboards import load_dashboard_tools
from server.tools.data_management import load_data_tools
from server.tools.governance import load_governance_tools
from server.tools.jobs_pipelines import load_job_tools
from server.tools.sql_operations import load_sql_tools
from server.tools.unity_catalog import load_uc_tools


@pytest.fixture
def mock_responses():
  """Load mock responses from fixtures file."""
  fixtures_path = Path(__file__).parent / 'fixtures' / 'mock_responses.json'
  with open(fixtures_path, 'r') as f:
    return json.load(f)


class TestToolIntegration:
  """Test tool integration and loading."""

  @pytest.mark.integration
  def test_all_tools_load_successfully(self, mcp_server, mock_env_vars):
    """Test that all tools load without errors."""
    # This should not raise any exceptions
    load_tools(mcp_server)

    # Verify tools were loaded by checking tool manager directly
    tools = mcp_server._tool_manager._tools
    assert len(tools) > 0

    # Check that key tool categories are present
    tool_names = list(tools.keys())
    assert 'health' in tool_names  # Core tools
    assert 'list_uc_catalogs' in tool_names  # Unity Catalog tools
    assert 'list_warehouses' in tool_names  # SQL tools
    assert 'list_jobs' in tool_names  # Jobs tools
    assert 'list_lakeview_dashboards' in tool_names  # Dashboard tools

  @pytest.mark.integration
  def test_tool_error_handling(self, mcp_server, mock_workspace_client):
    """Test that tools handle errors gracefully."""
    # Setup mock to raise exception
    mock_workspace_client.catalogs.list.side_effect = Exception('Test error')

    # Load tools and test
    load_uc_tools(mcp_server)
    tool = mcp_server._tool_manager._tools['list_uc_catalogs']
    result = tool.fn()

    # Assert error handling
    assert result['success'] is False
    assert 'error' in result
    assert result['catalogs'] == []
    assert result['count'] == 0

  @pytest.mark.integration
  def test_core_tools_loading(self, mcp_server, mock_env_vars):
    """Test core tools loading."""
    load_core_tools(mcp_server)

    tools = mcp_server._tool_manager._tools
    # Only health tool is currently implemented in core
    core_tool_names = ['health']

    for tool_name in core_tool_names:
      assert tool_name in tools, f'Core tool {tool_name} not loaded'

  @pytest.mark.integration
  def test_unity_catalog_tools_loading(self, mcp_server, mock_env_vars):
    """Test Unity Catalog tools loading."""
    load_uc_tools(mcp_server)

    tools = mcp_server._tool_manager._tools
    # Check for actual UC tools that are loaded
    uc_tool_names = ['list_uc_catalogs', 'describe_uc_catalog', 'describe_uc_schema']

    for tool_name in uc_tool_names:
      assert tool_name in tools, f'Unity Catalog tool {tool_name} not loaded'

  @pytest.mark.integration
  def test_sql_tools_loading(self, mcp_server, mock_env_vars):
    """Test SQL tools loading."""
    load_sql_tools(mcp_server)

    tools = mcp_server._tool_manager._tools
    # Check for actual SQL tools that are loaded
    sql_tool_names = ['list_warehouses', 'execute_dbsql', 'get_sql_warehouse']

    for tool_name in sql_tool_names:
      assert tool_name in tools, f'SQL tool {tool_name} not loaded'

  @pytest.mark.integration
  def test_jobs_tools_loading(self, mcp_server, mock_env_vars):
    """Test Jobs and Pipelines tools loading."""
    load_job_tools(mcp_server)

    tools = mcp_server._tool_manager._tools
    # Check for actual jobs tools that are loaded
    jobs_tool_names = ['list_jobs', 'list_pipelines', 'submit_job_run']

    for tool_name in jobs_tool_names:
      assert tool_name in tools, f'Jobs tool {tool_name} not loaded'

  @pytest.mark.integration
  def test_dashboard_tools_loading(self, mcp_server, mock_env_vars):
    """Test Dashboard tools loading."""
    load_dashboard_tools(mcp_server)

    tools = mcp_server._tool_manager._tools
    dashboard_tool_names = ['list_lakeview_dashboards']

    for tool_name in dashboard_tool_names:
      assert tool_name in tools, f'Dashboard tool {tool_name} not loaded'

  @pytest.mark.integration
  def test_data_management_tools_loading(self, mcp_server, mock_env_vars):
    """Test Data Management tools loading."""
    # Note: data_management tools are commented out in main load_tools
    # This test will fail until they are enabled
    load_data_tools(mcp_server)

    tools = mcp_server._tool_manager._tools
    # Check for actual data management tools that are loaded
    data_tool_names = ['list_dbfs_files', 'get_dbfs_file_info', 'list_external_locations']

    for tool_name in data_tool_names:
      assert tool_name in tools, f'Data Management tool {tool_name} not loaded'

  @pytest.mark.integration
  def test_governance_tools_loading(self, mcp_server, mock_env_vars):
    """Test Governance tools loading."""
    # Note: governance tools are commented out in main load_tools
    # This test will fail until they are enabled
    load_governance_tools(mcp_server)

    tools = mcp_server._tool_manager._tools
    # Check for actual governance tools that are loaded
    governance_tool_names = ['list_governance_rules', 'list_audit_logs', 'search_catalog']

    for tool_name in governance_tool_names:
      assert tool_name in tools, f'Governance tool {tool_name} not loaded'

  @pytest.mark.integration
  def test_tool_functionality_integration(self, mcp_server, mock_env_vars):
    """Test that tools can be called and return expected structure."""
    # Load all tools
    load_tools(mcp_server)

    # Test health tool (doesn't require external calls)
    health_tool = mcp_server._tool_manager._tools['health']
    health_result = health_tool.fn()

    assert health_result['status'] == 'healthy'
    assert health_result['service'] == 'databricks-mcp'
    assert 'databricks_configured' in health_result

  @pytest.mark.integration
  def test_tool_registration_consistency(self, mcp_server, mock_env_vars):
    """Test that tool registration is consistent across loads."""
    # Load tools twice
    load_tools(mcp_server)
    first_tools = mcp_server._tool_manager._tools
    first_count = len(first_tools)

    # Clear and reload
    mcp_server._tool_manager._tools.clear()
    load_tools(mcp_server)
    second_tools = mcp_server._tool_manager._tools
    second_count = len(second_tools)

    # Should have same number of tools
    assert first_count == second_count, 'Tool count should be consistent'

    # Should have same tool names
    first_names = set(first_tools.keys())
    second_names = set(second_tools.keys())
    assert first_names == second_names, 'Tool names should be consistent'
