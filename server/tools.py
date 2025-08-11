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
