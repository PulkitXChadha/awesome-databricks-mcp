# Core Tools & APIs

This document provides a comprehensive overview of all core tools and APIs available in the Databricks MCP Server.

## 🏗️ Architecture Overview

The Databricks MCP Server provides a unified interface to Databricks services through:

1. **Direct SDK Integration**: Raw access to Databricks SDK capabilities
2. **Tool Wrappers**: Simplified, consistent interfaces for common operations
3. **Error Handling**: Standardized error responses and validation
4. **Performance Optimization**: Pagination, caching, and async operations

## 🔐 Authentication & Setup

All tools use the same authentication mechanism:

```python
from databricks.sdk import WorkspaceClient

# Automatically uses configured authentication
client = WorkspaceClient()

# Available authentication methods:
# - Personal Access Token (DATABRICKS_HOST + DATABRICKS_TOKEN)
# - CLI Profile (DATABRICKS_CONFIG_PROFILE)
# - Service Principal (when deployed to Databricks Apps)
```

## 📊 Unity Catalog Tools

### Catalog Management
- **`list_uc_catalogs()`** - List all available catalogs
- **`describe_uc_catalog(catalog_name)`** - Get detailed catalog information
- **`search_uc_objects(query, object_types)`** - Search for catalog objects

### Schema & Table Operations
- **`describe_uc_schema(catalog, schema, include_columns)`** - Explore schema structure
- **`describe_uc_table(table_name, include_lineage)`** - Get table metadata and lineage
- **`get_table_statistics(table_name)`** - Retrieve table statistics

### Volume & Function Management
- **`list_uc_volumes(catalog, schema)`** - List volumes in schema
- **`describe_uc_volume(volume_name)`** - Get volume details
- **`list_uc_functions(catalog, schema)`** - List functions in schema
- **`describe_uc_function(function_name)`** - Get function details

### Model Management
- **`list_uc_models(catalog, schema)`** - List ML models in schema
- **`describe_uc_model(model_name)`** - Get model metadata and lineage

## 🗄️ SQL Operations

### Warehouse Management
- **`list_warehouses()`** - List all SQL warehouses
- **`get_sql_warehouse(warehouse_id)`** - Get warehouse details
- **`create_sql_warehouse(config)`** - Create new warehouse
- **`start_sql_warehouse(warehouse_id)`** - Start warehouse
- **`stop_sql_warehouse(warehouse_id)`** - Stop warehouse
- **`delete_sql_warehouse(warehouse_id)`** - Delete warehouse

### Query Execution
- **`execute_dbsql(query, warehouse_id, ...)`** - Execute SQL queries
- **`list_queries(warehouse_id)`** - List queries (all or per warehouse)
- **`get_query(query_id)`** - Get query details
- **`get_query_results(query_id)`** - Retrieve query results
- **`cancel_query(query_id)`** - Cancel running queries

### Statement Management
- **`get_statement_status(statement_id)`** - Check execution status
- **`get_statement_results(statement_id)`** - Get statement results
- **`cancel_statement(statement_id)`** - Cancel statement execution

## 💻 Compute Management

### Cluster Operations
- **`list_clusters()`** - List all clusters
- **`get_cluster(cluster_id)`** - Get cluster details
- **`create_cluster(config)`** - Create new cluster
- **`start_cluster(cluster_id)`** - Start cluster
- **`stop_cluster(cluster_id)`** - Stop cluster
- **`delete_cluster(cluster_id)`** - Delete cluster
- **`resize_cluster(cluster_id, num_workers)`** - Resize cluster

### Instance Pool Management
- **`list_instance_pools()`** - List instance pools
- **`get_instance_pool(pool_id)`** - Get pool details
- **`create_instance_pool(config)`** - Create new pool
- **`delete_instance_pool(pool_id)`** - Delete pool

### Cluster Policies
- **`list_cluster_policies()`** - List policies
- **`get_cluster_policy(policy_id)`** - Get policy details
- **`create_cluster_policy(config)`** - Create new policy
- **`update_cluster_policy(policy_id, updates)`** - Update policy

## 🔄 Jobs & Workflows

### Job Management
- **`list_jobs()`** - List all jobs
- **`get_job(job_id)`** - Get job details
- **`create_job(config)`** - Create new job
- **`update_job(job_id, updates)`** - Update job
- **`delete_job(job_id)`** - Delete job

### Job Execution
- **`list_job_runs(job_id)`** - List job runs
- **`get_job_run(run_id)`** - Get run details
- **`submit_job_run(job_id, parameters)`** - Submit new run
- **`cancel_job_run(run_id)`** - Cancel running job
- **`get_job_run_logs(run_id)`** - Get run logs

### Pipeline Management (Delta Live Tables)
- **`list_pipelines()`** - List DLT pipelines
- **`get_pipeline(pipeline_id)`** - Get pipeline details
- **`create_pipeline(config)`** - Create new pipeline
- **`update_pipeline(pipeline_id, updates)`** - Update pipeline
- **`delete_pipeline(pipeline_id)`** - Delete pipeline

## 📁 File Management

### DBFS Operations
- **`list_dbfs_path(path)`** - List files in DBFS
- **`get_dbfs_file_info(path)`** - Get file information
- **`read_dbfs_file(path, offset, length)`** - Read file content
- **`write_dbfs_file(path, content, overwrite)`** - Write file content
- **`delete_dbfs_path(path, recursive)`** - Delete file/directory
- **`create_dbfs_directory(path)`** - Create directory
- **`move_dbfs_path(source, destination)`** - Move/rename files

### Workspace Files
- **`list_workspace_files(path)`** - List workspace files
- **`get_workspace_file_info(path)`** - Get file metadata
- **`read_workspace_file(path)`** - Read workspace file
- **`write_workspace_file(path, content, language)`** - Write workspace file
- **`delete_workspace_file(path)`** - Delete workspace file
- **`create_workspace_directory(path)`** - Create workspace directory

## 🤖 Machine Learning & AI

### Model Serving
- **`list_serving_endpoints()`** - List serving endpoints
- **`get_serving_endpoint(endpoint_name)`** - Get endpoint details
- **`create_serving_endpoint(config)`** - Create new endpoint
- **`update_serving_endpoint(endpoint_name, updates)`** - Update endpoint
- **`delete_serving_endpoint(endpoint_name)`** - Delete endpoint
- **`query_serving_endpoint(endpoint_name, data)`** - Query endpoint

### Experiments & Model Registry
- **`list_experiments()`** - List MLflow experiments
- **`get_experiment(experiment_id)`** - Get experiment details
- **`create_experiment(config)`** - Create new experiment
- **`list_registered_models()`** - List registered models
- **`get_registered_model(model_name)`** - Get model details

### Feature Store
- **`list_feature_tables()`** - List feature tables
- **`get_feature_table(table_name)`** - Get feature table details
- **`create_feature_table(config)`** - Create new feature table

## 🏛️ Governance & Access Control

### User & Group Management
- **`list_users()`** - List all users
- **`get_user(user_id)`** - Get user details
- **`create_user(config)`** - Create new user
- **`list_groups()`** - List all groups
- **`get_group(group_id)`** - Get group details

### Service Principals
- **`list_service_principals()`** - List service principals
- **`get_service_principal(principal_id)`** - Get principal details
- **`create_service_principal(config)`** - Create new principal

### Permissions & Access Control
- **`get_permissions(resource_type, resource_id)`** - Get resource permissions
- **`set_permissions(resource_type, resource_id, permissions)`** - Set permissions
- **`update_permissions(resource_type, resource_id, changes)`** - Update permissions

## 🔍 Data Discovery & Lineage

### Search & Discovery
- **`search_catalog(query, object_type)`** - Search catalog objects
- **`get_object_usage_stats(object_name, time_range)`** - Get usage statistics
- **`list_recent_queries(limit)`** - List recent queries

### Lineage Tracking
- **`get_table_lineage(table_name, depth)`** - Get table lineage
- **`get_column_lineage(table_name, column_name)`** - Get column lineage
- **`search_lineage(query, object_type)`** - Search lineage graph

## 📊 Dashboards & Visualization

### Lakeview Dashboards
- **`list_lakeview_dashboards()`** - List Lakeview dashboards
- **`get_lakeview_dashboard(dashboard_id)`** - Get dashboard details
- **`create_lakeview_dashboard(config)`** - Create new dashboard
- **`update_lakeview_dashboard(dashboard_id, updates)`** - Update dashboard
- **`delete_lakeview_dashboard(dashboard_id)`** - Delete dashboard

### Legacy Dashboards
- **`list_dashboards()`** - List legacy dashboards
- **`get_dashboard(dashboard_id)`** - Get dashboard details
- **`create_dashboard(config)`** - Create new dashboard
- **`delete_dashboard(dashboard_id)`** - Delete dashboard

## 🔐 Secret Management

### Secret Scopes
- **`list_secret_scopes()`** - List secret scopes
- **`get_secret_scope(scope_name)`** - Get scope details
- **`create_secret_scope(scope_name, principal)`** - Create new scope
- **`delete_secret_scope(scope_name)`** - Delete scope

### Secret Operations
- **`list_secrets(scope_name)`** - List secrets in scope
- **`put_secret(scope_name, key, value)`** - Store secret
- **`get_secret(scope_name, key)`** - Retrieve secret
- **`delete_secret(scope_name, key)`** - Delete secret

## 🌐 External Storage & Credentials

### External Locations
- **`list_external_locations()`** - List external locations
- **`get_external_location(location_name)`** - Get location details
- **`create_external_location(name, url, credential, comment)`** - Create location
- **`update_external_location(location_name, updates)`** - Update location
- **`delete_external_location(location_name)`** - Delete location

### Storage Credentials
- **`list_storage_credentials()`** - List storage credentials
- **`get_storage_credential(credential_name)`** - Get credential details
- **`create_storage_credential(name, aws_role, azure_sp, comment)`** - Create credential
- **`update_storage_credential(credential_name, updates)`** - Update credential
- **`delete_storage_credential(credential_name)`** - Delete credential

## 📚 Repos & Git Integration

### Repository Management
- **`list_repos()`** - List all repositories
- **`get_repo(repo_id)`** - Get repository details
- **`create_repo(url, provider, path)`** - Create new repository
- **`update_repo(repo_id, updates)`** - Update repository
- **`delete_repo(repo_id)`** - Delete repository

### Git Operations
- **`get_repo_status(repo_id)`** - Get repository status
- **`pull_repo(repo_id)`** - Pull latest changes
- **`push_repo(repo_id, message)`** - Push local changes
- **`create_branch(repo_id, branch_name, source)`** - Create new branch
- **`delete_branch(repo_id, branch_name)`** - Delete branch
- **`list_branches(repo_id)`** - List all branches

## 📈 Monitoring & Quality

### Data Quality Monitoring
- **`list_data_quality_monitors(catalog_name)`** - List quality monitors
- **`get_data_quality_results(monitor_name, date_range)`** - Get monitor results
- **`create_data_quality_monitor(table_name, rules)`** - Create new monitor

### Audit & Compliance
- **`list_audit_logs(start_time, end_time, user_id)`** - List audit logs
- **`get_audit_log(event_id)`** - Get audit log details
- **`export_audit_logs(start_time, end_time, format)`** - Export audit logs

### Governance Rules
- **`list_governance_rules()`** - List governance rules
- **`get_governance_rule(rule_id)`** - Get rule details
- **`create_governance_rule(config)`** - Create new rule
- **`update_governance_rule(rule_id, updates)`** - Update rule
- **`delete_governance_rule(rule_id)`** - Delete rule

## 🚀 Advanced Features

### Vector Search
- **`list_vector_search_endpoints()`** - List vector search endpoints
- **`get_vector_search_endpoint(endpoint_name)`** - Get endpoint details
- **`create_vector_search_endpoint(config)`** - Create new endpoint
- **`list_vector_search_indexes(endpoint_name)`** - List indexes
- **`query_vector_search_index(index_name, query_vector, k)`** - Search vectors

### Marketplace & Delta Sharing
- **`list_marketplace_listings()`** - List marketplace listings
- **`install_marketplace_listing(listing_id, config)`** - Install listing
- **`list_shares()`** - List Delta shares
- **`get_share(share_name)`** - Get share details
- **`create_share(config)`** - Create new share

### Webhooks & Notifications
- **`list_webhooks()`** - List webhooks
- **`create_webhook(name, events, url, status)`** - Create new webhook
- **`update_webhook(webhook_id, updates)`** - Update webhook
- **`delete_webhook(webhook_id)`** - Delete webhook

## 📋 Usage Patterns

### Common Workflows

#### 1. Data Discovery
```python
# 1. List catalogs
catalogs = list_uc_catalogs()

# 2. Explore specific catalog
catalog_details = describe_uc_catalog("hive_metastore")

# 3. Explore schemas
schema_details = describe_uc_schema("hive_metastore", "default", include_columns=True)

# 4. Get table details
table_details = describe_uc_table("hive_metastore.default.users", include_lineage=True)
```

#### 2. SQL Operations
```python
# 1. List warehouses
warehouses = list_warehouses()

# 2. Execute query
result = execute_dbsql("SELECT * FROM table LIMIT 10", warehouse_id="warehouse-123")

# 3. Get query results
query_results = get_query_results(result["statement_id"])
```

#### 3. Model Serving
```python
# 1. List endpoints
endpoints = list_serving_endpoints()

# 2. Get endpoint details
endpoint = get_serving_endpoint("my-model-endpoint")

# 3. Query endpoint
prediction = query_serving_endpoint("my-model-endpoint", {"inputs": [[1, 2, 3]]})
```

## ⚡ Performance Considerations

- **Pagination**: Most list operations support pagination for large datasets
- **Lazy Loading**: Detailed information is only fetched when requested
- **Caching**: Consider implementing caching for frequently accessed metadata
- **Batch Operations**: Some operations can be batched for better performance
- **Async Operations**: Long-running operations support async patterns

## 🛡️ Security & Permissions

- **Authentication**: All tools use configured Databricks authentication
- **Permission Checks**: Tools respect Unity Catalog and workspace access controls
- **Audit Logging**: All operations are logged for compliance
- **Error Masking**: Sensitive information is not exposed in error messages

## 🔧 Error Handling

All tools follow consistent error handling patterns:

- **Success Responses**: Include `success: true` and relevant data
- **Error Responses**: Include `success: false` and detailed error information
- **Warning Logs**: Printed to console for non-critical issues
- **Exception Handling**: Comprehensive try-catch blocks with detailed error messages

## 📚 Related Documentation

- **[Getting Started](getting-started.md)** - Quick start guide and setup
- **[API Reference](api-reference.md)** - Complete tool reference
- **[Architecture](architecture.md)** - System design and implementation details
- **[Testing](testing.md)** - Testing strategies and development guidelines

---

**Next Steps**: 
- See [Getting Started](getting-started.md) for setup instructions
- Check [API Reference](api-reference.md) for detailed tool documentation
- Review [Architecture](architecture.md) for implementation details
