# Build Lakeview Dashboard

I can help you build a Lakeview Dashboard, transforming your data into actionable insights with production-ready Databricks Lakeview dashboards. This tool provides a systematic approach to building, validating, deploying, and continuously monitoring comprehensive dashboards that deliver real business value.

## Core Capabilities

- **Data Discovery & Validation**: Automated exploration of data characteristics, including joins and relationships between Unity Catalog tables and schemas with SQL query testing
- **Smart Widget Selection**: 20+ widget types optimized for your data characteristics  
- **Production Deployment**: Complete setup including permissions, scheduling
- **Continuous Monitoring**: Iterative error resolution until successful deployment
- **Error Prevention**: Proactive validation at every step to prevent runtime failures

## How to Use

To build your production-ready Lakeview Dashboard, provide the following information:

### Required Information
- **dashboard_name**: Name for your dashboard (e.g., "Sales Performance Dashboard")
- **purpose**: "executive_reporting | operational_monitoring | analytics_exploration | realtime_tracking"
- **data_sources**: List of Unity Catalog tables/views ["catalog.schema.table", ...]
- **key_metrics**: Primary KPIs to display ["revenue", "orders", "customer_satisfaction", ...]
- **audience**: Target users "executives | analysts | operations_teams | data_scientists"
- **sql_warehouse_id**: SQL warehouse ID for query execution
- **refresh_schedule**: Dashboard refresh frequency (e.g., "0 */6 * * *" for every 6 hours)

### Optional Configuration
- **filters_required**: Interactive filters needed ["date_range", "region", "product_category"]
- **drill_down_paths**: Navigation requirements between dashboards
- **alert_thresholds**: Values that trigger notifications

## Automated Deployment Workflow

The tool will execute a comprehensive deployment pipeline:

### Phase 1: Data Discovery & Validation
1. **Analyze input table schemas** and data characteristics, including joins and relationships between the tables.
2. **Write Dataset SQL queries** to support the widgets needed.
2. **Test SQL queries** for performance and validate the result data.

### Phase 2: Dashboard Creation & Configuration
1. **Create base dashboard** with proper metadata
2. **Build core widgets** starting with primary KPIs
3. **Add supporting visualizations** for context
4. **Configure interactive filters** and parameters
5. **Optimize layout** for target devices

### Phase 3: Deployment & Monitoring
1. **Deploy dashboard** to production environment
2. **Configure permissions** and access controls
3. **Set refresh schedules** for automated updates
4. **Monitor execution** continuously until success
5. **Resolve errors** iteratively with automated fixes

## Success Criteria ✅

A dashboard is considered successfully deployed when:
- **Dashboard State**: "ACTIVE" and accessible via URL
- **Widget Rendering**: All widgets display data without errors
- **Query Performance**: All queries complete within 10 seconds
- **Data Freshness**: Refresh schedule executing successfully
- **User Access**: Target audience can view and interact
- **Mobile Response**: Dashboard renders correctly on all devices
- **No ERROR Events**: Clean execution history in monitoring logs

## Widget Selection Guide

### Quantitative Data Visualization
- **Bar Charts**: Categorical comparisons, rankings, discrete values
- **Line Charts**: Time series trends, progression over time
- **Area Charts**: Cumulative trends, stacked categories
- **Scatter Plots**: Correlation analysis, outlier detection
- **Histograms**: Distribution analysis, frequency patterns
- **Heatmaps**: Matrix correlations, time-based patterns
- **Funnel Charts**: Conversion analysis, process flows
- **Box Plots**: Statistical distributions, quartile analysis

### KPI & Summary Widgets
- **Counters**: Single key metrics, totals, current values
- **Delta Counters**: Change indicators with trend arrows
- **Gauge Charts**: Progress towards targets
- **Bullet Charts**: Performance against benchmarks

### Data Display & Analysis
- **Data Tables**: Detailed record views, drill-down capabilities
- **Pivot Tables**: Cross-tabular analysis, multi-dimensional summaries
- **Combo Charts**: Multiple metrics with different scales
- **TreeMaps**: Hierarchical data visualization

### Interactive Controls
- **Dropdown Filters**: Single/multi-select options
- **Date Range Selectors**: Temporal filtering
- **Slider Controls**: Numeric range selection
- **Text Search**: Free-form filtering
- **Radio Buttons**: Exclusive option selection
- **Checkboxes**: Multiple option selection

### Supplementary Elements
- **Text Widgets**: Markdown documentation, instructions
- **Image Widgets**: Logos, diagrams, infographics
- **IFrame Widgets**: Embedded external content
- **Divider Lines**: Visual section separation

## Critical Validation Rules (MANDATORY)

### SQL Query Validation
- **ALWAYS** test queries with `execute_dbsql` before widget creation
- **ALWAYS** verify column names exist in query results
- **ALWAYS** check data types match widget requirements
- **NEVER** create widgets without validating underlying data
- **ALWAYS** handle NULL values with COALESCE or CASE statements
- **ALWAYS** prevent division by zero errors in calculations

### Widget Configuration Rules
- **ALWAYS** specify position coordinates (x, y, width, height)
- **ALWAYS** provide descriptive widget names for clarity
- **ALWAYS** validate dataset queries return expected columns
- **NEVER** hardcode values that should be parameters
- **NEVER** create widgets larger than 12 columns wide
- **ALWAYS** test filter interactions between widgets

### Data Quality Best Practices
```sql
-- Handle null values safely
COALESCE(field, 0) AS safe_field

-- Prevent division by zero
CASE WHEN total > 0 THEN value/total ELSE 0 END AS percentage

-- Ensure proper date formatting
DATE_FORMAT(date_column, 'yyyy-MM-dd') AS formatted_date

-- Truncate long text for display
LEFT(description, 50) AS short_description

-- Handle missing joins gracefully
IFNULL(t2.value, 'N/A') AS safe_value

-- Aggregate safely with proper grouping
SUM(COALESCE(amount, 0)) AS total_amount
```

### Performance Optimization Patterns
```sql
-- Use proper indexing hints
SELECT /*+ INDEX(orders idx_date) */ 
    date, SUM(revenue) 
FROM orders 
WHERE date >= CURRENT_DATE - 30

-- Limit data for initial load
SELECT * FROM large_table 
LIMIT 1000

-- Pre-aggregate for performance
WITH daily_summary AS (
    SELECT date, SUM(value) as total
    FROM transactions
    GROUP BY date
)
SELECT * FROM daily_summary
```

### Layout Optimization
- **Grid System**: 12-column responsive layout with consistent spacing
- **Visual Hierarchy**: Most important metrics prominently placed
- **Logical Grouping**: Related widgets organized by business function
- **Mobile Responsive**: Optimized for various screen sizes
- **Loading Order**: Critical KPIs first, details last
- **White Space**: Proper spacing between widget groups

## Dashboard Layout Patterns

### Executive Dashboard
```
+------------------+------------------+------------------+
| KPI Counter      | KPI Counter      | KPI Counter      |
| (2x2)           | (2x2)           | (2x2)           |
+------------------+------------------+------------------+
| Trend Line Chart                   | Status Pie Chart |
| (8x4)                             | (4x4)           |
+----------------------------------+------------------+
| Top Items Bar Chart               | Geographic Map   |
| (6x4)                            | (6x4)           |
+----------------------------------+------------------+
```

### Operational Dashboard
```
+----------------------------------+------------------+
| Real-time Metrics Area Chart     | Current Status   |
| (8x4)                           | Counter (4x2)    |
+----------------------------------+------------------+
| Detailed Data Table              | Alert Filters    |
| (8x6)                           | (4x6)           |
+----------------------------------+------------------+
```

### Analytical Dashboard
```
+------------------+------------------+------------------+
| Filter Controls  | Filter Controls  | Filter Controls  |
| (4x2)           | (4x2)           | (4x2)           |
+------------------+------------------+------------------+
| Main Analysis Chart                                 |
| (12x6)                                             |
+---------------------------------------------------+
| Supporting Chart 1 | Supporting Chart 2 | Details |
| (4x4)             | (4x4)             | Table   |
|                   |                   | (4x4)   |
+------------------+------------------+----------+
```

## Implementation Workflow

### Phase 1: Data Discovery & Validation
1. **Explore Unity Catalog**: Use `describe_uc_schema`, `describe_uc_table`
2. **Analyze Data Structure**: Review column types, constraints, and relationships
3. **Test SQL Queries**: Execute with `execute_dbsql` to validate syntax and results
4. **Assess Data Quality**: Check completeness, consistency, and update frequency

### Phase 2: Dashboard Creation
1. **Create Base Dashboard**: Use `create_lakeview_dashboard` with proper configuration
2. **Implement Core Widgets**: Start with primary KPIs and summary visualizations
3. **Add Detail Views**: Include supporting charts and detailed data tables
4. **Configure Filters**: Implement interactive filtering capabilities

### Phase 3: Validation & Deployment
1. **Test All Components**: Verify widgets render correctly with real data
2. **Validate Interactions**: Test filters, drill-downs, and user interactions
3. **Configure Permissions**: Set up proper access controls and sharing
4. **Deploy & Monitor**: Publish dashboard and monitor performance

## Continuous Monitoring Workflow

### Automated Dashboard Monitoring
I will continuously monitor your dashboard deployment until it achieves complete success:

```python
# Step 1: Deploy dashboard with initial configuration
dashboard_config = prepare_dashboard_config(requirements)
dashboard_id = create_lakeview_dashboard(dashboard_config)
print(f"📊 Dashboard created: {dashboard_id}")

# Step 2: Monitor continuously until successful
monitoring_attempts = 0
while monitoring_attempts < MAX_ATTEMPTS:
    dashboard_status = get_lakeview_dashboard(dashboard_id)
    
    if dashboard_status['state'] == 'ACTIVE':
        # Validate all components
        validation_results = {
            'widgets_rendering': check_all_widgets_render(dashboard_id),
            'queries_performant': verify_query_performance(dashboard_id),
            'filters_working': test_filter_interactions(dashboard_id),
            'data_fresh': check_data_freshness(dashboard_id),
            'mobile_ready': test_mobile_rendering(dashboard_id)
        }
        
        if all(validation_results.values()):
            print("✅ Dashboard successfully deployed and validated!")
            print(f"🔗 Access URL: {dashboard_status['url']}")
            break
    
    # Handle errors with automated fixes
    if 'errors' in dashboard_status:
        print(f"❌ Error detected: {dashboard_status['errors'][0]}")
        
        error_type = classify_error(dashboard_status['errors'][0])
        
        if error_type == 'MISSING_COLUMN':
            print("🔧 Fixing: Updating SQL queries with correct column names...")
            fix_column_references(dashboard_id)
        
        elif error_type == 'PERMISSION_DENIED':
            print("🔧 Fixing: Granting required permissions...")
            grant_dashboard_permissions(dashboard_id)
        
        elif error_type == 'QUERY_TIMEOUT':
            print("🔧 Fixing: Optimizing slow queries...")
            optimize_dashboard_queries(dashboard_id)
        
        elif error_type == 'WIDGET_CONFIG_ERROR':
            print("🔧 Fixing: Reconfiguring widget settings...")
            reconfigure_widgets(dashboard_id)
        
        elif error_type == 'DATA_TYPE_MISMATCH':
            print("🔧 Fixing: Adjusting data type conversions...")
            fix_data_type_issues(dashboard_id)
        
        # Apply fixes and redeploy
        update_lakeview_dashboard(dashboard_id, fixes)
    
    print(f"⏳ Monitoring attempt {monitoring_attempts + 1}...")
    monitoring_attempts += 1
    sleep(10)

# Step 3: Final comprehensive validation
print("🔍 Running final validation suite...")
final_checks = run_comprehensive_dashboard_tests(dashboard_id)
report_dashboard_health(final_checks)
```

### Critical Monitoring Points
1. **Widget Rendering**: Every widget must display data without errors
2. **Query Performance**: All queries complete within 10 seconds
3. **Filter Functionality**: All filters interact correctly with widgets
4. **Data Accuracy**: Values match source data with proper aggregations
5. **Mobile Responsiveness**: Dashboard adapts to different screen sizes
6. **Permission Access**: Target users can view and interact with dashboard

## Error Prevention & Resolution

### Proactive Error Prevention
Before creating any widget, I will:
1. **Validate SQL Query**: Test with `execute_dbsql` to ensure it returns data
2. **Check Column Names**: Verify all referenced columns exist in results
3. **Test Data Types**: Ensure data types match widget requirements
4. **Verify Permissions**: Confirm access to all referenced tables
5. **Optimize Performance**: Add appropriate filters and aggregations

### Common Issues & Automated Solutions

#### Missing Column Errors
**Detection**: "Column 'name' not found in query results"
**Automated Fix**:
```sql
-- Step 1: Get actual schema
DESCRIBE TABLE catalog.schema.table;

-- Step 2: Update query with correct columns
SELECT 
    correct_column_name AS expected_name,
    COALESCE(nullable_column, 0) AS safe_value
FROM catalog.schema.table;
```

#### Query Performance Issues
**Detection**: Widget loading spinner > 10 seconds
**Automated Fix**:
```sql
-- Add time-based filtering
WHERE date_column >= CURRENT_DATE - INTERVAL 30 DAY

-- Pre-aggregate data
WITH summary AS (
    SELECT date, category, SUM(value) as total
    FROM large_table
    GROUP BY date, category
)
SELECT * FROM summary;

-- Add result limits for preview
LIMIT 10000;
```

#### Permission Denied Errors
**Detection**: "User lacks privilege SELECT on catalog.schema.table"
**Automated Fix**:
```sql
-- Grant required permissions
GRANT USE CATALOG ON CATALOG catalog_name TO `user@company.com`;
GRANT USE SCHEMA ON SCHEMA catalog_name.schema_name TO `user@company.com`;
GRANT SELECT ON TABLE catalog_name.schema_name.table_name TO `user@company.com`;
```

#### Data Type Mismatches
**Detection**: Widget expects numeric but receives string
**Automated Fix**:
```sql
-- Cast to appropriate types
SELECT 
    CAST(string_number AS DOUBLE) AS numeric_value,
    DATE(timestamp_column) AS date_value,
    CAST(boolean_text AS BOOLEAN) AS flag_value
FROM source_table;
```

### Error Recovery Strategy
1. **Graceful Degradation**: Provide fallback widgets when preferred types fail
2. **Incremental Building**: Create dashboard progressively, validating each step
3. **Automated Retry**: Retry failed operations with exponential backoff
4. **Clear Communication**: Log all errors and fixes for transparency
5. **Continuous Monitoring**: Never stop monitoring until fully successful

**IMPORTANT**: The dashboard building process continues iteratively until all success criteria are met. I will not consider the dashboard complete until continuous monitoring confirms all widgets are rendering correctly with performant queries.

## Success Metrics

### Dashboard Quality Indicators
- ✅ **Data Accuracy**: All widgets display correct, up-to-date information
- ✅ **Performance**: Dashboard loads in under 5 seconds
- ✅ **Usability**: Users find insights quickly and interact intuitively
- ✅ **Maintainability**: Structure supports ongoing updates and modifications

### User Experience Criteria
- **Immediate Insights**: Key business questions answered at first glance
- **Actionable Information**: Dashboard prompts specific actions or decisions
- **Professional Appearance**: Builds confidence in data quality and reliability
- **Interactive Exploration**: Filters and drill-downs provide deeper analysis

## Available Tools

### Unity Catalog Exploration
- `describe_uc_schema` - Explore schema structure and tables
- `describe_uc_table` - Analyze table columns and data types

### SQL Execution & Validation
- `execute_dbsql` - Test and validate SQL queries
- `get_table_statistics` - Understand data characteristics

### Dashboard Management
- `list_lakeview_dashboards` - View existing dashboards
- `create_lakeview_dashboard` - Build new dashboard
- `get_lakeview_dashboard` - Retrieve dashboard details

### Widget Creation
- All widget creation functions for charts, KPIs, tables, and filters
- Automatic positioning and sizing optimization
- Data encoding validation and error prevention

## Example Implementation

### Sales Performance Dashboard
```markdown
1. Data Discovery
   - Explore sales catalog: orders, products, customers, regions
   
2. Query Validation
   - Test: SELECT SUM(revenue) FROM sales.orders WHERE date >= '2024-01-01'
   - Test: SELECT date, SUM(revenue) FROM sales.orders GROUP BY date ORDER BY date
   
3. Widget Creation
   - Revenue counter (current month total)
   - Revenue trend line chart (12-month progression)
   - Top products bar chart (sales ranking)
   - Regional breakdown pie chart
   
4. Layout Implementation
   - KPI counters at top
   - Trend chart prominently in center
   - Breakdown charts below for detailed analysis
   - Filter widgets for date range and region selection
```

## Final Validation Checklist

Before considering a dashboard complete:

- [ ] All SQL queries validated with `execute_dbsql`
- [ ] All widgets render properly with real data
- [ ] Filters and interactions work correctly
- [ ] Performance meets requirements (<5 second load time)
- [ ] Permissions configured properly
- [ ] Refresh schedules operating
- [ ] Mobile layout responsive
- [ ] User acceptance validated

## Documentation & Resources

- **[Lakeview Dashboards](https://docs.databricks.com/en/dashboards/lakeview.html)**: Complete guide to modern dashboard capabilities
- **[Unity Catalog](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)**: Data governance and catalog management
- **[Dashboard Creation](https://docs.databricks.com/en/dashboards/lakeview/create-lakeview-dashboard.html)**: Step-by-step dashboard building
- **[Widget Configuration](https://docs.databricks.com/en/dashboards/lakeview/add-visualizations.html)**: Visualization types and configuration

---

**Remember**: Always test your SQL queries first, choose widgets that match your data characteristics, and arrange layouts that tell a clear story with your data. The goal is a production-ready dashboard that delivers immediate value to your users.