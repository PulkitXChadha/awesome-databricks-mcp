"""MCP information router."""

import os
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter

router = APIRouter()


@router.get('/info')
async def get_mcp_info() -> Dict[str, Any]:
  """Get MCP server information including URL and capabilities.

  Returns:
      Dictionary with MCP server details
  """
  # Get the base directory
  base_dir = Path(__file__).parent.parent.parent

  # For Databricks Apps, the MCP endpoint is at the same host on /mcp/
  # For local development, it's on port 8001
  is_databricks_app = os.environ.get('DATABRICKS_APP_PORT') is not None

  if is_databricks_app:
    # In production, MCP is at same host/port but /mcp/ path
    mcp_url = '/mcp/'  # Relative URL for same-origin
  else:
    # Local development
    mcp_url = 'http://localhost:8001/mcp/'

  return {
    'mcp_url': mcp_url,
    'server_name': 'mcp-commands',
    'transport': 'http',
    'capabilities': {'prompts': True, 'tools': True},
    'client_path': str(base_dir / 'mcp_databricks_client.py'),
    # No wrapper needed anymore - direct Python execution
  }


@router.get('/discovery')
async def get_mcp_discovery() -> Dict[str, Any]:
  """Get MCP discovery information including prompts and tools.

  This endpoint dynamically discovers available prompts and tools
  from the FastMCP server instance.

  Returns:
      Dictionary with prompts and tools lists and servername
  """
  from server.app import mcp_server as mcp
  from server.app import servername

  prompts_list = []
  tools_list = []

  # Get prompts dynamically from FastMCP
  if hasattr(mcp, '_prompt_manager'):
    prompts = await mcp._prompt_manager.list_prompts()
    prompts_list = [
      {
        'name': prompt.key,
        'description': prompt.description or f'{prompt.key.replace("_", " ").title()}',
      }
      for prompt in prompts
    ]

  # Get tools dynamically from FastMCP
  if hasattr(mcp, '_tool_manager'):
    tools = await mcp._tool_manager.list_tools()
    tools_list = [
      {'name': tool.key, 'description': tool.description or f'{tool.key.replace("_", " ").title()}'}
      for tool in tools
    ]

  return {'prompts': prompts_list, 'tools': tools_list, 'servername': servername}


@router.get('/config')
async def get_mcp_config() -> Dict[str, Any]:
  """Get MCP configuration for Claude Code setup.

  Returns:
      Dictionary with configuration needed for Claude MCP setup
  """
  from server.app import servername

  # Get environment variables
  databricks_host = os.environ.get('DATABRICKS_HOST', '')
  is_databricks_app = os.environ.get('DATABRICKS_APP_PORT') is not None

  # Get the base directory for client path
  base_dir = Path(__file__).parent.parent.parent
  client_path = str(base_dir / 'mcp_databricks_client.py')

  return {
    'servername': servername,
    'databricks_host': databricks_host,
    'is_databricks_app': is_databricks_app,
    'client_path': client_path,
  }


@router.get('/prompt/{prompt_name}')
async def get_mcp_prompt_content(prompt_name: str) -> Dict[str, str]:
  """Get the content of a specific MCP prompt.

  Args:
      prompt_name: The name of the prompt

  Returns:
      Dictionary with prompt name and content
  """
  prompt_file = Path(f'prompts/{prompt_name}.md')

  if not prompt_file.exists():
    from fastapi import HTTPException

    raise HTTPException(status_code=404, detail=f"Prompt '{prompt_name}' not found")

  with open(prompt_file, 'r') as f:
    content = f.read()

  return {'name': prompt_name, 'content': content}
