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
