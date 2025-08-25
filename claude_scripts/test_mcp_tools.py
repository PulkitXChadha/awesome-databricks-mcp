#!/usr/bin/env python3
"""Test script for MCP Unity Catalog tools."""

import os
import sys
from pathlib import Path

# Add the server directory to the path so we can import tools
sys.path.insert(0, str(Path(__file__).parent.parent / 'server'))

from fastmcp import FastMCP

import server.tools


def test_mcp_tools():
  """Test MCP Unity Catalog tools functionality."""
  print('🔧 Testing MCP Unity Catalog tools...')

  # Load environment variables
  from pathlib import Path

  env_path = Path('.env.local')
  if env_path.exists():
    with open(env_path) as f:
      for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
          key, _, value = line.partition('=')
          if key and value:
            os.environ[key] = value

  # Check if environment variables are set
  host = os.environ.get('DATABRICKS_HOST')
  token = os.environ.get('DATABRICKS_TOKEN')

  if not host or not token:
    print('❌ Missing DATABRICKS_HOST or DATABRICKS_TOKEN environment variables')
    return False

  print(f'✅ Using host: {host}')

  # Create MCP server and load tools
  mcp_server = FastMCP(name='test-databricks-mcp')
  server.tools.load_tools(mcp_server)

  # Get the tools from the server
  tools = {}
  if hasattr(mcp_server, 'tools'):
    for tool_name, tool_info in mcp_server.tools.items():
      if hasattr(tool_info, 'fn'):
        tools[tool_name] = tool_info.fn

  # If we can't get tools from MCP server, let's directly call the functions
  if not tools:
    print('ℹ️  Could not access tools from MCP server, calling functions directly')
    # Already imported server.tools above

    # Create a mock server to get the functions
    class MockServer:
      def tool(self, func):
        tools[func.__name__] = func
        return func

    mock_server = MockServer()
    server.tools.load_tools(mock_server)

  print(f'✅ Loaded {len(tools)} tools: {list(tools.keys())}')

  try:
    # Test 1: list_uc_catalogs
    print('\n📁 Testing list_uc_catalogs...')
    result = tools['list_uc_catalogs']()
    if result['success']:
      count = result.get('count', 0)
      print(f'✅ Found {count} catalog(s)')

      if count > 0 and 'catalogs' in result:
        first_catalog = result['catalogs'][0]['name']
        print(f'📁 First catalog: {first_catalog}')

        # Test 2: describe_uc_catalog
        print(f"\n📋 Testing describe_uc_catalog for '{first_catalog}'...")
        result = tools['describe_uc_catalog'](first_catalog)
        if result['success']:
          schema_count = result.get('schema_count', 0)
          print(f'✅ Catalog has {schema_count} schema(s)')

          if schema_count > 0 and 'schemas' in result:
            first_schema = result['schemas'][0]['name']
            print(f'📁 First schema: {first_schema}')

            # Test 3: describe_uc_schema
            print(f"\n📋 Testing describe_uc_schema for '{first_catalog}.{first_schema}'...")
            result = tools['describe_uc_schema'](first_catalog, first_schema)
            if result['success']:
              table_count = result.get('table_count', 0)
              print(f'✅ Schema has {table_count} table(s)')

              if table_count > 0 and 'tables' in result:
                first_table = result['tables'][0]['name']
                full_table = f'{first_catalog}.{first_schema}.{first_table}'
                print(f'📁 First table: {full_table}')

                # Test 4: describe_uc_table
                print(f"\n📋 Testing describe_uc_table for '{full_table}'...")
                result = tools['describe_uc_table'](full_table)
                if result['success']:
                  table_info = result.get('table', {})
                  column_count = table_info.get('column_count', 0)
                  print(f'✅ Table has {column_count} column(s)')

                  # Test with lineage
                  print('📋 Testing describe_uc_table with lineage...')
                  result_lineage = tools['describe_uc_table'](full_table, include_lineage=True)
                  if result_lineage['success'] and 'lineage' in result_lineage:
                    print('✅ Lineage information included')
                  else:
                    print(f'⚠️  Lineage test failed: {result_lineage.get("error", "Unknown error")}')
                else:
                  print(f'⚠️  describe_uc_table failed: {result.get("error", "Unknown error")}')
              else:
                print('ℹ️  No tables found in schema')
            else:
              print(f'⚠️  describe_uc_schema failed: {result.get("error", "Unknown error")}')
          else:
            print('ℹ️  No schemas found in catalog')
        else:
          print(f'⚠️  describe_uc_catalog failed: {result.get("error", "Unknown error")}')
      else:
        print('ℹ️  No catalogs found')
    else:
      print(f'⚠️  list_uc_catalogs failed: {result.get("error", "Unknown error")}')

    print('\n✅ MCP Unity Catalog tools test completed!')
    return True

  except Exception as e:
    print(f'❌ Error testing MCP tools: {e}')
    import traceback

    traceback.print_exc()
    return False


if __name__ == '__main__':
  success = test_mcp_tools()
  sys.exit(0 if success else 1)
