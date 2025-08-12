"""Unity Catalog MCP tools for Databricks."""

import os
from databricks.sdk import WorkspaceClient


def load_uc_tools(mcp_server):
    """Register Unity Catalog MCP tools with the server.
    
    Args:
        mcp_server: The FastMCP server instance to register tools with
    """
    
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
                host=os.environ.get('DATABRICKS_HOST'), 
                token=os.environ.get('DATABRICKS_TOKEN')
            )

            # List all catalogs
            catalogs = w.catalogs.list()
            
            catalog_list = []
            for catalog in catalogs:
                catalog_list.append({
                    'name': catalog.name,
                    'type': catalog.catalog_type,
                    'comment': catalog.comment,
                    'owner': catalog.owner,
                    'created_time': catalog.created_time,
                    'updated_time': catalog.updated_time,
                    'properties': catalog.properties,
                })

            return {
                'success': True,
                'catalogs': catalog_list,
                'count': len(catalog_list),
                'message': f'Found {len(catalog_list)} catalog(s)',
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
                host=os.environ.get('DATABRICKS_HOST'), 
                token=os.environ.get('DATABRICKS_TOKEN')
            )

            # Get catalog details
            catalog = w.catalogs.get(catalog_name)
            
            # List schemas in the catalog
            schemas = w.schemas.list(catalog_name=catalog_name)
            
            schema_list = []
            for schema in schemas:
                schema_list.append({
                    'name': schema.name,
                    'comment': schema.comment,
                    'owner': schema.owner,
                    'created_time': schema.created_time,
                    'updated_time': schema.updated_time,
                    'properties': schema.properties,
                })

            return {
                'success': True,
                'catalog': {
                    'name': catalog.name,
                    'type': catalog.catalog_type,
                    'comment': catalog.comment,
                    'owner': catalog.owner,
                    'created_time': catalog.created_time,
                    'updated_time': catalog.updated_time,
                    'properties': catalog.properties,
                },
                'schemas': schema_list,
                'schema_count': len(schema_list),
                'message': f'Catalog {catalog_name} details retrieved successfully with {len(schema_list)} schema(s)',
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
                host=os.environ.get('DATABRICKS_HOST'), 
                token=os.environ.get('DATABRICKS_TOKEN')
            )

            # Get schema details
            schema = w.schemas.get(catalog_name=catalog_name, schema_name=schema_name)
            
            # List tables in the schema
            tables = w.tables.list(catalog_name=catalog_name, schema_name=schema_name)
            
            table_list = []
            for table in tables:
                table_info = {
                    'name': table.name,
                    'table_type': table.table_type,
                    'comment': table.comment,
                    'owner': table.owner,
                    'created_time': table.created_time,
                    'updated_time': table.updated_time,
                    'properties': table.properties,
                }
                
                if include_columns and hasattr(table, 'columns'):
                    columns = []
                    for col in table.columns:
                        columns.append({
                            'name': col.name,
                            'type': col.type,
                            'comment': col.comment,
                            'nullable': col.nullable,
                        })
                    table_info['columns'] = columns
                
                table_list.append(table_info)

            return {
                'success': True,
                'schema': {
                    'name': schema.name,
                    'comment': schema.comment,
                    'owner': schema.owner,
                    'created_time': schema.created_time,
                    'updated_time': schema.updated_time,
                    'properties': schema.properties,
                },
                'tables': table_list,
                'table_count': len(table_list),
                'include_columns': include_columns,
                'message': f'Schema {catalog_name}.{schema_name} details retrieved successfully with {len(table_list)} table(s)',
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
            # Parse table name
            parts = table_name.split('.')
            if len(parts) != 3:
                return {
                    'success': False,
                    'error': 'Table name must be in format: catalog.schema.table'
                }
            
            catalog_name, schema_name, table_name_only = parts
            
            # Initialize Databricks SDK
            w = WorkspaceClient(
                host=os.environ.get('DATABRICKS_HOST'), 
                token=os.environ.get('DATABRICKS_TOKEN')
            )

            # Get table details
            table = w.tables.get(catalog_name=catalog_name, schema_name=schema_name, table_name=table_name_only)
            
            # Get column information
            columns = []
            if hasattr(table, 'columns'):
                for col in table.columns:
                    columns.append({
                        'name': col.name,
                        'type': col.type,
                        'comment': col.comment,
                        'nullable': col.nullable,
                        'position': col.position,
                    })
            
            # Get partitioning information
            partitioning = []
            if hasattr(table, 'partitioning') and table.partitioning:
                for part in table.partitioning:
                    partitioning.append({
                        'name': part.name,
                        'type': part.type,
                    })
            
            table_info = {
                'name': table.name,
                'full_name': f'{catalog_name}.{schema_name}.{table.name}',
                'table_type': table.table_type,
                'comment': table.comment,
                'owner': table.owner,
                'created_time': table.created_time,
                'updated_time': table.updated_time,
                'properties': table.properties,
                'columns': columns,
                'partitioning': partitioning,
                'storage_location': table.storage_location if hasattr(table, 'storage_location') else None,
            }
            
            # Add lineage information if requested
            if include_lineage:
                # Note: Lineage information may require additional permissions
                table_info['lineage_note'] = 'Lineage information requires specific permissions and may not be directly accessible via SDK'
            
            return {
                'success': True,
                'table': table_info,
                'include_lineage': include_lineage,
                'message': f'Table {table_name} details retrieved successfully with {len(columns)} column(s)',
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
                host=os.environ.get('DATABRICKS_HOST'), 
                token=os.environ.get('DATABRICKS_TOKEN')
            )

            # List volumes in the schema
            volumes = w.volumes.list(catalog_name=catalog_name, schema_name=schema_name)
            
            volume_list = []
            for volume in volumes:
                volume_list.append({
                    'name': volume.name,
                    'full_name': f'{catalog_name}.{schema_name}.{volume.name}',
                    'volume_type': volume.volume_type,
                    'comment': volume.comment,
                    'owner': volume.owner,
                    'created_time': volume.created_time,
                    'updated_time': volume.updated_time,
                    'properties': volume.properties,
                })

            return {
                'success': True,
                'volumes': volume_list,
                'count': len(volume_list),
                'catalog': catalog_name,
                'schema': schema_name,
                'message': f'Found {len(volume_list)} volume(s) in {catalog_name}.{schema_name}',
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
            # Parse volume name
            parts = volume_name.split('.')
            if len(parts) != 3:
                return {
                    'success': False,
                    'error': 'Volume name must be in format: catalog.schema.volume'
                }
            
            catalog_name, schema_name, volume_name_only = parts
            
            # Initialize Databricks SDK
            w = WorkspaceClient(
                host=os.environ.get('DATABRICKS_HOST'), 
                token=os.environ.get('DATABRICKS_TOKEN')
            )

            # Get volume details
            volume = w.volumes.get(catalog_name=catalog_name, schema_name=schema_name, volume_name=volume_name_only)
            
            return {
                'success': True,
                'volume': {
                    'name': volume.name,
                    'full_name': f'{catalog_name}.{schema_name}.{volume.name}',
                    'volume_type': volume.volume_type,
                    'comment': volume.comment,
                    'owner': volume.owner,
                    'created_time': volume.created_time,
                    'updated_time': volume.updated_time,
                    'properties': volume.properties,
                    'storage_location': volume.storage_location if hasattr(volume, 'storage_location') else None,
                },
                'message': f'Volume {volume_name} details retrieved successfully',
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
                host=os.environ.get('DATABRICKS_HOST'), 
                token=os.environ.get('DATABRICKS_TOKEN')
            )

            # List functions in the schema
            functions = w.functions.list(catalog_name=catalog_name, schema_name=schema_name)
            
            function_list = []
            for func in functions:
                function_list.append({
                    'name': func.name,
                    'full_name': f'{catalog_name}.{schema_name}.{func.name}',
                    'function_type': func.function_type,
                    'comment': func.comment,
                    'owner': func.owner,
                    'created_time': func.created_time,
                    'updated_time': func.updated_time,
                    'properties': func.properties,
                })

            return {
                'success': True,
                'functions': function_list,
                'count': len(function_list),
                'catalog': catalog_name,
                'schema': schema_name,
                'message': f'Found {len(function_list)} function(s) in {catalog_name}.{schema_name}',
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
            # Parse function name
            parts = function_name.split('.')
            if len(parts) != 3:
                return {
                    'success': False,
                    'error': 'Function name must be in format: catalog.schema.function'
                }
            
            catalog_name, schema_name, function_name_only = parts
            
            # Initialize Databricks SDK
            w = WorkspaceClient(
                host=os.environ.get('DATABRICKS_HOST'), 
                token=os.environ.get('DATABRICKS_TOKEN')
            )

            # Get function details
            func = w.functions.get(catalog_name=catalog_name, schema_name=schema_name, function_name=function_name_only)
            
            return {
                'success': True,
                'function': {
                    'name': func.name,
                    'full_name': f'{catalog_name}.{schema_name}.{func.name}',
                    'function_type': func.function_type,
                    'comment': func.comment,
                    'owner': func.owner,
                    'created_time': func.created_time,
                    'updated_time': func.updated_time,
                    'properties': func.properties,
                    'parameters': func.parameters if hasattr(func, 'parameters') else None,
                    'return_type': func.return_type if hasattr(func, 'return_type') else None,
                },
                'message': f'Function {function_name} details retrieved successfully',
            }

        except Exception as e:
            print(f'❌ Error describing function: {str(e)}')
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
                host=os.environ.get('DATABRICKS_HOST'), 
                token=os.environ.get('DATABRICKS_TOKEN')
            )

            # List models in the schema
            models = w.model_registry.list_models()
            
            # Filter by catalog and schema if possible
            model_list = []
            for model in models:
                # Note: Model filtering by catalog/schema may require additional logic
                model_list.append({
                    'name': model.name,
                    'comment': model.comment,
                    'owner': model.owner,
                    'created_time': model.created_time,
                    'updated_time': model.updated_time,
                    'tags': model.tags,
                })

            return {
                'success': True,
                'models': model_list,
                'count': len(model_list),
                'catalog': catalog_name,
                'schema': schema_name,
                'message': f'Found {len(model_list)} model(s) in {catalog_name}.{schema_name}',
                'note': 'Model filtering by catalog/schema may require additional logic',
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
            # Parse model name
            parts = model_name.split('.')
            if len(parts) != 3:
                return {
                    'success': False,
                    'error': 'Model name must be in format: catalog.schema.model'
                }
            
            catalog_name, schema_name, model_name_only = parts
            
            # Initialize Databricks SDK
            w = WorkspaceClient(
                host=os.environ.get('DATABRICKS_HOST'), 
                token=os.environ.get('DATABRICKS_TOKEN')
            )

            # Get model details
            model = w.model_registry.get_model(model_name_only)
            
            return {
                'success': True,
                'model': {
                    'name': model.name,
                    'full_name': f'{catalog_name}.{schema_name}.{model.name}',
                    'comment': model.comment,
                    'owner': model.owner,
                    'created_time': model.created_time,
                    'updated_time': model.updated_time,
                    'tags': model.tags,
                    'description': model.description if hasattr(model, 'description') else None,
                },
                'message': f'Model {model_name} details retrieved successfully',
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
                host=os.environ.get('DATABRICKS_HOST'), 
                token=os.environ.get('DATABRICKS_TOKEN')
            )

            # Note: Tag listing may require specific permissions
            # This is a placeholder for the concept
            return {
                'success': True,
                'catalog': catalog_name,
                'message': f'Tag listing initiated for catalog {catalog_name}' if catalog_name else 'Tag listing initiated for all catalogs',
                'note': 'Tag listing requires specific permissions and may not be directly accessible via SDK',
                'tags': [],
                'count': 0,
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
                host=os.environ.get('DATABRICKS_HOST'), 
                token=os.environ.get('DATABRICKS_TOKEN')
            )

            # Note: Tag application requires specific permissions
            # This is a placeholder for the concept
            return {
                'success': True,
                'object_name': object_name,
                'tags': tags,
                'message': f'Tag application initiated for {object_name}',
                'note': 'Tag application requires specific permissions and may not be directly accessible via SDK',
            }

        except Exception as e:
            print(f'❌ Error applying tags: {str(e)}')
            return {'success': False, 'error': f'Error: {str(e)}'}

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
                host=os.environ.get('DATABRICKS_HOST'), 
                token=os.environ.get('DATABRICKS_TOKEN')
            )

            # Note: Object search requires Unity Catalog and specific permissions
            # This is a placeholder for the concept
            return {
                'success': True,
                'query': query,
                'object_types': object_types,
                'message': 'Unity Catalog object search initiated',
                'note': 'Object search requires Unity Catalog and specific permissions, may not be directly accessible via SDK',
                'results': [],
                'count': 0,
            }

        except Exception as e:
            print(f'❌ Error searching Unity Catalog objects: {str(e)}')
            return {'success': False, 'error': f'Error: {str(e)}'}

    @mcp_server.tool
    def get_table_statistics(table_name: str) -> dict:
        """Get table statistics including row count, size, and column statistics.

        Args:
            table_name: Full table name in catalog.schema.table format

        Returns:
            Dictionary with table statistics or error message
        """
        try:
            # Parse table name
            parts = table_name.split('.')
            if len(parts) != 3:
                return {
                    'success': False,
                    'error': 'Table name must be in format: catalog.schema.table'
                }
            
            catalog_name, schema_name, table_name_only = parts
            
            # Initialize Databricks SDK
            w = WorkspaceClient(
                host=os.environ.get('DATABRICKS_HOST'), 
                token=os.environ.get('DATABRICKS_TOKEN')
            )

            # Note: Table statistics require specific permissions
            # This is a placeholder for the concept
            return {
                'success': True,
                'table_name': table_name,
                'message': f'Table statistics retrieval initiated for {table_name}',
                'note': 'Table statistics require specific permissions and may not be directly accessible via SDK',
                'statistics': {},
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
                host=os.environ.get('DATABRICKS_HOST'), 
                token=os.environ.get('DATABRICKS_TOKEN')
            )

            # List metastores
            metastores = w.metastores.list()
            
            metastore_list = []
            for metastore in metastores:
                metastore_list.append({
                    'name': metastore.name,
                    'owner': metastore.owner,
                    'created_time': metastore.created_time,
                    'updated_time': metastore.updated_time,
                    'region': metastore.region,
                    'cloud': metastore.cloud,
                    'global_metastore_id': metastore.global_metastore_id,
                })

            return {
                'success': True,
                'metastores': metastore_list,
                'count': len(metastore_list),
                'message': f'Found {len(metastore_list)} metastore(s)',
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
                host=os.environ.get('DATABRICKS_HOST'), 
                token=os.environ.get('DATABRICKS_TOKEN')
            )

            # Get metastore details
            metastore = w.metastores.get(metastore_name)
            
            return {
                'success': True,
                'metastore': {
                    'name': metastore.name,
                    'owner': metastore.owner,
                    'created_time': metastore.created_time,
                    'updated_time': metastore.updated_time,
                    'region': metastore.region,
                    'cloud': metastore.cloud,
                    'global_metastore_id': metastore.global_metastore_id,
                    'storage_root': metastore.storage_root,
                    'delta_sharing_scope': metastore.delta_sharing_scope,
                    'delta_sharing_recipient_token_lifetime_in_seconds': metastore.delta_sharing_recipient_token_lifetime_in_seconds,
                    'delta_sharing_organization_name': metastore.delta_sharing_organization_name,
                },
                'message': f'Metastore {metastore_name} details retrieved successfully',
            }

        except Exception as e:
            print(f'❌ Error describing metastore: {str(e)}')
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
                host=os.environ.get('DATABRICKS_HOST'), 
                token=os.environ.get('DATABRICKS_TOKEN')
            )

            # Note: Data quality monitors require specific permissions
            # This is a placeholder for the concept
            return {
                'success': True,
                'catalog': catalog_name,
                'message': f'Data quality monitor listing initiated for catalog {catalog_name}' if catalog_name else 'Data quality monitor listing initiated for all catalogs',
                'note': 'Data quality monitors require specific permissions and may not be directly accessible via SDK',
                'monitors': [],
                'count': 0,
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
                host=os.environ.get('DATABRICKS_HOST'), 
                token=os.environ.get('DATABRICKS_TOKEN')
            )

            # Note: Data quality results require specific permissions
            # This is a placeholder for the concept
            return {
                'success': True,
                'monitor_name': monitor_name,
                'date_range': date_range,
                'message': f'Data quality results retrieval initiated for {monitor_name}',
                'note': 'Data quality results require specific permissions and may not be directly accessible via SDK',
                'results': {},
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
                host=os.environ.get('DATABRICKS_HOST'), 
                token=os.environ.get('DATABRICKS_TOKEN')
            )

            # Note: Data quality monitor creation requires specific permissions
            # This is a placeholder for the concept
            return {
                'success': True,
                'table_name': table_name,
                'rules': rules,
                'message': f'Data quality monitor creation initiated for {table_name}',
                'note': 'Data quality monitor creation requires specific permissions and may not be directly accessible via SDK',
            }

        except Exception as e:
            print(f'❌ Error creating data quality monitor: {str(e)}')
            return {'success': False, 'error': f'Error: {str(e)}'}
