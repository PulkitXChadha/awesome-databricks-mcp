# Build Comprehensive Lakeview Dashboard

I can help you build a Lakeview Dashboard from the set of Unity Catalog Tables. This tool will guide you the transforming your data into actionable business insights through automated dashboard creation with comprehensive widget selection, optimal layout design, and production deployment validation.

## Features
- **User Requirements Gathering**: **FIRST** ask user for catalog, schema, specific tables/views to analyze, and SQL warehouse ID
- **Data Discovery**: Explore Unity Catalog structure (`describe_uc_schema`, `describe_uc_table`)
- **Query Validation**: Test SQL with `execute_dbsql` - validate syntax, performance, results
- **Widget Creation**: Build widgets with validated data and proper configuration
- **Dashboard Deployment**: Deploy to Databricks with continuous monitoring
- **Error Resolution**: Iteratively fix issues until all widgets render correctly

## How to Use

To build your Lakeflow Dashboard, I'll need information the following information: 

- **Catalog**: Unity Catalog name containing your data
- **Schema**: Schema containing the tables to visualize  
- **Warehouse ID**: SQL warehouse ID for query execution
- **Dashboard Name**: Name for your dashboard
- **Tables**: List of tables/views to analyze (auto-discovered if not provided)
- **Target Workspace**: [specify workspace URL, e.g., https://<workspace-deployment-name>.cloud.databricks.com/]
- **Business Context**: [describe the business use case and target audience]
- **Key Metrics**: [list 3-5 primary KPIs to highlight

## CRITICAL REQUIREMENTS (MANDATORY)

### User Input Collection (FIRST STEP - NEVER SKIP)
- **ALWAYS** ask the user to specify:
  1. **Databricks Profile Name** (run `databricks auth profiles` if unknown)
  2. **Source tables/views** with full three-part names (catalog.schema.table)
  3. **SQL warehouse ID** with validation
  4. **Target workspace URL** for verification
- **VALIDATE** profile connectivity before proceeding with data discovery
- **NEVER** proceed with data discovery or tool execution until user provides table information AND warehouse ID
- **ALWAYS** confirm catalog, schema, specific tables to analyze, and SQL warehouse ID with the user first

### Widget Expression Validation
- **ALWAYS** validate that aggregations use widget expressions, not dataset pre-aggregation
- **TEST** widget expressions with sample queries: `SELECT SUM(field), COUNT(DISTINCT field) FROM table`
- **VERIFY** date functions work: `SELECT DATE_TRUNC('WEEK', date_field) FROM table`
- **CONFIRM** conditional logic: `SELECT COUNT(CASE WHEN condition THEN 1 END) FROM table`

### Data Validation (NEVER SKIP)
- **ALWAYS** test ALL SQL queries with `execute_dbsql` before creating ANY widgets
- **ALWAYS** verify column names exist in query results using `describe_uc_table`
- **ALWAYS** check data types match widget requirements
- **ALWAYS** handle NULL values: `COALESCE(field, 0)` or `CASE WHEN field IS NOT NULL`
- **ALWAYS** prevent division by zero: `CASE WHEN denominator > 0 THEN value/denominator ELSE 0 END`
- **ALWAYS**: Create consolidated datasets that can support multiple widget types (avoid 1:1 dataset-to-widget mapping)

### Dashboard Configuration (MANDATORY)
- **ALWAYS** create exactly ONE .lvdash.json file in `src/` directory
- **ALWAYS** create widgets with business focurse legends and axis names
- **NEVER** hard-code email addresses or user names
- **NEVER** create widgets wider than 6 columns
- **ALWAYS** specify position coordinates (x, y, width, height)

## 🎯 WIDGET EXPRESSIONS - PRIMARY APPROACH (MANDATORY)

### Core Principle: Raw Data + Widget Expressions
- **NEVER** pre-aggregate data in datasets
- **ALWAYS** provide raw, granular data in datasets
- **IMPLEMENT** all aggregations using widget expressions
- **LEVERAGE** Lakeview's native aggregation engine for optimal performance

### Required Widget Expression Patterns
- **Counters**: `SUM(field)`, `COUNT(DISTINCT field)`, `AVG(field)`
- **Conditional Counts**: `COUNT(CASE WHEN condition THEN 1 END)`
- **Charts**: Use `y_expression: "SUM(field)"` for aggregated values
- **Time Series**: `DATE_TRUNC('WEEK', date_field)` for time grouping
- **Histograms**: `BIN_FLOOR(field, bin_size)` for distribution analysis

### Dataset Design Philosophy
- **One dataset per logical entity** (sales, customers, orders)
- **Include all raw dimensions** needed for filtering and grouping
- **Avoid pre-calculated fields** like totals, averages, or counts
- **Let widgets handle aggregation** through expressions

**Why This Matters**: Widget expressions provide better performance, more flexibility, and easier maintenance than pre-aggregated datasets. This is a Lakeview best practice that should be the default approach.

## What You'll Get
### Deliverables

1. **Complete .lvdash.json File**: Production-ready dashboard in `src/` directory
2. **Optimized SQL Datasets**: Consolidated queries supporting multiple widgets
3. **Asset Bundle Structure**: `databricks.yml` with parameterized users
4. **Deploy in Databricks Workspace Bundle**: Deployed dashboard with working URL
5. Documentation (README.md)

## **🏗️ ASSET BUNDLE BEST PRACTICES**
- Use `file_path` (not `serialized_dashboard`) for native dashboard resources
- CRITICAL: Include sync exclusion to prevent duplicate dashboards:
  sync:
    exclude:
      - "*.lvdash.json" 
- Include proper `root_path` configuration to avoid warnings
- Use correct permission levels for dashboards (CAN_READ, CAN_MANAGE)
- Target workspace: field-eng-east (https://adb-984752964297111.11.azuredatabricks.net/)
- **IMPORTANT**: Remove unsupported fields from databricks.yml (exclude, include patterns not supported in current CLI version)

## Data Quality & Performance

### Safe SQL Patterns (REQUIRED)
```sql
-- Handle null values safely
COALESCE(field, 0) AS safe_field

-- Prevent division by zero  
CASE WHEN total > 0 THEN value/total ELSE 0 END AS percentage

```

### Layout Best Practices
- **12-column responsive grid** with consistent spacing
- **KPIs at top** for immediate visibility
- **Logical flow** from overview to detail
- **Filters prominently placed** for easy access


## Implementation Steps

1. **Requirements Collection**: **MANDATORY FIRST STEP** - Ask user for catalog, schema, table names, and SQL warehouse ID
2. **Data Discovery**: Use `describe_uc_schema`, `describe_uc_table` to explore structure
3. **Query Validation**: Test ALL SQL with `execute_dbsql` before widget creation  
4. **Dashboard Creation**: Use `create_lakeview_dashboard` with validated queries
5. **Widget Building**: Start with KPIs, add supporting charts, configure filters
6. **Deployment & Monitoring**: Deploy and monitor until all widgets render successfully

## **Deployment Requirements**
- **Asset Bundle**: Create Databricks Asset Bundle for version control
- **Parameterization**: Use ${workspace.current_user.userName} for all user references
- **Environment**: [specify target environment, e.g., dev/prod]
- **Permissions**: [specify permission levels needed]

## Common Error Fixes

### Missing Columns
```sql
-- Get actual schema first
DESCRIBE TABLE catalog.schema.table;

-- Update query with correct columns  
SELECT correct_column_name AS expected_name
FROM catalog.schema.table;
```

### Data Type Mismatches
```sql
-- Cast to appropriate types
SELECT CAST(string_number AS DOUBLE) AS numeric_value
FROM source_table;
```

## 🛠️ Available Tools

### Data Exploration
- `describe_uc_schema`, `describe_uc_table` - Analyze data structure
- `execute_dbsql` - Test and validate SQL queries

### Dashboard & Widget Creation  
- `create_lakeview_dashboard` - Build new dashboard
- `get_lakeview_dashboard` - Monitor dashboard status
- Widget functions: bar charts, line charts, counters, tables, filters

## Key Resources

- **[Lakeview Dashboards](https://docs.databricks.com/en/dashboards/lakeview/index.html)**: Complete guide
- **[Asset Bundles](https://docs.databricks.com/en/dev-tools/bundles/index.html)**: Deployment framework
- **[Unity Catalog](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)**: Data governance

---

**Remember**: This tool provides end-to-end dashboard creation from data discovery to production deployment. Always validate SQL queries first, use consolidated datasets for efficiency, and monitor until complete success.

Just describe your source tables and requirements, and I'll build a complete Lakeflow Dashboard and Asset Bundle deployment for you!