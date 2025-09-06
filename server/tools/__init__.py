"""MCP Tools for Databricks operations."""

from .core import load_core_tools

# from .data_management import load_data_tools
from .jobs_pipelines import load_job_tools
from .lakeview_dashboard import load_dashboard_tools
from .sql_operations import load_sql_tools
from .unity_catalog import load_uc_tools

# Commented out - widgets.py has duplicate tools that conflict with dashboards.py
# The dashboards.py module already includes comprehensive widget creation tools
# from .widgets import load_widget_tools

# from .governance import load_governance_tools


def load_tools(mcp_server):
  """Register all MCP tools with the server.

  Args:
      mcp_server: The FastMCP server instance to register tools with
  """
  # Load tools from each module
  load_core_tools(mcp_server)
  load_sql_tools(mcp_server)
  load_uc_tools(mcp_server)
  # load_data_tools(mcp_server)
  load_job_tools(mcp_server)

  # Dashboard tools include all widget creation functionality
  load_dashboard_tools(mcp_server)

  # Disabled: widgets.py has duplicate tools that conflict with dashboards.py
  # load_widget_tools(mcp_server)

  # load_governance_tools(mcp_server)
