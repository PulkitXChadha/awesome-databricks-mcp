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
    # Test 1: describe_uc_catalog (testing with common catalog names)
    print('\n📁 Testing describe_uc_catalog...')
    # Try common catalog names
    catalog_names = ["hive_metastore", "main", "samples"]
    catalog_found = False
    
    for catalog_name in catalog_names:
      print(f"  Trying catalog: {catalog_name}")
      try:
        result = tools['describe_uc_catalog'](catalog_name)
        if result['success']:
          schema_count = result.get('schema_count', 0)
          print(f'✅ Catalog "{catalog_name}" has {schema_count} schema(s)')
          catalog_found = True

          if schema_count > 0 and 'schemas' in result:
            first_schema = result['schemas'][0]['name']
            print(f'📁 First schema: {first_schema}')

            # Test 2: describe_uc_schema
            print(f"\n📋 Testing describe_uc_schema for '{catalog_name}.{first_schema}'...")
            result = tools['describe_uc_schema'](catalog_name, first_schema)
            if result['success']:
              table_count = result.get('table_count', 0)
              print(f'✅ Schema has {table_count} table(s)')

              if table_count > 0 and 'tables' in result:
                first_table = result['tables'][0]['name']
                full_table = f'{catalog_name}.{first_schema}.{first_table}'
                print(f'📁 First table: {full_table}')

                # Test 3: describe_uc_table
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
          break  # Found a working catalog, exit loop
        else:
          print(f'⚠️  Catalog "{catalog_name}" not accessible: {result.get("error", "Unknown error")}')
      except Exception as e:
        print(f'⚠️  Error testing catalog "{catalog_name}": {e}')
    
    if not catalog_found:
      print('⚠️  No accessible catalogs found')

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
