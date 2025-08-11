# Databricks SDK Tools Documentation

This document provides a comprehensive plan for implementing Databricks SDK tools in the Databricks MCP server. These tools will provide AI assistants with programmatic access to all major Databricks services and operations.

## Overview

The Databricks SDK for Python covers all public Databricks REST API operations, providing comprehensive access to:
- Unity Catalog (already implemented)
- Compute resources and clusters
- Jobs and workflows
- Machine Learning and AI
- SQL Warehouses and queries
- File management and DBFS
- Identity and access management
- And many more services

## Core Tool Categories

### 1. Compute Management Tools

#### Cluster Operations
- **`list_clusters()`** - List all clusters in the workspace
- **`get_cluster(cluster_id: str)`** - Get detailed cluster information
- **`create_cluster(cluster_config: dict)`** - Create a new cluster
- **`start_cluster(cluster_id: str)`** - Start a stopped cluster
- **`stop_cluster(cluster_id: str)`** - Stop a running cluster
- **`delete_cluster(cluster_id: str)`** - Delete a cluster
- **`resize_cluster(cluster_id: str, num_workers: int)`** - Resize cluster

#### Instance Pool Management
- **`list_instance_pools()`** - List all instance pools
- **`get_instance_pool(pool_id: str)`** - Get instance pool details
- **`create_instance_pool(pool_config: dict)`** - Create new instance pool
- **`delete_instance_pool(pool_id: str)`** - Delete instance pool

#### Cluster Policies
- **`list_cluster_policies()`** - List all cluster policies
- **`get_cluster_policy(policy_id: str)`** - Get policy details
- **`create_cluster_policy(policy_config: dict)`** - Create new policy
- **`update_cluster_policy(policy_id: str, updates: dict)`** - Update policy

### 2. Jobs and Workflows ✅

#### Job Management ✅
- **`list_jobs()`** ✅ - List all jobs in the workspace
- **`get_job(job_id: str)`** ✅ - Get detailed job information
- **`create_job(job_config: dict)`** ✅ - Create a new job
- **`update_job(job_id: str, updates: dict)`** ✅ - Update existing job
- **`delete_job(job_id: str)`** ✅ - Delete a job

#### Job Runs ✅
- **`list_job_runs(job_id: str = None)`** ✅ - List job runs (all or for specific job)
- **`get_job_run(run_id: str)`** ✅ - Get detailed run information
- **`submit_job_run(job_id: str, parameters: dict = None)`** ✅ - Submit a new job run
- **`cancel_job_run(run_id: str)`** ✅ - Cancel a running job
- **`get_job_run_logs(run_id: str)`** ✅ - Get logs from a job run

### 3. SQL Warehouses and Queries ✅

#### Warehouse Management
- **`list_warehouses()`** ✅ - List all SQL warehouses
- **`execute_dbsql(query: str, warehouse_id: str, ...)`** ✅ - Execute SQL query on warehouse
- **`get_sql_warehouse(warehouse_id: str)`** ✅ IMPLEMENTED - Get warehouse details
- **`create_sql_warehouse(warehouse_config: dict)`** ✅ IMPLEMENTED - Create new warehouse
- **`start_sql_warehouse(warehouse_id: str)`** ✅ IMPLEMENTED - Start a warehouse
- **`stop_sql_warehouse(warehouse_id: str)`** ✅ IMPLEMENTED - Stop a warehouse
- **`delete_sql_warehouse(warehouse_id: str)`** ✅ IMPLEMENTED - Delete warehouse

#### Query Operations
- **`list_queries(warehouse_id: str = None)`** ✅ IMPLEMENTED - List queries (all or for specific warehouse)
- **`get_query(query_id: str)`** ✅ IMPLEMENTED - Get query details
- **`get_query_results(query_id: str)`** ✅ IMPLEMENTED - Get query results
- **`cancel_query(query_id: str)`** ✅ IMPLEMENTED - Cancel running query

#### Statement Execution
- **`get_statement_status(statement_id: str)`** ✅ IMPLEMENTED - Get statement execution status
- **`get_statement_results(statement_id: str)`** ✅ IMPLEMENTED - Get statement results
- **`cancel_statement(statement_id: str)`** ✅ IMPLEMENTED - Cancel statement execution

### 4. Machine Learning and AI

#### Experiments
- **`list_experiments()`** - List all MLflow experiments
- **`get_experiment(experiment_id: str)`** - Get experiment details
- **`create_experiment(experiment_config: dict)`** - Create new experiment
- **`delete_experiment(experiment_id: str)`** - Delete experiment

#### Model Registry
- **`list_registered_models()`** - List all registered models
- **`get_registered_model(model_name: str)`** - Get model details
- **`create_registered_model(model_config: dict)`** - Create new model
- **`delete_registered_model(model_name: str)`** - Delete model
- **`list_model_versions(model_name: str)`** - List model versions
- **`get_model_version(model_name: str, version: str)`** - Get version details

#### Model Serving
- **`list_serving_endpoints()`** - List all serving endpoints
- **`get_serving_endpoint(endpoint_name: str)`** - Get endpoint details
- **`create_serving_endpoint(endpoint_config: dict)`** - Create new endpoint
- **`update_serving_endpoint(endpoint_name: str, updates: dict)`** - Update endpoint
- **`delete_serving_endpoint(endpoint_name: str)`** - Delete endpoint
- **`query_serving_endpoint(endpoint_name: str, data: dict)`** - Query endpoint

#### Feature Store
- **`list_feature_tables()`** - List all feature tables
- **`get_feature_table(table_name: str)`** - Get feature table details
- **`create_feature_table(table_config: dict)`** - Create new feature table
- **`delete_feature_table(table_name: str)`** - Delete feature table

### 5. File Management and DBFS ✅

#### DBFS Operations
- **`list_dbfs_path(path: str = "/")`** ✅ - List files and directories in DBFS
- **`get_dbfs_file_info(path: str)`** ✅ - Get file/directory information
- **`read_dbfs_file(path: str, offset: int = 0, length: int = None)`** ✅ - Read file content
- **`write_dbfs_file(path: str, content: bytes, overwrite: bool = False)`** ✅ - Write file content
- **`delete_dbfs_path(path: str, recursive: bool = False)`** ✅ - Delete file/directory
- **`create_dbfs_directory(path: str)`** ✅ - Create directory
- **`move_dbfs_path(source: str, destination: str)`** ✅ - Move/rename file/directory

#### Workspace Files
- **`list_workspace_files(path: str = "/")`** ✅ - List files in workspace
- **`get_workspace_file_info(path: str)`** ✅ - Get file information
- **`read_workspace_file(path: str)`** ✅ - Read workspace file
- **`write_workspace_file(path: str, content: str, language: str = None)`** ✅ - Write workspace file
- **`delete_workspace_file(path: str)`** ✅ - Delete workspace file
- **`create_workspace_directory(path: str)`** ✅ - Create workspace directory

### 6. Identity and Access Management

#### User Management
- **`list_users()`** - List all users in the workspace
- **`get_user(user_id: str)`** - Get user details
- **`create_user(user_config: dict)`** - Create new user
- **`update_user(user_id: str, updates: dict)`** - Update user
- **`delete_user(user_id: str)`** - Delete user

#### Group Management
- **`list_groups()`** - List all groups
- **`get_group(group_id: str)`** - Get group details
- **`create_group(group_config: dict)`** - Create new group
- **`update_group(group_id: str, updates: dict)`** - Update group
- **`delete_group(group_id: str)`** - Delete group
- **`add_user_to_group(user_id: str, group_id: str)`** - Add user to group
- **`remove_user_from_group(user_id: str, group_id: str)`** - Remove user from group

#### Service Principals
- **`list_service_principals()`** - List all service principals
- **`get_service_principal(principal_id: str)`** - Get service principal details
- **`create_service_principal(principal_config: dict)`** - Create new service principal
- **`update_service_principal(principal_id: str, updates: dict)`** - Update service principal
- **`delete_service_principal(principal_id: str)`** - Delete service principal

#### Permissions and Access Control
- **`get_permissions(resource_type: str, resource_id: str)`** - Get resource permissions
- **`set_permissions(resource_type: str, resource_id: str, permissions: list)`** - Set resource permissions
- **`update_permissions(resource_type: str, resource_id: str, changes: list)`** - Update permissions

### 7. Delta Live Tables and Pipelines ✅

#### Pipeline Management
- **`list_pipelines()`** ✅ - List all DLT pipelines
- **`get_pipeline(pipeline_id: str)`** ✅ - Get pipeline details
- **`create_pipeline(pipeline_config: dict)`** ✅ - Create new pipeline
- **`update_pipeline(pipeline_id: str, updates: dict)`** ✅ - Update pipeline
- **`delete_pipeline(pipeline_id: str)`** ✅ - Delete pipeline

#### Pipeline Runs
- **`list_pipeline_runs(pipeline_id: str = None)`** ✅ - List pipeline runs
- **`get_pipeline_run(run_id: str)`** ✅ - Get run details
- **`start_pipeline_update(pipeline_id: str, parameters: dict = None)`** ✅ - Start pipeline update
- **`stop_pipeline_update(pipeline_id: str)`** ✅ - Stop pipeline update

### 8. Vector Search

#### Vector Search Endpoints
- **`list_vector_search_endpoints()`** - List all vector search endpoints
- **`get_vector_search_endpoint(endpoint_name: str)`** - Get endpoint details
- **`create_vector_search_endpoint(endpoint_config: dict)`** - Create new endpoint
- **`delete_vector_search_endpoint(endpoint_name: str)`** - Delete endpoint

#### Vector Search Indexes
- **`list_vector_search_indexes(endpoint_name: str = None)`** - List indexes
- **`get_vector_search_index(index_name: str)`** - Get index details
- **`create_vector_search_index(index_config: dict)`** - Create new index
- **`delete_vector_search_index(index_name: str)`** - Delete index
- **`query_vector_search_index(index_name: str, query_vector: list, k: int = 10)`** - Search vectors

### 9. Dashboards and Visualization ✅

#### Lakeview Dashboards
- **`list_lakeview_dashboards()`** ✅ - List all Lakeview dashboards
- **`get_lakeview_dashboard(dashboard_id: str)`** ✅ - Get dashboard details
- **`create_lakeview_dashboard(dashboard_config: dict)`** ✅ - Create new dashboard
- **`update_lakeview_dashboard(dashboard_id: str, updates: dict)`** ✅ - Update dashboard
- **`delete_lakeview_dashboard(dashboard_id: str)`** ✅ - Delete dashboard

#### Legacy Dashboards
- **`list_dashboards()`** ✅ - List legacy dashboards
- **`get_dashboard(dashboard_id: str)`** ✅ - Get dashboard details
- **`create_dashboard(dashboard_config: dict)`** ✅ - Create new dashboard
- **`delete_dashboard(dashboard_id: str)`** ✅ - Delete dashboard

### 10. Alerts and Monitoring

#### SQL Alerts
- **`list_alerts()`** - List all SQL alerts
- **`get_alert(alert_id: str)`** - Get alert details
- **`create_alert(alert_config: dict)`** - Create new alert
- **`update_alert(alert_id: str, updates: dict)`** - Update alert
- **`delete_alert(alert_id: str)`** - Delete alert

#### Quality Monitors ✅
- **`list_data_quality_monitors(catalog_name: str = None)`** ✅ - List all quality monitors
- **`get_data_quality_results(monitor_name: str, date_range: str = "7d")`** ✅ - Get monitor results
- **`create_data_quality_monitor(table_name: str, rules: list)`** ✅ - Create new monitor
- **`get_quality_monitor(monitor_id: str)`** - Get monitor details
- **`delete_quality_monitor(monitor_id: str)`** - Delete monitor

### 11. Marketplace and Delta Sharing

#### Marketplace Operations
- **`list_marketplace_listings()`** - List marketplace listings
- **`get_marketplace_listing(listing_id: str)`** - Get listing details
- **`install_marketplace_listing(listing_id: str, config: dict)`** - Install listing

#### Delta Sharing
- **`list_shares()`** - List all shares
- **`get_share(share_name: str)`** - Get share details
- **`create_share(share_config: dict)`** - Create new share
- **`delete_share(share_name: str)`** - Delete share
- **`list_recipients()`** - List all recipients
- **`get_recipient(recipient_name: str)`** - Get recipient details

### 12. Settings and Configuration

#### Workspace Settings
- **`get_workspace_settings()`** - Get workspace settings
- **`update_workspace_settings(updates: dict)`** - Update workspace settings
- **`get_ip_access_lists()`** - Get IP access lists
- **`update_ip_access_lists(updates: dict)`** - Update IP access lists

#### Token Management
- **`list_tokens()`** - List all tokens
- **`create_token(comment: str = None, lifetime_seconds: int = None)`** - Create new token
- **`delete_token(token_id: str)`** - Delete token

### 13. Repos and Git Integration

#### Repository Management
- **`list_repos()`** ✅ IMPLEMENTED - List all repositories in the workspace
- **`get_repo(repo_id: str)`** ✅ IMPLEMENTED - Get repository details
- **`create_repo(url: str, provider: str, path: str = None)`** ✅ IMPLEMENTED - Create new repository
- **`update_repo(repo_id: str, updates: dict)`** ✅ IMPLEMENTED - Update repository settings
- **`delete_repo(repo_id: str)`** ✅ IMPLEMENTED - Delete repository

#### Git Operations
- **`get_repo_status(repo_id: str)`** ✅ IMPLEMENTED - Get repository status (ahead/behind)
- **`pull_repo(repo_id: str)`** ✅ IMPLEMENTED - Pull latest changes from remote
- **`push_repo(repo_id: str, message: str)`** ✅ IMPLEMENTED - Push local changes to remote
- **`create_branch(repo_id: str, branch_name: str, source_branch: str = None)`** ✅ IMPLEMENTED - Create new branch
- **`delete_branch(repo_id: str, branch_name: str)`** ✅ IMPLEMENTED - Delete branch
- **`list_branches(repo_id: str)`** ✅ IMPLEMENTED - List all branches in repository

### 14. Notebooks and Workspace Objects

#### Notebook Operations
- **`list_notebooks(path: str = "/")`** - List notebooks in workspace path
- **`get_notebook(path: str)`** - Get notebook content and metadata
- **`create_notebook(path: str, content: str, language: str = "python")`** - Create new notebook
- **`update_notebook(path: str, content: str)`** - Update notebook content
- **`delete_notebook(path: str)`** - Delete notebook
- **`move_notebook(source: str, destination: str)`** - Move notebook to new location

#### Workspace Object Management
- **`list_workspace_objects(path: str = "/")`** - List all workspace objects
- **`get_workspace_object_info(path: str)`** - Get object metadata
- **`export_workspace_object(path: str, format: str = "source")`** - Export object
- **`import_workspace_object(path: str, content: str, format: str = "source")`** - Import object

### 15. Secret Management

#### Secret Scopes
- **`list_secret_scopes()`** - List all secret scopes
- **`get_secret_scope(scope_name: str)`** - Get secret scope details
- **`create_secret_scope(scope_name: str, initial_manage_principal: str = None)`** - Create new scope
- **`delete_secret_scope(scope_name: str)`** - Delete secret scope

#### Secret Operations
- **`list_secrets(scope_name: str)`** - List secrets in scope
- **`put_secret(scope_name: str, key: str, value: str)`** - Store secret value
- **`get_secret(scope_name: str, key: str)`** - Get secret value
- **`delete_secret(scope_name: str, key: str)`** - Delete secret
- **`list_secret_acls(scope_name: str)`** - List access control for scope
- **`put_secret_acl(scope_name: str, principal: str, permission: str)`** - Set access permission

### 16. External Locations and Credentials

#### External Locations
- **`list_external_locations()`** - List all external locations
- **`get_external_location(location_name: str)`** - Get location details
- **`create_external_location(name: str, url: str, credential_name: str, comment: str = None)`** - Create new location
- **`update_external_location(location_name: str, updates: dict)`** - Update location
- **`delete_external_location(location_name: str)`** - Delete location

#### External Credentials
- **`list_external_credentials()`** - List all external credentials
- **`get_external_credential(credential_name: str)`** - Get credential details
- **`create_external_credential(name: str, aws_iam_role: str = None, azure_service_principal: dict = None, comment: str = None)`** - Create new credential
- **`update_external_credential(credential_name: str, updates: dict)`** - Update credential
- **`delete_external_credential(credential_name: str)`** - Delete credential

### 17. Metastore Operations

#### Metastore Management
- **`list_metastores()`** - List all metastores in the account
- **`get_metastore(metastore_id: str)`** - Get metastore details
- **`create_metastore(name: str, storage_root: str, owner: str = None)`** - Create new metastore
- **`update_metastore(metastore_id: str, updates: dict)`** - Update metastore
- **`delete_metastore(metastore_id: str, force: bool = False)`** - Delete metastore
- **`assign_metastore_to_workspace(metastore_id: str, workspace_id: str)`** - Assign metastore to workspace

#### Metastore Assignments
- **`list_metastore_assignments(workspace_id: str = None)`** - List metastore assignments
- **`get_metastore_assignment(workspace_id: str)`** - Get assignment details
- **`update_metastore_assignment(workspace_id: str, metastore_id: str)`** - Update assignment

### 18. Account-level Operations

#### Account Management
- **`get_account_info()`** - Get account information
- **`list_account_workspaces()`** - List all workspaces in account
- **`get_account_workspace(workspace_id: str)`** - Get workspace details
- **`create_account_workspace(workspace_name: str, aws_region: str = None, credentials_id: str = None)`** - Create new workspace
- **`delete_account_workspace(workspace_id: str)`** - Delete workspace

#### Account-level Settings
- **`get_account_settings()`** - Get account settings
- **`update_account_settings(updates: dict)`** - Update account settings
- **`list_account_groups()`** - List account-level groups
- **`list_account_users()`** - List account-level users

### 19. Webhooks and Notifications

#### Webhook Management
- **`list_webhooks()`** - List all webhooks
- **`get_webhook(webhook_id: str)`** - Get webhook details
- **`create_webhook(name: str, events: list, url: str, status: str = "ACTIVE")`** - Create new webhook
- **`update_webhook(webhook_id: str, updates: dict)`** - Update webhook
- **`delete_webhook(webhook_id: str)`** - Delete webhook

#### Webhook Events
- **`list_webhook_events(webhook_id: str = None)`** - List webhook events
- **`get_webhook_event(event_id: str)`** - Get event details
- **`resend_webhook_event(event_id: str)`** - Resend failed webhook event

### 20. Audit and Compliance

#### Audit Logs
- **`list_audit_logs(start_time: str = None, end_time: str = None, user_id: str = None)`** ✅ IMPLEMENTED - List audit logs
- **`get_audit_log(event_id: str)`** ✅ IMPLEMENTED - Get audit log details
- **`export_audit_logs(start_time: str, end_time: str, format: str = "json")`** ✅ IMPLEMENTED - Export audit logs

#### Compliance and Governance
- **`list_governance_rules()`** ✅ IMPLEMENTED - List governance rules
- **`get_governance_rule(rule_id: str)`** ✅ IMPLEMENTED - Get rule details
- **`create_governance_rule(rule_config: dict)`** ✅ IMPLEMENTED - Create new rule
- **`update_governance_rule(rule_id: str, updates: dict)`** ✅ IMPLEMENTED - Update rule
- **`delete_governance_rule(rule_id: str)`** ✅ IMPLEMENTED - Delete rule

### 21. Data Lineage and Discovery

#### Lineage Operations
- **`get_table_lineage(table_name: str, depth: int = 1)`** ✅ IMPLEMENTED - Get table lineage information
- **`get_column_lineage(table_name: str, column_name: str)`** ✅ IMPLEMENTED - Get column-level lineage
- **`search_lineage(query: str, object_type: str = None)`** ✅ IMPLEMENTED - Search lineage graph

#### Data Discovery
- **`search_catalog(query: str, object_type: str = None)`** ✅ IMPLEMENTED - Search catalog objects
- **`get_object_usage_stats(object_name: str, time_range: str = "30d")`** ✅ IMPLEMENTED - Get usage statistics
- **`list_recent_queries(limit: int = 100)`** ✅ IMPLEMENTED - List recent queries

### 22. Performance and Optimization

#### Query Performance
- **`get_query_performance(query_id: str)`** - Get query performance metrics
- **`list_slow_queries(warehouse_id: str = None, time_range: str = "7d")`** - List slow queries
- **`get_warehouse_performance(warehouse_id: str, time_range: str = "24h")`** - Get warehouse performance

#### Resource Optimization
- **`get_cluster_utilization(cluster_id: str, time_range: str = "24h")`** - Get cluster utilization
- **`get_storage_usage(path: str = "/")`** - Get storage usage statistics
- **`optimize_table(table_name: str, optimization_type: str = "auto")`** - Optimize table

## Implementation Considerations

### Authentication and Security
- All tools should respect existing authentication mechanisms
- Implement proper error handling for authentication failures
- Support both workspace and account-level operations where applicable

### Rate Limiting and Performance
- Implement appropriate rate limiting for API calls
- Use pagination for list operations
- Cache frequently accessed metadata

### Error Handling
- Provide clear error messages for common failure scenarios
- Implement retry logic for transient failures
- Log all operations for debugging and audit purposes

### Data Validation
- Validate all input parameters before making API calls
- Implement proper type checking for complex configurations
- Provide helpful error messages for validation failures

## Tool Naming Convention

All tools should follow the existing naming convention:
- Use snake_case for function names
- Prefix with service category when needed (e.g., `ml_`, `sql_`, `dbfs_`)
- Use descriptive names that clearly indicate the operation
- Maintain consistency with existing Unity Catalog tools

## Priority Implementation Order

1. **High Priority** (Core Infrastructure)
   - Compute management (clusters, instance pools)
   - Jobs and workflows
   - SQL warehouses and queries
   - Repos and Git integration
   - Notebooks and workspace objects

2. **Medium Priority** (Data Operations)
   - File management (DBFS, workspace files)
   - Machine Learning (experiments, model registry)
   - Delta Live Tables
   - Secret management
   - External locations and credentials

3. **Lower Priority** (Advanced Features)
   - Vector Search
   - Marketplace operations
   - Advanced monitoring and alerts
   - Account-level operations
   - Webhooks and notifications
   - Audit and compliance
   - Data lineage and discovery
   - Performance optimization

## Testing Strategy

- Unit tests for each tool function
- Integration tests with mock Databricks API responses
- End-to-end tests with real Databricks workspace (when available)
- Performance testing for list operations and large datasets

## Documentation Requirements

Each tool should include:
- Clear parameter descriptions
- Return value specifications
- Usage examples
- Error handling information
- Related tool references

This comprehensive toolset will provide AI assistants with full programmatic access to Databricks capabilities, enabling them to help users manage and operate their Databricks environment effectively.
