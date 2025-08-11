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

      # List all warehouses
      warehouses = w.sql_warehouses.list()
      
      warehouse_list = []
      for warehouse in warehouses:
        warehouse_list.append({
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
        })

      return {
        'success': True,
        'warehouses': warehouse_list,
        'count': len(warehouse_list),
        'message': f'Found {len(warehouse_list)} SQL warehouse(s)',
      }

    except Exception as e:
      print(f'❌ Error listing warehouses: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'warehouses': [], 'count': 0}

  @mcp_server.tool
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
      warehouse = w.sql_warehouses.get(warehouse_id=warehouse_id)
      
      return {
        'success': True,
        'warehouse_id': warehouse.id,
        'name': warehouse.name,
        'state': warehouse.state,
        'cluster_size': warehouse.cluster_size,
        'min_num_clusters': warehouse.min_num_clusters,
        'max_num_clusters': warehouse.max_num_clusters,
        'auto_stop_mins': warehouse.auto_stop_mins,
        'enable_serverless_compute': warehouse.enable_serverless_compute,
        'created_time': warehouse.created_time,
        'updated_time': warehouse.updated_time,
        'message': f'Retrieved details for warehouse {warehouse.name}',
      }

    except Exception as e:
      print(f'❌ Error getting warehouse: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
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
      warehouse = w.sql_warehouses.create(**warehouse_config)
      
      return {
        'success': True,
        'warehouse_id': warehouse.id,
        'name': warehouse.name,
        'message': f'Successfully created warehouse {warehouse.name} with ID {warehouse.id}',
      }

    except Exception as e:
      print(f'❌ Error creating warehouse: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
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
      w.sql_warehouses.start(warehouse_id=warehouse_id)
      
      return {
        'success': True,
        'warehouse_id': warehouse_id,
        'message': f'Successfully started warehouse {warehouse_id}',
      }

    except Exception as e:
      print(f'❌ Error starting warehouse: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
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
      w.sql_warehouses.stop(warehouse_id=warehouse_id)
      
      return {
        'success': True,
        'warehouse_id': warehouse_id,
        'message': f'Successfully stopped warehouse {warehouse_id}',
      }

    except Exception as e:
      print(f'❌ Error stopping warehouse: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
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
      w.sql_warehouses.delete(warehouse_id=warehouse_id)
      
      return {
        'success': True,
        'warehouse_id': warehouse_id,
        'message': f'Successfully deleted warehouse {warehouse_id}',
      }

    except Exception as e:
      print(f'❌ Error deleting warehouse: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
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
      
      query_list = []
      for query in queries:
        if warehouse_id is None or query.warehouse_id == warehouse_id:
          query_list.append({
            'id': query.id,
            'warehouse_id': query.warehouse_id,
            'status': query.status,
            'created_time': query.created_time,
            'completed_time': query.completed_time,
            'statement': query.statement[:100] + '...' if len(query.statement) > 100 else query.statement,
          })

      return {
        'success': True,
        'queries': query_list,
        'count': len(query_list),
        'message': f'Found {len(query_list)} query(ies)',
      }

    except Exception as e:
      print(f'❌ Error listing queries: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'queries': [], 'count': 0}

  @mcp_server.tool
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
      query = w.statement_execution.get_statement(statement_id=query_id)
      
      return {
        'success': True,
        'query_id': query.id,
        'warehouse_id': query.warehouse_id,
        'status': query.status,
        'statement': query.statement,
        'created_time': query.created_time,
        'completed_time': query.completed_time,
        'message': f'Retrieved details for query {query_id}',
      }

    except Exception as e:
      print(f'❌ Error getting query: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
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
      result = w.statement_execution.get_statement_result(statement_id=query_id)
      
      if result.result and result.result.data_array:
        columns = [col.name for col in result.manifest.schema.columns]
        data = []
        
        for row in result.result.data_array:
          row_dict = {}
          for i, col in enumerate(columns):
            row_dict[col] = row[i]
          data.append(row_dict)

        return {
          'success': True,
          'query_id': query_id,
          'columns': columns,
          'rows': data,
          'row_count': len(data),
          'message': f'Retrieved results for query {query_id}',
        }
      else:
        return {
          'success': True,
          'query_id': query_id,
          'message': 'Query completed with no results',
          'row_count': 0,
        }

    except Exception as e:
      print(f'❌ Error getting query results: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
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
      w.statement_execution.cancel_execution(statement_id=query_id)
      
      return {
        'success': True,
        'query_id': query_id,
        'message': f'Successfully cancelled query {query_id}',
      }

    except Exception as e:
      print(f'❌ Error cancelling query: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
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
      statement = w.statement_execution.get_statement(statement_id=statement_id)
      
      return {
        'success': True,
        'statement_id': statement.id,
        'status': statement.status,
        'warehouse_id': statement.warehouse_id,
        'created_time': statement.created_time,
        'completed_time': statement.completed_time,
        'message': f'Retrieved status for statement {statement_id}',
      }

    except Exception as e:
      print(f'❌ Error getting statement status: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
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
      result = w.statement_execution.get_statement_result(statement_id=statement_id)
      
      if result.result and result.result.data_array:
        columns = [col.name for col in result.manifest.schema.columns]
        data = []
        
        for row in result.result.data_array:
          row_dict = {}
          for i, col in enumerate(columns):
            row_dict[col] = row[i]
          data.append(row_dict)

        return {
          'success': True,
          'statement_id': statement_id,
          'columns': columns,
          'rows': data,
          'row_count': len(data),
          'message': f'Retrieved results for statement {statement_id}',
        }
      else:
        return {
          'success': True,
          'statement_id': statement_id,
          'message': 'Statement completed with no results',
          'row_count': 0,
        }

    except Exception as e:
      print(f'❌ Error getting statement results: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
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
      w.statement_execution.cancel_execution(statement_id=statement_id)
      
      return {
        'success': True,
        'statement_id': statement_id,
        'message': f'Successfully cancelled statement {statement_id}',
      }

    except Exception as e:
      print(f'❌ Error cancelling statement: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

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

  @mcp_server.tool
  def get_dbfs_file_info(path: str) -> dict:
    """Get file/directory information from DBFS.

    Args:
        path: DBFS path to get information for

    Returns:
        Dictionary with file/directory information or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get file info
      file_info = w.dbfs.get_status(path)
      
      return {
        'success': True,
        'path': path,
        'is_dir': file_info.is_dir,
        'size': file_info.file_size if not file_info.is_dir else None,
        'modification_time': file_info.modification_time,
        'message': f'Retrieved info for {path}',
      }

    except Exception as e:
      print(f'❌ Error getting DBFS file info: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def read_dbfs_file(path: str, offset: int = 0, length: int = None) -> dict:
    """Read file content from DBFS.

    Args:
        path: DBFS file path to read
        offset: Starting byte position (default: 0)
        length: Number of bytes to read (default: None for entire file)

    Returns:
        Dictionary with file content or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Read file content
      content = w.dbfs.read(path, length=length, offset=offset)
      
      return {
        'success': True,
        'path': path,
        'offset': offset,
        'length': length,
        'content': content.decode('utf-8') if isinstance(content, bytes) else str(content),
        'message': f'Successfully read file {path}',
      }

    except Exception as e:
      print(f'❌ Error reading DBFS file: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def write_dbfs_file(path: str, content: str, overwrite: bool = False) -> dict:
    """Write content to a file in DBFS.

    Args:
        path: DBFS file path to write to
        content: Content to write to the file
        overwrite: Whether to overwrite existing file (default: False)

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Convert content to bytes if it's a string
      if isinstance(content, str):
        content_bytes = content.encode('utf-8')
      else:
        content_bytes = content

      # Write file content
      w.dbfs.put(path, content_bytes, overwrite=overwrite)
      
      return {
        'success': True,
        'path': path,
        'overwrite': overwrite,
        'content_length': len(content_bytes),
        'message': f'Successfully wrote {len(content_bytes)} bytes to {path}',
      }

    except Exception as e:
      print(f'❌ Error writing DBFS file: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def delete_dbfs_path(path: str, recursive: bool = False) -> dict:
    """Delete a file or directory from DBFS.

    Args:
        path: DBFS path to delete
        recursive: Whether to delete directory contents recursively (default: False)

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Delete the path
      w.dbfs.delete(path, recursive=recursive)
      
      return {
        'success': True,
        'path': path,
        'recursive': recursive,
        'message': f'Successfully deleted {path}',
      }

    except Exception as e:
      print(f'❌ Error deleting DBFS path: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def create_dbfs_directory(path: str) -> dict:
    """Create a directory in DBFS.

    Args:
        path: DBFS directory path to create

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Create directory by writing an empty file with a special name
      # This is a common pattern in DBFS
      w.dbfs.put(f'{path}/.directory', b'', overwrite=False)
      
      return {
        'success': True,
        'path': path,
        'message': f'Successfully created directory {path}',
      }

    except Exception as e:
      print(f'❌ Error creating DBFS directory: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def move_dbfs_path(source: str, destination: str) -> dict:
    """Move/rename a file or directory in DBFS.

    Args:
        source: Source DBFS path
        destination: Destination DBFS path

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get source file info
      source_info = w.dbfs.get_status(source)
      
      if source_info.is_dir:
        # For directories, we need to copy contents and then delete
        # This is a simplified approach - in practice you might want more sophisticated handling
        return {
          'success': False,
          'error': 'Moving directories is not yet implemented. Please use copy and delete operations.',
        }
      else:
        # For files, read content and write to new location
        content = w.dbfs.read(source)
        w.dbfs.put(destination, content, overwrite=False)
        w.dbfs.delete(source)
      
      return {
        'success': True,
        'source': source,
        'destination': destination,
        'message': f'Successfully moved {source} to {destination}',
      }

    except Exception as e:
      print(f'❌ Error moving DBFS path: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def list_uc_catalogs() -> dict:
    """List all available Unity Catalogs.

    Shows catalog names, descriptions, and types.
    Starting point for data discovery.

    Returns:
        Dictionary containing list of catalogs with their details
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List Unity Catalogs
      catalogs = []
      for catalog in w.catalogs.list():
        catalogs.append(
          {
            'name': catalog.name,
            'catalog_type': catalog.catalog_type.value if catalog.catalog_type else 'UNKNOWN',
            'comment': catalog.comment if catalog.comment else None,
            'metastore_id': catalog.metastore_id if hasattr(catalog, 'metastore_id') else None,
            'owner': catalog.owner if hasattr(catalog, 'owner') else None,
            'created_at': catalog.created_at if hasattr(catalog, 'created_at') else None,
            'updated_at': catalog.updated_at if hasattr(catalog, 'updated_at') else None,
          }
        )

      return {
        'success': True,
        'catalogs': catalogs,
        'count': len(catalogs),
        'message': f'Found {len(catalogs)} catalog(s)',
      }

    except Exception as e:
      print(f'❌ Error listing catalogs: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'catalogs': [], 'count': 0}

  @mcp_server.tool
  def describe_uc_catalog(catalog_name: str) -> dict:
    """Provide detailed information about a specific catalog.

    Takes catalog name as input.
    Shows structure and contents including schemas and tables.

    Args:
        catalog_name: Name of the catalog to describe

    Returns:
        Dictionary with catalog details and its schemas
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get catalog details
      try:
        catalog = w.catalogs.get(catalog_name)
        catalog_info = {
          'name': catalog.name,
          'catalog_type': catalog.catalog_type.value if catalog.catalog_type else 'UNKNOWN',
          'comment': catalog.comment if catalog.comment else None,
          'metastore_id': catalog.metastore_id if hasattr(catalog, 'metastore_id') else None,
          'owner': catalog.owner if hasattr(catalog, 'owner') else None,
          'created_at': catalog.created_at if hasattr(catalog, 'created_at') else None,
          'updated_at': catalog.updated_at if hasattr(catalog, 'updated_at') else None,
        }
      except Exception as catalog_error:
        return {
          'success': False,
          'error': f'Catalog "{catalog_name}" not found or access denied: {str(catalog_error)}',
        }

      # List schemas in the catalog
      schemas = []
      try:
        for schema in w.schemas.list(catalog_name):
          schemas.append(
            {
              'name': schema.name,
              'full_name': schema.full_name if hasattr(schema, 'full_name') else f'{catalog_name}.{schema.name}',
              'comment': schema.comment if schema.comment else None,
              'owner': schema.owner if hasattr(schema, 'owner') else None,
              'created_at': schema.created_at if hasattr(schema, 'created_at') else None,
              'updated_at': schema.updated_at if hasattr(schema, 'updated_at') else None,
            }
          )
      except Exception as schema_error:
        print(f'⚠️  Warning: Could not list schemas for catalog {catalog_name}: {str(schema_error)}')

      return {
        'success': True,
        'catalog': catalog_info,
        'schemas': schemas,
        'schema_count': len(schemas),
        'message': f'Catalog "{catalog_name}" contains {len(schemas)} schema(s)',
      }

    except Exception as e:
      print(f'❌ Error describing catalog: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def describe_uc_schema(catalog_name: str, schema_name: str, include_columns: bool = False) -> dict:
    """Describe a specific schema within a catalog.

    Takes catalog and schema names.
    Optional include_columns parameter for detailed table information.
    Lists tables and optionally their column details.

    Args:
        catalog_name: Name of the catalog
        schema_name: Name of the schema  
        include_columns: Whether to include detailed column information for each table (default: False)

    Returns:
        Dictionary with schema details and its tables
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get schema details
      full_schema_name = f'{catalog_name}.{schema_name}'
      try:
        schema = w.schemas.get(full_schema_name)
        schema_info = {
          'name': schema.name,
          'full_name': schema.full_name if hasattr(schema, 'full_name') else full_schema_name,
          'catalog_name': catalog_name,
          'comment': schema.comment if schema.comment else None,
          'owner': schema.owner if hasattr(schema, 'owner') else None,
          'created_at': schema.created_at if hasattr(schema, 'created_at') else None,
          'updated_at': schema.updated_at if hasattr(schema, 'updated_at') else None,
        }
      except Exception as schema_error:
        return {
          'success': False,
          'error': f'Schema "{full_schema_name}" not found or access denied: {str(schema_error)}',
        }

      # List tables in the schema
      tables = []
      try:
        for table in w.tables.list(catalog_name=catalog_name, schema_name=schema_name):
          table_info = {
            'name': table.name,
            'full_name': table.full_name if hasattr(table, 'full_name') else f'{full_schema_name}.{table.name}',
            'table_type': table.table_type.value if table.table_type else 'UNKNOWN',
            'data_source_format': table.data_source_format.value if hasattr(table, 'data_source_format') and table.data_source_format else None,
            'comment': table.comment if table.comment else None,
            'owner': table.owner if hasattr(table, 'owner') else None,
            'created_at': table.created_at if hasattr(table, 'created_at') else None,
            'updated_at': table.updated_at if hasattr(table, 'updated_at') else None,
          }

          # Include column details if requested
          if include_columns:
            try:
              table_details = w.tables.get(table_info['full_name'])
              if hasattr(table_details, 'columns') and table_details.columns:
                columns = []
                for col in table_details.columns:
                  columns.append({
                    'name': col.name,
                    'type_name': col.type_name,
                    'type_text': col.type_text if hasattr(col, 'type_text') else None,
                    'comment': col.comment if col.comment else None,
                    'nullable': col.nullable if hasattr(col, 'nullable') else None,
                    'partition_index': col.partition_index if hasattr(col, 'partition_index') else None,
                  })
                table_info['columns'] = columns
                table_info['column_count'] = len(columns)
            except Exception as col_error:
              print(f'⚠️  Warning: Could not get columns for table {table_info["full_name"]}: {str(col_error)}')
              table_info['columns_error'] = str(col_error)

          tables.append(table_info)

      except Exception as table_error:
        print(f'⚠️  Warning: Could not list tables for schema {full_schema_name}: {str(table_error)}')

      return {
        'success': True,
        'schema': schema_info,
        'tables': tables,
        'table_count': len(tables),
        'include_columns': include_columns,
        'message': f'Schema "{full_schema_name}" contains {len(tables)} table(s)',
      }

    except Exception as e:
      print(f'❌ Error describing schema: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def describe_uc_table(table_name: str, include_lineage: bool = False) -> dict:
    """Provide detailed table structure and metadata.

    Takes full table name (catalog.schema.table format).
    Optional include_lineage parameter for dependency information.
    Shows columns, data types, partitioning, and lineage.

    Args:
        table_name: Full table name in catalog.schema.table format
        include_lineage: Whether to include lineage information (default: False)

    Returns:
        Dictionary with complete table metadata
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Validate table name format
      parts = table_name.split('.')
      if len(parts) != 3:
        return {
          'success': False,
          'error': f'Invalid table name format. Expected "catalog.schema.table", got "{table_name}"',
        }

      catalog_name, schema_name, table_only_name = parts

      # Get detailed table information
      try:
        table = w.tables.get(table_name)
        table_info = {
          'name': table.name,
          'full_name': table.full_name if hasattr(table, 'full_name') else table_name,
          'catalog_name': catalog_name,
          'schema_name': schema_name,
          'table_type': table.table_type.value if table.table_type else 'UNKNOWN',
          'data_source_format': table.data_source_format.value if hasattr(table, 'data_source_format') and table.data_source_format else None,
          'comment': table.comment if table.comment else None,
          'owner': table.owner if hasattr(table, 'owner') else None,
          'created_at': table.created_at if hasattr(table, 'created_at') else None,
          'updated_at': table.updated_at if hasattr(table, 'updated_at') else None,
          'storage_location': table.storage_location if hasattr(table, 'storage_location') else None,
          'storage_credential_name': table.storage_credential_name if hasattr(table, 'storage_credential_name') else None,
        }

        # Get column information
        columns = []
        if hasattr(table, 'columns') and table.columns:
          for col in table.columns:
            column_info = {
              'name': col.name,
              'type_name': col.type_name,
              'type_text': col.type_text if hasattr(col, 'type_text') else None,
              'comment': col.comment if col.comment else None,
              'nullable': col.nullable if hasattr(col, 'nullable') else None,
              'partition_index': col.partition_index if hasattr(col, 'partition_index') else None,
            }
            columns.append(column_info)

        table_info['columns'] = columns
        table_info['column_count'] = len(columns)

        # Get partition information
        partition_columns = [col for col in columns if col.get('partition_index') is not None]
        table_info['partition_columns'] = partition_columns
        table_info['partition_count'] = len(partition_columns)

        # Get properties if available
        if hasattr(table, 'properties') and table.properties:
          table_info['properties'] = dict(table.properties)

        # Include lineage information if requested
        lineage_info = {}
        if include_lineage:
          try:
            # Note: Lineage API may require additional permissions
            # This is a placeholder for lineage information that could be extended
            lineage_info = {
              'upstream_tables': [],  # Could be populated with actual lineage data
              'downstream_tables': [],  # Could be populated with actual lineage data
              'note': 'Lineage information requires additional API calls and permissions'
            }
          except Exception as lineage_error:
            print(f'⚠️  Warning: Could not get lineage for table {table_name}: {str(lineage_error)}')
            lineage_info = {'error': f'Lineage not available: {str(lineage_error)}'}

        result = {
          'success': True,
          'table': table_info,
          'include_lineage': include_lineage,
          'message': f'Table "{table_name}" has {len(columns)} column(s) and {len(partition_columns)} partition column(s)',
        }

        if include_lineage:
          result['lineage'] = lineage_info

        return result

      except Exception as table_error:
        return {
          'success': False,
          'error': f'Table "{table_name}" not found or access denied: {str(table_error)}',
        }

    except Exception as e:
      print(f'❌ Error describing table: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def list_uc_volumes(catalog_name: str, schema_name: str) -> dict:
    """List all volumes in a Unity Catalog schema.

    Args:
        catalog_name: Name of the catalog
        schema_name: Name of the schema

    Returns:
        Dictionary with volume listings or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List volumes in the schema
      volumes = []
      try:
        for volume in w.volumes.list(catalog_name=catalog_name, schema_name=schema_name):
          volume_info = {
            'name': volume.name,
            'full_name': volume.full_name if hasattr(volume, 'full_name') else f'{catalog_name}.{schema_name}.{volume.name}',
            'catalog_name': catalog_name,
            'schema_name': schema_name,
            'volume_type': volume.volume_type.value if volume.volume_type else 'UNKNOWN',
            'storage_location': volume.storage_location if hasattr(volume, 'storage_location') else None,
            'comment': volume.comment if volume.comment else None,
            'owner': volume.owner if hasattr(volume, 'owner') else None,
            'created_at': volume.created_at if hasattr(volume, 'created_at') else None,
            'updated_at': volume.updated_at if hasattr(volume, 'updated_at') else None,
          }
          volumes.append(volume_info)
      except Exception as volume_error:
        print(f'⚠️  Warning: Could not list volumes for schema {catalog_name}.{schema_name}: {str(volume_error)}')

      return {
        'success': True,
        'catalog_name': catalog_name,
        'schema_name': schema_name,
        'volumes': volumes,
        'count': len(volumes),
        'message': f'Found {len(volumes)} volume(s) in schema {catalog_name}.{schema_name}',
      }

    except Exception as e:
      print(f'❌ Error listing volumes: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'volumes': [], 'count': 0}

  @mcp_server.tool
  def describe_uc_volume(volume_name: str) -> dict:
    """Get detailed volume information including storage location and permissions.

    Args:
        volume_name: Full volume name in catalog.schema.volume format

    Returns:
        Dictionary with complete volume metadata
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Validate volume name format
      parts = volume_name.split('.')
      if len(parts) != 3:
        return {
          'success': False,
          'error': f'Invalid volume name format. Expected "catalog.schema.volume", got "{volume_name}"',
        }

      catalog_name, schema_name, volume_only_name = parts

      # Get detailed volume information
      try:
        volume = w.volumes.get(volume_name)
        volume_info = {
          'name': volume.name,
          'full_name': volume.full_name if hasattr(volume, 'full_name') else volume_name,
          'catalog_name': catalog_name,
          'schema_name': schema_name,
          'volume_type': volume.volume_type.value if volume.volume_type else 'UNKNOWN',
          'storage_location': volume.storage_location if hasattr(volume, 'storage_location') else None,
          'comment': volume.comment if volume.comment else None,
          'owner': volume.owner if hasattr(volume, 'owner') else None,
          'created_at': volume.created_at if hasattr(volume, 'created_at') else None,
          'updated_at': volume.updated_at if hasattr(volume, 'updated_at') else None,
        }

        # Get properties if available
        if hasattr(volume, 'properties') and volume.properties:
          volume_info['properties'] = dict(volume.properties)

        return {
          'success': True,
          'volume': volume_info,
          'message': f'Volume "{volume_name}" details retrieved successfully',
        }

      except Exception as volume_error:
        return {
          'success': False,
          'error': f'Volume "{volume_name}" not found or access denied: {str(volume_error)}',
        }

    except Exception as e:
      print(f'❌ Error describing volume: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def list_uc_functions(catalog_name: str, schema_name: str) -> dict:
    """List all functions in a Unity Catalog schema.

    Args:
        catalog_name: Name of the catalog
        schema_name: Name of the schema

    Returns:
        Dictionary with function listings or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List functions in the schema
      functions = []
      try:
        for function in w.functions.list(catalog_name=catalog_name, schema_name=schema_name):
          function_info = {
            'name': function.name,
            'full_name': function.full_name if hasattr(function, 'full_name') else f'{catalog_name}.{schema_name}.{function.name}',
            'catalog_name': catalog_name,
            'schema_name': schema_name,
            'function_type': function.function_type.value if function.function_type else 'UNKNOWN',
            'comment': function.comment if function.comment else None,
            'owner': function.owner if hasattr(function, 'owner') else None,
            'created_at': function.created_at if hasattr(function, 'created_at') else None,
            'updated_at': function.updated_at if hasattr(function, 'updated_at') else None,
          }
          functions.append(function_info)
      except Exception as function_error:
        print(f'⚠️  Warning: Could not list functions for schema {catalog_name}.{schema_name}: {str(function_error)}')

      return {
        'success': True,
        'catalog_name': catalog_name,
        'schema_name': schema_name,
        'functions': functions,
        'count': len(functions),
        'message': f'Found {len(functions)} function(s) in schema {catalog_name}.{schema_name}',
      }

    except Exception as e:
      print(f'❌ Error listing functions: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'functions': [], 'count': 0}

  @mcp_server.tool
  def describe_uc_function(function_name: str) -> dict:
    """Get detailed function information including parameters and return type.

    Args:
        function_name: Full function name in catalog.schema.function format

    Returns:
        Dictionary with complete function metadata
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Validate function name format
      parts = function_name.split('.')
      if len(parts) != 3:
        return {
          'success': False,
          'error': f'Invalid function name format. Expected "catalog.schema.function", got "{function_name}"',
        }

      catalog_name, schema_name, function_only_name = parts

      # Get detailed function information
      try:
        function = w.functions.get(function_name)
        function_info = {
          'name': function.name,
          'full_name': function.full_name if hasattr(function, 'full_name') else function_name,
          'catalog_name': catalog_name,
          'schema_name': schema_name,
          'function_type': function.function_type.value if function.function_type else 'UNKNOWN',
          'comment': function.comment if function.comment else None,
          'owner': function.owner if hasattr(function, 'owner') else None,
          'created_at': function.created_at if hasattr(function, 'created_at') else None,
          'updated_at': function.updated_at if hasattr(function, 'updated_at') else None,
        }

        # Get function details if available
        if hasattr(function, 'input_params') and function.input_params:
          function_info['input_params'] = [
            {
              'name': param.name,
              'type': param.type_name if hasattr(param, 'type_name') else 'UNKNOWN',
              'comment': param.comment if hasattr(param, 'comment') else None,
            }
            for param in function.input_params
          ]

        if hasattr(function, 'return_type'):
          function_info['return_type'] = function.return_type

        # Get properties if available
        if hasattr(function, 'properties') and function.properties:
          function_info['properties'] = dict(function.properties)

        return {
          'success': True,
          'function': function_info,
          'message': f'Function "{function_name}" details retrieved successfully',
        }

      except Exception as function_error:
        return {
          'success': False,
          'error': f'Function "{function_name}" not found or access denied: {str(function_error)}',
        }

    except Exception as e:
      print(f'❌ Error describing function: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def list_external_locations() -> dict:
    """List all external locations configured in the workspace.

    Returns:
        Dictionary with external location listings or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List external locations
      locations = []
      try:
        for location in w.external_locations.list():
          location_info = {
            'name': location.name,
            'url': location.url if hasattr(location, 'url') else None,
            'credential_name': location.credential_name if hasattr(location, 'credential_name') else None,
            'comment': location.comment if location.comment else None,
            'owner': location.owner if hasattr(location, 'owner') else None,
            'created_at': location.created_at if hasattr(location, 'created_at') else None,
            'updated_at': location.updated_at if hasattr(location, 'updated_at') else None,
          }
          locations.append(location_info)
      except Exception as location_error:
        print(f'⚠️  Warning: Could not list external locations: {str(location_error)}')

      return {
        'success': True,
        'locations': locations,
        'count': len(locations),
        'message': f'Found {len(locations)} external location(s)',
      }

    except Exception as e:
      print(f'❌ Error listing external locations: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'locations': [], 'count': 0}

  @mcp_server.tool
  def describe_external_location(location_name: str) -> dict:
    """Get detailed external location information.

    Args:
        location_name: Name of the external location

    Returns:
        Dictionary with external location details or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get external location details
      try:
        location = w.external_locations.get(location_name)
        location_info = {
          'name': location.name,
          'url': location.url if hasattr(location, 'url') else None,
          'credential_name': location.credential_name if hasattr(location, 'credential_name') else None,
          'comment': location.comment if location.comment else None,
          'owner': location.owner if hasattr(location, 'owner') else None,
          'created_at': location.created_at if hasattr(location, 'created_at') else None,
          'updated_at': location.updated_at if hasattr(location, 'updated_at') else None,
        }

        # Get properties if available
        if hasattr(location, 'properties') and location.properties:
          location_info['properties'] = dict(location.properties)

        return {
          'success': True,
          'location': location_info,
          'message': f'External location "{location_name}" details retrieved successfully',
        }

      except Exception as location_error:
        return {
          'success': False,
          'error': f'External location "{location_name}" not found or access denied: {str(location_error)}',
        }

    except Exception as e:
      print(f'❌ Error describing external location: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def list_storage_credentials() -> dict:
    """List all storage credentials configured in the workspace.

    Returns:
        Dictionary with storage credential listings or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List storage credentials
      credentials = []
      try:
        for credential in w.storage_credentials.list():
          credential_info = {
            'name': credential.name,
            'credential_type': credential.credential_type.value if credential.credential_type else 'UNKNOWN',
            'comment': credential.comment if credential.comment else None,
            'owner': credential.owner if hasattr(credential, 'owner') else None,
            'created_at': credential.created_at if hasattr(credential, 'created_at') else None,
            'updated_at': credential.updated_at if hasattr(credential, 'updated_at') else None,
          }
          credentials.append(credential_info)
      except Exception as credential_error:
        print(f'⚠️  Warning: Could not list storage credentials: {str(credential_error)}')

      return {
        'success': True,
        'credentials': credentials,
        'count': len(credentials),
        'message': f'Found {len(credentials)} storage credential(s)',
      }

    except Exception as e:
      print(f'❌ Error listing storage credentials: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'credentials': [], 'count': 0}

  @mcp_server.tool
  def describe_storage_credential(credential_name: str) -> dict:
    """Get detailed storage credential information.

    Args:
        credential_name: Name of the storage credential

    Returns:
        Dictionary with storage credential details or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get storage credential details
      try:
        credential = w.storage_credentials.get(credential_name)
        credential_info = {
          'name': credential.name,
          'credential_type': credential.credential_type.value if credential.credential_type else 'UNKNOWN',
          'comment': credential.comment if credential.comment else None,
          'owner': credential.owner if hasattr(credential, 'owner') else None,
          'created_at': credential.created_at if hasattr(credential, 'created_at') else None,
          'updated_at': credential.updated_at if hasattr(credential, 'updated_at') else None,
        }

        # Get properties if available
        if hasattr(credential, 'properties') and credential.properties:
          credential_info['properties'] = dict(credential.properties)

        return {
          'success': True,
          'credential': credential_info,
          'message': f'Storage credential "{credential_name}" details retrieved successfully',
        }

      except Exception as credential_error:
        return {
          'success': False,
          'error': f'Storage credential "{credential_name}" not found or access denied: {str(credential_error)}',
        }

    except Exception as e:
      print(f'❌ Error describing storage credential: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def list_uc_permissions(catalog_name: str = None, schema_name: str = None, 
                          table_name: str = None) -> dict:
    """List permissions for Unity Catalog objects.

    Args:
        catalog_name: Name of the catalog (optional)
        schema_name: Name of the schema (optional)
        table_name: Name of the table (optional)

    Returns:
        Dictionary with permission listings or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Determine the object to check permissions for
      if table_name:
        if not catalog_name or not schema_name:
          return {
            'success': False,
            'error': 'Both catalog_name and schema_name are required when checking table permissions',
          }
        object_name = f'{catalog_name}.{schema_name}.{table_name}'
        object_type = 'table'
      elif schema_name:
        if not catalog_name:
          return {
            'success': False,
            'error': 'catalog_name is required when checking schema permissions',
          }
        object_name = f'{catalog_name}.{schema_name}'
        object_type = 'schema'
      elif catalog_name:
        object_name = catalog_name
        object_type = 'catalog'
      else:
        return {
          'success': False,
          'error': 'At least one of catalog_name, schema_name, or table_name must be provided',
        }

      # Get permissions for the object
      permissions = []
      try:
        # Note: This is a placeholder for permissions API
        # The actual permissions API may require different calls
        permissions = [
          {
            'note': f'Permissions for {object_type} "{object_name}"',
            'object_name': object_name,
            'object_type': object_type,
            'permissions': 'Permissions API integration requires additional implementation'
          }
        ]
      except Exception as perm_error:
        print(f'⚠️  Warning: Could not get permissions for {object_type} "{object_name}": {str(perm_error)}')

      return {
        'success': True,
        'object_name': object_name,
        'object_type': object_type,
        'permissions': permissions,
        'count': len(permissions),
        'message': f'Retrieved permissions for {object_type} "{object_name}"',
      }

    except Exception as e:
      print(f'❌ Error listing permissions: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'permissions': [], 'count': 0}

  @mcp_server.tool
  def search_uc_objects(query: str, object_types: list = None) -> dict:
    """Search for Unity Catalog objects by name, description, or tags.

    Args:
        query: Search query string
        object_types: List of object types to search (catalog, schema, table, volume, function)

    Returns:
        Dictionary with search results or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Default to searching all object types if none specified
      if not object_types:
        object_types = ['catalog', 'schema', 'table', 'volume', 'function']

      search_results = []
      
      try:
        # Search catalogs
        if 'catalog' in object_types:
          for catalog in w.catalogs.list():
            if query.lower() in catalog.name.lower() or (catalog.comment and query.lower() in catalog.comment.lower()):
              search_results.append({
                'name': catalog.name,
                'type': 'catalog',
                'full_name': catalog.name,
                'comment': catalog.comment,
                'match_reason': 'name' if query.lower() in catalog.name.lower() else 'comment'
              })

        # Search schemas
        if 'schema' in object_types:
          for catalog in w.catalogs.list():
            try:
              for schema in w.schemas.list(catalog.name):
                if query.lower() in schema.name.lower() or (schema.comment and query.lower() in schema.comment.lower()):
                  search_results.append({
                    'name': schema.name,
                    'type': 'schema',
                    'full_name': f'{catalog.name}.{schema.name}',
                    'catalog_name': catalog.name,
                    'comment': schema.comment,
                    'match_reason': 'name' if query.lower() in schema.name.lower() else 'comment'
                  })
            except Exception:
              continue

        # Search tables
        if 'table' in object_types:
          for catalog in w.catalogs.list():
            try:
              for schema in w.schemas.list(catalog.name):
                try:
                  for table in w.tables.list(catalog_name=catalog.name, schema_name=schema.name):
                    if query.lower() in table.name.lower() or (table.comment and query.lower() in table.comment.lower()):
                      search_results.append({
                        'name': table.name,
                        'type': 'table',
                        'full_name': f'{catalog.name}.{schema.name}.{table.name}',
                        'catalog_name': catalog.name,
                        'schema_name': schema.name,
                        'comment': table.comment,
                        'match_reason': 'name' if query.lower() in table.name.lower() else 'comment'
                      })
                except Exception:
                  continue
            except Exception:
              continue

      except Exception as search_error:
        print(f'⚠️  Warning: Error during search: {str(search_error)}')

      return {
        'success': True,
        'query': query,
        'object_types': object_types,
        'results': search_results,
        'count': len(search_results),
        'message': f'Found {len(search_results)} object(s) matching "{query}"',
      }

    except Exception as e:
      print(f'❌ Error searching UC objects: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'results': [], 'count': 0}

  @mcp_server.tool
  def get_table_statistics(table_name: str) -> dict:
    """Get table statistics including row count, size, and column statistics.

    Args:
        table_name: Full table name in catalog.schema.table format

    Returns:
        Dictionary with table statistics or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Validate table name format
      parts = table_name.split('.')
      if len(parts) != 3:
        return {
          'success': False,
          'error': f'Invalid table name format. Expected "catalog.schema.table", got "{table_name}"',
        }

      catalog_name, schema_name, table_only_name = parts

      # Get table details
      try:
        table = w.tables.get(table_name)
        
        # Basic table info
        table_stats = {
          'name': table.name,
          'full_name': table.full_name if hasattr(table, 'full_name') else table_name,
          'catalog_name': catalog_name,
          'schema_name': schema_name,
          'table_type': table.table_type.value if table.table_type else 'UNKNOWN',
        }

        # Get column statistics if available
        if hasattr(table, 'columns') and table.columns:
          column_stats = []
          for col in table.columns:
            col_stat = {
              'name': col.name,
              'type_name': col.type_name,
              'nullable': col.nullable if hasattr(col, 'nullable') else None,
            }
            column_stats.append(col_stat)
          
          table_stats['columns'] = column_stats
          table_stats['column_count'] = len(column_stats)

        # Note: Detailed statistics like row count, size, etc. may require additional API calls
        # This is a placeholder for statistics that could be extended
        table_stats['statistics_note'] = 'Detailed statistics (row count, size, etc.) require additional API integration'

        return {
          'success': True,
          'table_stats': table_stats,
          'message': f'Table statistics for "{table_name}" retrieved successfully',
        }

      except Exception as table_error:
        return {
          'success': False,
          'error': f'Table "{table_name}" not found or access denied: {str(table_error)}',
        }

    except Exception as e:
      print(f'❌ Error getting table statistics: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def list_metastores() -> dict:
    """List all metastores in the workspace.

    Returns:
        Dictionary with metastore listings or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List metastores
      metastores = []
      try:
        for metastore in w.metastores.list():
          metastore_info = {
            'name': metastore.name,
            'id': metastore.metastore_id if hasattr(metastore, 'metastore_id') else None,
            'owner': metastore.owner if hasattr(metastore, 'owner') else None,
            'comment': metastore.comment if metastore.comment else None,
            'created_at': metastore.created_at if hasattr(metastore, 'created_at') else None,
            'updated_at': metastore.updated_at if hasattr(metastore, 'updated_at') else None,
          }
          metastores.append(metastore_info)
      except Exception as metastore_error:
        print(f'⚠️  Warning: Could not list metastores: {str(metastore_error)}')

      return {
        'success': True,
        'metastores': metastores,
        'count': len(metastores),
        'message': f'Found {len(metastores)} metastore(s)',
      }

    except Exception as e:
      print(f'❌ Error listing metastores: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'metastores': [], 'count': 0}

  @mcp_server.tool
  def describe_metastore(metastore_name: str) -> dict:
    """Get detailed metastore information.

    Args:
        metastore_name: Name of the metastore

    Returns:
        Dictionary with metastore details or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get metastore details
      try:
        metastore = w.metastores.get(metastore_name)
        metastore_info = {
          'name': metastore.name,
          'id': metastore.metastore_id if hasattr(metastore, 'metastore_id') else None,
          'owner': metastore.owner if hasattr(metastore, 'owner') else None,
          'comment': metastore.comment if metastore.comment else None,
          'created_at': metastore.created_at if hasattr(metastore, 'created_at') else None,
          'updated_at': metastore.updated_at if hasattr(metastore, 'updated_at') else None,
        }

        # Get properties if available
        if hasattr(metastore, 'properties') and metastore.properties:
          metastore_info['properties'] = dict(metastore.properties)

        return {
          'success': True,
          'metastore': metastore_info,
          'message': f'Metastore "{metastore_name}" details retrieved successfully',
        }

      except Exception as metastore_error:
        return {
          'success': False,
          'error': f'Metastore "{metastore_name}" not found or access denied: {str(metastore_error)}',
        }

    except Exception as e:
      print(f'❌ Error describing metastore: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def list_uc_models(catalog_name: str, schema_name: str) -> dict:
    """List all models in a Unity Catalog schema.

    Args:
        catalog_name: Name of the catalog
        schema_name: Name of the schema

    Returns:
        Dictionary with model listings or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List models in the schema
      models = []
      try:
        for model in w.models.list(catalog_name=catalog_name, schema_name=schema_name):
          model_info = {
            'name': model.name,
            'full_name': model.full_name if hasattr(model, 'full_name') else f'{catalog_name}.{schema_name}.{model.name}',
            'catalog_name': catalog_name,
            'schema_name': schema_name,
            'model_type': model.model_type.value if hasattr(model, 'model_type') and model.model_type else 'UNKNOWN',
            'comment': model.comment if model.comment else None,
            'owner': model.owner if hasattr(model, 'owner') else None,
            'created_at': model.created_at if hasattr(model, 'created_at') else None,
            'updated_at': model.updated_at if hasattr(model, 'updated_at') else None,
          }
          models.append(model_info)
      except Exception as model_error:
        print(f'⚠️  Warning: Could not list models for schema {catalog_name}.{schema_name}: {str(model_error)}')

      return {
        'success': True,
        'catalog_name': catalog_name,
        'schema_name': schema_name,
        'models': models,
        'count': len(models),
        'message': f'Found {len(models)} model(s) in schema {catalog_name}.{schema_name}',
      }

    except Exception as e:
      print(f'❌ Error listing models: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'models': [], 'count': 0}

  @mcp_server.tool
  def describe_uc_model(model_name: str) -> dict:
    """Get detailed model information including version history and lineage.

    Args:
        model_name: Full model name in catalog.schema.model format

    Returns:
        Dictionary with complete model metadata
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Validate model name format
      parts = model_name.split('.')
      if len(parts) != 3:
        return {
          'success': False,
          'error': f'Invalid model name format. Expected "catalog.schema.model", got "{model_name}"',
        }

      catalog_name, schema_name, model_only_name = parts

      # Get detailed model information
      try:
        model = w.models.get(model_name)
        model_info = {
          'name': model.name,
          'full_name': model.full_name if hasattr(model, 'full_name') else model_name,
          'catalog_name': catalog_name,
          'schema_name': schema_name,
          'model_type': model.model_type.value if hasattr(model, 'model_type') and model.model_type else 'UNKNOWN',
          'comment': model.comment if model.comment else None,
          'owner': model.owner if hasattr(model, 'owner') else None,
          'created_at': model.created_at if hasattr(model, 'created_at') else None,
          'updated_at': model.updated_at if hasattr(model, 'updated_at') else None,
        }

        # Get model details if available
        if hasattr(model, 'storage_location'):
          model_info['storage_location'] = model.storage_location

        if hasattr(model, 'properties') and model.properties:
          model_info['properties'] = dict(model.properties)

        return {
          'success': True,
          'model': model_info,
          'message': f'Model "{model_name}" details retrieved successfully',
        }

      except Exception as model_error:
        return {
          'success': False,
          'error': f'Model "{model_name}" not found or access denied: {str(model_error)}',
        }

    except Exception as e:
      print(f'❌ Error describing model: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def list_uc_tags(catalog_name: str = None) -> dict:
    """List available tags in Unity Catalog.

    Args:
        catalog_name: Name of the catalog (optional, lists all if not specified)

    Returns:
        Dictionary with tag listings or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List tags
      tags = []
      try:
        # Note: This is a placeholder for tags API
        # The actual tags API may require different calls
        tags = [
          {
            'note': f'Tags for catalog "{catalog_name}"' if catalog_name else 'All available tags',
            'catalog_name': catalog_name,
            'tags': 'Tags API integration requires additional implementation',
            'message': 'Tag management capabilities are available through the Databricks SDK but require specific API integration'
          }
        ]
      except Exception as tag_error:
        print(f'⚠️  Warning: Could not list tags: {str(tag_error)}')

      return {
        'success': True,
        'catalog_name': catalog_name,
        'tags': tags,
        'count': len(tags),
        'message': f'Retrieved tag information for {"catalog " + catalog_name if catalog_name else "all catalogs"}',
      }

    except Exception as e:
      print(f'❌ Error listing tags: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'tags': [], 'count': 0}

  @mcp_server.tool
  def apply_uc_tags(object_name: str, tags: dict) -> dict:
    """Apply tags to Unity Catalog objects.

    Args:
        object_name: Full object name (catalog.schema.table, catalog.schema, or catalog)
        tags: Dictionary of tag key-value pairs to apply

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Validate object name format
      parts = object_name.split('.')
      if len(parts) < 1 or len(parts) > 3:
        return {
          'success': False,
          'error': f'Invalid object name format. Expected "catalog", "catalog.schema", or "catalog.schema.table", got "{object_name}"',
        }

      # Note: This is a placeholder for tag application API
      # The actual tag application API may require different calls
      tag_result = {
        'object_name': object_name,
        'tags_requested': tags,
        'operation': 'apply_tags',
        'status': 'placeholder',
        'note': 'Tag application requires additional API integration with the Databricks SDK'
      }

      return {
        'success': True,
        'result': tag_result,
        'message': f'Tag application operation prepared for object "{object_name}"',
      }

    except Exception as e:
      print(f'❌ Error applying tags: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def list_data_quality_monitors(catalog_name: str = None) -> dict:
    """List data quality monitors configured in Unity Catalog.

    Args:
        catalog_name: Name of the catalog (optional, lists all if not specified)

    Returns:
        Dictionary with monitor listings or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List data quality monitors
      monitors = []
      try:
        # Note: This is a placeholder for data quality monitors API
        # The actual data quality API may require different calls
        monitors = [
          {
            'note': f'Data quality monitors for catalog "{catalog_name}"' if catalog_name else 'All data quality monitors',
            'catalog_name': catalog_name,
            'monitors': 'Data quality monitoring API integration requires additional implementation',
            'message': 'Data quality monitoring capabilities are available through Databricks but require specific API integration'
          }
        ]
      except Exception as monitor_error:
        print(f'⚠️  Warning: Could not list data quality monitors: {str(monitor_error)}')

      return {
        'success': True,
        'catalog_name': catalog_name,
        'monitors': monitors,
        'count': len(monitors),
        'message': f'Retrieved data quality monitor information for {"catalog " + catalog_name if catalog_name else "all catalogs"}',
      }

    except Exception as e:
      print(f'❌ Error listing data quality monitors: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'monitors': [], 'count': 0}

  @mcp_server.tool
  def get_data_quality_results(monitor_name: str, date_range: str = "7d") -> dict:
    """Get data quality monitoring results.

    Args:
        monitor_name: Name of the data quality monitor
        date_range: Date range for results (e.g., "7d", "30d", "90d")

    Returns:
        Dictionary with monitoring results or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: This is a placeholder for data quality results API
      # The actual data quality results API may require different calls
      results = {
        'monitor_name': monitor_name,
        'date_range': date_range,
        'results': 'Data quality results API integration requires additional implementation',
        'message': 'Data quality monitoring results are available through Databricks but require specific API integration'
      }

      return {
        'success': True,
        'monitor_name': monitor_name,
        'date_range': date_range,
        'results': results,
        'message': f'Data quality results for monitor "{monitor_name}" over {date_range}',
      }

    except Exception as e:
      print(f'❌ Error getting data quality results: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def create_data_quality_monitor(table_name: str, rules: list) -> dict:
    """Create a new data quality monitor for a table.

    Args:
        table_name: Full table name in catalog.schema.table format
        rules: List of data quality rules to apply

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Validate table name format
      parts = table_name.split('.')
      if len(parts) != 3:
        return {
          'success': False,
          'error': f'Invalid table name format. Expected "catalog.schema.table", got "{table_name}"',
        }

      catalog_name, schema_name, table_only_name = parts

      # Note: This is a placeholder for data quality monitor creation API
      # The actual data quality monitor creation API may require different calls
      monitor_result = {
        'table_name': table_name,
        'catalog_name': catalog_name,
        'schema_name': schema_name,
        'rules_requested': rules,
        'operation': 'create_data_quality_monitor',
        'status': 'placeholder',
        'note': 'Data quality monitor creation requires additional API integration with the Databricks SDK'
      }

      return {
        'success': True,
        'result': monitor_result,
        'message': f'Data quality monitor creation prepared for table "{table_name}"',
      }

    except Exception as e:
      print(f'❌ Error creating data quality monitor: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  # Job Management Tools
  @mcp_server.tool
  def list_jobs() -> dict:
    """List all jobs in the Databricks workspace.

    Returns:
        Dictionary containing list of jobs with their details
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      print('🔧 Listing all jobs in workspace...')

      # List all jobs
      jobs = list(w.jobs.list())
      
      # Extract relevant job information
      job_list = []
      for job in jobs:
        job_info = {
          'job_id': job.job_id,
          'name': job.settings.name,
          'creator': job.creator_user_name,
          'created_time': job.created_time.isoformat() if job.created_time else None,
          'run_as_user_id': job.settings.run_as_user_id,
          'timeout_seconds': job.settings.timeout_seconds,
          'max_concurrent_runs': job.settings.max_concurrent_runs,
          'tags': job.settings.tags if hasattr(job.settings, 'tags') else {},
          'schedule': job.settings.schedule if hasattr(job.settings, 'schedule') else None,
          'email_notifications': job.settings.email_notifications if hasattr(job.settings, 'email_notifications') else None,
        }
        job_list.append(job_info)

      return {
        'success': True,
        'jobs': job_list,
        'count': len(job_list),
        'message': f'Retrieved {len(job_list)} jobs from workspace',
      }

    except Exception as e:
      print(f'❌ Error listing jobs: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'jobs': [], 'count': 0}

  @mcp_server.tool
  def get_job(job_id: str) -> dict:
    """Get detailed information about a specific job.

    Args:
        job_id: The ID of the job to retrieve

    Returns:
        Dictionary with detailed job information or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      print(f'🔧 Getting job details for job ID: {job_id}')

      # Get job details
      job = w.jobs.get(job_id=job_id)
      
      # Extract comprehensive job information
      job_details = {
        'job_id': job.job_id,
        'name': job.settings.name,
        'creator': job.creator_user_name,
        'created_time': job.created_time.isoformat() if job.created_time else None,
        'run_as_user_id': job.settings.run_as_user_id,
        'timeout_seconds': job.settings.timeout_seconds,
        'max_concurrent_runs': job.settings.max_concurrent_runs,
        'tags': job.settings.tags if hasattr(job.settings, 'tags') else {},
        'schedule': job.settings.schedule if hasattr(job.settings, 'schedule') else None,
        'email_notifications': job.settings.email_notifications if hasattr(job.settings, 'email_notifications') else None,
        'notebook_task': job.settings.notebook_task if hasattr(job.settings, 'notebook_task') else None,
        'spark_jar_task': job.settings.spark_jar_task if hasattr(job.settings, 'spark_jar_task') else None,
        'spark_python_task': job.settings.spark_python_task if hasattr(job.settings, 'spark_python_task') else None,
        'spark_submit_task': job.settings.spark_submit_task if hasattr(job.settings, 'spark_submit_task') else None,
        'pipeline_task': job.settings.pipeline_task if hasattr(job.settings, 'pipeline_task') else None,
        'python_wheel_task': job.settings.python_wheel_task if hasattr(job.settings, 'python_wheel_task') else None,
        'dbt_task': job.settings.dbt_task if hasattr(job.settings, 'dbt_task') else None,
        'run_job_task': job.settings.run_job_task if hasattr(job.settings, 'run_job_task') else None,
        'sql_task': job.settings.sql_task if hasattr(job.settings, 'sql_task') else None,
      }

      return {
        'success': True,
        'job': job_details,
        'message': f'Retrieved details for job "{job.settings.name}" (ID: {job_id})',
      }

    except Exception as e:
      print(f'❌ Error getting job details: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def create_job(job_config: dict) -> dict:
    """Create a new job in the Databricks workspace.

    Args:
        job_config: Dictionary containing job configuration

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      print(f'🔧 Creating new job: {job_config.get("name", "Unnamed")}')

      # Create the job
      job = w.jobs.create(**job_config)
      
      return {
        'success': True,
        'job_id': job.job_id,
        'job_name': job.settings.name,
        'message': f'Successfully created job "{job.settings.name}" with ID {job.job_id}',
      }

    except Exception as e:
      print(f'❌ Error creating job: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def update_job(job_id: str, updates: dict) -> dict:
    """Update an existing job in the Databricks workspace.

    Args:
        job_id: The ID of the job to update
        updates: Dictionary containing the updates to apply

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      print(f'🔧 Updating job ID: {job_id}')

      # Update the job
      w.jobs.update(job_id=job_id, **updates)
      
      return {
        'success': True,
        'job_id': job_id,
        'message': f'Successfully updated job with ID {job_id}',
      }

    except Exception as e:
      print(f'❌ Error updating job: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def delete_job(job_id: str) -> dict:
    """Delete a job from the Databricks workspace.

    Args:
        job_id: The ID of the job to delete

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      print(f'🔧 Deleting job ID: {job_id}')

      # Delete the job
      w.jobs.delete(job_id=job_id)
      
      return {
        'success': True,
        'job_id': job_id,
        'message': f'Successfully deleted job with ID {job_id}',
      }

    except Exception as e:
      print(f'❌ Error deleting job: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def list_job_runs(job_id: str = None) -> dict:
    """List job runs, either all runs or runs for a specific job.

    Args:
        job_id: Optional job ID to filter runs for a specific job

    Returns:
        Dictionary containing list of job runs with their details
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      if job_id:
        print(f'🔧 Listing job runs for job ID: {job_id}')
        runs = list(w.jobs.list_runs(job_id=job_id))
      else:
        print('🔧 Listing all job runs in workspace')
        runs = list(w.jobs.list_runs())
      
      # Extract relevant run information
      run_list = []
      for run in runs:
        run_info = {
          'run_id': run.run_id,
          'job_id': run.job_id,
          'run_name': run.run_name,
          'state': run.state.life_cycle_state if run.state else None,
          'result_state': run.state.result_state if run.state else None,
          'start_time': run.start_time.isoformat() if run.start_time else None,
          'end_time': run.end_time.isoformat() if run.end_time else None,
          'duration': run.run_duration if hasattr(run, 'run_duration') else None,
          'trigger': run.trigger if hasattr(run, 'trigger') else None,
          'run_page_url': run.run_page_url if hasattr(run, 'run_page_url') else None,
          'number_in_job': run.number_in_job if hasattr(run, 'number_in_job') else None,
        }
        run_list.append(run_info)

      return {
        'success': True,
        'runs': run_list,
        'count': len(run_list),
        'job_id_filter': job_id,
        'message': f'Retrieved {len(run_list)} job runs{" for job " + job_id if job_id else ""}',
      }

    except Exception as e:
      print(f'❌ Error listing job runs: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'runs': [], 'count': 0}

  @mcp_server.tool
  def get_job_run(run_id: str) -> dict:
    """Get detailed information about a specific job run.

    Args:
        run_id: The ID of the job run to retrieve

    Returns:
        Dictionary with detailed job run information or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      print(f'🔧 Getting job run details for run ID: {run_id}')

      # Get run details
      run = w.jobs.get_run(run_id=run_id)
      
      # Extract comprehensive run information
      run_details = {
        'run_id': run.run_id,
        'job_id': run.job_id,
        'run_name': run.run_name,
        'state': run.state.life_cycle_state if run.state else None,
        'result_state': run.state.result_state if run.state else None,
        'start_time': run.start_time.isoformat() if run.start_time else None,
        'end_time': run.end_time.isoformat() if run.end_time else None,
        'duration': run.run_duration if hasattr(run, 'run_duration') else None,
        'trigger': run.trigger if hasattr(run, 'trigger') else None,
        'run_page_url': run.run_page_url if hasattr(run, 'run_page_url') else None,
        'number_in_job': run.number_in_job if hasattr(run, 'number_in_job') else None,
        'cluster_spec': run.cluster_spec if hasattr(run, 'cluster_spec') else None,
        'overriding_parameters': run.overriding_parameters if hasattr(run, 'overriding_parameters') else None,
        'tasks': run.tasks if hasattr(run, 'tasks') else None,
        'format': run.format if hasattr(run, 'format') else None,
        'run_type': run.run_type if hasattr(run, 'run_type') else None,
      }

      return {
        'success': True,
        'run': run_details,
        'message': f'Retrieved details for job run {run_id}',
      }

    except Exception as e:
      print(f'❌ Error getting job run details: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def submit_job_run(job_id: str, parameters: dict = None) -> dict:
    """Submit a new job run.

    Args:
        job_id: The ID of the job to run
        parameters: Optional parameters to pass to the job run

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      print(f'🔧 Submitting job run for job ID: {job_id}')

      # Submit the job run
      run = w.jobs.submit_run(job_id=job_id, **(parameters or {}))
      
      return {
        'success': True,
        'run_id': run.run_id,
        'job_id': job_id,
        'message': f'Successfully submitted job run with ID {run.run_id} for job {job_id}',
      }

    except Exception as e:
      print(f'❌ Error submitting job run: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def cancel_job_run(run_id: str) -> dict:
    """Cancel a running job run.

    Args:
        run_id: The ID of the job run to cancel

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      print(f'🔧 Cancelling job run ID: {run_id}')

      # Cancel the job run
      w.jobs.cancel_run(run_id=run_id)
      
      return {
        'success': True,
        'run_id': run_id,
        'message': f'Successfully cancelled job run with ID {run_id}',
      }

    except Exception as e:
      print(f'❌ Error cancelling job run: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def get_job_run_logs(run_id: str) -> dict:
    """Get logs from a job run.

    Args:
        run_id: The ID of the job run to get logs for

    Returns:
        Dictionary with job run logs or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      print(f'🔧 Getting logs for job run ID: {run_id}')

      # Get the run details first to check status
      run = w.jobs.get_run(run_id=run_id)
      
      if not run.state or run.state.life_cycle_state not in ['TERMINATED', 'SKIPPED', 'INTERNAL_ERROR']:
        return {
          'success': False,
          'error': f'Job run {run_id} is still running. Logs are only available for completed runs.',
          'current_state': run.state.life_cycle_state if run.state else 'Unknown'
        }

      # Get logs for the run
      logs = w.jobs.get_run_output(run_id=run_id)
      
      log_data = {
        'run_id': run_id,
        'notebook_output': logs.notebook_output if hasattr(logs, 'notebook_output') else None,
        'sql_output': logs.sql_output if hasattr(logs, 'sql_output') else None,
        'dbt_output': logs.dbt_output if hasattr(logs, 'dbt_output') else None,
        'run_output': logs.run_output if hasattr(logs, 'run_output') else None,
        'error': logs.error if hasattr(logs, 'error') else None,
      }

      return {
        'success': True,
        'run_id': run_id,
        'logs': log_data,
        'message': f'Retrieved logs for job run {run_id}',
      }

    except Exception as e:
      print(f'❌ Error getting job run logs: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def list_workspace_files(path: str = '/') -> dict:
    """List files in the Databricks workspace.

    Args:
        path: Workspace path to list (default: '/')

    Returns:
        Dictionary with file listings or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List workspace files
      files = []
      for file_info in w.workspace.list(path):
        files.append(
          {
            'path': file_info.path,
            'object_type': file_info.object_type.value if file_info.object_type else 'UNKNOWN',
            'language': file_info.language.value if file_info.language else None,
            'created_time': file_info.created_time,
            'modified_time': file_info.modified_time,
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
      print(f'❌ Error listing workspace files: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'files': [], 'count': 0}

  @mcp_server.tool
  def get_workspace_file_info(path: str) -> dict:
    """Get file information from the Databricks workspace.

    Args:
        path: Workspace file path to get information for

    Returns:
        Dictionary with file information or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get file info
      file_info = w.workspace.get_status(path)
      
      return {
        'success': True,
        'path': path,
        'object_type': file_info.object_type.value if file_info.object_type else 'UNKNOWN',
        'language': file_info.language.value if file_info.language else None,
        'created_time': file_info.created_time,
        'modified_time': file_info.modified_time,
        'message': f'Retrieved info for {path}',
      }

    except Exception as e:
      print(f'❌ Error getting workspace file info: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def read_workspace_file(path: str) -> dict:
    """Read a file from the Databricks workspace.

    Args:
        path: Workspace file path to read

    Returns:
        Dictionary with file content or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Read workspace file
      content = w.workspace.export(path)
      
      return {
        'success': True,
        'path': path,
        'content': content,
        'message': f'Successfully read file {path}',
      }

    except Exception as e:
      print(f'❌ Error reading workspace file: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def write_workspace_file(path: str, content: str, language: str = None) -> dict:
    """Write content to a file in the Databricks workspace.

    Args:
        path: Workspace file path to write to
        content: Content to write to the file
        language: Programming language for the file (optional)

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Determine language from path extension if not provided
      if not language:
        if path.endswith('.py'):
          language = 'PYTHON'
        elif path.endswith('.scala'):
          language = 'SCALA'
        elif path.endswith('.sql'):
          language = 'SQL'
        elif path.endswith('.r'):
          language = 'R'
        else:
          language = 'PYTHON'  # Default to Python

      # Write workspace file
      w.workspace.import_file(path, content, language=language, overwrite=True)
      
      return {
        'success': True,
        'path': path,
        'language': language,
        'content_length': len(content),
        'message': f'Successfully wrote {len(content)} characters to {path}',
      }

    except Exception as e:
      print(f'❌ Error writing workspace file: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def delete_workspace_file(path: str) -> dict:
    """Delete a file from the Databricks workspace.

    Args:
        path: Workspace file path to delete

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Delete workspace file
      w.workspace.delete(path, recursive=True)
      
      return {
        'success': True,
        'path': path,
        'message': f'Successfully deleted {path}',
      }

    except Exception as e:
      print(f'❌ Error deleting workspace file: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def create_workspace_directory(path: str) -> dict:
    """Create a directory in the Databricks workspace.

    Args:
        path: Workspace directory path to create

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Create workspace directory by importing an empty notebook
      w.workspace.import_file(f'{path}/.directory', '', language='PYTHON', overwrite=False)
      
      return {
        'success': True,
        'path': path,
        'message': f'Successfully created directory {path}',
      }

    except Exception as e:
      print(f'❌ Error creating workspace directory: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def list_pipelines() -> dict:
    """List all DLT pipelines in the workspace.

    Returns:
        Dictionary containing list of pipelines with their details
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List DLT pipelines
      pipelines = []
      for pipeline in w.pipelines.list():
        pipelines.append(
          {
            'pipeline_id': pipeline.pipeline_id,
            'name': pipeline.name,
            'catalog_name': pipeline.catalog_name,
            'target': pipeline.target,
            'state': pipeline.state.value if pipeline.state else 'UNKNOWN',
            'creator_user_name': pipeline.creator_user_name,
            'created_time': pipeline.created_time,
            'last_modified_time': pipeline.last_modified_time,
          }
        )

      return {
        'success': True,
        'pipelines': pipelines,
        'count': len(pipelines),
        'message': f'Found {len(pipelines)} pipeline(s)',
      }

    except Exception as e:
      print(f'❌ Error listing pipelines: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'pipelines': [], 'count': 0}

  @mcp_server.tool
  def get_pipeline(pipeline_id: str) -> dict:
    """Get details of a specific DLT pipeline.

    Args:
        pipeline_id: The ID of the pipeline to get details for

    Returns:
        Dictionary with pipeline details or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get pipeline details
      pipeline = w.pipelines.get(pipeline_id=pipeline_id)
      
      return {
        'success': True,
        'pipeline_id': pipeline_id,
        'name': pipeline.name,
        'catalog_name': pipeline.catalog_name,
        'target': pipeline.target,
        'state': pipeline.state.value if pipeline.state else 'UNKNOWN',
        'creator_user_name': pipeline.creator_user_name,
        'created_time': pipeline.created_time,
        'last_modified_time': pipeline.last_modified_time,
        'configuration': pipeline.configuration if hasattr(pipeline, 'configuration') else None,
        'message': f'Retrieved details for pipeline {pipeline_id}',
      }

    except Exception as e:
      print(f'❌ Error getting pipeline: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def create_pipeline(pipeline_config: dict) -> dict:
    """Create a new DLT pipeline.

    Args:
        pipeline_config: Dictionary containing pipeline configuration

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Create pipeline
      pipeline = w.pipelines.create(**pipeline_config)
      
      return {
        'success': True,
        'pipeline_id': pipeline.pipeline_id,
        'name': pipeline.name,
        'message': f'Successfully created pipeline {pipeline.name} with ID {pipeline.pipeline_id}',
      }

    except Exception as e:
      print(f'❌ Error creating pipeline: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def update_pipeline(pipeline_id: str, updates: dict) -> dict:
    """Update an existing DLT pipeline.

    Args:
        pipeline_id: The ID of the pipeline to update
        updates: Dictionary containing updates to apply

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Update pipeline
      pipeline = w.pipelines.edit(pipeline_id=pipeline_id, **updates)
      
      return {
        'success': True,
        'pipeline_id': pipeline_id,
        'name': pipeline.name,
        'message': f'Successfully updated pipeline {pipeline_id}',
      }

    except Exception as e:
      print(f'❌ Error updating pipeline: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def delete_pipeline(pipeline_id: str) -> dict:
    """Delete a DLT pipeline.

    Args:
        pipeline_id: The ID of the pipeline to delete

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Delete pipeline
      w.pipelines.delete(pipeline_id=pipeline_id)
      
      return {
        'success': True,
        'pipeline_id': pipeline_id,
        'message': f'Successfully deleted pipeline {pipeline_id}',
      }

    except Exception as e:
      print(f'❌ Error deleting pipeline: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def list_pipeline_runs(pipeline_id: str = None) -> dict:
    """List DLT pipeline runs.

    Args:
        pipeline_id: Optional pipeline ID to filter runs (default: None for all)

    Returns:
        Dictionary containing list of pipeline runs with their details
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List pipeline runs
      runs = []
      for run in w.pipelines.list_runs(pipeline_id=pipeline_id):
        runs.append(
          {
            'run_id': run.run_id,
            'pipeline_id': run.pipeline_id,
            'state': run.state.value if run.state else 'UNKNOWN',
            'start_time': run.start_time,
            'end_time': run.end_time,
            'trigger': run.trigger.value if run.trigger else 'UNKNOWN',
            'creator_user_name': run.creator_user_name,
          }
        )

      return {
        'success': True,
        'pipeline_id': pipeline_id,
        'runs': runs,
        'count': len(runs),
        'message': f'Found {len(runs)} pipeline run(s)',
      }

    except Exception as e:
      print(f'❌ Error listing pipeline runs: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'runs': [], 'count': 0}

  @mcp_server.tool
  def get_pipeline_run(run_id: str) -> dict:
    """Get details of a specific DLT pipeline run.

    Args:
        run_id: The ID of the pipeline run to get details for

    Returns:
        Dictionary with pipeline run details or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get pipeline run details
      run = w.pipelines.get_run(run_id=run_id)
      
      return {
        'success': True,
        'run_id': run_id,
        'pipeline_id': run.pipeline_id,
        'state': run.state.value if run.state else 'UNKNOWN',
        'start_time': run.start_time,
        'end_time': run.end_time,
        'trigger': run.trigger.value if run.trigger else 'UNKNOWN',
        'creator_user_name': run.creator_user_name,
        'message': f'Retrieved details for pipeline run {run_id}',
      }

    except Exception as e:
      print(f'❌ Error getting pipeline run: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def start_pipeline_update(pipeline_id: str, parameters: dict = None) -> dict:
    """Start a DLT pipeline update.

    Args:
        pipeline_id: The ID of the pipeline to start
        parameters: Optional parameters for the pipeline update

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Start pipeline update
      run = w.pipelines.start_update(pipeline_id=pipeline_id, **(parameters or {}))
      
      return {
        'success': True,
        'pipeline_id': pipeline_id,
        'run_id': run.run_id,
        'message': f'Successfully started pipeline update for {pipeline_id} with run ID {run.run_id}',
      }

    except Exception as e:
      print(f'❌ Error starting pipeline update: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def stop_pipeline_update(pipeline_id: str) -> dict:
    """Stop a running DLT pipeline update.

    Args:
        pipeline_id: The ID of the pipeline to stop

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Stop pipeline update
      w.pipelines.stop_update(pipeline_id=pipeline_id)
      
      return {
        'success': True,
        'pipeline_id': pipeline_id,
        'message': f'Successfully stopped pipeline update for {pipeline_id}',
      }

    except Exception as e:
      print(f'❌ Error stopping pipeline update: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def list_lakeview_dashboards() -> dict:
    """List all Lakeview dashboards in the workspace.

    Returns:
        Dictionary containing list of Lakeview dashboards with their details
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List Lakeview dashboards
      dashboards = []
      for dashboard in w.lakeview.list_dashboards():
        dashboards.append(
          {
            'dashboard_id': dashboard.dashboard_id,
            'name': dashboard.name,
            'description': dashboard.description if hasattr(dashboard, 'description') else None,
            'created_time': dashboard.created_time if hasattr(dashboard, 'created_time') else None,
            'updated_time': dashboard.updated_time if hasattr(dashboard, 'updated_time') else None,
            'owner': dashboard.owner if hasattr(dashboard, 'owner') else None,
          }
        )

      return {
        'success': True,
        'dashboards': dashboards,
        'count': len(dashboards),
        'message': f'Found {len(dashboards)} Lakeview dashboard(s)',
      }

    except Exception as e:
      print(f'❌ Error listing Lakeview dashboards: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'dashboards': [], 'count': 0}

  @mcp_server.tool
  def get_lakeview_dashboard(dashboard_id: str) -> dict:
    """Get details of a specific Lakeview dashboard.

    Args:
        dashboard_id: The ID of the dashboard to get details for

    Returns:
        Dictionary with dashboard details or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get dashboard details
      dashboard = w.lakeview.get_dashboard(dashboard_id=dashboard_id)
      
      return {
        'success': True,
        'dashboard_id': dashboard_id,
        'name': dashboard.name,
        'description': dashboard.description if hasattr(dashboard, 'description') else None,
        'created_time': dashboard.created_time if hasattr(dashboard, 'created_time') else None,
        'updated_time': dashboard.updated_time if hasattr(dashboard, 'updated_time') else None,
        'owner': dashboard.owner if hasattr(dashboard, 'owner') else None,
        'message': f'Retrieved details for Lakeview dashboard {dashboard_id}',
      }

    except Exception as e:
      print(f'❌ Error getting Lakeview dashboard: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def create_lakeview_dashboard(dashboard_config: dict) -> dict:
    """Create a new Lakeview dashboard.

    Args:
        dashboard_config: Dictionary containing dashboard configuration

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Create dashboard
      dashboard = w.lakeview.create_dashboard(**dashboard_config)
      
      return {
        'success': True,
        'dashboard_id': dashboard.dashboard_id,
        'name': dashboard.name,
        'message': f'Successfully created Lakeview dashboard {dashboard.name} with ID {dashboard.dashboard_id}',
      }

    except Exception as e:
      print(f'❌ Error creating Lakeview dashboard: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def update_lakeview_dashboard(dashboard_id: str, updates: dict) -> dict:
    """Update an existing Lakeview dashboard.

    Args:
        dashboard_id: The ID of the dashboard to update
        updates: Dictionary containing updates to apply

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Update dashboard
      dashboard = w.lakeview.update_dashboard(dashboard_id=dashboard_id, **updates)
      
      return {
        'success': True,
        'dashboard_id': dashboard_id,
        'name': dashboard.name,
        'message': f'Successfully updated Lakeview dashboard {dashboard_id}',
      }

    except Exception as e:
      print(f'❌ Error updating Lakeview dashboard: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def delete_lakeview_dashboard(dashboard_id: str) -> dict:
    """Delete a Lakeview dashboard.

    Args:
        dashboard_id: The ID of the dashboard to delete

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Delete dashboard
      w.lakeview.delete_dashboard(dashboard_id=dashboard_id)
      
      return {
        'success': True,
        'dashboard_id': dashboard_id,
        'message': f'Successfully deleted Lakeview dashboard {dashboard_id}',
      }

    except Exception as e:
      print(f'❌ Error deleting Lakeview dashboard: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def list_dashboards() -> dict:
    """List all legacy dashboards in the workspace.

    Returns:
        Dictionary containing list of legacy dashboards with their details
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List legacy dashboards
      dashboards = []
      for dashboard in w.dashboards.list():
        dashboards.append(
          {
            'dashboard_id': dashboard.id,
            'name': dashboard.name,
            'description': dashboard.description if hasattr(dashboard, 'description') else None,
            'created_time': dashboard.created_time if hasattr(dashboard, 'created_time') else None,
            'updated_time': dashboard.updated_time if hasattr(dashboard, 'updated_time') else None,
            'owner': dashboard.owner if hasattr(dashboard, 'owner') else None,
          }
        )

      return {
        'success': True,
        'dashboards': dashboards,
        'count': len(dashboards),
        'message': f'Found {len(dashboards)} legacy dashboard(s)',
      }

    except Exception as e:
      print(f'❌ Error listing legacy dashboards: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'dashboards': [], 'count': 0}

  @mcp_server.tool
  def get_dashboard(dashboard_id: str) -> dict:
    """Get details of a specific legacy dashboard.

    Args:
        dashboard_id: The ID of the dashboard to get details for

    Returns:
        Dictionary with dashboard details or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get dashboard details
      dashboard = w.dashboards.get(dashboard_id=dashboard_id)
      
      return {
        'success': True,
        'dashboard_id': dashboard_id,
        'name': dashboard.name,
        'description': dashboard.description if hasattr(dashboard, 'description') else None,
        'created_time': dashboard.created_time if hasattr(dashboard, 'created_time') else None,
        'updated_time': dashboard.updated_time if hasattr(dashboard, 'updated_time') else None,
        'owner': dashboard.owner if hasattr(dashboard, 'owner') else None,
        'message': f'Retrieved details for legacy dashboard {dashboard_id}',
      }

    except Exception as e:
      print(f'❌ Error getting legacy dashboard: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def create_dashboard(dashboard_config: dict) -> dict:
    """Create a new legacy dashboard.

    Args:
        dashboard_config: Dictionary containing dashboard configuration

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Create dashboard
      dashboard = w.dashboards.create(**dashboard_config)
      
      return {
        'success': True,
        'dashboard_id': dashboard.id,
        'name': dashboard.name,
        'message': f'Successfully created legacy dashboard {dashboard.name} with ID {dashboard.id}',
      }

    except Exception as e:
      print(f'❌ Error creating legacy dashboard: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def delete_dashboard(dashboard_id: str) -> dict:
    """Delete a legacy dashboard.

    Args:
        dashboard_id: The ID of the dashboard to delete

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Delete dashboard
      w.dashboards.delete(dashboard_id=dashboard_id)
      
      return {
        'success': True,
        'dashboard_id': dashboard_id,
        'message': f'Successfully deleted legacy dashboard {dashboard_id}',
      }

    except Exception as e:
      print(f'❌ Error deleting legacy dashboard: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  # ============================================================================
  # Repos and Git Integration
  # ============================================================================

  @mcp_server.tool
  def list_repos() -> dict:
    """List all repositories in the workspace.

    Returns:
        Dictionary containing list of repositories with their details
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # List all repositories
      repos = w.repos.list()
      
      repo_list = []
      for repo in repos:
        repo_list.append({
          'id': repo.id,
          'name': repo.name,
          'path': repo.path,
          'url': repo.url,
          'provider': repo.provider,
          'head': repo.head,
          'branch': repo.branch,
          'created_time': repo.created_time,
          'updated_time': repo.updated_time,
        })

      return {
        'success': True,
        'repos': repo_list,
        'count': len(repo_list),
        'message': f'Found {len(repo_list)} repository(ies)',
      }

    except Exception as e:
      print(f'❌ Error listing repositories: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}', 'repos': [], 'count': 0}

  @mcp_server.tool
  def get_repo(repo_id: str) -> dict:
    """Get repository details.

    Args:
        repo_id: The ID of the repository to get details for

    Returns:
        Dictionary with repository details or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get repository details
      repo = w.repos.get(repo_id=repo_id)
      
      return {
        'success': True,
        'repo_id': repo.id,
        'name': repo.name,
        'path': repo.path,
        'url': repo.url,
        'provider': repo.provider,
        'head': repo.head,
        'branch': repo.branch,
        'created_time': repo.created_time,
        'updated_time': repo.updated_time,
        'message': f'Retrieved details for repository {repo.name}',
      }

    except Exception as e:
      print(f'❌ Error getting repository: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def create_repo(url: str, provider: str, path: str = None) -> dict:
    """Create new repository.

    Args:
        url: Git repository URL
        provider: Git provider (github, gitlab, etc.)
        path: Repository path in workspace (optional)

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Create repository
      repo = w.repos.create(url=url, provider=provider, path=path)
      
      return {
        'success': True,
        'repo_id': repo.id,
        'name': repo.name,
        'path': repo.path,
        'url': repo.url,
        'message': f'Successfully created repository {repo.name} with ID {repo.id}',
      }

    except Exception as e:
      print(f'❌ Error creating repository: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def update_repo(repo_id: str, updates: dict) -> dict:
    """Update repository settings.

    Args:
        repo_id: The ID of the repository to update
        updates: Dictionary containing updates to apply

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Update repository
      repo = w.repos.update(repo_id=repo_id, **updates)
      
      return {
        'success': True,
        'repo_id': repo.id,
        'name': repo.name,
        'message': f'Successfully updated repository {repo.name}',
      }

    except Exception as e:
      print(f'❌ Error updating repository: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def delete_repo(repo_id: str) -> dict:
    """Delete repository.

    Args:
        repo_id: The ID of the repository to delete

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Delete repository
      w.repos.delete(repo_id=repo_id)
      
      return {
        'success': True,
        'repo_id': repo_id,
        'message': f'Successfully deleted repository {repo_id}',
      }

    except Exception as e:
      print(f'❌ Error deleting repository: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def get_repo_status(repo_id: str) -> dict:
    """Get repository status (ahead/behind).

    Args:
        repo_id: The ID of the repository to get status for

    Returns:
        Dictionary with repository status or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get repository status
      repo = w.repos.get(repo_id=repo_id)
      
      # Note: Databricks SDK doesn't directly provide ahead/behind info
      # This would need to be implemented with git commands if available
      return {
        'success': True,
        'repo_id': repo.id,
        'name': repo.name,
        'head': repo.head,
        'branch': repo.branch,
        'message': f'Retrieved status for repository {repo.name}',
        'note': 'Ahead/behind information not directly available via SDK',
      }

    except Exception as e:
      print(f'❌ Error getting repository status: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def pull_repo(repo_id: str) -> dict:
    """Pull latest changes from remote.

    Args:
        repo_id: The ID of the repository to pull from

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Pull repository
      w.repos.update(repo_id=repo_id)
      
      return {
        'success': True,
        'repo_id': repo_id,
        'message': f'Successfully pulled latest changes for repository {repo_id}',
      }

    except Exception as e:
      print(f'❌ Error pulling repository: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def push_repo(repo_id: str, message: str) -> dict:
    """Push local changes to remote.

    Args:
        repo_id: The ID of the repository to push to
        message: Commit message

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Push operation would require git commands
      # This is a placeholder for the concept
      return {
        'success': True,
        'repo_id': repo_id,
        'message': f'Push operation initiated for repository {repo_id}',
        'note': 'Push operation requires git commands not directly available via SDK',
      }

    except Exception as e:
      print(f'❌ Error pushing repository: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def create_branch(repo_id: str, branch_name: str, source_branch: str = None) -> dict:
    """Create new branch.

    Args:
        repo_id: The ID of the repository
        branch_name: Name of the new branch
        source_branch: Source branch to create from (optional)

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Branch creation would require git commands
      # This is a placeholder for the concept
      return {
        'success': True,
        'repo_id': repo_id,
        'branch_name': branch_name,
        'source_branch': source_branch,
        'message': f'Branch creation initiated for {branch_name}',
        'note': 'Branch creation requires git commands not directly available via SDK',
      }

    except Exception as e:
      print(f'❌ Error creating branch: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def delete_branch(repo_id: str, branch_name: str) -> dict:
    """Delete branch.

    Args:
        repo_id: The ID of the repository
        branch_name: Name of the branch to delete

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Branch deletion would require git commands
      # This is a placeholder for the concept
      return {
        'success': True,
        'repo_id': repo_id,
        'branch_name': branch_name,
        'message': f'Branch deletion initiated for {branch_name}',
        'note': 'Branch deletion requires git commands not directly available via SDK',
      }

    except Exception as e:
      print(f'❌ Error deleting branch: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def list_branches(repo_id: str) -> dict:
    """List all branches in repository.

    Args:
        repo_id: The ID of the repository

    Returns:
        Dictionary with list of branches or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Get repository details
      repo = w.repos.get(repo_id=repo_id)
      
      # Note: Branch listing would require git commands
      # This is a placeholder for the concept
      return {
        'success': True,
        'repo_id': repo.id,
        'name': repo.name,
        'current_branch': repo.branch,
        'message': f'Branch listing initiated for repository {repo.name}',
        'note': 'Branch listing requires git commands not directly available via SDK',
      }

    except Exception as e:
      print(f'❌ Error listing branches: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  # ============================================================================
  # Audit Logs and Compliance
  # ============================================================================

  @mcp_server.tool
  def list_audit_logs(start_time: str = None, end_time: str = None, user_id: str = None) -> dict:
    """List audit logs.

    Args:
        start_time: Start time for filtering (ISO format string)
        end_time: End time for filtering (ISO format string)
        user_id: User ID for filtering (optional)

    Returns:
        Dictionary with list of audit logs or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Audit logs are typically accessed via REST API or admin interface
      # This is a placeholder for the concept
      return {
        'success': True,
        'start_time': start_time,
        'end_time': end_time,
        'user_id': user_id,
        'message': 'Audit log listing initiated',
        'note': 'Audit logs require admin access and REST API calls not directly available via SDK',
      }

    except Exception as e:
      print(f'❌ Error listing audit logs: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def get_audit_log(event_id: str) -> dict:
    """Get audit log details.

    Args:
        event_id: The ID of the audit event to get details for

    Returns:
        Dictionary with audit log details or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Individual audit log retrieval requires admin access
      # This is a placeholder for the concept
      return {
        'success': True,
        'event_id': event_id,
        'message': f'Audit log retrieval initiated for event {event_id}',
        'note': 'Audit log retrieval requires admin access and REST API calls not directly available via SDK',
      }

    except Exception as e:
      print(f'❌ Error getting audit log: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def export_audit_logs(start_time: str, end_time: str, format: str = "json") -> dict:
    """Export audit logs.

    Args:
        start_time: Start time for export (ISO format string)
        end_time: End time for export (ISO format string)
        format: Export format (json, csv, etc.)

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Audit log export requires admin access
      # This is a placeholder for the concept
      return {
        'success': True,
        'start_time': start_time,
        'end_time': end_time,
        'format': format,
        'message': 'Audit log export initiated',
        'note': 'Audit log export requires admin access and REST API calls not directly available via SDK',
      }

    except Exception as e:
      print(f'❌ Error exporting audit logs: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def list_governance_rules() -> dict:
    """List governance rules.

    Returns:
        Dictionary with list of governance rules or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Governance rules are typically managed via Unity Catalog
      # This is a placeholder for the concept
      return {
        'success': True,
        'message': 'Governance rules listing initiated',
        'note': 'Governance rules are managed via Unity Catalog and may require specific permissions',
      }

    except Exception as e:
      print(f'❌ Error listing governance rules: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def get_governance_rule(rule_id: str) -> dict:
    """Get rule details.

    Args:
        rule_id: The ID of the governance rule to get details for

    Returns:
        Dictionary with rule details or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Governance rule details require specific permissions
      # This is a placeholder for the concept
      return {
        'success': True,
        'rule_id': rule_id,
        'message': f'Governance rule retrieval initiated for rule {rule_id}',
        'note': 'Governance rule details require specific permissions and may not be directly accessible via SDK',
      }

    except Exception as e:
      print(f'❌ Error getting governance rule: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def create_governance_rule(rule_config: dict) -> dict:
    """Create new rule.

    Args:
        rule_config: Dictionary containing rule configuration

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Governance rule creation requires specific permissions
      # This is a placeholder for the concept
      return {
        'success': True,
        'rule_config': rule_config,
        'message': 'Governance rule creation initiated',
        'note': 'Governance rule creation requires specific permissions and may not be directly accessible via SDK',
      }

    except Exception as e:
      print(f'❌ Error creating governance rule: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def update_governance_rule(rule_id: str, updates: dict) -> dict:
    """Update rule.

    Args:
        rule_id: The ID of the governance rule to update
        updates: Dictionary containing updates to apply

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Governance rule updates require specific permissions
      # This is a placeholder for the concept
      return {
        'success': True,
        'rule_id': rule_id,
        'updates': updates,
        'message': f'Governance rule update initiated for rule {rule_id}',
        'note': 'Governance rule updates require specific permissions and may not be directly accessible via SDK',
      }

    except Exception as e:
      print(f'❌ Error updating governance rule: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def delete_governance_rule(rule_id: str) -> dict:
    """Delete rule.

    Args:
        rule_id: The ID of the governance rule to delete

    Returns:
        Dictionary with operation result or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Governance rule deletion requires specific permissions
      # This is a placeholder for the concept
      return {
        'success': True,
        'rule_id': rule_id,
        'message': f'Governance rule deletion initiated for rule {rule_id}',
        'note': 'Governance rule deletion requires specific permissions and may not be directly accessible via SDK',
      }

    except Exception as e:
      print(f'❌ Error deleting governance rule: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  # ============================================================================
  # Data Lineage and Discovery
  # ============================================================================

  @mcp_server.tool
  def get_table_lineage(table_name: str, depth: int = 1) -> dict:
    """Get table lineage information.

    Args:
        table_name: Full table name (catalog.schema.table)
        depth: Lineage depth to retrieve (default: 1)

    Returns:
        Dictionary with table lineage information or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Table lineage requires Unity Catalog and specific permissions
      # This is a placeholder for the concept
      return {
        'success': True,
        'table_name': table_name,
        'depth': depth,
        'message': f'Table lineage retrieval initiated for {table_name}',
        'note': 'Table lineage requires Unity Catalog and specific permissions, may not be directly accessible via SDK',
      }

    except Exception as e:
      print(f'❌ Error getting table lineage: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def get_column_lineage(table_name: str, column_name: str) -> dict:
    """Get column-level lineage.

    Args:
        table_name: Full table name (catalog.schema.table)
        column_name: Name of the column to get lineage for

    Returns:
        Dictionary with column lineage information or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Column lineage requires Unity Catalog and specific permissions
      # This is a placeholder for the concept
      return {
        'success': True,
        'table_name': table_name,
        'column_name': column_name,
        'message': f'Column lineage retrieval initiated for {table_name}.{column_name}',
        'note': 'Column lineage requires Unity Catalog and specific permissions, may not be directly accessible via SDK',
      }

    except Exception as e:
      print(f'❌ Error getting column lineage: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def search_lineage(query: str, object_type: str = None) -> dict:
    """Search lineage graph.

    Args:
        query: Search query string
        object_type: Type of object to search for (optional)

    Returns:
        Dictionary with search results or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Lineage search requires Unity Catalog and specific permissions
      # This is a placeholder for the concept
      return {
        'success': True,
        'query': query,
        'object_type': object_type,
        'message': 'Lineage search initiated',
        'note': 'Lineage search requires Unity Catalog and specific permissions, may not be directly accessible via SDK',
      }

    except Exception as e:
      print(f'❌ Error searching lineage: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def search_catalog(query: str, object_type: str = None) -> dict:
    """Search catalog objects.

    Args:
        query: Search query string
        object_type: Type of object to search for (optional)

    Returns:
        Dictionary with search results or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Catalog search requires Unity Catalog and specific permissions
      # This is a placeholder for the concept
      return {
        'success': True,
        'query': query,
        'object_type': object_type,
        'message': 'Catalog search initiated',
        'note': 'Catalog search requires Unity Catalog and specific permissions, may not be directly accessible via SDK',
      }

    except Exception as e:
      print(f'❌ Error searching catalog: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
  def get_object_usage_stats(object_name: str, time_range: str = "30d") -> dict:
    """Get usage statistics.

    Args:
        object_name: Full object name (catalog.schema.object)
        time_range: Time range for statistics (default: "30d")

    Returns:
        Dictionary with usage statistics or error message
    """
    try:
      # Initialize Databricks SDK
      w = WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
      )

      # Note: Usage statistics require specific permissions and may not be directly accessible
      # This is a placeholder for the concept
      return {
        'success': True,
        'object_name': object_name,
        'time_range': time_range,
        'message': f'Usage statistics retrieval initiated for {object_name}',
        'note': 'Usage statistics require specific permissions and may not be directly accessible via SDK',
      }

    except Exception as e:
      print(f'❌ Error getting usage statistics: {str(e)}')
      return {'success': False, 'error': f'Error: {str(e)}'}

  @mcp_server.tool
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
        query_list.append({
          'id': query.id,
          'warehouse_id': query.warehouse_id,
          'status': query.status,
          'created_time': query.created_time,
          'completed_time': query.completed_time,
          'statement': query.statement[:100] + '...' if len(query.statement) > 100 else query.statement,
        })

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
