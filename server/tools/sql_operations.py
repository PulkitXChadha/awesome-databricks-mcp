"""SQL operations MCP tools for Databricks."""

import os

from databricks.sdk import WorkspaceClient


def load_sql_tools(mcp_server):
  """Register SQL operation MCP tools with the server.

  Args:
      mcp_server: The FastMCP server instance to register tools with
  """

  @mcp_server.tool()
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

  @mcp_server.tool()
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

      # List all warehouses
      warehouses = w.sql_warehouses.list()

      warehouse_list = []
      for warehouse in warehouses:
        warehouse_list.append(
          {
            'id': warehouse.id,
            'name': warehouse.name,
            'state': warehouse.state,
            'cluster_size': warehouse.cluster_size,
            'min_num_clusters': warehouse.min_num_clusters,
            'max_num_clusters': warehouse.max_num_clusters,
            'auto_stop_mins': warehouse.auto_stop_mins,
            'enable_serverless_compute': warehouse.enable_serverless_compute,
            'created_time': warehouse.created_time,
            'updated_time': warehouse.updated_time,
          }
        )

      return {
        'success': True,
        'warehouses': warehouse_list,
        'count': len(warehouse_list),
        'message': f'Found {len(warehouse_list)} warehouse(s)',
      }

    except Exception as e:
      print(f'❌ Error listing warehouses: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'warehouses': [], 'count': 0}

  @mcp_server.tool()
  def get_sql_warehouse(warehouse_id: str) -> dict:
    """Get details of a specific SQL warehouse.

    Args:
        warehouse_id: The ID of the warehouse to get details for

    Returns:
        Dictionary with warehouse details or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get warehouse details
      warehouse = w.sql_warehouses.get(warehouse_id)

      return {
        'success': True,
        'warehouse': {
          'id': warehouse.id,
          'name': warehouse.name,
          'state': warehouse.state,
          'cluster_size': warehouse.cluster_size,
          'min_num_clusters': warehouse.min_num_clusters,
          'max_num_clusters': warehouse.max_num_clusters,
          'auto_stop_mins': warehouse.auto_stop_mins,
          'enable_serverless_compute': warehouse.enable_serverless_compute,
          'created_time': warehouse.created_time,
          'updated_time': warehouse.updated_time,
          'tags': warehouse.tags,
          'channel': warehouse.channel,
          'warehouse_type': warehouse.warehouse_type,
        },
        'message': f'Warehouse {warehouse.name} details retrieved successfully',
      }

    except Exception as e:
      print(f'❌ Error getting warehouse details: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def create_sql_warehouse(warehouse_config: dict) -> dict:
    """Create a new SQL warehouse.

    Args:
        warehouse_config: Dictionary containing warehouse configuration

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Create warehouse
      warehouse = w.sql_warehouses.create(
        name=warehouse_config.get('name'),
        cluster_size=warehouse_config.get('cluster_size', 'Small'),
        min_num_clusters=warehouse_config.get('min_num_clusters', 1),
        max_num_clusters=warehouse_config.get('max_num_clusters', 1),
        auto_stop_mins=warehouse_config.get('auto_stop_mins', 10),
        enable_serverless_compute=warehouse_config.get('enable_serverless_compute', False),
      )

      return {
        'success': True,
        'warehouse_id': warehouse.id,
        'warehouse_name': warehouse.name,
        'message': f'Warehouse {warehouse.name} created successfully with ID {warehouse.id}',
      }

    except Exception as e:
      print(f'❌ Error creating warehouse: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def start_sql_warehouse(warehouse_id: str) -> dict:
    """Start a SQL warehouse.

    Args:
        warehouse_id: The ID of the warehouse to start

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Start warehouse
      w.sql_warehouses.start(warehouse_id)

      return {
        'success': True,
        'warehouse_id': warehouse_id,
        'message': f'Warehouse {warehouse_id} started successfully',
      }

    except Exception as e:
      print(f'❌ Error starting warehouse: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def stop_sql_warehouse(warehouse_id: str) -> dict:
    """Stop a SQL warehouse.

    Args:
        warehouse_id: The ID of the warehouse to stop

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Stop warehouse
      w.sql_warehouses.stop(warehouse_id)

      return {
        'success': True,
        'warehouse_id': warehouse_id,
        'message': f'Warehouse {warehouse_id} stopped successfully',
      }

    except Exception as e:
      print(f'❌ Error stopping warehouse: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def delete_sql_warehouse(warehouse_id: str) -> dict:
    """Delete a SQL warehouse.

    Args:
        warehouse_id: The ID of the warehouse to delete

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Delete warehouse
      w.sql_warehouses.delete(warehouse_id)

      return {
        'success': True,
        'warehouse_id': warehouse_id,
        'message': f'Warehouse {warehouse_id} deleted successfully',
      }

    except Exception as e:
      print(f'❌ Error deleting warehouse: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def list_queries(warehouse_id: str = None) -> dict:
    """List queries (all or for specific warehouse).

    Args:
        warehouse_id: SQL warehouse ID (optional, lists all queries if not provided)

    Returns:
        Dictionary with list of queries or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List queries
      queries = w.statement_execution.list_statements()

      # Filter by warehouse if specified
      if warehouse_id:
        queries = [q for q in queries if q.warehouse_id == warehouse_id]

      query_list = []
      for query in queries:
        query_list.append(
          {
            'id': query.id,
            'warehouse_id': query.warehouse_id,
            'status': query.status,
            'created_time': query.created_time,
            'completed_time': query.completed_time,
            'statement': query.statement[:100] + '...'
            if len(query.statement) > 100
            else query.statement,
          }
        )

      return {
        'success': True,
        'queries': query_list,
        'count': len(query_list),
        'warehouse_id': warehouse_id,
        'message': f'Found {len(query_list)} query(ies)'
        + (f' for warehouse {warehouse_id}' if warehouse_id else ''),
      }

    except Exception as e:
      print(f'❌ Error listing queries: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'queries': [], 'count': 0}

  @mcp_server.tool()
  def get_query(query_id: str) -> dict:
    """Get details of a specific query.

    Args:
        query_id: The ID of the query to get details for

    Returns:
        Dictionary with query details or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get query details
      query = w.statement_execution.get_statement(query_id)

      return {
        'success': True,
        'query': {
          'id': query.id,
          'warehouse_id': query.warehouse_id,
          'status': query.status,
          'created_time': query.created_time,
          'completed_time': query.completed_time,
          'statement': query.statement,
          'manifest': {
            'schema': [
              {'name': col.name, 'type': col.type} for col in query.manifest.schema.columns
            ]
          }
          if query.manifest and query.manifest.schema
          else None,
        },
        'message': f'Query {query_id} details retrieved successfully',
      }

    except Exception as e:
      print(f'❌ Error getting query details: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def get_query_results(query_id: str) -> dict:
    """Get results of a completed query.

    Args:
        query_id: The ID of the query to get results for

    Returns:
        Dictionary with query results or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get query results
      query = w.statement_execution.get_statement(query_id)

      if not query.result or not query.result.data_array:
        return {
          'success': True,
          'query_id': query_id,
          'data': {'message': 'Query has no results'},
          'row_count': 0,
        }

      # Process results
      columns = [col.name for col in query.manifest.schema.columns]
      data = []

      for row in query.result.data_array:
        row_dict = {}
        for i, col in enumerate(columns):
          row_dict[col] = row[i]
        data.append(row_dict)

      return {
        'success': True,
        'query_id': query_id,
        'data': {'columns': columns, 'rows': data},
        'row_count': len(data),
        'message': f'Retrieved {len(data)} row(s) from query {query_id}',
      }

    except Exception as e:
      print(f'❌ Error getting query results: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def cancel_query(query_id: str) -> dict:
    """Cancel a running query.

    Args:
        query_id: The ID of the query to cancel

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Cancel query
      w.statement_execution.cancel_statement(query_id)

      return {
        'success': True,
        'query_id': query_id,
        'message': f'Query {query_id} cancelled successfully',
      }

    except Exception as e:
      print(f'❌ Error cancelling query: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def get_statement_status(statement_id: str) -> dict:
    """Get statement execution status.

    Args:
        statement_id: The ID of the statement to get status for

    Returns:
        Dictionary with statement status or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get statement status
      statement = w.statement_execution.get_statement(statement_id)

      return {
        'success': True,
        'statement_id': statement_id,
        'status': statement.status,
        'warehouse_id': statement.warehouse_id,
        'created_time': statement.created_time,
        'completed_time': statement.completed_time,
        'message': f'Statement {statement_id} status: {statement.status}',
      }

    except Exception as e:
      print(f'❌ Error getting statement status: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def get_statement_results(statement_id: str) -> dict:
    """Get statement results.

    Args:
        statement_id: The ID of the statement to get results for

    Returns:
        Dictionary with statement results or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get statement results
      statement = w.statement_execution.get_statement(statement_id)

      if not statement.result or not statement.result.data_array:
        return {
          'success': True,
          'statement_id': statement_id,
          'data': {'message': 'Statement has no results'},
          'row_count': 0,
        }

      # Process results
      columns = [col.name for col in statement.manifest.schema.columns]
      data = []

      for row in statement.result.data_array:
        row_dict = {}
        for i, col in enumerate(columns):
          row_dict[col] = row[i]
        data.append(row_dict)

      return {
        'success': True,
        'statement_id': statement_id,
        'data': {'columns': columns, 'rows': data},
        'row_count': len(data),
        'message': f'Retrieved {len(data)} row(s) from statement {statement_id}',
      }

    except Exception as e:
      print(f'❌ Error getting statement results: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def cancel_statement(statement_id: str) -> dict:
    """Cancel statement execution.

    Args:
        statement_id: The ID of the statement to cancel

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Cancel statement
      w.statement_execution.cancel_statement(statement_id)

      return {
        'success': True,
        'statement_id': statement_id,
        'message': f'Statement {statement_id} cancelled successfully',
      }

    except Exception as e:
      print(f'❌ Error cancelling statement: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool()
  def list_recent_queries(limit: int = 100) -> dict:
    """List recent queries.

    Args:
        limit: Maximum number of queries to return (default: 100)

    Returns:
        Dictionary with list of recent queries or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List recent queries
      queries = w.statement_execution.list_statements()

      # Sort by creation time and limit results
      sorted_queries = sorted(queries, key=lambda x: x.created_time, reverse=True)[:limit]

      query_list = []
      for query in sorted_queries:
        query_list.append(
          {
            'id': query.id,
            'warehouse_id': query.warehouse_id,
            'status': query.status,
            'created_time': query.created_time,
            'completed_time': query.completed_time,
            'statement': query.statement[:100] + '...'
            if len(query.statement) > 100
            else query.statement,
          }
        )

      return {
        'success': True,
        'queries': query_list,
        'count': len(query_list),
        'limit': limit,
        'message': f'Found {len(query_list)} recent query(ies)',
      }

    except Exception as e:
      print(f'❌ Error listing recent queries: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'queries': [], 'count': 0}
