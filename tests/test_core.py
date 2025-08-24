"""Test core MCP tools."""


import pytest

from server.tools.core import load_core_tools


class TestCoreTools:
  """Test core MCP tools."""

  @pytest.mark.unit
  def test_health_check(self, mcp_server, mock_env_vars):
    """Test health check tool."""
    load_core_tools(mcp_server)

    # Test that the tool was registered
    tool = mcp_server._tool_manager._tools['health']
    result = tool.fn()

    expected_result = {
      'status': 'healthy',
      'service': 'databricks-mcp',
      'databricks_configured': True,  # Set by mock_env_vars
    }

    assert result == expected_result

  @pytest.mark.unit
  def test_core_tools_loading(self, mcp_server, mock_env_vars):
    """Test that core tools load correctly."""
    load_core_tools(mcp_server)

    # Should only have the health tool
    tools = mcp_server._tool_manager._tools
    assert 'health' in tools
    assert len(tools) == 1  # Only health tool exists
