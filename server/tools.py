"""MCP Tools for Databricks operations."""

import os

from databricks.sdk import WorkspaceClient


def load_tools(mcp_server):
  """Register all MCP tools with the server.

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

  @mcp_server.tool
  def execute_dbsql(
    query: str,
    warehouse_id: str = None,
    catalog: str = None,
    schema: str = None,
    limit: int = 100,
  ) -> dict:
    """Execute a SQL query on Databricks SQL warehouse.

    Args:
        query: SQL query to execute
        warehouse_id: SQL warehouse ID (optional, uses env var if not provided)
        catalog: Catalog to use (optional)
        schema: Schema to use (optional)
        limit: Maximum number of rows to return (default: 100)

    Returns:
        Dictionary with query results or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get warehouse ID from parameter or environment
      warehouse_id = warehouse_id or os.environ.get('DATABRICKS_SQL_WAREHOUSE_ID')
      if not warehouse_id:
        return {
          'success': False,
          'error': (
            'No SQL warehouse ID provided. Set DATABRICKS_SQL_WAREHOUSE_ID or pass warehouse_id.'
          ),
        }

      # Build the full query with catalog/schema if provided
      full_query = query
      if catalog and schema:
        full_query = f'USE CATALOG {catalog}; USE SCHEMA {schema}; {query}'

      print(f'🔧 Executing SQL on warehouse {warehouse_id}: {query[:100]}...')

      # Execute the query
      result = w.statement_execution.execute_statement(
        warehouse_id=warehouse_id, statement=full_query, wait_timeout='30s'
      )

      # Process results
      if result.result and result.result.data_array:
        columns = [col.name for col in result.manifest.schema.columns]
        data = []

        for row in result.result.data_array[:limit]:
          row_dict = {}
          for i, col in enumerate(columns):
            row_dict[col] = row[i]
          data.append(row_dict)

        return {'success': True, 'data': {'columns': columns, 'rows': data}, 'row_count': len(data)}
      else:
        return {
          'success': True,
          'data': {'message': 'Query executed successfully with no results'},
          'row_count': 0,
        }

    except Exception as e:
      print(f'❌ Error executing SQL: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def list_warehouses() -> dict:
    """List all SQL warehouses in the Databricks workspace.

    Returns:
        Dictionary containing list of warehouses with their details
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List SQL warehouses
      warehouses = []
      for warehouse in w.warehouses.list():
        warehouses.append(
          {
            'id': warehouse.id,
            'name': warehouse.name,
            'state': warehouse.state.value if warehouse.state else 'UNKNOWN',
            'size': warehouse.cluster_size,
            'type': warehouse.warehouse_type.value if warehouse.warehouse_type else 'UNKNOWN',
            'creator': warehouse.creator_name if hasattr(warehouse, 'creator_name') else None,
            'auto_stop_mins': warehouse.auto_stop_mins
            if hasattr(warehouse, 'auto_stop_mins')
            else None,
          }
        )

      return {
        'success': True,
        'warehouses': warehouses,
        'count': len(warehouses),
        'message': f'Found {len(warehouses)} SQL warehouse(s)',
      }

    except Exception as e:
      print(f'❌ Error listing warehouses: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'warehouses': [], 'count': 0}

  @mcp_server.tool
  def list_dbfs_files(path: str = '/') -> dict:
    """List files and directories in DBFS (Databricks File System).

    Args:
        path: DBFS path to list (default: '/')

    Returns:
        Dictionary with file listings or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List files in DBFS
      files = []
      for file_info in w.dbfs.list(path):
        files.append(
          {
            'path': file_info.path,
            'is_dir': file_info.is_dir,
            'size': file_info.file_size if not file_info.is_dir else None,
            'modification_time': file_info.modification_time,
          }
        )

      return {
        'success': True,
        'path': path,
        'files': files,
        'count': len(files),
        'message': f'Listed {len(files)} item(s) in {path}',
      }

    except Exception as e:
      print(f'❌ Error listing DBFS files: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'files': [], 'count': 0}
