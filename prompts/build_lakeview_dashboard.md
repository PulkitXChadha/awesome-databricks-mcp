# Build Lakeview Dashboard

Transform your data into actionable insights with production-ready Databricks Lakeview dashboards. This tool provides a systematic approach to building, validating, and deploying comprehensive dashboards that deliver real business value.

## Core Capabilities

- **Data Discovery & Validation**: Automated exploration of Unity Catalog with SQL query testing
- **Smart Widget Selection**: 15+ widget types optimized for your data characteristics  
- **Performance-First Design**: Built-in validation and optimization recommendations
- **Production Deployment**: Complete setup including permissions, scheduling, and monitoring
- **Error Resolution**: Automated troubleshooting with iterative improvement cycles

## Quick Start

### 1. Provide Dashboard Requirements
```yaml
purpose: "executive reporting | operational monitoring | analytics exploration"
data_sources: ["catalog.schema.table", "catalog.schema.view"]
key_metrics: ["revenue", "orders", "customer_satisfaction"]
audience: "executives | analysts | operations_teams"
dashboard_name: "Sales Performance Dashboard"
sql_warehouse_id: "your_warehouse_id"
```

### 2. Automated Workflow
The tool will:
1. **Explore** your data structure and relationships
2. **Validate** SQL queries for accuracy and performance
3. **Create** optimized widgets with proper data encoding
4. **Deploy** production-ready dashboard with permissions
5. **Monitor** performance and resolve any issues

## Widget Selection Guide

### Quantitative Data Visualization
- **Bar Charts**: Categorical comparisons, rankings, discrete values
- **Line Charts**: Time series trends, progression over time
- **Area Charts**: Cumulative trends, stacked categories
- **Scatter Plots**: Correlation analysis, outlier detection
- **Histograms**: Distribution analysis, frequency patterns

### KPI & Summary Widgets
- **Counters**: Single key metrics, totals, current values
- **Delta Counters**: Change indicators with trend arrows

### Data Display & Analysis
- **Data Tables**: Detailed record views, drill-down capabilities
- **Pivot Tables**: Cross-tabular analysis, multi-dimensional summaries
- **Combo Charts**: Multiple metrics with different scales

### Interactive Controls
- **Filters**: Date ranges, dropdowns, sliders, text search
- **Parameters**: Dynamic query modification and data exploration

## Critical Success Factors

### SQL Query Validation (MANDATORY)
- **ALWAYS** test queries with `execute_dbsql` before widget creation
- **ALWAYS** verify column names exist in query results
- **ALWAYS** check data types match widget requirements
- **NEVER** create widgets without validating underlying data

### Data Quality Best Practices
```sql
-- Handle null values safely
COALESCE(field, 0) AS safe_field

-- Prevent division by zero
CASE WHEN total > 0 THEN value/total ELSE 0 END AS percentage

-- Truncate long text for display
LEFT(description, 50) AS short_description
```

### Layout Optimization
- **Grid System**: 12-column responsive layout with consistent spacing
- **Visual Hierarchy**: Most important metrics prominently placed
- **Logical Grouping**: Related widgets organized by business function
- **Mobile Responsive**: Optimized for various screen sizes

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
1. **Explore Unity Catalog**: Use `list_uc_catalogs`, `describe_uc_schema`, `describe_uc_table`
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

## Error Prevention & Resolution

### Common Issues & Solutions
- **Query Performance**: Optimize with proper aggregations and filters
- **Permission Errors**: Verify Unity Catalog and dashboard access
- **Data Freshness**: Set up appropriate refresh schedules
- **Widget Failures**: Validate data types and field mappings

### Error Recovery Strategy
1. **Graceful Degradation**: Provide fallback options when preferred widgets fail
2. **Incremental Building**: Create dashboards progressively, validating each step
3. **User Feedback**: Clearly communicate issues and provide actionable solutions
4. **Continuous Monitoring**: Track performance and resolve issues proactively

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
- `list_uc_catalogs` - Discover available data catalogs
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