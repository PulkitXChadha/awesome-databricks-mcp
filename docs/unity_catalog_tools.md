# Unity Catalog Tools Documentation

This document provides comprehensive information about all Unity Catalog tools available in the Databricks MCP server.

## Overview

The Unity Catalog tools provide comprehensive access to Databricks Unity Catalog features, enabling AI assistants to discover, explore, and manage data assets programmatically. These tools cover all major Unity Catalog object types and operations.

## Core Unity Catalog Tools

### 1. Catalog Management

#### `describe_uc_catalog(catalog_name: str)`
Provides detailed information about a specific catalog and its schemas.

**Parameters:**
- `catalog_name`: Name of the catalog to describe

**Returns:**
- Catalog details (name, type, comment, owner, etc.)
- List of schemas in the catalog
- Schema count

**Example:**
```python
# Describe a specific catalog
result = describe_uc_catalog("hive_metastore")
# Returns: {"success": true, "catalog": {...}, "schemas": [...], "schema_count": 10}
```

### 2. Schema Management

#### `describe_uc_schema(catalog_name: str, schema_name: str, include_columns: bool = False)`
Describes a specific schema within a catalog, optionally including detailed table information.

**Parameters:**
- `catalog_name`: Name of the catalog
- `schema_name`: Name of the schema
- `include_columns`: Whether to include detailed column information (default: False)

**Returns:**
- Schema details (name, comment, owner, etc.)
- List of tables in the schema
- Table count
- Optional column details if requested

**Example:**
```python
# Describe schema with column details
result = describe_uc_schema("hive_metastore", "default", include_columns=True)
# Returns: {"success": true, "schema": {...}, "tables": [...], "table_count": 15}
```

### 3. Table Management

#### `describe_uc_table(table_name: str, include_lineage: bool = False)`
Provides detailed table structure and metadata, optionally including lineage information.

**Parameters:**
- `table_name`: Full table name in `catalog.schema.table` format
- `include_lineage`: Whether to include lineage information (default: False)

**Returns:**
- Complete table metadata (name, type, format, comment, owner, etc.)
- Column information with types and properties
- Partition information
- Storage location and credentials
- Optional lineage information

**Example:**
```python
# Describe table with lineage
result = describe_uc_table("hive_metastore.default.users", include_lineage=True)
# Returns: {"success": true, "table": {...}, "columns": [...], "partition_columns": [...]}
```

## Volume Management Tools

### 4. Volume Operations

#### `list_uc_volumes(catalog_name: str, schema_name: str)`
Lists all volumes in a Unity Catalog schema.

**Parameters:**
- `catalog_name`: Name of the catalog
- `schema_name`: Name of the schema

**Returns:**
- List of volumes with metadata (name, type, storage location, comment, etc.)
- Volume count

**Example:**
```python
# List volumes in a schema
result = list_uc_volumes("hive_metastore", "default")
# Returns: {"success": true, "volumes": [...], "count": 3}
```

#### `describe_uc_volume(volume_name: str)`
Gets detailed volume information including storage location and properties.

**Parameters:**
- `volume_name`: Full volume name in `catalog.schema.volume` format

**Returns:**
- Complete volume metadata (name, type, storage location, comment, owner, etc.)
- Volume properties if available

**Example:**
```python
# Describe a specific volume
result = describe_uc_volume("hive_metastore.default.raw_data")
# Returns: {"success": true, "volume": {...}}
```

## Function Management Tools

### 5. Function Operations

#### `list_uc_functions(catalog_name: str, schema_name: str)`
Lists all functions in a Unity Catalog schema.

**Parameters:**
- `catalog_name`: Name of the catalog
- `schema_name`: Name of the schema

**Returns:**
- List of functions with metadata (name, type, comment, owner, etc.)
- Function count

**Example:**
```python
# List functions in a schema
result = list_uc_functions("hive_metastore", "default")
# Returns: {"success": true, "functions": [...], "count": 8}
```

#### `describe_uc_function(function_name: str)`
Gets detailed function information including parameters and return type.

**Parameters:**
- `function_name`: Full function name in `catalog.schema.function` format

**Returns:**
- Complete function metadata (name, type, comment, owner, etc.)
- Input parameters with types and comments
- Return type information
- Function properties if available

**Example:**
```python
# Describe a specific function
result = describe_uc_function("hive_metastore.default.calculate_score")
# Returns: {"success": true, "function": {...}, "input_params": [...], "return_type": "..."}
```

## Model Management Tools

### 6. Model Operations

#### `list_uc_models(catalog_name: str, schema_name: str)`
Lists all models in a Unity Catalog schema.

**Parameters:**
- `catalog_name`: Name of the catalog
- `schema_name`: Name of the schema

**Returns:**
- List of models with metadata (name, type, comment, owner, etc.)
- Model count

**Example:**
```python
# List models in a schema
result = list_uc_models("hive_metastore", "ml_models")
# Returns: {"success": true, "models": [...], "count": 5}
```

#### `describe_uc_model(model_name: str)`
Gets detailed model information including version history and lineage.

**Parameters:**
- `model_name`: Full model name in `catalog.schema.model` format

**Returns:**
- Complete model metadata (name, type, comment, owner, etc.)
- Storage location information
- Model properties if available

**Example:**
```python
# Describe a specific model
result = describe_uc_model("hive_metastore.ml_models.churn_prediction")
# Returns: {"success": true, "model": {...}}
```

## External Storage Tools

### 7. External Location Management

#### `list_external_locations()`
Lists all external locations configured in the workspace.

**Returns:**
- List of external locations with metadata (name, URL, credential, comment, etc.)
- Location count

**Example:**
```python
# List all external locations
result = list_external_locations()
# Returns: {"success": true, "locations": [...], "count": 12}
```

#### `describe_external_location(location_name: str)`
Gets detailed external location information.

**Parameters:**
- `location_name`: Name of the external location

**Returns:**
- Complete location metadata (name, URL, credential, comment, owner, etc.)
- Location properties if available

**Example:**
```python
# Describe a specific external location
result = describe_external_location("s3_data_lake")
# Returns: {"success": true, "location": {...}}
```

### 8. Storage Credential Management

#### `list_storage_credentials()`
Lists all storage credentials configured in the workspace.

**Returns:**
- List of storage credentials with metadata (name, type, comment, owner, etc.)
- Credential count

**Example:**
```python
# List all storage credentials
result = list_storage_credentials()
# Returns: {"success": true, "credentials": [...], "count": 8}
```

#### `describe_storage_credential(credential_name: str)`
Gets detailed storage credential information.

**Parameters:**
- `credential_name`: Name of the storage credential

**Returns:**
- Complete credential metadata (name, type, comment, owner, etc.)
- Credential properties if available

**Example:**
```python
# Describe a specific storage credential
result = describe_storage_credential("aws_credentials")
# Returns: {"success": true, "credential": {...}}
```

## Governance and Access Control Tools

### 9. Permission Management

#### `list_uc_permissions(catalog_name: str = None, schema_name: str = None, table_name: str = None)`
Lists permissions for Unity Catalog objects.

**Parameters:**
- `catalog_name`: Name of the catalog (optional)
- `schema_name`: Name of the schema (optional)
- `table_name`: Name of the table (optional)

**Returns:**
- Permission information for the specified object
- Object type and name
- Note: This is a placeholder for permissions API integration

**Example:**
```python
# List permissions for a table
result = list_uc_permissions("hive_metastore", "default", "users")
# Returns: {"success": true, "object_name": "hive_metastore.default.users", "object_type": "table", ...}
```

## Discovery and Search Tools

### 10. Object Search

#### `search_uc_objects(query: str, object_types: list = None)`
Searches for Unity Catalog objects by name, description, or tags.

**Parameters:**
- `query`: Search query string
- `object_types`: List of object types to search (catalog, schema, table, volume, function)

**Returns:**
- Search results with object details
- Match reason (name or comment)
- Result count

**Example:**
```python
# Search for objects containing "user"
result = search_uc_objects("user", ["table", "schema"])
# Returns: {"success": true, "results": [...], "count": 5}
```

### 11. Table Statistics

#### `get_table_statistics(table_name: str)`
Gets table statistics including metadata and column information.

**Parameters:**
- `table_name`: Full table name in `catalog.schema.table` format

**Returns:**
- Table statistics and metadata
- Column information
- Note: Detailed statistics require additional API integration

**Example:**
```python
# Get table statistics
result = get_table_statistics("hive_metastore.default.users")
# Returns: {"success": true, "table_stats": {...}, "columns": [...]}
```

## Metastore Management Tools

### 12. Metastore Operations

#### `list_metastores()`
Lists all metastores in the workspace.

**Returns:**
- List of metastores with metadata (name, ID, owner, comment, etc.)
- Metastore count

**Example:**
```python
# List all metastores
result = list_metastores()
# Returns: {"success": true, "metastores": [...], "count": 2}
```

#### `describe_metastore(metastore_name: str)`
Gets detailed metastore information.

**Parameters:**
- `metastore_name`: Name of the metastore

**Returns:**
- Complete metastore metadata (name, ID, owner, comment, etc.)
- Metastore properties if available

**Example:**
```python
# Describe a specific metastore
result = describe_metastore("hive_metastore")
# Returns: {"success": true, "metastore": {...}}
```

## Advanced Features (Placeholder Implementations)

### 13. Tag Management

#### `list_uc_tags(catalog_name: str = None)`
Lists available tags in Unity Catalog.

**Parameters:**
- `catalog_name`: Name of the catalog (optional, lists all if not specified)

**Returns:**
- Tag information (placeholder implementation)
- Note: Tags API integration requires additional implementation

**Example:**
```python
# List tags for a catalog
result = list_uc_tags("hive_metastore")
# Returns: {"success": true, "tags": [...], "count": 1}
```

#### `apply_uc_tags(object_name: str, tags: dict)`
Applies tags to Unity Catalog objects.

**Parameters:**
- `object_name`: Full object name (catalog.schema.table, catalog.schema, or catalog)
- `tags`: Dictionary of tag key-value pairs to apply

**Returns:**
- Tag application operation result (placeholder implementation)
- Note: Tag application requires additional API integration

**Example:**
```python
# Apply tags to a table
result = apply_uc_tags("hive_metastore.default.users", {"environment": "production", "team": "data_engineering"})
# Returns: {"success": true, "result": {...}}
```

### 14. Data Quality Monitoring

#### `list_data_quality_monitors(catalog_name: str = None)`
Lists data quality monitors configured in Unity Catalog.

**Parameters:**
- `catalog_name`: Name of the catalog (optional, lists all if not specified)

**Returns:**
- Monitor information (placeholder implementation)
- Note: Data quality API integration requires additional implementation

**Example:**
```python
# List data quality monitors
result = list_data_quality_monitors("hive_metastore")
# Returns: {"success": true, "monitors": [...], "count": 1}
```

#### `get_data_quality_results(monitor_name: str, date_range: str = "7d")`
Gets data quality monitoring results.

**Parameters:**
- `monitor_name`: Name of the data quality monitor
- `date_range`: Date range for results (e.g., "7d", "30d", "90d")

**Returns:**
- Monitoring results (placeholder implementation)
- Note: Data quality results API integration requires additional implementation

**Example:**
```python
# Get data quality results
result = get_data_quality_results("user_data_quality", "30d")
# Returns: {"success": true, "results": {...}}
```

#### `create_data_quality_monitor(table_name: str, rules: list)`
Creates a new data quality monitor for a table.

**Parameters:**
- `table_name`: Full table name in `catalog.schema.table` format
- `rules`: List of data quality rules to apply

**Returns:**
- Monitor creation operation result (placeholder implementation)
- Note: Data quality monitor creation requires additional API integration

**Example:**
```python
# Create a data quality monitor
result = create_data_quality_monitor("hive_metastore.default.users", ["not_null", "unique_values"])
# Returns: {"success": true, "result": {...}}
```

## Usage Patterns

### Common Workflows

#### 1. Data Discovery
```python
# 1. Explore a specific catalog (start with common catalogs like hive_metastore)
catalog_details = describe_uc_catalog("hive_metastore")

# 3. Explore schemas in the catalog
schema_details = describe_uc_schema("hive_metastore", "default", include_columns=True)

# 4. Get detailed table information
table_details = describe_uc_table("hive_metastore.default.users", include_lineage=True)
```

#### 2. Storage Management
```python
# 1. List external locations
locations = list_external_locations()

# 2. Check storage credentials
credentials = list_storage_credentials()

# 3. Explore volumes in a schema
volumes = list_uc_volumes("hive_metastore", "default")
```

#### 3. Function and Model Discovery
```python
# 1. List functions in a schema
functions = list_uc_functions("hive_metastore", "default")

# 2. List models in a schema
models = list_uc_models("hive_metastore", "ml_models")

# 3. Get detailed information
function_details = describe_uc_function("hive_metastore.default.calculate_score")
model_details = describe_uc_model("hive_metastore.ml_models.churn_prediction")
```

## Error Handling

All tools follow consistent error handling patterns:

- **Success responses**: Include `success: true` and relevant data
- **Error responses**: Include `success: false` and error details
- **Warning logs**: Printed to console for non-critical issues
- **Exception handling**: Comprehensive try-catch blocks with detailed error messages

## Performance Considerations

- **Pagination**: Most list operations support pagination for large result sets
- **Lazy loading**: Column details are only fetched when explicitly requested
- **Caching**: Consider implementing caching for frequently accessed metadata
- **Batch operations**: Some operations can be batched for better performance

## Security and Permissions

- **Authentication**: All tools use the configured Databricks authentication
- **Permission checks**: Tools respect Unity Catalog access controls
- **Audit logging**: All operations are logged for compliance
- **Error masking**: Sensitive information is not exposed in error messages

## Future Enhancements

The following features are planned for future releases:

1. **Full permissions API integration** - Complete access control management
2. **Tag management** - Full CRUD operations for Unity Catalog tags
3. **Data quality monitoring** - Complete data quality API integration
4. **Lineage tracking** - Advanced data lineage and dependency analysis
5. **Performance metrics** - Table and query performance analytics
6. **Governance policies** - Policy management and enforcement

## Testing

Use the provided test script to validate all Unity Catalog tools:

```bash
# Set environment variables
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-token"

# Run the test script
python claude_scripts/test_uc_tools.py
```

## Support

For issues or questions about Unity Catalog tools:

1. Check the error messages and logs for debugging information
2. Verify your Databricks authentication and permissions
3. Ensure the target objects exist and are accessible
4. Check the Databricks SDK documentation for API details
5. Review the placeholder implementations for advanced features
