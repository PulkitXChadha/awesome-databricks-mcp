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

mutually_exclusive:
  - [schema, table_names]
---

Create a comprehensive Lakeview Dashboard from Unity Catalog tables with optimized widgets, layouts, and production-ready deployment.

## Context

**Configuration Provided:**
- Warehouse ID: ${warehouse_id}
- Catalog: ${catalog}
- Schema: ${schema}
- Tables: ${table_names}
- Dashboard Name: ${dashboard_name}

## Objective

Transform Unity Catalog data into an actionable Lakeview Dashboard by:
1. Discovering and analyzing the data structure
2. Creating optimized SQL datasets with widget expressions
3. Building responsive dashboard layouts with appropriate visualizations
4. Deploying via Databricks Asset Bundles

## Workflow

### 1. Data Discovery & Requirements
- Gather missing configuration details (catalog, schema, tables if not provided)
- Explore Unity Catalog structure using `describe_uc_schema` and `describe_uc_table`
- Understand business context and key metrics to highlight
- Identify relationships between tables

### 2. Query Design & Validation
- Design consolidated datasets that support multiple widgets
- Test all SQL queries with `execute_dbsql` before widget creation
- Validate column names, data types, and handle edge cases
- Implement safe SQL patterns (NULL handling, division by zero prevention)

### 3. Dashboard Creation Strategy

**Dataset Design Principles:**
- One dataset per logical entity (sales, customers, orders)
- Include raw dimensions for filtering and grouping
- Let widgets handle aggregation through expressions
- Optimize for performance with proper indexing hints

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
      host: https://adb-984752964297111.11.azuredatabricks.net/
```

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
✓ Layout is responsive and user-friendly
✓ Asset Bundle deploys successfully
✓ Performance meets expectations (<3s load time)

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