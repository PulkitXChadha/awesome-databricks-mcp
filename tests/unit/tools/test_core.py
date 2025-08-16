"""Unit tests for core MCP tools."""

import os
from unittest.mock import patch

import pytest


@pytest.mark.unit
@pytest.mark.tools
class TestCoreTools:
  """Test core MCP tools functionality."""

  async def test_load_core_tools_registers_health_tool(self, mcp_server):
    """Test that load_core_tools registers the health tool."""
    from server.tools.core import load_core_tools

    # Load core tools
    load_core_tools(mcp_server)

    # Check that health tool is registered
    tools = await mcp_server.get_tools()
    assert 'health' in tools

  async def test_health_tool_returns_correct_structure(self, mcp_server):
    """Test health tool returns expected data structure."""
    from server.tools.core import load_core_tools

    load_core_tools(mcp_server)

    # Get the health tool function
    health_tool_info = await mcp_server.get_tool('health')
    assert health_tool_info is not None

    # Call the tool function (accessing the actual function)
    health_tool = health_tool_info.fn
    result = health_tool()

    # Check structure
    assert isinstance(result, dict)
    assert 'status' in result
    assert 'service' in result
    assert 'databricks_configured' in result

    # Check values
    assert result['status'] == 'healthy'
    assert result['service'] == 'databricks-mcp'
    assert isinstance(result['databricks_configured'], bool)

  def test_health_tool_with_databricks_host_set(self, mcp_server, mock_environment):
    """Test health tool when DATABRICKS_HOST is set."""
    from server.tools.core import load_core_tools

    load_core_tools(mcp_server)

    # Get health tool
    tools = mcp_server._tool_manager._tools
    assert 'health' in tools, 'Health tool not found in registered tools'
    health_tool = tools['health'].fn

    with patch.dict(os.environ, {'DATABRICKS_HOST': 'https://test.databricks.com'}):
      result = health_tool()
      assert result['databricks_configured'] is True

  def test_health_tool_without_databricks_host(self, mcp_server):
    """Test health tool when DATABRICKS_HOST is not set."""
    from server.tools.core import load_core_tools

    load_core_tools(mcp_server)

    # Get health tool
    tools = mcp_server._tool_manager._tools
    assert 'health' in tools, 'Health tool not found in registered tools'
    health_tool = tools['health'].fn

    # Ensure DATABRICKS_HOST is not set
    with patch.dict(os.environ, {}, clear=False):
      if 'DATABRICKS_HOST' in os.environ:
        del os.environ['DATABRICKS_HOST']

      result = health_tool()
      assert result['databricks_configured'] is False

  def test_health_tool_with_empty_databricks_host(self, mcp_server):
    """Test health tool when DATABRICKS_HOST is empty string."""
    from server.tools.core import load_core_tools

    load_core_tools(mcp_server)

    # Get health tool
    tools = mcp_server._tool_manager._tools
    assert 'health' in tools, 'Health tool not found in registered tools'
    health_tool = tools['health'].fn

    with patch.dict(os.environ, {'DATABRICKS_HOST': ''}):
      result = health_tool()
      assert result['databricks_configured'] is False


@pytest.mark.unit
@pytest.mark.tools
class TestHealthToolIntegration:
  """Test health tool integration with MCP server."""

  def test_health_tool_is_callable_through_mcp_server(self, mcp_server_with_tools):
    """Test that health tool can be called through MCP server interface."""
    # The tool should be registered and callable
    tools = mcp_server_with_tools._tool_manager._tools
    assert 'health' in tools, 'Health tool not found in registered tools'

    # Get the tool and call it
    health_tool = tools['health'].fn
    result = health_tool()

    assert result['status'] == 'healthy'
    assert result['service'] == 'databricks-mcp'

  def test_health_tool_has_correct_metadata(self, mcp_server):
    """Test that health tool has correct metadata and documentation."""
    from server.tools.core import load_core_tools

    load_core_tools(mcp_server)

    # Get tool info
    tools = mcp_server._tool_manager._tools
    assert 'health' in tools, 'Health tool not found in registered tools'
    health_tool_info = tools['health']

    # Check that the function has documentation
    assert health_tool_info.fn.__doc__ is not None
    assert 'health' in health_tool_info.fn.__doc__.lower()
    assert 'databricks' in health_tool_info.fn.__doc__.lower()


@pytest.mark.integration
@pytest.mark.tools
class TestCoreToolsIntegration:
  """Integration tests for core tools with actual MCP server."""

  def test_core_tools_load_without_errors(self):
    """Test that core tools can be loaded without errors."""
    from fastmcp import FastMCP

    from server.tools.core import load_core_tools

    # Create a fresh MCP server
    test_server = FastMCP(name='test-core-tools')

    # This should not raise any exceptions
    load_core_tools(test_server)

    # Verify tools were loaded
    tools = test_server._tool_manager._tools
    assert len(tools) > 0
    assert 'health' in tools

  def test_health_tool_responds_correctly_in_different_environments(self, mcp_server):
    """Test health tool responds correctly in various environment configurations."""
    from server.tools.core import load_core_tools

    load_core_tools(mcp_server)
    tools = mcp_server._tool_manager._tools
    assert 'health' in tools, 'Health tool not found in registered tools'
    health_tool = tools['health'].fn

    # Test with minimal environment
    with patch.dict(os.environ, {}, clear=True):
      result = health_tool()
      assert result['status'] == 'healthy'
      assert result['databricks_configured'] is False

    # Test with Databricks configuration
    with patch.dict(
      os.environ,
      {'DATABRICKS_HOST': 'https://test.databricks.com', 'DATABRICKS_TOKEN': 'test-token'},
    ):
      result = health_tool()
      assert result['status'] == 'healthy'
      assert result['databricks_configured'] is True
