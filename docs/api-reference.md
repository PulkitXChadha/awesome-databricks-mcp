# API Reference

Complete reference for all MCP tools available in the Databricks MCP Server.

## 📊 Unity Catalog Tools

### Catalog Management

#### `list_uc_catalogs()`
Lists all available Unity Catalog catalogs.

**Returns**: `{"success": bool, "catalogs": list, "count": int}`

#### `describe_uc_catalog(catalog_name: str)`
Provides detailed catalog information and schemas.

**Parameters**:
- `catalog_name`: Name of the catalog

**Returns**: `{"success": bool, "catalog": dict, "schemas": list, "schema_count": int}`

#### `search_uc_objects(query: str, object_types: list = None)`
Searches for catalog objects by name, description, or tags.

**Parameters**:
- `query`: Search query string
- `object_types`: List of object types to search (optional)

**Returns**: `{"success": bool, "results": list, "count": int}`

### Schema & Table Operations

#### `describe_uc_schema(catalog_name: str, schema_name: str, include_columns: bool = False)`
Describes a schema and its tables.

**Parameters**:
- `catalog_name`: Name of the catalog
- `schema_name`: Name of the schema
- `include_columns`: Include detailed column information (default: False)

**Returns**: `{"success": bool, "schema": dict, "tables": list, "table_count": int}`

#### `describe_uc_table(table_name: str, include_lineage: bool = False)`
Provides detailed table structure and metadata.

**Parameters**:
- `table_name`: Full table name (catalog.schema.table)
- `include_lineage`: Include lineage information (default: False)

**Returns**: `{"success": bool, "table": dict, "columns": list, "partition_columns": list}`

#### `get_table_statistics(table_name: str)`
Gets table statistics and metadata.

**Parameters**:
- `table_name`: Full table name (catalog.schema.table)

**Returns**: `{"success": bool, "table_stats": dict, "columns": list}`

### Volume & Function Management

#### `list_uc_volumes(catalog_name: str, schema_name: str)`
Lists all volumes in a schema.

**Parameters**:
- `catalog_name`: Name of the catalog
- `schema_name`: Name of the schema

**Returns**: `{"success": bool, "volumes": list, "count": int}`

#### `describe_uc_volume(volume_name: str)`
Gets detailed volume information.

**Parameters**:
- `volume_name`: Full volume name (catalog.schema.volume)

**Returns**: `{"success": bool, "volume": dict}`

#### `list_uc_functions(catalog_name: str, schema_name: str)`
Lists all functions in a schema.

**Parameters**:
- `catalog_name`: Name of the catalog
- `schema_name`: Name of the schema

**Returns**: `{"success": bool, "functions": list, "count": int}`

#### `describe_uc_function(function_name: str)`
Gets detailed function information.

**Parameters**:
- `function_name`: Full function name (catalog.schema.function)

**Returns**: `{"success": bool, "function": dict, "input_params": list, "return_type": str}`

### Model Management

#### `list_uc_models(catalog_name: str, schema_name: str)`
Lists all models in a schema.

**Parameters**:
- `catalog_name`: Name of the catalog
- `schema_name`: Name of the schema

**Returns**: `{"success": bool, "models": list, "count": int}`

#### `describe_uc_model(model_name: str)`
Gets detailed model information.

**Parameters**:
- `model_name`: Full model name (catalog.schema.model)

**Returns**: `{"success": bool, "model": dict}`

## 🗄️ SQL Operations

### Warehouse Management

#### `list_warehouses()`
Lists all SQL warehouses.

**Returns**: `{"success": bool, "warehouses": list, "count": int}`

#### `get_sql_warehouse(warehouse_id: str)`
Gets warehouse details.

**Parameters**:
- `warehouse_id`: ID of the warehouse

**Returns**: `{"success": bool, "warehouse": dict}`

#### `create_sql_warehouse(warehouse_config: dict)`
Creates a new SQL warehouse.

**Parameters**:
- `warehouse_config`: Warehouse configuration dictionary

**Returns**: `{"success": bool, "warehouse": dict}`

#### `start_sql_warehouse(warehouse_id: str)`
Starts a SQL warehouse.

**Parameters**:
- `warehouse_id`: ID of the warehouse

**Returns**: `{"success": bool, "message": str}`

#### `stop_sql_warehouse(warehouse_id: str)`
Stops a SQL warehouse.

**Parameters**:
- `warehouse_id`: ID of the warehouse

**Returns**: `{"success": bool, "message": str}`

#### `delete_sql_warehouse(warehouse_id: str)`
Deletes a SQL warehouse.

**Parameters**:
- `warehouse_id`: ID of the warehouse

**Returns**: `{"success": bool, "message": str}`

### Query Execution

#### `execute_dbsql(query: str, warehouse_id: str, catalog: str = None, schema: str = None, limit: int = 100)`
Executes a SQL query on a warehouse.

**Parameters**:
- `query`: SQL query to execute
- `warehouse_id`: ID of the warehouse
- `catalog`: Catalog to use (optional)
- `schema`: Schema to use (optional)
- `limit`: Maximum rows to return (default: 100)

**Returns**: `{"success": bool, "statement_id": str, "status": str, "result": dict}`

#### `list_queries(warehouse_id: str = None)`
Lists queries (all or for specific warehouse).

**Parameters**:
- `warehouse_id`: Warehouse ID (optional)

**Returns**: `{"success": bool, "queries": list, "count": int}`

#### `get_query(query_id: str)`
Gets query details.

**Parameters**:
- `query_id`: ID of the query

**Returns**: `{"success": bool, "query": dict}`

#### `get_query_results(query_id: str)`
Gets query results.

**Parameters**:
- `query_id`: ID of the query

**Returns**: `{"success": bool, "results": dict}`

#### `cancel_query(query_id: str)`
Cancels a running query.

**Parameters**:
- `query_id`: ID of the query

**Returns**: `{"success": bool, "message": str}`

### Statement Management

#### `get_statement_status(statement_id: str)`
Gets statement execution status.

**Parameters**:
- `statement_id`: ID of the statement

**Returns**: `{"success": bool, "status": str}`

#### `get_statement_results(statement_id: str)`
Gets statement results.

**Parameters**:
- `statement_id`: ID of the statement

**Returns**: `{"success": bool, "results": dict}`

#### `cancel_statement(statement_id: str)`
Cancels statement execution.

**Parameters**:
- `statement_id`: ID of the statement

**Returns**: `{"success": bool, "message": str}`

## 💻 Compute Management

### Cluster Operations

#### `list_clusters()`
Lists all clusters.

**Returns**: `{"success": bool, "clusters": list, "count": int}`

#### `get_cluster(cluster_id: str)`
Gets cluster details.

**Parameters**:
- `cluster_id`: ID of the cluster

**Returns**: `{"success": bool, "cluster": dict}`

#### `create_cluster(cluster_config: dict)`
Creates a new cluster.

**Parameters**:
- `cluster_config`: Cluster configuration dictionary

**Returns**: `{"success": bool, "cluster": dict}`

#### `start_cluster(cluster_id: str)`
Starts a cluster.

**Parameters**:
- `cluster_id`: ID of the cluster

**Returns**: `{"success": bool, "message": str}`

#### `stop_cluster(cluster_id: str)`
Stops a cluster.

**Parameters**:
- `cluster_id`: ID of the cluster

**Returns**: `{"success": bool, "message": str}`

#### `delete_cluster(cluster_id: str)`
Deletes a cluster.

**Parameters**:
- `cluster_id`: ID of the cluster

**Returns**: `{"success": bool, "message": str}`

#### `resize_cluster(cluster_id: str, num_workers: int)`
Resizes a cluster.

**Parameters**:
- `cluster_id`: ID of the cluster
- `num_workers`: New number of workers

**Returns**: `{"success": bool, "message": str}`

## 🔄 Jobs & Workflows

### Job Management

#### `list_jobs()`
Lists all jobs.

**Returns**: `{"success": bool, "jobs": list, "count": int}`

#### `get_job(job_id: str)`
Gets job details.

**Parameters**:
- `job_id`: ID of the job

**Returns**: `{"success": bool, "job": dict}`

#### `create_job(job_config: dict)`
Creates a new job.

**Parameters**:
- `job_config`: Job configuration dictionary

**Returns**: `{"success": bool, "job": dict}`

#### `update_job(job_id: str, updates: dict)`
Updates a job.

**Parameters**:
- `job_id`: ID of the job
- `updates`: Updates to apply

**Returns**: `{"success": bool, "job": dict}`

#### `delete_job(job_id: str)`
Deletes a job.

**Parameters**:
- `job_id`: ID of the job

**Returns**: `{"success": bool, "message": str}`

### Job Execution

#### `list_job_runs(job_id: str = None)`
Lists job runs (all or for specific job).

**Parameters**:
- `job_id`: Job ID (optional)

**Returns**: `{"success": bool, "runs": list, "count": int}`

#### `get_job_run(run_id: str)`
Gets job run details.

**Parameters**:
- `run_id`: ID of the run

**Returns**: `{"success": bool, "run": dict}`

#### `submit_job_run(job_id: str, parameters: dict = None)`
Submits a new job run.

**Parameters**:
- `job_id`: ID of the job
- `parameters`: Run parameters (optional)

**Returns**: `{"success": bool, "run": dict}`

#### `cancel_job_run(run_id: str)`
Cancels a running job.

**Parameters**:
- `run_id`: ID of the run

**Returns**: `{"success": bool, "message": str}`

#### `get_job_run_logs(run_id: str)`
Gets job run logs.

**Parameters**:
- `run_id`: ID of the run

**Returns**: `{"success": bool, "logs": list}`

## 📁 File Management

### DBFS Operations

#### `list_dbfs_path(path: str = "/")`
Lists files in DBFS path.

**Parameters**:
- `path`: DBFS path to list (default: "/")

**Returns**: `{"success": bool, "files": list, "count": int}`

#### `get_dbfs_file_info(path: str)`
Gets file information.

**Parameters**:
- `path`: DBFS file path

**Returns**: `{"success": bool, "file_info": dict}`

#### `read_dbfs_file(path: str, offset: int = 0, length: int = None)`
Reads file content.

**Parameters**:
- `path`: DBFS file path
- `offset`: Byte offset (default: 0)
- `length`: Number of bytes to read (default: all)

**Returns**: `{"success": bool, "content": bytes, "file_info": dict}`

#### `write_dbfs_file(path: str, content: bytes, overwrite: bool = False)`
Writes file content.

**Parameters**:
- `path`: DBFS file path
- `content`: File content as bytes
- `overwrite`: Overwrite existing file (default: False)

**Returns**: `{"success": bool, "message": str}`

#### `delete_dbfs_path(path: str, recursive: bool = False)`
Deletes file or directory.

**Parameters**:
- `path`: DBFS path to delete
- `recursive`: Delete recursively (default: False)

**Returns**: `{"success": bool, "message": str}`

### Workspace Files

#### `list_workspace_files(path: str = "/")`
Lists workspace files.

**Parameters**:
- `path`: Workspace path to list (default: "/")

**Returns**: `{"success": bool, "files": list, "count": int}`

#### `get_workspace_file_info(path: str)`
Gets workspace file information.

**Parameters**:
- `path`: Workspace file path

**Returns**: `{"success": bool, "file_info": dict}`

#### `read_workspace_file(path: str)`
Reads workspace file content.

**Parameters**:
- `path`: Workspace file path

**Returns**: `{"success": bool, "content": str, "file_info": dict}`

#### `write_workspace_file(path: str, content: str, language: str = None)`
Writes workspace file content.

**Parameters**:
- `path`: Workspace file path
- `content`: File content as string
- `language`: File language (optional)

**Returns**: `{"success": bool, "message": str}`

## 🤖 Machine Learning & AI

### Model Serving

#### `list_serving_endpoints()`
Lists all serving endpoints.

**Returns**: `{"success": bool, "endpoints": list, "count": int}`

#### `get_serving_endpoint(endpoint_name: str)`
Gets endpoint details.

**Parameters**:
- `endpoint_name`: Name of the endpoint

**Returns**: `{"success": bool, "endpoint": dict}`

#### `create_serving_endpoint(endpoint_config: dict)`
Creates a new serving endpoint.

**Parameters**:
- `endpoint_config`: Endpoint configuration dictionary

**Returns**: `{"success": bool, "endpoint": dict}`

#### `update_serving_endpoint(endpoint_name: str, updates: dict)`
Updates a serving endpoint.

**Parameters**:
- `endpoint_name`: Name of the endpoint
- `updates`: Updates to apply

**Returns**: `{"success": bool, "endpoint": dict}`

#### `delete_serving_endpoint(endpoint_name: str)`
Deletes a serving endpoint.

**Parameters**:
- `endpoint_name`: Name of the endpoint

**Returns**: `{"success": bool, "message": str}`

#### `query_serving_endpoint(endpoint_name: str, data: dict)`
Queries a serving endpoint.

**Parameters**:
- `endpoint_name`: Name of the endpoint
- `data`: Input data for the model

**Returns**: `{"success": bool, "prediction": dict}`

## 📚 Repos & Git Integration

### Repository Management

#### `list_repos()`
Lists all repositories.

**Returns**: `{"success": bool, "repos": list, "count": int}`

#### `get_repo(repo_id: str)`
Gets repository details.

**Parameters**:
- `repo_id`: ID of the repository

**Returns**: `{"success": bool, "repo": dict}`

#### `create_repo(url: str, provider: str, path: str = None)`
Creates a new repository.

**Parameters**:
- `url`: Git repository URL
- `provider`: Git provider (github, gitlab, etc.)
- `path`: Local workspace path (optional)

**Returns**: `{"success": bool, "repo": dict}`

#### `update_repo(repo_id: str, updates: dict)`
Updates repository settings.

**Parameters**:
- `repo_id`: ID of the repository
- `updates`: Updates to apply

**Returns**: `{"success": bool, "repo": dict}`

#### `delete_repo(repo_id: str)`
Deletes a repository.

**Parameters**:
- `repo_id`: ID of the repository

**Returns**: `{"success": bool, "message": str}`

### Git Operations

#### `get_repo_status(repo_id: str)`
Gets repository status.

**Parameters**:
- `repo_id`: ID of the repository

**Returns**: `{"success": bool, "status": dict}`

#### `pull_repo(repo_id: str)`
Pulls latest changes.

**Parameters**:
- `repo_id`: ID of the repository

**Returns**: `{"success": bool, "message": str}`

#### `push_repo(repo_id: str, message: str)`
Pushes local changes.

**Parameters**:
- `repo_id`: ID of the repository
- `message`: Commit message

**Returns**: `{"success": bool, "message": str}`

#### `create_branch(repo_id: str, branch_name: str, source_branch: str = None)`
Creates a new branch.

**Parameters**:
- `repo_id`: ID of the repository
- `branch_name`: Name of the new branch
- `source_branch`: Source branch (optional)

**Returns**: `{"success": bool, "message": str}`

## 📊 Dashboards & Visualization

### Lakeview Dashboards

#### `list_lakeview_dashboards()`
Lists all Lakeview dashboards.

**Returns**: `{"success": bool, "dashboards": list, "count": int}`

#### `get_lakeview_dashboard(dashboard_id: str)`
Gets dashboard details.

**Parameters**:
- `dashboard_id`: ID of the dashboard

**Returns**: `{"success": bool, "dashboard": dict}`

#### `create_lakeview_dashboard(dashboard_config: dict)`
Creates a new dashboard.

**Parameters**:
- `dashboard_config`: Dashboard configuration dictionary

**Returns**: `{"success": bool, "dashboard": dict}`

#### `update_lakeview_dashboard(dashboard_id: str, updates: dict)`
Updates a dashboard.

**Parameters**:
- `dashboard_id`: ID of the dashboard
- `updates`: Updates to apply

**Returns**: `{"success": bool, "dashboard": dict}`

#### `delete_lakeview_dashboard(dashboard_id: str)`
Deletes a dashboard.

**Parameters**:
- `dashboard_id`: ID of the dashboard

**Returns**: `{"success": bool, "message": str}`

## 📈 Monitoring & Quality

### Data Quality Monitoring

#### `list_data_quality_monitors(catalog_name: str = None)`
Lists data quality monitors.

**Parameters**:
- `catalog_name`: Catalog name (optional)

**Returns**: `{"success": bool, "monitors": list, "count": int}`

#### `get_data_quality_results(monitor_name: str, date_range: str = "7d")`
Gets monitoring results.

**Parameters**:
- `monitor_name`: Name of the monitor
- `date_range`: Date range for results (default: "7d")

**Returns**: `{"success": bool, "results": dict}`

#### `create_data_quality_monitor(table_name: str, rules: list)`
Creates a new monitor.

**Parameters**:
- `table_name`: Full table name
- `rules`: List of quality rules

**Returns**: `{"success": bool, "monitor": dict}`

### Audit & Compliance

#### `list_audit_logs(start_time: str = None, end_time: str = None, user_id: str = None)`
Lists audit logs.

**Parameters**:
- `start_time`: Start time (optional)
- `end_time`: End time (optional)
- `user_id`: User ID (optional)

**Returns**: `{"success": bool, "logs": list, "count": int}`

#### `get_audit_log(event_id: str)`
Gets audit log details.

**Parameters**:
- `event_id`: ID of the event

**Returns**: `{"success": bool, "log": dict}`

#### `export_audit_logs(start_time: str, end_time: str, format: str = "json")`
Exports audit logs.

**Parameters**:
- `start_time`: Start time
- `end_time`: End time
- `format`: Export format (default: "json")

**Returns**: `{"success": bool, "export_url": str}`

## 🔐 Secret Management

### Secret Scopes

#### `list_secret_scopes()`
Lists all secret scopes.

**Returns**: `{"success": bool, "scopes": list, "count": int}`

#### `get_secret_scope(scope_name: str)`
Gets scope details.

**Parameters**:
- `scope_name`: Name of the scope

**Returns**: `{"success": bool, "scope": dict}`

#### `create_secret_scope(scope_name: str, initial_manage_principal: str = None)`
Creates a new scope.

**Parameters**:
- `scope_name`: Name of the scope
- `initial_manage_principal`: Initial manager (optional)

**Returns**: `{"success": bool, "scope": dict}`

#### `delete_secret_scope(scope_name: str)`
Deletes a scope.

**Parameters**:
- `scope_name`: Name of the scope

**Returns**: `{"success": bool, "message": str}`

### Secret Operations

#### `list_secrets(scope_name: str)`
Lists secrets in a scope.

**Parameters**:
- `scope_name`: Name of the scope

**Returns**: `{"success": bool, "secrets": list, "count": int}`

#### `put_secret(scope_name: str, key: str, value: str)`
Stores a secret.

**Parameters**:
- `scope_name`: Name of the scope
- `key`: Secret key
- `value`: Secret value

**Returns**: `{"success": bool, "message": str}`

#### `get_secret(scope_name: str, key: str)`
Retrieves a secret.

**Parameters**:
- `scope_name`: Name of the scope
- `key`: Secret key

**Returns**: `{"success": bool, "value": str}`

#### `delete_secret(scope_name: str, key: str)`
Deletes a secret.

**Parameters**:
- `scope_name`: Name of the scope
- `key`: Secret key

**Returns**: `{"success": bool, "message": str}`

## 🌐 External Storage & Credentials

### External Locations

#### `list_external_locations()`
Lists all external locations.

**Returns**: `{"success": bool, "locations": list, "count": int}`

#### `get_external_location(location_name: str)`
Gets location details.

**Parameters**:
- `location_name`: Name of the location

**Returns**: `{"success": bool, "location": dict}`

#### `create_external_location(name: str, url: str, credential_name: str, comment: str = None)`
Creates a new location.

**Parameters**:
- `name`: Location name
- `url`: Storage URL
- `credential_name`: Credential name
- `comment`: Comment (optional)

**Returns**: `{"success": bool, "location": dict}`

#### `update_external_location(location_name: str, updates: dict)`
Updates a location.

**Parameters**:
- `location_name`: Name of the location
- `updates`: Updates to apply

**Returns**: `{"success": bool, "location": dict}`

#### `delete_external_location(location_name: str)`
Deletes a location.

**Parameters**:
- `location_name`: Name of the location

**Returns**: `{"success": bool, "message": str}`

## 🚀 Advanced Features

### Vector Search

#### `list_vector_search_endpoints()`
Lists all vector search endpoints.

**Returns**: `{"success": bool, "endpoints": list, "count": int}`

#### `get_vector_search_endpoint(endpoint_name: str)`
Gets endpoint details.

**Parameters**:
- `endpoint_name`: Name of the endpoint

**Returns**: `{"success": bool, "endpoint": dict}`

#### `create_vector_search_endpoint(endpoint_config: dict)`
Creates a new endpoint.

**Parameters**:
- `endpoint_config`: Endpoint configuration dictionary

**Returns**: `{"success": bool, "endpoint": dict}`

#### `list_vector_search_indexes(endpoint_name: str = None)`
Lists vector search indexes.

**Parameters**:
- `endpoint_name`: Endpoint name (optional)

**Returns**: `{"success": bool, "indexes": list, "count": int}`

#### `query_vector_search_index(index_name: str, query_vector: list, k: int = 10)`
Searches vectors.

**Parameters**:
- `index_name`: Name of the index
- `query_vector`: Query vector
- `k`: Number of results (default: 10)

**Returns**: `{"success": bool, "results": list}`

## 📋 Common Response Format

All tools return responses in a consistent format:

### Success Response
```json
{
  "success": true,
  "data": {...},
  "count": 5,
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "details": {...}
}
```

## 🔧 Error Codes

| Code | Description |
|------|-------------|
| `AUTHENTICATION_ERROR` | Authentication failed |
| `PERMISSION_DENIED` | Insufficient permissions |
| `NOT_FOUND` | Resource not found |
| `VALIDATION_ERROR` | Invalid parameters |
| `RATE_LIMIT_EXCEEDED` | API rate limit exceeded |
| `INTERNAL_ERROR` | Server internal error |

## 📚 Related Documentation

- **[Getting Started](getting-started.md)** - Setup and basic usage
- **[Core Tools](core-tools.md)** - Tool categories and overview
- **[Architecture](architecture.md)** - System design details
- **[Examples](examples.md)** - Usage examples and patterns
