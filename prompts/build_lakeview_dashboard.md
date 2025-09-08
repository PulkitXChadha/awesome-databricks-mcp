---
name: build_lakeview_dashboard
description: Build comprehensive Lakeview Dashboard from Unity Catalog tables
arguments:
  - name: catalog
    description: Unity Catalog name containing source data
    required: false
    schema:
      type: string
      pattern: "^[a-zA-Z][a-zA-Z0-9_]*$"
  
  - name: schema
    description: Schema containing tables (use all tables) - mutually exclusive with table_names
    required: false
    schema:
      type: string
      pattern: "^[a-zA-Z][a-zA-Z0-9_]*$"
  
  - name: table_names
    description: Specific table names (catalog.schema.table format) - mutually exclusive with schema
    required: false
    schema:
      type: array
      items:
        type: string
        pattern: "^[a-zA-Z][a-zA-Z0-9_]*\\.[a-zA-Z][a-zA-Z0-9_]*\\.[a-zA-Z][a-zA-Z0-9_]*$"
      minItems: 1
      maxItems: 50
  
  - name: warehouse_id
    description: SQL Warehouse ID for query execution
    required: true
    schema:
      type: string
      pattern: "^[a-f0-9]{16}$"
  
  - name: dashboard_name
    description: Name for the dashboard
    required: false
    schema:
      type: string
      maxLength: 255
  
  - name: workspace_url
    description: Databricks workspace URL 
    required: true
    schema:
      type: string
      pattern: "^https://(adb-[0-9]{16}\\.[0-9]+\\.(azure|aws|gcp)?databricks\\.(net|com)|[a-zA-Z0-9][a-zA-Z0-9-]*\\.cloud\\.databricks\\.com)/?$"

mutually_exclusive:
  - [schema, table_names]
---

Create a comprehensive Lakeview Dashboard from Unity Catalog tables with optimized widgets, layouts, and production-ready deployment.

## Context

**Configuration Provided:**
- Warehouse ID: {warehouse_id}
- Workspace URL: {workspace_url}
- Catalog: {catalog}
- Schema: {schema}
- Tables: {table_names}
- Dashboard Name: {dashboard_name}

## Objective

Transform Unity Catalog data into an actionable Lakeview Dashboard by:
1. Discovering and analyzing the data structure
2. Creating optimized SQL datasets with widget expressions
3. Building responsive dashboard layouts with appropriate visualizations
4. Deploying via Databricks Asset Bundles

## Workflow

### 1: Validation & Discovery (REQUIRED FIRST)
- **STOP**: Verify workspace context and required parameters
- Explore Unity Catalog structure using `describe_uc_schema` and `describe_uc_table`
- Understand business context and key metrics to highlight
- Identify relationships between tables
- Extract configuration from existing databricks.yml if present
- Identify table relationships and data patterns
- Handle empty tables gracefully (common in dev environments)

### 2. Query Design & Validation
- **ALWAYS** Use widget-level aggregations rather than pre-aggregated datasets
- Design consolidated datasets that support multiple widgets
- Test all SQL queries with `execute_dbsql` before widget creation
- Validate column names, data types, and handle edge cases
- Design consolidated datasets supporting multiple widgets (avoid one dataset per widget)
- Implement robust SQL with COALESCE, CASE statements for NULL safety, division by zero prevention
- Use LEFT JOINs to handle missing dimension data gracefully

### 3. Dashboard Creation Strategy

**Critical Dashboard Requirements:**
- Use optimized datasets with widget expressions for flexibility
- Implement responsive grid positioning (12-column system)
- Include variety of widget types: counters, charts, tables, heatmaps
- Add descriptive titles, descriptions and formatting for all widgets
- Handle missing data scenarios gracefully

**Dataset Design Principles:**
- One dataset per logical entity (sales, customers, orders)
- Include raw dimensions for filtering and grouping
- Impement widget level aggregations through expressions over aggregations in Datasets

**Widget Expression Patterns:**
```sql
-- Aggregations in widgets, not datasets
y_expression: "SUM(revenue)"
x_expression: "DATE_TRUNC('MONTH', date)"

-- Conditional counts
"COUNT(CASE WHEN status = 'active' THEN 1 END)"

-- Percentages with safe division
"CASE WHEN SUM(total) > 0 THEN SUM(value)/SUM(total) * 100 ELSE 0 END"
```
- Optimize for performance with proper indexing hints

### 4. Dashboard Implementation
- Create dashboard using `create_dashboard_file` with validated configurations
- Design 12-column responsive grid layout
- Position KPIs at top for immediate visibility
- Add supporting charts with logical flow from overview to detail
- Include interactive filters for user exploration

**Layout Guidelines:**
- Full width: `width: 12` (for headers/separators)
- Half width: `width: 6` (side-by-side comparisons)
- Quarter width: `width: 3` (KPI cards)
- Standard height: `height: 4` (most widgets)

### 5. Deployment & Validation

- Deploys via Databricks Asset Bundles with serverless compute
- Create Databricks Asset Bundle structure
- Generate `databricks.yml` with proper configurations
- Deploy using `databricks bundle deploy`
- Monitor dashboard rendering and fix any issues
- Validate all widgets display correctly

### 6. Asset Bundle Configuration

**Critical Configuration Requirements:**
- Use `file_path` (not `serialized_dashboard`) for native dashboard resources
- Include sync exclusion to prevent duplicate dashboards:
  ```yaml
  sync:
    exclude:
      - "*.lvdash.json"
  ```
- Include proper `root_path` configuration to avoid warnings
- Use correct permission levels for dashboards (`CAN_READ`, `CAN_MANAGE`)
- Remove unsupported fields from databricks.yml (exclude/include patterns not supported in current CLI version)

**Example databricks.yml Configuration:**
```yaml
bundle:
  name: my_dashboard_bundle

workspace:
  root_path: /Workspace/Users/${workspace.current_user.userName}/dashboards

sync:
  exclude:
    - "*.lvdash.json"

resources:
  dashboards:
    my_dashboard:
      display_name: "Sales Analytics Dashboard"
      file_path: ./src/dashboard.lvdash.json
      permissions:
        - level: CAN_MANAGE
          user_name: ${workspace.current_user.userName}
        - level: CAN_READ
          group_name: analysts

targets:
  dev:
    workspace:
      host: ${workspace_url}
```
### 7. Automated Deployment & Validation
- Run `databricks bundle validate` before deployment
- Execute `databricks bundle deploy --target dev` 
- Provide `databricks bundle summary` output
- Include direct dashboard URL for immediate access
- Handle deployment errors gracefully with troubleshooting steps

## Best Practices

### Widget Selection Guide
- **Counters**: Single KPI metrics
- **Bar Charts**: Categorical comparisons
- **Line Charts**: Time series trends
- **Tables**: Detailed data exploration
- **Pie Charts**: Part-to-whole relationships
- **Heatmaps**: Two-dimensional analysis

### Error Prevention
- Verify table existence before querying
- Check column data types match widget requirements
- Test with sample data before full deployment
- Include error handling in SQL queries

## Available Tools

**Data Exploration:**
- `list_uc_schemas`, `list_uc_tables`
- `describe_uc_catalog`, `describe_uc_schema`, `describe_uc_table`
- `execute_dbsql` - Test and validate queries

**Dashboard Management:**
- `create_dashboard_file` - Create new dashboard with widgets
- `validate_dashboard_sql` - Validate SQL before dashboard creation
- `get_widget_configuration_guide` - Widget configuration reference

## Success Criteria

✓ All SQL queries execute without errors
✓ Dashboard renders with all widgets displaying data
✓ Asset Bundle deploys successfully
✓ Performance meets expectations (<3s load time)
✓ **Bundle Validation**: `databricks bundle validate` passes without errors  
✓ **Successful Deployment**: `databricks bundle deploy --target dev` completes successfully  
✓ **Resource Creation**: Dashboard appears in `databricks bundle summary --target dev` output  
✓ **Direct Access**: Dashboard URL is accessible and opens in browser via `databricks bundle open`  
✓ **Data Safety**: No SQL errors due to NULL values or missing data 
✓ **Join Integrity**: LEFT JOINs prevent data loss when dimension tables are incomplete  
✓ **Widget Field Expression**: Widget level aggregations (SUM(), COUNT(DISTINCT `field_name`) are used

## Example Dashboard Structure

```yaml
Dashboard:
  - Row 1: KPI Cards (4 counters)
  - Row 2: Revenue Trend (line chart) | Category Breakdown (bar chart)
  - Row 3: Detailed Table with Filters
  - Row 4: Geographic Distribution (map) | Top Products (horizontal bar)
```

## Notes

- Prioritize widget expressions over pre-aggregated datasets for flexibility
- Use parameterized queries for dynamic filtering
- Consider creating multiple dashboards for different user personas
- Document assumptions and data refresh schedules

Ready to build your Lakeview Dashboard! Provide any additional requirements or context to customize the implementation.