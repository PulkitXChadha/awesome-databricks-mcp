"""Core MCP tools for Databricks operations."""

import os


def load_core_tools(mcp_server):
  """Register core MCP tools with the server.

  Args:
      mcp_server: The FastMCP server instance to register tools with
  """

  @mcp_server.tool
  def health() -> dict:
    """Check the health of the MCP server and Databricks connection."""
    return {
      'status': 'healthy',
      'service': 'databricks-mcp',
      'databricks_configured': bool(os.environ.get('DATABRICKS_HOST')),
    }
