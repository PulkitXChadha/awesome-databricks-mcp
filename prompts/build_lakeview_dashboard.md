# Build Comprehensive Lakeview Dashboard

Transform your data into actionable business insights through automated dashboard creation with comprehensive widget selection, optimal layout design, and production deployment validation.

## CRITICAL REQUIREMENTS (MANDATORY)

### User Input Collection (FIRST STEP - NEVER SKIP)
- **ALWAYS** ask the user to specify source tables/views AND SQL warehouse ID BEFORE making ANY tool calls
- **NEVER** proceed with data discovery or tool execution until user provides table information AND warehouse ID
- **ALWAYS** confirm catalog, schema, specific tables to analyze, and SQL warehouse ID with the user first

### Data Validation (NEVER SKIP)
- **ALWAYS** test ALL SQL queries with `execute_dbsql` before creating ANY widgets
- **ALWAYS** verify column names exist in query results using `describe_uc_table`
- **ALWAYS** check data types match widget requirements
- **ALWAYS** handle NULL values: `COALESCE(field, 0)` or `CASE WHEN field IS NOT NULL`
- **ALWAYS** prevent division by zero: `CASE WHEN denominator > 0 THEN value/denominator ELSE 0 END`

### Dashboard Configuration (MANDATORY)
- **ALWAYS** create exactly ONE .lvdash.json file in `src/` directory
- **NEVER** hard-code email addresses or user names
- **NEVER** create widgets wider than 12 columns

### Widget Best Practices (REQUIRED)
- **ALWAYS** provide descriptive widget and axis titles for user clarity
- **ALWAYS** use widget expressions for aggregations (SUM, AVG, COUNT)
- **ALWAYS** specify position coordinates (x, y, width, height)
- **ALWAYS** test filter interactions between widgets

## Workflow Process

1. **User Requirements Gathering**: **FIRST** ask user for catalog, schema, specific tables/views to analyze, and SQL warehouse ID
2. **Data Discovery**: Explore Unity Catalog structure (`describe_uc_schema`, `describe_uc_table`)
3. **Query Validation**: Test SQL with `execute_dbsql` - validate syntax, performance, results
4. **Widget Creation**: Build widgets with validated data and proper configuration
5. **Dashboard Deployment**: Deploy to Databricks with continuous monitoring
6. **Error Resolution**: Iteratively fix issues until all widgets render correctly

## Success Criteria

Dashboard is complete ONLY when:
- ALL widgets display data without errors
- All filters and interactions work correctly

## How to Use

To build your Lakeflow Declarative Pipeline, I'll need information about your source tables and configuration preferences: 

### Required Information

#### Essential Configuration
- **catalog**: Unity Catalog name containing your data
- **schema**: Schema containing the tables to visualize  
- **warehouse_id**: SQL warehouse ID for query execution
- **dashboard_name**: Name for your dashboard
- **tables**: List of tables/views to analyze (auto-discovered if not provided)

## What You'll Get
### Deliverables

1. **Complete .lvdash.json File**: Production-ready dashboard in `src/` directory
2. **Optimized SQL Datasets**: Consolidated queries supporting multiple widgets
3. **Asset Bundle Structure**: `databricks.yml` with parameterized users
4. **Continuous Monitoring**: Until all widgets render successfully

## Data Quality & Performance

### Safe SQL Patterns (REQUIRED)
```sql
-- Handle null values safely
COALESCE(field, 0) AS safe_field

-- Prevent division by zero  
CASE WHEN total > 0 THEN value/total ELSE 0 END AS percentage

-- Pre-aggregate for performance
WITH daily_summary AS (
    SELECT date, SUM(COALESCE(value, 0)) as total
    FROM transactions 
    WHERE date >= CURRENT_DATE - 30
    GROUP BY date
)
SELECT * FROM daily_summary LIMIT 10000
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

## Continuous Monitoring

The dashboard building process continues iteratively until all success criteria are met:

1. **Deploy Dashboard**: Create dashboard with validated configuration
2. **Monitor Status**: Check dashboard state and widget rendering
3. **Auto-Fix Errors**: Apply automated fixes for common issues:
   - Missing columns → Update SQL queries with correct column names
   - Data type mismatches → Add proper casting
4. **Validate Success**: Confirm all widgets render without errors
5. **Repeat Until Complete**: Continue monitoring until fully successful

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